# EXP-046 - What the Recorded Human Review of the Frozen Run Already Shows

Status: analysis tooling added and run on 2026-09-02 over the delivered VEGO-AI dataset. This is the empirical baseline for the single preliminary study (see EXP-045) and for the 2026-09-03 one-page study design.

Related research question: umbrella question -> SQ1 (selective intervention), the "when" component only. Not "how to improve", not "how to approach the user", not accuracy.

## Purpose

The project's own analysis workbooks already contain human judgment about the agent's output: a reviewer went through a sample of the inspector's judgments and of the guidelines the domain advisor wrote, marked each item kept or overturned, and left a written reason. This experiment reads that record as it stands and answers two descriptive questions. Where did a human already change the agent's verdict, at which stage? And does anything the agent itself emits point at those places, so that they could be found automatically?

## Inputs (existing; no LLM call, no pipeline change, nothing new collected)

Delivered with the VEGO-AI dataset and kept OUTSIDE this repository because the workbooks carry student submission ids. Point the script at the directory containing `System/`:

- `System/analysis/guideline_clusters_<setting>.xlsx` - `Status` column (Full / Partially / WRONG / unsure) per guideline the domain advisor wrote, with a `Comment`.
- `System/analysis/scores_<setting>.xlsx` - sheets `compliance_vectors` and `uncovered_fragments`, `Score` column 1 = kept, 0 = overturned, with a `Comment` on the overturned rows.
- `System/analysis/all_scores_published.xlsx` - the agent's `score_pct` beside the course `grade`.
- `System/inputs/<domain>/domain_base_<diagram>.txt` - the course reference (all four now available, including Cheers).
- `System/eval_output/<setting>/agentB_metrics.json` and `agentD_variability_classes*.json`.

The evaluator outputs in the delivered dataset are byte-identical to the frozen run this project already tracks (`agentA_metrics.json` and `agentB_metrics.json` verified for all four settings), so these results and the EXP-045 signal inventory describe the same run.

## Method

```powershell
python scripts/exp046_recorded_review.py --dataset-root <dir containing System> --json reports/generated/exp046/summary.json
$env:VEGO_AI_DATASET_ROOT = "<dir containing System>"; python -m pytest scripts/tests/test_exp046_recorded_review.py -q
```

Read-only over the dataset; writes only the JSON summary passed to `--json`. Deterministic: no randomness, no model call. `openpyxl` is imported lazily, so the script is only needed where the workbooks are.

## Results (2026-09-02)

Stage 2, the guidelines the domain advisor wrote: 186 reviewed, 118 accepted in full, 68 not accepted in full (37%) - 46 partly, 21 wrong, 1 unsure. Separately, 59 requirements in the course reference (78 reference lines across the four settings) have no agent guideline matched to them.

Stage 3, the inspector: 915 guideline-compliance judgments reviewed over 32 model reviews, 120 overturned (13%); 104 alternative-or-mistake judgments reviewed, 27 overturned (26%). Pooled: 147 of 1,019 reviewed items overturned.

Overturn rate by the agent's own verdict on the compliance judgments: `Satisfied` 12 of 658 (1.8%), `Partially-Satisfied` 75 of 162 (46.3%), `Not-Satisfied` 33 of 95 (34.7%). A rule that escalates whenever the agent did not say `Satisfied` flags 257 of 915 items (28%) and covers 108 of the 120 overturns (90%). On the alternative-or-mistake judgments no field separates the overturned cases: the assigned severity does not distinguish them (`N/A` 21 of 84, `Medium` 3 of 11, `High` 2 of 3).

Stage 4: 11 of 27 patterns queued, the only point at which the run asks for a human.

Model level: over the 164 rows where both exist, the agent's score and the course grade correlate at r = 0.25 overall (cd_ch 0.36, ucd_ch 0.26, cd_pw 0.21, ucd_pw 0.02), matching the workbook's own pivot.

## Interpretation

At the inspector stage the agent's own verdict is already a usable escalation signal: reviewing everything it did not call `Satisfied` would have put roughly a quarter of the items in front of a person and reached nine of every ten judgments that person went on to change. At the alternative-or-mistake judgment, and at the domain-guideline stage, no such separator exists in the current output, and the pipeline asks for a human at neither. Those are the places the study points to.

## Limitations

The review is the project's own record, not independent adjudication, and its items were chosen by the reviewer rather than sampled at random, so every rate describes that sample and not the corpus. `Overturned` records a disagreement, not a demonstrated error. The overturn rates by verdict are an association within the reviewed sample; no threshold is fitted or selected here. The course grade and the agent's score measure different things, and the grade is not treated as the correct answer for any single guideline. Stage 1 has no recorded review.

## Claim boundary

Descriptive evidence about where a human already changed a verdict and about what the agent emits at those points. No claim that asking a human improves accuracy, reduces effort, generalizes, or is better; no how-to-improve or how-to-approach-the-user content; nothing here changes the pipeline or the baseline. EXP-005 remains at 0 of 24 generalization-safe expert labels, and none of the counts here is an expert label.

## Reproducibility

Anyone holding the delivered dataset can rerun the command above and obtain the same numbers; the smoke test pins 186/68, 59 of 78, 915/120, 104/27, 1,019/147, the 257/915 and 108/120 trade-off, 11 of 27, and the 164-row correlations, and skips where the dataset is absent, which is the case in CI.
