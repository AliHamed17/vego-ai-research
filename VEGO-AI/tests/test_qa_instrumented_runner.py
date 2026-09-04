from __future__ import annotations

import asyncio

from qa_communication import QACommunicationRecorder
from qa_instrumented_runner import (
    _ROUTE_CONTEXT,
    DeterministicFixtureClient,
    InstrumentedLLMClientProxy,
    run_parity_fixture,
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
            token = _ROUTE_CONTEXT.set({"source_agent": source, "source_stage": "concurrent",
                                        "source_skill": "fixture", "target_agent": target, "scope": scope})
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
