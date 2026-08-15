# Progress Visualizations

Generated: 2026-08-10 19:00 +03:00.

This generated dashboard summarizes docs/agent-memory/progress.md, docs/dashboards/progress-dashboard.md, and docs/dashboards/kpi-register.md. Regenerate it with .\scripts\build-progress-visualizations.ps1.

## Summary Cards

| Signal | Value | Visual |
| --- | --- | --- |
| Milestone completion | 74 of 84 done/green | [##################--] 88% |
| KPI green rate | 11 of 30 green | [#######-------------] 37% |
| Active work closed | 21 of 50 done | [########------------] 42% |
| Executive snapshot green | 6 of 22 green | [#####---------------] 27% |

## KPI Status Mix

```mermaid
pie showData
    title KPI status mix
    "Done/Green" : 11
    "In progress/Yellow" : 12
    "Risk/Red" : 2
    "Blocked" : 5
```

## Active Work Status Mix

```mermaid
pie showData
    title Active work status mix
    "Done/Green" : 21
    "In progress/Yellow" : 26
    "Blocked" : 2
    "Other" : 1
```

## Milestone Timeline

```mermaid
flowchart LR
    classDef done fill:#e6f4ea,stroke:#2f855a,color:#1f2933;
    classDef wait fill:#fff8e1,stroke:#b7791f,color:#1f2933;
    classDef blocked fill:#fde8e8,stroke:#c53030,color:#1f2933;
    classDef planned fill:#eef2ff,stroke:#5a67d8,color:#1f2933;
    m0["M1
Done"]:::done
    m1["M2
Done"]:::done
    m2["M3
Done"]:::done
    m3["M4A
Done"]:::done
    m4["M4B-1
Done / experimental"]:::done
    m5["M4B-2
Deferred"]:::blocked
    m6["M5
Planned"]:::planned
    m7["M6
Planned"]:::planned
    m0 --> m1
    m1 --> m2
    m2 --> m3
    m3 --> m4
    m4 --> m5
    m5 --> m6
    m6 --> m7
```

## Evidence Gate Flow

```mermaid
flowchart TD
    classDef done fill:#e6f4ea,stroke:#2f855a,color:#1f2933;
    classDef wait fill:#fff8e1,stroke:#b7791f,color:#1f2933;
    classDef blocked fill:#fde8e8,stroke:#c53030,color:#1f2933;
    m4b["M4B-1 baseline
implemented / parallel-only"]:::done
    exp005["EXP-005 real labels
0 valid labels in current gate"]:::blocked
    eval["EXP-003 / EXP-005 rerun
requires real labels"]:::blocked
    policy["Policy refinement / M4B-2
blocked until evidence and approval"]:::blocked
    thesis["Thesis evidence
mechanism readiness now; accuracy later"]:::wait
    m4b --> exp005 --> eval --> policy
    exp005 --> thesis
```

## EXP-005 Gate

> Current generated verdict is blocked: 27 rows, 24 safe candidates, 0 supplied labels, 0 valid labels, 0 safe labels.

## Open Active Work

| ID | Status | Summary | Next Step |
| --- | --- | --- | --- |
| TASK-003 | Open | Audit data sensitivity and provenance. | Review `VEGO-AI/inputs/`, `VEGO-AI/models/`, `VEGO-AI/analysis/`, and the IRB-related PDF. |
| TASK-004 | In progress | Map existing paper/package results to experiments. | Continue `EXP-000-existing-packaged-results-audit` without copying controlled artifacts into Git. |
| TASK-005 | Blocked | Keep curated Confluence wiki current. | Grant Atlassian Rovo access to cloud `724252a1-a5b7-45a5-b6ec-27a8292197ec`, then create/update child pages and store page IDs in local config. |
| TASK-008 | Open | Keep progress, KPI, and results dashboards current. | Update `docs/dashboards/` whenever progress, KPI values, validated results, or Confluence tracking status changes. |
| TASK-009 | Open | Keep dashboard/wiki tracking health verified. | Run `.\scripts\dashboard-health.ps1 -RequireOutbox` after every Confluence outbox build. |
| TASK-010 | Open | Keep runtime dashboard snapshot fresh. | Run `.\scripts\build-confluence-wiki.ps1` after memory/dashboard updates; it regenerates `docs/dashboards/status-snapshot.generated.md`. |
| TASK-011 | Open | Keep manual Confluence sync pack fresh while live access is blocked. | Run `.\scripts\build-confluence-wiki.ps1`; it regenerates `docs/confluence/manual-sync-pack.generated.md`. |
| TASK-013 | In review | Harden M4B nested schema requirements. | Review and merge PR #6. |
| TASK-016 | Open | Complete EXP-001 expert-label evaluation. | Add held-out/cross-setting expert labels, rerun `.\scripts\build-exp001-evaluation.ps1`, and update the evaluation report with generalization-safe metrics. |
| TASK-017 | Open | Fill EXP-002 expert labeling package. | Human/supervisor should label at least 20 rows, preferably all 27 current rows, then rerun evaluation with leakage-aware partitions. |

## Generated HTML

Open docs/dashboards/progress-visualizations.generated.html locally for the card-and-bar version.
