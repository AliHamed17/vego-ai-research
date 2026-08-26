"""Figure 7: source-bounded reuse decision and independent replication diagnosis."""

from __future__ import annotations

import math

from proposal_visuals.content import FigureContent
from proposal_visuals.model import Arrowhead, Diamond, Group, Polyline, Rect, Scene, Text
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


def _bus(
    points: tuple[tuple[float, float], ...], tokens: VisualTokens, dash: str = "dashed"
) -> Polyline:
    return _arrow(points, tokens, dash)


def build(content: FigureContent, tokens: VisualTokens) -> Scene:
    """Build three visually independent layers without inferring missing routing rules."""
    if content.figure_id != "fig-07":
        raise ValueError("Figure 7 builder requires fig-07 content")

    existing = tokens.colors["existing"].value
    conditional = tokens.colors["conditional"].value
    neutral = tokens.colors["neutral_fill"].value
    white = tokens.colors["background"].value
    elements: list[object] = [
        Text(20, 12, content.title, 33, max_width=1_190, weight="bold"),
        Text(20, 58, "Five sequential reuse gates", 27, max_width=420, weight="bold"),
    ]

    gate_x = (20, 260, 500, 740, 980)
    gate_y, gate_width, gate_height = 100, 190, 100
    for index, (x, label) in enumerate(zip(gate_x, content.items["gates"], strict=True), start=1):
        elements.append(
            Group(
                elements=(
                    Diamond(
                        x,
                        gate_y,
                        gate_width,
                        gate_height,
                        fill=white,
                        stroke=existing,
                        label=label,
                    ),
                    Text(
                        x + 20,
                        gate_y + 10,
                        label,
                        27,
                        max_width=150,
                        leading=1.0,
                        weight="bold",
                    ),
                ),
                semantic_role="reuse-gate",
                metadata=(("role", "reuse-gate"), ("label", label), ("sequence", str(index))),
            )
        )
        elements.append(
            Group(
                elements=(
                    _bus(
                        (
                            (x + gate_width / 2, gate_y + gate_height),
                            (x + gate_width / 2, 245),
                        ),
                        tokens,
                    ),
                ),
                semantic_role="gate-failure-path",
                metadata=(
                    ("role", "gate-failure-path"),
                    ("source_gate", str(index)),
                    ("target", "not eligible for reuse"),
                    ("bus_id", "any-gate-fails"),
                ),
            )
        )
        if index < 5:
            elements.append(
                Group(
                    elements=(
                        _arrow(((x + gate_width, 150), (gate_x[index], 150)), tokens),
                        Text(x + 197, 112, "yes", 27, max_width=38, weight="bold"),
                    ),
                    semantic_role="passed-path",
                    metadata=(
                        ("role", "passed-path"),
                        ("source_gate", str(index)),
                        ("target_gate", str(index + 1)),
                        ("label", "yes"),
                    ),
                )
            )

    elements.extend(
        (
            Group(
                elements=(_bus(((1_075, 245), (115, 245)), tokens),),
                semantic_role="shared-bus",
                metadata=(
                    ("role", "shared-bus"),
                    ("bus_id", "any-gate-fails"),
                    ("purpose", "source-figure-any-gate-fails-boundary"),
                ),
            ),
            Group(
                elements=(_arrow(((115, 245), (115, 300)), tokens, "dashed"),),
                semantic_role="failure-boundary-path",
                metadata=(
                    ("role", "failure-boundary-path"),
                    ("bus_id", "any-gate-fails"),
                    ("target", "not eligible for reuse"),
                ),
            ),
            Group(
                elements=(
                    Rect(
                        20,
                        300,
                        260,
                        70,
                        fill=neutral,
                        stroke=conditional,
                        dash="dashed",
                        label="not eligible for reuse",
                    ),
                    Text(
                        35,
                        310,
                        "not eligible for reuse",
                        27,
                        max_width=230,
                        leading=1.0,
                        weight="bold",
                    ),
                ),
                semantic_role="failure-boundary",
                metadata=(
                    ("role", "failure-boundary"),
                    ("label", "not eligible for reuse"),
                    ("gate_to_status_mapping", "not-specified-in-source"),
                ),
            ),
        )
    )

    status_positions = (
        (320, 170),
        (505, 285),
        (805, 170),
        (990, 220),
    )
    status_groups: list[Group] = []
    for label, (x, width) in zip(content.items["statuses"], status_positions, strict=True):
        status_groups.append(
            Group(
                elements=(
                    Rect(x, 330, width, 70, fill=white, stroke=existing, label=label),
                    Text(
                        x + 14,
                        336,
                        label,
                        27,
                        max_width=width - 28,
                        leading=1.0,
                        weight="bold",
                    ),
                ),
                semantic_role="formal-status",
                metadata=(
                    ("role", "formal-status"),
                    ("label", label),
                    ("kind", "formal-procedure-status"),
                ),
            )
        )
    elements.append(
        Group(
            elements=(
                Text(320, 266, "Four-status reuse decision", 27, max_width=390, weight="bold"),
                Text(
                    760,
                    268,
                    "Exact gate-to-status routing is not specified in the source.",
                    24,
                    max_width=450,
                    leading=1.0,
                    semantic_role="boundary-note",
                ),
                *status_groups,
            ),
            semantic_role="status-decision",
            metadata=(
                ("role", "status-decision"),
                ("status_count", "4"),
                ("routing_rule", "not-specified-in-source"),
            ),
        )
    )

    reuse_label = content.items["outcomes"][0]
    elements.extend(
        (
            Text(
                320,
                404,
                "The proposal specifies four procedure statuses but does not provide a gate-to-status lookup table.",
                24,
                max_width=550,
                leading=1.0,
                semantic_role="boundary-note",
            ),
            Group(
                elements=(
                    Rect(920, 405, 290, 90, fill=neutral, stroke=existing, label=reuse_label),
                    Text(936, 410, reuse_label, 27, max_width=258, leading=1.0, weight="bold"),
                    Text(
                        936,
                        443,
                        "advice + outcome receipt\nnot a fifth status",
                        24,
                        max_width=258,
                        leading=1.0,
                        semantic_role="supporting-note",
                    ),
                ),
                semantic_role="reuse-permission",
                metadata=(
                    ("role", "reuse-permission"),
                    ("label", reuse_label),
                    ("formal_status", "false"),
                    ("distinct_from_statuses", "true"),
                    ("routing_rule", "not-specified-in-source"),
                ),
            ),
        )
    )

    local_quirk, capability_gap = content.items["outcomes"][1:]
    check_positions = (
        (20, 580, 560),
        (620, 580, 590),
        (20, 670, 560),
        (620, 670, 590),
    )
    check_groups: list[Group] = []
    for label, (x, y, width) in zip(content.items["and_checks"], check_positions, strict=True):
        centre_y = y + 37
        endpoint_x = 600
        check_groups.append(
            Group(
                elements=(
                    Rect(
                        x,
                        y,
                        width,
                        74,
                        fill=neutral,
                        stroke=conditional,
                        dash="dashed",
                        label=label,
                    ),
                    Text(x + 14, y + 5, label, 27, max_width=width - 28, leading=1.0),
                    _bus(
                        (
                            (x + width if x < endpoint_x else x, centre_y),
                            (endpoint_x, centre_y),
                        ),
                        tokens,
                    ),
                ),
                semantic_role="capability-gap-check",
                metadata=(
                    ("role", "capability-gap-check"),
                    ("label", label),
                    ("operator", "AND"),
                    ("bus_id", "and-checks"),
                ),
            )
        )

    elements.append(
        Group(
            elements=(
                Text(
                    20,
                    510,
                    "Separate capability-gap replication diagnosis",
                    27,
                    max_width=560,
                    weight="bold",
                ),
                Text(
                    650,
                    512,
                    "Independent of reuse permission and the four-status reuse decision.",
                    24,
                    max_width=560,
                    leading=1.0,
                    semantic_role="boundary-note",
                ),
                *check_groups,
                Group(
                    elements=(
                        _arrow(((600, 617), (600, 790)), tokens, "dashed"),
                        Diamond(
                            560,
                            790,
                            80,
                            60,
                            fill=white,
                            stroke=conditional,
                            dash="dashed",
                            label="AND",
                        ),
                        Text(574, 804, "AND", 27, max_width=52, leading=1.0, weight="bold"),
                    ),
                    semantic_role="shared-bus",
                    metadata=(
                        ("role", "shared-bus"),
                        ("bus_id", "and-checks"),
                        ("purpose", "four-check-replication-guard"),
                    ),
                ),
                Group(
                    elements=(
                        Rect(
                            20,
                            790,
                            330,
                            90,
                            fill=white,
                            stroke=conditional,
                            dash="dashed",
                            label=local_quirk,
                        ),
                        Text(36, 797, local_quirk, 27, max_width=298, leading=1.0, weight="bold"),
                        Text(
                            36,
                            831,
                            "recorded and confined to this context",
                            24,
                            max_width=298,
                            leading=1.0,
                            semantic_role="supporting-note",
                        ),
                    ),
                    semantic_role="diagnosis",
                    metadata=(
                        ("role", "diagnosis"),
                        ("label", local_quirk),
                        ("independent_of_reuse_decision", "true"),
                    ),
                ),
                Group(
                    elements=(
                        Group(
                            elements=(
                                _arrow(
                                    ((640, 820), (700, 820), (700, 831), (780, 831)),
                                    tokens,
                                    "dashed",
                                ),
                                Rect(
                                    780,
                                    790,
                                    430,
                                    90,
                                    fill=white,
                                    stroke=conditional,
                                    dash="dashed",
                                    label=capability_gap,
                                ),
                                Text(
                                    796,
                                    797,
                                    capability_gap,
                                    27,
                                    max_width=398,
                                    leading=1.0,
                                    weight="bold",
                                ),
                                Text(
                                    796,
                                    831,
                                    "only if all four replication checks hold",
                                    24,
                                    max_width=398,
                                    leading=1.0,
                                    semantic_role="supporting-note",
                                ),
                            ),
                            semantic_role="diagnosis-guard-path",
                            metadata=(
                                ("role", "diagnosis-guard-path"),
                                ("source", "AND guard"),
                                ("target", capability_gap),
                                ("bus_id", "and-checks"),
                            ),
                        ),
                    ),
                    semantic_role="diagnosis",
                    metadata=(
                        ("role", "diagnosis"),
                        ("label", capability_gap),
                        ("independent_of_reuse_decision", "true"),
                    ),
                ),
            ),
            semantic_role="diagnostic-layer",
            metadata=(
                ("role", "diagnostic-layer"),
                ("relationship_to_reuse", "independent"),
                ("guard", "four-check-AND"),
            ),
        )
    )

    elements.append(
        Group(
            elements=(
                Text(
                    20,
                    902,
                    content.provenance,
                    24,
                    max_width=1_190,
                    leading=1.0,
                    semantic_role="provenance",
                ),
            ),
            semantic_role="reuse-procedure",
            metadata=(
                ("role", "reuse-procedure"),
                ("gate_count", "5"),
                ("status_count", "4"),
                ("gate_to_status_mapping", "not-specified-in-source"),
                ("diagnosis_dependency", "independent-of-reuse-status"),
            ),
        )
    )
    return Scene(
        width=1230,
        height=945,
        title=content.title,
        description=content.alt_text,
        elements=tuple(elements),
    )
