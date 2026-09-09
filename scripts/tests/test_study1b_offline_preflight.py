"""The historical Study 1B preflight must now verify closure only."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "study1b_offline_preflight.py"


def _load_module():
    spec = importlib.util.spec_from_file_location("study1b_closure_preflight", SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_closed_preflight_reports_closure_without_running_repeats(tmp_path: Path) -> None:
    module = _load_module()
    output = tmp_path / "receipt.json"
    assert module.main(["--output", str(output)]) == 0
    receipt = json.loads(output.read_text(encoding="utf-8"))
    assert receipt["status"] == "PASS"
    assert receipt["study1b_status"] == "BUDGET_BLOCKED_UNDER_FROZEN_PROTOCOL"
    assert receipt["repeat_execution"] == "NOT_STARTED"
    assert receipt["provider_calls"] == 0
