#!/usr/bin/env python3
"""Validate the July 29 Iris requirements-closure control package.

The checks in this module are documentation and governance conformance checks.
They do not turn a pending supervisor decision, human transcript review, live
presentation rehearsal, medical gate, or empirical evaluation into completed
evidence.

Examples:
    python scripts/validate_iris_requirements_closure.py --all --mode structure
    python scripts/validate_iris_requirements_closure.py --all --mode readiness
    python scripts/validate_iris_requirements_closure.py --experiment IRIS-EXP-05
    python scripts/validate_iris_requirements_closure.py --all --mode closure --refresh
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import subprocess
import sys
import zipfile
from collections import Counter
from dataclasses import asdict, dataclass
from datetime import datetime
from decimal import ROUND_HALF_UP, Decimal
from pathlib import Path
from urllib.parse import unquote
from xml.etree import ElementTree

ROOT = Path(__file__).resolve().parents[1]

MASTER = ROOT / "docs/research/phd-proposal/master-traceability-register.md"
CLOSURE = ROOT / "docs/research/phd-proposal/iris-requirements-closure-audit.md"
REQUIREMENT_REGISTER = (
    ROOT / "docs/research/meetings/2026-07-29-iris-requirements-register.md"
)
ACTION_REGISTER = (
    ROOT / "docs/research/meetings/2026-07-29-iris-supervisor-action-register.md"
)
EXPERIMENT_REGISTER = (
    ROOT / "docs/research/phd-proposal/iris-alignment-experiment-register.md"
)
PRESENTATION = (
    ROOT
    / "docs/research/meetings/2026-08-05-supervisor-presentation-checklist.md"
)
WEEKLY_TEMPLATE = (
    ROOT / "docs/templates/weekly-supervisor-pre-read.md"
)
DECISION_LOG = ROOT / "docs/research/phd-proposal/decision-change-log.md"
CLAIM_REGISTER = ROOT / "docs/research/phd-proposal/claim-register.md"
MACHINE_JSONL = (
    ROOT
    / "docs/research/meetings/2026-07-29-iris-supervisor-asr.he-en.machine.jsonl"
)
LEDGER_CSV = (
    ROOT
    / "docs/research/meetings/2026-07-29-iris-zoom-preliminary-disposition.csv"
)
LEDGER_JSON = (
    ROOT
    / "docs/research/meetings/2026-07-29-iris-zoom-preliminary-disposition.json"
)
LEDGER_BUILDER = ROOT / "scripts/build_iris_zoom_disposition_ledger.py"
GAP_LEDGER_CSV = (
    ROOT / "docs/research/meetings/2026-07-29-iris-zoom-machine-gap-ledger.csv"
)
REVIEWER_A_TEMPLATE = (
    ROOT / "docs/research/meetings/2026-07-29-iris-zoom-reviewer-a.csv"
)
REVIEWER_B_TEMPLATE = (
    ROOT / "docs/research/meetings/2026-07-29-iris-zoom-reviewer-b.csv"
)
ADJUDICATION_TEMPLATE = (
    ROOT / "docs/research/meetings/2026-07-29-iris-zoom-adjudication.csv"
)
HUMAN_REVIEW_WORKFLOW = (
    ROOT / "docs/research/meetings/2026-07-29-iris-zoom-human-review-workflow.md"
)
ADJUDICATED_CSV = (
    ROOT / "docs/research/meetings/2026-07-29-iris-zoom-adjudicated-ledger.csv"
)
ADJUDICATED_JSON = (
    ROOT / "docs/research/meetings/2026-07-29-iris-zoom-adjudicated-ledger.json"
)
ADJUDICATED_BUILDER = ROOT / "scripts/build_iris_zoom_adjudicated_ledger.py"
PROVENANCE_MANIFEST = (
    ROOT / "docs/research/meetings/2026-07-29-iris-supervisor-provenance-manifest.md"
)
PRESENTATION_DECK = (
    ROOT / "presentations/VEGO-AI-Iris-Supervisor-Decisions-2026-08-05.pptx"
)
PRESENTATION_PDF = (
    ROOT / "presentations/VEGO-AI-Iris-Supervisor-Decisions-2026-08-05.pdf"
)
REVIEW_WORKBOOK = (
    ROOT
    / "outputs/iris-closure-2026-08-01/Iris_Zoom_Review_Ledger_2026-07-29.xlsx"
)
LOCAL_PACKAGE_BACKUP = (
    ROOT
    / "outputs/iris-closure-2026-08-01/VEGO-AI-August5-Supervisor-Package-local-backup.zip"
)
PRESENTATION_MANIFEST = (
    ROOT / "docs/research/meetings/2026-08-05-supervisor-presentation-manifest.md"
)
PRESENTATION_SOURCE_MANIFEST = (
    ROOT
    / "docs/research/meetings/2026-08-05-supervisor-source-manifest.json"
)
PRESENTATION_SOURCE_MANIFEST_BUILDER = (
    ROOT / "scripts/build_supervisor_source_manifest.py"
)
PRESENTATION_RENDER_SCHEMA = (
    ROOT / "schemas/iris-presentation-render-manifest-v1.schema.json"
)
PRESENTATION_RENDER_TEMPLATE = (
    ROOT
    / "docs/research/meetings/2026-08-05-supervisor-render-manifest.template.json"
)
PRESENTATION_RENDER_RECORD = (
    ROOT / "docs/research/meetings/2026-08-05-supervisor-render-manifest.json"
)
REHEARSAL_RECORD = (
    ROOT / "docs/research/meetings/2026-08-05-supervisor-rehearsal-record.md"
)
DELIVERY_RECORD = (
    ROOT / "docs/research/meetings/2026-08-05-supervisor-delivery-access-record.md"
)
SUPERVISOR_MINUTES = (
    ROOT / "docs/research/meetings/2026-08-05-supervisor-minutes.md"
)
CLOSURE_CERTIFICATE = (
    ROOT / "docs/research/phd-proposal/iris-closure-certificate-template.md"
)
GOVERNANCE_CONTROL = (
    ROOT / "docs/research/phd-proposal/iris-closure-governance-control.md"
)
SUBMISSION_RECEIPT_SCHEMA = (
    ROOT / "schemas/iris-authorized-submission-receipt-v1.schema.json"
)
SUBMISSION_RECEIPT_TEMPLATE = (
    ROOT
    / "docs/research/phd-proposal/authorized-submission-receipt.template.json"
)
SUBMISSION_RECEIPT_RECORD = (
    ROOT / "docs/research/phd-proposal/authorized-submission-receipt.json"
)

EXPERIMENTS = (
    "IRIS-EXP-01",
    "IRIS-EXP-02",
    "IRIS-EXP-03",
    "IRIS-EXP-04",
    "IRIS-EXP-05",
    "IRIS-EXP-06",
    "IRIS-EXP-07",
    "IRIS-EXP-08",
    "IRIS-EXP-09",
    "IRIS-EXP-10",
)
MODES = ("structure", "readiness", "closure")
EXPECTED_IDS = (
    tuple(f"R-{index:02d}" for index in range(1, 20))
    + tuple(f"A-{index:02d}" for index in range(1, 16))
    + tuple(f"Q-{index:02d}" for index in range(1, 11))
)
EXPECTED_STATUS_COUNTS = {
    "Verified complete": 2,
    "Implemented awaiting human acceptance": 6,
    "Partial": 22,
    "Open": 5,
    "Blocked": 9,
}
# 2026-08-10: split into LIVE (current working draft, refined during the 2026-08-05
# supervisor call) and HISTORICAL (intentional frozen snapshots that must keep the
# pre-call wording verbatim: the 2026-07-29 execution-plan record and the
# 2026-08-05 decision pack's "before" baseline). This tracks INTERNAL CONSISTENCY
# of whichever wording each file is supposed to carry - it does NOT assert
# supervisor approval. D-RQ-01/D-RQ-02 remain Pending in the decision pack
# regardless of what this check reports; approval status is tracked there, not here.
CANONICAL_QUESTIONS_LIVE = (
    "How can human judgment be captured, governed, and used to support "
    "agentic-AI-driven variability exploration in guideline operationalization "
    "scenarios, enabling reliable human–AI co-reasoning?",
    "When and how, in variability exploration scenarios, should an agentic "
    "assessment system request human judgment so that important uncertainties "
    "are addressed without unnecessary expert burden?",
    "How should expert judgment — including the system's core reasoning — be "
    "represented, validated, reconciled, and stored so it can be reused "
    "transparently without unsafe generalization or loss of human authority?",
    "How can expert judgment be reused and transferred across different "
    "guideline-operationalization contexts without unsafe generalization or "
    "loss of human authority, first in software/modeling and, when governance "
    "and access permit, in healthcare?",
)
CANONICAL_QUESTIONS_HISTORICAL = (
    "How can reusable human judgment be captured, governed, and reused in "
    "agentic AI assessment of domain-specific artifacts and processes to "
    "support auditable, reliable, and transferable human–AI co-reasoning?",
    "When and how should an agentic assessment system request human judgment "
    "so that important uncertainties are addressed without unnecessary expert "
    "burden?",
    "How should expert judgments be represented, validated, reconciled, and "
    "stored so they can be reused transparently without unsafe generalization "
    "or loss of human authority?",
    "To what extent does the resulting framework improve assessment quality, "
    "consistency, traceability, and expert effort across domains, first in "
    "software/modeling and, when governance and access permit, in healthcare?",
)
LIVE_RQ_FILES = (
    MASTER,
    ROOT / "docs/research/phd-proposal/README.md",
    ROOT / "docs/research/phd-proposal/three-study-contract.md",
    ROOT / "docs/research/phd-proposal/proposal-v0.1.md",
)
# Frozen snapshots: must keep pre-2026-08-05-call wording verbatim by design.
HISTORICAL_RQ_FILES = (
    ROOT / "docs/research/phd-proposal/2026-07-29-doctoral-execution-plan.md",
    ROOT / "docs/research/phd-proposal/2026-08-05-rq-decision-pack.md",
)
MEDIA_DURATION_SECONDS = Decimal("2786.283")


@dataclass(frozen=True)
class Check:
    name: str
    passed: bool
    detail: str


@dataclass(frozen=True)
class Result:
    experiment: str
    state: str
    checks: tuple[Check, ...]
    evidence_boundary: str
    readiness_checks: tuple[Check, ...] = ()
    closure_checks: tuple[Check, ...] = ()

    @property
    def passed(self) -> bool:
        return all(check.passed for check in self.checks)

    def checks_for_mode(self, mode: str) -> tuple[Check, ...]:
        if mode == "structure":
            return self.checks
        if mode == "readiness":
            return self.checks + self.readiness_checks
        if mode == "closure":
            return self.checks + self.readiness_checks + self.closure_checks
        raise ValueError(f"unknown mode: {mode}")

    def passed_for_mode(self, mode: str) -> bool:
        return all(check.passed for check in self.checks_for_mode(mode))


def read(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")


def read_json(path: Path) -> dict[str, object]:
    if not path.exists():
        return {}
    try:
        payload = json.loads(read(path))
    except json.JSONDecodeError:
        return {}
    return payload if isinstance(payload, dict) else {}


def read_jsonl(path: Path) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    if not path.exists():
        return rows
    for line in read(path).splitlines():
        if not line.strip():
            continue
        try:
            payload = json.loads(line)
        except json.JSONDecodeError:
            return []
        if not isinstance(payload, dict):
            return []
        rows.append(payload)
    return rows


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    try:
        with path.open(encoding="utf-8", newline="") as handle:
            return list(csv.DictReader(handle))
    except (csv.Error, UnicodeError):
        return []


def sha256(path: Path) -> str:
    if not path.exists():
        return ""
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest().upper()


def decimal_value(value: object) -> Decimal:
    try:
        return Decimal(str(value))
    except Exception as error:  # noqa: BLE001 - malformed evidence must fail closed
        raise ValueError(f"not a decimal value: {value!r}") from error


def format_hms(seconds: Decimal) -> str:
    milliseconds = int(
        (seconds * 1000).quantize(Decimal("1"), rounding=ROUND_HALF_UP)
    )
    hours, remainder = divmod(milliseconds, 3_600_000)
    minutes, remainder = divmod(remainder, 60_000)
    whole_seconds, millis = divmod(remainder, 1_000)
    return f"{hours:02d}:{minutes:02d}:{whole_seconds:02d}.{millis:03d}"


def machine_timeline_accounting(
    rows: list[dict[str, object]],
) -> tuple[dict[str, Decimal | int], list[dict[str, str]]]:
    """Independently calculate ASR interval union and uncovered intervals."""

    if not rows:
        return {}, []
    cursor = Decimal("0")
    interval_sum = Decimal("0")
    union_seconds = Decimal("0")
    overlap_seconds = Decimal("0")
    overlap_count = 0
    gaps: list[dict[str, str]] = []
    previous_id = ""
    previous_start = Decimal("-1")

    for index, row in enumerate(rows, start=1):
        try:
            start = decimal_value(row.get("start"))
            end = decimal_value(row.get("end"))
        except ValueError:
            return {}, []
        if (
            start < 0
            or end < start
            or end > MEDIA_DURATION_SECONDS
            or start < previous_start
        ):
            return {}, []
        interval_sum += end - start
        if start > cursor:
            gaps.append(
                {
                    "Gap_ID": "",
                    "Gap_Type": "Lead" if not previous_id else "Internal",
                    "Start": format_hms(cursor),
                    "End": format_hms(start),
                    "Duration_Seconds": f"{start - cursor:.3f}",
                    "Previous_Segment_ID": previous_id,
                    "Next_Segment_ID": f"S-{index:04d}",
                }
            )
        if start < cursor:
            overlap_count += 1
            overlap_seconds += min(cursor, end) - start
        if end > cursor:
            union_seconds += end - max(start, cursor)
            cursor = end
        previous_id = f"S-{index:04d}"
        previous_start = start

    if cursor < MEDIA_DURATION_SECONDS:
        gaps.append(
            {
                "Gap_ID": "",
                "Gap_Type": "Tail",
                "Start": format_hms(cursor),
                "End": format_hms(MEDIA_DURATION_SECONDS),
                "Duration_Seconds": f"{MEDIA_DURATION_SECONDS - cursor:.3f}",
                "Previous_Segment_ID": previous_id,
                "Next_Segment_ID": "",
            }
        )
    elif cursor > MEDIA_DURATION_SECONDS:
        return {}, []

    for index, gap in enumerate(gaps, start=1):
        gap["Gap_ID"] = f"G-{index:04d}"
    gap_seconds = sum(
        (decimal_value(gap["Duration_Seconds"]) for gap in gaps), Decimal("0")
    )
    metrics: dict[str, Decimal | int] = {
        "asr_interval_duration_sum_seconds": interval_sum,
        "asr_interval_union_seconds": union_seconds,
        "overlap_count": overlap_count,
        "overlap_seconds": overlap_seconds,
        "uncovered_interval_count": len(gaps),
        "uncovered_seconds": gap_seconds,
        "lead_gap_count": sum(gap["Gap_Type"] == "Lead" for gap in gaps),
        "untranscribed_lead_seconds": sum(
            (
                decimal_value(gap["Duration_Seconds"])
                for gap in gaps
                if gap["Gap_Type"] == "Lead"
            ),
            Decimal("0"),
        ),
        "internal_gap_count": sum(
            gap["Gap_Type"] == "Internal" for gap in gaps
        ),
        "internal_gap_seconds": sum(
            (
                decimal_value(gap["Duration_Seconds"])
                for gap in gaps
                if gap["Gap_Type"] == "Internal"
            ),
            Decimal("0"),
        ),
        "tail_gap_count": sum(gap["Gap_Type"] == "Tail" for gap in gaps),
        "untranscribed_tail_seconds": sum(
            (
                decimal_value(gap["Duration_Seconds"])
                for gap in gaps
                if gap["Gap_Type"] == "Tail"
            ),
            Decimal("0"),
        ),
        "maximum_uncovered_interval_seconds": max(
            decimal_value(gap["Duration_Seconds"]) for gap in gaps
        ),
        "machine_accounted_timeline_seconds": union_seconds + gap_seconds,
    }
    return metrics, gaps


def pptx_slide_texts(path: Path) -> list[str]:
    """Extract normalized visible text per slide without Office automation."""
    if not path.is_file():
        return []
    try:
        with zipfile.ZipFile(path) as archive:
            slide_names = [
                name
                for name in archive.namelist()
                if re.fullmatch(r"ppt/slides/slide\d+\.xml", name)
            ]
            slide_names.sort(key=lambda name: int(re.search(r"\d+", name).group()))
            slides: list[str] = []
            for name in slide_names:
                root = ElementTree.fromstring(archive.read(name))
                parts = [
                    node.text or ""
                    for node in root.iter()
                    if node.tag.endswith("}t")
                ]
                slides.append(re.sub(r"\s+", " ", " ".join(parts)).strip())
    except (OSError, zipfile.BadZipFile, ElementTree.ParseError):
        return []
    return slides


def pptx_visible_text(path: Path) -> str:
    return " ".join(pptx_slide_texts(path))


def backup_members_match(
    backup: Path, artifacts: tuple[Path, ...]
) -> bool:
    """Return whether required backup members match the current artifacts."""
    if not backup.is_file() or any(not artifact.is_file() for artifact in artifacts):
        return False
    try:
        with zipfile.ZipFile(backup) as archive:
            members = [member for member in archive.infolist() if not member.is_dir()]
            by_name = {Path(member.filename).name: member for member in members}
            required_names = {artifact.name for artifact in artifacts}
            if len(by_name) != len(members) or not required_names <= set(by_name):
                return False
            for artifact in artifacts:
                digest = hashlib.sha256()
                with archive.open(by_name[artifact.name]) as stream:
                    for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                        digest.update(chunk)
                if digest.hexdigest().upper() != sha256(artifact):
                    return False
    except (OSError, zipfile.BadZipFile):
        return False
    return True


def valid_sha256(value: object) -> bool:
    return isinstance(value, str) and re.fullmatch(r"[A-Fa-f0-9]{64}", value) is not None


def valid_zoned_timestamp(value: object) -> bool:
    if not isinstance(value, str) or not value.strip():
        return False
    normalized = value.replace("Z", "+00:00")
    # RFC 3339 permits more fractional-second precision than datetime accepts.
    normalized = re.sub(r"(\.\d{6})\d+(?=[+-]\d{2}:\d{2}$)", r"\1", normalized)
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError:
        return False
    return parsed.tzinfo is not None and parsed.utcoffset() is not None


def receipt_structure_errors(payload: dict[str, object]) -> list[str]:
    required = {
        "submission": (
            "route",
            "submitted_at",
            "receipt_id",
            "submitted_by",
            "recipient_authority",
        ),
        "authorization": (
            "authorized",
            "authority",
            "authorized_at",
            "evidence_path",
            "evidence_sha256",
        ),
        "package": ("path", "sha256"),
        "receipt_artifact": ("path", "sha256"),
        "certificate_binding": (
            "certificate_id",
            "certificate_path",
            "certificate_sha256",
        ),
    }
    errors: list[str] = []
    if payload.get("schema_version") != "IrisAuthorizedSubmissionReceipt-v1":
        errors.append("schema_version")
    if payload.get("status") not in {"NOT_SUBMITTED", "VERIFIED"}:
        errors.append("status")
    for section, fields in required.items():
        value = payload.get(section)
        if not isinstance(value, dict):
            errors.append(section)
            continue
        errors.extend(f"{section}.{field}" for field in fields if field not in value)
    return errors


def repo_artifact(value: object) -> Path | None:
    if not isinstance(value, str) or not value.strip():
        return None
    candidate = (ROOT / value).resolve()
    try:
        candidate.relative_to(ROOT.resolve())
    except ValueError:
        return None
    return candidate if candidate.is_file() else None


def receipt_section(payload: dict[str, object], name: str) -> dict[str, object]:
    value = payload.get(name)
    return value if isinstance(value, dict) else {}


def source_manifest_errors(payload: dict[str, object]) -> list[str]:
    errors: list[str] = []
    if payload.get("schema_version") != "IrisSupervisorSourceManifest-v1":
        errors.append("schema_version")
    if payload.get("status") != "HASH_BOUND_LOCAL_CANDIDATE":
        errors.append("status")
    presentation = payload.get("presentation")
    if not isinstance(presentation, dict):
        errors.append("presentation")
    else:
        if presentation.get("path") != PRESENTATION_DECK.relative_to(ROOT).as_posix():
            errors.append("presentation.path")
        if presentation.get("bytes") != PRESENTATION_DECK.stat().st_size:
            errors.append("presentation.bytes")
        if presentation.get("sha256") != sha256(PRESENTATION_DECK):
            errors.append("presentation.sha256")
        if presentation.get("slide_count") != 21:
            errors.append("presentation.slide_count")
        if presentation.get("source_note_sections") != 21:
            errors.append("presentation.source_note_sections")
    sources = payload.get("sources")
    if not isinstance(sources, list) or not sources:
        errors.append("sources")
        return errors
    if payload.get("unique_source_path_count") != len(sources):
        errors.append("unique_source_path_count")
    seen: set[str] = set()
    for index, entry in enumerate(sources):
        prefix = f"sources[{index}]"
        if not isinstance(entry, dict):
            errors.append(prefix)
            continue
        path_text = entry.get("path")
        if not isinstance(path_text, str) or path_text in seen:
            errors.append(f"{prefix}.path")
            continue
        seen.add(path_text)
        path = repo_artifact(path_text)
        if entry.get("kind") == "file":
            if path is None:
                errors.append(f"{prefix}.file")
            elif (
                entry.get("bytes") != path.stat().st_size
                or entry.get("sha256") != sha256(path)
            ):
                errors.append(f"{prefix}.hash")
        elif entry.get("kind") == "directory":
            directory = (ROOT / path_text).resolve()
            try:
                directory.relative_to(ROOT.resolve())
            except ValueError:
                errors.append(f"{prefix}.directory")
                continue
            members = entry.get("members")
            if not directory.is_dir() or not isinstance(members, list) or not members:
                errors.append(f"{prefix}.members")
                continue
            member_errors = []
            for member in members:
                if not isinstance(member, dict):
                    member_errors.append("row")
                    continue
                member_path = repo_artifact(member.get("path"))
                if member_path is None or (
                    member.get("bytes") != member_path.stat().st_size
                    or member.get("sha256") != sha256(member_path)
                ):
                    member_errors.append(str(member.get("path")))
            canonical = json.dumps(
                members, ensure_ascii=False, sort_keys=True, separators=(",", ":")
            )
            if (
                member_errors
                or entry.get("member_count") != len(members)
                or entry.get("aggregate_sha256") != sha256_text(canonical)
            ):
                errors.append(f"{prefix}.members")
        else:
            errors.append(f"{prefix}.kind")
        if not isinstance(entry.get("slides"), list) or not entry.get("slides"):
            errors.append(f"{prefix}.slides")
    return errors


def render_manifest_structure_errors(
    payload: dict[str, object], *, require_verified: bool
) -> list[str]:
    errors: list[str] = []
    if payload.get("schema_version") != "IrisPresentationRenderManifest-v1":
        errors.append("schema_version")
    expected_status = "VERIFIED" if require_verified else "PENDING_FINAL_RENDER"
    if payload.get("status") != expected_status:
        errors.append("status")
    if payload.get("expected_slide_count") != 21:
        errors.append("expected_slide_count")
    for section in ("package", "renderer", "montage", "visual_review"):
        if not isinstance(payload.get(section), dict):
            errors.append(section)
    slides = payload.get("slides")
    if not isinstance(slides, list):
        errors.append("slides")
        return errors
    if not require_verified:
        if slides:
            errors.append("slides_pending")
        return errors

    package = payload.get("package", {})
    assert isinstance(package, dict)
    for label, expected in (("pptx", PRESENTATION_DECK), ("pdf", PRESENTATION_PDF)):
        artifact = package.get(label)
        if not isinstance(artifact, dict):
            errors.append(f"package.{label}")
            continue
        if artifact.get("path") != expected.relative_to(ROOT).as_posix():
            errors.append(f"package.{label}.path")
        if not expected.is_file():
            errors.append(f"package.{label}.not_present_in_checkout")
            continue
        if artifact.get("bytes") != expected.stat().st_size:
            errors.append(f"package.{label}.bytes")
        if artifact.get("sha256") != sha256(expected):
            errors.append(f"package.{label}.sha256")
    revision = package.get("repository_revision")
    if not isinstance(revision, str) or not revision or revision == "NOT_FROZEN":
        errors.append("package.repository_revision")

    renderer = payload.get("renderer", {})
    assert isinstance(renderer, dict)
    for field in ("name", "version", "environment"):
        if not isinstance(renderer.get(field), str) or not renderer.get(field):
            errors.append(f"renderer.{field}")
    if not valid_zoned_timestamp(renderer.get("rendered_at")):
        errors.append("renderer.rendered_at")

    if len(slides) != 21:
        errors.append("slides.count")
    numbers = [slide.get("number") for slide in slides if isinstance(slide, dict)]
    if numbers != list(range(1, 22)):
        errors.append("slides.sequence")
    for index, slide in enumerate(slides):
        prefix = f"slides[{index}]"
        if not isinstance(slide, dict):
            errors.append(prefix)
            continue
        artifact = repo_artifact(slide.get("path"))
        if artifact is None:
            errors.append(f"{prefix}.path")
        elif (
            slide.get("bytes") != artifact.stat().st_size
            or slide.get("sha256") != sha256(artifact)
        ):
            errors.append(f"{prefix}.hash")
        if slide.get("visual_result") != "PASS":
            errors.append(f"{prefix}.visual_result")
        if not slide.get("inspector"):
            errors.append(f"{prefix}.inspector")
        if not valid_zoned_timestamp(slide.get("reviewed_at")):
            errors.append(f"{prefix}.reviewed_at")

    montage = payload.get("montage", {})
    assert isinstance(montage, dict)
    montage_artifact = repo_artifact(montage.get("path"))
    if montage_artifact is None:
        errors.append("montage.path")
    elif (
        montage.get("bytes") != montage_artifact.stat().st_size
        or montage.get("sha256") != sha256(montage_artifact)
    ):
        errors.append("montage.hash")

    visual = payload.get("visual_review", {})
    assert isinstance(visual, dict)
    if visual.get("overall_result") != "PASS":
        errors.append("visual_review.overall_result")
    if visual.get("open_defect_count") != 0:
        errors.append("visual_review.open_defect_count")
    if not visual.get("inspector"):
        errors.append("visual_review.inspector")
    if not valid_zoned_timestamp(visual.get("reviewed_at")):
        errors.append("visual_review.reviewed_at")
    return errors


def check(name: str, passed: bool, passed_detail: str, failed_detail: str) -> Check:
    return Check(name, passed, passed_detail if passed else failed_detail)


def contains_pending_marker(text: str, markers: tuple[str, ...]) -> bool:
    normalized = text.upper()
    return any(marker.upper() in normalized for marker in markers)


def decision_outcomes(text: str) -> dict[str, str]:
    outcomes: dict[str, str] = {}
    allowed = (
        "Confirm with correction",
        "Retire or supersede",
        "Confirm",
        "Defer",
        "Reject",
    )
    for line in text.splitlines():
        match = re.match(r"^\|\s*(D-RQ-\d{2})\s*\|", line)
        if not match:
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        for outcome in allowed:
            if outcome in cells:
                outcomes[match.group(1)] = outcome
                break
    return outcomes


def table_rows(path: Path) -> dict[str, list[str]]:
    rows: dict[str, list[str]] = {}
    for line in read(path).splitlines():
        match = re.match(r"^\|\s*((?:R|A|Q)-\d{2})\s*\|", line)
        if not match:
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        # A controlled document may include a later keyed companion view (for
        # example the independent extraction/implementation/acceptance table
        # in the master register).  The first occurrence is the canonical
        # source table; later occurrences must not overwrite its wider schema.
        rows.setdefault(match.group(1), cells)
    return rows


def companion_status_rows(path: Path = MASTER) -> dict[str, list[str]]:
    text = read(path)
    marker = "## Independent status dimensions — canonical companion view"
    if marker not in text:
        return {}
    rows: dict[str, list[str]] = {}
    for line in text.split(marker, 1)[1].splitlines():
        match = re.match(r"^\|\s*((?:R|A|Q)-\d{2})\s*\|", line)
        if not match:
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        rows[match.group(1)] = cells
    return rows


def local_link_errors(path: Path) -> list[str]:
    errors: list[str] = []
    for target in re.findall(r"\[[^\]]+\]\(([^)]+)\)", read(path)):
        clean_target = target.strip()
        if (
            clean_target.startswith(("http://", "https://", "mailto:", "#"))
            or clean_target == ""
        ):
            continue
        target_parts = clean_target.split("#", 1)
        file_part = unquote(target_parts[0]).strip("<>")
        resolved = (path.parent / file_part).resolve()
        if not resolved.exists():
            errors.append(f"{path.relative_to(ROOT)} -> {clean_target}")
            continue
        if (
            len(target_parts) == 2
            and "iris-supervisor-bilingual-transcript" in resolved.name
        ):
            anchor = unquote(target_parts[1]).lower()
            target_text = read(resolved).lower()
            if f'<a id="{anchor}"></a>' not in target_text:
                errors.append(
                    f"{path.relative_to(ROOT)} -> missing anchor {clean_target}"
                )
    return errors


def exp01() -> Result:
    master_rows = table_rows(MASTER)
    closure_rows = table_rows(CLOSURE)
    requirement_rows = table_rows(REQUIREMENT_REGISTER)
    action_rows = table_rows(ACTION_REGISTER)
    master_ids = tuple(master_rows)
    closure_ids = tuple(closure_rows)
    source_ids = tuple(requirement_rows) + tuple(action_rows)
    companion_rows = companion_status_rows()
    companion_ids = tuple(companion_rows)
    incomplete_companion = sorted(
        row_id
        for row_id, row in companion_rows.items()
        if len(row) != 5 or any(not cell for cell in row[1:])
    )
    implementation_counts = Counter(
        row[2] for row in companion_rows.values() if len(row) == 5
    )
    expected_implementation_counts = {
        "Acceptance check passed": 2,
        "Evidence ready": 6,
        "Partial": 22,
        "Not started": 5,
        "Not started — blocked": 9,
    }
    status_counts = Counter(
        row[5] for row in closure_rows.values() if len(row) >= 6
    )
    incomplete_master = sorted(
        row_id
        for row_id, row in master_rows.items()
        if len(row) != 11 or any(not cell for cell in row)
    )
    incomplete_closure = sorted(
        row_id
        for row_id, row in closure_rows.items()
        if len(row) != 7 or any(not cell for cell in row)
    )
    missing_locator = sorted(
        row_id
        for row_id, row in closure_rows.items()
        if len(row) < 2 or "S-" not in row[1] or "00:" not in row[1]
    )
    link_errors: list[str] = []
    for path in (
        REQUIREMENT_REGISTER,
        ACTION_REGISTER,
        MASTER,
        CLOSURE,
        PRESENTATION,
    ):
        link_errors.extend(local_link_errors(path))

    checks = (
        Check(
            "source registers contain the exact 19/15/10 ID set",
            source_ids == EXPECTED_IDS,
            f"found {len(source_ids)} rows",
        ),
        Check(
            "master contains the exact 19/15/10 ID set",
            master_ids == EXPECTED_IDS,
            f"found {len(master_ids)} rows",
        ),
        Check(
            "closure audit contains the exact 19/15/10 ID set",
            closure_ids == EXPECTED_IDS,
            f"found {len(closure_ids)} rows",
        ),
        Check(
            "master owner/gate/evidence/acceptance/status fields are populated",
            not incomplete_master,
            "missing or malformed: " + ", ".join(incomplete_master)
            if incomplete_master
            else "44/44 rows populated",
        ),
        Check(
            "master companion view contains the exact 44-ID control set",
            companion_ids == EXPECTED_IDS,
            f"found {len(companion_ids)} companion rows",
        ),
        Check(
            "companion extraction/implementation/acceptance/ongoing fields are populated",
            not incomplete_companion,
            "missing or malformed: " + ", ".join(incomplete_companion)
            if incomplete_companion
            else "44/44 companion rows populated",
        ),
        Check(
            "companion implementation dimensions preserve the audited distribution",
            dict(implementation_counts) == expected_implementation_counts,
            f"found {dict(implementation_counts)}",
        ),
        Check(
            "closure rows contain all seven control fields",
            not incomplete_closure,
            "missing or malformed: " + ", ".join(incomplete_closure)
            if incomplete_closure
            else "44/44 rows populated",
        ),
        Check(
            "every closure row has a segment and timestamp locator",
            not missing_locator,
            "missing: " + ", ".join(missing_locator)
            if missing_locator
            else "44/44 locators present",
        ),
        Check(
            "closure classifications preserve the audited readiness boundary",
            dict(status_counts) == EXPECTED_STATUS_COUNTS,
            f"found {dict(status_counts)}",
        ),
        Check(
            "closure and presentation local links resolve",
            not link_errors,
            "; ".join(link_errors) if link_errors else "all local links resolve",
        ),
    )
    return Result(
        experiment="IRIS-EXP-01",
        state="PASS" if all(check.passed for check in checks) else "FAIL",
        checks=checks,
        evidence_boundary=(
            "A PASS proves control completeness and link integrity, not that all "
            "requirements have been accepted or completed."
        ),
    )


def exp02() -> Result:
    text = read(PRESENTATION)
    rehearsal = read(REHEARSAL_RECORD)
    required_sections = (
        "## Presentation sequence",
        "## Requirement coverage matrix",
        "## Before the meeting",
        "## During the meeting",
        "## After the meeting",
        "## Forbidden claims",
    )
    missing_sections = [section for section in required_sections if section not in text]
    missing_requirements = [
        row_id for row_id in EXPECTED_IDS[:19] if row_id not in text
    ]
    required_decisions = [f"D-RQ-{index:02d}" for index in range(1, 11)]
    missing_decisions = [decision for decision in required_decisions if decision not in text]
    checks = (
        Check(
            "presentation checklist contains the full preflight/live/closeout flow",
            not missing_sections,
            "missing: " + ", ".join(missing_sections)
            if missing_sections
            else "all required sections present",
        ),
        Check(
            "presentation maps R-01 through R-19",
            not missing_requirements,
            "missing: " + ", ".join(missing_requirements)
            if missing_requirements
            else "19/19 requirements mapped",
        ),
        Check(
            "presentation exposes all ten supervisor decisions",
            not missing_decisions,
            "missing: " + ", ".join(missing_decisions)
            if missing_decisions
            else "10/10 decision IDs present",
        ),
        Check(
            "presentation explicitly records the human rehearsal boundary",
            "Live rehearsal status:" in text,
            "live rehearsal status is explicit; readiness is checked separately",
        ),
    )
    return Result(
        experiment="IRIS-EXP-02",
        state=(
            "READY_PENDING_HUMAN_RUN"
            if all(check.passed for check in checks)
            else "FAIL"
        ),
        checks=checks,
        evidence_boundary=(
            "Document preflight may pass automatically. Timing, comprehensibility, "
            "speaker handoffs, and decision capture require a dated human rehearsal."
        ),
        readiness_checks=(
            check(
                "dated live rehearsal is complete",
                bool(rehearsal)
                and "STATUS: **COMPLETE**" in rehearsal.upper()
                and "NOT RUN" not in rehearsal.upper(),
                "rehearsal record says COMPLETE",
                "rehearsal record is missing or remains NOT RUN",
            ),
        ),
    )


def exp03() -> Result:
    rq_missing: list[str] = []
    for path in LIVE_RQ_FILES:
        text = read(path)
        for index, question in enumerate(CANONICAL_QUESTIONS_LIVE):
            if question not in text:
                rq_missing.append(f"{path.relative_to(ROOT)}: RQ{index}")
    for path in HISTORICAL_RQ_FILES:
        text = read(path)
        for index, question in enumerate(CANONICAL_QUESTIONS_HISTORICAL):
            if question not in text:
                rq_missing.append(f"{path.relative_to(ROOT)}: RQ{index} (historical snapshot)")
    # PRESENTATION_DECK was built 2026-08-03, before the 2026-08-05 call refined the
    # wording, and has not been rebuilt since (still checked against HISTORICAL
    # per its own "STALE" / not-yet-rehearsed status). Rebuild and switch this to
    # CANONICAL_QUESTIONS_LIVE once the deck is regenerated from the live wording.
    deck_text = re.sub(r"\s+", "", pptx_visible_text(PRESENTATION_DECK))
    for index, question in enumerate(CANONICAL_QUESTIONS_HISTORICAL):
        if re.sub(r"\s+", "", question) not in deck_text:
            rq_missing.append(f"{PRESENTATION_DECK.relative_to(ROOT)}: RQ{index} (historical, as-built 2026-08-03)")

    claim_text = read(CLAIM_REGISTER)
    required_claim_states = (
        "Established",
        "Preliminary",
        "Planned",
        "Blocked",
        "Partner-dependent",
    )
    closure_text = read(CLOSURE)
    presentation_assertions = read(PRESENTATION).split(
        "\n## Forbidden claims", 1
    )[0]
    package_text = "\n".join(
        (
            read(CLOSURE),
            presentation_assertions,
            read(ROOT / "docs/research/meetings/2026-08-05-supervisor-pre-read.md"),
            read(ROOT / "docs/research/phd-proposal/proposal-v0.1.md"),
        )
    )
    unsafe_patterns = (
        r"\ball (?:Iris )?requirements (?:are|have been) "
        r"(?:done|complete|completed|satisfied)\b",
        r"\bmedical readiness (?:is|has been) (?:complete|completed|approved)\b",
        r"\bEXP-005 (?:is|has) (?:complete|completed|passed)\b",
        r"\bclinical performance (?:is|has been) (?:proven|validated|improved)\b",
    )
    unsafe_matches: list[str] = []
    for line in package_text.splitlines():
        if re.search(
            r"\b(?:not|never|cannot|can't|do not|does not|no longer)\b",
            line,
            re.IGNORECASE,
        ):
            continue
        for pattern in unsafe_patterns:
            if re.search(pattern, line, re.IGNORECASE):
                unsafe_matches.append(f"{pattern}: {line.strip()}")
    checks = (
        Check(
            "canonical one-plus-three wording is identical in core artifacts",
            not rq_missing,
            "; ".join(rq_missing) if rq_missing else "six documents and the PPTX agree",
        ),
        Check(
            "all five claim states remain explicit",
            all(state in claim_text for state in required_claim_states),
            "required states: " + ", ".join(required_claim_states),
        ),
        Check(
            "closure audit preserves EXP-005 and medical gates",
            "EXP-005 remains `0/24`" in closure_text
            and "Medical readiness remains `0/6`" in closure_text,
            "both current gate values must be explicit",
        ),
        Check(
            "package contains no prohibited completion or performance claim",
            not unsafe_matches,
            "matched patterns: " + ", ".join(unsafe_matches)
            if unsafe_matches
            else "no prohibited pattern found",
        ),
        Check(
            "machine transcript and attribution caveat remains explicit",
            "machine-derived" in closure_text
            and "S-0001–S-0006" in closure_text
            and "direct quotation" in closure_text,
            "named attribution and quotation boundary must be visible",
        ),
    )
    return Result(
        experiment="IRIS-EXP-03",
        state="PASS" if all(check.passed for check in checks) else "FAIL",
        checks=checks,
        evidence_boundary=(
            "A PASS proves wording and claim-boundary consistency. It supplies no "
            "expert labels, medical evidence, or supervisor approval."
        ),
    )


def exp04() -> Result:
    weekly = read(WEEKLY_TEMPLATE)
    decision = read(DECISION_LOG)
    master = read(MASTER)
    required_weekly_fields = (
        "Previous commitment",
        "Completed evidence",
        "Blocker",
        "Decision requested",
        "Proposal delta",
        "One next task",
        "Definition of done",
        "Decision read-back",
    )
    missing_weekly = [field for field in required_weekly_fields if field not in weekly]
    required_decision_fields = (
        "Decision",
        "Date",
        "Rationale",
        "Affected artifacts",
        "Supersedes",
    )
    missing_decision = [
        field for field in required_decision_fields if field not in decision
    ]
    checks = (
        Check(
            "weekly pre-read template contains the commitment-to-closeout chain",
            not missing_weekly,
            "missing: " + ", ".join(missing_weekly)
            if missing_weekly
            else "all required fields present",
        ),
        Check(
            "decision log preserves change-propagation fields",
            not missing_decision,
            "missing: " + ", ".join(missing_decision)
            if missing_decision
            else "all required fields present",
        ),
        Check(
            "master register binds weekly evidence and decision read-back",
            "Dated weekly pre-reads, proposal deltas, and completed artifacts" in master
            and "decision read-back" in master,
            "R-06/R-13 controls must stay explicit",
        ),
        Check(
            "next-cycle execution remains evidence-honest",
            "First live-cycle status: **NOT RUN**" in weekly,
            "status must remain NOT RUN until the next meeting cycle is closed",
        ),
    )
    return Result(
        experiment="IRIS-EXP-04",
        state=(
            "READY_PENDING_NEXT_MEETING"
            if all(check.passed for check in checks)
            else "FAIL"
        ),
        checks=checks,
        evidence_boundary=(
            "The protocol is testable now; propagation effectiveness is not observed "
            "until a real weekly meeting produces a pre-read, decision, and proposal delta."
        ),
        readiness_checks=(
            check(
                "first real weekly cycle has evidence-linked minutes",
                SUPERVISOR_MINUTES.exists()
                and bool(re.findall(r"D-RQ-\d{2}", read(SUPERVISOR_MINUTES))),
                "meeting minutes and decision references exist",
                "first real weekly-cycle minutes are not recorded",
            ),
        ),
    )


def exp05() -> Result:
    source_rows = read_jsonl(MACHINE_JSONL)
    payload = read_json(LEDGER_JSON)
    adjudicated_payload = read_json(ADJUDICATED_JSON)
    json_rows_raw = payload.get("rows", [])
    json_rows = json_rows_raw if isinstance(json_rows_raw, list) else []
    adjudicated_rows_raw = adjudicated_payload.get("rows", [])
    adjudicated_rows = (
        adjudicated_rows_raw if isinstance(adjudicated_rows_raw, list) else []
    )
    csv_rows = read_csv_rows(LEDGER_CSV)
    gap_rows = read_csv_rows(GAP_LEDGER_CSV)
    timeline_metrics, expected_gaps = machine_timeline_accounting(source_rows)
    expected_ids = [f"S-{index:04d}" for index in range(1, 1196)]
    source_ids = [row.get("id") for row in source_rows]
    json_ids = [row.get("Segment_ID") for row in json_rows if isinstance(row, dict)]
    csv_ids = [row.get("Segment_ID") for row in csv_rows]
    required_fields = {
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
        "Preliminary_Disposition",
        "Control_IDs",
        "External_Claim_IDs",
        "Reviewer_A",
        "Reviewer_B",
        "Disagreement",
        "Adjudication",
        "Review_Status",
        "Evidence_Link",
    }
    schema_ok = bool(json_rows) and all(
        isinstance(row, dict) and required_fields <= set(row) for row in json_rows
    )
    copied_exactly = len(source_rows) == len(json_rows) == 1195 and all(
        json_row.get("Start") == source_row.get("start_hms")
        and json_row.get("End") == source_row.get("end_hms")
        and json_row.get("Machine_HE") == source_row.get("text_he_asr")
        and json_row.get("Machine_EN")
        == source_row.get("text_en_machine_translation")
        for source_row, json_row in zip(source_rows, json_rows, strict=True)
        if isinstance(json_row, dict)
    )
    coverage = payload.get("coverage", {})
    coverage = coverage if isinstance(coverage, dict) else {}
    preliminary_timeline_status = coverage.get("timeline_review_status")
    expected_gap_fields = {
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
        "Review_Status",
    }
    gap_schema_ok = bool(gap_rows) and all(
        expected_gap_fields <= set(row) for row in gap_rows
    )
    gap_rows_match = (
        len(gap_rows) == len(expected_gaps)
        and all(
            all(observed.get(field) == expected.get(field) for field in expected)
            and observed.get("Machine_Disposition")
            == "Uncovered by ASR/VAD interval union"
            and observed.get("Review_Status")
            == "Machine-only; human full-media classification needed"
            and not observed.get("Human_Classification")
            and not observed.get("Reviewer_A")
            and not observed.get("Reviewer_B")
            and not observed.get("Adjudication")
            for observed, expected in zip(gap_rows, expected_gaps, strict=True)
        )
    )

    def coverage_decimal(name: str) -> Decimal | None:
        try:
            return decimal_value(coverage.get(name))
        except ValueError:
            return None

    coverage_metrics_match = bool(timeline_metrics) and all(
        coverage_decimal(name) == value
        for name, value in timeline_metrics.items()
        if isinstance(value, Decimal)
    )
    coverage_metrics_match = coverage_metrics_match and all(
        coverage.get(name) == value
        for name, value in timeline_metrics.items()
        if isinstance(value, int)
    )
    coverage_metrics_match = coverage_metrics_match and (
        coverage_decimal("asr_interval_coverage_percent") == Decimal("83.750")
        and coverage.get("gap_register_path")
        == GAP_LEDGER_CSV.relative_to(ROOT).as_posix()
        and coverage.get("gap_register_sha256") == sha256(GAP_LEDGER_CSV)
        and coverage.get("human_classified_uncovered_intervals") == 0
        and coverage.get("unclassified_uncovered_intervals") == len(expected_gaps)
        and coverage_decimal("human_reviewed_media_seconds") == 0
        and coverage_decimal("unreviewed_media_seconds") == MEDIA_DURATION_SECONDS
    )
    interval_union_complete = bool(timeline_metrics) and (
        timeline_metrics.get("asr_interval_union_seconds") == Decimal("2333.500")
        and timeline_metrics.get("uncovered_seconds") == Decimal("452.783")
        and timeline_metrics.get("machine_accounted_timeline_seconds")
        == MEDIA_DURATION_SECONDS
        and timeline_metrics.get("overlap_count") == 0
        and timeline_metrics.get("internal_gap_count") == 932
    )
    linked_count = sum(
        bool(row.get("Control_IDs")) for row in json_rows if isinstance(row, dict)
    )
    unlinked_are_pending = all(
        row.get("Preliminary_Disposition") == "Human-review-needed"
        and row.get("Content_Class") == "Context"
        for row in json_rows
        if isinstance(row, dict) and not row.get("Control_IDs")
    )
    review_complete = adjudicated_payload.get("human_review_completed") is True
    adjudicated_coverage = adjudicated_payload.get("coverage", {})
    adjudicated_coverage = (
        adjudicated_coverage if isinstance(adjudicated_coverage, dict) else {}
    )
    timeline_status = adjudicated_coverage.get("timeline_review_status")
    full_timeline_reviewed = (
        timeline_status == "Human full-media review complete"
        and adjudicated_coverage.get("unreviewed_media_seconds") == 0
        and adjudicated_coverage.get("gap_register_sha256")
        == coverage.get("gap_register_sha256")
        and adjudicated_coverage.get("uncovered_interval_count")
        == len(expected_gaps)
        and adjudicated_coverage.get("human_classified_uncovered_intervals")
        == len(expected_gaps)
        and adjudicated_coverage.get("unclassified_uncovered_intervals") == 0
    )
    checks = (
        check(
            "machine source contains sequential IDs 1 through 1195",
            source_ids == list(range(1, 1196)),
            "1,195/1,195 source segments are present",
            f"found {len(source_rows)} valid source rows",
        ),
        check(
            "CSV and JSON ledgers contain the exact S-0001 through S-1195 sequence",
            json_ids == expected_ids and csv_ids == expected_ids,
            "both ledgers contain 1,195 ordered rows",
            f"JSON rows={len(json_ids)}; CSV rows={len(csv_ids)}",
        ),
        check(
            "ledger exposes the full review schema",
            schema_ok,
            f"all {len(required_fields)} fields are present on every row",
            "one or more ledger fields are missing",
        ),
        check(
            "machine timestamps and bilingual text are copied without alteration",
            copied_exactly,
            "1,195/1,195 rows match the machine source",
            "one or more ledger rows diverge from the machine source",
        ),
        check(
            "uncited segments remain conservative human-review placeholders",
            unlinked_are_pending,
            f"{1195 - linked_count} uncited segments remain human-review-needed",
            "an uncited segment was promoted beyond the conservative boundary",
        ),
        check(
            "ASR interval union and uncovered intervals account for the complete media duration",
            interval_union_complete,
            "2,333.500 ASR-union seconds plus 452.783 uncovered seconds equal 2,786.283 seconds; no overlaps",
            "ASR interval union, overlap, or uncovered-time accounting is inconsistent",
        ),
        check(
            "machine uncovered-interval ledger is exact and remains human-pending",
            gap_schema_ok and gap_rows_match,
            "934/934 lead/internal/tail intervals are enumerated without inferred human meaning",
            "gap-ledger schema, intervals, ordering, or human-pending boundary is inconsistent",
        ),
        check(
            "coverage summary is hash-bound to the exact interval accounting",
            coverage_metrics_match,
            "coverage JSON matches the independently recomputed union/gap metrics and gap-ledger hash",
            "coverage JSON omits or disagrees with interval-union/gap evidence",
        ),
        check(
            "machine timeline boundary is explicit",
            coverage.get("first_segment_start") == "00:00:01.060"
            and coverage.get("last_segment_end") == "00:46:25.010"
            and coverage.get("media_duration") == "00:46:26.283"
            and preliminary_timeline_status
            == (
                "Machine uncovered-interval register complete; human full-media "
                "classification pending"
            ),
            "ASR span, uncovered intervals, and unreviewed full-media boundary are recorded",
            "timeline metadata is missing or overstates human review",
        ),
    )
    return Result(
        experiment="IRIS-EXP-05",
        state=(
            "STRUCTURE_PASS_PENDING_FULL_MEDIA_HUMAN_REVIEW"
            if all(item.passed for item in checks)
            else "FAIL"
        ),
        checks=checks,
        readiness_checks=(
            check(
                "all 1,195 segments have completed human review",
                review_complete
                and len(adjudicated_rows) == 1195
                and all(
                    isinstance(row, dict)
                    and row.get("Review_Status") == "Adjudicated"
                    for row in adjudicated_rows
                ),
                "1,195/1,195 segments are adjudicated",
                "human review remains incomplete",
            ),
            check(
                "the complete 46:26.283 media timeline has human review evidence",
                full_timeline_reviewed,
                "full-media review is recorded with zero unreviewed seconds",
                "machine ASR span is present, but full-media human review is pending",
            ),
        ),
        closure_checks=(
            check(
                "all substantive reviewed segments have a control or external-claim link",
                review_complete
                and all(
                    isinstance(row, dict)
                    and (
                        row.get("Content_Class")
                        in {"Context", "Housekeeping", "Noise or non-speech"}
                        or bool(row.get("Control_IDs"))
                        or bool(row.get("External_Claim_IDs"))
                    )
                    for row in adjudicated_rows
                ),
                "zero orphan substantive clauses remain",
                "orphan-clause closure cannot be established before adjudication",
            ),
        ),
        evidence_boundary=(
            "A structural PASS proves deterministic machine/source coverage only. "
            "It does not prove full-media review, meaning, speaker identity, or clause closure."
        ),
    )


def exp06() -> Result:
    preliminary_payload = read_json(LEDGER_JSON)
    preliminary_rows_raw = preliminary_payload.get("rows", [])
    preliminary_rows = (
        preliminary_rows_raw if isinstance(preliminary_rows_raw, list) else []
    )
    payload = read_json(ADJUDICATED_JSON)
    rows_raw = payload.get("rows", [])
    rows = rows_raw if isinstance(rows_raw, list) else []
    fields = {
        "Reviewed_HE",
        "Reviewed_EN",
        "Reviewer_A",
        "Reviewer_B",
        "Disagreement",
        "Adjudication",
        "Review_Status",
        "Speaker",
        "Speaker_Basis",
    }
    fields_present = not rows or all(
        isinstance(row, dict) and fields <= set(row) for row in rows
    )
    named_machine_speakers = [
        row.get("Segment_ID")
        for row in preliminary_rows
        if isinstance(row, dict) and row.get("Speaker") != "Unresolved"
    ]
    no_fabricated_review = preliminary_payload.get("human_review_completed") is False and all(
        isinstance(row, dict)
        and row.get("Review_Status") == "Machine-only; human review needed"
        and not row.get("Reviewed_HE")
        and not row.get("Reviewed_EN")
        and not row.get("Reviewer_A")
        and not row.get("Reviewer_B")
        and not row.get("Adjudication")
        for row in preliminary_rows
    )
    try:
        merge_check = subprocess.run(
            [sys.executable, str(ADJUDICATED_BUILDER), "--check"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )
        merge_interface_valid = merge_check.returncode == 0
        merge_detail = (merge_check.stdout + merge_check.stderr).strip()
    except (OSError, subprocess.SubprocessError) as error:
        merge_interface_valid = False
        merge_detail = str(error)
    review_complete = payload.get("human_review_completed") is True
    reviewers_complete = review_complete and all(
        isinstance(row, dict)
        and row.get("Reviewer_A")
        and row.get("Reviewer_B")
        and row.get("Review_Status") == "Adjudicated"
        for row in rows
    )
    disagreements_resolved = reviewers_complete and all(
        isinstance(row, dict)
        and (not row.get("Disagreement") or row.get("Adjudication"))
        for row in rows
    )
    checks = (
        check(
            "separate adjudicated ledger schema is valid when present",
            fields_present,
            "adjudicated output is absent or has all human-review fields",
            "human-review schema is incomplete",
        ),
        check(
            "deterministic human-review merge interface is valid",
            merge_interface_valid,
            merge_detail or "merge interface verified",
            merge_detail or "merge-interface check failed",
        ),
        check(
            "machine-only ledger does not fabricate review completion",
            no_fabricated_review,
            "review state is internally consistent",
            "review fields and completion marker conflict",
        ),
        check(
            "machine-only named attribution is limited to documented S-0001–S-0006",
            named_machine_speakers == [f"S-{index:04d}" for index in range(1, 7)],
            "only the six documented opening segments are named",
            "unsupported named attribution exists in the machine-only ledger",
        ),
    )
    return Result(
        experiment="IRIS-EXP-06",
        state=(
            "STRUCTURE_PASS_PENDING_DUAL_BILINGUAL_REVIEW"
            if all(item.passed for item in checks) and not review_complete
            else "PASS" if all(item.passed for item in checks) else "FAIL"
        ),
        checks=checks,
        readiness_checks=(
            check(
                "two independent reviewers completed all 1,195 rows",
                reviewers_complete,
                "Reviewer A and Reviewer B are recorded on every adjudicated row",
                "dual bilingual review is pending",
            ),
            check(
                "all recorded disagreements have adjudication",
                disagreements_resolved,
                "no unresolved review disagreement remains",
                "disagreement adjudication is pending",
            ),
        ),
        closure_checks=(
            check(
                "every named speaker attribution has a documented human basis",
                reviewers_complete
                and all(
                    isinstance(row, dict)
                    and (row.get("Speaker") == "Unresolved" or row.get("Speaker_Basis"))
                    for row in rows
                ),
                "all named attributions retain their review basis",
                "named-attribution closure is not established",
            ),
        ),
        evidence_boundary=(
            "Schema integrity and conservative machine attribution are not bilingual "
            "review, diarization, or adjudication."
        ),
    )


def exp07() -> Result:
    payload = read_json(LEDGER_JSON)
    provenance = read(PROVENANCE_MANIFEST)
    source_entries_raw = payload.get("sources", [])
    source_entries = (
        source_entries_raw if isinstance(source_entries_raw, list) else []
    )
    expected_sources = (MACHINE_JSONL, REQUIREMENT_REGISTER, ACTION_REGISTER)
    recorded_hashes = {
        entry.get("path"): entry.get("sha256")
        for entry in source_entries
        if isinstance(entry, dict)
    }
    hashes_match = all(
        recorded_hashes.get(path.relative_to(ROOT).as_posix()) == sha256(path)
        for path in expected_sources
    )
    try:
        reproducibility = subprocess.run(
            [sys.executable, str(LEDGER_BUILDER), "--check"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )
        reproducible = reproducibility.returncode == 0
        reproduction_detail = (
            "tracked CSV/JSON exactly match deterministic regeneration"
            if reproducible
            else (reproducibility.stdout + reproducibility.stderr).strip()
        )
    except (OSError, subprocess.SubprocessError) as error:
        reproducible = False
        reproduction_detail = str(error)
    csv_rows = read_csv_rows(LEDGER_CSV)
    json_rows_raw = payload.get("rows", [])
    json_rows = json_rows_raw if isinstance(json_rows_raw, list) else []
    formats_agree = len(csv_rows) == len(json_rows) == 1195 and all(
        isinstance(json_row, dict)
        and csv_row.get("Segment_ID") == json_row.get("Segment_ID")
        and csv_row.get("Control_IDs") == json_row.get("Control_IDs")
        and csv_row.get("Review_Status") == json_row.get("Review_Status")
        for csv_row, json_row in zip(csv_rows, json_rows, strict=True)
    )
    manifested_paths = (
        MACHINE_JSONL,
        REQUIREMENT_REGISTER,
        ACTION_REGISTER,
        LEDGER_CSV,
        LEDGER_JSON,
        GAP_LEDGER_CSV,
    )
    provenance_current = all(
        path.name in provenance and sha256(path) in provenance
        for path in manifested_paths
    )
    merge_check = subprocess.run(
        [sys.executable, str(ADJUDICATED_BUILDER), "--check"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )
    merge_interface_current = merge_check.returncode == 0
    base_match = re.search(r"Repository base revision at refresh: `([0-9a-f]{40})`", provenance)
    head = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=10,
        check=False,
    ).stdout.strip()
    status_output = subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=10,
        check=False,
    ).stdout
    working_tree_dirty = bool(status_output.strip())
    package_revision = base_match.group(1) if base_match else ""
    package_revision_is_ancestor = bool(package_revision) and subprocess.run(
        ["git", "merge-base", "--is-ancestor", package_revision, head],
        cwd=ROOT,
        capture_output=True,
        timeout=10,
        check=False,
    ).returncode == 0
    frozen_package_paths = (
        MACHINE_JSONL,
        REQUIREMENT_REGISTER,
        ACTION_REGISTER,
        LEDGER_CSV,
        LEDGER_JSON,
        GAP_LEDGER_CSV,
        LEDGER_BUILDER,
        REVIEWER_A_TEMPLATE,
        REVIEWER_B_TEMPLATE,
        ADJUDICATION_TEMPLATE,
        HUMAN_REVIEW_WORKFLOW,
        ADJUDICATED_BUILDER,
        MASTER,
        CLOSURE,
        GOVERNANCE_CONTROL,
        CLOSURE_CERTIFICATE,
        PRESENTATION_MANIFEST,
        PRESENTATION_DECK,
        SUBMISSION_RECEIPT_SCHEMA,
        SUBMISSION_RECEIPT_TEMPLATE,
    )
    package_unchanged_from_revision = (
        package_revision_is_ancestor
        and subprocess.run(
            [
                "git",
                "diff",
                "--quiet",
                package_revision,
                "--",
                *(str(path.relative_to(ROOT)) for path in frozen_package_paths),
            ],
            cwd=ROOT,
            capture_output=True,
            timeout=20,
            check=False,
        ).returncode
        == 0
    )
    revision_distinction = package_unchanged_from_revision and (
        not working_tree_dirty
        or "base revision alone does not contain those updates" in provenance
        or "provenance binding may be committed in a later descendant" in provenance
    )
    broader_paths = (
        MASTER,
        CLOSURE,
        GOVERNANCE_CONTROL,
        PRESENTATION_MANIFEST,
        REHEARSAL_RECORD,
        DELIVERY_RECORD,
    )
    broader_provenance_current = all(
        path.name in provenance and sha256(path) in provenance for path in broader_paths
    )
    adjudicated_outputs_current = (
        ADJUDICATED_CSV.exists()
        and ADJUDICATED_JSON.exists()
        and sha256(ADJUDICATED_CSV) in provenance
        and sha256(ADJUDICATED_JSON) in provenance
    )
    checks = (
        check(
            "ledger records current machine/register SHA-256 values",
            hashes_match,
            "all three source hashes match current files",
            "a source file changed after ledger generation",
        ),
        check(
            "tracked ledger outputs are deterministic",
            reproducible,
            reproduction_detail,
            reproduction_detail or "generator check failed",
        ),
        check(
            "CSV and JSON control/review projections agree",
            formats_agree,
            "1,195/1,195 rows agree across formats",
            "CSV and JSON projections diverge",
        ),
        check(
            "provenance manifest contains current source and ledger hashes",
            provenance_current,
            "machine JSONL, source registers, segment ledgers, and gap ledger are current",
            "one or more provenance-manifest hash entries are missing or stale",
        ),
        check(
            "human-review merge interface is deterministic in pending or completed state",
            merge_interface_current,
            (merge_check.stdout + merge_check.stderr).strip(),
            (merge_check.stdout + merge_check.stderr).strip(),
        ),
        check(
            "provenance identifies an unchanged committed package revision and qualifies working state",
            revision_distinction,
            "package revision is an ancestor, frozen package paths are unchanged, and working state is explicit",
            "package revision, frozen-path comparison, or working-state provenance is missing or stale",
        ),
    )
    return Result(
        experiment="IRIS-EXP-07",
        state="PASS" if all(item.passed for item in checks) else "FAIL",
        checks=checks,
        readiness_checks=(
            check(
                "master, closure, governance, and presentation records have current hashes",
                broader_provenance_current,
                "all six canonical/governance presentation records are current",
                "one or more canonical/governance presentation hashes are absent or stale",
            ),
            check(
                "completed adjudicated outputs are provenance-bound",
                adjudicated_outputs_current,
                "both adjudicated-ledger hashes are recorded",
                "adjudicated outputs are not yet complete and provenance-bound",
            ),
        ),
        closure_checks=(
            check(
                "closure package is unchanged from its committed package revision with a clean working tree",
                not working_tree_dirty and package_unchanged_from_revision,
                "frozen package paths match the committed package revision and the working tree is clean",
                "package paths changed after the recorded revision or the working tree is dirty",
            ),
        ),
        evidence_boundary=(
            "A PASS proves current deterministic provenance for the preliminary "
            "ledger. It does not validate the truth of machine text or control meaning."
        ),
    )


def exp08() -> Result:
    checklist = read(PRESENTATION)
    manifest = read(PRESENTATION_MANIFEST)
    rehearsal = read(REHEARSAL_RECORD)
    delivery = read(DELIVERY_RECORD)
    source_manifest = read_json(PRESENTATION_SOURCE_MANIFEST)
    source_errors = source_manifest_errors(source_manifest)
    try:
        source_check = subprocess.run(
            [sys.executable, str(PRESENTATION_SOURCE_MANIFEST_BUILDER), "--check"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )
        source_manifest_current = source_check.returncode == 0 and not source_errors
        source_manifest_detail = (
            "detached source manifest matches the current PPTX and every notes source"
            if source_manifest_current
            else "; ".join(source_errors)
            or (source_check.stdout + source_check.stderr).strip()
        )
    except (OSError, subprocess.SubprocessError) as error:
        source_manifest_current = False
        source_manifest_detail = str(error)
    render_schema = read_json(PRESENTATION_RENDER_SCHEMA)
    render_template = read_json(PRESENTATION_RENDER_TEMPLATE)
    render_template_errors = render_manifest_structure_errors(
        render_template, require_verified=False
    )
    render_interface_ready = (
        render_schema.get("$id")
        == "https://vego-ai.local/schemas/iris-presentation-render-manifest-v1.schema.json"
        and "$defs" in render_schema
        and "allOf" in render_schema
        and not render_template_errors
    )
    render_record = read_json(PRESENTATION_RENDER_RECORD)
    render_record_errors = render_manifest_structure_errors(
        render_record, require_verified=True
    )
    verified_render_manifest = bool(render_record) and not render_record_errors
    missing_controls = [control for control in EXPECTED_IDS if control not in manifest]
    expected_artifacts_documented = "| PPTX |" in manifest and "| PDF |" in manifest
    package_paths = (
        PRESENTATION_DECK,
        PRESENTATION_PDF,
        REVIEW_WORKBOOK,
        LOCAL_PACKAGE_BACKUP,
    )
    package_artifacts_exist = all(
        path.exists() and path.stat().st_size > 0 for path in package_paths
    )
    provenance = read(PROVENANCE_MANIFEST)
    backup_status_lines = [
        line
        for line in (*manifest.splitlines(), *delivery.splitlines())
        if line.startswith("| Local offline backup |")
        or line.startswith("- Offline-backup state:")
    ]
    backup_marked_current = len(backup_status_lines) == 2 and all(
        "CURRENT" in line.upper()
        and "STALE" not in line.upper()
        and "INVALIDATED" not in line.upper()
        for line in backup_status_lines
    )
    backup_content_current = backup_members_match(
        LOCAL_PACKAGE_BACKUP,
        (PRESENTATION_DECK, PRESENTATION_PDF, REVIEW_WORKBOOK),
    )
    package_hashes_current = (
        package_artifacts_exist
        and backup_marked_current
        and backup_content_current
        and all(
            path.name in manifest
            and sha256(path) in manifest
            and path.name in provenance
            and sha256(path) in provenance
            for path in package_paths
        )
    )
    qa_bound_to_current_package = (
        package_artifacts_exist
        and verified_render_manifest
        and sha256(PRESENTATION_DECK) in rehearsal
        and sha256(PRESENTATION_PDF) in rehearsal
        and "Automated preflight verdict: `PASS`" in rehearsal
        and "21/21 PowerPoint-native renders inspected" in rehearsal
    )
    rehearsal_ready = (
        bool(rehearsal)
        and "STATUS: **COMPLETE**" in rehearsal.upper()
        and "NOT RUN" not in rehearsal.upper()
        and all(name in rehearsal for name in ("Iris-role", "Arnon-role", "Recorder"))
    )
    delivery_ready = (
        bool(delivery)
        and not contains_pending_marker(
            delivery, ("NOT SHARED", "NOT SENT", "PENDING", "NOT TESTED")
        )
        and re.search(r"Iris.*\bPASS\b", delivery, re.IGNORECASE) is not None
        and re.search(r"Arnon.*\bPASS\b", delivery, re.IGNORECASE) is not None
    )
    checks = (
        check(
            "presentation manifest maps all 44 current controls",
            bool(manifest) and not missing_controls,
            "44/44 R/A/Q controls are reachable from the manifest",
            "manifest missing or controls absent: " + ", ".join(missing_controls),
        ),
        check(
            "manifest reserves controlled PPTX and PDF package entries",
            expected_artifacts_documented,
            "both presentation artifact types are documented",
            "PPTX/PDF package entries are missing from the manifest",
        ),
        check(
            "checklist preserves preflight, live-call, and closeout controls",
            all(
                heading in checklist
                for heading in (
                    "## Before the meeting",
                    "## During the meeting",
                    "## After the meeting",
                    "## Forbidden claims",
                )
            ),
            "all presentation-control sections are present",
            "presentation-control section is missing",
        ),
        check(
            "Drive metadata, ACL, and research authorization remain separate gates",
            all(
                marker in checklist
                for marker in (
                    "metadata inventory",
                    "ACL and intended viewer-only permission",
                    "purpose-specific authorization",
                )
            ),
            "checklist separates observable inventory, permission evidence, and named-user authority",
            "Drive visibility or metadata is still conflated with ACL/authorization",
        ),
        check(
            "render-manifest schema and pending template preserve the final-render gate",
            render_interface_ready,
            "schema exists and the template remains PENDING_FINAL_RENDER",
            "render schema/template is missing, malformed, or overstates completion: "
            + ", ".join(render_template_errors),
        ),
    )
    return Result(
        experiment="IRIS-EXP-08",
        state=(
            "STRUCTURE_PASS_PENDING_REHEARSAL_AND_DELIVERY"
            if all(item.passed for item in checks)
            else "FAIL"
        ),
        checks=checks,
        readiness_checks=(
            check(
                "detached presentation source manifest is current and hash-bound",
                source_manifest_current,
                source_manifest_detail,
                source_manifest_detail or "source manifest is missing or stale",
            ),
            check(
                "controlled PPTX, PDF, review workbook, and backup exist",
                package_artifacts_exist,
                "all four local package artifacts are present and non-empty",
                "one or more controlled local package artifacts are missing",
            ),
            check(
                "current package hashes and backup members match controlled artifacts",
                package_hashes_current,
                "PPTX, PDF, workbook, and backup hashes match both records; backup members match the current artifacts",
                "package status, hashes, or backup members are missing, stale, or inconsistent",
            ),
            check(
                "verified render manifest binds the current package and all 21 inspected native slides",
                verified_render_manifest,
                "PPTX/PDF, 21 slide images, montage, renderer, and local visual inspection are hash-bound",
                "verified render manifest is absent or inconsistent: "
                + ", ".join(render_record_errors),
            ),
            check(
                "visual QA is bound to the current PPTX/PDF hashes",
                qa_bound_to_current_package,
                "current PPTX/PDF hashes and 21-slide render inspection are recorded",
                "visual-QA evidence is missing or refers to a different package",
            ),
            check(
                "dated four-role live rehearsal is complete",
                rehearsal_ready,
                "presenter, Iris-role, Arnon-role, and recorder are evidenced",
                "rehearsal remains missing, incomplete, or NOT RUN",
            ),
            check(
                "Iris and Arnon delivery/access tests pass",
                delivery_ready,
                "both recipient access tests are recorded as PASS",
                "package remains unshared or recipient access is untested",
            ),
        ),
        evidence_boundary=(
            "Artifact existence and manifest coverage are not a human rehearsal, "
            "Ali release approval, delivery, or recipient access proof."
        ),
    )


def exp09() -> Result:
    presentation = read(PRESENTATION)
    minutes = read(SUPERVISOR_MINUTES)
    decision_log = read(DECISION_LOG)
    required_decisions = [f"D-RQ-{index:02d}" for index in range(1, 11)]
    worksheet_complete = all(decision in presentation for decision in required_decisions)
    outcomes = decision_outcomes("\n".join((presentation, minutes)))
    all_outcomes_recorded = all(decision in outcomes for decision in required_decisions)
    propagated = all(decision in decision_log for decision in required_decisions)
    decision_interface_paths = (
        ROOT / "docs/research/phd-proposal/2026-08-05-rq-decision-pack.md",
        ROOT / "docs/research/meetings/2026-08-05-supervisor-pre-read.md",
        PRESENTATION,
        ROOT / "docs/research/meetings/2026-08-05-supervisor-release-gate-and-runbook.md",
    )
    interface_text = "\n".join(read(path) for path in decision_interface_paths)
    slide_texts = pptx_slide_texts(PRESENTATION_DECK)
    decision_slide = slide_texts[10] if len(slide_texts) >= 11 else ""
    vocabulary = (
        "Confirm",
        "Confirm with correction",
        "Retire or supersede",
        "Defer",
    )
    decision_vocabulary_aligned = (
        all(outcome in interface_text for outcome in vocabulary)
        and all(outcome in decision_slide for outcome in vocabulary)
        and "Approve with correction" not in decision_slide
        and "Reject" not in decision_slide
    )
    final_outcomes = {
        "Confirm",
        "Confirm with correction",
        "Retire or supersede",
    }
    all_final = all_outcomes_recorded and all(
        outcomes[decision] in final_outcomes for decision in required_decisions
    )
    checks = (
        check(
            "decision worksheet exposes D-RQ-01 through D-RQ-10",
            worksheet_complete,
            "10/10 supervisor decisions are present",
            "one or more supervisor decisions are absent",
        ),
        check(
            "decision log retains propagation fields",
            all(
                field in decision_log
                for field in (
                    "Decision or change",
                    "Authority/status",
                    "Rationale/evidence",
                    "Affected artifacts",
                    "Supersedes",
                    "Next verification",
                )
            ),
            "decision/change propagation schema is present",
            "decision/change propagation schema is incomplete",
        ),
        check(
            "live decision interfaces use the four canonical outcomes",
            decision_vocabulary_aligned,
            "Markdown interfaces and slide 11 use Confirm, correction, retire/supersede, or defer",
            "one or more live interfaces still use legacy approve/reject vocabulary",
        ),
    )
    return Result(
        experiment="IRIS-EXP-09",
        state=(
            "STRUCTURE_PASS_PENDING_SUPERVISOR_DECISIONS"
            if all(item.passed for item in checks)
            else "FAIL"
        ),
        checks=checks,
        readiness_checks=(
            check(
                "all ten decisions have explicit meeting outcomes",
                bool(minutes) and all_outcomes_recorded,
                "10/10 decision outcomes are recorded",
                f"recorded {len(outcomes)}/10 explicit outcomes",
            ),
            check(
                "all ten decisions are propagated to the decision log",
                propagated,
                "D-RQ-01 through D-RQ-10 appear in the canonical change log",
                "meeting decisions have not been fully propagated",
            ),
        ),
        closure_checks=(
            check(
                "no decision remains deferred or rejected without an approved disposition",
                all_final,
                "all ten outcomes are final accepted/corrected/superseded dispositions",
                "one or more outcomes are missing, deferred, or rejected",
            ),
        ),
        evidence_boundary=(
            "A prepared worksheet is not supervisor acceptance. Silence and missing "
            "written outcomes remain pending."
        ),
    )


def exp10() -> Result:
    certificate = read(CLOSURE_CERTIFICATE)
    certificate_upper = certificate.upper()
    receipt_schema = read_json(SUBMISSION_RECEIPT_SCHEMA)
    receipt_template = read_json(SUBMISSION_RECEIPT_TEMPLATE)
    receipt_record = read_json(SUBMISSION_RECEIPT_RECORD)
    required_labels = (
        "Certificate status",
        "Unresolved controls",
        "Human review",
        "Supervisor acceptance",
        "Submission evidence",
    )
    final_states = {
        "Accepted",
        "Accepted with ongoing control",
        "Accepted after correction",
        "Superseded by approved decision",
        "Not applicable by approved Plan B or other decision",
    }
    control_states: dict[str, str] = {}
    for line in certificate.splitlines():
        match = re.match(r"^\|\s*((?:R|A|Q)-\d{2})\s*\|", line)
        if not match:
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        for state in final_states:
            if state in cells:
                control_states[match.group(1)] = state
                break
    receipt_record_present = SUBMISSION_RECEIPT_RECORD.is_file()
    receipt_record_errors = receipt_structure_errors(receipt_record)
    submission = receipt_section(receipt_record, "submission")
    authorization = receipt_section(receipt_record, "authorization")
    package = receipt_section(receipt_record, "package")
    receipt_artifact = receipt_section(receipt_record, "receipt_artifact")
    certificate_binding = receipt_section(receipt_record, "certificate_binding")

    package_path = repo_artifact(package.get("path"))
    receipt_artifact_path = repo_artifact(receipt_artifact.get("path"))
    authorization_evidence_path = repo_artifact(authorization.get("evidence_path"))
    bound_certificate_path = repo_artifact(
        certificate_binding.get("certificate_path")
    )

    receipt_verified = (
        receipt_record_present
        and not receipt_record_errors
        and receipt_record.get("status") == "VERIFIED"
    )
    submission_identity_valid = all(
        isinstance(submission.get(field), str) and submission[field].strip()
        for field in ("route", "receipt_id", "submitted_by", "recipient_authority")
    ) and valid_zoned_timestamp(submission.get("submitted_at"))
    package_valid = (
        package_path is not None
        and valid_sha256(package.get("sha256"))
        and sha256(package_path) == str(package.get("sha256")).upper()
    )
    receipt_artifact_valid = (
        receipt_artifact_path is not None
        and receipt_artifact_path != SUBMISSION_RECEIPT_RECORD.resolve()
        and valid_sha256(receipt_artifact.get("sha256"))
        and sha256(receipt_artifact_path)
        == str(receipt_artifact.get("sha256")).upper()
    )
    authorization_valid = (
        authorization.get("authorized") is True
        and isinstance(authorization.get("authority"), str)
        and bool(str(authorization.get("authority")).strip())
        and valid_zoned_timestamp(authorization.get("authorized_at"))
        and authorization_evidence_path is not None
        and valid_sha256(authorization.get("evidence_sha256"))
        and sha256(authorization_evidence_path)
        == str(authorization.get("evidence_sha256")).upper()
    )
    certificate_id_match = re.search(
        r"Certificate ID(?: when issued)?\s*:\s*`([^`]+)`", certificate, re.I
    )
    certificate_id = certificate_id_match.group(1).strip() if certificate_id_match else ""
    certificate_binding_valid = (
        bound_certificate_path == CLOSURE_CERTIFICATE.resolve()
        and certificate_id
        and "YYYY" not in certificate_id.upper()
        and certificate_binding.get("certificate_id") == certificate_id
        and valid_sha256(certificate_binding.get("certificate_sha256"))
        and sha256(CLOSURE_CERTIFICATE)
        == str(certificate_binding.get("certificate_sha256")).upper()
        and all(
            str(value) in certificate
            for value in (
                submission.get("receipt_id", ""),
                package.get("sha256", ""),
                receipt_artifact.get("sha256", ""),
                SUBMISSION_RECEIPT_RECORD.relative_to(ROOT).as_posix(),
            )
            if str(value)
        )
    )
    issued = (
        re.search(r"Certificate status\s*:\s*\*\*ISSUED\*\*", certificate, re.I)
        is not None
        and "NOT ISSUED" not in certificate_upper
    )
    markers_closed = all(
        re.search(pattern, certificate, re.IGNORECASE) is not None
        for pattern in (
            r"Unresolved controls\s*:\s*\*\*0\*\*",
            r"Human review\s*:\s*\*\*COMPLETE\*\*",
            r"Supervisor acceptance\s*:\s*\*\*CONFIRMED\*\*",
            r"Submission evidence\s*:\s*\*\*VERIFIED\*\*",
        )
    )
    checks = (
        check(
            "closure certificate template contains all gate markers",
            bool(certificate) and all(label in certificate for label in required_labels),
            "certificate status, unresolved, review, acceptance, and submission fields exist",
            "closure certificate template or required marker is missing",
        ),
        check(
            "certificate issuance state is explicit",
            "Certificate status:" in certificate,
            "certificate status field is present",
            "certificate status field is missing",
        ),
        check(
            "authorized submission receipt schema and pending template are valid",
            bool(receipt_schema)
            and not receipt_structure_errors(receipt_template)
            and receipt_template.get("status") == "NOT_SUBMITTED"
            and receipt_section(receipt_template, "authorization").get("authorized")
            is False,
            "receipt schema exists and template remains explicitly unsubmitted",
            "receipt schema/template is missing, malformed, or falsely completed",
        ),
    )
    return Result(
        experiment="IRIS-EXP-10",
        state=(
            "STRUCTURE_PASS_CERTIFICATE_NOT_ISSUED"
            if all(item.passed for item in checks)
            else "FAIL"
        ),
        checks=checks,
        readiness_checks=(
            check(
                "certificate has a complete 44-control final-state table",
                set(control_states) == set(EXPECTED_IDS),
                "44/44 controls have allowed final dispositions",
                f"found {len(control_states)}/44 allowed final dispositions",
            ),
        ),
        closure_checks=(
            check(
                "certificate is issued with zero unresolved human/supervisor/submission gates",
                issued and markers_closed,
                "certificate markers establish issued evidence-backed closure",
                "certificate remains unissued or a closure marker is pending",
            ),
            check(
                "verified authorized submission receipt record exists",
                receipt_verified,
                "the exact authorized-submission-receipt record is schema-complete and VERIFIED",
                "the exact authorized-submission-receipt record is absent, pending, or malformed",
            ),
            check(
                "submission route, zoned timestamp, and receipt ID are recorded",
                receipt_verified and submission_identity_valid,
                "submission identity and route are complete",
                "submission route, zoned timestamp, receipt ID, submitter, or recipient authority is missing",
            ),
            check(
                "submitted package hash matches the recorded package",
                receipt_verified and package_valid,
                "submitted package path and SHA-256 match",
                "submitted package is missing, outside the repository, or hash-mismatched",
            ),
            check(
                "external receipt artifact hash is verified",
                receipt_verified and receipt_artifact_valid,
                "external receipt artifact path and SHA-256 match",
                "external receipt artifact is missing, self-referential, or hash-mismatched",
            ),
            check(
                "receipt is bound to the issued certificate and certificate evidence",
                receipt_verified and certificate_binding_valid,
                "certificate ID/hash and receipt/package evidence are bidirectionally bound",
                "certificate ID/hash or receipt/package evidence binding is absent or mismatched",
            ),
            check(
                "submission has explicit hashed authorization evidence",
                receipt_verified and authorization_valid,
                "authorization authority, zoned timestamp, evidence path, and SHA-256 are verified",
                "explicit authorization or its hashed evidence is absent or invalid",
            ),
        ),
        evidence_boundary=(
            "A template is not a certificate. It may be issued only after all controls "
            "have final dispositions and human, supervisor, and submission evidence exists."
        ),
    )


RUNNERS = {
    "IRIS-EXP-01": exp01,
    "IRIS-EXP-02": exp02,
    "IRIS-EXP-03": exp03,
    "IRIS-EXP-04": exp04,
    "IRIS-EXP-05": exp05,
    "IRIS-EXP-06": exp06,
    "IRIS-EXP-07": exp07,
    "IRIS-EXP-08": exp08,
    "IRIS-EXP-09": exp09,
    "IRIS-EXP-10": exp10,
}


def render(results: list[Result], mode: str = "structure") -> str:
    lines = [
        "# Iris Requirements-Closure Validation",
        "",
        "These are documentation/governance conformance results. A passing automated "
        "check does not close a human or external gate.",
        f"Selected gate mode: **{mode}**.",
        "",
    ]
    for result in results:
        mode_passed = result.passed_for_mode(mode)
        lines.extend(
            [
                f"## {result.experiment}",
                "",
                f"- State: **{result.state}**",
                f"- {mode.title()} gate: **{'PASS' if mode_passed else 'PENDING/FAIL'}**",
                f"- Evidence boundary: {result.evidence_boundary}",
                "",
            ]
        )
        for check in result.checks_for_mode(mode):
            marker = "PASS" if check.passed else "FAIL"
            lines.append(f"- [{marker}] {check.name} — {check.detail}")
        lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    selection = parser.add_mutually_exclusive_group(required=True)
    selection.add_argument(
        "--experiment",
        choices=EXPERIMENTS,
        help="Run one Iris-alignment experiment.",
    )
    selection.add_argument("--all", action="store_true", help="Run all experiments.")
    parser.add_argument(
        "--refresh",
        action="store_true",
        help="Write ignored JSON/Markdown diagnostics under reports/generated.",
    )
    parser.add_argument(
        "--mode",
        choices=MODES,
        default="structure",
        help=(
            "Gate depth: structure validates schemas/coverage; readiness also "
            "requires presentation/rehearsal/access evidence; closure also "
            "requires human adjudication, final decisions, and submission evidence."
        ),
    )
    args = parser.parse_args()

    selected = EXPERIMENTS if args.all else (args.experiment,)
    results = [RUNNERS[experiment]() for experiment in selected]
    report = render(results, args.mode)
    print(report)

    if args.refresh:
        output = ROOT / "reports/generated/iris_requirements_closure"
        output.mkdir(parents=True, exist_ok=True)
        (output / "latest.md").write_text(report + "\n", encoding="utf-8")
        payload = {
            "schemaVersion": "IrisRequirementsClosureValidation-v2",
            "mode": args.mode,
            "results": [
                {
                    **asdict(result),
                    "structure_passed": result.passed,
                    "selected_mode_passed": result.passed_for_mode(args.mode),
                }
                for result in results
            ],
        }
        (output / "latest.json").write_text(
            json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )

    return 0 if all(result.passed_for_mode(args.mode) for result in results) else 1


if __name__ == "__main__":
    sys.exit(main())
