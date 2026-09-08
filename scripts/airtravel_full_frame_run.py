"""One authorized provider-backed AirTravel run over the complete eligible case frame.

This is a NEW run, not a replication of the accepted Study 1 run and not poolable with it: the
case count differs (21 rather than 4), so the run configuration differs and each run keeps its
own denominator. Every other frozen parameter — model, output ceiling, input reserve, QA round
limit, concurrency, request timeout, egress restriction and Detector-v1 itself — is unchanged.

Budget, egress and credential handling are imported verbatim from ``airtravel_real_run`` rather
than reimplemented, so the guarantees the accepted run relied on are the same objects here.

Three provenance gaps recorded in the Study 1 close-out are closed by construction:

  * the receipt binds its own event-log digest, lifecycle summary and execution-code SHA;
  * ``MAX_QA_ROUNDS`` is recorded in the receipt rather than left as a harness constant;
  * a privacy-safe per-call ledger makes ``outbound_requests`` independently recomputable
    instead of receipt-asserted.

The ledger records token counts, finish reasons, latency and cost only. No prompt, no response,
no message content and no credential value is written to it.
"""

from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
import os
import subprocess
import sys
import time
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "VEGO-AI/framework"))

import airtravel_real_run as base  # noqa: E402  - frozen budget/egress/credential machinery
from study1_call_bound import MAX_QA_ROUNDS  # noqa: E402

SETTING_ID = base.SETTING_ID
CORPUS_ID = base.CORPUS_ID
MODEL = base.MODEL
RESERVE_INPUT_TOKENS = base.RESERVE_INPUT_TOKENS
RESERVE_OUTPUT_TOKENS = base.RESERVE_OUTPUT_TOKENS
REQUEST_TIMEOUT_SECONDS = base.REQUEST_TIMEOUT_SECONDS
MAX_CONCURRENT_CASES = base.MAX_CONCURRENT_CASES
PRICE_IN_PER_M = base.PRICE_IN_PER_M
PRICE_OUT_PER_M = base.PRICE_OUT_PER_M

RUN_TIMEOUT_SECONDS = 10_800
DEFAULT_BUDGET_USD = 5.00
DEFAULT_MAX_REQUESTS = 230
CONTRACT_NAME = "full-frame-contract.json"
HARNESS_PATHS = ("scripts/airtravel_full_frame_run.py", "scripts/airtravel_real_run.py")


class CallLedger:
    """Privacy-safe per-call record: counts, finish reasons, latency and cost only."""

    def __init__(self) -> None:
        self.rows: list[dict[str, Any]] = []

    def record(self, index: int, response: Any, started: float) -> None:
        usage = getattr(response, "usage", None)
        prompt = int(getattr(usage, "prompt_tokens", 0) or 0)
        completion = int(getattr(usage, "completion_tokens", 0) or 0)
        choices = getattr(response, "choices", None) or []
        finish = getattr(choices[0], "finish_reason", None) if choices else None
        self.rows.append(
            {
                "index": index,
                "prompt_tokens": prompt,
                "completion_tokens": completion,
                "finish_reason": finish,
                "truncated": finish == "length",
                "latency_seconds": round(time.monotonic() - started, 3),
                "cost_usd": round(
                    (prompt * PRICE_IN_PER_M + completion * PRICE_OUT_PER_M) / 1_000_000, 8
                ),
                "model_reported": getattr(response, "model", None),
            }
        )

    def summary(self) -> dict[str, Any]:
        completions = [row["completion_tokens"] for row in self.rows]
        return {
            "ledger_rows": len(self.rows),
            "truncated_calls": sum(1 for row in self.rows if row["truncated"]),
            "finish_reasons": dict(Counter(row["finish_reason"] for row in self.rows)),
            "max_completion_tokens_observed": max(completions, default=0),
            "mean_completion_tokens_observed": (
                round(sum(completions) / len(completions), 1) if completions else 0
            ),
            "recomputed_cost_usd": round(sum(row["cost_usd"] for row in self.rows), 6),
            "distinct_models_reported": sorted(
                {row["model_reported"] for row in self.rows if row["model_reported"]}
            ),
        }


def load_frame(runtime_root: Path) -> dict[str, Any]:
    """Load the frame only if every file still matches its pinned digest."""
    contract = json.loads((runtime_root / CONTRACT_NAME).read_text(encoding="utf-8"))
    for relative, pin in contract["runtime_files"].items():
        target = runtime_root / relative
        if not target.is_file():
            raise ValueError(f"runtime file absent: {relative}")
        if hashlib.sha256(target.read_bytes()).hexdigest() != pin["sha256"]:
            raise ValueError(f"runtime file digest mismatch: {relative}")
    cases = [
        {
            "case_id": relative.split("/", 1)[1].split("_", 1)[0],
            "case_model": (runtime_root / relative).read_text(encoding="utf-8"),
        }
        for relative in sorted(contract["runtime_files"])
        if relative.startswith("candidate_models/")
    ]
    if len(cases) != int(contract["case_count"]):
        raise ValueError("case count does not match the pinned contract")
    return {
        "domain_description": (
            runtime_root / "domain_description/description.md"
        ).read_text(encoding="utf-8"),
        "case_models": cases,
        "contract": contract,
    }


def build_client(guard: base.BudgetGuard, ledger: CallLedger):
    """Meter every outbound request and record its usage, exactly as the frozen harness does."""
    from llm_client import LLMClient

    if not os.environ.get("OPENAI_API_KEY"):
        raise RuntimeError("OPENAI_API_KEY is absent from the process environment")
    client = LLMClient(model=MODEL, interaction_log=None)
    completions = client._client.chat.completions
    original_create = completions.create

    async def metered(*args, **kwargs):
        guard.reserve()
        kwargs.setdefault("timeout", REQUEST_TIMEOUT_SECONDS)
        if "max_tokens" in kwargs:
            kwargs["max_completion_tokens"] = kwargs.pop("max_tokens")
        started = time.monotonic()
        response = await original_create(*args, **kwargs)
        guard.record(getattr(response, "usage", None))
        ledger.record(guard.requests, response, started)
        return response

    completions.create = metered
    return client


def harness_digests() -> dict[str, str]:
    return {
        path: hashlib.sha256((ROOT / path).read_bytes()).hexdigest() for path in HARNESS_PATHS
    }


async def run(
    output: Path,
    runtime_root: Path,
    run_id: str,
    *,
    budget_usd: float,
    prior_spend_usd: float,
    max_requests: int,
) -> dict[str, Any]:
    import orchestrator
    from airtravel_local_observer import Observer, Proxy, route_metrics, validate_final_stream
    from qa_communication import QACommunicationRecorder
    from qa_registry import QARegistry

    frame = load_frame(runtime_root)
    case_count = len(frame["case_models"])
    guard = base.BudgetGuard(budget_usd, prior_spend_usd, max_requests)
    ledger = CallLedger()
    egress = base.restrict_egress()
    client = build_client(guard, ledger)

    output.mkdir(parents=True, exist_ok=True)
    recorder = QACommunicationRecorder(output / "qa_events.jsonl", run_id=run_id)
    observer = Observer(recorder)
    proxy = Proxy(client, observer, case_count, SETTING_ID, run_id)

    cfg = {
        "setting_id": SETTING_ID,
        "corpus_id": CORPUS_ID,
        "language_name": "UML",
        "domain_description": frame["domain_description"],
        "case_models": frame["case_models"],
        "max_concurrent_cases": MAX_CONCURRENT_CASES,
        "model": MODEL,
        "output_dir": str(output),
    }

    original_client, original_registry = orchestrator.LLMClient, orchestrator.QARegistry
    orchestrator.LLMClient = lambda **_: proxy
    orchestrator.QARegistry = observer.registry(QARegistry)
    started = datetime.now(timezone.utc).replace(microsecond=0)
    status, exception = "TECHNICAL_SUCCESS", None
    try:
        await asyncio.wait_for(
            orchestrator.run_setting(
                cfg, output / "inline-config-not-written.json", None, SETTING_ID
            ),
            RUN_TIMEOUT_SECONDS,
        )
    except base.BudgetExceeded as exc:
        status, exception = "STOPPED_AT_CAP", f"BudgetStop: {exc}"
    except asyncio.TimeoutError:
        status, exception = "INCOMPLETE_TECHNICAL", "TimeoutError"
    except Exception as exc:  # noqa: BLE001 - recorded verbatim in the receipt
        status, exception = "INCOMPLETE_TECHNICAL", f"{type(exc).__name__}: {exc}"
    finally:
        orchestrator.LLMClient, orchestrator.QARegistry = original_client, original_registry
        recorder.close_open_episodes()

    events = recorder.events
    event_log = output / "qa_events.jsonl"
    ledger_path = output / "call-ledger.jsonl"
    ledger_path.write_text(
        "".join(json.dumps(row, sort_keys=True) + "\n" for row in ledger.rows), encoding="utf-8"
    )
    terminations = Counter(
        event.get("termination_reason")
        for event in events
        if event["event_type"] == "EPISODE_TERMINATED"
    )
    if status == "TECHNICAL_SUCCESS":
        validate_final_stream(events)
    completed = datetime.now(timezone.utc).replace(microsecond=0)

    usage = guard.summary()
    ledger_summary = ledger.summary()
    return {
        "schema_version": "airtravel-full-frame-receipt-v1",
        "run_id": run_id,
        "run_class": "FULL_ELIGIBLE_FRAME_DESCRIPTIVE_RUN",
        "not_a_replication_of": "REAL-efe686a-20260905T2303Z",
        "poolable_with_accepted_run": False,
        "pooling_prohibited_because": "case count differs (21 vs 4), so the configuration differs",
        "status": status,
        "technical_exception": exception,
        "setting_id": SETTING_ID,
        "corpus_id": CORPUS_ID,
        "N": case_count,
        "frame": "complete eligible population, not a sample",
        "provider": "openai",
        "model_requested": MODEL,
        "api_mode": "chat.completions",
        "max_tokens": RESERVE_OUTPUT_TOKENS,
        "max_qa_rounds": MAX_QA_ROUNDS,
        "request_timeout_seconds": REQUEST_TIMEOUT_SECONDS,
        "run_timeout_seconds": RUN_TIMEOUT_SECONDS,
        "max_concurrent_cases": MAX_CONCURRENT_CASES,
        "started_at": started.isoformat().replace("+00:00", "Z"),
        "completed_at": completed.isoformat().replace("+00:00", "Z"),
        "usage": usage,
        "call_ledger": ledger_summary,
        "call_ledger_sha256": hashlib.sha256(ledger_path.read_bytes()).hexdigest(),
        "outbound_requests_independently_recomputable": ledger_summary["ledger_rows"]
        == usage["outbound_requests"],
        "blocked_egress_attempts": egress["blocked_hosts"],
        "credential_source": "process environment variable, value never read",
        "event_log_sha256": hashlib.sha256(event_log.read_bytes()).hexdigest()
        if event_log.is_file()
        else None,
        "termination_counts": dict(terminations),
        "lifecycle_summary": {
            "episodes_opened": len({event["episode_id"] for event in events}),
            "episodes_terminated": sum(
                1 for event in events if event["event_type"] == "EPISODE_TERMINATED"
            ),
            "questions": sum(1 for event in events if event["event_type"] == "QUESTION_EMITTED"),
            "answers": sum(1 for event in events if event["event_type"] == "ANSWER_RECEIVED"),
        },
        "corpus_contract": {
            "pinned_commit": frame["contract"]["pinned_commit"],
            "archive_sha256": frame["contract"]["archive_sha256"],
            "case_count": frame["contract"]["case_count"],
        },
        "execution_code_sha256": harness_digests(),
        "reviewed_head": subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True, check=False
        ).stdout.strip(),
        **route_metrics(events),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--execute", action="store_true", required=True)
    parser.add_argument(
        "--runtime-root",
        type=Path,
        default=ROOT / "external_data/airtravel-pr38/fullframe_runtime",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=ROOT / "external_data/airtravel-pr38/full-frame-run/output",
    )
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--budget-usd", type=float, default=DEFAULT_BUDGET_USD)
    parser.add_argument("--prior-spend-usd", type=float, default=0.0)
    parser.add_argument("--max-requests", type=int, default=DEFAULT_MAX_REQUESTS)
    args = parser.parse_args()

    if args.prior_spend_usd < 0 or args.budget_usd <= 0:
        print(json.dumps({"status": "REFUSED", "error": "invalid budget arguments"}))
        return 2
    worst_case = args.max_requests * (
        (RESERVE_INPUT_TOKENS * PRICE_IN_PER_M + RESERVE_OUTPUT_TOKENS * PRICE_OUT_PER_M)
        / 1_000_000
    )
    if worst_case + args.prior_spend_usd > args.budget_usd:
        print(
            json.dumps(
                {
                    "status": "REFUSED_INSUFFICIENT_HEADROOM",
                    "worst_case_usd": round(worst_case, 6),
                    "budget_usd": args.budget_usd,
                }
            )
        )
        return 2
    if (args.output_dir / "run-receipt.json").exists():
        print(json.dumps({"status": "REFUSED", "error": "a run receipt already exists"}))
        return 2

    receipt = asyncio.run(
        run(
            args.output_dir,
            args.runtime_root,
            args.run_id,
            budget_usd=args.budget_usd,
            prior_spend_usd=args.prior_spend_usd,
            max_requests=args.max_requests,
        )
    )
    target = args.output_dir / "run-receipt.json"
    with target.open("xb") as handle:
        handle.write(
            (json.dumps(receipt, indent=2, sort_keys=True, ensure_ascii=False) + "\n").encode(
                "utf-8"
            )
        )
    print(json.dumps(receipt, indent=2, sort_keys=True, ensure_ascii=False))
    return 0 if receipt["status"] == "TECHNICAL_SUCCESS" else 3


if __name__ == "__main__":
    raise SystemExit(main())
