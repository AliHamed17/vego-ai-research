"""Descriptive analysis of a full-frame run, and a side-by-side view that never pools runs.

Every quantity is recomputed from the persisted event log rather than copied from a receipt, so
the analysis is independent of what the run asserted about itself. Where a receipt value is also
available it is cross-checked and any disagreement is reported rather than silently resolved.

The cross-run section places runs beside each other in separate columns. It never sums, averages
or pools them, because they were produced under different case counts and therefore different
configurations. A reader who wants a combined number will not find one here, by design.

Detector-v1 is imported and applied, never modified. No provider is contacted.
"""

from __future__ import annotations

import argparse
import json
import statistics
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from airtravel_detector_analysis import project_episodes  # noqa: E402
from extract_qa_escalation_features import detect_detector_v1  # noqa: E402

ALERT_CLASSES = {"STRONG_ALERT", "WEAK_ALERT"}


def load_events(path: Path) -> list[dict[str, Any]]:
    return [
        json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()
    ]


def evidence_stats(events: list[dict[str, Any]]) -> dict[str, Any]:
    lengths = [
        (event.get("answer_evidence_ref") or {}).get("length", 0)
        for event in events
        if event["event_type"] == "ANSWER_RECEIVED"
    ]
    if not lengths:
        return {"n": 0}
    return {
        "n": len(lengths),
        "zero_length": sum(1 for length in lengths if length == 0),
        "min": min(lengths),
        "median": int(statistics.median(lengths)),
        "max": max(lengths),
    }


def route_table(events: list[dict[str, Any]]) -> list[dict[str, Any]]:
    counts = Counter(
        (event["source_agent"], event["target_agent"])
        for event in events
        if event["event_type"] == "QUESTION_EMITTED"
    )
    return [
        {"asking_agent": asking, "answering_agent": answering, "questions": count}
        for (asking, answering), count in sorted(counts.items(), key=lambda kv: -kv[1])
    ]


def per_case(events: list[dict[str, Any]], episodes: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Per-case counts. Episodes with no case are global to the run and reported separately."""
    verdicts = {ep["episode_id"]: detect_detector_v1(ep) for ep in episodes}
    episode_case: dict[str, Any] = {}
    for event in events:
        episode_case.setdefault(event["episode_id"], event.get("case_id"))
    grouped: dict[Any, dict[str, Any]] = defaultdict(
        lambda: {"episodes": 0, "questions": 0, "answers": 0, "confidence": Counter(), "classes": Counter()}
    )
    for episode in episodes:
        case = episode_case.get(episode["episode_id"])
        row = grouped[case]
        row["episodes"] += 1
        row["questions"] += episode.get("question_count", 0)
        row["answers"] += len(episode.get("answers", []))
        row["confidence"].update(
            answer.get("answer_confidence") for answer in episode.get("answers", [])
        )
        row["classes"][verdicts[episode["episode_id"]]["classification"]] += 1
    return [
        {
            "case_id": case if case is not None else "RUN_GLOBAL",
            "episodes": row["episodes"],
            "questions": row["questions"],
            "answers": row["answers"],
            "confidence": dict(row["confidence"]),
            "detector_classes": dict(row["classes"]),
        }
        for case, row in sorted(grouped.items(), key=lambda kv: (kv[0] is None, kv[0]))
    ]


def case_size_context(runtime_root: Path) -> dict[str, int]:
    contract_path = runtime_root / "full-frame-contract.json"
    if not contract_path.is_file():
        return {}
    contract = json.loads(contract_path.read_text(encoding="utf-8"))
    return {
        relative.split("/", 1)[1].split("_", 1)[0]: pin["bytes"]
        for relative, pin in contract["runtime_files"].items()
        if relative.startswith("candidate_models/")
    }


def analyse(label: str, events_path: Path, receipt_path: Path | None,
            runtime_root: Path | None) -> dict[str, Any]:
    events = load_events(events_path)
    episodes = project_episodes(events)
    complete = [ep for ep in episodes if ep.get("scientific_complete")]
    verdicts = [detect_detector_v1(ep) for ep in complete]
    labels = [verdict["classification"] for verdict in verdicts]
    signals = Counter(
        signal for verdict in verdicts for signal in verdict["all_signals_fired"]
    )
    questions = [event for event in events if event["event_type"] == "QUESTION_EMITTED"]
    answers = [event for event in events if event["event_type"] == "ANSWER_RECEIVED"]

    result: dict[str, Any] = {
        "run_label": label,
        "denominator_complete_episodes": len(complete),
        "denominator_note": "this run's own denominator; never pooled with another run",
        "episodes_total": len(episodes),
        "episodes_excluded": len(episodes) - len(complete),
        "terminations": dict(
            Counter(
                event.get("termination_reason")
                for event in events
                if event["event_type"] == "EPISODE_TERMINATED"
            )
        ),
        "questions": len(questions),
        "answers": len(answers),
        "max_round_index": max((event.get("round_index") or 0 for event in questions), default=0),
        "routes": route_table(events),
        "confidence_distribution": dict(
            Counter(event.get("answer_confidence") for event in answers)
        ),
        "evidence_length": evidence_stats(events),
        "detector_v1_class_counts": dict(Counter(labels)),
        "detector_v1_review_load": round(
            sum(1 for label in labels if label in ALERT_CLASSES) / len(labels), 4
        )
        if labels
        else None,
        "detector_v1_separates_episodes": len(set(labels)) > 1,
        "signal_fire_counts": dict(signals),
        "per_case": per_case(events, episodes),
    }

    if runtime_root:
        sizes = case_size_context(runtime_root)
        if sizes:
            result["case_input_bytes"] = sizes
            result["case_input_bytes_note"] = (
                "file size is an observable property of the input, not a quality or "
                "difficulty measure; no claim is made that larger files are worse models"
            )

    if receipt_path and receipt_path.is_file():
        receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
        usage = receipt.get("usage", {})
        ledger = receipt.get("call_ledger", {})
        result["run_receipt"] = {
            "status": receipt.get("status"),
            "run_id": receipt.get("run_id"),
            "N": receipt.get("N"),
            "outbound_requests": usage.get("outbound_requests"),
            "outbound_request_cap": usage.get("outbound_request_cap"),
            "total_tokens": usage.get("total_tokens"),
            "actual_cost_usd": usage.get("actual_cost_usd"),
            "truncated_calls": ledger.get("truncated_calls"),
            "max_completion_tokens_observed": ledger.get("max_completion_tokens_observed"),
            "outbound_requests_independently_recomputable": receipt.get(
                "outbound_requests_independently_recomputable"
            ),
            "blocked_egress_attempts": receipt.get("blocked_egress_attempts"),
        }
        result["receipt_cross_check"] = {
            "questions_match": receipt.get("lifecycle_summary", {}).get("questions")
            == len(questions),
            "answers_match": receipt.get("lifecycle_summary", {}).get("answers") == len(answers),
        }
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--run",
        action="append",
        required=True,
        metavar="LABEL=EVENTS[,RECEIPT]",
        help="repeatable; runs are reported side by side and never pooled",
    )
    parser.add_argument("--runtime-root", type=Path, default=None)
    parser.add_argument("--out", type=Path, default=None)
    args = parser.parse_args()

    runs = []
    for spec in args.run:
        label, _, paths = spec.partition("=")
        events, _, receipt = paths.partition(",")
        runs.append(
            analyse(
                label,
                Path(events),
                Path(receipt) if receipt else None,
                args.runtime_root,
            )
        )

    report = {
        "schema_version": "study1-full-frame-analysis-v1",
        "evidence_class": "ARCHIVAL_RETROSPECTIVE_DESCRIPTIVE_EVIDENCE",
        "pooling": "PROHIBITED - runs differ in case count and therefore in configuration",
        "recomputed_from": "persisted event logs, not from receipt assertions",
        "detector_v1_modified": False,
        "provider_calls": 0,
        "runs": runs,
    }
    text = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(text, encoding="utf-8")
    print(text[:600])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
