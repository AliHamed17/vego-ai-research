"""Validate the selected Study 1 branch diff for public-release safety."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from vego_study1.release_validation import (  # noqa: E402
    ReleaseValidationError,
    scan_release_diff,
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repository-root", type=Path, default=Path.cwd())
    parser.add_argument("--base-ref", required=True)
    parser.add_argument("--head-ref", default="HEAD")
    arguments = parser.parse_args()
    try:
        scan = scan_release_diff(
            arguments.repository_root, base_ref=arguments.base_ref, head_ref=arguments.head_ref
        )
    except ReleaseValidationError as error:
        parser.error(str(error))
    if scan.findings:
        print(f"Study 1 release validation failed: {len(scan.findings)} prohibited reference(s).")
        return 1
    print(f"Study 1 release validation passed for {len(scan.paths)} proposed tracked artifact(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
