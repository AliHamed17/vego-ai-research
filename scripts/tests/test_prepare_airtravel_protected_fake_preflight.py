"""Fixture-only engineering tests for the AirTravel preflight harness.

These tests use synthetic fixture files and monkeypatched frozen constants
only.  They never invoke the exact protected AirTravel N=4 orchestrator
configuration, any provider, or any network access.
"""

from __future__ import annotations

import hashlib
import json
import pathlib
import socket
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

import prepare_airtravel_protected_fake_preflight as preflight  # noqa: E402


def _write(path: pathlib.Path, data: bytes) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    return hashlib.sha256(data).hexdigest()


def _fixture_pack(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> pathlib.Path:
    runtime_root = tmp_path / "runtime_input"
    fixture_files: dict[str, tuple[str, int]] = {}
    for index, relative in enumerate(sorted(preflight.FROZEN["runtime_files"]), start=1):
        data = f"fixture-{index}\n".encode()
        digest = _write(runtime_root / relative, data)
        fixture_files[relative] = (digest, len(data))
    config = {
        "setting_id": "cd_airtravel",
        "corpus_id": "text2uml_airtravel_253b26dc",
        "provider_execution_enabled": False,
        "description_path": "domain_description/description.md",
        "candidate_models_dir": "candidate_models",
        "runtime_files": sorted(fixture_files),
    }
    (runtime_root / "cd_airtravel.runtime-config.json").write_text(
        json.dumps(config), encoding="utf-8"
    )
    monkeypatch.setitem(preflight.FROZEN, "runtime_files", fixture_files)
    return runtime_root


def _fixture_archive(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> pathlib.Path:
    archive = tmp_path / "runtime.zip"
    digest = _write(archive, b"fixture-archive")
    monkeypatch.setitem(preflight.FROZEN, "runtime_archive_sha256", digest)
    return archive


def test_missing_runtime_root_is_blocked(tmp_path: pathlib.Path) -> None:
    result = preflight.check_runtime_pack(tmp_path / "absent")
    assert result["status"] == "BLOCKED"


def test_hash_mismatch_and_extra_and_missing_files_fail(
    tmp_path: pathlib.Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    runtime_root = _fixture_pack(tmp_path, monkeypatch)
    first = sorted(preflight.FROZEN["runtime_files"])[0]
    (runtime_root / first).write_bytes(b"tampered")
    (runtime_root / "candidate_models" / "extra.txt").write_bytes(b"extra")
    last = sorted(preflight.FROZEN["runtime_files"])[-1]
    (runtime_root / last).unlink()
    result = preflight.check_runtime_pack(runtime_root)
    assert result["status"] == "FAIL"
    text = " ".join(result["problems"])
    assert "mismatch" in text and "unexpected" in text and "missing" in text


def test_reference_leakage_is_rejected(
    tmp_path: pathlib.Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    runtime_root = _fixture_pack(tmp_path, monkeypatch)
    (runtime_root / "candidate_models" / "plantuml.txt").write_bytes(b"ref")
    result = preflight.check_runtime_pack(runtime_root)
    assert result["status"] == "FAIL"
    assert any("reference material" in problem for problem in result["problems"])


def test_runtime_archive_missing_and_wrong_hash(
    tmp_path: pathlib.Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    assert preflight.check_runtime_archive(tmp_path / "absent.zip")["status"] == "BLOCKED"
    archive = _fixture_archive(tmp_path, monkeypatch)
    archive.write_bytes(b"different")
    assert preflight.check_runtime_archive(archive)["status"] == "FAIL"


def test_protected_files_match_on_the_real_repository() -> None:
    result = preflight.check_protected_files(ROOT)
    assert result["status"] == "PASS", result["problems"]


def test_output_dir_rules(tmp_path: pathlib.Path) -> None:
    outside = preflight.check_output_dir(tmp_path / "elsewhere", tmp_path / "repo")
    assert outside["status"] == "FAIL"
    repo = tmp_path / "repo"
    bad_prefix = repo / "docs" / "run"
    bad_prefix.mkdir(parents=True)
    assert preflight.check_output_dir(bad_prefix, repo)["status"] == "FAIL"
    occupied = repo / "external_data" / "run1"
    occupied.mkdir(parents=True)
    (occupied / "old.json").write_text("{}", encoding="utf-8")
    assert preflight.check_output_dir(occupied, repo)["status"] == "FAIL"
    fresh = repo / "external_data" / "preflight" / "run2"
    assert preflight.check_output_dir(fresh, repo)["status"] == "PASS"
    assert preflight.check_output_dir(None, repo)["status"] == "FAIL"


def test_provider_disabled_reports_presence_only(
    tmp_path: pathlib.Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    runtime_root = _fixture_pack(tmp_path, monkeypatch)
    monkeypatch.setenv("OPENAI_API_KEY", "sk-fixture-value-never-shown")
    result = preflight.check_provider_disabled(runtime_root)
    assert result["status"] == "PASS"
    assert result["provider_key_presence"] == {"OPENAI_API_KEY": "PRESENT"}
    assert "sk-fixture-value-never-shown" not in json.dumps(result)
    config_path = runtime_root / "cd_airtravel.runtime-config.json"
    config = json.loads(config_path.read_text(encoding="utf-8"))
    config["provider_execution_enabled"] = True
    config_path.write_text(json.dumps(config), encoding="utf-8")
    assert preflight.check_provider_disabled(runtime_root)["status"] == "FAIL"


def test_network_guard_blocks_socket_creation() -> None:
    with preflight.network_disabled():
        with pytest.raises(preflight.PreflightGateError):
            socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        with pytest.raises(preflight.PreflightGateError):
            socket.create_connection(("localhost", 80))
    assert socket.socket is not None


def test_prepare_only_reports_counters_and_prepared_status(
    tmp_path: pathlib.Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    runtime_root = _fixture_pack(tmp_path, monkeypatch)
    archive = _fixture_archive(tmp_path, monkeypatch)
    result = preflight.prepare_only(
        runtime_root, archive, ROOT / "external_data/fixture-tests/new-run", repo_root=ROOT
    )
    assert result["status"] == "PREPARED"
    assert result["protected_orchestrator_fake_route_count"] == "NOT_EXECUTED"
    assert result["provider_backed_production_route_count"] == 0
    assert result["external_provider_call_count"] == 0
    assert result["orchestrator_invoked"] is False
    assert result["fake_client_invoked"] is False
    assert result["scientific_events_written"] is False


def test_prepare_only_is_blocked_when_pack_absent(tmp_path: pathlib.Path) -> None:
    result = preflight.prepare_only(
        tmp_path / "absent", tmp_path / "absent.zip", None, repo_root=ROOT
    )
    assert result["status"] == "BLOCKED"


def test_cli_defaults_to_prepare_only_and_exits_nonzero_when_blocked(
    tmp_path: pathlib.Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture,
) -> None:
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "prepare_airtravel_protected_fake_preflight.py",
            "--runtime-root",
            str(tmp_path / "absent"),
            "--runtime-archive",
            str(tmp_path / "absent.zip"),
        ],
    )
    assert preflight.main() == 2
    payload = json.loads(capsys.readouterr().out)
    assert payload["mode"] == "prepare_only"
    assert payload["status"] == "BLOCKED"


def test_execute_requires_authorization_flags(
    tmp_path: pathlib.Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "prepare_airtravel_protected_fake_preflight.py",
            "--execute",
            "--output-dir",
            str(tmp_path / "out"),
        ],
    )
    with pytest.raises(SystemExit) as excinfo:
        preflight.main()
    assert excinfo.value.code == 2


def test_execute_refuses_missing_packet_and_blocked_preparation(
    tmp_path: pathlib.Path,
) -> None:
    with pytest.raises(preflight.PreflightGateError, match="authorization packet"):
        preflight.execute_preflight(
            tmp_path / "absent",
            tmp_path / "absent.zip",
            tmp_path / "out",
            tmp_path / "missing-packet.md",
        )
    packet = tmp_path / "packet.md"
    packet.write_text("AUTHORIZATION REQUESTED", encoding="utf-8")
    with pytest.raises(preflight.PreflightGateError, match="grant"):
        preflight.execute_preflight(
            tmp_path / "absent", tmp_path / "absent.zip", tmp_path / "out", packet
        )


def test_scrubbed_provider_env_round_trip(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", "sk-fixture")
    import os

    removed = preflight.scrubbed_provider_env()
    assert os.environ.get("OPENAI_API_KEY") is None
    assert removed["OPENAI_API_KEY"] == "sk-fixture"
    os.environ["OPENAI_API_KEY"] = removed["OPENAI_API_KEY"]


@pytest.mark.parametrize(
    "status,expected_exit", [("TECHNICAL_SUCCESS", 0), ("TECHNICAL_FAILED", 2)]
)
def test_cli_exit_matches_future_receipt_status_without_execution(
    monkeypatch, tmp_path, status, expected_exit
):
    # Dispatch-only test: replace the entire execution function. No runtime,
    # grant receipt, corpus, fake client or orchestrator is constructed.
    monkeypatch.setattr(preflight, "execute_preflight", lambda *a, **k: {"status": status})
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "prepare_airtravel_protected_fake_preflight.py",
            "--execute",
            "--authorization-packet",
            str(tmp_path / "unused-request.md"),
            "--authorization-grant",
            str(tmp_path / "unused-grant.json"),
            "--output-dir",
            str(tmp_path / "unused-output"),
        ],
    )
    assert preflight.main() == expected_exit
    assert not (tmp_path / "unused-output").exists()
