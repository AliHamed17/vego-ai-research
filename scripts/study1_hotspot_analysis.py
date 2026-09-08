"""Tables A-D for the human-review hotspot baseline, fail-closed on missing human labels.

Tables B and C are defined against independent human judgement. When that judgement does not
exist this module emits `NOT_AVAILABLE` with the reason and the exact missing input. It does not
substitute a model label, a proxy signal, a heuristic, or the author's own opinion, and there is
no flag that makes it do so. That refusal is the point: a study whose primary outcome silently
became something else would be worse than one that reports the gap.

Table A and Table D need no labels and are computed from the persisted event logs and receipts.

The prioritized set is `STRONG_ALERT`, fixed in the manifest before any result, because
Detector-v1's alert rate including `WEAK_ALERT` has been 1.0 on every episode observed, which
makes an alert-versus-no-alert split degenerate. The preregistered sensitivity analysis recomputes
the same quantities with the prioritized set defined as `STRONG_ALERT` or `WEAK_ALERT`.

Detector-v1 is imported and applied, never modified. No provider is contacted.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from airtravel_detector_analysis import project_episodes  # noqa: E402
from extract_qa_escalation_features import detect_detector_v1  # noqa: E402

NOT_AVAILABLE = "NOT_AVAILABLE"
ALERT_CLASSES = {"STRONG_ALERT", "WEAK_ALERT"}
PRIORITIZED_DEFAULT = {"STRONG_ALERT"}
PRIORITIZED_SENSITIVITY = {"STRONG_ALERT", "WEAK_ALERT"}
WORTHY, NOT_WORTHY, INSUFFICIENT, DISAGREEMENT = (
    "HUMAN_REVIEW_WORTHY",
    "NOT_WORTHY",
    "INSUFFICIENT",
    "DISAGREEMENT",
)


def load_events(output_dir: Path) -> list[dict[str, Any]]:
    return [
        json.loads(line)
        for line in (output_dir / "qa_events.jsonl").read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def episode_rows(run_label: str, output_dir: Path) -> list[dict[str, Any]]:
    events = load_events(output_dir)
    episode_case: dict[str, Any] = {}
    for event in events:
        episode_case.setdefault(event["episode_id"], event.get("case_id"))
    rows = []
    for episode in project_episodes(events):
        verdict = detect_detector_v1(episode)
        rows.append(
            {
                "run_label": run_label,
                "episode_id": episode["episode_id"],
                "case_id": episode_case.get(episode["episode_id"]) or "RUN_GLOBAL",
                "classification": verdict["classification"],
                "signals": verdict["all_signals_fired"],
                "answers": len(episode.get("answers", [])),
                "round_count": episode.get("round_count"),
                "termination_reason": episode.get("termination_reason"),
                "complete": bool(episode.get("scientific_complete")),
            }
        )
    return rows


def table_a(runs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out = []
    for run in runs:
        rows = run["episodes"]
        receipt = run.get("receipt") or {}
        usage = receipt.get("usage", {})
        out.append(
            {
                "run_label": run["label"],
                "evidence_class": run["evidence_class"],
                "status": receipt.get("status", NOT_AVAILABLE),
                "selected_cases": receipt.get("N", NOT_AVAILABLE),
                "completed_cases": run.get("completed_cases", NOT_AVAILABLE),
                "complete_episodes": sum(1 for row in rows if row["complete"]),
                "incomplete_technical_episodes": sum(1 for row in rows if not row["complete"]),
                "termination_states": dict(
                    Counter(row["termination_reason"] for row in rows)
                ),
                "calls": usage.get("outbound_requests", NOT_AVAILABLE),
                "call_cap": usage.get("outbound_request_cap", NOT_AVAILABLE),
                "cost_usd": usage.get("actual_cost_usd", NOT_AVAILABLE),
                "started_at": receipt.get("started_at", NOT_AVAILABLE),
                "completed_at": receipt.get("completed_at", NOT_AVAILABLE),
                "truncated_calls": (receipt.get("call_ledger") or {}).get(
                    "truncated_calls", NOT_AVAILABLE
                ),
            }
        )
    return out


def adjudicate(rater_a: dict[str, Any], rater_b: dict[str, Any]) -> dict[str, str]:
    """The frozen rule. A disagreement stays a disagreement until a third adjudicator resolves it."""
    verdicts = {}
    for card_id, first in rater_a.items():
        second = rater_b.get(card_id)
        if second is None:
            verdicts[card_id] = NOT_AVAILABLE
        elif first == second == "Yes":
            verdicts[card_id] = WORTHY
        elif first == second == "No":
            verdicts[card_id] = NOT_WORTHY
        elif first == second == "Insufficient information":
            verdicts[card_id] = INSUFFICIENT
        else:
            verdicts[card_id] = DISAGREEMENT
    return verdicts


def unavailable(reason: str, missing: list[str]) -> dict[str, Any]:
    return {
        "status": NOT_AVAILABLE,
        "reason": reason,
        "missing_inputs": missing,
        "substitution_permitted": False,
        "note": (
            "no model label, proxy signal, heuristic or author judgement may stand in for the "
            "independent human ratings this table is defined against"
        ),
    }


def table_b(rows: list[dict[str, Any]], verdicts: dict[str, str] | None,
            key: dict[str, str] | None) -> dict[str, Any]:
    complete = [row for row in rows if row["complete"]]
    alert_rate = (
        round(sum(1 for row in complete if row["classification"] in ALERT_CLASSES) / len(complete), 4)
        if complete
        else None
    )
    base = {
        "denominator_complete_episodes": len(complete),
        "alert_rate": alert_rate,
        "class_counts": dict(Counter(row["classification"] for row in complete)),
    }
    if not verdicts or not key:
        base.update(
            unavailable(
                "two independent blinded rater response sets are required and are absent",
                ["rater A responses", "rater B responses"],
            )
        )
        base["human_review_worthy_rate"] = NOT_AVAILABLE
        base["confusion_matrix"] = NOT_AVAILABLE
        base["precision"] = NOT_AVAILABLE
        base["recall"] = NOT_AVAILABLE
        return base

    by_episode = {key[card]: verdict for card, verdict in verdicts.items() if card in key}
    matrix: Counter[tuple[str, str]] = Counter()
    for row in complete:
        verdict = by_episode.get(row["episode_id"])
        if verdict is None:
            continue
        prioritized = "prioritized" if row["classification"] in PRIORITIZED_DEFAULT else "not_prioritized"
        matrix[(prioritized, verdict)] += 1
    worthy = sum(count for (_, verdict), count in matrix.items() if verdict == WORTHY)
    rated = sum(matrix.values())
    hits = matrix[("prioritized", WORTHY)]
    flagged = sum(count for (side, _), count in matrix.items() if side == "prioritized")
    base.update(
        {
            "rated_episodes": rated,
            "human_review_worthy_rate": round(worthy / rated, 4) if rated else None,
            "confusion_matrix": {f"{side}|{verdict}": count for (side, verdict), count in sorted(matrix.items())},
            "precision": round(hits / flagged, 4) if flagged else None,
            "recall": round(hits / worthy, 4) if worthy else None,
            "metric_status": "EXPLORATORY",
            "metric_caveat": (
                "precision and recall are exploratory at this sample size, are computed only over "
                "adjudicated cards, and exclude DISAGREEMENT and INSUFFICIENT from both numerator "
                "and denominator"
            ),
        }
    )
    return base


def table_c(rows: list[dict[str, Any]], verdicts: dict[str, str] | None,
            key: dict[str, str] | None, receipts: list[dict[str, Any]],
            minutes: dict[str, float] | None) -> dict[str, Any]:
    complete = [row for row in rows if row["complete"]]
    prioritized = [row for row in complete if row["classification"] in PRIORITIZED_DEFAULT]
    cost = sum(
        (receipt.get("usage", {}).get("actual_cost_usd") or 0) for receipt in receipts
    )
    cases = sum((receipt.get("N") or 0) for receipt in receipts)
    result: dict[str, Any] = {
        "all_episodes_review_workload": len(complete),
        "detector_prioritized_review_workload": len(prioritized),
        "prioritized_set_definition": "STRONG_ALERT, fixed in the manifest before results",
        "workload_reduction_fraction": (
            round(1 - len(prioritized) / len(complete), 4) if complete else None
        ),
        "provider_cost_usd": round(cost, 6),
        "cost_per_completed_case_usd": round(cost / cases, 6) if cases else NOT_AVAILABLE,
    }
    if not verdicts or not key:
        result["proportion_of_human_worthy_retained"] = NOT_AVAILABLE
        result["cost_per_human_confirmed_review_worthy_episode_usd"] = NOT_AVAILABLE
        result["review_minutes_saved"] = NOT_AVAILABLE
        result["unavailable"] = unavailable(
            "retention, cost per confirmed episode and minutes saved are defined against human "
            "ratings that do not exist",
            ["rater A responses", "rater B responses"],
        )
        return result

    by_episode = {key[card]: verdict for card, verdict in verdicts.items() if card in key}
    worthy = [row for row in complete if by_episode.get(row["episode_id"]) == WORTHY]
    retained = [row for row in worthy if row["classification"] in PRIORITIZED_DEFAULT]
    result["proportion_of_human_worthy_retained"] = (
        round(len(retained) / len(worthy), 4) if worthy else None
    )
    result["cost_per_human_confirmed_review_worthy_episode_usd"] = (
        round(cost / len(worthy), 6) if worthy else NOT_AVAILABLE
    )
    if minutes:
        saved = sum(minutes.get(card, 0.0) for card in verdicts) - sum(
            minutes.get(card, 0.0)
            for card, verdict in verdicts.items()
            if key.get(card) in {row["episode_id"] for row in prioritized}
        )
        result["review_minutes_saved"] = round(saved, 2)
        result["review_minutes_basis"] = "measured per-card times supplied by raters"
    else:
        result["review_minutes_saved"] = NOT_AVAILABLE
        result["review_minutes_basis"] = (
            "raters did not record per-card time; minutes saved may not be estimated"
        )
    return result


def table_d(runs: list[dict[str, Any]]) -> dict[str, Any]:
    per_run, per_case = [], []
    for run in runs:
        rows = run["episodes"]
        complete = [row for row in rows if row["complete"]]
        per_run.append(
            {
                "run_label": run["label"],
                "evidence_class": run["evidence_class"],
                "complete_episodes": len(complete),
                "class_counts": dict(Counter(row["classification"] for row in complete)),
                "termination_states": dict(Counter(row["termination_reason"] for row in rows)),
                "routes": run.get("routes", {}),
                "mean_answers_per_complete_episode": (
                    round(sum(row["answers"] for row in complete) / len(complete), 2)
                    if complete
                    else None
                ),
            }
        )
        grouped: dict[str, list[dict[str, Any]]] = {}
        for row in complete:
            grouped.setdefault(row["case_id"], []).append(row)
        for case_id, group in sorted(grouped.items()):
            per_case.append(
                {
                    "run_label": run["label"],
                    "case_id": case_id,
                    "complete_episodes": len(group),
                    "class_counts": dict(Counter(row["classification"] for row in group)),
                    "answers": sum(row["answers"] for row in group),
                }
            )
    return {"per_run": per_run, "per_case": per_case}


def sensitivity(rows: list[dict[str, Any]]) -> dict[str, Any]:
    complete = [row for row in rows if row["complete"]]
    wide = [row for row in complete if row["classification"] in PRIORITIZED_SENSITIVITY]
    return {
        "preregistered": True,
        "prioritized_set_definition": "STRONG_ALERT or WEAK_ALERT",
        "detector_prioritized_review_workload": len(wide),
        "workload_reduction_fraction": (
            round(1 - len(wide) / len(complete), 4) if complete else None
        ),
        "note": "the only sensitivity analysis permitted by the manifest",
    }


VALID_R1 = {"Yes", "No", "Insufficient information"}


def read_responses(path: Path | None) -> tuple[dict[str, str], dict[str, float]] | tuple[None, None]:
    if path is None or not path.is_file():
        return None, None
    payload = json.loads(path.read_text(encoding="utf-8"))
    answers, minutes = {}, {}
    for row in payload.get("responses", []):
        value = row.get("R1_WORTHY")
        if value in VALID_R1:
            answers[row["card_id"]] = value
        if row.get("R4_MINUTES") is not None:
            minutes[row["card_id"]] = float(row["R4_MINUTES"])
    return (answers or None), (minutes or None)


def rater_sets_complete(expected: set[str], rater_a: dict[str, str] | None,
                        rater_b: dict[str, str] | None) -> dict[str, Any]:
    """A partial rating set may not produce a rate, because its denominator would be self-selected.

    Allowing adjudication over whichever cards happened to come back would let the sample be
    chosen by the raters' completion order. Every expected card must be answered by both raters
    before any adjudication, table, rate or primary outcome is computed.
    """
    if not rater_a or not rater_b:
        return {
            "complete": False,
            "reason": "one or both rater response sets are absent",
            "missing_from_rater_a": sorted(expected) if not rater_a else [],
            "missing_from_rater_b": sorted(expected) if not rater_b else [],
        }
    missing_a = sorted(expected - set(rater_a))
    missing_b = sorted(expected - set(rater_b))
    invalid_a = sorted(card for card, value in rater_a.items() if value not in VALID_R1)
    invalid_b = sorted(card for card, value in rater_b.items() if value not in VALID_R1)
    complete = not (missing_a or missing_b or invalid_a or invalid_b)
    return {
        "complete": complete,
        "expected_cards": len(expected),
        "missing_from_rater_a": missing_a,
        "missing_from_rater_b": missing_b,
        "invalid_in_rater_a": invalid_a,
        "invalid_in_rater_b": invalid_b,
        "reason": None if complete else "paired rater coverage is incomplete",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", action="append", required=True,
                        metavar="LABEL=OUTPUT_DIR:EVIDENCE_CLASS")
    parser.add_argument("--card-key", type=Path, default=None)
    parser.add_argument("--rater-a", type=Path, default=None)
    parser.add_argument("--rater-b", type=Path, default=None)
    parser.add_argument("--out", type=Path, default=None)
    args = parser.parse_args()

    runs, receipts, all_rows = [], [], []
    for spec in args.run:
        label, _, rest = spec.partition("=")
        path, _, evidence_class = rest.partition(":")
        directory = Path(path)
        rows = episode_rows(label, directory)
        receipt_path = directory / "run-receipt.json"
        receipt = json.loads(receipt_path.read_text(encoding="utf-8")) if receipt_path.is_file() else {}
        state_path = directory / "pipeline_state.json"
        completed_cases = NOT_AVAILABLE
        if state_path.is_file():
            state = json.loads(state_path.read_text(encoding="utf-8"))
            completed_cases = len(state.get("compliance_vectors", {}) or {})
        events = load_events(directory)
        routes = {
            f"{event['source_agent']} asks {event['target_agent']}": count
            for (event, count) in [
                (e, c)
                for e, c in Counter(
                    (q["source_agent"], q["target_agent"])
                    for q in events
                    if q["event_type"] == "QUESTION_EMITTED"
                ).items()
                for e in [{"source_agent": e[0], "target_agent": e[1]}]
            ]
        }
        runs.append(
            {
                "label": label,
                "evidence_class": evidence_class or NOT_AVAILABLE,
                "episodes": rows,
                "receipt": receipt,
                "completed_cases": completed_cases,
                "routes": routes,
            }
        )
        receipts.append(receipt)
        all_rows.extend(rows)

    rater_a, minutes_a = read_responses(args.rater_a)
    rater_b, minutes_b = read_responses(args.rater_b)
    key = None
    expected: set[str] = set()
    if args.card_key and args.card_key.is_file():
        payload = json.loads(args.card_key.read_text(encoding="utf-8"))
        key = {row["card_id"]: row["episode_id"] for row in payload.get("key", [])}
        expected = set(key)
    coverage = rater_sets_complete(expected, rater_a, rater_b)
    verdicts = adjudicate(rater_a, rater_b) if coverage["complete"] else None
    minutes = {**(minutes_a or {}), **(minutes_b or {})} or None

    report = {
        "schema_version": "study1-hotspot-analysis-v1",
        "study_id": "STUDY1-HOTSPOT",
        "detector_v1_modified": False,
        "detector_v1_scope": (
            "episode-level and reporting-only; it does not create a human queue and is not "
            "Agent-4's queue mechanism"
        ),
        "pooling": "PROHIBITED - every table is computed per run on its own denominator",
        "table_a_pipeline_reliability": table_a(runs),
        "table_b_detector_to_human_agreement": [
            {"run_label": run["label"], "evidence_class": run["evidence_class"],
             **table_b(run["episodes"], verdicts, key)}
            for run in runs
        ],
        "table_c_operational_baseline": [
            {"run_label": run["label"], "evidence_class": run["evidence_class"],
             **table_c(run["episodes"], verdicts, key, [run["receipt"]], minutes)}
            for run in runs
        ],
        "table_d_robustness": table_d(runs),
        "preregistered_sensitivity": [
            {"run_label": run["label"], **sensitivity(run["episodes"])} for run in runs
        ],
        "paired_rater_coverage": coverage,
        "adjudication": (
            {"verdict_counts": dict(Counter(verdicts.values()))} if verdicts
            else unavailable(coverage["reason"] or "no rater responses supplied", ["complete paired rater coverage for every expected card"])
        ),
    }
    text = json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(text, encoding="utf-8")
    print(text[:1400])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
