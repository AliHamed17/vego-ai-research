# EXP-045 - Escalation-Point Demonstration on the Frozen Course Run (Preliminary Study for the Proposal)

Status: descriptive inventory tooling added and run locally on 2026-09-02; blind human marks pending (Sunday 2026-09-06 run). This is the single preliminary study the supervisors asked for on 2026-09-02; it is DESCRIPTIVE and answers only WHEN to escalate.

Related research question: umbrella question -> SQ1 (selective intervention), the "when" component only. Not "how to improve", not "how to approach the user", not accuracy.

## Purpose

Demonstrate - not prove - points in the frozen VEGO-AI run over the Cheers and ParkWise course examples at which asking a human could have helped, and show how those points are identified automatically from signals the pipeline already emits at each stage. Iris Reinhartz-Berger's open question from the call ("how can you say it is better not to intervene at agent 2 rather than agent 3?") is turned into a measurable comparison of where the signals fire and where the reference material disagrees, per stage, on one concrete case, instead of a cost argument.

## Inputs (all existing, immutable, no LLM call)

- Dataset: the frozen run `VEGO-AI/runs/20260614-122150` over 179 student models, 27 recurring patterns, 4 settings (`ucd_ch` 46 models / 8 patterns, `ucd_pw` 44 / 8, `cd_ch` 48 / 4, `cd_pw` 41 / 7). Per-case Agent C score files exist for 165 of the 179 models.
- Per-stage artifacts (local, controlled, ignored by Git): `VEGO-AI/eval_output/<setting>/agentA_guideline_mapping.json`, `agentA_metrics.json`, `agentB_guideline_mapping.json`, `agentB_metrics.json`, `agentC_case_*.json`, `agentD_variability_classes*.json`; `VEGO-AI/human_review_output/<setting>/human_review_queue.jsonl`.
- Reference material (the "benchmark in some sense" Iris pointed to): `VEGO-AI/inputs/language_base_{ucd,cd}.txt` (Stage 1), `VEGO-AI/inputs/pw/domain_base_{ucd,cd}.txt` (Stage 2, ParkWise); the Cheers domain-base files are not in the repository, so the Cheers Stage 2 reference is read from the evaluator record (`agentB_metrics.json` unassigned list, `agentB_guideline_mapping.json` base assignments) and the course file should be recovered from Iris's teaching materials; `VEGO-AI/inputs/scoring_schema.txt` (labels only, Stage 3). Stages 3 and 4 have no reference verdict; the author-reviewed Agent D classes are byte-identical to Agent 4 output (agreement, not ground truth).
- Humans: none this month. For the Sunday run the three of us (Ali, Iris, Arnon) mark, blind to the signals, where they would have wanted to be asked on one case; the marks are stand-ins, and are reported as such.

## Method

Command (read-only over the artifacts; writes only under `reports/generated/exp045/`):

```powershell
python scripts/exp045_escalation_points.py --vego-root VEGO-AI --out reports/generated/exp045
python -m pytest scripts/tests/test_exp045_escalation_points.py -q
```

Stage map (Iris: "template guidelines, inspector, domain guidelines"): Stage 1 = Agent 1 language advisor; Stage 2 = Agent 2 domain advisor; Stage 3 = Agent 3 model inspector; Stage 4 = Agent 4 variability explorer (the only stage with an escalation hook today: `human_review_queue.py`, `PIPELINE_STAGE = agent4_classify_variability`).

Signals read per stage: Stage 1 cluster `match_confidence` not High or no `base_assignment`, and language-base constructs not reached; Stage 2 `mapping_certainty` < 0.8 or no base match, open `questions_to_language_advisor` in the best-run guideline set (12 across settings, none answered), and reference guidelines with no Agent 2 match (`unassigned_base_guidelines`, equal to the evaluator's false negatives); Stage 3 uncovered fragments labelled `Alternative` and mistakes with `severity` High; Stage 4 `confidence` Low/Medium, `requires_human_review`, `flag_for_guidelines_update`, `Undetermined`, plus the M1 queue items and `trigger_reasons`.

Measures (all descriptive, numerator / denominator): candidate points per stage over the stage's own denominator (clusters, reference guidelines, case files, patterns); overlap between automatic points and reference disagreements where a reference exists (Stages 1-2); on the Sunday case, agreement between automatic points and the three blind human marks per stage (counts, not rates of correctness).

Randomness: none. Runs: 1 deterministic inventory; Sunday adds the blind marks on one case.

## Results (2026-09-02 inventory over the local frozen artifacts)

| Stage | Signal / denominator | ucd_ch | ucd_pw | cd_ch | cd_pw | Total |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| 1 | language clusters not High-confidence or unassigned / clusters | 0/8 | 2/9 | 2/10 | 2/11 | 6/38 |
| 1 | language-base constructs not reached / base constructs | 0/8 | 1/8 | 3/12 | 3/12 | 7/40 |
| 2 | domain clusters low-certainty or no base match / clusters | 8/12 | 7/8 | 3/4 | 0/4 | 18/28 |
| 2 | guidelines with an open question to the language advisor / best-run guidelines | 2/27 | 1/48 | 3/26 | 6/18 | 12/119 |
| 2 | reference domain guidelines with no Agent 2 match / reference guidelines (as recorded by the evaluator) | 4/10 | 17/24 | 22/26 | 16/20 | 59/80 |
| 3 | case files with at least one Alternative fragment / case files | 40/45 | 34/37 | 44/46 | 32/37 | 150/165 |
| 3 | fragments labelled Alternative (count) / case files | 113/45 | 95/37 | 154/46 | 129/37 | 491/165 |
| 3 | High-severity mistakes / case files | 0/45 | 0/37 | 3/46 | 12/37 | 15/165 |
| 4 | patterns with a queue-trigger signal / patterns | 4/8 | 5/8 | 2/4 | 0/7 | 11/27 |
| 4 | M1 queue items actually created / patterns | 4/8 | 5/8 | 2/4 | 0/7 | 11/27 |

Reading: today nothing before Stage 4 is escalated. Stage 2 is where the reference disagrees most (59 of 80 reference domain guidelines missed) and where the agent's own certainty signal is already low on 18 of 28 clusters; Stage 3 produces the largest volume of ambiguity signals (150 of 165 case files carry at least one Alternative fragment; 491 such fragments in total); Stage 4 escalates 11 of 27 patterns, 9 of them for a proposed guideline update and 3 for medium confidence. These are counts of signal values, not verified errors.

## Interpretation

The counts locate, per stage, where a "when to ask" trigger would have fired if one existed, and they show that the existing hook at Stage 4 sees none of the Stage 2 disagreement. Whether asking at Stage 2 rather than Stage 3 (or vice versa) is preferable is not decided here; the Sunday case study measures how a Stage 2 point propagates into Stage 3 and Stage 4 outputs for one case, and whether the three blind marks fall where the signals fire.

## Limitations

No independent labels (EXP-005 0/24); no users; the three supervisors are stand-ins, not participants; the reference at Stages 1-2 is the course base, not an adjudicated ground truth (and for Cheers only the evaluator-recorded projection of it is available locally); Stage 3-4 points have no reference at all; the inventory covers one frozen run with one model version; the 0.8 certainty threshold is a declared reading threshold, not a fitted one.

## Claim boundary

Descriptive evidence only: where and by which existing signal a human could have been asked. No claim that asking improves accuracy, reduces effort, generalizes, or is "better"; no how-to-improve or how-to-approach-the-user content; nothing here changes Agent 4 or the baseline.

## Reproducibility

Anyone with the local controlled `eval_output/` and `human_review_output/` folders and the tracked `inputs/` can rerun the command above and obtain the same table; the smoke test pins the denominators (8/8/4/7 patterns, 11 queue items, ucd_ch Stage 2 TP 6 / FN 4) and checks that no artifact is modified. In CI, where the controlled folders are absent, the test skips.
