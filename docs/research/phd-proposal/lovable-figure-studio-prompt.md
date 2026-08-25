# Lovable Prompt — VEGO-AI Proposal Figure Studio

Paste-ready prompt for lovable.dev. Builds a small internal web tool that renders all 11 proposal
figures (plus the anchored Gantt) to the exact visual-language spec from
`proposal-enhancement-prompt-v3-2026-08-25.md`, and exports each as clean SVG for embedding in the
proposal document (Overleaf/TikZ, Word, or Google Docs). This does not write the proposal text — it
only produces the vector figures.

## Prompt

```text
Build "VEGO-AI Proposal Figure Studio" — a static, client-side-only web app (no backend, no auth,
no database) that renders a fixed set of 11 diagrams plus one Gantt timeline to a strict shared
visual style, and lets me export each one as a clean SVG file.

WHY THIS EXISTS
These are figures for an academic doctoral research proposal. They must all read as ONE visual
system — same shape/line/colour language throughout — not 11 unrelated pictures. Precision and
consistency matter more than flourish.

LAYOUT
- Left sidebar: a list of all 12 items (11 figures + the Gantt), each with its number and title.
  Clicking one loads it into the main canvas.
- Main canvas: renders the selected diagram at a fixed aspect ratio matching a printed page
  (roughly 16:10), centred, with generous whitespace margin.
- Top-right of the canvas: a "Download SVG" button, and a "Download PNG" secondary button, both
  exporting only the diagram content (no app chrome).
- A small always-visible legend panel under the sidebar showing the fixed shape/line/colour key
  (see VISUAL SYSTEM below), so I can sanity-check every figure against it.
- A "Print proof" view: a single page showing thumbnails of all 12 items on a grid, for a quick
  visual consistency check before export.

VISUAL SYSTEM — apply identically to every figure, no exceptions
- Shapes: rectangle = artifact or record; rounded rectangle = process or agent; diamond = decision;
  cylinder = data store; parallelogram = human-judgment input.
- Lines: solid = committed/existing flow; dashed = conditional, proposed, or gated; dotted =
  information reference (not control flow).
- Colour: exactly three semantic colours plus neutral text/lines.
    - "existing" (the current VEGO-AI baseline) — a neutral blue-grey.
    - "new" (the doctoral human-judgment layer being proposed) — one confident accent colour.
    - "conditional/out-of-scope" (anything gated, not-yet-approved, or not on the critical path) —
      a muted amber, always paired with a dashed line, never colour alone.
  Use a colourblind-safe palette (no red/green as the only contrast). Every colour distinction must
  also be visible in a greyscale render — add a toggle that desaturates the canvas so I can check
  this directly in the app.
- Typography: one sans-serif family throughout, used only in the app and exported figures (do not
  bring in a second display font). Minimum effective label size equivalent to 8pt at print scale.
  No all-caps except short status chips (e.g. "GATED", "NEW").
- No shadows, gradients, 3D bevels, icons, or clip art. Every mark must carry information.
- Each figure must stay readable at roughly 9 primary nodes or fewer and at most 2 nesting levels;
  if a figure config exceeds that, show a small on-canvas warning rather than silently overflowing.

DATA MODEL
Define each figure as a typed config object (nodes, edges, labels, groups) in a single
`figures.ts` file, NOT hard-coded per-component markup. This is important: it must be trivial for
me to edit a label or add a node later without touching rendering code. Use `@xyflow/react` (React
Flow) as the diagram engine for the 10 flow/state/decision figures, and a custom lightweight SVG
component for the Gantt (Figure 10) since it needs true calendar-date positioning, not a node graph.

THE 12 ITEMS TO IMPLEMENT

1. "Six readings of one observed model difference" — CORRECTED 2026-08-26: the earlier "four
   readings" spec was wrong; section 1.7's Shift Supervisor example gives six readings verbatim, not
   four. One model fragment (the Shift Supervisor actor, mentioned in a domain description but not
   named by the original text) shown once, fanning out to six labelled readings: defensible
   abstraction of an unnamed role; modeling-language error; domain misconception about authorization;
   genuine ambiguity in the task description; gap in the guideline; legitimate local/pedagogical
   decision by the instructor. Fan/radial layout, shared origin node visually obvious, all six arrows
   the same weight since the point is that none is privileged over the others.

2. "The four-agent VEGO-AI baseline" — pipeline: Language Advisor -> Domain Advisor -> Model
   Inspector -> Variability Explorer, left to right. Edge labels: language template, reference
   guidelines, compliance vector, uncovered-fragment audit, variability patterns. A dashed feedback
   edge from Model Inspector back to Domain Advisor labelled "refinement loop". All four agent
   nodes coloured "existing". Add a faint dashed outline region below the pipeline labelled "where
   the doctoral human-judgment layer attaches (developed later)", coloured "new" but visually
   secondary (lower opacity).

3. "Established research streams and the residual problem" — 5 source nodes (mixed-initiative
   design, deferral & active learning, explanatory debugging & provenance, case-based reasoning &
   transfer, guideline operationalization) converging with solid arrows toward one open/unclosed
   node labelled "residual gap: claim-level integration under contested authority" — draw that node
   as visibly open (dashed outline, not filled), not as a closed box.

4. "Three residual gaps mapped to research questions" — 3 rows, one per SQ1/SQ2/SQ3, each row: gap
   statement -> arrow -> research question. Keep small and plain.

5. "Sub-questions to artifacts, evaluations, and outputs" — a 4-row x 4-column grid: rows SQ1, SQ2,
   SQ3, Integrated Evaluation; columns Sub-question, Primary artifact, Evaluation, Planned output.
   The Integrated Evaluation row visually receives an arrow from each of the other three rows,
   showing it consumes them.

6. "Study 1 review policy" — 8 named signal inputs (claim-level uncertainty, consequence, novelty,
   evidence quality, cross-agent disagreement, expected future reuse value, reviewer competence,
   queue conditions) feeding a central "review policy" decision node, constrained by an explicit
   "attention budget" node drawn as a bounding constraint (not just another input), with a dashed
   "hard-rule bypass" path around it. Output: 6 routing actions (immediate qualified review, queue,
   batch review, audit sample, autonomous with logging, blocked).

7. "Study 2 governed-judgment record and lifecycle" — split view. Left half: record field groups as
   stacked rectangles (identity, evidence grounding, decision trace, scope & exclusions, competence
   & authority, provenance & version). Right half: a real state machine with labelled transitions
   between states created -> validated -> contested -> superseded / expired / revoked.

8. "Study 3 controlled-reuse and capability-gap decision procedure" — a decision flow with 4
   sequential diamond gates in order: similarity found? -> applicable to this case? -> requester
   authorized? -> still valid? A failure at any gate routes to "reuse not permitted". Passing all
   four leads to a further split: "reuse permitted" vs a guarded branch to "transferable
   capability-gap candidate", where that guard is explicitly the 4-part declaration test (stable
   failure signature, reproduction in distinct frozen contexts, independent confirmation, local
   artifacts ruled out) drawn as 4 small AND-gated checks, not a single arrow.

9. "Expert-review scores from the foundation manuscript" — a real data chart, not a node graph: a
   grouped bar chart, x-axis = 4 settings (ch-ucd, ch-cd, pw-ucd, pw-cd), two bars per group
   (compliance vector, uncovered-fragment audit) using colour "existing" for both since this is
   someone else's reported result. Y-axis fixed 0 to 1, never truncated. Data:
     ch-ucd: compliance 0.80, uncovered 0.55
     ch-cd:  compliance 0.96, uncovered 0.81
     pw-ucd: compliance 0.83, uncovered 0.55
     pw-cd:  compliance 0.92, uncovered 0.88
   Caption text under the chart: "n=16 sampled outcomes, 4 per setting, 2 experts. Source-reported;
   not independently reproduced."

10. THE GANTT (this is the most important export). Timeline from October 2026 to October 2030.
    - A distinct leading band, Oct 2026-Oct 2027, styled "conditional/out-of-scope" muted colour,
      labelled "Preparatory year (proposal, approval, candidacy) — not one of the three years".
    - Six swimlanes for Oct 2027-Oct 2030: Study 1, Study 2, Study 3, Integrated Evaluation,
      Literature Review, Publications. Each lane has activity bars aligned to this semester grid:
        Semester 1  Oct 2027-Mar 2028
        Semester 2  Apr 2028-Sep 2028
        Semester 3  Oct 2028-Mar 2029
        Semester 4  Apr 2029-Sep 2029
        Semester 5  Oct 2029-Mar 2030
        Semester 6  Apr 2030-Sep 2030
    - Milestone diamonds (not bars) for: Paper 1 submission (end of Semester 2), Paper 2 submission
      (end of Semester 4), Paper 3 submission (end of Semester 5), Thesis defence (Oct 2030).
    - A dashed amber bar in its own lane labelled "Medical extension (conditional, off critical
      path)" spanning from a "go/no-go" milestone diamond at September 2029 (end of Semester 4)
      onward into Semester 5-6, visually distinct from the committed lanes above it.
    - Dependency arrows: Study 1 -> Study 2 -> Study 3 -> Integrated Evaluation, drawn as thin
      connector lines between the lanes at the point one study's output feeds the next.
    - X-axis shows month/year ticks at each semester boundary. Today's date is not marked (this is
      a forward plan, not a status tracker).

11. "Where the taxonomy meets this research, and where it stops" — two-column layout. Left column
    (narrower, "existing" colour): the 4 taxonomy branches (Human Feedback, Interaction,
    Orchestration, Communication) with a one-line relevance verdict each. Right column (wider,
    "new" colour, must visually dominate — give it roughly 60% of the canvas width): the 11 missing
    concepts (reuse across episodes, claim-level validity scope, diagnostic attribution, temporal
    validity, claim-scoped authority, provenance binding, elicitation trigger, attention-budget
    accounting, preserved dissent, leakage control, judgment target layer), grouped loosely by
    which sub-question needs them. This figure must stand alone without surrounding text — add a
    one-line title strip: "Four taxonomy branches; two describe agent wiring the baseline already
    fixes. The doctoral contribution lives on the right."

BUILD NOTES
- Keep it fast and simple: Vite + React + TypeScript + Tailwind, @xyflow/react for the node
  diagrams, a small custom SVG component for the Gantt, and any lightweight chart library (e.g.
  Recharts) for Figure 9's bar chart.
- No login, no database, no API calls. Figure content lives entirely in figures.ts.
- SVG export must produce a standalone file — no external font or stylesheet dependency at export
  time — so it drops cleanly into LaTeX/Word without broken references.
- Make the greyscale toggle a genuine desaturation of the rendered SVG, not just a CSS filter on
  the preview, so what I see is what exports.
```
