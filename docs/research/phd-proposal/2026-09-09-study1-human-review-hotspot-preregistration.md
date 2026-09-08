# Study 1 — human-review hotspot baseline: preregistration

**Study class: `HUMAN_REVIEW_HOTSPOT_BASELINE`.**
**Status: `PREREGISTERED_NOT_EXECUTED`. Frozen 2026-09-09, before any provider call and before
any output of this study was observed.**

Machine-readable freeze record: [`study1-hotspot-manifest.json`](study1-hotspot-manifest.json).
Everything below that can be checked mechanically is in that file; this document states the
reasoning.

---

## 1. The primary question

> **Among complete Q&A episodes, how well does Detector-v1 prioritize episodes that blinded human
> raters independently judge as requiring human review?**

The outcome of interest is **not** whether the AI was correct. It is whether the detector
**reduces review workload while retaining the episodes humans judge worth reviewing**.

### 1.1 The primary outcome cannot be produced without human raters

The question is defined against independent human judgement. **Two blinded raters and the
adjudication rule in §6 are a precondition, not a nicety.** If they do not exist, the primary
outcome is reported `NOT_AVAILABLE` and **no substitute is permitted** — not a model-generated
label, not the author's own judgement, not a proxy signal, and not a heuristic. This is fixed now
so that a later absence of raters cannot be quietly filled.

The project record is that independent labelling has stood at 0 of 24 for months (IE-03, IE-09).
This study is designed so that the moment two raters are available, the analysis runs unchanged.

### 1.2 What is preserved from the existing record

- The historical AirTravel result is **ARCHIVAL / RETROSPECTIVE DESCRIPTIVE EVIDENCE**: four
  purposively selected public-external cases, three complete Q&A episodes.
- **Detector-v1 is episode-level and reporting-only. It does not create a human queue.**
- **Agent-4's queue mechanism is a different mechanism** and is never conflated with Detector-v1.
- No accuracy, benefit, superiority, causal or ON/OFF claim follows from anything already held.

## 2. Corpus and case selection — frozen before any output

| Item | Value |
|---|---|
| Corpus | `text2uml_airtravel_253b26dc` |
| Pinned upstream commit | `253b26dc704d523209a5cba79686f8f7fab57d63` |
| Archive SHA-256 | `8cf82e2a…d8da701`, independently re-acquired and reproduced byte-exactly |
| Eligible frame | **21 cases**, by the predicate already recorded in `study1_case_selection.py` |
| Sample size | **6** |
| Selection rule | deterministic seeded shuffle of the full eligible frame, take the first 6, sort by path |
| Seed | **20260909**, fixed in code before the draw |

**Selected cases** (all 21 eligible are listed in the manifest):

`result_one_Qwen_Qwen3.5-4B.txt` · `result_one_gpt-3.5-turbo.txt` · `result_one_gpt-5.2.txt` ·
`result_one_meta-llama_Llama-3.2-3B-Instruct.txt` ·
`result_one_mistralai_Mistral-7B-Instruct-v0.3.txt` · `result_one_o3-mini.txt`

The draw depends only on the seed and the pinned inventory. **It cannot depend on predicted or
observed alert status**, and anyone can recompute it. Two of the six are large outputs (7,161 and
7,182 bytes) and four are compact; that spread is a consequence of the draw, not a choice, and
file size is recorded as an observable property, never as a quality or difficulty measure.

## 3. Protocol — frozen

| Parameter | Value |
|---|---|
| Model | `gpt-5.6-luna` |
| Temperature / seed | provider default, not overridden |
| Prompts | unmodified protected runtime prompts; **no prompt is authored for this study** |
| Max output tokens | 16,384 |
| Input reserve per request | 8,000 |
| `MAX_QA_ROUNDS` | 10 |
| Concurrency | 2 cases |
| Request / run timeout | 180 s / 10,800 s |
| Retry rule | at most 3 per call, **only** for a documented transport or provider failure before a valid response; every retry counts against the call cap and the budget and is recorded |
| **Case cap** | **6** |
| **Call cap** | **240** |
| **Run count** | **exactly 1** |
| Egress | restricted to the provider host |
| Detector-v1 | byte-identical, thresholds untouched, SHA-256 pinned in the manifest |

## 4. Budget — pessimistic whole-study reservation

The gate is that **USD 6.00 must fund the entire frozen protocol under a pessimistic
reservation**, computed before the first call, with every permitted call — including retries and
failed calls — priced at the full worst-case reserve.

| Term | Value |
|---|---|
| Per-request worst case `(8,000 × $0.20/M) + (16,384 × $1.20/M)` | **$0.0212608** |
| Call cap × runs | 240 × 1 |
| **Whole-study reservation** | **$5.102592** |
| Ceiling | $6.00 |
| **Headroom** | **$0.897408** |
| **Verdict** | **FITS — not `BUDGET_NO_GO`** |

The cap of 240 allows 40 calls per case. For calibration only, and not as a bound: a prior
21-case run completed at 4.67 calls per case, and a prior run in the verbose regime was still
running at 22.08 calls per case when it stopped at its cap, so that figure is itself a lower
bound. Forty per case is roughly 1.8× that lower bound.

**Stop rule.** When the call cap or the ceiling is reached the run stops, is reported
`STOPPED_AT_CAP` and **partial**, and is **never re-run and never replaced**. A technical failure
is preserved and reported with its cost; it is never deleted and never re-run to improve a
result. Nothing — model, prompts, thresholds, sample, token cap, stopping rule — may change after
any output is seen.

## 5. Why one new run, given that episodes already exist

Fourteen complete episodes with retrievable Q&A text already exist from prior runs and are
**ARCHIVAL / RETROSPECTIVE DESCRIPTIVE EVIDENCE**. A new run is authorized here for reasons that
adding episodes to a rating pile would not justify on its own:

1. It is the only way to obtain **PROSPECTIVE EMPIRICAL EVIDENCE** for pipeline reliability
   (Table A), because that requires generation under a preregistration that predates it.
2. It supplies an independent test of the one quantity that decides the workload question:
   **whether any episode is ever `NO_ALERT`.** Across all 25 episodes observed to date, the count
   is zero. A further independent run returning zero again is substantive evidence about the
   detector's operating point; a run returning one would change the picture.

**More episodes are not treated as stronger evidence.** The archival and prospective sets keep
separate denominators and are never pooled.

## 6. Human validation — frozen rubric

Redacted episode cards are produced from the event log and Q&A history.

**Shown to raters:** question text; answer text; **evidence presence and length, not the evidence
text**; the directed route as asking agent and answering agent; round count and question count.

**Withheld from raters:** the Detector-v1 classification and every signal name; **the per-answer
confidence label**; the run, case and generating-model identifiers; and any other rater's
responses.

The confidence label is withheld because it is Detector-v1's dominant input — showing it would
make the human judgement partly a readback of the detector rather than an independent judgement.
The cost is that raters see less than a live operator would, and that is recorded as a limitation
rather than argued away.

**Two independent raters** answer exactly three questions per card:

| | Question | Options |
|---|---|---|
| R1 | Is this episode worthy of human review? | Yes · No · **Insufficient information** |
| R2 | Why? | Low confidence · Missing evidence · Repeated clarification · Non-convergence · Other *(multiple permitted)* |
| R3 | What action would be appropriate? | Verify · Clarify · Revise guideline · No action *(exactly one)* |

**`Insufficient information` is a distinct outcome and is never merged into `No`.**

**Adjudication, fixed now:** both Yes → `HUMAN_REVIEW_WORTHY`; both No → `NOT_WORTHY`; both
Insufficient → `INSUFFICIENT`; anything else → `DISAGREEMENT`. A `DISAGREEMENT` is resolved
**only** by a third supervisor-authorized adjudicator, never by the study author, and is reported
as `DISAGREEMENT` until that adjudication exists.

**Review time** is reported only if raters actually record time per card. Otherwise minutes saved
is `NOT_AVAILABLE` and **may not be estimated**.

## 7. Planned analysis

**A — pipeline reliability.** Selected cases, completed cases, complete episodes, incomplete
technical episodes, calls, cost, elapsed time, termination states.

**B — detector-to-human agreement.** Alert rate; human-review-worthy rate; confusion matrix of
alert or no-alert against Yes / No / Insufficient; precision and recall **only** when denominators
are valid, and labelled **exploratory** at this sample size; redacted false-positive and
false-negative cards.

**C — operational baseline.** All-episodes review workload; detector-prioritized review workload;
proportion of human-worthy episodes retained by the prioritized set; review minutes saved **only**
if measured; provider cost per completed case and per human-confirmed review-worthy episode.

**D — robustness.** Per-case results, per-run results, route distribution, termination
distribution.

**The prioritized set is defined now as the `STRONG_ALERT` episodes.** This is fixed before
results because Detector-v1's alert rate *including* `WEAK_ALERT` has been 1.0 on every episode
observed to date, which would make an alert-versus-no-alert split degenerate and the workload
comparison vacuous. The one preregistered sensitivity analysis is the same tables recomputed with
the prioritized set defined as `STRONG_ALERT` **or** `WEAK_ALERT`. No other sensitivity analysis
is permitted.

## 8. Evidence classes

| Label | Applies to |
|---|---|
| **PROSPECTIVE EMPIRICAL EVIDENCE** | the single run executed under this manifest |
| **ARCHIVAL / RETROSPECTIVE DESCRIPTIVE EVIDENCE** | the accepted AirTravel run and the earlier full-frame runs |
| **ENGINEERING-ONLY FIXTURE** | the offline fake-provider preflight and any fixture-derived label |
| **NOT_AVAILABLE** | every outcome requiring human raters, until those raters exist |

## 9. Claim boundary

**Forbidden**, whatever the results show: that any alert was correct; accuracy, precision, recall
or F1 as a confirmatory result; effectiveness, human benefit or workload reduction without
measured rater time; causality or any `VEGO_AI_ON`/`VEGO_AI_OFF` advantage; representativeness or
generalization; that Detector-v1 creates or feeds a human queue; that Agent-4's queue and
Detector-v1 are the same mechanism; pooling or averaging runs of differing configuration; and
that a larger episode count is stronger evidence unless it was frozen before outputs and passed
these gates.

**Permitted:** the counts in Table A on their own denominator; the alert-class distribution; the
Table B and C quantities **once and only once** two independent rater sets exist; and the
statement that a required input is `NOT_AVAILABLE`.
