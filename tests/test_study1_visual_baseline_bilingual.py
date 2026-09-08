from __future__ import annotations

import json
from pathlib import Path

import pytest
from build_study1_visual_baseline_bilingual import (
    PDF_FIXED_TIMESTAMP,
    EvidenceError,
    _translations,
    build_html,
    load_evidence,
    normalize_pdf_metadata,
)

ROOT = Path(__file__).resolve().parents[1]


def test_load_evidence_recomputes_the_published_operational_baseline() -> None:
    facts = load_evidence(ROOT)

    assert facts["run_id"] == "S2P-LIVE-20260908T192135Z"
    assert facts["planned_cases"] == 12
    assert facts["on_completed"] == 9
    assert facts["off_completed"] == 12
    assert facts["evidence_class"] == "PROSPECTIVE EMPIRICAL EVIDENCE"
    assert facts["on_status"] == "STOPPED_AT_CAP"
    assert facts["not_produced_case_ids"] == ["18", "20", "21"]
    assert facts["case_21_status"] == "NOT_PRODUCED"
    assert facts["on_cost_usd"] == pytest.approx(0.902863)
    assert facts["off_cost_usd"] == pytest.approx(0.053045)
    assert facts["cost_total_ratio"] == pytest.approx(17.0207, rel=1e-4)
    assert facts["cost_per_completed_ratio"] == pytest.approx(22.6964, rel=1e-4)
    assert facts["time_total_ratio"] == pytest.approx(7.1756, rel=1e-4)
    assert facts["time_per_completed_ratio"] == pytest.approx(9.5674, rel=1e-4)
    assert facts["qa_questions"] == 255
    assert facts["qa_answers"] == 250
    assert facts["episodes_total"] == 16
    assert facts["episodes_complete"] == 14
    assert facts["alerts_strong"] == 13
    assert facts["alerts_weak"] == 1
    assert facts["alerts_excluded"] == 2
    assert facts["human_raters_scored"] == 0
    assert facts["human_raters_required"] == 2
    assert facts["supervisor_reviewers_required"] == 3
    assert facts["agent4_labelled_requests"] == 0
    assert facts["agent4_archival_status"] == "EXECUTED_THEN_BLOCKED"
    assert facts["agent4_archival_queue_status"] == "NOT_AVAILABLE"
    assert facts["temperature"] == "PROVIDER_DEFAULT_NOT_SENT"
    assert facts["overlap_study1_inputs"] == 3
    assert facts["on_setting_level_requests"] == 2
    assert facts["on_setting_level_cost_usd"] == pytest.approx(0.007457)


def test_uncertainty_extension_is_recomputed_from_the_tracked_aggregate() -> None:
    facts = load_evidence(ROOT)

    assert facts["objective_known_unknown_status"] == "NOT_MEASURED"
    assert facts["objective_known_unknown_field"] == "NOT_AVAILABLE_IN_TRACKED_AGGREGATE"
    assert facts["detection_timing"] == "POST_EPISODE_TERMINATION_REPORTING"
    assert facts["episode_round_distribution"] == [
        {"round_count": 2, "episodes": 3},
        {"round_count": 3, "episodes": 1},
        {"round_count": 4, "episodes": 4},
        {"round_count": 10, "episodes": 6},
    ]
    assert facts["round_termination_distribution"][-1] == {
        "round_count": 10,
        "CONVERGED": 1,
        "TERMINATED_MAX_ROUNDS": 5,
    }
    assert facts["signal_cooccurrence"] == [
        {"signals": ["S1", "S2", "S6"], "episodes": 6},
        {"signals": ["S1", "S2", "S6", "S7"], "episodes": 5},
        {"signals": ["S1", "S6"], "episodes": 2},
        {"signals": ["S6"], "episodes": 1},
    ]
    assert [row["case_id"] for row in facts["case_qa"]] == facts["case_ids"]
    assert [row["questions"] for row in facts["case_qa"]] == [
        12,
        26,
        5,
        28,
        32,
        6,
        5,
        67,
        54,
        15,
        5,
        0,
    ]
    assert [row["status"] for row in facts["case_qa"]] == [
        "HAS_COMPLETE_EPISODE",
        "HAS_COMPLETE_EPISODE",
        "HAS_COMPLETE_EPISODE",
        "HAS_COMPLETE_EPISODE",
        "HAS_COMPLETE_EPISODE",
        "HAS_COMPLETE_EPISODE",
        "HAS_COMPLETE_EPISODE",
        "HAS_COMPLETE_EPISODE",
        "HAS_COMPLETE_EPISODE",
        "INCOMPLETE_EPISODE_ONLY",
        "INCOMPLETE_EPISODE_ONLY",
        "NO_EPISODE",
    ]
    assert facts["unselected_case_ids"] == ["04", "09", "10", "11", "13", "14", "16", "17", "19"]
    assert facts["unsupported_cuts"] == {
        "answer_confidence_distribution": "NOT_AVAILABLE_IN_TRACKED_AGGREGATE",
        "answer_evidence_length_distribution": "NOT_AVAILABLE_IN_TRACKED_AGGREGATE",
        "first_low_confidence_round": "NOT_AVAILABLE_IN_TRACKED_AGGREGATE",
    }
    by_case = {row["case_id"]: row for row in facts["case_qa"]}
    assert by_case["08"]["episode_classes"] == ["STRONG_ALERT", "WEAK_ALERT"]
    assert by_case["08"]["rounds"] == [2, 2]
    assert by_case["05"]["rounds"] == [10, 4]
    assert by_case["05"]["episode_classes"] == ["STRONG_ALERT", "STRONG_ALERT"]
    assert by_case["18"]["episode_classes"] == ["EXCLUDED"]
    assert by_case["18"]["strong_alerts"] is None
    assert by_case["18"]["detector_evaluation_status"] == "EXCLUDED_NOT_EVALUATED"
    assert by_case["21"]["episode_classes"] == ["NO_EPISODE"]
    assert by_case["21"]["weak_alerts"] is None
    assert by_case["21"]["detector_evaluation_status"] == "NO_EPISODE_NOT_APPLICABLE"


def test_bilingual_reports_have_four_pages_and_matching_fact_ids() -> None:
    facts = load_evidence(ROOT)
    english = build_html("en", facts)
    hebrew = build_html("he", facts)

    assert '<html lang="en" dir="ltr">' in english
    assert '<html lang="he" dir="rtl">' in hebrew
    assert english.count('<section class="page ') == 4
    assert hebrew.count('<section class="page ') == 4

    required_fact_ids = {
        "scope-airtravel",
        "ladder-archival",
        "ladder-engineering",
        "ladder-prospective",
        "ladder-human",
        "completion-on",
        "completion-off",
        "cost-total",
        "cost-per-output",
        "time-total",
        "time-per-output",
        "detector-distribution",
        "agent4-status",
        "human-next-step",
        "uncertainty-boundary",
        "trigger-location",
        "round-distribution",
        "signal-cooccurrence",
        "case-qa-volume",
        "unsupported-cuts",
    }
    for fact_id in required_fact_ids:
        marker = f'data-fact-id="{fact_id}"'
        assert marker in english
        assert marker in hebrew


def test_report_preserves_evidence_classes_and_claim_boundary() -> None:
    facts = load_evidence(ROOT)
    english = build_html("en", facts)
    hebrew = build_html("he", facts)
    joined = english + "\n" + hebrew

    for required in (
        "ARCHIVAL-RETROSPECTIVE DESCRIPTIVE EVIDENCE",
        "ENGINEERING_FIXTURE_NOT_SCIENTIFIC",
        "ENGINEERING-ONLY FIXTURE",
        "DESCRIPTIVE_INSTRUMENT_ROBUSTNESS_ON_ONE_ACCEPTED_RUN",
        "PROSPECTIVE EMPIRICAL EVIDENCE",
        "NOT_MEASURED",
        "STOPPED_AT_CAP",
        "NOT_PRODUCED",
        "NOT COMPARABLE AS QUALITY",
        "Detector-v1",
    ):
        assert required in joined

    assert "Alert = a candidate for human review in the report" in english
    assert "התראה = מועמד לבדיקה אנושית בדוח" in hebrew
    assert "current pack = 2 raters; supervisor freeze = 3" in english
    assert "חבילת הריצה דורשת 2 מעריכים; מסמך המנחים דורש 3" in hebrew
    assert "VEGO-AI is better" not in english
    assert "VEGO-AI טובה יותר" not in hebrew
    assert "proved accuracy" not in english.lower()
    assert "הוכחה לדיוק" not in hebrew
    for forbidden in (
        "PROSPECTIVE OPERATIONAL EVIDENCE",
        "PARTIAL_STOPPED_AT_CAP",
        "NOT_EVALUABLE_DUE_TO_CAP",
        "NOT_REACHED_DUE_TO_CAP",
    ):
        assert forbidden not in joined

    assert "LLM-generated" in english
    assert "שנוצר בידי LLM" in hebrew
    assert "PROVIDER_DEFAULT_NOT_SENT" in joined
    assert "a second run may differ" in english
    assert "ריצה נוספת עשויה להיות שונה" in hebrew
    assert "3 inputs overlap Study 1" in english
    assert "no outputs reused or pooled" in english
    assert "3 קלטים חופפים למחקר 1" in hebrew
    assert "לא נעשה שימוש חוזר או איגום של פלטים" in hebrew
    assert "2 shared setting-level requests" in english
    assert "2 בקשות משותפות ברמת התנאי" in hebrew
    assert "No objective known/unknown field is recorded" in english
    assert "לא נרשם שדה אובייקטיבי של ידוע/לא־ידוע" in hebrew
    assert "model self-report" in english
    assert "דיווח עצמי של המודל" in hebrew
    assert "not correctness" in english
    assert "לא נכונות" in hebrew
    assert "POST_EPISODE_TERMINATION_REPORTING" in joined
    assert "NOT_AVAILABLE_IN_TRACKED_AGGREGATE" in joined


def test_every_quantitative_visual_prints_its_evidence_contract_visibly() -> None:
    facts = load_evidence(ROOT)
    for language in ("en", "he"):
        html = build_html(language, facts)
        for chart_id in (
            "chart-completion",
            "chart-cost",
            "chart-time",
            "chart-detector",
            "chart-rounds",
            "chart-signal-cooccurrence",
            "chart-case-qa",
        ):
            start = html.index(f'id="{chart_id}"')
            end = html.index("</figure>", start)
            block = html[start:end]
            assert 'class="chart-caption"' in block
            for key in (
                "source_label",
                "condition_label",
                "denominator_label",
                "class_label",
                "metric_label",
                "limitation_label",
            ):
                assert f">{_translations(language)[key]}:" in block


def test_agent4_and_engineering_evidence_are_not_conflated() -> None:
    facts = load_evidence(ROOT)
    english = build_html("en", facts)

    assert "0 Agent-4-labelled requests" in english
    assert "EXECUTED_THEN_BLOCKED" in english
    assert "queue NOT_AVAILABLE" in english
    assert "9/9 rule modes" in english
    assert "500/500 seeded permutations" in english
    assert english.index("ENGINEERING-ONLY FIXTURE") < english.index(
        "DESCRIPTIVE_INSTRUMENT_ROBUSTNESS_ON_ONE_ACCEPTED_RUN"
    )


def test_source_hash_or_primary_value_drift_fails_closed(tmp_path: Path) -> None:
    evidence_dir = (
        ROOT
        / "docs"
        / "research"
        / "phd-proposal"
        / "study2-prospective"
        / "evidence"
        / "S2P-LIVE-20260908T192135Z"
    )
    altered = json.loads((evidence_dir / "analysis.json").read_text(encoding="utf-8"))
    altered["conditions"]["VEGO_AI_ON"]["completed"] = 12
    altered_path = tmp_path / "analysis.json"
    altered_path.write_text(json.dumps(altered), encoding="utf-8")

    with pytest.raises(EvidenceError, match="SHA-256 mismatch"):
        load_evidence(ROOT, analysis_path=altered_path)


def test_reports_do_not_expose_private_material() -> None:
    facts = load_evidence(ROOT)
    joined = build_html("en", facts) + build_html("he", facts)

    forbidden = (
        "external_data/",
        "external_data\\",
        "C:\\Users\\",
        "OPENAI_API_KEY",
        "sk-",
        "raw prompt",
        "raw answer",
    )
    assert not any(token in joined for token in forbidden)


def test_bilingual_render_sources_are_deterministic_and_fully_resolved() -> None:
    facts = load_evidence(ROOT)

    for language in ("en", "he"):
        first = build_html(language, facts)
        second = build_html(language, facts)

        assert first == second
        assert "{{" not in first
        assert "}}" not in first
        assert "${" not in first
        assert all(line == line.rstrip() for line in first.splitlines())


def test_compact_rtl_flow_uses_non_mirroring_css_arrowheads() -> None:
    hebrew = build_html("he", load_evidence(ROOT))

    assert '.mini-arrow::before { content:"";' in hebrew
    assert '[dir="rtl"] .mini-arrow::before' in hebrew
    assert 'content:"‹"' not in hebrew


def test_hebrew_robustness_and_route_labels_are_unambiguous() -> None:
    hebrew = build_html("he", load_evidence(ROOT))

    assert "3/3 שינויי סדר מוגדרים" in hebrew
    assert "סוכן 3 שואל · סוכן 1 משיב = 64 Q · סוכן 2 משיב = 191 Q" in hebrew
    assert "סידורים שמיים" not in hebrew
    assert "סוכן שואל 3" not in hebrew


def test_pdf_metadata_normalization_removes_volatile_render_timestamps(tmp_path: Path) -> None:
    first = tmp_path / "first.pdf"
    second = tmp_path / "second.pdf"
    template = b"%PDF /CreationDate ({created}) /ModDate ({modified}) %%EOF"
    first.write_bytes(
        template.replace(b"{created}", b"D:20260908214232+00'00'").replace(
            b"{modified}", b"D:20260908214232+00'00'"
        )
    )
    second.write_bytes(
        template.replace(b"{created}", b"D:20260908214509+00'00'").replace(
            b"{modified}", b"D:20260908214509+00'00'"
        )
    )

    normalize_pdf_metadata(first)
    normalize_pdf_metadata(second)

    assert first.read_bytes() == second.read_bytes()
    assert first.read_bytes().count(PDF_FIXED_TIMESTAMP) == 2
