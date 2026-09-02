"""Deterministic, privacy-safe adapter for a user-selected frozen C0 root.

This module deliberately reads only the four frozen C0 setting directories at
runtime.  It derives opaque candidate-event records and never persists source
paths, source identifiers, descriptions, or fragments.
"""

from __future__ import annotations

import hashlib
import json
import math
from collections import Counter
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from uuid import NAMESPACE_URL, uuid5

from vego_governed.policy import SIGNAL_IDS, replay_all

from .path_safety import (
    atomic_write_private_text,
    ensure_private_directory,
    local_path,
    read_local_bytes,
    resolve_local_directory,
    validate_private_output_root,
)
from .privacy import validate_candidate_event

SETTINGS = ("ucd_ch", "ucd_pw", "cd_ch", "cd_pw")
STAGES = ("template", "guideline", "case_inspection", "variability_classification")
SEED = 20260902
CLAIM_BOUNDARY = "descriptive_candidate_escalation_only_no_outcome_evidence"
REPOSITORY_ROOT = Path(__file__).resolve().parents[2]


class C0ValidationError(ValueError):
    """Raised when a C0 root or output location does not meet the frozen contract."""


class C0MutationError(C0ValidationError):
    """Raised when a selected frozen input changes during a run."""


@dataclass(frozen=True)
class SelectedFile:
    """Internal-only description of a selected C0 source file."""

    setting: str
    stage: str
    path: Path
    source_hash: str
    locator_hash: str
    content: bytes


def _canonical_json(value: Any) -> str:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )


def _sha256_bytes(value: bytes) -> str:
    return "sha256:" + hashlib.sha256(value).hexdigest()


def _serialized_json_bytes(value: Any) -> bytes:
    return (_canonical_json(value) + "\n").encode("utf-8")


def _locator_hash(*parts: object) -> str:
    return _sha256_bytes("|".join(str(part) for part in parts).encode("utf-8"))


def _read_json(content: bytes) -> Mapping[str, Any]:
    def _reject_constant(_value: str) -> None:
        raise ValueError("non_standard_numeric_constant")

    try:
        loaded = json.loads(content.decode("utf-8"), parse_constant=_reject_constant)
    except ValueError as error:
        if str(error) == "non_standard_numeric_constant":
            raise C0ValidationError(
                "selected C0 artifact validation failed [non_standard_numeric_constant]"
            ) from error
        raise C0ValidationError("selected C0 artifact is not valid UTF-8 JSON") from error
    if _contains_non_finite_number(loaded):
        raise C0ValidationError(
            "selected C0 artifact validation failed [non_standard_numeric_constant]"
        )
    if not isinstance(loaded, Mapping):
        raise C0ValidationError("selected C0 artifact must contain a JSON object")
    return loaded


def _contains_non_finite_number(value: Any) -> bool:
    if isinstance(value, float):
        return not math.isfinite(value)
    if isinstance(value, Mapping):
        return any(_contains_non_finite_number(item) for item in value.values())
    if isinstance(value, (list, tuple)):
        return any(_contains_non_finite_number(item) for item in value)
    return False


def _select_files(c0_root: Path | str) -> tuple[SelectedFile, ...]:
    root_candidate = local_path(c0_root, "c0_root", C0ValidationError)
    root = resolve_local_directory(root_candidate, "c0_root", C0ValidationError)
    try:
        evaluation_root = resolve_local_directory(
            root / "eval_output",
            "c0_root",
            C0ValidationError,
            containment_root=root,
        )
    except C0ValidationError as error:
        if "symlink" in str(error) or "reparse" in str(error):
            raise
        raise C0ValidationError("--c0-root must contain eval_output") from error

    selected: list[SelectedFile] = []
    patterns = {
        "template": "agentA_guideline_mapping.json",
        "guideline": "agentB_guideline_mapping.json",
        "case_inspection": "agentC_case_*.json",
        "variability_classification": "agentD_variability_classes*.json",
    }
    for stage in STAGES:
        pattern = patterns[stage]
        for setting in SETTINGS:
            try:
                directory = resolve_local_directory(
                    evaluation_root / setting,
                    "c0_root",
                    C0ValidationError,
                    containment_root=evaluation_root,
                )
            except C0ValidationError as error:
                if "symlink" in str(error) or "reparse" in str(error):
                    raise
                raise C0ValidationError(
                    "all four frozen C0 setting directories are required"
                ) from error
            files = sorted(directory.glob(pattern), key=lambda candidate: candidate.name)
            if stage in {"template", "guideline"} and len(files) != 1:
                raise C0ValidationError(
                    "each setting requires one Agent A and one Agent B mapping artifact"
                )
            for index, path in enumerate(files):
                content = read_local_bytes(
                    path,
                    "selected C0 artifact",
                    C0ValidationError,
                    containment_root=evaluation_root,
                )
                source_hash = _sha256_bytes(content)
                selected.append(
                    SelectedFile(
                        setting=setting,
                        stage=stage,
                        path=path,
                        source_hash=source_hash,
                        locator_hash=_locator_hash(setting, stage, source_hash, index),
                        content=content,
                    )
                )
    return tuple(selected)


def _manifest_from_selected(selected: Sequence[SelectedFile]) -> dict[str, Any]:
    return {
        "manifest_version": "Study1FrozenC0Manifest-v1",
        "selected": [
            {
                "setting": item.setting,
                "stage": item.stage,
                "source_hash": item.source_hash,
                "locator_hash": item.locator_hash,
            }
            for item in selected
        ],
    }


def build_manifest(c0_root: Path | str) -> dict[str, Any]:
    """Hash every selected input without exposing source paths or contents."""
    return _manifest_from_selected(_select_files(c0_root))


def assert_manifest_unchanged(c0_root: Path | str, manifest: Mapping[str, Any]) -> None:
    """Rehash selected inputs and abort if their canonical selection changed."""
    current = build_manifest(c0_root)
    if _canonical_json(current) != _canonical_json(dict(manifest)):
        raise C0MutationError("a selected frozen C0 input changed during baseline preparation")


def _unavailable(signal_id: str) -> dict[str, Any]:
    return {
        "signal_id": signal_id,
        "observation": {"kind": "unavailable"},
        "evidence_state": "unavailable",
    }


def _policy_input(
    signal_id: str,
    *,
    normalized_value: float | None = None,
    missing_value_policy: str | None = None,
    evidence_state: str = "derived",
) -> dict[str, Any]:
    observation: dict[str, Any] = {"kind": "policy_input"}
    if normalized_value is not None:
        observation["normalized_value"] = round(normalized_value, 3)
    if missing_value_policy is not None:
        observation["missing_value_policy"] = missing_value_policy
    return {
        "signal_id": signal_id,
        "observation": observation,
        "evidence_state": evidence_state,
    }


def _normalized(signal_id: str, value: float) -> dict[str, Any]:
    return _policy_input(signal_id, normalized_value=value)


def _missing(signal_id: str, policy: str) -> dict[str, Any]:
    return _policy_input(signal_id, missing_value_policy=policy)


def _with_review_request(signal: dict[str, Any]) -> dict[str, Any]:
    return {
        **signal,
        "escalation_request": {
            "kind": "requires_human_review",
            "evidence_state": "observed",
        },
    }


def _signals(overrides: Mapping[str, dict[str, Any]]) -> list[dict[str, Any]]:
    return [dict(overrides.get(signal_id, _unavailable(signal_id))) for signal_id in SIGNAL_IDS]


def _candidate(
    item: SelectedFile,
    ordinal: int,
    *,
    item_type: str,
    signal_overrides: Mapping[str, dict[str, Any]],
) -> dict[str, Any]:
    event_id = str(
        uuid5(
            NAMESPACE_URL,
            f"Study1C0|{item.setting}|{item.stage}|{item.source_hash}|{item.locator_hash}|{ordinal}",
        )
    )
    event = {
        "schema_version": "CandidateEscalationEvent-v1",
        "event_id": event_id,
        "source": {"source_hash": item.source_hash},
        "stage": item.stage,
        "item_type": item_type,
        "sanitized_local_locator": {
            "storage_scope": "private_workspace",
            "locator_hash": _locator_hash(item.locator_hash, ordinal),
        },
        "signals": _signals(signal_overrides),
        "claim_boundary": "candidate_escalation_only",
    }
    return validate_candidate_event(event)


def _is_missing_assignment(value: object) -> bool:
    return value is None or str(value).strip().lower() in {"", "null", "none"}


def _template_candidates(item: SelectedFile) -> Iterable[dict[str, Any]]:
    clusters = _read_json(item.content).get("clusters", [])
    if not isinstance(clusters, list):
        return
    for index, cluster in enumerate(clusters):
        if not isinstance(cluster, Mapping):
            continue
        confidence = str(cluster.get("match_confidence", "")).strip().lower()
        if not (_is_missing_assignment(cluster.get("base_assignment")) or confidence != "high"):
            continue
        confidence_map = {"low": 0.8, "medium": 0.6}
        overrides: dict[str, dict[str, Any]] = {}
        if confidence in confidence_map:
            overrides["claim_uncertainty"] = _normalized(
                "claim_uncertainty", confidence_map[confidence]
            )
        yield _candidate(item, index, item_type="candidate_artifact", signal_overrides=overrides)


def _guideline_candidates(item: SelectedFile) -> Iterable[dict[str, Any]]:
    clusters = _read_json(item.content).get("clusters", [])
    if not isinstance(clusters, list):
        return
    for index, cluster in enumerate(clusters):
        if not isinstance(cluster, Mapping):
            continue
        certainties = [
            cluster.get(f"run{run}_guideline", {}).get("mapping_certainty")
            for run in (1, 2, 3)
            if isinstance(cluster.get(f"run{run}_guideline"), Mapping)
        ]
        numeric = [
            float(value)
            for value in certainties
            if isinstance(value, (int, float)) and not isinstance(value, bool)
        ]
        minimum = min(numeric) if numeric else None
        if not (
            _is_missing_assignment(cluster.get("base_assignment"))
            or (minimum is not None and minimum < 0.8)
        ):
            continue
        overrides: dict[str, dict[str, Any]] = {}
        if minimum is not None:
            overrides["claim_uncertainty"] = _normalized(
                "claim_uncertainty", max(0.0, min(1.0, 1.0 - minimum))
            )
        yield _candidate(item, index, item_type="candidate_artifact", signal_overrides=overrides)


def _case_candidates(item: SelectedFile) -> Iterable[dict[str, Any]]:
    source = _read_json(item.content)
    uncovered = source.get("uncovered_fragments", [])
    if isinstance(uncovered, list):
        for index, fragment in enumerate(uncovered):
            if not isinstance(fragment, Mapping):
                continue
            overrides: dict[str, dict[str, Any]] = {}
            if str(fragment.get("label", "")).strip().lower() == "alternative":
                overrides["claim_uncertainty"] = _normalized("claim_uncertainty", 0.8)
            yield _candidate(
                item, index, item_type="candidate_interaction", signal_overrides=overrides
            )
    potential = source.get("potential_found", [])
    if isinstance(potential, list):
        offset = len(uncovered) if isinstance(uncovered, list) else 0
        for index, match in enumerate(potential):
            if not isinstance(match, Mapping):
                continue
            overrides = {}
            if str(match.get("compliance_status", "")).strip().lower() == "partially-satisfied":
                overrides["claim_uncertainty"] = _normalized("claim_uncertainty", 0.5)
            yield _candidate(
                item, offset + index, item_type="candidate_interaction", signal_overrides=overrides
            )


def _variability_candidates(item: SelectedFile) -> Iterable[dict[str, Any]]:
    classifications = _read_json(item.content).get("variability_classifications", [])
    if not isinstance(classifications, list):
        return
    for index, record in enumerate(classifications):
        if not isinstance(record, Mapping):
            continue
        confidence = str(record.get("confidence", "")).strip().lower()
        undetermined = (
            str(record.get("classification", "")).strip().lower().startswith("undetermined")
        )
        requested = record.get("requires_human_review") is True
        guideline_update = record.get("flag_for_guidelines_update") is True
        if not (confidence in {"low", "medium"} or undetermined or requested or guideline_update):
            continue
        overrides: dict[str, dict[str, Any]] = {}
        confidence_value = {"low": 0.8, "medium": 0.6}.get(confidence)
        if confidence_value is not None:
            overrides["claim_uncertainty"] = _normalized(
                "claim_uncertainty", confidence_value
            )
        elif requested:
            overrides["claim_uncertainty"] = _unavailable("claim_uncertainty")
        if requested:
            overrides["claim_uncertainty"] = _with_review_request(
                overrides["claim_uncertainty"]
            )
        if undetermined:
            overrides["evidence_quality"] = _missing("evidence_quality", "force_undetermined")
        if guideline_update:
            overrides["novelty_vs_judgment_store"] = _normalized("novelty_vs_judgment_store", 0.9)
        yield _candidate(item, index, item_type="candidate_interaction", signal_overrides=overrides)


def adapt_c0_root(c0_root: Path | str) -> list[dict[str, Any]]:
    """Adapt only selected C0 files into sorted privacy-safe candidate events."""
    return _adapt_selected(_select_files(c0_root))


def _adapt_selected(selected: Sequence[SelectedFile]) -> list[dict[str, Any]]:
    candidates: list[dict[str, Any]] = []
    adapters = {
        "template": _template_candidates,
        "guideline": _guideline_candidates,
        "case_inspection": _case_candidates,
        "variability_classification": _variability_candidates,
    }
    for item in selected:
        candidates.extend(adapters[item.stage](item))
    return sorted(
        candidates,
        key=lambda event: (STAGES.index(str(event["stage"])), event["event_id"]),
    )


def candidate_to_replay_event(candidate: Mapping[str, Any]) -> dict[str, Any]:
    """Translate independent candidate facts into one policy-engine event."""
    validated = validate_candidate_event(dict(candidate))
    observations = []
    explicit_requests = []
    for signal in validated["signals"]:
        signal_id = signal["signal_id"]
        observation = signal["observation"]
        policy_observation: dict[str, Any] = {"signalId": signal_id}
        if observation["kind"] == "unavailable":
            policy_observation.update({"missing": True, "missingValuePolicy": "exclude_from_score"})
        else:
            if "normalized_value" in observation:
                policy_observation["normalizedValue"] = observation["normalized_value"]
            missing_policy = observation.get("missing_value_policy")
            if missing_policy is not None:
                policy_observation.update({"missing": True, "missingValuePolicy": missing_policy})
            else:
                policy_observation["missing"] = False
        observations.append(policy_observation)
        request = signal.get("escalation_request")
        if request is not None:
            explicit_requests.append(
                {
                    "signalId": signal_id,
                    "trigger": "agent_requested_human_review",
                    "evidenceState": request["evidence_state"],
                }
            )
    return {
        "eventId": validated["event_id"],
        "fragmentId": validated["event_id"],
        "reviewerCandidates": [],
        "explicitEscalationRequests": explicit_requests,
        "signalObservations": observations,
    }


def run_baselines(candidates: Sequence[Mapping[str, Any]]) -> dict[str, dict[str, Any]]:
    """Replay all six arms over identical canonical input for the three budgets."""
    replay_events = [candidate_to_replay_event(candidate) for candidate in candidates]
    result: dict[str, dict[str, Any]] = {}
    for rate in (5, 10, 20):
        budget = max(1, len(replay_events) * rate // 100) if replay_events else 0
        ledgers = replay_all(replay_events, budget=budget, seed=SEED)
        result[str(rate)] = {
            "budget": budget,
            "event_ids": [event["eventId"] for event in replay_events],
            "arms": {
                arm_id: {
                    "event_ids": [event["eventId"] for event in replay_events],
                    **ledger.to_dict(),
                }
                for arm_id, ledger in ledgers.items()
            },
        }
    return result


def _jaccard(left: Sequence[str], right: Sequence[str]) -> float:
    left_set, right_set = set(left), set(right)
    union = left_set | right_set
    return 1.0 if not union else len(left_set & right_set) / len(union)


def _sanitized_summary(
    candidates: Sequence[Mapping[str, Any]],
    results: Mapping[str, Any],
    manifest: Mapping[str, Any],
    artifact_hashes: Mapping[str, str],
) -> dict[str, Any]:
    signal_availability: dict[str, Counter[str]] = {stage: Counter() for stage in STAGES}
    review_request_availability: dict[str, Counter[str]] = {
        stage: Counter() for stage in STAGES
    }
    candidate_ids_by_stage: dict[str, set[str]] = {stage: set() for stage in STAGES}
    for event in candidates:
        stage = str(event["stage"])
        for signal in event["signals"]:
            signal_availability[stage].update([signal["evidence_state"]])
        request_attached = any(signal.get("escalation_request") is not None for signal in event["signals"])
        review_request_availability[stage].update(
            ["attached" if request_attached else "not_attached"]
        )
        candidate_ids_by_stage[stage].add(str(event["event_id"]))
    rates: dict[str, Any] = {}
    for rate, result in results.items():
        arms = result["arms"]
        arm_summary = {}
        for arm_id, ledger in arms.items():
            escalated = set(ledger["escalated_event_ids"])
            trigger_attribution = {
                "arm_rule_triggered": len(ledger["escalated_event_ids"]),
                "arm_rule_not_triggered": len(ledger["declined_event_ids"]),
                "budget_deferred": len(ledger["deferred_event_ids"]),
            }
            arm_summary[arm_id] = {
                "queue": {
                    "escalated": len(ledger["escalated_event_ids"]),
                    "deferred": len(ledger["deferred_event_ids"]),
                    "declined": len(ledger["declined_event_ids"]),
                },
                "budget": ledger["budget"],
                "trigger_attribution": trigger_attribution,
                "candidate_coverage_by_stage": {
                    stage: {
                        "candidate_count": len(candidate_ids),
                        "escalated_count": len(candidate_ids & escalated),
                        "escalation_fraction": (
                            len(candidate_ids & escalated) / len(candidate_ids)
                            if candidate_ids
                            else 0.0
                        ),
                    }
                    for stage, candidate_ids in candidate_ids_by_stage.items()
                },
            }
        overlaps = {
            f"{left}__{right}": _jaccard(
                arms[left]["escalated_event_ids"], arms[right]["escalated_event_ids"]
            )
            for index, left in enumerate(sorted(arms))
            for right in sorted(arms)[index + 1 :]
        }
        rates[rate] = {
            "budget_units": result["budget"],
            "arms": arm_summary,
            "pairwise_jaccard_overlap": overlaps,
        }
    rate_pairs = (("5", "10"), ("5", "20"), ("10", "20"))
    arm_ids = sorted(next(iter(results.values()))["arms"]) if results else []
    selection_stability = {
        arm_id: {
            f"{left}__{right}": _jaccard(
                results[left]["arms"][arm_id]["escalated_event_ids"],
                results[right]["arms"][arm_id]["escalated_event_ids"],
            )
            for left, right in rate_pairs
        }
        for arm_id in arm_ids
    }
    manifest_hash = artifact_hashes["frozen_manifest"]
    return {
        "claim_boundary": CLAIM_BOUNDARY,
        "seed": SEED,
        "frozen_manifest": {
            "manifest_hash": manifest_hash,
            "mutation_check": "passed",
        },
        "candidate_count_by_stage": dict(Counter(event["stage"] for event in candidates)),
        "candidate_signal_availability_by_stage": {
            stage: dict(sorted(counts.items())) for stage, counts in signal_availability.items()
        },
        "review_request_availability_by_stage": {
            stage: {
                status: counts.get(status, 0) for status in ("attached", "not_attached")
            }
            for stage, counts in review_request_availability.items()
        },
        "rates": rates,
        "selection_stability_by_arm": selection_stability,
        "report_hashes": dict(artifact_hashes),
    }


def _validate_private_root(private_root: Path | str) -> Path:
    return validate_private_output_root(private_root, REPOSITORY_ROOT, C0ValidationError)


def _summary_markdown(summary: Mapping[str, Any]) -> str:
    lines = [
        "# Study 1 C0 baseline (sanitized aggregate)",
        "",
        f"Claim boundary: `{CLAIM_BOUNDARY}`.",
        "",
        f"Deterministic replay seed: `{summary['seed']}`.",
        "",
    ]
    lines.extend(
        [
            "## Frozen manifest check",
            "",
            "| Manifest SHA-256 | Mutation check |",
            "| --- | --- |",
            f"| {summary['frozen_manifest']['manifest_hash']} | "
            f"{summary['frozen_manifest']['mutation_check']} |",
            "",
        ]
    )
    lines.extend(["## Candidate counts", "", "| Stage | Candidates |", "| --- | ---: |"])
    for stage, count in sorted(summary["candidate_count_by_stage"].items()):
        lines.append(f"| {stage} | {count} |")
    lines.extend(
        [
            "",
            "## Signal availability by stage",
            "",
            "| Stage | Derived | Observed | Unavailable |",
            "| --- | ---: | ---: | ---: |",
        ]
    )
    for stage, counts in sorted(summary["candidate_signal_availability_by_stage"].items()):
        lines.append(
            f"| {stage} | {counts.get('derived', 0)} | {counts.get('observed', 0)} | "
            f"{counts.get('unavailable', 0)} |"
        )
    lines.extend(
        [
            "",
            "## Review-request availability by stage",
            "",
            "| Stage | Attached | Not attached |",
            "| --- | ---: | ---: |",
        ]
    )
    for stage, counts in sorted(summary["review_request_availability_by_stage"].items()):
        lines.append(
            f"| {stage} | {counts.get('attached', 0)} | {counts.get('not_attached', 0)} |"
        )
    lines.extend(
        [
            "",
            "## Queue and budget use",
            "",
            "| Rate | Arm | Budget | Consumed | Remaining | Escalated | Deferred | Declined |",
            "| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    for rate, rate_summary in sorted(summary["rates"].items(), key=lambda item: int(item[0])):
        for arm_id, arm in sorted(rate_summary["arms"].items()):
            queue, budget = arm["queue"], arm["budget"]
            lines.append(
                f"| {rate}% | {arm_id} | {budget['amount']} | {budget['consumed']} | "
                f"{budget['remaining']} | {queue['escalated']} | {queue['deferred']} | "
                f"{queue['declined']} |"
            )
    lines.extend(
        [
            "",
            "## Trigger attribution",
            "",
            "| Rate | Arm | Trigger | Count |",
            "| ---: | --- | --- | ---: |",
        ]
    )
    for rate, rate_summary in sorted(summary["rates"].items(), key=lambda item: int(item[0])):
        for arm_id, arm in sorted(rate_summary["arms"].items()):
            for trigger, count in sorted(arm["trigger_attribution"].items()):
                lines.append(f"| {rate}% | {arm_id} | {trigger} | {count} |")
    lines.extend(
        [
            "",
            "## Candidate coverage by stage",
            "",
            "| Rate | Arm | Stage | Candidates | Escalated | Escalation fraction |",
            "| ---: | --- | --- | ---: | ---: | ---: |",
        ]
    )
    for rate, rate_summary in sorted(summary["rates"].items(), key=lambda item: int(item[0])):
        for arm_id, arm in sorted(rate_summary["arms"].items()):
            for stage, coverage in sorted(arm["candidate_coverage_by_stage"].items()):
                lines.append(
                    f"| {rate}% | {arm_id} | {stage} | {coverage['candidate_count']} | "
                    f"{coverage['escalated_count']} | {coverage['escalation_fraction']:.6f} |"
                )
    lines.extend(
        [
            "",
            "## Pairwise Jaccard overlap",
            "",
            "| Rate | Arms | Jaccard |",
            "| ---: | --- | ---: |",
        ]
    )
    for rate, rate_summary in sorted(summary["rates"].items(), key=lambda item: int(item[0])):
        for arms, overlap in sorted(rate_summary["pairwise_jaccard_overlap"].items()):
            lines.append(f"| {rate}% | {arms} | {overlap:.6f} |")
    lines.extend(
        [
            "",
            "## Selection stability across budgets",
            "",
            "| Arm | Budget pair | Jaccard |",
            "| --- | --- | ---: |",
        ]
    )
    for arm_id, comparisons in sorted(summary["selection_stability_by_arm"].items()):
        for budget_pair, score in sorted(comparisons.items()):
            lines.append(f"| {arm_id} | {budget_pair} | {score:.6f} |")
    lines.extend(
        ["", "## Deterministic report hashes", "", "| Artifact | SHA-256 |", "| --- | --- |"]
    )
    for artifact, value in sorted(summary["report_hashes"].items()):
        lines.append(f"| {artifact} | {value} |")
    return "\n".join(lines) + "\n"


def write_baseline_artifacts(
    c0_root: Path | str, private_output_root: Path | str
) -> dict[str, Any]:
    """Create private manifests/events/ledgers and a separate sanitized aggregate report."""
    output_root = _validate_private_root(private_output_root)
    selected = _select_files(c0_root)
    manifest = _manifest_from_selected(selected)
    candidates = _adapt_selected(selected)
    results = run_baselines(candidates)
    assert_manifest_unchanged(c0_root, manifest)
    artifact_bytes = {
        "frozen_manifest": _serialized_json_bytes(manifest),
        "candidate_events": _serialized_json_bytes(candidates),
        "replay_ledgers": _serialized_json_bytes(results),
    }
    artifact_hashes = {
        artifact: _sha256_bytes(content) for artifact, content in artifact_bytes.items()
    }

    ensure_private_directory(output_root, output_root, REPOSITORY_ROOT, C0ValidationError)
    atomic_write_private_text(
        output_root / "frozen-c0-manifest.json",
        artifact_bytes["frozen_manifest"].decode("utf-8"),
        output_root,
        REPOSITORY_ROOT,
        C0ValidationError,
    )
    atomic_write_private_text(
        output_root / "candidate-events.json",
        artifact_bytes["candidate_events"].decode("utf-8"),
        output_root,
        REPOSITORY_ROOT,
        C0ValidationError,
    )
    atomic_write_private_text(
        output_root / "replay-ledgers.json",
        artifact_bytes["replay_ledgers"].decode("utf-8"),
        output_root,
        REPOSITORY_ROOT,
        C0ValidationError,
    )
    summary = _sanitized_summary(candidates, results, manifest, artifact_hashes)
    sanitized = output_root / "sanitized"
    ensure_private_directory(sanitized, output_root, REPOSITORY_ROOT, C0ValidationError)
    atomic_write_private_text(
        sanitized / "study1-c0-baseline-summary.json",
        _serialized_json_bytes(summary).decode("utf-8"),
        output_root,
        REPOSITORY_ROOT,
        C0ValidationError,
    )
    atomic_write_private_text(
        sanitized / "study1-c0-baseline-summary.md",
        _summary_markdown(summary),
        output_root,
        REPOSITORY_ROOT,
        C0ValidationError,
    )
    return summary
