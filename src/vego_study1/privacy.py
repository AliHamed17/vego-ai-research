"""Privacy-safe validation for the Study 1 candidate-event contract."""

from __future__ import annotations

import ast
import hashlib
import io
import ipaddress
import json
import math
import re
import subprocess
import tokenize
import unicodedata
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any
from urllib.parse import unquote, urlsplit
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
    (
        "drive_url",
        re.compile(
            r"(?i)https?://(?:drive|docs)\.google\.com/"
            r"|https?://drive\.usercontent\.google\.com/"
            r"|https?://(?:drive|docs)\.googleusercontent\.com/"
            r"|https?://(?:www\.)?googledrive\.com/"
        ),
    ),
    (
        "drive_id",
        re.compile(
            r"(?<!sha256:)(?:(?<=[/]d[/])1[A-Za-z0-9_-]{24,}(?=[/?#\s\"']|$)"
            r"|(?<![A-Za-z0-9_./-])"
            r"(?!(?:[0-9a-f]{40}|[0-9a-f]{64}|[0-9a-f]{128})(?![A-Za-z0-9_./-]))"
            r"1[A-Za-z0-9_-]{24,}(?![A-Za-z0-9_./-]))"
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
            r"(?i)(?<![\w+.-])(?:\\\\[\w][\w._-]*[\\/]"
            r"|(?<!:)//[\w][\w._-]*/"
            r"|(?:file|s3|ssh|ftp|git):(?://)?"
            r"|(?!(?:https?|sha256|pkg|urn|vego-ai):)[a-z][a-z0-9+.-]*://)"
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
PYTHON_ARTIFACT_SUFFIXES = frozenset({".py", ".pyi"})
PUBLIC_URI_SCHEMES = frozenset({"http", "https", "pkg", "sha256", "urn", "vego-ai"})
REVIEWED_GENERATED_ARTIFACT_SHA256 = {
    "VEGO-AI-Research-Hub.html": (
        "aabe3813951cc0e59669a1a45bf84f3cf6fc6a7396b52b1d701aa40959c14121"
    ),
    "VEGO-AI-Thesis-Baseline-Progress.html": (
        "c64f764fde9666446e8a76fd76cdf6a97b7bf71d17bdd814936deef53ac2da9d"
    ),
    "docs/research/thesis-evidence/thesis-evidence-snapshot-v1.json": (
        "c9703b84e369de926fec7a585969806ac70b69a6b219e7c80b5ec5f89ba80dad"
    ),
}
URI_SCHEME_PATTERN = re.compile(r"^(?P<scheme>[A-Za-z][A-Za-z0-9+.-]*):")
PRIVATE_HOST_PATTERN = re.compile(
    r"(?i)^(?:localhost|127\.0\.0\.1|(?:[a-z0-9-]+\.)+(?:internal|private|local))$"
)
URL_TOKEN_PATTERN = re.compile(r"(?i)\bhttps?://[^\s<>\"'`]+")
URI_TOKEN_PATTERN = re.compile(
    r"(?i)(?<![a-z0-9+._\\{\[-])(?P<scheme>[a-z][a-z0-9+.-]*):"
    r"(?P<remainder>[a-z0-9/%\\][^\s<>\"'`]*)"
)
WINDOWS_ABSOLUTE_PATH_TOKEN_PATTERN = re.compile(
    r"(?i)(?<![a-z0-9])[a-z]:[\\/][^\s<>\"'`|]+"
)
POSIX_ABSOLUTE_PATH_TOKEN_PATTERN = re.compile(
    r"(?i)(?<![:/\\}\]\w])/(?!/)[\w._~][\w._~-]*"
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
BARE_IPV6_TOKEN_PATTERN = re.compile(
    r"(?i)(?<![0-9a-f:])(?:"
    r"(?:[0-9a-f]{1,4}:){2,7}[0-9a-f]{1,4}"
    r"|(?:[0-9a-f]{1,4}:){1,7}:[0-9a-f]{0,4}"
    r")(?![0-9a-f:])"
)
CREDENTIAL_KEY_FRAGMENT_PATTERN = re.compile(
    r"(?i)api(?:key|keys)|token|secret|password|credential"
)
SAFE_CREDENTIAL_METADATA_KEYS = frozenset({"secretscan", "secretscanstatus"})
CREDENTIAL_PLACEHOLDER_PATTERNS = (
    re.compile(r"^\$\{[A-Za-z_][A-Za-z0-9_]*\}$"),
    re.compile(r"^\{\{\s*[A-Za-z_][A-Za-z0-9_.-]*\s*\}\}$"),
)
CREDENTIAL_TEXT_ASSIGNMENT_PATTERN = re.compile(
    r'''(?ix)(?<![\w.-])(?P<key>["']?[\w.-]+["']?)\s*[:=]\s*'''
    r'''(?P<value>"(?:[\x5c].|[^"\x5c\r\n])*"(?=\s*(?:$|[,;#\]\}]))|'''
    r''' '(?:[\x5c].|[^'\x5c\r\n])*'(?=\s*(?:$|[,;#\]\}]))'''
    r'''|[^\r\n]*)'''
)
CREDENTIAL_PLACEHOLDER_LITERALS = frozenset(
    {"", "redacted", "[redacted]", "<redacted>", "placeholder", "unset", "null", "none"}
)
DRIVE_HOSTS = frozenset(
    {
        "drive.google.com",
        "docs.google.com",
        "drive.usercontent.google.com",
        "drive.googleusercontent.com",
        "docs.googleusercontent.com",
        "googledrive.com",
        "www.googledrive.com",
    }
)
DRIVE_ID_CONTEXT_PATTERN = re.compile(
    r"(?i)(?:/(?:d|folders|host)/|[?&]id=)[A-Za-z0-9_-]{20,}"
)
LEGACY_DRIVE_ID_PATTERN = re.compile(
    r"(?<!sha256:)(?<![A-Za-z0-9_./-])"
    r"(?!(?:[0-9a-f]{40}|[0-9a-f]{64}|[0-9a-f]{128})(?![A-Za-z0-9_./-]))"
    r"(?:1[A-Za-z0-9_-]{24,}|0B[A-Za-z0-9_-]{22,})"
    r"(?![A-Za-z0-9_./-])"
)
_UNICODE_PATH_SEPARATORS = str.maketrans(
    {
        "\u2044": "/",
        "\u2215": "/",
        "\u29f8": "/",
        "\uff0f": "/",
        "\u29f5": "\\",
        "\ufe68": "\\",
        "\uff3c": "\\",
    }
)


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


def _is_credential_field_name(value: str | None) -> bool:
    if value is None:
        return False
    normalized = _normalized_structured_scalar(value)
    camel_separated = re.sub(r"(?<=[a-z0-9])(?=[A-Z])", " ", normalized)
    compact = re.sub(r"[^a-z0-9]", "", camel_separated.casefold())
    if compact in SAFE_CREDENTIAL_METADATA_KEYS:
        return False
    return CREDENTIAL_KEY_FRAGMENT_PATTERN.search(compact) is not None


def _credential_value_is_placeholder(value: str) -> bool:
    normalized = _normalized_structured_scalar(value)
    if normalized.casefold() in CREDENTIAL_PLACEHOLDER_LITERALS:
        return True
    return any(pattern.fullmatch(normalized) for pattern in CREDENTIAL_PLACEHOLDER_PATTERNS)


def _text_assignment_value_is_placeholder(value: str) -> bool:
    normalized = _normalized_structured_scalar(value)
    if len(normalized) >= 2 and normalized[0] == normalized[-1] and normalized[0] in {"'", '"'}:
        normalized = normalized[1:-1]
    else:
        comment = re.search(r"\s+#", normalized)
        if comment is not None:
            normalized = normalized[: comment.start()].rstrip()
    return _credential_value_is_placeholder(normalized)


def _json_scalar_values(
    value: Any, *, associated_key: str | None = None
) -> Iterable[tuple[int, str, str | None]]:
    if isinstance(value, str):
        yield 1, value, associated_key
    elif isinstance(value, bool):
        yield 1, "true" if value else "false", associated_key
    elif isinstance(value, (int, float)):
        yield 1, str(value), associated_key
    elif isinstance(value, _JsonObjectPairs):
        for key, item in value:
            yield 1, key, None
            inherited_credential_key = (
                associated_key if _is_credential_field_name(associated_key) else None
            )
            yield from _json_scalar_values(
                item,
                associated_key=inherited_credential_key or key,
            )
    elif isinstance(value, list):
        for item in value:
            yield from _json_scalar_values(item, associated_key=associated_key)


def _yaml_scalar_values(
    documents: Iterable[Node | None],
) -> Iterable[tuple[int, str, str | None]]:
    active: set[int] = set()

    def _walk(
        node: Node | None, *, associated_key: str | None = None
    ) -> Iterable[tuple[int, str, str | None]]:
        if node is None or id(node) in active:
            return
        active.add(id(node))
        try:
            if isinstance(node, ScalarNode):
                yield node.start_mark.line + 1, node.value, associated_key
            elif isinstance(node, SequenceNode):
                for item in node.value:
                    yield from _walk(item, associated_key=associated_key)
            elif isinstance(node, MappingNode):
                for key, item in node.value:
                    yield from _walk(key)
                    key_value = key.value if isinstance(key, ScalarNode) else None
                    inherited_credential_key = (
                        associated_key if _is_credential_field_name(associated_key) else None
                    )
                    yield from _walk(
                        item,
                        associated_key=inherited_credential_key or key_value,
                    )
        finally:
            active.remove(id(node))

    for document in documents:
        yield from _walk(document)


def _normalized_structured_scalar(value: str) -> str:
    decoded = unquote(value)
    normalized = unicodedata.normalize("NFKC", decoded).translate(_UNICODE_PATH_SEPARATORS)
    normalized = normalized.replace("\r\n", "\n").replace("\r", "\n")
    normalized = re.sub(
        r"[\u200b\u200c\u200d\u202a-\u202e\u2060\u2066-\u2069\ufeff]",
        "",
        normalized,
    )
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


def _text_finding_kinds(value: str, *, include_credentials: bool = True) -> tuple[str, ...]:
    """Extract and classify privacy-sensitive tokens from arbitrary decoded text."""
    normalized = _normalized_structured_scalar(value)
    findings = [
        kind
        for kind, pattern in PUBLIC_ARTIFACT_PATTERNS
        if (include_credentials or kind != "credential_like") and pattern.search(normalized)
    ]
    if WINDOWS_ABSOLUTE_PATH_TOKEN_PATTERN.search(
        normalized
    ) or POSIX_ABSOLUTE_PATH_TOKEN_PATTERN.search(normalized):
        findings.append("absolute_path_reference")
    if EMAIL_IDENTIFIER_PATTERN.search(normalized):
        findings.append("email_identifier")
    if include_credentials and any(
        _is_credential_field_name(match.group("key"))
        and not _text_assignment_value_is_placeholder(match.group("value"))
        for match in CREDENTIAL_TEXT_ASSIGNMENT_PATTERN.finditer(normalized)
    ):
        findings.append("credential_like")

    for match in URI_TOKEN_PATTERN.finditer(normalized):
        scheme = match.group("scheme").casefold()
        remainder = match.group("remainder")
        if len(scheme) == 1 and remainder.startswith(("/", "\\")):
            continue
        if scheme not in PUBLIC_URI_SCHEMES or (
            scheme == "sha256" and remainder.startswith(("/", "\\"))
        ):
            findings.append("remote_or_unc_reference")

    for match in URL_TOKEN_PATTERN.finditer(normalized):
        try:
            hostname = urlsplit(match.group(0)).hostname
        except ValueError:
            hostname = None
        if hostname is not None:
            normalized_host = hostname.casefold().rstrip(".")
            if normalized_host in DRIVE_HOSTS:
                findings.append("drive_url")
            if _is_private_host(normalized_host):
                findings.append("private_url")

    if DRIVE_ID_CONTEXT_PATTERN.search(normalized) or LEGACY_DRIVE_ID_PATTERN.search(normalized):
        findings.append("drive_id")

    host_tokens = (
        *(match.group(0) for match in IPV4_TOKEN_PATTERN.finditer(normalized)),
        *(match.group(0) for match in BRACKETED_IPV6_TOKEN_PATTERN.finditer(normalized)),
        *(match.group(0) for match in BARE_IPV6_TOKEN_PATTERN.finditer(normalized)),
    )
    if any(_is_private_host(token) for token in host_tokens):
        findings.append("private_host_reference")
    return tuple(dict.fromkeys(findings))


def _python_regex_constructor_names(tree: ast.AST | None) -> tuple[set[str], set[str]]:
    """Return imported module and function names used for regular-expression compilation."""
    modules = {"re", "regex"}
    functions: set[str] = set()
    if tree is None:
        return modules, functions
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name in {"re", "regex"}:
                    modules.add(alias.asname or alias.name)
        elif isinstance(node, ast.ImportFrom) and node.module in {"re", "regex"}:
            for alias in node.names:
                if alias.name == "compile":
                    functions.add(alias.asname or alias.name)
    return modules, functions


def _python_regex_string_token_indexes(
    tokens: tuple[tokenize.TokenInfo, ...], tree: ast.AST | None
) -> set[int]:
    """Identify string tokens passed to a known regular-expression compiler."""
    modules, functions = _python_regex_constructor_names(tree)
    significant_indexes = [
        index
        for index, token in enumerate(tokens)
        if token.type
        not in {
            tokenize.ENCODING,
            tokenize.INDENT,
            tokenize.DEDENT,
            tokenize.NL,
            tokenize.NEWLINE,
            tokenize.COMMENT,
            tokenize.ENDMARKER,
        }
    ]
    significant_position = {index: position for position, index in enumerate(significant_indexes)}
    regex_string_indexes: set[int] = set()
    delimiter_stack: list[tuple[str, bool]] = []
    for index, token in enumerate(tokens):
        if token.type == tokenize.OP and token.string in "([{":
            position = significant_position.get(index)
            is_regex_call = False
            if position is not None and position >= 1:
                previous = [tokens[item] for item in significant_indexes[position - 3 : position]]
                if len(previous) >= 3:
                    is_regex_call = (
                        previous[-3].type == tokenize.NAME
                        and previous[-3].string in modules
                        and previous[-2].string == "."
                        and previous[-1].type == tokenize.NAME
                        and previous[-1].string == "compile"
                    )
                if not is_regex_call and len(previous) >= 1:
                    is_regex_call = (
                        previous[-1].type == tokenize.NAME
                        and previous[-1].string in functions
                    )
            delimiter_stack.append((token.string, is_regex_call))
        elif token.type == tokenize.STRING and any(
            is_regex_call for _delimiter, is_regex_call in delimiter_stack
        ):
            regex_string_indexes.add(index)
        elif token.type == tokenize.OP and token.string in ")]}" and delimiter_stack:
            delimiter_stack.pop()
    return regex_string_indexes


def _python_literal_scalar(node: ast.AST | None) -> str | None:
    """Return a directly written scalar value, preserving strict placeholder handling."""
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
        left = _python_literal_string(node.left)
        right = _python_literal_string(node.right)
        if left is not None and right is not None:
            return left + right
        return None
    literal_string = _python_literal_string(node)
    if literal_string is not None:
        return literal_string
    if not isinstance(node, ast.Constant):
        return None
    value = node.value
    if isinstance(value, bool):
        return "true" if value else "false"
    if value is None:
        return "none"
    if isinstance(value, (int, float)):
        return str(value)
    return None


def _python_literal_string(node: ast.AST | None) -> str | None:
    """Return statically written string content without evaluating arbitrary Python code."""
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    if isinstance(node, ast.JoinedStr):
        parts: list[str] = []
        for value in node.values:
            if not isinstance(value, ast.Constant) or not isinstance(value.value, str):
                return None
            parts.append(value.value)
        return "".join(parts)
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
        left = _python_literal_string(node.left)
        right = _python_literal_string(node.right)
        if left is not None and right is not None:
            return left + right
    return None


def _python_credential_assignment_findings(tree: ast.AST) -> set[int]:
    """Find literal credential assignments represented by Python's parsed syntax tree."""
    lines: set[int] = set()

    def add_if_credential(target: ast.AST | None, value: ast.AST | None) -> None:
        if not isinstance(target, (ast.Name, ast.Attribute)):
            return
        name = target.id if isinstance(target, ast.Name) else target.attr
        if not _is_credential_field_name(name):
            return
        scalar = _python_literal_scalar(value)
        if scalar is not None and not _credential_value_is_placeholder(scalar):
            lines.add(getattr(target, "lineno", getattr(value, "lineno", 1)))

    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                add_if_credential(target, node.value)
        elif isinstance(node, ast.AnnAssign):
            add_if_credential(node.target, node.value)
        elif isinstance(node, ast.NamedExpr):
            add_if_credential(node.target, node.value)
        elif isinstance(node, ast.keyword) and node.arg is not None:
            add_if_credential(ast.Name(id=node.arg), node.value)
        elif isinstance(node, ast.Dict):
            for key, value in zip(node.keys, node.values, strict=True):
                if isinstance(key, ast.Constant) and isinstance(key.value, str):
                    add_if_credential(ast.Name(id=key.value), value)
    return lines


def _python_credential_finding_lines(text: str) -> set[int] | None:
    """Return credential findings for Python syntax, or ``None`` when parsing must fail closed."""
    try:
        tree = ast.parse(text)
        tokens = tuple(tokenize.generate_tokens(io.StringIO(text).readline))
    except (IndentationError, SyntaxError, tokenize.TokenError):
        return None

    findings = _python_credential_assignment_findings(tree)
    regex_string_indexes = _python_regex_string_token_indexes(tokens, tree)
    for index, token in enumerate(tokens):
        if token.type == tokenize.COMMENT or (
            token.type == tokenize.STRING and index not in regex_string_indexes
        ):
            if "credential_like" in _text_finding_kinds(token.string):
                findings.add(token.start[0])
    return findings


def _structured_mapping_finding_kinds(key: str | None, value: str) -> tuple[str, ...]:
    """Classify a decoded scalar while retaining its immediate mapping-key context."""
    if not _is_credential_field_name(key):
        return ()
    if _credential_value_is_placeholder(value):
        return ()
    return ("credential_like",)


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

    normalized_path = PurePosixPath(relative_path.replace("\\", "/")).as_posix()
    reviewed_hash = REVIEWED_GENERATED_ARTIFACT_SHA256.get(normalized_path)
    if reviewed_hash is not None and hashlib.sha256(content).hexdigest() == reviewed_hash:
        return ()

    findings: list[tuple[int, str]] = []
    suffix = PurePosixPath(relative_path).suffix.casefold()
    python_credential_lines = (
        _python_credential_finding_lines(text)
        if suffix in PYTHON_ARTIFACT_SUFFIXES
        else None
    )
    for line_number, line in enumerate(text.splitlines(), start=1):
        findings.extend(
            (line_number, kind)
            for kind in _text_finding_kinds(
                line,
                include_credentials=(
                    suffix not in PYTHON_ARTIFACT_SUFFIXES or python_credential_lines is None
                ),
            )
        )
        if python_credential_lines is not None and line_number in python_credential_lines:
            findings.append((line_number, "credential_like"))

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
