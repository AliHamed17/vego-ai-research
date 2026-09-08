"""Safe, machine-readable data-admission records for Study 1.

The module stores metadata and cryptographic identifiers only. Raw dataset
content and local private paths are intentionally rejected from data cards.
"""

from __future__ import annotations

import re
from collections.abc import Mapping
from typing import Any

from .schemas import SchemaError, validate_named


class AdmissionError(ValueError):
    """Raised when a data-admission card is malformed or overclaims access."""


_SHA256_RE = re.compile(r"^[a-f0-9]{64}$")
_DECISIONS = {"ADMITTED", "ADMITTED_WITH_LIMITATIONS", "NOT_ADMITTED"}
_PRIVATE_MARKERS = ("external_data/", "external_data\\", "c:\\users\\", "c:/users/")
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


def _known_licence(value: object) -> bool:
    return isinstance(value, Mapping) and isinstance(value.get("name"), str) and bool(value["name"].strip())


def _valid_sha256(value: object) -> bool:
    return isinstance(value, str) and bool(_SHA256_RE.fullmatch(value.lower()))


def _safe_text(value: object) -> bool:
    if not isinstance(value, str):
        return True
    lowered = value.lower()
    return not any(marker in lowered for marker in _PRIVATE_MARKERS)


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
    if card["decision"] in {"ADMITTED", "ADMITTED_WITH_LIMITATIONS"}:
        if not _known_licence(card["licence"]):
            raise AdmissionError("an admitted dataset requires a known licence")
        if not _valid_sha256(raw.get("sha256")):
            raise AdmissionError("an admitted dataset requires a raw SHA-256")
        if not isinstance(inventory, list) or not inventory:
            raise AdmissionError("an admitted dataset requires a versioned file inventory")
        for row in inventory:
            if not isinstance(row, Mapping) or not _valid_sha256(row.get("sha256")):
                raise AdmissionError("every admitted inventory row requires a SHA-256")
    _ensure_safe_values(card)
    try:
        validate_named(card, "multidataset-data-card-v1.schema.json")
    except SchemaError as exc:
        raise AdmissionError(str(exc)) from exc


def _licence(licence: object) -> dict[str, str | None]:
    if isinstance(licence, str) and licence.strip():
        return {"status": "VERIFIED", "name": licence.strip(), "url": None}
    return {"status": "UNVERIFIED", "name": None, "url": None}


def _inventory(source: Mapping[str, Any]) -> list[dict[str, Any]]:
    rows = source.get("file_inventory")
    if not isinstance(rows, list):
        return []
    safe_rows: list[dict[str, Any]] = []
    for row in rows:
        if not isinstance(row, Mapping):
            continue
        name = row.get("name")
        bytes_value = row.get("bytes")
        sha256 = row.get("sha256")
        if isinstance(name, str) and isinstance(bytes_value, int) and _valid_sha256(sha256):
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

    blockers: list[str] = []
    if not isinstance(inventory.get("provenance"), str) or not inventory["provenance"].strip():
        blockers.append("PROVENANCE_UNVERIFIED")
    if not isinstance(inventory.get("licence"), str) or not inventory["licence"].strip():
        blockers.append("LICENCE_UNVERIFIED")
    if inventory.get("task_fit") not in {"VERIFIED"}:
        blockers.append("TASK_FIT_UNVERIFIED")
    card = {
        "schema_version": "vego-multidataset-data-card-v1",
        "dataset_id": "VEGO_SE_ARCHIVE_DATASET_PENDING_ADMISSION",
        "dataset_name": "VEGO_SE_ARCHIVE",
        "evidence_class": "LOCAL_ARCHIVE_METADATA_ONLY",
        "owner_or_publisher": inventory.get("provenance") or "UNVERIFIED",
        "official_source": {"source": "AUTHORIZED_LOCAL_ARCHIVE_METADATA_ONLY"},
        "licence": _licence(inventory.get("licence")),
        "date_or_version": {"version": inventory.get("version") or "UNVERIFIED"},
        "raw_artifact": {
            "sha256": inventory.get("archive_sha256", "").lower()
            if _valid_sha256(inventory.get("archive_sha256"))
            else None,
            "bytes": inventory.get("archive_bytes") if isinstance(inventory.get("archive_bytes"), int) else None,
            "file_inventory": [],
            "storage": "GITIGNORED_LOCAL_ONLY",
            "inventory_method": inventory.get("inventory_method"),
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
            "source_class": inventory.get("source_class") or "UNVERIFIED",
            "top_level": inventory.get("top_level") or "UNVERIFIED",
            "extension_counts": inventory.get("extension_counts") or {},
            "content_inspection": inventory.get("content_inspection") or "NOT_PERFORMED",
        },
    }
    validate_data_card(card)
    return card
