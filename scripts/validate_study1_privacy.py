"""Check proposed tracked files for Study 1 privacy-boundary violations."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from vego_study1.privacy import validate_tracked_artifacts  # noqa: E402


def proposed_paths() -> list[Path]:
    result = subprocess.run(
        ["git", "diff", "--cached", "--name-only", "--diff-filter=ACMR"],
        check=True,
        capture_output=True,
        text=True,
    )
    return [Path(line) for line in result.stdout.splitlines()]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="*", type=Path, help="proposed public artifacts")
    args = parser.parse_args()
    findings = validate_tracked_artifacts(args.paths or proposed_paths())
    for finding in findings:
        print(f"{finding.path}:{finding.line}: {finding.kind}")
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
