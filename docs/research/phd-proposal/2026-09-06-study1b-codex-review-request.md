# Study 1B — independent read-only review request for Codex

**Status: `SUPERSEDED_CLOSED`.** This review request is retained as historical protocol context.
Study 1B is now permanently closed as `BUDGET_BLOCKED_UNDER_FROZEN_PROTOCOL`; no execution gate
remains open for that protocol.

The closure was recorded on 2026-09-07 after the frozen five-repeat budget was checked. The
historical request below is not an authorization to reopen, reduce, partially run, or relabel
Study 1B. The separate budget-constrained pilot has its own preregistration and review gate.

**Study class:** `EXPLORATORY_POST_STUDY1_VARIANCE_REPLICATION`.

**Head to review:** the branch head at review time; report it explicitly in the review output.
Do not review PR #42 or any divergent branch.

**Standing constraint:** this review is read-only. Do not execute a provider call, do not modify
the harness, and do not create or amend the preregistration.

---

## What to review

### 1. Budget guard — `scripts/airtravel_real_run.py`, `BudgetGuard`

- `reserve()` must refuse **before** a request is issued, never after.
- The ceiling must be shared across repeats: `cumulative_spend_usd = prior_spend_usd + spent_usd`,
  and the refusal must test that sum, not `spent_usd` alone. A per-repeat-only test would allow
  five repeats each to spend the full ceiling.
- `summary()` must report the ceiling **actually applied**, not the module default, or a $2 run
  would record a $10 ceiling in its receipt.
- Confirm the defaults still reproduce the Study 1 accepted-run behaviour exactly
  (`budget_usd = 10.0`, `max_requests = 326`, `prior_spend_usd = 0.0`).

### 2. Call guard

- Every outbound request, **including retries**, must increment the counter and be tested against
  the cap.
- Confirm the cap is enforced independently of cost: a cheap run must still stop at the request
  cap.

### 3. Egress restriction — `restrict_egress()`

- Confirm name resolution is permitted only for `api.openai.com`.
- Confirm a blocked host raises rather than silently falling through, and that the blocked count
  reaches the receipt.
- Confirm the patch is installed before the client is constructed, not after.

### 4. Receipt self-binding

- Each repeat must bind, at execution time: `event_log_sha256`, the lifecycle summary
  (`termination_counts`), and `reviewed_head`. These are the three fields the Study 1 accepted run
  did **not** bind.
- Confirm the receipt is written with exclusive creation so a repeat cannot silently overwrite
  another's receipt.
- Confirm `run_id` is distinct per repeat and appears in the receipt and in every event record.

### 5. Lifecycle failure handling

- A technical failure must be recorded in full, must not be silently replaced, and must not be
  retried outside the predeclared retry rules.
- A failed repeat must not halt the remaining repeats, must be excluded from the completed count,
  and must prevent a `COMPLETE` status.
- Confirm a repeat that produces no receipt is reported as `TECHNICAL_FAILURE_NO_RECEIPT` rather
  than being dropped.

---

## What the reviewer should know before starting

Two independent blockers were already recorded, so this review is not on the critical path to an
immediate run:

1. **`CREDENTIAL_NOT_AVAILABLE`** — `OPENAI_API_KEY` was absent at gate time.
2. **`BUDGET_INSUFFICIENT_FOR_FROZEN_FIVE_REPEAT_PROTOCOL`** — the conservative upper bound over
   five repeats is $34.6551 against a $2.00 ceiling. See Amendment A2 of the preregistration.

The historical offline preflight record is superseded by the closure receipt: the current
`study1b-offline-preflight-receipt.json` reports five closure checks, `repeat_execution =
NOT_STARTED`, and `provider_calls = 0`. It is a closure check, not an orchestration run and not
scientific evidence.

## Requested output

For each of the five areas: `PASS`, `PARTIAL` or `FAIL`, with the file and line supporting the
verdict, and any defect stated as a concrete required correction. Report the exact head reviewed.
