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
