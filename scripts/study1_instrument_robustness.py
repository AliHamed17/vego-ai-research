"""Instrument-robustness experiments on the accepted Study 1 event log.

These experiments ask whether the reported classification depends on anything other than the
frozen rule applied to the recorded answers. They read the accepted log only, contact no
provider, generate no new episodes, and leave Detector-v1 untouched.

  1. Event-order invariance. The log is permuted many times and reprojected; the per-episode
     classification must not move. The projection uses set/max/any aggregations, so invariance
     is expected, but the one order-sensitive path (a second EPISODE_TERMINATED for the same
     episode) is checked structurally rather than assumed away.
  2. Leave-one-episode-out. The class distribution after dropping each episode in turn.
  3. Denominator sensitivity. What the headline would be under a stricter completeness rule
     that also excluded TERMINATED_MAX_ROUNDS.
  4. Aggregation sensitivity (descriptive only). Detector-v1 reads confidence with `any` over
     the episode's answers. This reports the confidence summary of the same answers under other
     descriptive summaries (true majority, ordinal median, first round, final round, plurality)
     AND the class each summary would yield when the frozen rule is re-applied with the S1/S2
     contribution replaced and S3, S6, S7 kept as recorded. A label-level difference does not
     imply a class-level difference: an episode that reached the round cap stays STRONG_ALERT
     through S7 whatever its confidence summary. These are NOT alternative detectors.
  5. Value-domain audit. Confidence labels actually present, and whether any answer carried
     the recorder's UNKNOWN fallback.

Evidence class: DESCRIPTIVE_INSTRUMENT_ROBUSTNESS_ON_ONE_ACCEPTED_RUN.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import random
import sys
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from airtravel_detector_analysis import project_episodes  # noqa: E402
from extract_qa_escalation_features import detect_detector_v1  # noqa: E402

PERMUTATIONS = 500
LABELS = ("Low", "Medium", "High")


def load_events(path: Path) -> list[dict[str, Any]]:
    return [json.loads(l) for l in path.read_text(encoding="utf-8").splitlines() if l.strip()]


def classify(events: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    out = {}
    for ep in project_episodes(events):
        v = detect_detector_v1(ep)
        out[ep["episode_id"]] = {"classification": v["classification"],
                                 "signals": sorted(v["all_signals_fired"])}
    return out


def order_invariance(events: list[dict[str, Any]], canonical) -> dict[str, Any]:
    variants = {"reversed": list(reversed(events)),
                "sorted_by_event_type": sorted(events, key=lambda e: e["event_type"]),
                "sorted_by_episode_then_type": sorted(events, key=lambda e: (e["episode_id"], e["event_type"]))}
    named = {k: classify(v) == canonical for k, v in variants.items()}
    invariant = 0
    for seed in range(PERMUTATIONS):
        shuffled = list(events)
        random.Random(seed).shuffle(shuffled)
        invariant += classify(shuffled) == canonical
    terminations = Counter(e["episode_id"] for e in events if e["event_type"] == "EPISODE_TERMINATED")
    return {
        "seeded_permutations": PERMUTATIONS,
        "permutations_invariant": invariant,
        "named_reorderings_invariant": named,
        "episodes_with_multiple_termination_events": sum(1 for n in terminations.values() if n > 1),
        "invariant": invariant == PERMUTATIONS and all(named.values()),
        "why_expected": ("project_episodes aggregates with max(round_index), any(confidence), "
                         "any(evidence missing) and a set of routes; only a repeated "
                         "EPISODE_TERMINATED could make order matter, and none is present"),
    }


def leave_one_out(events: list[dict[str, Any]], canonical) -> list[dict[str, Any]]:
    scored = [eid for eid, v in canonical.items() if v["classification"] != "EXCLUDED"]
    rows = []
    for dropped in scored:
        rest = classify([e for e in events if e["episode_id"] != dropped])
        rest_scored = [v for v in rest.values() if v["classification"] != "EXCLUDED"]
        dist = Counter(v["classification"] for v in rest_scored)
        rows.append({"dropped_episode": dropped, "denominator": len(rest_scored),
                     "distribution": {k: dist.get(k, 0) for k in ("STRONG_ALERT", "WEAK_ALERT", "NO_ALERT")}})
    return rows


def denominator_sensitivity(events: list[dict[str, Any]]) -> dict[str, Any]:
    eps = project_episodes(events)
    frozen = [detect_detector_v1(e) for e in eps if e["scientific_complete"]]
    stricter = [detect_detector_v1(e) for e in eps
                if e["scientific_complete"] and e["termination_reason"] != "TERMINATED_MAX_ROUNDS"]

    def dist(vs):
        c = Counter(v["classification"] for v in vs)
        return {k: c.get(k, 0) for k in ("STRONG_ALERT", "WEAK_ALERT", "NO_ALERT")}

    return {
        "frozen_rule": {"denominator": len(frozen), "distribution": dist(frozen),
                        "complete_means": "CONVERGED or TERMINATED_MAX_ROUNDS"},
        "hypothetical_converged_only": {"denominator": len(stricter), "distribution": dist(stricter),
                                        "note": "NOT the preregistered rule; shown to expose dependence on the completeness definition"},
        "incomplete_technical_present": sum(1 for e in eps if not e["scientific_complete"]),
    }


CONFIDENCE_SIGNALS = ("S1_LOW_ANSWER_CONFIDENCE", "S2_MEDIUM_ANSWER_CONFIDENCE")
STRONG_OTHER = ("S3_MISSING_ANSWER_EVIDENCE", "S7_TERMINATED_MAX_ROUNDS")
WEAK_OTHER = ("S6_MULTIPLE_QA_ROUNDS",)
SUMMARIES = ("majority", "ordinal_median", "first_round_any", "final_round_any", "plurality")


def any_label(labels: list[str]) -> str:
    return "Low" if "Low" in labels else "Medium" if "Medium" in labels else "High"


def frozen_class(confidence_label: str | None, other_signals: list[str]) -> str:
    """Re-apply the frozen precedence with the confidence contribution replaced by one label.

    S3, S6 and S7 are taken verbatim from the recorded episode; only the S1/S2 contribution is
    derived from `confidence_label`. None (no majority) contributes neither S1 nor S2.
    """
    strong = [s for s in other_signals if s in STRONG_OTHER]
    weak = [s for s in other_signals if s in WEAK_OTHER]
    if confidence_label == "Low":
        strong.append("S1_LOW_ANSWER_CONFIDENCE")
    elif confidence_label == "Medium":
        weak.append("S2_MEDIUM_ANSWER_CONFIDENCE")
    return "STRONG_ALERT" if strong else "WEAK_ALERT" if weak else "NO_ALERT"


def aggregation_sensitivity(events: list[dict[str, Any]]) -> dict[str, Any]:
    round_of = {e["question_id"]: e.get("round_index") or 0
                for e in events if e["event_type"] == "QUESTION_EMITTED"}
    rows = []
    for ep in project_episodes(events):
        if not ep["scientific_complete"]:
            continue
        answers = [(round_of.get(a["question_id"], 0), a["answer_confidence"]) for a in ep["answers"]]
        if not answers:
            continue
        verdict = detect_detector_v1(ep)
        other = [s for s in verdict["all_signals_fired"] if s not in CONFIDENCE_SIGNALS]
        labels = [c for _, c in answers]
        n = len(labels)
        first_r, last_r = min(r for r, _ in answers), max(r for r, _ in answers)
        counts = Counter(labels)
        summaries = {
            "any": any_label(labels),
            "majority": next((k for k in LABELS if counts[k] * 2 > n), "NO_MAJORITY"),
            "ordinal_median": ("Low" if counts["Low"] * 2 > n
                               else "Medium" if (counts["Low"] + counts["Medium"]) * 2 > n else "High"),
            "first_round_any": any_label([c for r, c in answers if r == first_r]),
            "final_round_any": any_label([c for r, c in answers if r == last_r]),
            "plurality": counts.most_common(1)[0][0],
        }
        class_under = {k: frozen_class(None if v == "NO_MAJORITY" else v, other) for k, v in summaries.items()}
        if class_under["any"] != verdict["classification"]:
            raise RuntimeError(f"re-applied rule disagrees with Detector-v1 on {ep['episode_id']}")
        rows.append({
            "episode_id": ep["episode_id"],
            "answers": n,
            "rounds": ep["round_count"],
            "label_counts": {k: counts.get(k, 0) for k in LABELS},
            "recorded_other_signals": other,
            "frozen_class": verdict["classification"],
            "summaries": summaries,
            "class_under_summary": class_under,
            "class_depends_on_summary": any(c != verdict["classification"] for c in class_under.values()),
            "s1_depends_on_summary": summaries["any"] == "Low" and any(summaries[k] != "Low" for k in SUMMARIES),
        })
    return {
        "status": "DESCRIPTIVE_SENSITIVITY_NOT_A_DETECTOR",
        "frozen_aggregation": "any(answer_confidence == label) over the episode's answers",
        "class_recomputation": ("frozen precedence re-applied with the S1/S2 contribution replaced by the "
                                "summary label; S3, S6 and S7 kept exactly as recorded"),
        "episodes": rows,
        "class_agreement_with_frozen": {k: sum(1 for r in rows if r["class_under_summary"][k] == r["frozen_class"])
                                        for k in SUMMARIES},
        "label_agreement_with_frozen_any": {k: sum(1 for r in rows if r["summaries"][k] == r["summaries"]["any"])
                                            for k in SUMMARIES},
        "episodes_whose_class_depends_on_summary": [r["episode_id"] for r in rows if r["class_depends_on_summary"]],
        "episodes_whose_s1_depends_on_summary": [r["episode_id"] for r in rows if r["s1_depends_on_summary"]],
        "denominator": len(rows),
        "note": ("Detector-v1 is unchanged. Each summary is a descriptive view of the same recorded answers; "
                 "the class under each summary is obtained by re-applying the frozen rule, so an episode whose "
                 "S1 depends on `any` can still keep STRONG_ALERT through S3 or S7. None of these summaries is "
                 "proposed as a rule. 'majority' is a true majority (label with more than half the answers, else "
                 "NO_MAJORITY); 'ordinal_median' is the median on the ordered scale Low < Medium < High."),
    }


def value_domain(events: list[dict[str, Any]]) -> dict[str, Any]:
    answers = [e for e in events if e["event_type"] == "ANSWER_RECEIVED"]
    labels = Counter(a.get("answer_confidence") for a in answers)
    return {
        "answers": len(answers),
        "confidence_labels": dict(labels),
        "labels_outside_declared_domain": sorted(k for k in labels if k not in LABELS),
        "unknown_fallback_answers": labels.get("UNKNOWN", 0),
        "evidence_ref_null": sum(1 for a in answers if a.get("answer_evidence_ref") is None),
        "evidence_ref_zero_length": sum(1 for a in answers
                                        if (a.get("answer_evidence_ref") or {}).get("length", 0) == 0
                                        and a.get("answer_evidence_ref") is not None),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--events", type=Path,
                        default=ROOT / "external_data/airtravel-pr38/v4-real-run/output/qa_events.jsonl")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    events = load_events(args.events)
    canonical = classify(events)
    payload = {
        "schema_version": "study1-instrument-robustness-v1",
        "evidence_class": "DESCRIPTIVE_INSTRUMENT_ROBUSTNESS_ON_ONE_ACCEPTED_RUN",
        "provider_calls": 0,
        "detector_v1_modified": False,
        "event_log_sha256": hashlib.sha256(args.events.read_bytes()).hexdigest(),
        "event_count": len(events),
        "canonical": canonical,
        "event_order_invariance": order_invariance(events, canonical),
        "leave_one_episode_out": leave_one_out(events, canonical),
        "denominator_sensitivity": denominator_sensitivity(events),
        "aggregation_sensitivity": aggregation_sensitivity(events),
        "value_domain": value_domain(events),
        "claim_boundary": ("These are properties of the instrument applied to one accepted log. They "
                           "say nothing about alert correctness, model quality, or generalisation."),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    oi, ag = payload["event_order_invariance"], payload["aggregation_sensitivity"]
    print(f"order invariant: {oi['invariant']} ({oi['permutations_invariant']}/{oi['seeded_permutations']} "
          f"+ named {oi['named_reorderings_invariant']})")
    print(f"class agreement with frozen: {ag['class_agreement_with_frozen']} / {ag['denominator']}; "
          f"label agreement: {ag['label_agreement_with_frozen_any']}")
    print(f"class depends on summary: {ag['episodes_whose_class_depends_on_summary']}; "
          f"S1 depends on summary: {ag['episodes_whose_s1_depends_on_summary']}")
    for r in ag["episodes"]:
        print(f"  {r['episode_id']}: {r['frozen_class']} other={r['recorded_other_signals']} "
              f"labels={r['summaries']} classes={r['class_under_summary']} counts={r['label_counts']}")
    print(f"denominator sensitivity: {payload['denominator_sensitivity']}")
    print(f"value domain: {payload['value_domain']}")
    return 0 if oi["invariant"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
