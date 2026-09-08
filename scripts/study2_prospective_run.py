"""Thin entry point for the Study 2 prospective ON/OFF harness.

Usage (all commands load and verify the frozen manifest first):

    python scripts/study2_prospective_run.py preflight --private-root <ROOT> [--fake-mode two_rounds]
    python scripts/study2_prospective_run.py gates --private-root <ROOT> --expected-head <SHA>
    python scripts/study2_prospective_run.py execute --private-root <ROOT> --expected-head <SHA> --authorize-live-provider
    python scripts/study2_prospective_run.py validate --output-root <RUN_DIR> --public-aggregate <JSON>
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
for relative in ("src", "scripts", "VEGO-AI/framework"):
    path = str(ROOT / relative)
    if path not in sys.path:
        sys.path.insert(0, path)

from vego_study2.prospective.run import main  # noqa: E402

if __name__ == "__main__":
    raise SystemExit(main())
