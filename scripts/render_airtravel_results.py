"""Receipt-bound descriptive rendering. Frozen Detector-v1 is the only signal source.
CLI accepts no findings/conclusions. All eight outputs are deterministic and hashed.
Execution on experimental evidence needs separate human authorization.
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

import airtravel_preflight_contract as contract  # noqa: E402
from extract_qa_escalation_features import extract_live_corpus  # noqa: E402

DEFAULT_TEMPLATE = (
    REPO_ROOT
    / "docs"
    / "research"
    / "phd-proposal"
    / "2026-09-05-airtravel-preliminary-results-template-he.md"
)
TOKEN_RE = re.compile(r"\{\{[A-Z0-9_]+\}\}")
FORBIDDEN_REPORT_TERMS = ("accuracy", "precision", "recall", "F1")


def _distribution(counter: Counter[Any]) -> str:
    if not counter:
        return "אין נתונים (0 פרקים)"
    return "; ".join(f"{key}: {count}" for key, count in sorted(counter.items(), key=str))


def build_report_fields(corpus: dict[str, Any], receipt: dict) -> dict[str, str]:
    episodes = corpus["episodes"]
    complete = [e for e in episodes if e["scientific_complete"]]
    detector = {row["episode_id"]: row for row in corpus["detector_v1"]}
    totals = canonical_totals(corpus)
    classifications = Counter(detector[e["episode_id"]]["classification"] for e in complete)
    terminations = Counter(e["termination_reason"] or "UNTERMINATED" for e in episodes)
    termination_rows = (
        "\n".join(f"| `{state}` | {count} |" for state, count in sorted(terminations.items()))
        or "| — | 0 |"
    )
    route_rows = totals["route_rows"]
    rounds = Counter(e["round_count"] for e in complete)
    confidence = Counter(
        row.get("answer_confidence") for e in complete for row in e.get("answers", [])
    )
    evidence = Counter(
        "present"
        if (ref := row.get("answer_evidence_ref")) is not None and ref.get("length", 0) > 0
        else "missing"
        for e in complete
        for row in e.get("answers", [])
    )
    zero_qa = zero_qa_status(corpus["events"], receipt)
    return {
        "RUN_SHA": receipt["commit"],
        "MODEL": receipt["model"],
        "RUN_DATE": receipt.get("run_date", "NOT_RECORDED"),
        "SETTING_ID": receipt["setting_id"],
        "CORPUS_ID": receipt["corpus_id"],
        "N_CASES": str(receipt["N"]),
        "TOTAL_CALLS": str(receipt["instrumented_fake_call_count"]),
        "RUNTIME_SECONDS": str(receipt["elapsed_seconds"]),
        "MEASURED_COST": "TO BE MEASURED",
        "TECHNICAL_STATUS": receipt["status"],
        "N_TOTAL_EPISODES": str(len(episodes)),
        "N_COMPLETE_EPISODES": str(len(complete)),
        "N_INCOMPLETE_TECHNICAL": str(corpus["summary"]["excluded_incomplete_technical"]),
        "ZERO_QA_STATUS": zero_qa,
        "QUESTIONS_TOTAL": str(corpus["summary"]["questions"]),
        "ANSWERS_TOTAL": str(corpus["summary"]["answers"]),
        "ROUND_DISTRIBUTION": _distribution(rounds),
        "CONFIDENCE_DISTRIBUTION": _distribution(confidence),
        "EVIDENCE_DISTRIBUTION": _distribution(evidence),
        "DENOMINATOR": str(len(complete)),
        "N_S1": str(totals["signals"]["S1"]),
        "N_S2": str(totals["signals"]["S2"]),
        "N_S3": str(totals["signals"]["S3"]),
        "N_S6": str(totals["signals"]["S6"]),
        "N_S7": str(totals["signals"]["S7"]),
        "C1_STATUS": "לא זמין מיומן האירועים (mapping_certainty אינו אירוע Q&A); תיאור בלבד",
        "S5_STATUS": "לא זמין (השוואת נוסח מנורמלת אינה נשמרת); מדווח כלא-שמיש, לא מושמט",
        "S8_STATUS": _distribution(
            Counter("follow_up" if e["follow_up_present"] else "no_follow_up" for e in complete)
        ),
        "S9_STATUS": _distribution(Counter(e["question_count"] for e in complete)) + " (ללא סף)",
        "N_STRONG_ALERT": str(classifications.get("STRONG_ALERT", 0)),
        "N_WEAK_ALERT": str(classifications.get("WEAK_ALERT", 0)),
        "N_NO_ALERT": str(classifications.get("NO_ALERT", 0)),
        "TERMINATION_TABLE": termination_rows,
        "ROUTES_TABLE": route_rows,
        "DESCRIPTIVE_FINDINGS": f"נרשמו {len(episodes)} פרקי תקשורת; {len(complete)} מהם מלאים טכנית. זהו תיאור הריצה המאומתת בלבד.",
        "LIMITED_CONCLUSION": "הספירות מתארות תקשורת בלבד; הן אינן מוכיחות צורך בהתערבות או תועלת אנושית.",
        "NEXT_STEP": "סקירה אנושית של הראיות; כל הרצה נוספת דורשת הרשאה נפרדת.",
    }


def render_report(template_text: str, fields: dict[str, str]) -> str:
    rendered = template_text
    for token, value in fields.items():
        rendered = rendered.replace("{{" + token + "}}", str(value))
    residual = TOKEN_RE.findall(rendered)
    if residual:
        raise ValueError(f"unfilled template tokens remain: {sorted(set(residual))}")
    lowered = rendered.lower()
    for term in FORBIDDEN_REPORT_TERMS:
        if term.lower() in lowered:
            raise ValueError(f"forbidden claim term in rendered report: {term}")
    return rendered


def zero_qa_status(events, receipt):
    if events:
        return "NOT_ZERO_QA"
    required = {
        "status": "TECHNICAL_SUCCESS",
        "orchestrator_completed": True,
        "processed_case_ids": ["01", "02", "03", "04"],
        "expected_outputs_exist": True,
        "technical_exception": None,
        "timeout": False,
        "prompt_parity": True,
        "answer_parity": True,
        "state_parity": True,
        "output_parity": True,
        "event_recorder_completed": True,
        "event_count": 0,
        "question_count": 0,
    }
    return (
        "VALID_ZERO_QA_RUN"
        if all(k in receipt and receipt[k] == v for k, v in required.items())
        else "ZERO_EVENTS_TECHNICAL_FAILURE"
    )


def canonical_totals(corpus):
    signals = dict.fromkeys(("S1", "S2", "S3", "S6", "S7"), 0)
    for row in corpus["detector_v1"]:
        if row["classification"] == "EXCLUDED":
            continue
        for fired in row["all_signals_fired"]:
            key = fired.split("_", 1)[0]
            if key in signals:
                signals[key] += 1
    from airtravel_local_observer import route_metrics

    metrics = route_metrics(corpus["events"])
    return {
        "signals": signals,
        **metrics,
        "route_rows": "\n".join(
            f"| `{r['source_agent']} → {r['target_agent']}` | {r['question_count']} |"
            for r in metrics["routes"]
        )
        or "| — | 0 |",
    }


def verify_run_receipt(events_path, receipt_path, receipt_hash, commit, model):
    for path in (events_path, receipt_path):
        contract.no_links(path)
    if contract.digest(receipt_path) != receipt_hash:
        raise ValueError("run receipt hash mismatch")
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    import math

    elapsed = receipt.get("elapsed_seconds")
    if type(elapsed) not in (int, float) or not math.isfinite(elapsed) or elapsed < 0:
        raise ValueError("elapsed time must be a measured nonnegative number")
    if "run_date" in receipt and not re.fullmatch(r"\d{4}-\d{2}-\d{2}", receipt["run_date"]):
        raise ValueError("unstructured run date refused")
    from prepare_airtravel_protected_fake_preflight import FROZEN

    expected = {
        "schema_version": "airtravel-technical-receipt-v1",
        "setting_id": contract.SETTING,
        "corpus_id": contract.CORPUS,
        "N": 4,
        "commit": commit,
        "model": model,
        "runtime_archive_sha256": FROZEN["runtime_archive_sha256"],
        "status": "TECHNICAL_SUCCESS",
        "event_log_sha256": contract.digest(events_path),
    }
    if not re.fullmatch(r"[a-f0-9]{40}", commit) or not re.fullmatch(
        r"[A-Za-z0-9_.:/-]{1,128}", model
    ):
        raise ValueError("invalid run identity")
    if any(receipt.get(k) != v for k, v in expected.items()):
        raise ValueError("run receipt binding mismatch")
    checks = {
        "orchestrator_completed": True,
        "expected_outputs_exist": True,
        "event_recorder_completed": True,
        "prompt_parity": True,
        "answer_parity": True,
        "state_parity": True,
        "output_parity": True,
        "timeout": False,
        "technical_exception": None,
        "external_provider_call_count": 0,
        "network_attempt_count": 0,
    }
    if any(k not in receipt or receipt[k] != v for k, v in checks.items()):
        raise ValueError("technical proof incomplete")
    if receipt.get("processed_case_ids") != ["01", "02", "03", "04"]:
        raise ValueError("case completion not proved")
    files = receipt.get("files", {})
    if not files:
        raise ValueError("output hashes absent")
    for name, sha in files.items():
        target = receipt_path.parent / name
        contract.no_links(target)
        if (
            not target.resolve().is_relative_to(receipt_path.parent.resolve())
            or contract.digest(target) != sha
        ):
            raise ValueError("protected output hash mismatch")
    from airtravel_preflight_execution import SCIENTIFIC_FILES

    for side in ("baseline", "instrumented"):
        if not {side + "/" + name for name in SCIENTIFIC_FILES} <= files.keys():
            raise ValueError("expected outputs missing")
        state = json.loads(
            (receipt_path.parent / side / "pipeline_state.json").read_text(encoding="utf-8")
        )
        if set(state.get("compliance_vectors", {})) != {"01", "02", "03", "04"} or set(
            state.get("uncovered_fragments", {})
        ) != {"01", "02", "03", "04"}:
            raise ValueError("actual state does not prove four cases")
    events = [
        json.loads(line)
        for line in events_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    from airtravel_local_observer import validate_final_stream

    validate_final_stream(events)
    if receipt.get("event_count") != len(events) or receipt.get("question_count") != sum(
        e["event_type"] == "QUESTION_EMITTED" for e in events
    ):
        raise ValueError("event counts disagree")
    contract.check_counts(
        receipt["baseline_fake_call_count"], receipt["instrumented_fake_call_count"]
    )
    return receipt


def write_outputs(corpus, report, output_root, receipt, receipt_hash):
    contract.no_links(output_root)
    if output_root.exists() and any(output_root.iterdir()):
        raise ValueError("report output must be empty")
    output_root.mkdir(parents=True, exist_ok=True)
    totals = canonical_totals(corpus)

    def write_json(name, value):
        with (output_root / name).open("xb") as handle:
            handle.write(contract.canonical(value))

    def write_csv(name, rows, fields):
        with (output_root / name).open("x", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(
                handle, fieldnames=fields, extrasaction="ignore", lineterminator="\n"
            )
            writer.writeheader()
            for row in rows:
                writer.writerow(
                    {
                        k: json.dumps(v, ensure_ascii=False, sort_keys=True)
                        if isinstance(v, (dict, list))
                        else v
                        for k, v in row.items()
                    }
                )

    write_json(
        "validated-run-receipt.json",
        {
            "verified_run_receipt_sha256": receipt_hash,
            "commit": receipt["commit"],
            "event_log_sha256": receipt["event_log_sha256"],
            "setting_id": receipt["setting_id"],
            "corpus_id": receipt["corpus_id"],
            "N": receipt["N"],
            "model": receipt["model"],
            "status": receipt["status"],
        },
    )
    write_json("airtravel-results-machine.json", {**corpus, "descriptive_counts": totals})
    write_csv(
        "airtravel-episodes.csv",
        corpus["episodes"],
        [
            "episode_id",
            "run_id",
            "question_count",
            "answer_count",
            "round_count",
            "termination_reason",
            "scientific_complete",
            "exclusion_reason",
        ],
    )
    write_csv(
        "airtravel-detector.csv",
        corpus["detector_v1"],
        [
            "episode_id",
            "classification",
            "candidate_alert",
            "all_signals_fired",
            "reason_codes",
            "exclusion_reason",
        ],
    )
    write_csv(
        "airtravel-signals.csv",
        [{"signal": k, "episode_count": v} for k, v in totals["signals"].items()],
        ["signal", "episode_count"],
    )
    write_csv(
        "airtravel-routes.csv", totals["routes"], ["source_agent", "target_agent", "question_count"]
    )
    terms = Counter(e["termination_reason"] for e in corpus["episodes"])
    write_csv(
        "airtravel-terminations.csv",
        [{"termination": k, "episode_count": v} for k, v in sorted(terms.items())],
        ["termination", "episode_count"],
    )
    with (output_root / "airtravel-preliminary-results-he.md").open(
        "x", encoding="utf-8"
    ) as handle:
        handle.write(report)
    hashes = {p.name: contract.digest(p) for p in sorted(output_root.iterdir())}
    write_json("output-hashes.json", hashes)
    return hashes


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--events", type=Path, required=True)
    parser.add_argument("--run-receipt", type=Path, required=True)
    parser.add_argument("--run-receipt-sha256", required=True)
    parser.add_argument("--run-sha", required=True)
    parser.add_argument("--model", required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    args = parser.parse_args()
    receipt = verify_run_receipt(
        args.events, args.run_receipt, args.run_receipt_sha256, args.run_sha, args.model
    )
    corpus = extract_live_corpus(args.events)
    fields = build_report_fields(corpus, receipt)
    report = render_report(DEFAULT_TEMPLATE.read_text(encoding="utf-8"), fields)
    hashes = write_outputs(corpus, report, args.output_root, receipt, args.run_receipt_sha256)
    print(
        json.dumps(
            {
                "output_hashes": hashes,
                "manifest_sha256": contract.digest(args.output_root / "output-hashes.json"),
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
