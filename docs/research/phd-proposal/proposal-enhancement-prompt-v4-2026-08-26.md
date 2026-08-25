# Enhancement Prompt v4 — VEGO-AI Doctoral Proposal

Keyed to `doctoral-proposal-2026-08-25-rev3-review.md` (84/100). Supersedes v3. The six v3 repairs
all landed and are not repeated here. This prompt fixes three HIGH defects introduced or exposed by
the third revision, one MEDIUM, and finishes the visual and page work.

## Prompt

```text
You are producing the next revision of the VEGO-AI doctoral research proposal (currently 31 pages,
10 figures, 14 tables). A strict review scored it 84/100. The previous revision succeeded at the two
hardest things — anchoring the timeline and completing the ACL corpus screening — so do not disturb
those. Fix what is listed and nothing else.

DELIVERABLE FORMAT

The proposal exists only as a PDF; there is no editable source in the repository. Do not stop for
this and do not edit the PDF as if it were source. Produce a markdown deliverable with one entry per
change:

    ## <section or figure> — <one-line description>
    CURRENT:  <exact text or figure description as it stands>
    REPLACE:  <exact replacement text, or the full figure specification>
    REASON:   <one or two sentences>

Extract current text with pypdf. Do not work from memory.

HARD RULES

1. Never weaken the evidence boundary. These must remain stated and true: EXP-005
   generalization-safe expert labels incomplete; zero of six medical entry gates satisfied; zero of
   five registered query families executed; independent reviewers, raters and implementer not
   recruited; supervisor approval of the research-question wording not recorded; the count
   discrepancy explained but not closed. Never add an accuracy, generalization, expert-effort,
   transfer-safety or clinical claim.
2. Do not claim an artifact exists unless it exists. This revision's worst defect was citing three
   companion files that are not on disk. If a file is not produced, do not cite it as a source.
3. Do not over-correct. Fixes 1 and 2 below make the document MORE accurate, not more cautious.
4. Do not fabricate. If a change needs a fact you cannot verify in the repository or against a
   publisher record, leave the current text and say what you could not confirm.
5. Preserve integrity, all currently perfect and all to be re-verified after editing: 62 references
   numbered 1-62 with no gaps (this rises if you add references under Fix 2), every in-text citation
   resolving, no uncited entry, figures and tables ascending, every table-of-contents page number
   correct, no dangling section cross-reference.
```
```text
FIX 1 (HIGH) — three cited companion files do not exist. Resolve this first.

The document cites three external files. None is on disk anywhere: not in Downloads, Documents,
Desktop, concidium-local, the repository, or any OneDrive folder.

  VEGO_AI_Appendix_A2_Dimension_Disposition_20260825.md   cited twice
  VEGO_AI_Reference_Audit_20260825.md                     cited twice
  VEGO_AI_ACL_Taxonomy_Slide_20260825.pptx                cited once

The first is the damaging one. Section A.2 was reduced to prose and now says the ten dimension
dispositions "are recorded in the companion file ... because the detail is reference material and
reads poorly at proposal density". As a result six of the ten dimension names appear nowhere in the
document at all: Feedback Type, Feedback Subtype, Feedback Granularity, Interaction Types,
Orchestration Strategy, Orchestration Synchronization. Meanwhile Appendix B still asserts "Branch,
dimension, and corpus screening complete (§A.1-§A.4)". Dimension-level completeness is therefore
claimed on the strength of a file a supervisor cannot open.

Choose ONE of these two resolutions and apply it consistently:

  Option A, preferred if the files can be produced now. Actually write all three files, ship them
  alongside the PDF, and add one line to Appendix B naming them as accompanying deliverables with
  their dates. The slide in particular was requested by name by Prof. Reinhartz-Berger, so producing
  it has independent value.

  Option B, if they cannot be produced now. Restore the ten-row dimension-disposition table to §A.2
  in the document, restore to §A.3 the "nearest existing dimension and why it falls short" column,
  delete all three companion-file citations, and change Appendix B's reference-verification row to
  describe the method without citing a file. Accept the resulting page cost; Fix 5 recovers it.

Whichever you choose, Appendix B must not claim any part of the exercise is complete on the basis of
material that is not readable by whoever holds the PDF.

FIX 2 (HIGH) — a false claim about the learning-to-defer literature.

Current text in §1.8: "Learning-to-defer comes closest, since it conditions on expected human
performance -- but it chooses between a model and an undifferentiated human, not among people with
different standing over the claim."

This is true of the three learning-to-defer papers the proposal cites -- [33] Madras et al., [34]
Mozannar and Sontag, [35] Mozannar et al. are all single-expert formulations -- but it is stated as a
property of the method family, and as such it is false. Multi-expert learning-to-defer selects among
differentiated, named experts using per-expert competence estimates. Verified externally: Verma,
Barrejon and Nalisnick, "Learning to Defer to Multiple Experts: Consistent Surrogate Losses,
Confidence Calibration, and Conformal Ensembles", AISTATS 2023, PMLR v206; and Mao et al., "Two-Stage
Learning to Defer with Multiple Experts", NeurIPS 2023.

This sentence is the sole disqualifier for the nearest competing formulation, so the whole "narrower
and testable" deficit rests on it, and a committee member who knows this literature will raise it
immediately.

Replace with a concession that relocates the discriminator to authority, which survives the
concession intact:

  "Learning-to-defer comes closest. Single-expert formulations choose between a model and an
   undifferentiated human [33], [34], [35]; multi-expert formulations do select among differentiated
   experts, conditioning on per-expert estimated competence [NEW1], [NEW2]. What they condition on is
   an aggregate competence profile over a task distribution, not assessed standing to settle the
   specific contested fragment, and none models authority. One study that routed by claim-specific
   competence and authority would refute this."

Add both papers to the reference list, renumbering as required, so the near-miss is visibly screened
rather than missed. Add one sentence to §A.4 noting that the screened corpus could not have surfaced
this branch, because the ACL human-agent survey is not where machine-learning-theory deferral papers
appear -- a real and useful limit on what corpus screening can establish.
```
```text
FIX 3 (HIGH) — Figure 1 contradicts §1.7 on the same example.

Figure 1's caption says "Four readings of the same observed model difference ... The fragment is the
motivating example developed in §1.7", and its in-figure line says "the artifact is identical in all
four -- only the reading differs". Section 1.7 says "Six readings are available and the system cannot
choose between them from the artifact alone", and enumerates six. Both counts are stated as closed
and nothing marks the four as a selection.

For the record: this originated in an earlier version of these instructions, which briefed the figure
as four readings. That brief was wrong and was corrected on 2026-08-26. The document implemented what
it was given; the fix below is the correction, not a criticism of the execution.

Preferred: redraw with all six panels and retitle "Six readings of the same observed model
difference". Change the in-figure line to "the artifact is identical under all six -- only the reading
differs". The six, verbatim from §1.7, are: a defensible abstraction of a role the description implies
without naming; a modeling-language error, where an actor is used and the notation calls for a role or
boundary element; a domain misconception about who authorizes what; genuine ambiguity in the task
description; a gap in the guideline, which should have admitted this representation and does not; and
a legitimate local decision the instructor permits for a pedagogical reason.

Fallback, only if six will not fit legibly: retitle "Four of the six readings enumerated in §1.7",
change the in-figure line to "the artifact is identical under every reading -- only the reading
differs", and add one caption sentence naming the two omitted readings and stating they are omitted
for legibility, not because they are less likely.

Note why the fallback is second-best. The two currently omitted readings -- the guideline gap and the
instructor-sanctioned local decision -- are exactly the two where the fault lies outside the student.
Dropping them narrows the visible problem to "which student-side explanation applies" and removes the
case that most threatens the assumption that the guideline is a sound label source, which is the
hardest case for any artifact-only system and the one closest to this proposal's own argument.

Either way, state the canonical number of reading categories once, in one place, and cross-reference
it from both the figure and §1.7.

FIX 4 (HIGH) — the contribution's scope is currently defined by its own success.

Current text in the abstract's bounding paragraph: "It is comparative, and holds only where the
proposed mechanisms beat simpler baselines at matched expert attention and matched evidence, so a null
result narrows the thesis rather than being concealed."

The validity region is the region where the proposal wins, so any losing condition falls outside the
scope the sentence carved out and the claim cannot fail. The comparison conditions are not fixed in
advance; "beat" has no metric, margin or decision rule; "narrows" has no floor, so no result rejects
the thesis. It is the one sentence in the document that protects the conclusion rather than disclosing
a limit, which makes it conspicuous against everything around it.

Replace with pre-commitment and a reporting commitment:

  "It is comparative. Baselines, comparison conditions, the primary metric, and the margin that counts
   as an improvement are fixed in the pre-registration before any run. The thesis is retained only if
   the proposed mechanisms improve on the baselines in a pre-registered majority of conditions at
   matched expert attention and matched evidence; below that threshold it is rejected rather than
   re-scoped. Every pre-registered condition is reported, including those where the proposal does not
   improve on a baseline."

Drop "rather than being concealed" -- name the commitment instead of disclaiming the misconduct. Check
§2.5's propositions and §3.6's integrated evaluation for the same success-defined pattern and apply
the same treatment where it appears.

FIX 5 (MEDIUM) — screening criteria outrun their title-level evidence, and the page budget.

§A.4's criteria are content-level: Relevant turns on "the paper's own contribution is a method,
system, or study whose primary object is ...", and Less relevant requires choosing among six
contribution types. The disclosed evidence base is title-level, and contribution type is generally not
recoverable from a title. The 22/63/5 dispositions are therefore title-cued inferences presented as
applications of substantive criteria.

Preferred: screen the 22 relevant and the 5 not-relevant at abstract level. That is 27 abstracts, it
closes the gap for exactly the categories that carry the argument, and it lets you report a
confirmation rate. Report any disposition that changes.

Minimum: state that dispositions are provisional title-level inferences pending abstract-level
confirmation, and report how many of the 90 were confidently assignable from title alone.

PAGE BUDGET. The document is 31 pages; the target was 25-28 and remains so. The overrun is largely the
corpus-screening appendix, which was the right thing to add, so recover the pages from prose rather
than by deleting evidence. Note that Fix 1 Option B adds roughly a page, so plan for that. Sources, in
order of preference: compress Chapter 1, which remains the longest chapter and still states the gap at
two different scopes; merge the Study 1/2/3 outcome tables into one table with a Study column if that
was not already done; and remove any remaining duplication between the programme-spine figure and its
neighbouring table. Never hit the budget by shrinking margins, reducing the body font, cramming
figures, or cutting a limitation, a non-claim, an open-gate disclosure, or a provenance caption.
```
```text
FIX 6 (LOW) — finish the visual system.

The visual programme largely landed: all figures are vector, the shape/line/colour legend is present
and introduced on Figure 1, and the captions now match their briefs. Two things remain.

The "Reading the figure" explainer block appears exactly once, on Figure 1. Used once it reads as an
unfinished pattern. Either add it to every figure a reader cannot parse in one pass -- the programme
spine, the Study 1 policy, the Study 3 gate procedure, and the Gantt -- or remove it from Figure 1 and
let the captions carry the load. Adding it to four more figures costs space, so if the page budget is
tight, remove it.

Re-verify the greyscale rule on every figure. Render each in greyscale and confirm no distinction
becomes ambiguous. The medical bar on the Gantt is the highest-risk case, because conditional status
is carried by colour there; confirm it is also carried by line style or an explicit label.

DO NOT CHANGE

- The anchored timeline: October 2027 to October 2030, the preparatory band shown for context and
  excluded from the three years, and the go/no-go milestone at September 2029. It is correct.
- The corpus screening totals 22 / 63 / 5 over 90 unique papers, unless Fix 5's abstract-level pass
  actually changes a disposition, in which case report the change explicitly.
- The finding that the four branches are not a partition, with 89 of 90 papers appearing in all four
  branch tables. It is correct, it was not asked for, and it is good scholarship.
- The gap rewrite's structure: conceding that the conjunction form is close to unfalsifiable, naming
  one testable deficit, and bounding the claim to the anchor set and screened corpus. Only the
  learning-to-defer sentence inside it changes, per Fix 2.
- Reference [4] Hevner "pp. 75-106", reference [18] Ahmed's middle initial "K. E. Ahmed", the
  61-of-62 verification formulation, and the British-to-American spelling conversion. All previously
  verified; do not re-open them.
- Appendix B's self-disclosed row on the SQ2/SQ3 wording overlap. Recording a strict-review finding
  as an open supervisor decision is a strength.
- Every statement of an open gate, an unrecruited participant, an unexecuted query family, or the
  unresolved count discrepancy.

WHAT ONLY ALI CAN DO — list these at the end and never fabricate progress on them.

Executing the five registered query families; zero have been run, and this remains the ceiling on the
literature contribution. Obtaining the implementation snapshot that would close the 178/26 versus
165/27 count discrepancy. Supervisor approval of the research-question wording, including the SQ2/SQ3
overlap decision. Recruiting the independent reviewers, raters and implementer that Studies 2 and 3
require. Completing the EXP-005 generalization-safe expert labels.

VERIFY AND REPORT

1. Every companion file cited in the document exists on disk, or no companion file is cited at all.
   State which resolution you chose for Fix 1.
2. No sentence characterises learning-to-defer as choosing only between a model and an
   undifferentiated human; the multi-expert papers are cited and in the reference list.
3. Figure 1's count and §1.7's count agree, and the canonical number is stated once.
4. No scope sentence defines validity by where the proposal wins; a retention threshold and a
   full-reporting commitment are stated.
5. §A.4 states the evidence level its criteria actually rest on.
6. Final page count is 25-28, with the source of each saved page named.
7. References: complete sequence with no gaps after any additions; every in-text citation resolves;
   no entry uncited.
8. Figures and tables ascending; every table-of-contents page number correct; no dangling section
   cross-reference; every figure legible in greyscale.

Report what you changed with before and after for each fix, state which checks passed, and list
anything you could not do and why.
```
