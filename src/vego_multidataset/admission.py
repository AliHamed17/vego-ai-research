"""Safe, machine-readable data-admission records for Study 1.

The module stores metadata and cryptographic identifiers only. Raw dataset
content and local private paths are intentionally rejected from data cards.
"""

from __future__ import annotations

import re
from collections.abc import Mapping
from datetime import date, datetime
from typing import Any

from .schemas import SchemaError, validate_named


class AdmissionError(ValueError):
    """Raised when a data-admission card is malformed or overclaims access."""


_SHA256_RE = re.compile(r"^[a-f0-9]{64}$")
_QURE_PARSER_VERSION_RE = re.compile(r"^qure-adapter-v[1-9][0-9]*$")
_EXTENSION_RE = re.compile(r"^\.[a-z0-9]{1,16}$")
_DECISIONS = {"ADMITTED", "ADMITTED_WITH_LIMITATIONS", "NOT_ADMITTED"}
_PRIVATE_MARKERS = ("external_data/", "external_data\\", "c:\\users\\", "c:/users/")
_ABSOLUTE_PATH_RE = re.compile(r"^(?:[a-z]:[\\/]|\\\\|/|~[\\/]|file:)", re.IGNORECASE)
_CONTROL_CHAR_RE = re.compile(r"[\x00-\x1f\x7f]")
_WINDOWS_RESERVED_FILENAME_CHARS = frozenset('<>:"/\\|?*')
_QURE_DATASET_ID = "QURE_EXTERNAL_REQUIREMENTS_QUALITY_VALIDATION"
_ARCHIVE_DATASET_ID = "VEGO_SE_ARCHIVE_DATASET_PENDING_ADMISSION"
_QURE_SOURCE = {
    "concept_doi": "10.5281/zenodo.15656471",
    "record_doi": "10.5281/zenodo.15656472",
    "record_url": "https://zenodo.org/records/15656472",
}
_CC_BY_40 = "CC-BY-4.0"
_CC_BY_40_URL = "https://creativecommons.org/licenses/by/4.0/"
_ARCHIVE_SOURCE = "AUTHORIZED_LOCAL_ARCHIVE_METADATA_ONLY"
_ARCHIVE_INVENTORY_METHODS = {"ZIP_CENTRAL_DIRECTORY_METADATA_ONLY", "UNVERIFIED"}
_ARCHIVE_SOURCE_CLASSES = {"USER_SUPPLIED_PROJECT_BACKUP_ARCHIVE", "UNVERIFIED"}
_ARCHIVE_CONTENT_INSPECTION = {
    "NOT_PERFORMED_PENDING_PROVENANCE_LICENCE_AND_TASK_ADMISSION",
    "UNVERIFIED",
}
_REQUIRED_FIELDS = {
    "schema_version",
    "dataset_id",
    "dataset_name",
    "evidence_class",
    "owner_or_publisher",
    "official_source",
    "licence",
    "date_or_version",
    "raw_artifact",
    "source_file_count",
    "analysis_unit",
    "language_or_domain",
    "independent_labels_or_reference_artifacts",
    "potential_leakage_risk",
    "privacy_classification",
    "intended_vego_task",
    "permitted_claims",
    "prohibited_claims",
    "decision",
    "admission_blockers",
    "review_status",
}


def _valid_sha256(value: object) -> bool:
    return isinstance(value, str) and bool(_SHA256_RE.fullmatch(value.lower()))


def _safe_text(value: object) -> bool:
    if not isinstance(value, str):
        return True
    lowered = value.lower()
    return (
        len(value) <= 512
        and "\n" not in value
        and "\r" not in value
        and not _ABSOLUTE_PATH_RE.match(value)
        and not any(marker in lowered for marker in _PRIVATE_MARKERS)
    )


def _validate_logical_basename(value: object, field: str) -> str:
    if not isinstance(value, str) or not 1 <= len(value) <= 255:
        raise AdmissionError(f"{field} must be a 1-255 character logical basename")
    if (
        value in {".", ".."}
        or value.endswith((" ", "."))
        or _CONTROL_CHAR_RE.search(value)
        or any(character in _WINDOWS_RESERVED_FILENAME_CHARS for character in value)
    ):
        raise AdmissionError(f"{field} must be a safe logical basename")
    return value


def _value_or_default(source: Mapping[str, Any], key: str, default: Any) -> Any:
    value = source.get(key)
    return default if value is None else value


def _is_iso_date(value: object) -> bool:
    if not isinstance(value, str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
        return False
    try:
        date.fromisoformat(value)
    except ValueError:
        return False
    return True


def _is_iso_date_or_rfc3339_timestamp(value: object) -> bool:
    if _is_iso_date(value):
        return True
    if not isinstance(value, str) or not re.fullmatch(
        r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})",
        value,
    ):
        return False
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return False
    return parsed.tzinfo is not None


def _validate_licence_profile(value: object) -> None:
    if not isinstance(value, Mapping):
        raise AdmissionError("licence must be a metadata object")
    if value.get("status") == "UNVERIFIED":
        if value.get("name") is not None or value.get("url") is not None:
            raise AdmissionError("unverified licence must not carry a name or licence url")
        return
    if value.get("status") != "VERIFIED":
        raise AdmissionError("licence status is invalid")
    if value.get("name") != _CC_BY_40:
        raise AdmissionError("licence name is not supported by the current profile")
    if value.get("url") not in {None, _CC_BY_40_URL}:
        raise AdmissionError("licence url is not the canonical HTTPS CC-BY-4.0 URL")


def _validate_file_inventory(value: object) -> None:
    if not isinstance(value, list):
        raise AdmissionError("file inventory must be a list")
    for row in value:
        if not isinstance(row, Mapping):
            raise AdmissionError("file inventory rows must be metadata objects")
        _validate_logical_basename(row.get("name"), "inventory name")
        if isinstance(row.get("bytes"), bool) or not isinstance(row.get("bytes"), int):
            raise AdmissionError("inventory bytes must be a non-negative integer")
        if int(row["bytes"]) < 0:
            raise AdmissionError("inventory bytes must be a non-negative integer")
        if not _valid_sha256(row.get("sha256")):
            raise AdmissionError("inventory sha256 is invalid")


def _validate_qure_official_source(value: object) -> None:
    if not isinstance(value, Mapping) or set(value) != {
        "concept_doi",
        "record_doi",
        "record_url",
        "retrieved_at",
    }:
        raise AdmissionError("official_source must contain the exact QuRE source fields")
    for field, expected in _QURE_SOURCE.items():
        if value.get(field) != expected:
            raise AdmissionError(f"{field} does not match the pinned QuRE source")
    if not _is_iso_date_or_rfc3339_timestamp(value.get("retrieved_at")):
        raise AdmissionError("retrieved_at must be an ISO date or RFC3339 timestamp with timezone")


def _validate_archive_metadata(card: Mapping[str, Any]) -> None:
    source = card.get("official_source")
    if source != {"source": _ARCHIVE_SOURCE}:
        raise AdmissionError("official_source must be the authorized local archive metadata marker")
    raw = card.get("raw_artifact")
    if not isinstance(raw, Mapping) or raw.get("inventory_method") not in _ARCHIVE_INVENTORY_METHODS:
        raise AdmissionError("inventory_method is not an approved archive metadata tag")
    metadata = card.get("metadata_inventory")
    if not isinstance(metadata, Mapping):
        raise AdmissionError("metadata_inventory must be an archive metadata object")
    if metadata.get("source_class") not in _ARCHIVE_SOURCE_CLASSES:
        raise AdmissionError("source_class is not an approved archive metadata tag")
    _validate_logical_basename(metadata.get("top_level"), "top_level")
    if metadata.get("content_inspection") not in _ARCHIVE_CONTENT_INSPECTION:
        raise AdmissionError("content_inspection is not an approved archive metadata tag")
    extension_counts = metadata.get("extension_counts")
    if not isinstance(extension_counts, Mapping):
        raise AdmissionError("extension_counts must be an object")
    for extension, count in extension_counts.items():
        if not isinstance(extension, str) or not _EXTENSION_RE.fullmatch(extension):
            raise AdmissionError("extension_counts contains an invalid extension key")
        if isinstance(count, bool) or not isinstance(count, int) or count < 0:
            raise AdmissionError("extension_counts contains an invalid count")
    if card.get("owner_or_publisher") != "UNVERIFIED":
        raise AdmissionError("archive owner_or_publisher must remain UNVERIFIED")
    blockers = card.get("admission_blockers")
    if not isinstance(blockers, list) or "PROVENANCE_UNVERIFIED" not in blockers:
        raise AdmissionError("archive provenance must remain unverified")


def _validate_card_semantics(card: Mapping[str, Any]) -> None:
    raw = card.get("raw_artifact")
    if not isinstance(raw, Mapping):
        raise AdmissionError("raw artifact must be a metadata object")
    _validate_file_inventory(raw.get("file_inventory"))
    _validate_licence_profile(card.get("licence"))

    dataset_id = card.get("dataset_id")
    if dataset_id == _QURE_DATASET_ID:
        _validate_qure_official_source(card.get("official_source"))
        parser_version = raw.get("parser_version")
        if parser_version is not None and (
            not isinstance(parser_version, str) or not _QURE_PARSER_VERSION_RE.fullmatch(parser_version)
        ):
            raise AdmissionError("parser_version is not an approved QuRE adapter tag")
    elif dataset_id == _ARCHIVE_DATASET_ID:
        _validate_archive_metadata(card)
    else:
        raise AdmissionError("unsupported data-card dataset_id")


def _ensure_safe_values(value: Any) -> None:
    if isinstance(value, Mapping):
        for nested in value.values():
            _ensure_safe_values(nested)
    elif isinstance(value, list):
        for nested in value:
            _ensure_safe_values(nested)
    elif isinstance(value, str) and not _safe_text(value):
        raise AdmissionError("data card contains a private path or raw-data marker")


def validate_data_card(card: Mapping[str, Any]) -> None:
    """Validate a safe admission record without accessing a dataset.

    Primary admission is deliberately stricter than a status memo: an admitted
    dataset must name a licence and bind a raw file inventory by SHA-256.
    """

    missing = sorted(_REQUIRED_FIELDS - set(card))
    if missing:
        raise AdmissionError(f"data card missing required fields: {', '.join(missing)}")
    if card["schema_version"] != "vego-multidataset-data-card-v1":
        raise AdmissionError("unsupported data-card schema version")
    if card["decision"] not in _DECISIONS:
        raise AdmissionError("unsupported data-admission decision")
    if not isinstance(card["admission_blockers"], list):
        raise AdmissionError("admission blockers must be a list")
    if not isinstance(card["raw_artifact"], Mapping):
        raise AdmissionError("raw artifact must be a metadata object")

    raw = card["raw_artifact"]
    inventory = raw.get("file_inventory")
    _validate_file_inventory(inventory)
    if card["decision"] in {"ADMITTED", "ADMITTED_WITH_LIMITATIONS"}:
        licence = card["licence"]
        if not isinstance(licence, Mapping) or licence.get("status") != "VERIFIED":
            raise AdmissionError("an admitted dataset requires a verified licence")
        if licence.get("name") != _CC_BY_40:
            raise AdmissionError("licence name must be CC-BY-4.0")
        if licence.get("url") not in {None, _CC_BY_40_URL}:
            raise AdmissionError("licence url must be the canonical CC-BY-4.0 URL")
        if card["admission_blockers"]:
            raise AdmissionError("an admitted dataset cannot retain admission blockers")
        if not _valid_sha256(raw.get("sha256")):
            raise AdmissionError("an admitted dataset requires a raw SHA-256")
        if not isinstance(inventory, list) or not inventory:
            raise AdmissionError("an admitted dataset requires a versioned file inventory")
        for row in inventory:
            if not isinstance(row, Mapping) or not _valid_sha256(row.get("sha256")):
                raise AdmissionError("every admitted inventory row requires a SHA-256")
    _ensure_safe_values(card)
    _validate_card_semantics(card)
    try:
        validate_named(card, "multidataset-data-card-v1.schema.json")
    except SchemaError as exc:
        raise AdmissionError(str(exc)) from exc


def _licence(licence: object) -> dict[str, str | None]:
    if licence == _CC_BY_40:
        return {"status": "VERIFIED", "name": _CC_BY_40, "url": None}
    return {"status": "UNVERIFIED", "name": None, "url": None}


def _inventory(source: Mapping[str, Any]) -> list[dict[str, Any]]:
    rows = source.get("file_inventory")
    if not isinstance(rows, list):
        return []
    safe_rows: list[dict[str, Any]] = []
    for row in rows:
        if not isinstance(row, Mapping):
            raise AdmissionError("file inventory rows must be metadata objects")
        name = row.get("name")
        bytes_value = row.get("bytes")
        sha256 = row.get("sha256")
        _validate_logical_basename(name, "inventory name")
        if isinstance(bytes_value, bool) or not isinstance(bytes_value, int) or bytes_value < 0:
            raise AdmissionError("inventory bytes must be a non-negative integer")
        if not _valid_sha256(sha256):
            raise AdmissionError("inventory sha256 is invalid")
        safe_rows.append({"name": name, "bytes": bytes_value, "sha256": sha256.lower()})
    return safe_rows


def build_qure_data_card(source: Mapping[str, Any]) -> dict[str, Any]:
    """Build QuRE's status without treating a requirement label as alert truth."""

    licence = _licence(source.get("licence"))
    inventory = _inventory(source)
    raw_sha256 = source.get("raw_file_sha256")
    blockers: list[str] = []
    if licence["status"] != "VERIFIED":
        blockers.append("LICENCE_UNVERIFIED")
    if not _valid_sha256(raw_sha256):
        blockers.append("RAW_FILE_HASH_UNAVAILABLE")
    if not inventory:
        blockers.append("VERSIONED_FILE_INVENTORY_UNAVAILABLE")
    decision = "NOT_ADMITTED" if blockers else "ADMITTED_WITH_LIMITATIONS"
    card = {
        "schema_version": "vego-multidataset-data-card-v1",
        "dataset_id": "QURE_EXTERNAL_REQUIREMENTS_QUALITY_VALIDATION",
        "dataset_name": "QuRE",
        "evidence_class": "PUBLIC_EXTERNAL_DATASET_PENDING_OR_LIMITED_ADMISSION",
        "owner_or_publisher": "Anonymous (as displayed on the pinned Zenodo version record)",
        "official_source": {
            "concept_doi": source.get("concept_doi"),
            "record_doi": source.get("record_doi"),
            "record_url": source.get("record_url"),
            "retrieved_at": source.get("retrieved_at"),
        },
        "licence": licence,
        "date_or_version": {"published": source.get("published"), "version": source.get("version")},
        "raw_artifact": {
            "sha256": raw_sha256.lower() if _valid_sha256(raw_sha256) else None,
            "bytes": source.get("raw_file_bytes") if isinstance(source.get("raw_file_bytes"), int) else None,
            "file_inventory": inventory,
            "storage": "GITIGNORED_LOCAL_ONLY",
            "parser_version": source.get("parser_version"),
        },
        "source_file_count": len(inventory) if inventory else None,
        "analysis_unit": "REQUIREMENT_RECORD",
        "language_or_domain": "INDUSTRIAL_REQUIREMENTS_QUALITY",
        "independent_labels_or_reference_artifacts": "DEFECT_OK_REQUIREMENTS_QUALITY_LABELS",
        "label_role": "EXTERNAL_REQUIREMENTS_QUALITY_LABEL",
        "potential_leakage_risk": "LABELS_MUST_NOT_ENTER_EXECUTION_CASES_OR_PROMPTS",
        "privacy_classification": "PUBLIC_EXTERNAL_PENDING_LICENCE_VERIFICATION",
        "intended_vego_task": "ASSOCIATION_WITH_EXTERNAL_REQUIREMENTS_QUALITY_LABEL",
        "permitted_claims": [
            "ASSOCIATION_WITH_EXTERNAL_REQUIREMENTS_QUALITY_LABEL",
            "DESCRIPTIVE_CROSS_TABULATION_ONLY",
        ],
        "prohibited_claims": [
            "NOT_DIRECT_ALERT_GROUND_TRUTH",
            "DETECTOR_ACCURACY",
            "DEFECT_PREVALENCE",
            "HUMAN_INTERVENTION_NECESSITY",
        ],
        "decision": decision,
        "admission_blockers": blockers,
        "review_status": "PENDING_EXPLICIT_LICENCE_AND_VERIFIED_FILE_BINDING",
    }
    validate_data_card(card)
    return card


def build_vego_se_archive_card(inventory: Mapping[str, Any]) -> dict[str, Any]:
    """Build a fail-closed archive status from metadata-only inventory."""

    blockers: list[str] = ["PROVENANCE_UNVERIFIED"]
    if not isinstance(inventory.get("licence"), str) or not inventory["licence"].strip():
        blockers.append("LICENCE_UNVERIFIED")
    if inventory.get("task_fit") not in {"VERIFIED"}:
        blockers.append("TASK_FIT_UNVERIFIED")
    card = {
        "schema_version": "vego-multidataset-data-card-v1",
        "dataset_id": "VEGO_SE_ARCHIVE_DATASET_PENDING_ADMISSION",
        "dataset_name": "VEGO_SE_ARCHIVE",
        "evidence_class": "LOCAL_ARCHIVE_METADATA_ONLY",
        "owner_or_publisher": "UNVERIFIED",
        "official_source": {"source": _ARCHIVE_SOURCE},
        "licence": _licence(inventory.get("licence")),
        "date_or_version": {"version": inventory.get("version") or "UNVERIFIED"},
        "raw_artifact": {
            "sha256": inventory.get("archive_sha256", "").lower()
            if _valid_sha256(inventory.get("archive_sha256"))
            else None,
            "bytes": inventory.get("archive_bytes") if isinstance(inventory.get("archive_bytes"), int) else None,
            "file_inventory": [],
            "storage": "GITIGNORED_LOCAL_ONLY",
            "inventory_method": _value_or_default(
                inventory, "inventory_method", "UNVERIFIED"
            ),
        },
        "source_file_count": inventory.get("file_count"),
        "analysis_unit": "UNVERIFIED_PENDING_CONTENT_ADMISSION",
        "language_or_domain": "SOFTWARE_ENGINEERING_ARCHIVE_UNVERIFIED",
        "independent_labels_or_reference_artifacts": "UNVERIFIED",
        "potential_leakage_risk": "PRIVATE_OR_PROHIBITED_CONTENT_POSSIBLE",
        "privacy_classification": "LOCAL_ARCHIVE_RESTRICTED_UNTIL_ADMITTED",
        "intended_vego_task": "NONE_UNTIL_PROVENANCE_LICENCE_AND_TASK_FIT_ARE_VERIFIED",
        "permitted_claims": ["METADATA_ONLY_INVENTORY"],
        "prohibited_claims": ["DATASET_CONTENT_CLAIM", "EXPERIMENTAL_RESULT", "PROVIDER_EXECUTION"],
        "decision": "NOT_ADMITTED",
        "admission_blockers": blockers,
        "review_status": "METADATA_ONLY_REVIEW_REQUIRED",
        "metadata_inventory": {
            "source_class": _value_or_default(inventory, "source_class", "UNVERIFIED"),
            "top_level": _value_or_default(inventory, "top_level", "UNVERIFIED"),
            "extension_counts": _value_or_default(inventory, "extension_counts", {}),
            "content_inspection": _value_or_default(
                inventory, "content_inspection", "UNVERIFIED"
            ),
        },
    }
    validate_data_card(card)
    return card
