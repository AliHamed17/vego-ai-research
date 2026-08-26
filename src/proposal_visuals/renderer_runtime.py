"""Pinned, workspace-local renderer verification for proposal integration.

The renderer bootstrap is implemented in PowerShell because it must extract a
Windows MSI.  This module is the independent fail-closed boundary used by the
post-integration verifier: it binds the executable engine and fonts to a tracked
manifest, validates the isolated LibreOffice profile, and applies the
baseline-aware Word pagination policy without disclosing local paths.
"""

from __future__ import annotations

import hashlib
import json
import re
import unicodedata
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any
from xml.etree import ElementTree

_SHA256 = re.compile(r"^[0-9A-F]{64}$")
_OOR = "http://openoffice.org/2001/registry"
_ENGINE_CONTRACT_ALGORITHM = "sha256-path-size-content-v1"
_ENGINE_CONTRACT_SCOPE = (
    "program/* (top-level files only)",
    "program/services/** (all files)",
    "share/registry/** (all files)",
    "share/fonts/truetype/** (all files)",
)


class RendererContractError(ValueError):
    """The pinned renderer, profile, or pagination evidence has drifted."""


@dataclass(frozen=True)
class RendererEvidence:
    """Private runtime inputs that are reduced to a path-free receipt."""

    manifest_path: Path
    runtime_root: Path
    profile_registry_path: Path
    version_output: str
    word_baseline_pages: int
    word_integrated_pages: int
    workspace_root: Path | None = None


def _sha256(path: Path) -> str:
    try:
        digest = hashlib.sha256()
        with path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(chunk)
        return digest.hexdigest().upper()
    except OSError as exc:
        raise RendererContractError(f"cannot hash renderer input {path.name}: {exc}") from exc


def _engine_contract_paths(root: Path) -> tuple[Path, ...]:
    candidates: set[Path] = set()
    try:
        program = root / "program"
        if program.is_dir():
            candidates.update(path for path in program.iterdir() if path.is_file())
        for relative in (
            Path("program/services"),
            Path("share/registry"),
            Path("share/fonts/truetype"),
        ):
            scope_root = root / relative
            if scope_root.is_dir():
                candidates.update(path for path in scope_root.rglob("*") if path.is_file())
    except OSError as exc:
        raise RendererContractError(f"cannot enumerate renderer engine contract: {exc}") from exc
    return tuple(candidates)


def _engine_contract(root: Path) -> dict[str, object]:
    rows: list[tuple[str, int, str]] = []
    normalized_paths: set[str] = set()
    for path in _engine_contract_paths(root):
        if path.is_symlink():
            raise RendererContractError("renderer engine contract must not contain symbolic links")
        relative = unicodedata.normalize("NFC", path.relative_to(root).as_posix())
        if relative in normalized_paths:
            raise RendererContractError(f"duplicate normalized engine path: {relative}")
        normalized_paths.add(relative)
        try:
            size = path.stat().st_size
        except OSError as exc:
            raise RendererContractError(f"cannot stat renderer engine file {path.name}: {exc}") from exc
        rows.append((relative, size, _sha256(path)))
    rows.sort(key=lambda item: item[0].encode("utf-8"))
    tree_digest = hashlib.sha256()
    for relative, size, file_hash in rows:
        tree_digest.update(f"{relative}\0{size}\0{file_hash}\n".encode())
    return {
        "algorithm": _ENGINE_CONTRACT_ALGORITHM,
        "scope": list(_ENGINE_CONTRACT_SCOPE),
        "file_count": len(rows),
        "total_bytes": sum(row[1] for row in rows),
        "tree_sha256": tree_digest.hexdigest().upper(),
    }


def _expected_engine_contract(value: Any) -> dict[str, object]:
    if not isinstance(value, dict):
        raise RendererContractError("renderer.engine_contract must be an object")
    if value.get("algorithm") != _ENGINE_CONTRACT_ALGORITHM:
        raise RendererContractError("renderer.engine_contract.algorithm is unsupported")
    if value.get("scope") != list(_ENGINE_CONTRACT_SCOPE):
        raise RendererContractError("renderer.engine_contract.scope is unsupported")
    result: dict[str, object] = {"algorithm": value["algorithm"]}
    result["scope"] = list(_ENGINE_CONTRACT_SCOPE)
    for key in ("file_count", "total_bytes"):
        number = value.get(key)
        if not isinstance(number, int) or isinstance(number, bool) or number <= 0:
            raise RendererContractError(
                f"renderer.engine_contract.{key} must be a positive integer"
            )
        result[key] = number
    result["tree_sha256"] = _required_sha(
        value, "tree_sha256", "renderer.engine_contract"
    )
    return result


def _load_manifest(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise RendererContractError(f"cannot read renderer manifest: {exc}") from exc
    if not isinstance(payload, dict) or payload.get("schema_version") != 1:
        raise RendererContractError("renderer manifest schema_version must be 1")
    renderer = payload.get("renderer")
    fonts = payload.get("fonts")
    profile = payload.get("profile")
    if not isinstance(renderer, dict) or not isinstance(fonts, list) or not isinstance(profile, dict):
        raise RendererContractError("renderer manifest is missing renderer, fonts, or profile")
    return payload


def _required_text(mapping: dict[str, Any], key: str, label: str) -> str:
    value = mapping.get(key)
    if not isinstance(value, str) or not value.strip():
        raise RendererContractError(f"{label}.{key} must be nonempty text")
    return value


def _required_sha(mapping: dict[str, Any], key: str, label: str) -> str:
    value = _required_text(mapping, key, label).upper()
    if not _SHA256.fullmatch(value):
        raise RendererContractError(f"{label}.{key} must be a SHA-256 digest")
    return value


def _required_https_url(mapping: dict[str, Any], key: str, label: str) -> str:
    value = _required_text(mapping, key, label)
    if not value.startswith("https://"):
        raise RendererContractError(f"{label}.{key} must be an HTTPS URL")
    return value


def _public_archive(mapping: Any, label: str) -> dict[str, object]:
    if not isinstance(mapping, dict):
        raise RendererContractError(f"{label} must be an object")
    size = mapping.get("bytes")
    if not isinstance(size, int) or isinstance(size, bool) or size <= 0:
        raise RendererContractError(f"{label}.bytes must be a positive integer")
    return {
        "url": _required_https_url(mapping, "url", label),
        "bytes": size,
        "sha256": _required_sha(mapping, "sha256", label),
    }


def _public_font_sources(value: Any) -> list[dict[str, object]]:
    if not isinstance(value, list):
        raise RendererContractError("font_sources must be a list")
    sources: list[dict[str, object]] = []
    for index, raw_source in enumerate(value, start=1):
        label = f"font_sources[{index}]"
        if not isinstance(raw_source, dict):
            raise RendererContractError(f"{label} must be an object")
        source: dict[str, object] = {"family": _required_text(raw_source, "family", label)}
        if "license" in raw_source:
            source["license"] = _required_text(raw_source, "license", label)
        if "url" in raw_source:
            source["url"] = _required_https_url(raw_source, "url", label)
            source["sha256"] = _required_sha(raw_source, "sha256", label)
            if "bytes" in raw_source:
                size = raw_source["bytes"]
                if not isinstance(size, int) or isinstance(size, bool) or size <= 0:
                    raise RendererContractError(f"{label}.bytes must be a positive integer")
                source["bytes"] = size
        elif "source" in raw_source:
            source["source"] = _required_text(raw_source, "source", label)
        else:
            raise RendererContractError(f"{label} must contain url or source provenance")
        sources.append(source)
    return sources


def _safe_runtime_path(root: Path, relative: str, label: str) -> Path:
    pure = PurePosixPath(relative)
    if pure.is_absolute() or not pure.parts or ".." in pure.parts:
        raise RendererContractError(f"{label} must be a safe relative path")
    resolved_root = root.resolve()
    resolved = (resolved_root / Path(*pure.parts)).resolve()
    try:
        resolved.relative_to(resolved_root)
    except ValueError as exc:
        raise RendererContractError(f"{label} escapes the renderer runtime") from exc
    return resolved


def _is_within(path: Path, root: Path) -> bool:
    try:
        path.resolve().relative_to(root.resolve())
    except ValueError:
        return False
    return True


def _oor_name(element: ElementTree.Element) -> str | None:
    return element.attrib.get(f"{{{_OOR}}}name")


def _profile_substitutions(path: Path) -> tuple[bool, list[dict[str, object]]]:
    try:
        root = ElementTree.parse(path).getroot()
    except (OSError, ElementTree.ParseError) as exc:
        raise RendererContractError(f"cannot parse isolated renderer profile: {exc}") from exc
    replacement_enabled: bool | None = None
    substitutions: list[dict[str, object]] = []
    for item in root.findall("item"):
        item_path = item.attrib.get(f"{{{_OOR}}}path")
        if item_path == "/org.openoffice.Office.Common/Font/Substitution":
            for prop in item.findall("prop"):
                if _oor_name(prop) == "Replacement":
                    replacement_enabled = (prop.findtext("value") or "").strip().casefold() == "true"
        elif item_path == "/org.openoffice.Office.Common/Font/Substitution/FontPairs":
            for node in item.findall("node"):
                values = {
                    _oor_name(prop): (prop.findtext("value") or "").strip()
                    for prop in node.findall("prop")
                }
                if values.get("ReplaceFont") and values.get("SubstituteFont"):
                    substitutions.append(
                        {
                            "replace": values["ReplaceFont"],
                            "with": values["SubstituteFont"],
                            "always": values.get("Always", "").casefold() == "true",
                            "on_screen_only": values.get("OnScreenOnly", "").casefold() == "true",
                        }
                    )
    return replacement_enabled is True, substitutions


def verify_renderer_evidence(evidence: RendererEvidence) -> dict[str, object]:
    """Validate renderer inputs and return a sanitized, receipt-ready record."""

    manifest_path = Path(evidence.manifest_path).resolve()
    runtime_root = Path(evidence.runtime_root).resolve()
    profile_path = Path(evidence.profile_registry_path).resolve()
    workspace_root = (
        Path(evidence.workspace_root).resolve()
        if evidence.workspace_root is not None
        else manifest_path.parent.resolve()
    )
    if not _is_within(runtime_root, workspace_root) or not _is_within(profile_path, workspace_root):
        raise RendererContractError("renderer runtime and isolated profile must be workspace-local")

    manifest = _load_manifest(manifest_path)
    renderer = manifest["renderer"]
    archive = _public_archive(renderer.get("archive"), "renderer.archive")
    font_sources = _public_font_sources(manifest.get("font_sources"))
    expected_engine_contract = _expected_engine_contract(renderer.get("engine_contract"))
    expected_executable = _required_sha(renderer, "executable_sha256", "renderer")
    executable = _safe_runtime_path(
        runtime_root,
        _required_text(renderer, "relative_executable", "renderer"),
        "renderer.relative_executable",
    )
    if not executable.is_file():
        raise RendererContractError("pinned soffice.com does not exist")
    actual_executable = _sha256(executable)
    if actual_executable != expected_executable:
        raise RendererContractError(
            f"renderer executable hash drift: expected {expected_executable}, got {actual_executable}"
        )
    expected_version = _required_text(renderer, "version_output", "renderer")
    if evidence.version_output.strip() != expected_version:
        raise RendererContractError("renderer version output does not match the pinned manifest")

    font_hashes: dict[str, str] = {}
    for index, raw_font in enumerate(manifest["fonts"], start=1):
        if not isinstance(raw_font, dict):
            raise RendererContractError(f"fonts[{index}] must be an object")
        relative = _required_text(raw_font, "relative_path", f"fonts[{index}]")
        expected = _required_sha(raw_font, "sha256", f"fonts[{index}]")
        font_path = _safe_runtime_path(runtime_root, relative, f"fonts[{index}].relative_path")
        if not font_path.is_file():
            raise RendererContractError(f"pinned renderer font is missing: {PurePosixPath(relative).name}")
        actual = _sha256(font_path)
        if actual != expected:
            raise RendererContractError(
                f"renderer font hash drift for {PurePosixPath(relative).name}: "
                f"expected {expected}, got {actual}"
            )
        font_hashes[PurePosixPath(relative).name] = actual

    actual_engine_contract = _engine_contract(runtime_root)
    if actual_engine_contract != expected_engine_contract:
        raise RendererContractError(
            "renderer engine contract drift: "
            f"expected {expected_engine_contract}, got {actual_engine_contract}"
        )

    manifest_profile = manifest["profile"]
    expected_substitutions = manifest_profile.get("substitutions")
    if manifest_profile.get("replacement_enabled") is not True or not isinstance(
        expected_substitutions, list
    ):
        raise RendererContractError("renderer manifest profile must require Replacement=true")
    replacement_enabled, actual_substitutions = _profile_substitutions(profile_path)
    if not replacement_enabled:
        raise RendererContractError("isolated renderer profile must set Replacement=true")
    public_substitutions = [
        {"replace": item["replace"], "with": item["with"], "always": item["always"]}
        for item in actual_substitutions
    ]
    if any(item["always"] is not True for item in public_substitutions):
        raise RendererContractError("every renderer font substitution must set Always=true")
    if any(item["on_screen_only"] is not False for item in actual_substitutions):
        raise RendererContractError("renderer font substitutions must not be screen-only")
    if public_substitutions != expected_substitutions:
        raise RendererContractError("isolated renderer profile substitutions drifted from manifest")

    baseline = evidence.word_baseline_pages
    integrated = evidence.word_integrated_pages
    if baseline <= 0 or integrated <= 0:
        raise RendererContractError("Word pagination evidence must use positive page counts")
    if integrated != baseline:
        raise RendererContractError(
            f"Word pagination drifted from baseline: baseline {baseline}, integrated {integrated}"
        )

    return {
        "passed": True,
        "renderer": {
            "name": _required_text(renderer, "name", "renderer"),
            "version": _required_text(renderer, "version", "renderer"),
            "build_id": _required_text(renderer, "build_id", "renderer"),
            "executable_sha256": actual_executable,
            "manifest_sha256": _sha256(manifest_path),
            "pdf_export_filter": _required_text(renderer, "pdf_export_filter", "renderer"),
            "workspace_local": True,
            "archive": archive,
            "engine_contract": actual_engine_contract,
        },
        "font_sources": font_sources,
        "fonts": {"count": len(font_hashes), "sha256": font_hashes},
        "profile": {
            "isolated": True,
            "replacement_enabled": True,
            "substitutions": public_substitutions,
        },
        "word_pagination": {
            "policy": "baseline-aware-sanity",
            "baseline_pages": baseline,
            "integrated_pages": integrated,
            "delta_pages": integrated - baseline,
            "passed": True,
            "authoritative_for_release": False,
        },
    }
