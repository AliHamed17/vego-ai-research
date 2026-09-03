"""Tests for the public-safe Study 1 measurement receipt."""

from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path

import pytest

from vego_study1.measurement_validation import (
    MeasurementValidationError,
    validate_measurements,
    write_validation_receipt,
)

ROOT = Path(__file__).resolve().parents[2]
RESULTS = (
    ROOT
    / "docs/research/phd-proposal/2026-09-03-supervisor-review-package"
    / "study1-preliminary-results.sanitized.json"
)


def _results() -> dict[str, object]:
    return json.loads(RESULTS.read_text(encoding="utf-8"))


def test_validate_measurements_recomputes_attention_and_recorded_change_metrics() -> None:
    receipt = validate_measurements(_results())

    assert receipt["status"] == "PASS"
    assert receipt["metrics"] == {
        "guideline_not_accepted_share": 0.4024,
        "h2_review_load_share": 0.2809,
        "h2_recorded_change_coverage": 0.9,
        "h2_recorded_change_yield": 0.4202,
        "h2_review_volume_not_selected_share": 0.7191,
        "variability_trigger_share": 0.4074,
        "matched_budgets": {"5_percent": 93, "10_percent": 187, "20_percent": 374},
    }


def test_validate_measurements_rejects_an_inconsistent_stage_total() -> None:
    results = deepcopy(_results())
    results["exp046"]["stage_3_compliance_judgments_reviewed"] = 914

    with pytest.raises(MeasurementValidationError, match="compliance status totals"):
        validate_measurements(results)


def test_validate_measurements_rejects_a_stale_derived_share() -> None:
    results = deepcopy(_results())
    results["exp046"]["stage_3_compliance_overturn_share"] = 0.99

    with pytest.raises(MeasurementValidationError, match="compliance recorded-change share"):
        validate_measurements(results)


def test_write_validation_receipt_writes_canonical_public_json(tmp_path) -> None:
    destination = tmp_path / "measurement-validation.json"

    receipt = write_validation_receipt(RESULTS, destination)

    assert receipt["status"] == "PASS"
    assert json.loads(destination.read_text(encoding="utf-8")) == receipt
    assert destination.read_bytes().endswith(b"\n")
