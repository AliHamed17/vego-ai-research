# Final decision table — what is verified, what is not, and what needs a human

**Date:** 2026-09-06 · **Prepared by:** Claude, independent scientific reviewer.

This table exists so that nothing in the package is read at the wrong strength. Every row states
one status and nothing stronger.

> **Current transparency-package availability convention (2026-09-08):** `C1`, `C2`, and `C3`
> are code-defined context-only variables, but their accepted-run values are
> `NOT_AVAILABLE_IN_WORKTREE` in the canonical package because no validated private event/output
> binding is mounted here. The numeric values cited below are retained as archival retrospective
> evidence from the separately reviewed run; they are not recomputed or re-issued by this worktree.

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
| Context variables (archival retrospective only) | Historical C1 one value 0.85 → 0 below 0.7 · C2 High 15 / Medium 4 · C3 true 14 / false 5 (n = 19); current canonical availability: `NOT_AVAILABLE_IN_WORKTREE` | archived pipeline output; current package status |
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
| The S1 signal in one of three episodes rests on the `any` aggregation alone (12 Low / 24 Medium / 3 High answers summarise to Medium under majority or plurality), while no classification does — that episode stays `STRONG_ALERT` through S7 | A property of how Detector-v1 summarises this run's answers; not a proposal to change the rule, and Detector-v1 is unchanged (addendum 2026-09-08 §3, including the correction record) |
| The classification is invariant to event order (500/500 permutations) and the confidence labels are all within {Low, Medium, High} | An instrument property on one log; says nothing about correctness |

## 3. Engineering only — never a scientific result

| Item | Status |
|---|---|
| Fixture-versus-real comparison (`baseline-comparison.json`, figure 4) | Instrumentation check. **Not** provider performance, **not** `VEGO_AI_ON` vs `VEGO_AI_OFF`. Denominators 20 and 44 are separate and must not be merged. |
| Detector envelope fixture modes | `ENGINEERING_FIXTURE_NOT_SCIENTIFIC`; enters no scientific denominator |
| Extended detector envelope — nine fixture modes, 9/9 conforming; `WEAK_ALERT`, S1, S2, S3 (both encodings) and S6 each reached in isolation | `ENGINEERING_FIXTURE_NOT_SCIENTIFIC`; shows every class and every isolable branch is reachable; enters no scientific denominator (addendum 2026-09-08 §2) |
| Cost calibration and reserve-bound protocol menu (16 of 30 rows fit USD 6.00) | Arithmetic on frozen reserve constants against one receipt; bounds reservations, not spend, unless every prompt fits the 8,000-token input reserve; not authorisation, not a spend prediction; per-call maxima `NOT_AVAILABLE` (addendum 2026-09-08 §4) |
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
| Agent-4 queue status / whether the selective intervention policy fired | **`NOT_AVAILABLE`** — no validated `human_review_queue.jsonl` is mounted for AirTravel. Four of the five policy inputs cannot be evaluated; only `requires_human_review = false` (×19) is validated. Absence of the queue artifact does **not** establish whether the policy fired or a zero count. |
| Cached-token counts | Never captured by the run counter |
| Independent recomputation of `outbound_requests = 43` | The run persisted no per-call ledger; the value is receipt-asserted and only internally consistent |
| Original contents of `analysis/output-inventory.json` | Overwritten 2026-09-06; 144 candidate serializations failed to reproduce the pinned digest; **not reconstructed** |
| Alert correctness | No ground-truth labels exist for this corpus |

## 5.3 Code provenance correction

`reporting_code_sha` is non-evidentiary documentation metadata. Any value stamped by an older
document is `STAMPED_SUPERSEDED`; only the historical `execution_code_sha` belongs to the accepted
run's evidence chain. `airtravel_real_run.py` changed after that run for receipt-binding work, so
the historical executed code and the current reporting code are **not byte-identical**. This is a
reporting/provenance distinction, not a new scientific result.

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

### 5.2 What creating a binding manifest would actually require — new, 2026-09-06

Codex has since built the gate properly. `study1_evidence_recovery.py` requires the binding to
declare `created_after_run` as an explicit boolean, and enforces
`retrospective_validation → created_after_run = true`, locking the verdict to
`DESCRIPTIVE_REPORTING_WITH_RETROSPECTIVE_PROVENANCE`. A manifest written today therefore
**cannot** be promoted to prospective. That removes the mislabelling risk this table originally
raised against option (a).

**But a deeper obstacle was then found, and it is the reason option (a) is still not a reviewer's
call to make.** `schemas/study1-evidence-binding-v1.schema.json` requires two things the accepted
run cannot supply:

| Required field | Problem |
|---|---|
| `execution_code_sha256` (and `config_sha256`) | The validator compares the binding's value against the **run receipt's** field. The accepted run's receipt binds neither — that is provenance gap 3. Any value written into the binding is therefore **unverifiable by construction**: nothing in the evidence can confirm or refute it. |
| `pipeline_output_manifest` | A **required** primary artifact that the accepted run never produced. It is a run-time output in the Study 2 design; Study 1 predates it. It exists nowhere under `v4-real-run/`. |

Satisfying the schema thus requires authoring two attestations that no evidence can check, and
creating an artifact that did not exist at run time. The mode gate protects against mislabelling
provenance; it does not protect against a reviewer inventing the inputs. Doing that to unblock a
tool is the precise failure mode this package exists to prevent, so it was not done.

**This does not block descriptive reporting.** Every published number remains reproducible from
`analysis/evidence-validation.json` and from the recomputation validator, and Codex's own success
status agrees that descriptive reporting is permitted.

## 6. Requires a human decision — not more analysis

| # | Decision | Options | What turns on it |
|---|---|---|---|
| D0 | How is the validator divergence resolved? | (a) author a binding manifest, accepting that `execution_code_sha256` is unverifiable and that a `pipeline_output_manifest` must be created after the fact — see §5.2; (b) keep both validators and cite each by name; (c) relax the schema so a historical run can bind only what its receipt actually carries | **Highest priority.** Until this is settled the canonical tool emits no Study 1 numbers, while the published package cites 92 checks. Option (a) does **not** upgrade provenance and must never be presented as doing so. |
| D1 | Should Detector-v1's "candidate for human review" label ever be wired to the existing `human_review_queue`? | (a) keep Detector-v1 as a reporting label; (b) separately define a governed bridge | Today Detector-v1 is reporting-only and does not write the Agent-4 queue. The Agent-4 queue is a separate mechanism; wiring a bridge would be a new operational policy and would change what the thesis is claiming. |
| D2 | Which Study 2 preregistration is authoritative? | PR #41 version 2, PR #42's version, or a merged one | Two documents with the same filename exist on different branches. They must be reconciled before either is reviewed. |
| D3 | Does the unrecovered `output-inventory.json` block the package? | (a) proceed with it disclosed; (b) block | No published claim depends on it and all scientific values reproduce. Current handling: proceed with disclosure. |
| D4 | Retry policy: 1 or 3 attempts per call? | Preregistration says at most 3; Codex's frozen config says 1 | Must be one number before any paid run; it affects the request-cap arithmetic. |
| D5 | Are Iris and Arnon eligible as blinded raters? | (a) yes with declared interest; (b) recruit externally | They authored VEGO-AI. Either choice is defensible; the interest must be recorded beside any result. |
| D6 | Is `include_medium` true or false for the selective intervention policy in any future study? | true (Medium triggers) or false | Changes how many patterns enter the queue. Must be fixed before, not after, an outcome. |
| D7 | Timing of the supervisor meeting | before Wednesday, or later | The reply email is drafted and **not sent**; it awaits approval of both wording and date. |
| D8 | Which protocol, if any, runs under the USD 6.00 authorisation of 2026-09-08? | one row of the reserve-bound menu in `2026-09-08-study1-instrument-experiments-addendum.md` §4 (16 rows fit USD 6.00; e.g. 2×326 calls at 4,096 output → USD 4.25, or 5×180 at 4,096 → USD 5.86), or none | Fitting the ceiling is arithmetic, not authorisation to run. Any run still needs its own preregistration naming the exact row, D4 settled, gate 4 (independent review) closed, gate 6 (frozen model/ceiling/caps) confirmed, and a present credential — `OPENAI_API_KEY` is absent as of 2026-09-08. Nothing has been spent. |

## 7. Standing prohibitions

No claim of accuracy, precision, recall, F1, alert correctness, effectiveness, human benefit,
causality, representativeness, generalization, student behaviour, historical Cheers/ParkWise
recovery, or `VEGO_AI_ON`/`VEGO_AI_OFF` superiority. No fixture presented as an empirical
finding. Retrospective provenance is never described as fully prospective or fully preregistered.
"Candidate for human review" is never written as a confirmed need for intervention.
