"""Compatibility tests for the binding-required Study 1 validator CLI."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest
from test_study1_evidence_recovery import _valid_fixture

ROOT = Path(__file__).resolve().parents[2]
VALIDATOR = ROOT / "scripts" / "study1_validate_evidence.py"


def run_validator(*args: str) -> tuple[int, dict]:
    process = subprocess.run(
        [sys.executable, str(VALIDATOR), *args],
        capture_output=True,
        text=True,
        cwd=ROOT,
    )
    return process.returncode, json.loads(process.stdout)


def test_legacy_invocation_without_binding_is_unavailable(tmp_path: Path):
    output = tmp_path / "safe.json"
    code, summary = run_validator(
        "--run-root",
        str(tmp_path / "not-mounted"),
        "--manifest",
        str(output),
    )
    assert code == 2
    assert summary["status"] == "EVIDENCE_NOT_AVAILABLE_IN_REVIEWED_WORKTREE"
    payload = json.loads(output.read_text(encoding="utf-8"))
    assert payload["recomputed"] is None


def test_explicit_binding_delegates_to_recovery(tmp_path: Path):
    _, evidence, binding = _valid_fixture(tmp_path)
    output = tmp_path / "safe.json"
    code, summary = run_validator(
        "--run-root",
        str(evidence),
        "--binding-manifest",
        str(binding),
        "--manifest",
        str(output),
    )
    assert code == 0
    assert summary["status"] == "ACCEPTED_FOR_DESCRIPTIVE_REPORTING_WITH_RETROSPECTIVE_PROVENANCE"
    assert json.loads(output.read_text(encoding="utf-8"))["recomputed"]["questions"] == 1


def test_existing_output_is_not_overwritten(tmp_path: Path):
    output = tmp_path / "foreign.json"
    output.write_text('{"owner":"other"}\n', encoding="utf-8")
    code, summary = run_validator(
        "--run-root",
        str(tmp_path / "not-mounted"),
        "--manifest",
        str(output),
    )
    assert code == 3
    assert summary["status"] == "OUTPUT_EXISTS"
    assert json.loads(output.read_text(encoding="utf-8"))["owner"] == "other"


@pytest.mark.parametrize("name", ["study1_evidence_recovery.py", "study1_validate_evidence.py"])
def test_validator_modules_have_no_provider_imports(name: str):
    source = (ROOT / "scripts" / name).read_text(encoding="utf-8").lower()
    assert "openai" not in source
    assert "anthropic" not in source
