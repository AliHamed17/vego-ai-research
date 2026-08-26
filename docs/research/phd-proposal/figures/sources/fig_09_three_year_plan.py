"""Figure 9: a dated workstream swimlane with a separate preparatory phase."""

from __future__ import annotations

import math

from proposal_visuals.content import FigureContent
from proposal_visuals.model import (
    Arrowhead,
    Diamond,
    Group,
    Polyline,
    Rect,
    RoundedRect,
    Scene,
    Text,
    text_bounds,
)
from proposal_visuals.tokens import VisualTokens


def _arrow(points: tuple[tuple[float, float], ...], tokens: VisualTokens) -> Polyline:
    """Draw one explicit, marker-free dependency arrow."""
    previous, endpoint = points[-2:]
    dx, dy = endpoint[0] - previous[0], endpoint[1] - previous[1]
    length = math.hypot(dx, dy)
    ux, uy = dx / length, dy / length
    base = (endpoint[0] - 11 * ux, endpoint[1] - 11 * uy)
    perpendicular = (-6 * uy, 6 * ux)
    return Polyline(
        points=points,
        arrowhead=Arrowhead(
            (
                endpoint,
                (base[0] + perpendicular[0], base[1] + perpendicular[1]),
                (base[0] - perpendicular[0], base[1] - perpendicular[1]),
            )
        ),
        stroke=tokens.colors["existing"].value,
        line_width=2.4,
    )


def build(content: FigureContent, tokens: VisualTokens) -> Scene:
    """Render the October 2026-October 2030 calendar as workstream swimlanes."""
    if content.figure_id != "fig-09":
        raise ValueError("Figure 9 builder requires fig-09 content")

    navy = tokens.colors["existing"].value
    orange = tokens.colors["human_judgment"].value
    grey = tokens.colors["conditional"].value
    neutral = tokens.colors["neutral_fill"].value
    white = tokens.colors["background"].value
    plan = content.items
    semesters = plan["semesters"]
    readiness = plan["readiness_gates"]
    medical_option = plan["conditional_medical_option"]

    scene_width, scene_height = 1600.0, 1004.0
    left = 26.0
    lane_label_width = 338.0
    timeline_x = left + lane_label_width + 10.0
    timeline_width = scene_width - timeline_x - 26.0
    preparatory_width = timeline_width / 4.0
    main_x = timeline_x + preparatory_width
    semester_width = (timeline_width - preparatory_width) / 6.0
    header_top, schedule_top = 68.0, 252.0
    lane_height = 52.0
    medical_height = 62.0

    elements: list[object] = [
        Text(left, 12, content.title, 45, max_width=1548, weight="bold", leading=1.0),
        Group(
            elements=(
                Rect(
                    timeline_x,
                    header_top,
                    preparatory_width,
                    schedule_top - header_top - 7,
                    fill=neutral,
                    stroke=grey,
                    dash="dashed",
                    label=plan["preparatory_label"],
                ),
                Text(
                    timeline_x + 14,
                    78,
                    plan["preparatory_label"],
                    31,
                    max_width=preparatory_width - 28,
                    weight="bold",
                    semantic_role="boundary-note",
                    leading=1.0,
                ),
                Text(
                    timeline_x + 14,
                    175,
                    plan["preparatory_period"],
                    35,
                    max_width=preparatory_width - 28,
                    weight="bold",
                    leading=1.0,
                ),
            ),
            semantic_role="preparatory-band",
            metadata=(
                ("role", "preparatory-band"),
                ("period", plan["preparatory_period"]),
                ("outside_three_year_count", str(plan["preparatory_outside_count"]).lower()),
            ),
        ),
        Rect(
            main_x,
            header_top,
            6 * semester_width,
            34,
            fill=navy,
            stroke=navy,
            label=plan["counted_plan_label"],
        ),
        Text(
            main_x + 14,
            68,
            f"{plan['counted_plan_label']} | {plan['main_period']}",
            35,
            max_width=6 * semester_width - 28,
            fill=white,
            background=navy,
            weight="bold",
            leading=1.0,
        ),
    ]

    for year_index, label in enumerate(plan["year_labels"]):
        year_x = main_x + 2 * year_index * semester_width
        elements.append(
            Group(
                elements=(
                    Rect(
                        year_x,
                        102,
                        2 * semester_width,
                        35,
                        fill=neutral,
                        stroke=grey,
                        label=label,
                    ),
                    Text(
                        year_x + 12,
                        102,
                        label,
                        35,
                        max_width=2 * semester_width - 24,
                        weight="bold",
                        leading=1.0,
                    ),
                ),
                semantic_role="year-band",
                metadata=(
                    ("role", "year-band"),
                    ("year", label),
                    (
                        "semesters",
                        "|".join(
                            semesters[2 * year_index + offset]["semester"] for offset in range(2)
                        ),
                    ),
                ),
            )
        )

    for index, semester in enumerate(semesters):
        x = main_x + index * semester_width
        fill = white if index % 2 == 0 else neutral
        elements.append(
            Group(
                elements=(
                    Rect(
                        x,
                        137,
                        semester_width,
                        schedule_top - 137,
                        fill=fill,
                        stroke=grey,
                        line_width=0.8,
                        label=semester["period"],
                    ),
                    Text(
                        x + 10,
                        143,
                        f"S{index + 1}",
                        35,
                        max_width=semester_width - 20,
                        background=fill,
                        weight="bold",
                        leading=1.0,
                    ),
                    Text(
                        x + 10,
                        181,
                        semester["period"],
                        35,
                        max_width=semester_width - 20,
                        background=fill,
                        semantic_role="semester-date",
                        leading=1.0,
                    ),
                ),
                semantic_role="semester-band",
                metadata=(
                    ("role", "semester-band"),
                    ("semester", semester["semester"]),
                    ("period", semester["period"]),
                ),
            )
        )

    lane_y: dict[str, float] = {}
    lane_heights: dict[str, float] = {}
    next_lane_y = schedule_top
    for label in plan["workstreams"]:
        y = next_lane_y
        current_lane_height = 75.0 if label == "Publications" else lane_height
        lane_y[label] = y
        lane_heights[label] = current_lane_height
        cells = tuple(
            Rect(
                main_x + semester_index * semester_width,
                y,
                semester_width,
                current_lane_height,
                fill=white if semester_index % 2 == 0 else neutral,
                stroke=grey,
                line_width=0.8,
                label=f"{label}, S{semester_index + 1}",
            )
            for semester_index in range(6)
        )
        elements.append(
            Group(
                elements=(
                    Rect(
                        left,
                        y,
                        lane_label_width,
                        current_lane_height,
                        fill=neutral,
                        stroke=grey,
                        line_width=0.8,
                        label=label,
                    ),
                    Text(
                        left + 9,
                        y + 8,
                        label,
                        35,
                        max_width=lane_label_width - 18,
                        weight="bold",
                        semantic_role="workstream-label",
                        leading=1.0,
                    ),
                    *cells,
                ),
                semantic_role="workstream-lane",
                metadata=(("role", "workstream-lane"), ("label", label)),
            )
        )
        next_lane_y += current_lane_height

    bar_geometry: dict[str, tuple[float, float, float, float]] = {}
    for activity in plan["activity_bars"]:
        start_index = activity["start_semester"] - 1
        end_index = activity["end_semester"]
        x = main_x + start_index * semester_width + 8
        y = lane_y[activity["lane"]] + 8
        width = (end_index - start_index) * semester_width - 16
        height = lane_heights[activity["lane"]] - 16
        bar_geometry[activity["lane"]] = (x, y, width, height)
        elements.append(
            Group(
                elements=(
                    RoundedRect(
                        x,
                        y,
                        width,
                        height,
                        radius=7,
                        fill=orange,
                        stroke=orange,
                        label=activity["label"],
                    ),
                    Text(
                        x + 6,
                        y,
                        activity["label"],
                        35,
                        max_width=width - 12,
                        fill=white,
                        background=orange,
                        weight="bold",
                        leading=1.0,
                    ),
                ),
                semantic_role="schedule-bar",
                metadata=(
                    ("role", "schedule-bar"),
                    ("lane", activity["lane"]),
                    ("start_semester", str(activity["start_semester"])),
                    ("end_semester", str(activity["end_semester"])),
                ),
            )
        )

    dependency_pairs = (
        ("Study 1", "Study 2"),
        ("Study 2", "Study 3"),
        ("Study 3", "Integrated evaluation"),
    )
    for source, target in dependency_pairs:
        source_x, source_y, source_width, source_height = bar_geometry[source]
        target_x, target_y, _, target_height = bar_geometry[target]
        gutter_x = (source_x + source_width + target_x) / 2
        points = (
            (source_x + source_width, source_y + source_height / 2),
            (gutter_x, source_y + source_height / 2),
            (gutter_x, target_y + target_height / 2),
            (target_x, target_y + target_height / 2),
        )
        elements.append(
            Group(
                elements=(_arrow(points, tokens),),
                semantic_role="dependency",
                metadata=(
                    ("role", "dependency"),
                    ("from", source),
                    ("to", target),
                    ("critical_path", "true"),
                ),
            )
        )

    publications_y = lane_y["Publications"]
    paper_milestones = (
        ("Paper 1", "Sep 2028", 2, publications_y + 4),
        ("Paper 2", "Sep 2029", 4, publications_y + 4),
        ("Paper 3", "Mar 2030", 5, publications_y + 4),
        ("defence", "Oct 2030", 6, publications_y + 41),
    )
    for label, date, semester_index, y in paper_milestones:
        boundary_x = main_x + semester_index * semester_width
        diamond_x = min(boundary_x - 13, main_x + 6 * semester_width - 29)
        label_x = diamond_x + 31 if label != "defence" else diamond_x - 118
        elements.append(
            Group(
                elements=(
                    Diamond(
                        diamond_x,
                        y,
                        26,
                        26,
                        fill=white,
                        stroke=navy,
                        label=label,
                    ),
                    Text(
                        label_x,
                        y - 1,
                        label,
                        35,
                        max_width=118,
                        weight="bold",
                        semantic_role="milestone-label",
                        leading=1.0,
                    ),
                ),
                semantic_role="milestone",
                metadata=(
                    ("role", "milestone"),
                    ("label", label),
                    ("date", date),
                    ("semester_index", str(semester_index)),
                ),
            )
        )

    medical_y = next_lane_y
    medical_start = main_x + 4 * semester_width
    elements.append(
        Group(
            elements=(
                Rect(
                    left,
                    medical_y,
                    lane_label_width,
                    medical_height,
                    fill=neutral,
                    stroke=grey,
                    dash="dashed",
                    label=medical_option["label"],
                ),
                Text(
                    left + 12,
                    medical_y + 14,
                    "Conditional medical",
                    31,
                    max_width=lane_label_width - 24,
                    weight="bold",
                    semantic_role="boundary-note",
                    leading=1.0,
                ),
                Rect(
                    main_x,
                    medical_y,
                    6 * semester_width,
                    medical_height,
                    fill=white,
                    stroke=grey,
                    dash="dashed",
                    label=medical_option["label"],
                ),
                RoundedRect(
                    medical_start + 20,
                    medical_y + 10,
                    2 * semester_width - 28,
                    medical_height - 20,
                    radius=7,
                    fill=neutral,
                    stroke=grey,
                    dash="dashed",
                    label=medical_option["label"],
                ),
                Text(
                    medical_start + 31,
                    medical_y + 14,
                    "Medical 0/6",
                    35,
                    max_width=2 * semester_width - 50,
                    weight="bold",
                    leading=1.0,
                ),
            ),
            semantic_role="conditional-medical-option",
            metadata=(
                ("role", "conditional-medical-option"),
                ("critical_path", str(medical_option["critical_path"]).lower()),
                ("start", "Oct 2029"),
                ("end", "Sep 2030"),
                ("readiness", readiness["medical"]),
            ),
        )
    )
    decision_x = medical_start - 13
    elements.append(
        Group(
            elements=(
                Text(
                    main_x + 2 * semester_width - 22,
                    medical_y + 14,
                    medical_option["go_no_go"],
                    35,
                    max_width=2 * semester_width + 10,
                    weight="bold",
                    semantic_role="milestone-label",
                    leading=1.0,
                ),
                Diamond(
                    decision_x,
                    medical_y + 18,
                    26,
                    26,
                    fill=white,
                    stroke=grey,
                    dash="dashed",
                    label=medical_option["go_no_go"],
                ),
            ),
            semantic_role="milestone",
            metadata=(
                ("role", "milestone"),
                ("label", medical_option["go_no_go"]),
                ("date", "Sep 2029"),
                ("semester_index", "4"),
            ),
        )
    )

    readiness_y = medical_y + medical_height + 5
    elements.append(
        Text(
            left,
            readiness_y,
            readiness["note"],
            31,
            max_width=1548,
            semantic_role="supporting-note",
            leading=1.0,
        )
    )

    output_start_y = readiness_y + 36
    column_x = (left, 813.0)
    column_y = [output_start_y, output_start_y]
    card_width = 761.0
    for index, semester in enumerate(semesters):
        column = 0 if index < 3 else 1
        y = column_y[column]
        fill = neutral if index % 2 == 0 else white
        output_text = Text(
            column_x[column] + 64,
            y + 4,
            semester["output"],
            31,
            max_width=card_width - 76,
            background=fill,
            semantic_role="supporting-note",
            leading=1.0,
        )
        card_height = max(68.0, text_bounds(output_text)[3] + 8)
        elements.append(
            Group(
                elements=(
                    Rect(
                        column_x[column],
                        y,
                        card_width,
                        card_height,
                        fill=fill,
                        stroke=grey,
                        line_width=0.8,
                        label=semester["output"],
                    ),
                    Text(
                        column_x[column] + 10,
                        y + 4,
                        f"S{index + 1}",
                        35,
                        max_width=44,
                        background=fill,
                        weight="bold",
                        leading=1.0,
                    ),
                    output_text,
                ),
                semantic_role="table8-output",
                metadata=(
                    ("role", "table8-output"),
                    ("semester", semester["semester"]),
                    ("period", semester["period"]),
                    ("activity", semester["activity"]),
                    ("output", semester["output"]),
                ),
            )
        )
        column_y[column] = y + card_height + 4

    elements.append(
        Text(
            left,
            940,
            content.provenance,
            31,
            max_width=1548,
            semantic_role="provenance",
            leading=1.0,
        )
    )
    root = Group(
        elements=tuple(elements),
        semantic_role="figure-root",
        metadata=(
            ("role", "figure-root"),
            ("layout", "calendar-workstream-swimlane"),
            ("timeline_start", "Oct 2026"),
            ("timeline_end", "Oct 2030"),
            ("preparatory_period", plan["preparatory_period"]),
            ("main_period", plan["main_period"]),
            ("preparatory_in_three_year_count", "false"),
            ("medical_readiness", readiness["medical"]),
            ("exp005_readiness", readiness["exp005"]),
        ),
    )
    return Scene(
        width=scene_width,
        height=scene_height,
        title=content.title,
        description=content.alt_text,
        elements=(root,),
    )
