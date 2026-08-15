# VEGO-AI H-Layer Program Overview

This page mirrors the generated unified program overview (replay suite, conformance suite,
program validation, EXP-005 gate, decision snapshot, accepted iterations, and metric
trajectories). Regenerate locally with `python scripts/build_hlayer_program_overview.py`;
an interactive HTML version with trajectory charts sits next to the source file.

# H-Layer Program Overview

Generated: 2026-07-28T13:27:40.658590+00:00 (regenerate: `python scripts/build_hlayer_program_overview.py`)

Claim scope: Program status overview only: joins existing offline mechanism/conformance artifacts. It creates no evidence and authorizes no accuracy, generalization, or clinical claim.

**Gate state:** EXP-005 has 0 validated generalization-safe expert labels; downstream evaluation remains parked.

## Program At A Glance

| Area | State |
| --- | --- |
| Replay suite (EXP-006..010, 012) | run hlayer-20260726T140440Z-4a5a62e6ff |
| Conformance suite (EXP-013..018) | PASS (run HLAYER-CONFORMANCE-304738316e6a581c3c64) |
| Program validation | PASS (8 checks) |
| Accepted iterations | 15 (iter_015 latest) |
| EXP-005 validated safe labels | 0 |
| Program mode | offline_only |
| Live shadow authorized | False |

## Iterations

| Iteration | Kind | Verdict |
| --- | --- | --- |
| iter_001 | - | - |
| iter_002 | - | - |
| iter_003 | - | - |
| iter_004 | - | - |
| iter_005 | - | - |
| iter_006 | - | - |
| iter_007 | - | - |
| iter_008 | reliability_only | NEUTRAL |
| iter_009 | offline_metric_and_contract_repair | NEUTRAL |
| iter_010 | reliability_only | NEUTRAL |
| iter_011 | reliability_only | NEUTRAL |
| iter_012 | reliability_only | NEUTRAL |
| iter_013 | reliability_only | NEUTRAL |
| iter_014 | reliability_only | NEUTRAL |
| iter_015 | reliability_only | NEUTRAL |

## Metric Trajectories (threshold_sev2, pooled ALL)

| Iteration | Event load | Weighted coverage | High-sev coverage | Efficiency | Bundled load | Bundled efficiency |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| iter_002 | 0.799 | 0.96 | 1.0 | 1.202 | - | - |
| iter_003 | 0.799 | 0.96 | 1.0 | 1.202 | - | - |
| iter_004 | 0.799 | 0.96 | 1.0 | 1.202 | - | - |
| iter_005 | 0.799 | 0.96 | 1.0 | 1.202 | 0.799 | 1.202 |
| iter_006 | 0.799 | 0.96 | 1.0 | 1.202 | 0.891 | 1.077 |
| iter_007 | 0.799 | 0.96 | 1.0 | 1.202 | 0.891 | 1.077 |
| iter_008 | 0.799 | 0.981 | 1.0 | 1.228 | 0.796 | 1.233 |
| iter_009 | 0.799 | 0.981 | 1.0 | 1.228 | 0.796 | 1.233 |
| iter_010 | 0.799 | 0.981 | 1.0 | 1.228 | 0.796 | 1.233 |
| iter_011 | 0.799 | 0.981 | 1.0 | 1.228 | 0.796 | 1.233 |
| iter_012 | 0.799 | 0.981 | 1.0 | 1.228 | 0.796 | 1.233 |
| iter_013 | 0.799 | 0.981 | 1.0 | 1.228 | 0.796 | 1.233 |
| iter_014 | 0.799 | 0.981 | 1.0 | 1.228 | 0.796 | 1.233 |
| iter_015 | 0.799 | 0.981 | 1.0 | 1.228 | 0.796 | 1.233 |

Full per-mode trajectories: `metric_trajectories.csv` in this directory.

## Sources

- `reports/generated/hlayer_suite_manifest.json` (replay suite)
- `reports/generated/hlayer_conformance/manifest.json` (conformance suite)
- `reports/generated/hlayer_program_validation/latest.json` (program validator)
- `reports/generated/hlayer_iterations/iter_*/` (accepted iterations)
- validated EXP-005 gate + supervisor decision snapshot via `hlayer_harness`

