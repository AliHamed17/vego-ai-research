"""Unit tests for the v4 offline fake-provider executor.

These tests exercise only deterministic helpers and temporary fixture runs;
they never consume the private grant or invoke a real provider.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))


def runner():
    import airtravel_v4_execution

    return airtravel_v4_execution


def test_call_row_is_privacy_safe_and_preserves_inventory():
    raw = {
        "label": "agent3/01/resolve_r2",
        "phase": "phase3",
        "case_id": "01",
        "inventory_row": "P3_RESOLVE_PRODUCER",
        "prompt_sha256": "a" * 64,
        "answer_sha256": "b" * 64,
        "decision_sha256": "c" * 64,
        "prompt_length": 12,
        "answer_length": 18,
    }
    result = runner().privacy_safe_call_row(raw, 1)
    assert result["sequence"] == 1
    assert result["source_agent"] == "agent3"
    assert result["target_agent"] == "orchestrator"
    assert result["fake_client_identity"] == "LOCAL_DETERMINISTIC_FAKE_V4"
    assert "prompt" not in result and "answer" not in result


@pytest.mark.parametrize("label", ["agent1/build_language_template", "agent4/identify_patterns"])
def test_call_row_rejects_missing_inventory(label):
    with pytest.raises(ValueError, match="inventory"):
        runner().privacy_safe_call_row(
            {
                "label": label,
                "prompt_sha256": "a" * 64,
                "answer_sha256": "b" * 64,
                "decision_sha256": "c" * 64,
            },
            1,
        )


def test_output_inventory_is_stable_and_excludes_itself(tmp_path):
    (tmp_path / "baseline").mkdir()
    (tmp_path / "baseline" / "call-records.jsonl").write_text("x", encoding="utf-8")
    first = runner().output_inventory(tmp_path)
    second = runner().output_inventory(tmp_path)
    assert first == second
    assert "verification/final-output-inventory.json" not in first


def test_network_guard_rejects_provider_import():
    assert runner().OFFLINE_PROVIDER_IMPORTS
    assert "openai" in runner().OFFLINE_PROVIDER_IMPORTS
