#!/usr/bin/env python3
"""Build the evidence-gated thesis status package.

This script creates documentation and machine-readable research interfaces only.
It never reads or writes human labels, never changes VEGO-AI runtime behavior,
and never writes under protected VEGO-AI implementation paths.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PROGRAM_STATUS = ROOT / "docs/research/h-layer/program-status-snapshot-v1.json"
OUTPUT_DIR = ROOT / "docs/research/thesis-evidence"
SNAPSHOT_PATH = OUTPUT_DIR / "thesis-evidence-snapshot-v1.json"
BASELINE_MD_PATH = OUTPUT_DIR / "THESIS_EVIDENCE_BASELINE.md"
TRACE_MD_PATH = OUTPUT_DIR / "CLAIM_AND_CHAPTER_TRACEABILITY.md"

CANONICAL_SOURCE_PATHS = [
    Path("requirements-thesis.txt"),
    Path("scripts/build_thesis_evidence_package.py"),
    Path("scripts/validate_thesis_evidence_package.py"),
    Path("scripts/validate_research_records.py"),
    Path("scripts/check_thesis_citations.py"),
    Path("scripts/validate_thesis_content.py"),
    Path("scripts/build_thesis_progress_visual.py"),
    Path("scripts/build_thesis_review_document.py"),
    Path("scripts/build_thesis_review_manifest.py"),
    Path("scripts/validate_thesis_review_document.py"),
    Path("scripts/inspect_thesis_render.py"),
    Path("scripts/visualization_agent.py"),
    Path("visualizations-gallery/build_gallery.py"),
    Path("schemas/thesis-evidence-snapshot-v1.schema.json"),
    Path("schemas/gold-label-record-v2.schema.json"),
    Path("schemas/evaluation-run-manifest-v2.schema.json"),
    Path("schemas/policy-candidate-record-v1.schema.json"),
    Path("schemas/thesis-review-package-manifest-v1.schema.json"),
    Path("schemas/architecture-run-manifest-v1.schema.json"),
    Path("schemas/baseline-lock-manifest-v2.schema.json"),
    Path("schemas/hlayer-runtime-config-v1.schema.json"),
    Path("schemas/model-execution-manifest-v1.schema.json"),
    Path("schemas/security-posture-snapshot-v1.schema.json"),
    Path("configs/hlayer-runtime.json"),
    Path("configs/protected-change-authorization-v1.json"),
    Path("scripts/build_hardening_manifests.py"),
    Path("scripts/run_hlayer_architecture.py"),
    Path("scripts/verify-source.ps1"),
    Path("scripts/verify-controlled.ps1"),
    Path("scripts/verify-release.ps1"),
    Path("src/vego_hlayer/__init__.py"),
    Path("src/vego_hlayer/adapters.py"),
    Path("src/vego_hlayer/contracts.py"),
    Path("src/vego_hlayer/io_safety.py"),
    Path("src/vego_hlayer/runtime.py"),
    Path("src/vego_hlayer/state_machine.py"),
    Path("docs/research/h-layer/program-status-snapshot-v1.json"),
    Path("docs/research/hardening/README.md"),
    Path("docs/research/hardening/MODEL_EVALUATION_PROTOCOLS.md"),
    Path("docs/research/hardening/THREAT_MODEL.md"),
    Path("docs/research/hardening/UNIFIED_RUNTIME_ARCHITECTURE.md"),
    Path("docs/research/hardening/VERIFICATION_AND_RELEASE.md"),
    Path("docs/research/accuracy-improvement-plan.md"),
    Path("docs/research/supervisor-label-approval-pack.md"),
    Path("experiments/registry.md"),
    *[
        Path(f"experiments/EXP-{number:03d}-" + suffix + "/README.md")
        for number, suffix in [
            (19, "reviewer-calibration"),
            (20, "independent-expert-labeling"),
            (21, "development-baseline-error-analysis"),
            (22, "routing-retrieval-validity"),
            (23, "deterministic-policy-development"),
            (24, "sealed-holdout-pilot"),
            (25, "external-education-replication"),
            (26, "human-effort-study"),
            (27, "ablation-robustness"),
        ]
    ],
    Path("experiments/EXP-028-model-execution-reproducibility/README.md"),
    Path("experiments/EXP-029-frozen-candidate-model-comparison/README.md"),
    Path("thesis/outline.md"),
    Path("thesis/chapters/00-abstract.md"),
    Path("thesis/chapters/01-introduction.md"),
    Path("thesis/chapters/02-background-and-related-work.md"),
    Path("thesis/chapters/03-problem-and-research-questions.md"),
    Path("thesis/chapters/04-vego-ai-baseline-pipeline.md"),
    Path("thesis/chapters/05-human-ai-co-reasoning-artifact.md"),
    Path("thesis/chapters/06-evaluation-methodology.md"),
    Path("thesis/chapters/07-experimental-results.md"),
    Path("thesis/chapters/08-threats-to-validity.md"),
    Path("thesis/chapters/09-discussion.md"),
    Path("thesis/chapters/10-conclusion-and-phd-continuation.md"),
    Path("thesis/chapters/11-references.md"),
    Path("thesis/chapters/design-theory-governed-reuse.md"),
    Path("thesis/chapters/appendix-a-supplementary.md"),
]


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def sha256_portable_text_bytes(value: bytes) -> str:
    text = value.decode("utf-8-sig")
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def sha256_portable_text_file(path: Path) -> str:
    return sha256_portable_text_bytes(path.read_bytes())


def git(*args: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(ROOT), *args],
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def resolve_source_revision(explicit: str | None) -> str:
    if explicit:
        return git("rev-parse", explicit)
    if SNAPSHOT_PATH.exists():
        try:
            prior = json.loads(SNAPSHOT_PATH.read_text(encoding="utf-8"))
            prior_revision = prior.get("sourceRevision")
            if isinstance(prior_revision, str):
                if re.fullmatch(r"[0-9a-f]{40}", prior_revision):
                    return prior_revision
                if prior_revision:
                    return git("rev-parse", prior_revision)
        except (OSError, json.JSONDecodeError, subprocess.CalledProcessError):
            pass
    return git("rev-parse", "HEAD")


def canonical_source_hashes() -> dict[str, str]:
    missing = [path.as_posix() for path in CANONICAL_SOURCE_PATHS if not (ROOT / path).is_file()]
    if missing:
        raise FileNotFoundError(
            "missing canonical thesis sources: " + ", ".join(missing)
        )
    return {
        path.as_posix(): sha256_portable_text_file(ROOT / path)
        for path in CANONICAL_SOURCE_PATHS
    }


def source_tree_hash(source_hashes: dict[str, str]) -> str:
    digest = hashlib.sha256()
    for path, file_hash in sorted(source_hashes.items()):
        digest.update(path.encode("utf-8"))
        digest.update(b"\0")
        digest.update(file_hash.encode("ascii"))
        digest.update(b"\n")
    return digest.hexdigest()


def canonical_sources_dirty() -> bool:
    paths = [path.as_posix() for path in CANONICAL_SOURCE_PATHS]
    diff = subprocess.run(
        ["git", "-C", str(ROOT), "diff", "--quiet", "HEAD", "--", *paths],
        check=False,
    )
    untracked = git("ls-files", "--others", "--exclude-standard", "--", *paths)
    return diff.returncode != 0 or bool(untracked)


def generated_at(refresh: bool) -> str:
    if SNAPSHOT_PATH.exists() and not refresh:
        try:
            prior = json.loads(SNAPSHOT_PATH.read_text(encoding="utf-8"))
            value = prior.get("generatedAt")
            if isinstance(value, str) and value:
                return value
        except (OSError, json.JSONDecodeError):
            pass
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def evidence_value(
    value: int | float | str,
    unit: str,
    source: str,
    evidence_class: str,
    claim_boundary: str,
) -> dict[str, Any]:
    return {
        "value": value,
        "unit": unit,
        "source": source,
        "evidenceClass": evidence_class,
        "claimBoundary": claim_boundary,
    }


def build_experiments() -> list[dict[str, Any]]:
    return [
        {
            "id": "EXP-019",
            "title": "Reviewer calibration without evaluation leakage",
            "status": "Evaluation-ready",
            "question": "Can two reviewers apply the protocol consistently before the blinded evaluation begins?",
            "inputs": [
                "Three same-pattern rows excluded from every generalization metric",
                "Reviewer instructions and approved label vocabulary",
            ],
            "outputs": [
                "Calibration disagreement log",
                "Clarified protocol revision with no labels transferred to evaluation",
            ],
            "acceptance": [
                "Both reviewers complete all three rows independently",
                "Every disagreement is discussed and recorded",
                "Calibration rows remain excluded from EXP-020 through EXP-025 metrics",
            ],
            "dependencies": [
                "Supervisor protocol approval",
                "Two independent reviewers",
            ],
            "claimBoundary": "Calibration checks protocol usability only; it is not evidence of classification performance or generalization.",
        },
        {
            "id": "EXP-020",
            "title": "Independent expert labeling of the 24 safe candidates",
            "status": "Pending expert input",
            "question": "What independent gold labels do two reviewers and an adjudicator assign to the current leakage-safe candidate set?",
            "inputs": [
                "Twenty-four blinded generalization-safe rows",
                "Two independent reviewer returns",
                "Adjudication protocol",
            ],
            "outputs": [
                "Immutable reviewer-1 and reviewer-2 records",
                "Cohen's kappa before adjudication",
                "Adjudicated GoldLabelRecord-v2 set",
            ],
            "acceptance": [
                "No AI or memory-derived label is shown to reviewers",
                "All required rationale, confidence, reviewer, and date fields validate",
                "Disagreements are adjudicated without modifying raw reviewer returns",
            ],
            "dependencies": [
                "EXP-019 complete",
                "Ethics and consent handling approved",
            ],
            "claimBoundary": "At 1-19 safe labels results are pilot-only; at 20-24 quantitative reporting is allowed only with explicit small-sample limitations.",
        },
        {
            "id": "EXP-021",
            "title": "Development-only baseline error characterization",
            "status": "Blocked",
            "question": "Where does the frozen Agent 4 baseline disagree with adjudicated experts on the 16-row development partition?",
            "inputs": [
                "Frozen 16-row development partition",
                "Adjudicated EXP-020 labels",
                "Frozen Agent 4 baseline",
            ],
            "outputs": [
                "Baseline confusion matrix",
                "Error taxonomy and setting-by-error heatmap",
                "Candidate cases where advice might have helped",
            ],
            "acceptance": [
                "The sealed eight-row holdout remains unread",
                "Every error category has a human rationale and source row",
                "No policy rule is selected inside this experiment",
            ],
            "dependencies": [
                "EXP-020 has at least 20 safe adjudicated labels",
            ],
            "claimBoundary": "Development errors characterize the current sample; they do not establish holdout or cross-domain performance.",
        },
        {
            "id": "EXP-022",
            "title": "Routing and retrieval validity audit",
            "status": "Blocked",
            "question": "Do review triggers and memory retrieval focus attention on expert-identified baseline problems without hiding missed problems?",
            "inputs": [
                "EXP-021 development errors",
                "M1 review queue decisions",
                "M4A retrieval and match reasons",
            ],
            "outputs": [
                "Routing precision and recall",
                "Retrieval hit, relevance, scope, and conflict audit",
                "Missed-error and unnecessary-review table",
            ],
            "acceptance": [
                "Denominators distinguish patterns, queue items, cases, and review transactions",
                "Every retrieval judgment is made blind to candidate-policy output",
                "Same-pattern reuse is reported separately",
            ],
            "dependencies": [
                "EXP-021 complete",
            ],
            "claimBoundary": "This evaluates targeting and traceability; it does not by itself prove classification improvement or reduced effort at scale.",
        },
        {
            "id": "EXP-023",
            "title": "Deterministic policy development",
            "status": "Proposal — not approved",
            "question": "Can a frozen deterministic parallel policy be justified from development-only errors without changing the baseline?",
            "inputs": [
                "EXP-021 and EXP-022 development evidence",
                "At least three correctable development errors across at least two settings",
                "Supervisor-approved PolicyCandidateRecord-v1",
            ],
            "outputs": [
                "Versioned deterministic rules",
                "Policy hash and development-partition hash",
                "One frozen candidate for holdout evaluation",
            ],
            "acceptance": [
                "Rules use no sealed-holdout or external labels",
                "Every fallback preserves the baseline and requests or parks human review",
                "Output remains parallel_proposal_only",
            ],
            "dependencies": [
                "EXP-021 complete",
                "EXP-022 complete",
                "At least three development errors across two settings",
                "Explicit supervisor approval",
            ],
            "claimBoundary": "Policy development is proposal-only and cannot authorize Agent 4, runtime, or baseline changes.",
        },
        {
            "id": "EXP-024",
            "title": "One-time sealed eight-row holdout pilot",
            "status": "Blocked",
            "question": "Does the frozen policy produce positive net correction on eight previously sealed rows without a harmful regression?",
            "inputs": [
                "Frozen eight-row holdout manifest",
                "Frozen PolicyCandidateRecord-v1",
                "Adjudicated holdout labels opened only after policy freeze",
            ],
            "outputs": [
                "Paired correctness matrix",
                "Net correction and Wilson intervals",
                "One-time holdout evaluation manifest",
            ],
            "acceptance": [
                "Holdout is opened once after policy freeze",
                "No post-hoc policy change is made after viewing holdout outcomes",
                "All baseline and protected-path hashes remain unchanged",
            ],
            "dependencies": [
                "EXP-023 frozen and approved for one-time holdout evaluation",
            ],
            "claimBoundary": "Eight rows support a pilot decision only; they are too small for a formal improvement or generalization claim.",
        },
        {
            "id": "EXP-025",
            "title": "External education-domain replication",
            "status": "Proposal — not approved",
            "question": "Does a policy frozen before data collection retain a positive paired effect on a new education-domain batch?",
            "inputs": [
                "At least 30, target 48, new independently labeled patterns",
                "Frozen policy from EXP-023",
                "Two-reviewer and adjudication workflow",
            ],
            "outputs": [
                "External paired comparison",
                "Bootstrap confidence interval and exact McNemar test",
                "Setting and class subgroup safety analysis",
            ],
            "acceptance": [
                "Minimum external N is 30; target N is 48",
                "Net-correction confidence interval excludes zero",
                "Exact McNemar p-value is below 0.05",
                "Macro-F1 does not decline and no predefined subgroup shows harm",
            ],
            "dependencies": [
                "EXP-024 completed without policy revision",
                "New approved education-domain dataset",
            ],
            "claimBoundary": "Only this external gate can support a formal improvement claim, and only if every preregistered criterion passes.",
        },
        {
            "id": "EXP-026",
            "title": "Human-effort and workflow study",
            "status": "Proposal — not approved",
            "question": "Does memory change repeated-review demand, review time, or escalation quality under a controlled reviewer workflow?",
            "inputs": [
                "Timestamped review sessions",
                "Predefined before-memory and after-memory tasks",
                "Reviewer confidence and workload questionnaire",
            ],
            "outputs": [
                "Per-item review-time distribution",
                "Repeated-question and escalation-quality measures",
                "Reviewer confidence and qualitative findings",
            ],
            "acceptance": [
                "Task order and carryover effects are controlled",
                "No inferred or fabricated time savings",
                "Results separate local pilot observations from scale claims",
            ],
            "dependencies": [
                "Ethics and consent approval",
                "Reviewer availability",
            ],
            "claimBoundary": "Reduced human effort is unproven until this controlled study is completed; no scale claim is permitted from queue counts alone.",
        },
        {
            "id": "EXP-027",
            "title": "Ablation and robustness analysis",
            "status": "Proposal — not approved",
            "question": "Which approved mechanism elements are necessary for any observed paired effect and safety behavior?",
            "inputs": [
                "Frozen external evaluation set",
                "Approved policy and component configurations",
                "Predeclared ablations",
            ],
            "outputs": [
                "Ablation effect table",
                "Sensitivity to class balance and confidence thresholds",
                "Failure-mode and robustness report",
            ],
            "acceptance": [
                "Ablations do not tune on the external outcomes",
                "All configurations retain baseline immutability",
                "Negative and null results are reported",
            ],
            "dependencies": [
                "EXP-025 complete",
            ],
            "claimBoundary": "Ablation supports explanation and robustness only after the primary external analysis; it cannot rescue a failed primary gate.",
        },
    ]


def build_snapshot(
    refresh_timestamp: bool,
    source_revision: str | None = None,
) -> dict[str, Any]:
    status = json.loads(PROGRAM_STATUS.read_text(encoding="utf-8"))
    revision = resolve_source_revision(source_revision)
    baseline_revision = git("rev-parse", "official-vego-ai-baseline")
    exp005 = status["exp005Gate"]
    latest = status["latestAcceptedIteration"]

    source_hashes = canonical_source_hashes()

    snapshot: dict[str, Any] = {
        "schemaVersion": "ThesisEvidenceSnapshot-v1",
        "generatedAt": generated_at(refresh_timestamp),
        "sourceRevision": revision,
        "sourceTreeHash": source_tree_hash(source_hashes),
        "canonicalSourcesDirty": canonical_sources_dirty(),
        "programSnapshot": {
            "path": PROGRAM_STATUS.relative_to(ROOT).as_posix(),
            "sha256": sha256_file(PROGRAM_STATUS),
            "latestAcceptedIteration": latest["iteration"],
            "latestAcceptedRunId": latest["runId"],
            "verdict": latest["verdict"],
            "claimScope": latest["claimScope"],
            "verification": {
                "status": status["verificationRecord"]["status"],
                "recordedAt": status["verificationRecord"]["recordedAt"],
                "vegoTestsPassed": status["verificationRecord"]["tests"][
                    "VEGO-AI/tests"
                ]["passed"],
                "scriptTestsPassed": status["verificationRecord"]["tests"][
                    "scripts/tests"
                ]["passed"],
            },
        },
        "runtimeHardening": {
            "contractVersion": "1.0",
            "defaultMode": "legacy",
            "modes": [
                {
                    "id": "legacy",
                    "status": "Implemented",
                    "purpose": (
                        "Preserve the existing M1-M4B-1 implementation and public "
                        "artifacts as the publication reference."
                    ),
                    "failureBehavior": "Existing fail-safe behavior is preserved.",
                },
                {
                    "id": "unified",
                    "status": "Implemented",
                    "purpose": (
                        "Run M1-M4B-1 through versioned canonical contracts and "
                        "deterministic legacy adapters."
                    ),
                    "failureBehavior": (
                        "Invalid contracts, unauthorized paths, or unsafe outputs fail "
                        "without changing the baseline."
                    ),
                },
                {
                    "id": "parity",
                    "status": "Implemented",
                    "purpose": (
                        "Run legacy and unified paths from the same immutable inputs in "
                        "separate temporary directories."
                    ),
                    "failureBehavior": (
                        "Any normalized mismatch publishes only the legacy result and "
                        "records a structured difference."
                    ),
                },
            ],
            "parityEvidence": {
                "status": "PASS",
                "artifactCount": 14,
                "reviewItemCount": 11,
                "legacyMemoryRecordCount": 3,
                "comparisonRowCount": 27,
                "classificationChangeCount": 0,
                "claimBoundary": (
                    "Controlled compatibility evidence only; it is not an accuracy or "
                    "generalization result."
                ),
            },
            "authorityBoundary": {
                "supervisorDecisionState": "Deferred",
                "liveListenerAuthorized": False,
                "automaticCorrectionAuthorized": False,
                "trustedMemoryRule": (
                    "Only independently verified or human-adjudicated records may use "
                    "verified or adjudicated trust states."
                ),
                "timeoutBehavior": "Preserve the baseline and park the item.",
            },
            "securityBoundary": {
                "status": "PASS",
                "interactionLogDefault": "metadata_only",
                "pythonDependencyAudit": "PASS",
                "nodeDependencyAudit": "PASS",
                "secretAndPrivacyScan": "PASS",
                "baselineLock": "PASS",
                "claimBoundary": (
                    "The snapshot records reproducible controls and passing local scans; "
                    "it is not a guarantee that no future vulnerability exists."
                ),
            },
            "modelBoundary": {
                "defaultModel": "gpt-4o",
                "servedSnapshotKnown": False,
                "executionManifest": "ModelExecutionManifest-v1",
                "protocols": [
                    {
                        "id": "EXP-028",
                        "title": "Model execution reproducibility and drift",
                        "status": "Proposal — not approved",
                        "gate": (
                            "Record request/response provenance without changing prompts, "
                            "parameters, classifications, or the default model."
                        ),
                        "claimBoundary": "Protocol only; no model-comparison result.",
                        "chapterIds": ["4", "6", "8"],
                        "decisionIds": ["M-05", "M-06"],
                    },
                    {
                        "id": "EXP-029",
                        "title": "Frozen candidate-model comparison",
                        "status": "Blocked",
                        "gate": (
                            "At least 20 safe labels, completed reviewer agreement and "
                            "adjudication, frozen policy/prompt, supervisor approval, "
                            "sealed holdout, and recorded cost limit."
                        ),
                        "claimBoundary": (
                            "No candidate model becomes a default through Iteration 15."
                        ),
                        "chapterIds": ["6", "7", "8", "9"],
                        "decisionIds": ["M-05", "M-06"],
                    },
                ],
            },
        },
        "researchFrame": {
            "mainContribution": (
                "Reusable, traceable, leakage-aware human judgment for AI-assisted "
                "variability assessment, integrated as a non-destructive layer around "
                "the preserved VEGO-AI baseline."
            ),
            "evaluationResearchQuestions": [
                {
                    "id": "E-RQ1",
                    "question": (
                        "Where, and in which error categories, does the frozen Agent 4 "
                        "baseline disagree with independent expert judgment?"
                    ),
                    "evidenceRequired": [
                        "Two independent reviewers",
                        "Adjudicated generalization-safe labels",
                        "Development-only error taxonomy",
                    ],
                    "status": "Pending expert input",
                },
                {
                    "id": "E-RQ2",
                    "question": (
                        "Do selective review and memory retrieval target expert-identified "
                        "baseline problems with traceable and scope-correct evidence?"
                    ),
                    "evidenceRequired": [
                        "Adjudicated development labels",
                        "Routing precision and recall",
                        "Retrieval relevance, scope, and conflict audit",
                    ],
                    "status": "Pending expert input",
                },
                {
                    "id": "E-RQ3",
                    "question": (
                        "Does a frozen deterministic parallel policy produce positive net "
                        "correction on unseen, leakage-safe data while preserving baseline safety?"
                    ),
                    "evidenceRequired": [
                        "Frozen PolicyCandidateRecord-v1",
                        "One-time sealed holdout",
                        "External education-domain replication with at least 30 rows",
                    ],
                    "status": "Blocked",
                },
            ],
            "hypotheses": [
                {
                    "id": "H1",
                    "statement": (
                        "Selective review identifies a non-trivial subset of patterns that "
                        "contains expert-confirmed baseline errors."
                    ),
                    "status": "Pending expert input",
                    "test": "EXP-021 and EXP-022 routing precision/recall on adjudicated development labels.",
                },
                {
                    "id": "H2",
                    "statement": (
                        "Human judgment memory retrieves relevant, scope-correct prior "
                        "judgments for new review contexts."
                    ),
                    "status": "Pending expert input",
                    "test": "EXP-022 blind relevance, scope, conflict, and leakage audit.",
                },
                {
                    "id": "H3",
                    "statement": (
                        "A frozen deterministic parallel policy yields positive net correction "
                        "on unseen leakage-safe expert-labeled data."
                    ),
                    "status": "Blocked",
                    "test": "EXP-024 pilot followed by EXP-025 preregistered external paired comparison.",
                },
                {
                    "id": "H4",
                    "statement": (
                        "Reusable memory reduces repeated human review effort without reducing "
                        "escalation quality."
                    ),
                    "status": "Proposal — not approved",
                    "test": "EXP-026 controlled human-effort study.",
                },
            ],
            "traceability": [
                {
                    "id": "E-RQ1",
                    "kind": "research_question",
                    "experimentIds": ["EXP-019", "EXP-020", "EXP-021"],
                    "chapterIds": ["3", "6", "7"],
                    "decisionIds": ["M-01", "M-05"],
                    "metricOrGate": "Adjudicated baseline errors and error taxonomy",
                    "evidenceState": "Pending expert input",
                },
                {
                    "id": "E-RQ2",
                    "kind": "research_question",
                    "experimentIds": ["EXP-021", "EXP-022"],
                    "chapterIds": ["3", "5", "6", "7"],
                    "decisionIds": ["M-03", "M-04", "M-05"],
                    "metricOrGate": "Routing precision/recall and retrieval validity",
                    "evidenceState": "Pending expert input",
                },
                {
                    "id": "E-RQ3",
                    "kind": "research_question",
                    "experimentIds": ["EXP-023", "EXP-024", "EXP-025"],
                    "chapterIds": ["3", "6", "7", "8", "9"],
                    "decisionIds": ["M-02", "M-04", "M-05", "M-06"],
                    "metricOrGate": "Paired net correction after policy freeze",
                    "evidenceState": "Blocked",
                },
                {
                    "id": "H1",
                    "kind": "hypothesis",
                    "experimentIds": ["EXP-021", "EXP-022"],
                    "chapterIds": ["3", "6", "7"],
                    "decisionIds": ["M-03", "M-05"],
                    "metricOrGate": "Review routing contains adjudicated baseline errors",
                    "evidenceState": "Pending expert input",
                },
                {
                    "id": "H2",
                    "kind": "hypothesis",
                    "experimentIds": ["EXP-022"],
                    "chapterIds": ["3", "5", "6", "7"],
                    "decisionIds": ["M-02", "M-04"],
                    "metricOrGate": "Blind relevance, scope, conflict, and leakage audit",
                    "evidenceState": "Pending expert input",
                },
                {
                    "id": "H3",
                    "kind": "hypothesis",
                    "experimentIds": ["EXP-023", "EXP-024", "EXP-025"],
                    "chapterIds": ["3", "6", "7", "8", "9"],
                    "decisionIds": ["M-02", "M-04", "M-05"],
                    "metricOrGate": "Positive paired net correction on unseen safe data",
                    "evidenceState": "Blocked",
                },
                {
                    "id": "H4",
                    "kind": "hypothesis",
                    "experimentIds": ["EXP-026"],
                    "chapterIds": ["3", "6", "8", "9"],
                    "decisionIds": ["M-05", "M-06"],
                    "metricOrGate": "Controlled review-time and escalation-quality study",
                    "evidenceState": "Proposal — not approved",
                },
            ],
        },
        "baselines": [
            {
                "id": "B0",
                "name": "Frozen original VEGO-AI baseline",
                "status": "Implemented",
                "purpose": "Preserve the official Agent 4 output as the immutable comparator.",
                "data": "179 scored evaluations across 4 settings (83 distinct student models), aggregated into 27 Agent 4 patterns.",
                "policy": f"official-vego-ai-baseline at {baseline_revision}",
                "evaluationGate": "Byte and provenance integrity checks must pass.",
                "allowedClaim": "The original baseline is preserved and reproducibly identifiable.",
                "behaviorChanged": False,
                "experimentIds": ["EXP-021"],
                "chapterIds": ["4", "7"],
                "decisionIds": ["M-01"],
                "claimLevel": "safe_now",
            },
            {
                "id": "B1",
                "name": "Legacy and unified human-judgment mechanism",
                "status": "Implemented",
                "purpose": (
                    "Demonstrate selective review, structured feedback, memory, "
                    "advice, and comparison through compatible legacy and canonical "
                    "contract paths."
                ),
                "data": (
                    "Controlled parity covered 14 artifacts, 11 review items, 3 "
                    "legacy mechanism-memory records, and 27 comparison rows."
                ),
                "policy": (
                    "Legacy remains default; unified is explicit; parity fails closed "
                    "to the legacy result on every mismatch."
                ),
                "evaluationGate": (
                    "Contract, parity, mechanism, security, and safety checks only."
                ),
                "allowedClaim": (
                    "Mechanism readiness, compatibility, traceability, escalation, "
                    "and baseline protection."
                ),
                "behaviorChanged": False,
                "experimentIds": ["EXP-022"],
                "chapterIds": ["5", "7"],
                "decisionIds": ["M-01", "M-02", "M-03", "M-04", "M-05"],
                "claimLevel": "safe_now",
            },
            {
                "id": "B2",
                "name": "Independent expert-labeled baseline",
                "status": "Pending expert input",
                "purpose": "Measure Agent 4 performance against independent adjudicated labels.",
                "data": f"{exp005['generalizationSafeValidLabels']} of {exp005['candidateRows']} generalization-safe labels currently available.",
                "policy": "No candidate policy; characterize B0 only.",
                "evaluationGate": "At least 20 safe labels for quantitative reporting; 16 development and 8 sealed holdout.",
                "allowedClaim": "No accuracy result until the gate opens.",
                "behaviorChanged": False,
                "experimentIds": ["EXP-019", "EXP-020", "EXP-021"],
                "chapterIds": ["6", "7"],
                "decisionIds": ["M-05", "M-06"],
                "claimLevel": "conditional",
            },
            {
                "id": "B3",
                "name": "Frozen deterministic candidate policy",
                "status": "Proposal — not approved",
                "purpose": "Define one development-only parallel correction proposal if evidence warrants it.",
                "data": "Development labels only; sealed holdout remains unread.",
                "policy": "PolicyCandidateRecord-v1, deterministic, conflict-free, parallel_proposal_only.",
                "evaluationGate": "At least three correctable development errors across at least two settings plus supervisor approval.",
                "allowedClaim": "Policy design rationale only; no performance claim.",
                "behaviorChanged": False,
                "experimentIds": ["EXP-023"],
                "chapterIds": ["6", "8"],
                "decisionIds": ["M-02", "M-03", "M-04", "M-05"],
                "claimLevel": "proposal_only",
            },
            {
                "id": "B4",
                "name": "Sealed holdout pilot",
                "status": "Blocked",
                "purpose": "Evaluate one frozen candidate exactly once on eight previously sealed rows.",
                "data": "Eight rows selected before policy development.",
                "policy": "B3 frozen before opening labels.",
                "evaluationGate": "One-time run, no post-hoc policy revision.",
                "allowedClaim": "Pilot evidence only, regardless of direction.",
                "behaviorChanged": False,
                "experimentIds": ["EXP-024", "EXP-027"],
                "chapterIds": ["6", "7", "8"],
                "decisionIds": ["M-05"],
                "claimLevel": "conditional",
            },
            {
                "id": "B5",
                "name": "External education-domain replication",
                "status": "Proposal — not approved",
                "purpose": "Test the frozen policy on a newly collected education-domain batch.",
                "data": "Minimum 30, target 48, independently labeled patterns.",
                "policy": "B3 remains frozen; no external-set tuning.",
                "evaluationGate": "Preregistered paired statistics, macro-F1 non-decline, and subgroup safety.",
                "allowedClaim": "Formal improvement only if every preregistered criterion passes.",
                "behaviorChanged": False,
                "experimentIds": ["EXP-025", "EXP-026", "EXP-027"],
                "chapterIds": ["6", "7", "9", "10"],
                "decisionIds": ["M-06"],
                "claimLevel": "formal_gate",
            },
        ],
        "evidence": {
            "studentModels": evidence_value(
                179,
                "student models",
                "docs/PROGRESS_TRACKER.md",
                "Offline evidence",
                "Scale description only; not an independently labeled evaluation sample.",
            ),
            "agent4Patterns": evidence_value(
                27,
                "patterns",
                "VEGO-AI/eval_output/<setting>/agentD_variability_classes*.json",
                "Implemented",
                "Frozen baseline distribution, not expert ground truth.",
            ),
            "substantialPatterns": evidence_value(
                9,
                "patterns",
                "VEGO-AI/eval_output/<setting>/agentD_variability_classes*.json",
                "Implemented",
                "Agent 4 output class count.",
            ),
            "occasionalPatterns": evidence_value(
                18,
                "patterns",
                "VEGO-AI/eval_output/<setting>/agentD_variability_classes*.json",
                "Implemented",
                "Agent 4 output class count.",
            ),
            "undeterminedPatterns": evidence_value(
                0,
                "patterns",
                "VEGO-AI/eval_output/<setting>/agentD_variability_classes*.json",
                "Implemented",
                "Agent 4 output class count.",
            ),
            "reviewItems": evidence_value(
                11,
                "review queue items",
                "reports/generated/evaluation_comparison/evaluation_summary.json",
                "Offline evidence",
                "Observed prototype count; it is not a demonstrated effort reduction.",
            ),
            "reusableJudgments": evidence_value(
                3,
                "memory records",
                "reports/generated/evaluation_comparison/evaluation_summary.json",
                "Offline evidence",
                "All three are same-pattern mechanism evidence and excluded from generalization metrics.",
            ),
            "memoryAdviceItems": evidence_value(
                8,
                "advice items",
                "reports/generated/evaluation_comparison/evaluation_summary.json",
                "Offline evidence",
                "Retrieval availability only; independent relevance is pending EXP-022.",
            ),
            "comparisonRows": evidence_value(
                27,
                "comparison rows",
                "reports/generated/evaluation_comparison/evaluation_summary.json",
                "Offline evidence",
                "Parallel comparison coverage only.",
            ),
            "memoryInformedChanges": evidence_value(
                0,
                "changed classifications",
                "reports/generated/evaluation_comparison/evaluation_summary.json",
                "Offline evidence",
                "Current policy cannot produce an accuracy delta because it changes no classifications.",
            ),
            "reviewAfterMemory": evidence_value(
                2,
                "review flags",
                "reports/generated/evaluation_comparison/evaluation_summary.json",
                "Offline evidence",
                "Escalation mechanism evidence; precision and recall await expert labels.",
            ),
            "latestIteration": evidence_value(
                latest["iteration"],
                "accepted iteration",
                "docs/research/h-layer/program-status-snapshot-v1.json",
                "Offline evidence",
                "Reliability-only NEUTRAL snapshot; no performance default or accuracy claim.",
            ),
        },
        "labelGate": {
            "candidateRows": exp005["candidateRows"],
            "suppliedLabels": exp005["suppliedLabels"],
            "validLabels": exp005["validLabels"],
            "generalizationSafeLabels": exp005["generalizationSafeValidLabels"],
            "samePatternCalibrationRows": 3,
            "quantitativeMinimum": exp005["minimumForQuantitativeEvaluation"],
            "externalMinimum": 30,
            "externalTarget": 48,
            "developmentRows": 16,
            "sealedHoldoutRows": 8,
            "status": exp005["status"],
            "accuracyStatus": (
                "NOT YET COMPUTABLE"
                if exp005["generalizationSafeValidLabels"] == 0
                else (
                    "PILOT ONLY"
                    if exp005["generalizationSafeValidLabels"]
                    < exp005["minimumForQuantitativeEvaluation"]
                    else "QUANTITATIVE WITH LIMITATIONS"
                )
            ),
            "humanActionRequired": (
                "Approve the protocol, complete two independent blind reviews, "
                "adjudicate disagreements, and freeze the gold labels."
            ),
        },
        "experiments": build_experiments(),
        "decisionDependencies": [
            {
                "id": "M-01",
                "title": "Confirm or correct the July 1 record",
                "outcome": status["decisionState"]["M-01"],
                "confirmationStatus": status["decisionState"][
                    "confirmationStatus"
                ],
                "experimentIds": ["EXP-019", "EXP-020"],
                "baselineIds": ["B0", "B1", "B2"],
                "unlock": "Auditable terminology and directive provenance",
            },
            {
                "id": "M-02",
                "title": "Select the H-layer decomposition",
                "outcome": status["decisionState"]["M-02"],
                "confirmationStatus": status["decisionState"][
                    "confirmationStatus"
                ],
                "experimentIds": ["EXP-022", "EXP-023"],
                "baselineIds": ["B1", "B3"],
                "unlock": "Architecture-specific policy proposal only",
            },
            {
                "id": "M-03",
                "title": "Approve observation, routing, and dosage parameters",
                "outcome": status["decisionState"]["M-03"],
                "confirmationStatus": status["decisionState"][
                    "confirmationStatus"
                ],
                "experimentIds": ["EXP-021", "EXP-022", "EXP-026"],
                "baselineIds": ["B1", "B3"],
                "unlock": "Preregistered routing evaluation",
            },
            {
                "id": "M-04",
                "title": "Approve deterministic-first H-Verify protocol",
                "outcome": status["decisionState"]["M-04"],
                "confirmationStatus": status["decisionState"][
                    "confirmationStatus"
                ],
                "experimentIds": ["EXP-022", "EXP-023", "EXP-024"],
                "baselineIds": ["B1", "B3", "B4"],
                "unlock": "Bounded verification and adjudication tests",
            },
            {
                "id": "M-05",
                "title": "Confirm human authority and implementation boundary",
                "outcome": status["decisionState"]["M-05"],
                "confirmationStatus": status["decisionState"][
                    "confirmationStatus"
                ],
                "experimentIds": [
                    "EXP-019",
                    "EXP-020",
                    "EXP-023",
                    "EXP-024",
                    "EXP-026",
                ],
                "baselineIds": ["B1", "B2", "B3", "B4"],
                "unlock": "Reviewer roles, policy freeze, and one-time pilot",
            },
            {
                "id": "M-06",
                "title": "Confirm thesis and future-work scope",
                "outcome": status["decisionState"]["M-06"],
                "confirmationStatus": status["decisionState"][
                    "confirmationStatus"
                ],
                "experimentIds": ["EXP-025", "EXP-026", "EXP-027"],
                "baselineIds": ["B2", "B5"],
                "unlock": "External education replication and optional effort study",
            },
        ],
        "riskGates": [
            {
                "id": "RISK-LEAKAGE",
                "risk": "Same-pattern leakage could create circular evidence.",
                "status": "Implemented",
                "mitigation": "Exclude same-pattern and unknown provenance from primary metrics.",
                "blockedClaim": "Generalization",
                "experimentIds": ["EXP-020", "EXP-022", "EXP-024", "EXP-025"],
            },
            {
                "id": "RISK-SMALL-N",
                "risk": "The current candidate set is too small for a formal improvement claim.",
                "status": "Blocked",
                "mitigation": "Report 20–24 labels as a limited MSc result; require at least 30 new external rows for formal testing.",
                "blockedClaim": "Formal performance improvement",
                "experimentIds": ["EXP-020", "EXP-024", "EXP-025"],
            },
            {
                "id": "RISK-OVERFIT",
                "risk": "Policy design on all labeled rows would contaminate evaluation.",
                "status": "Offline design",
                "mitigation": "Freeze a 16/8 development/holdout partition before policy inspection.",
                "blockedClaim": "Held-out policy effect",
                "experimentIds": ["EXP-021", "EXP-023", "EXP-024"],
            },
            {
                "id": "RISK-EXTERNAL",
                "risk": "One course and two settings cannot establish broader validity.",
                "status": "Proposal — not approved",
                "mitigation": "Collect a new education-domain batch with a frozen policy and independent reviewers.",
                "blockedClaim": "External validity",
                "experimentIds": ["EXP-025", "EXP-027"],
            },
        ],
        "metrics": {
            "primary": [
                "Net correction = changed-and-correct minus changed-and-wrong on paired rows",
            ],
            "secondary": [
                "Original and candidate accuracy",
                "Original and candidate macro-F1",
                "Per-class precision and recall",
                "Paired correctness matrix",
                "Routing precision and recall",
                "Retrieval relevance, scope correctness, and conflict rate",
                "Inter-rater agreement before adjudication",
            ],
            "safety": [
                "Baseline files changed: must remain zero",
                "Unauthorized or forbidden protected-path changes: must remain zero",
                "Unknown or same-pattern leakage in primary metrics: must remain zero",
                "Automatic correction applications: must remain zero",
                "Post-hoc holdout policy revisions: must remain zero",
            ],
            "currentResults": {
                "originalAccuracy": None,
                "candidateAccuracy": None,
                "originalMacroF1": None,
                "candidateMacroF1": None,
                "netCorrection": None,
                "pairedPValue": None,
                "status": "NOT YET COMPUTABLE",
            },
        },
        "statisticalProtocol": {
            "confidenceLevel": 0.95,
            "proportionInterval": "Wilson",
            "pairedBootstrapReplicates": 10000,
            "pairedBootstrapSeed": 20260721,
            "pairedTest": "Exact McNemar on the external set",
            "formalImprovementGate": [
                "At least 30 externally collected, generalization-safe, adjudicated labels",
                "Candidate policy frozen before external data inspection",
                "Net-correction 95% paired-bootstrap confidence interval excludes zero",
                "Exact McNemar p-value is below 0.05",
                "Macro-F1 does not decline",
                "No predefined setting or class subgroup shows material harm",
                "Baseline and protected-path hashes remain unchanged",
            ],
        },
        "claimGates": {
            "safeNow": [
                "VEGO-AI has a reusable human-judgment mechanism supporting selective review, structured feedback, provenance-aware memory, advisory retrieval, and non-destructive comparison.",
                "The legacy and unified M1-M4B-1 paths pass controlled fail-closed parity with 27 comparison rows and zero classification changes.",
                "The current implementation preserves original Agent 4 classifications and baseline artifacts.",
                "The project is evaluation-ready but remains blocked on independent expert input.",
            ],
            "conditionalAfterLabels": [
                "At 20-24 generalization-safe adjudicated labels, report baseline and candidate metrics as an MSc pilot with explicit small-sample limitations.",
                "At eight sealed holdout rows, report one-time pilot net correction without a formal improvement claim.",
            ],
            "formalImprovement": [
                "A formal improvement claim requires EXP-025 and every preregistered statistical and safety criterion to pass.",
            ],
            "notAllowed": [
                "Guaranteed or proven accuracy improvement at the current zero-label state",
                "Generalization from same-pattern memory records",
                "Benchmark superiority using analysis files that duplicate Agent 4 output",
                "Reduced human effort at scale without EXP-026",
                "Clinical performance or domain transfer claims",
                "Automatic baseline mutation, Agent 4 changes, or M4B-2 authorization",
            ],
        },
        "chapterTraceability": [
            {
                "chapter": "1",
                "file": "thesis/chapters/01-introduction.md",
                "evidence": ["B0-B5 ladder", "Safe current claim"],
                "experiments": ["EXP-019", "EXP-020", "EXP-025"],
                "claimStatus": "Delivered — provisional",
            },
            {
                "chapter": "2",
                "file": "thesis/chapters/02-background-and-related-work.md",
                "evidence": ["Human oversight", "Selective prediction", "Design science"],
                "experiments": [],
                "claimStatus": "Delivered — provisional",
            },
            {
                "chapter": "3",
                "file": "thesis/chapters/03-problem-and-research-questions.md",
                "evidence": ["E-RQ1-E-RQ3", "H1-H4"],
                "experiments": ["EXP-021", "EXP-022", "EXP-024", "EXP-026"],
                "claimStatus": "Delivered — provisional",
            },
            {
                "chapter": "4",
                "file": "thesis/chapters/04-vego-ai-baseline-pipeline.md",
                "evidence": [
                    "Frozen B0 baseline",
                    "27-pattern distribution",
                    "Historical GPT-4o alias limitation",
                ],
                "experiments": ["EXP-000", "EXP-021", "EXP-028"],
                "claimStatus": "Offline evidence",
            },
            {
                "chapter": "5",
                "file": "thesis/chapters/05-human-ai-co-reasoning-artifact.md",
                "evidence": [
                    "B1 mechanism",
                    "Legacy/unified/parity contracts",
                    "Non-destructive boundary",
                ],
                "experiments": ["EXP-001", "EXP-022"],
                "claimStatus": "Implemented",
            },
            {
                "chapter": "6",
                "file": "thesis/chapters/06-evaluation-methodology.md",
                "evidence": ["Preregistered metrics", "16/8 split", "External gate"],
                "experiments": [f"EXP-{number:03d}" for number in range(19, 30)],
                "claimStatus": "Evaluation-ready",
            },
            {
                "chapter": "7",
                "file": "thesis/chapters/07-experimental-results.md",
                "evidence": ["Current mechanism counts", "Zero-label gate", "Blank accuracy panels"],
                "experiments": ["EXP-001", "EXP-005", "EXP-012", "EXP-019", "EXP-020"],
                "claimStatus": "Pending expert input",
            },
            {
                "chapter": "8",
                "file": "thesis/chapters/08-threats-to-validity.md",
                "evidence": [
                    "Leakage",
                    "Class prevalence",
                    "Reviewer roles",
                    "External replication",
                    "Model drift and served-snapshot limitation",
                ],
                "experiments": [
                    "EXP-019",
                    "EXP-020",
                    "EXP-025",
                    "EXP-027",
                    "EXP-028",
                    "EXP-029",
                ],
                "claimStatus": "Delivered — provisional",
            },
            {
                "chapter": "9",
                "file": "thesis/chapters/09-discussion.md",
                "evidence": ["Conditional outcome matrix", "Mechanism versus performance"],
                "experiments": ["EXP-021", "EXP-022", "EXP-024", "EXP-025", "EXP-026"],
                "claimStatus": "Delivered — provisional",
            },
            {
                "chapter": "10",
                "file": "thesis/chapters/10-conclusion-and-phd-continuation.md",
                "evidence": ["Safe claim now", "Conditional claim", "Not allowed yet"],
                "experiments": ["EXP-020", "EXP-024", "EXP-025"],
                "claimStatus": "Pending expert input",
            },
        ],
        "sourceHashes": source_hashes,
    }
    return snapshot


def baseline_markdown(data: dict[str, Any]) -> str:
    labels = data["labelGate"]
    lines = [
        "# Thesis Evidence Baseline",
        "",
        f"Generated from revision `{data['sourceRevision']}` and accepted Iteration "
        f"{data['programSnapshot']['latestAcceptedIteration']} "
        f"(`{data['programSnapshot']['latestAcceptedRunId']}`).",
        "",
        "> **Current verdict:** accuracy is **NOT YET COMPUTABLE** because the project "
        f"has {labels['generalizationSafeLabels']} of {labels['candidateRows']} "
        "generalization-safe expert labels. This file records a research baseline, "
        "not an accuracy result.",
        "",
        "## B0-B5 evidence ladder",
        "",
        "| ID | Baseline | Status | Evaluation gate | Allowed claim |",
        "| --- | --- | --- | --- | --- |",
    ]
    for baseline in data["baselines"]:
        lines.append(
            f"| {baseline['id']} | {baseline['name']} | {baseline['status']} | "
            f"{baseline['evaluationGate']} | {baseline['allowedClaim']} |"
        )
    lines += [
        "",
        "## Current evidence",
        "",
        "| Measure | Value | Source class | Boundary |",
        "| --- | ---: | --- | --- |",
    ]
    for key, item in data["evidence"].items():
        label = key.replace("memoryInformed", "memory-informed ").replace(
            "reviewAfter", "review-after-"
        )
        lines.append(
            f"| {label} | {item['value']} {item['unit']} | "
            f"{item['evidenceClass']} | {item['claimBoundary']} |"
        )
    lines += [
        "",
        "## Immediate human gate",
        "",
        f"- Candidate rows: **{labels['candidateRows']}**.",
        f"- Supplied labels: **{labels['suppliedLabels']}**.",
        f"- Quantitative MSc minimum: **{labels['quantitativeMinimum']}**.",
        f"- External minimum/target: **{labels['externalMinimum']} / {labels['externalTarget']}**.",
        f"- Required action: {labels['humanActionRequired']}",
        "",
        "## Decision rule",
        "",
        "Do not design or select a correction policy from the sealed holdout. Complete "
        "calibration and independent labeling, characterize errors on the 16-row "
        "development partition, and freeze any approved deterministic policy before "
        "opening the eight-row holdout. Formal improvement remains blocked until the "
        "separate external replication gate passes.",
        "",
        "_Generated by `scripts/build_thesis_evidence_package.py`. Do not edit manually._",
        "",
    ]
    return "\n".join(lines)


def trace_markdown(data: dict[str, Any]) -> str:
    lines = [
        "# Claim and Chapter Traceability",
        "",
        "This generated register connects each thesis chapter to its evidence state and "
        "planned experiment gate. A chapter marked `Pending expert input` may contain "
        "methodology and blank result structures but no positive performance conclusion.",
        "",
        "| Chapter | File | Evidence | Experiments | Claim status |",
        "| --- | --- | --- | --- | --- |",
    ]
    for chapter in data["chapterTraceability"]:
        lines.append(
            f"| {chapter['chapter']} | `{chapter['file']}` | "
            f"{'; '.join(chapter['evidence'])} | "
            f"{', '.join(chapter['experiments']) or 'Literature only'} | "
            f"{chapter['claimStatus']} |"
        )
    lines += [
        "",
        "## Current claim boundary",
        "",
        "### Safe now",
        "",
    ]
    lines.extend(f"- {claim}" for claim in data["claimGates"]["safeNow"])
    lines += ["", "### Conditional", ""]
    lines.extend(
        f"- {claim}" for claim in data["claimGates"]["conditionalAfterLabels"]
    )
    lines += ["", "### Not allowed", ""]
    lines.extend(f"- {claim}" for claim in data["claimGates"]["notAllowed"])
    lines += [
        "",
        "_Generated by `scripts/build_thesis_evidence_package.py`. Do not edit manually._",
        "",
    ]
    return "\n".join(lines)


def write_or_check(path: Path, content: str, check: bool) -> bool:
    normalized = content.replace("\r\n", "\n")
    if path.exists() and path.read_text(encoding="utf-8").replace("\r\n", "\n") == normalized:
        return True
    if check:
        print(f"STALE: {path.relative_to(ROOT)}")
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(normalized, encoding="utf-8", newline="\n")
    print(f"WROTE: {path.relative_to(ROOT)}")
    return True


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Build the evidence-gated thesis status package."
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Fail if generated outputs differ from their canonical build.",
    )
    parser.add_argument(
        "--refresh-timestamp",
        action="store_true",
        help="Refresh generatedAt; normally it remains stable for byte-determinism.",
    )
    parser.add_argument(
        "--source-revision",
        help=(
            "Historical source-build commit. Generated outputs may be committed later; "
            "portable source hashes remain the validation anchor after squash merge."
        ),
    )
    args = parser.parse_args()

    data = build_snapshot(args.refresh_timestamp, args.source_revision)
    json_text = json.dumps(data, ensure_ascii=False, indent=2) + "\n"
    results = [
        write_or_check(SNAPSHOT_PATH, json_text, args.check),
        write_or_check(BASELINE_MD_PATH, baseline_markdown(data), args.check),
        write_or_check(TRACE_MD_PATH, trace_markdown(data), args.check),
    ]
    return 0 if all(results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
