from __future__ import annotations

import json
import zipfile
from pathlib import Path

from scripts.audit_historical_slots import audit, write_outputs


def _fixture(tmp_path: Path) -> tuple[Path, Path]:
    repo = tmp_path / "repo"
    model_root = repo / "VEGO-AI" / "models"
    for directory, name in [
        ("UCD_PW_models", "10_UCD_PW.txt"),
        ("CD_PW_models", "20_CD_PW.txt"),
        ("UCD_Ch_models", "30_UCD_Ch.txt"),
        ("CD_Ch_models", "40_CD_Ch.txt"),
    ]:
        path = model_root / directory
        path.mkdir(parents=True, exist_ok=True)
        (path / name).write_text("@startuml\nA --> B\n@enduml\n", encoding="utf-8")
    archive = tmp_path / "archive.zip"
    with zipfile.ZipFile(archive, "w") as zf:
        for path in model_root.rglob("*"):
            if path.is_file():
                zf.write(path, path.relative_to(repo).as_posix())
    return repo, archive


def test_counts_do_not_assign_discovered_files_to_paper_slots(tmp_path: Path) -> None:
    repo, archive = _fixture(tmp_path)
    result = audit(repo, archive, synthetic_branch="missing/branch")
    assert result["aggregate"]["authoritative_expected_slots"] == 178
    assert result["aggregate"]["discovered_files"] == 4
    assert result["aggregate"]["recovery_candidate_unverified"] == 4
    assert result["aggregate"]["not_yet_searched"] == 178
    assert result["aggregate"]["synthesis_eligible"] == 0
    assert all(row["expected_case_slot"] is None for row in result["discovered_file_records"])
    assert all(row["provenance_status"] == "NOT_YET_SEARCHED" for row in result["expected_slot_records"])


def test_synthetic_branch_is_quarantined_without_content_inspection(tmp_path: Path) -> None:
    repo, archive = _fixture(tmp_path)
    synthetic = tmp_path / "synthetic"
    (synthetic / "Dataset1_ModelEval_SYNTHETIC").mkdir(parents=True)
    (synthetic / "Dataset1_ModelEval_SYNTHETIC" / "case.txt").write_text("synthetic", encoding="utf-8")
    # Use a temporary git repository/worktree-independent path by directly
    # checking that the output contract remains fail-closed when no branch is
    # resolvable; no synthetic file is ingested from arbitrary paths.
    result = audit(repo, archive, synthetic_branch="missing/branch")
    assert result["synthetic_quarantine"]["record_count"] == 0
    assert result["synthetic_quarantine"]["raw_content_inspected"] is False


def test_outputs_are_parseable_and_explicitly_not_search_closed(tmp_path: Path) -> None:
    repo, archive = _fixture(tmp_path)
    out = tmp_path / "out"
    write_outputs(repo, archive, out, synthetic_branch="missing/branch")
    scope = json.loads((out / "recovery-scope-report.json").read_text(encoding="utf-8"))
    assert scope["search_closed"] is False
    assert scope["synthesis_eligible_count"] == 0
