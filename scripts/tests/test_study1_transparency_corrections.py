from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

import build_study1_signal_traceability as traceability  # noqa: E402
import build_study1_transparency_package as transparency  # noqa: E402
from study1_case_selection import select_airtravel_cases  # noqa: E402


def test_inventory_selection_is_fail_closed_when_21_candidates_cannot_identify_four(tmp_path):
    inventory = json.loads(
        (ROOT / "docs/research/phd-proposal/text2uml-airtravel/airtravel-inventory.json").read_text(
            encoding="utf-8"
        )
    )
    result = select_airtravel_cases(inventory)
    assert result["status"] == "PURPOSIVE_NON_REPRODUCIBLE"
    assert result["eligible_case_count"] == 21
    assert result["predicate"]
    assert result["selected_case_hashes"] == [
        "240b034834e383b9844e9a3e9796f6be9b3d47fc95de6606ed022d278d751f91",
        "08399ca9432c1399f3f9784d34741314e4d39e40307a6efb14fa92a1c138b1d6",
        "ee4d689d59c9ce3a5e8ff385747641954bd4821f2efeb18e581dcd1d5441d20a",
        "1c3d15eac71fcaab138857dbbc7153833b3df55ab57925ac756a79dc28dc847a",
    ]
    assert "21 eligible" in result["reason"]


def test_inventory_selection_can_be_deterministic_only_with_explicit_case_metadata():
    payload = {
        "cases": [
            {"case_hash": f"{index:064x}", "eligible": index <= 4, "selection_rank": index}
            for index in range(1, 6)
        ]
    }
    result = select_airtravel_cases(payload)
    assert result["status"] == "DETERMINISTIC_PREDICATE"
    assert result["selected_case_hashes"] == [f"{index:064x}" for index in range(1, 5)]


def test_agent4_causal_path_records_execution_review_creation_and_legacy_enum_failure():
    path = transparency.agent4_causal_path()
    assert path["status"] == "EXECUTED_THEN_BLOCKED"
    assert path["review_record_created"] is True
    assert path["review_record_count"] == "AT_LEAST_ONE"
    assert path["queue_status"] == "NOT_AVAILABLE"
    assert path["failure_reason"] == "cd_airtravel absent from legacy schema enum"
    assert path["evidence_class"] == "DOCUMENTED_RUNTIME_PATH"
    assert "not triggered" not in json.dumps(path).lower()


def test_case_model_availability_is_explicit_and_does_not_infer_from_model_config():
    availability = transparency.case_model_availability()
    ep81 = next(value for key, value in availability.items() if key.startswith("EP-81b2c98"))
    assert ep81["model_availability"] == "UNAVAILABLE"
    assert ep81["evidence_status"] == "NOT_AVAILABLE_IN_WORKTREE"
    ep577 = next(value for key, value in availability.items() if key.startswith("EP-577319bf"))
    assert ep577["model_availability"] == "UNAVAILABLE"


def test_reporting_code_sha_is_non_evidentiary_metadata():
    metadata = transparency.reporting_code_metadata()
    assert metadata["status"] == "NON_EVIDENTIARY_DOCUMENTATION_METADATA"
    assert metadata["used_for_scientific_binding"] is False
    assert metadata["stale_values"] == "STAMPED_SUPERSEDED"


def test_s6_has_one_authoritative_definition_and_one_count_field():
    assert traceability.S6_OPERATIONAL_DEFINITION["signal"] == "S6_MULTIPLE_QA_ROUNDS"
    assert traceability.S6_OPERATIONAL_DEFINITION["rule"] == 'episode.get("round_count", 0) > 1'
    payload = traceability.signal_dictionary()
    s6_entries = [entry for entry in payload["entries"] if entry["english_code_name"].startswith("S6")]
    assert len(s6_entries) == 1
    assert payload["s6_operational_definition"] == traceability.S6_OPERATIONAL_DEFINITION


def test_context_availability_is_explicitly_unavailable_not_archival_numeric_data():
    payload = traceability.signal_dictionary()
    context = {
        entry["english_code_name"]: entry
        for entry in payload["entries"]
        if entry["english_code_name"] in {
            "C1_MAPPING_CERTAINTY",
            "C2_AGENT4_CLASSIFICATION_CONFIDENCE",
            "C3_AGENT4_REVIEW_FLAGS",
        }
    }
    assert set(context) == {
        "C1_MAPPING_CERTAINTY",
        "C2_AGENT4_CLASSIFICATION_CONFIDENCE",
        "C3_AGENT4_REVIEW_FLAGS",
    }
    for entry in context.values():
        assert entry["data_status"] == traceability.NOT_AVAILABLE
        assert "DATA_NOT_AVAILABLE_IN_WORKTREE" in entry["evidence_availability"]


def test_worked_example_uses_hash_refs_and_mandated_banner():
    cards = transparency.example_cards()
    worked = next(card for card in cards if card["card_id"] == "EP-577319bf")
    assert worked["evidence_class"] == "ENGINEERING_ILLUSTRATION_ONLY"
    assert worked["banner"] == "ENGINEERING_ILLUSTRATION_ONLY"
    assert worked["raw_content"] == "REDACTED"
    assert worked["case_reference"].startswith("sha256:")
    assert worked["detector_result"] == "STRONG_ALERT (archival classification; illustrative rule application only)"
    assert worked["limitation"]
    assert all(card["banner"] == "ENGINEERING_ILLUSTRATION_ONLY" for card in cards)


def test_package_receipts_expose_selection_and_causal_path_without_private_data(tmp_path):
    paths = transparency.write_package(
        tmp_path,
        reviewed_head_sha="a" * 40,
        main_sha="b" * 40,
    )
    provenance = json.loads(paths["provenance"].read_text(encoding="utf-8"))
    assert provenance["dataset"]["selection_status"] == "PURPOSIVE_NON_REPRODUCIBLE"
    assert provenance["dataset"]["selection"]["eligible_case_count"] == 21
    assert provenance["dataset"]["selection"]["selected_case_hashes"] == [
        "240b034834e383b9844e9a3e9796f6be9b3d47fc95de6606ed022d278d751f91",
        "08399ca9432c1399f3f9784d34741314e4d39e40307a6efb14fa92a1c138b1d6",
        "ee4d689d59c9ce3a5e8ff385747641954bd4821f2efeb18e581dcd1d5441d20a",
        "1c3d15eac71fcaab138857dbbc7153833b3df55ab57925ac756a79dc28dc847a",
    ]
    data_dictionary = json.loads(paths["data_dictionary"].read_text(encoding="utf-8"))
    causal = data_dictionary["agent4_causal_path"]
    assert causal["status"] == "EXECUTED_THEN_BLOCKED"
    assert causal["queue_status"] == "NOT_AVAILABLE"
    assert "legacy schema enum" in causal["failure_reason"]


def test_current_reporting_distinguishes_historical_execution_from_reporting_code():
    distinction = transparency.byte_identity_distinction()
    assert distinction["historical_executed_code"]
    assert distinction["current_reporting_code_status"] == "CHANGED_POST_RUN_FOR_RECEIPT_BINDING"
    assert distinction["byte_identical_to_historical"] is False


def test_supervisor_workflow_runs_root_tests_and_study2_tests():
    workflow = (ROOT / ".github/workflows/supervisor-package.yml").read_text(encoding="utf-8")
    assert "uv run python -m pytest tests -q -p no:cacheprovider" in workflow
    assert "tests/test_study2_on_off.py" in workflow
