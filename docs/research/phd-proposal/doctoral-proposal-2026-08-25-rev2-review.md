# Doctoral Proposal, 2026-08-25 Revision (second iteration) — Strict Review

**Reviewed:** `VEGO_AI_Doctoral_Proposal_Revised_20260825 (1).pdf` — 30 pages (footers read "Page N
of 30"; the harness labels it 21). Successor to the 29-page revision scored 93/100 in
`doctoral-proposal-2026-08-25-revision-review.md`. Confirmed a genuinely new file, not a
re-download: different sha256, 53 KB larger, two hours newer.

**Method:** pypdf extraction; a normalized sentence-level diff against the previous revision to
separate substantive change from the British-to-American spelling conversion that accounts for most
of the raw diff; full integrity suite (bibliography, in-text citation pointers, figure and table
ordering, TOC page numbers, section cross-references); an overclaim scan; a check for citation-title
corruption introduced by the spelling conversion; and a 21-agent adversarial pass over the seven
substantively new or rewritten passages, using three independent lenses (overclaim, rigor,
supervisor challenge) with a synthesis stage that dropped pedantic and out-of-bounds findings.
Every load-bearing factual claim made by an agent about the repository was re-verified by me before
being reported; two were rejected on that basis and are recorded below.

## Strict score: 91/100

**This score is not directly comparable to the 93 given to the previous revision, and the document
did not get worse.** The earlier review was mechanical and structural; this one added an adversarial
pass over the prose, which found defects the earlier method could not have surfaced. On every
dimension checked both times, this revision is equal or better. The three outstanding items from
the last review are all addressed, and the candidate made several unprompted self-corrections that
tighten claims. What pulls the number down is that the deeper pass exposed a weak link in the
central gap argument, an overstated description of the project's own evidence register, and — new
in this revision — three precision errors introduced by over-correcting toward caution.

| Dimension | Weight | Prev | Now | Why |
| --- | --- | --- | --- | --- |
| Evidence-boundary discipline | 25 | 25 | **24** | Still excellent; the register description overstates the artifact it points to |
| Citation integrity | 20 | 19 | **19** | [60] year fixed, 61/62 precisely stated, no title corruption from the spelling pass; "the reference audit" is an uncited external document |
| Fulfillment of Iris/Arnon's 08-12 instructions | 20 | 15 | **17** | Slide content now exists as Figure 11; corpus screening still not done, but disclosed in three places |
| Resolution of recurring cross-report issues | 15 | 15 | **15** | All five remain resolved or explicitly disclosed |
| Internal consistency / production quality | 10 | 9 | **7** | Integrity checks perfect, but three statements now contradict the project's own controlled documents |
| Methodological / design-science rigor | 10 | 10 | **8** | The central gap claim rests on a conjunction containing a tautological conjunct |
| **Total** | **100** | **93** | **91** | |

## The three outstanding items are all addressed

| Prior finding | Status |
| --- | --- |
| [60] Usman missing its publication year | Fixed — "2017" added |
| Uncited "the reference proposal" clause in §3.2 | Removed entirely; the sentence now rests on [59] Nickerson and [60] Usman, which is the right warrant |
| Corpus screening and the one slide | Slide content now exists as **Figure 11** ("Where the ACL-2026 human–agent taxonomy meets this research, and where it stops"). Corpus screening is **not done**, and is explicitly disclosed as outstanding in §4.2, in Appendix B, and in the exercise-status row |

The corpus response is the honest one rather than the convenient one. §4.2 states outright: "Two
further parts of that exercise are outstanding and should not be read as done."

## Unprompted self-corrections, all tightening claims

1. **"All 62 verified" became "61 of 62 … Reference [1] is unpublished."** This is exactly right and
   matches the project's own external-citation log: the foundation manuscript is MODELS-2026
   programme-listed but has no live DOI.
2. **A new epistemic caveat on the gap claim**: "Because the formal searches described in §3.2 have
   not been run, this is a statement about the literature reviewed here and not a proof that no such
   evidence exists." This is the correct scoping of a negative existential.
3. **The experiment register is now disclosed as "not independently auditable from this document."**
4. **The prototype behind the corrected taxonomy verdicts is disclosed** and scoped out of the
   contribution: "not part of the reported VEGO-AI baseline … not one of the three primary artifacts
   … not evaluated evidence."
5. **Negative claims were narrowed** from "what they do not supply" to "what the studies reviewed
   for this proposal do not supply."
6. **§4.1 was retitled** to "Reported baseline evidence from the foundation manuscript", making
   clearer that it reports someone else's result.

## Integrity: clean, again

62 references, sequence 1–62 complete, **zero** in-text citations without a bibliography entry and
**zero** bibliography entries never cited. Figures 1–11 and Tables 1–16 both ascending. **Zero** TOC
mismatches across 25 numbered subsection rows plus all six appendix and reference rows. **Zero**
dangling section cross-references.

The section-summary device now uses six chapter-appropriate label pairs across its 25 blocks —
`Established / Research implication` for literature, `Decision / Consequence` for research questions,
`Design choice / Evaluation consequence` for methodology, `Evidence to date / What it does not
establish` for progress, `Dependency / Planning implication` for the work plan, and `Risk / Decision
rule` for threats. This is a principled scheme, not drift, and the progress-section pair in
particular forces an explicit non-claim.

Two risks I checked that turned out to be **non-issues**: the British-to-American spelling conversion
did **not** corrupt any reference title (Fervers correctly retains "Utilisation", and the six
American-form titles were confirmed exact in the earlier full sweep), and an apparent "Appendix C"
reference was my own regex matching "appendix **c**ollects".

## Defects

### A. Three statements now contradict the project's own controlled documents

All three were introduced by this revision, and all three err by *understating* the work — an
unusual and comparatively benign direction, but they are still inaccuracies a supervisor can check.

1. **"The database-specific Boolean syntax has not been written, so the protocol is not yet frozen"
   (§4.2, and again in Appendix B) is wrong.** The project's own Search Execution Register states
   "This register *freezes* the first five literature-query concepts before execution", heads its §2
   "Exact *frozen* protocol queries", and says "The text in each code block is *the exact canonical
   Boolean expression*." The canonical syntax is written and registered; the QL-05 PubMed query is
   already in platform syntax. What actually remains is per-platform field-wrapper translation, which
   the register treats as an execution-time step.
   Accurate replacement: "The five query families and their canonical Boolean expressions are frozen
   and registered; the per-platform field wrappers and filters are recorded at execution. No query
   has been executed."
2. **"Per-family date bounds" (stated three times — §3.2 summary, §4.2, Appendix B) is wrong.** The
   register applies a single primary window, 2015–2026, across all five families, with a documented
   snowballing exception for older seminal work. Replace with "a single 2015–2026 window with a
   documented snowballing exception."
3. **The experiment register is described as recording more than it holds.** §4.3 calls it "a
   controlled document that records for each run its inputs, frozen versions, procedure, and
   outputs." `experiments/registry.md` is a seven-column table — ID, Title, Status, RQ, Code/Config,
   Outputs, Notes. There is no procedure column, no run-date column, and no per-run version or commit
   field; "frozen versions" is the weakest part, since version state appears only as a single global
   hash in the file header, not per run. Describe only what it holds: identifier, status, research
   question, code and configuration paths, output locations, and the interpretation attached to each.

### B. The central gap claim has a weak link

§1.8 and the abstract both carry the gap on a negative existential over a three-part conjunction: no
prior formulation assumes "a claim about a model fragment whose interpretation is contested, whose
reviewer must be selected for competence and authority, and whose resolution *may or may not*
legitimately affect a later and differently situated case."

Two problems. The conjuncts are the proposal's own design commitments stated in its own vocabulary,
so a conjunction of them is close to unfalsifiable by construction — no prior work was trying to
satisfy that specific triple. And the third conjunct, "may or may not", is a tautology: every
resolution either does or does not affect a later case, so it excludes nothing and cannot
discriminate prior work.

This matters more than the wording suggests, because it is the sentence the whole contribution rests
on, and it is the one a committee member will press. The fix is to name the single conjunct that
carries the deficit and state its falsifier — for example: "The specific deficit is reviewer
selection: no formulation in this corpus makes the choice of reviewer a function of assessed
competence and authority over the contested fragment. A single study that did so would refute this."
That is checkable, and it survives the honest caveat about unrun searches the passage already carries.

### C. Smaller items

- The prototype is doing load-bearing work that the disclaimer denies. The passage disclaims the
  prototype three times, yet one sentence earlier that same prototype is the sole reason "part of
  every first-pass verdict" changed. Every verdict in Appendix A is therefore conditional on an
  artifact the text says is not evidence. Also, "the *corrected* verdicts" presumes the second pass
  was right; "second-pass verdicts" is the neutral term. Keep the disclaimers and add the dependency.
- The classification is single-rater and does not say so; its reliability is unaddressed. Note it as
  a limitation. An adversarial reviewer asserted the register *requires* an independent second review
  of the branch dispositions — I checked, and that is not supported: every "independent review"
  mention in the document concerns Studies 2 and 3. Reported here only in the form the evidence bears.
- "The reference audit" is an uncited external document. It is relied on twice — in the References
  preamble and in Appendix B — for the verification claim, but is neither included nor identified.
  This is the same class of dangling pointer as the "reference proposal" clause this revision just
  removed. Either include it as an appendix or name it as a companion file.
- "No corpus size to report" reads more absolutely than intended, though it conceals nothing: the
  very next sentence discloses the 62-reference anchor set and the working per-question map. Scoping
  it to "no protocol-derived corpus size" removes the ambiguity. An adversarial reviewer called this
  concealment; that is overstated and I am not carrying it as such.

## Action list

Correct three factual statements against the project's own documents: the "not yet frozen" claim;
"per-family date bounds" in all three places; the experiment-register description.

Rewrite one substantive passage: the gap conjunction in §1.8 and the abstract — name the
load-bearing conjunct, drop the tautological "may or may not", state the falsifier.

Adjust wording: "corrected verdicts" to "second-pass verdicts", plus one clause acknowledging that
Appendix A's verdicts are conditional on the prototype; add a single-rater limitation note; identify
or attach the reference audit; scope "no corpus size" to the protocol.

Leave alone: everything the integrity suite passed, the 61/62 formulation, the spelling conversion,
and every fix already applied.

## Bottom line

The three items left open last time are closed or honestly disclosed, and the candidate went further
than asked — downgrading his own protocol status, narrowing his own negative claims, and volunteering
both the prototype dependency and the register's unauditability. That instinct is the most valuable
thing in this document and should not be discouraged by the score.

The irony of this revision is that its three new factual errors all come from over-correcting: the
protocol *is* frozen in the sense its own register means, and the document now says otherwise. Fix
those by restoring accuracy rather than by claiming more.

The one item needing real thought rather than a wording change is the gap conjunction. It is the
load-bearing sentence of the whole proposal, and as written a committee member can dismiss it as
either trivially true or unfalsifiable. Naming the single conjunct that carries the deficit, and its
falsifier, would close the last substantive weakness in an otherwise disciplined document.
