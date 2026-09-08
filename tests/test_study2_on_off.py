from __future__ import annotations

import asyncio
import importlib.util
import json
import os
import socket
import subprocess
import sys
from pathlib import Path

import pytest

from vego_study2.config import load_config
from vego_study2.fixtures import DeterministicFixtureClient, FixtureResponse, fixture_cases
from vego_study2.paths import UnsafeOutputPathError, ensure_safe_output_root
from vego_study2.runner import Study2RunError, Study2Runner, validate_persisted_receipt

CONFIG_PATH = Path(__file__).resolve().parents[1] / "docs/research/phd-proposal/study2-frozen-config.json"


def _runner(tmp_path: Path, client: DeterministicFixtureClient | None = None) -> Study2Runner:
    config = load_config(CONFIG_PATH)
    return Study2Runner(
        config=config,
        cases=fixture_cases(config),
        client=client or DeterministicFixtureClient(),
        output_root=tmp_path / "study2-output",
        code_sha="fixture-code-sha",
    )


def test_config_freezes_system_comparison_and_four_cases() -> None:
    config = load_config(CONFIG_PATH)
    assert config["intervention"]["type"] == "SYSTEM_COMPARISON"
    assert config["case_ids"] == ["01", "02", "03", "04"]
    assert config["conditions"]["VEGO_AI_ON"]["inter_agent_qa"] is True
    assert config["conditions"]["VEGO_AI_OFF"]["inter_agent_qa"] is False
    assert config["detector_v1"]["VEGO_AI_OFF"] == "NOT_APPLICABLE"
    assert config["model"]["model_id"] == "TO_BE_FROZEN_BEFORE_FIRST_CALL"


def test_off_rejects_malformed_output_fail_closed(tmp_path: Path) -> None:
    client = DeterministicFixtureClient(mode="malformed")
    report = asyncio.run(_runner(tmp_path, client).run_off())
    assert report["status"] == "TECHNICAL_FAILURE"
    assert report["successful_cases"] == 0
    assert all(row["status"] == "TECHNICAL_FAILURE" for row in report["cases"])
    assert all(row["validation"]["valid"] is False for row in report["cases"])


def test_invalid_json_payload_is_a_technical_failure(tmp_path: Path) -> None:
    report = asyncio.run(_runner(tmp_path, DeterministicFixtureClient(mode="invalid_json")).run_off())
    assert report["status"] == "TECHNICAL_FAILURE"
    assert report["failure_code"] == "OUTPUT_NOT_OBJECT"


def test_invalid_nested_output_types_fail_closed(tmp_path: Path) -> None:
    class WrongTypeClient(DeterministicFixtureClient):
        async def complete(self, request: object) -> object:
            response = await super().complete(request)
            response.payload["coverage_summary"] = None
            return response

    report = asyncio.run(_runner(tmp_path, WrongTypeClient()).run_off())
    assert report["status"] == "TECHNICAL_FAILURE"
    assert report["failure_code"] == "COVERAGE_SUMMARY_INVALID"


def test_failed_on_condition_does_not_emit_scientific_lifecycle_events(tmp_path: Path) -> None:
    report = asyncio.run(_runner(tmp_path, DeterministicFixtureClient(mode="malformed")).run_on())
    assert report["status"] == "TECHNICAL_FAILURE"
    assert report["events"] == []
    assert report["questions"] == 0
    assert report["answers"] == 0


def test_unknown_fixture_mode_fails_closed(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="unknown fixture mode"):
        asyncio.run(_runner(tmp_path).run_on(fixture_mode="unknown"))


def test_off_has_no_qa_and_detector_is_not_applicable(tmp_path: Path) -> None:
    runner = _runner(tmp_path)
    report = asyncio.run(runner.run_off())
    assert report["status"] == "PASS"
    assert report["episodes"] == 0
    assert report["detector_v1"]["denominator"] == "NOT_APPLICABLE"
    assert report["questions"] == 0
    assert report["answers"] == 0
    assert len(report["cases"]) == 4


def test_on_and_off_enforce_same_control_policy_and_shared_objective(tmp_path: Path) -> None:
    runner = _runner(tmp_path)
    result = asyncio.run(runner.run_both())
    on = result["conditions"]["VEGO_AI_ON"]
    off = result["conditions"]["VEGO_AI_OFF"]
    assert on["status"] == "PASS"
    assert off["status"] == "PASS"
    assert on["control_policy"] == off["control_policy"]
    assert set(on["prompt_sha_by_case"]) == {"01", "02", "03", "04"}
    assert set(off["prompt_sha_by_case"]) == {"01", "02", "03", "04"}
    assert on["objective_schema"] == off["objective_schema"]
    assert on["agent_decomposition"] is True
    assert off["agent_decomposition"] is False
    assert on["inter_agent_qa"] is True
    assert off["inter_agent_qa"] is False
    assert on["calls"] == 16
    assert off["calls"] == 4
    assert len(on["prompt_sha_by_call"]) == 16
    assert len(off["prompt_sha_by_call"]) == 4


def test_on_emits_qa_episodes_but_no_qa_fixture_is_allowed(tmp_path: Path) -> None:
    on = asyncio.run(_runner(tmp_path).run_on(fixture_mode="two_rounds"))
    assert on["questions"] == 8
    assert on["answers"] == 8
    assert on["episodes"] == 4
    no_qa = asyncio.run(_runner(tmp_path / "no-qa").run_on(fixture_mode="no_questions"))
    assert no_qa["questions"] == 0
    assert no_qa["answers"] == 0
    assert no_qa["episodes"] == 0
    answer = on["events"][1]
    assert answer["event_type"] == "ANSWER_RECEIVED"
    assert answer["question_id"] == on["events"][0]["question_id"]


def test_retry_is_counted_and_timeout_fails_closed(tmp_path: Path) -> None:
    retry_client = DeterministicFixtureClient(fail_first_attempts=1)
    retry_report = asyncio.run(_runner(tmp_path / "retry", retry_client).run_off())
    assert retry_report["status"] == "PASS"
    assert retry_report["attempts"] == 8
    assert retry_report["retries_used"] == 4

    timeout_client = DeterministicFixtureClient(mode="timeout", delay_seconds=0.05)
    timeout_report = asyncio.run(_runner(tmp_path / "timeout", timeout_client).run_off())
    assert timeout_report["status"] == "TECHNICAL_FAILURE"
    assert all(row["validation"]["reason_code"] == "TIMEOUT" for row in timeout_report["cases"])


def test_retry_exhaustion_is_not_a_success(tmp_path: Path) -> None:
    client = DeterministicFixtureClient(fail_first_attempts=99)
    report = asyncio.run(_runner(tmp_path, client).run_off())
    assert report["status"] == "TECHNICAL_FAILURE"
    assert report["attempts"] == 8
    assert all(row["validation"]["reason_code"] == "RUNTIMEERROR" for row in report["cases"])


def test_cost_and_call_ceiling_are_enforced(tmp_path: Path) -> None:
    expensive = DeterministicFixtureClient(cost_usd=100.0)
    report = asyncio.run(_runner(tmp_path, expensive).run_off())
    assert report["status"] == "TECHNICAL_FAILURE"
    assert report["failure_code"] == "COST_CEILING_EXCEEDED"


def test_secret_leak_is_rejected_without_persisting_raw_payload(tmp_path: Path) -> None:
    client = DeterministicFixtureClient(mode="secret")
    report = asyncio.run(_runner(tmp_path, client).run_off())
    assert report["status"] == "TECHNICAL_FAILURE"
    assert report["privacy_counters"]["secrets_detected"] == 4
    assert "sk-live" not in json.dumps(report)
    assert "sk-live" not in "\n".join(p.read_text(encoding="utf-8") for p in tmp_path.rglob("*.json"))


def test_output_escape_and_symlink_are_rejected(tmp_path: Path) -> None:
    allowed = tmp_path / "allowed"
    allowed.mkdir()
    with pytest.raises(UnsafeOutputPathError):
        ensure_safe_output_root(tmp_path / "sibling", allowed)
    with pytest.raises(UnsafeOutputPathError):
        ensure_safe_output_root(allowed / ".." / "sibling", allowed)
    link = tmp_path / "link"
    try:
        link.symlink_to(allowed, target_is_directory=True)
    except (OSError, NotImplementedError):
        pytest.skip("symlink creation is unavailable")
    with pytest.raises(UnsafeOutputPathError):
        ensure_safe_output_root(link / "output", allowed)


def test_receipt_self_binds_hashes_and_excludes_fixture_from_science(tmp_path: Path) -> None:
    result = asyncio.run(_runner(tmp_path).run_both())
    receipt = result["receipt"]
    assert receipt["evidence_class"] == "ENGINEERING_FIXTURE_ONLY"
    assert receipt["scientific_result_status"] == "NOT_EXECUTED"
    assert receipt["study1_pooled"] is False
    for condition in ("VEGO_AI_ON", "VEGO_AI_OFF"):
        bound = receipt["conditions"][condition]
        assert bound["result_file_sha256"]
        assert bound["pipeline_manifest_sha256"]
        assert bound["event_log_sha256"]
        assert bound["lifecycle_summary"]
    assert (tmp_path / "study2-output" / "run-receipt.json").is_file()


def test_two_runs_have_identical_normalized_hashes(tmp_path: Path) -> None:
    first = asyncio.run(_runner(tmp_path / "a").run_both())
    second = asyncio.run(_runner(tmp_path / "b").run_both())
    assert first["normalized_sha256"] == second["normalized_sha256"]


def test_runner_rejects_output_root_outside_approved_root(tmp_path: Path) -> None:
    config = load_config(CONFIG_PATH)
    runner = Study2Runner(
        config=config,
        cases=fixture_cases(config),
        client=DeterministicFixtureClient(),
        output_root=tmp_path / "outside",
        approved_root=tmp_path / "approved",
        code_sha="fixture-code-sha",
    )
    with pytest.raises(UnsafeOutputPathError):
        asyncio.run(runner.run_off())


def test_run_timeout_is_enforced_before_fixture_completion(tmp_path: Path) -> None:
    config = load_config(CONFIG_PATH)
    config["execution"]["run_timeout_seconds"] = 0.001
    runner = Study2Runner(
        config=config,
        cases=fixture_cases(config),
        client=DeterministicFixtureClient(delay_seconds=0.05),
        output_root=tmp_path / "study2-output",
        code_sha="fixture-code-sha",
    )
    with pytest.raises(Study2RunError, match="RUN_TIMEOUT"):
        asyncio.run(runner.run_off())


def test_max_round_fixture_has_explicit_terminal_state(tmp_path: Path) -> None:
    report = asyncio.run(_runner(tmp_path).run_on(fixture_mode="max_rounds"))
    assert report["status"] == "PASS"
    assert report["questions"] == 40
    assert report["lifecycle"]["termination_reasons"] == {"TERMINATED_MAX_ROUNDS": 4}


def test_cli_is_fixture_only_and_writes_private_root(tmp_path: Path) -> None:
    script = Path(__file__).resolve().parents[1] / "scripts/study2_on_off_experiment.py"
    env = {**os.environ, "PYTHONPATH": str(Path(__file__).resolve().parents[1] / "src")}
    output = tmp_path / "private-output"
    completed = subprocess.run(
        [sys.executable, str(script), "--output-dir", str(output), "--allowed-root", str(tmp_path), "--fixture-mode", "no_questions"],
        capture_output=True,
        text=True,
        env=env,
        check=False,
    )
    assert completed.returncode == 0, completed.stderr
    summary = json.loads(completed.stdout)
    assert summary["evidence_class"] == "ENGINEERING_FIXTURE_ONLY"
    assert summary["scientific_result_status"] == "NOT_EXECUTED"
    assert summary["provider_calls"] == 0


def test_cli_rejects_unscoped_legacy_runtime_path(tmp_path: Path) -> None:
    script = Path(__file__).resolve().parents[1] / "scripts/study2_on_off_experiment.py"
    env = {**os.environ, "PYTHONPATH": str(Path(__file__).resolve().parents[1] / "src")}
    completed = subprocess.run(
        [sys.executable, str(script), "--output-dir", str(tmp_path / "output")],
        capture_output=True,
        text=True,
        env=env,
        check=False,
    )
    assert completed.returncode != 0
    assert "--allowed-root is required" in completed.stderr


def test_legacy_protected_helpers_fail_closed() -> None:
    script = Path(__file__).resolve().parents[1] / "scripts/study2_on_off_experiment.py"
    spec = importlib.util.spec_from_file_location("study2_cli", script)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    with pytest.raises(RuntimeError, match="controlled fixture runner"):
        asyncio.run(module.run_on({}, Path("output"), "two_rounds", "legacy"))
    with pytest.raises(RuntimeError, match="controlled fixture runner"):
        asyncio.run(module.run_off({}, "two_rounds"))


def test_call_site_binds_model_temperature_token_and_timeout_policy(tmp_path: Path) -> None:
    class RecordingClient(DeterministicFixtureClient):
        async def complete(self, request: object) -> FixtureResponse:
            response = await super().complete(request)
            self.calls[-1]["timeout_seconds"] = request.timeout_seconds
            return response

    client = RecordingClient()
    runner = _runner(tmp_path, client)
    result = asyncio.run(runner.run_both())
    assert result["conditions"]["VEGO_AI_ON"]["status"] == "PASS"
    assert result["conditions"]["VEGO_AI_OFF"]["status"] == "PASS"
    expected = {
        "model_id": runner.config["model"]["model_id"],
        "temperature": runner.config["model"]["temperature"],
        "max_output_tokens": runner.config["model"]["max_output_tokens"],
        "timeout_seconds": runner.config["execution"]["timeout_seconds"],
    }
    assert client.calls
    assert all({key: call[key] for key in expected} == expected for call in client.calls)


def test_output_token_ceiling_is_enforced_at_call_site(tmp_path: Path) -> None:
    class OverTokenClient(DeterministicFixtureClient):
        async def complete(self, request: object) -> FixtureResponse:
            response = await super().complete(request)
            return FixtureResponse(
                response.payload,
                input_tokens=response.input_tokens,
                output_tokens=request.max_output_tokens + 1,
                cost_usd=response.cost_usd,
            )

    report = asyncio.run(_runner(tmp_path, OverTokenClient()).run_off())
    assert report["status"] == "TECHNICAL_FAILURE"
    assert report["failure_code"] == "OUTPUT_TOKEN_CEILING_EXCEEDED"
    assert report["output_tokens"] == 0


def test_zero_budget_blocks_before_client_call(tmp_path: Path) -> None:
    config = load_config(CONFIG_PATH)
    config["execution"]["cost_ceiling_usd"] = 0.0

    class CountingClient(DeterministicFixtureClient):
        pass

    client = CountingClient()
    runner = Study2Runner(
        config=config,
        cases=fixture_cases(config),
        client=client,
        output_root=tmp_path / "study2-output",
        code_sha="fixture-code-sha",
    )
    report = asyncio.run(runner.run_off())
    assert report["status"] == "TECHNICAL_FAILURE"
    assert report["failure_code"] == "COST_CEILING_EXCEEDED"
    assert report["attempts"] == 0
    assert client.calls == []


def test_call_ceiling_is_hard_limit_across_concurrent_cases(tmp_path: Path) -> None:
    config = load_config(CONFIG_PATH)
    config["execution"]["call_ceiling"] = 2
    config["execution"]["retries"] = 0
    client = DeterministicFixtureClient()
    runner = Study2Runner(
        config=config,
        cases=fixture_cases(config),
        client=client,
        output_root=tmp_path / "study2-output",
        code_sha="fixture-code-sha",
    )
    report = asyncio.run(runner.run_off())
    assert report["status"] == "TECHNICAL_FAILURE"
    assert report["attempts"] == 2
    assert len(client.calls) == 2
    assert report["failure_code"] == "CALL_CEILING_EXCEEDED"


def test_configuration_is_frozen_before_conditions_start(tmp_path: Path) -> None:
    config = load_config(CONFIG_PATH)
    client = DeterministicFixtureClient()
    runner = Study2Runner(
        config=config,
        cases=fixture_cases(config),
        client=client,
        output_root=tmp_path / "study2-output",
        code_sha="fixture-code-sha",
    )
    config["model"]["model_id"] = "mutated-after-construction"
    report = asyncio.run(runner.run_off())
    assert report["status"] == "PASS"
    assert all(call["model_id"] == "TO_BE_FROZEN_BEFORE_FIRST_CALL" for call in client.calls)


def test_runner_rejects_unmarked_non_fixture_client(tmp_path: Path) -> None:
    class UnmarkedClient:
        async def complete(self, request: object) -> FixtureResponse:
            raise AssertionError("a non-fixture client must never be called")

    config = load_config(CONFIG_PATH)
    with pytest.raises(Study2RunError, match="offline-only client"):
        Study2Runner(
            config=config,
            cases=fixture_cases(config),
            client=UnmarkedClient(),
            output_root=tmp_path / "study2-output",
            code_sha="fixture-code-sha",
        )


def test_egress_attempt_is_blocked_and_recorded(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    def forbidden_connect(*args: object, **kwargs: object) -> object:
        raise AssertionError("the test client attempted an unguarded connection")

    monkeypatch.setattr(socket, "create_connection", forbidden_connect)

    class EgressAttemptClient(DeterministicFixtureClient):
        async def complete(self, request: object) -> FixtureResponse:
            socket.create_connection(("api.openai.com", 443), timeout=0.001)
            return await super().complete(request)

    report = asyncio.run(_runner(tmp_path, EgressAttemptClient()).run_off())
    assert report["status"] == "TECHNICAL_FAILURE"
    assert report["privacy_counters"]["blocked_egress_attempts"] == 4
    assert report["provider_calls"] == 0
    assert report["external_calls"] == 0


def test_connect_ex_egress_attempt_is_blocked(tmp_path: Path) -> None:
    class EgressAttemptClient(DeterministicFixtureClient):
        async def complete(self, request: object) -> FixtureResponse:
            sock = socket.socket()
            try:
                sock.connect_ex(("api.openai.com", 443))
            finally:
                sock.close()
            return await super().complete(request)

    report = asyncio.run(_runner(tmp_path, EgressAttemptClient()).run_off())
    assert report["status"] == "TECHNICAL_FAILURE"
    assert report["privacy_counters"]["blocked_egress_attempts"] == 4


def test_non_finite_usage_fails_closed(tmp_path: Path) -> None:
    class NaNClient(DeterministicFixtureClient):
        async def complete(self, request: object) -> FixtureResponse:
            response = await super().complete(request)
            return FixtureResponse(
                response.payload,
                input_tokens=response.input_tokens,
                output_tokens=response.output_tokens,
                cost_usd=float("nan"),
            )

    report = asyncio.run(_runner(tmp_path, NaNClient()).run_off())
    assert report["status"] == "TECHNICAL_FAILURE"
    assert report["failure_code"] == "MISSING_USAGE"


def test_symlinked_approved_root_is_rejected(tmp_path: Path) -> None:
    allowed = tmp_path / "allowed"
    allowed.mkdir()
    link = tmp_path / "allowed-link"
    try:
        link.symlink_to(allowed, target_is_directory=True)
    except (OSError, NotImplementedError):
        pytest.skip("symlink creation is unavailable")
    config = load_config(CONFIG_PATH)
    with pytest.raises(UnsafeOutputPathError):
        asyncio.run(Study2Runner(
            config=config,
            cases=fixture_cases(config),
            client=DeterministicFixtureClient(),
            output_root=link / "output",
            approved_root=link,
            code_sha="fixture-code-sha",
        ).run_off())


def test_persisted_receipt_rejects_result_tampering(tmp_path: Path) -> None:
    asyncio.run(_runner(tmp_path).run_both())
    result_path = tmp_path / "study2-output" / "VEGO_AI_ON" / "result.json"
    payload = json.loads(result_path.read_text(encoding="utf-8"))
    payload["cost_usd"] = 0.123456
    result_path.write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(Study2RunError, match="result hash mismatch"):
        validate_persisted_receipt(tmp_path / "study2-output")


def test_persisted_receipt_rejects_receipt_binding_tampering(tmp_path: Path) -> None:
    asyncio.run(_runner(tmp_path).run_both())
    receipt_path = tmp_path / "study2-output" / "run-receipt.json"
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    receipt["run_id"] = "tampered"
    receipt_path.write_text(json.dumps(receipt), encoding="utf-8")
    with pytest.raises(Study2RunError, match="receipt binding mismatch"):
        validate_persisted_receipt(tmp_path / "study2-output")


def test_persisted_receipt_rejects_event_log_tampering(tmp_path: Path) -> None:
    asyncio.run(_runner(tmp_path).run_both())
    event_path = tmp_path / "study2-output" / "VEGO_AI_OFF" / "events.jsonl"
    event_path.write_text(event_path.read_text(encoding="utf-8") + "\n", encoding="utf-8")
    with pytest.raises(Study2RunError, match="event hash mismatch"):
        validate_persisted_receipt(tmp_path / "study2-output")


def test_on_off_receipt_bindings_are_symmetric(tmp_path: Path) -> None:
    result = asyncio.run(_runner(tmp_path).run_both())
    receipt = result["receipt"]
    for condition in ("VEGO_AI_ON", "VEGO_AI_OFF"):
        bound = receipt["conditions"][condition]
        summary = bound["summary"]
        assert bound["configuration_sha256"] == receipt["configuration_sha256"]
        assert summary["model"] == result["conditions"][condition]["model"]
        assert summary["control_policy"] == result["conditions"][condition]["control_policy"]
        assert summary["corpus_hashes"] == receipt["corpus_hashes"]
    assert receipt["conditions"]["VEGO_AI_ON"]["summary"]["detector_v1"]["status"] == "APPLICABLE"
    assert receipt["conditions"]["VEGO_AI_OFF"]["summary"]["detector_v1"]["status"] == "NOT_APPLICABLE"
