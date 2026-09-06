"""Contract tests for the separately preregistered Study 2A comparison."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

from study2_vego_ai_on_off import (  # noqa: E402
    build_prompt_difference_receipt,
    compare_config_parity,
    detector_applicability,
    detector_signal_context,
    deterministic_run_id,
    fake_run,
    load_condition_config,
    static_call_bounds,
    validate_condition_config,
    validate_condition_schema,
    validate_manifest_schema,
    validate_on_lifecycle,
    validate_reference_separation,
)

CONFIG_DIR = ROOT / "configs" / "study2"


def test_on_and_off_configs_are_valid_and_share_frozen_corpus() -> None:
    on = load_condition_config(CONFIG_DIR / "vego_ai_on.json")
    off = load_condition_config(CONFIG_DIR / "vego_ai_off.json")
    validate_condition_config(on, expected_condition="VEGO_AI_ON")
    validate_condition_config(off, expected_condition="VEGO_AI_OFF")
    assert on["corpus"] == off["corpus"]
    assert on["fairness"] == off["fairness"]
    assert on["provider"] == off["provider"]
    assert on["condition_id"] != off["condition_id"]


def test_parity_rejects_hidden_provider_or_corpus_changes() -> None:
    on = load_condition_config(CONFIG_DIR / "vego_ai_on.json")
    off = load_condition_config(CONFIG_DIR / "vego_ai_off.json")
    assert compare_config_parity(on, off)["status"] == "PASS"
    altered = json.loads(json.dumps(off))
    altered["provider"]["model"] = "hidden-model"
    with pytest.raises(ValueError, match="provider|parity"):
        compare_config_parity(on, altered)


@pytest.mark.parametrize(
    ("section", "field", "value"),
    [
        ("corpus", "runtime_archive_sha256", "0" * 64),
        ("corpus", "amendment_manifest_path", "docs/other.json"),
        ("output", "root", "external_data/study2a/other/"),
        ("prompts", "output_objective", "different_objective"),
    ],
)
def test_frozen_contract_fields_cannot_drift(section: str, field: str, value: str) -> None:
    on = load_condition_config(CONFIG_DIR / "vego_ai_on.json")
    altered = json.loads(json.dumps(on))
    altered[section][field] = value
    with pytest.raises(ValueError):
        validate_condition_config(altered, expected_condition="VEGO_AI_ON")


def test_runtime_file_manifest_is_exactly_five_unique_frozen_rows() -> None:
    on = load_condition_config(CONFIG_DIR / "vego_ai_on.json")
    altered = json.loads(json.dumps(on))
    altered["corpus"]["runtime_files"] = altered["corpus"]["runtime_files"][:-1]
    with pytest.raises(ValueError, match="runtime_files"):
        validate_condition_config(altered, expected_condition="VEGO_AI_ON")


def test_off_condition_prohibits_vego_routes_and_detector() -> None:
    off = load_condition_config(CONFIG_DIR / "vego_ai_off.json")
    validate_condition_config(off, expected_condition="VEGO_AI_OFF")
    assert off["orchestration_mode"] == "single_model_no_vego"
    assert off["vego_controls"] == {
        "orchestrator": "FORBIDDEN",
        "qa_registry": "FORBIDDEN",
        "feedback_loop": "FORBIDDEN",
        "detector_input": "FORBIDDEN",
    }
    assert detector_applicability(off) == "NOT_APPLICABLE"
    assert off["implementation_sources"] == []


def test_on_condition_exposes_detector_only_for_on() -> None:
    on = load_condition_config(CONFIG_DIR / "vego_ai_on.json")
    assert detector_applicability(on) == "AVAILABLE_ON_ONLY"


def test_prompt_difference_receipt_names_only_orchestration_difference(tmp_path: Path) -> None:
    on_prompt = tmp_path / "on.md"
    off_prompt = tmp_path / "off.md"
    on_prompt.write_text("same objective\nON decomposition\n", encoding="utf-8")
    off_prompt.write_text("same objective\nOFF direct call\n", encoding="utf-8")
    receipt = build_prompt_difference_receipt(
        on_sources=[on_prompt], off_sources=[off_prompt],
        allowed_difference="orchestration only",
    )
    assert receipt["status"] == "PASS"
    assert receipt["allowed_difference"] == "orchestration only"
    assert len(receipt["on"]) == len(receipt["off"]) == 1
    assert receipt["text_difference_present"] is True


def test_run_identity_is_stable_and_condition_specific() -> None:
    kwargs = {"study_id": "STUDY2A", "corpus_id": "text2uml_airtravel_253b26dc", "seed": 20260906}
    assert deterministic_run_id("VEGO_AI_ON", **kwargs) == deterministic_run_id("VEGO_AI_ON", **kwargs)
    assert deterministic_run_id("VEGO_AI_ON", **kwargs) != deterministic_run_id("VEGO_AI_OFF", **kwargs)


def test_run_identity_is_stable_across_processes() -> None:
    code = (
        "from study2_vego_ai_on_off import deterministic_run_id; "
        "print(deterministic_run_id('VEGO_AI_ON', study_id='STUDY2A', "
        "corpus_id='text2uml_airtravel_253b26dc', seed=20260906))"
    )
    env = dict(os.environ)
    env["PYTHONPATH"] = str(ROOT / "scripts")
    first = subprocess.check_output([sys.executable, "-c", code], text=True, env=env).strip()
    second = subprocess.check_output([sys.executable, "-c", code], text=True, env=env).strip()
    assert first == second


def test_static_bounds_keep_on_and_off_denominators_separate() -> None:
    bounds = static_call_bounds(4)
    assert bounds["on"] == {"minimum": 16, "maximum": 326}
    assert bounds["off"] == {"minimum": 4, "maximum": 4}
    assert bounds["cost_status"] == "NOT_MEASURED_PREPARATION"


@pytest.mark.parametrize("case_count", [0, 1, 4])
def test_static_bounds_scale_deterministically(case_count: int) -> None:
    bounds = static_call_bounds(case_count)
    assert bounds["on"]["minimum"] == 4 + 3 * case_count
    assert bounds["on"]["maximum"] == 82 + 61 * case_count
    assert bounds["off"] == {"minimum": case_count, "maximum": case_count}


def test_fake_runs_isolate_condition_events_and_never_use_network() -> None:
    on = load_condition_config(CONFIG_DIR / "vego_ai_on.json")
    off = load_condition_config(CONFIG_DIR / "vego_ai_off.json")
    cases = {"01": "case-one", "02": "case-two", "03": "case-three", "04": "case-four"}
    on_result = fake_run(on, cases)
    off_result = fake_run(off, cases)
    assert on_result["condition_id"] == "VEGO_AI_ON"
    assert off_result["condition_id"] == "VEGO_AI_OFF"
    assert on_result["run_id"] != off_result["run_id"]
    assert on_result["provider_calls"] == off_result["provider_calls"] == 0
    assert on_result["external_network_calls"] == off_result["external_network_calls"] == 0
    assert not set(on_result["event_ids"]) & set(off_result["event_ids"])


def test_reference_paths_are_rejected_when_visible_or_unsafe(tmp_path: Path) -> None:
    runtime = tmp_path / "runtime"
    runtime.mkdir()
    reference = tmp_path / "reference"
    reference.mkdir()
    assert validate_reference_separation(runtime, reference) is True
    with pytest.raises(ValueError, match="reference"):
        validate_reference_separation(runtime, runtime / "reference_only")
    with pytest.raises(ValueError, match="absolute"):
        validate_reference_separation(runtime, Path("C:/private/reference"))


def test_fake_run_rejects_provider_enabled_or_wrong_case_count() -> None:
    on = load_condition_config(CONFIG_DIR / "vego_ai_on.json")
    bad = json.loads(json.dumps(on))
    bad["provider"]["execution_enabled"] = True
    with pytest.raises(ValueError, match="provider"):
        fake_run(bad, {"01": "only"})


def test_condition_and_manifest_schema_validation_is_explicit() -> None:
    on = load_condition_config(CONFIG_DIR / "vego_ai_on.json")
    validate_condition_schema(on)
    from study2_vego_ai_on_off import build_manifest

    manifest = build_manifest()
    validate_manifest_schema(manifest)
    assert manifest["status"] == "PREPARATION_ONLY_NO_EXPERIMENT"
    malformed = json.loads(json.dumps(manifest))
    malformed.pop("conditions")
    with pytest.raises(ValueError, match="manifest schema"):
        validate_manifest_schema(malformed)


def _valid_on_events() -> list[dict[str, str]]:
    return [
        {"run_id": "run-1", "episode_id": "episode-a", "event_type": "QUESTION_EMITTED", "question_id": "q-a"},
        {"run_id": "run-1", "episode_id": "episode-a", "event_type": "ANSWER_RECEIVED", "question_id": "q-a"},
        {"run_id": "run-1", "episode_id": "episode-a", "event_type": "CONVERGED"},
        {"run_id": "run-1", "episode_id": "episode-b", "event_type": "QUESTION_EMITTED", "question_id": "q-b"},
        {"run_id": "run-1", "episode_id": "episode-b", "event_type": "ANSWER_RECEIVED", "question_id": "q-b"},
        {"run_id": "run-1", "episode_id": "episode-b", "event_type": "TERMINATED_MAX_ROUNDS"},
    ]


def test_on_lifecycle_accepts_complete_multi_episode_stream() -> None:
    result = validate_on_lifecycle(_valid_on_events())
    assert result["status"] == "PASS"
    assert result["episode_count"] == 2
    assert result["question_count"] == 2


@pytest.mark.parametrize(
    "mutator",
    [
        lambda events: events[:-1],  # episode b has no terminal event
        lambda events: events + [{"run_id": "run-1", "episode_id": "episode-a", "event_type": "CONTEXT"}],
        lambda events: events[:1] + [{"run_id": "run-1", "episode_id": "episode-a", "event_type": "CONVERGED"}],
        lambda events: [{"run_id": "run-1", "episode_id": "episode-a", "event_type": "CONVERGED"}],
        lambda events: [{"run_id": "run-1", "episode_id": "episode-a", "event_type": "QUESTION_EMITTED", "question_id": "q-a"},
                        {"run_id": "run-1", "episode_id": "episode-b", "event_type": "ANSWER_RECEIVED", "question_id": "q-a"},
                        {"run_id": "run-1", "episode_id": "episode-a", "event_type": "CONVERGED"}],
    ],
)
def test_on_lifecycle_malformed_streams_fail_closed(mutator) -> None:
    with pytest.raises(ValueError):
        validate_on_lifecycle(mutator(_valid_on_events()))


def test_on_lifecycle_rejects_mixed_run_and_zero_question_episode() -> None:
    mixed = _valid_on_events()
    mixed[-1] = dict(mixed[-1], run_id="run-2")
    with pytest.raises(ValueError, match="one run_id"):
        validate_on_lifecycle(mixed)
    with pytest.raises(ValueError, match="no question"):
        validate_on_lifecycle([{"run_id": "run-1", "episode_id": "episode-a", "event_type": "CONTEXT"},
                               {"run_id": "run-1", "episode_id": "episode-a", "event_type": "CONVERGED"}])


def test_detector_c1_boundary_remains_context_only() -> None:
    assert detector_signal_context("C1_MAPPING_CERTAINTY", 0.699)["triggering"] is False
    assert detector_signal_context("C1_MAPPING_CERTAINTY", 0.7)["classification"] == "CONTEXT_ONLY"
    for code in ("S5_REPEATED_CLARIFICATION", "S8_FOLLOW_UP", "S9_QUESTION_DENSITY"):
        assert detector_signal_context(code)["triggering"] is False


def test_fake_runs_are_deterministic_under_concurrency() -> None:
    on = load_condition_config(CONFIG_DIR / "vego_ai_on.json")
    cases = {case_id: f"ENGINEERING_FIXTURE_ONLY::{case_id}" for case_id in on["corpus"]["case_ids"]}
    with ThreadPoolExecutor(max_workers=4) as pool:
        results = list(pool.map(lambda _: fake_run(on, cases), range(4)))
    assert {result["run_id"] for result in results} == {results[0]["run_id"]}
    assert all(result["provider_calls"] == 0 for result in results)


def test_preparation_module_has_no_provider_or_model_download_path() -> None:
    source = (ROOT / "scripts" / "study2_vego_ai_on_off.py").read_text(encoding="utf-8")
    assert "from openai" not in source
    assert "import openai" not in source
    assert "huggingface" not in source.lower()
    assert "requests" not in source


def test_cli_dry_run_and_fake_mode_are_explicitly_non_executing() -> None:
    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "study2_vego_ai_on_off.py"), "--dry-run", "--fake-run"],
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(result.stdout)
    assert payload["mode"] == "DRY_RUN"
    assert payload["fake_run_parity"]["status"] == "ENGINEERING_FIXTURE_ONLY"
    rejected = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "study2_vego_ai_on_off.py"), "--execute"],
        capture_output=True,
        text=True,
    )
    assert rejected.returncode != 0
    assert "not part" in rejected.stderr


def test_tracked_manifest_uses_canonical_lf_bytes() -> None:
    manifest_bytes = (ROOT / "docs/research/phd-proposal/study2-vego-ai-on-off-manifest.json").read_bytes()
    assert b"\r\n" not in manifest_bytes
    assert manifest_bytes.endswith(b"\n")
