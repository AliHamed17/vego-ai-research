# Literature Review v16 + Workbook v11 — Workbook v12 Repair Follow-up

**Date:** 2026-08-20  
**Scope:** Direct repair of Ali's external workbook `VEGO-AI_Literature_Workbook_RQ_Only_Organized_v11_GitHub_Aligned.xlsx`.  
**Output:** `VEGO-AI_Literature_Workbook_RQ_Only_Organized_v12_Audit_Fixed.xlsx` (external `/mnt/data` artifact; not committed to this repository).

This follow-up resolves workbook-side findings from `literature-review-v16-workbook-v11-verification-report.md`. It does **not** modify Literature Review v16 PDF; the paired PDF remains a separate controlled artifact and must be re-audited after its own enhancement pass.

## Editing method

- Confirmed the workbook is an external, hand-maintained `.xlsx` file with four sheets (`RQ`, `RQ1`, `RQ2`, `RQ3`).
- Searched the repository for a generator/build script for this workbook; none was found.
- Edited the actual `.xlsx` directly with `artifact_tool` while preserving the four-sheet structure, formulas, merged sections, colors, and evidence-table conventions.
- Preserved the current exact provisional RQ rows and the separate v15 candidate wording rows.

## Resolved since the v16/v11 audit

### 1. G6 was silently absent — resolved

G6 is now present in:

- `RQ` gap table, as the umbrella construct-risk row;
- `RQ2` gap table, matching the PDF's operational ownership of G2 + G3 + G6.

Definition retained:

> Construct validity of substantial versus occasional variability.

Boundary and limitation retained:

> The current VEGO-AI terminology classifies validity rather than frequency, while “occasional” conventionally suggests rarity; independent labels and cross-context validation are absent. The conceptual distinction between intentional/valid variation and error is not wholly new.

Falsifier retained:

> Reliable evidence that the terminology and rubric are independently understood and produce stable judgments across languages, domains, and experts.

Workbook classification is explicit: **Construct risk / open decision**, not an automatically validated external literature gap. The proposed handling is a validity × recurrence coding rubric with origin, evidence-strength, ambiguity, and action fields; it is not presented as a second RQ2 thesis artifact.

### 2. FT-A / FT-B inconsistencies — re-derived and resolved on the workbook side

Evidence maturity was re-derived from actual source/access maturity rather than copied from either prior artifact.

| Source | Workbook v12 status | Basis |
| --- | --- | --- |
| Bansal et al. (2021) | FT-A | Author-hosted full CHI paper available and used for bounded results/discussion claims. |
| Kulesza et al. (2015) | FT-A | Full accepted-author manuscript available; bounded method/finding claims can be located. |
| Aamodt & Plaza (1994), RQ2 and RQ3 | FT-A | Full author-hosted paper available; the same label is now used consistently in both sheets. |
| Hu et al. / NIST SP 800-162 | FT-A | Official full NIST publication available. |
| Schünemann et al. (2017) | FT-A | Full article available; bounded adaptation-framework claims are locatable. |

The workbook therefore retains Bansal as FT-A and changes Kulesza, Aamodt & Plaza, NIST ABAC, and Schünemann to FT-A. The paired PDF may still disagree until its separate repair pass is complete.

### 3. Raykar anchor mismatch — resolved without assuming a PDF edit

Raykar et al. (2010) was removed from the five-source RQ2 anchor set because the current paired PDF v16 does not contain or resolve it. Aroyo & Welty (2015), which is present in the paired literature review, was restored as the disagreement-as-evidence anchor.

This change is recorded in the RQ2 `Anchor-set revision` row. It does **not** claim that formal multi-reviewer reliability is solved; that remains a supporting-literature and formal-search need.

### 4. EXP-008 arithmetic — resolved

The workbook now states:

> 33 / 26 = 1.269 (approximately 1.27)

instead of 1.35.

The same arithmetic error was corrected in `docs/research/phd-proposal/chapter-5-preliminary-results.md` in commit `f368bbf54e6fe6cb16115ce74bd64f6f75649370`.

### 5. RES-2 and RES-3 source attribution — resolved

The workbook now cites the files that actually state the resourcing facts:

- `docs/research/phd-proposal/chapter-4-research-methodology.md`;
- `docs/agent-memory/decisions.md` (2026-08-18 entry).

`RES-2` now attributes the unnamed independent Study-2 implementer to Chapter 4 §4.4 and the decisions entry. `RES-3` now attributes the unnamed two Study-3 raters to Chapter 4 §4.5/§4.7 and the decisions entry. The unrelated Chapter 4 decisions packet is no longer used for those two facts.

### 6. Unverifiable priority scores — resolved

The column is now named **Editorial priority**, not `Priority score`. Numeric pseudo-scores were removed and replaced with:

- Highest;
- Very high;
- High;
- Medium;
- Supporting.

The rubric now states that no weighted score is computed. Rank 1 is the most important source for the RQ based on an editorial synthesis of relevance, novelty-defense value, methodological centrality, evidence authority, and current agentic relevance.

### 7. ACL disposition and readiness-score overstatement — workbook side narrowed

The workbook no longer asserts that ACL-116 disposition is final or that 106/116 and the 49/36/21 split are certified. It now states that disposition remains provisional and requires second review.

The workbook continues to assert **no global readiness score**. It explicitly does not adopt the paired PDF v16 self-score pending the separate PDF-side correction. This resolves the workbook-side half of ISS-036; the PDF-side 76/100 and final ACL count remain open.

## Validation performed

- Four sheets preserved: `RQ`, `RQ1`, `RQ2`, `RQ3`.
- Formula scan: no `#REF!`, `#DIV/0!`, `#VALUE!`, `#NAME?`, or `#N/A` errors.
- Core-anchor count: 5 per RQ.
- RQ2 evidence count after repair: 4 FT-A / 1 FT-B.
- RQ3 evidence count after repair: 5 FT-A / 0 FT-B.
- Aamodt & Plaza maturity is identical across RQ2 and RQ3.
- G6 is present and consistently defined in RQ and RQ2.
- EXP-008 arithmetic was recomputed independently.
- RES-2/RES-3 replacement source files were opened and checked against the claims.
- All four sheets were rendered and visually inspected; shifted merged rows and control-note rows were repaired after the first render.
- Exported workbook was re-imported successfully.

## Remaining open items / assumptions

1. **The PDF was not changed in this task.** Workbook v12 may remain cross-artifact inconsistent until the paired PDF repair is completed and re-audited.
2. **PDF scorecard remains open.** The workbook rejects a global readiness score; the PDF-side 76/100 must be removed, reworked, or independently justified in the PDF task.
3. **PDF bibliography remains open.** This workbook repair does not add Raykar or any other citation to the PDF; the anchor was changed instead to avoid assuming a future PDF edit.
4. **Formal searches remain 0/5.** No source ranking, G6 placement, or maturity correction changes that evidence gate.
5. **PR #20 / ISS-038 remains open.** This workbook task does not merge the literature awesome-index PR or change `main`'s current `literature/README.md`.
6. **Generated presentation scripts may still contain the old 1.35 caption.** Chapter 5 and the workbook are corrected; any generated course-presentation figure should be rebuilt only after its script/caption is checked separately.

## Release state

**Workbook v12 is repaired as a supervisor briefing artifact, but the literature package is still NOT DOCTORAL-READY.** Formal search, full-text completion, second/human review, supervisor decisions, EXP-005, PDF-side reconciliation, and medical gates remain open.
