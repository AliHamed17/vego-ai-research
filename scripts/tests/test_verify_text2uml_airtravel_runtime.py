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
PREFIX = f"text2uml-{PUBLIC_AIRTRAVEL_COMMIT}/dataset/AirTravel/"
AUTHORITIES = ROOT / "docs/research/phd-proposal/text2uml-airtravel"
FIRST_SOURCE = "result_one_claude-sonnet-4-6.txt"
FIRST_RUNTIME = "candidate_models/01_result_one_claude-sonnet-4-6.txt"


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


def _write_source_archive(archive: Path, source_root: Path, prefix: str = PREFIX) -> None:
    with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED) as handle:
        handle.writestr(f"text2uml-{PUBLIC_AIRTRAVEL_COMMIT}/", b"")
        handle.writestr(f"text2uml-{PUBLIC_AIRTRAVEL_COMMIT}/dataset/", b"")
        if prefix:
            handle.writestr(prefix, b"")
        handle.writestr(f"text2uml-{PUBLIC_AIRTRAVEL_COMMIT}/LICENSE", b"synthetic license")
        for path in sorted(source_root.rglob("*")):
            if path.is_file():
                handle.write(path, prefix + path.relative_to(source_root).as_posix())


def _refresh_source_manifest(inputs: dict[str, Path]) -> None:
    source_root = inputs["source_root"]
    manifest = read_json(inputs["source_manifest"])
    original_rows = {row["path"]: row for row in manifest["files"]}
    manifest["files"] = [
        {
            **original_rows.get(path.relative_to(source_root).as_posix(), {}),
            **_file_row(source_root, path),
        }
        for path in sorted(source_root.rglob("*")) if path.is_file()
    ]
    write_json(inputs["source_manifest"], manifest)


def _refresh_amendment(inputs: dict[str, Path]) -> None:
    runtime_root = inputs["runtime_root"]
    amendment = read_json(inputs["amendment_manifest"])
    for row in amendment["runtime_files"]:
        row.update(_file_row(runtime_root, runtime_root / row["path"]))
    by_runtime = {row["path"]: row for row in amendment["runtime_files"]}
    for row in amendment["source_to_runtime_mapping"]:
        row.update({key: by_runtime[row["runtime_path"]][key] for key in ("bytes", "sha256")})
    for row in amendment["excluded_references"]:
        path = inputs["reference_root"] / row["path"].removeprefix("reference_only/")
        row.update({"bytes": path.stat().st_size, "sha256": _digest(path)})
    write_json(inputs["amendment_manifest"], amendment)


def make_verified_inputs(tmp_path: Path) -> dict[str, Path]:
    """Real authority shape/path names, with synthetic engineering bytes only."""
    source_root = tmp_path / "source"
    runtime_root = tmp_path / "runtime"
    reference_root = tmp_path / "reference_only"
    source = read_json(AUTHORITIES / "source-manifest.json")
    amendment = read_json(AUTHORITIES / "amendment-manifest-v1.0.2.json")
    for row in source["files"]:
        path = source_root / row["path"]
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(("ENGINEERING_FIXTURE_NOT_SCIENTIFIC:" + row["path"] + "\n").encode())
    for row in amendment["source_to_runtime_mapping"]:
        path = runtime_root / row["runtime_path"]
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes((source_root / row["source_path"]).read_bytes())
    for row in amendment["excluded_references"]:
        rel = row["path"].removeprefix("reference_only/")
        path = reference_root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes((source_root / rel).read_bytes())

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
    write_json(source_manifest, source)
    write_json(amendment_manifest, amendment)
    _refresh_source_manifest(inputs)
    _refresh_amendment(inputs)
    return inputs


def _verify_synthetic_public_pack(
    inputs: dict[str, Path], monkeypatch: pytest.MonkeyPatch
) -> dict[str, object]:
    archive = inputs["archive"]

    def archive_authority_digest(path: Path) -> str:
        return PUBLIC_AIRTRAVEL_ARCHIVE_SHA256 if path == archive else _digest(path)

    monkeypatch.setattr(verifier, "sha256", archive_authority_digest)
    return verify_pack(**inputs)


def test_verified_source_and_five_file_runtime_pass(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    inputs = make_verified_inputs(tmp_path)

    result = _verify_synthetic_public_pack(inputs, monkeypatch)

    assert result["status"] == "PASS"
    assert result["source_entries"]["matched"] == 143
    assert result["runtime_pack"]["observed_count"] == 5
    assert result["source_to_runtime"]["byte_identical"] is True
    assert result["source_archive"]["expected_sha256"] == PUBLIC_AIRTRAVEL_ARCHIVE_SHA256
    assert result["source_archive"]["expected_commit"] == PUBLIC_AIRTRAVEL_COMMIT
    assert result["source_archive"]["selected_prefix"] == PREFIX
    assert result["source_archive"]["observed_count"] == 143
    assert result["reference_separation"]["reference_count"] == 3
    assert result["reference_separation"]["declared_reference_match"] is True


def test_self_consistent_mutable_source_authority_still_blocks(tmp_path: Path) -> None:
    inputs = make_verified_inputs(tmp_path)
    source_manifest = read_json(inputs["source_manifest"])
    source_manifest["archive_sha256"] = _digest(inputs["archive"])
    source_manifest["upstream_commit"] = "substituted-commit"
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
    amendment["source_to_runtime_mapping"].append(dict(amendment["source_to_runtime_mapping"][0]))
    write_json(inputs["amendment_manifest"], amendment)
    assert verify_pack(**inputs)["source_to_runtime"]["byte_identical"] is False


def test_duplicate_archive_member_blocks_even_with_matching_digest(
    tmp_path: Path, monkeypatch
) -> None:
    inputs = make_verified_inputs(tmp_path)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", UserWarning)
        with zipfile.ZipFile(inputs["archive"], "a") as handle:
            handle.writestr(PREFIX + FIRST_SOURCE, b"@startuml\nduplicate\n@enduml\n")
    _refresh_source_manifest(inputs)

    result = _verify_synthetic_public_pack(inputs, monkeypatch)

    assert result["status"] == "BLOCKED"
    assert result["source_archive"]["duplicate_members"] == [PREFIX + FIRST_SOURCE]


@pytest.mark.parametrize("mutation", ["missing", "extra", "mismatched"])
def test_source_entry_drift_blocks(tmp_path: Path, mutation: str) -> None:
    inputs = make_verified_inputs(tmp_path)
    source_root = inputs["source_root"]
    if mutation == "missing":
        (source_root / FIRST_SOURCE).unlink()
    elif mutation == "extra":
        (source_root / "extra.txt").write_bytes(b"unexpected\n")
    else:
        (source_root / FIRST_SOURCE).write_bytes(b"changed source\n")

    result = verify_pack(**inputs)

    assert result["status"] == "BLOCKED"
    assert result["source_entries"]["status"] == "BLOCKED"


def test_missing_or_duplicate_mapping_blocks(tmp_path: Path) -> None:
    inputs = make_verified_inputs(tmp_path)
    amendment = read_json(inputs["amendment_manifest"])
    amendment["source_to_runtime_mapping"] = amendment["source_to_runtime_mapping"][:-1]
    write_json(inputs["amendment_manifest"], amendment)
    assert verify_pack(**inputs)["source_to_runtime"]["status"] == "BLOCKED"

    inputs = make_verified_inputs(tmp_path)
    amendment = read_json(inputs["amendment_manifest"])
    amendment["source_to_runtime_mapping"].append(dict(amendment["source_to_runtime_mapping"][0]))
    write_json(inputs["amendment_manifest"], amendment)
    assert verify_pack(**inputs)["source_to_runtime"]["status"] == "BLOCKED"


@pytest.mark.parametrize("mutation", ["extra", "missing"])
def test_runtime_pack_extra_or_missing_file_blocks(tmp_path: Path, mutation: str) -> None:
    inputs = make_verified_inputs(tmp_path)
    runtime_root = inputs["runtime_root"]
    if mutation == "extra":
        (runtime_root / "candidate_models/extra.txt").write_bytes(b"unexpected\n")
    else:
        (runtime_root / FIRST_RUNTIME).unlink()

    result = verify_pack(**inputs)

    assert result["status"] == "BLOCKED"
    assert result["runtime_pack"]["status"] == "BLOCKED"


def test_reference_bytes_block_even_when_source_and_runtime_match(tmp_path: Path) -> None:
    inputs = make_verified_inputs(tmp_path)
    forbidden = (inputs["reference_root"] / "plantuml.txt").read_bytes()
    (inputs["source_root"] / FIRST_SOURCE).write_bytes(forbidden)
    (inputs["runtime_root"] / FIRST_RUNTIME).write_bytes(forbidden)
    _write_source_archive(inputs["archive"], inputs["source_root"])
    _refresh_source_manifest(inputs)
    _refresh_amendment(inputs)

    result = verify_pack(**inputs)

    assert result["status"] == "BLOCKED"
    assert result["reference_separation"]["status"] == "BLOCKED"


def test_symlink_or_reparse_path_blocks(tmp_path: Path) -> None:
    inputs = make_verified_inputs(tmp_path)
    target = inputs["source_root"] / FIRST_SOURCE
    link = inputs["source_root"] / "link.txt"
    try:
        os.symlink(target, link)
    except OSError as exc:
        pytest.skip(f"symlinks unavailable in this environment: {exc}")

    result = verify_pack(**inputs)

    assert result["status"] == "BLOCKED"
    assert result["source_entries"]["status"] == "BLOCKED"


@pytest.mark.parametrize("manifest_name", ["source_manifest", "amendment_manifest"])
def test_empty_manifest_blocks(tmp_path: Path, manifest_name: str, monkeypatch) -> None:
    inputs = make_verified_inputs(tmp_path)
    write_json(inputs[manifest_name], {})

    result = _verify_synthetic_public_pack(inputs, monkeypatch)

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
    tmp_path: Path, manifest_name: str, row_key: str, value: object, monkeypatch
) -> None:
    inputs = make_verified_inputs(tmp_path)
    manifest = read_json(inputs[manifest_name])
    rows = (
        manifest["files"]
        if manifest_name == "source_manifest"
        else manifest["source_to_runtime_mapping"]
    )
    if row_key == "row":
        rows[0] = value
    else:
        rows[0][row_key] = value
    write_json(inputs[manifest_name], manifest)

    result = _verify_synthetic_public_pack(inputs, monkeypatch)

    assert result["status"] == "BLOCKED"


def test_source_entry_boolean_byte_length_blocks_for_one_byte_content(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    inputs = make_verified_inputs(tmp_path)
    source_file = inputs["source_root"] / FIRST_SOURCE
    source_file.write_bytes(b"x")
    _write_source_archive(inputs["archive"], inputs["source_root"])
    _refresh_source_manifest(inputs)
    source_manifest = read_json(inputs["source_manifest"])
    source_entries = source_manifest["files"]
    source_entry = next(entry for entry in source_entries if entry["path"] == FIRST_SOURCE)
    source_entry["bytes"] = True
    write_json(inputs["source_manifest"], source_manifest)

    result = _verify_synthetic_public_pack(inputs, monkeypatch)

    assert result["status"] == "BLOCKED"
    assert result["source_entries"]["status"] == "BLOCKED"


def test_mapping_boolean_byte_length_blocks_for_one_byte_content(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    inputs = make_verified_inputs(tmp_path)
    relative_path = FIRST_RUNTIME
    (inputs["source_root"] / FIRST_SOURCE).write_bytes(b"x")
    (inputs["runtime_root"] / relative_path).write_bytes(b"x")
    _write_source_archive(inputs["archive"], inputs["source_root"])
    _refresh_source_manifest(inputs)
    _refresh_amendment(inputs)
    amendment = read_json(inputs["amendment_manifest"])
    runtime_files = amendment["source_to_runtime_mapping"]
    mapping = next(entry for entry in runtime_files if entry["runtime_path"] == relative_path)
    mapping["bytes"] = True
    write_json(inputs["amendment_manifest"], amendment)

    result = _verify_synthetic_public_pack(inputs, monkeypatch)

    assert result["status"] == "BLOCKED"
    assert result["source_to_runtime"]["status"] == "BLOCKED"


def test_runtime_symlink_or_equivalent_reparse_blocks(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    inputs = make_verified_inputs(tmp_path)
    runtime_file = inputs["runtime_root"] / FIRST_RUNTIME
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
    assert (
        fallback_used
        or "candidate_models/runtime-link.txt" in result["runtime_pack"]["unsafe_paths"]
    )


@pytest.mark.parametrize(
    "prefix",
    [
        "",
        "dataset/AirTravel/",
        f"text2uml-{'f' * 40}/dataset/AirTravel/",
        PREFIX.replace("AirTravel", "airtravel"),
    ],
)
def test_wrong_archive_prefix_is_not_an_airtravel_pack(tmp_path, monkeypatch, prefix):
    inputs = make_verified_inputs(tmp_path)
    _write_source_archive(inputs["archive"], inputs["source_root"], prefix)
    assert (
        _verify_synthetic_public_pack(inputs, monkeypatch)["source_archive"]["status"] == "BLOCKED"
    )


@pytest.mark.parametrize(
    "mutation", ["missing", "extra", "mismatched", "shadow", "wrong_root", "symlink"]
)
def test_archive_member_drift_and_nonselected_ambiguity_block(tmp_path, monkeypatch, mutation):
    inputs = make_verified_inputs(tmp_path)
    with zipfile.ZipFile(inputs["archive"]) as handle:
        members = [(item, handle.read(item)) for item in handle.infolist()]
    target = PREFIX + FIRST_SOURCE
    with zipfile.ZipFile(inputs["archive"], "w") as handle:
        for item, data in members:
            if item.filename == target and mutation == "missing":
                continue
            if item.filename == target and mutation == "mismatched":
                data = b"changed"
            if item.filename == target and mutation == "symlink":
                item.create_system = 3
                item.external_attr = 0o120777 << 16
            handle.writestr(item, data)
        if mutation == "extra":
            handle.writestr(PREFIX + "extra.txt", b"extra")
        elif mutation == "shadow":
            handle.writestr(PREFIX.replace("AirTravel", "airtravel") + FIRST_SOURCE, b"shadow")
        elif mutation == "wrong_root":
            handle.writestr("other-root/dataset/AirTravel/" + FIRST_SOURCE, b"shadow")
    result = _verify_synthetic_public_pack(inputs, monkeypatch)
    assert result["source_archive"]["status"] == "BLOCKED"


@pytest.mark.parametrize(
    "mutation",
    [
        "omitted",
        "empty",
        "missing_file",
        "mismatched",
        "extra",
        "missing_declaration",
        "unbound_declaration",
        "within_runtime",
    ],
)
def test_reference_separation_requires_declared_verified_references(
    tmp_path, monkeypatch, mutation
):
    inputs = make_verified_inputs(tmp_path)
    if mutation == "omitted":
        inputs.pop("reference_root")
    elif mutation == "empty":
        empty = tmp_path / "empty"
        empty.mkdir()
        inputs["reference_root"] = empty
    elif mutation == "within_runtime":
        inputs["reference_root"] = inputs["runtime_root"]
    elif mutation in ("missing_file", "mismatched", "extra"):
        target = inputs["reference_root"] / "plantuml.txt"
        if mutation == "missing_file":
            target.unlink()
        elif mutation == "mismatched":
            target.write_bytes(b"different")
        else:
            (inputs["reference_root"] / "extra.txt").write_bytes(b"extra")
    else:
        amendment = read_json(inputs["amendment_manifest"])
        if mutation == "missing_declaration":
            amendment.pop("excluded_references")
        else:
            amendment["excluded_references"][0]["sha256"] = "e" * 64
        write_json(inputs["amendment_manifest"], amendment)
    assert (
        _verify_synthetic_public_pack(inputs, monkeypatch)["reference_separation"]["status"]
        == "BLOCKED"
    )


@pytest.mark.parametrize(
    "mutation",
    [
        "old_source_layout",
        "old_amendment_layout",
        "version",
        "wrong_setting",
        "wrong_corpus",
        "bool_N",
        "transformation",
        "source_duplicate",
        "runtime_duplicate",
    ],
)
def test_alternative_or_malformed_authorities_fail_closed(tmp_path, monkeypatch, mutation):
    inputs = make_verified_inputs(tmp_path)
    source = read_json(inputs["source_manifest"])
    amendment = read_json(inputs["amendment_manifest"])
    if mutation == "old_source_layout":
        source["source_entries"] = source.pop("files")
        source["commit"] = source.pop("upstream_commit")
    elif mutation == "old_amendment_layout":
        amendment.pop("source_to_runtime_mapping")
        amendment["allowed_configuration"] = {"provider_run_permitted": False}
    elif mutation == "version":
        amendment["amendment_version"] = "text2uml-airtravel-v1.0.2"
    elif mutation == "wrong_setting":
        amendment["setting_id"] = "cd_other"
    elif mutation == "wrong_corpus":
        amendment["corpus_id"] = "other"
    elif mutation == "bool_N":
        amendment["N"] = True
    elif mutation == "transformation":
        amendment["source_to_runtime_mapping"][0]["transformation"] = (
            "BYTE_IDENTICAL_RELOCATION_AND_CASE_ID_PREFIX"
        )
    elif mutation == "source_duplicate":
        amendment["source_to_runtime_mapping"][1]["source_path"] = "description.md"
    else:
        amendment["source_to_runtime_mapping"][1]["runtime_path"] = (
            "domain_description/description.md"
        )
    write_json(inputs["source_manifest"], source)
    write_json(inputs["amendment_manifest"], amendment)
    assert _verify_synthetic_public_pack(inputs, monkeypatch)["status"] == "BLOCKED"
