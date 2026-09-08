"""Build the four-page bilingual VEGO-AI human-intervention baseline.

The report is generated only from small, tracked, privacy-safe evidence files.
It performs no provider/model call and reads no private run artifact.  The
source hashes are pinned so a changed evidence record fails closed instead of
silently changing a supervisor-facing number.
"""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import re
import subprocess
import tempfile
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
RUN_ID = "S2P-LIVE-20260908T192135Z"
SOURCE_HEAD = "cbfc7f8adab29e9a521247109b60cf815228687e"
RUN_DIR = (
    Path("docs")
    / "research"
    / "phd-proposal"
    / "study2-prospective"
    / "evidence"
    / RUN_ID
)
ANALYSIS_REL = RUN_DIR / "analysis.json"
VALIDATION_REL = RUN_DIR / "validation.json"
AGGREGATE_REL = RUN_DIR / "public-aggregate.json"
ARCHIVAL_REL = Path("docs/research/phd-proposal/2026-09-06-study1-airtravel-execution-and-analysis-receipt.md")
ENGINEERING_REL = Path("docs/research/phd-proposal/2026-09-08-study1-instrument-experiments-addendum.md")
SUPERVISOR_REL = Path("docs/research/phd-proposal/2026-09-03-qa-human-escalation-study-freeze.md")
RUBRIC_REL = Path("docs/research/phd-proposal/study2-prospective/human-rater-rubric.he.md")
CLAIMS_REL = Path("docs/research/phd-proposal/study2-prospective/claims-and-limitations-contract.md")
AGENT4_INDEX_REL = Path("docs/research/phd-proposal/2026-09-08-study1-e2e-evidence-index.md")

SOURCE_SHA256 = {
    ANALYSIS_REL.as_posix(): "9b4e3ebc5dd1469ae4ed02af2dd3dc381e0e39c8e3c08cf7ae57e969b026321d",
    VALIDATION_REL.as_posix(): "1a4f14f7c20f48031c71026fac3fdc50de25d9e456aa09caa994b1657459a9be",
    AGGREGATE_REL.as_posix(): "6e103688526d4de9d581bb7f059a37b53afb301f0ae807bcd310465a240a6183",
    ARCHIVAL_REL.as_posix(): "0eda4798820a3af6e06583d5d51137f292d9cc081d19c9e3f99d3b98eb92f1b0",
    ENGINEERING_REL.as_posix(): "9d2a7e070d64c1549495649c0100b344206279792e61e7ceefcb7f289f05cf7f",
    SUPERVISOR_REL.as_posix(): "14f7959b76150787ac5ffd17f7b75626de0ba130b1d3b203cd81137aef473f76",
    RUBRIC_REL.as_posix(): "781f7f996d5952e67900fa6d67887d75e07005b8baafbfc1356aa088e4c67815",
    CLAIMS_REL.as_posix(): "26f241981c4dc8f1f88b930e016f11b640cda8aaabc195dfc7f9015629cf5a60",
    AGENT4_INDEX_REL.as_posix(): "c212bacbe77b6f9003bc854d0a79e95032f612897a68343810240faf984576ef",
}

OUTPUT_STEM = "2026-09-09-vego-ai-human-intervention-baseline"
PDF_FIXED_TIMESTAMP = b"D:20260909000000+03'00'"


class EvidenceError(RuntimeError):
    """Raised when tracked evidence does not match the frozen report contract."""


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _read_bound(path: Path, expected_sha256: str) -> str:
    if not path.is_file():
        raise EvidenceError(f"Missing bound evidence file: {path.name}")
    actual = _sha256(path)
    if actual != expected_sha256:
        raise EvidenceError(
            f"SHA-256 mismatch for {path.name}: expected {expected_sha256}, got {actual}"
        )
    return path.read_text(encoding="utf-8")


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise EvidenceError(message)


def _ratio(numerator: float, denominator: float) -> float:
    _require(denominator > 0, "A report ratio has a zero denominator")
    return numerator / denominator


def _extract_int(pattern: str, text: str, label: str) -> int:
    match = re.search(pattern, text, flags=re.IGNORECASE | re.MULTILINE)
    if not match:
        raise EvidenceError(f"Could not extract {label} from its bound source")
    return int(match.group(1))


def load_evidence(root: Path = ROOT, *, analysis_path: Path | None = None) -> dict[str, Any]:
    """Validate the pinned sources and return one canonical fact dictionary."""

    root = root.resolve()
    paths = {
        "analysis": analysis_path or root / ANALYSIS_REL,
        "validation": root / VALIDATION_REL,
        "aggregate": root / AGGREGATE_REL,
        "archival": root / ARCHIVAL_REL,
        "engineering": root / ENGINEERING_REL,
        "supervisor": root / SUPERVISOR_REL,
        "rubric": root / RUBRIC_REL,
        "claims": root / CLAIMS_REL,
        "agent4_index": root / AGENT4_INDEX_REL,
    }
    expected = {
        "analysis": SOURCE_SHA256[ANALYSIS_REL.as_posix()],
        "validation": SOURCE_SHA256[VALIDATION_REL.as_posix()],
        "aggregate": SOURCE_SHA256[AGGREGATE_REL.as_posix()],
        "archival": SOURCE_SHA256[ARCHIVAL_REL.as_posix()],
        "engineering": SOURCE_SHA256[ENGINEERING_REL.as_posix()],
        "supervisor": SOURCE_SHA256[SUPERVISOR_REL.as_posix()],
        "rubric": SOURCE_SHA256[RUBRIC_REL.as_posix()],
        "claims": SOURCE_SHA256[CLAIMS_REL.as_posix()],
        "agent4_index": SOURCE_SHA256[AGENT4_INDEX_REL.as_posix()],
    }
    text = {name: _read_bound(path, expected[name]) for name, path in paths.items()}

    analysis = json.loads(text["analysis"])
    validation = json.loads(text["validation"])
    aggregate = json.loads(text["aggregate"])

    _require(analysis.get("run_id") == RUN_ID, "Unexpected prospective run identity")
    _require(aggregate.get("run_id") == RUN_ID, "Aggregate run identity does not match")
    _require(
        analysis.get("evidence_class") == "PROSPECTIVE EMPIRICAL EVIDENCE",
        "Unexpected prospective evidence class",
    )
    _require(validation.get("match") is True, "Published aggregate does not recompute")
    _require(validation.get("receipt_binding_valid") is True, "Receipt binding is invalid")
    _require(
        validation.get("published_sha256") == validation.get("recomputed_sha256"),
        "Published and recomputed aggregate hashes differ",
    )

    on = analysis["conditions"]["VEGO_AI_ON"]
    off = analysis["conditions"]["VEGO_AI_OFF"]
    episode = on["episode_summary"]
    detector = analysis["detector"]
    human = analysis["human"]
    agg_on = aggregate["conditions"]["VEGO_AI_ON"]
    agg_off = aggregate["conditions"]["VEGO_AI_OFF"]

    _require(on["status"] == "STOPPED_AT_CAP", "ON did not preserve STOPPED_AT_CAP")
    _require(off["status"] == "COMPLETED", "OFF is not complete")
    _require(on["planned"] == off["planned"] == len(analysis["case_ids"]), "Case denominator mismatch")
    _require(on["completed"] == agg_on["completed_cases"], "ON completion mismatch")
    _require(off["completed"] == agg_off["completed_cases"], "OFF completion mismatch")
    _require(on["requests"] + off["requests"] == analysis["accounting"]["ledger_requests"], "Ledger request mismatch")
    _require(analysis["accounting"]["receipt_requests"] - analysis["accounting"]["ledger_requests"] == 1, "Expected one cancelled no-usage request")
    _require(human["status"] == "NOT_MEASURED" and human["raters_scored"] == 0, "Human-label state changed")
    _require(detector["applies_to"]["VEGO_AI_OFF"] == "NOT_APPLICABLE", "OFF Detector status changed")

    agent4_labels = sum(
        int((row.get("label_counts") or {}).get("agent4", 0))
        for row in agg_on.get("cases", [])
    ) + int((agg_on.get("setting_level_label_counts") or {}).get("agent4", 0))
    _require(agent4_labels == 0, "Agent 4 unexpectedly appears in the accepted live run")

    case_21 = next(row for row in analysis["paired"] if row["case_id"] == "21")
    _require(case_21["on_status"] == "NOT_PRODUCED", "Case 21 status changed")
    _require(case_21["on_requests"] == 0, "Case 21 unexpectedly has ON requests")

    archival_cases = _extract_int(
        r"Mapping result[^\n]*?\|\s*\d+\s*\|\s*(\d+)\s+cases",
        text["archival"],
        "archival N",
    )
    _require("3/3 complete episodes" in text["engineering"], "Archival complete-episode marker is missing")
    _require("9/9 modes conform" in text["engineering"], "Engineering envelope marker is missing")
    _require("500/500 seeded permutations" in text["engineering"], "Robustness marker is missing")
    _require("3/3 named reorderings" in text["engineering"], "Named robustness marker is missing")
    _require("Provider calls:** 0" in text["engineering"], "Engineering provider-call boundary is missing")
    _require("Three independent reviewers" in text["supervisor"], "Supervisor validation design marker is missing")
    _require("שני מעריכים בלתי תלויים" in text["rubric"], "Current two-rater requirement is missing")
    for limitation in (
        "One public LLM-generated corpus",
        "provider default temperature; a second",
        "attributions under concurrency, not isolated",
        "setting-level ON cost is shared",
        "Three selected inputs are byte-identical to Study 1 inputs",
        "no Study 1\n  output is reused and no pooling with Study 1 is performed",
    ):
        _require(limitation in text["claims"], f"Frozen limitation is missing: {limitation}")
    _require(
        "AirTravel status: `EXECUTED_THEN_BLOCKED`; queue status: `NOT_AVAILABLE`"
        in text["agent4_index"],
        "Agent-4 archival status changed",
    )

    not_produced_rows = [
        row for row in agg_on.get("cases", []) if row.get("status") == "NOT_PRODUCED"
    ]
    not_produced_case_ids = [row["case_id"] for row in not_produced_rows]
    _require(not_produced_case_ids == ["18", "20", "21"], "Unexpected ON non-produced cases")
    _require(
        all(row.get("failure_code") == "STOPPED_AT_CAP" for row in not_produced_rows),
        "ON non-produced case is not bound to STOPPED_AT_CAP",
    )
    _require(on["setting_level_requests"] == 2, "Unexpected ON setting-level request count")
    _require(on["setting_level_cost_usd"] == 0.007457, "Unexpected ON setting-level cost")
    request_parameters = analysis["model"]["request_parameters"]
    _require(
        request_parameters["temperature"] == "PROVIDER_DEFAULT_NOT_SENT",
        "Unexpected temperature setting",
    )

    planned = int(on["planned"])
    on_cost = float(on["cost_usd"])
    off_cost = float(off["cost_usd"])
    on_time = float(on["elapsed_seconds"])
    off_time = float(off["elapsed_seconds"])
    on_cost_completed = float(on["cost_per_completed_artifact_usd"])
    off_cost_completed = float(off["cost_per_completed_artifact_usd"])
    on_time_completed = on_time / int(on["completed"])
    off_time_completed = off_time / int(off["completed"])
    classifications = episode["detector_v1_classifications"]
    reasons = episode["detector_v1_reason_codes"]
    routes = {f"{row['source_agent']}-{row['target_agent']}": row["question_count"] for row in on["routes"]["routes"]}

    return {
        "run_id": RUN_ID,
        "source_head": SOURCE_HEAD,
        "source_sha256": expected,
        "evidence_class": analysis["evidence_class"],
        "corpus": "Text2UML AirTravel (public external LLM-generated corpus)",
        "eligible_cases": 21,
        "planned_cases": planned,
        "case_ids": list(analysis["case_ids"]),
        "model": analysis["model"]["model"],
        "temperature": request_parameters["temperature"],
        "overlap_study1_inputs": 3,
        "on_completed": int(on["completed"]),
        "off_completed": int(off["completed"]),
        "on_status": on["status"],
        "off_status": "COMPLETED",
        "case_21_status": case_21["on_status"],
        "not_produced_case_ids": not_produced_case_ids,
        "on_schema_valid": int(on["completed"] - on["schema_invalid"]),
        "off_schema_valid": int(off["completed"] - off["schema_invalid"]),
        "on_summary_consistent": int(on["summary_consistent_count"]),
        "off_summary_consistent": int(off["summary_consistent_count"]),
        "on_requests": int(on["requests"]),
        "off_requests": int(off["requests"]),
        "receipt_requests": int(analysis["accounting"]["receipt_requests"]),
        "ledger_requests": int(analysis["accounting"]["ledger_requests"]),
        "cancelled_no_usage": int(analysis["accounting"]["unrecorded_in_flight_requests"]),
        "on_setting_level_requests": int(on["setting_level_requests"]),
        "on_setting_level_cost_usd": float(on["setting_level_cost_usd"]),
        "on_cost_usd": on_cost,
        "off_cost_usd": off_cost,
        "total_cost_usd": float(analysis["budget"]["actual_cost_usd"]),
        "on_cost_per_completed": on_cost_completed,
        "off_cost_per_completed": off_cost_completed,
        "cost_total_ratio": _ratio(on_cost, off_cost),
        "cost_per_completed_ratio": _ratio(on_cost_completed, off_cost_completed),
        "on_time_seconds": on_time,
        "off_time_seconds": off_time,
        "on_time_per_completed": on_time_completed,
        "off_time_per_completed": off_time_completed,
        "time_total_ratio": _ratio(on_time, off_time),
        "time_per_completed_ratio": _ratio(on_time_completed, off_time_completed),
        "qa_questions": int(episode["questions"]),
        "qa_answers": int(episode["answers"]),
        "episodes_total": int(episode["episodes"]),
        "episodes_complete": int(episode["scientific_complete"]),
        "episodes_converged": int(episode["termination_reasons"]["CONVERGED"]),
        "episodes_max_rounds": int(episode["termination_reasons"]["TERMINATED_MAX_ROUNDS"]),
        "episodes_excluded": int(episode["termination_reasons"]["INCOMPLETE_TECHNICAL"]),
        "alerts_strong": int(classifications["STRONG_ALERT"]),
        "alerts_weak": int(classifications["WEAK_ALERT"]),
        "alerts_no": int(classifications.get("NO_ALERT", 0)),
        "alerts_excluded": int(classifications["EXCLUDED"]),
        "candidate_alerts": int(detector["candidate_alerts"]),
        "signal_s1": int(reasons.get("S1_LOW_ANSWER_CONFIDENCE", 0)),
        "signal_s2": int(reasons.get("S2_MEDIUM_ANSWER_CONFIDENCE", 0)),
        "signal_s3": int(reasons.get("S3_MISSING_ANSWER_EVIDENCE", 0)),
        "signal_s6": int(reasons.get("S6_MULTIPLE_QA_ROUNDS", 0)),
        "signal_s7": int(reasons.get("S7_TERMINATED_MAX_ROUNDS", 0)),
        "route_agent3_agent1": int(routes["agent3-agent1"]),
        "route_agent3_agent2": int(routes["agent3-agent2"]),
        "agent4_labelled_requests": agent4_labels,
        "agent4_archival_status": "EXECUTED_THEN_BLOCKED",
        "agent4_archival_queue_status": "NOT_AVAILABLE",
        "human_status": "NOT_MEASURED",
        "human_raters_required": int(human["raters_required"]),
        "supervisor_reviewers_required": 3,
        "human_raters_scored": int(human["raters_scored"]),
        "archival_cases": archival_cases,
        "archival_complete_episodes": 3,
        "archival_strong_alerts": 3,
        "engineering_modes_conform": 9,
        "engineering_modes_total": 9,
        "engineering_seeded_permutations": 500,
        "engineering_named_reorderings": 3,
        "engineering_fixture_calls": 724,
        "engineering_provider_calls": 0,
    }


def _e(value: Any) -> str:
    return html.escape(str(value), quote=True)


def _n(value: float, digits: int = 1) -> str:
    return f"{value:,.{digits}f}"


def _units(count: int, total: int, css_class: str) -> str:
    cells = []
    for index in range(total):
        state = css_class if index < count else "unit-empty"
        cells.append(f'<span class="unit {state}" aria-hidden="true"></span>')
    return "".join(cells)


def _bar(label: str, value: str, width: float, css_class: str, *, note: str = "") -> str:
    return f"""
      <div class="bar-row">
        <div class="bar-label">{label}</div>
        <div class="bar-track"><span class="bar-fill {css_class}" style="width:{width:.2f}%"></span></div>
        <div class="bar-value">{value}</div>
        <div class="bar-note">{note}</div>
      </div>"""


def _source_url(relative: Path) -> str:
    return (
        "https://github.com/AliHamed17/vego-ai-research/blob/"
        f"{SOURCE_HEAD}/{relative.as_posix()}"
    )


def _translations(language: str) -> dict[str, str]:
    if language == "en":
        return {
            "dir": "ltr",
            "title": "When should VEGO-AI involve a human?",
            "subtitle": "A visual baseline from existing AirTravel evidence",
            "date": "Supervisor readout · 9 September 2026",
            "summary": "Executive Summary",
            "hero": "We can now see where an alert can be raised. We still cannot say whether the alert is correct.",
            "bullet1": "VEGO-AI ON adds agent coordination, an inspectable Q&A log, and Detector-v1 labels.",
            "bullet2": "OFF is a direct workflow. It finished all cases with less time and cost in this run.",
            "bullet3": "Human labels are still missing. Quality, accuracy, benefit, and workload reduction are not measured.",
            "scope": "WHAT WAS STUDIED",
            "scope1": "Public external LLM-generated AirTravel corpus",
            "scope2": "12 seeded cases from 21 eligible",
            "scope3": "gpt-5.6-luna · PROVIDER_DEFAULT_NOT_SENT · one day",
            "scope4": "Not student data · not representative",
            "scope5": "3 inputs overlap Study 1 · no outputs reused or pooled",
            "repeat_limit": "Provider-default stochastic run; a second run may differ.",
            "ladder": "Evidence ladder",
            "archival": "1 · Archival Study 1",
            "archival_body": "4 purposive cases · 3 complete episodes · 3/3 candidate labels",
            "engineering": "2 · Engineering checks",
            "engineering_body": "9/9 rule modes · 724 fixture calls · 0 provider calls",
            "prospective": "3 · Prospective comparison",
            "prospective_body": "12 matched AirTravel cases · ON versus OFF · ON STOPPED_AT_CAP",
            "human": "4 · Human validation",
            "human_body": "0 raters scored · alert correctness remains open",
            "flow_title": "What changes when VEGO-AI is ON?",
            "flow_subtitle": "Same input, two different workflow packages",
            "on": "VEGO-AI ON",
            "off": "VEGO-AI OFF",
            "input": "AirTravel case",
            "agents12": "Agents 1–2\nprepare language + domain guidance",
            "agent3": "Agent 3\ninspects the model",
            "qa": "Q&A event log\nwho asked whom, rounds, confidence, evidence",
            "detector": "Detector-v1\nclassifies each complete Q&A episode",
            "label": "Report label\ncandidate for human review",
            "agent4": "{count} Agent-4-labelled requests are present in the public aggregate before ON STOPPED_AT_CAP",
            "direct": "One direct model workflow",
            "output": "Structured output",
            "off_na": "No inter-agent Q&A · Detector-v1 = NOT_APPLICABLE",
            "changed": "VEGO-AI added",
            "changed1": "observable coordination",
            "changed2": "traceable Q&A episodes",
            "changed3": "automatic reporting labels",
            "not_changed": "It did not add",
            "not_changed1": "automatic correction",
            "not_changed2": "an Agent-4 queue in this capped run",
            "not_changed3": "proof of better quality",
            "logs": "Which logs mean what",
            "log1": "qa_events.jsonl · Detector source when validated",
            "log2": "interaction_log.json · possible model trace; not Detector evidence",
            "log3": "user_actions.log · GUI audit; not Q&A evidence",
            "log4": "Agent-4 output · separate variability mechanism",
            "baseline_title": "Operational baseline: ON versus OFF",
            "baseline_subtitle": "Descriptive measurements on 12 planned cases",
            "completion": "Completed outputs",
            "completion_on": "ON · 9 of 12",
            "completion_off": "OFF · 12 of 12",
            "cap_note": "ON = STOPPED_AT_CAP; cases 18, 20 and 21 = NOT_PRODUCED.",
            "cost": "Recorded cost",
            "total": "Total",
            "cost_quotient": "Completed-output quotient",
            "throughput_quotient": "Throughput quotient: condition seconds ÷ completed outputs",
            "time": "Elapsed time",
            "detector_result": "Detector-v1 under ON",
            "strong": "Strong",
            "weak": "Weak",
            "no_alert": "No alert",
            "excluded": "Excluded",
            "saturation": "14/14 complete episodes received a candidate label. This is alert saturation—not proof of correctness.",
            "consistency": "Output structure check",
            "consistency_body": "ON 9/9 completed summaries were internally consistent; OFF 7/12. The workflows construct outputs differently.",
            "not_quality": "NOT COMPARABLE AS QUALITY",
            "supervisor_title": "Where can a human enter—and what is still missing?",
            "supervisor_subtitle": "Direct answer to Iris and Arnon’s questions",
            "rule_title": "How the smart alert works",
            "rule_line1": "STRONG_ALERT = S1 OR S3 OR S7",
            "rule_line2": "WEAK_ALERT = no strong signal AND (S2 OR S6)",
            "rule_line3": "NO_ALERT otherwise",
            "alert_meaning": "Alert = a candidate for human review in the report",
            "signal_header": "Observed trigger signals · denominator: 14 complete ON episodes",
            "s1": "S1 · at least one Low self-reported answer confidence",
            "s2": "S2 · at least one Medium self-reported answer confidence",
            "s3": "S3 · missing or zero-length evidence reference",
            "s6": "S6 · more than one Q&A round",
            "s7": "S7 · episode stopped at the maximum round",
            "agent_header": "Observed agent coverage",
            "asking": "Asking agent",
            "answering": "Answering agent",
            "route1": "Agent 3 · Model Inspector",
            "route1a": "Agent 1 · Language Advisor",
            "route2a": "Agent 2 · Domain Advisor",
            "agent4_row": "Agent 4 · Variability Explorer",
            "not_reached": "Prospective aggregate: 0 Agent-4-labelled requests before ON STOPPED_AT_CAP",
            "agent4_archival": "Separate archival path",
            "human_plan": "Next human-validation gate",
            "human_step1": "1 · Reconcile before scoring: current pack = 2 raters; supervisor freeze = 3 (Ali, Iris, Arnon).",
            "human_step2": "2 · Adjudicate disagreements and record rationale + review time.",
            "human_step3": "3 · Add valid non-alert examples before estimating recall or false negatives.",
            "matrix": "Human-labelled outcome",
            "tp": "TP · alert + review needed",
            "fp": "FP · alert + review not needed",
            "fn": "FN · no alert + review needed",
            "tn": "TN · no alert + review not needed",
            "not_measured": "NOT_MEASURED",
            "engineering_note": "9/9 rule modes · 724 fixture calls · 0 provider calls. Instrument behavior only.",
            "robustness_note": "500/500 seeded permutations + 3/3 named reorderings · one accepted run · 0 provider calls.",
            "final": "Current result: an inspectable escalation baseline—not validated human-intervention detection.",
            "footer_note": "Four-page visual readout · no new experiment or provider call was made to create this report",
            "sources": "Sources",
            "hebrew_note": "",
            "source_label": "Source",
            "condition_label": "Condition",
            "denominator_label": "Denominator",
            "class_label": "Evidence class",
            "metric_label": "Metric",
            "limitation_label": "Limitation",
            "source_analysis": "analysis.json",
            "completion_condition": "ON + OFF",
            "completion_denominator": "12 planned cases per condition",
            "completion_metric": "completed output artifacts ÷ planned cases",
            "completion_limit": "ON stopped at cap; completion is not quality.",
            "cost_condition": "ON + OFF",
            "cost_denominator": "all recorded requests; quotient uses ON 9 / OFF 12 completed outputs",
            "cost_metric": "recorded USD; quotient = condition cost ÷ completed outputs",
            "cost_limit": "ON includes 2 shared setting-level requests and concurrency attributions; not isolated per-case cost or quality.",
            "time_condition": "ON + OFF",
            "time_denominator": "whole conditions; quotient uses ON 9 / OFF 12 completed outputs",
            "time_metric": "condition wall-clock; throughput quotient = seconds ÷ completed outputs",
            "time_limit": "Not mean per-case latency; ON ran concurrently, with one model on one day.",
            "detector_condition": "ON only",
            "detector_denominator": "16 recorded episodes = 14 complete + 2 excluded",
            "detector_metric": "frozen Detector-v1 class per Q&A episode",
            "detector_limit": "No human labels; not correctness, accuracy, or benefit.",
            "routes_condition": "ON only",
            "routes_denominator": "255 questions; 250 answers",
            "routes_metric": "question count by asking agent × answering agent",
            "routes_limit": "Observed routes only; not agent performance.",
        }
    if language != "he":
        raise ValueError(f"Unsupported language: {language}")
    return {
        "dir": "rtl",
        "title": "מתי VEGO-AI צריכה לערב אדם?",
        "subtitle": "קו בסיס חזותי מתוך ראיות AirTravel שכבר נאספו",
        "date": "מסמך למנחים · 9 בספטמבר 2026",
        "summary": "תקציר מנהלים",
        "hero": "כעת אפשר לראות היכן ניתן להפיק התראה. עדיין אי־אפשר לומר אם ההתראה נכונה.",
        "bullet1": "מצב ON מוסיף תיאום בין סוכנים, יומן Q&A שניתן לבדוק ותוויות Detector-v1.",
        "bullet2": "מצב OFF הוא מסלול ישיר. בריצה זו הוא השלים את כל המקרים בפחות זמן ועלות.",
        "bullet3": "עדיין אין תיוג אנושי. איכות, דיוק, תועלת והפחתת עומס לא נמדדו.",
        "scope": "מה נבדק",
        "scope1": "קורפוס AirTravel ציבורי וחיצוני, שנוצר בידי LLM",
        "scope2": "12 מקרים שנדגמו מתוך 21 כשירים",
        "scope3": "gpt-5.6-luna · PROVIDER_DEFAULT_NOT_SENT · יום אחד",
        "scope4": "לא נתוני סטודנטים · לא מדגם מייצג",
        "scope5": "3 קלטים חופפים למחקר 1 · לא נעשה שימוש חוזר או איגום של פלטים",
        "repeat_limit": "ריצה סטוכסטית בברירת המחדל של הספק; ריצה נוספת עשויה להיות שונה.",
        "ladder": "סולם הראיות",
        "archival": "1 · מחקר 1 ארכיוני",
        "archival_body": "4 מקרים מכוונים · 3 אפיזודות שלמות · 3/3 תוויות מועמדות",
        "engineering": "2 · בדיקות הנדסיות",
        "engineering_body": "9/9 מצבי כלל · 724 קריאות fixture · 0 קריאות ספק",
        "prospective": "3 · השוואה פרוספקטיבית",
        "prospective_body": "12 מקרי AirTravel תואמים · ON מול OFF · ON STOPPED_AT_CAP",
        "human": "4 · אימות אנושי",
        "human_body": "0 מדרגים השלימו תיוג · נכונות ההתראות עדיין פתוחה",
        "flow_title": "מה משתנה כאשר VEGO-AI פועלת?",
        "flow_subtitle": "אותו קלט, שתי חבילות תהליך שונות",
        "on": "VEGO-AI ON",
        "off": "VEGO-AI OFF",
        "input": "מקרה AirTravel",
        "agents12": "סוכנים 1–2\nמכינים הנחיות שפה ותחום",
        "agent3": "סוכן 3\nבודק את המודל",
        "qa": "יומן אירועי Q&A\nמי שאל את מי, סבבים, ביטחון וראיה",
        "detector": "Detector-v1\nמסווג כל אפיזודת Q&A שלמה",
        "label": "תווית בדוח\nמועמד לבדיקה אנושית",
        "agent4": "{count} בקשות מתויגות Agent-4 נמצאות במצרף הציבורי לפני ON STOPPED_AT_CAP",
        "direct": "מסלול מודל ישיר אחד",
        "output": "פלט מובנה",
        "off_na": "אין Q&A בין סוכנים · Detector-v1 = NOT_APPLICABLE",
        "changed": "VEGO-AI הוסיפה",
        "changed1": "תיאום שניתן לצפייה",
        "changed2": "אפיזודות Q&A שניתנות למעקב",
        "changed3": "תוויות דיווח אוטומטיות",
        "not_changed": "היא לא הוסיפה",
        "not_changed1": "תיקון אוטומטי",
        "not_changed2": "תור Agent-4 בריצה שנעצרה בתקרה",
        "not_changed3": "הוכחה לאיכות טובה יותר",
        "logs": "מה משמעות כל יומן",
        "log1": "qa_events.jsonl · מקור Detector כאשר הוא מאומת",
        "log2": "interaction_log.json · עקבת מודל אפשרית; לא ראיית Detector",
        "log3": "user_actions.log · יומן ממשק; לא ראיית Q&A",
        "log4": "פלט סוכן 4 · מנגנון שונות נפרד",
        "baseline_title": "קו בסיס תפעולי: ON מול OFF",
        "baseline_subtitle": "מדידות תיאוריות על 12 מקרים מתוכננים",
        "completion": "פלטים שהושלמו",
        "completion_on": "ON · 9 מתוך 12",
        "completion_off": "OFF · 12 מתוך 12",
        "cap_note": "ON = STOPPED_AT_CAP; המקרים 18, 20 ו־21 = NOT_PRODUCED.",
        "cost": "עלות מתועדת",
        "total": "סה״כ",
        "cost_quotient": "מנה לפי פלט שהושלם",
        "throughput_quotient": "מנת תפוקה: שניות התנאי ÷ מספר הפלטים שהושלמו",
        "time": "זמן שעבר",
        "detector_result": "Detector-v1 במצב ON",
        "strong": "חזקה",
        "weak": "חלשה",
        "no_alert": "ללא התראה",
        "excluded": "הוחרגו",
        "saturation": "14/14 האפיזודות השלמות קיבלו תווית מועמדת. זו רוויה בהתראות—לא הוכחה לנכונות.",
        "consistency": "בדיקת מבנה הפלט",
        "consistency_body": "ב־ON היו 9/9 סיכומים פנימיים עקביים; ב־OFF היו 7/12. התהליכים בונים פלטים בדרך שונה.",
        "not_quality": "NOT COMPARABLE AS QUALITY",
        "supervisor_title": "היכן האדם יכול להיכנס—ומה עדיין חסר?",
        "supervisor_subtitle": "מענה ישיר לשאלות של איריס וארנון",
        "rule_title": "כיצד ההתראה החכמה פועלת",
        "rule_line1": "STRONG_ALERT = S1 OR S3 OR S7",
        "rule_line2": "WEAK_ALERT = no strong signal AND (S2 OR S6)",
        "rule_line3": "NO_ALERT otherwise",
        "alert_meaning": "התראה = מועמד לבדיקה אנושית בדוח",
        "signal_header": "אותות שנצפו · מכנה: 14 אפיזודות ON שלמות",
        "s1": "S1 · לפחות תשובה אחת עם ביטחון עצמי מדווח Low",
        "s2": "S2 · לפחות תשובה אחת עם ביטחון עצמי מדווח Medium",
        "s3": "S3 · הפניית ראיה חסרה או באורך אפס",
        "s6": "S6 · יותר מסבב Q&A אחד",
        "s7": "S7 · האפיזודה נעצרה במספר הסבבים המרבי",
        "agent_header": "כיסוי הסוכנים שנצפה",
        "asking": "סוכן שואל",
        "answering": "סוכן משיב",
        "route1": "סוכן 3 · בודק המודל",
        "route1a": "סוכן 1 · יועץ השפה",
        "route2a": "סוכן 2 · יועץ התחום",
        "agent4_row": "סוכן 4 · חוקר השונות",
        "not_reached": "מצרף פרוספקטיבי: 0 בקשות מתויגות Agent-4 לפני ON STOPPED_AT_CAP",
        "agent4_archival": "מסלול ארכיוני נפרד",
        "human_plan": "שער האימות האנושי הבא",
        "human_step1": "1 · להכריע לפני הניקוד: חבילת הריצה דורשת 2 מעריכים; מסמך המנחים דורש 3 (עלי, איריס וארנון).",
        "human_step2": "2 · מחלוקות יוכרעו ויירשמו נימוק וזמן בדיקה.",
        "human_step3": "3 · יש להוסיף דוגמאות תקפות ללא התראה לפני חישוב Recall או החמצות.",
        "matrix": "תוצאת תיוג אנושית",
        "tp": "TP · התראה + נדרשה בדיקה",
        "fp": "FP · התראה + לא נדרשה בדיקה",
        "fn": "FN · אין התראה + נדרשה בדיקה",
        "tn": "TN · אין התראה + לא נדרשה בדיקה",
        "not_measured": "NOT_MEASURED",
        "engineering_note": "9/9 מצבי כלל · 724 קריאות fixture · 0 קריאות ספק. התנהגות מכשור בלבד.",
        "robustness_note": "500/500 פרמוטציות seeded + 3/3 סידורים שמיים · ריצה מאושרת אחת · 0 קריאות ספק.",
        "final": "התוצאה הנוכחית: קו בסיס שניתן לבדיקה—לא זיהוי מאומת של צורך בהתערבות אנושית.",
        "footer_note": "מסמך חזותי בן ארבעה עמודים · לא בוצעו ניסוי או קריאת ספק חדשים לצורך הכנתו",
        "sources": "מקורות",
        "hebrew_note": "טיוטה עברית בסיוע מכונה; בדיקת משמעות אנושית ממתינה.",
        "source_label": "מקור",
        "condition_label": "תנאי",
        "denominator_label": "מכנה",
        "class_label": "סוג ראיה",
        "metric_label": "מדד",
        "limitation_label": "מגבלה",
        "source_analysis": "analysis.json",
        "completion_condition": "ON + OFF",
        "completion_denominator": "12 מקרים מתוכננים בכל תנאי",
        "completion_metric": "פלטים שהושלמו ÷ מקרים מתוכננים",
        "completion_limit": "ON נעצר בתקרה; השלמה אינה איכות.",
        "cost_condition": "ON + OFF",
        "cost_denominator": "כל הבקשות המתועדות; המנה משתמשת ב־9 פלטי ON וב־12 פלטי OFF",
        "cost_metric": "USD מתועד; מנה = עלות התנאי ÷ פלטים שהושלמו",
        "cost_limit": "ON כולל 2 בקשות משותפות ברמת התנאי וייחוס תחת מקביליות; זו אינה עלות מבודדת למקרה או איכות.",
        "time_condition": "ON + OFF",
        "time_denominator": "התנאים השלמים; המנה משתמשת ב־9 פלטי ON וב־12 פלטי OFF",
        "time_metric": "זמן קיר לתנאי; מנת תפוקה = שניות ÷ פלטים שהושלמו",
        "time_limit": "לא זמן ממוצע למקרה; ON רץ במקביל, עם מודל אחד ביום אחד.",
        "detector_condition": "ON בלבד",
        "detector_denominator": "16 אפיזודות מתועדות = 14 שלמות + 2 מוחרגות",
        "detector_metric": "סיווג Detector-v1 קפוא לכל אפיזודת Q&A",
        "detector_limit": "אין תיוג אנושי; לא נכונות, דיוק או תועלת.",
        "routes_condition": "ON בלבד",
        "routes_denominator": "255 שאלות; 250 תשובות",
        "routes_metric": "מספר שאלות לפי סוכן שואל × סוכן משיב",
        "routes_limit": "מסלולים שנצפו בלבד; לא ביצועי סוכן.",
    }


CSS = r"""
@page { size: A4 landscape; margin: 0; }
* { box-sizing: border-box; }
html, body { margin: 0; padding: 0; background: #dfe7ef; color: #16324a; }
body { font-family: "Segoe UI", Arial, sans-serif; }
.page { width: 297mm; height: 210mm; padding: 10mm 13mm 11mm; background: #fbfdff;
  position: relative; overflow: hidden; page-break-inside: avoid; break-inside: avoid;
  page-break-after: always; break-after: page; }
.page:last-child { page-break-after: auto; break-after: auto; }
.page::before { content: ""; position: absolute; inset: 0 0 auto 0; height: 3.5mm;
  background: linear-gradient(90deg,#145da0,#19a7a3 58%,#ff9f43); }
.top { display:flex; align-items:center; justify-content:space-between; margin-top:1.5mm; }
.brand { font-weight:800; font-size:9pt; letter-spacing:.08em; color:#145da0; }
.date { font-size:7.2pt; color:#6a7f91; }
h1 { margin: 3mm 0 1.2mm; font-size: 25pt; line-height: 1.08; color:#0c365a; }
h2 { margin:0; font-size:17.5pt; line-height:1.15; color:#0c365a; }
h3 { margin:0; font-size:10.7pt; line-height:1.2; color:#183b56; }
p { margin:0; line-height:1.32; }
.subtitle { color:#60788c; font-size:10.2pt; }
.pill { display:inline-flex; align-items:center; gap:1.5mm; border-radius:999px; padding:1.2mm 3mm;
  font-size:6.9pt; font-weight:750; background:#eaf3fb; color:#145da0; white-space:nowrap; }
.pill.orange { background:#fff1df; color:#b15400; }
.pill.gray { background:#edf1f4; color:#52687a; }
.pill.green { background:#e4f7ee; color:#147651; }
.tag { display:inline-block; font-size:6.3pt; font-weight:800; letter-spacing:.035em;
  border-radius:2.2mm; padding:1mm 2.1mm; direction:ltr; unicode-bidi:isolate; }
.tag.archival { background:#efeafd; color:#6741b9; }
.tag.engineering { background:#fff0df; color:#b15400; }
.tag.prospective { background:#e7f3ff; color:#145da0; }
.tag.unmeasured { background:#edf1f4; color:#52687a; }
.hero-grid { display:grid; grid-template-columns: 1.2fr .8fr; gap:7mm; margin-top:5mm; }
[dir="rtl"] .hero-grid { grid-template-columns:.8fr 1.2fr; }
.hero { background:linear-gradient(135deg,#0c365a,#145da0); color:white; border-radius:5mm;
  padding:6mm 7mm; min-height:47mm; display:flex; flex-direction:column; justify-content:center;
  box-shadow:0 3mm 8mm rgba(24,59,86,.12); }
.hero .eyebrow { font-size:7.2pt; font-weight:800; letter-spacing:.08em; color:#9ee5e1; }
.hero .statement { font-size:17pt; font-weight:800; line-height:1.18; margin-top:2.5mm; max-width:165mm; }
.summary { background:white; border:1px solid #d7e3ec; border-radius:5mm; padding:5mm 6mm; min-height:47mm; }
.summary h3 { color:#145da0; margin-bottom:2mm; }
.summary ul { margin:0; padding-inline-start:5mm; font-size:8.1pt; line-height:1.38; }
.summary li { margin:1.4mm 0; }
.scope-row { display:flex; flex-wrap:wrap; gap:2mm; margin:4mm 0 3mm; }
.scope-limit { font-size:6.2pt; color:#6a7f91; margin:-1mm 0 2.5mm; }
.section-label { font-size:7.2pt; font-weight:850; letter-spacing:.09em; color:#627d92; margin-bottom:2mm; }
.ladder { display:grid; grid-template-columns:repeat(4,1fr); gap:3mm; }
.ladder-card { min-height:40mm; border-radius:4mm; padding:4mm; background:white; border:1px solid #d9e4ec;
  position:relative; overflow:hidden; }
.ladder-card::after { content:""; position:absolute; inset:auto 0 0; height:2.2mm; background:#d9e4ec; }
.ladder-card.archival::after { background:#8167c9; }
.ladder-card.engineering::after { background:#f2994a; }
.ladder-card.prospective::after { background:#2385c7; }
.ladder-card.human::after { background:#9aa9b6; }
.ladder-num { display:none; }
.ladder-card .tag { font-size:5.6pt; line-height:1.12; max-width:55mm; white-space:normal; }
.fixture-marker { margin-top:1.2mm; font-size:5.1pt; font-weight:800; color:#a95508;
  direction:ltr; unicode-bidi:isolate; }
.ladder-card h3 { margin-top:6mm; max-width:46mm; }
.ladder-card p { margin-top:2.2mm; font-size:7.8pt; color:#526b7c; max-width:55mm; }
.legend { display:flex; gap:2mm; align-items:center; margin-top:3mm; }
.flow-lane { border-radius:4mm; border:1px solid #d9e4ec; background:white; padding:3.5mm 4mm; margin-top:3.2mm; }
.flow-lane.on { border-inline-start:3mm solid #2385c7; }
.flow-lane.off { border-inline-start:3mm solid #f2994a; }
.lane-head { display:flex; align-items:center; justify-content:space-between; margin-bottom:2.3mm; }
.lane-status { font-size:6.5pt; color:#526b7c; }
.flow { display:flex; align-items:stretch; justify-content:space-between; gap:2mm; direction:ltr; }
.node { flex:1; min-height:27mm; padding:3mm 2.2mm; border-radius:3mm; background:#f4f8fb;
  border:1px solid #d7e3ec; text-align:center; display:flex; flex-direction:column; justify-content:center;
  font-size:7.3pt; line-height:1.25; color:#23465f; white-space:pre-line; }
.node.focus { background:#e8f4ff; border-color:#6fb3df; }
.node.detector { background:#fff3e5; border-color:#f0b36b; }
.node.result { background:#e6f7ef; border-color:#6dc49a; }
.arrow { flex:0 0 7mm; align-self:center; height:1.5px; background:#7f98aa; position:relative; }
.arrow::after { content:""; position:absolute; right:-.2mm; top:-1.3mm; border-left:2.5mm solid #7f98aa;
  border-top:1.4mm solid transparent; border-bottom:1.4mm solid transparent; }
.agent4-stop { margin-top:2mm; border:1px dashed #d06a4b; border-radius:3mm; padding:2mm 3mm;
  color:#a74325; font-size:7pt; background:#fff6f1; text-align:center; }
.compare-strip { display:grid; grid-template-columns:1fr 1fr 1.05fr; gap:3mm; margin-top:3mm; }
.mini-panel { border:1px solid #d9e4ec; background:#fff; border-radius:3.5mm; padding:3.2mm 4mm; }
.mini-panel h3 { margin-bottom:1.5mm; }
.ticks { display:grid; grid-template-columns:1fr; gap:1mm; font-size:7.2pt; color:#526b7c; }
.tick::before { content:"✓"; color:#16835f; font-weight:850; margin-inline-end:1.5mm; }
.cross::before { content:"×"; color:#c85635; }
.logs { display:grid; grid-template-columns:1fr 1fr; gap:1.5mm 3mm; font-size:6.6pt; color:#526b7c; }
.log { border-top:1px solid #e3eaf0; padding-top:1mm; }
.baseline-grid { display:grid; grid-template-columns:.86fr 1.14fr 1.14fr; gap:3mm; margin-top:3mm; }
.panel { background:white; border:1px solid #d9e4ec; border-radius:4mm; padding:3.4mm; }
.panel h3 { margin-bottom:2.5mm; }
.units { display:grid; grid-template-columns:repeat(6,1fr); gap:1.7mm; width:49mm; margin:2mm 0 1.5mm; }
.unit { width:6mm; height:6mm; border-radius:1.7mm; display:block; }
.unit-on { background:#2385c7; } .unit-off { background:#f2994a; } .unit-empty { background:#dde5eb; }
.unit-label { display:flex; justify-content:space-between; font-size:7.4pt; margin-top:2mm; color:#405b6e; }
.bar-row { display:grid; grid-template-columns:24mm 1fr 24mm; gap:2mm; align-items:center; margin:2mm 0; }
.bar-label { font-size:7.2pt; color:#405b6e; }
.bar-track { height:5.2mm; background:#edf2f6; border-radius:99px; overflow:hidden; }
.bar-fill { display:block; height:100%; border-radius:99px; }
.bar-fill.on { background:#2385c7; } .bar-fill.off { background:#f2994a; }
.bar-value { font-size:7.4pt; font-weight:800; direction:ltr; unicode-bidi:isolate; }
.bar-note { display:none; }
.ratio { display:inline-block; border-radius:2mm; background:#eef4f8; color:#34536a; padding:1mm 2mm;
  font-size:6.6pt; font-weight:800; }
.chart-caption { margin-top:2mm; padding-top:1.4mm; border-top:1px solid #e2e9ef;
  font-size:5.55pt; line-height:1.23; color:#60788c; }
.chart-caption span { display:block; }
.chart-caption b { color:#3e5b70; font-weight:800; }
.detector-panel { margin-top:3mm; display:grid; grid-template-columns:1.55fr .9fr .9fr; gap:3mm; }
.detector-bar { display:flex; height:13mm; overflow:hidden; border-radius:2.5mm; margin:2.5mm 0; direction:ltr; }
.seg-strong { background:#db5a42; } .seg-weak { background:#f2a83b; } .seg-no { background:#53a983; }
.seg-excluded { background:#a9b7c2; }
.detector-legend { display:flex; gap:3mm; flex-wrap:wrap; font-size:6.8pt; color:#526b7c; }
.swatch { display:inline-block; width:2.5mm; height:2.5mm; border-radius:.8mm; margin-inline-end:1mm; }
.insight { background:#fff4e7; border:1px solid #f2b56e; border-radius:4mm; padding:4mm;
  font-size:9.2pt; font-weight:750; color:#8d4a08; display:flex; align-items:center; }
.struct-note { background:#f2f6f9; border:1px solid #d5e0e8; border-radius:4mm; padding:4mm; font-size:7.3pt; }
.struct-note h3 { margin-bottom:1.7mm; }
.super-grid { display:grid; grid-template-columns:1.15fr .85fr; gap:4mm; margin-top:3.5mm; }
.rule-box { background:#0f3b5e; color:white; border-radius:4mm; padding:4mm 5mm; }
.rule-box h3 { color:white; margin-bottom:2mm; }
.rule { direction:ltr; unicode-bidi:isolate; font-family:Consolas,"Courier New",monospace; font-size:7.2pt;
  padding:1.3mm 2mm; margin:1mm 0; background:rgba(255,255,255,.10); border-radius:2mm; }
.meaning { margin-top:2mm; color:#9ee5e1; font-size:8.3pt; font-weight:850; }
.signals { display:grid; grid-template-columns:1fr 1fr; gap:1.5mm 2mm; margin-top:2.5mm; }
.signal { display:flex; justify-content:space-between; gap:2mm; align-items:center; border:1px solid #dbe6ee;
  border-radius:2.5mm; padding:2mm 2.5mm; background:white; font-size:6.65pt; }
.signal .count { flex:0 0 auto; direction:ltr; unicode-bidi:isolate; font-size:9pt; font-weight:850; color:#145da0; }
.agent-table { display:grid; grid-template-columns:1.15fr 1.15fr .55fr; font-size:6.8pt; border:1px solid #d9e4ec;
  border-radius:3mm; overflow:hidden; }
.agent-table > div { padding:2.1mm; border-bottom:1px solid #e2e9ef; }
.agent-table > div:nth-last-child(-n+3) { border-bottom:0; }
.agent-table .head { background:#eaf3fb; font-weight:800; color:#145da0; }
.agent-table .count { text-align:center; direction:ltr; unicode-bidi:isolate; font-weight:800; }
.agent4 { margin-top:2mm; background:#fff6f1; border:1px dashed #d06a4b; border-radius:2.5mm; padding:2.2mm;
  font-size:7pt; color:#9d4326; }
.human-grid { display:grid; grid-template-columns:1.18fr .82fr; gap:4mm; margin-top:4mm; }
.steps { display:grid; gap:1.5mm; }
.step { background:white; border:1px solid #d9e4ec; border-radius:2.5mm; padding:2.5mm 3mm; font-size:7.2pt; }
.matrix { display:grid; grid-template-columns:1fr 1fr; gap:1.5mm; }
.matrix-cell { min-height:16mm; border-radius:2.5mm; border:1px solid #d9e4ec; padding:2mm; background:#f7fafc;
  font-size:6.6pt; display:flex; flex-direction:column; justify-content:space-between; }
.matrix-cell strong { font-size:6.4pt; color:#647b8d; direction:ltr; unicode-bidi:isolate; }
.engineering-strip { display:flex; gap:2mm; align-items:center; margin-top:3mm; padding:2.5mm 3mm;
  border-radius:3mm; background:#fff4e7; color:#8a4b0d; font-size:6.9pt; }
.evidence-strips { display:grid; grid-template-columns:1fr 1fr; gap:3mm; margin-top:2.5mm; }
.evidence-strips .engineering-strip { margin-top:0; padding:2mm 2.5mm; font-size:6.2pt; }
.engineering-strip.robustness { background:#eef4fb; color:#345f7c; }
.engineering-strip.robustness .tag { flex:0 0 49mm; max-width:49mm; font-size:5.35pt;
  line-height:1.08; white-space:normal; overflow-wrap:anywhere; }
.final { margin-top:3mm; border-radius:3mm; padding:3mm 4mm; background:#e5f5f3; color:#0f6865;
  font-size:9pt; font-weight:850; text-align:center; }
.footer { position:absolute; inset-inline:13mm; bottom:4mm; display:flex; align-items:flex-end; justify-content:space-between;
  gap:5mm; border-top:1px solid #dbe4eb; padding-top:1.5mm; color:#718697; font-size:5.7pt; }
.footer a { color:#4d748e; text-decoration:none; }
.sources { white-space:nowrap; }
.page-no { font-weight:800; color:#145da0; white-space:nowrap; direction:ltr; unicode-bidi:isolate; }
.he-note { font-size:5.3pt; color:#8797a4; }
bdi, code { direction:ltr; unicode-bidi:isolate; }
"""


def _footer(t: dict[str, str], page: int) -> str:
    links = [
        ("PR #45", "https://github.com/AliHamed17/vego-ai-research/pull/45"),
        ("prospective", _source_url(ANALYSIS_REL)),
        ("limits", _source_url(CLAIMS_REL)),
        ("archival", _source_url(ARCHIVAL_REL)),
        ("engineering", _source_url(ENGINEERING_REL)),
        ("Agent-4", _source_url(AGENT4_INDEX_REL)),
        ("supervisor", _source_url(SUPERVISOR_REL)),
    ]
    anchors = " · ".join(f'<a href="{_e(url)}">{_e(label)}</a>' for label, url in links)
    note = f'<span class="he-note">{_e(t["hebrew_note"])}</span>' if t["hebrew_note"] else ""
    return f"""
      <footer class="footer">
        <span>{_e(t['footer_note'])} {note}</span>
        <span class="sources">{_e(t['sources'])}: {anchors}</span>
        <span class="page-no">{page} / 4</span>
      </footer>"""


def _chart_caption(
    t: dict[str, str],
    *,
    condition: str,
    denominator: str,
    metric: str,
    limitation: str,
) -> str:
    """Render the full evidence contract where it remains visible in the PDF."""

    return f"""
      <figcaption class="chart-caption">
        <span><b>{_e(t['source_label'])}:</b> {_e(t['source_analysis'])} · <b>{_e(t['condition_label'])}:</b> {_e(condition)}</span>
        <span><b>{_e(t['denominator_label'])}:</b> {_e(denominator)}</span>
        <span><b>{_e(t['class_label'])}:</b> PROSPECTIVE EMPIRICAL EVIDENCE</span>
        <span><b>{_e(t['metric_label'])}:</b> {_e(metric)}</span>
        <span><b>{_e(t['limitation_label'])}:</b> {_e(limitation)}</span>
      </figcaption>"""


def _header(t: dict[str, str], title_key: str, subtitle_key: str) -> str:
    return f"""
      <div class="top"><div class="brand">VEGO-AI · HUMAN-IN-THE-LOOP</div><div class="date">{_e(t['date'])}</div></div>
      <h2>{_e(t[title_key])}</h2>
      <p class="subtitle">{_e(t[subtitle_key])}</p>"""


def _page_one(t: dict[str, str], f: dict[str, Any]) -> str:
    return f"""
    <section class="page page-1" aria-label="page 1">
      <div class="top"><div class="brand">VEGO-AI · HUMAN-IN-THE-LOOP</div><div class="date">{_e(t['date'])}</div></div>
      <h1>{_e(t['title'])}</h1>
      <p class="subtitle">{_e(t['subtitle'])}</p>
      <div class="hero-grid">
        <div class="hero" data-fact-id="scope-airtravel">
          <div class="eyebrow">{_e(t['scope'])}</div>
          <div class="statement">{_e(t['hero'])}</div>
        </div>
        <div class="summary">
          <h3>{_e(t['summary'])}</h3>
          <ul><li>{_e(t['bullet1'])}</li><li>{_e(t['bullet2'])}</li><li>{_e(t['bullet3'])}</li></ul>
        </div>
      </div>
      <div class="scope-row">
        <span class="pill">{_e(t['scope1'])}</span>
        <span class="pill">{_e(t['scope2'])}</span>
        <span class="pill">{_e(t['scope3'])}</span>
        <span class="pill gray">{_e(t['scope4'])}</span>
        <span class="pill gray">{_e(t['scope5'])}</span>
      </div>
      <div class="scope-limit">{_e(t['repeat_limit'])}</div>
      <div class="section-label">{_e(t['ladder'])}</div>
      <div class="ladder">
        <div class="ladder-card archival" data-fact-id="ladder-archival">
          <div class="ladder-num">01</div><span class="tag archival">ARCHIVAL-RETROSPECTIVE DESCRIPTIVE EVIDENCE</span>
          <h3>{_e(t['archival'])}</h3><p>{_e(t['archival_body'])}</p>
        </div>
        <div class="ladder-card engineering" data-fact-id="ladder-engineering">
          <div class="ladder-num">02</div><span class="tag engineering">ENGINEERING-ONLY FIXTURE</span>
          <div class="fixture-marker">ENGINEERING_FIXTURE_NOT_SCIENTIFIC</div>
          <h3>{_e(t['engineering'])}</h3><p>{_e(t['engineering_body'])}</p>
        </div>
        <div class="ladder-card prospective" data-fact-id="ladder-prospective">
          <div class="ladder-num">03</div><span class="tag prospective">PROSPECTIVE EMPIRICAL EVIDENCE</span>
          <h3>{_e(t['prospective'])}</h3><p>{_e(t['prospective_body'])}</p>
        </div>
        <div class="ladder-card human" data-fact-id="ladder-human">
          <div class="ladder-num">04</div><span class="tag unmeasured">NOT_MEASURED</span>
          <h3>{_e(t['human'])}</h3><p>{_e(t['human_body'])}</p>
        </div>
      </div>
      <div class="legend"><span class="pill green"><bdi>Run {f['run_id']}</bdi></span><span class="pill orange"><bdi>ON = {f['on_status']}</bdi></span><span class="pill gray"><bdi>N = {f['planned_cases']} planned cases</bdi></span></div>
      {_footer(t, 1)}
    </section>"""


def _flow_nodes(nodes: list[tuple[str, str]]) -> str:
    parts: list[str] = []
    for index, (label, css_class) in enumerate(nodes):
        if index:
            parts.append('<span class="arrow" aria-hidden="true"></span>')
        parts.append(f'<div class="node {css_class}">{_e(label)}</div>')
    return "".join(parts)


def _page_two(t: dict[str, str], f: dict[str, Any]) -> str:
    on_nodes = [(t["input"], ""), (t["agents12"], "focus"), (t["agent3"], "focus"), (t["qa"], "focus"), (t["detector"], "detector"), (t["label"], "result")]
    off_nodes = [(t["input"], ""), (t["direct"], ""), (t["output"], "result")]
    return f"""
    <section class="page page-2" aria-label="page 2">
      {_header(t, 'flow_title', 'flow_subtitle')}
      <div class="flow-lane on">
        <div class="lane-head"><h3>{_e(t['on'])}</h3><span class="tag prospective">PROSPECTIVE EMPIRICAL EVIDENCE · N=12</span></div>
        <div class="flow">{_flow_nodes(on_nodes)}</div>
        <div class="agent4-stop" data-fact-id="agent4-status"><bdi>Agent 4</bdi> — {_e(t['agent4'].format(count=f['agent4_labelled_requests']))}</div>
      </div>
      <div class="flow-lane off">
        <div class="lane-head"><h3>{_e(t['off'])}</h3><span class="tag prospective">BASELINE · N=12</span></div>
        <div class="flow">{_flow_nodes(off_nodes)}<div class="node detector">{_e(t['off_na'])}</div></div>
      </div>
      <div class="compare-strip">
        <div class="mini-panel"><h3>{_e(t['changed'])}</h3><div class="ticks"><span class="tick">{_e(t['changed1'])}</span><span class="tick">{_e(t['changed2'])}</span><span class="tick">{_e(t['changed3'])}</span></div></div>
        <div class="mini-panel"><h3>{_e(t['not_changed'])}</h3><div class="ticks"><span class="tick cross">{_e(t['not_changed1'])}</span><span class="tick cross">{_e(t['not_changed2'])}</span><span class="tick cross">{_e(t['not_changed3'])}</span></div></div>
        <div class="mini-panel"><h3>{_e(t['logs'])}</h3><div class="logs"><div class="log">{_e(t['log1'])}</div><div class="log">{_e(t['log2'])}</div><div class="log">{_e(t['log3'])}</div><div class="log">{_e(t['log4'])}</div></div></div>
      </div>
      {_footer(t, 2)}
    </section>"""


def _page_three(t: dict[str, str], f: dict[str, Any]) -> str:
    cost_max = max(f["on_cost_usd"], f["off_cost_usd"])
    cost_output_max = max(f["on_cost_per_completed"], f["off_cost_per_completed"])
    time_max = max(f["on_time_seconds"], f["off_time_seconds"])
    time_output_max = max(f["on_time_per_completed"], f["off_time_per_completed"])
    total = f["episodes_total"]
    detector_bar = (
        f'<span class="seg-strong" style="width:{100*f["alerts_strong"]/total:.2f}%"></span>'
        f'<span class="seg-weak" style="width:{100*f["alerts_weak"]/total:.2f}%"></span>'
        f'<span class="seg-no" style="width:{100*f["alerts_no"]/total:.2f}%"></span>'
        f'<span class="seg-excluded" style="width:{100*f["alerts_excluded"]/total:.2f}%"></span>'
    )
    return f"""
    <section class="page page-3" aria-label="page 3">
      {_header(t, 'baseline_title', 'baseline_subtitle')}
      <div class="baseline-grid">
        <figure class="panel" id="chart-completion" data-denominator="12 planned cases per condition" data-evidence-status="PROSPECTIVE EMPIRICAL EVIDENCE">
          <h3>{_e(t['completion'])}</h3>
          <div class="unit-label" data-fact-id="completion-on"><strong>{_e(t['completion_on'])}</strong><bdi>75%</bdi></div><div class="units">{_units(f['on_completed'], f['planned_cases'], 'unit-on')}</div>
          <div class="unit-label" data-fact-id="completion-off"><strong>{_e(t['completion_off'])}</strong><bdi>100%</bdi></div><div class="units">{_units(f['off_completed'], f['planned_cases'], 'unit-off')}</div>
          <p style="font-size:6.8pt;color:#6b7f8e;margin-top:2mm"><bdi>{_e(t['cap_note'])}</bdi></p>
          {_chart_caption(t, condition=t['completion_condition'], denominator=t['completion_denominator'], metric=t['completion_metric'], limitation=t['completion_limit'])}
        </figure>
        <figure class="panel" id="chart-cost" data-denominator="12 planned; ON 9 and OFF 12 completed" data-evidence-status="PROSPECTIVE EMPIRICAL EVIDENCE">
          <h3>{_e(t['cost'])}</h3>
          <div data-fact-id="cost-total"><span class="ratio">{f['cost_total_ratio']:.1f}× ON / OFF · {_e(t['total'])}</span>
          {_bar('ON', f'USD {f["on_cost_usd"]:.4f}', 100*f['on_cost_usd']/cost_max, 'on')}
          {_bar('OFF', f'USD {f["off_cost_usd"]:.4f}', 100*f['off_cost_usd']/cost_max, 'off')}</div>
          <div data-fact-id="cost-per-output"><span class="ratio">{f['cost_per_completed_ratio']:.1f}× ON / OFF · {_e(t['cost_quotient'])}</span>
          {_bar('ON', f'USD {f["on_cost_per_completed"]:.4f}', 100*f['on_cost_per_completed']/cost_output_max, 'on')}
          {_bar('OFF', f'USD {f["off_cost_per_completed"]:.4f}', 100*f['off_cost_per_completed']/cost_output_max, 'off')}</div>
          {_chart_caption(t, condition=t['cost_condition'], denominator=t['cost_denominator'], metric=t['cost_metric'], limitation=t['cost_limit'])}
        </figure>
        <figure class="panel" id="chart-time" data-denominator="12 planned; ON 9 and OFF 12 completed" data-evidence-status="PROSPECTIVE EMPIRICAL EVIDENCE">
          <h3>{_e(t['time'])}</h3>
          <div data-fact-id="time-total"><span class="ratio">{f['time_total_ratio']:.2f}× ON / OFF · {_e(t['total'])}</span>
          {_bar('ON', f'{_n(f["on_time_seconds"],1)} s', 100*f['on_time_seconds']/time_max, 'on')}
          {_bar('OFF', f'{_n(f["off_time_seconds"],1)} s', 100*f['off_time_seconds']/time_max, 'off')}</div>
          <div data-fact-id="time-per-output"><span class="ratio">{f['time_per_completed_ratio']:.2f}× ON / OFF · {_e(t['throughput_quotient'])}</span>
          {_bar('ON', f'{_n(f["on_time_per_completed"],1)} s', 100*f['on_time_per_completed']/time_output_max, 'on')}
          {_bar('OFF', f'{_n(f["off_time_per_completed"],1)} s', 100*f['off_time_per_completed']/time_output_max, 'off')}</div>
          {_chart_caption(t, condition=t['time_condition'], denominator=t['time_denominator'], metric=t['time_metric'], limitation=t['time_limit'])}
        </figure>
      </div>
      <div class="detector-panel">
        <figure class="panel" id="chart-detector" data-denominator="14 complete plus 2 excluded ON Q&amp;A episodes" data-evidence-status="PROSPECTIVE EMPIRICAL EVIDENCE" data-fact-id="detector-distribution">
          <h3>{_e(t['detector_result'])}</h3><div class="detector-bar">{detector_bar}</div>
          <div class="detector-legend">
            <span><i class="swatch seg-strong"></i>{_e(t['strong'])} <bdi>{f['alerts_strong']}</bdi></span>
            <span><i class="swatch seg-weak"></i>{_e(t['weak'])} <bdi>{f['alerts_weak']}</bdi></span>
            <span><i class="swatch seg-no"></i>{_e(t['no_alert'])} <bdi>{f['alerts_no']}</bdi></span>
            <span><i class="swatch seg-excluded"></i>{_e(t['excluded'])} <bdi>{f['alerts_excluded']}</bdi></span>
          </div>{_chart_caption(t, condition=t['detector_condition'], denominator=t['detector_denominator'], metric=t['detector_metric'], limitation=t['detector_limit'])}
        </figure>
        <div class="insight">{_e(t['saturation'])}</div>
        <div class="struct-note"><h3>{_e(t['consistency'])}</h3><p>{_e(t['consistency_body'])}</p><span class="tag unmeasured" style="margin-top:2mm">{_e(t['not_quality'])}</span></div>
      </div>
      {_footer(t, 3)}
    </section>"""


def _signal(label: str, count: int, denominator: int) -> str:
    return f'<div class="signal"><span>{_e(label)}</span><span class="count">{count}/{denominator}</span></div>'


def _page_four(t: dict[str, str], f: dict[str, Any]) -> str:
    d = f["episodes_complete"]
    return f"""
    <section class="page page-4" aria-label="page 4">
      {_header(t, 'supervisor_title', 'supervisor_subtitle')}
      <div class="super-grid">
        <div>
          <div class="rule-box"><h3>{_e(t['rule_title'])}</h3><div class="rule">{_e(t['rule_line1'])}</div><div class="rule">{_e(t['rule_line2'])}</div><div class="rule">{_e(t['rule_line3'])}</div><div class="meaning">{_e(t['alert_meaning'])}</div></div>
          <div class="section-label" style="margin-top:2.5mm">{_e(t['signal_header'])}</div>
          <div class="signals">{_signal(t['s1'],f['signal_s1'],d)}{_signal(t['s2'],f['signal_s2'],d)}{_signal(t['s3'],f['signal_s3'],d)}{_signal(t['s6'],f['signal_s6'],d)}{_signal(t['s7'],f['signal_s7'],d)}</div>
        </div>
        <figure class="panel" id="chart-routes" data-denominator="255 ON questions" data-evidence-status="PROSPECTIVE EMPIRICAL EVIDENCE">
          <h3>{_e(t['agent_header'])}</h3>
          <div class="agent-table">
            <div class="head">{_e(t['asking'])}</div><div class="head">{_e(t['answering'])}</div><div class="head">Q</div>
            <div data-fact-id="route-agent3-agent1">{_e(t['route1'])}</div><div>{_e(t['route1a'])}</div><div class="count">{f['route_agent3_agent1']}</div>
            <div data-fact-id="route-agent3-agent2">{_e(t['route1'])}</div><div>{_e(t['route2a'])}</div><div class="count">{f['route_agent3_agent2']}</div>
          </div>
          <div class="agent4" data-fact-id="agent4-status"><strong>{_e(t['agent4_row'])}</strong><br>{_e(t['not_reached'])}<br>{_e(t['agent4_archival'])}: <bdi>{f['agent4_archival_status']} · queue {f['agent4_archival_queue_status']}</bdi></div>
          {_chart_caption(t, condition=t['routes_condition'], denominator=t['routes_denominator'], metric=t['routes_metric'], limitation=t['routes_limit'])}
        </figure>
      </div>
      <div class="human-grid">
        <div class="panel" data-fact-id="human-next-step"><h3>{_e(t['human_plan'])}</h3><div class="steps"><div class="step">{_e(t['human_step1'])}</div><div class="step">{_e(t['human_step2'])}</div><div class="step">{_e(t['human_step3'])}</div></div></div>
        <div class="panel"><h3>{_e(t['matrix'])}</h3><div class="matrix"><div class="matrix-cell"><span>{_e(t['tp'])}</span><strong>{_e(t['not_measured'])}</strong></div><div class="matrix-cell"><span>{_e(t['fp'])}</span><strong>{_e(t['not_measured'])}</strong></div><div class="matrix-cell"><span>{_e(t['fn'])}</span><strong>{_e(t['not_measured'])}</strong></div><div class="matrix-cell"><span>{_e(t['tn'])}</span><strong>{_e(t['not_measured'])}</strong></div></div></div>
      </div>
      <div class="evidence-strips">
        <div class="engineering-strip"><span class="tag engineering">ENGINEERING-ONLY FIXTURE</span><span><bdi>ENGINEERING_FIXTURE_NOT_SCIENTIFIC</bdi> · {_e(t['engineering_note'])}</span></div>
        <div class="engineering-strip robustness"><span class="tag prospective">DESCRIPTIVE_INSTRUMENT_ROBUSTNESS_ON_ONE_ACCEPTED_RUN</span><span>{_e(t['robustness_note'])}</span></div>
      </div>
      <div class="final">{_e(t['final'])}</div>
      {_footer(t, 4)}
    </section>"""


def build_html(language: str, facts: dict[str, Any]) -> str:
    """Return one four-page HTML document from the canonical fact dictionary."""

    t = _translations(language)
    pages = "".join((_page_one(t, facts), _page_two(t, facts), _page_three(t, facts), _page_four(t, facts)))
    document = f"""<!doctype html>
<html lang="{language}" dir="{t['dir']}">
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{_e(t['title'])}</title><style>{CSS}</style></head>
<body>{pages}</body>
</html>
"""
    return "\n".join(line.rstrip() for line in document.splitlines()) + "\n"


def write_sources(root: Path, output_dir: Path) -> dict[str, Path]:
    facts = load_evidence(root)
    output_dir.mkdir(parents=True, exist_ok=True)
    outputs: dict[str, Path] = {}
    for language in ("en", "he"):
        target = output_dir / f"{OUTPUT_STEM}-{language}.html"
        target.write_text(build_html(language, facts), encoding="utf-8", newline="\n")
        outputs[f"html_{language}"] = target
    facts_path = output_dir / f"{OUTPUT_STEM}-facts.json"
    facts_path.write_text(json.dumps(facts, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    outputs["facts"] = facts_path
    return outputs


def normalize_pdf_metadata(pdf_path: Path) -> None:
    """Freeze Chrome's two volatile timestamp fields without changing PDF offsets."""

    data = pdf_path.read_bytes()
    for field in (b"CreationDate", b"ModDate"):
        pattern = rb"/" + field + rb" \(D:\d{14}[+-]\d{2}'\d{2}'\)"
        replacement = b"/" + field + b" (" + PDF_FIXED_TIMESTAMP + b")"
        data, count = re.subn(pattern, replacement, data)
        if count != 1:
            raise RuntimeError(
                f"Expected exactly one {field.decode('ascii')} in {pdf_path.name}; got {count}"
            )
    pdf_path.write_bytes(data)


def render_pdfs(outputs: dict[str, Path], chrome: Path, timeout: int = 120) -> dict[str, Path]:
    if not chrome.is_file():
        raise RuntimeError(f"Chrome executable not found: {chrome}")
    rendered: dict[str, Path] = {}
    for language in ("en", "he"):
        html_path = outputs[f"html_{language}"].resolve()
        pdf_path = html_path.with_suffix(".pdf")
        if pdf_path.exists():
            pdf_path.unlink()
        with tempfile.TemporaryDirectory(prefix=f"vego-pdf-{language}-") as profile:
            command = [
                str(chrome),
                "--headless=new",
                "--disable-gpu",
                "--no-first-run",
                "--no-default-browser-check",
                "--disable-extensions",
                "--no-pdf-header-footer",
                f"--user-data-dir={profile}",
                f"--print-to-pdf={pdf_path}",
                html_path.as_uri(),
            ]
            completed = subprocess.run(command, check=False, capture_output=True, text=True, timeout=timeout)
            if completed.returncode != 0 or not pdf_path.is_file():
                raise RuntimeError(
                    f"Chrome PDF render failed for {language}: rc={completed.returncode}; "
                    f"stderr={completed.stderr[-1000:]}"
                )
        normalize_pdf_metadata(pdf_path)
        rendered[f"pdf_{language}"] = pdf_path
    return rendered


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=ROOT / "docs" / "research" / "phd-proposal",
    )
    parser.add_argument("--render", action="store_true")
    parser.add_argument(
        "--chrome",
        type=Path,
        default=Path("C:/Program Files/Google/Chrome/Application/chrome.exe"),
    )
    args = parser.parse_args()
    outputs = write_sources(args.root, args.output_dir)
    if args.render:
        outputs.update(render_pdfs(outputs, args.chrome))
    print(json.dumps({name: str(path) for name, path in outputs.items()}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
