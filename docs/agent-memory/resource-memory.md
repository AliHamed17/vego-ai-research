# Shared Resource Memory

This file is the compact shared resource index for Codex and Claude. It points agents to reusable research resources without forcing every prompt to reload downloaded source files.

Last updated: 2026-08-15 by Codex.

## August 12 Evidence-to-Delivery Resources

Tracked sanitized controls:

- `docs/research/meetings/2026-08-12-control-register.csv`
- `docs/research/meetings/2026-08-12-claude-id-crosswalk.csv`
- `docs/research/meetings/2026-08-12-human-review-protocol.md`
- `docs/research/meetings/2026-08-12-machine-evidence-provenance.md`
- `docs/research/meetings/2026-08-12-corrected-meeting-report.en-he.md`
- `docs/research/meetings/2026-08-12-claim-register.csv`
- `docs/research/meetings/2026-08-12-open-decisions.en-he.md`
- `literature/acl2026-human-agent-corpus/`
- `docs/research/meetings/2026-08-19-supervisor-package/final/`

Private aliases and boundaries:

- `PRIVATE_EVIDENCE/packages/aug12-machine-evidence-v3`: exact ten-file machine-only evidence package; human review remains 0/1,280 records per reviewer.
- `NATIVE-WORKBOOK-PRIVATE-01`: canonical native literature workbook binding; public direct locator withheld.
- Scholarship evidence/drafts remain ignored and private; Gmail copies remain drafts and unsent.

Current release boundary: the ACL inventory/offline staging, private machine-only media v3 package,
and exact August 19 package have passed scoped independent review. Human media review remains
0/1,280 records per reviewer. No connector delivery or acceptance is implied.

## Iris Next-Step Execution Program

Canonical and operator interfaces:

- `docs/research/phd-proposal/aug1-oct7-execution-control-board.json`
- `docs/research/phd-proposal/aug1-oct7-execution-control-board.md`
- `docs/research/phd-proposal/next-step-implementation-manifest-2026-08-01.md`
- `docs/research/meetings/2026-08-05-supervisor-release-gate-and-runbook.md`
- `docs/research/meetings/2026-07-29-iris-zoom-reviewer-operations.md`
- `docs/research/phd-proposal/literature-search-execution-register.md`
- `docs/research/phd-proposal/proposal-v0.2-working-draft.md`
- `docs/research/phd-proposal/university-process-inquiry-draft.md`

Local companion output:

- `outputs/iris-next-step-2026-08-01-implementation/VEGO-AI-Iris-Next-Step-Execution-Control-2026-08-01.xlsx` (ignored; exact hash is recorded in the implementation manifest)

Validators:

- `scripts/validate_aug1_oct7_execution_program.py`
- `scripts/validate_iris_zoom_review_batches.py`
- `scripts/validate_iris_requirements_closure.py` (IRIS-EXP-08 also verifies offline-ZIP member hashes)

Current boundary: board structure is valid; all assignee, reviewer, rehearsal,
release, access, supervisor, medical, expert-label, approval, and submission
evidence fields remain human/external gates.

## July 29 Doctoral Execution Program

Local control package:

- `docs/research/phd-proposal/README.md`
- `docs/research/phd-proposal/master-traceability-register.md`
- `docs/research/phd-proposal/2026-08-05-rq-decision-pack.md`
- `docs/research/phd-proposal/three-study-contract.md`
- `docs/research/phd-proposal/proposal-v0.1.md`
- `docs/research/meetings/2026-08-05-supervisor-pre-read.md`
- `docs/research/governance/medical-readiness-scorecard.md`
- `docs/research/governance/mimic-metadata-audit-2026-07-30.md`

External working resources:

| Resource | URL | Current boundary |
| --- | --- | --- |
| Private Ali-owned PhD working folder | `private-binding://phd-working-root` | Nine-folder structure created; current permission state fails the August 12 release control. Direct locator is private. |
| Native literature workbook | `private-binding://native-literature-workbook` | Six tabs and six seed records exist; broad searches and screening are not complete. Direct locator is private. |
| Supplied MIMIC source folder | `restricted-binding://mimic-source-folder` | Source/viewer resource only; leave unchanged and do not treat file visibility as authorization. Direct locator is restricted. |

Operational state:

- Branch: `docs/iris-july29-phd-execution`.
- Preserved evidence commit: `3d0beca`.
- Calendar: historical records describe a Wednesday 09:00-10:00 recurrence through October 7; the
  August 15 live refresh confirmed only the August 19, 09:00-10:00 checkpoint. Recheck later RSVP state.
- Medical readiness: 0/6; no patient-row inspection or medical computation is authorized.
- External sharing: Ali must review and authorize the exact package first.

## HITL / Human-AI Resource Pack

Location:

- `literature/hitl-resource-pack/`

Purpose:

- Support thesis Chapter 2 and methodology framing for reusable human judgment.
- Support EXP-005 supervisor/expert labeling workflow design.
- Support future discussion of reviewer tooling, active learning, and label-quality checks.
- Keep literature and tooling context shared between Codex and Claude.

Tracked files:

- `literature/hitl-resource-pack/README.md`
- `literature/hitl-resource-pack/source-manifest.csv`
- `literature/hitl-resource-pack/bibliography.bib`
- `literature/hitl-resource-pack/tool-fit-matrix.md`

Ignored local files:

- `literature/hitl-resource-pack/downloads/`

Refresh command:

```powershell
.\scripts\download-hitl-resources.ps1
```

Dry-run command:

```powershell
.\scripts\download-hitl-resources.ps1 -DryRun
```

## Current Seed Sources

| ID | Resource | Use In VEGO-AI |
| --- | --- | --- |
| `HAI-001` | Microsoft Guidelines for Human-AI Interaction | Visualizer/review UI transparency, error recovery, and human-AI interaction framing. |
| `GOV-001` | NIST AI Risk Management Framework 1.0 | Governance, risk, human oversight, and claim-boundary language. |
| `HITL-001` | Human-in-the-loop machine learning: a state of the art | Positions active learning, interactive ML, and machine teaching relative to VEGO-AI. |
| `TOOL-001` | Label Studio | Candidate future labeling UI if EXP-005 grows beyond CSV/manual review. |
| `TOOL-002` | Argilla | Candidate future expert-feedback/data-quality collaboration tool. |
| `TOOL-003` | modAL | Future active-learning candidate for selecting high-value review rows after real labels exist. |
| `TOOL-004` | cleanlab | Future label-quality candidate after enough expert labels exist. |
| `MDE-001` | AI Assisted Domain Modeling Explainability and Traceability | Domain-modeling related work; metadata-only unless authorized open copy is confirmed. |

## Presentations & Meetings

| ID | Resource | Location | Status |
| --- | --- | --- | --- |
| `PRES-001` | Supervisor meeting recording (2026-07-03) | `presentations/video1832857678.mp4` | Transcribed |
| `PRES-002` | Supervisor meeting transcript (Hebrew) | `presentations/video1832857678_transcript.txt` | Searchable text |
| `PRES-003` | Supervisor meeting SRT subtitles | `presentations/video1832857678_transcript.srt` | Timestamped |
| `PRES-004` | Supervisor meeting structured notes | `docs/agent-memory/meeting-notes/2026-07-03-supervisor-meeting.md` | Extracted |
| `PRES-005` | Supervisor Zoom demo deck (2026-06-17) | `artifacts/supervisor_demo_2026-06-17/` | Used |
| `PRES-006` | Presentation plan (2026-07-01) | `docs/presentation-plan-2026-07-01.md` | Planning |
| `PRES-007` | August supervisor presentation/video-call checklist | `docs/research/meetings/2026-08-05-supervisor-presentation-checklist.md` | Local 21-slide PPTX/PDF and automated/render QA complete; human rehearsal, Ali release approval, delivery, and access pending |
| `PRES-008` | July 29 requirements closure audit | `docs/research/phd-proposal/iris-requirements-closure-audit.md` | 44/44 controlled; acceptance gates explicit |
| `PRES-009` | August 5 supervisor decisions deck | `presentations/VEGO-AI-Iris-Supervisor-Decisions-2026-08-05.pptx` | 12-slide English core plus nine-slide appendix; 21/21 source notes; local construction only |
| `PRES-010` | July 29 Zoom human-review workbook | `outputs/iris-closure-2026-08-01/Iris_Zoom_Review_Ledger_2026-07-29.xlsx` | 1,195 machine-only rows; 910 control-linked, 285 human-review-needed; dual review/adjudication 0/1,195 |
| `PRES-011` | August 5 presentation/rehearsal/delivery manifests | `docs/research/meetings/2026-08-05-supervisor-presentation-manifest.md` | Local package/QA recorded; human rehearsal, delivery, and access forms remain open |

Key meeting insights captured in `PRES-004`:
- Two VEGO-AI communication types (artifact + Q&A)
- Human expert as passive listener / selective activator
- Feedback must be bi-directional and configurable
- Learning from feedback (not just storage) — core PhD direction
- Literature survey scope: RLHF, agentic architectures, human-AI collaboration
- PhD direct-track discussion and cross-domain expansion

## Thesis Chapters

| ID | Chapter | Location | Status |
| --- | --- | --- | --- |
| `THESIS-01` | Introduction | `thesis/chapters/01-introduction.md` | Drafted |
| `THESIS-02` | Related Work | `thesis/chapters/02-related-work.md` | Drafted (verified cites) |
| `THESIS-03` | Problem & RQ | `thesis/chapters/03-problem-and-rq.md` | Drafted |
| `THESIS-04` | Baseline | `thesis/chapters/04-baseline.md` | Drafted |
| `THESIS-05` | Artifact | `thesis/chapters/05-artifact.md` | Drafted |
| `THESIS-06` | Methodology | `thesis/chapters/06-evaluation-methodology.md` | Drafted |
| `THESIS-07` | Results | `thesis/chapters/07-experimental-results.md` | Blocked on labels |
| `THESIS-08` | Threats | `thesis/chapters/08-threats-to-validity.md` | Drafted |
| `THESIS-09` | Discussion | `thesis/chapters/09-discussion.md` | Drafted |
| `THESIS-10` | Conclusion | `thesis/chapters/10-conclusion.md` | Drafted |

Thesis outline: `thesis/outline.md`

## Experiment Outputs

| ID | Experiment | Location | Status | Key Result |
| --- | --- | --- | --- | --- |
| `EXP-OUT-001` | EXP-001 mechanism evaluation | `reports/generated/exp001/` | Done | 27 rows, 0 changes, 0 safe labels |
| `EXP-OUT-002` | EXP-002 labeling package | `reports/generated/exp002/` | Done | 27 rows, 24 safe candidates |
| `EXP-OUT-003` | EXP-003 accuracy tooling | `reports/generated/exp003/` | Tooling done | Gate: cannot evaluate yet |
| `EXP-OUT-004` | EXP-004 policy sensitivity | `reports/generated/policy_sensitivity/` | Done | Synthetic screening only |
| `EXP-OUT-005` | EXP-005 real-label gate | `reports/generated/exp005_label_review/` | Tooling done | 0 labels, gate closed |
| `EXP-OUT-SIM` | Synthetic accuracy simulation | `reports/generated/synthetic_accuracy_simulation/` | Done | Not real evidence |
| `EXP-OUT-SYN` | Synthetic EXP-005 trial | `reports/generated/exp005_synthetic_trial/` | Done | Design guidance only |

Experiment registry: `experiments/registry.md`

## Architecture & Documentation

| ID | Resource | Location | Purpose |
| --- | --- | --- | --- |
| `ARCH-001` | Workspace diagram | `docs/architecture/workspace-diagram.md` | Mermaid repo structure |
| `ARCH-002` | Project map | `docs/architecture/project-map.md` | Component navigation |
| `ARCH-003` | Progress update diagram | `docs/architecture/progress-update-diagram.md` | Update flow |
| `ARCH-004` | Thesis & progress architecture | `docs/architecture/thesis-and-progress-architecture.md` | Full doc + progress |
| `ARCH-005` | Topology flow report | `artifacts/topology-export/VEGO_TOPOLOGY_FLOW_REPORT.html` | Pipeline visualization |
| `ARCH-006` | Baseline overlay report | `artifacts/topology-export/VEGO_BASELINE_OVERLAY_REPORT.html` | M1-M4B-1 overlay |
| `ARCH-007` | Alignment control | `docs/operations/alignment-control.md` | Claim/evidence checkpoint |
| `ARCH-008` | PhD thesis optimization | `docs/research/phd-thesis-optimization-plan.md` | PhD trajectory control |
| `ARCH-009` | Thesis structure map | `docs/research/thesis-structure-map.md` | Contribution chain |
| `ARCH-010` | Strategic review | `docs/research/strategic-review-and-hardening-plan.md` | Vulnerabilities/gates |

## Scripts & Tools Index

| Script | Purpose | When to Use |
| --- | --- | --- |
| `agent-memory-start.ps1` | Tiered compiled memory (T1/T2/T3) | Every prompt start |
| `agent-memory-finish.ps1` | Append session/revert, recompile | Every prompt end |
| `search-memory.ps1` | Search across memory files | Finding specific context |
| `memory-health.ps1` | Validate memory system format/staleness | Periodic health check |
| `process-meeting.ps1` | Transcribe and extract meeting notes | After new video recordings |
| `build-confluence-wiki.ps1` | Generate wiki outbox | After memory updates |
| `build-dashboard-snapshot.ps1` | Generate runtime snapshot | After dashboard changes |
| `build-e2e-progress-report.ps1` | Full E2E report + web page | After progress/KPI updates |
| `build-progress-visualizations.ps1` | Mermaid/HTML progress viz | After progress updates |
| `build-exp001-evaluation.ps1` | EXP-001 mechanism eval | After label changes |
| `build-exp002-labeling-package.ps1` | EXP-002 labeling package | After label changes |
| `build-exp003-error-analysis.ps1` | EXP-003 accuracy analysis | After real labels |
| `build-exp005-label-review.ps1` | EXP-005 label gate | After labeling |
| `build-policy-sensitivity-simulation.ps1` | EXP-004 policy screening | After real labels |
| `check_evidence_consistency.py` | Evidence invariant guard | Before claims/reviews |
| `dashboard-health.ps1` | Dashboard/wiki health | After outbox builds |
| `research-health.ps1` | Research infrastructure | After repo changes |
| `project-health.ps1` | Overall project health | After any changes |
| `run-codex-next-step.ps1` | Supervised continuation | "Continue" prompts |
| `run-project-review.ps1` | Structured review | Review prompts |
| `open-vego-workbench.ps1` | One-command local review | Daily review |
| `export-topology-report.ps1` | HTML/PDF topology export | Documentation |
| `export-baseline-overlay-report.ps1` | Baseline overlay export | Documentation |
| `refresh-tracking.ps1` | Progress tracker refresh | After progress changes |
| `download-hitl-resources.ps1` | HITL resource download | Literature needs |
| `new-experiment.ps1` | Experiment scaffold | New experiments |
| `feedback_generalizer.py` | Offline eligibility, grouping, conflict, and S7 synthesis-request package; never applies rules | Proposal-only Vector 1 work after feedback changes |
| `hlayer_prototype/hlayer-prototype-scaffold.py` | Isolated offline supervisor interaction demo with non-trusted outputs | July 15 demo preflight/session using a temporary output directory |
| `validate_hlayer_program.py` | End-to-end replay/conformance/decision/demo/protected-boundary validation | Before H-layer status claims or supervisor demos |
| `validate_hlayer_offline.py` | EXP-013–018 contract/conformance validation | After offline contract or fixture changes |
| `build_iris_zoom_disposition_ledger.py` | Deterministic S-0001–S-1195 preliminary CSV/JSON builder | Before bilingual review imports; `--check` proves tracked machine projection is current |
| `build_iris_zoom_adjudicated_ledger.py` | Fail-closed merger for two complete independent reviewer returns, full-media evidence, and third-person disagreement adjudication | `--check` validates a pending or completed interface without writing; no adjudicated output exists at 0/1,195 |
| `validate_iris_requirements_closure.py` | IRIS-EXP-01..10 validator with fail-closed `structure`, `readiness`, and `closure` modes | Before/after supervisor-package changes; readiness/closure must remain non-zero while required human/external evidence is absent; `--refresh` writes ignored diagnostics |
| `iris-authorized-submission-receipt-v1.schema.json` | Exact authorized submission, package, receipt, authorization, and certificate-binding contract | Closure only; the tracked pending template is `NOT_SUBMITTED` and never counts as evidence |

## Dashboards & Visualizations

| Resource | Location | Type |
| --- | --- | --- |
| Progress dashboard | `docs/dashboards/progress-dashboard.md` | Tracked |
| KPI register | `docs/dashboards/kpi-register.md` | Tracked |
| Results dashboard | `docs/dashboards/results-dashboard.md` | Tracked |
| Progress visualizations | `docs/dashboards/progress-visualizations.generated.md` | Generated |
| E2E dashboard | `docs/dashboards/e2e-dashboard.generated.md` | Generated |
| Status snapshot | `docs/dashboards/status-snapshot.generated.md` | Generated |
| Local results dashboard | `VEGO-AI/reports/results_dashboard/` | Generated |
| Confluence outbox | `docs/confluence/outbox/` | Generated |

## Agent Use Rules

- For HITL, human feedback, expert labeling, XAI, governance, or thesis-literature prompts, read this file first, then inspect `literature/hitl-resource-pack/`.
- For supervisor meeting context, read `docs/agent-memory/meeting-notes/2026-07-03-supervisor-meeting.md`.
- Use the resource pack to improve research framing and evaluation design.
- Do not treat downloaded resources or synthetic results as VEGO-AI accuracy evidence.
- Do not install Label Studio, Argilla, modAL, cleanlab, or any other tool unless the user explicitly asks for installation.
- Do not wire active learning, label quality tools, embeddings, LLM/API calls, Agent 4 changes, M4B-2, or baseline-output changes from these resources without a separate approved plan.
- Keep downloaded PDFs/docs ignored; tracked docs should use citations, summaries, links, and hashes only.

## Practical Current Decision

The immediate empirical-evaluation bottleneck remains real EXP-005 expert labels, not tooling. The framework track is separately gated by M-02 through M-05 and explicit implementation authorization. Current demo feedback is not trusted input, and the offline generalizer must report `BLOCKED_NO_VERIFIED_FEEDBACK` rather than inventing candidate rules. Use the resource pack to support supervisor discussion and thesis writing. Revisit Label Studio or Argilla only if the CSV workflow becomes too slow or the label set expands beyond the current safe candidates.

## Alignment Control Links

- Current implementation/evidence checkpoint: `docs/operations/alignment-control.md`
- Thesis contribution structure: `docs/research/thesis-structure-map.md`
- PhD thesis optimization control page: `docs/research/phd-thesis-optimization-plan.md`
- Claude PhD thesis collaboration prompt: `docs/agent-memory/claude-phd-thesis-collaboration-prompt.md`
- Supervisor meeting notes: `docs/agent-memory/meeting-notes/2026-07-03-supervisor-meeting.md`

Use these with the HITL resource pack when writing thesis text or planning evaluation. The resource pack can justify method choices and terminology, but it does not change the EXP-005 evidence gate.
