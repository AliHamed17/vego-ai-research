import hashlib
import importlib
import json
import shutil
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
    return tmp_path / "temporary-repository" / "research-private" / "study1" / "task-3"


@pytest.fixture(autouse=True)
def _approved_private_test_repository(tmp_path, monkeypatch):
    """Use a synthetic local Git repository to exercise the private-root ignore gate."""
    repository_root = tmp_path / "temporary-repository"
    repository_root.mkdir()
    subprocess.run(["git", "init", "-q", str(repository_root)], check=True)
    (repository_root / ".gitignore").write_text("research-private/study1/\n", encoding="utf-8")
    monkeypatch.setattr(_notes_module(), "REPOSITORY_ROOT", repository_root)


def _cli_private_root(tmp_path: Path) -> Path:
    return ROOT / "research-private" / "study1" / f"pytest-{tmp_path.name}"


def _write_synthetic_notes_and_manifest(tmp_path: Path) -> tuple[Path, Path]:
    tmp_path.mkdir(parents=True, exist_ok=True)
    notes = tmp_path / "synthetic-notes.csv"
    notes.write_text(
        "topic,observation\nalpha,synthetic one\nbeta,synthetic two\n", encoding="utf-8"
    )
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


def _write_manifest_for(notes: Path, manifest: Path) -> Path:
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
    return manifest


def _symlink_or_skip(link: Path, target: Path, *, directory: bool = False) -> None:
    try:
        link.symlink_to(target, target_is_directory=directory)
    except OSError as error:
        pytest.skip(f"local symlink creation is unavailable: {error}")


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
        (
            {"source_url": "https://" + "drive.google.com/file/d/synthetic"},
            "development_only",
            None,
            "remote URL",
        ),
        ({}, "evaluation", None, "development_only"),
        ({}, "development_only", "https://" + "drive.google.com/file/d/synthetic", "remote URL"),
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
        module.import_controlled_notes(
            notes, manifest, _private_root(tmp_path), intended_use="development_only"
        )

    _, valid_manifest = _write_synthetic_notes_and_manifest(tmp_path / "valid")
    valid_notes = tmp_path / "valid" / "synthetic-notes.csv"
    with pytest.raises(module.ControlledNotesError, match="research-private.*study1"):
        module.import_controlled_notes(
            valid_notes, valid_manifest, tmp_path / "public-output", intended_use="development_only"
        )


@pytest.mark.parametrize(
    ("manifest_change", "expected_message"),
    [
        ({"unexpected": "synthetic"}, "exactly"),
        ({"metadata": {"uncontrolled": "synthetic"}}, "exactly"),
        ({"schema_version": 1}, "schema_version must be a string"),
        ({"source_hash": "sha256:not-a-valid-hash"}, "source_hash must be a SHA-256"),
        ({"source_classification": []}, "source_classification must be a string"),
        ({"intended_use": {}}, "intended_use must be a string"),
    ],
)
def test_controlled_notes_import_requires_exactly_four_typed_provenance_fields(
    tmp_path, manifest_change, expected_message
):
    """Catches uncontrolled metadata, malformed hashes, and non-string provenance fields."""
    module = _notes_module()
    notes, manifest = _write_synthetic_notes_and_manifest(tmp_path)
    manifest_data = json.loads(manifest.read_text(encoding="utf-8"))
    manifest_data.update(manifest_change)
    manifest.write_text(json.dumps(manifest_data), encoding="utf-8")

    with pytest.raises(module.ControlledNotesError, match=expected_message):
        module.import_controlled_notes(
            notes, manifest, _private_root(tmp_path), intended_use="development_only"
        )


@pytest.mark.parametrize(
    "remote_value", ["drive" + ":notes.csv", "\\" + r"\server\share\notes.csv"]
)
def test_controlled_notes_rejects_uri_and_unc_notes_sources_before_reading(tmp_path, remote_value):
    """Catches URI-like and UNC note sources before the gate tries to open them."""
    module = _notes_module()

    with pytest.raises(module.ControlledNotesError, match="remote"):
        module.import_controlled_notes(
            remote_value,
            tmp_path / "must-not-read.json",
            _private_root(tmp_path),
            intended_use="development_only",
        )


@pytest.mark.parametrize(
    "remote_value", ["file" + ":manifest.json", "\\" + r"\server\share\manifest.json"]
)
def test_controlled_notes_rejects_uri_and_unc_manifests_before_reading(tmp_path, remote_value):
    """Catches URI-like and UNC manifests before the gate tries to open note input."""
    module = _notes_module()

    with pytest.raises(module.ControlledNotesError, match="remote"):
        module.import_controlled_notes(
            tmp_path / "must-not-read.csv",
            remote_value,
            _private_root(tmp_path),
            intended_use="development_only",
        )


@pytest.mark.parametrize("remote_value", ["s3" + ":private-output", "\\" + r"\server\share\output"])
def test_controlled_notes_rejects_uri_and_unc_output_before_reading(tmp_path, remote_value):
    """Catches remote output roots before the gate attempts any source or manifest reads."""
    module = _notes_module()

    with pytest.raises(module.ControlledNotesError, match="remote"):
        module.import_controlled_notes(
            tmp_path / "must-not-read.csv",
            tmp_path / "must-not-read.json",
            remote_value,
            intended_use="development_only",
        )


def test_controlled_notes_rejects_same_name_private_lookalike_outside_repository(tmp_path):
    """Catches a receipt write allowed merely by a matching private-looking path segment."""
    module = _notes_module()
    notes, manifest = _write_synthetic_notes_and_manifest(tmp_path)
    lookalike = tmp_path / "unapproved" / "research-private" / "study1" / "task-3"

    with pytest.raises(module.ControlledNotesError, match="repository.*research-private.*study1"):
        module.import_controlled_notes(notes, manifest, lookalike, intended_use="development_only")


def test_controlled_notes_import_performs_no_network_activity(tmp_path, monkeypatch):
    """Catches a future controlled-notes import that attempts to open a network socket."""
    module = _notes_module()
    notes, manifest = _write_synthetic_notes_and_manifest(tmp_path)

    def _blocked_socket(*_args, **_kwargs):
        raise AssertionError("network access is prohibited")

    monkeypatch.setattr(socket, "socket", _blocked_socket)

    assert (
        module.import_controlled_notes(
            notes, manifest, _private_root(tmp_path), intended_use="development_only"
        )["record_count"]
        == 2
    )


def test_controlled_notes_aborts_if_source_mutates_after_snapshot(tmp_path, monkeypatch):
    """Catches hashing one notes version while parsing or receipting another version."""
    module = _notes_module()
    notes, manifest = _write_synthetic_notes_and_manifest(tmp_path)
    original_read_local_bytes = module.read_local_bytes
    original_write_text = Path.write_text
    mutated = False

    def _read_and_mutate(path: Path, *args, **kwargs) -> bytes:
        nonlocal mutated
        content = original_read_local_bytes(path, *args, **kwargs)
        if path == notes and not mutated:
            mutated = True
            original_write_text(
                path, "topic,observation\ngamma,changed after snapshot\n", encoding="utf-8"
            )
        return content

    monkeypatch.setattr(module, "read_local_bytes", _read_and_mutate)

    with pytest.raises(module.ControlledNotesError, match="changed"):
        module.import_controlled_notes(
            notes, manifest, _private_root(tmp_path), intended_use="development_only"
        )


@pytest.mark.parametrize("constant", ["NaN", "Infinity", "-Infinity", "1e999"])
def test_controlled_notes_rejects_non_standard_json_numeric_constants(
    tmp_path: Path, constant: str
) -> None:
    """Catches non-standard JSON numbers in either controlled JSON boundary."""
    module = _notes_module()
    notes = tmp_path / "synthetic-notes.json"
    notes.write_text('{"score":' + constant + "}", encoding="utf-8")
    manifest = _write_manifest_for(notes, tmp_path / "synthetic-provenance.json")

    with pytest.raises(module.ControlledNotesError, match="non_standard_numeric_constant"):
        module.import_controlled_notes(
            notes, manifest, _private_root(tmp_path), intended_use="development_only"
        )

    provenance_constant = tmp_path / "constant-provenance.json"
    provenance_constant.write_text(constant, encoding="utf-8")
    csv_notes = tmp_path / "synthetic-notes.csv"
    csv_notes.write_text("topic,observation\nalpha,synthetic\n", encoding="utf-8")
    with pytest.raises(module.ControlledNotesError, match="non_standard_numeric_constant"):
        module.import_controlled_notes(
            csv_notes,
            provenance_constant,
            _private_root(tmp_path),
            intended_use="development_only",
        )


def test_controlled_notes_rejects_symlink_source_entry(tmp_path):
    """Catches a controlled source path that redirects outside the selected local file."""
    module = _notes_module()
    notes, manifest = _write_synthetic_notes_and_manifest(tmp_path)
    link = tmp_path / "linked-notes.csv"
    _symlink_or_skip(link, notes)

    with pytest.raises(module.ControlledNotesError, match="symlink|reparse"):
        module.import_controlled_notes(
            link, manifest, _private_root(tmp_path), intended_use="development_only"
        )


def test_controlled_notes_rejects_reparse_point_in_source_parent_component(tmp_path):
    """Catches controlled inputs reached through a redirecting parent directory."""
    module = _notes_module()
    real_parent = tmp_path / "real-parent"
    notes, manifest = _write_synthetic_notes_and_manifest(real_parent)
    linked_parent = tmp_path / "linked-parent"
    _symlink_or_skip(linked_parent, real_parent, directory=True)

    with pytest.raises(module.ControlledNotesError, match="symlink|reparse"):
        module.import_controlled_notes(
            linked_parent / notes.name,
            linked_parent / manifest.name,
            _private_root(tmp_path),
            intended_use="development_only",
        )


def test_controlled_notes_rejects_lexical_receipt_collision_before_write(tmp_path):
    """Catches a notes source being overwritten by its own fixed receipt destination."""
    module = _notes_module()
    output_root = _private_root(tmp_path)
    output_root.mkdir(parents=True)
    receipt = output_root / module.RECEIPT_NAME
    receipt.write_text("topic,observation\nalpha,synthetic\n", encoding="utf-8")
    original = receipt.read_bytes()
    manifest = _write_manifest_for(receipt, tmp_path / "synthetic-provenance.json")

    with pytest.raises(module.ControlledNotesError, match="receipt destination alias"):
        module.import_controlled_notes(
            receipt, manifest, output_root, intended_use="development_only"
        )

    assert receipt.read_bytes() == original


def test_controlled_notes_rejects_resolved_receipt_collision_before_write(tmp_path):
    """Catches a dot-segment source alias targeting the fixed receipt destination."""
    module = _notes_module()
    output_root = _private_root(tmp_path)
    (output_root / "alias").mkdir(parents=True)
    receipt = output_root / module.RECEIPT_NAME
    receipt.write_text("topic,observation\nalpha,synthetic\n", encoding="utf-8")
    original = receipt.read_bytes()
    alias = output_root / "alias" / ".." / module.RECEIPT_NAME
    manifest = _write_manifest_for(receipt, tmp_path / "synthetic-provenance.json")

    with pytest.raises(module.ControlledNotesError, match="receipt destination alias"):
        module.import_controlled_notes(alias, manifest, output_root, intended_use="development_only")

    assert receipt.read_bytes() == original


def test_controlled_notes_rejects_same_file_receipt_collision_before_write(tmp_path):
    """Catches a hard-link alias targeting the fixed receipt destination."""
    module = _notes_module()
    output_root = _private_root(tmp_path)
    output_root.mkdir(parents=True)
    notes = tmp_path / "synthetic-notes.csv"
    notes.write_text("topic,observation\nalpha,synthetic\n", encoding="utf-8")
    receipt = output_root / module.RECEIPT_NAME
    try:
        receipt.hardlink_to(notes)
    except OSError as error:
        pytest.skip(f"local hard-link creation is unavailable: {error}")
    original = receipt.read_bytes()
    manifest = _write_manifest_for(notes, tmp_path / "synthetic-provenance.json")

    with pytest.raises(module.ControlledNotesError, match="receipt destination alias"):
        module.import_controlled_notes(notes, manifest, output_root, intended_use="development_only")

    assert receipt.read_bytes() == original


def test_controlled_notes_rejects_manifest_receipt_collision_before_write(tmp_path):
    """Catches provenance being overwritten when it is the fixed receipt destination."""
    module = _notes_module()
    notes = tmp_path / "synthetic-notes.csv"
    notes.write_text("topic,observation\nalpha,synthetic\n", encoding="utf-8")
    output_root = _private_root(tmp_path)
    output_root.mkdir(parents=True)
    receipt = _write_manifest_for(notes, output_root / module.RECEIPT_NAME)
    original = receipt.read_bytes()

    with pytest.raises(module.ControlledNotesError, match="receipt destination alias"):
        module.import_controlled_notes(
            notes, receipt, output_root, intended_use="development_only"
        )

    assert receipt.read_bytes() == original


def test_controlled_notes_rejects_symlink_receipt_leaf_without_overwriting_target(tmp_path):
    """Catches a private receipt leaf redirecting an atomic write outside the approved root."""
    module = _notes_module()
    notes, manifest = _write_synthetic_notes_and_manifest(tmp_path)
    output_root = _private_root(tmp_path)
    output_root.mkdir(parents=True)
    outside = tmp_path / "outside-receipt.json"
    outside.write_text("outside stays unchanged", encoding="utf-8")
    _symlink_or_skip(output_root / module.RECEIPT_NAME, outside)

    with pytest.raises(module.ControlledNotesError, match="symlink|reparse"):
        module.import_controlled_notes(
            notes, manifest, output_root, intended_use="development_only"
        )

    assert outside.read_text(encoding="utf-8") == "outside stays unchanged"


def test_controlled_notes_cli_requires_development_only_and_prints_safe_summary(tmp_path):
    """Catches a wrapper that omits the intended-use gate or prints sensitive local input details."""
    notes, manifest = _write_synthetic_notes_and_manifest(tmp_path)
    private_root = _cli_private_root(tmp_path)

    try:
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
    finally:
        shutil.rmtree(private_root, ignore_errors=True)
