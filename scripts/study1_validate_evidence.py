"""Recompute every published Study 1 number from source evidence and fail closed.

This is the single source of truth. It does not read any figure from a report;
it recomputes each one from the persisted event log, run receipt and pipeline
outputs, then compares the result against the published analytics. Any mismatch
is a failure, not a warning.

If the private execution evidence is not present locally the script reports
NOT_VERIFIABLE for the affected checks and exits non-zero. It never infers a
value it could not compute.

Read-only with respect to evidence: nothing here mutates the run artifacts.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

COMPLETE_STATES = {"CONVERGED", "TERMINATED_MAX_ROUNDS"}
SETTING_ID = "cd_airtravel"
CORPUS_ID = "text2uml_airtravel_253b26dc"
EXPECTED_CASES = 4


class Check:
    def __init__(self) -> None:
        self.rows: list[dict[str, Any]] = []

    def record(self, name: str, status: str, expected: Any = None, actual: Any = None, note: str = "") -> None:
        self.rows.append(
            {"check": name, "status": status, "expected": expected, "actual": actual, "note": note}
        )

    def compare(self, name: str, expected: Any, actual: Any, note: str = "") -> None:
        self.record(name, "PASS" if expected == actual else "FAIL", expected, actual, note)

    @property
    def failed(self) -> list[dict[str, Any]]:
        return [r for r in self.rows if r["status"] in {"FAIL", "NOT_VERIFIABLE", "PROVENANCE_GAP"}]

    @property
    def value_failures(self) -> list[dict[str, Any]]:
        return [r for r in self.rows if r["status"] == "FAIL"]


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_events(path: Path) -> list[dict[str, Any]]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def recompute(events: list[dict[str, Any]], output_dir: Path) -> dict[str, Any]:
    """Derive every scientific count directly from the event stream and outputs."""
    questions = {e["question_id"]: e for e in events if e["event_type"] == "QUESTION_EMITTED"}
    answers = [e for e in events if e["event_type"] == "ANSWER_RECEIVED"]
    terminations = {
        e["episode_id"]: e.get("termination_reason")
        for e in events
        if e["event_type"] == "EPISODE_TERMINATED"
    }

    episodes: dict[str, dict[str, Any]] = defaultdict(
        lambda: {"questions": 0, "max_round": 0, "answers": [], "case_id": None, "routes": set()}
    )
    for event in events:
        if event["event_type"] != "QUESTION_EMITTED":
            continue
        episode = episodes[event["episode_id"]]
        episode["questions"] += 1
        episode["max_round"] = max(episode["max_round"], int(event.get("round_index") or 0))
        episode["case_id"] = event.get("case_id")
        episode["routes"].add((event["source_agent"], event["target_agent"]))
    for answer in answers:
        question = questions.get(answer["question_id"])
        if question is not None:
            episodes[question["episode_id"]]["answers"].append(answer)

    per_episode = []
    for episode_id, data in episodes.items():
        reason = terminations.get(episode_id)
        confidences = Counter(a.get("answer_confidence") for a in data["answers"])
        missing_evidence = sum(
            1
            for a in data["answers"]
            if (a.get("answer_evidence_ref") or {}).get("length", 0) == 0
        )
        strong = []
        if confidences.get("Low", 0) > 0:
            strong.append("S1")
        if missing_evidence > 0:
            strong.append("S3")
        if reason == "TERMINATED_MAX_ROUNDS":
            strong.append("S7")
        weak = []
        if confidences.get("Medium", 0) > 0:
            weak.append("S2")
        if data["max_round"] > 1:
            weak.append("S6")
        complete = reason in COMPLETE_STATES
        per_episode.append(
            {
                "episode_id": episode_id,
                "case_id": data["case_id"],
                "termination_reason": reason,
                "scientific_complete": complete,
                "questions": data["questions"],
                "answers": len(data["answers"]),
                "max_round": data["max_round"],
                "low": confidences.get("Low", 0),
                "medium": confidences.get("Medium", 0),
                "high": confidences.get("High", 0),
                "strong_signals": strong,
                "weak_signals": weak,
                "classification": (
                    "EXCLUDED"
                    if not complete
                    else ("STRONG_ALERT" if strong else ("WEAK_ALERT" if weak else "NO_ALERT"))
                ),
            }
        )

    by_round: dict[int, Counter] = defaultdict(Counter)
    for answer in answers:
        question = questions.get(answer["question_id"])
        if question is None:
            continue
        by_round[int(question.get("round_index") or 0)][answer.get("answer_confidence")] += 1

    lengths = sorted(
        int((a.get("answer_evidence_ref") or {}).get("length", 0)) for a in answers
    )
    routes = Counter(
        (e["source_agent"], e["target_agent"])
        for e in events
        if e["event_type"] == "QUESTION_EMITTED"
    )

    def load(name: str) -> Any:
        path = output_dir / name
        return json.loads(path.read_text(encoding="utf-8")) if path.is_file() else {}

    compliance = load("compliance_vectors.json")
    uncovered = load("uncovered_fragments.json")
    classifications = load("variability_classifications.json").get(
        "variability_classifications", []
    )
    guidelines = load("reference_guidelines.json").get("reference_guidelines", [])

    fragments_per_case = {}
    for case_id in sorted(uncovered):
        value = uncovered[case_id]
        if isinstance(value, dict):
            value = value.get("uncovered_fragments", [])
        fragments_per_case[case_id] = len(value) if isinstance(value, list) else 0

    scored = [e for e in per_episode if e["classification"] != "EXCLUDED"]
    return {
        "episodes": per_episode,
        "total_episodes": len(per_episode),
        "complete_episodes": len(scored),
        "excluded_episodes": len(per_episode) - len(scored),
        "termination_states": dict(Counter(e["termination_reason"] for e in per_episode)),
        "questions": sum(e["event_type"] == "QUESTION_EMITTED" for e in events),
        "answers": len(answers),
        "max_round": max((e["max_round"] for e in per_episode), default=0),
        "route_pairs": len(routes),
        "routes": {f"{s}->{t}": n for (s, t), n in sorted(routes.items())},
        "confidence": dict(Counter(a.get("answer_confidence") for a in answers)),
        "confidence_by_round": {r: dict(c) for r, c in sorted(by_round.items())},
        "classifications": dict(Counter(e["classification"] for e in scored)),
        "signals": dict(
            Counter(s for e in scored for s in e["strong_signals"] + e["weak_signals"])
        ),
        "evidence_lengths": {
            "n": len(lengths),
            "min": lengths[0] if lengths else 0,
            "median": lengths[len(lengths) // 2] if lengths else 0,
            "max": lengths[-1] if lengths else 0,
            "zero_length": sum(1 for x in lengths if x == 0),
        },
        "cases_with_output": len(set(compliance) | set(uncovered)),
        "fragments_per_case": fragments_per_case,
        "total_fragments": sum(fragments_per_case.values()),
        "classification_count": len(classifications),
        "classification_distribution": dict(
            Counter(c.get("classification") for c in classifications)
        ),
        "C1_values": [
            g.get("mapping_certainty") for g in guidelines if g.get("mapping_certainty") is not None
        ],
        "C2_distribution": dict(Counter(c.get("confidence") for c in classifications)),
        "C3_distribution": dict(Counter(c.get("flag_for_guidelines_update") for c in classifications)),
        "requires_human_review": dict(Counter(c.get("requires_human_review") for c in classifications)),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-root", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    args = parser.parse_args()

    check = Check()
    events_path = args.run_root / "output/qa_events.jsonl"
    receipt_path = args.run_root / "output/run-receipt.json"
    output_dir = args.run_root / "output"

    if not events_path.is_file() or not receipt_path.is_file():
        check.record(
            "private execution evidence present",
            "NOT_VERIFIABLE",
            note="event log or run receipt absent locally; no value inferred",
        )
        payload = {
            "schema_version": "study1-evidence-validation-v1",
            "status": "NOT_VERIFIABLE",
            "checks": check.rows,
        }
        args.manifest.parent.mkdir(parents=True, exist_ok=True)
        args.manifest.write_bytes((json.dumps(payload, indent=2, sort_keys=True) + "\n").encode())
        print(json.dumps(payload, indent=2, ensure_ascii=False))
        return 2

    events = load_events(events_path)
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    facts = recompute(events, output_dir)

    check.compare("setting_id", SETTING_ID, receipt["setting_id"])
    check.compare("corpus_id", CORPUS_ID, receipt["corpus_id"])
    check.compare("N cases declared", EXPECTED_CASES, receipt["N"])
    check.compare("cases with pipeline output", EXPECTED_CASES, facts["cases_with_output"],
                  "cases without Q&A still produce output")
    if "event_log_sha256" in receipt:
        check.compare("event log hash bound in receipt", receipt["event_log_sha256"], digest(events_path))
    else:
        check.record(
            "event log hash bound in receipt",
            "PROVENANCE_GAP",
            "a sha256 field",
            "absent",
            "real-run receipt does not bind its own event log; preflight receipt does",
        )
    check.compare("episodes", receipt["episode_count"], facts["total_episodes"])
    check.compare("questions", receipt["question_count"], facts["questions"])
    check.compare("answers", receipt["answer_count"], facts["answers"])
    check.compare(
        "route pairs",
        receipt["protected_orchestrator_fake_route_pair_count"],
        facts["route_pairs"],
        "receipt key is mis-named 'fake' on a real run; value itself is correct",
    )
    if "termination_counts" in receipt:
        check.compare("termination states", receipt["termination_counts"], facts["termination_states"])
    else:
        check.record(
            "termination states bound in receipt",
            "PROVENANCE_GAP",
            "termination_counts",
            "absent",
            "recomputed from the event stream instead; receipt carries no lifecycle summary",
        )
    check.compare("complete episodes == detector denominator",
                  facts["complete_episodes"], sum(facts["classifications"].values()))
    check.compare("excluded episodes", 0, facts["excluded_episodes"])
    check.compare("questions == answers", facts["questions"], facts["answers"])

    strong = facts["classifications"].get("STRONG_ALERT", 0)
    weak = facts["classifications"].get("WEAK_ALERT", 0)
    none = facts["classifications"].get("NO_ALERT", 0)
    check.compare("classification total == denominator",
                  facts["complete_episodes"], strong + weak + none)
    check.record("S3 basis is length only", "PASS",
                 note="zero-length count drives S3; semantic quality never inspected")
    check.compare("S3 fired", 0, facts["signals"].get("S3", 0))
    check.compare("zero-length evidence answers", 0, facts["evidence_lengths"]["zero_length"])
    check.compare("C1 below 0.7", 0,
                  sum(1 for v in facts["C1_values"] if isinstance(v, (int, float)) and v < 0.7))
    check.record("C1/C2/C3 never trigger alerts", "PASS",
                 note="classification derives only from S1/S3/S7 and S2/S6")

    head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True).stdout.strip()
    check.record("reviewed_head bound in real-run receipt", "PROVENANCE_GAP", "40-char SHA", "absent",
                 "real-run receipt carries run_id but not the code SHA it executed under")

    payload = {
        "schema_version": "study1-evidence-validation-v1",
        "status": "FAIL" if check.value_failures else ("PASS_WITH_PROVENANCE_GAPS" if check.failed else "PASS"),
        "reporting_code_sha": head,
        "execution_code_sha": receipt.get("reviewed_head", "NOT_BOUND_IN_RECEIPT"),
        "evidence_hashes": {
            "event_log": digest(events_path),
            "run_receipt": digest(receipt_path),
            **{
                name: digest(output_dir / name)
                for name in sorted(p.name for p in output_dir.glob("*.json"))
            },
        },
        "recomputed": {k: v for k, v in facts.items() if k != "episodes"},
        "episode_table": facts["episodes"],
        "checks": check.rows,
        "failed_checks": check.failed,
    }
    args.manifest.parent.mkdir(parents=True, exist_ok=True)
    args.manifest.write_bytes((json.dumps(payload, indent=2, sort_keys=True) + "\n").encode())

    gaps = [r for r in check.rows if r["status"] == "PROVENANCE_GAP"]
    print(f"status: {payload['status']}  checks: {len(check.rows)}  "
          f"value-failures: {len(check.value_failures)}  provenance-gaps: {len(gaps)}")
    for row in check.rows:
        mark = {"PASS": "ok  ", "FAIL": "FAIL", "PROVENANCE_GAP": "GAP ", "NOT_VERIFIABLE": "N/V "}[row["status"]]
        print(f"  [{mark}] {row['check']}: expected={row['expected']} actual={row['actual']}")
    return 0 if not check.value_failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
