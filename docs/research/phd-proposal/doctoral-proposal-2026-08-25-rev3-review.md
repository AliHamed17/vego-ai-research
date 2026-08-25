# Doctoral Proposal, third 2026-08-25 revision — Strict Review

**Reviewed:** `VEGO_AI_Doctoral_Proposal_Revised_20260825 (3).pdf` — 31 pages, 10 figures, 14 tables,
zero embedded raster images (all figures vector). Confirmed genuinely new: distinct sha256, and the
file dropped from 2.1 MB to 586 KB, consistent with replacing raster figures with vector.

**Method:** pypdf extraction; normalized sentence diff against the previous revision; full integrity
suite (bibliography, in-text citation resolution, figure/table ordering, TOC page numbers, section
cross-references, URLs and DOIs); overclaim scan; filesystem verification of every companion file
the document names; and a 16-agent adversarial pass over five substantively new passages across
three lenses, synthesized. Every agent claim about the document or repository was re-verified by me
before reporting; two were rejected as false and are recorded as such.

## Strict score: 84/100

**Not directly comparable to the previous 91, and the document did not get worse in the areas
previously measured.** All six outstanding repairs landed, the timeline is anchored exactly as
specified, and the corpus screening — missing from five consecutive artifacts — is now done. What
pulls the score down is three new HIGH defects, two of them introduced by this revision: content was
moved into companion files that do not exist, one scholarly claim is false about the literature
family it characterizes, and the anchor figure contradicts the text it cites.

| Dimension | Weight | Prev | Now | Why |
| --- | --- | --- | --- | --- |
| Evidence-boundary discipline | 25 | 25 | **21** | Boundary on research results intact, but artifacts are asserted to exist that do not, and one scope sentence is unfalsifiable as written |
| Citation integrity | 20 | 19 | **17** | Bibliography flawless (62/62, zero dangling, zero uncited); one false characterization of the learning-to-defer family |
| Fulfillment of instructions | 20 | 15 | **17** | Timeline anchored, corpus screening complete, visual system implemented; page budget missed; slide file absent |
| Resolution of recurring issues | 15 | 15 | **15** | All six repairs applied and verified |
| Internal consistency / production | 10 | 9 | **6** | TOC, references and cross-refs perfect; Figure 1 contradicts §1.7; A.2's content removed while completeness is claimed |
| Methodological / design-science rigor | 10 | 10 | **8** | Gap rewrite is excellent; screening criteria outrun their title-level evidence |
| **Total** | **100** | **91** | **84** | |

## What landed, verified

| Instruction | Result |
| --- | --- |
| Six outstanding repairs | **All applied.** "not yet frozen", "per-family date bounds", "frozen versions", "may or may not", "corrected verdicts" all now return zero hits; "two experts" added to §4.1 |
| Anchor the timeline | **Done exactly.** October 2027 – October 2030, preparatory year shown for context and explicitly "not counted among the three", go/no-go at September 2029 |
| Complete the corpus screening | **Done.** 90 unique papers, 22 relevant / 63 less relevant / 5 not relevant (sums to 90), criteria stated as fixed before screening, single-rater and title-level disclosed, findings marked corpus-scoped rather than field-scoped |
| Handle "missing" honestly | **Done, and correctly.** "A four-way disposition cannot be applied to papers, because no paper can be classified as missing. Papers were screened on a three-way scale, and missing was applied one level up, to research questions" |
| Rewrite the gap claim | **Done, and it is the best change in the revision.** See below |
| Visual programme | **Substantially done.** All figures vector, visual-language legend present and introduced on Figure 1, captions now match the briefs (Figure 5 "eight declared signals, a matched attention budget, six routing"; Figure 9 "anchored to October 2027 – October 2030") |
| Consolidate to reduce pages | **Partially.** Figures 11 to 10, tables 16 to 14, as advised |
| Page budget 25–28 | **Missed: 31 pages** |

Integrity is clean: 62 references numbered 1–62 with no gaps, every in-text citation resolving, no
uncited entry, figures and tables ascending, **zero TOC mismatches across 29 rows**, zero dangling
section cross-references, no bare URLs, 49 distinct DOIs.

## The best thing in this revision

The gap rewrite does something unusual and correct. It concedes its own previous formulation:

> "Put as a conjunction of everything this proposal happens to require, such a claim is close to
> unfalsifiable, and a committee is right to discount it."

then narrows to one testable deficit, names the nearest competitor rather than ignoring it, states
the falsifier, and bounds the claim to what was actually searched. That is exactly the right shape.

The corpus screening also produced a genuine structural finding that was not asked for: the four
branches are **not a partition** — 89 of the 90 papers appear in all four branch tables — so a
branch-by-disposition cross-tabulation is degenerate and reflects the repository's structure rather
than the papers. Disclosing that, rather than presenting a tidy but meaningless cross-tab, is good
scholarship.

## Defect 1 (HIGH) — three companion files are cited and none exists

The document now depends on three external files:

| File | Cited | Carries | Exists |
| --- | --- | --- | --- |
| `VEGO_AI_Appendix_A2_Dimension_Disposition_20260825.md` | 2× | The ten dimension-level dispositions, and for each of the eleven missing concepts the nearest existing dimension and why it falls short | **No** |
| `VEGO_AI_Reference_Audit_20260825.md` | 2× | Per-reference verification sources and the one disputed author name | **No** |
| `VEGO_AI_ACL_Taxonomy_Slide_20260825.pptx` | 1× | The standalone slide Prof. Reinhartz-Berger asked for | **No** |

Searched Downloads, Documents, Desktop, `concidium-local`, the repository, and every OneDrive
folder: only the four proposal PDFs exist. Nowhere does the document say these files are unwritten
or forthcoming; §A.2 says the detail "is recorded in" the companion file, and Appendix B cites the
audit file as "Sources:".

The first one is the serious case, because §A.2's table was removed to make room. **Six of the ten
dimension names no longer appear anywhere in the document** — Feedback Type, Feedback Subtype,
Feedback Granularity, Interaction Types, Orchestration Strategy, Orchestration Synchronization. Only
four survive, mentioned in passing prose. Meanwhile Appendix B asserts:

> "ACL taxonomy exercise: Branch, dimension, and corpus screening complete (§A.1–§A.4)."

So dimension-level completeness — one of the two halves of the assignment — is claimed on the
strength of a file a supervisor cannot open, while the evidence for it has been deleted from the
document. This is not an overclaim about research findings; the evidence boundary on results is
intact. It is an overclaim about the existence of artifacts, and it converts previously verifiable
in-document content into an unverifiable pointer.

**Fix:** either produce all three files and ship them with the PDF, or restore §A.2's dimension
table to the appendix and drop the pointer. Do not leave a completeness claim resting on a file that
does not exist. If the files are genuinely intended but not yet written, say so in Appendix B rather
than citing them as sources.

## Defect 2 (HIGH) — a false claim about the learning-to-defer literature

> "Learning-to-defer comes closest, since it conditions on expected human performance — but it
> chooses between a model and an undifferentiated human, not among people with different standing
> over the claim."

This is accurate about the three learning-to-defer papers the proposal actually cites — [33] Madras
et al., [34] Mozannar and Sontag, [35] Mozannar et al. are all single-expert formulations — but it
is stated as a property of the method family, and as such it is false. Multi-expert learning-to-defer
is an established branch that selects among differentiated, named experts using per-expert competence
estimates: Verma, Barrejón and Nalisnick, "Learning to Defer to Multiple Experts", AISTATS 2023
(PMLR v206); Mao et al., "Two-Stage Learning to Defer with Multiple Experts", NeurIPS 2023; and
subsequent work. Verified externally on 2026-08-26.

This matters disproportionately because the sentence is the sole disqualifier for the nearest
competing formulation, and the whole "narrower and testable" deficit rests on it. A committee member
who knows the L2D literature will raise it immediately.

Two claims made by an adversarial reviewer about this passage were **checked and rejected**: that
Verma et al. is already in the proposal's reference list (it is not — the only L2D entries are [33],
[34], [35]), and that §2.4 already describes learning-to-defer as routing "to one or more experts"
and studying "expert selection" (neither phrase appears anywhere in the document). The finding stands
on the external literature alone, not on any internal contradiction.

**Fix, and the candidate's real discriminator survives it intact:** concede the multi-expert branch
and relocate the distinction to authority. Something like — "Single-expert formulations choose between
a model and an undifferentiated human; multi-expert formulations do select among differentiated
experts, conditioning on per-expert estimated competence. What they condition on is an aggregate
competence profile over a task distribution, not assessed standing to settle the specific contested
fragment, and none models authority." Add the multi-expert papers to the references so the near-miss
is visibly screened rather than missed. Note also that the screened corpus could not have caught
this: the ACL human-agent survey is not where machine-learning-theory L2D papers live, which is
itself worth one sentence about the corpus's coverage limits.

## Defect 3 (HIGH) — Figure 1 contradicts §1.7 on the same example

Figure 1's caption reads "**Four** readings of the same observed model difference … The fragment is
the motivating example developed in §1.7", and its in-figure line reads "the artifact is identical in
all **four** — only the reading differs". Section 1.7 states "**Six** readings are available and the
system cannot choose between them from the artifact alone", and enumerates six.

Both counts are stated as closed. Nothing marks the four as a selection, so a reader who counts
cannot tell which is the document's position or whether the figure is a stale draft.

This one originated in my own specification, and I should say so plainly. My enhancement prompt of
2026-08-25 briefed Figure 1 as four readings; I corrected it to six on 2026-08-26 after checking §1.7
directly, but this PDF was built from the uncorrected brief. The document faithfully implemented what
it was given.

Worth noting which two were dropped, because the omission is directional rather than arbitrary: "a
gap in the guideline, which should have admitted this representation and does not" and "a legitimate
local decision that the instructor permits for a pedagogical reason". Both are the readings where the
fault lies outside the student. Dropping exactly those narrows the visible problem to "which
student-side explanation applies" and removes the case that most threatens the assumption that the
guideline is a sound label source — the hardest case for any artifact-only system, and the one
closest to this doctorate's own argument.

Fix: redraw with all six and retitle. If six will not fit legibly, retitle "Four of the six readings
enumerated in §1.7", change the in-figure line to "the artifact is identical under every reading",
and name the two omitted readings in the caption as omitted for legibility only. Either way, state
the canonical number once and cross-reference it from both places.

## Defect 4 (HIGH) — the contribution's scope is defined by its own success

> "It is comparative, and holds only where the proposed mechanisms beat simpler baselines at matched
> expert attention and matched evidence, so a null result narrows the thesis rather than being
> concealed."

As written, the validity region is the region where the proposal wins, so any condition where it
loses falls outside the scope the sentence carved out, and the claim cannot fail. Three things a
committee will ask for are missing: the comparison conditions are not fixed in advance, so which
conditions count as "where it holds" can be chosen after results are seen; "beat" has no metric,
margin, or decision rule; and "narrows" has no floor, so no pattern of results rejects the thesis.

This is conspicuous precisely because it is out of character — it is the one sentence in the passage
that protects the conclusion rather than disclosing a limit.

Fix: replace success-defined scope with pre-commitment. Fix baselines, conditions, primary metric and
the margin that counts as an improvement in the pre-registration; state a retention rule (for example,
improvement in at least k of n pre-registered conditions, below which the thesis is rejected rather
than re-scoped); and commit to reporting every pre-registered condition including those where the
proposal does not win. Drop "rather than being concealed" — name the commitment instead of
disclaiming the misconduct.

## Defect 5 (MEDIUM) — screening criteria outrun their evidence

The criteria are content-level determinations. Relevant requires that "the paper's own contribution
is a method, system, or study whose primary object is …"; Less relevant requires choosing among six
contribution types (benchmark, dataset, agent topology, orchestration mechanism, domain application,
training method). The disclosed evidence base is title-level.

Contribution type and "primary object" are generally not recoverable from a title, so the 22/63/5
dispositions are title-cued inferences presented as applications of substantive criteria. The
existing caveat bounds rater count and breadth but not this gap between criterion and evidence.

Fix: either state that dispositions are provisional title-level inferences pending abstract-level
confirmation, and report how many were confidently assignable from title alone; or screen the 22
relevant and 5 not-relevant at abstract level — 27 abstracts — which closes the gap for exactly the
categories that carry the argument.

## Smaller items

- Page budget missed: 31 pages against 25–28. In fairness the overrun is largely the corpus-screening
  appendix, which was the higher-value instruction, and that tension was mine to set up more clearly.
  Still, the target was stated and not met, and the merges achieved were real but insufficient.
- The "Reading the figure" explainer device appears exactly once, on Figure 1. Either apply it to
  every complex figure or drop it; used once it reads as an unfinished pattern.
- Appendix B's new self-disclosed row on the SQ2/SQ3 wording overlap is a genuine strength and should
  stay — it records a strict-review finding as an open supervisor decision rather than quietly
  resolving it.

## Bottom line

The two hardest instructions were met. The timeline is anchored correctly, and the corpus screening
that had been missing from five consecutive artifacts is complete, honest about its method, and
produced a real structural finding nobody asked for. The gap rewrite is the strongest single passage
in this document's history.

Against that, three HIGH defects need fixing before supervisors see it, and two are new. The
companion-file problem is the most damaging because it is invisible to a reader who trusts the
document: Appendix B says the dimension classification is complete, while the evidence for it has
been removed from the PDF and points at a file that does not exist. The learning-to-defer sentence is
the one a knowledgeable committee member will catch fastest. Figure 1's contradiction is mine in
origin and cheap to fix.

None of it requires new research. One needs three files produced or one table restored; one needs a
conceded paragraph and three added references; one needs a redraw; one needs a pre-registration
sentence.
