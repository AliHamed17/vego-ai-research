"""Privacy-safe validation for the Study 1 candidate-event contract."""

from __future__ import annotations

import json
import re
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from uuid import UUID

from jsonschema import Draft202012Validator

SIGNAL_IDS = frozenset(
    {
        "prompt_scope",
        "artifact_sensitivity",
        "identity_exposure",
        "evidence_conflict",
        "policy_uncertainty",
        "impact_severity",
        "human_review_need",
        "reversibility_risk",
    }
)
RAW_LOCATOR_KEYS = frozenset({"locator", "path", "raw_locator", "raw_content", "content"})
SCHEMA_PATH = Path(__file__).resolve().parents[2] / "schemas" / "study1" / "CandidateEscalationEvent-v1.schema.json"


class PrivacyValidationError(ValueError):
    """Raised when a candidate event or public artifact violates its privacy contract."""


@dataclass(frozen=True)
class PrivacyFinding:
    path: Path
    line: int
    kind: str


def _load_schema() -> dict[str, Any]:
    return json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))


def validate_candidate_event(event: dict[str, Any], *, schema: dict[str, Any] | None = None) -> dict[str, Any]:
    """Validate a privacy-sanitized candidate event and return it unchanged."""
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
            raise PrivacyValidationError("exactly one observation is required for every policy signal")

    validator = Draft202012Validator(schema or _load_schema())
    errors = sorted(validator.iter_errors(event), key=lambda error: list(error.absolute_path))
    if errors:
        error = errors[0]
        field = ".".join(str(part) for part in error.absolute_path)
        raise PrivacyValidationError(f"candidate event schema violation at {field or 'root'}: {error.message}")
    return event


_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("controlled_path", re.compile(r"(?i)(?:[a-z]:\\|/(?:home|users|private)/)")),
    ("controlled_content_marker", re.compile(r"(?i)RAW[_]CONTROLLED[_]CONTENT|CONTROLLED[_](?:STUDENT|EXPERT)|(?:STUDENT|EXPERT)[_]RAW[_]")),
    ("drive_url", re.compile(r"(?i)https?://(?:drive|docs)\.google\.com/")),
    ("drive_id", re.compile(r"\b1[A-Za-z0-9_-]{24,}\b")),
    ("private_url", re.compile(r"(?i)https?://(?:localhost|127\.0\.0\.1|[\w-]+\.(?:internal|private|local))/")),
    ("credential_like", re.compile(r"(?i)\b(?:api[_-]?key|token|secret|password|credential)\b\s*[:=]\s*(?!\$\{|\{\{)[A-Za-z0-9_./+=-]{8,}")),
)


def validate_tracked_artifacts(paths: Iterable[Path]) -> list[PrivacyFinding]:
    """Return privacy findings for proposed public artifacts without reading ignored data zones."""
    findings: list[PrivacyFinding] = []
    for path in paths:
        candidate = Path(path)
        if not candidate.is_file():
            continue
        try:
            lines = candidate.read_text(encoding="utf-8").splitlines()
        except UnicodeDecodeError:
            continue
        for line_number, line in enumerate(lines, start=1):
            for kind, pattern in _PATTERNS:
                if pattern.search(line):
                    findings.append(PrivacyFinding(path=candidate, line=line_number, kind=kind))
    return findings
