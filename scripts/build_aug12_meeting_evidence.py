#!/usr/bin/env python3
"""Build evidence-bound records for the 2026-08-12 supervisor meeting.

The raw Hebrew ASR remains immutable.  This module assigns meeting-scoped
segment IDs, accounts for every uncovered media interval, aligns a separate
local English translation, and refuses to emit human-reviewed evidence until
two complete independent reviews and all required adjudications are present.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import ipaddress
import json
import os
import platform
import re
import struct
import sys
import unicodedata
import urllib.request
from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from datetime import date, datetime, timezone
from decimal import ROUND_HALF_UP, Decimal
from pathlib import Path
from urllib.parse import urlsplit

SEGMENT_PREFIX = "S12"
GAP_PREFIX = "G12"
MEDIA_TIMELINE_ID = "MEDIA-TIMELINE"
CONTROL_PATTERN = re.compile(r"^(?:F12|A12|D12|Q12|R12)-\d{3}$")
CONTROL_ORDER = {"F12": 0, "A12": 1, "D12": 2, "Q12": 3, "R12": 4}
SPEAKERS = {"Iris", "Arnon", "Ali", "Multiple", "Unresolved", "Non-speech"}
SPEAKER_CONFIDENCE = {"High", "Medium", "Low", "Unknown"}
CONTENT_CLASSES = {
    "Requirement",
    "Action",
    "Decision",
    "Open question",
    "Risk or dependency",
    "External factual claim",
    "Rationale or clarification",
    "Context",
    "Housekeeping",
    "Noise or non-speech",
}
CONSENSUS_FIELDS = (
    "Reviewed_HE",
    "Reviewed_EN",
    "Speaker",
    "Speaker_Confidence",
    "Speaker_Basis",
    "Content_Class",
    "Control_IDs",
    "Review_Notes",
)
SUBSTANTIVE_CLASSES = CONTENT_CLASSES - {"Housekeeping", "Noise or non-speech"}
NAMED_SPEAKERS = {"Iris", "Arnon", "Ali"}
NAMED_SPEAKER_BASIS_PREFIXES = (
    "audiovisual confirmation",
    "audio-visual confirmation",
    "visible zoom name label",
    "speaker self-identification",
    "written attribution confirmation",
)
HUMAN_RETURN_FILENAMES = frozenset({"reviewer-a.csv", "reviewer-b.csv", "adjudication.csv"})
CSV_FORMULA_PREFIXES = ("=", "+", "-", "@", "\t", "\r", "\n")
SEGMENT_SPAN_PATTERN = re.compile(r"(S12-\d{4})(?:--(S12-\d{4}))?")
LEDGER_FIELDS = (
    "Segment_ID",
    "Start",
    "End",
    "Speaker",
    "Speaker_Confidence",
    "Speaker_Basis",
    "Machine_HE",
    "Reviewed_HE",
    "Machine_EN",
    "Reviewed_EN",
    "Content_Class",
    "Control_IDs",
    "Reviewer_A",
    "Reviewer_B",
    "Disagreement",
    "Adjudication",
    "Status",
    "Evidence_Link",
)
GAP_FIELDS = (
    "Gap_ID",
    "Gap_Type",
    "Start",
    "End",
    "Duration_Seconds",
    "Previous_Segment_ID",
    "Next_Segment_ID",
    "Machine_Disposition",
    "Human_Classification",
    "Reviewer_A",
    "Reviewer_B",
    "Adjudication",
    "Status",
)
REVIEW_FIELDS = (
    "Record_ID",
    "Record_Type",
    "Reviewer_ID",
    "Review_Date",
    "Reviewed_HE",
    "Reviewed_EN",
    "Speaker",
    "Speaker_Confidence",
    "Speaker_Basis",
    "Content_Class",
    "Control_IDs",
    "Review_Notes",
)
ADJUDICATION_FIELDS = (
    "Record_ID",
    "Adjudicator_ID",
    "Adjudication_Date",
    "Final_HE",
    "Final_EN",
    "Final_Speaker",
    "Final_Speaker_Confidence",
    "Final_Speaker_Basis",
    "Final_Content_Class",
    "Final_Control_IDs",
    "Adjudication_Rationale",
    "Decision_Status",
)
TRANSLATION_LINE = re.compile(r"^\s*(S12-\d{4})\s*\|\|\s*(\S.*?)\s*$")
DEFAULT_OLLAMA_OPTIONS = {
    "temperature": 0,
    "top_p": 1,
    "seed": 0,
    "num_ctx": 8192,
    "num_predict": 4096,
}
PACKAGE_OWNER_FILENAME = ".aug12-meeting-package-owner.json"
PACKAGE_FILENAMES = frozenset(
    {
        PACKAGE_OWNER_FILENAME,
        "source-provenance.json",
        "machine-normalized.he.jsonl",
        "machine-gap-ledger.csv",
        "machine-ledger.csv",
        "reviewer-a.csv",
        "reviewer-b.csv",
        "adjudication.csv",
        "preliminary-ledger.json",
        "artifact-manifest.json",
    }
)
REQUIRED_PROVENANCE_ROLES = frozenset(
    {
        "raw_audio",
        "raw_video",
        "raw_chat",
        "recording_config",
        "hebrew_asr",
        "hebrew_asr_readable",
        "asr_generator_script",
        "asr_task_log",
        "asr_model_blob",
        "media_comparison",
        "media_fingerprint_generator",
        "media_fingerprint_task_log",
        "evidence_builder",
        "control_register",
    }
)
REQUIRED_TRANSLATION_PROVENANCE_ROLES = frozenset(
    {
        "machine_english",
        "translation_event_log",
        "translation_generator_script",
        "ollama_model_blob",
        "ollama_model_manifest",
        "translation_attempt_01_partial",
        "translation_attempt_01_event_log",
        "translation_comparison_generator",
        "translation_comparison_report",
    }
)
PRIVATE_EVIDENCE_ROLES = frozenset(
    {
        "raw_audio",
        "raw_video",
        "raw_chat",
        "recording_config",
        "hebrew_asr",
        "hebrew_asr_readable",
        "asr_generator_script",
        "asr_task_log",
        "media_comparison",
        "media_fingerprint_generator",
        "media_fingerprint_task_log",
        "machine_english",
        "translation_event_log",
        "translation_generator_script",
        "translation_attempt_01_partial",
        "translation_attempt_01_event_log",
        "translation_comparison_generator",
        "translation_comparison_report",
    }
)
TRUSTED_REPO_ROLES = frozenset({"control_register", "evidence_builder"})
HF_CACHE_ROLES = frozenset({"asr_model_blob"})
OLLAMA_CACHE_ROLES = frozenset({"ollama_model_blob", "ollama_model_manifest"})
SUPPORTED_PROVENANCE_ROLES = (
    PRIVATE_EVIDENCE_ROLES | TRUSTED_REPO_ROLES | HF_CACHE_ROLES | OLLAMA_CACHE_ROLES
)
AUG12_SOURCE_PROFILE: dict[str, object] = {
    "profile_id": "2026-08-12-iris-arnon-zoom-local-v1",
    "media_duration_seconds": "3224.448",
    "raw_audio_sha256": "E562AE340AB8FF87BEB84AA03D5BFD709A01A396F0045F2CAE4EEE71C4C0E798",
    "raw_audio_bytes": 35_684_965,
    "raw_video_sha256": "617824ABBA9A9A1626BB73BDEC536ADC6C3A0F3F2A27CFE0335ECE3FC93E435C",
    "raw_video_bytes": 226_239_003,
    "raw_chat_sha256": "4682711493FD4CA6F694DB0EE0FC116497A8D0A9DA28EB1744F3D070E8E00F94",
    "raw_chat_bytes": 315,
    "recording_config_sha256": "124659343355D5A0EC76C053EC3958BDA39F51BCC7095A19A22A65C902574C7F",
    "recording_config_bytes": 127,
    "hebrew_asr_sha256": "A9267A95B0F93715375D3A21C2E4C897D7E0682EC0552811E4478831C994EC4D",
    "hebrew_asr_bytes": 93_920,
    "hebrew_asr_segment_count": 1_064,
    "hebrew_asr_schema": "jsonl:start,end,text:v1",
    "hebrew_asr_readable_sha256": "3CC7E56757B83BE416089247D4C8053D56A7F03C1A47699163670F421976EE32",
    "hebrew_asr_readable_bytes": 70_581,
    "asr_generator_script_sha256": "C71032EE0CA1579971B6BF71E057417B73BB13EE274DF0ACAAE8342DE4E2A05E",
    "asr_generator_script_bytes": 2_512,
    "asr_task_log_sha256": "C83503AA02ADBA100D13B7889B8E98B6CA4230F588AD88DDBDF141C418FB60B3",
    "asr_task_log_bytes": 1_561,
    "asr_model_repository": "mobiuslabsgmbh/faster-whisper-large-v3-turbo",
    "asr_model_name": "large-v3-turbo",
    "asr_model_snapshot_commit": "0a363e9161cbc7ed1431c9597a8ceaf0c4f78fcf",
    "asr_model_snapshot_tree_sha256": "4EDA58772FE73D11E2ECF35D63D1F22F8296181CE6BFEA849B612C3FD574C74D",
    "asr_model_blob_sha256": "E76620F83D5F5B69EFD3D87E3DC180C1BD21DF9FBEBACFD4335E5E1EFCC018DA",
    "asr_model_blob_bytes": 1_617_884_929,
    "control_register_sha256": "5F6422D0573FD144CF99A7D14623F3B52874028197210A9119C41A36B83C79F7",
    "control_register_bytes": 14_902,
    "translation_model_name": "qwen2.5:7b",
    "translation_model_digest": "845DBDA0EA48ED749CAAFD9E6037047AA19ACFCFD82E704D7CA97D631A0B697E",
    "ollama_model_blob_sha256": "2BADA8A7450677000F678BE90653B85D364DE7DB25EB5EA54136ADA5F3933730",
    "ollama_model_blob_bytes": 4_683_073_952,
    "ollama_model_manifest_sha256": "845DBDA0EA48ED749CAAFD9E6037047AA19ACFCFD82E704D7CA97D631A0B697E",
    "ollama_model_manifest_bytes": 858,
    "translation_generator_script_sha256": "0DA0B228BF939DC9B5EEB05CA6FB7F294E51BDAE29DA9978B7A719698C887208",
    "translation_generator_script_bytes": 57_314,
    "machine_english_sha256": "E163DC80783C2AECE0467FAA2456D0536BA950001D917A6C25B4D3013C8DC25B",
    "machine_english_bytes": 168_996,
    "translation_event_log_sha256": "4E5C26D84802158A360BF45E4C31EDC41659DE4904E0CAB9BDFE80EC51D6EA11",
    "translation_event_log_bytes": 92_704,
    "translation_attempt_01_partial_sha256": "D258060249CEFDA4F18F727FED6A41D5AD4362E3EEF73A63ABC327645C8B216E",
    "translation_attempt_01_partial_bytes": 81_051,
    "translation_attempt_01_event_log_sha256": "4B38124EF9EE9FED95EF3B81E791FEC0437666BE888EB1B1419A760FE62D6152",
    "translation_attempt_01_event_log_bytes": 45_808,
    "translation_comparison_generator_sha256": "5F1278880779C1BA747DFE6941E2DFF96BB42AE77E3A71F6996C67DCEB2F22F3",
    "translation_comparison_generator_bytes": 10_120,
    "translation_comparison_report_sha256": "256A8C773F0BAD5A9A244D64FB7EEDF10F36EE720D8E7E1D75069089594F7ADA",
    "translation_comparison_report_bytes": 4_149,
    "translation_comparison_prefix_rows": 198,
    "translation_comparison_exact_rows": 152,
    "translation_comparison_changed_rows": 46,
    "encoded_packet_sha256": "8D639C5FB0DDC66A31F7A303141F2451BE0AA91273242A3C7988906E0F22F67C",
    "packet_timing_sha256": "15EF42A61C432F45293DCFCB3A30A181464D82B957794B626AE6BAAD6DB4D0D2",
    "canonical_pcm_sha256": "60D4A3A25CBBEC7ADC68486E5397355D903C028B55A27A9488E5F77898723266",
    "canonical_pcm_samples": 51_591_168,
}
RECOMPUTE_MEDIA_FINGERPRINTS = True


@dataclass(frozen=True)
class PendingReviews(Exception):
    detail: str

    def __str__(self) -> str:
        return self.detail


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest().upper()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def sha256_tree(path: Path) -> str:
    """Hash relative path, byte size, and file hash for a frozen model snapshot."""

    if not path.is_absolute() or not path.is_dir():
        raise ValueError("model snapshot path must be an existing absolute directory")
    files = sorted((item for item in path.rglob("*") if item.is_file()), key=lambda item: item.relative_to(path).as_posix())
    if not files:
        raise ValueError("model snapshot directory is empty")
    digest = hashlib.sha256()
    for item in files:
        relative = item.relative_to(path).as_posix()
        size = item.stat().st_size
        digest.update(relative.encode("utf-8"))
        digest.update(b"\0")
        digest.update(str(size).encode("ascii"))
        digest.update(b"\0")
        digest.update(sha256_file(item).encode("ascii"))
        digest.update(b"\n")
    return digest.hexdigest().upper()


def as_decimal(value: object) -> Decimal:
    return Decimal(str(value))


def format_hms(seconds: Decimal) -> str:
    milliseconds = int((seconds * 1000).quantize(Decimal("1"), rounding=ROUND_HALF_UP))
    hours, remainder = divmod(milliseconds, 3_600_000)
    minutes, remainder = divmod(remainder, 60_000)
    whole_seconds, millis = divmod(remainder, 1_000)
    return f"{hours:02d}:{minutes:02d}:{whole_seconds:02d}.{millis:03d}"


def json_number(value: Decimal) -> float:
    return float(value.quantize(Decimal("0.001")))


def normalize_asr_lines(
    lines: Iterable[str],
    *,
    expected_segments: int,
    media_duration: Decimal,
    segment_prefix: str = SEGMENT_PREFIX,
) -> list[dict[str, object]]:
    """Normalize the immutable ASR JSONL without modifying its text or timing."""

    rows: list[dict[str, object]] = []
    previous_start = Decimal("-1")
    for source_line, line in enumerate(lines, start=1):
        if not line.strip():
            continue
        try:
            source = json.loads(line)
        except json.JSONDecodeError as error:
            raise ValueError(f"invalid JSON at source line {source_line}") from error
        if not isinstance(source, dict):
            raise ValueError(f"source line {source_line} is not a JSON object")
        missing = [field for field in ("start", "end", "text") if field not in source]
        if missing:
            raise ValueError(f"source line {source_line} missing fields: {', '.join(missing)}")
        start = as_decimal(source["start"])
        end = as_decimal(source["end"])
        text = str(source["text"])
        if not text.strip():
            raise ValueError(f"empty machine Hebrew at source line {source_line}")
        if start < 0 or end <= start or end > media_duration:
            raise ValueError(f"invalid ASR interval at source line {source_line}")
        if start < previous_start:
            raise ValueError(f"out-of-order ASR interval at source line {source_line}")
        previous_start = start
        index = len(rows) + 1
        rows.append(
            {
                "Segment_ID": f"{segment_prefix}-{index:04d}",
                "Source_Line": source_line,
                "Start_Seconds": json_number(start),
                "End_Seconds": json_number(end),
                "Start": format_hms(start),
                "End": format_hms(end),
                "Machine_HE": text,
                "Source_HE_SHA256": sha256_text(text),
            }
        )
    if len(rows) != expected_segments:
        raise ValueError(f"expected {expected_segments} ASR segments; found {len(rows)}")
    return rows


def build_gap_rows(
    source_rows: Sequence[dict[str, object]],
    *,
    media_duration: Decimal,
    gap_prefix: str = GAP_PREFIX,
) -> list[dict[str, str]]:
    """Enumerate the complement of the ASR interval union on the media timeline."""

    gaps: list[dict[str, str]] = []
    cursor = Decimal("0")
    previous_segment = ""
    for row in source_rows:
        start = as_decimal(row["Start_Seconds"])
        end = as_decimal(row["End_Seconds"])
        if start > cursor:
            gaps.append(
                {
                    "Gap_ID": "",
                    "Gap_Type": "Lead" if not previous_segment else "Internal",
                    "Start": format_hms(cursor),
                    "End": format_hms(start),
                    "Duration_Seconds": f"{start - cursor:.3f}",
                    "Previous_Segment_ID": previous_segment,
                    "Next_Segment_ID": str(row["Segment_ID"]),
                    "Machine_Disposition": "Uncovered by ASR/VAD interval union",
                    "Human_Classification": "",
                    "Reviewer_A": "",
                    "Reviewer_B": "",
                    "Adjudication": "",
                    "Status": "Machine-only; full-media human classification needed",
                }
            )
        cursor = max(cursor, end)
        previous_segment = str(row["Segment_ID"])
    if cursor < media_duration:
        gaps.append(
            {
                "Gap_ID": "",
                "Gap_Type": "Tail",
                "Start": format_hms(cursor),
                "End": format_hms(media_duration),
                "Duration_Seconds": f"{media_duration - cursor:.3f}",
                "Previous_Segment_ID": previous_segment,
                "Next_Segment_ID": "",
                "Machine_Disposition": "Uncovered by ASR/VAD interval union",
                "Human_Classification": "",
                "Reviewer_A": "",
                "Reviewer_B": "",
                "Adjudication": "",
                "Status": "Machine-only; full-media human classification needed",
            }
        )
    elif cursor > media_duration:
        raise ValueError("ASR interval union extends beyond media duration")
    for index, row in enumerate(gaps, start=1):
        row["Gap_ID"] = f"{gap_prefix}-{index:04d}"
    return gaps


def timeline_metrics(
    source_rows: Sequence[dict[str, object]],
    gap_rows: Sequence[dict[str, str]],
    *,
    media_duration: Decimal,
) -> dict[str, object]:
    interval_sum = sum(
        (as_decimal(row["End_Seconds"]) - as_decimal(row["Start_Seconds"]) for row in source_rows),
        Decimal("0"),
    )
    cursor = Decimal("0")
    union = Decimal("0")
    for row in source_rows:
        start = as_decimal(row["Start_Seconds"])
        end = as_decimal(row["End_Seconds"])
        if end <= cursor:
            continue
        union += end - max(start, cursor)
        cursor = end
    gap_seconds = sum((as_decimal(row["Duration_Seconds"]) for row in gap_rows), Decimal("0"))
    if union + gap_seconds != media_duration:
        raise ValueError("ASR interval union and gaps do not account for full media")
    return {
        "asr_interval_duration_sum_seconds": json_number(interval_sum),
        "asr_interval_union_seconds": json_number(union),
        "asr_interval_coverage_percent": float(
            (union / media_duration * 100).quantize(Decimal("0.001"))
        ),
        "uncovered_interval_count": len(gap_rows),
        "uncovered_seconds": json_number(gap_seconds),
        "lead_gap_count": sum(row["Gap_Type"] == "Lead" for row in gap_rows),
        "internal_gap_count": sum(row["Gap_Type"] == "Internal" for row in gap_rows),
        "tail_gap_count": sum(row["Gap_Type"] == "Tail" for row in gap_rows),
        "machine_accounted_timeline_seconds": json_number(union + gap_seconds),
    }


def validate_translation_rows(
    source_rows: Sequence[dict[str, object]],
    translation_rows: Sequence[dict[str, str]],
) -> None:
    source_ids = [str(row["Segment_ID"]) for row in source_rows]
    translated_ids = [str(row.get("Segment_ID", "")) for row in translation_rows]
    if translated_ids != source_ids:
        raise ValueError("translation IDs do not exactly match the source rows")
    for source, translated in zip(source_rows, translation_rows, strict=True):
        if not str(translated.get("Machine_EN", "")).strip():
            raise ValueError(f"empty machine English for {source['Segment_ID']}")
        if translated.get("Source_HE_SHA256") != source["Source_HE_SHA256"]:
            raise ValueError(f"source Hebrew hash mismatch for {source['Segment_ID']}")


def canonical_control_ids(
    value: str | Iterable[str],
    *,
    registered_control_ids: set[str] | frozenset[str] | None = None,
) -> tuple[str, ...]:
    items = (
        [item.strip() for item in value.split(";") if item.strip()]
        if isinstance(value, str)
        else [str(item).strip() for item in value if str(item).strip()]
    )
    if len(items) != len(set(items)):
        raise ValueError("duplicate August 12 control ID")
    for item in items:
        if CONTROL_PATTERN.fullmatch(item) is None:
            raise ValueError(f"invalid August 12 control ID: {item}")
        if registered_control_ids is not None and item not in registered_control_ids:
            raise ValueError(f"unregistered August 12 control ID: {item}")
    return tuple(
        sorted(
            items,
            key=lambda item: (CONTROL_ORDER[item.split("-", 1)[0]], int(item.rsplit("-", 1)[1])),
        )
    )


def load_control_mapping(
    path: Path,
    source_rows: Sequence[dict[str, object]],
) -> tuple[dict[str, tuple[str, ...]], frozenset[str]]:
    """Expand canonical register source spans into a reciprocal segment mapping."""

    if not path.is_file() or _is_reparse(path):
        raise ValueError("control register must be a regular non-reparse CSV")
    rows = list(csv.DictReader(path.open(encoding="utf-8", newline="")))
    if not rows:
        raise ValueError("control register is empty")
    source_ids = [str(row["Segment_ID"]) for row in source_rows]
    source_index = {segment_id: index for index, segment_id in enumerate(source_ids)}
    registered: set[str] = set()
    mapping: dict[str, list[str]] = {segment_id: [] for segment_id in source_ids}
    for row_number, row in enumerate(rows, start=2):
        control_id = str(row.get("Control_ID", "")).strip()
        if CONTROL_PATTERN.fullmatch(control_id) is None:
            raise ValueError(f"invalid control register ID at row {row_number}: {control_id}")
        if control_id in registered:
            raise ValueError(f"duplicate control register ID: {control_id}")
        registered.add(control_id)
        spans = str(row.get("Source_Spans", ""))
        span_tokens = re.findall(r"S12-[^;,\s]+", spans)
        residual = SEGMENT_SPAN_PATTERN.sub("", spans)
        if "S12" in residual.upper():
            raise ValueError(f"control {control_id} has a malformed segment span: {spans}")
        for token in span_tokens:
            match = SEGMENT_SPAN_PATTERN.fullmatch(token)
            if match is None:
                raise ValueError(f"control {control_id} has a malformed segment span: {token}")
            start_id = match.group(1)
            end_id = match.group(2) or start_id
            if start_id not in source_index or end_id not in source_index:
                raise ValueError(f"control {control_id} references an unknown segment")
            start_index = source_index[start_id]
            end_index = source_index[end_id]
            if end_index < start_index:
                raise ValueError(f"control {control_id} has a reversed segment span")
            for segment_id in source_ids[start_index : end_index + 1]:
                mapping[segment_id].append(control_id)
    registered_frozen = frozenset(registered)
    return (
        {
            segment_id: canonical_control_ids(values, registered_control_ids=registered_frozen)
            for segment_id, values in mapping.items()
            if values
        },
        registered_frozen,
    )


def build_machine_ledger(
    source_rows: Sequence[dict[str, object]],
    translation_rows: Sequence[dict[str, str]] | None = None,
    control_mapping: dict[str, Iterable[str]] | None = None,
) -> list[dict[str, str]]:
    if translation_rows is not None:
        validate_translation_rows(source_rows, translation_rows)
    translations = {
        str(row["Segment_ID"]): str(row["Machine_EN"]) for row in translation_rows or ()
    }
    control_mapping = control_mapping or {}
    result: list[dict[str, str]] = []
    for row in source_rows:
        segment_id = str(row["Segment_ID"])
        controls = canonical_control_ids(control_mapping.get(segment_id, ()))
        result.append(
            {
                "Segment_ID": segment_id,
                "Start": str(row["Start"]),
                "End": str(row["End"]),
                "Speaker": "Unresolved",
                "Speaker_Confidence": "Unknown",
                "Speaker_Basis": "No automatic diarization; human audiovisual review required",
                "Machine_HE": str(row["Machine_HE"]),
                "Reviewed_HE": "",
                "Machine_EN": translations.get(segment_id, ""),
                "Reviewed_EN": "",
                "Content_Class": "Context",
                "Control_IDs": "; ".join(controls),
                "Reviewer_A": "",
                "Reviewer_B": "",
                "Disagreement": "",
                "Adjudication": "",
                "Status": (
                    "Machine-only; human review needed"
                    if segment_id in translations
                    else "Machine-only; English translation and human review needed"
                ),
                "Evidence_Link": f"#segment-{segment_id.lower()}",
            }
        )
    return result


def translation_prompt(source_rows: Sequence[dict[str, object]]) -> str:
    source = "\n".join(f"{row['Segment_ID']} || {row['Machine_HE']}" for row in source_rows)
    return f"""Translate the Hebrew academic meeting-transcript segments below into faithful, natural English.
Each entry begins with an immutable meeting-scoped ID. Preserve names, technical English terms, uncertainty, questions, and interruptions. Do not summarize, add facts, repair terminology from outside context, or combine entries. Do not infer speakers. If a word is unintelligible, use [unclear] rather than guessing.

Return exactly one plain-text line for exactly one input entry, in this form:
ID || English translation
Return no heading, Markdown, notes, or source-language text.

SOURCE:
{source}
"""


def parse_translation_response(response: str, expected_ids: Sequence[str]) -> dict[str, str]:
    expected = tuple(expected_ids)
    expected_set = set(expected)
    parsed: dict[str, str] = {}
    extras: list[str] = []
    for line in response.splitlines():
        if not line.strip():
            continue
        match = TRANSLATION_LINE.fullmatch(line)
        if match is None:
            extras.append(line.strip())
            continue
        segment_id, english = match.groups()
        if segment_id in parsed:
            raise ValueError(f"duplicate translation ID: {segment_id}")
        if segment_id not in expected_set:
            extras.append(segment_id)
            continue
        parsed[segment_id] = english.strip()
    if extras:
        raise ValueError("unexpected translation output: " + "; ".join(extras))
    missing = [segment_id for segment_id in expected if segment_id not in parsed]
    if missing:
        raise ValueError("missing translation IDs: " + ", ".join(missing))
    return parsed


def translate_source_rows(
    source_rows: Sequence[dict[str, object]],
    requester,  # type: ignore[no-untyped-def]
    *,
    batch_size: int = 18,
) -> list[dict[str, str]]:
    if batch_size < 1:
        raise ValueError("batch_size must be positive")
    result: list[dict[str, str]] = []
    for offset in range(0, len(source_rows), batch_size):
        batch = list(source_rows[offset : offset + batch_size])
        expected_ids = tuple(str(row["Segment_ID"]) for row in batch)
        response = str(requester(batch))
        translations = parse_translation_response(response, expected_ids)
        for row in batch:
            segment_id = str(row["Segment_ID"])
            result.append(
                {
                    "Segment_ID": segment_id,
                    "Machine_EN": translations[segment_id],
                    "Source_HE_SHA256": str(row["Source_HE_SHA256"]),
                }
            )
    validate_translation_rows(source_rows, result)
    return result


def translate_with_checkpoints(
    source_rows: Sequence[dict[str, object]],
    requester,  # type: ignore[no-untyped-def]
    output_path: Path,
    *,
    batch_size: int = 18,
    event_logger=None,  # type: ignore[no-untyped-def]
    event_log_path: Path | None = None,
    run_context: dict[str, object] | None = None,
    run_metadata: dict[str, object] | None = None,
) -> list[dict[str, str]]:
    """Resume a local translation while binding every row to immutable Hebrew.

    A validated prefix is preserved.  Each newly completed batch is atomically
    checkpointed so an interrupted local-model run never masquerades as a
    complete translation.
    """

    if batch_size < 1:
        raise ValueError("batch_size must be positive")
    if (event_log_path is None) != (run_context is None):
        raise ValueError("event_log_path and run_context must be supplied together")
    existing: list[dict[str, str]] = []
    if output_path.exists():
        existing = [
            json.loads(line)
            for line in output_path.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
        if len(existing) > len(source_rows):
            raise ValueError("translation checkpoint has more rows than the source")
        expected_prefix = [str(row["Segment_ID"]) for row in source_rows[: len(existing)]]
        observed_prefix = [str(row.get("Segment_ID", "")) for row in existing]
        if observed_prefix != expected_prefix:
            raise ValueError("translation checkpoint IDs are not a source prefix")
        for source, translated in zip(source_rows[: len(existing)], existing, strict=True):
            if translated.get("Source_HE_SHA256") != source["Source_HE_SHA256"]:
                raise ValueError(f"source Hebrew hash mismatch for {source['Segment_ID']}")
            if not str(translated.get("Machine_EN", "")).strip():
                raise ValueError(f"empty machine English for {source['Segment_ID']}")
        if event_log_path is None or run_context is None:
            raise ValueError("an existing translation checkpoint requires bound event-ledger context")
        binding = validate_translation_event_ledger(
            event_log_path,
            output_path=output_path,
            run_context=run_context,
            expected_segments=len(source_rows),
            require_complete=len(existing) == len(source_rows),
        )
        if binding["status"] == "complete":
            validate_translation_rows(source_rows, existing)
            return existing

    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S.%fZ")

    def emit(event: dict[str, object]) -> None:
        record = {
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "run_id": run_id,
            **event,
        }
        if event_log_path is not None:
            append_jsonl_event(event_log_path, record)
        if event_logger is not None:
            event_logger(record)

    if run_context is not None:
        emit({"event": "translation_run_started", **run_context, **(run_metadata or {})})

    def log(event: str, batch: Sequence[dict[str, object]], **extra: object) -> None:
        if event_logger is None and event_log_path is None:
            return
        emit(
            {
                "event": event,
                "segment_ids": [str(row["Segment_ID"]) for row in batch],
                "prompt_sha256": sha256_text(translation_prompt(batch)),
                **extra,
            }
        )

    def checkpoint(rows: Sequence[dict[str, str]]) -> None:
        rendered = _render_jsonl(rows)
        temporary = output_path.with_suffix(output_path.suffix + ".tmp")
        temporary.write_text(rendered, encoding="utf-8", newline="\n")
        temporary.replace(output_path)
        if event_log_path is not None:
            emit(
                {
                    "event": "checkpoint_saved",
                    "translated_segment_count": len(rows),
                    "checkpoint_bytes": output_path.stat().st_size,
                    "checkpoint_sha256": sha256_file(output_path),
                }
            )

    result = list(existing)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        for offset in range(len(existing), len(source_rows), batch_size):
            batch = list(source_rows[offset : offset + batch_size])
            log("batch_started", batch)
            try:
                translated = translate_source_rows(batch, requester, batch_size=len(batch))
            except Exception as error:
                log(
                    "batch_failed",
                    batch,
                    error_type=type(error).__name__,
                    error=str(error),
                )
                for row in batch:
                    single = [row]
                    log("row_started", single)
                    try:
                        translated_row = translate_source_rows(single, requester, batch_size=1)
                    except Exception as row_error:
                        log(
                            "row_failed",
                            single,
                            error_type=type(row_error).__name__,
                            error=str(row_error),
                        )
                        raise
                    result.extend(translated_row)
                    checkpoint(result)
                    log(
                        "row_completed",
                        single,
                        output_sha256=sha256_text(_render_jsonl(translated_row)),
                    )
            else:
                result.extend(translated)
                checkpoint(result)
                log(
                    "batch_completed",
                    batch,
                    output_sha256=sha256_text(_render_jsonl(translated)),
                )
    except Exception as error:
        if event_log_path is not None:
            emit(
                {
                    "event": "translation_run_failed",
                    "error_type": type(error).__name__,
                    "error": str(error),
                    "translated_segment_count": len(result),
                    "checkpoint_bytes": output_path.stat().st_size if output_path.exists() else 0,
                    "checkpoint_sha256": sha256_file(output_path) if output_path.exists() else None,
                }
            )
        raise
    validate_translation_rows(source_rows, result)
    if event_log_path is not None:
        emit(
            {
                "event": "translation_run_completed",
                "translated_segment_count": len(result),
                "output_bytes": output_path.stat().st_size,
                "output_sha256": sha256_file(output_path),
            }
        )
    return result


def _render_csv(rows: Sequence[dict[str, str]], fields: Sequence[str]) -> str:
    def safe_cell(value: object) -> object:
        if not isinstance(value, str) or not value:
            return value
        stripped = value.lstrip(" \t\r\n")
        if value.startswith(CSV_FORMULA_PREFIXES) or stripped.startswith(
            CSV_FORMULA_PREFIXES
        ):
            return "'" + value
        return value

    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=fields, lineterminator="\n")
    writer.writeheader()
    writer.writerows({field: safe_cell(row.get(field, "")) for field in fields} for row in rows)
    return buffer.getvalue()


def _render_jsonl(rows: Sequence[dict[str, object]]) -> str:
    return "".join(
        json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n" for row in rows
    )


def build_review_template(
    source_rows: Sequence[dict[str, object]],
    gap_rows: Sequence[dict[str, str]],
) -> list[dict[str, str]]:
    records = [
        {"Record_ID": str(row["Segment_ID"]), "Record_Type": "Segment"} for row in source_rows
    ]
    records.extend({"Record_ID": str(row["Gap_ID"]), "Record_Type": "ASR gap"} for row in gap_rows)
    records.append({"Record_ID": MEDIA_TIMELINE_ID, "Record_Type": "Full media timeline"})
    return [{field: record.get(field, "") for field in REVIEW_FIELDS} for record in records]


def _is_reparse(path: Path) -> bool:
    if path.is_symlink():
        return True
    try:
        attributes = getattr(path.stat(follow_symlinks=False), "st_file_attributes", 0)
    except (FileNotFoundError, OSError):
        return False
    return bool(attributes & 0x400)


def validate_ollama_base_url(value: str) -> str:
    """Accept only an uncredentialed HTTP endpoint on the local loopback."""

    parsed = urlsplit(value.rstrip("/"))
    if parsed.scheme != "http" or not parsed.hostname:
        raise ValueError("Ollama URL must use HTTP on a loopback host")
    if parsed.username is not None or parsed.password is not None:
        raise ValueError("Ollama URL must not contain credentials")
    if parsed.query or parsed.fragment or parsed.path not in {"", "/"}:
        raise ValueError("Ollama URL must not contain a path, query, or fragment")
    hostname = parsed.hostname.casefold()
    try:
        address = ipaddress.ip_address(hostname)
    except ValueError as error:
        raise ValueError("Ollama URL host must be a numeric loopback address") from error
    if not address.is_loopback:
        raise ValueError("Ollama URL host is not loopback")
    try:
        port = parsed.port
    except ValueError as error:
        raise ValueError("Ollama URL has an invalid port") from error
    if port is not None and not 1 <= port <= 65535:
        raise ValueError("Ollama URL has an invalid port")
    host_text = f"[{hostname}]" if ":" in hostname else hostname
    return f"http://{host_text}{f':{port}' if port is not None else ''}"


def _require_under_root(path: Path, root: Path, *, label: str) -> Path:
    lexical = Path(os.path.abspath(path))
    try:
        relative = lexical.relative_to(root)
    except ValueError as error:
        raise ValueError(f"{label} is outside the allowed private root") from error
    current = root
    for part in relative.parts:
        current /= part
        if current.exists() and _is_reparse(current):
            raise ValueError(f"{label} contains a symlink or reparse escape")
    resolved = lexical.resolve(strict=False)
    try:
        resolved.relative_to(root)
    except ValueError as error:
        raise ValueError(f"{label} is outside the allowed private root") from error
    return resolved


def _resolve_evidence_roots(
    *,
    allowed_root: Path,
    repo_root: Path,
    hf_cache_root: Path,
    ollama_cache_root: Path | None,
) -> tuple[Path, Path, Path, Path | None]:
    roots: list[tuple[str, Path]] = [
        ("allowed private root", allowed_root),
        ("repository root", repo_root),
        ("Hugging Face cache root", hf_cache_root),
    ]
    if ollama_cache_root is not None:
        roots.append(("Ollama cache root", ollama_cache_root))
    resolved: dict[str, Path] = {}
    for label, root in roots:
        if not root.is_dir() or _is_reparse(root):
            raise ValueError(f"{label} must be an existing non-reparse directory")
        resolved[label] = root.resolve(strict=True)
    private_root = resolved["allowed private root"]
    repository = resolved["repository root"]
    if private_root == repository:
        raise ValueError("allowed private root must be separate from the repository")
    for outer, inner, message in (
        (private_root, repository, "allowed private root must not contain the repository"),
        (repository, private_root, "allowed private root must remain outside the repository"),
    ):
        try:
            inner.relative_to(outer)
        except ValueError:
            pass
        else:
            raise ValueError(message)
    for label in ("Hugging Face cache root", "Ollama cache root"):
        cache_root = resolved.get(label)
        if cache_root is None:
            continue
        try:
            cache_root.relative_to(repository)
        except ValueError:
            pass
        else:
            raise ValueError(f"{label} must remain outside the repository")
    return (
        private_root,
        repository,
        resolved["Hugging Face cache root"],
        resolved.get("Ollama cache root"),
    )


def _require_regular_file_under_root(path: Path, root: Path, *, label: str) -> Path:
    resolved = _require_under_root(path, root, label=label)
    if not path.is_file() or _is_reparse(path):
        raise ValueError(f"{label} must be a regular non-reparse file")
    return resolved


def _validate_provenance_path_policy(
    provenance_path: Path,
    artifacts: dict[str, dict[str, object]],
    *,
    allowed_root: Path,
    repo_root: Path,
    hf_cache_root: Path,
    ollama_cache_root: Path | None,
) -> tuple[Path, Path, Path, Path | None]:
    private_root, repository, hf_root, ollama_root = _resolve_evidence_roots(
        allowed_root=allowed_root,
        repo_root=repo_root,
        hf_cache_root=hf_cache_root,
        ollama_cache_root=ollama_cache_root,
    )
    _require_regular_file_under_root(
        provenance_path, private_root, label="private provenance"
    )
    unsupported = sorted(set(artifacts) - SUPPORTED_PROVENANCE_ROLES)
    if unsupported:
        raise ValueError("unsupported private provenance roles: " + ", ".join(unsupported))
    for role in sorted(PRIVATE_EVIDENCE_ROLES & set(artifacts)):
        _require_regular_file_under_root(
            Path(str(artifacts[role].get("path", ""))),
            private_root,
            label=role,
        )
    for role in sorted(HF_CACHE_ROLES & set(artifacts)):
        candidate = _require_regular_file_under_root(
            Path(str(artifacts[role].get("path", ""))),
            hf_root,
            label=role,
        )
        repository_slug = str(AUG12_SOURCE_PROFILE["asr_model_repository"]).replace(
            "/", "--"
        )
        expected = (
            hf_root
            / f"models--{repository_slug}"
            / "blobs"
            / str(AUG12_SOURCE_PROFILE["asr_model_blob_sha256"]).lower()
        )
        if candidate != expected.resolve(strict=False):
            raise ValueError(f"{role} is not the exact Hugging Face cache path")
    present_ollama_roles = OLLAMA_CACHE_ROLES & set(artifacts)
    if present_ollama_roles and ollama_root is None:
        raise ValueError("Ollama cache root is required for translation model artifacts")
    for role in sorted(present_ollama_roles):
        assert ollama_root is not None
        candidate = _require_regular_file_under_root(
            Path(str(artifacts[role].get("path", ""))),
            ollama_root,
            label=role,
        )
        model_name, separator, model_tag = str(
            AUG12_SOURCE_PROFILE["translation_model_name"]
        ).rpartition(":")
        if not separator or not model_name or not model_tag:
            raise ValueError("translation model name cannot define an exact Ollama cache path")
        expected = (
            ollama_root
            / "blobs"
            / f"sha256-{str(AUG12_SOURCE_PROFILE['ollama_model_blob_sha256']).lower()}"
            if role == "ollama_model_blob"
            else ollama_root
            / "manifests"
            / "registry.ollama.ai"
            / "library"
            / model_name
            / model_tag
        )
        if candidate != expected.resolve(strict=False):
            raise ValueError(f"{role} is not the exact Ollama cache path")
    trusted_paths = {
        "control_register": repository
        / "docs"
        / "research"
        / "meetings"
        / "2026-08-12-control-register.csv",
        "evidence_builder": Path(__file__).resolve(),
    }
    for role in sorted(TRUSTED_REPO_ROLES & set(artifacts)):
        candidate = Path(str(artifacts[role].get("path", "")))
        try:
            _require_regular_file_under_root(candidate, private_root, label=role)
        except ValueError:
            trusted = trusted_paths[role].resolve(strict=False)
            if Path(os.path.abspath(candidate)) != trusted:
                raise ValueError(
                    f"{role} is neither private nor the exact trusted repository file"
                ) from None
            _require_regular_file_under_root(trusted, repository, label=role)
    return private_root, repository, hf_root, ollama_root


def _validate_hf_snapshot_path(snapshot_path: Path, hf_root: Path) -> Path:
    repository_slug = str(AUG12_SOURCE_PROFILE["asr_model_repository"]).replace("/", "--")
    expected = (
        hf_root
        / f"models--{repository_slug}"
        / "snapshots"
        / str(AUG12_SOURCE_PROFILE["asr_model_snapshot_commit"])
    )
    lexical = Path(os.path.abspath(snapshot_path))
    if lexical != expected:
        raise ValueError("ASR snapshot is not the exact Hugging Face cache path")
    if not lexical.is_dir() or _is_reparse(lexical):
        raise ValueError("ASR snapshot must be a regular non-reparse directory")
    _require_under_root(lexical, hf_root, label="ASR snapshot")
    for entry in lexical.rglob("*"):
        if not _is_reparse(entry):
            continue
        try:
            target = entry.resolve(strict=True)
            target.relative_to(hf_root)
        except (FileNotFoundError, OSError, ValueError) as error:
            raise ValueError(
                "ASR snapshot symlink resolves outside the Hugging Face cache root"
            ) from error
        if not target.is_file() or _is_reparse(target):
            raise ValueError("ASR snapshot symlink target is not a regular cache file")
    return lexical


def validate_translation_paths(
    *,
    source_path: Path,
    output_path: Path,
    event_log_path: Path,
    allowed_root: Path,
    repo_root: Path,
) -> tuple[Path, Path, Path]:
    """Constrain all transcript-bearing translation I/O to a private root."""

    if not allowed_root.is_dir() or _is_reparse(allowed_root):
        raise ValueError("allowed private root must be an existing non-reparse directory")
    if not repo_root.is_dir() or _is_reparse(repo_root):
        raise ValueError("repository root must be an existing non-reparse directory")
    private_root = allowed_root.resolve(strict=True)
    repository = repo_root.resolve(strict=True)
    if private_root == repository:
        raise ValueError("allowed private root must be separate from the repository")
    try:
        repository.relative_to(private_root)
    except ValueError:
        pass
    else:
        raise ValueError("allowed private root must not contain the repository")
    try:
        private_root.relative_to(repository)
    except ValueError:
        pass
    else:
        raise ValueError("allowed private root must remain outside the repository")
    source = _require_under_root(source_path, private_root, label="translation source")
    output = _require_under_root(output_path, private_root, label="translation output")
    event_log = _require_under_root(event_log_path, private_root, label="translation event log")
    if not source_path.is_file() or _is_reparse(source_path):
        raise ValueError("translation source must be a regular non-reparse file")
    for label, candidate in (("translation output", output_path), ("translation event log", event_log_path)):
        if candidate.exists() and (not candidate.is_file() or _is_reparse(candidate)):
            raise ValueError(f"{label} must be a regular non-reparse file")
    for label, candidate in (
        ("translation source", source),
        ("translation output", output),
        ("translation event log", event_log),
    ):
        try:
            candidate.relative_to(repository)
        except ValueError:
            pass
        else:
            raise ValueError(f"{label} must remain outside the repository")
    if len({source, output, event_log}) != 3:
        raise ValueError("translation source, output, and event log must be distinct files")
    return source, output, event_log


def _artifact_map(provenance: dict[str, object]) -> dict[str, dict[str, object]]:
    artifacts = provenance.get("artifacts")
    if not isinstance(artifacts, list):
        raise ValueError("private provenance must contain an artifacts list")
    result: dict[str, dict[str, object]] = {}
    for record in artifacts:
        if not isinstance(record, dict):
            raise ValueError("private provenance artifact is not an object")
        role = str(record.get("role", ""))
        if not role or role in result:
            raise ValueError("private provenance has an empty or duplicate artifact role")
        result[role] = dict(record)
    return result


def validate_media_comparison(
    comparison_path: Path,
    artifacts: dict[str, dict[str, object]],
    *,
    media_duration: Decimal,
) -> dict[str, object]:
    profile = AUG12_SOURCE_PROFILE
    if as_decimal(profile.get("media_duration_seconds")) != media_duration:
        raise ValueError("selected media duration does not match the locked August 12 profile")
    payload = json.loads(comparison_path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict) or payload.get("schema_version") != (
        "Aug12MeetingAudioComparison-v1"
    ):
        raise ValueError("media comparison has an invalid schema")
    if payload.get("audio_evidence_equivalent") is not True or payload.get("differences") != []:
        raise ValueError("media comparison does not establish audio evidence equivalence")
    records = [payload.get("primary"), payload.get("secondary")]
    if any(not isinstance(record, dict) for record in records):
        raise ValueError("media comparison lacks primary or secondary fingerprints")
    fingerprints = [dict(record) for record in records if isinstance(record, dict)]
    by_source_hash = {str(record.get("source_sha256", "")).upper(): record for record in fingerprints}
    if len(by_source_hash) != 2:
        raise ValueError("media comparison does not bind two distinct raw source hashes")
    for role in ("raw_audio", "raw_video"):
        artifact = artifacts[role]
        if str(artifact["sha256"]).upper() != str(profile[f"{role}_sha256"]):
            raise ValueError(f"{role} does not match the locked August 12 source hash")
        if artifact["bytes"] != profile[f"{role}_bytes"]:
            raise ValueError(f"{role} does not match the locked August 12 source size")
        expected_hash = str(artifact["sha256"]).upper()
        record = by_source_hash.get(expected_hash)
        if record is None:
            raise ValueError(f"media comparison does not bind {role}")
        if record.get("source_bytes") != artifact["bytes"]:
            raise ValueError(f"media comparison byte-size drift for {role}")
        source_path = Path(str(artifact["path"]))
        if record.get("source_name") != source_path.name:
            raise ValueError(f"media comparison source-name drift for {role}")
    required_equal = (
        "encoded_packet_sha256",
        "packet_timing_sha256",
        "canonical_pcm_sha256",
        "canonical_pcm_samples",
        "canonical_pcm_rate_hz",
        "canonical_pcm_channels",
        "canonical_pcm_format",
        "duration_seconds",
    )
    primary, secondary = fingerprints
    for field in required_equal:
        if primary.get(field) != secondary.get(field):
            raise ValueError(f"media comparison {field} differs")
    for record in fingerprints:
        if record.get("audio_stream_count") != 1:
            raise ValueError("media comparison requires exactly one audio stream per source")
        if record.get("audio_codec") != "aac":
            raise ValueError("media comparison requires the expected AAC source codec")
        if record.get("canonical_pcm_rate_hz") != 16_000:
            raise ValueError("media comparison canonical PCM rate mismatch")
        if record.get("canonical_pcm_channels") != 1:
            raise ValueError("media comparison canonical PCM channel mismatch")
        if record.get("canonical_pcm_format") != "s16le":
            raise ValueError("media comparison canonical PCM format mismatch")
        if as_decimal(record.get("duration_seconds")) != media_duration:
            raise ValueError("media comparison duration does not match --media-duration")
        samples = record.get("canonical_pcm_samples")
        if not isinstance(samples, int) or samples <= 0:
            raise ValueError("media comparison canonical PCM sample count is invalid")
        if Decimal(samples) / Decimal(16_000) != media_duration:
            raise ValueError("media comparison PCM samples do not match media duration")
        for field in ("encoded_packet_sha256", "packet_timing_sha256", "canonical_pcm_sha256"):
            if re.fullmatch(r"[0-9A-F]{64}", str(record.get(field, "")).upper()) is None:
                raise ValueError(f"media comparison {field} is invalid")
        for field in (
            "encoded_packet_sha256",
            "packet_timing_sha256",
            "canonical_pcm_sha256",
            "canonical_pcm_samples",
        ):
            observed = record.get(field)
            expected = profile[field]
            if isinstance(expected, str):
                observed = str(observed).upper()
            if observed != expected:
                raise ValueError(f"media comparison {field} does not match the locked profile")
    if RECOMPUTE_MEDIA_FINGERPRINTS:
        for role in ("raw_audio", "raw_video"):
            artifact = artifacts[role]
            stored = by_source_hash[str(artifact["sha256"]).upper()]
            recomputed = fingerprint_audio(Path(str(artifact["path"])))
            if recomputed != stored:
                differing = sorted(
                    key
                    for key in set(recomputed) | set(stored)
                    if recomputed.get(key) != stored.get(key)
                )
                raise ValueError(
                    f"recomputed {role} fingerprint differs from comparison: {', '.join(differing)}"
                )
    return payload


def load_jsonl_objects(path: Path, *, label: str) -> list[dict[str, object]]:
    if not path.is_file() or _is_reparse(path):
        raise ValueError(f"{label} must be a regular non-reparse JSONL file")
    result: list[dict[str, object]] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            record = json.loads(line)
        except json.JSONDecodeError as error:
            raise ValueError(f"invalid {label} JSON at line {line_number}") from error
        if not isinstance(record, dict):
            raise ValueError(f"{label} line {line_number} is not an object")
        result.append(dict(record))
    return result


def translation_run_context(
    *,
    source_path: Path,
    source_rows: Sequence[dict[str, object]],
    generator_script_sha256: str,
    model: str,
    model_digest: str,
    options: dict[str, object],
    batch_size: int,
    timeout_seconds: int,
) -> dict[str, object]:
    return {
        "source_name": source_path.name,
        "source_bytes": source_path.stat().st_size,
        "source_sha256": sha256_file(source_path),
        "source_segment_count": len(source_rows),
        "script_sha256": generator_script_sha256.upper(),
        "model": model,
        "model_digest": model_digest.lower(),
        "options": dict(options),
        "batch_size": batch_size,
        "timeout_seconds": timeout_seconds,
        "translation_prompt_template_sha256": sha256_text(translation_prompt([])),
    }


def _parse_event_timestamp(value: object, *, label: str) -> datetime:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{label} has a blank timestamp")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as error:
        raise ValueError(f"{label} has an invalid timestamp") from error
    if parsed.tzinfo is None:
        raise ValueError(f"{label} timestamp is not timezone-aware")
    return parsed


def validate_translation_event_ledger(
    event_log_path: Path,
    *,
    output_path: Path,
    run_context: dict[str, object],
    expected_segments: int,
    require_complete: bool,
) -> dict[str, object]:
    """Bind a checkpoint to the newest ordered run in an append-only event ledger."""

    events = load_jsonl_objects(event_log_path, label="translation event ledger")
    if not events:
        raise ValueError("translation event ledger is empty")
    previous_timestamp: datetime | None = None
    starts: list[tuple[int, dict[str, object]]] = []
    for index, event in enumerate(events):
        timestamp = _parse_event_timestamp(event.get("timestamp_utc"), label=f"event {index + 1}")
        if previous_timestamp is not None and timestamp < previous_timestamp:
            raise ValueError("translation event timestamps are out of order")
        previous_timestamp = timestamp
        run_id = str(event.get("run_id", "")).strip()
        if not run_id:
            raise ValueError("translation event has a blank run_id")
        if event.get("event") == "translation_run_started":
            starts.append((index, event))
    if not starts:
        raise ValueError("translation event ledger has no run start")
    start_index, start = starts[-1]
    run_id = str(start["run_id"])
    for field, expected in run_context.items():
        observed = start.get(field)
        if field == "script_sha256":
            observed = str(observed or "").upper()
        elif field == "model_digest":
            observed = str(observed or "").lower()
        if observed != expected:
            raise ValueError(f"translation run start {field} drift")
    run_events = [
        (index, event)
        for index, event in enumerate(events[start_index:], start=start_index)
        if str(event.get("run_id", "")) == run_id
    ]
    completions = [
        (index, event) for index, event in run_events if event.get("event") == "translation_run_completed"
    ]
    output_sha = sha256_file(output_path)
    output_bytes = output_path.stat().st_size
    if completions:
        completion_index, completion = completions[-1]
        if completion_index <= start_index:
            raise ValueError("translation completion precedes its run start")
        if len(completions) != 1:
            raise ValueError("translation run has multiple completion events")
        if completion.get("translated_segment_count") != expected_segments:
            raise ValueError("translation completion count mismatch")
        if completion.get("output_bytes") != output_bytes:
            raise ValueError("translation completion byte-size mismatch")
        if str(completion.get("output_sha256", "")).upper() != output_sha:
            raise ValueError("translation completion output hash mismatch")
        if completion_index != len(events) - 1:
            raise ValueError("translation event ledger has events after completion")
        return {"status": "complete", "run_id": run_id, "start": start, "terminal": completion}
    if require_complete:
        raise ValueError("latest translation run is incomplete")
    checkpoints = [
        event for _, event in run_events if event.get("event") == "checkpoint_saved"
    ]
    terminals = [
        event
        for _, event in run_events
        if event.get("event") in {"translation_run_failed", "translation_run_interrupted"}
    ]
    candidates = checkpoints + terminals[-1:]
    binding = next(
        (
            event
            for event in reversed(candidates)
            if str(event.get("checkpoint_sha256", "")).upper() == output_sha
            and event.get("checkpoint_bytes") == output_bytes
        ),
        None,
    )
    if binding is None:
        raise ValueError("translation checkpoint is not bound to the latest event-ledger run")
    count = binding.get("translated_segment_count")
    if not isinstance(count, int) or count < 1 or count >= expected_segments:
        raise ValueError("translation checkpoint count is invalid")
    return {"status": "partial", "run_id": run_id, "start": start, "terminal": binding}


def validate_translation_attempt_comparison(
    translation: dict[str, object],
    artifacts: dict[str, dict[str, object]],
) -> dict[str, object]:
    """Validate the text-free, event-bound comparison and its claim boundary."""

    binding = translation.get("attempt_comparison")
    expected_roles = {
        "report_role": "translation_comparison_report",
        "generator_script_role": "translation_comparison_generator",
        "attempt_01_role": "translation_attempt_01_partial",
        "attempt_01_event_role": "translation_attempt_01_event_log",
        "attempt_02_role": "machine_english",
        "attempt_02_event_role": "translation_event_log",
    }
    if binding != expected_roles:
        raise ValueError("translation attempt comparison roles are not fully bound")
    report_path = Path(str(artifacts["translation_comparison_report"]["path"]))
    report = json.loads(report_path.read_text(encoding="utf-8"))
    if not isinstance(report, dict) or report.get("schema_version") != (
        "Aug12TranslationAttemptComparison-v1"
    ):
        raise ValueError("translation attempt comparison has an invalid schema")
    expected_counts = {
        "prefix_rows": AUG12_SOURCE_PROFILE["translation_comparison_prefix_rows"],
        "compared_rows": AUG12_SOURCE_PROFILE["translation_comparison_prefix_rows"],
        "exact_match_rows": AUG12_SOURCE_PROFILE["translation_comparison_exact_rows"],
        "changed_rows": AUG12_SOURCE_PROFILE["translation_comparison_changed_rows"],
    }
    if any(report.get(field) != value for field, value in expected_counts.items()):
        raise ValueError("translation attempt comparison counts drift")
    if (
        report.get("contains_transcript_text") is not False
        or report.get("parameter_comparability")
        != "event_metadata_partially_evidenced"
        or "requires bilingual human review"
        not in str(report.get("claim_boundary", "")).casefold()
    ):
        raise ValueError("translation attempt comparison claim boundary is unsafe")
    rendered = json.dumps(report, ensure_ascii=False).casefold()
    if any(
        phrase in rendered
        for phrase in ("deterministic translation", "reproducible output")
    ):
        raise ValueError("translation attempt comparison makes a forbidden stability claim")
    attempt_01 = report.get("attempt_01")
    attempt_02 = report.get("attempt_02")
    event_evidence = report.get("event_evidence")
    if not all(isinstance(item, dict) for item in (attempt_01, attempt_02, event_evidence)):
        raise ValueError("translation attempt comparison evidence is incomplete")
    assert isinstance(attempt_01, dict)
    assert isinstance(attempt_02, dict)
    assert isinstance(event_evidence, dict)
    event_01 = event_evidence.get("attempt_01")
    event_02 = event_evidence.get("attempt_02")
    if not isinstance(event_01, dict) or not isinstance(event_02, dict):
        raise ValueError("translation attempt event evidence is incomplete")
    if (
        str(attempt_01.get("sha256", "")).upper()
        != str(artifacts["translation_attempt_01_partial"]["sha256"]).upper()
        or str(attempt_02.get("sha256", "")).upper()
        != str(artifacts["machine_english"]["sha256"]).upper()
        or str(event_01.get("event_ledger_sha256", "")).upper()
        != str(artifacts["translation_attempt_01_event_log"]["sha256"]).upper()
        or str(event_02.get("event_ledger_sha256", "")).upper()
        != str(artifacts["translation_event_log"]["sha256"]).upper()
        or event_evidence.get("generator_script_hash_match") is not False
    ):
        raise ValueError("translation attempts are not cross-bound to the comparison report")
    return report


def validate_private_provenance(
    provenance_path: Path,
    *,
    source_path: Path,
    translation_path: Path | None,
    expected_segments: int,
    media_duration: Decimal,
    allowed_root: Path,
    repo_root: Path,
    hf_cache_root: Path,
    ollama_cache_root: Path | None,
) -> tuple[dict[str, object], str]:
    if not provenance_path.is_file() or _is_reparse(provenance_path):
        raise ValueError("private provenance must be a regular non-reparse file")
    provenance = json.loads(provenance_path.read_text(encoding="utf-8"))
    if not isinstance(provenance, dict):
        raise ValueError("private provenance is not a JSON object")
    if provenance.get("schema_version") != "Aug12MeetingPrivateProvenance-v1":
        raise ValueError("unsupported private provenance schema")
    artifacts = _artifact_map(provenance)
    resolved_private_root, _, resolved_hf_cache_root, _ = _validate_provenance_path_policy(
        provenance_path,
        artifacts,
        allowed_root=allowed_root,
        repo_root=repo_root,
        hf_cache_root=hf_cache_root,
        ollama_cache_root=ollama_cache_root,
    )
    _require_regular_file_under_root(
        source_path, resolved_private_root, label="selected source"
    )
    if translation_path is not None:
        _require_regular_file_under_root(
            translation_path, resolved_private_root, label="selected translation"
        )
    missing_roles = sorted(REQUIRED_PROVENANCE_ROLES - set(artifacts))
    if missing_roles:
        raise ValueError("private provenance missing roles: " + ", ".join(missing_roles))
    for role, record in artifacts.items():
        candidate = Path(str(record.get("path", "")))
        if not candidate.is_absolute() or not candidate.is_file() or _is_reparse(candidate):
            raise ValueError(f"{role} is not a regular absolute source file")
        expected_sha = str(record.get("sha256", "")).upper()
        if not re.fullmatch(r"[0-9A-F]{64}", expected_sha):
            raise ValueError(f"{role} has an invalid SHA-256")
        if sha256_file(candidate) != expected_sha:
            raise ValueError(f"{role} hash drift")
        expected_bytes = record.get("bytes")
        if expected_bytes != candidate.stat().st_size:
            raise ValueError(f"{role} byte-size drift")
    locked_roles = (
        "raw_audio",
        "raw_video",
        "raw_chat",
        "recording_config",
        "hebrew_asr",
        "hebrew_asr_readable",
        "asr_generator_script",
        "asr_task_log",
        "asr_model_blob",
        "control_register",
    )
    for role in locked_roles:
        record = artifacts[role]
        if str(record["sha256"]).upper() != str(
            AUG12_SOURCE_PROFILE[f"{role}_sha256"]
        ).upper():
            raise ValueError(f"{role} does not match the locked August 12 evidence hash")
        if record["bytes"] != AUG12_SOURCE_PROFILE[f"{role}_bytes"]:
            raise ValueError(f"{role} does not match the locked August 12 evidence size")
    if Path(str(artifacts["hebrew_asr"]["path"])).resolve() != source_path.resolve():
        raise ValueError("hebrew_asr path does not bind the selected source")
    if Path(str(artifacts["evidence_builder"]["path"])).resolve() != Path(__file__).resolve():
        raise ValueError("evidence_builder path does not bind this script")
    validate_media_comparison(
        Path(str(artifacts["media_comparison"]["path"])),
        artifacts,
        media_duration=media_duration,
    )
    media = provenance.get("media")
    if not isinstance(media, dict):
        raise ValueError("media execution provenance is missing")
    if media.get("source_profile_id") != AUG12_SOURCE_PROFILE.get("profile_id"):
        raise ValueError("media execution does not bind the locked source profile")
    if (
        media.get("generator_script_role") != "media_fingerprint_generator"
        or media.get("task_log_role") != "media_fingerprint_task_log"
        or media.get("comparison_role") != "media_comparison"
        or media.get("input_roles") != ["raw_audio", "raw_video"]
    ):
        raise ValueError("media execution artifact roles are incomplete")
    media_command = media.get("command")
    if (
        not isinstance(media_command, dict)
        or not media_command.get("argv")
        or media_command.get("exit_code") != 0
    ):
        raise ValueError("media fingerprint command provenance is incomplete")

    asr = provenance.get("asr")
    if not isinstance(asr, dict) or asr.get("segment_count") != expected_segments:
        raise ValueError("ASR provenance segment count mismatch")
    if (
        expected_segments != AUG12_SOURCE_PROFILE["hebrew_asr_segment_count"]
        or asr.get("output_schema") != AUG12_SOURCE_PROFILE["hebrew_asr_schema"]
    ):
        raise ValueError("ASR output count or schema does not match the locked profile")
    asr_model = asr.get("model")
    asr_command = asr.get("command")
    if not isinstance(asr_model, dict) or not asr_model.get("name"):
        raise ValueError("ASR model provenance is incomplete")
    if asr_model.get("blob_role") != "asr_model_blob":
        raise ValueError("ASR model blob provenance is incomplete")
    if str(asr_model.get("blob_sha256", "")).upper() != str(
        artifacts["asr_model_blob"]["sha256"]
    ).upper():
        raise ValueError("ASR model blob hash is not semantically bound")
    if (
        asr_model.get("name") != AUG12_SOURCE_PROFILE["asr_model_name"]
        or asr_model.get("repository") != AUG12_SOURCE_PROFILE["asr_model_repository"]
        or asr_model.get("snapshot_commit")
        != AUG12_SOURCE_PROFILE["asr_model_snapshot_commit"]
        or str(asr_model.get("snapshot_tree_sha256", "")).upper()
        != AUG12_SOURCE_PROFILE["asr_model_snapshot_tree_sha256"]
    ):
        raise ValueError("ASR model snapshot identity does not match the locked profile")
    snapshot_path = _validate_hf_snapshot_path(
        Path(str(asr_model.get("snapshot_path", ""))), resolved_hf_cache_root
    )
    if (
        snapshot_path.name != AUG12_SOURCE_PROFILE["asr_model_snapshot_commit"]
        or sha256_tree(snapshot_path)
        != AUG12_SOURCE_PROFILE["asr_model_snapshot_tree_sha256"]
    ):
        raise ValueError("ASR model snapshot bytes do not match the locked profile")
    if (
        asr.get("generator_script_role") != "asr_generator_script"
        or asr.get("task_log_role") != "asr_task_log"
        or asr.get("source_role") != "raw_audio"
        or asr.get("output_role") != "hebrew_asr"
        or asr.get("readable_output_role") != "hebrew_asr_readable"
    ):
        raise ValueError("ASR execution artifact roles are incomplete")
    if not isinstance(asr_command, dict) or not asr_command.get("argv"):
        raise ValueError("ASR command provenance is incomplete")
    if asr_command.get("exit_code") != 0:
        raise ValueError("ASR command does not have a successful exit record")
    execution_record = asr.get("execution_record")
    expected_execution_record = {
        "record_type": "recovered-task-output-binding-v1",
        "source_sha256": str(artifacts["raw_audio"]["sha256"]).upper(),
        "output_sha256": str(artifacts["hebrew_asr"]["sha256"]).upper(),
        "readable_output_sha256": str(
            artifacts["hebrew_asr_readable"]["sha256"]
        ).upper(),
        "generator_script_sha256": str(
            artifacts["asr_generator_script"]["sha256"]
        ).upper(),
        "task_log_sha256": str(artifacts["asr_task_log"]["sha256"]).upper(),
        "model_snapshot_tree_sha256": str(
            asr_model["snapshot_tree_sha256"]
        ).upper(),
        "model_blob_sha256": str(artifacts["asr_model_blob"]["sha256"]).upper(),
        "segment_count": expected_segments,
        "exit_code": 0,
    }
    if execution_record != expected_execution_record:
        raise ValueError("ASR recovered execution record is not bound to the locked chain")
    builder = provenance.get("builder")
    if not isinstance(builder, dict) or builder.get("script_role") != "evidence_builder":
        raise ValueError("builder provenance is incomplete")
    builder_command = builder.get("command")
    if not isinstance(builder_command, dict) or not builder_command.get("argv"):
        raise ValueError("builder command provenance is incomplete")

    translation = provenance.get("translation")
    if not isinstance(translation, dict):
        raise ValueError("translation provenance is missing")
    translation_status = translation.get("status")
    if translation_status not in {"not_started", "in_progress", "complete"}:
        raise ValueError("translation provenance has an invalid status")
    if translation_path is None and translation_status == "complete":
        raise ValueError("complete translation provenance requires a translation input")
    if translation_path is not None:
        if translation_status != "complete":
            raise ValueError("translation input requires complete translation provenance")
        missing_translation_roles = sorted(
            REQUIRED_TRANSLATION_PROVENANCE_ROLES - set(artifacts)
        )
        if missing_translation_roles:
            raise ValueError(
                "private provenance missing roles: " + ", ".join(missing_translation_roles)
            )
        if Path(str(artifacts["machine_english"]["path"])).resolve() != translation_path.resolve():
            raise ValueError("machine_english path does not bind the selected translation")
        for role in REQUIRED_TRANSLATION_PROVENANCE_ROLES:
            record = artifacts[role]
            if str(record["sha256"]).upper() != str(
                AUG12_SOURCE_PROFILE[f"{role}_sha256"]
            ).upper():
                raise ValueError(
                    f"{role} does not match the locked August 12 translation evidence hash"
                )
            if record["bytes"] != AUG12_SOURCE_PROFILE[f"{role}_bytes"]:
                raise ValueError(
                    f"{role} does not match the locked August 12 translation evidence size"
                )
        if translation.get("segment_count") != expected_segments:
            raise ValueError("translation provenance segment count mismatch")
        model = translation.get("model")
        command = translation.get("command")
        if not isinstance(model, dict) or not model.get("name") or not model.get("digest"):
            raise ValueError("translation model provenance is incomplete")
        if (
            model.get("name") != AUG12_SOURCE_PROFILE["translation_model_name"]
            or str(model.get("digest", "")).upper()
            != AUG12_SOURCE_PROFILE["translation_model_digest"]
        ):
            raise ValueError("translation model identity does not match the locked profile")
        if (
            model.get("blob_role") != "ollama_model_blob"
            or model.get("manifest_role") != "ollama_model_manifest"
        ):
            raise ValueError("translation model artifact provenance is incomplete")
        if str(model.get("blob_sha256", "")).upper() != str(
            artifacts["ollama_model_blob"]["sha256"]
        ).upper():
            raise ValueError("translation model blob hash is not semantically bound")
        if str(model.get("manifest_sha256", "")).upper() != str(
            artifacts["ollama_model_manifest"]["sha256"]
        ).upper():
            raise ValueError("translation model manifest hash is not semantically bound")
        if translation.get("generator_script_role") != "translation_generator_script":
            raise ValueError("translation generator provenance is incomplete")
        prompt_sha = str(translation.get("prompt_template_sha256", "")).upper()
        if prompt_sha != sha256_text(translation_prompt([])):
            raise ValueError("translation prompt template hash drift")
        if not isinstance(command, dict) or not command.get("argv"):
            raise ValueError("translation command provenance is incomplete")
        event_path = Path(str(artifacts["translation_event_log"]["path"]))
        source_rows = normalize_asr_lines(
            source_path.read_text(encoding="utf-8").splitlines(),
            expected_segments=expected_segments,
            media_duration=media_duration,
        )
        context = translation_run_context(
            source_path=source_path,
            source_rows=source_rows,
            generator_script_sha256=str(artifacts["translation_generator_script"]["sha256"]),
            model=str(model["name"]),
            model_digest=str(model["digest"]),
            options=dict(model.get("options", {})),
            batch_size=int(translation.get("batch_size", 18)),
            timeout_seconds=int(translation.get("timeout_seconds", 600)),
        )
        validate_translation_event_ledger(
            event_path,
            output_path=translation_path,
            run_context=context,
            expected_segments=expected_segments,
            require_complete=True,
        )
        validate_translation_attempt_comparison(translation, artifacts)

    rendered = json.dumps(provenance, ensure_ascii=False, indent=2) + "\n"
    return provenance, rendered


def build_package_contents(
    source_path: Path,
    *,
    expected_segments: int,
    media_duration: Decimal,
    provenance_path: Path,
    translation_path: Path | None = None,
    allowed_root: Path,
    repo_root: Path,
    hf_cache_root: Path,
    ollama_cache_root: Path | None = None,
) -> dict[str, str]:
    provenance, provenance_rendered = validate_private_provenance(
        provenance_path,
        source_path=source_path,
        translation_path=translation_path,
        expected_segments=expected_segments,
        media_duration=media_duration,
        allowed_root=allowed_root,
        repo_root=repo_root,
        hf_cache_root=hf_cache_root,
        ollama_cache_root=ollama_cache_root,
    )
    source_rows = normalize_asr_lines(
        source_path.read_text(encoding="utf-8").splitlines(),
        expected_segments=expected_segments,
        media_duration=media_duration,
    )
    translations: list[dict[str, str]] | None = None
    if translation_path is not None:
        translations = [
            json.loads(line)
            for line in translation_path.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
        validate_translation_rows(source_rows, translations)
    control_register_path = Path(
        str(_artifact_map(provenance)["control_register"]["path"])
    )
    control_mapping, registered_controls = load_control_mapping(
        control_register_path, source_rows
    )
    gaps = build_gap_rows(source_rows, media_duration=media_duration)
    metrics = timeline_metrics(source_rows, gaps, media_duration=media_duration)
    ledger = build_machine_ledger(source_rows, translations, control_mapping)
    review_template = build_review_template(source_rows, gaps)
    owner = {
        "schema_version": "Aug12MeetingPackageOwner-v1",
        "package_owner_id": "vego-ai-aug12-meeting-evidence",
        "source_provenance_sha256": sha256_text(provenance_rendered),
        "evidence_builder_sha256": sha256_file(Path(__file__)),
    }
    contents: dict[str, str] = {
        PACKAGE_OWNER_FILENAME: json.dumps(owner, indent=2) + "\n",
        "source-provenance.json": provenance_rendered,
        "machine-normalized.he.jsonl": _render_jsonl(source_rows),
        "machine-gap-ledger.csv": _render_csv(gaps, GAP_FIELDS),
        "machine-ledger.csv": _render_csv(ledger, LEDGER_FIELDS),
        "reviewer-a.csv": _render_csv(review_template, REVIEW_FIELDS),
        "reviewer-b.csv": _render_csv(review_template, REVIEW_FIELDS),
        "adjudication.csv": _render_csv([], ADJUDICATION_FIELDS),
    }
    preliminary = {
        "schema_version": "Aug12SupervisorMeetingLedger-v1",
        "evidence_boundary": (
            "Machine-only preliminary evidence. English is machine translation; "
            "speaker attribution, bilingual review, adjudication, and supervisor "
            "acceptance are not claimed."
        ),
        "human_review_completed": False,
        "source": {
            "name": source_path.name,
            "bytes": source_path.stat().st_size,
            "sha256": sha256_file(source_path),
        },
        "source_provenance": {
            "sha256": sha256_text(provenance_rendered),
            "schema_version": provenance["schema_version"],
        },
        "control_register": {
            "name": control_register_path.name,
            "sha256": sha256_file(control_register_path),
            "registered_control_count": len(registered_controls),
            "segments_with_machine_control_mapping": len(control_mapping),
            "mapping_status": "Machine-derived from canonical draft spans; human review pending",
        },
        "translation": (
            None
            if translation_path is None
            else {
                "name": translation_path.name,
                "bytes": translation_path.stat().st_size,
                "sha256": sha256_file(translation_path),
            }
        ),
        "coverage": {
            "segment_count": len(source_rows),
            "first_segment_start": source_rows[0]["Start"],
            "last_segment_end": source_rows[-1]["End"],
            "media_duration_seconds": json_number(media_duration),
            "human_reviewed_media_seconds": 0,
            "unreviewed_media_seconds": json_number(media_duration),
            **metrics,
        },
        "rows": ledger,
    }
    contents["preliminary-ledger.json"] = (
        json.dumps(preliminary, ensure_ascii=False, indent=2) + "\n"
    )
    artifact_manifest = {
        "schema_version": "Aug12MeetingPrivatePackageManifest-v1",
        "source_sha256": sha256_file(source_path),
        "artifacts": [
            {
                "name": name,
                "bytes": len(value.encode("utf-8")),
                "sha256": sha256_text(value),
            }
            for name, value in sorted(contents.items())
        ],
        "human_review_completed": False,
    }
    contents["artifact-manifest.json"] = (
        json.dumps(artifact_manifest, ensure_ascii=False, indent=2) + "\n"
    )
    if set(contents) != PACKAGE_FILENAMES:
        raise AssertionError("builder did not produce the exact code-owned inventory")
    return contents


def _validate_output_path(
    output_dir: Path,
    allowed_root: Path,
    repo_root: Path | None = None,
) -> None:
    if not allowed_root.is_dir() or _is_reparse(allowed_root):
        raise ValueError("allowed private root must be an existing regular directory")
    resolved_root = allowed_root.resolve(strict=True)
    repository = (repo_root or Path(__file__).resolve().parents[1]).resolve(strict=True)
    if resolved_root == repository:
        raise ValueError("allowed private root must be separate from the repository")
    try:
        repository.relative_to(resolved_root)
    except ValueError:
        pass
    else:
        raise ValueError("allowed private root must not contain the repository")
    try:
        resolved_root.relative_to(repository)
    except ValueError:
        pass
    else:
        raise ValueError("allowed private root must remain outside the repository")
    resolved_output = output_dir.resolve(strict=False)
    try:
        resolved_output.relative_to(resolved_root)
    except ValueError as error:
        raise ValueError("package output is outside the allowed private root") from error
    try:
        resolved_output.relative_to(repository)
    except ValueError:
        pass
    else:
        raise ValueError("package output must remain outside the repository")
    if output_dir.exists() and _is_reparse(output_dir):
        raise ValueError("package output is a symlink or reparse point")


def _validate_package_contents(contents: dict[str, str]) -> None:
    if set(contents) != PACKAGE_FILENAMES:
        missing = sorted(PACKAGE_FILENAMES - set(contents))
        extra = sorted(set(contents) - PACKAGE_FILENAMES)
        raise ValueError(f"invalid package inventory; missing={missing}; extra={extra}")
    if any(Path(name).name != name or name in {".", ".."} for name in contents):
        raise ValueError("package inventory contains path traversal")


def write_package(
    output_dir: Path,
    contents: dict[str, str],
    *,
    allowed_root: Path,
    repo_root: Path | None = None,
) -> None:
    _validate_package_contents(contents)
    _validate_output_path(output_dir, allowed_root, repo_root)
    if output_dir.exists():
        existing = {path.name for path in output_dir.iterdir()}
        if existing:
            owner_path = output_dir / PACKAGE_OWNER_FILENAME
            try:
                owner = json.loads(owner_path.read_text(encoding="utf-8"))
            except (FileNotFoundError, OSError, json.JSONDecodeError) as error:
                raise ValueError(
                    "existing package directory is not owned by this builder"
                ) from error
            if owner.get("package_owner_id") != "vego-ai-aug12-meeting-evidence":
                raise ValueError("existing package directory is not owned by this builder")
            if existing != PACKAGE_FILENAMES:
                raise ValueError("owned package inventory contains missing or unexpected files")
            if any(_is_reparse(path) for path in output_dir.iterdir()):
                raise ValueError("owned package contains a symlink or reparse file")
            for name in sorted(HUMAN_RETURN_FILENAMES):
                existing_bytes = (output_dir / name).read_bytes()
                expected_bytes = contents[name].encode("utf-8")
                if existing_bytes != expected_bytes:
                    raise ValueError(
                        f"refusing to overwrite changed human-return file: {name}; use a new versioned package"
                    )
    else:
        output_dir.mkdir(parents=True, exist_ok=False)
    for name, value in contents.items():
        if name in HUMAN_RETURN_FILENAMES and (output_dir / name).exists():
            continue
        (output_dir / name).write_text(value, encoding="utf-8", newline="\n")


def check_package(
    output_dir: Path,
    expected: dict[str, str],
    *,
    allowed_root: Path,
    repo_root: Path | None = None,
) -> list[str]:
    _validate_package_contents(expected)
    _validate_output_path(output_dir, allowed_root, repo_root)
    errors: list[str] = []
    if not output_dir.is_dir():
        return ["package directory is missing"]
    observed = {path.name for path in output_dir.iterdir()}
    for name in sorted(observed - PACKAGE_FILENAMES):
        errors.append(f"unexpected file: {name}")
    for name in sorted(PACKAGE_FILENAMES - observed):
        errors.append(f"{name} is missing")
    for name, value in expected.items():
        path = output_dir / name
        if not path.is_file() or _is_reparse(path):
            errors.append(f"{name} is missing")
            continue
        if path.read_text(encoding="utf-8") != value:
            errors.append(f"{name} differs from deterministic build")
    return errors


def compare_media_fingerprints(
    primary: dict[str, object], secondary: dict[str, object]
) -> list[str]:
    fields = (
        "encoded_packet_sha256",
        "packet_timing_sha256",
        "canonical_pcm_sha256",
        "canonical_pcm_samples",
    )
    return [f"{field} differs" for field in fields if primary.get(field) != secondary.get(field)]


def fingerprint_audio(path: Path, *, canonical_rate: int = 16_000) -> dict[str, object]:
    """Fingerprint encoded packets and decoded canonical PCM using local PyAV.

    PyAV is imported lazily so structure and ledger validation can run inside
    the project's dependency-isolated environment.  Media acceptance uses the
    separately recorded meeting-tool runtime.
    """

    try:
        import av  # type: ignore[import-not-found]
    except ImportError as error:
        raise RuntimeError(
            "PyAV is required only for media fingerprinting; use the frozen meeting-tool runtime"
        ) from error
    if canonical_rate < 1:
        raise ValueError("canonical_rate must be positive")

    encoded_digest = hashlib.sha256()
    timing_digest = hashlib.sha256()
    pcm_digest = hashlib.sha256()
    packet_count = 0
    packet_bytes = 0
    pcm_samples = 0

    with av.open(str(path), mode="r") as container:
        audio_streams = [stream for stream in container.streams if stream.type == "audio"]
        if len(audio_streams) != 1:
            raise ValueError(
                f"expected exactly one audio stream in {path.name}; found {len(audio_streams)}"
            )
        stream = audio_streams[0]
        resampler = av.audio.resampler.AudioResampler(
            format="s16", layout="mono", rate=canonical_rate
        )

        def consume(frame) -> None:  # type: ignore[no-untyped-def]
            nonlocal pcm_samples
            array = frame.to_ndarray()
            pcm_digest.update(array.tobytes(order="C"))
            pcm_samples += int(frame.samples)

        for packet in container.demux(stream):
            payload = bytes(packet)
            if payload:
                packet_count += 1
                packet_bytes += len(payload)
                encoded_digest.update(payload)
                timing_digest.update(
                    struct.pack(
                        ">qqqqq",
                        -1 if packet.pts is None else int(packet.pts),
                        -1 if packet.dts is None else int(packet.dts),
                        -1 if packet.duration is None else int(packet.duration),
                        int(packet.size),
                        int(stream.index),
                    )
                )
            for decoded in packet.decode():
                for frame in resampler.resample(decoded):
                    consume(frame)
        for frame in resampler.resample(None):
            consume(frame)

        duration_seconds = pcm_samples / canonical_rate
        codec = stream.codec_context
        library_versions = {
            name: ".".join(str(part) for part in version)
            for name, version in sorted(av.library_versions.items())
        }
        result: dict[str, object] = {
            "source_name": path.name,
            "source_bytes": path.stat().st_size,
            "source_sha256": sha256_file(path),
            "container_format": container.format.name,
            "audio_stream_count": len(audio_streams),
            "audio_codec": codec.name,
            "audio_sample_rate_hz": codec.sample_rate,
            "audio_channels": codec.channels,
            "encoded_packet_count": packet_count,
            "encoded_packet_bytes": packet_bytes,
            "encoded_packet_sha256": encoded_digest.hexdigest().upper(),
            "packet_timing_sha256": timing_digest.hexdigest().upper(),
            "canonical_pcm_format": "s16le",
            "canonical_pcm_rate_hz": canonical_rate,
            "canonical_pcm_channels": 1,
            "canonical_pcm_samples": pcm_samples,
            "canonical_pcm_bytes": pcm_samples * 2,
            "canonical_pcm_sha256": pcm_digest.hexdigest().upper(),
            "duration_seconds": float(f"{duration_seconds:.6f}"),
            "pyav_version": av.__version__,
            "ffmpeg_library_versions": library_versions,
        }
    return result


def require_ollama_model(
    tags_payload: dict[str, object], model_name: str, expected_digest: str
) -> dict[str, object]:
    models = tags_payload.get("models", [])
    if not isinstance(models, list):
        raise ValueError("Ollama tags response has no model list")
    match = next(
        (model for model in models if isinstance(model, dict) and model.get("name") == model_name),
        None,
    )
    if match is None:
        raise ValueError(f"Ollama model {model_name} is not available")
    observed = str(match.get("digest", "")).lower()
    if observed != expected_digest.lower():
        raise ValueError(
            f"Ollama model digest mismatch: expected {expected_digest}; observed {observed}"
        )
    return dict(match)


def _http_json(
    url: str,
    *,
    payload: dict[str, object] | None = None,
    timeout_seconds: int = 600,
) -> dict[str, object]:
    parsed_url = urlsplit(url)
    validate_ollama_base_url(f"{parsed_url.scheme}://{parsed_url.netloc}")
    if parsed_url.query or parsed_url.fragment:
        raise ValueError("Ollama request URL must not contain a query or fragment")
    body = None if payload is None else json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        url,
        data=body,
        method="GET" if body is None else "POST",
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(request, timeout=timeout_seconds) as response:
        parsed = json.loads(response.read().decode("utf-8"))
    if not isinstance(parsed, dict):
        raise ValueError(f"non-object JSON returned by {url}")
    return parsed


class OllamaRequester:
    def __init__(
        self,
        *,
        base_url: str,
        model: str,
        options: dict[str, object],
        timeout_seconds: int,
    ) -> None:
        self.base_url = validate_ollama_base_url(base_url)
        self.model = model
        self.options = dict(options)
        self.timeout_seconds = timeout_seconds

    def __call__(self, batch: Sequence[dict[str, object]]) -> str:
        payload = _http_json(
            self.base_url + "/api/generate",
            payload={
                "model": self.model,
                "prompt": translation_prompt(batch),
                "stream": False,
                "keep_alive": "30m",
                "options": self.options,
            },
            timeout_seconds=self.timeout_seconds,
        )
        if payload.get("done") is not True:
            raise ValueError("Ollama generation did not report done=true")
        response = payload.get("response")
        if not isinstance(response, str) or not response.strip():
            raise ValueError("Ollama returned an empty translation response")
        return response


def append_jsonl_event(path: Path, event: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(event, ensure_ascii=False, separators=(",", ":")))
        handle.write("\n")


def _valid_date(value: str) -> bool:
    try:
        date.fromisoformat(value)
    except ValueError:
        return False
    return True


def normalized_identity(value: str) -> str:
    return unicodedata.normalize("NFKC", value).strip().casefold()


def timeline_attestation(media_duration: Decimal) -> str:
    duration = f"{media_duration.quantize(Decimal('0.001')):.3f}"
    return (
        f"media_duration_seconds={duration}; reviewed_media_seconds={duration}; "
        "unreviewed_media_seconds=0.000"
    )


def _validate_attribution(
    row: dict[str, str],
    *,
    label: str,
    record_id: str,
) -> None:
    speaker = row.get("Speaker", "")
    confidence = row.get("Speaker_Confidence", "")
    basis = str(row.get("Speaker_Basis", "")).strip()
    if speaker not in SPEAKERS:
        raise ValueError(f"{label} has invalid speaker at {record_id}")
    if confidence not in SPEAKER_CONFIDENCE:
        raise ValueError(f"{label} has invalid speaker confidence at {record_id}")
    if not basis:
        raise ValueError(f"{label} has empty speaker basis at {record_id}")
    if speaker in NAMED_SPEAKERS:
        normalized_basis = basis.casefold()
        if confidence not in {"High", "Medium"} or not normalized_basis.startswith(
            NAMED_SPEAKER_BASIS_PREFIXES
        ):
            raise ValueError(f"{label} lacks evidence-grade named attribution at {record_id}")


def _validate_review_content(
    row: dict[str, str],
    *,
    label: str,
    record_id: str,
    record_type: str,
    registered_control_ids: frozenset[str],
    media_duration: Decimal,
) -> dict[str, str]:
    normalized = dict(row)
    content_class = str(row.get("Content_Class", ""))
    if content_class not in CONTENT_CLASSES:
        raise ValueError(f"{label} has invalid content class at {record_id}")
    controls = canonical_control_ids(
        str(row.get("Control_IDs", "")),
        registered_control_ids=registered_control_ids,
    )
    if content_class in SUBSTANTIVE_CLASSES and not controls:
        raise ValueError(f"{label} has substantive content without a registered control at {record_id}")
    normalized["Control_IDs"] = "; ".join(controls)
    notes = str(row.get("Review_Notes", "")).strip()
    if not notes:
        raise ValueError(f"{label} has empty review notes at {record_id}")
    if record_type == "Segment" or content_class in SUBSTANTIVE_CLASSES:
        if not str(row.get("Reviewed_HE", "")).strip():
            raise ValueError(f"{label} has empty reviewed Hebrew at {record_id}")
        if not str(row.get("Reviewed_EN", "")).strip():
            raise ValueError(f"{label} has empty reviewed English at {record_id}")
    if record_id == MEDIA_TIMELINE_ID:
        if notes != timeline_attestation(media_duration):
            raise ValueError(f"{label} lacks the exact full-media zero-unreviewed attestation")
        if row.get("Speaker") != "Non-speech" or content_class != "Noise or non-speech":
            raise ValueError(f"{label} has invalid full-media attestation classification")
    return normalized


def _validate_review(
    machine_rows: Sequence[dict[str, str]],
    gap_rows: Sequence[dict[str, str]],
    review_rows: Sequence[dict[str, str]],
    label: str,
    *,
    expected_reviewer_id: str,
    registered_control_ids: frozenset[str],
    media_duration: Decimal,
) -> tuple[dict[str, dict[str, str]], str]:
    if not review_rows:
        raise PendingReviews(f"{label} review is missing")
    segment_ids = [row["Segment_ID"] for row in machine_rows]
    gap_ids = [row["Gap_ID"] for row in gap_rows]
    expected = segment_ids + gap_ids + [MEDIA_TIMELINE_ID]
    observed = [str(row.get("Record_ID", "")) for row in review_rows]
    if observed != expected:
        raise PendingReviews(f"{label} review does not cover every segment, gap, and timeline")
    expected_identity = normalized_identity(expected_reviewer_id)
    if not expected_identity:
        raise ValueError(f"{label} expected reviewer identity is blank")
    reviewer_ids = {
        normalized_identity(str(row.get("Reviewer_ID", ""))) for row in review_rows
    }
    if reviewer_ids != {expected_identity}:
        raise ValueError(f"{label} is not bound to its explicit reviewer roster ID")
    normalized_rows: dict[str, dict[str, str]] = {}
    expected_types = {
        **{segment_id: "Segment" for segment_id in segment_ids},
        **{gap_id: "ASR gap" for gap_id in gap_ids},
        MEDIA_TIMELINE_ID: "Full media timeline",
    }
    for row in review_rows:
        record_id = str(row["Record_ID"])
        record_type = expected_types[record_id]
        if row.get("Record_Type") != record_type:
            raise ValueError(f"{label} has invalid record type at {record_id}")
        if not _valid_date(str(row.get("Review_Date", ""))):
            raise ValueError(f"{label} has invalid review date at {record_id}")
        _validate_attribution(row, label=label, record_id=record_id)
        normalized_rows[record_id] = _validate_review_content(
            row,
            label=label,
            record_id=record_id,
            record_type=record_type,
            registered_control_ids=registered_control_ids,
            media_duration=media_duration,
        )
    return normalized_rows, expected_reviewer_id


def _adjudication_map(
    rows: Sequence[dict[str, str]],
    *,
    reviewer_ids: set[str],
    expected_adjudicator_id: str | None,
) -> dict[str, dict[str, str]]:
    normalized_reviewers = {normalized_identity(value) for value in reviewer_ids}
    normalized_adjudicator = normalized_identity(expected_adjudicator_id or "")
    if rows and not normalized_adjudicator:
        raise PendingReviews("an explicit adjudicator roster ID is required")
    if normalized_adjudicator and normalized_adjudicator in normalized_reviewers:
        raise ValueError("adjudicator must be distinct from both reviewers")
    result: dict[str, dict[str, str]] = {}
    for row in rows:
        record_id = str(row.get("Record_ID", ""))
        if not record_id or record_id in result:
            raise ValueError("adjudication contains an empty or duplicate record ID")
        adjudicator = str(row.get("Adjudicator_ID", "")).strip()
        if normalized_identity(adjudicator) != normalized_adjudicator:
            raise ValueError("adjudication is not bound to the explicit adjudicator roster ID")
        if not _valid_date(str(row.get("Adjudication_Date", ""))):
            raise ValueError(f"invalid adjudication date for {record_id}")
        if row.get("Decision_Status") != "Resolved":
            raise PendingReviews(f"adjudication for {record_id} is not resolved")
        if not str(row.get("Adjudication_Rationale", "")).strip():
            raise ValueError(f"adjudication rationale is empty for {record_id}")
        result[record_id] = dict(row)
    return result


def merge_human_reviews(
    machine_rows: Sequence[dict[str, str]],
    reviewer_a_rows: Sequence[dict[str, str]],
    reviewer_b_rows: Sequence[dict[str, str]],
    adjudication_rows: Sequence[dict[str, str]],
    *,
    gap_rows: Sequence[dict[str, str]] = (),
    media_duration: Decimal,
    reviewer_a_id: str,
    reviewer_b_id: str,
    adjudicator_id: str | None,
    registered_control_ids: set[str] | frozenset[str],
) -> list[dict[str, str]]:
    registered = frozenset(registered_control_ids)
    if not registered:
        raise ValueError("a non-empty canonical control registry is required")
    if normalized_identity(reviewer_a_id) == normalized_identity(reviewer_b_id):
        raise ValueError("Reviewer A and Reviewer B must have distinct identities")
    review_a, reviewer_a = _validate_review(
        machine_rows,
        gap_rows,
        reviewer_a_rows,
        "Reviewer A",
        expected_reviewer_id=reviewer_a_id,
        registered_control_ids=registered,
        media_duration=media_duration,
    )
    review_b, reviewer_b = _validate_review(
        machine_rows,
        gap_rows,
        reviewer_b_rows,
        "Reviewer B",
        expected_reviewer_id=reviewer_b_id,
        registered_control_ids=registered,
        media_duration=media_duration,
    )
    adjudications = _adjudication_map(
        adjudication_rows,
        reviewer_ids={reviewer_a, reviewer_b},
        expected_adjudicator_id=adjudicator_id,
    )

    disagreements: set[str] = set()
    record_ids = (
        [row["Segment_ID"] for row in machine_rows]
        + [row["Gap_ID"] for row in gap_rows]
        + [MEDIA_TIMELINE_ID]
    )
    for record_id in record_ids:
        if any(
            review_a[record_id][field] != review_b[record_id][field] for field in CONSENSUS_FIELDS
        ):
            disagreements.add(record_id)
    missing = sorted(disagreements - set(adjudications))
    if missing:
        raise PendingReviews("missing completed adjudication for " + ", ".join(missing))
    extras = sorted(set(adjudications) - disagreements)
    if extras:
        raise ValueError("adjudication supplied without disagreement: " + ", ".join(extras))

    bases: list[dict[str, str]] = []
    for machine in machine_rows:
        bases.append({"Record_ID": machine["Segment_ID"], "Record_Type": "Segment", **machine})
    for gap in gap_rows:
        bases.append(
            {
                "Record_ID": gap["Gap_ID"],
                "Record_Type": "ASR gap",
                "Start": gap["Start"],
                "End": gap["End"],
                "Machine_HE": "",
                "Machine_EN": "",
                **gap,
            }
        )
    bases.append(
        {
            "Record_ID": MEDIA_TIMELINE_ID,
            "Record_Type": "Full media timeline",
            "Start": format_hms(Decimal("0")),
            "End": format_hms(media_duration),
            "Machine_HE": "",
            "Machine_EN": "",
        }
    )

    merged: list[dict[str, str]] = []
    for base in bases:
        record_id = base["Record_ID"]
        left = review_a[record_id]
        final = dict(base)
        final["Reviewer_A"] = reviewer_a
        final["Reviewer_B"] = reviewer_b
        if record_id in disagreements:
            decision = adjudications[record_id]
            required = ("Final_Speaker", "Final_Speaker_Confidence", "Final_Speaker_Basis", "Final_Content_Class")
            if any(not str(decision.get(field, "")).strip() for field in required):
                raise PendingReviews(f"adjudication for {record_id} is incomplete")
            decision_as_review = {
                "Reviewed_HE": str(decision.get("Final_HE", "")),
                "Reviewed_EN": str(decision.get("Final_EN", "")),
                "Speaker": str(decision.get("Final_Speaker", "")),
                "Speaker_Confidence": str(decision.get("Final_Speaker_Confidence", "")),
                "Speaker_Basis": str(decision.get("Final_Speaker_Basis", "")),
                "Content_Class": str(decision.get("Final_Content_Class", "")),
                "Control_IDs": str(decision.get("Final_Control_IDs", "")),
                "Review_Notes": (
                    timeline_attestation(media_duration)
                    if record_id == MEDIA_TIMELINE_ID
                    else str(decision.get("Adjudication_Rationale", ""))
                ),
            }
            _validate_attribution(
                decision_as_review, label="Adjudication", record_id=record_id
            )
            normalized_decision = _validate_review_content(
                decision_as_review,
                label="Adjudication",
                record_id=record_id,
                record_type=str(base["Record_Type"]),
                registered_control_ids=registered,
                media_duration=media_duration,
            )
            final.update(
                {
                    "Reviewed_HE": normalized_decision["Reviewed_HE"],
                    "Reviewed_EN": normalized_decision["Reviewed_EN"],
                    "Speaker": normalized_decision["Speaker"],
                    "Speaker_Confidence": normalized_decision["Speaker_Confidence"],
                    "Speaker_Basis": normalized_decision["Speaker_Basis"],
                    "Content_Class": normalized_decision["Content_Class"],
                    "Control_IDs": normalized_decision["Control_IDs"],
                    "Review_Notes": normalized_decision["Review_Notes"],
                    "Disagreement": "Yes",
                    "Adjudication": adjudicator_id or "",
                    "Adjudication_Rationale": decision["Adjudication_Rationale"],
                }
            )
            final["Status"] = "Human-reviewed adjudicated"
        else:
            final.update(
                {
                    "Reviewed_HE": left["Reviewed_HE"],
                    "Reviewed_EN": left["Reviewed_EN"],
                    "Speaker": left["Speaker"],
                    "Speaker_Confidence": left["Speaker_Confidence"],
                    "Speaker_Basis": left["Speaker_Basis"],
                    "Content_Class": left["Content_Class"],
                    "Control_IDs": left["Control_IDs"],
                    "Review_Notes": left["Review_Notes"],
                    "Disagreement": "No",
                    "Adjudication": "",
                    "Adjudication_Rationale": "",
                }
            )
            final["Status"] = "Human-reviewed consensus"
        merged.append(final)
    return merged


def _package_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--source", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--expected-segments", required=True, type=int)
    parser.add_argument("--media-duration", required=True, type=Decimal)
    parser.add_argument("--translation", type=Path)
    parser.add_argument("--provenance", required=True, type=Path)
    parser.add_argument("--allowed-root", required=True, type=Path)
    parser.add_argument("--repo-root", required=True, type=Path)
    parser.add_argument("--hf-cache-root", required=True, type=Path)
    parser.add_argument("--ollama-cache-root", type=Path)


def build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Build and validate private August 12 meeting evidence"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    _package_args(subparsers.add_parser("build", help="build private ledgers"))
    _package_args(subparsers.add_parser("check", help="check private ledgers"))
    fingerprint = subparsers.add_parser("fingerprint", help="compare M4A and MP4 audio evidence")
    fingerprint.add_argument("--primary", required=True, type=Path)
    fingerprint.add_argument("--secondary", required=True, type=Path)
    fingerprint.add_argument("--output", required=True, type=Path)
    translate = subparsers.add_parser(
        "translate", help="run or resume frozen local Hebrew-to-English translation"
    )
    translate.add_argument("--source", required=True, type=Path)
    translate.add_argument("--output", required=True, type=Path)
    translate.add_argument("--event-log", required=True, type=Path)
    translate.add_argument("--expected-segments", required=True, type=int)
    translate.add_argument("--media-duration", required=True, type=Decimal)
    translate.add_argument("--ollama-url", default="http://127.0.0.1:11434")
    translate.add_argument("--model", required=True)
    translate.add_argument("--model-digest", required=True)
    translate.add_argument("--batch-size", type=int, default=18)
    translate.add_argument("--timeout-seconds", type=int, default=600)
    translate.add_argument("--allowed-root", required=True, type=Path)
    translate.add_argument("--repo-root", required=True, type=Path)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_argument_parser().parse_args(argv)
    if args.command in {"build", "check"}:
        expected = build_package_contents(
            args.source,
            expected_segments=args.expected_segments,
            media_duration=args.media_duration,
            provenance_path=args.provenance,
            translation_path=args.translation,
            allowed_root=args.allowed_root,
            repo_root=args.repo_root,
            hf_cache_root=args.hf_cache_root,
            ollama_cache_root=args.ollama_cache_root,
        )
        if args.command == "build":
            write_package(
                args.output_dir,
                expected,
                allowed_root=args.allowed_root,
                repo_root=args.repo_root,
            )
            return 0
        errors = check_package(
            args.output_dir,
            expected,
            allowed_root=args.allowed_root,
            repo_root=args.repo_root,
        )
        for error in errors:
            print(error, file=sys.stderr)
        return 1 if errors else 0
    if args.command == "fingerprint":
        primary = fingerprint_audio(args.primary)
        secondary = fingerprint_audio(args.secondary)
        differences = compare_media_fingerprints(primary, secondary)
        payload = {
            "schema_version": "Aug12MeetingAudioComparison-v1",
            "primary": primary,
            "secondary": secondary,
            "audio_evidence_equivalent": not differences,
            "differences": differences,
        }
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
            newline="\n",
        )
        return 1 if differences else 0
    if args.command == "translate":
        validate_translation_paths(
            source_path=args.source,
            output_path=args.output,
            event_log_path=args.event_log,
            allowed_root=args.allowed_root,
            repo_root=args.repo_root,
        )
        base_url = validate_ollama_base_url(args.ollama_url)
        source_rows = normalize_asr_lines(
            args.source.read_text(encoding="utf-8").splitlines(),
            expected_segments=args.expected_segments,
            media_duration=args.media_duration,
        )
        tags = _http_json(base_url + "/api/tags", timeout_seconds=30)
        model_record = require_ollama_model(tags, args.model, args.model_digest)
        version = _http_json(base_url + "/api/version", timeout_seconds=30)
        context = translation_run_context(
            source_path=args.source,
            source_rows=source_rows,
            generator_script_sha256=sha256_file(Path(__file__)),
            model=args.model,
            model_digest=args.model_digest,
            options=DEFAULT_OLLAMA_OPTIONS,
            batch_size=args.batch_size,
            timeout_seconds=args.timeout_seconds,
        )
        run_metadata = {
            "python_version": platform.python_version(),
            "platform": platform.platform(),
            "process_id": os.getpid(),
            "ollama_version": version.get("version"),
            "model_size": model_record.get("size"),
        }
        requester = OllamaRequester(
            base_url=base_url,
            model=args.model,
            options=DEFAULT_OLLAMA_OPTIONS,
            timeout_seconds=args.timeout_seconds,
        )
        translate_with_checkpoints(
            source_rows,
            requester,
            args.output,
            batch_size=args.batch_size,
            event_log_path=args.event_log,
            run_context=context,
            run_metadata=run_metadata,
        )
        return 0
    raise AssertionError(f"unhandled command {args.command}")


if __name__ == "__main__":
    raise SystemExit(main())
