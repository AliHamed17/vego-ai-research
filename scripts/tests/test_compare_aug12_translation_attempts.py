from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts/compare_aug12_translation_attempts.py"
SPEC = importlib.util.spec_from_file_location("compare_aug12_translation_attempts", SCRIPT)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


def write_rows(path: Path, translations: tuple[str, ...]) -> None:
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for index, translation in enumerate(translations, start=1):
            handle.write(
                json.dumps(
                    {
                        "Segment_ID": f"S12-{index:04d}",
                        "Machine_EN": translation,
                        "Source_HE_SHA256": str(index) * 64,
                    },
                    separators=(",", ":"),
                )
                + "\n"
            )


def write_events(path: Path, output: Path, *, run_id: str, script_sha: str) -> None:
    rows = [line for line in output.read_text(encoding="utf-8").splitlines() if line.strip()]
    events = [
        {
            "timestamp_utc": "2026-08-15T00:00:00+00:00",
            "run_id": run_id,
            "event": "translation_run_started",
            "source_name": "machine.he.original.jsonl",
            "source_bytes": 100,
            "source_sha256": "A" * 64,
            "source_segment_count": 1064,
            "script_sha256": script_sha,
            "model": "qwen2.5:7b",
            "model_digest": "b" * 64,
            "options": {"temperature": 0, "seed": 0},
            "batch_size": 18,
            "timeout_seconds": 600,
            "translation_prompt_template_sha256": "C" * 64,
        },
        {
            "timestamp_utc": "2026-08-15T00:01:00+00:00",
            "run_id": run_id,
            "event": "translation_run_completed",
            "translated_segment_count": len(rows),
            "output_bytes": output.stat().st_size,
            "output_sha256": MODULE.sha256_file(output),
        },
    ]
    path.write_text(
        "".join(json.dumps(event, separators=(",", ":")) + "\n" for event in events),
        encoding="utf-8",
    )


def test_comparison_reports_counts_and_ids_without_translation_text(
    tmp_path: Path,
) -> None:
    first = tmp_path / "attempt-01.jsonl"
    second = tmp_path / "attempt-02.jsonl"
    write_rows(first, ("one", "two", "three"))
    write_rows(second, ("one", "changed", "three"))

    report = MODULE.compare_attempts(first, second, prefix_rows=3)

    assert report["compared_rows"] == 3
    assert report["exact_match_rows"] == 2
    assert report["changed_rows"] == 1
    assert report["changed_segment_ids"] == ["S12-0002"]
    assert "Machine_EN" not in json.dumps(report)
    assert report["contains_transcript_text"] is False
    assert report["parameter_comparability"] == "unverified"
    assert "requires bilingual human review" in report["claim_boundary"]
    assert "deterministic translation" not in json.dumps(report).lower()
    assert "reproducible output" not in json.dumps(report).lower()


def test_comparison_rejects_hebrew_source_hash_mismatch(tmp_path: Path) -> None:
    first = tmp_path / "attempt-01.jsonl"
    second = tmp_path / "attempt-02.jsonl"
    write_rows(first, ("one",))
    write_rows(second, ("one",))
    payload = json.loads(second.read_text(encoding="utf-8"))
    payload["Source_HE_SHA256"] = "f" * 64
    second.write_text(json.dumps(payload) + "\n", encoding="utf-8")

    with pytest.raises(ValueError, match="source Hebrew hash mismatch"):
        MODULE.compare_attempts(first, second, prefix_rows=1)


def test_comparison_binds_both_event_ledgers_without_claiming_frozen_parameters(
    tmp_path: Path,
) -> None:
    first = tmp_path / "attempt-01.jsonl"
    second = tmp_path / "attempt-02.jsonl"
    first_events = tmp_path / "attempt-01.events.jsonl"
    second_events = tmp_path / "attempt-02.events.jsonl"
    write_rows(first, ("one", "two"))
    write_rows(second, ("one", "changed"))
    write_events(first_events, first, run_id="run-1", script_sha="D" * 64)
    write_events(second_events, second, run_id="run-2", script_sha="E" * 64)

    report = MODULE.compare_attempts(
        first,
        second,
        prefix_rows=2,
        first_events=first_events,
        second_events=second_events,
    )

    assert report["parameter_comparability"] == "event_metadata_partially_evidenced"
    assert report["event_evidence"]["generator_script_hash_match"] is False
    assert report["event_evidence"]["attempt_01"]["event_ledger_sha256"] == MODULE.sha256_file(
        first_events
    )


def test_comparison_rejects_event_terminal_hash_drift(tmp_path: Path) -> None:
    first = tmp_path / "attempt-01.jsonl"
    second = tmp_path / "attempt-02.jsonl"
    first_events = tmp_path / "attempt-01.events.jsonl"
    second_events = tmp_path / "attempt-02.events.jsonl"
    write_rows(first, ("one",))
    write_rows(second, ("one",))
    write_events(first_events, first, run_id="run-1", script_sha="D" * 64)
    write_events(second_events, second, run_id="run-2", script_sha="E" * 64)
    first.write_text(first.read_text(encoding="utf-8") + "\n", encoding="utf-8")

    with pytest.raises(ValueError, match="terminal hash"):
        MODULE.compare_attempts(
            first,
            second,
            prefix_rows=1,
            first_events=first_events,
            second_events=second_events,
        )


def test_comparison_rejects_any_event_after_terminal_binding(tmp_path: Path) -> None:
    first = tmp_path / "attempt-01.jsonl"
    second = tmp_path / "attempt-02.jsonl"
    first_events = tmp_path / "attempt-01.events.jsonl"
    second_events = tmp_path / "attempt-02.events.jsonl"
    write_rows(first, ("one",))
    write_rows(second, ("one",))
    write_events(first_events, first, run_id="run-1", script_sha="D" * 64)
    write_events(second_events, second, run_id="run-2", script_sha="E" * 64)
    with first_events.open("a", encoding="utf-8") as handle:
        handle.write(
            json.dumps(
                {
                    "timestamp_utc": "2026-08-15T00:02:00+00:00",
                    "run_id": "run-1",
                    "event": "batch_started",
                }
            )
            + "\n"
        )

    with pytest.raises(ValueError, match="events after"):
        MODULE.compare_attempts(
            first,
            second,
            prefix_rows=1,
            first_events=first_events,
            second_events=second_events,
        )
