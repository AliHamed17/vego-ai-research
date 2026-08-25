# Enhancement Prompt v3 — VEGO-AI Doctoral Proposal

Supersedes `proposal-enhancement-prompt-v2-2026-08-25.md`. Adds the three things Ali asked for on
2026-08-25: an anchored three-year timeline, a hard page budget of 25–28 pages, and a serious
visualization programme. Carries forward the outstanding repairs from v2, plus one new item from the
foundation-manuscript verification.

Current state: 30 pages, 11 figures, 16 tables, scored 91/100
(`doctoral-proposal-2026-08-25-rev2-review.md`).

## Prompt

```text
You are producing the next revision of the VEGO-AI doctoral research proposal (currently 30 pages,
11 figures, 16 tables). This revision has three headline goals: anchor the work plan to real dates,
bring the document to 25–28 pages, and raise every visual to publication quality. It also carries a
set of specific repairs. Treat the visual work as the centre of this revision, not as decoration.

DELIVERABLE FORMAT

There is no editable source in the repository; the proposal exists only as a PDF. Do not stop for
this and do not edit the PDF as if it were source. Produce a markdown deliverable with one entry per
change:

    ## <section or figure> — <one-line description>
    CURRENT:  <exact text or figure description as it stands>
    REPLACE:  <exact replacement text, or the full figure specification>
    REASON:   <one or two sentences>

For figures, the REPLACE block must be a complete, buildable specification: the diagram type, every
node and edge with its exact label, the layout, the colour and line semantics, and the caption. Where
possible also emit the figure as source a build can consume — Mermaid, Graphviz DOT, or TikZ — so the
diagram is version-controllable rather than a screenshot. Extract current text with pypdf; do not
work from memory.

HARD RULES

1. Never weaken the evidence boundary. These must remain stated and true: EXP-005
   generalization-safe expert labels incomplete, so accuracy, generalization and integrated-benefit
   claims stay blocked; zero of six medical entry gates satisfied; zero of five literature query
   families executed; independent reviewers, raters and implementer not recruited; supervisor
   approval of the research-question wording not recorded. Never add an accuracy, generalization,
   expert-effort, transfer-safety or clinical claim. Compression must never be achieved by deleting
   a limitation, a non-claim, or an open-gate disclosure.
2. Do not over-correct. Every factual error in the previous revision came from making the work sound
   weaker than it is. The repairs in Part 4 restore accuracy; they do not add caution.
3. Do not fabricate. If a change needs a fact you cannot verify in the repository or against a
   publisher record, leave the current text and say what you could not confirm. Never invent counts,
   dates, approvals, or names.
4. Preserve integrity: 62 references numbered 1–62 with no gaps, every in-text citation resolving,
   no uncited entry, figures and tables ascending in reading order, every table-of-contents page
   number correct, no dangling section cross-reference.
```
```text
PART 1 — ANCHOR THE TIMELINE TO REAL DATES

Chapter 5 currently says "semester-aligned blocks over three years" and Table 11 runs Semester 1 to
Semester 6, but the document contains NO calendar dates anywhere. Anchor it as follows. These dates
are confirmed and are not to be altered.

The three doctoral years run OCTOBER 2027 to OCTOBER 2030.

October 2026 to October 2027 is a PREPARATORY YEAR and is explicitly NOT one of the three years. It
covers proposal completion, supervisor approval, and candidacy. Show it on the timeline figure as a
visually distinct pre-phase band, clearly labelled as preparatory and outside the three-year count,
so no reader mistakes it for Semester 1.

Semester mapping to apply in Table 11, Figure 10, and anywhere else periods are named:

    Preparatory   Oct 2026 – Oct 2027   proposal, approval, candidacy (not one of the three years)
    Semester 1    Oct 2027 – Mar 2028
    Semester 2    Apr 2028 – Sep 2028
    Semester 3    Oct 2028 – Mar 2029
    Semester 4    Apr 2029 – Sep 2029
    Semester 5    Oct 2029 – Mar 2030
    Semester 6    Apr 2030 – Sep 2030
    Submission and defence   by Oct 2030

Keep the existing activity and output content of Table 11 unchanged; only add the date range to each
period label. The dependency logic in Chapter 5 is sound and must survive.

Add one sentence to Chapter 5 stating the anchor explicitly, for example: "The plan is anchored to a
three-year period running October 2027 to October 2030; the preceding year, October 2026 to October
2027, covers proposal completion, approval and candidacy and is not counted among the three."

MEDICAL EXTENSION ON THE TIMELINE. Keep it as a dashed bar marking it conditional, off the critical
path, and gated. Add an explicit go/no-go decision point to the figure, placed at the END OF
SEMESTER 4 (September 2029). Rationale to state in the caption or adjacent text: Study 3's target
evaluation in Semester 5 is where a medical scenario would first be needed, so the decision must be
made before Semester 5 begins, and a no-go leaves the full non-medical path intact. The decision
point must be visually distinct from the activity bars — a marked milestone, not another bar. Do not
imply any gate has been satisfied; zero of six are.
```
```text
PART 2 — THE VISUALIZATION PROGRAMME (the centre of this revision)

Treat the eleven figures as a single designed system, not eleven separate pictures. A reader should
be able to learn the visual language once, in Figure 1, and then read every later figure without
re-learning it. Put real effort here.

GLOBAL STANDARDS — apply to all eleven figures without exception.

1. One visual language, defined once and obeyed everywhere. Fix the meaning of every shape, line and
   colour before drawing anything, state it in a short legend, and never reuse a form for a second
   meaning. Suggested and consistent with the document's own logic:
   - rectangle = artifact or record; rounded rectangle = process or agent; diamond = decision;
     cylinder = store; parallelogram = human judgment input.
   - solid line = committed or existing flow; dashed line = conditional, proposed, or gated;
     dotted line = information reference rather than control flow.
   - one accent colour for the human-judgment layer this doctorate adds; one neutral for the
     existing VEGO-AI baseline; one muted tone for anything conditional or out of scope. The reader
     must be able to see at a glance what is new versus what already exists.
2. Colour must be redundant, never load-bearing on its own. Every distinction carried by colour must
   also be carried by shape, line style, position or label. Test by rendering greyscale: if any
   figure becomes ambiguous, it fails. Use a colourblind-safe palette; avoid red/green as the sole
   contrast.
3. Vector only. Produce SVG or PDF figures, or emit Mermaid/DOT/TikZ source that builds to vector.
   No screenshots, no raster exports, nothing that blurs when zoomed or printed.
4. Typography matches the body text. Use the document's font family in figures; set labels no
   smaller than roughly 8pt at final print size; never rely on text below 7pt. No all-caps blocks
   except for short status tags.
5. Every figure must survive black-and-white printing on A4 and remain legible at 100% zoom on a
   laptop. Supervisors print things.
6. No chrome. No drop shadows, gradients, 3D effects, clip art, or decorative icons. Every mark on
   the page must carry information. Density is fine; ornament is not.
7. Caption discipline, which the document already does well and must keep: state what the figure
   shows, name the source, and mark author-generated synthesis as such. Where a figure is redrawn
   from the foundation manuscript, say so. Where it is the candidate's own design synthesis, say so.
   Never let a figure imply evidence the text does not license.
8. Each figure must be readable in one pass. If a figure needs more than roughly nine primary nodes
   or more than two nesting levels, split it or move detail to the adjacent table. Prefer left-to-
   right or top-to-bottom flow; avoid crossing edges; align to a grid.
9. Accessibility: give every figure alt text of one or two sentences stating its actual claim, not
   its title.
```
```text
PER-FIGURE BRIEF. Redraw all eleven. The four marked PRIORITY carry the most argumentative weight
and should receive the most effort.

Figure 1 (p.5) — "Six readings of one observed model difference". PRIORITY. CORRECTED 2026-08-26:
  the earlier "four readings" brief was wrong; §1.7's Shift Supervisor example gives six readings
  verbatim, not four, so use six. This is the document's opening argument and the reader's first
  contact with the visual language, so it must be the most carefully made image in the proposal.
  Show ONE concrete model fragment once, then six labelled readings of it, verbatim from §1.7:
  defensible abstraction of an unnamed role; modeling-language error; domain misconception about
  authorization; genuine ambiguity in the task description; gap in the guideline; legitimate
  local/pedagogical decision by the instructor. A one-to-six fan (radial or a vertical stack of six)
  works better than a quadrant here, since six does not tile evenly. Make the point visible without
  the caption: the artifact is identical in all six, only the interpretation differs, and none is
  privileged — keep every arrow the same weight. Use the real motivating example from §1.7 (the Shift
  Supervisor actor) rather than an abstract placeholder, so Figure 1 and the §1.7 text reinforce each
  other; the reader meets the same concrete case again nine pages later.

Figure 2 (p.6) — "The four-agent VEGO-AI baseline". Dataflow pipeline: Language Advisor, Domain
  Advisor, Model Inspector, Variability Explorer, with the artifacts passed between them (language
  template, reference guidelines, compliance vector, uncovered-fragment audit, variability patterns)
  labelled on the edges. Mark the refinement loop back to the Domain Advisor. Caption must keep
  "redrawn from the supplied foundation manuscript [1]". Critically: shade or outline where the
  doctoral layer will attach, so the reader sees the baseline and the gap in one image, but keep the
  doctoral layer visually secondary here — it is developed later.

Figure 3 (p.11) — "Established research streams and the residual problem". Convergence figure: four
  or five named streams flowing toward a single residual gap. Do not draw it as a Venn diagram of
  overlapping fields; that overstates integration. Draw streams that arrive at, but do not close, a
  marked opening.

Figure 4 (p.11) — "Three residual gaps to research questions". Straight mapping, three to three.
  Keep it small and deliberately plain. If Figures 3 and 4 sit on the same page and repeat each
  other, merge them into one figure with two panels and reclaim the space for the page budget.

Figure 5 (p.15) — "Sub-questions to artifacts, evaluations, and outputs". PRIORITY. This is the spine
  of the whole programme and the single most information-dense figure. Four columns: sub-question,
  primary artifact, evaluation, planned output. Three rows for SQ1/SQ2/SQ3 plus the integrated
  evaluation as a distinct fourth row that visibly consumes the other three. Keep row alignment
  strict so the reader can scan either across one study or down one column. This figure and Table 5
  must not duplicate each other; if they do, cut the table.

Figure 6 (p.17) — "Study 1 review policy, signal set, evaluation principle". PRIORITY. Must show all
  eight declared signals as named inputs — claim-level uncertainty, consequence, novelty, evidence
  quality, cross-agent disagreement, expected future reuse value, reviewer competence, queue
  conditions — feeding a policy that emits the six routing actions (immediate qualified review,
  queue, batch review, audit sample, autonomous with logging, blocked). Show the attention budget as
  an explicit constraint on the policy, not as an afterthought, since matched-budget evaluation is
  the whole point of P1. Show the hard rules as a bypass path.

Figure 7 (p.18) — "Study 2 governed-judgment record and lifecycle". Two-part figure: the record's
  field groups on one side, and a genuine state machine on the other with the lifecycle states and
  the transitions between them (created, validated, contested, superseded, expired, revoked). Draw it
  as a state machine with labelled transitions, not as a list of states in boxes.

Figure 8 (p.19) — "Study 3 controlled-reuse and capability-gap decision procedure". PRIORITY. A
  decision flow that makes the four separations §1.6 argues for visually unmistakable, as four
  sequential gates: similarity found, applicable to this case, requester authorized, still valid —
  and then the distinct fourth question of whether reuse actually helps. End in the three outcomes:
  reuse permitted, local quirk, transferable capability-gap candidate. The capability-gap branch must
  show the four-part declaration test as a guard, not as a single arrow.

Figure 9 (p.21) — "Expert-review scores from the foundation manuscript". The only true data chart.
  Small multiples or a grouped bar across the four settings (ch-ucd, ch-cd, pw-ucd, pw-cd) showing
  compliance vector against uncovered audit. Keep the y-axis at 0–1 and do not truncate it; the
  contrast between the two measures is the point and truncation would exaggerate it. Retain the
  caption's existing honesty about n=16, four per setting, and no dispersion reported.

Figure 10 (p.23) — "Three-year plan". PRIORITY, and now the most-changed figure. A proper Gantt or
  swimlane over the anchored dates from Part 1. Swimlanes by workstream (Study 1, Study 2, Study 3,
  integrated evaluation, literature review, publications), time on the x-axis from Oct 2027 to Oct
  2030. Show the preparatory year as a distinct leading band, clearly outside the three years. Mark
  the three paper submissions and the defence as milestones. Show the medical extension as a dashed
  bar with the go/no-go milestone at September 2029. Show the dependency arrows that Chapter 5's
  text describes, because the dependency logic is the reason the plan is ordered as it is.

Figure 11 (p.27) — "Where the taxonomy meets this research, and where it stops". Two-column contrast:
  covered on the left, absent on the right, with the four branches on the left and the eleven missing
  concepts grouped on the right. The asymmetry is the argument, so let the right column visibly
  dominate. This doubles as the slide Prof. Reinhartz-Berger asked for, so it must stand alone
  without the surrounding text.
```
```text
PART 3 — PAGE BUDGET: 25 TO 28 PAGES

The document is 30 pages and must come down to 25–28. Note the tension: Part 2 will make several
figures larger and denser, so the space has to come from prose and table consolidation. Do not hit
the budget by shrinking margins, reducing the body font, or cramming figures.

Where to find the pages, in order of preference:

1. Consolidate the outcome-measure tables. Tables 6, 7 and 8 (Study 1, 2, 3 primary outcomes) share
   a structure. Merge into one table with a Study column, keeping every measure and its definition.
   Likely saving: about one page.
2. Merge Tables 13 and 14 (branch-level and dimension-level disposition), or make Table 14 the single
   table and fold the branch verdict into it as a grouping column. Likely saving: half a page.
3. Merge Figures 3 and 4 into a two-panel figure if they repeat each other on page 11.
4. Remove duplication between Figure 5 and Table 5, keeping whichever carries the layer separation
   better — probably the figure.
5. Compress the abstract's final third. It states the non-claims twice over; state them once, keeping
   all four items (accuracy, expert effort, safe reuse, clinical validity).
6. Tighten Chapter 1's prose, which is the longest chapter. Target redundancy between §1.8's
   synthesis and the individual section summaries that precede it, and the two places where the gap
   statement appears at different scopes. Do not cut the citations or the caveats.

WHAT MUST NOT BE CUT TO SAVE SPACE, under any circumstances: the section summaries and their
established/open two-part structure; any non-claim in the abstract; Table 10's evidence gating; Table
16's open-decisions record in Appendix B; the disclosure that zero searches have been run; the
statement that supervisor approval is not recorded; the count-discrepancy note; Appendix A's
substance; any caption's provenance statement.

Report the final page count and where each saved page came from.
```
```text
PART 4 — REPAIRS CARRIED FORWARD (all verified; apply exactly)

4a. The protocol IS frozen; the document wrongly says it is not. In §4.2 and Appendix B Table 16,
    replace "The database-specific Boolean syntax has not been written, so the protocol is not yet
    frozen and no query has been executed" with: "The five query families and their canonical Boolean
    expressions are frozen and registered; the per-platform field wrappers and filters are recorded
    at execution. No query has been executed." The project's own search register states it "freezes
    the first five literature-query concepts", heads its §2 "Exact frozen protocol queries", and says
    the code blocks are "the exact canonical Boolean expression". Keep the following sentence about
    there being no screening or inclusion counts.

4b. "Per-family date bounds" is wrong in three places (§3.2 summary, §4.2, Appendix B Table 16). The
    register uses a single 2015–2026 window across all five families with a documented snowballing
    exception. Replace each occurrence with "a single 2015–2026 window with a documented snowballing
    exception".

4c. The experiment register is described as holding more than it does. §4.3 says it "records for each
    run its inputs, frozen versions, procedure, and outputs". experiments/registry.md has seven
    columns: ID, Title, Status, RQ, Code/Config, Outputs, Notes — no procedure, no run date, no
    per-run version field. Replace with "which records for each registered experiment its identifier,
    status, research question, code and configuration paths, the location of any generated outputs,
    and the interpretation attached to it." Keep the sentence about it not being independently
    auditable.

4d. The central gap claim contains a tautology. In the Abstract and §1.8, the three conjuncts are the
    proposal's own design commitments in its own vocabulary, and "may or may not legitimately affect a
    later and differently situated case" excludes nothing. Rewrite so ONE conjunct carries the deficit
    and a falsifier is stated, for example: "The specific deficit is reviewer selection: no formulation
    in the literature reviewed here makes the choice of reviewer a function of assessed competence and
    authority over the contested fragment. A single study that did so would refute this claim." Drop
    "may or may not" entirely. Keep the existing caveat about the searches not having been run, and
    make Abstract and §1.8 consistent.

4e. Appendix A denies a dependency it relies on. Change "and the corrected verdicts are the ones given
    here" to "and the second-pass verdicts are the ones given here; they are conditional on that
    prototype." Keep all three prototype disclaimers. Add one sentence noting the classification is
    single-rater and its reliability has not been assessed.

4f. "The reference audit" is relied on twice but never included or identified: attach it as an
    appendix and add it to the table of contents, or name it as a companion file with its filename.
    And in §4.2 change "no corpus size to report" to "no protocol-derived corpus size".

4g. NEW, from direct verification of the foundation manuscript. The manuscript states its Phase C
    review was performed by TWO experts; §4.1 says only "expert review". Add the rater count, since
    two raters with no reported inter-rater statistic is a real limitation of the source and this
    doctorate proposes to strengthen exactly that kind of evidence. Suggested: "...compared Model
    Inspector outputs with review by two experts on a sample of 16 outcomes, four per setting."

4h. NEW, same source. The manuscript's counts are now verified: its Table 1 gives 46+47+44+41 = 178
    case models, and it states verbatim 26 patterns, eight substantial and eighteen occasional. The
    proposal's figures are therefore correct and it is the companion evidence package's 165/27 that
    requires explanation. Update the count-discrepancy note to say so rather than presenting both
    sides as equally uncertain — for example: "The manuscript's figures have been checked against the
    manuscript itself and are correct; the companion evidence package's differing counts of 165 and
    27 remain unexplained, and the implementation snapshot needed to reconcile them has not been
    supplied." Do not claim the discrepancy is closed.

PART 5 — WHAT ONLY ALI CAN DO (list these at the end; never fabricate progress)

Executing the five query families — zero have been run, and this is the ceiling on the entire
literature contribution. Obtaining the implementation snapshot to close the count discrepancy.
Supervisor approval of the research-question wording. Recruiting the independent reviewers, raters
and implementer required by Studies 2 and 3. Completing EXP-005 generalization-safe expert labels.

PART 6 — DO NOT CHANGE

Reference [4] Hevner "pp. 75-106" (an allegation of 75-105 was checked and refuted; Crossref's
publisher-deposited record, OpenAlex, and the DOI's own landing page all give 75-106). Reference [18]
Ahmed's middle initial "K. E. Ahmed" (DBLP canonical form; an earlier request to change it was wrong
and withdrawn). The "61 of 62 ... Reference [1] is unpublished" formulation. The British-to-American
spelling conversion, and do not re-run any global spelling replacement over the reference list, since
[13] Fervers correctly retains "Utilisation". The six chapter-appropriate section-summary label pairs.
Every statement of an open gate, unrecruited participant, unexecuted search, or unresolved count.

PART 7 — VERIFY AND REPORT

1. Final page count is between 25 and 28, with the source of each saved page named.
2. All eleven figures redrawn to the Part 2 standards; each is vector, greyscale-legible, and carries
   alt text and a provenance-accurate caption.
3. Figure 10 shows Oct 2027–Oct 2030, the preparatory year as a distinct band outside the three
   years, milestones for three papers and the defence, and the medical go/no-go at September 2029.
4. Table 11 period labels carry the new date ranges; activities and outputs unchanged.
5. References: 62 entries, 1–62, no gaps; every in-text [N] resolves; no entry uncited.
6. Figures and tables ascending after any merge; every table-of-contents page number correct; no
   dangling section cross-reference.
7. "not yet frozen", "per-family date bounds", and "may or may not" appear nowhere.
8. The abstract still states all four non-claims.

Report what you changed, quoting before and after; state which checks passed; and list anything you
could not do and why.
```
