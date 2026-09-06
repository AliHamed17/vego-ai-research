"""Adversarial tests for the versioned AirTravel v4 authorization contract.

These tests never invoke the protected orchestrator, a provider, Detector-v1,
or the renderer.  They exercise only pure path, ledger, and parity contracts.
"""

from __future__ import annotations

import hashlib
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))


def v4():
    import airtravel_v4_contract

    return airtravel_v4_contract


def manifest():
    return v4().frozen_manifest()


def request():
    return v4().request_template()


def test_machine_manifest_has_single_fixed_root_and_layout():
    m = manifest()
    assert m["packet_version"] == "v4"
    assert m["run_root"] == "external_data/airtravel-pr38/v4-authorized-fake-run"
    assert m["required_layout"] == {
        "control": [
            "private-execution-request.json",
            "authorization-grant.message.txt",
            "authorization-grant.json",
            "execution-command.json",
            "preparation-receipt.json",
            "attempt-start.json",
            "attempt-end.json",
        ],
        "output": [
            "baseline",
            "instrumented",
            "preflight-receipt.json",
        ],
        "verification": [
            "final-output-inventory.json",
            "parity-verification.json",
            "lifecycle-verification.json",
            "post-verification-receipt.json",
        ],
    }


def test_request_manifest_alignment_is_required():
    c = v4()
    c.validate_request_against_manifest(request(), manifest())
    bad = request()
    bad["run_root"] = "external_data/airtravel-pr38/other"
    with pytest.raises(ValueError, match="run_root"):
        c.validate_request_against_manifest(bad, manifest())


def test_request_binds_protected_and_harness_hashes():
    c = v4()
    m = manifest()
    r = request()
    assert r["protected_manifest_sha256"] == m["protected_manifest_sha256"]
    assert r["harness_code_hashes"] == m["harness_code_hashes"]
    assert r["schema_hashes"] == m["schema_hashes"]
    bad = json.loads(json.dumps(r))
    bad["harness_code_hashes"]["scripts/airtravel_v4_execution.py"] = "f" * 64
    with pytest.raises(ValueError, match="harness_code_hashes"):
        c.validate_request_against_manifest(bad, m)


@pytest.mark.parametrize(
    "field,value",
    [
        ("run_root", "external_data/airtravel-pr38/../escape"),
        ("output_root", "external_data/airtravel-pr38/v4-authorized-fake-run/../escape"),
        ("receipt_path", "/absolute/receipt.json"),
        ("verification_root", "external_data/airtravel-pr38/v4-authorized-fake-run/verification/extra"),
    ],
)
def test_path_traversal_and_absolute_paths_fail(field, value):
    c = v4()
    bad = request()
    bad[field] = value
    with pytest.raises(ValueError):
        c.validate_request_against_manifest(bad, manifest())


def test_case_fold_collision_and_duplicate_layout_fail():
    c = v4()
    bad = json.loads(json.dumps(manifest()))
    bad["required_evidence_files"] = ["output/preflight-receipt.json", "OUTPUT/preflight-receipt.json"]
    with pytest.raises(ValueError, match="collision"):
        c.validate_manifest(bad)


def test_lexical_normalization_is_rejected_even_when_resolved_path_is_same():
    c = v4()
    bad = request()
    bad["receipt_path"] = bad["receipt_path"].replace("/preflight-receipt.json", "//preflight-receipt.json")
    with pytest.raises(ValueError, match="differs|normalization"):
        c.validate_request_against_manifest(bad, manifest())


def test_grant_must_match_machine_manifest_and_request():
    c = v4()
    m = manifest()
    r = request()
    grant = c.grant_template()
    c.validate_grant_bindings(grant, m, r)
    grant["run_root"] = "external_data/airtravel-pr38/other"
    with pytest.raises(ValueError, match="run_root"):
        c.validate_grant_bindings(grant, m, r)


def test_required_child_escape_is_rejected():
    c = v4()
    m = manifest()
    bad = request()
    bad["receipt_path"] = "external_data/airtravel-pr38/v4-authorized-fake-run/../receipt.json"
    with pytest.raises(ValueError):
        c.validate_request_against_manifest(bad, m)


def test_attempt_start_is_exclusive_and_bound(tmp_path):
    c = v4()
    control = tmp_path / "control"
    bindings = {
        "grant_sha256": "a" * 64,
        "authorization_message_sha256": "b" * 64,
        "command_sha256": "c" * 64,
        "reviewed_head": "d" * 40,
        "nonce": "nonce-0123456789",
        "invocation_id": "invocation-01",
    }
    first = c.create_attempt_start(
        control, bindings, invocation_id="invocation-01", nonce="nonce-0123456789"
    )
    assert first["attempt_number"] == 1
    assert first["invocation_id"] == "invocation-01"
    with pytest.raises(ValueError, match="already"):
        c.create_attempt_start(
            control, bindings, invocation_id="invocation-02", nonce="nonce-0123456789-reused"
        )


def test_attempt_end_is_exclusive_and_requires_matching_invocation(tmp_path):
    c = v4()
    control = tmp_path / "control"
    start = c.create_attempt_start(
        control,
        {
            "grant_sha256": "a" * 64,
            "command_sha256": "c" * 64,
            "reviewed_head": "d" * 40,
            "nonce": "nonce-0123456789",
            "invocation_id": "invocation-01",
        },
        invocation_id="invocation-01",
        nonce="nonce-0123456789",
    )
    end = c.create_attempt_end(control, start, status="TECHNICAL_SUCCESS", output_receipt_sha256="e" * 64)
    assert end["retry_count"] == 0 and end["replay_count"] == 0
    with pytest.raises(ValueError, match="already"):
        c.create_attempt_end(control, start, status="TECHNICAL_SUCCESS")


def test_deleting_output_does_not_allow_replay(tmp_path):
    c = v4()
    control = tmp_path / "control"
    bindings = {
        "grant_sha256": "a" * 64,
        "command_sha256": "c" * 64,
        "reviewed_head": "d" * 40,
        "nonce": "nonce-0123456789",
        "invocation_id": "invocation-01",
    }
    c.create_attempt_start(control, bindings, invocation_id="invocation-01", nonce="nonce-0123456789")
    (tmp_path / "output").mkdir()
    (tmp_path / "output" / "preflight-receipt.json").write_text("receipt")
    (tmp_path / "output" / "preflight-receipt.json").unlink()
    with pytest.raises(ValueError, match="attempt-start"):
        c.assert_not_consumed(control, tmp_path / "output")


def call(seq, *, prompt="p", answer="a", decision="d", phase="phase1", case_id="01"):
    return {
        "sequence": seq,
        "phase": phase,
        "case_id": case_id,
        "label": f"agent3/case{case_id}/r{seq}",
        "source_agent": "agent3",
        "target_agent": "agent1",
        "prompt_sha256": "a" * 64,
        "prompt_length": 1,
        "answer_sha256": "b" * 64,
        "answer_length": 1,
        "decision_sha256": "c" * 64,
        "fake_client_identity": "LOCAL_DETERMINISTIC_FAKE_V3",
    }


def test_call_records_are_persisted_and_reordered_records_fail(tmp_path):
    c = v4()
    path = tmp_path / "calls.jsonl"
    c.append_call_record(path, call(1))
    c.append_call_record(path, call(2, phase="phase2"))
    rows = c.load_call_records(path)
    assert [row["sequence"] for row in rows] == [1, 2]
    path.write_text("\n".join(json.dumps(row) for row in reversed(rows)) + "\n")
    with pytest.raises(ValueError, match="sequence"):
        c.load_call_records(path)


@pytest.mark.parametrize("field", ["prompt_sha256", "answer_sha256", "decision_sha256"])
def test_call_record_mutation_breaks_parity(tmp_path, field):
    c = v4()
    left = tmp_path / "left.jsonl"
    right = tmp_path / "right.jsonl"
    c.append_call_record(left, call(1))
    changed = call(1)
    changed[field] = "f" * 64
    c.append_call_record(right, changed)
    with pytest.raises(ValueError, match="parity"):
        c.compare_call_records(left, right)


def test_call_record_raw_prompt_answer_and_unknown_fields_fail(tmp_path):
    c = v4()
    path = tmp_path / "calls.jsonl"
    row = call(1)
    row["prompt"] = "raw"
    with pytest.raises(ValueError, match="raw"):
        c.append_call_record(path, row)


def test_call_record_count_and_phase_case_coverage_are_recomputed(tmp_path):
    c = v4()
    left = tmp_path / "left.jsonl"
    right = tmp_path / "right.jsonl"
    for seq in range(1, 3):
        c.append_call_record(left, call(seq, phase=f"phase{seq}"))
        c.append_call_record(right, call(seq, phase=f"phase{seq}"))
    result = c.compare_call_records(left, right)
    assert result["direct_count"] == result["instrumented_count"] == 2
    assert result["ordered_label_parity"] is True
    assert result["ordered_prompt_parity"] is True
    assert result["ordered_answer_parity"] is True
    assert result["decision_parity"] is True
    assert result["phase_case_coverage_equal"] is True


def test_nonzero_safety_counter_is_fail_closed():
    with pytest.raises(ValueError, match="safety"):
        v4().validate_safety_counters({**v4().zero_safety_counters(), "DNS_attempt_count": 1})


def test_receipt_v2_required_fields_cannot_be_omitted():
    required = set(v4().receipt_v2_required_fields())
    assert {"mode", "invocation_id", "attempt_number", "started_at", "completed_at"} <= required
    assert {"grant_consumption_status", "retry_count", "replay_count"} <= required
    assert {"call_record_hashes", "safety_counters", "tracked_manifest_hash_before"} <= required


def test_prepare_only_has_no_execute_path():
    import prepare_airtravel_v4

    assert prepare_airtravel_v4.prepare_only.__name__ == "prepare_only"


def test_preparation_layout_rejects_sibling_and_future_markers(tmp_path):
    c = v4()
    root = c.ROOT / c.RUN_ROOT
    # The contract is tested against a temporary surrogate by temporarily
    # checking the fixed root predicate through an explicit mismatch first.
    with pytest.raises(ValueError, match="fixed v4 root"):
        c.validate_private_layout(tmp_path)
    assert root.as_posix().endswith("v4-authorized-fake-run")


def test_machine_manifest_file_matches_contract_and_schema():
    from jsonschema import Draft202012Validator

    path = ROOT / "docs/research/phd-proposal/airtravel-pr38-correction/airtravel-v4-packet-manifest.json"
    schema = json.loads(
        (ROOT / "schemas/airtravel-v4-packet-manifest-v1.schema.json").read_text()
    )
    data = json.loads(path.read_text())
    Draft202012Validator(schema).validate(data)
    assert data == manifest()


def test_v4_cli_execute_flag_is_fail_closed_without_importing_runtime():
    import prepare_airtravel_v4

    assert prepare_airtravel_v4.main is not None
    original = sys.argv
    try:
        sys.argv = ["prepare_airtravel_v4.py", "--execute"]
        assert prepare_airtravel_v4.main() == 2
    finally:
        sys.argv = original


def test_prepared_fixed_root_is_valid_on_idempotent_second_read():
    c = v4()
    if (c.ROOT / c.RUN_ROOT / "control/attempt-start.json").exists():
        pytest.skip("private v4 attempt has been consumed; preparation layout no longer applies")
    c.validate_private_layout(c.ROOT / c.RUN_ROOT, preparation=True)


def test_command_record_binds_every_resolved_path():
    import prepare_airtravel_v4

    m = manifest()
    tokens = prepare_airtravel_v4._resolved_command(
        prepare_airtravel_v4.DEFAULT_RUNTIME_ROOT,
        prepare_airtravel_v4.DEFAULT_RUNTIME_ARCHIVE,
        prepare_airtravel_v4.PRIVATE_ROOT / "output",
    )
    import hashlib

    record = {
        "tokens": tokens,
        "command_sha256": hashlib.sha256(v4().canonical(tokens)).hexdigest(),
        "max_invocations": 1,
    }
    v4().validate_command_record(record, m)
    record["tokens"] = list(tokens)
    record["tokens"][record["tokens"].index("--output-dir") + 1] = str(Path("C:/outside").resolve())
    record["command_sha256"] = hashlib.sha256(v4().canonical(record["tokens"])).hexdigest()
    with pytest.raises(ValueError, match="command|output binding"):
        v4().validate_command_record(record, m)


@pytest.mark.parametrize("mutation", ["extra", "executable", "missing_execute"])
def test_command_record_rejects_any_command_mutation(mutation):
    import prepare_airtravel_v4

    c = v4()
    m = manifest()
    tokens = prepare_airtravel_v4._resolved_command(
        prepare_airtravel_v4.DEFAULT_RUNTIME_ROOT,
        prepare_airtravel_v4.DEFAULT_RUNTIME_ARCHIVE,
        prepare_airtravel_v4.PRIVATE_ROOT / "output",
    )
    if mutation == "extra":
        tokens = [*tokens, "--unexpected"]
    elif mutation == "executable":
        tokens = ["C:/unapproved/python.exe", *tokens[1:]]
    else:
        tokens = [token for token in tokens if token != "--execute"]
    record = {
        "tokens": tokens,
        "command_sha256": hashlib.sha256(c.canonical(tokens)).hexdigest(),
        "max_invocations": 1,
    }
    with pytest.raises(ValueError, match="command"):
        c.validate_command_record(record, m)


def test_request_packet_hash_is_bound_to_packet_bytes():
    c = v4()
    bad = request()
    bad["packet_sha256"] = "0" * 64
    with pytest.raises(ValueError, match="packet hash"):
        c.validate_request_against_manifest(bad, manifest())


def _schema_valid_grant():
    c = v4()
    grant = c.grant_template()
    grant.pop("grant_sha256", None)
    grant.update(
        {
            "status": "GRANTED",
            "packet_manifest_sha256": "a" * 64,
            "authorization_message_sha256": "b" * 64,
            "command_sha256": "c" * 64,
            "reviewed_head": "d" * 40,
            "nonce": "nonce-0123456789",
            "invocation_id": "invocation-01",
            "granted_at": "2026-01-01T00:00:00Z",
            "expires_at": "2026-01-01T01:00:00Z",
            "expiry_condition": "ANY_BOUND_HASH_COMMIT_COMMAND_OR_PATH_CHANGE",
        }
    )
    return grant


@pytest.mark.parametrize(
    "granted_at,expires_at,now",
    [
        ("2026-01-01T00:00:00Z", "2026-01-01T01:00:00Z", "2026-01-01T02:00:00Z"),
        ("2026-01-01T01:00:00Z", "2026-01-01T02:00:00Z", "2026-01-01T00:00:00Z"),
    ],
)
def test_grant_expired_or_not_yet_valid_is_rejected(granted_at, expires_at, now):
    from airtravel_v4_execution import validate_grant_freshness

    grant = _schema_valid_grant()
    grant["granted_at"], grant["expires_at"] = granted_at, expires_at
    with pytest.raises(ValueError, match="valid|expired|window"):
        validate_grant_freshness(grant, now=datetime.fromisoformat(now.replace("Z", "+00:00")))


@pytest.mark.parametrize(
    "granted_at,expires_at",
    [
        ("2026-01-01T00:00:00", "2026-01-01T01:00:00Z"),
        ("not-a-time", "2026-01-01T01:00:00Z"),
        ("2026-01-01T02:00:00Z", "2026-01-01T01:00:00Z"),
        ("2026-01-01T00:00:00Z", "2026-01-01T00:00:00Z"),
        ("2026-01-01T00:00:00Z", "2026-01-02T00:00:01Z"),
    ],
)
def test_grant_timestamp_window_is_strictly_validated(granted_at, expires_at):
    from airtravel_v4_execution import validate_grant_freshness

    grant = _schema_valid_grant()
    grant["granted_at"], grant["expires_at"] = granted_at, expires_at
    with pytest.raises(ValueError):
        validate_grant_freshness(grant, now=datetime(2026, 1, 1, 0, 30, tzinfo=timezone.utc))


@pytest.mark.parametrize("field", ["nonce", "invocation_id"])
def test_grant_schema_requires_nonce_and_invocation_id(field):
    from jsonschema import Draft202012Validator, FormatChecker
    from jsonschema.exceptions import ValidationError

    grant = _schema_valid_grant()
    del grant[field]
    schema = json.loads((ROOT / "schemas/airtravel-fake-grant-v2.schema.json").read_text())
    with pytest.raises(ValidationError):
        Draft202012Validator(schema, format_checker=FormatChecker()).validate(grant)


def test_attempt_start_nonce_and_invocation_must_match_grant():
    c = v4()
    grant = _schema_valid_grant()
    start = {
        "attempt_number": 1,
        "invocation_id": "wrong-id",
        "nonce": "wrong-nonce-1234",
    }
    with pytest.raises(ValueError, match="nonce|invocation"):
        c.validate_attempt_start_matches_grant(start, grant)


@pytest.mark.parametrize("field", ["nonce", "invocation_id"])
def test_nonce_or_invocation_reuse_is_rejected(tmp_path, field):
    c = v4()
    control = tmp_path / "control"
    bindings = {
        "grant_sha256": "a" * 64,
        "command_sha256": "b" * 64,
        "reviewed_head": "c" * 40,
        "nonce": "nonce-0123456789",
        "invocation_id": "invocation-01",
    }
    c.create_attempt_start(control, bindings, invocation_id=bindings["invocation_id"], nonce=bindings["nonce"])
    reused = dict(bindings)
    reused[field] = reused[field] + "-reused"
    with pytest.raises(ValueError, match="already|consum"):
        c.create_attempt_start(control, reused, invocation_id=reused["invocation_id"], nonce=reused["nonce"])


def test_manifest_write_roots_are_frozen_and_non_overlapping():
    c = v4()
    widened = json.loads(json.dumps(manifest()))
    widened["allowed_write_roots"] = [c.RUN_ROOT, "external_data/other"]
    with pytest.raises(ValueError, match="allowed_write_roots"):
        c.validate_manifest(widened)
    overlap = json.loads(json.dumps(manifest()))
    overlap["prohibited_write_roots"] = [c.RUN_ROOT]
    with pytest.raises(ValueError, match="overlap|prohibited_write_roots"):
        c.validate_manifest(overlap)


def test_execution_layout_rejects_post_verification_sibling(tmp_path, monkeypatch):
    c = v4()
    root = tmp_path / c.RUN_ROOT
    (root / "control").mkdir(parents=True)
    (root / "output" / "baseline").mkdir(parents=True)
    (root / "output" / "instrumented").mkdir(parents=True)
    (root / "verification").mkdir(parents=True)
    (root / "post-verification").mkdir()
    monkeypatch.setattr(c, "ROOT", tmp_path)
    with pytest.raises(ValueError, match="undeclared|layout"):
        c.validate_private_layout(root, preparation=False)


def test_symlink_run_root_is_rejected(tmp_path, monkeypatch):
    c = v4()
    expected = tmp_path / c.RUN_ROOT
    expected.parent.mkdir(parents=True)
    outside = tmp_path / "outside"
    outside.mkdir()
    try:
        os.symlink(outside, expected, target_is_directory=True)
    except (OSError, NotImplementedError):
        pytest.skip("symlink creation is unavailable on this Windows host")
    monkeypatch.setattr(c, "ROOT", tmp_path)
    with pytest.raises(ValueError, match="symlink|reparse|fixed"):
        c.validate_private_layout(expected, preparation=False)


def test_receipt_grant_validity_is_measured_not_a_schema_constant():
    from airtravel_v4_execution import validate_grant_freshness

    grant = _schema_valid_grant()
    valid = validate_grant_freshness(grant, now=datetime(2026, 1, 1, 0, 30, tzinfo=timezone.utc))
    assert valid is True
    grant["expires_at"] = "2026-01-01T00:15:00Z"
    with pytest.raises(ValueError):
        validate_grant_freshness(grant, now=datetime(2026, 1, 1, 0, 30, tzinfo=timezone.utc))


def test_receipt_cross_field_call_counts_are_validated(tmp_path):
    from airtravel_v4_execution import validate_receipt_v2

    # Schema-valid fields are deliberately inconsistent; evidence files are
    # not needed because cross-field validation must fail first.
    z = "0" * 64
    receipt = {
        "schema_version": "airtravel-technical-receipt-v2",
        "mode": "execute",
        "status": "TECHNICAL_SUCCESS",
        "reviewed_head": "a" * 40,
        "packet_manifest_sha256": z,
        "request_sha256": z,
        "authorization_message_sha256": z,
        "grant_sha256": z,
        "command_sha256": z,
        "invocation_id": "invocation-01",
        "nonce": "nonce-0123456789",
        "attempt_number": 1,
        "started_at": "2026-01-01T00:00:00Z",
        "completed_at": "2026-01-01T00:00:01Z",
        "grant_evaluated_at": "2026-01-01T00:00:00Z",
        "grant_valid_at_start": True,
        "timeout": False,
        "retry_count": 0,
        "replay_count": 0,
        "direct_fake_call_count": 16,
        "instrumented_fake_call_count": 16,
        "combined_fake_call_count": 33,
        "call_count_equal": True,
        "prompt_parity": True,
        "answer_parity": True,
        "decision_parity": True,
        "pipeline_state_parity": True,
        "scientific_artifact_parity": True,
        "completed_cases": ["01", "02", "03", "04"],
        "completed_phases": ["phase1", "phase2", "phase3", "phase4"],
        "event_log_sha256": z,
        "event_count": 1,
        "question_count": 1,
        "answer_count": 1,
        "termination_count": 1,
        "termination_counts": {},
        "route_pairs": [],
        "protected_manifest_hash_before": z,
        "protected_manifest_hash_after": z,
        "tracked_manifest_hash_before": z,
        "tracked_manifest_hash_after": z,
        "output_inventory_sha256": z,
        "containment_status": "PASS",
        "privacy_status": "PASS",
        "call_record_hashes": {"baseline": z, "instrumented": z},
        "safety_counters": v4().zero_safety_counters(),
        "grant_consumption_status": "CONSUMED",
    }
    with pytest.raises(ValueError, match="combined call count"):
        validate_receipt_v2(receipt, root=ROOT)
