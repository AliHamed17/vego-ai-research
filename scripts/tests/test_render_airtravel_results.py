"""Tests for the deterministic AirTravel post-run renderer.

All event streams below are explicitly labeled synthetic engineering fixtures
built through the frozen ``qa_communication`` recorder; they are not a
scientific corpus, and no provider or orchestrator is invoked.
"""

from __future__ import annotations

import json
import pathlib
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "VEGO-AI" / "framework"))

import render_airtravel_results as renderer  # noqa: E402
from qa_communication import QACommunicationRecorder  # noqa: E402


def _fixture_events(path: pathlib.Path) -> None:
    recorder = QACommunicationRecorder(path, run_id="fixture-run")
    recorder.observe_exchange(
        questions=[{"question_id": "Q_lang_001", "question": "fixture question one"}],
        answers=[
            {
                "question_id": "Q_lang_001",
                "answer": "fixture answer",
                "confidence": "High",
                "evidence": "fixture evidence",
            }
        ],
        source_agent="agent2",
        source_stage="guideline_construction",
        source_skill="qa_route",
        target_agent="agent1",
        scope="language",
        episode_id="EP-fixture-high",
        round_index=1,
    )
    recorder.emit_termination(
        episode_id="EP-fixture-high", termination_reason="CONVERGED", converged=True
    )
    recorder.observe_exchange(
        questions=[{"question_id": "Q_lang_002", "question": "fixture question two"}],
        answers=[
            {
                "question_id": "Q_lang_002",
                "answer": "fixture answer",
                "confidence": "Low",
                "evidence": None,
            }
        ],
        source_agent="agent2",
        source_stage="guideline_construction",
        source_skill="qa_route",
        target_agent="agent1",
        scope="language",
        episode_id="EP-fixture-low",
        round_index=1,
    )
    recorder.emit_termination(
        episode_id="EP-fixture-low", termination_reason="CONVERGED", converged=True
    )
    recorder.emit_question(
        question_id="Q_dom_003",
        episode_id="EP-fixture-broken",
        source_agent="agent2",
        source_stage="guideline_construction",
        source_skill="qa_route",
        target_agent="agent2",
        scope="domain",
        question_text="fixture question three",
        round_index=1,
    )
    recorder.emit_termination(
        episode_id="EP-fixture-broken", termination_reason="INCOMPLETE_TECHNICAL", converged=None
    )


def _technical_fixture(events):
    from airtravel_preflight_contract import canonical, digest
    from airtravel_preflight_execution import SCIENTIFIC_FILES
    from prepare_airtravel_protected_fake_preflight import FROZEN

    rows = [json.loads(line) for line in events.read_text().splitlines() if line.strip()]
    files = {}
    for side in ("baseline", "instrumented"):
        for name in SCIENTIFIC_FILES:
            path = events.parent / side / name
            path.parent.mkdir(parents=True, exist_ok=True)
            value = (
                {
                    "compliance_vectors": dict.fromkeys(("01", "02", "03", "04"), {}),
                    "uncovered_fragments": dict.fromkeys(("01", "02", "03", "04"), {}),
                }
                if name == "pipeline_state.json"
                else {}
            )
            path.write_bytes(canonical(value))
            files[side + "/" + name] = digest(path)
    return {
        "schema_version": "airtravel-technical-receipt-v1",
        "status": "TECHNICAL_SUCCESS",
        "fixture_only": True,
        "setting_id": "cd_airtravel",
        "corpus_id": "text2uml_airtravel_253b26dc",
        "N": 4,
        "commit": "1" * 40,
        "model": "LOCAL_DETERMINISTIC_FAKE_V3",
        "provider": "LOCAL_ONLY",
        "runtime_file_hashes": {p: v[0] for p, v in FROZEN["runtime_files"].items()},
        "timeout_seconds": 1800,
        "direct_fake_call_count": 16,
        "decision_parity": True,
        "call_label_parity": True,
        "phase_case_count_parity": True,
        "termination_parity": True,
        "lifecycle_status": "PASS",
        "call_inventory_status": "PASS",
        "filesystem_containment": "PASS",
        "provider_backed_production_route_pair_count": 0,
        "detector_v1_experimental_run_count": 0,
        "runtime_archive_sha256": FROZEN["runtime_archive_sha256"],
        "event_log_sha256": digest(events),
        "event_count": len(rows),
        "question_count": sum(e["event_type"] == "QUESTION_EMITTED" for e in rows),
        "orchestrator_completed": True,
        "expected_outputs_exist": True,
        "event_recorder_completed": True,
        "processed_case_ids": ["01", "02", "03", "04"],
        "technical_exception": None,
        "timeout": False,
        "prompt_parity": True,
        "answer_parity": True,
        "state_parity": True,
        "output_parity": True,
        "baseline_fake_call_count": 16,
        "instrumented_fake_call_count": 16,
        "elapsed_seconds": 0,
        "external_provider_call_count": 0,
        "network_attempt_count": 0,
        "files": files,
    }


def _base_argv(events: pathlib.Path, output_root: pathlib.Path) -> list[str]:
    from airtravel_preflight_contract import canonical, digest

    path = events.parent / "fixture-receipt.json"
    path.write_bytes(canonical(_technical_fixture(events)))
    return [
        "render_airtravel_results.py",
        "--events",
        str(events),
        "--output-root",
        str(output_root),
        "--run-receipt",
        str(path),
        "--run-receipt-sha256",
        digest(path),
        "--run-sha",
        "1" * 40,
        "--model",
        "LOCAL_DETERMINISTIC_FAKE_V3",
    ]


def test_renderer_produces_all_outputs_and_fills_every_token(
    tmp_path: pathlib.Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    events = tmp_path / "events.jsonl"
    _fixture_events(events)
    output_root = tmp_path / "out"
    monkeypatch.setattr(sys, "argv", _base_argv(events, output_root))
    assert renderer.main() == 0
    report = (output_root / "airtravel-preliminary-results-he.md").read_text(encoding="utf-8")
    assert not renderer.TOKEN_RE.findall(report)
    assert 'dir="rtl"' in report
    assert "PUBLIC_EXTERNAL" in report and "EXTERNAL_LLM_GENERATED" in report
    assert "NOT_DOCUMENTED" in report
    machine = json.loads(
        (output_root / "airtravel-results-machine.json").read_text(encoding="utf-8")
    )
    assert machine["summary"]["episodes"] == 3
    assert machine["summary"]["scientific_episode_count"] == 2
    assert machine["summary"]["excluded_incomplete_technical"] == 1
    episodes_csv = (output_root / "airtravel-episodes.csv").read_text(encoding="utf-8")
    assert episodes_csv.count("EP-fixture") == 3
    detector_csv = (output_root / "airtravel-detector.csv").read_text(encoding="utf-8")
    assert "STRONG_ALERT" in detector_csv and "EXCLUDED" in detector_csv


def test_report_counts_follow_frozen_rules(tmp_path: pathlib.Path) -> None:
    events = tmp_path / "events.jsonl"
    _fixture_events(events)
    corpus = renderer.extract_live_corpus(events)
    fields = renderer.build_report_fields(corpus, _technical_fixture(events))
    assert fields["N_TOTAL_EPISODES"] == "3"
    assert fields["N_COMPLETE_EPISODES"] == "2"
    assert fields["N_INCOMPLETE_TECHNICAL"] == "1"
    assert fields["DENOMINATOR"] == "2"
    assert fields["N_S1"] == "1" and fields["N_S3"] == "1"
    assert fields["N_S2"] == "0" and fields["N_S6"] == "0" and fields["N_S7"] == "0"
    assert fields["N_STRONG_ALERT"] == "1"
    assert fields["N_NO_ALERT"] == "1"
    assert fields["N_WEAK_ALERT"] == "0"
    assert fields["ZERO_QA_STATUS"] == "NOT_ZERO_QA"
    assert "INCOMPLETE_TECHNICAL" in fields["TERMINATION_TABLE"]


def test_zero_qa_stream_requires_successful_verified_technical_receipt(tmp_path):
    events = tmp_path / "events.jsonl"
    events.write_text("", encoding="utf-8")
    assert (
        renderer.zero_qa_status([], {"status": "FIXTURE_ONLY"}) == "INVALID_OR_INCOMPLETE_ZERO_QA"
    )
    fixture = _technical_fixture(events)
    assert renderer.zero_qa_status([], fixture) == "INVALID_OR_INCOMPLETE_ZERO_QA"
    # An in-memory successful-shape test, not a receipt for an actual run.
    fixture["fixture_only"] = False
    assert renderer.zero_qa_status([], fixture) == "VALID_ZERO_QA_RUN"


def test_residual_token_fails_closed() -> None:
    with pytest.raises(ValueError, match="unfilled template tokens"):
        renderer.render_report("before {{NOT_A_REAL_TOKEN}} after", {})


def test_forbidden_metric_terms_fail_closed() -> None:
    with pytest.raises(ValueError, match="forbidden claim term"):
        renderer.render_report("the precision of this run", {})


def test_all_eight_output_hashes_are_recorded_and_repeatable(tmp_path, monkeypatch):
    events = tmp_path / "events.jsonl"
    _fixture_events(events)
    outputs = [tmp_path / "one", tmp_path / "two"]
    for output in outputs:
        monkeypatch.setattr(sys, "argv", _base_argv(events, output))
        assert renderer.main() == 0
    from airtravel_preflight_contract import digest

    names = {
        "airtravel-analysis-receipt.json",
        "airtravel-results-machine.json",
        "airtravel-episodes.csv",
        "airtravel-detector.csv",
        "airtravel-signals.csv",
        "airtravel-routes.csv",
        "airtravel-terminations.csv",
        "airtravel-preliminary-results-he.md",
    }
    hashes = json.loads((outputs[0] / "airtravel-output-hashes.json").read_text())
    assert set(hashes) == names
    for name in names:
        assert digest(outputs[0] / name) == hashes[name] == digest(outputs[1] / name)


def test_receipt_cannot_inject_findings_through_elapsed_field(tmp_path):
    from airtravel_preflight_contract import canonical, digest

    events = tmp_path / "events.jsonl"
    _fixture_events(events)
    receipt = _technical_fixture(events)
    receipt["elapsed_seconds"] = "Unsupported scientific success"
    path = tmp_path / "receipt.json"
    path.write_bytes(canonical(receipt))
    with pytest.raises(ValueError):
        renderer.verify_run_receipt(
            events, path, digest(path), "1" * 40, "LOCAL_DETERMINISTIC_FAKE_V3"
        )


def test_findings_switch_rejected_even_with_all_valid_inputs(tmp_path, monkeypatch):
    events = tmp_path / "events.jsonl"
    _fixture_events(events)
    argv = _base_argv(events, tmp_path / "out") + ["--findings", "Unsupported claim"]
    monkeypatch.setattr(sys, "argv", argv)
    with pytest.raises(SystemExit):
        renderer.main()
    assert not (tmp_path / "out").exists()
