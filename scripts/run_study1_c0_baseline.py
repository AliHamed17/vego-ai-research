"""Run the deterministic Study 1 baseline over a selected frozen C0 root."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from vego_study1.c0 import C0ValidationError, write_baseline_artifacts  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--c0-root", required=True, type=Path)
    parser.add_argument("--private-output-root", required=True, type=Path)
    arguments = parser.parse_args()
    try:
        summary = write_baseline_artifacts(arguments.c0_root, arguments.private_output_root)
    except C0ValidationError as error:
        parser.error(str(error))
    print(
        f"wrote sanitized aggregate for {sum(summary['candidate_count_by_stage'].values())} candidates"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
