"""Deterministic, standalone SVG emission from the shared scene graph."""

from __future__ import annotations

from html import escape
from pathlib import Path

from proposal_visuals.fonts import svg_font_data_uri
from proposal_visuals.model import (
    HATCH_STROKE_WIDTH,
    Cylinder,
    Diamond,
    Element,
    Group,
    Parallelogram,
    Polyline,
    Rect,
    RoundedRect,
    Scene,
    Text,
    cylinder_geometry,
    hatch_region,
    rect_hatch_segments,
    text_lines,
    validate_scene,
)


def _number(value: float) -> str:
    return f"{value:.3f}".rstrip("0").rstrip(".")


def _points(points: tuple[tuple[float, float], ...]) -> str:
    return " ".join(f"{_number(x)},{_number(y)}" for x, y in points)


def _dash(style: str) -> str:
    return {"solid": "", "dashed": ' stroke-dasharray="6 4"', "dotted": ' stroke-dasharray="1 3"'}[style]


class SvgRenderer:
    """Emit only paths, basic vector shapes, text, and embedded font data."""

    def render(self, scene: Scene) -> str:
        body = "".join(self._element(element) for element in scene.elements)
        regular, bold = svg_font_data_uri(), svg_font_data_uri("bold")
        style = (
            "<style>@font-face{font-family:'Carlito';src:url('"
            f"{regular}') format('truetype');font-weight:400;}}"
            "@font-face{font-family:'Carlito';src:url('"
            f"{bold}') format('truetype');font-weight:700;}}"
            "</style>"
        )
        title = f"<title>{escape(scene.title)}</title>" if scene.title else ""
        description = f"<desc>{escape(scene.description)}</desc>" if scene.description else ""
        return (
            '<?xml version="1.0" encoding="UTF-8"?>'
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{_number(scene.width)}pt" height="{_number(scene.height)}pt" '
            f'viewBox="0 0 {_number(scene.width)} {_number(scene.height)}" role="img">'
            f"{title}{description}{style}{body}</svg>"
        )

    def _shape_style(self, element: Rect) -> str:
        return (
            f'fill="{element.fill}" stroke="{element.stroke}" stroke-width="{_number(element.line_width)}"'
            f"{_dash(element.dash)} data-role=\"{escape(element.semantic_role)}\""
        )

    def _outline_style(self, element: Rect) -> str:
        return (
            f'fill="none" stroke="{element.stroke}" '
            f'stroke-width="{_number(element.line_width)}"{_dash(element.dash)}'
        )

    def _hatch_lines(self, element: Rect) -> str:
        if not element.hatch:
            return ""
        return "".join(
            f'<line x1="{_number(start[0])}" y1="{_number(start[1])}" '
            f'x2="{_number(end[0])}" y2="{_number(end[1])}" '
            f'stroke="#5F6B7A" stroke-width="{_number(HATCH_STROKE_WIDTH)}"/>'
            for start, end in rect_hatch_segments(hatch_region(element))
        )

    def _with_hatch(self, element: Rect, base: str, outline: str) -> str:
        if not element.hatch:
            return base
        return base + self._hatch_lines(element) + outline

    def _element(self, element: Element) -> str:
        if isinstance(element, Group):
            metadata = "".join(
                f' data-meta-{key}="{escape(value)}"' for key, value in element.metadata
            )
            return f'<g data-role="{escape(element.semantic_role)}"{metadata}>' + "".join(
                self._element(child) for child in element.elements
            ) + "</g>"
        if isinstance(element, Text):
            weight = "700" if element.weight == "bold" else "400"
            lines = text_lines(element)
            tspans = "".join(
                f'<tspan x="{_number(element.x)}" dy="{_number(element.font_size * element.leading if index else 0)}">{escape(line)}</tspan>'
                for index, line in enumerate(lines)
            )
            return (
                f'<text x="{_number(element.x)}" y="{_number(element.y + element.font_size)}" '
                f'font-family="Carlito" font-size="{_number(element.font_size)}" font-weight="{weight}" '
                f'fill="{element.fill}" data-role="{escape(element.semantic_role)}">{tspans}</text>'
            )
        if isinstance(element, Polyline):
            arrowhead = element.arrowhead
            assert arrowhead is not None
            return (
                f'<polyline points="{_points(element.points)}" fill="none" stroke="{element.stroke}" '
                f'stroke-width="{_number(element.line_width)}"{_dash(element.dash)} '
                f'data-role="{escape(element.semantic_role)}"/>'
                f'<polygon points="{_points(arrowhead.points)}" fill="{element.stroke}" '
                f'data-role="arrowhead"/>'
            )
        style = self._shape_style(element)
        if isinstance(element, RoundedRect):
            base = (
                f'<rect x="{_number(element.x)}" y="{_number(element.y)}" width="{_number(element.width)}" '
                f'height="{_number(element.height)}" rx="{_number(element.radius)}" {style}/>'
            )
            outline = (
                f'<rect x="{_number(element.x)}" y="{_number(element.y)}" width="{_number(element.width)}" '
                f'height="{_number(element.height)}" rx="{_number(element.radius)}" '
                f'{self._outline_style(element)}/>'
            )
            return self._with_hatch(element, base, outline)
        if isinstance(element, Diamond):
            points = (
                (element.x + element.width / 2, element.y),
                (element.x + element.width, element.y + element.height / 2),
                (element.x + element.width / 2, element.y + element.height),
                (element.x, element.y + element.height / 2),
            )
            base = f'<polygon points="{_points(points)}" {style}/>'
            outline = f'<polygon points="{_points(points)}" {self._outline_style(element)}/>'
            return self._with_hatch(element, base, outline)
        if isinstance(element, Parallelogram):
            points = (
                (element.x + element.skew, element.y),
                (element.x + element.width, element.y),
                (element.x + element.width - element.skew, element.y + element.height),
                (element.x, element.y + element.height),
            )
            base = f'<polygon points="{_points(points)}" {style}/>'
            outline = f'<polygon points="{_points(points)}" {self._outline_style(element)}/>'
            return self._with_hatch(element, base, outline)
        if isinstance(element, Cylinder):
            geometry = cylinder_geometry(element)
            commands = geometry.outline_commands
            top_start, top_control_1, top_control_2, top_end = geometry.top_arc
            outline_data = (
                f'M {_number(geometry.outline_start[0])} {_number(geometry.outline_start[1])} '
                f'C {_number(commands[0][0][0])} {_number(commands[0][0][1])} {_number(commands[0][1][0])} {_number(commands[0][1][1])} {_number(commands[0][2][0])} {_number(commands[0][2][1])} '
                f'L {_number(commands[1][2][0])} {_number(commands[1][2][1])} '
                f'C {_number(commands[2][0][0])} {_number(commands[2][0][1])} {_number(commands[2][1][0])} {_number(commands[2][1][1])} {_number(commands[2][2][0])} {_number(commands[2][2][1])} Z'
            )
            base = f'<path d="{outline_data}" data-shape="cylinder" {style}/>'
            outline = f'<path d="{outline_data}" {self._outline_style(element)}/>'
            top = (
                f'<path d="M {_number(top_start[0])} {_number(top_start[1])} C {_number(top_control_1[0])} {_number(top_control_1[1])} '
                f'{_number(top_control_2[0])} {_number(top_control_2[1])} {_number(top_end[0])} {_number(top_end[1])}" '
                f'fill="none" stroke="{element.stroke}" stroke-width="{_number(element.line_width)}"{_dash(element.dash)} data-role="cylinder-top"/>'
            )
            return self._with_hatch(element, base, outline) + top
        rectangle = (
            f'<rect x="{_number(element.x)}" y="{_number(element.y)}" width="{_number(element.width)}" '
            f'height="{_number(element.height)}" {style}/>'
        )
        outline = (
            f'<rect x="{_number(element.x)}" y="{_number(element.y)}" '
            f'width="{_number(element.width)}" height="{_number(element.height)}" '
            f'fill="none" stroke="{element.stroke}" '
            f'stroke-width="{_number(element.line_width)}"{_dash(element.dash)}/>'
        )
        return self._with_hatch(element, rectangle, outline)


def render_svg(scene: Scene, output_path: Path) -> None:
    validate_scene(scene)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(SvgRenderer().render(scene), encoding="utf-8", newline="\n")
