"""Protocol guards for the planned multi-dataset ON/OFF study.

These guards prepare immutable, hash-safe configuration evidence. They do not
invoke a provider and they deliberately never authorize execution themselves.
"""

from __future__ import annotations

import hashlib
import json
import re
from collections.abc import Mapping
from typing import Any

from .schemas import SchemaError, validate_named


class ProtocolError(ValueError):
    """Raised when a proposed protocol is not safe to freeze or execute."""


_SHA256_RE = re.compile(r"^[a-f0-9]{64}$")
_CONTROL_FIELDS = {
    "provider",
    "model_id",
    "model_version",
    "temperature",
    "max_output_tokens",
    "timeout_seconds",
    "retry_policy",
    "concurrency",
    "budget_ceiling_usd",
    "call_ceiling",
    "output_schema",
    "egress",
}
_ON_EXPECTED = {
    "agent_decomposition": True,
    "inter_agent_qa": True,
    "round_loop": True,
    "detector_v1": "APPLICABLE_TO_COMPLETE_QA_EPISODES_ONLY",
    "agent4_queue": "SEPARATE_NOT_DETECTOR_INPUT",
}
_OFF_EXPECTED = {
    "agent_decomposition": False,
    "inter_agent_qa": False,
    "round_loop": False,
    "detector_v1": "NOT_APPLICABLE",
    "agent4_queue": "NOT_INVOKED",
}


def _canonical_sha256(value: Any) -> str:
    encoded = (json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode(
        "utf-8"
    )
    return hashlib.sha256(encoded).hexdigest()


def _is_sha256(value: object) -> bool:
    return isinstance(value, str) and bool(_SHA256_RE.fullmatch(value.lower()))


def validate_on_off_contract(contract: Mapping[str, Any]) -> None:
    """Validate matched controls plus strict ON/OFF mechanism separation."""

    if not isinstance(contract, Mapping):
        raise ProtocolError("ON/OFF contract must be a mapping")
    try:
        validate_named(contract, "multidataset-on-off-contract-v1.schema.json")
    except SchemaError as exc:
        raise ProtocolError(str(exc)) from exc
    if contract.get("schema_version") != "vego-multidataset-on-off-contract-v1":
        raise ProtocolError("unsupported ON/OFF contract schema")
    controls = contract.get("shared_controls")
    if not isinstance(controls, Mapping):
        raise ProtocolError("shared controls are required")
    if set(controls) != _CONTROL_FIELDS:
        raise ProtocolError("shared controls must be exact and contain no fallback policy")
    if controls.get("provider") != "OpenAI":
        raise ProtocolError("only OpenAI is allowed by the frozen protocol")
    for model_field in ("model_id", "model_version"):
        if not isinstance(controls.get(model_field), str) or not controls[model_field].strip():
            raise ProtocolError(f"{model_field} must be a non-empty frozen value")
    temperature = controls.get("temperature")
    if (
        not isinstance(temperature, (int, float))
        or isinstance(temperature, bool)
        or not 0.0 <= float(temperature) <= 2.0
    ):
        raise ProtocolError("temperature must be a number from 0.0 through 2.0")
    max_output_tokens = controls.get("max_output_tokens")
    if not isinstance(max_output_tokens, int) or isinstance(max_output_tokens, bool) or max_output_tokens < 1:
        raise ProtocolError("output-token cap must be a positive integer")
    timeout = controls.get("timeout_seconds")
    if not isinstance(timeout, int) or isinstance(timeout, bool) or timeout < 1:
        raise ProtocolError("timeout must be a positive integer in seconds")
    concurrency = controls.get("concurrency")
    if not isinstance(concurrency, int) or isinstance(concurrency, bool) or concurrency < 1:
        raise ProtocolError("concurrency must be a positive integer")
    if not isinstance(controls.get("output_schema"), str) or not controls["output_schema"].strip():
        raise ProtocolError("output schema must be a non-empty identifier")
    budget = controls.get("budget_ceiling_usd")
    if (
        not isinstance(budget, (int, float))
        or isinstance(budget, bool)
        or not 0 < float(budget) <= 6.0
    ):
        raise ProtocolError("budget ceiling must be positive and no more than USD 6.00")
    call_ceiling = controls.get("call_ceiling")
    if not isinstance(call_ceiling, int) or isinstance(call_ceiling, bool) or call_ceiling < 1:
        raise ProtocolError("call ceiling must be a positive integer")
    if controls.get("retry_policy") != "ONE_TRANSPORT_RETRY_BEFORE_VALID_OUTPUT":
        raise ProtocolError("retry policy must allow only one pre-valid-output transport retry")
    if controls.get("egress") != "PROVIDER_ENDPOINT_ONLY_DURING_AUTHORIZED_EXECUTION":
        raise ProtocolError("egress policy is not sufficiently restrictive")
    for condition, expected in (("VEGO_AI_ON", _ON_EXPECTED), ("VEGO_AI_OFF", _OFF_EXPECTED)):
        observed = contract.get(condition)
        if not isinstance(observed, Mapping):
            raise ProtocolError(f"{condition} mechanism is required")
        if dict(observed) != expected:
            raise ProtocolError(f"{condition} mechanism violates the frozen boundary")


def build_real_execution_gate(
    data_card: Mapping[str, Any],
    contract: Mapping[str, Any],
    selection_manifest: Mapping[str, Any],
) -> dict[str, Any]:
    """Create a non-authorizing status for a future real execution.

    This function is intentionally conservative: even a fully frozen model
    leaves the protocol pending the other pre-execution gates and an explicit
    one-time human authorization. It cannot turn a configuration into a run.
    """

    validate_on_off_contract(contract)
    if data_card.get("decision") not in {"ADMITTED", "ADMITTED_WITH_LIMITATIONS"}:
        raise ProtocolError("the dataset must be admitted before execution planning")
    licence = data_card.get("licence")
    raw = data_card.get("raw_artifact")
    if not isinstance(licence, Mapping) or not isinstance(licence.get("name"), str):
        raise ProtocolError("an admitted execution dataset requires a known licence")
    if not isinstance(raw, Mapping) or not _is_sha256(raw.get("sha256")):
        raise ProtocolError("an admitted execution dataset requires a raw SHA-256")
    if selection_manifest.get("dataset_id") != data_card.get("dataset_id"):
        raise ProtocolError("selection manifest dataset does not match the data card")
    if not _is_sha256(selection_manifest.get("selection_sha256")):
        raise ProtocolError("selection manifest must be hash-bound")
    controls = contract["shared_controls"]
    model_id = controls["model_id"]
    model_version = controls["model_version"]
    if not isinstance(model_id, str) or not isinstance(model_version, str):
        raise ProtocolError("model fields must be strings")
    model_pending = model_id.startswith("TO_BE_") or model_version.startswith("TO_BE_")
    status = "BLOCKED_PENDING_USER_FROZEN_MODEL_SELECTION" if model_pending else "PENDING_FULL_PRE_EXECUTION_GATES"
    return {
        "schema_version": "vego-multidataset-real-execution-gate-v1",
        "status": status,
        "provider_calls_permitted": False,
        "dataset_id": data_card["dataset_id"],
        "dataset_raw_sha256": raw["sha256"],
        "selection_sha256": selection_manifest["selection_sha256"],
        "on_off_contract_sha256": _canonical_sha256(contract),
        "model": {"provider": controls["provider"], "model_id": model_id, "model_version": model_version},
        "remaining_gates": [
            "EXACT_HEAD_GREEN_CI",
            "FULL_OFFLINE_FAKE_PREFLIGHT",
            "PRIVATE_OUTPUT_ROOT_BINDING",
            "PRE_EXECUTION_EVIDENCE_PACKET",
            "EXPLICIT_ONE_TIME_HUMAN_AUTHORIZATION",
        ],
    }
