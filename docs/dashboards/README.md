# Dashboards

Curated dashboard sources for VEGO-AI progress, KPIs, validated results, and generated review views.

## Purpose

- Track project state locally in Git
- Generate Confluence dashboard pages through `scripts/build-confluence-wiki.ps1`
- Provide metadata-only summaries for evidence-backed reporting

The full memory, dashboard, Confluence, and scheduled update flow is documented in `../operations/progress-update-architecture.md`.

## Dashboard files

| File | Purpose |
| --- | --- |
| `progress-dashboard.md` | Milestone and active-work status for quick project tracking. |
| `kpi-register.md` | KPI definitions, current values, status, source evidence, and next actions. |
| `results-dashboard.md` | Validated implementation and research result snapshots. |
| `status-snapshot.generated.md` | Ignored runtime snapshot generated for Confluence from current repo/outbox state. |
| `progress-visualizations.generated.md` | Ignored Mermaid and table visualizations generated from current progress and KPI files. |
| `progress-visualizations.generated.html` | Ignored local card-and-bar dashboard generated from current progress and KPI files. |
| `e2e-dashboard.generated.md` | Ignored full E2E progress report generated from memory, dashboards, experiment summaries, review state, and Git status. |
| `reports/generated/e2e_dashboard/index.html` | Ignored local static web dashboard for end-to-end progress review. |

## Checks

- Run `.\scripts\build-dashboard-snapshot.ps1` to refresh the ignored runtime status snapshot directly.
- Run `.\scripts\build-progress-visualizations.ps1` to refresh the ignored visual progress dashboard.
- Run `.\scripts\build-e2e-progress-report.ps1` to refresh the ignored full report and local web page.
- Run `.\scripts\dashboard-health.ps1` to verify dashboard sources, Confluence template wiring, local sync config shape, and generated outbox when present.
- Run `.\scripts\dashboard-health.ps1 -RequireOutbox` after `.\scripts\build-confluence-wiki.ps1` to require all five generated wiki page bodies.
- Run `.\scripts\dashboard-health.ps1 -RequireLivePageIds` only after Atlassian Rovo access is granted and child page IDs are recorded locally.
- Use `docs/confluence/manual-sync.md` when a manual Confluence update path is needed while live access is blocked.

## Update rules

- Update these dashboards after meaningful milestone, experiment, review, or publication-state changes.
- Keep values evidence-backed; cite commits, tags, commands, tests, or docs.
- Do not copy controlled artifact contents into dashboards.
- Use metadata-only summaries until publishability is approved.
- The Confluence outbox, `status-snapshot.generated.md`, `progress-visualizations.generated.*`, `e2e-dashboard.generated.md`, `reports/generated/e2e_dashboard/`, and `manual-sync-pack.generated.md` are generated; do not edit them directly.
