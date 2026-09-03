"""Tests for the read-only Iris preliminary-pilot evidence verifier."""

from __future__ import annotations

import json
import os
import pathlib
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

import verify_iris_preliminary_pilot as verifier  # noqa: E402

VEGO = pathlib.Path(os.environ.get("VEGO_AI_ROOT", str(ROOT / "VEGO-AI")))


def test_canonical_content_comparison_handles_checkout_line_endings() -> None:
    assert verifier.canonical_content_equal(b'{\r\n  "value": 1\r\n}\r\n', b'{\n"value": 1\n}\n')
    assert verifier.canonical_content_digest(
        b'{\r\n  "value": 1\r\n}\r\n'
    ) == verifier.canonical_content_digest(b'{\n"value": 1\n}\n')
    assert verifier.canonical_content_equal(b"a,b\r\n1,2\r\n", b"a,b\n1,2\n")
    assert not verifier.canonical_content_equal(b'{"value": 1}', b'{"value": 2}')


def test_read_csv_counts_only_nonblank_human_labels(tmp_path: pathlib.Path) -> None:
    path = tmp_path / "labels.csv"
    path.write_text(
        "expert_label,reviewer_2_label,adjudicated_label\n"
        ",,\n"
        "Occasional Variability,,\n"
        ",Substantial Variability,\n"
        ",,Undetermined / Needs Review\n",
        encoding="utf-8",
    )
    assert verifier.count_nonblank_csv_fields(path, verifier.EXP005_LABEL_FIELDS) == {
        "expert_label": 1,
        "reviewer_2_label": 1,
        "adjudicated_label": 1,
    }


@pytest.mark.skipif(
    not (VEGO / "eval_output" / "ucd_ch" / "agentC_all_scores.json").exists(),
    reason="local frozen VEGO-AI baseline artifacts are not available",
)
def test_local_frozen_evidence_audit_is_fail_closed_and_expected() -> None:
    report = verifier.audit(ROOT, VEGO)

    assert report["status"] == "TECHNICAL EVIDENCE AUDIT: PASS"
    assert report["scientific_pilot_status"] == "SCIENTIFIC PILOT EXECUTION: NOT YET AUTHORIZED"
    assert report["claim_boundary"] == "descriptive_mechanism_evidence_only"
    assert report["baseline_integrity"]["official_tag"] == "official-vego-ai-baseline"
    assert report["baseline_integrity"]["checked_files"] == 250
    assert report["baseline_integrity"]["content_equivalent_files"] == 250

    counts = report["frozen_run_counts"]
    assert counts["ranked_rows"] == 179
    assert counts["per_case_reports"] == 165
    assert counts["duplicate_ranked_rows"] == 14
    assert counts["distinct_case_ids"] == 83
    assert counts["variability_patterns"] == 27

    truth = report["agent4_ground_truth_check"]
    assert truth["byte_identical_pairs"] == 4
    assert truth["patterns_covered"] == 27
    assert truth["independent_ground_truth"] is False

    gate = report["exp005_gate"]
    assert gate["rows"] == 27
    assert gate["generalization_safe_candidates"] == 24
    assert gate["reviewer_1_labels"] == 0
    assert gate["reviewer_2_labels"] == 0
    assert gate["adjudicated_labels"] == 0
    assert gate["holdout_status"] == "sealed_not_evaluated"

    assert report["trigger_inventory"]["Alternative"]["count"] == 491
    assert report["trigger_inventory"]["Domain Mistake"]["count"] == 79
    assert report["trigger_inventory"]["Language Mistake"]["count"] == 37
    assert report["trigger_inventory"]["Not-Satisfied"]["count"] == 496
    assert report["trigger_inventory"]["Partially-Satisfied"]["count"] == 743
    assert report["trigger_inventory"]["open question"]["count"] == 12
    assert report["trigger_inventory"]["low/medium confidence"]["count"] == 3

    candidates = report["pilot_candidates"]
    assert candidates["C1"]["status"] == "FOUND"
    assert candidates["C2"]["status"] == "LOCAL_EXTERNAL_FOUND_PUBLIC_NOT_TRACKED"
    assert candidates["C3"]["status"] == "FOUND"
    assert candidates["C3"]["path"].startswith("VEGO-AI/eval_output/")
    assert len(candidates["C3"]["source_sha256"]) == 64
    assert candidates["C4"]["review_id"] == "HRQ-cd_ch-P2"


def test_cli_json_shape(
    capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(
        verifier,
        "audit",
        lambda repo, vego: {"status": "TECHNICAL EVIDENCE AUDIT: PASS", "read_only": True, "repository": str(repo)},
    )
    assert verifier.main(["--repo-root", str(ROOT), "--vego-root", str(ROOT / "VEGO-AI")]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["status"] == "TECHNICAL EVIDENCE AUDIT: PASS"
    assert payload["read_only"] is True
