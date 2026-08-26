"""Fail-closed planning for copy-only proposal figure integration.

This module performs only deterministic, read-only validation.  The companion
PowerShell script is the sole Word COM boundary and consumes the JSON plan
produced here only after every source, package, figure, and QA gate passes.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import posixpath
import re
import sys
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from pathlib import Path, PurePosixPath
from typing import Any
from xml.etree import ElementTree
from zipfile import BadZipFile, ZipFile

PROJECT_ROOT = Path(__file__).resolve().parents[2]
FIGURES_ROOT = PROJECT_ROOT / "docs" / "research" / "phd-proposal" / "figures"
DEFAULT_CONTENT_MANIFEST = FIGURES_ROOT / "content.json"
DEFAULT_QA_RECEIPT = FIGURES_ROOT / "qa" / "qa-receipt.json"
DEFAULT_OUTPUT_ROOT = PROJECT_ROOT / "output"

FROZEN_SOURCE_SHA256 = "D73C840BD606695DAE50EE2E9304403D0ECB0518BCD43F05FE68B1DE166063DA"
OUTPUT_DOCX_NAME = "VEGO_AI_Doctoral_Proposal_Visual_System_20260826.docx"
OUTPUT_PDF_NAME = "VEGO_AI_Doctoral_Proposal_Visual_System_20260826.pdf"

EXPECTED_WIDTHS_EMU = (
    4_716_000,
    4_716_000,
    4_716_000,
    4_716_000,
    4_716_000,
    4_716_000,
    4_716_000,
    4_104_000,
    4_716_000,
    4_716_000,
)
EXPECTED_HEIGHTS_EMU = (
    3_108_664,
    2_694_911,
    3_677_487,
    2_540_969,
    3_259_853,
    2_920_229,
    3_639_375,
    1_610_091,
    2_963_971,
    2_920_229,
)
EXPECTED_SOURCE_CAPTIONS = (
    "Figure 1. Four readings of the same observed model difference.",
    "Figure 2. The four-agent VEGO-AI baseline, redrawn from the supplied foundation manuscript [1].",
    "Figure 3. Established research streams, the opening none of them closes, and the mapping from gaps to questions.",
    "Figure 4. The programme spine: each sub-question to its artifact, its evaluation, and its planned output.",
    "Figure 5. The Study 1 review policy: eight declared signals, a matched attention budget, six routing actions.",
    "Figure 6. The Study 2 governed-judgment record, and its lifecycle as a state machine.",
    "Figure 7. The Study 3 reuse procedure: five gates, three outcomes, and the guard on a capability-gap claim.",
    "Figure 8. Expert-review scores reported in the VEGO-AI foundation manuscript.",
    "Figure 9. The three-year plan, anchored to October 2027 – October 2030.",
    "Figure 10. Where the ACL-2026 human–agent taxonomy meets this research, and where it stops.",
)
EXPECTED_FIGURE_IDS = tuple(f"fig-{index:02d}" for index in range(1, 11))
EXPECTED_QA_FIGURE_IDS = tuple(f"fig-{index:02d}" for index in range(1, 12))
VECTOR_EXTENSIONS = {".emf", ".svg", ".wmf"}

NS = {
    "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
    "pic": "http://schemas.openxmlformats.org/drawingml/2006/picture",
    "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
    "rel": "http://schemas.openxmlformats.org/package/2006/relationships",
    "w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main",
    "wp": "http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing",
}
IMAGE_RELATIONSHIP = "http://schemas.openxmlformats.org/officeDocument/2006/relationships/image"


class IntegrationError(RuntimeError):
    """Base class for a release-blocking integration contract failure."""


class SourceDriftError(IntegrationError):
    """The source identity no longer matches the frozen SHA-256."""


class PackageContractError(IntegrationError):
    """The editable proposal package no longer has the expected structure."""


class FigureContractError(IntegrationError):
    """The replacement figure set is missing, reordered, or otherwise unsafe."""


class QaGateError(IntegrationError):
    """The replacement set is not bound to a complete passing QA receipt."""


@dataclass(frozen=True)
class FrozenSource:
    path: Path
    sha256: str
    size_bytes: int
    _data: bytes = field(repr=False)

    def to_dict(self) -> dict[str, object]:
        return {
            "filename": self.path.name,
            "sha256": self.sha256,
            "size_bytes": self.size_bytes,
        }


@dataclass(frozen=True)
class SourceDrawing:
    ordinal: int
    paragraph_index: int
    caption_paragraph_index: int
    relationship_id: str
    media_target: str
    width_emu: int
    height_emu: int
    existing_alt_text: str
    caption: str


@dataclass(frozen=True)
class SourceInspection:
    drawings: tuple[SourceDrawing, ...]
    vector_media_count: int
    alt_text_count: int


@dataclass(frozen=True)
class Replacement:
    ordinal: int
    figure_id: str
    figure_path: Path
    figure_sha256: str
    inline_shape_index: int
    relationship_id: str
    media_target: str
    width_emu: int
    source_height_emu: int
    caption_before: str
    caption_after: str
    alt_text: str

    def to_dict(self) -> dict[str, object]:
        return {
            "ordinal": self.ordinal,
            "figure_id": self.figure_id,
            "figure_path": str(self.figure_path),
            "figure_sha256": self.figure_sha256,
            "inline_shape_index": self.inline_shape_index,
            "relationship_id": self.relationship_id,
            "media_target": self.media_target,
            "width_emu": self.width_emu,
            "source_height_emu": self.source_height_emu,
            "caption_before": self.caption_before,
            "caption_after": self.caption_after,
            "alt_text": self.alt_text,
        }


@dataclass(frozen=True)
class IntegrationPlan:
    source: FrozenSource
    replacements: tuple[Replacement, ...]
    content_manifest_sha256: str
    qa_receipt_sha256: str
    output_docx: Path
    output_pdf: Path

    def to_dict(self) -> dict[str, object]:
        return {
            "source": self.source.to_dict(),
            "content_manifest_sha256": self.content_manifest_sha256,
            "qa_receipt_sha256": self.qa_receipt_sha256,
            "output_docx": str(self.output_docx),
            "output_pdf": str(self.output_pdf),
            "replacements": [replacement.to_dict() for replacement in self.replacements],
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=True, indent=2, sort_keys=True) + "\n"


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest().upper()


def _sha256_path(path: Path) -> str:
    return _sha256_bytes(path.read_bytes())


def _normalize_sha256(value: str) -> str:
    normalized = value.strip().upper()
    if re.fullmatch(r"[0-9A-F]{64}", normalized) is None:
        raise SourceDriftError("expected source SHA-256 must be exactly 64 hexadecimal characters")
    return normalized


def freeze_source(source_docx: Path, *, expected_sha256: str) -> FrozenSource:
    """Read and bind an immutable source snapshot without writing to the source."""

    path = Path(source_docx).resolve(strict=True)
    if not path.is_file() or path.suffix.lower() != ".docx":
        raise SourceDriftError(f"source is not a readable DOCX file: {path.name}")
    expected = _normalize_sha256(expected_sha256)
    try:
        data = path.read_bytes()
    except OSError as exc:
        raise SourceDriftError(
            f"source could not be read consistently: {path.name}: {exc}"
        ) from exc
    actual = _sha256_bytes(data)
    if actual != expected:
        raise SourceDriftError(
            f"source SHA-256 drift: expected {expected}, observed {actual} for {path.name}"
        )
    return FrozenSource(path=path, sha256=actual, size_bytes=len(data), _data=data)


def _package_target(target: str) -> str:
    candidate = target.replace("\\", "/")
    normalized = posixpath.normpath(posixpath.join("word", candidate))
    if (
        normalized == "word"
        or not normalized.startswith("word/")
        or normalized.startswith("word/../")
    ):
        raise PackageContractError(f"unsafe image relationship target: {target!r}")
    return normalized


def _paragraph_text(paragraph: ElementTree.Element) -> str:
    return "".join(text.text or "" for text in paragraph.findall(".//w:t", NS)).strip()


def _parse_xml(package: ZipFile, member: str) -> ElementTree.Element:
    try:
        payload = package.read(member)
    except KeyError as exc:
        raise PackageContractError(f"DOCX package is missing {member}") from exc
    try:
        return ElementTree.fromstring(payload)
    except ElementTree.ParseError as exc:
        raise PackageContractError(f"DOCX package contains malformed {member}: {exc}") from exc


def _inspect_source_bytes(data: bytes) -> SourceInspection:
    from io import BytesIO

    try:
        package = ZipFile(BytesIO(data))
    except BadZipFile as exc:
        raise PackageContractError(
            "source DOCX is not a valid Open Packaging Convention archive"
        ) from exc

    with package:
        names = set(package.namelist())
        document = _parse_xml(package, "word/document.xml")
        relationships = _parse_xml(package, "word/_rels/document.xml.rels")

        image_relationships: dict[str, str] = {}
        for relationship in relationships.findall("rel:Relationship", NS):
            if relationship.get("Type") != IMAGE_RELATIONSHIP:
                continue
            relationship_id = relationship.get("Id", "")
            target = relationship.get("Target", "")
            if relationship.get("TargetMode", "").lower() == "external":
                raise PackageContractError("all image relationships must be internal")
            if not relationship_id or not target:
                raise PackageContractError("image relationship is missing Id or Target")
            image_relationships[relationship_id] = _package_target(target)

        if len(image_relationships) != 10:
            raise PackageContractError(
                f"expected exactly 10 vector image relationships, found {len(image_relationships)}"
            )
        targets = list(image_relationships.values())
        if len(set(targets)) != 10:
            raise PackageContractError("each drawing must use a unique vector media target")
        for target in targets:
            extension = PurePosixPath(target).suffix.lower()
            if extension not in VECTOR_EXTENSIONS:
                raise PackageContractError(
                    f"expected exactly 10 vector image relationships; {target} is not vector media"
                )
            if target not in names:
                raise PackageContractError(
                    f"image relationship target is absent from package: {target}"
                )

        body = document.find("w:body", NS)
        if body is None:
            raise PackageContractError("word/document.xml has no w:body")
        all_drawings = document.findall(".//w:drawing", NS)
        inline_drawings = document.findall(".//w:drawing/wp:inline", NS)
        if len(all_drawings) != 10 or len(inline_drawings) != 10:
            raise PackageContractError(
                "expected exactly 10 inline drawings and no anchored or extra drawings; "
                f"found {len(inline_drawings)} inline of {len(all_drawings)} total"
            )

        paragraphs = body.findall("w:p", NS)
        drawing_paragraphs = [
            (index, paragraph)
            for index, paragraph in enumerate(paragraphs)
            if paragraph.findall(".//w:drawing", NS)
        ]
        if len(drawing_paragraphs) != 10:
            raise PackageContractError(
                "all 10 inline drawings must be in direct, individually addressable body paragraphs"
            )

        drawings: list[SourceDrawing] = []
        used_relationships: set[str] = set()
        alt_text_count = 0
        for ordinal, (paragraph_index, paragraph) in enumerate(drawing_paragraphs, start=1):
            nodes = paragraph.findall(".//w:drawing", NS)
            if len(nodes) != 1:
                raise PackageContractError("each figure paragraph must contain exactly one drawing")
            drawing = nodes[0]
            inline = drawing.find("wp:inline", NS)
            if inline is None:
                raise PackageContractError("every proposal figure must remain an inline drawing")
            extent = inline.find("wp:extent", NS)
            doc_properties = inline.find("wp:docPr", NS)
            blip = inline.find(".//a:blip", NS)
            if extent is None or doc_properties is None or blip is None:
                raise PackageContractError(
                    f"inline drawing {ordinal} lacks extent, document properties, or image binding"
                )
            try:
                width_emu = int(extent.get("cx", ""))
                height_emu = int(extent.get("cy", ""))
            except ValueError as exc:
                raise PackageContractError(
                    f"inline drawing {ordinal} has a non-numeric extent"
                ) from exc
            expected_width = EXPECTED_WIDTHS_EMU[ordinal - 1]
            expected_height = EXPECTED_HEIGHTS_EMU[ordinal - 1]
            if width_emu != expected_width:
                raise PackageContractError(
                    f"drawing {ordinal} has unexpected inline width {width_emu}; expected {expected_width}"
                )
            if height_emu != expected_height:
                raise PackageContractError(
                    f"drawing {ordinal} has unexpected inline height {height_emu}; expected {expected_height}"
                )

            alt_text = (doc_properties.get("descr") or "").strip()
            if alt_text:
                alt_text_count += 1
            relationship_id = blip.get(f"{{{NS['r']}}}embed", "")
            if not relationship_id or relationship_id not in image_relationships:
                raise PackageContractError(
                    f"drawing {ordinal} is not bound to one of the ten vector image relationships"
                )
            if relationship_id in used_relationships:
                raise PackageContractError("each drawing must have a unique image relationship")
            used_relationships.add(relationship_id)

            caption_index = paragraph_index + 1
            if caption_index >= len(paragraphs):
                raise PackageContractError(f"drawing {ordinal} has no following caption paragraph")
            caption = _paragraph_text(paragraphs[caption_index])
            drawings.append(
                SourceDrawing(
                    ordinal=ordinal,
                    paragraph_index=paragraph_index,
                    caption_paragraph_index=caption_index,
                    relationship_id=relationship_id,
                    media_target=image_relationships[relationship_id],
                    width_emu=width_emu,
                    height_emu=height_emu,
                    existing_alt_text=alt_text,
                    caption=caption,
                )
            )

        if alt_text_count != 10:
            raise PackageContractError(
                f"expected exactly 10 non-empty alt-text entries, found {alt_text_count}"
            )
        observed_captions = tuple(drawing.caption for drawing in drawings)
        if observed_captions != EXPECTED_SOURCE_CAPTIONS:
            raise PackageContractError(
                "captions must be Figure 1 through Figure 10 in the frozen wording and order"
            )
        if used_relationships != set(image_relationships):
            raise PackageContractError(
                "every vector image relationship must bind exactly one drawing"
            )

        return SourceInspection(
            drawings=tuple(drawings),
            vector_media_count=len(image_relationships),
            alt_text_count=alt_text_count,
        )


def inspect_source_docx(source_docx: Path) -> SourceInspection:
    """Inspect the source package read-only and reject structural drift."""

    path = Path(source_docx).resolve(strict=True)
    try:
        data = path.read_bytes()
    except OSError as exc:
        raise PackageContractError(f"source DOCX could not be read: {path.name}: {exc}") from exc
    return _inspect_source_bytes(data)


def _read_json_object(path: Path, *, label: str) -> tuple[dict[str, Any], bytes]:
    resolved = path.resolve(strict=True)
    data = resolved.read_bytes()
    try:
        payload = json.loads(data.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise IntegrationError(f"{label} is not valid UTF-8 JSON: {resolved.name}") from exc
    if not isinstance(payload, dict):
        raise IntegrationError(f"{label} root must be a JSON object: {resolved.name}")
    return payload, data


def _validated_figures(figures: Sequence[Path]) -> tuple[Path, ...]:
    if len(figures) != 10:
        raise FigureContractError(f"expected exactly 10 replacement SVGs, found {len(figures)}")
    resolved = tuple(Path(path).resolve(strict=True) for path in figures)
    expected_names = tuple(f"{figure_id}.svg" for figure_id in EXPECTED_FIGURE_IDS)
    observed_names = tuple(path.name for path in resolved)
    if observed_names != expected_names:
        raise FigureContractError("replacement paths must be ordered fig-01.svg through fig-10.svg")
    if any(not path.is_file() or path.suffix.lower() != ".svg" for path in resolved):
        raise FigureContractError("every replacement must be an existing SVG file")
    if len({path.parent for path in resolved}) != 1:
        raise FigureContractError("all replacement SVGs must come from one controlled figure root")
    return resolved


def _validate_qa_receipt(
    qa_receipt: Path,
    figures: Sequence[Path],
) -> tuple[str, Mapping[str, object]]:
    payload, data = _read_json_object(Path(qa_receipt), label="QA receipt")
    if payload.get("passed") is not True:
        raise QaGateError("overall QA receipt is not passing")
    checks = payload.get("checks")
    if not isinstance(checks, dict):
        raise QaGateError("QA receipt has no checks object")
    manual = checks.get("manual_visual_review")
    if not isinstance(manual, dict) or manual.get("status") != "pass":
        raise QaGateError("manual visual review is not passing")
    figure_results = payload.get("figures")
    if not isinstance(figure_results, dict):
        raise QaGateError("QA receipt has no per-figure results")
    for figure_id in EXPECTED_QA_FIGURE_IDS:
        result = figure_results.get(figure_id)
        if not isinstance(result, dict) or result.get("status") != "pass":
            raise QaGateError(f"QA receipt does not pass {figure_id}")
    artifacts = payload.get("artifacts")
    if not isinstance(artifacts, dict):
        raise QaGateError("QA receipt has no artifact hash manifest")
    for figure in figures:
        key = f"rendered/svg/{figure.name}"
        expected = artifacts.get(key)
        actual = _sha256_path(figure)
        if not isinstance(expected, str) or expected.upper() != actual:
            raise QaGateError(f"artifact hash mismatch for {figure.name}")
    return _sha256_bytes(data), payload


def _load_content_contract(
    content_manifest: Path,
) -> tuple[dict[str, str], dict[str, str], str]:
    payload, data = _read_json_object(Path(content_manifest), label="content manifest")
    figures = payload.get("figures")
    if not isinstance(figures, dict):
        raise FigureContractError("content manifest has no figures object")
    alt_text: dict[str, str] = {}
    for figure_id in EXPECTED_FIGURE_IDS:
        content = figures.get(figure_id)
        if not isinstance(content, dict):
            raise FigureContractError(f"content manifest is missing {figure_id}")
        value = content.get("alt_text")
        if not isinstance(value, str) or not value.strip() or "\n" in value:
            raise FigureContractError(f"{figure_id} needs one-line claim-focused alt text")
        alt_text[figure_id] = value.strip()
    figure_one = figures["fig-01"].get("caption")
    expected_figure_one = "Figure 1. Six readings of one observed model difference."
    if figure_one != expected_figure_one:
        raise FigureContractError(
            "content manifest does not preserve the authorized Figure 1 caption"
        )
    return alt_text, {"fig-01": figure_one}, _sha256_bytes(data)


def build_integration_plan(
    source_docx: Path,
    figures: Sequence[Path],
    *,
    expected_source_sha256: str = FROZEN_SOURCE_SHA256,
    content_manifest: Path = DEFAULT_CONTENT_MANIFEST,
    qa_receipt: Path = DEFAULT_QA_RECEIPT,
    output_root: Path = DEFAULT_OUTPUT_ROOT,
) -> IntegrationPlan:
    """Build a complete plan or raise before any copy or Word process is created."""

    resolved_figures = _validated_figures(figures)
    qa_receipt_sha256, _ = _validate_qa_receipt(Path(qa_receipt), resolved_figures)
    alt_text, caption_overrides, content_manifest_sha256 = _load_content_contract(
        Path(content_manifest)
    )
    source = freeze_source(Path(source_docx), expected_sha256=expected_source_sha256)
    inspection = _inspect_source_bytes(source._data)

    output = Path(output_root).resolve()
    output_docx = output / "docx" / OUTPUT_DOCX_NAME
    output_pdf = output / "pdf" / OUTPUT_PDF_NAME
    if source.path in {output_docx, output_pdf}:
        raise SourceDriftError("derived output path must never equal the frozen source path")

    replacements: list[Replacement] = []
    for figure_id, figure_path, drawing in zip(
        EXPECTED_FIGURE_IDS,
        resolved_figures,
        inspection.drawings,
        strict=True,
    ):
        caption_after = drawing.caption
        if figure_id == "fig-01":
            caption_after = caption_overrides[figure_id]
            if caption_after == drawing.caption:
                raise PackageContractError("Figure 1 caption correction is unexpectedly unchanged")
        replacements.append(
            Replacement(
                ordinal=drawing.ordinal,
                figure_id=figure_id,
                figure_path=figure_path,
                figure_sha256=_sha256_path(figure_path),
                inline_shape_index=drawing.ordinal,
                relationship_id=drawing.relationship_id,
                media_target=drawing.media_target,
                width_emu=drawing.width_emu,
                source_height_emu=drawing.height_emu,
                caption_before=drawing.caption,
                caption_after=caption_after,
                alt_text=alt_text[figure_id],
            )
        )

    return IntegrationPlan(
        source=source,
        replacements=tuple(replacements),
        content_manifest_sha256=content_manifest_sha256,
        qa_receipt_sha256=qa_receipt_sha256,
        output_docx=output_docx,
        output_pdf=output_pdf,
    )


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-docx", type=Path, required=True)
    parser.add_argument("--figure-root", type=Path, required=True)
    parser.add_argument("--content-manifest", type=Path, default=DEFAULT_CONTENT_MANIFEST)
    parser.add_argument("--qa-receipt", type=Path, default=DEFAULT_QA_RECEIPT)
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    parser.add_argument("--expected-source-sha256", default=FROZEN_SOURCE_SHA256)
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
    except (IntegrationError, FileNotFoundError, OSError) as exc:
        print(f"BLOCKED: {exc}", file=sys.stderr)
        return 2
    print(plan.to_json(), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
