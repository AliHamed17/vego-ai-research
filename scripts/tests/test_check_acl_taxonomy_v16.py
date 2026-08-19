from __future__ import annotations

from pathlib import Path

from scripts.check_acl_taxonomy_v16 import (
    ALLOWED_LABELS,
    validate_csv_matrix,
    validate_repository_artifacts,
    validate_svg,
)


def _write_matrix(path: Path, rows: list[dict[str, str]]) -> None:
    import csv

    fieldnames = ["branch_id", "provenance", "relevance", "rq_mapping"]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def test_current_repository_artifacts_have_no_hard_errors() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    findings = validate_repository_artifacts(repo_root)
    errors = [finding for finding in findings if finding.level == "ERROR"]
    assert not errors, "\n".join(f"{item.check}: {item.detail}" for item in errors)


def test_matrix_rejects_non_controlled_relevance_label(tmp_path: Path) -> None:
    matrix = tmp_path / "matrix.csv"
    _write_matrix(
        matrix,
        [
            {
                "branch_id": "ACL-01",
                "provenance": "ACL-PAPER",
                "relevance": "RELEVANT",
                "rq_mapping": "U-RQ",
            }
        ],
    )

    findings = validate_csv_matrix(matrix, expected_total=None, expected_derived=None)
    assert any(
        finding.level == "ERROR" and "controlled relevance vocabulary" in finding.check
        for finding in findings
    )


def test_matrix_rejects_duplicate_branch_ids(tmp_path: Path) -> None:
    matrix = tmp_path / "matrix.csv"
    _write_matrix(
        matrix,
        [
            {
                "branch_id": "ACL-01",
                "provenance": "ACL-PAPER",
                "relevance": ALLOWED_LABELS[0],
                "rq_mapping": "U-RQ",
            },
            {
                "branch_id": "ACL-01",
                "provenance": "VEGO-AI-DERIVED",
                "relevance": ALLOWED_LABELS[-1],
                "rq_mapping": "SQ1",
            },
        ],
    )

    findings = validate_csv_matrix(matrix, expected_total=None, expected_derived=None)
    assert any(
        finding.level == "ERROR" and "unique branch identifiers" in finding.check
        for finding in findings
    )


def test_svg_rejects_external_http_image_dependency(tmp_path: Path) -> None:
    svg = tmp_path / "external.svg"
    svg.write_text(
        '<svg xmlns="http://www.w3.org/2000/svg" '
        'xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 10 10">'
        '<image xlink:href="https://example.org/external.png" />'
        "</svg>",
        encoding="utf-8",
    )

    findings = validate_svg(svg)
    assert any(
        finding.level == "ERROR" and "external asset dependencies" in finding.check
        for finding in findings
    )
