"""Immutable, provenance-bound proposal content for reproducible figures."""

from __future__ import annotations

import hashlib
import json
import re
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from types import MappingProxyType
from typing import Any

from pypdf import PdfReader
from pypdf.errors import PdfReadError

SHA256_RE = re.compile(r"^[0-9A-Fa-f]{64}$")
PAGE_LOCATOR_RE = re.compile(r"\bPDF p{1,2}\.?\s+\d+", re.IGNORECASE)
SECTION_OR_TABLE_LOCATOR_RE = re.compile(r"(?:§\s*\d|Table\s+\d)", re.IGNORECASE)


class FrozenList(tuple[Any, ...]):
    """An immutable sequence that compares naturally with JSON lists."""

    def __eq__(self, other: object) -> bool:
        if isinstance(other, list):
            return list(self) == other
        return super().__eq__(other)


def _freeze(value: Any) -> Any:
    if isinstance(value, Mapping):
        return MappingProxyType({key: _freeze(item) for key, item in value.items()})
    if isinstance(value, list):
        return FrozenList(_freeze(item) for item in value)
    return value


def _required_string(mapping: Mapping[str, Any], key: str) -> str:
    value = mapping.get(key)
    if not isinstance(value, str) or not value:
        raise ValueError(f"figure {key} must be a non-empty string")
    return value


def _validated_locators(figure_id: str, locators: Any) -> tuple[str, ...]:
    if not isinstance(locators, list) or not locators:
        raise ValueError(f"{figure_id} locators must be a non-empty list of strings")
    if not all(isinstance(locator, str) and locator.strip() for locator in locators):
        raise ValueError(f"{figure_id} locators must not be blank")
    if not any(PAGE_LOCATOR_RE.search(locator) for locator in locators):
        raise ValueError(f"{figure_id} locators must include a PDF page")
    if not any(SECTION_OR_TABLE_LOCATOR_RE.search(locator) for locator in locators):
        raise ValueError(f"{figure_id} locators must include a section or table")
    return tuple(locators)


@dataclass(frozen=True)
class FigureContent:
    figure_id: str
    title: str
    caption: str
    provenance: str
    alt_text: str
    locators: tuple[str, ...]
    items: Mapping[str, Any]

    @classmethod
    def from_mapping(cls, figure_id: str, payload: Mapping[str, Any]) -> FigureContent:
        locators = payload.get("locators")
        items = payload.get("items")
        if not isinstance(items, Mapping):
            raise ValueError(f"{figure_id} items must be a mapping")
        return cls(
            figure_id=figure_id,
            title=_required_string(payload, "title"),
            caption=_required_string(payload, "caption"),
            provenance=_required_string(payload, "provenance"),
            alt_text=_required_string(payload, "alt_text"),
            locators=_validated_locators(figure_id, locators),
            items=_freeze(items),
        )


@dataclass(frozen=True)
class VisualContent:
    figures: Mapping[str, FigureContent]

    @classmethod
    def from_mapping(cls, payload: Mapping[str, Any]) -> VisualContent:
        figures = payload.get("figures")
        if not isinstance(figures, Mapping):
            raise ValueError("content must contain a figures mapping")
        return cls(
            figures=MappingProxyType(
                {
                    figure_id: FigureContent.from_mapping(figure_id, figure_payload)
                    for figure_id, figure_payload in figures.items()
                    if isinstance(figure_payload, Mapping)
                }
            )
        )


@dataclass(frozen=True)
class SourceProvenance:
    filename: str
    media_type: str
    sha256: str
    proposal_date: str
    page_count: int
    authority: str


def load_source_provenance(path: Path) -> SourceProvenance:
    """Load a validated PDF provenance receipt for a render input."""
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, Mapping):
        raise ValueError("source provenance must be a mapping")
    artifact = payload.get("source_artifact")
    if not isinstance(artifact, Mapping):
        raise ValueError("source provenance must contain source_artifact")

    filename = _required_string(artifact, "filename")
    media_type = _required_string(artifact, "media_type")
    sha256 = _required_string(artifact, "sha256")
    proposal_date = _required_string(artifact, "proposal_date")
    authority = _required_string(artifact, "authority")
    page_count = artifact.get("page_count")

    if media_type != "application/pdf" or not filename.lower().endswith(".pdf"):
        raise ValueError("source artifact must be application/pdf")
    if not SHA256_RE.fullmatch(sha256):
        raise ValueError("source artifact SHA-256 must be a 64-character hexadecimal digest")
    if not isinstance(page_count, int) or isinstance(page_count, bool) or page_count < 1:
        raise ValueError("source artifact page_count must be a positive integer")

    return SourceProvenance(
        filename=filename,
        media_type=media_type,
        sha256=sha256.upper(),
        proposal_date=proposal_date,
        page_count=page_count,
        authority=authority,
    )


def load_content(path: Path) -> VisualContent:
    """Load the ordered figure manifest without permitting source-content drift."""
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, Mapping):
        raise ValueError("content manifest must be a mapping")
    figures = payload.get("figures")
    expected = [f"fig-{number:02d}" for number in range(1, 12)]
    if not isinstance(figures, Mapping) or list(figures) != expected:
        raise ValueError("figure IDs must be ordered fig-01 through fig-11")
    content = VisualContent.from_mapping(payload)
    if len(content.figures) != len(expected):
        raise ValueError("every figure payload must be a mapping")
    return content


def verify_source_hash(path: Path, expected: str) -> None:
    """Fail closed when the PDF bytes no longer match frozen provenance."""
    actual = hashlib.sha256(path.read_bytes()).hexdigest().upper()
    if actual != expected.upper():
        raise ValueError(f"source drift: expected {expected}, got {actual}")


def verify_source_pdf(path: Path, provenance: SourceProvenance) -> None:
    """Verify that an actual PDF matches its frozen source receipt."""
    if path.suffix.lower() != ".pdf" or path.name != provenance.filename:
        raise ValueError("source PDF does not match recorded filename")
    verify_source_hash(path, provenance.sha256)
    try:
        actual_page_count = len(PdfReader(path).pages)
    except (OSError, PdfReadError) as error:
        raise ValueError("source PDF is unreadable") from error
    if actual_page_count != provenance.page_count:
        raise ValueError(
            f"source page count drift: expected {provenance.page_count}, got {actual_page_count}"
        )


def load_verified_content(
    content_path: Path, provenance_path: Path, source_pdf_path: Path
) -> VisualContent:
    """Verify the recorded PDF before providing content to a renderer."""
    provenance = load_source_provenance(provenance_path)
    verify_source_pdf(source_pdf_path, provenance)
    return load_content(content_path)
