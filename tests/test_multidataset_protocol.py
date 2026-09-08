from __future__ import annotations

import copy

import pytest

from vego_multidataset.protocol import (
    ProtocolError,
    build_real_execution_gate,
    validate_on_off_contract,
)


def _contract() -> dict[str, object]:
    shared = {
        "provider": "OpenAI",
        "model_id": "TO_BE_SELECTED_BY_USER",
        "model_version": "TO_BE_FROZEN",
        "temperature": 0.0,
        "max_output_tokens": 512,
        "timeout_seconds": 60,
        "retry_policy": "ONE_TRANSPORT_RETRY_BEFORE_VALID_OUTPUT",
        "concurrency": 1,
        "budget_ceiling_usd": 6.0,
        "call_ceiling": 20,
        "output_schema": "vego-multidataset-output-v1",
        "egress": "PROVIDER_ENDPOINT_ONLY_DURING_AUTHORIZED_EXECUTION",
    }
    return {
        "schema_version": "vego-multidataset-on-off-contract-v1",
        "shared_controls": shared,
        "VEGO_AI_ON": {
            "agent_decomposition": True,
            "inter_agent_qa": True,
            "round_loop": True,
            "detector_v1": "APPLICABLE_TO_COMPLETE_QA_EPISODES_ONLY",
            "agent4_queue": "SEPARATE_NOT_DETECTOR_INPUT",
        },
        "VEGO_AI_OFF": {
            "agent_decomposition": False,
            "inter_agent_qa": False,
            "round_loop": False,
            "detector_v1": "NOT_APPLICABLE",
            "agent4_queue": "NOT_INVOKED",
        },
    }


def _admitted_card() -> dict[str, object]:
    return {
        "dataset_id": "QURE_EXTERNAL_REQUIREMENTS_QUALITY_VALIDATION",
        "decision": "ADMITTED_WITH_LIMITATIONS",
        "licence": {"name": "CC-BY-4.0"},
        "raw_artifact": {"sha256": "a" * 64, "file_inventory": [{"sha256": "a" * 64}]},
    }


def test_contract_requires_matched_controls_and_strict_off_boundary() -> None:
    contract = _contract()
    validate_on_off_contract(contract)

    altered = copy.deepcopy(contract)
    altered["VEGO_AI_OFF"]["inter_agent_qa"] = True
    with pytest.raises(ProtocolError, match="OFF"):
        validate_on_off_contract(altered)

    altered = copy.deepcopy(contract)
    altered["shared_controls"]["budget_ceiling_usd"] = 6.01
    with pytest.raises(ProtocolError, match="budget"):
        validate_on_off_contract(altered)


def test_real_execution_gate_requires_admission_and_explicit_model_selection() -> None:
    contract = _contract()
    selection = {
        "schema_version": "vego-multidataset-selection-v1",
        "dataset_id": "QURE_EXTERNAL_REQUIREMENTS_QUALITY_VALIDATION",
        "selection_sha256": "b" * 64,
    }
    gate = build_real_execution_gate(_admitted_card(), contract, selection)
    assert gate["status"] == "BLOCKED_PENDING_USER_FROZEN_MODEL_SELECTION"
    assert gate["provider_calls_permitted"] is False

    contract["shared_controls"]["model_id"] = "gpt-example"
    contract["shared_controls"]["model_version"] = "gpt-example-2026-09-08"
    gate = build_real_execution_gate(_admitted_card(), contract, selection)
    assert gate["status"] == "PENDING_FULL_PRE_EXECUTION_GATES"
    assert gate["provider_calls_permitted"] is False

    card = _admitted_card()
    card["decision"] = "NOT_ADMITTED"
    with pytest.raises(ProtocolError, match="admitted"):
        build_real_execution_gate(card, contract, selection)


def test_contract_rejects_model_fallback_and_on_off_control_drift() -> None:
    contract = _contract()
    contract["shared_controls"]["fallback_model_id"] = "not-allowed"
    with pytest.raises(ProtocolError, match="fallback"):
        validate_on_off_contract(contract)


@pytest.mark.parametrize(
    ("field", "value", "message"),
    [
        ("temperature", -0.1, "temperature"),
        ("max_output_tokens", 0, "output-token"),
        ("timeout_seconds", 0, "timeout"),
        ("concurrency", 0, "concurrency"),
        ("budget_ceiling_usd", True, "budget"),
        ("call_ceiling", True, "call ceiling"),
        ("output_schema", "", "output schema"),
        ("egress", "ALLOW_ALL", "egress"),
    ],
)
def test_contract_rejects_unenforceable_shared_control(
    field: str,
    value: object,
    message: str,
) -> None:
    contract = _contract()
    contract["shared_controls"][field] = value
    with pytest.raises(ProtocolError, match=message):
        validate_on_off_contract(contract)
