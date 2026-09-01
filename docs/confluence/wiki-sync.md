# Confluence Wiki Sync

Curated Confluence publishing workflow for the VEGO-AI research workspace. The repository and `docs/agent-memory/` remain the source of truth.

## Current mode

- Live Confluence target: configured locally, but Atlassian Rovo access is not granted yet.
- Default behavior: generate local Markdown page bodies in `docs/confluence/outbox/`.
- Generated outbox files and the manual sync pack are ignored by Git.

## Target

The intended live wiki target is:

| Field | Value |
| --- | --- |
| Site URL | `https://alih10j.atlassian.net/wiki` |
| Cloud ID | `724252a1-a5b7-45a5-b6ec-27a8292197ec` |
| Space | `~71202099edcf0e26ec40cea521806deb9e9687` |
| Home page ID | `294914` |
| Layout | Page `294914` is `VEGO-AI Wiki Home`; the other curated pages are children. |

Current access note: Atlassian Rovo reports that cloud `724252a1-a5b7-45a5-b6ec-27a8292197ec` is not explicitly granted; rechecked 2026-06-14 13:40 +03:00. A Chrome UI fallback was checked 2026-06-13 13:50 +03:00, but the extension-backed browser channel was unavailable after retry. Live sync must wait until Atlassian access is granted or a browser route is enabled.

## End-of-prompt order

For every meaningful prompt:

1. Run `.\scripts\agent-memory-start.ps1` at the beginning.
2. Do the requested work.
3. Update memory files and run `.\scripts\agent-memory-finish.ps1`.
4. Run `.\scripts\build-confluence-wiki.ps1`; this also refreshes `docs/dashboards/status-snapshot.generated.md` and `docs/confluence/manual-sync-pack.generated.md`.
5. Run `.\scripts\dashboard-health.ps1 -RequireOutbox` to verify the generated dashboard/wiki tracking package.
6. If `docs/confluence/wiki-sync-config.local.json` has real Confluence IDs and Atlassian Rovo access is granted, update the configured Confluence pages with Atlassian Rovo using `contentFormat: markdown`.
7. If IDs or access are missing, leave the generated outbox and manual sync pack as the pending wiki update and mention that live Confluence sync is pending.

## Curated pages

| Page | Generated File | Purpose |
| --- | --- | --- |
| VEGO-AI Wiki Home | `vego-ai-wiki-home.md` | Project overview and navigation. |
| VEGO-AI Current State | `vego-ai-current-state.md` | Latest status, active risks, and next steps. |
| VEGO-AI Progress Dashboard | `vego-ai-progress-dashboard.md` | KPI, milestone, and validated-results tracking. |
| VEGO-AI Update Changelog | `vego-ai-update-changelog.md` | Recent prompt/update history. |
| VEGO-AI Research Operations | `vego-ai-research-operations.md` | Roadmap, risks, experiment registry, audit posture. |

## Configuration

Copy `docs/confluence/wiki-sync-config.template.json` to `docs/confluence/wiki-sync-config.local.json` and fill:

- `cloudId`
- `spaceId`
- `parentId`, optional
- `pages.home.pageId`
- `pages.currentState.pageId`
- `pages.dashboard.pageId`
- `pages.changelog.pageId`
- `pages.researchOperations.pageId`

Do not commit the local config.

The local config currently maps `home.pageId` to `294914`; child page IDs remain blank until the pages are created or discovered after Atlassian access is granted.

## Manual fallback

If Atlassian Rovo and browser-based access are unavailable, use `docs/confluence/manual-sync.md`. The generated `docs/confluence/manual-sync-pack.generated.md` contains the five curated page bodies and hashes for an approved manual update path.

## Safety rules

- Do not mirror ignored artifacts or controlled contents.
- Do not paste PDF, model, analysis, eval output, or raw data contents into Confluence.
- Use metadata-only summaries until `docs/research/publishability-register.md` says otherwise.
- Confluence updates are agent-enforced workflow, not a background service.
