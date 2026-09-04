from __future__ import annotations

import hashlib
import json
import zipfile
from pathlib import Path

from scripts.audit_historical_case_recovery import build_audit, write_outputs


def _make_repo(tmp_path: Path, files: dict[str, bytes]) -> Path:
    repo = tmp_path / "repo"
    for relative, data in files.items():
        path = repo / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
    return repo


def _archive(tmp_path: Path, members: dict[str, bytes], *, extra: dict[str, bytes] | None = None) -> Path:
    archive = tmp_path / "archive.zip"
    with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for name, data in {**members, **(extra or {})}.items():
            zf.writestr(name, data)
    return archive


def _model(setting_dir: str, name: str, text: bytes = b"@startuml\nA --> B\n@enduml\n") -> tuple[str, bytes]:
    return f"VEGO-AI/models/{setting_dir}/{name}", text


def test_independent_inventories_and_set_differences(tmp_path: Path) -> None:
    member, data = _model("UCD_PW_models", "100_UCD_PW.txt")
    local_only, local_data = _model("UCD_PW_models", "101_UCD_PW.txt")
    archive_only, archive_data = _model("UCD_PW_models", "102_UCD_PW.txt")
    repo = _make_repo(tmp_path, {member: data, local_only: local_data})
    archive = _archive(tmp_path, {member: data, archive_only: archive_data}, extra={"README.md": b"unrelated"})
    inventory, manifest = build_audit(repo, archive)
    assert inventory["observed_local_count"] == 2
    assert inventory["archive_model_member_count"] == 2
    assert inventory["unrelated_archive_member_count"] == 1
    assert inventory["set_differences"]["archive_intersection_local"] == [member]
    assert inventory["set_differences"]["archive_minus_local"] == [archive_only]
    assert inventory["set_differences"]["local_minus_archive"] == [local_only]
    assert {row["provenance_status"] for row in manifest} == {"RECOVERED_VERBATIM", "LOCAL_ONLY", "ARCHIVE_ONLY"}


def test_nested_archive_member_is_independently_enumerated(tmp_path: Path) -> None:
    member, data = _model("UCD_PW_models", "nested/103_UCD_PW.txt")
    repo = _make_repo(tmp_path, {})
    archive = _archive(tmp_path, {member: data})
    inventory, manifest = build_audit(repo, archive)
    assert inventory["archive_model_member_count"] == 1
    assert inventory["set_differences"]["archive_minus_local"] == [member]
    assert manifest[0]["provenance_status"] == "ARCHIVE_ONLY"


def test_expected_but_absent_is_explicit_when_independent_universe_is_supplied(tmp_path: Path) -> None:
    member, data = _model("UCD_PW_models", "100_UCD_PW.txt")
    repo = _make_repo(tmp_path, {member: data})
    archive = _archive(tmp_path, {member: data})
    expected = {"ucd_pw": [member, "VEGO-AI/models/UCD_PW_models/999_UCD_PW.txt"]}
    inventory, _ = build_audit(repo, archive, expected_universe=expected)
    assert inventory["set_differences"]["expected_minus_recovered"] == [
        "VEGO-AI/models/UCD_PW_models/999_UCD_PW.txt"
    ]
    assert inventory["completeness_verdict"] == "INCOMPLETE_EXPECTED_UNIVERSE"


def test_no_independent_expected_universe_is_not_called_complete(tmp_path: Path) -> None:
    member, data = _model("UCD_PW_models", "100_UCD_PW.txt")
    repo = _make_repo(tmp_path, {member: data})
    archive = _archive(tmp_path, {member: data})
    inventory, _ = build_audit(repo, archive)
    assert inventory["completeness_verdict"] == "COMPLETENESS_UNRESOLVED"
    assert inventory["raw_model_inventory"]["per_setting"]["ucd_pw"]["observed_local_count"] == 1
    assert "expected_count" not in inventory["raw_model_inventory"]["per_setting"]["ucd_pw"]


def test_validation_fail_closed_for_empty_non_utf8_wrapper_and_setting_mismatch(tmp_path: Path) -> None:
    files = {
        "VEGO-AI/models/UCD_PW_models/100_UCD_PW.txt": b"",
        "VEGO-AI/models/UCD_PW_models/101_UCD_PW.txt": b"not uml",
        "VEGO-AI/models/UCD_PW_models/102_UCD_PW.txt": b"\xff\xfe",
        "VEGO-AI/models/CD_PW_models/103_UCD_PW.txt": b"@startuml\nA\n@enduml\n",
    }
    repo = _make_repo(tmp_path, files)
    archive = _archive(tmp_path, files)
    inventory, manifest = build_audit(repo, archive)
    by_name = {Path(row["source_path"]).name: row for row in manifest}
    assert by_name["100_UCD_PW.txt"]["validation_status"] == "EMPTY_MODEL"
    assert by_name["101_UCD_PW.txt"]["validation_status"] == "MISSING_PLANTUML_WRAPPER"
    assert by_name["102_UCD_PW.txt"]["validation_status"] == "NON_UTF8_INPUT"
    assert by_name["103_UCD_PW.txt"]["validation_status"] == "SETTING_DIRECTORY_MISMATCH"
    assert inventory["completeness_verdict"] == "COMPLETENESS_UNRESOLVED"


def test_missing_start_and_end_wrappers_are_distinguished(tmp_path: Path) -> None:
    files = {
        "VEGO-AI/models/UCD_PW_models/100_UCD_PW.txt": b"A\n@enduml\n",
        "VEGO-AI/models/UCD_PW_models/101_UCD_PW.txt": b"@startuml\nA\n",
    }
    repo = _make_repo(tmp_path, files)
    archive = _archive(tmp_path, files)
    _, manifest = build_audit(repo, archive)
    by_name = {Path(row["source_path"]).name: row for row in manifest}
    assert by_name["100_UCD_PW.txt"]["validation_status"] == "MISSING_STARTUML"
    assert by_name["101_UCD_PW.txt"]["validation_status"] == "MISSING_ENDUML"


def test_archive_and_local_superset_cases_are_not_collapsed(tmp_path: Path) -> None:
    first, data = _model("UCD_PW_models", "100_UCD_PW.txt")
    local_more, local_data = _model("UCD_PW_models", "101_UCD_PW.txt")
    archive_more, archive_data = _model("UCD_PW_models", "102_UCD_PW.txt")
    repo = _make_repo(tmp_path, {first: data, local_more: local_data})
    archive = _archive(tmp_path, {first: data, archive_more: archive_data})
    inventory, _ = build_audit(repo, archive)
    assert inventory["set_differences"]["archive_minus_local"] == [archive_more]
    assert inventory["set_differences"]["local_minus_archive"] == [local_more]


def test_byte_mismatch_and_duplicate_case_and_content_are_reported(tmp_path: Path) -> None:
    first, data = _model("UCD_PW_models", "100_UCD_PW.txt")
    second, _ = _model("UCD_PW_models", "100_duplicate_UCD_PW.txt", data)
    mismatch, original = _model("CD_PW_models", "200_CD_PW.txt")
    repo = _make_repo(tmp_path, {first: data, second: data, mismatch: original + b"local"})
    archive = _archive(tmp_path, {first: data, second: data, mismatch: original})
    inventory, manifest = build_audit(repo, archive)
    assert inventory["duplicate_case_ids"] == {"ucd_pw:100": ["ucd_pw:100_UCD_PW.txt", "ucd_pw:100_duplicate_UCD_PW.txt"]}
    assert inventory["duplicate_content_group_count"] == 1
    row = next(item for item in manifest if item["source_path"].endswith("200_CD_PW.txt"))
    assert row["provenance_status"] == "BYTE_MISMATCH"
    assert row["validation_status"] == "VALID"


def test_duplicate_archive_filename_is_reported(tmp_path: Path) -> None:
    member, data = _model("UCD_PW_models", "100_UCD_PW.txt")
    repo = _make_repo(tmp_path, {member: data})
    archive = tmp_path / "duplicate.zip"
    with zipfile.ZipFile(archive, "w") as zf:
        zf.writestr(member, data)
        zf.writestr(member, data)
    inventory, _ = build_audit(repo, archive)
    assert inventory["duplicate_archive_member_names"] == [member]


def test_evaluation_id_differences_are_separate_from_recovered_files(tmp_path: Path) -> None:
    member, data = _model("UCD_PW_models", "100_UCD_PW.txt")
    repo = _make_repo(tmp_path, {member: data})
    eval_dir = repo / "VEGO-AI" / "eval_output" / "ucd_pw"
    eval_dir.mkdir(parents=True)
    (eval_dir / "agentC_case_100.json").write_text("{}", encoding="utf-8")
    (eval_dir / "agentC_case_999.json").write_text("{}", encoding="utf-8")
    archive = _archive(tmp_path, {member: data})
    inventory, _ = build_audit(repo, archive)
    assert inventory["set_differences"]["evaluation_ids_minus_recovered_ids"] == ["ucd_pw:999"]
    assert inventory["set_differences"]["recovered_ids_minus_evaluation_ids"] == []


def test_outputs_are_deterministic_and_successor_is_fail_closed(tmp_path: Path) -> None:
    member, data = _model("UCD_PW_models", "100_UCD_PW.txt")
    repo = _make_repo(tmp_path, {member: data})
    archive = _archive(tmp_path, {member: data})
    first = write_outputs(repo, tmp_path / "out1", archive)
    second = write_outputs(repo, tmp_path / "out2", archive)
    assert first["manifest_sha256"] == second["manifest_sha256"]
    first_bytes = (tmp_path / "out1" / "provenance-manifest.json").read_bytes()
    second_bytes = (tmp_path / "out2" / "provenance-manifest.json").read_bytes()
    assert hashlib.sha256(first_bytes).hexdigest() == hashlib.sha256(second_bytes).hexdigest()
    assert json.loads((tmp_path / "out1" / "missingness-report.json").read_text(encoding="utf-8"))["historical_executability"] == "NOT_EXECUTABLE"


def test_no_absolute_paths_or_content_are_emitted(tmp_path: Path) -> None:
    member, data = _model("UCD_PW_models", "100_UCD_PW.txt")
    repo = _make_repo(tmp_path, {member: data})
    archive = _archive(tmp_path, {member: data})
    _, manifest = build_audit(repo, archive)
    for row in manifest:
        assert not Path(row["source_path"]).is_absolute()
        assert "text" not in row
