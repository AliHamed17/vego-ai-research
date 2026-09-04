from __future__ import annotations

from pathlib import Path

import pytest
from qa_communication import (
    QACommunicationRecorder,
    QACommunicationValidationError,
    build_episode_projection,
    validate_event_stream,
)


def _events(tmp_path: Path) -> list[dict]:
    recorder = QACommunicationRecorder(tmp_path / "events.jsonl", run_id="fixture-run")
    question = recorder.emit_question(
        question_id="Q_lang_001",
        episode_id="episode-1",
        source_agent="agent3",
        source_stage="case_inspection",
        source_skill="resolve_unsatisfied",
        target_agent="agent1",
        scope="language",
        question_text="Which template applies?",
        round_index=1,
    )
    recorder.emit_answer(
        question=question,
        answer_text="Template T1 applies.",
        answer_confidence="High",
        answer_evidence="T1 definition",
        source_tier="language_manual",
    )
    recorder.emit_termination(
        episode_id="episode-1", question_id="Q_lang_001", round_index=1,
        termination_reason="CONVERGED", converged=True,
    )
    return recorder.events


def test_append_only_events_project_to_complete_episode(tmp_path: Path) -> None:
    events = _events(tmp_path)
    projection = build_episode_projection(events)
    assert projection[0]["question_count"] == 1
    assert projection[0]["answer_count"] == 1
    assert projection[0]["converged"] is True
    assert projection[0]["termination_reason"] == "CONVERGED"
    assert projection[0]["round_count"] == 1
    assert projection[0]["answers"][0]["answer_confidence"] == "High"


def test_event_ids_and_order_are_deterministic(tmp_path: Path) -> None:
    first = _events(tmp_path / "one")
    second = _events(tmp_path / "two")
    assert [e["event_id"] for e in first] == [e["event_id"] for e in second]
    assert [e["sequence"] for e in first] == [1, 2, 3]


def test_malformed_and_duplicate_events_fail_closed(tmp_path: Path) -> None:
    events = _events(tmp_path)
    with pytest.raises(QACommunicationValidationError):
        validate_event_stream([{**events[0], "event_id": "bad"}])
    with pytest.raises(QACommunicationValidationError):
        validate_event_stream(events + [events[0]])


def test_jsonl_contains_metadata_only_references(tmp_path: Path) -> None:
    path = tmp_path / "events.jsonl"
    _events(tmp_path)
    payload = path.read_text(encoding="utf-8")
    assert "Which template applies?" not in payload
    assert "Template T1 applies." not in payload
    assert "question_text_ref" in payload
    assert "answer_text_ref" in payload


def test_all_supported_routes_are_representable(tmp_path: Path) -> None:
    routes = [("agent2", "agent1"), ("agent2", "agent2"), ("agent3", "agent1"),
              ("agent3", "agent2"), ("agent4", "agent1"), ("agent4", "agent2")]
    recorder = QACommunicationRecorder(tmp_path / "routes.jsonl", run_id="routes")
    for index, (source, target) in enumerate(routes, start=1):
        scope = "language" if target == "agent1" else "domain"
        question = recorder.emit_question(
            question_id=f"Q_{index:03d}", episode_id=f"ep-{index}", source_agent=source,
            source_stage="fixture", source_skill="route", target_agent=target,
            scope=scope, question_text="q", round_index=1,
        )
        recorder.emit_answer(question=question, answer_text="a", answer_confidence="Low")
        recorder.emit_termination(episode_id=f"ep-{index}", question_id=f"Q_{index:03d}",
                                  termination_reason="CONVERGED", converged=True, round_index=1)
    projections = build_episode_projection(recorder.events)
    assert len(projections) == len(routes)
    assert sorted(projections[0]["source_target_pairs"]) == [("agent2", "agent1")]


def test_follow_up_and_max_round_termination_are_projected(tmp_path: Path) -> None:
    recorder = QACommunicationRecorder(tmp_path / "followup.jsonl", run_id="followup")
    first = recorder.emit_question(
        question_id="Q_001", episode_id="ep", source_agent="agent3", source_stage="case",
        source_skill="resolve", target_agent="agent1", scope="language", question_text="q1",
        round_index=1,
    )
    recorder.emit_answer(question=first, answer_text="a1", answer_confidence="Low")
    second = recorder.emit_question(
        question_id="Q_002", episode_id="ep", source_agent="agent3", source_stage="case",
        source_skill="resolve", target_agent="agent1", scope="language", question_text="q2",
        round_index=2, follow_up_to_event_id=first["event_id"],
    )
    recorder.emit_answer(question=second, answer_text="a2", answer_confidence="Medium")
    recorder.emit_termination(episode_id="ep", question_id="Q_002", round_index=2,
        termination_reason="TERMINATED_MAX_ROUNDS", converged=False)
    projection = build_episode_projection(recorder.events)[0]
    assert projection["round_count"] == 2
    assert projection["follow_up_present"] is True
    assert projection["termination_reason"] == "TERMINATED_MAX_ROUNDS"
    assert projection["converged"] is False
    assert projection["termination_reason"] == "TERMINATED_MAX_ROUNDS"


def test_explicit_incomplete_technical_termination_is_projected(tmp_path: Path) -> None:
    recorder = QACommunicationRecorder(tmp_path / "incomplete.jsonl", run_id="incomplete")
    recorder.emit_termination(
        episode_id="ep", termination_reason="INCOMPLETE_TECHNICAL",
    )
    assert build_episode_projection(recorder.events) == []


def test_lifecycle_invariants_fail_closed(tmp_path: Path) -> None:
    recorder = QACommunicationRecorder(tmp_path / "lifecycle.jsonl", run_id="lifecycle")
    question = recorder.emit_question(
        question_id="Q_001", episode_id="ep", source_agent="agent2", source_stage="phase2",
        source_skill="qa", target_agent="agent1", scope="language", question_text="q", round_index=1,
    )
    with pytest.raises(QACommunicationValidationError):
        recorder.emit_termination(episode_id="ep", termination_reason="OTHER", converged=True)
    with pytest.raises(QACommunicationValidationError):
        recorder.emit_termination(episode_id="ep", termination_reason="CONVERGED", converged=False)
    recorder.emit_answer(question=question, answer_text="a", answer_confidence="High")
    recorder.emit_termination(episode_id="ep", termination_reason="CONVERGED", converged=True)
    duplicate = dict(recorder.events[1])
    duplicate["sequence"] = 4
    with pytest.raises(QACommunicationValidationError):
        validate_event_stream(recorder.events + [duplicate])


def test_unterminated_episode_is_not_scientifically_complete(tmp_path: Path) -> None:
    recorder = QACommunicationRecorder(tmp_path / "open.jsonl", run_id="open")
    recorder.emit_question(question_id="Q_001", episode_id="ep", source_agent="agent2",
                           source_stage="phase2", source_skill="qa", target_agent="agent1",
                           scope="language", question_text="q", round_index=1)
    projection = build_episode_projection(recorder.events)[0]
    assert projection["scientific_complete"] is False
    assert projection["exclusion_reason"] == "UNTERMINATED"


def test_mixed_run_and_cross_episode_answer_fail_closed(tmp_path: Path) -> None:
    recorder = QACommunicationRecorder(tmp_path / "mixed.jsonl", run_id="run-a")
    first = recorder.emit_question(question_id="Q_001", episode_id="ep-a", source_agent="agent2",
                                   source_stage="phase2", source_skill="qa", target_agent="agent1",
                                   scope="language", question_text="q", round_index=1)
    recorder.emit_answer(question=first, answer_text="a", answer_confidence="High")
    recorder.emit_termination(episode_id="ep-a", termination_reason="CONVERGED", converged=True)
    cross = dict(recorder.events[1])
    cross["episode_id"] = "ep-b"
    with pytest.raises(QACommunicationValidationError):
        validate_event_stream(recorder.events + [cross])
    mixed = dict(recorder.events[0])
    mixed["run_id"] = "run-b"
    with pytest.raises(QACommunicationValidationError):
        validate_event_stream([mixed])


def test_empty_scientific_episode_fails_closed(tmp_path: Path) -> None:
    recorder = QACommunicationRecorder(tmp_path / "empty.jsonl", run_id="empty")
    recorder.emit_termination(episode_id="ep", termination_reason="CONVERGED", converged=True)
    with pytest.raises(QACommunicationValidationError):
        validate_event_stream(recorder.events)


def test_events_after_termination_and_duplicate_terminal_fail_closed(tmp_path: Path) -> None:
    events = _events(tmp_path)
    after = dict(events[0])
    after["sequence"] = 4
    after["event_id"] = "tampered"
    with pytest.raises(QACommunicationValidationError):
        validate_event_stream(events + [after])
    duplicate = dict(events[-1])
    duplicate["sequence"] = 4
    duplicate["event_id"] = "tampered-terminal"
    with pytest.raises(QACommunicationValidationError):
        validate_event_stream(events + [duplicate])


def test_answer_before_question_and_cross_run_stream_fail_closed(tmp_path: Path) -> None:
    events = _events(tmp_path)
    answer, question = events[1], events[0]
    reordered = [answer, question, events[2]]
    for index, event in enumerate(reordered, start=1):
        event = dict(event)
        event["sequence"] = index
        reordered[index - 1] = event
    with pytest.raises(QACommunicationValidationError):
        validate_event_stream(reordered)
    mixed = [dict(event) for event in events]
    mixed[-1]["run_id"] = "other-run"
    with pytest.raises(QACommunicationValidationError):
        validate_event_stream(mixed)


def test_instrumentation_off_on_preserves_prompt_and_answer(tmp_path: Path) -> None:
    prompt = {"system": "system", "user": "user"}
    answer = {"question_id": "Q_lang_001", "answer": "ok", "confidence": "High"}
    recorder = QACommunicationRecorder(tmp_path / "events.jsonl", run_id="run-1")
    recorder.observe_exchange(
        questions=[{"question_id": "Q_lang_001", "question": "q"}], answers=[answer],
        source_agent="agent2", source_stage="fixture", source_skill="route",
        target_agent="agent1", scope="language", episode_id="ep-1", round_index=1,
    )
    assert prompt == {"system": "system", "user": "user"}
    assert answer["confidence"] == "High"
    assert [event["event_type"] for event in recorder.events] == [
        "QUESTION_EMITTED", "ANSWER_RECEIVED"
    ]
