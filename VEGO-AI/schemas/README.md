# Schemas

JSON schema definitions for VEGO-AI evaluation and human-AI collaboration artifacts.

## Human feedback & judgment (M1-M4)

- \human_review_item.schema.json\ — item in the human review queue (M1)
- \human_feedback.schema.json\ — structured feedback record (M2)
- \human_judgment.schema.json\ — reusable human judgment with provenance (M3)
- \memory_advice.schema.json\ — memory-informed advisory suggestions (M4A)
- \memory_informed_comparison.schema.json\ — parallel comparison of original and memory-informed classifications (M4B-1)

## Results & reporting

- \esults_dashboard_snapshot.schema.json\ — snapshot of dashboard metrics and KPIs

## Purpose

Each schema defines the expected structure of its corresponding artifact. Validation is performed during:
- Artifact generation (framework/eval/analysis)
- Dashboard ingestion (VEGO-AI/analysis/build_results_dashboard.py)
- Testing (VEGO-AI/tests/)
