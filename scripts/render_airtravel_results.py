"""Deterministic post-run renderer for the AirTravel preliminary results.

Transforms a future qa-communication event log into: machine JSON, an episode
CSV table, a Detector-v1 classification CSV, and the compact Hebrew RTL report
rendered from the committed template.  Detector-v1 itself is imported unchanged
from ``scripts/extract_qa_escalation_features.py`` (single-sourced, frozen);
this module adds description only and never re-classifies.

Signal counts S1/S2/S3/S6/S7 are descriptive per-episode booleans computed
with the frozen v1.0.1 rules over complete episodes only; every scientific
denominator excludes ``INCOMPLETE_TECHNICAL``.  C1 is reported as unavailable
from the event log (mapping_certainty is an Agent-2 artifact, not a Q&A
event); S5 is unavailable (normalized-repeat equality is not persisted); S8 is
reported descriptively from ``follow_up_present``; S9 is reported as the raw
question-per-episode distribution with no threshold.

Rendering fails (nonzero exit) if any ``{{...}}`` token remains in the final
report, so a partially filled report can never be delivered.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from extract_qa_escalation_features import extract_live_corpus  # noqa: E402

DEFAULT_TEMPLATE = (
    REPO_ROOT / "docs" / "research" / "phd-proposal"
    / "2026-09-05-airtravel-preliminary-results-template-he.md"
)
TOKEN_RE = re.compile(r"\{\{[A-Z0-9_]+\}\}")
FORBIDDEN_REPORT_TERMS = ("accuracy", "precision", "recall", "F1")


def _signal_booleans(episode: dict[str, Any]) -> dict[str, bool]:
    answers = episode.get("answers", [])
    evidence_missing = any(
        (ref := row.get("answer_evidence_ref")) is None or ref.get("length", 0) == 0
        for row in answers
    )
    return {
        "S1": any(row.get("answer_confidence") == "Low" for row in answers),
        "S2": any(row.get("answer_confidence") == "Medium" for row in answers),
        "S3": evidence_missing,
        "S6": episode.get("round_count", 0) > 1,
        "S7": episode.get("termination_reason") == "TERMINATED_MAX_ROUNDS",
    }


def _distribution(counter: Counter[Any]) -> str:
    if not counter:
        return "אין נתונים (0 פרקים)"
    return "; ".join(f"{key}: {count}" for key, count in sorted(counter.items(), key=str))


def build_report_fields(corpus: dict[str, Any], args: argparse.Namespace) -> dict[str, str]:
    episodes = corpus["episodes"]
    complete = [e for e in episodes if e["scientific_complete"]]
    detector = {row["episode_id"]: row for row in corpus["detector_v1"]}
    signals = {e["episode_id"]: _signal_booleans(e) for e in complete}
    classifications = Counter(
        detector[e["episode_id"]]["classification"] for e in complete
    )
    terminations = Counter(
        e["termination_reason"] or "UNTERMINATED" for e in episodes
    )
    termination_rows = "\n".join(
        f"| `{state}` | {count} |" for state, count in sorted(terminations.items())
    ) or "| — | 0 |"
    routes = Counter(
        f"{source} ← {target}"
        for e in episodes for source, target in (tuple(pair) for pair in e["source_target_pairs"])
    )
    route_rows = "\n".join(
        f"| `{route}` | {count} |" for route, count in sorted(routes.items())
    ) or "| — | 0 |"
    rounds = Counter(e["round_count"] for e in complete)
    confidence = Counter(
        row.get("answer_confidence") for e in complete for row in e.get("answers", [])
    )
    evidence = Counter(
        "present" if (ref := row.get("answer_evidence_ref")) is not None and ref.get("length", 0) > 0
        else "missing"
        for e in complete for row in e.get("answers", [])
    )
    zero_qa = (
        "VALID_ZERO_QA_RUN (תוצאה תקפה לפי v1.0.1 §9)" if not episodes else "NOT_ZERO_QA"
    )
    return {
        "RUN_SHA": args.run_sha,
        "MODEL": args.model,
        "RUN_DATE": args.run_date,
        "SETTING_ID": corpus.get("setting_id") or "cd_airtravel",
        "CORPUS_ID": corpus.get("corpus_id") or "text2uml_airtravel_253b26dc",
        "N_CASES": str(args.case_count),
        "TOTAL_CALLS": args.total_calls,
        "RUNTIME_SECONDS": args.runtime_seconds,
        "MEASURED_COST": args.measured_cost,
        "TECHNICAL_STATUS": args.technical_status,
        "N_TOTAL_EPISODES": str(len(episodes)),
        "N_COMPLETE_EPISODES": str(len(complete)),
        "N_INCOMPLETE_TECHNICAL": str(
            corpus["summary"]["excluded_incomplete_technical"]
        ),
        "ZERO_QA_STATUS": zero_qa,
        "QUESTIONS_TOTAL": str(corpus["summary"]["questions"]),
        "ANSWERS_TOTAL": str(corpus["summary"]["answers"]),
        "ROUND_DISTRIBUTION": _distribution(rounds),
        "CONFIDENCE_DISTRIBUTION": _distribution(confidence),
        "EVIDENCE_DISTRIBUTION": _distribution(evidence),
        "DENOMINATOR": str(len(complete)),
        "N_S1": str(sum(s["S1"] for s in signals.values())),
        "N_S2": str(sum(s["S2"] for s in signals.values())),
        "N_S3": str(sum(s["S3"] for s in signals.values())),
        "N_S6": str(sum(s["S6"] for s in signals.values())),
        "N_S7": str(sum(s["S7"] for s in signals.values())),
        "C1_STATUS": "לא זמין מיומן האירועים (mapping_certainty אינו אירוע Q&A); תיאור בלבד",
        "S5_STATUS": "לא זמין (השוואת נוסח מנורמלת אינה נשמרת); מדווח כלא-שמיש, לא מושמט",
        "S8_STATUS": _distribution(Counter(
            "follow_up" if e["follow_up_present"] else "no_follow_up" for e in complete
        )),
        "S9_STATUS": _distribution(Counter(e["question_count"] for e in complete)) + " (ללא סף)",
        "N_STRONG_ALERT": str(classifications.get("STRONG_ALERT", 0)),
        "N_WEAK_ALERT": str(classifications.get("WEAK_ALERT", 0)),
        "N_NO_ALERT": str(classifications.get("NO_ALERT", 0)),
        "TERMINATION_TABLE": termination_rows,
        "ROUTES_TABLE": route_rows,
        "DESCRIPTIVE_FINDINGS": args.findings,
        "LIMITED_CONCLUSION": args.conclusion,
        "NEXT_STEP": args.next_step,
    }


def render_report(template_text: str, fields: dict[str, str]) -> str:
    rendered = template_text
    for token, value in fields.items():
        rendered = rendered.replace("{{" + token + "}}", value)
    residual = TOKEN_RE.findall(rendered)
    if residual:
        raise ValueError(f"unfilled template tokens remain: {sorted(set(residual))}")
    lowered = rendered.lower()
    for term in FORBIDDEN_REPORT_TERMS:
        if term.lower() in lowered:
            raise ValueError(f"forbidden claim term in rendered report: {term}")
    return rendered


def write_outputs(corpus: dict[str, Any], report: str, output_root: Path) -> dict[str, Path]:
    output_root.mkdir(parents=True, exist_ok=True)
    machine = output_root / "airtravel-results-machine.json"
    machine.write_text(json.dumps(corpus, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
                       encoding="utf-8")
    episodes_csv = output_root / "airtravel-episodes.csv"
    episode_fields = ["episode_id", "run_id", "question_count", "answer_count", "round_count",
                      "follow_up_present", "converged", "termination_reason",
                      "scientific_complete", "exclusion_reason"]
    with episodes_csv.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=episode_fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(corpus["episodes"])
    detector_csv = output_root / "airtravel-detector.csv"
    detector_fields = ["episode_id", "classification", "candidate_alert", "reason_codes",
                       "exclusion_reason"]
    with detector_csv.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=detector_fields, extrasaction="ignore")
        writer.writeheader()
        for row in corpus["detector_v1"]:
            writer.writerow({**row, "reason_codes": ";".join(row["reason_codes"])})
    report_path = output_root / "airtravel-preliminary-results-he.md"
    report_path.write_text(report, encoding="utf-8")
    return {"machine": machine, "episodes": episodes_csv,
            "detector": detector_csv, "report": report_path}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--events", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--template", type=Path, default=DEFAULT_TEMPLATE)
    parser.add_argument("--run-sha", required=True)
    parser.add_argument("--model", required=True)
    parser.add_argument("--run-date", required=True)
    parser.add_argument("--case-count", type=int, required=True)
    parser.add_argument("--total-calls", required=True)
    parser.add_argument("--runtime-seconds", required=True)
    parser.add_argument("--measured-cost", default="TO BE MEASURED")
    parser.add_argument("--technical-status", required=True)
    parser.add_argument("--findings", required=True)
    parser.add_argument("--conclusion", required=True)
    parser.add_argument("--next-step", required=True)
    args = parser.parse_args()

    corpus = extract_live_corpus(args.events)
    fields = build_report_fields(corpus, args)
    report = render_report(args.template.read_text(encoding="utf-8"), fields)
    paths = write_outputs(corpus, report, args.output_root)
    print(json.dumps({name: str(path) for name, path in paths.items()}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
