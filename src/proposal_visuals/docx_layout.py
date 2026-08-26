"""Materialize narrowly scoped layout controls in a derived proposal DOCX.

The frozen source remains read-only.  This module is invoked only after Word
has saved the derived copy and before the pinned LibreOffice PDF export.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import stat
import sys
import tempfile
from collections.abc import Sequence
from dataclasses import asdict, dataclass
from io import BytesIO
from pathlib import Path
from zipfile import BadZipFile, ZipFile

from lxml import etree as ElementTree

W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
NS = {"w": W_NS}
DOCUMENT_XML = "word/document.xml"

REVIEW_SOURCE_ROLES_PREFIX = "Source roles are fixed in advance:"
REVIEW_SOURCE_ROLES_SHA256 = (
    "ABA14F67D890FC882AEC0C55E73691ED66AE38C8806E278E63A71918B92C5752"
)


class LayoutContractError(RuntimeError):
    """A derived DOCX does not satisfy the controlled layout contract."""


@dataclass(frozen=True)
class LayoutMaterializationReceipt:
    passed: bool
    docx: str
    changed: bool
    matched_paragraphs: int
    keep_lines_count: int
    sha256_before: str
    sha256_after: str

    def to_json(self) -> str:
        return json.dumps(asdict(self), ensure_ascii=True, indent=2, sort_keys=True) + "\n"


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest().upper()


def _paragraph_text(paragraph: ElementTree.Element) -> str:
    return "".join(node.text or "" for node in paragraph.findall(".//w:t", NS)).strip()


def _parse_document_xml(payload: bytes) -> ElementTree._Element:
    try:
        parser = ElementTree.XMLParser(
            resolve_entities=False,
            no_network=True,
            recover=False,
            remove_blank_text=False,
            strip_cdata=False,
            huge_tree=False,
        )
        return ElementTree.fromstring(payload, parser=parser)
    except ElementTree.XMLSyntaxError as exc:
        raise LayoutContractError(f"DOCX package contains malformed {DOCUMENT_XML}: {exc}") from exc


def _serialize_document_xml(document: ElementTree._Element, original: bytes) -> bytes:
    declaration = re.match(br"\s*<\?xml[^?]*\?>", original)
    if declaration is None:
        raise LayoutContractError(f"{DOCUMENT_XML} has no preserved XML declaration")
    root_offset = original.find(b"<w:document", declaration.end())
    if root_offset < 0 or original[declaration.end() : root_offset].strip():
        raise LayoutContractError(f"{DOCUMENT_XML} has an unexpected declaration/root boundary")
    updated = original[:root_offset] + ElementTree.tostring(
        document,
        encoding="UTF-8",
        xml_declaration=False,
        pretty_print=False,
        with_tail=False,
    )
    token = b"<w:keepLines/>"
    if original.count(token) != 0:
        raise LayoutContractError(
            f"{DOCUMENT_XML} already contains an unexpected keep-lines token outside the target"
        )
    if updated.count(token) != 1 or updated.replace(token, b"", 1) != original:
        raise LayoutContractError(
            f"{DOCUMENT_XML} changed outside the one exact keep-lines insertion"
        )
    return updated


def _insert_keep_lines(paragraph_properties: ElementTree._Element) -> None:
    # CT_PPr order places keepLines after keepNext and before pageBreakBefore. Insert
    # before the first known later property while leaving all existing nodes in
    # their original order.
    later_properties = {
        "pageBreakBefore",
        "framePr",
        "widowControl",
        "numPr",
        "suppressLineNumbers",
        "pBdr",
        "shd",
        "tabs",
        "suppressAutoHyphens",
        "kinsoku",
        "wordWrap",
        "overflowPunct",
        "topLinePunct",
        "autoSpaceDE",
        "autoSpaceDN",
        "bidi",
        "adjustRightInd",
        "snapToGrid",
        "spacing",
        "ind",
        "contextualSpacing",
        "mirrorIndents",
        "suppressOverlap",
        "jc",
        "textDirection",
        "textAlignment",
        "textboxTightWrap",
        "outlineLvl",
        "divId",
        "cnfStyle",
        "rPr",
        "sectPr",
    }
    insertion_index = len(paragraph_properties)
    for index, child in enumerate(paragraph_properties):
        if isinstance(child.tag, str) and child.tag.removeprefix(f"{{{W_NS}}}") in later_properties:
            insertion_index = index
            break
    paragraph_properties.insert(insertion_index, ElementTree.Element(f"{{{W_NS}}}keepLines"))


def _updated_document_xml(payload: bytes) -> tuple[bytes, bool, int, int]:
    document = _parse_document_xml(payload)
    body = document.find("w:body", NS)
    if body is None:
        raise LayoutContractError(f"{DOCUMENT_XML} has no direct w:body")
    matches = [
        paragraph
        for paragraph in body.findall("w:p", NS)
        if _paragraph_text(paragraph).startswith(REVIEW_SOURCE_ROLES_PREFIX)
    ]
    if len(matches) != 1:
        raise LayoutContractError(
            "expected exactly one direct-body paragraph beginning "
            f"{REVIEW_SOURCE_ROLES_PREFIX!r}; found {len(matches)}"
        )
    target_text = _paragraph_text(matches[0])
    target_sha256 = _sha256(target_text.encode("utf-8"))
    if target_sha256 != REVIEW_SOURCE_ROLES_SHA256:
        raise LayoutContractError(
            "target paragraph text SHA-256 drift: "
            f"expected {REVIEW_SOURCE_ROLES_SHA256}, observed {target_sha256}"
        )

    paragraph = matches[0]
    paragraph_properties = paragraph.find("w:pPr", NS)
    if paragraph_properties is None:
        raise LayoutContractError("target paragraph has no existing w:pPr layout container")

    controls = paragraph_properties.findall("w:keepLines", NS)
    if len(controls) > 1:
        raise LayoutContractError("target paragraph contains duplicate w:keepLines elements")
    if not controls:
        _insert_keep_lines(paragraph_properties)
        changed = True
    else:
        control = controls[0]
        if control.attrib:
            raise LayoutContractError("target w:keepLines control is not in canonical enabled form")
        changed = False

    updated = _serialize_document_xml(document, payload) if changed else payload
    count = len(paragraph_properties.findall("w:keepLines", NS))
    return updated, changed, len(matches), count


def _rewrite_document_member(path: Path, before: bytes, document_xml: bytes) -> None:
    try:
        with ZipFile(BytesIO(before)) as source:
            members = source.infolist()
            if sum(info.filename == DOCUMENT_XML for info in members) != 1:
                raise LayoutContractError(
                    f"DOCX package must contain exactly one {DOCUMENT_XML} member"
                )
            package_comment = source.comment
            payloads = [
                (info, document_xml if info.filename == DOCUMENT_XML else source.read(info))
                for info in members
            ]
    except BadZipFile as exc:
        raise LayoutContractError("derived DOCX is not a valid ZIP package") from exc

    temporary_path: Path | None = None
    try:
        descriptor, temporary_name = tempfile.mkstemp(
            prefix=f".{path.stem}-layout-", suffix=".docx", dir=path.parent
        )
        os.close(descriptor)
        temporary_path = Path(temporary_name)
        with ZipFile(temporary_path, "w") as destination:
            destination.comment = package_comment
            for info, payload in payloads:
                destination.writestr(info, payload)
        os.chmod(temporary_path, stat.S_IMODE(path.stat().st_mode))
        with temporary_path.open("r+b") as stream:
            stream.flush()
            os.fsync(stream.fileno())
        if path.read_bytes() != before:
            raise LayoutContractError("derived DOCX changed concurrently before layout publication")
        os.replace(temporary_path, path)
        temporary_path = None
    finally:
        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)


def materialize_review_keep_lines(docx: Path) -> LayoutMaterializationReceipt:
    """Keep the one review-source paragraph together in a derived DOCX."""

    try:
        path = Path(docx).resolve(strict=True)
    except FileNotFoundError as exc:
        raise LayoutContractError(f"derived DOCX does not exist: {Path(docx).name}") from exc
    if not path.is_file() or path.suffix.lower() != ".docx":
        raise LayoutContractError(f"layout target is not a DOCX file: {path.name}")

    before = path.read_bytes()
    try:
        with ZipFile(BytesIO(before)) as package:
            names = package.namelist()
            if names.count(DOCUMENT_XML) != 1:
                raise LayoutContractError(
                    f"DOCX package must contain exactly one {DOCUMENT_XML} member"
                )
            document_xml = package.read(DOCUMENT_XML)
    except BadZipFile as exc:
        raise LayoutContractError("derived DOCX is not a valid ZIP package") from exc

    updated_xml, changed, matched, keep_lines_count = _updated_document_xml(document_xml)
    if changed:
        _rewrite_document_member(path, before, updated_xml)
    after = path.read_bytes()
    return LayoutMaterializationReceipt(
        passed=True,
        docx=path.name,
        changed=changed,
        matched_paragraphs=matched,
        keep_lines_count=keep_lines_count,
        sha256_before=_sha256(before),
        sha256_after=_sha256(after),
    )


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--docx", type=Path, required=True)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        receipt = materialize_review_keep_lines(args.docx)
    except (LayoutContractError, OSError) as exc:
        print(f"BLOCKED: {exc}", file=sys.stderr)
        return 2
    print(receipt.to_json(), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
