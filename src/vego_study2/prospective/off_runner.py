"""VEGO_AI_OFF: one direct per-case call through the same protected client.

This module must never import agent orchestration, inter-agent Q&A,
Detector-v1, or Agent-4 queue construction.  It fails closed if any such
module is already loaded when the condition starts or has appeared by the
time it ends.  OFF is not "no AI": it is the identical model, input case,
domain material, output schema, output ceiling and request policy, minus the
multi-agent decomposition, the Q&A protocol and the round loop.
"""

from __future__ import annotations

import asyncio
import json
import sys
import time
from collections.abc import Callable
from pathlib import Path
from typing import Any

from . import constants as c
from .budget import BudgetStop
from .contract import ContractError, canonical_sha256, output_metrics, validate_condition_output
from .provider import CASE, CONDITION, LABEL, ModelMismatch, contains_secret, utc_now

ROOT = Path(__file__).resolve().parents[3]


class OffIsolationError(RuntimeError):
    """Raised when the OFF condition would share a process with ON machinery."""


def assert_off_isolation(stage: str) -> None:
    loaded = sorted(name for name in c.OFF_FORBIDDEN_MODULES if name in sys.modules)
    if loaded:
        raise OffIsolationError(f"OFF isolation violated at {stage}: {loaded}")


def _scripts_on_path() -> None:
    scripts = str(ROOT / "scripts")
    if scripts not in sys.path:
        sys.path.insert(0, scripts)


def off_prompt_template_sha256() -> str:
    _scripts_on_path()
    from study2_vego_off_baseline import OFF_SYSTEM_PROMPT, SKILL_VERSION

    return canonical_sha256({"system_template": OFF_SYSTEM_PROMPT, "skill_version": SKILL_VERSION})


async def run_off(
    *,
    client_factory: Callable[[], Any],
    cases: list[dict[str, str]],
    domain_description: str,
    output_dir: Path,
    lifecycle: Callable[..., None],
    run_timeout_seconds: int = c.OFF_RUN_TIMEOUT_SECONDS,
    max_concurrent: int = c.MAX_CONCURRENT_CASES,
) -> dict[str, Any]:
    assert_off_isolation("start")
    _scripts_on_path()
    from study2_vego_off_baseline import SKILL_VERSION, OutputSchemaError, normalise, off_prompt

    output_dir.mkdir(parents=True, exist_ok=False)
    (output_dir / "cases").mkdir()
    client = client_factory()
    semaphore = asyncio.Semaphore(max_concurrent)
    rows: list[dict[str, Any]] = []
    condition_started = time.perf_counter()

    async def one_case(case: dict[str, str]) -> dict[str, Any]:
        case_id = case["case_id"]
        prompt = off_prompt(case_id, case["case_model"], domain_description, c.LANGUAGE_NAME)
        row: dict[str, Any] = {
            "case_id": case_id,
            "condition": c.CONDITION_OFF,
            "prompt_sha256": canonical_sha256(prompt),
            "started_at": None,
            "completed_at": None,
            "elapsed_seconds": None,
            "status": "PLANNED",
            "failure_code": None,
            "output_sha256": None,
            "output_valid": False,
            "metrics": None,
        }
        async with semaphore:
            tokens = (CONDITION.set(c.CONDITION_OFF), CASE.set(case_id), LABEL.set(f"direct/{case_id}"))
            lifecycle(stage="CASE", condition=c.CONDITION_OFF, case_id=case_id, state="STARTED")
            row["started_at"] = utc_now()
            started = time.perf_counter()
            try:
                parsed = await client.call(prompt, label=f"direct/{case_id}", max_tokens=c.MAX_OUTPUT_TOKENS)
            except BudgetStop as exc:
                row.update(status="STOPPED_AT_CAP", failure_code=str(exc).split(":", 1)[0])
            except ModelMismatch:
                row.update(status="TECHNICAL_FAILURE", failure_code="MODEL_MISMATCH")
            except ValueError as exc:
                row.update(status="TECHNICAL_FAILURE", failure_code="OUTPUT_PARSE_FAILURE",
                           failure_detail=type(exc).__name__)
            except Exception as exc:  # noqa: BLE001 - recorded, never retried here
                row.update(status="TECHNICAL_FAILURE", failure_code="PROVIDER_FAILURE",
                           failure_detail=type(exc).__name__)
            else:
                if contains_secret(parsed):
                    row.update(status="TECHNICAL_FAILURE", failure_code="SECRET_DETECTED")
                else:
                    try:
                        normalised = normalise(case_id, parsed)
                        payload = {
                            "schema_version": c.CONDITION_OUTPUT_SCHEMA,
                            "condition": c.CONDITION_OFF,
                            "skill_version": normalised["skill_version"],
                            "case_id": case_id,
                            "existing_mapping": normalised["existing_mapping"],
                            "coverage_summary": normalised["coverage_summary"],
                            "uncovered_fragments": normalised["uncovered_fragments"],
                        }
                        validate_condition_output(payload, condition=c.CONDITION_OFF, case_id=case_id)
                    except (OutputSchemaError, ContractError) as exc:
                        row.update(status="SCHEMA_INVALID", failure_code="OUTPUT_SCHEMA_INVALID",
                                   failure_detail=str(exc)[:160])
                        (output_dir / "cases" / f"{case_id}.invalid.json").write_text(
                            json.dumps(parsed, indent=2, ensure_ascii=False, sort_keys=True), encoding="utf-8"
                        )
                    else:
                        target = output_dir / "cases" / f"{case_id}.json"
                        with target.open("xb") as handle:
                            handle.write(json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True).encode("utf-8"))
                        row.update(status="COMPLETED", output_sha256=canonical_sha256(payload),
                                   output_valid=True, metrics=output_metrics(payload),
                                   skill_version_reported=payload["skill_version"],
                                   skill_version_expected=SKILL_VERSION)
            finally:
                row["elapsed_seconds"] = round(time.perf_counter() - started, 3)
                row["completed_at"] = utc_now()
                for var, token in zip((CONDITION, CASE, LABEL), tokens, strict=True):
                    var.reset(token)
            lifecycle(stage="CASE", condition=c.CONDITION_OFF, case_id=case_id, state=row["status"],
                      detail=row.get("failure_code"))
        return row

    status = "COMPLETED"
    try:
        rows = list(await asyncio.wait_for(asyncio.gather(*(one_case(case) for case in cases)), run_timeout_seconds))
    except asyncio.TimeoutError:
        status = "RUN_TIMEOUT"
    rows.sort(key=lambda r: r["case_id"])
    assert_off_isolation("end")
    completed = sum(1 for r in rows if r["status"] == "COMPLETED")
    if status == "COMPLETED" and completed != len(cases):
        status = "COMPLETED_WITH_FAILURES"
    return {
        "condition": c.CONDITION_OFF,
        "status": status,
        "workflow": "one direct per-case call; no agents, no Q&A, no round loop",
        "agent_decomposition": False,
        "inter_agent_qa": False,
        "detector_v1": "NOT_APPLICABLE",
        "detector_v1_note": "no inter-agent episodes exist under OFF; the denominator is undefined, not zero",
        "cases": rows,
        "planned_cases": len(cases),
        "completed_cases": completed,
        "elapsed_seconds": round(time.perf_counter() - condition_started, 3),
        "isolation": {"forbidden_modules": list(c.OFF_FORBIDDEN_MODULES), "verified_at": ["start", "end"]},
    }
