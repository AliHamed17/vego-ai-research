# Progress Dashboard

Last curated update: 2026-09-06 by Codex.

## Executive Snapshot

The July 29 requirements-closure program is the current working authority, subject to bilingual and supervisor confirmation. All 19 requirements, 15 actions, and 10 open questions are controlled. A deterministic preliminary ledger accounts for all 1,195 machine segments, but bilingual/speaker review and adjudication remain 0/1,195. The recommended one-plus-three architecture, three studies, Plan A/B, proposal `v0.1`, and August 5 pre-read remain unapproved and unsent. The August 5 supervisor package is built locally as a 12-slide English core plus nine-slide appendix, with 21/21 source-note sections, corrected PPTX/PDF, visual QA, and review workbook; the previous offline ZIP is stale and must be rebuilt after rehearsal/freeze. Human rehearsal, Ali release approval, delivery, access tests, and supervisor decisions remain open. Medical readiness is NO-GO at 0/6 gates, and EXP-005 remains 0/24, so no accuracy, generalization, or clinical-performance gain is claimed.

Run `.\scripts\build-progress-visualizations.ps1` for generated Mermaid status charts and a local HTML progress dashboard at `docs/dashboards/progress-visualizations.generated.html`.
Run `.\scripts\build-e2e-progress-report.ps1` for the full E2E progress report and local web page at `reports/generated/e2e_dashboard/index.html`.

| Area | Status | Evidence | Next Action |
| --- | --- | --- | --- |
| July 29 doctoral control package | Yellow / awaiting supervisor decisions | `docs/research/phd-proposal/`: 19/15/10 master register, exact one-plus-three RQ recommendation, three-study contract, legacy crosswalk, claim/RACI/RAID registers, proposal `v0.1`, and August 5 pre-read. | Ali reviews the exact package; Iris and Arnon decide the RQs, studies, Plan A/B, owners, literature categories, and dates. |
| Study 2A ON/OFF preparation | Ready for independent review; run authorization pending | Draft PR #40 (`3deb8b4`) contains the separate ON/OFF configs, schema, deterministic preparation manifest, Hebrew preregistration/readiness docs, and disabled-by-default offline harness. CI run `34000338373` passed all six jobs. | Review the baseline definition and parity contract; issue a fresh explicit authorization before any provider-backed condition run. |
| July 29 call extraction and assurance | Structure green / human gates blocked | S-0001–S-1195 preliminary CSV/JSON and review workbook; 910 machine-linked rows, 285 human-review placeholders; separate Reviewer A/B and third-person merge interface; IRIS-EXP-01–10 validator. | Complete both 1,195-segment reviews plus one full-media record per reviewer and adjudicate every disagreement; readiness/closure remain non-zero meanwhile. |
| August 5 supervisor presentation | Local construction and automated/render QA green; human delivery readiness yellow | 21-slide PPTX/PDF, 21/21 source-note sections, 44/44 control reachability, 21/21 PowerPoint-native renders inspected; previous backup invalidated. | Ali reviews the exact package; run timed and adversarial human rehearsals; rebuild/freeze the backup; then authorize delivery and record Iris/Arnon access tests. |
| Private Drive and literature workbook | Green for initial structure; sharing/search pending | Ali-owned nine-folder Drive and native six-tab Sheet are recorded in `drive-workspace-manifest.md`; no external share or completed search is claimed. | Ali authorizes exact recipients, then execute and log database searches and screening. |
| Medical readiness and MIMIC audit | Blocked / 0 of 6 gates | `medical-readiness-scorecard.md` and metadata-only audit: 25 CSVs, 39.65 GiB, missing `NOTEEVENTS`, no patient-row inspection. | Collect all six prerequisite proofs; default to Plan B on August 26 if any critical gate remains open. |
| July 1 redirect and July 24 continuation | Legacy / absorbed | Both files retain their evidence and safety gates but point to the July 29 successor program. | Use the legacy RQ and decision crosswalks; do not treat older plans as active authority. |
| Phase 0 truth/governance reconciliation | Complete | `docs/research/h-layer/phase-0-boundary-record.md`; source reconciliation, generated memory/wiki refreshes, focused tests, and protected-path checks pass. | Preserve unrelated changes and keep runtime work gated by recorded authorization. |
| Offline experiment program | Yellow / gated | Ten accepted iterations; iteration 009 repairs contracts/metrics, iteration 010 is a reliability-only rerun, and the separate conformance suite passes offline. | Preserve the six-experiment replay contract; keep iteration 011 and live integration blocked until their gates clear. |
| Passive shadow listener | Blocked | `allowed-touch-proposal.md` and template are proposals only. | Require M-05 plus separate exact-file authorization; default-off/fail-open if later approved. |
| MediVARIA PhD-track study plan | Conditional Plan A proposal | `docs/research/medivaria/medivaria-study-plan.md`: clinical transfer mapping and legacy questions; no clinical-performance evidence exists. | Crosswalk to SQ3 and keep operational work blocked until the six medical gates pass. |
| Source baseline | Documentation branch; production unchanged | Branch `docs/iris-july29-phd-execution`; ten July 29 evidence artifacts preserved in commit `3d0beca`. | Stage only intended research, tracking, and generated documentation paths; verify protected behavior remains untouched. |
| M1 Human Review Queue | Green | Implemented and tested. | Use as upstream evidence for artifact manifest. |
| M2 Human Feedback Manager | Green | Implemented and tested. | Include schema/docs/tests in artifact manifest. |
| M3 Human Judgment Memory | Green | Tag `milestone-m3-human-judgment-memory`. | Reference tag in thesis evidence. |
| M4A Memory Advisory Layer | Green | Tag `milestone-m4a-memory-advisory`. | Include advisory-only proof in manifest. |
| M4B-1 Memory-informed parallel comparison | Historical implementation / evaluation pending | Historical merge `944c922`; tag `research-state-m4b1-deterministic-comparison`. | Keep as evaluation history; do not infer current worktree cleanliness or improvement. |
| Visualizer model/result matching | Green | PR #7 real-display validated, merged as `78b261e`, tag `research-state-visualizer-ux-clean`. | Preserve no-silent-mismatch and read-only research-panel boundaries. |
| EXP-001 evaluation | Yellow | Initial mechanism/readiness run generated ignored `reports/generated/exp001/` tables. | Add held-out or cross-setting expert labels before accuracy/generalization claims. |
| EXP-002 expert labeling package | Yellow | Ignored `reports/generated/exp002/` package generated: 27 rows, 24 generalization-safe candidates, 3 existing same-pattern labels. | Human/supervisor labels should fill at least 20 rows, preferably all 27 current rows. |
| Dashboard/wiki tracking gate | Historical pass / refresh needed | Runtime snapshot and manual sync pack exist; curated dashboard sources changed on 2026-07-10. | Announce generated-file refreshes, rebuild the outbox, then rerun `dashboard-health -RequireOutbox`. |
| Data/IRB audit | Red | Controlled artifacts still ignored and metadata-only. | Continue audit before sharing artifacts. |
| Confluence live tracking | Blocked | Outbox/manual sync pack exists; Atlassian Rovo cloud access not explicitly granted as of 2026-06-14 14:50 +03:00; Chrome extension fallback unavailable as of 2026-06-13 13:50 +03:00. | Grant Rovo access or enable the Chrome extension route, then create/update child pages. |

## Milestone Flow

| Milestone | Research Meaning | State | Anchor |
| --- | --- | --- | --- |
| M1 | Human judgment is selectively triggered. | Done | Human Review Queue docs/tests. |
| M2 | Human decisions are structurally captured. | Done | Human Feedback Manager docs/tests. |
| M3 | Human judgment is stored as reusable memory. | Done | `milestone-m3-human-judgment-memory`. |
| M4A | Reusable judgment is retrieved as advisory evidence. | Done | `milestone-m4a-memory-advisory`. |
| M4B-1 | Memory advice may inform a deterministic parallel comparison. | Done / experimental | `research-state-m4b1-deterministic-comparison`; EXP-001 evaluation still pending. |
| M4B-2 | Optional LLM/Agent 4 mode. | Deferred | Not approved. |
| M5 | Human-approved guideline refinement. | Planned | Roadmap. |
| M6 | Evaluation and thesis synthesis. | Planned | Evaluation plan and thesis outline. |

## Immediate Work Queue

| Priority | Work Item | Owner | Status |
| --- | --- | --- | --- |
| P1 | Review the exact August 5 package before any external share. | Ali | Human review |
| P1 | Decide RQ wording, three-study map, Plan A/B labels, medical owner, literature categories, Penina dates, and administrative owner. | Iris, Arnon, Ali | Awaiting August 5 |
| P1 | Record decisions and proposal deltas within 24 hours. | Ali | Awaiting decisions |
| P1 | Execute reproducible literature searches, deduplication, screening, identity/claim verification, and synthesis. | Ali | Ready to start |
| P1 | Obtain written official candidacy-process and deadline confirmation. | Department / Graduate Studies owner | Open |
| P1 | Maintain medical NO-GO at 0/6 and prepare the August 26 fallback review. | Ali + named gate owners | Blocked |
| P1 | Complete bilingual/speaker review before quotations or final attribution. | Ali + bilingual reviewer | Open |
| P1 | Approve EXP-005 protocol and schedule two human reviewers; never prefill labels. | Supervisors / research lead | Human-gated |
| P2 | Refresh project memory, dashboards, local wiki outbox, and health evidence after each tranche. | Codex / Claude | Active rule |

## Confluence Tracking

The generated Confluence outbox should include a dashboard page sourced from:

- `docs/dashboards/status-snapshot.generated.md` (ignored runtime snapshot)
- `docs/dashboards/progress-visualizations.generated.md` (ignored generated visual summary)
- `docs/dashboards/e2e-dashboard.generated.md` (ignored generated E2E report)
- `docs/dashboards/progress-dashboard.md`
- `docs/dashboards/kpi-register.md`
- `docs/dashboards/results-dashboard.md`

Until live Confluence access is granted, `docs/confluence/outbox/` is the pending wiki update.
`docs/confluence/manual-sync-pack.generated.md` is the ignored fallback publishing package with the same curated page bodies and hashes.
