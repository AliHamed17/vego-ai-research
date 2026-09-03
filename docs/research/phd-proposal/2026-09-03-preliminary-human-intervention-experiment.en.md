# Preliminary Experiment: Human Intervention in VEGO-AI

**Prepared for Prof. Iris Reinhartz-Berger | 3 September 2026 | Supervisor-review draft**

## 1. Objective

Investigate whether one bounded human input can resolve selected cases in which autonomous VEGO-AI produces a traceable incomplete, ambiguous, or disputed result. The experiment demonstrates technical feasibility and candidate intervention points; it does not test general human benefit.

## 2. Research Question / Sub-question

Supports the **provisional SQ1:** *When and how, in variability exploration scenarios, should an agentic assessment system request human judgment so that important uncertainties are addressed without unnecessary expert burden?* The wording remains pending supervisor approval.

## 3. Experimental Cases

Use three frozen Cheers/ParkWise cases from observed review strata: **P1**, one recorded classification disagreement; **P2**, one of 17 required guidelines absent from the autonomous output; and **P3**, one non-*Satisfied* model-guideline verdict. Each case has a credible reference: the existing recorded expert review for development, followed by independent blinded review and adjudication before an effectiveness claim. Top-down literature motivates selective review; bottom-up inspection of actual VEGO-AI outputs selects the cases.

## 4. Baseline

**Condition A - Autonomous VEGO-AI.** Preserve and record the frozen output, issue, responsible component, score where applicable, and reference evidence. Do not rerun an agent or modify the baseline.

## 5. Human-Intervention Trigger

P1 reviewer disagreement is **manually identified for this preliminary experiment**; P2 missing-reference detection is measurable only against the frozen reference; P3's non-*Satisfied* verdict is **currently automatically measurable**. No confidence or agent-conflict trigger is claimed because the frozen implementation provides no validated signal for either.

## 6. Human Intervention

**The human intervention is simulated/controlled for this preliminary feasibility experiment and does not constitute a human-subject user study.** The human supplies one bounded item only: correct one classification, add one missing guideline, or validate/reject one verdict. The human does not replace VEGO-AI or provide the complete final answer.

## 7. Human-Assisted Condition

**Condition B - Human-Assisted VEGO-AI.** Apply the single hash-bound human input to the same frozen case, preserve the baseline, and recompute only the dependent classification/score. Record the resulting output and provenance.

## 8. Comparison and Evaluation

No intervention outcome is claimed before independent evaluation.

| Case | Baseline Issue | Trigger | Human Input | Result After Intervention | Reference | Outcome |
| --- | --- | --- | --- | --- | --- | --- |
| P1 | Alternative-or-mistake judgment disputed in recorded review | Recorded disagreement; manual | Correct one bounded classification | Re-evaluate affected classification and score | Recorded expert review; development-only | To be measured independently |
| P2 | Required guideline absent | Missing reference; reference-dependent | Add one missing guideline | Re-evaluate affected inspections | Expert-added required guideline | To be measured |
| P3 | Non-*Satisfied* verdict | Non-*Satisfied*; automatic | Validate or reject one verdict | Recompute affected score | Blinded reviewers plus adjudication | To be measured |

## 9. Expected Preliminary Contribution

Demonstrate the feasibility of incorporating targeted human judgment when selected problematic conditions are detected, and identify candidate points for a later systematic study of when and where intervention is beneficial. **Demonstrate feasibility, not prove effectiveness.**

## 10. Limitations

Three selected cases; controlled/simulated intervention; recorded review is development-only; no real-user evaluation, independent outcome result, statistical claim, or generalisation.
