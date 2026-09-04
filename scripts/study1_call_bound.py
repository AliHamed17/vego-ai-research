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
