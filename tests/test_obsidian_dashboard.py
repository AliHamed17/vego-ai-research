from pathlib import Path

from obsidian_brain.adapters import AdapterRegistry
from obsidian_brain.dashboard import render_dashboard_note


def test_dashboard_note_lists_connector_status_without_private_paths(tmp_path: Path) -> None:
    note = render_dashboard_note(tmp_path, AdapterRegistry.default())

    content = note.read_text(encoding="utf-8")
    assert "# Secondary Brain Dashboard" in content
    assert "gmail — needs_authorization — read_only" in content
    assert "Private source bodies stay local" in content
    assert "C:\\" not in content
