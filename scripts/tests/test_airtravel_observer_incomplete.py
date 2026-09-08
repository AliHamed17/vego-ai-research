"""The observer must survive real-provider answer variance.

A provider may return duplicate, unknown or missing question identifiers.
That episode is technically incomplete and is excluded from every
Detector-v1 denominator; it must never abort the whole run.
"""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "VEGO-AI/framework"))


class Recorder:
    def __init__(self):
        self.answers = []
        self.terminations = []

    def emit_question(self, **kwargs):
        return {"question_id": kwargs["question_id"], **kwargs}

    def emit_answer(self, *, question, answer_text, answer_confidence, answer_evidence):
        self.answers.append(
            {
                "question_id": question["question_id"],
                "answer_confidence": answer_confidence,
                "answer_evidence": answer_evidence,
            }
        )

    def emit_termination(self, **kwargs):
        self.terminations.append(kwargs)


class BaseRegistry:
    async def allocate_ids(self, questions, scope):
        return [{"id": f"Q{i}", "question": q} for i, q in enumerate(questions, start=1)]

    async def record_answers(self, answers, scope):
        return None


def _meta():
    return {
        "episode_id": "EP-test",
        "round_index": 1,
        "case_id": "01",
        "source_agent": "agent2",
        "source_stage": "guideline_construction",
        "source_skill": "guidelines",
    }


def _drive(answers):
    import airtravel_local_observer as observer_module

    recorder = Recorder()
    observer = observer_module.Observer(recorder)
    registry = observer.registry(BaseRegistry)()
    meta = _meta()
    observer_module.CURRENT.set(meta)
    observer.expected[meta["episode_id"]] = {"lang": ["a", "b"], "dom": []}

    async def run():
        await registry.allocate_ids(["a", "b"], "lang")
        await registry.record_answers(answers, "lang")

    asyncio.run(run())
    return recorder


def test_matching_answers_do_not_terminate_the_episode():
    recorder = _drive(
        [
            {"question_id": "Q1", "answer": "x", "confidence": "High", "evidence": "e"},
            {"question_id": "Q2", "answer": "y", "confidence": "Low", "evidence": "f"},
        ]
    )
    assert len(recorder.answers) == 2
    assert recorder.terminations == []


@pytest.mark.parametrize(
    "answers",
    [
        pytest.param([{"question_id": "Q1", "answer": "x"}], id="missing"),
        pytest.param(
            [{"question_id": "Q1", "answer": "x"}, {"question_id": "Q1", "answer": "y"}],
            id="duplicate",
        ),
        pytest.param(
            [
                {"question_id": "Q1", "answer": "x"},
                {"question_id": "Q2", "answer": "y"},
                {"question_id": "Q9", "answer": "z"},
            ],
            id="unknown",
        ),
        pytest.param([], id="empty"),
    ],
)
def test_answer_variance_yields_incomplete_technical_without_aborting(answers):
    recorder = _drive(answers)
    assert len(recorder.terminations) == 1
    termination = recorder.terminations[0]
    assert termination["termination_reason"] == "INCOMPLETE_TECHNICAL"
    assert termination["converged"] is None
    for recorded in recorder.answers:
        assert recorded["question_id"] in {"Q1", "Q2"}


def test_terminated_episode_is_never_reopened():
    import airtravel_local_observer as observer_module

    recorder = Recorder()
    observer = observer_module.Observer(recorder)
    registry = observer.registry(BaseRegistry)()
    meta = _meta()
    observer_module.CURRENT.set(meta)
    observer.expected[meta["episode_id"]] = {"lang": ["a"], "dom": []}

    async def run():
        await registry.allocate_ids(["a"], "lang")
        await registry.record_answers([], "lang")
        observer.expected[meta["episode_id"]] = {"lang": ["b"], "dom": []}
        await registry.allocate_ids(["b"], "lang")
        await registry.record_answers([], "lang")

    asyncio.run(run())
    assert len(recorder.terminations) == 1
