from __future__ import annotations

import asyncio
import json
import os
import subprocess
import sys

from qa_communication import QACommunicationRecorder, QACommunicationValidationError
from qa_instrumented_runner import (
    _ROUTE_CONTEXT,
    DeterministicFixtureClient,
    InstrumentedLLMClientProxy,
    run_parity_fixture,
    stable_episode_id,
)


def test_protected_orchestrator_fixture_preserves_prompt_and_scientific_state() -> None:
    report = run_parity_fixture()
    assert report["prompt_label_parity"] is True
    assert report["scientific_state_parity"] is True
    assert report["on"]["events"]


def test_all_six_protected_routes_are_observed_without_raw_text() -> None:
    report = run_parity_fixture()
    pairs = {(event["source_agent"], event["target_agent"]) for event in report["on"]["events"]
             if event["source_agent"] and event["target_agent"]}
    assert pairs == {
        ("agent2", "agent1"), ("agent2", "agent2"), ("agent3", "agent1"),
        ("agent3", "agent2"), ("agent4", "agent1"), ("agent4", "agent2"),
    }
    serialized = str(report["on"]["events"])
    assert "Fixture answer." not in serialized
    assert "Fixture domain description." not in serialized


def test_concurrent_proxy_tasks_keep_route_context_separate(tmp_path) -> None:
    async def scenario() -> list[dict]:
        recorder = QACommunicationRecorder(tmp_path / "events.jsonl", run_id="concurrent")

        async def one(source: str, target: str, scope: str, qid: str) -> None:
            proxy = InstrumentedLLMClientProxy(DeterministicFixtureClient(), recorder)
            token = _ROUTE_CONTEXT.set({"run_id": "concurrent", "setting_id": "s",
                                        "source_agent": source, "source_stage": "concurrent",
                                        "source_skill": "fixture", "target_agent": target,
                                        "scope": scope, "case_id": qid,
                                        "round_index": 1, "question_texts": [f"actual {qid}"]})
            try:
                await proxy.call({"question_id": qid},
                                 label="agent1/answer_language_questions" if target == "agent1"
                                 else "agent2/answer_domain_questions")
            finally:
                _ROUTE_CONTEXT.reset(token)

        await asyncio.gather(one("agent3", "agent1", "language", "Q_lang_101"),
                             one("agent4", "agent2", "domain", "Q_dom_101"))
        return recorder.events

    events = asyncio.run(scenario())
    assert {(event["source_agent"], event["target_agent"]) for event in events
            if event["event_type"] == "QUESTION_EMITTED"} == {("agent3", "agent1"), ("agent4", "agent2")}


def test_concurrent_cases_and_rounds_keep_two_stable_episodes() -> None:
    async def scenario() -> list[dict]:
        recorder = QACommunicationRecorder(run_id="episodes")

        async def one(case_id: str, round_index: int) -> None:
            proxy = InstrumentedLLMClientProxy(DeterministicFixtureClient(), recorder,
                                                run_id="episodes", setting_id="s")
            context = {"run_id": "episodes", "setting_id": "s", "source_agent": "agent3",
                       "source_stage": "case_inspection", "source_skill": "resolve",
                       "target_agent": "agent1", "scope": "language", "case_id": case_id,
                       "round_index": round_index, "question_texts": [f"question {case_id} r{round_index}"]}
            token = _ROUTE_CONTEXT.set(context)
            try:
                await proxy.call({"question_id": f"Q_lang_{round_index:03d}"},
                                 label="agent1/answer_language_questions")
            finally:
                _ROUTE_CONTEXT.reset(token)

        await asyncio.gather(*(one(case, rnd) for case in ("case-a", "case-b") for rnd in (1, 2)))
        return recorder.events

    events = asyncio.run(scenario())
    questions = [e for e in events if e["event_type"] == "QUESTION_EMITTED"]
    assert len(questions) == 4
    by_case = {}
    for event in questions:
        by_case.setdefault(event["case_id"], set()).add(event["episode_id"])
    assert set(by_case) == {"case-a", "case-b"}
    assert all(len(episodes) == 1 for episodes in by_case.values())
    assert len({event["episode_id"] for event in questions}) == 2


def test_episode_event_ids_repeat_across_processes() -> None:
    code = "from qa_instrumented_runner import run_parity_fixture; import json; print(json.dumps([e['event_id'] for e in run_parity_fixture()['on']['events']]))"
    env = {**os.environ, "PYTHONPATH": str(__file__).split("VEGO-AI")[0] + "VEGO-AI/framework"}
    first = subprocess.check_output([sys.executable, "-c", code], env=env, text=True)
    second = subprocess.check_output([sys.executable, "-c", code], env=env, text=True)
    assert json.loads(first.strip().splitlines()[-1]) == json.loads(second.strip().splitlines()[-1])


def test_stable_episode_identity_distinguishes_cases_and_preserves_rounds() -> None:
    base = {"run_id": "r", "setting_id": "s", "source_agent": "agent3",
            "source_stage": "case_inspection", "source_skill": "resolve",
            "target_agent": "agent1", "scope": "language", "case_id": "case-a"}
    assert stable_episode_id({**base, "round_index": 1}) == stable_episode_id({**base, "round_index": 2})
    assert stable_episode_id(base) != stable_episode_id({**base, "case_id": "case-b"})


def test_proxy_uses_context_round_and_rejects_missing_text() -> None:
    async def scenario() -> None:
        recorder = QACommunicationRecorder(run_id="rounds")
        proxy = InstrumentedLLMClientProxy(DeterministicFixtureClient(), recorder)
        token = _ROUTE_CONTEXT.set({"run_id": "rounds", "setting_id": "s", "source_agent": "agent3",
                                    "source_stage": "case_inspection", "source_skill": "resolve",
                                    "target_agent": "agent1", "scope": "language", "case_id": "case-a",
                                    "round_index": "2", "question_texts": ["actual text"]})
        try:
            await proxy.call({"question_id": "Q_lang_001"}, label="agent1/answer_language_questions")
        finally:
            _ROUTE_CONTEXT.reset(token)
        assert recorder.events[0]["round_index"] == 2
        bad = InstrumentedLLMClientProxy(DeterministicFixtureClient(), QACommunicationRecorder(run_id="bad"))
        try:
            await bad.call({"question_id": "Q_lang_002"}, label="agent1/answer_language_questions")
        except QACommunicationValidationError:
            return
        raise AssertionError("missing producer text was silently accepted")

    asyncio.run(scenario())
