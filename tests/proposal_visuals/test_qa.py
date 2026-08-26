"""Contracts for deterministic proposal-visual package production and QA."""

from __future__ import annotations

import hashlib
import subprocess
import zlib
from dataclasses import replace
from pathlib import Path

import pytest
from PIL import Image
from pypdf import PdfReader, PdfWriter
from pypdf.generic import (
    ArrayObject,
    DictionaryObject,
    EncodedStreamObject,
    NameObject,
    TextStringObject,
)
from reportlab.pdfgen.canvas import Canvas

import proposal_visuals.qa as proposal_qa
from proposal_visuals.model import Group, Rect, Scene, Text
from proposal_visuals.qa import (
    BuildConfig,
    _manual_visual_review,
    _pdf_vector_check,
    _poppler_executable,
    _render_pdf_png,
    _semantic_redundancy,
    _svg_vector_check,
    _write_a4_proof,
    all_text_fill_contrasts,
    build_all,
    default_tokens,
    run_qa,
    safe_clean_generated,
)

ROOT = Path(__file__).resolve().parents[2]
SOURCE_PDF = Path.home() / "Downloads" / "VEGO_AI_Doctoral_Proposal_Revised_20260825 (4).pdf"


def test_build_emits_complete_verified_pair_set(tmp_path: Path) -> None:
    receipt = build_all(BuildConfig(output_root=tmp_path, source_pdf_path=SOURCE_PDF))

    assert [item.figure_id for item in receipt.figures] == [f"fig-{number:02d}" for number in range(1, 12)]
    assert all(item.svg.exists() and item.pdf.exists() for item in receipt.figures)
    assert receipt.source.filename == SOURCE_PDF.name
    assert receipt.source.page_count == 31
    assert receipt.source.sha256 == hashlib.sha256(SOURCE_PDF.read_bytes()).hexdigest().upper()
    assert str(SOURCE_PDF) not in receipt.to_json()


def test_palette_contrast_floor() -> None:
    ratios = all_text_fill_contrasts(default_tokens())
    assert ratios
    assert min(ratios.values()) >= 4.5


def test_clean_rejects_a_generated_name_outside_the_figures_root(tmp_path: Path) -> None:
    figures_root = tmp_path / "figures"
    outside = tmp_path / "rendered"
    outside.mkdir(parents=True)

    with pytest.raises(ValueError, match="safe generated child"):
        safe_clean_generated(figures_root, outside)


def test_cli_requires_explicit_source_unless_verify_is_requested(tmp_path: Path) -> None:
    result = subprocess.run(
        [
            "uv",
            "run",
            "python",
            "scripts/build_proposal_visuals.py",
            "--output-root",
            str(tmp_path),
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 2
    assert "--source is required unless --verify is supplied" in result.stderr


def test_svg_vector_check_accepts_the_xml_namespace_and_embedded_font(tmp_path: Path) -> None:
    svg = tmp_path / "embedded.svg"
    svg.write_text(
        '<svg xmlns="http://www.w3.org/2000/svg" width="100pt" height="100pt" '
        'viewBox="0 0 100 100" role="img"><title>Fixture</title>'
        '<desc>Strict vector fixture.</desc><style>'
        "@font-face{font-family:'Carlito';src:url('data:font/ttf;base64,AA==') "
        "format('truetype');font-weight:400;}"
        '</style><text x="5" y="12" font-family="Carlito" font-size="8" '
        'font-weight="400" fill="#172033"><tspan x="5" dy="0">standalone</tspan>'
        "</text></svg>",
        encoding="utf-8",
    )

    assert _svg_vector_check(svg)["passed"] is True


@pytest.mark.parametrize(
    "prohibited",
    (
        '<pattern id="hatch"><line x1="0" y1="0" x2="1" y2="1"/></pattern>',
        '<image href="data:image/png;base64,AA=="/>',
        '<rect fill="url(#hatch)"/>',
    ),
)
def test_svg_vector_check_rejects_pattern_image_and_paint_server_resources(
    tmp_path: Path, prohibited: str
) -> None:
    svg = tmp_path / "paint-server.svg"
    svg.write_text(
        '<svg xmlns="http://www.w3.org/2000/svg"><style>'
        "@font-face{src:url('data:font/ttf;base64,AA==')}"
        f"</style>{prohibited}</svg>",
        encoding="utf-8",
    )

    assert _svg_vector_check(svg)["passed"] is False


@pytest.mark.parametrize(
    "document",
    (
        '<s:svg xmlns:s="http://www.w3.org/2000/svg"><s:style>'
        "@font-face{src:url('data:font/ttf;base64,AA==')}"
        '</s:style><s:pattern id="hatch"/></s:svg>',
        '<s:svg xmlns:s="http://www.w3.org/2000/svg"><s:style>'
        "@font-face{src:url('data:font/ttf;base64,AA==')}"
        '</s:style><s:image/></s:svg>',
        '<notsvg xmlns="http://www.w3.org/2000/svg"><style>'
        "@font-face{src:url('data:font/ttf;base64,AA==')}"
        "</style></notsvg>",
    ),
)
def test_svg_vector_check_rejects_prefixed_resources_and_non_svg_roots(
    tmp_path: Path, document: str
) -> None:
    svg = tmp_path / "namespace-adversary.svg"
    svg.write_text(document, encoding="utf-8")

    assert _svg_vector_check(svg)["passed"] is False


@pytest.mark.parametrize(
    "active_content",
    (
        "<style>@import 'https://example.invalid/x.css';</style>",
        "<script>fetch('https://example.invalid/x')</script>",
        '<foreignObject><h:img xmlns:h="http://www.w3.org/1999/xhtml" '
        'src="https://example.invalid/x.png"/></foreignObject>',
    ),
)
def test_svg_vector_check_rejects_active_and_foreign_content(
    tmp_path: Path, active_content: str
) -> None:
    svg = tmp_path / "active-content.svg"
    svg.write_text(
        '<svg xmlns="http://www.w3.org/2000/svg"><style>'
        "@font-face{src:url('data:font/ttf;base64,AA==')}"
        f"</style>{active_content}</svg>",
        encoding="utf-8",
    )

    assert _svg_vector_check(svg)["passed"] is False


@pytest.mark.parametrize(
    ("body", "failed_metric"),
    (
        ("<g/>" * 499, "element_count"),
        ('<line x1="0" y1="0" x2="1" y2="1" stroke="#000" stroke-width="1"/>' * 418, "attribute_count"),
        ("<g>" * 10 + "</g>" * 10, "max_depth"),
    ),
)
def test_svg_vector_check_enforces_semantic_verifier_structure_limits(
    tmp_path: Path, body: str, failed_metric: str
) -> None:
    svg = tmp_path / "oversized-structure.svg"
    svg.write_text(
        '<svg xmlns="http://www.w3.org/2000/svg"><style>'
        "@font-face{src:url('data:font/ttf;base64,AA==')}"
        f"</style>{body}</svg>",
        encoding="utf-8",
    )

    result = _svg_vector_check(svg)

    assert result["passed"] is False
    assert result["structure_within_limits"] is False
    assert result[failed_metric] > {"element_count": 500, "attribute_count": 2_500, "max_depth": 10}[
        failed_metric
    ]


def test_hatch_and_semantic_roles_are_non_colour_redundancy() -> None:
    scene = Scene(
        width=100,
        height=100,
        elements=(
            Group(
                elements=(
                    Rect(10, 10, 50, 30, hatch="diagonal", semantic_role="score-bar"),
                    Text(12, 15, "baseline", 7),
                ),
                semantic_role="figure-root",
                metadata=(("figure", "8"),),
            ),
        ),
    )

    assert _semantic_redundancy(scene)["passed"] is True


def test_a4_proof_keeps_figure_content_in_the_upper_half(tmp_path: Path) -> None:
    receipt = build_all(
        BuildConfig(output_root=tmp_path, source_pdf_path=SOURCE_PDF, figure_ids=("fig-02",))
    )
    proof = tmp_path / "proof.pdf"
    placement = _write_a4_proof(receipt.figures[0], proof)
    assert placement["orientation"] == "portrait"
    assert placement["declared_width_emu"] == 4_716_000
    assert placement["final_width_pt"] == pytest.approx(371.3386, abs=0.001)
    executable = _poppler_executable()
    assert executable is not None
    _render_pdf_png(executable, proof, tmp_path / "proof", 144)

    with Image.open(tmp_path / "proof.png") as image:
        upper_half = image.convert("L").crop((0, image.height * 3 // 10, image.width, image.height // 2))
        assert sum(pixel < 230 for pixel in upper_half.get_flattened_data()) > 1_000


def test_qa_receipt_carries_path_safe_source_identity_and_rendered_pair_hashes(tmp_path: Path) -> None:
    receipt = build_all(
        BuildConfig(output_root=tmp_path, source_pdf_path=SOURCE_PDF, figure_ids=("fig-02",))
    )

    qa_receipt = run_qa(receipt)
    payload = qa_receipt.to_dict()

    assert payload["source"] == {
        "filename": SOURCE_PDF.name,
        "sha256": hashlib.sha256(SOURCE_PDF.read_bytes()).hexdigest().upper(),
        "page_count": 31,
    }
    assert "rendered/svg/fig-02.svg" in payload["artifacts"]
    assert "rendered/pdf/fig-02.pdf" in payload["artifacts"]
    assert payload["checks"]["FINAL_SIZE_FONT"]["status"] == "pass"
    assert payload["checks"]["FINAL_SIZE_FONT"]["failed_effective_minimum_pt"] == {}
    assert str(SOURCE_PDF) not in qa_receipt.to_json()


def test_qa_fails_the_ordinary_font_gate_when_the_absolute_floor_still_passes(
    tmp_path: Path,
) -> None:
    receipt = build_all(
        BuildConfig(output_root=tmp_path, source_pdf_path=SOURCE_PDF, figure_ids=("fig-02",))
    )
    artifact = receipt.figures[0]
    scale = float(_write_a4_proof(artifact, tmp_path / "scale-proof.pdf")["scale"])
    ordinary_scene = Scene(
        width=100,
        height=100,
        elements=(
            Group(
                elements=(
                    Rect(5, 5, 80, 80, hatch="diagonal"),
                    Text(10, 10, "ordinary", 7.5 / scale),
                ),
                semantic_role="figure-root",
                metadata=(("figure", "2"),),
            ),
        ),
    )
    receipt = replace(receipt, figures=(replace(artifact, scene=ordinary_scene),))

    payload = run_qa(receipt).to_dict()

    assert payload["figures"]["fig-02"]["font_size"]["effective_minimum_pt"] == pytest.approx(7.5)
    assert payload["figures"]["fig-02"]["font_size"]["ordinary_target_status"] == "fail"
    assert payload["figures"]["fig-02"]["status"] == "fail"
    assert payload["checks"]["FINAL_SIZE_FONT"]["status"] == "fail"
    assert payload["checks"]["FINAL_SIZE_FONT"]["failed_effective_minimum_pt"] == {}
    assert payload["checks"]["FINAL_SIZE_FONT"]["failed_effective_ordinary_minimum_pt"] == {
        "fig-02": pytest.approx(7.5)
    }


def test_manual_review_marker_cannot_override_a_failed_table_row(tmp_path: Path) -> None:
    review = tmp_path / "qa" / "visual-review.md"
    review.parent.mkdir(parents=True)
    rows = "\n".join(
        f"| fig-{number:02d} | {'FAIL' if number == 3 else 'PASS'} | PASS | PASS | PASS | PASS | PASS | PASS | PASS |"
        for number in range(1, 12)
    )
    review.write_text(
        "<!-- visual-review-status: PASS -->\n"
        "| Figure | A4 144 DPI clipping/crossing | 400% 576 DPI clipping/crossing | Font-size | Ambiguity | Consistency | Greyscale | Protanopia | Deuteranopia |\n"
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- |\n"
        f"{rows}\n",
        encoding="utf-8",
    )

    result = _manual_visual_review(tmp_path)

    assert result["status"] == "fail"
    assert "fig-03" in result["detail"]


def test_manual_review_rejects_contradictory_or_additional_status_markers(tmp_path: Path) -> None:
    review = tmp_path / "qa" / "visual-review.md"
    review.parent.mkdir(parents=True)
    rows = "\n".join(
        f"| fig-{number:02d} | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS |"
        for number in range(1, 12)
    )
    review.write_text(
        "<!-- visual-review-status: PASS -->\n"
        "<!-- visual-review-status: FAIL -->\n"
        "| Figure | A4 144 DPI clipping/crossing | 400% 576 DPI clipping/crossing | Font-size | Ambiguity | Consistency | Greyscale | Protanopia | Deuteranopia |\n"
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- |\n"
        f"{rows}\n",
        encoding="utf-8",
    )

    result = _manual_visual_review(tmp_path)

    assert result["status"] == "fail"
    assert "marker" in result["detail"]


def test_first_created_review_template_has_the_same_qa_receipt_as_a_clean_rerun(tmp_path: Path) -> None:
    first = build_all(
        BuildConfig(output_root=tmp_path, source_pdf_path=SOURCE_PDF, figure_ids=("fig-02",), clean=True)
    )
    first_receipt = run_qa(first)
    second = build_all(
        BuildConfig(output_root=tmp_path, source_pdf_path=SOURCE_PDF, figure_ids=("fig-02",), clean=True)
    )
    second_receipt = run_qa(second)
    isolated_root = tmp_path.parent / f"{tmp_path.name}-isolated"
    isolated = build_all(
        BuildConfig(output_root=isolated_root, source_pdf_path=SOURCE_PDF, figure_ids=("fig-02",), clean=True)
    )
    isolated_receipt = run_qa(isolated)

    assert first_receipt.to_json() == second_receipt.to_json()
    assert first_receipt.to_json() == isolated_receipt.to_json()
    assert first_receipt.checks["manual_visual_review"] == second_receipt.checks["manual_visual_review"]


@pytest.mark.parametrize(
    "reference",
    ("relative.png", "file:///private/image.png", "https://example.test/image.png"),
)
def test_svg_vector_check_rejects_non_embedded_resources(tmp_path: Path, reference: str) -> None:
    svg = tmp_path / "external.svg"
    svg.write_text(
        '<svg xmlns="http://www.w3.org/2000/svg"><style>'
        "@font-face{src:url('data:font/ttf;base64,AA==')}"
        f".bad{{fill:url('{reference}')}}"
        "</style><rect fill=\"url(#safe)\"/></svg>",
        encoding="utf-8",
    )

    assert _svg_vector_check(svg)["passed"] is False


def test_svg_vector_check_requires_an_embedded_font(tmp_path: Path) -> None:
    svg = tmp_path / "no-font.svg"
    svg.write_text('<svg xmlns="http://www.w3.org/2000/svg"><rect/></svg>', encoding="utf-8")

    assert _svg_vector_check(svg)["passed"] is False


def test_pdf_vector_check_rejects_a_used_unembedded_builtin_font(tmp_path: Path) -> None:
    pdf = tmp_path / "helvetica.pdf"
    canvas = Canvas(str(pdf))
    canvas.setFont("Helvetica", 12)
    canvas.drawString(36, 36, "used builtin font")
    canvas.save()

    result = _pdf_vector_check(pdf)

    assert result["passed"] is False
    assert result["unembedded_used_fonts"] == ["/Helvetica"]


def test_pdf_vector_check_accepts_current_embedded_carlito_usage(tmp_path: Path) -> None:
    receipt = build_all(
        BuildConfig(output_root=tmp_path, source_pdf_path=SOURCE_PDF, figure_ids=("fig-02",))
    )

    result = _pdf_vector_check(receipt.figures[0].pdf)

    assert result["passed"] is True
    assert "/Helvetica" not in result["used_fonts"]
    assert all("Carlito" in name for name in result["used_fonts"])


def test_pdf_vector_check_ignores_uri_bytes_inside_a_compressed_content_stream(
    tmp_path: Path,
) -> None:
    receipt = build_all(
        BuildConfig(output_root=tmp_path, source_pdf_path=SOURCE_PDF, figure_ids=("fig-02",))
    )
    source = receipt.figures[0].pdf
    pdf = tmp_path / "compressed-uri-marker.pdf"
    reader = PdfReader(source)
    writer = PdfWriter()
    writer.clone_document_from_reader(reader)

    marker = EncodedStreamObject()
    marker._data = zlib.compress(b"q\n% harmless /uri marker in compressed page content\nQ\n", level=0)
    marker[NameObject("/Filter")] = NameObject("/FlateDecode")
    marker_ref = writer._add_object(marker)
    original_contents = writer.pages[0]["/Contents"]
    writer.pages[0][NameObject("/Contents")] = ArrayObject([original_contents, marker_ref])
    with pdf.open("wb") as stream:
        writer.write(stream)

    content_stream = PdfReader(pdf).pages[0]["/Contents"][-1].get_object()

    assert content_stream.get("/Filter")
    assert b"/uri" in content_stream._data.lower()

    result = _pdf_vector_check(pdf)

    assert result["passed"] is True
    assert result["external_actions"] == []
    assert result["no_external_references"] is True


@pytest.mark.parametrize("action_type", ("/URI", "/Launch", "/GoToR"))
def test_pdf_vector_check_rejects_real_external_actions(
    tmp_path: Path,
    action_type: str,
) -> None:
    receipt = build_all(
        BuildConfig(output_root=tmp_path, source_pdf_path=SOURCE_PDF, figure_ids=("fig-02",))
    )
    source = receipt.figures[0].pdf
    target = tmp_path / f"external-{action_type.removeprefix('/')}.pdf"
    reader = PdfReader(source)
    writer = PdfWriter()
    writer.clone_document_from_reader(reader)
    action = DictionaryObject({NameObject("/S"): NameObject(action_type)})
    if action_type == "/URI":
        action[NameObject("/URI")] = TextStringObject("https://example.test")
    else:
        action[NameObject("/F")] = TextStringObject("external.pdf")
    writer._root_object[NameObject("/OpenAction")] = writer._add_object(action)
    with target.open("wb") as stream:
        writer.write(stream)

    result = _pdf_vector_check(target)

    assert result["passed"] is False
    assert result["external_actions"] == [action_type]
    assert result["no_external_references"] is False


def test_ordinary_font_sizes_do_not_exempt_default_labels() -> None:
    scene = Scene(
        width=100,
        height=100,
        elements=(
            Text(10, 10, "ordinary", 7),
            Text(10, 30, "source", 5, semantic_role="provenance"),
        ),
    )

    assert "label" not in proposal_qa.ORDINARY_TEXT_EXCEPTION_ROLES
    assert proposal_qa._ordinary_font_sizes(scene) == [7]
    assert proposal_qa._ordinary_minimum_font_size(scene) == 7


def test_ordinary_minimum_rejects_a_scene_without_ordinary_text() -> None:
    scene = Scene(
        width=100,
        height=100,
        elements=(Text(10, 10, "source", 5, semantic_role="provenance"),),
    )

    with pytest.raises(ValueError, match="no ordinary text"):
        proposal_qa._ordinary_minimum_font_size(scene)


def test_qa_receipt_records_complete_path_safe_build_and_font_receipts(tmp_path: Path) -> None:
    receipt = build_all(
        BuildConfig(output_root=tmp_path, source_pdf_path=SOURCE_PDF, figure_ids=("fig-02",))
    )

    payload = run_qa(receipt).to_dict()
    build_inputs = payload["checks"]["build_inputs"]
    font_receipt = payload["checks"]["vendored_fonts"]
    runtime_versions = payload["checks"]["runtime_versions"]

    assert build_inputs["status"] == "pass"
    assert set(build_inputs["files"]) == {
        "content_manifest",
        "font_manifest",
        "project:pyproject",
        "project:uv_lock",
        "script:build_proposal_visuals",
        "module:content",
        "module:fonts",
        "module:model",
        "module:pdf_backend",
        "module:qa",
        "module:svg_backend",
        "module:tokens",
        "source_provenance",
        *(f"figure_module:fig-{number:02d}" for number in range(1, 12)),
    }
    assert all(
        not record["path"].startswith(("C:", "/")) and len(record["sha256"]) == 64
        for record in build_inputs["files"].values()
    )
    for record in build_inputs["files"].values():
        source_path = ROOT / record["path"]
        assert record["bytes"] == source_path.stat().st_size
        assert record["sha256"] == hashlib.sha256(source_path.read_bytes()).hexdigest().upper()
    assert font_receipt["status"] == "pass"
    assert font_receipt["family"] == "Carlito"
    assert set(font_receipt["verified_files"]) == {"Carlito-Regular.ttf", "Carlito-Bold.ttf", "OFL.txt"}
    assert font_receipt["license_file"] == "OFL.txt"
    assert runtime_versions["uv"].startswith("uv ")
