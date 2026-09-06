# PR38 exclusive correction — technical gate

Scope: preparation for later authorization, not execution. PR38 must remain draft and unmerged.
Audit base: `c34d3954b5e080d090017d2ea655d454d75a6b92`.
Correction parent: `3727acfe2130863ab6b737824a1718e7b3648b92`.
The corrected head and its CI evidence are recorded in PR38 and the handoff; a later grant must bind that exact head independently of this document.

## Evidence and boundaries

- Packet v2: SUPERSEDED_NOT_AUTHORIZABLE. Packet v3: AUTHORIZATION_REQUESTED_NOT_GRANTED.
- A request packet alone, an arbitrary Markdown file or an authorization assertion flag cannot execute. The separate grant schema checks owner, status, UTC timestamps/expiry, commit, packet/harness/runtime hashes, corpus/setting/N, protected hashes, exact destination and command fingerprint. The only example is TEST_FIXTURE_ONLY and is rejected for execution.
- Current corpus verification is in `airtravel-pr38-correction/source-runtime-receipt.json`: 143 upstream files, five byte-identical mappings, five runtime files, no missing/extra/mismatch/reference leakage. Raw archives and runtime bytes are private and ignored.
- Prepare-only is authorized. Exact execution is not. Preparation makes zero orchestrator/fake/provider/Detector calls and writes no events. Its receipt is private under the explicit preparation directory.
- The guarded future execution performs direct-fake and observed-fake passes, each with 16–326 logical client calls; expected two-round schedule is 46 each, 92 combined. The combined maximum is 652. Token/API cost: TO BE MEASURED. This is not an HTTP retry bound.
- Every call-bound use verifies the protected orchestrator content hash. The 17-row inventory remains source-bound. Real protected phase tests use literal engineering fixtures, not the exact AirTravel configuration; N=0 is a phase-function boundary test, not a valid input-loader setting.
- Observer identity is SHA-256 of run, setting, source agent, skill/loop and case. Round and target are not episode identity components. Registry allocation binds actual producer question text to answer IDs. Context-local metadata separates concurrent cases.
- Convergence comes from a successful next questionless round, maximum-round termination from actual final-round answers, and technical closure from failures. Validation rejects unterminated streams. Technical-incomplete episodes are excluded by frozen Detector-v1.
- Unique routes are directed source/target pairs counted from questions, not episode IDs. Question, answer and episode counts are separate.
- Two-pass parity covers ordered labels, prompt hashes, answer hashes, counts, PipelineState and protected scientific output hashes. Wall-clock logging is excluded from scientific byte parity. The exact check is implemented, not executed on AirTravel.
- The complete two-pass coroutine has a 1,800-second timeout and no retry. Cancellation restores client/registry/environment and closes this run's handlers; failure is never valid zero-Q&A. The short timeout exists only in unit-level function calls, not CLI.
- IO/network guards apply to trusted Python runtime execution, not hostile native code or a kernel sandbox. Event-loop local IPC initializes before the guard. External sockets, DNS, provider/credential imports and subprocesses are forbidden and attempts fail execution. All writes are constrained to the grant-bound ignored external_data run directory; 40 files/16 MiB maximum, with space reserved for the failure receipt. Unexpected files and tracked/protected changes fail.
- Q&A events contain hashes/lengths/machine fields; pipeline outputs may contain complete fake/public-external state. Nothing is auto-committed. A separate privacy review is required for extracted receipts and all future raw provider output stays private.

## Reporting contract

The renderer requires a hash-verified successful run receipt, exact setting/corpus/N, commit, model, archive and event hashes, all four cases, expected output files and parity/completion proof. Empty events without that proof are ZERO_EVENTS_TECHNICAL_FAILURE, not a valid result. CLI accepts no free-form findings, conclusions or technical-status assertion.

All signal counts derive from the unchanged Detector-v1 `all_signals_fired`, `classification`, `reason_codes` and `exclusion_reason`. No rule/threshold copy remains in the renderer. C1/S5/S8/S9 remain non-triggering. Model, provenance and descriptive machine fields do not establish scientific correctness, usefulness, representativeness or supervisor approval.

Fixture rendering produces eight deterministic deliverables: validated-run-receipt.json; airtravel-results-machine.json; airtravel-episodes.csv; airtravel-detector.csv; airtravel-signals.csv; airtravel-routes.csv; airtravel-terminations.csv; airtravel-preliminary-results-he.md. `output-hashes.json` records all eight hashes; its own hash is emitted separately, avoiding self-reference. No experimental report was generated.

## Verification record and remaining decisions

New refusal tests first failed against PR38 for missing grants/source binding, execution guards and unsafe zero-event rendering. Subsequent tests verify the fixes using fixtures. A registry integration attempt exposed a frozen thesis-evidence dependency; the general validator was restored exactly, and the new grant schema is checked independently under `schemas/airtravel-fixtures/`. No thesis manifest or scientific source was rewritten to hide that failure.

Final commands: focused PR38 suites; full `scripts/tests`, `VEGO-AI/tests`, root `tests`; Ruff on all changed Python paths; compileall; repository privacy; security audit with history; evidence consistency; dedicated grant-schema tests; general research-record validation; quality ratchet; protected-change check; official hardening generator three times and `--check`. Detailed counts and exact fresh CI run/job outcomes are in the handoff/PR description, not assumed from the parent CI run.

Local verification at the correction freeze:

| Command/check | Observed result |
|---|---|
| `python -m pytest -q` with the seven focused PR38 test files | 85 passed |
| `python -m pytest -q scripts/tests` in the isolated locked Python 3.10 environment | 437 passed, 22 skipped, 7 subtests passed; two expected duplicate-ZIP fixture warnings |
| `python -m pytest -q VEGO-AI/tests` | 134 passed |
| `python -m pytest -q tests` | 46 passed |
| `python -m pytest -q VEGO-AI/tests tests` after the quota fix, locked Python 3.10 | 180 passed |
| Protected phase-function call counters, N=0/1/4 | Minimum 4/7/16; maximum 82/143/326; literal fixtures only |
| `python scripts/check_evidence_consistency.py --check` | Three present checks passed; five skipped because their ignored reports are absent, not newly validated |
| `python scripts/check_repository_privacy.py` | PASS |
| `python scripts/security_audit.py --history` | PASS |
| `python scripts/validate_research_records.py schemas/examples` | PASS; grant schema additionally validated by dedicated tests |
| `python scripts/check_quality_ratchet.py` | PASS |
| `python scripts/check_hlayer_change_authorization.py --base origin/main` | PASS; no protected changes |
| Changed-source Ruff and `compileall` | PASS |

Fresh corrected-head CI is still a separate release gate; these local results do not claim that CI ran, that a grant exists, or that the exact AirTravel preflight succeeded. Test fixtures verify all eight renderer outputs and their hashes twice. They are not experimental deliverables.

Final review also caught the legacy CLI success label: a future `TECHNICAL_SUCCESS` receipt would have incorrectly exited 2. A dispatch-only regression first failed, then passed after mapping that status to exit 0; `TECHNICAL_FAILED` still exits 2. The execution function is entirely replaced in that test, so no runtime or grant is constructed.

CI run `33959245561` on correction commit `1518fbd40745acaaf5d7b30d4b1c1f2375b056ca` passed source/security/documents and Python 3.11–3.13, but Python 3.10 failed a byte-quota regression, so merge-gate failed. This was not an authorization or release-manifest failure. The failure was reproduced in an isolated locked Python 3.10 environment: its pathlib caches an opener and bypassed the io.open wrapper. The follow-up guards Path.open explicitly, avoids double wrapping on newer Python versions, and restores it on exit. The original failing regression plus a new exact-byte/restoration test pass in both Python 3.10 and 3.13. No protected file or threshold was changed; packet v3 content hashes were refreshed and remain ungranted.

Release condition: PREFLIGHT_READY_AWAITING_EXPLICIT_AUTHORIZATION only after every local check and every corrected-head CI job passes. Until those checks finish: TECHNICAL_NO_GO. GPL publication/redistribution review does not block private local preflight, but publication is not authorized. Ali still must review packet v3 and issue a separate matching grant. A paid run requires another provider/model/budget/commit/corpus/command authorization.

## WIP reconciliation

The inspected WIP is preserved on local-only `wip/codex-airtravel-pre38-local-only`, never pushed. Fresh corrections began at exact PR38 head; no WIP merge was performed.

| Prior WIP path/group | Disposition |
|---|---|
| scripts/airtravel_fake_runner.py | Only independently tested metadata, fake-response schedule, registry correlation and closure reused in additive airtravel_local_observer.py; old exact runner/fixture entry omitted |
| scripts/airtravel_preflight_support.py | Not copied; incompatible grant/output/cleanup contract replaced |
| scripts/prepare_airtravel_protected_fake_preflight.py | Not copied; corrected PR38 implementation retained and repaired |
| scripts/study1_call_bound.py | Not copied; retained PR38 inventory, added actual source-hash validation |
| scripts/tests/test_study1_call_bound.py | Retained PR38 tests; new source-drift regression separate |
| scripts/prepare_airtravel_reporting.py and test_airtravel_reporting.py | Not copied; repaired PR38 renderer and its tests |
| scripts/airtravel_run_decision_guard.py and its tests | Not copied; paid execution outside this correction |
| scripts/build_airtravel_readiness_evidence.py | Not copied; new narrowly scoped packet builder recomputes evidence |
| scripts/tests/test_airtravel_preflight_preparation.py | Not copied; targeted new PR38 regressions |
| prior static-bound/authorization documents | Not copied; PR38 docs retained, v2 superseded explicitly |
| prior Hebrew template/email/provider decision documents | Not copied; PR38 Hebrew template corrected; email/provider work omitted |
| prior airtravel-preflight/call-sites.json, protected-files.json/.md and source-runtime-receipt.json | Not copied; new evidence independently recomputed |
| prior superpowers plan | Preserved locally only; correction-specific plan added |

No protected modification, real result inspection, exact preflight, provider/paid call, Detector-v1 experimental analysis, force push or merge is authorized or claimed.
