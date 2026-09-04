from __future__ import annotations

import zipfile
from pathlib import Path

import pytest

from scripts.audit_historical_case_recovery_v3 import (
    _load_rows,
    _normalize_model_path,
    audit,
)


def test_phase_c_loader_stops_at_first_completed_block() -> None:
    log = (
        b"=== Phase C: Case Model Scoring ===\n"
        b"Loaded case model '100' from redacted.txt (123 chars)\n"
        b"Loaded case model '100' from redacted_2.txt (123 chars)\n"
        b"Phase C - loaded 2 case model(s)\n"
        b"Loaded case model '999' from later.txt (1 chars)\n"
    )
    assert _load_rows(log) == [
        {"case_id": "100", "logged_chars": 123},
        {"case_id": "100", "logged_chars": 123},
    ]


def test_nested_model_path_normalizes_without_emitting_content() -> None:
    assert _normalize_model_path("VEGO-AI/System/models/UCD_PW_models/sub/100_UCD_PW.txt") == "VEGO-AI/models/UCD_PW_models/sub/100_UCD_PW.txt"


def test_backup_hash_mismatch_fails_closed(tmp_path: Path) -> None:
    backup = tmp_path / "backup.zip"
    with zipfile.ZipFile(backup, "w"):
        pass
    with pytest.raises(ValueError, match="SHA-256 mismatch"):
        audit(backup)
