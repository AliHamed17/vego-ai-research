"""Fail-closed tests for the Study 2 prospective ON/OFF harness.

Everything here runs offline with the in-process SDK stub.  Tests that need
the private corpus are skipped when it is absent (CI), and the end-to-end
preflight is then covered by the committed preflight aggregate instead.
"""

from __future__ import annotations

import asyncio
import json
import os
import socket
import sys
from pathlib import Path

import jsonschema
import pytest

from vego_study2.prospective import constants as c
from vego_study2.prospective.aggregate import (
    RedactionError,
    assert_redacted,
    build_public_aggregate,
)
from vego_study2.prospective.budget import (
    BudgetStop,
    SharedBudgetGuard,
    design_menu,
    per_request_reserve_usd,
    total_request_cap,
)
from vego_study2.prospective.contract import ContractError, validate_condition_output
from vego_study2.prospective.fake_provider import FakeSDK
from vego_study2.prospective.inventory import select_cases
from vego_study2.prospective.manifest import (
    CASE_SELECTION_PATH,
    MANIFEST_PATH,
    ROOT,
    ManifestError,
    assert_constants_match,
    load_manifest,
    load_schema,
    verify_self_binding,
)
from vego_study2.prospective.off_runner import OffIsolationError, assert_off_isolation, run_off
from vego_study2.prospective.provider import (
    CASE,
    CONDITION,
    LABEL,
    CallLedger,
    ProviderPolicyError,
    build_client,
    contains_secret,
    restrict_egress,
)

PRIVATE_ROOT = Path(os.environ.get("VEGO_PRIVATE_EVIDENCE_ROOT", "") or "/nonexistent-private-root")
FIXTURE_CASES = [
    {"case_id": cid, "case_model": f"ENGINEERING_FIXTURE_ONLY candidate model {cid}"} for cid in ("01", "02", "03", "05")
]
FIXTURE_DOMAIN = "ENGINEERING_FIXTURE_ONLY domain description"


def _guard(**overrides) -> SharedBudgetGuard:
    params = {
        "guard_ceiling_usd": c.GUARD_CEILING_USD,
        "total_request_cap": total_request_cap(),
        "condition_request_caps": {c.CONDITION_ON: 76, c.CONDITION_OFF: 12},
    }
    params.update(overrides)
    return SharedBudgetGuard(**params)


def _lifecycle():
    records = []

    def record(**kwargs):
        records.append(kwargs)

    record.records = records
    return record


def _run_off(tmp_path: Path, mode: str = "valid", guard: SharedBudgetGuard | None = None, **fake_kwargs):
    """Run OFF in this process; ON modules imported by earlier tests are parked meanwhile.

    The real CLI runs OFF before any ON import, so the isolation guard holds
    there by construction; the test process is the only place both coexist.
    """
    guard = guard or _guard()
    ledger = CallLedger(tmp_path / "ledger.jsonl")
    fake = FakeSDK(mode, **fake_kwargs)
    parked = {name: sys.modules.pop(name) for name in c.OFF_FORBIDDEN_MODULES if name in sys.modules}
    try:
        report = asyncio.run(run_off(
            client_factory=lambda: build_client(guard, ledger, live=False, fake_sdk=fake),
            cases=FIXTURE_CASES, domain_description=FIXTURE_DOMAIN, output_dir=tmp_path / "off", lifecycle=_lifecycle(),
        ))
    finally:
        sys.modules.update(parked)
    return report, guard, ledger


def test_frozen_manifest_validates_binds_and_matches_constants() -> None:
    manifest = load_manifest()
    assert manifest["provider"]["model"] == "gpt-5.6-luna"
    assert manifest["provider"]["fallback_model"] is None
    assert manifest["execution_order"] == ["VEGO_AI_OFF", "VEGO_AI_ON"]
    assert manifest["request_parameters"]["temperature"] == "PROVIDER_DEFAULT_NOT_SENT"
    assert manifest["detector_v1"]["applies_to"]["VEGO_AI_OFF"] == "NOT_APPLICABLE"
    assert manifest["case_selection"]["sample_size"] >= c.MIN_PAIRED_CASES
    caps = manifest["caps"]
    assert (caps["VEGO_AI_ON"] + caps["VEGO_AI_OFF"]) * per_request_reserve_usd() <= c.GUARD_CEILING_USD


def test_manifest_tamper_is_detected() -> None:
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    manifest["caps"]["VEGO_AI_ON"] += 1
    with pytest.raises(ManifestError):
        verify_self_binding(manifest)
    rebound = dict(manifest)
    rebound.pop("manifest_sha256")
    from vego_study2.prospective.contract import canonical_sha256

    rebound["manifest_sha256"] = canonical_sha256(rebound)
    with pytest.raises(ManifestError):
        assert_constants_match(rebound)


def test_frozen_selection_reproduces_from_seed() -> None:
    selection = json.loads(CASE_SELECTION_PATH.read_text(encoding="utf-8"))
    eligible = [row["case_id"] for row in selection["eligible_cases"]]
    assert len(eligible) == selection["eligible_case_count"] == 21
    assert select_cases(eligible, selection["sample_size"], selection["selection_seed"]) == selection["selected_case_ids"]
    assert set(selection["selected_case_ids"]).isdisjoint(selection["excluded_case_ids"])
    assert len(selection["selected_case_ids"]) + len(selection["excluded_case_ids"]) == 21
    for row in selection["eligible_cases"]:
        assert len(row["sha256"]) == 64 and row["bytes"] > 0


def test_budget_menu_never_exceeds_ceiling_and_minimum_four() -> None:
    menu = design_menu(21)
    for option in menu["options"]:
        assert option["fits_guard_ceiling"]
        assert option["meets_minimum_cases"]
        assert option["reservation_usd"] <= c.GUARD_CEILING_USD < c.HARD_CEILING_USD
    assert menu["total_request_cap"] == 267
    assert round(menu["per_request_reserve_usd"], 7) == round((12_000 * 0.20 + 16_384 * 1.20) / 1e6, 7)


def test_guard_refuses_cap_and_ceiling_and_counts_every_request() -> None:
    guard = _guard(condition_request_caps={c.CONDITION_ON: 2, c.CONDITION_OFF: 1}, total_request_cap=3)
    guard.reserve(c.CONDITION_OFF)
    with pytest.raises(BudgetStop, match="CONDITION_REQUEST_CAP"):
        guard.reserve(c.CONDITION_OFF)
    guard.reserve(c.CONDITION_ON)
    guard.reserve(c.CONDITION_ON)
    with pytest.raises(BudgetStop):
        guard.reserve(c.CONDITION_ON)
    assert guard.requests == 3
    tight = _guard(guard_ceiling_usd=per_request_reserve_usd() * 1.5)
    tight.reserve(c.CONDITION_OFF)
    tight.record(12_000, 16_384)
    with pytest.raises(BudgetStop, match="COST_CEILING"):
        tight.reserve(c.CONDITION_OFF)
    assert tight.summary()["within_hard_ceiling"]


def test_off_completes_with_one_request_per_case_and_no_detector(tmp_path: Path) -> None:
    report, guard, ledger = _run_off(tmp_path)
    assert report["status"] == "COMPLETED"
    assert report["detector_v1"] == "NOT_APPLICABLE"
    assert report["agent_decomposition"] is False and report["inter_agent_qa"] is False
    assert guard.requests == len(FIXTURE_CASES) == len(ledger.entries)
    assert all(row["status"] == "COMPLETED" and row["output_valid"] for row in report["cases"])
    assert all(e["label"].startswith("direct/") and e["condition"] == c.CONDITION_OFF for e in ledger.entries)
    payload = json.loads((tmp_path / "off" / "cases" / "01.json").read_text(encoding="utf-8"))
    validate_condition_output(payload, condition=c.CONDITION_OFF, case_id="01")


def test_off_malformed_output_is_schema_invalid_not_repaired(tmp_path: Path) -> None:
    report, _, _ = _run_off(tmp_path, mode="malformed_off")
    assert report["status"] == "COMPLETED_WITH_FAILURES"
    assert all(row["status"] == "SCHEMA_INVALID" for row in report["cases"])
    assert not list((tmp_path / "off" / "cases").glob("0?.json"))


def test_off_invalid_json_uses_parse_reattempts_then_fails(tmp_path: Path) -> None:
    report, guard, _ = _run_off(tmp_path, mode="invalid_json")
    assert all(row["status"] == "TECHNICAL_FAILURE" and row["failure_code"] == "OUTPUT_PARSE_FAILURE" for row in report["cases"])
    assert guard.requests == 3 * len(FIXTURE_CASES)


def test_off_secret_in_output_is_refused(tmp_path: Path) -> None:
    report, _, _ = _run_off(tmp_path, mode="secret")
    assert all(row["failure_code"] == "SECRET_DETECTED" for row in report["cases"])
    assert not list((tmp_path / "off" / "cases").glob("*.json"))


def test_transport_failure_is_retried_once_and_counted(tmp_path: Path) -> None:
    report, guard, ledger = _run_off(tmp_path, mode="transport_flaky", flaky_failures=1)
    assert report["completed_cases"] == len(FIXTURE_CASES)
    assert guard.requests == len(FIXTURE_CASES) + 1
    statuses = [e["status"] for e in ledger.entries]
    assert statuses.count("TRANSPORT_ERROR") == 1
    retried = [e for e in ledger.entries if e["retry_of_seq"]]
    assert len(retried) == 1


def test_model_drift_fails_closed(tmp_path: Path) -> None:
    report, _, ledger = _run_off(tmp_path, mode="model_drift")
    assert all(row["failure_code"] == "MODEL_MISMATCH" for row in report["cases"])
    assert all(e["status"] == "MODEL_MISMATCH" for e in ledger.entries)


def test_missing_usage_is_charged_at_full_reserve(tmp_path: Path) -> None:
    report, guard, ledger = _run_off(tmp_path, mode="missing_usage")
    assert report["status"] == "COMPLETED"
    assert abs(guard.spent_usd - len(FIXTURE_CASES) * per_request_reserve_usd()) < 1e-9
    assert all(e["usage_status"] == "MISSING_USAGE_CHARGED_AT_RESERVE" for e in ledger.entries)


def test_off_cap_stops_remaining_cases_and_keeps_them_in_evidence(tmp_path: Path) -> None:
    report, guard, _ = _run_off(tmp_path, guard=_guard(condition_request_caps={c.CONDITION_ON: 76, c.CONDITION_OFF: 2}))
    statuses = sorted(row["status"] for row in report["cases"])
    assert statuses.count("COMPLETED") == 2 and statuses.count("STOPPED_AT_CAP") == 2
    assert guard.requests == 2


def test_off_isolation_guard_and_static_source() -> None:
    source = (ROOT / "src/vego_study2/prospective/off_runner.py").read_text(encoding="utf-8")
    for name in c.OFF_FORBIDDEN_MODULES:
        assert f"import {name}" not in source and f"from {name}" not in source
    sys.modules["human_review_queue"] = type(sys)("human_review_queue")
    try:
        with pytest.raises(OffIsolationError):
            assert_off_isolation("test")
    finally:
        del sys.modules["human_review_queue"]


def test_provider_rejects_unfrozen_parameters_and_missing_context(tmp_path: Path) -> None:
    guard, ledger = _guard(), CallLedger(None)
    client = build_client(guard, ledger, live=False, fake_sdk=FakeSDK("valid"))
    create = client._client.chat.completions.create

    async def call(**kwargs):
        return await create(**kwargs)

    messages = [{"role": "system", "content": "s"}, {"role": "user", "content": "u"}]
    with pytest.raises(ProviderPolicyError, match="outside a condition context"):
        asyncio.run(call(model=c.MODEL, max_tokens=c.MAX_OUTPUT_TOKENS, messages=messages))
    token = CONDITION.set(c.CONDITION_OFF)
    try:
        with pytest.raises(ProviderPolicyError, match="model switching"):
            asyncio.run(call(model="gpt-4o", max_tokens=c.MAX_OUTPUT_TOKENS, messages=messages))
        with pytest.raises(ProviderPolicyError, match="ceiling"):
            asyncio.run(call(model=c.MODEL, max_tokens=4096, messages=messages))
        with pytest.raises(ProviderPolicyError, match="unfrozen"):
            asyncio.run(call(model=c.MODEL, max_tokens=c.MAX_OUTPUT_TOKENS, messages=messages, temperature=0.0))
    finally:
        CONDITION.reset(token)
    assert guard.requests == 0


def test_build_client_is_idempotent_under_shared_sdk(tmp_path: Path) -> None:
    guard, ledger, fake = _guard(), CallLedger(None), FakeSDK("valid")
    build_client(guard, ledger, live=False, fake_sdk=fake)
    client = build_client(guard, ledger, live=False, fake_sdk=fake)
    tokens = (CONDITION.set(c.CONDITION_OFF), LABEL.set("direct/01"), CASE.set("01"))
    try:
        asyncio.run(client.call({"system": "s", "user": "u"}, label="direct/01"))
    finally:
        for var, token in zip((CONDITION, LABEL, CASE), tokens, strict=True):
            var.reset(token)
    assert guard.requests == 1 and len(ledger.entries) == 1


def test_live_client_requires_credential_presence_without_reading_it(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv(c.CREDENTIAL_ENV, raising=False)
    from vego_study2.prospective.provider import CredentialAbsent

    with pytest.raises(CredentialAbsent):
        build_client(_guard(), CallLedger(None), live=True)


def test_egress_restriction_blocks_other_hosts() -> None:
    counters = restrict_egress(frozenset({"api.openai.com"}))
    try:
        with pytest.raises(PermissionError):
            socket.getaddrinfo("example.com", 443)
        assert counters["blocked_hosts"] == 1
    finally:
        counters["restore"]()


def test_secret_detector_and_contract_validation() -> None:
    assert contains_secret({"x": "sk-abcdefghijklmnop"})
    assert not contains_secret({"x": "plain"})
    with pytest.raises(ContractError):
        validate_condition_output({"schema_version": c.CONDITION_OUTPUT_SCHEMA}, condition=c.CONDITION_OFF, case_id="01")


def test_redaction_rejects_paths_and_prose() -> None:
    with pytest.raises(RedactionError):
        assert_redacted({"a": "C:/Users/someone/private"})
    with pytest.raises(RedactionError):
        assert_redacted({"metrics": {"x": " ".join(["word"] * 20)}})
    assert_redacted({"claim_boundary": [" ".join(["word"] * 20)], "case_id": "01", "sha": "a" * 64})
    with pytest.raises(RedactionError):
        assert_redacted({"note": "safe"}, forbidden_fragments=["safe"])


def test_schemas_are_valid_documents() -> None:
    for name in (c.MANIFEST_SCHEMA, c.RECEIPT_SCHEMA, c.AGGREGATE_SCHEMA):
        jsonschema.Draft202012Validator.check_schema(load_schema(name))


def test_on_runner_records_episodes_and_detector_labels(tmp_path: Path) -> None:
    from vego_study2.prospective.on_runner import run_on

    guard = _guard(condition_request_caps={c.CONDITION_ON: 200, c.CONDITION_OFF: 12})
    ledger = CallLedger(tmp_path / "ledger.jsonl")
    fake = FakeSDK("two_rounds")
    report = asyncio.run(run_on(
        client_factory=lambda: build_client(guard, ledger, live=False, fake_sdk=fake),
        cases=FIXTURE_CASES, domain_description=FIXTURE_DOMAIN, output_dir=tmp_path / "on", run_id="S2P-PREFLIGHT-TEST",
        lifecycle=_lifecycle(), ledger_entries=lambda: list(ledger.entries),
    ))
    assert report["status"] == "COMPLETED", report.get("technical_exception")
    assert report["detector_v1"] == "APPLICABLE"
    assert report["completed_cases"] == len(FIXTURE_CASES)
    assert report["episode_summary"]["episodes"] == 2 * len(FIXTURE_CASES) + 2
    assert set(report["episode_summary"]["detector_v1_classifications"]) <= {"STRONG_ALERT", "WEAK_ALERT", "NO_ALERT"}
    assert report["event_stream_valid"] is True
    expected_requests = 1 + 4 + 9 * len(FIXTURE_CASES) + 5
    assert guard.requests == expected_requests == len(ledger.entries)
    assert all(row["output_valid"] for row in report["cases"])
    assert all(row["requests"] == 9 for row in report["cases"])
    assert report["setting_level_requests"] == 10
    assert {p.name for p in (tmp_path / "on").iterdir()} == {"pipeline", "cases", "qa_events.jsonl"}
    assert all(d["classification"] in {"STRONG_ALERT", "WEAK_ALERT", "NO_ALERT", "EXCLUDED"} for d in report["episodes"])
    payload = json.loads((tmp_path / "on" / "cases" / "01.json").read_text(encoding="utf-8"))
    validate_condition_output(payload, condition=c.CONDITION_ON, case_id="01")


def test_on_cap_stop_keeps_partial_evidence(tmp_path: Path) -> None:
    from vego_study2.prospective.on_runner import run_on

    guard = _guard(condition_request_caps={c.CONDITION_ON: 10, c.CONDITION_OFF: 12})
    ledger = CallLedger(None)
    report = asyncio.run(run_on(
        client_factory=lambda: build_client(guard, ledger, live=False, fake_sdk=FakeSDK("valid")),
        cases=FIXTURE_CASES, domain_description=FIXTURE_DOMAIN, output_dir=tmp_path / "on", run_id="S2P-PREFLIGHT-CAP",
        lifecycle=_lifecycle(), ledger_entries=lambda: list(ledger.entries),
    ))
    assert report["status"] == "STOPPED_AT_CAP"
    assert guard.requests == 10
    assert len(report["cases"]) == len(FIXTURE_CASES)
    assert guard.refusals and guard.refusals[0]["code"] == "CONDITION_REQUEST_CAP"


def test_public_aggregate_is_redacted_and_schema_valid(tmp_path: Path) -> None:
    off_report, guard, ledger = _run_off(tmp_path)
    receipt = {
        "study_id": c.STUDY_ID, "run_id": "S2P-PREFLIGHT-AGG", "mode": "PREFLIGHT_FAKE_PROVIDER",
        "evidence_class": c.EVIDENCE_FIXTURE, "execution_git_sha": "0" * 40, "manifest_sha256": "a" * 64,
        "case_selection_sha256": "b" * 64, "receipt_binding": {"sha256": "c" * 64}, "started_at": "t", "completed_at": "t",
        "model": {"provider": "openai", "model": c.MODEL}, "budget": guard.summary(), "gates": {}, "case_ids": ["01", "02", "03", "05"],
        "conditions": {
            c.CONDITION_OFF: off_report,
            c.CONDITION_ON: {"status": "NOT_STARTED_INSUFFICIENT_RESERVATION", "cases": [], "planned_cases": 4, "completed_cases": 0,
                             "elapsed_seconds": 0.0, "agent_decomposition": True, "inter_agent_qa": True, "detector_v1": "APPLICABLE",
                             "setting_level_requests": 0, "setting_level_cost_usd": 0.0, "setting_level_label_counts": {},
                             "episode_summary": {}, "episodes": [], "routes": {}, "event_log_sha256": None, "event_count": 0,
                             "event_stream_valid": None, "detector_v1_sha256": None, "protected_runtime_sha256": {}},
        },
        "claim_boundary": ["No claim of superiority."],
    }
    aggregate = build_public_aggregate(receipt, ledger.entries)
    assert_redacted(aggregate, forbidden_fragments=[case["case_model"][:40] for case in FIXTURE_CASES])
    jsonschema.Draft202012Validator(load_schema(c.AGGREGATE_SCHEMA)).validate(aggregate)
    assert aggregate["conditions"][c.CONDITION_OFF]["detector_v1"] == "NOT_APPLICABLE"
    assert all(row["off_detector_v1"] == "NOT_APPLICABLE" for row in aggregate["paired"])
    assert "fixture evidence" not in json.dumps(aggregate)


@pytest.mark.skipif(not (PRIVATE_ROOT / "fullframe_runtime").is_dir(), reason="private corpus absent")
def test_end_to_end_preflight_against_private_frame(tmp_path: Path) -> None:
    import subprocess

    run_id = f"S2P-PREFLIGHT-T{os.getpid()}"
    public_dir = tmp_path / "public"
    completed = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "study2_prospective_run.py"), "preflight", "--private-root",
         str(PRIVATE_ROOT), "--fake-mode", "valid", "--run-id", run_id, "--public-dir", str(public_dir)],
        cwd=ROOT, capture_output=True, text=True, check=False,
    )
    output_root = PRIVATE_ROOT / "study2-prospective" / run_id
    try:
        assert completed.returncode == 0, completed.stdout[-2000:] + completed.stderr[-2000:]
        receipt = json.loads((output_root / "run-receipt.json").read_text(encoding="utf-8"))
        jsonschema.Draft202012Validator(load_schema(c.RECEIPT_SCHEMA)).validate(receipt)
        assert receipt["evidence_class"] == c.EVIDENCE_FIXTURE
        assert receipt["conditions"][c.CONDITION_ON]["status"] == "COMPLETED"
        assert receipt["conditions"][c.CONDITION_OFF]["status"] == "COMPLETED"
        assert receipt["budget"]["requests"] == 12 + (1 + 1 + 3 * 12 + 2)
        assert all(gate["passed"] for gate in receipt["gates"].values())
        assert receipt["egress"]["allowed_hosts"] == []
        from vego_study2.prospective.aggregate import validate_public

        result = validate_public(output_root, public_dir / "public-aggregate.json")
        assert result["match"] and result["receipt_binding_valid"] and result["ledger_matches_receipt"]
    finally:
        import shutil

        shutil.rmtree(output_root, ignore_errors=True)
