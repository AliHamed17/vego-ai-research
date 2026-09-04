from __future__ import annotations

import importlib.util
import json
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location("audit_v31", ROOT / "scripts" / "audit_historical_case_recovery_v3_1.py")
assert SPEC and SPEC.loader
MOD = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MOD)


def test_duplicate_excess_terminology_and_length_categories() -> None:
    result = {"duplicate_id_groups": {
        "cd_pw": [{"case_id": "70248", "row_count": 2, "logged_lengths": [3822, 3822]}],
        "ucd_pw": [{"case_id": "70248", "row_count": 2, "logged_lengths": [2719, 2719]}],
        "cd_ch": [{"case_id": "x", "row_count": 2, "logged_lengths": [1, 2]}],
    }}
    corrected = MOD._duplicate_correction(result)
    assert corrected["total_duplicate_id_excess_rows"] == 3
    assert corrected["totals"] == {"same_length_excess": 2, "differing_length_excess": 1}
    assert "duplicate_version_rows" not in json.dumps(corrected)


def test_airtravel_verifier_fails_closed_when_archive_unavailable(tmp_path: Path) -> None:
    result = MOD.verify_airtravel_archive(tmp_path / "missing.zip", tmp_path / "missing.json")
    assert result["status"] == "BLOCKED"
    assert result["provider_call_made"] is False


def test_runtime_measurement_is_separate_from_scientific_admissibility(tmp_path: Path) -> None:
    archive = tmp_path / "backup.zip"
    with zipfile.ZipFile(archive, "w") as zf:
        zf.writestr("VEGO-AI/System/models/UCD_PW_models/1.txt", "@startuml\n@enduml\n")
    measured = MOD._executability(archive)
    row = measured["ucd_pw"]
    assert row["decode_read_status"] == "PASS"
    assert row["plantuml_wrapper_status"] == "PASS"
    assert row["offline_input_loader_acceptance"] in {"PASS", "PARTIAL"}
    assert row["syntactic_validation_status"] == "NOT_INVOKED"
    assert row["scientific_admissibility"] == "NO"
