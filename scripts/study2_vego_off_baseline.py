"""Strict direct-per-case baseline helpers for Study 2.

The implementation deliberately raises on malformed output.  An invalid
response is a technical failure, never an empty successful baseline result.
"""

from __future__ import annotations

import asyncio
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from vego_study2.runner import CallRequest, validate_case_output  # noqa: E402

OFF_SYSTEM_PROMPT = (
    "STUDY2_OFF_DIRECT_V1: evaluate one case against the frozen guideline objective; "
    "return the shared JSON output contract and do not ask inter-agent questions."
)


class BaselineOutputValidationError(ValueError):
    """Raised when a direct baseline response is malformed."""


def off_prompt(case_id: str, case_model: str, domain_description: str, language_name: str) -> dict[str, str]:
    return {
        "system": OFF_SYSTEM_PROMPT,
        "user": (
            f"Language: {language_name}\n\nDomain description:\n{domain_description}\n\n"
            f"Candidate model for case {case_id}:\n{case_model}\n\nReturn JSON only."
        ),
    }


def prompt_digest(prompt: dict[str, str]) -> str:
    return hashlib.sha256(
        (json.dumps(prompt, sort_keys=True, ensure_ascii=False, separators=(",", ":")) + "\n").encode()
    ).hexdigest()


def normalise(case_id: str, payload: Any) -> dict[str, Any]:
    valid, reason = validate_case_output(case_id, payload)
    if not valid:
        raise BaselineOutputValidationError(reason or "OUTPUT_SCHEMA_INVALID")
    return payload


async def run_off_baseline(
    client: Any,
    cases: list[dict[str, str]],
    domain_description: str,
    language_name: str,
    max_concurrent: int = 2,
    *,
    model_id: str = "TO_BE_FROZEN_BEFORE_FIRST_CALL",
    timeout_seconds: float = 180.0,
    retries: int = 1,
) -> dict[str, Any]:
    if max_concurrent < 1 or retries < 0:
        raise ValueError("concurrency and retries must be non-negative/positive")
    semaphore = asyncio.Semaphore(max_concurrent)
    results: dict[str, dict[str, Any]] = {}
    prompt_hashes: dict[str, str] = {}
    attempts = 0

    async def one(case: dict[str, str]) -> None:
        nonlocal attempts
        case_id = case["case_id"]
        prompt = off_prompt(case_id, case["case_model"], domain_description, language_name)
        prompt_hashes[case_id] = prompt_digest(prompt)
        request = CallRequest(
            condition="VEGO_AI_OFF",
            case_id=case_id,
            label=f"off_baseline/{case_id}/evaluate",
            system_prompt=prompt["system"],
            user_prompt=prompt["user"],
            model_id=model_id,
            temperature=0.0,
            max_output_tokens=2048,
            timeout_seconds=timeout_seconds,
        )
        async with semaphore:
            for _attempt in range(retries + 1):
                attempts += 1
                try:
                    response = await asyncio.wait_for(client.complete(request), timeout=timeout_seconds)
                    results[case_id] = normalise(case_id, getattr(response, "payload", response))
                    return
                except asyncio.TimeoutError:
                    reason = "TIMEOUT"
                except BaselineOutputValidationError:
                    raise
                except Exception as exc:  # noqa: BLE001 - fixture boundary reports a type only
                    reason = type(exc).__name__.upper()
            raise BaselineOutputValidationError(reason)

    await asyncio.gather(*(one(case) for case in cases))
    return {
        "condition": "VEGO_AI_OFF",
        "cases": results,
        "calls": attempts,
        "episodes": 0,
        "detector_v1_denominator": "NOT_APPLICABLE",
        "prompt_sha_by_case": prompt_hashes,
    }
