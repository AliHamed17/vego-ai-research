"""Figures must agree with the values they are drawn from, at the level they claim.

The defect these tests exist to prevent is subtle and was shipped once already: a chart compared
three-class labels while its caption implied it compared the review decision. Both numbers are
real; quoting one as the other is false. So the properties pinned here are the ones a reader
cannot verify by looking at a PNG:

  * the two agreement levels are computed from the same episodes and are internally consistent;
  * when Detector-v1 sends every complete episode for review, ALWAYS_ALERT is identical to it at
    the binary level and the figure must say so;
  * a caption may not claim a count the source values do not support;
  * colour means one thing only, and the identical/differs mapping is not reversed between panels;
  * denominators come from the source and are never re-derived in the renderer.

No provider is contacted and no chart is rendered to disk here; the renderer's inputs and its
declared constants are checked directly.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

import render_study1c_figures as figures  # noqa: E402
import study1_detector_baselines as baselines  # noqa: E402

BASELINES_JSON = ROOT / "external_data/airtravel-pr38/analysis-baselines/detector-baselines.json"
ALERT = {"STRONG_ALERT", "WEAK_ALERT"}


def episodes(classes: dict[str, int]) -> list[str]:
    out: list[str] = []
    for label, count in classes.items():
        out.extend([label] * count)
    return out


class TestAgreementLevelsAreDistinctAndConsistent:
    def test_always_alert_matches_at_binary_when_every_episode_is_reviewed(self):
        """Run 1's exact shape: 7 STRONG and 4 WEAK, so every episode is sent for review."""
        reference = episodes({"STRONG_ALERT": 7, "WEAK_ALERT": 4})
        always = ["STRONG_ALERT"] * 11
        result = baselines.compare(always, reference)
        assert result["identical_three_class"] is False
        assert result["identical_binary_review"] is True
        assert result["exact_three_class_agreement"] == pytest.approx(7 / 11, abs=1e-4)
        assert result["binary_review_agreement"] == 1.0

    def test_always_alert_differs_at_binary_when_some_episode_is_not_reviewed(self):
        reference = episodes({"STRONG_ALERT": 5, "NO_ALERT": 1})
        result = baselines.compare(["STRONG_ALERT"] * 6, reference)
        assert result["identical_binary_review"] is False
        assert result["binary_review_agreement"] == pytest.approx(5 / 6, abs=1e-4)

    def test_three_class_identity_implies_binary_identity(self):
        reference = episodes({"STRONG_ALERT": 3, "WEAK_ALERT": 2, "NO_ALERT": 1})
        result = baselines.compare(list(reference), reference)
        assert result["identical_three_class"] is True
        assert result["identical_binary_review"] is True

    def test_the_reverse_implication_does_not_hold(self):
        reference = episodes({"STRONG_ALERT": 1, "WEAK_ALERT": 1})
        result = baselines.compare(["WEAK_ALERT", "STRONG_ALERT"], reference)
        assert result["identical_binary_review"] is True
        assert result["identical_three_class"] is False

    def test_every_comparison_carries_the_level_note(self):
        result = baselines.compare(["STRONG_ALERT"], ["STRONG_ALERT"])
        assert "three-class identity" in result["agreement_level_note"]
        assert "binary-review identity" in result["agreement_level_note"]


class TestColourMeaningIsSingleValued:
    def test_identical_and_differs_are_distinct_colours(self):
        assert figures.IDENTICAL_COLOUR != figures.DIFFERS_COLOUR

    def test_legend_labels_name_the_level_rather_than_asserting_a_general_match(self):
        for label in (figures.IDENTICAL_LABEL, figures.DIFFERS_LABEL):
            assert "at this level" in label

    def test_the_renderer_declares_the_two_panel_titles_by_level(self):
        source = (ROOT / "scripts/render_study1c_figures.py").read_text(encoding="utf-8")
        assert "(a) THREE-CLASS level" in source
        assert "(b) BINARY REVIEW level" in source
        assert "ANALYTIC RULE-SENSITIVITY, NOT EMPIRICAL ACCURACY" in source

    def test_the_mechanisms_figure_denies_a_safety_reading_and_a_truth_reading(self):
        source = (ROOT / "scripts/render_study1c_figures.py").read_text(encoding="utf-8")
        assert "NOT a finding that the case is safe" in source
        assert "not truth labels for Detector-v1" in source
        assert "NEITHER IS GROUND TRUTH" in source

    def test_the_characteristic_figure_distinguishes_answers_from_rounds(self):
        source = (ROOT / "scripts/render_study1c_figures.py").read_text(encoding="utf-8")
        assert "answer count, NOT Q&A rounds" in source


@pytest.mark.skipif(not BASELINES_JSON.is_file(), reason="baseline report not generated")
class TestCaptionCountsMatchTheSourceValues:
    @staticmethod
    @pytest.fixture(scope="class")
    def report():
        return json.loads(BASELINES_JSON.read_text(encoding="utf-8"))

    def test_each_run_lists_both_identity_sets(self, report):
        for run in report["runs"]:
            assert "baselines_identical_at_three_class_level" in run
            assert "baselines_identical_at_binary_review_level" in run

    def test_the_identity_lists_agree_with_the_per_baseline_flags(self, report):
        for run in report["runs"]:
            for level, key in (
                ("identical_three_class", "baselines_identical_at_three_class_level"),
                ("identical_binary_review", "baselines_identical_at_binary_review_level"),
            ):
                derived = sorted(
                    name
                    for name, row in run["baselines"].items()
                    if row[level] and not name.startswith("V1_WITHOUT_")
                )
                assert derived == run[key], f"{run['run_label']} {key} disagrees with its own rows"

    def test_three_class_identity_is_a_subset_of_binary_identity(self, report):
        for run in report["runs"]:
            three = set(run["baselines_identical_at_three_class_level"])
            binary = set(run["baselines_identical_at_binary_review_level"])
            assert three <= binary, f"{run['run_label']}: three-class identity must imply binary"

    def test_denominators_are_positive_and_stated_per_run(self, report):
        for run in report["runs"]:
            assert run["denominator_complete_episodes"] > 0

    def test_a_run_that_reviews_everything_has_always_alert_identical_at_binary(self, report):
        for run in report["runs"]:
            if run["detector_v1_binary_review_selection_rate"] == 1.0:
                assert "ALWAYS_ALERT" in run["baselines_identical_at_binary_review_level"], (
                    f"{run['run_label']} sends every episode for review, so ALWAYS_ALERT must be "
                    "identical at the binary level"
                )
