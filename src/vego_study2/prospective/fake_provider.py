"""In-process SDK stub for the offline preflight of both conditions.

The stub stands in for ``AsyncOpenAI`` at the SDK boundary, so the protected
LLMClient, the metering wrapper, the guard and the ledger run unchanged.  Its
content is literal fixture text and is classified ENGINEERING-ONLY FIXTURE.
"""

from __future__ import annotations

import asyncio
import json
import re
from types import SimpleNamespace
from typing import Any

from . import constants as c
from .provider import CASE, LABEL

MODES = ("valid", "two_rounds", "transport_flaky", "invalid_json", "malformed_off", "secret", "model_drift", "missing_usage")

_QUESTION_MARKERS = ("Questions to be Answered: ** ", "Questions to be Answered:")
_CASE_RE = re.compile(r"^agent3/([^/]+)/")


class FakeSDKError(RuntimeError):
    pass


def _questions_from_system_prompt(system: str) -> list[dict[str, Any]]:
    for marker in _QUESTION_MARKERS:
        offset = system.find(marker)
        if offset >= 0:
            start = system.find("[", offset)
            questions, _ = json.JSONDecoder().raw_decode(system[start:])
            return questions
    raise FakeSDKError("dedicated question field absent from answer prompt")


def _off_payload(case_id: str) -> dict[str, Any]:
    return {
        "schema_version": c.CONDITION_OUTPUT_SCHEMA,
        "condition": c.CONDITION_OFF,
        "skill_version": "off-baseline-v1",
        "case_id": case_id,
        "existing_mapping": [
            {"guideline_id": "G1", "evidence": "fixture evidence", "compliance_status": "Satisfied", "notes": ""},
            {"guideline_id": "G2", "evidence": "fixture evidence", "compliance_status": "Not-Satisfied", "notes": "fixture"},
        ],
        "coverage_summary": {"satisfied": 1, "partially_satisfied": 0, "not_satisfied": 1},
        "uncovered_fragments": [
            {"fragment": "fixture fragment", "label": "Alternative", "severity": "Low", "reason": "fixture reason"}
        ],
    }


class FakeChatCompletions:
    def __init__(self, mode: str, *, flaky_failures: int = 1) -> None:
        if mode not in MODES:
            raise FakeSDKError(f"unsupported fixture mode {mode!r}")
        self.mode = mode
        self.flaky_failures = flaky_failures
        self.requests = 0
        self.answer_calls = 0

    def _payload(self, label: str | None, case_id: str | None, messages: list[dict[str, str]]) -> Any:
        system = messages[0]["content"]
        if label is None:
            raise FakeSDKError("request without a label context")
        if label.startswith("direct/"):
            cid = label.split("/", 1)[1]
            if self.mode == "malformed_off":
                return {"schema_version": c.CONDITION_OUTPUT_SCHEMA, "condition": c.CONDITION_OFF, "case_id": cid,
                        "skill_version": "off-baseline-v1", "existing_mapping": "not-an-array",
                        "coverage_summary": {}, "uncovered_fragments": []}
            payload = _off_payload(cid)
            if self.mode == "secret":
                payload["uncovered_fragments"][0]["reason"] = "sk-live-engineering-fixture-secret-value"
            return payload
        if label in {"agent1/answer_language_questions", "agent2/answer_domain_questions"}:
            questions = _questions_from_system_prompt(system)
            schedule = ("Medium", "Low")
            answers = []
            for q in questions:
                confidence = schedule[self.answer_calls] if self.answer_calls < len(schedule) else "High"
                self.answer_calls += 1
                answers.append({
                    "question_id": q["id"],
                    "answer": "Local fixture answer.",
                    "confidence": confidence,
                    "evidence": "Local fixture evidence.",
                })
            return {"questions_answers": answers}
        if label == "agent1/build_language_template":
            return {"language_name": c.LANGUAGE_NAME, "guidelines": [], "agent1_capabilities": []}
        if label == "agent4/identify_patterns":
            return {"deviation_patterns": []}
        match = _CASE_RE.match(label)
        cid = match.group(1) if match else (case_id or "")
        round_match = re.search(r"(?:_round|_r)(\d+)$", label)
        round_n = int(round_match.group(1)) if round_match else 1
        ask = self.mode == "two_rounds" and round_n == 1
        questions_lang = [{"question": "Local language fixture: " + label}] if ask else []
        questions_dom = [{"question": "Local domain fixture: " + label}] if ask and "feedback" not in label else []
        if label.endswith("/map"):
            return {
                "skill_version": "fixture-3-1",
                "case_id": cid,
                "existing_mapping": [
                    {"guideline_id": "G1", "evidence": "fixture evidence", "compliance_status": "Satisfied", "notes": ""},
                    {"guideline_id": "G2", "evidence": "fixture evidence", "compliance_status": "Partially-Satisfied", "notes": "fixture"},
                ],
                "coverage_summary": {"satisfied": 1, "partially_satisfied": 1, "not_satisfied": 0},
            }
        if "/resolve_r" in label:
            return {"skill_version": "fixture-3-2", "case_id": cid, "potential_found": [],
                    "questions_to_language_advisor": questions_lang, "questions_to_domain_advisor": questions_dom}
        if "/audit_r" in label:
            return {"skill_version": "fixture-3-3", "case_id": cid,
                    "uncovered_fragments": [
                        {"fragment": "fixture fragment", "label": "Alternative", "severity": "Low", "reason": "fixture reason"}
                    ],
                    "questions_to_language_advisor": questions_lang, "questions_to_domain_advisor": questions_dom}
        if label.startswith("agent2/guidelines"):
            return {"reference_guidelines": [{"guideline_id": "G1", "text": "fixture guideline"},
                                             {"guideline_id": "G2", "text": "fixture guideline"}],
                    "questions_to_language_advisor": questions_lang, "questions_to_domain_advisor": questions_dom}
        if label.startswith("agent4/classify"):
            return {"variability_classifications": [],
                    "questions_to_language_advisor": questions_lang, "questions_to_domain_advisor": questions_dom}
        raise FakeSDKError(f"unknown protected call label {label!r}")

    async def create(self, **kwargs: Any) -> Any:
        await asyncio.sleep(0)
        self.requests += 1
        if self.mode == "transport_flaky" and self.requests <= self.flaky_failures:
            import openai

            raise openai.APIConnectionError(request=SimpleNamespace(url="fixture://none"))
        label, case_id = LABEL.get(), CASE.get()
        messages = kwargs["messages"]
        payload = self._payload(label, case_id, messages)
        text = "{not valid JSON" if self.mode == "invalid_json" and (label or "").startswith("direct/") else json.dumps(payload)
        prompt_tokens = sum(len(m["content"]) for m in messages) // 4
        completion_tokens = max(1, len(text) // 4)
        usage = None if self.mode == "missing_usage" else SimpleNamespace(
            prompt_tokens=prompt_tokens, completion_tokens=completion_tokens,
            total_tokens=prompt_tokens + completion_tokens,
        )
        model = "gpt-4o-fixture-drift" if self.mode == "model_drift" else c.MODEL + "-fixture"
        return SimpleNamespace(
            choices=[SimpleNamespace(message=SimpleNamespace(content=text), finish_reason="stop")],
            usage=usage,
            model=model,
            system_fingerprint="fixture",
        )


class FakeSDK:
    """Object shape expected by :func:`vego_study2.prospective.provider.build_client`."""

    def __init__(self, mode: str = "valid", **kwargs: Any) -> None:
        self.completions = FakeChatCompletions(mode, **kwargs)
        self.chat = SimpleNamespace(completions=self.completions)
