"""Frozen experiment manifest: loading, self-binding and gate helpers."""

from __future__ import annotations

import hashlib
import json
import platform
import subprocess
import sys
from pathlib import Path
from typing import Any

import jsonschema

from . import constants as c
from .budget import per_request_reserve_usd, total_request_cap
from .contract import OUTPUT_SCHEMA_SHA256, canonical_sha256

ROOT = Path(__file__).resolve().parents[3]
DOCS_DIR = ROOT / "docs" / "research" / "phd-proposal" / "study2-prospective"
MANIFEST_PATH = DOCS_DIR / "experiment-manifest.json"
CASE_SELECTION_PATH = DOCS_DIR / "case-selection-manifest.json"
BUDGET_PATH = DOCS_DIR / "budget-reservation.json"
FINGERPRINT_PATH = DOCS_DIR / "command-fingerprint.json"
SCHEMA_DIR = ROOT / "schemas"


class ManifestError(ValueError):
    """The frozen manifest is missing, unbound, or disagrees with the code."""


def load_schema(name: str) -> dict[str, Any]:
    return json.loads((SCHEMA_DIR / f"{name}.schema.json").read_text(encoding="utf-8"))


def self_bound(document: dict[str, Any], field: str = "manifest_sha256") -> dict[str, Any]:
    body = {k: v for k, v in document.items() if k != field}
    return {**body, field: canonical_sha256(body)}


def verify_self_binding(document: dict[str, Any], field: str = "manifest_sha256") -> None:
    body = {k: v for k, v in document.items() if k != field}
    if document.get(field) != canonical_sha256(body):
        raise ManifestError(f"{field} does not match the document body")


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_manifest(path: Path = MANIFEST_PATH) -> dict[str, Any]:
    if not path.is_file():
        raise ManifestError(f"manifest missing: {path.relative_to(ROOT)}")
    manifest = json.loads(path.read_text(encoding="utf-8"))
    try:
        jsonschema.Draft202012Validator(load_schema(c.MANIFEST_SCHEMA)).validate(manifest)
    except jsonschema.ValidationError as exc:
        raise ManifestError(f"manifest schema: {exc.message}") from exc
    verify_self_binding(manifest)
    assert_constants_match(manifest)
    bound_documents = (
        ("case_selection", "path", "sha256", CASE_SELECTION_PATH),
        ("budget", "reservation_path", "reservation_sha256", BUDGET_PATH),
    )
    for key, path_field, sha_field, expected_path in bound_documents:
        block = manifest[key]
        target = ROOT / block[path_field]
        if target != expected_path:
            raise ManifestError(f"{key} path differs from the frozen location")
        if not target.is_file() or file_sha256(target) != block[sha_field]:
            raise ManifestError(f"{key} document digest mismatch")
    if manifest["output_schema"]["sha256"] != OUTPUT_SCHEMA_SHA256:
        raise ManifestError("shared output schema digest drifted since freeze")
    return manifest


def assert_constants_match(manifest: dict[str, Any]) -> None:
    provider = manifest["provider"]
    budget = manifest["budget"]
    caps = manifest["caps"]
    checks = {
        "provider.model": (provider["model"], c.MODEL),
        "provider.name": (provider["name"], c.PROVIDER),
        "provider.allowed_hosts": (tuple(provider["allowed_hosts"]), tuple(sorted(c.ALLOWED_HOSTS))),
        "budget.hard_ceiling_usd": (budget["hard_ceiling_usd"], c.HARD_CEILING_USD),
        "budget.guard_ceiling_usd": (budget["guard_ceiling_usd"], c.GUARD_CEILING_USD),
        "budget.reserve_input_tokens": (budget["reserve_input_tokens"], c.RESERVE_INPUT_TOKENS),
        "budget.max_output_tokens": (budget["max_output_tokens"], c.MAX_OUTPUT_TOKENS),
        "budget.price_in": (budget["price_in_per_1m_usd"], c.PRICE_IN_PER_M),
        "budget.price_out": (budget["price_out_per_1m_usd"], c.PRICE_OUT_PER_M),
        "budget.per_request_reserve": (budget["per_request_reserve_usd"], round(per_request_reserve_usd(), 7)),
        "caps.total": (caps["total_requests"], total_request_cap()),
        "caps.on": (caps[c.CONDITION_ON], c.ON_REQUEST_CAP_PER_CASE * manifest["case_selection"]["sample_size"]),
        "caps.off": (caps[c.CONDITION_OFF], c.OFF_REQUEST_CAP_PER_CASE * manifest["case_selection"]["sample_size"]),
        "request.max_completion_tokens": (manifest["request_parameters"]["max_completion_tokens"], c.MAX_OUTPUT_TOKENS),
        "request.timeout": (manifest["request_parameters"]["request_timeout_seconds"], c.REQUEST_TIMEOUT_SECONDS),
        "retry.transport": (manifest["retry_policy"]["transport_retries_per_request"], c.TRANSPORT_RETRIES_PER_REQUEST),
        "selection.seed": (manifest["case_selection"]["seed"], c.SELECTION_SEED),
        "order": (tuple(manifest["execution_order"]), c.CONDITION_ORDER),
    }
    mismatches = [k for k, (a, b) in checks.items() if a != b]
    if mismatches:
        raise ManifestError(f"manifest disagrees with frozen constants: {mismatches}")
    if caps[c.CONDITION_ON] + caps[c.CONDITION_OFF] > caps["total_requests"]:
        raise ManifestError("condition caps exceed the total request cap")
    reservation = (caps[c.CONDITION_ON] + caps[c.CONDITION_OFF]) * per_request_reserve_usd()
    if reservation > c.GUARD_CEILING_USD + 1e-9:
        raise ManifestError("whole-study reservation exceeds the guard ceiling")
    if abs(reservation - budget["whole_study_reservation_usd"]) > 5e-4:
        raise ManifestError("recorded whole-study reservation differs from the recomputed value")
    if manifest["case_selection"]["sample_size"] < c.MIN_PAIRED_CASES:
        raise ManifestError("fewer than the minimum paired cases")


def git(*args: str) -> str:
    return subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True, check=True).stdout.strip()


def git_head() -> str:
    return git("rev-parse", "HEAD")


def git_is_clean() -> bool:
    return git("status", "--porcelain", "--untracked-files=no") == ""


def environment_fingerprint() -> dict[str, Any]:
    try:
        import openai

        openai_version = openai.__version__
    except Exception:  # noqa: BLE001 - reported as unknown
        openai_version = "unknown"
    return {
        "python": platform.python_version(),
        "implementation": platform.python_implementation(),
        "openai_sdk": openai_version,
        "platform": platform.system(),
    }


def command_fingerprint(public_argv: list[str]) -> dict[str, Any]:
    """Hash the command with private paths replaced by the placeholder token."""
    return {
        "argv_public": public_argv,
        "argv_sha256": hashlib.sha256(json.dumps(public_argv).encode("utf-8")).hexdigest(),
        "entrypoint": "scripts/study2_prospective_run.py",
        "entrypoint_sha256": file_sha256(ROOT / "scripts" / "study2_prospective_run.py"),
        "package_sha256": package_sha256(),
        "python_major_minor": ".".join(map(str, sys.version_info[:2])),
    }


def package_sha256() -> str:
    digest = hashlib.sha256()
    package = ROOT / "src" / "vego_study2" / "prospective"
    for path in sorted(package.glob("*.py")):
        digest.update(path.name.encode("utf-8"))
        digest.update(path.read_bytes())
    return digest.hexdigest()
