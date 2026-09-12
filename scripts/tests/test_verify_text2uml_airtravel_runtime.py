from __future__ import annotations

import hashlib
import importlib
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

verifier = importlib.import_module("verify_text2uml_airtravel_runtime")


PUBLIC_AIRTRAVEL_COMMIT = "253b26dc704d523209a5cba79686f8f7fab57d63"
PUBLIC_AIRTRAVEL_ARCHIVE_SHA256 = "8cf82e2ab2d2ce3da9a7ec4165e760ae1e0d9af14468f5aa2a3883037d8da701"
PUBLIC_AIRTRAVEL_SOURCE_ENTRY_COUNT = 143


verify_pack = verifier.verify_pack


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
    manifest = read_json(inputs["source_manifest"])
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
    values.update({
        f"source_only/{index:03d}.txt": f"synthetic source entry {index}\n".encode()
        for index in range(1, 139)
    })
    for rel, content in values.items():
        roots = (source_root,) if rel.startswith("source_only/") else (source_root, runtime_root)
        for root in roots:
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
        "archive_sha256": PUBLIC_AIRTRAVEL_ARCHIVE_SHA256,
        "commit": PUBLIC_AIRTRAVEL_COMMIT,
        "source_entries": [_file_row(source_root, source_root / rel) for rel in sorted(values)],
    })
    write_json(amendment_manifest, {
        "amendment_version": "text2uml-airtravel-v1.0.2",
        "runtime_files": [],
        "allowed_configuration": {"provider_run_permitted": False},
    })
    _refresh_amendment(inputs)
    return inputs


def _verify_synthetic_public_pack(inputs: dict[str, Path], monkeypatch: pytest.MonkeyPatch) -> dict[str, object]:
    archive = inputs["archive"]

    def archive_authority_digest(path: Path) -> str:
        return PUBLIC_AIRTRAVEL_ARCHIVE_SHA256 if path == archive else _digest(path)

    monkeypatch.setattr(verifier, "sha256", archive_authority_digest)
    return verify_pack(**inputs)


def test_verified_source_and_five_file_runtime_pass(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    inputs = make_verified_inputs(tmp_path)

    result = _verify_synthetic_public_pack(inputs, monkeypatch)

    assert result["status"] == "PASS"
    assert result["source_entries"]["matched"] == 143
    assert result["runtime_pack"]["observed_count"] == 5
    assert result["source_to_runtime"]["byte_identical"] is True
    assert result["source_archive"]["expected_sha256"] == PUBLIC_AIRTRAVEL_ARCHIVE_SHA256
    assert result["source_archive"]["expected_commit"] == PUBLIC_AIRTRAVEL_COMMIT


def test_self_consistent_mutable_source_authority_still_blocks(tmp_path: Path) -> None:
    inputs = make_verified_inputs(tmp_path)
    source_manifest = read_json(inputs["source_manifest"])
    source_manifest["archive_sha256"] = _digest(inputs["archive"])
    source_manifest["commit"] = "substituted-commit"
    write_json(inputs["source_manifest"], source_manifest)

    result = verify_pack(**inputs)

    assert result["status"] == "BLOCKED"
    assert result["source_archive"]["expected_sha256"] == PUBLIC_AIRTRAVEL_ARCHIVE_SHA256
    assert result["source_archive"]["commit_binding"] is False


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


@pytest.mark.parametrize("version", [None, "text2uml-airtravel-v1.0.3"])
def test_amendment_identity_must_match_v102(tmp_path: Path, version: str | None) -> None:
    inputs = make_verified_inputs(tmp_path)
    amendment = read_json(inputs["amendment_manifest"])
    if version is None:
        amendment.pop("amendment_version")
    else:
        amendment["amendment_version"] = version
    write_json(inputs["amendment_manifest"], amendment)

    result = verify_pack(**inputs)

    assert result["status"] == "BLOCKED"
    assert result["runtime_pack"]["status"] == "BLOCKED"


@pytest.mark.parametrize(
    ("manifest_name", "row_key", "value"),
    [
        ("source_manifest", "row", 42),
        ("source_manifest", "sha256", "not-a-digest"),
        ("source_manifest", "path", "../outside.txt"),
        ("amendment_manifest", "byte_transformation", "COPY"),
        ("amendment_manifest", "source_path", "../outside.txt"),
    ],
)
def test_malformed_manifest_rows_or_fields_block(
    tmp_path: Path, manifest_name: str, row_key: str, value: object
) -> None:
    inputs = make_verified_inputs(tmp_path)
    manifest = read_json(inputs[manifest_name])
    rows = manifest["source_entries"] if manifest_name == "source_manifest" else manifest["runtime_files"]
    if row_key == "row":
        rows[0] = value
    else:
        rows[0][row_key] = value
    write_json(inputs[manifest_name], manifest)

    result = verify_pack(**inputs)

    assert result["status"] == "BLOCKED"


def test_runtime_symlink_or_equivalent_reparse_blocks(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    inputs = make_verified_inputs(tmp_path)
    runtime_file = inputs["runtime_root"] / "candidate_models/01_case.txt"
    link = inputs["runtime_root"] / "candidate_models/runtime-link.txt"
    fallback_used = False
    try:
        os.symlink(runtime_file, link)
    except OSError:
        fallback_used = True
        original = verifier._is_link_or_reparse
        monkeypatch.setattr(
            verifier,
            "_is_link_or_reparse",
            lambda path: path == runtime_file or original(path),
        )

    result = verify_pack(**inputs)

    assert result["status"] == "BLOCKED"
    assert result["runtime_pack"]["status"] == "BLOCKED"
    assert fallback_used or "candidate_models/runtime-link.txt" in result["runtime_pack"]["unsafe_paths"]
