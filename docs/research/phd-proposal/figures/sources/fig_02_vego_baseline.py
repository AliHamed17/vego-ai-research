"""Figure 2: the reported VEGO-AI four-agent baseline and a separate attachment band."""

from __future__ import annotations

from proposal_visuals.content import FigureContent
from proposal_visuals.model import Arrowhead, Group, Polyline, RoundedRect, Scene, Text
from proposal_visuals.tokens import VisualTokens


def _right_arrow(start_x: float, y: float, end_x: float, tokens: VisualTokens) -> Polyline:
    return Polyline(
        points=((start_x, y), (end_x, y)),
        arrowhead=Arrowhead(((end_x, y), (end_x - 8, y - 5), (end_x - 8, y + 5))),
        stroke=tokens.colors["existing"].value,
        line_width=tokens.line_width,
    )


def build(content: FigureContent, tokens: VisualTokens) -> Scene:
    """Build a left-to-right baseline without portraying the doctoral band as deployed."""
    if content.figure_id != "fig-02":
        raise ValueError("Figure 2 builder requires fig-02 content")

    existing = tokens.colors["existing"].value
    conditional = tokens.colors["conditional"].value
    white = tokens.colors["background"].value
    positions = (30, 250, 470, 690)
    elements: list[object] = [Text(30, 18, content.title, 30, max_width=840, weight="bold")]
    for x, agent in zip(positions, content.items["agents"], strict=True):
        elements.append(
            Group(
                elements=(
                    RoundedRect(
                        x, 112, 180, 76, radius=8, fill=existing, stroke=existing, label=agent
                    ),
                    Text(
                        x + 14,
                        137,
                        agent,
                        20,
                        max_width=152,
                        fill=white,
                        background=existing,
                        weight="bold",
                    ),
                ),
                semantic_role="baseline-agent",
                metadata=(("role", "baseline-agent"), ("label", agent)),
            )
        )
    artifact_positions = ((30, 72), (250, 72), (470, 62), (690, 72))
    for (x, y), label in zip(artifact_positions, content.items["artifacts"], strict=True):
        elements.append(Text(x, y, label, 20, max_width=180, leading=1.0, weight="bold"))
    for start_x, end_x in zip((210, 430, 650), (250, 470, 690), strict=True):
        elements.append(_right_arrow(start_x, 150, end_x, tokens))
    elements.append(
        Group(
            elements=(
                Polyline(
                    points=((780, 190), (780, 232), (340, 232), (340, 191)),
                    arrowhead=Arrowhead(((340, 191), (334, 201), (346, 201))),
                    stroke=existing,
                    line_width=tokens.line_width,
                ),
                Text(470, 238, "refinement loop", 20, max_width=180, weight="bold"),
            ),
            semantic_role="refinement-loop",
            metadata=(
                ("role", "refinement-loop"),
                ("from", "Variability Explorer"),
                ("to", "Domain Advisor"),
            ),
        )
    )
    elements.append(
        Group(
            elements=(
                RoundedRect(
                    30,
                    280,
                    840,
                    100,
                    radius=8,
                    fill=white,
                    stroke=conditional,
                    dash="dashed",
                    label="doctoral attachment",
                ),
                Text(
                    54,
                    296,
                    "Proposed doctoral human-judgment attachment — outside the baseline",
                    20,
                    max_width=760,
                    weight="bold",
                ),
                Text(
                    54,
                    333,
                    "Attachment is developed later; it is not a reported baseline capability.",
                    20,
                    max_width=740,
                ),
            ),
            semantic_role="doctoral-attachment",
            metadata=(("role", "doctoral-attachment"), ("line-style", "dashed")),
        )
    )
    elements.append(
        Text(
            30,
            410,
            content.provenance,
            20,
            max_width=840,
            leading=1.0,
            semantic_role="provenance",
        )
    )
    return Scene(
        width=900,
        height=460,
        title=content.title,
        description=content.alt_text,
        elements=tuple(elements),
    )
