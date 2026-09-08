"""The shared cost ceiling must hold across repeats, not just within one.

Study 1B runs the paid harness five times under a single ceiling. If the guard only counted the
current run, five repeats could each spend up to the ceiling. These tests pin the cumulative
behaviour offline; none of them issues a provider request.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location(
    "airtravel_real_run_under_test", ROOT / "scripts" / "airtravel_real_run.py"
)
harness = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = harness
spec.loader.exec_module(harness)

BudgetGuard = harness.BudgetGuard
BudgetExceeded = harness.BudgetExceeded


class _Usage:
    def __init__(self, prompt: int, completion: int) -> None:
        self.prompt_tokens = prompt
        self.completion_tokens = completion


def test_reserve_counts_prior_spend_from_earlier_repeats() -> None:
    """A repeat that starts near the ceiling must refuse immediately."""
    guard = BudgetGuard(budget_usd=2.00, prior_spend_usd=1.999)
    with pytest.raises(BudgetExceeded) as excinfo:
        guard.reserve()
    assert "earlier runs" in str(excinfo.value)
    assert guard.requests == 0


def test_reserve_permitted_when_headroom_remains() -> None:
    guard = BudgetGuard(budget_usd=2.00, prior_spend_usd=0.50)
    guard.reserve()
    assert guard.requests == 1


def test_cumulative_spend_spans_prior_and_current() -> None:
    guard = BudgetGuard(budget_usd=2.00, prior_spend_usd=0.40)
    guard.reserve()
    guard.record(_Usage(1_000_000, 0))
    assert guard.spent_usd == pytest.approx(0.20)
    assert guard.cumulative_spend_usd == pytest.approx(0.60)


def test_ceiling_holds_across_repeats_when_reserving_per_request() -> None:
    """The harness reserves before EVERY request, so a repeat halts mid-way at the ceiling.

    Each repeat here issues many small requests, which is how the real client behaves. The
    cumulative spend must never pass the ceiling, even though no single repeat is aware of the
    others except through prior_spend_usd.
    """
    spend = 0.0
    for _ in range(5):
        guard = BudgetGuard(budget_usd=2.00, prior_spend_usd=spend)
        for _request in range(40):
            try:
                guard.reserve()
            except BudgetExceeded:
                break
            guard.record(_Usage(20_000, 8_000))
        spend += guard.spent_usd
    assert spend <= 2.00


def test_repeat_is_not_started_without_headroom_for_a_full_one() -> None:
    """Starting a repeat that the ceiling will kill mid-way wastes money and yields no denominator."""
    spec_v = importlib.util.spec_from_file_location(
        "study1b_headroom", ROOT / "scripts" / "study1b_variance_runs.py"
    )
    runner = importlib.util.module_from_spec(spec_v)
    sys.modules[spec_v.name] = runner
    spec_v.loader.exec_module(runner)
    assert runner.MIN_HEADROOM_TO_START_USD == pytest.approx(0.134972 * 3)
    # A $2 ceiling with $1.95 already spent leaves too little for a full repeat.
    assert 2.00 - 1.95 < runner.MIN_HEADROOM_TO_START_USD
    # A fresh $2 ceiling comfortably clears it.
    assert 2.00 > runner.MIN_HEADROOM_TO_START_USD


def test_receipt_records_the_ceiling_actually_applied() -> None:
    """A $2 run must not record the module default of $10."""
    guard = BudgetGuard(budget_usd=2.00, prior_spend_usd=0.25, max_requests=50)
    summary = guard.summary()
    assert summary["budget_usd"] == 2.00
    assert summary["outbound_request_cap"] == 50
    assert summary["prior_spend_usd"] == 0.25


def test_request_cap_is_enforced_independently_of_cost() -> None:
    guard = BudgetGuard(budget_usd=1000.0, max_requests=2)
    guard.reserve()
    guard.reserve()
    with pytest.raises(BudgetExceeded) as excinfo:
        guard.reserve()
    assert "request cap" in str(excinfo.value)


def test_defaults_preserve_the_original_frozen_caps() -> None:
    """The Study 1 accepted-run behaviour must be unchanged when no budget is passed."""
    guard = BudgetGuard()
    assert guard.budget_usd == harness.BUDGET_USD == 10.0
    assert guard.max_requests == harness.MAX_OUTBOUND_REQUESTS == 326
    assert guard.prior_spend_usd == 0.0


def test_variance_runner_declares_the_preregistered_repeat_count() -> None:
    """The repeat count is frozen in the preregistration and must not be a CLI argument."""
    spec_v = importlib.util.spec_from_file_location(
        "study1b_under_test", ROOT / "scripts" / "study1b_variance_runs.py"
    )
    runner = importlib.util.module_from_spec(spec_v)
    sys.modules[spec_v.name] = runner
    spec_v.loader.exec_module(runner)
    assert runner.PREREGISTERED_REPEATS == 5
    source = (ROOT / "scripts" / "study1b_variance_runs.py").read_text(encoding="utf-8")
    assert "--repeats" not in source, "repeat count must not be settable from the command line"
