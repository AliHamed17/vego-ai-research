"""Compare the independent escalation mechanisms the system already contains.

The pipeline does not have one notion of "this needs a person". It has at least four, produced
by different components at different stages, and they do not agree:

  * **Detector-v1** classifies a Q&A *episode* from conversation state alone — answer confidence,
    evidence presence, round count and termination.
  * **`requires_human_review`** is a per-*pattern* boolean the variability-classification stage
    writes about recurring representations across cases.
  * **Fragment severity and label** are per-*fragment* judgements the coverage stage writes about
    individual uncovered statements, including a `Domain Mistake` label and a severity.
  * **The human-review queue** is the only one of the four whose output would actually reach a
    person, and it is therefore the one whose size matters operationally.

Reporting these side by side is worth doing precisely because they disagree. That disagreement is
a describable property of the system as built, and it is the concrete form of the open question
of *when* to escalate.

**None of them is ground truth, and this module does not treat any of them as ground truth.**
They operate on different units of analysis — episodes, patterns, fragments and queued items — so
they are not
substitutes for one another, agreement between them would not make any of them correct, and
disagreement between them does not show that any one is wrong. No accuracy is computed, because
none is computable without human labels that do not exist for this corpus.

Detector-v1 is imported and applied, never modified. No provider is contacted.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from airtravel_detector_analysis import project_episodes  # noqa: E402
from extract_qa_escalation_features import detect_detector_v1  # noqa: E402

ALERT_CLASSES = {"STRONG_ALERT", "WEAK_ALERT"}
MISTAKE_LABEL = "Domain Mistake"


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8")) if path.is_file() else None


def detector_by_case(output_dir: Path) -> tuple[dict[str, list[str]], dict[str, Any]]:
    events = [
        json.loads(line)
        for line in (output_dir / "qa_events.jsonl").read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    episode_case: dict[str, Any] = {}
    for event in events:
        episode_case.setdefault(event["episode_id"], event.get("case_id"))
    by_case: dict[str, list[str]] = defaultdict(list)
    totals: Counter[str] = Counter()
    for episode in project_episodes(events):
        if not episode.get("scientific_complete"):
            continue
        label = detect_detector_v1(episode)["classification"]
        totals[label] += 1
        case = episode_case.get(episode["episode_id"])
        by_case[case if case is not None else "RUN_GLOBAL"].append(label)
    return dict(by_case), dict(totals)


def fragments_by_case(output_dir: Path) -> dict[str, dict[str, Any]]:
    payload = read_json(output_dir / "uncovered_fragments.json") or {}
    result = {}
    for case_id, block in payload.items():
        rows = block.get("uncovered_fragments", []) if isinstance(block, dict) else []
        mistakes = [row for row in rows if row.get("label") == MISTAKE_LABEL]
        result[case_id] = {
            "fragments": len(rows),
            "labels": dict(Counter(row.get("label") for row in rows)),
            "domain_mistakes": len(mistakes),
            "mistake_severities": dict(Counter(row.get("severity") for row in mistakes)),
            "flags_any_domain_mistake": bool(mistakes),
        }
    return result


def compliance_by_case(output_dir: Path) -> dict[str, dict[str, Any]]:
    payload = read_json(output_dir / "compliance_vectors.json") or {}
    result = {}
    for case_id, block in payload.items():
        if not isinstance(block, dict):
            continue
        statuses = Counter(
            row.get("compliance_status") for row in block.get("existing_mapping", [])
        )
        result[case_id] = {
            "statuses": dict(statuses),
            "any_not_fully_satisfied": any(
                status != "Satisfied" for status in statuses if status is not None
            ),
        }
    return result


def variability_summary(output_dir: Path) -> dict[str, Any]:
    payload = read_json(output_dir / "variability_classifications.json") or {}
    rows = payload.get("variability_classifications", []) if isinstance(payload, dict) else []
    flagged = sum(1 for row in rows if row.get("requires_human_review"))
    return {
        "patterns": len(rows),
        "requires_human_review_true": flagged,
        "requires_human_review_false": len(rows) - flagged,
        "classifications": dict(Counter(row.get("classification") for row in rows)),
        "confidence": dict(Counter(row.get("confidence") for row in rows)),
        "flag_for_guidelines_update_true": sum(
            1 for row in rows if row.get("flag_for_guidelines_update")
        ),
    }


def review_queue_summary(output_dir: Path) -> dict[str, Any]:
    """The queue is the only mechanism whose output would actually reach a person."""
    path = output_dir / "human_review_queue.jsonl"
    if not path.is_file():
        return {"present": False, "note": "this run produced no human-review queue artefact"}
    rows = [line for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    return {
        "present": True,
        "queued_items": len(rows),
        "note": (
            "the queue is the pipeline's own escalation output; its size is reported as an "
            "observation and is not evidence that the queue is right or wrong"
        ),
    }


def analyse(label: str, output_dir: Path) -> dict[str, Any]:
    detector, detector_totals = detector_by_case(output_dir)
    fragments = fragments_by_case(output_dir)
    compliance = compliance_by_case(output_dir)
    variability = variability_summary(output_dir)
    queue = review_queue_summary(output_dir)

    cases = sorted(set(fragments) | set(compliance) | {k for k in detector if k != "RUN_GLOBAL"})
    rows = []
    for case_id in cases:
        classes = detector.get(case_id, [])
        rows.append(
            {
                "case_id": case_id,
                "detector_v1_episodes": len(classes),
                "detector_v1_classes": dict(Counter(classes)),
                "detector_v1_flags_case": any(cls in ALERT_CLASSES for cls in classes),
                "fragment_stage": fragments.get(case_id),
                "compliance_stage": compliance.get(case_id),
            }
        )

    both = sum(
        1
        for row in rows
        if row["detector_v1_flags_case"] and (row["fragment_stage"] or {}).get("flags_any_domain_mistake")
    )
    detector_only = sum(
        1
        for row in rows
        if row["detector_v1_flags_case"]
        and not (row["fragment_stage"] or {}).get("flags_any_domain_mistake")
    )
    fragment_only = sum(
        1
        for row in rows
        if not row["detector_v1_flags_case"]
        and (row["fragment_stage"] or {}).get("flags_any_domain_mistake")
    )
    neither = len(rows) - both - detector_only - fragment_only

    return {
        "run_label": label,
        "cases": len(rows),
        "detector_v1_totals_all_episodes": detector_totals,
        "detector_v1_global_episode_classes": dict(Counter(detector.get("RUN_GLOBAL", []))),
        "variability_stage": variability,
        "human_review_queue": queue,
        "per_case": rows,
        "case_level_crosstab": {
            "note": (
                "a case-level crosstab of two mechanisms that judge different units; it "
                "describes co-occurrence, not correctness, and neither margin is ground truth"
            ),
            "detector_flags_and_fragment_stage_flags": both,
            "detector_flags_only": detector_only,
            "fragment_stage_flags_only": fragment_only,
            "neither_flags": neither,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", action="append", required=True, metavar="LABEL=OUTPUT_DIR")
    parser.add_argument("--out", type=Path, default=None)
    args = parser.parse_args()

    runs = []
    for spec in args.run:
        label, _, path = spec.partition("=")
        runs.append(analyse(label, Path(path)))

    report = {
        "schema_version": "study1-escalation-mechanism-comparison-v1",
        "evidence_class": "ARCHIVAL_RETROSPECTIVE_DESCRIPTIVE_EVIDENCE",
        "units_of_analysis": {
            "detector_v1": "Q&A episode",
            "requires_human_review": "recurring variability pattern",
            "fragment_severity_and_label": "individual uncovered fragment",
            "human_review_queue": "whatever the pipeline actually queues for a person",
        },
        "no_ground_truth": (
            "none of these mechanisms is ground truth; agreement would not make any of them "
            "correct and disagreement does not show any of them wrong"
        ),
        "not_computed_because_not_computable": [
            "accuracy, precision, recall, F1",
            "which mechanism is right",
            "whether any flagged item was actually an error",
        ],
        "detector_v1_modified": False,
        "provider_calls": 0,
        "runs": runs,
    }
    text = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(text, encoding="utf-8")
    print(text[:700])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
