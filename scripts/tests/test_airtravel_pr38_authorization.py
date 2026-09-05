"""Authorization contracts only; no exact configuration is executed."""

import importlib
import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))


def contract():
    assert importlib.util.find_spec("airtravel_preflight_contract") is not None
    return importlib.import_module("airtravel_preflight_contract")


def test_request_packet_without_grant_fails_before_runtime(tmp_path):
    import prepare_airtravel_protected_fake_preflight as harness

    packet = tmp_path / "request.md"
    packet.write_text("AUTHORIZATION_REQUESTED_NOT_GRANTED", encoding="utf-8")
    with pytest.raises(harness.PreflightGateError, match="grant"):
        harness.execute_preflight(tmp_path, tmp_path / "a.zip", tmp_path / "out", packet)


def test_arbitrary_existing_markdown_is_not_the_reviewed_packet(tmp_path):
    packet = tmp_path / "unreviewed.md"
    packet.write_text("AUTHORIZATION_REQUESTED_NOT_GRANTED", encoding="utf-8")
    with pytest.raises(ValueError, match="arbitrary packet"):
        contract().load_packet(packet, ROOT)


@pytest.mark.parametrize(
    "field,value",
    [
        ("status", "NOT_GRANTED"),
        ("packet_sha256", "0" * 64),
        ("harness_sha256", "0" * 64),
        ("commit", "0" * 40),
        ("corpus_id", "other"),
        ("output_dir", "elsewhere"),
        ("expires_at", "2000-01-01T00:00:00+00:00"),
        ("external_provider_calls_allowed", 1),
        ("N", True),
        ("protected_hashes", {"fixture.py": "0" * 64}),
    ],
)
def test_grant_mismatch_refused(field, value):
    c = contract()
    now = datetime.now(timezone.utc)
    expected = {
        "commit": "1" * 40,
        "packet_sha256": "2" * 64,
        "harness_sha256": "3" * 64,
        "runtime_archive_sha256": "4" * 64,
        "setting_id": "cd_airtravel",
        "corpus_id": "text2uml_airtravel_253b26dc",
        "N": 4,
        "output_dir": "external_data/fixture",
        "command_sha256": "5" * 64,
        "protected_hashes": {"fixture.py": "6" * 64},
    }
    grant = {
        **expected,
        "schema_version": "airtravel-fake-grant-v1",
        "status": "GRANTED",
        "granted_by": "Ali Hamed",
        "granted_at": now.isoformat(),
        "expires_at": (now + timedelta(hours=1)).isoformat(),
        "expiry_condition": "ANY_BOUND_HASH_COMMIT_COMMAND_OR_PATH_CHANGE",
        "provider_execution_forbidden": True,
        "external_provider_calls_allowed": 0,
    }
    # An in-memory unit object only: never written as an actual grant receipt.
    c.validate_grant(grant, expected, now=now)
    grant[field] = value
    with pytest.raises(ValueError):
        c.validate_grant(grant, expected, now=now)


def test_changed_protected_hash_and_test_example_rejected():
    c = contract()
    example = json.loads(
        (ROOT / "schemas/airtravel-fixtures/airtravel-fake-grant.test-only.json").read_text()
    )
    assert example["status"] == "TEST_FIXTURE_ONLY"
    with pytest.raises(ValueError):
        c.validate_grant(example, {"protected_hashes": {"x": "0" * 64}})


@pytest.mark.parametrize("baseline,instrumented", [(15, 16), (327, 16), (16, 15), (16, 327)])
def test_bounds_are_per_run(baseline, instrumented):
    with pytest.raises(ValueError):
        contract().check_counts(baseline, instrumented)


def test_combined_652_is_not_rejected_by_per_run_maximum():
    assert contract().check_counts(326, 326)["combined_fake_call_count"] == 652


def test_source_drift_refuses_bound(monkeypatch, tmp_path):
    import study1_call_bound as bound

    path = tmp_path / "orchestrator.py"
    path.write_text("changed")
    assert hasattr(bound, "verify_source")
    with pytest.raises(ValueError):
        bound.verify_source(path)


def test_grant_schema_accepts_test_example_without_granting():
    from jsonschema import Draft202012Validator, FormatChecker

    example = json.loads(
        (ROOT / "schemas/airtravel-fixtures/airtravel-fake-grant.test-only.json").read_text()
    )
    schema = json.loads((ROOT / "schemas/airtravel-fake-grant-v1.schema.json").read_text())
    Draft202012Validator(schema, format_checker=FormatChecker()).validate(example)
    with pytest.raises(ValueError):
        contract().validate_grant(example, {})
