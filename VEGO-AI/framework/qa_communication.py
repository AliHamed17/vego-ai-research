"""Append-only, privacy-safe live Q&A communication evidence.

This module observes the existing orchestration boundary. It stores hashes and
lengths for question/answer text by default, never raw content. Projection and
validation are deterministic and intentionally separate from policy decisions.
"""

from __future__ import annotations

import hashlib
import json
from collections import defaultdict
from pathlib import Path
from typing import Any

import jsonschema

SCHEMA_VERSION = "qa-communication-event-v1"
EVENT_TYPES = frozenset({"QUESTION_EMITTED", "ANSWER_RECEIVED", "EPISODE_CONTINUED", "EPISODE_TERMINATED"})
TERMINATION_REASONS = frozenset({"CONVERGED", "TERMINATED_MAX_ROUNDS", "INCOMPLETE_TECHNICAL"})
_SCHEMA_PATH = Path(__file__).resolve().parents[2] / "schemas" / "qa-communication-event-v1.schema.json"
_SCHEMA = json.loads(_SCHEMA_PATH.read_text(encoding="utf-8"))


class QACommunicationValidationError(ValueError):
    """Raised when an event stream cannot be safely reconstructed."""


def _ref(value: str | None) -> dict[str, Any] | None:
    if value is None:
        return None
    data = value.encode("utf-8")
    return {"sha256": hashlib.sha256(data).hexdigest(), "length": len(value)}


def _event_id(event: dict[str, Any]) -> str:
    stable = {key: value for key, value in event.items() if key not in {"event_id", "timestamp"}}
    payload = json.dumps(stable, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


class QACommunicationRecorder:
    """Write deterministic append-only events to a local JSONL file."""

    def __init__(self, path: Path | None = None, *, run_id: str, source_artifact: str | None = None,
                 source_sha256: str | None = None) -> None:
        self.path = path
        self.run_id = run_id
        self.source_artifact = source_artifact
        self.source_sha256 = source_sha256
        self.events: list[dict[str, Any]] = []
        self._active_episodes: set[str] = set()
        if path and path.exists():
            raise QACommunicationValidationError("event log already exists; append-only runs require a new path")

    def emit(self, *, event_type: str, episode_id: str, question_id: str | None = None,
             source_agent: str | None = None, source_stage: str | None = None,
             source_skill: str | None = None, target_agent: str | None = None,
             scope: str | None = None, case_id: str | None = None,
             guideline_id: str | None = None, pattern_id: str | None = None,
             question_text: str | None = None, answer_text: str | None = None,
             answer_confidence: str | None = None, answer_evidence: str | None = None,
             answer_source_tier: str | None = None, round_index: int | None = None,
             follow_up_to_event_id: str | None = None, termination_reason: str | None = None,
             converged: bool | None = None) -> dict[str, Any]:
        if event_type not in EVENT_TYPES:
            raise QACommunicationValidationError(f"unsupported event_type: {event_type}")
        if event_type == "EPISODE_TERMINATED":
            termination_reason = (termination_reason or "").upper()
            if termination_reason not in TERMINATION_REASONS:
                raise QACommunicationValidationError("termination_reason must be a permitted scientific state")
        elif termination_reason is not None or converged is not None:
            raise QACommunicationValidationError("non-termination events cannot carry termination fields")
        event: dict[str, Any] = {
            "schema_version": SCHEMA_VERSION,
            "run_id": self.run_id,
            "event_id": "0" * 64,
            "episode_id": episode_id,
            "event_type": event_type,
            "sequence": len(self.events) + 1,
            "timestamp": None,
            "question_id": question_id,
            "source_agent": source_agent,
            "source_stage": source_stage,
            "source_skill": source_skill,
            "target_agent": target_agent,
            "scope": scope,
            "case_id": case_id,
            "guideline_id": guideline_id,
            "pattern_id": pattern_id,
            "question_text_ref": _ref(question_text),
            "answer_text_ref": _ref(answer_text),
            "answer_confidence": answer_confidence if answer_confidence is not None else "UNKNOWN",
            "answer_evidence_ref": _ref(answer_evidence),
            "answer_source_tier": answer_source_tier,
            "round_index": round_index,
            "follow_up_to_event_id": follow_up_to_event_id,
            "termination_reason": termination_reason,
            "converged": converged,
            "provenance": {"source_artifact": self.source_artifact, "source_sha256": self.source_sha256},
        }
        event["event_id"] = _event_id(event)
        validate_event(event)
        self.events.append(event)
        if event_type in {"QUESTION_EMITTED", "EPISODE_CONTINUED"}:
            self._active_episodes.add(episode_id)
        elif event_type == "EPISODE_TERMINATED":
            self._active_episodes.discard(episode_id)
        if self.path:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            with self.path.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(event, sort_keys=True, ensure_ascii=False) + "\n")
        return event

    def emit_question(self, **kwargs: Any) -> dict[str, Any]:
        return self.emit(event_type="QUESTION_EMITTED", **kwargs)

    def emit_answer(self, *, question: dict[str, Any], answer_text: str | None = None,
                    answer_confidence: str | None = None, answer_evidence: str | None = None,
                    source_tier: str | None = None, **kwargs: Any) -> dict[str, Any]:
        return self.emit(
            event_type="ANSWER_RECEIVED", episode_id=question["episode_id"],
            question_id=question.get("question_id"), source_agent=question.get("source_agent"),
            source_stage=question.get("source_stage"), source_skill=question.get("source_skill"),
            target_agent=question.get("target_agent"), scope=question.get("scope"),
            case_id=question.get("case_id"), guideline_id=question.get("guideline_id"),
            pattern_id=question.get("pattern_id"), round_index=question.get("round_index"),
            question_text=None, answer_text=answer_text, answer_confidence=answer_confidence,
            answer_evidence=answer_evidence, answer_source_tier=source_tier, **kwargs,
        )

    def emit_termination(self, **kwargs: Any) -> dict[str, Any]:
        return self.emit(event_type="EPISODE_TERMINATED", **kwargs)

    def observe_exchange(
        self, *, questions: list[dict[str, Any]], answers: list[dict[str, Any]],
        source_agent: str, source_stage: str, source_skill: str,
        target_agent: str, scope: str, episode_id: str, round_index: int,
    ) -> None:
        """Observe one existing route exchange without invoking or changing it."""
        emitted: dict[str, dict[str, Any]] = {}
        for question in questions:
            question_id = question.get("question_id") or question.get("id")
            if not question_id:
                raise QACommunicationValidationError("question is missing question_id")
            emitted[question_id] = self.emit_question(
                question_id=question_id, episode_id=episode_id,
                source_agent=source_agent, source_stage=source_stage,
                source_skill=source_skill, target_agent=target_agent, scope=scope,
                case_id=question.get("case_id"), guideline_id=question.get("guideline_id"),
                pattern_id=question.get("pattern_id"), question_text=question.get("question"),
                round_index=round_index,
            )
        for answer in answers:
            question_id = answer.get("question_id")
            question = emitted.get(question_id)
            if question is None:
                raise QACommunicationValidationError("answer references unknown question_id")
            self.emit_answer(
                question=question, answer_text=answer.get("answer"),
                answer_confidence=answer.get("confidence"),
                answer_evidence=answer.get("evidence") or answer.get("supporting_evidence"),
                source_tier=answer.get("source_tier"),
            )

    def close_open_episodes(self, *, termination_reason: str = "INCOMPLETE_TECHNICAL",
                            converged: bool | None = None) -> None:
        """Close observed episodes without changing any scientific output."""
        for episode_id in sorted(self._active_episodes):
            self.emit_termination(
                episode_id=episode_id, question_id=None, round_index=None,
                termination_reason=termination_reason, converged=converged,
            )


def validate_event(event: dict[str, Any]) -> None:
    try:
        jsonschema.validate(event, _SCHEMA)
    except jsonschema.ValidationError as exc:
        raise QACommunicationValidationError(exc.message) from exc
    if event["event_type"] == "EPISODE_TERMINATED":
        reason = event["termination_reason"]
        if reason not in TERMINATION_REASONS:
            raise QACommunicationValidationError("invalid termination_reason")
        expected = {"CONVERGED": True, "TERMINATED_MAX_ROUNDS": False,
                    "INCOMPLETE_TECHNICAL": None}[reason]
        if event["converged"] is not expected:
            raise QACommunicationValidationError("termination_reason/converged invariant failed")
    elif event["termination_reason"] is not None or event["converged"] is not None:
        raise QACommunicationValidationError("termination fields are only valid on termination events")


def validate_event_stream(events: list[dict[str, Any]]) -> None:
    seen: set[str] = set()
    expected_sequence = 1
    for event in events:
        validate_event(event)
        if event["event_id"] in seen:
            raise QACommunicationValidationError("duplicate event_id")
        if event["sequence"] != expected_sequence:
            raise QACommunicationValidationError("event sequence is not append-only")
        if event["event_id"] != _event_id(event):
            raise QACommunicationValidationError("event_id does not match canonical event")
        seen.add(event["event_id"])
        expected_sequence += 1
    question_events = [event for event in events if event["event_type"] == "QUESTION_EMITTED"]
    questions = {event["question_id"] for event in question_events}
    if len(questions) != len(question_events):
        raise QACommunicationValidationError("duplicate question_id in run")
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for event in events:
        grouped[event["episode_id"]].append(event)
    for event in events:
        if event["event_type"] == "ANSWER_RECEIVED" and event["question_id"] not in questions:
            raise QACommunicationValidationError("answer references unknown question_id")
    for episode_id, rows in grouped.items():
        terminations = [row for row in rows if row["event_type"] == "EPISODE_TERMINATED"]
        if len(terminations) > 1:
            raise QACommunicationValidationError(f"episode {episode_id} has multiple terminations")
        if terminations and rows[-1]["event_type"] != "EPISODE_TERMINATED":
            raise QACommunicationValidationError(f"episode {episode_id} has events after termination")
        answer_ids = [row["question_id"] for row in rows if row["event_type"] == "ANSWER_RECEIVED"]
        if len(answer_ids) != len(set(answer_ids)):
            raise QACommunicationValidationError(f"episode {episode_id} has duplicate answers")
        by_id = {row["event_id"]: row for row in rows}
        episode_questions = {row["question_id"] for row in rows if row["event_type"] == "QUESTION_EMITTED"}
        if terminations and terminations[0]["termination_reason"] in {"CONVERGED", "TERMINATED_MAX_ROUNDS"}:
            if episode_questions - set(answer_ids):
                raise QACommunicationValidationError(f"scientific episode {episode_id} has missing answers")
        for row in rows:
            pointer = row["follow_up_to_event_id"]
            if pointer:
                prior = by_id.get(pointer)
                if prior is None or prior["event_type"] != "QUESTION_EMITTED" or prior["sequence"] >= row["sequence"]:
                    raise QACommunicationValidationError("invalid follow-up pointer")


def build_episode_projection(events: list[dict[str, Any]]) -> list[dict[str, Any]]:
    validate_event_stream(events)
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for event in events:
        grouped[event["episode_id"]].append(event)
    projections: list[dict[str, Any]] = []
    for episode_id in sorted(grouped):
        rows = grouped[episode_id]
        questions = [row for row in rows if row["event_type"] == "QUESTION_EMITTED"]
        answers = [row for row in rows if row["event_type"] == "ANSWER_RECEIVED"]
        continued = [row for row in rows if row["event_type"] == "EPISODE_CONTINUED"]
        terminated = [row for row in rows if row["event_type"] == "EPISODE_TERMINATED"]
        projections.append({
            "episode_id": episode_id,
            "run_id": rows[0]["run_id"],
            "question_count": len(questions),
            "answer_count": len(answers),
            "round_count": max((row["round_index"] or 0 for row in rows), default=0),
            "follow_up_present": any(row["follow_up_to_event_id"] for row in rows),
            "continued": bool(continued),
            "converged": any(row["converged"] is True for row in terminated),
            "termination_reason": terminated[-1]["termination_reason"] if terminated else None,
            "scientific_complete": bool(terminated and terminated[-1]["termination_reason"] in {"CONVERGED", "TERMINATED_MAX_ROUNDS"}),
            "exclusion_reason": None if terminated and terminated[-1]["termination_reason"] in {"CONVERGED", "TERMINATED_MAX_ROUNDS"} else (terminated[-1]["termination_reason"] if terminated else "UNTERMINATED"),
            "source_target_pairs": sorted({
                (row["source_agent"], row["target_agent"])
                for row in rows if row["source_agent"] or row["target_agent"]
            }),
            "answers": answers,
        })
    return projections


def load_event_stream(path: Path) -> list[dict[str, Any]]:
    events = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    if not all(isinstance(event, dict) for event in events):
        raise QACommunicationValidationError("event stream must contain JSON objects")
    validate_event_stream(events)
    return events
