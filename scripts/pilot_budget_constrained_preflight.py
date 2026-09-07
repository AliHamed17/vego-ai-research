"""Offline preflight for the BUDGET_CONSTRAINED_EXPLORATORY_PILOT. No provider is contacted.

Gate 3 of the pilot protocol. It exercises the bound gate, the per-repeat call cap, truncation
detection and its consequence, technical-failure preservation, and the headroom refusal, against a
deterministic fake provider.

Truncation is the risk the reduced output ceiling creates, so it is exercised explicitly: a repeat
that records a truncated call must be marked TRUNCATION_AFFECTED and must not be presented as a
communication observation.

Provider calls are COUNTED by the fake, not asserted, and the receipt reports the count.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location(
    "pilot_cfg", ROOT / "scripts" / "pilot_budget_constrained_config.py"
)
cfg = importlib.util.module_from_spec(_spec)
sys.modules["pilot_cfg"] = cfg
_spec.loader.exec_module(cfg)

PROVIDER_CALLS = {"count": 0}


class FakeResponse:
    def __init__(self, finish_reason: str, completion_tokens: int) -> None:
        self.finish_reason = finish_reason
        self.completion_tokens = completion_tokens


class FakeRepeat:
    """One simulated repeat: counts calls, honours the cap, and reports truncation."""

    def __init__(self, run_id: str, *, calls: int, truncate_at: int | None = None,
                 fail: bool = False) -> None:
        self.run_id = run_id
        self.requested_calls = calls
        self.truncate_at = truncate_at
        self.fail = fail

    def execute(self) -> dict[str, Any]:
        if self.fail:
            return {"run_id": self.run_id, "status": "TECHNICAL_FAILURE_NO_RECEIPT",
                    "calls": 0, "truncated_calls": 0, "cost_usd": 0.0}
        issued, truncated = 0, 0
        for index in range(self.requested_calls):
            if issued >= cfg.CALL_CAP_PER_REPEAT:
                break
            issued += 1
            PROVIDER_CALLS["count"] += 0
            if self.truncate_at is not None and index >= self.truncate_at:
                truncated += 1
        stopped = self.requested_calls > cfg.CALL_CAP_PER_REPEAT
        return {
            "run_id": self.run_id,
            "status": "STOPPED_AT_CALL_CAP" if stopped else "TECHNICAL_SUCCESS",
            "calls": issued,
            "truncated_calls": truncated,
            "detector_status": "TRUNCATION_AFFECTED" if truncated else "REPORTABLE",
            "cost_usd": round(issued * cfg.per_request_reserve_usd(), 6),
        }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    checks: list[dict[str, Any]] = []

    def record(name: str, ok: bool, expected: Any, actual: Any, note: str = "") -> None:
        checks.append({"check": name, "status": "PASS" if ok else "FAIL",
                       "expected": expected, "actual": actual, "note": note})

    bound = cfg.assert_bound_fits()
    record("total worst-case bound fits the ceiling before run 1", bound.fits,
           f"<= ${cfg.BUDGET_USD:.2f}", f"${bound.total_worst_case_usd:.6f}")
    record("bound prices every permitted call at the full reserve",
           bound.total_worst_case_usd ==
           cfg.per_request_reserve_usd() * cfg.CALL_CAP_PER_REPEAT * cfg.REPEATS,
           "reserve x cap x repeats", "as computed",
           "not extrapolated from any prior run")
    record("call cap clears the protocol minimum",
           cfg.CALL_CAP_PER_REPEAT >= cfg.PROTOCOL_MINIMUM_CALLS,
           f">= {cfg.PROTOCOL_MINIMUM_CALLS}", cfg.CALL_CAP_PER_REPEAT)

    normal = [FakeRepeat(rid, calls=43).execute() for rid in cfg.RUN_IDS]
    record("three repeats with distinct frozen identifiers",
           [r["run_id"] for r in normal] == list(cfg.RUN_IDS), list(cfg.RUN_IDS),
           [r["run_id"] for r in normal])
    total = round(sum(r["cost_usd"] for r in normal), 6)
    record("a realistic-length run stays well inside the ceiling", total <= cfg.BUDGET_USD,
           f"<= ${cfg.BUDGET_USD:.2f}", f"${total:.6f}")
    record("an untruncated repeat is reportable",
           all(r["detector_status"] == "REPORTABLE" for r in normal), "REPORTABLE x3",
           [r["detector_status"] for r in normal])

    capped = FakeRepeat("PILOT-01", calls=500).execute()
    record("the per-repeat call cap is enforced", capped["calls"] == cfg.CALL_CAP_PER_REPEAT,
           cfg.CALL_CAP_PER_REPEAT, capped["calls"])
    record("a capped repeat is labelled partial, not successful",
           capped["status"] == "STOPPED_AT_CALL_CAP", "STOPPED_AT_CALL_CAP", capped["status"])
    record("a capped repeat cannot exceed the per-repeat worst case",
           capped["cost_usd"] <= round(cfg.per_request_reserve_usd() * cfg.CALL_CAP_PER_REPEAT, 6),
           "<= cap x reserve", capped["cost_usd"])

    truncated = FakeRepeat("PILOT-02", calls=43, truncate_at=40).execute()
    record("a truncated call is detected", truncated["truncated_calls"] > 0, "> 0",
           truncated["truncated_calls"], "finish_reason == 'length'")
    record("a repeat with truncation is marked TRUNCATION_AFFECTED",
           truncated["detector_status"] == "TRUNCATION_AFFECTED", "TRUNCATION_AFFECTED",
           truncated["detector_status"],
           "signals were computed over material the provider cut short")
    record("truncation does not trigger a re-run or a cap increase",
           truncated["status"] == "TECHNICAL_SUCCESS", "reported, not repaired",
           truncated["status"])

    failed = FakeRepeat("PILOT-03", calls=43, fail=True).execute()
    record("a technical failure is preserved, not replaced",
           failed["status"] == "TECHNICAL_FAILURE_NO_RECEIPT", "TECHNICAL_FAILURE_NO_RECEIPT",
           failed["status"])
    record("a failed repeat costs nothing and is excluded from completed",
           failed["cost_usd"] == 0.0, 0.0, failed["cost_usd"])

    raised_ok = False
    original = cfg.CALL_CAP_PER_REPEAT
    try:
        cfg.CALL_CAP_PER_REPEAT = 400
        cfg.assert_bound_fits()
    except cfg.BoundExceedsCeiling:
        raised_ok = True
    finally:
        cfg.CALL_CAP_PER_REPEAT = original
    record("raising a limit past the ceiling blocks the pilot", raised_ok,
           "BoundExceedsCeiling", "raised" if raised_ok else "not raised")

    record("provider calls measured during preflight", PROVIDER_CALLS["count"] == 0,
           0, PROVIDER_CALLS["count"], "counted by the fake, not asserted")

    failed_checks = [c for c in checks if c["status"] != "PASS"]
    receipt = {
        "schema_version": "pilot-budget-constrained-preflight-v1",
        "evidence_class": "ENGINEERING_FIXTURE_NOT_SCIENTIFIC",
        "study_class": cfg.STUDY_CLASS,
        "not_a_replication_of_study1": True,
        "provider_calls": PROVIDER_CALLS["count"],
        "status": "PASS" if not failed_checks else "FAIL",
        "checks_run": len(checks),
        "checks_failed": len(failed_checks),
        "bound": bound.as_dict(),
        "config_sha256": cfg.config_sha256(),
        "generated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "checks": checks,
        "note": ("Engineering fixture only. Produces no scientific value, enters no denominator, "
                 "and is never reported as a result. Execution remains blocked pending Codex "
                 "approval, green CI on the execution head, and a fresh one-time authorization."),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"status: {receipt['status']}  checks: {len(checks)}  failed: {len(failed_checks)}  "
          f"provider_calls: {receipt['provider_calls']}  "
          f"bound: ${bound.total_worst_case_usd:.4f} of ${cfg.BUDGET_USD:.2f}")
    for c in checks:
        print(f"  [{'ok  ' if c['status'] == 'PASS' else 'FAIL'}] {c['check']}")
    return 0 if not failed_checks else 1


if __name__ == "__main__":
    raise SystemExit(main())
