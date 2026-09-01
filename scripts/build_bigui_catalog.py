#!/usr/bin/env python3
"""Build the canonical, privacy-safe VEGO-AI BigUI experiment catalog."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

import jsonschema

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from vego_bigui.store import load_bundles, run_store_summary  # noqa: E402

REGISTRY = ROOT / "experiments" / "registry.md"
PROGRAM = ROOT / "docs" / "research" / "h-layer" / "program-status-snapshot-v1.json"
THESIS = (
    ROOT
    / "docs"
    / "research"
    / "thesis-evidence"
    / "thesis-evidence-snapshot-v1.json"
)
BIGUI_PROGRAM = ROOT / "experiments" / "bigui-program-v1.json"
BASELINE = (
    ROOT / "docs" / "research" / "hardening" / "baseline-lock-manifest-v2.json"
)
SECURITY = (
    ROOT / "docs" / "research" / "hardening" / "security-posture-snapshot-v1.json"
)
ITERATION_15 = (
    ROOT / "docs" / "research" / "hardening" / "iteration-015-manifest.json"
)
ARCHITECTURE_FIXTURES = (
    ROOT
    / "docs"
    / "research"
    / "bigui"
    / "architecture-fixture-results-v1.json"
)
PAPER_BASELINE = (
    ROOT
    / "docs"
    / "research"
    / "bigui"
    / "paper-baseline-snapshot-v1.json"
)
BASELINE_COMPARISON = (
    ROOT
    / "docs"
    / "research"
    / "bigui"
    / "baseline-comparison-results-v1.json"
)
EVALUATION_STANDARD = (
    ROOT
    / "docs"
    / "research"
    / "bigui"
    / "experiment-evaluation-standard-v1.json"
)
EXPERIMENT_BENCHMARK = (
    ROOT
    / "docs"
    / "research"
    / "bigui"
    / "experiment-benchmark-snapshot-v1.json"
)
CATALOG_SCHEMA = ROOT / "schemas" / "experiment-catalog-snapshot-v1.schema.json"
METRIC_SCHEMA = ROOT / "schemas" / "metric-observation-v1.schema.json"
RUN_SCHEMA = ROOT / "schemas" / "experiment-run-envelope-v1.schema.json"
ARCHITECTURE_SCHEMA = ROOT / "schemas" / "architecture-variant-v1.schema.json"
PAPER_BASELINE_SCHEMA = (
    ROOT / "schemas" / "paper-baseline-snapshot-v1.schema.json"
)
BASELINE_COMPARISON_SCHEMA = (
    ROOT / "schemas" / "baseline-comparison-results-v1.schema.json"
)
EVALUATION_STANDARD_SCHEMA = (
    ROOT / "schemas" / "experiment-evaluation-standard-v1.schema.json"
)
EXPERIMENT_BENCHMARK_SCHEMA = (
    ROOT / "schemas" / "experiment-benchmark-snapshot-v1.schema.json"
)
METRIC_DEFINITION_V2_SCHEMA = ROOT / "schemas" / "metric-definition-v1.schema.json"
METRIC_V2_SCHEMA = ROOT / "schemas" / "metric-observation-v2.schema.json"
RUN_BUNDLE_SCHEMA = ROOT / "schemas" / "accepted-experiment-run-bundle-v1.schema.json"
ACCEPTED_RUNS_DIR = ROOT / "experiments" / "accepted-runs"
CURRENT_RUN_INDEX = ROOT / "experiments" / "current-run-index-v1.json"
CURRENT_RUN_INDEX_SCHEMA = ROOT / "schemas" / "current-run-index-v1.schema.json"
OUTPUT_DIR = ROOT / "docs" / "research" / "bigui"
CATALOG_OUTPUT = OUTPUT_DIR / "experiment-catalog-snapshot-v1.json"
ARTIFACT_MANIFEST_OUTPUT = OUTPUT_DIR / "artifact-manifest-v1.json"
ARTIFACT_SNAPSHOT_OUTPUT = OUTPUT_DIR / "artifact-snapshot-v1.json"

STATUS_VOCABULARY = {
    "Implemented",
    "Delivered — provisional",
    "Documented — parked",
    "Offline design",
    "Offline evidence",
    "Synthetic fixture",
    "Evaluation-ready",
    "Pending expert input",
    "Proposal — not approved",
    "Blocked",
    "Confirmed outcome",
}

DEPENDENCIES = {
    "EXP-003": ["EXP-005"],
    "EXP-005": ["EXP-002"],
    "EXP-011": ["EXP-005", "M-02", "M-05"],
    "EXP-012": ["EXP-005"],
    "EXP-019": ["M-05"],
    "EXP-020": ["EXP-019", "M-05"],
    "EXP-021": ["EXP-020"],
    "EXP-022": ["EXP-021"],
    "EXP-023": ["EXP-021", "EXP-022", "M-02", "M-04", "M-05"],
    "EXP-024": ["EXP-023"],
    "EXP-025": ["EXP-024", "M-06"],
    "EXP-026": ["EXP-025", "M-05"],
    "EXP-027": ["EXP-025"],
    "EXP-028": ["M-05", "M-06"],
    "EXP-029": ["EXP-020", "EXP-023", "M-05", "M-06"],
}

APPROVAL_GATES = {
    "EXP-005": ["Supervisor-approved protocol", "Two independent reviewers"],
    "EXP-011": ["M-02 and M-05 accepted", "At least 20 safe labels"],
    "EXP-019": ["Consent and calibration protocol approved"],
    "EXP-020": ["Reviewer panel and adjudicator approved"],
    "EXP-023": ["M-02, M-04, and M-05 accepted"],
    "EXP-024": ["Frozen policy and sealed partition"],
    "EXP-025": ["M-06 accepted", "External education batch approved"],
    "EXP-026": ["Human-study consent protocol approved"],
    "EXP-028": ["Model provenance protocol approved"],
    "EXP-029": [
        "At least 20 safe labels",
        "Frozen prompt, policy, partition, and cost limit",
        "Supervisor approval",
    ],
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_sha256(value: Any) -> str:
    payload = json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path.relative_to(ROOT)} must contain a JSON object")
    return value


def parse_registry() -> dict[str, dict[str, str]]:
    records: dict[str, dict[str, str]] = {}
    for line in REGISTRY.read_text(encoding="utf-8").splitlines():
        if not line.startswith("| EXP-"):
            continue
        parts = [part.strip() for part in line.strip().strip("|").split("|")]
        if len(parts) != 7:
            raise ValueError(f"malformed experiment registry row: {line}")
        experiment_id, title, status, rq, code, outputs, notes = parts
        if experiment_id in records:
            raise ValueError(f"duplicate registry ID {experiment_id}")
        records[experiment_id] = {
            "id": experiment_id,
            "title": title,
            "status": status,
            "researchQuestion": rq,
            "code": code,
            "outputs": outputs,
            "notes": notes,
        }
    expected = {f"EXP-{index:03d}" for index in range(41)}
    missing = sorted(expected - set(records))
    if missing:
        raise ValueError(f"registry mismatch; missing={missing}")
    extras = sorted(set(records) - expected)
    for extra_id in extras:
        number = int(extra_id.split("-")[1])
        if number <= 40:
            raise ValueError(f"unexpected non-sequential registry ID {extra_id}")
        experiment_directory(extra_id)
        print(
            f"NOTE: {extra_id} is registered outside the frozen EXP-000..EXP-040 "
            "benchmark cohort; it is identity-tracked only until a benchmark "
            "revision admits it.",
            file=sys.stderr,
        )
        del records[extra_id]
    return records


def experiment_directory(experiment_id: str) -> Path:
    matches = sorted((ROOT / "experiments").glob(f"{experiment_id}-*"))
    if len(matches) != 1 or not matches[0].is_dir():
        raise ValueError(
            f"{experiment_id} must have exactly one experiment directory"
        )
    readme = matches[0] / "README.md"
    if not readme.is_file():
        raise ValueError(f"{readme.relative_to(ROOT)} is missing")
    return matches[0]


def research_space(number: int) -> str:
    if 6 <= number <= 18 or number in {30, 33, 34, 35, 36}:
        return "Cross-program"
    if 25 <= number <= 29:
        return "PhD"
    return "MSc"


def research_track(number: int) -> str:
    if number == 0:
        return "Baseline integrity"
    if number == 1:
        return "Mechanism readiness"
    if 2 <= number <= 5 or number in {11, 12}:
        return "Evaluation infrastructure"
    if 6 <= number <= 10:
        return "Observation, dosage, and verification"
    if 13 <= number <= 18:
        return "Architecture conformance"
    if 19 <= number <= 24:
        return "MSc empirical evaluation"
    if 25 <= number <= 27:
        return "PhD extension"
    if 28 <= number <= 29:
        return "Model evaluation"
    if number == 30:
        return "Observatory integrity"
    if number in {31, 32}:
        return "BigUI human value"
    return "Architecture validation"


def evidence_class(experiment_id: str, status: str) -> str:
    number = int(experiment_id[-3:])
    if number == 0:
        return "historical"
    if number == 1 or status == "Implemented":
        return "mechanism"
    if status in {"Offline evidence", "Offline design"}:
        return "offline"
    if status == "Synthetic fixture":
        return "synthetic"
    if status == "Evaluation-ready":
        return "evaluation_ready"
    if status == "Proposal — not approved":
        return "proposal"
    if status in {"Pending expert input", "Blocked"}:
        return "blocked"
    if status == "Documented — parked":
        return "historical"
    return "proposal"


def architecture_targets(number: int) -> list[str]:
    if number == 0:
        return ["B0"]
    if number in {1, 13, 14, 15, 16, 17, 18}:
        return ["B1", "legacy", "unified", "parity"]
    if 2 <= number <= 5 or number in {11, 12, 19, 20, 21, 22, 23, 24}:
        return ["B0", "B1", "evaluation"]
    if 6 <= number <= 10:
        return ["B1", "topology-a", "topology-b", "topology-c"]
    if 25 <= number <= 27:
        return ["B0", "B1", "evaluation"]
    if 28 <= number <= 29:
        return ["B0", "model"]
    return ["BigUI"]


def experiment_metrics(number: int) -> list[str]:
    measured = {
        0: ["BASELINE_HASH_PRESERVATION"],
        1: [
            "MECH_ADVICE_STRENGTH_COUNT",
            "MECH_COMPARISON_ROWS",
            "MECH_REVIEW_AFTER_MEMORY",
            "SAFETY_CLASSIFICATION_CHANGES",
        ],
        2: [
            "LABEL_CANDIDATES",
            "LABEL_EXISTING_SAME_PATTERN",
            "LABEL_RECOMMENDED_ROWS",
        ],
        3: [
            "CLASSIFICATION_ACCURACY_B0",
            "CLASSIFICATION_ACCURACY_B1",
            "CLASSIFICATION_MACRO_F1_B0",
            "CLASSIFICATION_MACRO_F1_B1",
            "PAIRED_NET_CORRECTION",
        ],
        4: ["SYNTHETIC_POLICY_SAFE_DELTA_PP"],
        5: [
            "LABEL_ADJUDICATED",
            "LABEL_GENERALIZATION_SAFE",
            "LABEL_REVIEWER2",
            "LABEL_SUPPLIED",
            "LABEL_VALID",
        ],
        6: [
            "EVENT_EARLY_STAGE",
            "EVENT_SEV2PLUS",
            "EVENT_TOTAL_RECONSTRUCTED",
            "EVENT_UNCERTAINTY_MARKED",
            "MECH_QUEUE_TO_EVENT_COUNT_RATIO",
            "MECH_REVIEW_QUEUE_ITEMS",
        ],
        7: [
            "ROUTING_BUNDLING_REDUCTION",
            "ROUTING_EVENT_LOAD",
            "ROUTING_HIGH_SEVERITY_COVERAGE",
            "ROUTING_TRANSACTION_LOAD",
            "ROUTING_WEIGHTED_COVERAGE",
        ],
        8: ["TRIGGER_CAP_CAPTURE", "TRIGGER_MAX_ADDED_LOAD"],
        9: [
            "HVERIFY_DETECTION_RECALL",
            "HVERIFY_FALSE_NEGATIVES",
            "HVERIFY_FALSE_POSITIVES",
            "HVERIFY_FINAL_STATUS_COUNT",
            "HVERIFY_SPECIFICITY",
            "HVERIFY_TRUE_NEGATIVES",
            "HVERIFY_TRUE_POSITIVES",
        ],
        10: [
            "CONVERGENCE_ADJUDICATION_RATE",
            "CONVERGENCE_NO_CONFLICT_RATE",
            "CONVERGENCE_RESOLVED_RATE",
            "CONVERGENCE_TIMEOUT_RATE",
        ],
        12: [
            "CLASSIFICATION_ACCURACY_B0",
            "CLASSIFICATION_ACCURACY_B1",
            "CLASSIFICATION_MACRO_F1_B0",
            "CLASSIFICATION_MACRO_F1_B1",
            "EVALUATOR_CROSSCHECK_PASS",
            "LABEL_GENERALIZATION_SAFE",
            "LABEL_SUPPLIED",
            "PAIRED_NET_CORRECTION",
        ],
        13: [
            "CONTRACT_E15_PARKED",
            "CONTRACT_EXPLICIT_GAPS",
            "CONTRACT_LINEAGE_COMPLETE_RATE",
            "CONTRACT_SCHEMA_VALID_RATE",
        ],
        14: ["REPLAY_DUPLICATE_REVIEW_ITEMS", "REPLAY_IDENTICAL_RUNS"],
        15: [
            "WORKLOAD_BUNDLE_COLLISIONS",
            "WORKLOAD_DEFERRED_RECOVERY",
            "WORKLOAD_HIGH_SEVERITY_COVERAGE",
            "WORKLOAD_SELECTED_LOAD",
        ],
        16: [
            "AUTHORITY_CORRECTION_APPLICATIONS",
            "AUTHORITY_SAFE_CASE_RATE",
            "AUTHORITY_TRUSTED_MEMORY_WRITES",
        ],
        17: [
            "VERIFY_EXPECTED_OUTCOME_RATE",
            "VERIFY_SOURCE_FAMILY_COUNT",
        ],
        18: [
            "PROPOSAL_APPLICATIONS",
            "PROPOSAL_DIFF_REPRODUCIBLE",
            "PROPOSAL_SOURCE_HASH_CHANGED",
        ],
    }
    if number in measured:
        return measured[number]
    if number in {11, 19, 20, 21, 23, 24, 25}:
        return [
            "CLASSIFICATION_ACCURACY_B0",
            "CLASSIFICATION_MACRO_F1_B0",
            "PAIRED_NET_CORRECTION",
        ]
    if number == 22:
        return ["ROUTING_PRECISION", "ROUTING_RECALL", "RETRIEVAL_TOP1_RELEVANCE"]
    if number == 26:
        return ["HUMAN_REVIEW_TIME", "HUMAN_ESCALATION_QUALITY"]
    if number == 27:
        return ["ROBUSTNESS_ABLATION_DELTA"]
    if number in {28, 29}:
        return ["MODEL_REPLAY_STABILITY"]
    return []


def baseline_and_comparator(number: int) -> tuple[str, str]:
    if number == 0:
        return ("Official baseline tag", "Current locked baseline")
    if number == 1:
        return ("Original Agent 4", "M4B-1 parallel comparison")
    if 2 <= number <= 5 or number in {11, 12, 19, 20, 21, 22, 23, 24, 25}:
        return ("B0 frozen Agent 4", "Independent expert or frozen candidate")
    if 6 <= number <= 18:
        return ("Current offline contract behavior", "Candidate architecture configuration")
    if number == 26:
        return ("Review without reusable memory", "Review with advisory memory")
    if number == 27:
        return ("Frozen full configuration", "Predeclared ablations")
    if number in {28, 29}:
        return ("Frozen GPT-4o request", "Frozen candidate snapshot")
    return ("Current fragmented interfaces", "Catalog-driven BigUI")


def claim_boundary(experiment_id: str, evidence: str) -> str:
    if experiment_id == "EXP-005":
        return (
            "Zero safe labels means accuracy and macro-F1 remain not computable; "
            "labels are never inferred or prefilled."
        )
    if experiment_id == "EXP-012":
        return "The validated interface remains NOT YET COMPUTABLE at safe N=0."
    boundaries = {
        "historical": "Historical or parked record only; it is not current empirical evidence.",
        "mechanism": "Mechanism readiness and baseline protection only; no accuracy or generalization claim.",
        "offline": "Offline architecture or workload evidence only; no production approval or accuracy claim.",
        "synthetic": "Synthetic fixture behavior only; never human or empirical validation.",
        "evaluation_ready": "Protocol and tooling readiness only until independent evidence is supplied.",
        "pilot": "Pilot evidence only with explicit sample and validity limitations.",
        "empirical": "Claims are limited to the preregistered cohort, metrics, and confidence bounds.",
        "proposal": "Proposal only; not approved, implemented, or empirically validated.",
        "blocked": "The required human, evidence, or approval gate is closed.",
    }
    return boundaries[evidence]


def architecture_variants() -> list[dict[str, Any]]:
    common = {
        "schemaVersion": "ArchitectureVariant-v1",
        "contractVersion": "1.0",
        "humanAuthorityPreserved": True,
        "baselineMutationAllowed": False,
    }
    return [
        {
            **common,
            "id": "legacy",
            "kind": "runtime_mode",
            "title": "Legacy M1–M4B-1",
            "status": "Implemented",
            "implemented": True,
            "approved": True,
            "default": True,
            "failureBehavior": "Preserve the existing artifact behavior.",
            "evidenceClass": "mechanism",
            "claimBoundary": "Publication reference; not an accuracy result.",
        },
        {
            **common,
            "id": "unified",
            "kind": "runtime_mode",
            "title": "Unified contract runtime",
            "status": "Implemented",
            "implemented": True,
            "approved": False,
            "default": False,
            "failureBehavior": "Reject semantic drift and preserve the baseline.",
            "evidenceClass": "mechanism",
            "claimBoundary": "Explicit opt-in mechanism path; legacy remains default.",
        },
        {
            **common,
            "id": "parity",
            "kind": "runtime_mode",
            "title": "Fail-closed parity",
            "status": "Implemented",
            "implemented": True,
            "approved": False,
            "default": False,
            "failureBehavior": "Publish only legacy output on any mismatch.",
            "evidenceClass": "mechanism",
            "claimBoundary": "Compatibility control only; no empirical performance claim.",
        },
        {
            **common,
            "id": "topology-a",
            "kind": "h_layer_topology",
            "title": "Topology A · H1, H2, H3",
            "status": "Offline design",
            "implemented": False,
            "approved": False,
            "default": False,
            "failureBehavior": "Park unresolved cross-agent state and preserve baseline.",
            "evidenceClass": "proposal",
            "claimBoundary": "Offline comparison candidate while M-02 is deferred.",
        },
        {
            **common,
            "id": "topology-b",
            "kind": "h_layer_topology",
            "title": "Topology B · Observer + Integrator",
            "status": "Proposal — not approved",
            "implemented": False,
            "approved": False,
            "default": False,
            "failureBehavior": "Park unresolved integrator state and preserve baseline.",
            "evidenceClass": "proposal",
            "claimBoundary": "Provisional recommendation only while M-02 is deferred.",
        },
        {
            **common,
            "id": "topology-c",
            "kind": "h_layer_topology",
            "title": "Topology C · one modular agent",
            "status": "Offline design",
            "implemented": False,
            "approved": False,
            "default": False,
            "failureBehavior": "Park unresolved skill state and preserve baseline.",
            "evidenceClass": "proposal",
            "claimBoundary": "Offline comparison candidate while M-02 is deferred.",
        },
    ]


def metric_observations(
    thesis: dict[str, Any],
    program: dict[str, Any],
    baseline: dict[str, Any],
    architecture_fixtures: dict[str, Any],
    security: dict[str, Any],
) -> list[dict[str, Any]]:
    source_path = THESIS.relative_to(ROOT).as_posix()
    source_digest = sha256(THESIS)
    date = thesis["generatedAt"][:10]
    cohort_hash = canonical_sha256(
        [item["canonicalJsonSha256"] for item in baseline["agent4Outputs"]["files"]]
    )

    def observation(
        metric_id: str,
        value: Any,
        numerator: int | float | None,
        denominator: int | float | None,
        unit: str,
        direction: str,
        evidence: str,
        boundary: str,
    ) -> dict[str, Any]:
        return {
            "schemaVersion": "MetricObservation-v1",
            "metricId": metric_id,
            "value": value,
            "numerator": numerator,
            "denominator": denominator,
            "unit": unit,
            "direction": direction,
            "confidenceInterval": None,
            "sourcePath": source_path,
            "sourceSha256": source_digest,
            "evidenceClass": evidence,
            "observationDate": date,
            "cohortHash": cohort_hash,
            "metricSchemaVersion": "1.0",
            "claimBoundary": boundary,
        }

    evidence = thesis["evidence"]
    gate = program["exp005Gate"]
    result = [
        observation(
            "MECH_STUDENT_MODELS",
            evidence["studentModels"]["value"],
            evidence["studentModels"]["value"],
            evidence["studentModels"]["value"],
            "models",
            "neutral",
            "mechanism",
            "Descriptive corpus count; not a performance metric.",
        ),
        observation(
            "MECH_AGENT4_PATTERNS",
            evidence["agent4Patterns"]["value"],
            evidence["agent4Patterns"]["value"],
            evidence["agent4Patterns"]["value"],
            "patterns",
            "neutral",
            "mechanism",
            "Descriptive Agent 4 output count.",
        ),
        observation(
            "MECH_REVIEW_ITEMS",
            evidence["reviewItems"]["value"],
            evidence["reviewItems"]["value"],
            evidence["agent4Patterns"]["value"],
            "review items",
            "neutral",
            "mechanism",
            "Queue count is not validated human effort.",
        ),
        observation(
            "MECH_REUSABLE_JUDGMENTS",
            evidence["reusableJudgments"]["value"],
            evidence["reusableJudgments"]["value"],
            evidence["reviewItems"]["value"],
            "judgments",
            "neutral",
            "mechanism",
            "Legacy mechanism memory includes same-pattern evidence.",
        ),
        observation(
            "MECH_MEMORY_ADVICE_ITEMS",
            evidence["memoryAdviceItems"]["value"],
            evidence["memoryAdviceItems"]["value"],
            evidence["agent4Patterns"]["value"],
            "advice items",
            "neutral",
            "mechanism",
            "Advice remains advisory_only.",
        ),
        observation(
            "MECH_COMPARISON_ROWS",
            evidence["comparisonRows"]["value"],
            evidence["comparisonRows"]["value"],
            evidence["agent4Patterns"]["value"],
            "comparison rows",
            "neutral",
            "mechanism",
            "Parallel comparison coverage; not accuracy.",
        ),
        observation(
            "SAFETY_CLASSIFICATION_CHANGES",
            evidence["memoryInformedChanges"]["value"],
            evidence["memoryInformedChanges"]["value"],
            evidence["comparisonRows"]["value"],
            "classification changes",
            "lower_is_better",
            "mechanism",
            "The preserved mechanism changes zero baseline classifications.",
        ),
        observation(
            "LABEL_CANDIDATES",
            gate["candidateRows"],
            gate["candidateRows"],
            gate["candidateRows"],
            "candidate rows",
            "neutral",
            "evaluation_ready",
            "Candidate readiness is not supplied human evidence.",
        ),
        observation(
            "LABEL_GENERALIZATION_SAFE",
            gate["generalizationSafeValidLabels"],
            gate["generalizationSafeValidLabels"],
            gate["candidateRows"],
            "labels",
            "higher_is_better",
            "blocked",
            "Accuracy remains not computable at safe N=0.",
        ),
        observation(
            "ARCH_CONTROLLED_PARITY",
            1,
            thesis["runtimeHardening"]["parityEvidence"]["comparisonRowCount"],
            thesis["runtimeHardening"]["parityEvidence"]["comparisonRowCount"],
            "proportion",
            "target",
            "mechanism",
            "Controlled compatibility evidence only.",
        ),
    ]
    for metric_id in (
        "CLASSIFICATION_ACCURACY_B0",
        "CLASSIFICATION_ACCURACY_B1",
        "CLASSIFICATION_MACRO_F1_B0",
        "CLASSIFICATION_MACRO_F1_B1",
        "PAIRED_NET_CORRECTION",
    ):
        result.append(
            observation(
                metric_id,
                None,
                None,
                0,
                "not computable",
                "higher_is_better",
                "blocked",
                "Independent generalization-safe labels are required.",
            )
        )
    fixture_source_path = ARCHITECTURE_FIXTURES.relative_to(ROOT).as_posix()
    fixture_source_digest = sha256(ARCHITECTURE_FIXTURES)
    fixture_results = {
        item["experimentId"]: item for item in architecture_fixtures["experiments"]
    }

    def fixture_observation(
        metric_id: str,
        value: int | float,
        numerator: int | float | None,
        denominator: int | float | None,
        unit: str,
        evidence: str,
        boundary: str,
        direction: str = "target",
    ) -> dict[str, Any]:
        return {
            "schemaVersion": "MetricObservation-v1",
            "metricId": metric_id,
            "value": value,
            "numerator": numerator,
            "denominator": denominator,
            "unit": unit,
            "direction": direction,
            "confidenceInterval": None,
            "sourcePath": fixture_source_path,
            "sourceSha256": fixture_source_digest,
            "evidenceClass": evidence,
            "observationDate": architecture_fixtures["generatedAt"][:10],
            "cohortHash": architecture_fixtures["normalizedSha256"],
            "metricSchemaVersion": "1.0",
            "claimBoundary": boundary,
        }

    exp033 = fixture_results["EXP-033"]
    result.extend(
        [
            fixture_observation(
                "ARCH_FIXTURE_SEMANTIC_DIFFERENCES",
                exp033["semanticDifferences"],
                exp033["semanticDifferences"],
                exp033["artifactCount"] * exp033["repetitions"],
                "differences",
                "offline",
                "Clone-safe parity fixtures only; not controlled-corpus accuracy.",
            ),
            fixture_observation(
                "ARCH_FIXTURE_REPLAY_DETERMINISM",
                1 if exp033["deterministic"] else 0,
                exp033["artifactCount"] if exp033["deterministic"] else 0,
                exp033["artifactCount"],
                "proportion",
                "offline",
                "Deterministic fixture replay only.",
            ),
        ]
    )
    exp034 = fixture_results["EXP-034"]
    result.append(
        fixture_observation(
            "TOPOLOGY_CONTRACT_EQUIVALENCE",
            1 if exp034["contractEquivalent"] else 0,
            len(exp034["topologies"]) if exp034["contractEquivalent"] else 0,
            len(exp034["topologies"]),
            "proportion",
            "offline",
            "Structural simulation only; M-02 remains deferred.",
        )
    )
    for topology in exp034["topologies"]:
        prefix = topology["id"].replace("topology-", "TOPOLOGY_").upper()
        for suffix, key, unit, direction in (
            ("HANDOFFS", "handoffs", "handoffs", "lower_is_better"),
            (
                "CONTEXT_DUPLICATION",
                "contextBytes",
                "bytes",
                "lower_is_better",
            ),
            (
                "STATE_BOUNDARIES",
                "stateBoundaries",
                "boundaries",
                "lower_is_better",
            ),
            (
                "FAILURE_BREADTH",
                "failurePropagationBreadth",
                "skills affected",
                "lower_is_better",
            ),
            (
                "TRACE_COMPLETENESS",
                "traceCompleteness",
                "proportion",
                "higher_is_better",
            ),
        ):
            value = topology[key]
            result.append(
                fixture_observation(
                    f"{prefix}_{suffix}",
                    value,
                    value,
                    1 if suffix == "TRACE_COMPLETENESS" else None,
                    unit,
                    "offline",
                    "Structural fixture metric only; no topology is approved.",
                    direction,
                )
            )
    exp035 = fixture_results["EXP-035"]
    result.append(
        fixture_observation(
            "SAFETY_FAULT_CASES_PASS",
            1 if exp035["passed"] else 0,
            exp035["caseCount"] if exp035["passed"] else 0,
            exp035["caseCount"],
            "proportion",
            "synthetic",
            "Finite SYNTHETIC_NOT_HUMAN fault fixtures only.",
        )
    )
    exp036 = fixture_results["EXP-036"]
    for metric_id, key in (
        ("ARCH_TARGET_UNIFIED_P95_RATIO", "unifiedP95RatioMaximum"),
        ("ARCH_TARGET_UNIFIED_MEMORY_RATIO", "unifiedPeakMemoryRatioMaximum"),
        ("ARCH_TARGET_PARITY_P95_RATIO", "parityP95RatioMaximum"),
    ):
        value = exp036["targets"][key]
        result.append(
            fixture_observation(
                metric_id,
                value,
                None,
                None,
                "maximum ratio target",
                "proposal",
                "Engineering target only; no accepted EXP-036 result exists.",
                "lower_is_better",
            )
        )
    security_controls = [
        security["binaryAudit"],
        security["dependencyAudit"],
        security["privacy"],
        security["secretScan"],
        security["staticAnalysis"],
    ]
    passed_security_controls = sum(
        item["status"] == "PASS" for item in security_controls
    )
    result.append(
        {
            "schemaVersion": "MetricObservation-v1",
            "metricId": "OPS_SECURITY_CONTROLS_PASS",
            "value": passed_security_controls,
            "numerator": passed_security_controls,
            "denominator": len(security_controls),
            "unit": "controls",
            "direction": "target",
            "confidenceInterval": None,
            "sourcePath": SECURITY.relative_to(ROOT).as_posix(),
            "sourceSha256": sha256(SECURITY),
            "evidenceClass": "mechanism",
            "observationDate": program["generatedAt"][:10],
            "cohortHash": None,
            "metricSchemaVersion": "1.0",
            "claimBoundary": (
                "Recorded reproducible control status; not a guarantee that no "
                "future vulnerability exists."
            ),
        }
    )
    return result


def suite_envelopes(
    program: dict[str, Any],
    source_revision: str,
    architecture_fixtures: dict[str, Any],
    baseline: dict[str, Any],
) -> list[dict[str, Any]]:
    source_path = PROGRAM.relative_to(ROOT).as_posix()
    source_digest = sha256(PROGRAM)
    envelopes: list[dict[str, Any]] = []
    for suite_name, experiment_ids, evidence in (
        (
            "replaySuite",
            program["replaySuite"]["experiments"],
            "offline",
        ),
        (
            "conformanceSuite",
            program["conformanceSuite"]["experiments"],
            "offline",
        ),
    ):
        suite = program[suite_name]
        for experiment_id in experiment_ids:
            envelopes.append(
                {
                    "schemaVersion": "ExperimentRunEnvelope-v1",
                    "experimentId": experiment_id,
                    "runId": suite["runId"],
                    "manifestSchema": "ProgramStatusSnapshot-v1",
                    "manifestPath": source_path,
                    "manifestSha256": source_digest,
                    "acceptanceStatus": "accepted",
                    "acceptedAt": program["generatedAt"],
                    "evidenceClass": evidence,
                    "sourceRevision": source_revision,
                    "inputHashes": {},
                    "outputHashes": {"normalized": suite["normalizedSha256"]},
                    "metricObservationIds": [],
                    "comparisonContext": {
                        "datasetHash": suite["normalizedSha256"],
                        "partitionHash": "not_applicable",
                        "baselineRevision": baseline["officialTagCommit"],
                        "policyVersion": "offline-suite-v1",
                        "promptVersion": "not_applicable",
                        "modelIdentifier": "not_applicable",
                        "metricSchemaVersion": "1.0",
                        "labelEligibility": "not_applicable",
                        "leakageClass": "not_applicable",
                        "evidenceClass": evidence,
                    },
                }
            )
    accepted_dir = ROOT / "experiments" / "accepted-runs"
    if accepted_dir.is_dir():
        for path in sorted(accepted_dir.glob("*.json")):
            payload = load_json(path)
            if payload.get("schemaVersion") == "ExperimentRunEnvelope-v1":
                envelopes.append(payload)
    fixture_path = ARCHITECTURE_FIXTURES.relative_to(ROOT).as_posix()
    fixture_manifest_hash = sha256(ARCHITECTURE_FIXTURES)
    fixture_metric_ids = {
        "EXP-033": [
            "ARCH_FIXTURE_SEMANTIC_DIFFERENCES",
            "ARCH_FIXTURE_REPLAY_DETERMINISM",
        ],
        "EXP-034": ["TOPOLOGY_CONTRACT_EQUIVALENCE"],
        "EXP-035": ["SAFETY_FAULT_CASES_PASS"],
    }
    for result in architecture_fixtures["experiments"]:
        experiment_id = result["experimentId"]
        if experiment_id not in fixture_metric_ids:
            continue
        result_hash = canonical_sha256(result)
        envelopes.append(
            {
                "schemaVersion": "ExperimentRunEnvelope-v1",
                "experimentId": experiment_id,
                "runId": f"BIGUI-{experiment_id}-{result_hash[:12]}",
                "manifestSchema": "BigUIArchitectureFixtureResults-v1",
                "manifestPath": fixture_path,
                "manifestSha256": fixture_manifest_hash,
                "acceptanceStatus": "accepted",
                "acceptedAt": architecture_fixtures["generatedAt"],
                "evidenceClass": (
                    "synthetic" if experiment_id == "EXP-035" else "offline"
                ),
                "sourceRevision": source_revision,
                "inputHashes": architecture_fixtures["sources"],
                "outputHashes": {"result": result_hash},
                "metricObservationIds": fixture_metric_ids[experiment_id],
                "comparisonContext": {
                    "datasetHash": result_hash,
                    "partitionHash": "not_applicable",
                    "baselineRevision": baseline["officialTagCommit"],
                    "policyVersion": "architecture-fixture-v1",
                    "promptVersion": "not_applicable",
                    "modelIdentifier": "not_applicable",
                    "metricSchemaVersion": "1.0",
                    "labelEligibility": "not_applicable",
                    "leakageClass": (
                        "synthetic_fixture"
                        if experiment_id == "EXP-035"
                        else "not_applicable"
                    ),
                    "evidenceClass": (
                        "synthetic" if experiment_id == "EXP-035" else "offline"
                    ),
                },
            }
        )
    return envelopes


def sources() -> list[dict[str, str]]:
    return [
        {
            "id": "experiment-registry",
            "path": REGISTRY.relative_to(ROOT).as_posix(),
            "sha256": sha256(REGISTRY),
            "role": "Experiment titles, status narratives, and artifact references",
        },
        {
            "id": "program-status",
            "path": PROGRAM.relative_to(ROOT).as_posix(),
            "sha256": sha256(PROGRAM),
            "role": "Accepted iteration, gates, decisions, and verification state",
        },
        {
            "id": "thesis-evidence",
            "path": THESIS.relative_to(ROOT).as_posix(),
            "sha256": sha256(THESIS),
            "role": "Mechanism counts, B0–B5 evidence ladder, and claim gates",
        },
        {
            "id": "bigui-program",
            "path": BIGUI_PROGRAM.relative_to(ROOT).as_posix(),
            "sha256": sha256(BIGUI_PROGRAM),
            "role": "EXP-030–EXP-040 protocols and metadata",
        },
        {
            "id": "baseline-lock",
            "path": BASELINE.relative_to(ROOT).as_posix(),
            "sha256": sha256(BASELINE),
            "role": "Frozen baseline and Agent 4 provenance",
        },
        {
            "id": "security-posture",
            "path": SECURITY.relative_to(ROOT).as_posix(),
            "sha256": sha256(SECURITY),
            "role": "Reproducible security and privacy status",
        },
        {
            "id": "architecture-fixtures",
            "path": ARCHITECTURE_FIXTURES.relative_to(ROOT).as_posix(),
            "sha256": sha256(ARCHITECTURE_FIXTURES),
            "role": "Clone-safe EXP-033–EXP-035 fixture results and EXP-036 gate",
        },
        {
            "id": "paper-baseline",
            "path": PAPER_BASELINE.relative_to(ROOT).as_posix(),
            "sha256": sha256(PAPER_BASELINE),
            "role": "Reviewed paper-reported baseline values and comparison boundary",
        },
        {
            "id": "baseline-comparison",
            "path": BASELINE_COMPARISON.relative_to(ROOT).as_posix(),
            "sha256": sha256(BASELINE_COMPARISON),
            "role": "EXP-037–EXP-040 baseline, comparison, and thesis-readiness results",
        },
        {
            "id": "experiment-evaluation-standard",
            "path": EVALUATION_STANDARD.relative_to(ROOT).as_posix(),
            "sha256": sha256(EVALUATION_STANDARD),
            "role": "Canonical evaluation dimensions, baselines, parameters, gates, and statistical rules",
        },
        {
            "id": "experiment-benchmark",
            "path": EXPERIMENT_BENCHMARK.relative_to(ROOT).as_posix(),
            "sha256": sha256(EXPERIMENT_BENCHMARK),
            "role": "All-experiment evaluation records, program analytics, findings, and recommendations",
        },
        {
            "id": "current-run-index",
            "path": CURRENT_RUN_INDEX.relative_to(ROOT).as_posix(),
            "sha256": sha256(CURRENT_RUN_INDEX),
            "role": "Current accepted projection for each executed experiment; older bundles remain history",
        },
    ]


def recorded_source_revision() -> str | None:
    if not CATALOG_OUTPUT.is_file():
        return None
    try:
        value = load_json(CATALOG_OUTPUT).get("sourceRevision")
    except (OSError, json.JSONDecodeError):
        return None
    return value if isinstance(value, str) and re.fullmatch(r"[0-9a-f]{40}", value) else None


def build_catalog(
    tier: str = "tracked_sanitized",
    source_revision: str | None = None,
    validate_benchmark: bool = True,
) -> dict[str, Any]:
    registry = parse_registry()
    program = load_json(PROGRAM)
    thesis = load_json(THESIS)
    bigui_program = load_json(BIGUI_PROGRAM)
    baseline = load_json(BASELINE)
    security = load_json(SECURITY)
    architecture_fixtures = load_json(ARCHITECTURE_FIXTURES)
    paper_baseline = load_json(PAPER_BASELINE)
    baseline_comparison = load_json(BASELINE_COMPARISON)
    evaluation_standard = load_json(EVALUATION_STANDARD)
    experiment_benchmark = load_json(EXPERIMENT_BENCHMARK)
    current_run_index = load_json(CURRENT_RUN_INDEX)
    custom = {item["id"]: item for item in bigui_program["experiments"]}
    source_revision = (
        source_revision or recorded_source_revision() or program["sourceRevision"]
    )
    if not re.fullmatch(r"[0-9a-f]{40}", source_revision):
        raise ValueError("source revision must contain 40 lowercase hexadecimal characters")
    metrics = metric_observations(
        thesis, program, baseline, architecture_fixtures, security
    )
    loaded_bundles = load_bundles(ACCEPTED_RUNS_DIR, ROOT / "schemas")
    run_bundles = []
    for loaded_bundle in loaded_bundles:
        run_bundles.append(
            {
                key: value
                for key, value in loaded_bundle.items()
                if not key.startswith("_")
            }
        )
    run_summary = run_store_summary(run_bundles)
    metric_definitions_v2: dict[str, dict[str, Any]] = {}
    metric_observations_v2: list[dict[str, Any]] = []
    bundles_by_identity: dict[tuple[str, str], dict[str, Any]] = {}
    for bundle in run_bundles:
        envelope = bundle["envelope"]
        bundles_by_identity[
            (envelope["experimentId"], envelope["runId"])
        ] = bundle
        for definition in bundle["metricDefinitions"]:
            key = canonical_sha256(definition)
            metric_definitions_v2[key] = definition
        metric_observations_v2.extend(bundle["metricObservations"])
    latest_bundle_by_experiment: dict[str, dict[str, Any]] = {}
    for current_run in current_run_index["currentRuns"]:
        key = (current_run["experimentId"], current_run["runId"])
        bundle = bundles_by_identity.get(key)
        if bundle is None:
            raise ValueError(
                "current run index points to a missing accepted bundle: "
                f"{current_run['experimentId']} {current_run['runId']}"
            )
        if (
            bundle["envelope"]["manifestSha256"]
            != current_run["manifestSha256"]
        ):
            raise ValueError(
                "current run index manifest hash mismatch: "
                f"{current_run['experimentId']} {current_run['runId']}"
            )
        latest_bundle_by_experiment[current_run["experimentId"]] = bundle
    metric_ids = {item["metricId"] for item in metrics}
    runs = suite_envelopes(
        program, source_revision, architecture_fixtures, baseline
    )
    run_ids_by_experiment: dict[str, list[str]] = {}
    for run in runs:
        run_ids_by_experiment.setdefault(run["experimentId"], []).append(run["runId"])

    experiments: list[dict[str, Any]] = []
    for index in range(41):
        experiment_id = f"EXP-{index:03d}"
        row = registry[experiment_id]
        if experiment_id in custom:
            item = dict(custom[experiment_id])
            item.pop("datasetHash", None)
            item.pop("partitionHash", None)
        else:
            status = program["experimentStates"].get(experiment_id)
            if status is None:
                raise ValueError(f"{experiment_id} has no canonical status")
            if status not in STATUS_VOCABULARY:
                raise ValueError(f"{experiment_id} uses unsupported status {status!r}")
            evidence = evidence_class(experiment_id, status)
            baseline_name, comparator = baseline_and_comparator(index)
            item = {
                "id": experiment_id,
                "title": row["title"],
                "researchSpace": research_space(index),
                "researchTrack": research_track(index),
                "researchQuestion": row["researchQuestion"],
                "status": status,
                "evidenceClass": evidence,
                "architectureTargets": architecture_targets(index),
                "prerequisites": DEPENDENCIES.get(experiment_id, []),
                "approvalGates": APPROVAL_GATES.get(experiment_id, []),
                "baseline": baseline_name,
                "comparator": comparator,
                "metricDefinitions": experiment_metrics(index),
                "claimBoundary": claim_boundary(experiment_id, evidence),
                "validityThreats": [
                    "Evidence class and cohort limits must remain visible."
                ],
                "owner": (
                    "Human reviewers"
                    if status == "Pending expert input"
                    else "Research program"
                ),
                "nextAction": row["notes"],
                "artifactLinks": [
                    (experiment_directory(experiment_id) / "README.md")
                    .relative_to(ROOT)
                    .as_posix()
                ],
            }
        item["datasetHash"] = None
        item["partitionHash"] = None
        v2_run_ids = sorted(
            {
                bundle["envelope"]["runId"]
                for bundle in run_bundles
                if bundle["envelope"]["experimentId"] == experiment_id
            }
        )
        item["acceptedRunIds"] = (
            v2_run_ids
            if v2_run_ids
            else sorted(set(run_ids_by_experiment.get(experiment_id, [])))
        )
        relevant_metric_ids = [
            metric_id
            for metric_id in item["metricDefinitions"]
            if metric_id in metric_ids
        ]
        if experiment_id == "EXP-001":
            relevant_metric_ids = [
                "MECH_COMPARISON_ROWS",
                "SAFETY_CLASSIFICATION_CHANGES",
            ]
        elif experiment_id == "EXP-005":
            relevant_metric_ids = ["LABEL_CANDIDATES", "LABEL_GENERALIZATION_SAFE"]
        elif experiment_id == "EXP-012":
            relevant_metric_ids = [
                "CLASSIFICATION_ACCURACY_B0",
                "CLASSIFICATION_MACRO_F1_B0",
            ]
        elif experiment_id == "EXP-033":
            relevant_metric_ids = [
                "ARCH_FIXTURE_SEMANTIC_DIFFERENCES",
                "ARCH_FIXTURE_REPLAY_DETERMINISM",
            ]
        elif experiment_id == "EXP-034":
            relevant_metric_ids = sorted(
                metric_id
                for metric_id in metric_ids
                if metric_id.startswith("TOPOLOGY_")
            )
        elif experiment_id == "EXP-035":
            relevant_metric_ids = ["SAFETY_FAULT_CASES_PASS"]
        elif experiment_id == "EXP-036":
            relevant_metric_ids = sorted(
                metric_id
                for metric_id in metric_ids
                if metric_id.startswith("ARCH_TARGET_")
            )
        latest_bundle = latest_bundle_by_experiment.get(experiment_id)
        item["latestResult"] = (
            {
                "summary": row["notes"],
                "metricObservationIds": (
                    latest_bundle["envelope"]["metricObservationIds"]
                    if latest_bundle
                    else relevant_metric_ids
                ),
            }
            if item["acceptedRunIds"] or relevant_metric_ids
            else None
        )
        experiments.append(item)

    generated_at = max(
        datetime.fromisoformat(program["generatedAt"].replace("Z", "+00:00")),
        datetime.fromisoformat(thesis["generatedAt"].replace("Z", "+00:00")),
        datetime.fromisoformat(bigui_program["generatedAt"].replace("Z", "+00:00")),
        datetime.fromisoformat(
            evaluation_standard["generatedAt"].replace("Z", "+00:00")
        ),
        datetime.fromisoformat(
            experiment_benchmark["generatedAt"].replace("Z", "+00:00")
        ),
    ).isoformat()
    catalog = {
        "schemaVersion": "ExperimentCatalogSnapshot-v1",
        "generatedAt": generated_at,
        "sourceRevision": source_revision,
        "publicationTier": tier,
        "programState": {
            "latestAcceptedIteration": program["latestAcceptedIteration"]["iteration"],
            "iterationVerdict": program["latestAcceptedIteration"]["verdict"],
            "candidateLabels": program["exp005Gate"]["candidateRows"],
            "safeLabels": program["exp005Gate"]["generalizationSafeValidLabels"],
            "accuracyStatus": program["exp012Gate"]["result"],
            "comparisonRows": thesis["evidence"]["comparisonRows"]["value"],
            "classificationChanges": thesis["evidence"]["memoryInformedChanges"]["value"],
            "baselineFrozen": True,
            "decisionState": {
                key: program["decisionState"][key]
                for key in ("M-02", "M-03", "M-04", "M-05")
            },
        },
        "architectureVariants": architecture_variants(),
        "paperBaseline": paper_baseline,
        "baselineComparisonResults": baseline_comparison,
        "evaluationStandard": evaluation_standard,
        "experimentBenchmark": experiment_benchmark,
        "experiments": experiments,
        "metricObservations": metrics,
        "metricDefinitionsV2": sorted(
            metric_definitions_v2.values(),
            key=lambda item: item["metricId"],
        ),
        "metricObservationsV2": sorted(
            metric_observations_v2,
            key=lambda item: (
                item["experimentId"],
                item["runId"],
                item["metricId"],
                item["observationId"],
            ),
        ),
        "comparisonRules": {
            "requiredMatchingFields": [
                "datasetHash",
                "partitionHash",
                "baselineRevision",
                "policyVersion",
                "promptVersion",
                "modelIdentifier",
                "metricSchemaVersion",
                "labelEligibility",
                "leakageClass",
                "evidenceClass",
            ],
            "incomparableLabel": "Not directly comparable",
            "seriesIsolation": "Synthetic and empirical observations remain separate.",
        },
        "acceptedRuns": runs,
        "acceptedRunBundles": run_bundles,
        "currentRunIndex": current_run_index,
        "runStoreSummary": run_summary,
        "claimBoundaries": {
            "safeNow": thesis["claimGates"]["safeNow"],
            "conditional": (
                thesis["claimGates"]["conditionalAfterLabels"]
                + thesis["claimGates"]["formalImprovement"]
            ),
            "notAllowed": thesis["claimGates"]["notAllowed"],
        },
        "translations": {
            "en": {
                "title": "VEGO-AI Research Observatory",
                "blocked": "Blocked",
                "notComputable": "Not yet computable",
                "notComparable": "Not directly comparable",
            },
            "he": {
                "title": "מצפה המחקר של VEGO-AI",
                "blocked": "חסום",
                "notComputable": "עדיין לא ניתן לחישוב",
                "notComparable": "לא ניתן להשוואה ישירה",
            },
        },
        "sources": sources(),
    }
    validate_catalog(catalog, validate_benchmark=validate_benchmark)
    return catalog


def validate_catalog(
    catalog: dict[str, Any],
    *,
    validate_benchmark: bool = True,
) -> None:
    format_checker = jsonschema.FormatChecker()
    jsonschema.Draft202012Validator(
        load_json(CATALOG_SCHEMA), format_checker=format_checker
    ).validate(catalog)
    metric_validator = jsonschema.Draft202012Validator(
        load_json(METRIC_SCHEMA), format_checker=format_checker
    )
    for metric in catalog["metricObservations"]:
        metric_validator.validate(metric)
    metric_definition_v2_validator = jsonschema.Draft202012Validator(
        load_json(METRIC_DEFINITION_V2_SCHEMA), format_checker=format_checker
    )
    for definition in catalog["metricDefinitionsV2"]:
        metric_definition_v2_validator.validate(definition)
    metric_v2_validator = jsonschema.Draft202012Validator(
        load_json(METRIC_V2_SCHEMA), format_checker=format_checker
    )
    for metric in catalog["metricObservationsV2"]:
        metric_v2_validator.validate(metric)
    # Accepted bundles were already validated with a local schema registry by
    # load_bundles(). Avoid a second bare jsonschema pass here because relative
    # references would otherwise attempt an online lookup.
    run_validator = jsonschema.Draft202012Validator(
        load_json(RUN_SCHEMA), format_checker=format_checker
    )
    for run in catalog["acceptedRuns"]:
        run_validator.validate(run)
    architecture_validator = jsonschema.Draft202012Validator(
        load_json(ARCHITECTURE_SCHEMA), format_checker=format_checker
    )
    for variant in catalog["architectureVariants"]:
        architecture_validator.validate(variant)
    jsonschema.Draft202012Validator(
        load_json(PAPER_BASELINE_SCHEMA), format_checker=format_checker
    ).validate(catalog["paperBaseline"])
    jsonschema.Draft202012Validator(
        load_json(BASELINE_COMPARISON_SCHEMA), format_checker=format_checker
    ).validate(catalog["baselineComparisonResults"])
    jsonschema.Draft202012Validator(
        load_json(EVALUATION_STANDARD_SCHEMA),
        format_checker=format_checker,
    ).validate(catalog["evaluationStandard"])
    if validate_benchmark:
        jsonschema.Draft202012Validator(
            load_json(EXPERIMENT_BENCHMARK_SCHEMA),
            format_checker=format_checker,
        ).validate(catalog["experimentBenchmark"])

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
    if (
        validate_benchmark
        and canonical_sha256(core_projection)
        != catalog["experimentBenchmark"]["inputProjectionSha256"]
    ):
        raise ValueError(
            "experiment benchmark is stale against the catalog core projection"
        )

    ids = [item["id"] for item in catalog["experiments"]]
    expected = [f"EXP-{index:03d}" for index in range(41)]
    if ids != expected:
        raise ValueError("experiments must be ordered and complete from EXP-000 to EXP-040")
    metric_ids = [item["metricId"] for item in catalog["metricObservations"]]
    if len(metric_ids) != len(set(metric_ids)):
        raise ValueError("metric IDs must be unique")
    if catalog["programState"]["safeLabels"] == 0:
        for metric in [
            *catalog["metricObservations"],
            *catalog["metricObservationsV2"],
        ]:
            if metric["metricId"].startswith(("CLASSIFICATION_", "PAIRED_")):
                if metric["value"] is not None:
                    raise ValueError(
                        f"{metric['metricId']} must be null at safe N=0"
                    )
    serialized = json.dumps(catalog, ensure_ascii=False)
    for forbidden in ("file:///", "C:\\\\Users\\\\", "@gmail.com", "@outlook.com"):
        if forbidden.lower() in serialized.lower():
            raise ValueError(f"tracked catalog contains forbidden private text: {forbidden}")
    for source in catalog["sources"]:
        path = ROOT / source["path"]
        if not path.is_file() or sha256(path) != source["sha256"]:
            raise ValueError(f"source hash mismatch: {source['path']}")
    observation_ids = [
        item["observationId"] for item in catalog["metricObservationsV2"]
    ]
    if len(observation_ids) != len(set(observation_ids)):
        raise ValueError("v2 metric observation IDs must be unique")
    if catalog["runStoreSummary"] != run_store_summary(
        catalog["acceptedRunBundles"]
    ):
        raise ValueError("run-store summary does not match accepted bundles")
    jsonschema.Draft202012Validator(
        load_json(CURRENT_RUN_INDEX_SCHEMA),
        format_checker=format_checker,
    ).validate(catalog["currentRunIndex"])
    known_ids = set(ids)
    for item in catalog["experiments"]:
        for dependency in item["prerequisites"]:
            if re.fullmatch(r"EXP-[0-9]{3}", dependency) and dependency not in known_ids:
                raise ValueError(f"{item['id']} references unknown {dependency}")
        for artifact in item["artifactLinks"]:
            if not (ROOT / artifact).is_file():
                raise ValueError(f"{item['id']} artifact does not exist: {artifact}")


def artifact_payloads(catalog: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    status_rows: list[dict[str, Any]] = []
    for item in catalog["experiments"]:
        status_rows.append(
            {
                "experiment_id": item["id"],
                "title": item["title"],
                "research_space": item["researchSpace"],
                "track": item["researchTrack"],
                "status": item["status"],
                "evidence_class": item["evidenceClass"],
                "accepted_runs": len(item["acceptedRunIds"]),
                "claim_boundary": item["claimBoundary"],
                "next_action": item["nextAction"],
            }
        )
    evidence_counts: dict[str, int] = {}
    for row in status_rows:
        evidence_counts[row["evidence_class"]] = (
            evidence_counts.get(row["evidence_class"], 0) + 1
        )
    evidence_rows = [
        {"evidence_class": key, "experiment_count": value}
        for key, value in sorted(evidence_counts.items())
    ]
    manifest = {
        "version": 1,
        "surface": "dashboard",
        "title": "VEGO-AI BigUI Research Observatory",
        "description": "Catalog-driven research, architecture, and evidence status.",
        "generatedAt": catalog["generatedAt"],
        "blocks": [
            {"type": "markdown", "id": "intro", "body": "# VEGO-AI BigUI Research Observatory\n\nMechanism evidence and empirical validity are kept separate. Accuracy remains not computable at 0/24 safe labels."},
            {
                "type": "metric-strip",
                "id": "program-state",
                "cardIds": [
                    "iteration-card",
                    "label-card",
                    "classification-card"
                ]
            },
            {"type": "chart", "id": "evidence-chart-block", "chartId": "evidence-chart"},
            {"type": "table", "id": "experiment-table-block", "tableId": "experiment-table"}
        ],
        "cards": [
            {
                "id": "iteration-card",
                "dataset": "program_state",
                "sourceId": "program-status",
                "metrics": [
                    {
                        "label": "Accepted iteration",
                        "field": "accepted_iteration",
                        "format": "number"
                    }
                ]
            },
            {
                "id": "label-card",
                "dataset": "program_state",
                "sourceId": "program-status",
                "metrics": [
                    {
                        "label": "Safe labels",
                        "field": "safe_labels",
                        "format": "number"
                    },
                    {
                        "label": "Candidate rows",
                        "field": "candidate_labels",
                        "format": "number"
                    }
                ]
            },
            {
                "id": "classification-card",
                "dataset": "program_state",
                "sourceId": "thesis-evidence",
                "metrics": [
                    {
                        "label": "Classification changes",
                        "field": "classification_changes",
                        "format": "number"
                    },
                    {
                        "label": "Comparison rows",
                        "field": "comparison_rows",
                        "format": "number"
                    }
                ]
            }
        ],
        "charts": [
            {
                "id": "evidence-chart",
                "title": "Registered experiments by evidence class",
                "dataset": "evidence_counts",
                "sourceId": "experiment-registry",
                "type": "bar",
                "encodings": {
                    "x": {"field": "evidence_class", "type": "nominal"},
                    "y": {"field": "experiment_count", "type": "quantitative"}
                }
            }
        ],
        "tables": [
            {
                "id": "experiment-table",
                "title": "Experiment catalog",
                "dataset": "experiments",
                "sourceId": "experiment-registry",
                "columns": [
                    {"field": "experiment_id", "label": "ID"},
                    {"field": "title", "label": "Experiment"},
                    {"field": "research_space", "label": "Space"},
                    {"field": "status", "label": "Status"},
                    {"field": "evidence_class", "label": "Evidence"},
                    {"field": "accepted_runs", "label": "Accepted runs"}
                ],
                "defaultSort": {"field": "experiment_id", "direction": "asc"}
            }
        ],
        "sources": [
            {
                "id": source["id"],
                "label": source["role"],
                "path": source["path"],
                "query": {
                    "language": "sql",
                    "description": (
                        "Read the normalized BigUI artifact snapshot derived "
                        f"from {source['path']}."
                    ),
                    "sql": (
                        "SELECT * FROM program_state;"
                        if source["id"] in {"program-status", "thesis-evidence"}
                        else "SELECT * FROM experiments;"
                    ),
                    "tables_used": [
                        "program_state"
                        if source["id"] in {"program-status", "thesis-evidence"}
                        else "experiments"
                    ]
                }
            }
            for source in catalog["sources"]
        ]
    }
    snapshot = {
        "version": 1,
        "status": "ready",
        "generatedAt": catalog["generatedAt"],
        "datasets": {
            "program_state": [
                {
                    "accepted_iteration": catalog["programState"]["latestAcceptedIteration"],
                    "candidate_labels": catalog["programState"]["candidateLabels"],
                    "safe_labels": catalog["programState"]["safeLabels"],
                    "comparison_rows": catalog["programState"]["comparisonRows"],
                    "classification_changes": catalog["programState"]["classificationChanges"]
                }
            ],
            "experiments": status_rows,
            "evidence_counts": evidence_rows
        }
    }
    return manifest, snapshot


def write_or_check(path: Path, payload: dict[str, Any], check: bool) -> bool:
    content = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
    if check:
        if not path.is_file() or path.read_text(encoding="utf-8") != content:
            print(f"STALE: {path.relative_to(ROOT)}", file=sys.stderr)
            return False
        return True
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="\n")
    print(f"WROTE: {path.relative_to(ROOT)}")
    return True


def write_controlled(catalog: dict[str, Any], output: Path) -> None:
    if not output.is_absolute():
        output = ROOT / output
    output = output.resolve()
    generated_root = (ROOT / "reports" / "generated").resolve()
    if generated_root not in output.parents:
        raise ValueError("controlled BigUI output must stay under reports/generated")
    controlled = json.loads(json.dumps(catalog))
    controlled["publicationTier"] = "controlled_local"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(controlled, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(f"WROTE CONTROLLED: {output.relative_to(ROOT)}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    parser.add_argument(
        "--source-revision",
        help=(
            "Clean canonical-source commit used for a refresh. Checks preserve "
            "the revision already recorded in the tracked catalog."
        ),
    )
    parser.add_argument(
        "--controlled-output",
        type=Path,
        default=None,
        help="Optional ignored local catalog under reports/generated.",
    )
    args = parser.parse_args()
    if args.check and args.controlled_output:
        parser.error("--check cannot refresh a controlled output")
    if args.check and args.source_revision:
        parser.error("--check uses the source revision recorded in the catalog")
    try:
        catalog = build_catalog(source_revision=args.source_revision)
        manifest, snapshot = artifact_payloads(catalog)
        outputs = (
            (CATALOG_OUTPUT, catalog),
            (ARTIFACT_MANIFEST_OUTPUT, manifest),
            (ARTIFACT_SNAPSHOT_OUTPUT, snapshot),
        )
        ok = all(write_or_check(path, payload, args.check) for path, payload in outputs)
        if args.controlled_output:
            write_controlled(catalog, args.controlled_output)
    except (OSError, ValueError, json.JSONDecodeError, jsonschema.ValidationError) as exc:
        print(f"BigUI catalog: FAIL: {exc}", file=sys.stderr)
        return 1
    if args.check and ok:
        print("BigUI catalog: PASS")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
