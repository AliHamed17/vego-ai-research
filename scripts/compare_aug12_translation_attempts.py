#!/usr/bin/env python3
"""Compare private machine-English attempts without exposing transcript text."""

from __future__ import annotations

import argparse
import hashlib
import json
from collections.abc import Sequence
from datetime import datetime
from pathlib import Path


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest().upper()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def _load_prefix(path: Path, prefix_rows: int) -> tuple[list[str], list[dict[str, str]]]:
    if prefix_rows < 1:
        raise ValueError("prefix_rows must be positive")
    lines = [
        line for line in path.read_text(encoding="utf-8").splitlines(keepends=True) if line.strip()
    ]
    if len(lines) < prefix_rows:
        raise ValueError(f"{path.name} has only {len(lines)} rows; {prefix_rows} required")
    rows = [json.loads(line) for line in lines[:prefix_rows]]
    return lines[:prefix_rows], rows


def _load_events(path: Path) -> list[dict[str, object]]:
    events: list[dict[str, object]] = []
    previous: datetime | None = None
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        event = json.loads(line)
        if not isinstance(event, dict):
            raise ValueError(f"event line {line_number} is not an object")
        run_id = str(event.get("run_id", "")).strip()
        timestamp = str(event.get("timestamp_utc", "")).strip()
        if not run_id or not timestamp:
            raise ValueError("attempt event has a blank run_id or timestamp")
        parsed = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
        if parsed.tzinfo is None or (previous is not None and parsed < previous):
            raise ValueError("attempt event timestamps are invalid or out of order")
        previous = parsed
        events.append(dict(event))
    return events


def validate_attempt_events(path: Path, output_path: Path) -> dict[str, object]:
    events = _load_events(path)
    starts = [(index, event) for index, event in enumerate(events) if event.get("event") == "translation_run_started"]
    if not starts:
        raise ValueError("attempt event ledger lacks a run start")
    start_index, start = starts[-1]
    run_id = str(start["run_id"])
    required_start = (
        "source_name",
        "source_bytes",
        "source_sha256",
        "source_segment_count",
        "script_sha256",
        "model",
        "model_digest",
        "options",
        "batch_size",
        "timeout_seconds",
        "translation_prompt_template_sha256",
    )
    if any(start.get(field) in {None, ""} for field in required_start if field != "options"):
        raise ValueError("attempt run start metadata is incomplete")
    if not isinstance(start.get("options"), dict):
        raise ValueError("attempt run options are missing")
    terminals = [
        (index, event)
        for index, event in enumerate(events[start_index:], start=start_index)
        if str(event.get("run_id", "")) == run_id
        and event.get("event") in {"translation_run_completed", "translation_run_interrupted"}
    ]
    if len(terminals) != 1:
        raise ValueError("latest attempt run lacks one terminal binding")
    terminal_index, terminal = terminals[0]
    if terminal_index != len(events) - 1:
        raise ValueError("attempt event ledger has events after its terminal binding")
    if terminal.get("event") == "translation_run_completed":
        hash_field, bytes_field = "output_sha256", "output_bytes"
    else:
        hash_field, bytes_field = "checkpoint_sha256", "checkpoint_bytes"
    if str(terminal.get(hash_field, "")).upper() != sha256_file(output_path):
        raise ValueError("attempt terminal hash does not bind its JSONL")
    if terminal.get(bytes_field) != output_path.stat().st_size:
        raise ValueError("attempt terminal byte count does not bind its JSONL")
    row_count = sum(1 for line in output_path.read_text(encoding="utf-8").splitlines() if line.strip())
    if terminal.get("translated_segment_count") != row_count:
        raise ValueError("attempt terminal row count does not bind its JSONL")
    return {
        "event_ledger_name": path.name,
        "event_ledger_bytes": path.stat().st_size,
        "event_ledger_sha256": sha256_file(path),
        "run_id": run_id,
        "terminal_event": terminal["event"],
        "source_name": start["source_name"],
        "source_bytes": start["source_bytes"],
        "source_sha256": str(start["source_sha256"]).upper(),
        "source_segment_count": start["source_segment_count"],
        "script_sha256": str(start["script_sha256"]).upper(),
        "model": start["model"],
        "model_digest": str(start["model_digest"]).lower(),
        "options": start["options"],
        "batch_size": start["batch_size"],
        "timeout_seconds": start["timeout_seconds"],
        "translation_prompt_template_sha256": str(
            start["translation_prompt_template_sha256"]
        ).upper(),
    }


def compare_attempts(
    first_path: Path,
    second_path: Path,
    *,
    prefix_rows: int,
    first_events: Path | None = None,
    second_events: Path | None = None,
) -> dict[str, object]:
    first_lines, first = _load_prefix(first_path, prefix_rows)
    second_lines, second = _load_prefix(second_path, prefix_rows)
    changed: list[str] = []
    for left, right in zip(first, second, strict=True):
        segment_id = str(left.get("Segment_ID", ""))
        if not segment_id or right.get("Segment_ID") != segment_id:
            raise ValueError("attempt segment IDs do not align")
        if right.get("Source_HE_SHA256") != left.get("Source_HE_SHA256"):
            raise ValueError(f"source Hebrew hash mismatch for {segment_id}")
        if right != left:
            changed.append(segment_id)
    event_evidence: dict[str, object] | None = None
    comparability = "unverified"
    if (first_events is None) != (second_events is None):
        raise ValueError("both attempt event ledgers must be supplied together")
    if first_events is not None and second_events is not None:
        first_run = validate_attempt_events(first_events, first_path)
        second_run = validate_attempt_events(second_events, second_path)
        comparable_fields = (
            "source_name",
            "source_bytes",
            "source_sha256",
            "source_segment_count",
            "model",
            "model_digest",
            "options",
            "batch_size",
            "timeout_seconds",
            "translation_prompt_template_sha256",
        )
        mismatches = [field for field in comparable_fields if first_run[field] != second_run[field]]
        event_evidence = {
            "attempt_01": first_run,
            "attempt_02": second_run,
            "comparable_field_mismatches": mismatches,
            "generator_script_hash_match": first_run["script_sha256"] == second_run["script_sha256"],
        }
        comparability = (
            "event_metadata_partially_evidenced"
            if not mismatches
            else "event_metadata_not_comparable"
        )
    report = {
        "schema_version": "Aug12TranslationAttemptComparison-v1",
        "method": (
            "Parse the first N non-empty JSONL rows; require identical ordered Segment_ID and "
            "Source_HE_SHA256 values; compare complete row objects; report counts and changed IDs "
            "without emitting Hebrew or English text."
        ),
        "prefix_rows": prefix_rows,
        "compared_rows": prefix_rows,
        "exact_match_rows": prefix_rows - len(changed),
        "changed_rows": len(changed),
        "changed_segment_ids": changed,
        "attempt_01": {
            "name": first_path.name,
            "bytes": first_path.stat().st_size,
            "sha256": sha256_file(first_path),
            "prefix_sha256": sha256_bytes("".join(first_lines).encode("utf-8")),
        },
        "attempt_02": {
            "name": second_path.name,
            "bytes": second_path.stat().st_size,
            "sha256": sha256_file(second_path),
            "prefix_sha256": sha256_bytes("".join(second_lines).encode("utf-8")),
        },
        "parameter_comparability": comparability,
        "event_evidence": event_evidence,
        "claim_boundary": (
            "Machine-English content differs across reruns and requires bilingual human review. "
            "This tool does not establish stable translation output or direct quotations."
        ),
        "contains_transcript_text": False,
    }
    forbidden = ("deterministic translation", "reproducible output")
    rendered = json.dumps(report, ensure_ascii=False).casefold()
    if any(phrase in rendered for phrase in forbidden):
        raise AssertionError("comparison report contains a forbidden stability claim")
    return report


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--attempt-01", required=True, type=Path)
    parser.add_argument("--attempt-02", required=True, type=Path)
    parser.add_argument("--prefix-rows", required=True, type=int)
    parser.add_argument("--attempt-01-events", type=Path)
    parser.add_argument("--attempt-02-events", type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args(argv)
    report = compare_attempts(
        args.attempt_01,
        args.attempt_02,
        prefix_rows=args.prefix_rows,
        first_events=args.attempt_01_events,
        second_events=args.attempt_02_events,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
