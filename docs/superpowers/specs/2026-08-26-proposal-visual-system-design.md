# VEGO-AI Doctoral Proposal Visual System Design

**Status:** Approved design, pending Ali review of this written specification

**Date:** 2026-08-26

**Branch:** `feature/proposal-visual-system`

**Authority:** Ali's pasted `codex-visual-system-task-2026-08-26.md`, interpreted against the attached proposal PDF

## 1. Objective

Create a reproducible, committee-ready visual system for the VEGO-AI doctoral proposal. The work
covers the ten existing figures, one requested corpus-screening chart, reusable vector sources,
standalone SVG/PDF outputs, a derived integrated DOCX/PDF, and evidence-backed visual QA.

The work must improve visual precision without implying that proposed mechanisms are validated.
It must preserve the proposal's scholarly boundaries, provenance captions, numbering, page order,
and cross-references.

## 2. Frozen inputs and evidence hierarchy

The attached PDF is the factual and layout source:

- `VEGO_AI_Doctoral_Proposal_Revised_20260825 (4).pdf`
- SHA-256: `ADB663A4B8B0FFD3F09F2CEFEF43D690B5540FC36D4947FF60DCC624072846C9`
- 31 A4 pages, 10 figures, 14 tables, zero raster-image XObjects
- Byte-identical to revision `(3)` despite the later filename

The editable input is the adjacent Downloads copy
`VEGO_AI_Doctoral_Proposal_Revised_20260825.docx`. It is never modified in place. Integration uses
a frozen copy and records its hash once the file is no longer write-locked.

When sources disagree, the following order applies:

1. Exact proposal prose and numbered tables for factual labels, data, dates, and formal statuses.
2. Ali's visual-system task for visual semantics and requested transformations.
3. Existing figures for composition ideas only; they are not authoritative where clipped or stale.
4. Repository summaries and prior review notes for provenance and known issues.

Any unresolved conflict is reported, not silently normalized.

## 3. Observed defects that define the redesign

The visual audit established these defects in the source PDF:

- Figure 1 presents four interpretations while Section 1.7 enumerates six.
- Figures 1 and 3-10 contain material clipping at the left, right, or top page boundary.
- Figure 8's legend and category labels overlap or clip despite correct values and a 0-1 axis.
- Figure 10 visibly lists ten missing concepts although Table 11 contains eleven.
- The Figure 7 brief says three outcomes, while Section 3.5 defines four formal procedure statuses:
  `Eligible`, `Eligible with adaptation`, `Blocked`, and `Undetermined`.
- The Figure 6 brief and current figure use different state vocabularies.
- Current figures do not share a reliable print-width contract; correct standalone geometry is not
  sufficient unless document placement is also controlled.

## 4. Chosen implementation approach

Use one deterministic Python vector system with a shared design-token and geometry library.
Every figure has a small source module and imports only the shared renderer and its frozen content
manifest. The same scene graph produces SVG and PDF, preventing format drift.

This approach is chosen over a D2/Graphviz/Mermaid mixture because the task requires exact A4
placement, one semantic visual language, shared typography, and deterministic accessibility checks.
Specialized layout engines remain useful references, but mixing them would make line weights,
fonts, spacing, and output behavior harder to hold constant.

The implementation remains free and local. No paid service, cloud renderer, or external AI image
generation is used.

### 4.1 Components

- `content.json`: frozen proposal-derived labels, data, dates, captions, alt text, and locators.
- `visual_tokens.py`: shapes, line semantics, palette, typography, spacing, and final-size rules.
- `renderer.py`: shared scene graph with SVG and ReportLab PDF backends.
- `fig_01_*.py` through `fig_11_*.py`: one source module per visual.
- `build_figures.py`: one-command deterministic build and hash manifest.
- `integrate_proposal.py`: creates a derived DOCX using Word automation on a copy and exports PDF.
- `qa_figures.py`: automated correctness, accessibility, vector, placement, and integrity gates.

The integration script is optional at build time and fails closed when Word automation is
unavailable. Standalone figure generation and QA do not depend on Word.

### 4.2 Typography and palette

Use Carlito for figure labels to match the proposal's sans-serif display typography and Caladea
only where a serif text treatment is necessary. Pin open-licensed font files and their license in a
`vendor/fonts/` directory. SVG outputs embed the required font data. PDF outputs embed font subsets.

Semantic palette:

- Existing VEGO-AI baseline: dark navy neutral.
- Doctoral human-judgment layer: Okabe-Ito orange accent.
- Conditional, gated, or out-of-scope material: cool grey.
- Page/background: white and very light neutral fills only.

Colour is always paired with shape, line style, position, or an explicit label.

### 4.3 Shape and line contract

- Rectangle: artifact or record.
- Rounded rectangle: process or agent.
- Diamond: decision or milestone.
- Cylinder: store.
- Parallelogram: human-judgment input.
- Solid line: committed or existing flow.
- Dashed line: conditional, proposed, or gated flow.
- Dotted line: information reference.

The legend is introduced in Figure 1 and the semantics remain unchanged afterward.

## 5. Figure-by-figure design

### Figure 1 - Six readings of one observed model difference

One shared observed-fragment node fans out to six equal sibling readings with identical edge weight.
The six labels follow Section 1.7 verbatim. The branches do not reconverge. The footer states,
"the artifact is identical under all six". The complete shape/line/colour legend appears below.

### Figure 2 - Four-agent VEGO-AI baseline

Show Language Advisor, Domain Advisor, Model Inspector, and Variability Explorer left to right.
Place exchanged artifacts on edges and draw the refinement loop back to the Domain Advisor.
The proposed doctoral attachment band is secondary, dashed, and explicitly outside the baseline.
Retain the caption provenance: "redrawn from the supplied foundation manuscript [1]".

### Figure 3 - Streams, residual opening, and question mapping

Show five established streams converging toward a visibly open, unfilled, dashed residual gap.
Below it, map the three load-bearing gaps to SQ1-SQ3 and show the umbrella question as requiring an
integrated evaluation. No visual closure or validated-effect implication is permitted.

### Figure 4 - Programme spine

Use a four-column matrix: sub-question, primary artifact, evaluation, planned output. Strictly align
SQ1, SQ2, and SQ3 by row. A fourth integrated-evaluation row consumes all three and explicitly does
not imply that completing the component studies alone answers the umbrella question.

### Figure 5 - Study 1 review policy

Show the eight exact Section 3.3 signals as inputs and the six exact routing actions as outputs. The
matched attention budget encloses the policy as a constraint, never as a ninth signal. Hard rules
bypass the scoring policy. Literature-derived and proposed signals differ by fill and annotation as
well as colour.

### Figure 6 - Governed-judgment record and lifecycle

Panel A groups record fields. Panel B is a real state machine. To reconcile the brief with the
current figure, the canonical state labels are `Created`, `Validated`, `Contested`, `Superseded`,
`Expired`, and `Revoked`; transition labels explain activation, challenge, replacement, lapse, and
revocation. The current `Draft`, `Reviewed`, and `Active` labels are recorded as a source discrepancy
in the QA report rather than retained as unexplained competing terminology.

### Figure 7 - Reuse procedure and capability-gap guard

Show five sequential gates: retrieval/similarity, applicability, authorization, current validity,
and target benefit. Gate results map explicitly to the four formal Section 3.5 statuses:
`Eligible`, `Eligible with adaptation`, `Blocked`, and `Undetermined`.

Only eligible cases proceed to the separate diagnostic classification: `local quirk` or
`capability-gap candidate`. The latter requires four visibly separate AND-gated checks: a
predeclared failure signature, replication in at least two contexts above cohort, independent
confirmation, and exclusion of a local guideline/task/version/data/reviewer cause. This resolves
the brief's three-outcome wording without suppressing the proposal's four formal statuses.

### Figure 8 - Foundation-manuscript expert-review scores

Use grouped bars for `ch-ucd`, `ch-cd`, `pw-ucd`, and `pw-cd`. Plot compliance-vector and
uncovered-fragment-audit values of `0.80/0.55`, `0.96/0.81`, `0.83/0.55`, and `0.92/0.88`.
Keep the y-axis fixed at 0-1. Use a single neutral hue with solid versus hatch encoding. Preserve
the caption disclosure: n=16, four per setting, two experts, no dispersion reported.

### Figure 9 - Anchored three-year plan

Use swimlanes from October 2027 through October 2030. Place October 2026-October 2027 in a separate
preparatory band explicitly outside the three years. Draw inter-study dependency arrows, Paper 1-3
and defence milestones as diamonds, and the medical extension as a dashed conditional bar with a
September 2029 go/no-go diamond. Table 8 is authoritative for periods and outputs.

### Figure 10 - Taxonomy boundary

Use two columns at approximately 40/60 width. The left lists the four taxonomy branches. The right
lists all eleven Table 11 concepts in the same order, including the currently omitted elicitation
trigger. The claim-scope notice states that this is coverage of one taxonomy, not proof that the
concepts are necessary or that the proposed mechanisms work. The figure is also slide-safe.

### Figure 11 - Corpus screening and RQ coverage

Generate a compact stacked bar for 22 relevant, 63 less relevant, and 5 not relevant papers, with a
small panel for U-RQ, SQ1, SQ2, and SQ3 coverage below. Distinguish paper-level dispositions from
question-level `missing`. State single-rater, title-level screening in the visual and caption.

Figure 11 is built and delivered. It is not inserted into the derived proposal unless insertion can
preserve the 31-page count, Tables 12-13, numbering, TOC, and cross-references. If those conditions
cannot all be met, the QA report records it as a ready standalone candidate rather than changing the
document's scholarly structure.

## 6. Deliverables

Under `docs/research/phd-proposal/figures/`:

- One source module per figure.
- Shared renderer, tokens, content manifest, and font-license files.
- Eleven SVG and eleven PDF outputs.
- One-command PowerShell and Python build entry points.
- `README.md` with palette, typography, semantics, tools, and per-figure render commands.
- `qa/` manifest and contact sheets for accessibility and print review.
- A per-figure QA report and discrepancy register.

Derived integration outputs are written to `output/pdf/` and `output/docx/`, not over the Downloads
source. Repository policy determines whether generated binaries are tracked; source and manifests
are always tracked.

## 7. Integration contract

1. Freeze and hash the source DOCX after it can be read consistently.
2. Copy it to a controlled output path.
3. Replace only the ten existing inline figure objects, preserving their anchor paragraphs,
   captions, numbering, widths, and surrounding prose.
4. Update Figure 1's caption from four to six readings.
5. Set one- or two-sentence claim-focused alt text for every replaced figure.
6. Update genuine fields in the derived copy only and export a derived PDF. The source has no native
   Word TOC field: its Table of Contents is a static visible list and must not be described as
   automatically updateable.
7. Compare page count, figure/table order, the complete 39-row static TOC snapshot and its declared
   PDF pages, citations, and cross-references against the frozen source.
8. Abort integration if source drift, unexpected image count, unmatched captions, clipping, or page
   reflow cannot be reconciled without changing scholarly content.

The source document is never overwritten. Word automation runs invisibly and closes only the copy it
opened. If the original is already open, the integration path remains copy-only.

## 8. Verification design

### 8.1 Automated tests

- Content manifest contains every required label and locator.
- Figure 1 has exactly six equal branches.
- Figure 5 has exactly eight signals and six actions; budget is a constraint.
- Figure 6 uses legal states and named transitions.
- Figure 7 has five gates, four formal statuses, and four AND checks.
- Figure 8 has exact values and a 0-1 axis.
- Figure 9 dates and milestones match Table 8.
- Figure 10 has eleven ordered concepts.
- Figure 11 totals 90 and separates paper- and question-level semantics.
- SVGs contain no raster image elements or external resources.
- PDFs contain no raster-image XObjects and embed fonts.
- No text falls outside the declared artboard or below 7 pt.
- All text-on-fill pairs meet WCAG 4.5:1 at body-label size.
- Deterministic rebuild hashes match after path and metadata normalization.

New renderer behavior follows red-green-refactor tests before implementation.

### 8.2 Visual QA

For every figure:

- Render normal, greyscale, protanopia, and deuteranopia views.
- Place at final proposal width on simulated A4 black-and-white pages.
- Inspect at 100% and 400%.
- Record pass/fail for readability, ambiguity, clipping, line crossings, and semantic consistency.

Create one side-by-side contact sheet for the complete system and inspect each individual page.
Automated checks support but do not replace visual inspection.

### 8.3 Document integrity QA

For the derived proposal:

- 31 pages unless the build explicitly aborts.
- Figures and tables in ascending order.
- All 39 visible static TOC rows (Abstract plus 38 remaining entries) are byte-for-visible-text
  equivalent to the source snapshot and agree with their actual PDF pages. The earlier count of 29
  was an inspection error and is retired.
- No dangling section, figure, table, citation, URL, or DOI reference.
- Caption provenance remains unchanged except the approved Figure 1 count correction.
- Figure 8 disclosure and Figure 9 time boundary remain intact.
- No new empirical, accuracy, generalization, workload, transfer-safety, or clinical claim appears.

## 9. Error handling and evidence receipts

Every build writes a manifest containing input hashes, source module hashes, tool versions, output
hashes, font identities, and gate results. A failed gate stops integration and leaves standalone
assets available with a precise blocker. No failed or uninspected output is labeled final.

Known external/human gates remain unchanged: research-question approval, query execution,
independent reviewers, EXP-005 labels, and medical readiness are not advanced by visual work.

## 10. Source-control and release

- Work only on `feature/proposal-visual-system` in the isolated worktree.
- Preserve unrelated files and the user's untracked `docs/superpowers/` in the main checkout.
- Commit source, tests, manifests, documentation, and only policy-approved generated artifacts.
- Run independent code/evidence review after the frozen build.
- Open a draft PR after all available checks pass.
- Do not merge or externally release without Ali's approval.

## 11. Acceptance criteria

The implementation may be called `Ready for Ali review` only when:

- Eleven source-controlled visuals rebuild in one command to standalone SVG and PDF.
- All exact-label and data/date tests pass.
- All eight requested quality gates have per-figure results.
- No vector, font, clipping, contrast, greyscale, or colourblind blocker remains.
- The integrated DOCX/PDF either passes every document-integrity gate or is explicitly blocked with
  the standalone figure package complete.
- Every discrepancy and resolution is recorded.
- No evidence boundary or human approval gate is overstated.
