from __future__ import annotations

import importlib.util
import io
import json
import sys
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "find_original_interaction_log.py"
SPEC = importlib.util.spec_from_file_location("find_original_interaction_log", SCRIPT)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


def test_inventory_is_read_only_and_hashes_jsonl(tmp_path: Path) -> None:
    root = tmp_path / "eval_output" / "Cheers"
    root.mkdir(parents=True)
    path = root / "interaction_log.jsonl"
    path.write_text(
        json.dumps(
            {
                "timestamp": "2026-08-01T00:00:00Z",
                "label": "Agent B",
                "model": "test-model",
                "prompt_hash": "abc",
                "response_hash": "def",
                "prompt_length": 10,
                "response_length": 20,
            }
        )
        + "\n",
        encoding="utf-8",
    )
    before = path.read_bytes()
    result = MODULE.inventory([tmp_path])
    assert result["read_only"] is True
    assert result["network_used"] is False
    assert result["raw_content_emitted"] is False
    assert result["candidates"][0]["classification"] == "ORIGINAL_LOG_PROBABLE"
    assert result["candidates"][0]["record_summary"]["logging_mode_inferred"] == "metadata_only"
    assert path.read_bytes() == before


def test_archive_member_is_inspected_without_extraction(tmp_path: Path) -> None:
    archive = tmp_path / "VEGO-AI-eval.zip"
    data = json.dumps({"model": "gpt", "response_raw": "private"}).encode()
    with zipfile.ZipFile(archive, "w") as handle:
        handle.writestr("Cheers/eval_output/interaction_log.jsonl", data)
    result = MODULE.inventory([tmp_path])
    candidates = [item for item in result["candidates"] if item["member"]]
    assert len(candidates) == 1
    assert candidates[0]["archive"] == str(archive)
    assert candidates[0]["record_summary"]["content_nonempty"] is True
    assert not (tmp_path / "Cheers").exists()


def test_non_matching_content_is_not_reported(tmp_path: Path) -> None:
    path = tmp_path / "notes.json"
    path.write_text(json.dumps({"title": "ordinary note"}), encoding="utf-8")
    result = MODULE.inventory([tmp_path])
    assert result["candidate_count"] == 0
