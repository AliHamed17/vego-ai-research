# VEGO-AI Experiment Benchmark Analytics Report

Generated: `2026-07-26T16:00:00+03:00`
Input projection: `d262313d554d348a98348a2bce2c3ff9eb3b5114d876eb3f6df6a330c3d04fa0`

## Technical summary

The benchmark evaluated all 41 registered experiments. 26 have accepted source-backed runs; the remainder are protocols, gated studies, or parked history. Engineering progress is measured separately from empirical classification validity.

**Empirical boundary:** independent generalization-safe N=0. Accuracy, macro-F1, net correction, paired significance, generalization, and human-effort improvement remain not computable.

## Key findings

- 26 of 41 experiments have accepted source-backed runs; the remaining records are explicit protocols, gated studies, or parked history.
- 26 experiments expose measured engineering signals, while zero experiments contain eligible independent classification-performance evidence.
- Architecture progress is demonstrated through capability extension, semantic parity, deterministic replay, fail-closed safety, provenance, and reproducible run records.
- The pinned EXP-036 summary reports engineeringTargetMet=false: the unified P95 latency-ratio check fails at larger scale even though parity P95 and unified peak-memory both pass; the ratio varies run to run on the same machine, so a single favorable observation is not treated as a pass.
- The paper and current repository are directly comparable for architecture and versioned counts only; the paper's qualitative Phase D is not independent ground truth.

## Measured result highlights

These are selected latest-run observations. Every value retains its denominator, source, observation date, evidence class, and claim boundary; accepted-run history is analyzed separately.

### EXP-001 — M4B-1 memory-informed parallel comparison experiment

The conservative human-judgment mechanism produced a complete 27-row parallel comparison while preserving every baseline classification.

- `MECH_COMPARISON_ROWS` = 27 comparison rows (N=27; aggregate)  Source: `reports/generated/exp001/exp001_summary.json` (`06419d6e3a5a…`, 2026-06-16).
- `MECH_REVIEW_AFTER_MEMORY` = 2 review escalations (N=27; aggregate)  Source: `reports/generated/exp001/exp001_summary.json` (`06419d6e3a5a…`, 2026-06-16).
- `SAFETY_CLASSIFICATION_CHANGES` = 0 classification changes (N=27; aggregate)  Source: `reports/generated/exp001/exp001_summary.json` (`06419d6e3a5a…`, 2026-06-16).

Evidence class: `mechanism`. Claim boundary: Mechanism readiness and baseline protection only; no accuracy or generalization claim.

### EXP-006 — H-Listen event replay

The reconstructed lifecycle corpus makes the observation volume and the much smaller review queue explicit.

- `EVENT_TOTAL_RECONSTRUCTED` = 481 events (N=481; aggregate)  Source: `reports/generated/exp006/summary.json` (`7d8abc081553…`, 2026-07-26).
- `MECH_REVIEW_QUEUE_ITEMS` = 11 queue items (N=481; aggregate)  Source: `reports/generated/exp006/summary.json` (`7d8abc081553…`, 2026-07-26).
- `MECH_QUEUE_TO_EVENT_COUNT_RATIO` = 0.023 count ratio (N=481; aggregate)  Source: `reports/generated/exp006/summary.json` (`7d8abc081553…`, 2026-07-26).

Evidence class: `offline`. Claim boundary: Offline architecture or workload evidence only; no production approval or accuracy claim.

### EXP-007 — S2 dosage-mode replay

The severity-2 candidate preserves high-severity coverage but retains most of the replay workload, so it is not an approved default.

- `ROUTING_HIGH_SEVERITY_COVERAGE` = 1.000 proportion (N=289; mode=threshold_sev2, setting=ALL)  Source: `reports/generated/exp007/summary.json` (`1d1e4922f274…`, 2026-07-26).
- `ROUTING_WEIGHTED_COVERAGE` = 0.981 proportion (N=289; mode=threshold_sev2, setting=ALL)  Source: `reports/generated/exp007/summary.json` (`1d1e4922f274…`, 2026-07-26).
- `ROUTING_EVENT_LOAD` = 0.799 proportion (N=289; mode=threshold_sev2, setting=ALL)  Source: `reports/generated/exp007/summary.json` (`1d1e4922f274…`, 2026-07-26).
- `ROUTING_BUNDLING_REDUCTION` = 0.004 proportion (N=289; mode=threshold_sev2, setting=ALL)  Source: `reports/generated/exp007/summary.json` (`1d1e4922f274…`, 2026-07-26).

Evidence class: `offline`. Claim boundary: Offline architecture or workload evidence only; no production approval or accuracy claim.

### EXP-009 — H-Verify seeded-conflict dry run

The deterministic H-Verify rules separate conflicts and non-conflicts on a finite synthetic fixture; this is rule coverage, not human-error validation.

- `HVERIFY_DETECTION_RECALL` = 1.000 proportion (N=10; aggregate)  Source: `reports/generated/exp009/summary.json` (`5bea318ee21d…`, 2026-07-26).
- `HVERIFY_SPECIFICITY` = 1.000 proportion (N=10; aggregate)  Source: `reports/generated/exp009/summary.json` (`5bea318ee21d…`, 2026-07-26).
- `HVERIFY_FALSE_POSITIVES` = 0 count (N=10; aggregate)  Source: `reports/generated/exp009/summary.json` (`5bea318ee21d…`, 2026-07-26).
- `HVERIFY_FALSE_NEGATIVES` = 0 count (N=10; aggregate)  Source: `reports/generated/exp009/summary.json` (`5bea318ee21d…`, 2026-07-26).

Evidence class: `synthetic`. Claim boundary: Synthetic fixture behavior only; never human or empirical validation.

### EXP-013 — Event-contract fidelity

All fixture records satisfy the event contract, reconstructable records retain lineage, and evaluation-only E15 remains parked.

- `CONTRACT_SCHEMA_VALID_RATE` = 1.000 proportion (N=5; aggregate)  Source: `reports/generated/exp013/summary.json` (`abd2c4789581…`, 2026-07-26).
- `CONTRACT_LINEAGE_COMPLETE_RATE` = 1.000 proportion (N=3; aggregate)  Source: `reports/generated/exp013/summary.json` (`abd2c4789581…`, 2026-07-26).
- `CONTRACT_E15_PARKED` = 1 count (N=1; aggregate)  Source: `reports/generated/exp013/summary.json` (`abd2c4789581…`, 2026-07-26).

Evidence class: `offline`. Claim boundary: Offline architecture or workload evidence only; no production approval or accuracy claim.

### EXP-016 — Role-based action authorization (not claim-specific authority - see ISS-045) and timeout safety

All authority and timeout fixtures preserve the baseline and create no correction application or trusted-memory write.

- `AUTHORITY_SAFE_CASE_RATE` = 1.000 proportion (N=5; aggregate)  Source: `reports/generated/exp016/summary.json` (`2e9b44d98fbe…`, 2026-07-26).
- `AUTHORITY_TRUSTED_MEMORY_WRITES` = 0 count (N=5; aggregate)  Source: `reports/generated/exp016/summary.json` (`2e9b44d98fbe…`, 2026-07-26).
- `AUTHORITY_CORRECTION_APPLICATIONS` = 0 count (N=5; aggregate)  Source: `reports/generated/exp016/summary.json` (`2e9b44d98fbe…`, 2026-07-26).

Evidence class: `synthetic`. Claim boundary: Offline architecture or workload evidence only; no production approval or accuracy claim.

### EXP-033 — Full-corpus runtime parity

Legacy, unified, and parity paths are semantically equivalent on the controlled fixture, replay deterministically, and preserve classifications.

- `ARCH_SEMANTIC_PARITY_RATE` = 1.000 proportion (N=15; aggregate)  Source: `reports/generated/bigui_architecture/summary.json` (`9b351820bea6…`, 2026-07-26).
- `ARCH_REPLAY_DETERMINISM` = 1 proportion (N=1; aggregate)  Source: `reports/generated/bigui_architecture/summary.json` (`9b351820bea6…`, 2026-07-26).
- `ARCH_CLASSIFICATION_CHANGES` = 0 count (N=15; aggregate)  Source: `reports/generated/bigui_architecture/summary.json` (`9b351820bea6…`, 2026-07-26).

Evidence class: `offline`. Claim boundary: Mechanism-equivalence evidence only; zero semantic differences does not establish accuracy.

### EXP-034 — H-layer topology trade-off

The three H-layer topologies produce contract-equivalent traces while exposing different coordination and failure-containment trade-offs.

- `TOPOLOGY_HANDOFF_COUNT` = 30 handoffs (N=15; topology=topology-a)  Source: `reports/generated/bigui_architecture/summary.json` (`9b351820bea6…`, 2026-07-26).
- `TOPOLOGY_HANDOFF_COUNT` = 15 handoffs (N=15; topology=topology-b)  Source: `reports/generated/bigui_architecture/summary.json` (`9b351820bea6…`, 2026-07-26).
- `TOPOLOGY_HANDOFF_COUNT` = 0 handoffs (N=15; topology=topology-c)  Source: `reports/generated/bigui_architecture/summary.json` (`9b351820bea6…`, 2026-07-26).
- `TOPOLOGY_FAILURE_BREADTH` = 3 skills (N=15; topology=topology-a)  Source: `reports/generated/bigui_architecture/summary.json` (`9b351820bea6…`, 2026-07-26).
- `TOPOLOGY_FAILURE_BREADTH` = 4 skills (N=15; topology=topology-b)  Source: `reports/generated/bigui_architecture/summary.json` (`9b351820bea6…`, 2026-07-26).
- `TOPOLOGY_FAILURE_BREADTH` = 7 skills (N=15; topology=topology-c)  Source: `reports/generated/bigui_architecture/summary.json` (`9b351820bea6…`, 2026-07-26).

Evidence class: `offline`. Claim boundary: The result is a Pareto comparison and cannot approve a production topology.

### EXP-035 — Fault injection and authority safety

Every malformed, duplicate, missing, late, conflicting, and timed-out fixture resolves through a safe disposition without baseline mutation.

- `SAFETY_FAULT_CASE_PASS_RATE` = 1.000 proportion (N=20; aggregate)  Source: `reports/generated/bigui_architecture/summary.json` (`9b351820bea6…`, 2026-07-26).
- `SAFETY_BASELINE_PRESERVATION` = 1.000 proportion (N=20; aggregate)  Source: `reports/generated/bigui_architecture/summary.json` (`9b351820bea6…`, 2026-07-26).
- `SAFETY_TRUSTED_MEMORY_WRITES` = 0 writes (N=20; aggregate)  Source: `reports/generated/bigui_architecture/summary.json` (`9b351820bea6…`, 2026-07-26).
- `SAFETY_CORRECTION_APPLICATIONS` = 0 applications (N=20; aggregate)  Source: `reports/generated/bigui_architecture/summary.json` (`9b351820bea6…`, 2026-07-26).

Evidence class: `synthetic`. Claim boundary: Fixture safety evidence only; it is not a guarantee against every future fault.

### EXP-036 — Scale, latency, and reproducibility

The pinned summary records engineeringTargetMet=false for the latest controlled scale run: the unified P95 check fails at larger scale while the parity P95 and unified peak-memory checks pass; run-to-run p95-ratio variability remains visible separately.

- `ARCH_P95_RATIO_TO_LEGACY` = 1.079 ratio (N=100; fixture=SYNTHETIC_1X, mode=unified)  Source: `reports/generated/bigui_architecture/summary.json` (`9b351820bea6…`, 2026-07-26).
- `ARCH_P95_RATIO_TO_LEGACY` = 1.071 ratio (N=100; fixture=SYNTHETIC_5X, mode=unified)  Source: `reports/generated/bigui_architecture/summary.json` (`9b351820bea6…`, 2026-07-26).
- `ARCH_P95_RATIO_TO_LEGACY` = 1.016 ratio (N=100; fixture=SYNTHETIC_10X, mode=unified)  Source: `reports/generated/bigui_architecture/summary.json` (`9b351820bea6…`, 2026-07-26).
- `ARCH_P95_RATIO_TO_LEGACY` = 0.962 ratio (N=100; fixture=SYNTHETIC_10X, mode=parity)  Source: `reports/generated/bigui_architecture/summary.json` (`9b351820bea6…`, 2026-07-26).

Evidence class: `synthetic`. Claim boundary: Operational overhead only; synthetic scale fixtures cannot support classification or effort claims.

### EXP-037 — Paper baseline reconciliation

The paper and current repository can be aligned on corpus and architecture counts, but not on independent classification performance.

- `PAPER_CASE_MODEL_COUNT` = 178 case models (N=178; aggregate)  Source: `docs/research/bigui/baseline-comparison-results-v1.json` (`52a39a9a8b36…`, 2026-07-26).
- `CURRENT_CASE_MODEL_COUNT` = 179 case models (N=179; aggregate)  Source: `docs/research/bigui/baseline-comparison-results-v1.json` (`52a39a9a8b36…`, 2026-07-26).
- `PAPER_PATTERN_COUNT` = 26 patterns (N=26; aggregate)  Source: `docs/research/bigui/baseline-comparison-results-v1.json` (`52a39a9a8b36…`, 2026-07-26).
- `CURRENT_PATTERN_COUNT` = 27 patterns (N=27; aggregate)  Source: `docs/research/bigui/baseline-comparison-results-v1.json` (`52a39a9a8b36…`, 2026-07-26).
- `PAPER_CURRENT_CLASSIFICATION_COMPARISON_ELIGIBLE` = 0 boolean (N=1; aggregate)  Source: `docs/research/bigui/baseline-comparison-results-v1.json` (`52a39a9a8b36…`, 2026-07-26).

Evidence class: `offline`. Claim boundary: The comparison reconciles versions and capabilities; it cannot prove higher classification accuracy than the paper.

### EXP-040 — Thesis claim-readiness audit

The thesis traceability audit separates supported mechanism claims from empirical improvement claims that remain unopened.

- `THESIS_SAFE_CURRENT_CLAIMS` = 4 claims (N=4; aggregate)  Source: `docs/research/bigui/baseline-comparison-results-v1.json` (`52a39a9a8b36…`, 2026-07-26).
- `THESIS_EMPIRICAL_IMPROVEMENT_CLAIMS_READY` = 0 claims (N=3; aggregate)  Source: `docs/research/bigui/baseline-comparison-results-v1.json` (`52a39a9a8b36…`, 2026-07-26).
- `THESIS_HYPOTHESES_CONFIRMED` = 0 hypotheses (N=4; aggregate)  Source: `docs/research/bigui/baseline-comparison-results-v1.json` (`52a39a9a8b36…`, 2026-07-26).
- `THESIS_TRACEABILITY_RECORDS` = 7 records (N=7; aggregate)  Source: `docs/research/bigui/baseline-comparison-results-v1.json` (`52a39a9a8b36…`, 2026-07-26).

Evidence class: `offline`. Claim boundary: Readiness and traceability do not substitute for the missing independent observations.

## Scope, data, and metric definitions

The benchmark covers the tracked sanitized tier. Raw reviewer sheets, labels, transcripts, and controlled evidence remain local. Every accepted observation is evaluated for source hash, cohort hash, denominator, missingness, evidence class, and claim boundary.

No global weighted value score is calculated. The program reports seven independent dimensions: protocol, data, execution, reproducibility, safety, comparability, and empirical validity.

### Baseline ladder

| Baseline | Purpose | Current state |
| --- | --- | --- |
| B0 — Frozen original Agent 4 | Preserve the official original classification output and paper-aligned architecture reference. | available |
| B1 — Non-destructive H-layer mechanism | Measure M1–M4B-1 review, feedback, memory, advice, comparison, unified-contract, and parity behavior. | mechanism_only |
| B2 — Independent expert-labeled baseline | Establish classification validity and reviewer agreement against generalization-safe gold labels. | not_eligible |
| B3 — Frozen deterministic candidate | Compare one preregistered non-destructive policy candidate on development data. | not_eligible |
| B4 — Sealed holdout pilot | Measure a frozen candidate once on the sealed eight-row holdout. | not_started |
| B5 — External education replication | Test external validity on a new education-domain batch. | not_started |

## Methodology

Each experiment is assessed against its declared question, baseline, comparator, metrics, gates, source-backed accepted runs, metric observations, and claim boundary. Non-executed human studies receive a formal eligibility verdict rather than fabricated results. Direct deltas are allowed only when cohort, partition, baseline, policy, prompt, model, metric definition, leakage class, and evidence class are equivalent except for the declared treatment.

## All-experiment evaluation

| Experiment | Execution | Verdict | Protocol | Data | Reproducibility | Safety | Comparability | Empirical validity | Observations |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | ---: |
| EXP-000 — Existing packaged results audit | parked | PARKED_NO_RUN | pass | not_measured | not_measured | not_applicable | partial | not_applicable | 0 |
| EXP-001 — M4B-1 memory-informed parallel comparison experiment | executed | MEASURED_PASS | pass | pass | pass | pass | pass | not_applicable | 7 |
| EXP-002 — Expert label expansion and holdout evaluation | executed | MEASURED_PASS | pass | pass | pass | not_applicable | pass | not_applicable | 3 |
| EXP-003 — Accuracy improvement evaluation | executed | MEASURED_PARTIAL | pass | pass | pass | not_applicable | pass | not_eligible | 5 |
| EXP-004 — Policy sensitivity simulation | executed | MEASURED_PASS | pass | pass | pass | not_applicable | pass | not_applicable | 32 |
| EXP-005 — Real-label accuracy evaluation and policy gate | executed | MEASURED_PASS | pass | pass | pass | not_applicable | pass | not_eligible | 5 |
| EXP-006 — H-Listen event replay | executed | MEASURED_PASS | pass | pass | pass | not_applicable | pass | not_applicable | 6 |
| EXP-007 — S2 dosage-mode replay | executed | MEASURED_PARTIAL | pass | pass | pass | not_applicable | pass | not_applicable | 30 |
| EXP-008 — Early-trigger mining | executed | MEASURED_PASS | pass | pass | pass | not_applicable | pass | not_applicable | 10 |
| EXP-009 — H-Verify seeded-conflict dry run | executed | MEASURED_PASS | pass | pass | pass | not_applicable | pass | not_applicable | 10 |
| EXP-010 — Convergence-bound sweep | executed | MEASURED_PASS | pass | pass | pass | not_applicable | pass | not_applicable | 16 |
| EXP-011 — Version 0 vs Version 1 comparison | parked | PARKED_NO_RUN | pass | not_measured | not_measured | not_applicable | partial | not_eligible | 0 |
| EXP-012 — Validated EXP-005 baseline interface (M-D) | executed | MEASURED_PARTIAL | pass | pass | pass | not_applicable | pass | not_eligible | 8 |
| EXP-013 — Event-contract fidelity | executed | MEASURED_PASS | pass | pass | pass | not_applicable | pass | not_applicable | 4 |
| EXP-014 — Replay determinism | executed | MEASURED_PASS | pass | pass | pass | not_applicable | pass | not_applicable | 2 |
| EXP-015 — Workload, bundling, and fairness | executed | MEASURED_PASS | pass | pass | pass | not_applicable | pass | not_applicable | 8 |
| EXP-016 — Role-based action authorization (not claim-specific authority - see ISS-045) and timeout safety | executed | MEASURED_PASS | pass | pass | pass | pass | pass | not_applicable | 3 |
| EXP-017 — Verification provenance | executed | MEASURED_PASS | pass | pass | pass | not_applicable | pass | not_applicable | 2 |
| EXP-018 — Correction-proposal dry run | executed | MEASURED_PASS | pass | pass | pass | pass | pass | not_applicable | 3 |
| EXP-019 — Reviewer calibration without evaluation leakage | not_executed | GATED_NOT_RUN | pass | not_measured | not_measured | not_applicable | partial | not_eligible | 0 |
| EXP-020 — Independent expert labeling of 24 safe candidates | not_executed | GATED_NOT_RUN | pass | not_measured | not_measured | not_applicable | partial | not_eligible | 0 |
| EXP-021 — Development-only baseline error characterization | not_executed | GATED_NOT_RUN | pass | not_measured | not_measured | not_applicable | partial | not_eligible | 0 |
| EXP-022 — Routing and retrieval validity audit | not_executed | GATED_NOT_RUN | pass | not_measured | not_measured | not_applicable | partial | not_eligible | 0 |
| EXP-023 — Deterministic policy development | not_executed | GATED_NOT_RUN | pass | not_measured | not_measured | not_applicable | partial | not_eligible | 0 |
| EXP-024 — One-time sealed eight-row holdout pilot | not_executed | GATED_NOT_RUN | pass | not_measured | not_measured | not_applicable | partial | not_eligible | 0 |
| EXP-025 — External education-domain replication | not_executed | GATED_NOT_RUN | pass | not_measured | not_measured | not_applicable | partial | not_eligible | 0 |
| EXP-026 — Human-effort study | not_executed | GATED_NOT_RUN | pass | not_measured | not_measured | not_applicable | partial | not_eligible | 0 |
| EXP-027 — Ablation and robustness | not_executed | GATED_NOT_RUN | pass | not_measured | not_measured | not_applicable | partial | not_eligible | 0 |
| EXP-028 — Model execution reproducibility and drift | not_executed | GATED_NOT_RUN | pass | not_measured | not_measured | not_applicable | partial | not_eligible | 0 |
| EXP-029 — Frozen candidate-model comparison | not_executed | GATED_NOT_RUN | pass | not_measured | not_measured | not_applicable | partial | not_eligible | 0 |
| EXP-030 — BigUI source fidelity and provenance | executed | MEASURED_PARTIAL | pass | pass | pass | not_applicable | pass | not_applicable | 2 |
| EXP-031 — BigUI formative usability | not_executed | GATED_NOT_RUN | pass | not_measured | not_measured | not_applicable | partial | not_applicable | 0 |
| EXP-032 — BigUI decision-support comparison | not_executed | GATED_NOT_RUN | pass | not_measured | not_measured | not_applicable | partial | not_applicable | 0 |
| EXP-033 — Full-corpus runtime parity | executed | MEASURED_PASS | pass | pass | pass | pass | pass | not_applicable | 4 |
| EXP-034 — H-layer topology trade-off | executed | MEASURED_PASS | pass | pass | pass | not_applicable | pass | not_applicable | 18 |
| EXP-035 — Fault injection and authority safety | executed | MEASURED_PASS | pass | pass | pass | pass | pass | not_applicable | 11 |
| EXP-036 — Scale, latency, and reproducibility | executed | MEASURED_PASS | pass | pass | pass | not_applicable | pass | not_applicable | 54 |
| EXP-037 — Paper baseline reconciliation | executed | MEASURED_PASS | pass | pass | pass | not_applicable | pass | not_applicable | 7 |
| EXP-038 — Architecture improvement scorecard | executed | MEASURED_PASS | pass | pass | pass | not_applicable | pass | not_applicable | 2 |
| EXP-039 — Cross-experiment comparability and deltas | executed | MEASURED_PASS | pass | pass | pass | not_applicable | pass | not_applicable | 2 |
| EXP-040 — Thesis claim-readiness audit | executed | MEASURED_PASS | pass | pass | pass | not_applicable | pass | not_applicable | 4 |

## Limitations and robustness

- The paper comparison supports version and architecture alignment, not a paired accuracy result.
- Offline and synthetic fixtures do not establish external validity or population-level human benefit.
- Machine-specific latency values support local engineering decisions only.
- Protocol completeness does not substitute for execution.
- Safe N=0 forces all empirical classification fields to remain null.

## Recommended next steps

1. Use the per-dimension scorecard as the program baseline and never collapse protocol, safety, latency, and empirical validity into one value score.
2. Keep EXP-007 routing configurations on a workload-versus-coverage Pareto chart; do not name a default until M-03 and adjudicated routing targets exist.
3. Repeat EXP-036 on a second controlled machine and fix the unified-P95 interval computation before claiming a target pass at scale; preserve exact parity, determinism, and baseline hashes.
4. Approve and execute EXP-019/020 to obtain two independent reviews for all 24 safe candidates; only then populate classification metrics.
5. Run EXP-031 after the UI is frozen, then preregister EXP-032 before making a BigUI decision-value claim.
6. Refresh this benchmark atomically whenever an accepted run is added; rejected or stale runs must preserve the last accepted snapshot.

## Further analytical questions

- Which EXP-036 processing stage causes the p95 overhead, and can it be reduced without changing canonical output?
- Which routing configuration remains on the Pareto frontier after adjudicated routing targets become available?
- Do reviewers agree on the 24 safe candidates, and which Agent 4 error categories dominate after adjudication?
- Does BigUI improve evidence-state interpretation without increasing overclaim errors?
- Does a frozen deterministic candidate produce positive net correction on unseen data without macro-F1 or subgroup harm?

## Claim boundary

The benchmark demonstrates mechanism, architecture, safety, observability, routing, provenance, and reproducibility results. It does not demonstrate improved classification accuracy, generalization, benchmark superiority, or human-effort reduction.
