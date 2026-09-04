from __future__ import annotations

import json
import pathlib
import sys
from pathlib import Path

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

from verify_text2uml_airtravel_runtime import verify_pack  # noqa: E402


def _fixture(tmp_path: Path) -> tuple[Path, Path, Path]:
    stage = tmp_path / "external" / "prepared" / "AirTravel"
    runtime = stage / "runtime_input"
    (runtime / "domain_description").mkdir(parents=True)
    (runtime / "candidate_models").mkdir()
    (stage / "reference_only").mkdir()
    (runtime / "domain_description" / "description.md").write_text("domain\n", encoding="utf-8")
    (runtime / "candidate_models" / "01_case.txt").write_text("@startuml\n@enduml\n", encoding="utf-8")
    (stage / "reference_only" / "plantuml.txt").write_text("reference\n", encoding="utf-8")
    config = tmp_path / "config.json"
    config.write_text(json.dumps({"provider_run_permitted": False, "settings": [{
        "setting_id": "cd_airtravel", "corpus_id": "text2uml_airtravel_test",
        "provider_run_permitted": False,
    }]}), encoding="utf-8")
    amendment = tmp_path / "amendment.json"
    files = []
    for path in sorted(p for p in runtime.rglob("*") if p.is_file()):
        import hashlib
        files.append({"path": path.relative_to(runtime).as_posix(), "bytes": path.stat().st_size,
                      "sha256": hashlib.sha256(path.read_bytes()).hexdigest()})
    amendment.write_text(json.dumps({"amendment_version": "text2uml-airtravel-v1.0.2",
                                     "setting_id": "cd_airtravel", "corpus_id": "text2uml_airtravel_test",
                                     "runtime_files": files}), encoding="utf-8")
    return config, stage.parent.parent, amendment


def test_missing_v102_manifest_fails_closed(tmp_path: Path) -> None:
    config, stage_root, _ = _fixture(tmp_path)
    result = verify_pack(config, stage_root, tmp_path / "missing.json")
    assert result["status"] == "BLOCKED"
    assert result["provider_call_made"] is False


def test_runtime_hashes_and_reference_separation_pass(tmp_path: Path) -> None:
    config, stage_root, amendment = _fixture(tmp_path)
    result = verify_pack(config, stage_root, amendment)
    assert result["status"] == "PASS"
    assert {check["name"] for check in result["checks"]} == {
        "setting_and_corpus_identity", "runtime_bytes", "reference_separation", "provider_disabled"
    }


def test_runtime_byte_drift_blocks(tmp_path: Path) -> None:
    config, stage_root, amendment = _fixture(tmp_path)
    runtime = stage_root / "prepared" / "AirTravel" / "runtime_input"
    (runtime / "candidate_models" / "01_case.txt").write_text("drift\n", encoding="utf-8")
    result = verify_pack(config, stage_root, amendment)
    assert result["status"] == "BLOCKED"
    assert next(check for check in result["checks"] if check["name"] == "runtime_bytes")["status"] == "FAIL"
