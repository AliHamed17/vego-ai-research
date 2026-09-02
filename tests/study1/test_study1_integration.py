"""End-to-end synthetic safeguards across the public Study 1 interfaces."""

from __future__ import annotations

import json
import os
import socket
import subprocess
import sys
from pathlib import Path

import pytest

from vego_governed.policy import Arm, replay
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

ROOT = Path(__file__).resolve().parents[2]
STUDY1_CLIS = (
    "run_study1_c0_baseline.py",
    "inventory_state_diagram.py",
    "import_controlled_notes.py",
    "validate_study1_privacy.py",
    "validate_study1_release.py",
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


@pytest.mark.parametrize("script_name", STUDY1_CLIS)
def test_every_study1_cli_help_runs_with_pythonpath_cleared(script_name: str):
    """Catches direct entry points that rely on pytest or caller PYTHONPATH injection."""
    environment = dict(os.environ)
    environment.pop("PYTHONPATH", None)

    completed = subprocess.run(
        [sys.executable, "-B", str(ROOT / "scripts" / script_name), "--help"],
        cwd=ROOT,
        env=environment,
        capture_output=True,
        text=True,
    )

    assert completed.returncode == 0, completed.stderr
    assert "usage:" in completed.stdout.casefold()


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
        assert all(
            arm["event_ids"] == first[rate]["event_ids"] for arm in first[rate]["arms"].values()
        )
        assert first[rate]["arms"]["random_at_budget"] == second[rate]["arms"]["random_at_budget"]

    signal_states = {
        signal["evidence_state"] for event in first_events for signal in event["signals"]
    }
    assert signal_states == {"derived", "unavailable"}
    forced = next(event for event in first_events if event["stage"] == "variability_classification")
    observations = {signal["signal_id"]: signal["observation"] for signal in forced["signals"]}
    assert observations["claim_uncertainty"] == {
        "kind": "policy_input",
        "normalized_value": 0.8,
        "missing_value_policy": "force_escalation",
    }
    assert observations["evidence_quality"] == {
        "kind": "policy_input",
        "missing_value_policy": "force_undetermined",
    }
    assert observations["novelty_vs_judgment_store"] == {
        "kind": "policy_input",
        "normalized_value": 0.9,
    }


def test_synthetic_c0_integration_aborts_on_manifest_mutation_and_keeps_report_private(
    tmp_path: Path, monkeypatch
):
    """Catches a run accepting changed frozen input or emitting locators/content into its aggregate report."""
    root = synthetic_c0_root(tmp_path)
    manifest = build_manifest(root)
    selected = root / "eval_output" / "cd_ch" / "agentA_guideline_mapping.json"
    selected.write_text('{"clusters": []}', encoding="utf-8")
    with pytest.raises(C0MutationError):
        assert_manifest_unchanged(root, manifest)

    repository = tmp_path / "temporary-repository"
    repository.mkdir()
    subprocess.run(["git", "init", "-q", str(repository)], check=True)
    (repository / ".gitignore").write_text("research-private/study1/\n", encoding="utf-8")
    import vego_study1.c0 as c0

    monkeypatch.setattr(c0, "REPOSITORY_ROOT", repository)
    report_root = repository / "research-private" / "study1" / "synthetic-report"
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


def test_protocol_uncertainty_arm_description_matches_all_shipped_triggers(tmp_path: Path):
    """Catches protocol wording that hides evidence-quality or novelty trigger inputs."""
    protocol = (ROOT / "docs" / "research" / "study-1" / "protocol.md").read_text(encoding="utf-8")
    row = next(
        line for line in protocol.splitlines() if line.startswith("| `uncertainty_only`")
    ).casefold()
    event = next(
        candidate
        for candidate in adapt_c0_root(synthetic_c0_root(tmp_path))
        if candidate["stage"] == "variability_classification"
    )
    from vego_study1.c0 import candidate_to_replay_event

    decision = replay(
        Arm("uncertainty_only"), [candidate_to_replay_event(event)], budget=1
    ).decisions[0]

    assert "uncertainty" in row
    assert "evidence quality" in row
    assert "novelty" in row
    assert "undetermined_classification" in decision.reason
    assert "guideline_update_proposed" in decision.reason
