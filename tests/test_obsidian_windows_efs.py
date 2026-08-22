from pathlib import Path

from obsidian_brain.windows_efs import verify_windows_efs


def test_windows_efs_verification_requires_an_encrypted_probe_status(tmp_path: Path) -> None:
    root = tmp_path / "vault"
    root.mkdir()

    assert verify_windows_efs(root, run_cipher=lambda _: "  E .encryption-verification-probe")
    assert not verify_windows_efs(root, run_cipher=lambda _: "  U .encryption-verification-probe")
    assert not (root / ".encryption-verification-probe").exists()
