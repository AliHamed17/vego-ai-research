# Study 1C — results, baselines, and review against the supervisors' directives

**Date:** 2026-09-08 · **Audience:** Iris Reinhartz-Berger and Arnon Sturm.

Two provider-backed runs over the **complete eligible case frame**, plus six offline instruments.
Every number is recomputed from a persisted event log, not copied from a receipt. Detector-v1,
its thresholds and all preregistrations are unmodified. **No number here says an alert was
correct**: no ground-truth labels exist for this corpus, so accuracy, precision, recall and F1 are
not computed and are not computable.

---

## 1. Headline

**Whether Detector-v1 separates episodes into more than one class is not a stable property of the
rule. It changed between two runs whose configuration was byte-identical.**

| | Accepted run | Full-frame run 1 | Full-frame run 2 |
|---|---|---|---|
| Complete episodes | 3 | 11 | 11 *(partial run)* |
| Mean answers per episode | 14.7 | **2.6** | **39.5** |
| Detector-v1 classes | STRONG 3 | **STRONG 7, WEAK 4** | STRONG 11 |
| Separates episodes? | no | **yes** | no |
| Trivial baselines reproducing it exactly | 5 | **0** | 9 |
| Review load | 1.0 | 1.0 | 1.0 |

An earlier draft of this document, written after run 1 alone, concluded that the rule is
behaviourally distinct from every trivial baseline. **Run 2 refutes that as a general statement**,
and the draft is corrected here. Drawing a stable conclusion from run 1 would have repeated
exactly the error that the accepted run's three-episode conclusion made.

**What is stable across all three runs is the review load: 1.0.** Every complete episode ever
observed has been flagged STRONG or WEAK. No episode has ever been `NO_ALERT`. The D6 dosage
target of load ≤ 0.5 is unmet on every piece of evidence the project has.

## 2. The mechanism, and a model that predicted it

Detector-v1 fires `STRONG_ALERT` if **any** answer is `Low`. An any-of rule over a sequence fires
more readily the longer the sequence, whatever it contains. At the observed `Low` rate of 0.364:

| Episode length | 1 | 2 | 5 | 10 | 39 |
|---|---|---|---|---|---|
| P(`STRONG_ALERT`) | 0.36 | 0.60 | 0.90 | 0.99 | 1.00 |

The rule **saturates at 7 answers**; its separation window is lengths **1 to 3**.

This model was computed **before** run 2 and predicts that separation is possible only for short
episodes. The three runs instantiate both regimes and behave as it says:

| Run | Episode lengths | Regime | Separated? |
|---|---|---|---|
| Full-frame run 1 | 1, 2, 2, 2, 2, 3, 3, 3, 3, 4, 4 | almost all **inside** the window | **yes** |
| Full-frame run 2 | 3, 3, 5, 32, 37, 37, 39, 41, 44, 51, 60, 63, 64 | almost all **saturated** | no |
| Accepted run | 1, 4, 39 | mixed, two saturated | no |

**Episode length is not a controlled parameter.** It varied roughly fifteen-fold between two runs
with identical configuration, prompts, model, temperature policy and round limit. The rule's
observable behaviour therefore rides on a quantity nobody is holding fixed.

The model is a property of the rule under an explicit independence assumption the data does not
verify — answers within an episode plausibly influence one another. Its agreement with three runs
is a consistency check, **not** confirmation of the assumption, and not evidence about any alert's
correctness.

## 3. What was authorized, and what it bought

| | Run 1 `FULLFRAME-01` | Run 2 `FULLFRAME-02` |
|---|---|---|
| Status | `TECHNICAL_SUCCESS` | **`STOPPED_AT_CAP`** |
| Calls | 98 of a 272 cap | **265 of a 265 cap** |
| Tokens | 1,026,303 | 5,669,413 |
| Cost | USD 0.360827 | USD 1.600173 |
| Truncated calls | 0 | 0 |
| Blocked egress | 0 | 0 |

Cumulative spend **USD 1.961 of the USD 6.00 authorization**. Run 2 stopped exactly as its
preregistration specified: the cap was reached, the run stopped, and it is reported partial and
**not re-run**. Roughly twelve of twenty-one cases were processed before the stop, so **run 2 is
not a complete frame and its counts are lower bounds.** Its eleven complete episodes are scored on
their own denominator.

### 3.1 A discrepancy the ledger surfaced rather than hid

Run 2's receipt reports `outbound_requests_independently_recomputable: false`. The budget guard
counted 265 reservations; the per-call ledger holds 264 completed calls. The 265th call was
reserved and did not complete, because the cap stop occurred while it was in flight. **The
recorded cost of USD 1.600173 therefore covers 264 completed calls and is a lower bound** if the
265th request reached the provider. This is disclosed rather than reconciled: the flag exists to
make exactly this kind of mismatch visible.

Run 1's flag is `true` — 98 ledger rows against 98 reservations.

### 3.2 Provenance bindings closed

Both receipts self-bind their event-log digest, a lifecycle summary, the execution-code digests of
both harness files, and `MAX_QA_ROUNDS`, and both carry a **privacy-safe per-call ledger** — token
counts, finish reasons, latency, cost; no prompt, no response, no credential. `outbound_requests`
is now independently recomputable rather than receipt-asserted, closing item 3 of the close-out's
gap list **for these runs only**. It does not retroactively upgrade the accepted run.

## 4. Corpus provenance — strengthened, not merely restated

| Check | Result |
|---|---|
| Archive SHA-256 vs `source-manifest.json` | **reproduced byte-exactly** |
| Inventory rows vs archive entries | 143 vs 143 |
| Files verified (1 description + 21 cases) | **22 of 22** |
| Digest mismatches | **0** |

The digests were frozen in the tracked inventory long before this re-acquisition, so a match can
confirm provenance but cannot manufacture it.

### 4.1 A selection limitation removed at the root

`study1_case_selection.py` records that the pinned inventory **cannot identify which four** of the
twenty-one eligible candidates the accepted run used; the choice was purposive, not a reproducible
rule. Study 1C runs the **entire eligible population**. When the frame is the population there is
no selection rule left to justify and no selection bias left to bound.

## 5. Descriptive results

| Quantity | Accepted (N=4) | Run 1 (N=21) | Run 2 (N=21, partial) |
|---|---|---|---|
| Complete episodes | 3 | 11 | 11 |
| Excluded episodes | 0 | 0 | **2** `INCOMPLETE_TECHNICAL` |
| Questions / answers | 44 / 44 | 29 / 29 | 483 / 479 |
| Maximum round index | 10 | 2 | 10 |
| Terminations | CONVERGED 2, MAX_ROUNDS 1 | CONVERGED 11 | CONVERGED 3, MAX_ROUNDS 8 |
| Confidence | H 3, L 16, M 25 | H 7, L 10, M 12 | H 119, L 194, M 166 |
| Detector-v1 | STRONG 3 | STRONG 7, WEAK 4 | STRONG 11 |
| Signals | S1 3, S2 2, S6 2, S7 1 | S1 7, S2 6, S6 3 | S1 11, S2 10, S6 11, S7 8 |

**These are three runs on three denominators, placed side by side and never summed or averaged.**
The case counts differ, so the configurations differ, and run 2 is additionally partial.

Directed routes differ completely between runs. The accepted run was dominated by agent4 asking
agent2 (39 questions). Run 1 shows agent3 asking agent1 (14) and agent3 asking agent2 (13), with
no agent4 traffic at all.

S3 never fired in any run — every answer carried a non-empty evidence field. It is nevertheless
**reachable**: `_ref(None)` returns `None`, and the deterministic fixture envelope fires it. It is
inert on this data, not dead code.

## 6. Baselines — what the frozen rule adds over trivial alternatives

With no labels, correctness is not measurable. What *is* measurable is **what each rule selects**.

| | Accepted (n=3) | Run 1 (n=11) | Run 2 (n=11) |
|---|---|---|---|
| Baselines identical to Detector-v1 | 5 | **0** | 9 |
| Best exact three-class agreement | 1.00 | **0.64** | 1.00 |
| Signals that contribute | S1 only | S1 and S2 | S1 and S6 |
| Reachable patterns visited | 3 of 24 | **6 of 24** | 3 of 24 |

In the two saturated runs, `ALWAYS_ALERT` reproduces Detector-v1 **exactly**. In the one run whose
episodes fell in the separation window, no baseline does. The rule's added value over flagging
everything is therefore **regime-dependent**, and the regime is not controlled.

**The agreement numbers are reported with their chance band, because without it they mean
nothing.** Detector-v1's binary flag rate is 1.0 in all three runs, so a coin that always says
"alert" also achieves binary agreement 1.0 and Cohen's kappa is **undefined**, not 1.0. This is
why the three-class agreement, not the binary one, carries the information here.

Of the rule's 24 reachable signal patterns — 32 combinations less the 8 where S7 occurs without
S6, which a max-rounds termination makes impossible — **20 map to `STRONG_ALERT`**, 3 to
`WEAK_ALERT` and 1 to `NO_ALERT`. The rule is structurally biased toward strong alerts before any
data is seen.

## 7. Four escalation mechanisms, four different answers

| Mechanism | Unit | Full-frame run 1 (21 cases) |
|---|---|---|
| Detector-v1 | Q&A episode | flags **8 of 21** cases, and all 11 episodes |
| Fragment severity and label | uncovered fragment | domain mistakes in **15 of 21** cases |
| `requires_human_review` | variability pattern | **false on all 25** patterns |
| **The human-review queue** | queued item | **0 items** |

Case-level co-occurrence: both flag 6, Detector-v1 only 2, fragment stage only **9**, neither 4.

**The structural finding: Detector-v1 is silent on 13 of 21 cases**, because those cases produced
no Q&A episode. Nine of them carry domain-mistake labels from the coverage stage — case 09 has
six. Its coverage is conditional on the pipeline having chosen to ask a question, a decision made
upstream of it. And the one mechanism whose output would actually reach a person — the queue — is
**empty**.

None of the four is ground truth. Agreement would not make any correct, and disagreement does not
show any wrong. This is co-occurrence, reported as co-occurrence.

## 8. Review against the recorded directives

| Directive | What this work contributes | Status |
|---|---|---|
| **D6** — dosage, load target ≤ 0.5, recorded unmet | Load is now measured on three runs: **1.0 in every one**, and re-scoring under every round bound from 1 to 10 leaves it at 1.0. No episode has ever been `NO_ALERT`. | **Target missed on all evidence**, measured rather than assumed |
| **D10** — bounded interaction, two-round pilot candidate | Run 1 *was* effectively a two-round regime (maximum round index 2) and is the only run in which the rule separated. A bound would therefore plausibly improve **separation**. It would not reduce **load**, and it cannot: an episode cut off at the bound terminates `TERMINATED_MAX_ROUNDS`, itself a strong signal — visible in run 2, where 8 of 11 episodes did exactly that. | Quantified, with the trade-off made explicit |
| **D2** — intervene early, not only post-Agent-4 | §7: 13 of 21 cases are never assessed because they never triggered a question, 9 carrying domain-mistake labels — and the queue a reviewer would open is empty. | New evidence, at frame scale |
| **D5** — the human expert is real, never simulated | No human judgement was simulated, requested or synthesised. The resampled curve is labelled `ANALYTIC_MODEL_NOT_OBSERVATION`. | Respected |
| **IE-09** — macro-F1 as primary classification metric | Not computed and **not computable**: it needs the independent labels still at 0 of 24. | Correctly unavailable |
| "A trigger count is not a verified error count" | Every instrument refuses to compute accuracy and says so in its own output and command-line help, enforced by tests. | Respected |

## 9. Claim boundary

**Permitted.** The corpus provenance verification; the per-run counts, each on its own
denominator; which Detector-v1 classes occurred and how often in each run; that the class
distribution differed between two runs of identical configuration; the baseline agreement results
with their chance band; the rule's reachable-space distribution and operating characteristic as
properties of the rule under stated assumptions; the co-occurrence crosstab in §7; the measured
review load; the run costs, with run 2's stated as a lower bound.

**Forbidden.** Alert correctness; accuracy, precision, recall, F1; effectiveness; human benefit;
causality; representativeness; generalization to other corpora, settings or models; any
`VEGO_AI_ON`/`VEGO_AI_OFF` statement; any variance, standard deviation, confidence interval or
p-value over two runs; any statement that the pipeline "is stable" or "is unstable"; any claim
that a case's file size indicates its quality; any claim that one escalation mechanism is more
nearly right than another; any pooling or averaging of runs; and any claim that run 2 replicates,
confirms or refutes run 1 as a complete frame — it is partial.

**Two runs bound nothing.** A difference between two runs shows that variation exists. It supports
no estimate of how much.

## 10. What remains unknown, and what would close it

1. **Whether any alert was correct.** Unresolvable from this data at any sample size. It needs the
   independent human labels recorded as 0 of 24 under IE-03/IE-09, which only a person can supply.
   This is the single binding constraint on every quality verdict in the thesis.
2. **What drives the episode-length regime.** It varied fifteen-fold between identical runs and
   determines whether the rule separates at all. Nothing here explains it, and it is the most
   consequential open question this work surfaces.
3. **Whether cases that produce no episode should be escalated.** Live for 13 of 21 cases in run 1.
4. **Why no episode is ever `NO_ALERT`.** The rule reserves that class for one of its 24 reachable
   patterns, and no run has visited it.
5. **How much run-to-run variation there is.** Two observations cannot say. A third run is **not**
   authorized by the stability preregistration under any outcome, and none was executed.
