from __future__ import annotations

import hashlib
import os
import re
import sqlite3
import uuid
from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

from .adapters import AdapterRegistry, SourceProvenance
from .dashboard import render_dashboard_note
from .folders import is_allowed_file


class EncryptionUnavailable(RuntimeError):
    """Raised when an encrypted local vault has not been verified."""


def efs_output_is_verified(output: str) -> bool:
    """Accept only a ``cipher /c``-style encrypted file status line.

    Status text such as ``U`` (unencrypted), descriptive prose, or a missing
    file row fails closed.
    """

    return bool(re.search(r"(?m)^\s*E\s+\S+", output))


@dataclass(frozen=True)
class VaultRecord:
    item_id: str
    sha256: str
    source_kind: str
    provenance_sha256: str
    classification: str
    archived_at: str


class ObsidianVault:
    """Keep raw content in a verified local archive and expose safe Markdown notes."""

    def __init__(
        self, root: Path, *, encryption_verified: Callable[[Path], bool] | None = None
    ) -> None:
        self.root = root
        self.archive_root = root / "private_archive"
        self.notes_root = root / "Obsidian Notes"
        self.database = root / "vault.sqlite"
        self._encryption_verified = encryption_verified

    @classmethod
    def initialize(cls, root: Path, *, encryption_verified) -> ObsidianVault:
        if cls._is_inside_repository(root):
            raise ValueError("A private vault cannot be created inside a repository checkout")
        root.mkdir(parents=True, exist_ok=True)
        if not encryption_verified(root):
            raise EncryptionUnavailable(
                "A verified encrypted Windows location is required before storing private content."
            )
        vault = cls(root, encryption_verified=encryption_verified)
        vault.archive_root.mkdir(exist_ok=True)
        if not encryption_verified(vault.archive_root):
            raise EncryptionUnavailable(
                "The private archive target itself is not verifiably encrypted."
            )
        for folder in ("Inbox", "Sources", "Bills", "Activity", "Receipts"):
            (vault.notes_root / folder).mkdir(parents=True, exist_ok=True)
        render_dashboard_note(vault.notes_root, AdapterRegistry.default())
        with sqlite3.connect(vault.database) as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS records (
                    item_id TEXT PRIMARY KEY,
                    sha256 TEXT UNIQUE NOT NULL,
                    source_kind TEXT NOT NULL,
                    provenance_sha256 TEXT NOT NULL,
                    classification TEXT NOT NULL,
                    archived_at TEXT NOT NULL,
                    deleted_at TEXT
                )
                """
            )
        return vault

    @staticmethod
    def _is_reparse_point(path: Path) -> bool:
        try:
            attributes = os.lstat(path).st_file_attributes
        except OSError:
            return True
        except AttributeError:
            attributes = 0
        return path.is_symlink() or bool(attributes & 0x400)

    @staticmethod
    def _is_inside_repository(root: Path) -> bool:
        candidate = root.resolve(strict=False)
        return any((parent / ".git").exists() for parent in (candidate, *candidate.parents))

    def _assert_private_storage(self) -> None:
        if self._encryption_verified is None:
            raise EncryptionUnavailable("Private writes require a verified encrypted vault.")
        if self._is_inside_repository(self.root):
            raise EncryptionUnavailable("Private storage cannot be located inside a repository checkout.")
        if self._is_reparse_point(self.root) or self._is_reparse_point(self.archive_root):
            raise EncryptionUnavailable("Private storage cannot use a symbolic link or junction.")
        try:
            self.archive_root.resolve(strict=True).relative_to(self.root.resolve(strict=True))
        except (FileNotFoundError, ValueError) as error:
            raise EncryptionUnavailable("Private archive target is outside the vault root.") from error
        if not self._encryption_verified(self.root) or not self._encryption_verified(self.archive_root):
            raise EncryptionUnavailable("Private writes require current EFS verification at the raw target.")

    @property
    def search_database(self) -> Path:
        self._assert_private_storage()
        return self.archive_root / "search.sqlite"

    @property
    def journal_database(self) -> Path:
        self._assert_private_storage()
        return self.archive_root / "journal.sqlite"

    @staticmethod
    def _validate_title(title: str) -> str:
        if "\r" in title or "\n" in title:
            raise ValueError("Source title must be a single line")
        title = title.strip()
        if not title or len(title) > 120:
            raise ValueError("Source title must be between 1 and 120 characters")
        return title

    @staticmethod
    def _validate_classification(classification: str) -> None:
        if classification not in {"restricted", "project_safe"}:
            raise ValueError("Unknown classification")

    @staticmethod
    def _validate_provenance(provenance: SourceProvenance, *, content_sha256: str):
        return AdapterRegistry.default().validate_provenance(
            provenance, content_sha256=content_sha256
        )

    def _preserve_manifest(self, validated) -> None:
        manifest_root = self.archive_root / "manifests"
        manifest_root.mkdir(exist_ok=True)
        destination = manifest_root / f"{validated.manifest_sha256}.json"
        if not destination.exists():
            staged = manifest_root / f".{validated.manifest_sha256}-{uuid.uuid4().hex}.tmp"
            staged.write_bytes(validated.payload)
            staged.replace(destination)

    def _stage_source_file(self, source: Path) -> tuple[Path, str]:
        """Create one encrypted staged copy and hash exactly the bytes that will be promoted."""

        staged = self.archive_root / f".import-{uuid.uuid4().hex}.stage"
        digest = hashlib.sha256()
        try:
            with source.open("rb") as reader, staged.open("xb") as writer:
                for chunk in iter(lambda: reader.read(1024 * 1024), b""):
                    digest.update(chunk)
                    writer.write(chunk)
        except Exception:
            if staged.exists():
                staged.unlink()
            raise
        return staged, digest.hexdigest()

    @staticmethod
    def _digest(content: str) -> str:
        return hashlib.sha256(content.encode("utf-8")).hexdigest()

    @staticmethod
    def _file_digest(source: Path) -> str:
        digest = hashlib.sha256()
        with source.open("rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(chunk)
        return digest.hexdigest()

    def archive_text(
        self, *, title: str, content: str, provenance: SourceProvenance, classification: str
    ) -> VaultRecord:
        self._assert_private_storage()
        safe_title = self._validate_title(title)
        self._validate_classification(classification)
        digest = self._digest(content)
        validated = self._validate_provenance(provenance, content_sha256=digest)
        item_id = f"OBS-{digest[:16]}"
        destination = self.archive_root / f"{digest}.txt"
        staged = self.archive_root / f".text-{uuid.uuid4().hex}.stage"
        promoted = False
        try:
            staged.write_text(content, encoding="utf-8")
            with sqlite3.connect(self.database) as connection:
                connection.execute("BEGIN IMMEDIATE")
                row = connection.execute(
                    "SELECT item_id, sha256, source_kind, provenance_sha256, classification, archived_at "
                    "FROM records WHERE sha256 = ?",
                    (digest,),
                ).fetchone()
                if row:
                    return VaultRecord(*row)
                if destination.exists():
                    raise RuntimeError("Unreconciled raw content exists; recover it before retrying import.")
                archived_at = datetime.now(UTC).isoformat()
                staged.replace(destination)
                promoted = True
                self._preserve_manifest(validated)
                connection.execute(
                    "INSERT INTO records VALUES (?, ?, ?, ?, ?, ?, NULL)",
                    (
                        item_id,
                        digest,
                        validated.source,
                        validated.manifest_sha256,
                        classification,
                        archived_at,
                    ),
                )
        except Exception:
            if promoted and destination.exists():
                destination.unlink()
            raise
        finally:
            if staged.exists():
                staged.unlink()
        record = VaultRecord(
            item_id,
            digest,
            validated.source,
            validated.manifest_sha256,
            classification,
            archived_at,
        )
        self._write_safe_note(title=safe_title, record=record)
        return record

    def archive_file(
        self,
        source: Path,
        *,
        provenance: SourceProvenance,
        approved_roots: tuple[Path, ...],
        classification: str,
    ) -> VaultRecord:
        """Copy an approved source file into the encrypted archive without exposing its body in Markdown."""

        self._assert_private_storage()
        self._validate_classification(classification)
        if not is_allowed_file(source, approved_roots=approved_roots):
            raise ValueError(f"Source is not allowed for import: {source.name}")
        suffix = source.suffix.casefold()
        staged, digest = self._stage_source_file(source)
        destination = self.archive_root / f"{digest}{suffix}"
        promoted = False
        try:
            validated = self._validate_provenance(provenance, content_sha256=digest)
            item_id = f"OBS-{digest[:16]}"
            with sqlite3.connect(self.database) as connection:
                connection.execute("BEGIN IMMEDIATE")
                row = connection.execute(
                    "SELECT item_id, sha256, source_kind, provenance_sha256, classification, archived_at "
                    "FROM records WHERE sha256 = ?",
                    (digest,),
                ).fetchone()
                if row:
                    return VaultRecord(*row)
                if destination.exists():
                    raise RuntimeError("Unreconciled raw content exists; recover it before retrying import.")
                archived_at = datetime.now(UTC).isoformat()
                staged.replace(destination)
                promoted = True
                self._preserve_manifest(validated)
                connection.execute(
                    "INSERT INTO records VALUES (?, ?, ?, ?, ?, ?, NULL)",
                    (
                        item_id,
                        digest,
                        validated.source,
                        validated.manifest_sha256,
                        classification,
                        archived_at,
                    ),
                )
        except Exception:
            if promoted and destination.exists():
                destination.unlink()
            raise
        finally:
            if staged.exists():
                staged.unlink()
        record = VaultRecord(
            item_id,
            digest,
            validated.source,
            validated.manifest_sha256,
            classification,
            archived_at,
        )
        self._write_safe_note(title=source.stem, record=record)
        return record

    def _write_safe_note(self, *, title: str, record: VaultRecord) -> None:
        note = self.notes_root / "Sources" / f"{record.item_id}.md"
        note.write_text(
            "\n".join(
                (
                    "---",
                    f"item_id: {record.item_id}",
                    f"sha256: {record.sha256}",
                    f"source_kind: {record.source_kind}",
                    f"provenance_sha256: {record.provenance_sha256}",
                    f"classification: {record.classification}",
                    f"archived_at: {record.archived_at}",
                    "raw_content: local_encrypted_archive_only",
                    "---",
                    "",
                    f"# {title}",
                    "",
                    "This note deliberately excludes the source body and attachments.",
                )
            )
            + "\n",
            encoding="utf-8",
        )

    def delete(self, item_id: str) -> None:
        """Permanently remove the archived source and retain a content-free deletion receipt."""

        with sqlite3.connect(self.database) as connection:
            row = connection.execute(
                "SELECT item_id, sha256 FROM records WHERE item_id = ? AND deleted_at IS NULL",
                (item_id,),
            ).fetchone()
            if row is None:
                raise KeyError(item_id)
            _, digest = row
            archived_at = datetime.now(UTC).isoformat()
            raw_files = [self.archive_root / digest, *self.archive_root.glob(f"{digest}.*")]
            for raw in raw_files:
                if raw.exists():
                    raw.unlink()
            note = self.notes_root / "Sources" / f"{item_id}.md"
            if note.exists():
                note.unlink()
            connection.execute(
                "UPDATE records SET deleted_at = ? WHERE item_id = ?", (archived_at, item_id)
            )
        (self.notes_root / "Receipts" / f"{item_id}-deleted.md").write_text(
            "\n".join(
                (
                    "---",
                    f"item_id: {item_id}",
                    f"sha256: {digest}",
                    f"deleted_at: {archived_at}",
                    "---",
                    "",
                    "Raw content and the corresponding Obsidian source note were deleted locally.",
                )
            )
            + "\n",
            encoding="utf-8",
        )
