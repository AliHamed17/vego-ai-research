#!/usr/bin/env python3
"""Fail-closed validation for the VEGO-AI ACL-2026 taxonomy v16 artifacts.

The validator checks repository-visible structural invariants only. It does not
certify scholarly correctness, supervisor approval, formal-search completion,
or empirical evidence.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
import xml.etree.ElementTree as ET
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable, Sequence

ALLOWED_LABELS: tuple[str, ...] = (
    "HIGHLY RELEVANT",
    "LESS RELEVANT",
    "NOT RELEVANT AT ALL",
    "MISSING FROM ACL TAXONOMY",
)

EXPECTED_TOTAL_ROWS = 40
EXPECTED_DERIVED_ROWS = 6

MATRIX_PATH = Path(
    "docs/research/phd-proposal/acl-2026-taxonomy-evidence-matrix-v16.csv"
)
MAP_PATH = Path(
    "docs/research/phd-proposal/acl-2026-taxonomy-vego-ai-relevance-map-v16.md"
)
AUDIT_PATH = Path(
    "docs/research/phd-proposal/acl-taxonomy-v16-strict-audit.md"
)
REVIEW_GATE_PATH = Path(
    "docs/research/phd-proposal/acl-taxonomy-v16-strict-review-gate.md"
)
DECISION_RECORD_PATH = Path(
    "docs/research/phd-proposal/acl-taxonomy-v16-supervisor-decision-record.md"
)
MERMAID_PATH = Path("docs/visualizations/vego-ai-acl-taxonomy-map-v16.mmd")
SVG_PATH = Path("docs/visualizations/vego-ai-acl-taxonomy-map-v16.svg")

REQUIRED_PATHS: tuple[Path, ...] = (
    MATRIX_PATH,
    MAP_PATH,
    AUDIT_PATH,
    REVIEW_GATE_PATH,
    DECISION_RECORD_PATH,
    MERMAID_PATH,
    SVG_PATH,
)

PRIMARY_ARTIFACT_TERMS: tuple[str, ...] = (
    "attention-budget cost/coverage model",
    "normative judgment-record contract",
    "transfer-eligibility decision procedure",
)

OPEN_GATE_TERMS: tuple[str, ...] = ("0/5", "0/24", "0/6", "40–60")


@dataclass(frozen=True)
class Finding:
    level: str
    check: str
    detail: str


def _finding(level: str, check: str, detail: str) -> Finding:
    return Finding(level=level, check=check, detail=detail)


def _find_column(fieldnames: Sequence[str], needles: Sequence[str]) -> str | None:
    for field in fieldnames:
        normalized = field.strip().lower().replace("-", "_").replace(" ", "_")
        if any(needle in normalized for needle in needles):
            return field
    return None


def _is_derived_provenance(value: str) -> bool:
    normalized = value.upper()
    return "VEGO" in normalized or "ALI" in normalized or "DERIVED" in normalized


def validate_csv_matrix(
    path: Path,
    *,
    expected_total: int | None = EXPECTED_TOTAL_ROWS,
    expected_derived: int | None = EXPECTED_DERIVED_ROWS,
) -> list[Finding]:
    findings: list[Finding] = []
    if not path.is_file():
        return [_finding("ERROR", "matrix file exists", f"missing `{path}`")]

    try:
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            rows = list(reader)
            fieldnames = reader.fieldnames or []
    except (OSError, csv.Error) as exc:
        return [_finding("ERROR", "matrix CSV parses", repr(exc))]

    if not fieldnames:
        return [_finding("ERROR", "matrix has a header", "no CSV header detected")]

    findings.append(
        _finding("PASS", "matrix CSV parses", f"{len(rows)} rows; {len(fieldnames)} columns")
    )

    relevance_column = _find_column(fieldnames, ("relevance", "classification"))
    provenance_column = _find_column(fieldnames, ("provenance", "origin", "source_type"))
    id_column = _find_column(fieldnames, ("branch_id", "dimension_id", "row_id"))
    if id_column is None:
        for candidate in fieldnames:
            if candidate.strip().lower() == "id":
                id_column = candidate
                break

    if relevance_column is None:
        findings.append(
            _finding("ERROR", "controlled relevance vocabulary", "no relevance column found")
        )
    else:
        values = sorted(
            {
                (row.get(relevance_column) or "").strip()
                for row in rows
                if (row.get(relevance_column) or "").strip()
            }
        )
        invalid = [value for value in values if value not in ALLOWED_LABELS]
        missing = [label for label in ALLOWED_LABELS if label not in values]
        if invalid or missing:
            findings.append(
                _finding(
                    "ERROR",
                    "controlled relevance vocabulary",
                    f"invalid={invalid}; missing={missing}; observed={values}",
                )
            )
        else:
            findings.append(
                _finding(
                    "PASS",
                    "controlled relevance vocabulary",
                    "all four exact labels are present and no substitute label is used",
                )
            )

    if id_column is None:
        findings.append(
            _finding("ERROR", "unique branch identifiers", "no branch/dimension ID column found")
        )
    else:
        identifiers = [(row.get(id_column) or "").strip() for row in rows]
        blank_count = sum(not identifier for identifier in identifiers)
        duplicates = sorted(
            {
                identifier
                for identifier in identifiers
                if identifier and identifiers.count(identifier) > 1
            }
        )
        if blank_count or duplicates:
            findings.append(
                _finding(
                    "ERROR",
                    "unique branch identifiers",
                    f"blank={blank_count}; duplicates={duplicates}",
                )
            )
        else:
            findings.append(
                _finding(
                    "PASS",
                    "unique branch identifiers",
                    f"{len(identifiers)} stable non-duplicate IDs",
                )
            )

    if provenance_column is None:
        findings.append(
            _finding(
                "ERROR",
                "source/derived provenance separation",
                "no provenance/origin column found",
            )
        )
    else:
        derived = [
            row
            for row in rows
            if _is_derived_provenance((row.get(provenance_column) or "").strip())
        ]
        source = [row for row in rows if row not in derived]
        if not derived or not source:
            findings.append(
                _finding(
                    "ERROR",
                    "source/derived provenance separation",
                    f"source={len(source)}; derived={len(derived)}",
                )
            )
        else:
            findings.append(
                _finding(
                    "PASS",
                    "source/derived provenance separation",
                    f"source={len(source)}; derived={len(derived)}",
                )
            )
        if expected_derived is not None:
            findings.append(
                _finding(
                    "PASS" if len(derived) == expected_derived else "ERROR",
                    "expected VEGO-AI-derived dimension count",
                    f"expected={expected_derived}; observed={len(derived)}",
                )
            )

    if expected_total is not None:
        findings.append(
            _finding(
                "PASS" if len(rows) == expected_total else "ERROR",
                "expected evidence-matrix row count",
                f"expected={expected_total}; observed={len(rows)}",
            )
        )

    return findings


def validate_svg(path: Path) -> list[Finding]:
    findings: list[Finding] = []
    if not path.is_file():
        return [_finding("ERROR", "SVG exists", f"missing `{path}`")]

    try:
        tree = ET.parse(path)
    except (ET.ParseError, OSError) as exc:
        return [_finding("ERROR", "SVG XML parses", repr(exc))]

    root = tree.getroot()
    view_box = root.attrib.get("viewBox", "").strip()
    if not view_box:
        findings.append(_finding("ERROR", "SVG viewBox", "missing viewBox"))
    else:
        findings.append(_finding("PASS", "SVG viewBox", view_box))

    external: list[str] = []
    for element in root.iter():
        for attribute, value in element.attrib.items():
            if "href" not in attribute.lower() and "src" not in attribute.lower():
                continue
            if re.match(r"https?://", value or "", flags=re.IGNORECASE):
                external.append(value)

    if external:
        findings.append(
            _finding(
                "ERROR",
                "SVG has no external asset dependencies",
                ", ".join(sorted(set(external))),
            )
        )
    else:
        findings.append(
            _finding("PASS", "SVG has no external asset dependencies", "none detected")
        )

    findings.append(_finding("PASS", "SVG XML parses", root.tag))
    return findings


def _validate_text_contains(
    path: Path,
    terms: Iterable[str],
    *,
    check_prefix: str,
) -> list[Finding]:
    if not path.is_file():
        return [_finding("ERROR", check_prefix, f"missing `{path}`")]
    text = path.read_text(encoding="utf-8", errors="replace")
    findings: list[Finding] = []
    for term in terms:
        findings.append(
            _finding(
                "PASS" if term in text else "ERROR",
                f"{check_prefix}: `{term}`",
                "present" if term in text else f"missing from `{path}`",
            )
        )
    return findings


def validate_repository_artifacts(repo_root: Path) -> list[Finding]:
    repo_root = repo_root.resolve()
    findings: list[Finding] = []

    missing = [str(path) for path in REQUIRED_PATHS if not (repo_root / path).is_file()]
    findings.append(
        _finding(
            "PASS" if not missing else "ERROR",
            "required v16 artifact set",
            "all required files present" if not missing else f"missing={missing}",
        )
    )
    if missing:
        return findings

    findings.extend(validate_csv_matrix(repo_root / MATRIX_PATH))
    findings.extend(validate_svg(repo_root / SVG_PATH))

    for path in (MAP_PATH, MERMAID_PATH, SVG_PATH):
        findings.extend(
            _validate_text_contains(
                repo_root / path,
                ALLOWED_LABELS,
                check_prefix=f"exact four-label scale in {path.name}",
            )
        )

    combined_paths = (MAP_PATH, AUDIT_PATH, REVIEW_GATE_PATH, DECISION_RECORD_PATH)
    combined_text = "\n".join(
        (repo_root / path).read_text(encoding="utf-8", errors="replace")
        for path in combined_paths
    ).lower()

    for term in PRIMARY_ARTIFACT_TERMS:
        findings.append(
            _finding(
                "PASS" if term.lower() in combined_text else "ERROR",
                f"primary study artifact: `{term}`",
                "present" if term.lower() in combined_text else "missing",
            )
        )

    for term in OPEN_GATE_TERMS:
        findings.append(
            _finding(
                "PASS" if term in combined_text else "ERROR",
                f"open evidence gate disclosed: `{term}`",
                "present" if term in combined_text else "missing",
            )
        )

    map_text = (repo_root / MAP_PATH).read_text(encoding="utf-8", errors="replace")
    findings.append(
        _finding(
            "PASS" if "first-class" in map_text.lower() else "ERROR",
            "missing-dimension claim is branch-scoped",
            "first-class taxonomy-branch boundary present"
            if "first-class" in map_text.lower()
            else "no first-class taxonomy-branch boundary found",
        )
    )

    review_gate = (repo_root / REVIEW_GATE_PATH).read_text(
        encoding="utf-8", errors="replace"
    )
    findings.append(
        _finding(
            "PASS" if "NOT MERGE READY" in review_gate else "ERROR",
            "strict no-merge gate",
            "explicit NOT MERGE READY verdict present"
            if "NOT MERGE READY" in review_gate
            else "missing explicit no-merge verdict",
        )
    )

    return findings


def _render_text(findings: Sequence[Finding]) -> str:
    lines = ["ACL taxonomy v16 structural validation"]
    for finding in findings:
        lines.append(f"[{finding.level}] {finding.check}: {finding.detail}")
    errors = [finding for finding in findings if finding.level == "ERROR"]
    lines.append(
        f"Summary: {len(findings)} checks; {len(errors)} error(s); "
        "scholarly/human/empirical gates are outside this validator."
    )
    return "\n".join(lines)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path(__file__).resolve().parents[1],
        help="Repository root (default: parent of scripts/).",
    )
    parser.add_argument(
        "--json",
        dest="json_path",
        type=Path,
        help="Optional path for a machine-readable findings report.",
    )
    args = parser.parse_args(argv)

    findings = validate_repository_artifacts(args.repo_root)
    if args.json_path:
        args.json_path.parent.mkdir(parents=True, exist_ok=True)
        args.json_path.write_text(
            json.dumps([asdict(finding) for finding in findings], indent=2) + "\n",
            encoding="utf-8",
        )

    print(_render_text(findings))
    return 1 if any(finding.level == "ERROR" for finding in findings) else 0


if __name__ == "__main__":
    sys.exit(main())
