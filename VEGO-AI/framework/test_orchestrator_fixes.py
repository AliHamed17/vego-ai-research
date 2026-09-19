"""No-API regression tests for the six clean-run fixes.

Every LLM call is replaced by a scripted fake; no network, no OPENAI_API_KEY,
no cost. Run: py -3.13 test_orchestrator_fixes.py
"""
from __future__ import annotations

import asyncio
import sys
import types

import orchestrator as O
import qa_registry as QR
import agent4_variability_explorer as a4


class FakeClient:
    """Returns queued responses by label; records every call."""
    def __init__(self, script):
        self.script = script          # label -> list of responses (popped in order)
        self.calls = []               # (label, max_tokens)

    async def call(self, prompt, *, label="", max_tokens=16384):
        self.calls.append((label, max_tokens))
        q = self.script.get(label)
        if isinstance(q, list):
            return q.pop(0) if q else {}
        return q if q is not None else {}


class FakeState:
    def __init__(self):
        self.language_template = {"language_name": "UML", "agent1_capabilities": []}
        self.reference_guidelines = {"_domain_description": "d", "domain_identifier": "pw",
                                     "reference_guidelines": []}
        self.lang_qa_history = []
        self.dom_qa_history = []


def run(coro):
    return asyncio.run(coro)


def test_reroute_not_dropped():
    """#2: a scope-rejected domain question is rerouted to Agent 1, not dropped."""
    client = FakeClient({
        "agent2/answer_domain_questions": [
            {"questions_answers": [], "scope_errors": [
                {"question_id": "Q_dom_001", "reason": "language-scoped; route to Agent 1"}]},
        ],
        "agent1/answer_language_questions": [
            {"questions_answers": [{"question_id": "Q_lang_001", "answer": "yes",
                                    "confidence": "High"}]},
        ],
    })
    reg = QR.QARegistry()
    answers = run(O._answer_dom_questions(
        [{"question": "is X a class?"}], FakeState(), reg, client))
    assert len(answers) == 1, f"rerouted answer lost: {answers}"
    assert answers[0]["question_id"] == "Q_lang_001"
    labels = [c[0] for c in client.calls]
    assert labels == ["agent2/answer_domain_questions", "agent1/answer_language_questions"], labels
    return "reroute delivers the rejected question to Agent 1 (was: silently dropped)"


def test_reroute_no_infinite_loop():
    """#2: if BOTH agents reject, it stops after one reroute — no A->B->A->... loop."""
    client = FakeClient({
        "agent2/answer_domain_questions": [
            {"questions_answers": [], "scope_errors": [{"question_id": "Q_dom_001", "reason": "x"}]}],
        "agent1/answer_language_questions": [
            {"questions_answers": [], "scope_errors": [{"question_id": "Q_lang_001", "reason": "x"}]}],
    })
    answers = run(O._answer_dom_questions([{"question": "ambiguous"}], FakeState(),
                                          QR.QARegistry(), client))
    assert answers == [], answers
    assert len(client.calls) == 2, f"expected exactly 2 calls, got {client.calls}"
    return "double-rejection terminates after one reroute (no infinite loop)"


def test_registry_reseed():
    """#5: on resume the counter advances past ids already in history."""
    reg = QR.QARegistry()
    reg.dom_qa = [{"question_id": "Q_dom_003", "answer": "a"}]
    reg.lang_qa = [{"question_id": "Q_lang_007", "answer": "b"}]
    reg.seed_counters_from_history()
    assert run(reg.next_id("dom")) == "Q_dom_004", "dom counter did not resume past 003"
    assert run(reg.next_id("lang")) == "Q_lang_008", "lang counter did not resume past 007"
    fresh = QR.QARegistry()
    fresh.seed_counters_from_history()
    assert run(fresh.next_id("dom")) == "Q_dom_001", "empty history should start at 001"
    return "resumed counter never re-issues an id from a prior run (was: reset to 001)"


def test_phase4_compaction_shrinks_and_keeps_all_cases():
    """#1: compaction cuts tokens hard yet every case_id stays visible."""
    cvs = [{"case_id": f"c{i}", "coverage_summary": {"satisfied": 5},
            "existing_mapping": [{"guideline_id": "G1", "compliance_status": "Satisfied",
                                  "evidence": "long prose " * 200, "notes": "x" * 500}]}
           for i in range(10)]
    ufs = [{"case_id": f"c{i}", "uncovered_fragments": [
            {"label": "Alternative", "severity": "N/A", "fragment": "f" * 300,
             "reason": "r" * 800}]} for i in range(10)]
    rg = {"domain_identifier": "pw", "reference_guidelines": [
          {"id": "G1", "guideline_name": "n", "related_template_id": "T1",
           "description": "d" * 400, "citation": "c" * 400} for _ in range(46)]}
    full = a4.identify_deviation_patterns_prompt(cvs, ufs, rg, "pw", 1)
    slim = a4.identify_deviation_patterns_prompt(
        [O._compact_compliance_vector(c) for c in cvs],
        [O._compact_uncovered(u) for u in ufs],
        O._compact_guidelines(rg), "pw", 1)
    full_len = len(full["system"]) + len(full["user"])
    slim_len = len(slim["system"]) + len(slim["user"])
    assert slim_len < full_len * 0.6, f"compaction too weak: {slim_len}/{full_len}"
    for i in range(10):
        assert f"c{i}" in slim["system"], f"case c{i} dropped by compaction"
    return f"phase-4 payload {full_len}->{slim_len} chars, all 10 cases retained"


def test_phase4_output_capped():
    """#1: the phase-4 identify call requests a bounded output, not the 16384 default."""
    assert O.PHASE4_MAX_OUTPUT_TOKENS < 16384
    return f"phase-4 output capped at {O.PHASE4_MAX_OUTPUT_TOKENS} tokens"


def main():
    tests = [test_reroute_not_dropped, test_reroute_no_infinite_loop,
             test_registry_reseed, test_phase4_compaction_shrinks_and_keeps_all_cases,
             test_phase4_output_capped]
    ok = 0
    for t in tests:
        try:
            msg = t()
            print(f"  PASS  {t.__name__}: {msg}")
            ok += 1
        except AssertionError as e:
            print(f"  FAIL  {t.__name__}: {e}")
        except Exception as e:
            print(f"  ERROR {t.__name__}: {type(e).__name__}: {e}")
    print(f"\n{ok}/{len(tests)} passed")
    return 0 if ok == len(tests) else 1


if __name__ == "__main__":
    raise SystemExit(main())
