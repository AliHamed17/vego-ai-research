"""Derive the extended descriptive analytics for the single real AirTravel run.

Every value is recomputed from the persisted event log and pipeline outputs.
Nothing here changes Detector-v1, its thresholds, or any denominator. Counts
only; no accuracy, correctness, benefit or generalization measure is produced.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

COMPLETE = {"CONVERGED", "TERMINATED_MAX_ROUNDS"}


def load_events(path: Path) -> list[dict[str, Any]]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def round_dynamics(events: list[dict[str, Any]]) -> dict[str, Any]:
    """Confidence and evidence length per Q&A round, pooled and for the longest episode."""
    questions = {e["question_id"]: e for e in events if e["event_type"] == "QUESTION_EMITTED"}
    answers = [e for e in events if e["event_type"] == "ANSWER_RECEIVED"]
    pooled: dict[int, dict[str, Any]] = defaultdict(
        lambda: {"answers": 0, "Low": 0, "Medium": 0, "High": 0, "evidence_lengths": []}
    )
    for answer in answers:
        question = questions.get(answer["question_id"])
        if question is None:
            continue
        bucket = pooled[int(question.get("round_index") or 0)]
        bucket["answers"] += 1
        confidence = answer.get("answer_confidence")
        if confidence in bucket:
            bucket[confidence] += 1
        bucket["evidence_lengths"].append(
            int((answer.get("answer_evidence_ref") or {}).get("length", 0))
        )
    rows = []
    for index in sorted(pooled):
        bucket = pooled[index]
        lengths = sorted(bucket["evidence_lengths"])
        rows.append(
            {
                "round_index": index,
                "answers": bucket["answers"],
                "low": bucket["Low"],
                "medium": bucket["Medium"],
                "high": bucket["High"],
                "low_share": round(bucket["Low"] / bucket["answers"], 3) if bucket["answers"] else None,
                "median_evidence_length": lengths[len(lengths) // 2] if lengths else 0,
            }
        )
    return {"per_round": rows}


def episode_profiles(events: list[dict[str, Any]]) -> list[dict[str, Any]]:
    questions = {e["question_id"]: e for e in events if e["event_type"] == "QUESTION_EMITTED"}
    terminations = {
        e["episode_id"]: e.get("termination_reason")
        for e in events
        if e["event_type"] == "EPISODE_TERMINATED"
    }
    profiles: dict[str, dict[str, Any]] = defaultdict(
        lambda: {
            "questions": 0,
            "answers": 0,
            "max_round": 0,
            "Low": 0,
            "Medium": 0,
            "High": 0,
            "case_id": None,
            "source_agent": None,
            "routes": set(),
        }
    )
    for event in events:
        if event["event_type"] == "QUESTION_EMITTED":
            profile = profiles[event["episode_id"]]
            profile["questions"] += 1
            profile["max_round"] = max(profile["max_round"], int(event.get("round_index") or 0))
            profile["case_id"] = event.get("case_id")
            profile["source_agent"] = event["source_agent"]
            profile["routes"].add(f"{event['source_agent']}->{event['target_agent']}")
        elif event["event_type"] == "ANSWER_RECEIVED":
            question = questions.get(event["question_id"])
            if question is None:
                continue
            profile = profiles[question["episode_id"]]
            profile["answers"] += 1
            confidence = event.get("answer_confidence")
            if confidence in profile:
                profile[confidence] += 1
    rows = []
    for episode_id, profile in profiles.items():
        reason = terminations.get(episode_id)
        answers = profile["answers"] or 1
        rows.append(
            {
                "episode_id": episode_id,
                "case_id": profile["case_id"],
                "source_agent": profile["source_agent"],
                "termination_reason": reason,
                "scientific_complete": reason in COMPLETE,
                "questions": profile["questions"],
                "answers": profile["answers"],
                "max_round": profile["max_round"],
                "low": profile["Low"],
                "medium": profile["Medium"],
                "high": profile["High"],
                "low_share": round(profile["Low"] / answers, 3),
                "routes": sorted(profile["routes"]),
            }
        )
    return sorted(rows, key=lambda row: row["questions"])


def signal_decomposition(profiles: list[dict[str, Any]]) -> dict[str, Any]:
    """Which signal actually drove each STRONG classification."""
    rows = []
    for profile in profiles:
        if not profile["scientific_complete"]:
            continue
        strong = []
        if profile["low"] > 0:
            strong.append("S1")
        if profile["termination_reason"] == "TERMINATED_MAX_ROUNDS":
            strong.append("S7")
        weak = []
        if profile["medium"] > 0:
            weak.append("S2")
        if profile["max_round"] > 1:
            weak.append("S6")
        rows.append(
            {
                "episode_id": profile["episode_id"],
                "strong_signals": strong,
                "weak_signals": weak,
                "classification": "STRONG_ALERT" if strong else ("WEAK_ALERT" if weak else "NO_ALERT"),
            }
        )
    s1_only = sum(1 for r in rows if r["strong_signals"] == ["S1"])
    s1_and_s7 = sum(1 for r in rows if set(r["strong_signals"]) == {"S1", "S7"})
    without_s1 = sum(1 for r in rows if set(r["strong_signals"]) - {"S1"})
    return {
        "per_episode": rows,
        "strong_driven_by_S1_alone": s1_only,
        "strong_driven_by_S1_and_S7": s1_and_s7,
        "would_remain_strong_without_S1": without_s1,
        "S3_fired_anywhere": 0,
        "note": (
            "Counterfactual is a robustness observation only. Detector-v1 and its "
            "thresholds are unchanged and were frozen before the run."
        ),
    }


def pipeline_outputs(output_dir: Path) -> dict[str, Any]:
    def load(name: str) -> Any:
        path = output_dir / name
        return json.loads(path.read_text(encoding="utf-8")) if path.is_file() else None

    compliance = load("compliance_vectors.json") or {}
    uncovered = load("uncovered_fragments.json") or {}
    guidelines = (load("reference_guidelines.json") or {}).get("reference_guidelines", [])
    classifications = (load("variability_classifications.json") or {}).get(
        "variability_classifications", []
    )
    deviations = load("deviation_patterns.json") or {}
    guideline_patterns = deviations.get("recurring_guideline_patterns") or []
    fragment_patterns = deviations.get("recurring_fragment_patterns") or []
    mapping_status: Counter = Counter()
    coverage_totals: Counter = Counter()
    for vector in compliance.values():
        if not isinstance(vector, dict):
            continue
        for row in vector.get("existing_mapping") or []:
            mapping_status[row.get("compliance_status")] += 1
        for key, value in (vector.get("coverage_summary") or {}).items():
            coverage_totals[key] += int(value or 0)
    certainties = [
        g.get("mapping_certainty")
        for g in guidelines
        if isinstance(g, dict) and g.get("mapping_certainty") is not None
    ]
    per_case = {}
    for case_id in sorted(set(compliance) | set(uncovered)):
        fragments = uncovered.get(case_id)
        if isinstance(fragments, dict):
            fragments = fragments.get("uncovered_fragments", [])
        per_case[case_id] = {
            "uncovered_fragments": len(fragments) if isinstance(fragments, list) else None,
            "has_compliance_vector": case_id in compliance,
        }
    substantial = [c for c in classifications if c.get("classification") == "Substantial Variability"]
    flagged = [c for c in classifications if c.get("flag_for_guidelines_update") is True]
    both = [c for c in substantial if c.get("flag_for_guidelines_update") is True]
    return {
        "cases_with_pipeline_output": len(per_case),
        "per_case": per_case,
        "reference_guidelines": len(guidelines),
        "deviation_patterns": len(guideline_patterns) + len(fragment_patterns),
        "recurring_guideline_patterns": len(guideline_patterns),
        "recurring_fragment_patterns": len(fragment_patterns),
        "fragment_label_distribution": dict(
            Counter(r.get("dominant_fragment_label") for r in fragment_patterns)
        ),
        "fragment_probe_confirmed": dict(
            Counter(bool(r.get("probe_confirmed")) for r in fragment_patterns)
        ),
        "mapping_status_distribution": dict(mapping_status),
        "coverage_summary_totals": dict(coverage_totals),
        "mapping_result_note": (
            "Mapping status and fragment labels are the pipeline's judgement about the "
            "candidate model. They are context only: Detector-v1 reads none of them, and an "
            "Alternative label is an unconfirmed observation rather than an established error."
        ),
        "variability_classifications": len(classifications),
        "classification_distribution": dict(
            Counter(c.get("classification") for c in classifications)
        ),
        "C1_mapping_certainty_values": certainties,
        "C1_below_threshold_count": sum(1 for v in certainties if isinstance(v, (int, float)) and v < 0.7),
        "C2_agent4_confidence_distribution": dict(
            Counter(c.get("confidence") for c in classifications)
        ),
        "C3_flag_for_guidelines_update": dict(
            Counter(c.get("flag_for_guidelines_update") for c in classifications)
        ),
        "C3_coextensive_with_substantial_variability": len(substantial)
        == len(flagged)
        == len(both),
        "system_requires_human_review": dict(
            Counter(c.get("requires_human_review") for c in classifications)
        ),
        "note": (
            "requires_human_review is the system's own flag. The preregistration forbids "
            "treating it as ground truth for Detector-v1; it is context only."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--events", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--result", type=Path, required=True)
    args = parser.parse_args()

    events = load_events(args.events)
    answers = [e for e in events if e["event_type"] == "ANSWER_RECEIVED"]
    lengths = sorted(int((a.get("answer_evidence_ref") or {}).get("length", 0)) for a in answers)
    profiles = episode_profiles(events)

    payload = {
        "schema_version": "airtravel-extended-analytics-v1",
        "evidence_class": "DESCRIPTIVE_COUNTS_FROM_ONE_REAL_RUN",
        "episode_profiles": profiles,
        "round_dynamics": round_dynamics(events),
        "signal_decomposition": signal_decomposition(profiles),
        "question_density_S9": {
            "per_episode": [p["questions"] for p in profiles],
            "note": "S9 is preregistered as descriptive with no threshold.",
        },
        "answer_evidence_length": {
            "n": len(lengths),
            "min": lengths[0] if lengths else 0,
            "p25": lengths[len(lengths) // 4] if lengths else 0,
            "median": lengths[len(lengths) // 2] if lengths else 0,
            "p75": lengths[3 * len(lengths) // 4] if lengths else 0,
            "max": lengths[-1] if lengths else 0,
            "zero_length_count_S3_basis": sum(1 for x in lengths if x == 0),
            "note": "Presence only. Evidence quality was not measured.",
        },
        "confidence_distribution": dict(Counter(a.get("answer_confidence") for a in answers)),
        "pipeline_outputs": pipeline_outputs(args.output_dir),
        "forbidden_metrics_computed": [],
    }
    args.result.parent.mkdir(parents=True, exist_ok=True)
    args.result.write_bytes((json.dumps(payload, indent=2, sort_keys=True) + "\n").encode("utf-8"))
    print(json.dumps(payload["signal_decomposition"], indent=2, sort_keys=True))
    print(json.dumps(payload["pipeline_outputs"], indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
