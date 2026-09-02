"""End-to-end synthetic safeguards across the public Study 1 interfaces."""

from __future__ import annotations

import json
import socket
import subprocess
from pathlib import Path

import pytest

from vego_study1.c0 import (
    C0MutationError,
    adapt_c0_root,
    assert_manifest_unchanged,
    build_manifest,
    run_baselines,
    write_baseline_artifacts,
)
from vego_study1.controlled_notes import ControlledNotesError, import_controlled_notes
from vego_study1.privacy import validate_tracked_artifacts
from vego_study1.state_diagram_inventory import (
    StateDiagramInventoryError,
    write_state_diagram_inventory,
)


def _write_json(path: Path, content: object) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(content), encoding="utf-8")
    return path


def synthetic_c0_root(tmp_path: Path) -> Path:
    """Create the minimum non-sensitive frozen-C0 fixture for end-to-end coverage."""
    root = tmp_path / "frozen-c0"
    for index, setting in enumerate(("ucd_ch", "ucd_pw", "cd_ch", "cd_pw")):
        output = root / "eval_output" / setting
        _write_json(
            output / "agentA_guideline_mapping.json",
            {"clusters": [{"base_assignment": None, "match_confidence": "Low"}]},
        )
        _write_json(
            output / "agentB_guideline_mapping.json",
            {
                "clusters": [
                    {
                        "base_assignment": "assigned",
                        "run1_guideline": {"mapping_certainty": 0.4 + index / 100},
                    }
                ]
            },
        )
        _write_json(
            output / "agentC_case_synthetic.json",
            {
                "uncovered_fragments": [{"label": "Alternative"}],
                "potential_found": [{"compliance_status": "Partially-Satisfied"}],
            },
        )
        _write_json(
            output / "agentD_variability_classes.synthetic.json",
            {
                "variability_classifications": [
                    {
                        "confidence": "Low",
                        "classification": "Undetermined",
                        "requires_human_review": True,
                        "flag_for_guidelines_update": True,
                    }
                ]
            },
        )
    return root


def test_synthetic_c0_integration_preserves_determinism_arms_budgets_and_signals(tmp_path: Path):
    """Catches an integration path that changes events, budgets, or signal states between replays."""
    root = synthetic_c0_root(tmp_path)
    first_events, second_events = adapt_c0_root(root), adapt_c0_root(root)
    first, second = run_baselines(first_events), run_baselines(second_events)

    assert first_events == second_events
    assert set(first) == {"5", "10", "20"}
    for rate in ("5", "10", "20"):
        assert first[rate] == second[rate]
        assert first[rate]["budget"] == {"5": 1, "10": 2, "20": 4}[rate]
        assert len(first[rate]["arms"]) == 6
        assert all(arm["event_ids"] == first[rate]["event_ids"] for arm in first[rate]["arms"].values())
        assert first[rate]["arms"]["random_at_budget"] == second[rate]["arms"]["random_at_budget"]

    signal_states = {
        signal["evidence_state"]
        for event in first_events
        for signal in event["signals"]
    }
    assert signal_states == {"derived", "unavailable"}
    forced = next(event for event in first_events if event["stage"] == "variability_classification")
    assert {signal["observation"] for signal in forced["signals"]} >= {
        "missing_force_escalation",
        "missing_force_undetermined",
        "normalized:0.900",
    }


def test_synthetic_c0_integration_aborts_on_manifest_mutation_and_keeps_report_private(tmp_path: Path):
    """Catches a run accepting changed frozen input or emitting locators/content into its aggregate report."""
    root = synthetic_c0_root(tmp_path)
    manifest = build_manifest(root)
    selected = root / "eval_output" / "cd_ch" / "agentA_guideline_mapping.json"
    selected.write_text('{"clusters": []}', encoding="utf-8")
    with pytest.raises(C0MutationError):
        assert_manifest_unchanged(root, manifest)

    report_root = tmp_path / "research-private" / "study1" / "synthetic-report"
    write_baseline_artifacts(synthetic_c0_root(tmp_path / "report-input"), report_root)
    report = report_root / "sanitized" / "study1-c0-baseline-summary.json"
    rendered = report.read_text(encoding="utf-8")

    assert validate_tracked_artifacts([report]) == []
    assert str(root) not in rendered
    assert "agentA_guideline_mapping.json" not in rendered
    assert "descriptive_candidate_escalation_only_no_outcome_evidence" in rendered


def test_state_and_notes_interfaces_fail_closed_without_network(tmp_path: Path, monkeypatch):
    """Catches State or controlled-notes wiring that performs network work or bypasses its authorization gate."""
    def _blocked_socket(*_args, **_kwargs):
        raise AssertionError("network activity is prohibited")

    monkeypatch.setattr(socket, "socket", _blocked_socket)
    with pytest.raises(StateDiagramInventoryError, match="remote"):
        write_state_diagram_inventory("https://example.test/state", tmp_path / "output")

    notes = tmp_path / "synthetic-notes.csv"
    notes.write_text("topic,observation\nalpha,synthetic\n", encoding="utf-8")
    manifest = _write_json(
        tmp_path / "provenance.json",
        {
            "schema_version": "ControlledNotesProvenance-v1",
            "source_hash": "sha256:" + "0" * 64,
            "source_classification": "controlled_development_only",
            "intended_use": "development_only",
        },
    )
    repository = tmp_path / "temporary-repository"
    repository.mkdir()
    subprocess.run(["git", "init", "-q", str(repository)], check=True)
    (repository / ".gitignore").write_text("research-private/study1/\n", encoding="utf-8")
    import vego_study1.controlled_notes as controlled_notes

    monkeypatch.setattr(controlled_notes, "REPOSITORY_ROOT", repository)
    with pytest.raises(ControlledNotesError, match="source_hash"):
        import_controlled_notes(
            notes,
            manifest,
            repository / "research-private" / "study1" / "notes",
            intended_use="development_only",
        )
