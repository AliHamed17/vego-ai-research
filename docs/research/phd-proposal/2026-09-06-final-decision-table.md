# Final decision table — what is verified, what is not, and what needs a human

**Date:** 2026-09-06 · **Prepared by:** Claude, independent scientific reviewer.

This table exists so that nothing in the package is read at the wrong strength. Every row states
one status and nothing stronger.

---

## 1. Verified — recomputed from private evidence and cross-checked

| Item | Value | Source |
|---|---|---|
| Episodes / lifecycle | 3 (2 `CONVERGED`, 1 `TERMINATED_MAX_ROUNDS`), 0 `INCOMPLETE_TECHNICAL` | event log |
| Detector-v1 denominator | 3 complete episodes | event log |
| Questions / answers | 44 / 44 | event log |
| Maximum round index | 10 (bound is 10) | event log |
| Directed route pairs | 3 of 6 — asking agent4/answering agent2 = 39; agent3/agent2 = 4; agent3/agent1 = 1 | event log |
| Answer confidence | Low 16 · Medium 25 · High 3 (of 44) | event log |
| Evidence-field length | n 44, min 38, median 62, max 540, zero-length 0 → `S3` never fired | event log |
| Detector-v1 classification | `STRONG_ALERT` 3 · `WEAK_ALERT` 0 · `NO_ALERT` 0 | event log + frozen rule |
| Signals fired | S1 3 · S2 2 · S6 2 · S7 1 · S3 0 | event log + frozen rule |
| Calls / tokens / cost | 43 requests (cap 326) · 267,942 tokens · USD 0.134972 (budget USD 10) | run receipt, arithmetic reproduced |
| Mapping result | 4 of 4 cases `Satisfied`; partially 0; not-satisfied 0 | pipeline output |
| Deviation patterns | guideline 0 · fragment 19 (Alternative 14 / Domain Mistake 5), `probe_confirmed` false ×19 | pipeline output |
| Context variables | C1 one value 0.85 → 0 below 0.7 · C2 High 15 / Medium 4 · C3 true 14 / false 5 (n = 19) | pipeline output |
| Evidence integrity | event-log and run-receipt SHA-256 both reproduce byte-exactly | direct hashing |

Validator: **92 checks, 87 PASS, 0 scientific value failures.**

## 2. Descriptive only — true of this run, generalising to nothing

| Statement | Why it is descriptive only |
|---|---|
| All three episodes are candidates for human review | One run, one model, one configuration, N = 4, denominator 3 |
| The threshold does not separate on this corpus | A property of this corpus, not of the rule in general |
| Answer confidence skews Low/Medium | Self-reported by the model; not calibrated; not an external measure |
| 39 of 44 questions travelled one route | A routing observation; says nothing about whether that route was appropriate |
| Two of four cases produced no episode | A valid observation, not a technical failure — both produced complete pipeline output |

## 3. Engineering only — never a scientific result

| Item | Status |
|---|---|
| Fixture-versus-real comparison (`baseline-comparison.json`, figure 4) | Instrumentation check. **Not** provider performance, **not** `VEGO_AI_ON` vs `VEGO_AI_OFF`. Denominators 20 and 44 are separate and must not be merged. |
| Detector envelope fixture modes | `ENGINEERING_FIXTURE_NOT_SCIENTIFIC`; enters no scientific denominator |
| Study 2 fixture preflight | Both conditions emit empty lists by construction; every per-case row is 0 versus 0 |
| Offline authorized preflight (46/46 identical calls) | Engineering evidence for the instrumentation, not a finding |

## 4. Not executed — no result exists

| Item | Status |
|---|---|
| Study 2 `VEGO_AI_ON` vs `VEGO_AI_OFF` | `PREPARED_NOT_EXECUTED`. No provider call, no model frozen, no result. Not a baseline for Study 1 and never pooled with it. |
| Blinded human-rubric quality evaluation | Rubric defined (R1–R5), **no artifact scored**, no rater recruited. Outcome `NOT_COLLECTED`. |
| Study 2B model portability (Llama) | Separate future protocol; not designed, not authorized, not anticipated |
| Detector-v1 on any Study 2 data | Never invoked. `applicable_to` ON only; OFF denominator `NOT_APPLICABLE`, never zero |

## 5. NOT_AVAILABLE — absent, and absence is not zero

| Item | Why |
|---|---|
| Whether VEGO-AI's selective intervention policy fired on the accepted run | The run produced no `human_review_queue.jsonl` at all. Four of its five triggers cannot be evaluated. Only `requires_human_review = false` (×19) is validated. |
| Cached-token counts | Never captured by the run counter |
| Independent recomputation of `outbound_requests = 43` | The run persisted no per-call ledger; the value is receipt-asserted and only internally consistent |
| Original contents of `analysis/output-inventory.json` | Overwritten 2026-09-06; 144 candidate serializations failed to reproduce the pinned digest; **not reconstructed** |
| Alert correctness | No ground-truth labels exist for this corpus |

## 5.1 The validator divergence — the single most important open item

Two validators now exist for the same evidence, and they disagree about what may be emitted.

| | Recomputation validator (mine, at commit `63da010`) | Binding-gated validator (Codex, canonical at HEAD) |
|---|---|---|
| Method | Recomputes every aggregate from the event log and cross-checks all derived files | Requires a `study1-evidence-binding-v1` manifest first, then recomputes |
| Result on the accepted run | 92 checks · 87 PASS · **0 scientific value failures** · 4 provenance gaps · 1 derived-chain failure | `EVIDENCE_NOT_AVAILABLE_IN_REVIEWED_WORKTREE` |
| Why that result | The evidence is present in this worktree and its hashes reproduce byte-exactly | **No binding manifest was supplied.** Not a statement that the evidence is absent or wrong |
| Output artifact | `analysis/evidence-validation.json` (present) | one check row, no numbers |

**Neither result contradicts the other.** Codex's status string is scoped —
*"IN_REVIEWED_WORKTREE"* — and their handoff states the reason plainly: no private root is
mounted in the worktree they reviewed. `external_data/**` is git-ignored and does not propagate
between worktrees; this is the same worktree-scope condition that produced the earlier, later
withdrawn, `EVIDENCE_BLOCKED` claim.

Codex's own success status is `ACCEPTED_FOR_DESCRIPTIVE_REPORTING_WITH_RETROSPECTIVE_PROVENANCE`,
so both parties agree that descriptive reporting is permitted and that the provenance is
retrospective. The disagreement is only about the **gate**.

**A binding manifest was deliberately not created.** Every field it requires is known and
verified here, so producing one is trivially possible — and that is exactly why it was not done.
A manifest authored today, after the outputs exist, cannot establish the pre-output binding that
the caveat says is absent, and a file named `evidence-binding` created after the fact invites
precisely the misreading this package exists to prevent. Creating it is a decision for a human,
not a convenience for a reviewer.

**Consequence for the published numbers:** they remain reproducible from
`analysis/evidence-validation.json` and from the validator source at `63da010`, but they are
**not** reproducible by the canonical CLI at HEAD until the gate is satisfied. That must not be
described as the numbers being unverified; it is the canonical instrument declining to speak.

## 6. Requires a human decision — not more analysis

| # | Decision | Options | What turns on it |
|---|---|---|---|
| D0 | How is the validator divergence resolved? | (a) create an explicitly-labelled retrospective binding manifest so the canonical CLI can run; (b) keep both validators and cite each by name; (c) restore the recomputation validator as canonical | **Highest priority.** Until this is settled the canonical tool emits no Study 1 numbers, while the published package cites 92 checks. Option (a) does **not** upgrade provenance and must never be presented as doing so. |
| D1 | Should Detector-v1's "candidate for human review" label ever be wired to the existing `human_review_queue`? | (a) keep it a reporting label; (b) wire it | Today it is a reporting label only. Wiring it would make it an operational trigger and would change what the thesis is claiming. |
| D2 | Which Study 2 preregistration is authoritative? | PR #41 version 2, PR #42's version, or a merged one | Two documents with the same filename exist on different branches. They must be reconciled before either is reviewed. |
| D3 | Does the unrecovered `output-inventory.json` block the package? | (a) proceed with it disclosed; (b) block | No published claim depends on it and all scientific values reproduce. Current handling: proceed with disclosure. |
| D4 | Retry policy: 1 or 3 attempts per call? | Preregistration says at most 3; Codex's frozen config says 1 | Must be one number before any paid run; it affects the request-cap arithmetic. |
| D5 | Are Iris and Arnon eligible as blinded raters? | (a) yes with declared interest; (b) recruit externally | They authored VEGO-AI. Either choice is defensible; the interest must be recorded beside any result. |
| D6 | Is `include_medium` true or false for the selective intervention policy in any future study? | true (Medium triggers) or false | Changes how many patterns enter the queue. Must be fixed before, not after, an outcome. |
| D7 | Timing of the supervisor meeting | before Wednesday, or later | The reply email is drafted and **not sent**; it awaits approval of both wording and date. |

## 7. Standing prohibitions

No claim of accuracy, precision, recall, F1, alert correctness, effectiveness, human benefit,
causality, representativeness, generalization, student behaviour, historical Cheers/ParkWise
recovery, or `VEGO_AI_ON`/`VEGO_AI_OFF` superiority. No fixture presented as an empirical
finding. Retrospective provenance is never described as fully prospective or fully preregistered.
"Candidate for human review" is never written as a confirmed need for intervention.
