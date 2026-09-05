import asyncio
import importlib
import os
import socket
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))


def safety():
    assert importlib.util.find_spec("airtravel_execution_safety") is not None
    return importlib.import_module("airtravel_execution_safety")


def test_wall_clock_timeout_restores_client_environment_and_handlers(tmp_path, monkeypatch):
    m = safety()
    original = object()
    runtime = SimpleNamespace(LLMClient=original)
    monkeypatch.setenv("OPENAI_API_KEY", "fixture-private")

    async def slow():
        assert "OPENAI_API_KEY" not in os.environ
        runtime.LLMClient = object()
        await asyncio.sleep(10)

    result = asyncio.run(m.timed_operation(slow, runtime, timeout=0.01))
    assert result["status"] == "TECHNICAL_FAILED" and result["timeout"] is True
    assert runtime.LLMClient is original
    assert os.environ["OPENAI_API_KEY"] == "fixture-private"
    assert "fixture-private" not in str(result)


def test_network_attempt_is_counted_and_raises():
    m = safety()
    with m.ExecutionGuard(Path.cwd(), set(), set()) as guard:
        with pytest.raises(PermissionError):
            socket.create_connection(("example.invalid", 443))
        assert guard.network_attempt_count == 1
    assert guard.network_attempt_count == 1


def test_write_outside_or_unexpected_file_is_blocked(tmp_path):
    m = safety()
    out = tmp_path / "run"
    out.mkdir()
    with m.ExecutionGuard(out, {"expected.json"}, set()):
        with pytest.raises(PermissionError):
            (tmp_path / "outside.json").write_text("no")
        with pytest.raises(PermissionError):
            (out / "unexpected.json").write_text("no")
    assert not (tmp_path / "outside.json").exists()


def test_file_and_byte_limits_are_enforced_before_write(tmp_path):
    m = safety()
    with m.ExecutionGuard(tmp_path, {"a.json", "b.json"}, set(), max_files=1, max_bytes=4):
        (tmp_path / "a.json").write_text("1234")
        with pytest.raises(PermissionError):
            (tmp_path / "b.json").write_text("a")
        with pytest.raises(PermissionError):
            with (tmp_path / "a.json").open("a") as handle:
                handle.write("5")
    assert (tmp_path / "a.json").read_text() == "1234"


def test_receipt_escape_and_broad_execution_roots_fail(tmp_path):
    from airtravel_preflight_contract import output_path, receipt_path

    for path in [
        tmp_path / "output/run",
        tmp_path / "reports/generated/run",
        tmp_path / "external_data",
    ]:
        with pytest.raises(ValueError):
            output_path(path, tmp_path)
    out = tmp_path / "external_data/preflight/run1"
    assert output_path(out, tmp_path) == out
    with pytest.raises(ValueError):
        receipt_path(tmp_path / "receipt.json", out)


def test_output_symlink_escape_fails(tmp_path):
    from airtravel_preflight_contract import output_path

    outside = tmp_path / "outside"
    outside.mkdir()
    link = tmp_path / "external_data/preflight"
    link.parent.mkdir()
    try:
        link.symlink_to(outside, target_is_directory=True)
    except OSError:
        pytest.skip("OS did not grant symlink creation")
    with pytest.raises(ValueError):
        output_path(link / "run1", tmp_path)
