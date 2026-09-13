# AirTravel isolated API lane — public protocol

Status: `PREFLIGHT_PREPARED_AWAITING_FRESH_EXECUTION_GRANT`.
This is an implementation protocol, not an authorization or a result receipt.
The exact corpus preflight is documented but unexecuted. No provider run is
authorized by this document.

## Data boundary

- Only public AirTravel is eligible: `setting_id=cd_airtravel`,
  `corpus_id=text2uml_airtravel_253b26dc`, **N=4** selected candidate models.
- Public upstream commit: `253b26dc704d523209a5cba79686f8f7fab57d63`.
- Pinned source archive SHA-256:
  `8cf82e2ab2d2ce3da9a7ec4165e760ae1e0d9af14468f5aa2a3883037d8da701`.
- Admission requires all 143 source entries and the frozen v1.0.2 mapping:
  exactly one description and four candidate models, byte-identical to source.
  Missing, extra, duplicate, changed, linked, or reference-leaking files block.
- Reference models remain outside provider-visible inputs. No raw upstream
  bytes are published by this implementation.
- The source authority uses `files` and `upstream_commit`. The v1.0.2 amendment
  uses `source_to_runtime_mapping`: original source filenames map to the five
  relocated runtime filenames with no byte transformation. The verifier selects
  only the pinned codeload `dataset/AirTravel/` subtree and checks all 143 entries.
- Reference separation requires all three declared `excluded_references` to
  match both verified source bytes and the separate local reference directory.
  An empty or arbitrary reference directory cannot establish separation.
  The amendment has no `allowed_configuration` field: runtime-byte verification
  does not authorize execution; the separately validated execution config and
  fresh grant remain mandatory.
- **VEGO ZIP is not sent to an external provider.** Student/historical models,
  expert sheets, GUI exports, interaction logs, and user logs are excluded.
- **QuRE: `NOT_ADMITTED`.** Exact identity, licence, suitability, and separate
  transfer authority remain unresolved. It is not included by analogy.

These four cases are not a representative sample. This is a newly isolated
workflow, not demonstrated prompt/state parity with the protected legacy
orchestrator, and not an unchanged replication of an earlier run.

## Three separate modes

| Mode | Permitted action | Provider authority |
| --- | --- | --- |
| `prepare` | Recheck public bytes; create prospective private input binding. | None; no provider construction. |
| `preflight` | Deterministic local fake, only after a fresh human hash-bound local grant. | No external provider or API calls. |
| `execute` | One exact invocation after all reviews and a distinct fresh execution grant. | Only declared `api.openai.com`; never inherited from a fake grant. |

Every invocation uses a fresh ignored run directory. Config, manifest, source
mapping, code, exact command, model, price schedule, caps, round policy, and root
must agree. Current bytes are checked against the bound Git commit. An unchanged
Markdown document alone is not a binding.

## Calls and the $6 ceiling

`max_usd` is exactly `6.00`. Before nonce consumption or provider construction,
the gate recomputes a conservative **whole-run** allocation using the frozen
call count, both token caps, and the dated uncached Decimal price schedule.
The ledger activates that whole allocation before request one; each attempt
draws one slot from it. Unknown-cost failures retain their allocation, and unused
slots remain reserved. Successful known usage releases only that attempt's slot.
SDK automatic retries are disabled. This lane permits `max_retries=0` and
`concurrency=1`, with per-call and whole-run deadlines.

The isolated inventory is computed by
`scripts/airtravel_execution_contract.py::build_call_inventory`:
four context calls plus three stages per case; each stage permits one generation
and at most one answer per round. For frozen `R=max_rounds`, its completed-path
minimum is 16 calls and its maximum is `4 * (1 + 3 * R * 2)` calls. Failures may
stop earlier. `max_rounds` and `call_inventory_sha256` bind every contract.
The only admitted policy is
`authorized_call_count = max_calls = isolated_inventory.maximum_calls`.
A larger or smaller configured call cap is rejected; it cannot redefine rounds.

`per_call_usd = (max_input_tokens * input_rate + max_output_tokens * output_rate) / 1000000`.
`full_run_usd = authorized_call_count * per_call_usd`.
Rates are USD per million tokens. No cached-token discount or optimistic refund
is assumed. `full_run_usd > 6.00` blocks before a nonce, client, or request.
The calculation inputs, derived values, policy, and calculation hash are bound
in config, prospective manifest, grant, and receipt. Any mismatch is rejected.

The legacy `4 + 3N` / `82 + 61N` calculation belongs to the protected legacy
graph only; it is not the isolated lane's upper bound. A prospective model's
dated prices and supported token envelope must be reviewed before approval.
The affordability check is relative to the human-reviewed prices and supported
token envelope; it is not a live price quote or a guarantee of successful
completion. No particular model is selected or declared affordable here.
Fake preflight has `cost_basis=LOCAL_FAKE_SIMULATION`: `spent_usd=0.00`;
its separately named `simulated_spent_usd` and reservation ledger are engineering
calculations, not provider charges.

## Evidence and interpretation

The ignored event stream is the Q&A source of truth only after lifecycle
validation. Stable identities bind run, case, asking agent, answering agent,
stage, skill, and scope; rounds do not silently create a new episode.
Actual generated questions must correlate with their own returned answers.

`CONVERGED`, `TERMINATED_MAX_ROUNDS`, and `INCOMPLETE_TECHNICAL` remain distinct.
Incomplete runs are technical failures, not empty scientific success. A complete
case can have pipeline output without Q&A. No fixture question substitutes for
a missing generated question.

Detector-v1 remains unchanged and **reporting-only**: a complete Q&A episode may
receive a candidate-for-human-review label. It creates no queue and provides
**no automatic correction**. It does not establish accuracy, correctness,
human benefit, reduced workload, generalisation, or ON/OFF superiority.
Confidence is model self-report; evidence presence is not evidence quality.

Agent-4's variability classification and separate queue builder are a different
mechanism. This lane does not invoke that builder; queue status is
`NOT_AVAILABLE`, not “not triggered.” No source, guideline, target, or model is
changed automatically. C1/C2/C3 and semantic mapping labels are not new Detector
triggers.

## Privacy, review, and stop conditions

Raw inputs, prompts, answers, events, grants, and receipts stay ignored and
repository-local. Public documentation contains no private hash or actual grant.
Durable one-time nonce/invocation markers live outside disposable run outputs;
deleting output does not authorize replay. Preserve the control store.

Application-level containment and request guards are not a hostile-machine
sandbox. A local actor who can delete the control store or replace Python is
outside this trust boundary. No promise of machine-wide replay prevention is
made. GPL review concerns publication/redistribution, not private local fake
preflight; no upstream source is included in this package.

Independent review, exact-head green CI, verified real input bindings, reviewed
model/pricing/token assumptions, and the applicable fresh human grant remain
required. Any missing binding, drift, cap, timeout, malformed response, egress,
or lifecycle failure blocks/terminates the attempt. No real run, empirical
denominator, scientific result, or actual spend is reported here.
