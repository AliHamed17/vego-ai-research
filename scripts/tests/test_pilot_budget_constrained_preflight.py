"""Tests for the offline pilot preflight's fake-call accounting."""

from __future__ import annotations

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "pilot_budget_constrained_preflight.py"


def _load_module():
    spec = importlib.util.spec_from_file_location("pilot_preflight_under_test", SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_preflight_counts_fake_requests_without_calling_a_provider() -> None:
    module = _load_module()
    module.FAKE_CALLS["count"] = 0
    result = module.FakeRepeat("PILOT-01", calls=3).execute()
    assert result["calls"] == 3
    assert module.FAKE_CALLS["count"] == 3
    assert result["provider_calls"] == 0
