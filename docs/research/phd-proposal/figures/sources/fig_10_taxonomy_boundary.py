"""Figure 10: a 40/60 boundary between taxonomy coverage and proposal needs."""

from __future__ import annotations

from proposal_visuals.content import FigureContent
from proposal_visuals.model import Group, Rect, Scene, Text
from proposal_visuals.tokens import VisualTokens


def build(content: FigureContent, tokens: VisualTokens) -> Scene:
    """Contrast four taxonomy branches with eleven ordered missing concepts."""
    if content.figure_id != "fig-10":
        raise ValueError("Figure 10 builder requires fig-10 content")

    navy = tokens.colors["existing"].value
    orange = tokens.colors["human_judgment"].value
    grey = tokens.colors["conditional"].value
    neutral = tokens.colors["neutral_fill"].value
    white = tokens.colors["background"].value

    scene_width, scene_height = 2100.0, 1295.0
    margin, column_gap = 30.0, 30.0
    usable_width = scene_width - 2 * margin - column_gap
    left_width = usable_width * 0.4
    right_width = usable_width * 0.6
    left_x = margin
    right_x = left_x + left_width + column_gap
    panel_y, panel_height = 116.0, 1092.0
    row_y, row_height, row_step = 174.0, 93.0, 94.0

    elements: list[object] = [
        Text(margin, 10, content.title, 54, max_width=2040, weight="bold", leading=1.0),
        Text(
            margin,
            68,
            content.provenance,
            40,
            max_width=2040,
            semantic_role="provenance",
            leading=1.0,
        ),
        Group(
            elements=(
                Rect(
                    left_x,
                    panel_y,
                    left_width,
                    panel_height,
                    fill=neutral,
                    stroke=navy,
                    label="taxonomy coverage column",
                ),
            ),
            semantic_role="taxonomy-column",
            metadata=(
                ("role", "taxonomy-column"),
                ("share", "40%"),
                ("branch_count", "4"),
            ),
        ),
        Group(
            elements=(
                Rect(
                    right_x,
                    panel_y,
                    right_width,
                    panel_height,
                    fill=white,
                    stroke=orange,
                    label="proposal concept column",
                ),
            ),
            semantic_role="concept-column",
            metadata=(
                ("role", "concept-column"),
                ("share", "60%"),
                ("concept_count", "11"),
                ("ordering", "table-11"),
            ),
        ),
        Text(
            left_x + 20,
            126,
            "What the taxonomy covers",
            46,
            max_width=left_width - 40,
            weight="bold",
            leading=1.0,
        ),
        Text(
            right_x + 20,
            126,
            "What this proposal needs but the taxonomy cannot express",
            46,
            max_width=right_width - 40,
            weight="bold",
            leading=1.0,
        ),
    ]

    branch_card_y = (201.0, 367.0, 533.0, 699.0)
    for index, (label, y) in enumerate(
        zip(content.items["taxonomy_branches"], branch_card_y, strict=True), start=1
    ):
        elements.append(
            Group(
                elements=(
                    Rect(
                        left_x + 28,
                        y,
                        left_width - 56,
                        140,
                        fill=navy,
                        stroke=navy,
                        label=label,
                    ),
                    Text(
                        left_x + 50,
                        y + 20,
                        f"{index:02d}",
                        46,
                        max_width=72,
                        fill=white,
                        background=navy,
                        weight="bold",
                        leading=1.0,
                    ),
                    Text(
                        left_x + 135,
                        y + 20,
                        label,
                        46,
                        max_width=left_width - 205,
                        fill=white,
                        background=navy,
                        weight="bold",
                        leading=1.0,
                    ),
                ),
                semantic_role="taxonomy-branch",
                metadata=(
                    ("role", "taxonomy-branch"),
                    ("order", str(index)),
                    ("label", label),
                ),
            )
        )

    elements.extend(
        (
            Text(
                left_x + 28,
                879,
                "4 established branches",
                46,
                max_width=left_width - 56,
                weight="bold",
                leading=1.0,
            ),
            Text(
                left_x + 28,
                941,
                "The asymmetry is the argument about taxonomy coverage: four interaction branches versus eleven proposal-derived concepts.",
                40,
                max_width=left_width - 56,
                semantic_role="boundary-note",
                leading=1.0,
            ),
        )
    )

    for index, label in enumerate(content.items["missing_concepts"], start=1):
        y = row_y + (index - 1) * row_step
        fill = neutral if index % 2 == 0 else white
        elements.append(
            Group(
                elements=(
                    Rect(
                        right_x + 12,
                        y,
                        right_width - 24,
                        row_height,
                        fill=fill,
                        stroke=orange,
                        line_width=0.8,
                        label=label,
                    ),
                    Text(
                        right_x + 28,
                        y + 23,
                        f"{index:02d}",
                        46,
                        max_width=58,
                        background=fill,
                        weight="bold",
                        leading=1.0,
                    ),
                    Text(
                        right_x + 92,
                        y,
                        label,
                        46,
                        max_width=right_width - 116,
                        background=fill,
                        leading=1.0,
                    ),
                ),
                semantic_role="missing-concept",
                metadata=(
                    ("role", "missing-concept"),
                    ("order", str(index)),
                    ("label", label),
                ),
            )
        )

    elements.extend(
        (
            Rect(
                margin,
                1210,
                scene_width - 2 * margin,
                80,
                fill=neutral,
                stroke=grey,
                dash="dashed",
                label="claim scope",
            ),
            Text(
                margin + 14,
                1210,
                content.items["claim_scope"],
                40,
                max_width=scene_width - 2 * margin - 28,
                weight="bold",
                semantic_role="boundary-note",
                leading=1.0,
            ),
        )
    )
    root = Group(
        elements=tuple(elements),
        semantic_role="figure-root",
        metadata=(
            ("role", "figure-root"),
            ("layout", "two-column-taxonomy-boundary"),
            ("left_share", "40%"),
            ("right_share", "60%"),
            ("claim_scope", "coverage-not-necessity-or-effectiveness"),
        ),
    )
    return Scene(
        width=scene_width,
        height=scene_height,
        title=content.title,
        description=content.alt_text,
        elements=(root,),
    )
