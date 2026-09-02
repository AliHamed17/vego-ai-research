"""Validate the selected Study 1 branch diff for public-release safety."""

from __future__ import annotations

import argparse
from pathlib import Path

from vego_study1.release_validation import (
    ReleaseValidationError,
    proposed_tracked_paths,
    validate_release_diff,
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repository-root", type=Path, default=Path.cwd())
    parser.add_argument("--base-ref", required=True)
    parser.add_argument("--head-ref", default="HEAD")
    arguments = parser.parse_args()
    try:
        proposed = proposed_tracked_paths(
            arguments.repository_root, base_ref=arguments.base_ref, head_ref=arguments.head_ref
        )
        findings = validate_release_diff(
            arguments.repository_root, base_ref=arguments.base_ref, head_ref=arguments.head_ref
        )
    except ReleaseValidationError as error:
        parser.error(str(error))
    if findings:
        print(f"Study 1 release validation failed: {len(findings)} prohibited reference(s).")
        return 1
    print(f"Study 1 release validation passed for {len(proposed)} proposed tracked artifact(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
