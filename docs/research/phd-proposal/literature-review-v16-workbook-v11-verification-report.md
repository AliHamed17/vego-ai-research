# Literature Review v16 + Workbook v11 — Strict Verification Report

Audited files (external, not in git — supplied by Ali on 2026-08-20):
`VEGO_AI_Literature_Review_v16_GitHub_Synchronized_45_Page_2026-08-19.pdf` (45 pages) and
`VEGO-AI_Literature_Workbook_RQ_Only_Organized_v11_GitHub_Aligned.xlsx` (4 sheets: RQ, RQ1, RQ2,
RQ3). Method: a 70-agent workflow ran 7 independent expert-lens reviews (methodology, citation
integrity, cross-artifact consistency, workbook internal integrity, ground-truth alignment against
this repo's real state, claim-boundary compliance, academic writing quality); every finding was
then independently re-checked by a skeptical fact-checker instructed to actively try to refute it
and default to rejecting anything unverifiable; only findings that survived that adversarial pass
are reported below. Three independent judges then scored the release against the document's own
7-criterion rubric, and a final synthesis reconciled their scores. 59 findings were raised; 36
survived adversarial verification (4 critical, 17 high, 10 medium, 5 low).

## Headline verdict

**Reconciled score: 32/100** (median of three independent judges: 28, 32, 34). The document's own
self-reported **"Overall 76/100"** (p.35) is rejected, not averaged in — it is roughly 2.4x the
reconciled score. **Not doctoral-ready, and not close**, per all three judges independently.

## Score comparison (0-10 per criterion; document's own rubric)

| Criterion | Reconciled (median) | Judge range | Self-reported |
|---|---|---|---|
| Literature breadth | 6 | 4-6 | 9 |
| Critical synthesis | 6 | 6-7 | 9 |
| Gap defensibility | 5 | 4-5 | 7 |
| RQ derivation | 4 | 4-5 | 8 |
| Citation and evidence control | 3 | 2-3 | 7 |
| Visual quality and preservation | 8 | 7-8 | 10 |
| Reproducibility | 2 | 1-4 | 5 |
| **Overall** | **32** | 28-34 | **76** |

Every criterion is inflated in the self-score. The pattern is not random: the criterion closest to
accurate is visual quality (8 vs. 10 — the one dimension fully under the author's control), while
the two criteria that require unfakeable, externally-verifiable evidence — reproducibility (2 vs. 5)
and citation/evidence control (3 vs. 7) — are the most inflated. Self-scores track author control,
not verifiability.

Why the self-reported 76 is rejected outright rather than partly trusted: it has no disclosed
weighting method (68/90=75.6% or 55/70=78.6% are both plausible reconstructions of "76," and the
document states neither); it is entirely self-assigned despite being labeled a "hostile-review
scorecard" with no named or independent reviewer; a perfect, non-epistemic polish score (visual
quality 10/10) is summed at equal weight with whether any literature search was ever executed
(search rigor 4/10, reflecting QL-01-05 = 0/5); and this is not a new problem — it is the exact
defect the prior v15 verification report already flagged in this same document lineage ("the 51.05
composite buries the three hard-blocked gates under unrelated technical-quality scores"), shipped
again unfixed in a new composite.

## Critical findings (4)

1. **A precise, repeated headline count is contradicted by the document's own controlling
register.** "ACL identity/disposition remains 106/116" is stated as settled fact on the title page,
in the abstract, in the Figure 1 caption, and on p.34 — but the document's own Appendix A (the
place designated to hold exact counts) records the ACL-116 row's Screened/Included fields as "Not
final" and flags "second review required." The figure also traces only to the companion workbook
(49+36+21=106), never to any PDF-internal count, and the compound term "identity/disposition"
itself violates the document's own explicit rule three pages earlier that identity, publication
status, and ACL-116 disposition "must not be conflated."

2. **The thesis's central novelty argument cites three sources that do not exist in its own
bibliography.** Page 28's "recent 2026 evidence narrows novelty further" paragraph — the passage
that argues the thesis cannot claim novelty for three specific mechanisms — cites Dhanorkar et al.
(2026), Villavicencio et al. (2026), and Zhou et al. (2026). None of the three appears in the
45-page References list or the 81-entry Appendix B. All three are real, correctly-attributed papers
(verified independently) that the companion workbook already has fully cited with DOIs — this is a
bibliography-compilation failure on the document's own load-bearing claim, not a research gap.

3. **Three of the workbook's highest-priority "core anchor" sources are untraceable in the paired
PDF**, including the single #1-ranked anchor (Dhanorkar, priority 95) for the umbrella RQ and
Raykar et al. (rank 5, RQ2). "Raykar," "Learning From Crowds," and "crowds" produce zero hits
anywhere in the 45-page PDF. Two "GitHub Synchronized"/"GitHub Aligned" artifacts released the same
day disagree on their own core bibliography.

4. **The self-reported "76/100" cannot be reverse-engineered from the document's own disclosed
inputs** and is directly contradicted by the paired workbook, which states verbatim "No global
readiness score is asserted" (workbook sheet RQ, cell A3) — the same day, same version family.

## High-severity findings (17)

**Scoring methodology (2).** The scorecard has no behaviorally-anchored rubric distinguishing a 9
from a 7 or a 4 on any criterion, and no independent or named reviewer performed it despite the
"hostile-review" label — the pattern is self-serving: every criterion under the author's creative
control scores 7-10, while only the two criteria requiring external, unfakeable verification
(search rigor, reproducibility) score at or below 5.

**Citation integrity (3 more, beyond the critical findings above).** Shneiderman (2020) is cited
twice in-text (pp.7-8) with zero References/Appendix B entry, despite the companion workbook having
the full citation and DOI. Dellermann et al. (2019) is cited on p.7 with no bibliography entry —
this is a recurring defect: it was flagged in the v13 and v15 verification reports of this same
document lineage, nominally fixed once, and has now resurfaced again. Pearl & Bareinboim (2014) is
cited on p.25 (the RQ3/transfer chapter) with no bibliography entry.

**Cross-artifact and workbook integrity (3).** The workbook's specific 49/36/21 relevant/less-
relevant/not-relevant breakdown (summing to 106) exists only in the workbook — the PDF's own
Appendix A, the one place that should corroborate it, says "Not final" instead. FT-A/FT-B evidence-
maturity labels are inverted between the workbook and the PDF's own Appendix B for 6 of 20 shared
anchor slots (Bansal, Kulesza, Aamodt & Plaza in two sheets, Hu et al., Schünemann) — a third of the
audited anchors. Gap G6 — one of the PDF's own six claimed residual gaps — is entirely absent from
all four workbook gap tables, so the "six-gap/three-artifact" partition the PDF calls validated is
not reproduced in the evidence ledger meant to back it.

**RQ wording drift (1).** The PDF displays a demoted v15-candidate RQ wording as current. A full-
text search of the 45-page PDF for the project's own canonical current wording (per
`three-study-contract.md` and the 2026-08-19 decisions packet — "co-reasoning," "variability
exploration scenarios," "guideline operationalization scenarios") returns zero hits. This is an
undisclosed substitution, not merely "pending approval" as the document frames it.

**Argumentative/traceability weaknesses (8).** The claimed six-gap/three-RQ mutually-exclusive
partition does not hold as written: G1's own definition requires evaluating "persistent downstream
reuse," which Table 8 assigns exclusively to SQ3; "authority" is claimed as an owned construct of
both SQ2 and SQ3 with no distinguishing definition at the point of the claim; Figure 27's own
"primary and secondary RQ ownership" caption admits arbitrated overlap that Table 8's single-owner
rows don't even display; G6 is a construct-validity critique of VEGO-AI's own labels forced into the
same external-literature-gap template as G1-G5. Terminology drifts across the same two-page span:
"C1-C6 requirements" (Table 8) vs. "C1-C7" (p.34 narrative) for the same construct, and four
different, never-reconciled names for the same three-way structure (Study 1/2/3, Artifact A/B/C,
SQ1/SQ2/SQ3, workbook sheet titles RQ1/RQ2/RQ3).

## Medium findings (10)

The workbook labels non-taxonomy, likely Ali-derived categories ("human-agency scale,"
"evaluation/ethics") as ACL "taxonomy branches" without qualification, in the same document family
whose PDF elsewhere insists on exactly that distinction. The per-source "priority scores" in all
four workbook sheets form a smooth, strictly monotonic sequence exactly tracking rank order, with
no visible sub-scores — consistent with numbers back-filled to match a holistic ranking rather than
computed, despite the rubric's own caption conceding "scores are editorial priorities, not empirical
quality ratings." Section 1.2's claim to be "concept-centric... not a sequence of paper summaries"
is contradicted by Sections 2-12's actual narrative-citation-chaining prose, which draws confident
"the literature establishes..." conclusions from a source base that is simultaneously disclaimed as
non-systematic and only 20-of-81 fully extracted. Appendix B's S002 entry ships an unresolved
"(ref says 2013)" year discrepancy into the final References list rather than resolving it (the
correct year, independently verified, is 2014). Raykar et al. (2010) — a named RQ2 core anchor in
the workbook — appears nowhere in the PDF at all. Workbook row EXP-008 has an arithmetic error (33÷26
= 1.269, not the stated 1.35) inherited verbatim from `chapter-5-preliminary-results.md`. Two
workbook rows (RES-2, RES-3) cite a real GitHub file by URL that does not actually state the fact
attributed to it — the correct source is a different file. G6 answers a categorically different
question than G1-G5 (a construct-validity critique of VEGO-AI's own labels vs. an external-
literature-gap claim), and its falsifier logically implicates SQ1 and SQ3 as well as SQ2, weakening
the "exclusive to SQ2" placement. The scorecard's "RQ derivation 8/10" asserts orthogonality as
settled despite the document's own overlap admissions elsewhere.

Low findings (5), including two verification positives: a 24-entry spot-check of Appendix B (S014,
S015, S016, S077, S042, S041, S039, S040, S034, S033, S038, S036, S056, S057, S043, S051, S079,
S080, S048, S061, S068, S069, S070, S081) found **no misattribution or fabrication** — every
author/year/title/venue/DOI combination independently verified as real. Separately, the PDF's
four-branch ACL-2026 taxonomy claim (Human Feedback, Interaction, Orchestration, Communication + 1
Applications section + 3 Ali-derived categories) is **correct** and resolves a defect the prior v15
report had flagged (v15 had merged two branches, yielding only 3-of-7 matches). Lower-severity
issues: the PDF flags the manuscript/package model-count conflict (165 vs. 178 models) without
stating the actual numbers the workbook gives; the same "C1-C6 vs. C1-C7" count mismatch recurs; the
PDF's "139-source workbook baseline" is not reconciled against this repo's own tracked corpus
(`literature/verified-research-corpus-2026-08-12.json`, 144 sources) — a conflict the v15 report
already named as open; and `literature/README.md` (the file this repo actually has right now)
contains no taxonomy section to compare against, because the PR that rebuilds it (PR #20) is still
open, not yet merged into main — see Follow-up below.

## Highest-priority next actions (from the reconciled synthesis)

1. Run QL-01 through QL-05 for real and populate Appendix A with a final, certified count before
repeating "106/116" (or any number) in the narrative.
2. Fix the bibliography: add complete References/Appendix B entries for Dhanorkar 2026,
Villavicencio 2026, Zhou 2026, Shneiderman 2020, Dellermann et al. 2019, and Pearl & Bareinboim
2014 — or remove the claims that depend on them.
3. Reconcile the PDF and workbook into one source of truth: add G6 to all four workbook gap tables
(or justify dropping it from the PDF), fix the 6 inverted FT-A/FT-B labels, and resolve the "no
global score" vs. "76/100" contradiction.
4. Replace the self-graded scorecard with either an actual external review or a disclosed, justified
weighting formula that cannot let visual polish offset search-rigor/reproducibility failures, and
drop the headline number to reflect reality (roughly 30/100, not 76).
5. Fix the RQ wording to match `three-study-contract.md` / the 2026-08-19 decisions packet, or
explicitly disclose why it was substituted.
6. Resolve the gap-partition contradictions (G1/SQ3 overlap, the shared "authority" construct,
G6's template mismatch, Figure 27 vs. Table 8) before presenting the six-gap structure as validated.
7. Complete extraction on the remaining 61 of 81 sources, or explicitly scope all field-level claims
down to the 20 sources that are actually fully extracted.

`literature/README.md` on `main` is still the old generic stub — the rebuilt, deduped,
awesome-list-format version (140 sources, taxonomy cross-reference, bibliography.bib) exists only on
the still-open `docs/literature-awesome-index-and-root-cleanup` branch (PR #20), which is fully
green and mergeable but was never merged. Finding 36 above is a direct consequence of that: this
audit's own ground-truth comparison couldn't check the taxonomy section because it isn't on `main`
yet. Merging PR #20 would resolve this.

This report reflects only findings that survived adversarial verification: a separate agent, for
every claim raised, was instructed to actively try to refute it (relocate the cited evidence itself,
check for an overlooked hedge or resolution elsewhere in the document, and default to rejecting the
finding if uncertain) before it could be marked confirmed. 23 of 59 originally-raised findings did
not survive this pass and are not included above. Three independent scoring judges then read the
full 45-page extracted text and all four workbook sheets themselves — not just the findings list —
before scoring, and were explicitly instructed not to simply average their own seven criterion
scores if that wasn't a defensible weighting for a systematic-review-adjacent doctoral deliverable.
