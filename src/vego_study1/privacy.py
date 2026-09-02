"""Privacy-safe validation for the Study 1 candidate-event contract."""

from __future__ import annotations

import json
import math
import re
import subprocess
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any
from uuid import UUID

from jsonschema import Draft202012Validator

from .path_safety import local_path, resolve_local_directory

SIGNAL_IDS = frozenset(
    {
        "claim_uncertainty",
        "unreviewed_error_consequence",
        "evidence_quality",
        "reviewer_competence_for_claim",
        "current_queue_conditions",
        "novelty_vs_judgment_store",
        "cross_agent_disagreement",
        "expected_future_reuse_value",
    }
)
RAW_LOCATOR_KEYS = frozenset({"locator", "path", "raw_locator", "raw_content", "content"})
SCHEMA_PATH = (
    Path(__file__).resolve().parents[2]
    / "schemas"
    / "study1"
    / "CandidateEscalationEvent-v1.schema.json"
)


class PrivacyValidationError(ValueError):
    """Raised when a candidate event or public artifact violates its privacy contract."""


@dataclass(frozen=True)
class PrivacyFinding:
    path: Path
    line: int
    kind: str


@dataclass(frozen=True)
class StagedPrivacyScan:
    """One privacy scan bound to exact object bytes in a repository index."""

    repository_root: Path
    paths: tuple[Path, ...]
    findings: tuple[PrivacyFinding, ...]


def _load_schema() -> dict[str, Any]:
    return json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))


def _non_finite_number_path(value: Any, path: tuple[object, ...] = ()) -> tuple[object, ...] | None:
    if isinstance(value, float) and not math.isfinite(value):
        return path
    if isinstance(value, dict):
        for key, item in value.items():
            found = _non_finite_number_path(item, (*path, key))
            if found is not None:
                return found
    elif isinstance(value, list):
        for index, item in enumerate(value):
            found = _non_finite_number_path(item, (*path, index))
            if found is not None:
                return found
    return None


def validate_candidate_event(
    event: dict[str, Any], *, schema: dict[str, Any] | None = None
) -> dict[str, Any]:
    """Validate a privacy-sanitized candidate event and return it unchanged."""
    non_finite_path = _non_finite_number_path(event)
    if non_finite_path is not None:
        field = ".".join(str(part) for part in non_finite_path)
        raise PrivacyValidationError(
            f"candidate event validation at {field or 'root'} [non_finite_number]"
        )
    try:
        UUID(str(event.get("event_id")))
    except (TypeError, ValueError, AttributeError) as error:
        raise PrivacyValidationError("event_id must be a UUID") from error

    source = event.get("source")
    if not isinstance(source, dict) or not source.get("source_hash"):
        raise PrivacyValidationError("source_hash is required")

    locator = event.get("sanitized_local_locator")
    if isinstance(locator, dict) and RAW_LOCATOR_KEYS.intersection(locator):
        raise PrivacyValidationError("raw locator content is prohibited")

    if event.get("claim_boundary") != "candidate_escalation_only":
        raise PrivacyValidationError("claim_boundary must be candidate_escalation_only")

    signals = event.get("signals")
    if isinstance(signals, list):
        for signal in signals:
            if not isinstance(signal, dict):
                continue
            if signal.get("signal_id") not in SIGNAL_IDS:
                raise PrivacyValidationError("unknown signal ID")
            if not signal.get("evidence_state"):
                raise PrivacyValidationError("evidence_state is required")
        signal_ids = {signal.get("signal_id") for signal in signals if isinstance(signal, dict)}
        if len(signals) != len(SIGNAL_IDS) or signal_ids != SIGNAL_IDS:
            raise PrivacyValidationError(
                "exactly one observation is required for every policy signal"
            )

    validator = Draft202012Validator(schema or _load_schema())
    errors = sorted(validator.iter_errors(event), key=lambda error: list(error.absolute_path))
    if errors:
        error = errors[0]
        field = ".".join(str(part) for part in error.absolute_path)
        category = str(error.validator or "schema")
        raise PrivacyValidationError(
            f"candidate event schema violation at {field or 'root'} [{category}]"
        )
    return event


PUBLIC_ARTIFACT_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("controlled_path", re.compile(r"(?i)(?:[a-z]:\\|/(?:home|users|private)/)")),
    (
        "absolute_path_reference",
        re.compile(
            r"(?i)(?:[:=]\s*|(?:,|\[)\s*)[\"']?(?:[a-z]:[\\/][^\s\"'<>|]+"
            r"|/(?!/)[a-z0-9._~-]+(?:[\\/][^\s\"'<>|]+)*)"
        ),
    ),
    (
        "raw_subject_path",
        re.compile(r"(?i)(?<![a-z0-9_.-])(?:student|expert|model)[\\/][^\s\"']+"),
    ),
    (
        "raw_control_path",
        re.compile(r"(?i)(?<![a-z0-9_.-])(?:control|controlled)[\\/][^\s\"']+"),
    ),
    (
        "raw_evaluation_output_path",
        re.compile(r"(?i)(?<![a-z0-9_.-])(?:[^\s\"']*[\\/])?eval_output[\\/][^\s\"']+"),
    ),
    ("drive_url", re.compile(r"(?i)https?://(?:drive|docs)\.google\.com/")),
    ("drive_id", re.compile(r"(?<!sha256:)\b1[A-Za-z0-9_-]{24,}\b")),
    (
        "private_url",
        re.compile(
            r"(?i)https?://(?:localhost|127\.0\.0\.1|(?:[a-z0-9-]+\.)+(?:internal|private|local))"
            r"(?::\d+)?(?:[/?#]|$)"
        ),
    ),
    (
        "private_host_reference",
        re.compile(
            r"(?i)(?<![a-z0-9.-])(?:localhost|127\.0\.0\.1|"
            r"(?:[a-z0-9-]+\.)+(?:internal|private|local))"
            r"(?::\d+)?(?=[/?,;:\s\"'\]}]|$)"
        ),
    ),
    (
        "remote_or_unc_reference",
        re.compile(
            r"(?i)(?<![a-z0-9+.-])(?:\\\\[a-z0-9][a-z0-9._-]*[\\/]"
            r"|(?<!:)//[a-z0-9][a-z0-9._-]*/"
            r"|(?:file|s3|ssh|ftp|git):(?://)?"
            r"|(?!(?:https?|sha256):)[a-z][a-z0-9+.-]*://)"
        ),
    ),
    (
        "credential_like",
        re.compile(
            r"(?i)\b(?:[a-z0-9_]*api[_-]?key|token|secret|password|credential)\b"
            r"[\"']?\s*[:=]\s*[\"']?(?!\$\{|\{\{)[A-Za-z0-9_./+=-]{8,}"
        ),
    ),
    (
        "controlled_content_marker",
        re.compile(
            r"(?i)RAW[_]CONTROLLED[_]CONTENT|CONTROLLED[_](?:STUDENT|EXPERT)|"
            r"(?:STUDENT|EXPERT)[_]RAW[_]"
        ),
    ),
)

PROHIBITED_PUBLIC_PATH_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("private_release_path", re.compile(r"(?i)(?:^|/)research-private(?:/|$)")),
    ("raw_subject_path", re.compile(r"(?i)(?:^|/)(?:student|expert|model)(?:/|$)")),
    ("raw_control_path", re.compile(r"(?i)(?:^|/)(?:control|controlled)(?:/|$)")),
    ("raw_evaluation_output_path", re.compile(r"(?i)(?:^|/)eval_output(?:/|$)")),
)


def public_path_finding_kinds(relative_path: str) -> tuple[str, ...]:
    """Return prohibited kinds carried by one validated repository-relative path."""
    return tuple(
        kind for kind, pattern in PROHIBITED_PUBLIC_PATH_PATTERNS if pattern.search(relative_path)
    )


def _contains_non_finite_json_number(value: Any) -> bool:
    if isinstance(value, float):
        return not math.isfinite(value)
    if isinstance(value, dict):
        return any(_contains_non_finite_json_number(item) for item in value.values())
    if isinstance(value, list):
        return any(_contains_non_finite_json_number(item) for item in value)
    return False


def public_artifact_byte_findings(
    content: bytes, *, relative_path: str = ""
) -> tuple[tuple[int, str], ...]:
    """Scan immutable artifact bytes and fail closed for bytes that cannot be inspected."""
    if b"\0" in content:
        return ((1, "undecodable_or_binary_artifact"),)
    try:
        text = content.decode("utf-8")
    except UnicodeDecodeError:
        return ((1, "undecodable_or_binary_artifact"),)

    findings: list[tuple[int, str]] = []
    for line_number, line in enumerate(text.splitlines(), start=1):
        for kind, pattern in PUBLIC_ARTIFACT_PATTERNS:
            if pattern.search(line):
                findings.append((line_number, kind))

    if PurePosixPath(relative_path).suffix.casefold() == ".json":
        non_standard = False

        def _reject_constant(_value: str) -> None:
            raise ValueError("non_standard_numeric_constant")

        try:
            loaded = json.loads(text, parse_constant=_reject_constant)
        except json.JSONDecodeError:
            loaded = None
        except ValueError as error:
            loaded = None
            non_standard = str(error) == "non_standard_numeric_constant"
        if non_standard or _contains_non_finite_json_number(loaded):
            findings.append((1, "non_finite_json_number"))
    return tuple(findings)


def _validated_relative_path(value: str) -> str:
    candidate = PurePosixPath(value)
    if (
        not value
        or "\\" in value
        or candidate.is_absolute()
        or ".." in candidate.parts
        or candidate.parts in {(), (".",)}
        or re.match(r"^[A-Za-z]:", value)
    ):
        raise PrivacyValidationError(
            "staged artifact validation failed [path_outside_repository]"
        )
    return candidate.as_posix()


def _decode_nul_paths(output: bytes) -> tuple[str, ...]:
    """Decode Git's exact NUL-delimited path format without line splitting."""
    if not output:
        return ()
    if not output.endswith(b"\0"):
        raise PrivacyValidationError(
            "staged artifact validation failed [invalid_nul_path_stream]"
        )
    raw_paths = output[:-1].split(b"\0")
    if any(not raw_path for raw_path in raw_paths):
        raise PrivacyValidationError(
            "staged artifact validation failed [invalid_nul_path_stream]"
        )
    try:
        return tuple(raw_path.decode("utf-8") for raw_path in raw_paths)
    except UnicodeDecodeError as error:
        raise PrivacyValidationError(
            "staged artifact validation failed [undecodable_path]"
        ) from error


def _run_staged_git(repository_root: Path, *arguments: str, category: str) -> bytes:
    try:
        completed = subprocess.run(
            ["git", "-C", str(repository_root), *arguments],
            check=False,
            capture_output=True,
        )
    except OSError as error:
        raise PrivacyValidationError(
            f"staged artifact validation failed [{category}]"
        ) from error
    if completed.returncode != 0:
        raise PrivacyValidationError(f"staged artifact validation failed [{category}]")
    return completed.stdout


def _anchored_repository_root(value: str | Path) -> Path:
    candidate = local_path(value, "repository_root", PrivacyValidationError)
    candidate = resolve_local_directory(candidate, "repository_root", PrivacyValidationError)
    output = _run_staged_git(
        candidate,
        "rev-parse",
        "--show-toplevel",
        category="repository_root_unavailable",
    )
    try:
        reported = output.decode("utf-8").strip()
    except UnicodeDecodeError as error:
        raise PrivacyValidationError(
            "staged artifact validation failed [repository_root_undecodable]"
        ) from error
    if not reported:
        raise PrivacyValidationError(
            "staged artifact validation failed [repository_root_unavailable]"
        )
    return resolve_local_directory(
        local_path(reported, "repository_root", PrivacyValidationError),
        "repository_root",
        PrivacyValidationError,
    )


def _staged_entry(repository_root: Path, relative_path: str) -> tuple[str, str]:
    output = _run_staged_git(
        repository_root,
        "ls-files",
        "--stage",
        "-z",
        "--",
        relative_path,
        category="staged_entry_unreadable",
    )
    records = output[:-1].split(b"\0") if output.endswith(b"\0") and output else []
    if len(records) != 1 or b"\t" not in records[0]:
        raise PrivacyValidationError(
            "staged artifact validation failed [staged_entry_unreadable]"
        )
    metadata, raw_path = records[0].split(b"\t", 1)
    try:
        mode, object_id, stage = metadata.decode("ascii").split()
        indexed_path = raw_path.decode("utf-8")
    except (UnicodeDecodeError, ValueError) as error:
        raise PrivacyValidationError(
            "staged artifact validation failed [staged_entry_undecodable]"
        ) from error
    if stage != "0" or indexed_path != relative_path or not re.fullmatch(
        r"[0-9a-fA-F]{40}|[0-9a-fA-F]{64}", object_id
    ):
        raise PrivacyValidationError(
            "staged artifact validation failed [staged_entry_unreadable]"
        )
    return mode, object_id.lower()


def scan_staged_artifacts(repository_root: str | Path) -> StagedPrivacyScan:
    """Scan non-deleted staged entries from exact index objects, independent of CWD."""
    root = _anchored_repository_root(repository_root)
    output = _run_staged_git(
        root,
        "diff",
        "--cached",
        "--name-only",
        "-z",
        "--no-renames",
        "--diff-filter=ACMRT",
        category="staged_diff_unreadable",
    )
    relative_paths = tuple(_validated_relative_path(path) for path in _decode_nul_paths(output))
    paths: list[Path] = []
    findings: list[PrivacyFinding] = []
    for relative_path in relative_paths:
        display_path = root.joinpath(*PurePosixPath(relative_path).parts)
        paths.append(display_path)
        for kind in public_path_finding_kinds(relative_path):
            findings.append(PrivacyFinding(path=display_path, line=1, kind=kind))
        mode, object_id = _staged_entry(root, relative_path)
        if mode not in {"100644", "100755"}:
            findings.append(
                PrivacyFinding(path=display_path, line=1, kind="non_regular_staged_entry")
            )
            continue
        content = _run_staged_git(
            root,
            "cat-file",
            "blob",
            object_id,
            category="staged_object_unreadable",
        )
        findings.extend(
            PrivacyFinding(path=display_path, line=line, kind=kind)
            for line, kind in public_artifact_byte_findings(
                content, relative_path=relative_path
            )
        )
    return StagedPrivacyScan(root, tuple(paths), tuple(findings))


def validate_tracked_artifacts(paths: Iterable[Path]) -> list[PrivacyFinding]:
    """Return privacy findings for proposed public artifacts without reading ignored data zones."""
    findings: list[PrivacyFinding] = []
    for path in paths:
        candidate = Path(path)
        try:
            content = candidate.read_bytes()
        except OSError as error:
            raise PrivacyValidationError(
                "tracked artifact validation failed [artifact_unreadable]"
            ) from error
        findings.extend(
            PrivacyFinding(path=candidate, line=line, kind=kind)
            for line, kind in public_artifact_byte_findings(
                content, relative_path=candidate.name
            )
        )
    return findings
