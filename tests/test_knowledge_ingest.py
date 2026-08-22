from pathlib import Path

from knowledge_sync.ingest import ingest_file


def test_restricted_file_creates_reference_without_copying_content(tmp_path: Path) -> None:
    source = tmp_path / "meeting.txt"
    source.write_text("private URL https://example.invalid/secret", encoding="utf-8")
    records = tmp_path / "records"

    record = ingest_file(
        source=source,
        records_root=records,
        project="vego-ai",
        classification="restricted",
        source_kind="meeting_export",
    )

    assert record.source_ref.startswith("restricted:")
    assert "https://" not in record.summary
    assert not list(records.rglob("*.md"))
