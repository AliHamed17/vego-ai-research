"""Expanded September 5 contracts; fixtures only, no exact AirTravel execution."""

import copy
import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))


def grant_fixture():
    from airtravel_preflight_contract import GRANT_SCHEMA

    schema = json.loads((ROOT / GRANT_SCHEMA).read_text())
    example = json.loads(
        (ROOT / "schemas/airtravel-fixtures/airtravel-fake-grant.test-only.json").read_text()
    )
    now = datetime.now(timezone.utc)
    grant = {
        **example,
        "status": "GRANTED",
        "grant_type": "OFFLINE_FAKE_PREFLIGHT_ONLY",
        "authorization_message_sha256": "7" * 64,
        "implementation_commit": "2" * 40,
        "call_bound_sha256": "3" * 64,
        "protected_manifest_sha256": "4" * 64,
        "runtime_file_hashes": {f"fixture-{n}": str(n) * 64 for n in range(5)},
        "timeout_seconds": 1800,
        "maximum_calls_per_run": 326,
        "network_forbidden": True,
        "paid_execution_authorized": False,
        "granted_at": now.isoformat(),
        "expires_at": (now + timedelta(minutes=30)).isoformat(),
    }
    assert schema["type"] == "object"
    expected = {k: v for k, v in grant.items() if k not in {"granted_at", "expires_at"}}
    return grant, expected, now


NEW_FIELDS = [
    "grant_type",
    "authorization_message_sha256",
    "implementation_commit",
    "call_bound_sha256",
    "protected_manifest_sha256",
    "runtime_file_hashes",
    "timeout_seconds",
    "maximum_calls_per_run",
    "network_forbidden",
    "paid_execution_authorized",
]


@pytest.mark.parametrize("field", NEW_FIELDS)
def test_every_expanded_binding_is_required_and_checked(field):
    from airtravel_preflight_contract import validate_grant

    grant, expected, now = grant_fixture()
    validate_grant(grant, expected, now=now)
    missing = dict(grant)
    del missing[field]
    with pytest.raises(ValueError):
        validate_grant(missing, expected, now=now)
    changed = {**grant, field: "wrong"}
    with pytest.raises(ValueError):
        validate_grant(changed, expected, now=now)


def test_different_in_bound_pass_counts_rejected():
    from airtravel_preflight_contract import check_counts

    with pytest.raises(ValueError, match="differ"):
        check_counts(16, 17)


def test_new_counters_do_not_confuse_episodes_and_pairs():
    from airtravel_local_observer import route_metrics
    from airtravel_preflight_contract import counters

    before = counters()
    assert before["protected_orchestrator_fake_episode_count"] == "NOT_EXECUTED"
    assert before["provider_backed_production_route_pair_count"] == 0
    assert before["detector_v1_experimental_run_count"] == 0
    rows = [
        {
            "event_type": "QUESTION_EMITTED",
            "episode_id": e,
            "source_agent": "agent3",
            "target_agent": "agent1",
        }
        for e in ("a", "b", "c")
    ]
    result = route_metrics(rows)
    assert result["protected_orchestrator_fake_episode_count"] == 3
    assert result["protected_orchestrator_fake_route_pair_count"] == 1
    assert result["protected_orchestrator_fake_route_pairs"] == [
        {"source_agent": "agent3", "target_agent": "agent1"}
    ]


def parity_fixture():
    return {
        "calls": [
            {
                "label": "agent1/build_language_template",
                "prompt_sha256": "a" * 64,
                "answer_sha256": "b" * 64,
                "inventory_row": "P1_TEMPLATE",
                "phase": "phase1",
                "case_id": None,
                "decision_sha256": "c" * 64,
            }
        ],
        "state": {"completed_phases": ["phase1"], "decision": "keep"},
        "outputs": {"pipeline_state.json": "d" * 64},
        "termination_result": "RETURNED_WITH_ALL_PHASES_COMPLETED",
        "events": [],
    }


@pytest.mark.parametrize(
    "mutation", ["prompt", "answer", "decision", "state", "artifact", "termination"]
)
def test_parity_mutation_is_rejected(mutation):
    from airtravel_preflight_execution import assert_pair_parity

    a = parity_fixture()
    b = copy.deepcopy(a)
    if mutation in {"prompt", "answer", "decision"}:
        b["calls"][0][mutation + "_sha256"] = "f" * 64
    elif mutation == "state":
        b["state"]["decision"] = "change"
    elif mutation == "artifact":
        b["outputs"]["pipeline_state.json"] = "f" * 64
    else:
        b["termination_result"] = "FAILED"
    with pytest.raises(ValueError, match="parity"):
        assert_pair_parity(a, b)


def test_observer_only_difference_allowed():
    from airtravel_preflight_execution import assert_pair_parity

    a = parity_fixture()
    b = copy.deepcopy(a)
    b["events"] = [{"fixture": "observer-only"}]
    assert all(assert_pair_parity(a, b).values())


def test_unknown_call_inventory_refused():
    from study1_call_bound import validate_call_inventory

    with pytest.raises(ValueError):
        validate_call_inventory([{"label": "unexpected/provider"}])


def test_old_partial_zero_qa_proof_is_invalid():
    import render_airtravel_results as r

    assert r.zero_qa_status([], {"status": "TECHNICAL_SUCCESS"}) == "INVALID_OR_INCOMPLETE_ZERO_QA"


@pytest.mark.parametrize(
    "field,value",
    [
        ("granted_by", "Someone else"),
        ("grant_type", "PAID_RUN"),
        ("authorization_message_sha256", "8" * 64),
        ("granted_at", "2099-01-01T00:00:00Z"),
        ("expires_at", "2000-01-01T00:00:00Z"),
        ("command_sha256", "9" * 64),
        ("commit", "f" * 40),
    ],
)
def test_owner_message_time_and_command_mutations(field, value):
    from airtravel_preflight_contract import validate_grant

    grant, expected, now = grant_fixture()
    validate_grant(grant, expected, now=now)
    grant[field] = value
    with pytest.raises(ValueError):
        validate_grant(grant, expected, now=now)


@pytest.mark.parametrize(
    "field,value",
    [
        ("setting_id", "wrong"),
        ("corpus_id", "wrong"),
        ("N", 3),
        ("commit", "2" * 40),
        ("model", "external-model"),
        ("provider", "remote"),
        ("runtime_archive_sha256", "0" * 64),
        ("runtime_file_hashes", {}),
        ("event_log_sha256", "0" * 64),
        ("direct_fake_call_count", 15),
        ("instrumented_fake_call_count", 327),
        ("baseline_fake_call_count", 17),
        ("timeout_seconds", 9999),
        ("timeout", True),
        ("decision_parity", False),
        ("filesystem_containment", "NOT_CHECKED"),
        ("lifecycle_status", "NOT_CHECKED"),
        ("external_provider_call_count", 1),
        ("detector_v1_experimental_run_count", 1),
    ],
)
def test_complete_renderer_receipt_single_mutations(tmp_path, field, value):
    from airtravel_preflight_contract import canonical, digest
    from render_airtravel_results import verify_run_receipt
    from test_render_airtravel_results import _technical_fixture

    events = tmp_path / "events.jsonl"
    events.write_text("")
    receipt = _technical_fixture(events)
    path = tmp_path / "receipt.json"
    path.write_bytes(canonical(receipt))
    verify_run_receipt(events, path, digest(path), "1" * 40, "LOCAL_DETERMINISTIC_FAKE_V3")
    receipt[field] = value
    path.write_bytes(canonical(receipt))
    with pytest.raises(ValueError):
        verify_run_receipt(events, path, digest(path), "1" * 40, "LOCAL_DETERMINISTIC_FAKE_V3")


def test_route_metadata_cannot_inject_authoritative_prose(tmp_path):
    from airtravel_preflight_contract import canonical, digest
    from render_airtravel_results import verify_run_receipt
    from test_render_airtravel_results import _fixture_events, _technical_fixture

    events = tmp_path / "events.jsonl"
    _fixture_events(events)
    # Recompute IDs to prove this is not merely rejected for a stale content hash.
    from qa_communication import QACommunicationRecorder

    clean = tmp_path / "injected.jsonl"
    recorder = QACommunicationRecorder(clean, run_id="fixture-injection")
    recorder.observe_exchange(
        questions=[{"question_id": "q", "question": "fixture"}],
        answers=[
            {"question_id": "q", "answer": "fixture", "confidence": "High", "evidence": "fixture"}
        ],
        source_agent="This system proves human benefit",
        source_stage="case_inspection",
        source_skill="fixture",
        target_agent="agent1",
        scope="language",
        episode_id="fixture-e",
        round_index=1,
    )
    recorder.emit_termination(
        episode_id="fixture-e", termination_reason="CONVERGED", converged=True
    )
    receipt = _technical_fixture(clean)
    path = tmp_path / "receipt.json"
    path.write_bytes(canonical(receipt))
    with pytest.raises(ValueError, match="agent"):
        verify_run_receipt(clean, path, digest(path), "1" * 40, "LOCAL_DETERMINISTIC_FAKE_V3")
