from __future__ import annotations

import json
import zipfile
from pathlib import Path

import find_case_model_inputs as finder


def test_inventory_hashes_candidate_and_inspects_archive_members_only(tmp_path: Path) -> None:
    (tmp_path / "ParkWise-Cases").mkdir()
    model = tmp_path / "ParkWise-Cases" / "case01.txt"
    model.write_text("private fixture", encoding="utf-8")
    archive = tmp_path / "Dataset1_ModelEval.zip"
    with zipfile.ZipFile(archive, "w") as handle:
        handle.writestr("Cheers/Cases/case01.json", "private")
    result = finder.inventory([tmp_path])
    assert result["status"] == "RECOVERED_CANDIDATES"
    assert result["candidate_files"][0]["sha256"] == finder.sha256(model)
    assert result["candidate_archives"][0]["matching_members"][0]["name"] == "Cheers/Cases/case01.json"
    assert result["content_read"] is False


def test_inventory_empty_root_is_not_found(tmp_path: Path) -> None:
    result = finder.inventory([tmp_path])
    assert result["status"] == "NOT_FOUND"
    assert json.dumps(result).find("private fixture") == -1
