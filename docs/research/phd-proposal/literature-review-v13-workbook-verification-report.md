# Literature Review v13 + Evidence Workbook v5 — Verification Report

**Reviewed:** `VEGO_AI_Literature_Review_v13_45_Page_Visual_Repaired_2026-08-19.docx` (409 paragraphs, 31 tables, 16 sections + 2 appendices + references) and `VEGO-AI_Literature_Workbook_Consolidated_Strict_v5_RQ_Sheets.xlsx` (22 sheets).

**Method:** Full-text extraction of both files (docx to a paragraph/table dump, xlsx to per-sheet CSV), then a 7-dimension automated review with independent adversarial verification of each finding against the exact cited source, followed by direct spot-checks I ran myself on the highest-stakes claims (all confirmed). This supersedes `literature-review-v10-verification-report.md` as the current verification record for this document lineage.

**One honest limitation up front:** this dump captures paragraph and table text in reading order. It does not capture running page headers/footers, so the v10 report's specific "Page 1 of 41" header bug cannot be confirmed fixed or unfixed from this artifact alone — check that directly in the rendered file. Embedded figure/chart *images* were not visually inspected; only captions and source notes were reviewed.

## Executive summary

Real, cited progress since v10: the review now runs to 16 substantive sections plus two appendices, adds an explicit falsifier and disconfirming-result to every gap and RQ, keeps a genuinely candid self-critique section, and — most importantly — the underlying workbook is scrupulous about never letting exploratory AI-assisted searches count as the formally frozen QL-01–QL-05 protocol. That discipline is exactly right and should not change.

But the single most important number in the document — **"Current readiness score: 84/100"**, repeated as the hostile-review scorecard's headline "Overall" — directly contradicts the companion workbook's own computed score for the same dimensions: **`Overall literature readiness: 36`**, with an explicit **`Release Decision: NOT DOCTORAL-READY`** and a stated reason (`QL-01–QL-05 remain 0/5; EXP-005 is 0/24; medical readiness is 0/6; RQs are provisional`). I verified both numbers directly against the source files myself. Part of the explanation is structural, not malicious: the workbook's own Provenance sheet still records itself as rebased to **v10**, not v13 — the two artifacts describing "this project's literature review" are currently two different, unreconciled versions. That explains the drift; it doesn't resolve it, and the docx's own internal scorecard (Table 29) uses the identical dimension names as the workbook (`Search rigor`, `Gap defensibility`) without ever mentioning the workbook's very different values for those same names.

Second headline issue: this week's actual assignment from Iris — work through the ACL-2026 GitHub taxonomy corpus and classify its branches as relevant / less relevant / not relevant / missing, producing one slide — was not done. v13 instead ran nine broader search families across ACL/ACM/AAAI/PMLR/PubMed/ScienceDirect and the open web, which is the *broader* search Iris explicitly deferred to after the proposal stage.

## What was done well (verified strengths)

These are specific, cited, and should be preserved as-is in future revisions — not generic praise.

1. **Formal-vs-exploratory search status is never blurred.** `Search_Registry.csv` keeps QL-01–QL-05 marked `PLANNED — NOT EXECUTED` / `Counts as Formal Execution? No`, and separately logs the nine new AI-assisted queries (SQL-01–SQL-09) as `EXECUTED — EXPLORATORY ONLY` with `not a database-systematic execution and not counted toward QL completion`. Even though those exploratory searches turned up real, usable literature, the workbook refuses to let them inflate the formal-search count.
2. **Four-tier evidence maturity, not binary cited/not-cited.** Beyond FT-A/FT-B, the workbook operationalizes AB-S (abstract-only) and ID-S (identity-verified, not yet extracted), with the explicit policy: *"Blank or controlled 'not extracted' values are deliberate: methods, samples, and limitations are never inferred when the evidence has not been reviewed."*
3. **A candidate gap was honestly demoted, not inflated.** G6 ("substantial vs. occasional variability") is explicitly marked `Category: Construct Risk` (not `Research Gap` like G1–G5), `v4 Decision: Reclassified`, with the note *"not yet a defensible external literature gap."*
4. **The review names the specific counter-example that would zero out its own contribution.** For G4, the workbook's own "Notes" column calls out "ordinary CBR plus standard authorization metadata" as *"the strongest novelty threat"* — written down as a pre-specified defeat condition, not left for a future critic to discover.
5. **Every gap and RQ carries a falsifier or disconfirming result**, not just supporting rationale (Tables 7 and 8) — e.g., G1's falsifier is "a validated prior system that jointly implements those decision variables... and evaluates burden, coverage, and downstream reuse."
6. **The primary source's weakest result is reported as the weakest result.** The uncovered-fragment audit's 0.55 score is stated plainly, immediately followed by *"Values redrawn from Table 3 of the supplied manuscript... This is not an independent re-analysis."*
7. **A template artifact in the primary manuscript was caught, not laundered into a false citation.** The review noticed the supplied VEGO-AI PDF "retains generic author and affiliation fields, WOODSTOCK template text, and placeholder DOI material" and deliberately declined to assert a final DOI or pagination.
8. **The hostile-review scorecard is differentiated, not a flattering blanket score** — `Search rigor` and `Reproducibility` are explicitly its two lowest self-assigned scores (7/10 each), each annotated with the specific open item.
9. **Weak/uncovered literature streams stay visible in `Coverage_Matrix.csv`** (e.g. "Adjustable autonomy," "Joint / distributed cognition" both marked `Uncovered`, `Discovered/Included: 0`) rather than being smoothed over.
10. **Five distinct evaluation-leakage mechanisms are pre-specified before any transfer experiment exists** (case, guideline, reviewer, temporal, policy-tuning leakage), each requiring "a frozen artifact and a receipt in the evaluation harness."
11. **Cross-literature tensions are kept open rather than resolved in the review's own favor** — eleven named contradictions (e.g. "disagreement may be informative rather than noise") are retained explicitly because *"contradictory evidence... narrows gap claims and reveals failure conditions."*

## Gaps and defects

### A. Evidence-boundary / overclaim risk (highest priority — this is the project's core discipline)

I verified each of these directly myself against the primary sources; all four are confirmed.

- **84/100 vs. 36/100, self-contradicted under identical dimension names.** Docx line 26 and line 435: `Current readiness score || 84/100` and `Overall || 84/100 || Doctoral working-review quality`. `Dashboard.csv`: `Overall literature readiness,36` and `Release Decision: NOT DOCTORAL-READY`, reason: *"QL-01–QL-05 remain 0/5; 139-record row-level screening is incomplete; FT-A target and human/second review remain open; RQs are provisional; EXP-005 is 0/24; medical readiness is 0/6."* The docx's own Table 29 hostile-review scorecard uses the same dimension labels (`Search rigor`, `Gap defensibility`) as the workbook without ever citing or reconciling the workbook's much lower values for those same labels. *(Note: the workbook's Dashboard sheet lays out several side-by-side panels that flattened into one CSV grid during extraction — the headline `36` / `NOT DOCTORAL-READY` pairing is unambiguous and single-panel, but the more granular per-dimension pairings, e.g. exactly which "Search rigor" number belongs to which panel, should be re-checked by opening the actual Excel file before quoting a specific per-dimension number.)*
- **"Nine targeted search families executed" appears 5 times; the frozen QL-01–QL-05 protocol is named by that label exactly once, and never alongside any of those five "executed" mentions.** A reader who only sees Table 3, Table 29, or the Appendix A heading — the most skimmable locations — has no way to learn the pre-committed 5-query protocol sits at 0% completion. I confirmed zero occurrences of "EXP-005" anywhere in the document — a genuinely clean result on that specific risk, but it also means EXP-005's 0/24 status never appears next to the 84/100 figure either.
- **Appendix A's table drops the "exploratory only, human review pending" qualifier that `Search_Registry.csv` is careful to state for the same nine searches.** The docx paraphrases this down to "Executed - targeted, non-exhaustive," a real but weaker caveat that silently omits that Ali's human review of these AI-assisted searches hasn't happened yet.
- **Search-rigor self-score (7/10) rates the dimension the frozen protocol is at 0/5 on.** `Construct_Risks.csv` row MR-01 independently states "Formal QL-01–QL-05 searches remain 0/5," status `Blocked`.

### B. Production and reference defects

- **Confirmed by me directly:** Section 7 says *"The schema in Figure 5 (below) has six groups"* and lists case grounding / decision trace / governance / reuse signals / validation / outcome trace — but Figure 5 is captioned "Human-agent teaming and control architecture" (unrelated). The six-group schema is Figure 16, "Governed Judgment Object and minimum reconstructability fields," which appears a few lines later. Same underlying sloppiness pattern the v10 report flagged (stale labels not updated after the document was revised) — this time as a stale figure pointer instead of a stale page-header/version label.
- At least a dozen author-year citations used in the prose (Shneiderman 2020, Dellermann et al. 2019, Fox et al. 1997, Ananieva et al. 2022, Pearl & Bareinboim 2014, Reflexion, Voyager, and others) have no matching entry anywhere in References or Appendix B.
- Roughly 30 of the 81 catalogued References/Appendix-B sources — including all four of the document's own highest-maturity 2026 agent-memory papers (APEX-MEM, MemORAI, PerMemSafe, TiMem, all tagged FT-A) — are never mentioned by name in any of the 16 narrative sections. Section 9 ("Retrieval, persistent agent memory, and case-based reuse") discusses different, uncited systems instead.
- `Fervers et al., 2006` is cited in Section 10; the only Fervers entry in References/Appendix B is dated 2011.
- Section 1.2 cites "Appendix D" for bibliographic-identity verification; the document only contains Appendix A and Appendix B before References. No Appendix C or D exists.
- **Two things checked out exactly, no discrepancy:** the "20 core anchors, 14 FT-A / 6 FT-B" claim matches `Core_Anchors.csv` precisely, and the "preserved 139-source workbook" reference matches `Dashboard.csv`'s historical baseline exactly.

### C. Docx-vs-workbook consistency (root cause: the workbook is rebased to v10, not v13)

I confirmed directly: `Provenance.csv` row PROV-003 names "Literature Review v10 (18 Aug 2026)" as the "Current authoritative literature review," and even the newest workbook artifact, PROV-006 (v5, dated 2026-08-19 — the same day as v13), is described only as adding "U-RQ, SQ1, SQ2, and SQ3 deep-dive sheets," never as rebased to v13. The docx and its own supporting workbook are, right now, describing two different states of the project.

- Claimed "81 sources, 44 FT-A, 37 FT-B" (docx) vs. workbook's tracked "Included: 60" / "FT-A: 15" / "FT-B: 7" (`Dashboard.csv`) — roughly a third of the claimed maturity counts. `Bibliographic_QA.csv` has only 62 data rows, not 81.
- Appendix A's Q1–Q9 search families and their specific screened/included counts (e.g. "Q5 Reuse and Memory: 26 screened / 15 included") have no basis in `Search_Registry.csv`, which instead names a differently-labeled set (SQL-01–SQL-09) with `Result Count: Not captured` on every row.
- Table 6's "provisional wording" for SQ3 (and the Umbrella RQ, and SQ2) does not match `RQ_Registry.csv`'s own "Current Exact Provisional Wording" column — it's closer to that sheet's separate "Candidate Revised Wording," which is explicitly marked `Supervisor approval pending` on every row.
- Gap_Audit.csv's G6 (`Category: Construct Risk`, excluded from the external-gap count) and G5 (`Status: Blocked for empirical closure — EXP-005 0/24`) are both presented in docx Section 13/Table 25 as co-equal open literature gaps with no status column reproducing either distinction.
- `Core_Anchors.csv`'s CA-S205 (Raykar et al. 2010, an SQ2 anchor) does not appear anywhere in the docx's own 81-row Appendix B or References — even though Section 1.2 claims bibliographic identity was rechecked "for all 20 core anchor mappings."
- Three sources (the VEGO-AI baseline manuscript itself, plus Santoni de Sio 2018 and Lewis 2020/RAG) are rated `ID-S` or `AB-S` (identity/abstract-only) in `Bibliographic_QA.csv` but `FT-A` (full-text reviewed) in the docx's own Appendix B — and Section 16 then states detailed, settled-sounding findings about the baseline manuscript on the strength of that inflated label.
- An unapproved "candidate" SQ2 definition (excluding reuse, per `Decision_Log.csv` D-011, `Supervisor approval required`) is narrated as already-settled fact in Section 14 ("SQ2 owns the judgment representation and lifecycle... It does not assert that the record may be reused"), while Section 15 separately, correctly, still lists RQ wording as an open P0 blocker requiring supervisor approval — the document contradicts itself on this point across two adjacent sections.
- Corpus maturity (44 FT-A / 37 FT-B) is cited as grounds for a higher score in Section 15, without ever mentioning that the workbook's own "Direct evidence proportion" metric is 8.3/100 — maturity (how much text was read) and directness (whether it actually applies) are separate axes in the project's own controls, and only the more flattering one is surfaced.

### D. Fulfillment of Iris/Arnon's specific Aug-12 instructions

| Instruction | Status | Evidence |
| --- | --- | --- |
| Organizing principle = human involvement × agentic AI, not HCI | **Met** | No section is HCI-organized; the two HCI mentions are on-topic HCI-venue papers cited as sources, exactly as she said was fine |
| Gap must sit in the problem world, not the solution world | **Partially met, high-severity slip** | Section 7 specifies a concrete record schema with its own "invariants" and "minimum acceptance test"; Figures 30–31 present a full proposed architecture and a three-study roadmap — solution design narrated at length inside the literature chapter, not confined to a separate section, despite being captioned "hypothesis, not a validated contribution" |
| This week's scope: classify the ACL-2026 GitHub taxonomy corpus as relevant / less relevant / not relevant / missing; one slide for the next meeting | **Not met** | The taxonomy gets one passing mention ("the bounded ACL taxonomy seed"); the four-way classification and the slide do not exist anywhere in the document. Instead, nine broad search families ran across ACL/ACM/AAAI/PMLR/PubMed/ScienceDirect/web — the broader search explicitly deferred to *after* the proposal stage |
| Conventional lit-review structure, not literal SQ1/SQ2/SQ3 section labels | **Met** | 16 sections organized by literature stream/topic; SQ-labels appear only in the positioning section (14) as a mapping, not as section headings |
| Each SQ → one study → one artifact + methodology, two guideline scenarios (SE + medical) | **Correctly out of scope** | This was explicitly assigned to the methodology chapter, not the literature review, and Iris resequenced methodology work to start only after the literature review is judged done — so its absence here is right, not a defect |

### E. Carryforward from the v10 verification report

| v10 finding | v13 status |
| --- | --- |
| Page-header stuck at "Page 1 of 41," "END OF VERSION 9" tail line | **Cannot confirm from this dump** (headers/footers not captured); same underlying sloppiness pattern recurs as the Figure 5/16 mislink |
| 6 contribution hypotheses (C1–C6) vs. Chapter 4's 1-artifact-per-study, SQ2 the clearest split | **Not resolved** — Table 8 still lists two separate SQ2 rows (G2+G6 judgment representation; G3 governance lifecycle); the string "Chapter 4" does not appear anywhere in v13; none of v10's three reconciliation options were taken |
| ACL-116 corpus disposition incomplete | **Not resolved, and now less traceable** — "ACL-116" no longer appears anywhere; replaced by the smaller, differently-scoped "Zou et al. taxonomy seed" with no explicit statement of what happened to the original disposition |
| Manuscript-vs-package count mismatch (178 vs 165 models, 26 vs 27 patterns) | **Still flagged open (correct not to silently resolve it), but the specific competing numbers (165, 27) are no longer stated** — a reader has to go find the original discrepancy elsewhere |
| Name a 2nd Study-2 implementer, 2 Study-3 raters | **Not addressed** — no mention anywhere in v13, despite Chapter 4 independently flagging the identical gap twice |
| Trim the repeated evidence-boundary disclaimer | **Body text looks improved** — roughly once per major part rather than repeated verbatim; page-header repetition unverifiable from this dump |

## Add / modify / change / delete — consolidated action list

**Add**

- The ACL-2026 GitHub taxonomy walkthrough and the relevant/less-relevant/not-relevant/missing classification slide Iris asked for — this is the single most concrete unmet deliverable.
- A status/category column on the gap table (Section 13) reproducing `Gap_Audit.csv`'s per-gap Category/Status distinctions (G6 = construct risk, not research gap; G5 = blocked on EXP-005).
- The specific competing counts (178 vs 165 models, 26 vs 27 patterns) back into the limitations text, and an explicit "ACL-116 disposition: status X" statement.
- A resourcing-gap line naming the still-missing second Study-2 implementer and two Study-3 raters, mirroring Chapter 4 §4.7.
- Missing References/Appendix B entries for every citation actually used in the prose (Shneiderman 2020, Reflexion, Voyager, etc.), or removal of the citation if the source was dropped.

**Modify**

- Move the Governed Judgment Object schema (Section 7) and Figures 30–31's proposed architecture/roadmap out of the literature-review chapter and into Chapter 4, leaving Chapter 2 to state only the problem, prior-work coverage, and falsifiers.
- Fix the Figure 5 → Figure 16 cross-reference in Section 7.
- Correct the Fervers citation year (2006 → 2011) to match References/Appendix B.
- Align the docx's Appendix B maturity labels for the VEGO-AI baseline, Santoni de Sio (2018), and Lewis (2020/RAG) with `Bibliographic_QA.csv`'s more conservative ratings before Section 16 treats their findings as settled.

**Change**

- Reconcile the 84/100 headline score against the workbook's 36/100 `NOT DOCTORAL-READY` verdict — either explain why the two scoring frameworks diverge, or replace the headline with the stricter, workbook-computed figure until they agree.
- Add the QL-01–QL-05 execution count (0/5) as a standing sub-note wherever "nine search families executed" appears (5 occurrences), so no single skimmed location omits it.
- Restore the "AI-assisted, human review pending" qualifier in Appendix A's Table 30 to match `Search_Registry.csv`.

**Delete / reconcile**

- Either the docx's "81 sources / 44 FT-A / 37 FT-B" claim or the workbook's "60 included / 15 FT-A / 7 FT-B" tally has to go — right now both exist and disagree by roughly a factor of three. Given the workbook is the more conservative, methodically-tracked artifact, the likely right move is to add the missing ~20 sources to `Supporting_Literature.csv`/`Bibliographic_QA.csv` and regenerate `Dashboard.csv` against v13, rather than trust the docx's higher, currently unsubstantiated count.
- The single biggest structural fix: rebuild/rebase the workbook against v13 (Provenance.csv currently still names v10 as authoritative) before either artifact is shown to Iris/Arnon as representing the current state — most of section C's mismatches trace back to this one root cause.

## Bottom line

v13 is a genuine, substantial improvement over v10 in rigor, falsifiability, and self-critique — the strengths list above is real and specific, not padding. But it is not yet consistent with its own supporting workbook (which independently scores it 36/100, not-doctoral-ready, for the same evidence state), it has not yet done this week's actual assigned task (the ACL taxonomy classification and slide), and it repeats — in a new form — the exact carryforward gaps v10 already named (SQ2 artifact-count conflict with Chapter 4, missing resourcing names, unresolved ACL-116 and count-mismatch flags). None of this requires new research to fix; it requires reconciling two artifacts that are currently describing two different project states, and finishing the narrower, already-assigned taxonomy exercise before broadening the search further.
