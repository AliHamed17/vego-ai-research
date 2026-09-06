#!/usr/bin/env python3
"""Build the Study 1 signal dictionary and safe aggregate metrics.

This module is deliberately evidence-first.  It can describe the frozen code
contract without a private run log, but it never turns a missing log into
numeric science.  If a log is supplied, it must be bound by a user-supplied
accepted-run manifest before any aggregate is calculated.  Event text is never
written to the generated public artifacts.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
FRAMEWORK = ROOT / "VEGO-AI" / "framework"
if str(FRAMEWORK) not in sys.path:
    sys.path.insert(0, str(FRAMEWORK))

from qa_communication import build_episode_projection, load_event_stream  # noqa: E402

try:
    from extract_qa_escalation_features import detect_detector_v1  # noqa: E402
except ImportError:  # pragma: no cover - direct package import fallback
    detect_detector_v1 = None


NOT_AVAILABLE = "NOT_AVAILABLE_IN_WORKTREE"
AVAILABLE = "AVAILABLE_VERIFIED"
INVALID = "EVIDENCE_INVALID"

TRACEABILITY_COLUMNS = [
    "Category",
    "Variable/signal",
    "Measured from",
    "Unit",
    "Asking agent",
    "Answering agent",
    "Direct trigger?",
    "Action",
    "Not evidence of",
]

_SOURCE = "scripts/extract_qa_escalation_features.py"
_QA = "VEGO-AI/framework/qa_communication.py"
REVIEW_CONTEXT = {
    "origin_main_sha": "c34d3954b5e080d090017d2ea655d454d75a6b92",
    "pr_38_head": "a976494a624391efb0fb96e8f769512f52f52af0",
    "pr_41_head": "63da0105f25207e3cc6e67bb3ec499652d65124c",
    "pr_42_head": "de65a57d5ca7289cc6032baa7cc797499fdc6812",
    "canonical_draft": "pr-41 descendant; PR-42 is divergent and not merged wholesale",
    "source_definitions_head": "c34d3954b5e080d090017d2ea655d454d75a6b92",
}


class EvidenceError(RuntimeError):
    """Raised when a supplied private evidence chain cannot be verified."""


def _entry(
    *,
    category: str,
    hebrew_name: str,
    english_code_name: str,
    source_artifact: str,
    source_field: str,
    unit_of_analysis: str,
    calculation_rule: str,
    code_reference: str,
    measurement_kind: str,
    can_cooccur: bool | str,
    cooccurrence_scope: str,
    detector_role: str,
    direct_trigger: bool,
    candidate_for_review: bool | str,
    action: str,
    does_not_prove: str,
    evidence_availability: str = "CODE_DEFINED; RUN_EVIDENCE_STATUS_SEPARATE",
) -> dict[str, Any]:
    return {
        "category": category,
        "hebrew_name": hebrew_name,
        "english_code_name": english_code_name,
        "source_artifact": source_artifact,
        "source_field": source_field,
        "unit_of_analysis": unit_of_analysis,
        "calculation_rule": calculation_rule,
        "code_reference": code_reference,
        "measurement_kind": measurement_kind,
        "can_cooccur_with_other_signals": can_cooccur,
        "cooccurrence_scope": cooccurrence_scope,
        "detector_role": detector_role,
        "direct_detector_v1_trigger": direct_trigger,
        "candidate_for_human_review": candidate_for_review,
        "action": action,
        "does_not_prove": does_not_prove,
        "evidence_availability": evidence_availability,
    }


def signal_dictionary() -> dict[str, Any]:
    """Return the code-grounded dictionary for every requested layer."""

    entries: list[dict[str, Any]] = []

    raw = [
        (
            "RAW_QUESTION_ID",
            "מזהה השאלה",
            "question_id",
            "question",
            "Recorded on QUESTION_EMITTED and copied to ANSWER_RECEIVED.",
            f"{_QA}:77-105 (emit); {_QA}:122-134 (emit_answer)",
            "deterministic_event_field",
            "Identifies a question; it does not classify the question.",
        ),
        (
            "RAW_SOURCE_AGENT",
            "הסוכן השואל",
            "source_agent",
            "question",
            "Recorded from the producer route context.",
            f"{_QA}:77-105; {_QA}:150-156 (observe_exchange)",
            "deterministic_event_field",
            "Agent identity is provenance, not competence or correctness.",
        ),
        (
            "RAW_TARGET_AGENT",
            "הסוכן העונה",
            "target_agent",
            "question",
            "Recorded from the intended answering route; the matrix calls this answering agent.",
            f"{_QA}:77-105; {_QA}:150-156 (observe_exchange)",
            "deterministic_event_field",
            "A route target is not proof that an answer was received or was correct.",
        ),
        (
            "RAW_ANSWER_CONFIDENCE",
            "ביטחון התשובה",
            "answer_confidence",
            "answer",
            "Copied from the answer payload and constrained by the event schema.",
            f"{_QA}:94-99; schemas/qa-communication-event-v1.schema.json:35",
            "model_self_report",
            "The confidence label is not calibrated correctness or evidence quality.",
        ),
        (
            "RAW_ANSWER_EVIDENCE_REF",
            "הפניה לראיות התשובה",
            "answer_evidence_ref",
            "answer",
            "A deterministic SHA-256/length reference; null means no reference was recorded.",
            f"{_QA}:29-34,94-99; schemas/qa-communication-event-v1.schema.json:36,53-60",
            "deterministic_derived_field",
            "Presence or length is not a judgment of evidence quality or validity.",
        ),
        (
            "RAW_ROUND_INDEX",
            "מספר הסבב",
            "round_index",
            "question or answer",
            "Recorded by the route observer and retained on the paired event.",
            f"{_QA}:57-66,99; schemas/qa-communication-event-v1.schema.json:38",
            "deterministic_event_field",
            "A later round does not itself mean failure, disagreement, or human benefit.",
        ),
        (
            "RAW_TERMINATION_REASON",
            "סיבת סיום הפרק",
            "termination_reason",
            "Q&A episode",
            "Recorded only on EPISODE_TERMINATED and checked against the closed vocabulary.",
            f"{_QA}:67-76,136-137,185-195; schemas/qa-communication-event-v1.schema.json:40",
            "deterministic_control_state",
            "Termination state is not an outcome label or correctness judgment.",
        ),
    ]
    for code, he, field, unit, rule, ref, kind, not_prove in raw:
        entries.append(
            _entry(
                category="raw_event_field",
                hebrew_name=he,
                english_code_name=code,
                source_artifact=(_QA if field not in {"termination_reason"} else "schemas/qa-communication-event-v1.schema.json"),
                source_field=field,
                unit_of_analysis=unit,
                calculation_rule=rule,
                code_reference=ref,
                measurement_kind=kind,
                can_cooccur=True,
                cooccurrence_scope="Field values can coexist in one event; only downstream predicates may co-occur.",
                detector_role="descriptive_only",
                direct_trigger=False,
                candidate_for_review=False,
                action="Preserve for traceability; do not route a person from the raw field alone.",
                does_not_prove=not_prove,
            )
        )

    process = [
        (
            "S1_LOW_ANSWER_CONFIDENCE",
            "ביטחון תשובה נמוך",
            'any(row.get("answer_confidence") == "Low" for row in answers)',
            "answer → Q&A episode",
            f"{_SOURCE}:316-321 (detect_detector_v1)",
            "model_self_report",
            "strong; may co-occur with S3, S6, and S7 on one complete episode",
            "Low confidence on any answer in a complete episode.",
            "Candidate alert only; no correctness or human-benefit conclusion.",
        ),
        (
            "S2_MEDIUM_ANSWER_CONFIDENCE",
            "ביטחון תשובה בינוני",
            'any(row.get("answer_confidence") == "Medium" for row in answers)',
            "answer → Q&A episode",
            f"{_SOURCE}:323-328 (detect_detector_v1)",
            "model_self_report",
            "weak; may co-occur with S6, but S2 is suppressed from reason_codes when a strong signal fires",
            "Medium confidence on any answer in a complete episode.",
            "A weak candidate alert, not an error, correctness, or calibrated probability.",
        ),
        (
            "S3_MISSING_ANSWER_EVIDENCE",
            "היעדר הפניית ראיות בתשובה",
            'any((ref := row.get("answer_evidence_ref")) is None or ref.get("length", 0) == 0 for row in answers)',
            "answer → Q&A episode",
            f"{_SOURCE}:319-322 (detect_detector_v1)",
            "deterministic_derived_field",
            "strong; can co-occur with S1, S6, and S7",
            "Any answer has no recorded evidence reference or a zero-length reference.",
            "Missing reference is a grounding-observability condition, not proof that the answer lacks evidence.",
        ),
        (
            "S6_MULTIPLE_QA_ROUNDS",
            "יותר מסבב שאלות ותשובות אחד",
            'episode.get("round_count", 0) > 1',
            "Q&A episode",
            f"{_SOURCE}:323-328 (detect_detector_v1); {_SOURCE}:351-364 (projection)",
            "deterministic_derived_field",
            "weak; can co-occur with any strong signal or S2",
            "The maximum observed round count for the episode is greater than one.",
            "Multiple rounds are not proof of disagreement, failure, burden, or quality.",
        ),
        (
            "S7_TERMINATED_MAX_ROUNDS",
            "אי־התכנסות עד הגבלת הסבבים",
            'episode.get("termination_reason") == "TERMINATED_MAX_ROUNDS"',
            "Q&A episode",
            f"{_SOURCE}:319-324 (detect_detector_v1); {_QA}:20,185-192",
            "deterministic_control_state",
            "strong; can co-occur with S1, S3, and S6",
            "A complete episode ended because the configured maximum was reached.",
            "It is not proof that a human would resolve the issue or that the system is wrong.",
        ),
    ]
    for code, he, rule, unit, ref, kind, cooccur, action_rule, not_prove in process:
        entries.append(
            _entry(
                category="communication_process_signal",
                hebrew_name=he,
                english_code_name=code,
                source_artifact=_SOURCE,
                source_field=(
                    "answer_confidence"
                    if code.startswith("S1") or code.startswith("S2")
                    else "answer_evidence_ref"
                    if code.startswith("S3")
                    else "round_count"
                    if code.startswith("S6")
                    else "termination_reason"
                ),
                unit_of_analysis=unit,
                calculation_rule=rule,
                code_reference=ref,
                measurement_kind=kind,
                can_cooccur=True,
                cooccurrence_scope=cooccur,
                detector_role="direct_trigger",
                direct_trigger=True,
                candidate_for_review=True,
                action=action_rule + " The result is a candidate label only.",
                does_not_prove=not_prove,
            )
        )

    context = [
        (
            "C1_MAPPING_CERTAINTY",
            "ודאות מיפוי Agent 2",
            "mapping_certainty",
            "guideline / mapping item",
            "VEGO-AI/eval_output/*/agentB_best_guidelines.json",
            f"{_SOURCE}:209-227 (_mapping_certainty_count); VEGO-AI/framework/agent2_domain_advisor.py:38-44,53-54",
            "semantic_model_output",
            "A numeric mapping confidence; the future-corpus comparator uses < 0.7 in the helper.",
            "Context-only; never a Detector-v1 trigger and never a correctness label.",
        ),
        (
            "C2_AGENT4_CLASSIFICATION_CONFIDENCE",
            "ביטחון סיווג Agent 4",
            "variability_classifications[].confidence",
            "variability classification",
            "VEGO-AI/eval_output/*/agentD_variability_classes*.json",
            f"{_SOURCE}:230-237 (_agent4_confidence); VEGO-AI/framework/agent4_variability_explorer.py:524-531",
            "model_self_report",
            "Agent-4 classification confidence is reported separately from Q&A answer confidence.",
            "Context-only; never a Detector-v1 trigger and never a performance measure.",
        ),
        (
            "C3_AGENT4_REVIEW_FLAGS",
            "דגלי בדיקה של Agent 4",
            "requires_human_review; flag_for_guidelines_update",
            "variability classification",
            "VEGO-AI/eval_output/*/agentD_variability_classes*.json",
            "VEGO-AI/framework/human_review_queue.py:278-325 (build_review_items)",
            "semantic_model_output",
            "Flags are copied into a separate Agent-4 review item when the queue builder policy selects it.",
            "Context-only; not a Detector-v1 trigger and not proof of an error or guideline defect.",
        ),
    ]
    for code, he, field, unit, artifact, ref, kind, rule, not_prove in context:
        entries.append(
            _entry(
                category="context_only_variable",
                hebrew_name=he,
                english_code_name=code,
                source_artifact=artifact,
                source_field=field,
                unit_of_analysis=unit,
                calculation_rule=rule,
                code_reference=ref,
                measurement_kind=kind,
                can_cooccur=True,
                cooccurrence_scope="May be reported alongside process signals; excluded from Detector-v1 logic.",
                detector_role="context_only",
                direct_trigger=False,
                candidate_for_review=False,
                action="Report as context only; do not promote to an alert without a separately approved rule.",
                does_not_prove=not_prove,
                evidence_availability="CODE_DEFINED; REQUIRES_FROZEN_EVAL_OUTPUT_NOT_PRESENT_IN_THIS_WORKTREE",
            )
        )

    semantic = [
        (
            "MAPPING_SATISFIED",
            "מיפוי מסופק",
            "existing_mapping[].compliance_status == Satisfied",
            "mapping item",
            "VEGO-AI/framework/orchestrator.py:279-297",
            "semantic_model_output",
            "Mutually exclusive with other compliance_status values for one mapping item; may co-occur with episode alerts.",
            'entry.get("compliance_status") == "Satisfied"',
        ),
        (
            "MAPPING_PARTIALLY_SATISFIED",
            "מיפוי מסופק חלקית",
            "existing_mapping[].compliance_status == Partially-Satisfied",
            "mapping item",
            "VEGO-AI/framework/orchestrator.py:279-297",
            "semantic_model_output",
            "Mutually exclusive with other compliance_status values for one mapping item; may co-occur with episode alerts.",
            'entry.get("compliance_status") == "Partially-Satisfied"',
        ),
        (
            "MAPPING_NON_SATISFIED",
            "מיפוי לא מסופק",
            "existing_mapping[].compliance_status == Non-Satisfied (or other non-matching value is counted in the fallback bucket)",
            "mapping item",
            "VEGO-AI/framework/orchestrator.py:288-297",
            "semantic_model_output",
            "Mutually exclusive with other compliance_status values for one mapping item; may co-occur with episode alerts.",
            'entry.get("compliance_status") == "Non-Satisfied"; orchestrator.py counts other values in the not_satisfied fallback bucket',
        ),
        (
            "MAPPING_ALTERNATIVE",
            "חלופה במיפוי",
            "dominant_fragment_label == Alternative / fragment label in Agent-4 pattern output",
            "fragment or pattern",
            "VEGO-AI/framework/agent4_variability_explorer.py:359-366,411-417",
            "semantic_model_output",
            "May co-occur with compliance outputs at different units; not a single-valued detector input.",
            'pattern.get("dominant_fragment_label") == "Alternative" or fragment label is "Alternative"',
        ),
        (
            "MAPPING_CERTAINTY",
            "ודאות המיפוי",
            "existing_mapping[].mapping_certainty",
            "mapping item",
            "VEGO-AI/framework/agent2_domain_advisor.py:37-44,140-146",
            "semantic_model_output",
            "May co-occur with compliance labels; context comparator C1 remains outside Detector-v1.",
            'entry.get("mapping_certainty")',
        ),
        (
            "SOURCE_TARGET_ALIGNMENT",
            "התאמת מקור–יעד",
            "No canonical semantic alignment field; route metadata is source_agent/target_agent",
            "route",
            _QA,
            "deterministic_event_field",
            "Route metadata can co-occur with every semantic output; semantic alignment itself is not operationalized.",
            "No canonical semantic alignment calculation; retain source_agent and target_agent as route metadata only",
        ),
        (
            "UNCOVERED_FRAGMENTS",
            "שברים שלא כוסו",
            "PipelineState.uncovered_fragments and audit_uncovered_fragments output",
            "case / fragment",
            "VEGO-AI/framework/orchestrator.py:248-274,607",
            "semantic_model_output",
            "May co-occur with mapping and detector outputs at different units.",
            "Read state.uncovered_fragments[case_id] from the audited fragment output",
        ),
    ]
    for code, he, field, unit, ref, kind, cooccur, action in semantic:
        entries.append(
            _entry(
                category="semantic_mapping_output",
                hebrew_name=he,
                english_code_name=code,
                source_artifact=ref.split(":", 1)[0],
                source_field=field,
                unit_of_analysis=unit,
                calculation_rule=action,
                code_reference=ref,
                measurement_kind=kind,
                can_cooccur=True,
                cooccurrence_scope=cooccur,
                detector_role="descriptive_only" if code != "SOURCE_TARGET_ALIGNMENT" else "unavailable",
                direct_trigger=False,
                candidate_for_review=False,
                action="Keep as an analysis output; any human-review use needs an explicit, separately governed policy.",
                does_not_prove=(
                    "It does not prove correctness, error, reviewer need, or generalization."
                    if code != "SOURCE_TARGET_ALIGNMENT"
                    else "A route does not prove semantic alignment, answer quality, or human need."
                ),
                evidence_availability=(
                    "NOT_OPERATIONALIZED_IN_CANONICAL_CODE"
                    if code == "SOURCE_TARGET_ALIGNMENT"
                    else "CODE_DEFINED; REQUIRES_FROZEN_PIPELINE_OUTPUT"
                ),
            )
        )

    operational = [
        (
            "CANDIDATE_FOR_HUMAN_REVIEW",
            "מועמד לבדיקה אנושית",
            "Detector-v1 candidate_alert == true for a complete episode",
            "Q&A episode",
            f"{_SOURCE}:330-339",
            "deterministic_derived_field",
            "Derived from co-occurring S1/S2/S3/S6/S7; it is not a verdict.",
            "Reporting label only; it does not create an automatic correction.",
        ),
        (
            "Q_AND_A_QUEUE_BINDING",
            "חיבור לתור בדיקה",
            "No Q&A Detector-v1 enqueue call; separate Agent-4 queue builder exists",
            "Q&A episode / review item",
            "VEGO-AI/framework/human_review_queue.py:226-336,354-366",
            "deterministic_control_path",
            "May be discussed alongside alerts, but is not automatically populated by the Q&A detector.",
            "No automatic queue or correction is implemented for these Q&A signals; this is a reporting label only.",
        ),
        (
            "AUTOMATIC_SOURCE_OR_MODEL_CHANGE",
            "שינוי אוטומטי במקור או במודל",
            "No canonical field or call path",
            "run",
            "Not implemented in the reviewed code",
            "unavailable",
            "No co-occurrence semantics; unavailable by design.",
            "No source, guideline, target, or model is changed automatically by this package.",
        ),
    ]
    for code, he, field, unit, ref, kind, cooccur, action in operational:
        entries.append(
            _entry(
                category="operational_action",
                hebrew_name=he,
                english_code_name=code,
                source_artifact=ref.split(":", 1)[0] if ":" in ref else ref,
                source_field=field,
                unit_of_analysis=unit,
                calculation_rule=action,
                code_reference=ref,
                measurement_kind=kind,
                can_cooccur=True,
                cooccurrence_scope=cooccur,
                detector_role="descriptive_only" if code != "AUTOMATIC_SOURCE_OR_MODEL_CHANGE" else "unavailable",
                direct_trigger=False,
                candidate_for_review=(code == "CANDIDATE_FOR_HUMAN_REVIEW"),
                action=action,
                does_not_prove=(
                    "A candidate label is not a human decision, a queue insertion, correctness, or benefit."
                    if code == "CANDIDATE_FOR_HUMAN_REVIEW"
                    else "No automatic queue, correction, source change, target change, or model replacement is implied."
                ),
                evidence_availability=(
                    "CODE_DEFINED; Q&A_QUEUE_BINDING_NOT_PRESENT"
                    if code != "AUTOMATIC_SOURCE_OR_MODEL_CHANGE"
                    else "NOT_OPERATIONALIZED_IN_CANONICAL_CODE"
                ),
            )
        )

    return {
        "schema": "vego-ai-study1-signal-dictionary-v1",
        "title": "VEGO-AI Study 1 signal and measurement dictionary",
        "review_context": REVIEW_CONTEXT,
        "evidence_status": NOT_AVAILABLE,
        "evidence_boundary": (
            "Code-grounded definitions are available. Numeric Study 1 evidence is not generated "
            "unless a private accepted-run event log and binding manifest are supplied and verified."
        ),
        "claim_boundary": (
            "This dictionary documents observability and candidate-review mechanics only. It does not "
            "establish accuracy, human benefit, reduced burden, generalization, or policy superiority."
        ),
        "detector_logic": {
            "strong_alert": "S1_LOW_ANSWER_CONFIDENCE OR S3_MISSING_ANSWER_EVIDENCE OR S7_TERMINATED_MAX_ROUNDS",
            "weak_alert": "NOT STRONG_ALERT AND (S2_MEDIUM_ANSWER_CONFIDENCE OR S6_MULTIPLE_QA_ROUNDS)",
            "candidate_alert": "STRONG_ALERT OR WEAK_ALERT",
            "non_triggering_context": ["C1_MAPPING_CERTAINTY", "C2_AGENT4_CLASSIFICATION_CONFIDENCE", "C3_AGENT4_REVIEW_FLAGS"],
            "non_triggering_semantics": ["MAPPING_ALTERNATIVE", "MAPPING_NON_SATISFIED", "SOURCE_TARGET_ALIGNMENT"],
            "source_reference": f"{_SOURCE}:309-339",
        },
        "required_layers": [
            "raw_event_field",
            "communication_process_signal",
            "context_only_variable",
            "semantic_mapping_output",
            "operational_action",
        ],
        "entries": entries,
        "entries_by_code": {entry["english_code_name"]: entry for entry in entries},
    }


def traceability_matrix() -> list[dict[str, str]]:
    """Return the explicit, non-RTL route-oriented traceability matrix."""

    dictionary = signal_dictionary()
    rows: list[dict[str, str]] = []
    for entry in dictionary["entries"]:
        code = entry["english_code_name"]
        category = entry["category"]
        if code.startswith("RAW_"):
            asking, answering = "Recorded source_agent", "Recorded target_agent"
        elif code.startswith("S") and code[1:2].isdigit():
            asking, answering = "Recorded producer (Agent 2/3/4)", "Recorded target (Agent 1/2)"
        elif code.startswith("C"):
            asking, answering = "Not applicable", "Not applicable"
        else:
            asking, answering = "Not applicable", "Not applicable"
        rows.append(
            {
                "Category": category,
                "Variable/signal": code,
                "Measured from": f"{entry['source_artifact']} :: {entry['source_field']}",
                "Unit": entry["unit_of_analysis"],
                "Asking agent": asking,
                "Answering agent": answering,
                "Direct trigger?": "YES" if entry["direct_detector_v1_trigger"] else "NO",
                "Action": entry["action"],
                "Not evidence of": entry["does_not_prove"],
            }
        )
    return rows


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _manifest_artifact(manifest: dict[str, Any]) -> tuple[str, str]:
    if manifest.get("accepted_run") is not True:
        raise EvidenceError("binding manifest is not explicitly marked accepted_run")
    for key in ("run_kind", "evidence_class", "execution_class", "run_type"):
        marker = manifest.get(key)
        if isinstance(marker, str) and marker.strip().casefold() in {
            "fake_preflight",
            "local_only",
            "local-only",
            "preflight",
        }:
            raise EvidenceError("fake-preflight evidence cannot be used as an accepted scientific run")
    identity = manifest.get("run_identity")
    if not isinstance(identity, dict):
        raise EvidenceError("binding manifest lacks run_identity")
    if identity.get("accepted_replacement") is not True or identity.get("run_class") != "accepted_replacement_real_run" or identity.get("fake_preflight") is True:
        raise EvidenceError("binding manifest run_identity is not an accepted replacement")
    run_id = identity.get("run_id")
    if not isinstance(run_id, str) or not run_id:
        raise EvidenceError("binding manifest lacks run_id")
    artifacts = manifest.get("artifacts")
    if not isinstance(artifacts, dict):
        raise EvidenceError("binding manifest lacks artifacts")
    item = artifacts.get("qa_events_jsonl")
    if not isinstance(item, dict) or not isinstance(item.get("sha256"), str):
        raise EvidenceError("binding manifest lacks qa_events_jsonl.sha256")
    if not re.fullmatch(r"[0-9a-fA-F]{64}", item["sha256"]):
        raise EvidenceError("binding manifest contains an invalid event-log hash")
    return run_id, item["sha256"].lower()


def load_verified_events(event_log: Path, binding_manifest: Path) -> list[dict[str, Any]]:
    """Verify an explicitly accepted event log and return validated events."""

    if not event_log.is_file() or not binding_manifest.is_file():
        raise EvidenceError("accepted event log or binding manifest is unavailable")
    try:
        manifest = json.loads(binding_manifest.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise EvidenceError("binding manifest cannot be read") from exc
    run_id, expected_hash = _manifest_artifact(manifest)
    observed_hash = _sha256_file(event_log)
    if observed_hash != expected_hash:
        raise EvidenceError("event-log SHA-256 does not match the accepted-run manifest")
    try:
        events = load_event_stream(event_log)
    except Exception as exc:  # noqa: BLE001 - validation boundary must fail closed
        raise EvidenceError("event log fails schema/lifecycle validation") from exc
    if not events:
        raise EvidenceError("accepted event log is empty")
    if {event.get("run_id") for event in events} != {run_id}:
        raise EvidenceError("event log run_id does not match the accepted-run manifest")
    return events


def _safe_id(value: Any, prefix: str = "ID") -> str:
    if value is None or value == "":
        return "NOT_RECORDED"
    return f"{prefix}-{hashlib.sha256(str(value).encode('utf-8')).hexdigest()[:16]}"


def _table(rows: list[dict[str, Any]], denominator: str) -> dict[str, Any]:
    return {"evidence_status": AVAILABLE, "denominator": denominator, "rows": rows}


def _empty_tables(status: str) -> dict[str, Any]:
    names = (
        "episodes",
        "agent_questions",
        "agent_answers",
        "route_matrix",
        "questions_answers_by_case_episode_route_round",
        "confidence_by_episode_round",
        "evidence_reference_lengths",
        "confidence_evidence_termination",
        "signal_cooccurrence",
        "termination_states",
        "cases_with_q_and_a",
        "cases_without_q_and_a",
    )
    return {name: {"evidence_status": status, "denominator": status, "rows": []} for name in names}


def _evidence_bucket(ref: dict[str, Any] | None) -> str:
    if ref is None:
        return "MISSING_REFERENCE"
    length = ref.get("length")
    if length == 0:
        return "ZERO_LENGTH_REFERENCE"
    if not isinstance(length, int) or length < 0:
        return "INVALID_REFERENCE"
    if length <= 32:
        return "1_TO_32"
    if length <= 256:
        return "33_TO_256"
    return "257_PLUS"


def aggregate_verified_events(events: list[dict[str, Any]]) -> dict[str, Any]:
    """Create aggregate-only tables from an already verified event stream."""

    if detect_detector_v1 is None:  # pragma: no cover - import guard
        raise EvidenceError("Detector-v1 implementation is unavailable")
    projections = build_episode_projection(events)
    complete = [row for row in projections if row.get("scientific_complete")]
    denominator = "complete_scientific_episodes"
    detector_rows = {row["episode_id"]: detect_detector_v1(row) for row in complete}

    episode_rows: list[dict[str, Any]] = []
    for episode in complete:
        questions = [
            event for event in events
            if event.get("episode_id") == episode["episode_id"]
            and event.get("event_type") == "QUESTION_EMITTED"
        ]
        case_ids = sorted({event.get("case_id") for event in questions if event.get("case_id")})
        sources = sorted({event.get("source_agent") for event in questions if event.get("source_agent")})
        targets = sorted({event.get("target_agent") for event in questions if event.get("target_agent")})
        detection = detector_rows[episode["episode_id"]]
        episode_rows.append(
            {
                "episode_id": _safe_id(episode["episode_id"], "EP"),
                "case_ids": [_safe_id(case_id, "CASE") for case_id in case_ids],
                "asking_agents": sources,
                "answering_agents": targets,
                "question_count": episode["question_count"],
                "answer_count": episode["answer_count"],
                "max_round": episode["round_count"],
                "termination_reason": episode["termination_reason"],
                "completeness": "COMPLETE",
                "signals_fired": detection["all_signals_fired"],
                "detector_classification": detection["classification"],
            }
        )

    question_counts = Counter(
        event.get("source_agent") or "UNKNOWN"
        for event in events
        if event.get("event_type") == "QUESTION_EMITTED"
    )
    answer_counts = Counter(
        event.get("target_agent") or "UNKNOWN"
        for event in events
        if event.get("event_type") == "ANSWER_RECEIVED"
    )
    route_counts: Counter[tuple[str, str]] = Counter()
    for event in events:
        if event.get("event_type") == "QUESTION_EMITTED":
            route_counts[(event.get("source_agent") or "UNKNOWN", event.get("target_agent") or "UNKNOWN")] += 1

    route_rows = [
        {
            "asking_agent": asking,
            "answering_agent": answering,
            "question_count": count,
            "answer_count": sum(
                1
                for event in events
                if event.get("event_type") == "ANSWER_RECEIVED"
                and (event.get("source_agent") or "UNKNOWN") == asking
                and (event.get("target_agent") or "UNKNOWN") == answering
            ),
        }
        for (asking, answering), count in sorted(route_counts.items())
    ]

    q_by_id = {
        event.get("question_id"): event
        for event in events
        if event.get("event_type") == "QUESTION_EMITTED"
    }
    a_by_id = {
        event.get("question_id"): event
        for event in events
        if event.get("event_type") == "ANSWER_RECEIVED"
    }
    qar_groups: Counter[tuple[str, str, str, str, int]] = Counter()
    for question_id, question in q_by_id.items():
        if question.get("episode_id") not in detector_rows:
            continue
        answer = a_by_id.get(question_id)
        key = (
            _safe_id(question.get("case_id"), "CASE"),
            _safe_id(question.get("episode_id"), "EP"),
            question.get("source_agent") or "UNKNOWN",
            question.get("target_agent") or "UNKNOWN",
            int(question.get("round_index") or 0),
        )
        qar_groups[key] += 1
        if answer is None:  # Defensive; validated complete episodes normally cannot reach this.
            continue
    qar_rows = [
        {
            "case_id": case_id,
            "episode_id": episode_id,
            "asking_agent": asking,
            "answering_agent": answering,
            "round_index": round_index,
            "question_count": count,
            "answer_count": count,
        }
        for (case_id, episode_id, asking, answering, round_index), count in sorted(qar_groups.items())
    ]

    confidence_groups: Counter[tuple[str, int, str]] = Counter()
    evidence_groups: Counter[str] = Counter()
    confidence_evidence_termination: Counter[tuple[str, str, str]] = Counter()
    for episode in complete:
        for answer in episode["answers"]:
            confidence = answer.get("answer_confidence") or "UNKNOWN"
            round_index = int(answer.get("round_index") or 0)
            confidence_groups[(_safe_id(episode["episode_id"], "EP"), round_index, confidence)] += 1
            ref = answer.get("answer_evidence_ref")
            bucket = _evidence_bucket(ref)
            evidence_groups[bucket] += 1
            confidence_evidence_termination[(confidence, bucket, episode["termination_reason"])] += 1

    confidence_rows = [
        {"episode_id": episode_id, "round_index": round_index, "confidence": confidence, "answer_count": count}
        for (episode_id, round_index, confidence), count in sorted(confidence_groups.items())
    ]
    evidence_rows = [
        {"evidence_reference_bucket": bucket, "answer_count": count}
        for bucket, count in sorted(evidence_groups.items())
    ]
    confidence_evidence_rows = [
        {
            "confidence": confidence,
            "evidence_reference_bucket": bucket,
            "termination_reason": termination,
            "answer_count": count,
        }
        for (confidence, bucket, termination), count in sorted(confidence_evidence_termination.items())
    ]

    cooccurrence = Counter(tuple(detector_rows[episode_id]["all_signals_fired"]) for episode_id in detector_rows)
    cooccurrence_rows = [
        {"signals_fired": list(signals), "episode_count": count}
        for signals, count in sorted(cooccurrence.items())
    ]
    termination_counts = Counter(episode["termination_reason"] for episode in complete)
    termination_rows = [
        {"termination_reason": reason, "episode_count": count}
        for reason, count in sorted(termination_counts.items())
    ]

    # The Q&A stream does not establish the universe of cases that produced no
    # question.  The absence category must therefore remain unavailable rather
    # than being reported as zero.
    case_rows = [
        {
            "case_id": _safe_id(case_id, "CASE"),
            "has_q_and_a": True,
        }
        for case_id in sorted(
            {
                event.get("case_id")
                for event in events
                if event.get("event_type") == "QUESTION_EMITTED" and event.get("case_id")
            }
        )
    ]

    tables = {
        "episodes": _table(episode_rows, denominator),
        "agent_questions": _table(
            [{"asking_agent": agent, "question_count": count} for agent, count in sorted(question_counts.items())],
            "all_validated_question_events",
        ),
        "agent_answers": _table(
            [{"answering_agent": agent, "answer_count": count} for agent, count in sorted(answer_counts.items())],
            "all_validated_answer_events",
        ),
        "route_matrix": _table(route_rows, "all_validated_question_events"),
        "questions_answers_by_case_episode_route_round": _table(qar_rows, denominator),
        "confidence_by_episode_round": _table(confidence_rows, "complete_episode_answers"),
        "evidence_reference_lengths": _table(evidence_rows, "complete_episode_answers"),
        "confidence_evidence_termination": _table(confidence_evidence_rows, "complete_episode_answers"),
        "signal_cooccurrence": _table(cooccurrence_rows, denominator),
        "termination_states": _table(termination_rows, denominator),
        "cases_with_q_and_a": _table(case_rows, "cases_observed_in_question_events"),
        "cases_without_q_and_a": {
            "evidence_status": "NOT_AVAILABLE_CASE_UNIVERSE_NOT_BOUND",
            "denominator": "NOT_AVAILABLE_CASE_UNIVERSE_NOT_BOUND",
            "rows": [],
        },
    }
    return {
        "schema": "vego-ai-study1-safe-aggregate-metrics-v1",
        "evidence_status": AVAILABLE,
        "denominator": denominator,
        "tables": tables,
        "claim_boundary": (
            "Retrospective descriptive observability only. Confidence is an LLM self-report; "
            "evidence presence/length is not evidence quality. No correctness, benefit, burden, "
            "generalization, or policy-superiority claim is permitted."
        ),
    }


def build_metrics(events: list[dict[str, Any]] | None, *, evidence_status: str = NOT_AVAILABLE) -> dict[str, Any]:
    if evidence_status != AVAILABLE or events is None:
        return {
            "schema": "vego-ai-study1-safe-aggregate-metrics-v1",
            "evidence_status": evidence_status,
            "denominator": evidence_status,
            "tables": _empty_tables(evidence_status),
            "claim_boundary": (
                "No numeric Study 1 values are available in this worktree. A private accepted event "
                "log and binding manifest are required before any aggregate is calculated."
            ),
        }
    return aggregate_verified_events(events)


def _write_hebrew_note(path: Path, dictionary: dict[str, Any], metrics: dict[str, Any]) -> None:
    if metrics["evidence_status"] == NOT_AVAILABLE:
        availability = "קובץ האירועים הפרטי של ההרצה שהתקבלה אינו נמצא ב-worktree הנבדק."
    elif metrics["evidence_status"] == INVALID:
        availability = "שרשרת הראיות שסופקה לא אומתה; לא חושבו ערכים מספריים."
    else:
        availability = "שרשרת הראיות אומתה; יש לקרוא את הטבלאות בהתאם לסטטוס שלהן."
    path.write_text(
        "\n".join(
            [
                '<div dir="rtl">',
                "# הערה טכנית ל-Claude — מילון אותות ומדידה של VEGO-AI Study 1",
                "",
                "**סטטוס ראיות:** `" + str(metrics["evidence_status"]) + "`.",
                "הגדרות הקוד מתועדות להלן, אך סטטוס הנתונים הוא: " + availability,
                "",
                "## חמש שכבות המדידה",
                "",
                "1. **שדות אירוע גולמיים:** מזהה שאלה, סוכן שואל, סוכן עונה, ביטחון תשובה, הפניית ראיות, מספר סבב וסיבת סיום.",
                "2. **אותות תהליך:** `S1`, `S2`, `S3`, `S6`, `S7` מחושבים בדיוק כפי שמופיע ב-`scripts/extract_qa_escalation_features.py`.",
                "3. **משתני הקשר:** `C1`, `C2`, `C3` מוצגים לצד האירועים בלבד ואינם קלט ל-Detector-v1.",
                "4. **פלטים סמנטיים:** `Satisfied`, `Partially-Satisfied`, `Non-Satisfied`, `Alternative`, ודאות מיפוי, התאמת מקור–יעד ושברים שלא כוסו. אלה פלטי ניתוח, לא תוויות שגיאה אוטומטיות.",
                "5. **פעולה תפעולית:** המונח היחיד המותר הוא ‘מועמד לבדיקה אנושית’. אין שינוי אוטומטי במקור, בהנחיה, ביעד או במודל.",
                "",
                "## איך ההתראה החכמה פועלת",
                "",
                '<div dir="ltr">STRONG_ALERT = S1 OR S3 OR S7</div>',
                '<div dir="ltr">WEAK_ALERT = no strong signal AND (S2 OR S6)</div>',
                '<div dir="ltr">NO_ALERT otherwise</div>',
                "",
                "ההתראה היא מועמד בלבד. עבור אותות ה-Q&A אין חיבור אוטומטי לתור או תיקון; זהו reporting label בלבד. קיים ב-code תור נפרד עבור Agent 4, אך הוא אינו מוזן אוטומטית מ-Detector-v1.",
                "",
                "## גבול הפרשנות",
                "",
                "ביטחון הוא דיווח עצמי של ה-LLM. נוכחות או אורך הפניה לראיות אינם מדד לאיכות הראיות. אין להסיק דיוק, תועלת לאדם, הפחתת עומס, הכללה או עדיפות מדיניות. `Alternative` ו-`Non-Satisfied` אינם שגיאה כשלעצמם.",
                "",
                "## זמינות הנתונים",
                "",
                "הטבלאות המצורפות מציינות `NOT_AVAILABLE_IN_WORKTREE` ואין בהן אפסים מומצאים. לאחר קבלת קובץ אירועים פרטי ומניפסט binding מאושר, יש לאמת SHA-256, run_id ושלמות lifecycle לפני חישוב כל ערך.",
                "",
                "המסמך הוא טיוטה טכנית מסייעת-מכונה; המשמעות העברית דורשת ביקורת אנושית של Ali/המנחים.",
                "</div>",
                "",
            ]
        ),
        encoding="utf-8",
    )


def write_outputs(output_dir: Path, *, event_log: Path | None = None, binding_manifest: Path | None = None) -> dict[str, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    evidence_status = NOT_AVAILABLE
    events: list[dict[str, Any]] | None = None
    error: str | None = None
    if event_log is not None:
        if binding_manifest is None:
            evidence_status = INVALID
            error = "binding manifest is required when --event-log is supplied"
        else:
            try:
                events = load_verified_events(event_log, binding_manifest)
                evidence_status = AVAILABLE
            except EvidenceError as exc:
                evidence_status = INVALID
                error = str(exc)

    dictionary = signal_dictionary()
    dictionary["evidence_status"] = evidence_status
    metrics = build_metrics(events, evidence_status=evidence_status)
    if error:
        metrics["validation_error"] = "private evidence validation failed; no numeric rows emitted"
    matrix = traceability_matrix()

    dictionary_path = output_dir / "study1-signal-dictionary-v1.json"
    matrix_path = output_dir / "study1-signal-traceability-matrix-v1.csv"
    metrics_path = output_dir / "study1-signal-metrics-v1.json"
    hebrew_path = output_dir / "2026-09-06-study1-signal-technical-note.he.md"

    dictionary_path.write_text(json.dumps(dictionary, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    with matrix_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=TRACEABILITY_COLUMNS)
        writer.writeheader()
        writer.writerows(matrix)
    metrics_path.write_text(json.dumps(metrics, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    _write_hebrew_note(hebrew_path, dictionary, metrics)
    return {
        "dictionary": dictionary_path,
        "matrix": matrix_path,
        "metrics": metrics_path,
        "hebrew_note": hebrew_path,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=ROOT / "docs" / "research" / "phd-proposal")
    parser.add_argument("--event-log", type=Path, default=None, help="Private accepted qa_events.jsonl; never copied to output")
    parser.add_argument("--binding-manifest", type=Path, default=None, help="Private accepted-run binding manifest")
    args = parser.parse_args(argv)
    paths = write_outputs(args.output_dir, event_log=args.event_log, binding_manifest=args.binding_manifest)
    for key, path in paths.items():
        print(f"{key}: {path.as_posix()}")
    if args.event_log is not None:
        # A caller that supplied evidence receives a non-zero status when the
        # chain cannot be proven; the safe artifacts remain non-numeric.
        metrics = json.loads(paths["metrics"].read_text(encoding="utf-8"))
        if metrics["evidence_status"] == INVALID:
            return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
