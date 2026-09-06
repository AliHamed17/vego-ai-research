"""One authorized provider-backed AirTravel run under hard caps.

Frozen before any output is observed: one setting (cd_airtravel, N=4), one
model, one run. The credential is read only by the OpenAI SDK from the process
environment; this module never reads, logs, stores or transmits its value.
Every outbound request is counted (retries included) and budget-reserved before
it is issued, and egress is restricted to the provider API host.
"""

from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
import os
import socket
import subprocess
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "VEGO-AI/framework"))

SETTING_ID = "cd_airtravel"
CORPUS_ID = "text2uml_airtravel_253b26dc"
N = 4
MODEL = "gpt-5.6-luna"
PRICE_IN_PER_M = 0.20
PRICE_OUT_PER_M = 1.20
MAX_OUTBOUND_REQUESTS = 326
BUDGET_USD = 10.0
RESERVE_INPUT_TOKENS = 8000
RESERVE_OUTPUT_TOKENS = 16384
REQUEST_TIMEOUT_SECONDS = 180
RUN_TIMEOUT_SECONDS = 3600
MAX_CONCURRENT_CASES = 2
ALLOWED_HOSTS = frozenset({"api.openai.com"})
RUN_ROOT = "external_data/airtravel-pr38/v4-real-run"


class BudgetExceeded(RuntimeError):
    """Raised when a request would breach the frozen cost or request cap."""


class BudgetGuard:
    """Count every outbound request and reserve worst-case cost before it."""

    def __init__(self) -> None:
        self.requests = 0
        self.spent_usd = 0.0
        self.prompt_tokens = 0
        self.completion_tokens = 0
        self.per_request_reserve = (
            RESERVE_INPUT_TOKENS * PRICE_IN_PER_M + RESERVE_OUTPUT_TOKENS * PRICE_OUT_PER_M
        ) / 1_000_000

    def reserve(self) -> None:
        if self.requests + 1 > MAX_OUTBOUND_REQUESTS:
            raise BudgetExceeded(f"outbound request cap {MAX_OUTBOUND_REQUESTS} reached")
        if self.spent_usd + self.per_request_reserve > BUDGET_USD:
            raise BudgetExceeded(
                f"budget reservation would exceed ${BUDGET_USD:.2f} (spent ${self.spent_usd:.4f})"
            )
        self.requests += 1

    def record(self, usage: Any) -> None:
        prompt = int(getattr(usage, "prompt_tokens", 0) or 0)
        completion = int(getattr(usage, "completion_tokens", 0) or 0)
        self.prompt_tokens += prompt
        self.completion_tokens += completion
        self.spent_usd += (
            prompt * PRICE_IN_PER_M + completion * PRICE_OUT_PER_M
        ) / 1_000_000

    def summary(self) -> dict[str, Any]:
        return {
            "outbound_requests": self.requests,
            "outbound_request_cap": MAX_OUTBOUND_REQUESTS,
            "prompt_tokens": self.prompt_tokens,
            "completion_tokens": self.completion_tokens,
            "total_tokens": self.prompt_tokens + self.completion_tokens,
            "actual_cost_usd": round(self.spent_usd, 6),
            "budget_usd": BUDGET_USD,
            "within_budget": self.spent_usd <= BUDGET_USD,
            "price_input_per_1m_usd": PRICE_IN_PER_M,
            "price_output_per_1m_usd": PRICE_OUT_PER_M,
        }


def restrict_egress() -> dict[str, int]:
    """Permit name resolution only for the provider API host."""
    counters = {"blocked_hosts": 0}
    original = socket.getaddrinfo

    def guarded(host, port, *args, **kwargs):
        if isinstance(host, bytes):
            host = host.decode()
        if host not in ALLOWED_HOSTS:
            counters["blocked_hosts"] += 1
            raise PermissionError(f"egress to {host!r} is not permitted for this run")
        return original(host, port, *args, **kwargs)

    socket.getaddrinfo = guarded
    return counters


def load_runtime(runtime_root: Path) -> dict[str, Any]:
    import airtravel_v4_contract as contract

    for relative, expected in contract.RUNTIME_FILES.items():
        target = runtime_root / relative
        if not target.is_file() or contract.digest(target) != expected["sha256"]:
            raise ValueError(f"runtime file mismatch: {relative}")
    domain = (runtime_root / "domain_description/description.md").read_text(encoding="utf-8")
    cases = [
        {
            "case_id": relative.split("/", 1)[1].split("_", 1)[0],
            "case_model": (runtime_root / relative).read_text(encoding="utf-8"),
        }
        for relative in sorted(contract.RUNTIME_FILES)
        if relative.startswith("candidate_models/")
    ]
    if len(cases) != N:
        raise ValueError("expected exactly four AirTravel cases")
    return {"domain_description": domain, "case_models": cases}


def build_client(guard: BudgetGuard):
    """Construct the real provider client and meter every outbound request."""
    from llm_client import LLMClient

    if not os.environ.get("OPENAI_API_KEY"):
        raise RuntimeError("OPENAI_API_KEY is absent from the process environment")
    client = LLMClient(model=MODEL, interaction_log=None)
    completions = client._client.chat.completions
    original_create = completions.create

    async def metered(*args, **kwargs):
        guard.reserve()
        kwargs.setdefault("timeout", REQUEST_TIMEOUT_SECONDS)
        # GPT-5.6 rejects the legacy max_tokens parameter; the output ceiling
        # is unchanged, only the parameter name the endpoint accepts.
        if "max_tokens" in kwargs:
            kwargs["max_completion_tokens"] = kwargs.pop("max_tokens")
        response = await original_create(*args, **kwargs)
        guard.record(getattr(response, "usage", None))
        return response

    completions.create = metered
    return client


async def run(output: Path, runtime_root: Path, run_id: str) -> dict[str, Any]:
    import orchestrator
    from airtravel_local_observer import Observer, Proxy, route_metrics, validate_final_stream
    from qa_communication import QACommunicationRecorder
    from qa_registry import QARegistry

    inputs = load_runtime(runtime_root)
    guard = BudgetGuard()
    egress = restrict_egress()
    client = build_client(guard)

    output.mkdir(parents=True, exist_ok=True)
    recorder = QACommunicationRecorder(output / "qa_events.jsonl", run_id=run_id)
    observer = Observer(recorder)
    proxy = Proxy(client, observer, N, SETTING_ID, run_id)

    cfg = {
        "setting_id": SETTING_ID,
        "corpus_id": CORPUS_ID,
        "language_name": "UML",
        "domain_description": inputs["domain_description"],
        "case_models": inputs["case_models"],
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
    except BudgetExceeded as exc:
        status, exception = "INCOMPLETE_TECHNICAL", f"BudgetStop: {exc}"
    except asyncio.TimeoutError:
        status, exception = "INCOMPLETE_TECHNICAL", "TimeoutError"
    except Exception as exc:  # noqa: BLE001 - recorded verbatim in the receipt
        status, exception = "INCOMPLETE_TECHNICAL", f"{type(exc).__name__}: {exc}"
    finally:
        orchestrator.LLMClient, orchestrator.QARegistry = original_client, original_registry
        recorder.close_open_episodes()

    events = recorder.events
    event_log = output / "qa_events.jsonl"
    terminations = Counter(
        e.get("termination_reason") for e in events if e["event_type"] == "EPISODE_TERMINATED"
    )
    if status == "TECHNICAL_SUCCESS":
        validate_final_stream(events)
    completed = datetime.now(timezone.utc).replace(microsecond=0)
    return {
        "schema_version": "airtravel-real-run-receipt-v1",
        "run_id": run_id,
        "status": status,
        "technical_exception": exception,
        "setting_id": SETTING_ID,
        "corpus_id": CORPUS_ID,
        "N": N,
        "provider": "openai",
        "model_requested": MODEL,
        "api_mode": "chat.completions",
        "max_tokens": RESERVE_OUTPUT_TOKENS,
        "request_timeout_seconds": REQUEST_TIMEOUT_SECONDS,
        "run_timeout_seconds": RUN_TIMEOUT_SECONDS,
        "max_concurrent_cases": MAX_CONCURRENT_CASES,
        "started_at": started.isoformat().replace("+00:00", "Z"),
        "completed_at": completed.isoformat().replace("+00:00", "Z"),
        "usage": guard.summary(),
        "blocked_egress_attempts": egress["blocked_hosts"],
        "credential_source": "process environment variable, value never read",
        "event_log_sha256": hashlib.sha256(event_log.read_bytes()).hexdigest()
        if event_log.is_file()
        else None,
        "termination_counts": dict(terminations),
        "reviewed_head": subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True, check=False
        ).stdout.strip(),
        **route_metrics(events),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--execute", action="store_true", required=True)
    parser.add_argument("--runtime-root", type=Path, default=ROOT / "external_data/airtravel-pr38/runtime_input")
    parser.add_argument("--output-dir", type=Path, default=ROOT / RUN_ROOT / "output")
    parser.add_argument("--run-id", required=True)
    args = parser.parse_args()
    if (args.output_dir / "run-receipt.json").exists():
        print(json.dumps({"status": "REFUSED", "error": "a run receipt already exists"}))
        return 2
    receipt = asyncio.run(run(args.output_dir, args.runtime_root, args.run_id))
    target = args.output_dir / "run-receipt.json"
    with target.open("xb") as handle:
        handle.write((json.dumps(receipt, indent=2, sort_keys=True, ensure_ascii=False) + "\n").encode("utf-8"))
    print(json.dumps(receipt, indent=2, sort_keys=True, ensure_ascii=False))
    return 0 if receipt["status"] == "TECHNICAL_SUCCESS" else 3


if __name__ == "__main__":
    raise SystemExit(main())
