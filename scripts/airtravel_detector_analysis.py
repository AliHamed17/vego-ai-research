"""Apply the frozen Detector-v1 to one real AirTravel run.

Episodes are projected from the persisted event log only. INCOMPLETE_TECHNICAL
episodes are excluded from every scientific denominator and reported
separately. No signal definition, threshold or classification rule is defined
here; all of it is imported unchanged from the preregistered detector.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from extract_qa_escalation_features import detect_detector_v1  # noqa: E402

COMPLETE = {"CONVERGED", "TERMINATED_MAX_ROUNDS"}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def project_episodes(events: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Group the event stream into episodes with the fields the detector reads."""
    questions: dict[str, dict[str, Any]] = {}
    by_episode: dict[str, dict[str, Any]] = {}
    for event in events:
        episode_id = event["episode_id"]
        episode = by_episode.setdefault(
            episode_id,
            {
                "episode_id": episode_id,
                "answers": [],
                "round_count": 0,
                "question_count": 0,
                "termination_reason": None,
                "routes": set(),
            },
        )
        kind = event["event_type"]
        if kind == "QUESTION_EMITTED":
            questions[event["question_id"]] = event
            episode["question_count"] += 1
            episode["round_count"] = max(episode["round_count"], event.get("round_index") or 0)
            episode["routes"].add((event["source_agent"], event["target_agent"]))
        elif kind == "ANSWER_RECEIVED":
            evidence = event.get("answer_evidence_ref")
            episode["answers"].append(
                {
                    "question_id": event.get("question_id"),
                    "answer_confidence": event.get("answer_confidence"),
                    "answer_evidence_ref": evidence,
                }
            )
        elif kind == "EPISODE_TERMINATED":
            episode["termination_reason"] = event.get("termination_reason")

    for episode in by_episode.values():
        reason = episode["termination_reason"]
        episode["scientific_complete"] = reason in COMPLETE
        episode["exclusion_reason"] = None if reason in COMPLETE else reason
        episode["routes"] = sorted(episode["routes"])
    return list(by_episode.values())


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--events", type=Path, required=True)
    parser.add_argument("--run-receipt", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()

    events = [
        json.loads(line)
        for line in args.events.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    receipt = json.loads(args.run_receipt.read_text(encoding="utf-8"))
    episodes = project_episodes(events)
    results = [detect_detector_v1(episode) for episode in episodes]

    complete = [e for e in episodes if e["scientific_complete"]]
    incomplete = [e for e in episodes if not e["scientific_complete"]]
    scored = [r for r in results if r["classification"] != "EXCLUDED"]
    classifications = Counter(r["classification"] for r in scored)
    signals = Counter(code for r in scored for code in r["all_signals_fired"])

    args.output_dir.mkdir(parents=True, exist_ok=True)
    with (args.output_dir / "episodes.csv").open("w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        writer.writerow(
            ["episode_id", "termination_reason", "questions", "answers", "rounds",
             "routes", "in_detector_denominator"]
        )
        for episode in episodes:
            writer.writerow(
                [episode["episode_id"], episode["termination_reason"],
                 episode["question_count"], len(episode["answers"]),
                 episode["round_count"],
                 " | ".join(f"{s}->{t}" for s, t in episode["routes"]),
                 episode["scientific_complete"]]
            )

    with (args.output_dir / "detector.csv").open("w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        writer.writerow(["episode_id", "classification", "reason_codes", "all_signals_fired"])
        for result in results:
            writer.writerow(
                [result["episode_id"], result["classification"],
                 " | ".join(result["reason_codes"]),
                 " | ".join(result["all_signals_fired"])]
            )

    summary = {
        "schema_version": "airtravel-study1-detector-summary-v1",
        "setting_id": receipt["setting_id"],
        "corpus_id": receipt["corpus_id"],
        "N": receipt["N"],
        "model": receipt["model_requested"],
        "run_id": receipt["run_id"],
        "run_status": receipt["status"],
        "denominators": {
            "total_episodes_observed": len(episodes),
            "complete_episodes": len(complete),
            "incomplete_technical_episodes": len(incomplete),
            "detector_v1_denominator": len(scored),
        },
        "counts": {
            "questions": sum(e["question_count"] for e in episodes),
            "answers": sum(len(e["answers"]) for e in episodes),
            "max_round_index": max((e["round_count"] for e in episodes), default=0),
            "route_pairs": len({tuple(r) for e in episodes for r in e["routes"]}),
        },
        "termination_states": dict(Counter(e["termination_reason"] for e in episodes)),
        "detector_v1": {
            "STRONG_ALERT": classifications.get("STRONG_ALERT", 0),
            "WEAK_ALERT": classifications.get("WEAK_ALERT", 0),
            "NO_ALERT": classifications.get("NO_ALERT", 0),
            "EXCLUDED": sum(1 for r in results if r["classification"] == "EXCLUDED"),
        },
        "signals_fired": dict(signals),
        "usage": receipt["usage"],
        "evidence": {
            "event_log_sha256": digest(args.events),
            "run_receipt_sha256": digest(args.run_receipt),
            "event_count": len(events),
        },
        "forbidden_metrics_computed": [],
    }
    target = args.output_dir / "detector-summary.json"
    target.write_bytes((json.dumps(summary, indent=2, sort_keys=True, ensure_ascii=False) + "\n").encode("utf-8"))
    print(json.dumps(summary, indent=2, sort_keys=True, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
