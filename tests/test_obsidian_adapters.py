from hashlib import sha256
from pathlib import Path

import pytest

from obsidian_brain.adapters import (
    AdapterRegistry,
    write_user_authorized_manifest,
)


def test_remote_connectors_are_read_only_and_require_user_authorization() -> None:
    registry = AdapterRegistry.default()

    for connector in ("gmail", "google_drive", "chatgpt", "claude", "gemini"):
        adapter = registry.get(connector)
        assert adapter.access_mode == "read_only"
        assert adapter.state == "needs_authorization"


def test_remote_content_requires_an_official_export_provenance_receipt(tmp_path: Path) -> None:
    registry = AdapterRegistry.default()
    content = b"authorized export"
    direct_manifest = write_user_authorized_manifest(
        tmp_path / "direct.json",
        source="gmail",
        method="direct_api",
        content_sha256=sha256(content).hexdigest(),
    )
    export_manifest = write_user_authorized_manifest(
        tmp_path / "official-export.json",
        source="gmail",
        method="official_export",
        content_sha256=sha256(content).hexdigest(),
    )

    with pytest.raises(ValueError, match="official_export"):
        registry.validate_provenance(direct_manifest, content_sha256=sha256(content).hexdigest())
    registry.validate_provenance(export_manifest, content_sha256=sha256(content).hexdigest())
    with pytest.raises(ValueError, match="content hash"):
        registry.validate_provenance(export_manifest, content_sha256="b" * 64)
