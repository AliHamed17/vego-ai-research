# PR38 sequential hardening — technical evidence gate

Evidence parent: `b362c55b7c6f7829bf5d99402f77ab015a7417e0`.
Green main base: `c34d3954b5e080d090017d2ea655d454d75a6b92`.
Implementation commit: `28a1d95f39058e5b9dd3e7601584e2393311d405`.

This is the successor to the earlier PR38 correction gate, not a historical recovery audit. Its acceptance label supersedes the earlier preparation wording: **PREFLIGHT_PREPARED_AWAITING_EXPLICIT_GRANT**, conditional on all final local checks and all six fresh corrected-head CI jobs passing. CI is a separate external receipt, reported with its exact head/run URL after push; this document does not predict a CI result.

Exact AirTravel fake preflight: **NOT_EXECUTED**. Packet: **AUTHORIZATION_REQUESTED_NOT_GRANTED**. No real grant or authorization-message file exists. No model/provider call, paid run, experimental Detector run, synthetic corpus generation, protected modification or merge is authorized by this record. GitHub fetch/push/Actions metadata operations are not model-provider calls.

## Starting-state reconciliation and fail-before evidence

The supplied request expected PR head `3727acfe2130863ab6b737824a1718e7b3648b92`. Live fetch found two intervening Codex correction commits, `1518fbd40745acaaf5d7b30d4b1c1f2375b056ca` and `b362c55b7c6f7829bf5d99402f77ab015a7417e0`. Their provenance is the previous exclusive correction, not a new competing writer. This tranche uses a new isolated worktree and does not alter other WIP or stashes.

The seven inherited focused test files ran first: **85 passed, exit 0**. Therefore the older list of 32 defects is not a truthful description of the starting head. Already-corrected defects below are reported as inherited protections with fresh regression evidence; no new fail-before evidence is invented for them.

New red command: `python -m pytest -q scripts/tests/test_airtravel_pr38_hardening.py`, **21 failed, exit 1**. Ten failures demonstrated unsupported expanded grant fields (the old schema rejected the expanded positive fixture); the remaining failures demonstrated unequal in-bound calls accepted, missing new counters/parity/inventory interfaces, and old zero-Q&A status. The old positive grant regression at the starting head accepted its legacy field set without the new message/implementation/runtime-map bindings. This is contract expansion evidence, not a claim that arbitrary grants could execute at the starting head.

Additional red command: `python -m pytest -q scripts/tests/test_airtravel_pr38_hardening.py -k route_metadata`, **1 failed, 47 deselected, exit 1**. A schema-valid, rehashed fixture event carrying free-form agent prose was accepted. Closed agent identities now reject it; after correction the hardening/renderer group passed **56 tests, exit 0**.

## Individual defect disposition

Test paths below are under `scripts/tests/`. “Inherited” means already implemented at the evidence parent, verified again, not newly reproduced as broken.

| # | Starting defect allegation / disposition | Correction and executable evidence |
|---:|---|---|
| 1 | Arbitrary packet accepted — inherited protection | `test_airtravel_pr38_authorization::test_arbitrary_existing_markdown_is_not_the_reviewed_packet` |
| 2 | NOT_GRANTED request executes — inherited protection | `test_request_packet_without_grant_fails_before_runtime`; packet remains a request |
| 3 | Self-assertion flag grants authority — inherited protection | `test_prepare_airtravel_protected_fake_preflight.py` authorization dispatch tests; separate receipt mandatory |
| 4 | No grant required — inherited protection | Missing-grant test rejects before runtime import |
| 5 | v2 stale harness — inherited supersession | Only designated v3 packet is accepted; v2 retained, not authorizable |
| 6 | Expanded bindings absent — corrected | `test_every_expanded_binding_is_required_and_checked`, `test_owner_message_time_and_command_mutations`; exact human-message hash, implementation/module/protected-manifest/runtime-map/limits bound |
| 7 | Timeout absent — inherited protection | `test_airtravel_pr38_safety::test_wall_clock_timeout_restores_client_environment_and_handlers` uses 0.01-second fixture |
| 8 | Call cap absent — inherited cap, equality corrected | `test_bounds_are_per_run`, `test_different_in_bound_pass_counts_rejected`, combined 652 accepted for 326+326 |
| 9 | Episodes mislabeled routes — inherited separation, expanded names | `test_new_counters_do_not_confuse_episodes_and_pairs`: three episodes, one ordered pair |
| 10 | No direct comparison — inherited protection | `test_complete_protected_two_case_fixture_outputs_and_parity` runs literal two-case fixtures through real protected control flow |
| 11 | No prompt parity — inherited, adversarial proof extended | `test_parity_mutation_is_rejected[prompt]` |
| 12 | No answer parity — inherited, adversarial proof extended | `test_parity_mutation_is_rejected[answer]` |
| 13 | No explicit decision parity — extended | Full response-decision hash plus complete state; decision mutation rejected |
| 14 | No state parity — inherited, adversarial proof extended | State mutation rejected; no scientific fields removed |
| 15 | No output parity — inherited, adversarial proof extended | Artifact mutation rejected; all ten scientific output hashes compared |
| 16 | Required counters absent — corrected | Canonical episode/pair/list/direct/provider/Detector counters added; aliases preserved |
| 17 | Broad outputs — inherited protection | `test_receipt_escape_and_broad_execution_roots_fail`; exact dedicated ignored root |
| 18 | Receipt escape — inherited protection | Fixed `preflight-receipt.json` child only |
| 19 | Links/traversal — inherited links, explicit traversal rejection added | `test_output_symlink_escape_fails`; `output_path` rejects `..` before resolution |
| 20 | Quotas absent — inherited protection | File/byte and Python-3.10 pathlib quota tests; 40 files, 16 MiB ceiling |
| 21 | Privacy description inaccurate — inherited correction retained | Packet distinguishes hash-only event journal from full private state/templates/guidelines/vectors/history/logs |
| 22 | Missing termination — inherited protection | Converged and max-round real-loop fixtures; unterminated stream rejected |
| 23 | Unscientific closure — inherited protection | Exact protected loop labels/registry correlation; failed exchange closes INCOMPLETE_TECHNICAL |
| 24 | Return implies convergence — inherited protection | Only observed questionless next round closes CONVERGED; max-round fixture stays nonconverged |
| 25 | Failed/fixture empty result valid — stronger receipt correction | `test_successful_zero_qa_requires_every_completion_proof`; missing proof or fixture-only is INVALID_OR_INCOMPLETE_ZERO_QA |
| 26 | Silent setting/corpus defaults — inherited, schema strengthened | `test_complete_renderer_receipt_single_mutations` starts with complete valid shape and mutates one field |
| 27 | Arbitrary CLI technical status — inherited protection | Parser accepts receipt/hash/identity/output only, not status/findings |
| 28 | Duplicate Detector logic — inherited single source | `test_canonical_signal_totals_and_forward_route`; unchanged canonical extractor supplies classifications/all_signals_fired |
| 29 | Reversed route — inherited correction | Source→target direction tested with agent3→agent1 |
| 30 | Missing machine CSVs — inherited CSVs, nine-name contract updated | Repeated renderer output hashes test; analysis receipt and named output manifest added |
| 31 | Free narrative injection — inherited CLI closure, metadata gap corrected | Rehashed route-metadata injection red/green test; agent vocabulary closed |
| 32 | Blacklist-only validation — corrected boundary proof | Fixed authoritative prose plus typed receipt and closed agent fields; blacklist is only an extra residual check |

## Frozen bounds and natural fixture paths

The protected orchestrator SHA remains `fca4b885ee07381db0f02e558b1aebf25bdc7c27da1c471fd3103d7e0e2d5b88`. Seventeen accounting rows describe ten physical call sites. Captured protected frame positions bind shared answer helpers to their actual invoking branch and case; unknown branches/labels/rounds reject. This uses no task ID, memory address or nondeterministic counter.

| Component | Minimum | Maximum |
|---|---:|---:|
| Fixed template | 1 | 1 |
| Fixed guideline producer + language/domain answers | 1 | 30 |
| Fixed pattern identification | 1 | 1 |
| Fixed classification + language/domain answers | 1 | 30 |
| Conditional feedback + language answers | 0 | 20 |
| Each case: mapping | 1 | 1 |
| Each case: resolve + language/domain answers | 1 | 30 |
| Each case: audit + language/domain answers | 1 | 30 |
| Total | 4+3N | 82+61N |

Real phase-control-flow fixture counters, N=0/1/4: minima **4/7/16**, maxima **82/143/326**. These are logical fake calls, not HTTP attempts or spend estimates. Two-pass counts must be equal and each within 16..326; never apply 326 to the combined total. The historical 6+3N expression counted optional answers as mandatory; the historical 22+61N expression yields 266 at N=4, not 326. Neither is an active bound.

The full two-case fixture proves direct-versus-observed calls/state/artifacts with separate directories. Additional mutations reject prompts, answers, decisions, state, artifacts and termination results; observer-only event differences are permitted. Complete state is compared without normalization. Only time-stamped pipeline logs are outside scientific byte parity.

Concurrent cases retain separate source/skill/case episode identities across rounds. Independent subprocess tests reproduce the same episode ID for the same frozen identity. These are **protected-orchestrator fake paths**, not provider-backed production observations. The exact AirTravel route counts remain NOT_EXECUTED; provider-backed route pairs remain zero.

## Runtime and preparation receipts

Source/runtime receipt: `airtravel-pr38-correction/source-runtime-receipt.json`. Actual pinned archive verification: **143/143**, zero missing/extra/mismatches, no duplicate members; upstream commit identity PASS. A separate read-only ZIP/manifest comparison checked all 143 declared byte lengths: zero size mismatches, archive-path collisions or manifest-path collisions, exit 0. Five unique mappings, no collisions, byte-identical true. Runtime: exactly five observed/expected/matching files, no extra/missing/mismatching/reference files, configuration PASS.

Independent materializations in this worktree produced the same ZIP SHA-256 twice:
`e37baecd20a0c84eb1d9b87b3b78a23bc4b4eb8a9824ad3086dc30aa35fdd31f`.

Actual prepare-only command, from the isolated repository root:

```powershell
python scripts/prepare_airtravel_protected_fake_preflight.py --prepare-only --runtime-root external_data/airtravel-pr38/runtime_input --runtime-archive external_data/airtravel-pr38/cd_airtravel-runtime-v1.0.2.zip --output-dir external_data/airtravel-pr38/final-prepare --receipt external_data/airtravel-pr38/final-prepare/preflight-receipt.json
```

Exit **0**, status **PREPARED**, all six checks PASS. Receipt SHA-256:
`4598bb3fe3fd9653662e874192cd4cd605f8cda18d2eb9fbd28664763916159b`.
This path now contains the preparation receipt and is not reusable as an empty execution root. The distinct future `authorized-fake-run` root remains absent.

Amendment SHA-256 remains `bd2b7f03585582ff7591d21795fbd3ed4701244d66d26221683520238c2dead2`. Policy-derived inventory: **83 protected files unchanged** versus base. The generator binds every runtime-relevant code hash to the actual implementation commit; future external grant binds final PR head and packet hash, avoiding self-referential commits.

## Authorization and residual limits

The future grant schema is `schemas/airtravel-fake-grant-v1.schema.json`; its existing test-only example is expired and cannot authorize. The owner provides both a matching grant and exact authorization-message file. This is a local owner-controlled receipt workflow, not a digital-signature identity system against a malicious filesystem writer. Missing message, mismatching hash, future issue time, expiry or changed commit/command/output rejects.

Timeout is cooperative asyncio cancellation of trusted yielding Python control flow, with cleanup; the guard is not a kernel sandbox or hard-kill defense against hostile native code. Socket/DNS/provider construction, credential reads, subprocesses and outside writes are denied during execution. Full outputs remain private. Quotas, before/after inventory and hash checks fail closed; no automatic analysis follows failure.

GPL review addresses publication/redistribution, not private local fake preflight. The separate paid-run decision packet records the existing gpt-4o default as unconfirmed, cost TO BE MEASURED, and transport-attempt/budget gates still requiring human decisions. No paid grant is issued.

## Verification accounting

Commands: focused eight-file PR38 group; complete `python -m pytest -q scripts/tests`; `python -m pytest -q VEGO-AI/tests tests`; targeted Ruff plus `python scripts/check_quality_ratchet.py`; compileall for framework/eval/analysis/scripts/src; `check_repository_privacy.py`; `security_audit.py --history`; `check_evidence_consistency.py --check`; `validate_research_records.py schemas/examples`; `check_hlayer_change_authorization.py --base c34d3954b5e080d090017d2ea655d454d75a6b92`; supported hardening generator three times followed by `--check`.

Final local code rerun: full scripts **485 passed, 22 skipped, seven subtests passed**, exit 0; two expected duplicate-ZIP fixture warnings. VEGO-AI/root: **180 passed**, exit 0. Privacy, security, protected authorization, research records, quality/Ruff and compile passed. Evidence consistency: three present checks passed, five absent ignored-report checks skipped; those five are not new validation. The final six CI job outcomes belong to the external execution report, not an assumed success here.

Human next step remains sequential: Claude performs read-only adversarial review after push; Ali reviews both outputs and decides whether to issue the exact grant. No model/provider experiment is part of this task.
