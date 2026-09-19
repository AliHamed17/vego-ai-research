"""End-to-end integrity of the agent-to-agent Q&A loop, driven through the real
orchestrator with a scripted offline client. Each test asserts one property that a
live run depends on, and fails if the corresponding fix is removed."""
from __future__ import annotations

import asyncio
import json
import re
import sys
import tempfile
from pathlib import Path

import pytest

FRAMEWORK = Path(__file__).resolve().parents[1] / "framework"
sys.path.insert(0, str(FRAMEWORK))

import orchestrator as O  # noqa: E402
import qa_registry as QR  # noqa: E402
from qa_instrumented_runner import asked_question_ids  # noqa: E402

REAL_ID_RE = re.compile(r'(?<!question_)"id"\s*:\s*"(Q_(?:lang|dom)_\d{3})"')


def flatten(prompt):
    if isinstance(prompt, dict):
        return "\n".join(str(v) for v in prompt.values())
    return str(prompt)


class ScriptClient:
    """Offline client that raises questions on cue and answers on instruction."""

    def __init__(self, *, lang_q=2, dom_q=1, converge_round=2, scope_errors=None,
                 drop_answers=0, omit_fields=(), never_converge=False):
        self.lang_q, self.dom_q = lang_q, dom_q
        self.converge_round = converge_round
        self.scope_errors = scope_errors or {}
        self.drop_answers = drop_answers
        self.omit_fields = omit_fields
        self.never_converge = never_converge
        self.calls: list[str] = []
        self.dispatched: list[dict] = []

    def _round(self, label):
        m = re.search(r"(?:round|_r)(\d+)", label)
        return int(m.group(1)) if m else 1

    def _raise(self, label):
        emit = True if self.never_converge else self._round(label) < self.converge_round
        if not emit:
            return [], []
        return ([{"question": f"LANG|{label}|{i}"} for i in range(self.lang_q)],
                [{"question": f"DOM|{label}|{i}"} for i in range(self.dom_q)])

    def _answers(self, prompt, scope):
        ids = list(dict.fromkeys(REAL_ID_RE.findall(flatten(prompt))))
        self.dispatched.append({"scope": scope, "ids": ids})
        bad = [i for i in ids if i in self.scope_errors]
        good = [i for i in ids if i not in self.scope_errors]
        if self.drop_answers:
            good = good[: max(0, len(good) - self.drop_answers)]
        answers = []
        for qid in good:
            entry = {"question_id": qid, "answer": f"A::{qid}",
                     "evidence": "verbatim", "confidence": "High"}
            for field in self.omit_fields:
                entry.pop(field, None)
            answers.append(entry)
        out = {"questions_answers": answers}
        if bad:
            out["scope_errors"] = [{"question_id": i, "reason": "wrong recipient"} for i in bad]
        return out

    async def call(self, prompt, *, label="", max_tokens=None):
        self.calls.append(label)
        if label == "agent1/build_language_template":
            return {"language_name": "ScriptUML", "guidelines": [], "agent1_capabilities": ["x"]}
        if label.startswith("agent2/guidelines_round") or label.startswith("agent2/guidelines_feedback"):
            ql, qd = self._raise(label)
            return {"domain_identifier": "scripted", "reference_guidelines": [],
                    "questions_to_language_advisor": ql, "questions_to_domain_advisor": qd}
        if label == "agent1/answer_language_questions":
            return self._answers(prompt, "lang")
        if label == "agent2/answer_domain_questions":
            return self._answers(prompt, "dom")
        if "/map" in label:
            return {"existing_mapping": [], "coverage_summary": {
                "satisfied": 0, "partially_satisfied": 0, "not_satisfied": 0}}
        if "/resolve_r" in label or "/audit_r" in label:
            ql, qd = self._raise(label)
            key = "potential_found" if "/resolve_r" in label else "uncovered_fragments"
            return {key: [], "questions_to_language_advisor": ql,
                    "questions_to_domain_advisor": qd}
        if label == "agent4/identify_patterns":
            return {"deviation_patterns": []}
        if label.startswith("agent4/classify_r"):
            ql, qd = self._raise(label)
            return {"variability_classifications": [],
                    "questions_to_language_advisor": ql, "questions_to_domain_advisor": qd}
        return {}


def run_pipeline(client, cases=("c1",)):
    """Drive the real orchestrator end to end against a temporary workspace."""
    tmp = Path(tempfile.mkdtemp())
    inputs = tmp / "in"
    inputs.mkdir()
    for c in cases:
        (inputs / f"{c}.txt").write_text(f"model {c}", encoding="utf-8")
    cfg = {"language_name": "ScriptUML", "domain_description": "d",
           "domain_identifier": "scripted", "case_models_dir": str(inputs),
           "output_dir": str(tmp / "out"), "min_recurrence_threshold": 1}
    state = O.PipelineState.load_or_new(tmp / "state.json")
    registry = QR.QARegistry(setting_id="s1")

    async def go():
        await O.phase1_build_language_template(cfg, state, client, tmp / "state.json")
        await O.phase2_build_reference_guidelines(cfg, state, registry, client, tmp / "state.json")

    asyncio.run(go())
    return state, registry, client


def test_every_raised_question_is_allocated_an_id():
    _, registry, client = run_pipeline(ScriptClient(lang_q=2, dom_q=1))
    dispatched = [i for d in client.dispatched for i in d["ids"]]
    assert dispatched, "no questions were dispatched at all"
    assert len(dispatched) == len(set(dispatched)), "duplicate ids within a single run"


def test_language_and_domain_scopes_are_not_crossed():
    _, _, client = run_pipeline(ScriptClient(lang_q=2, dom_q=2))
    for d in client.dispatched:
        prefix = "Q_lang_" if d["scope"] == "lang" else "Q_dom_"
        assert all(i.startswith(prefix) for i in d["ids"]), f"scope crossed: {d}"


def test_every_answer_joins_back_to_its_question_text():
    state, _, _ = run_pipeline(ScriptClient())
    records = list(state.lang_qa_history) + list(state.dom_qa_history)
    assert records, "no Q&A was persisted"
    for r in records:
        assert r.get("question"), f"answer persisted with no question text: {r}"
        assert r["answer"].endswith(r["question_id"])


def test_persisted_answers_carry_their_provenance():
    state, _, _ = run_pipeline(ScriptClient())
    records = list(state.lang_qa_history) + list(state.dom_qa_history)
    for r in records:
        assert r.get("asked_by"), f"no asking agent recorded: {r}"
        assert r.get("round_index") is not None, f"no round recorded: {r}"
        assert r.get("scope") in {"lang", "dom"}, f"no scope recorded: {r}"


def test_persisted_answers_carry_the_setting_so_ids_cannot_be_merged_across_settings():
    state, _, _ = run_pipeline(ScriptClient())
    records = list(state.lang_qa_history) + list(state.dom_qa_history)
    assert records
    assert all(r.get("setting_id") == "s1" for r in records)


def test_unanswered_questions_are_reported(caplog):
    import logging
    with caplog.at_level(logging.WARNING, logger=O.logger.name):
        run_pipeline(ScriptClient(lang_q=3, dom_q=0, drop_answers=2))
    assert "received no answer" in caplog.text


def test_malformed_answers_are_reported(caplog):
    import logging
    with caplog.at_level(logging.WARNING, logger=O.logger.name):
        run_pipeline(ScriptClient(lang_q=2, dom_q=0, omit_fields=("confidence", "evidence")))
    assert "malformed answer" in caplog.text


def test_wellformed_answers_raise_no_warning(caplog):
    import logging
    with caplog.at_level(logging.WARNING, logger=O.logger.name):
        run_pipeline(ScriptClient(lang_q=1, dom_q=1))
    assert "malformed answer" not in caplog.text
    assert "received no answer" not in caplog.text


def test_a_scope_rejected_question_is_rerouted_not_dropped():
    client = ScriptClient(lang_q=1, dom_q=0)
    first = ScriptClient(lang_q=1, dom_q=0)
    _, _, probe = run_pipeline(first)
    rejected = probe.dispatched[0]["ids"][0]
    client = ScriptClient(lang_q=1, dom_q=0, scope_errors={rejected: 1})
    _, _, client = run_pipeline(client)
    assert "agent2/answer_domain_questions" in client.calls, "rejected question was never rerouted"


def test_reroute_happens_at_most_once():
    probe = ScriptClient(lang_q=1, dom_q=0)
    _, _, p = run_pipeline(probe)
    first_id = p.dispatched[0]["ids"][0]
    client = ScriptClient(lang_q=1, dom_q=0, scope_errors={first_id: 1, "Q_dom_001": 1})
    _, _, client = run_pipeline(client)
    lang_calls = client.calls.count("agent1/answer_language_questions")
    dom_calls = client.calls.count("agent2/answer_domain_questions")
    assert lang_calls + dom_calls < 12, "reroute did not terminate"


def test_qa_loop_terminates_at_the_round_cap():
    _, _, client = run_pipeline(ScriptClient(never_converge=True))
    rounds = [c for c in client.calls if c.startswith("agent2/guidelines_round")]
    assert len(rounds) <= O.MAX_QA_ROUNDS, f"loop exceeded the cap: {len(rounds)}"


def test_qa_loop_stops_early_when_no_questions_remain():
    _, _, client = run_pipeline(ScriptClient(converge_round=2))
    rounds = [c for c in client.calls if c.startswith("agent2/guidelines_round")]
    assert len(rounds) < O.MAX_QA_ROUNDS, "converged run still ran to the cap"


def test_resumed_registry_does_not_reissue_ids():
    registry = QR.QARegistry(setting_id="s1")
    registry.lang_qa = [{"question_id": "Q_lang_004", "answer": "a"}]
    registry.seed_counters_from_history()
    nxt = asyncio.run(registry.next_id("lang"))
    assert nxt == "Q_lang_005", f"resumed run re-issued {nxt}"


def test_instrumented_harness_ignores_output_format_example_ids():
    import agent2_domain_advisor as a2
    prompt = a2.answer_domain_question_prompt(
        domain_description="d", reference_guidelines={},
        questions=[{"id": "Q_dom_004", "question": "q"}], domain_identifier="x")
    assert asked_question_ids(prompt) == ["Q_dom_004"]
