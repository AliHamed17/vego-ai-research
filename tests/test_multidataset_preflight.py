from __future__ import annotations

import asyncio
import hashlib
import json
import socket
from pathlib import Path

import pytest

from vego_multidataset.adapter import build_execution_projection
from vego_multidataset.preflight import (
    DeterministicOfflineFixtureClient,
    EngineeringPreflightError,
    EngineeringPreflightRunner,
    _network_disabled,
    validate_engineering_preflight_receipt,
)


def _fixture_cases():
    projection = build_execution_projection(
        [
            {
                "id": "fixture-a",
                "text": "ENGINEERING_FIXTURE_NOT_SCIENTIFIC: concise requirement A",
                "label": "ok",
            },
            {
                "id": "fixture-b",
                "text": "ENGINEERING_FIXTURE_NOT_SCIENTIFIC: concise requirement B",
                "label": "defect",
            },
        ],
        dataset_id="ENGINEERING_FIXTURE_NOT_SCIENTIFIC",
        id_field="id",
        text_field="text",
        label_field="label",
    )
    return projection.execution_cases


def test_engineering_preflight_keeps_on_off_mechanisms_separate(tmp_path: Path) -> None:
    result = asyncio.run(
        EngineeringPreflightRunner(
            cases=_fixture_cases(),
            client=DeterministicOfflineFixtureClient(),
            output_root=tmp_path / "output",
            approved_root=tmp_path,
            execution_code_sha="a" * 40,
        ).run()
    )
    on = result["conditions"]["VEGO_AI_ON"]
    off = result["conditions"]["VEGO_AI_OFF"]
    assert result["evidence_class"] == "ENGINEERING_FIXTURE_ONLY"
    assert result["scientific_result_status"] == "NOT_EXECUTED"
    assert result["execution_code_sha"] == "a" * 40
    assert result["provider_calls"] == 0
    assert result["external_provider_calls"] == 0
    assert on["fake_client_requests"] == 8
    assert on["qa_envelope_episodes"] == 2
    assert on["detector_v1"] == "NOT_EXECUTED_ENGINEERING_ENVELOPE_ONLY"
    assert off["fake_client_requests"] == 2
    assert off["qa_envelope_episodes"] == 0
    assert off["detector_v1"] == "NOT_APPLICABLE"
    assert off["agent4_invoked"] is False
    validate_engineering_preflight_receipt(tmp_path / "output" / "engineering-preflight-receipt.json")


def test_fixture_preflight_rejects_non_fixture_input(tmp_path: Path) -> None:
    cases = list(_fixture_cases())
    cases[0] = cases[0].__class__(
        dataset_id=cases[0].dataset_id,
        case_id=cases[0].case_id,
        requirement_text="non-fixture input must never be relabelled as engineering only",
        input_sha256=cases[0].input_sha256,
    )
    with pytest.raises(EngineeringPreflightError, match="fixture"):
        EngineeringPreflightRunner(
            cases=tuple(cases),
            client=DeterministicOfflineFixtureClient(),
            output_root=tmp_path / "output",
            approved_root=tmp_path,
            execution_code_sha="a" * 40,
        )


def test_preflight_rejects_untrusted_fixture_client_and_network_guard_blocks_egress(tmp_path: Path) -> None:
    class EgressAttemptClient(DeterministicOfflineFixtureClient):
        async def complete(self, request):  # type: ignore[no-untyped-def]
            socket.getaddrinfo("example.invalid", 443)
            return await super().complete(request)

    with pytest.raises(EngineeringPreflightError, match="trusted deterministic"):
        EngineeringPreflightRunner(
            cases=_fixture_cases(),
            client=EgressAttemptClient(),
            output_root=tmp_path / "output",
            approved_root=tmp_path,
            execution_code_sha="a" * 40,
        )

    state = {"blocked_egress_attempts": 0}
    with _network_disabled(state), pytest.raises(EngineeringPreflightError, match="EGRESS_BLOCKED"):
        socket.getaddrinfo("example.invalid", 443)
    assert state["blocked_egress_attempts"] == 1


def test_receipt_is_hash_bound_and_does_not_persist_fixture_text(tmp_path: Path) -> None:
    asyncio.run(
        EngineeringPreflightRunner(
            cases=_fixture_cases(),
            client=DeterministicOfflineFixtureClient(),
            output_root=tmp_path / "output",
            approved_root=tmp_path,
            execution_code_sha="a" * 40,
        ).run()
    )
    receipt_path = tmp_path / "output" / "engineering-preflight-receipt.json"
    raw = receipt_path.read_text(encoding="utf-8")
    assert "concise requirement" not in raw
    receipt = json.loads(raw)
    assert receipt["receipt_binding"]["content_sha256"]
    receipt["conditions"]["VEGO_AI_OFF"]["fake_client_requests"] = 999
    receipt_path.write_text(json.dumps(receipt), encoding="utf-8")
    with pytest.raises(EngineeringPreflightError, match="binding"):
        validate_engineering_preflight_receipt(receipt_path)


@pytest.mark.parametrize(
    ("field", "value"),
    [("agent_decomposition", True), ("qa_envelope_episodes", 1), ("inter_agent_qa", True)],
)
def test_receipt_validator_rejects_semantically_invalid_off_shape(
    tmp_path: Path,
    field: str,
    value: object,
) -> None:
    asyncio.run(
        EngineeringPreflightRunner(
            cases=_fixture_cases(),
            client=DeterministicOfflineFixtureClient(),
            output_root=tmp_path / "output",
            approved_root=tmp_path,
            execution_code_sha="a" * 40,
        ).run()
    )
    receipt_path = tmp_path / "output" / "engineering-preflight-receipt.json"
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    receipt["conditions"]["VEGO_AI_OFF"][field] = value
    unsigned = dict(receipt)
    unsigned.pop("receipt_binding")
    canonical = json.dumps(unsigned, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n"
    receipt["receipt_binding"]["content_sha256"] = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    receipt_path.write_text(json.dumps(receipt), encoding="utf-8")
    with pytest.raises(EngineeringPreflightError):
        validate_engineering_preflight_receipt(receipt_path)
