from __future__ import annotations

import csv
import hashlib
import importlib.util
import json
import re
import sys
from collections import Counter
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts/build_acl2026_corpus.py"
SPEC = importlib.util.spec_from_file_location("build_acl2026_corpus", SCRIPT)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)

CORPUS = ROOT / "literature/acl2026-human-agent-corpus"

SAMPLE = """# Example
## 📄 Latest Research Papers
- **[2026-01-01]** [arXiv 2026] [Ask or Assume?](https://arxiv.org/abs/2601.00001) [![GitHub stars](https://img.shields.io/github/stars/a/b?style=social)](https://github.com/a/b)

## 📚 Applications, Datasets & Benchmarks
### 👨🏻‍💻 Software Engineering, Coding
- **[2026-01-01]** [arXiv 2026] [Ask or Assume?](https://www.arxiv.org/pdf/2601.00001)

## 🔍 Taxonomy
### 🤝 Human Feedback
| Title | Date & Code | Feedback Type | Feedback Subtype | Feedback Granularity | Feedback Phase |
| --- | --- | --- | --- | --- | --- |
| [Ask or Assume?](https://arxiv.org/abs/2601.00001v2) | [2026/01](https://github.com/a/b) | Guidance | Critique | Segment | During Task |
### 🔄 Interaction
| Title | Date & Code | Interaction Types | Interaction Variant |
| --- | --- | --- | --- |
| [A fuller title](https://arxiv.org/abs/2601.00001) | 2026/01 | Collaboration | Supervision |
### 🎛️ Orchestration
| Title | Date & Code | Orchestration Strategy | Orchestration Synchronization |
| --- | --- | --- | --- |
| [Other work](https://openreview.net/forum?id=ABC123) | 2025/01 | One-by-One | Synchronous |
### 💬 Communication
| Title | Date & Code | Communication Structure | Communication Mode |
| --- | --- | --- | --- |
| [Other work](https://openreview.net/forum?id=ABC123) | 2025/01 | Centralized | Conversation |

## 📌 Contributing
"""


def _read_csv(name: str) -> list[dict[str, str]]:
    with (CORPUS / name).open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def test_parser_scopes_source_sections_and_ignores_badge_links() -> None:
    occurrences = MODULE.parse_readme(SAMPLE)

    assert len(occurrences) == 6
    assert occurrences[0].title == "Ask or Assume?"
    assert occurrences[0].primary_url == "https://arxiv.org/abs/2601.00001"
    assert Counter(item.source_section for item in occurrences) == {
        "Latest Research Papers": 1,
        "Applications, Datasets & Benchmarks": 1,
        "Taxonomy": 4,
    }


def test_dedup_connects_title_and_identifier_aliases() -> None:
    occurrences = MODULE.parse_readme(SAMPLE)
    works = MODULE.build_works(occurrences)

    # The arXiv aliases and the title variant are one component. The second work
    # is linked by its exact strong identifier and normalized title.
    assert len(works) == 2
    assert {work.occurrence_count for work in works} == {2, 4}
    assert all(work.work_id.startswith("ACL26-W-") for work in works)


def test_generated_manifest_is_pinned_and_hash_bound() -> None:
    manifest = json.loads((CORPUS / "source-manifest.json").read_text(encoding="utf-8"))

    assert manifest["schema_version"] == "VEGO-ACL2026-Corpus-v1"
    assert manifest["source"]["commit"] == "7b3ba9deefe99172748582f6025d995ccc2a6f86"
    assert manifest["source"]["readme_sha256"] == (
        "3410215aad4085e4caf15b1217e19825da988bc7e5189fe8baa870fa2794bf5c"
    )
    assert manifest["counts"] == {
        "raw_occurrences": 525,
        "distinct_works": 116,
        "latest_research_works": 106,
        "application_works": 57,
        "taxonomy_works": 90,
    }
    assert manifest["boundaries"]["formal_queries"] == (
        "QL-01 through QL-05: protocol ready / deferred after proposal"
    )
    assert manifest["boundaries"]["research_questions"] == "Provisional / unresolved"
    assert manifest["boundaries"]["methodology"] == "Frozen pre-existing draft"
    for name, expected_hash in manifest["artifacts"].items():
        assert hashlib.sha256((CORPUS / name).read_bytes()).hexdigest() == expected_hash


def test_generated_occurrences_and_taxonomy_counts_are_exact() -> None:
    occurrences = _read_csv("occurrences.csv")
    works = _read_csv("works.csv")

    assert len(occurrences) == 525
    assert len(works) == 116
    branches = Counter(
        row["Taxonomy_Branch"]
        for row in occurrences
        if row["Source_Section"] == "Taxonomy"
    )
    assert branches == {
        "Human Feedback": 89,
        "Interaction": 89,
        "Orchestration": 90,
        "Communication": 89,
    }
    assert len({row["Work_ID"] for row in works}) == 116
    assert all(int(row["Occurrence_Count"]) >= 1 for row in works)
    assert all(row["Source_Commit"] == MODULE.SOURCE_COMMIT for row in works)


def test_machine_screen_is_complete_but_never_claims_human_inclusion() -> None:
    works = _read_csv("works.csv")
    screening = _read_csv("screening.csv")

    assert {row["Work_ID"] for row in screening} == {row["Work_ID"] for row in works}
    assert all(row["Machine_Screen_Status"] == "Complete" for row in screening)
    assert all(row["Human_Review_Status"] == "Pending" for row in screening)
    assert all(row["Inclusion_Decision"] == "Pending human title/abstract review" for row in screening)
    assert all(not row["Exclusion_Reason"] for row in screening)
    assert all(row["Authors_Conclusions"] == "Pending full-text review" for row in screening)
    assert all(row["Researcher_Synthesis"] == "Pending human review" for row in screening)


def test_local_candidate_corpus_audit_uses_correct_denominators() -> None:
    audit = json.loads(
        (CORPUS / "local-candidate-corpus-audit.json").read_text(encoding="utf-8")
    )

    assert audit["raw_records"] == 144
    assert audit["deduplicated_works"] == 139
    assert audit["duplicate_title_groups"] == 5
    assert audit["verification_after_title_grouping"] == {
        "source_label_verified": 127,
        "source_label_partial": 11,
        "source_label_unverified": 1,
    }
    assert audit["input_sha256"] == (
        "df21d7ea6b9d664967fd6c3981b884ff9e4c7a74bf8ca629c6a80e0483b4d23c"
    )
    assert audit["input_source_locator"]["repository_commit"] == (
        "3659de33c569d9cd107133a74372c24364f98048"
    )
    assert audit["drive_xlsx_binding_status"] == "Not established; import blocked"
    assert audit["declared_counts_match_actual"] is True
    assert audit["acl_title_overlap"] == 0
    assert audit["native_workbook"]["paper_rows"] == 6
    assert audit["native_workbook"]["overlap_with_local_candidates"] == 4


def test_local_candidate_audit_fails_closed_on_declared_count_mismatch(
    tmp_path: Path,
) -> None:
    source = json.loads(MODULE.LOCAL_CANDIDATE_CORPUS.read_text(encoding="utf-8"))
    source["totalSources"] += 1
    path = tmp_path / "candidate.json"
    path.write_text(json.dumps(source), encoding="utf-8")

    with pytest.raises(ValueError, match="declared candidate counts do not match"):
        MODULE.local_candidate_audit([], source_path=path)


def test_local_candidate_audit_uses_conservative_duplicate_status(
    tmp_path: Path,
) -> None:
    fixture = {
        "totalSources": 3,
        "verified": 1,
        "partial": 1,
        "unverified": 1,
        "sources": [
            {"title": "Same work", "year": "2025", "verification": "VERIFIED_ONLINE"},
            {"title": "Same work", "year": "2025", "verification": "PARTIALLY_VERIFIED"},
            {"title": "Other", "year": "2024", "verification": "COULD_NOT_VERIFY"},
        ],
    }
    path = tmp_path / "candidate.json"
    path.write_text(json.dumps(fixture), encoding="utf-8")

    audit = MODULE.local_candidate_audit([], source_path=path)

    assert audit["verification_after_title_grouping"] == {
        "source_label_verified": 0,
        "source_label_partial": 1,
        "source_label_unverified": 1,
    }


def test_hash_bound_capture_loader_rejects_tampering(tmp_path: Path) -> None:
    capture = {"schema_version": "Example-v1", "status": "Captured"}
    content = (json.dumps(capture, indent=2) + "\n").encode()
    path = tmp_path / "capture.json"
    path.write_bytes(content)
    expected_hash = hashlib.sha256(content).hexdigest()

    assert MODULE.load_hash_bound_json(path, expected_hash, "Example-v1") == capture
    path.write_text('{"schema_version":"Example-v1","status":"changed"}\n')
    with pytest.raises(ValueError, match="capture hash mismatch"):
        MODULE.load_hash_bound_json(path, expected_hash, "Example-v1")


def test_conflicting_strong_identifiers_do_not_merge() -> None:
    occurrences = [
        MODULE.Occurrence(
            1,
            "Latest Research Papers",
            "",
            "Shared title",
            "https://arxiv.org/abs/2501.00001",
            "2025",
            "arXiv 2025",
            "",
            {},
        ),
        MODULE.Occurrence(
            2,
            "Latest Research Papers",
            "",
            "Shared title",
            "https://arxiv.org/abs/2501.00002",
            "2025",
            "arXiv 2025",
            "",
            {},
        ),
    ]

    with pytest.raises(ValueError, match="conflicting strong identifiers"):
        MODULE.build_works(occurrences)


def test_missing_taxonomy_marker_is_not_a_sheet_formula_prefix() -> None:
    assert MODULE.plain_cell("-") == ""
    occurrences = MODULE.parse_readme(
        """## Taxonomy
### Interaction
| Title | Date & Code | Interaction Types | Interaction Variant |
| --- | --- | --- | --- |
| [Example](https://arxiv.org/abs/2501.00003) | 2025/01 | Collaboration | - |
"""
    )
    rows = MODULE.native_paper_rows(MODULE.build_works(occurrences))
    assert "-" not in rows[0]["Taxonomy_Tags"].split("; ")
    assert not rows[0]["Taxonomy_Tags"].startswith(("=", "+", "-", "@"))
    with pytest.raises(ValueError, match="spreadsheet formula prefix"):
        MODULE.validate_sheet_safe_rows([{"Title": "=IMPORTXML('x','y')"}])


def test_native_workbook_snapshot_and_staging_are_append_only() -> None:
    snapshot = json.loads(
        (CORPUS / "native-workbook-snapshot-2026-08-15.json").read_text(encoding="utf-8")
    )
    expected_rows = {
        "Papers": 6,
        "Search_Log": 6,
        "Screening": 6,
        "Taxonomy_and_Gaps": 8,
        "Resources": 12,
        "Controlled_Lists": 11,
    }

    assert snapshot["spreadsheet_alias"] == "NATIVE-WORKBOOK-PRIVATE-01"
    assert snapshot["spreadsheet_locator"] == "private-binding://native-literature-workbook"
    assert snapshot["identity_withheld_from_public_artifacts"] is True
    assert snapshot["data_rows"] == expected_rows
    assert snapshot["write_status"] == "Not written; read-only snapshot"
    assert len(snapshot["headers"]["Papers"]) == 36
    assert snapshot["capture_evidence"]["hash_verified"] is True
    assert snapshot["append_gate"]["live_append_ready"] is False
    assert snapshot["append_gate"]["table_metadata_status"] == (
        "Unavailable from connector; live append blocked"
    )
    for sheet in snapshot["sheet_captures"].values():
        assert len(sheet["schema_sha256"]) == 64
        assert len(sheet["values_sha256"]) == 64
        assert len(sheet["validation_sha256"]) == 64
        assert len(sheet["table_evidence_sha256"]) == 64

    paper_rows = _read_csv("native-papers-append-staging.csv")
    screening_rows = _read_csv("native-screening-append-staging.csv")
    search_rows = _read_csv("native-search-log-append-staging.csv")
    assert len(paper_rows) == 116
    assert len(screening_rows) == 116
    assert len(search_rows) == 1
    assert list(paper_rows[0]) == snapshot["headers"]["Papers"]
    assert list(screening_rows[0]) == snapshot["headers"]["Screening"]
    assert list(search_rows[0]) == snapshot["headers"]["Search_Log"]
    assert search_rows[0]["Query_ID"] == "ACL-CORPUS-001"
    assert all(row["Inclusion_Decision"] == "Pending human title/abstract review" for row in paper_rows)
    assert all(not row["SQ_Map"] for row in paper_rows)
    assert all(not row["Plan_Map"] for row in paper_rows)
    assert all("Provisional machine suggestion" in row["Follow_Up"] for row in paper_rows)
    assert all(row["Identity_Verified"] == "Pending" for row in screening_rows)
    assert all(not row["Reviewer"] and not row["Review_Date"] for row in screening_rows)
    MODULE.validate_sheet_safe_rows(paper_rows)
    MODULE.validate_sheet_safe_rows(screening_rows)
    MODULE.validate_sheet_safe_rows(search_rows)

    preflight = json.loads(
        (CORPUS / "native-append-preflight.json").read_text(encoding="utf-8")
    )
    assert preflight["offline_staging_lossless"] is True
    assert preflight["idempotency_guard_enabled"] is True
    assert preflight["live_append_ready"] is False
    assert preflight["staged_counts"] == {
        "Papers": 116,
        "Screening": 116,
        "Search_Log": 1,
    }
    assert preflight["expected_post_append_counts"] == {
        "Papers": 122,
        "Search_Log": 7,
        "Screening": 122,
        "Taxonomy_and_Gaps": 8,
        "Resources": 12,
        "Controlled_Lists": 11,
    }


def test_public_acl_artifacts_do_not_expose_the_private_native_sheet_identifier() -> None:
    public_paths = [
        ROOT / "scripts/build_acl2026_corpus.py",
        *sorted(CORPUS.rglob("*")),
    ]
    for path in public_paths:
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        locator = path.relative_to(ROOT).as_posix()
        assert "https://docs.google.com/spreadsheets/d/" not in text, locator
        assert not re.search(
            r'"spreadsheet_id"\s*:\s*"[A-Za-z0-9_-]{20,}"', text
        ), locator


def test_chapter2_anchors_are_primary_source_bounded() -> None:
    anchors = (CORPUS / "chapter2-source-anchors.md").read_text(encoding="utf-8")
    key_sources = _read_csv("conservative-key-sources.csv")

    assert "pp. 36337–36338, Section 3.2 and Table 1" in anchors
    assert "pp. 36341–36342, Section 3.6 and Table 3" in anchors
    assert MODULE.SOURCE_COMMIT in anchors
    assert len(key_sources) == 12
    assert key_sources[0]["Title"] == (
        "LLM-Based Human-Agent Collaboration and Interaction Systems: A Survey"
    )
    assert all(row["Human_Review_Status"] == "Pending" for row in key_sources)
    assert all(
        row["Evidence_Level"] == "Pinned repository title/taxonomy metadata only"
        for row in key_sources
    )
    assert all("Do not attribute a finding" in row["Claim_Boundary"] for row in key_sources)


def test_foundations_live_query_is_bounded_and_not_formal_ql_execution() -> None:
    record = json.loads(
        (CORPUS / "foundations-query-test-2026-08-15.json").read_text(
            encoding="utf-8"
        )
    )

    assert record["exact_query"] == (
        '("agentic AI" OR "autonomous agent" OR "LLM agent") AND '
        '("human-AI collaboration" OR "human-AI interaction") AND '
        "(variability OR variant)"
    )
    assert record["observation_date"] == "2026-08-15"
    assert record["time_zone"] == "Asia/Jerusalem (UTC+03:00 at capture)"
    assert record["interface_locale"] == "English (hl=en)"
    assert record["result_summary_as_displayed"] == "About 2,500 results (0.25 sec)"
    assert record["captcha_observed"] is False
    assert record["authentication_block_observed"] is False
    assert record["export_performed"] is False
    assert record["screening_performed"] is False
    assert "not QL-01" in record["formal_query_boundary"]
    assert "not confirmed" in record["query_status"]
    assert record["evidence_status"] == "Unverified operator observation"
    assert record["readiness_eligible"] is False
    assert len(record["capture_input_sha256"]) == 64


def test_manifest_binds_all_external_and_local_inputs() -> None:
    manifest = json.loads((CORPUS / "source-manifest.json").read_text(encoding="utf-8"))

    inputs = manifest["source_inputs"]
    assert set(inputs) == {
        "pinned_repository_readme",
        "local_candidate_corpus",
        "native_workbook_capture",
        "foundations_query_capture",
    }
    assert all(len(item["sha256"]) == 64 for item in inputs.values())
    assert inputs["native_workbook_capture"]["evidence_status"].startswith(
        "Verified live read"
    )
    assert inputs["foundations_query_capture"]["evidence_status"] == (
        "Unverified operator observation"
    )
