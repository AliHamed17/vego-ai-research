"""Offline contract and fixture harness for VEGO-AI Study 2A.

This module deliberately has no provider, SDK, credential, or network import.
It validates the frozen ON/OFF comparison contract and can produce a
deterministic *engineering fixture* receipt.  A future provider-backed runner
must be a separately authorized adapter; ``fake_run`` is not an experiment and
does not read corpus content.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from collections.abc import Iterable
from pathlib import Path
from typing import Any

import jsonschema

ROOT = Path(__file__).resolve().parents[1]
CONFIG_DIR = ROOT / "configs" / "study2"
MANIFEST_PATH = ROOT / "docs" / "research" / "phd-proposal" / "study2-vego-ai-on-off-manifest.json"
SCHEMA_PATH = ROOT / "schemas" / "study2a-vego-ai-on-off-v1.schema.json"
SCHEMA_VERSION = "study2a-vego-ai-on-off-v1"
RUN_SEED = 20260906
ALLOWED_DIFFERENCE_PREFIXES = {
    "condition_id",
    "condition_label",
    "orchestration_mode",
    "vego_controls",
    "detector_applicability",
    "implementation_sources",
    "output.root",
    "output.event_log",
    "prompts.sources",
}
REQUIRED_TOP_LEVEL = {
    "schema_version",
    "study_id",
    "condition_id",
    "condition_label",
    "orchestration_mode",
    "provider",
    "corpus",
    "fairness",
    "vego_controls",
    "detector_applicability",
    "output",
    "prompts",
    "claims",
    "references",
    "model_parameters",
    "output_schema",
    "validation",
    "retention",
    "implementation_sources",
}

EXPECTED_RUNTIME_FILES = (
    {
        "path": "domain_description/description.md",
        "bytes": 1477,
        "sha256": "96bc8a6fbf2c2fdd93592fdbf6fac7c2b9db403494fe2d5a45e0a2bcbf0167e2",
        "role": "domain_description",
    },
    {
        "path": "candidate_models/01_result_one_claude-sonnet-4-6.txt",
        "bytes": 1248,
        "sha256": "240b034834e383b9844e9a3e9796f6be9b3d47fc95de6606ed022d278d751f91",
        "role": "candidate_model",
    },
    {
        "path": "candidate_models/02_result_one_codestral-2508.txt",
        "bytes": 1272,
        "sha256": "08399ca9432c1399f3f9784d34741314e4d39e40307a6efb14fa92a1c138b1d6",
        "role": "candidate_model",
    },
    {
        "path": "candidate_models/03_result_one_deepseek-chat.txt",
        "bytes": 1324,
        "sha256": "ee4d689d59c9ce3a5e8ff385747641954bd4821f2efeb18e581dcd1d5441d20a",
        "role": "candidate_model",
    },
    {
        "path": "candidate_models/04_result_one_gemini-2.5-flash.txt",
        "bytes": 1231,
        "sha256": "1c3d15eac71fcaab138857dbbc7153833b3df55ab57925ac756a79dc28dc847a",
        "role": "candidate_model",
    },
)
EXPECTED_MODEL_PARAMETERS = {"temperature": 0.0, "top_p": 1.0, "seed": RUN_SEED}
EXPECTED_OUTPUT_SCHEMA = {"id": "structured_uml_review_v1", "validation": "strict"}
EXPECTED_VALIDATION = {"schema": "strict", "parseability": "strict", "unknown_fields": "reject"}
EXPECTED_RETENTION = {
    "raw_content": "PRIVATE_IGNORED_ONLY",
    "event_logs": "PRIVATE_IGNORED_ONLY",
    "tracked_outputs": "SAFE_METADATA_ONLY",
}
EXPECTED_AMENDMENT_MANIFEST_PATH = (
    "docs/research/phd-proposal/text2uml-airtravel/amendment-manifest-v1.0.2.json"
)
EXPECTED_AMENDMENT_MANIFEST_SHA256 = "bd2b7f03585582ff7591d21795fbd3ed4701244d66d26221683520238c2dead2"
EXPECTED_RUNTIME_ARCHIVE_SHA256 = "e37baecd20a0c84eb1d9b87b3b78a23bc4b4eb8a9824ad3086dc30aa35fdd31f"
EXPECTED_CASE_MANIFEST_SHA256 = "7ef0c1308ad359a17c2a8a87c008e296f28a58eadd13e82f2e098c44a5e7dbb0"
EXPECTED_ON_IMPLEMENTATION_SOURCES = [
    "VEGO-AI/framework/orchestrator.py",
    "VEGO-AI/framework/agent1_language_advisor.py",
    "VEGO-AI/framework/agent2_domain_advisor.py",
    "VEGO-AI/framework/agent3_model_inspector.py",
    "VEGO-AI/framework/agent4_variability_explorer.py",
]
EXPECTED_PROMPT_DIFFERENCE_POLICY = (
    "ON decomposes the same output objective into the frozen four-agent orchestration; "
    "OFF uses one direct call per case. No other difference is permitted."
)
EXPECTED_REFERENCE_POLICY = {
    "runtime_visible": [],
    "excluded_paths": [
        "reference_only/plantuml.txt",
        "reference_only/plantuml_adjusted.txt",
        "reference_only/extramaterial/AirTravel.cd4a",
    ],
    "status": "EXCLUDED_FROM_RUNTIME",
}


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _require_relative_path(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value or Path(value).is_absolute():
        raise ValueError(f"{field} must be a non-empty repository-relative path")
    normalized = value.replace("\\", "/")
    parts = Path(normalized).parts
    if any(part in {"", ".", ".."} for part in parts):
        raise ValueError(f"{field} contains unsafe traversal")
    return normalized


def _load_schema() -> dict[str, Any]:
    try:
        value = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"Study 2 schema is unavailable: {SCHEMA_PATH}") from exc
    if not isinstance(value, dict):
        raise ValueError("Study 2 schema must be a JSON object")
    return value


def validate_condition_schema(config: dict[str, Any]) -> None:
    """Validate the structural JSON Schema before semantic checks."""

    schema = _load_schema()
    condition_schema = schema.get("$defs", {}).get("condition")
    if not isinstance(condition_schema, dict):
        raise ValueError("Study 2 schema has no condition definition")
    # Validate the definition as a standalone schema while retaining the
    # parent definitions used by its nested ``$ref`` entries.
    standalone = dict(condition_schema)
    standalone["$defs"] = schema.get("$defs", {})
    errors = sorted(jsonschema.Draft202012Validator(standalone).iter_errors(config), key=str)
    if errors:
        raise ValueError(f"condition schema validation failed: {errors[0].message}")


def validate_manifest_schema(manifest: dict[str, Any]) -> None:
    """Validate the complete machine manifest against the tracked schema."""

    schema = _load_schema()
    errors = sorted(jsonschema.Draft202012Validator(schema).iter_errors(manifest), key=str)
    if errors:
        raise ValueError(f"Study 2 manifest schema validation failed: {errors[0].message}")


def load_condition_config(path: Path) -> dict[str, Any]:
    """Load one tracked condition profile without touching external inputs."""

    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot load Study 2 condition config: {path}") from exc
    if not isinstance(value, dict):
        raise ValueError("condition config must be a JSON object")
    missing = REQUIRED_TOP_LEVEL - set(value)
    if missing:
        raise ValueError(f"condition config missing fields: {sorted(missing)}")
    if value["schema_version"] != SCHEMA_VERSION:
        raise ValueError("unsupported Study 2 condition schema")
    validate_condition_schema(value)
    return value


def validate_condition_config(config: dict[str, Any], *, expected_condition: str) -> None:
    """Fail closed on fairness, containment, or condition-definition drift."""

    if not isinstance(config, dict):
        raise ValueError("condition config must be an object")
    if config.get("study_id") != "STUDY2A":
        raise ValueError("Study 2A study_id is required")
    if config.get("condition_id") != expected_condition:
        raise ValueError("condition id does not match expected condition")
    if config.get("condition_id") not in {"VEGO_AI_ON", "VEGO_AI_OFF"}:
        raise ValueError("unknown Study 2 condition")
    provider = config.get("provider")
    corpus = config.get("corpus")
    fairness = config.get("fairness")
    output = config.get("output")
    controls = config.get("vego_controls")
    prompts = config.get("prompts")
    for name, value in (("provider", provider), ("corpus", corpus), ("fairness", fairness),
                        ("output", output), ("vego_controls", controls), ("prompts", prompts)):
        if not isinstance(value, dict):
            raise ValueError(f"{name} must be an object")
    if config["condition_id"] == "VEGO_AI_ON":
        if config.get("orchestration_mode") != "full_vego_ai_orchestrator":
            raise ValueError("ON must use the full VEGO-AI orchestrator")
        if config.get("detector_applicability") != "AVAILABLE_ON_ONLY":
            raise ValueError("Detector-v1 is available only for ON")
    else:
        if config.get("orchestration_mode") != "single_model_no_vego":
            raise ValueError("OFF must use the named single-model baseline")
        if config.get("detector_applicability") != "NOT_APPLICABLE":
            raise ValueError("Detector-v1 must be NOT_APPLICABLE for OFF")
        expected_controls = {
            "orchestrator": "FORBIDDEN",
            "qa_registry": "FORBIDDEN",
            "feedback_loop": "FORBIDDEN",
            "detector_input": "FORBIDDEN",
        }
        if controls != expected_controls:
            raise ValueError("OFF condition exposes a VEGO control")
    if (
        provider.get("name") != "openai"
        or provider.get("model") != "gpt-5.6-luna"
        or provider.get("api_mode") != "chat.completions"
    ):
        raise ValueError("provider/model must remain the frozen Study 1-compatible pair")
    if provider.get("execution_enabled") is not False or provider.get("network_allowed") is not False:
        raise ValueError("provider execution and network must be disabled in preparation")
    if provider.get("external_calls_forbidden") is not True:
        raise ValueError("external provider calls must be forbidden")
    if config.get("model_parameters") != EXPECTED_MODEL_PARAMETERS:
        raise ValueError("model parameters must be identical and frozen")
    if config.get("output_schema") != EXPECTED_OUTPUT_SCHEMA:
        raise ValueError("output schema must be identical and frozen")
    if config.get("validation") != EXPECTED_VALIDATION:
        raise ValueError("validation rules must be identical and strict")
    if config.get("retention") != EXPECTED_RETENTION:
        raise ValueError("retention policy must be identical and private")
    implementation_sources = config.get("implementation_sources")
    if not isinstance(implementation_sources, list):
        raise ValueError("implementation_sources must be an explicit list")
    if config["condition_id"] == "VEGO_AI_OFF" and implementation_sources:
        raise ValueError("OFF baseline must not import or route through VEGO implementation")
    required_corpus = {
        "setting_id": "cd_airtravel",
        "corpus_id": "text2uml_airtravel_253b26dc",
        "N": 4,
        "case_ids": ["01", "02", "03", "04"],
        "case_manifest_sha256": EXPECTED_CASE_MANIFEST_SHA256,
    }
    for key, expected in required_corpus.items():
        if corpus.get(key) != expected:
            raise ValueError(f"corpus field {key} is not frozen")
    if corpus.get("amendment_manifest_path") != EXPECTED_AMENDMENT_MANIFEST_PATH:
        raise ValueError("amendment manifest path is not the frozen AirTravel manifest")
    if corpus.get("amendment_manifest_sha256") != EXPECTED_AMENDMENT_MANIFEST_SHA256:
        raise ValueError("amendment manifest hash is not the frozen AirTravel hash")
    if corpus.get("runtime_archive_sha256") != EXPECTED_RUNTIME_ARCHIVE_SHA256:
        raise ValueError("runtime archive hash is not the frozen AirTravel hash")
    _require_relative_path(corpus.get("amendment_manifest_path"), "amendment_manifest_path")
    for hash_field in ("amendment_manifest_sha256", "runtime_archive_sha256"):
        value = corpus.get(hash_field)
        if not isinstance(value, str) or len(value) != 64 or any(c not in "0123456789abcdef" for c in value):
            raise ValueError(f"{hash_field} must be a lowercase SHA-256")
    runtime_files = corpus.get("runtime_files")
    expected_runtime = [dict(row) for row in EXPECTED_RUNTIME_FILES]
    if runtime_files != expected_runtime:
        raise ValueError("runtime_files must match the frozen five-file manifest exactly")
    if len(runtime_files) != 5 or len({row["path"] for row in runtime_files}) != 5:
        raise ValueError("runtime_files must contain five unique paths")
    if sum(row["role"] == "domain_description" for row in runtime_files) != 1:
        raise ValueError("runtime_files require one domain description")
    if sum(row["role"] == "candidate_model" for row in runtime_files) != 4:
        raise ValueError("runtime_files require four candidate models")
    if not all(
        isinstance(row["bytes"], int) and row["bytes"] > 0
        and isinstance(row["sha256"], str) and len(row["sha256"]) == 64
        and row["sha256"] == row["sha256"].lower()
        for row in runtime_files
    ):
        raise ValueError("runtime file byte lengths and hashes must be valid")
    expected_fairness = {
        "max_completion_tokens": 16384,
        "request_timeout_seconds": 180,
        "run_timeout_seconds": 3600,
        "max_retries": 3,
        "max_concurrent_cases": 2,
        "call_cap": 326,
        "cost_cap_usd": 10.0,
        "replicates": 1,
        "condition_order": ["VEGO_AI_ON", "VEGO_AI_OFF"],
    }
    if fairness != expected_fairness:
        raise ValueError("fairness configuration differs between frozen profiles")
    root = _require_relative_path(output.get("root"), "output.root")
    event_log = _require_relative_path(output.get("event_log"), "output.event_log")
    root_path = Path(root.rstrip("/"))
    event_path = Path(event_log)
    try:
        event_path.relative_to(root_path)
    except ValueError as exc:
        raise ValueError("condition event log is not contained by its private root") from exc
    expected_root = f"external_data/study2a/{'vego-ai-on' if config['condition_id'] == 'VEGO_AI_ON' else 'vego-ai-off'}/"
    if not root.endswith("/") or root != expected_root:
        raise ValueError("condition output is not contained by its private root")
    if output.get("raw_content_policy") != "PRIVATE_IGNORED_ONLY":
        raise ValueError("raw content policy must remain private")
    if not isinstance(prompts.get("sources"), list) or not prompts["sources"]:
        raise ValueError("prompt sources must be enumerated")
    if prompts.get("output_objective") != EXPECTED_OUTPUT_SCHEMA["id"]:
        raise ValueError("output objective must remain frozen")
    if prompts.get("difference_policy") != EXPECTED_PROMPT_DIFFERENCE_POLICY:
        raise ValueError("prompt difference policy must remain frozen")
    for source in prompts["sources"]:
        if not isinstance(source, dict):
            raise ValueError("prompt source must be an object")
        _require_relative_path(source.get("path"), "prompt source path")
        if not isinstance(source.get("sha256"), str) or len(source["sha256"]) != 64:
            raise ValueError("prompt source hash is required")
        source_path = ROOT / source["path"]
        if not source_path.is_file() or sha256_file(source_path) != source["sha256"]:
            raise ValueError(f"prompt source hash/path mismatch: {source['path']}")
    claims = config.get("claims")
    if not isinstance(claims, dict) or not isinstance(claims.get("forbidden"), list):
        raise ValueError("forbidden claims must be explicit")
    references = config.get("references")
    if references != EXPECTED_REFERENCE_POLICY:
        raise ValueError("reference-model exposure policy must remain excluded")
    if config["condition_id"] == "VEGO_AI_ON":
        if implementation_sources != EXPECTED_ON_IMPLEMENTATION_SOURCES:
            raise ValueError("ON implementation sources must enumerate the protected orchestrator and four agents")


def _flatten(value: Any, prefix: str = "") -> dict[str, Any]:
    result: dict[str, Any] = {}
    if isinstance(value, dict):
        for key, child in value.items():
            path = f"{prefix}.{key}" if prefix else key
            result.update(_flatten(child, path))
    else:
        result[prefix] = value
    return result


def compare_config_parity(on: dict[str, Any], off: dict[str, Any]) -> dict[str, Any]:
    """Compare profiles, allowing only condition/orchestration/output/prompt fields."""

    validate_condition_config(on, expected_condition="VEGO_AI_ON")
    validate_condition_config(off, expected_condition="VEGO_AI_OFF")
    left = _flatten(on)
    right = _flatten(off)
    differences = []
    for path in sorted(set(left) | set(right)):
        if left.get(path) == right.get(path):
            continue
        if not any(path == allowed or path.startswith(allowed + ".") for allowed in ALLOWED_DIFFERENCE_PREFIXES):
            differences.append({"path": path, "on": left.get(path), "off": right.get(path)})
    if differences:
        raise ValueError(f"configuration parity failed: {differences}")
    return {
        "status": "PASS",
        "allowed_differences": sorted(ALLOWED_DIFFERENCE_PREFIXES),
        "difference_count": sum(left.get(path) != right.get(path) for path in set(left) | set(right)),
        "same_provider_model_parameters": True,
        "same_corpus_case_manifest": True,
        "same_output_schema_validation_retention": True,
    }


def build_prompt_difference_receipt(
    *, on_sources: Iterable[Path], off_sources: Iterable[Path], allowed_difference: str,
) -> dict[str, Any]:
    """Hash every prompt source and record the deliberately allowed text delta."""

    def record(path: Path) -> dict[str, Any]:
        if not path.is_file():
            raise ValueError(f"prompt source is unavailable: {path}")
        try:
            display_path = path.resolve().relative_to(ROOT).as_posix()
        except ValueError:
            display_path = path.as_posix()
        return {"path": display_path, "sha256": sha256_file(path), "bytes": path.stat().st_size}

    on = [record(path) for path in on_sources]
    off = [record(path) for path in off_sources]
    if not on or not off:
        raise ValueError("both conditions require prompt sources")
    return {
        "schema_version": "study2a-prompt-difference-v1",
        "status": "PASS",
        "allowed_difference": allowed_difference,
        "text_difference_present": {row["sha256"] for row in on} != {row["sha256"] for row in off},
        "on": on,
        "off": off,
        "model_data_token_parity": "validated by compare_config_parity",
        "same_output_objective": True,
        "raw_prompt_content_recorded": False,
        "reference_model_exposure": "NONE",
    }


def deterministic_run_id(condition_id: str, *, study_id: str, corpus_id: str, seed: int) -> str:
    if condition_id not in {"VEGO_AI_ON", "VEGO_AI_OFF"}:
        raise ValueError("unknown condition for run identity")
    payload = f"{study_id}|{corpus_id}|{condition_id}|{seed}"
    return "S2A-" + hashlib.sha256(payload.encode("utf-8")).hexdigest()[:24]


def static_call_bounds(case_count: int) -> dict[str, Any]:
    if isinstance(case_count, bool) or not isinstance(case_count, int) or case_count < 0:
        raise ValueError("case_count must be a non-negative integer")
    return {
        "N": case_count,
        "on": {"minimum": 4 + 3 * case_count, "maximum": 82 + 61 * case_count},
        "off": {"minimum": case_count, "maximum": case_count},
        "cost_status": "NOT_MEASURED_PREPARATION",
        "derivation": {
            "on": {
                "minimum": {
                    "fixed_calls": 4,
                    "per_case_calls": 3,
                    "formula": "4 + 3N",
                    "basis": "protected orchestrator direct no-question path",
                },
                "maximum": {
                    "fixed_calls": 82,
                    "per_case_calls": 61,
                    "formula": "82 + 61N",
                    "basis": "protected orchestrator static branch inventory with bounded Q&A",
                },
            },
            "off": {
                "fixed_calls": 0,
                "per_case_calls": 1,
                "formula": "N",
                "basis": "one direct baseline call per fixed case",
            },
            "max_qa_rounds": 10,
            "provider_cost": "TO_BE_MEASURED_AFTER_SEPARATE_AUTHORIZED_RUN",
        },
    }


def detector_applicability(config: dict[str, Any]) -> str:
    value = config.get("detector_applicability")
    if value not in {"AVAILABLE_ON_ONLY", "NOT_APPLICABLE"}:
        raise ValueError("invalid Detector applicability")
    return value


TERMINAL_EVENT_TYPES = {"CONVERGED", "TERMINATED_MAX_ROUNDS", "INCOMPLETE_TECHNICAL"}


def validate_on_lifecycle(events: list[dict[str, Any]]) -> dict[str, Any]:
    """Validate the minimal ON event contract before any scientific analysis.

    This is an offline contract checker for future observed events.  It does
    not infer answers or episode membership: malformed, missing, duplicate,
    cross-episode, and post-terminal records fail closed.
    """

    if not isinstance(events, list):
        raise ValueError("event stream must be a list")
    if not events:
        return {"status": "PASS", "run_id": None, "episode_count": 0, "question_count": 0}
    run_ids = {event.get("run_id") for event in events if isinstance(event, dict)}
    if len(run_ids) != 1 or None in run_ids or "" in run_ids:
        raise ValueError("event stream must contain exactly one run_id")
    if any(not isinstance(event, dict) for event in events):
        raise ValueError("event stream contains a malformed event")
    episodes: dict[str, list[dict[str, Any]]] = {}
    for event in events:
        episode_id = event.get("episode_id")
        if episode_id is None or not isinstance(episode_id, str) or not episode_id:
            raise ValueError("scientific events require an episode_id")
        event_type = event.get("event_type")
        if event_type not in {"QUESTION_EMITTED", "ANSWER_RECEIVED", *TERMINAL_EVENT_TYPES, "CONTEXT"}:
            raise ValueError(f"unknown lifecycle event type: {event_type}")
        episodes.setdefault(episode_id, []).append(event)
    question_count = 0
    for episode_id, episode_events in episodes.items():
        questions: dict[str, int] = {}
        answers: dict[str, int] = {}
        terminals = [index for index, event in enumerate(episode_events) if event["event_type"] in TERMINAL_EVENT_TYPES]
        if len(terminals) != 1:
            raise ValueError(f"episode {episode_id} must have exactly one terminal event")
        terminal_index = terminals[0]
        if terminal_index != len(episode_events) - 1:
            raise ValueError(f"events after termination are not allowed for episode {episode_id}")
        for index, event in enumerate(episode_events):
            event_type = event["event_type"]
            if event_type == "QUESTION_EMITTED":
                question_id = event.get("question_id")
                if not isinstance(question_id, str) or not question_id or question_id in questions:
                    raise ValueError(f"episode {episode_id} has a duplicate or missing question_id")
                questions[question_id] = index
            elif event_type == "ANSWER_RECEIVED":
                question_id = event.get("question_id")
                if question_id not in questions:
                    raise ValueError(f"answer references a missing or future question in episode {episode_id}")
                if question_id in answers:
                    raise ValueError(f"question {question_id} has more than one answer")
                answers[question_id] = index
        if not questions:
            raise ValueError(f"episode {episode_id} is empty or has no question")
        if set(questions) != set(answers) or any(answers[q] <= questions[q] for q in questions):
            raise ValueError(f"episode {episode_id} has an unanswered or non-later answer")
        if episode_events[-1]["event_type"] in {"CONVERGED", "TERMINATED_MAX_ROUNDS"} and not questions:
            raise ValueError(f"episode {episode_id} has an empty terminal state")
        question_count += len(questions)
    return {
        "status": "PASS",
        "run_id": next(iter(run_ids)),
        "episode_count": len(episodes),
        "question_count": question_count,
    }


def detector_signal_context(signal_code: str, value: float | None = None) -> dict[str, Any]:
    """Keep the frozen non-triggering C1 boundary descriptive only."""

    if signal_code == "C1_MAPPING_CERTAINTY" and value is not None and not 0 <= value <= 1:
        raise ValueError("C1 value must lie in [0, 1]")
    if signal_code in {"C1_MAPPING_CERTAINTY", "S5_REPEATED_CLARIFICATION", "S8_FOLLOW_UP", "S9_QUESTION_DENSITY"}:
        return {"signal": signal_code, "triggering": False, "classification": "CONTEXT_ONLY"}
    return {"signal": signal_code, "triggering": None, "classification": "UNSPECIFIED_PREPARATION"}


def build_privacy_receipt() -> dict[str, Any]:
    """Return the tracked-output privacy boundary without reading private data."""

    return {
        "schema_version": "study2a-privacy-receipt-v1",
        "status": "PASS",
        "tracked_content": "SAFE_METADATA_ONLY",
        "raw_prompts_answers_corpus_bytes": "NOT_TRACKED",
        "private_output_roots": ["external_data/study2a/vego-ai-on/", "external_data/study2a/vego-ai-off/"],
        "private_roots_are_ignored": True,
        "reference_models_runtime_visible": False,
        "absolute_paths": "NOT_EMITTED",
        "credentials_provider_calls_and_student_data": "FORBIDDEN",
    }


def build_fake_run_parity_receipt(on: dict[str, Any], off: dict[str, Any]) -> dict[str, Any]:
    """Run only in-memory engineering fixtures; no corpus or provider is touched."""

    fixture_cases = {case_id: f"ENGINEERING_FIXTURE_ONLY::{case_id}" for case_id in on["corpus"]["case_ids"]}
    on_result = fake_run(on, fixture_cases)
    off_result = fake_run(off, fixture_cases)
    overlap = sorted(set(on_result["event_ids"]) & set(off_result["event_ids"]))
    if overlap:
        raise ValueError("fake fixture event IDs cross condition boundaries")
    return {
        "schema_version": "study2a-fake-parity-receipt-v1",
        "status": "ENGINEERING_FIXTURE_ONLY",
        "scientific_result": False,
        "fixture_input_policy": "hashed-only synthetic engineering labels; not corpus data",
        "conditions": {
            "VEGO_AI_ON": {
                "run_id": on_result["run_id"],
                "case_count": on_result["case_count"],
                "event_count": len(on_result["event_ids"]),
                "provider_calls": on_result["provider_calls"],
                "external_network_calls": on_result["external_network_calls"],
            },
            "VEGO_AI_OFF": {
                "run_id": off_result["run_id"],
                "case_count": off_result["case_count"],
                "event_count": len(off_result["event_ids"]),
                "provider_calls": off_result["provider_calls"],
                "external_network_calls": off_result["external_network_calls"],
            },
        },
        "cross_condition_event_id_overlap": overlap,
        "raw_content_written": False,
    }


def validate_reference_separation(runtime_root: Path, reference_root: Path) -> bool:
    """Ensure reference material is not inside, equal to, or beside an unsafe root."""

    runtime = runtime_root.resolve()
    reference = reference_root.resolve()
    if runtime == reference or runtime in reference.parents:
        raise ValueError("reference path is runtime-visible")
    if runtime.parent != reference.parent:
        raise ValueError("absolute or non-sibling reference path is not permitted")
    return True


def fake_run(config: dict[str, Any], cases: dict[str, str]) -> dict[str, Any]:
    """Create an isolated, deterministic engineering fixture receipt.

    ``cases`` values are hashed only; raw text is never returned or written.
    The function has no provider path and therefore cannot produce a Study 2
    scientific observation.
    """

    validate_condition_config(config, expected_condition=config.get("condition_id", ""))
    expected_ids = config["corpus"]["case_ids"]
    if not isinstance(cases, dict) or list(cases) != expected_ids:
        raise ValueError("fixed case manifest differs from the frozen corpus")
    if any(not isinstance(case_id, str) or not isinstance(value, str) or not value for case_id, value in cases.items()):
        raise ValueError("engineering fixture cases must have non-empty string values")
    condition = config["condition_id"]
    run_id = deterministic_run_id(
        condition, study_id=config["study_id"], corpus_id=config["corpus"]["corpus_id"], seed=RUN_SEED
    )
    event_ids = [
        hashlib.sha256(f"{run_id}|{case_id}|{sha256_bytes(cases[case_id].encode())}".encode()).hexdigest()
        for case_id in expected_ids
    ]
    return {
        "schema_version": "study2a-fake-receipt-v1",
        "status": "ENGINEERING_FIXTURE_ONLY",
        "condition_id": condition,
        "run_id": run_id,
        "case_count": len(expected_ids),
        "provider_calls": 0,
        "external_network_calls": 0,
        "detector_applicability": detector_applicability(config),
        "event_ids": event_ids,
        "raw_content_written": False,
        "scientific_result": False,
    }


def build_manifest() -> dict[str, Any]:
    on = load_condition_config(CONFIG_DIR / "vego_ai_on.json")
    off = load_condition_config(CONFIG_DIR / "vego_ai_off.json")
    validate_condition_config(on, expected_condition="VEGO_AI_ON")
    validate_condition_config(off, expected_condition="VEGO_AI_OFF")
    parity = compare_config_parity(on, off)
    prompt_receipt = build_prompt_difference_receipt(
        on_sources=[ROOT / source["path"] for source in on["prompts"]["sources"]],
        off_sources=[ROOT / source["path"] for source in off["prompts"]["sources"]],
        allowed_difference="orchestration only; same output objective and frozen provider/corpus limits",
    )
    fake_parity = build_fake_run_parity_receipt(on, off)
    manifest = {
        "schema_version": SCHEMA_VERSION,
        "study_id": "STUDY2A",
        "frozen_date": "2026-09-06",
        "research_question": "How does full VEGO-AI orchestration change observable execution and communication behavior relative to a non-VEGO baseline on the same fixed public-external corpus?",
        "status": "PREPARATION_ONLY_NO_EXPERIMENT",
        "conditions": {"VEGO_AI_ON": on, "VEGO_AI_OFF": off},
        "baseline": {
            "id": "BASELINE_SINGLE_MODEL_NO_VEGO",
            "selection_status": "NEWLY_CONSTRUCTED_EXPERIMENTAL_BASELINE",
            "selection_evidence": "Repository search found no existing non-VEGO AirTravel baseline; this direct one-call profile is therefore explicit and is not a historical VEGO baseline.",
        },
        "config_parity": parity,
        "prompt_difference_receipt": prompt_receipt,
        "call_bounds": static_call_bounds(4),
        "lifecycle_contract": {
            "validator": "validate_on_lifecycle",
            "status": "OFFLINE_CONTRACT_TESTED",
            "malformed_streams": "FAIL_CLOSED",
            "scientific_events": "NOT_OBSERVED",
        },
        "detector_contract": {
            "VEGO_AI_ON": "AVAILABLE_ON_ONLY",
            "VEGO_AI_OFF": "NOT_APPLICABLE",
            "non_triggering_context": [
                "C1_MAPPING_CERTAINTY",
                "S5_REPEATED_CLARIFICATION",
                "S8_FOLLOW_UP",
                "S9_QUESTION_DENSITY",
            ],
        },
        "measures": {
            "both": [
                "attempted_case_count", "completed_case_count", "technical_failure_count",
                "output_schema_validity", "parseability", "elapsed_time", "provider_calls",
                "input_tokens", "output_tokens", "cached_tokens", "cost", "retry_count",
                "completion_state", "artifact_count", "output_structural_fields",
            ],
            "VEGO_AI_ON_only": [
                "complete_episodes", "incomplete_episodes", "questions", "answers", "rounds",
                "route_pairs", "termination_states", "confidence_distribution",
                "evidence_presence", "Detector_v1_signal_and_tier_counts", "C1_C2_C3_context_only",
            ],
            "VEGO_AI_OFF_detector": "NOT_APPLICABLE",
        },
        "forbidden_claims": [
            "accuracy", "correctness", "precision", "recall", "F1", "human benefit",
            "intervention effectiveness", "superiority", "generalization", "student-data claims",
        ],
        "execution_gates": {
            "provider_run": "SEPARATE_EXPLICIT_AUTHORIZATION_REQUIRED",
            "llama": "SEPARATE_STUDY_2B_FEASIBILITY_ONLY",
            "synthetic_data": "FORBIDDEN_EXCEPT_ENGINEERING_FIXTURES",
        },
        "receipts": {
            "schema_validation": {"status": "PASS", "schema_path": "schemas/study2a-vego-ai-on-off-v1.schema.json"},
            "privacy": build_privacy_receipt(),
            "fake_run_parity": fake_parity,
            "baseline_definition": {
                "id": "BASELINE_SINGLE_MODEL_NO_VEGO",
                "call_path": "one direct model call per fixed case",
                "delegation": "NONE",
                "qa_registry": "NONE",
                "feedback_loop": "NONE",
                "detector_input": "NONE",
                "status": "NEWLY_CONSTRUCTED_EXPERIMENTAL_BASELINE",
            },
            "protected_runtime": {
                "modified": False,
                "provider_execution": "DISABLED",
                "network": "DISABLED",
                "detector_v1_run": False,
            },
        },
    }
    validate_manifest_schema(manifest)
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-manifest", action="store_true")
    parser.add_argument("--dry-run", action="store_true", help="validate contracts without writing or executing")
    parser.add_argument("--fake-run", action="store_true", help="emit the in-memory engineering fixture receipt")
    parser.add_argument(
        "--execute",
        action="store_true",
        help="reserved and rejected; provider-backed execution requires a separately authorized runner",
    )
    args = parser.parse_args()
    if args.execute:
        parser.error("provider-backed execution is not part of the Study 2 preparation harness")
    manifest = build_manifest()
    if args.write_manifest:
        MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)
        temp = MANIFEST_PATH.with_suffix(".tmp")
        # Path.write_text uses the host newline convention on Windows.  Open
        # with an explicit LF newline so the generated manifest has identical
        # bytes across platforms (Git normalization is not part of the
        # reproducibility contract).
        with temp.open("w", encoding="utf-8", newline="\n") as handle:
            handle.write(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n")
        os.replace(temp, MANIFEST_PATH)
    result: dict[str, Any] = {"status": manifest["status"], "manifest_path": MANIFEST_PATH.as_posix()}
    if args.fake_run:
        result["fake_run_parity"] = manifest["receipts"]["fake_run_parity"]
    if args.dry_run:
        result["mode"] = "DRY_RUN"
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
