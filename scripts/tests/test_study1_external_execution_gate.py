from __future__ import annotations

import json
from pathlib import Path

import pytest

from scripts.study1_external_execution_gate import evaluate_gate, run_if_authorized

ROOT = Path(__file__).resolve().parents[2]
CONFIG = ROOT / "docs/research/phd-proposal/text2uml-airtravel/vego-ai-config-airtravel.json"
STAGE = ROOT / "external_data/text2uml/253b26dc704d523209a5cba79686f8f7fab57d63"
AMENDMENT = ROOT / "docs/research/phd-proposal/text2uml-airtravel/amendment-manifest-v1.0.2.json"


def _gate(**overrides: object) -> dict:
    values: dict[str, object] = {
        "config_path": CONFIG,
        "stage_root": STAGE,
        "amendment_manifest": AMENDMENT,
        "current_commit": "e999c480eb6536ab71c1f19e54bf914b9ddbd64b",
        "authorization_path": None,
        "exact_model": None,
        "max_concurrent_cases": 1,
        "call_cap": 16,
        "ci_green": False,
    }
    values.update(overrides)
    return evaluate_gate(**values)  # type: ignore[arg-type]


def test_gate_blocks_before_client_construction() -> None:
    gate = _gate()
    assert gate["status"] == "BLOCKED"
    assert gate["provider_call_permitted"] is False
    constructed: list[bool] = []
    with pytest.raises(RuntimeError):
        run_if_authorized(gate, lambda: constructed.append(True))
    assert constructed == []


def test_each_missing_precondition_blocks() -> None:
    baseline = {
        "exact_model": "approved-model",
        "ci_green": True,
    }
    for missing in ("exact_model", "max_concurrent_cases", "call_cap", "ci_green"):
        values = dict(baseline)
        values[missing] = None if missing != "ci_green" else False
        result = _gate(**values)
        assert result["status"] == "BLOCKED", missing


def test_mismatched_or_unexpired_authorization_is_blocked(tmp_path: Path) -> None:
    auth = tmp_path / "authorization.json"
    auth.write_text(json.dumps({"authorized": True, "commit_sha": "0" * 40, "expires_at": "2099-01-01T00:00:00Z"}), encoding="utf-8")
    result = _gate(authorization_path=auth, exact_model="approved-model", ci_green=True)
    assert result["status"] == "BLOCKED"
    assert any(item["name"] == "hash_bound_human_authorization" and item["status"] == "BLOCKED" for item in result["checks"])


def test_no_raw_inputs_are_persisted_by_gate() -> None:
    result = _gate()
    serialized = json.dumps(result)
    assert "prompt" not in serialized.lower()
    assert "answer" not in serialized.lower()
    assert str(ROOT) not in serialized
