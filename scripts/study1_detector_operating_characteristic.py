"""Operating characteristic of Detector-v1: how its alert class depends on episode length.

Detector-v1 fires `STRONG_ALERT` whenever **any** answer in an episode carries `Low` confidence.
Any-of rules over a sequence have a property that is easy to miss when reading the rule text: the
probability that they fire grows with the length of the sequence, whatever the sequence contains.
A long episode is therefore more likely to be flagged than a short one at the same per-answer
rate, and past a certain length the rule flags essentially everything.

This module makes that dependence explicit. It computes, for the frozen rule:

  * `P(STRONG_ALERT)` as a function of episode length and the per-answer rate of `Low`;
  * the length at which the rule stops separating episodes in practice;
  * the same curve by resampling the **observed** answer pool, which avoids assuming a
    parametric rate but still assumes answers are exchangeable within an episode.

**This is a property of the rule, not an observation about the world.** Nothing here is an
empirical result, none of it is evidence that any alert was correct or incorrect, and the
independence and exchangeability assumptions below are assumptions the data does not verify —
answers within one episode plausibly influence each other, which the model ignores.

Detector-v1 is imported and applied, never modified. No provider is contacted.
"""

from __future__ import annotations

import argparse
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

LENGTHS = (1, 2, 3, 4, 5, 8, 10, 15, 20, 30, 39, 50)
LOW_RATES = (0.05, 0.10, 0.20, 0.364, 0.50)
RESAMPLE_DRAWS = 20_000
SEPARATION_BAND = (0.20, 0.80)


def analytic_strong_probability(low_rate: float, length: int) -> float:
    """P(at least one Low answer) = 1 - (1 - p)^k, the S1 branch acting alone."""
    return 1.0 - (1.0 - low_rate) ** length


def saturation_length(low_rate: float, ceiling: float = 0.95) -> int | None:
    """Shortest episode length at which the rule flags with probability >= ceiling."""
    if low_rate <= 0.0:
        return None
    length = 1
    while length <= 1000:
        if analytic_strong_probability(low_rate, length) >= ceiling:
            return length
        length += 1
    return None


def separation_window(low_rate: float) -> dict[str, Any]:
    """Episode lengths for which the rule's firing probability is neither near 0 nor near 1."""
    low, high = SEPARATION_BAND
    lengths = [
        length
        for length in range(1, 201)
        if low <= analytic_strong_probability(low_rate, length) <= high
    ]
    return {
        "band": f"P(STRONG) in [{low}, {high}]",
        "lengths_in_band": [lengths[0], lengths[-1]] if lengths else [],
        "band_width_in_answers": len(lengths),
        "meaning": (
            "outside this window the rule returns nearly the same verdict regardless of the "
            "episode's content, because length alone determines the outcome"
        ),
    }


def analytic_grid() -> list[dict[str, Any]]:
    return [
        {
            "low_rate": rate,
            "saturation_length_at_0_95": saturation_length(rate),
            "separation_window": separation_window(rate),
            "p_strong_by_length": {
                str(length): round(analytic_strong_probability(rate, length), 6)
                for length in LENGTHS
            },
        }
        for rate in LOW_RATES
    ]


def observed_answer_pool(episodes: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        answer
        for episode in episodes
        if episode.get("scientific_complete")
        for answer in episode.get("answers", [])
    ]


def resampled_curve(pool: list[dict[str, Any]], seed: int = 0) -> dict[str, Any]:
    """Firing rate for synthetic episodes drawn with replacement from the observed answers.

    This substitutes the observed answer distribution for a parametric rate. It still assumes
    answers are exchangeable within an episode, which the data does not establish. The synthetic
    episodes are a model of the instrument and are never reported as observations.
    """
    if not pool:
        return {"available": False, "reason": "no complete-episode answers available"}
    rng = random.Random(seed)
    curve = {}
    for length in LENGTHS:
        strong = 0
        for _ in range(RESAMPLE_DRAWS):
            drawn = [rng.choice(pool) for _ in range(length)]
            episode = {
                "episode_id": "SYNTHETIC",
                "answers": drawn,
                "round_count": 1,
                "termination_reason": "CONVERGED",
                "scientific_complete": True,
            }
            if detect_detector_v1(episode)["classification"] == "STRONG_ALERT":
                strong += 1
        curve[str(length)] = round(strong / RESAMPLE_DRAWS, 4)
    return {
        "available": True,
        "draws_per_length": RESAMPLE_DRAWS,
        "seed": seed,
        "pool_size": len(pool),
        "observed_confidence_mix": dict(
            Counter(answer.get("answer_confidence") for answer in pool)
        ),
        "p_strong_by_length": curve,
        "evidence_class": "ANALYTIC_MODEL_NOT_OBSERVATION",
    }


def observed_episodes_table(episodes: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows = []
    for episode in episodes:
        verdict = detect_detector_v1(episode)
        rows.append(
            {
                "answer_count": len(episode.get("answers", [])),
                "round_count": episode.get("round_count"),
                "termination_reason": episode.get("termination_reason"),
                "classification": verdict["classification"],
                "signals": verdict["all_signals_fired"],
            }
        )
    return sorted(rows, key=lambda row: row["answer_count"])


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
        episodes = project_episodes(events)
        pool = observed_answer_pool(episodes)
        runs.append(
            {
                "run_label": label,
                "denominator_complete_episodes": sum(
                    1 for episode in episodes if episode.get("scientific_complete")
                ),
                "observed_episodes": observed_episodes_table(episodes),
                "resampled_operating_characteristic": resampled_curve(pool),
            }
        )

    report = {
        "schema_version": "study1-detector-operating-characteristic-v1",
        "evidence_class": "DEFINITION_AND_ANALYTIC_MODEL",
        "subject": "the frozen Detector-v1 rule, not the corpus and not the world",
        "assumptions_the_data_does_not_verify": [
            "answers within an episode are independent (analytic curve)",
            "answers within an episode are exchangeable (resampled curve)",
        ],
        "what_this_is_not": [
            "not an empirical result",
            "not evidence that any alert was correct or incorrect",
            "not a measure of accuracy, precision, recall or F1",
            "not a claim about any corpus other than the one resampled",
        ],
        "detector_v1_modified": False,
        "provider_calls": 0,
        "analytic_grid": analytic_grid(),
        "runs": runs,
    }
    text = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(text, encoding="utf-8")
    print(text[:1200])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
