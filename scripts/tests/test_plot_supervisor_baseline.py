"""Tests for the descriptive supervisor baseline plots."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

from plot_supervisor_baseline import DATA_PATH, build_figures, load_data  # noqa: E402


def test_plot_data_contains_only_pinned_descriptive_aggregates() -> None:
    data = load_data()
    assert data["evidence_status"] == "DESCRIPTIVE_ONLY"
    assert [row["numerator"] for row in data["signal_rows"]] == [6, 18, 59, 150, 11]
    assert [row["denominator"] for row in data["signal_rows"]] == [38, 28, 80, 165, 27]
    assert [row["numerator"] for row in data["review_rows"]] == [120, 27, 147, 257]
    assert [row["denominator"] for row in data["review_rows"]] == [915, 104, 1019, 915]
    assert all("private" not in str(row).lower() for row in data["signal_rows"] + data["review_rows"])


def test_plot_data_rejects_invalid_denominator(tmp_path: Path) -> None:
    bad = json.loads(DATA_PATH.read_text(encoding="utf-8"))
    bad["signal_rows"][0]["denominator"] = 0
    path = tmp_path / "bad.json"
    path.write_text(json.dumps(bad), encoding="utf-8")
    with pytest.raises(ValueError, match="numerator/denominator"):
        load_data(path)


def test_build_figures_writes_both_formats_and_receipt(tmp_path: Path) -> None:
    out_dir = tmp_path / "figures"
    receipt = build_figures(load_data(), out_dir)
    assert receipt["evidence_status"] == "DESCRIPTIVE_ONLY"
    assert len(receipt["figures"]) == 2
    for figure in receipt["figures"]:
        for field in ("png", "svg", "png_sha256", "svg_sha256"):
            assert figure[field]
        assert (out_dir / Path(figure["png"]).name).is_file()
        assert (out_dir / Path(figure["svg"]).name).is_file()
    receipt_path = tmp_path / "2026-09-06-tomorrow-baseline-figure-receipt.json"
    assert receipt_path.is_file()
    assert json.loads(receipt_path.read_text(encoding="utf-8"))["qa"]["no_provider_or_network"] is True


def test_cli_is_local_and_non_executing(tmp_path: Path) -> None:
    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "plot_supervisor_baseline.py"), "--out-dir", str(tmp_path / "figures")],
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(result.stdout)
    assert payload["evidence_status"] == "DESCRIPTIVE_ONLY"
    source = (ROOT / "scripts" / "plot_supervisor_baseline.py").read_text(encoding="utf-8").lower()
    assert "openai" not in source
    assert "requests" not in source
    assert "urllib" not in source
    assert "httpx" not in source
    assert "socket" not in source
    assert "https://" not in source
