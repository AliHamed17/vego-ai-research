from __future__ import annotations

import hashlib
import json
import os
import pathlib
import sys
import warnings
import zipfile
from pathlib import Path

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

from verify_text2uml_airtravel_runtime import verify_pack  # noqa: E402


def _digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _file_row(root: Path, path: Path) -> dict[str, object]:
    return {
        "path": path.relative_to(root).as_posix(),
        "bytes": path.stat().st_size,
        "sha256": _digest(path),
    }


def read_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _write_source_archive(archive: Path, source_root: Path) -> None:
    with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED) as handle:
        for path in sorted(source_root.rglob("*")):
            if path.is_file():
                handle.write(path, path.relative_to(source_root).as_posix())


def _refresh_source_manifest(inputs: dict[str, Path]) -> None:
    source_root = inputs["source_root"]
    archive = inputs["archive"]
    manifest = read_json(inputs["source_manifest"])
    manifest["archive_sha256"] = _digest(archive)
    manifest["source_entries"] = [
        _file_row(source_root, path)
        for path in sorted(source_root.rglob("*"))
        if path.is_file()
    ]
    write_json(inputs["source_manifest"], manifest)


def _refresh_amendment(inputs: dict[str, Path]) -> None:
    source_root = inputs["source_root"]
    runtime_root = inputs["runtime_root"]
    amendment = read_json(inputs["amendment_manifest"])
    runtime_files = []
    for path in sorted(runtime_root.rglob("*")):
        if path.is_file():
            rel = path.relative_to(runtime_root).as_posix()
            source = source_root / rel
            runtime_files.append({
                "source_path": rel,
                "path": rel,
                "bytes": path.stat().st_size,
                "sha256": _digest(path),
                "byte_transformation": "NONE",
                "role": "domain_description" if rel.startswith("domain_description/") else "candidate_model",
            })
            assert source.read_bytes() == path.read_bytes()
    amendment["runtime_files"] = runtime_files
    write_json(inputs["amendment_manifest"], amendment)


def make_verified_inputs(tmp_path: Path) -> dict[str, Path]:
    source_root = tmp_path / "source"
    runtime_root = tmp_path / "runtime"
    reference_root = tmp_path / "reference_only"
    values = {
        "domain_description/description.md": b"AirTravel domain description\n",
        "candidate_models/01_case.txt": b"@startuml\nAlice -> Bob: booking\n@enduml\n",
        "candidate_models/02_case.txt": b"@startuml\nAlice -> Bob: cancel\n@enduml\n",
        "candidate_models/03_case.txt": b"@startuml\nAlice -> Bob: change\n@enduml\n",
        "candidate_models/04_case.txt": b"@startuml\nAlice -> Bob: pay\n@enduml\n",
    }
    for rel, content in values.items():
        for root in (source_root, runtime_root):
            path = root / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(content)
    reference_root.mkdir(exist_ok=True)
    (reference_root / "plantuml_reference.txt").write_bytes(b"reference-only bytes\n")

    archive = tmp_path / "public-airtravel.zip"
    _write_source_archive(archive, source_root)
    source_manifest = tmp_path / "source-manifest.json"
    amendment_manifest = tmp_path / "amendment-manifest.json"
    inputs = {
        "archive": archive,
        "source_root": source_root,
        "source_manifest": source_manifest,
        "amendment_manifest": amendment_manifest,
        "runtime_root": runtime_root,
        "reference_root": reference_root,
    }
    write_json(source_manifest, {
        "archive_sha256": _digest(archive),
        "commit": "public-airtravel-fixture-commit",
        "source_entries": [_file_row(source_root, source_root / rel) for rel in sorted(values)],
    })
    write_json(amendment_manifest, {
        "amendment_version": "text2uml-airtravel-v1.0.2",
        "runtime_files": [],
        "allowed_configuration": {"provider_run_permitted": False},
    })
    _refresh_amendment(inputs)
    return inputs


def test_verified_source_and_five_file_runtime_pass(tmp_path: Path) -> None:
    inputs = make_verified_inputs(tmp_path)

    result = verify_pack(**inputs)

    assert result["status"] == "PASS"
    assert result["source_entries"]["matched"] == 5
    assert result["runtime_pack"]["observed_count"] == 5
    assert result["source_to_runtime"]["byte_identical"] is True


def test_archive_or_mapping_drift_blocks(tmp_path: Path) -> None:
    inputs = make_verified_inputs(tmp_path)
    inputs["archive"].write_bytes(b"changed")
    assert verify_pack(**inputs)["status"] == "BLOCKED"

    inputs = make_verified_inputs(tmp_path)
    amendment = read_json(inputs["amendment_manifest"])
    amendment["runtime_files"].append(dict(amendment["runtime_files"][0]))
    write_json(inputs["amendment_manifest"], amendment)
    assert verify_pack(**inputs)["source_to_runtime"]["byte_identical"] is False


def test_duplicate_archive_member_blocks_even_with_matching_digest(tmp_path: Path) -> None:
    inputs = make_verified_inputs(tmp_path)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", UserWarning)
        with zipfile.ZipFile(inputs["archive"], "a") as handle:
            handle.writestr("candidate_models/01_case.txt", b"@startuml\nduplicate\n@enduml\n")
    _refresh_source_manifest(inputs)

    result = verify_pack(**inputs)

    assert result["status"] == "BLOCKED"
    assert result["source_archive"]["duplicate_members"] == ["candidate_models/01_case.txt"]


@pytest.mark.parametrize("mutation", ["missing", "extra", "mismatched"])
def test_source_entry_drift_blocks(tmp_path: Path, mutation: str) -> None:
    inputs = make_verified_inputs(tmp_path)
    source_root = inputs["source_root"]
    if mutation == "missing":
        (source_root / "candidate_models/04_case.txt").unlink()
    elif mutation == "extra":
        (source_root / "candidate_models/extra.txt").write_bytes(b"unexpected\n")
    else:
        (source_root / "candidate_models/01_case.txt").write_bytes(b"changed source\n")

    result = verify_pack(**inputs)

    assert result["status"] == "BLOCKED"
    assert result["source_entries"]["status"] == "BLOCKED"


def test_missing_or_duplicate_mapping_blocks(tmp_path: Path) -> None:
    inputs = make_verified_inputs(tmp_path)
    amendment = read_json(inputs["amendment_manifest"])
    amendment["runtime_files"] = amendment["runtime_files"][:-1]
    write_json(inputs["amendment_manifest"], amendment)
    assert verify_pack(**inputs)["source_to_runtime"]["status"] == "BLOCKED"

    inputs = make_verified_inputs(tmp_path)
    amendment = read_json(inputs["amendment_manifest"])
    amendment["runtime_files"].append(dict(amendment["runtime_files"][0]))
    write_json(inputs["amendment_manifest"], amendment)
    assert verify_pack(**inputs)["source_to_runtime"]["status"] == "BLOCKED"


@pytest.mark.parametrize("mutation", ["extra", "missing"])
def test_runtime_pack_extra_or_missing_file_blocks(tmp_path: Path, mutation: str) -> None:
    inputs = make_verified_inputs(tmp_path)
    runtime_root = inputs["runtime_root"]
    if mutation == "extra":
        (runtime_root / "candidate_models/extra.txt").write_bytes(b"unexpected\n")
    else:
        (runtime_root / "candidate_models/04_case.txt").unlink()

    result = verify_pack(**inputs)

    assert result["status"] == "BLOCKED"
    assert result["runtime_pack"]["status"] == "BLOCKED"


def test_reference_bytes_block_even_when_source_and_runtime_match(tmp_path: Path) -> None:
    inputs = make_verified_inputs(tmp_path)
    rel = "candidate_models/01_case.txt"
    forbidden = (inputs["reference_root"] / "plantuml_reference.txt").read_bytes()
    (inputs["source_root"] / rel).write_bytes(forbidden)
    (inputs["runtime_root"] / rel).write_bytes(forbidden)
    _write_source_archive(inputs["archive"], inputs["source_root"])
    _refresh_source_manifest(inputs)
    _refresh_amendment(inputs)

    result = verify_pack(**inputs)

    assert result["status"] == "BLOCKED"
    assert result["reference_separation"]["status"] == "BLOCKED"


def test_symlink_or_reparse_path_blocks(tmp_path: Path) -> None:
    inputs = make_verified_inputs(tmp_path)
    target = inputs["source_root"] / "candidate_models/01_case.txt"
    link = inputs["source_root"] / "candidate_models/link.txt"
    try:
        os.symlink(target, link)
    except OSError as exc:
        pytest.skip(f"symlinks unavailable in this environment: {exc}")

    result = verify_pack(**inputs)

    assert result["status"] == "BLOCKED"
    assert result["source_entries"]["status"] == "BLOCKED"


@pytest.mark.parametrize("manifest_name", ["source_manifest", "amendment_manifest"])
def test_empty_manifest_blocks(tmp_path: Path, manifest_name: str) -> None:
    inputs = make_verified_inputs(tmp_path)
    write_json(inputs[manifest_name], {})

    result = verify_pack(**inputs)

    assert result["status"] == "BLOCKED"
