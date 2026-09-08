from __future__ import annotations

import json
from pathlib import Path

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


def _admitted_qure_card() -> dict[str, object]:
    source = _qure_source(licence="CC-BY-4.0")
    source["raw_file_sha256"] = "a" * 64
    source["file_inventory"] = [{"name": "QuRE.csv", "bytes": 1, "sha256": "a" * 64}]
    return build_qure_data_card(source)


def _archive_source() -> dict[str, object]:
    return {
        "archive_sha256": "b" * 64,
        "archive_bytes": 22_450_455,
        "file_count": 632,
        "inventory_method": "ZIP_CENTRAL_DIRECTORY_METADATA_ONLY",
        "provenance": None,
        "licence": None,
        "task_fit": "UNVERIFIED",
        "source_class": "USER_SUPPLIED_PROJECT_BACKUP_ARCHIVE",
        "top_level": "VEGO-AI",
        "extension_counts": {".json": 252, ".py": 15},
        "content_inspection": "NOT_PERFORMED_PENDING_PROVENANCE_LICENCE_AND_TASK_ADMISSION",
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


def test_data_card_rejects_named_but_unverified_licence_and_unsafe_metadata() -> None:
    card = _admitted_qure_card()

    named_but_unverified = dict(card)
    named_but_unverified["licence"] = {"status": "UNVERIFIED", "name": "CC-BY-4.0", "url": None}
    with pytest.raises(AdmissionError, match="licence"):
        validate_data_card(named_but_unverified)

    unsafe_extra = dict(card)
    unsafe_extra["unreviewed_raw_content"] = "a requirement copied from a private dataset"
    with pytest.raises(AdmissionError, match="schema"):
        validate_data_card(unsafe_extra)

    unsafe_path = dict(card)
    unsafe_path["official_source"] = dict(card["official_source"])
    unsafe_path["official_source"]["source"] = r"\\server\restricted\dataset"
    with pytest.raises(AdmissionError, match="private path"):
        validate_data_card(unsafe_path)


@pytest.mark.parametrize(
    "unsafe_name",
    [
        "../private.csv",
        r"..\\restricted\\records.csv",
        "nested/record.csv",
        r"nested\\record.csv",
        "C:records.csv",
        ".",
        "..",
        "record.csv ",
        "record.csv.",
        "record\x00.csv",
        "record\n.csv",
        "record<private>.csv",
    ],
)
def test_inventory_rejects_pathlike_names_before_a_card_is_created(unsafe_name: str) -> None:
    source = _qure_source(licence="CC-BY-4.0")
    source["raw_file_sha256"] = "a" * 64
    source["file_inventory"] = [{"name": unsafe_name, "bytes": 1, "sha256": "a" * 64}]

    with pytest.raises(AdmissionError, match="inventory name"):
        build_qure_data_card(source)


@pytest.mark.parametrize("unsafe_name", ["nested/record.csv", "record\x00.csv"])
def test_inventory_rejects_pathlike_names_when_a_card_is_revalidated(unsafe_name: str) -> None:
    card = _admitted_qure_card()
    card["raw_artifact"] = dict(card["raw_artifact"])
    card["raw_artifact"]["file_inventory"] = [
        {"name": unsafe_name, "bytes": 1, "sha256": "a" * 64}
    ]

    with pytest.raises(AdmissionError, match="inventory name"):
        validate_data_card(card)


@pytest.mark.parametrize(
    ("field", "value", "message"),
    [
        ("record_url", "copied private-source note", "record_url"),
        ("record_url", "http://example.org/record", "record_url"),
        ("record_doi", "this is not a DOI", "record_doi"),
        ("concept_doi", "https://doi.org/10.5281/zenodo.15656471", "concept_doi"),
        ("retrieved_at", "meeting notes copied verbatim", "retrieved_at"),
    ],
)
def test_data_card_rejects_nonsemantic_official_source_metadata(
    field: str, value: str, message: str
) -> None:
    card = build_qure_data_card(_qure_source())
    card["official_source"] = dict(card["official_source"])
    card["official_source"][field] = value

    with pytest.raises(AdmissionError, match=message):
        validate_data_card(card)


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("concept_doi", "10.5281/zenodo.99999999"),
        ("record_doi", "10.5281/zenodo.99999999"),
        ("record_url", "https://zenodo.org/records/99999999"),
    ],
)
def test_qure_card_rejects_a_different_but_syntactically_valid_pinned_identity(
    field: str, value: str
) -> None:
    card = build_qure_data_card(_qure_source())
    card["official_source"] = dict(card["official_source"])
    card["official_source"][field] = value

    with pytest.raises(AdmissionError, match=field):
        validate_data_card(card)


def test_qure_card_rejects_mixed_external_and_local_official_source_shapes() -> None:
    card = build_qure_data_card(_qure_source())
    card["official_source"] = dict(card["official_source"])
    card["official_source"]["source"] = "AUTHORIZED_LOCAL_ARCHIVE_METADATA_ONLY"

    with pytest.raises(AdmissionError, match="official_source"):
        validate_data_card(card)


def test_data_card_rejects_non_url_licence_metadata() -> None:
    card = build_qure_data_card(_qure_source())
    card["licence"] = dict(card["licence"])
    card["licence"]["url"] = "copied licence discussion"

    with pytest.raises(AdmissionError, match="licence url"):
        validate_data_card(card)


def test_licence_profile_allows_only_cc_by_and_its_canonical_https_url() -> None:
    card = _admitted_qure_card()
    card["licence"] = {
        "status": "VERIFIED",
        "name": "CC-BY-4.0",
        "url": "https://creativecommons.org/licenses/by/4.0/",
    }
    validate_data_card(card)

    card["licence"]["name"] = "MIT"
    with pytest.raises(AdmissionError, match="licence name"):
        validate_data_card(card)


def test_unverified_licence_cannot_carry_claimed_name_or_url() -> None:
    card = build_qure_data_card(_qure_source())
    card["licence"] = {
        "status": "UNVERIFIED",
        "name": "CC-BY-4.0",
        "url": "https://creativecommons.org/licenses/by/4.0/",
    }

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


@pytest.mark.parametrize(
    ("field", "value", "message"),
    [
        ("inventory_method", "ARBITRARY_FREE_TEXT", "inventory_method"),
        ("source_class", "ARBITRARY_FREE_TEXT", "source_class"),
        ("top_level", "../VEGO-AI", "top_level"),
        ("content_inspection", "ARBITRARY_FREE_TEXT", "content_inspection"),
        ("extension_counts", {"../.py": 1}, "extension_counts"),
    ],
)
def test_archive_builder_rejects_uncontrolled_metadata_tags(
    field: str, value: object, message: str
) -> None:
    source = _archive_source()
    source[field] = value

    with pytest.raises(AdmissionError, match=message):
        build_vego_se_archive_card(source)


def test_archive_builder_never_publishes_unverified_provenance_as_owner() -> None:
    source = _archive_source()
    source["provenance"] = "unverified person and copied local note"

    card = build_vego_se_archive_card(source)

    assert card["owner_or_publisher"] == "UNVERIFIED"
    assert "PROVENANCE_UNVERIFIED" in card["admission_blockers"]


def test_tracked_data_cards_remain_semantically_valid() -> None:
    root = Path(__file__).resolve().parents[1]
    cards = root / "docs" / "research" / "phd-proposal" / "multidataset"
    for name in ("qure-data-card-v1.json", "vego-se-archive-data-card-v1.json"):
        validate_data_card(json.loads((cards / name).read_text(encoding="utf-8")))


def test_cards_are_safe_to_publish_without_raw_content_or_private_paths() -> None:
    card = build_qure_data_card(_qure_source())
    serialised = json.dumps(card, ensure_ascii=False)
    assert "external_data" not in serialised
    assert "C:\\" not in serialised
    assert "requirement text" not in serialised.lower()
