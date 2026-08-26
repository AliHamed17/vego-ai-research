"""Figure 3: established streams, an explicitly unclosed residual gap, and SQ mapping."""

from __future__ import annotations

import math

from proposal_visuals.content import FigureContent
from proposal_visuals.model import Arrowhead, Group, Polyline, Rect, RoundedRect, Scene, Text
from proposal_visuals.tokens import VisualTokens


def _arrow(
    points: tuple[tuple[float, float], ...], tokens: VisualTokens, dash: str = "solid"
) -> Polyline:
    previous, (end_x, end_y) = points[-2:]
    direction_x, direction_y = end_x - previous[0], end_y - previous[1]
    length = math.hypot(direction_x, direction_y)
    if length == 0:
        raise ValueError("arrow final segment must have length")
    unit_x, unit_y = direction_x / length, direction_y / length
    base_x, base_y = end_x - 8 * unit_x, end_y - 8 * unit_y
    perpendicular_x, perpendicular_y = -5 * unit_y, 5 * unit_x
    return Polyline(
        points=points,
        arrowhead=Arrowhead(
            (
                (end_x, end_y),
                (base_x + perpendicular_x, base_y + perpendicular_y),
                (base_x - perpendicular_x, base_y - perpendicular_y),
            )
        ),
        stroke=tokens.colors["existing"].value,
        line_width=tokens.line_width,
        dash=dash,
    )


def build(content: FigureContent, tokens: VisualTokens) -> Scene:
    """Build an open problem framing rather than an implied closed solution."""
    if content.figure_id != "fig-03":
        raise ValueError("Figure 3 builder requires fig-03 content")

    ink = tokens.colors["ink"].value
    existing = tokens.colors["existing"].value
    conditional = tokens.colors["conditional"].value
    white = tokens.colors["background"].value
    streams = content.items["streams"]
    elements: list[object] = [Text(20, 14, content.title, 27, max_width=760, weight="bold")]
    for index, (label, x) in enumerate(zip(streams, (5, 164, 323, 482, 641), strict=True)):
        target_x = 200 + index * 100
        elements.append(
            Group(
                elements=(
                    RoundedRect(
                        x, 62, 154, 82, radius=7, fill=white, stroke=existing, label=label
                    ),
                    Text(x + 8, 70, label, 18, max_width=138, leading=1.0, weight="bold"),
                    _arrow(
                        ((x + 77, 147), (x + 77, 156), (target_x, 166)), tokens
                    ),
                ),
                semantic_role="established-stream",
                metadata=(("role", "established-stream"), ("stream", str(index + 1))),
            )
        )
    elements.append(
        Group(
            elements=(
                Rect(
                    160,
                    172,
                    480,
                    68,
                    fill=white,
                    stroke=conditional,
                    dash="dashed",
                    label="residual gap",
                ),
                Text(
                    183,
                    183,
                    "Residual opening: claim-level integration\nunder contested authority",
                    18,
                    max_width=434,
                    leading=1.0,
                    weight="bold",
                ),
            ),
            semantic_role="residual-gap",
            metadata=(("role", "residual-gap"), ("fill", "unfilled"), ("line-style", "dashed")),
        )
    )
    for index, gap in enumerate(content.items["gaps"]):
        y = 264 + index * 82
        sq = f"SQ{index + 1}"
        elements.append(
            Group(
                elements=(
                    Text(20, y + 8, gap, 18, max_width=420, leading=1.0),
                    _arrow(((448, y + 30), (500, y + 30)), tokens),
                    RoundedRect(510, y, 108, 60, radius=6, fill=white, stroke=ink, label=sq),
                    Text(537, y + 18, sq, 20, max_width=54, weight="bold"),
                ),
                semantic_role="gap-to-sq",
                metadata=(("role", "gap-to-sq"), ("sq", sq)),
            )
        )
    elements.append(
        Group(
            elements=(
                RoundedRect(
                    650,
                    296,
                    132,
                    188,
                    radius=7,
                    fill=white,
                    stroke=conditional,
                    dash="dashed",
                    label="umbrella question",
                ),
                Text(
                    666,
                    340,
                    "Umbrella question:\nintegrated evaluation",
                    18,
                    max_width=100,
                    leading=1.0,
                    weight="bold",
                ),
                Group(
                    elements=(
                        _arrow(
                            ((620, 294), (634, 294), (634, 332), (645, 332)), tokens, dash="dotted"
                        ),
                    ),
                    semantic_role="sq-reference",
                    metadata=(("role", "sq-reference"), ("source", "SQ1")),
                ),
                Group(
                    elements=(_arrow(((620, 376), (645, 376)), tokens, dash="dotted"),),
                    semantic_role="sq-reference",
                    metadata=(("role", "sq-reference"), ("source", "SQ2")),
                ),
                Group(
                    elements=(
                        _arrow(
                            ((620, 458), (634, 458), (634, 438), (645, 438)), tokens, dash="dotted"
                        ),
                    ),
                    semantic_role="sq-reference",
                    metadata=(("role", "sq-reference"), ("source", "SQ3")),
                ),
            ),
            semantic_role="umbrella-reference",
            metadata=(("role", "umbrella-reference"), ("line-style", "dotted")),
        )
    )
    elements.extend(
        (
            Text(
                20,
                505,
                "The opening remains open; integrated evaluation is proposed rather than established.",
                16,
                max_width=760,
                weight="bold",
                semantic_role="boundary-note",
            ),
            Text(
                20,
                535,
                content.provenance,
                16,
                max_width=760,
                leading=1.0,
                semantic_role="provenance",
            ),
        )
    )
    return Scene(
        width=800,
        height=600,
        title=content.title,
        description=content.alt_text,
        elements=tuple(elements),
    )
