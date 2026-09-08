from __future__ import annotations

import pathlib
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

import study1_call_bound as bound  # noqa: E402

CALL_BOUND_DOC = (
    ROOT / "docs" / "research" / "phd-proposal" / "2026-09-04-one-setting-static-call-bound.md"
)


def test_minimum_bound_for_n0_n1_n4() -> None:
    assert bound.minimum_calls(0) == 4
    assert bound.minimum_calls(1) == 7
    assert bound.minimum_calls(4) == 16


def test_worst_case_bound_for_n0_n1_n4() -> None:
    assert bound.worst_case_calls(0) == 82
    assert bound.worst_case_calls(1) == 143
    assert bound.worst_case_calls(4) == 326


def test_max_qa_rounds_is_ten() -> None:
    assert bound.MAX_QA_ROUNDS == 10


def test_negative_case_count_fails_closed() -> None:
    for fn in (bound.minimum_calls, bound.worst_case_calls):
        with pytest.raises(ValueError):
            fn(-1)


def test_fractional_case_count_fails_closed() -> None:
    for fn in (bound.minimum_calls, bound.worst_case_calls, bound.call_bound_breakdown):
        with pytest.raises(ValueError):
            fn(2.5)  # type: ignore[arg-type]
    with pytest.raises(ValueError):
        bound.fake_client_call_counter(1, qa_dependent_calls=0.5)  # type: ignore[arg-type]


def test_boolean_case_count_fails_closed() -> None:
    with pytest.raises(ValueError):
        bound.minimum_calls(True)  # type: ignore[arg-type]


def test_inventory_derives_fixed_subtotals() -> None:
    fixed = [site for site in bound.CALL_SITES if site["scope"] == "fixed"]
    assert sum(int(site["min_calls"]) for site in fixed) == bound.MIN_BASE == 4
    assert sum(int(site["max_calls"]) for site in fixed) == bound.WORST_BASE == 82


def test_inventory_derives_per_case_subtotals() -> None:
    per_case = [site for site in bound.CALL_SITES if site["scope"] == "per_case"]
    assert sum(int(site["min_calls"]) for site in per_case) == bound.MIN_PER_CASE == 3
    assert sum(int(site["max_calls"]) for site in per_case) == bound.WORST_PER_CASE == 61


def test_inventory_expectations_rebuild_the_formulas() -> None:
    """Derive expected bounds from the inventory alone, independent of the constants."""
    derived_min_base = sum(
        int(site["min_calls"]) for site in bound.CALL_SITES if site["scope"] == "fixed"
    )
    derived_min_per_case = sum(
        int(site["min_calls"]) for site in bound.CALL_SITES if site["scope"] == "per_case"
    )
    derived_worst_base = sum(
        int(site["max_calls"]) for site in bound.CALL_SITES if site["scope"] == "fixed"
    )
    derived_worst_per_case = sum(
        int(site["max_calls"]) for site in bound.CALL_SITES if site["scope"] == "per_case"
    )
    for n in (0, 1, 4, 7):
        assert bound.minimum_calls(n) == derived_min_base + derived_min_per_case * n
        assert bound.worst_case_calls(n) == derived_worst_base + derived_worst_per_case * n


def test_inventory_structure_is_complete() -> None:
    assert len(bound.CALL_SITES) == 17
    labels = {str(site["label"]) for site in bound.CALL_SITES}
    assert "agent1/build_language_template" in labels
    assert "agent4/identify_patterns" in labels
    assert "agent3/{case}/map" in labels
    for site in bound.CALL_SITES:
        assert site["scope"] in {"fixed", "per_case"}
        assert 0 <= int(site["min_calls"]) <= int(site["max_calls"])
        assert "orchestrator.py" in str(site["evidence"])
        if site["conditional"]:
            assert int(site["min_calls"]) == 0
        assert int(site["max_calls"]) in {1, bound.MAX_QA_ROUNDS}


def test_unconditional_fixed_sites_match_min_base() -> None:
    unconditional_fixed = [
        site for site in bound.CALL_SITES
        if site["scope"] == "fixed" and not site["conditional"]
    ]
    assert sum(int(site["min_calls"]) for site in unconditional_fixed) == bound.MIN_BASE


def test_fake_counter_reports_fixed_per_case_and_qa_components() -> None:
    assert bound.fake_client_call_counter(0) == {
        "fixed_calls": 4, "per_case_calls": 0, "qa_dependent_calls": 0, "total_calls": 4,
    }
    assert bound.fake_client_call_counter(1) == {
        "fixed_calls": 4, "per_case_calls": 3, "qa_dependent_calls": 0, "total_calls": 7,
    }
    assert bound.fake_client_call_counter(4) == {
        "fixed_calls": 4, "per_case_calls": 12, "qa_dependent_calls": 0, "total_calls": 16,
    }


def test_call_bound_breakdown_accounts_for_max_rounds() -> None:
    breakdown = bound.call_bound_breakdown(4)
    assert breakdown["max_qa_rounds"] == 10
    assert breakdown["minimum_formula"] == "4 + 3N"
    assert breakdown["worst_case_formula"] == "82 + 61N"
    assert breakdown["worst_case_calls"] == 326
    assert breakdown["qa_dependent_worst_case"] == 78
    assert breakdown["call_site_count"] == 17


def test_document_is_consistent_with_module() -> None:
    text = CALL_BOUND_DOC.read_text(encoding="utf-8")
    assert "4 + 3N" in text
    assert "82 + 61N" in text
    assert bound.ORCHESTRATOR_SHA256 in text


def test_legacy_wrong_formula_is_not_reintroduced() -> None:
    """22 + 61*4 = 266, not 326; the string may appear only as a quoted correction."""
    module_text = (ROOT / "scripts" / "study1_call_bound.py").read_text(encoding="utf-8")
    doc_text = CALL_BOUND_DOC.read_text(encoding="utf-8")
    for text in (module_text, doc_text):
        for line in text.splitlines():
            if bound.FORBIDDEN_LEGACY_FORMULA in line:
                allowed = (
                    "wrong" in line.lower()
                    or "266" in line
                    or "FORBIDDEN_LEGACY_FORMULA" in line
                )
                assert allowed, (
                    "legacy formula reintroduced outside its correction context: " + line
                )
