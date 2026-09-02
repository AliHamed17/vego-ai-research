import hashlib
import importlib
import json
import socket
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
CLI = ROOT / "scripts" / "import_controlled_notes.py"


def _notes_module():
    return importlib.import_module("vego_study1.controlled_notes")


def _private_root(tmp_path: Path) -> Path:
    return tmp_path / "research-private" / "study1" / "task-3"


def _write_synthetic_notes_and_manifest(tmp_path: Path) -> tuple[Path, Path]:
    tmp_path.mkdir(parents=True, exist_ok=True)
    notes = tmp_path / "synthetic-notes.csv"
    notes.write_text("topic,observation\nalpha,synthetic one\nbeta,synthetic two\n", encoding="utf-8")
    manifest = tmp_path / "synthetic-provenance.json"
    manifest.write_text(
        json.dumps(
            {
                "schema_version": "ControlledNotesProvenance-v1",
                "source_hash": "sha256:" + hashlib.sha256(notes.read_bytes()).hexdigest(),
                "source_classification": "controlled_development_only",
                "intended_use": "development_only",
            }
        ),
        encoding="utf-8",
    )
    return notes, manifest


def test_controlled_notes_import_writes_redacted_development_only_receipt(tmp_path):
    """Catches a controlled import that stores note content, source names, or a broader use status."""
    module = _notes_module()
    notes, manifest = _write_synthetic_notes_and_manifest(tmp_path)

    receipt = module.import_controlled_notes(
        notes, manifest, _private_root(tmp_path), intended_use="development_only"
    )
    receipt_text = (_private_root(tmp_path) / "controlled_notes_import.receipt.json").read_text(
        encoding="utf-8"
    )

    assert receipt["schema_version"] == "ControlledNotesImportReceipt-v1"
    assert receipt["status"] == "development_only"
    assert receipt["record_count"] == 2
    assert len(receipt["opaque_record_hashes"]) == 2
    assert receipt["source_hash"] == "sha256:" + hashlib.sha256(notes.read_bytes()).hexdigest()
    assert "synthetic one" not in receipt_text
    assert "synthetic-notes.csv" not in receipt_text
    assert str(notes) not in receipt_text
    assert json.loads(receipt_text) == receipt


@pytest.mark.parametrize(
    ("manifest_change", "intended_use", "source", "expected_message"),
    [
        ({"schema_version": "wrong"}, "development_only", None, "schema_version"),
        ({"source_hash": "sha256:" + "0" * 64}, "development_only", None, "source_hash"),
        ({"source_classification": "public"}, "development_only", None, "source_classification"),
        ({"intended_use": "evaluation"}, "development_only", None, "intended_use"),
        ({"source_url": "https://drive.google.com/file/d/synthetic"}, "development_only", None, "remote URL"),
        ({}, "evaluation", None, "development_only"),
        ({}, "development_only", "https://drive.google.com/file/d/synthetic", "remote URL"),
    ],
)
def test_controlled_notes_import_fails_closed_for_invalid_provenance_or_input(
    tmp_path, manifest_change, intended_use, source, expected_message
):
    """Catches any branch that imports notes without the required local development-only provenance."""
    module = _notes_module()
    notes, manifest = _write_synthetic_notes_and_manifest(tmp_path)
    manifest_data = json.loads(manifest.read_text(encoding="utf-8"))
    manifest_data.update(manifest_change)
    manifest.write_text(json.dumps(manifest_data), encoding="utf-8")

    with pytest.raises(module.ControlledNotesError, match=expected_message):
        module.import_controlled_notes(
            source or notes,
            manifest,
            _private_root(tmp_path),
            intended_use=intended_use,
        )


def test_controlled_notes_import_rejects_bad_json_and_non_private_output(tmp_path):
    """Catches a parser that accepts malformed provenance or writes receipts outside the private zone."""
    module = _notes_module()
    notes, manifest = _write_synthetic_notes_and_manifest(tmp_path)
    manifest.write_text("not JSON", encoding="utf-8")

    with pytest.raises(module.ControlledNotesError, match="valid JSON"):
        module.import_controlled_notes(notes, manifest, _private_root(tmp_path), intended_use="development_only")

    _, valid_manifest = _write_synthetic_notes_and_manifest(tmp_path / "valid")
    valid_notes = tmp_path / "valid" / "synthetic-notes.csv"
    with pytest.raises(module.ControlledNotesError, match="research-private.*study1"):
        module.import_controlled_notes(
            valid_notes, valid_manifest, tmp_path / "public-output", intended_use="development_only"
        )


def test_controlled_notes_import_performs_no_network_activity(tmp_path, monkeypatch):
    """Catches a future controlled-notes import that attempts to open a network socket."""
    module = _notes_module()
    notes, manifest = _write_synthetic_notes_and_manifest(tmp_path)

    def _blocked_socket(*_args, **_kwargs):
        raise AssertionError("network access is prohibited")

    monkeypatch.setattr(socket, "socket", _blocked_socket)

    assert module.import_controlled_notes(
        notes, manifest, _private_root(tmp_path), intended_use="development_only"
    )["record_count"] == 2


def test_controlled_notes_cli_requires_development_only_and_prints_safe_summary(tmp_path):
    """Catches a wrapper that omits the intended-use gate or prints sensitive local input details."""
    notes, manifest = _write_synthetic_notes_and_manifest(tmp_path)
    private_root = _private_root(tmp_path)

    missing_use = subprocess.run(
        [
            sys.executable,
            str(CLI),
            "--notes-source",
            str(notes),
            "--provenance-manifest",
            str(manifest),
            "--private-output-root",
            str(private_root),
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    completed = subprocess.run(
        [
            sys.executable,
            str(CLI),
            "--notes-source",
            str(notes),
            "--provenance-manifest",
            str(manifest),
            "--private-output-root",
            str(private_root),
            "--intended-use",
            "development_only",
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )

    assert missing_use.returncode != 0
    assert completed.returncode == 0, completed.stderr
    assert "development_only" in completed.stdout
    assert str(notes) not in completed.stdout
    assert "synthetic one" not in completed.stdout
