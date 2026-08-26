"""Figure 4: an aligned programme spine with a visibly consuming integrated evaluation."""

from __future__ import annotations

from proposal_visuals.content import FigureContent
from proposal_visuals.model import Arrowhead, Group, Polyline, Rect, Scene, Text
from proposal_visuals.tokens import VisualTokens


def _left_arrow(points: tuple[tuple[float, float], ...], tokens: VisualTokens) -> Polyline:
    end_x, end_y = points[-1]
    return Polyline(
        points=points,
        arrowhead=Arrowhead(((end_x, end_y), (end_x + 9, end_y - 5), (end_x + 9, end_y + 5))),
        stroke=tokens.colors["conditional"].value,
        line_width=tokens.line_width,
        dash="dashed",
    )


def build(content: FigureContent, tokens: VisualTokens) -> Scene:
    """Build the four-column, four-row programme matrix from the frozen proposal spine."""
    if content.figure_id != "fig-04":
        raise ValueError("Figure 4 builder requires fig-04 content")

    ink = tokens.colors["ink"].value
    neutral = tokens.colors["neutral_fill"].value
    white = tokens.colors["background"].value
    columns = tuple(
        zip((25, 205, 445, 680), (170, 230, 225, 255), content.items["columns"], strict=True)
    )
    row_specs = content.items["spine_rows"]
    integrated_arms = tuple(content.items["integrated_arms"])
    if len(integrated_arms) != 4:
        raise ValueError("Figure 4 requires exactly four integrated comparator arms")
    elements: list[object] = [Text(25, 12, content.title, 28, max_width=880, weight="bold")]
    for x, width, label in columns:
        elements.extend(
            (
                Rect(x, 50, width, 48, fill=neutral, stroke=ink, label=label),
                Text(x + 10, 61, label, 21, max_width=width - 20, leading=1.05, weight="bold"),
            )
        )
    row_groups: list[Group] = []
    row_y = (104, 174, 244, 314)
    for row_spec, y in zip(row_specs, row_y, strict=True):
        row_name = row_spec["row"]
        cells = row_spec["cells"]
        height = 70 if row_name != "Integrated" else 120
        fill = white if row_name != "Integrated" else neutral
        row_elements: list[object] = []
        for (x, width, _), label in zip(columns, cells, strict=True):
            row_elements.append(
                Rect(x, y, width, height, fill=fill, stroke=ink, label=label)
            )
            if row_name != "Integrated":
                row_elements.append(
                    Text(
                        x + 10,
                        y + 3,
                        label,
                        21,
                        max_width=width - 20,
                        leading=1.0,
                    )
                )
        if row_name == "Integrated":
            row_elements.extend(
                (
                    Text(35, y + 10, cells[0], 21, max_width=150, leading=1.0, weight="bold"),
                    Text(215, y + 8, cells[1], 21, max_width=210, leading=1.0, weight="bold"),
                    Text(215, y + 40, integrated_arms[0], 21, max_width=210, leading=1.0),
                    Text(215, y + 72, integrated_arms[1], 21, max_width=210, leading=1.0),
                    Text(455, y + 8, cells[2], 21, max_width=205, leading=1.0, weight="bold"),
                    Text(455, y + 38, integrated_arms[2], 21, max_width=205, leading=1.0),
                    Text(455, y + 85, integrated_arms[3], 21, max_width=205, leading=1.0),
                    Text(690, y + 10, cells[3], 21, max_width=235, leading=1.0, weight="bold"),
                )
            )
        metadata = [
            ("role", "spine-row"),
            ("row", row_name),
            ("treatment", "integrated" if row_name == "Integrated" else "component"),
        ]
        if row_name == "Integrated":
            metadata.extend(
                (
                    ("comparison", "four-arm"),
                    ("arms", "|".join(integrated_arms)),
                )
            )
        row_groups.append(
            Group(
                elements=tuple(row_elements),
                semantic_role="spine-row",
                metadata=tuple(metadata),
            )
        )
    elements.append(
        Group(
            elements=tuple(row_groups),
            semantic_role="programme-spine",
            metadata=(
                ("role", "programme-spine"),
                ("columns", "4"),
                ("rows", "SQ1|SQ2|SQ3|Integrated"),
            ),
        )
    )
    consumption_routes = (
        ((935, 136), (958, 136), (958, 370), (935, 370)),
        ((935, 206), (951, 206), (951, 351), (935, 351)),
        ((935, 276), (944, 276), (944, 332), (935, 332)),
    )
    for index, route in enumerate(consumption_routes, start=1):
        elements.append(
            Group(
                elements=(_left_arrow(route, tokens),),
                semantic_role="consumption-arrow",
                metadata=(
                    ("role", "consumption-arrow"),
                    ("source", f"SQ{index}"),
                    ("target", "Integrated"),
                ),
            )
        )
    elements.extend(
        (
            Text(
                25,
                447,
                content.items["integrated_boundary"],
                18.2,
                max_width=910,
                leading=1.05,
                semantic_role="boundary-note",
            ),
            Text(
                25,
                477,
                content.provenance,
                18.2,
                max_width=910,
                leading=1.05,
                semantic_role="provenance",
            ),
        )
    )
    return Scene(
        width=960,
        height=515,
        title=content.title,
        description=content.alt_text,
        elements=tuple(elements),
    )
