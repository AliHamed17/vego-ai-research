"""Tests for the ReuseDecisionRecord-v1 five-gate engine (src/vego_governed/reuse.py).

Fixtures are built in-test from the shipped valid example so gate ids,
outcome enums, ladder dimensions, and receipt field names stay verbatim to
the schema. All timestamps are fixed strings; nothing reads a clock.
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import jsonschema
import pytest

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

from vego_governed import reuse  # noqa: E402

EXAMPLE = json.loads(
    (REPO / "schemas" / "examples" / "reuse-decision-record.valid.json").read_text(
        encoding="utf-8"
    )
)
SCHEMA = json.loads(
    (REPO / "schemas" / "reuse-decision-record-v1.schema.json").read_text(encoding="utf-8")
)
LADDER = EXAMPLE["contextDistanceSchema"]

WHEN = "2026-08-28T09:12:30+03:00"
CLAIM_KEY = "actor-unnamed-supervisory-role-defensible-abstraction"
SECRET_RATIONALE = (
    "RESTRICTED-RATIONALE the shift supervisor actor was ruled a defensible abstraction"
)
ATTRIBUTION = "Instructor of record, SE-101 2025A"
AUTHORIZED_REQUESTER_ID = "staff:inst-a:se101:reviewer-07"

EVIDENCE_REF = {
    "refId": "MODEL-FRAGMENT-S0207-ACTOR-SHIFT-SUPERVISOR",
    "path": "examples/c3-shift-supervisor/model-fragment-S0207-actor-shift-supervisor.json",
    "sha256": "e" * 64,
}


def make_source_judgment(**overrides) -> dict:
    judgment = {
        "judgmentId": EXAMPLE["sourceJudgmentRef"]["judgmentId"],
        "envelope": {
            "visibilityScope": [AUTHORIZED_REQUESTER_ID],
            "lifecycleStateAtUse": "active",
            "lifecycleReadAt": "2026-08-28T09:12:02+03:00",
            "contractId": "GovernedJudgmentRecord-v1",
            "contractVersion": "1.0",
        },
        "payload": {
            "judgmentVersion": "1.0",
            "judgmentSha256": "3" * 64,
            "claimKey": CLAIM_KEY,
            "rationale": SECRET_RATIONALE,
            "attribution": ATTRIBUTION,
            "sourceContext": {
                "descriptorId": EXAMPLE["sourceContext"]["descriptorId"],
                "dimensionValues": dict(EXAMPLE["sourceContext"]["dimensionValues"]),
            },
        },
    }
    judgment.update(overrides)
    return judgment


def make_target_context(**overrides) -> dict:
    context = {
        "descriptorId": EXAMPLE["targetContext"]["descriptorId"],
        "caseRef": EXAMPLE["targetContext"]["caseRef"],
        "dimensionValues": dict(EXAMPLE["targetContext"]["dimensionValues"]),
        "claimKey": CLAIM_KEY,
        "capturedAt": "2026-08-28T08:05:00+03:00",
        "currentCaseEvidenceRefs": [dict(EVIDENCE_REF)],
        "adaptation": dict(EXAMPLE["adaptation"]),
    }
    context.update(overrides)
    return context


def make_requester(**overrides) -> dict:
    requester = {"requesterId": AUTHORIZED_REQUESTER_ID, "consumerType": "reviewer_interface"}
    requester.update(overrides)
    return requester


def evaluate(source=None, target=None, requester=None):
    return reuse.evaluate(
        source or make_source_judgment(),
        target or make_target_context(),
        requester or make_requester(),
        LADDER,
        evaluated_at=WHEN,
    )


def canonical_sha256(value) -> str:
    encoded = json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def test_gate_one_failure_short_circuits_and_leaks_no_payload():
    result = evaluate(requester=make_requester(requesterId="staff:inst-b:unrelated-01"))
    gates = result["gateEvaluations"]
    assert gates[0]["gateId"] == "g1_visibility_authorization"
    assert gates[0]["result"] == "fail"
    for gate in gates[1:]:
        assert gate["result"] == "not_evaluated"
        assert gate["evaluatedAt"] is None
        assert gate["evidenceRefs"] == []
    assert result["restrictedEvidenceExposed"] is False
    assert result["decision"]["outcome"] == "reuse_blocked"
    assert result["effect"] == "prior_judgment_withheld"
    assert result["sourceJudgmentRef"] == {
        "judgmentId": EXAMPLE["sourceJudgmentRef"]["judgmentId"]
    }
    assert result["contextDistance"] is None
    serialized = json.dumps(result)
    assert SECRET_RATIONALE not in serialized
    assert ATTRIBUTION not in serialized
    assert CLAIM_KEY not in serialized
    assert EXAMPLE["sourceContext"]["dimensionValues"]["same_case"] not in serialized
    assert "advice" not in result


def test_gate_one_undetermined_when_scope_missing_keeps_payload_sealed():
    source = make_source_judgment()
    source["envelope"] = {"lifecycleStateAtUse": "active", "visibilityScope": None}
    result = evaluate(source=source)
    assert result["gateEvaluations"][0]["result"] == "undetermined"
    assert result["decision"]["outcome"] == "reuse_undetermined"
    assert result["restrictedEvidenceExposed"] is False
    assert SECRET_RATIONALE not in json.dumps(result)


def test_sealed_source_refuses_unseal_without_passing_gate_one():
    sealed = reuse.SealedSourceJudgment(make_source_judgment())
    with pytest.raises(reuse.SealedSourceError):
        sealed.payload()
    with pytest.raises(reuse.SealedSourceError):
        sealed.unseal({"gateId": "g1_visibility_authorization", "result": "fail"})


def test_gate_order_matches_schema_prefix_items():
    result = evaluate()
    assert [gate["gateId"] for gate in result["gateEvaluations"]] == list(reuse.GATE_IDS)
    assert [gate["gateOrder"] for gate in result["gateEvaluations"]] == [1, 2, 3, 4, 5]


def test_eligible_outcome_when_no_dimension_differs():
    target = make_target_context(
        dimensionValues=dict(EXAMPLE["sourceContext"]["dimensionValues"])
    )
    target.pop("adaptation")
    result = evaluate(target=target)
    assert [gate["result"] for gate in result["gateEvaluations"]] == ["pass"] * 5
    assert result["decision"]["outcome"] == "reuse_eligible"
    assert result["decision"]["outcomeLabel"] == "Eligible"
    assert result["effect"] == "prior_judgment_surfaced_as_attributed_advice"
    assert "adaptation" not in result
    advice = result["advice"]
    assert advice["presented_as"] == "attributed_advice"
    assert advice["presented_as_settled_label"] is False
    assert advice["attribution"] == ATTRIBUTION
    assert advice["content"] == SECRET_RATIONALE


def test_eligible_with_adaptation_on_later_cohort_revised_description():
    result = evaluate()
    results = [gate["result"] for gate in result["gateEvaluations"]]
    assert results == ["pass", "pass", "pass_with_adaptation", "pass", "pass"]
    decision = result["decision"]
    assert decision["outcome"] == "reuse_eligible_with_adaptation"
    assert decision["outcomeLabel"] == "Eligible with adaptation"
    assert decision["gateId"] == "g3_context_fit"
    assert decision["ruleId"] == "R-G3-CONTEXT-FIT"
    assert decision["contextDimensionId"] == "cohort"
    assert result["adaptation"]["adaptationId"] == EXAMPLE["adaptation"]["adaptationId"]
    assert result["advice"]["adaptation"]["adaptationId"] == EXAMPLE["adaptation"]["adaptationId"]
    assert result["advice"]["presented_as_settled_label"] is False


def test_blocked_outcome_when_institution_differs_beyond_tolerance():
    values = dict(EXAMPLE["targetContext"]["dimensionValues"])
    values["institution"] = "INST-B/SE-201"
    result = evaluate(target=make_target_context(dimensionValues=values))
    gates = result["gateEvaluations"]
    assert gates[2]["result"] == "fail"
    assert gates[2]["contextDimensionId"] == "institution"
    assert gates[3]["result"] == "not_evaluated"
    assert gates[4]["result"] == "not_evaluated"
    assert sum(1 for gate in gates if gate["result"] == "fail") == 1
    assert result["decision"]["outcome"] == "reuse_blocked"
    assert result["effect"] == "prior_judgment_withheld"
    assert "advice" not in result
    assert "adaptation" not in result


def test_undetermined_on_conflicting_evidence_routes_to_review():
    result = evaluate(target=make_target_context(currentCaseEvidenceConflicting=True))
    gates = result["gateEvaluations"]
    assert gates[3]["result"] == "undetermined"
    assert gates[4]["result"] == "not_evaluated"
    assert result["decision"]["outcome"] == "reuse_undetermined"
    assert result["decision"]["outcomeLabel"] == "Undetermined"
    assert result["effect"] == "no_effect_pending_review"
    assert result["routed_to_independent_review"] is True
    review = result["independentReview"]
    assert review["routed"] is True
    assert review["cause"] == "conflicting_evidence"
    assert review["treatedAsSafeReuse"] is False
    assert review["treatedAsPermanentProhibition"] is False
    assert "advice" not in result


def test_undetermined_on_missing_evidence_never_eligible_never_blocked():
    result = evaluate(target=make_target_context(currentCaseEvidenceRefs=[]))
    assert result["decision"]["outcome"] == "reuse_undetermined"
    assert result["independentReview"]["cause"] == "missing_evidence"

    source = make_source_judgment()
    source["envelope"]["lifecycleStateAtUse"] = "unknown"
    result = evaluate(source=source)
    assert result["decision"]["outcome"] == "reuse_undetermined"
    assert result["independentReview"]["cause"] == "unknown_lifecycle_state"


def test_every_decision_names_rule_and_dimension():
    scenarios = [
        evaluate(),
        evaluate(requester=make_requester(requesterId="staff:inst-b:unrelated-01")),
        evaluate(target=make_target_context(currentCaseEvidenceConflicting=True)),
        evaluate(
            target={
                **make_target_context(
                    dimensionValues=dict(EXAMPLE["sourceContext"]["dimensionValues"])
                ),
                "adaptation": None,
            }
        ),
    ]
    for result in scenarios:
        decision = result["decision"]
        assert decision["ruleId"] in reuse.GATE_RULE_IDS.values()
        assert decision["contextDimensionId"] in dict(reuse.LADDER_DIMENSIONS)
        assert decision["ruleId"] in decision["statement"]
        assert decision["contextDimensionId"] in decision["statement"]


def test_receipt_always_emitted_and_mirrors_decision():
    receipt_validator = jsonschema.Draft202012Validator(
        {"$ref": "#/$defs/outcomeReceipt", "$defs": SCHEMA["$defs"]}
    )
    scenarios = [
        evaluate(),
        evaluate(requester=make_requester(requesterId="staff:inst-b:unrelated-01")),
        evaluate(target=make_target_context(currentCaseEvidenceConflicting=True)),
    ]
    for result in scenarios:
        receipt = result["outcomeReceipt"]
        receipt_validator.validate(receipt)
        assert receipt["receiptId"].startswith("RDR-RCPT-")
        assert receipt["issuanceTrigger"] == "every_reuse_decision_evaluation"
        assert receipt["recordedOutcome"] == result["decision"]["outcome"]
        assert receipt["recordedDimensionId"] == result["decision"]["contextDimensionId"]
        without_receipt = {k: v for k, v in result.items() if k != "outcomeReceipt"}
        assert receipt["decisionRecordSha256"] == canonical_sha256(without_receipt)
        without_digest = {k: v for k, v in receipt.items() if k != "receiptSha256"}
        assert receipt["receiptSha256"] == canonical_sha256(without_digest)


def test_advice_requires_attribution():
    source = make_source_judgment()
    source["payload"] = {**source["payload"], "attribution": ""}
    with pytest.raises(reuse.ReuseEngineError):
        evaluate(source=source)


def test_ladder_ranks_later_cohort_with_revised_description():
    distance = reuse.context_distance(
        EXAMPLE["sourceContext"]["dimensionValues"],
        EXAMPLE["targetContext"]["dimensionValues"],
        LADDER,
    )
    assert distance["comparisons"] == EXAMPLE["contextDistance"]["comparisons"]
    assert distance["maxDifferingDimensionId"] == "cohort"
    assert distance["max_differing_rank"] == 2
    assert distance["maxDifferingRank"] == 2
    assert distance["exceeds_cohort"] is False
    assert distance["exceedsCohort"] is False
    assert (
        distance["computedFromSchemaSha256"]
        == EXAMPLE["contextDistance"]["computedFromSchemaSha256"]
    )


def test_ladder_ranks_above_cohort_dimension():
    target_values = dict(EXAMPLE["sourceContext"]["dimensionValues"])
    target_values["modeling_language"] = "BPMN 2.0 collaboration diagram"
    distance = reuse.context_distance(
        EXAMPLE["sourceContext"]["dimensionValues"], target_values, LADDER
    )
    assert distance["maxDifferingDimensionId"] == "modeling_language"
    assert distance["max_differing_rank"] == 3
    assert distance["exceeds_cohort"] is True


def test_capability_gap_refused_for_shipped_unreplicated_candidate():
    candidate = EXAMPLE["capabilityGapAssertion"]
    assert candidate["status"] == "candidate"
    with pytest.raises(reuse.CapabilityGapRefusal):
        reuse.claim_capability_gap(candidate, candidate["replications"], ladder=LADDER)


def make_replication(index: int, dimension: str, rank: int) -> dict:
    return {
        "replicationId": f"REPL-{index:02d}",
        "contextDescriptorId": f"TCD-REPL-{index:02d}",
        "contextSha256": f"{index:x}" * 64,
        "contextFrozenAt": "2026-08-25T09:00:00+03:00",
        "signatureMatched": True,
        "distanceFromSourceDimensionId": dimension,
        "distanceFromSourceRank": rank,
        "observationRef": {
            "refId": f"OBS-{index:02d}",
            "path": f"examples/replication-{index:02d}.json",
            "sha256": "9" * 64,
        },
    }


def make_confirmed_candidate() -> dict:
    candidate = json.loads(json.dumps(EXAMPLE["capabilityGapAssertion"]))
    candidate["distinctFrozenContextsConfirmed"] = True
    candidate["independentConfirmation"] = {
        "confirmed": True,
        "confirmerRole": "external reviewer",
        "confirmerId": "reviewer:external-17",
        "independenceStatement": "Not part of the SE-101 staff of record.",
        "confirmedAt": "2026-08-27T10:00:00+03:00",
        "recordId": "ICR-0001",
    }
    for cause in candidate["alternativeCausesRuledOut"].values():
        cause["status"] = "ruled_out"
        cause["evidenceRef"] = None
    return candidate


def test_capability_gap_accepted_with_two_above_cohort_contexts_and_all_flags():
    candidate = make_confirmed_candidate()
    replications = [
        make_replication(1, "modeling_language", 3),
        make_replication(2, "institution", 4),
    ]
    declared = reuse.claim_capability_gap(candidate, replications, ladder=LADDER)
    assert declared["status"] == "declared_transferable_capability_gap"
    assert len(declared["replications"]) == 2


def test_capability_gap_refused_when_contexts_not_above_cohort():
    candidate = make_confirmed_candidate()
    replications = [
        make_replication(1, "cohort", 2),
        make_replication(2, "institution", 4),
    ]
    with pytest.raises(reuse.CapabilityGapRefusal):
        reuse.claim_capability_gap(candidate, replications, ladder=LADDER)


def test_capability_gap_refused_when_a_cause_is_not_assessed():
    candidate = make_confirmed_candidate()
    candidate["alternativeCausesRuledOut"]["taskDesign"]["status"] = "not_assessed"
    replications = [
        make_replication(1, "modeling_language", 3),
        make_replication(2, "institution", 4),
    ]
    with pytest.raises(reuse.CapabilityGapRefusal):
        reuse.claim_capability_gap(candidate, replications, ladder=LADDER)
