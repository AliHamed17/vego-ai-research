"""One machine-readable reconciliation row per run, derived from what the head can prove.

Execution status is never taken from a commit message, a local report or a receipt that only
exists on one machine. A run is `EXECUTED` here only when the live pull request already
establishes it; otherwise it is `PREREGISTERED_NOT_EXECUTED_OR_UNVERIFIED`, whatever a local
artefact says. A private receipt is evidence to its owner and to nobody else.

Two further rules are enforced rather than described:

  * **Screening is not saving.** The share of episodes a rule declines to select is reported as
    `UNVALIDATED_SCREENING_FRACTION` and carries, in every row, the sentence denying that it shows
    reduced human workload, retained useful cases, correctness, benefit or safety.
  * **"Match" always names its level.** Three-class agreement and binary review-selection
    agreement are different questions with different answers, and a row states both or neither.

Cost is `EXACT` only when reserved and completed calls reconcile. Otherwise it is a `LOWER_BOUND`
with the reason, because an unreconciled counter means at least one reserved call is unaccounted
for and may still have reached the provider.

Runs are never pooled: there is no total row, and adding one would describe a run nobody executed.

No provider is contacted. Missing evidence yields `NOT_AVAILABLE`, never a reconstructed value.
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
BINARY_RULE = "selected for review iff class is STRONG_ALERT or WEAK_ALERT; NO_ALERT is not selected"

ARCHIVAL = "ARCHIVAL / RETROSPECTIVE DESCRIPTIVE EVIDENCE"
FIXTURE = "ENGINEERING-ONLY FIXTURE"
UNVERIFIED = "PREREGISTERED_NOT_EXECUTED_OR_UNVERIFIED"

SCREENING_DENIAL = (
    "A reduced number of episodes selected by a rule is not evidence of reduced human workload, "
    "retained useful cases, correctness, benefit, or safety without blinded human ratings and "
    "measured review time."
)

RUNS = [
    {
        "run_id": "REAL-efe686a-20260905T2303Z",
        "label": "ACCEPTED_HISTORICAL",
        "dir": "external_data/airtravel-pr38/v4-real-run/output",
        "evidence_class": ARCHIVAL,
        "execution_established_by_live_pr": True,
    },
    {
        "run_id": "FULLFRAME-01",
        "label": "STUDY1C_RUN1",
        "dir": "external_data/airtravel-pr38/full-frame-run/output",
        "evidence_class": ARCHIVAL,
        "execution_established_by_live_pr": True,
    },
    {
        "run_id": "FULLFRAME-02",
        "label": "STUDY1C_RUN2",
        "dir": "external_data/airtravel-pr38/full-frame-run-02/output",
        "evidence_class": ARCHIVAL,
        "execution_established_by_live_pr": True,
    },
    {
        "run_id": "HOTSPOT-01",
        "label": "HOTSPOT_BASELINE",
        "dir": "external_data/airtravel-pr38/hotspot/run/output",
        "evidence_class": UNVERIFIED,
        "execution_established_by_live_pr": False,
        "sample_class": "PILOT_INFORMED_POST_OUTCOME",
    },
]


def head_sha() -> str:
    return subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True, check=False
    ).stdout.strip()


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def tracked(relative: str) -> bool:
    return (
        subprocess.run(
            ["git", "ls-files", "--error-unmatch", relative],
            cwd=ROOT,
            capture_output=True,
            check=False,
        ).returncode
        == 0
    )


def cost_row(receipt: dict[str, Any]) -> dict[str, Any]:
    usage = receipt.get("usage", {})
    ledger = receipt.get("call_ledger") or {}
    recorded = usage.get("actual_cost_usd")
    reserved = usage.get("outbound_requests")
    completed = ledger.get("ledger_rows")
    if recorded is None:
        return {"status": NOT_AVAILABLE, "reason": "receipt carries no cost"}
    if completed is None:
        return {
            "status": "LOWER_BOUND",
            "usd": recorded,
            "reason": "this run predates the per-call ledger, so reserved and completed calls "
                      "cannot be reconciled",
        }
    if completed == reserved:
        return {"status": "EXACT", "usd": recorded,
                "reason": "reserved and completed calls reconcile"}
    return {
        "status": "LOWER_BOUND",
        "usd": recorded,
        "reason": f"{completed} completed calls against {reserved} reserved; at least one "
                  "reserved call is unaccounted for and may still have reached the provider",
    }


def episode_row(events_path: Path) -> dict[str, Any]:
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
        "detector_class_STRONG_ALERT": counts.get("STRONG_ALERT", 0),
        "detector_class_WEAK_ALERT": counts.get("WEAK_ALERT", 0),
        "detector_class_NO_ALERT": counts.get("NO_ALERT", 0),
        "binary_review_decision_rule": BINARY_RULE,
        "episodes_selected_for_review": selected,
        "binary_review_selection_rate": round(selected / len(complete), 4) if complete else None,
        "unvalidated_screening_fraction": (
            round(1 - selected / len(complete), 4) if complete else None
        ),
        "unvalidated_screening_fraction_meaning": SCREENING_DENIAL,
    }


def permitted_claims(row: dict[str, Any]) -> list[str]:
    if row["execution_status"] == UNVERIFIED:
        return [
            "that the study is preregistered and its manifest is frozen",
            "that no execution is verifiable from this head",
        ]
    return [
        "the per-run counts in this row, on this run's own denominator",
        "which detector classes occurred and how often, in this run",
        "the binary review-selection rate and the UNVALIDATED_SCREENING_FRACTION, with the "
        "denial sentence attached",
        "the cost, at the exactness stated in this row",
    ]


def reconcile(spec: dict[str, Any], head: str) -> dict[str, Any]:
    directory = ROOT / spec["dir"]
    events = directory / "qa_events.jsonl"
    receipt_path = directory / "run-receipt.json"
    receipt_relative = spec["dir"] + "/run-receipt.json"
    mounted = events.is_file() and receipt_path.is_file()
    established = spec["execution_established_by_live_pr"]

    row: dict[str, Any] = {
        "run_id": spec["run_id"],
        "label": spec["label"],
        "head_sha": head,
        "evidence_class": spec["evidence_class"],
        "sample_class": spec.get("sample_class", "FROZEN_FRAME_OR_FULL_POPULATION"),
        "execution_status": "EXECUTED" if established else UNVERIFIED,
        "private_evidence_mounted_locally": mounted,
        "receipt_tracked_in_head": tracked(receipt_relative),
        "independently_verifiable_from_this_head": tracked(receipt_relative),
    }
    if not established:
        row["why_unverified"] = (
            "the live pull request does not establish execution, no receipt is tracked in this "
            "head, and a local report or private receipt does not prove execution to a reader"
        )
    if not mounted:
        row.update({"status": NOT_AVAILABLE,
                    "reason": "private receipt or event log is not mounted in this worktree",
                    "fail_closed": "no empirical value is reconstructed or inferred"})
        row["permitted_claims"] = permitted_claims(row)
        return row

    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    usage = receipt.get("usage", {})
    ledger = receipt.get("call_ledger") or {}
    if established:
        row.update(
            {
                "status": receipt.get("status", NOT_AVAILABLE),
                "cases": receipt.get("N", NOT_AVAILABLE),
                **episode_row(events),
                "call_cap": usage.get("outbound_request_cap", NOT_AVAILABLE),
                "calls_reserved": usage.get("outbound_requests", NOT_AVAILABLE),
                "calls_completed": ledger.get("ledger_rows", NOT_AVAILABLE),
                "cost": cost_row(receipt),
                "receipt_binds_event_log_hash": bool(receipt.get("event_log_sha256")),
                "receipt_hash_status": (
                    "MATCHES_LOCAL_EVENT_LOG"
                    if receipt.get("event_log_sha256") == digest(events)
                    else "MISMATCH"
                ),
            }
        )
    else:
        row.update(
            {
                "status": UNVERIFIED,
                "cases": NOT_AVAILABLE,
                "complete_episodes": NOT_AVAILABLE,
                "incomplete_technical_episodes": NOT_AVAILABLE,
                "detector_class_STRONG_ALERT": NOT_AVAILABLE,
                "detector_class_WEAK_ALERT": NOT_AVAILABLE,
                "detector_class_NO_ALERT": NOT_AVAILABLE,
                "call_cap": NOT_AVAILABLE,
                "calls_reserved": NOT_AVAILABLE,
                "calls_completed": NOT_AVAILABLE,
                "cost": {"status": NOT_AVAILABLE,
                         "reason": "no verifiable execution, so no cost may be reported"},
                "receipt_hash_status": "PRESENT_LOCALLY_BUT_NOT_VERIFIABLE_FROM_HEAD",
                "withheld_values_note": (
                    "counts exist in a local artefact and are deliberately not published here; "
                    "publishing them would represent an unverified run as an executed one"
                ),
            }
        )
    row["permitted_claims"] = permitted_claims(row)
    return row


def fixtures_row(head: str) -> dict[str, Any]:
    return {
        "run_id": "OFFLINE_FIXTURES",
        "label": "ENGINEERING_FIXTURES",
        "head_sha": head,
        "evidence_class": FIXTURE,
        "sample_class": "SYNTHETIC_DETERMINISTIC_INPUT",
        "execution_status": "OFFLINE_NO_PROVIDER_CALLS",
        "private_evidence_mounted_locally": True,
        "receipt_tracked_in_head": False,
        "independently_verifiable_from_this_head": False,
        "status": "TECHNICAL_SUCCESS",
        "cases": NOT_AVAILABLE,
        "complete_episodes": NOT_AVAILABLE,
        "incomplete_technical_episodes": NOT_AVAILABLE,
        "detector_class_STRONG_ALERT": NOT_AVAILABLE,
        "detector_class_WEAK_ALERT": NOT_AVAILABLE,
        "detector_class_NO_ALERT": NOT_AVAILABLE,
        "call_cap": NOT_AVAILABLE,
        "calls_reserved": 0,
        "calls_completed": 0,
        "cost": {"status": "EXACT", "usd": 0.0, "reason": "no provider call was made"},
        "receipt_hash_status": NOT_AVAILABLE,
        "permitted_claims": [
            "that the frozen rule reaches every class and every isolable branch on synthetic input",
            "that the fixture contacted no provider",
        ],
        "prohibited": [
            "any scientific reading; fixture outputs share no denominator with any run",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=None)
    args = parser.parse_args()

    head = head_sha()
    rows = [reconcile(spec, head) for spec in RUNS] + [fixtures_row(head)]
    report = {
        "schema_version": "study1c-reconciliation-v2",
        "head_sha": head,
        "pooling": "PROHIBITED - no total row; the runs differ in configuration",
        "binary_review_decision_rule": BINARY_RULE,
        "agreement_levels": {
            "three_class": "compares STRONG_ALERT / WEAK_ALERT / NO_ALERT labels",
            "binary_review": "compares only the selected-for-review decision",
            "why_both": (
                "a rule that emits STRONG for everything differs from Detector-v1 at the "
                "three-class level whenever Detector-v1 emits any WEAK, yet is identical at the "
                "binary-review level whenever Detector-v1 selects every episode for review"
            ),
            "never": "the phrase 'baseline matches exactly' may not be used without its level",
        },
        "unvalidated_screening_fraction_meaning": SCREENING_DENIAL,
        "verdict": "DESCRIPTIVE_RULE_BEHAVIOUR_ONLY / NOT_READY_FOR_SCIENTIFIC_CONCLUSION",
        "verdict_basis": (
            "no blinded human ratings and no measured review time exist, so no claim about "
            "accuracy, benefit, workload, retention, causality, generalization or hotspot "
            "validity is computable. What remains is rule behaviour on recorded inputs"
        ),
        "strongest_defensible_finding": (
            "Under the recorded rule, alert classification is highly sensitive to Q&A episode "
            "length; long episodes tend to saturate toward STRONG_ALERT. This is a rule-behaviour "
            "finding, not validation of real human-intervention need."
        ),
        "prohibited_claims": [
            "accuracy, precision, recall, F1",
            "human benefit or workload saving",
            "retention of useful cases",
            "causality", "generalization", "hotspot validity", "VEGO-AI superiority",
            "that Detector-v1 demonstrably prioritizes",
            "that the only remaining blocker is two raters",
            "PROSPECTIVE EMPIRICAL EVIDENCE for any run in this package",
        ],
        "runs": rows,
    }
    text = json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(text, encoding="utf-8")
    print(text[:1200])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
