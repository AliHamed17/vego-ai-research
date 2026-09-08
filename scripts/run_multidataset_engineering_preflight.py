"""Run the generic local-only engineering fixture preflight.

This command is intentionally distinct from dataset execution. It creates only
an ignored, hash-safe engineering receipt and never loads QuRE, a VEGO archive,
an OpenAI SDK, credentials, or a provider endpoint.
"""

from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from vego_multidataset.adapter import build_execution_projection  # noqa: E402
from vego_multidataset.preflight import (  # noqa: E402
    DeterministicOfflineFixtureClient,
    EngineeringPreflightRunner,
)


def _fixture_cases():
    """Return transparent engineering fixtures, never a scientific dataset."""

    projection = build_execution_projection(
        [
            {
                "id": "fixture-a",
                "text": "ENGINEERING_FIXTURE_NOT_SCIENTIFIC: short requirement A",
                "label": "ok",
            },
            {
                "id": "fixture-b",
                "text": "ENGINEERING_FIXTURE_NOT_SCIENTIFIC: short requirement B",
                "label": "defect",
            },
        ],
        dataset_id="ENGINEERING_FIXTURE_NOT_SCIENTIFIC",
        id_field="id",
        text_field="text",
        label_field="label",
    )
    return projection.execution_cases


def _private_output(path: Path) -> Path:
    candidate = path.absolute()
    approved = (ROOT / "external_data").absolute()
    try:
        candidate.relative_to(approved)
    except ValueError as exc:
        raise ValueError("output root must be a child of ignored external_data") from exc
    return candidate


def _clean_head() -> str:
    """Return HEAD only when tracked source is clean enough to bind a receipt."""

    status = subprocess.run(
        ["git", "status", "--porcelain", "--untracked-files=no"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    if status.stdout.strip():
        raise ValueError("refusing to bind an engineering receipt to a dirty tracked tree")
    return subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=ROOT, check=True, capture_output=True, text=True
    ).stdout.strip()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output-root",
        type=Path,
        default=ROOT / "external_data/multidataset-engineering-preflight",
    )
    args = parser.parse_args()
    output_root = _private_output(args.output_root)
    result = asyncio.run(
        EngineeringPreflightRunner(
            cases=_fixture_cases(),
            client=DeterministicOfflineFixtureClient(),
            output_root=output_root,
            approved_root=(ROOT / "external_data").absolute(),
            execution_code_sha=_clean_head(),
        ).run()
    )
    receipt = output_root / "engineering-preflight-receipt.json"
    print(
        json.dumps(
            {
                "status": "PASS_ENGINEERING_ONLY",
                "receipt_sha256": hashlib.sha256(receipt.read_bytes()).hexdigest(),
                "provider_calls": result["provider_calls"],
                "external_provider_calls": result["external_provider_calls"],
                "scientific_result_status": result["scientific_result_status"],
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
