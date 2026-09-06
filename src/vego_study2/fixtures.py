from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class FixtureResponse:
    payload: Any
    input_tokens: int = 32
    output_tokens: int = 48
    cost_usd: float = 0.001


def fixture_cases(config: dict[str, Any]) -> list[dict[str, Any]]:
    """Return non-scientific in-memory cases for tests only.

    The text is deliberately generic and is never written to tracked output.
    Real corpus bytes must be supplied separately after a human-approved
    evidence binding; this helper cannot stand in for them.
    """
    return [
        {
            "case_id": case_id,
            "case_model": f"ENGINEERING_FIXTURE_ONLY case {case_id}",
            "fixture_only": True,
        }
        for case_id in config["case_ids"]
    ]


class DeterministicFixtureClient:
    """Offline client used by tests; it has no provider or network path."""

    def __init__(
        self,
        mode: str = "valid",
        *,
        fail_first_attempts: int = 0,
        delay_seconds: float = 0.0,
        cost_usd: float = 0.001,
    ) -> None:
        self.mode = mode
        self.fail_first_attempts = fail_first_attempts
        self.delay_seconds = delay_seconds
        self.cost_usd = cost_usd
        self.calls: list[dict[str, Any]] = []
        self._attempts = 0
        self._attempts_by_case: dict[str, int] = {}

    async def complete(self, request: Any) -> FixtureResponse:
        self._attempts += 1
        case_attempt = self._attempts_by_case.get(request.case_id, 0) + 1
        self._attempts_by_case[request.case_id] = case_attempt
        self.calls.append(
            {
                "case_id": request.case_id,
                "condition": request.condition,
                "label": request.label,
                "model_id": request.model_id,
                "temperature": request.temperature,
                "max_output_tokens": request.max_output_tokens,
            }
        )
        if self.delay_seconds:
            await asyncio.sleep(self.delay_seconds)
        if case_attempt <= self.fail_first_attempts:
            raise RuntimeError("fixture transient failure")
        if self.mode == "timeout":
            raise asyncio.TimeoutError("fixture timeout")
        if self.mode == "malformed":
            return FixtureResponse({"case_id": request.case_id, "existing_mapping": "not-an-array"}, cost_usd=self.cost_usd)
        if self.mode == "invalid_json":
            return FixtureResponse("{not valid JSON", cost_usd=self.cost_usd)
        if self.mode == "secret":
            payload = _valid_payload(request.case_id, request.condition)
            payload["uncovered_fragments"][0]["reason"] = "sk-live-engineering-fixture-secret"
            return FixtureResponse(payload, cost_usd=self.cost_usd)
        return FixtureResponse(_valid_payload(request.case_id, request.condition), cost_usd=self.cost_usd)


def _valid_payload(case_id: str, condition: str) -> dict[str, Any]:
    return {
        "schema_version": "study2-condition-output-v1",
        "condition": condition,
        "skill_version": "study2-fixture-v1",
        "case_id": case_id,
        "existing_mapping": [
            {
                "guideline_id": "G1",
                "evidence": "fixture evidence",
                "compliance_status": "Satisfied",
                "notes": "",
            }
        ],
        "coverage_summary": {"satisfied": 1, "partially_satisfied": 0, "not_satisfied": 0},
        "uncovered_fragments": [
            {
                "fragment": "fixture fragment",
                "label": "Alternative",
                "severity": "Low",
                "reason": "fixture reason",
            }
        ],
    }
