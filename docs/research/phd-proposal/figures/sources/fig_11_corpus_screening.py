"""Figure 11: standalone corpus-screening candidate with separate RQ coverage."""

from __future__ import annotations

from proposal_visuals.content import FigureContent
from proposal_visuals.model import Group, Rect, Scene, Text
from proposal_visuals.tokens import VisualTokens


def build(content: FigureContent, tokens: VisualTokens) -> Scene:
    """Draw paper-level dispositions separately from research-question-level coverage."""
    if content.figure_id != "fig-11":
        raise ValueError("Figure 11 builder requires fig-11 content")

    navy = tokens.colors["existing"].value
    grey = tokens.colors["conditional"].value
    neutral = tokens.colors["neutral_fill"].value
    white = tokens.colors["background"].value
    dispositions = content.items["paper_disposition"]
    total, x, width, y = content.items["paper_total"], 80, 1060, 132
    elements: list[object] = [
        Text(28, 24, content.title, 26, max_width=1120, weight="bold"),
        Text(80, 88, content.items["paper_disposition_heading"], 21, max_width=720, weight="bold"),
    ]
    cursor = x
    treatments = ((navy, navy, None), (neutral, grey, "diagonal"), (white, grey, None))
    for (label, count), (fill, stroke, hatch) in zip(dispositions.items(), treatments, strict=True):
        segment_width = width * count / total
        bar_label = f"{label}: {count}" if segment_width >= 160 else str(count)
        segment_elements: list[object] = [
            Rect(
                cursor,
                y,
                segment_width,
                68,
                fill=fill,
                stroke=stroke,
                hatch=hatch,
                label=label,
            )
        ]
        if label == "Less relevant":
            segment_elements.append(
                Rect(
                    cursor + 6,
                    y + 17,
                    180,
                    30,
                    fill=neutral,
                    stroke=neutral,
                    line_width=0.7,
                    semantic_role="label-background",
                )
            )
        segment_elements.append(
            Text(
                cursor + 10,
                y + 22,
                bar_label,
                19,
                max_width=segment_width - 20,
                fill=white if label == "Relevant" else navy,
                background=fill,
                weight="bold",
            )
        )
        elements.append(
            Group(
                elements=tuple(segment_elements),
                semantic_role="paper-disposition",
                metadata=(
                    ("role", "paper-disposition"),
                    ("label", label),
                    ("count", str(count)),
                    (
                        "encoding",
                        "label+diagonal-hatch+muted-tone"
                        if label == "Less relevant"
                        else "label+solid+existing-tone"
                        if label == "Relevant"
                        else "label+plain+muted-tone",
                    ),
                ),
            )
        )
        cursor += segment_width
    elements.append(Text(80, 206, "Not relevant: 5", 19, max_width=260, weight="bold"))
    elements.append(
        Text(80, 240, content.items["rq_coverage_heading"], 21, max_width=900, weight="bold")
    )
    for index, (rq, coverage) in enumerate(content.items["rq_coverage"].items()):
        x_card = 80 + index * 275
        if coverage == "Yes":
            fill, stroke, texture = navy, navy, "solid"
            text_fill, text_background = white, navy
        elif coverage == "Partly":
            fill, stroke, texture = white, grey, "diagonal-hatch"
            text_fill, text_background = navy, white
        else:
            fill, stroke, texture = neutral, grey, "dotted-border"
            text_fill, text_background = navy, neutral
        card_elements: list[object] = [
            Rect(
                x_card,
                282,
                230,
                120,
                fill=fill,
                stroke=stroke,
                dash="dotted" if coverage == "No" else "solid",
                label=f"{rq} {coverage}",
            ),
            Text(
                x_card + 18,
                304,
                rq,
                21,
                max_width=190,
                fill=text_fill,
                background=text_background,
                weight="bold",
            ),
            Text(
                x_card + 18,
                340,
                coverage,
                25,
                max_width=190,
                fill=text_fill,
                background=text_background,
                weight="bold",
            ),
        ]
        texture_x = x_card + 18
        if coverage == "Partly":
            texture = "diagonal hatch"
            card_elements.append(
                Rect(
                    x_card + 18,
                    376,
                    24,
                    16,
                    fill=white,
                    stroke=grey,
                    hatch="diagonal",
                    semantic_role="status-texture",
                    label=f"{rq} partly texture",
                )
            )
            texture_x = x_card + 52
        card_elements.append(
            Text(
                texture_x,
                375,
                texture,
                19,
                max_width=156 if coverage == "Partly" else 190,
                fill=text_fill,
                background=text_background,
            )
        )
        elements.append(
            Group(
                elements=tuple(card_elements),
                semantic_role="rq-coverage",
                metadata=(
                    ("role", "rq-coverage"),
                    ("rq", rq),
                    ("coverage", coverage),
                    (
                        "encoding",
                        "text+diagonal-hatch+muted-tone"
                        if coverage == "Partly"
                        else "text+solid+existing-tone"
                        if coverage == "Yes"
                        else "text+dotted-border+muted-tone",
                    ),
                ),
            )
        )
    elements.extend(
        (
            Text(
                80,
                454,
                content.items["missing_coverage_note"],
                17,
                max_width=1060,
                weight="bold",
                semantic_role="boundary-note",
            ),
            Text(
                80,
                486,
                content.items["screening_limit"],
                17,
                max_width=1060,
                semantic_role="supporting-note",
            ),
            Rect(
                80,
                524,
                1060,
                45,
                fill=neutral,
                stroke=grey,
                dash="dashed",
                label="standalone candidate",
            ),
            Text(
                98,
                536,
                content.items["standalone_status"],
                17,
                max_width=1000,
                weight="bold",
                semantic_role="boundary-note",
            ),
            Text(
                80,
                604,
                content.provenance,
                17,
                max_width=1060,
                leading=1.1,
                semantic_role="provenance",
            ),
        )
    )
    root = Group(
        elements=tuple(elements),
        semantic_role="figure-root",
        metadata=(
            ("role", "figure-root"),
            ("paper_total", str(total)),
            ("missing_level", content.items["missing_level"]),
            ("standalone_candidate", "true"),
        ),
    )
    return Scene(
        width=1200, height=650, title=content.title, description=content.alt_text, elements=(root,)
    )
