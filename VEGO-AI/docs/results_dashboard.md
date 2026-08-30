# Results Dashboard

The results dashboard is a local, offline reporting layer for VEGO-AI research
outputs. It summarizes existing JSON and JSONL artifacts into static HTML plus a
machine-readable snapshot so model-assessment progress can be reviewed without
rerunning agents or changing AI behavior.

## Purpose

- Compare the four standard VEGO-AI settings: `ucd_ch`, `cd_ch`, `ucd_pw`,
  and `cd_pw`.
- Summarize Agent C scores, Agent D variability patterns, and human judgment
  layers from M1-M4A.
- Provide a reproducible, shareable view of current evidence while keeping
  controlled research artifacts out of Git.
- Verify the M4A boundary: memory advice is advisory-only and
  `ai_classification_changed` must remain `false`.

## Inputs

The generator reads existing files only. It does not call APIs, LLMs, network
services, or VEGO-AI agents.

Default input roots are:

- `VEGO-AI/eval_output/<setting>/`
- `VEGO-AI/eval_runs/<setting>/`
- `VEGO-AI/output_runs/<setting>/`
- `VEGO-AI/human_review_output/<setting>/`

Expected file families include:

- `agentC_all_scores.json` and `agentC_case_*.json`
- `agentD_variability_classes*.json`
- `agentD_deviation_patterns*.json`
- `human_review_queue.jsonl`
- `human_review_queue_resolved.jsonl`
- `human_judgment_memory.jsonl`
- `memory_advice.json`

Missing files are recorded as dashboard health issues rather than treated as
fatal errors unless `--strict` is used.

## Outputs

Run:

```powershell
python VEGO-AI/analysis/build_results_dashboard.py --root VEGO-AI --out VEGO-AI/reports/results_dashboard
```

Generated outputs:

- `VEGO-AI/reports/results_dashboard/index.html`
- `VEGO-AI/reports/results_dashboard/metrics_snapshot.json`
- `VEGO-AI/reports/results_dashboard/settings/<setting>.html`

The generated report directory is ignored by Git. Commit the generator, tests,
schema, and documentation, not the generated dashboard files.

Useful options:

```powershell
python VEGO-AI/analysis/build_results_dashboard.py --root VEGO-AI --out VEGO-AI/reports/results_dashboard --json-only
python VEGO-AI/analysis/build_results_dashboard.py --root VEGO-AI --settings ucd_ch cd_ch --strict
python VEGO-AI/analysis/build_results_dashboard.py --root VEGO-AI --human-dir VEGO-AI/human_review_output
```

## Metrics

The dashboard includes:

- Overview KPI cards for cases, scores, variability patterns, human review,
  reusable memory, and M4A classification-change counts.
- Setting comparison tables across the four standard settings.
- Model performance from Agent C score summaries and case-level compliance
  labels.
- Variability patterns from Agent D classifications and recurring pattern
  files.
- Human Review Queue status, trigger, guideline, and pattern-strength counts.
- Human Feedback decision, reusability, and guideline-update counts.
- Human Judgment Memory decision, conflict, guideline, and reusable-scope
  counts.
- Memory Advisory strength, matching, conflict, and
  `ai_classification_changed` counts.
- Health and reproducibility metadata, including Git commit, branch, parser
  issues, and whether baseline result files changed during generation.

## Interpretation

Use the dashboard as an evidence index, not as a new evaluator. It is designed
to help compare settings and identify which parts of the research pipeline have
usable evidence, missing artifacts, or parse issues.

The M4A section is a boundary check. Any nonzero
`ai_classification_changed_count` means the advisory-only invariant has been
violated and the generated output should be treated as invalid for M4A evidence.

## Limitations

- The dashboard is tolerant of evolving JSON shapes and therefore reports
  conservative aggregate metrics.
- It does not validate every source artifact against every VEGO-AI schema.
- It does not implement M4B, reclassify variability patterns, modify Agent 4, or
  change any baseline evaluation output.
- It does not publish controlled artifacts, PDFs, models, analysis spreadsheets,
  or generated evaluation outputs.
