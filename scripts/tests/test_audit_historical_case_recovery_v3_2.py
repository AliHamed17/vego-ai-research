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
    result = MOD.verify_runtime_pack(archive, amendment)
    assert result["status"] == "PASS"
    assert result["matched_count"] == 5
