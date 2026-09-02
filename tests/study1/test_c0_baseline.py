"""Synthetic contract tests for the frozen Study 1 C0 baseline adapter."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from vego_study1.c0 import (
    C0MutationError,
    C0ValidationError,
    adapt_c0_root,
    assert_manifest_unchanged,
    build_manifest,
    run_baselines,
    write_baseline_artifacts,
)

SETTINGS = ("ucd_ch", "ucd_pw", "cd_ch", "cd_pw")


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
    assert signals["claim_uncertainty"]["observation"] == "missing_force_escalation"
    assert signals["evidence_quality"]["observation"] == "missing_force_undetermined"
    assert signals["novelty_vs_judgment_store"]["observation"] == "normalized:0.900"


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
        assert any("no_selectable_reviewer" in decision["reason"] for decision in proposed["decisions"])


def test_artifacts_are_sanitized_and_private_root_is_enforced(tmp_path: Path):
    root = synthetic_c0_root(tmp_path)
    private_root = tmp_path / "research-private" / "study1" / "baseline"
    result = write_baseline_artifacts(root, private_root)
    public_json = json.loads(
        (private_root / "sanitized" / "study1-c0-baseline-summary.json").read_text(encoding="utf-8")
    )
    rendered = json.dumps(public_json)

    assert result["claim_boundary"] == "descriptive_candidate_escalation_only_no_outcome_evidence"
    assert "agentA_guideline_mapping.json" not in rendered
    assert "synthetic" not in rendered
    assert str(root) not in rendered
    assert "candidate_signal_availability_by_stage" in public_json
    assert all("pairwise_jaccard_overlap" in rate for rate in public_json["rates"].values())
    with pytest.raises(C0ValidationError, match="research-private/study1"):
        write_baseline_artifacts(root, tmp_path / "not-private")
