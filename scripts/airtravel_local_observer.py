"""Additive local fake runner. Exact corpus execution requires the guarded CLI.

Importing this module does not import protected runtime or a provider SDK.
Fixture entry accepts only declared fixture modes and literal fixture content.
"""

from __future__ import annotations

import asyncio
import contextvars
import hashlib
import importlib
import json
import re
import sys
import types

from airtravel_preflight_contract import ROOT
from study1_call_bound import MAX_QA_ROUNDS, capture_call_inventory, worst_case_calls

CURRENT = contextvars.ContextVar("airtravel_loop_context", default=None)


def digest(value) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, ensure_ascii=False).encode()
    ).hexdigest()


def runtime():
    sys.path.insert(0, str(ROOT / "VEGO-AI/framework"))
    if "orchestrator" not in sys.modules:
        stub = types.ModuleType("llm_client")

        class ForbiddenProvider:
            def __init__(self, *args, **kwargs):
                raise PermissionError("real provider construction forbidden")

        stub.LLMClient = ForbiddenProvider
        original = sys.modules.get("llm_client")
        sys.modules["llm_client"] = stub
        try:
            module = importlib.import_module("orchestrator")
        finally:
            if original is None:
                sys.modules.pop("llm_client", None)
            else:
                sys.modules["llm_client"] = original
    else:
        module = sys.modules["orchestrator"]
    return module


def metadata(label: str, run_id: str, setting: str) -> dict | None:
    match = re.fullmatch(
        r"agent([234])/(?:(.+)/)?(guidelines_round|guidelines_feedback_r|resolve_r|audit_r|classify_r)(\d+)",
        label,
    )
    if not match:
        return None
    agent, case_id, skill, round_n = match.groups()
    round_n = int(round_n)
    if not 1 <= round_n <= MAX_QA_ROUNDS:
        raise ValueError("round outside protected guard")
    skill = re.sub(r"(?:_round|_r)$", "", skill)
    identity = {
        "run_id": run_id,
        "setting_id": setting,
        "case_id": case_id,
        "source_agent": "agent" + agent,
        "source_skill": skill,
    }
    return {
        **identity,
        "episode_id": "EP-" + digest(identity)[:24],
        "round_index": round_n,
        "source_stage": {
            "2": "guideline_construction",
            "3": "case_inspection",
            "4": "variability_classification",
        }[agent],
    }


class FakeClient:
    """Deterministic response schedule; no SDK, credentials or learned model."""

    def __init__(self, mode: str):
        if mode not in {"no_questions", "two_rounds", "max_rounds"}:
            raise ValueError("unsupported fixture mode")
        self.mode = mode

    async def call(self, prompt, *, label):
        await asyncio.sleep(0)
        if label in {"agent1/answer_language_questions", "agent2/answer_domain_questions"}:
            # The protected prompt's dedicated Questions field, not prior history.
            text = prompt["system"]
            marker = "Questions to be Answered: ** "
            if marker not in text:
                marker = "Questions to be Answered:"
            offset = text.find(marker)
            if offset < 0:
                raise ValueError("dedicated question field absent")
            start = text.find("[", offset)
            questions, _ = json.JSONDecoder().raw_decode(text[start:])
            return {
                "questions_answers": [
                    {
                        "question_id": q["id"],
                        "answer": "Local fixture answer.",
                        "confidence": "High",
                        "evidence": "Local fixture evidence.",
                    }
                    for q in questions
                ]
            }
        if label == "agent1/build_language_template":
            return {"language_name": "FixtureUML", "guidelines": [], "agent1_capabilities": []}
        if label.endswith("/map"):
            return {"existing_mapping": [], "coverage_summary": {}}
        if label == "agent4/identify_patterns":
            return {"deviation_patterns": []}
        meta = metadata(label, "fixture", "fixture")
        if meta is None:
            raise ValueError("unknown protected call label")
        question_round = self.mode == "max_rounds" or (
            self.mode == "two_rounds" and meta["round_index"] == 1
        )
        result = {
            "reference_guidelines": [],
            "potential_found": [],
            "uncovered_fragments": [],
            "variability_classifications": [],
            "questions_to_language_advisor": [],
            "questions_to_domain_advisor": [],
        }
        if question_round:
            result["questions_to_language_advisor"] = [
                {"question": "Local language fixture: " + label}
            ]
            if "feedback" not in label:
                result["questions_to_domain_advisor"] = [
                    {"question": "Local domain fixture: " + label}
                ]
        if label.startswith("agent4/classify") and self.mode == "max_rounds":
            result["variability_classifications"] = [
                {
                    "pattern_id": "fixture-pattern",
                    "justification": "Local fixture branch",
                    "flag_for_guidelines_update": True,
                }
            ]
        return result


class Observer:
    def __init__(self, recorder):
        self.recorder = recorder
        self.pending = {}
        self.expected = {}
        self.active = set()
        self.closed = set()
        self.last = {}

    def producer(self, meta, response):
        CURRENT.set(meta)
        if not self.recorder or meta is None:
            return
        episode = meta["episode_id"]
        scopes = ("lang",) if meta["source_skill"] == "guidelines_feedback" else ("lang", "dom")
        expected = {
            scope: response.get(
                "questions_to_" + ("language" if scope == "lang" else "domain") + "_advisor", []
            )
            for scope in scopes
        }
        if any(self.pending.get((episode, s)) for s in scopes):
            raise ValueError("previous round missing answers")
        self.expected[episode] = expected
        if not any(expected.values()) and episode in self.active:
            self.finish(meta, "CONVERGED")

    def finish(self, meta, reason):
        if meta["episode_id"] in self.active and meta["episode_id"] not in self.closed:
            self.closed.add(meta["episode_id"])
            self.recorder.emit_termination(
                episode_id=meta["episode_id"],
                round_index=meta["round_index"],
                termination_reason=reason,
                converged={
                    "CONVERGED": True,
                    "TERMINATED_MAX_ROUNDS": False,
                    "INCOMPLETE_TECHNICAL": None,
                }[reason],
            )
            self.active.remove(meta["episode_id"])

    def registry(self, base):
        observer = self

        class ObservedRegistry(base):
            async def allocate_ids(self, questions, scope):
                assigned = await super().allocate_ids(questions, scope)
                if not observer.recorder:
                    return assigned
                meta = CURRENT.get()
                if meta is None or questions != observer.expected[meta["episode_id"]].get(scope):
                    raise ValueError("producer/question correlation failed")
                key = (meta["episode_id"], scope)
                observer.pending[key] = {}
                observer.active.add(meta["episode_id"])
                for q in assigned:
                    event = observer.recorder.emit_question(
                        episode_id=meta["episode_id"],
                        question_id=q["id"],
                        question_text=q["question"],
                        case_id=meta["case_id"],
                        source_agent=meta["source_agent"],
                        source_stage=meta["source_stage"],
                        source_skill=meta["source_skill"],
                        target_agent="agent1" if scope == "lang" else "agent2",
                        scope=scope,
                        round_index=meta["round_index"],
                    )
                    observer.pending[key][q["id"]] = event
                return assigned

            async def record_answers(self, answers, scope):
                if observer.recorder:
                    meta = CURRENT.get()
                    key = (meta["episode_id"], scope)
                    pending = observer.pending.get(key, {})
                    ids = [a.get("question_id") for a in answers]
                    correspondent = len(ids) == len(set(ids)) and set(ids) == set(pending)
                    for answer in answers:
                        question = pending.get(answer.get("question_id"))
                        if question is None:
                            continue
                        observer.recorder.emit_answer(
                            question=question,
                            answer_text=answer.get("answer"),
                            answer_confidence=answer.get("confidence"),
                            answer_evidence=answer.get("evidence"),
                        )
                    observer.pending[key] = {}
                    observer.expected[meta["episode_id"]][scope] = []
                    if not correspondent:
                        # A provider may answer with duplicate, unknown or
                        # missing identifiers. That episode is technically
                        # incomplete; it is excluded from every Detector-v1
                        # denominator rather than aborting the whole run.
                        observer.finish(meta, "INCOMPLETE_TECHNICAL")
                    elif meta["round_index"] == MAX_QA_ROUNDS and not any(
                        observer.expected[meta["episode_id"]].values()
                    ):
                        observer.finish(meta, "TERMINATED_MAX_ROUNDS")
                await super().record_answers(answers, scope)

        return ObservedRegistry


class Proxy:
    def __init__(self, fake, observer, n, setting, run_id):
        self.fake, self.observer, self.setting, self.run_id = fake, observer, setting, run_id
        self.calls = []
        self.maximum = worst_case_calls(n)

    async def call(self, prompt, *, label):
        if len(self.calls) >= self.maximum:
            raise ValueError("maximum fake-call count exceeded")
        record = {"label": label, "prompt_sha256": digest(prompt)}
        self.calls.append(record)
        result = await self.fake.call(prompt, label=label)
        record["answer_sha256"] = digest(result)
        if label not in {"agent1/answer_language_questions", "agent2/answer_domain_questions"}:
            self.observer.producer(metadata(label, self.run_id, self.setting), result)
        return result


def validate_final_stream(events):
    from qa_communication import validate_event_stream

    validate_event_stream(events)
    episodes = {e["episode_id"] for e in events}
    for episode in episodes:
        if (
            sum(
                e["event_type"] == "EPISODE_TERMINATED" and e["episode_id"] == episode
                for e in events
            )
            != 1
        ):
            raise ValueError("unterminated episode")


class RecordingFake(FakeClient):
    """Direct fake baseline: records inputs/answers without an observer proxy."""

    def __init__(self, mode):
        super().__init__(mode)
        self.calls = []

    async def call(self, prompt, *, label):
        if len(self.calls) >= worst_case_calls(4):
            raise ValueError("individual fake-run maximum exceeded")
        record = {"label": label, "prompt_sha256": digest(prompt), **capture_call_inventory(label)}
        self.calls.append(record)
        result = await super().call(prompt, label=label)
        record["answer_sha256"] = digest(result)
        # Compare the complete deterministic return value as the decision surface;
        # no scientific fields are removed to obtain parity.
        record["decision_sha256"] = digest(result)
        return result


def route_metrics(events):
    from collections import Counter

    pairs = Counter(
        (e["source_agent"], e["target_agent"])
        for e in events
        if e["event_type"] == "QUESTION_EMITTED"
    )
    return {
        "protected_orchestrator_fake_episode_count": len({e["episode_id"] for e in events}),
        "protected_orchestrator_fake_route_pair_count": len(pairs),
        "protected_orchestrator_fake_route_pairs": [
            {"source_agent": s, "target_agent": t} for s, t in sorted(pairs)
        ],
        "protected_orchestrator_fake_route_count": len(pairs),
        "routes": [
            {"source_agent": s, "target_agent": t, "question_count": n}
            for (s, t), n in sorted(pairs.items())
        ],
        "episode_count": len({e["episode_id"] for e in events}),
        "question_count": sum(pairs.values()),
        "answer_count": sum(e["event_type"] == "ANSWER_RECEIVED" for e in events),
    }
