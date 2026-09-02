"""Local-only, aggregate StateDiagram inventory receipts for Study 1."""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
from collections import Counter
from pathlib import Path
from typing import Any

STATUS = "blocked_pending_data_processing_authorization"
RECEIPT_NAME = "state_diagram_inventory.receipt.json"
REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
_URI_SCHEME = re.compile(r"^[A-Za-z][A-Za-z0-9+.-]*:")
_WINDOWS_DRIVE = re.compile(r"^[A-Za-z]:[\\/]")


class StateDiagramInventoryError(ValueError):
    """Raised when a local-only StateDiagram inventory gate is not satisfied."""


def _is_remote_value(value: str | Path) -> bool:
    raw_value = str(value)
    return (
        raw_value.startswith((r"\\", "//"))
        or (bool(_URI_SCHEME.match(raw_value)) and not bool(_WINDOWS_DRIVE.match(raw_value)))
    )


def _local_path(value: str | Path, field_name: str) -> Path:
    if _is_remote_value(value):
        raise StateDiagramInventoryError(f"{field_name} must not be a remote URI or UNC path")
    return Path(value)


def _private_study1_root(value: str | Path) -> Path:
    root = _local_path(value, "private_output_root").resolve()
    private_base = (REPOSITORY_ROOT / "research-private" / "study1").resolve()
    if not _is_within(root, private_base):
        raise StateDiagramInventoryError(
            "private_output_root must be beneath this repository's research-private/study1"
        )
    try:
        relative_root = root.relative_to(REPOSITORY_ROOT)
        ignored = subprocess.run(
            ["git", "-C", str(REPOSITORY_ROOT), "check-ignore", "-q", "--", str(relative_root)],
            capture_output=True,
            check=False,
        ).returncode == 0
    except OSError as error:
        raise StateDiagramInventoryError("private_output_root Git-ignore check failed") from error
    if not ignored:
        raise StateDiagramInventoryError("private_output_root must pass the repository Git-ignore check")
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
    source_candidate = _local_path(state_root, "state_root")
    output_candidate = _local_path(private_output_root, "private_output_root")
    output_root = _private_study1_root(output_candidate)
    source_root = source_candidate.resolve()
    files = _source_files(source_root, output_root)
    receipt = _build_receipt(source_root, files)
    output_root.mkdir(parents=True, exist_ok=True)
    (output_root / RECEIPT_NAME).write_text(
        json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return receipt
