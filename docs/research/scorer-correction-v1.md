# Scorer correction layer v1 — evidence

A diagnostic study established that agentC systematically over-scores student models
relative to human expert graders, by **+18.0 points on average** across 152 graded cases.
This document records three corrections, the evidence that they work, and the one that
did not.

## 1. The defect

Three concrete mechanisms were identified in agentC's output across the 165 scored cases.

**An uncapped reward channel.** There are 480 reward fragments corpus-wide, worth +240
points. Every one is exactly **+0.50**, flat, with no ceiling. Nothing prevents the total
from exceeding full marks: 23 of 152 cases scored **above 100 %**, one at **122.2 %**
(`cd_pw/70213`: 22.0 points out of a maximum of 18.0, 18 of 18 guidelines Satisfied, zero
penalties, human grade 42.9).

**Rewards granted for text that is itself a criticism.** 36 reward fragments award +0.50
to justifications such as *"SalesStaff class extends Employee but does not provide any new
attributes"*, *"without clear alignment"*, *"lacks operations"*. The channel never inspects
the sentiment of its own stated reason.

**Credit for requirements the notation cannot express.** A UML Use Case Diagram cannot show
a data value, a format or an ordering rule; a UML Class Diagram cannot show behaviour,
permission or temporal sequence. The scorer nonetheless marks such guidelines Satisfied.

## 2. The corrections

| id | correction | principle |
|---|---|---|
| **FIX-1** | a reward may only offset a penalty, never create surplus | full marks already represent complete credit for everything the rubric asked for |
| **FIX-2** | reject any reward whose own justification text is a criticism | a reason that describes a defect cannot justify a reward |
| **FIX-3** | a guideline the notation cannot express earns **partial** credit (0.5), not full | the student may have expressed the intent even where the notation cannot show the detail |

Implemented in `scripts/score_correction.py` as a post-hoc layer over agentC output. It
does **not** modify the scorer, so no protected runtime path is touched.

## 3. Results — 152 graded cases

The credit fraction in FIX-3 was selected by 5-fold cross-validation, choosing on training
folds only. **All five folds independently selected 0.5.**

| | mean gap | bias | better | worse | p |
|---|---|---|---|---|---|
| no correction | 20.27 | **+18.00** | — | — | — |
| **all three, out of fold** | **9.92** | **+1.17** | 114 | 37 | **2.7 × 10⁻¹⁴** |

*gap* = mean │LLM − human│. *bias* = mean (LLM − human); positive means too generous.

The disagreement is **more than halved** and the systematic bias is **eliminated rather
than reversed** — the corrected scorer is neither generous nor harsh on average.

Both notations improve near-identically:

| | gap before → after | bias before → after |
|---|---|---|
| Class Diagrams (n=76) | 19.78 → 10.12 | +17.58 → +1.30 |
| Use Case Diagrams (n=76) | 20.77 → 9.73 | +18.41 → +1.03 |

Cases scoring above 100 % go from **23 to 0**.

### Per-correction contribution

| variant | mean gap | bias |
|---|---|---|
| cap at full marks only | 20.05 | +17.83 |
| FIX-1 only | 17.39 | +14.55 |
| FIX-2 only | 20.00 | +17.78 |
| FIX-3 only (partial credit 0.5) | 12.48 | +5.61 |
| **all three** | **9.92** | **+1.17** |

FIX-3 carries most of the effect; FIX-1 adds materially; FIX-2 is small numerically but
removes a logical defect that should not exist regardless of its size.

## 4. A correction that did NOT work, recorded because it matters

The first form of FIX-3 **dropped** inexpressible guidelines from the denominator instead
of reducing their credit. This made results **worse**: gap 20.27 → 26.4, with 105 of 152
cases moving further from the human grade.

The reason is structural and worth stating: the guidelines a notation cannot express are
also the ones students most often *fail*. Removing them from the denominator therefore
removes mostly-failed items and **inflates** the percentage — the opposite of the intent.
Denying part of the *credit* while keeping the guideline in the denominator is the correct
form.

Similarly, denying credit **entirely** (fraction 0.0) overshoots into under-scoring:
bias −7.7 alone, −12.2 combined with FIX-1. Partial credit is what removes the bias.

## 5. The expressibility coding, independently validated

FIX-3 depends entirely on classifying each of 119 guidelines as expressible or not in its
target notation. That classification was previously a single analyst's judgement and was
the largest unvalidated assumption in the study.

Three analysts re-coded all 119 guidelines **independently** — blind to each other, to the
prior coding, and to every outcome field.

| | value |
|---|---|
| Fleiss κ among the three blind analysts | **0.868** |
| pairwise Cohen κ among them | 0.832 – 0.895 |
| Cohen κ against the prior coding | 0.637 – 0.737 |
| unanimous among the three | 107 / 119 |
| consensus differs from prior coding | 20 / 119 (17 %) |
| guidelines coded *not expressible* | prior 47, consensus **50** |

`configs/guideline-expressibility-v1.json` now ships the **majority consensus**, not the
original coding.

**The correction is insensitive to which coding is used:**

| coding | mean gap | bias | p |
|---|---|---|---|
| prior single-analyst | 9.92 | +1.17 | 2.7 × 10⁻¹⁴ |
| **consensus of three** | **9.75** | **+0.57** | 8.3 × 10⁻¹⁴ |
| analyst A | 9.73 | −1.49 | 9.9 × 10⁻¹³ |
| analyst B | 9.64 | +0.30 | 8.3 × 10⁻¹⁴ |
| analyst C | 9.70 | +1.00 | 3.0 × 10⁻¹⁴ |

## 6. Limitations

- A residual gap of **9.75 points** remains. This halves the problem; it does not solve it.
- 37–44 of 152 cases move **further** from the human grade. The correction is an
  improvement on average, not case by case.
- The credit fraction 0.5 was chosen on this corpus. All five folds agreeing is reassuring
  but it has not been confirmed on data outside these 152 cases.
- 13 further scored cases carry no human grade and could not be used.
- The correction is applied post-hoc. Folding it into agentC itself requires changing
  `VEGO-AI/eval/agentC_case_scorer.py`, which is a protected path.

## 7. Reproducing

```bash
py -3.13 scripts/score_correction.py \
  --eval-output VEGO-AI/eval_output \
  --expressibility configs/guideline-expressibility-v1.json \
  --out corrected-scores.json
```

```bash
py -3.13 -m pytest scripts/tests/test_score_correction.py -q
```
