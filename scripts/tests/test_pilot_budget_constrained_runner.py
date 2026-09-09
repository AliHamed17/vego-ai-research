"""Offline tests for the constrained pilot controller.

These tests exercise the preparation/controller contract only.  The client is
explicitly marked offline-only, and no provider adapter is available here.
"""

from __future__ import annotations

import asyncio
import importlib.util
import json
import sys
from pathlib import Path
from typing import Any

import jsonschema
import pytest

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "pilot_budget_constrained_runner.py"


def _load_module():
    spec = importlib.util.spec_from_file_location("pilot_runner_under_test", SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


runner = _load_module()


class FakePilotClient:
    offline_only = True

    def __init__(self, *, finish_reason: str = "stop", fail_run: str | None = None) -> None:
        self.finish_reason = finish_reason
        self.fail_run = fail_run
        self.calls: list[Any] = []
        self.binding_roots: list[Path] = []

    async def complete(self, request: Any) -> Any:
        self.calls.append(request)
        if self.fail_run and request.run_id == self.fail_run:
            raise RuntimeError("fixture failure")
        return runner.PilotResponse(
            payload={"run_id": request.run_id, "case_id": request.case_id, "text": "PRIVATE"},
            input_tokens=16,
            output_tokens=24,
            cost_usd=0.0001,
            finish_reason=self.finish_reason,
        )


def _requests(run_id: str, count: int = 2) -> list[Any]:
    return [
        runner.PilotRequest(
            run_id=run_id,
            case_id=f"case-{i % 2}",
            label=f"{run_id}/case-{i % 2}/{i}",
            system_prompt="private system",
            user_prompt="private user",
        )
        for i in range(count)
    ]


def _controller(tmp_path: Path, client: FakePilotClient) -> Any:
    return runner.PilotExecutionController(
        output_root=tmp_path / "external_data" / "pilot",
        code_sha256="c" * 64,
        case_input_hashes={"case-0": "a" * 64, "case-1": "b" * 64},
        client=client,
    )


def test_all_repeat_bindings_exist_before_first_response(tmp_path: Path) -> None:
    client = FakePilotClient()
    controller = _controller(tmp_path, client)
    schedules = {run_id: _requests(run_id) for run_id in runner.cfg.RUN_IDS}

    original_complete = client.complete

    async def checked_complete(request: Any) -> Any:
        assert controller.reserved_budget_usd == pytest.approx(
            controller.repeat_reserve_usd * runner.cfg.REPEATS
        )
        for run_id in runner.cfg.RUN_IDS:
            binding = controller.output_root / run_id / "prospective-binding.json"
            assert binding.is_file(), f"binding missing before first response: {run_id}"
            assert json.loads(binding.read_text(encoding="utf-8"))["created_before_results"] is True
        return await original_complete(request)

    client.complete = checked_complete  # type: ignore[method-assign]
    summary = asyncio.run(controller.run(schedules))

    assert summary["status"] == "PREPARED_OFFLINE_ONLY"
    assert summary["provider_calls"] == 0
    assert summary["reservation_complete"] is True
    assert summary["reserved_budget_usd"] == pytest.approx(
        summary["bound"]["total_worst_case_usd"]
    )
    for run_id in runner.cfg.RUN_IDS:
        receipt = json.loads(
            (controller.output_root / run_id / "run-receipt.json").read_text(encoding="utf-8")
        )
        binding_path = controller.output_root / run_id / "prospective-binding.json"
        assert receipt["event_log_sha256"]
        assert receipt["lifecycle_summary"]["complete"] is True
        assert receipt["config_sha256"] == runner.cfg.config_sha256()
        assert receipt["code_sha256"] == "c" * 64
        assert receipt["prospective_binding_sha256"] == runner.hashlib.sha256(binding_path.read_bytes()).hexdigest()
        binding = json.loads(binding_path.read_text(encoding="utf-8"))
        assert binding["global_reserved_budget_usd"] == pytest.approx(1.759104)


def test_truncation_is_reported_and_not_repaired(tmp_path: Path) -> None:
    controller = _controller(tmp_path, FakePilotClient(finish_reason="length"))
    schedules = {run_id: _requests(run_id, 1) for run_id in runner.cfg.RUN_IDS}
    summary = asyncio.run(controller.run(schedules))

    repeat = summary["repeats"][0]
    assert repeat["status"] == "TRUNCATION_AFFECTED"
    assert repeat["truncated_calls"] == 1
    assert repeat["retry_count"] == 0
    assert repeat["scientific_denominator_eligible"] is False


def test_repeat_failure_is_preserved_without_automatic_repeat_retry(tmp_path: Path) -> None:
    client = FakePilotClient(fail_run="PILOT-02")
    controller = _controller(tmp_path, client)
    schedules = {run_id: _requests(run_id, 1) for run_id in runner.cfg.RUN_IDS}
    summary = asyncio.run(controller.run(schedules))

    failed = next(row for row in summary["repeats"] if row["run_id"] == "PILOT-02")
    assert failed["status"] == "TECHNICAL_FAILURE"
    assert failed["repeat_retry_count"] == 0
    assert failed["scientific_denominator_eligible"] is False
    assert sum(request.run_id == "PILOT-02" for request in client.calls) == runner.cfg.MAX_RETRIES_PER_CALL + 1


def test_call_cap_is_enforced_and_raw_payload_is_not_persisted(tmp_path: Path) -> None:
    run_id = runner.cfg.RUN_IDS[0]
    controller = _controller(tmp_path, FakePilotClient())
    schedules = {rid: _requests(rid, 0) for rid in runner.cfg.RUN_IDS}
    schedules[run_id] = _requests(run_id, runner.cfg.CALL_CAP_PER_REPEAT + 5)
    summary = asyncio.run(controller.run(schedules))

    repeat = next(row for row in summary["repeats"] if row["run_id"] == run_id)
    assert repeat["status"] == "STOPPED_AT_CALL_CAP"
    assert repeat["calls"] == runner.cfg.CALL_CAP_PER_REPEAT
    event_log = (controller.output_root / run_id / "events.jsonl").read_text(encoding="utf-8")
    assert "PRIVATE" not in event_log
    assert "private system" not in event_log
    assert "prompt_sha256" in event_log


def test_missing_repeat_schedule_fails_before_any_call(tmp_path: Path) -> None:
    client = FakePilotClient()
    controller = _controller(tmp_path, client)
    with pytest.raises(runner.PilotProtocolError, match="exactly the frozen repeat IDs"):
        asyncio.run(controller.run({"PILOT-01": _requests("PILOT-01")}))
    assert client.calls == []


def test_budget_gate_refuses_before_any_repeat_is_started(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    client = FakePilotClient()
    controller = _controller(tmp_path, client)
    monkeypatch.setattr(runner.cfg, "BUDGET_USD", 0.01)
    schedules = {run_id: _requests(run_id, 1) for run_id in runner.cfg.RUN_IDS}
    with pytest.raises(runner.cfg.BoundExceedsCeiling):
        asyncio.run(controller.run(schedules))
    assert client.calls == []
    assert not controller.output_root.exists()


def test_repeat_receipts_validate_against_the_pilot_schema(tmp_path: Path) -> None:
    controller = _controller(tmp_path, FakePilotClient())
    schedules = {run_id: _requests(run_id, 1) for run_id in runner.cfg.RUN_IDS}
    asyncio.run(controller.run(schedules))
    schema = json.loads(
        (ROOT / "schemas" / "pilot-repeat-receipt-v1.schema.json").read_text(encoding="utf-8")
    )
    for run_id in runner.cfg.RUN_IDS:
        receipt = json.loads(
            (controller.output_root / run_id / "run-receipt.json").read_text(encoding="utf-8")
        )
        jsonschema.Draft202012Validator(schema).validate(receipt)


def test_non_offline_client_is_rejected(tmp_path: Path) -> None:
    client = FakePilotClient()
    client.offline_only = False
    with pytest.raises(runner.PilotProtocolError, match="offline-only"):
        _controller(tmp_path, client)


def test_output_root_must_be_git_ignored_external_data(tmp_path: Path) -> None:
    with pytest.raises(runner.PilotProtocolError, match="external_data"):
        runner.PilotExecutionController(
            output_root=tmp_path / "tracked" / "pilot",
            code_sha256="c" * 64,
            case_input_hashes={"case-0": "a" * 64},
            client=FakePilotClient(),
        )


def test_malformed_response_is_recorded_as_a_failure_without_leaking_content(tmp_path: Path) -> None:
    class MalformedClient(FakePilotClient):
        async def complete(self, request: Any) -> Any:
            self.calls.append(request)
            return {"private": "do-not-persist"}

    controller = _controller(tmp_path, MalformedClient())
    schedules = {run_id: _requests(run_id, 1) for run_id in runner.cfg.RUN_IDS}
    summary = asyncio.run(controller.run(schedules))
    assert summary["repeats"][0]["status"] == "TECHNICAL_FAILURE"
    event_log = (controller.output_root / "PILOT-01" / "events.jsonl").read_text(encoding="utf-8")
    assert "do-not-persist" not in event_log


def test_closed_study1b_runner_cannot_invoke_the_provider(monkeypatch: pytest.MonkeyPatch) -> None:
    path = ROOT / "scripts" / "study1b_variance_runs.py"
    spec = importlib.util.spec_from_file_location("closed_study1b", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    called = False

    def forbidden(*args: Any, **kwargs: Any) -> Any:
        nonlocal called
        called = True
        raise AssertionError("provider path must not be reached")

    monkeypatch.setattr(module, "execute_repeat", forbidden)
    assert module.main(["--execute", "--budget-usd", "40"]) != 0
    assert called is False
