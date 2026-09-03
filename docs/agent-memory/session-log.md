# Session Log

Chronological prompt history for Codex and Claude.

## 2026-09-01 - Claude - Wave 1 governed-judgment engines, two plans, and main-red repair (PR #33)

- Request: Ali asked for a huge comprehensive plan to enhance the VEGO-AI architecture/infrastructure following the literature review, implemented end to end; then (mid-work) a second plan for future work emphasizing that the pipeline/data flow must be verifiably unbroken, every step validated, and comparisons must show enhancement rather than mere correctness.
- Actions taken: Wrote `docs/research/architecture-enhancement-master-plan-2026-08-31.md` (8 workstreams, 3 waves, gated by decisions/evidence rather than optimism). Implemented Wave 1 via a 9-agent workflow (5 module builders over disjoint file sets + 1 validator-wiring agent + verify; the final fix/verify agents died on a session limit, so verification and repair were finished by hand): `src/vego_governed/` (lifecycle state machine with named rejection codes and dissent-blocking reuse gate; six §3.3 comparator policy arms as configurations of one engine with budget + selective-risk ledgers; five-gate reuse engine with short-circuit non-exposure and a capability-gap replication guard), `scripts/run_governed_contract_conformance.py` (reconstructability + discrimination over 5 planted `.invalid.json` variants + honest not_run completeness arm), EXP-041..044 cards/rows, ISS-045 relabels, `experiment-definition-v3` (N-arm designs), GovernedJudgmentRecord referential invariants in the validator, and the D1-D4 supervisor decisions packet. Then wrote `docs/research/future-work-and-verification-plan-2026-09-01.md`: the standing 22-rung health ladder, 8 gated research steps (each with entry gate / verification / exit artifact), the 5-point enhancement-vs-correctness comparison discipline, and the whole-plan exit criterion.
- Pipeline repairs: (1) the catalog registry parser required registry == exactly EXP-000..040, so any new experiment row broke two generators and five tests - the identity registry may now grow past the frozen benchmark cohort (extras validated and announced on stderr, never silently dropped). (2) Found `main` RED: PR #32 edited protected `VEGO-AI/eval/README_EVALUATOR.md` without updating `CURRENT_RUNTIME_LOCKS` and was merged with a failing CI run; diff reviewed (docs-only), hash re-locked with an in-code note, logged as ISS-049 with a branch-protection recommendation. Resolved the full hash cascade to a fixed point (regenerate-then-rebind, several iterations); every cascade diff inspected - hash/revision rebinding plus the intended ISS-045 relabels only, EXP-005 stays 0/24.
- Result: PR #33 merged; 282 tests pass (89 new), all 22 CI-equivalent checks green, and the first green `Source, security, browser, and documents` run on the repo since #32 broke it.
- Next steps: D1-D4 need Iris/Arnon (see the decisions packet); ISS-046 (rfc3339-validator) and ISS-044 (protected-tree defects, needs signed authorization) remain open; PR #20 still open/green/unmerged; consider branch protection per ISS-049.

## 2026-08-31 - Claude - Architecture alignment audit and C1-C3 contract artifacts (PR #31)

- Request: Ali supplied `VEGO_AI_Doctoral_Proposal_Revised_20260825 (9).pdf` (28 pages) and asked to continue work on the VEGO-AI architecture, ensure it is aligned with what the literature review requires, and start the enhancements needed on the architecture and experiments.
- Actions taken: Extracted the proposal to text (pymupdf) and ran a 14-agent workflow - five parallel auditors (C1, C2, C3, C4/architecture-docs, experiment portfolio) each pipelined into an adversarial verifier, then three artifact designers and a synthesizer. 94 gaps raised, 88 confirmed, 86 closable without new evidence. Hand-verified every load-bearing claim before publishing.
- Key finding: the construct the proposal's §1.8 designates as the thesis's falsifiable novelty - reviewer selection as a function of claim-specific competence and authority, modelled as distinct - has no implementation surface, and `competence` is absent from `chapter-4-research-methodology.md` §4.4's own field list too, making it the only §3.4 content element that is undesigned as well as unimplemented. What exists (`ROLE_AUTHORITY` in `scripts/hlayer_offline/exp016.py`, `ReviewItem.owner_role`, `gold-label-record-v2.reviewerRole`) is aggregate role over an action class checked after submission - verbatim the form §1.8 names as the literature's insufficient version, so the architecture currently instantiates the prior work the novelty claim is defined against.
- Correction worth recording: an earlier interim report in this session stated the construct had "zero implementation surface" based on greps scoped to `VEGO-AI/framework/`, `schemas/`, `docs/architecture/` and `docs/research/h-layer/`, presented as a whole-repo conclusion. The workflow's adversarial verifier caught that `src/vego_hlayer/` and `scripts/hlayer_offline/` were not searched and do contain reviewer/authority/budget models. Corrected to Ali in-session; the corrected framing is stronger, not weaker.
- Three live defects hand-verified and logged as ISS-044 (all in the protected `VEGO-AI/framework/` tree, so logged rather than fixed): `write_memory()` dedups by `memory_id` keep-first where `memory_id` is setting+pattern only, so an amended judgment is silently dropped; `search_memory()` gates on `conflict_status` but never on `status` and takes no requester parameter; `applies_to_future_models` appears exactly once in the framework, written `False`, never read, with `memory_advisor.py` dropping it from `reuse_scope` - a default-deny scope control nothing consults.
- Delivered: three versioned system-independent contracts (`review-policy-signal-contract-v1`, `governed-judgment-record-v1`, `reuse-decision-record-v1`) with worked examples grounded in the proposal's own Shift Supervisor scenario, registered with the CI record validator; plus implementation of the cross-field invariants the C1/C3 schemas describe in prose but which nothing executed (proven non-vacuous by deliberate mutation). Audit report at `docs/research/phd-proposal/architecture-alignment-audit-2026-08-31.md`. ISS-043 through ISS-048 logged for items needing a supervisor decision or a signed change authorization.
- Flagged not hidden: the C2 schema ships seven lifecycle states, not the six §4.4 fixes, because §4.4's six and §3.4's dissent-blocks-reuse requirement are in genuine tension and `Contested` is under-defined (ISS-048); `format: "date-time"` is inert repo-wide because `rfc3339-validator` is not installed (ISS-046); the C3 context-distance ladder has no rank for a revised description (ISS-047).
- Commands run: `Workflow` (14 agents, ~2.2M subagent tokens), 3 parallel example-builder agents, the full CI script list verbatim (all PASS except `vego_doctor.py`, the known local-only Playwright-browser failure), `pytest scripts/tests` (186 passed; `test_hlayer_hardening.py` passes 26/26 twice on the branch while unmodified `main` fails one, so that flakiness is pre-existing). Resolved a long source-hash cascade in dependency order using the documented regenerate-then-rebind pattern; verified the cascade diff contains no change to any measured value and EXP-005 stays 0/24.
- Next steps: ISS-043 (competence construct) and ISS-048 (six vs seven states) need supervisor decisions, not implementation. ISS-044 needs a signed H-layer change authorization. PR #20 remains open, green, and unmerged.

## 2026-08-31 - Claude - Architecture tracking-freshness alignment (PR #30)

- Request: User asked to "work on the architecture, enhance it" - a terse follow-on to the dashboard-enhancement request, same session, same standing push/PR/merge authorization.
- Actions taken: Read all of `docs/architecture/` (README, project-map, framework-diagram, evaluation-diagram, workspace-diagram, progress-update-diagram, thesis-and-progress-architecture, reproducibility-contract, research-lifecycle, source-package-manifest). Found `docs/PROGRESS_TRACKER.md`'s `AUTO:stamp` reading "As of 2026-07-26" - initially suspected broken automation, but traced it precisely: `scripts/build-progress-tracker.py` runs fine instantly when invoked directly (confirmed via both `uv run python` and bare `python`, in both bash and pwsh - ruling out a PATH/interpreter theory), and the stamp's date is deliberately sourced from `docs/research/h-layer/program-status-snapshot-v1.json`'s own `generatedAt` field, not wall-clock time (by design, for determinism). That snapshot file has no dedicated regenerator script (only consumers) and only one version exists (`v1`), with no decision record saying whether it's an intentionally-frozen snapshot of the paused H-layer track or an accidentally-stalled feed - correctly declined to guess which. Fixed the stamp wording to state its H-layer-only scope explicitly and point to `current-state.md` (itself confirmed fresh, 2026-08-24) for overall project status, logged the open question as ISS-042, added the un-indexed `thesis-and-progress-architecture.md` to the README reading order, and cross-referenced `framework-diagram.md`'s July H1/H2/H3 framing against the current SQ1/SQ2/SQ3 framing in `three-study-contract.md` (an unreconciled-terminology gap this session's earlier literature-review audit had already found from the other direction).
- Result: Opened and merged PR #30 (`docs/architecture-tracking-alignment`) - all checks including `merge-gate` passed on the first CI run.
- Commands run: `uv run python scripts/build-progress-tracker.py --run-tests` / `--check`, `uv run python scripts/check_evidence_consistency.py --check`, `python -c "import ast; ast.parse(...)"`, `gh pr create/checks/view`, `gh api repos/.../pulls/30/merge`, `git worktree add/remove`.
- Next steps: ISS-042 needs an actual decision (freeze-and-document `program-status-snapshot-v1.json` as historical, or specify a `v2` regeneration trigger) - not something an agent should decide unilaterally. PR #20 (literature awesome-list rebuild, flagged since ISS-038) is still open, green, and unmerged as of this entry.

## 2026-08-31 - Claude - Dashboard visualization enhancement (PR #29)

- Request: User asked for a "full enhancement" of the VEGO-AI dashboard, aligned and accurate, with better visualizations, and explicit authorization to push/PR/merge without pausing for confirmation.
- Actions taken: Read `docs/dashboards/README.md`, `scripts/build-progress-visualizations.ps1`, and the existing `progress-visualizations.generated.html` to find the target: a plain single-color bar-row dashboard that only rendered 2 of the 4 status mixes it already computed (KPI, Active Work) while silently dropping Milestone and Executive Snapshot mixes from both the HTML and Markdown outputs. Invoked the `dataviz` skill for the form/color method; replaced the flat bars with proper stacked-bar charts (part-to-whole form per the skill's choosing-a-form guide), using the skill's fixed status palette (good/warning/critical) plus a distinct categorical violet for "Blocked" (keeping this project's existing convention of treating Blocked as visually separate from the Risk/Red severity axis, after an initial mapping attempt put Blocked on the reddest color and Risk/Red on a paler one - caught and fixed by visually reviewing the rendered output), direct labels on wide-enough segments, always-present legends with counts/percentages, and dark-mode support via `prefers-color-scheme` using the skill's validated dark steps. Fixed a real layout bug (`align-items: stretch` on the mix grid was stretching short columns to match the tallest one's legend-wrap height) found by rendering and inspecting the page in-browser (light and dark) per the skill's "render it and look at it" step. Also fixed two stale references to already-merged PR #6 found while reading the data (`docs/agent-memory/progress.md` TASK-013, `docs/dashboards/kpi-register.md`).
- Result: Opened PR #29 from `feature/dashboard-visual-enhancement`. First CI run failed on `build_hardening_manifests.py --check` (STALE) even though the branch was already even with `origin/main` - not the branch-staleness pattern seen earlier with PR #20, just the manifest needing regeneration after the dashboard files changed; ran it locally, verified the 1-line diff, reran the same script list CI uses locally (bigui suite, thesis citations/content/evidence, `visualization_agent.py --check`, `check_repository_privacy.py`, `check_evidence_consistency.py --check`, `visualizations-gallery/build_gallery.py --check`, `check_dependency_lock.py --check`, `vego_doctor.py` [one expected local-only Playwright-browser-not-installed failure, since CI installs Chromium first], `check_quality_ratchet.py`, `security_audit.py --history`) before repushing. All checks including `merge-gate` passed; merged via `gh api .../pulls/29/merge` (plain `gh pr merge` failed because `main` was already checked out in the primary worktree).
- Commands run: `pwsh ./scripts/build-progress-visualizations.ps1` (multiple iterations), `[Parser]::ParseFile` syntax checks, Browser tool screenshots (light + dark), `gh pr create/checks/view`, `gh api repos/.../pulls/29/merge`, `git worktree add/remove`.
- Next steps: None outstanding for this task. The dashboard now shows all 4 status mixes it already computes, in both generated outputs, with real charts instead of flat bars.

## 2026-08-24 16:32 +03:00 - Claude - Strict proposal review delivery plus CI security and build-chain fix

- Request: Strict scored review of 2026-08-23 doctoral proposal PDF as reviewer and orchestrator; also fix broken main CI.
- Actions taken:
  - Delivered strict scored review (75/100) of the 2026-08-23 consolidated doctoral proposal PDF via a 7-dimension Workflow plus manual recovery of two wrongly auto-dropped findings, cross-referenced against v13/v8/v15 verification reports.
  - Sent doctoral-proposal-2026-08-23-strict-review.md to user via SendUserFile.
  - Diagnosed a pre-existing broken main: pip-audit flagged pip 26.1.2 (PYSEC-2026-3721) pinned via pip_api in uv.lock; bumped to 26.2.1 with uv lock --upgrade-package pip --native-tls.
  - Discovered the lock hash bump cascaded through build_hardening_manifests, build_bigui_run_store, build_experiment_benchmark, build_bigui_catalog, build_bigui, build_thesis_evidence_package, build_thesis_progress_visual, build_thesis_review_manifest.
  - Regenerated the full chain iteratively to a verified fixed point: 3 stable passes with identical experiment-catalog-snapshot-v1.json SHA256, 103 accepted bundles, 932 observations, 0 safe labels unchanged.
  - Verified all 18 CI check gates individually with real exit codes plus full 190-test pytest suite before each commit.
  - Confirmed CI green on main (all jobs incl. merge-gate) via gh run view --json jobs, not just the watch notification.
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
- Commands/checks:
  - python scripts/check_evidence_consistency.py --check -> 18/18 PASS
  - uv lock --upgrade-package pip --native-tls -> pip 26.1.2 to 26.2.1
  - uv run python -m pytest scripts/tests -q -> 190 passed 7 subtests passed
  - gh run view 32732249579 --json jobs -> all jobs success incl merge-gate
- Status: Completed
- Next steps: None outstanding for this task; a concurrent session's v16 proposal and workbook v12 work (ISS-036 to 038) is separate and not yet reconciled.

## 2026-08-25 14:10 +03:00 - Claude - Verification pass corrects the strict proposal review

- Request: Attached the same proposal PDF alongside the delivered strict review; verified the review against the actual document.
- Actions taken:
  - Re-verified every falsifiable claim in the 2026-08-23 strict proposal review against the same PDF (sha256 a4c9739..., confirmed 21 pages; the harness reported 24, which is harness metadata not the document).
  - WITHDREW my own reference [45] finding: DBLP canonical form is 'Khaled E. Ahmed', so 'K. E. Ahmed' is correct as written. Earlier sources (arXiv/ORCID/GitHub) render the name without the middle initial, which misled the original check.
  - CORRECTED the 'Chapter 2 duplicates Chapter 4' claim as unsupported (only 14 shared 5-grams, nearly all page boilerplate); the 'move it to Chapter 4' recommendation rested on a false premise and was replaced.
  - STRENGTHENED the solution-world finding: Chapter 2 names the author's own Studies five times and issues design orders in two Research implication lines (p.8 Study 2 must test, p.9 Study 3 must treat).
  - Widened the bibliography check from 13 refs to all 57 via a 12-agent adversarially-adjudicated workflow: 54 exact, 0 unverifiable, 3 real defects, 0 overturned.
  - Newly found [35] GLIF3 cites the wrong journal entirely (JAMIA 11(4) 375-385 -> Journal of Biomedical Informatics 37(3) 147-161); independent proof the cited locus cannot exist since JAMIA 11(4) spans pp. 235-338.
  - New finding B2: Chapter 2 requires a review policy to combine eight named signals; Chapter 4 never enumerates them and three (novelty, evidence quality, reviewer competence) appear nowhere in the methodology chapter.
  - Score adjusted 75 to 73; delivered corrected review to Ali and pushed as 118570b.
- Files changed:
  - docs/research/phd-proposal/doctoral-proposal-2026-08-23-strict-review.md
- Commands/checks:
  - python scripts/check_evidence_consistency.py --check -> 18/18 PASS
  - pypdf page/footer check -> 21 pages, all footers Page N of 21
  - Workflow verify-proposal-bibliography -> 57 refs, 54 exact, 3 defects, 0 overturned
- Status: Completed
- Next steps: Ali to apply the three verified citation fixes ([35] venue, [20] and [27] titles) and leave [45] unchanged.

## 2026-09-02 09:28 +03:00 - Claude - Proposal Revision 19: committee + supervisor review closure

- Request: Work on all the committee review items toward 100/100, then follow the supervisor Hebrew review and the 26 inline comments word by word, verifying everything
- Actions taken:
  - Closed all 10 committee items (1 Sept review) on the doctoral proposal via 6 staged XML edits: 2.6 false sentence replaced and competitors engaged; SQ1 reworded with competence/authority selection; operative falsifiers; C4 interaction hypothesis; Appendix C constants (Tables 8-9); Study 1 fitting admitted; 4.7 design fixed; participant table + second context + 4.2-year elapsed time; 4.5 blind-reconstruction instrument; dates/disclaimers/TOC/renumber; Table 7 reference row reconciled with 82 entries
  - Traced the 31 Aug supervisor review (Hebrew email + 26 Arnon Sturm inline comments) item by item in VEGO_AI_Supervisor_Compliance_Matrix_20260902.md
  - Companion SLR files given a 25 Aug -> Rev 19 numbering map; two stale lines in the Reference Audit corrected
  - Checker changes documented in checker_updates.md (24 sections); assure.py gained the reconciled-row assertion (138)
  - Delivered VEGO_AI_Proposal_Bundle_20260902.zip (61 hashed files) to Downloads\VEGO_AI_Proposal_v19_20260902
  - Honest projection given: ~80/100 on the committee rubric, not 100; remaining points need executed searches, constants pilot, participants, EXP-005 labels
- Files changed:
  - (outside repo) Downloads\VEGO_AI_Proposal_v19_20260902\*
- Commands/checks:
  - python verify.py -> 77 pass / 0 fail (mean 20.2 w/s)
  - python verify_reviewer.py -> 101 pass / 0 fail
  - python assure.py -> 138 pass / 0 fail
  - render.ps1 (Word COM) -> 36-page PDF; DOCX zip ok, 553 paragraphs
- Status: completed
- Next steps: Regenerate figure images 11/14/18/20; complete author lists for refs 74/75/78/79/80/81 against publisher records; execute QL-01..05; run constants pilot; decide ISS-042..049

## 2026-09-02 19:10 +03:00 - Claude - Preliminary study one-pager (2026-09-03) and EXP-045 registration

- Request: Follow the 2026-09-02 supervisor requirements word by word; produce the one-page study design for Iris (baseline/benchmark of WHEN to involve the human in VEGO-AI), a checklist of every requirement, and the repository work behind it
- Actions taken:
  - Grounded the 2026-09-02 supervisor call: Cheers/ParkWise course examples are the VEGO-AI frozen run (179 scored rows / 165 case files, 27 patterns, 4 settings); eval_output and human_review_output are local-only; only Agent 4 has an escalation hook
  - Built and registered EXP-045 (scripts/exp045_escalation_points.py + smoke test + card + registry row): deterministic read-only inventory of per-stage escalation signals and reference disagreement; Stage 2 misses 59/80 reference guidelines (evaluator FN authoritative), 12 unanswered Agent 2 questions, 150/165 case files with an Alternative fragment, 11/27 patterns queued
  - Wrote the Thursday 2026-09-03 one-page study design (EN + HE) via a 3-angle draft panel, judges, synthesis and adversarial verification (4 blocking defects fixed: false advisor-questions count, untraceable bracket citations, non-computable m2, infeasible blindness on P6); rendered to one A4 page with Word
  - Produced the 115-item word-by-word call checklist and compliance matrix (66 covered on the page, 8 partly, 11 deferred, 30 context); all 192 quotations verified verbatim against the page
  - Repo hygiene: fixed red main (stale visualization catalog after untracking generated dashboards; pypdf CVE-2026-84309/84310/84311 bump to 6.16.1 + vego_doctor pin), ran the hash cascade to fixed points, ISS-050..052 logged, baseline-characterization trigger description corrected
  - Delivered to Downloads\VEGO_AI_Preliminary_Study_2026-09-03 (PDF/DOCX/MD EN+HE, checklist, matrix, inventory table)
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
- Commands/checks:
  - python scripts/exp045_escalation_points.py --vego-root C:/Users/ahamed/vego-ai/VEGO-AI -> summary.md (per-stage table)
  - pytest scripts/tests/test_exp045_escalation_points.py -> 5 passed (VEGO_AI_ROOT set)
  - CI check list (22 scripts) -> all pass at 68f8bbf; pytest VEGO-AI/tests 113 passed; tests/hlayer_offline 46 passed; scripts/tests 256 passed + 26 long-path fixture errors (environment-only, pass in the main checkout and CI)
  - GitHub CI: green at a671543 and 68f8bbf; a72ee0a pending
  - Word COM render: EN and HE pages = 1 page each
- Status: completed
- Next steps: Thu 09-03 13:00: send the one-pager to Iris and Arnon; Fri 09-04: freeze the per-row CSV and send the marking sheet (7 ucd_ch patterns), request the Cheers domain-base files / TA index from Iris; Sat 09-05: marks, m2-m5, injected P6 intervention; Sun 09-06: two-page results; Wed 09-09: proposal v2 with Study 1 preliminary results; regenerate proposal figure images 11/14/18/20; complete reference entries 74-81

## 2026-09-02 20:49 +03:00 - Claude - EXP-046 recorded-review analysis and the data-driven 2026-09-03 one-pager

- Request: Use the delivered VEGO-AI dataset and its baselines to rebuild the preliminary-study page around where the human should be involved
- Actions taken:
  - Ingested the delivered VEGO-AI dataset zip (System/, Dataset_Cheers/, Visualizer/; 27.8 MB): its evaluator outputs are byte-identical to the frozen run already tracked, so the EXP-045 signal inventory and this analysis describe the same run
  - Found human judgment already recorded in the project analysis workbooks and registered it as EXP-046 (scripts/exp046_recorded_review.py + smoke test + card + registry row)
  - Stage 2: 186 agent guidelines reviewed, 68 not accepted in full (46 partly, 21 wrong, 1 unsure); 59 course requirements unmatched (the Cheers domain bases, previously absent locally, ship with the dataset)
  - Stage 3: 915 compliance judgments reviewed with 120 overturned, 104 alternative-or-mistake judgments with 27 overturned (147 of 1,019 pooled); overturn rate by the agents own verdict Satisfied 1.8% / Partially-Satisfied 46.3% / Not-Satisfied 34.7%, so escalating everything not called Satisfied flags 257 of 915 items (28%) and covers 108 of 120 overturns (90%)
  - Model level: agent score against course grade over 164 rows, r = 0.25 overall and 0.02 for ucd_pw, recomputed independently and matching the workbook pivot
  - Rebuilt the 2026-09-03 one-pager (EN + HE) on these numbers: the baseline is now empirical, every figure cross-checked against the EXP-046 output before commit
  - Source workbooks deliberately kept out of the repository (student submission ids); check_repository_privacy passes and the smoke test skips where the dataset is absent
- Files changed:
  - scripts/exp046_recorded_review.py
  - scripts/tests/test_exp046_recorded_review.py
  - experiments/EXP-046-recorded-review-analysis/README.md
  - experiments/registry.md
  - docs/research/phd-proposal/2026-09-03-preliminary-study-design.en.md
  - docs/research/phd-proposal/2026-09-03-preliminary-study-design.he.md
  - regenerated snapshots under docs/research/bigui, docs/research/hardening, docs/research/thesis-evidence, docs/visualizations
- Commands/checks:
  - python scripts/exp046_recorded_review.py --dataset-root <dataset> --json summary.json -> all page figures
  - pytest scripts/tests/test_exp046_recorded_review.py -> 6 passed with the dataset, 6 skipped without
  - Regeneration chain to a fixed point after the registry row; all 22 CI checks pass locally
  - Word render: EN and HE pages are one page each
- Status: completed
- Next steps: Thu 09-03: send the page; ask whether the recorded review may be cited as preliminary evidence and who performed it. Fri 09-04: apply the signals to the whole corpus (not only the reviewed sample) and produce the capture/load curve. Sat 09-05: worked P6 case and earliest-stage counts. Sun 09-06: two-page results. Wed 09-09: proposal v2 with Study 1 preliminary results.

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
