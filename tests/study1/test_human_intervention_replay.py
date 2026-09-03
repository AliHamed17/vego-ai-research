"""Contract tests for the bounded Study 1 simulated-human correction replay."""

from __future__ import annotations

import json
import subprocess
import sys
from copy import deepcopy
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator

import vego_study1.human_intervention as human_intervention_module
from vego_study1.human_intervention import (
    HumanInterventionValidationError,
    apply_fragment_label_intervention,
    write_intervention_replay,
)

SCORING_SCHEMA = """\
Alternative | +0.5 | Valid alternative
Domain Mistake | -1.0 | Domain error
Language Mistake | -0.5 | Language error
Severity-High | -0.5 | High severity
Severity-Medium | 0.0 | Medium severity
Severity-Low | +0.25 | Low severity
"""

ROOT = Path(__file__).resolve().parents[2]


def _case_record() -> dict:
    return {
        "case_id": "private-case-1",
        "uncovered_fragments": [
            {
                "fragment": "Customer actor",
                "label": "Alternative",
                "severity": "N/A",
                "reason": "Agent rationale",
            },
            {
                "fragment": "Other fragment",
                "label": "Domain Mistake",
                "severity": "Medium",
                "reason": "Other rationale",
            },
        ],
        "fragment_contributions": [
            {
                "fragment": "Customer actor",
                "label": "Alternative",
                "severity": "N/A",
                "base_score": 0.5,
                "severity_modifier": 0.0,
                "total_contribution": 0.5,
                "note": "",
            },
            {
                "fragment": "Other fragment",
                "label": "Domain Mistake",
                "severity": "Medium",
                "base_score": -1.0,
                "severity_modifier": 0.0,
                "total_contribution": -1.0,
                "note": "",
            },
        ],
        "total_score": 2.5,
        "max_score": 4.0,
        "score_pct": 62.5,
    }


def _intervention() -> dict:
    return {
        "schema_version": "study1-human-intervention-v1",
        "intervention_id": "SIM-HI-001",
        "source_kind": "recorded_human_review",
        "human_input_mode": "simulated_from_recorded_review",
        "target_fragment_sha256": (
            "eb2b2b0000307dfff61bd290584327a1bf2eefb1e7364ecbf5ae946424942ea4"
        ),
        "expected_baseline_label": "Alternative",
        "replacement_label": "Language Mistake",
        "replacement_severity": "N/A",
        "reference_status": "development_only",
        "claim_boundary": "technical_propagation_only",
    }


def test_fragment_intervention_propagates_one_recorded_correction_without_mutating_input():
    """A missing score update or broad mutation must fail this test."""
    baseline = _case_record()
    snapshot = deepcopy(baseline)

    assisted, receipt = apply_fragment_label_intervention(
        baseline,
        _intervention(),
        SCORING_SCHEMA,
    )

    assert baseline == snapshot
    assert assisted["uncovered_fragments"][0]["label"] == "Language Mistake"
    assert assisted["fragment_contributions"][0] == {
        "fragment": "Customer actor",
        "label": "Language Mistake",
        "severity": "N/A",
        "base_score": -0.5,
        "severity_modifier": 0.0,
        "total_contribution": -0.5,
        "note": "Simulated bounded human correction; development-only evidence.",
    }
    assert assisted["uncovered_fragments"][1] == baseline["uncovered_fragments"][1]
    assert assisted["fragment_contributions"][1] == baseline["fragment_contributions"][1]
    assert assisted["total_score"] == 1.5
    assert assisted["score_pct"] == 37.5
    assert receipt == {
        "schema_version": "study1-human-intervention-receipt-v1",
        "intervention_id": "SIM-HI-001",
        "case_id_sha256": ("8e88eb1264bcf26886c24643364e4274d35fb88e054bd95d3568bcfd3906e2c5"),
        "target_fragment_sha256": (
            "eb2b2b0000307dfff61bd290584327a1bf2eefb1e7364ecbf5ae946424942ea4"
        ),
        "baseline_label": "Alternative",
        "assisted_label": "Language Mistake",
        "baseline_total_score": 2.5,
        "assisted_total_score": 1.5,
        "baseline_score_pct": 62.5,
        "assisted_score_pct": 37.5,
        "score_delta": -1.0,
        "recorded_review_alignment_before": 0,
        "recorded_review_alignment_after": 1,
        "technical_propagation_success": True,
        "reference_status": "development_only",
        "claim_boundary": "technical_propagation_only",
    }


@pytest.mark.parametrize(
    ("field", "value", "message"),
    [
        ("reference_status", "gold_label", "development_only"),
        ("claim_boundary", "accuracy_improvement", "technical_propagation_only"),
        ("replacement_label", "Reviewer says no", "unsupported replacement_label"),
        ("target_fragment_sha256", "0" * 64, "exactly one fragment"),
    ],
)
def test_fragment_intervention_fails_closed_for_unbounded_or_unmatched_input(
    field: str,
    value: str,
    message: str,
):
    """Relaxing the bounded-development contract must fail this test."""
    intervention = _intervention()
    intervention[field] = value

    with pytest.raises(HumanInterventionValidationError, match=message):
        apply_fragment_label_intervention(_case_record(), intervention, SCORING_SCHEMA)


def test_fragment_intervention_rejects_a_stale_baseline_label():
    """A correction must not apply after the selected baseline item has changed."""
    intervention = _intervention()
    intervention["expected_baseline_label"] = "Not-Satisfied"

    with pytest.raises(HumanInterventionValidationError, match="baseline label changed"):
        apply_fragment_label_intervention(_case_record(), intervention, SCORING_SCHEMA)


def test_writer_keeps_full_assisted_record_private_and_receipt_identifier_free(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
):
    """Writing outside the ignored private zone or leaking the case id must fail this test."""
    repository = tmp_path / "repository"
    repository.mkdir()
    subprocess.run(["git", "init", "-q", str(repository)], check=True)
    (repository / ".gitignore").write_text("research-private/study1/\n", encoding="utf-8")
    monkeypatch.setattr(human_intervention_module, "REPOSITORY_ROOT", repository)

    sources = tmp_path / "sources"
    sources.mkdir()
    case_path = sources / "case.json"
    intervention_path = sources / "intervention.json"
    schema_path = sources / "scoring.txt"
    case_path.write_text(json.dumps(_case_record()), encoding="utf-8")
    intervention_path.write_text(json.dumps(_intervention()), encoding="utf-8")
    schema_path.write_text(SCORING_SCHEMA, encoding="utf-8")
    output_root = repository / "research-private" / "study1" / "feasibility"

    receipt = write_intervention_replay(
        case_path,
        intervention_path,
        schema_path,
        output_root,
    )

    assert receipt["technical_propagation_success"] is True
    assisted = json.loads((output_root / "assisted-case.private.json").read_text("utf-8"))
    saved_receipt_text = (output_root / "receipt.sanitized.json").read_text("utf-8")
    assert assisted["case_id"] == "private-case-1"
    assert "private-case-1" not in saved_receipt_text
    assert json.loads(saved_receipt_text) == receipt


def test_public_intervention_schema_accepts_only_the_bounded_synthetic_contract():
    """The published contract must be valid and must reject outcome claims or raw text."""
    schema = json.loads(
        (ROOT / "schemas/study1/study1-human-intervention-v1.schema.json").read_text(
            encoding="utf-8"
        )
    )
    example = json.loads(
        (ROOT / "schemas/study1/examples/study1-human-intervention-v1.synthetic.json").read_text(
            encoding="utf-8"
        )
    )
    validator = Draft202012Validator(schema)
    validator.validate(example)

    outcome_claim = deepcopy(example)
    outcome_claim["claim_boundary"] = "accuracy_improvement"
    assert list(validator.iter_errors(outcome_claim))

    raw_text = deepcopy(example)
    raw_text["raw_fragment"] = "student text must never enter the public contract"
    assert list(validator.iter_errors(raw_text))


def test_human_intervention_cli_is_directly_executable_from_repository_root():
    """The protocol command must not depend on an undocumented PYTHONPATH mutation."""
    completed = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts/run_study1_human_intervention_feasibility.py"),
            "--help",
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert completed.returncode == 0, completed.stderr
    assert "--private-output-root" in completed.stdout
