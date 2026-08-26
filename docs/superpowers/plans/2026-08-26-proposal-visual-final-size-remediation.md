# VEGO-AI Proposal Visual Final-Size Remediation Plan

> **For agentic workers:** Use `superpowers:subagent-driven-development` and red-green-refactor for each task. This plan remediates the `FINAL_SIZE_FONT` gate discovered by the approved Task 6 QA system.

**Goal:** Reflow all eleven visuals so every label is at least 7 pt and every ordinary label is at least 8 pt at its declared final width, without weakening any reviewed semantic, evidence, geometry, accessibility, or integration boundary.

**Verified base:** `58cad72a0c3b348ef6f6b3dd57463f6d071180f3`.

## Final-size contract

- Figures 1-7 and 9-10: `4,716,000 EMU = 371.338582677 pt`, from the source DOCX inline extent.
- Figure 8: `4,104,000 EMU = 323.149606299 pt`, from the source DOCX inline extent.
- Figure 11: `6,642,100 EMU = 523 pt`, standalone A4 proof width; it remains outside proposal integration.
- Absolute final text floor: 7 pt.
- Ordinary final text target and release gate: 8 pt.
- Only `provenance`, `supporting-note`, and `boundary-note` text roles may use the 7 pt exception floor. Default `label` text is ordinary.
- A portrait A4 proof uses 36 pt margins. Final placed height must fit the resulting content height.
- Every pre-existing exact-content, source-provenance, semantic-role, arrow-direction, non-crossing, contrast, vector, and evidence-boundary test remains mandatory.
- Text-size compliance must be tested from scene geometry and the QA width constants, not asserted through metadata.

Minimum practical native sizes (rounded upward with margin) are:

| Figure | Ordinary native min | Exception native min |
| --- | ---: | ---: |
| 1 | 16 | 14 |
| 2 | 20 | 17 |
| 3 | 18 | 16 |
| 4 | 21 | 19 |
| 5 | 25 | 22 |
| 6 | 23 | 20 |
| 7 | 27 | 24 |
| 8 | 28 | 24 |
| 9 | 27 | 24 |
| 10 | 28 | 25 |
| 11 | 19 | 17 |

These are lower bounds, not instructions to apply a blind font multiplier. Reflow cards, lanes, rows, wrapping, and scene height so labels remain readable and connectors remain unambiguous.

### Task 1: Reflow Figures 1-4

**Files:** Modify only `fig_01_six_readings.py` through `fig_04_programme_spine.py` and their focused tests.

- Add failing declared-width font tests for each scene using `DECLARED_WIDTH_EMU` and `EMU_PER_POINT` from the QA contract.
- Tag only genuine provenance/boundary/support text with an exception semantic role.
- Raise native sizes to the table floor and reflow all cards, rows, legends, and routes.
- Preserve the complete Figure 1 legend and exact six equal readings; the Figure 2 pipeline; the Figure 3 open gap; and the Figure 4 4x4 spine.
- Require 7/8 pt effective text, A4 height fit, no card/text/line crossings, and 144/576-DPI proof legibility.
- Commit `fix: reflow proposal figures 1 through 4 at final size`.

### Task 2: Reflow Figures 5-7

**Files:** Modify only `fig_05_review_policy.py` through `fig_07_reuse_procedure.py` and their focused tests.

- Add the same measured final-size tests before implementation.
- Reflow policy signals/actions, lifecycle states/transitions, and the full five-gate procedure without reducing exact labels or changing formal logic.
- Preserve every reviewed shared-bus declaration and status-versus-diagnosis boundary.
- Require 7/8 pt effective text, A4 height fit, no undeclared crossings/traversals, and 144/576-DPI proof legibility.
- Commit `fix: reflow proposal figures 5 through 7 at final size`.

### Task 3: Reflow Figures 8-11

**Files:** Modify only `fig_08_expert_scores.py` through `fig_11_corpus_screening.py` and their focused tests.

- Add the same measured final-size tests before implementation.
- Preserve exact Figure 8 values/full axis; Figure 9 dates/dependencies/gates; Figure 10 40/60 geometry and eleven ordered concepts; and Figure 11 paper/RQ levels and limitations.
- Keep Figure 11 standalone.
- Require 7/8 pt effective text, A4 height fit, no crossings/clipping, direct-label readability, and 144/576-DPI proof legibility.
- Commit `fix: reflow proposal figures 8 through 11 at final size`.

### Task 4: Rebuild and close Task 6 QA

- Run `uv run python scripts/build_proposal_visuals.py --clean --verify` after regenerating the manual-review table from actual inspection.
- Inspect all eleven portrait 144-DPI proofs, all eleven 576-DPI proofs, and all four contact sheets individually.
- Mark a row PASS only after actual clipping, crossing, font-size, ambiguity, consistency, greyscale, protanopia, and deuteranopia checks pass.
- Require `FINAL_SIZE_FONT=pass`, `manual_visual_review=pass`, overall receipt `passed=true`, 125 deterministic artifacts, full tests, scoped Ruff, diff check, and independent review.
- Do not begin DOCX/PDF integration until this task passes.
