"""Tests for the C2 governed-judgment conformance suite (chapter-4 section 4.4).

Mechanism/design tests only: fixtures use fixed timestamps and no test asserts
any empirical outcome (EXP-005 0/24).
"""

from __future__ import annotations

import importlib.util
import json
import shutil
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
SCRIPT = REPO / "scripts" / "run_governed_contract_conformance.py"
EXAMPLE = REPO / "schemas" / "examples" / "governed-judgment-record.valid.json"
VARIANTS_DIR = REPO / "schemas" / "examples" / "conformance-variants"


def _load_suite():
    spec = importlib.util.spec_from_file_location(
        "run_governed_contract_conformance", SCRIPT
    )
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


suite = _load_suite()


def load_example() -> dict:
    return json.loads(EXAMPLE.read_text(encoding="utf-8"))


def test_shipped_example_passes_every_subcheck() -> None:
    results = suite.reconstructability_checks(load_example())
    assert [result.reason for result in results if not result.passed] == []
    assert len(results) == 14
    reasons = [result.reason for result in results]
    assert len(reasons) == len(set(reasons))


def test_cli_defaults_exit_zero_and_report_completeness_gap(capsys) -> None:
    assert suite.main(["--check"]) == 0
    output = capsys.readouterr().out
    assert "GOVERNED CONTRACT CONFORMANCE: PASS" in output
    assert "[not_run] independent-implementer completeness review" in output
    assert "independent_implementer_not_recruited" in output


def test_cli_record_flag_checks_single_record(capsys) -> None:
    assert suite.main(["--record", str(EXAMPLE)]) == 0
    output = capsys.readouterr().out
    assert "skipped: --record checks a single record only" in output


def test_variant_directory_matches_registry() -> None:
    on_disk = sorted(path.name for path in VARIANTS_DIR.glob("*.json"))
    assert on_disk == sorted(suite.VARIANT_EXPECTATIONS)
    assert all(name.endswith(".invalid.json") for name in on_disk)


@pytest.mark.parametrize(
    ("variant_name", "expected_reason"), sorted(suite.VARIANT_EXPECTATIONS.items())
)
def test_each_variant_fails_for_its_named_reason(
    variant_name: str, expected_reason: str
) -> None:
    record = json.loads((VARIANTS_DIR / variant_name).read_text(encoding="utf-8"))
    failed = suite.failed_reasons(suite.reconstructability_checks(record))
    assert failed, f"{variant_name} passed the suite"
    assert expected_reason in failed
    row = suite.evaluate_variant(variant_name, record)
    assert row.caught is True
    assert row.expected_reason == expected_reason


def test_dangling_rationale_ref_variant_is_schema_valid_but_rejected() -> None:
    record = json.loads(
        (VARIANTS_DIR / "gjr-variant-dangling-rationale-ref.invalid.json").read_text(
            encoding="utf-8"
        )
    )
    results = suite.reconstructability_checks(record)
    by_reason = {result.reason: result.passed for result in results}
    assert by_reason["schema_conformance"] is True
    assert by_reason["rationale_refs_resolve"] is False


def test_competence_claim_mismatch_caught_by_reference_resolution() -> None:
    record = load_example()
    record["competence"]["assessedForClaimId"] = "CLAIM-SE310-2026S-A2-9999-OTHER-01"
    failed = suite.failed_reasons(suite.reconstructability_checks(record))
    assert "claim_references_resolve" in failed


def test_conforming_variant_fails_discrimination(tmp_path: Path, capsys) -> None:
    shutil.copyfile(
        EXAMPLE, tmp_path / "gjr-variant-scope-removed.invalid.json"
    )
    rows, problems = suite.discrimination_results(tmp_path)
    assert [row.caught for row in rows] == [False]
    assert "variant PASSED the whole suite" in rows[0].detail
    assert any("registered variant missing on disk" in item for item in problems)
    assert suite.main(["--variants-dir", str(tmp_path)]) == 1
    assert "GOVERNED CONTRACT CONFORMANCE: FAIL" in capsys.readouterr().out


def test_unregistered_variant_fails_discrimination(tmp_path: Path) -> None:
    for name in suite.VARIANT_EXPECTATIONS:
        shutil.copyfile(VARIANTS_DIR / name, tmp_path / name)
    shutil.copyfile(EXAMPLE, tmp_path / "gjr-variant-unregistered.invalid.json")
    rows, problems = suite.discrimination_results(tmp_path)
    assert problems == []
    unregistered = [row for row in rows if row.expected_reason == "<unregistered>"]
    assert len(unregistered) == 1
    assert unregistered[0].caught is False


def test_empty_variants_dir_fails_discrimination(tmp_path: Path) -> None:
    assert suite.main(["--variants-dir", str(tmp_path)]) == 1
