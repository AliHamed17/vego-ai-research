"""Tests for the offline baseline, operating-characteristic and round-bound instruments.

These instruments exist to stop a reader from over-reading Detector-v1's output, so the
properties worth testing are the ones that would let an over-reading slip through: a baseline
that silently disagrees with the frozen rule, an agreement score reported without the chance
band that makes it interpretable, a truncation that invents a termination the data never showed,
and a signal counted as contributing when it changed nothing.

No provider is contacted and no run is executed.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

import study1_detector_baselines as baselines  # noqa: E402
import study1_detector_operating_characteristic as characteristic  # noqa: E402
import study1_round_bound_sensitivity as bounds  # noqa: E402
from extract_qa_escalation_features import detect_detector_v1  # noqa: E402


def episode(confidences, *, rounds=1, termination="CONVERGED", evidence_length=100):
    return {
        "episode_id": "EP-TEST",
        "answers": [
            {
                "answer_confidence": confidence,
                "answer_evidence_ref": {"length": evidence_length},
            }
            for confidence in confidences
        ],
        "round_count": rounds,
        "question_count": len(confidences),
        "termination_reason": termination,
        "scientific_complete": termination in {"CONVERGED", "TERMINATED_MAX_ROUNDS"},
    }


def rounded_episode(rounds_present, *, round_count, termination, confidence="High"):
    return {
        "episode_id": "EP",
        "answers": [
            {
                "answer_confidence": confidence,
                "answer_evidence_ref": {"length": 50},
                "round_index": index,
            }
            for index in rounds_present
        ],
        "round_count": round_count,
        "termination_reason": termination,
        "scientific_complete": True,
    }


class TestSignalPredicatesMatchTheFrozenRule:
    """The suite reimplements the signal predicates; they must agree with Detector-v1 itself."""

    @pytest.mark.parametrize(
        "confidences,rounds,termination",
        [
            (["High"], 1, "CONVERGED"),
            (["Low"], 1, "CONVERGED"),
            (["Medium"], 1, "CONVERGED"),
            (["High", "Medium"], 2, "CONVERGED"),
            (["High"], 10, "TERMINATED_MAX_ROUNDS"),
            (["Low", "Medium", "High"], 3, "CONVERGED"),
        ],
    )
    def test_classification_from_signals_reproduces_detector_v1(
        self, confidences, rounds, termination
    ):
        subject = episode(confidences, rounds=rounds, termination=termination)
        fired = {name for name, predicate in baselines.SIGNALS.items() if predicate(subject)}
        assert baselines.classify_from_signals(fired) == detect_detector_v1(subject)[
            "classification"
        ]

    def test_missing_evidence_reference_counts_as_zero_length(self):
        subject = episode(["High"])
        subject["answers"][0]["answer_evidence_ref"] = None
        assert baselines.evidence_lengths(subject) == [0]
        assert baselines.SIGNALS["S3_MISSING_ANSWER_EVIDENCE"](subject)


class TestAgreementMetrics:
    def test_identical_labels_agree_exactly_at_both_levels(self):
        labels = ["STRONG_ALERT", "NO_ALERT", "WEAK_ALERT"]
        result = baselines.compare(labels, labels)
        assert result["identical_three_class"]
        assert result["identical_binary_review"]
        assert result["exact_three_class_agreement"] == 1.0
        assert result["binary_review_agreement"] == 1.0
        assert result["jaccard_on_flagged"] == 1.0

    def test_kappa_is_none_when_chance_agreement_is_total(self):
        assert baselines.cohens_kappa([True, True], [True, True]) is None

    def test_kappa_is_zero_for_independent_flags(self):
        assert baselines.cohens_kappa([True, True, False, False], [True, False, True, False]) == 0.0

    def test_flagging_everything_agrees_perfectly_and_discriminates_nothing(self):
        """The finding this guards: perfect agreement is uninformative at a flag rate of one."""
        reference = ["STRONG_ALERT"] * 3
        result = baselines.compare(["STRONG_ALERT"] * 3, reference)
        assert result["identical_three_class"]
        assert result["identical_binary_review"]
        assert not result["discriminates_on_this_data"]

    def test_always_alert_differs_at_three_class_but_matches_at_binary(self):
        """The distinction the package previously collapsed into one ambiguous word."""
        reference = ["STRONG_ALERT"] * 7 + ["WEAK_ALERT"] * 4
        result = baselines.compare(["STRONG_ALERT"] * 11, reference)
        assert result["identical_three_class"] is False
        assert result["identical_binary_review"] is True

    def test_chance_baseline_reproduces_the_reference_flag_rate(self):
        chance = baselines.chance_baseline(["STRONG_ALERT"] * 3, seeds=50)
        assert chance["matched_flag_rate"] == 1.0
        assert chance["mean_binary_agreement"] == 1.0


class TestSignalSpaceCoverage:
    def test_s7_without_s6_is_excluded_as_unreachable(self):
        coverage = baselines.signal_space_coverage([])
        assert coverage["reachable_signal_patterns"] == 24
        assert coverage["observed_signal_patterns"] == 0

    def test_most_of_the_reachable_space_maps_to_strong(self):
        """A structural property of the rule, and why an all-STRONG run is unsurprising."""
        distribution = baselines.signal_space_coverage([])["reachable_class_distribution"]
        assert distribution == {"STRONG_ALERT": 20, "WEAK_ALERT": 3, "NO_ALERT": 1}


class TestAblationsExposeInertSignals:
    def test_removing_an_unfired_signal_changes_nothing(self):
        subject = episode(["Low"])
        variant = baselines.ablations()["V1_WITHOUT_S7_TERMINATED_MAX_ROUNDS"]
        assert variant(subject) == detect_detector_v1(subject)["classification"]

    def test_removing_the_only_strong_signal_downgrades_the_class(self):
        subject = episode(["Low", "Medium"], rounds=2)
        variant = baselines.ablations()["V1_WITHOUT_S1_LOW_ANSWER_CONFIDENCE"]
        assert detect_detector_v1(subject)["classification"] == "STRONG_ALERT"
        assert variant(subject) == "WEAK_ALERT"


class TestRoundBoundTruncation:
    def test_an_episode_that_converged_within_the_bound_keeps_its_termination(self):
        """The defect found on first output: converging at the bound is not being cut off by it."""
        subject = rounded_episode([1], round_count=1, termination="CONVERGED")
        assert bounds.truncate(subject, 1)["termination_reason"] == "CONVERGED"

    def test_an_episode_that_needed_more_rounds_is_cut_off_by_the_bound(self):
        subject = rounded_episode([1, 2, 3], round_count=3, termination="CONVERGED")
        truncated = bounds.truncate(subject, 2)
        assert truncated["termination_reason"] == "TERMINATED_MAX_ROUNDS"
        assert len(truncated["answers"]) == 2
        assert truncated["round_count"] == 2

    def test_a_bound_above_the_observed_depth_changes_nothing(self):
        subject = rounded_episode([1], round_count=1, termination="CONVERGED", confidence="Low")
        truncated = bounds.truncate(subject, 10)
        assert len(truncated["answers"]) == 1
        assert truncated["termination_reason"] == "CONVERGED"

    def test_load_is_the_share_of_flagged_episodes(self):
        flagged = rounded_episode([1], round_count=1, termination="CONVERGED", confidence="Low")
        clear = rounded_episode([1], round_count=1, termination="CONVERGED", confidence="High")
        scored = bounds.score([flagged, clear], None)
        assert scored["review_load"] == 0.5
        assert scored["meets_d6_load_target"] is True
        assert scored["separates_episodes"] is True


class TestOperatingCharacteristic:
    def test_probability_grows_with_length(self):
        values = [characteristic.analytic_strong_probability(0.2, k) for k in (1, 2, 5, 10)]
        assert values == sorted(values)
        assert values[0] == pytest.approx(0.2)

    def test_a_zero_rate_never_fires_and_never_saturates(self):
        assert characteristic.analytic_strong_probability(0.0, 100) == 0.0
        assert characteristic.saturation_length(0.0) is None

    def test_saturation_length_is_the_first_length_at_or_above_the_ceiling(self):
        length = characteristic.saturation_length(0.364)
        assert characteristic.analytic_strong_probability(0.364, length) >= 0.95
        assert characteristic.analytic_strong_probability(0.364, length - 1) < 0.95

    def test_separation_window_narrows_as_the_rate_rises(self):
        wide = characteristic.separation_window(0.05)["band_width_in_answers"]
        narrow = characteristic.separation_window(0.5)["band_width_in_answers"]
        assert wide > narrow

    def test_resampled_curve_is_labelled_a_model_not_an_observation(self):
        pool = [{"answer_confidence": "Low", "answer_evidence_ref": {"length": 50}}]
        assert characteristic.resampled_curve(pool)["evidence_class"] == (
            "ANALYTIC_MODEL_NOT_OBSERVATION"
        )

    def test_resampling_refuses_an_empty_pool_rather_than_reporting_zero(self):
        assert characteristic.resampled_curve([])["available"] is False


class TestDeclaredBoundaries:
    @pytest.mark.parametrize(
        "script,phrase",
        [
            ("study1_detector_baselines.py", "runs are never pooled"),
            (
                "study1_round_bound_sensitivity.py",
                "the same as having run the pipeline",
            ),
            (
                "study1_detector_operating_characteristic.py",
                "Nothing here is an empirical result",
            ),
        ],
    )
    def test_each_instrument_states_its_boundary_in_its_own_help(self, script, phrase):
        result = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / script), "--help"],
            capture_output=True,
            text=True,
            check=True,
        )
        assert phrase in " ".join(result.stdout.split())
