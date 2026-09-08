"""The pilot's frozen limits must prove their own bound, and must refuse if they cannot.

Gate 2 of the BUDGET_CONSTRAINED_EXPLORATORY_PILOT protocol requires the total worst-case bound to
be shown to fit the ceiling before any call. These tests pin that gate, the frozen-limit values
themselves, and the separation from Study 1. Nothing here contacts a provider.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
_spec = importlib.util.spec_from_file_location(
    "pilot_cfg_under_test", ROOT / "scripts" / "pilot_budget_constrained_config.py"
)
cfg = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = cfg
_spec.loader.exec_module(cfg)


def test_total_worst_case_bound_fits_the_ceiling() -> None:
    bound = cfg.assert_bound_fits()
    assert bound.fits
    assert bound.total_worst_case_usd == pytest.approx(1.759104, abs=1e-6)
    assert bound.total_worst_case_usd <= cfg.BUDGET_USD


def test_bound_is_the_product_of_every_permitted_call_at_full_reserve() -> None:
    """Not an average, not an extrapolation from a prior run."""
    expected = cfg.per_request_reserve_usd() * cfg.CALL_CAP_PER_REPEAT * cfg.REPEATS
    assert cfg.global_bound().total_worst_case_usd == pytest.approx(expected)


def test_reserve_derives_from_the_frozen_token_limits() -> None:
    expected = (8_000 * 0.20 + 4_096 * 1.20) / 1_000_000
    assert cfg.per_request_reserve_usd() == pytest.approx(expected)


def test_gate_refuses_when_limits_do_not_fit(monkeypatch: pytest.MonkeyPatch) -> None:
    """Raising any limit past the ceiling must block, not warn."""
    monkeypatch.setattr(cfg, "CALL_CAP_PER_REPEAT", 400)
    with pytest.raises(cfg.BoundExceedsCeiling) as excinfo:
        cfg.assert_bound_fits()
    assert "exceeds" in str(excinfo.value)


def test_gate_refuses_a_cap_below_the_protocol_minimum(monkeypatch: pytest.MonkeyPatch) -> None:
    """A cap that cannot complete the protocol is not a pilot, even though it is cheap."""
    monkeypatch.setattr(cfg, "CALL_CAP_PER_REPEAT", 10)
    with pytest.raises(cfg.BoundExceedsCeiling) as excinfo:
        cfg.assert_bound_fits()
    assert "protocol minimum" in str(excinfo.value)


def test_the_study1b_frozen_limits_would_not_have_passed_this_gate() -> None:
    """The rejected Study 1B protocol must remain rejected under the same arithmetic."""
    study1b_reserve = (8_000 * 0.20 + 16_384 * 1.20) / 1_000_000
    study1b_bound = study1b_reserve * 326 * 5
    assert study1b_bound > cfg.BUDGET_USD
    assert study1b_bound == pytest.approx(34.6551, abs=1e-3)


def test_output_ceiling_keeps_headroom_over_the_observed_average() -> None:
    """A ceiling near the observed mean would truncate about half the calls."""
    observed_average_completion = 81_384 / 43
    assert cfg.MAX_OUTPUT_TOKENS / observed_average_completion > 2.0


def test_input_reserve_is_an_upper_bound_not_an_average() -> None:
    observed_average_prompt = 186_558 / 43
    assert cfg.RESERVE_INPUT_TOKENS > observed_average_prompt


def test_repeat_count_and_run_ids_are_frozen() -> None:
    assert cfg.REPEATS == 3
    assert cfg.RUN_IDS == ("PILOT-01", "PILOT-02", "PILOT-03")
    assert len(set(cfg.RUN_IDS)) == cfg.REPEATS
    source = (ROOT / "scripts" / "pilot_budget_constrained_config.py").read_text(encoding="utf-8")
    assert "argparse" not in source, "frozen limits must not be settable from the command line"


def test_config_declares_it_is_not_comparable_with_study1() -> None:
    frozen = cfg.frozen_config()
    assert frozen["study_class"] == "BUDGET_CONSTRAINED_EXPLORATORY_PILOT"
    assert frozen["not_a_replication_of_study1"] is True
    assert frozen["comparable_with_study1"] is False


def test_config_hash_is_stable_and_changes_with_any_limit(monkeypatch: pytest.MonkeyPatch) -> None:
    first = cfg.config_sha256()
    assert first == cfg.config_sha256()
    monkeypatch.setattr(cfg, "MAX_OUTPUT_TOKENS", 2_048)
    assert cfg.config_sha256() != first


def test_egress_allowlist_is_the_provider_host_only() -> None:
    assert cfg.ALLOWED_HOSTS == frozenset({"api.openai.com"})


def test_truncation_marker_is_declared() -> None:
    """Truncation must be detectable, since the reduced ceiling makes it possible."""
    assert cfg.TRUNCATED_FINISH_REASON == "length"
