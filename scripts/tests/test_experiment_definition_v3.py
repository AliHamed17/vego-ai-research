"""ExperimentDefinition-v3 schema constraints.

Constraints under test: the v3 example is a design-only artifact (no runner,
no evaluator, no metric observations, proposal evidence class); the arms
array requires at least two arms with closed roles; v2's baseline/comparator
pair is not admitted by v3; artifact links stay portable. Nothing here is
empirical evidence of any outcome (EXP-005 0/24).
"""

from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any

import jsonschema
import pytest
from referencing import Registry, Resource

ROOT = Path(__file__).resolve().parents[2]
SCHEMA_PATH = ROOT / "schemas" / "experiment-definition-v3.schema.json"
EXAMPLE_PATH = ROOT / "schemas" / "examples" / "experiment-definition-v3.valid.json"

_SCHEMA_REGISTRY = Registry().with_resources(
    [
        (schema["$id"], Resource.from_contents(schema))
        for schema in (
            json.loads(path.read_text(encoding="utf-8"))
            for path in sorted((ROOT / "schemas").glob("*.schema.json"))
        )
        if "$id" in schema
    ]
)


def _validator() -> jsonschema.Draft202012Validator:
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    return jsonschema.Draft202012Validator(schema, registry=_SCHEMA_REGISTRY)


def _example() -> dict[str, Any]:
    return json.loads(EXAMPLE_PATH.read_text(encoding="utf-8"))


def _errors(record: dict[str, Any]) -> list[str]:
    return [error.message for error in _validator().iter_errors(record)]


def test_valid_example_passes() -> None:
    assert _errors(_example()) == []


def test_example_is_design_only() -> None:
    record = _example()
    assert record["definitionStatus"] == "future_study"
    assert record["evidenceClass"] == "proposal"
    assert record["runner"] is None
    assert record["evaluator"] is None
    assert record["metricDefinitionIds"] == []
    assert "0/24" in record["claimBoundary"]


def test_example_expresses_the_four_c4_arms() -> None:
    arms = {arm["armId"]: arm["role"] for arm in _example()["arms"]}
    assert set(arms) == {"ai_only", "human_only", "ordinary_hitl", "governed"}
    assert arms["governed"] == "treatment"


def test_fewer_than_two_arms_is_rejected() -> None:
    record = _example()
    record["arms"] = record["arms"][:1]
    assert _errors(record)


def test_unknown_arm_role_is_rejected() -> None:
    record = _example()
    record["arms"][0]["role"] = "winner"
    assert _errors(record)


def test_arm_requires_arm_id_description_and_role() -> None:
    for missing in ("armId", "description", "role"):
        record = _example()
        del record["arms"][0][missing]
        assert _errors(record), missing


def test_missing_arms_is_rejected() -> None:
    record = _example()
    del record["arms"]
    assert _errors(record)


def test_v2_baseline_comparator_pair_is_not_admitted() -> None:
    record = _example()
    record["baseline"] = "ai_only"
    record["comparator"] = "governed"
    assert _errors(record)


def test_schema_version_is_pinned() -> None:
    record = _example()
    record["schemaVersion"] = "ExperimentDefinition-v2"
    assert _errors(record)


def test_windows_artifact_links_are_rejected() -> None:
    record = _example()
    record["artifactLinks"] = ["C:\\Users\\example\\evidence.json"]
    assert _errors(record)


def test_comparison_spec_ref_is_enforced() -> None:
    record = _example()
    record["comparisonSpec"] = {"comparisonFamily": "empirical"}
    assert _errors(record)


def test_mutations_do_not_leak_between_cases() -> None:
    original = _example()
    mutated = copy.deepcopy(original)
    mutated["arms"][0]["role"] = "winner"
    assert original["arms"][0]["role"] != "winner"
    assert _errors(original) == []


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-q"]))
