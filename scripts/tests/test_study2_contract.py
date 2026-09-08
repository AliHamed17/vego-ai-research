from __future__ import annotations

import asyncio
import importlib.util
import json
import sys
from pathlib import Path

import jsonschema
import pytest

ROOT = Path(__file__).resolve().parents[2]


def load_module():
    path = ROOT / "scripts" / "study2_vego_off_baseline.py"
    spec = importlib.util.spec_from_file_location("study2_vego_off_baseline", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def valid_payload(case_id: str = "01") -> dict:
    return {
        "schema_version": "study2-condition-output-v1",
        "condition": "VEGO_AI_OFF",
        "skill_version": "off-baseline-v1",
        "case_id": case_id,
        "existing_mapping": [],
        "coverage_summary": {"satisfied": 0, "partially_satisfied": 0, "not_satisfied": 0},
        "uncovered_fragments": [],
    }


def test_off_payload_requires_strict_shared_schema():
    module = load_module()
    result = module.normalise("01", valid_payload())
    assert result["schema_complete"] is True
    assert result["condition"] == "VEGO_AI_OFF"
    with pytest.raises(module.OutputSchemaError):
        module.normalise("01", {k: v for k, v in valid_payload().items() if k != "existing_mapping"})
    with pytest.raises(module.OutputSchemaError):
        module.normalise("01", {**valid_payload(), "unexpected": 1})
    with pytest.raises(module.OutputSchemaError):
        module.normalise("01", {**valid_payload(), "case_id": "02"})


def test_off_prompt_declares_condition_and_schema():
    module = load_module()
    prompt = module.off_prompt("01", "fixture model", "fixture domain", "UML")
    assert '"schema_version": "study2-condition-output-v1"' in prompt["system"]
    assert '"condition": "VEGO_AI_OFF"' in prompt["system"]


def test_off_runner_propagates_malformed_output_instead_of_coercing_to_empty():
    module = load_module()
    with pytest.raises(module.OutputSchemaError):
        module.normalise("01", {"case_id": "01"})


def test_legacy_off_runner_rejects_any_client():
    module = load_module()
    with pytest.raises(RuntimeError, match="controlled fixture runner"):
        asyncio.run(
            module.run_off_baseline(
                object(),
                [{"case_id": "01", "case_model": "a"}, {"case_id": "01", "case_model": "b"}],
                "domain",
                "UML",
            )
        )


def test_legacy_off_runner_cannot_emit_detector_metadata():
    module = load_module()
    with pytest.raises(RuntimeError, match="controlled fixture runner"):
        asyncio.run(
            module.run_off_baseline(
                object(),
                [{"case_id": "01", "case_model": "fixture"}],
                "domain",
                "UML",
            )
        )


def test_on_summary_rejects_missing_arrays_instead_of_reporting_zero(tmp_path: Path):
    experiment = importlib.util.spec_from_file_location(
        "study2_on_off_experiment", ROOT / "scripts" / "study2_on_off_experiment.py"
    )
    assert experiment and experiment.loader
    module = importlib.util.module_from_spec(experiment)
    sys.modules[experiment.name] = module
    experiment.loader.exec_module(module)
    (tmp_path / "compliance_vectors.json").write_text(
        '{"01": {"coverage_summary": {}}}', encoding="utf-8"
    )
    (tmp_path / "uncovered_fragments.json").write_text(
        '{"01": {}}', encoding="utf-8"
    )
    with pytest.raises(ValueError, match="schema"):
        module.summarise_on(tmp_path)


def test_comparison_schema_freezes_fixture_and_off_detector_boundary():
    schema_path = ROOT / "schemas" / "study2-on-off-comparison-v1.schema.json"
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    jsonschema.Draft202012Validator.check_schema(schema)
    assert schema["properties"]["provider_calls"]["const"] == 0
    assert schema["properties"]["detector_v1"]["properties"]["off_denominator"]["const"] == "NOT_APPLICABLE"
    assert schema["properties"]["detector_v1"]["properties"]["detector_v1_executed"]["const"] is False
    assert schema["properties"]["per_case_comparison"]["items"]["properties"]["comparability"]["const"] == "NOT_COMPARABLE_AS_QUALITY"
