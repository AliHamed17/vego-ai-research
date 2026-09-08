# Study 1C — full eligible frame: preregistration

**Study class: `FULL_ELIGIBLE_FRAME_DESCRIPTIVE_RUN`.**
**Status: `PREREGISTERED_NOT_EXECUTED`. Frozen 2026-09-08, before any provider call.**

This is a **new descriptive run**. It is not a replication of the accepted Study 1 run, not
Study 1B, not the budget-constrained pilot, and not Study 2. It is **not poolable** with any of
them: the case count differs, so the run configuration differs, and every run keeps its own
denominator.

---

## 1. The one question

> Over the **complete eligible case frame**, what does inter-agent communication look like, and
> does Detector-v1 assign more than one class to real episodes?

The accepted run observed three episodes and placed all three in `STRONG_ALERT`. The close-out
recorded this as a property of that corpus rather than of the rule, because a deterministic
fixture check showed the rule does separate different inputs. That statement rests on a
denominator of three. This run enlarges the denominator on real material.

**A negative outcome is a result.** If every episode again lands in one class, that is reported
as the finding, not treated as a failure or a reason to change anything.

## 2. Why the whole frame, and why that removes a known limitation

`scripts/study1_case_selection.py` records a limitation: the pinned inventory contains a
deterministic eligibility predicate but **cannot identify which four of the twenty-one eligible
candidates the accepted run used**. The selection was a recorded purposive choice, not a
reproducible rule.

Running the **entire eligible population** dissolves that limitation rather than arguing around
it. When the frame is the population, there is no selection rule left to justify and no
selection bias left to bound. The eligibility predicate is copied verbatim from the existing
module and is not re-derived.

Twenty-one eligible cases are the outputs of twenty-one different generator models for the same
AirTravel domain description. Their sizes span 1,096 to 10,461 bytes. **Size is recorded as an
observable file property. It is not a quality measure, not a difficulty measure, and no claim is
made that larger files are worse models.**

## 3. Corpus provenance — re-acquired and verified, not asserted

| Item | Value |
|---|---|
| Upstream | `IlKaiser/text2uml`, GPL-3.0 |
| Pinned commit | `253b26dc704d523209a5cba79686f8f7fab57d63` |
| Archive SHA-256 pinned in `source-manifest.json` | `8cf82e2a…d8da701` |
| Archive SHA-256 on independent re-acquisition | **identical** |
| Inventory rows | 143 |
| Archive entries matched | 143 |
| Files verified byte-exactly | 22 of 22 (1 description + 21 cases) |
| Digest mismatches | 0 |

Every digest was frozen in the tracked inventory **before** this re-acquisition. A matching
digest can therefore confirm provenance but cannot manufacture it. The materialiser refuses to
write a runtime root unless the archive digest and all per-file digests match, and re-hashes
every file after writing.

## 4. Frozen parameters — fixed now, before any call

| Parameter | Value | Relation to the accepted run |
|---|---|---|
| Corpus | `text2uml_airtravel_253b26dc` | identical |
| Setting | `cd_airtravel` | identical |
| **Cases** | **all 21 eligible** | **changed from 4** |
| Model | `gpt-5.6-luna` | identical |
| Temperature / seed | provider default, not overridden | identical |
| Max output tokens | 16,384 | identical |
| Input reserve per request | 8,000 | identical |
| `MAX_QA_ROUNDS` | 10 | identical |
| Concurrency | 2 cases | identical |
| Request timeout | 180 s | identical |
| **Run timeout** | **10,800 s** | **changed from 3,600 s** — operational only, for a 5.25× larger frame |
| **Call cap** | **272** | changed from 326; budget-derived, see §5 |
| **Budget ceiling** | **USD 5.80** | changed from 10.00 |
| Egress | restricted to `api.openai.com` | identical |
| Detector-v1 | byte-identical, thresholds untouched | identical |
| Run identifier | `FULLFRAME-01` | assigned before execution |
| Output root | private, git-ignored | identical |

The budget, egress and credential machinery are **imported from the frozen harness**, not
reimplemented, so those guarantees are the same objects that governed the accepted run.

## 5. The two bounds, both proven before call 1

| Term | Value |
|---|---|
| Per-request worst-case reserve `(8,000 × $0.20/M) + (16,384 × $1.20/M)` | **$0.0212608** |
| Call cap | 272 |
| **Reserve-based worst case** | **$5.7830** |
| Authorized ceiling | $6.00 |
| **Headroom** | **$0.2170** |
| **Verdict** | **FITS** |

A second, independent brake applies at run time: the budget guard refuses any request when
`actual spend so far + one worst-case reserve > USD 5.80`. Actual spend therefore cannot exceed
the ceiling even if every call were maximal. The run refuses to start unless both checks pass.

### 5.1 Why 272 and not a guess

The cap is derived from **measured control flow**, not from an extrapolated cost. An offline
preflight ran the protected orchestrator against the deterministic local fake at frame sizes
4, 8, 14 and 21, contacting no provider:

| Cases | Structural calls |
|---|---|
| 4 | 46 |
| 8 | 82 |
| 14 | 136 |
| 21 | 199 |

The fit is exact: `calls = 10 + 9N`. At N = 21 the structural requirement is 199 calls. The cap
of 272 provides 1.37× that figure for live conversational depth, which the fake cannot simulate
because it converges in one round. **This is a floor on structure, not a forecast of cost.**

For reference only, and not as a bound: the accepted run spent $0.00314 per call in actuals,
6.8× below the worst-case reserve.

## 6. Predefined handling — fixed now

| Situation | Handling |
|---|---|
| The run completes | Reported with all counts in §7 |
| Any call returns `finish_reason == "length"` | Counted as a truncated call, reported in the receipt; affected episodes marked `TRUNCATION_AFFECTED` and not presented as communication observations |
| Zero Q&A episodes | Valid observation, `NO_EPISODE`, distinct from `NO_ALERT` |
| The call cap is reached | Run stops, reported `STOPPED_AT_CAP`, labelled partial |
| The budget ceiling is reached | Run stops, reported `STOPPED_AT_CAP`, labelled partial |
| A technical failure occurs | Recorded in full with its cost, preserved, **not replaced** |
| An episode is incomplete | `EXCLUDED` by the frozen rule, counted, never silently dropped |

**No outcome-dependent adaptation.** The frame, limits, model, temperature, prompts, corpus and
detector cannot be changed after any outcome is observed. The run is executed **once**. It may
not be repeated, discarded, re-ordered or extended on the basis of its result. If it fails, the
failure is reported and no substitute run is authorized under this preregistration.

## 7. Reported outcomes — descriptive only

Episodes; complete episodes; lifecycle states; questions; answers; maximum round index; directed
route pairs and counts; answer-confidence distribution; evidence-field presence and length
distribution; Detector-v1 classification over complete episodes only; signals fired; truncated
calls; calls; tokens; cost; elapsed time; per-case episode yield.

No mean-as-estimate, no confidence interval, no p-value, no accuracy, precision, recall or F1,
no causal effect, no generalization.

## 8. Denominators and pooling

This run has **one denominator: its own complete episodes**. It is never pooled with the accepted
Study 1 run, with Study 1B, with the budget-constrained pilot, with Study 2, or with any
engineering fixture. Where the accepted run's values appear beside this run's, they appear as
**two separately labelled runs on separate denominators**, never summed and never averaged.

## 9. Claim boundary

**Permitted:** that the pipeline did or did not complete over the full eligible frame; the
per-run counts in §7; the truncated-call count; which Detector-v1 classes occurred and with what
frequency **in this run**; the observed per-case episode yield; the cost.

**Forbidden:** alert correctness; accuracy, precision, recall, F1; effectiveness; human benefit;
causality; representativeness; generalization to other corpora, settings or models; any
`VEGO_AI_ON`/`VEGO_AI_OFF` statement; any claim that a case's file size indicates its quality;
any pooling or averaging with another run; and any claim that this run replicates, confirms or
refutes the accepted Study 1 run.

## 10. Provenance bindings closed by this run

The close-out records four provenance gaps in the accepted run's receipt, removable only by a new
authorized run whose receipt self-binds them. This run's receipt binds, at execution time:

1. its own event-log SHA-256;
2. a lifecycle summary (episodes opened, terminated, questions, answers);
3. the execution-code SHA-256 of both harness files, plus the reviewed head;
4. `MAX_QA_ROUNDS` as a recorded value rather than an implicit harness constant;
5. **a privacy-safe per-call ledger**, so `outbound_requests` becomes independently
   recomputable rather than receipt-asserted — the fifth gap, recorded as gap 3 in the close-out.

The ledger records index, token counts, `finish_reason`, latency, cost and the model string the
provider reported. **It records no prompt, no response, no message content and no credential.**

This closes those gaps **for this run only**. It does not retroactively upgrade the accepted
run's provenance, and supervisor acknowledgement does not either.
