"""Freeze the human-review hotspot study: case selection, protocol, rubric and claim boundary.

The manifest is written **before** any provider call and before any output is observed. Its
purpose is to make every later choice checkable against a record that predates the results, so
that a reader can tell the difference between a finding and a decision made after seeing one.

Two properties matter most and are enforced here rather than promised in prose:

  * **Selection cannot depend on outcomes.** The sample is a deterministic draw from the full
    eligible frame using a seed fixed in this module. Anyone can recompute the draw from the seed
    and the pinned inventory; there is no place for a human choice to enter.
  * **The rubric predates the labels.** The rating question set, the response options, the
    adjudication rule and the metrics are all frozen here, before a single rater sees a card,
    so the rubric cannot be reshaped to fit whatever the labels turn out to be.

No provider is contacted and nothing is executed. This module only writes the freeze record.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import random
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
INVENTORY = ROOT / "docs/research/phd-proposal/text2uml-airtravel/airtravel-inventory.json"
HEX64 = re.compile(r"^[0-9a-fA-F]{64}$")

STUDY_ID = "STUDY1-HOTSPOT"
CORPUS_ID = "text2uml_airtravel_253b26dc"
PINNED_COMMIT = "253b26dc704d523209a5cba79686f8f7fab57d63"
ARCHIVE_SHA256 = "8cf82e2ab2d2ce3da9a7ec4165e760ae1e0d9af14468f5aa2a3883037d8da701"

SELECTION_SEED = 20260909
SELECTION_SIZE = 6

MODEL = "gpt-5.6-luna"
PRICE_IN_PER_M = 0.20
PRICE_OUT_PER_M = 1.20
RESERVE_INPUT_TOKENS = 8000
RESERVE_OUTPUT_TOKENS = 16384
MAX_QA_ROUNDS = 10
MAX_CONCURRENT_CASES = 2
REQUEST_TIMEOUT_SECONDS = 180
RUN_TIMEOUT_SECONDS = 10_800
MAX_RETRIES_PER_CALL = 3
CALL_CAP = 240
BUDGET_USD = 6.00
RUN_COUNT = 1

DETECTOR_FILES = (
    "scripts/extract_qa_escalation_features.py",
    "scripts/study1_signal_contract.py",
)

RATER_QUESTIONS = [
    {
        "id": "R1_WORTHY",
        "prompt": "Is this episode worthy of human review?",
        "options": ["Yes", "No", "Insufficient information"],
        "note": "'Insufficient information' is a distinct outcome and is never merged into 'No'.",
    },
    {
        "id": "R2_REASON",
        "prompt": "Why?",
        "options": [
            "Low confidence",
            "Missing evidence",
            "Repeated clarification",
            "Non-convergence",
            "Other",
        ],
        "note": "Multiple selections permitted; recorded verbatim.",
    },
    {
        "id": "R3_ACTION",
        "prompt": "What action would be appropriate?",
        "options": ["Verify", "Clarify", "Revise guideline", "No action"],
        "note": "Exactly one selection.",
    },
]

CARD_FIELDS_SHOWN = [
    "question text",
    "answer text",
    "evidence presence and length, not the evidence text",
    "directed route, as asking agent and answering agent",
    "round count and question count",
]
CARD_FIELDS_WITHHELD = [
    "the Detector-v1 classification and every signal name",
    "the per-answer confidence label",
    "the run identifier, the case identifier and the generating model name",
    "any other rater's responses",
]

FORBIDDEN_CLAIMS = [
    "that any Detector-v1 alert was correct",
    "accuracy, precision, recall or F1 as a confirmatory result",
    "effectiveness, human benefit or workload reduction without measured rater time",
    "causality or any ON/OFF advantage",
    "representativeness or generalization beyond this corpus and configuration",
    "that Detector-v1 creates or feeds a human queue",
    "that Agent-4's queue mechanism and Detector-v1 are the same mechanism",
    "pooling or averaging runs that differ in configuration",
    "that a larger episode count is stronger evidence unless it was frozen before outputs",
]


def digest_text(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def eligible_case_rows() -> list[dict[str, Any]]:
    payload = json.loads(INVENTORY.read_text(encoding="utf-8"))
    rows = [
        row
        for row in payload["files"]
        if row.get("classification") == "GENERATED_CANDIDATE_MODEL"
        and str(row.get("path", "")).startswith("result_one_")
        and int(row.get("bytes", 0) or 0) > 0
        and row.get("syntax_validation") == "WRAPPER_PRESENT"
        and HEX64.fullmatch(str(row.get("sha256", "")))
    ]
    return sorted(rows, key=lambda row: row["path"])


def draw_sample(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Deterministic seeded draw. Reproducible from the seed alone, so no choice can enter."""
    ordered = list(rows)
    random.Random(SELECTION_SEED).shuffle(ordered)
    chosen = sorted(ordered[:SELECTION_SIZE], key=lambda row: row["path"])
    if len(chosen) != SELECTION_SIZE:
        raise ValueError("eligible frame is smaller than the frozen sample size")
    return chosen


def pessimistic_reservation() -> dict[str, Any]:
    per_request = (
        RESERVE_INPUT_TOKENS * PRICE_IN_PER_M + RESERVE_OUTPUT_TOKENS * PRICE_OUT_PER_M
    ) / 1_000_000
    whole_study = CALL_CAP * per_request * RUN_COUNT
    return {
        "per_request_worst_case_usd": round(per_request, 10),
        "call_cap": CALL_CAP,
        "run_count": RUN_COUNT,
        "whole_study_reservation_usd": round(whole_study, 6),
        "ceiling_usd": BUDGET_USD,
        "headroom_usd": round(BUDGET_USD - whole_study, 6),
        "fits": whole_study <= BUDGET_USD,
        "basis": (
            "every permitted call, including retries and failed calls, is priced at the full "
            "worst-case reserve; this is a bound, not an extrapolation from a prior run"
        ),
    }


def build() -> dict[str, Any]:
    rows = eligible_case_rows()
    chosen = draw_sample(rows)
    head = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True, check=False
    ).stdout.strip()
    return {
        "schema_version": "study1-hotspot-manifest-v1",
        "study_id": STUDY_ID,
        "status": "PREREGISTERED_NOT_EXECUTED",
        "frozen_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "frozen_against_head": head,
        "primary_question": (
            "Among complete Q&A episodes, how well does Detector-v1 prioritize episodes that "
            "blinded human raters independently judge as requiring human review?"
        ),
        "primary_outcome_requires": (
            "two independent blinded human raters and the adjudication rule below; without them "
            "the primary outcome is NOT_AVAILABLE and no substitute is permitted"
        ),
        "corpus": {
            "corpus_id": CORPUS_ID,
            "pinned_commit": PINNED_COMMIT,
            "archive_sha256": ARCHIVE_SHA256,
            "eligible_case_count": len(rows),
            "eligible_case_paths": [row["path"] for row in rows],
        },
        "selection": {
            "rule": (
                "deterministic seeded shuffle of the full eligible frame, take the first "
                f"{SELECTION_SIZE}, then sort by path"
            ),
            "seed": SELECTION_SEED,
            "sample_size": SELECTION_SIZE,
            "selected": [
                {"path": row["path"], "sha256": row["sha256"], "bytes": row["bytes"]}
                for row in chosen
            ],
            "outcome_independence": (
                "the draw depends only on the seed and the pinned inventory, so it cannot depend "
                "on predicted or observed alert status"
            ),
        },
        "protocol": {
            "model": MODEL,
            "temperature": "provider default, not overridden",
            "max_output_tokens": RESERVE_OUTPUT_TOKENS,
            "input_reserve_tokens": RESERVE_INPUT_TOKENS,
            "max_qa_rounds": MAX_QA_ROUNDS,
            "max_concurrent_cases": MAX_CONCURRENT_CASES,
            "request_timeout_seconds": REQUEST_TIMEOUT_SECONDS,
            "run_timeout_seconds": RUN_TIMEOUT_SECONDS,
            "retry_rule": (
                f"at most {MAX_RETRIES_PER_CALL} per call, permitted only for a documented "
                "transport or provider failure before a valid response is received; every retry "
                "counts against the call cap and the budget and is recorded"
            ),
            "prompts": "unmodified protected runtime prompts; no prompt is authored for this study",
            "run_count": RUN_COUNT,
            "stop_rule": (
                "the run stops when the call cap or the budget ceiling is reached and is reported "
                "STOPPED_AT_CAP and partial; it is never re-run and never replaced"
            ),
            "technical_failure_rule": (
                "a technical failure is preserved and reported with its cost; it is never deleted "
                "and never re-run to improve a result"
            ),
        },
        "budget": pessimistic_reservation(),
        "detector_v1": {
            "modified": False,
            "code_sha256": {path: digest_text(ROOT / path) for path in DETECTOR_FILES},
            "thresholds": {
                "STRONG_ALERT": "S1 or S3 or S7",
                "WEAK_ALERT": "not STRONG and (S2 or S6)",
                "NO_ALERT": "otherwise",
                "EXCLUDED": "episode is not scientific_complete",
                "S1": "any answer confidence == Low",
                "S2": "any answer confidence == Medium",
                "S3": "any answer evidence reference is null or length 0",
                "S6": "round_count > 1",
                "S7": "termination_reason == TERMINATED_MAX_ROUNDS",
            },
            "scope": (
                "episode-level and reporting-only; Detector-v1 does not create, feed or modify any "
                "human queue, and it is a different mechanism from Agent-4's queue"
            ),
        },
        "human_review_rubric": {
            "raters": 2,
            "independence": "raters do not see each other's responses at any point",
            "blinding": {"shown": CARD_FIELDS_SHOWN, "withheld": CARD_FIELDS_WITHHELD},
            "confidence_withheld_because": (
                "the per-answer confidence label is Detector-v1's dominant input, so showing it "
                "would make the human judgement partly a readback of the detector rather than an "
                "independent judgement; the cost is that raters see less than an operator would, "
                "and that is recorded as a limitation"
            ),
            "questions": RATER_QUESTIONS,
            "adjudication_rule": (
                "an episode is HUMAN_REVIEW_WORTHY when both raters answer Yes; NOT_WORTHY when "
                "both answer No; INSUFFICIENT when both answer Insufficient information; and "
                "DISAGREEMENT otherwise. A DISAGREEMENT is resolved only by a third "
                "supervisor-authorized adjudicator, is never resolved by the study author, and is "
                "reported as DISAGREEMENT until that adjudication exists."
            ),
            "review_time_rule": (
                "review minutes are reported only if raters actually record time per card; "
                "otherwise minutes saved is NOT_AVAILABLE and may not be estimated"
            ),
        },
        "planned_metrics": {
            "A_pipeline_reliability": [
                "selected cases", "completed cases", "complete episodes",
                "incomplete technical episodes", "calls", "cost", "elapsed time",
                "termination states",
            ],
            "B_detector_to_human_agreement": [
                "alert rate", "human-review-worthy rate",
                "confusion matrix of alert or no-alert against Yes, No and Insufficient",
                "precision and recall, exploratory only and only when denominators are valid",
                "redacted false-positive and false-negative episode cards",
            ],
            "C_operational_baseline": [
                "all-episodes review workload", "detector-prioritized review workload",
                "proportion of human-worthy episodes retained by the prioritized set",
                "review minutes saved, only if raters measured time",
                "provider cost per completed case and per human-confirmed review-worthy episode",
            ],
            "D_robustness": [
                "per-case results", "per-run results", "route distribution",
                "termination distribution",
            ],
            "prioritized_set_definition": (
                "the prioritized set is the STRONG_ALERT episodes. This is fixed now because "
                "Detector-v1's alert rate including WEAK_ALERT has been 1.0 on every episode "
                "observed to date, which would make an alert-versus-no-alert split degenerate."
            ),
            "sensitivity_analyses_preregistered": [
                "prioritized set defined as STRONG_ALERT only, versus STRONG_ALERT or WEAK_ALERT"
            ],
        },
        "evidence_classes": {
            "this_run": "PROSPECTIVE EMPIRICAL EVIDENCE once executed under this manifest",
            "prior_airtravel_runs": "ARCHIVAL / RETROSPECTIVE DESCRIPTIVE EVIDENCE",
            "fake_provider_preflight": "ENGINEERING-ONLY FIXTURE",
            "unavailable_outcomes": "NOT_AVAILABLE",
        },
        "forbidden_claims": FORBIDDEN_CLAIMS,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--out",
        type=Path,
        default=ROOT / "docs/research/phd-proposal/study1-hotspot-manifest.json",
    )
    args = parser.parse_args()
    manifest = build()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(
        json.dumps(
            {
                "status": manifest["status"],
                "selected": [row["path"] for row in manifest["selection"]["selected"]],
                "budget": manifest["budget"],
                "manifest": str(args.out),
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
