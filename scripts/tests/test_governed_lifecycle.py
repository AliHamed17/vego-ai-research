"""Tests for the GovernedJudgmentRecord-v1 lifecycle engine and record loader.

Mechanism/design tests only: fixtures use fixed timestamps and no test asserts
any empirical outcome (EXP-005 0/24).
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

from vego_governed import lifecycle, records  # noqa: E402

EXAMPLE = REPO / "schemas" / "examples" / "governed-judgment-record.valid.json"
FIXED_AT = "2026-05-18T09:12:00+03:00"
ACTOR = "person:test-actor-01"


def pending_dissent(status: str = "pending") -> dict:
    return {
        "dissentId": "GJD-TEST-01",
        "dissentingRecordId": "GJR-TEST-DISSENT-01",
        "qualified": True,
        "dissentingCompetenceRef": "COMP-TEST-01",
        "dissentingAuthorityRef": "AUTH-TEST-01",
        "conflictOn": "verdict",
        "registeredAt": FIXED_AT,
        "registeredByRef": "person:test-dissenter-01",
        "retentionPolicy": "retained_not_averaged",
        "withdrawn": False,
        "blocksReuse": True,
        "adjudication": {"status": status},
    }


def adjudicated_dissent() -> dict:
    entry = pending_dissent(status="adjudicated")
    entry["adjudication"].update(
        {
            "outcome": "this_record_upheld",
            "adjudicatedAt": FIXED_AT,
            "adjudicatorAuthorityRef": "AUTH-TEST-PANEL-01",
            "dissentPreservedAfterAdjudication": True,
        }
    )
    return entry


def guard_kwargs(to_state: str) -> dict:
    if to_state == "superseded":
        return {"superseded_by_record_id": "GJR-TEST-SUCCESSOR-01"}
    if to_state == "expired":
        return {"fired_condition_id": "EXP-COND-01"}
    if to_state == "revoked":
        return {
            "revocation_reason": "Recorded reason for the test fixture.",
            "revoked_by_authority_ref": "AUTH-TEST-01",
        }
    return {}


def minimal_label_only_record() -> dict:
    return {
        "schemaVersion": "GovernedJudgmentRecord-v1",
        "recordId": "GJR-TEST-LABEL-ONLY-01",
        "contractStatus": "Draft — not approved",
        "conformanceProfile": "label_only",
        "ablation": {
            "mode": "none",
            "withheldComponents": [],
            "strikeMethod": "delete_top_level_property",
        },
        "createdAt": FIXED_AT,
        "caseGrounding": {
            "caseId": "CASE-TEST-01",
            "claimId": "CLAIM-TEST-01",
            "fragmentRef": {"locator": "element:test-01", "locatorType": "element_id"},
            "artifactRef": {"id": "ART-TEST-01", "version": "1.0", "sha256": None},
            "guidelineRef": {"id": "GUIDE-TEST-01", "version": "1.0", "sha256": None},
            "contextFacets": {
                "contextDimensionSchemaId": "CTXDIM-TEST",
                "contextDimensionSchemaVersion": "1.0",
                "values": {"institution": "INST-TEST"},
            },
            "observedDeviation": "Test fixture deviation statement.",
            "evidence": [
                {
                    "evidenceId": "EV-01",
                    "evidenceType": "guideline_text",
                    "locator": "GUIDE-TEST-01#G-1",
                    "locatorType": "uri",
                    "contentSha256": "0" * 64,
                    "presentedToReviewer": True,
                    "privacyClass": "internal",
                    "retrievability": "referenced_stable",
                }
            ],
            "groundingIntegrity": "reconstructable",
        },
        "verdict": {
            "vocabularyId": "VOCAB-TEST",
            "vocabularyVersion": "1.0",
            "vocabularySha256": "0" * 64,
            "value": "acceptable_as_submitted",
            "dispositionClass": "no_finding",
        },
        "claimBoundary": (
            "Test fixture; design artifact only, no empirical outcome asserted."
        ),
    }


def test_every_legal_transition_accepted() -> None:
    for transition_id, (from_state, to_state) in lifecycle.TRANSITION_TABLE.items():
        engine = lifecycle.LifecycleEngine(state=from_state)
        record = engine.attempt(
            to_state,
            actor_ref=ACTOR,
            attempted_at=FIXED_AT,
            **guard_kwargs(to_state),
        )
        assert record["accepted"] is True
        assert record["transitionId"] == transition_id
        assert record["rejectionCode"] is None
        assert engine.state == to_state


def test_transition_table_export_enumerates_all_twenty() -> None:
    rows = lifecycle.export_transition_table()
    assert len(rows) == 20
    assert {row["transitionId"] for row in rows} == set(lifecycle.TRANSITION_TABLE)
    for row in rows:
        assert lifecycle.LEGAL_TRANSITIONS[(row["from"], row["to"])] == (
            row["transitionId"]
        )
    assert "TXX" not in lifecycle.TRANSITION_TABLE


@pytest.mark.parametrize(
    ("from_state", "to_state"),
    [
        ("draft", "contested"),
        ("draft", "superseded"),
        ("draft", "expired"),
        ("active", "draft"),
        ("retained_dissent", "draft"),
        ("superseded", "active"),
        ("expired", "contested"),
        ("revoked", "active"),
        ("active", "active"),
    ],
)
def test_illegal_pair_rejected_with_named_code(from_state: str, to_state: str) -> None:
    engine = lifecycle.LifecycleEngine(state=from_state)
    with pytest.raises(lifecycle.TransitionRejected) as excinfo:
        engine.attempt(
            to_state,
            actor_ref=ACTOR,
            attempted_at=FIXED_AT,
            **guard_kwargs(to_state),
        )
    assert excinfo.value.code == "GJR-E-002"
    assert engine.state == from_state
    recorded = engine.transitions[-1]
    assert recorded["accepted"] is False
    assert recorded["transitionId"] == "TXX"
    assert recorded["rejectionCode"] == "GJR-E-002"


def test_retained_dissent_to_active_blocked_pending_adjudication() -> None:
    engine = lifecycle.LifecycleEngine(
        state="retained_dissent", retained_dissent=[pending_dissent()]
    )
    with pytest.raises(lifecycle.TransitionRejected) as excinfo:
        engine.attempt("active", actor_ref=ACTOR, attempted_at=FIXED_AT)
    assert excinfo.value.code == "GJR-E-014"
    assert excinfo.value.guard_id == "G-ADJ-AUTHORITY"
    assert engine.state == "retained_dissent"
    recorded = engine.transitions[-1]
    assert recorded["transitionId"] == "T13"
    assert recorded["rejectionCode"] == "GJR-E-014"
    assert recorded["guardEvaluations"][0]["guardId"] == "G-ADJ-AUTHORITY"
    assert recorded["guardEvaluations"][0]["result"] == "fail"


@pytest.mark.parametrize(
    "status", sorted(lifecycle.UNADJUDICATED_STATUSES)
)
def test_every_unadjudicated_status_blocks_return_to_active(status: str) -> None:
    engine = lifecycle.LifecycleEngine(
        state="retained_dissent", retained_dissent=[pending_dissent(status=status)]
    )
    with pytest.raises(lifecycle.TransitionRejected) as excinfo:
        engine.attempt("active", actor_ref=ACTOR, attempted_at=FIXED_AT)
    assert excinfo.value.code == "GJR-E-014"


def test_retained_dissent_to_active_allowed_after_adjudication() -> None:
    engine = lifecycle.LifecycleEngine(
        state="retained_dissent", retained_dissent=[adjudicated_dissent()]
    )
    record = engine.attempt("active", actor_ref=ACTOR, attempted_at=FIXED_AT)
    assert record["accepted"] is True
    assert record["transitionId"] == "T13"
    assert {"guardId": "G-ADJ-AUTHORITY", "result": "pass"} in record[
        "guardEvaluations"
    ]
    assert engine.state == "active"


def test_revocation_without_reason_rejected() -> None:
    engine = lifecycle.LifecycleEngine(state="active")
    with pytest.raises(lifecycle.TransitionRejected) as excinfo:
        engine.attempt(
            "revoked",
            actor_ref=ACTOR,
            attempted_at=FIXED_AT,
            revoked_by_authority_ref="AUTH-TEST-01",
        )
    assert excinfo.value.code == "GJR-E-017"
    assert excinfo.value.guard_id == "G-REVOKE-REASON"
    assert engine.state == "active"
    with pytest.raises(lifecycle.TransitionRejected) as blank:
        engine.attempt(
            "revoked",
            actor_ref=ACTOR,
            attempted_at=FIXED_AT,
            revocation_reason="   ",
            revoked_by_authority_ref="AUTH-TEST-01",
        )
    assert blank.value.code == "GJR-E-017"


def test_revocation_without_authority_rejected() -> None:
    engine = lifecycle.LifecycleEngine(state="active")
    with pytest.raises(lifecycle.TransitionRejected) as excinfo:
        engine.attempt(
            "revoked",
            actor_ref=ACTOR,
            attempted_at=FIXED_AT,
            revocation_reason="Recorded reason for the test fixture.",
        )
    assert excinfo.value.code == "GJR-E-018"
    assert engine.state == "active"


def test_supersession_and_expiry_guards() -> None:
    engine = lifecycle.LifecycleEngine(state="active")
    with pytest.raises(lifecycle.TransitionRejected) as successor:
        engine.attempt("superseded", actor_ref=ACTOR, attempted_at=FIXED_AT)
    assert successor.value.code == "GJR-E-015"
    with pytest.raises(lifecycle.TransitionRejected) as expiry:
        engine.attempt("expired", actor_ref=ACTOR, attempted_at=FIXED_AT)
    assert expiry.value.code == "GJR-E-016"
    assert engine.state == "active"


def test_reuse_gate_blocked_by_pending_qualified_dissent() -> None:
    gate = lifecycle.reuse_gate("active", [pending_dissent()])
    assert gate["decision"] == "blocked"
    assert gate["blockingReasons"] == ["retained_dissent_pending_adjudication"]
    assert gate["derivedFrom"] == "lifecycle.state"


def test_reuse_gate_unblocked_once_dissent_adjudicated() -> None:
    gate = lifecycle.reuse_gate("active", [adjudicated_dissent()])
    assert gate["decision"] == "permitted"
    assert gate["blockingReasons"] == []


def test_reuse_gate_state_reasons_match_schema_enum() -> None:
    expected = {
        "draft": "not_yet_published",
        "contested": "challenge_open",
        "retained_dissent": "retained_dissent_pending_adjudication",
        "superseded": "superseded",
        "expired": "expired",
        "revoked": "revoked",
    }
    for state, reason in expected.items():
        gate = lifecycle.reuse_gate(state)
        assert gate["decision"] == "blocked"
        assert gate["blockingReasons"] == [reason]
    assert lifecycle.reuse_gate("active")["decision"] == "permitted"


def test_reuse_gate_rejects_unknown_state() -> None:
    with pytest.raises(ValueError):
        lifecycle.reuse_gate("published")


def test_valid_example_loads_clean_and_reports_reuse_blocked() -> None:
    record = records.load_record(EXAMPLE)
    assert record.record_id == "GJR-SE310-2026S-A2-0417-ACTOR-R2"
    assert record.lifecycle_state == "retained_dissent"
    gate = lifecycle.reuse_gate(record.lifecycle_state, record.retained_dissent)
    assert gate["decision"] == "blocked"
    assert "retained_dissent_pending_adjudication" in gate["blockingReasons"]
    assert gate == dict(record.recorded_reuse_gate)
    engine = lifecycle.LifecycleEngine.from_record(record)
    assert engine.reuse_gate()["decision"] == "blocked"


def test_valid_example_typed_accessors() -> None:
    record = records.load_record(EXAMPLE)
    dissent = record.retained_dissent
    assert len(dissent) == 1
    assert dissent[0].qualified is True
    assert dissent[0].blocks_reuse is True
    assert dissent[0].adjudication_status == "pending"
    assert record.scope is not None
    assert record.scope.ladder_level == "pattern_specific"
    assert record.scope.decidable is True
    assert len(record.scope.exclusions) == 6
    assert record.competence is not None
    assert record.competence.claim_specific is True
    assert record.competence.distinct_from_authority is True
    assert record.authority is not None
    assert record.authority.claim_scoped is True
    assert record.authority.distinct_from_competence is True
    assert record.receipts is not None
    assert record.receipts.append_only is True
    assert len(record.receipts.retrieval) == 3
    assert len(record.receipts.use) == 2
    assert len(record.receipts.outcome) == 2
    recorded = record.recorded_transitions
    assert [item["transitionId"] for item in recorded] == ["T01", "T04", "T13", "TXX"]
    assert [item["rejectionCode"] for item in recorded] == [
        None,
        None,
        "GJR-E-014",
        "GJR-E-002",
    ]


def test_minimal_label_only_dict_loads_and_omits_optional_groups() -> None:
    record = records.load_record(minimal_label_only_record())
    assert record.conformance_profile == "label_only"
    assert record.lifecycle_state is None
    assert record.retained_dissent == ()
    assert record.scope is None
    assert record.competence is None
    assert record.authority is None
    assert record.receipts is None


def test_invalid_record_raises_single_error_type_with_messages() -> None:
    broken = minimal_label_only_record()
    del broken["verdict"]
    broken["recordId"] = "not-a-gjr-id"
    with pytest.raises(records.ValidationError) as excinfo:
        records.load_record(broken)
    assert isinstance(excinfo.value.messages, list)
    assert len(excinfo.value.messages) >= 2
    assert any("verdict" in message for message in excinfo.value.messages)
    assert any("recordId" in message for message in excinfo.value.messages)


def test_rejected_attempts_are_recorded_not_lost() -> None:
    engine = lifecycle.LifecycleEngine(
        state="retained_dissent", retained_dissent=[pending_dissent()]
    )
    with pytest.raises(lifecycle.TransitionRejected):
        engine.attempt("active", actor_ref=ACTOR, attempted_at=FIXED_AT)
    with pytest.raises(lifecycle.TransitionRejected):
        engine.attempt("draft", actor_ref=ACTOR, attempted_at=FIXED_AT)
    accepted = engine.attempt(
        "superseded",
        actor_ref=ACTOR,
        attempted_at=FIXED_AT,
        **guard_kwargs("superseded"),
    )
    assert [item["attemptId"] for item in engine.transitions] == [
        "TR-0001",
        "TR-0002",
        "TR-0003",
    ]
    assert [item["accepted"] for item in engine.transitions] == [False, False, True]
    assert accepted["transitionId"] == "T14"
    assert engine.state == "superseded"
