"""Study 1B: five repeat AirTravel runs under one shared cost ceiling.

Frozen by docs/research/phd-proposal/2026-09-06-study1b-variance-preregistration.md before any
repeat was executed. The repeat count, the corpus, the model, the configuration and the frozen
Detector-v1 rule are fixed there and are not arguments here.

Each repeat is an independent execution of the reviewed paid-run harness. Spend accumulates
across repeats against a single ceiling: repeat k is told what repeats 1..k-1 already cost, and
refuses to issue a request that would breach the ceiling. A repeat that fails technically is
recorded and does not stop the remaining repeats; the cap being reached does stop them.

Nothing here interprets a result. It executes, records, and stops.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]

PREREGISTERED_REPEATS = 5
PREREGISTRATION = "docs/research/phd-proposal/2026-09-06-study1b-variance-preregistration.md"
DEFAULT_ROOT = ROOT / "external_data/airtravel-pr38/study1b-variance"

# The Study 1 accepted run cost USD 0.134972. A repeat halted mid-way by the ceiling would burn
# money and leave a partial episode set that no denominator can use, so a repeat is only started
# when the remaining headroom covers a full one at three times that observed cost.
OBSERVED_REPEAT_COST_USD = 0.134972
HEADROOM_SAFETY_FACTOR = 3.0
MIN_HEADROOM_TO_START_USD = OBSERVED_REPEAT_COST_USD * HEADROOM_SAFETY_FACTOR


def load_receipt(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8")) if path.is_file() else {}


def execute_repeat(index: int, out_root: Path, runtime_root: Path, budget_usd: float,
                   prior_spend: float) -> dict[str, Any]:
    run_id = f"VARIANCE-{index:02d}"
    output = out_root / run_id / "output"
    if (output / "run-receipt.json").is_file():
        return {"run_id": run_id, "status": "ALREADY_PRESENT",
                "receipt": load_receipt(output / "run-receipt.json")}

    proc = subprocess.run(
        [sys.executable, str(ROOT / "scripts/airtravel_real_run.py"), "--execute",
         "--runtime-root", str(runtime_root), "--output-dir", str(output),
         "--run-id", run_id, "--budget-usd", f"{budget_usd}",
         "--prior-spend-usd", f"{prior_spend}"],
        capture_output=True, text=True, cwd=ROOT,
    )
    receipt = load_receipt(output / "run-receipt.json")
    if receipt:
        return {"run_id": run_id, "status": receipt.get("status", "UNKNOWN"), "receipt": receipt}
    return {
        "run_id": run_id,
        "status": "TECHNICAL_FAILURE_NO_RECEIPT",
        "returncode": proc.returncode,
        "stderr_tail": proc.stderr.strip().splitlines()[-5:] if proc.stderr else [],
        "receipt": {},
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--execute", action="store_true", required=True,
                        help="required so a paid run is never started by accident")
    parser.add_argument("--budget-usd", type=float, required=True,
                        help="hard ceiling shared across every repeat")
    parser.add_argument("--output-root", type=Path, default=DEFAULT_ROOT)
    parser.add_argument("--runtime-root", type=Path,
                        default=ROOT / "external_data/airtravel-pr38/runtime_input")
    args = parser.parse_args()

    started = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    repeats: list[dict[str, Any]] = []
    spend = 0.0
    stopped_at_cap = False

    for index in range(1, PREREGISTERED_REPEATS + 1):
        headroom = args.budget_usd - spend
        if headroom < MIN_HEADROOM_TO_START_USD:
            repeats.append({
                "run_id": f"VARIANCE-{index:02d}",
                "status": "NOT_STARTED_INSUFFICIENT_HEADROOM",
                "headroom_usd": round(headroom, 6),
                "required_usd": round(MIN_HEADROOM_TO_START_USD, 6),
                "cost_usd": 0.0,
                "cumulative_spend_usd": round(spend, 6),
            })
            print(f"VARIANCE-{index:02d}: NOT STARTED — headroom ${headroom:.4f} is below the "
                  f"${MIN_HEADROOM_TO_START_USD:.4f} needed for a full repeat", flush=True)
            stopped_at_cap = True
            break
        row = execute_repeat(index, args.output_root, args.runtime_root, args.budget_usd, spend)
        usage = (row.get("receipt") or {}).get("usage") or {}
        row["cost_usd"] = usage.get("actual_cost_usd", 0.0)
        spend += float(row["cost_usd"] or 0.0)
        row["cumulative_spend_usd"] = round(spend, 6)
        repeats.append(row)
        print(f"{row['run_id']}: {row['status']}  cost ${row['cost_usd']}  "
              f"cumulative ${row['cumulative_spend_usd']}", flush=True)

        headroom = args.budget_usd - spend
        if row["status"] not in {"TECHNICAL_SUCCESS", "ALREADY_PRESENT"} and "budget" in json.dumps(row).lower():
            stopped_at_cap = True
            break
        if headroom <= 0:
            stopped_at_cap = True
            break

    completed = [r for r in repeats if r["status"] in {"TECHNICAL_SUCCESS", "ALREADY_PRESENT"}]
    summary = {
        "schema_version": "study1b-variance-summary-v1",
        "preregistration": PREREGISTRATION,
        "preregistered_repeats": PREREGISTERED_REPEATS,
        "repeats_attempted": len(repeats),
        "repeats_completed": len(completed),
        "status": "STOPPED_AT_CAP" if stopped_at_cap else (
            "COMPLETE" if len(completed) == PREREGISTERED_REPEATS else "INCOMPLETE"),
        "budget_usd": args.budget_usd,
        "total_spend_usd": round(spend, 6),
        "started_at": started,
        "completed_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "repeats": [{k: v for k, v in r.items() if k != "receipt"} for r in repeats],
        "note": (
            "Repeats are never pooled into one denominator and are never pooled with the Study 1 "
            "accepted run, with Study 2, or with any fixture. Detector-v1 classification per "
            "repeat must be computed by the frozen analysis script; this summary records "
            "execution only and interprets nothing."
        ),
    }
    target = args.output_root / "variance-summary.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes((json.dumps(summary, indent=2, sort_keys=True) + "\n").encode("utf-8"))
    print(json.dumps({k: summary[k] for k in
                      ("status", "repeats_completed", "total_spend_usd", "budget_usd")}, indent=2))
    return 0 if summary["status"] in {"COMPLETE", "STOPPED_AT_CAP"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
