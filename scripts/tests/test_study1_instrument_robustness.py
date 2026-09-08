"""Tests for the instrument-robustness and cost-calibration analyses.

They pin the correction that the adversarial review forced: a difference in the confidence
summary label must not be reported as a difference in Detector-v1 class when another recorded
strong signal (S3, S7) keeps the episode STRONG_ALERT. Synthetic event streams only; the frozen
detector is imported unmodified and no provider is contacted.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

import study1_cost_calibration as cost  # noqa: E402
import study1_instrument_robustness as rob  # noqa: E402


def episode_events(episode_id: str, labels: list[str], *, rounds: int, termination: str,
                   evidence_length: int = 40) -> list[dict]:
    events = []
    per_round = max(1, len(labels) // rounds)
    for i, label in enumerate(labels):
        qid = f"{episode_id}-Q{i}"
        round_index = min(rounds, i // per_round + 1)
        events.append({"event_type": "QUESTION_EMITTED", "episode_id": episode_id, "question_id": qid,
                       "round_index": round_index, "source_agent": "agent4", "target_agent": "agent2"})
        events.append({"event_type": "ANSWER_RECEIVED", "episode_id": episode_id, "question_id": qid,
                       "answer_confidence": label,
                       "answer_evidence_ref": {"sha256": "0" * 64, "length": evidence_length}})
    events.append({"event_type": "EPISODE_TERMINATED", "episode_id": episode_id, "termination_reason": termination})
    return events


def row(result, episode_id):
    return next(e for e in result["episodes"] if e["episode_id"] == episode_id)


def test_max_rounds_episode_keeps_strong_when_its_label_summary_is_medium():
    events = episode_events("EP-max", ["Low", "Medium", "Medium"], rounds=10, termination="TERMINATED_MAX_ROUNDS")
    result = rob.aggregation_sensitivity(events)
    r = row(result, "EP-max")
    assert r["frozen_class"] == "STRONG_ALERT"
    assert r["summaries"]["majority"] == "Medium"
    assert r["class_under_summary"]["majority"] == "STRONG_ALERT"
    assert r["s1_depends_on_summary"] is True
    assert r["class_depends_on_summary"] is False
    assert result["episodes_whose_class_depends_on_summary"] == []
    assert result["episodes_whose_s1_depends_on_summary"] == ["EP-max"]


def test_converged_single_round_episode_does_flip_to_weak_under_majority():
    events = episode_events("EP-conv", ["Low", "Medium", "Medium"], rounds=1, termination="CONVERGED")
    result = rob.aggregation_sensitivity(events)
    r = row(result, "EP-conv")
    assert r["frozen_class"] == "STRONG_ALERT"
    assert r["class_under_summary"]["majority"] == "WEAK_ALERT"
    assert r["class_depends_on_summary"] is True
    assert result["episodes_whose_class_depends_on_summary"] == ["EP-conv"]


def test_missing_evidence_keeps_strong_under_every_summary():
    events = episode_events("EP-s3", ["Low", "High", "High"], rounds=1, termination="CONVERGED", evidence_length=0)
    r = row(rob.aggregation_sensitivity(events), "EP-s3")
    assert "S3_MISSING_ANSWER_EVIDENCE" in r["recorded_other_signals"]
    assert set(r["class_under_summary"].values()) == {"STRONG_ALERT"}
    assert r["class_depends_on_summary"] is False


def test_no_majority_is_explicit_and_contributes_neither_s1_nor_s2():
    events = episode_events("EP-tie", ["Low", "Medium", "High"], rounds=1, termination="CONVERGED")
    r = row(rob.aggregation_sensitivity(events), "EP-tie")
    assert r["summaries"]["majority"] == "NO_MAJORITY"
    assert r["class_under_summary"]["majority"] == "NO_ALERT"
    assert r["summaries"]["ordinal_median"] == "Medium"


def test_reapplied_any_always_matches_detector_v1():
    from extract_qa_escalation_features import detect_detector_v1
    from airtravel_detector_analysis import project_episodes

    combos = [(["High"], 1, "CONVERGED"), (["Medium", "High"], 2, "CONVERGED"),
              (["Low"], 1, "CONVERGED"), (["High", "High"], 10, "TERMINATED_MAX_ROUNDS")]
    events = [e for i, (labels, rounds, term) in enumerate(combos)
              for e in episode_events(f"EP-{i}", labels, rounds=rounds, termination=term)]
    result = rob.aggregation_sensitivity(events)
    verdicts = {ep["episode_id"]: detect_detector_v1(ep)["classification"] for ep in project_episodes(events)}
    for r in result["episodes"]:
        assert r["class_under_summary"]["any"] == verdicts[r["episode_id"]] == r["frozen_class"]


def test_excluded_episodes_are_not_scored_and_leave_one_out_denominator_excludes_them():
    events = (episode_events("EP-a", ["Low"], rounds=1, termination="CONVERGED")
              + episode_events("EP-b", ["High"], rounds=1, termination="CONVERGED")
              + episode_events("EP-x", ["Low"], rounds=1, termination="INCOMPLETE_TECHNICAL"))
    canonical = rob.classify(events)
    assert canonical["EP-x"]["classification"] == "EXCLUDED"
    loo = rob.leave_one_out(events, canonical)
    assert [r["dropped_episode"] for r in loo] == ["EP-a", "EP-b"]
    for r in loo:
        assert r["denominator"] == 1
        assert sum(r["distribution"].values()) == r["denominator"]
    assert all(e["episode_id"] != "EP-x" for e in rob.aggregation_sensitivity(events)["episodes"])


def test_order_invariance_holds_on_synthetic_stream():
    events = (episode_events("EP-a", ["Low", "Medium"], rounds=2, termination="CONVERGED")
              + episode_events("EP-b", ["High"], rounds=1, termination="CONVERGED"))
    canonical = rob.classify(events)
    oi = rob.order_invariance(events, canonical)
    assert oi["invariant"] is True
    assert oi["episodes_with_multiple_termination_events"] == 0


def usage(completion_per_request: float, n: int = 43) -> dict:
    return {"outbound_requests": n, "prompt_tokens": 186_558, "completion_tokens": int(completion_per_request * n),
            "actual_cost_usd": 0.134972, "price_input_per_1m_usd": 0.2, "price_output_per_1m_usd": 1.2}


def test_truncation_statement_is_computed_not_asserted():
    below = cost.calibration(usage(1_800))["truncation_risk_under_pilot_cap"]
    above = cost.calibration(usage(5_000))["truncation_risk_under_pilot_cap"]
    assert below["mean_below_pilot_cap"] is True
    assert above["mean_below_pilot_cap"] is False
    assert below["max_completion_tokens_per_request"] == "NOT_AVAILABLE"
    assert below["share_of_requests_the_cap_would_truncate"] == "NOT_AVAILABLE"


def test_menu_uses_reserve_bound_terminology_and_frozen_rows_are_marked():
    rows = cost.menu(usage(1_893))
    assert rows and all("reserve_bound_usd" in r and "proven_bound_usd" not in r for r in rows)
    study1b = [r for r in rows if r["is_frozen_study1b"]]
    pilot = [r for r in rows if r["is_frozen_pilot"]]
    assert len(study1b) == len(pilot) == 1
    assert study1b[0]["reserve_bound_usd"] == pytest.approx(34.6551, abs=1e-4)
    assert pilot[0]["reserve_bound_usd"] == pytest.approx(1.7591, abs=1e-4)
    assert not study1b[0]["fits"]["6.00"] and pilot[0]["fits"]["2.00"]


def test_actuals_keep_maxima_and_per_episode_cost_not_available():
    a = cost.actuals(usage(1_893))
    assert a["max_prompt_tokens_per_request"] == "NOT_AVAILABLE"
    assert a["max_completion_tokens_per_request"] == "NOT_AVAILABLE"
    assert a["per_episode_cost"] == "NOT_AVAILABLE"
    assert json.dumps(a)  # serialisable
