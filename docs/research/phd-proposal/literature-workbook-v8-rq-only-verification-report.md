# Literature Workbook v8 (RQ-Only, Audit-Aligned) — Strict Verification Report

**Reviewed:** `VEGO-AI_Literature_Workbook_RQ_Only_Organized_v8_Audit_Aligned.xlsx` — 4 sheets (`RQ`, `RQ1`, `RQ2`, `RQ3`), 5 core anchor sources per sheet, 20 total.

**Method:** Full read of all four sheets (every row, no sampling), then direct cross-checks against files already verified in this session: `Core_Anchors.csv` and the full text dump from the literature-review-v13 docx (both still on disk from the earlier audit), plus `chapter-4-research-methodology.md`, `docs/agent-memory/issues.md` (ISS-033/034), and `literature-review-v13-workbook-verification-report.md`. I re-grepped the primary sources myself for every cross-file claim below rather than relying on recall.

## Executive summary

This is a genuine, substantive response to the two prior verification reports (v10, v13) — not a cosmetic relabeling. Three specific citation-integrity defects I found in v13 are fixed by removal in v8: Raykar et al. (2010), which v13's own Appendix B never actually listed despite being claimed as a core SQ2 anchor, is dropped and replaced with Aamodt & Plaza (1994); Fervers et al., cited in v13 with a year (2006) that didn't match its own bibliography entry (2011), is dropped entirely; Dellermann et al. (2019), cited in v13's body text with no bibliography entry at all, is dropped and replaced with Dhanorkar et al. (2026). Every one of the specific unresolved gaps I flagged in the v5 workbook and Chapter 4 — the SQ2 two-artifact split, the un-named second Study-2 implementer, the un-named two Study-3 raters, the RQ2/RQ3 boundary — is now explicitly named as an open item inside the relevant RQ sheet's own "Open evidence gates" row, rather than being silently repeated without comment the way v13's docx did.

That said, "acknowledged" is not "resolved," and this is the third consecutive artifact (v10 review → v13 review → this v8 workbook) where the SQ2/SQ3 artifact-count conflict with Chapter 4 surfaces and nothing actually closes it. There is also a real structural gap: this file drops from the 22-sheet v5 workbook down to 4 sheets with no provenance statement anywhere explaining the relationship — a reader who hasn't seen v5 has no way to know whether the missing 18 sheets (Search Registry, Bibliographic QA, Dashboard, Decision Log, Controls, Coverage Matrix, and others) were intentionally out of scope for this file or have simply been abandoned.

## What was done well (verified strengths)

1. **Three specific citation defects from the v13 review are fixed by removal, confirmed directly against the v13 text.** v13's body text (line 113) cites "(Dellermann et al., 2019)" with no matching bibliography entry anywhere in the document — v8's `RQ` sheet explicitly states "Dellermann et al. (2019) was replaced by Dhanorkar et al. (2026)." v13's body text (line 284) cites "(Fervers et al., 2006...)" while the only Fervers entry in v13's own References (line 564) is dated 2011 — v8's `RQ3` sheet explicitly states "Fervers... [was] replaced by... NIST SP 800-162 (ABAC)." v5's `Core_Anchors.csv` (row CA-S205) lists Raykar et al. (2010) as a core SQ2 anchor, but that source never appears in v13's own Appendix B or References — v8's `RQ2` sheet explicitly states "Raykar et al. (2010) was replaced by Aamodt & Plaza (1994)."
2. **Every unresolved gap I previously flagged is now named explicitly, in the artifact itself, rather than silently repeated.** `RQ2`'s "Open evidence gates" row states outright: "one-artifact-per-study alignment and Chapter 4 separation unresolved... second Study-2 implementer not named." `RQ3`'s equivalent row states "RQ2/RQ3 boundary unresolved... two independent Study-3 raters not named." `RQ2`'s closing note states plainly: "Literature-chapter content must stay problem/prior-work focused; detailed schema and architecture belong in the methodology/solution chapter" — a direct, correct response to the problem-world/solution-world blur the v13 review flagged in Chapter 4-adjacent material.
3. **Inline, checkable citations for every anchor — no separate References section that can drift out of sync.** Each of the 20 anchor rows carries its own DOI/URL, exact locator (page range or section), and a two-column "what it establishes / what it does not establish" pair. This avoids the exact failure mode that produced v13's missing-citation problem in the first place — a docx that cites something in prose and separately maintains an appendix that can fall out of sync.
4. **Evidence-boundary discipline is applied uniformly across every sheet, not just once.** All four sheets carry an identical "Formal QL, 0/5" figure in their anchor-count row, a "CONTROL STATE" banner at the top restating what is and isn't done, and a paired "Permitted wording" / "Prohibited stronger wording" row that is calibrated correctly in every case — e.g. `RQ1`'s permitted wording is "RQ1 tests VEGO-AI-specific multi-signal routing under a fixed expert-attention budget," never a claim that the routing works or improves anything.
5. **Every RQ sheet names, and does not shy away from, the single strongest existing-work objection to its own proposed artifact** — e.g. `RQ2`: "the Governed Judgment Object may be ordinary CBR plus provenance, contestability, and authorization metadata"; `RQ3`: "ordinary CBR + ABAC + context-adaptation metadata may already implement the proposed mechanism." This is the same falsifier discipline the v13 review praised, carried through correctly into this narrower artifact.

## Gaps and issues

### A. Acknowledged but still not resolved (same substance, third consecutive report)

- **SQ2 artifact count still conflicts with Chapter 4.** `RQ2` proposes "Governed Judgment Object + reconciliation process + Contestable Judgment Store" as its artifact(s) — still effectively two to three distinct constructs for one sub-question, against Chapter 4's own recommendation of one artifact per study (a single "contract-plus-conformance-suite"). `RQ2` itself names this as open ("one-artifact-per-study alignment and Chapter 4 separation unresolved"), which is honest, but naming a conflict for the third time across three separate artifacts without a decision point is itself a process gap — nothing in this project currently forces that decision to close.
- **Resourcing gaps restated, still nobody named.** `RQ2`: "second Study-2 implementer not named." `RQ3`: "two independent Study-3 raters not named." Both exactly match what Chapter 4 §4.7 and the v10/v13 reports already said. Restating a gap is not the same as assigning an owner or a deadline for closing it.
- **RQ2/RQ3 boundary still open**, matching v5's `Decision_Log.csv` D-011 and `Construct_Risks.csv` CR-02 (the SQ2/SQ3 reuse-scope overlap) — `RQ3` names it directly, but no resolution is proposed here either.

### B. Structural / provenance gap

- **No statement of this file's relationship to the 22-sheet v5 workbook.** v5 had a `Provenance.csv` sheet with an explicit rebase manifest naming every predecessor artifact and its role. v8 has no equivalent sheet and no note anywhere in `RQ`/`RQ1`/`RQ2`/`RQ3` stating whether v8 supersedes v5, is a scoped extract of it, or runs in parallel with it. A reader who has only seen v8 cannot tell whether `Search_Registry`, `Bibliographic_QA`, `Screening_Log`, `Full-Text_Extraction`, `Decision_Log`, `Controls`, `Coverage_Matrix`, `Dashboard`, `Construct_Risks`, `Prior_Work_Matrix`, `Claim-Evidence`, and `Survey_Snowballing` (all present in v5, all absent here) were deliberately out of scope for this narrower "RQ-only" file or have been quietly dropped.
- **v5's `Core_Anchors.csv` is now stale and nothing marks it so.** v8 changed 3 of the 20 core anchor identities (Raykar→Aamodt & Plaza; Fervers→NIST SP 800-162; Dellermann→Dhanorkar; plus WILDS dropped from the RQ3 anchor set). None of this is reflected back into v5's own `Core_Anchors.csv`, which still lists the old set. The two files currently disagree about which 20 sources are load-bearing, with no cross-reference in either direction.

### C. Minor items

- **Two of the twenty anchors are 2026-dated papers I cannot independently verify from this review alone** (Dhanorkar, Passi & Vorvoreanu, FAccT 2026; Dong et al., ACL 2026). Both are plausible, specific, well-formed citations with real-looking venues and page ranges, and I have no basis to call either fabricated — but neither should be treated as confirmed until the actual QL-01–QL-05 database export runs, per the workbook's own stated discipline.
- **Not every anchor swap was a defect fix.** WILDS/Koh et al. (2021) was a properly cited, `FT-A` source in v13 (Appendix B row S048) — removing it from `RQ3`'s five-anchor cap was an editorial narrowing choice, not a correction of an error, unlike the Raykar/Fervers/Dellermann swaps. Worth being explicit about which swaps were fixes versus which were curation, since the "replaced" framing currently reads the same for both.

## Add / modify / change / remove

**Add**

- A provenance/version note (even one sentence per sheet, or a fifth sheet) stating v8's relationship to v5 — supersedes it, extracts from it, or runs alongside it — and which of v5's other 18 sheets remain active elsewhere.
- A one-line note in `Core_Anchors.csv` (v5) or a changelog entry flagging that its SQ2 and SQ3 anchor rows are now superseded by v8's `RQ2`/`RQ3` sheets, so the two files stop silently disagreeing.
- An explicit owner and target date for closing the SQ2 artifact-count question — this has now been named as open in three consecutive artifacts (v10 report, v13 report, this workbook) without ever reaching a decision point. It belongs as a sixth item in `2026-08-19-decisions-packet.md` alongside the five already there, or as an explicit agenda item for the next supervisor call.

**Modify**

- Distinguish, in the "Anchor-selection decision" note for each sheet, which swaps corrected a citation defect (Raykar, Fervers, Dellermann) versus which were ordinary curation (WILDS) — right now both read as equivalent "replacement" decisions.

**Change**

- Nothing found here needs walking back; the wording discipline (permitted/prohibited claims, evidence gates, falsifiers) is calibrated correctly throughout and should not be loosened.

**Remove**

- Nothing in the 4 sheets warrants removal. The only "removal" concern is the opposite direction: v5's now-superseded Core_Anchors rows for SQ2/SQ3 should be removed or flagged, not v8's content.

## Bottom line

This is real progress, not a relabeling exercise — three specific, previously-flagged citation defects are fixed, and every substantive gap I named in the last two reports is now named inside the artifact itself rather than silently repeated. What's missing is closure, not honesty: the SQ2 artifact-count conflict with Chapter 4 has now been flagged three times running without anyone deciding it, and the file itself doesn't say how it relates to the 22-sheet workbook it appears to narrow down from. Fix the provenance gap and put the SQ2 question on an actual decision agenda, and this artifact is in good shape.
