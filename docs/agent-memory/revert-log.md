# Revert Log

Record file changes and rollback notes here.

## 2026-07-27 - Codex - Evaluation Phase Branch & Supervisor Checklist

- Files added:
  - `docs/research/evaluation-run-guide.md`
  - `docs/research/supervisor-label-approval-checklist.md`
- Files updated:
  - `docs/research/supervisor-label-approval-pack.md` (appended sign-off checklist reference section 8)
- Git branch: `feature/evaluation-phase` created and active.
- Rollback note: Delete `docs/research/evaluation-run-guide.md` and `docs/research/supervisor-label-approval-checklist.md`, revert `docs/research/supervisor-label-approval-pack.md`, and switch back to `main` branch (`git checkout main`).

## 2026-07-27 - Codex - Evaluation Phase Branch & Supervisor Checklist

- Files added:
  - `docs/research/evaluation-run-guide.md`
  - `docs/research/supervisor-label-approval-checklist.md`
- Files updated:
  - `docs/research/supervisor-label-approval-pack.md` (appended sign-off checklist reference section 8)
- Git branch: `feature/evaluation-phase` created and active.
- Rollback note: Delete `docs/research/evaluation-run-guide.md` and `docs/research/supervisor-label-approval-checklist.md`, revert `docs/research/supervisor-label-approval-pack.md`, and switch back to `main` branch (`git checkout main`).

## 2026-07-20 22:22 +03:00 - Codex - July 21 Supervisor Package And Repository Hardening

- Files changed:
  - ProgramStatusSnapshot v1, Iteration 14 ledger/registry/tracker/dashboard/handoff surfaces, and safe future-proposal rewrites.
  - VEGO-AI-July1-PointByPoint-EN-HE.html plus July 21 canonical package data, Markdown records, deck source/output, and PDF builders.
  - Visualization gallery/research hub, CI workflow, privacy check, browser smoke test, package validator, and verify-hlayer-all.ps1.
  - Agent memory session/revert logs and archives; archive conservation was verified with zero missing or changed historical entries.
- Rollback note: Revert the July 21 package commits to remove tracked package/governance/gallery/QA changes; delete only the dated 2026-07-21 share folder and ignored PDF/log outputs if those copies must be withdrawn. Do not alter July 15 history, raw ASR, Agent 4, protected VEGO-AI runtime paths, baseline outputs, or EXP-005 labels.
- Git commit: none recorded by script.
## 2026-07-24 20:24 +03:00 - Codex - Thesis accuracy-evidence advancement package

- Files changed:
  - docs/research/thesis-evidence/**
  - experiments/EXP-019-* through EXP-027-*
  - thesis/chapters/**
  - thesis/output/VEGO-AI-MSc-Thesis-Evidence-Ready-Draft-2026-07-24.docx
  - VEGO-AI-Thesis-Baseline-Progress.html
  - scripts/build_thesis_*
  - schemas/*.schema.json
- Rollback note: All changes are documentation, experiment planning, validation, or shareable artifacts. Revert this change set; no protected runtime path, Agent 4 behavior, baseline output, or expert label was modified.
- Git commit: none recorded by script.

## 2026-07-24 22:28 +03:00 - Codex - Thesis evidence release finalization

- Files changed:
  - schemas/** and schema examples
  - scripts/build_thesis_*.py, validators, tests, and CI workflow
  - experiments/EXP-019-* through EXP-027-* and thesis chapters
  - VEGO-AI-Thesis-Baseline-Progress.html and thesis/output/*.docx
  - docs/research/thesis-evidence/**, research hub, gallery, and visualization catalog
  - docs/agent-memory/**, docs/PROGRESS_TRACKER.md, and .gitignore
- Rollback note: Revert the focused branch commits or the final squash commit to remove the thesis evidence package. Local ignored PDF, page renders, delivery manifest, and share copies may be deleted separately. No protected runtime, Agent 4, baseline output, or expert-label file was changed.
- Git commit: none recorded by script.

## 2026-07-25 16:08 +03:00 - Codex - Unified runtime, security hardening, and thesis release

- Files changed:
  - src/vego_hlayer/**
  - VEGO-AI/framework human-review M1-M4B-1 files only
  - scripts/** hardening, validation, manifest, and document tooling
  - docs/research/** and docs/agent-memory/**
  - thesis/**, VEGO-AI-Thesis-Baseline-Progress.html, .github/workflows/**
- Rollback note: Revert the focused commits from the feature branch; legacy remains the default and baseline artifacts are unchanged.
- Git commit: none recorded by script.

## 2026-07-25 22:17 +03:00 - Codex - Unified runtime final review and release hardening

- Files changed:
  - VEGO-AI/framework/llm_client.py
  - src/vego_hlayer/adapters.py
  - tests and protected-change authorization
  - docs/research/h-layer/program-status-snapshot-v1.json
  - thesis evidence HTML, DOCX, manifests, and appendix
- Rollback note: Revert the final focused commits in reverse order; baseline Agent 4 outputs were never modified.
- Git commit: none recorded by script.

## 2026-07-25 22:53 +03:00 - Codex - Close exact-head unified runtime review gaps

- Files changed:
  - VEGO-AI/framework/hlayer_architecture.py and focused regression test
  - src/vego_hlayer/runtime.py and offline parity regression
  - scripts/security_audit.py and history regression
  - configs/protected-change-authorization-v1.json
  - thesis evidence HTML, figures, DOCX, and manifests
  - docs/agent-memory current state, progress, issues, session and revert logs
- Rollback note: Revert commits after f704239 in reverse order; tracked package and runtime hardening roll back together. Local ignored PDF, page renders, and share copies may be removed separately. Agent 4 and baseline outputs were never changed.
- Git commit: none recorded by script.

## 2026-07-25 23:17 +03:00 - Codex - Close final PR review gaps and republish verified thesis package

- Files changed:
  - src/vego_hlayer/io_safety.py
  - src/vego_hlayer/adapters.py
  - scripts/security_audit.py
  - scripts/tests/test_security_audit.py
  - tests/hlayer_offline/test_io_safety.py
  - tests/hlayer_offline/test_unified_runtime.py
  - docs/research/thesis-evidence/*
  - docs/research/hardening/release-manifest-v3.json
  - VEGO-AI-Thesis-Baseline-Progress.html
  - thesis/output/VEGO-AI-MSc-Thesis-Evidence-Ready-Draft-2026-07-25.docx
- Rollback note: Revert commits 0c2fcbb, e301ef0, and 7a65266 to remove this final review wave and its regenerated package metadata; ignored PDF and share copies can be deleted independently.
- Git commit: none recorded by script.

## 2026-07-25 23:35 +03:00 - Codex - Bind external authorization trust and transactional CLI publication

- Files changed:
  - .github/workflows/supervisor-package.yml
  - scripts/check_hlayer_change_authorization.py
  - scripts/run_hlayer_architecture.py
  - scripts/tests/test_change_authorization.py
  - scripts/tests/test_hlayer_architecture_cli.py
  - docs/research/thesis-evidence/*
  - docs/research/hardening/release-manifest-v3.json
  - VEGO-AI-Thesis-Baseline-Progress.html
  - thesis/output/VEGO-AI-MSc-Thesis-Evidence-Ready-Draft-2026-07-25.docx
- Rollback note: Revert commits 78c7442, bc9522f, and 951c68d; unset local Git config vego.hlayerAuthorizationSha256 and repository variable H_LAYER_AUTHORIZATION_SHA256 if abandoning this authorization trust mechanism.
- Git commit: none recorded by script.

## 2026-07-25 23:50 +03:00 - Codex - Repair clone-safe authorization integration tests

- Files changed:
  - scripts/tests/test_hlayer_hardening.py
  - docs/research/hardening/release-manifest-v3.json
- Rollback note: Revert commits 4b46b2e and d9f0c44 to remove the clone-safe test fixture and its release hash refresh.
- Git commit: none recorded by script.

## 2026-07-26 00:31 +03:00 - Codex - Exact-head security review and release verification

- Files changed:
  - scripts/security_audit.py
  - scripts/check_hlayer_change_authorization.py
  - src/vego_hlayer/adapters.py
  - scripts/tests/
  - docs/research/h-layer/
  - docs/research/hardening/
  - docs/research/thesis-evidence/
  - thesis/
  - VEGO-AI-Thesis-Baseline-Progress.html
- Rollback note: Revert commits 14ec374 through d7646f2 in reverse order to remove this final review-fix cycle; local ignored PDF, QA pages, and dated share folders can be removed separately. Agent 4 outputs and expert labels were not changed.
- Git commit: none recorded by script.

## 2026-07-26 01:00 +03:00 - Codex - Close final validation and provenance review findings

- Files changed:
  - src/vego_hlayer/adapters.py
  - scripts/run_hlayer_architecture.py
  - scripts/check_hlayer_change_authorization.py
  - scripts/tests/test_hlayer_architecture_cli.py
  - scripts/tests/test_change_authorization.py
  - docs/research/h-layer/
  - docs/research/hardening/
  - docs/research/thesis-evidence/
  - thesis/
  - VEGO-AI-Thesis-Baseline-Progress.html
- Rollback note: Revert commits a6c2b42 through 9995804 in reverse order to remove this final review-fix and republishing cycle; ignored PDF, QA, and dated share folders can be removed independently. Agent 4 outputs and expert labels were not changed.
- Git commit: none recorded by script.

## 2026-07-26 01:13 +03:00 - Codex - Address exact-head envelope and archive review findings

- Files changed:
  - src/vego_hlayer/adapters.py
  - scripts/security_audit.py
  - scripts/tests/test_hlayer_architecture_cli.py
  - scripts/tests/test_security_audit.py
  - docs/research/h-layer/
  - docs/research/hardening/
  - docs/research/thesis-evidence/
  - thesis/
  - VEGO-AI-Thesis-Baseline-Progress.html
- Rollback note: Revert commits 1ff9f72 through eb15a13 in reverse order to remove the empty-envelope and disguised-archive review cycle; ignored PDF, QA, and share folders can be removed separately.
- Git commit: none recorded by script.

## 2026-07-26 13:30 +03:00 - Codex - Execute experiments and publish results-first BigUI

- Files changed:
  - VEGO-AI-Research-Hub.html
  - experiments/accepted-runs/
  - docs/research/bigui/
  - scripts/build_bigui_run_store.py
  - scripts/run_bigui_architecture_experiments.py
  - .github/workflows/supervisor-package.yml
- Rollback note: Revert the BigUI experiment-platform commits on agent/bigui-experiment-platform; Agent 4 and baseline outputs were not changed.
- Git commit: none recorded by script.

## 2026-07-26 14:55 +03:00 - Codex - Add paper-aligned experiment comparison evidence

- Files changed:
  - scripts/run_bigui_comparison_experiments.py
  - docs/research/bigui/paper-baseline-snapshot-v1.json
  - docs/research/bigui/baseline-comparison-results-v1.json
  - VEGO-AI-Research-Hub.html
- Rollback note: Revert the four focused commits from this task; Agent 4 and baseline outputs were not modified.
- Git commit: none recorded by script.

## 2026-07-26 17:14 +03:00 - Codex - Evaluate all experiments and publish benchmark BigUI

- Files changed:
  - schemas/experiment-evaluation-standard-v1.schema.json
  - schemas/experiment-benchmark-snapshot-v1.schema.json
  - schemas/current-run-index-v1.schema.json
  - experiments/current-run-index-v1.json
  - experiments/accepted-runs/
  - docs/research/bigui/
  - VEGO-AI-Research-Hub.html
  - VEGO-AI-Experiment-Benchmark-Report.html
  - scripts/build_experiment_benchmark.py
  - scripts/build_bigui_run_store.py
  - scripts/run_bigui_comparison_experiments.py
  - scripts/build_bigui.py
- Rollback note: Revert the focused BigUI benchmark commits; accepted run bundles are append-only and the frozen Agent 4 baseline remains unchanged.
- Git commit: none recorded by script.

## 2026-07-26 18:36 +03:00 - Codex - Independent expert evidence evaluation pipeline

- Files changed:
  - schemas/independent-evidence-package-v1.schema.json
  - schemas/independent-review-return-v1.schema.json
  - schemas/independent-evidence-delivery-v1.schema.json
  - scripts/build_independent_evidence_package.py
  - scripts/validate_independent_evidence_returns.py
  - scripts/freeze_independent_gold_labels.py
  - scripts/evaluate_independent_ground_truth.py
  - scripts/publish_independent_evidence_package.py
  - scripts/build_bigui.py
  - VEGO-AI-Research-Hub.html
  - docs/research/independent-evidence/README.md
  - docs/research/independent-evidence/MEASUREMENT_CONTRACT.md
  - docs/research/independent-evidence/SUPERVISOR_DECISIONS_REQUIRED.md
- Rollback note: Revert the five independent-evidence commits; no protected runtime or baseline artifact was modified.
- Git commit: none recorded by script.

## 2026-07-26 20:45 +03:00 - Codex - Advance independent evidence study to calibration

- Files changed:
  - docs/research/independent-evidence/decision-register.json
  - docs/research/independent-evidence/PARTICIPANT_INFORMATION_AND_CONSENT.md
  - schemas/independent-calibration-return-v1.schema.json
  - schemas/independent-evidence-decision-register-v1.schema.json
  - scripts/validate_independent_calibration_returns.py
  - scripts/freeze_independent_calibration.py
  - scripts/publish_independent_evidence_package.py
  - VEGO-AI-Research-Hub.html
- Rollback note: Revert the calibration-phase commits; the baseline, Agent 4, private mapping, expert-label count, and evaluation results were not changed.
- Git commit: none recorded by script.

## 2026-07-27 09:39 +03:00 - Codex - Evaluation Phase Implementation Plan & Supervisor Sign-off Checklist

- Files changed:
  - docs/research/evaluation-run-guide.md,docs/research/supervisor-label-approval-checklist.md,docs/research/supervisor-label-approval-pack.md
- Rollback note: Delete docs/research/evaluation-run-guide.md and docs/research/supervisor-label-approval-checklist.md, revert docs/research/supervisor-label-approval-pack.md, and checkout main.
- Git commit: none recorded by script.

## 2026-07-28 14:02 +03:00 - Claude - Evaluation phase: component verdicts, advisory analyst, Iris matrix, full-eval runner

- Files changed:
  - scripts/build_agent_contribution_report.py
  - scripts/tests/test_agent_contribution_report.py
  - scripts/hlayer_llm_analyst.py
  - scripts/run-full-evaluation.ps1
  - docs/research/iris-july1-implementation-matrix.md
  - docs/research/comprehensive-evaluation-plan-2026-07-26.md
  - configs/protected-change-authorization-v1.json
  - docs/research/thesis-evidence/thesis-evidence-snapshot-v1.json
  - docs/research/bigui/experiment-catalog-snapshot-v1.json
  - VEGO-AI-Research-Hub.html
  - docs/agent-memory/current-state.md
  - docs/agent-memory/progress.md
  - docs/agent-memory/issues.md
  - docs/agent-memory/decisions.md
- Rollback note: Revert commits aeddc13, 886c5fb, d59a3df, fa48953 plus the memory-finish commit; the trusted-SHA git config and repo variable stay at 54d2f919 (cacfab7 record).
- Git commit: none recorded by script.

## 2026-07-28 15:46 +03:00 - Claude - Adversarial review fixes, honest-evidence rewrite, and main merge for the evaluation phase

- Files changed:
  - scripts/build_agent_contribution_report.py
  - scripts/tests/test_agent_contribution_report.py
  - scripts/hlayer_llm_analyst.py
  - scripts/run-full-evaluation.ps1
  - docs/research/iris-july1-implementation-matrix.md
- Rollback note: Revert commits d86b8d4 (review fixes) and merge commit 796acfc; earlier evaluation-phase commits listed in the previous entry.
- Git commit: none recorded by script.

## 2026-07-28 19:14 +03:00 - Claude - Enhanced supervisor deck for 29 July, with a fact-check that corrected two published figures

- Files changed:
  - docs/agent-memory/issues.md
- Rollback note: The deck is an external deliverable in Downloads; only docs/agent-memory/issues.md changed in the repo (revert that single file to undo).
- Git commit: none recorded by script.

## 2026-07-30 15:10 +03:00 - Codex - Implement July 29 doctoral requirements-closure program

- Files changed:
  - docs/research/
  - docs/templates/weekly-supervisor-pre-read.md
  - docs/templates/supervisor-decision-change-log.md
  - docs/agent-memory/
  - docs/dashboards/
  - docs/PROGRESS_TRACKER.md
- Rollback note: Revert the implementation commit that follows this entry to remove the July 29 doctoral-control tranche; keep evidence commit 3d0beca if the machine-derived source package must remain preserved. External Drive and Sheet changes require separate owner-controlled archival or deletion and are not reverted by Git.
- Git commit: none recorded by script.

## 2026-07-30 16:21 +03:00 - Codex - Iris requirements assurance and presentation controls

- Files changed:
  - docs/research and docs/templates supervisor-control artifacts
  - experiments/IRIS-EXP-01 through IRIS-EXP-04
  - scripts/validate_iris_requirements_closure.py and focused tests
  - docs/agent-memory and docs/PROGRESS_TRACKER.md
- Rollback note: Revert commit 28ece6e to remove the Iris assurance tranche. Ignored generated diagnostics can be deleted separately; no external sharing or source-data mutation occurred.
- Git commit: none recorded by script.

## 2026-08-01 13:27 +03:00 - Codex - Enhanced Iris Zoom-to-submission closure tranche

- Files changed:
  - docs/research/meetings and docs/research/phd-proposal Iris closure artifacts
  - experiments/IRIS-EXP-05 through IRIS-EXP-10
  - presentations/VEGO-AI-Iris-Supervisor-Decisions-2026-08-05.pptx and local ignored PDF/workbook/backup
  - scripts/build_iris_zoom_disposition_ledger.py and scripts/validate_iris_requirements_closure.py with focused tests
  - docs/agent-memory, docs/dashboards, and docs/PROGRESS_TRACKER.md
- Rollback note: Revert the focused implementation commit to remove tracked closure docs, protocols, validator changes, and PPTX. Delete only the dated ignored local PDF, workbook, backup, and generated QA outputs if those local derivatives must also be withdrawn. Do not alter raw Zoom media, ASR, source Drive, production VEGO-AI behavior, EXP-005 labels, or patient data.
- Git commit: `18c0f2b1cf2170dec6ba7b6a4edfcd2869394051`.

## 2026-08-01 13:47 +03:00 - Codex - Iris closure reachability and receipt hardening

- Files changed:
  - scripts/build_iris_zoom_adjudicated_ledger.py and focused tests
  - docs/research/meetings July 29 human-review workflow and header-only return templates
  - schemas/iris-authorized-submission-receipt-v1.schema.json and pending receipt template
  - IRIS validator, EXP-10 protocol, certificate, governance, provenance, and shared tracking
- Rollback note: Revert the final closure-interface commit to remove the human-review merger, header-only returns, receipt schema/template, and associated validator controls. Do not delete raw media, preliminary ledgers, local presentation artifacts, or any future real human/receipt evidence without separate owner approval.
- Git commit: `18c0f2b1cf2170dec6ba7b6a4edfcd2869394051`.

## 2026-08-01 18:13 +03:00 - Codex - Implement Iris next-step execution controls

- Files changed:
  - docs/research/phd-proposal and docs/research/meetings execution artifacts
  - presentations/VEGO-AI-Iris-Supervisor-Decisions-2026-08-05.pptx
  - scripts/validate_aug1_oct7_execution_program.py and tests
  - scripts/validate_iris_zoom_review_batches.py and tests
  - scripts/validate_iris_requirements_closure.py and tests
  - docs/agent-memory and dashboard status files
- Rollback note: Revert the two final documentation commits; ignored workbook/PDF/previews can be removed locally if no longer required.
- Git commit: none recorded by script.

## 2026-08-03 22:27 +03:00 - Claude - Independent audit + fix pass on the Iris Zoom-closure supervisor package

- Files changed:
  - presentations/VEGO-AI-Iris-Supervisor-Decisions-2026-08-05.pptx
  - presentations/VEGO-AI-Iris-Supervisor-Decisions-2026-08-05.pdf
  - outputs/iris-next-step-2026-08-01-implementation/presentation-qa/v10/*.PNG
  - docs/research/meetings/2026-08-05-supervisor-render-manifest.json
  - docs/research/meetings/2026-08-05-supervisor-source-manifest.json
  - docs/research/meetings/2026-08-05-supervisor-presentation-manifest.md
  - docs/research/meetings/2026-08-05-supervisor-rehearsal-record.md
  - docs/research/meetings/2026-08-05-supervisor-delivery-access-record.md
  - docs/research/meetings/2026-07-29-iris-supervisor-provenance-manifest.md
  - docs/research/phd-proposal/aug1-oct7-execution-control-board.json
  - docs/research/thesis-evidence/THESIS_ACCURACY_EVIDENCE_ADVANCEMENT_PLAN.md
  - docs/agent-memory/current-state.md
- Rollback note: All changes are in the uncommitted working tree of branch docs/iris-july29-phd-execution; git diff/git status shows every touched path; nothing has been committed or pushed.
- Git commit: none recorded by script.

## 2026-08-03 22:XX +03:00 - Claude - Merge Iris closure workstream into main, resolving shared-memory-file conflicts

- Files changed:
  - docs/PROGRESS_TRACKER.md, docs/agent-memory/current-state.md, docs/agent-memory/decisions.md, docs/agent-memory/issues.md, docs/agent-memory/revert-log.md, docs/agent-memory/session-log.md, docs/agent-memory/session-log-archive.md (all conflict-resolved by combining both sides' content, not overwriting either)
- Rollback note: This is a merge commit combining `docs/iris-july29-phd-execution` (209+ commits) into `main` alongside the already-merged evaluation-phase work (PR #15). Revert the merge commit to undo; the source branch remains available at `origin/docs/iris-july29-phd-execution` for cherry-picking if a partial revert is ever needed.
- Git commit: recorded as the merge commit for PR #16.

## 2026-08-04 00:47 +03:00 - Claude - Push Iris workstream to main: merge-conflict resolution and CI hardening

- Files changed:
  - docs/agent-memory/current-state.md
  - docs/agent-memory/issues.md
  - docs/agent-memory/decisions.md
  - docs/agent-memory/revert-log.md
  - docs/agent-memory/session-log.md
  - docs/agent-memory/session-log-archive.md
  - docs/PROGRESS_TRACKER.md
  - scripts/tests/test_iris_zoom_adjudicated_ledger.py
  - scripts/validate_iris_requirements_closure.py
  - scripts/tests/test_iris_requirements_closure.py
  - scripts/tests/test_supervisor_source_manifest.py
  - .gitattributes
  - docs/research/hardening/release-manifest-v3.json
  - docs/agent-memory/revert-log-archive.md
  - docs/research/governance/drive-boundary-verification-2026-08-03.md
  - docs/research/meetings/2026-07-29-iris-supervisor-asr.he.srt
  - docs/research/meetings/2026-07-29-iris-supervisor-provenance-manifest.md
  - pyproject.toml (renormalized only)
  - scripts/tests/bigui_browser_smoke.mjs (renormalized only)
  - scripts/verify-controlled.ps1 (renormalized only)
  - scripts/verify-source.ps1 (renormalized only)
- Rollback note: Merge commit a78c1bf on main; feature branch docs/iris-july29-phd-execution retained (not deleted) at commit 20b04fc for reference.
- Git commit: none recorded by script.

## 2026-08-10 18:59 +03:00 - Claude - Aug-5 call: master plan, Chapter-3 draft, literature map, repairs, full verification

- Files changed:
  - docs/research/meetings/2026-08-05-master-plan.md
  - docs/research/phd-proposal/chapter-3-gap-and-research-questions-draft.md
  - literature/per-rq-literature-map.md
  - docs/research/meetings/2026-08-12-walkthrough-outline.md
  - docs/research/meetings/2026-08-05-tracking.md
  - docs/research/meetings/2026-08-10-work-report.md
  - docs/research/phd-proposal/master-traceability-register.md
  - docs/research/phd-proposal/three-study-contract.md
  - docs/research/meetings/2026-07-29-iris-supervisor-provenance-manifest.md
  - docs/research/meetings/2026-08-05-supervisor-source-manifest.json
  - docs/research/thesis-evidence/thesis-evidence-snapshot-v1.json
  - docs/research/thesis-evidence/THESIS_REVIEW_PACKAGE_MANIFEST.json
  - docs/research/bigui/experiment-catalog-snapshot-v1.json
  - docs/research/hardening/release-manifest-v3.json
- Rollback note: Commits 0595590..2ed820c on main; all repairs additive or manifest rebinds; b605937's content preserved unchanged.
- Git commit: none recorded by script.

## 2026-08-11 00:24 +03:00 - Claude - Full project-wide gaps, blockers, and deferred-work audit

- Files changed:
  - docs/research/meetings/2026-08-11-full-gaps-and-blockers-report.md
  - docs/agent-memory/issues.md
- Rollback note: Two new files added, non-destructive; no code changes.
- Git commit: none recorded by script.

## 2026-08-15 04:43 +03:00 - Codex - August 12 evidence-to-delivery implementation

- Files changed:
  - docs/research/meetings/2026-08-12-*
  - docs/research/meetings/2026-08-19-supervisor-package/**
  - literature/acl2026-human-agent-corpus/**
  - scripts/build_aug12_meeting_evidence.py and focused tests
  - scripts/build_acl2026_corpus.py and focused tests
  - docs/operations/2026-08-vatat-scholarship-status.md
  - docs/agent-memory canonical status files
- Rollback note: Revert only the August 12 review-branch commits if the local implementation must be withdrawn; preserve private append-only evidence packages, raw sources, human-return areas, incident records, and external drafts.
- Git commit: none recorded by script.
