"""Build reproducible, privacy-safe baseline plots for the supervisor readout.

The input is a small tracked evidence table containing only aggregate counts from
EXP-045, EXP-046, and the C0 characterization.  The figures are descriptive:
they locate candidate human-review signals and recorded reviewer changes.  They
are not accuracy, quality, human-benefit, or VEGO-AI_ON/OFF outcome plots.

The renderer intentionally uses Pillow plus a small deterministic SVG writer.
It has no provider, model, network, corpus, or private-data dependency.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "docs" / "research" / "phd-proposal" / "2026-09-06-tomorrow-baseline-plot-data.json"
DEFAULT_OUT = ROOT / "docs" / "research" / "phd-proposal" / "figures"

SURFACE = "#FCFCFB"
INK = "#17202A"
MUTED = "#5B6770"
GRID = "#D9E0E4"
AXIS = "#94A3AD"
BLUE = "#1F5A94"
BLUE_DARK = "#123A63"
ORANGE = "#C96A2B"
ORANGE_DARK = "#8A451D"
CALLOUT = "#F2F6F8"

WIDTH = 1800
HEIGHT = 1180
LEFT = 585
RIGHT = 180
TOP = 220
BOTTOM = 190
BAR_HEIGHT = 65
BAR_GAP = 45


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def load_data(path: Path = DATA_PATH) -> dict[str, Any]:
    """Load and validate the aggregate evidence table."""

    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"plot data unavailable: {path}") from exc
    if not isinstance(value, dict) or value.get("schema_version") != "vego-ai-supervisor-baseline-plot-data-v1":
        raise ValueError("unsupported supervisor plot-data schema")
    if value.get("evidence_status") != "DESCRIPTIVE_ONLY":
        raise ValueError("plot data must remain descriptive-only")
    sources = value.get("sources")
    if not isinstance(sources, list) or not sources:
        raise ValueError("plot data requires source records")
    for source in sources:
        if not isinstance(source, dict) or not isinstance(source.get("path"), str):
            raise ValueError("plot source paths must be relative strings")
        source_path = Path(source["path"])
        if source_path.is_absolute() or ".." in source_path.parts:
            raise ValueError("plot sources must not contain absolute or traversal paths")
        if not (ROOT / source_path).is_file():
            raise ValueError(f"plot source is missing: {source_path.as_posix()}")
    for field in ("signal_rows", "review_rows"):
        rows = value.get(field)
        if not isinstance(rows, list) or not rows:
            raise ValueError(f"plot data requires non-empty {field}")
        ids: set[str] = set()
        for row in rows:
            if not isinstance(row, dict):
                raise ValueError(f"{field} rows must be objects")
            row_id = row.get("id")
            numerator = row.get("numerator")
            denominator = row.get("denominator")
            if not isinstance(row_id, str) or not row_id or row_id in ids:
                raise ValueError(f"{field} row identifiers must be unique")
            if (
                isinstance(numerator, bool)
                or not isinstance(numerator, int)
                or isinstance(denominator, bool)
                or not isinstance(denominator, int)
                or denominator <= 0
                or numerator < 0
                or numerator > denominator
            ):
                raise ValueError(f"invalid numerator/denominator for {row_id}")
            if not isinstance(row.get("label"), str) or not row["label"]:
                raise ValueError(f"missing label for {row_id}")
            ids.add(row_id)
    return value


def _font(size: int, *, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    """Use a stable system sans font with a safe fallback."""

    candidates = []
    windows = os.environ.get("WINDIR")
    if windows:
        candidates.append(Path(windows) / "Fonts" / ("segoeuib.ttf" if bold else "segoeui.ttf"))
    candidates.extend(
        [
            Path("/usr/share/fonts/truetype/dejavu") / ("DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"),
            Path("/usr/share/fonts/truetype/liberation2") / ("LiberationSans-Bold.ttf" if bold else "LiberationSans-Regular.ttf"),
        ]
    )
    for candidate in candidates:
        if candidate.is_file():
            return ImageFont.truetype(str(candidate), size)
    return ImageFont.load_default()


def _svg_escape(value: str) -> str:
    return (
        value.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def _svg_text(lines: list[str], x: float, y: float, *, size: int, fill: str, weight: str = "400") -> str:
    parts = [f'<text x="{x:g}" y="{y:g}" font-family="Segoe UI, Arial, sans-serif" font-size="{size}px" font-weight="{weight}" fill="{fill}">']
    for index, line in enumerate(lines):
        dy = 0 if index == 0 else size + 8
        parts.append(f'<tspan x="{x:g}" dy="{dy:g}">{_svg_escape(line)}</tspan>')
    parts.append("</text>")
    return "".join(parts)


def _split_label(label: str, width: int = 40) -> list[str]:
    words = label.split()
    lines: list[str] = []
    current = ""
    for word in words:
        candidate = f"{current} {word}".strip()
        if current and len(candidate) > width:
            lines.append(current)
            current = word
        else:
            current = candidate
    if current:
        lines.append(current)
    return lines or [label]


def _rate(row: dict[str, Any]) -> float:
    return 100.0 * row["numerator"] / row["denominator"]


def _display_path(path: Path) -> str:
    """Return a repository-relative path without leaking temporary absolutes."""

    try:
        return path.relative_to(ROOT).as_posix()
    except ValueError:
        return path.name


def _draw_header(draw: ImageDraw.ImageDraw, title: str, subtitle: str) -> None:
    draw.text((80, 52), title, font=_font(42, bold=True), fill=INK)
    draw.text((80, 118), subtitle, font=_font(24), fill=MUTED)
    # Small four-dot research mark. It is a non-data decorative header anchor;
    # the chart itself carries all quantitative meaning.
    for index, color in enumerate((BLUE, ORANGE, BLUE_DARK, ORANGE_DARK)):
        draw.ellipse((WIDTH - 184 + index * 28, 72, WIDTH - 160 + index * 28, 96), fill=color)


def _draw_axes(draw: ImageDraw.ImageDraw, *, y_top: int, y_bottom: int) -> None:
    plot_width = WIDTH - LEFT - RIGHT
    for tick in (0, 25, 50, 75, 100):
        x = LEFT + plot_width * tick / 100
        draw.line((x, y_top, x, y_bottom), fill=GRID, width=2)
        label = f"{tick}%"
        bbox = draw.textbbox((0, 0), label, font=_font(22))
        draw.text((x - (bbox[2] - bbox[0]) / 2, y_bottom + 20), label, font=_font(22), fill=MUTED)
    draw.line((LEFT, y_top, LEFT, y_bottom), fill=AXIS, width=2)
    draw.text((LEFT, y_bottom + 64), "Share of denominator (%)", font=_font(23, bold=True), fill=MUTED)


def _bar_chart_png(rows: list[dict[str, Any]], output: Path, *, title: str, subtitle: str, footer: str, palette: str) -> None:
    image = Image.new("RGB", (WIDTH, HEIGHT), SURFACE)
    draw = ImageDraw.Draw(image)
    _draw_header(draw, title, subtitle)
    y_top = TOP
    y_bottom = TOP + len(rows) * (BAR_HEIGHT + BAR_GAP) - BAR_GAP
    _draw_axes(draw, y_top=y_top - 20, y_bottom=y_bottom + 10)
    plot_width = WIDTH - LEFT - RIGHT
    bar_color = BLUE if palette == "blue" else ORANGE
    outline = BLUE_DARK if palette == "blue" else ORANGE_DARK
    for index, row in enumerate(rows):
        y = TOP + index * (BAR_HEIGHT + BAR_GAP)
        label_lines = _split_label(row["label"])
        text_bbox = draw.multiline_textbbox((0, 0), "\n".join(label_lines), font=_font(23), spacing=7)
        draw.multiline_text((80, y + BAR_HEIGHT / 2 - (text_bbox[3] - text_bbox[1]) / 2), "\n".join(label_lines), font=_font(23), fill=INK, spacing=7)
        width = plot_width * _rate(row) / 100.0
        draw.rounded_rectangle((LEFT, y, LEFT + width, y + BAR_HEIGHT), radius=14, fill=bar_color, outline=outline, width=2)
        value = f"{row['numerator']}/{row['denominator']}  ({_rate(row):.1f}%)"
        draw.text((LEFT + width + 18, y + BAR_HEIGHT / 2 - 17), value, font=_font(24, bold=True), fill=outline)
    draw.rounded_rectangle((80, HEIGHT - 112, WIDTH - 80, HEIGHT - 50), radius=12, fill=CALLOUT)
    draw.text((104, HEIGHT - 95), footer, font=_font(20), fill=MUTED)
    image.save(output, format="PNG", optimize=False, compress_level=9, dpi=(300, 300))


def _bar_chart_svg(rows: list[dict[str, Any]], output: Path, *, title: str, subtitle: str, footer: str, palette: str) -> None:
    plot_width = WIDTH - LEFT - RIGHT
    y_top = TOP
    y_bottom = TOP + len(rows) * (BAR_HEIGHT + BAR_GAP) - BAR_GAP
    bar_color = BLUE if palette == "blue" else ORANGE
    outline = BLUE_DARK if palette == "blue" else ORANGE_DARK
    elements = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}">',
        f'<rect width="{WIDTH}" height="{HEIGHT}" fill="{SURFACE}"/>',
        _svg_text([title], 80, 86, size=42, fill=INK, weight="700"),
        _svg_text([subtitle], 80, 154, size=24, fill=MUTED),
    ]
    for index, color in enumerate((BLUE, ORANGE, BLUE_DARK, ORANGE_DARK)):
        elements.append(f'<circle cx="{WIDTH - 172 + index * 28}" cy="84" r="12" fill="{color}"/>')
    for tick in (0, 25, 50, 75, 100):
        x = LEFT + plot_width * tick / 100
        elements.append(f'<line x1="{x:g}" y1="{y_top - 20}" x2="{x:g}" y2="{y_bottom + 10}" stroke="{GRID}" stroke-width="2"/>')
        elements.append(_svg_text([f"{tick}%"], x - 18 if tick < 100 else x - 24, y_bottom + 48, size=22, fill=MUTED))
    elements.append(f'<line x1="{LEFT}" y1="{y_top - 20}" x2="{LEFT}" y2="{y_bottom + 10}" stroke="{AXIS}" stroke-width="2"/>')
    elements.append(_svg_text(["Share of denominator (%)"], LEFT, y_bottom + 92, size=23, fill=MUTED, weight="700"))
    for index, row in enumerate(rows):
        y = TOP + index * (BAR_HEIGHT + BAR_GAP)
        lines = _split_label(row["label"])
        text_y = y + 30 - (len(lines) - 1) * 15
        elements.append(_svg_text(lines, 80, text_y, size=23, fill=INK))
        width = plot_width * _rate(row) / 100.0
        elements.append(f'<rect x="{LEFT}" y="{y}" width="{width:g}" height="{BAR_HEIGHT}" rx="14" fill="{bar_color}" stroke="{outline}" stroke-width="2"/>')
        elements.append(_svg_text([f"{row['numerator']}/{row['denominator']}  ({_rate(row):.1f}%)"], LEFT + width + 18, y + 43, size=24, fill=outline, weight="700"))
    elements.extend(
        [
            f'<rect x="80" y="{HEIGHT - 112}" width="{WIDTH - 160}" height="62" rx="12" fill="{CALLOUT}"/>',
            _svg_text([footer], 104, HEIGHT - 73, size=20, fill=MUTED),
            "</svg>",
        ]
    )
    output.write_text("\n".join(elements), encoding="utf-8", newline="\n")


def build_figures(data: dict[str, Any], output_dir: Path) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    signal_rows = list(data["signal_rows"])
    review_rows = list(data["review_rows"])
    outputs = [
        {
            "stem": "tomorrow-human-escalation-signals",
            "rows": signal_rows,
            "title": "Observed human-escalation signals by pipeline stage",
            "subtitle": "Frozen run; descriptive signal share with exact numerator / denominator",
            "footer": "EXP-045 descriptive inventory · signal values are not accuracy labels",
            "palette": "blue",
        },
        {
            "stem": "tomorrow-reviewer-change-baseline",
            "rows": review_rows,
            "title": "Observed reviewer changes and candidate queue load",
            "subtitle": "Frozen run; reviewer disagreement and candidate routing, not model quality",
            "footer": "EXP-046 recorded review · an overturn is disagreement, not independent ground truth",
            "palette": "orange",
        },
    ]
    figure_receipt: dict[str, Any] = {
        "schema_version": "vego-ai-supervisor-baseline-figure-receipt-v1",
        "evidence_status": "DESCRIPTIVE_ONLY",
        "data_sha256": sha256_bytes(DATA_PATH.read_bytes()),
        "renderer": "scripts/plot_supervisor_baseline.py",
        "figures": [],
        "qa": {
            "formats": ["PNG", "SVG"],
            "dpi": 300,
            "denominator_labels_visible": True,
            "no_provider_or_network": True,
            "scientific_outcome_observed": False,
        },
    }
    for item in outputs:
        png = output_dir / f"{item['stem']}.png"
        svg = output_dir / f"{item['stem']}.svg"
        _bar_chart_png(item["rows"], png, title=item["title"], subtitle=item["subtitle"], footer=item["footer"], palette=item["palette"])
        _bar_chart_svg(item["rows"], svg, title=item["title"], subtitle=item["subtitle"], footer=item["footer"], palette=item["palette"])
        figure_receipt["figures"].append(
            {
                "stem": item["stem"],
                "png": _display_path(png),
                "png_sha256": sha256_bytes(png.read_bytes()),
                "svg": _display_path(svg),
                "svg_sha256": sha256_bytes(svg.read_bytes()),
                "rows": [row["id"] for row in item["rows"]],
            }
        )
    receipt_path = output_dir.parent / "2026-09-06-tomorrow-baseline-figure-receipt.json"
    receipt_path.write_text(json.dumps(figure_receipt, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    figure_receipt["receipt"] = _display_path(receipt_path)
    return figure_receipt


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args(argv)
    data = load_data()
    receipt = build_figures(data, args.out_dir.resolve())
    print(json.dumps(receipt, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
