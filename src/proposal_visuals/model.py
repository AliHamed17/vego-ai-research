"""Immutable, top-left-coordinate scene primitives for proposal figures."""

from __future__ import annotations

import math
import re
from dataclasses import dataclass, field
from typing import TypeAlias

from proposal_visuals.fonts import measure_carlito
from proposal_visuals.tokens import DEFAULT_TOKENS

Point: TypeAlias = tuple[float, float]
DashStyle: TypeAlias = str
_METADATA_KEY = re.compile(r"^[a-z][a-z0-9_-]*$")
_ALLOWED_PAINTS = frozenset(color.value for color in DEFAULT_TOKENS.colors.values())
_ALLOWED_HATCHES = frozenset({"diagonal"})
HATCH_STROKE_WIDTH = 0.7


class SceneValidationError(ValueError):
    """Raised before a scene that could clip or mislead is rendered."""


def _wrapped_lines(
    value: str, font_size: float, max_width: float | None, weight: str
) -> tuple[str, ...]:
    if max_width is None:
        return tuple(value.splitlines() or [value])
    lines: list[str] = []
    for paragraph in value.splitlines() or [value]:
        current = ""
        for word in paragraph.split() or [""]:
            if measure_carlito(word, font_size, weight) > max_width:
                raise SceneValidationError("text token does not fit measured max width")
            candidate = word if not current else f"{current} {word}"
            if current and measure_carlito(candidate, font_size, weight) > max_width:
                lines.append(current)
                current = word
            else:
                current = candidate
        lines.append(current)
    return tuple(lines)


def text_lines(text: Text) -> tuple[str, ...]:
    """Wrap with one pinned-Carlito metric path shared by SVG and PDF."""
    return _wrapped_lines(text.value, text.font_size, text.max_width, text.weight)


def text_bounds(text: Text) -> tuple[float, float, float, float]:
    lines = text_lines(text)
    width = max((measure_carlito(line, text.font_size, text.weight) for line in lines), default=0.0)
    height = len(lines) * text.font_size * text.leading
    return text.x, text.y, width, height


@dataclass(frozen=True)
class Text:
    x: float
    y: float
    value: str
    font_size: float
    max_width: float | None = None
    leading: float = 1.2
    fill: str = "#172033"
    background: str = "#FFFFFF"
    weight: str = "regular"
    semantic_role: str = "label"


@dataclass(frozen=True)
class Rect:
    x: float
    y: float
    width: float
    height: float
    fill: str = "#F2F4F7"
    stroke: str = "#172033"
    line_width: float = 1.2
    dash: DashStyle = "solid"
    hatch: str | None = None
    semantic_role: str = "artifact"
    label: str | None = None


def rect_hatch_segments(
    rectangle: Rect, *, spacing: float = 6.0
) -> tuple[tuple[Point, Point], ...]:
    """Return globally phased diagonal segments clipped to a plain rectangle."""

    if not math.isfinite(spacing) or spacing <= 0:
        raise SceneValidationError("hatch spacing must be positive and finite")
    x_min, y_min = rectangle.x, rectangle.y
    x_max = rectangle.x + rectangle.width
    y_max = rectangle.y + rectangle.height
    first = math.ceil((x_min + y_min) / spacing) * spacing
    last = x_max + y_max
    count = max(0, math.floor((last - first) / spacing) + 1)
    segments: list[tuple[Point, Point]] = []
    epsilon = 1e-9
    for index in range(count):
        diagonal = first + index * spacing
        candidates = (
            (x_min, diagonal - x_min),
            (x_max, diagonal - x_max),
            (diagonal - y_min, y_min),
            (diagonal - y_max, y_max),
        )
        points: list[Point] = []
        for x, y in candidates:
            if not (
                x_min - epsilon <= x <= x_max + epsilon
                and y_min - epsilon <= y <= y_max + epsilon
            ):
                continue
            point = (
                min(x_max, max(x_min, x)),
                min(y_max, max(y_min, y)),
            )
            if not any(
                abs(point[0] - seen[0]) <= epsilon
                and abs(point[1] - seen[1]) <= epsilon
                for seen in points
            ):
                points.append(point)
        if len(points) == 2:
            segments.append((points[0], points[1]))
    return tuple(segments)


@dataclass(frozen=True)
class RoundedRect(Rect):
    radius: float = 4.0
    semantic_role: str = "process"


@dataclass(frozen=True)
class Diamond(Rect):
    semantic_role: str = "decision"


@dataclass(frozen=True)
class Cylinder(Rect):
    semantic_role: str = "store"


@dataclass(frozen=True)
class CylinderGeometry:
    """Shared cylinder outline and top-ellipse geometry, all inside shape bounds."""

    outline_start: Point
    outline_commands: tuple[tuple[Point, Point, Point], ...]
    top_arc: tuple[Point, Point, Point, Point]

    def all_points(self) -> tuple[Point, ...]:
        points = [self.outline_start]
        for command in self.outline_commands:
            points.extend(command)
        points.extend(self.top_arc)
        return tuple(points)


def cylinder_geometry(cylinder: Cylinder) -> CylinderGeometry:
    """Return a bounded top-left-coordinate cylinder path for both backends."""
    x, y, width, height = cylinder.x, cylinder.y, cylinder.width, cylinder.height
    radius_y = min(height / 6, width / 8)
    left_top, right_top = (x, y + radius_y), (x + width, y + radius_y)
    right_bottom, left_bottom = (x + width, y + height - radius_y), (x, y + height - radius_y)
    return CylinderGeometry(
        outline_start=left_top,
        outline_commands=(
            ((x, y), (x + width, y), right_top),
            (right_bottom, right_bottom, right_bottom),
            ((x + width, y + height), (x, y + height), left_bottom),
            (left_top, left_top, left_top),
        ),
        top_arc=(left_top, (x, y + 2 * radius_y), (x + width, y + 2 * radius_y), right_top),
    )


@dataclass(frozen=True)
class Parallelogram(Rect):
    skew: float = 8.0
    semantic_role: str = "human_judgment"


def hatch_region(shape: Rect) -> Rect:
    """Return an axis-aligned region proven to stay inside a hatchable shape."""

    stroke_inset = HATCH_STROKE_WIDTH / 2
    if type(shape) is Rect:
        inset_x = inset_y = stroke_inset
    elif isinstance(shape, RoundedRect):
        inset_x = inset_y = shape.radius + stroke_inset
    elif isinstance(shape, Cylinder):
        inset_x = inset_y = min(shape.height / 6, shape.width / 8) + stroke_inset
    elif isinstance(shape, Diamond):
        inset_x = shape.width / 4 + stroke_inset
        inset_y = shape.height / 4 + stroke_inset
    elif isinstance(shape, Parallelogram):
        inset_x, inset_y = abs(shape.skew) + stroke_inset, stroke_inset
    else:
        raise SceneValidationError(f"unsupported hatched shape: {type(shape).__name__}")
    width = shape.width - 2 * inset_x
    height = shape.height - 2 * inset_y
    if width <= 0 or height <= 0:
        raise SceneValidationError("hatched shape has no safe interior region")
    return Rect(shape.x + inset_x, shape.y + inset_y, width, height)


@dataclass(frozen=True)
class Arrowhead:
    """A real polygon, never a backend marker, for directional flow."""

    points: tuple[Point, ...]


@dataclass(frozen=True)
class Polyline:
    points: tuple[Point, ...]
    arrowhead: Arrowhead | None = None
    stroke: str = "#172033"
    line_width: float = 1.2
    dash: DashStyle = "solid"
    semantic_role: str = "flow"


@dataclass(frozen=True)
class Group:
    elements: tuple[Element, ...]
    semantic_role: str = "group"
    metadata: tuple[tuple[str, str], ...] = field(default_factory=tuple)


Element: TypeAlias = Text | Rect | RoundedRect | Diamond | Cylinder | Parallelogram | Polyline | Group


@dataclass(frozen=True)
class Scene:
    width: float
    height: float
    elements: tuple[Element, ...]
    title: str = ""
    description: str = ""


def _assert_bounds(scene: Scene, bounds: tuple[float, float, float, float], kind: str) -> None:
    x, y, width, height = bounds
    if x < 0 or y < 0 or x + width > scene.width or y + height > scene.height:
        raise SceneValidationError(f"{kind} outside artboard")


def _validate_finite(**values: float | None) -> None:
    """Reject NaN and infinities before any geometry comparison or emission."""
    for name, value in values.items():
        if value is None:
            continue
        try:
            finite = math.isfinite(value)
        except TypeError as error:
            raise SceneValidationError(f"{name} must be finite") from error
        if not finite:
            raise SceneValidationError(f"{name} must be finite")


def _validate_dash(dash: DashStyle) -> None:
    if dash not in {"solid", "dashed", "dotted"}:
        raise SceneValidationError(f"unknown dash style: {dash}")


def _validate_paint(value: str) -> None:
    if value not in _ALLOWED_PAINTS:
        raise SceneValidationError(f"unapproved paint value: {value}")


def _validate_hatch(hatch: str | None) -> None:
    if hatch is not None and hatch not in _ALLOWED_HATCHES:
        raise SceneValidationError(f"unapproved hatch paint: {hatch}")


def _validate_element(scene: Scene, element: Element) -> None:
    if isinstance(element, Group):
        if not element.semantic_role:
            raise SceneValidationError("group needs semantic role metadata")
        metadata_keys = [key for key, _ in element.metadata]
        if len(set(metadata_keys)) != len(metadata_keys):
            raise SceneValidationError("group metadata keys must be unique")
        if any(
            not _METADATA_KEY.fullmatch(key) or not value for key, value in element.metadata
        ):
            raise SceneValidationError("group metadata must use nonblank safe keys and values")
        for child in element.elements:
            _validate_element(scene, child)
        return
    if not element.semantic_role:
        raise SceneValidationError("element needs semantic role metadata")
    if isinstance(element, Text):
        _validate_finite(
            text_x=element.x,
            text_y=element.y,
            text_font_size=element.font_size,
            text_max_width=element.max_width,
            text_leading=element.leading,
        )
        if not element.value:
            raise SceneValidationError("text must not be empty")
        if element.font_size < DEFAULT_TOKENS.body_text_pt:
            raise SceneValidationError("text below 7 pt")
        if element.leading < 1:
            raise SceneValidationError("text leading must be at least 1")
        if element.max_width is not None and element.max_width <= 0:
            raise SceneValidationError("text max width must be positive")
        if element.weight not in {"regular", "bold"}:
            raise SceneValidationError("unsupported text weight")
        _validate_paint(element.fill)
        _validate_paint(element.background)
        try:
            DEFAULT_TOKENS.assert_text_contrast(element.fill, element.background)
        except ValueError as error:
            raise SceneValidationError(str(error)) from error
        _assert_bounds(scene, text_bounds(element), "text")
        return
    if isinstance(element, Polyline):
        if len(element.points) < 2:
            raise SceneValidationError("polyline needs at least two points")
        if element.arrowhead is None or len(element.arrowhead.points) < 3:
            raise SceneValidationError("polyline needs an explicit arrowhead polygon")
        _validate_finite(polyline_line_width=element.line_width)
        for point_index, (x, y) in enumerate(element.points):
            _validate_finite(**{f"polyline_point_{point_index}_x": x, f"polyline_point_{point_index}_y": y})
        for point_index, (x, y) in enumerate(element.arrowhead.points):
            _validate_finite(
                **{f"arrowhead_point_{point_index}_x": x, f"arrowhead_point_{point_index}_y": y}
            )
        if element.line_width <= 0:
            raise SceneValidationError("polyline line width must be positive")
        _validate_paint(element.stroke)
        _validate_dash(element.dash)
        all_points = (*element.points, *element.arrowhead.points)
        min_x, min_y = min(x for x, _ in all_points), min(y for _, y in all_points)
        max_x, max_y = max(x for x, _ in all_points), max(y for _, y in all_points)
        bleed = element.line_width / 2
        _assert_bounds(
            scene,
            (min_x - bleed, min_y - bleed, max_x - min_x + 2 * bleed, max_y - min_y + 2 * bleed),
            "polyline",
        )
        return
    _validate_finite(
        shape_x=element.x,
        shape_y=element.y,
        shape_width=element.width,
        shape_height=element.height,
        shape_line_width=element.line_width,
    )
    if isinstance(element, RoundedRect):
        _validate_finite(rounded_rect_radius=element.radius)
    if isinstance(element, Parallelogram):
        _validate_finite(parallelogram_skew=element.skew)
    if element.width <= 0 or element.height <= 0:
        raise SceneValidationError("shape dimensions must be positive")
    if element.line_width <= 0:
        raise SceneValidationError("shape line width must be positive")
    _validate_paint(element.fill)
    _validate_paint(element.stroke)
    _validate_hatch(element.hatch)
    _validate_dash(element.dash)
    if isinstance(element, RoundedRect) and (element.radius < 0 or element.radius * 2 > min(element.width, element.height)):
        raise SceneValidationError("rounded rectangle radius is invalid")
    if isinstance(element, Parallelogram) and abs(element.skew) * 2 >= element.width:
        raise SceneValidationError("parallelogram skew is invalid")
    if element.hatch:
        hatch_region(element)
    bleed = element.line_width / 2
    _assert_bounds(
        scene,
        (element.x - bleed, element.y - bleed, element.width + 2 * bleed, element.height + 2 * bleed),
        "shape",
    )


def validate_scene(scene: Scene) -> None:
    """Reject invalid geometry, inaccessible text, and clipping before output."""
    _validate_finite(scene_width=scene.width, scene_height=scene.height)
    if scene.width <= 0 or scene.height <= 0:
        raise SceneValidationError("artboard dimensions must be positive")
    for element in scene.elements:
        _validate_element(scene, element)
