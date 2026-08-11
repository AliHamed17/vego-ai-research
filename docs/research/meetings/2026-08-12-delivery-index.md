# Aug-12 Supervisor Delivery Index

Status: **presentation-ready package for the 2026-08-12 supervisor meeting — not supervisor-approved.**
Research-question wording remains provisional pending `D-RQ-01`/`D-RQ-02`.

Prepared for Prof. Iris Reinhartz-Berger and Prof. Arnon Sturm. Everything derives from the tracked,
machine-derived 2026-08-05 meeting record. Claim discipline throughout: EXP-005 = 0 supplied labels
(27 blind rows, 24 generalization-safe; gate needs ≥20); medical readiness 0/6; no verbatim transcript
quotation; reconstructed wording.

## 1. Two folders, two audiences

Published by [`scripts/publish-supervisor-package.ps1`](../../../scripts/publish-supervisor-package.ps1)
to both the Obsidian vault and Google Drive:

```
VEGO-AI PhD\
├── 2026-08-12 Supervisor Package\      ← SHARE THIS ONE (Viewer) with Iris and Arnon
└── _Ali private (do not share)\        ← presenter notes and rebuttal prep; keep unshared
```

The split is deliberate. The private folder holds the presenter walkthrough script, the
anticipated-Q&A rebuttal prep, the unreviewed machine transcript, the internal master plan, the work
report, and this index — material that is either Ali's own preparation or not fit for supervisor
consumption. The shared folder is rebuilt from scratch on every publish run, so a file removed here
does not linger in a folder that may already be shared.

## 2. The shared folder — supervisor-facing, numbered in presentation order

| # | Published name | Format | Purpose | Traces to |
| --- | --- | --- | --- | --- |
| 00 | README - Start Here | PDF + Word | What is in the folder, where things stand, what is being asked at the meeting | — |
| 01 | Executive Brief (EN + HE) | PDF + Word | The whole picture in about a minute, bilingual | — |
| 02 | Chapter 3 - Gap and Research Questions | Word + PDF | **The written chapter deliverable** | `A08-02` |
| 03 | Literature Review - Per Research Question | Excel (4 sheets) | **The per-question literature spreadsheet**: README, Inventory, Coverage Gaps, Search Protocol | `A08-03` |
| 04 | Progress Presentation | PowerPoint + PDF | The live 13-slide progress deck | `A08-08` |
| 05 | Requirements and Progress Tracking | Excel (7 sheets) | **Every requirement, action, and open question from both calls, with status — plus the ten decisions requested.** Sheets: README, Requirements (R-01..R-19), Actions (A-01..A-15), Open Questions (Q-01..Q-10), Aug-5 Directives (E1..E15), Aug-5 Actions (A08-01..09), Decisions Requested (D-RQ-01..10) | `A08-06` + the full 44-control register |

Deliberately **not** in the shared folder: Markdown source files (supervisors get Word/Excel/PDF),
integrity-hash manifests, the machine transcript, and Ali's presenter/rebuttal material.

## 3. Provenance of file 05

Rows in the Requirements and Progress Tracking workbook are extracted **programmatically** from the
tracked records — 44 controls from
[`master-traceability-register.md`](../phd-proposal/master-traceability-register.md) and 15 directives
plus 9 actions from [`2026-08-05-supervisor-meeting.md`](2026-08-05-supervisor-meeting.md) — not
retyped. Status wording is quoted from those sources unchanged; no status is upgraded, softened, or
invented in the workbook. Colour coding is derived from the quoted status text (green = complete or
verified, amber = working/partial/pending, red = open/blocked/not started).

## 4. Regenerating and republishing

```powershell
# rebuild the two Excel workbooks and the Word/PDF renders first (see the session scratchpad
# builders), then publish both folders to the vault and Drive:
.\scripts\publish-supervisor-package.ps1 -DriveRoot "G:\My Drive"
```

## 5. Actions only Ali can do

1. **Share the `2026-08-12 Supervisor Package` folder** with Iris and Arnon (Viewer) — right-click in
   `G:\My Drive\VEGO-AI PhD\`, or via drive.google.com. Do **not** share the parent folder or the
   private folder.
2. **Verify the final RQ/SQ wording** against the saved AI-assistant chat from the 5 Aug call (or
   re-listen to `00:13:07–00:44:37`) — blocks Chapter-3 sign-off (`A08-01`, `D-RQ-01`/`D-RQ-02`).
3. **Check the inbox** for Iris's check-in email (`A08-07`) and reply with real status.
4. Replicate the literature RQ-tag column into the native Google Sheet, if the Sheet remains the
   working copy of record.
5. Paste the Chapter-3 content into the Word proposal document.
6. One dry run of the presentation.

*The AI environment has no Google Drive sharing, Gmail, or Obsidian connector with write authority over
sharing permissions, so items 1 and 3 are manual by necessity — the files themselves are already in
place.*
