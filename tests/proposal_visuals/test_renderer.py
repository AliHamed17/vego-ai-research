from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
from xml.etree import ElementTree

import pytest
from pypdf import PdfReader

from proposal_visuals.fonts import verify_vendored_fonts
from proposal_visuals.model import (
    HATCH_STROKE_WIDTH,
    Arrowhead,
    Cylinder,
    Diamond,
    Group,
    Parallelogram,
    Polyline,
    Rect,
    RoundedRect,
    Scene,
    SceneValidationError,
    Text,
    cylinder_geometry,
    hatch_region,
    rect_hatch_segments,
    text_lines,
    validate_scene,
)
from proposal_visuals.pdf_backend import render_pdf
from proposal_visuals.svg_backend import render_svg


@pytest.fixture
def sample_scene() -> Scene:
    return Scene(
        width=240,
        height=120,
        title="Deterministic renderer sample",
        description="A vector-only renderer contract fixture.",
        elements=(
            Group(
                semantic_role="existing",
                elements=(
                    Rect(10, 10, 70, 30, label="artifact"),
                    RoundedRect(150, 10, 70, 30, radius=6, label="process"),
                    Text(20, 30, "Carlito", 8, max_width=50),
                    Polyline(
                        points=((80, 25), (145, 25)),
                        arrowhead=Arrowhead(points=((145, 25), (137, 21), (137, 29))),
                    ),
                ),
            ),
        ),
    )


def test_scene_rejects_out_of_bounds_and_tiny_text() -> None:
    with pytest.raises(SceneValidationError, match="outside artboard"):
        validate_scene(Scene(width=100, height=100, elements=(Text(-1, 20, "bad", 8),)))
    with pytest.raises(SceneValidationError, match="below 7 pt"):
        validate_scene(Scene(width=100, height=100, elements=(Text(10, 20, "bad", 6.9),)))


def test_scene_rejects_stroked_shape_that_would_clip_at_artboard_edge() -> None:
    scene = Scene(width=100, height=100, elements=(Rect(0, 10, 30, 20, line_width=2),))

    with pytest.raises(SceneValidationError, match="outside artboard"):
        validate_scene(scene)


def test_scene_requires_explicit_arrowhead_polygon() -> None:
    scene = Scene(width=100, height=100, elements=(Polyline(points=((10, 10), (90, 10))),))

    with pytest.raises(SceneValidationError, match="explicit arrowhead"):
        validate_scene(scene)


@pytest.mark.parametrize("weight", ["regular", "bold"])
def test_measured_carlito_wrapping_rejects_wide_unbreakable_words(weight: str) -> None:
    wide = Text(10, 10, "WWWW", 8, max_width=20, weight=weight)
    narrow = Text(10, 10, "iiiiiiii", 8, max_width=20, weight=weight)

    assert text_lines(narrow) == ("iiiiiiii",)
    with pytest.raises(SceneValidationError, match="does not fit"):
        validate_scene(Scene(width=100, height=100, elements=(wide,)))


def test_shared_cylinder_geometry_stays_inside_declared_shape_and_hatches_both_backends(
    tmp_path: Path,
) -> None:
    cylinder = Cylinder(20, 20, 80, 40, hatch="diagonal")
    geometry = cylinder_geometry(cylinder)

    assert all(20 <= x <= 100 and 20 <= y <= 60 for x, y in geometry.all_points())
    with pytest.raises(SceneValidationError, match="outside artboard"):
        validate_scene(Scene(width=100, height=100, elements=(Cylinder(0, 20, 80, 40),)))

    scene = Scene(width=140, height=100, elements=(cylinder,))
    svg, pdf = tmp_path / "cylinder.svg", tmp_path / "cylinder.pdf"
    render_svg(scene, svg)
    render_pdf(scene, pdf)

    svg_text = svg.read_text(encoding="utf-8")
    assert 'data-shape="cylinder"' in svg_text
    assert "<pattern" not in svg_text
    assert "<image" not in svg_text
    assert "url(#" not in svg_text
    pdf_content = PdfReader(pdf).pages[0].get_contents().get_data()
    assert pdf_content.count(b" l") > 10


def test_plain_rect_hatch_uses_explicit_bounded_vector_segments(
    tmp_path: Path,
) -> None:
    rectangle = Rect(20, 20, 80, 30, fill="#FFFFFF", hatch="diagonal")
    segments = rect_hatch_segments(rectangle)

    assert len(segments) > 10
    assert all(
        20 <= x <= 100 and 20 <= y <= 50
        for segment in segments
        for x, y in segment
    )

    scene = Scene(width=140, height=90, elements=(rectangle,))
    svg, pdf = tmp_path / "rect-hatch.svg", tmp_path / "rect-hatch.pdf"
    render_svg(scene, svg)
    render_pdf(scene, pdf)

    svg_text = svg.read_text(encoding="utf-8")
    assert "<pattern" not in svg_text
    assert "<image" not in svg_text
    assert "url(#" not in svg_text
    assert svg_text.count("<line ") == len(segments)
    reader = PdfReader(pdf)
    assert not reader.pages[0].images
    assert reader.pages[0].get_contents().get_data().count(b" l") >= len(segments)


def test_hatch_stroke_stays_inside_shape_and_artboard_with_thin_outline(
    tmp_path: Path,
) -> None:
    rectangle = Rect(0.05, 0.05, 50, 50, line_width=0.1, hatch="diagonal")
    scene = Scene(width=60, height=60, elements=(rectangle,))
    region = hatch_region(rectangle)

    half_hatch_stroke = HATCH_STROKE_WIDTH / 2
    assert region.x - half_hatch_stroke == pytest.approx(rectangle.x)
    assert region.y - half_hatch_stroke == pytest.approx(rectangle.y)
    assert region.x + region.width + half_hatch_stroke == pytest.approx(
        rectangle.x + rectangle.width
    )
    assert region.y + region.height + half_hatch_stroke == pytest.approx(
        rectangle.y + rectangle.height
    )

    svg, pdf = tmp_path / "thin-outline.svg", tmp_path / "thin-outline.pdf"
    render_svg(scene, svg)
    render_pdf(scene, pdf)

    assert _all_svg_line_strokes_within_artboard(svg, width=60, height=60)
    assert not PdfReader(pdf).pages[0].images


def _all_svg_line_strokes_within_artboard(path: Path, *, width: float, height: float) -> bool:
    root = ElementTree.parse(path).getroot()
    for element in root.iter():
        if element.tag.rsplit("}", 1)[-1] != "line":
            continue
        half_stroke = float(element.attrib["stroke-width"]) / 2
        for coordinate, limit in (("x1", width), ("x2", width), ("y1", height), ("y2", height)):
            value = float(element.attrib[coordinate])
            if not half_stroke <= value <= limit - half_stroke:
                return False
    return True


def test_scene_rejects_hatched_shape_without_stroke_safe_interior() -> None:
    scene = Scene(width=10, height=10, elements=(Rect(1, 1, 0.5, 0.5, hatch="diagonal"),))

    with pytest.raises(SceneValidationError, match="no safe interior"):
        validate_scene(scene)


@pytest.mark.parametrize(
    "shape",
    (
        RoundedRect(20, 20, 80, 40, radius=6, hatch="diagonal"),
        Cylinder(20, 20, 80, 40, hatch="diagonal"),
        Diamond(20, 20, 80, 40, hatch="diagonal"),
        Parallelogram(20, 20, 80, 40, skew=8, hatch="diagonal"),
    ),
)
def test_non_rect_hatches_use_explicit_lines_within_conservative_shape_region(
    tmp_path: Path, shape: Rect
) -> None:
    region = hatch_region(shape)
    segments = rect_hatch_segments(region)
    assert segments
    assert all(
        region.x <= x <= region.x + region.width
        and region.y <= y <= region.y + region.height
        for segment in segments
        for x, y in segment
    )

    scene = Scene(width=140, height=100, elements=(shape,))
    svg = tmp_path / f"{type(shape).__name__}.svg"
    pdf = tmp_path / f"{type(shape).__name__}.pdf"
    render_svg(scene, svg)
    render_pdf(scene, pdf)

    svg_text = svg.read_text(encoding="utf-8")
    assert "<pattern" not in svg_text
    assert "<image" not in svg_text
    assert "url(#" not in svg_text
    assert svg_text.count("<line ") == len(segments)
    reader = PdfReader(pdf)
    assert not reader.pages[0].images
    assert reader.pages[0].get_contents().get_data().count(b" l") >= len(segments)


@pytest.mark.parametrize(
    "element",
    [
        Rect(10, 10, 30, 20, fill="url(https://example.test/pattern)"),
        Rect(10, 10, 30, 20, stroke="url(#unapproved)"),
        Text(10, 10, "safe", 8, fill="red"),
        Polyline(
            points=((20, 20), (70, 20)),
            arrowhead=Arrowhead(points=((70, 20), (64, 16), (64, 24))),
            stroke="url(http://example.test/line)",
        ),
    ],
)
def test_scene_rejects_external_or_non_token_paint_values(element: object) -> None:
    with pytest.raises(SceneValidationError, match="paint"):
        validate_scene(Scene(width=100, height=100, elements=(element,)))  # type: ignore[arg-type]


def test_scene_rejects_non_positive_polyline_line_width() -> None:
    line = Polyline(
        points=((20, 20), (70, 20)),
        arrowhead=Arrowhead(points=((70, 20), (64, 16), (64, 24))),
        line_width=0,
    )

    with pytest.raises(SceneValidationError, match="line width"):
        validate_scene(Scene(width=100, height=100, elements=(line,)))


@pytest.mark.parametrize(
    "scene",
    [
        Scene(width=math.nan, height=100, elements=()),
        Scene(width=100, height=-math.inf, elements=()),
        Scene(width=100, height=100, elements=(Text(math.nan, 10, "text", 8),)),
        Scene(width=100, height=100, elements=(Text(10, math.inf, "text", 8),)),
        Scene(width=100, height=100, elements=(Text(10, 10, "text", math.nan),)),
        Scene(width=100, height=100, elements=(Text(10, 10, "text", 8, max_width=math.inf),)),
        Scene(width=100, height=100, elements=(Text(10, 10, "text", 8, leading=math.nan),)),
        Scene(width=100, height=100, elements=(Rect(math.nan, 10, 20, 20),)),
        Scene(width=100, height=100, elements=(Rect(10, math.inf, 20, 20),)),
        Scene(width=100, height=100, elements=(Rect(10, 10, math.nan, 20),)),
        Scene(width=100, height=100, elements=(Rect(10, 10, 20, math.inf),)),
        Scene(width=100, height=100, elements=(Rect(10, 10, 20, 20, line_width=math.nan),)),
        Scene(width=100, height=100, elements=(RoundedRect(10, 10, 20, 20, radius=math.inf),)),
        Scene(width=100, height=100, elements=(Parallelogram(10, 10, 20, 20, skew=math.nan),)),
        Scene(
            width=100,
            height=100,
            elements=(
                Polyline(
                    points=((math.nan, 20), (70, 20)),
                    arrowhead=Arrowhead(points=((70, 20), (64, 16), (64, 24))),
                ),
            ),
        ),
        Scene(
            width=100,
            height=100,
            elements=(
                Polyline(
                    points=((20, 20), (70, 20)),
                    arrowhead=Arrowhead(points=((70, math.inf), (64, 16), (64, 24))),
                ),
            ),
        ),
        Scene(
            width=100,
            height=100,
            elements=(
                Polyline(
                    points=((20, 20), (70, 20)),
                    arrowhead=Arrowhead(points=((70, math.inf), (64, 16), (64, 24))),
                    line_width=math.nan,
                ),
            ),
        ),
    ],
)
def test_nonfinite_geometry_fails_closed_before_svg_or_pdf_output(tmp_path: Path, scene: Scene) -> None:
    with pytest.raises(SceneValidationError, match="finite"):
        validate_scene(scene)

    svg, pdf = tmp_path / "invalid.svg", tmp_path / "invalid.pdf"
    with pytest.raises(SceneValidationError, match="finite"):
        render_svg(scene, svg)
    with pytest.raises(SceneValidationError, match="finite"):
        render_pdf(scene, pdf)
    assert not svg.exists()
    assert not pdf.exists()


def test_vendored_font_manifest_verifies_every_file_and_exact_license_receipt() -> None:
    receipt = verify_vendored_fonts()

    assert set(receipt) == {"Carlito-Regular.ttf", "Carlito-Bold.ttf", "OFL.txt"}
    assert receipt["OFL.txt"]["bytes"] == 4424
    assert receipt["OFL.txt"]["sha256"] == "58402F82A7C332A700294988FE7554FBB0A63A8D27CCC1EE3BBC640311990A00"
    assert all(str(item["url"]).startswith("https://raw.githubusercontent.com/google/fonts/") for item in receipt.values())


def test_group_metadata_is_preserved_in_svg_and_pdf_document_metadata(tmp_path: Path) -> None:
    scene = Scene(
        width=100,
        height=80,
        elements=(Group(elements=(Text(10, 10, "metadata", 8),), metadata=(("phase", "review"),)),),
    )
    svg, pdf = tmp_path / "metadata.svg", tmp_path / "metadata.pdf"
    render_svg(scene, svg)
    render_pdf(scene, pdf)

    assert 'data-meta-phase="review"' in svg.read_text(encoding="utf-8")
    keywords = PdfReader(pdf).metadata.get("/Keywords")
    assert keywords is not None
    assert json.loads(keywords) == {"groups": [{"metadata": {"phase": "review"}, "role": "group"}]}


def test_svg_is_standalone_vector(tmp_path: Path, sample_scene: Scene) -> None:
    target = tmp_path / "sample.svg"
    render_svg(sample_scene, target)
    text = target.read_text(encoding="utf-8")

    assert "<image" not in text
    assert text.count("http://") == 1
    assert "https://" not in text
    assert "data:font/ttf;base64," in text
    assert 'font-family="Carlito"' in text
    assert 'marker-end=' not in text


def test_svg_text_uses_unitless_viewbox_font_sizes(tmp_path: Path) -> None:
    """CSS pt units scale 4/3 in SVG consumers and make measured text overflow."""
    target = tmp_path / "unitless-font-size.svg"
    render_svg(Scene(width=100, height=60, elements=(Text(10, 10, "fit", 8),)), target)

    root = ElementTree.fromstring(target.read_text(encoding="utf-8"))
    text_element = root.find("{http://www.w3.org/2000/svg}text")
    assert text_element is not None
    assert text_element.attrib["font-size"] == "8"
    assert not text_element.attrib["font-size"].endswith(("pt", "px", "em", "rem"))


def test_svg_root_is_namespace_qualified_standalone_svg(tmp_path: Path) -> None:
    target = tmp_path / "namespace.svg"
    render_svg(Scene(width=60, height=40, elements=(Text(8, 8, "svg", 7),)), target)

    text = target.read_text(encoding="utf-8")
    assert text.count('xmlns="http://www.w3.org/2000/svg"') == 1
    assert ElementTree.fromstring(text).tag == "{http://www.w3.org/2000/svg}svg"


def test_renderers_are_deterministic_and_pdf_has_only_vector_content(
    tmp_path: Path, sample_scene: Scene
) -> None:
    svg_a, svg_b = tmp_path / "a.svg", tmp_path / "b.svg"
    pdf_a, pdf_b = tmp_path / "a.pdf", tmp_path / "b.pdf"

    render_svg(sample_scene, svg_a)
    render_svg(sample_scene, svg_b)
    render_pdf(sample_scene, pdf_a)
    render_pdf(sample_scene, pdf_b)

    assert hashlib.sha256(svg_a.read_bytes()).digest() == hashlib.sha256(svg_b.read_bytes()).digest()
    assert hashlib.sha256(pdf_a.read_bytes()).digest() == hashlib.sha256(pdf_b.read_bytes()).digest()

    reader = PdfReader(pdf_a)
    resources = reader.pages[0]["/Resources"]
    assert "/XObject" not in resources or "/Image" not in resources.get("/XObject", {})
    font_names = {str(font.get_object().get("/BaseFont", "")) for font in resources["/Font"].values()}
    assert any("Carlito" in name for name in font_names)
