"""Parser-level support for the VEGO_AI_OFF output contract.

The baseline pursues the same per-case objective as the orchestrated pipeline —
map reference guidelines onto a candidate model and audit what the model covers
that the guidelines do not — using one direct model call per case.

What is deliberately absent, and nothing else:
  * no agent decomposition (no agent1/2/3/4 roles),
  * no inter-agent question-and-answer protocol,
  * no round loop and no MAX_QA_ROUNDS.

The canonical controlled execution path is :class:`vego_study2.runner.Study2Runner`,
which enforces the frozen model, token, retry, timeout, concurrency, cost, call,
privacy and egress policy at each call site.  This low-level helper is retained
for strict parser/fixture tests and must not be used as a paid-run harness.

Because the baseline emits no inter-agent episodes, Detector-v1 has no unit of
analysis here. Its denominator is NOT_APPLICABLE, never zero.
"""

from __future__ import annotations

import asyncio
import json
from pathlib import Path
from typing import Any

import jsonschema

SKILL_VERSION = "off-baseline-v1"
ROOT = Path(__file__).resolve().parents[1]
OUTPUT_SCHEMA_PATH = ROOT / "schemas" / "study2-condition-output-v1.schema.json"
OUTPUT_SCHEMA = json.loads(OUTPUT_SCHEMA_PATH.read_text(encoding="utf-8"))


class OutputSchemaError(ValueError):
    """Raised when a condition response cannot enter the shared comparison."""

OFF_SYSTEM_PROMPT = """You are evaluating one candidate model against a domain description.

Perform BOTH tasks in a single response, without asking any questions:

TASK A - map the reference guidelines onto the candidate model. For each
guideline, state whether the candidate model satisfies it, and cite the evidence
in your own words.

TASK B - audit fragments present in the candidate model that the reference
guidelines do not cover. Categorise each uncovered fragment.

RULES:
- Return only the JSON block below. No prose, explanation or markdown wrapping.
- compliance_status must be one of: Satisfied | Partially-Satisfied | Not-Satisfied
- label must be one of: Alternative | Domain Mistake | Language Mistake
- severity must be one of: High | Medium | Low | N/A
- Do not ask clarifying questions. Resolve ambiguity yourself and proceed.

OUTPUT FORMAT:
{
  "schema_version": "study2-condition-output-v1",
  "condition": "VEGO_AI_OFF",
  "skill_version": "%(skill_version)s",
  "case_id": "%(case_id)s",
  "existing_mapping": [
    {
      "guideline_id": "Gj",
      "evidence": "<description of the match in your own words>",
      "compliance_status": "Satisfied | Partially-Satisfied | Not-Satisfied",
      "notes": "<explanation of partial satisfaction, or empty string>"
    }
  ],
  "coverage_summary": {"satisfied": 0, "partially_satisfied": 0, "not_satisfied": 0},
  "uncovered_fragments": [
    {
      "fragment": "<description in your own words>",
      "label": "Alternative | Domain Mistake | Language Mistake",
      "severity": "High | Medium | Low | N/A",
      "reason": "<brief justification>"
    }
  ]
}
"""


def off_prompt(case_id: str, case_model: str, domain_description: str, language_name: str) -> dict[str, str]:
    """Build the single-call baseline prompt for one case."""
    system = OFF_SYSTEM_PROMPT % {"skill_version": SKILL_VERSION, "case_id": case_id}
    user = (
        f"Language: {language_name}\n\n"
        f"Domain description:\n{domain_description}\n\n"
        f"Candidate model for case {case_id}:\n{case_model}\n\n"
        "Return the JSON block only."
    )
    return {"system": system, "user": user}


def normalise(case_id: str, payload: Any) -> dict[str, Any]:
    """Validate a response strictly; malformed output must stop the condition."""
    if not isinstance(payload, dict):
        raise OutputSchemaError("condition response must be a JSON object")
    try:
        jsonschema.Draft202012Validator(OUTPUT_SCHEMA).validate(payload)
    except jsonschema.ValidationError as exc:
        raise OutputSchemaError(f"condition response schema invalid: {exc.message}") from exc
    if payload["case_id"] != case_id:
        raise OutputSchemaError("condition response case_id differs from requested case")
    if payload["condition"] != "VEGO_AI_OFF":
        raise OutputSchemaError("OFF baseline received a non-OFF condition response")
    return {
        "case_id": case_id,
        "condition": payload["condition"],
        "skill_version": payload["skill_version"],
        "existing_mapping": payload["existing_mapping"],
        "uncovered_fragments": payload["uncovered_fragments"],
        "coverage_summary": payload["coverage_summary"],
        "schema_complete": True,
    }


async def run_off_baseline(
    client: Any,
    cases: list[dict[str, str]],
    domain_description: str,
    language_name: str,
    max_concurrent: int = 2,
) -> dict[str, Any]:
    """Run one direct call per case with the ON condition's concurrency limit."""
    case_ids = [case.get("case_id") for case in cases]
    if (
        any(not isinstance(case_id, str) or not case_id for case_id in case_ids)
        or len(case_ids) != len(set(case_ids))
    ):
        raise OutputSchemaError("OFF baseline case identifiers must be unique and non-empty")
    if not isinstance(domain_description, str) or not isinstance(language_name, str):
        raise OutputSchemaError("OFF baseline context must be text")
    semaphore = asyncio.Semaphore(max_concurrent)
    calls: list[dict[str, Any]] = []

    async def one(case: dict[str, str]) -> dict[str, Any]:
        case_id = case["case_id"]
        prompt = off_prompt(case_id, case["case_model"], domain_description, language_name)
        label = f"off_baseline/{case_id}/evaluate"
        call_record = {
            "case_id": case_id,
            "label": label,
            "prompt_sha256": prompt_digest(prompt),
        }
        calls.append(call_record)
        async with semaphore:
            response = await client.call(prompt, label=label)
        return normalise(case_id, response)

    results = await asyncio.gather(*[one(case) for case in cases])
    by_case = {row["case_id"]: row for row in results}
    return {
        "condition": "VEGO_AI_OFF",
        "skill_version": SKILL_VERSION,
        "cases": by_case,
        "calls": len(calls),
        "calls_per_case": 1,
        "agent_decomposition": False,
        "inter_agent_qa": False,
        "episodes": 0,
        "detector_v1_denominator": "NOT_APPLICABLE",
        "detector_v1_note": (
            "The baseline emits no inter-agent episodes, so Detector-v1 has no unit of "
            "analysis. This is not a zero-alert observation."
        ),
        "prompt_sha_by_case": {
            call["case_id"]: call["prompt_sha256"] for call in calls
        },
        "prompt_sha_by_call": sorted(calls, key=lambda call: call["case_id"]),
    }


def prompt_digest(prompt: dict[str, str]) -> str:
    import hashlib

    return hashlib.sha256(
        json.dumps(prompt, sort_keys=True, ensure_ascii=False).encode("utf-8")
    ).hexdigest()
