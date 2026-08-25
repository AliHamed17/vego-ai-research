# Codex Task — Visual System for the VEGO-AI Doctoral Proposal

Owner: Codex. Requested by Ali, 2026-08-26. Companion to
`proposal-enhancement-prompt-v4-2026-08-26.md`, which covers text repairs; this file covers
everything visual and is the authority for it.

Target document: `VEGO_AI_Doctoral_Proposal_Revised_20260825 (3).pdf` — 31 pages, 10 figures,
14 tables, reviewed at 84/100 in `doctoral-proposal-2026-08-25-rev3-review.md`.

## Task

```text
You are taking ownership of the entire visual system of a doctoral research proposal: every figure,
diagram, chart, plot, timeline and visual table treatment in the document. The goal is a set of
figures that a doctoral committee reads as professional, precise, and effortless — comprehensive
without being dense, and correct in every label.

START BY READING THE CURRENT STATE. Do not assume you are starting from zero.

The previous revision already did real visual work and you must not undo it:
- All ten figures are already vector. The PDF contains zero embedded raster images.
- A shape/line/colour legend already exists and is introduced on Figure 1.
- Captions already carry provenance ("redrawn from the supplied foundation manuscript [1]",
  "Author-generated synthesis", and so on). That discipline is deliberate — keep it.
- Figure and table numbering is already in ascending reading order, the table of contents is
  accurate to the page across 29 rows, and there are no dangling cross-references. Do not break any
  of this; re-verify all of it after your changes.

Extract the current figures and their exact labels before redrawing anything. Work from the actual
document, not from this brief's summaries.

YOU ARE ENCOURAGED TO USE EXTERNAL TOOLS. Use whatever produces the best result, and connect to it
directly rather than hand-drawing.

Recommended, with what each is genuinely best at:
- D2 (terrastruct.com/d2) — modern diagram language with strong automatic layout and good defaults;
  excellent for the pipeline, the spine, and the gate procedures. Renders to SVG/PDF.
- Graphviz DOT — best when you need precise control of ranks and edge routing without crossings;
  strongest for the state machine.
- Mermaid — fastest iteration, native gantt support, and easy to keep in version control. Render
  via mermaid.live, the mmdc CLI (npm i -g @mermaid-js/mermaid-cli), or the VS Code extension.
- TikZ/PGF — if the final document is LaTeX, this makes figures native document code rather than
  imported assets, with typography guaranteed to match the body text.
- matplotlib, plotnine, or Vega-Lite — for the one true data chart (Figure 8) and any new chart.
  Use whichever gives you exact control of axis limits.
- Inkscape (CLI: inkscape --export-type=pdf) — for final SVG cleanup, text-to-path where a font
  cannot be embedded, and precise bounding boxes.
- SVGO — to strip editor cruft from exported SVG without changing appearance.

For colour and accessibility, use real tools rather than judgement:
- Okabe-Ito or ColorBrewer for the palette. Both are designed colourblind-safe.
- Coblis or an equivalent colourblind simulator to check deuteranopia and protanopia.
- A WCAG contrast checker for every text-on-fill combination; target at least 4.5:1 for body-size
  label text.

If you find a better tool than any of these, use it and say which and why in your report.
```
```text
THE VISUAL LANGUAGE — one system, defined once, obeyed everywhere

A reader should learn the language once, at Figure 1, and read every later figure without
re-learning it. Fix the semantics before drawing, state them in the legend, and never reuse a form
for a second meaning.

  Shapes:  rectangle = artifact or record; rounded rectangle = process or agent; diamond = decision;
           cylinder = store; parallelogram = human-judgment input.
  Lines:   solid = committed or existing flow; dashed = conditional, proposed, or gated;
           dotted = information reference rather than control flow.
  Colour:  one neutral for the existing VEGO-AI baseline; one accent reserved exclusively for the
           human-judgment layer this doctorate adds; one muted tone for anything conditional, gated,
           or out of scope. A reader must see at a glance what is new versus what already exists.

Non-negotiable rules:
1. Colour is never load-bearing alone. Every distinction carried by colour must also be carried by
   shape, line style, position, or label. Render every figure in greyscale and confirm nothing
   becomes ambiguous. The conditional medical bar on the timeline is the highest-risk case.
2. Vector only, and text as real text where the font can be embedded so it stays searchable and
   selectable. Convert to paths only where embedding fails.
3. Typography matches the body text: same family, labels no smaller than about 8pt at final print
   size, nothing below 7pt, no all-caps blocks except short status chips.
4. No chrome. No shadows, gradients, 3D effects, clip art, or decorative icons. Every mark carries
   information. Density is acceptable; ornament is not.
5. One-pass readability. If a figure needs more than about nine primary nodes or more than two
   nesting levels, split it or move detail into the adjacent table.
6. Prefer left-to-right or top-to-bottom flow. No crossing edges. Align to a grid.
7. Every figure must survive A4 black-and-white printing and remain legible at 100% on a laptop.
8. Every figure gets alt text of one or two sentences stating its claim, not its title.
9. Captions keep their provenance statement and never imply evidence the text does not license.

THE TEN FIGURES

Figure 1 — Readings of one observed model difference. HIGHEST PRIORITY, and it currently contains a
  factual error you must fix. The figure says "Four readings" and its in-figure line says "identical
  in all four", but §1.7 of the same document says "Six readings are available" and enumerates six.
  Redraw with all six, verbatim from §1.7: a defensible abstraction of a role the description
  implies without naming; a modeling-language error, where an actor is used and the notation calls
  for a role or boundary element; a domain misconception about who authorizes what; genuine
  ambiguity in the task description; a gap in the guideline, which should have admitted this
  representation and does not; and a legitimate local decision the instructor permits for a
  pedagogical reason. Retitle to "Six readings of one observed model difference" and change the
  in-figure line to "the artifact is identical under all six". One shared origin node, six equal
  siblings, identical arrow weight — no reading is privileged, and the figure must not converge back
  to an answer. This is the reader's first contact with the visual language, so it is the most
  carefully made image in the document.

Figure 2 — The four-agent VEGO-AI baseline. Pipeline: Language Advisor, Domain Advisor, Model
  Inspector, Variability Explorer, with artifacts labelled on the edges and the refinement loop back
  to the Domain Advisor drawn explicitly. Shade where the doctoral layer attaches, but keep that
  band visually secondary — it is developed later. Caption must retain "redrawn from the supplied
  foundation manuscript [1]".

Figure 3 — Established streams, the opening none closes, and the gap-to-question mapping. This
  figure already merges two earlier ones. Draw the residual gap as visibly open — dashed outline,
  unfilled — not as a closed box, so the convergence does not read as closure.

Figure 4 — The programme spine. HIGH PRIORITY, most information-dense figure in the document. Four
  columns: sub-question, primary artifact, evaluation, planned output. Rows for SQ1, SQ2, SQ3, and
  the integrated evaluation drawn as a fourth row that visibly consumes the other three. Strict row
  alignment so a reader can scan across one study or down one column.

Figure 5 — The Study 1 review policy. HIGH PRIORITY. All eight declared signals as named inputs:
  claim-level uncertainty, consequence, novelty, evidence quality, cross-agent disagreement,
  expected future reuse value, reviewer competence, queue conditions. Six routing actions out:
  immediate qualified review, queue, batch review, audit sample, autonomous with logging, blocked.
  The matched attention budget must be drawn as a constraint bounding the policy, not as a ninth
  input — matched-budget comparison is the entire point of proposition P1. Show the hard rules as a
  bypass path.

Figure 6 — The Study 2 record and lifecycle. Two panels: field groups on one side, a genuine state
  machine on the other with labelled transitions between created, validated, contested, superseded,
  expired and revoked. Draw transitions as transitions; do not render states as a list of boxes.

Figure 7 — The Study 3 reuse procedure. HIGH PRIORITY. Five sequential gates, three outcomes, and
  the capability-gap branch guarded by the four-part declaration test drawn as four AND-gated checks
  rather than a single arrow. The reader must be able to see that similarity, applicability,
  authorization and current validity are four separate questions.

Figure 8 — Expert-review scores from the foundation manuscript. THE ONLY TRUE DATA CHART. Grouped
  bars or small multiples across ch-ucd, ch-cd, pw-ucd, pw-cd, comparing compliance vector against
  uncovered-fragment audit. Data: 0.80/0.55, 0.96/0.81, 0.83/0.55, 0.92/0.88. Y-axis fixed 0 to 1
  and never truncated — the gap between the two measures is the finding, and truncation would
  exaggerate it. Both series in the neutral "existing" colour, since these are someone else's
  reported results. Keep the caption's existing honesty about n=16, four per setting, two experts,
  and no dispersion reported.

Figure 9 — The three-year plan. HIGH PRIORITY. Gantt or swimlane, October 2027 to October 2030, with
  the October 2026 to October 2027 preparatory year as a visually distinct leading band clearly
  labelled as outside the three years. Swimlanes by workstream. Milestones as diamonds for the three
  paper submissions and the defence. The medical extension as a dashed conditional bar with a
  go/no-go milestone at September 2029, visually distinct from committed bars. Draw the dependency
  arrows between studies — Chapter 5's prose argues from that dependency, so it must be visible.
  Note that Mermaid's gantt cannot draw inter-lane dependency arrows or dashed task borders; if you
  use Mermaid, use it to verify dates and then rebuild the final figure in D2, TikZ, or custom SVG.

Figure 10 — Where the taxonomy meets this research and where it stops. Two columns: four branches on
  the left, eleven missing concepts on the right, with the right column given roughly 60% of the
  width so the asymmetry is the argument. Must stand alone without surrounding text — it doubles as
  the standalone slide requested by Prof. Reinhartz-Berger.
```
```text
THE FOURTEEN TABLES — where a chart would genuinely serve the reader better

Most of these tables are text matrices and must stay tables; converting them to graphics would lose
information and look decorative. Do not convert Tables 1, 2, 3, 4, 7, 9, 11 or 14. They carry
definitions, rejection conditions, decision rules and status records that read better as text.

One genuine chart opportunity exists, and it is the strongest new-visual candidate in the document:

  Tables 12 and 13 — the ninety-paper screening result (22 relevant / 63 less relevant / 5 not
  relevant) and the per-research-question coverage. Two adjacent tables of counts are harder on the
  eye than one small chart. Build a single compact figure: a horizontal stacked bar for the
  three-way disposition, with a small per-question panel beneath showing coverage by SQ1, SQ2 and
  SQ3. This is where the "missing" category becomes visible, since missing applies at question level
  rather than paper level — make that distinction visually explicit rather than relying on a
  footnote. Keep both tables if the numbers are needed for citation, or replace the weaker of the
  two if the chart carries it.

  Constraint on that chart: the underlying screening is single-rater and title-level, and the
  document says so. The chart must not imply more precision than that. Do not add error bars, do not
  imply a sampling distribution, and keep the caption's method disclosure.

Two further candidates, lower priority and only if the page budget allows:

  Table 5, outcome measures for the three studies, could gain a small visual key showing which
  measure belongs to which study, if the merged table has become hard to scan.

  Table 8, the semester-aligned activities, is the textual twin of Figure 9. Check them against each
  other line by line; every period label, date range and output must agree exactly. If they disagree,
  the table is authoritative for content and the figure for chronology — reconcile and report.

CORRECTNESS IS PART OF THIS TASK, NOT SEPARATE FROM IT

Every label you draw is a factual claim. Verify each against the document text rather than against
this brief:
- The eight signal names in Figure 5 must match §3.3 exactly.
- The six routing actions must match §3.3 exactly.
- The lifecycle states in Figure 6 must match the contract fields listed in §3.4.
- The five gates and three outcomes in Figure 7 must match §3.5.
- Every date in Figure 9 must match Table 8, and both must match the anchored window October 2027 to
  October 2030 with the preparatory year excluded from the three.
- Figure 8's four data pairs must match the values reported in §4.1.
- Figure 10's eleven concepts must match Table 11 exactly, in the same order.
Report any discrepancy you find between a figure and the text rather than silently choosing one.
```
```text
DELIVERABLE AND SOURCE CONTROL

Do not hand back screenshots or a pile of images. For each figure deliver three things:

1. The diagram source — D2, DOT, Mermaid, TikZ, or the plotting script — as a text file under
   docs/research/phd-proposal/figures/, one file per figure, named fig-NN-slug.d2 (or .dot, .mmd,
   .tex, .py). These must be version-controllable and re-renderable by someone who is not you.
2. The rendered output as SVG and PDF, vector, with fonts embedded or text converted to paths where
   embedding fails. Standalone: no external stylesheet or font dependency at render time, so the
   file drops cleanly into LaTeX or Word without broken references.
3. A one-line render command per figure, so the whole set can be rebuilt in one pass. A single
   Makefile or shell script covering all figures is better than ten separate instructions.

Also deliver a short figures/README.md recording the palette hex values with their semantic
meanings, the font family and sizes, and the tool used per figure.

QUALITY GATES — run all of these and report each result

1. Greyscale: render every figure in greyscale. No distinction may become ambiguous. State pass or
   fail per figure.
2. Colourblind: run every figure through a deuteranopia and protanopia simulation. State pass or
   fail per figure.
3. Contrast: check every text-on-fill pair against WCAG. Report the lowest ratio found and confirm
   it is at least 4.5:1 at body-label size.
4. Print: export at final size, print or simulate A4 black-and-white, confirm every label is legible.
5. Zoom: confirm no blurring at 400%, which also confirms nothing raster slipped in.
6. Label correctness: confirm every label matches the document text per the list above.
7. Consistency sweep: view all ten figures side by side and confirm one visual language — same
   shapes for same meanings, same palette, same type sizes, same line weights.
8. Integrity: after any figure merge or addition, re-verify that figures and tables remain in
   ascending reading order, that the table of contents page numbers are still correct, and that no
   cross-reference dangles.

WHAT MUST NOT CHANGE

- The provenance statements in captions, including "redrawn from the supplied foundation manuscript
  [1]" on Figure 2 and "Author-generated" wherever it appears.
- Figure 8's y-axis at 0 to 1, untruncated, and its caption's disclosure of n=16, four per setting,
  two experts, no dispersion reported.
- The anchored timeline: October 2027 to October 2030, preparatory year shown for context and
  excluded from the three years, go/no-go at September 2029.
- The evidence boundary. No figure may imply an accuracy, generalization, expert-effort,
  transfer-safety or clinical result. If a drawing choice would make the proposed system look
  validated, choose differently.
- The existing shape/line/colour semantics, unless you have a concrete reason to change one, in
  which case change it everywhere and say so.

REPORT BACK

State per figure: the tool used, whether the eight quality gates passed, and what changed. List any
figure-versus-text discrepancy you found and how you resolved it. List anything you could not do and
why. If you used a tool not named in this brief, say which and why it was better.

Do not fabricate. If a value, label, or date cannot be verified against the document, leave it and
flag it rather than inventing a plausible one.
```
