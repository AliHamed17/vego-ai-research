from __future__ import annotations

import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

import study1_call_bound as bound  # noqa: E402


def test_minimum_bound_matches_control_flow() -> None:
    assert bound.minimum_calls(0) == 4
    assert bound.minimum_calls(7) == 4 + 3 * 7


def test_worst_case_bound_matches_documented_derivation() -> None:
    assert bound.worst_case_calls(0) == 82
    assert bound.worst_case_calls(7) == 82 + 61 * 7


def test_negative_case_count_fails_closed() -> None:
    for fn in (bound.minimum_calls, bound.worst_case_calls):
        try:
            fn(-1)
        except ValueError:
            pass
        else:
            raise AssertionError("negative case count was accepted")


def test_fake_counter_reports_fixed_per_case_and_qa_components() -> None:
    assert bound.fake_client_call_counter(0) == {
        "fixed_calls": 4,
        "per_case_calls": 0,
        "qa_dependent_calls": 0,
        "total_calls": 4,
    }
    assert bound.fake_client_call_counter(1) == {
        "fixed_calls": 4,
        "per_case_calls": 3,
        "qa_dependent_calls": 0,
        "total_calls": 7,
    }
    assert bound.fake_client_call_counter(4) == {
        "fixed_calls": 4,
        "per_case_calls": 12,
        "qa_dependent_calls": 0,
        "total_calls": 16,
    }


def test_call_bound_breakdown_accounts_for_max_rounds() -> None:
    breakdown = bound.call_bound_breakdown(4)
    assert breakdown["max_qa_rounds"] == 10
    assert breakdown["minimum_formula"] == "4 + 3N"
    assert breakdown["worst_case_formula"] == "82 + 61N"
    assert breakdown["worst_case_calls"] == 326
