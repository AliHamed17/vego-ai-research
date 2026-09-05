# AirTravel PR38 hardening implementation plan

> Execution: use superpowers:executing-plans inline. Codex is the sole writer; no delegated writers or concurrent Claude session.

**Goal:** Prepare PR38 for strict independent review, without executing its exact AirTravel preflight or granting execution.

**Architecture:** Extend the existing external contract, observer and two-pass harness, retaining the protected orchestrator byte-for-byte. Validate authorization and reporting through closed machine contracts. Separate preparation, fixture evidence, future fake execution and future paid execution.

**Tech stack:** Python 3.10–3.13, pytest, JSON Schema, SQLite-free file receipts, GitHub Actions.

**Spec:** User's September 5 sequential exclusive-writer request, “Complete and Harden PR #38 End-to-End.” Starting main `c34d3954b5e080d090017d2ea655d454d75a6b92`; starting PR head `b362c55b7c6f7829bf5d99402f77ab015a7417e0`. Intervening commits `1518fbd40745acaaf5d7b30d4b1c1f2375b056ca` and `b362c55b7c6f7829bf5d99402f77ab015a7417e0` are prior Codex corrections, not a newly competing writer.

## Global constraints

- Exact setting `cd_airtravel`, corpus `text2uml_airtravel_253b26dc`, N=4; PUBLIC_EXTERNAL + EXTERNAL_LLM_GENERATED; supervisor approval NOT_DOCUMENTED; paid execution NOT_AUTHORIZED.
- Preserve both scientific amendments and all policy-protected prefixes. No Detector experimental execution, model/provider request, exact fake preflight, actual grant or synthetic corpus.
- Minimum 4+3N and maximum 82+61N, each pass independently: 16..326 at N=4. MAX_QA_ROUNDS=10. Cost TO BE MEASURED.
- Source archive `8cf82e2ab2d2ce3da9a7ec4165e760ae1e0d9af14468f5aa2a3883037d8da701`; runtime archive `e37baecd20a0c84eb1d9b87b3b78a23bc4b4eb8a9824ad3086dc30aa35fdd31f`.
- No raw bytes, private paths, grants, prompts, answers or complete run state in Git. Fresh isolated worktree only. Published commits are never amended or force-pushed.

## File and interface responsibilities

| File | Responsibility and interface |
|---|---|
| `scripts/airtravel_preflight_contract.py` | Pure boundaries: `validate_grant(grant, expected, now=None)`, `authorize(...) -> dict`, `check_counts(a,b) -> dict`, `counters() -> dict`; fail before runtime import. |
| `schemas/airtravel-fake-grant-v1.schema.json` | Extend the existing grant contract, not a second competing validator; require nonce/message binding, implementation and module hashes, frozen runtime map and prohibitions. |
| `schemas/airtravel-fixtures/airtravel-fake-grant.test-only.json` | Non-authorizing expired TEST_FIXTURE_ONLY example; never a real grant. |
| `scripts/airtravel_preflight_execution.py` | Real two-pass control-flow preparation, closed parity assertions, unique identity, containment inventory and truthful counters. |
| `scripts/airtravel_local_observer.py` | Existing exact question/answer correlation and lifecycle; add explicit directed-pair and episode counters without scientific changes. |
| `scripts/airtravel_execution_safety.py` | Preserve cooperative timeout, cancellation, socket denial, credentials restoration and IO quotas; changes only if a named fixture exposes a defect. |
| `scripts/study1_call_bound.py` | Preserve source-bound call inventory; validate actual fake labels against that inventory. |
| `scripts/prepare_airtravel_protected_fake_preflight.py` | Preparation only by default, exact runtime checks and fail-closed execution dispatch. |
| `scripts/render_airtravel_results.py` | Require validated successful receipt and frozen runtime bindings; deterministic nine-output protocol and closed Hebrew prose. |
| `schemas/airtravel-technical-receipt-v1.schema.json` | Machine validation for successful analysis inputs, no defaults for identity or evidence. |
| `scripts/build_airtravel_pr38_packet.py` | Metadata-only generator; explicit implementation commit, private materialization, packet and private exact command. |
| `scripts/tests/test_airtravel_pr38_*.py` | Existing regression baseline plus adversarial grant, parity, lifecycle, safety and report mutations. |
| `scripts/tests/test_render_airtravel_results.py` | Valid receipt fixtures and deterministic output contract. |
| `docs/research/phd-proposal/2026-09-05-airtravel-protected-fake-preflight-authorization-packet-v3.md` | Updated ungranted request binding implementation commit; preserves v2 as superseded history. |
| `docs/research/phd-proposal/airtravel-pr38-correction/*.json` | Sanitized source/runtime/protected receipts generated from actual bytes. |
| `docs/research/phd-proposal/2026-09-05-pr38-hardening-technical-gate.md` | Defect-by-defect inherited/current evidence, commands/results, remaining gates. |
| `docs/research/phd-proposal/2026-09-05-airtravel-paid-run-decision-packet.md` | Proposal only: protected adapter/default, unconfirmed model, cap/concurrency/timeout, cost and human decisions. |
| `docs/research/hardening/release-manifest-v3.json` | Repository generator only, last; three identical generations. |

## Test-first sequence and commit boundaries

- [ ] Baseline: `python -m pytest -q scripts/tests/test_airtravel_pr38_authorization.py scripts/tests/test_airtravel_pr38_lifecycle.py scripts/tests/test_airtravel_pr38_reporting.py scripts/tests/test_airtravel_pr38_safety.py scripts/tests/test_study1_call_bound.py scripts/tests/test_prepare_airtravel_protected_fake_preflight.py scripts/tests/test_render_airtravel_results.py`. Distinguish inherited passing protections from reproduced new failures.
- [ ] Authorization: add mutations to a fully valid fixture, remove each newly required field and require rejection. Example: `with pytest.raises(ValueError): validate_grant({k:v for k,v in valid.items() if k != 'implementation_commit'}, expected)`. Run red, implement strict schema and independently derived bindings, rerun green, commit code/tests.
- [ ] Execution: assert `check_counts(16,17)` rejects, each boundary rejects 15/327, and all canonical counters exist. Add separate valid parity snapshots, mutate one prompt/answer/decision/state/artifact and require rejection. Exercise only literal fixture cases, not the verified AirTravel configuration. Commit tested enforcement and parity changes.
- [ ] Lifecycle: rerun real-loop fixture closure and malformed-event tests. Returning alone never closes CONVERGED. If a required closure lacks an external hook, stop without protected edits.
- [ ] Renderer: start with complete valid receipt; mutate every identity/hash/status/count/containment binding separately. Require `INVALID_OR_INCOMPLETE_ZERO_QA` for unsupported empty results. Assert exact nine filenames, byte-identical repeated outputs and canonical Detector classifications. Commit tested reporting changes.
- [ ] Packet: after code/tests commit, resolve and bind its full SHA; materialize pinned archive in this worktree, verify all 143 source and five runtime files, run prepare-only, and record private receipt hash. Generate packet v3 REQUESTED_NOT_GRANTED, no actual grant. Commit packet and paid decision preparation.
- [ ] Release: run complete scripts, VEGO-AI and root suites; Ruff, compile, privacy/security/evidence/research-record checks. Run `python scripts/build_hardening_manifests.py` three times, compare SHA-256, then `--check`; commit generated manifest last.
- [ ] Fetch/check expected main and remote PR before every commit/push; normal push to existing PR branch, wait for all six fresh CI jobs. No merge or ready-state change.

## Defect interpretation

The request lists 32 defects against an older head. Existing tests and actual source determine current status. Defects 1–5, 7–12, 14–15, 17–24 and 26–31 already have prior correction implementations; they require fresh verification, not fabricated fail-before evidence. Expanded bindings (6), explicit decisions/parity mutation proof (13), canonical counters (16), stronger successful-zero receipt (25), and closed-prose validation (32) require targeted adversarial checks. Each named defect receives an individual final status and test reference; any newly reproduced defect supersedes this initial classification.

## Acceptance matrix

| Gate | Required evidence |
|---|---|
| Exclusive writer | Fresh worktree, same remote head before each push, no unrelated diff |
| Science/protection | Full original/observed hashes, zero protected or amendment byte drift |
| Authorization | Every missing/mismatched field rejected; packet ungranted; actual grant absent |
| Execution safety | Fixture timeout/cancellation, network denial, call caps, path/quota tests |
| Parity | Positive direct/observed fixture plus named negative mutations |
| Lifecycle | Converged/max/incomplete, malformed and concurrency tests |
| Runtime | Archive, 143 source files, five mappings/files, config/reference checks PASS |
| Preparation | Exact prepare-only command exit 0, PREPARED receipt and SHA |
| Reporting | Receipt/schema binding, zero-Q&A rules, nine deterministic files, fixed Hebrew claims |
| Release | All local checks and six fresh CI jobs pass |
| Human boundary | No exact preflight, provider, real grant, paid run or merge |

## Stop, rollback and final state

Stop on unaccounted competing commits (`BLOCKED_CONCURRENT_WRITER`), unavailable/mismatched bytes (`BLOCKED_RUNTIME_BYTES`), required protected lifecycle edits (`BLOCKED_LIFECYCLE_ARCHITECTURE`), or remaining technical failure (`TECHNICAL_NO_GO`). An unfinished check cannot become PASS. Only full acceptance permits `PREFLIGHT_PREPARED_AWAITING_EXPLICIT_GRANT`.

Rollback uses a normal reviewed revert of this task's commits. Preserve other worktrees, WIP and stashes. Private fixture directories are temporary; any material cleanup first verifies the exact local path. No broad clean/reset, no protected rollback without authorization, no automatic retry of execution.
