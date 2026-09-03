"""Direct-CLI regression test for the public Study 1 measurement receipt."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RESULTS = (
    ROOT
    / "docs/research/phd-proposal/2026-09-03-supervisor-review-package"
    / "study1-preliminary-results.sanitized.json"
)


def test_measurement_validation_cli_writes_a_passing_receipt(tmp_path: Path) -> None:
    destination = tmp_path / "receipt.json"

    completed = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts/validate_study1_measurements.py"),
            "--input",
            str(RESULTS),
            "--output",
            str(destination),
        ],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )

    assert completed.returncode == 0, completed.stderr
    assert "PASS" in completed.stdout
    receipt = json.loads(destination.read_text(encoding="utf-8"))
    assert receipt["metrics"]["h2_recorded_change_coverage"] == 0.9
    assert receipt["claim_boundary"].startswith("arithmetic_and_reproducibility")
