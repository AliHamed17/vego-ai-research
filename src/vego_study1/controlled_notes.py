"""Fail-closed local receipt gate for controlled Study 1 development notes."""

from __future__ import annotations

import csv
import hashlib
import json
import re
import subprocess
from pathlib import Path
from typing import Any

RECEIPT_NAME = "controlled_notes_import.receipt.json"
PROVENANCE_SCHEMA = "ControlledNotesProvenance-v1"
DEVELOPMENT_ONLY = "development_only"
REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
PROVENANCE_FIELDS = frozenset(
    {"schema_version", "source_hash", "source_classification", "intended_use"}
)
_SHA256 = re.compile(r"^sha256:[0-9a-f]{64}$")
_URI_SCHEME = re.compile(r"^[A-Za-z][A-Za-z0-9+.-]*:")
_WINDOWS_DRIVE = re.compile(r"^[A-Za-z]:[\\/]")


class ControlledNotesError(ValueError):
    """Raised when controlled notes do not satisfy the development-only import gate."""


def _sha256(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def _is_remote_value(value: str | Path) -> bool:
    raw_value = str(value)
    return (
        raw_value.startswith((r"\\", "//"))
        or (bool(_URI_SCHEME.match(raw_value)) and not bool(_WINDOWS_DRIVE.match(raw_value)))
    )


def _local_path(value: str | Path, field_name: str) -> Path:
    if _is_remote_value(value):
        raise ControlledNotesError(f"{field_name} must not be a remote URL, URI, or UNC path")
    return Path(value)


def _contains_remote_url(value: Any) -> bool:
    if isinstance(value, str):
        return not value.startswith("sha256:") and _is_remote_value(value)
    if isinstance(value, dict):
        return any(_contains_remote_url(item) for item in value.values())
    if isinstance(value, list):
        return any(_contains_remote_url(item) for item in value)
    return False


def _private_study1_root(value: str | Path) -> Path:
    root = _local_path(value, "private_output_root").resolve()
    private_base = (REPOSITORY_ROOT / "research-private" / "study1").resolve()
    try:
        root.relative_to(private_base)
    except ValueError as error:
        raise ControlledNotesError(
            "private_output_root must be beneath this repository's research-private/study1"
        ) from error
    try:
        relative_root = root.relative_to(REPOSITORY_ROOT)
        ignored = subprocess.run(
            ["git", "-C", str(REPOSITORY_ROOT), "check-ignore", "-q", "--", str(relative_root)],
            capture_output=True,
            check=False,
        ).returncode == 0
    except OSError as error:
        raise ControlledNotesError("private_output_root Git-ignore check failed") from error
    if not ignored:
        raise ControlledNotesError("private_output_root must pass the repository Git-ignore check")
    return root


def _load_provenance(path_value: str | Path) -> dict[str, Any]:
    path = _local_path(path_value, "provenance_manifest")
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
    if set(provenance) != PROVENANCE_FIELDS:
        raise ControlledNotesError("provenance_manifest must contain exactly four allowed fields")
    for field_name in PROVENANCE_FIELDS:
        if not isinstance(provenance[field_name], str):
            raise ControlledNotesError(f"{field_name} must be a string")
    if not _SHA256.fullmatch(provenance["source_hash"]):
        raise ControlledNotesError("source_hash must be a SHA-256 value")
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
    notes_path = _local_path(notes_source, "notes_source")
    manifest_path = _local_path(provenance_manifest, "provenance_manifest")
    output_root = _private_study1_root(private_output_root)
    try:
        source_bytes = notes_path.read_bytes()
    except OSError as error:
        raise ControlledNotesError("notes_source must be a readable local file") from error
    source_hash = _sha256(source_bytes)
    provenance = _load_provenance(manifest_path)
    _validate_provenance(provenance, source_hash, intended_use)
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
