"""Review load under alternative round bounds, for supervisor directives D6 and D10.

Two standing directives meet in Detector-v1's output:

  * **D6, configurable intervention dosage.** The dosage work measures *load* — the share of
    items sent to a human — against a target of load <= 0.5, recorded as unmet. Detector-v1's
    load is directly computable from any run: it is the share of complete episodes it flags.
  * **D10, convergence through bounded interaction.** The round-bound sweep named a two-round
    policy as the pilot candidate, explicitly not an approved default. Because Detector-v1's
    S1 branch fires on *any* low-confidence answer, the round bound controls episode length,
    and episode length drives whether the rule can separate episodes at all.

This module re-scores already-observed episodes under hypothetical round bounds and reports the
resulting load, so the two directives can be discussed against numbers rather than intuitions.

**The central limitation, stated before any number.** Truncating an observed episode at round k
is **not** the same as having run the pipeline with `MAX_QA_ROUNDS = k`. Under a real lower
bound the agents would have asked different questions and received different answers, and the
episode would have terminated differently — `TERMINATED_MAX_ROUNDS` would fire at k rather than
at 10. This is a re-scoring of answers that were actually observed, not a simulation of a
counterfactual run, and it cannot predict what a bounded run would produce.

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

from extract_qa_escalation_features import MAX_QA_ROUNDS, detect_detector_v1  # noqa: E402

ALERT_CLASSES = {"STRONG_ALERT", "WEAK_ALERT"}
DOSAGE_LOAD_TARGET = 0.5


def project_with_rounds(events: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Project episodes while retaining each answer's round index, which the frozen projection drops."""
    rounds = {
        event["question_id"]: event.get("round_index") or 0
        for event in events
        if event["event_type"] == "QUESTION_EMITTED"
    }
    episodes: dict[str, dict[str, Any]] = {}
    for event in events:
        episode = episodes.setdefault(
            event["episode_id"],
            {
                "episode_id": event["episode_id"],
                "answers": [],
                "round_count": 0,
                "question_count": 0,
                "termination_reason": None,
            },
        )
        if event["event_type"] == "QUESTION_EMITTED":
            episode["question_count"] += 1
            episode["round_count"] = max(episode["round_count"], event.get("round_index") or 0)
        elif event["event_type"] == "ANSWER_RECEIVED":
            episode["answers"].append(
                {
                    "answer_confidence": event.get("answer_confidence"),
                    "answer_evidence_ref": event.get("answer_evidence_ref"),
                    "round_index": rounds.get(event.get("question_id"), 0),
                }
            )
        elif event["event_type"] == "EPISODE_TERMINATED":
            episode["termination_reason"] = event.get("termination_reason")
    for episode in episodes.values():
        episode["scientific_complete"] = episode["termination_reason"] in {
            "CONVERGED",
            "TERMINATED_MAX_ROUNDS",
        }
    return list(episodes.values())


def truncate(episode: dict[str, Any], bound: int) -> dict[str, Any]:
    """Keep only answers from rounds at or below the bound, and re-derive the round count."""
    kept = [
        answer for answer in episode["answers"] if (answer.get("round_index") or 0) <= bound
    ]
    # Only an episode that actually needed more rounds than the bound allows would have been
    # cut off by it. One that converged at or before the bound still converges.
    reached_bound = episode["round_count"] > bound
    return {
        "episode_id": episode["episode_id"],
        "answers": kept,
        "round_count": min(episode["round_count"], bound),
        # Under a bound of k, an episode that ran to k or beyond ends by hitting that bound.
        "termination_reason": (
            "TERMINATED_MAX_ROUNDS" if reached_bound else episode["termination_reason"]
        ),
        "scientific_complete": episode["scientific_complete"],
    }


def score(episodes: list[dict[str, Any]], bound: int | None) -> dict[str, Any]:
    complete = [ep for ep in episodes if ep.get("scientific_complete")]
    scored = [ep if bound is None else truncate(ep, bound) for ep in complete]
    labels = [detect_detector_v1(ep)["classification"] for ep in scored]
    flagged = sum(1 for label in labels if label in ALERT_CLASSES)
    load = flagged / len(labels) if labels else None
    return {
        "round_bound": bound if bound is not None else MAX_QA_ROUNDS,
        "is_observed_configuration": bound is None,
        "denominator_complete_episodes": len(labels),
        "class_counts": dict(Counter(labels)),
        "review_load": round(load, 4) if load is not None else None,
        "meets_d6_load_target": (load <= DOSAGE_LOAD_TARGET) if load is not None else None,
        "distinct_classes": len(set(labels)),
        "separates_episodes": len(set(labels)) > 1,
        "mean_answers_per_episode": round(
            sum(len(ep["answers"]) for ep in scored) / len(scored), 2
        )
        if scored
        else None,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", action="append", required=True, metavar="LABEL=PATH")
    parser.add_argument("--out", type=Path, default=None)
    args = parser.parse_args()

    runs = []
    for spec in args.run:
        label, _, path = spec.partition("=")
        events = [
            json.loads(line)
            for line in Path(path).read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
        episodes = project_with_rounds(events)
        runs.append(
            {
                "run_label": label,
                "observed_configuration": score(episodes, None),
                "rescored_under_bounds": [
                    score(episodes, bound) for bound in range(1, MAX_QA_ROUNDS + 1)
                ],
            }
        )

    report = {
        "schema_version": "study1-round-bound-sensitivity-v1",
        "evidence_class": "RESCORING_OF_OBSERVED_ANSWERS_NOT_A_SIMULATED_RUN",
        "serves_directives": {
            "D6": "configurable intervention dosage; recorded load target <= 0.5, unmet",
            "D10": "convergence through bounded interaction; two-round pilot candidate",
        },
        "central_limitation": (
            "truncating an observed episode at round k is not equivalent to running the "
            "pipeline with MAX_QA_ROUNDS = k; under a real bound the agents would have asked "
            "different questions and received different answers"
        ),
        "what_this_cannot_support": [
            "any prediction of what a bounded run would produce",
            "alert correctness, accuracy, precision, recall or F1",
            "any recommendation that a bound be adopted",
        ],
        "detector_v1_modified": False,
        "provider_calls": 0,
        "runs": runs,
    }
    text = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(text, encoding="utf-8")
    print(text[:900])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
