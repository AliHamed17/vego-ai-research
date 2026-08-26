from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

import pytest
from PIL import Image
from reportlab.pdfgen import canvas

from proposal_visuals.document_integrity import (
    EXPECTED_PDF_PAGE_COUNT,
    EXPECTED_STATIC_TOC_ROWS,
    WORD_INLINE_WIDTH_TOLERANCE_EMU,
    DocumentIntegrityError,
    verify_integrated_outputs,
    write_integration_receipt,
)
from proposal_visuals.integration import EXPECTED_SOURCE_CAPTIONS, build_integration_plan
from proposal_visuals.renderer_runtime import RendererEvidence

WIDTHS_EMU = (
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
HEIGHTS_EMU = (
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
SOURCE_CAPTIONS = EXPECTED_SOURCE_CAPTIONS
TOC_ENTRIES = (
    ("Abstract", 2),
    ("1. Introduction and Motivation", 4),
    ("1.1 Domain modeling, variability, and model assessment", 4),
    ("1.2 Agentic AI for modeling and assessment", 5),
    ("1.3 Human involvement in agentic AI", 6),
    ("1.3.1 Coverage of an existing human-agent taxonomy", 7),
    ("1.4 Selective human intervention", 7),
    ("1.5 Capturing and governing expert judgment", 8),
    ("1.6 Reusing judgment across contexts", 9),
    ("1.7 A motivating example", 9),
    ("1.8 Synthesis and residual research gaps", 10),
    ("2. Research Objectives, Questions, and Expected Contributions", 12),
    ("2.1 Research objectives", 12),
    ("2.2 Research questions", 12),
    ("2.3 Scenario instantiation", 13),
    ("2.4 Expected contributions", 13),
    ("2.5 Testable propositions", 14),
    ("3. Research Methodology and Expected Artifacts", 14),
    ("3.1 Design-science programme", 14),
    ("3.2 The literature review as a research activity", 15),
    ("3.3 Study 1 - selective intervention", 16),
    ("3.4 Study 2 - governed judgment", 17),
    ("3.5 Study 3 - controlled reuse and capability-gap classification", 18),
    ("3.6 Integrated evaluation", 20),
    ("3.7 Ethics, privacy, and leakage controls", 21),
    ("4. Progress and Preliminary Results", 21),
    ("4.1 Reported baseline evidence from the foundation manuscript", 21),
    ("4.2 Literature-review progress", 22),
    ("4.3 Current doctoral-project evidence and open gates", 22),
    ("5. Research Work Plan", 23),
    ("6. Challenges, Pitfalls, and Threats to Validity", 24),
    ("6.1 Threats to validity", 25),
    ("7. References", 25),
    ("Appendix A. Classification of the ACL-2026 human-agent taxonomy", 27),
    ("A.1 Branch-level disposition", 28),
    ("A.2 Dimension-level disposition", 28),
    ("A.3 Concepts the taxonomy cannot express", 29),
    ("A.4 Screening the survey corpus", 29),
    ("Appendix B. Scholarly status note", 30),
)
TABLE_CAPTIONS = tuple(
    f"Table {index}. Frozen scholarly table caption {index}." for index in range(1, 15)
)


def _profile_xml() -> str:
    return """<?xml version="1.0" encoding="UTF-8"?>
<oor:items xmlns:oor="http://openoffice.org/2001/registry">
  <item oor:path="/org.openoffice.Office.Common/Font/Substitution/FontPairs">
    <node oor:name="_0" oor:op="replace">
      <prop oor:name="Always" oor:op="fuse"><value>true</value></prop>
      <prop oor:name="ReplaceFont" oor:op="fuse"><value>Calibri</value></prop>
      <prop oor:name="OnScreenOnly" oor:op="fuse"><value>false</value></prop>
      <prop oor:name="SubstituteFont" oor:op="fuse"><value>Carlito</value></prop>
    </node>
    <node oor:name="_1" oor:op="replace">
      <prop oor:name="Always" oor:op="fuse"><value>true</value></prop>
      <prop oor:name="ReplaceFont" oor:op="fuse"><value>Cambria</value></prop>
      <prop oor:name="OnScreenOnly" oor:op="fuse"><value>false</value></prop>
      <prop oor:name="SubstituteFont" oor:op="fuse"><value>Caladea</value></prop>
    </node>
  </item>
  <item oor:path="/org.openoffice.Office.Common/Font/Substitution">
    <prop oor:name="Replacement" oor:op="fuse"><value>true</value></prop>
  </item>
</oor:items>
"""


def _write_renderer_evidence(root: Path) -> RendererEvidence:
    runtime = root / "renderer"
    executable = runtime / "program" / "soffice.com"
    executable.parent.mkdir(parents=True)
    executable.write_bytes(b"test-renderer")
    (runtime / "program" / "soffice.bin").write_bytes(b"test-engine")
    registry = runtime / "share" / "registry" / "writer.xcd"
    registry.parent.mkdir(parents=True)
    registry.write_bytes(b"test-writer-filter-registry")
    font_root = runtime / "share" / "fonts" / "truetype"
    font_root.mkdir(parents=True)
    font_rows = []
    for index, name in enumerate(
        (
            "Caladea-Bold.ttf",
            "Caladea-BoldItalic.ttf",
            "Caladea-Italic.ttf",
            "Caladea-Regular.ttf",
            "Carlito-Bold.ttf",
            "Carlito-BoldItalic.ttf",
            "Carlito-Italic.ttf",
            "Carlito-Regular.ttf",
        ),
        start=1,
    ):
        path = font_root / name
        path.write_bytes(f"font-{index}".encode())
        font_rows.append(
            {
                "relative_path": f"share/fonts/truetype/{name}",
                "sha256": hashlib.sha256(path.read_bytes()).hexdigest().upper(),
            }
        )
    engine_candidates = {
        path for path in (runtime / "program").iterdir() if path.is_file()
    }
    for relative in (
        Path("program/services"),
        Path("share/registry"),
        Path("share/fonts/truetype"),
    ):
        scope_root = runtime / relative
        if scope_root.is_dir():
            engine_candidates.update(
                path for path in scope_root.rglob("*") if path.is_file()
            )
    engine_rows = []
    for path in engine_candidates:
        payload = path.read_bytes()
        engine_rows.append(
            (
                path.relative_to(runtime).as_posix(),
                len(payload),
                hashlib.sha256(payload).hexdigest().upper(),
            )
        )
    engine_rows.sort(key=lambda item: item[0].encode())
    engine_digest = hashlib.sha256()
    for relative, size, file_hash in engine_rows:
        engine_digest.update(f"{relative}\0{size}\0{file_hash}\n".encode())
    engine_contract = {
        "algorithm": "sha256-path-size-content-v1",
        "scope": [
            "program/* (top-level files only)",
            "program/services/** (all files)",
            "share/registry/** (all files)",
            "share/fonts/truetype/** (all files)",
        ],
        "file_count": len(engine_rows),
        "total_bytes": sum(row[1] for row in engine_rows),
        "tree_sha256": engine_digest.hexdigest().upper(),
    }
    manifest = root / "renderer-manifest.json"
    manifest.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "renderer": {
                    "name": "LibreOffice",
                    "version": "24.2.7.2",
                    "build_id": "test-build",
                    "engine_contract": engine_contract,
                    "license": "MPL-2.0 / LGPL-3.0-or-later",
                    "archive": {
                        "url": "https://example.invalid/lo.msi",
                        "bytes": 1,
                        "sha256": "A" * 64,
                    },
                    "relative_executable": "program/soffice.com",
                    "executable_sha256": hashlib.sha256(executable.read_bytes())
                    .hexdigest()
                    .upper(),
                    "version_output": "LibreOffice 24.2.7.2 test-build",
                    "pdf_export_filter": "writer_pdf_Export",
                },
                "font_sources": [],
                "fonts": font_rows,
                "profile": {
                    "replacement_enabled": True,
                    "substitutions": [
                        {"replace": "Calibri", "with": "Carlito", "always": True},
                        {"replace": "Cambria", "with": "Caladea", "always": True},
                    ],
                },
            }
        ),
        encoding="utf-8",
    )
    profile = root / "profile" / "user" / "registrymodifications.xcu"
    profile.parent.mkdir(parents=True)
    profile.write_text(_profile_xml(), encoding="utf-8")
    return RendererEvidence(
        manifest_path=manifest,
        runtime_root=runtime,
        profile_registry_path=profile,
        version_output="LibreOffice 24.2.7.2 test-build",
        word_baseline_pages=33,
        word_integrated_pages=33,
        workspace_root=root,
    )


def _xml_escape(value: str) -> str:
    return (
        value.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def _text_paragraph(value: str) -> str:
    return f"<w:p><w:r><w:t>{_xml_escape(value)}</w:t></w:r></w:p>"


def _toc_paragraph(title: str, page: int) -> str:
    return (
        "<w:p><w:pPr><w:tabs><w:tab w:val=\"right\" w:leader=\"dot\" "
        "w:pos=\"9411\"/></w:tabs></w:pPr>"
        f"<w:r><w:t>{_xml_escape(title)}</w:t></w:r>"
        f"<w:r><w:tab/><w:t>{page}</w:t></w:r></w:p>"
    )


def _drawing_paragraph(index: int, *, derived: bool, width: int, alt_text: str) -> str:
    if derived:
        binding = (
            f'<a:blip r:embed="rIdP{index}"><a:extLst><a:ext uri="svg">'
            f'<asvg:svgBlip r:embed="rIdS{index}"/>'
            "</a:ext></a:extLst></a:blip>"
        )
    else:
        binding = f'<a:blip r:embed="rId{index}"/>'
    return (
        "<w:p><w:r><w:drawing><wp:inline>"
        f'<wp:extent cx="{width}" cy="{HEIGHTS_EMU[index - 1]}"/>'
        f'<wp:docPr id="{index + 20}" name="Figure {index}" descr="{_xml_escape(alt_text)}"/>'
        "<a:graphic><a:graphicData><pic:pic><pic:blipFill>"
        f"{binding}"
        "</pic:blipFill></pic:pic></a:graphicData></a:graphic>"
        "</wp:inline></w:drawing></w:r></w:p>"
    )


def _document_xml(
    *,
    derived: bool,
    mutation: str | None = None,
    first_width_delta_emu: int = 0,
) -> str:
    toc_entries = list(TOC_ENTRIES)
    if mutation == "toc-snapshot":
        toc_entries[0] = (toc_entries[0][0], 3)
    paragraphs = [
        _text_paragraph("Doctoral Research Proposal"),
        _text_paragraph("Table of Contents"),
        *(_toc_paragraph(title, page) for title, page in toc_entries),
        '<w:p><w:r><w:br w:type="page"/></w:r></w:p>',
        *(_text_paragraph(title) for title, _ in TOC_ENTRIES),
        _text_paragraph(
            "The governed argument and its citations [1], [20], and [62] are frozen scholarly text."
        ),
    ]
    if mutation == "scholarly-text":
        paragraphs[-1] = _text_paragraph(
            "The governed argument and its citations [1], [20], and [61] are frozen scholarly text."
        )

    captions = list(SOURCE_CAPTIONS)
    if derived:
        captions[0] = "Figure 1. Six readings of one observed model difference."
    if mutation == "caption-two":
        captions[1] += " Changed."

    for index in range(1, 11):
        alt = f"Claim-focused replacement alt {index}." if derived else f"Existing alt {index}"
        if mutation == "alt-text" and index == 1:
            alt = "Wrong alt text."
        width = WIDTHS_EMU[index - 1]
        if index == 1:
            width += first_width_delta_emu
        if mutation == "width" and index == 1:
            width -= 12_700
        paragraphs.extend(
            (
                _drawing_paragraph(index, derived=derived, width=width, alt_text=alt),
                _text_paragraph(captions[index - 1]),
            )
        )

    table_captions = list(TABLE_CAPTIONS)
    if mutation == "table-order":
        table_captions[0], table_captions[1] = table_captions[1], table_captions[0]
    for index, caption in enumerate(table_captions, start=1):
        paragraphs.append(_text_paragraph(caption))
        paragraphs.append(
            "<w:tbl><w:tr><w:tc>"
            f"{_text_paragraph(f'Frozen table {index} cell [20].')}"
            "</w:tc></w:tr></w:tbl>"
        )
    if mutation == "dangling-docx":
        paragraphs.append(_text_paragraph("Error! Reference source not found."))
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" '
        'xmlns:wp="http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing" '
        'xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" '
        'xmlns:asvg="http://schemas.microsoft.com/office/drawing/2016/SVG/main" '
        'xmlns:pic="http://schemas.openxmlformats.org/drawingml/2006/picture" '
        'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">'
        f"<w:body>{''.join(paragraphs)}<w:sectPr/></w:body></w:document>"
    )


def _relationships_xml(*, derived: bool, swap_first_two: bool = False) -> str:
    relationships: list[str] = []
    for index in range(1, 11):
        if derived:
            svg_index = 3 - index if swap_first_two and index in {1, 2} else index
            relationships.extend(
                (
                    "<Relationship "
                    f'Id="rIdP{index}" '
                    'Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/image" '
                    f'Target="media/fallback{index}.png"/>',
                    "<Relationship "
                    f'Id="rIdS{index}" '
                    'Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/image" '
                    f'Target="media/fig-{svg_index:02d}.svg"/>',
                )
            )
        else:
            relationships.append(
                "<Relationship "
                f'Id="rId{index}" '
                'Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/image" '
                f'Target="media/image{index}.emf"/>'
            )
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        f"{''.join(relationships)}</Relationships>"
    )


def _write_docx(
    path: Path,
    *,
    figures: list[Path],
    derived: bool,
    mutation: str | None = None,
    first_width_delta_emu: int = 0,
) -> str:
    with ZipFile(path, "w", compression=ZIP_DEFLATED) as package:
        document_xml = _document_xml(
            derived=derived,
            mutation=mutation,
            first_width_delta_emu=first_width_delta_emu,
        )
        if mutation == "second-svg-binding":
            document_xml = document_xml.replace(
                '<asvg:svgBlip r:embed="rIdS1"/>',
                '<asvg:svgBlip r:embed="rIdS1"/>'
                '<asvg:svgBlip r:embed="rIdS2"/>',
                1,
            )
        package.writestr(
            "word/document.xml",
            document_xml,
        )
        package.writestr(
            "word/_rels/document.xml.rels",
            _relationships_xml(derived=derived, swap_first_two=mutation == "figure-order"),
        )
        for index, figure in enumerate(figures, start=1):
            if derived:
                package.writestr(f"word/media/fallback{index}.png", b"fallback")
                svg_bytes = figure.read_bytes()
                if (
                    mutation == "word-normalized-svg"
                    or (mutation or "").startswith("svg-")
                ) and index == 1:
                    svg_bytes = _word_normalized_test_svg(index, mutation=mutation)
                package.writestr(f"word/media/fig-{index:02d}.svg", svg_bytes)
            else:
                package.writestr(f"word/media/image{index}.emf", f"vector-{index}".encode())
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def _write_figures(root: Path) -> list[Path]:
    root.mkdir()
    figures = []
    for index in range(1, 11):
        figure = root / f"fig-{index:02d}.svg"
        figure.write_text(
            '<svg xmlns="http://www.w3.org/2000/svg" width="960pt" height="630pt" '
            'viewBox="0 0 960 630" role="img">'
            '<title>Fixture</title><desc>Fixture description.</desc>'
            "<style>@font-face{font-family:'Carlito';"
            "src:url('data:font/ttf;base64,AA==') format('truetype');font-weight:400;}</style>"
            '<line x1="0" y1="0" x2="6" y2="6" stroke="#5F6B7A" stroke-width="0.7"/>'
            '<polyline points="0,0 10,10 20,0" fill="none" data-role="flow"/>'
            '<polygon points="20,0 18,2 22,2" fill="#000" data-role="arrowhead"/>'
            f'<text x="1" y="12" font-family="Test" data-role="label"><tspan>{index}</tspan>'
            '</text></svg>',
            encoding="utf-8",
        )
        figures.append(figure)
    return figures


def _word_normalized_test_svg(index: int, *, mutation: str | None = None) -> bytes:
    svg = (
        '<svg xmlns="http://www.w3.org/2000/svg" width="1280" height="840" '
        'viewBox="0 0 960 630" overflow="hidden">'
        '<line x1="0" y1="0" x2="6" y2="6" stroke="#5F6B7A" stroke-width="0.7"/>'
        '<path d="M0 0 10 10 20 0" fill="none"/>'
        '<path d="M20 0 18 2 22 2Z" fill="#000"/>'
        f'<text x="1" y="12" font-family="Test"><tspan>{index}</tspan></text></svg>'
    )
    replacements = {
        "svg-semantic-change": (f">{index}</tspan>", ">changed</tspan>"),
        "svg-active-script": ("</svg>", "<script>alert(1)</script></svg>"),
        "svg-data-image": (
            "</svg>",
            '<image href="data:image/png;base64,AA=="/></svg>',
        ),
        "svg-external-href": (
            "</svg>",
            '<image href="https://example.invalid/pixel.png"/></svg>',
        ),
        "svg-event-attribute": ("<text x=", '<text onclick="alert(1)" x='),
        "svg-viewbox-change": ('viewBox="0 0 960 630"', 'viewBox="0 0 961 630"'),
        "svg-root-size-change": ('width="1280"', 'width="1279"'),
        "svg-root-size-boundary": ('width="1280"', 'width="1280.005"'),
        "svg-root-size-outside": ('width="1280"', 'width="1280.005001"'),
        "svg-overflow-change": ('overflow="hidden"', 'overflow="visible"'),
        "svg-hatch-line-change": ('x2="6" y2="6"', 'x2="7" y2="6"'),
        "svg-pattern-introduced": (
            "</svg>",
            '<pattern id="unsafe"><line x1="0" y1="0" x2="1" y2="1"/></pattern></svg>',
        ),
        "svg-polygon-open": ('22 2Z"', '22 2"'),
        "svg-path-nbsp": ("M20 0", "M20\u00a00"),
        "svg-path-exponent": ("M20 0", "M1e-999999 0"),
        "svg-text-whitespace": (f">{index}</tspan>", f"> {index}</tspan>"),
        "svg-foreign-element": (
            "</svg>",
            '<foreign:node xmlns:foreign="https://example.invalid/ns"/></svg>',
        ),
        "svg-processing-instruction": (
            "<svg ",
            '<?xml-stylesheet href="https://example.invalid/x.css"?><svg ',
        ),
        "svg-doctype": ("<svg ", "<!DOCTYPE svg><svg "),
        "svg-missing-namespace": (
            ' xmlns="http://www.w3.org/2000/svg"',
            "",
        ),
    }
    if mutation in replacements:
        old, new = replacements[mutation]
        svg = svg.replace(old, new, 1)
    elif mutation in {"svg-shadow-fill", "svg-shadow-path"}:
        svg = svg.replace(
            'xmlns="http://www.w3.org/2000/svg"',
            'xmlns="http://www.w3.org/2000/svg" '
            'xmlns:s="http://www.w3.org/2000/svg"',
            1,
        )
        if mutation == "svg-shadow-fill":
            svg = svg.replace(
                'fill="#000"',
                'fill="#FF0000" s:fill="#000"',
                1,
            )
        else:
            svg = svg.replace(
                'd="M20 0 18 2 22 2Z"',
                'd="M20 0 18 2 23 2Z" s:d="M20 0 18 2 22 2Z"',
                1,
            )
    if mutation == "svg-utf16-processing-instruction":
        return (
            '<?xml version="1.0" encoding="UTF-16"?>'
            '<?xml-stylesheet href="https://example.invalid/x.css"?>'
            f"{svg}"
        ).encode("utf-16")
    if mutation == "svg-utf32-doctype":
        return (
            '<?xml version="1.0" encoding="UTF-32"?>'
            f"<!DOCTYPE svg>{svg}"
        ).encode("utf-32")
    return svg.encode()


def _write_manifest(path: Path) -> None:
    path.write_text(
        json.dumps(
            {
                "figures": {
                    f"fig-{index:02d}": {
                        "caption": (
                            "Figure 1. Six readings of one observed model difference."
                            if index == 1
                            else SOURCE_CAPTIONS[index - 1]
                        ),
                        "alt_text": f"Claim-focused replacement alt {index}.",
                    }
                    for index in range(1, 11)
                }
            }
        ),
        encoding="utf-8",
    )


def _write_qa_receipt(path: Path, figures: list[Path]) -> None:
    path.write_text(
        json.dumps(
            {
                "passed": True,
                "checks": {"manual_visual_review": {"status": "pass"}},
                "figures": {f"fig-{index:02d}": {"status": "pass"} for index in range(1, 12)},
                "artifacts": {
                    f"rendered/svg/{figure.name}": hashlib.sha256(figure.read_bytes())
                    .hexdigest()
                    .upper()
                    for figure in figures
                },
            }
        ),
        encoding="utf-8",
    )


def _write_pdf(
    path: Path,
    *,
    page_count: int = EXPECTED_PDF_PAGE_COUNT,
    omit_toc_title: str | None = None,
    dangling: bool = False,
    raster: bool = False,
) -> None:
    pdf = canvas.Canvas(str(path), pageCompression=0)
    titles_by_page: dict[int, list[str]] = {}
    for title, page in TOC_ENTRIES:
        titles_by_page.setdefault(page, []).append(title)
    raster_path = path.with_suffix(".png")
    if raster:
        Image.new("RGB", (1, 1), (255, 0, 0)).save(raster_path)
    for page in range(1, page_count + 1):
        pdf.setFont("Helvetica", 9)
        y = 800
        for title in titles_by_page.get(page, []):
            if title != omit_toc_title:
                pdf.drawString(36, y, title)
                y -= 14
        if dangling and page == 1:
            pdf.drawString(36, y, "Error! Reference source not found.")
        if raster and page == 1:
            pdf.drawImage(str(raster_path), 36, 36, width=10, height=10)
        pdf.showPage()
    pdf.save()


@pytest.fixture
def document_package(tmp_path: Path) -> dict[str, object]:
    figures = _write_figures(tmp_path / "figures")
    source = tmp_path / "source.docx"
    source_hash = _write_docx(source, figures=figures, derived=False)
    manifest = tmp_path / "content.json"
    _write_manifest(manifest)
    qa = tmp_path / "qa.json"
    _write_qa_receipt(qa, figures)
    output_root = tmp_path / "output"
    plan = build_integration_plan(
        source,
        figures,
        expected_source_sha256=source_hash,
        content_manifest=manifest,
        qa_receipt=qa,
        output_root=output_root,
    )
    plan.output_docx.parent.mkdir(parents=True)
    plan.output_pdf.parent.mkdir(parents=True)
    _write_docx(plan.output_docx, figures=figures, derived=True)
    _write_pdf(plan.output_pdf)
    renderer_evidence = _write_renderer_evidence(tmp_path)
    return {
        "figures": figures,
        "manifest": manifest,
        "qa": qa,
        "source": source,
        "source_hash": source_hash,
        "plan": plan,
        "renderer_evidence": renderer_evidence,
    }


def test_post_integration_verifier_proves_the_complete_release_contract(
    document_package: dict[str, object],
) -> None:
    plan = document_package["plan"]
    receipt = verify_integrated_outputs(
        plan, renderer_evidence=document_package["renderer_evidence"]
    )

    assert receipt.passed is True
    assert receipt.checks["figures"]["count"] == 10
    assert receipt.checks["figures"]["widths_emu"] == list(WIDTHS_EMU)
    assert receipt.checks["figures"]["planned_widths_emu"] == list(WIDTHS_EMU)
    assert receipt.checks["figures"]["width_deltas_emu"] == [0] * 10
    assert WORD_INLINE_WIDTH_TOLERANCE_EMU == 1_270
    assert receipt.checks["figures"]["width_tolerance_emu"] == 1_270
    assert receipt.checks["scholarly_text_parity"]["passed"] is True
    assert receipt.checks["table_caption_parity"]["count"] == 14
    assert receipt.checks["static_toc"]["kind"] == "static-visible-list"
    assert receipt.checks["static_toc"]["row_count"] == EXPECTED_STATIC_TOC_ROWS == 39
    assert receipt.checks["static_toc"]["actual_page_matches"] == 39
    assert receipt.checks["pdf"]["page_count"] == EXPECTED_PDF_PAGE_COUNT == 31
    assert receipt.checks["pdf"]["authoritative_for_release"] is True
    assert receipt.checks["pdf"]["raster_image_xobjects"] == 0
    assert receipt.checks["renderer"]["renderer"]["version"] == "24.2.7.2"
    assert receipt.checks["renderer"]["word_pagination"]["baseline_pages"] == 33
    assert receipt.checks["renderer"]["word_pagination"]["integrated_pages"] == 33


@pytest.mark.parametrize("width_delta_emu", [-490, -1_270, 1_270])
def test_post_integration_verifier_accepts_bounded_word_width_rounding(
    document_package: dict[str, object],
    width_delta_emu: int,
) -> None:
    plan = document_package["plan"]
    _write_docx(
        plan.output_docx,
        figures=document_package["figures"],
        derived=True,
        first_width_delta_emu=width_delta_emu,
    )

    receipt = verify_integrated_outputs(
        plan, renderer_evidence=document_package["renderer_evidence"]
    )

    figures = receipt.checks["figures"]
    assert WORD_INLINE_WIDTH_TOLERANCE_EMU == 1_270
    assert figures["planned_widths_emu"] == list(WIDTHS_EMU)
    assert figures["widths_emu"][0] == WIDTHS_EMU[0] + width_delta_emu
    assert figures["width_deltas_emu"] == [width_delta_emu, *([0] * 9)]
    assert figures["width_tolerance_emu"] == 1_270


def test_post_integration_verifier_accepts_word_normalized_svg_semantics(
    document_package: dict[str, object],
) -> None:
    plan = document_package["plan"]
    _write_docx(
        plan.output_docx,
        figures=document_package["figures"],
        derived=True,
        mutation="word-normalized-svg",
    )

    receipt = verify_integrated_outputs(
        plan, renderer_evidence=document_package["renderer_evidence"]
    )

    figures = receipt.checks["figures"]
    assert figures["word_normalized_svg_count"] == 1
    assert figures["semantic_schema"] == "vego-ai-word-svg-semantic-v2"
    assert figures["normalization_contract"] == {
        "root_size": "planned pt lengths to unitless 4/3 Word rewrite",
        "root_size_tolerance_svg_units": "0.005",
        "metadata": "title/desc/font-style/role/data attributes removed",
        "geometry": "polygon/polyline to M/L/Z paths",
        "hatch_encoding": "explicit bounded vector lines with zero pattern/image resources",
        "overflow": "hidden added to root only",
        "active_content": 0,
        "raster_content": 0,
        "external_references": 0,
    }
    assert len(figures["planned_svg_hashes"]) == 10
    assert len(figures["embedded_svg_hashes"]) == 10
    assert len(figures["planned_semantic_svg_hashes"]) == 10
    assert len(figures["embedded_semantic_svg_hashes"]) == 10
    expected_planned_hashes = [
        hashlib.sha256(path.read_bytes()).hexdigest().upper()
        for path in document_package["figures"]
    ]
    assert figures["planned_svg_hashes"] == expected_planned_hashes
    assert figures["embedded_svg_hashes"][0] == hashlib.sha256(
        _word_normalized_test_svg(1, mutation="word-normalized-svg")
    ).hexdigest().upper()
    assert figures["embedded_svg_hashes"][1:] == expected_planned_hashes[1:]
    assert figures["planned_svg_hashes"][0] != figures["embedded_svg_hashes"][0]
    assert figures["planned_semantic_svg_hashes"] == figures["embedded_semantic_svg_hashes"]


def test_post_integration_verifier_blocks_semantic_svg_change(
    document_package: dict[str, object],
) -> None:
    plan = document_package["plan"]
    _write_docx(
        plan.output_docx,
        figures=document_package["figures"],
        derived=True,
        mutation="svg-semantic-change",
    )

    with pytest.raises(
        DocumentIntegrityError,
        match="does not preserve the planned SVG semantics",
    ):
        verify_integrated_outputs(
            plan, renderer_evidence=document_package["renderer_evidence"]
        )


def test_post_integration_verifier_accepts_word_root_size_rounding_boundary(
    document_package: dict[str, object],
) -> None:
    plan = document_package["plan"]
    _write_docx(
        plan.output_docx,
        figures=document_package["figures"],
        derived=True,
        mutation="svg-root-size-boundary",
    )

    receipt = verify_integrated_outputs(
        plan, renderer_evidence=document_package["renderer_evidence"]
    )

    assert receipt.checks["figures"]["word_normalized_svg_count"] == 1
    assert receipt.checks["figures"]["normalization_contract"][
        "root_size_tolerance_svg_units"
    ] == "0.005"


@pytest.mark.parametrize(
    "mutation",
    [
        "svg-active-script",
        "svg-data-image",
        "svg-doctype",
        "svg-event-attribute",
        "svg-external-href",
        "svg-foreign-element",
        "svg-missing-namespace",
        "svg-overflow-change",
        "svg-path-nbsp",
        "svg-path-exponent",
        "svg-polygon-open",
        "svg-processing-instruction",
        "svg-root-size-change",
        "svg-root-size-outside",
        "svg-shadow-fill",
        "svg-shadow-path",
        "svg-text-whitespace",
        "svg-hatch-line-change",
        "svg-pattern-introduced",
        "svg-utf16-processing-instruction",
        "svg-utf32-doctype",
        "svg-viewbox-change",
    ],
)
def test_post_integration_verifier_blocks_unsafe_or_changed_word_svg(
    document_package: dict[str, object],
    mutation: str,
) -> None:
    plan = document_package["plan"]
    _write_docx(
        plan.output_docx,
        figures=document_package["figures"],
        derived=True,
        mutation=mutation,
    )

    with pytest.raises(
        DocumentIntegrityError,
        match="does not preserve the planned SVG semantics",
    ):
        verify_integrated_outputs(
            plan, renderer_evidence=document_package["renderer_evidence"]
        )


def test_post_integration_verifier_requires_exactly_one_svg_binding(
    document_package: dict[str, object],
) -> None:
    plan = document_package["plan"]
    _write_docx(
        plan.output_docx,
        figures=document_package["figures"],
        derived=True,
        mutation="second-svg-binding",
    )

    with pytest.raises(
        DocumentIntegrityError,
        match="must bind exactly one embedded SVG",
    ):
        verify_integrated_outputs(
            plan, renderer_evidence=document_package["renderer_evidence"]
        )


@pytest.mark.parametrize("width_delta_emu", [-1_271, 1_271])
def test_post_integration_verifier_blocks_width_just_outside_word_tolerance(
    document_package: dict[str, object],
    width_delta_emu: int,
) -> None:
    plan = document_package["plan"]
    _write_docx(
        plan.output_docx,
        figures=document_package["figures"],
        derived=True,
        first_width_delta_emu=width_delta_emu,
    )

    with pytest.raises(
        DocumentIntegrityError,
        match=r"width drift:.*1270-EMU Word round-trip tolerance",
    ):
        verify_integrated_outputs(
            plan, renderer_evidence=document_package["renderer_evidence"]
        )


@pytest.mark.parametrize(
    ("mutation", "message"),
    [
        ("figure-order", "Figure 1 does not preserve the planned SVG semantics"),
        ("width", "Figure 1 width drift"),
        ("alt-text", "Figure 1 alt-text drift"),
        ("caption-two", "Figure 2 caption drift"),
        ("scholarly-text", "scholarly body text or citations changed"),
        ("table-order", "table captions changed or reordered"),
        ("toc-snapshot", "static TOC changed"),
        ("dangling-docx", "dangling-reference marker"),
    ],
)
def test_docx_mutations_are_release_blocking(
    document_package: dict[str, object],
    mutation: str,
    message: str,
) -> None:
    plan = document_package["plan"]
    _write_docx(
        plan.output_docx,
        figures=document_package["figures"],
        derived=True,
        mutation=mutation,
    )

    with pytest.raises(DocumentIntegrityError, match=message):
        verify_integrated_outputs(
            plan, renderer_evidence=document_package["renderer_evidence"]
        )


@pytest.mark.parametrize(
    ("pdf_options", "message"),
    [
        ({"page_count": 30}, "exactly 31 pages"),
        ({"raster": True}, "raster-image XObjects"),
        ({"omit_toc_title": TOC_ENTRIES[10][0]}, "does not appear on declared PDF page"),
        ({"dangling": True}, "dangling-reference marker"),
    ],
)
def test_pdf_mutations_are_release_blocking(
    document_package: dict[str, object],
    pdf_options: dict[str, object],
    message: str,
) -> None:
    plan = document_package["plan"]
    _write_pdf(plan.output_pdf, **pdf_options)

    with pytest.raises(DocumentIntegrityError, match=message):
        verify_integrated_outputs(
            plan, renderer_evidence=document_package["renderer_evidence"]
        )


def test_receipt_is_written_only_after_verification_and_never_overwritten(
    document_package: dict[str, object],
    tmp_path: Path,
) -> None:
    plan = document_package["plan"]
    receipt_path = tmp_path / "integration-receipt.json"
    receipt = verify_integrated_outputs(
        plan, renderer_evidence=document_package["renderer_evidence"]
    )

    write_integration_receipt(receipt, receipt_path)

    payload = json.loads(receipt_path.read_text(encoding="utf-8"))
    assert payload["passed"] is True
    before = receipt_path.read_bytes()
    with pytest.raises(FileExistsError):
        write_integration_receipt(receipt, receipt_path)
    assert receipt_path.read_bytes() == before

    receipt_path.unlink()
    _write_pdf(plan.output_pdf, page_count=30)
    with pytest.raises(DocumentIntegrityError):
        verify_integrated_outputs(
            plan, renderer_evidence=document_package["renderer_evidence"]
        )
    assert not receipt_path.exists()


def test_powershell_exposes_no_caller_asserted_post_verify_recovery_mode(
    document_package: dict[str, object],
    tmp_path: Path,
) -> None:
    pwsh = shutil.which("pwsh")
    if pwsh is None:
        pytest.skip("PowerShell 7 is unavailable")
    plan = document_package["plan"]
    receipt_path = tmp_path / "integration-receipt.json"
    script = Path(__file__).resolve().parents[2] / "scripts" / "integrate_proposal_visuals.ps1"
    parameter_block = script.read_text(encoding="utf-8").split("Set-StrictMode", 1)[0]
    for removed_parameter in (
        "$PostVerifyOnly",
        "$LibreOfficeProfileRegistry",
        "$LibreOfficeVersionOutput",
        "$RendererWorkspaceRoot",
        "$WordBaselinePages",
        "$WordIntegratedPages",
    ):
        assert removed_parameter not in parameter_block
    command = [
        pwsh,
        "-NoProfile",
        "-NonInteractive",
        "-File",
        str(script),
        "-SourceDocx",
        str(document_package["source"]),
        "-OutputRoot",
        str(plan.output_docx.parents[1]),
        "-FigureRoot",
        str(document_package["figures"][0].parent),
        "-ContentManifest",
        str(document_package["manifest"]),
        "-QaReceipt",
        str(document_package["qa"]),
        "-IntegrationReceipt",
        str(receipt_path),
        "-ExpectedSourceSha256",
        str(document_package["source_hash"]),
        "-PythonExecutable",
        sys.executable,
        "-PostVerifyOnly",
    ]

    completed = subprocess.run(command, capture_output=True, text=True, check=False)

    assert completed.returncode != 0
    assert "parameter cannot be found" in completed.stderr.casefold()
    assert not receipt_path.exists()
