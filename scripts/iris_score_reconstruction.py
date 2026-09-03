#!/usr/bin/env python3
"""Read-only reconstruction of frozen Agent-C scores and external C2 evidence.

This module deliberately performs no model, network, or intervention calls.  The
external spreadsheets are treated as private, hash-bound development evidence.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import re
import statistics
import xml.etree.ElementTree as ET
import zipfile
from collections import Counter
from typing import Any

SETTINGS = ("ucd_ch", "ucd_pw", "cd_ch", "cd_pw")
CANONICAL_STATUSES = ("Satisfied", "Partially-Satisfied", "Not-Satisfied")
STATUS_SCORE = {"Satisfied": 1.0, "Partially-Satisfied": 0.5, "Not-Satisfied": 0.0}
_NS = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main", "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships"}


class ReconstructionError(RuntimeError):
    """Raised when a provenance or structural invariant fails."""


def sha256_file(path: pathlib.Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _column(cell_ref: str) -> str:
    return re.match(r"[A-Z]+", cell_ref.upper()).group(0)  # type: ignore[union-attr]


def _shared_strings(archive: zipfile.ZipFile) -> list[str]:
    if "xl/sharedStrings.xml" not in archive.namelist():
        return []
    root = ET.fromstring(archive.read("xl/sharedStrings.xml"))
    return ["".join(text.text or "" for text in item.findall(".//m:t", _NS)) for item in root.findall("m:si", _NS)]


def _cell_value(cell: ET.Element, shared: list[str]) -> str:
    value = cell.find("m:v", _NS)
    text = value.text if value is not None and value.text is not None else ""
    if cell.attrib.get("t") == "s" and text:
        try:
            return shared[int(text)]
        except (IndexError, ValueError) as exc:
            raise ReconstructionError(f"invalid shared string index: {text}") from exc
    if cell.attrib.get("t") == "inlineStr":
        return "".join(node.text or "" for node in cell.findall(".//m:t", _NS))
    return text


def _sheet_targets(archive: zipfile.ZipFile) -> dict[str, str]:
    workbook = ET.fromstring(archive.read("xl/workbook.xml"))
    rels = ET.fromstring(archive.read("xl/_rels/workbook.xml.rels"))
    rel_map = {rel.attrib["Id"]: rel.attrib["Target"] for rel in rels}
    result: dict[str, str] = {}
    for sheet in workbook.findall("m:sheets/m:sheet", _NS):
        target = rel_map[sheet.attrib[f"{{{_NS['r']}}}id"]]
        result[sheet.attrib["name"]] = "xl/" + target.lstrip("/")
    return result


def read_xlsx_rows(path: pathlib.Path, *, expected_sha256: str | None = None) -> dict[str, list[dict[str, Any]]]:
    """Read worksheet values using only the Python standard library."""
    actual = sha256_file(path)
    if expected_sha256 is not None and actual != expected_sha256:
        raise ReconstructionError(f"hash mismatch for {path.name}")
    try:
        archive = zipfile.ZipFile(path)
    except (OSError, zipfile.BadZipFile) as exc:
        raise ReconstructionError(f"invalid xlsx: {path}") from exc
    with archive:
        shared = _shared_strings(archive)
        result: dict[str, list[dict[str, Any]]] = {}
        for name, target in _sheet_targets(archive).items():
            root = ET.fromstring(archive.read(target))
            rows: list[dict[str, Any]] = []
            for row in root.findall(".//m:sheetData/m:row", _NS):
                values = {_column(cell.attrib["r"]): _cell_value(cell, shared) for cell in row.findall("m:c", _NS)}
                rows.append({"row_number": int(row.attrib["r"]), "values": values})
            result[name] = rows
        return result


def reconstruct_case_score(case: dict[str, Any]) -> dict[str, float]:
    stored = float(case.get("total_score", 0.0))
    guideline = sum(float(item.get("score", 0.0)) for item in case.get("compliance_contributions", []))
    fragments = sum(float(item.get("total_contribution", 0.0)) for item in case.get("fragment_contributions", []))
    reconstructed = guideline + fragments
    return {
        "stored_total": stored,
        "reconstructed_total": reconstructed,
        "signed_delta": stored - reconstructed,
    }


def _case_reports(vego_root: pathlib.Path) -> list[tuple[str, pathlib.Path, dict[str, Any]]]:
    output = vego_root / "eval_output"
    result = []
    for path in sorted(output.glob("*/agentC_case_*.json")):
        setting = path.parent.name
        if setting in SETTINGS:
            result.append((setting, path, json.loads(path.read_text(encoding="utf-8"))))
    return result


def audit_agent_c(vego_root: pathlib.Path) -> dict[str, Any]:
    by_setting: dict[str, dict[str, Any]] = {}
    all_rows: list[dict[str, Any]] = []
    for setting, _path, case in _case_reports(vego_root):
        reconstructed = reconstruct_case_score(case)
        all_rows.append({"setting": setting, "case_id": str(case.get("case_id", "")), **reconstructed})
    for setting in SETTINGS:
        values = [row for row in all_rows if row["setting"] == setting]
        abs_deltas = [abs(float(row["signed_delta"])) for row in values]
        deltas = [float(row["signed_delta"]) for row in values]
        by_setting[setting] = {
            "case_reports": len(values),
            "exact_matches": sum(delta == 0 for delta in deltas),
            "mismatches": sum(delta != 0 for delta in deltas),
            "min_signed_delta": min(deltas) if deltas else None,
            "max_signed_delta": max(deltas) if deltas else None,
            "mean_absolute_delta": statistics.fmean(abs_deltas) if abs_deltas else None,
            "median_absolute_delta": statistics.median(abs_deltas) if abs_deltas else None,
        }
    labels = {"entries": 0, "common_key_disagreements": 0, "common_key_cases": 0, "key_set_disagreements": 0, "key_set_cases": 0}
    for _, _, case in _case_reports(vego_root):
        existing = {item.get("guideline_id"): item.get("compliance_status") for item in case.get("existing_mapping", [])}
        contributions = {item.get("guideline_id"): item.get("compliance_status") for item in case.get("compliance_contributions", [])}
        common = set(existing) & set(contributions)
        labels["entries"] += len(case.get("compliance_contributions", []))
        labels["common_key_disagreements"] += sum(existing[key] != contributions[key] for key in common)
        labels["common_key_cases"] += any(existing[key] != contributions[key] for key in common)
        labels["key_set_disagreements"] += int(set(existing) != set(contributions))
        labels["key_set_cases"] += int(set(existing) != set(contributions))
    deltas = [float(row["signed_delta"]) for row in all_rows]
    abs_deltas = [abs(delta) for delta in deltas]
    return {
        "case_reports": len(all_rows),
        "exact_matches": sum(delta == 0 for delta in deltas),
        "mismatches": sum(delta != 0 for delta in deltas),
        "min_signed_delta": min(deltas) if deltas else None,
        "max_signed_delta": max(deltas) if deltas else None,
        "mean_absolute_delta": statistics.fmean(abs_deltas) if abs_deltas else None,
        "median_absolute_delta": statistics.median(abs_deltas) if abs_deltas else None,
        "by_setting": by_setting,
        "label_reconciliation": labels,
        "claim_boundary": "technical_reconstruction_only",
    }


def classify_correction(comment: str) -> tuple[str, str | None]:
    """Classify a Score=0 comment without inferring a new scientific label."""
    normalized = re.sub(r"\s+", " ", comment.strip().lower())
    exact = {
        "satisfied": "Satisfied",
        "partially-satisfied": "Partially-Satisfied",
        "not-satisfied": "Not-Satisfied",
    }
    if normalized in exact:
        return "A", exact[normalized]
    deterministic = {
        "not satisfied": "Not-Satisfied",
        "statisfied": "Satisfied",
        "partialy satisfied": "Partially-Satisfied",
        "partially": "Partially-Satisfied",
        "can be considered as satisfied": "Satisfied",
        "can be considerted as satisfied": "Satisfied",
    }
    if normalized in deterministic:
        return "B", deterministic[normalized]
    if normalized:
        return "C", None
    return "D", None


def audit_external_c2(analysis_root: pathlib.Path) -> dict[str, Any]:
    workbooks: dict[str, dict[str, Any]] = {}
    details: list[dict[str, Any]] = []
    for setting in SETTINGS:
        path = analysis_root / f"scores_{setting}.xlsx"
        if not path.is_file():
            return {"status": "NOT_FOUND", "missing": str(path.name), "claim_boundary": "external_evidence_unavailable"}
        sheets = read_xlsx_rows(path)
        rows = sheets.get("compliance_vectors")
        if not rows:
            raise ReconstructionError(f"compliance_vectors sheet missing in {path.name}")
        headers = rows[0]["values"]
        score_col = next((key for key, value in headers.items() if value.lower() in {"score", "scores"}), None)
        if score_col is None:
            raise ReconstructionError(f"score column missing in {path.name}")
        comment_col = "H" if "H" in headers else "G"
        judgment_rows = [row for row in rows[1:] if row["values"].get(score_col, "") in {"0", "1"}]
        rejected = []
        classifications = Counter()
        for row in judgment_rows:
            values = row["values"]
            if values.get(score_col) != "0":
                continue
            classification, corrected = classify_correction(values.get(comment_col, ""))
            classifications[classification] += 1
            rejected.append({
                "setting": setting,
                "sheet": "compliance_vectors",
                "row_number": row["row_number"],
                "case_id": values.get("A", ""),
                "guideline_id": values.get("B", ""),
                "existing_status": values.get("D", ""),
                "score": values.get(score_col, ""),
                "comment": values.get(comment_col, ""),
                "classification": classification,
                "deterministic_corrected_status": corrected,
            })
        workbooks[setting] = {
            "filename": path.name,
            "sha256": sha256_file(path),
            "sheet": "compliance_vectors",
            "worksheet_rows_including_header": len(rows),
            "judgments": len(judgment_rows),
            "rejected_rows": len(rejected),
            "classification_counts": dict(sorted(classifications.items())),
        }
        details.extend(rejected)
    return {
        "status": "FOUND",
        "total_judgments": sum(item["judgments"] for item in workbooks.values()),
        "rejected_rows": sum(item["rejected_rows"] for item in workbooks.values()),
        "classification_counts": dict(sorted(Counter(row["classification"] for row in details).items())),
        "workbooks": workbooks,
        "rejected_rows_detail": details,
        "claim_boundary": "private_external_development_evidence_only",
    }


def bridge_external_rows(external: dict[str, Any], vego_root: pathlib.Path) -> dict[str, Any]:
    """Attach each private C2 row to its frozen Agent-C contribution, fail closed on absence."""
    if external.get("status") != "FOUND":
        return {"status": "NOT_AVAILABLE", "rows": 0}
    index: dict[tuple[str, str, str], tuple[pathlib.Path, dict[str, Any]]] = {}
    for setting, path, case in _case_reports(vego_root):
        for item in case.get("compliance_contributions", []):
            key = (setting, str(case.get("case_id", "")), str(item.get("guideline_id", "")))
            index[key] = (path, item)
    bridged: list[dict[str, Any]] = []
    unmatched = 0
    for row in external.get("rejected_rows_detail", []):
        key = (row["setting"], row["case_id"], row["guideline_id"])
        match = index.get(key)
        if match is None:
            unmatched += 1
            bridged.append({**row, "bridge_status": "UNMATCHED"})
            continue
        case_path, contribution = match
        corrected = row.get("deterministic_corrected_status")
        original_status = str(contribution.get("compliance_status", ""))
        original_score = float(contribution.get("score", 0.0))
        corrected_score = STATUS_SCORE.get(corrected) if corrected else None
        bridged.append({
            **row,
            "bridge_status": "MATCHED",
            "agent_c_json": case_path.name,
            "agent_c_json_sha256": sha256_file(case_path),
            "agent_c_status": original_status,
            "agent_c_contribution": original_score,
            "deterministic_corrected_contribution": corrected_score,
            "deterministic_contribution_delta": (
                corrected_score - original_score if corrected_score is not None else None
            ),
        })
    return {
        "status": "FOUND" if unmatched == 0 else "PARTIAL",
        "rows": len(bridged),
        "matched_rows": len(bridged) - unmatched,
        "unmatched_rows": unmatched,
        "rows_detail": bridged,
        "claim_boundary": "technical_row_bridge_only",
    }


def run(vego_root: pathlib.Path, analysis_root: pathlib.Path) -> dict[str, Any]:
    external = audit_external_c2(analysis_root)
    return {
        "schema": "iris-score-reconstruction-v1",
        "network": "not_used",
        "holdout_opened": False,
        "intervention_executed": False,
        "agent_c": audit_agent_c(vego_root),
        "external_c2": external,
        "external_c2_agent_c_bridge": bridge_external_rows(external, vego_root),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--vego-root", type=pathlib.Path, default=pathlib.Path("VEGO-AI"))
    parser.add_argument("--analysis-root", type=pathlib.Path, default=None)
    parser.add_argument("--output", type=pathlib.Path, default=None)
    args = parser.parse_args()
    analysis_root = args.analysis_root or args.vego_root / "analysis"
    report = run(args.vego_root, analysis_root)
    rendered = json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
