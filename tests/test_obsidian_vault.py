import shutil
import sqlite3
import threading
import time
from hashlib import sha256
from pathlib import Path

import pytest

from obsidian_brain.adapters import SourceProvenance, write_user_authorized_manifest
from obsidian_brain.vault import EncryptionUnavailable, ObsidianVault, efs_output_is_verified


def local_provenance(tmp_path: Path, content: str | bytes) -> SourceProvenance:
    payload = content.encode("utf-8") if isinstance(content, str) else content
    return write_user_authorized_manifest(
        tmp_path / "approved-local-export.json",
        source="local_folders",
        method="approved_local_root",
        content_sha256=sha256(payload).hexdigest(),
    )


def test_efs_verifier_accepts_only_explicit_encrypted_status() -> None:
    assert efs_output_is_verified("Directory: C:\\vault\n  E vault.sqlite")
    assert not efs_output_is_verified("Directory: C:\\vault\n  U vault.sqlite")


def test_vault_refuses_to_initialize_when_encryption_is_unverified(tmp_path: Path) -> None:
    with pytest.raises(EncryptionUnavailable):
        ObsidianVault.initialize(tmp_path / "Private Brain", encryption_verified=lambda _: False)


def test_initialize_creates_an_obsidian_dashboard(tmp_path: Path) -> None:
    vault = ObsidianVault.initialize(tmp_path / "Private Brain", encryption_verified=lambda _: True)

    dashboard = vault.notes_root / "Secondary Brain Dashboard.md"
    assert dashboard.exists()
    assert "# Secondary Brain Dashboard" in dashboard.read_text(encoding="utf-8")


def test_private_content_is_archived_but_only_a_safe_note_is_written_to_obsidian(tmp_path: Path) -> None:
    vault = ObsidianVault.initialize(tmp_path / "Private Brain", encryption_verified=lambda _: True)

    record = vault.archive_text(
        title="Electricity bill",
        content="Account 123456. Amount due 125 ILS.",
        provenance=local_provenance(tmp_path, "Account 123456. Amount due 125 ILS."),
        classification="restricted",
    )

    note = (vault.notes_root / "Sources" / f"{record.item_id}.md").read_text(encoding="utf-8")
    assert record.item_id in note
    assert record.sha256 in note
    assert "Account 123456" not in note
    assert "Amount due 125" not in note


def test_deletion_removes_private_content_and_leaves_a_receipt(tmp_path: Path) -> None:
    vault = ObsidianVault.initialize(tmp_path / "Private Brain", encryption_verified=lambda _: True)
    record = vault.archive_text(
        title="Private note",
        content="Sensitive private text",
        provenance=local_provenance(tmp_path, "Sensitive private text"),
        classification="restricted",
    )

    vault.delete(record.item_id)

    assert not (vault.archive_root / f"{record.sha256}.txt").exists()
    receipt = (vault.notes_root / "Receipts" / f"{record.item_id}-deleted.md").read_text(
        encoding="utf-8"
    )
    assert record.sha256 in receipt
    assert "Sensitive private text" not in receipt


def test_file_archive_preserves_the_original_only_inside_the_encrypted_area(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    vault = ObsidianVault.initialize(tmp_path / "Private Brain", encryption_verified=lambda _: True)
    source = tmp_path / "invoice.pdf"
    source.write_bytes(b"private attachment 98765")
    monkeypatch.setattr("obsidian_brain.vault.is_allowed_file", lambda *_args, **_kwargs: True)

    record = vault.archive_file(
        source,
        provenance=local_provenance(tmp_path, b"private attachment 98765"),
        approved_roots=(tmp_path,),
        classification="restricted",
    )

    assert (vault.archive_root / f"{record.sha256}.pdf").read_bytes() == b"private attachment 98765"
    note = (vault.notes_root / "Sources" / f"{record.item_id}.md").read_text(encoding="utf-8")
    assert "98765" not in note


def test_file_archive_does_not_reread_the_source_after_staging(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    vault = ObsidianVault.initialize(tmp_path / "Private Brain", encryption_verified=lambda _: True)
    source = tmp_path / "export.pdf"
    source.write_bytes(b"private attachment")
    monkeypatch.setattr("obsidian_brain.vault.is_allowed_file", lambda *_args, **_kwargs: True)
    monkeypatch.setattr(
        shutil, "copy2", lambda *_args, **_kwargs: (_ for _ in ()).throw(AssertionError())
    )

    record = vault.archive_file(
        source,
        provenance=local_provenance(tmp_path, b"private attachment"),
        approved_roots=(tmp_path,),
        classification="restricted",
    )

    assert (vault.archive_root / f"{record.sha256}.pdf").read_bytes() == b"private attachment"


def test_file_archive_rejects_a_secret_like_source(tmp_path: Path) -> None:
    vault = ObsidianVault.initialize(tmp_path / "Private Brain", encryption_verified=lambda _: True)
    source = tmp_path / "secrets.env"
    source.write_text("API_KEY=not-for-import", encoding="utf-8")

    with pytest.raises(ValueError, match="not allowed"):
        vault.archive_file(
            source,
            provenance=local_provenance(tmp_path, "API_KEY=not-for-import"),
            approved_roots=(tmp_path,),
            classification="restricted",
        )


def test_deletion_removes_an_archived_file_without_an_extension(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    vault = ObsidianVault.initialize(tmp_path / "Private Brain", encryption_verified=lambda _: True)
    source = tmp_path / "meeting-export"
    source.write_bytes(b"private export")
    monkeypatch.setattr("obsidian_brain.vault.is_allowed_file", lambda *_args, **_kwargs: True)
    record = vault.archive_file(
        source,
        provenance=local_provenance(tmp_path, b"private export"),
        approved_roots=(tmp_path,),
        classification="restricted",
    )

    vault.delete(record.item_id)

    assert not (vault.archive_root / record.sha256).exists()


def test_raw_write_rechecks_encryption_at_the_actual_archive_target(tmp_path: Path) -> None:
    outcomes = iter((True, True, False))
    vault = ObsidianVault.initialize(
        tmp_path / "Private Brain", encryption_verified=lambda _: next(outcomes)
    )

    with pytest.raises(EncryptionUnavailable):
        vault.archive_text(
            title="Safe title",
            content="Private body",
            provenance=local_provenance(tmp_path, "Private body"),
            classification="restricted",
        )


def test_vault_rejects_a_root_inside_a_git_checkout(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / ".git").mkdir(parents=True)

    with pytest.raises(ValueError, match="repository"):
        ObsidianVault.initialize(repo / "private-vault", encryption_verified=lambda _: True)
    direct = ObsidianVault(repo / "private-vault", encryption_verified=lambda _: True)
    with pytest.raises(EncryptionUnavailable, match="repository"):
        _ = direct.search_database


def test_vault_rejects_multiline_title_and_unknown_classification(tmp_path: Path) -> None:
    vault = ObsidianVault.initialize(tmp_path / "Private Brain", encryption_verified=lambda _: True)

    with pytest.raises(ValueError, match="title"):
        vault.archive_text(
            title="Title\nprivate source body",
            content="Private body",
            provenance=local_provenance(tmp_path, "Private body"),
            classification="restricted",
        )
    with pytest.raises(ValueError, match="classification"):
        vault.archive_text(
            title="Safe title",
            content="Private body",
            provenance=local_provenance(tmp_path, "Private body"),
            classification="anything\nprivate source body",
        )


def test_archived_manifest_is_the_exact_validated_payload(tmp_path: Path) -> None:
    vault = ObsidianVault.initialize(tmp_path / "Private Brain", encryption_verified=lambda _: True)
    content = "Private body"
    provenance = local_provenance(tmp_path, content)
    expected_payload = provenance.manifest.read_bytes()

    record = vault.archive_text(
        title="Safe title",
        content=content,
        provenance=provenance,
        classification="restricted",
    )

    stored = vault.archive_root / "manifests" / f"{record.provenance_sha256}.json"
    assert stored.read_bytes() == expected_payload


def test_text_import_cleans_raw_content_when_receipt_persistence_fails(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    vault = ObsidianVault.initialize(tmp_path / "Private Brain", encryption_verified=lambda _: True)
    content = "Private body"
    monkeypatch.setattr(vault, "_preserve_manifest", lambda _: (_ for _ in ()).throw(OSError()))

    with pytest.raises(OSError):
        vault.archive_text(
            title="Safe title",
            content=content,
            provenance=local_provenance(tmp_path, content),
            classification="restricted",
        )

    assert not (vault.archive_root / f"{sha256(content.encode()).hexdigest()}.txt").exists()


def test_file_import_cleans_promoted_content_when_receipt_persistence_fails(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    vault = ObsidianVault.initialize(tmp_path / "Private Brain", encryption_verified=lambda _: True)
    content = b"Private export"
    source = tmp_path / "export.pdf"
    source.write_bytes(content)
    monkeypatch.setattr("obsidian_brain.vault.is_allowed_file", lambda *_args, **_kwargs: True)
    monkeypatch.setattr(vault, "_preserve_manifest", lambda _: (_ for _ in ()).throw(OSError()))

    with pytest.raises(OSError):
        vault.archive_file(
            source,
            provenance=local_provenance(tmp_path, content),
            approved_roots=(tmp_path,),
            classification="restricted",
        )

    assert not (vault.archive_root / f"{sha256(content).hexdigest()}.pdf").exists()


def test_import_refuses_an_unreconciled_raw_destination(tmp_path: Path) -> None:
    vault = ObsidianVault.initialize(tmp_path / "Private Brain", encryption_verified=lambda _: True)
    content = "Private body"
    destination = vault.archive_root / f"{sha256(content.encode()).hexdigest()}.txt"
    destination.write_text("unreconciled", encoding="utf-8")

    with pytest.raises(RuntimeError, match="Unreconciled"):
        vault.archive_text(
            title="Safe title",
            content=content,
            provenance=local_provenance(tmp_path, content),
            classification="restricted",
        )

    assert destination.read_text(encoding="utf-8") == "unreconciled"


def test_text_import_cleans_a_partial_staged_write(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    vault = ObsidianVault.initialize(tmp_path / "Private Brain", encryption_verified=lambda _: True)
    content = "Private body"
    original_write = Path.write_text

    def fail_staged_write(path: Path, value: str, *args, **kwargs) -> int:
        if path.parent == vault.archive_root and path.name.startswith(".text-"):
            path.write_bytes(b"partial")
            raise OSError("disk full")
        return original_write(path, value, *args, **kwargs)

    monkeypatch.setattr(Path, "write_text", fail_staged_write)
    with pytest.raises(OSError, match="disk full"):
        vault.archive_text(
            title="Safe title",
            content=content,
            provenance=local_provenance(tmp_path, content),
            classification="restricted",
        )

    assert not list(vault.archive_root.glob(".text-*.stage"))
    assert not (vault.archive_root / f"{sha256(content.encode()).hexdigest()}.txt").exists()


def test_import_waits_for_the_sqlite_writer_lock_before_promoting_raw_content(tmp_path: Path) -> None:
    vault = ObsidianVault.initialize(tmp_path / "Private Brain", encryption_verified=lambda _: True)
    content = "Concurrent private body"
    destination = vault.archive_root / f"{sha256(content.encode()).hexdigest()}.txt"
    result: list[object] = []

    with sqlite3.connect(vault.database) as lock_connection:
        lock_connection.execute("BEGIN IMMEDIATE")
        worker = threading.Thread(
            target=lambda: result.append(
                vault.archive_text(
                    title="Safe title",
                    content=content,
                    provenance=local_provenance(tmp_path, content),
                    classification="restricted",
                )
            )
        )
        worker.start()
        time.sleep(0.1)
        assert not destination.exists()
        lock_connection.commit()
    worker.join(timeout=5)

    assert not worker.is_alive()
    assert result
