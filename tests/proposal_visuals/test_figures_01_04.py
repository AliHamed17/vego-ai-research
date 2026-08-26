"""Semantic contracts for the first four proposal figures."""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

from proposal_visuals.content import load_content
from proposal_visuals.model import (
    Cylinder,
    Diamond,
    Group,
    Parallelogram,
    Polyline,
    Rect,
    RoundedRect,
    Scene,
    Text,
    text_bounds,
    validate_scene,
)
from proposal_visuals.qa import A4_HEIGHT_PT, DECLARED_WIDTH_EMU, EMU_PER_POINT, PROOF_MARGIN_PT
from proposal_visuals.tokens import VisualTokens

ROOT = Path(__file__).resolve().parents[2]
CONTENT = load_content(ROOT / "docs" / "research" / "phd-proposal" / "figures" / "content.json")
TOKENS = VisualTokens.proposal()

FROZEN_INLINE_HEIGHT_EMU = {
    "fig-01": 3_108_664,
    "fig-02": 2_694_911,
    "fig-03": 3_677_487,
    "fig-04": 2_540_969,
}


def _builder(filename: str):
    source = ROOT / "docs" / "research" / "phd-proposal" / "figures" / "sources" / filename
    spec = importlib.util.spec_from_file_location(filename.removesuffix(".py"), source)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.build


def _groups(scene: Scene) -> tuple[Group, ...]:
    def visit(elements: tuple[object, ...]) -> tuple[Group, ...]:
        found: list[Group] = []
        for element in elements:
            if isinstance(element, Group):
                found.append(element)
                found.extend(visit(element.elements))
        return tuple(found)

    return visit(scene.elements)


def _metadata(group: Group) -> dict[str, str]:
    return dict(group.metadata)


def _texts(scene: Scene) -> tuple[str, ...]:
    values: list[str] = []

    def visit(elements: tuple[object, ...]) -> None:
        for element in elements:
            if isinstance(element, Text):
                values.append(element.value)
            elif isinstance(element, Group):
                visit(element.elements)

    visit(scene.elements)
    return tuple(values)


def _text_elements(scene: Scene) -> tuple[Text, ...]:
    def visit(elements: tuple[object, ...]) -> tuple[Text, ...]:
        found: list[Text] = []
        for element in elements:
            if isinstance(element, Text):
                found.append(element)
            elif isinstance(element, Group):
                found.extend(visit(element.elements))
        return tuple(found)

    return visit(scene.elements)


def _elements(group: Group) -> tuple[object, ...]:
    found: list[object] = []
    for element in group.elements:
        found.append(element)
        if isinstance(element, Group):
            found.extend(_elements(element))
    return tuple(found)


def _segment_intersects_shape(
    start: tuple[float, float], end: tuple[float, float], shape: Rect, bleed: float
) -> bool:
    """Return whether a closed line segment enters a stroked rectangular card bound."""
    left, top = shape.x - bleed, shape.y - bleed
    right, bottom = shape.x + shape.width + bleed, shape.y + shape.height + bleed
    dx, dy = end[0] - start[0], end[1] - start[1]
    lower, upper = 0.0, 1.0
    for direction, boundary in (
        (-dx, start[0] - left),
        (dx, right - start[0]),
        (-dy, start[1] - top),
        (dy, bottom - start[1]),
    ):
        if direction == 0:
            if boundary < 0:
                return False
            continue
        point = boundary / direction
        if direction < 0:
            if point > upper:
                return False
            lower = max(lower, point)
        else:
            if point < lower:
                return False
            upper = min(upper, point)
    return lower <= upper


def _polyline_intersects_card(line: Polyline, card: Rect) -> bool:
    segments = tuple(
        (line.points[index], line.points[index + 1]) for index in range(len(line.points) - 1)
    )
    arrow = line.arrowhead
    assert arrow is not None
    arrow_segments = tuple(zip(arrow.points, arrow.points[1:] + arrow.points[:1], strict=True))
    return any(
        _segment_intersects_shape(start, end, card, line.line_width / 2)
        for start, end in (*segments, *arrow_segments)
    )


def _arrow_points_with_final_segment(line: Polyline) -> bool:
    """Check arrowhead direction numerically, independent of its exact polygon dimensions."""
    arrow = line.arrowhead
    assert arrow is not None
    previous, endpoint = line.points[-2:]
    direction = (endpoint[0] - previous[0], endpoint[1] - previous[1])
    base_midpoint = (
        sum(point[0] for point in arrow.points[1:]) / (len(arrow.points) - 1),
        sum(point[1] for point in arrow.points[1:]) / (len(arrow.points) - 1),
    )
    head_direction = (endpoint[0] - base_midpoint[0], endpoint[1] - base_midpoint[1])
    return direction[0] * head_direction[0] + direction[1] * head_direction[1] > 0


def _line_segments(line: Polyline) -> tuple[tuple[tuple[float, float], tuple[float, float]], ...]:
    """Include the arrowhead edges because a filled head must not enter a card either."""
    arrow = line.arrowhead
    assert arrow is not None
    return tuple(
        (line.points[index], line.points[index + 1]) for index in range(len(line.points) - 1)
    ) + tuple(zip(arrow.points, arrow.points[1:] + arrow.points[:1], strict=True))


def _point_is_inside_card(point: tuple[float, float], card: Rect) -> bool:
    x, y = point
    return card.x < x < card.x + card.width and card.y < y < card.y + card.height


def _segment_enters_card_interior(
    start: tuple[float, float], end: tuple[float, float], card: Rect
) -> bool:
    """Check a segment against the open card interior, so boundary touches remain legal."""
    x0, y0 = start
    x1, y1 = end
    parameters = {0.0, 1.0}
    for start_value, end_value, lower, upper in (
        (x0, x1, card.x, card.x + card.width),
        (y0, y1, card.y, card.y + card.height),
    ):
        delta = end_value - start_value
        if delta:
            for boundary in (lower, upper):
                parameter = (boundary - start_value) / delta
                if 0.0 < parameter < 1.0:
                    parameters.add(parameter)
    ordered = sorted(parameters)
    probes = ordered + [
        (left + right) / 2 for left, right in zip(ordered, ordered[1:], strict=False)
    ]
    return any(
        _point_is_inside_card((x0 + (x1 - x0) * parameter, y0 + (y1 - y0) * parameter), card)
        for parameter in probes
    )


def _orientation(
    start: tuple[float, float], end: tuple[float, float], point: tuple[float, float]
) -> float:
    return (end[0] - start[0]) * (point[1] - start[1]) - (end[1] - start[1]) * (
        point[0] - start[0]
    )


def _segments_intersect(
    first: tuple[tuple[float, float], tuple[float, float]],
    second: tuple[tuple[float, float], tuple[float, float]],
) -> bool:
    """Return true for crossings, touches, and collinear overlaps."""
    (a, b), (c, d) = first, second
    orientations = (_orientation(a, b, c), _orientation(a, b, d), _orientation(c, d, a), _orientation(c, d, b))
    if all(value == 0 for value in orientations):
        return not (
            max(a[0], b[0]) < min(c[0], d[0])
            or max(c[0], d[0]) < min(a[0], b[0])
            or max(a[1], b[1]) < min(c[1], d[1])
            or max(c[1], d[1]) < min(a[1], b[1])
        )
    return orientations[0] * orientations[1] <= 0 and orientations[2] * orientations[3] <= 0


@pytest.fixture
def fig1() -> Scene:
    return _builder("fig_01_six_readings.py")(CONTENT.figures["fig-01"], TOKENS)


@pytest.fixture
def fig2() -> Scene:
    return _builder("fig_02_vego_baseline.py")(CONTENT.figures["fig-02"], TOKENS)


@pytest.fixture
def fig3() -> Scene:
    return _builder("fig_03_gap_mapping.py")(CONTENT.figures["fig-03"], TOKENS)


@pytest.fixture
def fig4() -> Scene:
    return _builder("fig_04_programme_spine.py")(CONTENT.figures["fig-04"], TOKENS)


def test_figure_1_has_equal_six_way_nonconverging_fanout(fig1: Scene) -> None:
    branches = [
        group for group in _groups(fig1) if _metadata(group).get("role") == "reading-branch"
    ]

    assert len(branches) == 6
    assert len({_metadata(branch)["edge-width"] for branch in branches}) == 1
    assert (
        len({(_metadata(branch)["column"], _metadata(branch)["row"]) for branch in branches}) == 6
    )
    assert not any(_metadata(group).get("role") == "reading-convergence" for group in _groups(fig1))
    assert _metadata(_groups(fig1)[0])["origin-count"] == "1"
    assert CONTENT.figures["fig-01"].title == "Six readings of one observed model difference"
    assert set(CONTENT.figures["fig-01"].items["readings"]).issubset(set(_texts(fig1)))
    assert "the artifact is identical under all six" in _texts(fig1)
    legend = next(
        group for group in _groups(fig1) if _metadata(group).get("role") == "visual-language-legend"
    )
    legend_elements = _elements(legend)
    assert (
        sum(
            isinstance(element, Rect)
            and not isinstance(element, (RoundedRect, Diamond, Cylinder, Parallelogram))
            for element in legend_elements
        )
        >= 1
    )
    assert sum(isinstance(element, RoundedRect) for element in legend_elements) >= 1
    assert sum(isinstance(element, Diamond) for element in legend_elements) >= 1
    assert sum(isinstance(element, Cylinder) for element in legend_elements) >= 1
    assert sum(isinstance(element, Parallelogram) for element in legend_elements) >= 1
    assert {
        "Rectangle: artifact or record",
        "Rounded rectangle: process or agent",
        "Diamond: decision or milestone",
        "Cylinder: store",
        "Parallelogram: human-judgment input",
        "Solid: committed or existing flow",
        "Dashed: conditional, proposed, or gated flow",
        "Dotted: information reference",
        "Navy: existing VEGO-AI baseline",
        "Orange: proposed doctoral human-judgment layer",
        "Cool grey: conditional, gated, or out of scope",
    }.issubset(set(_texts(fig1)))
    observed_fragment = next(
        element
        for element in fig1.elements
        if isinstance(element, Rect) and element.label == "observed fragment"
    )
    assert type(observed_fragment) is Rect
    cards = [
        element
        for branch in branches
        for element in branch.elements
        if isinstance(element, Rect)
        and element.label
        and element.label.startswith("reading ")
    ]
    assert len(cards) == 6
    assert all(type(card) is Rect for card in cards)
    for branch in branches:
        line = next(element for element in branch.elements if isinstance(element, Polyline))
        assert all(not _polyline_intersects_card(line, card) for card in cards)
    validate_scene(fig1)


def test_figure_1_reading_labels_stay_inside_their_cards(fig1: Scene) -> None:
    """Catch wrapped reading text that spills into the next row at final size."""
    branches = [
        group for group in _groups(fig1) if _metadata(group).get("role") == "reading-branch"
    ]

    for branch in branches:
        card = next(element for element in branch.elements if isinstance(element, Rect))
        labels = [element for element in branch.elements if isinstance(element, Text)]
        for label in labels:
            x, y, width, height = text_bounds(label)
            assert card.x <= x
            assert x + width <= card.x + card.width
            assert card.y <= y
            assert y + height <= card.y + card.height


def test_figure_2_preserves_pipeline_artifacts_refinement_loop_and_attachment_band(
    fig2: Scene,
) -> None:
    agents = [group for group in _groups(fig2) if _metadata(group).get("role") == "baseline-agent"]
    labels = [_metadata(agent)["label"] for agent in agents]

    assert labels == list(CONTENT.figures["fig-02"].items["agents"])
    assert set(CONTENT.figures["fig-02"].items["artifacts"]).issubset(set(_texts(fig2)))
    assert any(_metadata(group).get("role") == "refinement-loop" for group in _groups(fig2))
    band = next(
        group for group in _groups(fig2) if _metadata(group).get("role") == "doctoral-attachment"
    )
    assert _metadata(band)["line-style"] == "dashed"
    assert any("outside the baseline" in value for value in _texts(fig2))
    source_note = CONTENT.figures["fig-02"].provenance
    assert source_note in _texts(fig2)
    assert "[1]" in source_note
    assert not source_note.startswith("Figure 2.")
    assert CONTENT.figures["fig-02"].caption not in _texts(fig2)
    validate_scene(fig2)


def test_figure_3_keeps_the_residual_gap_open_and_maps_each_gap_to_a_subquestion(
    fig3: Scene,
) -> None:
    streams = [
        group for group in _groups(fig3) if _metadata(group).get("role") == "established-stream"
    ]
    rows = [group for group in _groups(fig3) if _metadata(group).get("role") == "gap-to-sq"]
    gap = next(group for group in _groups(fig3) if _metadata(group).get("role") == "residual-gap")

    assert len(streams) == 5
    assert list(CONTENT.figures["fig-03"].items["streams"]) == [
        "mixed-initiative design",
        "deferral & active learning",
        "explanatory debugging & provenance",
        "case-based reasoning & transfer",
        "guideline operationalization",
    ]
    assert set(CONTENT.figures["fig-03"].items["streams"]).issubset(set(_texts(fig3)))
    assert len(rows) == 3
    assert _metadata(gap)["fill"] == "unfilled"
    assert _metadata(gap)["line-style"] == "dashed"
    assert any(
        _metadata(group).get("role") == "umbrella-reference"
        and _metadata(group)["line-style"] == "dotted"
        for group in _groups(fig3)
    )
    assert {"SQ1", "SQ2", "SQ3"}.issubset(set(_texts(fig3)))
    sq3_reference = next(
        group
        for group in _groups(fig3)
        if _metadata(group).get("role") == "sq-reference"
        and _metadata(group).get("source") == "SQ3"
    )
    sq3_line = next(element for element in sq3_reference.elements if isinstance(element, Polyline))
    assert _arrow_points_with_final_segment(sq3_line)
    validate_scene(fig3)


def test_figure_4_is_exact_four_by_four_programme_spine(fig4: Scene) -> None:
    spine = next(
        group for group in _groups(fig4) if _metadata(group).get("role") == "programme-spine"
    )
    rows = [group for group in _groups(fig4) if _metadata(group).get("role") == "spine-row"]

    assert _metadata(spine)["columns"] == "4"
    assert [_metadata(row)["row"] for row in rows] == ["SQ1", "SQ2", "SQ3", "Integrated"]
    assert _metadata(rows[-1])["treatment"] == "integrated"
    consumption = [
        group for group in _groups(fig4) if _metadata(group).get("role") == "consumption-arrow"
    ]
    assert len(consumption) == 3
    assert list(CONTENT.figures["fig-04"].items["columns"]) == [
        "Sub-question",
        "Primary artifact",
        "Evaluation",
        "Planned output",
    ]
    assert set(CONTENT.figures["fig-04"].items["columns"]).issubset(set(_texts(fig4)))
    assert {
        cell for row in CONTENT.figures["fig-04"].items["spine_rows"] for cell in row["cells"]
    }.issubset(set(_texts(fig4)))
    validate_scene(fig4)


def test_figure_4_preserves_specified_study_labels_and_four_arm_comparison(
    fig4: Scene,
) -> None:
    """Catch a genericized programme spine that drops the proposal's study contract."""
    visible_text = set(_texts(fig4))
    rows = {
        _metadata(group)["row"]: group
        for group in _groups(fig4)
        if _metadata(group).get("role") == "spine-row"
    }

    assert {
        "Attention-budget review-policy model",
        "Conformance and comparator study",
        "Reliability and frozen-target study",
    }.issubset(visible_text)
    integrated = rows["Integrated"]
    assert _metadata(integrated)["comparison"] == "four-arm"
    assert _metadata(integrated)["arms"] == (
        "AI-only|human-only|ordinary non-governed HITL|governed VEGO-AI"
    )
    assert {
        "AI-only",
        "human-only",
        "ordinary non-governed HITL",
        "governed VEGO-AI",
    }.issubset(visible_text)


def test_figure_4_row_labels_stay_inside_their_aligned_cells(fig4: Scene) -> None:
    """Catch specified study labels wrapping through a programme-row boundary."""
    rows = [
        group
        for group in _groups(fig4)
        if _metadata(group).get("role") == "spine-row"
    ]

    for row in rows:
        cards = [element for element in row.elements if isinstance(element, Rect)]
        labels = [element for element in row.elements if isinstance(element, Text)]
        for label in labels:
            card = next(card for card in cards if card.x <= label.x < card.x + card.width)
            x, y, width, height = text_bounds(label)
            assert card.x <= x
            assert x + width <= card.x + card.width
            assert card.y <= y
            assert y + height <= card.y + card.height


def test_figure_4_consumption_routes_use_separate_boundary_only_lanes(fig4: Scene) -> None:
    rows = {
        _metadata(group)["row"]: group
        for group in _groups(fig4)
        if _metadata(group).get("role") == "spine-row"
    }
    target = next(
        element
        for element in rows["Integrated"].elements
        if isinstance(element, Rect) and element.label == "Matched cases, evidence and attention"
    )
    routes = [
        group
        for group in _groups(fig4)
        if _metadata(group).get("role") == "consumption-arrow"
    ]
    lanes: list[float] = []
    route_segments: list[tuple[tuple[tuple[float, float], tuple[float, float]], ...]] = []
    for route in routes:
        metadata = _metadata(route)
        line = next(element for element in route.elements if isinstance(element, Polyline))
        source = next(
            element
            for element in rows[metadata["source"]].elements
            if isinstance(element, Rect) and element.label == f"Paper {metadata['source'][-1]}"
        )
        cards = [
            element
            for row in rows.values()
            for element in row.elements
            if isinstance(element, Rect)
        ]

        assert line.dash == "dashed"
        assert line.points[0][0] == source.x + source.width
        assert source.y < line.points[0][1] < source.y + source.height
        assert line.points[-1][0] == target.x + target.width
        assert target.y < line.points[-1][1] < target.y + target.height
        assert _arrow_points_with_final_segment(line)
        assert all(
            not _segment_enters_card_interior(start, end, card)
            for start, end in _line_segments(line)
            for card in cards
        )
        lanes.append(line.points[1][0])
        route_segments.append(_line_segments(line))

    assert len(routes) == 3
    assert len(set(lanes)) == 3
    for index, first_route in enumerate(route_segments):
        for second_route in route_segments[index + 1 :]:
            for first in first_route:
                for second in second_route:
                    if _segments_intersect(first, second):
                        assert set(first) & set(second), "routes may meet only at an intentional endpoint"


@pytest.mark.parametrize(
    ("figure_id", "builder_filename", "exception_values"),
    (
        ("fig-01", "fig_01_six_readings.py", lambda: {CONTENT.figures["fig-01"].provenance}),
        (
            "fig-02",
            "fig_02_vego_baseline.py",
            lambda: {CONTENT.figures["fig-02"].provenance},
        ),
        (
            "fig-03",
            "fig_03_gap_mapping.py",
            lambda: {
                CONTENT.figures["fig-03"].provenance,
                "The opening remains open; integrated evaluation is proposed rather than established.",
            },
        ),
        (
            "fig-04",
            "fig_04_programme_spine.py",
            lambda: {
                CONTENT.figures["fig-04"].provenance,
                "Consumes all three studies; not answered by completing them.",
            },
        ),
    ),
)
def test_figures_01_04_meet_declared_width_text_and_a4_height_contract(
    figure_id: str, builder_filename: str, exception_values: object
) -> None:
    """Measure the actual scene roles at the fixed DOCX insertion width."""
    scene = _builder(builder_filename)(CONTENT.figures[figure_id], TOKENS)
    scale = DECLARED_WIDTH_EMU[figure_id] / EMU_PER_POINT / scene.width
    texts = _text_elements(scene)
    ordinary = [text for text in texts if text.semantic_role == "label"]
    exceptions = [text for text in texts if text.semantic_role != "label"]

    assert min(text.font_size * scale for text in texts) >= 7.0
    assert min(text.font_size * scale for text in ordinary) >= 8.0
    assert scene.height * scale <= A4_HEIGHT_PT - 2 * PROOF_MARGIN_PT
    assert {text.semantic_role for text in exceptions} <= {
        "provenance",
        "supporting-note",
        "boundary-note",
    }
    assert {text.value for text in exceptions} == exception_values()


@pytest.mark.parametrize(
    ("figure_id", "builder_filename"),
    (
        ("fig-01", "fig_01_six_readings.py"),
        ("fig-02", "fig_02_vego_baseline.py"),
        ("fig-03", "fig_03_gap_mapping.py"),
        ("fig-04", "fig_04_programme_spine.py"),
    ),
)
def test_figures_01_04_fit_their_frozen_docx_height_envelopes(
    figure_id: str, builder_filename: str
) -> None:
    """Catch any layout that would expand the frozen 31-page proposal pagination."""
    scene = _builder(builder_filename)(CONTENT.figures[figure_id], TOKENS)
    scale = DECLARED_WIDTH_EMU[figure_id] / EMU_PER_POINT / scene.width
    rendered_height_pt = scene.height * scale
    frozen_height_pt = FROZEN_INLINE_HEIGHT_EMU[figure_id] / EMU_PER_POINT

    assert rendered_height_pt <= frozen_height_pt + 0.5
