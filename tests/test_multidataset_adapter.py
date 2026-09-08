from __future__ import annotations

import json
from dataclasses import asdict, replace

import pytest

from vego_multidataset.adapter import (
    DatasetAdapterError,
    build_execution_projection,
    build_external_label_evaluation,
    build_prompt_payload,
    deterministic_selection_manifest,
    validate_selection_manifest,
)


def _engineering_rows() -> list[dict[str, str]]:
    return [
        {
            "record_id": "fixture-1",
            "requirement": "ENGINEERING_FIXTURE_NOT_SCIENTIFIC: The service responds quickly.",
            "quality_label": "defect",
        },
        {
            "record_id": "fixture-2",
            "requirement": "ENGINEERING_FIXTURE_NOT_SCIENTIFIC: The service responds within 2 seconds.",
            "quality_label": "ok",
        },
        {
            "record_id": "fixture-3",
            "requirement": "ENGINEERING_FIXTURE_NOT_SCIENTIFIC: The interface is intuitive.",
            "quality_label": "defect",
        },
    ]


def test_execution_projection_separates_external_labels_from_cases() -> None:
    projection = build_execution_projection(
        _engineering_rows(),
        dataset_id="QURE_EXTERNAL_REQUIREMENTS_QUALITY_VALIDATION",
        id_field="record_id",
        text_field="requirement",
        label_field="quality_label",
    )

    assert len(projection.execution_cases) == 3
    assert projection.external_labels == {"fixture-1": "defect", "fixture-2": "ok", "fixture-3": "defect"}
    serialised_cases = json.dumps([asdict(case) for case in projection.execution_cases])
    assert "quality_label" not in serialised_cases
    assert '"defect"' not in serialised_cases
    assert '"ok"' not in serialised_cases


def test_prompt_payload_contains_input_only_and_rejects_label_keys() -> None:
    projection = build_execution_projection(
        _engineering_rows(),
        dataset_id="QURE_EXTERNAL_REQUIREMENTS_QUALITY_VALIDATION",
        id_field="record_id",
        text_field="requirement",
        label_field="quality_label",
    )
    payload = build_prompt_payload(projection.execution_cases[0])
    assert set(payload) == {"case_id", "requirement_text", "input_sha256"}
    assert "quality_label" not in payload

    with pytest.raises(DatasetAdapterError, match="label"):
        build_prompt_payload({"case_id": "bad", "requirement_text": "x", "quality_label": "defect"})


def test_selection_is_deterministic_and_label_independent() -> None:
    projection = build_execution_projection(
        _engineering_rows(),
        dataset_id="QURE_EXTERNAL_REQUIREMENTS_QUALITY_VALIDATION",
        id_field="record_id",
        text_field="requirement",
        label_field="quality_label",
    )
    first = deterministic_selection_manifest(projection.execution_cases, seed="20260908", count=2)
    second = deterministic_selection_manifest(projection.execution_cases, seed="20260908", count=2)

    assert first == second
    assert "quality_label" not in json.dumps(first)
    assert "requirement_text" not in json.dumps(first)
    mutated = replace(projection, external_labels={key: "ok" for key in projection.external_labels})
    assert deterministic_selection_manifest(mutated.execution_cases, seed="20260908", count=2) == first
    assert validate_selection_manifest(first, projection.execution_cases) == tuple(first["selected_case_ids"])

    tampered = dict(first)
    tampered["case_input_hashes"] = {"fixture-1": "0" * 64}
    with pytest.raises(DatasetAdapterError, match="selection"):
        validate_selection_manifest(tampered, projection.execution_cases)


def test_external_labels_can_only_join_after_execution_by_case_and_hash() -> None:
    projection = build_execution_projection(
        _engineering_rows(),
        dataset_id="QURE_EXTERNAL_REQUIREMENTS_QUALITY_VALIDATION",
        id_field="record_id",
        text_field="requirement",
        label_field="quality_label",
    )
    rows = [
        {"case_id": case.case_id, "input_sha256": case.input_sha256, "status": "VALID"}
        for case in projection.execution_cases
    ]
    evaluation = build_external_label_evaluation(projection, rows)
    assert [row["external_requirements_quality_label"] for row in evaluation] == ["defect", "ok", "defect"]
    assert all(row["label_role"] == "NOT_DIRECT_ALERT_GROUND_TRUTH" for row in evaluation)

    rows[0]["input_sha256"] = "0" * 64
    with pytest.raises(DatasetAdapterError, match="input hash"):
        build_external_label_evaluation(projection, rows)


def test_invalid_or_duplicate_rows_fail_closed() -> None:
    rows = _engineering_rows() + [_engineering_rows()[0]]
    with pytest.raises(DatasetAdapterError, match="duplicate"):
        build_execution_projection(
            rows,
            dataset_id="QURE_EXTERNAL_REQUIREMENTS_QUALITY_VALIDATION",
            id_field="record_id",
            text_field="requirement",
            label_field="quality_label",
        )
    with pytest.raises(DatasetAdapterError, match="unexpected external label"):
        build_execution_projection(
            [{"record_id": "x", "requirement": "x", "quality_label": "unknown"}],
            dataset_id="QURE_EXTERNAL_REQUIREMENTS_QUALITY_VALIDATION",
            id_field="record_id",
            text_field="requirement",
            label_field="quality_label",
        )
