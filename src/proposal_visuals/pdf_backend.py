"""Deterministic ReportLab PDF emission from the top-left scene graph."""

from __future__ import annotations

import json
from pathlib import Path

from reportlab.lib.colors import HexColor
from reportlab.pdfgen.canvas import Canvas

from proposal_visuals.fonts import register_carlito_fonts
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


def _scene_semantics(scene: Scene) -> str:
    groups: list[dict[str, object]] = []

    def collect(element: Element) -> None:
        if isinstance(element, Group):
            groups.append({"role": element.semantic_role, "metadata": dict(element.metadata)})
            for child in element.elements:
                collect(child)

    for element in scene.elements:
        collect(element)
    return json.dumps({"groups": groups}, sort_keys=True, separators=(",", ":"))


def _dash(canvas: Canvas, style: str) -> None:
    if style == "solid":
        canvas.setDash()
    elif style == "dashed":
        canvas.setDash(6, 4)
    else:
        canvas.setDash(1, 3)


class PdfRenderer:
    """Render with the exact top-left coordinates used by SVG."""

    def __init__(self, output_path: Path, width: float, height: float) -> None:
        self.output_path = output_path
        self.width = width
        self.height = height

    def _y(self, y: float) -> float:
        return self.height - y

    def _draw_vector_hatch(self, canvas: Canvas, element: Rect) -> None:
        canvas.setStrokeColor(HexColor("#5F6B7A"))
        canvas.setLineWidth(HATCH_STROKE_WIDTH)
        canvas.setDash()
        for start, end in rect_hatch_segments(hatch_region(element)):
            canvas.line(start[0], self._y(start[1]), end[0], self._y(end[1]))

    def _redraw_outline(self, canvas: Canvas, element: Rect, path) -> None:  # type: ignore[no-untyped-def]
        canvas.setStrokeColor(HexColor(element.stroke))
        canvas.setLineWidth(element.line_width)
        _dash(canvas, element.dash)
        canvas.drawPath(path, stroke=1, fill=0)

    def _style(self, canvas: Canvas, element: Rect) -> None:
        canvas.setFillColor(HexColor(element.fill))
        canvas.setStrokeColor(HexColor(element.stroke))
        canvas.setLineWidth(element.line_width)
        _dash(canvas, element.dash)

    def _draw_rect_path(self, canvas: Canvas, element: Rect):  # type: ignore[no-untyped-def]
        path = canvas.beginPath()
        path.rect(element.x, self.height - element.y - element.height, element.width, element.height)
        return path

    def _element(self, canvas: Canvas, element: Element) -> None:
        if isinstance(element, Group):
            for child in element.elements:
                self._element(canvas, child)
            return
        if isinstance(element, Text):
            canvas.setFillColor(HexColor(element.fill))
            canvas.setFont("Carlito-Bold" if element.weight == "bold" else "Carlito", element.font_size)
            for index, line in enumerate(text_lines(element)):
                canvas.drawString(element.x, self._y(element.y + element.font_size * (index * element.leading + 1)), line)
            return
        if isinstance(element, Polyline):
            canvas.setStrokeColor(HexColor(element.stroke))
            canvas.setFillColor(HexColor(element.stroke))
            canvas.setLineWidth(element.line_width)
            _dash(canvas, element.dash)
            path = canvas.beginPath()
            first_x, first_y = element.points[0]
            path.moveTo(first_x, self._y(first_y))
            for x, y in element.points[1:]:
                path.lineTo(x, self._y(y))
            canvas.drawPath(path, stroke=1, fill=0)
            arrowhead = element.arrowhead
            assert arrowhead is not None
            arrow = canvas.beginPath()
            x, y = arrowhead.points[0]
            arrow.moveTo(x, self._y(y))
            for x, y in arrowhead.points[1:]:
                arrow.lineTo(x, self._y(y))
            arrow.close()
            canvas.drawPath(arrow, stroke=0, fill=1)
            return
        self._style(canvas, element)
        if isinstance(element, RoundedRect):
            path = canvas.beginPath()
            path.roundRect(element.x, self.height - element.y - element.height, element.width, element.height, element.radius)
        elif isinstance(element, Diamond):
            path = canvas.beginPath()
            points = (
                (element.x + element.width / 2, element.y),
                (element.x + element.width, element.y + element.height / 2),
                (element.x + element.width / 2, element.y + element.height),
                (element.x, element.y + element.height / 2),
            )
            path.moveTo(points[0][0], self._y(points[0][1]))
            for x, y in points[1:]:
                path.lineTo(x, self._y(y))
            path.close()
        elif isinstance(element, Parallelogram):
            path = canvas.beginPath()
            points = (
                (element.x + element.skew, element.y),
                (element.x + element.width, element.y),
                (element.x + element.width - element.skew, element.y + element.height),
                (element.x, element.y + element.height),
            )
            path.moveTo(points[0][0], self._y(points[0][1]))
            for x, y in points[1:]:
                path.lineTo(x, self._y(y))
            path.close()
        elif isinstance(element, Cylinder):
            geometry = cylinder_geometry(element)
            commands = geometry.outline_commands
            path = canvas.beginPath()
            path.moveTo(geometry.outline_start[0], self._y(geometry.outline_start[1]))
            path.curveTo(
                commands[0][0][0], self._y(commands[0][0][1]),
                commands[0][1][0], self._y(commands[0][1][1]),
                commands[0][2][0], self._y(commands[0][2][1]),
            )
            path.lineTo(commands[1][2][0], self._y(commands[1][2][1]))
            path.curveTo(
                commands[2][0][0], self._y(commands[2][0][1]),
                commands[2][1][0], self._y(commands[2][1][1]),
                commands[2][2][0], self._y(commands[2][2][1]),
            )
            path.close()
            canvas.drawPath(path, stroke=1, fill=1)
            if element.hatch:
                self._draw_vector_hatch(canvas, element)
                self._redraw_outline(canvas, element, path)
            top_start, top_control_1, top_control_2, top_end = geometry.top_arc
            top_arc = canvas.beginPath()
            top_arc.moveTo(top_start[0], self._y(top_start[1]))
            top_arc.curveTo(
                top_control_1[0], self._y(top_control_1[1]),
                top_control_2[0], self._y(top_control_2[1]),
                top_end[0], self._y(top_end[1]),
            )
            canvas.drawPath(top_arc, stroke=1, fill=0)
            return
        else:
            path = self._draw_rect_path(canvas, element)
        canvas.drawPath(path, stroke=1, fill=1)
        if element.hatch:
            self._draw_vector_hatch(canvas, element)
            self._redraw_outline(canvas, element, path)

    def render(self, scene: Scene) -> None:
        register_carlito_fonts()
        self.output_path.parent.mkdir(parents=True, exist_ok=True)
        canvas = Canvas(
            str(self.output_path),
            pagesize=(self.width, self.height),
            pageCompression=1,
            invariant=1,
        )
        canvas.setTitle(scene.title or "VEGO-AI proposal visual")
        canvas.setAuthor("VEGO-AI proposal visual system")
        canvas.setCreator("VEGO-AI deterministic vector renderer")
        canvas.setSubject(scene.description)
        canvas.setKeywords(_scene_semantics(scene))
        for element in scene.elements:
            self._element(canvas, element)
        canvas.showPage()
        canvas.save()


def render_pdf(scene: Scene, output_path: Path) -> None:
    validate_scene(scene)
    PdfRenderer(output_path, scene.width, scene.height).render(scene)
