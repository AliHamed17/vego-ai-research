from __future__ import annotations

import hashlib
import json
import zipfile
from pathlib import Path

from scripts.audit_historical_case_recovery import build_audit, write_outputs


def _fixture(tmp_path: Path, *, mismatch: bool = False) -> tuple[Path, Path]:
    repo = tmp_path / "repo"
    model_root = repo / "VEGO-AI" / "models"
    for directory, name, text in [
        ("UCD_PW_models", "100_UCD_PW.txt", "@startuml\nA --> B\n@enduml\n"),
        ("CD_PW_models", "200_CD_PW.txt", "@startuml\nclass A\n@enduml\n"),
        ("UCD_Ch_models", "300_UCD_Ch.txt", "@startuml\nC --> D\n@enduml\n"),
        ("CD_Ch_models", "400_CD_Ch.txt", "@startuml\nclass C\n@enduml\n"),
    ]:
        target = model_root / directory
        target.mkdir(parents=True, exist_ok=True)
        (target / name).write_text(text, encoding="utf-8")
    archive = tmp_path / "archive.zip"
    with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for path in model_root.rglob("*"):
            if path.is_file():
                data = path.read_bytes()
                if mismatch and path.name.startswith("300_"):
                    data += b"changed"
                zf.writestr(path.relative_to(repo).as_posix(), data)
    return repo, archive


def test_all_current_case_files_are_recovered_verbatim(tmp_path: Path) -> None:
    repo, archive = _fixture(tmp_path)
    inventory, manifest = build_audit(repo, archive)
    assert inventory["raw_model_inventory"]["total"] == 4
    assert inventory["provenance_counts"]["RECOVERED_VERBATIM"] == 4
    assert inventory["provenance_counts"]["PARTIAL_RECOVERY"] == 0
    assert [row["expected_case_slot"] for row in manifest] == [
        "ucd_pw-0001",
        "cd_pw-0001",
        "ucd_ch-0001",
        "cd_ch-0001",
    ]
    assert all(row["admissibility_pending_claude"] for row in manifest)
    assert all("text" not in row for row in manifest)


def test_byte_mismatch_is_partial_and_fail_closed(tmp_path: Path) -> None:
    repo, archive = _fixture(tmp_path, mismatch=True)
    inventory, manifest = build_audit(repo, archive)
    assert inventory["provenance_counts"]["PARTIAL_RECOVERY"] == 1
    row = next(item for item in manifest if item["historical_setting"] == "ucd_ch")
    assert row["provenance_status"] == "PARTIAL_RECOVERY"
    assert row["source_entry_sha256"] != row["recovered_file_sha256"]


def test_output_is_deterministic_and_hashes_are_stable(tmp_path: Path) -> None:
    repo, archive = _fixture(tmp_path)
    first = write_outputs(repo, tmp_path / "out1", archive)
    second = write_outputs(repo, tmp_path / "out2", archive)
    assert first["manifest_sha256"] == second["manifest_sha256"]
    first_bytes = (tmp_path / "out1" / "provenance-manifest.json").read_bytes()
    second_bytes = (tmp_path / "out2" / "provenance-manifest.json").read_bytes()
    assert hashlib.sha256(first_bytes).hexdigest() == hashlib.sha256(second_bytes).hexdigest()
    parsed = json.loads(first_bytes)
    assert len(parsed) == 4


def test_no_absolute_paths_are_emitted(tmp_path: Path) -> None:
    repo, archive = _fixture(tmp_path)
    _, manifest = build_audit(repo, archive)
    for row in manifest:
        assert not Path(row["source_path"]).is_absolute()
        assert "\\" not in row["source_path"]
