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
PUBLIC_AIRTRAVEL_COMMIT = "253b26dc704d523209a5cba79686f8f7fab57d63"
PUBLIC_AIRTRAVEL_ARCHIVE_SHA256 = "8cf82e2ab2d2ce3da9a7ec4165e760ae1e0d9af14468f5aa2a3883037d8da701"
PUBLIC_AIRTRAVEL_SOURCE_ENTRY_COUNT = 143
AIRTRAVEL_AMENDMENT_VERSION = "1.0.2"
PUBLIC_AIRTRAVEL_ARCHIVE_ROOT = f"text2uml-{PUBLIC_AIRTRAVEL_COMMIT}/"
PUBLIC_AIRTRAVEL_ARCHIVE_PREFIX = PUBLIC_AIRTRAVEL_ARCHIVE_ROOT + "dataset/AirTravel/"
FROZEN_SOURCE_RUNTIME_PATHS = (
    ("description.md", "domain_description/description.md"),
    ("result_one_claude-sonnet-4-6.txt", "candidate_models/01_result_one_claude-sonnet-4-6.txt"),
    ("result_one_codestral-2508.txt", "candidate_models/02_result_one_codestral-2508.txt"),
    ("result_one_deepseek-chat.txt", "candidate_models/03_result_one_deepseek-chat.txt"),
    ("result_one_gemini-2.5-flash.txt", "candidate_models/04_result_one_gemini-2.5-flash.txt"),
)
FROZEN_REFERENCE_PATHS = (
    "reference_only/plantuml.txt",
    "reference_only/plantuml_adjusted.txt",
    "reference_only/extramaterial/AirTravel.cd4a",
)


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
    if (
        candidate.is_absolute()
        or ".." in candidate.parts
        or "\\" in value
        or ":" in value
        or any(part.endswith((".", " ")) for part in candidate.parts)
        or any(ord(char) < 32 for char in value)
    ):
        return None
    normalised = candidate.as_posix()
    return normalised if normalised == value and normalised != "." else None


def _is_strict_int(value: object) -> bool:
    return type(value) is int


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
        if path is None or not _is_strict_int(size) or size < 0 or not isinstance(digest, str):
            errors.append(f"row {index} is malformed")
            continue
        digest = digest.lower()
        if not SHA256_RE.fullmatch(digest):
            errors.append(f"row {index} has an invalid SHA-256")
            continue
        canonical.append((path, size, digest))
    paths = [row[0] for row in canonical]
    if len(paths) != len({path.casefold() for path in paths}):
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


def verify_source_archive(
    archive: Path, expected_sha256: str, expected_commit: str
) -> dict[str, Any]:
    """Return archive digest, commit binding, member inventory, and status."""
    result = _blocked(
        expected_sha256=PUBLIC_AIRTRAVEL_ARCHIVE_SHA256,
        expected_commit=PUBLIC_AIRTRAVEL_COMMIT,
        declared_sha256=expected_sha256,
        declared_commit=expected_commit,
        actual_sha256=None,
        member_inventory=[],
        duplicate_members=[],
        invalid_members=[],
        ambiguous_members=[],
        selected_prefix=PUBLIC_AIRTRAVEL_ARCHIVE_PREFIX,
        observed_count=0,
        commit_binding=False,
    )
    authority_matches = (
        expected_sha256 == PUBLIC_AIRTRAVEL_ARCHIVE_SHA256
        and expected_commit == PUBLIC_AIRTRAVEL_COMMIT
    )
    if not archive.is_file() or _is_link_or_reparse(archive) or not authority_matches:
        return result
    try:
        actual_sha256 = sha256(archive)
        result["actual_sha256"] = actual_sha256
        if actual_sha256 != PUBLIC_AIRTRAVEL_ARCHIVE_SHA256:
            return result
        with zipfile.ZipFile(archive) as handle:
            all_members = handle.infolist()
            member_names = [info.filename.rstrip("/") for info in all_members]
            duplicate_members = sorted(
                name for name, count in Counter(member_names).items() if count > 1
            )
            invalid_members = [name for name in member_names if _safe_relative_path(name) is None]
            ambiguous_members = [
                info.filename
                for info in all_members
                if (
                    not info.filename.startswith(PUBLIC_AIRTRAVEL_ARCHIVE_ROOT)
                    or (
                        "/dataset/airtravel/" in info.filename.casefold()
                        and not info.filename.startswith(PUBLIC_AIRTRAVEL_ARCHIVE_PREFIX)
                    )
                )
            ]
            folded = Counter(name.casefold() for name in member_names)
            ambiguous_members.extend(name for name in member_names if folded[name.casefold()] > 1)
            invalid_members.extend(
                info.filename for info in all_members if stat.S_ISLNK(info.external_attr >> 16)
            )
            members = [
                info
                for info in all_members
                if not info.is_dir() and info.filename.startswith(PUBLIC_AIRTRAVEL_ARCHIVE_PREFIX)
            ]
            inventory = [
                {
                    "path": info.filename.removeprefix(PUBLIC_AIRTRAVEL_ARCHIVE_PREFIX),
                    "bytes": info.file_size,
                    "sha256": hashlib.sha256(handle.read(info)).hexdigest(),
                }
                for info in members
            ]
    except (OSError, zipfile.BadZipFile, RuntimeError, ValueError):
        return result
    digest_matches = actual_sha256 == PUBLIC_AIRTRAVEL_ARCHIVE_SHA256
    result.update(
        {
            "actual_sha256": actual_sha256,
            "member_inventory": sorted(inventory, key=lambda row: row["path"]),
            "duplicate_members": duplicate_members,
            "invalid_members": invalid_members,
            "ambiguous_members": sorted(set(ambiguous_members)),
            "observed_count": len(inventory),
            "commit_binding": authority_matches,
        }
    )
    if (
        digest_matches
        and not duplicate_members
        and not invalid_members
        and not ambiguous_members
        and len(inventory) == PUBLIC_AIRTRAVEL_SOURCE_ENTRY_COUNT
    ):
        result["status"] = "PASS"
    return result


def verify_source_entries(source_root: Path, source_manifest: Mapping[str, Any]) -> dict[str, Any]:
    """Compare every expected source entry by path, byte length, and digest."""
    expected, errors = _canonical_rows(source_manifest.get("files"))
    if source_manifest.get("upstream_commit") != PUBLIC_AIRTRAVEL_COMMIT:
        errors.append("source manifest commit mismatch")
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
    if (
        not errors
        and not unsafe_paths
        and len(expected) == PUBLIC_AIRTRAVEL_SOURCE_ENTRY_COUNT
        and expected == observed
    ):
        result["status"] = "PASS"
    return result


def _amendment_identity(amendment: Mapping[str, Any]) -> bool:
    return (
        amendment.get("amendment_version") == AIRTRAVEL_AMENDMENT_VERSION
        and amendment.get("upstream_commit") == PUBLIC_AIRTRAVEL_COMMIT
        and amendment.get("setting_id") == "cd_airtravel"
        and amendment.get("corpus_id") == "text2uml_airtravel_253b26dc"
        and type(amendment.get("N")) is int
        and amendment["N"] == 4
    )


def _runtime_declarations(
    amendment: Mapping[str, Any],
) -> tuple[list[tuple[str, int, str]], list[str]]:
    expected, errors = _canonical_rows(amendment.get("runtime_files"))
    if {row[0] for row in expected} != {row[1] for row in FROZEN_SOURCE_RUNTIME_PATHS}:
        errors.append("runtime paths differ from frozen five-file selection")
    for row in (
        amendment.get("runtime_files", [])
        if isinstance(amendment.get("runtime_files"), list)
        else []
    ):
        if not isinstance(row, Mapping):
            continue
        expected_role = (
            "domain_description"
            if row.get("path") == "domain_description/description.md"
            else "candidate_model"
        )
        if row.get("role") != expected_role:
            errors.append("runtime role mismatch")
    return expected, errors


def verify_source_to_runtime_mapping(
    source_root: Path, runtime_root: Path, amendment: Mapping[str, Any]
) -> dict[str, Any]:
    """Require exactly five unique, byte-identical source-to-runtime mappings."""
    rows = amendment.get("source_to_runtime_mapping")
    declared_runtime, errors = _runtime_declarations(amendment)
    declared_by_path = {path: (size, digest) for path, size, digest in declared_runtime}
    if not _amendment_identity(amendment):
        errors.append("amendment identity mismatch")
    comparisons: list[dict[str, Any]] = []
    source_paths: list[str] = []
    runtime_paths: list[str] = []
    if not isinstance(rows, list) or len(rows) != RUNTIME_FILE_COUNT:
        errors.append("source_to_runtime_mapping must contain exactly five mappings")
        rows = rows if isinstance(rows, list) else []
    for index, row in enumerate(rows):
        if not isinstance(row, Mapping):
            errors.append(f"mapping {index} is not an object")
            continue
        source_path = _safe_relative_path(row.get("source_path"))
        runtime_path = _safe_relative_path(row.get("runtime_path"))
        declared_size = row.get("bytes")
        declared_digest = row.get("sha256")
        transformation = row.get("byte_transformation")
        if (
            source_path is None
            or runtime_path is None
            or not _is_strict_int(declared_size)
            or declared_size < 0
            or not isinstance(declared_digest, str)
            or not SHA256_RE.fullmatch(declared_digest.lower())
            or transformation != "NONE"
            or (source_path, runtime_path) not in FROZEN_SOURCE_RUNTIME_PATHS
            or row.get("transformation")
            != (
                "BYTE_IDENTICAL_RELOCATION"
                if source_path == "description.md"
                else "BYTE_IDENTICAL_RELOCATION_AND_CASE_ID_PREFIX"
            )
            or declared_by_path.get(runtime_path) != (declared_size, declared_digest.lower())
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
        comparisons.append(
            {"source_path": source_path, "path": runtime_path, "byte_identical": identical}
        )
    if len(source_paths) != len(set(source_paths)):
        errors.append("duplicate source mapping path")
    if len(runtime_paths) != len(set(runtime_paths)):
        errors.append("duplicate runtime mapping path")
    if set(zip(source_paths, runtime_paths, strict=True)) != set(FROZEN_SOURCE_RUNTIME_PATHS):
        errors.append("mappings differ from frozen five-file selection")
    byte_identical = (
        not errors
        and len(comparisons) == RUNTIME_FILE_COUNT
        and all(comparison["byte_identical"] for comparison in comparisons)
    )
    return {
        "status": "PASS" if byte_identical else "BLOCKED",
        "byte_identical": byte_identical,
        "mapping_count": len(comparisons),
        "errors": errors,
        "mappings": comparisons,
    }


def verify_runtime_pack(runtime_root: Path, amendment: Mapping[str, Any]) -> dict[str, Any]:
    """Verify the five runtime bytes; execution configuration is a separate gate."""
    expected, errors = _runtime_declarations(amendment)
    observed_rows, unsafe_paths = _tree_rows(runtime_root)
    observed = _canonical_observed(observed_rows)
    amendment_identity = amendment.get("amendment_version") == AIRTRAVEL_AMENDMENT_VERSION
    runtime_identity = _amendment_identity(amendment)
    if len(expected) != RUNTIME_FILE_COUNT:
        errors.append("runtime manifest must contain exactly five files")
    result = _blocked(
        expected_count=len(expected),
        observed_count=len(observed),
        unsafe_paths=unsafe_paths,
        manifest_errors=errors,
        runtime_identity=runtime_identity,
        amendment_identity=amendment_identity,
    )
    if (
        not errors
        and not unsafe_paths
        and runtime_identity
        and amendment_identity
        and expected == observed
    ):
        result["status"] = "PASS"
    return result


def _verify_reference_separation(
    runtime_root: Path,
    reference_root: Path | None,
    source_root: Path,
    source_manifest: Mapping[str, Any],
    amendment: Mapping[str, Any],
) -> dict[str, Any]:
    if reference_root is None:
        return _blocked(reason="reference root was not supplied")
    reference_rows, unsafe_paths = _tree_rows(reference_root)
    if unsafe_paths:
        return _blocked(unsafe_paths=unsafe_paths)
    runtime_rows, runtime_unsafe = _tree_rows(runtime_root)
    if runtime_unsafe:
        return _blocked(unsafe_paths=runtime_unsafe)
    expected, errors = _canonical_rows(amendment.get("excluded_references"))
    if {row[0] for row in expected} != set(FROZEN_REFERENCE_PATHS):
        errors.append("excluded references differ from frozen declaration")
    expected_local = [
        (path.removeprefix("reference_only/"), size, digest) for path, size, digest in expected
    ]
    source_rows, source_errors = _canonical_rows(source_manifest.get("files"))
    errors.extend(source_errors)
    source_reference_match = all(row in source_rows for row in expected_local)
    for path, size, digest in expected_local:
        source_path = source_root / path
        try:
            if (
                _is_link_or_reparse(source_path)
                or source_path.stat().st_size != size
                or sha256(source_path) != digest
            ):
                source_reference_match = False
        except OSError:
            source_reference_match = False
    expected_local = sorted(expected_local)
    observed = _canonical_observed(reference_rows)
    declared_reference_match = (
        not errors and len(expected_local) == 3 and expected_local == observed
    )
    if (
        runtime_root.resolve() == reference_root.resolve()
        or runtime_root.resolve() in reference_root.resolve().parents
        or reference_root.resolve() in runtime_root.resolve().parents
    ):
        errors.append("reference and runtime roots overlap")
    reference_bytes = {(size, digest) for _, size, digest in expected}
    leaked_paths = [
        row["path"] for row in runtime_rows if (row["bytes"], row["sha256"]) in reference_bytes
    ]
    return {
        "status": "PASS"
        if declared_reference_match and source_reference_match and not errors and not leaked_paths
        else "BLOCKED",
        "reference_count": len(reference_rows),
        "declared_reference_match": declared_reference_match,
        "source_reference_match": source_reference_match,
        "errors": errors,
        **_comparison(expected_local, observed),
        "leaked_paths": leaked_paths,
    }


def _comparison(
    expected: list[tuple[str, int, str]], observed: list[tuple[str, int, str]]
) -> dict[str, Any]:
    want, got = {row[0]: row[1:] for row in expected}, {row[0]: row[1:] for row in observed}
    return {
        "missing": sorted(want.keys() - got.keys()),
        "extra": sorted(got.keys() - want.keys()),
        "mismatched": sorted(path for path in want.keys() & got.keys() if want[path] != got[path]),
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
        source.get("upstream_commit", ""),
    )
    source_entries = verify_source_entries(source_root, source)
    expected_entries, entry_errors = _canonical_rows(source.get("files"))
    archive_entries, archive_errors = _canonical_rows(source_archive.get("member_inventory"))
    source_archive.update(_comparison(expected_entries, archive_entries))
    if entry_errors or archive_errors or expected_entries != archive_entries:
        source_archive["status"] = "BLOCKED"
        source_archive["inventory_matches_manifest"] = False
    else:
        source_archive["inventory_matches_manifest"] = True
    source_to_runtime = verify_source_to_runtime_mapping(source_root, runtime_root, amendment)
    runtime_pack = verify_runtime_pack(runtime_root, amendment)
    reference_separation = _verify_reference_separation(
        runtime_root, reference_root, source_root, source, amendment
    )
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
