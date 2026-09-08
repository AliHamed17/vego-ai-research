"""Local, deterministic engineering preflight for generic ON/OFF plumbing.

This module never imports a provider SDK or the protected AirTravel runtime.
It accepts only explicitly labelled engineering fixtures and persists hashes,
not fixture text, into an ignored output root.
"""

from __future__ import annotations

import hashlib
import json
import re
import socket
from collections.abc import Iterator, Mapping, Sequence
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Protocol

from vego_study2.paths import UnsafeOutputPathError, ensure_safe_output_root

from .adapter import ExecutionCase
from .schemas import SchemaError, validate_named


class EngineeringPreflightError(ValueError):
    """Raised when a local-only engineering preflight cannot prove its boundary."""


_FIXTURE_MARKER = "ENGINEERING_FIXTURE_NOT_SCIENTIFIC"
_SHA256_RE = re.compile(r"^[a-f0-9]{40}$")


@dataclass(frozen=True)
class FixtureRequest:
    condition: str
    case_id: str
    role: str
    requirement_text: str
    input_sha256: str


@dataclass(frozen=True)
class FixtureResponse:
    valid: bool = True


class OfflineFixtureClient(Protocol):
    offline_only: bool

    async def complete(self, request: FixtureRequest) -> FixtureResponse: ...


class DeterministicOfflineFixtureClient:
    """A non-networking client used solely for engineering preflight tests."""

    offline_only = True

    async def complete(self, request: FixtureRequest) -> FixtureResponse:
        del request
        return FixtureResponse()


def _canonical_json(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode(
        "utf-8"
    )


def _sha256(value: Any) -> str:
    return hashlib.sha256(_canonical_json(value)).hexdigest()


@contextmanager
def _network_disabled(state: dict[str, int]) -> Iterator[None]:
    """Fail closed on any socket egress attempt during local fixture work."""

    original_create = socket.create_connection
    original_getaddrinfo = socket.getaddrinfo
    original_connect = socket.socket.connect
    original_connect_ex = socket.socket.connect_ex

    def deny(*args: Any, **kwargs: Any) -> Any:
        del args, kwargs
        state["blocked_egress_attempts"] += 1
        raise EngineeringPreflightError("EGRESS_BLOCKED")

    socket.create_connection = deny  # type: ignore[assignment]
    socket.getaddrinfo = deny  # type: ignore[assignment]
    socket.socket.connect = deny  # type: ignore[method-assign]
    socket.socket.connect_ex = deny  # type: ignore[method-assign]
    try:
        yield
    finally:
        socket.create_connection = original_create  # type: ignore[assignment]
        socket.getaddrinfo = original_getaddrinfo  # type: ignore[assignment]
        socket.socket.connect = original_connect  # type: ignore[method-assign]
        socket.socket.connect_ex = original_connect_ex  # type: ignore[method-assign]


class EngineeringPreflightRunner:
    """Exercise the generic adapter envelope without real data or providers."""

    def __init__(
        self,
        *,
        cases: Sequence[ExecutionCase],
        client: OfflineFixtureClient,
        output_root: Path,
        approved_root: Path,
        execution_code_sha: str,
    ) -> None:
        if type(client) is not DeterministicOfflineFixtureClient:
            raise EngineeringPreflightError("preflight requires the trusted deterministic fixture client")
        if not cases:
            raise EngineeringPreflightError("preflight requires at least one engineering fixture")
        if any(case.dataset_id != _FIXTURE_MARKER for case in cases):
            raise EngineeringPreflightError("preflight accepts engineering fixtures only")
        if any(_FIXTURE_MARKER not in case.requirement_text for case in cases):
            raise EngineeringPreflightError("preflight fixture marker is missing")
        if len({case.case_id for case in cases}) != len(cases):
            raise EngineeringPreflightError("preflight fixture case ids must be unique")
        if not isinstance(execution_code_sha, str) or not _SHA256_RE.fullmatch(execution_code_sha.lower()):
            raise EngineeringPreflightError("preflight requires an immutable execution-code SHA")
        self.cases = tuple(cases)
        self.client = client
        self.execution_code_sha = execution_code_sha.lower()
        try:
            self.output_root = ensure_safe_output_root(Path(output_root), Path(approved_root))
        except UnsafeOutputPathError as exc:
            raise EngineeringPreflightError(str(exc)) from exc

    async def _run_condition(
        self,
        condition: str,
        roles: tuple[str, ...],
        state: dict[str, int],
    ) -> dict[str, Any]:
        calls: list[dict[str, str]] = []
        for case in self.cases:
            for role in roles:
                request = FixtureRequest(
                    condition=condition,
                    case_id=case.case_id,
                    role=role,
                    requirement_text=case.requirement_text,
                    input_sha256=case.input_sha256,
                )
                response = await self.client.complete(request)
                state["fake_client_requests"] += 1
                if not isinstance(response, FixtureResponse) or response.valid is not True:
                    raise EngineeringPreflightError("fixture client returned an invalid response")
                calls.append(
                    {
                        "condition": condition,
                        "case_id": case.case_id,
                        "role": role,
                        "input_sha256": case.input_sha256,
                    }
                )
        on = condition == "VEGO_AI_ON"
        return {
            "condition": condition,
            "case_input_hashes": {case.case_id: case.input_sha256 for case in self.cases},
            "fake_client_requests": len(calls),
            "call_manifest_sha256": _sha256(calls),
            "agent_decomposition": on,
            "inter_agent_qa": on,
            "round_loop": on,
            "qa_envelope_episodes": len(self.cases) if on else 0,
            "detector_v1": "NOT_EXECUTED_ENGINEERING_ENVELOPE_ONLY" if on else "NOT_APPLICABLE",
            "agent4_invoked": False,
            "raw_content_persisted": False,
        }

    async def run(self) -> dict[str, Any]:
        """Run local calls and write a self-binding, non-scientific receipt."""

        self.output_root.mkdir(parents=True, exist_ok=True)
        state = {"fake_client_requests": 0, "blocked_egress_attempts": 0}
        with _network_disabled(state):
            on = await self._run_condition("VEGO_AI_ON", ("agent1", "agent2", "agent3", "agent4"), state)
            off = await self._run_condition("VEGO_AI_OFF", ("direct",), state)
        unsigned = {
            "schema_version": "vego-multidataset-engineering-preflight-receipt-v1",
            "evidence_class": "ENGINEERING_FIXTURE_ONLY",
            "scientific_result_status": "NOT_EXECUTED",
            "study1_pooled": False,
            "execution_code_sha": self.execution_code_sha,
            "provider_calls": 0,
            "external_provider_calls": 0,
            "network_policy": "DISABLED",
            "blocked_egress_attempts": state["blocked_egress_attempts"],
            "fake_client_requests": state["fake_client_requests"],
            "conditions": {"VEGO_AI_ON": on, "VEGO_AI_OFF": off},
        }
        receipt = {**unsigned, "receipt_binding": {"algorithm": "SHA-256", "content_sha256": _sha256(unsigned)}}
        receipt_path = self.output_root / "engineering-preflight-receipt.json"
        receipt_path.write_bytes(_canonical_json(receipt))
        return receipt


def validate_engineering_preflight_receipt(path: Path) -> dict[str, Any]:
    """Validate a receipt without contacting a provider or loading source data."""

    try:
        receipt = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise EngineeringPreflightError("engineering preflight receipt is unavailable") from exc
    try:
        validate_named(receipt, "multidataset-engineering-preflight-receipt-v1.schema.json")
    except SchemaError as exc:
        raise EngineeringPreflightError(str(exc)) from exc
    binding = receipt.get("receipt_binding")
    if not isinstance(binding, Mapping) or binding.get("algorithm") != "SHA-256":
        raise EngineeringPreflightError("receipt binding is missing")
    unsigned = dict(receipt)
    unsigned.pop("receipt_binding", None)
    if binding.get("content_sha256") != _sha256(unsigned):
        raise EngineeringPreflightError("receipt binding mismatch")
    if receipt.get("evidence_class") != "ENGINEERING_FIXTURE_ONLY":
        raise EngineeringPreflightError("receipt is not engineering-only")
    if receipt.get("scientific_result_status") != "NOT_EXECUTED":
        raise EngineeringPreflightError("receipt makes an unsupported scientific claim")
    execution_code_sha = receipt.get("execution_code_sha")
    if not isinstance(execution_code_sha, str) or not _SHA256_RE.fullmatch(execution_code_sha):
        raise EngineeringPreflightError("receipt execution code SHA is invalid")
    if receipt.get("provider_calls") != 0 or receipt.get("external_provider_calls") != 0:
        raise EngineeringPreflightError("receipt reports a provider or external call")
    conditions = receipt.get("conditions")
    if not isinstance(conditions, Mapping) or set(conditions) != {"VEGO_AI_ON", "VEGO_AI_OFF"}:
        raise EngineeringPreflightError("receipt conditions are unavailable")
    off = conditions.get("VEGO_AI_OFF")
    on = conditions.get("VEGO_AI_ON")
    if not isinstance(on, Mapping) or not isinstance(off, Mapping):
        raise EngineeringPreflightError("receipt condition records are unavailable")
    if on.get("detector_v1") != "NOT_EXECUTED_ENGINEERING_ENVELOPE_ONLY":
        raise EngineeringPreflightError("ON detector boundary is invalid")
    if (
        on.get("agent_decomposition") is not True
        or on.get("inter_agent_qa") is not True
        or on.get("round_loop") is not True
        or not isinstance(on.get("qa_envelope_episodes"), int)
        or on["qa_envelope_episodes"] < 1
        or on.get("agent4_invoked") is not False
        or on.get("raw_content_persisted") is not False
    ):
        raise EngineeringPreflightError("ON boundary is invalid")
    if (
        off.get("detector_v1") != "NOT_APPLICABLE"
        or off.get("agent_decomposition") is not False
        or off.get("inter_agent_qa") is not False
        or off.get("round_loop") is not False
        or off.get("qa_envelope_episodes") != 0
        or off.get("agent4_invoked") is not False
        or off.get("raw_content_persisted") is not False
    ):
        raise EngineeringPreflightError("OFF boundary is invalid")
    return receipt
