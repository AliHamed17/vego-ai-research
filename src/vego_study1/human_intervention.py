"""Bounded, offline replay of one simulated human correction for Study 1.

The transformation is deliberately narrow: it may replace exactly one uncovered-
fragment label already present in a frozen Agent C record and deterministically
propagate that replacement through the existing scoring schema.  It is development
evidence of technical propagation, not an accuracy or human-benefit evaluation.
"""

from __future__ import annotations

import hashlib
import json
from copy import deepcopy
from pathlib import Path
from typing import Any

from .path_safety import (
    assert_local_file_unchanged,
    atomic_write_private_text,
    ensure_private_directory,
    local_path,
    read_local_bytes,
    validate_private_output_root,
)


class HumanInterventionValidationError(ValueError):
    """Raised when a simulated intervention exceeds the bounded replay contract."""


_ALLOWED_LABELS = frozenset({"Alternative", "Domain Mistake", "Language Mistake"})
_ALLOWED_SEVERITIES = frozenset({"N/A", "High", "Medium", "Low"})
REPOSITORY_ROOT = Path(__file__).resolve().parents[2]


def _sha256(value: object) -> str:
    return hashlib.sha256(str(value).encode("utf-8")).hexdigest()


def _parse_scoring_schema(schema_text: str) -> dict[str, float]:
    scores: dict[str, float] = {}
    for raw_line in schema_text.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        parts = [part.strip() for part in line.split("|")]
        if len(parts) < 2:
            continue
        try:
            scores[parts[0].casefold()] = float(parts[1].lstrip("+"))
        except ValueError:
            continue
    return scores


def _required_text(mapping: dict[str, Any], field: str) -> str:
    value = mapping.get(field)
    if not isinstance(value, str) or not value.strip():
        raise HumanInterventionValidationError(f"{field} must be non-empty text")
    return value


def apply_fragment_label_intervention(
    case_record: dict[str, Any],
    intervention: dict[str, Any],
    scoring_schema_text: str,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Apply one development-only label correction and return a sanitized receipt."""
    if intervention.get("schema_version") != "study1-human-intervention-v1":
        raise HumanInterventionValidationError("unsupported schema_version")
    if intervention.get("reference_status") != "development_only":
        raise HumanInterventionValidationError("reference_status must be development_only")
    if intervention.get("claim_boundary") != "technical_propagation_only":
        raise HumanInterventionValidationError("claim_boundary must be technical_propagation_only")
    if intervention.get("human_input_mode") != "simulated_from_recorded_review":
        raise HumanInterventionValidationError(
            "human_input_mode must be simulated_from_recorded_review"
        )
    if intervention.get("source_kind") != "recorded_human_review":
        raise HumanInterventionValidationError("source_kind must be recorded_human_review")

    intervention_id = _required_text(intervention, "intervention_id")
    target_hash = _required_text(intervention, "target_fragment_sha256")
    if len(target_hash) != 64 or any(ch not in "0123456789abcdef" for ch in target_hash):
        raise HumanInterventionValidationError("target_fragment_sha256 must be lowercase SHA-256")
    baseline_label = _required_text(intervention, "expected_baseline_label")
    replacement_label = _required_text(intervention, "replacement_label")
    replacement_severity = _required_text(intervention, "replacement_severity")
    if replacement_label not in _ALLOWED_LABELS:
        raise HumanInterventionValidationError("unsupported replacement_label")
    if replacement_severity not in _ALLOWED_SEVERITIES:
        raise HumanInterventionValidationError("unsupported replacement_severity")
    if baseline_label == replacement_label:
        raise HumanInterventionValidationError("replacement_label must change the baseline")

    assisted = deepcopy(case_record)
    fragments = assisted.get("uncovered_fragments")
    contributions = assisted.get("fragment_contributions")
    if not isinstance(fragments, list) or not isinstance(contributions, list):
        raise HumanInterventionValidationError(
            "case record must contain uncovered_fragments and fragment_contributions"
        )

    fragment_matches = [
        item
        for item in fragments
        if isinstance(item, dict) and _sha256(item.get("fragment", "")) == target_hash
    ]
    contribution_matches = [
        item
        for item in contributions
        if isinstance(item, dict) and _sha256(item.get("fragment", "")) == target_hash
    ]
    if len(fragment_matches) != 1 or len(contribution_matches) != 1:
        raise HumanInterventionValidationError(
            "intervention must match exactly one fragment and one contribution"
        )

    fragment = fragment_matches[0]
    contribution = contribution_matches[0]
    if fragment.get("label") != baseline_label or contribution.get("label") != baseline_label:
        raise HumanInterventionValidationError(
            "baseline label changed since the intervention freeze"
        )

    scores = _parse_scoring_schema(scoring_schema_text)
    label_score = scores.get(replacement_label.casefold())
    if label_score is None:
        raise HumanInterventionValidationError("replacement_label is absent from scoring schema")
    severity_score = 0.0
    if replacement_severity != "N/A":
        severity_score = scores.get(f"severity-{replacement_severity}".casefold(), 0.0)

    try:
        old_contribution = float(contribution["total_contribution"])
        baseline_total = float(assisted["total_score"])
        max_score = float(assisted["max_score"])
        baseline_pct = float(assisted["score_pct"])
    except (KeyError, TypeError, ValueError) as error:
        raise HumanInterventionValidationError("case record score fields are invalid") from error
    if max_score <= 0:
        raise HumanInterventionValidationError("case record max_score must be positive")

    new_contribution = label_score + severity_score
    assisted_total = baseline_total - old_contribution + new_contribution
    assisted_pct = round(assisted_total / max_score * 100, 1)

    fragment["label"] = replacement_label
    fragment["severity"] = replacement_severity
    fragment["reason"] = "Bounded simulated human correction from the recorded review."
    contribution.update(
        {
            "label": replacement_label,
            "severity": replacement_severity,
            "base_score": label_score,
            "severity_modifier": severity_score,
            "total_contribution": new_contribution,
            "note": "Simulated bounded human correction; development-only evidence.",
        }
    )
    assisted["total_score"] = assisted_total
    assisted["score_pct"] = assisted_pct

    case_id = _required_text(assisted, "case_id")
    receipt = {
        "schema_version": "study1-human-intervention-receipt-v1",
        "intervention_id": intervention_id,
        "case_id_sha256": _sha256(case_id),
        "target_fragment_sha256": target_hash,
        "baseline_label": baseline_label,
        "assisted_label": replacement_label,
        "baseline_total_score": baseline_total,
        "assisted_total_score": assisted_total,
        "baseline_score_pct": baseline_pct,
        "assisted_score_pct": assisted_pct,
        "score_delta": new_contribution - old_contribution,
        "recorded_review_alignment_before": 0,
        "recorded_review_alignment_after": 1,
        "technical_propagation_success": True,
        "reference_status": "development_only",
        "claim_boundary": "technical_propagation_only",
    }
    return assisted, receipt


def _json_object(content: bytes, field_name: str) -> dict[str, Any]:
    try:
        value = json.loads(content.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise HumanInterventionValidationError(
            f"{field_name} must contain a UTF-8 JSON object"
        ) from error
    if not isinstance(value, dict):
        raise HumanInterventionValidationError(f"{field_name} must contain a JSON object")
    return value


def _canonical_json(value: Any) -> str:
    return (
        json.dumps(
            value,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        )
        + "\n"
    )


def _content_hash(content: bytes) -> str:
    return "sha256:" + hashlib.sha256(content).hexdigest()


def write_intervention_replay(
    case_path: str | Path,
    intervention_path: str | Path,
    scoring_schema_path: str | Path,
    private_output_root: str | Path,
) -> dict[str, Any]:
    """Read immutable local inputs and write full/private plus sanitized receipts."""
    case_source = local_path(case_path, "case_path", HumanInterventionValidationError)
    intervention_source = local_path(
        intervention_path,
        "intervention_path",
        HumanInterventionValidationError,
    )
    schema_source = local_path(
        scoring_schema_path,
        "scoring_schema_path",
        HumanInterventionValidationError,
    )
    case_bytes = read_local_bytes(
        case_source,
        "case_path",
        HumanInterventionValidationError,
    )
    intervention_bytes = read_local_bytes(
        intervention_source,
        "intervention_path",
        HumanInterventionValidationError,
    )
    schema_bytes = read_local_bytes(
        schema_source,
        "scoring_schema_path",
        HumanInterventionValidationError,
    )
    try:
        schema_text = schema_bytes.decode("utf-8")
    except UnicodeDecodeError as error:
        raise HumanInterventionValidationError(
            "scoring_schema_path must contain UTF-8 text"
        ) from error

    assisted, receipt = apply_fragment_label_intervention(
        _json_object(case_bytes, "case_path"),
        _json_object(intervention_bytes, "intervention_path"),
        schema_text,
    )
    receipt["input_hashes"] = {
        "case_record": _content_hash(case_bytes),
        "intervention_directive": _content_hash(intervention_bytes),
        "scoring_schema": _content_hash(schema_bytes),
    }

    root = validate_private_output_root(
        private_output_root,
        REPOSITORY_ROOT,
        HumanInterventionValidationError,
    )
    ensure_private_directory(
        root,
        root,
        REPOSITORY_ROOT,
        HumanInterventionValidationError,
    )
    assert_local_file_unchanged(
        case_source,
        case_bytes,
        "case_path",
        HumanInterventionValidationError,
    )
    assert_local_file_unchanged(
        intervention_source,
        intervention_bytes,
        "intervention_path",
        HumanInterventionValidationError,
    )
    assert_local_file_unchanged(
        schema_source,
        schema_bytes,
        "scoring_schema_path",
        HumanInterventionValidationError,
    )
    atomic_write_private_text(
        root / "assisted-case.private.json",
        _canonical_json(assisted),
        root,
        REPOSITORY_ROOT,
        HumanInterventionValidationError,
    )
    atomic_write_private_text(
        root / "receipt.sanitized.json",
        _canonical_json(receipt),
        root,
        REPOSITORY_ROOT,
        HumanInterventionValidationError,
    )
    return receipt
