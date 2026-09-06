"""Robustness tests for the frozen Detector-v1 and the Study 1 evidence rules.

These pin behaviour the reports depend on: the C1 threshold boundary, the S3
presence rule, lifecycle handling, and fail-closed behaviour on malformed event
streams. No provider is contacted and Detector-v1 itself is never modified.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))


def detector():
    from extract_qa_escalation_features import detect_detector_v1

    return detect_detector_v1


def episode(**overrides):
    base = {
        "episode_id": "EP-test",
        "scientific_complete": True,
        "termination_reason": "CONVERGED",
        "round_count": 1,
        "answers": [],
    }
    base.update(overrides)
    return base


def answer(confidence="High", evidence_length=42, evidence=True):
    return {
        "answer_confidence": confidence,
        "answer_evidence_ref": {"length": evidence_length} if evidence else None,
    }


# ── C1 boundary ──────────────────────────────────────────────────────────────

@pytest.mark.parametrize(
    "value,expected",
    [(0.699999, True), (0.7, False), (0.700001, False), (0.0, True), (1.0, False)],
)
def test_c1_threshold_is_strictly_below_zero_point_seven(value, expected):
    from extract_qa_escalation_features import _is_new_corpus_c1

    assert _is_new_corpus_c1(value) is expected


def test_c1_never_changes_a_classification():
    """C1 is contextual: it must not appear in any alert decision."""
    verdict = detector()(episode(answers=[answer("High")]))
    assert verdict["classification"] == "NO_ALERT"
    assert not any("C1" in code for code in verdict["all_signals_fired"])


# ── S3: presence and length only, never semantic quality ─────────────────────

def test_s3_fires_on_null_evidence():
    verdict = detector()(episode(answers=[answer("High", evidence=False)]))
    assert "S3_MISSING_ANSWER_EVIDENCE" in verdict["reason_codes"]
    assert verdict["classification"] == "STRONG_ALERT"


def test_s3_fires_on_zero_length_evidence():
    verdict = detector()(episode(answers=[answer("High", evidence_length=0)]))
    assert "S3_MISSING_ANSWER_EVIDENCE" in verdict["reason_codes"]


def test_s3_does_not_fire_on_nonempty_evidence_regardless_of_content():
    """One character of evidence is presence. Quality is never inspected."""
    verdict = detector()(episode(answers=[answer("High", evidence_length=1)]))
    assert "S3_MISSING_ANSWER_EVIDENCE" not in verdict["reason_codes"]
    assert verdict["classification"] == "NO_ALERT"


# ── Frozen rule table ────────────────────────────────────────────────────────

def test_strong_requires_s1_or_s3_or_s7():
    assert detector()(episode(answers=[answer("Low")]))["classification"] == "STRONG_ALERT"
    assert detector()(episode(answers=[answer("High", evidence=False)]))["classification"] == "STRONG_ALERT"
    max_rounds = episode(termination_reason="TERMINATED_MAX_ROUNDS", answers=[answer("High")])
    assert detector()(max_rounds)["classification"] == "STRONG_ALERT"


def test_weak_requires_no_strong_and_s2_or_s6():
    assert detector()(episode(answers=[answer("Medium")]))["classification"] == "WEAK_ALERT"
    assert detector()(episode(round_count=2, answers=[answer("High")]))["classification"] == "WEAK_ALERT"


def test_strong_suppresses_weak():
    verdict = detector()(episode(round_count=3, answers=[answer("Low"), answer("Medium")]))
    assert verdict["classification"] == "STRONG_ALERT"
    assert verdict["reason_codes"] == ["S1_LOW_ANSWER_CONFIDENCE"]
    assert "S2_MEDIUM_ANSWER_CONFIDENCE" in verdict["all_signals_fired"]


def test_no_alert_when_nothing_fires():
    assert detector()(episode(answers=[answer("High")]))["classification"] == "NO_ALERT"


def test_incomplete_technical_is_excluded_not_scored():
    verdict = detector()(
        episode(
            scientific_complete=False,
            termination_reason="INCOMPLETE_TECHNICAL",
            exclusion_reason="INCOMPLETE_TECHNICAL",
            answers=[answer("Low")],
        )
    )
    assert verdict["classification"] == "EXCLUDED"
    assert verdict["candidate_alert"] is False
    assert verdict["reason_codes"] == []


# ── Event-stream integrity ───────────────────────────────────────────────────

def test_malformed_event_stream_fails_closed():
    from qa_communication import QACommunicationValidationError, validate_event_stream

    with pytest.raises((QACommunicationValidationError, Exception)):
        validate_event_stream([{"event_type": "NOT_A_REAL_EVENT"}])


def test_duplicate_call_record_sequence_is_rejected():
    from airtravel_v4_contract import _validate_call

    row = {
        "sequence": 2,
        "phase": "phase3",
        "case_id": "01",
        "label": "agent3/01/resolve_r1",
        "source_agent": "agent3",
        "target_agent": "orchestrator",
        "prompt_sha256": "a" * 64,
        "prompt_length": 10,
        "answer_sha256": "b" * 64,
        "answer_length": 10,
        "decision_sha256": "c" * 64,
        "fake_client_identity": "LOCAL_DETERMINISTIC_FAKE_V4",
    }
    with pytest.raises(ValueError, match="append-only"):
        _validate_call(row, 1)


def test_route_direction_is_source_to_target_and_not_symmetric():
    from airtravel_local_observer import route_metrics

    events = [
        {
            "event_type": "QUESTION_EMITTED",
            "episode_id": "EP-1",
            "source_agent": "agent4",
            "target_agent": "agent2",
        }
    ]
    metrics = route_metrics(events)
    pairs = metrics["protected_orchestrator_fake_route_pairs"]
    assert pairs == [{"source_agent": "agent4", "target_agent": "agent2"}]
    assert pairs != [{"source_agent": "agent2", "target_agent": "agent4"}]
