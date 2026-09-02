"""Synthetic contract tests for the frozen Study 1 C0 baseline adapter."""

from __future__ import annotations

import hashlib
import importlib
import json
import subprocess
from pathlib import Path

import pytest

from vego_study1.c0 import (
    C0MutationError,
    C0ValidationError,
    adapt_c0_root,
    assert_manifest_unchanged,
    build_manifest,
    candidate_to_replay_event,
    run_baselines,
    write_baseline_artifacts,
)

SETTINGS = ("ucd_ch", "ucd_pw", "cd_ch", "cd_pw")


def _c0_module():
    return importlib.import_module("vego_study1.c0")


def _private_root(tmp_path: Path) -> Path:
    return tmp_path / "temporary-repository" / "research-private" / "study1" / "baseline"


@pytest.fixture(autouse=True)
def _approved_private_test_repository(tmp_path: Path, monkeypatch):
    """Use a synthetic repository to exercise exact containment and ignore checks."""
    repository_root = tmp_path / "temporary-repository"
    repository_root.mkdir()
    subprocess.run(["git", "init", "-q", str(repository_root)], check=True)
    (repository_root / ".gitignore").write_text("research-private/study1/\n", encoding="utf-8")
    monkeypatch.setattr(_c0_module(), "REPOSITORY_ROOT", repository_root, raising=False)


def _write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value), encoding="utf-8")


def synthetic_c0_root(tmp_path: Path) -> Path:
    """Create the smallest non-sensitive frozen-C0 shaped fixture."""
    root = tmp_path / "frozen-c0"
    for index, setting in enumerate(SETTINGS):
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
                "uncovered_fragments": [{"label": "Alternative", "severity": "High"}],
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


def test_adapter_manifest_detects_a_selected_input_mutation(tmp_path: Path):
    root = synthetic_c0_root(tmp_path)
    manifest = build_manifest(root)
    selected = root / "eval_output" / "ucd_ch" / "agentA_guideline_mapping.json"
    selected.write_text('{"clusters": []}', encoding="utf-8")

    with pytest.raises(C0MutationError, match="changed"):
        assert_manifest_unchanged(root, manifest)


def test_adapter_orders_uuid5_events_and_exposes_all_policy_signals(tmp_path: Path):
    events = adapt_c0_root(synthetic_c0_root(tmp_path))
    repeat = adapt_c0_root(synthetic_c0_root(tmp_path / "repeat"))

    assert [event["event_id"] for event in events] == [event["event_id"] for event in repeat]
    assert [event["stage"] for event in events] == sorted(
        (event["stage"] for event in events),
        key=("template", "guideline", "case_inspection", "variability_classification").index,
    )
    assert all(event["event_id"].count("-") == 4 for event in events)
    assert all(len(event["signals"]) == 8 for event in events)
    requested = next(event for event in events if event["stage"] == "variability_classification")
    signals = {signal["signal_id"]: signal for signal in requested["signals"]}
    assert signals["claim_uncertainty"]["observation"] == {
        "kind": "policy_input",
        "normalized_value": 0.8,
        "missing_value_policy": "force_escalation",
    }
    assert signals["evidence_quality"]["observation"] == {
        "kind": "policy_input",
        "missing_value_policy": "force_undetermined",
    }
    assert signals["novelty_vs_judgment_store"]["observation"] == {
        "kind": "policy_input",
        "normalized_value": 0.9,
    }
    replay = candidate_to_replay_event(requested)
    replay_signals = {item["signalId"]: item for item in replay["signalObservations"]}
    assert replay_signals["claim_uncertainty"] == {
        "signalId": "claim_uncertainty",
        "normalizedValue": 0.8,
        "missing": True,
        "missingValuePolicy": "force_escalation",
    }


def test_agent_c_high_severity_does_not_fabricate_error_consequence(tmp_path: Path):
    events = adapt_c0_root(synthetic_c0_root(tmp_path))
    case_event = next(event for event in events if event["stage"] == "case_inspection")
    signals = {signal["signal_id"]: signal for signal in case_event["signals"]}

    assert signals["unreviewed_error_consequence"] == {
        "signal_id": "unreviewed_error_consequence",
        "observation": {"kind": "unavailable"},
        "evidence_state": "unavailable",
    }


def test_adapter_uses_one_immutable_byte_snapshot_for_hashing_and_parsing(
    tmp_path: Path, monkeypatch
):
    """Catches parsing a later filesystem read than the bytes used for source provenance."""
    module = _c0_module()
    root = synthetic_c0_root(tmp_path)
    target = root / "eval_output" / "ucd_ch" / "agentA_guideline_mapping.json"
    original_read_local_bytes = module.read_local_bytes
    original_write_text = Path.write_text
    mutated = False

    def _read_and_mutate(path: Path, *args, **kwargs) -> bytes:
        nonlocal mutated
        content = original_read_local_bytes(path, *args, **kwargs)
        if path == target and not mutated:
            mutated = True
            original_write_text(path, '{"clusters": []}', encoding="utf-8")
        return content

    monkeypatch.setattr(module, "read_local_bytes", _read_and_mutate)

    events = module.adapt_c0_root(root)

    assert sum(event["stage"] == "template" for event in events) == 4


def test_byte_identical_files_at_one_stage_have_unique_event_ids(tmp_path: Path):
    """Catches UUID generation that omits the selected file's opaque locator identity."""
    root = synthetic_c0_root(tmp_path)
    source = root / "eval_output" / "ucd_ch" / "agentC_case_synthetic.json"
    duplicate = source.with_name("agentC_case_duplicate.json")
    duplicate.write_bytes(source.read_bytes())

    events = adapt_c0_root(root)
    event_ids = [event["event_id"] for event in events]

    assert len(event_ids) == len(set(event_ids))


def test_six_arms_share_events_budgets_and_deterministic_random_replay(tmp_path: Path):
    events = adapt_c0_root(synthetic_c0_root(tmp_path))
    first = run_baselines(events)
    second = run_baselines(events)

    assert set(first) == {"5", "10", "20"}
    for rate, result in first.items():
        assert result["budget"] == max(1, len(events) * int(rate) // 100)
        assert set(result["arms"]) == {
            "never_ask",
            "always_ask",
            "random_at_budget",
            "uncertainty_only",
            "fixed_threshold",
            "proposed_joint_policy",
        }
        assert all(arm["event_ids"] == result["event_ids"] for arm in result["arms"].values())
        assert result["arms"]["random_at_budget"] == second[rate]["arms"]["random_at_budget"]
        proposed = result["arms"]["proposed_joint_policy"]
        assert all(decision["selected_reviewer_id"] is None for decision in proposed["decisions"])
        assert any(
            "no_selectable_reviewer" in decision["reason"] for decision in proposed["decisions"]
        )


def test_artifacts_are_sanitized_and_private_root_is_enforced(tmp_path: Path):
    root = synthetic_c0_root(tmp_path)
    private_root = _private_root(tmp_path)
    result = write_baseline_artifacts(root, private_root)
    public_json = json.loads(
        (private_root / "sanitized" / "study1-c0-baseline-summary.json").read_text(encoding="utf-8")
    )
    markdown = (private_root / "sanitized" / "study1-c0-baseline-summary.md").read_text(
        encoding="utf-8"
    )
    rendered = json.dumps(public_json)

    assert result["claim_boundary"] == "descriptive_candidate_escalation_only_no_outcome_evidence"
    assert "agentA_guideline_mapping.json" not in rendered
    assert "synthetic" not in rendered
    assert str(root) not in rendered
    assert "candidate_signal_availability_by_stage" in public_json
    assert all("pairwise_jaccard_overlap" in rate for rate in public_json["rates"].values())
    manifest = json.loads((private_root / "frozen-c0-manifest.json").read_text(encoding="utf-8"))
    expected_manifest_hash = (
        "sha256:"
        + hashlib.sha256(
            json.dumps(manifest, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode(
                "utf-8"
            )
        ).hexdigest()
    )
    assert public_json["frozen_manifest"] == {
        "manifest_hash": expected_manifest_hash,
        "mutation_check": "passed",
    }
    assert public_json["seed"] == 20260902
    assert public_json["report_hashes"] == {
        "candidate_events": public_json["report_hashes"]["candidate_events"],
        "frozen_manifest": expected_manifest_hash,
        "replay_ledgers": public_json["report_hashes"]["replay_ledgers"],
    }
    assert set(public_json["selection_stability_by_arm"]) == {
        "never_ask",
        "always_ask",
        "random_at_budget",
        "uncertainty_only",
        "fixed_threshold",
        "proposed_joint_policy",
    }
    assert all(
        0.0 <= score <= 1.0
        for rate_pairs in public_json["selection_stability_by_arm"].values()
        for score in rate_pairs.values()
    )
    for rate in public_json["rates"].values():
        for arm in rate["arms"].values():
            coverage = arm["candidate_coverage_by_stage"]
            assert set(coverage) == {
                "template",
                "guideline",
                "case_inspection",
                "variability_classification",
            }
            assert all(0.0 <= stage["escalation_fraction"] <= 1.0 for stage in coverage.values())
    for required_section in (
        "Frozen manifest check",
        "Candidate counts",
        "Signal availability by stage",
        "Queue and budget use",
        "Trigger attribution",
        "Candidate coverage by stage",
        "Pairwise Jaccard overlap",
        "Selection stability across budgets",
        "Deterministic report hashes",
        "descriptive_candidate_escalation_only_no_outcome_evidence",
    ):
        assert required_section in markdown


def test_results_template_top_level_fields_match_generated_safe_summary(tmp_path: Path):
    """Catches template fields that cannot be populated from the actual sanitized summary."""
    root = synthetic_c0_root(tmp_path)
    summary = write_baseline_artifacts(root, _private_root(tmp_path))
    template = (
        Path(__file__).resolve().parents[2]
        / "docs"
        / "research"
        / "study-1"
        / "results-template.md"
    ).read_text(encoding="utf-8")
    template_keys = {
        line.split("`")[1]
        for line in template.splitlines()
        if line.startswith("| `") and "." not in line.split("`")[1]
    }

    assert template_keys == set(summary)
    assert "`report_hashes.candidate_events`" in template
    assert "`report_hashes.replay_ledgers`" in template
    assert "`report_hashes.frozen_manifest`" in template
    with pytest.raises(C0ValidationError, match="research-private/study1"):
        write_baseline_artifacts(root, tmp_path / "not-private")


def test_c0_output_rejects_private_lookalikes_and_unignored_repository_paths(tmp_path: Path):
    """Catches output authorization based only on path spelling rather than repository ownership."""
    module = _c0_module()
    root = synthetic_c0_root(tmp_path)
    lookalike = tmp_path / "unapproved" / "research-private" / "study1" / "baseline"

    with pytest.raises(module.C0ValidationError, match="repository.*research-private.*study1"):
        module.write_baseline_artifacts(root, lookalike)

    repository_root = tmp_path / "unignored-repository"
    repository_root.mkdir()
    subprocess.run(["git", "init", "-q", str(repository_root)], check=True)
    module.REPOSITORY_ROOT = repository_root
    with pytest.raises(module.C0ValidationError, match="Git-ignore"):
        module.write_baseline_artifacts(
            root, repository_root / "research-private" / "study1" / "baseline"
        )


@pytest.mark.parametrize("remote_value", ["s3" + ":study1-c0", "\\" + r"\server\share\c0"])
def test_c0_rejects_uri_and_unc_source_roots_before_filesystem_probing(
    tmp_path: Path, remote_value: str
):
    """Catches remote C0 values reaching eval_output filesystem inspection."""
    with pytest.raises(C0ValidationError, match="remote"):
        write_baseline_artifacts(remote_value, _private_root(tmp_path))


@pytest.mark.parametrize(
    "remote_value", ["file" + "://study1-output", "\\" + r"\server\share\output"]
)
def test_c0_rejects_uri_and_unc_output_roots_before_source_reads(tmp_path: Path, remote_value: str):
    """Catches remote outputs reaching any C0 source selection or hashing."""
    with pytest.raises(C0ValidationError, match="remote"):
        write_baseline_artifacts(tmp_path / "must-not-read", remote_value)
