from __future__ import annotations

import pathlib
import sys
from dataclasses import FrozenInstanceError

import pytest

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


@pytest.mark.parametrize(("n", "minimum", "maximum"), [(0, 4, 82), (1, 7, 143), (4, 16, 326)])
def test_call_site_plan_derives_historical_bounds(n, minimum, maximum) -> None:
    assert hasattr(bound, "derive_call_bounds"), "inspectable call plan is missing"
    result = bound.derive_call_bounds(n)
    assert result["minimum_calls"] == minimum
    assert result["worst_case_calls"] == maximum
    assert result["scope"] == "LEGACY_STATIC_REFERENCE_NOT_EXECUTION_BUDGET"
    assert result["status"] == "PASS"
    assert result["phase_minimum_calls"] == {"phase1": 1, "phase2": 1, "phase3": 3 * n, "phase4": 2}
    assert result["phase_worst_case_calls"] == {
        "phase1": 1,
        "phase2": 30,
        "phase3": 61 * n,
        "phase4": 51,
    }


def test_call_plan_is_immutable() -> None:
    assert hasattr(bound, "CALL_SITES"), "inspectable call plan is missing"
    assert isinstance(bound.CALL_SITES, tuple)
    with pytest.raises(FrozenInstanceError):
        bound.CALL_SITES[0].minimum_visits = 20


@pytest.mark.parametrize("value", [-1, True, 1.5, "4"])
def test_all_bound_consumers_reject_invalid_case_counts(value) -> None:
    for fn in (bound.minimum_calls, bound.worst_case_calls, bound.call_bound_breakdown):
        with pytest.raises(ValueError):
            fn(value)


@pytest.mark.parametrize(
    ("old", "new"),
    [
        ('label="agent1/build_language_template"', 'label="drift"'),
        ("MAX_QA_ROUNDS = 10", "MAX_QA_ROUNDS = 11"),
        ("range(1, MAX_QA_ROUNDS + 1)", "range(1, MAX_QA_ROUNDS + 2)"),
    ],
)
def test_static_source_drift_blocks_reference_claim(tmp_path, old, new) -> None:
    assert hasattr(bound, "derive_call_bounds"), "static source verification is missing"
    source = (ROOT / "VEGO-AI/framework/orchestrator.py").read_text(encoding="utf-8")
    changed = tmp_path / "orchestrator.py"
    changed.write_text(source.replace(old, new, 1), encoding="utf-8")
    result = bound.derive_call_bounds(4, source_path=changed)
    assert result["status"] == "BLOCKED"
    assert result["minimum_calls"] is None
    assert result["worst_case_calls"] is None


def test_missing_source_fails_closed(tmp_path) -> None:
    assert hasattr(bound, "derive_call_bounds"), "static source verification is missing"
    assert bound.derive_call_bounds(4, source_path=tmp_path / "missing")["status"] == "BLOCKED"
