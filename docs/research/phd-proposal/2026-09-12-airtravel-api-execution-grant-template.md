# AirTravel grant checklist — blank, private completion only

**`TEMPLATE_ONLY_NOT_AUTHORIZATION`**

This document contains no private hash or actual grant. It creates no authority,
nonce, signature, or execution record. A human owner must review the final exact
code and complete a fresh, one-time, hash-bound authorization privately.
It does not authorize VEGO ZIP or QuRE, a corpus change, a retry, or extra runs.
Earlier private configurations/grants without the mandatory full-run reservation
fields are rejected, not silently upgraded. A template is never a grant.

## Choose exactly one authority

| Purpose | `schema_version` | `mode` | Delivery |
| --- | --- | --- | --- |
| Local fake preflight only | `airtravel-local-fake-preflight-grant-v1` | `preflight` | Private `fake_preflight_authorization.json` beside the prepared input manifest. |
| Future real execution only | `airtravel-api-execution-grant-v1` | `execute` | Separate private file selected by the exact `--grant` argument. |

A local fake authorization cannot authorize a real provider. A future execution
authorization must be newly issued after local review/preflight requirements
pass. Do not reuse an earlier grant or retrospectively authorize artifacts.

## Fields the human must bind

All blank values below are **NOT SET**. This table is not executable grant JSON.

| Field | Required private value and check |
| --- | --- |
| `code_sha` | Full final reviewed execution commit; exact-head CI must be green. Do not use this document's parent as a future execution SHA. |
| `input_manifest_sha256` | Canonical digest of the freshly verified prospective manifest, including public corpus and exact five runtime files. |
| `config_sha256` | Canonical digest of the complete frozen configuration. |
| `model` | Exact human-selected supported model ID; no model is selected here. |
| `provider_host` | `api.openai.com`; fake mode still binds the proposed configuration but cannot contact it. |
| `price_schedule` | Private configuration's input/output price rates and authoritative source. |
| `checked_at_utc` | Time at which the price source and supported model/token envelope were verified. |
| `price_schedule_sha256` | Canonical digest of that dated schedule. Prices are not claimed current by this template. |
| `max_usd` | `6.00` maximum USD for the authorized invocation, including uncertain-cost attempts. |
| `max_calls`, `authorized_call_count` | Both must equal the verified isolated inventory maximum exactly. No smaller or larger cap is admitted. |
| `max_rounds` | Frozen integer round limit, 1–10; never inferred from `max_calls`. |
| `call_inventory_sha256` | Digest from the canonical isolated inventory for those rounds. |
| `max_input_tokens`, `max_output_tokens` | Verified per-call ceilings consistent with model envelope, prices, and budget. |
| `full_run_reservation` | Immutable calculation: authorized slots, inventory hash, token caps, dated full price schedule/hash, per-call cost and total full-run allocation; policy `CANONICAL_ISOLATED_INVENTORY_MAXIMUM`. |
| `full_run_reservation_sha256` | Canonical calculation hash, identical across config, manifest, grant and receipt. The gate independently recomputes it. |
| `timeout_seconds`, `run_timeout_seconds` | Exact per-call and whole-run deadlines. |
| `max_retries`, `concurrency` | `0` and `1` respectively for this lane. No automatic retry. |
| `command_sha256` | Digest over the exact **mode-and-options argv**, excluding the `uv run python` launcher and script path. |
| `run_id`, `private_root` | One fresh safe ID and its exact ignored repository-relative run root; only the approved parent is accepted. |
| `issued_at_utc`, `expires_at_utc` | Explicit UTC `Z` timestamps; not future-issued or expired at invocation. |
| `nonce` | New private 64-character lowercase hex one-time value. |
| `invocation_id` | New private UUID; never shared with an earlier attempt. |
| `consumed` | Initially `false`; durable attempt markers consume the nonce and invocation before provider construction. |

`price_schedule` and `checked_at_utc` are configuration fields, not extra grant
keys. The strict grant schema rejects undeclared keys. Fake authority uses the
same binding fields with its separate schema/version and mode.

## Required review before signing

1. Verify current code/file hashes, corpus and five runtime hashes, private
   root containment, reference exclusion, and exact command fingerprint.
2. Verify the isolated call inventory; do not use the legacy orchestrator bound.
3. Confirm model tokenization/envelope and dated prices. Recompute the full
   reservation as authorized slots times the conservative capped input/output
   cost. It must be at most $6 before a nonce can be consumed or a client created.
   The ledger must hold this full allocation before request one. This calculation
   is not a guarantee of scientific or technical completion.
4. Confirm independent code review and green CI on the exact final SHA.
5. For a local fake grant, authorize only the documented local fake command.
   For a later provider grant, require a separate reviewed local preflight
   receipt and fresh human execution decision.

## Consumption and rollback

The gate exclusively records both nonce and invocation attempts in the ignored
repository-local control store, separate from disposable output. Failure after
claiming an attempt still consumes it. Deleting output must not delete these
markers. Never delete markers to replay an authorization.

Rollback stops the process and preserves its private technical receipt and
control records. Reverting the isolated lane does not change protected runtime
or corpus bytes. Any later attempt requires a new decision and fresh grant;
no paid retry is authorized by this template.
