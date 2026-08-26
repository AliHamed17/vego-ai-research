# Visual review

<!-- visual-review-status: PASS -->

Inspected on 2026-08-26 after the clean shared 11-figure rebuild. The canonical build command was `uv run python scripts/build_proposal_visuals.py --clean --verify`; it passed. The tool chain was CPython 3.11.14, the deterministic SVG/PDF scene builders with embedded Carlito, ReportLab 4.4.9, Poppler `pdftoppm` 25.07.0, Pillow 12.3.0, and the local proof viewer. The 144-DPI proof represents the declared proposal insertion width or, for Figure 11, its standalone A4 proof width. The 576-DPI proof is the 400% diagnostic. Automated contrast ratios below come from the final `qa-receipt.json`.

I opened all eight current proof variants for Figures 1, 5, 7, and 11: normal, greyscale, protanopia, and deuteranopia at both 144 and 576 DPI. I also opened all four current full-system contact sheets. The scoped reviewers for Figures 4, 9, and 10 independently inspected those figures in all four modes at both DPIs before freezing their sources; the final clean build preserved those frozen inputs, and I rechecked them in the canonical contact sheets. Figures 2, 3, 6, and 8 were unchanged, their generated hashes remained byte-identical to the previously inspected artifacts, and their current contact-sheet and automated checks were revalidated. Figure 7's canonical eight-variant review confirmed that the redesigned gate, status, permission, and diagnostic layers remain legible and visually independent. This review does not imply that the integrated DOCX/PDF has already been rebuilt or inspected.

| Figure | A4 144 DPI clipping/crossing | 400% 576 DPI clipping/crossing | Font-size | Ambiguity | Consistency | Greyscale | Protanopia | Deuteranopia |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| fig-01 | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS |
| fig-02 | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS |
| fig-03 | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS |
| fig-04 | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS |
| fig-05 | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS |
| fig-06 | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS |
| fig-07 | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS |
| fig-08 | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS |
| fig-09 | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS |
| fig-10 | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS |
| fig-11 | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS |

## Per-figure report

### fig-01

- Tool used: canonical tool chain above; all eight current proof variants were opened directly.
- What changed: the title and controlled integration caption preserve “Six readings of one observed model difference”; the observed fragment and all six readings now use rectangle artifact/record semantics.
- Greyscale: PASS; rectangle, rounded-process legend sample, line style, and text distinctions remain visible without colour.
- Deuteranopia: PASS; all six readings, artifact source, and legend encodings remain distinguishable.
- Protanopia: PASS; the orange legend swatch changes hue but remains redundant with its explicit label.
- Contrast with lowest ratio: PASS at 12.194:1.
- Print/final-size: PASS at 371.339 by 243.691 pt; minimum text 7.040 pt and minimum ordinary text 8.046 pt.
- 400% vector/zoom: PASS at 576 DPI; no clipping, crossing, or text displacement, and the source SVG/PDF vector checks pass.
- Label correctness: PASS; the title says “one observed model difference”, readings 1–6 are present once, and the source is labelled “Observed fragment / Shift Supervisor actor”.
- Consistency: PASS; artifact rectangles and the visual-language legend now agree with the frozen shape semantics.
- Integrity: PASS; SVG has 130 elements, 539 attributes, depth 4, strict semantic preflight, embedded font, no external resource, and the PDF has zero raster-image XObjects.

### fig-02

- Tool used: canonical tool chain above; unchanged byte-identical proofs were revalidated through the current contact sheets and automated receipt.
- What changed: no source change in this audit; the four-agent VEGO-AI baseline remains the controlled reference architecture.
- Greyscale: PASS; agent, pipeline, artifact, and refinement-loop meaning remains label- and shape-supported.
- Deuteranopia: PASS; the baseline flow and doctoral attachment band remain distinct through labels and borders.
- Protanopia: PASS; the same non-colour distinctions remain intact.
- Contrast with lowest ratio: PASS at 12.194:1.
- Print/final-size: PASS at 371.339 by 189.795 pt; minimum and ordinary text are both 8.252 pt.
- 400% vector/zoom: PASS at 576 DPI; unchanged inspected geometry and current vector checks show no clipping or crossing.
- Label correctness: PASS; the four agents, existing artifacts, refinement loop, and proposed attachment remain visibly separated.
- Consistency: PASS; baseline navy, proposed-layer treatment, and common shape grammar match the system legend.
- Integrity: PASS; SVG has 52 elements, 224 attributes, depth 4, strict semantic preflight, embedded font, no external resource, and the PDF has zero raster-image XObjects.

### fig-03

- Tool used: canonical tool chain above; unchanged byte-identical proofs were revalidated through the current contact sheets and automated receipt.
- What changed: no source change in this audit; the literature streams, residual gap, and research-question mapping remain explicit.
- Greyscale: PASS; the open gap and question mapping are carried by spacing, arrows, boxes, and text rather than colour alone.
- Deuteranopia: PASS; streams and mapped questions remain distinguishable.
- Protanopia: PASS; streams and mapped questions remain distinguishable.
- Contrast with lowest ratio: PASS at 16.268:1.
- Print/final-size: PASS at 371.339 by 278.504 pt; minimum text 7.427 pt and minimum ordinary text 8.355 pt.
- 400% vector/zoom: PASS at 576 DPI; unchanged inspected geometry and current vector checks show no clipping or crossing.
- Label correctness: PASS; U-RQ and SQ1–SQ3 mappings remain visible and the residual gap is not presented as a demonstrated result.
- Consistency: PASS; proposed and conditional states use the shared colours, labels, and border grammar.
- Integrity: PASS; SVG has 92 elements, 392 attributes, depth 4, strict semantic preflight, embedded font, no external resource, and the PDF has zero raster-image XObjects.

### fig-04

- Tool used: canonical tool chain above; the scoped reviewer opened all eight frozen proof variants, and the final canonical contact sheets were rechecked.
- What changed: the three specified study labels were restored, and the integrated evaluation row now exposes all four comparison arms; the mapping remains working material pending supervisor confirmation.
- Greyscale: PASS; row/column boundaries, study labels, and comparison-arm text preserve the programme structure.
- Deuteranopia: PASS; the three studies and integrated row remain separable by labels and table geometry.
- Protanopia: PASS; the three studies and integrated row remain separable by labels and table geometry.
- Contrast with lowest ratio: PASS at 16.268:1.
- Print/final-size: PASS at 371.339 by 199.208 pt; minimum text 7.040 pt and minimum ordinary text 8.123 pt.
- 400% vector/zoom: PASS at 576 DPI; no row overflow, label clipping, or route crossing was observed, and vector checks pass.
- Label correctness: PASS; “Attention-budget review-policy model”, “Conformance and comparator study”, “Reliability and frozen-target study”, and AI-only, human-only, ordinary non-governed HITL, and governed VEGO-AI are all present.
- Consistency: PASS; the programme-spine table uses the same artifact, evaluation, and conditional visual grammar as the other figures.
- Integrity: PASS; SVG has 107 elements, 498 attributes, depth 5, strict semantic preflight, embedded font, no external resource, and the PDF has zero raster-image XObjects.

### fig-05

- Tool used: canonical tool chain above; all eight current proof variants were opened directly.
- What changed: all eight input signals now use rectangle artifact/input semantics; each hard-rule condition uses a compact dashed diamond and bypasses the matched scoring policy through the hard-rule bus.
- Greyscale: PASS; proposed signals remain distinguishable by shading and labels, while hard rules remain visible through diamonds and dashed routing.
- Deuteranopia: PASS; input, policy, action, and bypass meanings remain shape-, border-, and text-redundant.
- Protanopia: PASS; input, policy, action, and bypass meanings remain shape-, border-, and text-redundant.
- Contrast with lowest ratio: PASS at 16.268:1.
- Print/final-size: PASS at 371.339 by 256.096 pt; minimum text 7.043 pt and minimum ordinary text 8.003 pt.
- 400% vector/zoom: PASS at 576 DPI; no label/diamond overlap, clipping, or unintended connector crossing, and vector checks pass.
- Label correctness: PASS; eight signals, matched attention budget B, six routing actions, and the three hard rules are visible and correctly separated.
- Consistency: PASS; rectangles denote signals/inputs, the rounded rectangle denotes the review process, and diamonds denote hard-rule decisions.
- Integrity: PASS; SVG has 153 elements, 730 attributes, depth 4, strict semantic preflight, embedded font, no external resource, and the PDF has zero raster-image XObjects.

### fig-06

- Tool used: canonical tool chain above; unchanged byte-identical proofs were revalidated through the current contact sheets and automated receipt.
- What changed: no source change in this audit; grouped judgment fields and the lifecycle state machine remain the controlled design.
- Greyscale: PASS; states, transitions, field groups, and stores remain distinguished by shape, arrows, and text.
- Deuteranopia: PASS; lifecycle order and governed-state meanings remain explicit.
- Protanopia: PASS; lifecycle order and governed-state meanings remain explicit.
- Contrast with lowest ratio: PASS at 16.268:1.
- Print/final-size: PASS at 371.339 by 229.169 pt; minimum text 7.073 pt and minimum ordinary text 8.134 pt.
- 400% vector/zoom: PASS at 576 DPI; unchanged inspected geometry and current vector checks show no clipping or crossing.
- Label correctness: PASS; judgment components, lifecycle states, transitions, and governed store remain present without conflation.
- Consistency: PASS; state, artifact/store, and transition semantics match the shared visual system.
- Integrity: PASS; SVG has 96 elements, 449 attributes, depth 4, strict semantic preflight, embedded font, no external resource, and the PDF has zero raster-image XObjects.

### fig-07

- Tool used: canonical tool chain above; all eight current proof variants were opened directly after the clean global rebuild.
- What changed: the invented gate-to-status classifier, adaptation-flag split, and permission-to-diagnosis sequence were removed. Five source-supported gates now feed only the stated “any gate fails” boundary; the four formal statuses are shown without a fabricated lookup rule, “reuse permitted” is visibly not a fifth status, and local-quirk/capability-gap diagnosis is an independent layer.
- Greyscale: PASS; gate decisions, the any-failure boundary, four formal statuses, reuse permission, and the independent diagnostic guard remain distinguishable through labels, geometry, and line style.
- Deuteranopia: PASS; status, permission, and diagnosis layers remain legible and visually independent.
- Protanopia: PASS; status, permission, and diagnosis layers remain legible and visually independent.
- Contrast with lowest ratio: PASS at 16.268:1.
- Print/final-size: PASS at 371.339 by 285.297 pt; minimum text 7.246 pt and minimum ordinary text 8.151 pt.
- 400% vector/zoom: PASS at 576 DPI; no clipping, label collision, or unintended connector path was observed in any colour-vision mode, and vector checks pass.
- Label correctness: PASS; five gates, four statuses, “reuse permitted”, “local quirk”, “capability-gap candidate”, and four AND checks are present without an inferred status/permission/diagnosis sequence.
- Consistency: PASS; reuse decision, permission effect, and replication diagnosis remain separate through headings, spacing, shape, and explicit boundary notes.
- Integrity: PASS; SVG has 169 elements, 762 attributes, depth 6, strict semantic preflight, embedded font, no external resource, and the PDF has zero raster-image XObjects.

### fig-08

- Tool used: canonical tool chain above; unchanged byte-identical proofs were revalidated through the current contact sheets and automated receipt.
- What changed: no source change in this audit; the exact baseline pairs, full zero-to-one scale, direct values, and hatch redundancy remain frozen.
- Greyscale: PASS; direct values and hatching preserve the paired-score comparison.
- Deuteranopia: PASS; direct values and hatching preserve the paired-score comparison.
- Protanopia: PASS; direct values and hatching preserve the paired-score comparison.
- Contrast with lowest ratio: PASS at 16.268:1.
- Print/final-size: PASS at 323.150 by 126.322 pt; minimum text 7.051 pt and minimum ordinary text 8.226 pt.
- 400% vector/zoom: PASS at 576 DPI; unchanged inspected hatch containment and current vector checks show no clipping or pattern resource.
- Label correctness: PASS; the full scale, paired direct values, and evidence-bound limitation notes remain visible, with no unreported dispersion introduced.
- Consistency: PASS; bars, direct labels, and hatch encoding follow the shared evidence and accessibility contract.
- Integrity: PASS; SVG has 382 elements, 2,255 attributes, depth 5, strict semantic preflight, embedded font, no external resource or SVG pattern, and the PDF has zero raster-image XObjects.

### fig-09

- Tool used: canonical tool chain above; the scoped reviewer opened all eight frozen proof variants, and the final canonical contact sheets were rechecked.
- What changed: the preparatory period is visibly outside the three-year count; six exact semesters, study dependencies, dated milestones, and the conditional medical track are aligned to the true calendar. Lane geometry is quantized to Word's observed six-significant-digit SVG serialization without changing content or chronology.
- Greyscale: PASS; calendar order, dependencies, milestones, and conditional track remain visible through bands, diamonds, dashed borders, and labels.
- Deuteranopia: PASS; year/semester boundaries and medical conditionality remain explicit.
- Protanopia: PASS; year/semester boundaries and medical conditionality remain explicit.
- Contrast with lowest ratio: PASS at 5.762:1.
- Print/final-size: PASS at 371.339 by 233.015 pt; minimum text 7.195 pt and minimum ordinary text 8.123 pt.
- 400% vector/zoom: PASS at 576 DPI; no milestone-label collision, clipping, or reversed dependency route, and vector checks pass.
- Label correctness: PASS; Oct 2026–Oct 2027 is preparatory, Oct 2027–Oct 2030 contains six semesters, Paper 1/2/3 and defence dates are exact, and the medical and EXP-005 gates remain 0/6 and 0/24.
- Consistency: PASS; semester bands, process bars, decision diamonds, dependencies, and conditional dashed treatment match the shared grammar.
- Integrity: PASS; SVG has 238 elements, 1,268 attributes, depth 5, strict semantic preflight, embedded font, no external resource, and the PDF has zero raster-image XObjects.

### fig-10

- Tool used: canonical tool chain above; the scoped reviewer opened all eight frozen proof variants, and the final canonical contact sheets were rechecked.
- What changed: the taxonomy boundary is a true 40/60 two-column argument with four taxonomy branches on the left and eleven ordered proposal concepts on the right.
- Greyscale: PASS; branch/concept separation, column boundaries, labels, and the scope note do not depend on colour.
- Deuteranopia: PASS; taxonomy coverage and proposal-needs columns remain distinct.
- Protanopia: PASS; taxonomy coverage and proposal-needs columns remain distinct.
- Contrast with lowest ratio: PASS at 12.194:1.
- Print/final-size: PASS at 371.339 by 228.992 pt; minimum text 7.073 pt and minimum ordinary text 8.134 pt.
- 400% vector/zoom: PASS at 576 DPI; all branch and concept labels remain inside their columns without clipping, and vector checks pass.
- Label correctness: PASS; Human Feedback, Communication Mode, Interaction Variant, Orchestration, and all eleven Table 11 concepts appear in order; the claim remains coverage, not necessity or effectiveness.
- Consistency: PASS; the two columns use the shared existing/proposed boundary treatment and text-first non-colour redundancy.
- Integrity: PASS; SVG has 130 elements, 593 attributes, depth 5, strict semantic preflight, embedded font, no external resource, and the PDF has zero raster-image XObjects.

### fig-11

- Tool used: canonical tool chain above; all eight current proof variants were opened directly.
- What changed: “Less relevant” and “Partly” no longer use the reserved orange doctoral-layer accent; they now use neutral/muted styling plus explicit diagonal-hatch redundancy and label-safe background treatment.
- Greyscale: PASS; Relevant is solid, Less relevant and Partly are labelled with diagonal hatch, and No uses a dotted border.
- Deuteranopia: PASS; disposition and RQ-coverage meanings remain fully text-, hatch-, fill-, and border-redundant.
- Protanopia: PASS; disposition and RQ-coverage meanings remain fully text-, hatch-, fill-, and border-redundant.
- Contrast with lowest ratio: PASS at 11.067:1.
- Print/final-size: PASS at the standalone 523.000 by 283.292 pt proof size; minimum text 7.409 pt and minimum ordinary text 8.281 pt.
- 400% vector/zoom: PASS at 576 DPI; hatch lines do not cross evidence labels, texture chips remain clear, and vector checks pass.
- Label correctness: PASS; the 90-paper disposition remains 22 relevant, 63 less relevant, and 5 not relevant; U-RQ/SQ1/SQ2/SQ3 coverage remains Partly/Yes/Partly/No and is explicitly separated from paper-level disposition.
- Consistency: PASS; reserved orange is absent from these evidential states, while solid, diagonal-hatch, and dotted-border treatments align with the shared non-colour contract.
- Integrity: PASS; SVG has 220 elements, 1,254 attributes, depth 5, strict semantic preflight, embedded font, no external resource or SVG pattern, and the PDF has zero raster-image XObjects.

## Release boundary

The final deterministic QA receipt SHA-256 is `F7517D070F39DFF0595527EB02E7350B3CE88243DFC84075B8DC4EDEEE9DA978`; its overall status is PASS. All 11 SVG/PDF pairs pass source provenance, final-size font, contrast, vector, semantic, embedded-font, no-external-reference, and zero-raster-image checks. The largest current SVG is Figure 8 at 382 elements and 2,255 attributes, below the fail-closed 500-element and 2,500-attribute ceilings.

This is an agent QA gate and a source-artifact review, not Ali's scholarly or visual approval. Figure 11 remains a standalone candidate. The revised figures have not yet been integrated into, rendered from, or visually inspected inside the final 31-page DOCX/PDF package; that separate integration gate remains pending.

Evidence: `qa/generated/proofs/{144,576}/{normal,greyscale,protanopia,deuteranopia}/`, `qa/generated/contact-sheets/`, and `qa/qa-receipt.json`.
