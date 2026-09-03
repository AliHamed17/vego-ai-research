#!/usr/bin/env python3
"""Read-only inventory of historical interaction-log candidates.

The command searches explicitly supplied local roots and ZIP members.  It never
extracts, rewrites, or prints record content.  The JSON output is intended for
an ignored/private evidence workspace; only safe aggregates should be copied
into tracked research documentation.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import zipfile
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Iterator


NAME_PATTERN = re.compile(
    r"(?:interaction|llm|model[_-]?call|response)[^/\\]*",
    re.IGNORECASE,
)
TEXT_EXTENSIONS = {".jsonl", ".json", ".log", ".txt"}
ARCHIVE_EXTENSIONS = {".zip"}
SCHEMA_KEYS = {
    "timestamp",
    "time",
    "label",
    "model",
    "prompt_hash",
    "prompt_length",
    "response_hash",
    "response_length",
    "prompt_system",
    "prompt_user",
    "response_raw",
    "response_parsed_content",
    "usage",
    "tokens",
    "error",
    "duration",
    "latency",
}
CONTENT_KEYS = {
    "prompt_system",
    "prompt_user",
    "response_raw",
    "response_parsed_content",
}
PROVENANCE_KEYS = {"run_id", "setting", "dataset", "suite", "experiment", "model"}
MAX_TEXT_BYTES = 8 * 1024 * 1024
MAX_ARCHIVE_MEMBER_BYTES = 32 * 1024 * 1024
SKIP_DIR_NAMES = {
    ".git",
    ".venv",
    "node_modules",
    "__pycache__",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
}


@dataclass(frozen=True)
class Payload:
    data: bytes
    source: str
    archive: str | None = None
    member: str | None = None


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest().upper()


def file_timestamp(path: Path) -> str | None:
    try:
        return datetime.fromtimestamp(path.stat().st_mtime, timezone.utc).isoformat()
    except OSError:
        return None


def safe_read(path: Path, limit: int = MAX_TEXT_BYTES) -> bytes | None:
    try:
        with path.open("rb") as handle:
            return handle.read(limit + 1)
    except (OSError, PermissionError):
        return None


def likely_name(value: str) -> bool:
    return bool(NAME_PATTERN.search(value))


def iter_files(root: Path) -> Iterator[Path]:
    root = root.resolve()
    for current, directories, files in os.walk(root, topdown=True, onerror=lambda _error: None):
        directories[:] = [directory for directory in directories if directory not in SKIP_DIR_NAMES]
        directories.sort(key=str.lower)
        files.sort(key=str.lower)
        for filename in files:
            path = Path(current) / filename
            try:
                if path.is_file():
                    yield path
            except OSError:
                continue


def contextual_path(value: str) -> bool:
    lowered = value.lower()
    return any(
        token in lowered
        for token in (
            "vego",
            "eval",
            "experiment",
            "cheers",
            "parkwise",
            "ucd",
            "cd_",
            "interaction",
            "llm",
            "model",
            "response",
            "orchestrat",
            "output",
            "run",
            "research",
            "archive",
            "log",
        )
    )


def archive_members(path: Path, max_depth: int, depth: int = 0) -> Iterator[Payload]:
    raw = safe_read(path, MAX_ARCHIVE_MEMBER_BYTES)
    # Archive bytes may be larger than the ordinary read limit; open the path
    # directly after the inexpensive signature read.
    if raw is None:
        return
    try:
        with zipfile.ZipFile(path) as archive:
            for info in sorted(archive.infolist(), key=lambda item: item.filename.lower()):
                if info.is_dir() or info.file_size > MAX_ARCHIVE_MEMBER_BYTES:
                    continue
                member_suffix = Path(info.filename).suffix.lower()
                if not (
                    likely_name(info.filename)
                    or (member_suffix in TEXT_EXTENSIONS and contextual_path(info.filename))
                ):
                    continue
                try:
                    data = archive.read(info)
                except (OSError, RuntimeError, KeyError, zipfile.BadZipFile):
                    continue
                yield Payload(data, str(path), str(path), info.filename)
                if depth < max_depth and info.filename.lower().endswith(".zip"):
                    # Nested ZIP inspection is bounded and in-memory only.
                    try:
                        with zipfile.ZipFile(__import__("io").BytesIO(data)) as nested:
                            for nested_info in sorted(
                                nested.infolist(), key=lambda item: item.filename.lower()
                            ):
                                if nested_info.is_dir() or nested_info.file_size > MAX_ARCHIVE_MEMBER_BYTES:
                                    continue
                                nested_suffix = Path(nested_info.filename).suffix.lower()
                                if not (
                                    likely_name(nested_info.filename)
                                    or (
                                        nested_suffix in TEXT_EXTENSIONS
                                        and contextual_path(nested_info.filename)
                                    )
                                ):
                                    continue
                                try:
                                    nested_data = nested.read(nested_info)
                                except (OSError, RuntimeError, KeyError, zipfile.BadZipFile):
                                    continue
                                yield Payload(
                                    nested_data,
                                    str(path),
                                    str(path),
                                    f"{info.filename}!/{nested_info.filename}",
                                )
                    except (OSError, RuntimeError, zipfile.BadZipFile):
                        continue
    except (OSError, zipfile.BadZipFile):
        return


def parse_records(data: bytes, suffix: str) -> tuple[list[dict[str, Any]], str]:
    if len(data) > MAX_TEXT_BYTES:
        return [], "too_large"
    try:
        text = data.decode("utf-8-sig")
    except UnicodeDecodeError:
        return [], "non_utf8"
    records: list[dict[str, Any]] = []
    if suffix.lower().endswith(".jsonl") or "\n" in text:
        for line in text.splitlines():
            if not line.strip():
                continue
            try:
                value = json.loads(line)
            except (TypeError, ValueError):
                continue
            if isinstance(value, dict):
                records.append(value)
    else:
        try:
            value = json.loads(text)
        except (TypeError, ValueError):
            return [], "invalid_json"
        if isinstance(value, dict):
            records.append(value)
        elif isinstance(value, list):
            records.extend(item for item in value if isinstance(item, dict))
    return records, "parsed" if records else "no_records"


def record_summary(records: list[dict[str, Any]]) -> dict[str, Any]:
    keys = sorted({key for record in records for key in record if isinstance(key, str)})
    schema_hits = sorted(set(keys) & SCHEMA_KEYS)
    content_keys = sorted(set(keys) & CONTENT_KEYS)
    labels: set[str] = set()
    models: set[str] = set()
    settings: set[str] = set()
    for record in records:
        for field, target in (("label", labels), ("model", models), ("setting", settings)):
            value = record.get(field)
            if isinstance(value, str) and value and len(value) <= 160:
                # Only allow safe identifier-like values into the receipt.
                if re.fullmatch(r"[A-Za-z0-9_.:/ -]+", value):
                    target.add(value)
    nonempty_content = any(
        isinstance(record.get(key), (str, list, dict)) and bool(record.get(key))
        for record in records
        for key in CONTENT_KEYS
    )
    has_hash_or_length = any(
        key in record
        for record in records
        for key in {"prompt_hash", "response_hash", "prompt_length", "response_length"}
    )
    if nonempty_content:
        logging_mode = "full_content"
    elif has_hash_or_length or schema_hits:
        logging_mode = "metadata_only"
    else:
        logging_mode = "unknown"
    return {
        "record_count": len(records),
        "keys": keys,
        "schema_fields_present": schema_hits,
        "content_fields_present": content_keys,
        "content_nonempty": nonempty_content,
        "labels": sorted(labels),
        "models": sorted(models),
        "settings": sorted(settings),
        "logging_mode_inferred": logging_mode,
    }


def candidate_reason(path_text: str, records: list[dict[str, Any]], member: str | None) -> list[str]:
    reasons: list[str] = []
    name = member or path_text
    if likely_name(name):
        reasons.append("filename_matches_interaction_pattern")
    if records:
        hits = set().union(*(set(record) for record in records)) & SCHEMA_KEYS
        if hits:
            reasons.append("JSON_schema_resembles_model_interaction_record")
    lowered = f"{path_text} {member or ''}".lower()
    for token in ("cheers", "parkwise", "ucd_ch", "ucd_pw", "cd_ch", "cd_pw", "eval_output"):
        if token in lowered:
            reasons.append(f"path_contains_{token}")
    return sorted(set(reasons))


def classify(path_text: str, records: list[dict[str, Any]], member: str | None, reasons: list[str]) -> str:
    if not reasons:
        return "NOT_RELEVANT"
    lowered = f"{path_text} {member or ''}".lower()
    has_historical_context = any(
        token in lowered for token in ("cheers", "parkwise", "ucd_ch", "ucd_pw", "cd_ch", "cd_pw", "eval_output")
    )
    if records and has_historical_context and "filename_matches_interaction_pattern" in reasons:
        return "ORIGINAL_LOG_PROBABLE"
    if records and "JSON_schema_resembles_model_interaction_record" in reasons:
        return "UNVERIFIABLE_CANDIDATE"
    return "NON_ORIGINAL_LOG"


def inventory(roots: Iterable[Path], max_archive_depth: int = 1) -> dict[str, Any]:
    candidates: list[dict[str, Any]] = []
    searched_roots: list[dict[str, Any]] = []
    seen_files: set[str] = set()
    for root in sorted({path.resolve() for path in roots}, key=lambda p: p.as_posix().lower()):
        root_record: dict[str, Any] = {"root": str(root), "exists": root.exists(), "file_count": 0}
        searched_roots.append(root_record)
        if not root.exists():
            continue
        for path in iter_files(root):
            key = str(path).lower()
            if key in seen_files:
                continue
            seen_files.add(key)
            root_record["file_count"] += 1
            suffix = path.suffix.lower()
            archive = suffix in ARCHIVE_EXTENSIONS
            data: bytes | None = None
            payloads: list[Payload] = []
            if archive:
                payloads.extend(archive_members(path, max_archive_depth))
            relative_hint = path.relative_to(root).as_posix()
            if likely_name(path.name) or (
                suffix in TEXT_EXTENSIONS and contextual_path(relative_hint)
            ):
                data = safe_read(path)
                if data is not None:
                    payloads.append(Payload(data, str(path)))
            for payload in payloads:
                display_name = payload.member or Path(payload.source).name
                if not likely_name(display_name) and payload.member is not None:
                    # Parse only explicitly named interaction-like members; this
                    # keeps archive inspection broad without reading every blob.
                    continue
                records, parse_status = parse_records(payload.data, display_name)
                reasons = candidate_reason(payload.source, records, payload.member)
                if not reasons:
                    continue
                candidate = {
                    "path": payload.source,
                    "archive": payload.archive,
                    "member": payload.member,
                    "filename": display_name,
                    "bytes": len(payload.data),
                    "sha256": sha256_bytes(payload.data),
                    "filesystem_mtime_utc": file_timestamp(Path(payload.source))
                    if payload.member is None
                    else file_timestamp(Path(payload.source)),
                    "parse_status": parse_status,
                    "match_reasons": reasons,
                    "classification": classify(payload.source, records, payload.member, reasons),
                }
                if records:
                    candidate["record_summary"] = record_summary(records)
                candidates.append(candidate)
    candidates.sort(key=lambda item: (item["path"].lower(), (item["member"] or "").lower()))
    return {
        "schema_version": "OriginalInteractionLogRecoveryInventory-v1",
        "read_only": True,
        "network_used": False,
        "raw_content_emitted": False,
        "search_roots": searched_roots,
        "candidate_count": len(candidates),
        "classification_counts": {
            cls: sum(item["classification"] == cls for item in candidates)
            for cls in (
                "ORIGINAL_LOG_CONFIRMED",
                "ORIGINAL_LOG_PROBABLE",
                "NON_ORIGINAL_LOG",
                "UNVERIFIABLE_CANDIDATE",
                "NOT_RELEVANT",
            )
        },
        "candidates": candidates,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("roots", nargs="+", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--max-archive-depth", type=int, default=1)
    args = parser.parse_args(argv)
    if args.max_archive_depth < 0 or args.max_archive_depth > 3:
        parser.error("--max-archive-depth must be between 0 and 3")
    payload = inventory(args.roots, args.max_archive_depth)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"wrote: {args.output} ({payload['candidate_count']} candidates)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
