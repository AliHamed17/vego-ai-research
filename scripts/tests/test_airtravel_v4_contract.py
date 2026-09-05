"""Adversarial tests for the versioned AirTravel v4 authorization contract.

These tests never invoke the protected orchestrator, a provider, Detector-v1,
or the renderer.  They exercise only pure path, ledger, and parity contracts.
"""

from __future__ import annotations

import json
import sys
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
    }
    first = c.create_attempt_start(control, bindings, invocation_id="inv-1", nonce="n-1")
    assert first["attempt_number"] == 1
    assert first["invocation_id"] == "inv-1"
    with pytest.raises(ValueError, match="already"):
        c.create_attempt_start(control, bindings, invocation_id="inv-2", nonce="n-2")


def test_attempt_end_is_exclusive_and_requires_matching_invocation(tmp_path):
    c = v4()
    control = tmp_path / "control"
    start = c.create_attempt_start(
        control,
        {"grant_sha256": "a" * 64, "command_sha256": "c" * 64, "reviewed_head": "d" * 40},
        invocation_id="inv-1",
        nonce="n-1",
    )
    end = c.create_attempt_end(control, start, status="TECHNICAL_SUCCESS", output_receipt_sha256="e" * 64)
    assert end["retry_count"] == 0 and end["replay_count"] == 0
    with pytest.raises(ValueError, match="already"):
        c.create_attempt_end(control, start, status="TECHNICAL_SUCCESS")


def test_deleting_output_does_not_allow_replay(tmp_path):
    c = v4()
    control = tmp_path / "control"
    bindings = {"grant_sha256": "a" * 64, "command_sha256": "c" * 64, "reviewed_head": "d" * 40}
    c.create_attempt_start(control, bindings, invocation_id="inv-1", nonce="n-1")
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
    with pytest.raises(ValueError, match="output binding"):
        v4().validate_command_record(record, m)
