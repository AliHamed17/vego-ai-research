"""Semantic and geometry contracts for proposal figures 8 through 11."""

from __future__ import annotations

import importlib.util
import re
from decimal import Decimal
from pathlib import Path
from xml.etree import ElementTree

import pytest

from proposal_visuals.content import load_content
from proposal_visuals.document_integrity import verify_planned_svg_semantics
from proposal_visuals.model import (
    Diamond,
    Group,
    Polyline,
    Rect,
    RoundedRect,
    Scene,
    Text,
    text_bounds,
    validate_scene,
)
from proposal_visuals.qa import (
    A4_HEIGHT_PT,
    DECLARED_WIDTH_EMU,
    EMU_PER_POINT,
    ORDINARY_TEXT_EXCEPTION_ROLES,
    PROOF_MARGIN_PT,
)
from proposal_visuals.svg_backend import render_svg
from proposal_visuals.tokens import VisualTokens

ROOT = Path(__file__).resolve().parents[2]
CONTENT = load_content(ROOT / "docs" / "research" / "phd-proposal" / "figures" / "content.json")
TOKENS = VisualTokens.proposal()
INTEGRATION_HEIGHT_EMU = {
    "fig-08": 1_610_091,
    "fig-09": 2_963_971,
    "fig-10": 2_920_229,
}
INTEGRATION_HEIGHT_TOLERANCE_PT = 0.5
TABLE8_PERIOD_OUTPUTS = (
    (
        "Semester 1",
        "Oct 2027 - Mar 2028",
        "Executed review with screening and inclusion counts; taxonomy first version; preregistered Study 1 protocol; labeled baseline.",
    ),
    (
        "Semester 2",
        "Apr 2028 - Sep 2028",
        "Study 1 artifact, evaluation package, and Paper 1 submission.",
    ),
    (
        "Semester 3",
        "Oct 2028 - Mar 2029",
        "Governed-judgment contract, conformance suite, and reference implementation.",
    ),
    (
        "Semester 4",
        "Apr 2029 - Sep 2029",
        "Study 2 empirical report, Paper 2 submission, and governed source corpus.",
    ),
    (
        "Semester 5",
        "Oct 2029 - Mar 2030",
        "Study 3 artifact, target evaluation, and Paper 3 submission.",
    ),
    (
        "Semester 6",
        "Apr 2030 - Sep 2030",
        "Integrated thesis contribution, dissertation, and review package.",
    ),
)
FIGURE9_WORKSTREAMS = (
    "Literature review",
    "Study 1",
    "Study 2",
    "Study 3",
    "Integrated evaluation",
    "Publications",
)
FIGURE9_TABLE8_ACTIVITIES = (
    "Execute the five registered query families with screening and record the per-query audit; confirm research questions and artifact boundaries; freeze the Study 1 protocol including its primary estimand and selective-risk ceiling; complete independent labels for the software and modeling baseline.",
    "Implement and evaluate Study 1; analyse burden and important-case capture; prepare the first paper.",
    "Freeze the Study 2 contract; build conformance fixtures; recruit an independent implementer and reviewers; run instrument validation.",
    "Run the Study 2 comparator study; complete analysis and Paper 2; prepare the frozen source store for Study 3.",
    "Run the Study 3 reliability and target-context evaluation. Any medical work proceeds only if the go/no-go decision at the end of Semester 4, September 2029, was affirmative and all six entry gates are approved.",
    "Run the integrated evaluation; synthesize findings and boundary conditions; complete the thesis and defence preparation.",
)
FIGURE9_SCHEDULE_BARS = (
    ("Literature review", "Review", "1", "1"),
    ("Study 1", "Protocol -> eval.", "1", "2"),
    ("Study 2", "Contract -> study", "3", "4"),
    ("Study 3", "Target", "5", "5"),
    ("Integrated evaluation", "Thesis", "6", "6"),
)
FIGURE9_MILESTONE_LABELS = (
    "Paper 1",
    "Paper 2",
    "Paper 3",
    "defence",
    "go / no-go - Sep 2029",
)
TABLE11_CONCEPTS = (
    "Reuse of a stored judgment in a later, different episode, and the reuse mode - inert, advisory, or behavior-changing",
    "Claim-level validity scope: the prospective applicability envelope, including explicit negative scope",
    "Diagnostic attribution: whether an intervention reveals a domain-specific quirk or a transferable capability gap",
    "Temporal validity: expiry, supersession, revocation, and lapse when the interpreted guideline is revised",
    "Claim-scoped authority and competence, separating case-level decisions from rubric-level changes",
    "Version-exact provenance binding to the artifact state judged, with staleness detection",
    "The elicitation trigger as a versioned, reason-coded policy object",
    "Attention-budget accounting: a bounded budget per run and an allocation rule across claims",
    "Preserved dissent: two conflicting judgments both retained, reuse blocked pending adjudication",
    "Reuse-leakage control: provenance disjointness between the judgment store and the evaluation cases",
    "Judgment target layer: verdict, the agent's stated reasoning, evidence selection, or the guideline",
)


def _builder(filename: str):
    source = ROOT / "docs" / "research" / "phd-proposal" / "figures" / "sources" / filename
    spec = importlib.util.spec_from_file_location(filename.removesuffix(".py"), source)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.build


def _groups(scene: Scene, role: str | None = None) -> tuple[Group, ...]:
    found: list[Group] = []

    def visit(elements: tuple[object, ...]) -> None:
        for element in elements:
            if isinstance(element, Group):
                if (
                    role is None
                    or element.semantic_role == role
                    or dict(element.metadata).get("role") == role
                ):
                    found.append(element)
                visit(element.elements)

    visit(scene.elements)
    return tuple(found)


def _elements(elements: tuple[object, ...]) -> tuple[object, ...]:
    found: list[object] = []
    for element in elements:
        found.append(element)
        if isinstance(element, Group):
            found.extend(_elements(element.elements))
    return tuple(found)


def _texts(scene: Scene) -> tuple[str, ...]:
    return tuple(
        element.value for element in _elements(scene.elements) if isinstance(element, Text)
    )


def _text_elements(scene: Scene) -> tuple[Text, ...]:
    return tuple(element for element in _elements(scene.elements) if isinstance(element, Text))


def _assert_final_size_contract(
    figure_id: str, scene: Scene, *, native_ordinary_floor: float, native_exception_floor: float
) -> None:
    """Measure scene text and placed height at the reviewed final width."""
    scale = (DECLARED_WIDTH_EMU[figure_id] / EMU_PER_POINT) / scene.width
    all_text = _text_elements(scene)
    ordinary = tuple(
        text for text in all_text if text.semantic_role not in ORDINARY_TEXT_EXCEPTION_ROLES
    )
    exceptions = tuple(
        text for text in all_text if text.semantic_role in ORDINARY_TEXT_EXCEPTION_ROLES
    )

    assert all_text
    assert ordinary
    assert all(text.semantic_role in ORDINARY_TEXT_EXCEPTION_ROLES for text in exceptions)
    assert min(text.font_size for text in ordinary) >= native_ordinary_floor
    assert not exceptions or min(text.font_size for text in exceptions) >= native_exception_floor
    assert min(text.font_size * scale for text in all_text) >= 7.0
    assert min(text.font_size * scale for text in ordinary) >= 8.0
    assert scene.height * scale <= A4_HEIGHT_PT - 2 * PROOF_MARGIN_PT


def _assert_integration_height_envelope(figure_id: str, scene: Scene) -> None:
    scale = (DECLARED_WIDTH_EMU[figure_id] / EMU_PER_POINT) / scene.width
    placed_height_pt = scene.height * scale
    maximum_height_pt = INTEGRATION_HEIGHT_EMU[figure_id] / EMU_PER_POINT

    assert placed_height_pt <= maximum_height_pt + INTEGRATION_HEIGHT_TOLERANCE_PT


def _metadata(scene: Scene, key: str) -> str:
    root = _groups(scene, "figure-root")
    assert len(root) == 1
    return dict(root[0].metadata)[key]


def _points_forward(line: Polyline) -> bool:
    start, end = line.points[-2:]
    arrow = line.arrowhead
    assert arrow is not None
    base_midpoint = (
        sum(point[0] for point in arrow.points[1:]) / (len(arrow.points) - 1),
        sum(point[1] for point in arrow.points[1:]) / (len(arrow.points) - 1),
    )
    return (end[0] - start[0]) * (end[0] - base_midpoint[0]) + (end[1] - start[1]) * (
        end[1] - base_midpoint[1]
    ) > 0


def _contains(rect: Rect, point: tuple[float, float]) -> bool:
    return rect.x <= point[0] <= rect.x + rect.width and rect.y <= point[1] <= rect.y + rect.height


def _bounds_overlap(
    first: tuple[float, float, float, float], second: tuple[float, float, float, float]
) -> bool:
    first_x, first_y, first_width, first_height = first
    second_x, second_y, second_width, second_height = second
    return (
        first_x < second_x + second_width
        and second_x < first_x + first_width
        and first_y < second_y + second_height
        and second_y < first_y + first_height
    )


@pytest.fixture
def fig8() -> Scene:
    return _builder("fig_08_expert_scores.py")(CONTENT.figures["fig-08"], TOKENS)


@pytest.fixture
def fig9() -> Scene:
    return _builder("fig_09_three_year_plan.py")(CONTENT.figures["fig-09"], TOKENS)


@pytest.fixture
def fig10() -> Scene:
    return _builder("fig_10_taxonomy_boundary.py")(CONTENT.figures["fig-10"], TOKENS)


@pytest.fixture
def fig11() -> Scene:
    return _builder("fig_11_corpus_screening.py")(CONTENT.figures["fig-11"], TOKENS)


def test_figure_8_uses_exact_values_full_axis_and_baseline_boundary(fig8: Scene) -> None:
    bars = _groups(fig8, "score-bar")

    assert _metadata(fig8, "y_domain") == "0.0|1.0"
    assert _metadata(fig8, "pairs") == "0.80|0.55;0.96|0.81;0.83|0.55;0.92|0.88"
    assert [dict(group.metadata)["setting"] for group in bars] == [
        "ch-ucd",
        "ch-ucd",
        "ch-cd",
        "ch-cd",
        "pw-ucd",
        "pw-ucd",
        "pw-cd",
        "pw-cd",
    ]
    assert [dict(group.metadata)["value"] for group in bars] == [
        "0.80",
        "0.55",
        "0.96",
        "0.81",
        "0.83",
        "0.55",
        "0.92",
        "0.88",
    ]
    assert {_metadata(fig8, "evidence_scope")} == {"reported-baseline-only"}
    assert CONTENT.figures["fig-08"].items["axis"]["label"] in _texts(fig8)
    assert CONTENT.figures["fig-08"].items["sample_disclosure"] in _texts(fig8)
    assert CONTENT.figures["fig-08"].items["evidence_boundary"] in _texts(fig8)
    assert set(CONTENT.figures["fig-08"].items["series_labels"]).issubset(_texts(fig8))
    assert {dict(group.metadata)["encoding"] for group in bars} == {"solid", "hatch"}
    axis = next(group for group in _groups(fig8, "score-axis"))
    assert dict(axis.metadata)["ticks"] == "|".join(
        f"{value:.1f}" for value in CONTENT.figures["fig-08"].items["axis"]["ticks"]
    )
    for group in bars:
        rect = next(element for element in _elements(group.elements) if isinstance(element, Rect))
        assert float(dict(group.metadata)["height"]) == pytest.approx(rect.height)
    validate_scene(fig8)


def test_figure_8_meets_measured_final_size_and_keeps_direct_labels_readable(fig8: Scene) -> None:
    _assert_final_size_contract("fig-08", fig8, native_ordinary_floor=28, native_exception_floor=24)

    text_by_value = {text.value: text for text in _text_elements(fig8)}
    axis_label = text_by_value[CONTENT.figures["fig-08"].items["axis"]["label"]]
    for value in ("0.80", "0.55", "0.96", "0.81", "0.83", "0.92", "0.88"):
        assert text_by_value[value].font_size >= 28
    for tick in (f"{value:.1f}" for value in CONTENT.figures["fig-08"].items["axis"]["ticks"]):
        assert text_by_value[tick].font_size >= 28
        assert not _bounds_overlap(text_bounds(axis_label), text_bounds(text_by_value[tick]))
    for label in CONTENT.figures["fig-08"].items["series_labels"]:
        assert text_by_value[label].font_size >= 28


def test_figure_8_uses_horizontal_bars_and_fits_source_height_envelope(fig8: Scene) -> None:
    _assert_integration_height_envelope("fig-08", fig8)
    bars = _groups(fig8, "score-bar")
    assert all(dict(group.metadata)["orientation"] == "horizontal" for group in bars)
    assert all(
        next(element for element in _elements(group.elements) if isinstance(element, Rect)).width
        > next(element for element in _elements(group.elements) if isinstance(element, Rect)).height
        for group in bars
    )


def test_figure_9_is_a_calendar_workstream_swimlane_with_table_8_periods_and_outputs(
    fig9: Scene,
) -> None:
    plan = CONTENT.figures["fig-09"].items
    lanes = _groups(fig9, "workstream-lane")
    semesters = _groups(fig9, "semester-band")
    outputs = _groups(fig9, "table8-output")
    preparatory = _groups(fig9, "preparatory-band")

    assert _metadata(fig9, "layout") == "calendar-workstream-swimlane"
    assert _metadata(fig9, "timeline_start") == "Oct 2026"
    assert _metadata(fig9, "timeline_end") == "Oct 2030"
    assert _metadata(fig9, "preparatory_period") == "Oct 2026 - Oct 2027"
    assert _metadata(fig9, "main_period") == "Oct 2027 - Oct 2030"
    assert _metadata(fig9, "preparatory_in_three_year_count") == "false"
    assert [dict(group.metadata)["label"] for group in lanes] == list(FIGURE9_WORKSTREAMS)
    assert [
        (dict(group.metadata)["semester"], dict(group.metadata)["period"]) for group in semesters
    ] == [(semester, period) for semester, period, _ in TABLE8_PERIOD_OUTPUTS]
    assert [
        (
            dict(group.metadata)["semester"],
            dict(group.metadata)["period"],
            dict(group.metadata)["output"],
        )
        for group in outputs
    ] == list(TABLE8_PERIOD_OUTPUTS)
    expected_outputs = tuple(output for _, _, output in TABLE8_PERIOD_OUTPUTS)
    assert (
        tuple(value for value in _texts(fig9) if value in set(expected_outputs)) == expected_outputs
    )
    assert len(preparatory) == 1
    assert dict(preparatory[0].metadata) == {
        "role": "preparatory-band",
        "period": "Oct 2026 - Oct 2027",
        "outside_three_year_count": "true",
    }
    assert plan["preparatory_label"] in _texts(fig9)
    validate_scene(fig9)


def test_figure_9_preserves_every_table_8_activity_in_chronological_order(fig9: Scene) -> None:
    outputs = _groups(fig9, "table8-output")

    assert [
        (
            dict(group.metadata)["semester"],
            dict(group.metadata)["period"],
            dict(group.metadata)["activity"],
            dict(group.metadata)["output"],
        )
        for group in outputs
    ] == [
        (semester, period, activity, output)
        for (semester, period, output), activity in zip(
            TABLE8_PERIOD_OUTPUTS, FIGURE9_TABLE8_ACTIVITIES, strict=True
        )
    ]


def test_figure_9_places_every_schedule_bar_on_its_exact_semester_span(fig9: Scene) -> None:
    schedule_bars = _groups(fig9, "schedule-bar")

    assert [
        (
            dict(group.metadata)["lane"],
            next(
                text.value
                for text in _elements(group.elements)
                if isinstance(text, Text)
            ),
            dict(group.metadata)["start_semester"],
            dict(group.metadata)["end_semester"],
        )
        for group in schedule_bars
    ] == list(FIGURE9_SCHEDULE_BARS)


def test_figure_9_uses_three_study_dependencies_and_exact_milestone_dates(fig9: Scene) -> None:
    dependencies = _groups(fig9, "dependency")
    milestones = _groups(fig9, "milestone")
    medical = _groups(fig9, "conditional-medical-option")

    assert [
        (dict(group.metadata)["from"], dict(group.metadata)["to"]) for group in dependencies
    ] == [
        ("Study 1", "Study 2"),
        ("Study 2", "Study 3"),
        ("Study 3", "Integrated evaluation"),
    ]
    assert all(dict(group.metadata)["critical_path"] == "true" for group in dependencies)
    assert all(
        _points_forward(line)
        for group in dependencies
        for line in _elements(group.elements)
        if isinstance(line, Polyline)
    )
    assert [
        (dict(group.metadata)["label"], dict(group.metadata)["date"]) for group in milestones
    ] == [
        ("Paper 1", "Sep 2028"),
        ("Paper 2", "Sep 2029"),
        ("Paper 3", "Mar 2030"),
        ("defence", "Oct 2030"),
        ("go / no-go - Sep 2029", "Sep 2029"),
    ]
    assert all(
        any(isinstance(element, Diamond) for element in _elements(group.elements))
        for group in milestones
    )
    assert len(medical) == 1
    medical_metadata = dict(medical[0].metadata)
    assert medical_metadata["critical_path"] == "false"
    assert medical_metadata["start"] == "Oct 2029"
    assert medical_metadata["end"] == "Sep 2030"
    medical_shapes = tuple(
        element for element in _elements(medical[0].elements) if isinstance(element, Rect)
    )
    assert medical_shapes and all(shape.dash == "dashed" for shape in medical_shapes)
    assert _metadata(fig9, "medical_readiness") == "0/6"
    assert _metadata(fig9, "exp005_readiness") == "0/24"
    assert CONTENT.figures["fig-09"].items["readiness_gates"]["note"] in _texts(fig9)


def test_figure_9_has_true_time_order_and_meets_final_size_contract(fig9: Scene) -> None:
    _assert_final_size_contract("fig-09", fig9, native_ordinary_floor=35, native_exception_floor=31)
    _assert_integration_height_envelope("fig-09", fig9)

    prep_rect = next(
        element
        for element in _elements(_groups(fig9, "preparatory-band")[0].elements)
        if type(element) is Rect
    )
    semester_rects = [
        next(element for element in _elements(group.elements) if type(element) is Rect)
        for group in _groups(fig9, "semester-band")
    ]
    assert prep_rect.x + prep_rect.width <= semester_rects[0].x
    assert all(
        left.x + left.width == pytest.approx(right.x)
        for left, right in zip(semester_rects[:-1], semester_rects[1:], strict=True)
    )
    assert len({round(rect.width, 6) for rect in semester_rects}) == 1

    for dependency in _groups(fig9, "dependency"):
        line = next(
            element for element in _elements(dependency.elements) if isinstance(element, Polyline)
        )
        for bounds in (text_bounds(text) for text in _text_elements(fig9)):
            assert not _polyline_enters_bounds(line, bounds)


def test_figure_9_core_calendar_labels_are_ordinary_text_at_eight_points_or_larger(
    fig9: Scene,
) -> None:
    scale = (DECLARED_WIDTH_EMU["fig-09"] / EMU_PER_POINT) / fig9.width
    semesters = _groups(fig9, "semester-band")
    lanes = _groups(fig9, "workstream-lane")
    milestones = _groups(fig9, "milestone")

    semester_dates = tuple(
        next(
            text
            for text in _elements(group.elements)
            if isinstance(text, Text) and text.value == dict(group.metadata)["period"]
        )
        for group in semesters
    )
    workstream_names = tuple(
        next(
            text
            for text in _elements(group.elements)
            if isinstance(text, Text) and text.value == dict(group.metadata)["label"]
        )
        for group in lanes
    )
    milestone_labels = tuple(
        next(
            text
            for text in _elements(group.elements)
            if isinstance(text, Text) and text.value == dict(group.metadata)["label"]
        )
        for group in milestones
    )

    assert tuple(text.value for text in semester_dates) == tuple(
        period for _, period, _ in TABLE8_PERIOD_OUTPUTS
    )
    assert tuple(text.value for text in workstream_names) == FIGURE9_WORKSTREAMS
    assert tuple(text.value for text in milestone_labels) == FIGURE9_MILESTONE_LABELS
    assert {text.semantic_role for text in semester_dates} == {"semester-date"}
    assert {text.semantic_role for text in workstream_names} == {"workstream-label"}
    assert {text.semantic_role for text in milestone_labels} == {"milestone-label"}
    core_labels = (*semester_dates, *workstream_names, *milestone_labels)
    assert all(text.semantic_role not in ORDINARY_TEXT_EXCEPTION_ROLES for text in core_labels)
    assert min(text.font_size * scale for text in core_labels) >= 8.0


def test_figure_9_keeps_lane_and_milestone_labels_inside_their_visual_rows(fig9: Scene) -> None:
    for lane in _groups(fig9, "workstream-lane"):
        label_cell = next(element for element in lane.elements if type(element) is Rect)
        label = next(element for element in lane.elements if isinstance(element, Text))
        x, y, width, height = text_bounds(label)
        assert label_cell.x <= x and x + width <= label_cell.x + label_cell.width
        assert label_cell.y <= y and y + height <= label_cell.y + label_cell.height

    milestone_labels = tuple(
        element
        for group in _groups(fig9, "milestone")
        for element in _elements(group.elements)
        if isinstance(element, Text)
    )
    for index, label in enumerate(milestone_labels):
        assert all(
            not _bounds_overlap(text_bounds(label), text_bounds(other))
            for other in milestone_labels[index + 1 :]
        )


def test_figure_9_keeps_preparatory_and_go_no_go_text_clear_of_row_boundaries(
    fig9: Scene,
) -> None:
    preparatory = _groups(fig9, "preparatory-band")[0]
    preparatory_rect = next(element for element in preparatory.elements if type(element) is Rect)
    preparatory_texts = tuple(
        element for element in preparatory.elements if isinstance(element, Text)
    )
    assert len(preparatory_texts) == 2
    assert not _bounds_overlap(
        text_bounds(preparatory_texts[0]), text_bounds(preparatory_texts[1])
    )
    for label in preparatory_texts:
        x, y, width, height = text_bounds(label)
        assert preparatory_rect.x <= x and x + width <= preparatory_rect.x + preparatory_rect.width
        assert preparatory_rect.y <= y and y + height <= preparatory_rect.y + preparatory_rect.height

    medical = _groups(fig9, "conditional-medical-option")[0]
    medical_timeline_rect = max(
        (element for element in medical.elements if type(element) is Rect),
        key=lambda element: element.width,
    )
    decision = next(
        group
        for group in _groups(fig9, "milestone")
        if dict(group.metadata)["label"] == "go / no-go - Sep 2029"
    )
    decision_label = next(
        element for element in decision.elements if isinstance(element, Text)
    )
    x, y, width, height = text_bounds(decision_label)
    assert height == pytest.approx(decision_label.font_size)
    assert medical_timeline_rect.x <= x
    assert x + width <= medical_timeline_rect.x + medical_timeline_rect.width
    assert medical_timeline_rect.y <= y
    assert y + height <= medical_timeline_rect.y + medical_timeline_rect.height


def test_figure_9_svg_geometry_is_stable_under_words_six_digit_round_trip(
    fig9: Scene,
    tmp_path: Path,
) -> None:
    """Word writes six-significant-digit SVG geometry; Figure 9 must remain exact."""
    svg_path = tmp_path / "fig-09.svg"
    render_svg(fig9, svg_path)
    svg = svg_path.read_bytes()
    verify_planned_svg_semantics(svg)
    root = ElementTree.fromstring(svg)
    numeric_token = re.compile(r"[-+]?(?:\d+(?:\.\d*)?|\.\d+)")
    geometry_attributes = {
        "cx",
        "cy",
        "d",
        "dx",
        "dy",
        "height",
        "points",
        "r",
        "rx",
        "ry",
        "viewBox",
        "width",
        "x",
        "x1",
        "x2",
        "y",
        "y1",
        "y2",
    }
    unstable: list[tuple[str, str, str, str]] = []

    for element in root.iter():
        tag = element.tag.rsplit("}", 1)[-1]
        for qualified_name, value in element.attrib.items():
            name = qualified_name.rsplit("}", 1)[-1]
            if name not in geometry_attributes:
                continue
            for token in numeric_token.findall(value):
                number = Decimal(token)
                rounded = Decimal(format(number, ".6g"))
                if rounded != number:
                    unstable.append((tag, name, token, str(rounded)))

    assert unstable == []


def test_figure_10_uses_required_two_column_argument_and_exact_table_11_order(fig10: Scene) -> None:
    branches = _groups(fig10, "taxonomy-branch")
    concepts = _groups(fig10, "missing-concept")
    taxonomy_column = _groups(fig10, "taxonomy-column")
    concept_column = _groups(fig10, "concept-column")

    assert len(taxonomy_column) == 1
    assert len(concept_column) == 1
    taxonomy_rect = next(
        element for element in _elements(taxonomy_column[0].elements) if type(element) is Rect
    )
    matrix_rect = next(
        element for element in _elements(concept_column[0].elements) if type(element) is Rect
    )
    content_width = taxonomy_rect.width + matrix_rect.width
    assert taxonomy_rect.width / content_width == pytest.approx(0.4, abs=0.015)
    assert matrix_rect.width / content_width == pytest.approx(0.6, abs=0.015)
    assert taxonomy_rect.x + taxonomy_rect.width < matrix_rect.x
    branch_rects = [
        next(element for element in _elements(group.elements) if isinstance(element, Rect))
        for group in branches
    ]
    assert all(type(card) is Rect for card in branch_rects)
    assert all(
        not any(isinstance(element, RoundedRect) for element in _elements(group.elements))
        for group in branches
    )
    concept_rects = [
        next(element for element in _elements(group.elements) if isinstance(element, Rect))
        for group in concepts
    ]
    assert all(
        taxonomy_rect.x <= card.x
        and card.x + card.width <= taxonomy_rect.x + taxonomy_rect.width
        and taxonomy_rect.y <= card.y
        and card.y + card.height <= taxonomy_rect.y + taxonomy_rect.height
        for card in branch_rects
    )
    assert all(
        matrix_rect.x <= card.x
        and card.x + card.width <= matrix_rect.x + matrix_rect.width
        and matrix_rect.y <= card.y
        and card.y + card.height <= matrix_rect.y + matrix_rect.height
        for card in concept_rects
    )
    assert all(
        upper.y + upper.height < lower.y
        for upper, lower in zip(branch_rects[:-1], branch_rects[1:], strict=True)
    )
    assert all(
        upper.y + upper.height < lower.y
        for upper, lower in zip(concept_rects[:-1], concept_rects[1:], strict=True)
    )
    assert [dict(group.metadata)["label"] for group in branches] == [
        "Human Feedback",
        "Communication Mode",
        "Interaction Variant",
        "Orchestration",
    ]
    assert [dict(group.metadata)["label"] for group in concepts] == list(TABLE11_CONCEPTS)
    assert len(concepts) == 11
    assert (
        dict(concepts[6].metadata)["label"]
        == "The elicitation trigger as a versioned, reason-coded policy object"
    )
    assert _metadata(fig10, "layout") == "two-column-taxonomy-boundary"
    assert _metadata(fig10, "left_share") == "40%"
    assert _metadata(fig10, "right_share") == "60%"
    assert _metadata(fig10, "claim_scope") == "coverage-not-necessity-or-effectiveness"
    assert CONTENT.figures["fig-10"].items["claim_scope"] in _texts(fig10)
    assert "What the taxonomy covers" in _texts(fig10)
    assert "What this proposal needs but the taxonomy cannot express" in _texts(fig10)
    validate_scene(fig10)


def test_figure_10_meets_measured_final_size_and_contains_all_labels(fig10: Scene) -> None:
    _assert_final_size_contract(
        "fig-10", fig10, native_ordinary_floor=46, native_exception_floor=40
    )

    for text in _text_elements(fig10):
        x, y, width, height = text_bounds(text)
        assert x >= 0 and y >= 0
        assert x + width <= fig10.width
        assert y + height <= fig10.height


def test_figure_10_two_column_boundary_fits_source_height(fig10: Scene) -> None:
    _assert_integration_height_envelope("fig-10", fig10)


def test_figure_11_separates_paper_dispositions_from_research_question_coverage(
    fig11: Scene,
) -> None:
    segments = _groups(fig11, "paper-disposition")
    coverage = _groups(fig11, "rq-coverage")

    screening = CONTENT.figures["fig-11"].items
    assert _metadata(fig11, "paper_total") == str(screening["paper_total"])
    assert _metadata(fig11, "missing_level") == "research-question"
    assert [dict(group.metadata)["label"] for group in segments] == [
        "Relevant",
        "Less relevant",
        "Not relevant",
    ]
    assert [dict(group.metadata)["count"] for group in segments] == ["22", "63", "5"]
    assert [dict(group.metadata)["rq"] for group in coverage] == ["U-RQ", "SQ1", "SQ2", "SQ3"]
    assert [dict(group.metadata)["coverage"] for group in coverage] == [
        "Partly",
        "Yes",
        "Partly",
        "No",
    ]
    assert {dict(group.metadata)["encoding"] for group in coverage} == {
        "text+diagonal-hatch+muted-tone",
        "text+solid+existing-tone",
        "text+dotted-border+muted-tone",
    }
    assert _metadata(fig11, "standalone_candidate") == "true"
    assert screening["paper_disposition_heading"] in _texts(fig11)
    assert screening["rq_coverage_heading"] in _texts(fig11)
    assert screening["missing_coverage_note"] in _texts(fig11)
    assert screening["screening_limit"] in _texts(fig11)
    assert screening["standalone_status"] in _texts(fig11)
    validate_scene(fig11)


def test_figure_11_reserves_orange_for_the_doctoral_layer(fig11: Scene) -> None:
    """Corpus relevance and partial coverage are muted evidence states, not doctoral components."""
    orange = TOKENS.colors["human_judgment"].value
    less_relevant = next(
        group
        for group in _groups(fig11, "paper-disposition")
        if dict(group.metadata)["label"] == "Less relevant"
    )
    partly = tuple(
        group
        for group in _groups(fig11, "rq-coverage")
        if dict(group.metadata)["coverage"] == "Partly"
    )

    assert dict(less_relevant.metadata)["encoding"] == "label+diagonal-hatch+muted-tone"
    assert all(
        dict(group.metadata)["encoding"] == "text+diagonal-hatch+muted-tone" for group in partly
    )
    for group in (less_relevant, *partly):
        for element in _elements(group.elements):
            assert getattr(element, "fill", None) != orange
            assert getattr(element, "stroke", None) != orange
            assert getattr(element, "background", None) != orange


def test_figure_11_uses_rectangles_for_evidence_status_categories(fig11: Scene) -> None:
    """Evidence categories are structural states, not rounded process or agent nodes."""
    for group in _groups(fig11, "paper-disposition"):
        label = dict(group.metadata)["label"]
        card = next(
            element
            for element in _elements(group.elements)
            if isinstance(element, Rect) and element.label == label
        )
        assert type(card) is Rect
        assert not any(isinstance(element, RoundedRect) for element in _elements(group.elements))

    for group in _groups(fig11, "rq-coverage"):
        metadata = dict(group.metadata)
        label = f"{metadata['rq']} {metadata['coverage']}"
        card = next(
            element
            for element in _elements(group.elements)
            if isinstance(element, Rect) and element.label == label
        )
        assert type(card) is Rect
        assert not any(isinstance(element, RoundedRect) for element in _elements(group.elements))


def test_figure_11_keeps_hatching_clear_of_evidence_labels(fig11: Scene) -> None:
    less_relevant = next(
        group
        for group in _groups(fig11, "paper-disposition")
        if dict(group.metadata)["label"] == "Less relevant"
    )
    disposition_label = next(
        element for element in _elements(less_relevant.elements) if isinstance(element, Text)
    )
    label_background = next(
        element
        for element in _elements(less_relevant.elements)
        if type(element) is Rect and element.semantic_role == "label-background"
    )
    label_bounds = text_bounds(disposition_label)
    assert label_background.x <= label_bounds[0]
    assert label_background.y <= label_bounds[1]
    assert label_bounds[0] + label_bounds[2] <= label_background.x + label_background.width
    assert label_bounds[1] + label_bounds[3] <= label_background.y + label_background.height

    for group in (
        group
        for group in _groups(fig11, "rq-coverage")
        if dict(group.metadata)["coverage"] == "Partly"
    ):
        card = next(
            element
            for element in _elements(group.elements)
            if type(element) is Rect and element.semantic_role != "status-texture"
        )
        texture_chip = next(
            element
            for element in _elements(group.elements)
            if type(element) is Rect and element.hatch == "diagonal"
        )
        texture_label = next(
            element
            for element in _elements(group.elements)
            if isinstance(element, Text) and element.value == "diagonal hatch"
        )
        assert card.hatch is None
        assert not _bounds_overlap(
            (texture_chip.x, texture_chip.y, texture_chip.width, texture_chip.height),
            text_bounds(texture_label),
        )


def test_figure_11_meets_measured_final_size_and_stays_standalone(fig11: Scene) -> None:
    _assert_final_size_contract(
        "fig-11", fig11, native_ordinary_floor=19, native_exception_floor=17
    )
    assert _metadata(fig11, "standalone_candidate") == "true"


def _polyline_enters_bounds(line: Polyline, bounds: tuple[float, float, float, float]) -> bool:
    """Detect a route segment's entry into a text box, excluding endpoint contact."""
    x, y, width, height = bounds
    for start, end in zip(line.points[:-1], line.points[1:], strict=True):
        low, high = 0.0, 1.0
        for origin, delta, minimum, maximum in (
            (start[0], end[0] - start[0], x, x + width),
            (start[1], end[1] - start[1], y, y + height),
        ):
            if delta == 0:
                if not minimum < origin < maximum:
                    low, high = 1.0, 0.0
                    break
                continue
            first, second = sorted(((minimum - origin) / delta, (maximum - origin) / delta))
            low, high = max(low, first), min(high, second)
        if low < high and low < 1.0 and high > 0.0:
            return True
    return False
