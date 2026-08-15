#!/usr/bin/env python3
"""Record a fail-closed visual-inspection receipt after every render was viewed."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from pypdf import PdfReader


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_text_lf(path: Path, text: str) -> None:
    """Write tracked text with canonical LF bytes on every platform."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(text)


def validate_render_index(index: dict[str, Any], render_dir: Path) -> int:
    items = index.get("items")
    if not isinstance(items, list) or not items:
        raise ValueError("render index has no items")
    seen: set[tuple[str, int]] = set()
    for row in items:
        if not isinstance(row, dict):
            raise ValueError("render index row is not an object")
        artifact = str(row.get("artifact", ""))
        sequence = int(row.get("page_or_slide", 0))
        file_name = str(row.get("render_file", ""))
        if not artifact or sequence <= 0 or not file_name:
            raise ValueError("render index row is incomplete")
        if Path(file_name).name != file_name:
            raise ValueError(f"unsafe render file: {file_name}")
        key = (artifact, sequence)
        if key in seen:
            raise ValueError(f"duplicate render item: {key}")
        seen.add(key)
        image = render_dir / file_name
        if not image.is_file():
            raise ValueError(f"render file missing: {file_name}")
        if sha256_file(image) != str(row.get("sha256", "")):
            raise ValueError(f"render hash changed: {file_name}")
    return len(items)


def validate_page_parity(office_receipt: dict[str, Any], package_dir: Path) -> dict[str, int]:
    exports = office_receipt.get("exports")
    if not isinstance(exports, list) or len(exports) != 5:
        raise ValueError("Office receipt must contain five Word exports")
    counts: dict[str, int] = {}
    for row in exports:
        target = str(row.get("target", ""))
        expected = int(row.get("pages_or_slides", 0))
        if Path(target).name != target or expected <= 0:
            raise ValueError(f"invalid Office receipt row: {target}")
        pdf = package_dir / target
        if not pdf.is_file():
            raise ValueError(f"exported PDF missing: {target}")
        actual = len(PdfReader(str(pdf)).pages)
        if actual != expected:
            raise ValueError(f"DOCX/PDF or PPTX/PDF page parity failed for {target}: {expected}!={actual}")
        counts[target] = actual
    slide_pdf = package_dir / "Human_Agent_Classification_Bilingual.pdf"
    if not slide_pdf.is_file() or len(PdfReader(str(slide_pdf)).pages) != 1:
        raise ValueError("artifact-tool slide PDF must contain exactly one page")
    counts[slide_pdf.name] = 1
    return counts


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--render-index", type=Path, required=True)
    parser.add_argument("--render-dir", type=Path, required=True)
    parser.add_argument("--office-receipt", type=Path, required=True)
    parser.add_argument("--package-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--reviewer-role", required=True)
    parser.add_argument("--confirm-visual", action="store_true")
    parser.add_argument("--confirm-en-he-parity", action="store_true")
    parser.add_argument("--confirm-rtl", action="store_true")
    parser.add_argument("--confirm-links", action="store_true")
    args = parser.parse_args()
    confirmations = {
        "all_pages_and_slides_visually_inspected": args.confirm_visual,
        "english_hebrew_parity": args.confirm_en_he_parity,
        "rtl_inspected": args.confirm_rtl,
        "citations_and_links_inspected": args.confirm_links,
    }
    if not all(confirmations.values()):
        parser.error("all four human QA confirmations are required")

    render_index = json.loads(args.render_index.read_text(encoding="utf-8"))
    office_receipt = json.loads(args.office_receipt.read_text(encoding="utf-8-sig"))
    render_count = validate_render_index(render_index, args.render_dir)
    page_counts = validate_page_parity(office_receipt, args.package_dir)
    receipt = {
        "schema_version": "vego-ai.aug19-visual-inspection-receipt.v1",
        "reviewer_role": args.reviewer_role,
        "render_index_sha256": sha256_file(args.render_index),
        "office_receipt_sha256": sha256_file(args.office_receipt),
        "render_count": render_count,
        "page_counts": page_counts,
        "docx_pdf_page_parity": True,
        **confirmations,
        "inspection_scope": "Every indexed PDF page plus the artifact-tool PPTX slide render",
        "findings": [],
    }
    write_text_lf(
        args.output,
        json.dumps(receipt, indent=2, ensure_ascii=False) + "\n",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
