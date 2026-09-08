"""Shared per-case output contract used identically by both conditions."""

from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any

import jsonschema

from . import constants as c

ROOT = Path(__file__).resolve().parents[3]
OUTPUT_SCHEMA_PATH = ROOT / "schemas" / "study2-condition-output-v1.schema.json"
OUTPUT_SCHEMA = json.loads(OUTPUT_SCHEMA_PATH.read_text(encoding="utf-8"))
OUTPUT_SCHEMA_SHA256 = hashlib.sha256(OUTPUT_SCHEMA_PATH.read_bytes()).hexdigest()

ALLOWED_COMPLIANCE = ("Satisfied", "Partially-Satisfied", "Not-Satisfied")
ALLOWED_LABELS = ("Alternative", "Domain Mistake", "Language Mistake")
ALLOWED_SEVERITY = ("High", "Medium", "Low", "N/A")


class ContractError(ValueError):
    """Raised when a condition output cannot enter the shared comparison."""


def canonical_json(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(canonical_json(value)).hexdigest()


def validate_condition_output(payload: Any, *, condition: str, case_id: str) -> None:
    if not isinstance(payload, dict):
        raise ContractError("condition output must be a JSON object")
    try:
        jsonschema.Draft202012Validator(OUTPUT_SCHEMA).validate(payload)
    except jsonschema.ValidationError as exc:
        raise ContractError(f"schema: {exc.message}") from exc
    if payload.get("schema_version") != c.CONDITION_OUTPUT_SCHEMA:
        raise ContractError("schema_version mismatch")
    if payload.get("condition") != condition:
        raise ContractError("condition mismatch")
    if payload.get("case_id") != case_id:
        raise ContractError("case_id mismatch")
    for row in payload["existing_mapping"]:
        if row.get("compliance_status") not in ALLOWED_COMPLIANCE:
            raise ContractError("invalid compliance_status")
    for row in payload["uncovered_fragments"]:
        if row.get("label") not in ALLOWED_LABELS:
            raise ContractError("invalid fragment label")
        if row.get("severity") not in ALLOWED_SEVERITY:
            raise ContractError("invalid fragment severity")
    summary = payload["coverage_summary"]
    if set(summary) != {"satisfied", "partially_satisfied", "not_satisfied"}:
        raise ContractError("coverage_summary keys")
    if any(type(summary[k]) is not int or summary[k] < 0 for k in summary):
        raise ContractError("coverage_summary counts must be non-negative integers")


def on_payload_from_pipeline(case_id: str, vector: Any, fragments: Any) -> dict[str, Any]:
    """Adapt the protected pipeline's two per-case records to the shared contract.

    Nothing is coerced: a missing or mistyped part is left as-is so that the
    contract validator rejects it and the case is recorded as SCHEMA_INVALID.
    """
    vector = vector if isinstance(vector, dict) else {}
    fragments = fragments if isinstance(fragments, dict) else {}
    return {
        "schema_version": c.CONDITION_OUTPUT_SCHEMA,
        "condition": c.CONDITION_ON,
        "skill_version": str(vector.get("skill_version", fragments.get("skill_version", ""))),
        "case_id": case_id,
        "existing_mapping": vector.get("existing_mapping"),
        "coverage_summary": vector.get("coverage_summary"),
        "uncovered_fragments": fragments.get("uncovered_fragments"),
    }


def output_metrics(payload: dict[str, Any]) -> dict[str, Any]:
    """Structural metrics only; no text leaves this function."""
    mapping = payload["existing_mapping"]
    fragments = payload["uncovered_fragments"]
    status_counts = Counter(row["compliance_status"] for row in mapping)
    recomputed = {
        "satisfied": status_counts.get("Satisfied", 0),
        "partially_satisfied": status_counts.get("Partially-Satisfied", 0),
        "not_satisfied": status_counts.get("Not-Satisfied", 0),
    }
    guideline_ids = [row["guideline_id"] for row in mapping]
    return {
        "mapping_rows": len(mapping),
        "distinct_guideline_ids": len(set(guideline_ids)),
        "duplicate_guideline_ids": len(guideline_ids) - len(set(guideline_ids)),
        "coverage_summary_reported": dict(payload["coverage_summary"]),
        "coverage_summary_recomputed": recomputed,
        "coverage_summary_consistent": recomputed == payload["coverage_summary"],
        "empty_evidence_rows": sum(1 for row in mapping if not str(row.get("evidence", "")).strip()),
        "uncovered_fragments": len(fragments),
        "fragment_labels": {label: sum(1 for f in fragments if f["label"] == label) for label in ALLOWED_LABELS},
        "fragment_severity": {sev: sum(1 for f in fragments if f["severity"] == sev) for sev in ALLOWED_SEVERITY},
        "empty_reason_rows": sum(1 for f in fragments if not str(f.get("reason", "")).strip()),
    }
