"""Private AirTravel execution contracts. No provider, transport, or execution capability.

Validation is deliberately not authorization consumption. A later gate must
atomically create an exclusive private attempt marker outside the disposable
run directory before constructing a provider. A successful validation here
leaves the grant's consumed flag false and cannot prevent a later replay alone.
"""

from __future__ import annotations

import hashlib
import json
import re
import stat
import subprocess
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from pathlib import Path, PurePosixPath
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker
from verify_text2uml_airtravel_runtime import (
    PUBLIC_AIRTRAVEL_ARCHIVE_SHA256,
    PUBLIC_AIRTRAVEL_COMMIT,
)

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_ROOT = REPOSITORY_ROOT / "schemas"
PRIVATE_PARENT = "external_data/airtravel-api-runs"
SHA256_RE = re.compile(r"[0-9a-f]{64}\Z")
COMMIT_RE = re.compile(r"[0-9a-f]{40}\Z")
RUN_ID_RE = re.compile(r"[a-z0-9][a-z0-9_-]{0,63}\Z")
RESERVED_NAMES = {
    "con",
    "prn",
    "aux",
    "nul",
    *(f"com{i}" for i in range(1, 10)),
    *(f"lpt{i}" for i in range(1, 10)),
}


class ContractValidationError(ValueError):
    """Malformed or incomplete contract; messages contain no input payloads."""


class GrantValidationError(ContractValidationError):
    """An execution grant is missing, invalid, stale, or mismatched."""


class ContainmentError(ContractValidationError):
    """The requested output is not a fresh repository-local private directory."""


def _decimal_string(value: Decimal) -> str:
    if not isinstance(value, Decimal) or not value.is_finite() or value < 0 or value.is_signed():
        raise ContractValidationError("invalid nonnegative Decimal")
    whole, _, fraction = format(value, "f").partition(".")
    return whole + "." + fraction.rstrip("0").ljust(2, "0")


def _json_value(value: Any) -> Any:
    if isinstance(value, Decimal):
        return _decimal_string(value)
    if value is None or type(value) in (str, int, bool):
        return value
    if isinstance(value, Mapping):
        if any(type(key) is not str for key in value):
            raise ContractValidationError("JSON object keys must be strings")
        return {key: _json_value(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_value(item) for item in value]
    raise ContractValidationError("unsupported canonical JSON value")


def canonical_json_sha256(value: Mapping[str, Any]) -> str:
    """Hash sorted, compact UTF-8 JSON; money uses canonical decimal strings.

    Floats and non-JSON objects are rejected, not coerced. No Unicode or command
    whitespace normalization is performed because it could erase a binding.
    """
    if not isinstance(value, Mapping):
        raise ContractValidationError("canonical JSON root must be an object")
    try:
        payload = json.dumps(
            _json_value(value),
            sort_keys=True,
            ensure_ascii=False,
            separators=(",", ":"),
            allow_nan=False,
        ).encode("utf-8")
    except (ValueError, TypeError, UnicodeError, RecursionError):
        raise ContractValidationError("invalid canonical JSON") from None
    return hashlib.sha256(payload).hexdigest()


def _schema_validate(kind: str, value: Mapping[str, Any]) -> None:
    try:
        schema = json.loads(
            (SCHEMA_ROOT / f"airtravel-api-execution-{kind}-v1.schema.json").read_text(
                encoding="utf-8"
            )
        )
        validator = Draft202012Validator(schema, format_checker=FormatChecker())
        if not validator.is_valid(value):
            raise ContractValidationError(f"invalid {kind} schema")
        # JSON Schema regards 1.0 as an integer; contracts require actual integers.
        for name, rule in schema["properties"].items():
            if rule.get("type") == "integer" and type(value[name]) is not int:
                raise ContractValidationError(f"invalid {kind} integer")
    except (OSError, ValueError, TypeError, KeyError):
        raise ContractValidationError(f"invalid {kind} schema") from None


def _load_json(path: Path) -> Mapping[str, Any]:
    def unique_keys(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ContractValidationError("duplicate JSON key")
            result[key] = value
        return result

    try:
        value = json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=unique_keys)
        if not isinstance(value, Mapping):
            raise ContractValidationError("JSON root must be an object")
        return value
    except (OSError, UnicodeError, ValueError, TypeError):
        raise ContractValidationError("missing or malformed private JSON") from None


def _utc(value: datetime) -> datetime:
    if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() != timedelta(0):
        raise ContractValidationError("timestamp must be timezone-aware UTC")
    return value


def _timestamp(value: datetime) -> str:
    return _utc(value).isoformat().replace("+00:00", "Z")


def _parse_timestamp(value: str) -> datetime:
    if not isinstance(value, str) or not value.endswith("Z"):
        raise ContractValidationError("timestamp must use UTC Z")
    try:
        return _utc(datetime.fromisoformat(value[:-1] + "+00:00"))
    except ValueError:
        raise ContractValidationError("invalid UTC timestamp") from None


@dataclass(frozen=True)
class PriceSchedule:
    source: str
    checked_at_utc: datetime
    input_usd_per_million_tokens: Decimal
    output_usd_per_million_tokens: Decimal

    def to_dict(self) -> dict[str, Any]:
        return {
            "source": self.source,
            "checked_at_utc": _timestamp(self.checked_at_utc),
            "input_usd_per_million_tokens": _decimal_string(self.input_usd_per_million_tokens),
            "output_usd_per_million_tokens": _decimal_string(self.output_usd_per_million_tokens),
        }

    @property
    def sha256(self) -> str:
        return canonical_json_sha256(self.to_dict())


def build_call_inventory(max_rounds: int) -> dict[str, Any]:
    """Canonical isolated-lane inventory, independent of provider imports/caps.

    Four context calls plus three stages per case, each with one generation
    and at most one answer per round. No implicit retries or legacy formula.
    """
    if type(max_rounds) is not int or not 1 <= max_rounds <= 10:
        raise ContractValidationError("invalid bounded round policy")
    return {
        "schema_version": "airtravel-isolated-call-inventory-v1",
        "case_count": 4,
        "context_calls_per_case": 1,
        "stage_count_per_case": 3,
        "generation_calls_per_round": 1,
        "maximum_answer_calls_per_round": 1,
        "max_rounds": max_rounds,
        "minimum_calls": 16,
        "maximum_calls": 4 * (1 + 3 * max_rounds * 2),
        "automatic_retries": 0,
    }


_ONE_ROUND_SHA256 = canonical_json_sha256(build_call_inventory(1))


@dataclass(frozen=True)
class ExecutionConfig:
    """Frozen configuration; the only permitted total cap is exactly USD 6.00."""

    model: str
    provider_host: str
    max_usd: Decimal
    timeout_seconds: int
    run_timeout_seconds: int
    max_retries: int
    concurrency: int
    max_calls: int
    max_input_tokens: int
    max_output_tokens: int
    price_schedule: PriceSchedule
    max_rounds: int = 1

    @property
    def call_inventory_sha256(self) -> str:
        return canonical_json_sha256(build_call_inventory(self.max_rounds))

    def __post_init__(self) -> None:
        if not isinstance(self.price_schedule, PriceSchedule):
            raise ContractValidationError("immutable price schedule required")
        _schema_validate("config", self.to_dict())
        if self.run_timeout_seconds < self.timeout_seconds:
            raise ContractValidationError("run timeout is shorter than per-call timeout")

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": "airtravel-api-execution-config-v1",
            "model": self.model,
            "provider_host": self.provider_host,
            "max_usd": _decimal_string(self.max_usd),
            "timeout_seconds": self.timeout_seconds,
            "run_timeout_seconds": self.run_timeout_seconds,
            "max_retries": self.max_retries,
            "concurrency": self.concurrency,
            "max_calls": self.max_calls,
            "max_rounds": self.max_rounds,
            "call_inventory_sha256": self.call_inventory_sha256,
            "max_input_tokens": self.max_input_tokens,
            "max_output_tokens": self.max_output_tokens,
            "price_schedule": self.price_schedule.to_dict(),
        }

    @property
    def sha256(self) -> str:
        return canonical_json_sha256(self.to_dict())

    @classmethod
    def from_dict(cls, value: Mapping[str, Any]) -> ExecutionConfig:
        _schema_validate("config", value)
        data = dict(value)
        data.pop("schema_version")
        inventory_sha256 = data.pop("call_inventory_sha256")
        price = dict(data.pop("price_schedule"))
        price["checked_at_utc"] = _parse_timestamp(price["checked_at_utc"])
        for name in ("input_usd_per_million_tokens", "output_usd_per_million_tokens"):
            price[name] = Decimal(price[name])
        data["max_usd"] = Decimal(data["max_usd"])
        result = cls(**data, price_schedule=PriceSchedule(**price))
        if result.call_inventory_sha256 != inventory_sha256:
            raise ContractValidationError("call inventory hash mismatch")
        return result

    @classmethod
    def from_json(cls, path: Path) -> ExecutionConfig:
        return cls.from_dict(_load_json(path))


def _digest(value: str) -> str:
    if not isinstance(value, str) or not SHA256_RE.fullmatch(value):
        raise ContractValidationError("invalid SHA-256")
    return value


def _commit(value: str) -> str:
    if not isinstance(value, str) or not COMMIT_RE.fullmatch(value):
        raise ContractValidationError("invalid Git commit")
    return value


def _relative_file(value: str) -> str:
    if not isinstance(value, str) or not value or "\\" in value or ":" in value:
        raise ContractValidationError("unsafe manifest path")
    path = PurePosixPath(value)
    if path.is_absolute() or ".." in path.parts or path.as_posix() != value or value == ".":
        raise ContractValidationError("unsafe manifest path")
    return value


@dataclass(frozen=True)
class RuntimeFileBinding:
    source_path: str
    path: str
    bytes: int
    sha256: str

    def __post_init__(self) -> None:
        _relative_file(self.source_path)
        _relative_file(self.path)
        _digest(self.sha256)
        if type(self.bytes) is not int or self.bytes < 0:
            raise ContractValidationError("invalid file byte length")

    def to_dict(self) -> dict[str, Any]:
        return {
            "source_path": self.source_path,
            "path": self.path,
            "bytes": self.bytes,
            "sha256": self.sha256,
            "byte_transformation": "NONE",
        }


def _five_files(rows: tuple[RuntimeFileBinding, ...]) -> None:
    if (
        type(rows) is not tuple
        or len(rows) != 5
        or any(not isinstance(r, RuntimeFileBinding) for r in rows)
    ):
        raise ContractValidationError("exactly five immutable runtime bindings required")
    for name in ("source_path", "path"):
        paths = [getattr(row, name) for row in rows]
        if (
            len({path.casefold() for path in paths}) != 5
            or sum(path.startswith("domain_description/") for path in paths) != 1
            or sum(path.startswith("candidate_models/") for path in paths) != 4
        ):
            raise ContractValidationError("invalid five-file selection")


@dataclass(frozen=True)
class VerifiedInputManifest:
    """Hash-only input binding; contains no archive, prompt, or model bytes."""

    code_sha: str
    config_sha256: str
    verification_sha256: str
    source_inventory_sha256: str
    source_archive_sha256: str
    source_commit: str
    runtime_files: tuple[RuntimeFileBinding, ...]
    max_rounds: int = 1
    call_inventory_sha256: str = _ONE_ROUND_SHA256
    verification_inputs: tuple[tuple[str, str], ...] = ()

    def __post_init__(self) -> None:
        _commit(self.code_sha)
        if self.call_inventory_sha256 != canonical_json_sha256(
            build_call_inventory(self.max_rounds)
        ):
            raise ContractValidationError("manifest inventory mismatch")
        if type(self.verification_inputs) is not tuple:
            raise ContractValidationError("immutable verification paths required")
        names = set()
        for row in self.verification_inputs:
            if type(row) is not tuple or len(row) != 2 or row[0] in names:
                raise ContractValidationError("invalid verification path binding")
            names.add(row[0])
            if row[0] not in {
                "archive",
                "source_root",
                "source_manifest",
                "amendment_manifest",
                "runtime_root",
                "reference_root",
            }:
                raise ContractValidationError("unknown verification path")
            _relative_file(row[1])
        for value in (self.config_sha256, self.verification_sha256, self.source_inventory_sha256):
            _digest(value)
        if (
            self.source_archive_sha256 != PUBLIC_AIRTRAVEL_ARCHIVE_SHA256
            or self.source_commit != PUBLIC_AIRTRAVEL_COMMIT
        ):
            raise ContractValidationError("unapproved source identity")
        _five_files(self.runtime_files)

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": "airtravel-api-input-manifest-v1",
            "code_sha": self.code_sha,
            "config_sha256": self.config_sha256,
            "verification_sha256": self.verification_sha256,
            "source_inventory_sha256": self.source_inventory_sha256,
            "source_archive_sha256": self.source_archive_sha256,
            "source_commit": self.source_commit,
            "selection_rule": "verified-v1.0.2-source-to-runtime-mapping",
            "runtime_files": [row.to_dict() for row in self.runtime_files],
            "max_rounds": self.max_rounds,
            "call_inventory_sha256": self.call_inventory_sha256,
            "verification_inputs": dict(self.verification_inputs),
        }

    @property
    def sha256(self) -> str:
        return canonical_json_sha256(self.to_dict())

    @classmethod
    def from_dict(cls, value: Mapping[str, Any]) -> VerifiedInputManifest:
        try:
            data = dict(value)
            if not {"max_rounds", "call_inventory_sha256"} <= data.keys():
                raise ContractValidationError("explicit manifest inventory required")
            if (
                data.pop("schema_version") != "airtravel-api-input-manifest-v1"
                or data.pop("selection_rule") != "verified-v1.0.2-source-to-runtime-mapping"
            ):
                raise ContractValidationError("invalid manifest identity")
            rows = []
            inputs = data.pop("verification_inputs")
            if not isinstance(inputs, Mapping):
                raise ContractValidationError("invalid verification inputs")
            for raw in data.pop("runtime_files"):
                row = dict(raw)
                if row.pop("byte_transformation") != "NONE":
                    raise ContractValidationError("invalid byte transformation")
                rows.append(RuntimeFileBinding(**row))
            return cls(
                **data, runtime_files=tuple(rows), verification_inputs=tuple(sorted(inputs.items()))
            )
        except (ValueError, TypeError, KeyError):
            raise ContractValidationError("malformed input manifest") from None


def build_input_manifest(
    *,
    verification: Mapping[str, Any],
    config: ExecutionConfig,
    code_sha: str,
    verification_inputs: tuple[tuple[str, str], ...] = (),
) -> VerifiedInputManifest:
    """Bind all Task 1 evidence and derive runtime digests from its source inventory.

    Task 1's PASS result is an in-process trusted verifier result, not proof of
    authenticity for arbitrary caller-authored JSON. The gate must rerun Task 1
    on the actual bytes before using a persisted manifest for execution.
    """
    try:
        if verification["status"] != "PASS" or verification["provider_call_made"] is not False:
            raise ContractValidationError("verification did not pass")
        archive = verification["source_archive"]
        entries = verification["source_entries"]
        mapping = verification["source_to_runtime"]
        runtime = verification["runtime_pack"]
        reference = verification["reference_separation"]
        for check in (archive, entries, mapping, runtime, reference):
            if check["status"] != "PASS":
                raise ContractValidationError("verification component did not pass")
        required = (
            (archive, "commit_binding", True),
            (archive, "inventory_matches_manifest", True),
            (archive, "duplicate_members", []),
            (archive, "invalid_members", []),
            (entries, "unsafe_paths", []),
            (entries, "manifest_errors", []),
            (mapping, "byte_identical", True),
            (mapping, "errors", []),
            (runtime, "unsafe_paths", []),
            (runtime, "manifest_errors", []),
            (runtime, "allowed_configuration", True),
            (runtime, "amendment_identity", True),
            (reference, "leaked_paths", []),
        )
        for section, field, expected in required:
            actual = section[field]
            if type(actual) is not type(expected) or actual != expected:
                raise ContractValidationError("incomplete verification evidence")
        for section, names, count in (
            (entries, ("expected_count", "observed_count", "matched"), 143),
            (runtime, ("expected_count", "observed_count"), 5),
            (mapping, ("mapping_count",), 5),
        ):
            if any(type(section[name]) is not int or section[name] != count for name in names):
                raise ContractValidationError("invalid verification counts")
        if type(reference["reference_count"]) is not int or reference["reference_count"] < 0:
            raise ContractValidationError("invalid reference count")
        if any(
            archive[name] != PUBLIC_AIRTRAVEL_ARCHIVE_SHA256
            for name in ("actual_sha256", "expected_sha256", "declared_sha256")
        ) or any(
            archive[name] != PUBLIC_AIRTRAVEL_COMMIT
            for name in ("expected_commit", "declared_commit")
        ):
            raise ContractValidationError("unapproved source identity")
        inventory = archive["member_inventory"]
        if type(inventory) is not list or len(inventory) != 143:
            raise ContractValidationError("incomplete source inventory")
        indexed = {}
        for row in inventory:
            path = _relative_file(row["path"])
            _digest(row["sha256"])
            if type(row["bytes"]) is not int or row["bytes"] < 0 or path.casefold() in indexed:
                raise ContractValidationError("invalid source inventory row")
            indexed[path.casefold()] = row
        rows = []
        if type(mapping["mappings"]) is not list:
            raise ContractValidationError("invalid mapping list")
        for row in mapping["mappings"]:
            source_path = _relative_file(row["source_path"])
            source = indexed[source_path.casefold()]
            if row["byte_identical"] is not True or source["path"] != source_path:
                raise ContractValidationError("invalid source mapping")
            rows.append(
                RuntimeFileBinding(source_path, row["path"], source["bytes"], source["sha256"])
            )
        return VerifiedInputManifest(
            code_sha=_commit(code_sha),
            config_sha256=config.sha256,
            verification_sha256=canonical_json_sha256(verification),
            source_inventory_sha256=canonical_json_sha256({"source_entries": inventory}),
            source_archive_sha256=archive["actual_sha256"],
            source_commit=archive["expected_commit"],
            runtime_files=tuple(sorted(rows, key=lambda row: row.path)),
            max_rounds=config.max_rounds,
            call_inventory_sha256=config.call_inventory_sha256,
            verification_inputs=verification_inputs,
        )
    except (KeyError, TypeError, AttributeError, ValueError):
        raise ContractValidationError("missing or invalid verifier evidence") from None


def assert_safe_run_id(value: str) -> str:
    """Require a portable lowercase identifier without traversal or device names."""
    if not isinstance(value, str) or not RUN_ID_RE.fullmatch(value) or value in RESERVED_NAMES:
        raise ContainmentError("unsafe run identifier")
    return value


def _check_path_components(path: Path) -> None:
    for part in reversed((path, *path.parents)):
        try:
            metadata = part.lstat()
        except FileNotFoundError:
            continue
        if (
            stat.S_ISLNK(metadata.st_mode)
            or getattr(metadata, "st_file_attributes", 0)
            & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 1024)
            or not stat.S_ISDIR(metadata.st_mode)
        ):
            raise ContainmentError("link, reparse point, or nondirectory output ancestor")
        if part != part.parent:
            for sibling in part.parent.iterdir():
                if sibling.name.casefold() == part.name.casefold() and sibling.name != part.name:
                    raise ContainmentError("case-fold collision in output path")


def _git(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(REPOSITORY_ROOT), *args],
        capture_output=True,
        text=True,
        check=False,
        timeout=10,
    )


def assert_private_empty_run_root(root: Path, run_id: str) -> Path:
    """Exclusively create one ignored run directory anchored to this repository.

    Even empty existing run directories are rejected. This checks filesystem
    state at creation, not future writes or hostile concurrent directory swaps;
    the eventual writer must preserve containment when it opens each artifact.
    """
    assert_safe_run_id(run_id)
    try:
        if ".." in root.parts:
            raise ContainmentError("output traversal rejected")
        candidate_parent = root if root.is_absolute() else REPOSITORY_ROOT / root
        expected = REPOSITORY_ROOT / "external_data" / "airtravel-api-runs"
        if candidate_parent.as_posix() != expected.as_posix():
            raise ContainmentError("output root is not the approved repository-local parent")
        candidate = expected / run_id
        _check_path_components(candidate)
        result = _git("rev-parse", "--show-toplevel")
        if (
            result.returncode
            or Path(result.stdout.strip()).as_posix() != REPOSITORY_ROOT.as_posix()
        ):
            raise ContainmentError("repository anchor is not a Git root")
        relative = f"{PRIVATE_PARENT}/{run_id}"
        for item in (relative, relative + "/receipt.json", relative + "/qa_events.jsonl"):
            if _git("check-ignore", "--no-index", "--quiet", "--", item).returncode != 0:
                raise ContainmentError("private output is not Git-ignored")
        tracked = _git("ls-files", "--", relative)
        if tracked.returncode or tracked.stdout.strip():
            raise ContainmentError("private output contains tracked paths")
        expected.mkdir(mode=0o700, parents=True, exist_ok=True)
        _check_path_components(expected)
        if any(child.name.casefold() == run_id.casefold() for child in expected.iterdir()):
            raise ContainmentError("run directory already exists or case-fold collides")
        candidate.mkdir(mode=0o700, exist_ok=False)
        _check_path_components(candidate)
        if any(candidate.iterdir()):
            raise ContainmentError("run directory is not empty")
        return candidate
    except (OSError, subprocess.SubprocessError):
        raise ContainmentError("private output containment check failed") from None


def command_fingerprint(command: Sequence[str]) -> str:
    """Hash the complete argv vector with argument boundaries preserved."""
    if (
        isinstance(command, (str, bytes))
        or not isinstance(command, Sequence)
        or not command
        or any(type(arg) is not str or not arg or "\0" in arg for arg in command)
    ):
        raise ContractValidationError("invalid command vector")
    return canonical_json_sha256({"argv": list(command)})


def parse_execution_command(command: Sequence[str]) -> dict[str, str]:
    """Parse the shared CLI grammar without argparse's aliases or override rules.

    Grammar: ``[launcher ...] MODE (EXACT_OPTION VALUE)*``. The optional launcher
    consists only of non-option tokens (for example ``uv run python runner.py``).
    Every mode option is a single known ``--name`` followed by one value, and
    occurs at most once. Equals-form options, abbreviations, option-like values,
    control characters, ``--``, and extra positional arguments are rejected.

    A CLI can pass its mode-and-options argv directly and consume this returned
    mapping; it must not reinterpret argv with a more permissive parser. Values
    are preserved verbatim. Parsing is not authorization, file containment, or
    validation that all mode-specific input files have been supplied.
    """
    command_fingerprint(command)  # Apply the same primitive argv constraints.
    argv = list(command)
    if any(any(ord(char) < 32 or ord(char) == 127 for char in arg) for arg in argv):
        raise ContractValidationError("control character in command")
    modes = {"prepare", "preflight", "execute"}
    mode_index = next((i for i, arg in enumerate(argv) if arg in modes), None)
    if mode_index is None or any(arg.startswith("-") for arg in argv[:mode_index]):
        raise ContractValidationError("missing mode or invalid command launcher")
    mode = argv[mode_index]
    options = {"--config", "--private-root", "--run-id"}
    if mode == "prepare":
        options.update(
            {
                "--archive",
                "--source-root",
                "--source-manifest",
                "--runtime-root",
                "--amendment",
                "--reference-root",
            }
        )
    else:
        options.add("--input-manifest")
        if mode == "execute":
            options.add("--grant")
    tail = argv[mode_index + 1 :]
    if len(tail) % 2:
        raise ContractValidationError("command options require separated values")
    parsed = {"mode": mode}
    for index in range(0, len(tail), 2):
        option, value = tail[index : index + 2]
        if option not in options or value.startswith("-"):
            raise ContractValidationError("unknown or noncanonical command option")
        key = option[2:].replace("-", "_")
        if key in parsed:
            raise ContractValidationError("duplicate command option")
        parsed[key] = value
    return parsed


@dataclass(frozen=True)
class ExecutionGrant:
    """Immutable exact execute bindings; validation never consumes authorization."""

    nonce: str
    invocation_id: str
    run_id: str
    mode: str
    issued_at_utc: datetime
    expires_at_utc: datetime
    consumed: bool
    code_sha: str
    input_manifest_sha256: str
    config_sha256: str
    model: str
    provider_host: str
    price_schedule_sha256: str
    timeout_seconds: int
    run_timeout_seconds: int
    max_retries: int
    concurrency: int
    max_calls: int
    max_input_tokens: int
    max_output_tokens: int
    max_usd: Decimal
    command_sha256: str
    private_root: str
    max_rounds: int = 1
    call_inventory_sha256: str = _ONE_ROUND_SHA256

    def __post_init__(self) -> None:
        try:
            _schema_validate("grant", self.to_dict())
            if self.call_inventory_sha256 != canonical_json_sha256(
                build_call_inventory(self.max_rounds)
            ):
                raise GrantValidationError("grant inventory mismatch")
            assert_safe_run_id(self.run_id)
            if self.private_root != f"{PRIVATE_PARENT}/{self.run_id}":
                raise GrantValidationError("output root binding mismatch")
            if self.issued_at_utc >= self.expires_at_utc:
                raise GrantValidationError("grant time interval is invalid")
        except ContractValidationError:
            raise GrantValidationError("invalid grant contract") from None

    def to_dict(self) -> dict[str, Any]:
        result = {name: getattr(self, name) for name in self.__dataclass_fields__}
        result.update(
            schema_version="airtravel-api-execution-grant-v1",
            issued_at_utc=_timestamp(self.issued_at_utc),
            expires_at_utc=_timestamp(self.expires_at_utc),
            max_usd=_decimal_string(self.max_usd),
        )
        return result

    @classmethod
    def from_dict(cls, value: Mapping[str, Any]) -> ExecutionGrant:
        try:
            _schema_validate("grant", value)
            data = dict(value)
            data.pop("schema_version")
            for key in ("issued_at_utc", "expires_at_utc"):
                data[key] = _parse_timestamp(data[key])
            data["max_usd"] = Decimal(data["max_usd"])
            return cls(**data)
        except (ContractValidationError, TypeError, ValueError):
            raise GrantValidationError("invalid grant schema") from None

    @classmethod
    def from_json(cls, path: Path) -> ExecutionGrant:
        try:
            return cls.from_dict(_load_json(path))
        except ContractValidationError:
            raise GrantValidationError("missing or malformed private grant") from None


def validate_execution_grant(
    grant: ExecutionGrant,
    *,
    config: ExecutionConfig,
    manifest: VerifiedInputManifest,
    current_commit: str,
    command: Sequence[str],
    mode: str = "execute",
    now: datetime | None = None,
) -> None:
    """Validate exact bindings without consumption, network, or any private writes."""
    try:
        if not isinstance(grant, ExecutionGrant) or mode != "execute":
            raise GrantValidationError("missing grant or wrong mode")
        _schema_validate("grant", grant.to_dict())
        instant = _utc(now if now is not None else datetime.now(timezone.utc))
        if not grant.issued_at_utc <= instant < grant.expires_at_utc or grant.consumed is not False:
            raise GrantValidationError("grant expired, not yet valid, or consumed")
        if grant.config_sha256 != config.sha256 or manifest.config_sha256 != config.sha256:
            raise GrantValidationError("configuration hash mismatch")
        if (
            manifest.max_rounds != config.max_rounds
            or manifest.call_inventory_sha256 != config.call_inventory_sha256
        ):
            raise GrantValidationError("manifest inventory mismatch")
        if grant.input_manifest_sha256 != manifest.sha256:
            raise GrantValidationError("input manifest hash mismatch")
        if grant.code_sha != _commit(current_commit) or manifest.code_sha != current_commit:
            raise GrantValidationError("code commit mismatch")
        if grant.price_schedule_sha256 != config.price_schedule.sha256:
            raise GrantValidationError("price schedule hash mismatch")
        for field in (
            "model",
            "provider_host",
            "max_usd",
            "timeout_seconds",
            "run_timeout_seconds",
            "max_retries",
            "concurrency",
            "max_calls",
            "max_rounds",
            "call_inventory_sha256",
            "max_input_tokens",
            "max_output_tokens",
        ):
            if getattr(grant, field) != getattr(config, field):
                raise GrantValidationError("provider or cap binding mismatch")
        if grant.command_sha256 != command_fingerprint(command):
            raise GrantValidationError("command fingerprint mismatch")
        parsed = parse_execution_command(command)
        if parsed["mode"] != "execute":
            raise GrantValidationError("command is not exact execute mode")
        for option, expected in (("run_id", grant.run_id), ("private_root", PRIVATE_PARENT)):
            if parsed.get(option) != expected:
                raise GrantValidationError("command output binding mismatch")
        if grant.private_root != f"{PRIVATE_PARENT}/{grant.run_id}":
            raise GrantValidationError("private root binding mismatch")
    except GrantValidationError:
        raise
    except (ContractValidationError, TypeError, AttributeError):
        raise GrantValidationError("invalid execution binding") from None


def parse_execution_receipt(value: Mapping[str, Any]) -> dict[str, Any]:
    """Validate a private receipt and return a detached copy without trimming strings."""
    _schema_validate("receipt", value)
    if value["call_inventory_sha256"] != canonical_json_sha256(
        build_call_inventory(value["max_rounds"])
    ):
        raise ContractValidationError("receipt inventory mismatch")
    _parse_timestamp(value["created_at_utc"])
    return _json_value(value)


def build_receipt_skeleton(
    *,
    config: ExecutionConfig,
    manifest: VerifiedInputManifest,
    run_id: str,
    mode: str,
    now: datetime | None = None,
) -> dict[str, Any]:
    """Return a private zero-call engineering receipt, never an execution claim."""
    assert_safe_run_id(run_id)
    if (
        manifest.config_sha256 != config.sha256
        or manifest.max_rounds != config.max_rounds
        or manifest.call_inventory_sha256 != config.call_inventory_sha256
    ):
        raise ContractValidationError("configuration hash mismatch")
    receipt = {
        "schema_version": "airtravel-api-execution-receipt-v1",
        "run_id": run_id,
        "mode": mode,
        "status": "NOT_STARTED",
        "created_at_utc": _timestamp(now if now is not None else datetime.now(timezone.utc)),
        "code_sha": manifest.code_sha,
        "input_manifest_sha256": manifest.sha256,
        "config_sha256": config.sha256,
        "model": config.model,
        "provider_host": config.provider_host,
        "price_schedule_sha256": config.price_schedule.sha256,
        "max_usd": _decimal_string(config.max_usd),
        "max_rounds": config.max_rounds,
        "call_inventory_sha256": config.call_inventory_sha256,
        "physical_call_count": 0,
        "external_provider_call_count": 0,
        "input_token_count": 0,
        "output_token_count": 0,
        "spent_usd": "0.00",
        "reserved_usd": "0.00",
        "scientific_result_count": 0,
        "technical_error_code": "NONE",
        "event_log_sha256": None,
        "pipeline_output_sha256": None,
        "ledger_sha256": None,
        "detector_version": "Detector-v1",
        "agent4_queue_status": "NOT_AVAILABLE",
        "containment_check": "NOT_CHECKED",
        "lifecycle_summary": {
            "CONVERGED": 0,
            "TERMINATED_MAX_ROUNDS": 0,
            "INCOMPLETE_TECHNICAL": 0,
        },
    }
    return parse_execution_receipt(receipt)
