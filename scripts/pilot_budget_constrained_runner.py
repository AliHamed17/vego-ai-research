"""Fail-closed controller for the budget-constrained exploratory pilot.

The controller is deliberately provider-agnostic and accepts only a client that
declares ``offline_only = True``.  It is therefore suitable for engineering
preflight and deterministic fixtures, not for a provider-backed run.  A future
provider execution requires a separately reviewed adapter and fresh
authorization; this module must not be used to smuggle one in.

The controller enforces the frozen pilot decisions at the boundary where a
request would be issued:

* the complete three-repeat budget is reserved before the first repeat starts;
* every attempt (including transport retries) consumes one call-cap slot;
* truncation is recorded and makes the repeat ineligible for scientific
  communication reporting;
* a failed repeat is recorded once and is never automatically restarted; and
* only hashes and closed metadata are persisted to the private output root.
"""

from __future__ import annotations

import asyncio
import hashlib
import json
import math
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Protocol

import pilot_budget_constrained_config as cfg
from pilot_budget_constrained_config import config_sha256, frozen_config

from vego_study2.paths import UnsafeOutputPathError, ensure_safe_output_root


class PilotProtocolError(ValueError):
    """Raised when a frozen pilot contract cannot be satisfied."""


class PilotClient(Protocol):
    offline_only: bool

    async def complete(self, request: PilotRequest) -> PilotResponse: ...


@dataclass(frozen=True)
class PilotRequest:
    """The metadata needed to issue one already-prepared request.

    Prompts are accepted in memory so a future orchestrator can construct its
    request, but they are never written to the controller's event log.
    """

    run_id: str
    case_id: str
    label: str
    system_prompt: str
    user_prompt: str


@dataclass(frozen=True)
class PilotResponse:
    """Provider-shaped response used by offline fixtures only."""

    payload: Any
    input_tokens: int
    output_tokens: int
    cost_usd: float
    finish_reason: str


def _canonical(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode(
        "utf-8"
    )


def _sha256(value: Any) -> str:
    if isinstance(value, bytes):
        data = value
    else:
        data = _canonical(value)
    return hashlib.sha256(data).hexdigest()


def _now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _write_exclusive_json(path: Path, value: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    try:
        with path.open("x", encoding="utf-8", newline="\n") as handle:
            handle.write(payload)
    except FileExistsError as exc:
        raise PilotProtocolError(f"refusing to overwrite existing pilot artifact: {path.name}") from exc


class PilotExecutionController:
    """Prepare and exercise one offline-only pilot plan.

    ``run`` is intentionally an in-process fixture controller.  It performs no
    import of an SDK, no DNS/socket operation, and no network call.  A client
    without the explicit offline marker is rejected before any output or
    request is created.
    """

    def __init__(
        self,
        *,
        output_root: Path,
        code_sha256: str,
        case_input_hashes: Mapping[str, str],
        client: PilotClient,
        approved_root: Path | None = None,
    ) -> None:
        if getattr(client, "offline_only", False) is not True:
            raise PilotProtocolError("pilot controller requires an explicit offline-only client")
        if not isinstance(code_sha256, str) or len(code_sha256) != 64:
            raise PilotProtocolError("code_sha256 is required for prospective binding")
        try:
            int(code_sha256, 16)
        except ValueError as exc:
            raise PilotProtocolError("code_sha256 is required for prospective binding") from exc
        normalized_hashes = dict(case_input_hashes)
        expected_cases = set(normalized_hashes)
        if not expected_cases:
            raise PilotProtocolError("at least one case input hash is required")
        for case_id, digest in normalized_hashes.items():
            if not isinstance(case_id, str) or not isinstance(digest, str) or len(digest) != 64:
                raise PilotProtocolError(f"invalid case input hash for {case_id!r}")
            try:
                int(digest, 16)
            except ValueError as exc:
                raise PilotProtocolError(f"invalid case input hash for {case_id!r}") from exc

        candidate = Path(output_root).absolute()
        root = Path(approved_root or candidate.parent).absolute()
        if "external_data" not in {part.casefold() for part in candidate.parts}:
            raise PilotProtocolError("pilot output must be under the git-ignored external_data root")
        try:
            self.output_root = ensure_safe_output_root(candidate, root)
        except UnsafeOutputPathError as exc:
            raise PilotProtocolError(str(exc)) from exc
        self.code_sha256 = code_sha256
        self.case_input_hashes = normalized_hashes
        self.client = client
        self._reserved_repeat_budget = 0.0

    @property
    def repeat_reserve_usd(self) -> float:
        return cfg.per_request_reserve_usd() * cfg.CALL_CAP_PER_REPEAT

    @property
    def reserved_budget_usd(self) -> float:
        """Full repeat reservations made before any fixture response is visible."""
        return self._reserved_repeat_budget

    def _validate_schedules(
        self, schedules: Mapping[str, Sequence[PilotRequest]]
    ) -> dict[str, tuple[PilotRequest, ...]]:
        if set(schedules) != set(cfg.RUN_IDS) or len(schedules) != cfg.REPEATS:
            raise PilotProtocolError("schedules must contain exactly the frozen repeat IDs")
        normalized: dict[str, tuple[PilotRequest, ...]] = {}
        for run_id in cfg.RUN_IDS:
            requests = tuple(schedules[run_id])
            for request in requests:
                if not isinstance(request, PilotRequest):
                    raise PilotProtocolError("pilot schedules must contain PilotRequest values")
                if request.run_id != run_id:
                    raise PilotProtocolError("request run_id differs from its schedule")
                if request.case_id not in self.case_input_hashes:
                    raise PilotProtocolError(f"unknown case_id in request: {request.case_id}")
            normalized[run_id] = requests
        return normalized

    def _binding(self, run_id: str) -> dict[str, Any]:
        return {
            "schema_version": "pilot-prospective-binding-v1",
            "evidence_class": "ENGINEERING_FIXTURE_ONLY",
            "study_class": cfg.STUDY_CLASS,
            "run_id": run_id,
            "created_before_results": True,
            "bound_at": _now(),
            "setting_id": cfg.SETTING_ID,
            "corpus_id": cfg.CORPUS_ID,
            "model": cfg.MODEL,
            "config_sha256": config_sha256(),
            "config": frozen_config(),
            "code_sha256": self.code_sha256,
            "case_input_hashes": self.case_input_hashes,
            "event_log_path": f"{run_id}/events.jsonl",
            "event_log_sha256": "PENDING_UNTIL_FINALIZATION",
            "lifecycle_summary": "PENDING_UNTIL_FINALIZATION",
            "repeat_reserve_usd": round(self.repeat_reserve_usd, 7),
            "global_reserved_budget_usd": round(cfg.global_bound().total_worst_case_usd, 6),
            "usage": {
                "calls": 0,
                "input_tokens": 0,
                "output_tokens": 0,
                "cost_usd": 0.0,
            },
            "provider_calls": 0,
            "external_calls": 0,
            "repeat_retry_count": 0,
        }

    def _reserve_repeat(self) -> bool:
        bound = cfg.global_bound()
        if not bound.fits:
            raise PilotProtocolError("frozen pilot budget bound does not fit")
        proposed = self._reserved_repeat_budget + self.repeat_reserve_usd
        if proposed > float(cfg.BUDGET_USD) + 1e-12:
            return False
        self._reserved_repeat_budget = proposed
        return True

    @staticmethod
    def _response_metadata(response: PilotResponse) -> tuple[bool, str | None]:
        if not isinstance(response, PilotResponse):
            return False, "RESPONSE_TYPE_INVALID"
        if not isinstance(response.finish_reason, str):
            return False, "FINISH_REASON_INVALID"
        if (
            isinstance(response.input_tokens, bool)
            or isinstance(response.output_tokens, bool)
            or not isinstance(response.input_tokens, int)
            or not isinstance(response.output_tokens, int)
            or response.input_tokens < 0
            or response.output_tokens < 0
        ):
            return False, "USAGE_INVALID"
        if response.output_tokens > cfg.MAX_OUTPUT_TOKENS:
            return False, "OUTPUT_TOKEN_CEILING_EXCEEDED"
        if (
            isinstance(response.cost_usd, bool)
            or not isinstance(response.cost_usd, (int, float))
            or not math.isfinite(float(response.cost_usd))
            or response.cost_usd < 0
            or float(response.cost_usd) > cfg.per_request_reserve_usd() + 1e-12
        ):
            return False, "COST_RESERVE_EXCEEDED"
        return True, None

    @staticmethod
    def _event(
        request: PilotRequest,
        response: PilotResponse | None,
        *,
        attempt: int,
        error_code: str | None = None,
    ) -> dict[str, Any]:
        payload_hash = _sha256(response.payload) if isinstance(response, PilotResponse) else None
        return {
            "run_id": request.run_id,
            "case_id": request.case_id,
            "label_sha256": _sha256(request.label),
            "attempt": attempt,
            "prompt_sha256": _sha256(
                {"system": request.system_prompt, "user": request.user_prompt}
            ),
            "response_sha256": payload_hash,
            "finish_reason": response.finish_reason if isinstance(response, PilotResponse) else None,
            "input_tokens": response.input_tokens if isinstance(response, PilotResponse) else None,
            "output_tokens": response.output_tokens if isinstance(response, PilotResponse) else None,
            "cost_usd": round(float(response.cost_usd), 8) if isinstance(response, PilotResponse) else None,
            "error_code": error_code,
        }

    async def _run_repeat(
        self, run_id: str, requests: Sequence[PilotRequest], binding_sha256: str
    ) -> dict[str, Any]:
        repeat_root = self.output_root / run_id
        events: list[dict[str, Any]] = []
        calls = successful_calls = retry_count = truncated_calls = 0
        input_tokens = output_tokens = 0
        cost_usd = 0.0
        status = "TECHNICAL_SUCCESS"
        failure_code: str | None = None
        started = _now()

        for request in requests:
            if calls >= cfg.CALL_CAP_PER_REPEAT:
                status = "STOPPED_AT_CALL_CAP"
                break
            request_succeeded = False
            for attempt in range(1, cfg.MAX_RETRIES_PER_CALL + 2):
                if calls >= cfg.CALL_CAP_PER_REPEAT:
                    status = "STOPPED_AT_CALL_CAP"
                    break
                calls += 1
                try:
                    response = await asyncio.wait_for(
                        self.client.complete(request), timeout=cfg.REQUEST_TIMEOUT_SECONDS
                    )
                except asyncio.TimeoutError:
                    error_code = "TIMEOUT"
                    events.append(self._event(request, None, attempt=attempt, error_code=error_code))
                    if attempt <= cfg.MAX_RETRIES_PER_CALL:
                        retry_count += 1
                        continue
                    failure_code = error_code
                    status = "TECHNICAL_FAILURE"
                    break
                except Exception as exc:  # noqa: BLE001 - sanitize to class only
                    error_code = type(exc).__name__.upper()
                    events.append(self._event(request, None, attempt=attempt, error_code=error_code))
                    if attempt <= cfg.MAX_RETRIES_PER_CALL:
                        retry_count += 1
                        continue
                    failure_code = error_code
                    status = "TECHNICAL_FAILURE"
                    break

                valid, error_code = self._response_metadata(response)
                if not valid:
                    events.append(self._event(request, response, attempt=attempt, error_code=error_code))
                    if error_code in {"USAGE_INVALID", "RESPONSE_TYPE_INVALID", "FINISH_REASON_INVALID"} and attempt <= cfg.MAX_RETRIES_PER_CALL:
                        retry_count += 1
                        continue
                    failure_code = error_code
                    status = "TECHNICAL_FAILURE"
                    break

                events.append(self._event(request, response, attempt=attempt))
                successful_calls += 1
                input_tokens += response.input_tokens
                output_tokens += response.output_tokens
                cost_usd += float(response.cost_usd)
                request_succeeded = True
                if response.finish_reason == cfg.TRUNCATED_FINISH_REASON:
                    truncated_calls += 1
                break

            if status in {"TECHNICAL_FAILURE", "STOPPED_AT_CALL_CAP"}:
                break
            if not request_succeeded:
                status = "TECHNICAL_FAILURE"
                failure_code = failure_code or "REQUEST_NOT_COMPLETED"
                break

        if truncated_calls:
            status = "TRUNCATION_AFFECTED"
        if status == "TECHNICAL_SUCCESS" and calls >= cfg.CALL_CAP_PER_REPEAT and len(events) < len(requests):
            status = "STOPPED_AT_CALL_CAP"

        event_bytes = "".join(json.dumps(event, sort_keys=True, ensure_ascii=False) + "\n" for event in events).encode("utf-8")
        event_path = repeat_root / "events.jsonl"
        try:
            with event_path.open("xb") as handle:
                handle.write(event_bytes)
        except FileExistsError as exc:
            raise PilotProtocolError(f"refusing to overwrite pilot event log: {run_id}") from exc
        event_log_sha256 = hashlib.sha256(event_bytes).hexdigest()
        eligible = status == "TECHNICAL_SUCCESS" and truncated_calls == 0 and failure_code is None
        lifecycle = {
            "complete": eligible,
            "termination_reason": status,
            "events": len(events),
            "failed_events": sum(event["error_code"] is not None for event in events),
        }
        receipt = {
            "schema_version": "pilot-repeat-receipt-v1",
            "evidence_class": "ENGINEERING_FIXTURE_ONLY",
            "study_class": cfg.STUDY_CLASS,
            "run_id": run_id,
            "setting_id": cfg.SETTING_ID,
            "corpus_id": cfg.CORPUS_ID,
            "model": cfg.MODEL,
            "config_sha256": config_sha256(),
            "code_sha256": self.code_sha256,
            "case_input_hashes": self.case_input_hashes,
            "prospective_binding_sha256": binding_sha256,
            "event_log_sha256": event_log_sha256,
            "lifecycle_summary": lifecycle,
            "status": status,
            "failure_code": failure_code,
            "calls": calls,
            "successful_calls": successful_calls,
            "retry_count": retry_count,
            "repeat_retry_count": 0,
            "truncated_calls": truncated_calls,
            "scientific_denominator_eligible": eligible,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "cost_usd": round(cost_usd, 8),
            "started_at": started,
            "completed_at": _now(),
            "provider_calls": 0,
            "external_calls": 0,
            "privacy_counters": {"raw_content_persisted": 0, "provider_calls": 0},
        }
        _write_exclusive_json(repeat_root / "run-receipt.json", receipt)
        return {
            "run_id": run_id,
            "status": status,
            "calls": calls,
            "successful_calls": successful_calls,
            "retry_count": retry_count,
            "repeat_retry_count": 0,
            "truncated_calls": truncated_calls,
            "scientific_denominator_eligible": eligible,
            "cost_usd": round(cost_usd, 8),
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "failure_code": failure_code,
            "event_log_sha256": event_log_sha256,
            "lifecycle_summary": lifecycle,
        }

    async def run(self, schedules: Mapping[str, Sequence[PilotRequest]]) -> dict[str, Any]:
        """Run the frozen schedule through an offline-only deterministic client."""

        schedules_normalized = self._validate_schedules(schedules)
        bound = cfg.assert_bound_fits()
        self.output_root.mkdir(parents=True, exist_ok=True)

        # Bind every repeat before the first response is observable.  This is
        # the prospective part of the protocol; final event hashes are added
        # only after each private event log has been closed.
        bindings: dict[str, str] = {}
        for run_id in cfg.RUN_IDS:
            if not self._reserve_repeat():
                raise PilotProtocolError("insufficient headroom for a complete repeat")
            binding = self._binding(run_id)
            binding_path = self.output_root / run_id / "prospective-binding.json"
            _write_exclusive_json(binding_path, binding)
            bindings[run_id] = hashlib.sha256(binding_path.read_bytes()).hexdigest()

        repeats: list[dict[str, Any]] = []
        for run_id in cfg.RUN_IDS:
            repeats.append(await self._run_repeat(run_id, schedules_normalized[run_id], bindings[run_id]))

        summary = {
            "schema_version": "pilot-run-summary-v1",
            "evidence_class": "ENGINEERING_FIXTURE_ONLY",
            "study_class": cfg.STUDY_CLASS,
            "status": "PREPARED_OFFLINE_ONLY",
            "setting_id": cfg.SETTING_ID,
            "corpus_id": cfg.CORPUS_ID,
            "config_sha256": config_sha256(),
            "bound": bound.as_dict(),
            "reserved_budget_usd": round(self.reserved_budget_usd, 6),
            "reservation_complete": math.isclose(
                self.reserved_budget_usd, bound.total_worst_case_usd, abs_tol=1e-12
            ),
            "repeats": repeats,
            "provider_calls": 0,
            "external_calls": 0,
            "scientific_results": "NOT_GENERATED",
            "note": (
                "Offline engineering fixture only. No provider adapter, network path or scientific "
                "denominator is provided by this controller. A future provider run requires a "
                "separate reviewed adapter and fresh authorization."
            ),
        }
        _write_exclusive_json(self.output_root / "pilot-summary.json", summary)
        return summary


__all__ = [
    "PilotExecutionController",
    "PilotProtocolError",
    "PilotRequest",
    "PilotResponse",
]
