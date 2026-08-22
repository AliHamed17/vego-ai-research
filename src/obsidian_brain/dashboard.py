from __future__ import annotations

from pathlib import Path

from .adapters import AdapterRegistry


def render_dashboard_note(notes_root: Path, registry: AdapterRegistry) -> Path:
    """Write the Obsidian landing note with connector states, not private data."""

    notes_root.mkdir(parents=True, exist_ok=True)
    note = notes_root / "Secondary Brain Dashboard.md"
    connectors = "\n".join(
        f"- {adapter.name} — {adapter.state} — {adapter.access_mode}"
        for adapter in registry.all()
    )
    note.write_text(
        "\n".join(
            (
                "# Secondary Brain Dashboard",
                "",
                "Private source bodies stay local in the verified encrypted archive.",
                "Connectors are read-only; no sending, sharing, deletion, payment, or cloud sync is enabled.",
                "",
                "## Connector status",
                connectors,
                "",
                "## Obsidian folders",
                "- [[Inbox]]",
                "- [[Sources]]",
                "- [[Bills]]",
                "- [[Activity]]",
                "- [[Receipts]]",
            )
        )
        + "\n",
        encoding="utf-8",
    )
    return note
