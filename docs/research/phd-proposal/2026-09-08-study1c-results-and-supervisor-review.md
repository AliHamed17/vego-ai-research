# Study 1C — results, baselines, and review against the supervisors' directives

**Date:** 2026-09-08 · **Audience:** Iris Reinhartz-Berger and Arnon Sturm.

Provider-backed runs over the **complete eligible case frame**, plus six offline instruments.
Every number is recomputed from a persisted event log, not copied from a receipt. Detector-v1,
its thresholds and all preregistrations are unmodified. **No number here says an alert was
correct**: no ground-truth labels exist for this corpus, so accuracy, precision, recall and F1
are not computed and are not computable.

---

## 1. Headline

At a denominator of 3 episodes, five trivial baselines — including "always alert" — reproduced
Detector-v1's output exactly, and the rule looked indistinguishable from flagging everything.

**At a denominator of 11 episodes over the full eligible frame, no baseline reproduces it.** The
composite rule is behaviourally distinct, and it assigns **two** classes rather than one.

The earlier "all episodes fall in one class" observation was **an artefact of the denominator**,
not a property of the rule. That correction is the main scientific result of this work.

**But the review load is still 1.0.** Every episode in both runs is flagged as STRONG or WEAK, and
no episode is `NO_ALERT`. The D6 dosage target of load ≤ 0.5 remains unmet, and re-scoring under
every round bound from 1 to 10 does not move it.

## 2. What was authorized, and what it bought

| | |
|---|---|
| Authorized | USD 6.00 |
| Run 1 (`FULLFRAME-01`) actual spend | **USD 0.360827** |
| Run 1 calls | 98 of a 272 cap |
| Run 1 tokens | 1,026,303 |
| Truncated calls (`finish_reason == "length"`) | **0** |
| Blocked egress attempts | 0 |
| Preregistrations frozen before any call | 2 |
| Offline instruments added | 6 |
| Detector-v1 changes | **0** |

## 3. Corpus provenance — strengthened, not merely restated

The corpus was **independently re-acquired** from the pinned upstream commit and verified against
digests frozen in the tracked inventory long beforehand.

| Check | Result |
|---|---|
| Archive SHA-256 vs `source-manifest.json` | **reproduced byte-exactly** |
| Inventory rows vs archive entries | 143 vs 143 |
| Files verified (1 description + 21 cases) | **22 of 22** |
| Digest mismatches | **0** |

Because the digests predate the re-acquisition, a match can confirm provenance but cannot
manufacture it.

### 3.1 A selection limitation removed at the root

`study1_case_selection.py` records that the pinned inventory **cannot identify which four** of the
twenty-one eligible candidates the accepted run used; the choice was purposive, not a
reproducible rule. Study 1C runs the **entire eligible population**. When the frame is the
population there is no selection rule left to justify and no selection bias left to bound.

## 4. Study 1C run 1 — descriptive results

`FULLFRAME-01`, `TECHNICAL_SUCCESS`, N = 21, **denominator 11 complete episodes, 0 excluded.**

| Quantity | Full frame (N=21) | Accepted run (N=4) |
|---|---|---|
| Complete episodes | **11** | 3 |
| Questions / answers | 29 / 29 | 44 / 44 |
| Maximum round index | **2** | 10 |
| Terminations | `CONVERGED` 11 | `CONVERGED` 2, `TERMINATED_MAX_ROUNDS` 1 |
| Answer confidence | High 7, Low 10, Medium 12 | High 3, Low 16, Medium 25 |
| Evidence length (min / median / max) | 44 / 122 / 613 | 38 / 62 / 540 |
| Zero-length evidence | 0 | 0 |
| **Detector-v1** | **STRONG 7, WEAK 4, NO 0** | STRONG 3 |
| Signals fired | S1 7, S2 6, S6 3 | S1 3, S2 2, S6 2, S7 1 |
| Review load | 1.0 | 1.0 |

**These two columns are two runs on two denominators. They are placed side by side, never summed
and never averaged.** The case count differs, so the configuration differs; pooling them would be
invalid on its face.

Directed routes differ completely between the runs. The accepted run was dominated by one
asking–answering pair (agent4 asking, agent2 answering, 39 questions) belonging to its single
long episode. The full frame shows agent3 asking agent1 (14) and agent3 asking agent2 (13), with
no agent4 traffic at all.

### 4.1 Provenance bindings closed

Run 1's receipt self-binds its event-log digest, a lifecycle summary, the execution-code digests
of both harness files, and `MAX_QA_ROUNDS`. It also carries a **privacy-safe per-call ledger** of
98 rows whose count matches the budget guard's independently maintained counter, so
`outbound_requests` is now **independently recomputable** rather than receipt-asserted — the gap
recorded as item 3 in the close-out. The ledger records token counts, finish reasons, latency and
cost; it records no prompt, no response and no credential.

This closes those gaps **for this run only**. It does not retroactively upgrade the accepted run.

## 5. Baselines — what the frozen rule adds over trivial alternatives

With no labels, correctness is not measurable. What *is* measurable is **what each rule selects**.

| | Accepted run (n=3) | Full frame (n=11) |
|---|---|---|
| Baselines identical to Detector-v1 | **5** | **0** |
| Best exact three-class agreement by any baseline | 1.00 | **0.64** |
| Signals whose removal changes nothing | S2, S3, S6, S7 | S3, S6, S7 |
| Signals that contribute | S1 only | **S1 (7 episodes) and S2 (3)** |
| Reachable signal patterns visited | 3 of 24 | **6 of 24** |

At n=3 the rule was behaviourally a one-signal rule and `ALWAYS_ALERT` matched it exactly. At
n=11 the best any baseline achieves is 0.64 exact agreement, so the rule differs from every
trivial alternative on more than a third of episodes.

**The agreement numbers are reported with their chance band, because without it they mean
nothing.** Detector-v1's binary flag rate is 1.0 in both runs, so a coin that always says "alert"
also achieves binary agreement 1.0 and Cohen's kappa is **undefined**, not 1.0. This is why the
three-class agreement, not the binary one, carries the information here.

S3 never fired in either run — every answer carried a non-empty evidence field. S3 is
nevertheless **reachable**: `_ref(None)` returns `None`, and the deterministic fixture envelope
fires it. It is inert on this data, not dead code.

## 6. The instrument's operating characteristic — and a prediction it made

Detector-v1 fires `STRONG_ALERT` if **any** answer is `Low`. Any-of rules over a sequence fire
more readily the longer the sequence, whatever it contains.

At the accepted run's `Low` rate of 0.364:

| Episode length | 1 | 2 | 5 | 10 | 39 |
|---|---|---|---|---|---|
| P(`STRONG_ALERT`) | 0.36 | 0.60 | 0.90 | 0.99 | 1.00 |

The rule **saturates at 7 answers**; its separation window is lengths **1 to 3**.

This model was computed **before** the full-frame run and predicted that separation is only
possible for short episodes. The full-frame episodes average **2.6 answers** with a maximum round
index of 2 — inside the window — and the rule **did** separate, 7 STRONG against 4 WEAK. The
accepted run's episodes were 1, 4 and 39 answers, two of them in the saturated zone, and it did
not separate.

The model is a property of the rule under an explicit independence assumption the data does not
verify. Its agreement with the outcome is a consistency check, **not** confirmation of the
assumption and not evidence about any alert's correctness.

## 7. Four escalation mechanisms, four different answers

| Mechanism | Unit | Full frame (21 cases) |
|---|---|---|
| Detector-v1 | Q&A episode | flags **8 of 21** cases, and all 11 episodes |
| Fragment severity and label | uncovered fragment | records domain mistakes in **15 of 21** cases |
| `requires_human_review` | variability pattern | **false on all 25** patterns |
| **The human-review queue** | queued item | **0 items** |

The fourth is the one that matters operationally: it is the only mechanism whose output would
actually reach a person, and across all 21 cases **it is empty**. Detector-v1 flags every episode
it can see; the queue that a reviewer would open contains nothing. The accepted run produced no
queue artefact at all, so this is reported for the full-frame run only.

Case-level co-occurrence:

| | Count |
|---|---|
| Both flag | 6 |
| Detector-v1 only | 2 |
| Fragment stage only | **9** |
| Neither | 4 |

**The structural finding, now at scale: Detector-v1 is silent on 13 of 21 cases**, because those
cases produced no Q&A episode. Nine of them carry domain-mistake labels from the coverage stage —
case 09 has six, cases 06 and 20 have five and four. The detector's coverage is conditional on
the pipeline having chosen to ask a question, a decision made upstream of it.

None of the four is ground truth. Agreement would not make any of them correct, and disagreement
does not show any of them wrong. This is co-occurrence, reported as co-occurrence.

## 8. Review against the recorded directives

| Directive | What this work contributes | Status |
|---|---|---|
| **D6** — dosage, load target ≤ 0.5, recorded unmet | Load is now measured on two runs: **1.0 in both**. Re-scoring under every round bound from 1 to 10 leaves it at 1.0. At bound 1 the split shifts to 8 STRONG / 3 WEAK, but nothing becomes `NO_ALERT`. | **Target missed on all evidence**, measured rather than assumed |
| **D10** — bounded interaction, two-round pilot candidate | The full-frame run *already* behaves like a bounded regime — maximum round index 2 — and that is precisely where the rule separates. But a bound does not reduce load, and it cannot: an episode cut off at the bound terminates `TERMINATED_MAX_ROUNDS`, which is itself a strong signal. | Quantified; the two-round candidate improves *separation*, not *load* |
| **D2** — intervene early, not only post-Agent-4 | §7 shows the gap concretely: 13 of 21 cases are never assessed by the detector because they never triggered a question, 9 of them carrying domain-mistake labels — and the queue a reviewer would actually open is empty. | New evidence, at frame scale |
| **D5** — the human expert is real, never simulated | No human judgement was simulated, requested or synthesised. The resampled curve in §6 is labelled `ANALYTIC_MODEL_NOT_OBSERVATION`. | Respected |
| **IE-09** — macro-F1 as primary classification metric | Not computed and **not computable**: it needs the independent labels still at 0 of 24. | Correctly unavailable |
| "A trigger count is not a verified error count" | Every instrument refuses to compute accuracy and says so in its own output and command-line help, enforced by tests. | Respected |

## 9. Claim boundary

**Permitted.** The corpus provenance verification; the per-run counts, each on its own
denominator; which Detector-v1 classes occurred and how often in each run; that the rule assigned
more than one class in the full-frame run and one class in the accepted run; the baseline
agreement results with their chance band; the rule's reachable-space distribution and operating
characteristic as properties of the rule under stated assumptions; the co-occurrence crosstab in
§7; the measured review load; the run costs.

**Forbidden.** Alert correctness; accuracy, precision, recall, F1; effectiveness; human benefit;
causality; representativeness; generalization to other corpora, settings or models; any
`VEGO_AI_ON`/`VEGO_AI_OFF` statement; any claim that a case's file size indicates its quality; any
claim that one escalation mechanism is more nearly right than another; any pooling or averaging
of runs that differ in configuration; and any claim that the full-frame run replicates, confirms
or refutes the accepted run — it does none of those, because its configuration differs.

## 10. What remains unknown, and what would close it

1. **Whether any alert was correct.** Unresolvable from this data at any sample size. It needs the
   independent human labels recorded as 0 of 24 under IE-03/IE-09, which only a person can supply.
   This is the single binding constraint on every quality verdict in the thesis.
2. **Whether cases that produce no episode should be escalated.** §7 shows the question is live
   for 13 of 21 cases; nothing here answers it.
3. **Why no episode is ever `NO_ALERT`.** The rule reserves that class for a single one of its 24
   reachable signal patterns, and the corpus has not visited it.
4. **Run-to-run variation.** A stability repeat under byte-identical configuration is
   preregistered and executed; two observations bound nothing and support no variance estimate.
