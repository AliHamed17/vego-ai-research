import importlib
import json
import socket
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
CLI = ROOT / "scripts" / "inventory_state_diagram.py"


def _inventory_module():
    return importlib.import_module("vego_study1.state_diagram_inventory")


def _synthetic_state_root(tmp_path: Path) -> Path:
    source = tmp_path / "synthetic-state"
    source.mkdir()
    (source / "transition.alpha").write_text("synthetic state A", encoding="utf-8")
    nested = source / "nested"
    nested.mkdir()
    (nested / "transition.beta").write_text("synthetic state B", encoding="utf-8")
    return source


def _private_root(tmp_path: Path) -> Path:
    return tmp_path / "research-private" / "study1" / "task-3"


def test_inventory_receipt_is_deterministic_aggregate_only_and_blocked(tmp_path):
    """Catches an inventory that leaks source details or varies for unchanged local inputs."""
    module = _inventory_module()
    source = _synthetic_state_root(tmp_path)

    first = module.write_state_diagram_inventory(source, _private_root(tmp_path))
    second = module.write_state_diagram_inventory(source, _private_root(tmp_path))
    receipt_text = (_private_root(tmp_path) / "state_diagram_inventory.receipt.json").read_text(
        encoding="utf-8"
    )

    assert first == second
    assert first["status"] == "blocked_pending_data_processing_authorization"
    assert first["file_count"] == 2
    assert first["total_bytes"] == len(b"synthetic state A") + len(b"synthetic state B")
    assert first["suffix_counts"] == {".alpha": 1, ".beta": 1}
    assert len(first["file_hashes"]) == 2
    assert len(first["opaque_locator_hashes"]) == 2
    assert "transition.alpha" not in receipt_text
    assert "nested" not in receipt_text
    assert "synthetic state A" not in receipt_text
    assert "no evaluator configuration" in first["limitations"]
    assert "no cloud model processing" in first["limitations"]
    assert json.loads(receipt_text) == first


def test_inventory_accepts_only_private_study1_destinations(tmp_path):
    """Catches receipt writes to destinations outside the required private Study 1 zone."""
    module = _inventory_module()
    source = _synthetic_state_root(tmp_path)

    with pytest.raises(module.StateDiagramInventoryError, match="research-private.*study1"):
        module.write_state_diagram_inventory(source, tmp_path / "public-output")

    receipt = module.write_state_diagram_inventory(source, _private_root(tmp_path))

    assert receipt["schema_version"] == "StateDiagramInventoryReceipt-v1"


def test_inventory_performs_no_network_activity(tmp_path, monkeypatch):
    """Catches a future local inventory implementation that opens a network socket."""
    module = _inventory_module()
    source = _synthetic_state_root(tmp_path)

    def _blocked_socket(*_args, **_kwargs):
        raise AssertionError("network access is prohibited")

    monkeypatch.setattr(socket, "socket", _blocked_socket)

    assert module.write_state_diagram_inventory(source, _private_root(tmp_path))["file_count"] == 2


def test_inventory_cli_requires_both_roots_and_prints_only_safe_summary(tmp_path):
    """Catches a wrapper that accepts unscoped input or echoes a raw source path."""
    source = _synthetic_state_root(tmp_path)
    private_root = _private_root(tmp_path)

    missing_argument = subprocess.run(
        [sys.executable, str(CLI), "--state-root", str(source)],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    completed = subprocess.run(
        [
            sys.executable,
            str(CLI),
            "--state-root",
            str(source),
            "--private-output-root",
            str(private_root),
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )

    assert missing_argument.returncode != 0
    assert completed.returncode == 0, completed.stderr
    assert "blocked_pending_data_processing_authorization" in completed.stdout
    assert str(source) not in completed.stdout
    assert "transition.alpha" not in completed.stdout
