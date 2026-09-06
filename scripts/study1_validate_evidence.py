"""Compatibility CLI for the fail-closed Study 1 evidence validator.

Older drafts called this script with ``--run-root`` and ``--manifest``.  The
previous implementation could enter a partially bound path and attempted to
recompute values without a private binding manifest.  This wrapper retains the
CLI name while delegating all validation to :mod:`study1_evidence_recovery`.
It never trusts narrative documents and never emits numeric results without a
verified accepted-run chain.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(ROOT / "scripts"))

from study1_evidence_recovery import (  # noqa: E402
    EVIDENCE_INVALID,
    EVIDENCE_NOT_AVAILABLE,
    recover,
    unavailable_result,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-root", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True, help="safe output receipt path")
    parser.add_argument("--binding-manifest", type=Path)
    args = parser.parse_args(argv)
    if args.binding_manifest is None:
        result = unavailable_result(
            "binding manifest was not supplied; legacy validator refuses unbound evidence"
        )
    else:
        result = recover(args.run_root, args.binding_manifest)
    if args.manifest.exists():
        print(json.dumps({"status": "OUTPUT_EXISTS", "check_count": 0}, sort_keys=True))
        return 3
    args.manifest.parent.mkdir(parents=True, exist_ok=True)
    args.manifest.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(
        json.dumps(
            {"status": result["status"], "check_count": len(result["checks"])},
            sort_keys=True,
        )
    )
    return 0 if result["status"] not in {EVIDENCE_NOT_AVAILABLE, EVIDENCE_INVALID} else 2


if __name__ == "__main__":
    raise SystemExit(main())
