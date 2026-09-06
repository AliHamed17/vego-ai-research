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

    class BadClient:
        async def call(self, prompt, *, label):
            return {"case_id": label.split("/")[1]}

    with pytest.raises(module.OutputSchemaError):
        asyncio.run(
            module.run_off_baseline(
                BadClient(),
                [{"case_id": "01", "case_model": "fixture"}],
                "domain",
                "UML",
            )
        )


def test_off_runner_rejects_duplicate_case_ids():
    module = load_module()

    class NeverCalled:
        async def call(self, prompt, *, label):
            raise AssertionError("duplicate case validation should happen before calls")

    with pytest.raises(module.OutputSchemaError, match="unique"):
        asyncio.run(
            module.run_off_baseline(
                NeverCalled(),
                [{"case_id": "01", "case_model": "a"}, {"case_id": "01", "case_model": "b"}],
                "domain",
                "UML",
            )
        )


def test_off_metadata_keeps_detector_not_applicable():
    module = load_module()

    class GoodClient:
        async def call(self, prompt, *, label):
            return valid_payload(label.split("/")[1])

    result = asyncio.run(
        module.run_off_baseline(
            GoodClient(),
            [{"case_id": "01", "case_model": "fixture"}],
            "domain",
            "UML",
        )
    )
    assert result["detector_v1_denominator"] == "NOT_APPLICABLE"
    assert result["episodes"] == 0


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
