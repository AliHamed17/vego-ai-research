# Estate Audit — 2026-08-12

**Auditor:** Claude (standing adviser / orchestrator / verifier role, established 2026-08-12)
**Scope:** Google Drive, GitHub, Obsidian, mail/identity, and the research deliverables against Iris's 2026-08-05 requirements.
**Method:** direct inspection — byte-level hash and size comparison, git state, filesystem link resolution. No status was taken on trust.

---

## 0. Headline

**One critical failure was found and fixed during this audit.** Google Drive for Desktop had silently
reverted **10 of the 16** files in the 2026-08-12 supervisor package to older cloud versions — including
**Chapter 3** (the meeting's deliverable) and the **literature workbook**. Had the meeting proceeded
without this check, the supervisors would have been shown the previous, uncited Chapter 3 and the old
8-source spreadsheet.

Root cause: a plain copy into `G:\` loses to Google Drive's conflict resolution when a file of the same
name already exists in the cloud — the cloud copy wins and the newer local file is discarded. Files with
*new* names (06, 07, 08) survived; every file that already existed was reverted.

**Fixed:** all files re-published through a new delete-then-copy-then-verify routine
(`scripts/publish-and-verify-drive.ps1`) and confirmed byte-identical after a settle delay.

---

## 1. Google Drive

### 1.1 Structure — healthy

Nine-folder canonical structure present and populated: `00_Admin_and_Decisions` (19 files),
`01_Research_Questions` (10), `02_PhD_Proposal` (12→18), `03_Literature_Review` (12),
`04_SE_Modeling_Studies` (14), `05_Medical_Feasibility_Gated` (19), `06_Weekly_Meetings` (32),
`07_Submission_Package` (2, intentionally near-empty), `99_Archive` (2), plus
`_Ali private (do not share)` (6).

### 1.2 Findings

| ID | Sev | Finding | State |
| --- | --- | --- | --- |
| D-01 | **CRITICAL** | Drive reverted 10/16 package files to older cloud versions — incl. Chapter 3 (44,643 B old vs 52,922 B correct) and the literature workbook (12,536 B old vs 27,023 B correct) | **FIXED + verified** |
| D-02 | **HIGH** | Canonical topic folders held stale copies: `02_PhD_Proposal` had the 08-10 Chapter 3; `03_Literature_Review` had the 8-source workbook; `00_Admin` had an old tracker | **FIXED + verified** |
| D-03 | **HIGH** | **Proposal v0.3 was entirely absent** from `02_PhD_Proposal` — only v0.1 and v0.2 were there, so the canonical proposal folder did not contain the current proposal | **FIXED** (published as *Proposal v0.3 (current)*) |
| D-04 | MEDIUM | Two literature spreadsheets now coexist: the native `VEGO-AI PhD Literature Workbook v0.1.gsheet` (untouched since 07-30) and the new `.xlsx`. Ambiguous which is authoritative for Iris | **OPEN** — see plan A2 |
| D-05 | MEDIUM | `_Ali private (do not share)` holds `.md` files, which Google Drive cannot preview. If they matter, they should be `.docx`/`.pdf`; if internal-only, they are fine as-is | **OPEN** — low urgency |
| D-06 | INFO | `07_Submission_Package` is empty except its overview — this is **correct by design** (stays empty until a submission candidate is approved) | No action |
| D-07 | **UNVERIFIABLE** | Whether the Drive is actually **shared** with Iris and Arnon (`A08-05`) cannot be determined from the filesystem — sharing lives in Drive's ACL | **NEEDS ALI** |

---

## 2. GitHub

| ID | Sev | Finding | State |
| --- | --- | --- | --- |
| G-01 | **HIGH** | **13 uncommitted files** on `main` — the entire Aug-12 package work (Chapter 3, workbooks, builders, audit) exists only on local disk. A disk failure loses it | **OPEN** |
| G-02 | MEDIUM | PR **#14** open since 2026-07-26 (~2.5 weeks) — "Publish BigUI experiment evaluation…" | **OPEN** — decide merge or close |
| G-03 | MEDIUM | Two branches severely divergent: `agent/bigui-experiment-platform` (ahead 172 / behind 41) and `agent/independent-evidence-evaluation` (ahead 184 / behind 14). The longer they diverge the harder the merge | **OPEN** |
| G-04 | LOW | Local-only branches never pushed: `docs/iris-july29-phd-execution`, `feature/human-feedback-manager`, `feature/m4a-test-compat` — unbacked-up work | **OPEN** |
| G-05 | INFO | `main` is level with origin (0 unpushed commits); PR #9 (July-01 redirect package) is no longer open — merged or closed | No action |

---

## 3. Obsidian

| ID | Sev | Finding | State |
| --- | --- | --- | --- |
| O-01 | **MEDIUM–HIGH** | The vault lives at `C:\Users\ahamed\OneDrive - Parallel Wireless\Documents\Obsidian Vault` — inside the **employer's corporate OneDrive tenant**. Anything created directly in the vault syncs to Parallel Wireless. Note: the research content itself is reached through a junction to `G:\`, and OneDrive does not follow junctions, so the *research files* are very likely not uploading — but the vault, its config, and any note authored in place are in the corporate tenant. For a personal PhD this is an IP/ownership question worth settling deliberately | **OPEN — decision needed** |
| O-02 | LOW | A `VEGO-AI PhD` entry appeared in one enumeration but no longer resolves (`File Not Found`) — a stale/dangling link from an earlier layout | **OPEN** — remove reference |
| O-03 | LOW | Junk files in vault root: `Untitled.canvas`, `Untitled 1.canvas` (2 bytes each) | **OPEN** — delete |
| O-04 | INFO | The live junction `VEGO-AI PhD Working 2026` → Drive folder **works correctly** (12 files visible on both sides) — this is a good setup | No action |

---

## 4. Mail and identity

| ID | Sev | Finding | State |
| --- | --- | --- | --- |
| M-01 | **HIGH (capability gap)** | The only connected mail account is **`ahamed@parallelwireless.com`** (Microsoft 365, "Engineer I, QA"). **There is no Gmail/academic mail connected.** I therefore *cannot* see or verify correspondence with Iris and Arnon — including her check-in email (`A08-07`) | **OPEN — needs a decision** |
| M-02 | MEDIUM | Consequence: I cannot verify whether Iris's email arrived, nor whether the Drive share notification was sent. These stay `NEEDS ALI` in every report until an academic mailbox is connected | **OPEN** |
| M-03 | NOTE | Using a corporate mailbox for PhD supervision correspondence carries the same IP/retention question as O-01 | **OPEN** |

---

## 5. Research deliverables vs Iris's 2026-08-05 requirements

| Req | What Iris asked | Verdict | Evidence |
| --- | --- | --- | --- |
| `E15`.1 | Gap + RQ chapter **in full** | **DONE** | ~5,200 words, 66 citation markers, on Drive verified at 52,922 B |
| `E15`.2 | Per-RQ literature spreadsheet with RQ tag column | **DONE** | 40 verified sources, 4 sheets, coverage-gap analysis; 27,023 B verified |
| `E15`.3 | *Think about* §2 and §4, do **not** start | **DONE (correctly not started)** | 4 §2 options, 9 §4 options, 14 questions; no design committed |
| `E15`.4 | Share the Drive with Iris and Arnon | **NOT VERIFIABLE — NEEDS ALI** | ACL not inspectable from disk |
| `E15`.5 | Word proposal + separate tracking doc | **DONE** | v0.3 `.docx` + 6-sheet tracker, both on Drive |
| `E15`.6 | Reply to her check-in email | **NEEDS ALI** | No mail visibility (M-01) |
| `E15`.7 | Present live on Aug 12 | **READY** | 10-slide deck + walkthrough + Q&A |
| `A08-01` | Verify final RQ wording vs saved draft | **BLOCKING — NEEDS ALI** | Two discrepancies surfaced: `E6` *exploration* vs *identification/classification*; `E8` *human* vs *expert* judgment |
| `E5`,`E6`,`E7`,`E8`,`E9`,`E10`,`E12`,`E13` | Wording/structure corrections | **APPLIED** | Each traced in the tracking workbook |
| `E14` | 3-month blocks, 3-year horizon | **NOT STARTED (correct)** | Belongs to the Plan chapter, not this cycle |

---

## 6. Standing evidence gates — unchanged

| Gate | Value | Blocks |
| --- | --- | --- |
| EXP-005 generalization-safe expert labels | **0 of 24** (≥20 needed) | every quantitative accuracy claim |
| Medical entry gates G1–G6 | **0 of 6** | any medical data processing |
| Literature searches QL-01…QL-05 | **not run** | any novelty/completeness statement |
| Accuracy / generalization / clinical claims | **none made** | — verified by automated guard, 18/18 PASS |

---

## 7. What I could NOT verify (stated honestly)

1. **Drive sharing status** — requires the Drive UI or API; not inspectable from the filesystem.
2. **Any email** — no academic mailbox connected (M-01).
3. **Whether the supervisors have opened anything** — no telemetry, by design.
4. **The exact agreed RQ wording** — only Ali's saved working draft can settle it (`A08-01`).
5. **Cloud-side Drive state** beyond what the local client exposes; the client is the only window, and
   D-01 proves it can disagree with the cloud.

---

*Audit performed 2026-08-12. Every "FIXED" above was re-verified by byte comparison after a settle
delay. Every "OPEN" item appears in the plan with an owner.*
