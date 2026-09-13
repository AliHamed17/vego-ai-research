# AirTravel isolated lane — preflight review packet

Status: `PREFLIGHT_PREPARED_AWAITING_FRESH_EXECUTION_GRANT`.
The exact public-corpus fake preflight is **documented but unexecuted**.
This packet requests review; it does not create a grant, a passed preflight,
provider permission, or empirical evidence.

Implementation-parent SHA: `ef633339f3ca73430dd02e55dc14b31757a3a3cc`.
This is a reproducible code-inspection anchor, not a self-referential “current
head.” Review and future authorization must bind the final full commit and its
exact-head CI after documentation/tests are committed.

## Scope and inspection map

Public AirTravel only: `cd_airtravel` / `text2uml_airtravel_253b26dc`, N=4.
VEGO ZIP, student/historical data, expert worksheets, GUI/private logs, and
QuRE (`NOT_ADMITTED`) are excluded. Runtime reference models must be absent.
No measured scientific result is supplied by this package.

| Boundary | Inspect |
| --- | --- |
| Pinned archive, 143 source entries, five-file mapping, reference separation | `scripts/verify_text2uml_airtravel_runtime.py` |
| Immutable config, prospective manifest, grant/receipt schemas and inventory | `scripts/airtravel_execution_contract.py`; `schemas/airtravel-api-execution-*-v1.schema.json` |
| Per-attempt Decimal reservation, physical calls, deadlines and host guard | `scripts/airtravel_execution_provider.py` |
| Isolated workflow, actual Q&A correlation, lifecycle and terminal integrity | `scripts/airtravel_execution_pipeline.py` |
| Fresh verification, current bytes, command, one-time consumption, containment | `scripts/study1_external_execution_gate.py` |
| Mode selection and fixed fake-only route | `scripts/study1_airtravel_external_runner.py` |
| Historical graph arithmetic only | `scripts/study1_call_bound.py` |

The legacy `4 + 3N` / `82 + 61N` reference **does not size the isolated lane**.
The new inventory binds `max_rounds` and `call_inventory_sha256` across config,
manifest, grant, frame, pipeline and receipt. It has 16 completed-path minimum
calls and `4 * (1 + 3 * max_rounds * 2)` maximum calls. It has no automatic retry.
The current exact fake fixture takes the no-Q&A path: 16 local fake calls,
four completed cases, sixteen completed stages, zero Q&A episodes. These are
**expected engineering assertions**, not observed preflight results.

## Exact future command — DO NOT RUN from this packet

```text
uv run python scripts/study1_airtravel_external_runner.py preflight --config <private-config> --input-manifest <private-manifest> --private-root external_data/airtravel-api-runs --run-id preflight-<safe-id>
```

The placeholders must become exact reviewed repository-relative paths and a
safe ID before a fresh, hash-bound local fake-preflight authorization can be
issued. This is a command template, not an executable authorization.
`fake_preflight_authorization.json` must be present privately beside the
prepared manifest; preflight does not accept an execute `--grant` option.
The command fingerprint is computed from the exact mode-and-options argv only,
not the launcher. Duplicate, equals-form, extra, and ambiguous arguments block.

## Permitted reads and writes

- Read only the exact ignored public archive/source/runtime/reference inputs,
  private config/input manifest/local fake grant, tracked amendment, and checked
  implementation/schema files bound to the final commit. No credential read.
- Run outputs may be written only to the fresh safe-ID child of the command's
  approved ignored parent. Absolute/traversal/alias/symlink/reparse/case-colliding
  paths and nonempty output roots block.
- Durable nonce and invocation markers are written only to the separate ignored
  repository-local `external_data/airtravel-api-control` store. They survive
  output deletion. No Git metadata, source input, or protected runtime write.
- Expected private outputs: `qa_events.jsonl`, `pipeline_manifest.json`,
  `episode_projection.json`, `detector_v1.json`, `ledger.json`, `receipt.json`.
  The empty-Q&A fake path's detector file is engineering output only.

No private path, input hash, grant, corpus byte, prompt, or answer is published
in this packet. The known public commit/archive hashes belong to the protocol.

## Safety and expected receipt assertions

The preflight's deterministic fake provider has no external transport. The
runner cannot construct OpenAI in `prepare`/`preflight`. A later execute path
allows only `api.openai.com`, no alternate host/proxy/redirect endpoint, with
SDK retries disabled. This is an application guard, **not an operating-system
sandbox**; it does not protect against a privileged actor replacing Python,
mutating a running process, or deleting the durable control store.

Before any future execution, fill and review the exact model, supported token
envelope, dated prices, round/call inventory, per-call timeout and whole-run
timeout in config and the fresh grant. Those values are not chosen here.
The present per-attempt budget guard is not proof of upfront full-run funding;
whole-run affordability/reservation requirements remain a pre-authorization
review item. Maximum authorized spend is $6 (`6.00`), not a spend report.

For the exact future local fake invocation require:

- `external_provider_call_count=0`, API calls zero, actual API spend zero;
- `scientific_result_count=0`; fake token/cost ledger values are engineering
  calibration values, never real usage or billed spend;
- exact input/config/code/inventory binding, output/ledger/event hashes,
  containment `PASS`, terminal technical code `NONE`;
- complete stage/case processing; no incomplete lifecycle, missing answer,
  cross-case answer, substituted terminal event, or post-termination event;
- `agent4_queue_status=NOT_AVAILABLE`; no automatic correction.

The no-Q&A exact fake route does not itself demonstrate natural Q&A behavior.
Separate synthetic unit tests exercise Q&A correlation, concurrency, identity,
and adversarial lifecycles. They must not be presented as real observations.
Any fixture must remain `ENGINEERING_FIXTURE_NOT_SCIENTIFIC`.

## Timeouts, failure, rollback, and release

Use the exact config-bound `timeout_seconds` and `run_timeout_seconds`. Missing
or stale grants, changed bytes, unsupported configuration, attempt reuse,
budget/call/timeout/egress failures, malformed responses and invalid lifecycles
fail closed. A technical failure cannot become successful empty science.

Stop the process on failure; preserve its ignored receipt, outputs and consumed
control records for review. Do not erase markers or repeat the command.
Reverting the isolated implementation branch changes no protected orchestrator,
Detector-v1 definitions or corpus. This packet authorizes no rollback deletion.
GPL review governs publication/redistribution, not private local fake preflight.
No raw GPL-covered upstream bytes are committed.

Before signing, the reviewer must check the focused suites; complete
`scripts/tests`, `VEGO-AI/tests`, and `tests/hlayer_offline`; Ruff, compile,
privacy, security/history, evidence consistency, diff whitespace, protected-file
preservation, and exact-head CI. Local tests are not CI and are not this exact
preflight. Any failing release check means `TECHNICAL_NO_GO` for execution.

Independent review and exact-head CI are pending until recorded separately.
Only after they pass may the human issue the local fake grant. A passed local
preflight still cannot authorize a provider run: a distinct fresh execution
grant and model/budget approval are required. Detector-v1 remains a reporting
candidate label, not evidence of accuracy, benefit, intervention effectiveness,
generalisation, or system superiority.

## Local implementation checkpoint — 2026-09-13

This checkpoint supersedes the initial full-suite failures after the
test-isolation correction at the implementation-parent SHA above. All listed
test/check results pass except the existing broad Ruff baseline findings.
This is not execution readiness: independent review, exact-head CI, actual
input/model/budget checks and fresh grants remain required. These are
software-test counts, not AirTravel observations.

| Check | Observed local result |
| --- | --- |
| Six focused AirTravel verification/contract/provider/pipeline/gate suites | 421 passed. |
| Complete `scripts/tests` | Post-fix integration rerun: 770 passed, 22 skipped; 7 subtests passed. |
| Task 6 fresh checks at the new parent | Public-document boundary tests: 3 passed. Import probe plus the two previously failing synthetic gate tests: 3 passed. These are focused subsets, not additional scientific observations or distinct suite totals. |
| `VEGO-AI/tests` | 134 passed. |
| Root `tests` / `tests/hlayer_offline` | 46 passed in each command; the same tests, not 92 distinct tests. |
| Compile; privacy; history security; diff whitespace | PASS. |
| Evidence consistency | 3 present checks passed; 5 ignored-report checks skipped because reports were absent. |
| Broad `ruff check scripts src` | FAIL: 110 findings, all in files unchanged from branch base `158714064a2ecc40f5eda8561240978ebfe1b371`; zero overlap with branch-changed code. Task 6 test-file Ruff passed. |
| CI / exact public-corpus preflight / provider execution | Not run by Task 6; no push, PR, merge, grant, or provider call. |

The initial full-suite run had two failures in
`scripts/tests/test_study1_external_execution_gate.py`:

- `test_authorized_fake_preflight_has_full_hash_bound_zero_external_receipt`:
  the synthetic CLI invocation returned `INCOMPLETE_TECHNICAL`, not `PASS`.
- `test_receipt_composition_failure_keeps_terminal_call_counts`:
  the synthetic terminal receipt had 0 physical calls, not the expected 16.

Both had passed in the focused suite. Diagnosis found that the provider import
safety test reloaded shared classes and invalidated the pipeline's class
identities. Commit `ef633339f3ca73430dd02e55dc14b31757a3a3cc` moves that import
probe into a fresh subprocess; it does not modify runtime behavior or weaken
the expected PASS/call counts. The integration owner supplied the full-suite
post-fix results above (770 passed) and a fresh focused rerun (421 passed).
They are not a second independent Task 6 full-suite rerun.
Synthetic temporary-workspace tests are not the exact public-corpus preflight.
The first full-suite collection attempt lacked the thesis dependency group;
`uv sync --frozen --all-groups --offline` installed cached frozen dependencies,
and enabled complete collection. No dependency file changed.
