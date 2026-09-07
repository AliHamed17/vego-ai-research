from __future__ import annotations

import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]

import build_study1_transparency_package as transparency  # noqa: E402


def test_public_provenance_is_source_bound_and_sha_mismatch_fails_closed():
    record = transparency.build_provenance_record(
        reviewed_head_sha="6d7f9dcef6c033c98dc1717e973a0714034aea82",
        main_sha="158714064a2ecc40f5eda8561240978ebfe1b371",
        airtravel_archive_sha256=transparency.AIRTRAVEL_ARCHIVE_SHA256,
        airtravel_file_count=143,
        airtravel_matched_count=143,
    )
    assert record["dataset"]["classification"] == "PUBLIC_EXTERNAL"
    assert record["dataset"]["is_student_or_historical_vego_data"] is False
    assert record["dataset"]["airtravel_source_verification"]["status"] == "PASS"
    assert record["dataset"]["airtravel_source_verification"]["matched_count"] == 143
    assert transparency.validate_provenance_record(record) == []
    with pytest.raises(transparency.TransparencyValidationError):
        transparency.verify_archive_sha256("0" * 64)
    with pytest.raises(transparency.TransparencyValidationError, match="release archive is unavailable"):
        transparency.verify_official_release_archive(Path("missing-vego-release.zip"))


def test_artifact_matrix_distinguishes_source_presence_from_runtime_artifact():
    rows = {row["artifact"]: row for row in transparency.log_contract_matrix()}
    assert rows["interaction_log.json"]["exists_in_official_v2_1_5_3_source"] is True
    assert rows["interaction_log.json"]["exists_in_reviewed_run_worktree"] == (
        "NOT_AVAILABLE_IN_WORKTREE"
    )
    assert rows["user_actions.log"]["used_for_detector_v1"] is False
    assert rows["user_actions.log"]["q_and_a_source_of_truth"] is False
    assert rows["qa_events.jsonl"]["used_for_detector_v1"] is True


def test_detector_criteria_are_traceable_to_canonical_code_only():
    source = (ROOT / "scripts" / "extract_qa_escalation_features.py").read_text(encoding="utf-8")
    rows = transparency.detector_criteria()
    assert {row["signal"] for row in rows} == {"S1", "S2", "S3", "S6", "S7"}
    assert transparency.validate_detector_criteria(rows, source) == []
    for row in rows:
        assert row["observed_in_accepted_evidence"] == "NOT_AVAILABLE_IN_WORKTREE"
        assert row["unit"] == "Q&A episode"
    tampered = [dict(rows[0], exact_code_rule="event.get('made_up') == True")]
    assert transparency.validate_detector_criteria(tampered, source)


def test_missing_evidence_never_turns_s3_into_observed_zero():
    metrics = transparency.safe_metrics(None)
    assert metrics["evidence_status"] == "NOT_AVAILABLE_IN_WORKTREE"
    assert metrics["scientific_denominator"] == "NOT_AVAILABLE_IN_WORKTREE"
    assert metrics["detector_signals"]["S3"]["observed_count"] == "NOT_AVAILABLE_IN_WORKTREE"
    assert metrics["detector_signals"]["S3"]["observed"] is False
    assert not any(isinstance(v, (int, float)) and not isinstance(v, bool) for v in metrics.values())


def test_mechanisms_and_queue_are_separate():
    mechanisms = transparency.mechanism_boundaries()
    assert mechanisms["detector_v1"]["unit"] == "Q&A episode"
    assert mechanisms["detector_v1"]["writes_queue"] is False
    assert mechanisms["selective_intervention_agent4"]["unit"] == "Agent-4 variability classification"
    assert mechanisms["selective_intervention_agent4"]["queue_status"] == "NOT_AVAILABLE"
    assert mechanisms["selective_intervention_agent4"]["queue_artifact"] == "human_review_queue.jsonl"


def test_context_and_mapping_outputs_are_not_detector_triggers():
    dictionary = transparency.transparency_data_dictionary(
        reviewed_head_sha="6d7f9dcef6c033c98dc1717e973a0714034aea82",
        main_sha="158714064a2ecc40f5eda8561240978ebfe1b371",
    )
    by_code = {entry["english_code_name"]: entry for entry in dictionary["canonical_signal_entries"]}
    for code in ("C1_MAPPING_CERTAINTY", "C2_AGENT4_CLASSIFICATION_CONFIDENCE", "C3_AGENT4_REVIEW_FLAGS"):
        assert by_code[code]["direct_detector_v1_trigger"] is False
    for code in ("MAPPING_ALTERNATIVE", "MAPPING_NON_SATISFIED", "SOURCE_TARGET_ALIGNMENT"):
        assert by_code[code]["direct_detector_v1_trigger"] is False


def test_example_cards_are_engineering_only_and_not_metrics():
    cards = transparency.example_cards()
    assert len(cards) == 3
    for card in cards:
        assert card["evidence_class"] == "ENGINEERING_ILLUSTRATION_ONLY"
        assert "המחשה הנדסית בלבד" in card["banner_he"]
        assert card["enters_scientific_metrics"] is False
    assert cards[1]["detector_result"] == "STRONG_ALERT (illustrative rule application only)"
    assert cards[2]["mechanism"] == "Selective Intervention Policy / Agent-4"


def test_generated_hebrew_document_is_rtl_and_has_no_template_tokens(tmp_path):
    out = tmp_path / "note.he.md"
    transparency.write_hebrew_note(out, transparency.build_provenance_record(
        reviewed_head_sha="6d7f9dcef6c033c98dc1717e973a0714034aea82",
        main_sha="158714064a2ecc40f5eda8561240978ebfe1b371",
        airtravel_archive_sha256=transparency.AIRTRAVEL_ARCHIVE_SHA256,
        airtravel_file_count=143,
        airtravel_matched_count=143,
    ), transparency.safe_metrics(None))
    text = out.read_text(encoding="utf-8")
    assert text.startswith('<div dir="rtl">')
    assert "{{" not in text and "TODO" not in text and "TBD" not in text
    assert "STRONG_ALERT = S1 OR S3 OR S7" in text
    assert "NOT_AVAILABLE_IN_WORKTREE" in text


def test_package_outputs_are_safe_and_schema_like(tmp_path):
    paths = transparency.write_package(
        tmp_path,
        reviewed_head_sha="6d7f9dcef6c033c98dc1717e973a0714034aea82",
        main_sha="158714064a2ecc40f5eda8561240978ebfe1b371",
    )
    assert {p.name for p in paths.values()} >= {
        "study1-data-provenance-v1.json",
        "study1-log-contract-matrix-v1.csv",
        "detector-v1-criteria-to-log-fields-v1.csv",
        "study1-transparency-metrics-v1.json",
        "study1-transparency-data-dictionary-v1.json",
        "study1-transparency-figures-manifest-v1.json",
    }
    serialized = "\n".join(p.read_text(encoding="utf-8") for p in paths.values() if p.suffix in {".json", ".md", ".csv"})
    credential_marker = "OPENAI" + "_API_KEY"
    assert credential_marker not in serialized
    assert "C:\\Users\\" not in serialized
    metrics = json.loads(paths["metrics"].read_text(encoding="utf-8"))
    assert metrics["evidence_status"] == "NOT_AVAILABLE_IN_WORKTREE"
    assert metrics["tables"]["episodes"]["rows"] == []
    provenance = json.loads(paths["provenance"].read_text(encoding="utf-8"))
    assert provenance["dataset"]["airtravel_source_verification"]["status"] == "NOT_AVAILABLE_IN_WORKTREE"
    assert provenance["official_vego_release"]["archive_verification"] == "NOT_AVAILABLE_IN_WORKTREE"
    dictionary = json.loads(paths["data_dictionary"].read_text(encoding="utf-8"))
    assert dictionary["layers"]["communication_process_signals"] == ["S1", "S2", "S3", "S6", "S7"]
    assert dictionary["mechanisms"]["detector_v1"]["writes_queue"] is False
    assert dictionary["mechanisms"]["selective_intervention_agent4"]["queue_status"] == "NOT_AVAILABLE"
    figures = json.loads(paths["figures_manifest"].read_text(encoding="utf-8"))
    assert figures["status"] == "SAFE_RULE_VISUALS_ONLY"
    assert len(figures["figures"]) == 3
    assert all(item["evidence_class"] == "ENGINEERING_ILLUSTRATION_ONLY" for item in figures["figures"])


def test_dictionary_has_clean_checkout_fallback(monkeypatch, tmp_path):
    monkeypatch.setattr(transparency, "ROOT", tmp_path)
    dictionary = transparency.transparency_data_dictionary(
        reviewed_head_sha="6d7f9dcef6c033c98dc1717e973a0714034aea82",
        main_sha="158714064a2ecc40f5eda8561240978ebfe1b371",
    )
    assert dictionary["canonical_signal_entries"]
    assert {row["signal"] for row in transparency.detector_criteria()} == {"S1", "S2", "S3", "S6", "S7"}


def test_package_rejects_unverified_manual_airtravel_counts_or_hash(tmp_path):
    with pytest.raises(transparency.TransparencyValidationError, match="actual pinned archive"):
        transparency.write_package(
            tmp_path,
            reviewed_head_sha="6d7f9dcef6c033c98dc1717e973a0714034aea82",
            main_sha="158714064a2ecc40f5eda8561240978ebfe1b371",
            airtravel_archive_sha256=transparency.AIRTRAVEL_ARCHIVE_SHA256,
            airtravel_file_count=143,
            airtravel_matched_count=143,
        )
