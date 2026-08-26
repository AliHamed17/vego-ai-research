"""Deterministic production and evidence checks for proposal vector figures."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import platform
import re
import shutil
import subprocess
import xml.etree.ElementTree as ET
from collections.abc import Iterable, Mapping
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

import PIL
import pypdf
import reportlab
from PIL import Image, ImageDraw
from pypdf import PdfReader, PdfWriter, Transformation
from pypdf.generic import ContentStream, IndirectObject

from proposal_visuals.content import SourceProvenance, load_source_provenance, load_verified_content
from proposal_visuals.document_integrity import (
    DocumentIntegrityError,
    verify_planned_svg_semantics,
)
from proposal_visuals.fonts import verify_vendored_fonts
from proposal_visuals.model import Element, Group, Scene, Text
from proposal_visuals.pdf_backend import render_pdf
from proposal_visuals.svg_backend import render_svg
from proposal_visuals.tokens import DEFAULT_TOKENS, Color, VisualTokens, contrast_ratio

PROJECT_ROOT = Path(__file__).resolve().parents[2]
FIGURES_ROOT = PROJECT_ROOT / "docs" / "research" / "phd-proposal" / "figures"
CONTENT_PATH = FIGURES_ROOT / "content.json"
PROVENANCE_PATH = FIGURES_ROOT / "source-provenance.json"
SOURCE_DIRECTORY = FIGURES_ROOT / "sources"
A4_WIDTH_PT = 595.276
A4_HEIGHT_PT = 841.89
PROOF_MARGIN_PT = 36.0
EMU_PER_POINT = 12_700
DOCX_INLINE_WIDTH_EMU = 4_716_000
FIGURE_08_INLINE_WIDTH_EMU = 4_104_000
STANDALONE_FIGURE_11_WIDTH_PT = 523.0
DECLARED_WIDTH_EMU = {
    **{f"fig-{number:02d}": DOCX_INLINE_WIDTH_EMU for number in range(1, 8)},
    "fig-08": FIGURE_08_INLINE_WIDTH_EMU,
    "fig-09": DOCX_INLINE_WIDTH_EMU,
    "fig-10": DOCX_INLINE_WIDTH_EMU,
    "fig-11": round(STANDALONE_FIGURE_11_WIDTH_PT * EMU_PER_POINT),
}
COLOR_MODES = ("normal", "greyscale", "protanopia", "deuteranopia")
PROOF_DPI = (144, 576)
REVIEW_COLUMNS = (
    "A4 144 DPI clipping/crossing",
    "400% 576 DPI clipping/crossing",
    "Font-size",
    "Ambiguity",
    "Consistency",
    "Greyscale",
    "Protanopia",
    "Deuteranopia",
)
REVIEW_FIGURE_IDS = tuple(f"fig-{number:02d}" for number in range(1, 12))
ORDINARY_TEXT_EXCEPTION_ROLES = frozenset({"provenance", "supporting-note", "boundary-note"})
_SVG_URL_REFERENCE = re.compile(r"url\(\s*(['\"]?)(.*?)\1\s*\)", re.IGNORECASE)
_SVG_NAMESPACE = "http://www.w3.org/2000/svg"
_SVG_MAX_ELEMENTS = 500
_SVG_MAX_ATTRIBUTES = 2_500
_SVG_MAX_DEPTH = 10
_REVIEW_STATUS_MARKER = re.compile(r"<!--\s*visual-review-status:\s*([^>]+?)\s*-->")
_PDF_EXTERNAL_ACTION_TYPES = frozenset(
    {
        "/GoToE",
        "/GoToR",
        "/ImportData",
        "/JavaScript",
        "/Launch",
        "/SubmitForm",
        "/URI",
    }
)
COLOR_MATRICES: Mapping[str, tuple[float, ...]] = {
    "protanopia": (
        0.152286,
        1.052583,
        -0.204868,
        0.0,
        0.114503,
        0.786281,
        0.099216,
        0.0,
        -0.003882,
        -0.048116,
        1.051998,
        0.0,
    ),
    "deuteranopia": (
        0.367322,
        0.860646,
        -0.227968,
        0.0,
        0.280085,
        0.672501,
        0.047413,
        0.0,
        -0.011820,
        0.042940,
        0.968881,
        0.0,
    ),
}


@dataclass(frozen=True)
class SourceReceipt:
    """Public provenance fields only; never serialises a local source path."""

    filename: str
    sha256: str
    page_count: int


@dataclass(frozen=True)
class FigureArtifact:
    """One deterministic SVG/PDF pair and its scene for QA."""

    figure_id: str
    svg: Path
    pdf: Path
    svg_sha256: str
    pdf_sha256: str
    scene: Scene = field(repr=False, compare=False)


@dataclass(frozen=True)
class BuildReceipt:
    """A path-safe record of every vector output."""

    output_root: Path = field(repr=False, compare=False)
    source: SourceReceipt
    build_inputs: Mapping[str, Mapping[str, object]]
    figures: tuple[FigureArtifact, ...]

    def _relative(self, path: Path) -> str:
        return path.resolve().relative_to(self.output_root.resolve()).as_posix()

    def to_dict(self) -> dict[str, object]:
        return {
            "build_inputs": {key: self.build_inputs[key] for key in sorted(self.build_inputs)},
            "source": asdict(self.source),
            "figures": [
                {
                    "id": item.figure_id,
                    "svg": self._relative(item.svg),
                    "svg_sha256": item.svg_sha256,
                    "pdf": self._relative(item.pdf),
                    "pdf_sha256": item.pdf_sha256,
                }
                for item in self.figures
            ],
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2, sort_keys=True) + "\n"


@dataclass(frozen=True)
class BuildConfig:
    """Explicit paths keep the build reproducible without exposing them in receipts."""

    output_root: Path = FIGURES_ROOT
    source_pdf_path: Path | None = None
    figure_ids: tuple[str, ...] = tuple(f"fig-{number:02d}" for number in range(1, 12))
    clean: bool = False


@dataclass(frozen=True)
class QaReceipt:
    """Machine-readable QA result, including blocked or unavailable checks."""

    passed: bool
    source: SourceReceipt
    checks: Mapping[str, Mapping[str, object]]
    figures: Mapping[str, Mapping[str, object]]
    artifacts: Mapping[str, str]

    def to_dict(self) -> dict[str, object]:
        return {
            "artifacts": dict(sorted(self.artifacts.items())),
            "checks": {key: self.checks[key] for key in sorted(self.checks)},
            "figures": {key: self.figures[key] for key in sorted(self.figures)},
            "passed": self.passed,
            "source": asdict(self.source),
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2, sort_keys=True) + "\n"


def default_tokens() -> VisualTokens:
    """Expose the frozen palette through a small, testable public API."""
    return DEFAULT_TOKENS


def all_text_fill_contrasts(tokens: VisualTokens) -> dict[str, float]:
    """Return every approved text-on-fill pairing used by the visual language."""
    colors = tokens.colors
    pairs = {
        "ink/background": ("ink", "background"),
        "ink/neutral_fill": ("ink", "neutral_fill"),
        "existing/background": ("existing", "background"),
        "human_judgment/background": ("human_judgment", "background"),
        "conditional/background": ("conditional", "background"),
    }
    return {
        name: contrast_ratio(colors[foreground], colors[background])
        for name, (foreground, background) in pairs.items()
    }


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def _builder_path(figure_id: str) -> Path:
    filename = figure_id.replace("-", "_")
    candidates = sorted(SOURCE_DIRECTORY.glob(f"{filename}_*.py"))
    if len(candidates) != 1:
        raise ValueError(f"expected one builder for {figure_id}")
    return candidates[0]


def _load_builder(figure_id: str):  # type: ignore[no-untyped-def]
    filename = figure_id.replace("-", "_")
    path = _builder_path(figure_id)
    spec = importlib.util.spec_from_file_location(f"proposal_visuals_{filename}", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load builder for {figure_id}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    builder = getattr(module, "build", None)
    if not callable(builder):
        raise TypeError(f"builder for {figure_id} must expose build")
    return builder


def _path_safe_file_receipt(path: Path) -> dict[str, object]:
    relative = path.resolve().relative_to(PROJECT_ROOT.resolve()).as_posix()
    return {"path": relative, "bytes": path.stat().st_size, "sha256": _sha256(path)}


def _build_input_receipts() -> dict[str, Mapping[str, object]]:
    module_directory = PROJECT_ROOT / "src" / "proposal_visuals"
    paths = {
        "content_manifest": CONTENT_PATH,
        "font_manifest": FIGURES_ROOT / "vendor" / "fonts" / "manifest.json",
        "project:pyproject": PROJECT_ROOT / "pyproject.toml",
        "project:uv_lock": PROJECT_ROOT / "uv.lock",
        "script:build_proposal_visuals": PROJECT_ROOT / "scripts" / "build_proposal_visuals.py",
        "module:content": module_directory / "content.py",
        "module:fonts": module_directory / "fonts.py",
        "module:model": module_directory / "model.py",
        "module:pdf_backend": module_directory / "pdf_backend.py",
        "module:qa": module_directory / "qa.py",
        "module:svg_backend": module_directory / "svg_backend.py",
        "module:tokens": module_directory / "tokens.py",
        "source_provenance": PROVENANCE_PATH,
        **{f"figure_module:{figure_id}": _builder_path(figure_id) for figure_id in REVIEW_FIGURE_IDS},
    }
    return {key: _path_safe_file_receipt(path) for key, path in sorted(paths.items())}


def _resolved_child(figures_root: Path, candidate: Path) -> Path:
    root = figures_root.resolve()
    target = candidate.resolve()
    try:
        relative = target.relative_to(root)
    except ValueError as error:
        raise ValueError("safe generated child must remain under figures root") from error
    if relative.parts not in {("rendered",), ("qa", "generated")}:
        raise ValueError("safe generated child must be rendered or qa/generated")
    return target


def safe_clean_generated(figures_root: Path, generated_child: Path) -> None:
    """Remove only a named generated child after containment checks."""
    target = _resolved_child(figures_root, generated_child)
    if target.exists():
        if not target.is_dir():
            raise ValueError("safe generated child must be a directory")
        shutil.rmtree(target)


def _resolved_source_path(config: BuildConfig, provenance: SourceProvenance) -> Path:
    if config.source_pdf_path is not None:
        return config.source_pdf_path
    return Path.home() / "Downloads" / provenance.filename


def build_all(config: BuildConfig) -> BuildReceipt:
    """Verify the approved proposal PDF, then build an ordered SVG/PDF pair set."""
    output_root = config.output_root.resolve()
    provenance = load_source_provenance(PROVENANCE_PATH)
    source_pdf = _resolved_source_path(config, provenance)
    content = load_verified_content(CONTENT_PATH, PROVENANCE_PATH, source_pdf)
    expected_ids = tuple(f"fig-{number:02d}" for number in range(1, 12))
    if not config.figure_ids or any(figure_id not in expected_ids for figure_id in config.figure_ids):
        raise ValueError("figure IDs must be fig-01 through fig-11")
    if len(set(config.figure_ids)) != len(config.figure_ids):
        raise ValueError("figure IDs must be unique")
    if config.clean:
        safe_clean_generated(output_root, output_root / "rendered")
        safe_clean_generated(output_root, output_root / "qa" / "generated")

    artifacts: list[FigureArtifact] = []
    for figure_id in config.figure_ids:
        scene = _load_builder(figure_id)(content.figures[figure_id], DEFAULT_TOKENS)
        svg = output_root / "rendered" / "svg" / f"{figure_id}.svg"
        pdf = output_root / "rendered" / "pdf" / f"{figure_id}.pdf"
        render_svg(scene, svg)
        render_pdf(scene, pdf)
        artifacts.append(
            FigureArtifact(
                figure_id=figure_id,
                svg=svg,
                pdf=pdf,
                svg_sha256=_sha256(svg),
                pdf_sha256=_sha256(pdf),
                scene=scene,
            )
        )
    return BuildReceipt(
        output_root=output_root,
        source=SourceReceipt(provenance.filename, provenance.sha256, provenance.page_count),
        build_inputs=_build_input_receipts(),
        figures=tuple(artifacts),
    )


def _walk_elements(elements: Iterable[Element]) -> Iterable[Element]:
    for element in elements:
        yield element
        if isinstance(element, Group):
            yield from _walk_elements(element.elements)


def _scene_text_contrasts(scene: Scene) -> dict[str, float]:
    ratios: dict[str, float] = {}
    for index, element in enumerate(_walk_elements(scene.elements), start=1):
        if isinstance(element, Text):
            ratios[f"text-{index}"] = contrast_ratio(Color(element.fill), Color(element.background))
    return ratios


def _minimum_font_size(scene: Scene) -> float:
    sizes = _font_sizes(scene)
    if not sizes:
        raise ValueError("scene has no text to check")
    return min(sizes)


def _font_sizes(scene: Scene) -> list[float]:
    return [element.font_size for element in _walk_elements(scene.elements) if isinstance(element, Text)]


def _ordinary_font_sizes(scene: Scene) -> list[float]:
    """P2 ordinary labels exclude only documented, non-default support-note roles."""
    return [
        element.font_size
        for element in _walk_elements(scene.elements)
        if isinstance(element, Text) and element.semantic_role not in ORDINARY_TEXT_EXCEPTION_ROLES
    ]


def _ordinary_minimum_font_size(scene: Scene) -> float:
    sizes = _ordinary_font_sizes(scene)
    if not sizes:
        raise ValueError("scene has no ordinary text for the 8 pt target")
    return min(sizes)


def _semantic_redundancy(scene: Scene) -> dict[str, object]:
    elements = tuple(_walk_elements(scene.elements))
    semantic_roles = sorted({element.semantic_role for element in elements if element.semantic_role})
    dash_styles = sorted(
        {element.dash for element in elements if hasattr(element, "dash") and not isinstance(element, Text)}
    )
    hatches = sorted(
        {
            element.hatch
            for element in elements
            if hasattr(element, "hatch") and element.hatch is not None
        }
    )
    shapes = sorted(
        {
            type(element).__name__
            for element in elements
            if not isinstance(element, (Group, Text))
        }
    )
    metadata_groups = sum(1 for element in elements if isinstance(element, Group) and element.metadata)
    passed = len(semantic_roles) >= 2 and (
        len(shapes) >= 2 or len(dash_styles) >= 2 or bool(hatches)
    )
    return {
        "passed": passed,
        "semantic_roles": semantic_roles,
        "dash_styles": dash_styles,
        "hatches": hatches,
        "shape_types": shapes,
        "metadata_groups": metadata_groups,
    }


def _svg_vector_check(path: Path) -> dict[str, object]:
    data = path.read_bytes()
    try:
        text = data.decode("utf-8", errors="strict")
    except UnicodeDecodeError:
        text = ""
    root: ET.Element | None = None
    try:
        root = ET.fromstring(text)
        parseable = root.tag == f"{{{_SVG_NAMESPACE}}}svg"
    except ET.ParseError:
        parseable = False
    try:
        semantic_sha256 = verify_planned_svg_semantics(data)
        strict_semantics = True
        strict_semantics_error: str | None = None
    except DocumentIntegrityError as error:
        semantic_sha256 = None
        strict_semantics = False
        strict_semantics_error = str(error)
    lower = text.lower()
    element_count, attribute_count, max_depth = _svg_structure_metrics(root)
    structure_within_limits = (
        element_count <= _SVG_MAX_ELEMENTS
        and attribute_count <= _SVG_MAX_ATTRIBUTES
        and max_depth <= _SVG_MAX_DEPTH
    )
    element_names = (
        {element.tag.rsplit("}", 1)[-1] for element in root.iter()}
        if root is not None
        else set()
    )
    resource_violations = _svg_resource_violations(root) if parseable else ("unparseable",)
    embedded_font = "data:font/ttf;base64," in lower
    no_patterns = "pattern" not in element_names
    no_raster_images = "image" not in element_names
    return {
        "passed": (
            parseable
            and strict_semantics
            and structure_within_limits
            and no_patterns
            and no_raster_images
            and embedded_font
            and not resource_violations
        ),
        "parseable": parseable,
        "strict_semantics": strict_semantics,
        "strict_semantics_error": strict_semantics_error,
        "semantic_sha256": semantic_sha256,
        "structure_within_limits": structure_within_limits,
        "element_count": element_count,
        "attribute_count": attribute_count,
        "max_depth": max_depth,
        "no_patterns": no_patterns,
        "no_raster_images": no_raster_images,
        "no_external_references": strict_semantics and not resource_violations,
        "embedded_font": embedded_font,
        "resource_violations": list(resource_violations),
    }


def _svg_structure_metrics(root: ET.Element | None) -> tuple[int, int, int]:
    if root is None:
        return 0, 0, 0
    element_count = 0
    attribute_count = 0
    max_depth = 0
    stack = [(root, 1)]
    while stack:
        element, depth = stack.pop()
        element_count += 1
        attribute_count += len(element.attrib)
        max_depth = max(max_depth, depth)
        stack.extend((child, depth + 1) for child in element)
    return element_count, attribute_count, max_depth


def _svg_resource_violations(root: ET.Element) -> tuple[str, ...]:
    """Allow only embedded TTF data inside the pinned font style."""
    violations: list[str] = []
    for element in root.iter():
        for name, value in element.attrib.items():
            local_name = name.rsplit("}", 1)[-1]
            if local_name == "href":
                violations.append(f"{local_name}:{value}")
            if _SVG_URL_REFERENCE.search(value):
                violations.append(f"paint-server:{value}")
        if element.tag.rsplit("}", 1)[-1] == "style" and element.text:
            violations.extend(_svg_url_violations(element.text))
    return tuple(sorted(set(violations)))


def _svg_url_violations(value: str) -> list[str]:
    return [
        f"url:{reference.strip()}"
        for _, reference in _SVG_URL_REFERENCE.findall(value)
        if not _allowed_svg_resource(reference)
    ]


def _allowed_svg_resource(value: str) -> bool:
    reference = value.strip().lower()
    return reference.startswith("data:font/ttf;base64,")


def _as_object(value: Any) -> Any:
    return value.get_object() if hasattr(value, "get_object") else value


def _pdf_external_actions(reader: PdfReader) -> tuple[str, ...]:
    """Return external/active PDF action types found in the parsed object graph.

    Stream payload bytes are deliberately not inspected: compressed font or content
    data can contain strings such as ``/URI`` by chance without defining a PDF action.
    """
    actions: set[str] = set()
    seen_references: set[tuple[int, int, int]] = set()
    seen_containers: set[int] = set()

    def visit(value: Any) -> None:
        if isinstance(value, IndirectObject):
            reference = (id(value.pdf), value.idnum, value.generation)
            if reference in seen_references:
                return
            seen_references.add(reference)
            visit(value.get_object())
            return

        if isinstance(value, Mapping):
            object_id = id(value)
            if object_id in seen_containers:
                return
            seen_containers.add(object_id)
            action_type = str(_as_object(value.get("/S", "")))
            if action_type in _PDF_EXTERNAL_ACTION_TYPES:
                actions.add(action_type)
            for child in value.values():
                visit(child)
            return

        if isinstance(value, (list, tuple)):
            object_id = id(value)
            if object_id in seen_containers:
                return
            seen_containers.add(object_id)
            for child in value:
                visit(child)

    visit(reader.trailer)
    return tuple(sorted(actions))


def _pdf_vector_check(path: Path) -> dict[str, object]:
    reader = PdfReader(path)
    image_count = 0
    font_names: set[str] = set()
    used_fonts: set[str] = set()
    unembedded_used_fonts: set[str] = set()
    for page in reader.pages:
        resources = _as_object(page.get("/Resources", {}))
        fonts = _as_object(resources.get("/Font", {})) if resources else {}
        font_by_resource = {
            str(resource_name): _as_object(font)
            for resource_name, font in (fonts.items() if hasattr(fonts, "items") else ())
        }
        for resolved in font_by_resource.values():
            font_names.add(str(resolved.get("/BaseFont", "")))
        for resource_name in _used_font_resource_names(page, reader):
            resolved = font_by_resource.get(resource_name)
            if resolved is None:
                unembedded_used_fonts.add(f"missing-resource:{resource_name}")
                continue
            base_font = str(resolved.get("/BaseFont", ""))
            used_fonts.add(base_font)
            if not _embedded_font_descriptor(resolved):
                unembedded_used_fonts.add(base_font)
        xobjects = _as_object(resources.get("/XObject", {})) if resources else {}
        for xobject in xobjects.values() if hasattr(xobjects, "values") else ():
            if str(_as_object(xobject).get("/Subtype", "")) == "/Image":
                image_count += 1
    external_actions = _pdf_external_actions(reader)
    return {
        "passed": (
            len(reader.pages) == 1
            and image_count == 0
            and not external_actions
            and bool(used_fonts)
            and not unembedded_used_fonts
        ),
        "page_count": len(reader.pages),
        "image_xobjects": image_count,
        "font_names": sorted(font_names),
        "used_fonts": sorted(used_fonts),
        "unembedded_used_fonts": sorted(unembedded_used_fonts),
        "external_actions": list(external_actions),
        "no_external_references": not external_actions,
    }


def _used_font_resource_names(page: Any, reader: PdfReader) -> set[str]:
    """Return only Tf-selected fonts that reach a text-showing operator."""
    active_font: str | None = None
    used: set[str] = set()
    stream = ContentStream(page.get_contents(), reader)
    for operands, operator in stream.operations:
        if operator == b"Tf":
            active_font = str(operands[0])
        elif operator in {b"Tj", b"TJ", b"'", b'"'} and active_font is not None:
            used.add(active_font)
    return used


def _embedded_font_descriptor(font: Any) -> bool:
    descriptor = _as_object(font.get("/FontDescriptor")) if font.get("/FontDescriptor") else None
    if descriptor is None:
        descendants = font.get("/DescendantFonts")
        if descendants:
            descendant = _as_object(descendants[0])
            descriptor = (
                _as_object(descendant.get("/FontDescriptor"))
                if descendant.get("/FontDescriptor")
                else None
            )
    return bool(descriptor and any(descriptor.get(key) for key in ("/FontFile", "/FontFile2", "/FontFile3")))


def _write_a4_proof(artifact: FigureArtifact, target: Path) -> dict[str, float | int | str]:
    """Place one native vector page on an A4 proof page without rasterising it."""
    target.parent.mkdir(parents=True, exist_ok=True)
    reader = PdfReader(artifact.pdf)
    page = reader.pages[0]
    width = float(page.mediabox.width)
    height = float(page.mediabox.height)
    declared_width_emu = DECLARED_WIDTH_EMU[artifact.figure_id]
    declared_width_pt = declared_width_emu / EMU_PER_POINT
    if declared_width_pt > A4_WIDTH_PT - 2 * PROOF_MARGIN_PT:
        raise ValueError("declared proof width exceeds portrait A4 content width")
    scale = declared_width_pt / width
    rendered_width, rendered_height = width * scale, height * scale
    if rendered_height > A4_HEIGHT_PT - 2 * PROOF_MARGIN_PT:
        raise ValueError("declared proof height exceeds portrait A4 content height")
    x = (A4_WIDTH_PT - rendered_width) / 2
    y = (A4_HEIGHT_PT - rendered_height) / 2
    writer = PdfWriter()
    proof = writer.add_blank_page(A4_WIDTH_PT, A4_HEIGHT_PT)
    proof.merge_transformed_page(page, Transformation().scale(scale).translate(x, y))
    writer.add_metadata(
        {
            "/Title": f"{artifact.figure_id} A4 visual proof",
            "/Author": "VEGO-AI proposal visual system",
            "/Creator": "VEGO-AI deterministic visual QA",
            "/Producer": "pypdf deterministic proof assembly",
        }
    )
    with target.open("wb") as stream:
        writer.write(stream)
    return {
        "scale": scale,
        "final_width_pt": rendered_width,
        "final_height_pt": rendered_height,
        "orientation": "portrait",
        "declared_width_emu": declared_width_emu,
        "declared_width_source": (
            "standalone A4 proof width" if artifact.figure_id == "fig-11" else "DOCX inline width"
        ),
    }


def _poppler_executable() -> Path | None:
    package_root = Path.home() / "AppData" / "Local" / "Microsoft" / "WinGet" / "Packages"
    candidates = sorted(
        package_root.glob("oschwartz10612.Poppler_*/*/Library/bin/pdftoppm.exe"),
        key=lambda item: item.as_posix(),
    )
    return candidates[-1] if candidates else None


def _poppler_version(executable: Path) -> str:
    result = subprocess.run([str(executable), "-v"], capture_output=True, text=True, check=False)
    return (result.stderr or result.stdout).strip()


def _render_pdf_png(executable: Path, pdf: Path, target: Path, dpi: int) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    result = subprocess.run(
        [str(executable), "-png", "-singlefile", "-r", str(dpi), str(pdf), str(target)],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0 or not target.with_suffix(".png").exists():
        raise RuntimeError(f"Poppler rendering failed for {pdf.name}: {result.stderr.strip()}")


def _transform_png(source: Path, target: Path, mode: str) -> None:
    with Image.open(source) as original:
        image = original.convert("RGB")
        if mode == "greyscale":
            transformed = image.convert("L").convert("RGB")
        elif mode in COLOR_MATRICES:
            transformed = image.convert("RGB", COLOR_MATRICES[mode])
        else:
            raise ValueError(f"unknown colour mode: {mode}")
        target.parent.mkdir(parents=True, exist_ok=True)
        transformed.save(target, format="PNG", optimize=False)


def _create_contact_sheet(image_paths: list[tuple[str, Path]], target: Path) -> None:
    thumb_width = 300
    margin = 12
    title_height = 20
    rows, columns = 3, 4
    thumbs: list[tuple[str, Image.Image]] = []
    for figure_id, path in image_paths:
        with Image.open(path) as opened:
            copy = opened.convert("RGB")
            copy.thumbnail((thumb_width, 260))
            thumbs.append((figure_id, copy.copy()))
    sheet = Image.new(
        "RGB",
        (columns * (thumb_width + margin) + margin, rows * (260 + title_height + margin) + margin),
        "white",
    )
    draw = ImageDraw.Draw(sheet)
    for index, (figure_id, image) in enumerate(thumbs):
        column, row = index % columns, index // columns
        x = margin + column * (thumb_width + margin)
        y = margin + row * (260 + title_height + margin)
        sheet.paste(image, (x + (thumb_width - image.width) // 2, y + title_height))
        draw.text((x, y), figure_id, fill="#172033")
    target.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(target, format="PNG", optimize=False)


def _review_template() -> str:
    rows = "\n".join(
        f"| fig-{number:02d} | PENDING | PENDING | PENDING | PENDING | PENDING | PENDING | PENDING | PENDING |"
        for number in range(1, 12)
    )
    return (
        "# Visual review\n\n"
        "<!-- visual-review-status: PENDING -->\n\n"
        "This human review gate is intentionally separate from automated rasterisation. "
        "Set every cell to PASS only after opening the named proof/contact evidence; record a failure "
        "with its observed issue instead.\n\n"
        f"| Figure | {' | '.join(REVIEW_COLUMNS)} |\n"
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- |\n"
        f"{rows}\n\n"
        "Evidence: `qa/generated/proofs/{144,576}/{normal,greyscale,protanopia,deuteranopia}/` "
        "and `qa/generated/contact-sheets/`.\n"
    )


def _manual_visual_review(figures_root: Path) -> dict[str, object]:
    review = figures_root / "qa" / "visual-review.md"
    if not review.exists():
        review.parent.mkdir(parents=True, exist_ok=True)
        review.write_text(_review_template(), encoding="utf-8", newline="\n")
    content = review.read_text(encoding="utf-8")
    errors = _manual_review_errors(content)
    return {
        "status": "pass" if not errors else "fail",
        "detail": "human review recorded" if not errors else "; ".join(errors),
    }


def _vendored_font_receipt() -> dict[str, object]:
    try:
        verified = verify_vendored_fonts()
    except RuntimeError as error:
        return {"status": "fail", "detail": str(error), "verified": False}
    return {
        "status": "pass",
        "family": "Carlito",
        "verified": True,
        "verified_files": {name: dict(record) for name, record in sorted(verified.items())},
        "license_file": "OFL.txt",
        "license_receipt": dict(verified["OFL.txt"]),
    }


def _runtime_versions() -> dict[str, object]:
    uv_result = subprocess.run(["uv", "--version"], capture_output=True, text=True, check=False)
    uv_version = (uv_result.stdout or uv_result.stderr).strip()
    return {
        "status": "pass",
        "build_runtime": "uv",
        "python": platform.python_version(),
        "python_implementation": platform.python_implementation(),
        "pillow": PIL.__version__,
        "pypdf": pypdf.__version__,
        "reportlab": reportlab.Version,
        "uv": uv_version if uv_result.returncode == 0 else "unavailable",
    }


def _manual_review_errors(content: str) -> tuple[str, ...]:
    expected_header = ("Figure", *REVIEW_COLUMNS)
    errors: list[str] = []
    markers = tuple(marker.strip() for marker in _REVIEW_STATUS_MARKER.findall(content))
    if markers != ("PASS",):
        rendered_markers = ", ".join(markers) if markers else "none"
        errors.append(f"review status marker must be exactly one PASS (found: {rendered_markers})")
    table_rows = [_markdown_table_cells(line) for line in content.splitlines() if line.strip().startswith("|")]
    rows = [row for row in table_rows if row is not None]
    matching_headers = [index for index, row in enumerate(rows) if tuple(row) == expected_header]
    if len(matching_headers) != 1:
        return tuple(errors + ["required review columns missing or duplicated"])
    header_index = matching_headers[0]
    figure_rows: dict[str, tuple[str, ...]] = {}
    for row in rows[header_index + 1 :]:
        if all(cell and set(cell) <= {"-", ":"} for cell in row):
            continue
        if len(row) != len(expected_header):
            errors.append("review row has missing or extra columns")
            continue
        figure_id, *cells = row
        if figure_id not in REVIEW_FIGURE_IDS:
            errors.append(f"unexpected review row: {figure_id}")
            continue
        if figure_id in figure_rows:
            errors.append(f"duplicate review row: {figure_id}")
            continue
        figure_rows[figure_id] = tuple(cells)
        failed_columns = [
            REVIEW_COLUMNS[index] for index, cell in enumerate(cells) if cell != "PASS"
        ]
        if failed_columns:
            errors.append(f"{figure_id} has non-PASS cells: {', '.join(failed_columns)}")
    missing = [figure_id for figure_id in REVIEW_FIGURE_IDS if figure_id not in figure_rows]
    if missing:
        errors.append(f"missing review rows: {', '.join(missing)}")
    return tuple(errors)


def _markdown_table_cells(line: str) -> tuple[str, ...] | None:
    cells = [cell.strip() for cell in line.strip().split("|")]
    if not cells or cells[0] or cells[-1]:
        return None
    return tuple(cells[1:-1])


def _write_qa_receipt(output_root: Path, receipt: QaReceipt) -> Path:
    target = output_root / "qa" / "qa-receipt.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(receipt.to_json(), encoding="utf-8", newline="\n")
    return target


def run_qa(receipt: BuildReceipt) -> QaReceipt:
    """Create proof evidence and fail closed on structural, accessibility, or review defects."""
    output_root = receipt.output_root
    generated = output_root / "qa" / "generated"
    executable = _poppler_executable()
    checks: dict[str, Mapping[str, object]] = {}
    figure_results: dict[str, Mapping[str, object]] = {}
    artifact_hashes: dict[str, str] = {}
    palette = all_text_fill_contrasts(DEFAULT_TOKENS)
    checks["palette_contrast"] = {
        "status": "pass" if min(palette.values()) >= 4.5 else "fail",
        "minimum_ratio": min(palette.values()),
        "ratios": palette,
    }
    checks["poppler"] = (
        {"status": "unavailable", "detail": "bundled Poppler pdftoppm.exe not found"}
        if executable is None
        else {"status": "pass", "tool": "pdftoppm", "version": _poppler_version(executable)}
    )
    checks["source_provenance"] = {
        "status": "pass",
        "filename": receipt.source.filename,
        "sha256": receipt.source.sha256,
        "page_count": receipt.source.page_count,
    }
    checks["build_inputs"] = {"status": "pass", "files": receipt.build_inputs}
    checks["vendored_fonts"] = _vendored_font_receipt()
    checks["runtime_versions"] = _runtime_versions()

    proof_paths: dict[tuple[str, int, str], Path] = {}
    for artifact in receipt.figures:
        artifact_hashes[receipt._relative(artifact.svg)] = artifact.svg_sha256
        artifact_hashes[receipt._relative(artifact.pdf)] = artifact.pdf_sha256
        svg_check = _svg_vector_check(artifact.svg)
        pdf_check = _pdf_vector_check(artifact.pdf)
        text_contrasts = _scene_text_contrasts(artifact.scene)
        semantic = _semantic_redundancy(artifact.scene)
        min_font = _minimum_font_size(artifact.scene)
        proof = generated / "proof-pdf" / f"{artifact.figure_id}.pdf"
        a4 = _write_a4_proof(artifact, proof)
        effective_min_font = min_font * float(a4["scale"])
        ordinary_sizes = _ordinary_font_sizes(artifact.scene)
        effective_ordinary_min_font = (
            min(ordinary_sizes) * float(a4["scale"]) if ordinary_sizes else None
        )
        artifact_hashes[proof.relative_to(output_root).as_posix()] = _sha256(proof)
        if executable is not None:
            for dpi in PROOF_DPI:
                normal_base = generated / "proofs" / str(dpi) / "normal" / artifact.figure_id
                _render_pdf_png(executable, proof, normal_base, dpi)
                normal = normal_base.with_suffix(".png")
                proof_paths[(artifact.figure_id, dpi, "normal")] = normal
                artifact_hashes[normal.relative_to(output_root).as_posix()] = _sha256(normal)
                for mode in COLOR_MODES[1:]:
                    transformed = generated / "proofs" / str(dpi) / mode / f"{artifact.figure_id}.png"
                    _transform_png(normal, transformed, mode)
                    proof_paths[(artifact.figure_id, dpi, mode)] = transformed
                    artifact_hashes[transformed.relative_to(output_root).as_posix()] = _sha256(transformed)
        figure_results[artifact.figure_id] = {
            "status": "pass"
            if svg_check["passed"]
            and pdf_check["passed"]
            and min(text_contrasts.values()) >= 4.5
            and effective_min_font >= 7.0
            and effective_ordinary_min_font is not None
            and effective_ordinary_min_font >= 8.0
            and semantic["passed"]
            else "fail",
            "svg_vector": svg_check,
            "pdf_vector": pdf_check,
            "text_contrast": {"lowest_ratio": min(text_contrasts.values()), "ratios": text_contrasts},
            "font_size": {
                "status": "pass" if effective_min_font >= 7.0 else "fail",
                "native_minimum_pt": min_font,
                "effective_minimum_pt": effective_min_font,
                "ordinary_target_pt": 8.0,
                "ordinary_target_status": (
                    "pass"
                    if effective_ordinary_min_font is not None and effective_ordinary_min_font >= 8.0
                    else "fail"
                ),
                "effective_ordinary_minimum_pt": effective_ordinary_min_font,
                "ordinary_text_count": len(ordinary_sizes),
                "exception_text_count": len(_font_sizes(artifact.scene)) - len(ordinary_sizes),
                "exception_roles": sorted(ORDINARY_TEXT_EXCEPTION_ROLES),
            },
            "semantic_non_colour_redundancy": semantic,
            "a4_proof": a4,
        }

    if executable is not None:
        for mode in COLOR_MODES:
            contact = generated / "contact-sheets" / f"{mode}.png"
            _create_contact_sheet(
                [(artifact.figure_id, proof_paths[(artifact.figure_id, 144, mode)]) for artifact in receipt.figures],
                contact,
            )
            artifact_hashes[contact.relative_to(output_root).as_posix()] = _sha256(contact)
    checks["proof_rasterisation"] = {
        "status": "pass" if executable is not None else "unavailable",
        "dpi": list(PROOF_DPI),
        "colour_modes": list(COLOR_MODES),
        "colour_matrices": {key: list(value) for key, value in COLOR_MATRICES.items()},
    }
    failed_final_sizes = {
        figure_id: result["font_size"]["effective_minimum_pt"]
        for figure_id, result in figure_results.items()
        if result["font_size"]["effective_minimum_pt"] < 7.0
    }
    failed_ordinary_final_sizes = {
        figure_id: result["font_size"]["effective_ordinary_minimum_pt"]
        for figure_id, result in figure_results.items()
        if result["font_size"]["effective_ordinary_minimum_pt"] is None
        or result["font_size"]["effective_ordinary_minimum_pt"] < 8.0
    }
    checks["FINAL_SIZE_FONT"] = {
        "status": "pass" if not failed_final_sizes and not failed_ordinary_final_sizes else "fail",
        "minimum_pt": 7.0,
        "ordinary_target_pt": 8.0,
        "failed_effective_minimum_pt": failed_final_sizes,
        "failed_effective_ordinary_minimum_pt": failed_ordinary_final_sizes,
        "detail": (
            "all declared-width labels meet the 7 pt floor and 8 pt ordinary-label gate"
            if not failed_final_sizes and not failed_ordinary_final_sizes
            else "declared-width text is below the 7 pt floor or ordinary text is below the 8 pt gate"
        ),
    }
    checks["manual_visual_review"] = _manual_visual_review(output_root)
    passed = all(result["status"] == "pass" for result in figure_results.values()) and all(
        result["status"] == "pass" for result in checks.values()
    )
    qa_receipt = QaReceipt(passed, receipt.source, checks, figure_results, artifact_hashes)
    _write_qa_receipt(output_root, qa_receipt)
    return qa_receipt
