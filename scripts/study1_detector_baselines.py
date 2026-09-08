"""Baseline comparison suite for Detector-v1, computed offline from persisted event logs.

No ground-truth labels exist for this corpus. Nothing here therefore measures whether an alert
was *correct*, and no accuracy, precision, recall or F1 is computed or computable. What can be
measured without labels is what each rule *selects*, and how that selection relates to the
frozen rule's selection. That is what this module reports:

  * **selectivity** — how much of the episode set each rule flags;
  * **discrimination** — whether a rule assigns more than one class on the observed data at all;
  * **agreement with Detector-v1** — exact three-class match, binary match, Cohen's kappa and
    Jaccard over the flagged set;
  * **redundancy** — whether some single signal reproduces the composite rule exactly, which
    would mean the other signals contribute nothing on this data;
  * **marginal contribution** — how many episodes change class when each signal is removed;
  * **space coverage** — how much of the rule's reachable signal space the corpus actually visits.

A chance baseline is included because an agreement number is uninterpretable without one: a rule
that flags everything agrees perfectly with any rule that also flags everything.

Detector-v1 is imported and called, never reimplemented and never modified. Each run is scored
on its own denominator; runs are never pooled.
"""

from __future__ import annotations

import argparse
import itertools
import json
import random
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Callable

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from airtravel_detector_analysis import project_episodes  # noqa: E402
from extract_qa_escalation_features import detect_detector_v1  # noqa: E402
from study1_signal_contract import s6_fires  # noqa: E402

STRONG, WEAK, NONE, EXCLUDED = "STRONG_ALERT", "WEAK_ALERT", "NO_ALERT", "EXCLUDED"
ALERT_CLASSES = {STRONG, WEAK}
RANDOM_SEEDS = 2000

SIGNALS: dict[str, Callable[[dict[str, Any]], bool]] = {
    "S1_LOW_ANSWER_CONFIDENCE": lambda ep: any(
        a.get("answer_confidence") == "Low" for a in ep.get("answers", [])
    ),
    "S2_MEDIUM_ANSWER_CONFIDENCE": lambda ep: any(
        a.get("answer_confidence") == "Medium" for a in ep.get("answers", [])
    ),
    "S3_MISSING_ANSWER_EVIDENCE": lambda ep: any(
        (ref := a.get("answer_evidence_ref")) is None or ref.get("length", 0) == 0
        for a in ep.get("answers", [])
    ),
    "S6_MULTIPLE_QA_ROUNDS": s6_fires,
    "S7_TERMINATED_MAX_ROUNDS": lambda ep: ep.get("termination_reason") == "TERMINATED_MAX_ROUNDS",
}
STRONG_SIGNALS = ("S1_LOW_ANSWER_CONFIDENCE", "S3_MISSING_ANSWER_EVIDENCE", "S7_TERMINATED_MAX_ROUNDS")
WEAK_SIGNALS = ("S2_MEDIUM_ANSWER_CONFIDENCE", "S6_MULTIPLE_QA_ROUNDS")


def confidences(episode: dict[str, Any]) -> list[str]:
    return [a.get("answer_confidence") for a in episode.get("answers", [])]


def evidence_lengths(episode: dict[str, Any]) -> list[int]:
    """A missing evidence reference counts as length zero, matching the S3 predicate."""
    return [
        (answer.get("answer_evidence_ref") or {}).get("length", 0)
        for answer in episode.get("answers", [])
    ]


def classify_from_signals(fired: set[str]) -> str:
    if any(name in fired for name in STRONG_SIGNALS):
        return STRONG
    return WEAK if any(name in fired for name in WEAK_SIGNALS) else NONE


def baseline_catalog() -> dict[str, Callable[[dict[str, Any]], str]]:
    """Each baseline maps a complete episode to one of the three frozen classes."""
    catalog: dict[str, Callable[[dict[str, Any]], str]] = {
        "ALWAYS_ALERT": lambda ep: STRONG,
        "NEVER_ALERT": lambda ep: NONE,
        "ANY_NON_HIGH_CONFIDENCE": lambda ep: (
            STRONG if any(c != "High" for c in confidences(ep)) else NONE
        ),
        "MAJORITY_LOW_CONFIDENCE": lambda ep: (
            STRONG
            if confidences(ep) and sum(c == "Low" for c in confidences(ep)) * 2 > len(confidences(ep))
            else NONE
        ),
        "ANY_QUESTION_ASKED": lambda ep: STRONG if ep.get("question_count", 0) > 0 else NONE,
    }
    for name, predicate in SIGNALS.items():
        catalog[f"SINGLE_{name}"] = (
            lambda ep, predicate=predicate: STRONG if predicate(ep) else NONE
        )
    for k in range(1, 10):
        catalog[f"ROUNDS_GT_{k}"] = (
            lambda ep, k=k: STRONG if ep.get("round_count", 0) > k else NONE
        )
    for k in (40, 60, 100, 200):
        catalog[f"ANY_EVIDENCE_SHORTER_THAN_{k}"] = (
            lambda ep, k=k: STRONG
            if any(length < k for length in evidence_lengths(ep))
            else NONE
        )
    return catalog


def ablations() -> dict[str, Callable[[dict[str, Any]], str]]:
    """Detector-v1 with exactly one signal removed, to expose each signal's marginal effect."""
    variants: dict[str, Callable[[dict[str, Any]], str]] = {}
    for dropped in SIGNALS:
        def variant(ep: dict[str, Any], dropped: str = dropped) -> str:
            fired = {name for name, pred in SIGNALS.items() if name != dropped and pred(ep)}
            return classify_from_signals(fired)

        variants[f"V1_WITHOUT_{dropped}"] = variant
    return variants


def cohens_kappa(a: list[bool], b: list[bool]) -> float | None:
    """Chance-corrected agreement on the binary flag decision."""
    n = len(a)
    if n == 0:
        return None
    observed = sum(x == y for x, y in zip(a, b)) / n
    pa, pb = sum(a) / n, sum(b) / n
    expected = pa * pb + (1 - pa) * (1 - pb)
    if expected == 1.0:
        return None
    return round((observed - expected) / (1 - expected), 4)


def jaccard(a: list[bool], b: list[bool]) -> float | None:
    union = sum(x or y for x, y in zip(a, b))
    if union == 0:
        return None
    return round(sum(x and y for x, y in zip(a, b)) / union, 4)


def compare(labels: list[str], reference: list[str]) -> dict[str, Any]:
    n = len(labels)
    flag = [label in ALERT_CLASSES for label in labels]
    ref_flag = [label in ALERT_CLASSES for label in reference]
    return {
        "class_counts": dict(Counter(labels)),
        "flag_rate": round(sum(flag) / n, 4) if n else None,
        "distinct_classes": len(set(labels)),
        "discriminates_on_this_data": len(set(labels)) > 1,
        "exact_three_class_agreement": round(
            sum(x == y for x, y in zip(labels, reference)) / n, 4
        )
        if n
        else None,
        "binary_agreement": round(sum(x == y for x, y in zip(flag, ref_flag)) / n, 4) if n else None,
        "cohens_kappa_binary": cohens_kappa(flag, ref_flag),
        "jaccard_on_flagged": jaccard(flag, ref_flag),
        "identical_to_detector_v1": labels == reference,
    }


def chance_baseline(reference: list[str], seeds: int = RANDOM_SEEDS) -> dict[str, Any]:
    """What agreement does a coin weighted to Detector-v1's own flag rate produce?"""
    n = len(reference)
    ref_flag = [label in ALERT_CLASSES for label in reference]
    rate = sum(ref_flag) / n if n else 0.0
    agreements, kappas = [], []
    for seed in range(seeds):
        rng = random.Random(seed)
        draw = [rng.random() < rate for _ in range(n)]
        agreements.append(sum(x == y for x, y in zip(draw, ref_flag)) / n if n else 0.0)
        kappa = cohens_kappa(draw, ref_flag)
        if kappa is not None:
            kappas.append(kappa)
    agreements.sort()
    return {
        "matched_flag_rate": round(rate, 4),
        "seeds": seeds,
        "mean_binary_agreement": round(sum(agreements) / len(agreements), 4) if agreements else None,
        "p05_binary_agreement": round(agreements[int(0.05 * len(agreements))], 4)
        if agreements
        else None,
        "p95_binary_agreement": round(agreements[int(0.95 * len(agreements))], 4)
        if agreements
        else None,
        "mean_kappa": round(sum(kappas) / len(kappas), 4) if kappas else None,
        "interpretation": (
            "an agreement score at or below this band is what chance alone produces at "
            "Detector-v1's own flag rate, and carries no evidence of shared structure"
        ),
    }


def signal_space_coverage(episodes: list[dict[str, Any]]) -> dict[str, Any]:
    """How much of the rule's reachable input space does this corpus actually visit?"""
    names = list(SIGNALS)
    reachable = []
    for combination in itertools.product([False, True], repeat=len(names)):
        fired = {name for name, on in zip(names, combination) if on}
        # S7 forces a tenth round, so it cannot occur without S6.
        if "S7_TERMINATED_MAX_ROUNDS" in fired and "S6_MULTIPLE_QA_ROUNDS" not in fired:
            continue
        reachable.append(frozenset(fired))
    observed = {
        frozenset(name for name, pred in SIGNALS.items() if pred(ep))
        for ep in episodes
        if ep.get("scientific_complete")
    }
    by_class = Counter(classify_from_signals(set(pattern)) for pattern in reachable)
    return {
        "reachable_signal_patterns": len(reachable),
        "constraint_applied": "S7 implies S6, because a max-rounds termination requires >1 round",
        "observed_signal_patterns": len(observed),
        "coverage_fraction": round(len(observed) / len(reachable), 4) if reachable else None,
        "reachable_class_distribution": dict(by_class),
        "observed_patterns": sorted(sorted(pattern) for pattern in observed),
        "limitation": (
            "coverage counts which signal combinations occurred; it is not a measure of how "
            "likely each combination is, and carries no claim about other corpora"
        ),
    }


def score_run(label: str, events_path: Path) -> dict[str, Any]:
    events = [
        json.loads(line)
        for line in events_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    episodes = project_episodes(events)
    complete = [ep for ep in episodes if ep.get("scientific_complete")]
    reference = [detect_detector_v1(ep)["classification"] for ep in complete]

    catalog = {**baseline_catalog(), **ablations()}
    results = {
        name: compare([rule(ep) for ep in complete], reference) for name, rule in catalog.items()
    }
    for name in ablations():
        dropped = name.removeprefix("V1_WITHOUT_")
        labels = [catalog[name](ep) for ep in complete]
        results[name]["episodes_changed_by_removing_signal"] = sum(
            x != y for x, y in zip(labels, reference)
        )
        results[name]["signal_is_inert_on_this_data"] = labels == reference
        results[name]["dropped_signal"] = dropped

    equivalents = sorted(
        name
        for name, row in results.items()
        if row["identical_to_detector_v1"] and not name.startswith("V1_WITHOUT_")
    )
    signal_counts = {
        name: sum(1 for ep in complete if pred(ep)) for name, pred in SIGNALS.items()
    }
    return {
        "run_label": label,
        "denominator_complete_episodes": len(complete),
        "episodes_total": len(episodes),
        "episodes_excluded": len(episodes) - len(complete),
        "denominator_note": "this run is scored on its own denominator and is never pooled",
        "detector_v1_class_counts": dict(Counter(reference)),
        "detector_v1_flag_rate": round(
            sum(label in ALERT_CLASSES for label in reference) / len(reference), 4
        )
        if reference
        else None,
        "detector_v1_discriminates_on_this_data": len(set(reference)) > 1,
        "signal_fire_counts": signal_counts,
        "inert_signals_on_this_data": sorted(
            name for name, count in signal_counts.items() if count == 0
        ),
        "baselines": results,
        "baselines_equivalent_to_detector_v1": equivalents,
        "chance_baseline": chance_baseline(reference),
        "signal_space_coverage": signal_space_coverage(episodes),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--run",
        action="append",
        required=True,
        metavar="LABEL=PATH",
        help="a run label and its qa_events.jsonl; repeatable, never pooled",
    )
    parser.add_argument("--out", type=Path, default=None)
    args = parser.parse_args()

    runs = []
    for spec in args.run:
        label, _, path = spec.partition("=")
        runs.append(score_run(label, Path(path)))

    report = {
        "schema_version": "study1-detector-baselines-v1",
        "evidence_class": "ARCHIVAL_RETROSPECTIVE_DESCRIPTIVE_EVIDENCE",
        "what_this_measures": "selection agreement between rules, on data without ground truth",
        "what_this_cannot_measure": [
            "whether any alert was correct",
            "accuracy, precision, recall or F1",
            "effectiveness, human benefit or causality",
            "representativeness or generalization",
        ],
        "detector_v1_modified": False,
        "provider_calls": 0,
        "runs": runs,
    }
    text = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(text, encoding="utf-8")
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
