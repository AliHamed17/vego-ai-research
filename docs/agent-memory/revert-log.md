# Revert Log

Record file changes and rollback notes here.

## 2026-08-20 - ChatGPT - Direct repair of external Literature Workbook v11 to v12

- External file added: `/mnt/data/VEGO-AI_Literature_Workbook_RQ_Only_Organized_v12_Audit_Fixed.xlsx` plus SHA-256 and local verification report; original v11 workbook preserved unchanged.
- Repository files updated: `docs/research/phd-proposal/chapter-5-preliminary-results.md` (EXP-008 33/26 arithmetic corrected to 1.269/~1.27), `docs/research/phd-proposal/literature-review-v16-workbook-v11-follow-up-v12.md` (workbook-side repair verification), `docs/agent-memory/issues.md` (ISS-036 workbook-side remediated; ISS-038 unchanged/open), `docs/agent-memory/session-log.md`, and this revert log.
- Workbook changes: added G6 to RQ and RQ2 as a construct-risk/open-decision row; re-derived shared FT-A/FT-B labels; replaced the unresolved Raykar anchor with Aroyo & Welty; corrected EXP-008 arithmetic; corrected RES-2/RES-3 citations; relabeled pseudo priority scores as editorial priorities; narrowed ACL disposition and readiness language; preserved four sheets, formulas, current provisional RQs, and separate v15 candidate wording.
- Rollback note: delete the v12 external workbook, checksum, and local verification report to withdraw the spreadsheet output. Revert the repository commits touching Chapter 5, the follow-up report, issues, session log, and this entry to restore the previous tracked documentation. The paired Literature Review v16 PDF was not changed by this task and has a separate repair path.

## 2026-08-19 - Claude - CL7 deck rebuild, literature awesome-list reorg, PR #19/#20 CI fixes, branch backup

- Files added: `literature/README.md` (regenerated), `literature/bibliography.bib`, `scripts/build_awesome_literature_index.py`, `outputs/course-presentation/speaking-script-he.md`.
- Files updated: `scripts/build_course_presentation.py`, `scripts/build_course_presentation_charts.py`, `scripts/check_course_presentation_claims.py`, `scripts/render_deck.ps1` (all: `REPO = Path(__file__).resolve().parent.parent` fix), `outputs/course-presentation/findings.json`, `literature/verified-research-corpus-2026-08-12.json` (dedup 144->140, added Zou et al. 2026), `literature/per-rq-literature-map.md` (superseded notice), `docs/research/literature-review-taxonomy.md` (cross-links), `docs/research/governance/vego-ai-foundation-paper-record.md` (VEGO-AI acronym correction).
- PR #19 (`Realign the seminar deck to CL7 and cap it at 20 slides`): rerun-fixed a stuck `source-security-and-documents` check via `gh run cancel` then `gh run rerun --failed`; now `mergeable: MERGEABLE`, `mergeStateStatus: CLEAN`, all checks pass.
- PR #20 (`Reorganize literature as a generated awesome-list index; add the missing Zou et al. survey`, branch `docs/literature-awesome-index-and-root-cleanup`): resynced with `origin/main` twice in disposable worktrees (`git worktree add`, later removed with `git worktree remove --force`) after main advanced past the branch each time; both times the only conflicts were append-only rows in `docs/agent-memory/decisions.md`/`issues.md`, resolved by keeping the union of both sides' rows; local CI-equivalent checks run and passed after each resync (see session-log for the full command list) before pushing.
- Branch backup: pushed 6 local-only, unmerged branches to origin as plain backup refs (no PR opened): `feature/m4a-test-compat`, `feature/memory-advisor`, `feature/memory-informed-comparison`, `feature/results-dashboard`, `feature/visualizer-ux-refresh`, `fix/m4b-schema-hardening`.
- Rollback note: Deck/literature changes live only on PR branches (`docs/literature-awesome-index-and-root-cleanup`) or already-merged history (via PR #19, once merged) - nothing was pushed directly to `main`. To undo the branch backups, delete the remote refs (`git push origin --delete <branch>`); this does not affect `main` or either PR.

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

## 2026-08-11 - Claude - Aug-12 supervisor package rebuilt to deliverable quality

- Files added:
  - `docs/research/phd-proposal/chapter-3-gap-and-research-questions.md` (A08-02; ~5,200 words, 66 citation markers, supersedes the uncited `-draft` version)
  - `docs/research/phd-proposal/sections-2-and-4-thinking-notes.md` (A08-04; 4 §2 options, 9 §4 artifact options, 14 supervisor questions)
  - `docs/research/phd-proposal/proposal-v0.3-aug12.md` (A08-06 proposal half; raises D-TITLE-01)
  - `docs/research/meetings/2026-08-12-package-readme.md`, `-executive-brief.md` (EN+HE), `-walkthrough-and-qa.md`
  - `scripts/build_aug12_literature_workbook.py`, `build_aug12_tracking_workbook.py`, `build_aug12_think_pass.py`, `build_aug12_presentation.py`, `md_to_docx.py`, `office_to_pdf.ps1`
  - generated: `outputs/aug12/` (16 files: 6 docx + 7 pdf + 2 xlsx + 1 pptx)
- Published: all 16 files to `G:\My Drive\VEGO-AI PhD Working 2026\06_Weekly_Meetings\2026-08-12 Supervisor Package\`
- Key content decisions: Chapter 3 now grounds every positioning claim in a VERIFIED seed corpus (the 29 refs of the group's own MAS4Models submission + 8 resource-pack entries); a 4-lens workflow independently fabrication-checked all 40 sources (zero invented); absence claims scoped to "on title-level evidence"; two wording discrepancies surfaced for A08-01 rather than silently resolved (E6 exploration-vs-identification; E8 human-vs-expert judgment); decomposition sufficiency raised as an open question in §3.8.
- Boundaries held: literature searches remain PROTOCOL READY / NOT RUN and every artifact says so; EXP-005 0/24 and medical gates 0/6 stated in the chapter, the tracker and the deck; no accuracy/generalization/clinical/effort claim (regex scan clean across all new artifacts); §2 and §4 thought about but NOT started per Iris's instruction.
- Rollback note: delete the added docs/scripts and `outputs/aug12/`, and remove the 16 files from the Drive package folder. The prior `chapter-3-...-draft.md` is retained unchanged as the superseded version. No VEGO-AI source file touched.
- Verification: evidence-consistency guard 18/18 PASS; forbidden-claim regex scan clean; all 16 Drive files confirmed present.

## 2026-08-14 - Claude - Transcribed and analyzed the 2026-08-12 Iris/Arnon supervisor call

- Files added:
  - `docs/research/meetings/2026-08-12-supervisor-meeting.md` (evidence matrix `F1`-`F17`, action items `A0812-01`..`10`, "still open" carry-forward section)
  - `docs/research/meetings/2026-08-12-post-meeting-plan.md` (bilingual EN+HE next-week plan)
  - `docs/research/meetings/2026-08-12-supervisor-call-asr.he.metadata.json` (ASR run provenance)
  - `docs/research/phd-proposal/literature-review-structure-and-queries-draft.md` (fulfills `F5`/`A0812-02`/`A0812-03`)
  - (not tracked, gitignored under `artifacts/**`) `artifacts/meetings/2026-08-12-iris-arnon/machine.jsonl`, `machine-transcript.txt` - produced by a concurrent session (worktree `relaxed-raman-7b6fff`) running faster-whisper `large-v3-turbo` (he, cpu, int8); this session watched for completion rather than re-transcribing
- Files edited:
  - `docs/agent-memory/progress.md` (Next Steps section replaced with the August-12-derived list)
- Rollback note: all additions are new documentation files; nothing generated, code, or VEGO-AI source was touched. Deleting the four added files and reverting `progress.md`'s Next Steps section restores the prior state exactly.
- Git commit: none recorded by script; not yet committed.

## 2026-08-18 23:15 +03:00 - Claude - Chapter 4 draft and remaining Aug-12 action items

- Files added:
  - `docs/research/phd-proposal/chapter-4-research-methodology.md`
  - `docs/operations/scholarship-recommendation-request-template.md`
  - `outputs/chapter-4-2026-08-18/Chapter-4-Research-Methodology-draft.docx` (gitignored render, not tracked)
- Files edited:
  - `docs/agent-memory/progress.md` (Next Steps replaced again to reflect Chapter 4 and the remaining A0812 items)
- Rollback note: pure documentation additions; no VEGO-AI source, no experiment output, no baseline changed. Deleting the two new markdown files and reverting `progress.md`'s Next Steps section restores the prior state exactly.
- Git commit: none recorded by script; pending push to main.

## 2026-08-18 23:35 +03:00 - Claude - Rewrote Chapter 4 prose (no analytical content changed)

- Files edited:
  - `docs/research/phd-proposal/chapter-4-research-methodology.md` (style pass only: removed the repeated "Design problem: / Knowledge question: / Recommended artifact: / Validation model: / Dependency and fallback:" label template, cut most em-dash asides and self-referential filler, varied sentence structure per study)
- Rollback note: wording-only change; every citation, artifact recommendation, dependency, fallback, and open-decision item is unchanged from the prior version. Re-ran the forbidden-claims grep and `check_evidence_consistency.py --check` (18/18 PASS) after the rewrite.
- Git commit: pending push to main.

## 2026-08-19 02:12 +03:00 - Claude - Fix CI packageRevision self-reference (thesis review manifest)

- Files changed:
  - docs/research/thesis-evidence/THESIS_REVIEW_PACKAGE_MANIFEST.json
  - docs/research/bigui/baseline-comparison-results-v1.json
  - docs/research/bigui/experiment-catalog-snapshot-v1.json
  - docs/research/bigui/experiment-benchmark-snapshot-v1.json
  - docs/research/hardening/release-manifest-v3.json
  - VEGO-AI-Thesis-Baseline-Progress.html
  - VEGO-AI-Research-Hub.html
  - VEGO-AI-Experiment-Benchmark-Report.html
  - thesis/figures/evidence-ready/*.png
  - thesis/figures/evidence-ready/figure-assets-v1.json
  - thesis/output/VEGO-AI-MSc-Thesis-Evidence-Ready-Draft-2026-07-25.docx
- Rollback note: All 4 commits (64b6b79, 99ff8ad, 1537b78, 4455138) are mechanical regenerate/rebind commits with no narrative or claim changes; safe to revert individually if ever needed, but reverting only one half of a regenerate+rebind pair will reintroduce the packageRevision failure.
- Git commit: none recorded by script.

## 2026-08-19 13:36 +03:00 - Claude - Verify literature review v13 and evidence workbook v5

- Files changed:
  - docs/research/phd-proposal/literature-review-v13-workbook-verification-report.md
- Rollback note: Single new markdown file, no code/build-artifact changes; safe to revert independently if ever needed.
- Git commit: none recorded by script.

## 2026-08-20 02:10 +03:00 - Claude - Do-next-step review: fix forbidden-artifact unsafe verdict

- Files changed:
  - docs/agent-memory/issues.md
  - docs/research/figures/fig1-vego-ai-architecture.pdf (untracked, kept on disk)
  - outputs and presentations PDFs/ZIP (26 more files, untracked, kept on disk)
- Rollback note: git rm --cached is non-destructive, all 27 files remain on disk and in git history; git add -f path would re-track any of them if this decision needs reversing.
- Git commit: none recorded by script.

## 2026-08-24 16:32 +03:00 - Claude - Strict proposal review delivery plus CI security and build-chain fix

- Files changed:
  - docs/research/phd-proposal/doctoral-proposal-2026-08-23-strict-review.md
  - uv.lock
  - docs/research/hardening/release-manifest-v3.json
  - docs/research/hardening/security-posture-snapshot-v1.json
  - docs/research/bigui/experiment-catalog-snapshot-v1.json
  - docs/research/bigui/artifact-snapshot-v1.json
  - docs/research/bigui/baseline-comparison-results-v1.json
  - docs/research/bigui/experiment-benchmark-snapshot-v1.json
  - docs/research/bigui/EXPERIMENT_BENCHMARK_ANALYTICS_REPORT.md
  - docs/research/thesis-evidence/THESIS_REVIEW_PACKAGE_MANIFEST.json
  - experiments/current-run-index-v1.json
  - experiments/accepted-runs/EXP-033-EXP-033-9b351820bea6.json through EXP-040 variants
  - VEGO-AI-Research-Hub.html
  - VEGO-AI-Experiment-Benchmark-Report.html
- Rollback note: git revert e44a308, 41810e0, 2e725f9, 36a36c4 in reverse order if any of these commits need to be undone; each is independently revertable.
- Git commit: none recorded by script.
