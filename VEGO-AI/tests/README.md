# Tests

Unit and integration tests for the VEGO-AI framework, evaluation pipeline, and human-AI collaboration components.

## Core components

- \	est_llm_client_security.py\ — LLM API client security and error handling
- \	est_memory_advisor.py\ — memory advisory layer (M4A)
- \	est_memory_informed_classifier.py\ — memory-informed comparison (M4B-1)
- \	est_accuracy_improvement_analysis.py\ — accuracy analysis helpers

## Human-AI collaboration (M1-M4)

- \	est_human_review_queue.py\ — human review queue generation and management (M1)
- \	est_human_feedback_manager.py\ — structured feedback validation (M2)
- \	est_human_judgment_memory.py\ — judgment memory storage and retrieval (M3)

## Reporting

- \	est_results_dashboard.py\ — dashboard generation and metrics aggregation
- \	est_visualizer_helpers.py\ — visualizer utilities and diagram rendering

## Running tests

From the \VEGO-AI/\ directory:

\\\ash
pytest tests/ -v                          # Run all tests
pytest tests/test_accuracy_improvement_analysis.py -v  # Single test file
pytest -k "memory_advisor"                # Run tests matching pattern
\\\

All tests must pass before committing changes to the framework.
