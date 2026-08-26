"""Figure 6: a governed record next to an auditable canonical lifecycle."""

from __future__ import annotations

import math

from proposal_visuals.content import FigureContent
from proposal_visuals.model import Arrowhead, Group, Polyline, Rect, RoundedRect, Scene, Text
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
    base = (endpoint[0] - 10 * ux, endpoint[1] - 10 * uy)
    perpendicular = (-5 * uy, 5 * ux)
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
    """Build compact record lanes and a canonical state machine without conflation."""
    if content.figure_id != "fig-06":
        raise ValueError("Figure 6 builder requires fig-06 content")

    ink = tokens.colors["ink"].value
    existing = tokens.colors["existing"].value
    conditional = tokens.colors["conditional"].value
    neutral = tokens.colors["neutral_fill"].value
    white = tokens.colors["background"].value
    elements: list[object] = [
        Text(20, 12, content.title, 28, max_width=1_010, weight="bold"),
        Text(20, 55, "A. Governed-judgment record", 23, max_width=410, weight="bold"),
        Text(465, 55, "B. Canonical auditable lifecycle", 23, max_width=560, weight="bold"),
    ]

    record_positions = ((20, 95), (225, 95), (20, 185), (225, 185), (20, 275), (225, 275))
    for index, (label, (x, y)) in enumerate(
        zip(content.items["record_groups"], record_positions, strict=True)
    ):
        elements.append(
            Group(
                elements=(
                    Rect(
                        x,
                        y,
                        190,
                        76,
                        fill=neutral if index % 2 else white,
                        stroke=ink,
                        label=label,
                    ),
                    Text(x + 12, y + 11, label, 23, max_width=166, leading=1.0, weight="bold"),
                ),
                semantic_role="record-field-group",
                metadata=(("role", "record-field-group"), ("label", label), ("panel", "record")),
            )
        )
    elements.append(
        Text(
            20,
            366,
            "Six field groups are retained as an inspectable governed record.",
            20,
            max_width=405,
            leading=1.0,
            semantic_role="supporting-note",
        )
    )

    state_positions = {
        "Created": (465, 110),
        "Validated": (650, 110),
        "Contested": (835, 110),
        "Revoked": (465, 290),
        "Expired": (650, 290),
        "Superseded": (835, 290),
    }
    for state in content.items["states"]:
        x, y = state_positions[state]
        terminal = state in {"Superseded", "Expired", "Revoked"}
        elements.append(
            Group(
                elements=(
                    RoundedRect(
                        x,
                        y,
                        150,
                        68,
                        radius=7,
                        fill=neutral if terminal else white,
                        stroke=conditional if terminal else existing,
                        dash="dashed" if terminal else "solid",
                        label=state,
                    ),
                    Text(x + 13, y + 22, state, 23, max_width=124, leading=1.0, weight="bold"),
                ),
                semantic_role="lifecycle-state",
                metadata=(
                    ("role", "lifecycle-state"),
                    ("state", state),
                    ("auditability", "retained" if terminal else "current"),
                ),
            )
        )

    transition_specs = (
        ("activation", "Created", "Validated", ((615, 144), (650, 144)), (500, 190)),
        ("challenge", "Validated", "Contested", ((800, 144), (835, 144)), (760, 190)),
        ("replacement", "Contested", "Superseded", ((910, 178), (910, 290)), (918, 218)),
        ("lapse", "Validated", "Expired", ((725, 178), (725, 290)), (733, 218)),
        (
            "revocation",
            "Validated",
            "Revoked",
            ((650, 160), (632, 160), (632, 324), (615, 324)),
            (500, 238),
        ),
    )
    for label, source, target, points, label_position in transition_specs:
        elements.append(
            Group(
                elements=(
                    _arrow(
                        points,
                        tokens,
                        "dashed" if target in {"Superseded", "Expired", "Revoked"} else "solid",
                    ),
                    Text(
                        label_position[0],
                        label_position[1],
                        label,
                        23,
                        max_width=125,
                        weight="bold",
                    ),
                ),
                semantic_role="state-transition",
                metadata=(
                    ("role", "state-transition"),
                    ("label", label),
                    ("source", source),
                    ("target", target),
                ),
            )
        )

    elements.append(
        Group(
            elements=(
                Text(
                    465,
                    386,
                    "Current source labels Draft / Reviewed / Active are not silently merged with these canonical lifecycle states.",
                    20,
                    max_width=560,
                    leading=1.05,
                    semantic_role="boundary-note",
                ),
            ),
            semantic_role="judgment-lifecycle",
            metadata=(
                ("role", "judgment-lifecycle"),
                ("current_source_states", "Draft|Reviewed|Active"),
                (
                    "canonical_states",
                    "Created|Validated|Contested|Superseded|Expired|Revoked",
                ),
                ("discrepancy_resolution", "recorded-not-conflated"),
            ),
        )
    )
    elements.append(
        Text(
            20,
            580,
            content.provenance,
            20,
            max_width=1_010,
            leading=1.08,
            semantic_role="provenance",
        )
    )
    return Scene(
        width=1050,
        height=648,
        title=content.title,
        description=content.alt_text,
        elements=tuple(elements),
    )
