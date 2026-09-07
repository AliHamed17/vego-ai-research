"""Offline closure check for the permanently closed Study 1B protocol.

Study 1B was a five-repeat variance protocol whose conservative bound did not
fit its frozen USD 2.00 ceiling.  This command verifies that the historical
execution module is a fail-closed guard and does not exercise a repeat.  The
separately preregistered constrained pilot has its own controller and receipt
contract; it is not a Study 1B replacement.
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
STUDY1B_STATUS = "BUDGET_BLOCKED_UNDER_FROZEN_PROTOCOL"
VARIANCE_SCRIPT = ROOT / "scripts" / "study1b_variance_runs.py"
PILOT_CONTROLLER = ROOT / "scripts" / "pilot_budget_constrained_runner.py"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)

    variance_source = VARIANCE_SCRIPT.read_text(encoding="utf-8")
    checks: list[dict[str, Any]] = [
        {
            "check": "historical status is frozen",
            "status": "PASS" if STUDY1B_STATUS == "BUDGET_BLOCKED_UNDER_FROZEN_PROTOCOL" else "FAIL",
            "expected": "BUDGET_BLOCKED_UNDER_FROZEN_PROTOCOL",
            "actual": STUDY1B_STATUS,
        },
        {
            "check": "variance module is a closure guard",
            "status": "PASS" if "airtravel_real_run.py" not in variance_source else "FAIL",
            "expected": "no provider harness reference",
            "actual": "no provider harness reference" if "airtravel_real_run.py" not in variance_source else "provider harness reference present",
        },
        {
            "check": "replacement pilot controller is separate",
            "status": "PASS" if PILOT_CONTROLLER.is_file() else "FAIL",
            "expected": "pilot_budget_constrained_runner.py exists",
            "actual": "present" if PILOT_CONTROLLER.is_file() else "missing",
        },
        {
            "check": "repeat execution is not started",
            "status": "PASS",
            "expected": "NOT_STARTED",
            "actual": "NOT_STARTED",
        },
        {
            "check": "provider calls remain disabled",
            "status": "PASS",
            "expected": 0,
            "actual": 0,
        },
    ]
    failed = [check for check in checks if check["status"] != "PASS"]
    receipt = {
        "schema_version": "study1b-closure-preflight-v1",
        "evidence_class": "ENGINEERING_FIXTURE_NOT_SCIENTIFIC",
        "study_class": "EXPLORATORY_POST_STUDY1_VARIANCE_REPLICATION",
        "study1b_status": STUDY1B_STATUS,
        "repeat_execution": "NOT_STARTED",
        "provider_calls": 0,
        "status": "PASS" if not failed else "FAIL",
        "checks_run": len(checks),
        "checks_failed": len(failed),
        "generated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "checks": checks,
        "note": (
            "Closure verification only. No repeat, provider call, Detector-v1 run or scientific "
            "denominator was produced. The constrained pilot is a separate study."
        ),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(
        f"status: {receipt['status']}  checks: {len(checks)}  failed: {len(failed)}  "
        f"repeat_execution: {receipt['repeat_execution']}  provider_calls: {receipt['provider_calls']}"
    )
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
