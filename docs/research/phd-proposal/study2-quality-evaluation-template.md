# Study 2 blinded human-evaluation template

**Status:** `TEMPLATE_NOT_EXECUTED`
**Purpose:** prepare independent assessment of the shared ON/OFF output objective. No scores are present.

The template is not an accuracy measurement by itself; it becomes evaluable only after independently verified human assessments.

## Blinding and unit

One row represents one condition output for one frozen case. The evaluator
receives a blinded condition label and the same case model/reference package.
The condition label, prompt hashes, run identifiers and system metadata are
not shown during scoring. Two independent assessors score each row; a separate
adjudication record resolves disagreements. Evaluators must not infer that ON
or OFF is preferable from the presentation order.

## Rubric (1–5 ordinal scale)

| Criterion | 1 | 3 | 5 |
|---|---|---|---|
| Factual alignment to case model | Major contradictions | Mixed alignment | No material contradiction observed |
| Coverage of reference guidelines | Most required items absent | Partial coverage | All relevant items addressed |
| Unsupported claims | Many unsupported claims | Some require checking | No material unsupported claim observed |
| Usefulness of uncovered-fragment analysis | Not useful | Some actionable information | Clear and actionable analysis |
| Schema completeness | Missing/invalid required fields | Minor omissions | All required fields complete |

The scale is an assessment aid, not a truth label. Assessors record a short
rationale and an uncertainty flag for every criterion. A blank score is
permitted when the case cannot be judged; it is not silently converted to zero.

## Machine-readable row fields

`evaluation_id`, blinded `condition_token`, `case_id`, `run_id`,
`output_artifact_sha256`, `evaluator_id`, `criterion`, `score_or_blank`,
`rationale`, `uncertainty`, `timestamp`, and `review_status`.

## Analysis gate

No scores, agreement statistic, quality difference, benefit claim or condition
ranking may be generated until the evaluator returns are independently
verified, the adjudication protocol is frozen, and the human-approval gate is
recorded. The fixture suite cannot populate this template.
