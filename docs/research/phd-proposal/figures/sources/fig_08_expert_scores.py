"""Figure 8: manuscript-reported expert-review scores, without inferred statistics."""

from __future__ import annotations

from proposal_visuals.content import FigureContent
from proposal_visuals.model import Group, Rect, Scene, Text
from proposal_visuals.tokens import VisualTokens


def build(content: FigureContent, tokens: VisualTokens) -> Scene:
    """Draw the four reported score pairs as compact horizontal bars."""
    if content.figure_id != "fig-08":
        raise ValueError("Figure 8 builder requires fig-08 content")

    ink = tokens.colors["ink"].value
    navy = tokens.colors["existing"].value
    neutral = tokens.colors["neutral_fill"].value
    white = tokens.colors["background"].value
    axis = content.items["axis"]
    domain = content.items["y_domain"]
    lower, upper = (float(value) for value in domain)
    plot_left, plot_top, plot_width, plot_height = 300, 96, 600, 170
    elements: list[object] = [
        Text(30, 16, content.title, 32, max_width=1040, weight="bold", leading=1.05),
        Text(30, 57, axis["label"], 28, max_width=300, weight="bold", leading=1.05),
    ]
    for value in axis["ticks"]:
        x = plot_left + (float(value) - lower) / (upper - lower) * plot_width
        elements.extend(
            (
                Rect(x - 0.4, plot_top, 0.8, plot_height, fill=neutral, stroke=neutral, line_width=0.8),
                Text(x - 13, 69, f"{value:.1f}", 28, max_width=55, leading=1.0),
            )
        )
    elements.append(
        Group(
            elements=(
                Rect(plot_left, plot_top, 0.8, plot_height, fill=ink, stroke=ink, line_width=0.8),
                Rect(plot_left, plot_top + plot_height, plot_width, 0.8, fill=ink, stroke=ink, line_width=0.8),
            ),
            semantic_role="score-axis",
            metadata=(("role", "score-axis"), ("ticks", "|".join(f"{value:.1f}" for value in axis["ticks"]))),
        )
    )

    values = content.items["values"]
    for index, (setting, pair) in enumerate(values.items()):
        row_y = 103 + index * 42
        elements.append(Text(30, row_y + 5, setting, 28, max_width=190, weight="bold", leading=1.0))
        for offset, key, label, encoding in (
            (0, "compliance_vectors", content.items["series_labels"][0], "solid"),
            (18, "uncovered_fragment_audits", content.items["series_labels"][1], "hatch"),
        ):
            value = float(pair[key])
            length = value * plot_width
            y = row_y + offset
            rect = Rect(
                plot_left,
                y,
                length,
                13,
                fill=navy if encoding == "solid" else white,
                stroke=navy,
                hatch="diagonal" if encoding == "hatch" else None,
                label=f"{setting} {label} {value:.2f}",
            )
            elements.append(
                Group(
                    elements=(
                        rect,
                        Text(plot_left + length + 8, y - 7, f"{value:.2f}", 28, max_width=65, weight="bold", leading=1.0),
                    ),
                    semantic_role="score-bar",
                    metadata=(
                        ("role", "score-bar"),
                        ("setting", setting),
                        ("series", key),
                        ("value", f"{value:.2f}"),
                        ("height", f"{rect.height:.1f}"),
                        ("length", f"{length:.1f}"),
                        ("encoding", encoding),
                        ("orientation", "horizontal"),
                    ),
                )
            )

    elements.extend(
        (
            Rect(170, 282, 30, 14, fill=navy, stroke=navy, label="solid series"),
            Text(212, 274, content.items["series_labels"][0], 28, max_width=320, leading=1.0),
            Rect(570, 282, 30, 14, fill=white, stroke=navy, hatch="diagonal", label="hatched series"),
            Text(612, 274, content.items["series_labels"][1], 28, max_width=390, leading=1.0),
            Text(30, 315, content.items["sample_disclosure"], 24, max_width=1040, leading=1.05, semantic_role="supporting-note"),
            Text(30, 343, content.items["evidence_boundary"], 24, max_width=1040, leading=1.05, semantic_role="boundary-note"),
            Text(30, 373, content.provenance, 24, max_width=1040, leading=1.05, semantic_role="provenance"),
        )
    )
    root = Group(
        elements=tuple(elements),
        semantic_role="figure-root",
        metadata=(
            ("role", "figure-root"),
            ("layout", "compact-horizontal-score-chart"),
            ("y_domain", "|".join(f"{value:.1f}" for value in domain)),
            ("pairs", ";".join("|".join(f"{float(score):.2f}" for score in pair.values()) for pair in values.values())),
            ("evidence_scope", content.items["evidence_scope"]),
        ),
    )
    return Scene(width=1100, height=430, title=content.title, description=content.alt_text, elements=(root,))
