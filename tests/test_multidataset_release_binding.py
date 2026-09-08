from __future__ import annotations

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BUILDER = ROOT / "scripts" / "build_hardening_manifests.py"


def _load_builder():
    spec = importlib.util.spec_from_file_location("build_hardening_manifests", BUILDER)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_release_manifest_generator_binds_multidataset_safety_implementation() -> None:
    builder = _load_builder()

    assert "src/vego_multidataset/" in builder.SOURCE_PREFIXES
    assert {
        "scripts/build_multidataset_admission.py",
        "scripts/run_multidataset_engineering_preflight.py",
        "tests/test_multidataset_adapter.py",
        "tests/test_multidataset_admission.py",
        "tests/test_multidataset_admission_report.py",
        "tests/test_multidataset_preflight.py",
        "tests/test_multidataset_protocol.py",
        "tests/test_multidataset_release_binding.py",
    }.issubset(builder.SOURCE_EXTRA)
