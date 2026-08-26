"""Pinned local Carlito font access for vector renderers."""

from __future__ import annotations

import base64
import hashlib
import json
from collections.abc import Mapping
from pathlib import Path
from types import MappingProxyType

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

FONT_DIRECTORY = (
    Path(__file__).resolve().parents[2]
    / "docs"
    / "research"
    / "phd-proposal"
    / "figures"
    / "vendor"
    / "fonts"
)
FONT_MANIFEST = FONT_DIRECTORY / "manifest.json"
_FONT_NAMES = {"regular": "Carlito", "bold": "Carlito-Bold"}


def _manifest() -> Mapping[str, object]:
    payload = json.loads(FONT_MANIFEST.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise RuntimeError("vendored font manifest must be an object")
    return payload


def font_path(weight: str = "regular") -> Path:
    filename = {"regular": "Carlito-Regular.ttf", "bold": "Carlito-Bold.ttf"}.get(weight)
    if filename is None:
        raise ValueError(f"unsupported Carlito weight: {weight}")
    return FONT_DIRECTORY / filename


def font_name(weight: str = "regular") -> str:
    try:
        return _FONT_NAMES[weight]
    except KeyError as error:
        raise ValueError(f"unsupported Carlito weight: {weight}") from error


def _receipt_entries(manifest: Mapping[str, object]) -> Mapping[str, Mapping[str, object]]:
    fonts = manifest.get("fonts")
    license_receipt = manifest.get("license")
    if not isinstance(fonts, dict) or not isinstance(license_receipt, dict):
        raise RuntimeError("vendored font manifest needs fonts and license receipts")
    entries: dict[str, Mapping[str, object]] = dict(fonts)
    license_file = license_receipt.get("file")
    if not isinstance(license_file, str):
        raise RuntimeError("vendored font license receipt needs a file")
    entries[license_file] = license_receipt
    return entries


def verify_vendored_fonts() -> Mapping[str, Mapping[str, object]]:
    """Verify URL, byte count, and digest for every committed font receipt."""
    entries = _receipt_entries(_manifest())
    expected = {"Carlito-Regular.ttf", "Carlito-Bold.ttf", "OFL.txt"}
    if set(entries) != expected:
        raise RuntimeError("vendored font manifest files do not match the approved receipt")
    verified: dict[str, Mapping[str, object]] = {}
    for filename in sorted(entries):
        record = entries[filename]
        url, size, digest = record.get("url"), record.get("bytes"), record.get("sha256")
        if not isinstance(url, str) or not url.startswith("https://raw.githubusercontent.com/google/fonts/"):
            raise RuntimeError(f"vendored font receipt has an invalid URL: {filename}")
        if not isinstance(size, int) or isinstance(size, bool) or size < 1:
            raise RuntimeError(f"vendored font receipt has an invalid byte count: {filename}")
        if not isinstance(digest, str) or len(digest) != 64:
            raise RuntimeError(f"vendored font receipt has an invalid SHA-256: {filename}")
        data = (FONT_DIRECTORY / filename).read_bytes()
        if len(data) != size or hashlib.sha256(data).hexdigest().upper() != digest:
            raise RuntimeError(f"vendored font integrity check failed: {filename}")
        verified[filename] = MappingProxyType({"url": url, "bytes": size, "sha256": digest})
    return MappingProxyType(verified)


def verified_font_bytes(weight: str = "regular") -> bytes:
    path = font_path(weight)
    verify_vendored_fonts()
    return path.read_bytes()


def register_carlito_fonts() -> None:
    """Register the pinned TTFs once for shared ReportLab metrics and PDF output."""
    for weight in _FONT_NAMES:
        name = font_name(weight)
        verified_font_bytes(weight)
        if name not in pdfmetrics.getRegisteredFontNames():
            pdfmetrics.registerFont(TTFont(name, str(font_path(weight))))


def measure_carlito(value: str, font_size: float, weight: str = "regular") -> float:
    """Measure text with the same pinned Carlito TTF used by the PDF renderer."""
    if font_size <= 0:
        raise ValueError("font size must be positive")
    register_carlito_fonts()
    return pdfmetrics.stringWidth(value, font_name(weight), font_size)


def svg_font_data_uri(weight: str = "regular") -> str:
    return "data:font/ttf;base64," + base64.b64encode(verified_font_bytes(weight)).decode("ascii")
