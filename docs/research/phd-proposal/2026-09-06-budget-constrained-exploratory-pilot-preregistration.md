# Budget-constrained exploratory pilot — preregistration

**Study class: `BUDGET_CONSTRAINED_EXPLORATORY_PILOT`.**
**Status: `PREREGISTERED_NOT_EXECUTED`. Frozen 2026-09-06, before any provider call.**

**This is a new exploratory pilot. It is NOT a replication of Study 1, and it is not Study 1B.**
Its token and call limits are deliberately lower than Study 1's, so its outputs are produced under
a **different configuration** and are **not comparable with Study 1**, not poolable with it, and
not a check on it. Any sentence comparing a pilot number with a Study 1 number is a
claim-boundary violation.

It replaces nothing. Study 1B remains `BUDGET_BLOCKED_UNDER_FROZEN_PROTOCOL`: its frozen protocol
could not be conservatively bounded under USD 2.00 and was not run, not reduced, and not partially
executed.

---

## 1. What this pilot is for

One question, and only one:

> Under explicitly reduced call and token limits, does the AirTravel pipeline complete, and what
> does its inter-agent communication look like?

This is a **feasibility observation under constrained limits**. It is not a variance study, not a
replication, not a measurement of stability, and not a test of anything about Detector-v1's
correctness.

**Why the distinction matters.** Study 1B would have held the configuration identical and varied
only the provider's sampling, which is what makes a stability claim possible. This pilot changes
the configuration itself. Any difference observed here could be caused by the reduced limits
rather than by run-to-run variation, and the design cannot separate the two. That is an accepted
and stated limitation, not a flaw to be argued away later.

## 2. Frozen limits — fixed now, before any call

| Parameter | Value | Basis |
|---|---|---|
| Corpus | `text2uml_airtravel_253b26dc` | identical hash pin |
| Setting / cases | `cd_airtravel`, cases `01`–`04` | identical |
| Model | `gpt-5.6-luna` | identical |
| Temperature / seed | provider default, not overridden | identical |
| **Max output tokens** | **4,096** | **reduced from 16,384.** 2.16× the observed Study 1 average of 1,893 completion tokens per call |
| **Input reserve per request** | **8,000** | an upper bound, not an average: observed average prompt was 4,339 tokens |
| **Call cap per repeat** | **90** | 2.09× the 43 calls Study 1 actually used; protocol minimum is `4+3N` = 16 |
| **Repeats** | **exactly 3** | fixed now, not revisable after any outcome |
| **Budget ceiling** | **USD 2.00 total across all three repeats** | unchanged |
| Concurrency | 2 cases | identical |
| `MAX_QA_ROUNDS` | 10 | identical |
| Retries | at most 3 per call, counted against the call cap | identical |
| Request / run timeout | 180 s / 3,600 s | identical |
| Egress | restricted to the provider host | identical |
| Detector-v1 | byte-identical, unmodified, thresholds untouched | identical |
| Run identifiers | `PILOT-01`, `PILOT-02`, `PILOT-03` | assigned before execution |
| Output root | private, git-ignored, one directory per repeat | identical |

## 3. The bound, proven before run 1

The gate requires a conservative upper bound over **all** repeats, including every permitted
retry, computed and shown to fit **before** the first call.

| Term | Value |
|---|---|
| Per-request worst-case reserve | `(8,000 × $0.20/M) + (4,096 × $1.20/M)` = **$0.0065152** |
| Call cap per repeat | 90 |
| Repeats | 3 |
| **Total worst-case bound** | **$1.7591** |
| Ceiling | $2.00 |
| **Headroom** | **$0.2409** |
| **Verdict** | **FITS** |

This is a worst-case bound, not an extrapolation from a prior run. Every permitted call is priced
at the full reserve. The pilot refuses to start unless this check is recomputed and passes at
execution time.

## 4. Truncation — the principal risk, and it is instrumented

Reducing the output ceiling from 16,384 to 4,096 creates a risk that did not exist in Study 1: a
response longer than 4,096 tokens is **truncated by the provider**. Truncation would corrupt
exactly the fields Detector-v1 reads — the answer's confidence value and its evidence field — so
it cannot be allowed to pass silently.

Therefore, fixed now:

- every response's `finish_reason` is recorded; `finish_reason == "length"` is counted as a
  **truncated call**;
- the truncated-call count appears in every repeat receipt and in the pilot summary;
- **if any repeat records one or more truncated calls, that repeat's Detector-v1 output is
  reported as `TRUNCATION_AFFECTED` and is not presented as a communication observation**, because
  the signals were computed over material the provider cut short;
- truncation is **not** grounds for re-running the repeat, raising the cap, or discarding the
  repeat. It is reported.

## 5. Predefined handling

| Situation | Handling |
|---|---|
| A repeat completes | Reported with its counts and its truncated-call count |
| A repeat records truncated calls | Reported, and its detector output marked `TRUNCATION_AFFECTED` |
| A repeat produces zero Q&A episodes | Valid observation, `NO_EPISODE`, distinct from `NO_ALERT` |
| A repeat fails technically | Recorded in full with its cost, preserved, **not replaced**, does not halt the remaining repeats, excluded from the completed count |
| The call cap is reached mid-repeat | That repeat stops and is reported `STOPPED_AT_CALL_CAP`, partial and labelled partial |
| The ceiling is reached | The pilot stops and reports `STOPPED_AT_CAP` |
| A repeat cannot be started with full headroom | Refused as `NOT_STARTED_INSUFFICIENT_HEADROOM`; never started to be killed mid-way |

**No outcome-dependent adaptation.** The repeat count, limits, model, temperature, prompts,
corpus and detector cannot be changed after any outcome is observed. No repeat may be discarded,
re-run or re-ordered on the basis of its result.

## 6. Reported outcomes — descriptive only

Per repeat: episodes; complete episodes; lifecycle states; questions; answers; maximum round
index; route pairs and counts; answer-confidence distribution; evidence-field presence;
Detector-v1 classification over complete episodes only; signals fired; **truncated calls**; calls;
tokens; cost; elapsed time.

No mean, no confidence interval, no p-value, no accuracy, precision, recall or F1, no causal
effect, no generalization.

## 7. Denominators and pooling

Each repeat has its own denominator. Repeats are **never pooled** with each other into a single
denominator, and are **never pooled or compared** with the Study 1 accepted run, with Study 1B,
with Study 2, or with any fixture. The reduced limits make cross-study comparison invalid on its
face.

## 8. Claim boundary

**Permitted:** that the pipeline did or did not complete under the reduced limits; the per-repeat
counts above; the truncated-call count; the observed range across the three repeats, described as
a range and nothing more.

**Forbidden:** any comparison with Study 1; any stability or replication claim — the configuration
changed, so run-to-run variation and limit effects are confounded by design; alert correctness;
accuracy, precision, recall, F1; effectiveness; human benefit; causality; representativeness;
generalization; and any `VEGO_AI_ON`/`VEGO_AI_OFF` statement.

## 9. Provenance

Each repeat's receipt binds, at execution time: the execution-code SHA, the frozen-config hash,
the corpus hashes, its own event-log hash, the lifecycle summary, the output hashes, model
metadata, calls, tokens, cost, start and end time, the egress record, and the truncated-call
count.

### 9.1 Implemented preparation boundary

The preparation controller is `scripts/pilot_budget_constrained_runner.py`. It is deliberately
provider-agnostic and accepts only a client that declares `offline_only = True`; it does not
import an SDK, resolve a host, open a socket, read credentials, or provide a provider adapter.
Before the first fixture response is observable it writes one prospective binding for each of
`PILOT-01` … `PILOT-03`, including the frozen configuration hash, code hash, case-input hashes,
run identity, expected event-log path, and the zeroed accounting fields. It then reserves the
complete worst-case budget for each repeat before starting that repeat. A final private receipt
adds the event-log hash, lifecycle summary, output accounting, and truncation status.

Transport retries (at most three per request) are counted against the 90-call cap. A failed
repeat is recorded once and has `repeat_retry_count = 0`; the controller never restarts a
repeat or changes a limit after observing a response. `finish_reason == "length"` is counted per
call and marks the repeat `TRUNCATION_AFFECTED` with
`scientific_denominator_eligible = false`.

## 10. Gates — all must be green before any provider call

| # | Gate | Status |
|---|---|---|
| 1 | This preregistration committed and immutable | pending commit |
| 2 | Worst-case bound proven to fit USD 2.00 | **PASS** — $1.7591, §3 |
| 3 | Offline-only controller/preflight checks across all three repeat identities | **PASS** — no provider adapter or provider call |
| 4 | Codex independent approval of egress, call cap, **token cap**, budget cap, receipt self-binding and lifecycle handling | pending |
| 5 | Green CI on the exact execution head | pending |
| 6 | **Fresh one-time provider authorization**, naming model, ceiling and caps in the authorization text | **pending — not requested** |

Execution is prohibited until every row is green. A credential may not be used before then.

## 11. What has not been done

No provider call. No credential used or inspected. No repeat executed. No outcome observed. No
authorization requested. This document is a design.
