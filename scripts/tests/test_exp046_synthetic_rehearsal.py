# -*- coding: utf-8 -*-
"""Smoke test for the EXP-046 synthetic rehearsal - not expert evidence.

Guards the one property that matters for a rehearsal instrument: every record
is unambiguously marked synthetic, and none of the deterministic rules produce
a disagreement it cannot name. Skips if the dataset is absent, as in CI.
"""
import os
import pathlib
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

import exp046_synthetic_rehearsal as syn  # noqa: E402

DATASET = os.environ.get("VEGO_AI_DATASET_ROOT", "")


@pytest.fixture(scope="module")
def result():
    if not DATASET or not (pathlib.Path(DATASET) / "System" / "analysis").is_dir():
        pytest.skip("VEGO_AI_DATASET_ROOT is not set to a dataset containing System/analysis")
    return syn.build(DATASET)


def test_covers_all_27_patterns(result):
    assert result["counts"]["records"] == 27


def test_every_record_is_marked_synthetic(result):
    assert all(r["reviewerId"] == "SYNTHETIC_NOT_HUMAN" for r in result["records"])
    assert all(r["evidenceClass"] == "SYNTHETIC_NOT_EXPERT_EVIDENCE" for r in result["records"])
    assert all(r["generalizationSafe"] is False for r in result["records"])


def test_every_record_names_the_rule_it_applied(result):
    valid_rules = {rid for rid, _ in syn.RULES}
    assert all(r["appliedRule"] in valid_rules for r in result["records"])


def test_claim_boundary_denies_evidentiary_status(result):
    boundary = result["claimBoundary"].lower()
    assert "not expert evidence" in boundary
    assert "not ground truth" in boundary
    assert "0 of 24" in boundary
