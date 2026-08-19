Literature review v10 — full verification report

Reviewed file: VEGO_AI_Literature_Review_v10_Iris_Aligned_Controlled_2026-08-18.pdf (41 pages,
read in full, word by word). Cross-checked against the canonical Aug-12 record
(2026-08-12-supervisor-meeting.md), the Aug-5 and July-29 records, this repo's own
three-study-contract.md and sections-2-and-4-thinking-notes.md, the foundation-paper
verification record, and my own Chapter 4 draft. Not cross-checked: the actual QL-01 to
QL-05 database searches (nobody has run them, including this review) and the pinned ACL-116
corpus disposition (also still open per the document's own admission).

Bottom line: this is a genuinely strong, disciplined piece of work. It correctly internalizes
every evidence-boundary rule this project has built up over three supervisor calls, its
empirical citations check out against sources I could independently verify, and its own
self-graded compliance matrix (Appendix E) is honest rather than inflated - I checked it against
my independent record of the Aug-12 call and did not find an overclaim. The real problems are
one production defect that needs a two-minute fix, one substantive structural disagreement with
the methodology chapter that needs a decision, and the same evidence gates that have been open
since July.

1. Recognition and production check (what you asked me to check first)

The PDF's text layer extracts cleanly - no garbled words, no broken encoding, no dropped
characters anywhere across 41 pages. That part is fine. Two real production defects, though:

- Every single page's running header reads "Page 1 of 41" - not page 2, not page 3, all the way
  through page 41. This is a template field that never advanced. It is the exact kind of defect
  that makes a document look unfinished the moment a reader flips past page 2, and it takes one
  find-and-replace-the-field-code fix in whatever tool generated it.
- The very last line of the document reads "END OF VERSION 9 DOCTORAL WORKING REVIEW" - but the
  title page, every header, and the filename all say v10. This is a leftover tail from the prior
  version that never got updated when the document was bumped to v10.

Neither defect touches content or evidence discipline, but both are the first thing a careful
reader (or Iris) will notice, and both are trivially fixable before this goes anywhere near a
supervisor.

2. Requirement-by-requirement cross-check against the Aug-12 (and Aug-5, July-29) record

I went through Appendix E's self-graded compliance matrix line by line and checked each grade
against my own independent record of the same calls, rather than trusting the document's own
summary. It holds up:

- E6 (exploration vs identification/classification) - graded Open. Correct: neither call
  resolved this, and the document does not pretend otherwise.
- E8 (human vs expert judgment) - graded Open. Correct, same reasoning. The document instead
  builds a controlled-terminology table (Appendix C.2) so both terms stay usable without
  conflation until the supervisors rule - a genuinely good way to keep working without faking a
  decision.
- A08-01 (recover the exact live-edited RQ wording from 08-05) - graded Open, "no saved copy."
  Matches exactly what I found when I looked for that saved chat earlier this session - it does
  not exist on this workstation either.
- 12A-05 ("was Google Scholar actually searched?") - graded Open, "blocks strong gap claims."
  Correct and important: this document designs six Scholar-safe query families (section 2.2.1)
  but does not execute them, and says so plainly rather than presenting query design as search
  execution.
- 12A-06 (the Arnon-vs-Iris HCI-framing disagreement from the 08-12 call) - graded Open. Correct;
  the document takes a middle position (HCI-venue papers included when on-topic, organizing frame
  stays domain-independent) but does not claim either side of that disagreement was resolved.
- The five hard gates (QL 0/5, ACL-116 incomplete, EXP-005 0/24, medical 0/6, the 40-60 full-text
  extraction target) are all graded Open/blocked, consistently, everywhere they appear in the
  document - not softened in the executive synthesis and then quietly reappearing correctly in
  the appendix, which is the failure mode I was specifically checking for.

I did not find a single item where the document's self-grade was more favorable than what the
underlying record actually supports.

3. Fact-check of the empirical numbers it cites about your own foundation paper

Section 10.2 reports specific numbers from the supplied VEGO-AI manuscript: 178 case models
(46+47+44+41 across the four settings), Language Advisor F1 of 0.75-1.00, Domain Advisor
guideline alignment of 0.70-0.88, and uncovered-fragment audit scores of 0.55 in both use-case
settings. I checked every one of these against docs/research/governance/vego-ai-foundation-
paper-record.md, which independently verified the same paper earlier in this project. All four
numbers match exactly. This matters because it is the easiest place for a literature review to
quietly round a paper's own caveated numbers into something more flattering, and this one did
not do that - it reported the weak 0.55 result as prominently as the strong ones, which is
exactly the "argues the gap, not the solution" framing Arnon originally asked for.

It also correctly reports the manuscript-versus-package count mismatch (178 case models in the
manuscript narrative versus 165 unique files in the supplied ZIP, 26 versus 27 variability
patterns) as an unresolved "reproducibility blocker" rather than picking one number and moving
on. That is the right call, but it is also a real, still-open item - see section 5 below.

4. Is the structure (topology) good?

Yes, with one caveat. The chapter follows exactly the order Iris asked for on 08-12 (E13/12A-10):
literature review before the gap chapter, organized around human involvement in agentic AI
rather than around the research questions or the VEGO-AI solution, with the software/medical
scenario split kept as a separate, later concern (sections 9-10) rather than baked into the
opening framing. Part 1 (purpose and RQs) through Part 8 (transfer) reads as a genuine
problem-world argument that only introduces VEGO-AI's own architecture in Part 10 - the "argue
the gap, not the solution" test Arnon raised on 08-05 and again implicitly on 08-12.

The caveat: this is a 41-page document with fourteen numbered parts and five lettered appendices.
That is defensible for a working evidence base, but it is not what a reader opens expecting when
they hear "literature review chapter." Before this becomes Chapter 2 of the actual proposal, it
needs a shorter reading path through it - either a 1-2 page front summary pointing to which parts
matter for which purpose, or a split between "the chapter" (parts 1-14) and "the audit trail"
(appendices A, C, D - which are genuinely appendix material, not reading material).

5. The one real substantive problem: it disagrees with my own Chapter 4 draft on artifact
granularity, and nobody has reconciled that yet

Section 13.2 of this review proposes six contribution hypotheses - C1 (Selective Human Review
Orchestrator), C2 (Governed Judgment Object), C3 (Contestable Judgment Store), C4 (Scope-Aware
Retrieval Advisor), C5 (Transfer Ladder and Classifier), C6 (Leakage-Safe Evaluation Harness) -
roughly two per study. My own chapter-4-research-methodology.md, written independently on this
side, recommends exactly one artifact per study (an attention-budget cost/coverage model for
SQ1, a judgment-record contract plus conformance suite for SQ2, a transfer-eligibility procedure
for SQ3). These are not contradictory in substance - SQ1's C1 orchestrator is clearly meant to be
driven by the same kind of trigger-priority model I described, and SQ3's C5+C6 map reasonably
onto my single SQ3 artifact plus its leakage-safe evaluation design - but SQ2 genuinely splits
differently: this review treats the object (C2) and its governance/lifecycle store (C3) as two
separate hypotheses, while my chapter folds both into one contract-plus-conformance-suite
artifact. That is precisely the question sections-2-and-4-thinking-notes.md Part 3 item 6 already
flagged as unresolved ("does each study need exactly one named artifact, or is a package
acceptable?") - and now two independently-produced documents in the same proposal have answered
it two different ways without either one saying so. Left alone, a supervisor reading both will
notice the mismatch before you do. This needs one of: (a) a short cross-reference note in each
document pointing at the other and stating they are compatible at different granularity, (b)
revising one document to match the other, or (c) taking it to Iris and Arnon as an explicit
sixth open decision alongside the five already in the decisions packet.

6. What's still missing or blocked - unchanged by anything in this review, and it says so itself

Nothing here closes any of the five hard gates: QL-01 through QL-05 remain at 0 of 5 executed,
the pinned ACL-116-work corpus disposition remains incomplete, the 40-60 complete full-text-
extraction target is not met (20 of the required range exist), EXP-005 remains 0 of 24, and
medical readiness remains 0 of 6. None of that is a defect in this document - it is honest about
every one of them, repeatedly. It is, however, the actual remaining work before this can become
an approved Chapter 2, and this review does not shrink that list; it just does the part of the
work that does not require a database subscription or an expert panel.

7. What to add, what to remove, what to fix - the direct answer

Add:
- Execute at least the ACL-116 corpus disposition first - it is bounded, does not need paid
  database access, and closing it converts one open gate into a closed one relatively cheaply
  compared to the QL-01-05 database searches.
- A one-paragraph reconciliation note addressing the artifact-granularity question in section 5
  above, in both this document and chapter-4-research-methodology.md.
- A short "how to read this chapter" pointer near the front, given the length noted in section 4.

Fix:
- The "Page 1 of 41" header on every page (section 1).
- "END OF VERSION 9" in the closing line (section 1).
- The "occasional variability... does not necessarily denote low frequency" naming issue the
  document raises about itself in section 1.3 - it correctly identifies this as a construct-
  validity risk but leaves the actual rename or explicit-definition fix as a "later revision
  should" item. That later revision should probably be this one, since the ambiguity is already
  fully diagnosed.
- The manuscript-vs-package count mismatch (178 vs 165 models, 26 vs 27 patterns) - it is
  correctly flagged as a reproducibility blocker but not resolved; resolving which count is
  authoritative should happen before either number is quoted in a submitted chapter.

Remove or shorten: nothing needs deleting for being wrong. If anything needs trimming for length
(section 4's caveat), it is the volume of near-identical-looking control tables (evidence levels,
claim-language status, controlled terminology, implementation-to-evidence checklist all use the
same table shape back to back) - a reader benefits more from fewer, denser tables than from many
thin ones that all say "here is a category and its permitted wording."

8. As an outside reviewer: what this needs more of, what it needs less of

More of: named people. Section 13.4's empirical sequence and my own Chapter 4 both converge on
the same real gap - nobody is named as the second independent implementer (for the SQ2
conformance suite) or the two raters (for SQ3's reliability evaluation), and this review's own
hard-gates list does not surface that resourcing gap as clearly as the evidence gates. It should.

Less of: repeated boilerplate. The evidence-boundary disclaimer ("no empirical, medical, or
supervisor-approval claim is inferred...") appears, in slightly different words, on nearly every
page's running header context and again in the front matter, section 2, section 14, and Appendix
E. Once per major section is enough; the current density risks a reader skimming past it
entirely because it stops reading as a warning and starts reading as furniture.
