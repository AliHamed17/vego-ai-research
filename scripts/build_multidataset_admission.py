"""Build safe tracked multi-dataset admission artifacts from metadata only.

The source input contains no raw records, prompts, model outputs, or private
paths. This builder makes no network or provider calls.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
DEFAULT_INPUT = ROOT / "docs/research/phd-proposal/multidataset/admission-inputs-v1.json"
DEFAULT_OUTPUT = ROOT / "docs/research/phd-proposal/multidataset"


def _canonical_json(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode(
        "utf-8"
    )


def _load(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot load admission inputs: {path.name}") from exc
    if payload.get("schema_version") != "vego-multidataset-admission-inputs-v1":
        raise ValueError("unsupported admission-inputs schema")
    return payload


def _write(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(_canonical_json(payload))


def build(input_path: Path = DEFAULT_INPUT, output_dir: Path = DEFAULT_OUTPUT) -> dict[str, Any]:
    """Build cards and one summary; return the safe machine-readable report."""

    from vego_multidataset.admission import build_qure_data_card, build_vego_se_archive_card
    from vego_multidataset.schemas import validate_named

    source = _load(input_path)
    qure = build_qure_data_card(source["qure"])
    archive = build_vego_se_archive_card(source["vego_se_archive"])
    for card in (qure, archive):
        validate_named(card, "multidataset-data-card-v1.schema.json")
    report = {
        "schema_version": "vego-multidataset-admission-report-v1",
        "review_date": source["review_date"],
        "study_status": "NO_GO_FOR_PROVIDER_EXECUTION",
        "datasets": {
            "AIRTRAVEL_QA_FEASIBILITY_BASELINE": {
                "evidence_class": "ARCHIVAL_RETROSPECTIVE_DESCRIPTIVE_EVIDENCE",
                "new_empirical_run": "NOT_PERFORMED",
                "pooling": "PROHIBITED",
            },
            qure["dataset_id"]: {
                "decision": qure["decision"],
                "admission_blockers": qure["admission_blockers"],
            },
            archive["dataset_id"]: {
                "decision": archive["decision"],
                "admission_blockers": archive["admission_blockers"],
            },
        },
        "provider_calls": 0,
        "spend_usd": 0.0,
        "claim_boundary": "MULTI_DATASET_DESCRIPTIVE_BASELINE_NOT_ESTABLISHED_UNTIL_DATA_ADMISSION_AND_EXECUTION_GATES_PASS",
    }
    _write(output_dir / "qure-data-card-v1.json", qure)
    _write(output_dir / "vego-se-archive-data-card-v1.json", archive)
    _write(output_dir / "multidataset-admission-report-v1.json", report)
    _write_card_markdown(output_dir / "qure-data-card-v1.md", qure)
    _write_card_markdown(output_dir / "vego-se-archive-data-card-v1.md", archive)
    _write_markdown(output_dir / "2026-09-08-multidataset-data-admission-report.md", report, qure, archive)
    _write_decision_table(output_dir / "2026-09-08-multidataset-decision-table.md", report, qure, archive)
    return report


def _write_markdown(path: Path, report: dict[str, Any], qure: dict[str, Any], archive: dict[str, Any]) -> None:
    text = f"""# VEGO-AI Study 1 — multi-dataset admission status

Status: `{report['study_status']}`. This is a metadata-only admission report,
not a result report. It made no provider/API/model call and spent USD 0.

## Evidence boundary

- `AIRTRAVEL_QA_FEASIBILITY_BASELINE` remains archival, retrospective,
  descriptive evidence. It is not pooled with the datasets below.
- `QURE_EXTERNAL_REQUIREMENTS_QUALITY_VALIDATION` is not admitted. The pinned
  concept DOI is [`10.5281/zenodo.15656471`](https://doi.org/10.5281/zenodo.15656471);
  the captured version record is
  [`10.5281/zenodo.15656472`](https://doi.org/10.5281/zenodo.15656472). The
  record-specific licence, local raw-file hash, and versioned file inventory
  are not yet verified.
- `VEGO_SE_ARCHIVE_DATASET_PENDING_ADMISSION` is a metadata-only local archive
  inventory. Its provenance, licence, and task fit are unverified; no content
  inspection or provider execution was performed.

## Admission decisions

| Dataset | Decision | Blocking conditions | Permitted statement |
| --- | --- | --- | --- |
| QuRE | `{qure['decision']}` | `{', '.join(qure['admission_blockers'])}` | Official metadata was located; no requirements-quality experiment was run. |
| VEGO_SE archive | `{archive['decision']}` | `{', '.join(archive['admission_blockers'])}` | A local archive was inventoried by ZIP metadata only. |

## Claim boundary

No multi-dataset baseline, association result, ON/OFF result, alert accuracy,
human benefit, or generalisation claim has been established. QuRE labels, if
later admitted, are external requirements-quality labels —
`NOT_DIRECT_ALERT_GROUND_TRUTH`.
"""
    path.write_text(text.rstrip() + "\n", encoding="utf-8", newline="\n")


def _display(value: Any) -> str:
    """Render metadata values without serialising raw content into Markdown."""

    if value is None:
        return "NOT_AVAILABLE"
    if isinstance(value, list):
        return ", ".join(str(item) for item in value) or "NONE"
    if isinstance(value, dict):
        return json.dumps(value, ensure_ascii=False, sort_keys=True)
    return str(value)


def _write_card_markdown(path: Path, card: dict[str, Any]) -> None:
    """Emit a human-readable counterpart to one safe machine data card."""

    fields = (
        ("Dataset ID", card["dataset_id"]),
        ("Dataset name", card["dataset_name"]),
        ("Owner / publisher", card["owner_or_publisher"]),
        ("Official source", card["official_source"]),
        ("Licence", card["licence"]),
        ("Date / version", card["date_or_version"]),
        ("Raw artifact", card["raw_artifact"]),
        ("Source-file count", card["source_file_count"]),
        ("Analysis unit", card["analysis_unit"]),
        ("Language / domain", card["language_or_domain"]),
        ("Independent labels / references", card["independent_labels_or_reference_artifacts"]),
        ("Potential leakage risk", card["potential_leakage_risk"]),
        ("Privacy classification", card["privacy_classification"]),
        ("Intended VEGO-AI task", card["intended_vego_task"]),
        ("Permitted claims", card["permitted_claims"]),
        ("Prohibited claims", card["prohibited_claims"]),
        ("Admission decision", card["decision"]),
        ("Admission blockers", card["admission_blockers"]),
        ("Review status", card["review_status"]),
    )
    rows = "\n".join(f"| {label} | {_display(value)} |" for label, value in fields)
    text = f"""# VEGO-AI Study 1 data card — {card['dataset_name']}

Evidence class: `{card['evidence_class']}`. This card contains only safe
metadata and hashes; it does not contain raw dataset content, prompts, labels,
or model outputs.

| Field | Value |
| --- | --- |
{rows}

"""
    path.write_text(text.rstrip() + "\n", encoding="utf-8", newline="\n")


def _write_decision_table(
    path: Path,
    report: dict[str, Any],
    qure: dict[str, Any],
    archive: dict[str, Any],
) -> None:
    """Write a claim-safe end-state table, without fabricating results."""

    text = f"""# VEGO-AI Study 1 — multi-dataset decision table

Status: `{report['study_status']}`. Every item below is a decision or evidence
state, not an empirical result.

| Lane | Evidence state | Decision | What can be stated now | What cannot be stated now |
| --- | --- | --- | --- | --- |
| AIRTRAVEL_QA_FEASIBILITY_BASELINE | ARCHIVAL / RETROSPECTIVE DESCRIPTIVE | PRESERVED | Existing feasibility evidence remains separate. | No new empirical result or pooled comparison. |
| QURE_EXTERNAL_REQUIREMENTS_QUALITY_VALIDATION | PUBLIC_EXTERNAL_PENDING_ADMISSION | {qure['decision']} | Official metadata was located. | No QuRE execution, association, or Detector accuracy claim. |
| VEGO_SE_ARCHIVE_DATASET_PENDING_ADMISSION | LOCAL_ARCHIVE_METADATA_ONLY | {archive['decision']} | ZIP metadata was inventoried safely. | No content claim, execution, or portability claim. |
| MULTI_DATASET_DESCRIPTIVE_BASELINE | BLOCKED | NO_GO | Engineering admission and leakage controls are implemented. | No multi-dataset baseline or ON/OFF result. |
| Human-review validity | NOT_MEASURED | TEMPLATE_PREPARED | A Hebrew rubric and scoring template are ready. | No alert correctness, false-positive rate, or human benefit claim. |

Provider/API/model calls: `0`. Spend: `USD 0`. No provider-backed execution is
permitted from this state.
"""
    path.write_text(text, encoding="utf-8", newline="\n")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    report = build(args.input, args.output_dir)
    print(json.dumps({"status": report["study_status"], "provider_calls": 0}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
