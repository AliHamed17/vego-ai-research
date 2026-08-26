"""Figure 5: a bounded review policy, not a claim of policy effectiveness."""

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
)
from proposal_visuals.tokens import VisualTokens


def _arrow(
    points: tuple[tuple[float, float], ...], tokens: VisualTokens, dash: str = "solid"
) -> Polyline:
    previous, endpoint = points[-2:]
    dx, dy = endpoint[0] - previous[0], endpoint[1] - previous[1]
    length = math.hypot(dx, dy)
    if length == 0:
        raise ValueError("arrow final segment must have length")
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
        stroke=(
            tokens.colors["conditional"].value
            if dash != "solid"
            else tokens.colors["existing"].value
        ),
        line_width=tokens.line_width,
        dash=dash,
    )


def build(content: FigureContent, tokens: VisualTokens) -> Scene:
    """Build a compact lateral signal-policy-action layout with hard-rule bypasses."""
    if content.figure_id != "fig-05":
        raise ValueError("Figure 5 builder requires fig-05 content")

    ink = tokens.colors["ink"].value
    existing = tokens.colors["existing"].value
    proposed = tokens.colors["human_judgment"].value
    conditional = tokens.colors["conditional"].value
    neutral = tokens.colors["neutral_fill"].value
    white = tokens.colors["background"].value
    elements: list[object] = [
        Text(20, 14, content.title, 30, max_width=1_120, weight="bold"),
        Text(20, 61, "Literature-derived signals (1–5)", 25, max_width=340, weight="bold"),
        Text(
            20,
            88,
            "Proposed signals (6–8, shaded)",
            22,
            max_width=340,
            semantic_role="supporting-note",
        ),
        Text(385, 61, "Matched attention constraint", 25, max_width=330, weight="bold"),
        Text(765, 61, "Equal routing actions", 25, max_width=370, weight="bold"),
    ]

    signal_y = (118, 177, 236, 295, 354, 413, 472, 531)
    signal_centres: list[float] = []
    for index, (label, y) in enumerate(zip(content.items["signals"], signal_y, strict=True)):
        source = "literature-derived" if index < 5 else "proposed"
        fill, stroke = (white, existing) if source == "literature-derived" else (neutral, proposed)
        centre_y = y + 27
        signal_centres.append(centre_y)
        elements.append(
            Group(
                elements=(
                    Rect(20, y, 300, 54, fill=fill, stroke=stroke, label=label),
                    Text(30, y + 2, label, 25, max_width=270, leading=1.0, weight="bold"),
                    _arrow(
                        ((320, centre_y), (345, centre_y)),
                        tokens,
                        "dashed" if source == "proposed" else "solid",
                    ),
                ),
                semantic_role="policy-signal",
                metadata=(
                    ("role", "policy-signal"),
                    ("label", label),
                    ("source", source),
                    ("source_id", f"signal-{index + 1}"),
                    ("target_id", "signal-input-bus"),
                ),
            )
        )

    elements.append(
        Group(
            elements=(
                _arrow(((345, signal_centres[0]), (345, signal_centres[-1])), tokens, "dotted"),
                _arrow(((345, 355), (385, 355)), tokens, "dotted"),
            ),
            semantic_role="shared-bus",
            metadata=(
                ("role", "shared-bus"),
                ("bus_id", "signal-input-bus"),
                ("source_ids", "|".join(f"signal-{index}" for index in range(1, 9))),
                ("target_id", "budget-constraint"),
                ("purpose", "eight-policy-signals-to-budget-constrained-review-policy"),
            ),
        )
    )

    constraint = content.items["constraint"]
    elements.append(
        Group(
            elements=(
                Rect(
                    385,
                    175,
                    320,
                    360,
                    fill=white,
                    stroke=conditional,
                    dash="dashed",
                    label=constraint,
                ),
                Text(410, 199, constraint, 25, max_width=270, weight="bold"),
                Text(
                    410,
                    232,
                    "matched constraint; not a policy signal",
                    22,
                    max_width=270,
                    leading=1.0,
                    semantic_role="supporting-note",
                ),
                RoundedRect(
                    425,
                    312,
                    240,
                    106,
                    radius=9,
                    fill=neutral,
                    stroke=ink,
                    label="review policy",
                ),
                Text(459, 326, "review policy", 30, max_width=174, weight="bold"),
                Text(
                    454,
                    370,
                    "declared routing only",
                    22,
                    max_width=182,
                    semantic_role="supporting-note",
                ),
                Text(
                    410,
                    458,
                    "Dashed border and path mean gated; they do not state an outcome.",
                    22,
                    max_width=270,
                    leading=1.0,
                    semantic_role="supporting-note",
                ),
            ),
            semantic_role="budget-constraint",
            metadata=(
                ("role", "budget-constraint"),
                ("label", constraint),
                ("treatment", "enclosing-constraint"),
            ),
        )
    )

    action_y = (112, 191, 270, 349, 428, 507)
    for label, y in zip(content.items["actions"], action_y, strict=True):
        gated = label == "blocked action"
        centre_y = y + 32
        elements.append(
            Group(
                elements=(
                    _arrow(
                        ((665, 365), (730, 365), (730, centre_y), (765, centre_y)),
                        tokens,
                        "dashed" if gated else "solid",
                    ),
                    RoundedRect(
                        765,
                        y,
                        370,
                        64,
                        radius=7,
                        fill=white,
                        stroke=conditional if gated else existing,
                        dash="dashed" if gated else "solid",
                        label=label,
                    ),
                    Text(783, y + 17, label, 25, max_width=334, leading=1.0, weight="bold"),
                ),
                semantic_role="routing-action",
                metadata=(
                    ("role", "routing-action"),
                    ("label", label),
                    ("width", "370"),
                    ("height", "64"),
                    ("treatment", "gated" if gated else "equal"),
                ),
            )
        )

    elements.append(
        Text(20, 585, "Hard rules bypass the scoring policy", 25, max_width=470, weight="bold")
    )
    hard_rule_x = (20, 395, 770)
    for label, x in zip(content.items["hard_rules"], hard_rule_x, strict=True):
        decision_size = 36
        decision_centre_x = x + decision_size / 2
        elements.append(
            Group(
                elements=(
                    Diamond(
                        x,
                        650,
                        decision_size,
                        decision_size,
                        fill=white,
                        stroke=conditional,
                        dash="dashed",
                        label=label,
                    ),
                    Text(x + 50, 650, label, 25, max_width=285, leading=1.0, weight="bold"),
                    _arrow(
                        ((decision_centre_x, 650), (decision_centre_x, 630)),
                        tokens,
                        "dashed",
                    ),
                ),
                semantic_role="hard-rule",
                metadata=(
                    ("role", "hard-rule"),
                    ("label", label),
                    ("route", "bypass-policy-to-blocked-action"),
                ),
            )
        )

    elements.append(
        Group(
            elements=(
                _arrow(((38, 630), (805, 630)), tokens, "dashed"),
                _arrow(((740, 630), (740, 539), (765, 539)), tokens, "dashed"),
            ),
            semantic_role="hard-rule-bus",
            metadata=(
                ("role", "hard-rule-bus"),
                ("bus_id", "hard-rule-bypass"),
                (
                    "source_ids",
                    "missing-authorization|prohibited-transfer|other-high-consequence-conditions",
                ),
                ("target_id", "blocked-action"),
            ),
        )
    )

    elements.append(
        Text(
            20,
            736,
            content.provenance,
            22,
            max_width=1_120,
            leading=1.08,
            semantic_role="provenance",
        )
    )
    return Scene(
        width=1160,
        height=800,
        title=content.title,
        description=content.alt_text,
        elements=tuple(elements),
    )
