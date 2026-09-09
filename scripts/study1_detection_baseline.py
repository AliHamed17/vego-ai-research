"""Detection baseline: what the recorded answers looked like, and when the rule would fire.

The question this answers is operational rather than scientific: across the conversations we
recorded, how sure did the answering agent say it was, and at which point in the conversation did
the first not-fully-sure answer arrive? The second number is the moment the frozen rule would
first have something to fire on.

Three things are deliberately *not* claimed anywhere in the output:

  * a `Low` label is the answering agent's own stated confidence, not a finding that the answer
    was wrong. Nothing here knows whether any answer was correct;
  * a detection point is where the rule *would* fire, not where a problem occurred;
  * each run keeps its own denominator. There is no combined row, because the runs used different
    case counts and configurations.

The unverified pilot run is excluded entirely rather than shown with dashes: this file is about
answer-level detail, and publishing answer-level detail for a run a reader cannot verify would be
worse than omitting it.

No provider is contacted.
"""

from __future__ import annotations

import argparse
import collections
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from airtravel_detector_analysis import project_episodes  # noqa: E402
from extract_qa_escalation_features import detect_detector_v1  # noqa: E402

COMPLETE = {"CONVERGED", "TERMINATED_MAX_ROUNDS"}
CONFIDENCE_ORDER = ["High", "Medium", "Low"]
MAX_ROUNDS = 10

RUNS = [
    {"key": "run0", "run_id": "REAL-efe686a-20260905T2303Z", "cases": 4,
     "dir": "external_data/airtravel-pr38/v4-real-run/output"},
    {"key": "run1", "run_id": "FULLFRAME-01", "cases": 21,
     "dir": "external_data/airtravel-pr38/full-frame-run/output"},
    {"key": "run2", "run_id": "FULLFRAME-02", "cases": 21,
     "dir": "external_data/airtravel-pr38/full-frame-run-02/output"},
]

SIGNALS = ["S1_LOW_ANSWER_CONFIDENCE", "S2_MEDIUM_ANSWER_CONFIDENCE",
           "S3_MISSING_ANSWER_EVIDENCE", "S6_MULTIPLE_QA_ROUNDS",
           "S7_TERMINATED_MAX_ROUNDS"]

SIGNAL_PLAIN = {
    "S1_LOW_ANSWER_CONFIDENCE": "an answer said 'not sure'",
    "S2_MEDIUM_ANSWER_CONFIDENCE": "an answer said 'partly sure'",
    "S3_MISSING_ANSWER_EVIDENCE": "an answer gave no evidence",
    "S6_MULTIPLE_QA_ROUNDS": "took more than one round",
    "S7_TERMINATED_MAX_ROUNDS": "hit the round limit without settling",
}


def load_events(output_dir: Path) -> list[dict[str, Any]]:
    return [
        json.loads(line)
        for line in (output_dir / "qa_events.jsonl").read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def analyse(spec: dict[str, Any]) -> dict[str, Any]:
    events = load_events(ROOT / spec["dir"])
    round_of = {
        event["question_id"]: (event.get("round_index") or 0)
        for event in events
        if event["event_type"] == "QUESTION_EMITTED"
    }
    case_of: dict[str, Any] = {}
    for event in events:
        case_of.setdefault(event["episode_id"], event.get("case_id"))

    episodes = {ep["episode_id"]: ep for ep in project_episodes(events)}
    complete_ids = {
        eid for eid, ep in episodes.items() if ep.get("termination_reason") in COMPLETE
    }

    answers_by_episode: dict[str, list[tuple[int, str]]] = collections.defaultdict(list)
    confidence = collections.Counter()
    per_round = collections.Counter()
    evidence_lengths: list[int] = []
    for event in events:
        if event["event_type"] != "ANSWER_RECEIVED":
            continue
        label = event.get("answer_confidence")
        rnd = round_of.get(event.get("question_id"), 0)
        confidence[label] += 1
        per_round[rnd] += 1
        evidence_lengths.append((event.get("answer_evidence_ref") or {}).get("length", 0))
        if event["episode_id"] in complete_ids:
            answers_by_episode[event["episode_id"]].append((rnd, label))

    first_unsure = collections.Counter()
    first_low = collections.Counter()
    never_unsure = 0
    lengths: list[int] = []
    for eid in complete_ids:
        rows = sorted(answers_by_episode.get(eid, []))
        lengths.append(len(rows))
        unsure = [rnd for rnd, label in rows if label != "High"]
        low = [rnd for rnd, label in rows if label == "Low"]
        if unsure:
            first_unsure[min(unsure)] += 1
        else:
            never_unsure += 1
        if low:
            first_low[min(low)] += 1

    total_complete = len(complete_ids)
    cumulative = []
    running = 0
    for rnd in range(1, MAX_ROUNDS + 1):
        running += first_unsure.get(rnd, 0)
        cumulative.append(
            {"round": rnd, "detected_by_here": running,
             "share": round(running / total_complete, 4) if total_complete else None}
        )

    signal_counts = collections.Counter()
    classes = collections.Counter()
    per_case: dict[str, dict[str, Any]] = {}
    for eid in complete_ids:
        verdict = detect_detector_v1(episodes[eid])
        classes[verdict["classification"]] += 1
        for signal in verdict["all_signals_fired"]:
            signal_counts[signal] += 1
        case = case_of.get(eid) or "RUN_GLOBAL"
        row = per_case.setdefault(case, {"episodes": 0, "classes": collections.Counter()})
        row["episodes"] += 1
        row["classes"][verdict["classification"]] += 1

    return {
        "run_key": spec["key"],
        "run_id": spec["run_id"],
        "cases_in_run": spec["cases"],
        "complete_episodes": total_complete,
        "answers_total": sum(confidence.values()),
        "confidence_counts": {label: confidence.get(label, 0) for label in CONFIDENCE_ORDER},
        "confidence_share": {
            label: round(confidence.get(label, 0) / max(sum(confidence.values()), 1), 4)
            for label in CONFIDENCE_ORDER
        },
        "answers_per_round": {str(r): per_round.get(r, 0) for r in range(1, MAX_ROUNDS + 1)},
        "first_unsure_answer_round": {str(r): first_unsure.get(r, 0)
                                      for r in range(1, MAX_ROUNDS + 1)},
        "first_low_answer_round": {str(r): first_low.get(r, 0) for r in range(1, MAX_ROUNDS + 1)},
        "episodes_with_no_unsure_answer": never_unsure,
        "cumulative_detection_by_round": cumulative,
        "episode_lengths": sorted(lengths),
        "evidence_length_values": sorted(evidence_lengths),
        "signal_episode_counts": {s: signal_counts.get(s, 0) for s in SIGNALS},
        "detector_classes": dict(classes),
        "per_case": {
            case: {"episodes": row["episodes"], "classes": dict(row["classes"])}
            for case, row in sorted(per_case.items())
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    runs = [analyse(spec) for spec in RUNS]
    report = {
        "schema_version": "study1-detection-baseline-v1",
        "evidence_class": "ARCHIVAL / RETROSPECTIVE DESCRIPTIVE EVIDENCE",
        "pooling": "PROHIBITED - each run keeps its own denominator; there is no combined row",
        "excluded": {
            "HOTSPOT-01": "PREREGISTERED_NOT_EXECUTED_OR_UNVERIFIED; answer-level detail is not "
                          "published for a run a reader cannot verify from this head",
        },
        "confidence_label_meaning": (
            "the answering agent's own stated confidence in its answer. It is not a judgement "
            "that the answer was right or wrong, and nothing here knows which answers were correct"
        ),
        "detection_point_meaning": (
            "the round carrying the first not-fully-sure answer, which is the earliest point the "
            "frozen rule would have had something to fire on. It is not the point at which a "
            "problem occurred"
        ),
        "signal_plain_language": SIGNAL_PLAIN,
        "runs": runs,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(
        json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(json.dumps({"written": str(args.out), "runs": [r["run_key"] for r in runs]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
