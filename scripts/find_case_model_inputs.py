#!/usr/bin/env python3
"""Inventory likely Study 1 case-model inputs without reading model content.

The inventory is deliberately metadata-only: filenames, archive member names,
sizes and hashes are recorded for provenance, while raw student material stays
outside tracked output.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import pathlib
import zipfile
from typing import Any

FRAGMENTS = ("Dataset1_ModelEval", "ParkWise", "Cheers", "Cases", "ucd", "cd")
EXCLUDED_DIRS = {".git", "node_modules", "__pycache__", ".venv", "venv"}


def sha256(path: pathlib.Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _candidate(path: pathlib.Path, root: pathlib.Path) -> bool:
    parts = [part.casefold() for part in path.parts]
    context = any(any(token in part for token in ("dataset1_modeleval", "parkwise", "cheers")) for part in parts)
    if context and path.suffix.casefold() in {".txt", ".json", ".yaml", ".yml", ".xml", ".zip"}:
        return True
    name = path.name.casefold()
    return path.suffix.casefold() == ".zip" and any(token in name for token in ("dataset1", "parkwise", "cheers", "model", "vego-ai"))


def inventory(roots: list[pathlib.Path]) -> dict[str, Any]:
    files: list[dict[str, Any]] = []
    archives: list[dict[str, Any]] = []
    seen: set[str] = set()
    for root in roots:
        root = root.expanduser().resolve()
        if not root.exists():
            continue
        if root.is_file():
            paths = [root]
        else:
            paths = []
            for base, dirs, names in os.walk(root):
                dirs[:] = [name for name in dirs if name not in EXCLUDED_DIRS]
                for name in names:
                    paths.append(pathlib.Path(base) / name)
        for path in sorted(paths):
            try:
                resolved = path.resolve()
                key = str(resolved).casefold()
                if key in seen or not _candidate(resolved, root):
                    continue
                seen.add(key)
                stat = resolved.stat()
                row = {"name": resolved.name, "path": str(resolved), "relative_hint": resolved.name,
                       "bytes": stat.st_size, "sha256": sha256(resolved),
                       "kind": "file"}
                if resolved.suffix.casefold() == ".zip":
                    try:
                        with zipfile.ZipFile(resolved) as archive:
                            members = [info for info in archive.infolist()
                                       if any(f.casefold() in info.filename.casefold() for f in FRAGMENTS)]
                            archives.append({**row, "kind": "archive",
                                             "member_count": len(archive.infolist()),
                                             "matching_members": [
                                                 {"name": info.filename, "bytes": info.file_size}
                                                 for info in members]})
                    except (OSError, zipfile.BadZipFile) as exc:
                        archives.append({**row, "kind": "archive_error", "error": type(exc).__name__})
                else:
                    files.append(row)
            except (OSError, PermissionError):
                continue
    return {
        "schema": "study1-case-model-input-recovery-v1",
        "read_only": True,
        "content_read": False,
        "roots": [str(root.expanduser().resolve()) for root in roots],
        "candidate_files": files,
        "candidate_archives": archives,
        "status": "RECOVERED_CANDIDATES" if files or archives else "NOT_FOUND",
        "claim_boundary": "metadata_inventory_only; no case-model content or evaluation output inspected",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", action="append", type=pathlib.Path, required=True)
    parser.add_argument("--output", type=pathlib.Path, required=True)
    args = parser.parse_args()
    result = inventory(args.root)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": result["status"], "files": len(result["candidate_files"]), "archives": len(result["candidate_archives"])}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
