"""Check proposed tracked files for Study 1 privacy-boundary violations."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from vego_study1.privacy import (  # noqa: E402
    PrivacyValidationError,
    scan_staged_artifacts,
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--repository-root",
        type=Path,
        default=ROOT,
        help="repository whose staged index objects are validated",
    )
    args = parser.parse_args()
    try:
        scan = scan_staged_artifacts(args.repository_root)
    except PrivacyValidationError as error:
        parser.error(str(error))
    findings = scan.findings
    for finding in findings:
        print(f"field=staged_artifact line={finding.line} category={finding.kind}")
    if not findings:
        print(f"Study 1 privacy validation passed for {len(scan.paths)} staged artifact(s).")
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
