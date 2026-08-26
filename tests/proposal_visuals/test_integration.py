from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

import pytest

from proposal_visuals.integration import (
    FigureContractError,
    PackageContractError,
    QaGateError,
    SourceDriftError,
    build_integration_plan,
    freeze_source,
    inspect_source_docx,
)

WIDTHS_EMU = (
    4_716_000,
    4_716_000,
    4_716_000,
    4_716_000,
    4_716_000,
    4_716_000,
    4_716_000,
    4_104_000,
    4_716_000,
    4_716_000,
)
HEIGHTS_EMU = (
    3_108_664,
    2_694_911,
    3_677_487,
    2_540_969,
    3_259_853,
    2_920_229,
    3_639_375,
    1_610_091,
    2_963_971,
    2_920_229,
)
SOURCE_CAPTIONS = (
    "Figure 1. Four readings of the same observed model difference.",
    "Figure 2. The four-agent VEGO-AI baseline, redrawn from the supplied foundation manuscript [1].",
    "Figure 3. Established research streams, the opening none of them closes, and the mapping from gaps to questions.",
    "Figure 4. The programme spine: each sub-question to its artifact, its evaluation, and its planned output.",
    "Figure 5. The Study 1 review policy: eight declared signals, a matched attention budget, six routing actions.",
    "Figure 6. The Study 2 governed-judgment record, and its lifecycle as a state machine.",
    "Figure 7. The Study 3 reuse procedure: five gates, three outcomes, and the guard on a capability-gap claim.",
    "Figure 8. Expert-review scores reported in the VEGO-AI foundation manuscript.",
    "Figure 9. The three-year plan, anchored to October 2027 – October 2030.",
    "Figure 10. Where the ACL-2026 human–agent taxonomy meets this research, and where it stops.",
)
OUTPUT_DOCX_NAME = "VEGO_AI_Doctoral_Proposal_Visual_System_20260826.docx"
OUTPUT_PDF_NAME = "VEGO_AI_Doctoral_Proposal_Visual_System_20260826.pdf"


def _document_xml(
    *,
    captions: tuple[str, ...] = SOURCE_CAPTIONS,
    widths: tuple[int, ...] = WIDTHS_EMU,
    drawing_kind: str = "inline",
) -> str:
    paragraphs: list[str] = []
    for index in range(1, 11):
        kind = drawing_kind if index == 1 else "inline"
        paragraphs.append(
            f"""
            <w:p><w:r><w:drawing><wp:{kind}>
              <wp:extent cx="{widths[index - 1]}" cy="{HEIGHTS_EMU[index - 1]}"/>
              <wp:docPr id="{index + 10}" name="Figure {index + 10}" descr="Existing alt {index}"/>
              <a:graphic><a:graphicData><pic:pic>
                <pic:nvPicPr><pic:cNvPr id="{index}" name="image{index}.emf"/></pic:nvPicPr>
                <pic:blipFill><a:blip r:embed="rId{index}"/></pic:blipFill>
              </pic:pic></a:graphicData></a:graphic>
            </wp:{kind}></w:drawing></w:r></w:p>
            <w:p><w:r><w:t>{_xml_escape(captions[index - 1])}</w:t></w:r></w:p>
            """
        )
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" '
        'xmlns:wp="http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing" '
        'xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" '
        'xmlns:pic="http://schemas.openxmlformats.org/drawingml/2006/picture" '
        'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">'
        f"<w:body>{''.join(paragraphs)}<w:sectPr/></w:body></w:document>"
    )


def _xml_escape(value: str) -> str:
    return (
        value.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")
    )


def _relationships_xml(*, extension: str = "emf", duplicate_last: bool = False) -> str:
    relationships = []
    for index in range(1, 11):
        target_index = 9 if duplicate_last and index == 10 else index
        relationships.append(
            "<Relationship "
            f'Id="rId{index}" '
            'Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/image" '
            f'Target="media/image{target_index}.{extension}"/>'
        )
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        f"{''.join(relationships)}</Relationships>"
    )


def _write_source_docx(
    path: Path,
    *,
    captions: tuple[str, ...] = SOURCE_CAPTIONS,
    widths: tuple[int, ...] = WIDTHS_EMU,
    extension: str = "emf",
    drawing_kind: str = "inline",
    duplicate_last: bool = False,
) -> str:
    with ZipFile(path, "w", compression=ZIP_DEFLATED) as package:
        package.writestr(
            "word/document.xml",
            _document_xml(captions=captions, widths=widths, drawing_kind=drawing_kind),
        )
        package.writestr(
            "word/_rels/document.xml.rels",
            _relationships_xml(extension=extension, duplicate_last=duplicate_last),
        )
        for index in range(1, 11):
            package.writestr(f"word/media/image{index}.{extension}", f"vector-{index}".encode())
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def _write_figures(root: Path) -> list[Path]:
    root.mkdir(parents=True)
    figures = []
    for index in range(1, 11):
        figure = root / f"fig-{index:02d}.svg"
        figure.write_text('<svg xmlns="http://www.w3.org/2000/svg"/>', encoding="utf-8")
        figures.append(figure)
    return figures


def _write_content_manifest(path: Path) -> None:
    payload = {
        "figures": {
            f"fig-{index:02d}": {
                "caption": (
                    "Figure 1. Six readings of one observed model difference."
                    if index == 1
                    else SOURCE_CAPTIONS[index - 1]
                ),
                "alt_text": f"Claim-focused replacement alt {index}.",
            }
            for index in range(1, 11)
        }
    }
    path.write_text(json.dumps(payload), encoding="utf-8")


def _write_qa_receipt(
    path: Path,
    *,
    figures: list[Path],
    passed: bool = True,
    manual: str = "pass",
) -> None:
    payload = {
        "passed": passed,
        "checks": {"manual_visual_review": {"status": manual}},
        "figures": {f"fig-{index:02d}": {"status": "pass"} for index in range(1, 12)},
        "artifacts": {
            f"rendered/svg/{figure.name}": hashlib.sha256(figure.read_bytes()).hexdigest().upper()
            for figure in figures
        },
    }
    path.write_text(json.dumps(payload), encoding="utf-8")


@pytest.fixture
def integration_inputs(tmp_path: Path) -> dict[str, object]:
    source = tmp_path / "proposal.docx"
    source_sha256 = _write_source_docx(source)
    figures = _write_figures(tmp_path / "figures")
    manifest = tmp_path / "content.json"
    _write_content_manifest(manifest)
    qa_receipt = tmp_path / "qa-receipt.json"
    _write_qa_receipt(qa_receipt, figures=figures)
    return {
        "source": source,
        "source_sha256": source_sha256,
        "figures": figures,
        "manifest": manifest,
        "qa_receipt": qa_receipt,
        "output_root": tmp_path / "output",
    }


def _build(inputs: dict[str, object]):
    return build_integration_plan(
        inputs["source"],
        inputs["figures"],
        expected_source_sha256=inputs["source_sha256"],
        content_manifest=inputs["manifest"],
        qa_receipt=inputs["qa_receipt"],
        output_root=inputs["output_root"],
    )


def test_freeze_source_rejects_hash_drift(tmp_path: Path) -> None:
    source = tmp_path / "proposal.docx"
    source.write_bytes(b"changed")

    with pytest.raises(SourceDriftError, match="source SHA-256 drift"):
        freeze_source(source, expected_sha256="0" * 64)


def test_inspection_requires_ten_ordered_inline_vector_drawings(
    integration_inputs: dict[str, object],
) -> None:
    inspection = inspect_source_docx(integration_inputs["source"])

    assert [drawing.ordinal for drawing in inspection.drawings] == list(range(1, 11))
    assert [drawing.width_emu for drawing in inspection.drawings] == list(WIDTHS_EMU)
    assert [drawing.caption for drawing in inspection.drawings] == list(SOURCE_CAPTIONS)
    assert [drawing.media_target for drawing in inspection.drawings] == [
        f"word/media/image{index}.emf" for index in range(1, 11)
    ]
    assert inspection.alt_text_count == 10
    assert inspection.vector_media_count == 10


def test_integration_plan_maps_exactly_ten_figures_without_modifying_source(
    integration_inputs: dict[str, object],
) -> None:
    source = integration_inputs["source"]
    before = source.read_bytes()

    plan = _build(integration_inputs)

    assert source.read_bytes() == before
    assert [item.figure_id for item in plan.replacements] == [
        f"fig-{index:02d}" for index in range(1, 11)
    ]
    assert [item.width_emu for item in plan.replacements] == list(WIDTHS_EMU)
    assert [item.alt_text for item in plan.replacements] == [
        f"Claim-focused replacement alt {index}." for index in range(1, 11)
    ]
    assert [item.figure_sha256 for item in plan.replacements] == [
        hashlib.sha256(Path(path).read_bytes()).hexdigest().upper()
        for path in integration_inputs["figures"]
    ]
    assert plan.replacements[0].caption_before == SOURCE_CAPTIONS[0]
    assert (
        plan.replacements[0].caption_after
        == "Figure 1. Six readings of one observed model difference."
    )
    assert plan.replacements[1].caption_after == SOURCE_CAPTIONS[1]
    assert plan.output_docx == Path(integration_inputs["output_root"]) / "docx" / OUTPUT_DOCX_NAME
    assert plan.output_pdf == Path(integration_inputs["output_root"]) / "pdf" / OUTPUT_PDF_NAME


def test_nonpassing_or_incomplete_qa_receipt_blocks_before_integration(
    integration_inputs: dict[str, object],
) -> None:
    _write_qa_receipt(
        integration_inputs["qa_receipt"],
        figures=integration_inputs["figures"],
        passed=False,
    )
    with pytest.raises(QaGateError, match="overall QA receipt is not passing"):
        _build(integration_inputs)

    _write_qa_receipt(
        integration_inputs["qa_receipt"],
        figures=integration_inputs["figures"],
        passed=True,
        manual="fail",
    )
    with pytest.raises(QaGateError, match="manual visual review is not passing"):
        _build(integration_inputs)


def test_qa_receipt_must_be_bound_to_the_exact_replacement_svgs(
    integration_inputs: dict[str, object],
) -> None:
    first = integration_inputs["figures"][0]
    first.write_text(
        '<svg xmlns="http://www.w3.org/2000/svg"><text>drift</text></svg>', encoding="utf-8"
    )

    with pytest.raises(QaGateError, match="artifact hash mismatch for fig-01.svg"):
        _build(integration_inputs)


def test_unordered_or_missing_replacement_svg_blocks_integration(
    integration_inputs: dict[str, object],
) -> None:
    integration_inputs["figures"] = list(reversed(integration_inputs["figures"]))
    with pytest.raises(FigureContractError, match="ordered fig-01.svg through fig-10.svg"):
        _build(integration_inputs)

    integration_inputs["figures"] = list(reversed(integration_inputs["figures"]))[:-1]
    with pytest.raises(FigureContractError, match="exactly 10 replacement SVGs"):
        _build(integration_inputs)


@pytest.mark.parametrize(
    ("mutation", "message"),
    [
        ("wrong-width", "unexpected inline width"),
        ("duplicate-caption", "captions must be Figure 1 through Figure 10"),
        ("anchor", "exactly 10 inline drawings"),
        ("raster", "vector image relationships"),
        ("duplicate-media", "unique vector media target"),
    ],
)
def test_docx_contract_drift_blocks_before_word(
    tmp_path: Path,
    mutation: str,
    message: str,
) -> None:
    source = tmp_path / "proposal.docx"
    captions = SOURCE_CAPTIONS
    widths = WIDTHS_EMU
    extension = "emf"
    drawing_kind = "inline"
    duplicate_last = False
    if mutation == "wrong-width":
        widths = (4_000_000, *WIDTHS_EMU[1:])
    elif mutation == "duplicate-caption":
        captions = (SOURCE_CAPTIONS[0], SOURCE_CAPTIONS[0], *SOURCE_CAPTIONS[2:])
    elif mutation == "anchor":
        drawing_kind = "anchor"
    elif mutation == "raster":
        extension = "png"
    elif mutation == "duplicate-media":
        duplicate_last = True
    _write_source_docx(
        source,
        captions=captions,
        widths=widths,
        extension=extension,
        drawing_kind=drawing_kind,
        duplicate_last=duplicate_last,
    )

    with pytest.raises(PackageContractError, match=message):
        inspect_source_docx(source)


def test_plan_only_powershell_path_preserves_unicode_without_creating_outputs(
    integration_inputs: dict[str, object],
) -> None:
    pwsh = shutil.which("pwsh")
    if pwsh is None:
        pytest.skip("PowerShell 7 is unavailable")
    script = Path(__file__).resolve().parents[2] / "scripts" / "integrate_proposal_visuals.ps1"
    command = [
        pwsh,
        "-NoProfile",
        "-NonInteractive",
        "-File",
        str(script),
        "-SourceDocx",
        str(integration_inputs["source"]),
        "-OutputRoot",
        str(integration_inputs["output_root"]),
        "-FigureRoot",
        str(Path(integration_inputs["figures"][0]).parent),
        "-ContentManifest",
        str(integration_inputs["manifest"]),
        "-QaReceipt",
        str(integration_inputs["qa_receipt"]),
        "-ExpectedSourceSha256",
        str(integration_inputs["source_sha256"]),
        "-PythonExecutable",
        sys.executable,
        "-PlanOnly",
    ]

    completed = subprocess.run(command, capture_output=True, text=True, check=False)

    assert completed.returncode == 0, completed.stderr
    payload = json.loads(completed.stdout)
    assert [item["figure_id"] for item in payload["replacements"]] == [
        f"fig-{index:02d}" for index in range(1, 11)
    ]
    assert payload["replacements"][8]["caption_before"] == SOURCE_CAPTIONS[8]
    assert payload["replacements"][8]["caption_after"] == SOURCE_CAPTIONS[8]
    assert payload["replacements"][9]["caption_before"] == SOURCE_CAPTIONS[9]
    assert payload["replacements"][9]["caption_after"] == SOURCE_CAPTIONS[9]
    assert not Path(payload["output_docx"]).exists()
    assert not Path(payload["output_pdf"]).exists()


def test_powershell_production_path_rejects_noncanonical_renderer_manifest(
    integration_inputs: dict[str, object],
    tmp_path: Path,
) -> None:
    pwsh = shutil.which("pwsh")
    if pwsh is None:
        pytest.skip("PowerShell 7 is unavailable")
    script = Path(__file__).resolve().parents[2] / "scripts" / "integrate_proposal_visuals.ps1"
    custom_manifest = tmp_path / "renderer-manifest.json"
    custom_manifest.write_text("{}", encoding="utf-8")
    command = [
        pwsh,
        "-NoProfile",
        "-NonInteractive",
        "-File",
        str(script),
        "-SourceDocx",
        str(integration_inputs["source"]),
        "-OutputRoot",
        str(integration_inputs["output_root"]),
        "-FigureRoot",
        str(Path(integration_inputs["figures"][0]).parent),
        "-ContentManifest",
        str(integration_inputs["manifest"]),
        "-QaReceipt",
        str(integration_inputs["qa_receipt"]),
        "-ExpectedSourceSha256",
        str(integration_inputs["source_sha256"]),
        "-PythonExecutable",
        sys.executable,
        "-RendererManifest",
        str(custom_manifest),
        "-PlanOnly",
    ]

    completed = subprocess.run(command, capture_output=True, text=True, check=False)

    assert completed.returncode != 0
    assert "canonical renderer manifest" in completed.stderr
    assert not (Path(integration_inputs["output_root"]) / "docx" / OUTPUT_DOCX_NAME).exists()


def test_powershell_path_refuses_to_overwrite_a_derived_output_before_word(
    integration_inputs: dict[str, object],
) -> None:
    pwsh = shutil.which("pwsh")
    if pwsh is None:
        pytest.skip("PowerShell 7 is unavailable")
    script = Path(__file__).resolve().parents[2] / "scripts" / "integrate_proposal_visuals.ps1"
    existing = Path(integration_inputs["output_root"]) / "docx" / OUTPUT_DOCX_NAME
    existing.parent.mkdir(parents=True)
    existing.write_bytes(b"do-not-overwrite")
    command = [
        pwsh,
        "-NoProfile",
        "-NonInteractive",
        "-File",
        str(script),
        "-SourceDocx",
        str(integration_inputs["source"]),
        "-OutputRoot",
        str(integration_inputs["output_root"]),
        "-FigureRoot",
        str(Path(integration_inputs["figures"][0]).parent),
        "-ContentManifest",
        str(integration_inputs["manifest"]),
        "-QaReceipt",
        str(integration_inputs["qa_receipt"]),
        "-ExpectedSourceSha256",
        str(integration_inputs["source_sha256"]),
        "-PythonExecutable",
        sys.executable,
    ]

    completed = subprocess.run(command, capture_output=True, text=True, check=False)

    assert completed.returncode != 0
    assert "Derived output already exists" in completed.stderr
    assert existing.read_bytes() == b"do-not-overwrite"
    assert not (Path(integration_inputs["output_root"]) / "pdf" / OUTPUT_PDF_NAME).exists()
