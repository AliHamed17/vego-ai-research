from pathlib import Path

from obsidian_brain.__main__ import run


def test_init_command_creates_the_obsidian_layer_only_after_verification(tmp_path: Path) -> None:
    root = tmp_path / "Private Brain"

    exit_code = run(["init", "--vault-root", str(root)], encryption_verified=lambda _: True)

    assert exit_code == 0
    assert (root / "Obsidian Notes" / "Secondary Brain Dashboard.md").exists()
