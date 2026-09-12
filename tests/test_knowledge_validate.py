from pathlib import Path

from knowledge_sync.validate import validate_records


def test_validation_rejects_private_drive_identifier(tmp_path: Path) -> None:
    record = tmp_path / "record.json"
    record.write_text('{"summary":"https://drive.google.com/file/d/private-id"}', encoding="utf-8")

    assert validate_records(tmp_path) == ["private identifier found: record.json"]
