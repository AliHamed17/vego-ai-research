"""Tests for the agentC score correction layer."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from score_correction import (  # noqa: E402
    CorrectionConfig,
    correct_case,
    fragment_contribution,
    is_self_critical,
    load_expressibility,
)

REPO = Path(__file__).resolve().parents[2]
EXPRESSIBILITY = REPO / "configs" / "guideline-expressibility-v1.json"


def make_case(compliance, fragments, max_score=None, score_pct=0.0):
    return {
        "case_id": "T1",
        "compliance_contributions": compliance,
        "fragment_contributions": fragments,
        "max_score": max_score if max_score is not None else len(compliance),
        "score_pct": score_pct,
    }


def test_fragment_contribution_prefers_total_contribution():
    assert fragment_contribution({"total_contribution": -1.0, "base_score": -1.0,
                                  "severity_modifier": -0.5}) == -1.0


def test_fragment_contribution_falls_back_to_product():
    assert fragment_contribution({"base_score": -1.0, "severity_modifier": 0.5}) == -0.5


def test_bonus_cannot_exceed_full_marks():
    case = make_case([{"guideline_id": "G1", "score": 1.0}],
                     [{"total_contribution": 0.5, "fragment": "extra content"}])
    out = correct_case(case, {}, CorrectionConfig())
    assert out["corrected_score_pct"] == pytest.approx(100.0)
    assert out["bonus_effective"] == 0.0
    assert out["bonus_withheld"] == pytest.approx(0.5)


def test_bonus_may_offset_a_penalty():
    case = make_case([{"guideline_id": "G1", "score": 1.0}, {"guideline_id": "G2", "score": 1.0}],
                     [{"total_contribution": 0.5, "fragment": "extra content"},
                      {"total_contribution": -0.5, "fragment": "a real defect"}])
    out = correct_case(case, {}, CorrectionConfig())
    assert out["bonus_effective"] == pytest.approx(0.5)
    assert out["corrected_total"] == pytest.approx(2.0)


def test_self_critical_reward_is_rejected():
    case = make_case([{"guideline_id": "G1", "score": 1.0}],
                     [{"total_contribution": 0.5,
                       "fragment": "SalesStaff extends Employee but does not provide new attributes"}])
    out = correct_case(case, {}, CorrectionConfig())
    assert len(out["rewards_rejected_as_self_critical"]) == 1
    assert out["bonus_raw"] == 0.0


def test_self_critical_detection_is_case_insensitive():
    assert is_self_critical("Class LACKS operations")
    assert not is_self_critical("Class declares three operations")


def test_inexpressible_guideline_receives_partial_credit():
    case = make_case([{"guideline_id": "G1", "score": 1.0}, {"guideline_id": "G2", "score": 1.0}], [])
    out = correct_case(case, {"G1": "N"}, CorrectionConfig(inexpressible_credit_fraction=0.5))
    assert out["corrected_total"] == pytest.approx(1.5)
    assert out["guidelines_credit_reduced"][0]["guideline_id"] == "G1"


def test_expressible_guideline_keeps_full_credit():
    case = make_case([{"guideline_id": "G1", "score": 1.0}], [])
    out = correct_case(case, {"G1": "E"}, CorrectionConfig(inexpressible_credit_fraction=0.5))
    assert out["corrected_total"] == pytest.approx(1.0)
    assert out["guidelines_credit_reduced"] == []


def test_uncredited_inexpressible_guideline_is_untouched():
    case = make_case([{"guideline_id": "G1", "score": 0.0}], [])
    out = correct_case(case, {"G1": "N"}, CorrectionConfig())
    assert out["guidelines_credit_reduced"] == []


def test_corrections_can_each_be_disabled():
    case = make_case([{"guideline_id": "G1", "score": 1.0}],
                     [{"total_contribution": 0.5, "fragment": "lacks nothing at all"}])
    off = CorrectionConfig(bonus_may_only_offset_penalties=False,
                           reject_self_critical_rewards=False,
                           inexpressible_credit_fraction=1.0,
                           cap_at_full_marks=False)
    out = correct_case(case, {"G1": "N"}, off)
    assert out["corrected_total"] == pytest.approx(1.5)
    assert out["rewards_rejected_as_self_critical"] == []


def test_score_over_one_hundred_is_impossible_after_correction():
    case = make_case([{"guideline_id": f"G{i}", "score": 1.0} for i in range(1, 6)],
                     [{"total_contribution": 0.5, "fragment": f"extra {i}"} for i in range(8)],
                     score_pct=122.2)
    out = correct_case(case, {}, CorrectionConfig())
    assert out["corrected_score_pct"] <= 100.0


def test_shipped_expressibility_file_is_well_formed():
    coding = load_expressibility(EXPRESSIBILITY)
    assert set(coding) == {"cd_ch", "cd_pw", "ucd_ch", "ucd_pw"}
    total = sum(len(v) for v in coding.values())
    assert total == 119
    for per_condition in coding.values():
        assert set(per_condition.values()) <= {"N", "E", "X"}


def test_expressibility_file_parses_as_json():
    json.loads(EXPRESSIBILITY.read_text(encoding="utf-8"))
