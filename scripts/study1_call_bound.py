"""Static Study 1 provider-call bounds (no provider access)."""

MAX_QA_ROUNDS = 10
MIN_BASE = 4
MIN_PER_CASE = 3
WORST_BASE = 82
WORST_PER_CASE = 61


def minimum_calls(case_count: int) -> int:
    if case_count < 0:
        raise ValueError("case_count must be non-negative")
    return MIN_BASE + MIN_PER_CASE * case_count


def worst_case_calls(case_count: int) -> int:
    if case_count < 0:
        raise ValueError("case_count must be non-negative")
    return WORST_BASE + WORST_PER_CASE * case_count


def call_bound_breakdown(case_count: int) -> dict[str, object]:
    """Return the control-flow accounting used by the offline authorization gate."""
    if case_count < 0:
        raise ValueError("case_count must be non-negative")
    return {
        "case_count": case_count,
        "max_qa_rounds": MAX_QA_ROUNDS,
        "fixed_calls": MIN_BASE,
        "per_case_calls": MIN_PER_CASE * case_count,
        "qa_dependent_minimum": 0,
        "qa_dependent_worst_case": 78,
        "maximum_calls_per_round": {"phase2": 3, "phase3_each_skill": 3, "phase4_classify": 3, "phase4_feedback": 2},
        "minimum_formula": "4 + 3N",
        "worst_case_formula": "82 + 61N",
        "minimum_calls": minimum_calls(case_count),
        "worst_case_calls": worst_case_calls(case_count),
        "discrepancy_resolution": "6 + 3N counts optional Phase 2/4 Q&A as mandatory; 4 + 3N is the direct no-question path.",
    }


def fake_client_call_counter(case_count: int, qa_dependent_calls: int = 0) -> dict[str, int]:
    """Count deterministic baseline calls without constructing provider clients."""
    if case_count < 0 or qa_dependent_calls < 0:
        raise ValueError("counts must be non-negative")
    per_case = MIN_PER_CASE * case_count
    return {"fixed_calls": MIN_BASE, "per_case_calls": per_case, "qa_dependent_calls": qa_dependent_calls, "total_calls": MIN_BASE + per_case + qa_dependent_calls}
