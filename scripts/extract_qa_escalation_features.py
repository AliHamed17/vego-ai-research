#!/usr/bin/env python3
"""Extract frozen inter-agent Q&A observability and a transparent alert scaffold.

The extractor is deliberately offline and read-only.  It never calls an agent,
uses a network/API, fills a human label, or changes the frozen baseline.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import pathlib
import re
import sys
from collections import Counter
from typing import Any

try:
    from qa_communication import build_episode_projection, load_event_stream
except ImportError:  # pragma: no cover - direct script execution without repo path
    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "VEGO-AI" / "framework"))
    from qa_communication import build_episode_projection, load_event_stream

SETTINGS = ("ucd_ch", "ucd_pw", "cd_ch", "cd_pw")
MAX_QA_ROUNDS = 10
EVENT_FIELDS = (
    "event_id", "question_id", "source_agent", "source_stage", "target_agent", "scope",
    "case_id", "guideline_id", "pattern_id", "question_text", "answer_text",
    "answer_confidence", "answer_evidence", "evidence_present", "round_index", "answered",
    "follow_up_observed", "repeated_question", "converged", "unresolved",
    "source_artifact_path", "source_artifact_sha256",
)


class ExtractionError(RuntimeError):
    """Raised when a frozen Q&A record is malformed or untraceable."""


class EvaluationError(RuntimeError):
    """Raised when a requested evaluation exceeds the available labels."""


def sha256_file(path: pathlib.Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _event_id(source_path: str, index: int, question_id: str | None, question_text: str | None) -> str:
    payload = f"{source_path}\0{index}\0{question_id or ''}\0{question_text or ''}".encode()
    return "QA-" + hashlib.sha256(payload).hexdigest()[:20]


def _relative_path(path: pathlib.Path, root: pathlib.Path) -> str:
    return path.relative_to(root.parent).as_posix()


def _answer_for(question_id: str | None, histories: list[dict[str, Any]]) -> dict[str, Any] | None:
    if not question_id:
        return None
    return next((row for row in histories if row.get("question_id") == question_id or row.get("id") == question_id), None)


def make_event(
    *,
    source_path: str,
    source_agent: str,
    source_stage: str,
    target_agent: str,
    scope: str,
    question: dict[str, Any],
    answer: dict[str, Any] | None,
    source_hash: str | None = None,
    case_id: str | None = None,
    guideline_id: str | None = None,
    pattern_id: str | None = None,
    round_index: int | None = None,
) -> dict[str, Any]:
    question_id = question.get("id") or question.get("question_id")
    question_text = question.get("question") or question.get("question_text")
    answer_text = answer.get("answer") if answer else None
    answer_evidence = None
    if answer:
        answer_evidence = answer.get("evidence") or answer.get("supporting_evidence")
    event = {
        "event_id": _event_id(source_path, int(question.get("_index", 0)), question_id, question_text),
        "question_id": question_id,
        "source_agent": source_agent,
        "source_stage": source_stage,
        "target_agent": target_agent,
        "scope": scope,
        "case_id": case_id,
        "guideline_id": guideline_id,
        "pattern_id": pattern_id,
        "question_text": question_text,
        "answer_text": answer_text,
        "answer_confidence": answer.get("confidence") if answer else None,
        "answer_evidence": answer_evidence,
        "evidence_present": (bool(answer_evidence) if answer else None),
        "round_index": round_index,
        "answered": answer is not None,
        "answer_status": "ANSWER_PERSISTED" if answer is not None else "ANSWER_NOT_PERSISTED",
        "follow_up_observed": None,
        "repeated_question": None,
        "converged": None,
        "unresolved": (not bool(answer)) if answer is not None else None,
        "source_artifact_path": source_path,
        "source_artifact_sha256": source_hash,
    }
    validate_event(event)
    return event


def validate_event(event: dict[str, Any]) -> None:
    missing = [field for field in EVENT_FIELDS if field not in event]
    if missing:
        raise ExtractionError(f"event missing fields: {', '.join(missing)}")
    if not event["event_id"] or not event["source_artifact_sha256"] or len(event["source_artifact_sha256"]) != 64:
        raise ExtractionError("event must have a traceable source hash and event ID")
    if event["source_agent"] not in {"agent1", "agent2", "agent3", "agent4", "UNKNOWN"}:
        raise ExtractionError("unsupported source agent")
    if event["target_agent"] not in {"language_advisor", "domain_advisor", "UNKNOWN"}:
        raise ExtractionError("unsupported target agent")


def _load(path: pathlib.Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def _question_events(root: pathlib.Path) -> list[dict[str, Any]]:
    events: list[dict[str, Any]] = []
    for setting in SETTINGS:
        directory = root / "eval_output" / setting
        best_path = directory / "agentB_best_guidelines.json"
        if not best_path.is_file():
            continue
        document = _load(best_path)
        state = _load(directory / "eval_state.json") if (directory / "eval_state.json").is_file() else {}
        histories = list(state.get("lang_qa_history", [])) + list(state.get("dom_qa_history", []))
        source_path = _relative_path(best_path, root)
        source_hash = sha256_file(best_path)
        for scope, key, target in (
            ("language", "questions_to_language_advisor", "language_advisor"),
            ("domain", "questions_to_domain_advisor", "domain_advisor"),
        ):
            for index, question in enumerate(document.get(key, [])):
                q = {**question, "_index": index}
                answer = _answer_for(q.get("id"), histories)
                events.append(make_event(
                    source_path=source_path,
                    source_agent="agent2",
                    source_stage="phase2_guideline_build",
                    target_agent=target,
                    scope=scope,
                    question=q,
                    answer=answer,
                    source_hash=source_hash,
                ))

        for d_path in sorted(directory.glob("agentD_variability_classes*.json")):
            d_doc = _load(d_path)
            d_source_path = _relative_path(d_path, root)
            d_hash = sha256_file(d_path)
            for scope, key, target in (
                ("language", "questions_to_language_advisor", "language_advisor"),
                ("domain", "questions_to_domain_advisor", "domain_advisor"),
            ):
                for index, question in enumerate(d_doc.get(key, [])):
                    q = {**question, "_index": index}
                    events.append(make_event(
                        source_path=d_source_path,
                        source_agent="agent4",
                        source_stage="phase4_variability_classification",
                        target_agent=target,
                        scope=scope,
                        question=q,
                        answer=None,
                        source_hash=d_hash,
                    ))
    return events


def _normalized(text: str | None) -> str:
    return re.sub(r"\W+", " ", (text or "").casefold()).strip()


def _round_snapshot_summary(root: pathlib.Path) -> dict[str, Any]:
    records: list[tuple[str, str, str, str]] = []
    for setting in SETTINGS:
        for path in sorted((root / "eval_output" / setting).glob("agentB_run*_guidelines.json")):
            doc = _load(path)
            round_name = re.search(r"run(\d+)", path.name)
            for question in doc.get("questions_to_language_advisor", []) + doc.get("questions_to_domain_advisor", []):
                records.append((setting, round_name.group(1) if round_name else "UNKNOWN", str(question.get("id", "")), _normalized(question.get("question"))))
    repeated = Counter(row[3] for row in records if row[3])
    return {
        "round_snapshot_questions": len(records),
        "round_snapshot_unique_normalized_questions": len(set(row[3] for row in records if row[3])),
        "round_snapshot_repeated_normalized_questions": sum(count > 1 for count in repeated.values()),
        "round_snapshot_multiple_round_episodes": "NOT COMPUTABLE FROM FROZEN EVIDENCE",
    }


def _is_new_corpus_c1(value: float, threshold: float = 0.7) -> bool:
    """Return the preregistered strict C1 condition for the new corpus."""
    return value < threshold


def _mapping_certainty_count(root: pathlib.Path, threshold: float = 0.7) -> int:
    count = 0
    for path in sorted((root / "eval_output").glob("*/agentB_best_guidelines.json")):
        def walk(value: Any) -> None:
            nonlocal count
            if isinstance(value, dict):
                for key, child in value.items():
                    if key == "mapping_certainty" and isinstance(child, (int, float)) and _is_new_corpus_c1(child, threshold):
                        count += 1
                    walk(child)
            elif isinstance(value, list):
                for child in value:
                    walk(child)
        walk(_load(path))
    return count


def _agent4_confidence(root: pathlib.Path) -> Counter[str]:
    counter: Counter[str] = Counter()
    for path in sorted((root / "eval_output").glob("*/agentD_variability_classes*.json")):
        for row in _load(path).get("variability_classifications", []):
            value = row.get("confidence")
            if value in {"High", "Medium", "Low"}:
                counter[value] += 1
    return counter


def _apply_repeated_flags(events: list[dict[str, Any]]) -> None:
    counts = Counter(_normalized(event.get("question_text")) for event in events)
    for event in events:
        normalized = _normalized(event.get("question_text"))
        event["repeated_question"] = bool(normalized and counts[normalized] > 1)


def build_feature_inventory(root: pathlib.Path, events: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    _apply_repeated_flags(events)
    confidence = Counter(event.get("answer_confidence") for event in events if event.get("answer_confidence"))
    return {
        "F1_low_answer_confidence": {"available": False, "count": confidence["Low"], "deterministic": True, "rule": "answer_confidence == Low", "limitation": "answer confidence absent from frozen Q&A records"},
        "F2_low_or_medium_answer_confidence": {"available": False, "count": confidence["Low"] + confidence["Medium"], "deterministic": True, "rule": "answer_confidence in {Low, Medium}", "limitation": "answer confidence absent from frozen Q&A records"},
        "F3_answer_evidence_missing": {"available": False, "count": sum(event.get("answered") and event.get("evidence_present") is False for event in events), "deterministic": True, "rule": "answered and evidence_present == false", "limitation": "answers are not persisted"},
        "F4_lower_priority_source": {"available": False, "count": 0, "deterministic": True, "rule": "explicit source-priority field", "limitation": "no source-priority field"},
        "F5_answer_not_persisted": {"available": True, "count": sum(not event["answered"] for event in events), "deterministic": True, "rule": "answer_status == ANSWER_NOT_PERSISTED", "escalation_signal": False, "limitation": "data-availability condition only; not evidence of agent uncertainty or a human-escalation need"},
        "F6_multiple_rounds": {"available": False, "count": 0, "deterministic": True, "rule": "same episode has round_index > 1", "limitation": "episode linkage is not persisted"},
        "F7_repeated_question": {"available": True, "count": sum(event["repeated_question"] for event in events), "deterministic": True, "rule": "normalized question text repeats", "limitation": "canonical final snapshot has no repeats"},
        "F8_follow_up_clarification": {"available": False, "count": 0, "deterministic": True, "rule": "follow_up_observed == true", "limitation": "follow-up linkage is not persisted"},
        "F9_high_question_count": {"available": False, "count": 0, "deterministic": True, "rule": "declared per-case/claim count threshold", "limitation": "case/claim scope unavailable on Q&A rows"},
        "F10_max_round_or_unresolved": {"available": False, "count": 0, "deterministic": True, "rule": "MAX_QA_ROUNDS or unresolved episode", "limitation": "round termination is not persisted"},
        "F11_low_mapping_certainty": {"available": True, "count": _mapping_certainty_count(root), "deterministic": True, "rule": "new corpus Agent-2 mapping_certainty < 0.7", "supersedes_legacy_rule": "mapping_certainty <= 0.75", "limitation": "separate Agent-2 feature, not answer confidence; legacy scaffold is not C1"},
    }


def detect_event(event: dict[str, Any]) -> dict[str, Any]:
    validate_event(event)
    reasons: list[str] = []
    if event.get("answer_confidence") == "Low":
        reasons.append("F1_LOW_ANSWER_CONFIDENCE")
    if event.get("answer_confidence") in {"Low", "Medium"}:
        reasons.append("F2_LOW_OR_MEDIUM_ANSWER_CONFIDENCE")
    if event.get("answered") and event.get("evidence_present") is False:
        reasons.append("F3_MISSING_ANSWER_EVIDENCE")
    # Missing historical answers are a data-availability status, not a
    # behavioral escalation signal.  Keep the status visible without alerting.
    if event.get("repeated_question"):
        reasons.append("F7_REPEATED_NORMALIZED_QUESTION")
    if event.get("follow_up_observed"):
        reasons.append("F8_FOLLOW_UP_CLARIFICATION")
    if event.get("unresolved"):
        reasons.append("F10_UNRESOLVED")
    if event.get("mapping_certainty") is not None and _is_new_corpus_c1(event["mapping_certainty"]):
        reasons.append("F11_LOW_MAPPING_CERTAINTY")
    decision = "ALERT" if reasons else "NO_ALERT"
    return {
        "alert_id": "ALERT-" + event["event_id"].removeprefix("QA-"),
        "event_id": event["event_id"],
        "question_id": event.get("question_id"),
        "scope": event.get("scope"),
        "question_text": event.get("question_text"),
        "answer_text": event.get("answer_text"),
        "case_id": event.get("case_id"),
        "guideline_id": event.get("guideline_id"),
        "pattern_id": event.get("pattern_id"),
        "source_agent": event["source_agent"],
        "source_stage": event["source_stage"],
        "target_agent": event["target_agent"],
        "decision": decision,
        "reason_codes": reasons,
        "answer_confidence": event.get("answer_confidence"),
        "answer_status": event.get("answer_status", "UNKNOWN"),
        "evidence_present": event.get("evidence_present"),
        "explanation": "; ".join(reasons) if reasons else "No declared Q&A escalation rule fired.",
        "source_artifact_path": event["source_artifact_path"],
        "source_artifact_sha256": event["source_artifact_sha256"],
    }


def detect_detector_v1(episode: dict[str, Any]) -> dict[str, Any]:
    """Apply the preregistered strong/weak detector to a complete episode."""
    if not episode.get("scientific_complete"):
        return {"episode_id": episode["episode_id"], "classification": "EXCLUDED",
                "candidate_alert": False, "reason_codes": [],
                "exclusion_reason": episode.get("exclusion_reason")}
    answers = episode.get("answers", [])
    reasons: list[str] = []
    if any(row.get("answer_confidence") == "Low" for row in answers):
        reasons.append("S1_LOW_ANSWER_CONFIDENCE")
    if any((ref := row.get("answer_evidence_ref")) is None or ref.get("length", 0) == 0 for row in answers):
        reasons.append("S3_MISSING_ANSWER_EVIDENCE")
    if episode.get("termination_reason") == "TERMINATED_MAX_ROUNDS":
        reasons.append("S7_TERMINATED_MAX_ROUNDS")
    if reasons:
        classification = "STRONG_ALERT"
    else:
        if any(row.get("answer_confidence") == "Medium" for row in answers):
            reasons.append("S2_MEDIUM_ANSWER_CONFIDENCE")
        if episode.get("round_count", 0) > 1:
            reasons.append("S6_MULTIPLE_QA_ROUNDS")
        classification = "WEAK_ALERT" if reasons else "NO_ALERT"
    return {"episode_id": episode["episode_id"], "classification": classification,
            "candidate_alert": classification in {"STRONG_ALERT", "WEAK_ALERT"},
            "reason_codes": reasons, "exclusion_reason": None}


def extract_live_corpus(path: pathlib.Path) -> dict[str, Any]:
    """Project a versioned live communication stream into safe episode features."""
    if load_event_stream is None or build_episode_projection is None:
        raise ExtractionError("qa communication module is unavailable")
    try:
        events = load_event_stream(path)
        episodes = build_episode_projection(events)
    except Exception as exc:  # noqa: BLE001 - fail closed at the script boundary
        raise ExtractionError(f"invalid live communication stream: {exc}") from exc
    features: list[dict[str, Any]] = []
    for episode in episodes:
        features.append({
            "episode_id": episode["episode_id"],
            "run_id": episode["run_id"],
            "question_count": episode["question_count"],
            "answer_count": episode["answer_count"],
            "answer_confidence": [row.get("answer_confidence") for row in episode["answers"]],
            "evidence_present": [
                (ref := row.get("answer_evidence_ref")) is not None and ref.get("length", 0) > 0
                for row in episode["answers"]
            ],
            "round_count": episode["round_count"],
            "follow_up_present": episode["follow_up_present"],
            "converged": episode["converged"],
            "termination_reason": episode["termination_reason"],
            "scientific_complete": episode["scientific_complete"],
            "exclusion_reason": episode["exclusion_reason"],
            "source_target_pairs": episode["source_target_pairs"],
            "answers": episode["answers"],
        })
    detector_v1 = [detect_detector_v1(row) for row in features]
    return {
        "schema": "qa-live-communication-features-v1",
        "read_only": True,
        "network": "not_used",
        "baseline_modified": False,
        "events": events,
        "episodes": features,
        "detector_v1": detector_v1,
        "summary": {
            "events": len(events),
            "episodes": len(features),
            "questions": sum(row["question_count"] for row in features),
            "answers": sum(row["answer_count"] for row in features),
            "max_round_termination": sum(row["termination_reason"] == "TERMINATED_MAX_ROUNDS" for row in features),
            "excluded_unterminated": sum(row["exclusion_reason"] == "UNTERMINATED" for row in features),
            "excluded_incomplete_technical": sum(row["exclusion_reason"] == "INCOMPLETE_TECHNICAL" for row in features),
            "scientific_episode_count": sum(row["scientific_complete"] for row in features),
        },
        "claim_boundary": "live_communication_observability_only",
    }


def evaluate_alerts(alerts: list[dict[str, Any]], labels: list[dict[str, Any]], *, labels_cover_all_events: bool) -> dict[str, Any]:
    if not labels_cover_all_events:
        raise EvaluationError("recall/coverage cannot be computed from alert-only labels")
    by_id = {row.get("alert_id"): row for row in labels}
    confirmed = sum(by_id.get(alert["alert_id"], {}).get("review_label") == "HUMAN INTERVENTION REQUIRED" for alert in alerts)
    false_alerts = sum(by_id.get(alert["alert_id"], {}).get("review_label") == "HUMAN INTERVENTION NOT REQUIRED" for alert in alerts)
    unclear = sum(by_id.get(alert["alert_id"], {}).get("review_label") == "UNCLEAR" for alert in alerts)
    total = len(alerts)
    return {
        "alerts_total": total,
        "confirmed_alerts": confirmed,
        "false_alerts": false_alerts,
        "unclear_alerts": unclear,
        "alert_yield": confirmed / total if total else None,
        "false_alert_rate": false_alerts / total if total else None,
        "recall_status": "COMPUTABLE_ONLY_WITH_ALL_EVENT_LABELS",
    }


def write_blind_review_material(alerts: list[dict[str, Any]], output_dir: pathlib.Path) -> dict[str, pathlib.Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    rows = []
    audit = []
    for index, alert in enumerate(alerts, start=1):
        blind_id = f"BLIND-{index:04d}"
        rows.append({
            "blind_row_id": blind_id,
            "question_id": alert.get("question_id") or "",
            "scope": alert.get("scope") or "",
            "source_stage": alert.get("source_stage") or "",
            "target_agent": alert.get("target_agent") or "",
            "question_text": alert.get("question_text") or "",
            "answer_text": alert.get("answer_text") or "",
            "review_label": "",
            "short_rationale": "",
            "reviewer_id": "",
            "review_date": "",
            "reviewer_confidence": "",
            "event_context": "Review whether human intervention was warranted at this Q&A event.",
        })
        audit.append({"blind_row_id": blind_id, "alert_id": alert["alert_id"], "event_id": alert["event_id"]})
    paths: dict[str, pathlib.Path] = {}
    for reviewer in ("a", "b", "c"):
        path = output_dir / f"reviewer_{reviewer}.json"
        path.write_text(json.dumps(rows, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        paths[f"reviewer_{reviewer}"] = path
        csv_reviewer = output_dir / f"reviewer_{reviewer}.csv"
        with csv_reviewer.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(rows[0]) if rows else ["blind_row_id"])
            writer.writeheader()
            writer.writerows(rows)
        paths[f"reviewer_{reviewer}_csv"] = csv_reviewer
    audit_path = output_dir / "internal_audit_mapping.json"
    audit_path.write_text(json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    paths["internal_audit"] = audit_path
    csv_path = output_dir / "reviewer_sheets.csv"
    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]) if rows else ["blind_row_id"])
        writer.writeheader()
        writer.writerows(rows)
    paths["csv"] = csv_path
    return paths


def communication_matrix(summary: dict[str, Any]) -> list[dict[str, Any]]:
    observed = {("agent2", "language_advisor"): summary.get("by_source_target", {}).get("agent2→language_advisor", 0)}
    return [
        {"source_agent_stage": "Agent 2 / phase2, phase3, phase4 routing", "target_agent": "Agent 1", "question_field": "questions_to_language_advisor", "answer_field": "questions_answers", "confidence_field": "answer.confidence", "evidence_field": "answer.evidence", "persisted": "state.lang_qa_history", "frozen_rows": observed.get(("agent2", "language_advisor"), 0), "status": "OBSERVED" if observed.get(("agent2", "language_advisor"), 0) else "SUPPORTED BY CODE, NOT OBSERVED"},
        {"source_agent_stage": "Agent 2 / phase2, phase3, phase4 routing", "target_agent": "Agent 2", "question_field": "questions_to_domain_advisor", "answer_field": "questions_answers", "confidence_field": "answer.confidence", "evidence_field": "answer.evidence", "persisted": "state.dom_qa_history", "frozen_rows": 0, "status": "SUPPORTED BY CODE, NOT OBSERVED"},
        {"source_agent_stage": "Agent 3 / skill 3-2 and 3-3", "target_agent": "Agent 1", "question_field": "questions_to_language_advisor", "answer_field": "questions_answers", "confidence_field": "answer.confidence", "evidence_field": "answer.evidence", "persisted": "state.lang_qa_history", "frozen_rows": 0, "status": "SUPPORTED BY CODE, NOT OBSERVED"},
        {"source_agent_stage": "Agent 3 / skill 3-2 and 3-3", "target_agent": "Agent 2", "question_field": "questions_to_domain_advisor", "answer_field": "questions_answers", "confidence_field": "answer.confidence", "evidence_field": "answer.evidence", "persisted": "state.dom_qa_history", "frozen_rows": 0, "status": "SUPPORTED BY CODE, NOT OBSERVED"},
        {"source_agent_stage": "Agent 4 / skill 4-2", "target_agent": "Agent 1", "question_field": "questions_to_language_advisor", "answer_field": "questions_answers", "confidence_field": "answer.confidence", "evidence_field": "answer.evidence", "persisted": "state.lang_qa_history", "frozen_rows": 0, "status": "SUPPORTED BY CODE, NOT OBSERVED"},
        {"source_agent_stage": "Agent 4 / skill 4-2", "target_agent": "Agent 2", "question_field": "questions_to_domain_advisor", "answer_field": "questions_answers", "confidence_field": "answer.confidence", "evidence_field": "answer.evidence", "persisted": "state.dom_qa_history", "frozen_rows": 0, "status": "SUPPORTED BY CODE, NOT OBSERVED"},
    ]


def extract_frozen_corpus(root: pathlib.Path) -> dict[str, Any]:
    root = root.resolve()
    events = _question_events(root)
    _apply_repeated_flags(events)
    answers = sum(event["answered"] for event in events)
    by_source = Counter(event["source_agent"] for event in events)
    by_target = Counter(event["target_agent"] for event in events)
    by_source_target = Counter(f"{event['source_agent']}→{event['target_agent']}" for event in events)
    agent4_confidence = _agent4_confidence(root)
    summary = {
        "canonical_questions": len(events),
        "answers": answers,
        "unanswered_questions": len(events) - answers,
        "language_questions": sum(event["scope"] == "language" for event in events),
        "domain_questions": sum(event["scope"] == "domain" for event in events),
        "by_source_agent": dict(sorted(by_source.items())),
        "by_target_agent": dict(sorted(by_target.items())),
        "by_source_target": dict(sorted(by_source_target.items())),
        "high_confidence_answers": sum(event.get("answer_confidence") == "High" for event in events),
        "medium_confidence_answers": sum(event.get("answer_confidence") == "Medium" for event in events),
        "low_confidence_answers": sum(event.get("answer_confidence") == "Low" for event in events),
        "answers_without_evidence": sum(event["answered"] and event["evidence_present"] is False for event in events),
        "questions_with_multiple_rounds": "NOT COMPUTABLE FROM FROZEN EVIDENCE",
        "repeated_normalized_questions": sum(event["repeated_question"] for event in events),
        "cases_with_multiple_questions": "NOT COMPUTABLE FROM FROZEN EVIDENCE",
        "episodes_reaching_max_qa_rounds": "NOT COMPUTABLE FROM FROZEN EVIDENCE",
        "unresolved_episodes": "NOT COMPUTABLE FROM FROZEN EVIDENCE",
        "agent4_classification_confidence": dict(sorted(agent4_confidence.items())),
    }
    return {
        "schema": "qa-escalation-observability-v1",
        "read_only": True,
        "network": "not_used",
        "baseline_modified": False,
        "events": events,
        "summary": summary,
        "round_snapshots": _round_snapshot_summary(root),
        "features": build_feature_inventory(root, events),
        "communication_matrix": communication_matrix(summary),
        "claim_boundary": "observability_and_detector_scaffold_only",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--vego-root", type=pathlib.Path, default=pathlib.Path("VEGO-AI"))
    parser.add_argument("--output", type=pathlib.Path, default=None)
    parser.add_argument("--review-output", type=pathlib.Path, default=None)
    args = parser.parse_args()
    corpus = extract_frozen_corpus(args.vego_root)
    alerts = [detect_event(event) for event in corpus["events"]]
    corpus["alerts"] = alerts
    if args.review_output:
        corpus["review_material"] = {key: path.as_posix() for key, path in write_blind_review_material(alerts, args.review_output).items()}
    rendered = json.dumps(corpus, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
