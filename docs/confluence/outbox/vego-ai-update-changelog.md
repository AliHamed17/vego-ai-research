# VEGO-AI Update Changelog

Generated from repository memory on 2026-09-07 16:51 +03:00.

Showing the latest 20 session entries.

## 2026-09-03 23:30 +03:00 - Codex - Final revision of supervisor Q&A task plan

- Request: Refine the operational plan with interaction-log recovery first, one-setting rerun, minimal supervisor requests, and no internal SHA in supervisor artifacts.
- Actions taken:
  - Added interaction-log recovery as Task 1
  - Re-sequenced eight operational tasks and narrowed first rerun to one setting
  - Removed internal revision SHA from DOCX/PDF and regenerated artifacts
- Files changed:
  - docs/research/phd-proposal/2026-09-03-qa-escalation-task-plan.he.md
  - scripts/qa_task_plan_data.py
  - scripts/build_qa_escalation_task_plan.py
  - scripts/build_qa_escalation_task_plan_pdf.py
  - scripts/tests/test_qa_escalation_task_plan.py
- Commands/checks:
  - python -m pytest -q scripts/tests/test_qa_escalation_task_plan.py (2 passed)
  - python scripts/build_qa_escalation_task_plan.py
  - python scripts/build_qa_escalation_task_plan_pdf.py
  - pdftoppm/pdfinfo and visual inspection (3 A4 pages)
- Status: completed; pending final push and CI
- Next steps: Push the focused revision; no study execution until interaction-log recovery and one-setting approval gate.

## 2026-09-04 00:00 +03:00 - Codex - Unify Iris task plan source and harden RTL verification

- Request: Engineering hardening only: canonical JSON source, generated Markdown/DOCX/PDF, content equality tests, bidi scanner, and interaction-log semantic guard; no experiment execution.
- Actions taken:
  - Added scripts/data/qa_task_plan.json as the sole structured plan source
  - Converted qa_task_plan_data.py to a JSON loader
  - Added Markdown generator and deterministic bidi-aware send-gate scanner
  - Removed hard-coded PDF summary rows and task list duplication
  - Added full task-field and summary equality tests
  - Regenerated DOCX and PDF without changing approved supervisor Markdown
- Files changed:
  - scripts/data/qa_task_plan.json
  - scripts/qa_task_plan_data.py
  - scripts/build_qa_escalation_task_plan_md.py
  - scripts/build_qa_escalation_task_plan.py
  - scripts/build_qa_escalation_task_plan_pdf.py
  - scripts/qa_task_plan_send_gate.py
  - scripts/tests/test_qa_escalation_task_plan.py
- Commands/checks:
  - focused task-plan tests: 9 passed
  - compileall: PASS
  - repository privacy: PASS
  - evidence consistency: 18/18 PASS
  - PDF: 3 A4 pages and visual inspection PASS
  - DOCX render unavailable: pdf2image/LibreOffice unavailable; structural QA PASS
- Status: Ready for human review; engineering hardening complete locally, no VEGO-AI experiment executed.
- Next steps: Run full CI after commit; preserve approved supervisor-facing content; no runtime study execution in this change.

## 2026-09-04 01:04 +03:00 - Codex - Audit original VEGO-AI interaction-log availability

- Request: Task 1 only: recover the original historical interaction log read-only.
- Actions taken:
  - Ran deterministic inventory across repository, archives, Downloads, Claude workspace, OneDrive Documents, mounted VEGO-AI Drive, and Codex attachments.
  - Inspected archived evaluator configuration, source, and safe evaluator-log aggregates.
- Files changed:
  - docs/research/phd-proposal/2026-09-04-interaction-log-recovery-receipt.md
  - scripts/find_original_interaction_log.py
  - scripts/tests/test_find_original_interaction_log.py
  - tracking memory updates
- Commands/checks:
  - focused recovery tests: 3 passed
  - compileall: PASS
  - repository privacy: PASS
  - evidence consistency: 18/18 PASS
- Status: Task 1 complete: local search exhausted; original interaction log not found; historical mode conditionally full_content; Q&A baseline unchanged; no experiment, rerun, or API call.
- Next steps: Human decision whether to request the inaccessible original interaction log from Iris/Arnon; do not proceed to instrumentation or rerun.

## 2026-09-04 13:05 +03:00 - Codex - Implement passive Q&A communication contract and offline verification

- Request: Tasks 2–5: freeze baseline terminology, define live contract, implement privacy-safe observer/extractor, verify offline, and prepare one-setting run without live API execution.
- Actions taken:
  - Added qa-communication-event-v1 schema and deterministic append-only observer/projection; corrected frozen extractor F5 semantics to ANSWER_NOT_PERSISTED; documented blocked inputs, cost boundary, and protected-runtime integration gate; ran offline route/parity fixtures.
- Files changed:
  - schemas/qa-communication-event-v1.schema.json
  - VEGO-AI/framework/qa_communication.py
  - VEGO-AI/tests/test_qa_communication.py
  - scripts/extract_qa_escalation_features.py
  - scripts/tests/test_extract_qa_escalation_features.py
  - docs/research/phd-proposal/2026-09-04-qa-baseline-freeze.md
  - docs/research/phd-proposal/2026-09-04-qa-instrumentation-verification.md
  - docs/research/phd-proposal/2026-09-03-qa-escalation-observability.md
  - tracking memory updates
- Commands/checks:
  - offline focused tests: 14 passed; VEGO-AI tests: 120 passed; full tests: 237 passed, 10 skipped, 1 pre-existing merge-base hardening failure; ruff: PASS; compileall: PASS; privacy: PASS; evidence consistency: 18/18 PASS
- Status: Tasks 2–5 partial: observer contract and offline verification pass; protected orchestrator wiring remains pending; all four settings blocked by missing case-model directories; no live LLM/API run.
- Next steps: Obtain reviewed runtime integration authorization and complete case-model inputs before one-setting dry-run/live decision; do not execute real LLM run yet.

## 2026-09-04 23:45 +03:00 - Codex - AirTravel v3.2.1 materialization and verifier hardening

- Request: Final AirTravel materialization and v3.2 verifier hardening
- Actions taken:
  - Downloaded pinned Text2UML codeload archive and verified SHA
  - Materialized ignored five-file runtime pack and provider-disabled config
  - Refactored historical-only audit path and added strict adversarial tests
  - Ran local suites and CI without provider calls
- Files changed:
  - scripts/audit_historical_case_recovery_v3_2.py
  - scripts/materialize_airtravel_runtime_v3_2_1.py
  - scripts/tests/test_audit_historical_case_recovery_v3_2.py
  - docs/research/phd-proposal/2026-09-04-historical-case-recovery-audit-v3.2.1-airtravel-materialization.md
  - docs/research/phd-proposal/historical-case-recovery-v3.2.1/*
- Commands/checks:
  - pytest scripts/tests -q (346 passed, 22 skipped)
  - pytest VEGO-AI/tests -q (134 passed)
  - pytest -q (46 passed)
  - ruff and compileall pass
  - evidence consistency, security, privacy pass
  - GitHub Actions 33917630552 (source gate red; Python matrix pass)
- Status: TECHNICAL NO-GO: protected preflight authorization and CI stale manifest gate remain
- Next steps: Resolve release-manifest gate; obtain protected observer authorization; then rerun offline protected fake preflight before any paid authorization

## 2026-09-04 23:55 +03:00 - Codex - AirTravel v3.2.1 verifier hardening

- Request: Complete final offline AirTravel materialization and v3.2.1 technical gate without provider execution.
- Actions taken:
  - Harden normalized path collision checks; regenerate receipts; run offline checks
- Files changed:
  - v3.2.1 verifier, tests, report and receipts
- Commands/checks:
  - 349 scripts tests; 46 root; 134 VEGO-AI; ruff/compile/privacy/security/evidence pass
- Status: TECHNICAL NO-GO; no provider calls
- Next steps: Resolve protected observer authorization, CI stale release gate, model/budget selection and paid-run authorization before provider execution.

## 2026-09-05 00:00 +03:00 - Codex - AirTravel v3.2.1 adversarial test completion

- Request: Complete offline adversarial coverage and final verification without provider execution.
- Actions taken:
  - Add strict adversarial tests for wrong manifests, mappings, runtime files and configuration
- Files changed:
  - scripts/tests/test_audit_historical_case_recovery_v3_2.py and audit report
- Commands/checks:
  - 353 scripts tests; focused 16; root 46; VEGO-AI 134; ruff compile privacy security evidence pass
- Status: TECHNICAL NO-GO; no provider calls
- Next steps: Synchronize, commit and push; await protected authorization, green CI and explicit paid-run authorization.

## 2026-09-05 00:03 +03:00 - Codex - AirTravel v3.2.1 CI gate recorded

- Request: Record final CI outcomes after pushing the hardened verifier.
- Actions taken:
  - Pushed c9c674e; reproduced CI run 33919095658; source gate stale release manifest and merge gate failed while all four Python jobs passed.
- Files changed:
  - AirTravel v3.2.1 report
- Commands/checks:
  - gh run watch 33919095658; gh run view --log-failed
- Status: TECHNICAL NO-GO; CI red; no provider calls
- Next steps: Human policy process must resolve stale manifest, protected observer authorization, model/budget and paid-run authorization.

## 2026-09-05 00:04 +03:00 - Codex - AirTravel v3.2.1 final CI run recorded

- Request: Record the final reproduced CI outcome and preserve the technical no-go gate.
- Actions taken:
  - Reproduced CI run 33919262015; all Python jobs passed; source freshness gate and merge gate failed.
- Files changed:
  - Final AirTravel materialization report
- Commands/checks:
  - gh run watch 33919262015; gh run view --json jobs
- Status: TECHNICAL NO-GO; no provider calls
- Next steps: Human policy remediation remains required before any paid run.

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
