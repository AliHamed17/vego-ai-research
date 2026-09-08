"""One machine-generated reconciliation table per run, and the contradictions it resolves.

The package accumulated three defects that this module exists to make impossible to repeat:

  1. **"Match" was ambiguous.** A baseline can differ from Detector-v1 on the three-class label and
     still be *identical* on the send-for-review decision. Saying "no baseline matches" without
     naming the level is false at one of the two levels. Both are reported here, always together.
  2. **A screening fraction was called workload reduction.** Selecting fewer episodes is not saved
     human work. The quantity is reported as `UNVALIDATED_SCREENING_FRACTION` and carries its own
     denial of benefit, retention, correctness and safety meaning.
  3. **Run status drifted from what the repository can prove.** A run whose receipt is not tracked
     is not independently verifiable, whatever a commit message says. Status is derived from
     tracked evidence, never asserted.

Cost is reported exactly only when the per-call ledger reconciles with the budget guard's own
counter. Otherwise it is a lower bound with the reason attached, because an unreconciled counter
means at least one reserved call is unaccounted for.

Runs are never pooled. There is no total row, and adding one would be a category error: the runs
differ in case count, configuration and evidence class.

No provider is contacted. If private evidence is absent the module fails closed and reports
`NOT_AVAILABLE` rather than reconstructing any empirical value.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from airtravel_detector_analysis import project_episodes  # noqa: E402
from extract_qa_escalation_features import detect_detector_v1  # noqa: E402

NOT_AVAILABLE = "NOT_AVAILABLE"
ALERT_CLASSES = {"STRONG_ALERT", "WEAK_ALERT"}
BINARY_RULE = "send for review iff class is STRONG_ALERT or WEAK_ALERT; NO_ALERT is not sent"

PROSPECTIVE = "PROSPECTIVE EMPIRICAL EVIDENCE"
ARCHIVAL = "ARCHIVAL / RETROSPECTIVE DESCRIPTIVE EVIDENCE"
FIXTURE = "ENGINEERING-ONLY FIXTURE"

RUNS = [
    {
        "run_id": "REAL-efe686a-20260905T2303Z",
        "label": "ACCEPTED_HISTORICAL",
        "dir": "external_data/airtravel-pr38/v4-real-run/output",
        "evidence_class": ARCHIVAL,
        "study": "accepted historical AirTravel run",
    },
    {
        "run_id": "FULLFRAME-01",
        "label": "STUDY1C_RUN1",
        "dir": "external_data/airtravel-pr38/full-frame-run/output",
        "evidence_class": ARCHIVAL,
        "study": "Study 1C, full eligible frame, run 1",
    },
    {
        "run_id": "FULLFRAME-02",
        "label": "STUDY1C_RUN2",
        "dir": "external_data/airtravel-pr38/full-frame-run-02/output",
        "evidence_class": ARCHIVAL,
        "study": "Study 1C, full eligible frame, run 2, stopped at cap and partial",
    },
    {
        "run_id": "HOTSPOT-01",
        "label": "HOTSPOT_PILOT",
        "dir": "external_data/airtravel-pr38/hotspot/run/output",
        "evidence_class": ARCHIVAL,
        "study": "human-review hotspot pilot, sample seed chosen after full-frame outcomes",
        "sample_class": "PILOT_INFORMED_POST_OUTCOME",
    },
]


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def tracked(relative: str) -> bool:
    result = subprocess.run(
        ["git", "ls-files", "--error-unmatch", relative],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    return result.returncode == 0


def cost_report(receipt: dict[str, Any]) -> dict[str, Any]:
    """Exact only when the ledger reconciles with the guard; otherwise a lower bound."""
    usage = receipt.get("usage", {})
    ledger = receipt.get("call_ledger") or {}
    recorded = usage.get("actual_cost_usd")
    guard_calls = usage.get("outbound_requests")
    ledger_rows = ledger.get("ledger_rows")
    if recorded is None:
        return {"status": NOT_AVAILABLE, "reason": "receipt carries no cost"}
    if ledger_rows is None:
        return {
            "status": "LOWER_BOUND",
            "usd": recorded,
            "reason": "this run predates the per-call ledger, so cost cannot be reconciled",
        }
    if ledger_rows == guard_calls:
        return {"status": "EXACT", "usd": recorded, "reason": "ledger rows equal guard reservations"}
    return {
        "status": "LOWER_BOUND",
        "usd": recorded,
        "reason": (
            f"ledger holds {ledger_rows} completed calls against {guard_calls} guard "
            "reservations, so at least one reserved call is unaccounted for"
        ),
    }


def call_report(receipt: dict[str, Any]) -> dict[str, Any]:
    usage = receipt.get("usage", {})
    return {
        "reserved_call_cap": usage.get("outbound_request_cap", NOT_AVAILABLE),
        "wrapper_calls_counted_by_guard": usage.get("outbound_requests", NOT_AVAILABLE),
        "completed_calls_in_ledger": (receipt.get("call_ledger") or {}).get(
            "ledger_rows", NOT_AVAILABLE
        ),
        "physical_request_caveat": (
            "the guard counted SDK wrapper calls, not physical HTTP attempts; with SDK-level "
            "retries enabled a wrapper call could issue more than one physical request, so the "
            "cap bounded wrapper calls only"
        ),
    }


def episode_report(events_path: Path) -> dict[str, Any]:
    rows = [
        json.loads(line)
        for line in events_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    episodes = project_episodes(rows)
    complete = [ep for ep in episodes if ep.get("scientific_complete")]
    labels = [detect_detector_v1(ep)["classification"] for ep in complete]
    counts = Counter(labels)
    selected = sum(1 for label in labels if label in ALERT_CLASSES)
    return {
        "complete_episodes": len(complete),
        "incomplete_technical_episodes": len(episodes) - len(complete),
        "STRONG_ALERT": counts.get("STRONG_ALERT", 0),
        "WEAK_ALERT": counts.get("WEAK_ALERT", 0),
        "NO_ALERT": counts.get("NO_ALERT", 0),
        "binary_review_decision_rule": BINARY_RULE,
        "episodes_selected_for_review": selected,
        "unvalidated_screening_fraction": (
            round(1 - selected / len(complete), 4) if complete else None
        ),
        "screening_fraction_meaning": (
            "the share of complete episodes this rule does NOT send for review. It is not saved "
            "human work, not a benefit, not retention, not correctness and not safety evidence"
        ),
    }


def reconcile_run(spec: dict[str, Any]) -> dict[str, Any]:
    directory = ROOT / spec["dir"]
    events = directory / "qa_events.jsonl"
    receipt_path = directory / "run-receipt.json"
    row: dict[str, Any] = {
        "run_id": spec["run_id"],
        "label": spec["label"],
        "study": spec["study"],
        "evidence_class": spec["evidence_class"],
        "sample_class": spec.get("sample_class", "PREREGISTERED_FRAME_OR_FULL_POPULATION"),
        "private_evidence_mounted": events.is_file() and receipt_path.is_file(),
        "receipt_tracked_in_repository": tracked(spec["dir"] + "/run-receipt.json"),
    }
    if not row["private_evidence_mounted"]:
        row["status"] = NOT_AVAILABLE
        row["reason"] = "private receipt or event log is not mounted in this worktree"
        row["fail_closed"] = "no empirical value is reconstructed or inferred"
        return row

    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    row.update(
        {
            "status": receipt.get("status", NOT_AVAILABLE),
            "selected_cases": receipt.get("N", NOT_AVAILABLE),
            **episode_report(events),
            **call_report(receipt),
            "cost": cost_report(receipt),
            "event_log_sha256": digest(events),
            "receipt_binds_event_log_hash": bool(receipt.get("event_log_sha256")),
            "event_log_hash_matches_receipt": receipt.get("event_log_sha256") == digest(events),
            "independently_verifiable_from_repository": False,
            "verifiability_note": (
                "the receipt and event log are git-ignored private evidence. Their hashes can be "
                "recomputed locally but cannot be checked by a reader who has only the repository"
            ),
        }
    )
    return row


def hotspot_status() -> dict[str, Any]:
    """Status is derived from tracked evidence, never asserted from a commit message."""
    manifest_path = ROOT / "docs/research/phd-proposal/study1-hotspot-manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    receipt_relative = "external_data/airtravel-pr38/hotspot/run/output/run-receipt.json"
    return {
        "manifest_declared_status": manifest["status"],
        "receipt_tracked_in_repository": tracked(receipt_relative),
        "repository_verifiable_status": (
            "PREREGISTERED_NOT_EXECUTED"
            if not tracked(receipt_relative)
            else "EXECUTED_AND_VERIFIABLE"
        ),
        "resolution": (
            "the manifest still declares PREREGISTERED_NOT_EXECUTED and no receipt is tracked, so "
            "the status a reader can verify from this repository is preregistered-and-not-executed. "
            "A local private receipt exists, but a private artefact cannot upgrade a public status"
        ),
        "sample_class": "PILOT_INFORMED_POST_OUTCOME",
        "sample_class_reason": (
            "the draw seed was fixed after the full-frame run outcomes were already known to the "
            "author. The draw is mechanically reproducible, but there is no pre-commitment record "
            "predating those outcomes, so the sample may not be described as prospective"
        ),
    }


def no_alert_reconciliation(rows: list[dict[str, Any]]) -> dict[str, Any]:
    scored = [r for r in rows if r.get("status") not in (NOT_AVAILABLE, None)]
    per_run = {r["run_id"]: r.get("NO_ALERT", NOT_AVAILABLE) for r in scored}
    earlier = [r for r in scored if r["label"] != "HOTSPOT_PILOT"]
    earlier_total = sum(r.get("NO_ALERT", 0) for r in earlier)
    hotspot = next((r for r in scored if r["label"] == "HOTSPOT_PILOT"), None)
    return {
        "no_alert_by_run": per_run,
        "claim_1": "no episode has ever been NO_ALERT",
        "claim_1_scope_that_makes_it_true": (
            "the accepted historical run and both Study 1C full-frame runs, taken together at the "
            f"time those documents were written: {earlier_total} NO_ALERT episodes"
        ),
        "claim_2": "a later hotspot pilot run recorded one NO_ALERT episode",
        "claim_2_status": (
            NOT_AVAILABLE
            if hotspot is None
            else f"{hotspot.get('NO_ALERT')} NO_ALERT in {hotspot.get('complete_episodes')} episodes"
        ),
        "contradiction": False,
        "resolution": (
            "the two claims do not contradict once each is scoped to its own runs. Claim 1 was "
            "true of the runs it described and must be written with that scope. Claim 2 concerns "
            "a different, later run whose sample is PILOT_INFORMED_POST_OUTCOME and whose receipt "
            "is not tracked, so it is not prospective evidence and is not poolable with claim 1"
        ),
        "required_wording": (
            "state the scope in the sentence: 'across the accepted run and the two full-frame "
            "runs, no complete episode was NO_ALERT' - never the unscoped 'never'"
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=None)
    args = parser.parse_args()

    rows = [reconcile_run(spec) for spec in RUNS]
    report = {
        "schema_version": "study1c-reconciliation-v1",
        "pooling": "PROHIBITED - there is no total row and adding one would be a category error",
        "binary_review_decision_rule": BINARY_RULE,
        "agreement_levels": {
            "three_class": "compares STRONG_ALERT / WEAK_ALERT / NO_ALERT labels",
            "binary_review": "compares only the send-for-review decision",
            "why_both": (
                "a rule that emits STRONG for everything differs from Detector-v1 at the "
                "three-class level whenever Detector-v1 emits any WEAK, yet is identical at the "
                "binary-review level whenever Detector-v1 sends every episode for review"
            ),
        },
        "evidence_class_separation": {
            "accepted_historical": ARCHIVAL,
            "study1c_run1": ARCHIVAL,
            "study1c_run2": ARCHIVAL,
            "offline_engineering_fixtures": FIXTURE,
            "hotspot_study": "PREREGISTERED; execution not verifiable from this repository",
        },
        "prohibited_terms": [
            "workload reduction",
            "hotspot detection",
            "prioritization effectiveness",
            "accuracy, precision, recall, F1",
            "human benefit",
            "causality",
            "generalization",
            "VEGO-AI superiority",
        ],
        "strongest_defensible_finding": (
            "Under the recorded rule, alert classification is highly sensitive to Q&A episode "
            "length; long episodes tend to saturate toward STRONG_ALERT. This is a rule-behaviour "
            "finding, not validation of real human-intervention need."
        ),
        "runs": rows,
        "hotspot_status": hotspot_status(),
        "no_alert_reconciliation": no_alert_reconciliation(rows),
    }
    text = json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(text, encoding="utf-8")
    print(text[:1500])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
