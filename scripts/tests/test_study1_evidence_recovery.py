from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
FRAMEWORK = ROOT / "VEGO-AI" / "framework"
if str(FRAMEWORK) not in sys.path:
    sys.path.insert(0, str(FRAMEWORK))


def load_module():
    path = ROOT / "scripts" / "study1_evidence_recovery.py"
    spec = importlib.util.spec_from_file_location("study1_evidence_recovery", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _write(path: Path, value: object) -> str:
    data = (json.dumps(value, sort_keys=True, ensure_ascii=False) + "\n").encode()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    return hashlib.sha256(data).hexdigest()


def _valid_fixture(tmp_path: Path) -> tuple[object, Path, Path]:
    module = load_module()
    from qa_communication import QACommunicationRecorder

    evidence = tmp_path / "mounted-evidence"
    output = evidence / "output"
    recorder = QACommunicationRecorder(output / "qa_events.jsonl", run_id="accepted-run-1")
    question = recorder.emit_question(
        question_id="Q-1",
        episode_id="EP-1",
        source_agent="agent3",
        source_stage="case_inspection",
        source_skill="resolve_unsatisfied",
        target_agent="agent1",
        scope="language",
        case_id="01",
        question_text="private question",
        round_index=1,
    )
    recorder.emit_answer(
        question=question,
        answer_text="private answer",
        answer_confidence="High",
        answer_evidence="private evidence",
    )
    recorder.emit_termination(
        episode_id="EP-1", termination_reason="CONVERGED", converged=True
    )
    event_hash = hashlib.sha256((output / "qa_events.jsonl").read_bytes()).hexdigest()
    receipt = {
        "run_id": "accepted-run-1",
        "status": "ACCEPTED_REPLACEMENT",
        "setting_id": module.SETTING_ID,
        "corpus_id": module.CORPUS_ID,
        "N": 1,
        "execution_code_sha256": "a" * 64,
        "config_sha256": "b" * 64,
        "event_log_sha256": event_hash,
        "episode_count": 1,
        "question_count": 1,
        "answer_count": 1,
        "termination_counts": {"CONVERGED": 1},
    }
    receipt_hash = _write(output / "run-receipt.json", receipt)
    pipeline_hash = _write(
        output / "pipeline-output-manifest.json",
        {"counts": {"episodes": 1, "questions": 1, "answers": 1}},
    )
    detector_hash = _write(
        output / "detector-summary.json",
        {
            "denominators": {"complete_episodes": 1},
            "counts": {"questions": 1, "answers": 1},
            "detector_v1": {"NO_ALERT": 1},
        },
    )
    manifest = {
        "schema_version": "study1-evidence-binding-v1",
        "accepted_run": True,
        "run_identity": {
            "run_id": "accepted-run-1",
            "run_class": "accepted_replacement_real_run",
            "accepted_replacement": True,
            "fake_preflight": False,
            "status": "ACCEPTED_REPLACEMENT",
        },
        "setting_id": module.SETTING_ID,
        "corpus_id": module.CORPUS_ID,
        "execution_code_sha256": "a" * 64,
        "config_sha256": "b" * 64,
        "artifacts": {
            "qa_events_jsonl": {"path": "output/qa_events.jsonl", "sha256": event_hash},
            "run_receipt": {"path": "output/run-receipt.json", "sha256": receipt_hash},
            "pipeline_output_manifest": {
                "path": "output/pipeline-output-manifest.json",
                "sha256": pipeline_hash,
            },
            "detector_summary": {
                "path": "output/detector-summary.json",
                "sha256": detector_hash,
            },
        },
    }
    binding = tmp_path / "binding-manifest.json"
    _write(binding, manifest)
    return module, evidence, binding


def test_missing_private_evidence_is_unavailable_without_numeric_values(tmp_path: Path):
    module = load_module()
    result = module.recover(tmp_path / "not-mounted", tmp_path / "missing.json")
    assert result["status"] == module.EVIDENCE_NOT_AVAILABLE
    assert result["recomputed"] is None
    assert result["location_class"] == "authorized_read_only_evidence_root"
    assert not any(isinstance(v, (int, float)) for v in result["safe_values"].values())


def test_existing_root_without_binding_manifest_is_unavailable(tmp_path: Path):
    module = load_module()
    evidence = tmp_path / "mounted-evidence"
    evidence.mkdir()
    result = module.recover(evidence, tmp_path / "missing-binding.json")
    assert result["status"] == module.EVIDENCE_NOT_AVAILABLE
    assert result["recomputed"] is None


def test_valid_accepted_chain_is_hash_and_identity_bound(tmp_path: Path):
    module, evidence, binding = _valid_fixture(tmp_path)
    result = module.recover(evidence, binding)
    assert result["status"] == module.ACCEPTED
    assert result["run_id_sha256"] == hashlib.sha256(b"accepted-run-1").hexdigest()
    assert result["recomputed"]["complete_episodes"] == 1
    assert result["recomputed"]["questions"] == 1
    assert result["recomputed"]["answers"] == 1
    assert result["recomputed"]["detector_v1_denominator"] == 1
    serialized = json.dumps(result, sort_keys=True)
    assert "private question" not in serialized
    assert "private answer" not in serialized


def test_artifact_hash_mismatch_is_invalid(tmp_path: Path):
    module, evidence, binding = _valid_fixture(tmp_path)
    payload = json.loads(binding.read_text(encoding="utf-8"))
    payload["artifacts"]["run_receipt"]["sha256"] = "0" * 64
    binding.write_text(json.dumps(payload), encoding="utf-8")
    result = module.recover(evidence, binding)
    assert result["status"] == module.EVIDENCE_INVALID
    assert result["recomputed"] is None


def test_missing_receipt_code_binding_is_partial_not_accepted(tmp_path: Path):
    module, evidence, binding = _valid_fixture(tmp_path)
    receipt_path = evidence / "output/run-receipt.json"
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    receipt.pop("execution_code_sha256")
    receipt.pop("config_sha256")
    receipt_path.write_text(json.dumps(receipt) + "\n", encoding="utf-8")
    # Rebind the changed receipt bytes, as a real manifest generator would.
    payload = json.loads(binding.read_text(encoding="utf-8"))
    payload["artifacts"]["run_receipt"]["sha256"] = hashlib.sha256(receipt_path.read_bytes()).hexdigest()
    binding.write_text(json.dumps(payload), encoding="utf-8")
    result = module.recover(evidence, binding)
    assert result["status"] == module.PARTIAL
    assert len(result["provenance_gaps"]) == 2


def test_fake_preflight_cannot_be_accepted(tmp_path: Path):
    module, evidence, binding = _valid_fixture(tmp_path)
    payload = json.loads(binding.read_text(encoding="utf-8"))
    payload["run_identity"]["fake_preflight"] = True
    binding.write_text(json.dumps(payload), encoding="utf-8")
    result = module.recover(evidence, binding)
    assert result["status"] == module.EVIDENCE_INVALID
    assert any("fake" in check["check"] for check in result["checks"])


def test_mixed_run_event_stream_fails_closed(tmp_path: Path):
    module, evidence, binding = _valid_fixture(tmp_path)
    event_path = evidence / "output/qa_events.jsonl"
    rows = [json.loads(line) for line in event_path.read_text(encoding="utf-8").splitlines()]
    rows[1]["run_id"] = "other-run"
    event_path.write_text("\n".join(json.dumps(row, sort_keys=True) for row in rows) + "\n", encoding="utf-8")
    result = module.recover(evidence, binding)
    assert result["status"] == module.EVIDENCE_INVALID
    assert result["recomputed"] is None


def test_absolute_and_traversal_artifact_paths_fail_closed(tmp_path: Path):
    module, evidence, binding = _valid_fixture(tmp_path)
    payload = json.loads(binding.read_text(encoding="utf-8"))
    payload["artifacts"]["run_receipt"]["path"] = "../outside.json"
    binding.write_text(json.dumps(payload), encoding="utf-8")
    result = module.recover(evidence, binding)
    assert result["status"] == module.EVIDENCE_INVALID
    assert result["recomputed"] is None


@pytest.mark.parametrize("kind", ["failed_real_attempt", "fake_preflight", "unknown"])
def test_non_accepted_run_class_is_not_scientific_evidence(tmp_path: Path, kind: str):
    module, evidence, binding = _valid_fixture(tmp_path)
    payload = json.loads(binding.read_text(encoding="utf-8"))
    payload["run_identity"]["run_class"] = kind
    binding.write_text(json.dumps(payload), encoding="utf-8")
    result = module.recover(evidence, binding)
    assert result["status"] == module.EVIDENCE_INVALID
