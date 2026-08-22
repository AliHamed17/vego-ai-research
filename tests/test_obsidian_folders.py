from pathlib import Path

from obsidian_brain import folders
from obsidian_brain.folders import is_allowed_file


def test_folder_ingestion_blocks_credentials_browser_profiles_and_executables(tmp_path: Path) -> None:
    for name in (
        "secrets.env",
        "app.exe",
        "id_ed25519",
        "id_ecdsa",
        "Login Data",
        "Local State",
        "credentials.json",
        "client_secret.json",
        "secrets.json",
        "History",
    ):
        blocked = tmp_path / name
        blocked.write_text("test", encoding="utf-8")
        assert not is_allowed_file(blocked, approved_roots=(tmp_path,))
    approved = tmp_path / "invoice.pdf"
    approved.write_text("test", encoding="utf-8")
    assert not is_allowed_file(approved, approved_roots=(tmp_path,))  # pytest temp roots are under AppData.


def test_folder_ingestion_requires_explicit_approved_root(tmp_path: Path) -> None:
    source = tmp_path / "source" / "invoice.pdf"
    source.parent.mkdir()
    source.write_text("test", encoding="utf-8")

    assert not is_allowed_file(source, approved_roots=(tmp_path / "other",))


def test_reparse_inspection_error_fails_closed(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(folders.os, "lstat", lambda _: (_ for _ in ()).throw(OSError("denied")))

    assert folders._is_reparse_point(tmp_path)
