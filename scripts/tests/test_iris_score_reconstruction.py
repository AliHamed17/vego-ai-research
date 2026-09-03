"""Tests for the read-only Agent-C/C2 reconstruction audit."""

from __future__ import annotations

import hashlib
import pathlib
import sys
import zipfile

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

import iris_score_reconstruction as recon  # noqa: E402


def test_reconstruct_case_score_uses_guideline_and_fragment_contributions() -> None:
    case = {
        "total_score": 1.5,
        "compliance_contributions": [
            {"guideline_id": "G1", "score": 1.0},
        ],
        "fragment_contributions": [
            {"fragment": "x", "total_contribution": 0.5},
        ],
    }
    result = recon.reconstruct_case_score(case)
    assert result == {"stored_total": 1.5, "reconstructed_total": 1.5, "signed_delta": 0.0}


def test_correction_classifier_is_conservative() -> None:
    assert recon.classify_correction("Satisfied") == ("A", "Satisfied")
    assert recon.classify_correction("Partialy Satisfied") == ("B", "Partially-Satisfied")
    assert recon.classify_correction("should be satisfied") == ("C", None)
    assert recon.classify_correction("") == ("D", None)


@pytest.mark.skipif(
    not (ROOT / "VEGO-AI" / "analysis" / "scores_cd_ch.xlsx").exists(),
    reason="local C2 workbooks are not available",
)
def test_local_c2_package_is_hash_bound_and_counts_120_rejections() -> None:
    report = recon.audit_external_c2(ROOT / "VEGO-AI" / "analysis")
    assert report["status"] == "FOUND"
    assert report["total_judgments"] == 915
    assert report["rejected_rows"] == 120
    assert set(report["workbooks"]) == {"cd_ch", "cd_pw", "ucd_ch", "ucd_pw"}
    assert all(len(item["sha256"]) == 64 for item in report["workbooks"].values())
    bridge = recon.bridge_external_rows(report, ROOT / "VEGO-AI")
    assert bridge["status"] == "FOUND"
    assert bridge["matched_rows"] == 120
    assert all(len(row["agent_c_json_sha256"]) == 64 for row in bridge["rows_detail"])


def test_xlsx_reader_rejects_hash_drift(tmp_path: pathlib.Path) -> None:
    path = tmp_path / "scores.xlsx"
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr(
            "xl/workbook.xml",
            '<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"><sheets><sheet name="compliance_vectors" sheetId="1" r:id="rId1" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"/></sheets></workbook>',
        )
        archive.writestr(
            "xl/sharedStrings.xml",
            '<sst xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"><si><t>Name</t></si><si><t>Score</t></si></sst>',
        )
        archive.writestr(
            "xl/worksheets/sheet1.xml",
            '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"><sheetData><row r="1"><c r="A1" t="s"><v>0</v></c><c r="B1" t="s"><v>1</v></c></row><row r="2"><c r="A2"><v>1</v></c><c r="B2"><v>0</v></c></row></sheetData></worksheet>',
        )
    original = recon.sha256_file(path)
    path.write_bytes(path.read_bytes() + b"drift")
    with pytest.raises(recon.ReconstructionError, match="hash"):
        recon.read_xlsx_rows(path, expected_sha256=original)


@pytest.mark.skipif(
    not (ROOT / "VEGO-AI" / "eval_output" / "cd_ch" / "agentC_case_68064.json").exists(),
    reason="local frozen Agent-C artifacts are not available",
)
def test_agent_c_reconstruction_is_repeatable_and_read_only() -> None:
    source = ROOT / "VEGO-AI" / "eval_output" / "cd_ch" / "agentC_case_68064.json"
    before = hashlib.sha256(source.read_bytes()).hexdigest()
    first = recon.audit_agent_c(ROOT / "VEGO-AI")
    second = recon.audit_agent_c(ROOT / "VEGO-AI")
    assert first == second
    assert hashlib.sha256(source.read_bytes()).hexdigest() == before
    assert first["exact_matches"] == 27
    assert first["mismatches"] == 138
