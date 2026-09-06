from __future__ import annotations

import json
import pathlib
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]

sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "VEGO-AI" / "framework"))

import build_study1_signal_traceability as traceability  # noqa: E402
from extract_qa_escalation_features import detect_detector_v1  # noqa: E402
from qa_communication import QACommunicationRecorder  # noqa: E402


def _episode(*, confidence="High", evidence=True, rounds=1, termination="CONVERGED"):
    ref = {"sha256": "0" * 64, "length": 3} if evidence else None
    return {
        "episode_id": "ep-fixture",
        "scientific_complete": True,
        "exclusion_reason": None,
        "termination_reason": termination,
        "round_count": rounds,
        "answers": [{"answer_confidence": confidence, "answer_evidence_ref": ref}],
    }


@pytest.mark.parametrize(
    ("episode", "classification", "reason"),
    [
        (_episode(), "NO_ALERT", []),
        (_episode(confidence="Low"), "STRONG_ALERT", ["S1_LOW_ANSWER_CONFIDENCE"]),
        (_episode(confidence="Medium"), "WEAK_ALERT", ["S2_MEDIUM_ANSWER_CONFIDENCE"]),
        (_episode(evidence=False), "STRONG_ALERT", ["S3_MISSING_ANSWER_EVIDENCE"]),
        (_episode(rounds=2), "WEAK_ALERT", ["S6_MULTIPLE_QA_ROUNDS"]),
        (_episode(termination="TERMINATED_MAX_ROUNDS"), "STRONG_ALERT", ["S7_TERMINATED_MAX_ROUNDS"]),
    ],
)
def test_detector_v1_truth_table(episode, classification, reason):
    result = detect_detector_v1(episode)
    assert result["classification"] == classification
    assert result["reason_codes"] == reason
    assert result["candidate_alert"] is (classification != "NO_ALERT")


def test_detector_v1_preserves_cooccurrence_and_strong_precedence():
    episode = _episode(confidence="Low", evidence=False, rounds=2,
                       termination="TERMINATED_MAX_ROUNDS")
    result = detect_detector_v1(episode)
    assert result["classification"] == "STRONG_ALERT"
    assert "S2_MEDIUM_ANSWER_CONFIDENCE" not in result["reason_codes"]
    assert set(result["all_signals_fired"]) == {
        "S1_LOW_ANSWER_CONFIDENCE",
        "S3_MISSING_ANSWER_EVIDENCE",
        "S6_MULTIPLE_QA_ROUNDS",
        "S7_TERMINATED_MAX_ROUNDS",
    }


def test_context_and_semantic_fields_never_trigger_detector():
    episode = _episode()
    episode.update({
        "mapping_certainty": 0.1,
        "agent4_confidence": "Low",
        "requires_human_review": True,
        "flag_for_guidelines_update": True,
        "compliance_status": "Non-Satisfied",
        "fragment_label": "Alternative",
    })
    result = detect_detector_v1(episode)
    assert result["classification"] == "NO_ALERT"
    assert result["reason_codes"] == []


def test_signal_dictionary_predicates_are_code_grounded():
    source = (ROOT / "scripts" / "extract_qa_escalation_features.py").read_text(encoding="utf-8")
    entries = {row["english_code_name"]: row for row in traceability.signal_dictionary()["entries"]}
    expected = {
        "S1_LOW_ANSWER_CONFIDENCE": 'row.get("answer_confidence") == "Low"',
        "S2_MEDIUM_ANSWER_CONFIDENCE": 'row.get("answer_confidence") == "Medium"',
        "S3_MISSING_ANSWER_EVIDENCE": 'row.get("answer_evidence_ref")',
        "S6_MULTIPLE_QA_ROUNDS": 'episode.get("round_count", 0) > 1',
        "S7_TERMINATED_MAX_ROUNDS": 'episode.get("termination_reason") == "TERMINATED_MAX_ROUNDS"',
    }
    for code, snippet in expected.items():
        assert snippet in source
        assert snippet in entries[code]["calculation_rule"]
        assert entries[code]["direct_detector_v1_trigger"] is True


def test_route_orientation_is_explicit():
    recorder = QACommunicationRecorder(run_id="trace-fixture")
    question = recorder.emit_question(
        episode_id="ep-1", question_id="Q_lang_001", source_agent="agent2",
        source_stage="fixture", source_skill="fixture", target_agent="agent1",
        scope="language", case_id="case-1", question_text="fixture question", round_index=1,
    )
    recorder.emit_answer(question=question, answer_text="fixture answer",
                         answer_confidence="High", answer_evidence="fixture evidence")
    recorder.emit_termination(episode_id="ep-1", termination_reason="CONVERGED", converged=True)
    summary = traceability.aggregate_verified_events(recorder.events)
    row = summary["tables"]["route_matrix"]["rows"][0]
    assert row["asking_agent"] == "agent2"
    assert row["answering_agent"] == "agent1"
    assert "source_agent" not in row
    assert "target_agent" not in row


def test_missing_event_log_cannot_produce_numeric_metrics(tmp_path):
    metrics = traceability.build_metrics(None, evidence_status=traceability.NOT_AVAILABLE)
    assert metrics["evidence_status"] == traceability.NOT_AVAILABLE
    assert metrics["denominator"] == traceability.NOT_AVAILABLE
    for table in metrics["tables"].values():
        assert table["evidence_status"] == traceability.NOT_AVAILABLE
        assert table["denominator"] == traceability.NOT_AVAILABLE
        assert table["rows"] == []

    def reject_numbers(value):
        if isinstance(value, bool) or value is None:
            return
        if isinstance(value, (int, float)):
            raise AssertionError(f"numeric result leaked from unavailable evidence: {value}")
        if isinstance(value, dict):
            for child in value.values():
                reject_numbers(child)
        elif isinstance(value, list):
            for child in value:
                reject_numbers(child)

    reject_numbers(metrics)


def test_every_generated_table_declares_status_and_denominator():
    metrics = traceability.build_metrics(None, evidence_status=traceability.NOT_AVAILABLE)
    assert metrics["tables"]
    for name, table in metrics["tables"].items():
        assert name
        assert set(("evidence_status", "denominator", "rows")) <= table.keys()


def test_aggregate_exposes_producing_phase_and_round_tables():
    recorder = QACommunicationRecorder(run_id="trace-fixture")
    question = recorder.emit_question(
        episode_id="ep-1", question_id="Q_lang_001", source_agent="agent2",
        source_stage="guideline", source_skill="fixture", target_agent="agent1",
        scope="language", case_id="case-1", question_text="fixture question", round_index=1,
    )
    recorder.emit_answer(question=question, answer_text="fixture answer",
                         answer_confidence="High", answer_evidence="fixture evidence")
    recorder.emit_termination(episode_id="ep-1", termination_reason="CONVERGED", converged=True)
    summary = traceability.aggregate_verified_events(recorder.events)
    producing = summary["tables"]["episodes_by_producing_agent_phase"]
    rounds = summary["tables"]["rounds_per_episode"]
    assert producing["denominator"] == "complete_scientific_episodes"
    assert producing["rows"] == [{"producing_agent": "agent2", "phase": "guideline", "episode_count": 1}]
    assert rounds["rows"][0]["round_count"] == 1
    assert rounds["rows"][0]["question_count"] == 1
    assert rounds["rows"][0]["answer_count"] == 1


def test_dictionary_and_matrix_have_required_contract_fields():
    dictionary = traceability.signal_dictionary()
    assert dictionary["review_context"]["origin_main_sha"] == "c34d3954b5e080d090017d2ea655d454d75a6b92"
    assert dictionary["review_context"]["pr_38_head"] == "a976494a624391efb0fb96e8f769512f52f52af0"
    assert dictionary["review_context"]["pr_41_head"] == "63da0105f25207e3cc6e67bb3ec499652d65124c"
    assert dictionary["review_context"]["pr_42_head"] == "de65a57d5ca7289cc6032baa7cc797499fdc6812"
    required = {
        "hebrew_name", "english_code_name", "source_artifact", "source_field",
        "unit_of_analysis", "calculation_rule", "code_reference", "measurement_kind",
        "can_cooccur_with_other_signals", "detector_role", "direct_detector_v1_trigger",
        "candidate_for_human_review", "does_not_prove",
    }
    assert dictionary["entries"]
    for entry in dictionary["entries"]:
        assert required <= entry.keys(), entry["english_code_name"]
    assert traceability.TRACEABILITY_COLUMNS == [
        "Category", "Variable/signal", "Measured from", "Unit", "Asking agent",
        "Answering agent", "Direct trigger?", "Action", "Not evidence of",
    ]


def test_hebrew_note_contract_is_rtl_and_bounded():
    note = traceability.ROOT / "docs" / "research" / "phd-proposal" / "2026-09-06-study1-signal-technical-note.he.md"
    # The generated note is checked in after the build step; this assertion
    # remains a no-op for a clean source checkout before generation.
    if note.exists():
        text = note.read_text(encoding="utf-8")
        assert text.startswith('<div dir="rtl">')
        assert "STRONG_ALERT = S1 OR S3 OR S7" in text
        assert "NOT_AVAILABLE_IN_WORKTREE" in text


def test_manifest_mismatch_fails_closed(tmp_path):
    event_log = tmp_path / "qa_events.jsonl"
    event_log.write_text("{}\n", encoding="utf-8")
    manifest = tmp_path / "binding.json"
    manifest.write_text(json.dumps({
        "accepted_run": True,
        "run_identity": {
            "run_id": "run-1",
            "run_class": "accepted_replacement_real_run",
            "accepted_replacement": True,
            "fake_preflight": False,
            "status": "ACCEPTED_REPLACEMENT",
        },
        "artifacts": {"qa_events_jsonl": {"sha256": "0" * 64}},
    }), encoding="utf-8")
    with pytest.raises(traceability.EvidenceError):
        traceability.load_verified_events(event_log, manifest)


def test_bound_accepted_event_log_can_be_recomputed_without_raw_output(tmp_path):
    event_log = tmp_path / "qa_events.jsonl"
    recorder = QACommunicationRecorder(event_log, run_id="accepted-fixture")
    question = recorder.emit_question(
        episode_id="ep-1", question_id="Q_lang_001", source_agent="agent2",
        source_stage="fixture", source_skill="fixture", target_agent="agent1",
        scope="language", case_id="case-1", question_text="private fixture question", round_index=1,
    )
    recorder.emit_answer(question=question, answer_text="private fixture answer",
                         answer_confidence="Medium", answer_evidence="evidence")
    recorder.emit_termination(episode_id="ep-1", termination_reason="CONVERGED", converged=True)
    manifest = tmp_path / "binding.json"
    manifest.write_text(json.dumps({
        "accepted_run": True,
        "run_identity": {
            "run_id": "accepted-fixture",
            "run_class": "accepted_replacement_real_run",
            "accepted_replacement": True,
            "fake_preflight": False,
            "status": "ACCEPTED_REPLACEMENT",
        },
        "artifacts": {"qa_events_jsonl": {"sha256": traceability._sha256_file(event_log)}},
    }), encoding="utf-8")

    events = traceability.load_verified_events(event_log, manifest)
    metrics = traceability.build_metrics(events, evidence_status=traceability.AVAILABLE)
    assert metrics["evidence_status"] == traceability.AVAILABLE
    assert metrics["tables"]["episodes"]["rows"][0]["detector_classification"] == "WEAK_ALERT"
    rendered = json.dumps(metrics, ensure_ascii=False)
    assert "private fixture question" not in rendered
    assert "private fixture answer" not in rendered
