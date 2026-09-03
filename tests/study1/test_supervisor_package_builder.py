"""Regression tests for the September 3 supervisor document builder."""

from __future__ import annotations

import zipfile

import pytest

docx = pytest.importorskip("docx")
Document = docx.Document

from scripts.build_20260903_supervisor_package import (  # noqa: E402
    _add_table,
    _inline,
    build_one_page,
)


def test_inline_turns_a_plain_https_url_into_a_docx_hyperlink(tmp_path) -> None:
    document = Document()
    paragraph = document.add_paragraph()
    url = "https://doi.org/10.1145/3290605.3300233"

    _inline(paragraph, f"Amershi et al. {url}.", size=9.6)

    destination = tmp_path / "hyperlink.docx"
    document.save(destination)
    with zipfile.ZipFile(destination) as archive:
        relationships = archive.read("word/_rels/document.xml.rels").decode("utf-8")
        document_xml = archive.read("word/document.xml").decode("utf-8")

    assert url in relationships
    assert f'{url}."' not in relationships
    word_prefix = "w"
    assert f"{word_prefix}:hyperlink" in document_xml


def test_inline_renders_single_asterisk_emphasis_as_italics(tmp_path) -> None:
    document = Document()
    paragraph = document.add_paragraph()

    _inline(paragraph, "Published in *Journal of Controlled Evidence*.", size=9.6)

    destination = tmp_path / "italics.docx"
    document.save(destination)
    with zipfile.ZipFile(destination) as archive:
        document_xml = archive.read("word/document.xml").decode("utf-8")

    word_prefix = "w"
    assert f"<{word_prefix}:i" in document_xml
    assert "*Journal of Controlled Evidence*" not in document_xml


def test_inline_renders_relative_markdown_link_as_clean_label(tmp_path) -> None:
    document = Document()
    paragraph = document.add_paragraph()

    _inline(paragraph, "See [`controlled protocol`](study1-protocol.md).", size=9.6)

    destination = tmp_path / "relative-link.docx"
    document.save(destination)
    with zipfile.ZipFile(destination) as archive:
        relationships = archive.read("word/_rels/document.xml.rels").decode("utf-8")
        document_xml = archive.read("word/document.xml").decode("utf-8")

    assert "controlled protocol" in document_xml
    assert "[`controlled protocol`](study1-protocol.md)" not in document_xml
    assert "`controlled protocol`" not in document_xml
    assert "study1-protocol.md" not in relationships


def test_one_page_builder_does_not_drop_body_when_source_heading_changes(tmp_path) -> None:
    destination = build_one_page({}, tmp_path)

    document = Document(destination)
    text = "\n".join(paragraph.text for paragraph in document.paragraphs)
    table_text = "\n".join(
        cell.text for table in document.tables for row in table.rows for cell in row.cells
    )

    assert "Question, data, and claim boundary" in text
    assert "Measurable now versus evidence still required" in text
    assert "Recorded-change coverage" in table_text
    assert "Tomorrow: show, decide, then measure prospectively" in text


def test_table_cells_are_left_aligned_to_avoid_justified_word_gaps() -> None:
    document = Document()

    _add_table(document, [["Measure", "Formula"], ["Review load", "selected / eligible"]])

    for row in document.tables[0].rows:
        for cell in row.cells:
            assert cell.paragraphs[0].alignment == 0
