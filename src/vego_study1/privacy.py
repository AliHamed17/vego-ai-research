"""Privacy-safe validation for the Study 1 candidate-event contract."""

from __future__ import annotations

import ipaddress
import json
import math
import re
import subprocess
import unicodedata
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any
from urllib.parse import urlsplit
from uuid import UUID

import yaml
from jsonschema import Draft202012Validator
from yaml.nodes import MappingNode, Node, ScalarNode, SequenceNode

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
SAFE_CANDIDATE_FIELD_NAMES = frozenset(
    {
        "root",
        "schema_version",
        "event_id",
        "source",
        "source_hash",
        "stage",
        "item_type",
        "sanitized_local_locator",
        "storage_scope",
        "locator_hash",
        "signals",
        "signal_id",
        "observation",
        "kind",
        "normalized_value",
        "missing_value_policy",
        "evidence_state",
        "escalation_request",
        "claim_boundary",
    }
)
SAFE_SCHEMA_VALIDATION_CATEGORIES = frozenset(
    {
        "additionalProperties",
        "const",
        "enum",
        "format",
        "maxContains",
        "maximum",
        "maxItems",
        "minContains",
        "minimum",
        "minItems",
        "oneOf",
        "pattern",
        "required",
        "type",
        "uniqueItems",
    }
)
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


def _safe_candidate_field(path: Iterable[object]) -> str:
    """Return only schema-owned field labels, never caller-controlled path components."""
    fields = [part for part in path if isinstance(part, str) and part in SAFE_CANDIDATE_FIELD_NAMES]
    return ".".join(fields) or "root"


def _safe_schema_category(value: object) -> str:
    if isinstance(value, str) and value in SAFE_SCHEMA_VALIDATION_CATEGORIES:
        return value
    return "schema"


def validate_candidate_event(
    event: dict[str, Any], *, schema: dict[str, Any] | None = None
) -> dict[str, Any]:
    """Validate a privacy-sanitized candidate event and return it unchanged."""
    non_finite_path = _non_finite_number_path(event)
    if non_finite_path is not None:
        raise PrivacyValidationError(
            f"candidate event validation at {_safe_candidate_field(non_finite_path)} "
            "[non_finite_number]"
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
    errors = sorted(
        validator.iter_errors(event),
        key=lambda error: (
            _safe_candidate_field(error.absolute_path),
            _safe_schema_category(error.validator),
        ),
    )
    if errors:
        error = errors[0]
        field = _safe_candidate_field(error.absolute_path)
        category = _safe_schema_category(error.validator)
        raise PrivacyValidationError(
            f"candidate event schema violation at {field} [{category}]"
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
    (
        "drive_id",
        re.compile(
            r"(?<!sha256:)(?:(?<=[/]d[/])1[A-Za-z0-9_-]{24,}(?=[/?#\s\"']|$)"
            r"|(?<![A-Za-z0-9_./-])1[A-Za-z0-9_-]{24,}(?![A-Za-z0-9_./-]))"
        ),
    ),
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
STRUCTURED_ARTIFACT_SUFFIXES = frozenset({".json", ".yaml", ".yml"})
PUBLIC_URI_SCHEMES = frozenset({"http", "https", "sha256"})
URI_SCHEME_PATTERN = re.compile(r"^(?P<scheme>[A-Za-z][A-Za-z0-9+.-]*):")
PRIVATE_HOST_PATTERN = re.compile(
    r"(?i)^(?:localhost|127\.0\.0\.1|(?:[a-z0-9-]+\.)+(?:internal|private|local))$"
)
URL_TOKEN_PATTERN = re.compile(r"(?i)\bhttps?://[^\s<>\"'`]+")
WINDOWS_ABSOLUTE_PATH_TOKEN_PATTERN = re.compile(
    r"(?i)(?<![a-z0-9])[a-z]:[\\/][^\s<>\"'`|]+"
)
POSIX_ABSOLUTE_PATH_TOKEN_PATTERN = re.compile(
    r"(?i)(?<![a-z0-9:/\\}\]])/(?!/)[a-z0-9._~][a-z0-9._~-]*"
    r"(?:/[^\s<>\"'`|]+)*"
)
EMAIL_IDENTIFIER_PATTERN = re.compile(
    r"(?i)(?<![a-z0-9._%+-])[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,63}"
    r"(?![a-z0-9.-])"
)
IPV4_TOKEN_PATTERN = re.compile(
    r"(?<![a-zA-Z0-9.])(?:\d{1,3}\.){3}\d{1,3}(?::\d+)?(?![a-zA-Z0-9.])"
)
BRACKETED_IPV6_TOKEN_PATTERN = re.compile(r"\[[0-9a-fA-F:.%]+\](?::\d+)?")
CREDENTIAL_FIELD_PATTERN = re.compile(
    r"(?i)^[a-z0-9_-]*(?:api[_-]?keys?|tokens?|secrets?|passwords?|credentials?)$"
)
CREDENTIAL_VALUE_PATTERN = re.compile(r"[A-Za-z0-9_./+=-]{8,}")


class _JsonObjectPairs(list[tuple[str, Any]]):
    """Preserve duplicate JSON members so every decoded key and value is scanned."""


def public_path_finding_kinds(relative_path: str) -> tuple[str, ...]:
    """Scan the complete validated repository-relative path for private metadata."""
    findings = [
        kind for kind, pattern in PROHIBITED_PUBLIC_PATH_PATTERNS if pattern.search(relative_path)
    ]
    findings.extend(_text_finding_kinds(relative_path))
    return tuple(dict.fromkeys(findings))


def _contains_non_finite_json_number(value: Any) -> bool:
    if isinstance(value, float):
        return not math.isfinite(value)
    if isinstance(value, _JsonObjectPairs):
        return any(
            _contains_non_finite_json_number(key) or _contains_non_finite_json_number(item)
            for key, item in value
        )
    if isinstance(value, dict):
        return any(_contains_non_finite_json_number(item) for item in value.values())
    if isinstance(value, (list, tuple)):
        return any(_contains_non_finite_json_number(item) for item in value)
    return False


def _json_object_pairs(pairs: list[tuple[str, Any]]) -> _JsonObjectPairs:
    return _JsonObjectPairs(pairs)


def _reject_non_standard_json_constant(_value: str) -> None:
    raise ValueError("non_standard_numeric_constant")


def _json_scalar_values(
    value: Any, *, associated_key: str | None = None
) -> Iterable[tuple[int, str, str | None]]:
    if isinstance(value, str):
        yield 1, value, associated_key
    elif isinstance(value, _JsonObjectPairs):
        for key, item in value:
            yield 1, key, None
            yield from _json_scalar_values(item, associated_key=key)
    elif isinstance(value, list):
        for item in value:
            yield from _json_scalar_values(item, associated_key=associated_key)


def _yaml_scalar_values(
    documents: Iterable[Node | None],
) -> Iterable[tuple[int, str, str | None]]:
    seen: set[int] = set()

    def _walk(
        node: Node | None, *, associated_key: str | None = None
    ) -> Iterable[tuple[int, str, str | None]]:
        if node is None or id(node) in seen:
            return
        seen.add(id(node))
        if isinstance(node, ScalarNode):
            yield node.start_mark.line + 1, node.value, associated_key
        elif isinstance(node, SequenceNode):
            for item in node.value:
                yield from _walk(item, associated_key=associated_key)
        elif isinstance(node, MappingNode):
            for key, item in node.value:
                yield from _walk(key)
                key_value = key.value if isinstance(key, ScalarNode) else None
                yield from _walk(item, associated_key=key_value)

    for document in documents:
        yield from _walk(document)


def _normalized_structured_scalar(value: str) -> str:
    normalized = unicodedata.normalize("NFKC", value)
    normalized = normalized.replace("\r\n", "\n").replace("\r", "\n")
    normalized = re.sub(r"[\u200b\u200c\u200d\u2060\ufeff]", "", normalized)
    return re.sub(r"\s+", " ", normalized).strip()


def _is_private_host(value: str) -> bool:
    candidate = value.casefold().strip().rstrip(".")
    if candidate.startswith("[") and candidate.endswith("]"):
        candidate = candidate[1:-1]
    elif candidate.count(":") == 1:
        host, separator, port = candidate.rpartition(":")
        if separator and port.isdigit():
            candidate = host.rstrip(".")
    if PRIVATE_HOST_PATTERN.fullmatch(candidate):
        return True
    try:
        address = ipaddress.ip_address(candidate)
    except ValueError:
        return False
    return address.is_private or address.is_loopback or address.is_link_local


def _text_finding_kinds(value: str) -> tuple[str, ...]:
    """Extract and classify privacy-sensitive tokens from arbitrary decoded text."""
    findings = [kind for kind, pattern in PUBLIC_ARTIFACT_PATTERNS if pattern.search(value)]
    if WINDOWS_ABSOLUTE_PATH_TOKEN_PATTERN.search(value) or POSIX_ABSOLUTE_PATH_TOKEN_PATTERN.search(
        value
    ):
        findings.append("absolute_path_reference")
    if EMAIL_IDENTIFIER_PATTERN.search(value):
        findings.append("email_identifier")

    for match in URL_TOKEN_PATTERN.finditer(value):
        try:
            hostname = urlsplit(match.group(0)).hostname
        except ValueError:
            hostname = None
        if hostname is not None and _is_private_host(hostname):
            findings.append("private_url")

    host_tokens = (
        *(match.group(0) for match in IPV4_TOKEN_PATTERN.finditer(value)),
        *(match.group(0) for match in BRACKETED_IPV6_TOKEN_PATTERN.finditer(value)),
    )
    if any(_is_private_host(token) for token in host_tokens):
        findings.append("private_host_reference")
    return tuple(dict.fromkeys(findings))


def _structured_mapping_finding_kinds(key: str | None, value: str) -> tuple[str, ...]:
    """Classify a decoded scalar while retaining its immediate mapping-key context."""
    if key is None:
        return ()
    normalized_key = _normalized_structured_scalar(key)
    if CREDENTIAL_FIELD_PATTERN.fullmatch(normalized_key) is None:
        return ()
    normalized_value = _normalized_structured_scalar(value)
    if normalized_value.startswith(("${", "{{")):
        return ()
    compact_value = re.sub(r"\s+", "", normalized_value)
    if CREDENTIAL_VALUE_PATTERN.fullmatch(compact_value) is not None:
        return ("credential_like",)
    return ()


def _structured_scalar_finding_kinds(value: str) -> tuple[str, ...]:
    """Classify one decoded scalar using fixed public/privacy boundary labels."""
    normalized = _normalized_structured_scalar(value)
    if not normalized:
        return ()

    findings = list(_text_finding_kinds(normalized))
    path_value = normalized.replace("\\", "/")
    if path_value.startswith("//"):
        findings.append("remote_or_unc_reference")
    elif re.match(r"^[A-Za-z]:/", path_value) or path_value.startswith("/"):
        findings.append("absolute_path_reference")

    scheme_match = URI_SCHEME_PATTERN.match(normalized)
    if scheme_match is not None and not re.match(r"^[A-Za-z]:[\\/]", normalized):
        scheme = scheme_match.group("scheme").casefold()
        remainder = normalized[scheme_match.end() :]
        if scheme not in PUBLIC_URI_SCHEMES or (
            scheme == "sha256" and remainder.startswith(("/", "\\"))
        ):
            findings.append("remote_or_unc_reference")
        elif scheme in {"http", "https"}:
            try:
                hostname = urlsplit(normalized).hostname
            except ValueError:
                hostname = None
            if hostname is not None and _is_private_host(hostname):
                findings.append("private_host_reference")

    if _is_private_host(normalized):
        findings.append("private_host_reference")
    return tuple(dict.fromkeys(findings))


def _decoded_structured_scalars(
    text: str, *, suffix: str
) -> tuple[tuple[tuple[int, str, str | None], ...], str | None]:
    """Return decoded scalars and an optional fixed parse-failure category."""
    if suffix == ".json":
        try:
            loaded = json.loads(
                text,
                parse_constant=_reject_non_standard_json_constant,
                object_pairs_hook=_json_object_pairs,
            )
        except json.JSONDecodeError:
            return (), "unparseable_structured_artifact"
        except ValueError as error:
            if str(error) == "non_standard_numeric_constant":
                return (), "non_finite_json_number"
            return (), "unparseable_structured_artifact"
        if _contains_non_finite_json_number(loaded):
            return tuple(_json_scalar_values(loaded)), "non_finite_json_number"
        return tuple(_json_scalar_values(loaded)), None

    try:
        documents = tuple(yaml.compose_all(text, Loader=yaml.SafeLoader))
    except yaml.YAMLError:
        return (), "unparseable_structured_artifact"
    return tuple(_yaml_scalar_values(documents)), None


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
        findings.extend((line_number, kind) for kind in _text_finding_kinds(line))

    suffix = PurePosixPath(relative_path).suffix.casefold()
    if suffix in STRUCTURED_ARTIFACT_SUFFIXES:
        scalars, parse_finding = _decoded_structured_scalars(text, suffix=suffix)
        if parse_finding is not None:
            findings.append((1, parse_finding))
        for line_number, value, associated_key in scalars:
            findings.extend(
                (line_number, kind) for kind in _structured_scalar_finding_kinds(value)
            )
            findings.extend(
                (line_number, kind)
                for kind in _structured_mapping_finding_kinds(associated_key, value)
            )
    return tuple(dict.fromkeys(findings))


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
