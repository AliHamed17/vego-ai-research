#!/usr/bin/env python3
"""Executable conformance suite for the C2 governed-judgment contract.

Implements the three parts chapter-4 section 4.4 specifies for the contract in
``schemas/governed-judgment-record-v1.schema.json``:

- RECONSTRUCTABILITY: mechanically verify that a conforming record alone
  answers what was judged, why, and under what scope — decision-trace slots
  present and internally referenced, rationale refs resolving to real slot
  ids, scope carrying at least one predicate term and one exclusion,
  verdict/rationale/uncertainty present, bindings and claim references
  resolving, and the recorded reuse gate agreeing with the lifecycle state.
- DISCRIMINATION: every deliberately non-conforming variant in
  ``schemas/examples/conformance-variants/`` must fail the suite for the
  specific named reason registered for it; a variant that passes fails the
  whole suite.
- COMPLETENESS REVIEW: the independent-implementer arm is reported honestly
  as not_run (reason: independent_implementer_not_recruited).

Read-only, deterministic, offline: no LLM/API calls, no network, no writes.
Reuses ``src/vego_governed`` (WS-A) for schema validation and reuse-gate
recomputation instead of duplicating either. Design artifact only: a PASS is
a mechanism/conformance result and asserts no empirical outcome
(EXP-005 0/24).

Run:  python scripts/run_governed_contract_conformance.py [--check]
      python scripts/run_governed_contract_conformance.py --record PATH
"""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from types import MappingProxyType
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from vego_governed import lifecycle, records  # noqa: E402

EXAMPLE = ROOT / "schemas" / "examples" / "governed-judgment-record.valid.json"
VARIANTS_DIR = ROOT / "schemas" / "examples" / "conformance-variants"
VARIANT_SUFFIX = ".invalid.json"

TRACE_SLOT_NAMES = (
    "claim",
    "evidence",
    "appliedRuleOrGuideline",
    "alternativesConsidered",
    "sourceOfUncertainty",
    "decisiveInference",
)

COMPLETENESS_STATUS = "not_run"
COMPLETENESS_REASON = "independent_implementer_not_recruited"

VARIANT_EXPECTATIONS: Mapping[str, str] = MappingProxyType(
    {
        "gjr-variant-scope-removed.invalid.json": "scope_predicate_present",
        "gjr-variant-stuck-in-draft.invalid.json": (
            "left_draft_before_asserting_reuse"
        ),
        "gjr-variant-authority-removed.invalid.json": "authority_binding_present",
        "gjr-variant-dissent-ignored.invalid.json": "qualified_dissent_blocks_reuse",
        "gjr-variant-dangling-rationale-ref.invalid.json": "rationale_refs_resolve",
    }
)

PASS, FAIL = "OK  ", "FAIL"


@dataclass(frozen=True)
class CheckResult:
    """One reconstructability sub-check; ``reason`` is its stable named reason."""

    check_id: str
    reason: str
    passed: bool
    detail: str = ""


@dataclass(frozen=True)
class VariantResult:
    """One discrimination row: variant-name -> named-reason, and whether caught."""

    name: str
    expected_reason: str
    failed_reasons: tuple[str, ...]
    caught: bool
    detail: str = ""


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _id_set(items: Any, key: str) -> set[str]:
    if not isinstance(items, list):
        return set()
    return {
        entry[key]
        for entry in items
        if isinstance(entry, Mapping) and isinstance(entry.get(key), str)
    }


def reconstructability_checks(record: Mapping[str, Any]) -> list[CheckResult]:
    """Run every reconstructability sub-check over one raw record mapping.

    Structural checks are evaluated defensively against missing fields so a
    non-conforming variant fails with its own named reason rather than a
    KeyError, and so failures beyond the schema check stay attributable.
    """

    results: list[CheckResult] = []

    def add(check_id: str, reason: str, passed: bool, detail: str = "") -> None:
        results.append(CheckResult(check_id, reason, bool(passed), detail))

    schema_issues = records.schema_errors(dict(record))
    add(
        "RC-01",
        "schema_conformance",
        not schema_issues,
        "; ".join(schema_issues[:2])
        + (f" (+{len(schema_issues) - 2} more)" if len(schema_issues) > 2 else ""),
    )

    case = _mapping(record.get("caseGrounding"))
    evidence_ids = _id_set(case.get("evidence"), "evidenceId")
    judged_claim = case.get("claimId")
    add(
        "RC-02",
        "judged_claim_grounded",
        bool(judged_claim)
        and bool(_mapping(case.get("fragmentRef")).get("locator"))
        and bool(case.get("observedDeviation"))
        and bool(evidence_ids),
        "caseGrounding must name the judged claim, fragment, deviation, and evidence",
    )

    slots = _mapping(_mapping(record.get("decisionTrace")).get("slots"))
    missing_slots = [
        name
        for name in TRACE_SLOT_NAMES
        if not _mapping(slots.get(name)).get("slotId")
        or not _mapping(slots.get(name)).get("content")
    ]
    add(
        "RC-03",
        "trace_slots_present",
        not missing_slots,
        "missing or empty trace slots: " + ", ".join(missing_slots),
    )
    slot_ids = {
        _mapping(slot).get("slotId")
        for slot in slots.values()
        if _mapping(slot).get("slotId")
    }

    bindings = _mapping(record.get("bindings"))
    binding_ids = _id_set(bindings.get("systemBindings"), "bindingId") | _id_set(
        bindings.get("artifactBindings"), "bindingId"
    )
    dangling_trace_refs = [
        f"slots.{name}.{field}[{ref!r}]"
        for name in TRACE_SLOT_NAMES
        for field, known in (("evidenceIds", evidence_ids), ("bindingIds", binding_ids))
        for ref in _mapping(slots.get(name)).get(field) or []
        if ref not in known
    ]
    add(
        "RC-04",
        "trace_refs_resolve",
        not dangling_trace_refs,
        "unresolved trace references: " + ", ".join(dangling_trace_refs),
    )

    rationale = _mapping(record.get("rationale"))
    structure = rationale.get("structure")
    add(
        "RC-05",
        "rationale_present",
        bool(rationale.get("freeText"))
        and isinstance(structure, list)
        and len(structure) >= 1,
        "rationale must carry freeText plus at least one structured assertion",
    )

    dangling_rationale_refs = []
    for index, assertion in enumerate(structure if isinstance(structure, list) else []):
        entry = _mapping(assertion)
        if entry.get("traceSlotRef") not in slot_ids:
            dangling_rationale_refs.append(
                f"structure[{index}].traceSlotRef={entry.get('traceSlotRef')!r}"
            )
        dangling_rationale_refs.extend(
            f"structure[{index}].evidenceIds[{ref!r}]"
            for ref in entry.get("evidenceIds") or []
            if ref not in evidence_ids
        )
    uncertainty = _mapping(record.get("uncertainty"))
    sources = uncertainty.get("sources")
    for index, source in enumerate(sources if isinstance(sources, list) else []):
        ref = _mapping(source).get("traceSlotRef")
        if ref is not None and ref not in slot_ids:
            dangling_rationale_refs.append(f"uncertainty.sources[{index}]={ref!r}")
    add(
        "RC-06",
        "rationale_refs_resolve",
        not dangling_rationale_refs,
        "refs to nonexistent slots/evidence: " + ", ".join(dangling_rationale_refs),
    )

    scope = _mapping(record.get("scope"))
    terms = _mapping(scope.get("predicate")).get("terms")
    add(
        "RC-07",
        "scope_predicate_present",
        isinstance(terms, list) and len(terms) >= 1,
        "scope must carry a predicate with at least one term",
    )
    exclusions = scope.get("exclusions")
    add(
        "RC-08",
        "scope_exclusions_present",
        isinstance(exclusions, list) and len(exclusions) >= 1,
        "scope must record at least one exclusion (the negative half)",
    )

    verdict = _mapping(record.get("verdict"))
    add(
        "RC-09",
        "verdict_and_uncertainty_present",
        bool(verdict.get("value"))
        and bool(verdict.get("dispositionClass"))
        and bool(uncertainty.get("selfRating"))
        and isinstance(sources, list)
        and len(sources) >= 1,
        "verdict value/dispositionClass and uncertainty selfRating/sources required",
    )

    competence = record.get("competence")
    authority = record.get("authority")
    claim_mismatches = []
    if isinstance(competence, Mapping) and competence.get(
        "assessedForClaimId"
    ) != judged_claim:
        claim_mismatches.append(
            f"competence.assessedForClaimId={competence.get('assessedForClaimId')!r}"
        )
    if isinstance(authority, Mapping) and _mapping(authority.get("mandate")).get(
        "claimId"
    ) != judged_claim:
        claim_mismatches.append(
            "authority.mandate.claimId="
            f"{_mapping(authority.get('mandate')).get('claimId')!r}"
        )
    add(
        "RC-10",
        "claim_references_resolve",
        not claim_mismatches,
        f"does not match caseGrounding.claimId {judged_claim!r}: "
        + ", ".join(claim_mismatches),
    )

    lifecycle_group = _mapping(record.get("lifecycle"))
    transitions = lifecycle_group.get("transitions")
    receipts_use = _mapping(record.get("receipts")).get("use")
    agents = _mapping(record.get("provenance")).get("agents")
    claims_binding = (
        any(
            _mapping(item).get("accepted") is True
            and _mapping(item).get("actorAuthorityRef")
            for item in (transitions if isinstance(transitions, list) else [])
        )
        or any(
            _mapping(item).get("useMode") == "binding_decision"
            for item in (receipts_use if isinstance(receipts_use, list) else [])
        )
        or any(
            _mapping(item).get("actorAuthorityRef")
            for item in (agents if isinstance(agents, list) else [])
        )
    )
    add(
        "RC-11",
        "authority_binding_present",
        not claims_binding
        or (
            isinstance(authority, Mapping)
            and authority.get("claimScoped") is True
            and bool(authority.get("bindingPower"))
        ),
        "record claims binding force but carries no claim-scoped authority binding",
    )

    state = lifecycle_group.get("state")
    recorded_gate = _mapping(lifecycle_group.get("reuseGate"))
    retained = record.get("retainedDissent")
    dissent_entries = retained if isinstance(retained, list) else []
    if not lifecycle_group:
        add("RC-12", "reuse_gate_recomputes", True, "no lifecycle content group")
    elif state not in lifecycle.STATES:
        add("RC-12", "reuse_gate_recomputes", False, f"unknown state {state!r}")
    else:
        expected_gate = lifecycle.reuse_gate(state, dissent_entries)
        add(
            "RC-12",
            "reuse_gate_recomputes",
            recorded_gate.get("decision") == expected_gate["decision"]
            and sorted(recorded_gate.get("blockingReasons") or [])
            == sorted(expected_gate["blockingReasons"]),
            f"recorded gate {recorded_gate.get('decision')!r} != gate recomputed "
            f"from state {state!r}: {expected_gate['decision']!r} "
            f"{expected_gate['blockingReasons']}",
        )

    add(
        "RC-13",
        "left_draft_before_asserting_reuse",
        state != "draft"
        or (
            recorded_gate.get("decision") == "blocked"
            and "not_yet_published" in (recorded_gate.get("blockingReasons") or [])
        ),
        "record never left draft yet asserts an open record-side reuse gate",
    )

    dissent_pending = lifecycle.has_unadjudicated_qualified_dissent(dissent_entries)
    add(
        "RC-14",
        "qualified_dissent_blocks_reuse",
        not dissent_pending
        or (
            state == "retained_dissent"
            and recorded_gate.get("decision") == "blocked"
            and lifecycle.REASON_RETAINED_DISSENT
            in (recorded_gate.get("blockingReasons") or [])
        ),
        "unadjudicated qualified dissent requires state retained_dissent and a "
        "closed reuse gate",
    )

    return results


def failed_reasons(results: list[CheckResult]) -> tuple[str, ...]:
    return tuple(result.reason for result in results if not result.passed)


def evaluate_variant(name: str, record: Mapping[str, Any]) -> VariantResult:
    """Judge one variant: it must fail the suite for its registered reason."""

    expected = VARIANT_EXPECTATIONS.get(name)
    if expected is None:
        return VariantResult(
            name,
            "<unregistered>",
            (),
            False,
            "variant file has no registered named reason in VARIANT_EXPECTATIONS",
        )
    failed = failed_reasons(reconstructability_checks(record))
    if not failed:
        return VariantResult(
            name, expected, failed, False, "variant PASSED the whole suite"
        )
    if expected not in failed:
        return VariantResult(
            name,
            expected,
            failed,
            False,
            f"expected reason missing; variant failed only for {list(failed)}",
        )
    return VariantResult(name, expected, failed, True)


def discrimination_results(variants_dir: Path) -> tuple[list[VariantResult], list[str]]:
    """Evaluate every ``*.invalid.json`` variant; also report registry gaps."""

    problems: list[str] = []
    rows: list[VariantResult] = []
    found = sorted(variants_dir.glob(f"*{VARIANT_SUFFIX}")) if variants_dir.is_dir() else []
    if not found:
        problems.append(f"no {VARIANT_SUFFIX} variants found in {variants_dir}")
    missing = sorted(set(VARIANT_EXPECTATIONS) - {path.name for path in found})
    problems.extend(f"registered variant missing on disk: {name}" for name in missing)
    for path in found:
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            rows.append(
                VariantResult(path.name, "<unreadable>", (), False, str(exc))
            )
            continue
        rows.append(evaluate_variant(path.name, _mapping(payload)))
    return rows, problems


def _print_section(title: str) -> None:
    print()
    print(title)
    print("-" * 72)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="Read-only validation (default; the suite never writes)",
    )
    parser.add_argument(
        "--record",
        type=Path,
        default=None,
        help="Check one record's reconstructability instead of the shipped "
        "example plus discrimination variants",
    )
    parser.add_argument(
        "--variants-dir",
        type=Path,
        default=VARIANTS_DIR,
        help="Directory of *.invalid.json discrimination variants",
    )
    args = parser.parse_args(argv)

    print("governed-judgment contract conformance suite (C2, chapter-4 section 4.4)")
    print("=" * 72)

    target = args.record if args.record is not None else EXAMPLE
    _print_section(f"RECONSTRUCTABILITY: {target}")
    try:
        payload = json.loads(Path(target).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"[{FAIL}] record unreadable  <- {exc}")
        reconstructable = False
    else:
        checks = reconstructability_checks(_mapping(payload))
        for result in checks:
            line = f"[{PASS if result.passed else FAIL}] {result.check_id} {result.reason}"
            if not result.passed and result.detail:
                line += f"  <- {result.detail}"
            print(line)
        passed_count = sum(1 for result in checks if result.passed)
        reconstructable = passed_count == len(checks)
        print(
            f"reconstructability: {'PASS' if reconstructable else 'FAIL'} "
            f"({passed_count}/{len(checks)} sub-checks)"
        )

    if args.record is not None:
        _print_section("DISCRIMINATION")
        print("skipped: --record checks a single record only")
        discriminating = True
    else:
        _print_section(f"DISCRIMINATION: {args.variants_dir}")
        rows, problems = discrimination_results(args.variants_dir)
        for problem in problems:
            print(f"[{FAIL}] {problem}")
        for row in rows:
            line = f"[{PASS if row.caught else FAIL}] {row.name} -> {row.expected_reason}"
            if row.caught:
                line += f"  (rejected; failed reasons: {list(row.failed_reasons)})"
            elif row.detail:
                line += f"  <- {row.detail}"
            print(line)
        discriminating = not problems and rows != [] and all(row.caught for row in rows)
        print(
            f"discrimination: {'PASS' if discriminating else 'FAIL'} "
            f"({sum(1 for row in rows if row.caught)}/{len(rows)} variants failed "
            "for their named reason)"
        )

    _print_section("COMPLETENESS REVIEW")
    print(
        f"[{COMPLETENESS_STATUS}] independent-implementer completeness review "
        f"(reason: {COMPLETENESS_REASON})"
    )
    print(
        "the specification-completeness arm needs the independent implementer "
        "chapter-4 section 4.7 names; nobody is recruited, so it is reported as "
        "not_run rather than simulated"
    )

    print()
    overall = reconstructable and discriminating
    print(f"GOVERNED CONTRACT CONFORMANCE: {'PASS' if overall else 'FAIL'}")
    return 0 if overall else 1


if __name__ == "__main__":
    sys.exit(main())
