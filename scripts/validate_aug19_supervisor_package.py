#!/usr/bin/env python3
"""Fail-closed validation for the controlled 2026-08-19 supervisor package."""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import re
import zipfile
from pathlib import Path
from typing import Any

from packaging.version import InvalidVersion, Version

REQUIRED_FILES = (
    "Chapter_2_Literature_Review_EN.docx",
    "Chapter_2_Literature_Review_EN.pdf",
    "Chapter_2_Literature_Review_HE.docx",
    "Chapter_2_Literature_Review_HE.pdf",
    "Human_Agent_Classification_Bilingual.pptx",
    "Human_Agent_Classification_Bilingual.pdf",
    "Supervisor_PreRead_EN.pdf",
    "Supervisor_PreRead_HE.pdf",
    "Supervisor_Tracker_and_Decisions_Bilingual.pdf",
    "package-manifest.sanitized.json",
)

LOCKED_BOUNDARIES = {
    "scope": "Literature only",
    "section_4": "Frozen pre-existing methodology draft",
    "rq_wording": "Open",
    "e6_exploration_identification": "Open",
    "e8_human_expert": "Open",
    "plan_a_b": "Open",
    "methodology_conflict": "Open",
    "exp_005": "0/24",
    "medical_readiness": "0/6",
    "human_screening": "Pending",
}

PLACEHOLDER_PATTERNS = (
    re.compile(r"\b(?:TODO|TBD|FIXME|LOREM IPSUM)\b", re.IGNORECASE),
    re.compile(r"\[(?:insert|replace|placeholder)[^\]]*\]", re.IGNORECASE),
)

FORBIDDEN_CLAIM_PATTERNS = (
    re.compile(r"\b(?:RQ|research questions?) (?:is|are|were|has been|have been) approved\b", re.IGNORECASE),
    re.compile(r"\bmethodology (?:is|was|has been) approved\b", re.IGNORECASE),
    re.compile(r"\bEXP-?005 (?:is|was|has been) (?:complete|validated)\b", re.IGNORECASE),
    re.compile(r"\bmedical readiness (?:is|was|has been) (?:complete|approved)\b", re.IGNORECASE),
)

FORBIDDEN_HEBREW_CLAIM_PATTERNS = (
    re.compile(r"(?:שאל(?:ו|ת) המחקר|שאלות? המחקר)\s+אושר(?:ה|ו)"),
    re.compile(r"המתודולוגיה\s+אושר(?:ה|ו)"),
    re.compile(r"EXP-?005\s+(?:הושלם|אומת|תקף)"),
    re.compile(r"המוכנות הרפואית\s+(?:הושלמה|אושרה)"),
)

UNNATURAL_HEBREW_TERMS = {
    "מוגבלת-ראיות": "תחומה לראיות הזמינות",
    "סוכנית": "של מערכת סוכנים / מבוססת סוכנים",
}

WORKBOOK_ALIAS = "VEGO-AI-PHD-LITERATURE-WORKBOOK"
WORKBOOK_DELIVERY = (
    "Native workbook referenced by logical alias; not duplicated; "
    "live link withheld until Ali-approved release"
)
WORKBOOK_LINK_STATUS = "Withheld pending Ali-approved private release binding"
RESTRICTED_WORKBOOK_PATTERNS = (
    re.compile(r"https://docs\.google\.com/spreadsheets/d/[A-Za-z0-9_-]+", re.IGNORECASE),
    re.compile(r'"spreadsheet_(?:id|url)"\s*:', re.IGNORECASE),
)


class PackageValidationError(ValueError):
    """Raised when a release-blocking package contract is violated."""


MINIMUM_PYPDF_VERSION = Version("6.15.0")


def validate_pypdf_runtime(installed_version: str, receipt_version: str) -> None:
    """Reject vulnerable or ambiguous pypdf runtime and receipt versions."""
    for label, value in (
        ("installed pypdf runtime", installed_version),
        ("pypdf build receipt", receipt_version),
    ):
        try:
            parsed = Version(value)
        except InvalidVersion as exc:
            raise PackageValidationError(
                f"{label} must be at least pypdf 6.15.0; got {value!r}"
            ) from exc
        if parsed < MINIMUM_PYPDF_VERSION:
            raise PackageValidationError(
                f"{label} must be at least pypdf 6.15.0; got {value}"
            )


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def validate_file_set(package_dir: Path) -> None:
    if not package_dir.is_dir():
        raise PackageValidationError(f"package directory missing: {package_dir}")
    actual = {path.name for path in package_dir.iterdir() if path.is_file()}
    expected = set(REQUIRED_FILES)
    missing = sorted(expected - actual)
    extra = sorted(actual - expected)
    if missing:
        raise PackageValidationError(f"missing required package files: {missing}")
    if extra:
        raise PackageValidationError(f"extra files are forbidden in final package: {extra}")


def scan_forbidden_claims(text_by_file: dict[str, str]) -> list[str]:
    """Return evidence-overclaim findings in either package language."""
    return sorted(
        _scan_patterns(
            text_by_file,
            FORBIDDEN_CLAIM_PATTERNS + FORBIDDEN_HEBREW_CLAIM_PATTERNS,
        )
    )


def validate_restricted_workbook_references(text_by_file: dict[str, str]) -> None:
    """Reject live or connector-specific workbook references from tracked review files."""
    findings = _scan_patterns(text_by_file, RESTRICTED_WORKBOOK_PATTERNS)
    if findings:
        raise PackageValidationError(f"restricted workbook reference found: {findings}")


def _section_ids(content: dict[str, Any], language: str) -> list[str]:
    rows = content.get("chapter2", {}).get(language, [])
    if not isinstance(rows, list) or not rows:
        raise PackageValidationError(f"chapter2.{language} must be a non-empty list")
    ids = [str(row.get("id", "")) for row in rows if isinstance(row, dict)]
    if len(ids) != len(rows) or not all(ids):
        raise PackageValidationError(f"chapter2.{language} contains a missing section ID")
    if len(ids) != len(set(ids)):
        raise PackageValidationError(f"chapter2.{language} contains duplicate section IDs")
    return ids


def _json_text(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True)


def validate_hebrew_terminology(content: dict[str, Any]) -> None:
    """Reject known misleading or unnatural Hebrew research terminology."""
    all_text = _json_text(content)
    for term, replacement in UNNATURAL_HEBREW_TERMS.items():
        if term in all_text:
            raise PackageValidationError(
                f"Hebrew terminology contains {term!r}; use {replacement!r}"
            )

    en_by_id = {
        str(row.get("id", "")): _json_text(row)
        for row in content.get("chapter2", {}).get("en", [])
        if isinstance(row, dict)
    }
    he_by_id = {
        str(row.get("id", "")): _json_text(row)
        for row in content.get("chapter2", {}).get("he", [])
        if isinstance(row, dict)
    }
    for section_id, en_text in en_by_id.items():
        he_text = he_by_id.get(section_id, "")
        if re.search(r"\bprovenance\b", en_text, re.IGNORECASE) and "מקוריות" in he_text:
            raise PackageValidationError(
                f"Hebrew provenance terminology in {section_id} must express "
                "ייחוס ומקור ראייתי, not מקוריות (originality)"
            )


def validate_content_contract(content: dict[str, Any]) -> None:
    meeting = content.get("meeting", {})
    expected_meeting = {
        "date": "2026-08-19",
        "time": "09:00-10:00",
        "timezone": "Asia/Jerusalem",
    }
    for key, value in expected_meeting.items():
        if meeting.get(key) != value:
            raise PackageValidationError(f"meeting.{key} must be {value!r}")

    boundaries = content.get("boundaries", {})
    for key, value in LOCKED_BOUNDARIES.items():
        if boundaries.get(key) != value:
            raise PackageValidationError(f"boundaries.{key} must be {value!r}")

    en_ids = _section_ids(content, "en")
    he_ids = _section_ids(content, "he")
    if en_ids != he_ids:
        raise PackageValidationError(
            f"English/Hebrew Chapter 2 section IDs differ: EN={en_ids}, HE={he_ids}"
        )

    decisions = content.get("decisions", [])
    if not isinstance(decisions, list) or not decisions:
        raise PackageValidationError("decisions must be a non-empty list")
    invalid_states = sorted(
        {
            str(row.get("state", ""))
            for row in decisions
            if not isinstance(row, dict)
            or row.get("state") not in {"Open", "Deferred", "Blocked"}
        }
    )
    if invalid_states:
        raise PackageValidationError(
            f"supervisor decisions cannot be presented as resolved: {invalid_states}"
        )

    canonical_pattern = re.compile(r"^(?:F|A|D|Q|R)12-\d{3}$")
    for row in decisions:
        raw = str(row.get("canonical_control_id", "")).strip()
        control_ids = [value.strip() for value in raw.split(";") if value.strip()]
        if not control_ids or not all(canonical_pattern.fullmatch(value) for value in control_ids):
            raise PackageValidationError(
                f"decision is missing a valid canonical control mapping: {raw or 'blank'}"
            )

    workbook = content.get("workbook", {})
    if workbook.get("logical_alias") != WORKBOOK_ALIAS:
        raise PackageValidationError("workbook logical alias is missing or changed")
    if workbook.get("delivery") != WORKBOOK_DELIVERY:
        raise PackageValidationError("workbook delivery must retain the withheld-link policy")
    if workbook.get("link_status") != WORKBOOK_LINK_STATUS:
        raise PackageValidationError("workbook link status must remain withheld")
    if "url" in workbook or "spreadsheet_id" in workbook:
        raise PackageValidationError("workbook contains a restricted live resource reference")
    if "ignored private binding" not in str(workbook.get("private_binding_policy", "")):
        raise PackageValidationError("workbook private release-binding policy is missing")

    validate_restricted_workbook_references({"package-content.json": _json_text(content)})

    validate_hebrew_terminology(content)


def _zip_text(path: Path, prefix: str) -> str:
    with zipfile.ZipFile(path) as archive:
        names = [name for name in archive.namelist() if name.startswith(prefix) and name.endswith(".xml")]
        if not names:
            raise PackageValidationError(f"{path.name} contains no {prefix} XML")
        return "\n".join(
            archive.read(name).decode("utf-8", errors="replace") for name in names
        )


def _pdf_text_and_pages(path: Path) -> tuple[str, int]:
    try:
        from pypdf import PdfReader
    except ImportError as exc:  # pragma: no cover - environment gate
        raise PackageValidationError("bundled pypdf is required for PDF validation") from exc
    reader = PdfReader(str(path))
    if not reader.pages:
        raise PackageValidationError(f"{path.name} has zero pages")
    return "\n".join(page.extract_text() or "" for page in reader.pages), len(reader.pages)


def _artifact_text(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix == ".pdf":
        return _pdf_text_and_pages(path)[0]
    if suffix == ".docx":
        return _zip_text(path, "word/")
    if suffix == ".pptx":
        return _zip_text(path, "ppt/slides/") + "\n" + _zip_text(path, "ppt/notesSlides/")
    return path.read_text(encoding="utf-8")


def _artifact_reference_text(path: Path) -> str:
    """Extract visible and relationship/annotation text for privacy validation."""
    suffix = path.suffix.lower()
    if suffix in {".docx", ".pptx"}:
        try:
            with zipfile.ZipFile(path) as archive:
                names = [
                    name
                    for name in archive.namelist()
                    if name.endswith((".xml", ".rels"))
                ]
                return "\n".join(
                    archive.read(name).decode("utf-8", errors="replace")
                    for name in names
                )
        except zipfile.BadZipFile as exc:
            raise PackageValidationError(
                f"Office reference scan unavailable for {path.name}: {exc}"
            ) from exc
    if suffix == ".pdf":
        visible, _ = _pdf_text_and_pages(path)
        return visible + "\n" + "\n".join(sorted(_pdf_uris(path)))
    return path.read_text(encoding="utf-8")


def _scan_patterns(text_by_file: dict[str, str], patterns: tuple[re.Pattern[str], ...]) -> list[str]:
    findings: list[str] = []
    for name, text in text_by_file.items():
        for pattern in patterns:
            if pattern.search(text):
                findings.append(f"{name}: {pattern.pattern}")
    return sorted(findings)


def validate_manifest_artifacts(artifacts: Any, package_dir: Path) -> int:
    """Validate the manifest's exact, local, non-manifest artifact binding."""
    if not isinstance(artifacts, list):
        raise PackageValidationError("manifest artifacts must be a list")
    expected = set(REQUIRED_FILES) - {"package-manifest.sanitized.json"}
    seen: set[str] = set()
    for row in artifacts:
        if not isinstance(row, dict):
            raise PackageValidationError("manifest artifact row must be an object")
        name = str(row.get("file", "")).strip()
        candidate = Path(name)
        if (
            not name
            or candidate.is_absolute()
            or len(candidate.parts) != 1
            or name in {".", ".."}
            or "/" in name
            or "\\" in name
        ):
            raise PackageValidationError(f"unsafe artifact path: {name!r}")
        if name in seen:
            raise PackageValidationError(f"duplicate manifest artifact: {name}")
        if name == "package-manifest.sanitized.json":
            raise PackageValidationError("manifest cannot bind itself")
        seen.add(name)
        path = package_dir / name
        if not path.is_file():
            raise PackageValidationError(f"manifest artifact is missing: {name}")
        expected_hash = str(row.get("sha256", "")).strip().lower()
        actual_hash = sha256_file(path)
        if expected_hash != actual_hash:
            raise PackageValidationError(f"hash mismatch for {name}")
    if seen != expected:
        raise PackageValidationError(
            f"manifest artifact set does not match package: "
            f"missing={sorted(expected - seen)}, extra={sorted(seen - expected)}"
        )
    return len(seen)


def validate_manifest_bindings(manifest: dict[str, Any], expected: dict[str, str]) -> None:
    """Require every source, runtime, and receipt binding to match exactly."""
    actual = manifest.get("bindings")
    if not isinstance(actual, dict):
        raise PackageValidationError("manifest binding object is missing")
    missing = sorted(set(expected) - set(actual))
    extra = sorted(set(actual) - set(expected))
    mismatched = sorted(
        key for key, value in expected.items() if str(actual.get(key, "")) != value
    )
    if missing or extra or mismatched:
        raise PackageValidationError(
            "manifest binding mismatch: "
            f"missing={missing}, extra={extra}, mismatched={mismatched}"
        )


def validate_pptx_source_notes(path: Path, required_urls: set[str]) -> None:
    """Require a notes [Sources] block containing the exact public URLs."""
    try:
        raw = _zip_text(path, "ppt/notesSlides/")
    except (zipfile.BadZipFile, PackageValidationError) as exc:
        raise PackageValidationError(f"PPTX source notes unavailable: {exc}") from exc
    text = html.unescape(raw)
    if "[Sources]" not in text:
        raise PackageValidationError("PPTX notes are missing a [Sources] block")
    missing = sorted(url for url in required_urls if url not in text)
    if missing:
        raise PackageValidationError(f"PPTX [Sources] URLs missing: {missing}")


def validate_docx_hyperlinks(path: Path, required_urls: set[str]) -> None:
    """Require exact external hyperlink targets in a DOCX relationship set."""
    try:
        with zipfile.ZipFile(path) as archive:
            names = [name for name in archive.namelist() if name.endswith(".rels")]
            raw = "\n".join(
                archive.read(name).decode("utf-8", errors="replace") for name in names
            )
    except zipfile.BadZipFile as exc:
        raise PackageValidationError(f"DOCX hyperlinks unavailable: {exc}") from exc
    text = html.unescape(raw)
    missing = sorted(url for url in required_urls if url not in text)
    if missing:
        raise PackageValidationError(f"DOCX hyperlinks missing: {missing}")


def validate_docx_rtl(path: Path, *, minimum_bidi: int, minimum_rtl: int) -> None:
    """Require Word bidi paragraph and RTL run controls in Hebrew DOCX files."""
    raw = _zip_text(path, "word/")
    bidi_count = len(re.findall(r"<w:bidi(?:\s|/|>)", raw))
    rtl_count = len(re.findall(r"<w:rtl(?:\s|/|>)", raw))
    if bidi_count < minimum_bidi or rtl_count < minimum_rtl:
        raise PackageValidationError(
            "Hebrew DOCX RTL controls insufficient: "
            f"bidi={bidi_count}/{minimum_bidi}, rtl={rtl_count}/{minimum_rtl}"
        )


def _pdf_uris(path: Path) -> set[str]:
    try:
        from pypdf import PdfReader
    except ImportError as exc:  # pragma: no cover - environment gate
        raise PackageValidationError("bundled pypdf is required for PDF validation") from exc
    uris: set[str] = set()
    reader = PdfReader(str(path))
    for page in reader.pages:
        annotations = page.get("/Annots", [])
        for annotation_ref in annotations:
            annotation = annotation_ref.get_object()
            action = annotation.get("/A")
            if action and action.get("/URI"):
                uris.add(str(action.get("/URI")))
    return uris


def validate_pdf_hyperlinks(path: Path, required_urls: set[str]) -> None:
    missing = sorted(required_urls - _pdf_uris(path))
    if missing:
        raise PackageValidationError(f"PDF hyperlinks missing: {missing}")


def validate_visible_tokens(text_by_file: dict[str, str], required_tokens: set[str]) -> None:
    failures: list[str] = []
    for name, text in text_by_file.items():
        normalized_text = text.replace("\u2011", "-").replace("\u200e", "")
        # Word's PDF text layer may insert spaces around visual hyphens and a
        # line break after a hyphen even though the rendered token is intact.
        # Normalize only whitespace adjacent to hyphens so the parity check
        # remains exact for every non-whitespace character.
        normalized_text = re.sub(r"\s*-\s*", "-", normalized_text)
        missing = sorted(token for token in required_tokens if token not in normalized_text)
        if missing:
            failures.append(f"{name}: {missing}")
    if failures:
        raise PackageValidationError(f"visible source parity failed: {failures}")


def validate_package(package_dir: Path, *, content_path: Path) -> dict[str, Any]:
    validate_file_set(package_dir)
    content = json.loads(content_path.read_text(encoding="utf-8"))
    validate_content_contract(content)

    manifest_path = package_dir / "package-manifest.sanitized.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    artifacts = manifest.get("artifacts", [])
    bound_count = validate_manifest_artifacts(artifacts, package_dir)
    expected_bound = set(REQUIRED_FILES) - {manifest_path.name}

    qa_dir = package_dir.parent / "qa"
    build_receipt_path = qa_dir / "build-receipt.json"
    render_receipt_path = qa_dir / "render-receipt.json"
    if not build_receipt_path.is_file() or not render_receipt_path.is_file():
        raise PackageValidationError("build/render receipts are missing")
    build_receipt = json.loads(build_receipt_path.read_text(encoding="utf-8"))
    render_receipt = json.loads(render_receipt_path.read_text(encoding="utf-8"))
    sources = build_receipt.get("sources", {})
    runtimes = build_receipt.get("runtimes", {})
    try:
        import pypdf
    except ImportError as exc:  # pragma: no cover - environment gate
        raise PackageValidationError("pypdf 6.15.0 or newer is required") from exc
    validate_pypdf_runtime(pypdf.__version__, str(runtimes.get("pypdf", "")))
    expected_bindings = {
        "acl_corpus_git_commit": str(sources.get("acl_corpus_git_commit", "")),
        "taxonomy_repository_commit": str(sources.get("taxonomy_repository_commit", "")),
        "content_sha256": str(sources.get("content_sha256", "")),
        "control_register_sha256": str(sources.get("control_register_sha256", "")),
        "acl_source_manifest_sha256": str(sources.get("acl_source_manifest_sha256", "")),
        "python_runtime": str(runtimes.get("python", "")),
        "python_executable_sha256": str(runtimes.get("python_executable_sha256", "")),
        "python_docx_runtime": str(runtimes.get("python_docx", "")),
        "pypdf_runtime": str(runtimes.get("pypdf", "")),
        "node_runtime": str(runtimes.get("node", "")),
        "node_executable_sha256": str(runtimes.get("node_executable_sha256", "")),
        "powershell_runtime": str(runtimes.get("powershell", "")),
        "powershell_executable_sha256": str(
            runtimes.get("powershell_executable_sha256", "")
        ),
        "artifact_tool_runtime": str(runtimes.get("artifact_tool", "")),
        "office_runtime": ",".join(runtimes.get("office", [])),
        "pdf_renderer_sha256": str(runtimes.get("pdf_renderer_sha256", "")),
        "docx_sanitizer_sha256": str(runtimes.get("docx_sanitizer_sha256", "")),
        "build_receipt_sha256": sha256_file(build_receipt_path),
        "render_receipt_sha256": sha256_file(render_receipt_path),
    }
    if any(not value for value in expected_bindings.values()):
        raise PackageValidationError("source/runtime/render receipt binding is blank")
    validate_manifest_bindings(manifest, expected_bindings)
    if sources.get("content_sha256") != sha256_file(content_path):
        raise PackageValidationError("content source changed after build receipt")

    text_by_file = {
        name: _artifact_text(package_dir / name)
        for name in sorted(expected_bound)
    }
    reference_text_by_file = {
        content_path.name: content_path.read_text(encoding="utf-8"),
        **{
            name: _artifact_reference_text(package_dir / name)
            for name in sorted(expected_bound)
        },
    }
    validate_restricted_workbook_references(reference_text_by_file)
    placeholders = _scan_patterns(text_by_file, PLACEHOLDER_PATTERNS)
    forbidden = scan_forbidden_claims(text_by_file)
    if placeholders:
        raise PackageValidationError(f"placeholders found: {placeholders}")
    if forbidden:
        raise PackageValidationError(f"forbidden completion claims found: {forbidden}")

    survey_url = "https://aclanthology.org/2026.findings-acl.1811/"
    required_note_urls = {
        survey_url,
        "https://github.com/HenryPengZou/Awesome-Human-Agent-Collaboration-Interaction-Systems/"
        "tree/7b3ba9deefe99172748582f6025d995ccc2a6f86",
    }
    validate_pptx_source_notes(
        package_dir / "Human_Agent_Classification_Bilingual.pptx", required_note_urls
    )
    for name in (
        "Chapter_2_Literature_Review_EN.docx",
        "Chapter_2_Literature_Review_HE.docx",
    ):
        validate_docx_hyperlinks(package_dir / name, {survey_url})
    validate_docx_rtl(
        package_dir / "Chapter_2_Literature_Review_HE.docx", minimum_bidi=20, minimum_rtl=20
    )
    for name in (
        "Chapter_2_Literature_Review_EN.pdf",
        "Chapter_2_Literature_Review_HE.pdf",
        "Supervisor_PreRead_EN.pdf",
        "Supervisor_PreRead_HE.pdf",
        "Supervisor_Tracker_and_Decisions_Bilingual.pdf",
    ):
        validate_pdf_hyperlinks(package_dir / name, {survey_url})

    validate_visible_tokens(
        {
            name: text_by_file[name]
            for name in (
                "Chapter_2_Literature_Review_EN.docx",
                "Chapter_2_Literature_Review_EN.pdf",
                "Chapter_2_Literature_Review_HE.docx",
                "Chapter_2_Literature_Review_HE.pdf",
                "Supervisor_PreRead_EN.pdf",
                "Supervisor_PreRead_HE.pdf",
                "Supervisor_Tracker_and_Decisions_Bilingual.pdf",
            )
        },
        {WORKBOOK_ALIAS},
    )

    validate_visible_tokens(
        {
            "Supervisor_Tracker_and_Decisions_Bilingual.pdf": text_by_file[
                "Supervisor_Tracker_and_Decisions_Bilingual.pdf"
            ]
        },
        {
            "Supervisor tracker and decisions",
            "מעקב והחלטות למנחים",
            "Decision recording worksheet",
            "Selected outcome",
            "Correction / read-back",
            "Approver / timestamp",
            "Owner / due date",
            "Evidence link",
            "Pending",
        },
    )

    parity_tokens = {"C2-01", "C2-ACL-01", "0/116", "0/24", "0/6"}
    validate_visible_tokens(
        {
            name: text_by_file[name]
            for name in (
                "Chapter_2_Literature_Review_EN.docx",
                "Chapter_2_Literature_Review_EN.pdf",
                "Chapter_2_Literature_Review_HE.docx",
                "Chapter_2_Literature_Review_HE.pdf",
            )
        },
        parity_tokens,
    )

    qa = manifest.get("qa", {})
    if qa.get("docx_pdf_page_parity") is not True:
        raise PackageValidationError("manifest does not record DOCX/PDF page parity")
    if qa.get("all_pages_and_slides_visually_inspected") is not True:
        raise PackageValidationError("visual inspection is not recorded complete")
    if render_receipt.get("all_pages_and_slides_visually_inspected") is not True:
        raise PackageValidationError("render receipt visual inspection is not complete")
    for key in (
        "docx_pdf_page_parity",
        "english_hebrew_parity",
        "rtl_inspected",
        "citations_and_links_inspected",
    ):
        if render_receipt.get(key) is not True or qa.get(key) is not True:
            raise PackageValidationError(f"QA receipt/manifest does not pass {key}")

    return {
        "file_count": len(REQUIRED_FILES),
        "manifest_hashes_verified": bound_count,
        "docx_pdf_page_parity": True,
        "placeholders_found": placeholders,
        "forbidden_claims_found": forbidden,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("package_dir", type=Path)
    parser.add_argument("--content", type=Path, required=True)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    try:
        report = validate_package(args.package_dir, content_path=args.content)
    except (OSError, ValueError, json.JSONDecodeError, zipfile.BadZipFile) as exc:
        print(f"AUGUST 19 SUPERVISOR PACKAGE: FAIL - {exc}")
        return 1
    if args.json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        print(
            "AUGUST 19 SUPERVISOR PACKAGE: PASS - "
            f"{report['file_count']} files, {report['manifest_hashes_verified']} hashes"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
