"""Recompute public-safe Study 1 measures and validate denominator integrity."""

from __future__ import annotations

import json
import math
from collections.abc import Mapping
from pathlib import Path
from typing import Any


class MeasurementValidationError(ValueError):
    """Raised when a sanitized Study 1 result violates a measurement invariant."""


def _mapping(value: object, label: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise MeasurementValidationError(f"{label} must be an object")
    return value


def _integer(value: object, label: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise MeasurementValidationError(f"{label} must be a non-negative integer")
    return value


def _number(value: object, label: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise MeasurementValidationError(f"{label} must be numeric")
    return float(value)


def _equal(actual: int, expected: int, label: str) -> None:
    if actual != expected:
        raise MeasurementValidationError(f"{label}: expected {expected}, found {actual}")


def _equal_share(actual: object, expected: float, label: str) -> None:
    value = round(_number(actual, label), 4)
    if value != expected:
        raise MeasurementValidationError(f"{label}: expected {expected}, found {value}")


def _share(numerator: int, denominator: int) -> float:
    if denominator <= 0:
        raise MeasurementValidationError("metric denominator must be positive")
    return round(numerator / denominator, 4)


def validate_measurements(payload: Mapping[str, Any]) -> dict[str, Any]:
    """Return a denominator-audited measurement receipt from sanitized aggregates."""

    exp046 = _mapping(payload.get("exp046"), "exp046")
    agent_written = _integer(
        exp046.get("stage_2_agent_written_guidelines_reviewed"),
        "stage_2_agent_written_guidelines_reviewed",
    )
    missing_required = _integer(
        exp046.get("stage_2_missing_required_guidelines"),
        "stage_2_missing_required_guidelines",
    )
    total_review_rows = _integer(
        exp046.get("stage_2_total_review_rows"), "stage_2_total_review_rows"
    )
    _equal(total_review_rows, agent_written + missing_required, "guideline review-row total")

    stage2_status = _mapping(
        exp046.get("stage_2_agent_written_review_status_counts"),
        "stage_2_agent_written_review_status_counts",
    )
    full = _integer(stage2_status.get("accepted_in_full"), "accepted_in_full")
    partial = _integer(stage2_status.get("partially_accepted"), "partially_accepted")
    wrong = _integer(stage2_status.get("wrong"), "wrong")
    unsure = _integer(stage2_status.get("unsure"), "unsure")
    _equal(agent_written, full + partial + wrong + unsure, "guideline status totals")
    not_accepted = _integer(
        exp046.get("stage_2_not_accepted_in_full"), "stage_2_not_accepted_in_full"
    )
    _equal(not_accepted, partial + wrong + unsure, "not-accepted guideline total")
    guideline_not_accepted_share = _share(not_accepted, agent_written)
    _equal_share(
        exp046.get("stage_2_not_accepted_share_of_agent_written"),
        guideline_not_accepted_share,
        "not-accepted guideline share",
    )

    compliance_total = _integer(
        exp046.get("stage_3_compliance_judgments_reviewed"),
        "stage_3_compliance_judgments_reviewed",
    )
    compliance_status = _mapping(
        exp046.get("stage_3_compliance_status_counts"),
        "stage_3_compliance_status_counts",
    )
    satisfied = _integer(compliance_status.get("satisfied"), "satisfied")
    partial_satisfied = _integer(
        compliance_status.get("partially_satisfied"), "partially_satisfied"
    )
    not_satisfied = _integer(compliance_status.get("not_satisfied"), "not_satisfied")
    _equal(
        compliance_total,
        satisfied + partial_satisfied + not_satisfied,
        "compliance status totals",
    )

    change_total = _integer(
        exp046.get("stage_3_compliance_judgments_overturned"),
        "stage_3_compliance_judgments_overturned",
    )
    change_status = _mapping(
        exp046.get("stage_3_recorded_change_counts"), "stage_3_recorded_change_counts"
    )
    satisfied_changes = _integer(change_status.get("satisfied"), "satisfied changes")
    partial_changes = _integer(
        change_status.get("partially_satisfied"), "partially satisfied changes"
    )
    not_satisfied_changes = _integer(
        change_status.get("not_satisfied"), "not satisfied changes"
    )
    _equal(
        change_total,
        satisfied_changes + partial_changes + not_satisfied_changes,
        "compliance recorded-change totals",
    )
    compliance_change_share = _share(change_total, compliance_total)
    _equal_share(
        exp046.get("stage_3_compliance_overturn_share"),
        compliance_change_share,
        "compliance recorded-change share",
    )

    uncovered_total = _integer(
        exp046.get("stage_3_uncovered_fragment_judgments_reviewed"),
        "stage_3_uncovered_fragment_judgments_reviewed",
    )
    uncovered_changes = _integer(
        exp046.get("stage_3_uncovered_fragment_judgments_overturned"),
        "stage_3_uncovered_fragment_judgments_overturned",
    )
    _equal_share(
        exp046.get("stage_3_uncovered_fragment_overturn_share"),
        _share(uncovered_changes, uncovered_total),
        "uncovered-fragment recorded-change share",
    )

    flagged = _integer(exp046.get("non_satisfied_rule_flagged"), "non_satisfied_rule_flagged")
    covered = _integer(
        exp046.get("non_satisfied_rule_overturns_covered"),
        "non_satisfied_rule_overturns_covered",
    )
    _equal(
        _integer(exp046.get("non_satisfied_rule_denominator"), "non_satisfied_rule_denominator"),
        compliance_total,
        "non-Satisfied rule denominator",
    )
    _equal(
        _integer(
            exp046.get("non_satisfied_rule_total_overturns"),
            "non_satisfied_rule_total_overturns",
        ),
        change_total,
        "non-Satisfied total recorded changes",
    )
    _equal(flagged, partial_satisfied + not_satisfied, "non-Satisfied flagged total")
    _equal(covered, partial_changes + not_satisfied_changes, "non-Satisfied change coverage")

    exp045 = _mapping(payload.get("exp045"), "exp045")
    variability_triggers = _integer(
        exp045.get("stage_4_candidate_trigger_patterns"), "stage_4_candidate_trigger_patterns"
    )
    variability_total = _integer(
        exp045.get("stage_4_pattern_denominator"), "stage_4_pattern_denominator"
    )

    replay = _mapping(payload.get("c0_policy_replay"), "c0_policy_replay")
    events = _integer(replay.get("candidate_events"), "candidate_events")
    by_stage = _mapping(replay.get("by_stage"), "by_stage")
    stage_total = sum(_integer(value, f"by_stage.{key}") for key, value in by_stage.items())
    _equal(events, stage_total, "candidate-event stage total")
    budgets = _mapping(replay.get("budgets"), "budgets")
    expected_budgets = {
        "5_percent": max(1, math.floor(events * 0.05)),
        "10_percent": max(1, math.floor(events * 0.10)),
        "20_percent": max(1, math.floor(events * 0.20)),
    }
    for key, expected in expected_budgets.items():
        _equal(_integer(budgets.get(key), f"budgets.{key}"), expected, f"{key} budget")

    intervention = _mapping(payload.get("human_intervention_replay"), "human_intervention_replay")
    if intervention.get("run_a_run_b_hash_match") is not True:
        raise MeasurementValidationError("human intervention replay hashes do not match")
    if replay.get("run_a_run_b_hash_match") is not True:
        raise MeasurementValidationError("C0 replay hashes do not match")

    metrics = {
        "guideline_not_accepted_share": guideline_not_accepted_share,
        "h2_review_load_share": _share(flagged, compliance_total),
        "h2_recorded_change_coverage": _share(covered, change_total),
        "h2_recorded_change_yield": _share(covered, flagged),
        "h2_review_volume_not_selected_share": _share(compliance_total - flagged, compliance_total),
        "variability_trigger_share": _share(variability_triggers, variability_total),
        "matched_budgets": expected_budgets,
    }
    return {
        "schema_version": "vego-study1-measurement-validation-v1",
        "as_of": payload.get("as_of"),
        "status": "PASS",
        "metrics": metrics,
        "validated_invariants": [
            "guideline review rows and status categories reconcile",
            "stored derived shares match recomputed guideline, compliance, and uncovered-fragment values",
            "compliance judgments and recorded-change categories reconcile",
            "non-Satisfied rule numerators reconcile to category totals",
            "candidate events reconcile across lifecycle stages",
            "5/10/20 percent budgets use floor(event_count * rate)",
            "paired C0 and intervention runs are hash-identical",
        ],
        "claim_boundary": (
            "arithmetic_and_reproducibility_validation_only; recorded-change measures are "
            "descriptive and are not accuracy, human-benefit, or effort-reduction estimates"
        ),
    }


def write_validation_receipt(source: Path, destination: Path) -> dict[str, Any]:
    """Validate one sanitized result file and write a canonical public receipt."""

    payload = json.loads(source.read_text(encoding="utf-8"))
    if not isinstance(payload, Mapping):
        raise MeasurementValidationError("result payload must be an object")
    receipt = validate_measurements(payload)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(
        json.dumps(receipt, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return receipt
