"""Build verified VEGO-AI proposal figures and their QA evidence."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT / "src"))

from proposal_visuals.qa import FIGURES_ROOT, BuildConfig, build_all, run_qa  # noqa: E402


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--source",
        type=Path,
        help="explicit approved proposal PDF; required unless --verify resolves the provenance filename",
    )
    parser.add_argument(
        "--output-root",
        type=Path,
        default=FIGURES_ROOT,
        help="figures root receiving rendered/ and qa/ children",
    )
    parser.add_argument("--clean", action="store_true", help="remove only rendered/ and qa/generated/")
    parser.add_argument(
        "--verify",
        action="store_true",
        help="run QA and allow the approved provenance filename to resolve in Downloads",
    )
    parser.add_argument(
        "--figure",
        action="append",
        choices=[f"fig-{number:02d}" for number in range(1, 12)],
        help="build one named figure (repeatable); defaults to all eleven",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _parser()
    args = parser.parse_args(argv)
    if args.source is None and not args.verify:
        parser.error("--source is required unless --verify is supplied")
    receipt = build_all(
        BuildConfig(
            output_root=args.output_root,
            source_pdf_path=args.source,
            figure_ids=tuple(args.figure) if args.figure else tuple(f"fig-{number:02d}" for number in range(1, 12)),
            clean=args.clean,
        )
    )
    print(receipt.to_json(), end="")
    if not args.verify:
        return 0
    qa = run_qa(receipt)
    print(qa.to_json(), end="")
    return 0 if qa.passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
