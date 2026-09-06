# Results Dashboard

Last curated update: 2026-09-06 by Claude. Historical validation rows below retain their original dates; they are not claims about the current dirty worktree unless explicitly rerun.

Standing views: tracked `docs/research/h-layer/program-status-snapshot-v1.json`; ignored unified program overview at `reports/generated/hlayer_program_overview/program_overview.md`; one-command verification gate `.\scripts\verify-hlayer-all.ps1`. The final unsuppressed July 21 package rerun on 2026-07-20 recorded 94 + 53 passing tests; the status snapshot records the runtime and durations.

## Validated Implementation Results

| Result | Value | Evidence | Interpretation |
| --- | --- | --- | --- |
| Current VEGO-AI test suite | 94 passed | `python -m pytest VEGO-AI\tests -q` on 2026-07-20 | Current source/test result for the July 21 package; no runtime behavior change was introduced. |
| Current research-tool test suite | 53 passed | `python -m pytest scripts\tests -q` on 2026-07-20 | Current source/tooling result for the July 21 package. |
| Full VEGO-AI test suite | Historical: 93 passed | `python -m pytest VEGO-AI\tests -q` on 2026-06-14 after PR #7 merge | Historical snapshot only; rerun before reporting a current count. |
| Framework/eval/analysis/visualizer compile check | Historical pass | `python -m compileall -q VEGO-AI\framework VEGO-AI\eval VEGO-AI\analysis VEGO-AI\vego_visualizer_delivery` on 2026-06-14 after PR #7 merge | Historical snapshot only, not a current clean-state claim. |
| Dashboard/wiki tracking health | Passed | `.\scripts\build-confluence-wiki.ps1` and `.\scripts\dashboard-health.ps1 -RequireOutbox` on 2026-06-14 | Runtime snapshot, manual sync pack, KPI dashboard, and generated Confluence outbox wiring are verified. |
| Visualizer real-display GUI validation | Passed | PR #7 checklist on 2026-06-14 with screenshots in `%TEMP%\vego_gui_validation_20260614_144509` | Mismatch warning, no-match stale clearing, auto-match, filters/details, read-only research panels, and graceful diagram failure handling are verified. |
| M4A advisory report validation | Passed | M4A review session log and schema validation | `memory_advice.json` conforms to the M4A schema. |
| M4A classification changes | 0 | M4A generated advice review | Advisory layer did not change AI classifications. |
| M4A advice distribution | none 5, strong 2, moderate 1 | M4A generated `ucd_ch` advice review | Memory advice surfaces relevant prior judgments where available. |
| Post-merge behavior boundary | No framework/schema/test changes in `2828940` | `docs/research/m4a-post-merge-confirmation.md` | Research-story update did not change VEGO-AI behavior. |
| M4B-1 implementation baseline | Implemented / evaluation pending | Tag `research-state-m4b1-deterministic-comparison`, `docs/research/evaluation-report.md`, and EXP-001 | M4B-1 is available as deterministic, parallel-only, leakage-labeled comparison; improvement claims still require expert-label evaluation. |
| M4B-1 release artifact | Published | GitHub release assets `vego-ai-M1-M4A-dashboard-M4B1-changes.zip` and `M1-M4A-dashboard-M4B1-manifest.md` | Artifact bundle supports external technical review, not empirical proof. |
| EXP-001 initial evaluation run | Mechanism/readiness only | `.\scripts\build-exp001-evaluation.ps1`; ignored `reports/generated/exp001/` | 27 comparisons, 0 memory-informed classification changes, 2 human-review-after-memory flags, 0 generalization-safe expert labels; no accuracy-improvement claim allowed. |
| EXP-002 expert labeling package | Ready for human labeling | `.\scripts\build-exp002-labeling-package.ps1`; ignored `reports/generated/exp002/` | 27 labeling rows across 4 settings, 24 generalization-safe candidates, 3 existing same-pattern labels, and 27 recommended labeling targets. |
| EXP-006 H-Listen event replay (historical) | 481 captured/reconstructed records + 20 explicit gap records = 501 contract records | `.\scripts\run-hlayer-iteration.ps1`; ignored `reports/generated/exp006/` | `11 queue items / 481 heterogeneous lifecycle records` is a count ratio only; no event-level visibility inference or linkage exists. Early-stage share 0.187; E3 answers are not persisted. |
| EXP-007 dosage-mode replay (historical iteration 6) | `threshold_sev2` load=0.799, bundled=0.891, wcov=0.96 | Ignored `reports/generated/exp007/` | Replay pilot candidate, not a default. Bundling produced a modest absolute reduction (for example 54 to 53); design evidence only. |
| EXP-008 early-trigger mining (2026-07-10, iteration 6) | 167 unstable guidelines; 160 never reviewed; rank-and-cap K=30 -> 0.75 capture | Ignored `reports/generated/exp008/` | Rank-and-cap enforces the load budget by construction but reveals a genuine trade-off: 0.8 capture and <=30 load/setting are not simultaneously achievable with a uniform K - a real design decision for Iris, not a tuning gap. Mechanism/observability evidence only. |
| EXP-009/010 synthetic prototypes (2026-07-10, iteration 7) | Provisional run complete; protocol unapproved | Ignored `reports/generated/exp009/` and `exp010/` | Assumption-driven synthetic rule tests only. They do not validate real expert mistakes or approve the four-source/two-round proposal. |
| EXP-012 validated baseline interface | Interface repaired; canonical EXP-003 cross-check PASS; safe N=0 | Ignored `reports/generated/exp012/` | Generalization-safe status remains `NOT YET COMPUTABLE`. Historical same-pattern pilot is excluded; interface readiness is not evaluation evidence. |
| EXP-013–018 conformance fixtures (2026-07-10) | Six CLIs pass; 24 focused tests; offline validator 19/19 PASS | Ignored `reports/generated/exp013/` through `exp018/` | Fixture-level contract, determinism, workload, authority, provenance, and proposal-safety evidence. No empirical-performance or runtime-authorization claim. |
| H-layer reliability iteration 008 (2026-07-10) | Accepted `NEUTRAL`; run `hlayer-20260710T171143Z-2a66e71a3f` | Ignored `reports/generated/hlayer_iterations/iter_008/` | Atomic temp execution/promotion, manifests, deferred decision snapshot, validated EXP-005 N=0 gate, and repaired EXP-012 cross-check. Reliability evidence only; protected runtime unchanged. |
| H-layer metric/contract iteration 009 (2026-07-10) | Accepted `NEUTRAL`; run `hlayer-20260710T175523Z-ab5175fd07` | Ignored `reports/generated/hlayer_iterations/iter_009/` | 481 captured + 20 explicit gaps = 501 ObservationRecords; `threshold_sev2` event/transaction load 0.799/0.796, weighted/high-severity coverage 0.981/1.0; target coverage>=0.8 at load<=0.5 remains unmet; K30/K35 capture 0.75/0.85. Pareto only; no default. |
| H-layer reliability iteration 010 (2026-07-10) | Accepted `NEUTRAL`; run `hlayer-20260710T183658Z-9199809f30` | Ignored `reports/generated/hlayer_iterations/iter_010/` | Reproducibility snapshot of the unchanged six-experiment replay suite. It is not an interactive-demo result and adds no mechanism-performance evidence. EXP-005 safe N=0; EXP-012 remains not computable. |
| H-layer reliability iterations 011-013 (2026-07-11) | Accepted `NEUTRAL` manifest-backed snapshots | Ignored `reports/generated/hlayer_iterations/iter_011/` through `iter_013/` | Preserve feedback-generalization and decision-snapshot boundaries; no default, empirical claim, or live authorization. Iteration 013 run is `hlayer-20260711T130619Z-f8a39357da`. |
| H-layer reliability iteration 014 (2026-07-20) | Accepted `NEUTRAL`; run `hlayer-20260720T173308Z-d79047f5e2` | Ignored `reports/generated/hlayer_iterations/iter_014/`; tracked status snapshot | Coherence restoration only; normalized `fa3debf25ba705224bfa27748aaee7cd92d72e8f50b6704ccea2ff9f6255651e`. It creates no mechanism-performance evidence and does not create a default. |
| Separate H-layer conformance suite | Offline-only run `HLAYER-CONFORMANCE-8c458da3755870930900` | Normalized `8c458da3755870930900d29f6fff8e8161214eb60dabfaa1edd919b05588a7af` | Six fixture experiments pass; separate from numbered iterations; no runtime authorization. |
| Study 1 AirTravel descriptive provider-backed run (2026-09-05, accepted) | 3 episodes (2 `CONVERGED`, 1 `TERMINATED_MAX_ROUNDS`); denominator 3 complete episodes; 0 `INCOMPLETE_TECHNICAL`; 44 questions and 44 answers; Detector-v1 `STRONG_ALERT` 3, `WEAK_ALERT` 0, `NO_ALERT` 0; actual cost USD 0.134972 | `docs/research/phd-proposal/2026-09-06-study1-airtravel-execution-and-analysis-receipt.md`; run_id `REAL-efe686a-20260905T2303Z`, setting `cd_airtravel`, corpus `text2uml_airtravel_253b26dc`, model `gpt-5.6-luna`, N=4 cases; raw prompts, answers, and corpus bytes are held outside version control | Controlling verdict `PARTIAL_EVIDENCE_ONLY / DESCRIPTIVE_REPORTING_WITH_RETROSPECTIVE_PROVENANCE`: the run receipt does not self-bind the event-log hash, a lifecycle summary, or the execution code SHA. Descriptive counts only. A `STRONG_ALERT` means solely that an episode is a candidate for human review; it is not a finding that an error occurred, that the model was wrong, that output was defective, or that intervention was required. **Alert correctness is untested** - no accuracy, precision, recall, alert-correctness, human-benefit, or generalization claim is supported. Detector-v1 reads conversation-state signals only (`S1`/`S3`/`S7` and `S2`/`S6`); mapping results and the context-only variables C1/C2/C3 never trigger an alert. The corpus is public-external Text2UML material - **not** student data and **not** Cheers or ParkWise. |

## Reproducibility Anchors

| State | Tag / Commit | Purpose |
| --- | --- | --- |
| M3 code state | `milestone-m3-human-judgment-memory` / `5e109e5` | Human Judgment Memory milestone. |
| M4A code state | `milestone-m4a-memory-advisory` / `ecd0972` | Advisory memory layer milestone. |
| M4A research state | `research-state-m4a` / `2828940` | Research story and documentation state after M4A. |
| M4B-1 comparison state | `research-state-m4b1-deterministic-comparison` / `944c922` | Deterministic parallel comparison milestone. |
| Visualizer UX clean state | `research-state-visualizer-ux-clean` / `78b261e` | Model/result matching and read-only research-panel UX cleanup. |

Live branch, revision, and worktree state are intentionally omitted from this table, matching the convention `docs/PROGRESS_TRACKER.md` already applies. Verified with `git` on 2026-09-06: the previously listed `Current workspace` row named branch `agent/publish-hlayer-and-supervisor-package`, which no longer exists, so the row was removed rather than re-pinned to another transient value. Read the current branch and head directly with `git branch --show-current` and `git rev-parse HEAD`, and use `phase-0-boundary-record.md` plus `program-status-snapshot-v1.json` for protected-path fingerprints and current gates. Evidence-bound revisions belong in the row that cites them: the Study 1 AirTravel run above is bound to execution code SHA `efe686ac0b13c6e17695b816da7eb0cdd3eadcc1` (the reporting code SHA is a document-generation stamp and is not part of that evidence chain).

## Research Result Claims

| Claim | Current Support | Status |
| --- | --- | --- |
| VEGO-AI can route selected AI decisions to human review. | M1 implementation and tests. | Supported |
| VEGO-AI can capture structured human feedback. | M2 schema, manager, docs, and tests. | Supported |
| VEGO-AI can store reusable human judgment with provenance. | M3 implementation, schema, docs, and tests. | Supported |
| VEGO-AI can retrieve reusable judgment as advisory evidence without changing AI behavior. | M4A implementation, schema, docs, tests, and review metrics. | Supported |
| Reusable memory improves AI variability interpretation. | Not yet tested; requires M4B-1/C4B evidence with leakage labels. | Not claimed |

## Boundaries

- No controlled model, analysis, evaluation-output, PDF, archive, or executable contents are copied into this dashboard.
- Existing M4A result numbers are metadata-level review results.
- No performance or improvement claim is permitted for Study 1: no independent quality measure exists. For any other programme area, such a claim additionally requires an experiment record and a publishability decision — the linkage is a necessary condition, never a sufficient one.
- Study 1 rows keep three layers separate and must never conflate them: (a) the **mapping result** (Satisfied / Partially-Satisfied / Not-Satisfied), which is the pipeline's judgement about the candidate model and feeds Detector-v1 not at all; (b) the **conversation-state signal** (answer confidence, evidence-field presence, round count), which is Detector-v1's only input; and (c) the **operational action**, which is candidacy for human review and is Detector-v1's only output. A deviation labelled `Alternative` and a `Not-Satisfied` mapping both sit in layer (a): neither is an error and neither triggers an alert.
- No independent quality measure exists in this study, so no row may be read as a statement about quality, benefit, or provider performance.
- Any fixture-versus-real comparison is an engineering and instrumentation check, never a scientific result and never a `VEGO_AI_ON` versus `VEGO_AI_OFF` contrast. The fixture is not a control group, and its denominator (20 answers) must never be merged with the real run's (44 answers).
