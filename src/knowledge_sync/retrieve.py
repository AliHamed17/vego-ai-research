from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass
from pathlib import Path

from .contracts import KnowledgeRecord


@dataclass(frozen=True)
class ContextPacket:
    records: list[KnowledgeRecord]
    rendered_markdown: str


def build_index(records_root: Path, database: Path) -> None:
    database.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(database) as connection:
        connection.execute("DROP TABLE IF EXISTS records")
        connection.execute(
            "CREATE TABLE records (record_id TEXT PRIMARY KEY, project TEXT, classification TEXT, "
            "source_kind TEXT, source_ref TEXT, sha256 TEXT, summary TEXT, review_state TEXT, publish_target TEXT)"
        )
        for path in sorted(records_root.rglob("*.json")):
            payload = json.loads(path.read_text(encoding="utf-8"))
            record = KnowledgeRecord(**payload)
            connection.execute(
                "INSERT INTO records VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", tuple(record.__dict__.values())
            )


def retrieve(database: Path, *, project: str, query: str, max_records: int) -> ContextPacket:
    terms = [term.lower() for term in query.split() if term]
    with sqlite3.connect(database) as connection:
        rows = connection.execute(
            "SELECT * FROM records WHERE project = ? AND review_state != 'rejected'", (project,)
        ).fetchall()
    records = [KnowledgeRecord(*row) for row in rows]
    ranked = sorted(
        records,
        key=lambda record: sum(term in record.summary.lower() for term in terms),
        reverse=True,
    )[:max_records]
    markdown = "\n".join(
        f"- [{record.record_id}] {record.summary} (source: {record.source_ref}; review: {record.review_state})"
        for record in ranked
    )
    return ContextPacket(records=ranked, rendered_markdown=markdown)
