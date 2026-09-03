"""Validate sanitized Study 1 aggregates and write a public-safe receipt."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from vego_study1.measurement_validation import (  # noqa: E402
    MeasurementValidationError,
    write_validation_receipt,
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    arguments = parser.parse_args()
    try:
        receipt = write_validation_receipt(arguments.input, arguments.output)
    except (MeasurementValidationError, OSError, ValueError) as error:
        parser.error(str(error))
    print(f"{receipt['status']}: wrote denominator-audited Study 1 measurement receipt")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
