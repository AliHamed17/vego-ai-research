"""Run one bounded, offline Study 1 simulated-human correction replay."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from vego_study1.human_intervention import write_intervention_replay  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--case", required=True, help="frozen Agent C case JSON")
    parser.add_argument("--intervention", required=True, help="bounded intervention JSON")
    parser.add_argument("--scoring-schema", required=True, help="frozen scoring schema text")
    parser.add_argument(
        "--private-output-root",
        required=True,
        help="ignored repository-owned research-private/study1 destination",
    )
    arguments = parser.parse_args()
    receipt = write_intervention_replay(
        arguments.case,
        arguments.intervention,
        arguments.scoring_schema,
        arguments.private_output_root,
    )
    print(json.dumps(receipt, sort_keys=True, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
