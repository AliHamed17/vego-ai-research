from __future__ import annotations

import sqlite3
from dataclasses import dataclass

from .vault import ObsidianVault


@dataclass(frozen=True)
class SearchResult:
    item_id: str
    sha256: str
    title: str


class VaultSearch:
    """Local FTS retrieval; source text never appears in result objects."""

    def __init__(self, vault: ObsidianVault) -> None:
        self.vault = vault
        self.database = vault.search_database
        with sqlite3.connect(self.database) as connection:
            connection.execute(
                "CREATE VIRTUAL TABLE IF NOT EXISTS documents "
                "USING fts5(item_id UNINDEXED, sha256 UNINDEXED, title, text)"
            )

    def index(self, *, item_id: str, sha256: str, title: str, text: str) -> None:
        self.database = self.vault.search_database
        with sqlite3.connect(self.database) as connection:
            connection.execute("DELETE FROM documents WHERE item_id = ?", (item_id,))
            connection.execute(
                "INSERT INTO documents VALUES (?, ?, ?, ?)", (item_id, sha256, title, text)
            )

    def query(self, query: str, *, limit: int = 20) -> list[SearchResult]:
        terms = [term for term in query.replace('"', " ").split() if term]
        if not terms:
            return []
        expression = " AND ".join(f'"{term}"' for term in terms)
        self.database = self.vault.search_database
        with sqlite3.connect(self.database) as connection:
            rows = connection.execute(
                "SELECT item_id, sha256, title FROM documents WHERE documents MATCH ? "
                "ORDER BY rank LIMIT ?",
                (expression, limit),
            ).fetchall()
        return [SearchResult(*row) for row in rows]
