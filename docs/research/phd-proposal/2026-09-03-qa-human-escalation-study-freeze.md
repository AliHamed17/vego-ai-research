# VEGO-AI Preliminary Study — Automatic Human-Escalation Detection from Inter-Agent Q&A

**AUTHORITATIVE CURRENT PRELIMINARY-STUDY DESIGN. DESIGN FREEZE ONLY — NOT EXECUTED.**
Scientific/methodological lead record. Codex owns implementation. 2026-09-03, base revision `87e3ce9`.

Supersedes, for the current milestone,
[`2026-09-03-preliminary-human-intervention-pilot-evidence-freeze.md`](2026-09-03-preliminary-human-intervention-pilot-evidence-freeze.md),
which is preserved as valid later-stage material.

**Supervisor basis.** Arnon: stage one is only *identify the cases in which human intervention is
required* — define the conditions, build an automatic detector, run it, and judge which alerts are correct.
No relation yet to whether intervention improves anything. Iris: the study should not be organised
primarily around individual agents; examine **inter-agent communication, especially Q&A**, and possibly
the agents' **answer confidence**. Arnon agreed communication is important.

## 1. Study question

**Can observable patterns in VEGO-AI's inter-agent Q&A communication be used to automatically identify
situations in which human expert intervention is warranted?**

This addresses the **WHEN** component of provisional SQ1. *(SQ1 wording is provisional and not
supervisor-approved.)*

## 2. Unit of analysis

**One inter-agent Q&A / communication episode.** Not a model, not a compliance judgment, not a variability
pattern, not an agent. Each episode retains: source agent · source stage/skill · target agent · question id
· question type · question text · answer · answer confidence · answer evidence · case/guideline/pattern
context where available · Q&A round · whether follow-up occurred · whether the issue converged.

Communication is the primary object (Iris); results are **stratified** by agent and stage (Arnon).

## 3. BLOCKING GATE — the frozen corpus is half-present

Verified read-only across 8 `eval_state.json` files and every JSON artifact in both the supervisor package
and `VEGO-AI/eval_output` (byte-identical trees).

| What | Count | Evidence |
| --- | --- | --- |
| Question emissions, canonical (`agentB_best_guidelines.json` / `eval_state.json`) | **12** — cd_ch 3, cd_pw 6, ucd_ch 2, ucd_pw 1 | `questions_to_language_advisor` |
| Question emissions across all three runs | **30** distinct texts | `agentB_run{1,2,3}_guidelines.json` |
| Questions to the Domain Advisor | **0** | `questions_to_domain_advisor` empty everywhere |
| Questions from Agent 3 or Agent 4 | **0** | no such key in any `agentC_*` / `agentD_*` artifact |
| **Answers** | **0** | `lang_qa_history` = `[]` and `dom_qa_history` = `[]` in all 4 canonical states |
| **Answer confidence values** | **0** | no `confidence` key on any persisted answer |
| Q&A rounds / convergence records | **0** | nothing persisted |

The corpus is therefore **a one-sided, never-routed question stream: asked and abandoned, zero-turn.**

**Cause — a harness gap, not agent behaviour.** The shipped corpus was produced by `System/eval/evaluator.py`,
which carries the author's own comment at line 402: `agent1_caps: list = []   # no Q&A loop in evaluator`.
It declares `MAX_QA_ROUNDS = 10` at line 371 and never references it again; skills 3-2 and 3-3 are labelled
"single pass" at lines 414 and 429. Agent 3 is handed empty advisor capability lists, so it has no routing
targets. The full pipeline `System/framework/orchestrator.py` *does* implement Q&A — `from qa_registry import
QARegistry`, `MAX_QA_ROUNDS = 10`, `_answer_lang_questions`, `_answer_dom_questions`, unconditional at
lines 154-166 — and would produce answers on a normal run.

**Consequence.** Every one of the 12/30 questions is trivially "unanswered". That is an artifact of the
harness, not a signal about the agents. A detector whose alerts all fire for the same structural reason has
**no feature variance and cannot be validated**. Answer confidence — Iris's specific suggestion — is
architecturally supported (`agent1_language_advisor.py:224` specifies `"confidence": "High | Medium | Low"`,
mirrored in `agent2_domain_advisor.py:487`) but has **zero instances** and is never validated by any code.

## 4. Corpus options, in preference order

| Option | Cost | What it yields |
| --- | --- | --- |
| **O1 — request `interaction_log.jsonl` from the authors** | **zero LLM cost** | `eval_config.json:13` sets `"interaction_log": "interaction_log.jsonl"` and `llm_client.py:170` writes `response_raw` for every call, but **no such file was shipped**. If the authors retained it, the raw Agent-2/3 outputs discarded by `evaluator.py:537` may be recoverable, possibly including questions in context. **Try this before spending money.** |
| **O2 — re-run `orchestrator.py` on one setting** | LLM cost; needs approval | Produces genuine answers, confidence, rounds and convergence. Reverses the standing "no agent is re-run" posture — a supervisor decision |
| **O3 — question-emission study on n=12** | zero | Executable today, but all 12 are feature-identical; supports description, not detector validation |

**Recommendation: O1, then O2 scoped to one setting.** O3 alone cannot answer the study question.

## 5. Verified communication routes

| Route | Status |
| --- | --- |
| Agent 2 → Language Advisor (phase 2, skill 2-1) | **OBSERVED IN FROZEN DATA** — 12 canonical / 30 across runs |
| Agent 2 → Language Advisor, answered | **SUPPORTED IN CODE, NOT OBSERVED** — `orchestrator.py:71-90` |
| Agent 3 → Domain Advisor (naming equivalence) | **SUPPORTED IN CODE, NOT OBSERVED** — evaluator passes empty caps |
| Agent 3 → Language/Domain Advisor (undeterminable candidates) | **SUPPORTED IN CODE, NOT OBSERVED** |
| Agent 4 → any advisor | **SUPPORTED IN CODE, NOT OBSERVED** — keys emitted with 0 entries |
| Any agent → human | **NOT AVAILABLE** — no such route in the original system |

Only **one of six** channels was ever exercised, and only in one direction without answers.

## 6. Candidate signals — admissibility

| | Signal | Verdict |
| --- | --- | --- |
| S1 | Low Q&A answer confidence | ADMISSIBLE AFTER CORPUS GENERATION |
| S2 | Medium Q&A answer confidence | ADMISSIBLE AFTER CORPUS GENERATION |
| S3 | Unanswered question | **REMOVE** — true of 100% of the frozen corpus by harness construction; carries no information |
| S4 | Answer lacks supporting evidence | AFTER CORPUS GENERATION; weak, largely collinear with S1 |
| S5 | Repeated / follow-up clarification | NOT IMPLEMENTED — no follow-up linkage field exists |
| S6 | Multiple Q&A rounds before resolution | AFTER CORPUS GENERATION |
| S7 | Non-convergence / `MAX_QA_ROUNDS` | AFTER CORPUS GENERATION; expect a near-zero base rate |
| S8 | Unusually many Q&A events per decision episode | NOT IMPLEMENTED — no episode grouping key exists |
| S9 | Lower Agent-2 `mapping_certainty` | **ADMISSIBLE NOW**, but explicitly a **non-Q&A contextual signal** |

**Starting set: S1, S2, S6, S7 on a generated corpus; S9 as a separate contextual comparator.**

**Do not mix the three confidences.** Q&A *answer* confidence (`questions_answers[].confidence`, LLM
self-report, unvalidated, n=0), Agent-2 `mapping_certainty` (n=444, read by **zero** code paths), and
Agent-4 classification confidence (n=27) have different semantics and different producers. S1/S2 are
LLM self-reports and inherit the weakness already documented for Agent-4's `total_cases`: a model-authored
value that no code validates.

## 7. Automatic detector (version 1)

Transparent · deterministic · rule-based · auditable. **No ML.** For each episode: observable features →
frozen rule → **ALERT / NO ALERT**, and every alert emits a **reason code** naming the firing feature.

Version 1 is frozen **before** any human labels are seen. Rules must not be tuned on reviewer labels prior
to the first evaluation; any later tuning creates a version 2 evaluated on held-out episodes.

## 8. What exactly is tested, and why it answers the question

The study tests whether **predefined, observable communication characteristics of VEGO-AI Q&A episodes can
act as automatic indicators that expert intervention may be warranted.**

It answers the question because if Ali, Iris and Arnon independently judge that the automatically selected
communication events are indeed situations where a human should intervene, then those patterns become
**candidate automatic escalation conditions**. Whether intervening subsequently improves VEGO-AI is out of
scope for this milestone.

## 9. Human validation protocol

Three independent reviewers, documented generically as **Reviewer A / B / C** (Ali, Iris, Arnon).

Per episode: **HUMAN INTERVENTION REQUIRED / NOT REQUIRED / UNCLEAR**, plus a short rationale and optional
confidence. **Blind first pass** — reviewers must not see the detector's ALERT state where technically
possible. Independent review first, then agreement is computed, then disagreements are adjudicated.

**No labels are generated by this document, by Claude, or by any automated process.** The reviewer sheets
are Codex's to build; the protocol is fixed here.

## 10. Alert classification (after adjudication)

| Detector | Adjudicated label | Class |
| --- | --- | --- |
| ALERT | Human required | **CONFIRMED ALERT** |
| ALERT | Human not required | **FALSE ALERT** |
| ALERT | Unclear | **UNCLEAR ALERT** |
| NO ALERT | Human required | **MISSED REQUIRED INTERVENTION** |

**If only alerts are reviewed, recall must not be computed.** Coverage measures require that non-alert
episodes are also labelled.

## 11. Metrics

Primary: total evaluated communication events · alerts generated · confirmed / false / unclear alerts ·
**alert yield** = confirmed / all alerts · **false-alert rate** = false / all alerts · reviewer agreement
before adjudication. Only with full-event labelling: missed required interventions and a coverage measure.

None of these is model accuracy. They describe a rule against a small adjudicated reviewer panel.

## 12. Stratification

By source agent · source stage · target agent · Q&A type · confidence level · trigger reason code. This
delivers Arnon's per-agent view without abandoning Iris's communication-centred unit.

## 13. Allowed claim

*"Certain observable inter-agent communication patterns can be evaluated as candidate automatic indicators
for when VEGO-AI should escalate to a human."*

Only after labels exist may we state which candidate patterns had high or low confirmed-alert yield.

## 14. Forbidden claims

Human intervention improves VEGO-AI · accuracy improvement · score improvement · better assessment quality
· reduced burden · generalization · causal benefit · never *prove*. An agent-versus-expert disagreement does
**not** by itself mean a human should have been interrupted — only the adjudicated reviewer label
establishes that.

## 15. Execution GO / NO-GO

**GO requires:** a corpus with answered Q&A episodes (O1 or O2) · detector v1 frozen before labels ·
blind reviewer sheets from Codex · supervisor decision on O2's LLM re-run · reviewers confirmed.

**NO-GO if:** the corpus remains answer-free (no feature variance) · S3 is used as a signal · any label is
machine-generated · detector rules are tuned on labels before the first evaluation · recall is reported
from alert-only review.

## 16. Codex dependencies

Q&A corpus extraction · communication-path observability receipts · confidence inventory · deterministic
feature extraction · alert detector scaffold · blind review-sheet generator · evaluation scaffold. Codex has
already delivered the 138-case Agent-C score reconstruction and the external C2 evidence bridge
(`b1d7990`), and has begun the extractor as untracked working-tree files.

## 17. Open supervisor decisions

1. **Approve O1** — ask the authors for `interaction_log.jsonl`? Zero cost, highest value.
2. **Approve O2** — re-run `orchestrator.py` on one setting to generate answered Q&A? This reverses the
   "no agent is re-run" posture and costs LLM calls. **This is the blocking decision.**
3. Confirm Reviewer A/B/C are Ali, Iris, Arnon, and that blind first-pass review is acceptable.
4. Confirm the milestone change is recorded: the counterfactual-replay pilot is later-stage, not current.
5. The delivered one-pager still describes the superseded study and needs replacing for this milestone.
