# VEGO-AI Research Workspace

## Structure

Six folders:

```
├── analysis/     # Result synthesis and reporting helpers
├── eval/         # Evaluation scripts and configuration
├── framework/    # Multi-agent pipeline source code
├── inputs/      # Domain descriptions, language bases, scoring schema
├── models/      # Case models by experimental condition
└── reports/     # Generated summaries and dashboards
```

## Main areas

- `framework/` runs the agent pipeline.
- `eval/` scores outputs and produces evaluation artifacts.
- `analysis/` builds dashboards and result summaries.
- `inputs/` stores the fixed research inputs.
- `models/` stores case models grouped by condition.
- `reports/` stores generated, reviewable outputs.

## Human-AI Co-Reasoning Extension

- `docs/human_review_queue.md` documents Milestone 1: selective human-review queue generation.
- `docs/human_feedback_manager.md` documents Milestone 2: validating and attaching structured human feedback to review items.
