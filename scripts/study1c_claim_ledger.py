"""A machine-readable ledger of every claim the Study 1C package may and may not make.

Each entry names the claim, where its evidence comes from, its evidence class, whether it is
permitted or prohibited, and the limitation that travels with it. Prose can drift; a ledger that
tests read cannot, so the guard rails live here rather than in a paragraph somebody may edit.

The prohibited entries are not decoration. Each one was either asserted in an earlier draft of
this package or is one step away from a number the package does report, which is exactly when a
reader is most likely to make the leap.

No provider is contacted; the ledger is authored from the reconciliation output and the frozen
manifest, and it computes nothing empirical of its own.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]

PROSPECTIVE = "PROSPECTIVE EMPIRICAL EVIDENCE"
ARCHIVAL = "ARCHIVAL / RETROSPECTIVE DESCRIPTIVE EVIDENCE"
FIXTURE = "ENGINEERING-ONLY FIXTURE"
UNAVAILABLE = "NOT_AVAILABLE"

RECON = "external_data/airtravel-pr38/reconciliation.json"
BASELINES = "external_data/airtravel-pr38/analysis-baselines/detector-baselines.json"
MANIFEST = "docs/research/phd-proposal/study1-hotspot-manifest.json"

PERMITTED = [
    {
        "claim": "Under the recorded rule, alert classification is highly sensitive to Q&A episode "
                 "length; long episodes tend to saturate toward STRONG_ALERT.",
        "evidence_source": BASELINES,
        "evidence_class": ARCHIVAL,
        "limitation": "a rule-behaviour finding, not validation of real human-intervention need",
    },
    {
        "claim": "On Study 1C run 1, no baseline is identical to Detector-v1 at the THREE-CLASS "
                 "level, and three baselines including ALWAYS_ALERT are identical at the BINARY "
                 "REVIEW level.",
        "evidence_source": BASELINES,
        "evidence_class": ARCHIVAL,
        "limitation": "the two levels answer different questions and may never be quoted as one",
    },
    {
        "claim": "Detector-v1 selected every complete episode for review in the accepted run and "
                 "in both Study 1C runs, so its UNVALIDATED_SCREENING_FRACTION there is 0.",
        "evidence_source": RECON,
        "evidence_class": ARCHIVAL,
        "limitation": "a screening fraction is not saved human work and not a benefit",
    },
    {
        "claim": "Per-run counts of complete episodes, incomplete technical episodes, "
                 "STRONG/WEAK/NO_ALERT, calls and cost, each on its own denominator.",
        "evidence_source": RECON,
        "evidence_class": ARCHIVAL,
        "limitation": "runs differ in configuration and are never pooled or averaged",
    },
    {
        "claim": "The AirTravel corpus archive digest reproduced byte-exactly against the value "
                 "pinned before re-acquisition.",
        "evidence_source": "docs/research/phd-proposal/text2uml-airtravel/source-manifest.json",
        "evidence_class": "PUBLIC PROVENANCE, VERIFIED",
        "limitation": "byte identity of inputs, not validity of anything computed from them",
    },
    {
        "claim": "The deterministic fixture envelope reaches every class and every isolable branch "
                 "of the frozen rule.",
        "evidence_source": "scripts/airtravel_detector_envelope_extended.py",
        "evidence_class": FIXTURE,
        "limitation": "synthetic inputs; carries no scientific meaning and no denominator shared "
                      "with any run",
    },
    {
        "claim": "The hotspot study is preregistered; its manifest declares "
                 "PREREGISTERED_NOT_EXECUTED and no run receipt is tracked in this repository.",
        "evidence_source": MANIFEST,
        "evidence_class": "REPOSITORY-VERIFIABLE STATUS",
        "limitation": "a private local receipt cannot upgrade a public status",
    },
]

PROHIBITED = [
    {
        "claim": "Detector-v1 reduces human review workload.",
        "why_prohibited": "no human review time was measured and no human-review outcome exists; "
                          "a screening fraction is not saved work",
        "required_wording_instead": "UNVALIDATED_SCREENING_FRACTION, with its denial of benefit",
        "evidence_class_if_ever_available": UNAVAILABLE,
    },
    {
        "claim": "Detector-v1 detects hotspots, or prioritizes effectively.",
        "why_prohibited": "effectiveness is defined against human judgement that does not exist",
        "required_wording_instead": "the rule selects episodes according to its recorded signals",
        "evidence_class_if_ever_available": UNAVAILABLE,
    },
    {
        "claim": "No baseline matches Detector-v1.",
        "why_prohibited": "false at the binary review level whenever every episode is reviewed; "
                          "the sentence omits the level and is therefore not evaluable",
        "required_wording_instead": "name the level: three-class, or binary review",
        "evidence_class_if_ever_available": ARCHIVAL,
    },
    {
        "claim": "No episode has ever been NO_ALERT.",
        "why_prohibited": "unscoped. True of the accepted run and both full-frame runs; a later "
                          "pilot run recorded one",
        "required_wording_instead": "scope the sentence to the runs it describes",
        "evidence_class_if_ever_available": ARCHIVAL,
    },
    {
        "claim": "A case on which Detector-v1 is silent is safe, or contains no problem.",
        "why_prohibited": "silence is the absence of a selection, not a finding about the case",
        "required_wording_instead": "Detector-v1 produced no episode-level selection for this case",
        "evidence_class_if_ever_available": UNAVAILABLE,
    },
    {
        "claim": "Domain-Mistake labels from the coverage stage are ground truth for Detector-v1.",
        "why_prohibited": "different unit of analysis and a different mechanism's own output",
        "required_wording_instead": "co-occurrence between two mechanisms, neither of them truth",
        "evidence_class_if_ever_available": UNAVAILABLE,
    },
    {
        "claim": "The hotspot run is prospective evidence.",
        "why_prohibited": "the draw seed was fixed after the full-frame outcomes were known, so no "
                          "pre-commitment record predates them",
        "required_wording_instead": "PILOT_INFORMED_POST_OUTCOME",
        "evidence_class_if_ever_available": ARCHIVAL,
    },
    {
        "claim": "Accuracy, precision, recall or F1 for Detector-v1.",
        "why_prohibited": "no ground-truth labels exist for this corpus; the quantities are not "
                          "computable, not merely unmeasured",
        "required_wording_instead": UNAVAILABLE,
        "evidence_class_if_ever_available": UNAVAILABLE,
    },
    {
        "claim": "Causality, generalization, representativeness, or VEGO-AI superiority.",
        "why_prohibited": "no comparison condition, no sampling frame beyond this corpus, and no "
                          "ON/OFF design was executed",
        "required_wording_instead": "descriptive statement scoped to this corpus and configuration",
        "evidence_class_if_ever_available": UNAVAILABLE,
    },
    {
        "claim": "Pooled or averaged figures across runs.",
        "why_prohibited": "the runs differ in case count and configuration; a pooled denominator "
                          "would describe no run that was executed",
        "required_wording_instead": "report each run beside the others on its own denominator",
        "evidence_class_if_ever_available": UNAVAILABLE,
    },
]


def build() -> dict[str, Any]:
    return {
        "schema_version": "study1c-claim-ledger-v1",
        "purpose": "the authoritative list of what this package may and may not assert",
        "evidence_class_vocabulary": [PROSPECTIVE, ARCHIVAL, FIXTURE, UNAVAILABLE],
        "permitted": [{**row, "status": "PERMITTED"} for row in PERMITTED],
        "prohibited": [{**row, "status": "PROHIBITED"} for row in PROHIBITED],
        "counts": {"permitted": len(PERMITTED), "prohibited": len(PROHIBITED)},
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--out",
        type=Path,
        default=ROOT / "docs/research/phd-proposal/study1c-claim-ledger.json",
    )
    args = parser.parse_args()
    ledger = build()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(
        json.dumps(ledger, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(json.dumps({"written": str(args.out), **ledger["counts"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
