"""Semantic and geometry contracts for proposal Figures 5 through 7."""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

from proposal_visuals.content import load_content
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
from proposal_visuals.tokens import VisualTokens

ROOT = Path(__file__).resolve().parents[2]
CONTENT = load_content(ROOT / "docs" / "research" / "phd-proposal" / "figures" / "content.json")
TOKENS = VisualTokens.proposal()

FROZEN_HEIGHT_ENVELOPES_EMU = {
    "fig-05": 3_259_853,
    "fig-06": 2_920_229,
    "fig-07": 3_639_375,
}
HEIGHT_TOLERANCE_PT = 0.5


def _builder(filename: str):
    source = ROOT / "docs" / "research" / "phd-proposal" / "figures" / "sources" / filename
    spec = importlib.util.spec_from_file_location(filename.removesuffix(".py"), source)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.build


def _all_elements(elements: tuple[object, ...]) -> tuple[object, ...]:
    found: list[object] = []
    for element in elements:
        found.append(element)
        if isinstance(element, Group):
            found.extend(_all_elements(element.elements))
    return tuple(found)


def _groups(scene: Scene, role: str) -> tuple[Group, ...]:
    return tuple(
        element
        for element in _all_elements(scene.elements)
        if isinstance(element, Group) and dict(element.metadata).get("role") == role
    )


def _texts(scene: Scene, role: str | None = None) -> tuple[Text, ...]:
    return tuple(
        element
        for element in _all_elements(scene.elements)
        if isinstance(element, Text) and (role is None or element.semantic_role == role)
    )


def _lines(group: Group) -> tuple[Polyline, ...]:
    return tuple(element for element in _all_elements(group.elements) if isinstance(element, Polyline))


def _assert_final_size_contract(
    figure_id: str, scene: Scene, *, native_ordinary_floor: float, native_exception_floor: float
) -> None:
    """Measure actual scene text at its proposal insertion width, without metadata shortcuts."""
    scale = (DECLARED_WIDTH_EMU[figure_id] / EMU_PER_POINT) / scene.width
    all_text = _texts(scene)
    ordinary = tuple(text for text in all_text if text.semantic_role not in ORDINARY_TEXT_EXCEPTION_ROLES)
    exceptions = tuple(text for text in all_text if text.semantic_role in ORDINARY_TEXT_EXCEPTION_ROLES)

    assert all_text
    assert ordinary
    assert all(text.semantic_role in ORDINARY_TEXT_EXCEPTION_ROLES for text in exceptions)
    assert min(text.font_size for text in ordinary) >= native_ordinary_floor
    assert not exceptions or min(text.font_size for text in exceptions) >= native_exception_floor
    assert min(text.font_size * scale for text in all_text) >= 7.0
    assert min(text.font_size * scale for text in ordinary) >= 8.0
    assert scene.height * scale <= A4_HEIGHT_PT - 2 * PROOF_MARGIN_PT


def _assert_frozen_height_envelope(figure_id: str, scene: Scene) -> None:
    """Keep the vector replacement inside the source drawing's inline height."""
    scale = (DECLARED_WIDTH_EMU[figure_id] / EMU_PER_POINT) / scene.width
    rendered_height_pt = scene.height * scale
    frozen_height_pt = FROZEN_HEIGHT_ENVELOPES_EMU[figure_id] / EMU_PER_POINT

    assert rendered_height_pt <= frozen_height_pt + HEIGHT_TOLERANCE_PT


def _points_forward(line: Polyline) -> bool:
    assert line.arrowhead is not None
    previous, endpoint = line.points[-2:]
    base = (
        sum(point[0] for point in line.arrowhead.points[1:]) / 2,
        sum(point[1] for point in line.arrowhead.points[1:]) / 2,
    )
    return (endpoint[0] - previous[0]) * (endpoint[0] - base[0]) + (endpoint[1] - previous[1]) * (endpoint[1] - base[1]) > 0


def _line_enters_bounds(line: Polyline, bounds: tuple[float, float, float, float]) -> bool:
    """Detect a route's entry into an open card or label bound without sampling gaps."""
    card_x, card_y, card_width, card_height = bounds
    for start, end in zip(line.points[:-1], line.points[1:], strict=True):
        lower, upper = 0.0, 1.0
        enters = True
        for origin, delta, minimum, maximum in (
            (start[0], end[0] - start[0], card_x, card_x + card_width),
            (start[1], end[1] - start[1], card_y, card_y + card_height),
        ):
            if delta == 0:
                if not minimum < origin < maximum:
                    enters = False
                    break
                continue
            first, second = sorted(((minimum - origin) / delta, (maximum - origin) / delta))
            lower, upper = max(lower, first), min(upper, second)
        if enters and lower < upper and lower < 1 and upper > 0:
            return True
    return False


def _line_enters_card(line: Polyline, card: Rect) -> bool:
    return _line_enters_bounds(line, (card.x, card.y, card.width, card.height))


def _bounds_overlap(
    first: tuple[float, float, float, float], second: tuple[float, float, float, float]
) -> bool:
    first_x, first_y, first_width, first_height = first
    second_x, second_y, second_width, second_height = second
    return (
        max(first_x, second_x) < min(first_x + first_width, second_x + second_width)
        and max(first_y, second_y) < min(first_y + first_height, second_y + second_height)
    )


def _orientation(start: tuple[float, float], end: tuple[float, float], point: tuple[float, float]) -> float:
    return (end[0] - start[0]) * (point[1] - start[1]) - (end[1] - start[1]) * (point[0] - start[0])


def _on_segment(start: tuple[float, float], end: tuple[float, float], point: tuple[float, float]) -> bool:
    return min(start[0], end[0]) <= point[0] <= max(start[0], end[0]) and min(start[1], end[1]) <= point[1] <= max(start[1], end[1])


def _segments_intersect(first: tuple[tuple[float, float], tuple[float, float]], second: tuple[tuple[float, float], tuple[float, float]]) -> bool:
    first_start, first_end = first
    second_start, second_end = second
    values = (
        _orientation(first_start, first_end, second_start),
        _orientation(first_start, first_end, second_end),
        _orientation(second_start, second_end, first_start),
        _orientation(second_start, second_end, first_end),
    )
    if any(value == 0 for value in values):
        return (
            (values[0] == 0 and _on_segment(first_start, first_end, second_start))
            or (values[1] == 0 and _on_segment(first_start, first_end, second_end))
            or (values[2] == 0 and _on_segment(second_start, second_end, first_start))
            or (values[3] == 0 and _on_segment(second_start, second_end, first_end))
        )
    return (values[0] > 0) != (values[1] > 0) and (values[2] > 0) != (values[3] > 0)


def _only_shared_endpoint(
    first: tuple[tuple[float, float], tuple[float, float]], second: tuple[tuple[float, float], tuple[float, float]]
) -> bool:
    return len(set(first).intersection(second)) == 1


def _declares_shared_bus(first: Group, second: Group) -> bool:
    first_metadata, second_metadata = dict(first.metadata), dict(second.metadata)
    return (
        first_metadata.get("bus_id")
        and first_metadata.get("bus_id") == second_metadata.get("bus_id")
        and "shared-bus" in {first_metadata.get("role"), second_metadata.get("role")}
    )


def _assert_routes_are_geometrically_separate(scene: Scene, route_roles: set[str]) -> None:
    routes = [group for role in route_roles for group in _groups(scene, role)]
    route_lines = [(group, line) for group in routes for line in _lines(group)]
    cards = [element for element in _all_elements(scene.elements) if isinstance(element, Rect)]
    label_bounds = [text_bounds(element) for element in _all_elements(scene.elements) if isinstance(element, Text)]
    for _, line in route_lines:
        assert all(not _line_enters_card(line, card) for card in cards)
        assert all(not _line_enters_bounds(line, bounds) for bounds in label_bounds)
    for first_index, (first_group, first_line) in enumerate(route_lines):
        first_segments = tuple(zip(first_line.points[:-1], first_line.points[1:], strict=True))
        for second_group, second_line in route_lines[first_index + 1 :]:
            second_segments = tuple(zip(second_line.points[:-1], second_line.points[1:], strict=True))
            for first_segment in first_segments:
                for second_segment in second_segments:
                    if _segments_intersect(first_segment, second_segment):
                        assert _only_shared_endpoint(first_segment, second_segment) or _declares_shared_bus(first_group, second_group)


@pytest.fixture
def fig5() -> Scene:
    return _builder("fig_05_review_policy.py")(CONTENT.figures["fig-05"], TOKENS)


@pytest.fixture
def fig6() -> Scene:
    return _builder("fig_06_judgment_lifecycle.py")(CONTENT.figures["fig-06"], TOKENS)


@pytest.fixture
def fig7() -> Scene:
    return _builder("fig_07_reuse_procedure.py")(CONTENT.figures["fig-07"], TOKENS)


def test_figure_5_keeps_exact_signals_budget_hard_rules_and_equal_actions(fig5: Scene) -> None:
    signals = _groups(fig5, "policy-signal")
    actions = _groups(fig5, "routing-action")
    constraint = _groups(fig5, "budget-constraint")
    hard_rules = _groups(fig5, "hard-rule")

    assert len(signals) == 8
    assert [dict(group.metadata)["label"] for group in signals] == CONTENT.figures["fig-05"].items["signals"]
    assert [dict(group.metadata)["source"] for group in signals] == ["literature-derived"] * 5 + ["proposed"] * 3
    assert len(constraint) == 1
    assert dict(constraint[0].metadata)["label"] == CONTENT.figures["fig-05"].items["constraint"]
    assert dict(constraint[0].metadata)["treatment"] == "enclosing-constraint"
    assert [dict(group.metadata)["label"] for group in hard_rules] == CONTENT.figures["fig-05"].items["hard_rules"]
    signal_cards = [
        next(element for element in _all_elements(group.elements) if isinstance(element, Rect))
        for group in signals
    ]
    assert all(type(card) is Rect for card in signal_cards)
    assert all(
        any(isinstance(element, Diamond) for element in _all_elements(group.elements))
        for group in hard_rules
    )
    assert len(actions) == 6
    assert [dict(group.metadata)["label"] for group in actions] == CONTENT.figures["fig-05"].items["actions"]
    assert len({dict(group.metadata)["width"] for group in actions}) == 1
    assert len({dict(group.metadata)["height"] for group in actions}) == 1
    blocked = actions[-1]
    assert dict(blocked.metadata)["treatment"] == "gated"
    assert all(line.dash == "dashed" for line in _lines(blocked))
    assert all(_points_forward(line) for group in (*signals, *actions, *hard_rules) for line in _lines(group))
    action_cards = {
        dict(group.metadata)["label"]: next(
            element for element in _all_elements(group.elements) if isinstance(element, RoundedRect)
        )
        for group in actions
    }
    for action in actions:
        own_label = dict(action.metadata)["label"]
        foreign_cards = [card for label, card in action_cards.items() if label != own_label]
        assert all(not _line_enters_card(line, card) for line in _lines(action) for card in foreign_cards)
    validate_scene(fig5)


def test_figure_5_meets_the_measured_final_size_and_portrait_height_contract(fig5: Scene) -> None:
    _assert_final_size_contract("fig-05", fig5, native_ordinary_floor=25, native_exception_floor=22)


def test_figure_5_fits_the_frozen_source_height_envelope(fig5: Scene) -> None:
    _assert_frozen_height_envelope("fig-05", fig5)


def test_figure_5_routes_all_signals_through_a_declared_input_bus_to_the_budget_constraint(fig5: Scene) -> None:
    signals = _groups(fig5, "policy-signal")
    buses = _groups(fig5, "shared-bus")
    constraint = _groups(fig5, "budget-constraint")[0]
    constraint_card = next(element for element in _all_elements(constraint.elements) if isinstance(element, Rect))

    assert len(buses) == 1
    bus = buses[0]
    bus_metadata = dict(bus.metadata)
    collector = next(line for line in _lines(bus) if line.points[0][0] == line.points[-1][0])
    bus_exit = next(line for line in _lines(bus) if line.points[-1][0] == constraint_card.x)
    bus_x = collector.points[0][0]
    assert bus_metadata["bus_id"] == "signal-input-bus"
    assert bus_metadata["source_ids"] == "|".join(f"signal-{index}" for index in range(1, 9))
    assert bus_metadata["target_id"] == "budget-constraint"
    assert bus_exit.points[0][0] == bus_x
    assert bus_exit.points[-1][0] == constraint_card.x
    assert constraint_card.y < bus_exit.points[-1][1] < constraint_card.y + constraint_card.height
    assert _points_forward(collector)
    assert _points_forward(bus_exit)

    assert len(signals) == 8
    for index, signal in enumerate(signals, start=1):
        signal_metadata = dict(signal.metadata)
        card = next(
            element
            for element in _all_elements(signal.elements)
            if type(element) is Rect
        )
        connector = _lines(signal)[0]
        assert signal_metadata["source_id"] == f"signal-{index}"
        assert signal_metadata["target_id"] == "signal-input-bus"
        assert connector.points[0] == (card.x + card.width, card.y + card.height / 2)
        assert connector.points[-1][0] == bus_x
        assert min(point[1] for point in collector.points) <= connector.points[-1][1] <= max(
            point[1] for point in collector.points
        )
        assert _points_forward(connector)


def test_figure_5_signal_input_bus_stays_outside_cards_and_text(fig5: Scene) -> None:
    routes = [*(_groups(fig5, "policy-signal")), *(_groups(fig5, "shared-bus"))]
    cards = [element for element in _all_elements(fig5.elements) if isinstance(element, Rect)]
    label_bounds = [text_bounds(element) for element in _all_elements(fig5.elements) if isinstance(element, Text)]

    for route in routes:
        for line in _lines(route):
            assert all(not _line_enters_card(line, card) for card in cards)
            assert all(not _line_enters_bounds(line, bounds) for bounds in label_bounds)


def test_figure_5_hard_rule_bypasses_do_not_strike_labels(fig5: Scene) -> None:
    label_bounds = [text_bounds(text) for text in _texts(fig5)]

    for hard_rule in _groups(fig5, "hard-rule"):
        for line in _lines(hard_rule):
            assert all(not _line_enters_bounds(line, bounds) for bounds in label_bounds)


def test_figure_5_hard_rule_labels_do_not_overlap_their_decision_diamonds(
    fig5: Scene,
) -> None:
    """Long condition labels must remain readable beside, not across, the decision symbol."""
    for hard_rule in _groups(fig5, "hard-rule"):
        diamond = next(
            element for element in _all_elements(hard_rule.elements) if isinstance(element, Diamond)
        )
        label = next(
            element for element in _all_elements(hard_rule.elements) if isinstance(element, Text)
        )
        connector = _lines(hard_rule)[0]
        assert not _bounds_overlap(
            (diamond.x, diamond.y, diamond.width, diamond.height), text_bounds(label)
        )
        assert connector.points[0] == (diamond.x + diamond.width / 2, diamond.y)


def test_figure_6_uses_canonical_ordered_states_explicit_transitions_and_discrepancy(fig6: Scene) -> None:
    fields = _groups(fig6, "record-field-group")
    states = _groups(fig6, "lifecycle-state")
    transitions = _groups(fig6, "state-transition")
    lifecycle = _groups(fig6, "judgment-lifecycle")[0]

    assert [dict(group.metadata)["label"] for group in fields] == CONTENT.figures["fig-06"].items["record_groups"]
    assert [dict(group.metadata)["state"] for group in states] == CONTENT.figures["fig-06"].items["states"]
    assert [dict(group.metadata)["label"] for group in transitions] == CONTENT.figures["fig-06"].items["transitions"]
    assert {dict(group.metadata)["target"] for group in transitions} == {"Validated", "Contested", "Superseded", "Expired", "Revoked"}
    assert {dict(group.metadata)["auditability"] for group in states if dict(group.metadata)["state"] in {"Superseded", "Expired", "Revoked"}} == {"retained"}
    assert dict(lifecycle.metadata)["current_source_states"] == "Draft|Reviewed|Active"
    assert dict(lifecycle.metadata)["canonical_states"] == "Created|Validated|Contested|Superseded|Expired|Revoked"
    assert dict(lifecycle.metadata)["discrepancy_resolution"] == "recorded-not-conflated"
    assert all(_points_forward(line) for group in transitions for line in _lines(group))
    validate_scene(fig6)


def test_figure_6_transition_routes_do_not_cross_cards_labels_or_each_other(fig6: Scene) -> None:
    _assert_routes_are_geometrically_separate(fig6, {"state-transition"})


def test_figure_6_meets_the_measured_final_size_and_portrait_height_contract(fig6: Scene) -> None:
    _assert_final_size_contract("fig-06", fig6, native_ordinary_floor=23, native_exception_floor=20)


def test_figure_6_fits_the_frozen_source_height_envelope(fig6: Scene) -> None:
    _assert_frozen_height_envelope("fig-06", fig6)


def test_figure_7_keeps_five_gates_four_statuses_and_a_separate_diagnostic_guard(
    fig7: Scene,
) -> None:
    gates = _groups(fig7, "reuse-gate")
    statuses = _groups(fig7, "formal-status")
    diagnoses = _groups(fig7, "diagnosis")
    checks = _groups(fig7, "capability-gap-check")
    procedure = _groups(fig7, "reuse-procedure")[0]

    assert [dict(group.metadata)["label"] for group in gates] == [
        "Similarity found",
        "Applicable here",
        "Requester authorized",
        "Still valid",
        "Does reuse actually help?",
    ]
    assert [dict(group.metadata)["sequence"] for group in gates] == [str(value) for value in range(1, 6)]
    assert [dict(group.metadata)["label"] for group in statuses] == [
        "Eligible",
        "Eligible with adaptation",
        "Blocked",
        "Undetermined",
    ]
    assert [dict(group.metadata)["label"] for group in diagnoses] == ["local quirk", "capability-gap candidate"]
    assert [dict(group.metadata)["label"] for group in checks] == [
        "one failure signature is predeclared",
        "it reproduces in at least two contexts differing above cohort",
        "an independent reviewer confirms it",
        "a local guideline, task, version, data or reviewer cause is ruled out",
    ]
    assert all(dict(group.metadata)["operator"] == "AND" for group in checks)
    assert dict(procedure.metadata)["gate_count"] == "5"
    assert dict(procedure.metadata)["status_count"] == "4"
    assert dict(procedure.metadata)["gate_to_status_mapping"] == "not-specified-in-source"
    assert dict(procedure.metadata)["diagnosis_dependency"] == "independent-of-reuse-status"
    validate_scene(fig7)


def test_figure_7_keeps_reuse_permission_distinct_from_statuses_and_diagnoses(
    fig7: Scene,
) -> None:
    """Catch any visual conflation of the positive effect, formal status, and diagnosis layers."""
    statuses = _groups(fig7, "formal-status")
    permission = _groups(fig7, "reuse-permission")
    diagnoses = _groups(fig7, "diagnosis")

    assert len(permission) == 1
    assert dict(permission[0].metadata) == {
        "role": "reuse-permission",
        "label": "reuse permitted",
        "formal_status": "false",
        "distinct_from_statuses": "true",
        "routing_rule": "not-specified-in-source",
    }
    assert {dict(group.metadata)["label"] for group in statuses} == {
        "Eligible",
        "Eligible with adaptation",
        "Blocked",
        "Undetermined",
    }
    assert {dict(group.metadata)["label"] for group in diagnoses} == {
        "local quirk",
        "capability-gap candidate",
    }
    assert all(dict(group.metadata)["independent_of_reuse_decision"] == "true" for group in diagnoses)
    assert {"reuse permitted", "local quirk", "capability-gap candidate"}.issubset(
        {text.value for text in _texts(fig7)}
    )


def test_figure_7_preserves_only_the_source_supported_gate_routes(fig7: Scene) -> None:
    pass_paths = _groups(fig7, "passed-path")
    failure_paths = _groups(fig7, "gate-failure-path")
    failure_boundary = _groups(fig7, "failure-boundary")

    assert len(pass_paths) == 4
    assert [dict(group.metadata)["source_gate"] for group in pass_paths] == ["1", "2", "3", "4"]
    assert [dict(group.metadata)["target_gate"] for group in pass_paths] == ["2", "3", "4", "5"]
    assert all(dict(group.metadata)["label"] == "yes" for group in pass_paths)
    assert len(failure_paths) == 5
    assert {dict(group.metadata)["source_gate"] for group in failure_paths} == {
        "1",
        "2",
        "3",
        "4",
        "5",
    }
    assert {dict(group.metadata)["target"] for group in failure_paths} == {
        "not eligible for reuse"
    }
    assert len(failure_boundary) == 1
    assert dict(failure_boundary[0].metadata)["gate_to_status_mapping"] == "not-specified-in-source"
    assert not any(
        _groups(fig7, role)
        for role in {
            "failure-classifier",
            "failure-status-branch",
            "status-split-path",
            "status-path",
            "reuse-permission-path",
            "diagnosis-path",
        }
    )


def test_figure_7_diagnosis_is_not_drawn_downstream_of_reuse_permission(fig7: Scene) -> None:
    diagnoses = _groups(fig7, "diagnosis")
    diagnostic_layer = _groups(fig7, "diagnostic-layer")

    assert len(diagnostic_layer) == 1
    assert dict(diagnostic_layer[0].metadata)["relationship_to_reuse"] == "independent"
    assert all("after_status" not in dict(group.metadata) for group in diagnoses)
    assert all("after_outcome" not in dict(group.metadata) for group in diagnoses)
    assert all(dict(group.metadata)["independent_of_reuse_decision"] == "true" for group in diagnoses)


def test_figure_7_routes_do_not_cross_cards_labels_or_nondeclared_routes(fig7: Scene) -> None:
    _assert_routes_are_geometrically_separate(
        fig7,
        {
            "passed-path",
            "gate-failure-path",
            "failure-boundary-path",
            "shared-bus",
            "diagnosis-guard-path",
            "capability-gap-check",
        },
    )


def test_figure_7_meets_the_measured_final_size_and_portrait_height_contract(fig7: Scene) -> None:
    _assert_final_size_contract("fig-07", fig7, native_ordinary_floor=27, native_exception_floor=24)


def test_figure_7_fits_the_frozen_source_height_envelope(fig7: Scene) -> None:
    _assert_frozen_height_envelope("fig-07", fig7)


def test_figure_7_text_labels_do_not_overlap(fig7: Scene) -> None:
    texts = _texts(fig7)
    bounds = tuple(text_bounds(text) for text in texts)
    overlaps = [
        (first.value, second.value)
        for index, first in enumerate(texts)
        for second_index, second in enumerate(texts[index + 1 :], start=index + 1)
        if _bounds_overlap(bounds[index], bounds[second_index])
    ]

    assert overlaps == [], overlaps


def test_figure_7_card_text_stays_inside_its_card(fig7: Scene) -> None:
    """Catch labels that look valid geometrically but print through a card border."""
    for role in {
        "failure-boundary",
        "formal-status",
        "reuse-permission",
        "capability-gap-check",
        "diagnosis",
    }:
        for group in _groups(fig7, role):
            card = next(
                element
                for element in _all_elements(group.elements)
                if isinstance(element, Rect)
            )
            for label in (
                element
                for element in _all_elements(group.elements)
                if isinstance(element, Text)
            ):
                x, y, width, height = text_bounds(label)
                assert card.x <= x
                assert x + width <= card.x + card.width
                assert card.y <= y
                assert y + height <= card.y + card.height


def test_figure_7_path_and_boundary_labels_do_not_enter_cards(fig7: Scene) -> None:
    cards = [element for element in _all_elements(fig7.elements) if isinstance(element, Rect)]
    route_labels = [
        text
        for group in _groups(fig7, "passed-path")
        for text in _texts(Scene(1_230, 945, group.elements))
    ]
    boundary_labels = _texts(fig7, "boundary-note")

    assert route_labels
    assert boundary_labels
    for label in (*route_labels, *boundary_labels):
        assert all(
            not _bounds_overlap(text_bounds(label), (card.x, card.y, card.width, card.height))
            for card in cards
        )
