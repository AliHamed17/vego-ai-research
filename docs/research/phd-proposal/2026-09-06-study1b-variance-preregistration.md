# Study 1B preregistration — repeat-run variance of Detector-v1 on AirTravel

**Study class: `EXPLORATORY_POST_STUDY1_VARIANCE_REPLICATION`.**

This is an exploratory post-hoc replication that assesses run-to-run variability of the fixed
AirTravel protocol. It does **not** upgrade the original Study 1 run to prospective provenance,
and it does **not** test alert correctness, effectiveness, human benefit, accuracy or
generalization.

**Status: `PREREGISTERED_NOT_EXECUTED`.**
**Frozen 2026-09-06, before any repeat run has been executed and before any repeat outcome has
been observed.**

This document exists so that the repeat runs cannot be read as re-running until the result
changes. Everything that could be chosen to fit an outcome is fixed here, in advance.

---

## 1. Why this study exists, and what would make it illegitimate

Study 1 executed **one** provider-backed run. It produced `STRONG_ALERT` 3, `WEAK_ALERT` 0,
`NO_ALERT` 0 on a denominator of 3 complete episodes. From a single run **nothing can be said
about whether that outcome is stable**: it may be a property of the corpus and the frozen rule,
or an artifact of one sampling of a non-deterministic model.

That is the gap this study fills, and the only gap it fills.

**What would make this illegitimate:** running repeats *because the first result was
uninteresting*, then reporting whichever run reads best; or choosing the number of repeats after
seeing them; or stopping early once a repeat produced a different classification. All three are
prohibited below and the prohibition is what makes the repeats worth anything.

## 2. Research question

> Holding corpus, cases, model, prompts, configuration and the frozen Detector-v1 rule constant,
> how much does the observed classification vary across independent repeat executions?

Descriptive. It asks about **stability of the measurement**, not about correctness, quality or
benefit.

## 3. Frozen before any repeat is executed

| Parameter | Value |
|---|---|
| Number of repeats | **exactly 5** — fixed now, not revisable after any outcome |
| Corpus | `text2uml_airtravel_253b26dc`, identical hash pin to Study 1 |
| Setting / cases | `cd_airtravel`, cases `01`–`04`, identical |
| Model | `gpt-5.6-luna`, identical to the Study 1 accepted run |
| Temperature / seed | provider default, not overridden — this is the source of variation under study |
| Max output tokens | 16,384 |
| Concurrency | 2 cases |
| `MAX_QA_ROUNDS` | 10 |
| Request cap | 326 outbound requests per repeat |
| **Budget cap** | **USD 2.00 total across all 5 repeats**, hard stop with per-request worst-case reservation |
| Egress | restricted to the provider host |
| Detector-v1 | byte-identical, unmodified, thresholds untouched |
| Run identifiers | `VARIANCE-01` … `VARIANCE-05`, assigned before execution |
| Output root | private, git-ignored, one directory per repeat |

## 4. Reported outcomes — all descriptive

Per repeat, and then across the five:

- episodes observed; complete episodes; `INCOMPLETE_TECHNICAL` excluded;
- lifecycle states (`CONVERGED` / `TERMINATED_MAX_ROUNDS`);
- questions, answers, maximum round index;
- directed route pairs and their counts;
- answer-confidence distribution;
- evidence-field presence;
- **Detector-v1 classification counts** — the primary descriptive outcome;
- signals fired (S1, S2, S3, S6, S7);
- calls, tokens, cost, elapsed time.

**Stability is reported as the observed range and the per-repeat table, never as a mean with a
confidence interval.** With five repeats and a denominator of three episodes, no inferential
statistic is computed.

## 5. Predefined handling — fixed now

| Situation | Handling |
|---|---|
| A repeat produces a different classification distribution | **Reported as-is.** This is the finding, not a problem. It is not grounds for a sixth repeat. |
| A repeat produces zero Q&A episodes | Valid observation. The repeat stays in the denominator with `NO_EPISODE`, distinct from `NO_ALERT`. |
| A repeat fails technically (transport, timeout, schema) | Reported as a technical failure with its cost disclosed, excluded from the classification denominator only, **not replaced**. The remaining repeats are reported as fewer than five. |
| The USD 2.00 ceiling is reached | The study stops immediately and reports `STOPPED_AT_CAP` with however many repeats completed. Partial results are published as partial. |
| Every repeat gives an identical result | Reported plainly. "No variation observed across five repeats" is a legitimate and useful outcome. |

**No outcome-dependent adaptation.** The repeat count cannot be increased or decreased after any
outcome is observed. The model, temperature, prompts, corpus and detector cannot be changed. No
repeat may be discarded, re-run or re-ordered on the basis of its result. Transport-level retries
are capped at 3 per call and counted against the request cap.

## 6. Denominators and pooling

Each repeat has its **own** denominator. Repeats are **never pooled** into a single denominator,
and are never pooled with the Study 1 accepted run, with Study 2, or with any fixture. The
Study 1 accepted run remains the single reported descriptive result; these repeats are reported
beside it as a separate stability observation.

## 7. Claim boundary

**Permitted:** the per-repeat values above; the observed range across repeats; a statement that
the classification did or did not vary under repetition, on this corpus, with this model, at
this configuration.

**Forbidden:** alert correctness; accuracy, precision, recall, F1; that stability implies
correctness — a consistently wrong measurement is also stable; human benefit; effectiveness;
causality; representativeness; generalization to other corpora, models or settings; and any
comparison with `VEGO_AI_OFF`, which is a different study.

## 8. Provenance

Each repeat's receipt binds, **at execution time**, its own event-log hash, its lifecycle
summary, and the execution-code SHA — the three fields the Study 1 accepted run's receipt did
not bind. If those bindings are present and verify, these repeats carry **prospective**
provenance, unlike the Study 1 accepted run. That difference must be stated wherever the two are
shown together, and it does **not** retroactively upgrade the Study 1 run.

## 9. What has not been done

No repeat has been executed. No repeat outcome has been observed. `OPENAI_API_KEY` was not
present in the execution environment when this document was frozen. This document is a design.

---

## Amendment A — 2026-09-06, before any execution

Recorded before any provider call. The design below is unchanged; these are the study class
label required by the sponsor and the outcome of the pre-execution budget gate.

**A1. Study class.** `EXPLORATORY_POST_STUDY1_VARIANCE_REPLICATION`, as stated in the header.

**A2. Global reservation gate — FAILED.** The gate requires a conservative upper bound for all
five repeats combined, including every permitted retry, to fit the ceiling before run 1 starts.

| Term | Value |
|---|---|
| Per-request worst-case reserve | `(8,000 × $0.20/M) + (16,384 × $1.20/M)` = **$0.0212608** |
| Permitted requests per repeat | 326 (retries counted against this cap) |
| Repeats | 5 |
| **Conservative upper bound** | **$34.6551** |
| Ceiling | $2.00 |
| **Result** | **`BUDGET_INSUFFICIENT_FOR_FROZEN_FIVE_REPEAT_PROTOCOL`** |

The largest per-repeat request cap that fits $2.00 across five repeats is **18**, against a
protocol minimum of `4 + 3N` = **16** calls. Any inter-agent Q&A at all would breach the ceiling,
so the frozen protocol cannot be conservatively bounded under $2.00.

For reference only, and explicitly **not** the bound the gate uses: the accepted Study 1 run cost
$0.134972 over 43 calls, so five repeats would realistically cost about $0.67. The guard cannot
know that in advance, which is the point of a worst-case reservation.

**No partial study was run.** Per the frozen design, five repeats are executed or none are.

**A3. Credential.** `OPENAI_API_KEY` was absent from the execution environment at gate time:
`CREDENTIAL_NOT_AVAILABLE`. No provider call was attempted, and no credential was inspected,
requested or substituted.

Either blocker alone is sufficient to prevent execution. Both were present.
