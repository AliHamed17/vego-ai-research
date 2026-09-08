# Implementation plan — Study 1 AirTravel final offline preflight preparation

**Date:** 2026-09-05. **Branch:** `study1/airtravel-final-offline-preflight-prep`, created from green `main`
`c34d3954b5e080d090017d2ea655d454d75a6b92` (the PR #36 merge commit; main CI run `33923180564`, all six jobs
successful). **Authorization:** Ali Hamed's master execution prompt of 2026-09-05, §0. This plan authorizes
preparation only: the exact protected AirTravel fake preflight is **not executed** in this task, no provider
or paid call is made, Detector-v1 is not run on new experimental data, and no scientific content of v1.0.1
or the v1.0.2 amendment changes.

## Scope

| Deliverable | Path | Action |
|---|---|---|
| Implementation plan (this file) | `docs/superpowers/plans/2026-09-05-airtravel-final-offline-preflight-preparation.md` | add |
| Call-bound proof module | `scripts/study1_call_bound.py` | rewrite: add machine-readable call-site inventory; constants derived from it |
| Call-bound tests | `scripts/tests/test_study1_call_bound.py` | extend: inventory-derived expectations, N∈{0,1,4}, subtotals, fractional/negative rejection, doc consistency, legacy-formula guard |
| Call-bound document | `docs/research/phd-proposal/2026-09-04-one-setting-static-call-bound.md` | update: per-call-site inventory table with line evidence; explicit subtotal sums |
| Preflight harness | `scripts/prepare_airtravel_protected_fake_preflight.py` | add: `--prepare-only` default; execution path defined but gated and not invoked |
| Harness tests | `scripts/tests/test_prepare_airtravel_protected_fake_preflight.py` | add: fixture-only; never invokes the exact protected AirTravel N=4 configuration |
| Post-run renderer | `scripts/render_airtravel_results.py` | add: event log → machine JSON, episode CSV, detector CSV, Hebrew RTL report; residual-token validation |
| Renderer tests | `scripts/tests/test_render_airtravel_results.py` | add: labeled fixture events only |
| Authorization packet v2 | `docs/research/phd-proposal/2026-09-05-airtravel-protected-fake-preflight-authorization-packet-v2.md` | add: supersedes the 2026-09-05 v1 packet (bound to stale main `11cbe04`) |
| Hebrew results template | `docs/research/phd-proposal/2026-09-05-airtravel-preliminary-results-template-he.md` | add: 14 required sections, `{{...}}` machine tokens |
| Hardening manifest | `docs/research/hardening/release-manifest-v3.json` | mechanical regeneration only, verified deterministic ×3, only this file changed by the generator |

## Commit boundaries

1. `Correct Study 1 call-bound proof` — plan, call-bound module/tests/doc.
2. `Prepare exact AirTravel offline preflight harness` — harness, renderer, their tests.
3. `Add preflight authorization packet and results template` — packet v2, Hebrew template.
4. `Refresh hardening manifest for final preflight-preparation tree` — generated manifest only.

Before each commit: fetch origin/main, verify it has not moved from `c34d395`, inspect `git status`, verify
no protected file changed, no ignored external data staged, no credentials staged.

## Protected-path table (all read-only intent)

| Path | Protected reason | SHA-256 at branch base | Intent |
|---|---|---|---|
| `VEGO-AI/framework/orchestrator.py` | forbidden path, `configs/protected-change-authorization-v1.json`; frozen scientific control flow | `fca4b885ee07381db0f02e558b1aebf25bdc7c27da1c471fd3103d7e0e2d5b88` | read-only |
| `VEGO-AI/framework/agent1_language_advisor.py` | forbidden path (same policy) | `13e152fe4ec3b417a8c515bbe1bdb28ff952766579ce1ed6463a7ad9fa5b724e` | read-only |
| `VEGO-AI/framework/agent2_domain_advisor.py` | forbidden path | `fdf330b99295e871ad3cc3e5e934bb04a15f996a5060ea35d43fa13243d16d79` | read-only |
| `VEGO-AI/framework/agent3_model_inspector.py` | forbidden path | `4d0042777040f76abc1ca616a6e1dddcda591ddec54478fa2491b5020a817fa4` | read-only |
| `VEGO-AI/framework/agent4_variability_explorer.py` | forbidden path | `6b043c5643f9211d93ac402a9bf98685727e2cd92cab3377d1462dc3417df2ff` | read-only |
| `VEGO-AI/framework/llm_client.py` | client boundary; hardening allowlist locks content hash | `1a36b4ee860619db97a6ff84ecf64b4845a292ef67cf432c17a86eacd56f55da` | read-only |
| `VEGO-AI/framework/qa_registry.py` | protected runtime (evidence guard) | `ab189d3fd954ea03ba891f5746b36eff8889baeff73d7594f820e68f8762ad5f` | read-only |
| `VEGO-AI/framework/state.py` | protected runtime (evidence guard) | `d8492a623804065b86905d6183979c322d6f83376bf91026e718c615eea1730d` | read-only |
| `VEGO-AI/framework/qa_communication.py` | frozen live-event contract implementation | `9f2cda1dc52fe919be22ac2ea42d61dce3ed22d3fae7ae27077b3db821594236` | read-only (imported) |
| `VEGO-AI/framework/qa_instrumented_runner.py` | reviewed additive harness | `d187f8e8113a86caf24e55720e227f9a5f9b3466126969166bcefb83625a215f` | read-only (imported) |
| `schemas/qa-communication-event-v1.schema.json` | frozen event schema | `7df773a6a141a656b32012abd35c34aab25002f2a873c84e61c9ade06af670b2` | read-only |
| `docs/research/phd-proposal/2026-09-04-qa-escalation-signal-preregistration.md` | v1.0.1, controlling preregistration | `605fba835005fdb167cd8736e5585adc5f57c981681722e29a22d760c33832ea` | read-only |
| `docs/research/phd-proposal/2026-09-04-qa-escalation-signal-preregistration-v1.0.2-airtravel-amendment.md` | v1.0.2 frozen amendment | `6749ab64e2a70755c48152f2a4f976446bbce72a84bb70339aa7bf514d04b7c1` | read-only |
| `docs/research/phd-proposal/text2uml-airtravel/amendment-manifest-v1.0.2.json` | frozen machine manifest | `bd2b7f03585582ff7591d21795fbd3ed4701244d66d26221683520238c2dead2` | read-only |
| `VEGO-AI/eval/*`, `VEGO-AI/eval_output`, `VEGO-AI/inputs` | forbidden paths (policy) | directory-level | read-only |

No required deliverable needs a write to any protected path; the harness injects a fake client only at the
existing `orchestrator.LLMClient` boundary, exactly as the already-reviewed `qa_instrumented_runner.py` does.

## Interfaces

- `study1_call_bound.CALL_SITES`: list of call-site records (path, function, phase, label pattern,
  fixed/per-case, conditional, min/max multiplicity, evidence line). `MIN_BASE`, `MIN_PER_CASE`,
  `WORST_BASE`, `WORST_PER_CASE` are derived by summation from `CALL_SITES`; module import fails if the
  derivation disagrees with the published formulas. Public functions keep their existing signatures;
  `minimum_calls`/`worst_case_calls` additionally reject non-integer inputs.
- `prepare_airtravel_protected_fake_preflight.py`: `--prepare-only` (default), `--runtime-root`,
  `--runtime-archive`, `--output-dir`, `--receipt`; future `--execute` requires
  `--i-have-explicit-authorization` and `--authorization-packet` and is not invoked in this task.
- `render_airtravel_results.py`: `--events`, `--run-sha`, `--model`, `--template`, `--output-root`;
  imports `extract_qa_escalation_features.extract_live_corpus` unchanged (Detector-v1 single-sourced).

## Test commands

`python -m pytest scripts/tests/test_study1_call_bound.py scripts/tests/test_prepare_airtravel_protected_fake_preflight.py scripts/tests/test_render_airtravel_results.py -q`,
then full `pytest tests`, `pytest scripts/tests`, `pytest VEGO-AI/tests`, `ruff check` on new files,
`python -m compileall` on new files, `scripts/check_repository_privacy.py`,
`scripts/check_evidence_consistency.py --check`, `scripts/validate_research_records.py schemas/examples`,
`scripts/security_audit.py` if present, forbidden-claim scan of new documents.

## Stop conditions

Exactly the master prompt §13 list. In particular: any protected-file diff, any main movement at a commit
boundary, any hardening-generator change outside `docs/research/hardening/release-manifest-v3.json`, any
test requiring a provider, any credential in staged content.
