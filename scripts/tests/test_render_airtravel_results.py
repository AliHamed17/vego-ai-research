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
        answers=[{"question_id": "Q_lang_001", "answer": "fixture answer",
                  "confidence": "High", "evidence": "fixture evidence"}],
        source_agent="agent2", source_stage="guideline_construction",
        source_skill="qa_route", target_agent="agent1", scope="language",
        episode_id="EP-fixture-high", round_index=1,
    )
    recorder.emit_termination(episode_id="EP-fixture-high",
                              termination_reason="CONVERGED", converged=True)
    recorder.observe_exchange(
        questions=[{"question_id": "Q_lang_002", "question": "fixture question two"}],
        answers=[{"question_id": "Q_lang_002", "answer": "fixture answer",
                  "confidence": "Low", "evidence": None}],
        source_agent="agent2", source_stage="guideline_construction",
        source_skill="qa_route", target_agent="agent1", scope="language",
        episode_id="EP-fixture-low", round_index=1,
    )
    recorder.emit_termination(episode_id="EP-fixture-low",
                              termination_reason="CONVERGED", converged=True)
    recorder.emit_question(
        question_id="Q_dom_003", episode_id="EP-fixture-broken",
        source_agent="agent2", source_stage="guideline_construction",
        source_skill="qa_route", target_agent="agent2", scope="domain",
        question_text="fixture question three", round_index=1,
    )
    recorder.emit_termination(episode_id="EP-fixture-broken",
                              termination_reason="INCOMPLETE_TECHNICAL", converged=None)


def _base_argv(events: pathlib.Path, output_root: pathlib.Path) -> list[str]:
    return [
        "render_airtravel_results.py",
        "--events", str(events),
        "--output-root", str(output_root),
        "--run-sha", "fixture-sha",
        "--model", "local-fake-fixture",
        "--run-date", "2026-09-05",
        "--case-count", "4",
        "--total-calls", "0",
        "--runtime-seconds", "0",
        "--technical-status", "FIXTURE_ONLY",
        "--findings", "נתוני בדיקה סינתטיים בלבד.",
        "--conclusion", "בדיקת תבנית בלבד; אין תוצאה מדעית.",
        "--next-step", "אין; זוהי בדיקת תשתית.",
    ]


def test_renderer_produces_all_outputs_and_fills_every_token(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch,
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
        (output_root / "airtravel-results-machine.json").read_text(encoding="utf-8"))
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
    args = type("Args", (), {
        "run_sha": "fixture-sha", "model": "local-fake-fixture", "run_date": "2026-09-05",
        "case_count": 4, "total_calls": "0", "runtime_seconds": "0",
        "measured_cost": "TO BE MEASURED", "technical_status": "FIXTURE_ONLY",
        "findings": "x", "conclusion": "y", "next_step": "z",
    })()
    fields = renderer.build_report_fields(corpus, args)
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


def test_zero_qa_stream_is_reported_as_valid(tmp_path: pathlib.Path) -> None:
    events = tmp_path / "events.jsonl"
    events.write_text("", encoding="utf-8")
    corpus = renderer.extract_live_corpus(events)
    args = type("Args", (), {
        "run_sha": "fixture-sha", "model": "local-fake-fixture", "run_date": "2026-09-05",
        "case_count": 4, "total_calls": "0", "runtime_seconds": "0",
        "measured_cost": "TO BE MEASURED", "technical_status": "FIXTURE_ONLY",
        "findings": "x", "conclusion": "y", "next_step": "z",
    })()
    fields = renderer.build_report_fields(corpus, args)
    assert fields["N_TOTAL_EPISODES"] == "0"
    assert fields["ZERO_QA_STATUS"].startswith("VALID_ZERO_QA_RUN")


def test_residual_token_fails_closed() -> None:
    with pytest.raises(ValueError, match="unfilled template tokens"):
        renderer.render_report("before {{NOT_A_REAL_TOKEN}} after", {})


def test_forbidden_metric_terms_fail_closed() -> None:
    with pytest.raises(ValueError, match="forbidden claim term"):
        renderer.render_report("the precision of this run", {})
