#!/usr/bin/env python3
"""Minimal SVG drawing helpers for publication figures.

Why this exists: SVG `marker-end` arrowheads are silently dropped by several
renderers (svglib among them), which produces a directed diagram with no
direction. Every arrowhead here is emitted as explicit polygon geometry, so the
figure looks identical in a browser, in Word, and in print.

Coordinates are plain SVG user units; the caller sets the viewBox.
"""
from __future__ import annotations

import math

# House palette - matches the document template.
NAVY = "#1b2a4a"
BLUE = "#2f5aa8"
GREEN = "#1e8e5a"
PURPLE = "#6b3fa0"
AMBER = "#c8860d"
RED = "#b3261e"
INK = "#1f2430"
GREY = "#5b6472"
LINE = "#44506b"
RULE = "#c3cad8"
PANEL = "#fafbfd"

FONT = "Calibri, 'Segoe UI', Arial, sans-serif"


def esc(t: str) -> str:
    return (str(t).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


class Fig:
    def __init__(self, w: int, h: int, bg: str = "#ffffff"):
        self.w, self.h = w, h
        self.parts: list[str] = []
        self.parts.append(
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" '
            f'width="{w}" height="{h}" font-family="{FONT}">'
        )
        self.parts.append(f'<rect width="{w}" height="{h}" fill="{bg}"/>')

    # ---------- primitives ----------
    def rect(self, x, y, w, h, fill="#ffffff", stroke=None, sw=1.3, r=8, dash=None):
        d = f' stroke-dasharray="{dash}"' if dash else ""
        s = f' stroke="{stroke}" stroke-width="{sw}"' if stroke else ""
        self.parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" ry="{r}" fill="{fill}"{s}{d}/>')

    def text(self, x, y, s, size=12, fill=INK, anchor="middle", weight=None, italic=False, spacing=None):
        w = f' font-weight="{weight}"' if weight else ""
        i = ' font-style="italic"' if italic else ""
        ls = f' letter-spacing="{spacing}"' if spacing else ""
        self.parts.append(
            f'<text x="{x}" y="{y}" font-size="{size}" fill="{fill}" '
            f'text-anchor="{anchor}"{w}{i}{ls}>{esc(s)}</text>'
        )

    def lines(self, x, y, items, size=12, fill=INK, anchor="middle", lh=16, weight=None):
        """Multi-line text block; y is the baseline of the first line."""
        for k, s in enumerate(items):
            self.text(x, y + k * lh, s, size=size, fill=fill, anchor=anchor, weight=weight)

    def path(self, d, stroke=LINE, sw=1.4, fill="none", dash=None):
        dd = f' stroke-dasharray="{dash}"' if dash else ""
        self.parts.append(f'<path d="{d}" stroke="{stroke}" stroke-width="{sw}" fill="{fill}"{dd}/>')

    # ---------- arrowheads ----------
    def _head(self, x, y, angle, color, size=9.0):
        """Filled triangle with its tip at (x, y), pointing along `angle` (radians)."""
        back = angle + math.pi
        spread = math.radians(22)
        x1 = x + size * math.cos(back - spread)
        y1 = y + size * math.sin(back - spread)
        x2 = x + size * math.cos(back + spread)
        y2 = y + size * math.sin(back + spread)
        self.parts.append(
            f'<polygon points="{x:.1f},{y:.1f} {x1:.1f},{y1:.1f} {x2:.1f},{y2:.1f}" fill="{color}"/>'
        )

    def arrow(self, pts, color=LINE, sw=1.4, head=True, head_size=9.0, dash=None, both=False):
        """Orthogonal or straight polyline with a real arrowhead at the end.

        pts: [(x, y), ...]. The head is aligned to the final segment, and the line
        is shortened so it meets the base of the head rather than poking through it.
        """
        pts = [(float(a), float(b)) for a, b in pts]
        if head and len(pts) >= 2:
            (x0, y0), (x1, y1) = pts[-2], pts[-1]
            ang = math.atan2(y1 - y0, x1 - x0)
            shrink = head_size * 0.85
            pts[-1] = (x1 - shrink * math.cos(ang), y1 - shrink * math.sin(ang))
        if both and len(pts) >= 2:
            (x0, y0), (x1, y1) = pts[1], pts[0]
            ang0 = math.atan2(y1 - y0, x1 - x0)
            shrink = head_size * 0.85
            pts[0] = (x1 - shrink * math.cos(ang0), y1 - shrink * math.sin(ang0))
        d = "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in pts)
        self.path(d, stroke=color, sw=sw, dash=dash)
        if head:
            (x0, y0), (x1, y1) = pts[-2], pts[-1]
            ang = math.atan2(y1 - y0, x1 - x0)
            self._head(x1 + head_size * 0.85 * math.cos(ang),
                       y1 + head_size * 0.85 * math.sin(ang), ang, color, head_size)
        if both:
            (x0, y0), (x1, y1) = pts[1], pts[0]
            ang = math.atan2(y1 - y0, x1 - x0)
            self._head(x1 + head_size * 0.85 * math.cos(ang),
                       y1 + head_size * 0.85 * math.sin(ang), ang, color, head_size)

    # ---------- composites ----------
    def box(self, x, y, w, h, title, subtitle=None, fill=BLUE, tcolor="#ffffff",
            scolor="#e8edf7", tsize=15, ssize=11.5, r=8, stroke=None, sw=1.3):
        self.rect(x, y, w, h, fill=fill, stroke=stroke, sw=sw, r=r)
        cx = x + w / 2
        if subtitle:
            subs = subtitle if isinstance(subtitle, list) else [subtitle]
            top = y + h / 2 - (len(subs) * 15) / 2 - 2
            self.text(cx, top, title, size=tsize, fill=tcolor, weight="700")
            for k, s in enumerate(subs):
                self.text(cx, top + 19 + k * 15, s, size=ssize, fill=scolor)
        else:
            self.text(cx, y + h / 2 + tsize * 0.35, title, size=tsize, fill=tcolor, weight="700")

    def caption(self, x, y, bold, normal=None, width_hint=None):
        self.text(x, y, bold, size=13.5, fill=NAVY, weight="700")
        if normal:
            self.text(x, y + 20, normal, size=11.5, fill=GREY)

    def save(self, path: str) -> None:
        self.parts.append("</svg>")
        with open(path, "w", encoding="utf-8") as fh:
            fh.write("\n".join(self.parts))
