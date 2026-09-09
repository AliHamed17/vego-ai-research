from __future__ import annotations

import asyncio
from pathlib import Path

import pytest
from study2_vego_off_baseline import OutputSchemaError, normalise, run_off_baseline

from vego_study2.config import load_config
from vego_study2.fixtures import fixture_cases

CONFIG_PATH = Path(__file__).resolve().parents[1] / "docs/research/phd-proposal/study2-frozen-config.json"


def test_normalise_rejects_missing_required_arrays() -> None:
    with pytest.raises(OutputSchemaError):
        normalise("01", {"case_id": "01", "existing_mapping": []})


def test_legacy_direct_baseline_path_is_fail_closed() -> None:
    config = load_config(CONFIG_PATH)

    class Client:
        async def call(self, prompt: dict[str, str], *, label: str) -> dict[str, object]:
            raise AssertionError("legacy OFF execution path must never call a client")

    with pytest.raises(RuntimeError, match="controlled fixture runner"):
        asyncio.run(
            run_off_baseline(
                Client(),
                fixture_cases(config),
                "fixture domain",
                "UML",
                max_concurrent=2,
            )
        )
