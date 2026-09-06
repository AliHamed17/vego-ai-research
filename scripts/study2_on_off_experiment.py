"""Prepare/run the deterministic Study 2 ON/OFF fixture only.

This command never creates a provider client.  It is deliberately limited to
the engineering fixture suite; its receipt is not a scientific result.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from vego_study2.config import load_config  # noqa: E402
from vego_study2.fixtures import DeterministicFixtureClient, fixture_cases  # noqa: E402
from vego_study2.runner import Study2Runner  # noqa: E402


def _current_code_sha() -> str:
    try:
        completed = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
    except (OSError, subprocess.CalledProcessError):
        return "working-tree"
    return completed.stdout.strip() or "working-tree"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--config",
        type=Path,
        default=ROOT / "docs/research/phd-proposal/study2-frozen-config.json",
    )
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--allowed-root", type=Path, required=True)
    parser.add_argument(
        "--mode", choices=["valid", "malformed", "invalid_json", "timeout", "secret"], default="valid"
    )
    parser.add_argument(
        "--fixture-mode", choices=["no_questions", "two_rounds", "max_rounds"], default="two_rounds"
    )
    args = parser.parse_args(argv)
    config = load_config(args.config)
    runner = Study2Runner(
        config=config,
        cases=fixture_cases(config),
        client=DeterministicFixtureClient(mode=args.mode),
        output_root=args.output_dir,
        approved_root=args.allowed_root,
        code_sha=_current_code_sha(),
    )
    result = __import__("asyncio").run(runner.run_both(fixture_mode=args.fixture_mode))
    summary = {
        "evidence_class": result["evidence_class"],
        "scientific_result_status": result["receipt"]["scientific_result_status"],
        "provider_calls": 0,
        "conditions": {
            condition: {
                "status": payload["status"],
                "successful_cases": payload["successful_cases"],
                "technical_failures": payload["technical_failures"],
                "questions": payload["questions"],
                "answers": payload["answers"],
            }
            for condition, payload in result["conditions"].items()
        },
        "normalized_sha256": result["normalized_sha256"],
    }
    print(json.dumps(summary, ensure_ascii=False, sort_keys=True))
    return 0 if all(payload["status"] == "PASS" for payload in result["conditions"].values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
