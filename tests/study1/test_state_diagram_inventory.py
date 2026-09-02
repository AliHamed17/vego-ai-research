import importlib
import json
import shutil
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
    return tmp_path / "temporary-repository" / "research-private" / "study1" / "task-3"


@pytest.fixture(autouse=True)
def _approved_private_test_repository(tmp_path, monkeypatch):
    """Use a synthetic local Git repository to exercise the private-root ignore gate."""
    repository_root = tmp_path / "temporary-repository"
    repository_root.mkdir()
    subprocess.run(["git", "init", "-q", str(repository_root)], check=True)
    (repository_root / ".gitignore").write_text("research-private/study1/\n", encoding="utf-8")
    monkeypatch.setattr(_inventory_module(), "REPOSITORY_ROOT", repository_root)


def _cli_private_root(tmp_path: Path) -> Path:
    return ROOT / "research-private" / "study1" / f"pytest-{tmp_path.name}"


def _symlink_or_skip(link: Path, target: Path, *, directory: bool = False) -> None:
    try:
        link.symlink_to(target, target_is_directory=directory)
    except OSError as error:
        pytest.skip(f"local symlink creation is unavailable: {error}")


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


@pytest.mark.parametrize("remote_value", ["s3" + ":study1-state", "\\" + r"\server\share\state"])
def test_inventory_rejects_uri_and_unc_state_roots_before_reading(tmp_path, remote_value):
    """Catches URI-like and UNC state roots that would be treated as local filesystem input."""
    module = _inventory_module()

    with pytest.raises(module.StateDiagramInventoryError, match="remote"):
        module.write_state_diagram_inventory(remote_value, _private_root(tmp_path))


def test_inventory_screens_remote_state_root_before_private_git_check(tmp_path, monkeypatch):
    """Catches a remote state root that reaches private-root filesystem validation first."""
    module = _inventory_module()

    def _unexpected_git_check(*_args, **_kwargs):
        raise AssertionError("remote input reached the Git-ignore check")

    path_safety = importlib.import_module("vego_study1.path_safety")
    monkeypatch.setattr(path_safety.subprocess, "run", _unexpected_git_check)

    with pytest.raises(module.StateDiagramInventoryError, match="remote"):
        module.write_state_diagram_inventory("s3" + ":study1-state", _private_root(tmp_path))


@pytest.mark.parametrize("remote_value", ["s3" + ":study1-output", "\\" + r"\server\share\output"])
def test_inventory_rejects_uri_and_unc_output_roots_before_reading(tmp_path, remote_value):
    """Catches remote output roots before the inventory attempts to inspect a source directory."""
    module = _inventory_module()

    with pytest.raises(module.StateDiagramInventoryError, match="remote"):
        module.write_state_diagram_inventory(tmp_path / "must-not-read", remote_value)


def test_inventory_rejects_same_name_private_lookalike_outside_repository(tmp_path):
    """Catches an output root accepted solely because its path contains private-looking segments."""
    module = _inventory_module()
    source = _synthetic_state_root(tmp_path)
    lookalike = tmp_path / "unapproved" / "research-private" / "study1" / "task-3"

    with pytest.raises(
        module.StateDiagramInventoryError, match="repository.*research-private.*study1"
    ):
        module.write_state_diagram_inventory(source, lookalike)


def test_inventory_performs_no_network_activity(tmp_path, monkeypatch):
    """Catches a future local inventory implementation that opens a network socket."""
    module = _inventory_module()
    source = _synthetic_state_root(tmp_path)

    def _blocked_socket(*_args, **_kwargs):
        raise AssertionError("network access is prohibited")

    monkeypatch.setattr(socket, "socket", _blocked_socket)

    assert module.write_state_diagram_inventory(source, _private_root(tmp_path))["file_count"] == 2


def test_inventory_rejects_symlink_entries_during_state_discovery(tmp_path):
    """Catches recursive discovery following a state entry outside the selected source root."""
    module = _inventory_module()
    source = _synthetic_state_root(tmp_path)
    outside = tmp_path / "outside-state.txt"
    outside.write_text("must not be inventoried", encoding="utf-8")
    _symlink_or_skip(source / "linked-outside.txt", outside)

    with pytest.raises(module.StateDiagramInventoryError, match="symlink|reparse"):
        module.write_state_diagram_inventory(source, _private_root(tmp_path))


def test_inventory_rejects_reparse_point_in_state_root_parent_component(tmp_path):
    """Catches a source root reached through a redirecting parent directory."""
    module = _inventory_module()
    real_parent = tmp_path / "real-parent"
    real_parent.mkdir()
    source = _synthetic_state_root(real_parent)
    linked_parent = tmp_path / "linked-parent"
    _symlink_or_skip(linked_parent, real_parent, directory=True)
    aliased_source = linked_parent / source.relative_to(real_parent)

    with pytest.raises(module.StateDiagramInventoryError, match="symlink|reparse"):
        module.write_state_diagram_inventory(aliased_source, _private_root(tmp_path))


def test_inventory_rejects_symlink_receipt_leaf_without_overwriting_target(tmp_path):
    """Catches an inventory receipt leaf redirecting a write outside the approved root."""
    module = _inventory_module()
    source = _synthetic_state_root(tmp_path)
    output_root = _private_root(tmp_path)
    output_root.mkdir(parents=True)
    outside = tmp_path / "outside-inventory.json"
    outside.write_text("outside stays unchanged", encoding="utf-8")
    _symlink_or_skip(output_root / module.RECEIPT_NAME, outside)

    with pytest.raises(module.StateDiagramInventoryError, match="symlink|reparse"):
        module.write_state_diagram_inventory(source, output_root)

    assert outside.read_text(encoding="utf-8") == "outside stays unchanged"


def test_inventory_cli_requires_both_roots_and_prints_only_safe_summary(tmp_path):
    """Catches a wrapper that accepts unscoped input or echoes a raw source path."""
    source = _synthetic_state_root(tmp_path)
    private_root = _cli_private_root(tmp_path)

    try:
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
    finally:
        shutil.rmtree(private_root, ignore_errors=True)
