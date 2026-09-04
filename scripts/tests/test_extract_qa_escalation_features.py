"""Tests for the read-only Q&A escalation observability scaffold."""

from __future__ import annotations

import json
import pathlib
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

import extract_qa_escalation_features as extractor  # noqa: E402


def test_malformed_event_fails_closed() -> None:
    with pytest.raises(extractor.ExtractionError):
        extractor.validate_event({"event_id": "x"})


def test_detector_is_transparent_and_non_optimizing() -> None:
    event = extractor.make_event(
        source_path="fixture.json",
        source_agent="agent2",
        source_stage="phase2_guideline_build",
        target_agent="language_advisor",
        scope="language",
        question={"id": "Q_lang_001", "question": "Clarify this."},
        answer=None,
        source_hash="0" * 64,
    )
    alert = extractor.detect_event(event)
    assert alert["decision"] == "NO_ALERT"
    assert alert["reason_codes"] == []
    assert alert["answer_status"] == "ANSWER_NOT_PERSISTED"
    assert alert["answer_confidence"] is None


def test_answer_confidence_and_evidence_are_not_merged() -> None:
    event = extractor.make_event(
        source_path="fixture.json",
        source_agent="agent1",
        source_stage="phase2_answer",
        target_agent="language_advisor",
        scope="language",
        question={"id": "Q_lang_001", "question": "Clarify this."},
        answer={"answer": "It depends.", "confidence": "Low", "evidence": "p. 1"},
        source_hash="0" * 64,
    )
    assert event["answer_confidence"] == "Low"
    assert event["evidence_present"] is True
    assert extractor.detect_event(event)["reason_codes"] == ["F1_LOW_ANSWER_CONFIDENCE", "F2_LOW_OR_MEDIUM_ANSWER_CONFIDENCE"]


def test_alert_only_evaluation_cannot_compute_recall() -> None:
    with pytest.raises(extractor.EvaluationError, match="recall"):
        extractor.evaluate_alerts(
            [{"decision": "ALERT", "alert_id": "a"}],
            [{"alert_id": "a", "review_label": "HUMAN INTERVENTION REQUIRED"}],
            labels_cover_all_events=False,
        )


@pytest.mark.skipif(
    not (ROOT / "VEGO-AI" / "eval_output" / "cd_ch" / "agentB_best_guidelines.json").exists(),
    reason="local frozen outputs are not available",
)
def test_frozen_qa_snapshot_is_deterministic_and_unanswered() -> None:
    first = extractor.extract_frozen_corpus(ROOT / "VEGO-AI")
    second = extractor.extract_frozen_corpus(ROOT / "VEGO-AI")
    assert first == second
    assert first["summary"]["canonical_questions"] == 12
    assert first["summary"]["answers"] == 0
    assert first["summary"]["unanswered_questions"] == 12
    assert first["summary"]["by_source_agent"] == {"agent2": 12}
    assert all(event["answer_confidence"] is None for event in first["events"])


def test_blind_review_rows_do_not_expose_detector_decision(tmp_path: pathlib.Path) -> None:
    event = extractor.make_event(
        source_path="fixture.json",
        source_agent="agent2",
        source_stage="phase2_guideline_build",
        target_agent="language_advisor",
        scope="language",
        question={"id": "Q_lang_001", "question": "Clarify this."},
        answer=None,
        source_hash="0" * 64,
    )
    alerts = [extractor.detect_event(event)]
    paths = extractor.write_blind_review_material(alerts, tmp_path)
    blind = json.loads(paths["reviewer_a"].read_text(encoding="utf-8"))
    assert "decision" not in blind[0]
    assert "reason_codes" not in blind[0]
    assert blind[0]["review_label"] == ""


def test_extractor_has_no_network_or_model_client_path() -> None:
    source = (ROOT / "scripts" / "extract_qa_escalation_features.py").read_text(encoding="utf-8")
    assert "openai" not in source.lower()
    assert "requests" not in source.lower()
    assert "urlopen" not in source.lower()
