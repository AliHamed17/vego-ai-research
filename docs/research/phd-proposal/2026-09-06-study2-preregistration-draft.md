# Study 2 preregistration — VEGO_AI_ON versus VEGO_AI_OFF

**Status: `PREPARED_NOT_EXECUTED` — requires separate independent review and fresh authorization.**

**Version 2 (2026-09-06).** Supersedes version 1 of the same date. Version 1 is
withdrawn: it declared orchestration the *single varying factor*, which its own
prompt-difference receipt contradicts, and it defined no primary outcome. The
substantive changes are listed in §16.

Nothing in this document has been run against a provider. No result exists. This
draft freezes the design *before* any outcome is observed, so the design cannot be
chosen to fit a result afterwards.

Study 2 is **separate from Study 1**. No denominator, episode, count or artifact from
Study 1 is pooled with Study 2, and Study 1 results are not reinterpreted here.

## 1. Research question

> Holding corpus, cases, model and provider configuration constant, how does the
> quality of the produced per-case artifact — judged blind against a fixed rubric —
> and how do call volume, token usage, cost and elapsed time differ between the
> VEGO-AI orchestrated system and a defined non-VEGO single-call system?

The question is comparative. The quality outcome is judged by humans against a rubric
defined below; it is **not** a measure of correctness against ground truth, because no
ground-truth labels exist for this corpus.

## 2. Operational definitions

| Condition | Definition |
|---|---|
| `VEGO_AI_ON` | Full four-agent VEGO-AI orchestration: agent1 language advisor, agent2 domain advisor, agent3 model inspector, agent4 variability explorer, with the inter-agent question-and-answer protocol and the round loop bounded by `MAX_QA_ROUNDS = 10`. |
| `VEGO_AI_OFF` | A defined non-VEGO baseline: one direct model call per case pursuing the same per-case objective — map reference guidelines onto the candidate model and audit uncovered fragments — returning the same output contract. |

`VEGO_AI_OFF` must **not** contain agent decomposition, inter-agent Q&A, or a round
loop. It is not a disabled flag inside the orchestrator, and it is not a broken or
degraded system. It is a straightforward single-model implementation of the same task.

**Codex and Claude are implementation agents. They are never experimental conditions
and never appear as a row in any results table.**

## 3. This is a system comparison, not a single-factor experiment

Version 1 asserted that orchestration was the single varying factor. **That claim is
withdrawn and must not be restated.** The two conditions necessarily differ in more
than one respect:

- **prompt text** — ON issues role-scoped skill prompts to four agents; OFF issues one
  direct per-case prompt;
- **task decomposition** — ON splits the objective across agents and rounds; OFF
  performs both sub-tasks in a single response;
- **call structure** — ON makes many calls per case; OFF makes exactly one.

These differences are not incidental; they *are* the orchestration. They cannot be
held constant while still varying orchestration, so no design can isolate
orchestration as a lone factor here.

Study 2 is therefore a **system comparison**: two complete systems addressing the same
objective, compared as wholes. Every reported difference is attributable to the
*system*, not to orchestration as an isolated mechanism. Any sentence asserting that
orchestration alone caused an observed difference is a claim-boundary violation.

The `prompt_difference_receipt` emitted by the harness records prompt hashes for both
conditions so that the difference is **auditable rather than asserted**. It documents
the difference; it does not eliminate it, and it must never be cited as evidence that
only orchestration varied.

## 4. Frozen before any output is observed

| Parameter | Value | Bound where |
|---|---|---|
| Corpus | `text2uml_airtravel_253b26dc` | code (`RUNTIME_FILES` hash pin) |
| Setting | `cd_airtravel` | code |
| Case identifiers | exactly `01`, `02`, `03`, `04` — identical in both conditions | code |
| Provider / model | one model, identical in both conditions, recorded before any future provider call | **not yet bound for a paid run; fixture runner accepts only a local injected client** |
| Temperature / seed | temperature `0.0`; no stochastic seed is used by the deterministic fixture | frozen config + runner |
| Max output tokens | `2048`, identical in both conditions | frozen config + call request |
| Retry policy | one transport retry (`retries=1`), counted against the request cap; no content-based retry | frozen config + runner |
| Request timeout | 180 s per call; 3600 s per condition run | frozen config + runner |
| Concurrency | 2 cases | frozen config + runner (both conditions) |
| Request cap | 326 attempts including retries, **per condition** | frozen config + runner |
| Budget cap | USD 10 hard ceiling, charged only from supplied usage, **per condition** | frozen config + runner |
| Egress restriction | `DISABLED` for the fixture; no provider/network adapter is supplied | frozen config + dependency injection |
| Output contract | `study2-condition-output-v1`: mapping rows, coverage summary, uncovered fragments | schema + runner (strict) |
| Privacy | private git-ignored output root; hash/count receipts only in version control | runner + path/privacy tests |

The "bound where" column is a factual statement about the current implementation, not
an aspiration. Only the provider/model identity remains intentionally unbound for a
future paid run; the fixture path is local-only and cannot call a provider.

## 5. Primary outcome — blinded human-rubric quality

The **primary outcome** is the rubric-scored quality of the shared per-case output
artifact (mapping rows, coverage summary, uncovered fragments), judged blind.

**Unit of analysis.** One produced artifact per case per condition: 4 cases × 2
conditions = 8 artifacts.

**Judges.** At least two independent judges competent in UML domain modelling. A judge
must not be the candidate. Any judge who is an author of the VEGO-AI paper has a
declared interest and this must be recorded beside the result.

**Blinding procedure.**
1. Condition labels, file paths, run identifiers, agent names, round counts, call
   counts, timings and cost are stripped from every artifact before scoring.
2. Artifacts are presented in an order randomised per case, fixed before scoring.
3. Judges receive only: the case identifier, the domain description, the candidate
   model, the reference guidelines, and the artifact under review.
4. Judges score independently, without conferring, and record scores before any
   discussion.
5. Condition labels are revealed only after **all** scores are recorded and frozen.
   Re-scoring after unblinding is prohibited.

**Rubric.** Five dimensions, each scored 1–5 against written anchors fixed before
scoring begins:

| # | Dimension | What is judged |
|---|---|---|
| Q1 | Mapping correctness | Does each stated compliance status follow from the candidate model? |
| Q2 | Evidence adequacy | Does the cited evidence actually support the stated status? |
| Q3 | Fragment identification | Are model fragments outside the guidelines identified without omission or invention? |
| Q4 | Fragment labelling | Is each fragment label (Alternative / Domain Mistake / Language Mistake) defensible? |
| Q5 | Internal consistency | Is the artifact self-consistent and faithful to the output contract? |

The per-artifact quality score is the vector `(Q1…Q5)`. **No composite index is
computed**, and dimensions are never summed or averaged into a single quality number.

**Agreement.** Inter-judge agreement is computed per dimension with an ordinal measure
(Krippendorff's alpha; quadratic-weighted Cohen's kappa if exactly two judges) and is
**reported with the result, always, including when it is poor**. A minimum acceptable
agreement of α ≥ 0.60 per dimension is set now. Any dimension falling below it is
reported as `AGREEMENT_INSUFFICIENT` and its scores are **not** interpreted — they are
not repaired, re-judged, or dropped from the report.

**Adjudication.** Disagreements of two points or more are discussed and the discussion
recorded, after independent scores are frozen. Adjudicated scores are reported
alongside the original independent scores, never in place of them.

**If no judges are available, the primary outcome is reported as `NOT_COLLECTED`.**
The secondary outcomes are then reported alone and the study is explicitly labelled as
having produced no quality finding. Secondary outcomes are never promoted to primary.

## 6. Secondary outcomes — descriptive only

Reported per condition, per case, with no inferential claim:

- completed cases (of 4);
- output-schema validity per case;
- mapping rows per case; uncovered fragments per case;
- outbound calls; input and output tokens; cost; elapsed wall-clock time;
- technical failures.

Cost, latency and call volume are **resource descriptions**. They are not efficiency
claims and must never be worded as one: a cheaper condition is not thereby better.

## 7. The non-shared measure — the decisive constraint

Detector-v1 operates on inter-agent Q&A episodes. `VEGO_AI_OFF` produces **no such
episodes**, so:

- Detector-v1 is applied to `VEGO_AI_ON` **only**;
- the Detector-v1 denominator for `VEGO_AI_OFF` is **`NOT_APPLICABLE`, never zero**;
- reporting OFF as "zero alerts" is a **category error** — absence of a measuring
  instrument is not absence of a phenomenon;
- **alert rates, alert counts and alert proportions are never compared across the two
  conditions, in any table, figure, sentence or supplementary file.**

This prohibition is absolute and is not waived by any result.

## 8. Sampling, denominators and analysis

**N = 4 is a purposive feasibility sample.** The four cases were selected because a
hash-pinned public-external corpus was available for them, not because they represent
any population. Consequently:

- no hypothesis is tested; no p-value, confidence interval, effect size or power
  calculation is computed or reported;
- no generalization is claimed to other corpora, domains, models, settings or users;
- results are reported as per-case tables and per-case values, never as a single
  headline statistic;
- separate denominators per condition. No pooling across conditions, across models, or
  with Study 1.

Repeats, if separately authorized, are reported as distinct runs with per-run values
and an explicit range — never averaged into one figure.

## 9. Missingness, failures and zero-Q&A behaviour — predefined

Fixed now, before any outcome exists:

| Situation | Predefined handling |
|---|---|
| A case produces no artifact in a condition | Reported as `NOT_PRODUCED` for that case and condition. Excluded from that condition's denominator only. Never imputed, never replaced by the other condition's value. |
| An artifact fails the output-schema contract | Reported as `SCHEMA_INVALID`, counted in the schema-validity outcome, and excluded from the quality denominator. It is not repaired before judging. |
| An artifact is partially complete | Judged as it stands. Missing content lowers the relevant rubric dimension; it does not trigger a re-run. |
| **A case produces zero Q&A episodes under ON** | This is a **valid observation, not a failure**. The case remains in every denominator. Its Detector-v1 contribution is `NO_EPISODE`, which is distinct from both `NO_ALERT` and `NOT_APPLICABLE`. In Study 1, two of four cases produced zero episodes while still producing complete pipeline output; that outcome must not be recorded as an error. |
| A provider or transport error | Reported as a technical failure per condition, with the attempt and its cost disclosed. |
| A cap, budget or timeout is reached | The run stops and reports. Partial results are published as partial and labelled `STOPPED_AT_CAP`. |

**No outcome-dependent adaptation.** Retries are permitted only for transport-level
failures, are capped at three per call, and are counted against the request cap. It is
prohibited to retry a call because its *content* was judged poor, to switch model,
change temperature, change prompts, change the corpus, or re-run a condition after
seeing any outcome. The model is frozen in the authorization text before the first
call and cannot be changed afterwards; changing it starts a new, separately
preregistered study.

## 10. Offline paired preflight requirement

Before any paid execution, **both conditions together** must pass an offline
fake-provider preflight proving: no network, no credential, no provider call;
configuration parity on every parameter in §4; that outputs are separately tagged;
that no cross-condition contamination occurs; that OFF contains no hidden Q&A; and
that the prompt-difference receipt is produced and internally consistent.

The preflight **cannot** prove that only orchestration differs — §3 explains why no
design can. It proves parity on the enumerated parameters and records the structural
differences; nothing more may be claimed from it.

A preflight harness exists (`scripts/study2_on_off_experiment.py`) and is exercised by
dependency-injected engineering fixtures only. Fixture payloads are deliberately
non-scientific and are written only to a caller-supplied private output root. They
demonstrate plumbing, strict schema rejection, policy caps, privacy and lifecycle
shape; they carry no comparative content and no figure or sentence may present them
as a difference between the conditions.

## 11. Authorization gates

1. Independent review of this preregistration.
2. Closure of every blocking precondition in §13.
3. Independent review of the implementation at one immutable head with green CI.
4. Fresh one-time offline paired-preflight grant.
5. Independent audit of the preflight evidence.
6. **Separate fresh authorization for each paid condition** — one for the ON run and
   one for the OFF run — each naming the model, the budget and the cap in the
   authorization text itself. One authorization never covers both conditions.

## 12. Stop conditions

Stop and report — do not repair after the fact — if the baseline is undefined or
unrunnable, if the prompt-difference receipt is missing or inconsistent, if a cap or
budget is breached, if a credential, raw prompt, raw answer or private path reaches
version control, or if any parameter in §4 is found to differ between the conditions.

## 13. Remaining gates before any provider-backed run

The offline implementation now binds the declared control policy through
`src/vego_study2/config.py` and `src/vego_study2/runner.py`, and the dependency
injection boundary has no provider or network adapter. The following gates remain
open for a future provider-backed run:

1. Independent review of this implementation and the frozen configuration.
2. Freeze one provider/model identity, temperature/seed policy and exact budget in a
   fresh authorization message before the first call.
3. Separately verify provider-host egress, credential handling and any provider client
   in the authorized execution environment; the fixture path cannot establish those
   properties.
4. Obtain a fresh one-time paired offline-preflight grant and audit its receipt.
5. Obtain separate fresh authorizations for the ON and OFF paid conditions, with no
   adaptive retry, model switching, corpus change or outcome-dependent rerun.
6. Obtain independent blinded human-rubric scores; without them the primary outcome
   is `NOT_COLLECTED` and no quality finding exists.

Until these gates are closed, **no paid Study 2 run may be authorized**.

## 14. Claim boundary

**Permitted:** blinded rubric scores per artifact with their agreement statistics;
descriptive differences in produced artifacts, calls, tokens, cost and elapsed time;
on one corpus, four purposively selected cases, one model, one configuration; framed
as a comparison of two systems.

**Forbidden:** that orchestration alone caused any observed difference; accuracy,
precision, recall, F1; alert correctness; any cross-condition alert comparison; human
benefit or intervention effectiveness; efficiency framed as merit; representativeness;
generalization; statistical inference of any kind; and any statement about student
behaviour or historical Cheers/ParkWise material.

## 15. Study 2B — model factor, separately preregistered

A comparison across model families (for example Llama versus the provider model used
here) is **not part of Study 2** and must not be mixed into the ON/OFF design. Varying
the model alongside orchestration would confound the two and make every difference
uninterpretable.

If pursued, it becomes **Study 2B** with its own preregistration written before any
outcome, its own authorization, its own denominators, and no pooling with Study 2 or
Study 1. Nothing in the present document authorizes, designs or anticipates a result
for Study 2B.

## 16. Changes from version 1

| § | Change |
|---|---|
| 3 | The single-varying-factor claim is withdrawn and replaced with system-comparison framing. |
| 4 | A "bound where" column distinguishes controls that exist in code from controls that do not. |
| 5 | A primary outcome is defined: blinded human-rubric quality, with judges, blinding procedure, a five-dimension rubric, an agreement threshold, and a `NOT_COLLECTED` fallback. Version 1 had no primary outcome. |
| 6 | The former outcome list becomes explicitly secondary and descriptive. |
| 7 | The alert-comparison prohibition is stated as absolute and extended to counts and proportions. |
| 8 | N = 4 is stated as a purposive feasibility sample; inference is prohibited by name. |
| 9 | Missingness, schema failure, partial output, zero-Q&A behaviour and technical failure are given predefined handling; outcome-dependent retry and model switching are prohibited. |
| 10 | The preflight claim that prompt differences arise only from orchestration is removed as unprovable; the all-zero fixture result is disclosed. |
| 11 | Separate authorization is required for each paid condition. |
| 13 | Replaced the stale six-control gap list with the controls now bound in the offline runner and the remaining provider/authorization gates. |
| 15 | New: Llama is confined to a separately preregistered Study 2B. |

## 17. What has not been done

No provider call, no paid run, no result, no repeat count chosen, no model frozen, no
judges recruited, no rubric anchors written out, no authorization requested. This
document is a design, not an outcome.
