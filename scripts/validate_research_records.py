#!/usr/bin/env python3
"""Validate thesis research records against schemas and cross-field invariants."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import jsonschema
from referencing import Registry, Resource

ROOT = Path(__file__).resolve().parents[1]
SCHEMAS = {
    "GoldLabelRecord-v2": ROOT / "schemas/gold-label-record-v2.schema.json",
    "EvaluationRunManifest-v2": ROOT
    / "schemas/evaluation-run-manifest-v2.schema.json",
    "PolicyCandidateRecord-v1": ROOT
    / "schemas/policy-candidate-record-v1.schema.json",
    "ArchitectureRunManifest": ROOT
    / "schemas/architecture-run-manifest-v1.schema.json",
    "BaselineLockManifest-v2": ROOT
    / "schemas/baseline-lock-manifest-v2.schema.json",
    "model-execution-manifest-v1": ROOT
    / "schemas/model-execution-manifest-v1.schema.json",
    "ReleaseManifest-v3": ROOT / "schemas/release-manifest-v3.schema.json",
    "SecurityPostureSnapshot-v1": ROOT
    / "schemas/security-posture-snapshot-v1.schema.json",
    "HLayerIterationManifest-v1": ROOT
    / "schemas/hlayer-iteration-manifest-v1.schema.json",
    "MetricObservation-v1": ROOT / "schemas/metric-observation-v1.schema.json",
    "MetricObservation-v2": ROOT / "schemas/metric-observation-v2.schema.json",
    "MetricDefinition-v1": ROOT / "schemas/metric-definition-v1.schema.json",
    "ExperimentRunEnvelope-v1": ROOT
    / "schemas/experiment-run-envelope-v1.schema.json",
    "ExperimentRunEnvelope-v2": ROOT
    / "schemas/experiment-run-envelope-v2.schema.json",
    "ExperimentEvaluation-v1": ROOT
    / "schemas/experiment-evaluation-v1.schema.json",
    "RunAcceptanceRecord-v1": ROOT
    / "schemas/run-acceptance-record-v1.schema.json",
    "AcceptedExperimentRunBundle-v1": ROOT
    / "schemas/accepted-experiment-run-bundle-v1.schema.json",
    "ArchitectureVariant-v1": ROOT
    / "schemas/architecture-variant-v1.schema.json",
    "ComparisonEligibility-v1": ROOT
    / "schemas/comparison-eligibility-v1.schema.json",
    "BigUIStudyRecord-v1": ROOT / "schemas/bigui-study-record-v1.schema.json",
    "ExperimentCatalogSnapshot-v1": ROOT
    / "schemas/experiment-catalog-snapshot-v1.schema.json",
    "ExperimentDefinition-v3": ROOT
    / "schemas/experiment-definition-v3.schema.json",
    "ReviewPolicySignalContract-v1": ROOT
    / "schemas/review-policy-signal-contract-v1.schema.json",
    "GovernedJudgmentRecord-v1": ROOT
    / "schemas/governed-judgment-record-v1.schema.json",
    "ReuseDecisionRecord-v1": ROOT
    / "schemas/reuse-decision-record-v1.schema.json",
}

_ALL_SCHEMA_DOCUMENTS = [
    json.loads(path.read_text(encoding="utf-8"))
    for path in sorted((ROOT / "schemas").glob("*.schema.json"))
]
_SCHEMA_REGISTRY = Registry().with_resources(
    [
        (schema["$id"], Resource.from_contents(schema))
        for schema in _ALL_SCHEMA_DOCUMENTS
        if "$id" in schema
    ]
)


def schema_errors(record: dict[str, Any], version: str) -> list[str]:
    schema_path = SCHEMAS[version]
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    validator = jsonschema.Draft202012Validator(
        schema,
        registry=_SCHEMA_REGISTRY,
        format_checker=jsonschema.FormatChecker(),
    )
    return [
        (
            ".".join(str(part) for part in issue.absolute_path) or "<root>"
        )
        + f": {issue.message}"
        for issue in sorted(validator.iter_errors(record), key=lambda item: list(item.path))
    ]


def semantic_errors(record: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    version = record.get("schemaVersion")
    if version == "EvaluationRunManifest-v2":
        counts = record["labelStats"]
        ordered = [
            counts["generalizationSafeLabels"],
            counts["validLabels"],
            counts["suppliedLabels"],
            counts["candidateRows"],
        ]
        if ordered != sorted(ordered):
            errors.append(
                "label counts must satisfy generalizationSafeLabels <= "
                "validLabels <= suppliedLabels <= candidateRows"
            )
        if counts["adjudicatedRows"] > counts["validLabels"]:
            errors.append("adjudicatedRows cannot exceed validLabels")
        if counts["validLabels"] > 0 and counts["reviewerCount"] < 2:
            errors.append("valid empirical labels require at least two reviewers")
    elif version == "PolicyCandidateRecord-v1":
        rule_ids = [rule["ruleId"] for rule in record["deterministicRules"]]
        if len(rule_ids) != len(set(rule_ids)):
            errors.append("deterministicRules must have unique ruleId values")
    elif version == "GoldLabelRecord-v2":
        if (
            record["recordType"] == "adjudicated_gold"
            and record["recordId"] in record["rawReviewRecordIds"]
        ):
            errors.append("an adjudicated record cannot reference itself")
    elif version == "MetricObservation-v1":
        interval = record["confidenceInterval"]
        if interval is not None and interval["lower"] > interval["upper"]:
            errors.append("confidenceInterval lower cannot exceed upper")
    elif version == "ExperimentRunEnvelope-v1":
        if record["acceptanceStatus"] != "accepted" and record["acceptedAt"] is not None:
            errors.append("only accepted runs may have acceptedAt")
    elif version == "ComparisonEligibility-v1":
        fields = [check["field"] for check in record["checks"]]
        if len(fields) != len(set(fields)):
            errors.append("comparison checks must use each field at most once")
        mismatches = [check for check in record["checks"] if not check["matches"]]
        if record["eligible"] and mismatches:
            errors.append("eligible comparisons cannot contain mismatched checks")
        if not record["eligible"] and not mismatches:
            errors.append("ineligible comparisons must contain a mismatched check")
    elif version == "ExperimentCatalogSnapshot-v1":
        experiment_ids = [item["id"] for item in record["experiments"]]
        expected_ids = [f"EXP-{index:03d}" for index in range(41)]
        if experiment_ids != expected_ids:
            errors.append("experiments must contain EXP-000 through EXP-040 in order")
        metric_ids = [item.get("metricId") for item in record["metricObservations"]]
        if len(metric_ids) != len(set(metric_ids)):
            errors.append("metricObservations must have unique metricId values")
        v2_observation_ids = [
            item.get("observationId")
            for item in record.get("metricObservationsV2", [])
        ]
        if len(v2_observation_ids) != len(set(v2_observation_ids)):
            errors.append(
                "metricObservationsV2 must have unique observationId values"
            )
        run_ids = [item.get("runId") for item in record["acceptedRuns"]]
        bundle_run_ids = [
            item["envelope"].get("runId")
            for item in record.get("acceptedRunBundles", [])
        ]
        run_keys = [
            (item.get("experimentId"), item.get("runId"))
            for item in record["acceptedRuns"]
        ]
        bundle_run_keys = [
            (
                item["envelope"].get("experimentId"),
                item["envelope"].get("runId"),
                item["envelope"].get("attemptId"),
            )
            for item in record.get("acceptedRunBundles", [])
        ]
        if len(run_keys) != len(set(run_keys)):
            errors.append(
                "acceptedRuns must have unique experimentId and runId pairs"
            )
        if len(bundle_run_keys) != len(set(bundle_run_keys)):
            errors.append(
                "acceptedRunBundles must have unique experimentId, runId, and "
                "attemptId tuples"
            )
        nested_groups = [
            ("architectureVariants", "ArchitectureVariant-v1"),
            ("metricObservations", "MetricObservation-v1"),
            ("metricDefinitionsV2", "MetricDefinition-v1"),
            ("metricObservationsV2", "MetricObservation-v2"),
            ("acceptedRuns", "ExperimentRunEnvelope-v1"),
            ("acceptedRunBundles", "AcceptedExperimentRunBundle-v1"),
        ]
        for field, nested_version in nested_groups:
            for index, nested_record in enumerate(record[field]):
                for nested_error in schema_errors(nested_record, nested_version):
                    errors.append(f"{field}.{index}: {nested_error}")
                for nested_error in semantic_errors(nested_record):
                    errors.append(f"{field}.{index}: {nested_error}")

        known_metrics = set(metric_ids) | set(v2_observation_ids)
        known_runs = set(run_ids) | set(bundle_run_ids)
        for experiment in record["experiments"]:
            missing_runs = sorted(set(experiment["acceptedRunIds"]) - known_runs)
            if missing_runs:
                errors.append(
                    f"{experiment['id']} references unknown accepted runs: "
                    + ", ".join(missing_runs)
                )
            latest = experiment["latestResult"]
            if latest is not None:
                missing_metrics = sorted(
                    set(latest["metricObservationIds"]) - known_metrics
                )
                if missing_metrics:
                    errors.append(
                        f"{experiment['id']} references unknown metrics: "
                        + ", ".join(missing_metrics)
                    )
    elif version == "ReviewPolicySignalContract-v1":
        errors.extend(_review_policy_signal_contract_errors(record))
    elif version == "GovernedJudgmentRecord-v1":
        errors.extend(_governed_judgment_record_errors(record))
    elif version == "ReuseDecisionRecord-v1":
        errors.extend(_reuse_decision_record_errors(record))
    return errors


def _review_policy_signal_contract_errors(record: dict[str, Any]) -> list[str]:
    """Cross-field invariants the schema declares but JSON Schema cannot express."""
    errors: list[str] = []
    declared = record.get("declaredSignalSet") or []

    weights = (record.get("combinationRule") or {}).get("weights") or []
    weighted_ids = [weight.get("signalId") for weight in weights]
    for signal_id in sorted(set(weighted_ids) - set(declared)):
        errors.append(
            f"combinationRule.weights references undeclared signalId {signal_id!r}"
        )
    duplicate_weights = sorted(
        {sid for sid in weighted_ids if weighted_ids.count(sid) > 1 and sid is not None}
    )
    for signal_id in duplicate_weights:
        errors.append(f"combinationRule.weights has duplicate signalId {signal_id!r}")

    observations = record.get("signalObservations") or []
    observed_ids = [obs.get("signalId") for obs in observations]
    for signal_id in sorted(set(declared) - set(observed_ids)):
        errors.append(f"declared signal {signal_id!r} has no signalObservations entry")
    duplicate_observed = sorted(
        {sid for sid in observed_ids if observed_ids.count(sid) > 1 and sid is not None}
    )
    for signal_id in duplicate_observed:
        errors.append(f"signalObservations has duplicate signalId {signal_id!r}")

    fragment_id = (record.get("contestedFragment") or {}).get("fragmentId")
    candidates = record.get("reviewerCandidates") or []
    for candidate in candidates:
        candidate_id = candidate.get("candidateId")
        for field in ("assessedCompetence", "assertedAuthority"):
            scoped = (candidate.get(field) or {}).get("fragmentId")
            if scoped is not None and scoped != fragment_id:
                errors.append(
                    f"reviewerCandidates[{candidate_id}].{field}.fragmentId "
                    f"{scoped!r} does not match contestedFragment.fragmentId "
                    f"{fragment_id!r}"
                )

    routing = record.get("routingDecision") or {}
    selected = routing.get("selectedReviewerCandidateId")
    known_candidates = {candidate.get("candidateId") for candidate in candidates}
    if selected is not None and selected not in known_candidates:
        errors.append(
            f"routingDecision.selectedReviewerCandidateId {selected!r} "
            "does not match any reviewerCandidates entry"
        )

    budget_id = (record.get("attentionBudget") or {}).get("budgetId")
    charged_id = (record.get("attentionAccounting") or {}).get("budgetId")
    if budget_id is not None and charged_id is not None and budget_id != charged_id:
        errors.append(
            f"attentionAccounting.budgetId {charged_id!r} does not match "
            f"attentionBudget.budgetId {budget_id!r}"
        )

    arm_version = (record.get("policyArm") or {}).get("policyVersion")
    prov_version = (record.get("provenance") or {}).get("policyVersion")
    if arm_version is not None and prov_version is not None and arm_version != prov_version:
        errors.append(
            f"provenance.policyVersion {prov_version!r} does not match "
            f"policyArm.policyVersion {arm_version!r}"
        )
    return errors


def _governed_judgment_record_errors(record: dict[str, Any]) -> list[str]:
    """Referential invariants across content groups that JSON Schema cannot express.

    Each check is tolerant of absent optional sections: a pair is flagged only
    when both sides are present and inconsistent.
    """
    errors: list[str] = []
    grounding = record.get("caseGrounding") or {}
    grounded_claim = grounding.get("claimId")

    assessed_claim = (record.get("competence") or {}).get("assessedForClaimId")
    if (
        assessed_claim is not None
        and grounded_claim is not None
        and assessed_claim != grounded_claim
    ):
        errors.append(
            f"competence.assessedForClaimId {assessed_claim!r} does not match "
            f"caseGrounding.claimId {grounded_claim!r}"
        )
    mandate_claim = ((record.get("authority") or {}).get("mandate") or {}).get(
        "claimId"
    )
    if (
        mandate_claim is not None
        and grounded_claim is not None
        and mandate_claim != grounded_claim
    ):
        errors.append(
            f"authority.mandate.claimId {mandate_claim!r} does not match "
            f"caseGrounding.claimId {grounded_claim!r}"
        )

    slots = (record.get("decisionTrace") or {}).get("slots") or {}
    declared_evidence = grounding.get("evidence")
    if declared_evidence is not None and slots:
        evidence_ids = {item.get("evidenceId") for item in declared_evidence}
        for slot_name in sorted(slots):
            slot = slots[slot_name] or {}
            referenced = set(slot.get("evidenceIds") or [])
            for evidence_id in sorted(referenced - evidence_ids):
                errors.append(
                    f"decisionTrace.slots.{slot_name} references undeclared "
                    f"evidenceId {evidence_id!r}"
                )

    structure = (record.get("rationale") or {}).get("structure") or []
    if record.get("decisionTrace") is not None and structure:
        slot_ids = {
            slot.get("slotId") for slot in slots.values() if isinstance(slot, dict)
        }
        for entry in structure:
            slot_ref = entry.get("traceSlotRef")
            if slot_ref is not None and slot_ref not in slot_ids:
                errors.append(
                    f"rationale.structure[{entry.get('assertionId')}].traceSlotRef "
                    f"{slot_ref!r} does not match any decisionTrace slotId"
                )

    receipts = record.get("receipts") or {}
    retrieval = receipts.get("retrieval")
    if retrieval is not None:
        retrieval_ids = {receipt.get("receiptId") for receipt in retrieval}
        for use_receipt in receipts.get("use") or []:
            retrieval_ref = use_receipt.get("retrievalReceiptId")
            if retrieval_ref is not None and retrieval_ref not in retrieval_ids:
                errors.append(
                    f"receipts.use[{use_receipt.get('receiptId')}]"
                    f".retrievalReceiptId {retrieval_ref!r} does not match any "
                    "receipts.retrieval receiptId"
                )

    lifecycle = record.get("lifecycle") or {}
    if lifecycle.get("state") == "revoked":
        revocation = lifecycle.get("revocation") or {}
        for field in ("reason", "revokedByAuthorityRef"):
            if revocation.get(field) is None:
                errors.append(
                    "lifecycle.state 'revoked' requires non-null "
                    f"lifecycle.revocation.{field}"
                )
    return errors


def _reuse_decision_record_errors(record: dict[str, Any]) -> list[str]:
    """Keep an outcome receipt from contradicting the decision it receipts."""
    errors: list[str] = []
    decision = record.get("decision") or {}
    receipt = record.get("outcomeReceipt") or {}
    pairs = (
        ("recordedOutcome", "outcome"),
        ("recordedDimensionId", "contextDimensionId"),
    )
    for receipt_field, decision_field in pairs:
        recorded = receipt.get(receipt_field)
        decided = decision.get(decision_field)
        if recorded is not None and decided is not None and recorded != decided:
            errors.append(
                f"outcomeReceipt.{receipt_field} {recorded!r} does not match "
                f"decision.{decision_field} {decided!r}"
            )
    return errors


def validate_record(record: dict[str, Any]) -> list[str]:
    version = (
        record.get("schemaVersion")
        or record.get("contract")
        or record.get("schema_version")
    )
    schema_path = SCHEMAS.get(version)
    if schema_path is None:
        return [f"unsupported schemaVersion: {version!r}"]
    errors = schema_errors(record, version)
    errors.extend(semantic_errors(record))
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("records", nargs="+", type=Path)
    args = parser.parse_args()
    paths: list[Path] = []
    for supplied in args.records:
        if supplied.is_dir():
            paths.extend(
                path
                for path in sorted(supplied.rglob("*.json"))
                if not path.name.endswith(".invalid.json")
                and not path.name.endswith("-fixtures.json")
            )
        else:
            paths.append(supplied)
    failures: list[str] = []
    for path in paths:
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            failures.append(f"{path}: {exc}")
            continue
        records = payload if isinstance(payload, list) else [payload]
        for index, record in enumerate(records):
            for error in validate_record(record):
                failures.append(f"{path}[{index}]: {error}")
    if failures:
        print("research record validation: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("research record validation: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
