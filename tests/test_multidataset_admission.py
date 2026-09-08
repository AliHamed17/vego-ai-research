from __future__ import annotations

import json

import pytest

from vego_multidataset.admission import (
    AdmissionError,
    build_qure_data_card,
    build_vego_se_archive_card,
    validate_data_card,
)


def _qure_source(*, licence: str | None = None) -> dict[str, object]:
    return {
        "concept_doi": "10.5281/zenodo.15656471",
        "record_doi": "10.5281/zenodo.15656472",
        "record_url": "https://zenodo.org/records/15656472",
        "version": "1",
        "published": "2025-06-13",
        "retrieved_at": "2026-09-08T00:00:00+03:00",
        "licence": licence,
        "raw_file_sha256": None,
        "parser_version": "qure-adapter-v1",
    }


def test_qure_without_explicit_licence_is_not_admitted() -> None:
    card = build_qure_data_card(_qure_source())

    assert card["dataset_id"] == "QURE_EXTERNAL_REQUIREMENTS_QUALITY_VALIDATION"
    assert card["decision"] == "NOT_ADMITTED"
    assert "LICENCE_UNVERIFIED" in card["admission_blockers"]
    assert "NOT_DIRECT_ALERT_GROUND_TRUTH" in card["prohibited_claims"]
    assert card["label_role"] == "EXTERNAL_REQUIREMENTS_QUALITY_LABEL"
    validate_data_card(card)


def test_qure_requires_versioned_source_and_hash_before_admission() -> None:
    source = _qure_source(licence="CC-BY-4.0")
    card = build_qure_data_card(source)
    assert card["decision"] == "NOT_ADMITTED"
    assert set(card["admission_blockers"]) == {"RAW_FILE_HASH_UNAVAILABLE", "VERSIONED_FILE_INVENTORY_UNAVAILABLE"}

    source["raw_file_sha256"] = "a" * 64
    source["file_inventory"] = [{"name": "QuRE.csv", "bytes": 1, "sha256": "a" * 64}]
    card = build_qure_data_card(source)
    assert card["decision"] == "ADMITTED_WITH_LIMITATIONS"
    validate_data_card(card)


def test_data_card_rejects_admitted_decision_when_licence_is_unknown() -> None:
    card = build_qure_data_card(_qure_source())
    card["decision"] = "ADMITTED"
    with pytest.raises(AdmissionError, match="licence"):
        validate_data_card(card)


def test_vego_archive_without_provenance_or_licence_is_not_admitted() -> None:
    card = build_vego_se_archive_card(
        {
            "archive_sha256": "b" * 64,
            "archive_bytes": 22_450_455,
            "file_count": 632,
            "inventory_method": "ZIP_CENTRAL_DIRECTORY_METADATA_ONLY",
            "provenance": None,
            "licence": None,
            "task_fit": "UNVERIFIED",
        }
    )

    assert card["dataset_id"] == "VEGO_SE_ARCHIVE_DATASET_PENDING_ADMISSION"
    assert card["decision"] == "NOT_ADMITTED"
    assert card["raw_artifact"]["bytes"] == 22_450_455
    assert set(card["admission_blockers"]) == {
        "PROVENANCE_UNVERIFIED",
        "LICENCE_UNVERIFIED",
        "TASK_FIT_UNVERIFIED",
    }
    validate_data_card(card)


def test_cards_are_safe_to_publish_without_raw_content_or_private_paths() -> None:
    card = build_qure_data_card(_qure_source())
    serialised = json.dumps(card, ensure_ascii=False)
    assert "external_data" not in serialised
    assert "C:\\" not in serialised
    assert "requirement text" not in serialised.lower()
