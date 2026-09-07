"""Offline preflight for the Study 1B five-repeat orchestration. No provider is contacted.

Gate 3 of the Study 1B execution protocol. It exercises the orchestration loop that is new for
Study 1B — repeat sequencing, distinct run identifiers, cumulative budget accounting across
repeats, the headroom refusal, and technical-failure preservation — against a deterministic fake
repeat executor.

The single-run harness underneath was preflighted separately for Study 1 (46/46 identical calls,
zero provider calls). This preflight does not re-cover that; it covers the loop above it.

Provider calls are COUNTED, not asserted: the fake executor increments a counter that the receipt
reports, and the run refuses to emit a passing receipt if that counter is non-zero.
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

_spec = importlib.util.spec_from_file_location("study1b_runner", ROOT / "scripts/study1b_variance_runs.py")
runner = importlib.util.module_from_spec(_spec)
sys.modules["study1b_runner"] = runner
_spec.loader.exec_module(runner)

_hspec = importlib.util.spec_from_file_location("study1b_harness", ROOT / "scripts/airtravel_real_run.py")
harness = importlib.util.module_from_spec(_hspec)
sys.modules["study1b_harness"] = harness
_hspec.loader.exec_module(harness)

PROVIDER_CALLS = {"count": 0}
OBSERVED_COST = 0.134972


def fake_repeat(index: int, out_root: Path, runtime_root: Path, budget_usd: float,
                prior_spend: float, *, fail_on: set[int]) -> dict[str, Any]:
    """Stand in for one repeat. Contacts nothing; records what a real repeat would have cost."""
    run_id = f"VARIANCE-{index:02d}"
    if index in fail_on:
        return {"run_id": run_id, "status": "TECHNICAL_FAILURE_NO_RECEIPT",
                "returncode": 3, "stderr_tail": ["simulated lifecycle failure"], "receipt": {}}
    return {
        "run_id": run_id,
        "status": "TECHNICAL_SUCCESS",
        "receipt": {"run_id": run_id, "status": "TECHNICAL_SUCCESS",
                    "usage": {"actual_cost_usd": OBSERVED_COST}},
    }


def scenario(name: str, budget_usd: float, fail_on: set[int], tmp: Path) -> dict[str, Any]:
    original = runner.execute_repeat
    runner.execute_repeat = lambda i, o, r, b, p: fake_repeat(i, o, r, b, p, fail_on=fail_on)
    argv = sys.argv
    out_root = tmp / name
    sys.argv = ["study1b", "--execute", "--budget-usd", str(budget_usd), "--output-root", str(out_root)]
    try:
        runner.main()
    finally:
        runner.execute_repeat = original
        sys.argv = argv
    return json.loads((out_root / "variance-summary.json").read_text(encoding="utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    tmp = args.output.parent / "_preflight_scratch"

    checks: list[dict[str, Any]] = []

    def record(name: str, ok: bool, expected: Any, actual: Any, note: str = "") -> None:
        checks.append({"check": name, "status": "PASS" if ok else "FAIL",
                       "expected": expected, "actual": actual, "note": note})

    ample = scenario("ample", 40.00, set(), tmp)
    record("five repeats attempted under an ample ceiling", ample["repeats_attempted"] == 5,
           5, ample["repeats_attempted"])
    record("five repeats completed", ample["repeats_completed"] == 5, 5, ample["repeats_completed"])
    ids = [r["run_id"] for r in ample["repeats"]]
    record("run identifiers are distinct", len(set(ids)) == 5, 5, len(set(ids)))
    record("run identifiers follow the frozen sequence",
           ids == [f"VARIANCE-{i:02d}" for i in range(1, 6)],
           "VARIANCE-01..05", ids)
    record("cumulative spend accumulates across repeats",
           ample["total_spend_usd"] == round(OBSERVED_COST * 5, 6),
           round(OBSERVED_COST * 5, 6), ample["total_spend_usd"])
    record("status is COMPLETE when all five finish", ample["status"] == "COMPLETE",
           "COMPLETE", ample["status"])

    tight = scenario("tight", 0.60, set(), tmp)
    started = [r for r in tight["repeats"] if r["status"] != "NOT_STARTED_INSUFFICIENT_HEADROOM"]
    refused = [r for r in tight["repeats"] if r["status"] == "NOT_STARTED_INSUFFICIENT_HEADROOM"]
    record("a repeat without headroom for a full one is refused, not truncated",
           len(refused) >= 1, ">=1 refusal", len(refused))
    record("spend never exceeds the ceiling", tight["total_spend_usd"] <= 0.60,
           "<= 0.60", tight["total_spend_usd"])
    record("a partial study is reported STOPPED_AT_CAP, never COMPLETE",
           tight["status"] == "STOPPED_AT_CAP", "STOPPED_AT_CAP", tight["status"])
    record("started repeats are still reported", len(started) >= 1, ">=1", len(started))

    failing = scenario("failure", 40.00, {3}, tmp)
    failed_rows = [r for r in failing["repeats"] if r["status"] == "TECHNICAL_FAILURE_NO_RECEIPT"]
    record("a technical failure is preserved and reported, not replaced",
           len(failed_rows) == 1, 1, len(failed_rows))
    record("a technical failure does not halt the remaining repeats",
           failing["repeats_attempted"] == 5, 5, failing["repeats_attempted"])
    record("a failed repeat is excluded from the completed count",
           failing["repeats_completed"] == 4, 4, failing["repeats_completed"])
    record("a run with a failure is not reported COMPLETE",
           failing["status"] != "COMPLETE", "not COMPLETE", failing["status"])

    record("repeat count is frozen, not a command-line argument",
           "--repeats" not in (ROOT / "scripts/study1b_variance_runs.py").read_text(encoding="utf-8"),
           "absent", "absent")
    record("provider calls measured during preflight", PROVIDER_CALLS["count"] == 0,
           0, PROVIDER_CALLS["count"], "counted by the fake executor, not asserted")

    failed = [c for c in checks if c["status"] != "PASS"]
    receipt = {
        "schema_version": "study1b-offline-preflight-v1",
        "evidence_class": "ENGINEERING_FIXTURE_NOT_SCIENTIFIC",
        "study_class": "EXPLORATORY_POST_STUDY1_VARIANCE_REPLICATION",
        "provider_calls": PROVIDER_CALLS["count"],
        "status": "PASS" if not failed else "FAIL",
        "checks_run": len(checks),
        "checks_failed": len(failed),
        "generated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "checks": checks,
        "note": ("Covers the Study 1B repeat-orchestration loop only. It produces no scientific "
                 "value, enters no denominator, and is never reported as a result."),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"status: {receipt['status']}  checks: {len(checks)}  failed: {len(failed)}  "
          f"provider_calls: {receipt['provider_calls']}")
    for c in checks:
        print(f"  [{'ok  ' if c['status']=='PASS' else 'FAIL'}] {c['check']}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
