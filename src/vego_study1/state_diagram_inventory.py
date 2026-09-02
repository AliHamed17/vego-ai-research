"""Local-only, aggregate StateDiagram inventory receipts for Study 1."""

from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any

STATUS = "blocked_pending_data_processing_authorization"
RECEIPT_NAME = "state_diagram_inventory.receipt.json"


class StateDiagramInventoryError(ValueError):
    """Raised when a local-only StateDiagram inventory gate is not satisfied."""


def _is_remote_value(value: str | Path) -> bool:
    return "://" in str(value)


def _private_study1_root(value: str | Path) -> Path:
    root = Path(value).resolve()
    parts = [part.casefold() for part in root.parts]
    if not any(parts[index : index + 2] == ["research-private", "study1"] for index in range(len(parts) - 1)):
        raise StateDiagramInventoryError(
            "private_output_root must resolve beneath research-private/study1"
        )
    return root


def _sha256(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def _is_within(candidate: Path, parent: Path) -> bool:
    try:
        candidate.relative_to(parent)
    except ValueError:
        return False
    return True


def _source_files(source_root: Path, private_output_root: Path) -> list[Path]:
    if _is_remote_value(source_root):
        raise StateDiagramInventoryError("state_root must be a local directory")
    if not source_root.is_dir():
        raise StateDiagramInventoryError("state_root must be an existing local directory")
    if _is_within(private_output_root, source_root):
        raise StateDiagramInventoryError("private_output_root must not be inside state_root")
    return sorted((path for path in source_root.rglob("*") if path.is_file()), key=lambda path: path.as_posix())


def _build_receipt(source_root: Path, files: list[Path]) -> dict[str, Any]:
    suffix_counts: Counter[str] = Counter()
    file_hashes: list[str] = []
    opaque_locator_hashes: list[str] = []
    total_bytes = 0
    for path in files:
        content = path.read_bytes()
        total_bytes += len(content)
        suffix_counts[path.suffix.casefold() or "[no_suffix]"] += 1
        file_hashes.append(_sha256(content))
        relative_locator = path.relative_to(source_root).as_posix().encode("utf-8")
        opaque_locator_hashes.append(_sha256(b"StateDiagramLocator-v1\0" + relative_locator))

    return {
        "schema_version": "StateDiagramInventoryReceipt-v1",
        "status": STATUS,
        "file_count": len(files),
        "total_bytes": total_bytes,
        "suffix_counts": dict(sorted(suffix_counts.items())),
        "file_hashes": sorted(file_hashes),
        "opaque_locator_hashes": sorted(opaque_locator_hashes),
        "readiness": {
            "data_processing_authorization": "not_authorized",
            "inventory_only": True,
        },
        "limitations": (
            "no evaluator configuration; no cloud model processing; no C0 comparison; "
            "no empirical result was produced"
        ),
    }


def write_state_diagram_inventory(
    state_root: str | Path, private_output_root: str | Path
) -> dict[str, Any]:
    """Write only a deterministic aggregate receipt beneath the private Study 1 root."""
    output_root = _private_study1_root(private_output_root)
    source_root = Path(state_root).resolve()
    files = _source_files(source_root, output_root)
    receipt = _build_receipt(source_root, files)
    output_root.mkdir(parents=True, exist_ok=True)
    (output_root / RECEIPT_NAME).write_text(
        json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return receipt
