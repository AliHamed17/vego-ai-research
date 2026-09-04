"""Offline execution harness for protected VEGO-AI orchestration paths.

The protected orchestrator is imported and executed unchanged.  A deterministic
fake client is injected at the client boundary; it records prompt/answer hashes
and the observer records only metadata references.  No provider client or
network is reachable from this module.
"""
from __future__ import annotations

import asyncio
import contextvars
import hashlib
import json
import re
import tempfile
from pathlib import Path
from typing import Any

import orchestrator
from qa_communication import QACommunicationRecorder, QACommunicationValidationError
from qa_registry import QARegistry
from state import PipelineState

_ROUTE_CONTEXT: contextvars.ContextVar[dict[str, str] | None] = contextvars.ContextVar(
    "qa_route_context", default=None
)
_CURRENT_PRODUCER: contextvars.ContextVar[str | None] = contextvars.ContextVar(
    "qa_current_producer", default=None
)


def _correlation_token(context: dict[str, Any] | None, label: str, run_id: str,
                       setting_id: str) -> str:
    """Choose a deterministic pending-Q&A key without leaking task identity.

    Explicit route contexts are authoritative.  Synthetic helper fixtures carry
    question text and therefore must not accidentally consume a stale producer
    token left by a previous route in the same asyncio task.
    """
    if context:
        explicit = context.get("correlation_key")
        if explicit:
            return str(explicit)
        if context.get("question_texts"):
            return "helper-" + stable_episode_id(context)
    return (_CURRENT_PRODUCER.get()
            or f"{run_id}|{setting_id}|{label}")


def _sha(value: Any) -> str:
    payload = json.dumps(value, sort_keys=True, ensure_ascii=False, default=str).encode()
    return hashlib.sha256(payload).hexdigest()


def stable_episode_id(context: dict[str, Any]) -> str:
    """Derive an episode ID from frozen scientific context, excluding round."""
    fields = ("run_id", "setting_id", "source_stage", "source_agent", "source_skill",
              "target_agent", "scope", "case_id", "guideline_id", "pattern_id", "episode_key")
    identity = "|".join(str(context.get(field) or "") for field in fields)
    if not any(identity.split("|")):
        raise ValueError("stable episode identity requires declared scientific context")
    return "EP-" + hashlib.sha256(identity.encode()).hexdigest()[:24]


def _producer_metadata(label: str, run_id: str, setting_id: str) -> dict[str, Any]:
    match = re.match(r"agent(?P<agent>[234])/(?:(?P<case>[^/]+)/)?(?P<skill>[^/]+)", label)
    agent = f"agent{match.group('agent')}" if match else "UNKNOWN"
    case_id = match.group("case") if match else None
    skill = match.group("skill") if match else "UNKNOWN"
    stage = {"agent2": "guideline_construction", "agent3": "case_inspection",
             "agent4": "variability_classification"}.get(agent, "UNKNOWN")
    round_match = re.search(r"(?:round|_r)(\d+)", label)
    return {"run_id": run_id, "setting_id": setting_id, "source_agent": agent,
            "source_stage": stage, "source_skill": skill, "case_id": case_id,
            "round_index": int(round_match.group(1)) if round_match else 1}


class DeterministicFixtureClient:
    """Return schema-shaped, non-sensitive responses for every protected phase."""

    def __init__(self) -> None:
        self.phase2_round = 0

    async def call(self, prompt: dict[str, Any], *, label: str) -> dict[str, Any]:
        if label == "agent1/build_language_template":
            return {"language_name": "FixtureUML", "guidelines": [], "agent1_capabilities": ["fixture"]}
        if label.startswith("agent2/guidelines_round"):
            self.phase2_round += 1
            questions = [{"question": "Clarify the fixture guideline boundary."}] if self.phase2_round == 1 else []
            return {"domain_identifier": "fixture", "reference_guidelines": [],
                    "questions_to_language_advisor": questions, "questions_to_domain_advisor": []}
        if label.startswith("agent1/answer_language_questions") or label.startswith("agent2/answer_domain_questions"):
            ids = re.findall(r"Q_(?:lang|dom)_\d{3}", json.dumps(prompt, ensure_ascii=False))
            return {"questions_answers": [{"question_id": qid, "answer": "Fixture answer.",
                                            "confidence": "High", "evidence": "fixture-evidence"}
                                           for qid in dict.fromkeys(ids)]}
        if "/map" in label:
            return {"existing_mapping": [], "coverage_summary": {"satisfied": 0,
                    "partially_satisfied": 0, "not_satisfied": 0}}
        if "/resolve_r" in label:
            return {"potential_found": [], "questions_to_language_advisor": [],
                    "questions_to_domain_advisor": []}
        if "/audit_r" in label:
            return {"uncovered_fragments": [], "questions_to_language_advisor": [],
                    "questions_to_domain_advisor": []}
        if label == "agent4/identify_patterns":
            return {"deviation_patterns": []}
        if label.startswith("agent4/classify_r"):
            return {"variability_classifications": [], "questions_to_language_advisor": [],
                    "questions_to_domain_advisor": []}
        if label.startswith("agent2/guidelines_feedback"):
            return {"reference_guidelines": [], "questions_to_language_advisor": []}
        return {}


class InstrumentedLLMClientProxy:
    """Pass-through proxy that cannot alter prompts, answers, or decisions."""

    def __init__(self, fake: DeterministicFixtureClient, recorder: QACommunicationRecorder | None = None,
                 *, run_id: str = "study1-fixture", setting_id: str = "fixture") -> None:
        self.fake = fake
        self.recorder = recorder
        self.run_id = run_id
        self.setting_id = setting_id
        self.calls: list[dict[str, Any]] = []
        self._pending: dict[str, list[dict[str, Any]]] = {}

    async def call(self, prompt: dict[str, Any], *, label: str) -> dict[str, Any]:
        context = _ROUTE_CONTEXT.get()
        token = _correlation_token(context, label, self.run_id, self.setting_id)
        self.calls.append({"label": label, "prompt_sha256": _sha(prompt),
                           "prompt_length": len(json.dumps(prompt, ensure_ascii=False))})
        result = await self.fake.call(prompt, label=label)
        if self.recorder and (result.get("questions_to_language_advisor") or result.get("questions_to_domain_advisor")):
            pending = []
            producer = _producer_metadata(label, self.run_id, self.setting_id)
            for scope, key, target in (("language", "questions_to_language_advisor", "agent1"),
                                       ("domain", "questions_to_domain_advisor", "agent2")):
                for q in result.get(key, []):
                    pending.append({"question": q.get("question"), "scope": scope, "target_agent": target,
                                    **producer})
            self._pending[token] = pending
            _CURRENT_PRODUCER.set(token)
        self.calls[-1]["answer_sha256"] = _sha(result)
        self.calls[-1]["answer_length"] = len(json.dumps(result, ensure_ascii=False))
        if self.recorder and label in {"agent1/answer_language_questions", "agent2/answer_domain_questions"}:
            all_ids = list(dict.fromkeys(re.findall(r"Q_(?:lang|dom)_\d{3}", json.dumps(prompt, ensure_ascii=False))))
            context = _ROUTE_CONTEXT.get()
            pending = self._pending.pop(token, [])
            if not pending and context and context.get("question_texts"):
                pending = [{**context, "question": text} for text in context["question_texts"]]
            if not pending:
                raise QACommunicationValidationError("Q&A answer cannot be correlated to producer metadata")
            # Prompts may include prior Q&A history.  The producer's pending
            # list identifies the current suffix; never correlate historical IDs.
            ids = all_ids[-len(pending):]
            questions = []
            for index, question_id in enumerate(ids):
                meta = (pending[index] if index < len(pending) else {}) | (context or {})
                if not meta.get("question"):
                    raise QACommunicationValidationError(
                        f"Q&A producer text is unavailable; episode is technical-incomplete "
                        f"(pending={pending!r}, context={context!r}, ids={ids!r})"
                    )
                questions.append({"question_id": question_id, "question": meta["question"],
                                  "case_id": meta.get("case_id"), "round_index": int(meta.get("round_index", 1))})
            answer_by_id = {answer.get("question_id"): answer
                            for answer in result.get("questions_answers", [])}
            if any(question_id not in answer_by_id for question_id in ids):
                raise QACommunicationValidationError(
                    "Q&A answer is missing for a correlated producer question; "
                    "episode is technical-incomplete"
                )
            answers = [answer_by_id[question_id] for question_id in ids
                       if question_id in answer_by_id]
            if questions and answers:
                source = context or {"source_agent": "agent2", "source_stage": "guideline_construction",
                                     "source_skill": "qa_route", "target_agent": questions[0].get("target", "agent1"),
                                     "scope": "language" if "language" in label else "domain"}
                source = {"run_id": self.run_id, "setting_id": self.setting_id, **source}
                episode_id = stable_episode_id(source)
                round_index = int(source.get("round_index") or questions[0].get("round_index") or 1)
                self.recorder.observe_exchange(
                    questions=questions, answers=answers,
                    source_agent=source.get("source_agent", "UNKNOWN"),
                    source_stage=source.get("source_stage", "fixture"),
                    source_skill=source.get("source_skill", "qa_route"),
                    target_agent=source.get("target_agent", "agent1"),
                    scope=source.get("scope", "language"), episode_id=episode_id, round_index=round_index,
                )
        return result


async def run_protected_route_fixtures(recorder: QACommunicationRecorder) -> None:
    """Exercise each protected Q&A helper route without provider access."""
    state = PipelineState(language_template={"language_name": "FixtureUML"},
                          reference_guidelines={"_domain_description": "fixture"})
    registry = QARegistry()
    for index, (source, target, scope) in enumerate(
        (("agent2", "agent1", "language"), ("agent2", "agent2", "domain"),
         ("agent3", "agent1", "language"), ("agent3", "agent2", "domain"),
         ("agent4", "agent1", "language"), ("agent4", "agent2", "domain")), start=1):
        proxy = InstrumentedLLMClientProxy(DeterministicFixtureClient(), recorder,
                                           run_id=recorder.run_id)
        ctx = _ROUTE_CONTEXT.set({"run_id": recorder.run_id, "setting_id": "fixture", "source_agent": source,
                                  "source_stage": "protected_helper_fixture", "source_skill": "qa_route",
                                  "target_agent": target, "scope": scope, "case_id": f"route-{index}",
                                  "round_index": "1", "question_texts": [f"Route fixture {index}"]})
        try:
            questions = [{"question": f"Route fixture {index}"}]
            if target == "agent1":
                await orchestrator._answer_lang_questions(questions, state, registry, proxy)
            else:
                await orchestrator._answer_dom_questions(questions, state, registry, proxy)
        finally:
            _ROUTE_CONTEXT.reset(ctx)
    for episode in sorted({event["episode_id"] for event in recorder.events}):
        recorder.emit_termination(episode_id=episode, termination_reason="CONVERGED", converged=True)


async def run_protected_orchestrator_fixture(*, instrument: bool, root: Path | None = None) -> dict[str, Any]:
    """Run the actual protected ``orchestrator.run`` against local fixture inputs."""
    work = root or Path(tempfile.mkdtemp(prefix="vego-ai-study1-fixture-"))
    work.mkdir(parents=True, exist_ok=True)
    cases = work / "cases"
    cases.mkdir(exist_ok=True)
    (work / "domain.txt").write_text("Fixture domain description.", encoding="utf-8")
    (cases / "01_fixture.txt").write_text("Fixture case model.", encoding="utf-8")
    output = work / "output"
    config = work / "run_config.json"
    config.write_text(json.dumps({"log_level": "WARNING", "settings": [{
        "setting_id": "fixture", "language_name": "FixtureUML",
        "domain_description_file": "domain.txt", "case_models_dir": "cases",
        "output_dir": str(output), "max_concurrent_cases": 2}]}, indent=2), encoding="utf-8")
    recorder = QACommunicationRecorder(work / "qa_events.jsonl", run_id="study1-fixture") if instrument else None
    proxy = InstrumentedLLMClientProxy(DeterministicFixtureClient(), recorder,
                                       run_id="study1-fixture", setting_id="fixture")
    original = orchestrator.LLMClient
    orchestrator.LLMClient = lambda **_: proxy  # type: ignore[assignment]
    try:
        await orchestrator.run(config, only_setting="fixture")
    finally:
        orchestrator.LLMClient = original
    state = json.loads((output / "pipeline_state.json").read_text(encoding="utf-8"))
    if recorder:
        await run_protected_route_fixtures(recorder)
    return {"calls": proxy.calls, "scientific_state": state,
            "events": recorder.events if recorder else [],
            "workdir": str(work)}


def run_parity_fixture() -> dict[str, Any]:
    """Return deterministic off/on parity and protected route evidence."""
    off = asyncio.run(run_protected_orchestrator_fixture(instrument=False))
    on = asyncio.run(run_protected_orchestrator_fixture(instrument=True))
    off_state = {key: value for key, value in off["scientific_state"].items()}
    on_state = {key: value for key, value in on["scientific_state"].items()}
    return {"prompt_label_parity": off["calls"] == on["calls"],
            "scientific_state_parity": off_state == on_state,
            "off": off, "on": on}
