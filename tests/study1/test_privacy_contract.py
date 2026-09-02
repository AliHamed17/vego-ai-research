import json
import subprocess
import sys
from pathlib import Path

import pytest

from vego_study1.privacy import (
    PrivacyValidationError,
    validate_candidate_event,
    validate_tracked_artifacts,
)

ROOT = Path(__file__).resolve().parents[2]
SCHEMA_PATH = ROOT / "schemas" / "study1" / "CandidateEscalationEvent-v1.schema.json"
EXAMPLE_PATH = ROOT / "schemas" / "study1" / "examples" / "candidate-escalation-event-v1.synthetic.json"
VALIDATOR_SCRIPT = ROOT / "scripts" / "validate_study1_privacy.py"
REVIEW_POLICY_SIGNAL_IDS = (
    "claim_uncertainty",
    "unreviewed_error_consequence",
    "evidence_quality",
    "reviewer_competence_for_claim",
    "current_queue_conditions",
    "novelty_vs_judgment_store",
    "cross_agent_disagreement",
    "expected_future_reuse_value",
)


def synthetic_event() -> dict:
    return {
        "schema_version": "CandidateEscalationEvent-v1",
        "event_id": "8d9f2f51-3f06-4569-9a99-9a12a3286c34",
        "source": {"source_hash": "sha256:" + "a" * 64},
        "stage": "case_inspection",
        "item_type": "candidate_interaction",
        "sanitized_local_locator": {
            "storage_scope": "private_workspace",
            "locator_hash": "sha256:" + "b" * 64,
        },
        "signals": [
            {"signal_id": signal_id, "observation": "present", "evidence_state": "observed"}
            for signal_id in REVIEW_POLICY_SIGNAL_IDS
        ],
        "claim_boundary": "candidate_escalation_only",
    }


def test_schema_and_public_example_validate_a_synthetic_candidate_event():
    """Catches a missing or invalid published event-contract artifact."""
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    example = json.loads(EXAMPLE_PATH.read_text(encoding="utf-8"))

    assert validate_candidate_event(synthetic_event(), schema=schema) == synthetic_event()
    assert validate_candidate_event(example, schema=schema)["claim_boundary"] == "candidate_escalation_only"


@pytest.mark.parametrize(
    ("mutate", "expected_message"),
    [
        (lambda event: event["signals"].__setitem__(0, {"signal_id": "unknown_signal", "observation": "present", "evidence_state": "observed"}), "unknown signal"),
        (lambda event: event["source"].pop("source_hash"), "source_hash"),
        (lambda event: event["signals"][0].pop("evidence_state"), "evidence_state"),
        (lambda event: event["sanitized_local_locator"].update({"raw_locator": "synthetic-local-item"}), "raw locator"),
        (lambda event: event.__setitem__("claim_boundary", "verified_finding"), "claim_boundary"),
    ],
)
def test_event_validator_rejects_privacy_or_claim_contract_violations(mutate, expected_message):
    """Catches validation branches that would admit unsafe candidate events."""
    event = synthetic_event()
    mutate(event)

    with pytest.raises(PrivacyValidationError, match=expected_message):
        validate_candidate_event(event)


def test_event_validator_accepts_derived_evidence_state():
    """Catches a contract that rejects the required derived evidence state."""
    event = synthetic_event()
    event["signals"][0]["evidence_state"] = "derived"

    assert validate_candidate_event(event)["signals"][0]["evidence_state"] == "derived"


def test_event_validator_rejects_non_contract_evidence_state():
    """Catches a contract that admits evidence states outside the three-state vocabulary."""
    event = synthetic_event()
    event["signals"][0]["evidence_state"] = "not_applicable"

    with pytest.raises(PrivacyValidationError, match="evidence_state"):
        validate_candidate_event(event)


def test_event_validator_rejects_duplicate_signal_id_even_when_observations_differ():
    """Catches eight distinct signal objects that do not cover all eight policy signals."""
    event = synthetic_event()
    event["signals"][-1] = {
        "signal_id": "claim_uncertainty",
        "observation": "second synthetic observation",
        "evidence_state": "observed",
    }

    with pytest.raises(PrivacyValidationError, match="exactly one observation"):
        validate_candidate_event(event)


def test_event_validator_rejects_non_uuid_event_id():
    """Catches schema-only UUID annotations that do not validate helper input."""
    event = synthetic_event()
    event["event_id"] = "synthetic-event-id"

    with pytest.raises(PrivacyValidationError, match="event_id"):
        validate_candidate_event(event)


def test_event_validator_rejects_legacy_signal_id():
    """Catches a contract that accepts identifiers outside ReviewPolicySignalContract-v1."""
    event = synthetic_event()
    event["signals"][0]["signal_id"] = "prompt_scope"

    with pytest.raises(PrivacyValidationError, match="unknown signal"):
        validate_candidate_event(event)


def test_event_validator_rejects_routing_outcome_as_stage():
    """Catches a stage vocabulary that encodes routing outcomes instead of policy workflow stages."""
    event = synthetic_event()
    event["stage"] = "triaged"

    with pytest.raises(PrivacyValidationError, match="stage"):
        validate_candidate_event(event)


def test_tracked_artifact_validator_reports_only_unsafe_synthetic_markers(tmp_path):
    """Catches a scanner that misses proposed tracked-artifact privacy leaks."""
    safe = tmp_path / "safe.json"
    safe.write_text('{"source_hash": "sha256:synthetic"}', encoding="utf-8")
    unsafe = tmp_path / "unsafe.txt"
    unsafe.write_text(
        "\n".join(
            (
                "RAW_" + "CONTROLLED_CONTENT",
                "https://" + "drive.google.com/file/d/" + "1" + "abcdefghijklmnopqrstuvwxYZ",
                "API_" + "KEY=synthetic-token-value",
            )
        ),
        encoding="utf-8",
    )

    findings = validate_tracked_artifacts([safe, unsafe])

    assert [finding.kind for finding in findings] == ["controlled_content_marker", "drive_url", "drive_id", "credential_like"]
    assert all(finding.path == unsafe for finding in findings)


def test_privacy_validator_cli_accepts_the_public_synthetic_example():
    """Catches direct CLI execution that loses the repository src import path."""
    result = subprocess.run(
        [sys.executable, str(VALIDATOR_SCRIPT), str(EXAMPLE_PATH)],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
