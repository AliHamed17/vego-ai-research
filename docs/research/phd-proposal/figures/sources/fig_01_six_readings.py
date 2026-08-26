"""Figure 1: six equal readings of a single observed model difference."""

from __future__ import annotations

from proposal_visuals.content import FigureContent
from proposal_visuals.model import (
    Arrowhead,
    Cylinder,
    Diamond,
    Group,
    Parallelogram,
    Polyline,
    Rect,
    RoundedRect,
    Scene,
    Text,
)
from proposal_visuals.tokens import VisualTokens


def _down_arrow(points: tuple[tuple[float, float], ...], tokens: VisualTokens) -> Polyline:
    end_x, end_y = points[-1]
    return Polyline(
        points=points,
        arrowhead=Arrowhead(((end_x, end_y), (end_x - 5, end_y - 8), (end_x + 5, end_y - 8))),
        stroke=tokens.colors["existing"].value,
        line_width=tokens.line_width,
    )


def build(content: FigureContent, tokens: VisualTokens) -> Scene:
    """Build the non-hierarchical six-reading fanout from frozen §1.7 wording."""
    if content.figure_id != "fig-01":
        raise ValueError("Figure 1 builder requires fig-01 content")

    ink = tokens.colors["ink"].value
    existing = tokens.colors["existing"].value
    neutral = tokens.colors["neutral_fill"].value
    white = tokens.colors["background"].value
    cards = ((15, 132), (330, 132), (645, 132), (15, 270), (330, 270), (645, 270))
    elements: list[object] = [
        Group(
            elements=(),
            semantic_role="figure-metadata",
            metadata=(("origin-count", "1"), ("figure", "1")),
        ),
        Text(15, 12, content.title, 28, max_width=700, weight="bold"),
        Rect(345, 52, 270, 52, fill=existing, stroke=existing, label="observed fragment"),
        Text(
            365,
            58,
            "Observed fragment\nShift Supervisor actor",
            21,
            max_width=230,
            leading=1.0,
            fill=white,
            background=existing,
            weight="bold",
        ),
    ]
    routes = (
        ((390, 106), (390, 116), (165, 116), (165, 126)),
        ((480, 106), (480, 126)),
        ((570, 106), (570, 116), (795, 116), (795, 126)),
        ((390, 106), (8, 106), (8, 258), (165, 258), (165, 264)),
        ((480, 106), (322, 106), (322, 258), (480, 258), (480, 264)),
        ((570, 106), (952, 106), (952, 258), (795, 258), (795, 264)),
    )
    for index, ((x, y), reading, route) in enumerate(
        zip(cards, content.items["readings"], routes, strict=True)
    ):
        target_x = x + 150
        if route[-1][0] != target_x:
            raise ValueError("reading route must terminate over its target card")
        elements.append(
            Group(
                elements=(
                    _down_arrow(route, tokens),
                    Rect(
                        x,
                        y,
                        300,
                        118,
                        fill=neutral,
                        stroke=ink,
                        label=f"reading {index + 1}",
                    ),
                    Text(x + 9, y + 8, f"Reading {index + 1}", 20.8, max_width=282, weight="bold"),
                    Text(x + 9, y + 31, reading, 20.8, max_width=282, leading=1.0),
                ),
                semantic_role="reading-branch",
                metadata=(
                    ("role", "reading-branch"),
                    ("edge-width", str(tokens.line_width)),
                    ("column", str(index % 3 + 1)),
                    ("row", str(index // 3 + 1)),
                ),
            )
        )
    elements.extend(
        (
            Text(
                15,
                394,
                "the artifact is identical under all six",
                20.8,
                max_width=520,
                weight="bold",
            ),
            Text(735, 394, "Visual language", 20.8, max_width=210, weight="bold"),
            Group(
                elements=(
                    RoundedRect(15, 425, 20, 16, radius=4, fill=neutral, stroke=ink),
                    Text(
                        45,
                        420,
                        "Rounded rectangle: process or agent",
                        20.8,
                        max_width=205,
                        leading=1.0,
                    ),
                    Polyline(
                        points=((259, 433), (279, 433)),
                        arrowhead=Arrowhead(((279, 433), (271, 428), (271, 438))),
                        stroke=existing,
                        line_width=tokens.line_width,
                    ),
                    Text(
                        285,
                        420,
                        "Solid: committed or existing flow",
                        20.8,
                        max_width=205,
                        leading=1.0,
                    ),
                    Rect(495, 425, 20, 16, fill=existing, stroke=existing),
                    Text(
                        525,
                        420,
                        "Navy: existing VEGO-AI baseline",
                        20.8,
                        max_width=205,
                        leading=1.0,
                    ),
                    Diamond(735, 423, 20, 20, fill=white, stroke=ink),
                    Text(
                        765, 420, "Diamond: decision or milestone", 20.8, max_width=180, leading=1.0
                    ),
                    Parallelogram(15, 474, 20, 16, skew=4, fill=white, stroke=ink),
                    Text(
                        45,
                        468,
                        "Parallelogram: human-judgment input",
                        20.8,
                        max_width=205,
                        leading=1.0,
                    ),
                    Polyline(
                        points=((259, 482), (279, 482)),
                        arrowhead=Arrowhead(((279, 482), (271, 477), (271, 487))),
                        stroke=ink,
                        line_width=tokens.line_width,
                        dash="dashed",
                    ),
                    Text(
                        285,
                        468,
                        "Dashed: conditional, proposed, or gated flow",
                        20.8,
                        max_width=205,
                        leading=1.0,
                    ),
                    Rect(
                        495,
                        474,
                        20,
                        16,
                        fill=tokens.colors["human_judgment"].value,
                        stroke=tokens.colors["human_judgment"].value,
                    ),
                    Text(
                        525,
                        468,
                        "Orange: proposed doctoral human-judgment layer",
                        20.8,
                        max_width=205,
                        leading=1.0,
                    ),
                    Cylinder(735, 472, 20, 20, fill=white, stroke=ink),
                    Text(765, 468, "Cylinder: store", 20.8, max_width=180, leading=1.0),
                    Rect(15, 540, 20, 16, fill=neutral, stroke=ink),
                    Text(
                        45, 535, "Rectangle: artifact or record", 20.8, max_width=205, leading=1.0
                    ),
                    Polyline(
                        points=((259, 548), (279, 548)),
                        arrowhead=Arrowhead(((279, 548), (271, 543), (271, 553))),
                        stroke=ink,
                        line_width=tokens.line_width,
                        dash="dotted",
                    ),
                    Text(
                        285, 535, "Dotted: information reference", 20.8, max_width=205, leading=1.0
                    ),
                    Rect(
                        495,
                        540,
                        20,
                        16,
                        fill=tokens.colors["conditional"].value,
                        stroke=tokens.colors["conditional"].value,
                    ),
                    Text(
                        525,
                        535,
                        "Cool grey: conditional, gated, or out of scope",
                        20.8,
                        max_width=205,
                        leading=1.0,
                    ),
                ),
                semantic_role="visual-language-legend",
                metadata=(("role", "visual-language-legend"),),
            ),
            Text(
                15,
                588,
                content.provenance,
                18.2,
                max_width=930,
                leading=1.0,
                semantic_role="provenance",
            ),
        )
    )
    return Scene(
        width=960,
        height=630,
        title=content.title,
        description=content.alt_text,
        elements=tuple(elements),
    )
