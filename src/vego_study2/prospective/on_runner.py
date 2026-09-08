"""VEGO_AI_ON: the unmodified four-agent pipeline under the shared guard.

The protected orchestrator is executed exactly as in Study 1: its client and
registry are swapped for the observed, metered proxies at run time, nothing in
``VEGO-AI/framework`` is edited, and the Q&A stream is recorded by the same
observer.  Detector-v1 is applied afterwards to the recorded episodes as a
reporting-only label; it never writes a queue, alters an answer, or causes a
retry.
"""

from __future__ import annotations

import asyncio
import hashlib
import json
import logging
import re
import sys
import time
from collections import Counter
from collections.abc import Callable
from pathlib import Path
from typing import Any

from . import constants as c
from .budget import BudgetStop
from .contract import (
    ContractError,
    canonical_sha256,
    on_payload_from_pipeline,
    output_metrics,
    validate_condition_output,
)
from .provider import CASE, CONDITION, LABEL, ModelMismatch, contains_secret

ROOT = Path(__file__).resolve().parents[3]
_CASE_LABEL_RE = re.compile(r"^agent3/([^/]+)/")


def _paths_on_sys_path() -> None:
    for relative in ("scripts", "VEGO-AI/framework"):
        path = str(ROOT / relative)
        if path not in sys.path:
            sys.path.insert(0, path)


def detector_v1_sha256() -> str:
    return hashlib.sha256((ROOT / "scripts" / "extract_qa_escalation_features.py").read_bytes()).hexdigest()


def protected_runtime_sha256() -> dict[str, str]:
    names = (
        "orchestrator.py", "qa_registry.py", "state.py", "llm_client.py", "qa_communication.py",
        "agent1_language_advisor.py", "agent2_domain_advisor.py", "agent3_model_inspector.py",
        "agent4_variability_explorer.py",
    )
    return {name: hashlib.sha256((ROOT / "VEGO-AI" / "framework" / name).read_bytes()).hexdigest() for name in names}


def _load_partial_state(output_dir: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    vectors = output_dir / "compliance_vectors.json"
    fragments = output_dir / "uncovered_fragments.json"
    if vectors.is_file() and fragments.is_file():
        return (json.loads(vectors.read_text(encoding="utf-8")), json.loads(fragments.read_text(encoding="utf-8")))
    state_path = output_dir / "pipeline_state.json"
    if state_path.is_file():
        state = json.loads(state_path.read_text(encoding="utf-8"))
        if isinstance(state, dict):
            return (state.get("compliance_vectors") or {}, state.get("uncovered_fragments") or {})
    return ({}, {})


async def run_on(
    *,
    client_factory: Callable[[], Any],
    cases: list[dict[str, str]],
    domain_description: str,
    output_dir: Path,
    run_id: str,
    lifecycle: Callable[..., None],
    ledger_entries: Callable[[], list[dict[str, Any]]],
    run_timeout_seconds: int = c.ON_RUN_TIMEOUT_SECONDS,
    max_concurrent: int = c.MAX_CONCURRENT_CASES,
) -> dict[str, Any]:
    _paths_on_sys_path()
    import orchestrator
    from airtravel_local_observer import (
        CURRENT,
        Observer,
        Proxy,
        route_metrics,
        validate_final_stream,
    )
    from extract_qa_escalation_features import detect_detector_v1
    from qa_communication import QACommunicationRecorder, build_episode_projection
    from qa_registry import QARegistry

    output_dir.mkdir(parents=True, exist_ok=False)
    pipeline_dir = output_dir / "pipeline"
    pipeline_dir.mkdir()
    client = client_factory()
    recorder = QACommunicationRecorder(output_dir / "qa_events.jsonl", run_id=run_id)
    observer = Observer(recorder)
    started_cases: set[str] = set()

    class LabelledProxy(Proxy):
        async def call(self, prompt, *, label):
            match = _CASE_LABEL_RE.match(label)
            if match:
                case_id = match.group(1)
            else:
                meta = CURRENT.get()
                case_id = meta.get("case_id") if isinstance(meta, dict) else None
            tokens = (LABEL.set(label), CASE.set(case_id))
            if case_id and case_id not in started_cases:
                started_cases.add(case_id)
                lifecycle(stage="CASE", condition=c.CONDITION_ON, case_id=case_id, state="STARTED")
            try:
                return await super().call(prompt, label=label)
            finally:
                LABEL.reset(tokens[0])
                CASE.reset(tokens[1])

    proxy = LabelledProxy(client, observer, len(cases), c.SETTING_ID, run_id)
    cfg = {
        "setting_id": c.SETTING_ID,
        "corpus_id": c.CORPUS_ID,
        "language_name": c.LANGUAGE_NAME,
        "domain_description": domain_description,
        "case_models": [dict(case) for case in cases],
        "max_concurrent_cases": max_concurrent,
        "model": c.MODEL,
        "output_dir": str(pipeline_dir),
    }
    root_logger = logging.getLogger()
    previous_level = root_logger.level
    root_logger.setLevel(logging.INFO)
    original_client, original_registry = orchestrator.LLMClient, orchestrator.QARegistry
    orchestrator.LLMClient = lambda **_: proxy
    orchestrator.QARegistry = observer.registry(QARegistry)
    condition_token = CONDITION.set(c.CONDITION_ON)
    condition_started = time.perf_counter()
    status, exception = "COMPLETED", None
    try:
        await asyncio.wait_for(
            orchestrator.run_setting(cfg, pipeline_dir / "inline-config-not-written.json", None, c.SETTING_ID),
            run_timeout_seconds,
        )
    except BudgetStop as exc:
        status, exception = "STOPPED_AT_CAP", f"{type(exc).__name__}: {exc}"
    except asyncio.TimeoutError:
        status, exception = "RUN_TIMEOUT", "TimeoutError"
    except ModelMismatch as exc:
        status, exception = "TECHNICAL_FAILURE", f"MODEL_MISMATCH: {exc}"
    except Exception as exc:  # noqa: BLE001 - recorded verbatim (type only) in the receipt
        status, exception = "TECHNICAL_FAILURE", f"{type(exc).__name__}"
    finally:
        orchestrator.LLMClient, orchestrator.QARegistry = original_client, original_registry
        CONDITION.reset(condition_token)
        root_logger.setLevel(previous_level)
        recorder.close_open_episodes()
    elapsed = round(time.perf_counter() - condition_started, 3)

    events = recorder.events
    stream_valid = True
    if status == "COMPLETED":
        try:
            validate_final_stream(events)
        except Exception as exc:  # noqa: BLE001 - reported, not hidden
            stream_valid = False
            exception = f"EVENT_STREAM_INVALID: {type(exc).__name__}"
            status = "TECHNICAL_FAILURE"

    vectors, fragments = _load_partial_state(pipeline_dir)
    (output_dir / "cases").mkdir()
    rows: list[dict[str, Any]] = []
    ledger = ledger_entries()
    for case in cases:
        case_id = case["case_id"]
        row: dict[str, Any] = {
            "case_id": case_id,
            "condition": c.CONDITION_ON,
            "status": "NOT_PRODUCED",
            "failure_code": None,
            "output_sha256": None,
            "output_valid": False,
            "metrics": None,
        }
        if case_id in vectors or case_id in fragments:
            payload = on_payload_from_pipeline(case_id, vectors.get(case_id), fragments.get(case_id))
            if contains_secret(payload):
                row.update(status="TECHNICAL_FAILURE", failure_code="SECRET_DETECTED")
            else:
                try:
                    validate_condition_output(payload, condition=c.CONDITION_ON, case_id=case_id)
                except ContractError as exc:
                    row.update(status="SCHEMA_INVALID", failure_code="OUTPUT_SCHEMA_INVALID", failure_detail=str(exc)[:160])
                else:
                    target = output_dir / "cases" / f"{case_id}.json"
                    with target.open("xb") as handle:
                        handle.write(json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True).encode("utf-8"))
                    row.update(status="COMPLETED", output_sha256=canonical_sha256(payload), output_valid=True,
                               metrics=output_metrics(payload), skill_version_reported=payload["skill_version"])
        elif status != "COMPLETED":
            row.update(failure_code=status)
        case_ledger = [e for e in ledger if e.get("condition") == c.CONDITION_ON and e.get("case_id") == case_id]
        row["requests"] = len(case_ledger)
        row["prompt_tokens"] = sum(e.get("prompt_tokens") or 0 for e in case_ledger)
        row["completion_tokens"] = sum(e.get("completion_tokens") or 0 for e in case_ledger)
        row["cost_usd"] = round(sum(e.get("cost_usd") or 0.0 for e in case_ledger), 6)
        stamps = sorted(e["timestamp"] for e in case_ledger)
        row["first_request_at"] = stamps[0] if stamps else None
        row["last_request_at"] = stamps[-1] if stamps else None
        row["label_counts"] = dict(Counter(e.get("label", "").split("/")[0] for e in case_ledger))
        lifecycle(stage="CASE", condition=c.CONDITION_ON, case_id=case_id, state=row["status"], detail=row.get("failure_code"))
        rows.append(row)

    episodes = build_episode_projection(events) if stream_valid else []
    case_by_episode: dict[str, str | None] = {}
    for event in events:
        if event["event_type"] == "QUESTION_EMITTED":
            case_by_episode.setdefault(event["episode_id"], event.get("case_id"))
    detector = []
    for episode in episodes:
        result = detect_detector_v1(episode)
        result["case_id"] = case_by_episode.get(episode["episode_id"]) or "SETTING_LEVEL"
        result["source_target_pairs"] = [list(pair) for pair in episode["source_target_pairs"]]
        result["round_count"] = episode["round_count"]
        result["question_count"] = episode["question_count"]
        result["answer_count"] = episode["answer_count"]
        result["termination_reason"] = episode["termination_reason"]
        detector.append(result)
    for row in rows:
        mine = [d for d in detector if d["case_id"] == row["case_id"]]
        row["episodes"] = len(mine)
        row["questions"] = sum(d["question_count"] for d in mine)
        row["answers"] = sum(d["answer_count"] for d in mine)
        row["detector_v1"] = (
            dict(Counter(d["classification"] for d in mine)) if mine else {"NO_EPISODE": 1}
        )
    setting_ledger = [e for e in ledger if e.get("condition") == c.CONDITION_ON and e.get("case_id") is None]
    event_log = output_dir / "qa_events.jsonl"
    return {
        "condition": c.CONDITION_ON,
        "status": status,
        "technical_exception": exception,
        "workflow": "four role-scoped agents, bounded inter-agent Q&A, MAX_QA_ROUNDS as shipped",
        "agent_decomposition": True,
        "inter_agent_qa": True,
        "detector_v1": "APPLICABLE",
        "detector_v1_role": "reporting-only label on recorded episodes; no queue, no answer change, no retry",
        "cases": rows,
        "planned_cases": len(cases),
        "completed_cases": sum(1 for r in rows if r["status"] == "COMPLETED"),
        "elapsed_seconds": elapsed,
        "setting_level_requests": len(setting_ledger),
        "setting_level_prompt_tokens": sum(e.get("prompt_tokens") or 0 for e in setting_ledger),
        "setting_level_completion_tokens": sum(e.get("completion_tokens") or 0 for e in setting_ledger),
        "setting_level_cost_usd": round(sum(e.get("cost_usd") or 0.0 for e in setting_ledger), 6),
        "setting_level_label_counts": dict(Counter(e.get("label", "") for e in setting_ledger)),
        "event_log_sha256": hashlib.sha256(event_log.read_bytes()).hexdigest() if event_log.is_file() else None,
        "event_count": len(events),
        "event_stream_valid": stream_valid,
        "episodes": detector,
        "episode_summary": {
            "episodes": len(episodes),
            "scientific_complete": sum(1 for e in episodes if e["scientific_complete"]),
            "questions": sum(e["question_count"] for e in episodes),
            "answers": sum(e["answer_count"] for e in episodes),
            "termination_reasons": dict(Counter(e["termination_reason"] for e in episodes)),
            "detector_v1_classifications": dict(Counter(d["classification"] for d in detector)),
            "detector_v1_reason_codes": dict(Counter(code for d in detector for code in d["all_signals_fired"])),
        },
        "routes": route_metrics(events),
        "protected_runtime_sha256": protected_runtime_sha256(),
        "detector_v1_sha256": detector_v1_sha256(),
    }
