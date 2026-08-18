<!--
last_updated: 2026-07-04
staleness_threshold_days: 14
-->

# Decisions

Durable decisions for this project.

## Decision Lifecycle Registry

| Date | Title | Status | Notes / Superseded By |
|---|---|---|---|
| 2026-08-19 | packageRevision Regenerate-Then-Rebind Pattern | Active | `THESIS_REVIEW_PACKAGE_MANIFEST.json`'s `packageRevision` cannot equal the commit currently being authored (the HTML badge and manifest sha256 are fixed at build time, before that commit's hash exists), so `--package-revision` defaulting to `git rev-parse HEAD` only works if HEAD already contains byte-identical tracked outputs. Fix pattern (already present in repo history as e.g. `0ac71b8`, `92850ec`, `ccd80b1`): commit 1 regenerates content and accepts a transient `packageRevision` `--check` failure; commit 2 immediately reruns `build_thesis_review_manifest.py --package-revision <commit-1-hash>` touching only the manifest, then both are pushed together so CI only ever evaluates the final consistent tip. Applied twice on 2026-08-19 (commits 64b6b79+99ff8ad, then 1537b78+4455138) to fix two prior-session CI-red pushes (`aba2450`, `ba65471`, `4ac2ed8`) that had instead tried to pin `sourceRevision`/`packageRevision` to literal current HEAD in a single commit. |
| 2026-08-03 | Independent Audit Standard for the Iris Closure Package | Active | 21-agent adversarial audit found 0 refuted findings; restored all 10 IRIS-EXP structure checks to PASS. |
| 2026-07-30 | July 29 Requirements-Closure Authority | Active working authority | The 19 requirements, 15 actions, and 10 open questions control the successor program, subject to bilingual confirmation and supervisor decisions. |
| 2026-07-30 | One-Plus-Three Research Architecture | Recommended, pending approval | One umbrella RQ and SQ1 selective intervention, SQ2 governed knowledge reuse, and SQ3 evaluation/transfer map to three studies. |
| 2026-07-30 | Plan A / Plan B and August 26 Fallback | Active working default | Plan A is a gated medical extension; Plan B completes through software/modeling and becomes the September default if any critical medical prerequisite is unproved. |
| 2026-07-30 | Three-Zone PhD Data Boundary | Active | Repository metadata/aggregate evidence, private working Drive, and restricted VDI are separated; patient rows and restricted derivatives never enter Git, ordinary Drive, or online LLMs. |
| 2026-06-11 | Shared Agent Memory | Active | Uses AGENTS.md, CLAUDE.md, and docs/agent-memory/ |
| 2026-06-11 | Current-State First Workflow | Active | Stored in current-state.md and progress.md |
| 2026-06-11 | Scripted Prompt Memory | Active | start/finish scripts for memory updates |
| 2026-06-11 | PhD Research Workspace Architecture | Active | Folders for research, thesis, experiments |
| 2026-06-11 | Git And Generated Artifact Policy | Active | Ignores local large data/caches, tracks code/docs |
| 2026-06-11 | Safe GitHub Baseline | Active | Pushed safe baseline to private repo |
| 2026-06-11 | Claude Bootstrap Prompt | Active | Startup instructions at claude-bootstrap-prompt.md |
| 2026-06-11 | Workspace Diagram Format | Active | Markdown + Mermaid diagram in workspace-diagram.md |
| 2026-06-12 | Claude Local Settings Policy | Active | Ignored machine-specific permission files |
| 2026-06-12 | Human-AI Co-Reasoning Milestone 2 | Active | feedback manager and test harness |
| 2026-06-12 | Research OS Infrastructure | Active | Ethics, management, and audit registers |
| 2026-06-12 | Confluence Wiki Target Site | Active | Target space ~71202099edcf0e26ec40cea521806deb9e9687 |
| 2026-06-12 | Reusable Human Judgment Story | Active | Focus on framework, inert memory, controlled M4 |
| 2026-06-12 | Memory Advisory Layer (M4A) Merge | Active | Squashed to main; advisory-only verification |
| 2026-06-13 | Milestone Tags & Handoff | Active | Lightweight tags created, Claude prompts written |
| 2026-06-13 | KPI Register Dashboard | Active | Track dashboards locally and in Confluence outbox |
| 2026-06-13 | Dashboard Health Gate | Active | dashboard-health.ps1 script blocks invalid outbox |
| 2026-06-13 | Runtime Dashboard Snapshot | Active | snapshot.generated.md embedded in Progress page |
| 2026-06-13 | Confluence Manual Sync Pack | Active | Outbox generator fallback for blocked access |
| 2026-06-14 | Conditional M4B-1 Approval Contract | Active | comparison only, Agent 4 frozen |
| 2026-06-14 | Results Dashboard Implementation | Active | offline build_results_dashboard.py merged |
| 2026-06-14 | Visualizer UX and Match Hardening | Active | PR #7 exact matching, auto-clear stale models |
| 2026-06-14 | Evaluation Report and Register | Active | registry.md and evaluation-report.md created |
| 2026-06-14 | EXP-001 Mechanism Readiness | Active | mechanism validation on 27 comparisons |
| 2026-06-14 | EXP-002 Expert Labeling Package | Active | Identified 24 safe candidate rows |
| 2026-06-16 | Supervisor Zoom Preparation | Active | demo prep scripts and slide decks |
| 2026-06-16 | EXP-003 Scaffolding & Accuracy | Active | accuracy evaluation path tooling |
| 2026-06-16 | EXP-004 Policy Sensitivity Tooling | Active | policy sensitivity checks on synthetic labels |
| 2026-06-17 | EXP-005 Real-Label Gate Tooling | Active | blind labeling sheets, κ stats, adjudication |
| 2026-06-21 | VEGO Workbench Launcher | Active | open-vego-workbench.ps1 command-line tool |
| 2026-06-22 | Strategic Review and Hardening | Active | validation consistency checks and strict gates |
| 2026-06-23 | Supervised Codex Next-Step Loop | Active | run-codex-next-step.ps1 for loop execution |
| 2026-06-23 | Project Review Architecture | Active | run-project-review.ps1 updates review-state.md |
| 2026-06-23 | Generated Progress Visualizations | Active | progress visualizations generated for dashboard |
| 2026-06-23 | Progress Update Architecture | Active | defines e2e report, Confluence, and 4-hr updates |
| 2026-06-23 | Progress Update Diagram | Active | diagrams the progress update operational contract |
| 2026-06-23 | E2E Progress Report and Web Page | Active | build-e2e-progress-report.ps1 web output |
| 2026-06-23 | HITL Resource Pack | Active | literature and tooling templates for Chapter 2 |
| 2026-06-24 | Hardened Annotation Pack | Active | 24 safe blind rows split, Dev/Holdout split |
| 2026-07-03 | Tiered Memory & Log Archival | Active | T1/T2/T3 compiled files, session-log pruning |

## 2026-06-11 - Shared Agent Memory

- Decision: Use root-level `AGENTS.md` for Codex instructions and `CLAUDE.md` for Claude instructions.
- Decision: Store shared progress, issues, decisions, and rollback notes in `docs/agent-memory/`.
- Reason: Both agents can read plain Markdown files, which keeps the history portable and easy to review.
- Consequence: Every future prompt that involves meaningful work should update the memory files before the final response.

## 2026-06-11 - Current-State First Workflow

- Decision: Add `docs/agent-memory/current-state.md` and `docs/agent-memory/progress.md`.
- Reason: Future prompts need a quick way to understand project flow without rereading every historical entry.
- Consequence: Agents should use current-state and progress as the first memory resources, then consult detailed logs/issues/decisions as needed.

## 2026-06-11 - Scripted Prompt Memory

- Decision: Add PowerShell scripts for prompt start and prompt finish.
- Reason: The user wants memory files pulled and updated automatically at each prompt.
- Consequence: Agents should run `scripts/agent-memory-start.ps1` at prompt start, then `scripts/agent-memory-finish.ps1` before the final response when meaningful work happened.
- Boundary: Scripts can standardize memory updates, but agents must still use judgment for issues, decisions, and current-state changes.

## 2026-06-11 - PhD Research Workspace Architecture

- Decision: Preserve the extracted source package in `VEGO-AI/` and build the PhD research architecture around it at the repository root.
- Decision: Use dedicated folders for experiments, data zones, literature, papers, thesis, reports, outputs, tests, future cleaned source, and project documentation.
- Reason: The project needs to support scientific traceability, reproducibility, writing, data governance, prompt memory, and software evolution at the same time.
- Consequence: Research notes and thesis/paper materials should stay outside `VEGO-AI/`; source behavior changes inside `VEGO-AI/` should be linked to experiments or decisions.

## 2026-06-11 - Git And Generated Artifact Policy

- Decision: Initialize Git and add `.gitignore` before the first baseline commit.
- Decision: Ignore large archives, generated outputs, raw/interim/processed/external data zones, Python caches, virtual environments, and generated compiled memory.
- Reason: Version control should track source, docs, templates, and lightweight reproducibility records without accidentally committing secrets, bulky generated data, or disposable artifacts.
- Consequence: A baseline commit is still needed before Git gives strong rollback support.

## 2026-06-11 - Safe GitHub Baseline

- Decision: Publish directly to private GitHub repo `AliHamed17/Vego-Ai` on `main` without force-pushing.
- Decision: Preserve remote README-only history with an `ours` merge.
- Decision: Exclude root PDF, zip archives, generated outputs, compiled memory, model files, analysis files, eval outputs, visualizer bundled data, generated review queues, bundled executable, and `get-pip.py` from the safe baseline.
- Reason: The repo should have durable GitHub history while avoiding premature upload of research artifacts that need data/IRB review.
- Consequence: Deferred artifacts remain local and ignored until the data/provenance audit decides what can be shared.

## 2026-06-11 - Claude Bootstrap Prompt

- Decision: Keep a paste-ready Claude startup prompt at `docs/agent-memory/claude-bootstrap-prompt.md` and link it from `CLAUDE.md`.
- Reason: Fresh Claude sessions need a reliable way to load shared memory, respect the PhD architecture, and follow the same Git/data-safety workflow as Codex.
- Consequence: When starting Claude, the user can paste the bootstrap prompt so Claude treats project memory as context and updates it before final responses.

## 2026-06-11 - Workspace Diagram Format

- Decision: Use Markdown plus Mermaid for the first workspace architecture diagram at `docs/architecture/workspace-diagram.md`.
- Reason: GitHub renders Mermaid diagrams directly, so the diagram stays reviewable as text and avoids binary asset management.
- Consequence: Future architecture diagrams can follow the same text-first pattern unless a paper-quality figure export is needed.

## 2026-06-12 - Claude Local Settings Policy

- Decision: Ignore `.claude/*.local.json`.
- Reason: Claude local settings can contain machine-specific permission state and absolute paths that are not portable project configuration.
- Consequence: Portable Claude instructions remain tracked in `CLAUDE.md` and `docs/agent-memory/claude-bootstrap-prompt.md`; local permission state stays untracked.

## 2026-06-12 - Research OS And Confluence Sync

- Decision: Use metadata-only research registers for artifact audit, provenance, and publishability before exposing deferred artifacts.
- Decision: Generate five curated Confluence page bodies after meaningful prompts: wiki home, current state, progress dashboard, update changelog, and research operations.
- Decision: Keep Confluence target IDs in ignored `docs/confluence/wiki-sync-config.local.json`; track only `wiki-sync-config.template.json`.
- Reason: The project needs an external latest wiki without copying controlled research artifacts or local machine state into Git/Confluence.
- Consequence: Until real Confluence IDs are configured, agents generate ignored outbox pages and report live sync as pending.

## 2026-06-12 - Confluence Live Target

- Decision: Use Confluence page `294914` in `https://alih10j.atlassian.net/wiki` as `VEGO-AI Wiki Home`.
- Decision: Use child pages under `294914` for current state, progress dashboard, update changelog, and research operations.
- Decision: Store actual target/page IDs only in ignored `docs/confluence/wiki-sync-config.local.json`.
- Reason: The user provided the Confluence edit URL and requested the wiki stay updated with the latest project state.
- Consequence: Live sync is blocked until Atlassian Rovo access is granted for cloud `724252a1-a5b7-45a5-b6ec-27a8292197ec`; generated outbox remains the pending update meanwhile.

## 2026-06-13 - Dashboard/KPI Tracking

- Decision: Use tracked Markdown files under `docs/dashboards/` as the source of truth for progress, KPI, and results dashboards.
- Decision: Generate a dedicated `VEGO-AI Progress Dashboard` Confluence outbox page from those tracked dashboard sources.
- Decision: Generate an ignored runtime snapshot at `docs/dashboards/status-snapshot.generated.md` and embed it in the Confluence Progress Dashboard.
- Decision: Generate an ignored manual sync pack at `docs/confluence/manual-sync-pack.generated.md` with curated page bodies, target metadata, and hashes for approved fallback publishing.
- Decision: Add dashboard files to research health so progress tracking becomes part of the standard quality gate.
- Decision: Add `scripts/dashboard-health.ps1` to verify dashboard sources, KPI rows, Confluence builder wiring, config page slots, and generated outbox readiness.
- Reason: The user wants progress and research results visible in Confluence without copying controlled artifacts or relying on ad hoc summaries.
- Consequence: Agents should update `docs/dashboards/` whenever progress, KPI values, validated results, or Confluence tracking status changes, then regenerate the runtime snapshot/Confluence outbox/manual sync pack and run `.\scripts\dashboard-health.ps1 -RequireOutbox`.

## 2026-06-12 - Milestone Branch/PR Discipline + Baseline Preservation

- Decision: From Milestone 3 onward, milestone CODE goes on a feature branch (e.g. `feature/human-judgment-memory`) and lands on `main` via a reviewed PR. No direct commits of milestone code to `main` without review (applies to both Codex and Claude). Shared-memory/doc updates may still be committed directly.
- Decision: Preserve the official VEGO-AI baseline (`2eeccb1`) as tag `official-vego-ai-baseline` and branch `baseline/official-vego-ai` on `origin`.
- Decision: Adopt `main` as the canonical development branch (it already carries baseline + M1 + M1.2 + M2 at `217150c`). Do NOT merge `master` into `main` with `--allow-unrelated-histories`. Keep `master` + `feature/human-review-queue` as a granular-history archive; PR #1 closed as superseded.
- Reason: A clean, reviewable audit trail is required for thesis reproducibility; M1/M2 had been published directly to `main`, losing per-milestone review.
- Consequence: Future milestones use feature branches + PRs into `main`, approved before merge.
- Status: M1 (Human Review Queue) + M1.2 (review_signature) + M2 (Human Feedback Manager) complete on `main`. M3 (Human Judgment Memory) was implemented and published as commit `5e109e5`.

## 2026-06-12 - Reusable Human Judgment Research Spine

- Decision: Make reusable human judgment in AI-assisted domain model assessment the explicit research spine for VEGO-AI.
- Decision: Use the main research question: "What approaches have been proposed to support human-AI collaboration in AI-assisted domain modeling and model assessment, and how can they inform the design of reusable human judgment mechanisms in systems such as VEGO-AI?"
- Decision: Use the contribution statement: "selectively triggered, structurally captured, and stored as reusable knowledge."
- Reason: The research review identified this framing as the strongest MSc thesis foundation and the clearest bridge to PhD continuation.
- Consequence: Research docs, thesis outline, evaluation plan, roadmap, and claim/evidence tracking should align to M1 selective review, M2 structured feedback, M3 reusable memory, M4A advisory evidence, and M4B controlled reuse.

## 2026-06-12 - M3 Inert Boundary And M4 Controlled Reuse

- Decision: Treat M3 Human Judgment Memory as implemented but inert.
- Decision: Do not wire memory into Agent 4, embeddings, guideline mutation, or the visualizer until a separate controlled experiment is run.
- Reason: The thesis needs a clean distinction between building reusable knowledge and proving that reused knowledge improves AI-assisted variability interpretation.
- Consequence: M4A is advisory-only; M4B/EXP-001 is the next behavior-changing controlled experiment and behavior-improvement claims wait for C4B evidence.

## 2026-06-12 - M4A Advisory Boundary And M4B Design Gate

- Decision: Treat M4A as an advisory-only bridge from Human Judgment Memory to future model assessment.
- Decision: M4A may retrieve relevant human judgments and generate `memory_advice.json`, but it must not change Agent 4 classifications, prompts, guidelines, visualizer behavior, or baseline evaluation outputs.
- Decision: M4B is design-only until separately reviewed; it must preserve original Agent 4 output and produce a comparison rather than replacing the baseline classification.
- Reason: PR #2 showed the safe bridge needed before any behavior-changing memory-informed reclassification.
- Consequence: Future M4B plans must include `original_agent4_classification`, `memory_advice`, `memory_informed_classification`, `memory_informed_differs_from_original`, `requires_human_review_after_memory`, `evaluation_leakage_status`, `decision_trace`, `policy_version`, and `human_memory_used`.

## 2026-06-13 - M4A Reproducibility Tags

- Decision: Use lightweight Git tags for the M3 code state, M4A code state, and M4A research-state snapshot.
- Decision: Keep `milestone-m3-human-judgment-memory` at `5e109e5f9f2073d9cdc2325bcea2823d57c77882`, `milestone-m4a-memory-advisory` at `ecd097245c463089a5721d68b17d6b22a1005a43`, and `research-state-m4a` at `28289405fc7cb687665f949bf039355a97967c59`.
- Reason: Thesis and artifact review need stable, reproducible anchors for the code milestone and the surrounding research-story state.
- Consequence: Future artifact manifests should reference these tags instead of relying only on moving branch names.

## 2026-06-14 - M4B-1 Conditional Approval Contract

- Decision: Treat M4B-1 as a deterministic, experimental, parallel-comparison layer, not a baseline Agent 4 behavior change.
- Decision: Use `memory_informed_differs_from_original` and always keep `ai_behavior_changed_in_baseline=false`.
- Decision: Require `policy_version="memory-informed-classifier-v1"`, `decision_trace`, `requires_human_review_after_memory`, and `evaluation_leakage_status` on future M4B-1 outputs.
- Decision: Defer M4B-2, Agent 4 `resolve_with_answers`, LLM/API calls, embeddings, visualizer changes, and baseline output overwrites.
- Decision: Future M4B-1 implementation must use branch `feature/memory-informed-comparison` and PR review; Codex must not commit VEGO-AI milestone implementation paths directly to `main`.
- Reason: The M4B review approved the research direction only if reusable memory remains a controlled comparison mechanism with leakage tracking and reproducible deterministic rules.
- Consequence: Claude can implement only the approved M4B-1 scope after confirming `docs/research/m4b-conditional-approval.md`; improvement claims wait for EXP-001/C4B evidence.

## 2026-06-14 - Offline Results Dashboard Boundary

- Decision: Add a local/offline VEGO-AI results dashboard generator under `VEGO-AI/analysis/build_results_dashboard.py`, with generated HTML/JSON output ignored under `VEGO-AI/reports/results_dashboard/`.
- Decision: Track only the generator, tests, docs, schema, and ignore policy; do not track generated dashboard outputs or controlled result artifacts.
- Decision: The dashboard is evidence reporting only: it reads existing JSON/JSONL artifacts, performs no LLM/API/network calls, does not modify baseline outputs, and does not change Agent 4 or M4A classifications.
- Reason: The project needs visual, reviewable research metrics without weakening IRB/data boundaries or confusing reporting with model behavior.
- Consequence: Use PR #5 for review/merge; keep `ai_classification_changed_count=0` as the M4A boundary check and continue treating M4B as a separate controlled experiment.

## 2026-06-14 - Visualizer Pairing And Read-Only Research Panels

- Decision: The visualizer must treat model/result pairing as an explicit case-id contract: Agent C results use `agentC_case_<case_id>.json`, model files use the substring before the first underscore, and auto-load searches only for files beginning with `<case_id>_`.
- Decision: When no exact case-prefix model exists, the visualizer must clear the previous model selection and show `No matching model found`; it must never keep a stale model silently.
- Decision: Manual model changes must be validated against the currently selected result and surfaced as Matched, Mismatch, Unknown, or No matching model found in a persistent top banner.
- Decision: Visualizer research panels are read-only only; they may display M1/M2 review, M3 memory, M4A advice, and M4B-1 comparison sidecars, but must not write feedback, memory, advice, comparison, eval output, model, or analysis artifacts.
- Reason: The review identified stale visualizer pairing as the highest-risk UX issue because it could make a wrong assessment appear normal.
- Consequence: PR #7 carries the UI/helper/test implementation; any future visualizer work must preserve the no-silent-mismatch boundary and avoid changing Agent 4 or evaluator behavior.

## 2026-06-14 - System Validation Artifact And Dashboard Generator Allowlist

- Decision: Track `VEGO-AI/reports/system_validation_report.md` as a research validation artifact.
- Decision: Allowlist only `VEGO-AI/analysis/build_results_dashboard.py` in `scripts/research-health.ps1` because it is an intentionally tracked source generator, not a controlled/generated analysis artifact.
- Decision: Keep all other `VEGO-AI/analysis/` artifacts forbidden unless separately reviewed and explicitly allowlisted.
- Reason: The full-system QA report is useful thesis/research evidence, and the dashboard generator is now part of the reproducibility infrastructure.
- Consequence: `project-health`, `research-health`, and `dashboard-health` pass while controlled analysis spreadsheets/outputs remain excluded.

## 2026-06-14 - Visualizer UX Merge Anchor

- Decision: Treat PR #7 as the validated visualizer UX clean state after real-display GUI validation and squash merge.
- Decision: Use lightweight tag `research-state-visualizer-ux-clean` at commit `78b261e033fc4f3f66170985a884aa5cd0a0cfd2`.
- Reason: The stale model/result mismatch risk affected research interpretation, so the fixed UI state needs a stable reproducibility anchor.
- Consequence: Future visualizer work should preserve exact case-id pairing, stale-model clearing, visible match status, read-only research panels, and unchanged AI behavior.

## 2026-06-14 - Shared Claude/Codex State Report

- Decision: Keep a high-level shared state report at `docs/agent-memory/shared-state-report.md` and include it in generated compiled memory.
- Reason: Claude and Codex need one compact research/governance narrative that explains the milestone chain, contribution, boundaries, and next evaluation direction without relying only on chronological logs.
- Consequence: Future agents should read the report at startup, but still rely on `current-state.md` and Git for exact moving branch/PR status.

## 2026-06-14 - Implementation Freeze And Evaluation Pivot

- Decision: Treat the implemented prototype as complete through M4B-1 for evaluation purposes, anchored by `research-state-m4b1-deterministic-comparison` and the later visualizer UX tag `research-state-visualizer-ux-clean`.
- Decision: The next major deliverable is `docs/research/evaluation-report.md`, not additional feature implementation.
- Reason: The engineering prototype is strong, but empirical evidence is still incomplete; the thesis now needs expert-label comparison, leakage-aware evaluation, and dashboard-backed tables/figures.
- Consequence: M4B-2, Agent 4 memory-based reclassification, LLM resolve modes, embeddings, automatic guideline rewriting, and GUI feedback editing remain blocked until M4B-1 evaluation evidence exists.

## 2026-06-14 - EXP-001 Initial Evaluation Interpretation

- Decision: Treat the first EXP-001 output as mechanism/readiness evidence only.
- Reason: The run has 27 comparison rows and valid leakage tracking, but only 3 expert-labeled rows are available and all are same-pattern Human Judgment Memory cases; there are 0 generalization-safe expert-labeled rows.
- Consequence: The thesis may say M4B-1 preserves baseline output, produces reproducible comparison tables, and flags 2 cases for human review after memory. It must not claim accuracy improvement or generalization until held-out expert labels are added and evaluated.

## 2026-06-14 - EXP-002 Expert Labeling Before More Features

- Decision: Move from mechanism validation to expert-label collection through EXP-002 before implementing more memory behavior.
- Decision: Treat the generated EXP-002 labeling package as the next research artifact: 27 rows, 24 generalization-safe candidates, 3 existing same-pattern labels, and 27 recommended labeling targets.
- Reason: The weak point is empirical evidence, not architecture; M4B-1 cannot support accuracy/generalization claims until independent labels exist.
- Consequence: M4B-2, Agent 4 `resolve_with_answers`, LLM/API reclassification, embeddings, automatic guideline rewriting, and GUI feedback editing remain blocked. The next manual work is expert labeling and rationale collection.

## 2026-06-16 - EXP-003 Accuracy Improvement Gate

- Decision: Treat EXP-003 as the evaluation-first path for any future accuracy-improvement claim or deterministic M4B-1 policy refinement.
- Decision: Generate full and blind expert-labeling sheets, but do not treat original Agent 4 output, copied analysis files, or same-pattern memory as independent ground truth.
- Decision: If there are zero generalization-safe expert labels, the required conclusion is `Accuracy improvement cannot be evaluated yet.`
- Decision: If there are fewer than 20 generalization-safe expert labels, any accuracy or macro-F1 result is pilot evidence only.
- Decision: Do not implement M4B-1.1, M4B-2, Agent 4 changes, LLM/API calls, embeddings, or baseline-output overwrites until EXP-003 provides enough safe labels and a reviewed policy-refinement plan exists.
- Reason: The strict evaluation found no independent benchmark, 0 safe labels, and 0 memory-informed classification differences.
- Consequence: The next research action is expert labeling and error analysis, not classifier behavior change.

## 2026-06-16 - EXP-004 Policy Sensitivity Boundary

- Decision: Add EXP-004 as a policy-sensitivity simulation harness only.
- Decision: Treat EXP-004 synthetic deltas as pipeline/risk screening, not expert evidence and not accuracy improvement.
- Decision: Keep current M4B-1 as the only implemented behavior; candidate variants must not modify Agent 4, M4B-1 production behavior, M4B-2, baseline outputs, `VEGO-AI/eval_output/`, LLM/API behavior, or embeddings.
- Decision: Use EXP-004 after real EXP-003 labels exist to compare candidate policies against non-synthetic evidence.
- Reason: The user wants to keep working toward better accuracy, but the project still lacks independent labels; safe progress requires measurable simulations and gates rather than unreviewed behavior changes.
- Consequence: Accuracy improvement remains unclaimed. Candidate M4B-1.1 policy implementation remains blocked until EXP-003 labels and reviewed error analysis justify a specific rule.

## 2026-06-17 - EXP-005 Real-Label Accuracy Gate

- Decision: Add EXP-005 as the supervisor/expert label-review and real-label policy gate before any deterministic accuracy-improvement change.
- Decision: Use the EXP-005 blind CSV for expert labeling so original Agent 4 and memory-informed classifications are hidden from the reviewer.
- Decision: Use the EXP-005 full CSV as audit context and as the merged downstream input when a filled blind sheet is supplied.
- Decision: Keep the strict gate: `0` safe labels means `Accuracy improvement cannot be evaluated yet`; `1-19` safe labels means pilot evidence only; `20+` safe labels allows quantitative reporting with validity threats, not automatic improvement claims.
- Decision: Keep M4B-1.1, M4B-2, Agent 4 changes, LLM/API calls, embeddings, baseline-output overwrites, and `VEGO-AI/eval_output` changes blocked until EXP-005 evidence and supervisor/reviewer approval justify a specific policy.
- Reason: EXP-004 showed candidate policy risk synthetically, but real accuracy improvement needs independent, leakage-safe expert labels.
- Consequence: The immediate accuracy work is filling and validating EXP-005 labels, not changing classifier behavior.

## 2026-06-21 - Local VEGO Workbench Launcher

- Decision: Use `scripts/open-vego-workbench.ps1` as the main local startup command for result review, EXP-005 labeling, demos, and visualizer opening.
- Decision: Keep the launcher operational only: it may regenerate ignored dashboard/EXP-005/wiki outputs and open local files, but it must not modify Agent 4, M4B-2, `VEGO-AI/eval_output`, baseline outputs, LLM/API behavior, or embeddings.
- Reason: Manual path mistakes were slowing down review and demos; one repo-root command reduces friction without changing research behavior.
- Consequence: Daily review can use `.\scripts\open-vego-workbench.ps1`, GUI review can use `.\scripts\open-vego-workbench.ps1 -Gui`, and non-interactive validation can use `.\scripts\open-vego-workbench.ps1 -All -NoOpen`.

## 2026-06-22 - Strategic Review Evidence Freeze

- Decision: Freeze new feature work and treat EXP-005 real labels as the next required evidence gate.
- Decision: Keep M4B-2, Agent 4 changes, LLM/API reclassification, embeddings, baseline overwrites, and `VEGO-AI/eval_output` changes blocked.
- Decision: Treat EXP-004 synthetic results and same-pattern labels as mechanism/risk-screening evidence only, not real accuracy improvement.
- Decision: Add a second reviewer or supervisor adjudication path before treating EXP-005 labels as strong quantitative evidence.
- Reason: The strategic review found that the architecture is technically strong, while the remaining blocker is empirical validity: 0 supplied EXP-005 labels and 0 generalization-safe valid labels.
- Consequence: The next move is expert-label collection, validation, and strict interpretation, not classifier or policy implementation.

## 2026-06-22 - EXP-005 Evidence Coverage

- Decision: Keep the blind EXP-005 sheet as the first-pass expert-labeling file and add a separate generated adjudication sheet for reviewer-2 or supervisor review.
- Decision: Generate an EXP-005 evidence verdict and reproducibility manifest for every package/rerun.
- Decision: Treat generated EXP-005 verdicts and manifests as ignored local evidence artifacts until publishability is approved.
- Reason: The project needs stronger reliability and reproducibility without changing VEGO-AI classification behavior.
- Consequence: Evidence reruns should review `evidence_verdict.md`, `reproducibility_manifest.json`, reviewer reliability counts, and protected-path diff status before any thesis claim or tag.

## 2026-06-22 - EXP-005 Synthetic Trial Boundary

- Decision: Allow synthetic EXP-005 labels only in a separate ignored trial folder and mark them with reviewer ID `SYNTHETIC_NOT_HUMAN`.
- Decision: Treat the synthetic policy-candidate review as design-only guidance, not real evidence and not authorization for implementation.
- Decision: Keep M4B-1.1, M4B-2, Agent 4 changes, LLM/API calls, embeddings, baseline-output overwrites, and `VEGO-AI/eval_output` changes blocked after the synthetic trial.
- Reason: The synthetic trial confirmed the pipeline works and current M4B-1 has 0.00 pp synthetic accuracy delta, while candidate policy gains depend on synthetic assumptions.
- Consequence: Real EXP-005 labels remain the required next step before any accuracy claim or policy refinement.

## 2026-06-23 - Supervised Next-Step Loop

- Decision: Use `scripts/run-codex-next-step.ps1` as the supervised one-cycle loop for "continue" or "next step" prompts.
- Decision: Keep the loop per-prompt and explicit; do not represent it as a background service or unattended 24/7 automation.
- Decision: The loop may inspect state, open blocked materials, refresh wiki/dashboard outputs, and run EXP-005 downstream only when real labels are saved, complete, valid, and the sheet is closed.
- Decision: The loop must stop on missing labels, invalid/incomplete labels, locked CSV files, or protected VEGO behavior diffs.
- Reason: The user wants Codex to keep making progress with minimal intervention, but the project has hard research and behavior-safety gates.
- Consequence: Future continuation prompts should run the loop first, inspect `reports/generated/next_step_loop/last-run.md`, then perform any safe follow-up work.

## 2026-06-23 - Project Review Architecture

- Decision: Add a structured project review architecture connected to shared agent memory.
- Decision: Keep `docs/agent-memory/review-state.md` as the tracked fast review state and include it in compiled memory.
- Decision: Use `scripts/run-project-review.ps1` to produce ignored review reports under `reports/generated/project_review/`.
- Decision: Use fixed review verdicts: `green`, `yellow`, `blocked`, and `unsafe`.
- Decision: When EXP-005 blocks the next-step loop, run the project review cycle so Codex and Claude get a full audit report instead of only repeating the label blocker.
- Reason: The project now needs repeatable governance/evidence review more than new feature work.
- Consequence: Future review/continue prompts should inspect `reports/generated/project_review/latest-review.md`, keep safe claims separate from blocked claims, and update review-state memory when the review changes project state.

## 2026-07-04 - July 2026 Supervisor Redirect Adopted As A Provisional Working Plan

- Repository planning decision: use `docs/research/extension-plan-2026-07-supervisor-redirect.md` as the active provisional framework-first plan while preserving the parked evaluation gate.
- Proposed design: the human-judgment layer is reframed as an H-layer with skills S1-S7 mapped to H1/H2/H3. Full passive E1-E14 observation, active routing, and agent decomposition remain M-02/M-03 choices, not recorded supervisor decisions.
- Decision: Rename M1/M2/M3 to H1/H2/H3 in NEW research docs and diagrams only; code, schemas, tags, and history keep M-names until a dedicated rename PR is approved.
- Working interpretation pending participant confirmation: M4 is deferred to a separate parked evaluation view; framework and evaluation live in separate diagrams.
- Safety boundary: the expert is a real person; detailed dosage, reviewer roles, source set, round bound, and authority matrix remain M-03..M-05 choices. On timeout, preserve baseline behavior and park the item; no H3 auto-application. S6 is proposal-only.
- Decision: EXP-005 stays the real-label gate of the parked evaluation track; all existing claim boundaries and behavior blocks remain in force; this phase is documentation-only (no VEGO-AI source changes).
- Reason: Machine ASR and machine-derived meeting notes support the redirect, but wording, attribution, and D1-D12 still await participant confirmation.
- Consequence: Offline docs/contracts/experiments may advance. Live implementation stays blocked until M-05 and a separate exact-file authorization are explicitly recorded.

## 2026-07-04 - MediVARIA Drafted As Proposed PhD/Future Work

- Proposal: MediVARIA is a post-meeting planning draft for possible medical-domain transfer; it is not an Iris/Arnon-endorsed clinical project. Study plan: `docs/research/medivaria/medivaria-study-plan.md`.
- Working boundary: the MSc thesis stays education-domain in scope; MediVARIA appears only as motivation, transferability discussion, and proposed future work unless separately approved.
- Governance boundary: no patient data in this repository; ethics/IRB review precedes any future data work; education-domain results are never clinical-performance evidence; partner/negotiation details stay out of tracked docs while TBD.
- Open M-06 choice: whether H-layer detail specs should be domain-parameterized for future transfer. Education remains the MSc empirical scope.
- Reason: User direction on 2026-07-04 to integrate the MediVARIA study and enhance project/thesis per the supervisor's guidance; MediVARIA operationalizes phd-extension-ideas idea 1 and gives ideas 2, 3, and 5 their clinical setting.
- Consequence: 2026-07-15 meeting agenda gains the MediVARIA items (study-plan section 8); TASK-043 tracks MV-P0; all existing evidence gates and the framework-first sequencing remain unchanged.

## 2026-07-10 - Offline Feedback Generalization and Demo Boundary

- Decision: Treat iteration manifests as authoritative: iteration 010 is a `NEUTRAL`, `reliability_only` snapshot of the six-experiment replay suite, not an interactive-demo or quality-improvement result.
- Decision: Implement Vector 1 only as a deterministic, offline proposal generator. It may emit eligibility, grouping, conflict, provenance, and synthesis-request artifacts, but it must not call an LLM, inject Agent B, or mark any rule runtime-eligible.
- Decision: Require S5-verified or explicitly supervisor-adjudicated status, an allowlisted trusted origin, `trusted_memory_eligible = true`, `reusable = true`, a nonblank reuse scope, provenance references, no unresolved override, and a separately validated manifest binding the exact export hash and eligible record IDs before feedback can enter a synthesis group.
- Decision: Keep the supervisor CLI as an isolated offline demo. Ordinary demo feedback and `needs_adjudication` candidates use separate files; every record is unconfirmed and `trusted_memory_eligible = false`; semantic checking remains disabled.
- Decision: Reject generated-output paths under repository `VEGO-AI/` and `.git/` for both the generalizer and demo.
- Reason: M-02 through M-05 remain deferred, current prototype records are informal/unadjudicated, EXP-005 has zero valid safe labels, and automatic prompt/context delivery would cross the protected decision boundary.
- Consequence: The current generalizer result is `BLOCKED_NO_VERIFIED_FEEDBACK` with zero candidate rules. Any LLM synthesis, trusted-memory reuse, Agent B context delivery, or live listener work requires new evidence and explicit authorization.

## 2026-07-28 - One-Command Full Evaluation and Component Verdict Standard

- Decision: `scripts/run-full-evaluation.ps1` is the canonical end-to-end evaluation entry: 16-check verification gate -> experiment benchmark (--refresh) -> per-component contribution report -> program overview/charts -> advisory analyst. Evidence stages gate the exit code; the analyst stage is advisory and never gates.
- Decision: Per-agent/component value questions are answered only by `scripts/build_agent_contribution_report.py` verdicts (CONTRIBUTING / PARTIAL / NOT-YET-MEASURABLE), each backed by named measured signals with N and source paths, plus an explicit "verdict changes if" condition. Narrative layers (LLM analyst) must carry the ADVISORY banner and may never introduce numbers absent from the cited artifacts.
- Decision: When canonical sources legitimately change, re-anchor derived artifacts in this order: commit sources -> `build_thesis_evidence_package.py --source-revision HEAD` + review manifest -> `build_bigui_catalog.py --source-revision <full sha>` -> `build_bigui.py` -> commit. Skipping the catalog/HTML step leaves determinism tests failing (and pytest can stall for minutes computing a difflib diff of the multi-megabyte research hub HTML).
- Reason: The 2026-07-28 evaluation phase surfaced each of these as a real failure mode while wiring the pipeline end to end.
- Consequence: Continuation prompts can run one command for the full program verdict; component claims stay evidence-bound while the EXP-005 gate holds at 0/24 labels.

## 2026-07-30 - July 29 Doctoral Requirements-Closure and Proposal Program

- Decision: Treat the July 29 requirement/action/open-question registers as the successor working authority. The July 1 redirect and July 24 continuation remain preserved as absorbed legacy plans; no older file is silently deleted.
- Decision: Recommend exactly one umbrella research question plus SQ1 selective intervention, SQ2 governed knowledge reuse, and SQ3 evaluation/transfer, mapped one-to-one to intervention architecture, judgment lifecycle, and evaluation/transfer studies.
- Decision: Keep the working wording provisional until Iris and Arnon decide it. The August 5 pre-read is prepared but not recorded as shared or sent.
- Decision: Use Plan A as a staged medical extension and Plan B as a complete software/modeling route. If any critical medical prerequisite remains unproved on August 26, use Plan B in the September proposal and retain Plan A only as a conditional annex.
- Decision: Enforce six sequential pre-row-level medical gates: use-case, people, authorization, ethics/privacy, environment, and protocol. Current readiness is 0/6; integrity, pilot, and export controls are downstream and cannot replace an entry gate.
- Decision: Maintain three data zones: repository for metadata/schemas/proposal/aggregate evidence; private working Drive for collaborative documents; restricted VDI for patient-level data, clinical derivatives, approved local tools, and audit logs.
- Decision: Keep the supplied MIMIC folder unchanged and viewer/source-only. The metadata audit records 25 CSVs and 39.65 GiB versus 26 official tables, with `NOTEEVENTS` and provenance unresolved; no patient rows were inspected.
- Decision: Keep five claim states (`Established`, `Preliminary`, `Planned`, `Blocked`, `Partner-dependent`) and preserve EXP-005 at 0/24 until independent real labels exist.
- Decision: Require Ali review of the exact private Drive, native literature Sheet, proposal, and pre-read before any external sharing. Literature searches and screening are not complete merely because the workbook exists.
- Decision: Treat September and October dates as working targets until written department or Graduate Studies confirmation arrives.

## 2026-07-30 - Iris Requirements Assurance and Presentation Controls

- Decision: Distinguish control coverage from accepted completion. The closure audit has 44/44 locators, while current readiness is 2 verified complete, 6 implemented awaiting human acceptance, 22 partial, 5 open, and 9 blocked.
- Decision: Synchronize the exact recommended umbrella RQ and SQ1-SQ3 wording across the master register, study contract, proposal, decision pack, and execution plan. This fixes internal drift but does not create supervisor approval.
- Decision: Use a separate `IRIS-EXP-01`–`IRIS-EXP-04` assurance register so presentation/process checks do not alter the canonical `EXP-000`–`EXP-040` scientific catalog or empirical evidence.
- Decision: Treat IRIS-EXP-01 traceability and IRIS-EXP-03 claim-boundary results as PASS; treat IRIS-EXP-02 as ready pending a human rehearsal and IRIS-EXP-04 as ready pending the first real weekly cycle.
- Decision: Replace the unsupported “completed four-hour MIMIC audit” statement with the evidenced formulation: bounded metadata/schema audit documented; no patient rows inspected; elapsed time not recorded.
- Decision: Do not reuse July 15/21 decks unchanged. A current August/candidacy presentation requires the 12-checkpoint outline, `[Sources]` notes, rendered QA, a dated rehearsal, and Ali’s exact-package review.
- Reason: Independent call, traceability, and presentation audits found inconsistent question wording, stale presentation material, absent current deck/rehearsal evidence, and an unsupported elapsed-time claim.
- Consequence: The supervisor package can now be checked deterministically without overstating completion. Supervisor decisions, live usability, literature execution, shared access, university rules, EXP-005, and medical gates remain human/external work.

## 2026-08-01 - Enhanced Iris Zoom-to-Submission Closure Controls

- Decision: Preserve the raw media, ASR, translation, and July 29 R/A/Q registers as immutable evidence/snapshots; use the 1,195-row ledger as a machine-only review interface until two independent bilingual reviews and adjudication are recorded.
- Decision: Keep the first 910 control-linked segments distinct from 285 conservative `Human-review-needed` placeholders. A preliminary disposition is not a reviewed translation, speaker attribution, substantive-clause disposition, or acceptance.
- Decision: Separate extraction, implementation, acceptance, and ongoing-control state in the master register. A drafted or built artifact cannot satisfy supervisor acceptance, and silence cannot close a control.
- Decision: Extend assurance through IRIS-EXP-10 and require three fail-closed modes: `structure` may pass on deterministic artifacts; `readiness` also requires current human rehearsal/delivery/access evidence; `closure` additionally requires adjudication, final dispositions, approvals, and submission evidence.
- Decision: Treat SCI-EXP-01–06 as proposal aliases crosswalked to the canonical EXP registry, not as independent result IDs. No new accuracy, generalization, effort, usability, medical, or transfer result is created.
- Decision: The August 5 supervisor presentation is a separate controlled artifact from the later candidacy presentation. The local PPTX/PDF, notes, appendix, workbook, visual QA, and backup establish construction only; human rehearsal, Ali release approval, sharing, access, meeting decisions, and acceptance remain open.
- Decision: Keep reviewer returns and adjudication separate from the byte-reproducible preliminary ledger. The merger may emit an authoritative adjudicated ledger only after both distinct reviewers supply all 1,195 segment rows plus full-media evidence and a third person resolves every disagreement.
- Decision: A submission filename or placeholder cannot satisfy closure. IRIS-EXP-10 requires one exact schema-valid `authorized-submission-receipt.json` whose verified route, zoned time, receipt ID, submitted-package hash, external-receipt hash, authorization evidence, and issued-certificate binding all validate.
- Reason: The enhanced plan requires media-to-control completeness, evidence-honest delivery assurance, and a signed route to submission without allowing automated structure checks to impersonate human or institutional evidence.
- Consequence: The program can report `structure` PASS while `readiness` and `closure` correctly return non-zero. A 100% certificate remains ineligible until every human, external, acceptance, approval, and receipt gate is evidenced.

## 2026-08-01 - Iris Next-Step Execution Interfaces and Release Integrity

- Decision: Operationalize the August 1-October 7 program as a canonical 29-work-package JSON board plus a human-readable ten-sheet workbook; the workbook is a companion view and does not replace the master traceability register or board.
- Decision: Keep Reviewer A/B inputs blind and separate, validate partial batches without treating them as reviewed truth, require one full-media row per reviewer, and require a distinct adjudicator for every disagreement.
- Decision: Treat the university inquiry, proposal v0.2, literature search register, release runbook, role assignments, rehearsals, sharing, access tests, supervisor outcomes, and submission records as prepared interfaces only until the named human or external evidence exists.
- Decision: Correct appendix-title and slide-11 footer defects in native PowerPoint, rerender the changed slides, and bind the final PPTX/PDF hashes before release review.
- Decision: Invalidate the earlier offline ZIP after any package correction. Readiness must parse the current backup status and compare each required ZIP member hash with the current PPTX, PDF, and review workbook; matching a stale ZIP filename or outer hash is insufficient.
- Reason: The user requested implementation of the full next-step plan while preserving an evidence-honest boundary between locally automatable work and human, supervisor, institutional, medical, and submission gates.
- Consequence: Local structure can be complete and testable now, while human rehearsal, delivery, transcript adjudication, decisions, labels, medical authorization, proposal approval, and submission remain visibly blocked.

## 2026-08-03 - Independent Audit Standard for the Iris Closure Package

- Decision: Before reporting any package as "high quality" or "100% correct," an independent audit must reproduce the claim from source — run the actual tests/validators, recompute hashes, and visually inspect rendered artifacts — rather than trust prior session narration. A 21-agent adversarial audit (0 findings refuted) is the standard applied here and should be repeated after any future large edit pass on this package.
- Decision: All 10 IRIS-EXP structure-mode checks must pass at all times going forward; a stale provenance hash, a missing detached manifest, or an uncommitted frozen-package path is treated as a structure-mode regression to fix immediately, not a readiness/closure-only concern.
- Reason: The 2026-08-03 audit found the prior "Structure passes" claim in this file was false against the live repository (9 of 31 provenance hashes stale, 2 test failures, IRIS-EXP-07/08 both FAIL), because a documentation edit pass changed frozen-package files without re-running the provenance/manifest builders afterward.
- Consequence: `bf45c98` (fix pass) + `0456cff` (provenance rebinding) + `e637f0d` (.gitignore) + `ef12f6f` (source-manifest refresh) restore all 10 structure checks to PASS. Readiness and closure remain correctly non-zero pending human evidence.

## 2026-08-04 - Fresh-Worktree Verification Before Trusting Local Checkouts

- Decision: Before pushing a branch and expecting CI to pass, verify CI-equivalent checks (full test suite, structure-mode validator, hardening manifest, diff hygiene) in a disposable `git worktree add --detach HEAD` at the exact commit being pushed, not only in the primary long-lived local checkout.
- Reason: Pushing `docs/iris-july29-phd-execution` triggered CI for the first time this branch had ever run (`supervisor-package.yml` had never executed against it before), and it failed repeatedly for reasons invisible locally: (1) gitignored PDF/workbook artifacts that only ever existed on this machine, crashing validators that assumed local presence; (2) a missing `.gitattributes` `eol=lf` rule for `.jsonl`, so Windows `core.autocrlf` silently corrupted the raw ASR transcript on any fresh checkout while the long-lived local copy (checked out before the rule existed, or written directly by a script) stayed correct; (3) 4 further tracked files (`pyproject.toml`, one `.mjs`, two `.ps1`) whose on-disk bytes in this specific checkout had drifted from the declared attribute policy and were never re-smudged, corrupting an aggregate content hash (the evaluation-phase hardening manifest) that a fresh checkout computed differently. None of these were visible running tests directly in the primary checkout; each was only caught by diffing a fresh worktree's files byte-for-byte against the primary checkout, or by running the actual GitHub Actions job.
- Consequence: 6 CI-blocking commits (`bf980ec` through `20b04fc`) fixed all of the above; CI went green on both the feature branch and the resulting `main` merge commit (`a78c1bf`). Adopt this verification step as standard practice before any push expected to pass CI, especially after a long-lived local checkout has accumulated manual edits, scratch scripts, or older `.gitattributes` history.

## 2026-08-12 - Second Supervisor Checkpoint: Literature-First Sequencing and Structural Correction

- Decision: Treat the August 12 call's closing instruction as binding over its opening one: this week is literature-review-only (Chapter 2); methodology (Chapter 4) work does not start until the following week, and only if literature is done well.
- Decision: Chapter 2 must be structured as a conventional literature-review chapter that builds the reader from the Introduction toward Chapter 3's gap, not as three subsections mirroring SQ1/SQ2/SQ3. The existing per-RQ tag column in the literature spreadsheet (`A08-03`) stays as an internal tracking tool only; it does not dictate the chapter's table of contents.
- Decision: This week's literature scope is deliberately narrow - work the one ACL-2026 Findings paper and its associated GitHub taxonomy corpus thoroughly (classify relevance against the RQs, log gaps), rather than chasing additional separate papers. Broader search is deferred to after the proposal stage. This was an explicit, stated disagreement Iris raised against Arnon's preference to center the review on HCI as a field.
- Decision: `D-RQ-01`/`D-RQ-02` (RQ wording sign-off), `E6`, `E8`, the Plan A/B boundary wording, and the evidence-boundary wording remain explicitly open - the August 12 call did not raise or resolve any of them, and reading the working RQ text aloud without objection is not treated as approval.
- Reason: Direct machine transcript of the 2026-08-12 Zoom call (Ali, Iris, Arnon; ASR in `artifacts/meetings/2026-08-12-iris-arnon/`, evidence matrix in `docs/research/meetings/2026-08-12-supervisor-meeting.md`, items `F1`-`F17`).
- Consequence: `docs/research/phd-proposal/literature-review-structure-and-queries-draft.md` was produced as the first draft satisfying Iris's live request to hand the RQs to an AI assistant for a subsection breakdown and per-subsection Google Scholar queries (`F5`), reconciled against her later structural correction (`F10`). The five frozen `QL-01`-`QL-05` queries in `literature-search-execution-register.md` were found to already answer most of that request and were left untouched; a sixth candidate query (`F9`, live-drafted on the call) is flagged `Needs transcript verification` pending Ali's confirmation before it can become `QL-06` or fold into `QL-01`.

## 2026-08-18 - Chapter 4 (Research Methodology) Drafted With Recommended-Not-Decided Artifacts

- Decision: Write Chapter 4 now, in parallel with a separate literature-review verification track (run outside this session), per Ali's explicit instruction to execute the 2026-08-12 call's non-literature requirements and skip literature-review work.
- Decision: Recommend one concrete artifact per sub-question — an attention-budget cost/coverage model (SQ1), a normative judgment-record contract plus conformance suite (SQ2), and a transfer-eligibility decision procedure plus context descriptor (C2, SQ3) — chosen from the option sets already analyzed in `sections-2-and-4-thinking-notes.md`, each because it is buildable without waiting on EXP-005 (0/24) or medical gates (0/6). Each recommendation is explicitly marked as a recommendation, not a supervisor-confirmed decision.
- Decision: Cite only the chapter's own methodological framework (Peffers et al. 2007 DSRM; Wieringa 2014), both already `VERIFIED_ONLINE` in `literature/verified-research-corpus-2026-08-12.json`, and cite no substantive related-work literature — that stays out of scope for this chapter, consistent with skipping the literature-review track.
- Reason: `sections-2-and-4-thinking-notes.md` Part 3 lists 14 open questions that block a fully-decided Chapter 4, and the 2026-08-12 call did not resolve them (it reaffirmed the three-study structure at a high level only). Writing a chapter with no artifact choice would not be reviewable; writing one that silently picks an artifact without flagging it as provisional would repeat the exact solution-first framing Arnon's `E4` criticism targeted on 2026-08-05.
- Consequence: `docs/research/phd-proposal/chapter-4-research-methodology.md` (new) states the three recommended artifacts and their validation models, and carries forward eight specific open items in its own §4.7 (artifact/abstraction confirmation, the SQ2/SQ3 boundary, instrument-reliability admissibility, offline-replay wording, EXP-009/010 gating, Plan A placement, two unnamed resourcing gaps — an independent implementer for Study 2 and two raters for Study 3). None of it should be read as supervisor-approved.
