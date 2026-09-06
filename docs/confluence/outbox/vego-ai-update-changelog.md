# VEGO-AI Update Changelog

Generated from repository memory on 2026-09-06 16:19 +03:00.

Showing the latest 20 session entries.

## 2026-09-03 12:07 +03:00 - Codex - Strict one-page human-intervention experiment for Iris

- Request: Create one A4 page only with the paired baseline and controlled human-intervention experiment, preserve evidence boundaries, validate it, and publish the sanitized change to main.
- Actions taken:
  - Created a ten-section one-page experiment design tied to provisional SQ1.
  - Defined three frozen Cheers/ParkWise cases with explicit Condition A and Condition B.
  - Separated automatic, reference-dependent, and manually identified triggers.
  - Kept every evaluative outcome To be measured and removed an exact rehearsal number not yet present on main.
  - Rendered with Microsoft Word, visually inspected the full page, and verified A4 geometry, embedded fonts, content, and hash.
- Files changed:
  - docs/research/phd-proposal/2026-09-03-preliminary-human-intervention-experiment.en.md
  - docs/research/phd-proposal/README.md
  - scripts/build_paper.py
  - scripts/tests/test_preliminary_human_intervention_one_page.py
  - docs/agent-memory/current-state.md
  - docs/agent-memory/progress.md
  - docs/agent-memory/resource-memory.md
- Commands/checks:
  - uv run pytest targeted Study 1 suite: 6 passed, 10 dataset-dependent skips
  - uv run ruff check targeted files: passed
  - PDF semantic QA: one A4 page, 16 required markers, no private path or unsupported rehearsal numbers
  - PDF font embedding: three Calibri subsets embedded
  - repository privacy scan: passed
  - git diff --check: passed
- Status: Ready for Iris review; no human-effectiveness result or supervisor approval is claimed.
- Next steps: Ali sends the one-page PDF; Iris confirms the case/review unit and independent evaluation protocol before any outcome is filled.

## 2026-09-03 12:55 +03:00 - Codex - Iris preliminary-pilot technical evidence audit

- Request: Verify frozen VEGO-AI evidence, human-layer milestones, EXP-005 gate, trigger inventory, real pilot candidates, and deterministic replay boundaries without changing VEGO-AI behavior.
- Actions taken:
  - Added a fail-closed read-only local evidence verifier.
  - Reconciled 179 ranked rows, 165 per-case reports, 83 distinct case IDs, 27 patterns, and the separate paper 178/26 snapshot.
  - Hash-verified Agent 4 analysis copies, audited EXP-005 at 0/24, classified triggers, and documented C1-C4 feasibility and scientific boundaries.
- Files changed:
  - scripts/verify_iris_preliminary_pilot.py
  - scripts/tests/test_verify_iris_preliminary_pilot.py
  - docs/research/phd-proposal/2026-09-03-iris-preliminary-pilot-technical-evidence-map.md
  - docs/research/phd-proposal/2026-09-03-iris-preliminary-pilot-technical-boundary.md
- Commands/checks:
  - uv run pytest scripts/tests/test_verify_iris_preliminary_pilot.py -q => 4 passed
  - uv run pytest -q => 46 passed
  - uv run pytest VEGO-AI/tests -q => 113 passed
  - uv run ruff check focused files => passed
  - scripts/check_repository_privacy.py and scripts/security_audit.py => passed
  - project-health/research-health => research-health blocked by pre-existing tracked Confluence outbox files
- Status: ready for human review
- Next steps: Supervisor approves pilot protocol and human evidence collection; EXP-005 remains blocked at 0/24.

## 2026-09-03 22:42 +03:00 - Codex - Implement Q&A escalation observability study scaffold

- Request: Implement the supervisor-directed Q&A escalation detection milestone while preserving score-replay work as later-stage evidence.
- Actions taken:
  - Read live orchestrator and agent communication paths
  - Extract frozen Q&A questions and confidence inventories
  - Build transparent detector and blind reviewer material
  - Defer C2 111-versus-114 reconciliation
- Files changed:
  - scripts/extract_qa_escalation_features.py
  - scripts/tests/test_extract_qa_escalation_features.py
  - schemas/qa-escalation-event-v1.schema.json
  - docs/research/phd-proposal/2026-09-03-qa-escalation-observability.md
  - docs/agent-memory/current-state.md
  - docs/agent-memory/progress.md
  - docs/agent-memory/issues.md
  - docs/agent-memory/decisions.md
- Commands/checks:
  - python -m pytest -q
  - python -m pytest -q VEGO-AI/tests
  - ruff check scripts/extract_qa_escalation_features.py scripts/tests/test_extract_qa_escalation_features.py
  - python scripts/check_repository_privacy.py
  - python scripts/check_evidence_consistency.py
- Status: completed
- Next steps: Obtain approved answer-level Q&A histories and blind labels; do not run intervention or score-effect replay.

## 2026-09-03 23:06 +03:00 - Codex - Supervisor-facing Q&A task plan

- Request: Create the precise Hebrew operational task list requested by Iris without implementing instrumentation or manual validation.
- Actions taken:
  - Created eight filled tasks with P0/P1/P2 priorities
  - Corrected terminology to ANSWER_NOT_PERSISTED
  - Built ignored RTL DOCX/PDF companions and added plan tests
- Files changed:
  - docs/research/phd-proposal/2026-09-03-qa-escalation-task-plan.he.md
  - scripts/build_qa_escalation_task_plan.py
  - scripts/build_qa_escalation_task_plan_pdf.py
  - scripts/tests/test_qa_escalation_task_plan.py
- Commands/checks:
  - python -m pytest -q scripts/tests/test_qa_escalation_task_plan.py (2 passed)
  - python scripts/build_qa_escalation_task_plan.py
  - python scripts/build_qa_escalation_task_plan_pdf.py
  - pdftoppm/pdfinfo and visual inspection (3 A4 pages)
- Status: completed; ready for supervisor review
- Next steps: Supervisor decides whether descriptive feasibility is acceptable; instrumentation and rerun remain pending.

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
