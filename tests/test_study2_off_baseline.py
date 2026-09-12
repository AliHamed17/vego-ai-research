from __future__ import annotations

import asyncio
from pathlib import Path

import pytest
from study2_vego_off_baseline import BaselineOutputValidationError, normalise, run_off_baseline

from vego_study2.config import load_config
from vego_study2.fixtures import DeterministicFixtureClient, fixture_cases

CONFIG_PATH = Path(__file__).resolve().parents[1] / "docs/research/phd-proposal/study2-frozen-config.json"


def test_normalise_rejects_missing_required_arrays() -> None:
    with pytest.raises(BaselineOutputValidationError):
        normalise("01", {"case_id": "01", "existing_mapping": []})


def test_direct_baseline_is_one_call_per_case_and_has_no_qa() -> None:
    config = load_config(CONFIG_PATH)
    client = DeterministicFixtureClient()
    result = asyncio.run(
        run_off_baseline(
            client,
            fixture_cases(config),
            "fixture domain",
            "UML",
            max_concurrent=2,
        )
    )
    assert result["calls"] == 4
    assert result["episodes"] == 0
    assert result["detector_v1_denominator"] == "NOT_APPLICABLE"
    assert set(result["cases"]) == {"01", "02", "03", "04"}
