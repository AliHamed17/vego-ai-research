from __future__ import annotations

import hashlib
import sqlite3
import uuid
from dataclasses import dataclass
from datetime import UTC, datetime

from .adapters import AdapterRegistry
from .vault import ObsidianVault


@dataclass(frozen=True)
class InteractionEvent:
    event_id: str
    source: str
    input_sha256: str
    output_sha256: str
    recorded_at: str


class InteractionJournal:
    """Retain local prompt provenance as hashes, never copy prompts to Markdown."""

    def __init__(self, vault: ObsidianVault) -> None:
        self.vault = vault
        self.database = vault.journal_database
        self.notes_root = vault.notes_root
        (self.notes_root / "Activity").mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(self.database) as connection:
            connection.execute(
                "CREATE TABLE IF NOT EXISTS events "
                "(event_id TEXT PRIMARY KEY, source TEXT, input_sha256 TEXT, "
                "output_sha256 TEXT, recorded_at TEXT)"
            )

    @staticmethod
    def _digest(value: str) -> str:
        return hashlib.sha256(value.encode("utf-8")).hexdigest()

    def record(self, *, source: str, user_input: str, output: str) -> InteractionEvent:
        AdapterRegistry.default().validate_source_label(source)
        self.database = self.vault.journal_database
        event = InteractionEvent(
            event_id=str(uuid.uuid4()),
            source=source,
            input_sha256=self._digest(user_input),
            output_sha256=self._digest(output),
            recorded_at=datetime.now(UTC).isoformat(),
        )
        with sqlite3.connect(self.database) as connection:
            connection.execute(
                "INSERT INTO events VALUES (?, ?, ?, ?, ?)",
                (
                    event.event_id,
                    event.source,
                    event.input_sha256,
                    event.output_sha256,
                    event.recorded_at,
                ),
            )
        (self.notes_root / "Activity" / f"{event.event_id}.md").write_text(
            "\n".join(
                (
                    "---",
                    f"event_id: {event.event_id}",
                    f"source: {event.source}",
                    f"input_sha256: {event.input_sha256}",
                    f"output_sha256: {event.output_sha256}",
                    f"recorded_at: {event.recorded_at}",
                    "---",
                    "",
                    "Prompt and response content stay in the encrypted archive or the authorized export.",
                )
            )
            + "\n",
            encoding="utf-8",
        )
        return event
