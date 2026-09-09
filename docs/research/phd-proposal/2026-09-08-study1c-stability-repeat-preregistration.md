# Study 1C-R — stability repeat: preregistration

**Study class: `IDENTICAL_CONFIGURATION_STABILITY_REPEAT`.**
**Status: `PREREGISTERED_NOT_EXECUTED`. Frozen 2026-09-08, while run 1 was still executing and
before any of its output was observed.**

This document is committed **before** the first full-frame run's results are read. The two-run
design is therefore fixed independently of what run 1 shows, which is the property that makes a
stability statement possible at all.

---

## 1. What this adds that run 1 cannot

Study 1B was recorded as `BUDGET_BLOCKED_UNDER_FROZEN_PROTOCOL`: its protocol could not be
bounded under USD 2.00 and was never run. Its question remains open and is the one asked here:

> Holding **every** configuration parameter identical and varying only the provider's own
> sampling, how much does the observed communication and its Detector-v1 classification move
> between two runs?

The budget-constrained pilot deliberately could **not** answer this, because it changed the
limits, confounding run-to-run variation with limit effects. This repeat changes nothing at all.

## 2. Frozen parameters

Every parameter is **byte-identical to Study 1C run 1**, including corpus, frame of 21 cases,
model, temperature default, 16,384 output ceiling, 8,000 input reserve, `MAX_QA_ROUNDS` = 10,
concurrency 2, request timeout, run timeout, egress restriction and Detector-v1 itself. The same
two harness files execute it, and their SHA-256 digests are bound into both receipts.

| Parameter | Value |
|---|---|
| Repeats | **exactly one**, run identifier `FULLFRAME-02` |
| Temperature / seed | provider default, **not** overridden — this is the only source of variation |
| Call cap | `min(272, floor((6.00 − actual run-1 spend) ÷ 0.0212608))` |
| Budget ceiling | the unspent remainder of the USD 6.00 authorization |

The call cap is a deterministic function of **budget headroom**, which is not a scientific
outcome. It is not a function of run 1's episode counts, classifications, signals or any other
result, and it may not be revised after run 2 begins.

## 3. Predefined handling — fixed now

| Situation | Handling |
|---|---|
| Run 2 completes | Reported beside run 1 as two runs, never pooled and never averaged |
| Run 2 stops at cap or ceiling | Reported `STOPPED_AT_CAP`, labelled partial, **not** re-run |
| Run 2 fails technically | Recorded in full with its cost, preserved, **not** replaced |
| Headroom is insufficient | Refused as `NOT_STARTED_INSUFFICIENT_HEADROOM`; never started to be killed mid-way |
| The two runs disagree | **That is the result.** Disagreement is reported, not investigated away |
| The two runs agree | Reported as agreement **on two observations**, which is not a stability guarantee |

**No outcome-dependent adaptation.** Exactly one repeat is authorized. A third run is not
authorized by this document under any outcome, and neither run may be discarded or re-ordered.

## 4. What two runs can and cannot support

Two observations bound nothing. With n = 2 there is no variance estimate, no confidence
interval, and no distribution.

**Permitted:** the per-run counts, side by side; the observed difference between them, stated as
a difference between two runs and nothing more; whether the Detector-v1 class distribution was
the same or different across the two.

**Forbidden:** any variance, standard deviation, confidence interval or p-value; any statement
that the pipeline "is stable" or "is unstable"; any extrapolation to further runs; any pooling or
averaging of the two runs into one denominator; and every claim already forbidden by the run-1
preregistration — alert correctness, accuracy, precision, recall, F1, effectiveness, human
benefit, causality, representativeness and generalization.

A difference between two runs demonstrates that variation exists. Agreement between two runs
does not demonstrate that it does not.
