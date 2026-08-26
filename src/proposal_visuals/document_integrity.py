"""Post-integration integrity gates for the derived VEGO-AI proposal.

The Word automation boundary is intentionally outside this module.  This
verifier reopens the saved DOCX and exported PDF, compares them with the
frozen source and integration plan, and emits a receipt only after every
release-blocking check passes.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import posixpath
import re
import sys
import unicodedata
from collections.abc import Sequence
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from pathlib import Path, PurePosixPath
from typing import Any
from xml.etree import ElementTree
from zipfile import BadZipFile, ZipFile

from pypdf import PdfReader

from proposal_visuals.integration import (
    DEFAULT_CONTENT_MANIFEST,
    DEFAULT_OUTPUT_ROOT,
    DEFAULT_QA_RECEIPT,
    EXPECTED_FIGURE_IDS,
    FIGURES_ROOT,
    FROZEN_SOURCE_SHA256,
    IMAGE_RELATIONSHIP,
    NS,
    IntegrationError,
    IntegrationPlan,
    build_integration_plan,
)
from proposal_visuals.renderer_runtime import (
    RendererContractError,
    RendererEvidence,
    verify_renderer_evidence,
)

EXPECTED_PDF_PAGE_COUNT = 31
EXPECTED_STATIC_TOC_ROWS = 39
EXPECTED_TABLE_CAPTIONS = 14
# Word persists inline drawing widths through a points-based COM value.  A
# sub-twentieth-point OOXML round-trip is expected; larger drift remains a
# release blocker.  1,270 EMU = 0.1 pt, which safely contains the observed
# 490-EMU (0.0386-pt) round-trip while staying well below the integration
# script's 0.5-pt pre-save guard.
WORD_INLINE_WIDTH_TOLERANCE_EMU = 1_270
DEFAULT_INTEGRATION_RECEIPT = FIGURES_ROOT / "qa" / "integration-receipt.json"

_TABLE_CAPTION = re.compile(r"^Table ([1-9][0-9]*)\.")
_DANGLING_REFERENCE_MARKERS = (
    "error! reference source not found",
    "error! bookmark not defined",
    "reference source not found",
    "bookmark not defined",
)
_SVG_NAMESPACE = "http://www.w3.org/2000/svg"
_SVG_ASCII_WSP = " \t\r\n\f"
_SVG_ASCII_WSP_CLASS = r"[ \t\r\n\f]"
_SVG_ALLOWED_TAGS = frozenset(
    {
        "g",
        "line",
        "path",
        "polygon",
        "polyline",
        "rect",
        "svg",
        "text",
        "tspan",
    }
)
_SVG_PLANNED_METADATA_TAGS = frozenset({"desc", "style", "title"})
_SVG_NUMBER_PATTERN = r"[-+]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][-+]?\d+)?"
_SVG_PATH_TOKEN = re.compile(rf"[AaCcHhLlMmQqSsTtVvZz]|{_SVG_NUMBER_PATTERN}")
_SVG_NUMBER = re.compile(rf"^{_SVG_NUMBER_PATTERN}$")
_SVG_LOCAL_URL = re.compile(
    rf"^url\({_SVG_ASCII_WSP_CLASS}*#([A-Za-z_][A-Za-z0-9_.-]*)"
    rf"{_SVG_ASCII_WSP_CLASS}*\)$"
)
_SVG_FONT_STYLE = re.compile(
    r"(?:@font-face\{font-family:'Carlito';"
    r"src:url\('data:font/ttf;base64,[A-Za-z0-9+/=]+'\) "
    r"format\('truetype'\);font-weight:(?:400|700);\})+"
)
_SVG_ALLOWED_ATTRIBUTES = {
    "g": frozenset(),
    "line": frozenset({"stroke", "stroke-width", "x1", "x2", "y1", "y2"}),
    "path": frozenset(
        {"d", "fill", "stroke", "stroke-dasharray", "stroke-width"}
    ),
    "polygon": frozenset(
        {"fill", "points", "stroke", "stroke-dasharray", "stroke-width"}
    ),
    "polyline": frozenset(
        {"fill", "points", "stroke", "stroke-dasharray", "stroke-width"}
    ),
    "rect": frozenset(
        {
            "fill",
            "height",
            "rx",
            "stroke",
            "stroke-dasharray",
            "stroke-width",
            "width",
            "x",
            "y",
        }
    ),
    "svg": frozenset({"height", "overflow", "role", "viewBox", "width"}),
    "text": frozenset(
        {"fill", "font-family", "font-size", "font-weight", "x", "y"}
    ),
    "tspan": frozenset({"dy", "x"}),
}
_SVG_MAX_BYTES = 3_000_000
_SVG_MAX_ELEMENTS = 500
_SVG_MAX_ATTRIBUTES = 2_500
_SVG_MAX_DEPTH = 10
_SVG_MAX_PATH_TOKENS = 20_000
_SVG_SEMANTIC_SCHEMA = "vego-ai-word-svg-semantic-v2"
_WORD_SVG_ROOT_ROUNDTRIP_TOLERANCE = Decimal("0.005")
_SVG_XML_DECLARATION = re.compile(
    br'^<\?xml\s+version=["\']1\.0["\']\s+encoding=["\']UTF-8["\']\s*\?>',
    re.IGNORECASE,
)
_SVG_PLANNED_LENGTH = re.compile(rf"^({_SVG_NUMBER_PATTERN})pt$")


class DocumentIntegrityError(IntegrationError):
    """A saved DOCX or exported PDF violates the controlled release contract."""


@dataclass(frozen=True)
class TocEntry:
    title: str
    page: int

    def to_dict(self) -> dict[str, object]:
        return {"title": self.title, "page": self.page}


@dataclass(frozen=True)
class IntegrationReceipt:
    passed: bool
    source_sha256: str
    output_docx_sha256: str
    output_pdf_sha256: str
    content_manifest_sha256: str
    qa_receipt_sha256: str
    checks: dict[str, dict[str, object]]

    def to_dict(self) -> dict[str, object]:
        return {
            "passed": self.passed,
            "status": "pass" if self.passed else "fail",
            "source": {"sha256": self.source_sha256},
            "outputs": {
                "docx": {"sha256": self.output_docx_sha256},
                "pdf": {"sha256": self.output_pdf_sha256},
            },
            "inputs": {
                "content_manifest_sha256": self.content_manifest_sha256,
                "qa_receipt_sha256": self.qa_receipt_sha256,
            },
            "checks": self.checks,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=True, indent=2, sort_keys=True) + "\n"


@dataclass(frozen=True)
class _DocxEvidence:
    body_text: tuple[str, ...]
    table_captions: tuple[str, ...]
    toc: tuple[TocEntry, ...]
    has_native_toc: bool
    figure_checks: tuple[dict[str, object], ...]


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest().upper()


def _sha256_path(path: Path) -> str:
    try:
        return _sha256_bytes(path.read_bytes())
    except OSError as exc:
        raise DocumentIntegrityError(f"cannot hash output {path.name}: {exc}") from exc


def _parse_xml(package: ZipFile, member: str) -> ElementTree.Element:
    try:
        data = package.read(member)
    except KeyError as exc:
        raise DocumentIntegrityError(f"DOCX package is missing {member}") from exc
    try:
        return ElementTree.fromstring(data)
    except ElementTree.ParseError as exc:
        raise DocumentIntegrityError(f"DOCX package contains malformed {member}: {exc}") from exc


def _paragraph_text(paragraph: ElementTree.Element) -> str:
    return "".join(text.text or "" for text in paragraph.findall(".//w:t", NS)).strip()


def _body_paragraph_text(document: ElementTree.Element) -> tuple[str, ...]:
    body = document.find("w:body", NS)
    if body is None:
        raise DocumentIntegrityError("word/document.xml has no w:body")
    return tuple(
        text
        for paragraph in body.findall(".//w:p", NS)
        if (text := _paragraph_text(paragraph))
    )


def _relationship_targets(
    package: ZipFile,
    relationships: ElementTree.Element,
) -> dict[str, str]:
    names = set(package.namelist())
    targets: dict[str, str] = {}
    for relationship in relationships.findall("rel:Relationship", NS):
        if relationship.get("Type") != IMAGE_RELATIONSHIP:
            continue
        relationship_id = relationship.get("Id", "")
        target = relationship.get("Target", "")
        if relationship.get("TargetMode", "").lower() == "external":
            raise DocumentIntegrityError("integrated images must not use external relationships")
        candidate = target.replace("\\", "/")
        normalized = posixpath.normpath(posixpath.join("word", candidate))
        if not relationship_id or not normalized.startswith("word/") or normalized not in names:
            raise DocumentIntegrityError(
                f"integrated image relationship is missing or unsafe: {relationship_id!r}"
            )
        targets[relationship_id] = normalized
    return targets


def _embedded_relationship_ids(drawing: ElementTree.Element) -> tuple[str, ...]:
    embed = f"{{{NS['r']}}}embed"
    return tuple(
        relationship_id
        for element in drawing.iter()
        if (relationship_id := element.get(embed))
    )


def _svg_local_name(name: str) -> str:
    """Return an element local name while requiring the SVG namespace."""

    if not name.startswith("{"):
        raise DocumentIntegrityError("SVG element is missing the SVG namespace")
    namespace, separator, local_name = name[1:].partition("}")
    if not separator or namespace != _SVG_NAMESPACE:
        raise DocumentIntegrityError("SVG contains a foreign XML namespace")
    return local_name


def _svg_attribute_name(name: str) -> str:
    """Accept only the unqualified attributes emitted by the pinned sources and Word."""

    if name.startswith("{"):
        raise DocumentIntegrityError("SVG contains a qualified attribute")
    return name


def _canonical_svg_number(value: str) -> str:
    if not _SVG_NUMBER.fullmatch(value):
        raise DocumentIntegrityError(f"SVG contains an invalid number: {value!r}")
    if len(value) > 32 or "e" in value.casefold():
        raise DocumentIntegrityError("SVG number is outside the observed decimal grammar")
    try:
        number = Decimal(value)
    except InvalidOperation as exc:
        raise DocumentIntegrityError(f"SVG contains an invalid number: {value!r}") from exc
    if not number.is_finite():
        raise DocumentIntegrityError("SVG contains a non-finite number")
    if abs(number) > Decimal("1000000000"):
        raise DocumentIntegrityError("SVG contains an out-of-range number")
    if number == 0:
        return "0"
    rendered = format(number.normalize(), "f")
    if "." in rendered:
        rendered = rendered.rstrip("0").rstrip(".")
    return rendered


def _svg_tokenize_path(value: str) -> tuple[str, ...]:
    tokens: list[str] = []
    position = 0
    for match in _SVG_PATH_TOKEN.finditer(value):
        if not re.fullmatch(r"[ \t\r\n\f,]*", value[position : match.start()]):
            raise DocumentIntegrityError("SVG path data contains unsupported syntax")
        token = match.group(0)
        tokens.append(token if token.isalpha() else _canonical_svg_number(token))
        if len(tokens) > _SVG_MAX_PATH_TOKENS:
            raise DocumentIntegrityError("SVG path exceeds the token limit")
        position = match.end()
    if not tokens or not re.fullmatch(r"[ \t\r\n\f,]*", value[position:]):
        raise DocumentIntegrityError("SVG path data contains unsupported syntax")
    return tuple(tokens)


def _canonical_svg_path(value: str) -> tuple[str, ...]:
    """Parse the exact M/L/C/Z grammar emitted by the source and Word."""

    tokens = _svg_tokenize_path(value)
    output: list[str] = []
    index = 0
    current_command: str | None = None
    first_command = True
    while index < len(tokens):
        token = tokens[index]
        if token.isalpha():
            if token not in {"M", "L", "C", "Z"}:
                raise DocumentIntegrityError(
                    f"SVG path command {token!r} is outside the observed grammar"
                )
            current_command = token
            index += 1
            if token == "Z":
                output.append("Z")
                current_command = None
                first_command = False
                continue
        if current_command is None:
            raise DocumentIntegrityError("SVG path has coordinates without a command")
        start = index
        while index < len(tokens) and not tokens[index].isalpha():
            index += 1
        values = tokens[start:index]
        if current_command == "M":
            if len(values) < 2 or len(values) % 2:
                raise DocumentIntegrityError("SVG M command requires coordinate pairs")
            if not first_command:
                raise DocumentIntegrityError("SVG path contains an unexpected extra subpath")
            output.extend(("M", *values[:2]))
            for point in range(2, len(values), 2):
                output.extend(("L", *values[point : point + 2]))
            current_command = "L"
        elif current_command == "L":
            if len(values) < 2 or len(values) % 2:
                raise DocumentIntegrityError("SVG L command requires coordinate pairs")
            for point in range(0, len(values), 2):
                output.extend(("L", *values[point : point + 2]))
        elif current_command == "C":
            if len(values) < 6 or len(values) % 6:
                raise DocumentIntegrityError("SVG C command requires groups of six values")
            for group in range(0, len(values), 6):
                output.extend(("C", *values[group : group + 6]))
        first_command = False
    if not output or output[0] != "M":
        raise DocumentIntegrityError("SVG path must begin with M")
    return tuple(output)


def _svg_point_tokens(value: str) -> tuple[str, ...]:
    tokens = _svg_tokenize_path(value)
    if any(token.isalpha() for token in tokens) or len(tokens) < 4 or len(tokens) % 2:
        raise DocumentIntegrityError("SVG points must contain complete coordinate pairs")
    return tokens


def _check_svg_url_references(value: str) -> None:
    if "url(" in value.casefold():
        raise DocumentIntegrityError("SVG paint-server URL references are prohibited")


def _svg_text(value: str | None, *, significant: bool) -> str:
    if value is None:
        return ""
    if significant:
        return value
    return value if value.strip(_SVG_ASCII_WSP) else ""


def _canonical_svg_node(
    element: ElementTree.Element,
    *,
    planned: bool,
    is_root: bool = False,
) -> list[object] | None:
    tag = _svg_local_name(element.tag)
    if tag in _SVG_PLANNED_METADATA_TAGS:
        if not planned:
            raise DocumentIntegrityError(
                f"Word-normalized SVG unexpectedly retains {tag!r} metadata"
            )
        if element.attrib or list(element):
            raise DocumentIntegrityError(f"planned SVG {tag!r} metadata is not text-only")
        if tag == "style" and not _SVG_FONT_STYLE.fullmatch(element.text or ""):
            raise DocumentIntegrityError("planned SVG font style is outside the pinned form")
        if tag in {"title", "desc"} and not (element.text or "").strip(
            _SVG_ASCII_WSP
        ):
            raise DocumentIntegrityError(f"planned SVG {tag!r} metadata is empty")
        return None
    if tag not in _SVG_ALLOWED_TAGS:
        raise DocumentIntegrityError(f"SVG contains disallowed element {tag!r}")
    if is_root and tag != "svg":
        raise DocumentIntegrityError("SVG root element is not <svg>")

    attributes: dict[str, str] = {}
    for qualified_name, raw_value in element.attrib.items():
        name = _svg_attribute_name(qualified_name)
        value = raw_value
        if name.startswith("data-"):
            if tag not in {"g", "path", "polygon", "polyline", "rect", "text"}:
                raise DocumentIntegrityError(
                    f"SVG data metadata is not allowed on {tag!r}"
                )
            if name not in {"data-role", "data-shape"} and not name.startswith(
                "data-meta-"
            ):
                raise DocumentIntegrityError(f"SVG contains unknown data attribute {name!r}")
            if planned:
                continue
            raise DocumentIntegrityError("Word-normalized SVG unexpectedly retains data metadata")
        if name not in _SVG_ALLOWED_ATTRIBUTES[tag]:
            raise DocumentIntegrityError(
                f"SVG contains unknown attribute {name!r} on {tag!r}"
            )
        if name.casefold() in {"href", "src"}:
            raise DocumentIntegrityError("SVG contains a prohibited href or src reference")
        _check_svg_url_references(value)
        if is_root and name in {"width", "height"}:
            continue
        if is_root and name == "role":
            if planned:
                continue
            raise DocumentIntegrityError("Word-normalized SVG unexpectedly retains root role")
        if name == "overflow":
            if planned or tag != "svg":
                raise DocumentIntegrityError("SVG overflow is outside Word's observed additions")
            if value != "hidden":
                raise DocumentIntegrityError("SVG overflow normalization is not 'hidden'")
            continue
        if name in attributes:
            raise DocumentIntegrityError(
                f"SVG contains a duplicate canonical attribute {name!r}"
            )
        attributes[name] = value

    canonical_tag = tag
    if tag in {"polyline", "polygon"}:
        points = attributes.pop("points", None)
        if points is None:
            raise DocumentIntegrityError(f"SVG {tag} has no points")
        path_tokens = ("M", *_svg_point_tokens(points))
        if tag == "polygon":
            path_tokens = (*path_tokens, "Z")
        canonical_tag = "path"
        attributes["d"] = " ".join(_canonical_svg_path(" ".join(path_tokens)))
    elif tag == "path":
        path_data = attributes.get("d")
        if path_data is None:
            raise DocumentIntegrityError("SVG path has no d attribute")
        attributes["d"] = " ".join(_canonical_svg_path(path_data))

    if is_root and "viewBox" not in attributes:
        raise DocumentIntegrityError("SVG root has no viewBox")

    significant_text = tag in {"text", "tspan"}
    children: list[list[object]] = []
    for child in element:
        canonical_child = _canonical_svg_node(child, planned=planned)
        if canonical_child is None:
            continue
        children.append(
            [canonical_child, _svg_text(child.tail, significant=significant_text)]
        )
    return [
        canonical_tag,
        sorted(attributes.items()),
        _svg_text(element.text, significant=significant_text),
        children,
    ]


def _svg_semantic_sha256(data: bytes, *, planned: bool) -> str:
    root = _parse_and_preflight_svg(data, planned=planned)
    canonical = _canonical_svg_node(root, planned=planned, is_root=True)
    payload = json.dumps(
        [_SVG_SEMANTIC_SCHEMA, canonical],
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=False,
    ).encode("utf-8")
    return _sha256_bytes(payload)


def verify_planned_svg_semantics(data: bytes) -> str:
    """Return a semantic hash only for a strictly safe renderer-source SVG."""

    return _svg_semantic_sha256(data, planned=True)


def _parse_and_preflight_svg(
    data: bytes, *, planned: bool
) -> ElementTree.Element:
    if len(data) > _SVG_MAX_BYTES:
        raise DocumentIntegrityError("SVG exceeds the 3,000,000-byte limit")
    if data.startswith(b"\xef\xbb\xbf") or b"\x00" in data:
        raise DocumentIntegrityError("SVG must be BOM-free UTF-8")
    try:
        data.decode("utf-8", errors="strict")
    except UnicodeDecodeError as exc:
        raise DocumentIntegrityError("SVG must be strictly encoded as UTF-8") from exc
    remainder = data
    declaration = _SVG_XML_DECLARATION.match(remainder)
    if declaration:
        remainder = remainder[declaration.end() :]
    lowered = remainder.lower()
    if (
        b"<!" in lowered
        or b"<?" in lowered
        or b"<!--" in lowered
        or b"javascript:" in lowered
        or b"data:image/" in lowered
        or b"@import" in lowered
    ):
        raise DocumentIntegrityError("SVG contains prohibited XML or active content")
    try:
        root = ElementTree.fromstring(data)
    except ElementTree.ParseError as exc:
        raise DocumentIntegrityError(f"SVG is malformed: {exc}") from exc
    if _svg_local_name(root.tag) != "svg":
        raise DocumentIntegrityError("SVG root element is not <svg>")

    element_count = 0
    attribute_count = 0
    identifiers: set[str] = set()
    references: set[str] = set()
    metadata_counts = {tag: 0 for tag in _SVG_PLANNED_METADATA_TAGS}
    stack: list[tuple[ElementTree.Element, int]] = [(root, 1)]
    while stack:
        element, depth = stack.pop()
        element_count += 1
        attribute_count += len(element.attrib)
        if element_count > _SVG_MAX_ELEMENTS:
            raise DocumentIntegrityError("SVG exceeds the 500-element limit")
        if attribute_count > _SVG_MAX_ATTRIBUTES:
            raise DocumentIntegrityError("SVG exceeds the 2,500-attribute limit")
        if depth > _SVG_MAX_DEPTH:
            raise DocumentIntegrityError("SVG exceeds the depth limit")
        tag = _svg_local_name(element.tag)
        if tag in metadata_counts:
            metadata_counts[tag] += 1
        identifier = element.get("id")
        if identifier:
            if identifier in identifiers:
                raise DocumentIntegrityError("SVG contains a duplicate id")
            identifiers.add(identifier)
        for value in element.attrib.values():
            if "url(" not in value.casefold():
                continue
            reference = _SVG_LOCAL_URL.fullmatch(value.strip(_SVG_ASCII_WSP))
            if reference is None:
                raise DocumentIntegrityError(
                    "SVG contains a non-local or malformed URL reference"
                )
            references.add(reference.group(1))
        stack.extend((child, depth + 1) for child in reversed(list(element)))
    if not references.issubset(identifiers):
        raise DocumentIntegrityError("SVG contains an unresolved local URL reference")
    if planned and metadata_counts != {"desc": 1, "style": 1, "title": 1}:
        raise DocumentIntegrityError(
            "planned SVG must contain exactly one title, description, and font style"
        )
    if not planned and any(metadata_counts.values()):
        raise DocumentIntegrityError("Word-normalized SVG retained planned metadata")
    return root


def _planned_svg_dimension(value: str | None, name: str) -> Decimal:
    match = _SVG_PLANNED_LENGTH.fullmatch(value or "")
    if match is None:
        raise DocumentIntegrityError(f"planned SVG root {name} is not an exact pt length")
    return Decimal(_canonical_svg_number(match.group(1)))


def _word_svg_dimension(value: str | None, name: str) -> Decimal:
    if value is None or _SVG_NUMBER.fullmatch(value) is None:
        raise DocumentIntegrityError(
            f"Word-normalized SVG root {name} is not an exact unitless length"
        )
    return Decimal(_canonical_svg_number(value))


def _validate_word_svg_normalization(planned_data: bytes, embedded_data: bytes) -> None:
    planned_root = _parse_and_preflight_svg(planned_data, planned=True)
    embedded_root = _parse_and_preflight_svg(embedded_data, planned=False)
    if planned_root.get("viewBox") != embedded_root.get("viewBox"):
        raise DocumentIntegrityError("Word-normalized SVG changed the viewBox")
    if planned_root.get("role") != "img" or embedded_root.get("role") is not None:
        raise DocumentIntegrityError("Word-normalized SVG role removal is outside contract")
    if planned_root.get("overflow") is not None or embedded_root.get("overflow") != "hidden":
        raise DocumentIntegrityError("Word-normalized SVG root overflow is outside contract")

    for dimension in ("width", "height"):
        planned_value = _planned_svg_dimension(planned_root.get(dimension), dimension)
        embedded_value = _word_svg_dimension(embedded_root.get(dimension), dimension)
        expected = planned_value * Decimal(4) / Decimal(3)
        if abs(embedded_value - expected) > _WORD_SVG_ROOT_ROUNDTRIP_TOLERANCE:
            raise DocumentIntegrityError(
                f"Word-normalized SVG root {dimension} is not the observed 4/3 rewrite"
            )

def _figure_evidence(
    package: ZipFile,
    document: ElementTree.Element,
    relationships: ElementTree.Element,
    plan: IntegrationPlan,
) -> tuple[dict[str, object], ...]:
    body = document.find("w:body", NS)
    if body is None:
        raise DocumentIntegrityError("word/document.xml has no w:body")
    paragraphs = body.findall("w:p", NS)
    drawing_paragraphs = [
        (index, paragraph)
        for index, paragraph in enumerate(paragraphs)
        if paragraph.findall(".//w:drawing", NS)
    ]
    if len(drawing_paragraphs) != 10:
        raise DocumentIntegrityError(
            f"integrated DOCX must contain exactly 10 direct-body figure paragraphs; "
            f"found {len(drawing_paragraphs)}"
        )
    if len(document.findall(".//w:drawing", NS)) != 10:
        raise DocumentIntegrityError("integrated DOCX contains extra or missing drawing objects")

    relationship_targets = _relationship_targets(package, relationships)
    evidence: list[dict[str, object]] = []
    for replacement, (paragraph_index, paragraph) in zip(
        plan.replacements,
        drawing_paragraphs,
        strict=True,
    ):
        figure_number = replacement.ordinal
        drawings = paragraph.findall(".//w:drawing", NS)
        if len(drawings) != 1:
            raise DocumentIntegrityError(
                f"Figure {figure_number} paragraph must contain exactly one drawing"
            )
        inline = drawings[0].find("wp:inline", NS)
        if inline is None:
            raise DocumentIntegrityError(f"Figure {figure_number} is not an inline drawing")
        extent = inline.find("wp:extent", NS)
        properties = inline.find("wp:docPr", NS)
        if extent is None or properties is None:
            raise DocumentIntegrityError(
                f"Figure {figure_number} lacks an inline extent or document properties"
            )
        try:
            width_emu = int(extent.get("cx", ""))
        except ValueError as exc:
            raise DocumentIntegrityError(
                f"Figure {figure_number} has a non-numeric inline width"
            ) from exc
        width_delta_emu = width_emu - replacement.width_emu
        if abs(width_delta_emu) > WORD_INLINE_WIDTH_TOLERANCE_EMU:
            raise DocumentIntegrityError(
                f"Figure {figure_number} width drift: expected {replacement.width_emu}, "
                f"observed {width_emu} EMU; delta {width_delta_emu} EMU exceeds "
                f"the {WORD_INLINE_WIDTH_TOLERANCE_EMU}-EMU Word round-trip tolerance"
            )
        alt_text = (properties.get("descr") or "").strip()
        if alt_text != replacement.alt_text:
            raise DocumentIntegrityError(f"Figure {figure_number} alt-text drift")

        caption_index = paragraph_index + 1
        if caption_index >= len(paragraphs):
            raise DocumentIntegrityError(f"Figure {figure_number} has no following caption")
        caption = _paragraph_text(paragraphs[caption_index])
        if caption != replacement.caption_after:
            raise DocumentIntegrityError(f"Figure {figure_number} caption drift")

        svg_bindings: list[tuple[str, bytes]] = []
        for relationship_id in _embedded_relationship_ids(drawings[0]):
            target = relationship_targets.get(relationship_id)
            if target and PurePosixPath(target).suffix.lower() == ".svg":
                if package.getinfo(target).file_size > _SVG_MAX_BYTES:
                    raise DocumentIntegrityError(
                        f"Figure {figure_number} embedded SVG exceeds the size limit"
                    )
                svg_bindings.append((target, package.read(target)))
        if len(svg_bindings) != 1:
            raise DocumentIntegrityError(
                f"Figure {figure_number} must bind exactly one embedded SVG"
            )
        try:
            planned_svg = replacement.figure_path.read_bytes()
        except OSError as exc:
            raise DocumentIntegrityError(
                f"Figure {figure_number} planned SVG cannot be reopened"
            ) from exc
        planned_hash = _sha256_bytes(planned_svg)
        if planned_hash != replacement.figure_sha256:
            raise DocumentIntegrityError(
                f"Figure {figure_number} planned SVG changed after planning"
            )
        _, embedded_svg = svg_bindings[0]
        embedded_hash = _sha256_bytes(embedded_svg)
        planned_semantic_hash = _svg_semantic_sha256(planned_svg, planned=True)
        byte_exact = embedded_hash == planned_hash
        if byte_exact:
            embedded_semantic_hash = planned_semantic_hash
        else:
            try:
                _validate_word_svg_normalization(planned_svg, embedded_svg)
                embedded_semantic_hash = _svg_semantic_sha256(
                    embedded_svg, planned=False
                )
            except DocumentIntegrityError as exc:
                raise DocumentIntegrityError(
                    f"Figure {figure_number} does not preserve the planned SVG semantics: "
                    f"{exc}"
                ) from exc
        if embedded_semantic_hash != planned_semantic_hash:
            raise DocumentIntegrityError(
                f"Figure {figure_number} does not preserve the planned SVG semantics"
            )
        evidence.append(
            {
                "figure_id": replacement.figure_id,
                "ordinal": figure_number,
                "width_emu": width_emu,
                "planned_width_emu": replacement.width_emu,
                "width_delta_emu": width_delta_emu,
                "width_tolerance_emu": WORD_INLINE_WIDTH_TOLERANCE_EMU,
                "alt_text": alt_text,
                "caption": caption,
                "svg_sha256": planned_hash,
                "planned_svg_sha256": planned_hash,
                "embedded_svg_sha256": embedded_hash,
                "planned_semantic_svg_sha256": planned_semantic_hash,
                "embedded_semantic_svg_sha256": embedded_semantic_hash,
                "svg_byte_exact": byte_exact,
            }
        )
    return tuple(evidence)


def _has_native_toc(document: ElementTree.Element) -> bool:
    instructions = [
        element.text or "" for element in document.findall(".//w:instrText", NS)
    ]
    instruction_attribute = f"{{{NS['w']}}}instr"
    instructions.extend(
        element.get(instruction_attribute, "")
        for element in document.findall(".//w:fldSimple", NS)
    )
    return any(re.search(r"(^|\s)TOC(\s|$)", instruction, re.IGNORECASE) for instruction in instructions)


def _toc_entry(paragraph: ElementTree.Element) -> TocEntry | None:
    runs = paragraph.findall("w:r", NS)
    split_index = next(
        (index for index, run in enumerate(runs) if run.find("w:tab", NS) is not None),
        None,
    )
    if split_index is None:
        return None
    title = "".join(
        text.text or ""
        for run in runs[:split_index]
        for text in run.findall(".//w:t", NS)
    ).strip()
    page_text = "".join(
        text.text or ""
        for run in runs[split_index:]
        for text in run.findall(".//w:t", NS)
    ).strip()
    if not title or not page_text.isdecimal():
        return None
    return TocEntry(title=title, page=int(page_text))


def _static_toc(document: ElementTree.Element) -> tuple[TocEntry, ...]:
    body = document.find("w:body", NS)
    if body is None:
        raise DocumentIntegrityError("word/document.xml has no w:body")
    children = list(body)
    title_index = next(
        (
            index
            for index, element in enumerate(children)
            if element.tag == f"{{{NS['w']}}}p" and _paragraph_text(element) == "Table of Contents"
        ),
        None,
    )
    if title_index is None:
        raise DocumentIntegrityError("static Table of Contents heading is missing")
    entries: list[TocEntry] = []
    page_break = f"{{{NS['w']}}}type"
    for element in children[title_index + 1 :]:
        if element.tag != f"{{{NS['w']}}}p":
            raise DocumentIntegrityError("static TOC is not a contiguous visible paragraph list")
        if any(
            node.get(page_break) == "page" for node in element.findall(".//w:br", NS)
        ):
            break
        text = _paragraph_text(element)
        if not text:
            continue
        entry = _toc_entry(element)
        if entry is None:
            raise DocumentIntegrityError(f"static TOC row is malformed: {text!r}")
        entries.append(entry)
    if len(entries) != EXPECTED_STATIC_TOC_ROWS:
        raise DocumentIntegrityError(
            f"static TOC must contain exactly {EXPECTED_STATIC_TOC_ROWS} visible rows; "
            f"found {len(entries)}"
        )
    return tuple(entries)


def _inspect_docx(path: Path, *, plan: IntegrationPlan | None = None) -> _DocxEvidence:
    try:
        package = ZipFile(path)
    except (BadZipFile, OSError) as exc:
        raise DocumentIntegrityError(f"cannot reopen DOCX {path.name}: {exc}") from exc
    with package:
        document = _parse_xml(package, "word/document.xml")
        relationships = _parse_xml(package, "word/_rels/document.xml.rels")
        body_text = _body_paragraph_text(document)
        table_captions = tuple(text for text in body_text if _TABLE_CAPTION.match(text))
        toc = _static_toc(document)
        figures = (
            _figure_evidence(package, document, relationships, plan)
            if plan is not None
            else ()
        )
        return _DocxEvidence(
            body_text=body_text,
            table_captions=table_captions,
            toc=toc,
            has_native_toc=_has_native_toc(document),
            figure_checks=figures,
        )


def _normalized_locator(value: str) -> str:
    normalized = unicodedata.normalize("NFKC", value).casefold()
    return "".join(character for character in normalized if character.isalnum())


def _resolved(value: Any) -> Any:
    return value.get_object() if hasattr(value, "get_object") else value


def _object_key(value: Any) -> tuple[object, ...]:
    if hasattr(value, "idnum"):
        return ("indirect", value.idnum, getattr(value, "generation", 0))
    return ("direct", id(_resolved(value)))


def _count_raster_image_xobjects(reader: PdfReader) -> int:
    seen: set[tuple[object, ...]] = set()

    def visit_resources(resources_value: Any) -> int:
        resources = _resolved(resources_value) if resources_value else None
        if not resources:
            return 0
        xobjects = _resolved(resources.get("/XObject", {}))
        count = 0
        for value in xobjects.values() if hasattr(xobjects, "values") else ():
            key = _object_key(value)
            if key in seen:
                continue
            seen.add(key)
            xobject = _resolved(value)
            subtype = str(xobject.get("/Subtype", ""))
            if subtype == "/Image":
                count += 1
            elif subtype == "/Form":
                count += visit_resources(xobject.get("/Resources"))
        return count

    return sum(visit_resources(page.get("/Resources")) for page in reader.pages)


def _dangling_markers(value: str) -> tuple[str, ...]:
    lowered = value.casefold()
    return tuple(marker for marker in _DANGLING_REFERENCE_MARKERS if marker in lowered)


def _body_text_hash(values: Sequence[str]) -> str:
    payload = json.dumps(list(values), ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    return _sha256_bytes(payload)


def verify_integrated_outputs(
    plan: IntegrationPlan, *, renderer_evidence: RendererEvidence
) -> IntegrationReceipt:
    """Reopen both outputs and return a passing receipt or raise without writing one."""

    try:
        renderer_checks = verify_renderer_evidence(renderer_evidence)
    except RendererContractError as exc:
        raise DocumentIntegrityError(f"renderer evidence failed: {exc}") from exc
    if not plan.output_docx.is_file() or not plan.output_pdf.is_file():
        raise DocumentIntegrityError("both derived DOCX and PDF must exist before verification")
    source = _inspect_docx(plan.source.path)
    derived = _inspect_docx(plan.output_docx, plan=plan)

    docx_dangling = _dangling_markers("\n".join(derived.body_text))
    if docx_dangling:
        raise DocumentIntegrityError(
            "derived output contains a dangling-reference marker: "
            f"{sorted(set(docx_dangling))}"
        )
    if len(source.table_captions) != EXPECTED_TABLE_CAPTIONS:
        raise DocumentIntegrityError(
            f"source must contain exactly {EXPECTED_TABLE_CAPTIONS} numbered table captions"
        )
    if derived.table_captions != source.table_captions:
        raise DocumentIntegrityError("table captions changed or reordered")
    if source.has_native_toc or derived.has_native_toc:
        raise DocumentIntegrityError(
            "the proposal TOC must remain a static visible list, not a native TOC field"
        )
    if derived.toc != source.toc:
        raise DocumentIntegrityError("static TOC changed after figure integration")

    expected_body = list(source.body_text)
    source_caption = plan.replacements[0].caption_before
    matching_caption_indexes = [
        index for index, value in enumerate(expected_body) if value == source_caption
    ]
    if len(matching_caption_indexes) != 1:
        raise DocumentIntegrityError("source Figure 1 caption is not uniquely identifiable")
    expected_body[matching_caption_indexes[0]] = plan.replacements[0].caption_after
    if tuple(expected_body) != derived.body_text:
        raise DocumentIntegrityError(
            "scholarly body text or citations changed outside the approved Figure 1 caption"
        )

    try:
        reader = PdfReader(plan.output_pdf)
    except Exception as exc:  # pypdf exposes several parse exception classes
        raise DocumentIntegrityError(f"cannot reopen derived PDF: {exc}") from exc
    if len(reader.pages) != EXPECTED_PDF_PAGE_COUNT:
        raise DocumentIntegrityError(
            f"derived PDF must contain exactly {EXPECTED_PDF_PAGE_COUNT} pages; "
            f"found {len(reader.pages)}"
        )
    pdf_page_text = tuple(page.extract_text() or "" for page in reader.pages)
    for entry in derived.toc:
        if not 1 <= entry.page <= len(pdf_page_text):
            raise DocumentIntegrityError(
                f"TOC row {entry.title!r} points outside the derived PDF"
            )
        if _normalized_locator(entry.title) not in _normalized_locator(
            pdf_page_text[entry.page - 1]
        ):
            raise DocumentIntegrityError(
                f"TOC row {entry.title!r} does not appear on declared PDF page {entry.page}"
            )
    raster_images = _count_raster_image_xobjects(reader)
    if raster_images:
        raise DocumentIntegrityError(
            f"derived PDF contains {raster_images} raster-image XObjects"
        )
    pdf_dangling = _dangling_markers("\n".join(pdf_page_text))
    if pdf_dangling:
        raise DocumentIntegrityError(
            "derived output contains a dangling-reference marker: "
            f"{sorted(set(pdf_dangling))}"
        )

    figure_checks = list(derived.figure_checks)
    return IntegrationReceipt(
        passed=True,
        source_sha256=plan.source.sha256,
        output_docx_sha256=_sha256_path(plan.output_docx),
        output_pdf_sha256=_sha256_path(plan.output_pdf),
        content_manifest_sha256=plan.content_manifest_sha256,
        qa_receipt_sha256=plan.qa_receipt_sha256,
        checks={
            "figures": {
                "passed": True,
                "count": len(figure_checks),
                "order": [item["figure_id"] for item in figure_checks],
                "widths_emu": [item["width_emu"] for item in figure_checks],
                "planned_widths_emu": [
                    item["planned_width_emu"] for item in figure_checks
                ],
                "width_deltas_emu": [
                    item["width_delta_emu"] for item in figure_checks
                ],
                "width_tolerance_emu": WORD_INLINE_WIDTH_TOLERANCE_EMU,
                "alt_text_count": len(figure_checks),
                "captions": [item["caption"] for item in figure_checks],
                "svg_hashes": [item["svg_sha256"] for item in figure_checks],
                "planned_svg_hashes": [
                    item["planned_svg_sha256"] for item in figure_checks
                ],
                "embedded_svg_hashes": [
                    item["embedded_svg_sha256"] for item in figure_checks
                ],
                "planned_semantic_svg_hashes": [
                    item["planned_semantic_svg_sha256"] for item in figure_checks
                ],
                "embedded_semantic_svg_hashes": [
                    item["embedded_semantic_svg_sha256"] for item in figure_checks
                ],
                "word_normalized_svg_count": sum(
                    not bool(item["svg_byte_exact"]) for item in figure_checks
                ),
                "semantic_schema": _SVG_SEMANTIC_SCHEMA,
                "normalization_contract": {
                    "root_size": "planned pt lengths to unitless 4/3 Word rewrite",
                    "root_size_tolerance_svg_units": str(
                        _WORD_SVG_ROOT_ROUNDTRIP_TOLERANCE
                    ),
                    "metadata": "title/desc/font-style/role/data attributes removed",
                    "geometry": "polygon/polyline to M/L/Z paths",
                    "hatch_encoding": (
                        "explicit bounded vector lines with zero pattern/image resources"
                    ),
                    "overflow": "hidden added to root only",
                    "active_content": 0,
                    "raster_content": 0,
                    "external_references": 0,
                },
            },
            "scholarly_text_parity": {
                "passed": True,
                "paragraph_count": len(derived.body_text),
                "derived_body_text_sha256": _body_text_hash(derived.body_text),
                "authorized_change": "Figure 1 caption count: Four to Six",
            },
            "table_caption_parity": {
                "passed": True,
                "count": len(derived.table_captions),
                "captions": list(derived.table_captions),
            },
            "static_toc": {
                "passed": True,
                "kind": "static-visible-list",
                "native_toc_fields": 0,
                "row_count": len(derived.toc),
                "actual_page_matches": len(derived.toc),
                "entries": [entry.to_dict() for entry in derived.toc],
            },
            "pdf": {
                "passed": True,
                "page_count": len(reader.pages),
                "raster_image_xobjects": raster_images,
                "authoritative_for_release": True,
            },
            "renderer": renderer_checks,
            "references": {
                "passed": True,
                "dangling_markers": [],
            },
        },
    )


def write_integration_receipt(receipt: IntegrationReceipt, path: Path) -> None:
    """Durably create a receipt without replacing any prior review record."""

    if not receipt.passed:
        raise DocumentIntegrityError("a nonpassing integration receipt cannot be written")
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    created = False
    try:
        with target.open("x", encoding="utf-8", newline="\n") as handle:
            created = True
            handle.write(receipt.to_json())
            handle.flush()
            os.fsync(handle.fileno())
    except Exception:
        if created and target.exists():
            target.unlink()
        raise


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-docx", type=Path, required=True)
    parser.add_argument("--figure-root", type=Path, required=True)
    parser.add_argument("--content-manifest", type=Path, default=DEFAULT_CONTENT_MANIFEST)
    parser.add_argument("--qa-receipt", type=Path, default=DEFAULT_QA_RECEIPT)
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    parser.add_argument("--integration-receipt", type=Path, default=DEFAULT_INTEGRATION_RECEIPT)
    parser.add_argument("--expected-source-sha256", default=FROZEN_SOURCE_SHA256)
    parser.add_argument("--renderer-manifest", type=Path, required=True)
    parser.add_argument("--renderer-runtime-root", type=Path, required=True)
    parser.add_argument("--renderer-profile", type=Path, required=True)
    parser.add_argument("--renderer-version-output", required=True)
    parser.add_argument("--renderer-workspace-root", type=Path, required=True)
    parser.add_argument("--word-baseline-pages", type=int, required=True)
    parser.add_argument("--word-integrated-pages", type=int, required=True)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    figures = [args.figure_root / f"{figure_id}.svg" for figure_id in EXPECTED_FIGURE_IDS]
    try:
        plan = build_integration_plan(
            args.source_docx,
            figures,
            expected_source_sha256=args.expected_source_sha256,
            content_manifest=args.content_manifest,
            qa_receipt=args.qa_receipt,
            output_root=args.output_root,
        )
        renderer_evidence = RendererEvidence(
            manifest_path=args.renderer_manifest,
            runtime_root=args.renderer_runtime_root,
            profile_registry_path=args.renderer_profile,
            version_output=args.renderer_version_output,
            word_baseline_pages=args.word_baseline_pages,
            word_integrated_pages=args.word_integrated_pages,
            workspace_root=args.renderer_workspace_root,
        )
        receipt = verify_integrated_outputs(plan, renderer_evidence=renderer_evidence)
        write_integration_receipt(receipt, args.integration_receipt)
    except (IntegrationError, FileExistsError, FileNotFoundError, OSError) as exc:
        print(f"BLOCKED: {exc}", file=sys.stderr)
        return 2
    print(receipt.to_json(), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
