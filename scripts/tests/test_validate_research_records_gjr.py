"""GovernedJudgmentRecord-v1 semantic branch of validate_research_records.py.

Constraints under test: the ExperimentDefinition-v3 schema is registered; the
GovernedJudgmentRecord-v1 referential invariants (claim-id agreement across
competence/authority/caseGrounding, decision-trace evidence resolution,
rationale trace-slot resolution, use-receipt retrieval resolution, revocation
reason/authority non-null) each fire on a mutated copy of the shipped valid
example and stay silent on the intact example and on records whose optional
sections are absent. Mechanism checks only; nothing here is empirical
evidence of any outcome (EXP-005 0/24).
"""

from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
VALIDATOR_PATH = ROOT / "scripts/validate_research_records.py"
EXAMPLE_PATH = ROOT / "schemas/examples/governed-judgment-record.valid.json"

_spec = importlib.util.spec_from_file_location(
    "validate_research_records", VALIDATOR_PATH
)
assert _spec is not None and _spec.loader is not None
validator = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(validator)


def _example() -> dict[str, Any]:
    return json.loads(EXAMPLE_PATH.read_text(encoding="utf-8"))


def test_experiment_definition_v3_schema_is_registered() -> None:
    path = validator.SCHEMAS["ExperimentDefinition-v3"]
    assert path.name == "experiment-definition-v3.schema.json"
    assert path.is_file()


def test_valid_example_has_no_semantic_errors() -> None:
    assert validator.semantic_errors(_example()) == []


def test_valid_example_passes_full_validation() -> None:
    assert validator.validate_record(_example()) == []


def test_competence_claim_mismatch_is_flagged() -> None:
    record = _example()
    record["competence"]["assessedForClaimId"] = "CLAIM-OTHER"
    errors = validator.semantic_errors(record)
    assert any("competence.assessedForClaimId" in error for error in errors)


def test_authority_mandate_claim_mismatch_is_flagged() -> None:
    record = _example()
    record["authority"]["mandate"]["claimId"] = "CLAIM-OTHER"
    errors = validator.semantic_errors(record)
    assert any("authority.mandate.claimId" in error for error in errors)


def test_undeclared_trace_evidence_is_flagged() -> None:
    record = _example()
    record["decisionTrace"]["slots"]["claim"]["evidenceIds"].append("EV-99")
    errors = validator.semantic_errors(record)
    assert any("undeclared evidenceId 'EV-99'" in error for error in errors)


def test_dangling_rationale_trace_slot_ref_is_flagged() -> None:
    record = _example()
    record["rationale"]["structure"][0]["traceSlotRef"] = "DT-INF-0417-MISSING"
    errors = validator.semantic_errors(record)
    assert any(
        "does not match any decisionTrace slotId" in error for error in errors
    )


def test_dangling_use_receipt_retrieval_ref_is_flagged() -> None:
    record = _example()
    record["receipts"]["use"][0]["retrievalReceiptId"] = "RCPT-RET-9999"
    errors = validator.semantic_errors(record)
    assert any(
        "does not match any receipts.retrieval receiptId" in error
        for error in errors
    )


def test_revoked_state_requires_non_null_reason_and_authority() -> None:
    record = _example()
    record["lifecycle"]["state"] = "revoked"
    record["lifecycle"]["revocation"] = {
        "revoked": True,
        "revokedAt": "2026-05-22T08:41:00+03:00",
        "revokedByAuthorityRef": None,
        "reason": None,
        "reasonCode": "other",
        "effect": "must_not_influence_any_later_decision",
        "propagationRequired": True,
    }
    errors = validator.semantic_errors(record)
    assert any("lifecycle.revocation.reason" in error for error in errors)
    assert any(
        "lifecycle.revocation.revokedByAuthorityRef" in error for error in errors
    )


def test_non_revoked_state_does_not_require_revocation() -> None:
    record = _example()
    assert record["lifecycle"]["state"] != "revoked"
    assert validator.semantic_errors(record) == []


def test_absent_optional_sections_are_tolerated() -> None:
    record = _example()
    for section in (
        "competence",
        "authority",
        "decisionTrace",
        "rationale",
        "receipts",
        "lifecycle",
    ):
        trimmed = copy.deepcopy(record)
        del trimmed[section]
        assert validator.semantic_errors(trimmed) == [], section


def test_rationale_refs_not_checked_without_decision_trace() -> None:
    record = _example()
    del record["decisionTrace"]
    record["rationale"]["structure"][0]["traceSlotRef"] = "DT-INF-0417-MISSING"
    assert validator.semantic_errors(record) == []
