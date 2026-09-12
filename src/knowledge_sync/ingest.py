from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

from .contracts import KnowledgeRecord, validate_record

URL_PATTERN = re.compile(r"https?://\S+", re.IGNORECASE)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _safe_summary(path: Path) -> str:
    text = path.read_text(encoding="utf-8", errors="replace")
    text = URL_PATTERN.sub("[redacted-url]", text)
    return " ".join(text.split())[:500]


def ingest_file(
    *,
    source: Path,
    records_root: Path,
    project: str,
    classification: str,
    source_kind: str,
) -> KnowledgeRecord:
    digest = _sha256(source)
    record = KnowledgeRecord(
        record_id=f"K-{digest[:12]}",
        project=project,
        classification=classification,
        source_kind=source_kind,
        source_ref=(f"restricted:{digest}" if classification in {"restricted", "secret"} else f"file:{source.name}"),
        sha256=digest,
        summary=("Restricted source; summary withheld." if classification in {"restricted", "secret"} else _safe_summary(source)),
        review_state="pending_human_review",
    )
    errors = validate_record(record)
    if errors:
        raise ValueError("; ".join(errors))
    if classification in {"public", "internal"}:
        target = records_root / project
        target.mkdir(parents=True, exist_ok=True)
        (target / f"{record.record_id}.json").write_text(
            json.dumps(record.__dict__, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
    return record
