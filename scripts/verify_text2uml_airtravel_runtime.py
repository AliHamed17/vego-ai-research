"""Fail-closed verification for a frozen public Text2UML/AirTravel pack.

The verifier only compares supplied bytes and manifests.  It never creates a
model, provider, or API client, and treats incomplete or malformed evidence as
blocking.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import stat
import zipfile
from collections import Counter
from collections.abc import Mapping
from pathlib import Path, PurePosixPath
from typing import Any

SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
RUNTIME_FILE_COUNT = 5


def sha256(path: Path) -> str:
    """Return the SHA-256 digest for one regular file."""
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _blocked(**values: Any) -> dict[str, Any]:
    return {"status": "BLOCKED", **values}


def _is_link_or_reparse(path: Path) -> bool:
    try:
        metadata = path.lstat()
    except OSError:
        return True
    reparse_point = getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0)
    return path.is_symlink() or bool(getattr(metadata, "st_file_attributes", 0) & reparse_point)


def _safe_relative_path(value: object) -> str | None:
    if not isinstance(value, str) or not value:
        return None
    candidate = PurePosixPath(value)
    if candidate.is_absolute() or ".." in candidate.parts or "\\" in value:
        return None
    normalised = candidate.as_posix()
    return normalised if normalised == value and normalised != "." else None


def _row_from_path(root: Path, path: Path) -> dict[str, Any]:
    return {
        "path": path.relative_to(root).as_posix(),
        "bytes": path.stat().st_size,
        "sha256": sha256(path),
    }


def _tree_rows(root: Path) -> tuple[list[dict[str, Any]], list[str]]:
    """Return regular-file rows and unsafe paths without following links."""
    if not root.is_dir() or _is_link_or_reparse(root):
        return [], ["."]
    rows: list[dict[str, Any]] = []
    unsafe: list[str] = []
    try:
        paths = sorted(root.rglob("*"))
    except OSError:
        return [], ["."]
    for path in paths:
        relative = path.relative_to(root).as_posix()
        if _is_link_or_reparse(path):
            unsafe.append(relative)
        elif path.is_file():
            try:
                rows.append(_row_from_path(root, path))
            except OSError:
                unsafe.append(relative)
    return rows, unsafe


def _canonical_rows(rows: object) -> tuple[list[tuple[str, int, str]], list[str]]:
    if not isinstance(rows, list) or not rows:
        return [], ["manifest rows are missing or empty"]
    canonical: list[tuple[str, int, str]] = []
    errors: list[str] = []
    for index, row in enumerate(rows):
        if not isinstance(row, Mapping):
            errors.append(f"row {index} is not an object")
            continue
        path = _safe_relative_path(row.get("path"))
        size = row.get("bytes")
        digest = row.get("sha256")
        if path is None or not isinstance(size, int) or size < 0 or not isinstance(digest, str):
            errors.append(f"row {index} is malformed")
            continue
        digest = digest.lower()
        if not SHA256_RE.fullmatch(digest):
            errors.append(f"row {index} has an invalid SHA-256")
            continue
        canonical.append((path, size, digest))
    paths = [row[0] for row in canonical]
    if len(paths) != len(set(paths)):
        errors.append("duplicate paths in manifest")
    return sorted(canonical), errors


def _canonical_observed(rows: list[dict[str, Any]]) -> list[tuple[str, int, str]]:
    return sorted((row["path"], row["bytes"], row["sha256"]) for row in rows)


def _load_manifest(path: Path) -> Mapping[str, Any] | None:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        return None
    return value if isinstance(value, Mapping) else None


def verify_source_archive(archive: Path, expected_sha256: str, expected_commit: str) -> dict[str, Any]:
    """Return archive digest, commit binding, member inventory, and status."""
    result = _blocked(
        expected_sha256=expected_sha256,
        expected_commit=expected_commit,
        actual_sha256=None,
        member_inventory=[],
        duplicate_members=[],
        commit_binding=False,
    )
    if not archive.is_file() or not isinstance(expected_sha256, str) or not SHA256_RE.fullmatch(expected_sha256.lower()):
        return result
    if not isinstance(expected_commit, str) or not expected_commit.strip():
        return result
    try:
        actual_sha256 = sha256(archive)
        with zipfile.ZipFile(archive) as handle:
            members = [info for info in handle.infolist() if not info.is_dir()]
            member_names = [info.filename for info in members]
            duplicate_members = sorted(name for name, count in Counter(member_names).items() if count > 1)
            invalid_members = [name for name in member_names if _safe_relative_path(name) is None]
            inventory = [
                {"path": info.filename, "bytes": info.file_size, "sha256": hashlib.sha256(handle.read(info)).hexdigest()}
                for info in members
            ]
    except (OSError, zipfile.BadZipFile, RuntimeError, ValueError):
        return result
    digest_matches = actual_sha256 == expected_sha256.lower()
    result.update({
        "actual_sha256": actual_sha256,
        "member_inventory": sorted(inventory, key=lambda row: row["path"]),
        "duplicate_members": duplicate_members,
        "invalid_members": invalid_members,
        "commit_binding": True,
    })
    if digest_matches and not duplicate_members and not invalid_members:
        result["status"] = "PASS"
    return result


def verify_source_entries(source_root: Path, source_manifest: Mapping[str, Any]) -> dict[str, Any]:
    """Compare every expected source entry by path, byte length, and digest."""
    expected, errors = _canonical_rows(source_manifest.get("source_entries"))
    observed_rows, unsafe_paths = _tree_rows(source_root)
    observed = _canonical_observed(observed_rows)
    matched = sum(1 for row in expected if row in observed)
    result = _blocked(
        expected_count=len(expected),
        observed_count=len(observed),
        matched=matched,
        unsafe_paths=unsafe_paths,
        manifest_errors=errors,
    )
    if not errors and not unsafe_paths and expected == observed:
        result["status"] = "PASS"
    return result


def verify_source_to_runtime_mapping(
    source_root: Path, runtime_root: Path, amendment: Mapping[str, Any]
) -> dict[str, Any]:
    """Require exactly five unique, byte-identical source-to-runtime mappings."""
    rows = amendment.get("runtime_files")
    errors: list[str] = []
    comparisons: list[dict[str, Any]] = []
    source_paths: list[str] = []
    runtime_paths: list[str] = []
    if not isinstance(rows, list) or len(rows) != RUNTIME_FILE_COUNT:
        errors.append("runtime_files must contain exactly five mappings")
        rows = rows if isinstance(rows, list) else []
    for index, row in enumerate(rows):
        if not isinstance(row, Mapping):
            errors.append(f"mapping {index} is not an object")
            continue
        source_path = _safe_relative_path(row.get("source_path"))
        runtime_path = _safe_relative_path(row.get("path"))
        declared_size = row.get("bytes")
        declared_digest = row.get("sha256")
        transformation = row.get("byte_transformation")
        if (
            source_path is None
            or runtime_path is None
            or not isinstance(declared_size, int)
            or declared_size < 0
            or not isinstance(declared_digest, str)
            or not SHA256_RE.fullmatch(declared_digest.lower())
            or transformation != "NONE"
        ):
            errors.append(f"mapping {index} is malformed")
            continue
        source_paths.append(source_path)
        runtime_paths.append(runtime_path)
        source = source_root / source_path
        runtime = runtime_root / runtime_path
        identical = False
        if (
            source.is_file()
            and runtime.is_file()
            and not _is_link_or_reparse(source)
            and not _is_link_or_reparse(runtime)
        ):
            try:
                source_digest = sha256(source)
                runtime_digest = sha256(runtime)
                identical = (
                    source.stat().st_size == runtime.stat().st_size == declared_size
                    and source_digest == runtime_digest == declared_digest.lower()
                )
            except OSError:
                identical = False
        comparisons.append({"source_path": source_path, "path": runtime_path, "byte_identical": identical})
    if len(source_paths) != len(set(source_paths)):
        errors.append("duplicate source mapping path")
    if len(runtime_paths) != len(set(runtime_paths)):
        errors.append("duplicate runtime mapping path")
    if sum(path.startswith("domain_description/") for path in source_paths) != 1:
        errors.append("mappings must contain one domain description source")
    if sum(path.startswith("candidate_models/") for path in source_paths) != 4:
        errors.append("mappings must contain four candidate model sources")
    if sum(path.startswith("domain_description/") for path in runtime_paths) != 1:
        errors.append("mappings must contain one domain description runtime path")
    if sum(path.startswith("candidate_models/") for path in runtime_paths) != 4:
        errors.append("mappings must contain four candidate model runtime paths")
    byte_identical = not errors and len(comparisons) == RUNTIME_FILE_COUNT and all(
        comparison["byte_identical"] for comparison in comparisons
    )
    return {
        "status": "PASS" if byte_identical else "BLOCKED",
        "byte_identical": byte_identical,
        "mapping_count": len(comparisons),
        "errors": errors,
        "mappings": comparisons,
    }


def verify_runtime_pack(runtime_root: Path, amendment: Mapping[str, Any]) -> dict[str, Any]:
    """Require the exact five runtime files and a restrictive configuration."""
    expected, errors = _canonical_rows(amendment.get("runtime_files"))
    observed_rows, unsafe_paths = _tree_rows(runtime_root)
    observed = _canonical_observed(observed_rows)
    configuration = amendment.get("allowed_configuration")
    allowed_configuration = (
        isinstance(configuration, Mapping)
        and configuration.get("provider_run_permitted") is False
    )
    if len(expected) != RUNTIME_FILE_COUNT:
        errors.append("runtime manifest must contain exactly five files")
    result = _blocked(
        expected_count=len(expected),
        observed_count=len(observed),
        unsafe_paths=unsafe_paths,
        manifest_errors=errors,
        allowed_configuration=allowed_configuration,
    )
    if not errors and not unsafe_paths and allowed_configuration and expected == observed:
        result["status"] = "PASS"
    return result


def _verify_reference_separation(runtime_root: Path, reference_root: Path | None) -> dict[str, Any]:
    if reference_root is None:
        return _blocked(reason="reference root was not supplied")
    reference_rows, unsafe_paths = _tree_rows(reference_root)
    if unsafe_paths:
        return _blocked(unsafe_paths=unsafe_paths)
    runtime_rows, runtime_unsafe = _tree_rows(runtime_root)
    if runtime_unsafe:
        return _blocked(unsafe_paths=runtime_unsafe)
    reference_bytes = {(row["bytes"], row["sha256"]) for row in reference_rows}
    leaked_paths = [
        row["path"] for row in runtime_rows if (row["bytes"], row["sha256"]) in reference_bytes
    ]
    return {
        "status": "PASS" if not leaked_paths else "BLOCKED",
        "reference_count": len(reference_rows),
        "leaked_paths": leaked_paths,
    }


def verify_pack(
    archive: Path,
    source_root: Path,
    source_manifest: Path,
    amendment_manifest: Path,
    runtime_root: Path,
    reference_root: Path | None = None,
) -> dict[str, Any]:
    """Verify source/archive/runtime evidence and fail closed on every anomaly."""
    source = _load_manifest(source_manifest)
    amendment = _load_manifest(amendment_manifest)
    if source is None or amendment is None:
        return {
            "status": "BLOCKED",
            "source_archive": _blocked(reason="manifest parsing failed"),
            "source_entries": _blocked(reason="manifest parsing failed"),
            "source_to_runtime": _blocked(byte_identical=False, reason="manifest parsing failed"),
            "runtime_pack": _blocked(reason="manifest parsing failed"),
            "reference_separation": _blocked(reason="manifest parsing failed"),
        }
    source_archive = verify_source_archive(
        archive,
        source.get("archive_sha256", ""),
        source.get("commit", ""),
    )
    source_entries = verify_source_entries(source_root, source)
    expected_entries, entry_errors = _canonical_rows(source.get("source_entries"))
    archive_entries, archive_errors = _canonical_rows(source_archive.get("member_inventory"))
    if entry_errors or archive_errors or expected_entries != archive_entries:
        source_archive["status"] = "BLOCKED"
        source_archive["inventory_matches_manifest"] = False
    else:
        source_archive["inventory_matches_manifest"] = True
    source_to_runtime = verify_source_to_runtime_mapping(source_root, runtime_root, amendment)
    runtime_pack = verify_runtime_pack(runtime_root, amendment)
    reference_separation = _verify_reference_separation(runtime_root, reference_root)
    checks = (source_archive, source_entries, source_to_runtime, runtime_pack, reference_separation)
    return {
        "status": "PASS" if all(check["status"] == "PASS" for check in checks) else "BLOCKED",
        "provider_call_made": False,
        "source_archive": source_archive,
        "source_entries": source_entries,
        "source_to_runtime": source_to_runtime,
        "runtime_pack": runtime_pack,
        "reference_separation": reference_separation,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--archive", type=Path, required=True)
    parser.add_argument("--source-root", type=Path, required=True)
    parser.add_argument("--source-manifest", type=Path, required=True)
    parser.add_argument("--amendment-manifest", type=Path, required=True)
    parser.add_argument("--runtime-root", type=Path, required=True)
    parser.add_argument("--reference-root", type=Path, required=True)
    parser.add_argument("--receipt", type=Path)
    args = parser.parse_args()
    receipt = args.receipt
    result = verify_pack(
        archive=args.archive,
        source_root=args.source_root,
        source_manifest=args.source_manifest,
        amendment_manifest=args.amendment_manifest,
        runtime_root=args.runtime_root,
        reference_root=args.reference_root,
    )
    if receipt:
        receipt.parent.mkdir(parents=True, exist_ok=True)
        receipt.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["status"] == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
