# Standing Verifier Checklist and Governance Plan

**Role established 2026-08-12.** Claude acts as adviser, orchestrator and verifier across the whole
estate: Drive, Obsidian, GitHub, mail, and the research record itself. This file defines *what I check,
how often, and what I report* — so verification is repeatable rather than ad hoc.

**Reporting rule (Ali's instruction).** I report immediately and unprompted whenever I find: a missing
or stale file, a broken link, a document that is wrong or not research-relevant, an unsupported claim,
or a sync divergence. I never report an item as verified unless I inspected it directly.

---

## Part 1 — The checklist

### A. Every session that touches deliverables

| # | Check | Command / method | Pass condition |
| --- | --- | --- | --- |
| A1 | Drive publish actually landed | `scripts/publish-and-verify-drive.ps1` | every file `OK`; **never** a bare `Copy-Item` into `G:\` |
| A2 | Re-verify after settle (Drive can revert) | re-compare sizes 20–60 s later | all `HOLDING` |
| A3 | Canonical folder ≠ stale | size/hash compare topic folders vs `outputs/` | identical |
| A4 | Claim-boundary scan | regex for accuracy/generalization/clinical/effort claims | zero hits |
| A5 | Evidence guard | `python scripts/check_evidence_consistency.py` | 18/18 PASS |
| A6 | No fabricated citation | every source traceable to a named origin file | 100 % traceable |
| A7 | Repo protected paths | `scripts/check_hlayer_protected_paths.py` + `git status -- VEGO-AI` | PASS / empty |

### B. Weekly (before each supervisor meeting)

| # | Check | Pass condition |
| --- | --- | --- |
| B1 | Every meeting requirement mapped to a deliverable with evidence | no unmapped requirement |
| B2 | Package folder complete, numbered, and byte-verified | matches the index |
| B3 | Tracking document reflects reality on the day | no "done" that is not done |
| B4 | Evidence gates restated with current counts | EXP-005, medical gates, searches |
| B5 | Open decisions listed with owner | each has an owner and a blocking note |
| B6 | Uncommitted work committed and pushed | `git status` clean, 0 unpushed |
| B7 | Wording provisional-ness stated wherever RQs appear | no artifact implies approval |

### C. Monthly (estate health)

| # | Check | Pass condition |
| --- | --- | --- |
| C1 | Full Drive tree inventory + stale-file sweep | no file older than its repo source |
| C2 | Obsidian links resolve; no dangling junctions | all resolve |
| C3 | Branch divergence review | no branch >50 commits behind without a plan |
| C4 | Stale PR review | none open >14 days without a decision |
| C5 | Unrelated/incorrect documents in research folders | none |
| C6 | Data-boundary audit (no patient data, no secrets) | clean |
| C7 | Backup reality check: does anything exist only on one disk? | nothing |

### D. Continuous red flags — I report these the moment I see them

- A claim of accuracy, generalization, clinical performance or effort reduction anywhere.
- A citation I cannot trace to a verified origin.
- A "completed literature review" implication while `QL-01…QL-05` are unrun.
- A supervisor wording presented as approved before `D-RQ-01`/`D-RQ-02` are logged.
- A file on Drive older than the repo source it came from.
- Patient data, credentials, tokens or secrets anywhere in the repo or the general Drive.
- A document in a research folder that is not research (or is factually wrong).

---

## Part 2 — Open items and the plan to close them

Ordered by urgency. **Owner "Ali"** means it cannot be done by anyone else.

### Immediate — before/at today's meeting (2026-08-12)

| # | Item | Owner | Action |
| --- | --- | --- | --- |
| P1 | **Verify the RQ wording** (`A08-01`) | **Ali** | Open the saved working draft from the Aug-5 call. Settle: *exploration* vs *identification/classification*; *human* vs *expert* judgment. This blocks Chapter 3 sign-off |
| P2 | **Confirm the Drive is shared** with Iris and Arnon (`A08-05`) | **Ali** | Check the share dialog on `VEGO-AI PhD Working 2026`; grant comment/edit. I cannot see ACLs |
| P3 | Open the package from Drive once before presenting | **Ali** | Confirms the correct (52,922 B) Chapter 3 renders — belt and braces after the revert incident |
| P4 | Capture decisions during the meeting | **Ali** | Use the post-meeting capture table in the walkthrough doc; 8 decisions are queued |

### This week

| # | Item | Owner | Action |
| --- | --- | --- | --- |
| P5 | **Commit and push the 13 uncommitted files** (G-01) | Claude + Ali | The whole Aug-12 package exists only on local disk. Commit to a branch and PR |
| P6 | Resolve the two literature spreadsheets (D-04) | Claude | Retire or clearly mark the 07-30 `.gsheet` as superseded so Iris has one authoritative file |
| P7 | Decide on PR #14 (G-02) | Ali | Merge or close — 2.5 weeks stale |
| P8 | Apply the supervisors' wording ruling | Claude | One find-replace pass across every artifact, then re-verify and re-publish |

### Decisions I need from you (not urgent, but they shape everything)

| # | Question | Why it matters |
| --- | --- | --- |
| Q1 | **Should the Obsidian vault stay in the Parallel Wireless OneDrive?** (O-01) | Your PhD is personal work; the vault currently lives in your employer's tenant. Moving it to a personal location (or straight onto `G:\`) removes an IP/ownership question before the proposal is submitted |
| Q2 | **Do you want an academic/personal mailbox connected?** (M-01) | Right now the only mail I can see is your work Outlook. I cannot verify anything about Iris's or Arnon's correspondence — including her check-in email — and I will keep marking those `NEEDS ALI` until this changes |
| Q3 | Do the divergent `agent/*` branches still matter? (G-03) | 172 and 184 commits ahead. Either they get merged soon or they should be archived — the merge cost grows every week |
| Q4 | Should `_Ali private` `.md` files become `.docx`? (D-05) | Google Drive cannot preview `.md`. Fine if they are for you only |

### Longer arc — to proposal submission

| Phase | Window | Gate |
| --- | --- | --- |
| Wording locked | after 2026-08-12 | `D-RQ-01`/`D-RQ-02` logged |
| Literature searches executed | after wording lock | `QL-01…QL-05` run, screened, appraised |
| §2 written | after searches | structure chosen (`D-CH2-01`) |
| §4 written | after artifact decision | `D-ART-01` settled |
| Expert labels collected | ongoing, blocking | ≥20 generalization-safe (currently **0 of 24**) |
| Plan A vs Plan B decision | **2026-08-26** internal checkpoint | medical gates all six, or fall back to Plan B |
| Proposal submission | Sept–Oct target | supervisor approval + university process verified |

---

## Part 3 — How I will report to you

Every time I do work I will give you:

1. **What I verified** — with the actual evidence (byte counts, exit codes, hashes), never "looks fine".
2. **What I found wrong** — flagged by severity, with the fix applied or the reason it needs you.
3. **What I could not verify** — stated explicitly rather than assumed (mail, Drive ACLs, cloud state).
4. **What needs you** — a short list, each item saying exactly why nobody else can do it.

I will not mark anything done that is not done, and I will not present a draft as approved.
