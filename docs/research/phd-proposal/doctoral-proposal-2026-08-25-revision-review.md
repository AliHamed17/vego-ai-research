# Doctoral Proposal, 2026-08-25 Revision - Strict Review

**Reviewed:** `VEGO_AI_Doctoral_Proposal_Revised_20260825.pdf` - 29 pages (the harness labels it 21;
the document's own footers read "Page N of 29"). Successor to the 2026-08-23 draft scored 73/100 in
`doctoral-proposal-2026-08-23-strict-review.md`.

**Method:** pypdf text extraction, then mechanical verification of every falsifiable claim carried
forward from the prior review plus every item in
`literature-review-enhancement-2026-08-25.md`; figure/table/TOC/cross-reference integrity checks;
an overclaim scan against the standing evidence boundary; and external verification of the five
newly added and three newly changed references (Crossref, DBLP, OpenAlex, publisher PDFs, PubMed),
each alleged defect re-checked by an independent adversarial adjudicator.

## Strict score: 93/100

This is a different document, not a patched one. The standalone literature-review chapter is gone,
replaced by the structure of the approved Haifa reference proposal: literature as Introduction
background funnelling to a gap, the systematic review as a research activity with a stated
protocol, and its progress reported honestly. Every verified defect from the prior review is fixed,
the restructure introduced no technical regressions, and the evidence boundary held. What remains
is one trivial citation slip, one uncited clause, and the fact that the specific deliverable Iris
named is now substantially - but still not completely - discharged.

| Dimension | Weight | 08-23 | 08-25 | Why |
| --- | --- | --- | --- | --- |
| Evidence-boundary discipline | 25 | 24 | **25** | Held through a full restructure; Table 10 gates each evidence source; Appendix B consolidates every open item |
| Citation integrity | 20 | 16 | **19** | All three prior defects fixed, DOIs added throughout, author lists expanded, renumbering flawless; one missing year |
| Fulfillment of Iris/Arnon's 08-12 instructions | 20 | 8 | **15** | Organizing principle, domain-independence, scenario separation and solution-world removal all done; the corpus-level classification and the slide are still outstanding |
| Resolution of recurring cross-report issues | 15 | 10 | **15** | All five now resolved or explicitly disclosed as open |
| Internal consistency / production quality | 10 | 5 | **9** | Figures and tables ascending, zero TOC errors, zero dangling cross-references; one uncited clause |
| Methodological / design-science rigor | 10 | 10 | **10** | Strengthened: the review is now an activity with a protocol and an evaluated artifact |
| **Total** | **100** | **73** | **93** | |

## What was fixed, verified item by item

| Prior finding | Status in this revision |
| --- | --- |
| ACL taxonomy exercise absent (4 artifacts running) | **Substantially done.** §1.3.1 in-body plus Appendix A; all 10 taxonomy dimensions and all 11 gap concepts present |
| Solution-world bleed in the literature chapter | **Fully fixed.** Zero "Study N" mentions anywhere in the Introduction (pp.4-11); the "Study 2 must test" and "Study 3 must treat" directives are gone; Figures 5/6/7 relocated into the methodology at pp.15/16/18 |
| Figures 5,6,7 preceding 3,4 | **Fixed.** 11 figures in ascending order; 16 tables also ascending |
| TOC page-number error at §1.2 | **Fixed.** Zero mismatches across all 28 numbered TOC rows |
| [35] GLIF3 wrong journal | **Fixed.** Now *Journal of Biomedical Informatics*, vol. 37, no. 3, pp. 147-161, with DOI |
| [20] Ancker truncated title | **Fixed** (now [42]) - closing clause restored, DOI added |
| [27] Santoni de Sio missing subtitle | **Fixed** (now [31]) - subtitle restored, DOI added |
| [45] Ahmed - my own erroneous correction | **Correctly ignored.** Kept "K. E. Ahmed" and expanded to the full five-author list |
| Count-discrepancy regression | **Reversed.** Both 178/26 and 165/27 now stated, flagged "Unresolved" in Appendix B |
| Eight signals derived but never specified | **Fixed.** All eight enumerated in §3.3, versioned and ablatable, with P1 tested against the declared set |
| Two-scenario split | **Done.** §2.3 "Scenario instantiation", Scenario A/B, with the medical route staged and off the critical path |
| Organizing principle not in Iris's words | **Done.** Chapter 1 opens with "organized around human involvement in the context of agentic AI, treated domain-independently" |
| Survey described as six categories | **Fixed.** Now "five core components ... of which the latter four form the top-level branches", with the conjoined-component point made explicitly |

## Genuine strengths

1. The restructure is technically clean, which is rare. A 21-to-29-page reorganization that
   renumbered 57 references to 62 produced: zero dangling in-text citations, zero uncited
   bibliography entries, a complete 1-62 sequence, zero dangling section cross-references, and no
   surviving "Chapter 2" language. This is precisely where such rewrites normally break.
2. §4.2 is a model of honest progress reporting: "None has been executed. There are therefore no
   screening counts, no inclusion counts, and no corpus size to report, and none will be reported
   until the searches are run." The section summary then refuses the stronger reading outright —
   "Chapter 1 stands as a critical synthesis and nothing stronger."
3. Appendix B is the single best addition. It consolidates open decisions and boundaries in one
   table, including two things most candidates would quietly omit: "Supervisor approval is not
   recorded", and a reference-verification note conceding that "one author-name form remains in
   dispute between indexes" rather than silently picking a side.
4. The evidence boundary survived the restructure intact. The abstract still leads with the
   non-claims ("They establish neither improved accuracy, nor reduced expert effort, nor safe
   reuse, nor clinical validity"), Table 10 gates each evidence source, and EXP-005 and the six
   medical gates are both disclosed. An overclaim scan found no unqualified claim; the hedging is
   careful to the point of elegance — "these results do not support a simple claim that assistance
   improves modelling; they support the narrower claim that assistance changes which errors
   survive."
5. §1.3.1 leads with the negative result, which is the correct emphasis: "The more useful result is
   negative", followed by the unifying observation that all eleven missing concepts "concern what
   happens to a judgement after it has been given."
6. The review is now a research activity with a citable protocol and an evaluated artifact (§3.2):
   SLR guidelines, Wohlin snowballing and PRISMA 2020, five concept groups with actual terms, fixed
   source roles, a per-query audit record, and consolidation into a taxonomy developed and evaluated
   by established methods. This is the reference proposal's pattern, correctly applied.
7. The section-summary device scaled cleanly — 25 blocks, each with exactly one "Established." and
   one "Research implication.", up from 23, with the solution-world instances repaired rather than
   removed.

## Remaining defects

### A. The named deliverable is substantially, not fully, discharged

Iris's assignment as recorded in `issues.md` (ISS-034) was to classify the ACL-2026 GitHub taxonomy
*corpus* as relevant / less relevant / not relevant / missing, and to produce *one slide*. This
revision classifies the taxonomy's *branches and dimensions* — four branches, ten dimensions,
eleven unexpressible concepts — which is genuine, well-executed work, and the document is honest
about its scope (§4.2: "complete as a classification of that one survey's branches and dimensions").
But the corpus is the roughly ninety papers classified under those branches, and they have not been
screened for relevance. No slide exists either; Appendix A is a document section.

In fairness, this narrowing is mine as much as the candidate's. My own enhancement package (Item 8)
framed the exercise as a branch-and-dimension classification, and the revision implemented exactly
what I specified. The gap is therefore in my specification, not in the execution of it. It still
needs closing, because it is the fifth artifact in which the corpus-level screening does not appear.

Fix: screen the ~90 papers under the four branches against the RQs with the four-way disposition,
report the counts, and cut the one slide from Appendix A's existing content plus §8.4 of the
enhancement package.

### B. An uncited, reader-opaque appeal to an external document

§3.2 states: "Following *the reference proposal's* treatment of a taxonomy as the deliverable of a
systematic review, the classification ... will be consolidated into a taxonomy". There is no
citation for "the reference proposal", and the phrase is meaningless to any reader who was not shown
the University of Haifa privacy-compliant-software-reuse proposal. Leaning on an unpublished peer
document as a methodological warrant is also the wrong kind of authority for a proposal.

Fix: delete the clause. The sentence already cites [59] Nickerson et al. and [60] Usman et al. for
taxonomy development and evaluation, which are published, citable methods and are all the warrant
the sentence needs.

### C. One citation defect, and one non-defect worth knowing about

All five newly added references and three newly changed ones were verified externally; each alleged
defect was then re-checked by an independent adversarial adjudicator.

- [60] Usman et al. is missing its publication year entirely. The entry ends at "pp. 43-59." The
  correct year is 2017 (Crossref published-print 2017-05, online 16 January 2017; DOI
  `10.1016/j.infsof.2017.01.006`). Every other field — authors, title, journal, volume, pages — is
  correct. Minimal fix: append ", 2017".
- [4] Hevner et al., pp. 75-106: no change needed. This revision changed the range from 75-105, and
  the change is defensible. The publisher's own typeset PDF footer reads "pp. 75-105", and DBLP,
  Semantic Scholar and Scopus-fed repositories agree; but Crossref's publisher-deposited record
  (MISQ's own DOI prefix) and OpenAlex both give 75-106, the printed DOI resolves to a landing page
  carrying 75-106, and the issue's table of contents allocates 75-106 to this article with the next
  starting at 107. The one-page difference turns entirely on whether the trailing blank verso inside
  the article's allocation is counted. Both forms circulate legitimately and neither affects
  identification or retrieval. Leave it as printed.
- Confirmed exact: [56] Kitchenham & Charters, [57] Wohlin, [58] PRISMA 2020, [59] Nickerson et al.,
  [48] Aroyo & Welty ("Crowd Truth" as two words is the published form), and [14] Schunemann et al.
  (the expanded GRADE-ADOLOPMENT title is correct).

### D. Standing limitations, correctly disclosed rather than concealed

These are not defects in the document — they are the state of the work, and the revision states each
one plainly. They are listed so the ceiling is explicit: zero of five query lines executed, so no
coverage or corpus claim is available; EXP-005 generalization-safe labels incomplete, so accuracy,
generalization and integrated-benefit claims stay blocked; zero of six medical entry gates
satisfied; independent reviewers, raters and implementer not yet recruited, so reliability and
implementation-independence claims are blocked; supervisor approval of the RQ wording not recorded;
and the 178/26 versus 165/27 count discrepancy unresolved because the implementation snapshot was
not supplied to this revision.

## Action list

Add: the year 2017 to [60]; the corpus-level screening of the ~90 taxonomy papers, with counts; the
one slide.

Delete: the "Following the reference proposal's treatment..." clause in §3.2.

Leave alone: [4] Hevner's page range, [18] Ahmed's middle initial, and every fix already applied —
all were verified correct as they now stand.

## Bottom line

The prior review's three headline complaints are all discharged: the solution-world bleed is gone
from the Introduction entirely, the count discrepancy is restored and explicitly labelled
unresolved, and the ACL taxonomy work now occupies both a chapter subsection and an appendix. The
restructure to the reference proposal's shape was executed without introducing a single technical
regression, and the evidence-boundary discipline — the thing most likely to break in a rewrite this
large — came through stronger than before, now with a per-source gating table and a consolidated
status appendix.

What separates 93 from the high nineties is small and specific: a missing year, an uncited clause,
and the corpus-level half of one supervisor instruction. None requires new research. The larger
honest caveat is the one the document itself makes: with zero searches executed, Chapter 1 is a
critical synthesis and cannot yet be presented as systematic coverage — and it says so in those
words rather than leaving a reader to infer it.
