#!/usr/bin/env python3
"""Evaluate the complete VEGO-AI experiment program and publish analytics.

The evaluator intentionally separates engineering evidence from empirical
classification evidence.  Human-gated experiments receive a structured
eligibility verdict; they are never populated with synthetic outcomes.
"""

from __future__ import annotations

import argparse
import hashlib
import html
import importlib.util
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import jsonschema

ROOT = Path(__file__).resolve().parents[1]
CATALOG = (
    ROOT
    / "docs"
    / "research"
    / "bigui"
    / "experiment-catalog-snapshot-v1.json"
)
STANDARD = (
    ROOT
    / "docs"
    / "research"
    / "bigui"
    / "experiment-evaluation-standard-v1.json"
)
SNAPSHOT = (
    ROOT
    / "docs"
    / "research"
    / "bigui"
    / "experiment-benchmark-snapshot-v1.json"
)
REPORT_MD = (
    ROOT
    / "docs"
    / "research"
    / "bigui"
    / "EXPERIMENT_BENCHMARK_ANALYTICS_REPORT.md"
)
REPORT_HTML = ROOT / "VEGO-AI-Experiment-Benchmark-Report.html"
SCHEMAS = ROOT / "schemas"

EMPIRICAL_EXPERIMENTS = {
    "EXP-003",
    "EXP-005",
    "EXP-011",
    "EXP-012",
    *{f"EXP-{index:03d}" for index in range(19, 30)},
}
HUMAN_GATE_EXPERIMENTS = {
    "EXP-005",
    "EXP-019",
    "EXP-020",
    "EXP-021",
    "EXP-022",
    "EXP-024",
    "EXP-025",
    "EXP-026",
    "EXP-029",
    "EXP-031",
    "EXP-032",
}
PARKED_EXPERIMENTS = {"EXP-000", "EXP-011"}
EXACT_ONE_METRICS = {
    "ARCH_SEMANTIC_PARITY_RATE",
    "ARCH_REPLAY_DETERMINISM",
    "ARCH_BASELINE_PRESERVATION",
    "ARCH_OUTPUT_PARITY",
    "SAFETY_FAULT_CASE_PASS_RATE",
    "SAFETY_BASELINE_PRESERVATION",
    "SAFETY_PARK_OR_ESCALATE_ACCURACY",
    "AUTHORITY_SAFE_CASE_RATE",
    "PROPOSAL_DIFF_REPRODUCIBLE",
    "CATALOG_REFERENCE_RESOLUTION",
    "CATALOG_SOURCE_HASH_AGREEMENT",
    "CATALOG_METRIC_REDERIVATION",
}
EXACT_ZERO_TOKENS = (
    "CLASSIFICATION_CHANGES",
    "SEMANTIC_DIFFERENCES",
    "TRUSTED_MEMORY_WRITES",
    "CORRECTION_APPLICATIONS",
    "UNSAFE_",
    "BASELINE_MODIFICATIONS",
    "PROPOSAL_APPLICATIONS",
    "PROPOSAL_SOURCE_HASH_CHANGED",
)
HIGHLIGHT_SPECS: dict[str, dict[str, Any]] = {
    "EXP-001": {
        "summary": "The conservative human-judgment mechanism produced a complete 27-row parallel comparison while preserving every baseline classification.",
        "metrics": [
            ("MECH_COMPARISON_ROWS", {}),
            ("MECH_REVIEW_AFTER_MEMORY", {}),
            ("SAFETY_CLASSIFICATION_CHANGES", {}),
        ],
    },
    "EXP-006": {
        "summary": "The reconstructed lifecycle corpus makes the observation volume and the much smaller review queue explicit.",
        "metrics": [
            ("EVENT_TOTAL_RECONSTRUCTED", {}),
            ("MECH_REVIEW_QUEUE_ITEMS", {}),
            ("MECH_QUEUE_TO_EVENT_COUNT_RATIO", {}),
        ],
    },
    "EXP-007": {
        "summary": "The severity-2 candidate preserves high-severity coverage but retains most of the replay workload, so it is not an approved default.",
        "metrics": [
            ("ROUTING_HIGH_SEVERITY_COVERAGE", {"mode": "threshold_sev2"}),
            ("ROUTING_WEIGHTED_COVERAGE", {"mode": "threshold_sev2"}),
            ("ROUTING_EVENT_LOAD", {"mode": "threshold_sev2"}),
            ("ROUTING_BUNDLING_REDUCTION", {"mode": "threshold_sev2"}),
        ],
    },
    "EXP-009": {
        "summary": "The deterministic H-Verify rules separate conflicts and non-conflicts on a finite synthetic fixture; this is rule coverage, not human-error validation.",
        "metrics": [
            ("HVERIFY_DETECTION_RECALL", {}),
            ("HVERIFY_SPECIFICITY", {}),
            ("HVERIFY_FALSE_POSITIVES", {}),
            ("HVERIFY_FALSE_NEGATIVES", {}),
        ],
    },
    "EXP-013": {
        "summary": "All fixture records satisfy the event contract, reconstructable records retain lineage, and evaluation-only E15 remains parked.",
        "metrics": [
            ("CONTRACT_SCHEMA_VALID_RATE", {}),
            ("CONTRACT_LINEAGE_COMPLETE_RATE", {}),
            ("CONTRACT_E15_PARKED", {}),
        ],
    },
    "EXP-016": {
        "summary": "All authority and timeout fixtures preserve the baseline and create no correction application or trusted-memory write.",
        "metrics": [
            ("AUTHORITY_SAFE_CASE_RATE", {}),
            ("AUTHORITY_TRUSTED_MEMORY_WRITES", {}),
            ("AUTHORITY_CORRECTION_APPLICATIONS", {}),
        ],
    },
    "EXP-033": {
        "summary": "Legacy, unified, and parity paths are semantically equivalent on the controlled fixture, replay deterministically, and preserve classifications.",
        "metrics": [
            ("ARCH_SEMANTIC_PARITY_RATE", {}),
            ("ARCH_REPLAY_DETERMINISM", {}),
            ("ARCH_CLASSIFICATION_CHANGES", {}),
        ],
    },
    "EXP-034": {
        "summary": "The three H-layer topologies produce contract-equivalent traces while exposing different coordination and failure-containment trade-offs.",
        "metrics": [
            ("TOPOLOGY_HANDOFF_COUNT", {"topology": "topology-a"}),
            ("TOPOLOGY_HANDOFF_COUNT", {"topology": "topology-b"}),
            ("TOPOLOGY_HANDOFF_COUNT", {"topology": "topology-c"}),
            ("TOPOLOGY_FAILURE_BREADTH", {"topology": "topology-a"}),
            ("TOPOLOGY_FAILURE_BREADTH", {"topology": "topology-b"}),
            ("TOPOLOGY_FAILURE_BREADTH", {"topology": "topology-c"}),
        ],
    },
    "EXP-035": {
        "summary": "Every malformed, duplicate, missing, late, conflicting, and timed-out fixture resolves through a safe disposition without baseline mutation.",
        "metrics": [
            ("SAFETY_FAULT_CASE_PASS_RATE", {}),
            ("SAFETY_BASELINE_PRESERVATION", {}),
            ("SAFETY_TRUSTED_MEMORY_WRITES", {}),
            ("SAFETY_CORRECTION_APPLICATIONS", {}),
        ],
    },
    "EXP-036": {
        "summary": "The pinned summary records engineeringTargetMet=false for the latest controlled scale run: the unified P95 check fails at larger scale while the parity P95 and unified peak-memory checks pass; run-to-run p95-ratio variability remains visible separately.",
        "metrics": [
            (
                "ARCH_P95_RATIO_TO_LEGACY",
                {"fixture": "SYNTHETIC_1X", "mode": "unified"},
            ),
            (
                "ARCH_P95_RATIO_TO_LEGACY",
                {"fixture": "SYNTHETIC_5X", "mode": "unified"},
            ),
            (
                "ARCH_P95_RATIO_TO_LEGACY",
                {"fixture": "SYNTHETIC_10X", "mode": "unified"},
            ),
            (
                "ARCH_P95_RATIO_TO_LEGACY",
                {"fixture": "SYNTHETIC_10X", "mode": "parity"},
            ),
        ],
    },
    "EXP-037": {
        "summary": "The paper and current repository can be aligned on corpus and architecture counts, but not on independent classification performance.",
        "metrics": [
            ("PAPER_CASE_MODEL_COUNT", {}),
            ("CURRENT_CASE_MODEL_COUNT", {}),
            ("PAPER_PATTERN_COUNT", {}),
            ("CURRENT_PATTERN_COUNT", {}),
            ("PAPER_CURRENT_CLASSIFICATION_COMPARISON_ELIGIBLE", {}),
        ],
    },
    "EXP-040": {
        "summary": "The thesis traceability audit separates supported mechanism claims from empirical improvement claims that remain unopened.",
        "metrics": [
            ("THESIS_SAFE_CURRENT_CLAIMS", {}),
            ("THESIS_EMPIRICAL_IMPROVEMENT_CLAIMS_READY", {}),
            ("THESIS_HYPOTHESES_CONFIRMED", {}),
            ("THESIS_TRACEABILITY_RECORDS", {}),
        ],
    },
}


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path.relative_to(ROOT)} must contain a JSON object")
    return value


def load_catalog_builder() -> Any:
    path = ROOT / "scripts" / "build_bigui_catalog.py"
    spec = importlib.util.spec_from_file_location("build_bigui_catalog", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load the BigUI catalog builder")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_sha256(value: Any) -> str:
    payload = json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def dimension_result(
    status: str,
    explanation: str,
    numerator: int | float | None = None,
    denominator: int | float | None = None,
) -> dict[str, Any]:
    value = (
        numerator / denominator
        if numerator is not None and denominator not in (None, 0)
        else None
    )
    passed: bool | None
    if status == "pass":
        passed = True
    elif status == "fail":
        passed = False
    else:
        passed = None
    return {
        "status": status,
        "passed": passed,
        "numerator": numerator,
        "denominator": denominator,
        "value": value,
        "explanation": explanation,
    }


def target_for(observation: dict[str, Any]) -> tuple[str | None, str]:
    metric_id = observation["metricId"]
    value = observation["value"]
    dimensions = observation.get("dimensions", {})
    if value is None:
        return None, "not_computable"
    if metric_id in EXACT_ONE_METRICS:
        return "= 1.0", "met" if float(value) == 1.0 else "missed"
    if any(token in metric_id for token in EXACT_ZERO_TOKENS):
        return "= 0", "met" if float(value) == 0.0 else "missed"
    if metric_id == "ROUTING_HIGH_SEVERITY_COVERAGE":
        return "= 1.0", "met" if float(value) == 1.0 else "missed"
    if metric_id == "ROUTING_WEIGHTED_COVERAGE":
        return ">= 0.8", "met" if float(value) >= 0.8 else "missed"
    if metric_id == "ROUTING_EVENT_LOAD":
        return "<= 0.5", "met" if float(value) <= 0.5 else "missed"
    if metric_id == "ARCH_MEMORY_RATIO_TO_LEGACY":
        return "<= 1.5", "met" if float(value) <= 1.5 else "missed"
    if metric_id == "ARCH_P95_RATIO_TO_LEGACY":
        mode = dimensions.get("mode")
        limit = 2.25 if mode == "parity" else 1.15
        return f"<= {limit}", "met" if float(value) <= limit else "missed"
    return None, "descriptive"


def protocol_dimension(experiment: dict[str, Any]) -> dict[str, Any]:
    checks = [
        bool(experiment["researchQuestion"].strip()),
        bool(experiment["baseline"].strip()),
        bool(experiment["comparator"].strip()),
        bool(experiment["metricDefinitions"]),
        experiment["approvalGates"] is not None
        and experiment["prerequisites"] is not None,
        bool(experiment["validityThreats"])
        and bool(experiment["claimBoundary"].strip()),
        bool(experiment["artifactLinks"]),
    ]
    passed = sum(checks)
    return dimension_result(
        "pass" if passed == len(checks) else "partial",
        f"{passed}/{len(checks)} protocol elements are explicit.",
        passed,
        len(checks),
    )


def data_dimension(observations: list[dict[str, Any]]) -> dict[str, Any]:
    if not observations:
        return dimension_result(
            "not_measured",
            "No accepted observation exists; data quality remains a protocol requirement.",
        )
    checks = [
        all(bool(item.get("sourceSha256")) for item in observations),
        all(bool(item.get("cohortHash")) for item in observations),
        all(item.get("denominator") is not None for item in observations),
        all(item.get("missingCount") is not None for item in observations),
        all(
            not (
                item.get("evidenceClass") in {"synthetic", "same_pattern"}
                and item["metricId"].startswith(("CLASSIFICATION_", "PAIRED_"))
                and item.get("value") is not None
            )
            for item in observations
        ),
    ]
    passed = sum(checks)
    status = "pass" if passed == len(checks) else (
        "partial" if passed else "fail"
    )
    return dimension_result(
        status,
        f"{passed}/{len(checks)} source, cohort, denominator, missingness, and leakage checks pass across {len(observations)} observations.",
        passed,
        len(checks),
    )


def execution_dimension(bundles: list[dict[str, Any]]) -> dict[str, Any]:
    if not bundles:
        return dimension_result(
            "not_measured",
            "No accepted run exists; this is not an executed result.",
        )
    checks: list[bool] = []
    for bundle in bundles:
        envelope = bundle["envelope"]
        checks.extend(
            [
                envelope["executionStatus"] == "succeeded",
                envelope["acceptanceStatus"] == "accepted",
                bool(envelope["evaluation"]["executionValid"]),
                bundle["acceptance"]["status"] == "accepted"
                and bool(bundle["acceptance"]["criteriaOutcomes"]),
            ]
        )
    passed = sum(checks)
    return dimension_result(
        "pass" if passed == len(checks) else "fail",
        f"{passed}/{len(checks)} accepted-run execution checks pass across {len(bundles)} run bundles.",
        passed,
        len(checks),
    )


def reproducibility_dimension(
    bundles: list[dict[str, Any]],
) -> dict[str, Any]:
    if not bundles:
        return dimension_result(
            "not_measured",
            "No accepted run exists; replay and provenance have not been measured.",
        )
    checks: list[bool] = []
    deterministic_required = False
    deterministic_values: list[bool] = []
    for bundle in bundles:
        envelope = bundle["envelope"]
        evaluation = envelope["evaluation"]
        checks.extend(
            [
                len(envelope["sourceRevision"]) == 40,
                len(envelope["manifestSha256"]) == 64,
                all(
                    len(item["metricDefinitionSha256"]) == 64
                    and len(item["cohortHash"]) == 64
                    for item in bundle["metricObservations"]
                ),
            ]
        )
        if evaluation["deterministic"] is not None:
            deterministic_required = True
            deterministic_values.append(bool(evaluation["deterministic"]))
    if deterministic_required:
        checks.append(all(deterministic_values))
    passed = sum(checks)
    status = "pass" if passed == len(checks) else "partial"
    return dimension_result(
        status,
        f"{passed}/{len(checks)} manifest, source, cohort, metric-version, and required determinism checks pass.",
        passed,
        len(checks),
    )


def safety_dimension(
    observations: list[dict[str, Any]],
) -> dict[str, Any]:
    safety_observations: list[dict[str, Any]] = []
    for item in observations:
        metric_id = item["metricId"]
        target, status = target_for(item)
        if (
            metric_id.startswith(("SAFETY_", "AUTHORITY_", "PROPOSAL_"))
            or "BASELINE" in metric_id
            or "CLASSIFICATION_CHANGES" in metric_id
            or "SEMANTIC_DIFFERENCES" in metric_id
        ) and target is not None:
            safety_observations.append({**item, "_targetStatus": status})
    if not safety_observations:
        return dimension_result(
            "not_applicable",
            "This experiment does not declare a direct safety or baseline-integrity measure.",
        )
    passed = sum(
        item["_targetStatus"] == "met" for item in safety_observations
    )
    status = "pass" if passed == len(safety_observations) else "fail"
    return dimension_result(
        status,
        f"{passed}/{len(safety_observations)} exact safety and baseline guardrails pass.",
        passed,
        len(safety_observations),
    )


def comparability_dimension(
    experiment: dict[str, Any],
    bundles: list[dict[str, Any]],
) -> dict[str, Any]:
    declared = bool(experiment["baseline"].strip()) and bool(
        experiment["comparator"].strip()
    )
    if not bundles:
        return dimension_result(
            "partial" if declared else "fail",
            "A baseline and comparator are declared, but no accepted run pair exists."
            if declared
            else "The comparison contract is incomplete.",
            1 if declared else 0,
            2,
        )
    context_fields = [
        "baselineRevision",
        "policyVersion",
        "promptVersion",
        "modelIdentifier",
        "metricSchemaVersion",
        "labelEligibility",
        "leakageClass",
        "evidenceClass",
    ]
    contexts_complete = all(
        all(
            bundle["envelope"]["comparisonContext"].get(field) is not None
            for field in context_fields
        )
        for bundle in bundles
    )
    checks = [declared, contexts_complete]
    passed = sum(checks)
    return dimension_result(
        "pass" if passed == len(checks) else "partial",
        f"{passed}/{len(checks)} baseline/comparator and invariant-context checks pass. Direct deltas still require a declared treatment pair.",
        passed,
        len(checks),
    )


def empirical_dimension(
    experiment_id: str, safe_n: int
) -> dict[str, Any]:
    if experiment_id not in EMPIRICAL_EXPERIMENTS:
        return dimension_result(
            "not_applicable",
            "Classification validity is not the estimand of this experiment.",
        )
    if safe_n == 0:
        return dimension_result(
            "not_eligible",
            "Independent generalization-safe N=0; all empirical classification fields must remain null.",
            0,
            20,
        )
    if safe_n < 20:
        return dimension_result(
            "partial",
            f"Independent safe N={safe_n}; pilot-only descriptive reporting is permitted.",
            safe_n,
            20,
        )
    return dimension_result(
        "pass",
        f"Independent safe N={safe_n}; limited MSc quantitative reporting is eligible, but a positive result still requires the preregistered paired rules.",
        min(safe_n, 20),
        20,
    )


def eligibility_for(experiment: dict[str, Any]) -> str:
    experiment_id = experiment["id"]
    if experiment_id in PARKED_EXPERIMENTS:
        return "parked"
    if experiment_id in HUMAN_GATE_EXPERIMENTS:
        return "human_gate_required"
    if experiment["approvalGates"]:
        return "approval_gate_required"
    if experiment["prerequisites"] and not experiment["acceptedRunIds"]:
        return "dependency_gate_required"
    return "eligible_now"


def signal_rows(
    observations: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    prioritized = sorted(
        observations,
        key=lambda item: (
            0 if target_for(item)[0] is not None else 1,
            0 if target_for(item)[1] == "missed" else 1,
            item["metricId"],
            json.dumps(item.get("dimensions", {}), sort_keys=True),
        ),
    )
    rows: list[dict[str, Any]] = []
    seen: set[tuple[str, str]] = set()
    for item in prioritized:
        dimensions = json.dumps(item.get("dimensions", {}), sort_keys=True)
        key = (item["metricId"], dimensions)
        if key in seen:
            continue
        seen.add(key)
        target, status = target_for(item)
        rows.append(
            {
                "metricId": item["metricId"],
                "value": item["value"],
                "unit": item["unit"],
                "denominator": item["denominator"],
                "dimensions": item.get("dimensions", {}),
                "target": target,
                "status": status,
            }
        )
        if len(rows) == 8:
            break
    return rows


def result_highlights(
    experiments: list[dict[str, Any]],
    latest_bundles: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    experiment_index = {item["id"]: item for item in experiments}
    highlights: list[dict[str, Any]] = []
    for experiment_id, spec in HIGHLIGHT_SPECS.items():
        bundle = latest_bundles.get(experiment_id)
        if bundle is None:
            raise ValueError(
                f"result highlight requires an accepted run: {experiment_id}"
            )
        observations = bundle["metricObservations"]
        selected: list[dict[str, Any]] = []
        for metric_id, expected_dimensions in spec["metrics"]:
            matches = [
                item
                for item in observations
                if item["metricId"] == metric_id
                and all(
                    item.get("dimensions", {}).get(key) == value
                    for key, value in expected_dimensions.items()
                )
            ]
            if len(matches) != 1:
                raise ValueError(
                    f"{experiment_id} highlight expected exactly one "
                    f"{metric_id} {expected_dimensions}, found {len(matches)}"
                )
            observation = matches[0]
            selected.append(
                {
                    "metricId": observation["metricId"],
                    "value": observation["value"],
                    "denominator": observation["denominator"],
                    "unit": observation["unit"],
                    "dimensions": observation.get("dimensions", {}),
                    "sourcePath": observation["sourcePath"],
                    "sourceSha256": observation["sourceSha256"],
                    "observationDate": observation["observationDate"],
                    "claimBoundary": observation["claimBoundary"],
                }
            )
        experiment = experiment_index[experiment_id]
        highlights.append(
            {
                "experimentId": experiment_id,
                "title": experiment["title"],
                "summary": spec["summary"],
                "evidenceClass": bundle["envelope"]["evidenceClass"],
                "metrics": selected,
                "claimBoundary": experiment["claimBoundary"],
            }
        )
    return highlights


def build_snapshot() -> dict[str, Any]:
    catalog_builder = load_catalog_builder()
    catalog = catalog_builder.build_catalog(validate_benchmark=False)
    standard = load_json(STANDARD)
    jsonschema.Draft202012Validator(
        load_json(
            SCHEMAS / "experiment-evaluation-standard-v1.schema.json"
        ),
        format_checker=jsonschema.FormatChecker(),
    ).validate(standard)

    core_projection = {
        key: catalog[key]
        for key in (
            "programState",
            "experiments",
            "metricDefinitionsV2",
            "metricObservationsV2",
            "comparisonRules",
            "acceptedRunBundles",
            "currentRunIndex",
            "paperBaseline",
            "baselineComparisonResults",
        )
    }
    observations_by_experiment: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for observation in catalog["metricObservationsV2"]:
        observations_by_experiment[observation["experimentId"]].append(
            observation
        )
    bundles_by_experiment: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for bundle in catalog["acceptedRunBundles"]:
        bundles_by_experiment[bundle["envelope"]["experimentId"]].append(
            bundle
        )
    bundle_index = {
        (
            bundle["envelope"]["experimentId"],
            bundle["envelope"]["runId"],
        ): bundle
        for bundle in catalog["acceptedRunBundles"]
    }
    latest_bundle_by_experiment = {}
    for current_run in catalog["currentRunIndex"]["currentRuns"]:
        key = (current_run["experimentId"], current_run["runId"])
        bundle = bundle_index.get(key)
        if bundle is None:
            raise ValueError(
                "current run index points to a missing bundle: "
                f"{current_run['experimentId']} {current_run['runId']}"
            )
        latest_bundle_by_experiment[current_run["experimentId"]] = bundle

    safe_n = catalog["programState"]["safeLabels"]
    records: list[dict[str, Any]] = []
    coverage_rows: list[dict[str, Any]] = []
    for experiment in catalog["experiments"]:
        experiment_id = experiment["id"]
        historical_observations = observations_by_experiment[experiment_id]
        bundles = bundles_by_experiment[experiment_id]
        latest_bundle = latest_bundle_by_experiment.get(experiment_id)
        observations = (
            latest_bundle["metricObservations"] if latest_bundle else []
        )
        declared_ids = set(experiment["metricDefinitions"])
        observed_ids = {item["metricId"] for item in observations}
        observed_declared_ids = observed_ids & declared_ids
        metric_contract_incomplete = bool(bundles) and not declared_ids.issubset(
            observed_ids
        )
        eligibility = eligibility_for(experiment)
        if bundles:
            execution_state = "executed"
        elif eligibility == "parked":
            execution_state = "parked"
        else:
            execution_state = "not_executed"
        dimensions = {
            "protocol": protocol_dimension(experiment),
            "data": data_dimension(observations),
            "execution": execution_dimension(bundles),
            "reproducibility": reproducibility_dimension(bundles),
            "safety": safety_dimension(observations),
            "comparability": comparability_dimension(experiment, bundles),
            "empiricalValidity": empirical_dimension(experiment_id, safe_n),
        }
        if bundles:
            execution_failed = dimensions["execution"]["status"] == "fail"
            safety_failed = dimensions["safety"]["status"] == "fail"
            target_missed = any(
                target_for(item)[1] == "missed" for item in observations
            )
            null_blocked = any(
                item["metricId"].startswith(("CLASSIFICATION_", "PAIRED_"))
                and item["value"] is None
                for item in observations
            )
            if execution_failed or safety_failed:
                verdict = "MEASURED_FAIL"
            elif target_missed or null_blocked or metric_contract_incomplete:
                verdict = "MEASURED_PARTIAL"
            else:
                verdict = "MEASURED_PASS"
        elif eligibility == "parked":
            verdict = "PARKED_NO_RUN"
        elif eligibility == "eligible_now":
            verdict = "PROTOCOL_READY"
        else:
            verdict = "GATED_NOT_RUN"
        empirical_status = (
            "NOT_COMPUTABLE"
            if safe_n == 0
            else ("PILOT_ONLY" if safe_n < 20 else "ELIGIBLE")
        )
        record = {
            "experimentId": experiment_id,
            "title": experiment["title"],
            "status": experiment["status"],
            "evidenceClass": experiment["evidenceClass"],
            "executionState": execution_state,
            "eligibility": eligibility,
            "verdict": verdict,
            "acceptedRunCount": len(bundles),
            "observationCount": len(observations),
            "historicalObservationCount": len(historical_observations),
            "nullObservationCount": sum(
                item["value"] is None for item in observations
            ),
            "baseline": experiment["baseline"],
            "comparator": experiment["comparator"],
            "dimensions": dimensions,
            "engineeringSignals": signal_rows(observations),
            "empiricalMetrics": {
                "safeN": safe_n,
                "accuracy": None,
                "macroF1": None,
                "netCorrection": None,
                "mcnemarP": None,
                "status": empirical_status,
            },
            "claimBoundary": experiment["claimBoundary"],
            "nextAction": experiment["nextAction"],
        }
        records.append(record)
        declared = len(declared_ids)
        observed = len(observed_declared_ids)
        coverage_rows.append(
            {
                "experimentId": experiment_id,
                "declared": declared,
                "observed": observed,
                "coverage": (
                    observed / declared if declared else None
                ),
                "status": (
                    "measured"
                    if observations
                    else (
                        "protocol_only"
                        if declared
                        else "no_metrics_declared"
                    )
                ),
            }
        )

    executed_records = [
        item for item in records if item["executionState"] == "executed"
    ]
    not_eligible_records = [
        item
        for item in records
        if item["eligibility"]
        in {
            "human_gate_required",
            "approval_gate_required",
            "dependency_gate_required",
        }
        and item["executionState"] != "executed"
    ]
    engineering_records = [
        item
        for item in records
        if item["engineeringSignals"]
        and item["executionState"] == "executed"
    ]
    target_statuses: list[tuple[str, str]] = []
    for experiment_id, bundle in latest_bundle_by_experiment.items():
        for observation in bundle["metricObservations"]:
            target, status = target_for(observation)
            if target is not None or status == "not_computable":
                target_statuses.append((experiment_id, status))
    historical_target_statuses: list[tuple[str, str]] = []
    for experiment_id, observations in observations_by_experiment.items():
        for observation in observations:
            target, status = target_for(observation)
            if target is not None or status == "not_computable":
                historical_target_statuses.append((experiment_id, status))
    missed_experiments = {
        experiment_id
        for experiment_id, status in target_statuses
        if status == "missed"
    }
    snapshot = {
        "schemaVersion": "ExperimentBenchmarkSnapshot-v1",
        "generatedAt": max(catalog["generatedAt"], standard["generatedAt"]),
        "publicationTier": "tracked_sanitized",
        "inputProjectionSha256": canonical_sha256(core_projection),
        "standardSha256": sha256(STANDARD),
        "programState": {
            "registeredExperiments": len(records),
            "acceptedBundles": len(catalog["acceptedRunBundles"]),
            "metricObservations": len(catalog["metricObservationsV2"]),
            "safeLabels": safe_n,
            "classificationChanges": catalog["programState"][
                "classificationChanges"
            ],
            "baselineFrozen": catalog["programState"]["baselineFrozen"],
        },
        "summary": {
            "evaluatedExperiments": len(records),
            "executedExperiments": len(executed_records),
            "protocolOnlyExperiments": len(records) - len(executed_records),
            "notEligibleExperiments": len(not_eligible_records),
            "experimentsWithMeasuredEngineeringEvidence": len(
                engineering_records
            ),
            "experimentsWithEmpiricalClassificationEvidence": sum(
                item["dimensions"]["empiricalValidity"]["status"] == "pass"
                for item in records
            ),
            "protocolPassCount": sum(
                item["dimensions"]["protocol"]["status"] == "pass"
                for item in records
            ),
            "executionPassCount": sum(
                item["dimensions"]["execution"]["status"] == "pass"
                for item in records
            ),
            "safetyPassCount": sum(
                item["dimensions"]["safety"]["status"] == "pass"
                for item in records
            ),
            "comparabilityDefinedCount": sum(
                item["dimensions"]["comparability"]["status"] == "pass"
                for item in records
            ),
        },
        "parameterDictionary": [
            {
                "id": "BASELINE_ID",
                "title": "Baseline identity",
                "definition": "Frozen reference against which a treatment is interpreted.",
                "allowedValues": ["B0", "B1", "B2", "B3", "B4", "B5"],
                "whyItMatters": "A delta is meaningless when its reference changes.",
            },
            {
                "id": "COMPARATOR_ID",
                "title": "Comparator identity",
                "definition": "Declared treatment or alternative architecture/configuration.",
                "allowedValues": ["legacy", "unified", "parity", "topology-a", "topology-b", "topology-c", "policy", "interface"],
                "whyItMatters": "Only the declared treatment may differ in a direct comparison.",
            },
            {
                "id": "COHORT_HASH",
                "title": "Cohort hash",
                "definition": "Stable hash of the unit-of-analysis cohort.",
                "allowedValues": ["64-character SHA-256"],
                "whyItMatters": "It prevents silent comparison of different cases or participants.",
            },
            {
                "id": "PARTITION_HASH",
                "title": "Partition hash",
                "definition": "Stable hash of development, holdout, or external assignment.",
                "allowedValues": ["null before partitioning", "64-character SHA-256 after freeze"],
                "whyItMatters": "It protects the sealed-holdout boundary.",
            },
            {
                "id": "MODEL_IDENTIFIER",
                "title": "Model identifier",
                "definition": "Requested and returned model identity or frozen snapshot.",
                "allowedValues": ["gpt-4o baseline", "future dated snapshot after gate"],
                "whyItMatters": "Model drift can invalidate a performance comparison.",
            },
            {
                "id": "POLICY_VERSION",
                "title": "Policy version",
                "definition": "Frozen routing or comparison policy used by the run.",
                "allowedValues": ["none", "declared semantic version or source hash"],
                "whyItMatters": "Policy changes cannot be mixed with evaluation changes.",
            },
            {
                "id": "PROMPT_VERSION",
                "title": "Prompt version",
                "definition": "Frozen prompt identity used by an AI-dependent run.",
                "allowedValues": ["none", "source hash"],
                "whyItMatters": "Prompt drift changes the treatment.",
            },
            {
                "id": "EVIDENCE_CLASS",
                "title": "Evidence class",
                "definition": "Origin and admissibility level of the observation.",
                "allowedValues": ["historical", "mechanism", "offline", "synthetic", "evaluation_ready", "pilot", "empirical", "proposal", "blocked"],
                "whyItMatters": "Synthetic and empirical values cannot share a headline series.",
            },
            {
                "id": "LEAKAGE_CLASS",
                "title": "Leakage class",
                "definition": "Relationship between prior memory evidence and the evaluation case.",
                "allowedValues": ["none", "same_pattern", "cross_setting", "unknown"],
                "whyItMatters": "Same-pattern and unknown records cannot support generalization.",
            },
            {
                "id": "METRIC_SCHEMA_VERSION",
                "title": "Metric schema version",
                "definition": "Versioned calculation, unit, grain, and exclusions.",
                "allowedValues": ["2.0"],
                "whyItMatters": "Same metric names with different formulas are not comparable.",
            },
            {
                "id": "SAFE_LABEL_N",
                "title": "Generalization-safe label count",
                "definition": "Count of independently reviewed, adjudicated, leakage-safe labels.",
                "allowedValues": ["0", "1–19 pilot", "20+ limited MSc", "30–50 stronger replication"],
                "whyItMatters": "It controls whether empirical performance fields may be populated.",
            },
            {
                "id": "REPETITIONS",
                "title": "Deterministic repetitions",
                "definition": "Number of repeated executions over identical immutable inputs.",
                "allowedValues": ["1 descriptive", "3 conformance minimum"],
                "whyItMatters": "One successful run does not establish replay determinism.",
            },
        ],
        "evaluationRecords": records,
        "resultHighlights": result_highlights(
            catalog["experiments"], latest_bundle_by_experiment
        ),
        "metricCoverage": coverage_rows,
        "guardrailSummary": {
            "assessedObservations": len(target_statuses),
            "met": sum(status == "met" for _, status in target_statuses),
            "missed": sum(status == "missed" for _, status in target_statuses),
            "notComputable": sum(
                status == "not_computable" for _, status in target_statuses
            ),
            "experimentsWithMissedGuardrails": len(missed_experiments),
            "historicalAssessedObservations": len(
                historical_target_statuses
            ),
            "historicalMissed": sum(
                status == "missed"
                for _, status in historical_target_statuses
            ),
        },
        "evidenceDistribution": dict(
            sorted(Counter(item["evidenceClass"] for item in records).items())
        ),
        "comparisonFamilies": [
            {
                "family": "paper_to_current_capability",
                "status": "demonstrated",
                "experiments": ["EXP-037", "EXP-038"],
                "interpretation": "The H-layer adds traceable human-judgment capabilities and preserves baseline behavior; this is not a classification-accuracy comparison.",
            },
            {
                "family": "routing_tradeoff",
                "status": "demonstrated",
                "experiments": ["EXP-006", "EXP-007", "EXP-008"],
                "interpretation": "Coverage, load, bundling, and caps can be compared on the shared offline replay; the Pareto boundary is reported without declaring a default.",
            },
            {
                "family": "runtime_architecture",
                "status": "demonstrated",
                "experiments": ["EXP-033", "EXP-035", "EXP-036"],
                "interpretation": "Legacy, unified, and parity modes have mechanism, fault, determinism, and overhead evidence on equivalent fixtures.",
            },
            {
                "family": "topology",
                "status": "partially_measured",
                "experiments": ["EXP-034"],
                "interpretation": "Offline structural trade-offs are measured; live LLM coordination and production authorization are not.",
            },
            {
                "family": "classification_validity",
                "status": "not_computable",
                "experiments": ["EXP-003", "EXP-005", "EXP-012", "EXP-019", "EXP-020", "EXP-021", "EXP-023", "EXP-024"],
                "interpretation": "Independent generalization-safe N=0; no experiment may claim better accuracy, macro-F1, net correction, or generalization.",
            },
            {
                "family": "human_value",
                "status": "not_computable",
                "experiments": ["EXP-026", "EXP-031", "EXP-032"],
                "interpretation": "Usability, decision-support, and effort protocols exist but require consented human observations.",
            },
        ],
        "findings": [
            f"{len(executed_records)} of {len(records)} experiments have accepted source-backed runs; the remaining records are explicit protocols, gated studies, or parked history.",
            f"{len(engineering_records)} experiments expose measured engineering signals, while zero experiments contain eligible independent classification-performance evidence.",
            "Architecture progress is demonstrated through capability extension, semantic parity, deterministic replay, fail-closed safety, provenance, and reproducible run records.",
            (
                "The pinned EXP-036 summary reports engineeringTargetMet=false: the unified P95 latency-ratio check fails at larger scale even though parity P95 and unified peak-memory both pass; the ratio varies run to run on the same machine, so a single favorable observation is not treated as a pass."
            ),
            "The paper and current repository are directly comparable for architecture and versioned counts only; the paper's qualitative Phase D is not independent ground truth.",
        ],
        "recommendations": [
            "Use the per-dimension scorecard as the program baseline and never collapse protocol, safety, latency, and empirical validity into one value score.",
            "Keep EXP-007 routing configurations on a workload-versus-coverage Pareto chart; do not name a default until M-03 and adjudicated routing targets exist.",
            "Repeat EXP-036 on a second controlled machine and fix the unified-P95 interval computation before claiming a target pass at scale; preserve exact parity, determinism, and baseline hashes.",
            "Approve and execute EXP-019/020 to obtain two independent reviews for all 24 safe candidates; only then populate classification metrics.",
            "Run EXP-031 after the UI is frozen, then preregister EXP-032 before making a BigUI decision-value claim.",
            "Refresh this benchmark atomically whenever an accepted run is added; rejected or stale runs must preserve the last accepted snapshot.",
        ],
        "claimBoundary": "The benchmark demonstrates mechanism, architecture, safety, observability, routing, provenance, and reproducibility results. It does not demonstrate improved classification accuracy, generalization, benchmark superiority, or human-effort reduction.",
        "sources": [
            {
                "path": STANDARD.relative_to(ROOT).as_posix(),
                "sha256": sha256(STANDARD),
                "role": "Canonical criteria, parameter, baseline, gate, and statistical contract.",
            },
            {
                "path": "experiments/registry.md",
                "sha256": sha256(ROOT / "experiments" / "registry.md"),
                "role": "Complete experiment identity and status registry.",
            },
            {
                "path": "experiments/bigui-program-v1.json",
                "sha256": sha256(ROOT / "experiments" / "bigui-program-v1.json"),
                "role": "BigUI experiment protocols and claim boundaries.",
            },
            {
                "path": "docs/research/bigui/paper-baseline-snapshot-v1.json",
                "sha256": sha256(
                    ROOT
                    / "docs"
                    / "research"
                    / "bigui"
                    / "paper-baseline-snapshot-v1.json"
                ),
                "role": "Reviewed paper baseline extraction.",
            },
            {
                "path": "docs/research/bigui/baseline-comparison-results-v1.json",
                "sha256": sha256(
                    ROOT
                    / "docs"
                    / "research"
                    / "bigui"
                    / "baseline-comparison-results-v1.json"
                ),
                "role": "Paper, architecture, comparison, and thesis-readiness results.",
            },
        ],
    }
    validate_snapshot(snapshot)
    return snapshot


def validate_snapshot(snapshot: dict[str, Any]) -> None:
    jsonschema.Draft202012Validator(
        load_json(SCHEMAS / "experiment-benchmark-snapshot-v1.schema.json"),
        format_checker=jsonschema.FormatChecker(),
    ).validate(snapshot)
    ids = [item["experimentId"] for item in snapshot["evaluationRecords"]]
    expected = [f"EXP-{index:03d}" for index in range(41)]
    if ids != expected:
        raise ValueError("benchmark must evaluate EXP-000 through EXP-040 in order")
    if snapshot["programState"]["safeLabels"] == 0:
        for record in snapshot["evaluationRecords"]:
            empirical = record["empiricalMetrics"]
            if any(
                empirical[key] is not None
                for key in ("accuracy", "macroF1", "netCorrection", "mcnemarP")
            ):
                raise ValueError(
                    f"{record['experimentId']} contains empirical values at safe N=0"
                )
    highlight_ids = [
        item["experimentId"] for item in snapshot["resultHighlights"]
    ]
    if len(highlight_ids) != len(set(highlight_ids)):
        raise ValueError("result highlight experiment IDs must be unique")
    record_ids = {
        item["experimentId"] for item in snapshot["evaluationRecords"]
    }
    for highlight in snapshot["resultHighlights"]:
        if highlight["experimentId"] not in record_ids:
            raise ValueError(
                f"dangling result highlight: {highlight['experimentId']}"
            )
        for metric in highlight["metrics"]:
            if metric["denominator"] is None:
                raise ValueError(
                    f"{highlight['experimentId']} highlight "
                    f"{metric['metricId']} has no denominator"
                )
    for source in snapshot["sources"]:
        path = ROOT / source["path"]
        if not path.is_file() or sha256(path) != source["sha256"]:
            raise ValueError(f"benchmark source hash mismatch: {source['path']}")


def format_value(value: Any) -> str:
    if value is None:
        return "—"
    if isinstance(value, float):
        return f"{value:.3f}"
    return str(value)


def format_dimensions(dimensions: dict[str, Any]) -> str:
    if not dimensions:
        return "aggregate"
    return ", ".join(
        f"{key}={value}" for key, value in sorted(dimensions.items())
    )


def format_highlight_metric(metric: dict[str, Any]) -> str:
    return (
        f"`{metric['metricId']}` = {format_value(metric['value'])} "
        f"{metric['unit']} (N={format_value(metric['denominator'])}; "
        f"{format_dimensions(metric['dimensions'])})"
    )


def render_markdown(snapshot: dict[str, Any]) -> str:
    summary = snapshot["summary"]
    lines = [
        "# VEGO-AI Experiment Benchmark Analytics Report",
        "",
        f"Generated: `{snapshot['generatedAt']}`",
        f"Input projection: `{snapshot['inputProjectionSha256']}`",
        "",
        "## Technical summary",
        "",
        (
            f"The benchmark evaluated all {summary['evaluatedExperiments']} "
            f"registered experiments. {summary['executedExperiments']} have "
            "accepted source-backed runs; the remainder are protocols, gated "
            "studies, or parked history. Engineering progress is measured "
            "separately from empirical classification validity."
        ),
        "",
        (
            "**Empirical boundary:** independent generalization-safe N=0. "
            "Accuracy, macro-F1, net correction, paired significance, "
            "generalization, and human-effort improvement remain not computable."
        ),
        "",
        "## Key findings",
        "",
    ]
    lines.extend(f"- {item}" for item in snapshot["findings"])
    lines.extend(
        [
            "",
            "## Measured result highlights",
            "",
            "These are selected latest-run observations. Every value retains its denominator, source, observation date, evidence class, and claim boundary; accepted-run history is analyzed separately.",
            "",
        ]
    )
    for highlight in snapshot["resultHighlights"]:
        lines.extend(
            [
                f"### {highlight['experimentId']} — {highlight['title']}",
                "",
                highlight["summary"],
                "",
            ]
        )
        lines.extend(
            f"- {format_highlight_metric(metric)}  "
            f"Source: `{metric['sourcePath']}` "
            f"(`{metric['sourceSha256'][:12]}…`, "
            f"{metric['observationDate']})."
            for metric in highlight["metrics"]
        )
        lines.extend(
            [
                "",
                f"Evidence class: `{highlight['evidenceClass']}`. "
                f"Claim boundary: {highlight['claimBoundary']}",
                "",
            ]
        )
    lines.extend(
        [
            "## Scope, data, and metric definitions",
            "",
            "The benchmark covers the tracked sanitized tier. Raw reviewer sheets, labels, transcripts, and controlled evidence remain local. Every accepted observation is evaluated for source hash, cohort hash, denominator, missingness, evidence class, and claim boundary.",
            "",
            "No global weighted value score is calculated. The program reports seven independent dimensions: protocol, data, execution, reproducibility, safety, comparability, and empirical validity.",
            "",
            "### Baseline ladder",
            "",
            "| Baseline | Purpose | Current state |",
            "| --- | --- | --- |",
        ]
    )
    standard = load_json(STANDARD)
    for item in standard["baselineLadder"]:
        lines.append(
            f"| {item['id']} — {item['title']} | {item['purpose']} | {item['currentState']} |"
        )
    lines.extend(
        [
            "",
            "## Methodology",
            "",
            "Each experiment is assessed against its declared question, baseline, comparator, metrics, gates, source-backed accepted runs, metric observations, and claim boundary. Non-executed human studies receive a formal eligibility verdict rather than fabricated results. Direct deltas are allowed only when cohort, partition, baseline, policy, prompt, model, metric definition, leakage class, and evidence class are equivalent except for the declared treatment.",
            "",
            "## All-experiment evaluation",
            "",
            "| Experiment | Execution | Verdict | Protocol | Data | Reproducibility | Safety | Comparability | Empirical validity | Observations |",
            "| --- | --- | --- | --- | --- | --- | --- | --- | --- | ---: |",
        ]
    )
    for record in snapshot["evaluationRecords"]:
        dimensions = record["dimensions"]
        lines.append(
            "| "
            + " | ".join(
                [
                    f"{record['experimentId']} — {record['title']}",
                    record["executionState"],
                    record["verdict"],
                    dimensions["protocol"]["status"],
                    dimensions["data"]["status"],
                    dimensions["reproducibility"]["status"],
                    dimensions["safety"]["status"],
                    dimensions["comparability"]["status"],
                    dimensions["empiricalValidity"]["status"],
                    str(record["observationCount"]),
                ]
            )
            + " |"
        )
    lines.extend(
        [
            "",
            "## Limitations and robustness",
            "",
            "- The paper comparison supports version and architecture alignment, not a paired accuracy result.",
            "- Offline and synthetic fixtures do not establish external validity or population-level human benefit.",
            "- Machine-specific latency values support local engineering decisions only.",
            "- Protocol completeness does not substitute for execution.",
            "- Safe N=0 forces all empirical classification fields to remain null.",
            "",
            "## Recommended next steps",
            "",
        ]
    )
    lines.extend(
        f"{index}. {item}"
        for index, item in enumerate(snapshot["recommendations"], 1)
    )
    lines.extend(
        [
            "",
            "## Further analytical questions",
            "",
            "- Which EXP-036 processing stage causes the p95 overhead, and can it be reduced without changing canonical output?",
            "- Which routing configuration remains on the Pareto frontier after adjudicated routing targets become available?",
            "- Do reviewers agree on the 24 safe candidates, and which Agent 4 error categories dominate after adjudication?",
            "- Does BigUI improve evidence-state interpretation without increasing overclaim errors?",
            "- Does a frozen deterministic candidate produce positive net correction on unseen data without macro-F1 or subgroup harm?",
            "",
            "## Claim boundary",
            "",
            snapshot["claimBoundary"],
            "",
        ]
    )
    return "\n".join(lines)


def render_html(snapshot: dict[str, Any]) -> str:
    summary = snapshot["summary"]
    records = snapshot["evaluationRecords"]
    dimension_ids = [
        "protocol",
        "data",
        "execution",
        "reproducibility",
        "safety",
        "comparability",
        "empiricalValidity",
    ]
    status_counts = Counter(record["verdict"] for record in records)
    dimension_pass = {
        dimension: sum(
            record["dimensions"][dimension]["status"] == "pass"
            for record in records
        )
        for dimension in dimension_ids
    }
    max_pass = max(dimension_pass.values()) or 1
    evidence_max = max(snapshot["evidenceDistribution"].values()) or 1
    guardrails = snapshot["guardrailSummary"]
    def esc(value: Any) -> str:
        return html.escape(str(value), quote=True)

    kpis = [
        ("Registered", summary["evaluatedExperiments"], "EXP-000–EXP-040"),
        ("Executed", summary["executedExperiments"], "accepted source-backed runs"),
        ("Protocol / gated", summary["protocolOnlyExperiments"], "no result invented"),
        ("Measured engineering", summary["experimentsWithMeasuredEngineeringEvidence"], "mechanism and operations"),
        ("Empirical classification", summary["experimentsWithEmpiricalClassificationEvidence"], "safe N=0"),
    ]
    kpi_html = "".join(
        f'<article class="kpi"><strong>{esc(value)}</strong><span>{esc(label)}</span><small>{esc(note)}</small></article>'
        for label, value, note in kpis
    )
    execution_bars = "".join(
        f'<div class="bar-row"><span>{esc(label.replace("_", " "))}</span><div class="track"><i style="width:{count / len(records) * 100:.2f}%"></i></div><b>{count}</b></div>'
        for label, count in sorted(status_counts.items())
    )
    dimension_bars = "".join(
        f'<div class="bar-row"><span>{esc(dimension)}</span><div class="track"><i style="width:{count / max_pass * 100:.2f}%"></i></div><b>{count}</b></div>'
        for dimension, count in dimension_pass.items()
    )
    evidence_bars = "".join(
        f'<div class="bar-row"><span>{esc(label)}</span><div class="track"><i style="width:{count / evidence_max * 100:.2f}%"></i></div><b>{count}</b></div>'
        for label, count in snapshot["evidenceDistribution"].items()
    )
    guardrail_bars = "".join(
        f'<div class="bar-row"><span>{esc(label)}</span><div class="track"><i style="width:{value / max(guardrails["assessedObservations"], 1) * 100:.2f}%"></i></div><b>{value}</b></div>'
        for label, value in (
            ("met", guardrails["met"]),
            ("missed", guardrails["missed"]),
            ("not computable", guardrails["notComputable"]),
        )
    )
    table_rows = []
    for record in records:
        cells = "".join(
            f'<td><span class="state {esc(record["dimensions"][dimension]["status"])}">{esc(record["dimensions"][dimension]["status"].replace("_", " "))}</span></td>'
            for dimension in dimension_ids
        )
        search = " ".join(
            [
                record["experimentId"],
                record["title"],
                record["status"],
                record["evidenceClass"],
                record["verdict"],
            ]
        ).lower()
        table_rows.append(
            f'<tr data-search="{esc(search)}" data-verdict="{esc(record["verdict"])}">'
            f'<td><b>{esc(record["experimentId"])}</b><small>{esc(record["title"])}</small></td>'
            f'<td>{esc(record["executionState"])}</td><td>{esc(record["verdict"])}</td>'
            f"{cells}<td>{record['observationCount']}</td></tr>"
        )
    ladder = "".join(
        f'<article class="stage"><b>{esc(item["id"])}</b><strong>{esc(item["title"])}</strong><span>{esc(item["currentState"].replace("_", " "))}</span><p>{esc(item["purpose"])}</p></article>'
        for item in load_json(STANDARD)["baselineLadder"]
    )
    findings = "".join(f"<li>{esc(item)}</li>" for item in snapshot["findings"])
    recommendations = "".join(
        f"<li>{esc(item)}</li>" for item in snapshot["recommendations"]
    )
    highlight_cards = "".join(
        '<article class="highlight-card">'
        f'<div class="highlight-head"><b>{esc(item["experimentId"])}</b>'
        f'<span>{esc(item["evidenceClass"])}</span></div>'
        f'<h3>{esc(item["title"])}</h3><p>{esc(item["summary"])}</p>'
        '<div class="highlight-metrics">'
        + "".join(
            '<div class="highlight-metric">'
            f'<strong>{esc(metric["metricId"])}</strong>'
            f'<b>{esc(format_value(metric["value"]))} '
            f'{esc(metric["unit"])}</b>'
            f'<small>N={esc(format_value(metric["denominator"]))} · '
            f'{esc(format_dimensions(metric["dimensions"]))}</small>'
            f'<small>{esc(metric["observationDate"])} · '
            f'{esc(metric["sourcePath"])} · '
            f'{esc(metric["sourceSha256"][:12])}…</small></div>'
            for metric in item["metrics"]
        )
        + "</div>"
        f'<div class="claim">{esc(item["claimBoundary"])}</div></article>'
        for item in snapshot["resultHighlights"]
    )
    data_json = json.dumps(
        snapshot, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).replace("</", "<\\/")
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="description" content="VEGO-AI all-experiment benchmark and analytics report.">
<title>VEGO-AI Experiment Benchmark Analytics</title>
<style>
:root{{--bg:#071119;--panel:#102731;--panel2:#15343f;--line:#31515c;--text:#f3fbfc;--muted:#b4c8cd;--cyan:#61e6d6;--blue:#67a9ff;--green:#69db9d;--amber:#ffc857;--red:#ff7b78;--violet:#c5a3ff}}
*{{box-sizing:border-box}}html{{scroll-behavior:smooth}}body{{margin:0;background:radial-gradient(circle at 10% 0,rgba(97,230,214,.12),transparent 28rem),var(--bg);color:var(--text);font:15px/1.55 "Segoe UI",Arial,sans-serif}}main,header,footer{{width:min(1380px,calc(100% - 28px));margin:auto;min-width:0}}header{{padding:56px 0 30px}}h1{{font-size:clamp(2.4rem,6vw,5.2rem);line-height:.98;margin:.3rem 0;letter-spacing:-.05em}}h2{{font-size:clamp(1.5rem,3vw,2.3rem)}}p,small,footer{{color:var(--muted);overflow-wrap:anywhere}}a{{color:var(--cyan)}}.eyebrow{{color:var(--cyan);font-weight:800;letter-spacing:.12em;text-transform:uppercase}}.boundary{{border-left:4px solid var(--amber);padding:14px;background:rgba(255,200,87,.08);border-radius:10px}}section{{padding:32px 0;border-top:1px solid var(--line);min-width:0;max-width:100%}}.kpis,.grid,.ladder,.highlight-grid{{display:grid;gap:12px;min-width:0}}.kpis{{grid-template-columns:repeat(5,1fr)}}.grid{{grid-template-columns:repeat(3,1fr)}}.ladder{{grid-template-columns:repeat(6,1fr)}}.highlight-grid{{grid-template-columns:repeat(2,1fr)}}.kpi,.panel,.stage,.highlight-card{{background:linear-gradient(145deg,var(--panel),#0c1e27);border:1px solid var(--line);border-radius:16px;padding:16px;min-width:0}}.kpi strong{{display:block;font-size:2.2rem}}.kpi span,.stage strong{{display:block}}.stage b{{color:var(--cyan);font-size:1.35rem}}.highlight-head{{display:flex;justify-content:space-between;gap:8px;color:var(--cyan)}}.highlight-head span{{border:1px solid var(--line);border-radius:999px;padding:2px 8px;color:var(--muted)}}.highlight-metrics{{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:8px}}.highlight-metric{{padding:10px;border:1px solid var(--line);border-radius:12px;background:rgba(7,17,25,.45);min-width:0}}.highlight-metric strong,.highlight-metric b,.highlight-metric small{{display:block;overflow-wrap:anywhere}}.highlight-metric b{{color:var(--green);font-size:1.1rem}}.claim{{margin-top:10px;padding-top:9px;border-top:1px solid var(--line);color:var(--amber);font-size:.82rem}}.bar-list{{display:grid;gap:10px}}.bar-row{{display:grid;grid-template-columns:minmax(140px,1fr) 3fr 42px;gap:10px;align-items:center}}.track{{height:12px;background:#07141b;border:1px solid var(--line);border-radius:999px;overflow:hidden}}.track i{{display:block;height:100%;background:linear-gradient(90deg,var(--cyan),var(--blue))}}.explain{{margin-top:12px;padding-top:10px;border-top:1px solid var(--line)}}.table-shell{{overflow:auto;border:1px solid var(--line);border-radius:16px;max-width:100%}}table{{width:100%;border-collapse:collapse;min-width:1180px;background:var(--panel)}}th,td{{padding:9px;border-bottom:1px solid var(--line);text-align:left;vertical-align:top}}td small{{display:block;max-width:240px}}.state{{display:inline-block;border:1px solid var(--line);border-radius:999px;padding:3px 7px;font-size:.72rem}}.pass{{color:var(--green)}}.partial,.not_measured{{color:var(--amber)}}.fail,.not_eligible{{color:var(--red)}}.not_applicable{{color:var(--muted)}}.controls{{display:flex;gap:8px;flex-wrap:wrap;margin:12px 0}}input,select{{background:var(--panel);color:var(--text);border:1px solid var(--line);border-radius:10px;padding:9px;min-width:220px}}input:focus-visible,select:focus-visible,a:focus-visible{{outline:3px solid var(--amber);outline-offset:2px}}.pipeline{{display:flex;gap:8px;overflow:auto;max-width:100%}}.pipeline span{{flex:1 0 140px;text-align:center;padding:14px;border:1px solid var(--line);border-radius:12px;background:var(--panel2)}}.stop{{border-color:var(--red)!important;color:var(--red)}}footer{{padding:28px 0 50px}}
@media(max-width:900px){{.kpis{{grid-template-columns:repeat(2,1fr)}}.grid,.highlight-grid{{grid-template-columns:1fr}}.ladder{{grid-template-columns:repeat(2,1fr)}}}}
@media(max-width:480px){{main,header,footer{{width:calc(100% - 18px)}}.kpis,.ladder,.highlight-metrics{{grid-template-columns:1fr}}.bar-row{{grid-template-columns:1fr}}input,select{{width:100%;min-width:0}}}}
@media(prefers-reduced-motion:reduce){{*{{scroll-behavior:auto!important;transition:none!important}}}}
@media print{{:root{{--bg:#fff;--panel:#fff;--panel2:#f3f3f3;--line:#777;--text:#111;--muted:#333}}body{{background:#fff}}.controls{{display:none}}.panel,.kpi,.stage{{break-inside:avoid}}}}
</style>
</head>
<body>
<header>
<div class="eyebrow">VEGO-AI · ExperimentBenchmarkSnapshot-v1 · tracked sanitized</div>
<h1>Every experiment evaluated against one measurable standard.</h1>
<p>This technical report separates what was executed, what passed, what missed an engineering target, what remains a protocol, and what cannot be computed without independent evidence.</p>
<div class="boundary"><strong>Current empirical gate:</strong> 0/24 independent safe labels. Accuracy, macro-F1, paired correctness, net correction, and generalization remain intentionally blank.</div>
</header>
<main>
<section id="summary"><h2>Technical summary</h2><div class="kpis">{kpi_html}</div><p>The accepted run store contains {snapshot['programState']['acceptedBundles']} bundles and {snapshot['programState']['metricObservations']} source-linked MetricObservation-v2 records. These support mechanism, architecture, safety, routing, provenance, and reproducibility evaluation—not an accuracy claim.</p></section>
<section id="journey"><h2>Evidence journey</h2><div class="pipeline"><span>B0<br>frozen baseline</span><span>B1<br>mechanism evidence</span><span class="stop">B2<br>0 safe labels</span><span>B3<br>frozen candidate</span><span>B4<br>sealed pilot</span><span>B5<br>external replication</span></div><p class="explain">The stop at B2 is a methodological control. It prevents same-pattern memory, synthetic fixtures, or paper author judgments from being reused as independent ground truth.</p></section>
<section id="findings"><h2>Key findings</h2><div class="panel"><ul>{findings}</ul></div></section>
<section id="results"><h2>Measured result highlights</h2><p>Selected latest-run observations with explicit denominators, source hashes, dates, evidence classes, and claim boundaries.</p><div class="highlight-grid">{highlight_cards}</div></section>
<section id="visuals"><h2>Program analytics</h2><div class="grid"><article class="panel"><h3>Result verdicts</h3><div class="bar-list">{execution_bars}</div><p class="explain">Executed does not mean positive: measured partial results keep null empirical fields and missed operational targets visible.</p></article><article class="panel"><h3>Dimension pass coverage</h3><div class="bar-list">{dimension_bars}</div><p class="explain">These are independent pass counts, not a weighted global score. Not-applicable and not-eligible dimensions are not converted to failures.</p></article><article class="panel"><h3>Evidence classes</h3><div class="bar-list">{evidence_bars}</div><p class="explain">Synthetic, offline, mechanism, historical, and blocked records stay in distinct classes. They cannot be merged into one performance series.</p></article><article class="panel"><h3>Latest accepted guardrail outcomes</h3><div class="bar-list">{guardrail_bars}</div><p class="explain">{guardrails['assessedObservations']} target-bearing or gated observations were assessed on latest accepted runs. Accepted history retains {guardrails['historicalMissed']} misses across {guardrails['historicalAssessedObservations']} assessed observations.</p></article></div></section>
<section id="baseline"><h2>Baseline ladder</h2><div class="ladder">{ladder}</div><p class="explain">B0 and B1 are available for integrity and mechanism analysis. B2–B5 are evidence stages, not claims that have already been achieved.</p></section>
<section id="matrix"><h2>All-experiment evaluation matrix</h2><div class="controls"><label>Search <input id="search" type="search" placeholder="EXP-036, parity, labels…"></label><label>Verdict <select id="verdict"><option value="">All</option>{''.join(f'<option>{esc(key)}</option>' for key in sorted(status_counts))}</select></label><strong id="visible-count">{len(records)} / {len(records)}</strong></div><div class="table-shell"><table><thead><tr><th>Experiment</th><th>Execution</th><th>Verdict</th>{''.join(f'<th>{esc(item)}</th>' for item in dimension_ids)}<th>Observations</th></tr></thead><tbody id="records">{''.join(table_rows)}</tbody></table></div><p class="explain">Every experiment receives a result: a measured verdict when an accepted run exists, a protocol or gate verdict when human/approval evidence is required, or a parked verdict for preserved historical work.</p></section>
<section id="method"><h2>Scope, data, metric definitions, and methodology</h2><div class="grid"><article class="panel"><h3>Data integrity</h3><p>Every measured record is checked for source hash, cohort hash, denominator, explicit missingness, evidence class, and leakage constraints.</p></article><article class="panel"><h3>Comparison integrity</h3><p>Direct deltas require equivalent dataset, partition, baseline, policy, prompt, model, metric version, eligibility, leakage class, and evidence class except for the declared treatment.</p></article><article class="panel"><h3>Statistical integrity</h3><p>Safe N=0 forces null empirical fields. Positive formal improvement later requires paired unseen evidence, positive net-correction confidence bounds, exact McNemar p&lt;0.05, no macro-F1 decline, and no predefined subgroup harm.</p></article></div></section>
<section id="limitations"><h2>Limitations and robustness</h2><div class="panel"><ul><li>Paper-versus-current counts are contextual version markers, not accuracy deltas.</li><li>Offline topology and fault fixtures do not establish live or universal behavior.</li><li>Latency is machine-specific; the pinned EXP-036 summary reports engineeringTargetMet=false for the unified P95 check at scale, and the ratio varies run to run on the same machine.</li><li>Human-value and classification experiments remain unexecuted until their consent and evidence gates open.</li><li>Negative and null results remain reportable and cannot be silently retuned away.</li></ul></div></section>
<section id="next"><h2>Recommended next steps</h2><div class="panel"><ol>{recommendations}</ol></div></section>
</main>
<footer>Generated {esc(snapshot['generatedAt'])} · projection {esc(snapshot['inputProjectionSha256'])} · <a href="VEGO-AI-Research-Hub.html#experiment-benchmarks">Open BigUI benchmark workspace</a></footer>
<script id="benchmark-data" type="application/json">{data_json}</script>
<script>
(()=>{{const rows=[...document.querySelectorAll("#records tr")],search=document.getElementById("search"),verdict=document.getElementById("verdict"),count=document.getElementById("visible-count");function filter(){{const q=search.value.trim().toLowerCase(),v=verdict.value;let n=0;for(const row of rows){{const show=(!q||row.dataset.search.includes(q))&&(!v||row.dataset.verdict===v);row.hidden=!show;if(show)n++}}count.textContent=`${{n}} / ${{rows.length}}`}}search.addEventListener("input",filter);verdict.addEventListener("change",filter)}})();
</script>
</body>
</html>
"""


def update_file(path: Path, content: str, check: bool) -> None:
    current = path.read_text(encoding="utf-8") if path.is_file() else None
    if current == content:
        return
    if check:
        raise ValueError(f"stale generated output: {path.relative_to(ROOT)}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="\n")


def main() -> int:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--check", action="store_true")
    group.add_argument("--refresh", action="store_true")
    args = parser.parse_args()
    try:
        snapshot = build_snapshot()
        update_file(
            SNAPSHOT,
            json.dumps(snapshot, ensure_ascii=False, indent=2) + "\n",
            args.check,
        )
        update_file(REPORT_MD, render_markdown(snapshot), args.check)
        update_file(REPORT_HTML, render_html(snapshot), args.check)
        print(
            "Experiment benchmark: PASS "
            f"({snapshot['summary']['executedExperiments']}/"
            f"{snapshot['summary']['evaluatedExperiments']} executed; "
            f"{snapshot['programState']['safeLabels']} safe labels)"
        )
        return 0
    except Exception as exc:
        print(f"Experiment benchmark: FAIL: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
