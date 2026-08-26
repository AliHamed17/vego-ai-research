"""Immutable visual tokens for the proposal's accessible vector figures."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from types import MappingProxyType


@dataclass(frozen=True)
class Color:
    """An sRGB colour whose contrast can be evaluated locally."""

    value: str

    def __post_init__(self) -> None:
        if len(self.value) != 7 or not self.value.startswith("#"):
            raise ValueError("colour values must be #RRGGBB")
        try:
            int(self.value[1:], 16)
        except ValueError as error:
            raise ValueError("colour values must be #RRGGBB") from error

    def rgb(self) -> tuple[float, float, float]:
        return (
            int(self.value[1:3], 16) / 255,
            int(self.value[3:5], 16) / 255,
            int(self.value[5:7], 16) / 255,
        )


def _linear(channel: float) -> float:
    return channel / 12.92 if channel <= 0.04045 else ((channel + 0.055) / 1.055) ** 2.4


def contrast_ratio(foreground: Color, background: Color) -> float:
    """Return the WCAG relative-luminance contrast ratio."""
    weights = (0.2126, 0.7152, 0.0722)
    fg_luminance = sum(
        weight * _linear(value) for weight, value in zip(weights, foreground.rgb(), strict=True)
    )
    bg_luminance = sum(
        weight * _linear(value) for weight, value in zip(weights, background.rgb(), strict=True)
    )
    lighter, darker = max(fg_luminance, bg_luminance), min(fg_luminance, bg_luminance)
    return (lighter + 0.05) / (darker + 0.05)


@dataclass(frozen=True)
class VisualTokens:
    """Shared, WCAG-capable semantic roles used by both rendering backends."""

    colors: Mapping[str, Color]
    font_family: str = "Carlito"
    body_text_pt: float = 7.0
    line_width: float = 1.2

    @classmethod
    def proposal(cls) -> VisualTokens:
        return cls(
            colors=MappingProxyType(
                {
                    "background": Color("#FFFFFF"),
                    "ink": Color("#172033"),
                    "existing": Color("#17365D"),
                    "human_judgment": Color("#A84A00"),
                    "conditional": Color("#5F6B7A"),
                    "neutral_fill": Color("#F2F4F7"),
                }
            )
        )

    def assert_text_contrast(self, foreground: str, background: str) -> None:
        ratio = contrast_ratio(Color(foreground), Color(background))
        if ratio < 4.5:
            raise ValueError(f"text contrast {ratio:.2f}:1 is below WCAG 4.5:1")


DEFAULT_TOKENS = VisualTokens.proposal()
