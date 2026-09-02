"""Fail-closed local receipt gate for controlled Study 1 development notes."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
from typing import Any

RECEIPT_NAME = "controlled_notes_import.receipt.json"
PROVENANCE_SCHEMA = "ControlledNotesProvenance-v1"
DEVELOPMENT_ONLY = "development_only"


class ControlledNotesError(ValueError):
    """Raised when controlled notes do not satisfy the development-only import gate."""


def _sha256(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def _is_remote_value(value: str | Path) -> bool:
    return "://" in str(value)


def _contains_remote_url(value: Any) -> bool:
    if isinstance(value, str):
        return _is_remote_value(value)
    if isinstance(value, dict):
        return any(_contains_remote_url(item) for item in value.values())
    if isinstance(value, list):
        return any(_contains_remote_url(item) for item in value)
    return False


def _private_study1_root(value: str | Path) -> Path:
    root = Path(value).resolve()
    parts = [part.casefold() for part in root.parts]
    if not any(parts[index : index + 2] == ["research-private", "study1"] for index in range(len(parts) - 1)):
        raise ControlledNotesError("private_output_root must resolve beneath research-private/study1")
    return root


def _load_provenance(path_value: str | Path) -> dict[str, Any]:
    if _is_remote_value(path_value):
        raise ControlledNotesError("provenance_manifest must not be a remote URL")
    path = Path(path_value)
    try:
        loaded = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
        raise ControlledNotesError("provenance_manifest must be valid JSON") from error
    if not isinstance(loaded, dict):
        raise ControlledNotesError("provenance_manifest must be a JSON object")
    if _contains_remote_url(loaded):
        raise ControlledNotesError("provenance_manifest must not contain a remote URL")
    return loaded


def _validate_provenance(provenance: dict[str, Any], source_hash: str, intended_use: str) -> None:
    if intended_use != DEVELOPMENT_ONLY:
        raise ControlledNotesError("intended_use must be development_only")
    if provenance.get("schema_version") != PROVENANCE_SCHEMA:
        raise ControlledNotesError("schema_version must be ControlledNotesProvenance-v1")
    if provenance.get("source_hash") != source_hash:
        raise ControlledNotesError("source_hash must match the local notes source")
    if provenance.get("source_classification") != "controlled_development_only":
        raise ControlledNotesError("source_classification must be controlled_development_only")
    if provenance.get("intended_use") != DEVELOPMENT_ONLY:
        raise ControlledNotesError("provenance intended_use must be development_only")


def _record_hashes(notes_path: Path) -> list[str]:
    try:
        content = notes_path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as error:
        raise ControlledNotesError("notes_source must be a readable local UTF-8 file") from error
    suffix = notes_path.suffix.casefold()
    if suffix == ".csv":
        records: list[Any] = list(csv.DictReader(content.splitlines()))
    elif suffix == ".json":
        try:
            document = json.loads(content)
        except json.JSONDecodeError as error:
            raise ControlledNotesError("notes_source JSON must be valid") from error
        if isinstance(document, list):
            records = document
        elif isinstance(document, dict) and isinstance(document.get("records"), list):
            records = document["records"]
        elif isinstance(document, dict):
            records = [document]
        else:
            raise ControlledNotesError("notes_source JSON must contain an object or record list")
    else:
        raise ControlledNotesError("notes_source must be CSV or JSON")
    return sorted(
        _sha256(json.dumps(record, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8"))
        for record in records
    )


def import_controlled_notes(
    notes_source: str | Path,
    provenance_manifest: str | Path,
    private_output_root: str | Path,
    *,
    intended_use: str,
) -> dict[str, Any]:
    """Validate local provenance and emit a redacted, private development-only receipt."""
    if _is_remote_value(notes_source):
        raise ControlledNotesError("notes_source must not be a remote URL")
    notes_path = Path(notes_source)
    try:
        source_bytes = notes_path.read_bytes()
    except OSError as error:
        raise ControlledNotesError("notes_source must be a readable local file") from error
    source_hash = _sha256(source_bytes)
    provenance = _load_provenance(provenance_manifest)
    _validate_provenance(provenance, source_hash, intended_use)
    output_root = _private_study1_root(private_output_root)
    record_hashes = _record_hashes(notes_path)
    receipt = {
        "schema_version": "ControlledNotesImportReceipt-v1",
        "status": DEVELOPMENT_ONLY,
        "source_hash": source_hash,
        "import_hash": _sha256(
            json.dumps(
                {"source_hash": source_hash, "opaque_record_hashes": record_hashes},
                sort_keys=True,
                separators=(",", ":"),
            ).encode("utf-8")
        ),
        "record_count": len(record_hashes),
        "opaque_record_hashes": record_hashes,
        "provenance": {
            "schema_version": provenance["schema_version"],
            "source_classification": provenance["source_classification"],
            "intended_use": provenance["intended_use"],
        },
    }
    output_root.mkdir(parents=True, exist_ok=True)
    (output_root / RECEIPT_NAME).write_text(
        json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return receipt
