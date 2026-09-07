# Budget-constrained exploratory pilot — independent read-only review request for Codex

**Status: `REVIEW_OUTSTANDING`.** This is gate 4 of the pilot protocol. It has not been performed.
The pilot must not execute until it is.

**Study class:** `BUDGET_CONSTRAINED_EXPLORATORY_PILOT`.
**Not a replication of Study 1, and not Study 1B.**

**Head to review:** the branch head at review time; report it explicitly. Do not review PR #42 or
any divergent branch.

**Standing constraint:** read-only. Do not execute a provider call, do not modify the frozen
configuration, and do not amend the preregistration.

---

## Context the reviewer needs

Study 1B is closed as `BUDGET_BLOCKED_UNDER_FROZEN_PROTOCOL`: its worst-case bound was $34.6551
against a $2.00 ceiling. It was not reduced, not partially run, and not repaired. This pilot is a
**separate protocol with newly frozen, lower limits**, not a rescue of that one.

Frozen limits: output ceiling **4,096** tokens (Study 1 used 16,384), input reserve **8,000**,
call cap **90 per repeat**, **3 repeats**, ceiling **USD 2.00**. Proven bound:
`$0.0065152 × 90 × 3 = $1.7591`, headroom $0.2409.

The offline-only fixture preflight passed with 17 checks, 262 measured fake requests, and zero
provider calls (`pilot-budget-constrained-preflight-receipt.json`). The fixture is engineering
evidence only; it is not a pilot repeat and produces no scientific result.

---

## What to review — six areas

### 1. Egress restriction

- Name resolution permitted only for `api.openai.com`.
- A blocked host must raise, not fall through silently, and the blocked count must reach the
  receipt.
- The patch must be installed **before** the client is constructed.

### 2. Call cap

- The cap is **90 per repeat**, and every request including retries must count against it.
- Confirm the cap is enforced independently of cost: a cheap repeat must still stop at 90.
- Confirm a capped repeat is reported `STOPPED_AT_CALL_CAP` and labelled partial, never
  `TECHNICAL_SUCCESS`.

### 3. Token cap — new for this pilot, and the highest-risk area

- The output ceiling is **4,096**, down from 16,384, against an observed Study 1 average of 1,893
  completion tokens per call.
- Confirm the ceiling is actually applied to the request, and that the parameter name the endpoint
  accepts is used (`max_completion_tokens` for this model family, not `max_tokens`).
- **Confirm truncation is detected**: `finish_reason == "length"` must be counted per repeat and
  reach the receipt.
- Confirm a repeat with any truncated call is marked `TRUNCATION_AFFECTED` and that its
  Detector-v1 output is not presented as a communication observation. Truncation corrupts the
  answer-confidence and evidence fields, which are the detector's only inputs.
- Confirm truncation does **not** trigger a re-run, a cap increase, or a discard.

### 4. Budget cap

- The ceiling is **USD 2.00 across all three repeats**, not per repeat.
- `reserve()` must refuse **before** a request is issued, and must test cumulative spend across
  repeats, not the current repeat alone.
- Confirm `assert_bound_fits()` is invoked before the first request and that raising any limit past
  the ceiling blocks rather than warns.
- Confirm the receipt records the ceiling **actually applied**, not a module default.

### 5. Receipt self-binding

Each repeat's receipt must bind, at execution time: execution-code SHA, frozen-config hash, corpus
hashes, its own event-log hash, lifecycle summary, output hashes, model metadata, calls, tokens,
cost, start and end time, the egress record, and the **truncated-call count**.

- Confirm exclusive creation so one repeat cannot overwrite another's receipt.
- Confirm `run_id` is distinct per repeat (`PILOT-01`…`PILOT-03`) and appears in every event record.

### 6. Lifecycle handling

- A technical failure is recorded in full, not silently replaced, not retried outside the
  predeclared rules, does not halt the remaining repeats, is excluded from the completed count, and
  prevents a `COMPLETE` status.
- A repeat without headroom for a full one is refused as `NOT_STARTED_INSUFFICIENT_HEADROOM`
  rather than started and killed mid-way.
- A repeat producing zero Q&A episodes is `NO_EPISODE`, distinct from `NO_ALERT`.

---

## Requested output

For each of the six areas: `PASS`, `PARTIAL` or `FAIL`, with file and line supporting the verdict,
and any defect stated as a concrete required correction. Report the exact head reviewed.

**A `PASS` on all six does not authorize execution.** Gates 5 (green CI on the execution head) and
6 (a fresh one-time provider authorization naming model, ceiling and caps) remain outstanding, and
no credential may be used before all are green.
