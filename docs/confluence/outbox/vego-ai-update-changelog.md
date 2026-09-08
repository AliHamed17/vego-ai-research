# VEGO-AI Update Changelog

Generated from repository memory on 2026-09-08 18:26 +03:00.

Showing the latest 20 session entries.

## 2026-09-05 00:06 +03:00 - Codex - AirTravel v3.2.1 receipt completeness finalized

- Request: Finalize machine receipt completeness and preserve no-go status.
- Actions taken:
  - Added call bound, API cost, instrumentation and protected authorization fields to backup evidence receipt; regenerated and pushed.
- Files changed:
  - scripts/audit_historical_case_recovery_v3_2.py and backup receipt
- Commands/checks:
  - offline CLI re-run exit 2 as blocked; git pull rebase and push
- Status: TECHNICAL NO-GO; no provider calls
- Next steps: No further execution; await policy, observer authorization, CI freshness gate and paid-run approval.

## 2026-09-05 00:32 +03:00 - Codex - Final pre-authorization consistency correction

- Request: Remove obsolete current-receipt status token while preserving superseded evidence and keep the gate blocked.
- Actions taken:
  - Current v3.2.1 report now states source/runtime/config PASS and fake preflight BLOCKED_PENDING_AUTHORIZATION without obsolete status wording.
- Files changed:
  - v3.2.1 report
- Commands/checks:
  - git diff check; no provider call
- Status: TECHNICAL NO-GO; final correction pending push
- Next steps: Await explicit fake-preflight authorization, CI green, model/budget and paid-run approval.

## 2026-09-06 00:07 +03:00 - Codex - AirTravel v4 authorization repair

- Request: Repair v4 authorization freshness, nonce/invocation binding, exact command and root enforcement, and receipt validation without executing.
- Actions taken:
  - Added test-first negative coverage for grant windows and identities
  - Hardened manifest, command, layout, attempt and receipt validators
  - Regenerated v4 manifest, preparation records, packet documentation and release manifest
- Files changed:
  - scripts/airtravel_v4_contract.py
  - scripts/airtravel_v4_execution.py
  - scripts/prepare_airtravel_v4.py
  - schemas/airtravel-fake-grant-v2.schema.json
  - schemas/airtravel-technical-receipt-v2.schema.json
  - scripts/tests/test_airtravel_v4_contract.py
  - docs/research/phd-proposal/2026-09-05-airtravel-protected-fake-preflight-authorization-packet-v4.md
  - docs/research/phd-proposal/2026-09-airtravel-v4-correction-record.md
  - docs/research/phd-proposal/airtravel-pr38-correction/airtravel-v4-packet-manifest.json
  - docs/research/hardening/release-manifest-v3.json
- Commands/checks:
  - python -m pytest scripts/tests/test_airtravel_v4_contract.py -q
  - python -m pytest scripts/tests -q
  - python -m pytest VEGO-AI/tests -q
  - python -m pytest tests -q
  - ruff check ...
  - python scripts/security_audit.py --json
  - python scripts/check_repository_privacy.py
- Status: Authorization repair prepared; no execution authorized or performed.
- Next steps: Independent Claude review; do not create or consume a grant; do not execute preflight.

## 2026-09-06 00:19 +03:00 - Codex - AirTravel v4 authorization repair

- Request: Repair the v4 authorization contract and stop before any preflight or provider call.
- Actions taken:
  - Implemented fail-closed grant freshness, identity binding, exact command and private-layout validation, and receipt evidence checks.
  - Regenerated the v4 machine manifest and prepare-only request after code and packet changes.
  - No provider, preflight, Detector-v1, renderer, synthetic generation, or protected runtime modification.
- Files changed:
  - scripts/airtravel_v4_contract.py
  - scripts/airtravel_v4_execution.py
  - scripts/prepare_airtravel_v4.py
  - schemas/airtravel-fake-grant-v2.schema.json
  - schemas/airtravel-technical-receipt-v2.schema.json
  - scripts/tests/test_airtravel_v4_contract.py
  - docs/research/phd-proposal/2026-09-05-airtravel-protected-fake-preflight-authorization-packet-v4.md
  - docs/research/phd-proposal/2026-09-05-airtravel-v4-correction-record.md
  - docs/research/phd-proposal/airtravel-pr38-correction/airtravel-v4-packet-manifest.json
  - docs/research/hardening/release-manifest-v3.json
- Commands/checks:
  - python -m pytest scripts/tests/test_airtravel_v4_contract.py -q
  - python -m pytest scripts/tests -q
  - python -m pytest VEGO-AI/tests -q
  - python -m pytest tests -q
  - ruff check changed AirTravel files
  - python -m compileall -q changed AirTravel files
  - python scripts/check_repository_privacy.py
  - python scripts/security_audit.py --json
  - python scripts/check_evidence_consistency.py --check
  - python scripts/build_airtravel_v4_manifest.py --check
  - python scripts/build_hardening_manifests.py --check
- Status: Authorization repair prepared; awaiting independent review.
- Next steps: Independent review and CI on the consolidated PR head; do not create or consume a grant.

## 2026-09-06 01:54 +03:00 - Codex - AirTravel Study 1 execution evidence reconciliation

- Request: Complete the authorized AirTravel Study 1 evidence package, reconcile the offline fake preflight and the single recorded provider-backed run, and publish truthful Hebrew reports.
- Actions taken:
  - Revalidated final-head fake preflight and private receipt
  - Reconciled provider-run receipts and corrected Hebrew report claims
  - Added six-slide outline and execution-analysis receipt
  - Updated PR #38 description to current truthful status
- Files changed:
  - docs/research/phd-proposal/2026-09-05-study1-airtravel-preliminary-results-he.md
  - docs/research/phd-proposal/2026-09-05-study1-airtravel-presentation-he.md
  - docs/research/phd-proposal/2026-09-05-study1-airtravel-six-slides-he.md
  - docs/research/phd-proposal/2026-09-06-study1-airtravel-execution-and-analysis-receipt.md
- Commands/checks:
  - python -m pytest -q scripts/tests (547 passed, 23 skipped)
  - python -m pytest -q VEGO-AI/tests (134 passed)
  - python -m pytest -q tests (46 passed)
  - ruff check (PASS)
  - python -m compileall -q scripts VEGO-AI (PASS)
  - privacy/security/evidence/manifests (PASS)
  - CI 33997099007 (all six jobs green)
- Status: TECHNICAL_NO_GO: one provider run incomplete; no scientific denominator
- Next steps: Repair answer-correlation instrumentation, validate with malformed-answer fake fixtures, and seek a fresh human decision before any additional provider run.

## 2026-09-06 14:53 +03:00 - Claude - Study 1 transparency correction: retrospective-provenance verdict and unambiguous route columns

- Request: Set the controlling verdict PARTIAL_EVIDENCE_ONLY / DESCRIPTIVE_REPORTING_WITH_RETROSPECTIVE_PROVENANCE everywhere, publish the provenance caveat beside every numeric result and figure, keep Study 2 PREPARED_NOT_EXECUTED and unpooled, replace ambiguous RTL route arrows with explicit asking/answering columns, update PR 38 with a superseding note pointing to PR 41, and run the claim scanner and document validation.
- Actions taken:
  - Set the controlling verdict PARTIAL_EVIDENCE_ONLY / DESCRIPTIVE_REPORTING_WITH_RETROSPECTIVE_PROVENANCE in all five Study 1 supervisor documents and all three print sources.
  - Published the provenance caveat as a banner at document top, as a marker under every table (zero-height CSS marker in print sources), and inline on every figure caption.
  - Replaced arrow route notation with explicit asking-agent / answering-agent columns in the Hebrew results report, study1-results-source.html and fig2-routes.svg.
  - Revoked the supervisor-acknowledgement route to removing the caveat in 2026-09-06-study1-evidence-status-he.md section 6; only a new self-binding receipt can remove it.
  - Documented reporting_code_sha as a generation stamp outside the evidence chain, resolving the mismatch between documents generated at different commits.
  - Regenerated the three Hebrew PDFs via headless Chrome and verified every page image for overlap, clipping and orphan pages; removed an orphan page in the supervisor report.
  - Added a superseding status note to PR 38 pointing reviewers to PR 41 and the provenance caveat, and prepended the controlling verdict to PR 41.
- Files changed:
  - docs/research/phd-proposal/2026-09-06-study1-airtravel-preliminary-results-he.md
  - docs/research/phd-proposal/2026-09-06-study1-airtravel-six-slides-he.md
  - docs/research/phd-proposal/2026-09-06-study1-airtravel-technical-appendix-he.md
  - docs/research/phd-proposal/2026-09-06-study1-airtravel-execution-and-analysis-receipt.md
  - docs/research/phd-proposal/2026-09-06-study1-evidence-status-he.md
  - docs/research/phd-proposal/figures/fig2-routes.svg
  - docs/research/phd-proposal/figures/study1-results-source.html
  - docs/research/phd-proposal/figures/study1-supervisor-report.html
  - docs/research/phd-proposal/figures/study1-technical-appendix.html
  - docs/agent-memory/decisions.md
- Commands/checks:
  - py -3.13 scripts/study1_validate_evidence.py --run-root external_data/airtravel-pr38/v4-real-run --manifest .../output-inventory.json -> PASS_WITH_PROVENANCE_GAPS, 17 PASS, 0 value failures, 3 gaps
  - py -3.13 -m pytest scripts/tests -q -> 596 passed, 23 skipped
  - py -3.13 scripts/check_thesis_citations.py / validate_thesis_content.py / check_repository_privacy.py / check_evidence_consistency.py --check / build_hardening_manifests.py --check / visualization_agent.py --check -> all PASS
- Status: completed
- Next steps: Await CI on head ffe8fc0; Study 2 requires independent preregistration review and fresh authorization before any paid run.

## 2026-09-06 16:19 +03:00 - Claude - Study 1 close-out: 92-check revalidation, C2/C3 correction, RTL figure repair; Study 2 review and preregistration v2

- Request: Finish every legitimate Study 1 analysis and reporting task, prepare Study 2 ON/OFF for preregistration, and produce Hebrew RTL supervisor materials, working only from the accepted private evidence with no provider call and no fabrication.
- Actions taken:
  - Task A: extended the evidence validator from 20 to 92 checks covering rounds, confidence, calls, tokens, cost, the context-only variables, the mapping result, S9 density, and a full cross-check of every derived analysis file against the event-log recomputation. Result: 0 scientific value failures.
  - Found and fixed at source a false zero: airtravel_extended_analytics.py read deviation_patterns.json for a key that does not exist, publishing 0 where the evidence holds 19 recurring fragment patterns.
  - Disclosed a self-inflicted derived-artifact loss: analysis/output-inventory.json was overwritten by a validator invocation pointed at it as --manifest; 144 candidate serializations failed to reproduce the pinned digest, so it was not reconstructed. Status model split into EVIDENCE_INVALID (scientific) versus DERIVED_CHAIN_BROKEN (derived chain).
  - Closed three fail-open holes in the validator itself: NOT_VERIFIABLE was excluded from failures so a deleted derived file passed silently; reporting_code_sha was stamped from a dirty tree; and confidence labels were asserted to be exactly three so a run without High confidence would have failed. Added nine unit tests that assert the validator fails when it should.
  - Task B/C: withdrew the NOT_AVAILABLE claim for C2 and C3 across every document; both are computable (C2 High 15 / Medium 4; C3 true 14 / false 5, n=19 variability patterns).
  - Repaired all four Study 1 SVG figures: direction=rtl with text-anchor=end anchors the left edge, so every label ran off the viewBox and rendered as one or two characters. 29 elements re-anchored, verified by rasterising.
  - Separated the three layers in every document: mapping result (4/4 Satisfied), conversation-state signal, and operational action; recorded that Alternative and Not-Satisfied are never errors and never alert triggers; defined alert in plain language as candidacy for human review.
  - Labelled all fixture-versus-real material as an engineering instrumentation check with separate denominators; removed the instrumentation-quality claim from every proved column.
  - Corrected stale heads, stale CI claims and stale validator counts in PR 38, PR 41, the dashboards and current-state; repaired a malformed table.
  - Task D: independent Study 2 implementation review, verdict NOT_READY_FOR_PAID_AUTHORIZATION. Six of eleven controls are unbound, the single-varying-factor claim is contradicted by the harness's own receipt, and several attestations are hardcoded literals. No Study 2 implementation file was modified.
  - Task E: Study 2 preregistration v2 with a blinded human-rubric primary outcome, secondary descriptive outcomes, an absolute ban on cross-condition alert comparison, purposive N=4, predefined missingness and zero-Q&A handling, a ban on outcome-dependent retry and model switching, paired offline preflight before separate per-condition authorization, and Llama confined to Study 2B.
- Files changed:
  - scripts/study1_validate_evidence.py
  - scripts/airtravel_extended_analytics.py
  - scripts/tests/test_study1_validate_evidence.py
  - docs/research/phd-proposal/2026-09-06-study1-airtravel-preliminary-results-he.md
  - docs/research/phd-proposal/2026-09-06-study1-airtravel-technical-appendix-he.md
  - docs/research/phd-proposal/2026-09-06-study1-airtravel-six-slides-he.md
  - docs/research/phd-proposal/2026-09-06-study1-airtravel-execution-and-analysis-receipt.md
  - docs/research/phd-proposal/2026-09-06-study1-evidence-status-he.md
  - docs/research/phd-proposal/2026-09-06-study2-preregistration-draft.md
  - docs/research/phd-proposal/2026-09-06-study2-implementation-review.md
  - docs/research/phd-proposal/figures/fig1-confidence.svg
  - docs/research/phd-proposal/figures/fig2-routes.svg
  - docs/research/phd-proposal/figures/fig3-episodes.svg
  - docs/research/phd-proposal/figures/fig4-baseline.svg
  - docs/research/phd-proposal/figures/study1-results-source.html
  - docs/research/phd-proposal/figures/study1-supervisor-report.html
  - docs/research/phd-proposal/figures/study1-technical-appendix.html
  - docs/dashboards/results-dashboard.md
  - docs/agent-memory/current-state.md
- Commands/checks:
  - py -3.13 scripts/study1_validate_evidence.py --run-root external_data/airtravel-pr38/v4-real-run --manifest .../analysis/evidence-validation.json -> DERIVED_CHAIN_BROKEN, 92 checks, 87 PASS, 0 scientific value failures, 4 provenance gaps, 1 derived-chain failure
  - py -3.13 -m pytest scripts/tests/test_study1_validate_evidence.py -q -> 9 passed
  - py -3.13 -m pytest scripts/tests -q -> full suite
  - citations / thesis content / privacy / evidence consistency / hardening manifest / visualization catalog / gallery --check -> all PASS
- Status: completed
- Next steps: Study 2 requires Codex to bind six controls and correct the single-factor claim before any paid authorization; the overwritten analysis/output-inventory.json remains unrecovered and is disclosed.

## 2026-09-06 17:03 +03:00 - Codex - Study 1/Study 2 evidence-bound implementation and validation

- Request: Implement and validate the combined Study 1 signal/evidence recovery and Study 2 ON/OFF engineering package without provider execution.
- Actions taken:
  - Implemented fail-closed Study 1 accepted-run recovery and signal traceability with explicit unavailable-evidence status.
  - Added Study 2 ON/OFF system-comparison fixture runner with strict schemas, caps, timeout, privacy, path, retry and no-Q&A controls.
  - Added explicit Study 1 producing-agent/phase and rounds-per-episode aggregate tables; no numeric values generated without a bound private event log.
  - Selected PR #41 descendant as canonical draft and ported only the Study 2 contract from divergent PR #42.
- Files changed:
  - scripts/study1_evidence_recovery.py
  - scripts/study1_validate_evidence.py
  - scripts/build_study1_signal_traceability.py
  - src/vego_study2/
  - scripts/study2_on_off_experiment.py
  - schemas/study1-evidence-binding-v1.schema.json
  - schemas/study2-*.schema.json
  - docs/research/phd-proposal/study1-*
  - docs/research/phd-proposal/study2-*
  - scripts/tests/test_study1_*.py
  - scripts/tests/test_study2_contract.py
  - tests/test_study2_*.py
- Commands/checks:
  - focused pytest: 66 passed
  - root pytest: 71 passed
  - VEGO-AI pytest: 134 passed
  - scripts pytest: 654 passed, 22 skipped, 2 warnings, 7 subtests
  - scoped Ruff: PASS; full Ruff baseline: 159 pre-existing findings
  - privacy/evidence/security/compile/schema checks: PASS
- Status: Implemented and locally validated; Study 1 accepted private evidence unavailable in reviewed worktree; Study 2 fixture prepared but not executed as science.
- Next steps: Independent review of the canonical branch; supply the explicitly mounted accepted-run binding/event log if descriptive numeric reporting is required; separately authorize any future provider run.

## 2026-09-07 13:28 +03:00 - Claude - Study 1B variance preregistered and prepared; binding-manifest obstacle recorded

- Request: Continue and save all work.
- Actions taken:
  - Rebased the Study 1B variance work onto three new Codex commits on the shared branch; no conflicts. Full scripts suite 674 passed, 23 skipped.
  - Accepted Codex's corrections to the detector signal-map memo: my claim that the Agent-4 mechanism DOES write human_review_queue.jsonl overstated it (the queue builder is invoked conditionally), and their scoping of the absence to this worktree is safer than asserting the run produced none.
  - Verified Codex's new evidence-binding mode gate: retrospective_validation requires created_after_run=true, so a manifest written today cannot be promoted to prospective. That removes the mislabelling risk originally raised against D0 option (a).
  - Found a deeper obstacle and did NOT create the binding manifest: the schema requires execution_code_sha256, which the accepted run's receipt does not bind and which nothing can therefore cross-check, and a pipeline_output_manifest that the accepted run never produced. Recorded as decision-table section 5.2 and D0 was re-scoped accordingly.
  - Regenerated all four Hebrew PDFs after Codex edited the memo print source; memo remains two pages.
  - Confirmed OPENAI_API_KEY is still absent, so no provider call was made and none could have been.
- Files changed:
  - scripts/airtravel_real_run.py
  - scripts/study1b_variance_runs.py
  - scripts/tests/test_study1b_variance_budget.py
  - docs/research/phd-proposal/2026-09-06-study1b-variance-preregistration.md
  - docs/research/phd-proposal/2026-09-06-final-decision-table.md
  - docs/research/hardening/release-manifest-v3.json
- Commands/checks:
  - git rebase origin/study1/closure-and-study2-prep -> clean, 1 commit replayed
  - py -3.13 -m pytest scripts/tests -q -> 674 passed, 23 skipped
  - hardening manifest / visualization catalog / gallery / privacy / evidence consistency / BigUI catalog --check -> all PASS
  - OPENAI_API_KEY presence check -> absent; no provider call attempted
- Status: completed
- Next steps: Awaiting OPENAI_API_KEY to execute the five Study 1B repeats under the USD 2 ceiling, a decision on D0 given decision-table section 5.2, and a decision on whether Claude may close the Study 2 egress and call-site-test gaps on Codex's PR 42 branch.

## 2026-09-07 15:21 +03:00 - Codex - Study 2 ON/OFF enforcement and Study 1B independent gate

- Request: Review PR #41 Study 1B before execution and harden Study 2 ON/OFF controls without provider or experiment execution.
- Actions taken:
  - Reviewed PR #41 successor and rejected Study 1B execution because frozen five-repeat protocol is budget-blocked.
  - Enforced offline-only model/configuration, cost/token/call ceilings, timeout/retry controls, egress blocking, strict OFF schema, receipt self-binding, provenance hashes, and fail-closed CLI/helpers.
- Files changed:
  - src/vego_study2/runner.py
  - src/vego_study2/fixtures.py
  - scripts/study2_on_off_experiment.py
  - schemas/study2-result-v1.schema.json
  - schemas/study2-run-receipt-v1.schema.json
  - schemas/study2-on-off-comparison-v1.schema.json
  - tests/test_study2_on_off.py
  - scripts/tests/test_study2_contract.py
  - docs/research/phd-proposal/2026-09-07-study2-control-hardening.md
  - docs/research/phd-proposal/study2-on-off-readiness-v1.json
  - docs/research/phd-proposal/2026-09-06-study2-readiness-note.he.md
  - docs/research/hardening/release-manifest-v3.json
- Commands/checks:
  - Focused pytest: 54 passed
  - CI run 34121059938: all six jobs passed
  - Focused Ruff, compile, schemas, privacy, security, evidence consistency: passed
- Status: completed; PR remains draft/open/unmerged; no provider, model, experiment, or credentials
- Next steps: Independent human review, freeze provider/model/budget, and issue separate one-time execution grant before any real run.

## 2026-09-07 16:51 +03:00 - Codex - Study 1B closure and bounded pilot readiness

- Request: Implement the attached Study 1B closure and separate budget-constrained exploratory pilot preparation without provider execution.
- Actions taken:
  - Closed Study 1B under frozen budget
  - Added fail-closed three-repeat offline pilot controller and receipts
  - Added truncation, reservation, privacy, schema, and no-provider tests
  - Added Hebrew technical note and email draft
  - Refreshed hardening manifest and verified head-specific CI
- Files changed:
  - scripts/pilot_budget_constrained_runner.py
  - scripts/pilot_budget_constrained_preflight.py
  - scripts/study1b_variance_runs.py
  - scripts/study1b_offline_preflight.py
  - schemas/pilot-repeat-receipt-v1.schema.json
  - docs/research/phd-proposal/2026-09-06-budget-constrained-exploratory-pilot-preregistration.md
  - docs/research/phd-proposal/2026-09-06-study1b-variance-preregistration.md
  - docs/research/phd-proposal/2026-09-06-study1b-codex-review-request.md
  - docs/research/phd-proposal/2026-09-06-pilot-codex-review-request.md
  - docs/research/phd-proposal/2026-09-07-study1b-pilot-technical-note.he.md
  - docs/research/phd-proposal/2026-09-07-study1b-pilot-email-draft.he.md
- Commands/checks:
  - uv run python -m pytest -q -p no:cacheprovider VEGO-AI/tests scripts/tests tests/hlayer_offline tests
  - uv run ruff check on changed files
  - uv run python scripts/build_hardening_manifests.py --check
  - GitHub Actions run 34129167954
- Status: completed
- Next steps: Independent review; mount accepted private evidence before any Study 1 numeric report; obtain separate explicit provider authorization for any future pilot.

## 2026-09-07 23:46 +03:00 - Codex - Study 1 transparency package

- Request: Build sanitized evidence, log, and Detector transparency package for supervisor review.
- Actions taken:
  - Added evidence-bound provenance and release verification
  - Added log-contract, signal dictionary, detector criteria, metrics, Hebrew note, slides, and email
  - Added privacy/schema/tests and regenerated supported release manifest
- Files changed:
  - scripts/build_study1_transparency_package.py
  - scripts/tests/test_study1_transparency_package.py
  - schemas/study1-data-provenance-v1.schema.json
  - docs/research/phd-proposal transparency package
- Commands/checks:
  - focused package tests; full scripts tests; root and VEGO-AI tests; changed-scope Ruff and compile; verify-source; security/evidence checks
- Status: completed; private accepted evidence unavailable in reviewed worktree
- Next steps: Human/supervisor review; mount and validate private accepted-run binding manifest before any scientific metrics

## 2026-09-07 23:48 +03:00 - Codex - Study 1 transparency package finalization

- Request: Finalize the sanitized supervisor transparency package under the no-new-experiment boundary.
- Actions taken:
  - Revalidated staged privacy and schema outputs
  - Updated shared project memory with evidence boundary and next gate
- Files changed:
  - docs/agent-memory/current-state.md
  - docs/agent-memory/progress.md
  - docs/agent-memory/issues.md
  - docs/agent-memory/decisions.md
  - docs/agent-memory/resource-memory.md
  - docs/agent-memory/session-log.md
- Commands/checks:
  - focused transparency tests; changed-scope Ruff; compileall; staged privacy and JSON/CSV checks
- Status: completed; scientific evidence unavailable in reviewed worktree
- Next steps: Push one draft-PR update and await supervisor review; mount private binding manifest before numeric reporting

## 2026-09-08 00:11 +03:00 - Codex - Transparency manifest and clean-checkout hardening

- Request: Extend the Study 1 transparency package with a safe generated-figures manifest and clean-checkout fallback.
- Actions taken:
  - Added three-entry rule-only figures manifest
  - Removed dependency on deleted legacy signal dictionary through a descriptive fallback
  - Re-ran full verify-source successfully
- Files changed:
  - scripts/build_study1_transparency_package.py
  - scripts/tests/test_study1_transparency_package.py
  - docs/research/phd-proposal/study1-transparency-figures-manifest-v1.json
- Commands/checks:
  - 11 focused tests; verify-source PASS; hardening manifest check
- Status: completed; no scientific evidence generated
- Next steps: Commit/push package for draft PR review; wait for private evidence binding and supervisor review

## 2026-09-08 00:21 +03:00 - Codex - Study 1 transparency package CI and PR finalization

- Request: Finalize the sanitized Study 1 data/log/pattern transparency package, refresh the hardening manifest, verify green CI on the pushed head, and update PR #41 metadata.
- Actions taken:
  - Refreshed release-manifest-v3 through the supported builder after CI freshness failure; pushed commit 60db152; dispatched workflow 34162596621 and verified all six jobs passed; updated PR #41 description with final head, provenance, evidence boundary, and supervisor-review status.
- Files changed:
  - docs/research/hardening/release-manifest-v3.json
  - PR #41 metadata only
- Commands/checks:
  - git fetch origin --prune
  - uv run python scripts/build_hardening_manifests.py
  - gh workflow run supervisor-package.yml --ref study1/closure-and-study2-prep
  - gh run view 34162596621 --json status,conclusion,headSha,jobs
  - gh pr edit 41 --body <sanitized final status>
- Status: READY FOR SUPERVISOR TRANSPARENCY REVIEW — NOT A NEW SCIENTIFIC RESULT; CI green on 60db152; private accepted-run evidence remains unavailable in the reviewed worktree.
- Next steps: Mount and validate the accepted private binding manifest/event log; semantically rebase PR #41 onto current origin/main 158714064; obtain supervisor and independent review before any scientific reporting or merge.

## 2026-09-07 11:52 +03:00 - Claude - Literature evidence-closure audit: protocol audit, gap-refutation matrix, claim audit

- Request: Perform a strict evidence-closure audit of the current literature review, test GAP-1/GAP-2/GAP-3 adversarially, audit the five registered query families, and prepare the execution-ready search corpus. Do not rewrite Chapter 2.
- Actions taken:
  - Re-verified 54 of 68 proposal references against external records (51 DOIs via Crossref; [13] via ACM DL; [52] via arXiv; [54] via IJCAI index; [60] via PMLR; [61] via NeurIPS)
  - Searched the two adjacent literatures Section 2.6 names as likeliest refuters (BPM work-item/resource allocation; knowledge-base curation/truth maintenance/belief revision) plus organisational memory and expert routing
  - Assessed 35 candidate refuters and mapped 28 high-priority papers (24 Tier A, 4 Tier B) with 45 extraction fields each
  - Classified 37 Chapter 2 absence/novelty claims: 22 SUPPORTED, 9 NEEDS_NARROWING, 2 LIKELY_FALSE, 4 UNVERIFIED, 0 REFUTED
  - Gap verdicts: GAP-1, GAP-2 and GAP-3 all NARROWED; none refuted
  - Found that the QL-05 substrate conjunction structurally prevents the registered generic terms from reaching the BPM and provenance literatures, and that the 2026-07-30 repo register defines five different query families from proposal Section 4.3 Table 3
  - Recommended a frozen pre-execution protocol amendment including a new QL-06 adjacent-refuter family run without the substrate conjunction
- Files changed:
  - literature/2026-09-06-gap-refutation-matrix.csv
  - literature/2026-09-06-high-priority-literature-map.csv
  - docs/research/phd-proposal/2026-09-06-literature-search-protocol-audit.md
  - docs/research/phd-proposal/2026-09-06-chapter2-claim-audit.md
- Commands/checks:
  - curl Crossref REST /works (51 DOI lookups + 42 bibliographic queries)
  - OpenAlex via WebFetch (4 queries)
  - python CSV validation battery: structure, duplicate DOI, duplicate title, tier, gap-claim consistency - all PASS
- Status: completed
- Next steps: Reviewer/orchestrator (ChatGPT) to accept or return the evidence audit. Chapter 2 NOT rewritten pending acceptance. Supervisor decisions open: freeze the amended protocol before execution; resolve single-rater screening; adopt GAP-1 replacement wording; tighten the SQ2 refutation condition.

## 2026-09-08 01:59 +03:00 - Codex - Study 1 supervisor transparency correction integration

- Request: Implement the nine-blocker supervisor-transparency correction package on the live PR branch without provider or experiment execution.
- Actions taken:
  - Integrated current origin/main safely with tracking-history conflict resolution
  - Preserved Agent-4 causal-path, deterministic selection, case-model availability, S6, worked-example, CI, and byte-identity corrections
  - Validated public provenance and sanitized outputs
- Files changed:
  - transparency package scripts, schemas, tests, generated documentation and workflow; no private artifacts
- Commands/checks:
  - targeted and full pytest suites
  - Ruff and compileall
  - privacy, security, evidence consistency and manifest checks
- Status: completed; awaiting PR CI and human review
- Next steps: Review CI and supervisor package; mount private evidence only through its binding manifest before numeric reporting

## 2026-09-08 07:35 +03:00 - Codex - Study 1 supervisor transparency correction and CI hardening

- Request: Implement the nine-blocker Study 1 transparency corrections, harden cross-platform Study 2 output containment, refresh deterministic manifests, and verify complete offline suites and CI.
- Actions taken:
  - Corrected Agent-4 path, case/model availability, canonical S6, C1/C2/C3, worked example, CI coverage, byte-identity wording, portable symlink checks, and generated manifests; ran offline suites, privacy/security gates, clone-safe verifier, and green six-job CI.
- Files changed:
  - src/vego_study2/paths.py; VEGO-AI-Thesis-Baseline-Progress.html; docs/research/thesis-evidence/THESIS_REVIEW_PACKAGE_MANIFEST.json; docs/research/hardening/release-manifest-v3.json
- Commands/checks:
  - Full scripts/root/VEGO-AI pytest suites; Ruff; compileall; privacy/security/evidence checks; verify-source.ps1; gh run watch 34187274766
- Status: completed
- Next steps: Supervisor review of the transparency package; private accepted-run evidence remains unavailable in this worktree; no scientific reporting or merge until reviewed.

## 2026-09-08 16:08 +03:00 - Claude - Study 1 instrument experiments: extended envelope truth table, log robustness, cost calibration, adversarial review corrections

- Request: Keep running experiments under the USD 6 authorisation: more results, more baselines, gaps not checked before, high quality; show a PDF with all results.
- Actions taken:
  - Added scripts/airtravel_detector_envelope_extended.py: nine deterministic fixture modes drive the protected orchestrator; 9/9 conform with exact signal sets; WEAK_ALERT, S1, S2, S3 (empty and null encodings) and S6 are each reached in isolation end-to-end; orchestrator output goes to a gitignored scratch dir under external_data and is deleted after projection; provider-SDK module audit after each mode.
  - Added scripts/study1_instrument_robustness.py on the accepted log: event-order invariance 500/500 permutations + 3 named reorderings; value domain clean (44 answers, Low 16 / Medium 25 / High 3, no UNKNOWN, no missing evidence); denominator sensitivity; aggregation sensitivity with the frozen rule re-applied per summary (0 of 3 classifications depend on the any aggregation; the S1 signal in 1 of 3 episodes does; S7 preserves that episode).
  - Added scripts/study1_cost_calibration.py: reserve-to-actual 6.77x (Study 1B bound) and 2.08x (pilot bound) on the one receipt; 16 of 30 enumerated protocols fit USD 6.00, 5 fit USD 2.00; Study 1B frozen bound 34.6551; per-call maxima and per-episode cost NOT_AVAILABLE; bounds are reserve bounds under the 8,000-token input-reserve assumption.
  - Folded the three analyses into the results dossier (sections 2, 8, 11; authorisation block with credential presence measured at build time and a receipt scan; NOT_AVAILABLE degradation when an analysis file is missing) and regenerated the three-page Hebrew PDF locally (gitignored).
  - Ran an adversarial review workflow (3 lenses, 27 agents, paired refuters). Fixed the confirmed blocking finding: the first draft compared confidence labels instead of re-applied classes and claimed one classification depended on the any aggregation; the max-rounds episode stays STRONG_ALERT through S7, so the claim was withdrawn and a correction record added. Also fixed ledger-row indexing under concurrency, the non-reentrant mode swap, the majority vs ordinal-median mislabel, the leave-one-out denominator, hard-coded literals, novelty wording and loanwords, and temp residue (removed 44 fixture-output directories containing corpus text from system TEMP).
  - Wrote docs/research/phd-proposal/2026-09-08-study1-instrument-experiments-addendum.md, indexed it in the proposal README, added decision D8 and new descriptive/engineering rows to the final decision table, and updated current-state, progress, issues (ISS-060 open, ISS-061 resolved) and decisions.
  - OPENAI_API_KEY absent (presence-only check); USD 6.00 authorisation unused; provider calls 0; Detector-v1 unchanged.
- Files changed:
  - scripts/airtravel_detector_envelope_extended.py
  - scripts/study1_instrument_robustness.py
  - scripts/study1_cost_calibration.py
  - scripts/build_study1_results_dossier.py
  - scripts/render_study1_results_dossier.py
  - scripts/tests/test_airtravel_detector_envelope_extended.py
  - scripts/tests/test_study1_instrument_robustness.py
  - docs/research/phd-proposal/2026-09-08-study1-instrument-experiments-addendum.md
  - docs/research/phd-proposal/2026-09-06-final-decision-table.md
  - docs/research/phd-proposal/README.md
  - docs/research/phd-proposal/figures/study1-results-dossier.html
  - docs/research/hardening/release-manifest-v3.json
  - docs/agent-memory/current-state.md
  - docs/agent-memory/progress.md
  - docs/agent-memory/issues.md
  - docs/agent-memory/decisions.md
- Commands/checks:
  - py -3.13 -m pytest scripts/tests -> 778 passed, 23 skipped
  - py -3.13 scripts/build_hardening_manifests.py; --check -> PASS
  - check_repository_privacy, check_evidence_consistency --check, check_hlayer_change_authorization --base origin/main, security_audit --history -> PASS
  - headless Chrome print of docs/research/phd-proposal/figures/study1-results-dossier.html -> 3-page PDF (gitignored)
  - Workflow study1-new-experiments-adversarial-review (27 agents; 1 verifier hit the session limit)
- Status: completed; ENGINEERING_FIXTURE_NOT_SCIENTIFIC and descriptive instrument analyses only; 0 provider calls; Detector-v1 unchanged
- Next steps: Commit and push to study1/closure-and-study2-prep (PR #41) and confirm CI. To spend under the USD 6.00 authorisation: set OPENAI_API_KEY in the execution environment, close pilot gate 4 (independent review) and gate 6 (frozen model, ceiling, caps), preregister exactly one reserve-bound menu row (D8), then run with BudgetGuard at 6.00. Candidate zero-cost follow-ups: mixed-confidence multi-answer fixture episodes; a per-call ledger in the real-run harness so maxima and per-episode cost stop being NOT_AVAILABLE.

## 2026-09-08 18:18 +03:00 - Codex - Study 1 Hebrew supervisor E2E readout

- Request: Produce and verify a concise Hebrew RTL Study 1 supervisor package on PR #41.
- Actions taken:
  - Created a six-page RTL readout and six-slide RTL deck with evidence boundaries and visual QA.
  - Added a safe evidence index and Hebrew supervisor email draft.
  - Ran local tests, privacy/evidence/security checks, and green CI on the package commit.
- Files changed:
  - docs/research/phd-proposal/2026-09-08-study1-e2e-supervisor-readout-he[PDF omitted]
  - docs/research/phd-proposal/2026-09-08-study1-e2e-supervisor-slides-he.pptx
  - docs/research/phd-proposal/2026-09-08-study1-e2e-supervisor-slides-he[PDF omitted]
  - docs/research/phd-proposal/2026-09-08-study1-e2e-evidence-index.md
  - docs/research/phd-proposal/2026-09-08-study1-supervisor-email-he.md
- Commands/checks:
  - python -m pytest scripts/tests -q -p no:cacheprovider
  - CI run 34243313635
- Status: completed
- Next steps: Independent supervisor-package review; no new empirical claim or provider run is authorized by this documentation package.
- Git commit: `90ddf83a8644638afaa3165c28fa0a98c06aa033` (`docs: add bounded Hebrew Study 1 supervisor readout`).
