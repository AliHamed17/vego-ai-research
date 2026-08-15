from __future__ import annotations

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BUILDER_PATH = ROOT / "scripts/build-progress-tracker.py"


def load_builder():
    spec = importlib.util.spec_from_file_location("build_progress_tracker", BUILDER_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_recent_activity_returns_latest_entries_newest_first(tmp_path: Path) -> None:
    log = tmp_path / "session-log.md"
    log.write_text(
        "# Session Log\n\n"
        + "\n\n".join(f"## 2026-07-{day:02d} - Entry {day}" for day in range(1, 9))
        + "\n",
        encoding="utf-8",
    )
    builder = load_builder()
    assert builder.recent_activity_lines(log) == [
        "- 2026-07-08 - Entry 8",
        "- 2026-07-07 - Entry 7",
        "- 2026-07-06 - Entry 6",
        "- 2026-07-05 - Entry 5",
        "- 2026-07-04 - Entry 4",
        "- 2026-07-03 - Entry 3",
    ]
    status = {
        "generatedAt": "2026-07-26T02:27:30+03:00",
        "iterationHistory": {
            "acceptedCount": 15,
            "historicalPreManifest": list(range(1, 8)),
            "manifestBacked": list(range(8, 16)),
        },
        "latestAcceptedIteration": {
            "iteration": 15,
            "verdict": "NEUTRAL",
            "iterationKind": "reliability_only",
        },
    }
    snapshot = builder.snapshot_lines(status)
    assert "15 H-layer iterations are accepted" in snapshot
    assert "001-007" in snapshot
    assert "008-015" in snapshot
    assert "Iteration 015" in snapshot
    assert builder.snapshot_generated_at(status) == "2026-07-25 23:27 UTC"


def test_evidence_guard_summary_discloses_skipped_inputs() -> None:
    builder = load_builder()
    output = (
        "3/3 present checks passed; 5 skipped (reports not generated).\n"
        "EVIDENCE CONSISTENCY: PASS\n"
    )
    assert builder.evidence_guard_summary(output, 0) == (
        "3/3 present checks passed; 5 skipped", "PASS"
    )


def test_evidence_guard_summary_fails_closed_without_counts() -> None:
    builder = load_builder()
    assert builder.evidence_guard_summary("unexpected output", 1) == (
        "see guard", "FAIL"
    )
