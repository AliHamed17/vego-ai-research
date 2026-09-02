# -*- coding: utf-8 -*-
"""Smoke test for the EXP-045 descriptive escalation-point inventory.

Runs read-only over the tracked frozen artifacts and pins the denominators that
the 2026-09-03 study-design page cites. Skips if the artifacts are absent.
"""
import json
import os
import pathlib
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

import exp045_escalation_points as exp  # noqa: E402

# The frozen eval_output/human_review_output artifacts are controlled, local-only files
# (not tracked), so CI skips; locally, point VEGO_AI_ROOT at a checkout that has them.
VEGO = pathlib.Path(os.environ.get("VEGO_AI_ROOT", str(ROOT / "VEGO-AI")))


@pytest.fixture(scope="module")
def summary(tmp_path_factory):
    if not (VEGO / "eval_output" / "ucd_ch" / "agentB_metrics.json").exists():
        pytest.skip("frozen eval_output artifacts not present")
    out = tmp_path_factory.mktemp("exp045")
    return exp.run(str(VEGO), str(out)), out


def test_settings_and_stages_present(summary):
    s, _ = summary
    assert set(s["settings"]) == set(exp.SETTINGS)
    for setting in exp.SETTINGS:
        assert set(s["settings"][setting]) == {"stage1", "stage2", "stage3", "stage4"}


def test_stage4_denominators_match_baseline_characterization(summary):
    s, _ = summary
    patterns = {k: v["stage4"]["denominators"]["patterns"] for k, v in s["settings"].items()}
    assert patterns == {"ucd_ch": 8, "ucd_pw": 8, "cd_ch": 4, "cd_pw": 7}
    assert s["totals"]["stage4.queue_items"] == 11


def test_stage2_reference_metrics_are_read_not_computed(summary):
    s, _ = summary
    m = s["settings"]["ucd_ch"]["stage2"]["metrics"]
    assert m["true_positives"] == 6 and m["false_negatives"] == 4
    assert s["settings"]["ucd_ch"]["stage2"]["counts"]["reference_guidelines_missed"] == 4


def test_outputs_written_and_claim_boundary_present(summary):
    s, out = summary
    assert (out / "summary.md").exists()
    for setting in exp.SETTINGS:
        assert (out / f"escalation_points_{setting}.json").exists()
    assert "no claim of improvement" in (out / "summary.md").read_text(encoding="utf-8").lower()
    assert "0/24" in s["claim_boundary"]


def test_no_artifact_is_modified(summary):
    before = {p: p.stat().st_mtime for p in (VEGO / "eval_output").rglob("*.json")}
    exp.run(str(VEGO), str(summary[1]))
    after = {p: p.stat().st_mtime for p in (VEGO / "eval_output").rglob("*.json")}
    assert before == after
