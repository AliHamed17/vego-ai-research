# Proposal Visual Integration-Size Remediation

**Goal:** Reflow Figures 1–10 into the exact height envelopes of the frozen source DOCX so the
readable vector replacements can preserve the proposal's 31-page pagination without weakening the
7 pt absolute or 8 pt ordinary-label gates.

**Trigger evidence:** The controlled Word integration run on 2026-08-26 passed source, QA, SVG,
caption, order, width, and alt-text checks, then failed closed at 40 pages versus the required 31.
The derived copy and PDF were removed. The source remained SHA-256
`D73C840BD606695DAE50EE2E9304403D0ECB0518BCD43F05FE68B1DE166063DA`.

## Locked interfaces

- Preserve every content label, value, date, state, edge, dependency, evidence boundary, caption,
  and alt-text contract already covered by the figure tests.
- Preserve the declared insertion widths. Do not stretch, crop, or distort figures in Word.
- Preserve the absolute 7 pt floor and ordinary 8 pt release gate at the declared width.
- Figure 11 remains standalone and unchanged.
- A figure passes this remediation only when its rendered height at the declared width is no more
  than the frozen source inline height (0.5 pt rounding tolerance):

| Figure | Width EMU | Maximum height EMU | Maximum height pt |
| --- | ---: | ---: | ---: |
| fig-01 | 4,716,000 | 3,108,664 | 244.78 |
| fig-02 | 4,716,000 | 2,694,911 | 212.20 |
| fig-03 | 4,716,000 | 3,677,487 | 289.57 |
| fig-04 | 4,716,000 | 2,540,969 | 200.08 |
| fig-05 | 4,716,000 | 3,259,853 | 256.68 |
| fig-06 | 4,716,000 | 2,920,229 | 229.94 |
| fig-07 | 4,716,000 | 3,639,375 | 286.56 |
| fig-08 | 4,104,000 | 1,610,091 | 126.78 |
| fig-09 | 4,716,000 | 2,963,971 | 233.38 |
| fig-10 | 4,716,000 | 2,920,229 | 229.94 |

## Task 1: Compact Figures 1–4

Use red/green structural tests to enforce each height envelope. Recompose into dense landscape
grids/tables while retaining exact six-reading equality, baseline/proposed boundary, gap-to-RQ
mapping, and programme-spine dependency semantics. Inspect 144/576 DPI normal proofs and all
accessibility modes before committing.

## Task 2: Compact Figures 5–7

Use red/green structural tests to enforce each height envelope. Prefer lateral signal/action banks,
compact state-machine lanes, and a horizontal five-gate reuse procedure. Preserve all eight signals,
six actions, hard-rule bypass, canonical lifecycle states/transitions, five reuse gates, four formal
statuses, and four capability-gap AND checks. Inspect every proof before committing.

## Task 3: Compact Figures 8–10

Use red/green structural tests to enforce each height envelope. Use a compact horizontal score chart,
a true three-column year grid with two consecutive semesters per year and attached milestones, and a
dense taxonomy/concept matrix. Preserve all exact scores/disclosures, dates/dependencies, eleven
ordered concepts, and scope limitations. Figure 9 must remain Year 1=S1/S2, Year 2=S3/S4, and
Year 3=S5/S6.

## Task 4: Rebuild and integrate

1. Run a clean verified build twice and prove all 125 artifact hashes identical.
2. Inspect all 11 normal proofs at 144 DPI, all 11 at 576 DPI, and all four accessibility contact
   sheets. Record only observed PASS results.
3. Obtain an independent frozen-commit review.
4. Run the copy-only Word integration against the frozen source.
5. Require the post-integration receipt to prove 31 pages, 10 ordered SVG-bound figures, exact
   widths/alt text/captions, only Figure 1 Four-to-Six, 14 table captions, scholarly text/citation
   parity, 39 static TOC rows with actual-page matches, zero raster PDF XObjects, and no dangling
   references.
6. Render all 31 PDF pages at 144 DPI and the ten figure pages at 576 DPI. Inspect every page before
   calling the package ready for human review.

No source proposal file may be modified or closed. Any failed gate removes only the controlled
derived outputs and records the exact blocker.
