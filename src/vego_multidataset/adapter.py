"""Leakage-safe adapters for the planned multi-dataset baseline.

QuRE labels are external requirements-quality labels. They are deliberately
kept apart from execution cases, prompts, selection manifests, and model
outputs until the post-execution association layer.
"""

from __future__ import annotations

import hashlib
import json
import re
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any

from .schemas import SchemaError, validate_named


class DatasetAdapterError(ValueError):
    """Raised when a dataset adapter would make an unsafe or ambiguous projection."""


_SHA256_RE = re.compile(r"^[a-f0-9]{64}$")
_QURE_LABELS = {"defect", "ok"}
_LABEL_KEY_MARKERS = ("label", "ground_truth", "gold")


@dataclass(frozen=True)
class ExecutionCase:
    """Label-free input used by a provider or offline engineering preflight."""

    dataset_id: str
    case_id: str
    requirement_text: str
    input_sha256: str


@dataclass(frozen=True)
class DatasetProjection:
    """Keep execution input and independent evaluation labels in separate fields."""

    dataset_id: str
    execution_cases: tuple[ExecutionCase, ...]
    external_labels: Mapping[str, str]


def _canonical_json(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode(
        "utf-8"
    )


def _sha256(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _has_label_key(mapping: Mapping[str, Any]) -> bool:
    return any(any(marker in str(key).lower() for marker in _LABEL_KEY_MARKERS) for key in mapping)


def _require_string(row: Mapping[str, Any], field: str) -> str:
    value = row.get(field)
    if not isinstance(value, str) or not value.strip():
        raise DatasetAdapterError(f"missing or invalid {field}")
    return value.strip()


def build_execution_projection(
    rows: Sequence[Mapping[str, Any]],
    *,
    dataset_id: str,
    id_field: str,
    text_field: str,
    label_field: str,
) -> DatasetProjection:
    """Split an input table into label-free execution input and hidden labels.

    The returned ``ExecutionCase`` has no label field. Callers must preserve
    that separation; any later association is performed by
    :func:`build_external_label_evaluation` after output is bound to a case
    hash.
    """

    if not isinstance(dataset_id, str) or not dataset_id.strip():
        raise DatasetAdapterError("dataset id is required")
    if not rows:
        raise DatasetAdapterError("at least one input row is required")
    case_ids: set[str] = set()
    cases: list[ExecutionCase] = []
    labels: dict[str, str] = {}
    for row in rows:
        if not isinstance(row, Mapping):
            raise DatasetAdapterError("dataset rows must be mappings")
        case_id = _require_string(row, id_field)
        text = _require_string(row, text_field)
        label = _require_string(row, label_field).lower()
        if label not in _QURE_LABELS:
            raise DatasetAdapterError("unexpected external label")
        if case_id in case_ids:
            raise DatasetAdapterError("duplicate case id")
        case_ids.add(case_id)
        input_sha256 = _sha256(f"{dataset_id}\0{case_id}\0{text}")
        cases.append(
            ExecutionCase(
                dataset_id=dataset_id,
                case_id=case_id,
                requirement_text=text,
                input_sha256=input_sha256,
            )
        )
        labels[case_id] = label
    return DatasetProjection(dataset_id=dataset_id, execution_cases=tuple(cases), external_labels=labels)


def build_prompt_payload(case: ExecutionCase | Mapping[str, Any]) -> dict[str, str]:
    """Build the only input shape the execution path may receive.

    This boundary explicitly rejects dict inputs carrying a label-like key,
    including an accidental label reattachment before a provider call.
    """

    if isinstance(case, ExecutionCase):
        return {
            "case_id": case.case_id,
            "requirement_text": case.requirement_text,
            "input_sha256": case.input_sha256,
        }
    if not isinstance(case, Mapping):
        raise DatasetAdapterError("execution case must be an ExecutionCase or mapping")
    if _has_label_key(case):
        raise DatasetAdapterError("execution payload must not contain a label")
    expected = {"case_id", "requirement_text", "input_sha256"}
    if set(case) != expected:
        raise DatasetAdapterError("execution payload has an unexpected shape")
    input_sha256 = case["input_sha256"]
    if not isinstance(input_sha256, str) or not _SHA256_RE.fullmatch(input_sha256):
        raise DatasetAdapterError("execution payload has an invalid input hash")
    return {key: _require_string(case, key) for key in sorted(expected)}


def deterministic_selection_manifest(
    cases: Sequence[ExecutionCase],
    *,
    seed: str,
    count: int,
) -> dict[str, Any]:
    """Select cases deterministically without touching external labels or text."""

    if not isinstance(seed, str) or not seed:
        raise DatasetAdapterError("selection seed is required")
    if not isinstance(count, int) or count < 1 or count > len(cases):
        raise DatasetAdapterError("selection count is outside the available case range")
    if not cases:
        raise DatasetAdapterError("selection requires at least one case")
    dataset_ids = {case.dataset_id for case in cases}
    if len(dataset_ids) != 1:
        raise DatasetAdapterError("selection cases must belong to exactly one dataset")
    if len({case.case_id for case in cases}) != len(cases):
        raise DatasetAdapterError("selection cases must have unique case ids")
    ranked = sorted(
        cases,
        key=lambda case: (hashlib.sha256(f"{seed}\0{case.input_sha256}".encode()).hexdigest(), case.case_id),
    )
    selected = ranked[:count]
    unsigned = {
        "schema_version": "vego-multidataset-selection-v1",
        "dataset_id": next(iter(dataset_ids)),
        "seed": seed,
        "selection_rule": "SHA256(seed + NUL + input_sha256), ascending; first count",
        "selected_case_ids": [case.case_id for case in selected],
        "case_input_hashes": {case.case_id: case.input_sha256 for case in selected},
    }
    manifest = {**unsigned, "selection_sha256": hashlib.sha256(_canonical_json(unsigned)).hexdigest()}
    try:
        validate_named(manifest, "multidataset-selection-manifest-v1.schema.json")
    except SchemaError as exc:
        raise DatasetAdapterError(str(exc)) from exc
    return manifest


def validate_selection_manifest(
    manifest: Mapping[str, Any],
    cases: Sequence[ExecutionCase],
) -> tuple[str, ...]:
    """Validate a selection binding against the same label-free input cases."""

    try:
        validate_named(manifest, "multidataset-selection-manifest-v1.schema.json")
    except SchemaError as exc:
        raise DatasetAdapterError(str(exc)) from exc
    unsigned = dict(manifest)
    observed_hash = unsigned.pop("selection_sha256", None)
    if observed_hash != hashlib.sha256(_canonical_json(unsigned)).hexdigest():
        raise DatasetAdapterError("selection manifest hash binding mismatch")
    selected_case_ids = manifest["selected_case_ids"]
    expected = deterministic_selection_manifest(
        cases,
        seed=manifest["seed"],
        count=len(selected_case_ids),
    )
    comparable_keys = {"dataset_id", "seed", "selection_rule", "selected_case_ids", "case_input_hashes"}
    if any(manifest[key] != expected[key] for key in comparable_keys):
        raise DatasetAdapterError("selection manifest does not match the label-free cases")
    return tuple(selected_case_ids)


def build_external_label_evaluation(
    projection: DatasetProjection,
    execution_outputs: Sequence[Mapping[str, Any]],
) -> list[dict[str, str]]:
    """Join QuRE labels only after a case's execution output is hash-bound.

    This returns an association table, not Detector accuracy or a human-review
    verdict. It contains no requirement text or model output content.
    """

    by_case = {case.case_id: case for case in projection.execution_cases}
    seen: set[str] = set()
    output_by_case: dict[str, Mapping[str, Any]] = {}
    for row in execution_outputs:
        if not isinstance(row, Mapping):
            raise DatasetAdapterError("execution output must be a mapping")
        if _has_label_key(row):
            raise DatasetAdapterError("execution output must not contain an external label")
        case_id = _require_string(row, "case_id")
        if case_id not in by_case or case_id in seen:
            raise DatasetAdapterError("unknown or duplicate output case")
        expected_hash = by_case[case_id].input_sha256
        observed_hash = row.get("input_sha256")
        if observed_hash != expected_hash:
            raise DatasetAdapterError("execution output input hash does not match")
        seen.add(case_id)
        output_by_case[case_id] = row
    if seen != set(by_case):
        raise DatasetAdapterError("execution output cases do not match the projection")
    return [
        {
            "case_id": case.case_id,
            "input_sha256": case.input_sha256,
            "external_requirements_quality_label": projection.external_labels[case.case_id],
            "label_role": "NOT_DIRECT_ALERT_GROUND_TRUTH",
        }
        for case in projection.execution_cases
    ]
