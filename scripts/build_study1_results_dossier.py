"""Comprehensive descriptive analytics dossier for the accepted Study 1 run.

Recomputes every figure from the persisted event log and pipeline outputs, adds analytics not
previously published, and renders one supervisor-facing results document.

Nothing here contacts a provider, changes Detector-v1 or its thresholds, or alters any evidence
file. It reads the accepted run and writes only its own dossier artifacts.

The analytics added here are descriptive. The counterfactual section reports which episodes would
change class if a single signal were absent; it is a robustness description of the frozen rule on
frozen evidence, NOT a threshold change and NOT a new detector.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import statistics
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
COMPLETE_STATES = {"CONVERGED", "TERMINATED_MAX_ROUNDS"}
STRONG_SIGNALS = ("S1", "S3", "S7")
WEAK_SIGNALS = ("S2", "S6")


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_events(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def project(events: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Rebuild episodes from the event stream, independent of any derived file."""
    questions = {e["question_id"]: e for e in events if e["event_type"] == "QUESTION_EMITTED"}
    terminations = {
        e["episode_id"]: e.get("termination_reason")
        for e in events if e["event_type"] == "EPISODE_TERMINATED"
    }
    episodes: dict[str, dict[str, Any]] = defaultdict(
        lambda: {"questions": 0, "max_round": 0, "answers": [], "case_id": None, "routes": Counter()}
    )
    for e in events:
        if e["event_type"] != "QUESTION_EMITTED":
            continue
        ep = episodes[e["episode_id"]]
        ep["questions"] += 1
        ep["max_round"] = max(ep["max_round"], int(e.get("round_index") or 0))
        ep["case_id"] = e.get("case_id")
        ep["routes"][(e["source_agent"], e["target_agent"])] += 1
    for e in events:
        if e["event_type"] != "ANSWER_RECEIVED":
            continue
        q = questions.get(e["question_id"])
        if q is not None:
            episodes[q["episode_id"]]["answers"].append(e)

    rows = []
    for episode_id, data in episodes.items():
        reason = terminations.get(episode_id)
        conf = Counter(a.get("answer_confidence") for a in data["answers"])
        empty_evidence = sum(
            1 for a in data["answers"]
            if (a.get("answer_evidence_ref") or {}).get("length", 0) == 0
        )
        fired = {
            "S1": conf.get("Low", 0) > 0,
            "S3": empty_evidence > 0,
            "S7": reason == "TERMINATED_MAX_ROUNDS",
            "S2": conf.get("Medium", 0) > 0,
            "S6": data["max_round"] > 1,
        }
        complete = reason in COMPLETE_STATES
        strong = [s for s in STRONG_SIGNALS if fired[s]]
        weak = [s for s in WEAK_SIGNALS if fired[s]]
        rows.append({
            "episode_id": episode_id,
            "case_id": data["case_id"],
            "termination_reason": reason,
            "scientific_complete": complete,
            "questions": data["questions"],
            "answers": len(data["answers"]),
            "max_round": data["max_round"],
            "routes": {f"{s}|{t}": n for (s, t), n in sorted(data["routes"].items())},
            "confidence": dict(conf),
            "empty_evidence_answers": empty_evidence,
            "signals_fired": fired,
            "strong": strong,
            "weak": weak,
            "classification": (
                "EXCLUDED" if not complete
                else "STRONG_ALERT" if strong
                else "WEAK_ALERT" if weak
                else "NO_ALERT"
            ),
        })
    return rows


def counterfactual(rows: list[dict[str, Any]]) -> dict[str, Any]:
    """Which episodes change class if one signal were absent? Descriptive robustness only."""
    scored = [r for r in rows if r["classification"] != "EXCLUDED"]
    out: dict[str, Any] = {}
    for removed in STRONG_SIGNALS + WEAK_SIGNALS:
        classes = Counter()
        changed = []
        for r in scored:
            strong = [s for s in r["strong"] if s != removed]
            weak = [s for s in r["weak"] if s != removed]
            new = "STRONG_ALERT" if strong else "WEAK_ALERT" if weak else "NO_ALERT"
            classes[new] += 1
            if new != r["classification"]:
                changed.append({"episode_id": r["episode_id"],
                                "from": r["classification"], "to": new})
        out[removed] = {"resulting_distribution": dict(classes),
                        "episodes_changed": len(changed), "changes": changed}
    return {
        "method": ("each signal is removed in turn from the frozen rule and the class recomputed "
                   "over the same episodes; the rule itself and its thresholds are unchanged"),
        "denominator": len(scored),
        "per_removed_signal": out,
    }


def cooccurrence(rows: list[dict[str, Any]]) -> dict[str, Any]:
    """How often do signals fire together on the same episode?"""
    scored = [r for r in rows if r["classification"] != "EXCLUDED"]
    names = list(STRONG_SIGNALS + WEAK_SIGNALS)
    matrix = {a: {b: 0 for b in names} for a in names}
    for r in scored:
        on = [s for s in names if r["signals_fired"][s]]
        for a in on:
            for b in on:
                matrix[a][b] += 1
    return {"denominator": len(scored), "matrix": matrix,
            "note": "diagonal is the count of episodes in which that signal fired"}


def confidence_trajectory(events: list[dict[str, Any]]) -> dict[str, Any]:
    """Is low confidence concentrated early or late in a conversation?"""
    questions = {e["question_id"]: e for e in events if e["event_type"] == "QUESTION_EMITTED"}
    per_round: dict[int, Counter] = defaultdict(Counter)
    for e in events:
        if e["event_type"] != "ANSWER_RECEIVED":
            continue
        q = questions.get(e["question_id"])
        if q is None:
            continue
        per_round[int(q.get("round_index") or 0)][e.get("answer_confidence")] += 1
    rows = []
    for rnd in sorted(per_round):
        c = per_round[rnd]
        total = sum(c.values())
        rows.append({
            "round_index": rnd, "answers": total,
            "low": c.get("Low", 0), "medium": c.get("Medium", 0), "high": c.get("High", 0),
            "low_share": round(c.get("Low", 0) / total, 4) if total else None,
        })
    first, last = rows[0] if rows else {}, rows[-1] if rows else {}
    return {
        "per_round": rows,
        "first_round_low_share": first.get("low_share"),
        "final_round_low_share": last.get("low_share"),
        "note": ("a descriptive trajectory over rounds; it does not establish that later rounds "
                 "resolve or fail to resolve uncertainty"),
    }


def evidence_by_confidence(events: list[dict[str, Any]]) -> dict[str, Any]:
    """Evidence-field length grouped by the model's own confidence label."""
    buckets: dict[str, list[int]] = defaultdict(list)
    for e in events:
        if e["event_type"] != "ANSWER_RECEIVED":
            continue
        length = (e.get("answer_evidence_ref") or {}).get("length")
        if length is not None:
            buckets[e.get("answer_confidence") or "UNKNOWN"].append(int(length))
    out = {}
    for label, values in sorted(buckets.items()):
        values.sort()
        out[label] = {
            "n": len(values), "min": values[0], "max": values[-1],
            "median": int(statistics.median(values)),
            "zero_length": sum(1 for v in values if v == 0),
        }
    return {"by_confidence": out,
            "note": ("evidence length measures presence and size of the field only; it is not a "
                     "measure of evidence quality, correctness or relevance")}


def route_concentration(rows: list[dict[str, Any]]) -> dict[str, Any]:
    totals = Counter()
    for r in rows:
        for route, n in r["routes"].items():
            totals[route] += n
    total = sum(totals.values())
    ranked = [{"asking_agent": k.split("|")[0], "answering_agent": k.split("|")[1],
               "questions": n, "share": round(n / total, 4) if total else None}
              for k, n in totals.most_common()]
    return {
        "total_questions": total,
        "observed_route_pairs": len(totals),
        "possible_route_pairs": 6,
        "routes": ranked,
        "largest_route_share": ranked[0]["share"] if ranked else None,
        "note": ("route volume is descriptive routing metadata; no detector signal reads it and it "
                 "says nothing about whether a route was appropriate"),
    }


def separation_baseline(envelope: dict[str, Any]) -> dict[str, Any]:
    """The engineering baseline: does the frozen rule discriminate at all?"""
    modes = envelope.get("modes") or []
    rows = []
    for m in modes:
        d = m.get("detector_v1", {})
        rows.append({
            "fixture_mode": m.get("fixture_mode"),
            "episodes": m.get("episodes_observed"),
            "denominator": m.get("detector_denominator"),
            "STRONG_ALERT": d.get("STRONG_ALERT"),
            "WEAK_ALERT": d.get("WEAK_ALERT"),
            "NO_ALERT": d.get("NO_ALERT"),
            "run_level_status": m.get("run_level_status"),
        })
    classes_seen = {k for r in rows for k in ("STRONG_ALERT", "NO_ALERT") if (r.get(k) or 0) > 0}
    return {
        "evidence_class": "ENGINEERING_FIXTURE_NOT_SCIENTIFIC",
        "provider_calls": envelope.get("provider_calls", 0),
        "modes": rows,
        "distinct_classes_produced": sorted(classes_seen),
        "rule_discriminates": len(classes_seen) > 1,
        "interpretation": (
            "Deterministic fixtures drive the frozen rule to opposite classes, so the rule is not "
            "degenerate. This is an instrumentation check on synthetic input, NOT a scientific "
            "result, NOT provider performance, and NOT a VEGO_AI_ON/OFF comparison. Its "
            "denominators are separate from the accepted run's and must never be merged with them."
        ),
    }


def build(run_root: Path) -> dict[str, Any]:
    output, analysis = run_root / "output", run_root / "analysis"
    events_path = output / "qa_events.jsonl"
    events = load_events(events_path)
    receipt = json.loads((output / "run-receipt.json").read_text(encoding="utf-8"))
    rows = project(events)

    def maybe(name: str) -> dict[str, Any]:
        path = analysis / name
        return json.loads(path.read_text(encoding="utf-8")) if path.is_file() else {}

    envelope = maybe("detector-envelope.json")
    scored = [r for r in rows if r["classification"] != "EXCLUDED"]
    usage = receipt.get("usage") or {}

    return {
        "schema_version": "study1-results-dossier-v1",
        "evidence_class": "DESCRIPTIVE_COUNTS_FROM_ONE_ACCEPTED_RUN",
        "verdict": "DESCRIPTIVE_REPORTING_WITH_RETROSPECTIVE_PROVENANCE",
        "generated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "provider_calls_made_by_this_script": 0,
        "evidence": {
            "run_id": receipt.get("run_id"),
            "setting_id": receipt.get("setting_id"),
            "corpus_id": receipt.get("corpus_id"),
            "model": receipt.get("model_requested"),
            "event_log_sha256": digest(events_path),
            "run_receipt_sha256": digest(output / "run-receipt.json"),
            "event_count": len(events),
        },
        "headline": {
            "episodes_observed": len(rows),
            "complete_episodes_denominator": len(scored),
            "excluded": len(rows) - len(scored),
            "questions": sum(r["questions"] for r in rows),
            "answers": sum(r["answers"] for r in rows),
            "max_round_index": max((r["max_round"] for r in rows), default=0),
            "classification": dict(Counter(r["classification"] for r in scored)),
            "signals_fired": {
                s: sum(1 for r in scored if r["signals_fired"][s])
                for s in STRONG_SIGNALS + WEAK_SIGNALS
            },
        },
        "episode_table": rows,
        "signal_cooccurrence": cooccurrence(rows),
        "counterfactual_class_stability": counterfactual(rows),
        "confidence_trajectory": confidence_trajectory(events),
        "evidence_length_by_confidence": evidence_by_confidence(events),
        "route_concentration": route_concentration(rows),
        "separation_baseline": separation_baseline(envelope),
        "cost": {
            "outbound_requests": usage.get("outbound_requests"),
            "prompt_tokens": usage.get("prompt_tokens"),
            "completion_tokens": usage.get("completion_tokens"),
            "total_tokens": usage.get("total_tokens"),
            "actual_cost_usd": usage.get("actual_cost_usd"),
            "per_episode_attribution": "NOT_AVAILABLE",
            "per_episode_note": ("the run persisted no per-call ledger, so cost and tokens cannot "
                                 "be attributed to an individual episode; this is NOT_AVAILABLE "
                                 "and must not be reported as zero or estimated by division"),
        },
        "forbidden_metrics_computed": [],
        "claim_boundary": {
            "permitted": ("descriptive counts from one accepted provider-backed run on this corpus, "
                          "under this configuration"),
            "forbidden": ("alert correctness; accuracy, precision, recall, F1; effectiveness; human "
                          "benefit; causality; representativeness; generalization; any comparison "
                          "of the fixture baseline with the accepted run as if it were a result"),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-root", type=Path,
                        default=ROOT / "external_data/airtravel-pr38/v4-real-run")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    dossier = build(args.run_root)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(dossier, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
                           encoding="utf-8")
    h = dossier["headline"]
    print(f"dossier written: {args.output}")
    print(f"  episodes {h['episodes_observed']} denominator {h['complete_episodes_denominator']} "
          f"classes {h['classification']}")
    print(f"  signals {h['signals_fired']}")
    print(f"  rule discriminates on fixtures: {dossier['separation_baseline']['rule_discriminates']} "
          f"{dossier['separation_baseline']['distinct_classes_produced']}")
    print(f"  provider calls made by this script: {dossier['provider_calls_made_by_this_script']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
