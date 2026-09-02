"""Local-only, aggregate StateDiagram inventory receipts for Study 1."""

from __future__ import annotations

import hashlib
import json
import os
from collections import Counter
from pathlib import Path
from typing import Any

from .path_safety import (
    atomic_write_private_text,
    ensure_private_directory,
    local_path,
    read_local_bytes,
    reject_reparse_entry,
    validate_private_output_root,
)

STATUS = "blocked_pending_data_processing_authorization"
RECEIPT_NAME = "state_diagram_inventory.receipt.json"
REPOSITORY_ROOT = Path(__file__).resolve().parents[2]


class StateDiagramInventoryError(ValueError):
    """Raised when a local-only StateDiagram inventory gate is not satisfied."""


def _private_study1_root(value: str | Path) -> Path:
    return validate_private_output_root(value, REPOSITORY_ROOT, StateDiagramInventoryError)


def _sha256(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def _is_within(candidate: Path, parent: Path) -> bool:
    try:
        candidate.relative_to(parent)
    except ValueError:
        return False
    return True


def _source_files(source_root: Path, private_output_root: Path) -> list[Path]:
    if not source_root.is_dir():
        raise StateDiagramInventoryError("state_root must be an existing local directory")
    if _is_within(private_output_root, source_root):
        raise StateDiagramInventoryError("private_output_root must not be inside state_root")
    files: list[Path] = []

    def _visit(directory: Path) -> None:
        reject_reparse_entry(directory, "state source entry", StateDiagramInventoryError)
        try:
            entries = sorted(os.scandir(directory), key=lambda entry: entry.name)
        except OSError as error:
            raise StateDiagramInventoryError(
                "state_root must be a readable local directory"
            ) from error
        for entry in entries:
            path = Path(entry.path)
            reject_reparse_entry(path, "state source entry", StateDiagramInventoryError)
            if entry.is_dir(follow_symlinks=False):
                _visit(path)
            elif entry.is_file(follow_symlinks=False):
                files.append(path)

    _visit(source_root)
    return files


def _build_receipt(source_root: Path, files: list[Path]) -> dict[str, Any]:
    suffix_counts: Counter[str] = Counter()
    file_hashes: list[str] = []
    opaque_locator_hashes: list[str] = []
    total_bytes = 0
    for path in files:
        content = read_local_bytes(
            path,
            "state source entry",
            StateDiagramInventoryError,
            containment_root=source_root,
        )
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
    source_candidate = local_path(state_root, "state_root", StateDiagramInventoryError)
    output_candidate = local_path(
        private_output_root, "private_output_root", StateDiagramInventoryError
    )
    output_root = _private_study1_root(output_candidate)
    reject_reparse_entry(source_candidate, "state_root", StateDiagramInventoryError)
    source_root = source_candidate.resolve()
    files = _source_files(source_root, output_root)
    receipt = _build_receipt(source_root, files)
    ensure_private_directory(
        output_root,
        output_root,
        REPOSITORY_ROOT,
        StateDiagramInventoryError,
    )
    atomic_write_private_text(
        output_root / RECEIPT_NAME,
        json.dumps(receipt, indent=2, sort_keys=True) + "\n",
        output_root,
        REPOSITORY_ROOT,
        StateDiagramInventoryError,
    )
    return receipt
