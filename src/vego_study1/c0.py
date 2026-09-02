"""Deterministic, privacy-safe adapter for a user-selected frozen C0 root.

This module deliberately reads only the four frozen C0 setting directories at
runtime.  It derives opaque candidate-event records and never persists source
paths, source identifiers, descriptions, or fragments.
"""

from __future__ import annotations

import hashlib
import json
from collections import Counter
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from uuid import NAMESPACE_URL, uuid5

from vego_governed.policy import SIGNAL_IDS, replay_all

from .privacy import validate_candidate_event

SETTINGS = ("ucd_ch", "ucd_pw", "cd_ch", "cd_pw")
STAGES = ("template", "guideline", "case_inspection", "variability_classification")
SEED = 20260902
CLAIM_BOUNDARY = "descriptive_candidate_escalation_only_no_outcome_evidence"
_PRIVATE_ROOT_PARTS = ("research-private", "study1")


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


def _canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _sha256_bytes(value: bytes) -> str:
    return "sha256:" + hashlib.sha256(value).hexdigest()


def _hash_file(path: Path) -> str:
    return _sha256_bytes(path.read_bytes())


def _locator_hash(*parts: object) -> str:
    return _sha256_bytes("|".join(str(part) for part in parts).encode("utf-8"))


def _read_json(path: Path) -> Mapping[str, Any]:
    try:
        loaded = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
        raise C0ValidationError("selected C0 artifact is not valid UTF-8 JSON") from error
    if not isinstance(loaded, Mapping):
        raise C0ValidationError("selected C0 artifact must contain a JSON object")
    return loaded


def _select_files(c0_root: Path | str) -> tuple[SelectedFile, ...]:
    root = Path(c0_root).resolve()
    evaluation_root = root / "eval_output"
    if not evaluation_root.is_dir():
        raise C0ValidationError("--c0-root must contain eval_output")

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
            directory = evaluation_root / setting
            if not directory.is_dir():
                raise C0ValidationError("all four frozen C0 setting directories are required")
            files = sorted(directory.glob(pattern), key=lambda candidate: candidate.name)
            if stage in {"template", "guideline"} and len(files) != 1:
                raise C0ValidationError("each setting requires one Agent A and one Agent B mapping artifact")
            for index, path in enumerate(files):
                if not path.is_file():
                    continue
                source_hash = _hash_file(path)
                selected.append(
                    SelectedFile(
                        setting=setting,
                        stage=stage,
                        path=path,
                        source_hash=source_hash,
                        locator_hash=_locator_hash(setting, stage, source_hash, index),
                    )
                )
    return tuple(selected)


def build_manifest(c0_root: Path | str) -> dict[str, Any]:
    """Hash every selected input without exposing source paths or contents."""
    selected = _select_files(c0_root)
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


def assert_manifest_unchanged(c0_root: Path | str, manifest: Mapping[str, Any]) -> None:
    """Rehash selected inputs and abort if their canonical selection changed."""
    current = build_manifest(c0_root)
    if _canonical_json(current) != _canonical_json(dict(manifest)):
        raise C0MutationError("a selected frozen C0 input changed during baseline preparation")


def _unavailable(signal_id: str) -> dict[str, str]:
    return {"signal_id": signal_id, "observation": "unavailable", "evidence_state": "unavailable"}


def _normalized(signal_id: str, value: float, *, evidence_state: str = "derived") -> dict[str, str]:
    return {
        "signal_id": signal_id,
        "observation": f"normalized:{value:.3f}",
        "evidence_state": evidence_state,
    }


def _missing(signal_id: str, policy: str) -> dict[str, str]:
    return {
        "signal_id": signal_id,
        "observation": f"missing_{policy}",
        "evidence_state": "derived",
    }


def _signals(overrides: Mapping[str, dict[str, str]]) -> list[dict[str, str]]:
    return [dict(overrides.get(signal_id, _unavailable(signal_id))) for signal_id in SIGNAL_IDS]


def _candidate(
    item: SelectedFile,
    ordinal: int,
    *,
    item_type: str,
    signal_overrides: Mapping[str, dict[str, str]],
) -> dict[str, Any]:
    event_id = str(uuid5(NAMESPACE_URL, f"Study1C0|{item.setting}|{item.stage}|{item.source_hash}|{ordinal}"))
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
    clusters = _read_json(item.path).get("clusters", [])
    if not isinstance(clusters, list):
        return
    for index, cluster in enumerate(clusters):
        if not isinstance(cluster, Mapping):
            continue
        confidence = str(cluster.get("match_confidence", "")).strip().lower()
        if not (_is_missing_assignment(cluster.get("base_assignment")) or confidence != "high"):
            continue
        confidence_map = {"low": 0.8, "medium": 0.6}
        overrides: dict[str, dict[str, str]] = {}
        if confidence in confidence_map:
            overrides["claim_uncertainty"] = _normalized(
                "claim_uncertainty", confidence_map[confidence]
            )
        yield _candidate(item, index, item_type="candidate_artifact", signal_overrides=overrides)


def _guideline_candidates(item: SelectedFile) -> Iterable[dict[str, Any]]:
    clusters = _read_json(item.path).get("clusters", [])
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
        numeric = [float(value) for value in certainties if isinstance(value, (int, float)) and not isinstance(value, bool)]
        minimum = min(numeric) if numeric else None
        if not (_is_missing_assignment(cluster.get("base_assignment")) or (minimum is not None and minimum < 0.8)):
            continue
        overrides: dict[str, dict[str, str]] = {}
        if minimum is not None:
            overrides["claim_uncertainty"] = _normalized(
                "claim_uncertainty", max(0.0, min(1.0, 1.0 - minimum))
            )
        yield _candidate(item, index, item_type="candidate_artifact", signal_overrides=overrides)


def _case_candidates(item: SelectedFile) -> Iterable[dict[str, Any]]:
    source = _read_json(item.path)
    uncovered = source.get("uncovered_fragments", [])
    if isinstance(uncovered, list):
        for index, fragment in enumerate(uncovered):
            if not isinstance(fragment, Mapping):
                continue
            overrides: dict[str, dict[str, str]] = {}
            if str(fragment.get("label", "")).strip().lower() == "alternative":
                overrides["claim_uncertainty"] = _normalized("claim_uncertainty", 0.8)
            yield _candidate(item, index, item_type="candidate_interaction", signal_overrides=overrides)
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
    classifications = _read_json(item.path).get("variability_classifications", [])
    if not isinstance(classifications, list):
        return
    for index, record in enumerate(classifications):
        if not isinstance(record, Mapping):
            continue
        confidence = str(record.get("confidence", "")).strip().lower()
        undetermined = str(record.get("classification", "")).strip().lower().startswith("undetermined")
        requested = record.get("requires_human_review") is True
        guideline_update = record.get("flag_for_guidelines_update") is True
        if not (confidence in {"low", "medium"} or undetermined or requested or guideline_update):
            continue
        overrides: dict[str, dict[str, str]] = {}
        if requested:
            overrides["claim_uncertainty"] = _missing("claim_uncertainty", "force_escalation")
        elif confidence in {"low", "medium"}:
            overrides["claim_uncertainty"] = _normalized(
                "claim_uncertainty", {"low": 0.8, "medium": 0.6}[confidence]
            )
        if undetermined:
            overrides["evidence_quality"] = _missing("evidence_quality", "force_undetermined")
        if guideline_update:
            overrides["novelty_vs_judgment_store"] = _normalized(
                "novelty_vs_judgment_store", 0.9
            )
        yield _candidate(item, index, item_type="candidate_interaction", signal_overrides=overrides)


def adapt_c0_root(c0_root: Path | str) -> list[dict[str, Any]]:
    """Adapt only selected C0 files into sorted privacy-safe candidate events."""
    candidates: list[dict[str, Any]] = []
    adapters = {
        "template": _template_candidates,
        "guideline": _guideline_candidates,
        "case_inspection": _case_candidates,
        "variability_classification": _variability_candidates,
    }
    for item in _select_files(c0_root):
        candidates.extend(adapters[item.stage](item))
    return sorted(
        candidates,
        key=lambda event: (STAGES.index(str(event["stage"])), event["event_id"]),
    )


def candidate_to_replay_event(candidate: Mapping[str, Any]) -> dict[str, Any]:
    """Translate a candidate record into the unchanged policy engine contract."""
    observations = []
    for signal in candidate["signals"]:
        signal_id = signal["signal_id"]
        observation = signal["observation"]
        policy_observation: dict[str, Any] = {"signalId": signal_id}
        if observation == "missing_force_escalation":
            policy_observation.update({"missing": True, "missingValuePolicy": "force_escalation"})
        elif observation == "missing_force_undetermined":
            policy_observation.update({"missing": True, "missingValuePolicy": "force_undetermined"})
        elif observation.startswith("normalized:"):
            policy_observation["normalizedValue"] = float(observation.split(":", 1)[1])
        else:
            policy_observation["missing"] = True
        observations.append(policy_observation)
    return {
        "eventId": candidate["event_id"],
        "fragmentId": candidate["event_id"],
        "reviewerCandidates": [],
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
                arm_id: {"event_ids": [event["eventId"] for event in replay_events], **ledger.to_dict()}
                for arm_id, ledger in ledgers.items()
            },
        }
    return result


def _jaccard(left: Sequence[str], right: Sequence[str]) -> float:
    left_set, right_set = set(left), set(right)
    union = left_set | right_set
    return 1.0 if not union else len(left_set & right_set) / len(union)


def _sanitized_summary(candidates: Sequence[Mapping[str, Any]], results: Mapping[str, Any]) -> dict[str, Any]:
    availability: dict[str, Counter[str]] = {stage: Counter() for stage in STAGES}
    for event in candidates:
        availability[str(event["stage"])].update(signal["evidence_state"] for signal in event["signals"])
    rates: dict[str, Any] = {}
    for rate, result in results.items():
        arms = result["arms"]
        arm_summary = {}
        for arm_id, ledger in arms.items():
            reasons = Counter(decision["reason"] for decision in ledger["decisions"])
            arm_summary[arm_id] = {
                "queue": {
                    "escalated": len(ledger["escalated_event_ids"]),
                    "deferred": len(ledger["deferred_event_ids"]),
                    "declined": len(ledger["declined_event_ids"]),
                },
                "budget": ledger["budget"],
                "trigger_attribution": dict(sorted(reasons.items())),
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
    return {
        "claim_boundary": CLAIM_BOUNDARY,
        "candidate_count_by_stage": dict(Counter(event["stage"] for event in candidates)),
        "candidate_signal_availability_by_stage": {
            stage: dict(sorted(counts.items())) for stage, counts in availability.items()
        },
        "rates": rates,
        "report_hashes": {
            "candidate_events": _sha256_bytes(_canonical_json(list(candidates)).encode("utf-8")),
            "replay_ledgers": _sha256_bytes(_canonical_json(results).encode("utf-8")),
        },
    }


def _validate_private_root(private_root: Path | str) -> Path:
    root = Path(private_root).resolve()
    parts = tuple(part.lower() for part in root.parts)
    if not any(parts[index : index + 2] == _PRIVATE_ROOT_PARTS for index in range(len(parts) - 1)):
        raise C0ValidationError("private output root must resolve beneath research-private/study1")
    return root


def _summary_markdown(summary: Mapping[str, Any]) -> str:
    lines = ["# Study 1 C0 baseline (sanitized aggregate)", "", f"Claim boundary: `{CLAIM_BOUNDARY}`.", ""]
    lines.extend(["## Candidate counts", "", "| Stage | Candidates |", "| --- | ---: |"])
    for stage, count in sorted(summary["candidate_count_by_stage"].items()):
        lines.append(f"| {stage} | {count} |")
    lines.extend(["", "## Signal availability by stage", "", "| Stage | Derived | Observed | Unavailable |", "| --- | ---: | ---: | ---: |"])
    for stage, counts in sorted(summary["candidate_signal_availability_by_stage"].items()):
        lines.append(
            f"| {stage} | {counts.get('derived', 0)} | {counts.get('observed', 0)} | "
            f"{counts.get('unavailable', 0)} |"
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
    lines.extend(["", "## Trigger attribution", "", "| Rate | Arm | Trigger | Count |", "| ---: | --- | --- | ---: |"])
    for rate, rate_summary in sorted(summary["rates"].items(), key=lambda item: int(item[0])):
        for arm_id, arm in sorted(rate_summary["arms"].items()):
            for trigger, count in sorted(arm["trigger_attribution"].items()):
                lines.append(f"| {rate}% | {arm_id} | {trigger} | {count} |")
    lines.extend(["", "## Pairwise Jaccard overlap", "", "| Rate | Arms | Jaccard |", "| ---: | --- | ---: |"])
    for rate, rate_summary in sorted(summary["rates"].items(), key=lambda item: int(item[0])):
        for arms, overlap in sorted(rate_summary["pairwise_jaccard_overlap"].items()):
            lines.append(f"| {rate}% | {arms} | {overlap:.6f} |")
    lines.extend(["", "## Deterministic report hashes", "", "| Artifact | SHA-256 |", "| --- | --- |"])
    for artifact, value in sorted(summary["report_hashes"].items()):
        lines.append(f"| {artifact} | {value} |")
    return "\n".join(lines) + "\n"


def write_baseline_artifacts(c0_root: Path | str, private_output_root: Path | str) -> dict[str, Any]:
    """Create private manifests/events/ledgers and a separate sanitized aggregate report."""
    output_root = _validate_private_root(private_output_root)
    manifest = build_manifest(c0_root)
    candidates = adapt_c0_root(c0_root)
    results = run_baselines(candidates)
    assert_manifest_unchanged(c0_root, manifest)

    output_root.mkdir(parents=True, exist_ok=True)
    (output_root / "frozen-c0-manifest.json").write_text(_canonical_json(manifest) + "\n", encoding="utf-8")
    (output_root / "candidate-events.json").write_text(_canonical_json(candidates) + "\n", encoding="utf-8")
    (output_root / "replay-ledgers.json").write_text(_canonical_json(results) + "\n", encoding="utf-8")
    summary = _sanitized_summary(candidates, results)
    sanitized = output_root / "sanitized"
    sanitized.mkdir(exist_ok=True)
    (sanitized / "study1-c0-baseline-summary.json").write_text(
        _canonical_json(summary) + "\n", encoding="utf-8"
    )
    (sanitized / "study1-c0-baseline-summary.md").write_text(
        _summary_markdown(summary), encoding="utf-8"
    )
    return summary
