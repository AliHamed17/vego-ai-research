from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path
from xml.etree import ElementTree
from zipfile import ZIP_DEFLATED, ZipFile

import pytest

from proposal_visuals.docx_layout import (
    REVIEW_SOURCE_ROLES_PREFIX,
    LayoutContractError,
    materialize_review_keep_lines,
)

W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
NS = {"w": W_NS}
MC_NS = "http://schemas.openxmlformats.org/markup-compatibility/2006"
W15_NS = "http://schemas.microsoft.com/office/word/2012/wordml"

REVIEW_SOURCE_ROLES_TEXT = (
    "Source roles are fixed in advance: ACM Digital Library, IEEE Xplore, Scopus, and Web of "
    "Science as primary databases; PubMed conditionally, for the medical scenario only; and "
    "Google Scholar for snowballing only, never as a primary source. Each query line carries an "
    "audit record giving the database, the Boolean expression as executed, field and document-type "
    "restrictions, language and date filters, the execution date, the returned, screened, and "
    "included counts, the searcher, and an export identifier. The five query families and their "
    "canonical Boolean expressions are frozen and registered before execution; the per-platform "
    "field wrappers and filters are recorded at execution, which is the point at which they can be "
    "stated accurately."
)


def _document_xml(*, target_count: int = 1, target_text: str = REVIEW_SOURCE_ROLES_TEXT) -> str:
    targets = "".join(
        (
            '<w:p><w:pPr><w:spacing w:after="100"/><w:jc w:val="both"/></w:pPr>'
            f"<w:r><w:t>{target_text}</w:t></w:r></w:p>"
        )
        for _ in range(target_count)
    )
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\r\n'
        f'<w:document xmlns:w="{W_NS}" xmlns:mc="{MC_NS}" xmlns:w15="{W15_NS}" '
        'mc:Ignorable="w15"><w:body>'
        '<w:p><w:pPr><w:keepNext/></w:pPr><w:r><w:t>Unrelated paragraph.</w:t></w:r></w:p>'
        f"{targets}<w:sectPr/></w:body></w:document>"
    )


def _write_docx(
    path: Path, *, target_count: int = 1, target_text: str = REVIEW_SOURCE_ROLES_TEXT
) -> None:
    with ZipFile(path, "w", compression=ZIP_DEFLATED) as package:
        package.comment = b"layout-fixture"
        package.writestr(
            "word/document.xml",
            _document_xml(target_count=target_count, target_text=target_text),
        )
        package.writestr("word/media/keep.bin", b"preserve-this-payload")


def _paragraphs(path: Path) -> list[ElementTree.Element]:
    with ZipFile(path) as package:
        document = ElementTree.fromstring(package.read("word/document.xml"))
    body = document.find("w:body", NS)
    assert body is not None
    return body.findall("w:p", NS)


def _paragraph_text(paragraph: ElementTree.Element) -> str:
    return "".join(node.text or "" for node in paragraph.findall(".//w:t", NS))


def test_materializes_one_targeted_keep_lines_without_touching_other_content(
    tmp_path: Path,
) -> None:
    derived = tmp_path / "derived.docx"
    _write_docx(derived)
    with ZipFile(derived) as package:
        preserved_payload = package.read("word/media/keep.bin")
        preserved_comment = package.comment
        document_xml_before = package.read("word/document.xml")
    text_before = [_paragraph_text(paragraph) for paragraph in _paragraphs(derived)]

    result = materialize_review_keep_lines(derived)

    paragraphs = _paragraphs(derived)
    target = next(
        paragraph
        for paragraph in paragraphs
        if _paragraph_text(paragraph).startswith(REVIEW_SOURCE_ROLES_PREFIX)
    )
    unrelated = next(
        paragraph for paragraph in paragraphs if _paragraph_text(paragraph) == "Unrelated paragraph."
    )
    assert target.find("w:pPr/w:keepLines", NS) is not None
    assert unrelated.find("w:pPr/w:keepLines", NS) is None
    assert [_paragraph_text(paragraph) for paragraph in paragraphs] == text_before
    with ZipFile(derived) as package:
        assert package.read("word/media/keep.bin") == preserved_payload
        assert package.comment == preserved_comment
        document_xml_after = package.read("word/document.xml")
    assert document_xml_before.count(b"<w:keepLines/>") == 0
    assert document_xml_after.count(b"<w:keepLines/>") == 1
    assert document_xml_after.replace(b"<w:keepLines/>", b"", 1) == document_xml_before
    assert result.passed is True
    assert result.changed is True
    assert result.matched_paragraphs == 1
    assert result.keep_lines_count == 1


def test_materialization_is_byte_idempotent(tmp_path: Path) -> None:
    derived = tmp_path / "derived.docx"
    _write_docx(derived)
    first = materialize_review_keep_lines(derived)
    first_bytes = derived.read_bytes()
    first_hash = hashlib.sha256(first_bytes).hexdigest().upper()

    second = materialize_review_keep_lines(derived)

    assert derived.read_bytes() == first_bytes
    assert second.passed is True
    assert second.changed is False
    assert second.sha256_before == first_hash
    assert second.sha256_after == first_hash
    assert first.sha256_before != first.sha256_after


@pytest.mark.parametrize("target_count", [0, 2])
def test_materialization_fails_closed_unless_target_is_unique(
    tmp_path: Path,
    target_count: int,
) -> None:
    derived = tmp_path / "derived.docx"
    _write_docx(derived, target_count=target_count)
    before = derived.read_bytes()

    with pytest.raises(LayoutContractError, match="exactly one direct-body paragraph"):
        materialize_review_keep_lines(derived)

    assert derived.read_bytes() == before


def test_materialization_rejects_target_text_drift(tmp_path: Path) -> None:
    derived = tmp_path / "derived.docx"
    _write_docx(derived, target_text=REVIEW_SOURCE_ROLES_TEXT.replace("accurately", "inaccurately"))
    before = derived.read_bytes()

    with pytest.raises(LayoutContractError, match="target paragraph text SHA-256 drift"):
        materialize_review_keep_lines(derived)

    assert derived.read_bytes() == before


def test_cli_materializes_layout_and_emits_machine_readable_receipt(tmp_path: Path) -> None:
    derived = tmp_path / "derived.docx"
    _write_docx(derived)
    source_root = Path(__file__).resolve().parents[2] / "src"
    python_path = str(source_root)
    if os.environ.get("PYTHONPATH"):
        python_path = f"{python_path}{os.pathsep}{os.environ['PYTHONPATH']}"

    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "proposal_visuals.docx_layout",
            "--docx",
            str(derived),
        ],
        capture_output=True,
        text=True,
        check=False,
        env={**os.environ, "PYTHONPATH": python_path},
    )

    assert completed.returncode == 0, completed.stderr
    payload = json.loads(completed.stdout)
    assert payload["passed"] is True
    assert payload["changed"] is True
    assert payload["matched_paragraphs"] == 1
    assert payload["keep_lines_count"] == 1
    assert derived.name in payload["docx"]
