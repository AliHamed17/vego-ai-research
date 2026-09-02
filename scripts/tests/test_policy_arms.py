"""Tests for the selective-intervention policy engine v2 (src/vego_governed/policy.py).

Mechanism tests only: they verify determinism, budget accounting, arm
configuration, and contract-shape fidelity of the synthetic replay fixtures.
No test asserts or implies any empirical outcome (EXP-005 labels remain 0/24;
the fixtures carry no ground-truth labels).
"""

from __future__ import annotations

import copy
import json
import re
import sys
from pathlib import Path

import jsonschema
import pytest

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from vego_governed.policy import (  # noqa: E402
    ARM_IDS,
    SIGNAL_IDS,
    Arm,
    BudgetLedger,
    PolicyValidationError,
    replay,
    replay_all,
    select_reviewer,
)

FIXTURES_PATH = ROOT / "schemas" / "examples" / "policy-replay-fixtures.json"
SCHEMA_PATH = ROOT / "schemas" / "review-policy-signal-contract-v1.schema.json"

ALL_EVENT_IDS = tuple(f"EVT-FIX-{n:03d}" for n in range(1, 15))
FORBIDDEN_LABEL_KEYS = {
    "importantCaseLabel",
    "importantCaseLabelSource",
    "unreviewedOutcome",
    "selectiveRiskAccounting",
    "groundTruthLabel",
}


@pytest.fixture(scope="module")
def events() -> list[dict]:
    return json.loads(FIXTURES_PATH.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def contract_defs() -> dict:
    return json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))["$defs"]


def _def_validator(contract_defs: dict, def_name: str) -> jsonschema.Draft202012Validator:
    return jsonschema.Draft202012Validator(
        {"$ref": f"#/$defs/{def_name}", "$defs": contract_defs}
    )


def _constructed_candidate(candidate_id: str, competence: float, authority: str) -> dict:
    return {
        "candidateId": candidate_id,
        "reviewerId": f"reviewer-{candidate_id.lower()}",
        "available": True,
        "assessedCompetence": {
            "assessmentScope": "contested_fragment",
            "fragmentId": "FRG-CONSTRUCTED",
            "value": competence,
        },
        "assertedAuthority": {
            "status": "active",
            "fragmentId": "FRG-CONSTRUCTED",
            "value": authority,
        },
    }


def test_fixture_events_mirror_contract_signal_shapes(events, contract_defs) -> None:
    assert 12 <= len(events) <= 20
    assert tuple(event["eventId"] for event in events) == ALL_EVENT_IDS
    observation_validator = _def_validator(contract_defs, "signalObservation")
    candidate_validator = _def_validator(contract_defs, "reviewerCandidate")
    for event in events:
        assert re.fullmatch(r"EVT-FIX-\d{3}", event["eventId"])
        assert event["syntheticFixture"] is True
        assert not FORBIDDEN_LABEL_KEYS & set(event)
        observations = event["signalObservations"]
        assert tuple(obs["signalId"] for obs in observations) == SIGNAL_IDS
        for observation in observations:
            observation_validator.validate(observation)
        assert event["reviewerCandidates"]
        for candidate in event["reviewerCandidates"]:
            candidate_validator.validate(candidate)


def test_replay_decisions_are_byte_identical_across_replays(events) -> None:
    first = replay_all(events, 6, seed=7)
    second = replay_all(events, 6, seed=7)
    assert set(first) == set(ARM_IDS)
    for arm_id in ARM_IDS:
        assert first[arm_id].to_json().encode("utf-8") == second[arm_id].to_json().encode(
            "utf-8"
        )


def test_never_ask_escalates_zero_events(events) -> None:
    ledger = replay(Arm("never_ask"), events, 3)
    assert ledger.escalated_event_ids == ()
    assert ledger.deferred_event_ids == ()
    assert ledger.declined_event_ids == ALL_EVENT_IDS
    assert ledger.budget.consumed == 0
    assert all(not decision.escalate for decision in ledger.decisions)


def test_always_ask_escalates_all_until_budget_then_defers(events) -> None:
    ample = replay(Arm("always_ask"), events, len(events))
    assert ample.escalated_event_ids == ALL_EVENT_IDS
    assert ample.budget.remaining == 0

    capped = replay(Arm("always_ask"), events, 5)
    assert capped.escalated_event_ids == ALL_EVENT_IDS[:5]
    assert capped.deferred_event_ids == ALL_EVENT_IDS[5:]
    assert capped.declined_event_ids == ()
    assert capped.decisions[4].budget_state == "capped"
    for decision in capped.decisions[5:]:
        assert decision.escalate is False
        assert decision.budget_state == "deferred"
        assert decision.reason.startswith("deferred_due_to_budget_exhaustion:")
    total = (
        len(capped.escalated_event_ids)
        + len(capped.deferred_event_ids)
        + len(capped.declined_event_ids)
    )
    assert total == len(events)


def test_random_at_budget_is_deterministic_per_seed(events) -> None:
    same_seed_a = replay(Arm("random_at_budget", {"seed": 7}), events, 100)
    same_seed_b = replay(Arm("random_at_budget", {"seed": 7}), events, 100)
    assert same_seed_a.to_json() == same_seed_b.to_json()

    other_seed = replay(Arm("random_at_budget", {"seed": 11}), events, 100)
    flags_seed_7 = [decision.escalate for decision in same_seed_a.decisions]
    flags_seed_11 = [decision.escalate for decision in other_seed.decisions]
    assert flags_seed_7 != flags_seed_11

    with pytest.raises(PolicyValidationError):
        Arm("random_at_budget")
    with pytest.raises(PolicyValidationError):
        Arm("not_a_comparator_arm")


def test_uncertainty_only_matches_hand_computed_expectation(events) -> None:
    ledger = replay(Arm("uncertainty_only"), events[:5], 10)
    expected = [
        ("EVT-FIX-001", True, "low_confidence"),
        ("EVT-FIX-002", True, "medium_confidence"),
        ("EVT-FIX-003", False, "no_trigger_fired"),
        ("EVT-FIX-004", True, "agent_requested_human_review"),
        ("EVT-FIX-005", True, "undetermined_classification"),
    ]
    observed = [(d.event_id, d.escalate, d.reason) for d in ledger.decisions]
    assert observed == expected

    without_medium = replay(
        Arm("uncertainty_only", {"include_medium": False}), events[:5], 10
    )
    assert [d.escalate for d in without_medium.decisions] == [True, False, False, True, True]

    guideline = replay(Arm("uncertainty_only"), events, 100)
    by_id = {d.event_id: d for d in guideline.decisions}
    assert by_id["EVT-FIX-006"].reason == "guideline_update_proposed"
    assert by_id["EVT-FIX-011"].reason == "guideline_update_proposed"


def test_explicit_review_request_coexists_with_numeric_confidence_for_every_arm() -> None:
    """Catches an observed review request masking a separately derived confidence value."""
    event = {
        "eventId": "EVT-COOCCURRING-001",
        "fragmentId": "EVT-COOCCURRING-001",
        "reviewerCandidates": [],
        "explicitEscalationRequests": [
            {
                "signalId": "claim_uncertainty",
                "trigger": "agent_requested_human_review",
                "evidenceState": "observed",
            }
        ],
        "signalObservations": [
            {
                "signalId": "claim_uncertainty",
                "normalizedValue": 0.8,
                "missing": False,
            }
        ],
    }

    ledgers = replay_all([event], budget=1, seed=7)

    uncertainty = ledgers["uncertainty_only"].decisions[0]
    assert uncertainty.escalate is True
    assert uncertainty.reason == "agent_requested_human_review+low_confidence"
    threshold = ledgers["fixed_threshold"].decisions[0]
    assert threshold.escalate is True
    assert threshold.reason == "mean_signal_score=0.8000>=fixed_threshold=0.6000"
    proposed = ledgers["proposed_joint_policy"].decisions[0]
    assert proposed.escalate is True
    assert proposed.reason.startswith("explicit_review_request:claim_uncertainty")


@pytest.mark.parametrize(
    "requests",
    [
        "agent_requested_human_review",
        [{"signalId": "claim_uncertainty", "trigger": "unexpected", "evidenceState": "observed"}],
        [
            {
                "signalId": "claim_uncertainty",
                "trigger": "agent_requested_human_review",
                "evidenceState": "derived",
            }
        ],
    ],
)
def test_explicit_review_request_contract_fails_closed(requests: object) -> None:
    """Catches unbounded or non-observed request facts entering policy replay."""
    event = {
        "eventId": "EVT-REQUEST-VALIDATION-001",
        "explicitEscalationRequests": requests,
        "signalObservations": [],
    }

    with pytest.raises(PolicyValidationError, match="explicit escalation request"):
        replay_all([event], budget=1, seed=7)


@pytest.mark.parametrize(
    "invalid_value",
    [float("nan"), float("inf"), float("-inf"), True, False, -0.01, 1.01, "0.8"],
)
def test_direct_replay_rejects_invalid_normalized_observation_values(
    invalid_value: object,
) -> None:
    """Catches direct callers bypassing finite unit-interval observation validation."""
    event = {
        "eventId": "EVT-INVALID-NUMERIC-001",
        "signalObservations": [
            {
                "signalId": "claim_uncertainty",
                "normalizedValue": invalid_value,
                "missing": False,
            }
        ],
    }

    with pytest.raises(PolicyValidationError, match="normalizedValue"):
        replay_all([event], budget=1, seed=7)


def test_direct_replay_rejects_non_finite_raw_observation_value() -> None:
    """Catches non-finite full-contract observation values hidden from policy arithmetic."""
    event = {
        "eventId": "EVT-INVALID-RAW-NUMERIC-001",
        "signalObservations": [
            {
                "signalId": "claim_uncertainty",
                "value": float("nan"),
                "normalizedValue": 0.8,
                "missing": False,
            }
        ],
    }

    with pytest.raises(PolicyValidationError, match="observation value"):
        replay_all([event], budget=1, seed=7)


@pytest.mark.parametrize("invalid_value", [True, "0.8"])
def test_direct_replay_rejects_non_numeric_values_for_numeric_observation_types(
    invalid_value: object,
) -> None:
    """Catches Python booleans or strings masquerading as raw probability values."""
    event = {
        "eventId": "EVT-INVALID-RAW-TYPE-001",
        "signalObservations": [
            {
                "signalId": "claim_uncertainty",
                "valueType": "probability",
                "value": invalid_value,
                "normalizedValue": 0.8,
                "missing": False,
            }
        ],
    }

    with pytest.raises(PolicyValidationError, match="observation value"):
        replay_all([event], budget=1, seed=7)


def test_direct_replay_rejects_missing_observation_with_numeric_value() -> None:
    """Catches replay silently discarding a contradictory numeric observation."""
    event = {
        "eventId": "EVT-CONTRADICTORY-001",
        "signalObservations": [
            {
                "signalId": "claim_uncertainty",
                "normalizedValue": 0.8,
                "missing": True,
                "missingValuePolicy": "force_undetermined",
            }
        ],
    }

    with pytest.raises(PolicyValidationError, match="missing.*normalizedValue"):
        replay_all([event], budget=1, seed=7)


@pytest.mark.parametrize(
    ("arm_id", "params"),
    [
        ("random_at_budget", {"seed": 7, "selection_probability": True}),
        ("uncertainty_only", {"low_confidence_floor": float("nan")}),
        ("uncertainty_only", {"medium_confidence_floor": -0.01}),
        ("uncertainty_only", {"guideline_novelty_floor": 1.01}),
        ("fixed_threshold", {"threshold": float("inf")}),
        ("proposed_joint_policy", {"escalation_threshold": True}),
        ("proposed_joint_policy", {"competence_floor": -0.01}),
        (
            "proposed_joint_policy",
            {
                "weights": [
                    {
                        "signalId": "claim_uncertainty",
                        "weight": False,
                        "weightVersion": "test-v1",
                    }
                ]
            },
        ),
        (
            "proposed_joint_policy",
            {
                "weights": [
                    {
                        "signalId": "claim_uncertainty",
                        "weight": float("nan"),
                        "weightVersion": "test-v1",
                    }
                ]
            },
        ),
    ],
)
def test_arm_rejects_invalid_numeric_parameters(arm_id: str, params: dict) -> None:
    """Catches bool, non-finite, or out-of-range arm parameters reaching replay."""
    with pytest.raises(PolicyValidationError, match="numeric parameter|weight"):
        Arm(arm_id, params)


def test_policy_validation_errors_do_not_echo_caller_event_ids_or_parameter_keys() -> None:
    """Catches private caller-controlled identifiers being reflected in failures."""
    private_event_id = "C:" + "/" + "sensitive/control" + "led/event"
    duplicate = {"eventId": private_event_id, "signalObservations": []}

    with pytest.raises(PolicyValidationError) as event_error:
        replay_all([duplicate, duplicate], budget=1, seed=7)

    private_parameter = "C:" + "/" + "sensitive/control" + "led/parameter"
    with pytest.raises(PolicyValidationError) as parameter_error:
        Arm("fixed_threshold", {private_parameter: 0.5})

    assert private_event_id not in str(event_error.value)
    assert private_parameter not in str(parameter_error.value)


@pytest.mark.parametrize(
    ("budget", "seed"),
    [
        (True, 7),
        (float("nan"), 7),
        (float("inf"), 7),
        (1, True),
        (1, float("nan")),
    ],
)
def test_replay_all_rejects_invalid_direct_numeric_inputs(budget: object, seed: object) -> None:
    """Catches direct matched-replay inputs bypassing ledger or random-arm validation."""
    with pytest.raises(PolicyValidationError):
        replay_all([], budget=budget, seed=seed)


def test_budget_exhaustion_produces_deferred_not_dropped(events) -> None:
    ledger = replay(Arm("uncertainty_only"), events, 4)
    assert ledger.escalated_event_ids == (
        "EVT-FIX-001",
        "EVT-FIX-002",
        "EVT-FIX-004",
        "EVT-FIX-005",
    )
    assert ledger.deferred_event_ids == (
        "EVT-FIX-006",
        "EVT-FIX-007",
        "EVT-FIX-008",
        "EVT-FIX-010",
        "EVT-FIX-011",
        "EVT-FIX-012",
        "EVT-FIX-014",
    )
    assert ledger.declined_event_ids == ("EVT-FIX-003", "EVT-FIX-009", "EVT-FIX-013")
    partition = (
        ledger.escalated_event_ids + ledger.deferred_event_ids + ledger.declined_event_ids
    )
    assert sorted(partition) == sorted(ALL_EVENT_IDS)
    assert ledger.not_escalated_event_ids == (
        "EVT-FIX-003",
        "EVT-FIX-006",
        "EVT-FIX-007",
        "EVT-FIX-008",
        "EVT-FIX-009",
        "EVT-FIX-010",
        "EVT-FIX-011",
        "EVT-FIX-012",
        "EVT-FIX-013",
        "EVT-FIX-014",
    )
    assert ledger.decisions[4].budget_state == "capped"
    assert ledger.budget.remaining == 0
    deferred_states = [d for d in ledger.decisions if d.budget_state == "deferred"]
    assert len(deferred_states) == len(ledger.deferred_event_ids)


def test_all_six_arms_consume_identical_event_inputs(events) -> None:
    snapshot = copy.deepcopy(events)
    ledgers = replay_all(events, 6, seed=7)
    assert set(ledgers) == set(ARM_IDS)
    for arm_id in ARM_IDS:
        decided_ids = tuple(d.event_id for d in ledgers[arm_id].decisions)
        assert decided_ids == ALL_EVENT_IDS
        assert ledgers[arm_id].budget.amount == 6
    assert events == snapshot


def test_proposed_policy_reviewer_selection_prefers_authority(events) -> None:
    high_competence_advisory = _constructed_candidate("RC-HIGH-COMP-ADVISORY", 0.95, "advisory")
    authorized_lower_competence = _constructed_candidate("RC-AUTHORIZED", 0.50, "decides")
    below_floor_top_authority = _constructed_candidate(
        "RC-BELOW-FLOOR", 0.20, "decides_and_may_amend_guideline"
    )
    candidates = [
        high_competence_advisory,
        authorized_lower_competence,
        below_floor_top_authority,
    ]
    selected = select_reviewer(candidates, fragment_id="FRG-CONSTRUCTED")
    assert selected == "RC-AUTHORIZED"
    relaxed_floor = select_reviewer(
        candidates, competence_floor=0.1, fragment_id="FRG-CONSTRUCTED"
    )
    assert relaxed_floor == "RC-BELOW-FLOOR"

    proposed = replay(Arm("proposed_joint_policy"), events, 100)
    first = proposed.decisions[0]
    assert first.event_id == "EVT-FIX-001"
    assert first.escalate is True
    assert first.selected_reviewer_id == "RC-FIX-001-B"
    ninth = proposed.decisions[8]
    assert ninth.event_id == "EVT-FIX-009"
    assert ninth.selected_reviewer_id == "RC-FIX-009-B"


def test_evaluation_only_ledger_records_without_charging(events) -> None:
    ledger = replay(Arm("always_ask"), events, BudgetLedger(amount=1, evaluation_only=True))
    assert ledger.escalated_event_ids == ALL_EVENT_IDS
    assert ledger.budget.consumed == 0
    assert all(d.budget_state == "evaluation_only" for d in ledger.decisions)
