from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from pathlib import Path

_SHA256 = re.compile(r"[0-9a-f]{64}\Z")
_REMOTE_EXPORT_SOURCES = {"gmail", "google_drive", "chatgpt", "claude", "gemini"}
_LOCAL_SOURCES = {"local_folders"}
_AUTHORIZED_EXPORT_SOURCES = {"codex"}


@dataclass(frozen=True)
class SourceProvenance:
    """A local receipt that binds an import to its declared authorization/export method."""

    manifest: Path


@dataclass(frozen=True)
class ValidatedProvenance:
    source: str
    manifest_sha256: str
    payload: bytes


def write_user_authorized_manifest(
    path: Path, *, source: str, method: str, content_sha256: str
) -> SourceProvenance:
    """Write an auditable local authorization receipt after the operator approves an export."""

    if not _SHA256.fullmatch(content_sha256):
        raise ValueError("Manifest content hash must be a SHA-256 value")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(
            {
                "authorized_by": "local_operator",
                "content_sha256": content_sha256,
                "method": method,
                "schema_version": 1,
                "source": source,
            },
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    return SourceProvenance(path)


@dataclass(frozen=True)
class Adapter:
    name: str
    access_mode: str
    state: str


class AdapterRegistry:
    """Describe source integrations without storing credentials or mutating sources."""

    def __init__(self, adapters: tuple[Adapter, ...]) -> None:
        self._adapters = {adapter.name: adapter for adapter in adapters}

    @classmethod
    def default(cls) -> AdapterRegistry:
        remote = tuple(sorted(_REMOTE_EXPORT_SOURCES))
        return cls(
            tuple(Adapter(name, "read_only", "needs_authorization") for name in remote)
            + (
                Adapter("codex", "read_only", "import_ready"),
                Adapter("local_folders", "read_only", "import_ready"),
            )
        )

    def get(self, name: str) -> Adapter:
        return self._adapters[name]

    def all(self) -> tuple[Adapter, ...]:
        return tuple(self._adapters.values())

    def validate_source_label(self, source: str) -> None:
        if source not in self._adapters:
            raise ValueError("Unknown source label")

    def validate_provenance(
        self, provenance: SourceProvenance, *, content_sha256: str
    ) -> ValidatedProvenance:
        """Bind an imported content hash to a local user-authorized export manifest."""

        try:
            payload = provenance.manifest.read_bytes()
            manifest = json.loads(payload)
        except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
            raise ValueError("A readable user-authorized export manifest is required") from error
        expected_keys = {"authorized_by", "content_sha256", "method", "schema_version", "source"}
        if set(manifest) != expected_keys or manifest["schema_version"] != 1:
            raise ValueError("Export manifest schema is invalid")
        source = manifest["source"]
        method = manifest["method"]
        self.validate_source_label(source)
        if manifest["authorized_by"] != "local_operator":
            raise ValueError("Export manifest must record local operator authorization")
        if not _SHA256.fullmatch(manifest["content_sha256"]):
            raise ValueError("Export manifest content hash is invalid")
        if manifest["content_sha256"] != content_sha256:
            raise ValueError("Export manifest content hash does not match the imported content")
        if source in _REMOTE_EXPORT_SOURCES and method != "official_export":
            raise ValueError("Remote sources require official_export provenance")
        if source in _AUTHORIZED_EXPORT_SOURCES and method != "authorized_export":
            raise ValueError("Codex imports require authorized_export provenance")
        if source in _LOCAL_SOURCES and method != "approved_local_root":
            raise ValueError("Local-folder imports require approved_local_root provenance")
        return ValidatedProvenance(source, hashlib.sha256(payload).hexdigest(), payload)
