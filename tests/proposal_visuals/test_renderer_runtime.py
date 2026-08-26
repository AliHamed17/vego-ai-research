from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from proposal_visuals.renderer_runtime import (
    RendererContractError,
    RendererEvidence,
    verify_renderer_evidence,
)


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest().upper()


_ENGINE_SCOPE = [
    "program/* (top-level files only)",
    "program/services/** (all files)",
    "share/registry/** (all files)",
    "share/fonts/truetype/** (all files)",
]


def _engine_contract(root: Path) -> dict[str, object]:
    rows: list[tuple[str, int, str]] = []
    candidates = set(path for path in (root / "program").iterdir() if path.is_file())
    for relative in (
        Path("program/services"),
        Path("share/registry"),
        Path("share/fonts/truetype"),
    ):
        scope_root = root / relative
        if scope_root.is_dir():
            candidates.update(path for path in scope_root.rglob("*") if path.is_file())
    for path in candidates:
        payload = path.read_bytes()
        rows.append((path.relative_to(root).as_posix(), len(payload), _sha256(payload)))
    rows.sort(key=lambda item: item[0].encode())
    digest = hashlib.sha256()
    for relative, size, file_hash in rows:
        digest.update(f"{relative}\0{size}\0{file_hash}\n".encode())
    return {
        "algorithm": "sha256-path-size-content-v1",
        "scope": _ENGINE_SCOPE,
        "file_count": len(rows),
        "total_bytes": sum(row[1] for row in rows),
        "tree_sha256": digest.hexdigest().upper(),
    }


def _profile_xml(*, always: bool = True, replacement: bool = True) -> str:
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<oor:items xmlns:oor="http://openoffice.org/2001/registry">
  <item oor:path="/org.openoffice.Office.Common/Font/Substitution/FontPairs">
    <node oor:name="_0" oor:op="replace">
      <prop oor:name="Always" oor:op="fuse"><value>{str(always).lower()}</value></prop>
      <prop oor:name="ReplaceFont" oor:op="fuse"><value>Calibri</value></prop>
      <prop oor:name="OnScreenOnly" oor:op="fuse"><value>false</value></prop>
      <prop oor:name="SubstituteFont" oor:op="fuse"><value>Carlito</value></prop>
    </node>
    <node oor:name="_1" oor:op="replace">
      <prop oor:name="Always" oor:op="fuse"><value>{str(always).lower()}</value></prop>
      <prop oor:name="ReplaceFont" oor:op="fuse"><value>Cambria</value></prop>
      <prop oor:name="OnScreenOnly" oor:op="fuse"><value>false</value></prop>
      <prop oor:name="SubstituteFont" oor:op="fuse"><value>Caladea</value></prop>
    </node>
  </item>
  <item oor:path="/org.openoffice.Office.Common/Font/Substitution">
    <prop oor:name="Replacement" oor:op="fuse"><value>{str(replacement).lower()}</value></prop>
  </item>
</oor:items>
"""


@pytest.fixture
def renderer_fixture(tmp_path: Path) -> RendererEvidence:
    runtime = tmp_path / "runtime"
    program = runtime / "program"
    fonts = runtime / "share" / "fonts" / "truetype"
    program.mkdir(parents=True)
    fonts.mkdir(parents=True)
    executable = program / "soffice.com"
    executable.write_bytes(b"pinned-renderer")
    (program / "soffice.bin").write_bytes(b"writer-engine")
    filter_file = runtime / "share" / "registry" / "writerfilter.xcd"
    filter_file.parent.mkdir(parents=True)
    filter_file.write_bytes(b"pdf-filter")
    font_contracts = []
    for index, name in enumerate(
        (
            "Caladea-Bold.ttf",
            "Caladea-BoldItalic.ttf",
            "Caladea-Italic.ttf",
            "Caladea-Regular.ttf",
            "Carlito-Bold.ttf",
            "Carlito-BoldItalic.ttf",
            "Carlito-Italic.ttf",
            "Carlito-Regular.ttf",
        ),
        start=1,
    ):
        payload = f"font-{index}".encode()
        (fonts / name).write_bytes(payload)
        font_contracts.append(
            {
                "relative_path": f"share/fonts/truetype/{name}",
                "sha256": _sha256(payload),
            }
        )
    engine_contract = _engine_contract(runtime)
    manifest = tmp_path / "renderer-manifest.json"
    manifest.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "renderer": {
                    "name": "LibreOffice",
                    "version": "24.2.7.2",
                    "build_id": "test-build",
                    "license": "MPL-2.0 / LGPL-3.0-or-later",
                    "archive": {
                        "url": "https://example.invalid/libreoffice.msi",
                        "bytes": 123,
                        "sha256": "A" * 64,
                    },
                    "relative_executable": "program/soffice.com",
                    "executable_sha256": _sha256(b"pinned-renderer"),
                    "version_output": "LibreOffice 24.2.7.2 test-build",
                    "pdf_export_filter": "writer_pdf_Export",
                    "engine_contract": engine_contract,
                },
                "font_sources": [
                    {
                        "family": "Caladea",
                        "url": "https://example.invalid/caladea.tar.gz",
                        "sha256": "B" * 64,
                    }
                ],
                "fonts": font_contracts,
                "profile": {
                    "replacement_enabled": True,
                    "substitutions": [
                        {"replace": "Calibri", "with": "Carlito", "always": True},
                        {"replace": "Cambria", "with": "Caladea", "always": True},
                    ],
                },
            }
        ),
        encoding="utf-8",
    )
    profile = tmp_path / "profile" / "user" / "registrymodifications.xcu"
    profile.parent.mkdir(parents=True)
    profile.write_text(_profile_xml(), encoding="utf-8")
    return RendererEvidence(
        manifest_path=manifest,
        runtime_root=runtime,
        profile_registry_path=profile,
        version_output="LibreOffice 24.2.7.2 test-build",
        word_baseline_pages=33,
        word_integrated_pages=33,
    )


def test_runtime_receipt_binds_renderer_fonts_profile_and_baseline_without_private_paths(
    renderer_fixture: RendererEvidence,
) -> None:
    result = verify_renderer_evidence(renderer_fixture)

    assert result["passed"] is True
    assert result["renderer"] == {
        "name": "LibreOffice",
        "version": "24.2.7.2",
        "build_id": "test-build",
        "executable_sha256": _sha256(b"pinned-renderer"),
        "manifest_sha256": _sha256(renderer_fixture.manifest_path.read_bytes()),
        "pdf_export_filter": "writer_pdf_Export",
        "workspace_local": True,
        "archive": {
            "url": "https://example.invalid/libreoffice.msi",
            "bytes": 123,
            "sha256": "A" * 64,
        },
        "engine_contract": _engine_contract(renderer_fixture.runtime_root),
    }
    assert result["fonts"]["count"] == 8
    assert result["renderer"]["engine_contract"] == _engine_contract(
        renderer_fixture.runtime_root
    )
    assert result["font_sources"] == [
        {
            "family": "Caladea",
            "url": "https://example.invalid/caladea.tar.gz",
            "sha256": "B" * 64,
        }
    ]
    assert result["profile"] == {
        "isolated": True,
        "replacement_enabled": True,
        "substitutions": [
            {"replace": "Calibri", "with": "Carlito", "always": True},
            {"replace": "Cambria", "with": "Caladea", "always": True},
        ],
    }
    assert result["word_pagination"] == {
        "policy": "baseline-aware-sanity",
        "baseline_pages": 33,
        "integrated_pages": 33,
        "delta_pages": 0,
        "passed": True,
        "authoritative_for_release": False,
    }
    serialized = json.dumps(result)
    assert str(renderer_fixture.runtime_root) not in serialized
    assert str(renderer_fixture.profile_registry_path) not in serialized


def test_runtime_verification_rejects_executable_drift(
    renderer_fixture: RendererEvidence,
) -> None:
    (renderer_fixture.runtime_root / "program" / "soffice.com").write_bytes(b"drift")

    with pytest.raises(RendererContractError, match="executable hash drift"):
        verify_renderer_evidence(renderer_fixture)


@pytest.mark.parametrize("mutation", ["change", "addition", "removal"])
def test_runtime_verification_binds_every_engine_and_filter_file(
    renderer_fixture: RendererEvidence,
    mutation: str,
) -> None:
    if mutation == "change":
        (renderer_fixture.runtime_root / "program" / "soffice.bin").write_bytes(b"drift")
    elif mutation == "addition":
        (renderer_fixture.runtime_root / "program" / "unexpected-filter.dll").write_bytes(b"new")
    else:
        (renderer_fixture.runtime_root / "share" / "registry" / "writerfilter.xcd").unlink()

    with pytest.raises(RendererContractError, match="engine contract drift"):
        verify_renderer_evidence(renderer_fixture)


def test_runtime_verification_excludes_nonexecutable_localization_resources(
    renderer_fixture: RendererEvidence,
) -> None:
    resource = renderer_fixture.runtime_root / "share" / "config" / "images.zip"
    resource.parent.mkdir(parents=True)
    resource.write_bytes(b"non-executable-resource")

    assert verify_renderer_evidence(renderer_fixture)["passed"] is True


@pytest.mark.parametrize(
    ("profile_xml", "message"),
    [
        (_profile_xml(always=False), "Always=true"),
        (_profile_xml(replacement=False), "Replacement=true"),
    ],
)
def test_runtime_verification_rejects_unsafe_profile_semantics(
    renderer_fixture: RendererEvidence,
    profile_xml: str,
    message: str,
) -> None:
    renderer_fixture.profile_registry_path.write_text(profile_xml, encoding="utf-8")

    with pytest.raises(RendererContractError, match=message):
        verify_renderer_evidence(renderer_fixture)


def test_word_pagination_is_baseline_aware_not_an_exact_31_page_gate(
    renderer_fixture: RendererEvidence,
) -> None:
    changed = RendererEvidence(
        manifest_path=renderer_fixture.manifest_path,
        runtime_root=renderer_fixture.runtime_root,
        profile_registry_path=renderer_fixture.profile_registry_path,
        version_output=renderer_fixture.version_output,
        word_baseline_pages=33,
        word_integrated_pages=34,
    )

    with pytest.raises(RendererContractError, match="Word pagination drifted from baseline"):
        verify_renderer_evidence(changed)
