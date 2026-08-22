from pathlib import Path

from knowledge_sync.ingest import ingest_file
from knowledge_sync.retrieve import build_index, retrieve


def test_retrieval_returns_cited_approved_project_record(tmp_path: Path) -> None:
    source = tmp_path / "decision.md"
    source.write_text("VEGO-AI decision: preserve baseline classifications.", encoding="utf-8")
    records = tmp_path / "records"
    ingest_file(
        source=source,
        records_root=records,
        project="vego-ai",
        classification="internal",
        source_kind="decision_log",
    )
    database = tmp_path / "knowledge.sqlite"

    build_index(records, database)
    packet = retrieve(database, project="vego-ai", query="baseline", max_records=3)

    assert len(packet.records) == 1
    assert packet.records[0].source_ref == "file:decision.md"
    assert "[K-" in packet.rendered_markdown
