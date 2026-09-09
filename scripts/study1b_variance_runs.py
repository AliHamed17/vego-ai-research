"""Historical Study 1B closure guard.

The frozen five-repeat variance protocol is permanently closed as
``BUDGET_BLOCKED_UNDER_FROZEN_PROTOCOL``.  This module is retained as a
metadata/provenance record for the old design, but it is intentionally not an
execution harness.  Calling it must fail before any subprocess, SDK import,
credential access or provider request can occur.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]

PREREGISTERED_REPEATS = 5
PREREGISTRATION = "docs/research/phd-proposal/2026-09-06-study1b-variance-preregistration.md"
DEFAULT_ROOT = ROOT / "external_data/airtravel-pr38/study1b-variance"
STUDY1B_STATUS = "BUDGET_BLOCKED_UNDER_FROZEN_PROTOCOL"

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
    del index, out_root, runtime_root, budget_usd, prior_spend
    raise RuntimeError(
        f"{STUDY1B_STATUS}: historical five-repeat execution is disabled; "
        "use the separately preregistered exploratory pilot"
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--execute", action="store_true", required=True,
                        help="legacy flag; execution is permanently closed")
    parser.add_argument("--budget-usd", type=float, required=False,
                        help="legacy value retained for audit output only")
    parser.add_argument("--output-root", type=Path, default=DEFAULT_ROOT)
    parser.add_argument("--runtime-root", type=Path,
                        default=ROOT / "external_data/airtravel-pr38/runtime_input")
    args = parser.parse_args(argv)
    del args
    print(json.dumps({
        "schema_version": "study1b-closure-v1",
        "preregistration": PREREGISTRATION,
        "preregistered_repeats": PREREGISTERED_REPEATS,
        "status": STUDY1B_STATUS,
        "provider_calls": 0,
        "note": "No repeat was started; the separate constrained exploratory pilot is not a replacement.",
    }, indent=2, sort_keys=True))
    return 4


if __name__ == "__main__":
    raise SystemExit(main())
