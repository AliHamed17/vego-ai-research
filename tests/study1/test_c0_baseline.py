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
ROOT = Path(__file__).resolve().parents[2]
SHIPPED_POLICY_PATH = ROOT / "VEGO-AI" / "framework" / "selective_intervention_policy.py"


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


def _shipped_selective_policy():
    spec = importlib.util.spec_from_file_location(
        "study1_shipped_selective_intervention_policy",
        SHIPPED_POLICY_PATH,
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _symlink_or_skip(link: Path, target: Path, *, directory: bool = False) -> None:
    try:
        link.symlink_to(target, target_is_directory=directory)
    except OSError as error:
        pytest.skip(f"local symlink creation is unavailable: {error}")


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
    }
    assert signals["claim_uncertainty"]["evidence_state"] == "derived"
    assert signals["claim_uncertainty"]["escalation_request"] == {
        "kind": "requires_human_review",
        "evidence_state": "observed",
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
        "missing": False,
    }
    assert replay["explicitEscalationRequests"] == [
        {
            "signalId": "claim_uncertainty",
            "trigger": "agent_requested_human_review",
            "evidenceState": "observed",
        }
    ]


def test_cooccurring_review_request_and_low_confidence_fire_independent_triggers(
    tmp_path: Path,
) -> None:
    """Catches the observed request fact masking confidence in replay behavior."""
    event = next(
        candidate
        for candidate in adapt_c0_root(synthetic_c0_root(tmp_path))
        if candidate["stage"] == "variability_classification"
    )

    replay_results = run_baselines([event])["20"]["arms"]

    assert replay_results["uncertainty_only"]["decisions"][0]["reason"] == (
        "agent_requested_human_review+undetermined_classification+"
        "low_confidence+guideline_update_proposed"
    )
    assert replay_results["fixed_threshold"]["decisions"][0]["escalate"] is True
    assert "fixed_threshold" in replay_results["fixed_threshold"]["decisions"][0]["reason"]


@pytest.mark.parametrize(
    "classification",
    [
        "Undetermined",
        " undetermined ",
        "Undetermined pending",
        "Undetermined_extra",
    ],
)
def test_variability_undetermined_mapping_matches_the_shipped_comparator(
    tmp_path: Path, classification: str
) -> None:
    """Catches prefix matching that broadens the shipped normalized equality comparator."""
    root = synthetic_c0_root(tmp_path)
    for setting in SETTINGS:
        artifact = (
            root
            / "eval_output"
            / setting
            / "agentD_variability_classes.synthetic.json"
        )
        payload = json.loads(artifact.read_text(encoding="utf-8"))
        payload["variability_classifications"][0]["classification"] = classification
        _write_json(artifact, payload)

    shipped = _shipped_selective_policy()
    source_record = {
        "classification": classification,
        "confidence": "Low",
        "requires_human_review": False,
        "flag_for_guidelines_update": False,
    }
    _needs_review, shipped_reasons = shipped.should_request_human_review(source_record)
    shipped_undetermined = shipped.TRIGGER_UNDETERMINED in shipped_reasons
    candidates = [
        candidate
        for candidate in adapt_c0_root(root)
        if candidate["stage"] == "variability_classification"
    ]

    assert len(candidates) == len(SETTINGS)
    for candidate in candidates:
        evidence_quality = next(
            signal
            for signal in candidate["signals"]
            if signal["signal_id"] == "evidence_quality"
        )
        adapter_undetermined = (
            evidence_quality["observation"].get("missing_value_policy")
            == "force_undetermined"
        )
        assert adapter_undetermined is shipped_undetermined


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


@pytest.mark.parametrize("constant", ["NaN", "Infinity", "-Infinity", "1e999"])
def test_adapter_rejects_non_standard_json_numeric_constants(
    tmp_path: Path, constant: str
) -> None:
    """Catches permissive JSON parsing of values that cannot be serialized portably."""
    root = synthetic_c0_root(tmp_path)
    target = root / "eval_output" / "ucd_ch" / "agentB_guideline_mapping.json"
    target.write_text(
        '{"clusters":[{"run1_guideline":{"mapping_certainty":' + constant + "}}]}",
        encoding="utf-8",
    )

    with pytest.raises(C0ValidationError, match="non_standard_numeric_constant"):
        adapt_c0_root(root)


def test_c0_discovery_safety_checks_entries_before_any_is_file_probe(
    tmp_path: Path, monkeypatch
) -> None:
    """Catches C0 discovery following a leaf before the reparse-point safety gate."""
    root = synthetic_c0_root(tmp_path)

    def _unexpected_is_file(_path: Path) -> bool:
        raise AssertionError("C0 discovery called Path.is_file before safety validation")

    monkeypatch.setattr(Path, "is_file", _unexpected_is_file)

    assert adapt_c0_root(root)


def test_c0_rejects_reparse_point_in_a_parent_component(tmp_path: Path) -> None:
    """Catches a safe-looking C0 leaf reached through an unsafe parent component."""
    real_parent = tmp_path / "real-parent"
    root = synthetic_c0_root(real_parent)
    linked_parent = tmp_path / "linked-parent"
    _symlink_or_skip(linked_parent, real_parent, directory=True)
    aliased_root = linked_parent / root.relative_to(real_parent)

    with pytest.raises(C0ValidationError, match="symlink|reparse"):
        adapt_c0_root(aliased_root)


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
    manifest_path = private_root / "frozen-c0-manifest.json"
    expected_manifest_hash = "sha256:" + hashlib.sha256(manifest_path.read_bytes()).hexdigest()
    assert public_json["frozen_manifest"] == {
        "manifest_hash": expected_manifest_hash,
        "mutation_check": "passed",
    }
    assert public_json["seed"] == 20260902
    emitted_artifacts = {
        "candidate_events": private_root / "candidate-events.json",
        "frozen_manifest": manifest_path,
        "replay_ledgers": private_root / "replay-ledgers.json",
    }
    assert public_json["report_hashes"] == {
        artifact: "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()
        for artifact, path in emitted_artifacts.items()
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
        "Review-request availability by stage",
        "Queue and budget use",
        "Trigger attribution",
        "Candidate coverage by stage",
        "Pairwise Jaccard overlap",
        "Selection stability across budgets",
        "Deterministic report hashes",
        "descriptive_candidate_escalation_only_no_outcome_evidence",
    ):
        assert required_section in markdown


def test_sanitized_reports_reduce_replay_reasons_to_fixed_trigger_categories(
    tmp_path: Path,
) -> None:
    """Catches numeric draws, scores, or candidate-level factors leaking through reason keys."""
    private_root = _private_root(tmp_path)
    summary = write_baseline_artifacts(synthetic_c0_root(tmp_path), private_root)
    markdown = (private_root / "sanitized" / "study1-c0-baseline-summary.md").read_text(
        encoding="utf-8"
    )
    rendered = json.dumps(summary, sort_keys=True) + markdown
    allowed_codes = {
        "arm_rule_triggered",
        "arm_rule_not_triggered",
        "budget_deferred",
    }

    for rate in summary["rates"].values():
        for arm in rate["arms"].values():
            assert set(arm["trigger_attribution"]) == allowed_codes
    assert not any(
        prohibited in rendered
        for prohibited in (
            "seeded_draw=",
            "selection_probability=",
            "mean_signal_score=",
            "fixed_threshold=",
            "combined_score=",
            "escalation_threshold=",
            "agent_requested_human_review",
            "undetermined_classification",
            "low_confidence",
            "guideline_update_proposed",
            "explicit_review_request",
        )
    )


def test_summary_counts_eight_signal_states_once_and_reports_review_requests_separately(
    tmp_path: Path,
) -> None:
    """Catches review-request attachment inflating fixed policy-signal availability."""
    summary = write_baseline_artifacts(synthetic_c0_root(tmp_path), _private_root(tmp_path))

    for stage, candidate_count in summary["candidate_count_by_stage"].items():
        signal_counts = summary["candidate_signal_availability_by_stage"][stage]
        assert sum(signal_counts.values()) == candidate_count * 8
        request_counts = summary["review_request_availability_by_stage"][stage]
        assert sum(request_counts.values()) == candidate_count
    assert sum(
        counts["attached"]
        for counts in summary["review_request_availability_by_stage"].values()
    ) > 0


def test_markdown_receipt_renders_the_json_deterministic_seed(tmp_path: Path) -> None:
    """Catches a Markdown receipt that cannot reproduce the JSON replay configuration."""
    private_root = _private_root(tmp_path)
    summary = write_baseline_artifacts(synthetic_c0_root(tmp_path), private_root)
    markdown = (private_root / "sanitized" / "study1-c0-baseline-summary.md").read_text(
        encoding="utf-8"
    )

    assert f"Deterministic replay seed: `{summary['seed']}`." in markdown


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
    assert f"| `seed` | `{summary['seed']}` |" in template
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


def test_c0_rejects_a_mapped_network_drive_before_filesystem_probing(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Catches a mapped SMB or WebDAV drive treated as a local C0 source."""
    import vego_study1.path_safety as path_safety

    def _drive_type(root: str) -> int:
        return 4 if root.casefold().startswith("z:") else 3

    monkeypatch.setattr(path_safety, "_windows_drive_type", _drive_type, raising=False)
    mapped_source = "Z:" + chr(92) + "controlled-c0"

    with pytest.raises(C0ValidationError, match="mapped network drive"):
        write_baseline_artifacts(mapped_source, _private_root(tmp_path))


@pytest.mark.parametrize(
    "remote_value", ["file" + "://study1-output", "\\" + r"\server\share\output"]
)
def test_c0_rejects_uri_and_unc_output_roots_before_source_reads(tmp_path: Path, remote_value: str):
    """Catches remote outputs reaching any C0 source selection or hashing."""
    with pytest.raises(C0ValidationError, match="remote"):
        write_baseline_artifacts(tmp_path / "must-not-read", remote_value)
