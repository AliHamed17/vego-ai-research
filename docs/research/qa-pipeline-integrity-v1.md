# Q&A pipeline integrity — defects, fixes, and evidence

An adversarial pre-run verification of the agent-to-agent Q&A loop returned
**DEFECTIVE** and found eight defects. This records each one, the fix, and the
evidence that the fix is now guarded by a test that fails without it.

## Why this was needed

The verification's most important finding was not any single defect. It was that
**the existing 134-test suite passed identically on a tree with the Q&A fixes and on a
tree without them.** The suite provided no signal at all, so it could not be used as
the gate for a paid live run.

## The defects and their disposition

| # | severity | defect | status |
|---|---|---|---|
| 1 | BLOCKER | "framework silently reverted" | **not a defect** — a branch switch during the session; the fixes were on another branch |
| 2 | BLOCKER | `scope_errors` ignored: a question the answering agent rejects as out of scope is silently dropped, never re-asked | fixed — `_scope_rejected_questions` reroutes once, loop-guarded |
| 3 | BLOCKER | question ids collide across conditions and are re-issued on resume | fixed — `seed_counters_from_history` on resume; `setting_id` stamped on every record so cross-setting joins cannot merge unrelated Q&A |
| 4 | HIGH | no validation that every allocated question was answered, or that answers carry the expected fields | fixed — `_report_unanswered` and `_report_malformed_answers` |
| 5 | HIGH | the instrumented harness correlated the **wrong** question ids | fixed — `asked_question_ids` |
| 6 | HIGH | consequence of 5: a spec-compliant model aborts the instrumented run | fixed with 5 |
| 7 | MEDIUM | only answer dicts were persisted; the originating question text and provenance were lost, making the join unverifiable from saved state | fixed — `record_answers` joins each answer to its question and stamps asking agent, case, round, scope and setting |
| 8 | MEDIUM | the test suite was blind to every defect above | fixed — see the evidence below |

### Defect 5 in detail

The answer prompts embed literal example ids in their OUTPUT FORMAT blocks —
`Q_lang_001` (`agent1_language_advisor.py:219`), `Q_dom_001` and `Q_dom_002`
(`agent2_domain_advisor.py:482,492`) — and again in prose. The harness regexed every
`Q_(lang|dom)_NNN` token out of the whole prompt and then took the trailing slice
`all_ids[-len(pending):]`, on the assumption that the real ids come last.

They come **first**. The examples come last. So the harness selected the examples every
time: a probe asking `[Q_dom_004]` recorded `[Q_dom_002]`, an id that was never asked.

This was masked offline because the deterministic fixture answers every id it finds,
including the examples. A spec-compliant model answering only what it was asked would
have aborted the run. **An instrumented live run could not have produced usable Q&A
evidence.**

`asked_question_ids` now extracts only ids rendered as a bare `"id"` member, which is
how the questions block renders them and how the OUTPUT FORMAT examples, keyed
`"question_id"`, do not.

## Evidence: every fix is guarded

`scripts/qa_integrity_evidence.py` reverts each fix in an isolated clone and re-runs the
integrity suite. A fix whose removal breaks no test is unguarded.

```
BASELINE: 25 passed, 0 failed

M1-id-correlation        CAUGHT   7 failed   test_correlation_holds_for_both_scopes, ...
M2-unanswered-reporting  CAUGHT   1 failed   test_unanswered_questions_are_reported
M3-malformed-reporting   CAUGHT   1 failed   test_malformed_answers_are_reported
M4-provenance            CAUGHT   1 failed   test_persisted_answers_carry_their_provenance
M5-question-text         CAUGHT   1 failed   test_every_answer_joins_back_to_its_question_text
M6-setting-id            CAUGHT   1 failed   test_persisted_answers_carry_the_setting...
M7-reroute               CAUGHT   1 failed   test_a_scope_rejected_question_is_rerouted_not_dropped
M8-resume-seeding        CAUGHT   1 failed   test_resumed_registry_does_not_reissue_ids

SUMMARY: 8/8 reverted fixes were caught by the suite
```

## What the integrity suite asserts

`VEGO-AI/tests/test_qa_pipeline_integrity.py` drives the **real** orchestrator end to
end against a scripted offline client. It makes no network call.

- every raised question is allocated an id, and ids are unique within a run
- language questions reach Agent 1 and domain questions reach Agent 2, never crossed
- every persisted answer carries the text of the question that produced it
- every persisted answer carries its asking agent, round, scope and setting
- an unanswered question is reported, not dropped
- an answer missing `answer`, `confidence` or `evidence` is reported
- a well-formed exchange produces no warning at all
- a scope-rejected question is rerouted, and rerouting terminates
- the Q&A loop stops at the round cap, and stops early on convergence
- a resumed registry does not re-issue an id from the prior run
- the instrumented harness ignores OUTPUT FORMAT example ids

## Current state

- `VEGO-AI/tests`: **159 passing** (was 134 before this work).
- `VEGO-AI/framework/test_orchestrator_fixes.py`: 5/5.
- Mutation evidence: **8/8 fixes guarded**.

## Reproducing

```bash
py -3.13 -m pytest VEGO-AI/tests -q
```

```bash
py -3.13 scripts/qa_integrity_evidence.py --out reports/qa-integrity-evidence.json
```

## Limitation

Everything here is offline. It establishes that the Q&A machinery is internally
consistent, that no question is lost, and that every answer is traceable to its
question. It does **not** establish that a provider model will behave well; that
requires a live run, and this suite is the precondition for authorising one, not a
substitute for it.
