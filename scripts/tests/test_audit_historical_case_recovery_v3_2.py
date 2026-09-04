from __future__ import annotations

import hashlib
import importlib.util
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location("audit_v32", ROOT / "scripts" / "audit_historical_case_recovery_v3_2.py")
assert SPEC and SPEC.loader
MOD = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MOD)


def test_manifest_ref_mismatch_fails_closed() -> None:
    result = MOD.resolve_manifest("refs/does-not-exist", "missing.json", "0" * 64)
    assert result["status"] == "BLOCKED"


def test_fake_preflight_does_not_run_when_runtime_gate_is_blocked() -> None:
    result = MOD.fake_preflight("BLOCKED")
    assert result == {"status": "BLOCKED_NOT_RUN", "reason": "exact five-file runtime verification did not pass", "provider_calls": 0}


def test_upstream_verification_requires_real_archive(tmp_path: Path) -> None:
    result = MOD.verify_upstream(tmp_path / "missing.zip", tmp_path / "missing.json")
    assert result["status"] == "BLOCKED"


def test_known_valid_runtime_pack_is_strict_pass(tmp_path: Path) -> None:
    files = {
        "domain_description/description.md": b"domain",
        "candidate_models/01.txt": b"@startuml\n@enduml\n",
        "candidate_models/02.txt": b"a",
        "candidate_models/03.txt": b"b",
        "candidate_models/04.txt": b"c",
    }
    archive = tmp_path / "runtime.zip"
    with zipfile.ZipFile(archive, "w") as zf:
        for path, data in files.items():
            zf.writestr(path, data)
    amendment = {"runtime_files": [{"path": path, "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()} for path, data in files.items()]}
    config = tmp_path / "config.json"
    config.write_text(__import__("json").dumps({"setting_id": "cd_airtravel", "corpus_id": "text2uml_airtravel_253b26dc", "provider_execution_enabled": False, "description_path": "domain_description/description.md", "candidate_models_dir": "candidate_models", "runtime_files": sorted(files)}), encoding="utf-8")
    result = MOD.verify_runtime_pack(archive, amendment, config)
    assert result["status"] == "PASS"
    assert result["matched_count"] == 5


def test_runtime_pack_requires_configuration(tmp_path: Path) -> None:
    archive = tmp_path / "runtime.zip"
    with zipfile.ZipFile(archive, "w") as zf:
        for i in range(5):
            zf.writestr(f"runtime_input/{i}.txt", b"x")
    amendment = {"runtime_files": [{"path": f"{i}.txt", "bytes": 1, "sha256": hashlib.sha256(b"x").hexdigest()} for i in range(5)]}
    assert MOD.verify_runtime_pack(archive, amendment)["status"] == "BLOCKED"


def test_runtime_pack_rejects_duplicate_member_and_reference(tmp_path: Path) -> None:
    archive = tmp_path / "runtime.zip"
    with zipfile.ZipFile(archive, "w") as zf:
        for i in range(5):
            zf.writestr(f"runtime_input/{i}.txt", b"x")
        zf.writestr("runtime_input/0.txt", b"x")
        zf.writestr("runtime_input/reference_only/model.txt", b"secret")
    amendment = {"runtime_files": [{"path": f"{i}.txt", "bytes": 1, "sha256": hashlib.sha256(b"x").hexdigest()} for i in range(5)]}
    config = tmp_path / "config.json"
    config.write_text(__import__("json").dumps({"setting_id": "cd_airtravel", "corpus_id": "text2uml_airtravel_253b26dc", "provider_execution_enabled": False, "description_path": "domain_description/description.md", "candidate_models_dir": "candidate_models", "runtime_files": [f"{i}.txt" for i in range(5)]}), encoding="utf-8")
    result = MOD.verify_runtime_pack(archive, amendment, config)
    assert result["status"] == "FAIL"
    assert result["duplicate_members"]
    assert result["reference_files_visible"]


def test_mapping_requires_five_unique_byte_identical_entries(tmp_path: Path) -> None:
    data = {"description.md": b"d", "result_one_a.txt": b"1", "result_one_b.txt": b"2", "result_one_c.txt": b"3", "result_one_d.txt": b"4"}
    archive = tmp_path / "runtime.zip"
    with zipfile.ZipFile(archive, "w") as zf:
        for name, value in data.items():
            zf.writestr("runtime_input/" + ("domain_description/description.md" if name == "description.md" else f"candidate_models/{name}"), value)
    mappings = [{"source_path": name, "runtime_path": "domain_description/description.md" if name == "description.md" else f"candidate_models/{name}", "bytes": len(value), "sha256": hashlib.sha256(value).hexdigest(), "transformation": "BYTE_IDENTICAL_RELOCATION", "byte_transformation": "NONE"} for name, value in data.items()]
    upstream = {"status": "PASS", "archive_members": ["root/dataset/AirTravel/" + name for name in data], "archive_bytes": {"root/dataset/AirTravel/" + name: hashlib.sha256(value).hexdigest() for name, value in data.items()}}
    amendment = {"source_to_runtime_mapping": mappings, "runtime_files": [{"path": item["runtime_path"], "role": "domain_description" if item["source_path"] == "description.md" else "candidate_model"} for item in mappings]}
    result = MOD.verify_mapping(upstream, amendment, archive)
    assert result["status"] == "PASS"
    assert result["byte_identical"] is True


def test_mapping_duplicate_paths_fail_closed(tmp_path: Path) -> None:
    amendment = {"source_to_runtime_mapping": [{"source_path": "a", "runtime_path": "x"}] * 5, "runtime_files": [{"role": "domain_description"}] + [{"role": "candidate_model"}] * 4}
    archive = tmp_path / "empty.zip"
    with zipfile.ZipFile(archive, "w"):
        pass
    result = MOD.verify_mapping({"status": "PASS"}, amendment, archive)
    assert result["status"] == "FAIL"


def test_historical_path_does_not_invoke_obsolete_airtravel_audit() -> None:
    source = (ROOT / "scripts" / "audit_historical_case_recovery_v3_2.py").read_text(encoding="utf-8")
    assert "audit_v31(" not in source
    assert "origin/review/study1-airtravel-v102" not in source
