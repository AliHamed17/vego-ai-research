"""VEGO_AI_OFF: a defined non-VEGO baseline for the same output objective.

The baseline pursues the same per-case objective as the orchestrated pipeline —
map reference guidelines onto a candidate model and audit what the model covers
that the guidelines do not — using one direct model call per case.

What is deliberately absent, and nothing else:
  * no agent decomposition (no agent1/2/3/4 roles),
  * no inter-agent question-and-answer protocol,
  * no round loop and no MAX_QA_ROUNDS.

Everything else is held identical to the ON condition: same corpus, same case
identifiers, same model, same token policy, same retry policy, same timeout,
same concurrency, same output schema, same private output root.

Because the baseline emits no inter-agent episodes, Detector-v1 has no unit of
analysis here. Its denominator is NOT_APPLICABLE, never zero.
"""

from __future__ import annotations

import asyncio
import json
from typing import Any

SKILL_VERSION = "off-baseline-v1"

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
    """Coerce a baseline response into the shared comparison shape."""
    payload = payload if isinstance(payload, dict) else {}
    mapping = payload.get("existing_mapping")
    fragments = payload.get("uncovered_fragments")
    summary = payload.get("coverage_summary")
    return {
        "case_id": case_id,
        "existing_mapping": mapping if isinstance(mapping, list) else [],
        "uncovered_fragments": fragments if isinstance(fragments, list) else [],
        "coverage_summary": summary if isinstance(summary, dict) else {},
        "schema_complete": isinstance(mapping, list) and isinstance(fragments, list),
    }


async def run_off_baseline(
    client: Any,
    cases: list[dict[str, str]],
    domain_description: str,
    language_name: str,
    max_concurrent: int = 2,
) -> dict[str, Any]:
    """Run one direct call per case with the ON condition's concurrency limit."""
    semaphore = asyncio.Semaphore(max_concurrent)
    calls: list[dict[str, Any]] = []

    async def one(case: dict[str, str]) -> dict[str, Any]:
        case_id = case["case_id"]
        prompt = off_prompt(case_id, case["case_model"], domain_description, language_name)
        async with semaphore:
            response = await client.call(prompt, label=f"off_baseline/{case_id}/evaluate")
        calls.append({"case_id": case_id, "label": f"off_baseline/{case_id}/evaluate"})
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
            case["case_id"]: prompt_digest(
                off_prompt(case["case_id"], case["case_model"], domain_description, language_name)
            )
            for case in cases
        },
    }


def prompt_digest(prompt: dict[str, str]) -> str:
    import hashlib

    return hashlib.sha256(
        json.dumps(prompt, sort_keys=True, ensure_ascii=False).encode("utf-8")
    ).hexdigest()
