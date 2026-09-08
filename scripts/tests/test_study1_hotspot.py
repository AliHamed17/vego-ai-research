"""Tests for the human-review hotspot instrument: freeze, blinding, adjudication, refusal.

The study's integrity rests on four things a reader cannot check by eye, so they are pinned here:

  1. **The freeze binds.** The case draw is reproducible from the seed alone, and the pessimistic
     reservation actually fits the ceiling it claims to fit.
  2. **The blinding holds.** A card carrying a detector label, a signal name or a confidence
     value must fail the audit rather than reach a rater.
  3. **The adjudication rule is the frozen one.** Disagreement stays disagreement, and
     "Insufficient information" is never folded into "No".
  4. **Missing human labels produce a refusal, not a substitute.** Tables B and C must report
     NOT_AVAILABLE with the missing inputs named, and no code path may fill them.

No provider is contacted and no run is executed.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

import study1_hotspot_analysis as analysis  # noqa: E402
import study1_hotspot_manifest as freeze  # noqa: E402
import study1_hotspot_rater_cards as cards  # noqa: E402

MANIFEST_PATH = ROOT / "docs/research/phd-proposal/study1-hotspot-manifest.json"


@pytest.fixture(scope="module")
def manifest():
    return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))


class TestTheFreezeBinds:
    def test_the_draw_is_reproducible_from_the_seed_alone(self, manifest):
        rows = freeze.eligible_case_rows()
        redrawn = [row["path"] for row in freeze.draw_sample(rows)]
        recorded = [row["path"] for row in manifest["selection"]["selected"]]
        assert redrawn == recorded

    def test_the_draw_comes_from_the_whole_eligible_frame(self, manifest):
        assert manifest["corpus"]["eligible_case_count"] == 21
        assert len(manifest["selection"]["selected"]) == 6
        eligible = set(manifest["corpus"]["eligible_case_paths"])
        assert {row["path"] for row in manifest["selection"]["selected"]} <= eligible

    def test_the_pessimistic_reservation_fits_the_ceiling(self, manifest):
        budget = manifest["budget"]
        assert budget["fits"] is True
        assert budget["whole_study_reservation_usd"] == pytest.approx(
            budget["call_cap"] * budget["per_request_worst_case_usd"] * budget["run_count"]
        )
        assert budget["whole_study_reservation_usd"] <= budget["ceiling_usd"]

    def test_the_primary_outcome_declares_its_human_precondition(self, manifest):
        assert "two independent blinded human raters" in manifest["primary_outcome_requires"]

    def test_the_detector_scope_is_recorded_and_not_conflated_with_the_queue(self, manifest):
        scope = manifest["detector_v1"]["scope"]
        assert "reporting-only" in scope
        assert "does not create" in scope
        assert "Agent-4" in scope

    @pytest.mark.parametrize(
        "phrase",
        [
            "that any Detector-v1 alert was correct",
            "causality or any ON/OFF advantage",
            "representativeness or generalization beyond this corpus and configuration",
            "that Detector-v1 creates or feeds a human queue",
        ],
    )
    def test_the_forbidden_claims_are_frozen(self, manifest, phrase):
        assert phrase in manifest["forbidden_claims"]


class TestBlindingHolds:
    def make_card(self, **overrides):
        card = {
            "card_id": "CARD-001",
            "exchanges": [
                {"round": 1, "question": "q", "answer": "a", "evidence_present": True,
                 "evidence_length_characters": 10}
            ],
            "route": ["agent3 asks agent2"],
            "round_count": 1,
            "question_count": 1,
            "answers_with_evidence": 1,
            "answers_without_evidence": 0,
        }
        card.update(overrides)
        return card

    def test_a_clean_card_passes(self):
        assert cards.audit_blinding([self.make_card()]) == []

    @pytest.mark.parametrize(
        "leak",
        [
            {"classification": "STRONG_ALERT"},
            {"signals": ["S1_LOW_ANSWER_CONFIDENCE"]},
            {"answer_confidence": "Low"},
            {"run_label": "FULLFRAME-01"},
        ],
    )
    def test_a_card_carrying_a_withheld_field_is_refused(self, leak):
        problems = cards.audit_blinding([self.make_card(**leak)])
        assert problems, f"audit failed to catch {leak}"

    def test_a_detector_token_hidden_inside_a_permitted_field_is_refused(self):
        card = self.make_card()
        card["exchanges"][0]["answer"] = "this episode is a STRONG_ALERT"
        assert cards.audit_blinding([card])

    def test_the_card_field_set_is_exactly_the_frozen_one(self):
        assert cards.ALLOWED_CARD_KEYS == {
            "card_id", "exchanges", "route", "round_count", "question_count",
            "answers_with_evidence", "answers_without_evidence",
        }

    def test_card_ids_are_shuffled_so_order_carries_no_signal(self):
        made = [self.make_card(card_id=None) for _ in range(10)]
        key = [{"card_id": None, "episode_id": f"EP-{i}"} for i in range(10)]
        cards.assign_ids(made, key)
        mapping = {row["card_id"]: row["episode_id"] for row in key}
        assert mapping["CARD-001"] != "EP-0"


class TestAdjudicationRule:
    @pytest.mark.parametrize(
        "a,b,expected",
        [
            ("Yes", "Yes", analysis.WORTHY),
            ("No", "No", analysis.NOT_WORTHY),
            ("Insufficient information", "Insufficient information", analysis.INSUFFICIENT),
            ("Yes", "No", analysis.DISAGREEMENT),
            ("Yes", "Insufficient information", analysis.DISAGREEMENT),
            ("No", "Insufficient information", analysis.DISAGREEMENT),
        ],
    )
    def test_the_frozen_rule_is_applied(self, a, b, expected):
        assert analysis.adjudicate({"CARD-001": a}, {"CARD-001": b}) == {"CARD-001": expected}

    def test_insufficient_is_never_folded_into_no(self):
        verdicts = analysis.adjudicate(
            {"C": "Insufficient information"}, {"C": "Insufficient information"}
        )
        assert verdicts["C"] == analysis.INSUFFICIENT
        assert verdicts["C"] != analysis.NOT_WORTHY

    def test_a_missing_second_rater_is_not_a_verdict(self):
        assert analysis.adjudicate({"C": "Yes"}, {})["C"] == analysis.NOT_AVAILABLE


class TestMissingLabelsProduceRefusal:
    def rows(self):
        return [
            {"run_label": "R", "episode_id": f"EP-{i}", "case_id": "01",
             "classification": cls, "signals": [], "answers": 3, "round_count": 1,
             "termination_reason": "CONVERGED", "complete": True}
            for i, cls in enumerate(["STRONG_ALERT", "STRONG_ALERT", "WEAK_ALERT"])
        ]

    def test_table_b_refuses_without_raters(self):
        table = analysis.table_b(self.rows(), None, None)
        assert table["status"] == analysis.NOT_AVAILABLE
        assert table["substitution_permitted"] is False
        assert table["precision"] == analysis.NOT_AVAILABLE
        assert table["recall"] == analysis.NOT_AVAILABLE
        assert table["confusion_matrix"] == analysis.NOT_AVAILABLE

    def test_table_b_still_reports_what_needs_no_raters(self):
        table = analysis.table_b(self.rows(), None, None)
        assert table["alert_rate"] == 1.0
        assert table["denominator_complete_episodes"] == 3

    def test_table_c_refuses_retention_and_minutes_without_raters(self):
        table = analysis.table_c(self.rows(), None, None, [], None)
        assert table["proportion_of_human_worthy_retained"] == analysis.NOT_AVAILABLE
        assert table["review_minutes_saved"] == analysis.NOT_AVAILABLE
        assert table["unavailable"]["substitution_permitted"] is False

    def test_table_c_reports_the_workload_split_which_needs_no_raters(self):
        table = analysis.table_c(self.rows(), None, None, [], None)
        assert table["all_episodes_review_workload"] == 3
        assert table["detector_prioritized_review_workload"] == 2
        assert table["workload_reduction_fraction"] == pytest.approx(1 / 3, abs=1e-4)

    def test_minutes_are_never_estimated_when_unmeasured(self):
        verdicts = {"CARD-001": analysis.WORTHY}
        key = {"CARD-001": "EP-0"}
        table = analysis.table_c(self.rows(), verdicts, key, [], None)
        assert table["review_minutes_saved"] == analysis.NOT_AVAILABLE
        assert "may not be estimated" in table["review_minutes_basis"]

    def test_the_wide_prioritized_set_is_degenerate_at_an_alert_rate_of_one(self):
        """The reason the manifest fixes the prioritized set to STRONG_ALERT before results."""
        result = analysis.sensitivity(self.rows())
        assert result["preregistered"] is True
        assert result["workload_reduction_fraction"] == 0.0


class TestExecutionGates:
    def test_an_unevaluable_ci_status_is_treated_as_failure(self, monkeypatch):
        import study1_hotspot_execute as execute

        monkeypatch.setattr(
            execute.subprocess, "run",
            lambda *a, **k: type("R", (), {"stdout": "not json"})(),
        )
        with pytest.raises(execute.GateFailure, match="could not read CI status"):
            execute.gate_ci_green("deadbeef")

    def test_ci_at_a_different_head_does_not_satisfy_the_gate(self, monkeypatch):
        import study1_hotspot_execute as execute

        payload = json.dumps(
            [{"databaseId": 1, "status": "completed", "conclusion": "success",
              "headSha": "aaaa", "workflowName": "w"}]
        )
        monkeypatch.setattr(
            execute.subprocess, "run", lambda *a, **k: type("R", (), {"stdout": payload})()
        )
        with pytest.raises(execute.GateFailure, match="no CI run found at exact head"):
            execute.gate_ci_green("bbbb")

    def test_a_failing_ci_conclusion_refuses(self, monkeypatch):
        import study1_hotspot_execute as execute

        payload = json.dumps(
            [{"databaseId": 1, "status": "completed", "conclusion": "failure",
              "headSha": "aaaa", "workflowName": "w"}]
        )
        monkeypatch.setattr(
            execute.subprocess, "run", lambda *a, **k: type("R", (), {"stdout": payload})()
        )
        with pytest.raises(execute.GateFailure, match="concluded"):
            execute.gate_ci_green("aaaa")

    def test_untracked_executable_code_refuses(self, monkeypatch):
        import study1_hotspot_execute as execute

        monkeypatch.setattr(execute, "git", lambda *a: "?? scripts/sneaky.py")
        with pytest.raises(execute.GateFailure, match="untracked executable code"):
            execute.gate_clean_tree()

    def test_an_untracked_document_does_not_block_execution(self, monkeypatch):
        import study1_hotspot_execute as execute

        monkeypatch.setattr(execute, "git", lambda *a: "?? docs/notes.md")
        assert execute.gate_clean_tree()["clean_tree"] is True
