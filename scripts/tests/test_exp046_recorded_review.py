# -*- coding: utf-8 -*-
"""Smoke test for the EXP-046 recorded-review analysis.

The analysis workbooks ship with the VEGO-AI dataset and are kept outside the
repository because they carry student submission ids, so this test skips unless
VEGO_AI_DATASET_ROOT points at a directory containing System/. It pins the
figures quoted in the 2026-09-03 one-page study design.
"""
import os
import pathlib
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

import exp046_recorded_review as exp  # noqa: E402

DATASET = os.environ.get("VEGO_AI_DATASET_ROOT", "")


@pytest.fixture(scope="module")
def result():
    if not DATASET or not (pathlib.Path(DATASET) / "System" / "analysis").is_dir():
        pytest.skip("VEGO_AI_DATASET_ROOT is not set to a dataset containing System/analysis")
    pytest.importorskip("openpyxl")
    return exp.run(DATASET)


def test_stage2_guideline_review(result):
    s2 = result["stage2_guideline_review"]
    assert s2["reviewed"] == 169
    assert s2["accepted_in_full"] == 101
    assert s2["not_accepted_in_full"] == 68
    assert s2["breakdown"]["wrong"] == 21
    assert s2["absent_no_run_wrote_it"] == 17


def test_stage2_reference_coverage(result):
    cov = result["stage2_reference_coverage"]
    assert cov["unmatched"] == 59
    assert cov["reference_lines"] == 78
    assert cov["per_setting"]["ucd_ch"]["reference_lines"] == 9


def test_stage3_review_and_overturn_rates(result):
    s3 = result["stage3_review"]
    assert (s3["compliance_vectors"]["reviewed"], s3["compliance_vectors"]["overturned"]) == (915, 120)
    assert (s3["uncovered_fragments"]["reviewed"], s3["uncovered_fragments"]["overturned"]) == (104, 27)
    by = s3["compliance_vectors"]["by_agent_verdict"]
    assert by["Satisfied"]["overturn_rate"] < 0.05
    assert by["Partially-Satisfied"]["overturn_rate"] > by["Not-Satisfied"]["overturn_rate"] > by["Satisfied"]["overturn_rate"]
    assert result["pooled_review"] == {"items_reviewed": 1019, "items_overturned": 147}


def test_escalation_rule_trade_off(result):
    rule = result["stage3_escalation_rule"]
    assert (rule["items_flagged"], rule["items_total"]) == (257, 915)
    assert (rule["overturns_covered"], rule["overturns_total"]) == (108, 120)
    assert round(rule["share_flagged"], 2) == 0.28
    assert round(rule["share_of_overturns_covered"], 2) == 0.90


def test_stage4_queue_and_grade_association(result):
    q = result["stage4_queue"]
    assert (q["queued"], q["patterns"]) == (11, 27)
    g = result["score_versus_course_grade"]
    assert g["rows"] == 164
    assert round(g["correlation"], 2) == 0.25
    assert round(g["per_setting"]["ucd_pw"]["correlation"], 2) == 0.02


def test_claim_boundary_is_stated(result):
    boundary = result["claim_boundary"].lower()
    assert "not that the system was proven wrong" in boundary
    assert "not independent adjudication" in boundary
    assert "0/24" in boundary
