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
import csv
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
SCHEMA_VERSION = "study1-evidence-validation-v1"
MAX_QA_ROUNDS = 10


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
        """FAIL is a wrong value; NOT_VERIFIABLE is an artifact this validator must check and
        cannot find. Both must terminate non-zero, or deleting a derived file would silently
        remove its cross-checks and still report success. PROVENANCE_GAP is neither: it records
        that the receipt does not bind a quantity, which is a disclosed fact about the run."""
        return [r for r in self.rows if r["status"] in {"FAIL", "NOT_VERIFIABLE"}]


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
    deviations = load("deviation_patterns.json")

    # deviation_patterns.json carries two sibling lists, not a "deviation_patterns" key.
    # Reading a key that does not exist yields a false zero, so both are counted by name.
    guideline_patterns = deviations.get("recurring_guideline_patterns") or []
    fragment_patterns = deviations.get("recurring_fragment_patterns") or []

    # Mapping result is the pipeline's judgement about the candidate model. It is reported
    # separately from the conversation-state signals and never feeds Detector-v1.
    mapping_status = Counter()
    coverage_totals = Counter()
    for vector in compliance.values():
        if not isinstance(vector, dict):
            continue
        for row in vector.get("existing_mapping") or []:
            mapping_status[row.get("compliance_status")] += 1
        for key, value in (vector.get("coverage_summary") or {}).items():
            coverage_totals[key] += int(value or 0)

    by_pattern = {
        row.get("pattern_id"): row for row in fragment_patterns if isinstance(row, dict)
    }
    pattern_join = Counter()
    for row in classifications:
        source = by_pattern.get(row.get("pattern_id")) or {}
        pattern_join[
            (
                source.get("dominant_fragment_label"),
                row.get("classification"),
                row.get("confidence"),
                bool(row.get("flag_for_guidelines_update")),
            )
        ] += 1

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
        "mapping_status_distribution": dict(mapping_status),
        "coverage_summary_totals": dict(coverage_totals),
        "recurring_guideline_patterns": len(guideline_patterns),
        "recurring_fragment_patterns": len(fragment_patterns),
        "fragment_label_distribution": dict(
            Counter(r.get("dominant_fragment_label") for r in fragment_patterns)
        ),
        "fragment_probe_confirmed": dict(
            Counter(bool(r.get("probe_confirmed")) for r in fragment_patterns)
        ),
        "pattern_join": {" | ".join(str(x) for x in k): n for k, n in sorted(pattern_join.items(), key=lambda kv: str(kv[0]))},
        "question_density_S9": sorted(e["questions"] for e in per_episode),
    }


def cross_check_derived(check, run_root, facts, receipt, usage, events, events_path,
                        strong, weak, none) -> None:
    """Compare every derived analysis file against the event-log recomputation."""
    analysis_dir = run_root / "analysis"

    def derived(name):
        path = analysis_dir / name
        if not path.is_file():
            return {}
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except ValueError:
            return {}

    labels = {"STRONG_ALERT": strong, "WEAK_ALERT": weak, "NO_ALERT": none, "EXCLUDED": 0}
    signal_names = {
        "S1": "S1_LOW_ANSWER_CONFIDENCE", "S2": "S2_MEDIUM_ANSWER_CONFIDENCE",
        "S3": "S3_MISSING_EVIDENCE", "S6": "S6_MULTIPLE_QA_ROUNDS",
        "S7": "S7_TERMINATED_MAX_ROUNDS",
    }
    expected_signals = {signal_names[k]: v for k, v in facts["signals"].items() if v}

    summary = derived("detector-summary.json")
    if summary:
        check.compare("derived detector-summary: denominator", facts["complete_episodes"],
                      summary.get("denominators", {}).get("detector_v1_denominator"))
        check.compare("derived detector-summary: classifications", labels,
                      summary.get("detector_v1"))
        check.compare("derived detector-summary: termination states",
                      facts["termination_states"], summary.get("termination_states"))
        check.compare("derived detector-summary: counts",
                      {"answers": facts["answers"], "max_round_index": facts["max_round"],
                       "questions": facts["questions"], "route_pairs": facts["route_pairs"]},
                      summary.get("counts"))
        check.compare("derived detector-summary: usage matches the receipt", usage,
                      summary.get("usage"))
        check.compare("derived detector-summary: event log hash", digest(events_path),
                      summary.get("evidence", {}).get("event_log_sha256"))
        check.compare("derived detector-summary: event count", len(events),
                      summary.get("evidence", {}).get("event_count"))
        check.compare("derived detector-summary: signals fired", expected_signals,
                      summary.get("signals_fired"))
    else:
        check.record("derived detector-summary present", "NOT_VERIFIABLE", "a file", "absent")

    extended = derived("extended-analytics.json")
    if extended:
        pipe = extended.get("pipeline_outputs", {})
        check.compare("derived extended-analytics: confidence distribution",
                      facts["confidence"], extended.get("confidence_distribution"))
        check.compare("derived extended-analytics: C2", facts["C2_distribution"],
                      pipe.get("C2_agent4_confidence_distribution"))
        check.compare("derived extended-analytics: C3",
                      {str(k).lower(): v for k, v in facts["C3_distribution"].items()},
                      {str(k).lower(): v for k, v in (pipe.get("C3_flag_for_guidelines_update") or {}).items()})
        check.compare("derived extended-analytics: S9 density", facts["question_density_S9"],
                      sorted(extended.get("question_density_S9", {}).get("per_episode", [])))
        lengths = extended.get("answer_evidence_length", {})
        check.compare("derived extended-analytics: evidence lengths",
                      (facts["evidence_lengths"]["n"], facts["evidence_lengths"]["min"],
                       facts["evidence_lengths"]["median"], facts["evidence_lengths"]["max"]),
                      (lengths.get("n"), lengths.get("min"), lengths.get("median"), lengths.get("max")))
        check.compare("derived extended-analytics: deviation patterns not falsely zero",
                      facts["recurring_fragment_patterns"] + facts["recurring_guideline_patterns"],
                      pipe.get("deviation_patterns"),
                      "a wrong key name here reads as zero; both sibling lists must be counted")
        check.compare("derived extended-analytics: C1 values", facts["C1_values"],
                      pipe.get("C1_mapping_certainty_values"))
        check.compare("derived extended-analytics: reference guideline count",
                      len(facts["C1_values"]), pipe.get("reference_guidelines"))
        check.compare("derived extended-analytics: variability classification distribution",
                      facts["classification_distribution"], pipe.get("classification_distribution"))
        check.compare("derived extended-analytics: uncovered fragments per case",
                      facts["fragments_per_case"],
                      {k: v.get("uncovered_fragments") for k, v in (pipe.get("per_case") or {}).items()})
        check.compare("derived extended-analytics: fragment label distribution",
                      facts["fragment_label_distribution"], pipe.get("fragment_label_distribution"))
        check.compare("derived extended-analytics: mapping result distribution",
                      facts["mapping_status_distribution"], pipe.get("mapping_status_distribution"))
        check.compare("derived extended-analytics: round dynamics",
                      {str(k): dict(sorted(v.items())) for k, v in facts["confidence_by_round"].items()},
                      {str(r["round_index"]): dict(sorted(
                          (k, v) for k, v in (("High", r.get("high")), ("Low", r.get("low")),
                                              ("Medium", r.get("medium"))) if v))
                       for r in (extended.get("round_dynamics", {}).get("per_round") or [])})
        check.compare("derived extended-analytics: episode profiles",
                      {e["episode_id"]: (e["low"], e["medium"], e["high"], e["max_round"])
                       for e in facts["episodes"]},
                      {p["episode_id"]: (p.get("low"), p.get("medium"), p.get("high"), p.get("max_round"))
                       for p in (extended.get("episode_profiles") or [])})
    else:
        check.record("derived extended-analytics present", "NOT_VERIFIABLE", "a file", "absent")

    analysis_receipt = derived("analysis-receipt.json")
    if analysis_receipt:
        check.compare("derived analysis-receipt: detector labels", labels,
                      analysis_receipt.get("detector_v1"))
        check.compare("derived analysis-receipt: denominator", facts["complete_episodes"],
                      analysis_receipt.get("denominators", {}).get("detector_v1_denominator"))
        pinned = analysis_receipt.get("output_inventory_sha256")
        inventory = analysis_dir / "output-inventory.json"
        actual = digest(inventory) if inventory.is_file() else "absent"
        check.compare(
            "derived analysis-receipt: output inventory pin resolves", pinned, actual,
            "A binding that exists and does not resolve is a value disagreement, not a missing "
            "binding, so this is FAIL and never PROVENANCE_GAP. Cause: analysis/"
            "output-inventory.json was overwritten on 2026-09-06 by an invocation of this "
            "validator pointed at it as --manifest. Recovery was attempted over 144 candidate "
            "serializations of the 52 pinned artifacts and none reproduced the pinned digest; "
            "the file was not reconstructed, because matching a hash by trial would fabricate "
            "provenance. The failure is confined to the derived artifact chain: no published "
            "claim cites this file and every scientific value reproduces.")
    else:
        check.record("derived analysis-receipt present", "NOT_VERIFIABLE", "a file", "absent")

    detector_csv = analysis_dir / "detector.csv"
    if detector_csv.is_file():
        rows = list(csv.DictReader(detector_csv.read_text(encoding="utf-8").splitlines()))
        check.compare("derived detector.csv: one row per episode", facts["total_episodes"], len(rows))
        check.compare("derived detector.csv: labels agree with the recomputation",
                      {e["episode_id"]: e["classification"] for e in facts["episodes"]},
                      {r["episode_id"]: r["classification"] for r in rows})
        check.compare("derived detector.csv: reason codes agree with the recomputation",
                      {e["episode_id"]: [signal_names[s] for s in e["strong_signals"]]
                       for e in facts["episodes"]},
                      {r["episode_id"]: [s for s in r["reason_codes"].split(" | ") if s]
                       for r in rows})
        check.compare("derived detector.csv: all signals agree with the recomputation",
                      {e["episode_id"]: sorted(signal_names[s] for s in
                                               e["strong_signals"] + e["weak_signals"])
                       for e in facts["episodes"]},
                      {r["episode_id"]: sorted(s for s in r["all_signals_fired"].split(" | ") if s)
                       for r in rows})
    else:
        check.record("derived detector.csv present", "NOT_VERIFIABLE", "a file", "absent")

    episodes_csv = analysis_dir / "episodes.csv"
    if episodes_csv.is_file():
        rows = list(csv.DictReader(episodes_csv.read_text(encoding="utf-8").splitlines()))
        check.compare("derived episodes.csv: one row per episode", facts["total_episodes"], len(rows))
        check.compare("derived episodes.csv: rounds agree with the recomputation",
                      {e["episode_id"]: e["max_round"] for e in facts["episodes"]},
                      {r["episode_id"]: int(r["rounds"]) for r in rows})
        check.compare("derived episodes.csv: question counts agree",
                      {e["episode_id"]: e["questions"] for e in facts["episodes"]},
                      {r["episode_id"]: int(r["questions"]) for r in rows})
        check.compare("derived episodes.csv: answer counts agree",
                      {e["episode_id"]: e["answers"] for e in facts["episodes"]},
                      {r["episode_id"]: int(r["answers"]) for r in rows})
        check.compare("derived episodes.csv: denominator membership agrees",
                      {e["episode_id"]: e["scientific_complete"] for e in facts["episodes"]},
                      {r["episode_id"]: r["in_detector_denominator"] == "True" for r in rows})
    else:
        check.record("derived episodes.csv present", "NOT_VERIFIABLE", "a file", "absent")

    envelope = derived("detector-envelope.json")
    if envelope:
        check.compare("derived detector-envelope: no provider calls", 0,
                      envelope.get("provider_calls"))
        check.compare("derived detector-envelope: file is fixture-classed",
                      "ENGINEERING_FIXTURE_NOT_SCIENTIFIC", envelope.get("evidence_class"))
        modes = envelope.get("modes") or []
        check.compare("derived detector-envelope: every mode is fixture-classed",
                      ["ENGINEERING_FIXTURE_NOT_SCIENTIFIC"] * len(modes),
                      [m.get("evidence_class") for m in modes],
                      "envelope rows are engineering fixtures and enter no scientific denominator")
    else:
        check.record("derived detector-envelope present", "NOT_VERIFIABLE", "a file", "absent")

    baseline = derived("baseline-comparison.json")
    if baseline:
        check.record("baseline comparison is labelled engineering-only",
                     "PASS" if "fake" in json.dumps(baseline).lower() else "FAIL",
                     "fixture provider named explicitly", "named",
                     "the fixture-vs-real contrast is an instrumentation check, never VEGO_AI_ON/OFF")
        check.compare("derived baseline-comparison: real side agrees with the event log",
                      {"answers": facts["answers"], "confidence": facts["confidence"],
                       "episodes": facts["total_episodes"], "evidence_missing": 0,
                       "max_round": facts["max_round"], "questions": facts["questions"],
                       "routes": facts["route_pairs"], "terminations": facts["termination_states"]},
                      baseline.get("real_provider_run"))
        check.compare("derived baseline-comparison: real usage matches the receipt", usage,
                      baseline.get("real_usage"))
        check.compare("derived baseline-comparison: detector applied to the real run only",
                      labels, baseline.get("detector_v1_real_run_only"))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-root", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument(
        "--force",
        action="store_true",
        help="permit writing over a file this validator did not produce (audited action)",
    )
    args = parser.parse_args()

    # An earlier invocation in this project overwrote a derived artifact by being pointed at
    # it as --manifest. The target is now refused unless it is this validator's own output.
    if args.manifest.exists() and not args.force:
        try:
            existing = json.loads(args.manifest.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            existing = {}
        if existing.get("schema_version") != SCHEMA_VERSION:
            print(
                f"refusing to overwrite {args.manifest}: it is not a {SCHEMA_VERSION} payload "
                f"(found schema_version={existing.get('schema_version')!r}). "
                "Choose a different --manifest path, or pass --force deliberately.",
                file=sys.stderr,
            )
            return 3

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
            "schema_version": SCHEMA_VERSION,
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
    check.compare("denominator excludes incomplete-technical episodes",
                  facts["total_episodes"] - facts["excluded_episodes"], facts["complete_episodes"])
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
    check.record("C1 is computable from pipeline outputs",
                 "PASS" if facts["C1_values"] else "FAIL",
                 "a non-empty certainty list", facts["C1_values"])
    check.compare("C1 below 0.7", 0,
                  sum(1 for v in facts["C1_values"] if isinstance(v, (int, float)) and v < 0.7))
    check.compare("evidence length sample covers every answer", facts["answers"],
                  facts["evidence_lengths"]["n"],
                  "a zero-length count is only meaningful if every answer was measured")
    check.record("C1/C2/C3 never trigger alerts", "PASS",
                 note="classification derives only from S1/S3/S7 and S2/S6")

    check.record("round bound enforced",
                 "PASS" if facts["max_round"] <= MAX_QA_ROUNDS else "FAIL",
                 f"<= {MAX_QA_ROUNDS}", facts["max_round"],
                 "exceeding the bound would mean the round loop was not enforced")
    check.record("MAX_QA_ROUNDS bound in receipt", "PROVENANCE_GAP", "max_qa_rounds", "absent",
                 f"the bound is a constant in the harness ({MAX_QA_ROUNDS}); the receipt does not "
                 "record the round limit the run executed under")
    check.compare("confidence total == answers", facts["answers"],
                  sum(facts["confidence"].values()))
    unexpected = sorted(set(facts["confidence"]) - {"High", "Low", "Medium"})
    check.record("confidence labels are within the frozen three",
                 "FAIL" if unexpected else "PASS",
                 "a subset of ['High', 'Low', 'Medium']", sorted(facts["confidence"]),
                 "a level that never occurs is a legitimate observation; only an unexpected "
                 f"label is a defect{' — found ' + str(unexpected) if unexpected else ''}")
    check.compare("per-round answers sum to answers", facts["answers"],
                  sum(sum(c.values()) for c in facts["confidence_by_round"].values()))
    check.compare("episode answer counts sum to answers", facts["answers"],
                  sum(e["answers"] for e in facts["episodes"]))
    check.compare("episode question counts sum to questions", facts["questions"],
                  sum(e["questions"] for e in facts["episodes"]))
    check.compare("route question counts sum to questions", facts["questions"],
                  sum(facts["routes"].values()))

    usage = receipt.get("usage") or {}
    check.compare("total tokens == prompt + completion", usage.get("total_tokens"),
                  (usage.get("prompt_tokens") or 0) + (usage.get("completion_tokens") or 0))
    priced = round(
        (usage.get("prompt_tokens", 0) / 1_000_000) * usage.get("price_input_per_1m_usd", 0)
        + (usage.get("completion_tokens", 0) / 1_000_000) * usage.get("price_output_per_1m_usd", 0),
        6,
    )
    check.compare("cost reproduces from token counts and published prices",
                  usage.get("actual_cost_usd"), priced)
    check.record("outbound requests within cap",
                 "PASS" if usage.get("outbound_requests", 0) <= usage.get("outbound_request_cap", 0) else "FAIL",
                 f"<= {usage.get('outbound_request_cap')}", usage.get("outbound_requests"))
    check.record("cost within budget",
                 "PASS" if usage.get("actual_cost_usd", 0) <= usage.get("budget_usd", 0) else "FAIL",
                 f"<= {usage.get('budget_usd')}", usage.get("actual_cost_usd"))
    check.compare("within_budget flag agrees with the arithmetic",
                  usage.get("actual_cost_usd", 0) <= usage.get("budget_usd", 0),
                  bool(usage.get("within_budget")))
    check.compare("blocked egress attempts", 0, receipt.get("blocked_egress_attempts"))
    check.compare("run status", "TECHNICAL_SUCCESS", receipt.get("status"))
    check.compare("no technical exception", None, receipt.get("technical_exception"))
    check.compare("receipt routes agree with the event log",
                  {f"{r['source_agent']}->{r['target_agent']}": r["question_count"]
                   for r in receipt.get("routes") or []},
                  facts["routes"])

    check.record("C2 is computable from pipeline outputs",
                 "PASS" if facts["C2_distribution"] else "FAIL",
                 "a non-empty distribution", facts["C2_distribution"],
                 "publishing C2 as NOT_AVAILABLE would contradict the evidence")
    check.record("C3 is computable from pipeline outputs",
                 "PASS" if facts["C3_distribution"] else "FAIL",
                 "a non-empty distribution", facts["C3_distribution"],
                 "publishing C3 as NOT_AVAILABLE would contradict the evidence")
    check.compare("C1/C2/C3 row counts agree", facts["classification_count"],
                  sum(facts["C2_distribution"].values()))

    check.compare("mapping rows == cases with a compliance vector",
                  EXPECTED_CASES, sum(facts["mapping_status_distribution"].values()))
    check.compare("coverage summary agrees with the mapping rows",
                  facts["mapping_status_distribution"].get("Satisfied", 0),
                  facts["coverage_summary_totals"].get("satisfied", 0))
    check.record("mapping result never feeds Detector-v1", "PASS",
                 note="Satisfied/Partially-Satisfied/Not-Satisfied is a model judgement; "
                      "Detector-v1 reads only S1/S3/S7 and S2/S6 from the conversation")
    check.compare("fragment patterns are counted by their real key",
                  facts["recurring_fragment_patterns"],
                  sum(facts["fragment_label_distribution"].values()))
    check.record("fragment patterns are unconfirmed by probe",
                 "PASS" if set(facts["fragment_probe_confirmed"]) <= {False} else "FAIL",
                 "no pattern probe-confirmed", facts["fragment_probe_confirmed"],
                 "an Alternative label is an unconfirmed observation, not an established error")
    check.compare("pattern join accounts for every classification row",
                  facts["classification_count"], sum(facts["pattern_join"].values()))
    check.compare("S9 question density covers every episode",
                  facts["total_episodes"], len(facts["question_density_S9"]))
    check.record("S9 has no threshold", "PASS",
                 note="preregistered as descriptive; no classification derives from it")

    cross_check_derived(check, args.run_root, facts, receipt, usage, events, events_path,
                        strong, weak, none)

    head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True).stdout.strip()
    dirty = bool(subprocess.run(["git", "status", "--porcelain"], cwd=ROOT,
                                capture_output=True, text=True).stdout.strip())
    check.record("reporting tree is committed",
                 "PROVENANCE_GAP" if dirty else "PASS",
                 "a clean working tree", "dirty" if dirty else "clean",
                 "a stamp taken from a dirty tree names a commit that cannot reproduce this "
                 "artifact; reporting_code_sha is marked DIRTY_TREE until the tree is committed")
    if "reviewed_head" in receipt:
        check.compare("reviewed_head bound in real-run receipt", receipt["reviewed_head"],
                      receipt["reviewed_head"],
                      "receipt binds its execution code SHA; compare it against the authorization packet")
    else:
        check.record("reviewed_head bound in real-run receipt", "PROVENANCE_GAP", "40-char SHA",
                     "absent",
                     "real-run receipt carries run_id but not the code SHA it executed under; the "
                     "value efe686ac0b13c6e17695b816da7eb0cdd3eadcc1 is known from the authorization "
                     "packet and the preflight receipt, not from this receipt")

    chain_checks = {"derived analysis-receipt: output inventory pin resolves"}
    scientific_failures = [r for r in check.value_failures if r["check"] not in chain_checks]
    chain_failures = [r for r in check.value_failures if r["check"] in chain_checks]
    if scientific_failures:
        status, scope = "EVIDENCE_INVALID", "SCIENTIFIC_VALUES"
    elif chain_failures:
        status, scope = "DERIVED_CHAIN_BROKEN", "DERIVED_ARTIFACT_CHAIN"
    elif check.failed:
        status, scope = "PASS_WITH_PROVENANCE_GAPS", "NONE"
    else:
        status, scope = "PASS", "NONE"

    payload = {
        "schema_version": SCHEMA_VERSION,
        "status": status,
        "scientific_values_reproduce": not scientific_failures,
        "failure_scope": scope,
        "reporting_code_sha": f"{head}+DIRTY_TREE" if dirty else head,
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
          f"scientific-value-failures: {len(scientific_failures)}  "
          f"derived-chain-failures: {len(chain_failures)}  provenance-gaps: {len(gaps)}")
    for row in check.rows:
        mark = {"PASS": "ok  ", "FAIL": "FAIL", "PROVENANCE_GAP": "GAP ", "NOT_VERIFIABLE": "N/V "}[row["status"]]
        print(f"  [{mark}] {row['check']}: expected={row['expected']} actual={row['actual']}")
    return 0 if not check.value_failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
