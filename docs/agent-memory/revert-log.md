# Revert Log

Record file changes and rollback notes here.

## 2026-09-01 - Claude - Wave 1 engines, plans, and main-red repair (PR #33, merged to main)

- Files added: `src/vego_governed/` (records, lifecycle, policy, reuse + package init), `scripts/run_governed_contract_conformance.py`, 6 test files under `scripts/tests/`, `schemas/experiment-definition-v3.schema.json` + example, `schemas/examples/policy-replay-fixtures.json`, `schemas/examples/conformance-variants/*.invalid.json` (5 planted variants), `experiments/EXP-041..044/`, `docs/research/architecture-enhancement-master-plan-2026-08-31.md`, `docs/research/future-work-and-verification-plan-2026-09-01.md`, `docs/research/phd-proposal/2026-08-31-architecture-decisions-packet.md`.
- Files updated: `experiments/registry.md` (4 new rows; EXP-016/035 relabeled per ISS-045), `scripts/validate_research_records.py` (v3 registration + GJR invariants), `scripts/build_bigui_catalog.py` (post-cohort registry tolerance), `scripts/build_hardening_manifests.py` (README_EVALUATOR re-lock after PR #32 broke main; ISS-049), `docs/architecture/README.md` (plan links), `docs/agent-memory/issues.md` (ISS-049), plus the regenerated derived-artifact set (evidence snapshot/baseline, review manifest, comparison results, benchmark, catalog, hub, progress visual, hardening manifests).
- Rollback note: `git revert` the PR #33 merge commit (`6ec035f`). The engines/tests/cards/plans are additive. Reverting also restores the broken pre-#32-repair lock hash and the cohort-strict registry parser, so after reverting either also revert PR #32's README change or re-apply the re-lock, and remove the EXP-041..044 registry rows or re-apply the parser tolerance - then rerun the §1 health ladder of `docs/research/future-work-and-verification-plan-2026-09-01.md` and regenerate to a clean fixed point.

## 2026-08-31 - Claude - C1-C3 contract artifacts and alignment audit (PR #31, merged to main)

- Files added: `schemas/review-policy-signal-contract-v1.schema.json`, `schemas/governed-judgment-record-v1.schema.json`, `schemas/reuse-decision-record-v1.schema.json`, their three `schemas/examples/*.valid.json` counterparts, and `docs/research/phd-proposal/architecture-alignment-audit-2026-08-31.md`.
- Files updated: `scripts/validate_research_records.py` (registered the three schemas in `SCHEMAS`; added `_review_policy_signal_contract_errors` and `_reuse_decision_record_errors` implementing the cross-field invariants), `docs/agent-memory/issues.md` (ISS-043..ISS-048).
- Regenerated as a source-hash cascade, in dependency order, across several commits: `docs/research/thesis-evidence/thesis-evidence-snapshot-v1.json` and `THESIS_EVIDENCE_BASELINE.md`, `THESIS_REVIEW_PACKAGE_MANIFEST.json`, `docs/research/bigui/{experiment-catalog-snapshot,baseline-comparison-results,experiment-benchmark-snapshot,artifact-manifest,artifact-snapshot}-v1.json`, `EXPERIMENT_BENCHMARK_ANALYTICS_REPORT.md`, `docs/research/hardening/release-manifest-v3.json`, `VEGO-AI-Research-Hub.html`, `VEGO-AI-Experiment-Benchmark-Report.html`, `VEGO-AI-Thesis-Baseline-Progress.html`. The cascade diff was inspected: hash rebinding only, no measured value changed, EXP-005 remains 0 of 24.
- Rollback note: `git revert` the merge commit for PR #31 (`fa86e4d`). The three schemas and their examples are additive and unreferenced by any runtime path, so reverting them is safe; the `validate_research_records.py` revert will re-trigger the same source-hash cascade in reverse, so afterwards regenerate in this order - `build_thesis_evidence_package.py --source-revision <commit>`, `build_thesis_review_manifest.py` then `--package-revision`, `run_bigui_comparison_experiments.py --refresh`, `build_experiment_benchmark.py --refresh`, `build_bigui_catalog.py`, `build_bigui.py`, `build_thesis_progress_visual.py`, `build_hardening_manifests.py`. Nothing under the protected `VEGO-AI/framework/` tree was touched.

## 2026-08-31 - Claude - Architecture tracking-freshness alignment (PR #30, merged to main)

- Files updated: `scripts/build-progress-tracker.py` (stamp text now states H-layer-only scope and points to `current-state.md`), `docs/PROGRESS_TRACKER.md` (regenerated with `--run-tests`), `docs/agent-memory/issues.md` (added ISS-042), `docs/architecture/README.md` (added `thesis-and-progress-architecture.md` to the reading order), `docs/architecture/framework-diagram.md` (added an SQ1/SQ2/SQ3 terminology cross-reference note; no diagram content removed or rewritten).
- Rollback note: `git revert` the merge commit for PR #30 (`679aebc`) restores the prior stamp wording and un-indexed README; also remove the ISS-042 row from `issues.md` if reverting, since it references the wording this revert would undo.

## 2026-08-31 - Claude - Dashboard visualization enhancement (PR #29, merged to main)

- Files updated: `scripts/build-progress-visualizations.ps1` (new `New-StackedBar`/`Get-BucketColorRole` functions replacing `New-HtmlBar`; full CSS rewrite to dataviz-skill tokens with light/dark support; added Milestone/Executive mermaid pies to the Markdown output), `docs/dashboards/progress-visualizations.generated.html` and `.generated.md` (regenerated), `docs/agent-memory/progress.md` (TASK-013 status Done, PR #6 merged), `docs/dashboards/kpi-register.md` (same PR #6 staleness fix), `docs/research/hardening/release-manifest-v3.json` (regenerated to include the above files' new hashes).
- Rollback note: `git revert` the merge commit for PR #29 (`0812aa6`) restores the old flat-bar dashboard and the two stale PR #6 references; regenerate `docs/research/hardening/release-manifest-v3.json` afterward via `uv run python scripts/build_hardening_manifests.py` so it matches the reverted tree.

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

## 2026-08-25 14:10 +03:00 - Claude - Verification pass corrects the strict proposal review

- Files changed:
  - docs/research/phd-proposal/doctoral-proposal-2026-08-23-strict-review.md
- Rollback note: git revert 118570b restores the pre-verification version of the review.
- Git commit: none recorded by script.

## 2026-09-02 09:28 +03:00 - Claude - Proposal Revision 19: committee + supervisor review closure

- Files changed:
  - (outside repo) Downloads\VEGO_AI_Proposal_v19_20260902\*
- Rollback note: No repo code changed; proposal artifacts live outside the repo. Revert = git revert of this log commit.
- Git commit: none recorded by script.

## 2026-09-02 19:10 +03:00 - Claude - Preliminary study one-pager (2026-09-03) and EXP-045 registration

- Files changed:
  - scripts/exp045_escalation_points.py
  - scripts/tests/test_exp045_escalation_points.py
  - experiments/EXP-045-escalation-point-demonstration/README.md
  - experiments/registry.md
  - docs/research/phd-proposal/2026-09-03-preliminary-study-design.en.md
  - docs/research/phd-proposal/2026-09-03-preliminary-study-design.he.md
  - docs/research/phd-proposal/iris-arnon-requirements-2026-09-02-checklist.md
  - docs/research/phd-proposal/README.md
  - docs/research/baseline-characterization.md
  - docs/agent-memory/issues.md
  - pyproject.toml
  - uv.lock
  - requirements-thesis.txt
  - scripts/vego_doctor.py
  - regenerated snapshots under docs/research/bigui, docs/research/hardening, docs/research/thesis-evidence, docs/visualizations
- Rollback note: All changes are additive docs/scripts/registry plus regenerated snapshots; revert = git revert of commits 5860aa0..a72ee0a on main. No protected runtime path changed.
- Git commit: none recorded by script.

## 2026-09-02 20:49 +03:00 - Claude - EXP-046 recorded-review analysis and the data-driven 2026-09-03 one-pager

- Files changed:
  - scripts/exp046_recorded_review.py
  - scripts/tests/test_exp046_recorded_review.py
  - experiments/EXP-046-recorded-review-analysis/README.md
  - experiments/registry.md
  - docs/research/phd-proposal/2026-09-03-preliminary-study-design.en.md
  - docs/research/phd-proposal/2026-09-03-preliminary-study-design.he.md
  - regenerated snapshots under docs/research/bigui, docs/research/hardening, docs/research/thesis-evidence, docs/visualizations
- Rollback note: Additive scripts/docs plus regenerated snapshots; revert = git revert of 193cc13..4953f43. The dataset itself is not in the repository.
- Git commit: none recorded by script.

## 2026-09-03 12:07 +03:00 - Codex - Strict one-page human-intervention experiment for Iris

- Files changed:
  - docs/research/phd-proposal/2026-09-03-preliminary-human-intervention-experiment.en.md
  - docs/research/phd-proposal/README.md
  - scripts/build_paper.py
  - scripts/tests/test_preliminary_human_intervention_one_page.py
  - docs/agent-memory/current-state.md
  - docs/agent-memory/progress.md
  - docs/agent-memory/resource-memory.md
- Rollback note: Revert the one-page source, README, builder geometry, regression test, and associated memory updates from the resulting main commit; the generated PDF is ignored and the prior Downloads PDF is preserved as a timestamped backup.
- Git commit: none recorded by script.

## 2026-09-03 12:55 +03:00 - Codex - Iris preliminary-pilot technical evidence audit

- Files changed:
  - scripts/verify_iris_preliminary_pilot.py
  - scripts/tests/test_verify_iris_preliminary_pilot.py
  - docs/research/phd-proposal/2026-09-03-iris-preliminary-pilot-technical-evidence-map.md
  - docs/research/phd-proposal/2026-09-03-iris-preliminary-pilot-technical-boundary.md
- Rollback note: Revert the audit script, focused test, two technical notes, and corresponding session/revert entries; no VEGO-AI baseline or Agent 4 artifact was modified.
- Git commit: none recorded by script.

## 2026-09-03 22:42 +03:00 - Codex - Implement Q&A escalation observability study scaffold

- Files changed:
  - scripts/extract_qa_escalation_features.py
  - scripts/tests/test_extract_qa_escalation_features.py
  - schemas/qa-escalation-event-v1.schema.json
  - docs/research/phd-proposal/2026-09-03-qa-escalation-observability.md
  - docs/agent-memory/current-state.md
  - docs/agent-memory/progress.md
  - docs/agent-memory/issues.md
  - docs/agent-memory/decisions.md
- Rollback note: Revert the Q&A scaffold, schema, docs, and tracking entries; frozen baseline and prior score-reconstruction artifacts are untouched.
- Git commit: none recorded by script.

## 2026-09-03 23:06 +03:00 - Codex - Supervisor-facing Q&A task plan

- Files changed:
  - docs/research/phd-proposal/2026-09-03-qa-escalation-task-plan.he.md
  - scripts/build_qa_escalation_task_plan.py
  - scripts/build_qa_escalation_task_plan_pdf.py
  - scripts/tests/test_qa_escalation_task_plan.py
- Rollback note: Remove the four new source/build/test files; ignored output/docx and output/pdf artifacts remain local.
- Git commit: none recorded by script.

## 2026-09-03 23:30 +03:00 - Codex - Final revision of supervisor Q&A task plan

- Files changed:
  - docs/research/phd-proposal/2026-09-03-qa-escalation-task-plan.he.md
  - scripts/qa_task_plan_data.py
  - scripts/build_qa_escalation_task_plan.py
  - scripts/build_qa_escalation_task_plan_pdf.py
  - scripts/tests/test_qa_escalation_task_plan.py
- Rollback note: Revert the focused task-plan/data/builder/test changes; generated DOCX/PDF remain ignored local outputs.
- Git commit: none recorded by script.

## 2026-09-04 00:00 +03:00 - Codex - Unify Iris task plan source and harden RTL verification

- Files changed:
  - scripts/data/qa_task_plan.json
  - scripts/qa_task_plan_data.py
  - scripts/build_qa_escalation_task_plan_md.py
  - scripts/build_qa_escalation_task_plan.py
  - scripts/build_qa_escalation_task_plan_pdf.py
  - scripts/qa_task_plan_send_gate.py
  - scripts/tests/test_qa_escalation_task_plan.py
- Rollback note: Revert the canonical JSON/loader/generator/scanner/builder/test changes; generated DOCX/PDF remain local ignored outputs.
- Git commit: none recorded by script.

## 2026-09-04 01:04 +03:00 - Codex - Audit original VEGO-AI interaction-log availability

- Files changed:
  - docs/research/phd-proposal/2026-09-04-interaction-log-recovery-receipt.md
  - scripts/find_original_interaction_log.py
  - scripts/tests/test_find_original_interaction_log.py
  - tracking memory updates
- Rollback note: Revert the receipt, recovery utility, tests, and tracking-memory entries; private generated inventories remain ignored.
- Git commit: none recorded by script.
