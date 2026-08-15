#!/usr/bin/env python3
"""Build the bounded ACL-2026 human-agent literature corpus.

The source is an immutable GitHub README revision associated with the ACL 2026
survey by Zou et al.  The builder preserves every in-scope README occurrence,
deduplicates occurrences into works, and produces a machine metadata screen.
It deliberately does not claim that a human title/abstract or full-text screen
has happened.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import re
import urllib.request
from collections import Counter, defaultdict
from collections.abc import Iterable
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "literature/acl2026-human-agent-corpus"
LOCAL_CANDIDATE_CORPUS = ROOT / "literature/verified-research-corpus-2026-08-12.json"
EVIDENCE_INPUT_DIR = OUTPUT_DIR / "evidence-inputs"
NATIVE_WORKBOOK_CAPTURE = (
    EVIDENCE_INPUT_DIR / "native-workbook-connector-capture-2026-08-15.json"
)
FOUNDATIONS_QUERY_CAPTURE = (
    EVIDENCE_INPUT_DIR / "foundations-query-observation-capture-2026-08-15.json"
)

LOCAL_CANDIDATE_SHA256 = (
    "df21d7ea6b9d664967fd6c3981b884ff9e4c7a74bf8ca629c6a80e0483b4d23c"
)
LOCAL_CANDIDATE_SOURCE_COMMIT = "3659de33c569d9cd107133a74372c24364f98048"
NATIVE_WORKBOOK_CAPTURE_SHA256 = (
    "68242fa0bad8c71ff13c98f13263fa42d237e8d1cf46f5a46280369127c65346"
)
FOUNDATIONS_QUERY_CAPTURE_SHA256 = (
    "c926c9912f948602e8361bc19e6250a46ee80aeeef2ef3a4396dbfa0e7ea3d58"
)

SOURCE_COMMIT = "7b3ba9deefe99172748582f6025d995ccc2a6f86"
SOURCE_README_URL = (
    "https://raw.githubusercontent.com/HenryPengZou/"
    "Awesome-Human-Agent-Collaboration-Interaction-Systems/"
    f"{SOURCE_COMMIT}/README.md"
)
SOURCE_REPOSITORY_URL = (
    "https://github.com/HenryPengZou/"
    "Awesome-Human-Agent-Collaboration-Interaction-Systems"
)
SOURCE_README_SHA256 = "3410215aad4085e4caf15b1217e19825da988bc7e5189fe8baa870fa2794bf5c"
SURVEY_URL = "https://aclanthology.org/2026.findings-acl.1811/"
SURVEY_DOI = "10.18653/v1/2026.findings-acl.1811"

EXPECTED_COUNTS = {
    "raw_occurrences": 525,
    "distinct_works": 116,
    "latest_research_works": 106,
    "application_works": 57,
    "taxonomy_works": 90,
}
EXPECTED_TAXONOMY_ROWS = {
    "Human Feedback": 89,
    "Interaction": 89,
    "Orchestration": 90,
    "Communication": 89,
}

NATIVE_WORKBOOK_ALIAS = "NATIVE-WORKBOOK-PRIVATE-01"
NATIVE_WORKBOOK_LOCATOR = "private-binding://native-literature-workbook"
NATIVE_WORKBOOK_HEADERS = {
    "Papers": [
        "Paper_ID",
        "Title",
        "Authors",
        "Year",
        "Venue",
        "Publication_Type",
        "DOI",
        "URL",
        "Database",
        "Query_ID",
        "Search_Date",
        "Access_or_License",
        "Objective",
        "Domain",
        "Study_Design",
        "Data_or_Corpus",
        "Sample",
        "Artifact_or_System",
        "Baseline",
        "Metrics",
        "Main_Results",
        "Authors_Conclusions",
        "Authors_Limitations",
        "Taxonomy_Tags",
        "SQ_Map",
        "Plan_Map",
        "Use_Case_Map",
        "Gap_Evidence",
        "Quality_Rating",
        "Transferability",
        "Researcher_Synthesis",
        "Inclusion_Decision",
        "Exclusion_Reason",
        "Follow_Up",
        "Reviewer",
        "Review_Date",
    ],
    "Search_Log": [
        "Query_ID",
        "Prepared_Date",
        "Database",
        "Concept_Group",
        "Search_String",
        "Primary_Window",
        "Older_Seminal_Rule",
        "Status",
        "Results_Returned",
        "Results_Screened",
        "Added_to_Papers",
        "Searcher",
        "Execution_Date",
        "Notes",
    ],
    "Screening": [
        "Paper_ID",
        "Title",
        "Identity_Verified",
        "Deduplicated",
        "Title_Abstract_Decision",
        "Full_Text_Decision",
        "Exclusion_Reason",
        "Reviewer",
        "Review_Date",
        "Evidence_or_Link",
        "Notes",
    ],
    "Taxonomy_and_Gaps": [
        "Category_ID",
        "Taxonomy_Category",
        "SQ_Map",
        "Evidence_Need",
        "Current_Coverage_Count",
        "Coverage_Assessment",
        "Gap_Status",
        "Linked_Paper_IDs",
        "Study_Contribution_Link",
        "Next_Search_Action",
        "Owner",
        "Due_Date",
    ],
    "Resources": [
        "Resource_ID",
        "Name",
        "Type",
        "URL",
        "Research_Evidence",
        "Allowed_Use",
        "License_or_Access",
        "Repository_Source",
        "Notes",
    ],
    "Controlled_Lists": [
        "Publication_Type",
        "Database",
        "Domain",
        "Study_Design",
        "SQ_Map",
        "Plan_Map",
        "Quality_Rating",
        "Transferability",
        "Inclusion_Decision",
        "Yes_No",
        "Gap_Status",
        "Search_Status",
    ],
}
NATIVE_WORKBOOK_DATA_ROWS = {
    "Papers": 6,
    "Search_Log": 6,
    "Screening": 6,
    "Taxonomy_and_Gaps": 8,
    "Resources": 12,
    "Controlled_Lists": 11,
}

# These title groups are reviewed publisher/preprint aliases present in the
# pinned source. Any other same-title group with distinct strong identifiers is
# rejected rather than silently collapsed.
REVIEWED_STRONG_ID_ALIASES = {
    "ask before plan proactive language agents for real world planning": frozenset(
        {"acl:2024.findings-emnlp.636", "arxiv:2406.12639"}
    ),
    "into the unknown unknowns engaged human learning through participation in language model agent conversations": frozenset(
        {"acl:2024.emnlp-main.554", "arxiv:2408.15232"}
    ),
    "investigating agency of llms in human ai collaboration tasks": frozenset(
        {"acl:2024.eacl-long.119", "arxiv:2305.12815"}
    ),
    "metagpt meta programming for a multi agent collaborative framework": frozenset(
        {"arxiv:2308.00352", "openreview:vtmbagcn7o"}
    ),
    "mindagent emergent gaming interaction": frozenset(
        {"acl:2024.findings-naacl.200", "arxiv:2309.09971"}
    ),
    "partnr a benchmark for planning and reasoning in embodied multi agent tasks": frozenset(
        {"arxiv:2411.00081", "openreview:t5qlrrhyl1"}
    ),
    "sotopia interactive evaluation for social intelligence in language agents": frozenset(
        {"arxiv:2310.11667", "openreview:mm7vurba4r"}
    ),
}

IN_SCOPE_SECTIONS = {
    "Latest Research Papers",
    "Applications, Datasets & Benchmarks",
    "Taxonomy",
}
TAXONOMY_BRANCHES = set(EXPECTED_TAXONOMY_ROWS)
TAXONOMY_FIELDS = (
    "Feedback_Type",
    "Feedback_Subtype",
    "Feedback_Granularity",
    "Feedback_Phase",
    "Interaction_Types",
    "Interaction_Variant",
    "Orchestration_Strategy",
    "Orchestration_Synchronization",
    "Communication_Structure",
    "Communication_Mode",
)

BULLET_RE = re.compile(
    r"^- \*\*\[(?P<date>[^\]]+)\]\*\*\s+"
    r"\[(?P<venue>[^\]]+)\]\s+"
    r"\[(?P<title>[^\]]+)\]\((?P<url>https?://[^)]+)\)"
)
LINK_RE = re.compile(r"(?<!!)\[([^\]]+)\]\((https?://[^)]+)\)")
NON_ALNUM_RE = re.compile(r"[^a-z0-9]+")


@dataclass(frozen=True)
class Occurrence:
    source_line: int
    source_section: str
    source_subsection: str
    title: str
    primary_url: str
    repo_date: str
    venue_label: str
    taxonomy_branch: str
    taxonomy: dict[str, str] = field(default_factory=dict)

    @property
    def normalized_title(self) -> str:
        return normalize_title(self.title)

    @property
    def strong_id(self) -> str:
        return strong_identifier(self.primary_url, self.normalized_title)


@dataclass(frozen=True)
class Work:
    work_id: str
    title: str
    primary_url: str
    year: str
    venue_label: str
    strong_identifiers: str
    source_sections: str
    application_categories: str
    taxonomy_branches: str
    source_line_refs: str
    occurrence_count: int
    taxonomy_conflict: str
    taxonomy: dict[str, str]
    occurrence_indexes: tuple[int, ...]


def normalize_title(value: str) -> str:
    return NON_ALNUM_RE.sub(" ", value.lower()).strip()


def load_hash_bound_json(
    path: Path, expected_sha256: str, expected_schema_version: str
) -> dict[str, object]:
    """Load a captured JSON input only when both bytes and schema are exact."""

    content = path.read_bytes()
    actual_sha256 = hashlib.sha256(content).hexdigest()
    if actual_sha256 != expected_sha256:
        raise ValueError(
            f"capture hash mismatch for {path}: expected {expected_sha256}, "
            f"got {actual_sha256}"
        )
    data = json.loads(content)
    if not isinstance(data, dict) or data.get("schema_version") != expected_schema_version:
        raise ValueError(
            f"capture schema mismatch for {path}: expected {expected_schema_version}"
        )
    return data


def clean_heading(value: str) -> str:
    value = value.strip()
    match = re.search(r"[A-Za-z0-9]", value)
    return value[match.start() :].strip() if match else value


def strong_identifier(url: str, normalized_title: str) -> str:
    arxiv = re.search(r"arxiv\.org/(?:abs|pdf)/(\d{4}\.\d{4,5})(?:v\d+)?", url, re.I)
    if arxiv:
        return f"arxiv:{arxiv.group(1)}"
    openreview = re.search(r"openreview\.net/forum\?id=([^&#]+)", url, re.I)
    if openreview:
        return f"openreview:{openreview.group(1).lower()}"
    acl = re.search(r"aclanthology\.org/([^/?#]+)", url, re.I)
    if acl:
        return f"acl:{acl.group(1).lower()}"
    doi = re.search(r"doi\.org/(10\.[^?#]+)", url, re.I)
    if doi:
        return f"doi:{doi.group(1).rstrip('/').lower()}"
    pubmed = re.search(r"pubmed\.ncbi\.nlm\.nih\.gov/(\d+)", url, re.I)
    if pubmed:
        return f"pubmed:{pubmed.group(1)}"
    return f"title:{normalized_title}"


def split_table_row(line: str) -> list[str]:
    return [cell.strip() for cell in line.strip().strip("|").split("|")]


def plain_cell(value: str) -> str:
    value = re.sub(r"!\[[^\]]*\]\([^)]+\)", "", value)
    value = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", value)
    value = value.replace("***", "").replace("**", "").replace("`", "")
    value = " ".join(value.split())
    return "" if value in {"-", "–", "—"} else value


def header_to_field(value: str) -> str:
    normalized = re.sub(r"[^a-z0-9]+", "_", value.lower()).strip("_")
    mapping = {
        "feedback_type": "Feedback_Type",
        "feedback_subtype": "Feedback_Subtype",
        "feedback_granularity": "Feedback_Granularity",
        "feedback_phase": "Feedback_Phase",
        "interaction_types": "Interaction_Types",
        "interaction_type": "Interaction_Types",
        "interaction_variant": "Interaction_Variant",
        "orchestration_strategy": "Orchestration_Strategy",
        "orchestration_synchronization": "Orchestration_Synchronization",
        "communication_structure": "Communication_Structure",
        "communication_mode": "Communication_Mode",
    }
    return mapping.get(normalized, normalized)


def parse_readme(text: str) -> list[Occurrence]:
    occurrences: list[Occurrence] = []
    section = ""
    subsection = ""
    table_headers: list[str] = []

    for line_no, line in enumerate(text.splitlines(), start=1):
        if line.startswith("## "):
            section = clean_heading(line[3:])
            subsection = ""
            table_headers = []
            continue
        if line.startswith("### "):
            subsection = clean_heading(line[4:])
            table_headers = []
            continue
        if section not in IN_SCOPE_SECTIONS:
            continue

        bullet = BULLET_RE.match(line)
        if bullet and section in {
            "Latest Research Papers",
            "Applications, Datasets & Benchmarks",
        }:
            occurrences.append(
                Occurrence(
                    source_line=line_no,
                    source_section=section,
                    source_subsection=subsection,
                    title=bullet.group("title").strip(),
                    primary_url=bullet.group("url").strip(),
                    repo_date=bullet.group("date").strip(),
                    venue_label=bullet.group("venue").strip(),
                    taxonomy_branch="",
                )
            )
            continue

        if section != "Taxonomy" or subsection not in TAXONOMY_BRANCHES:
            continue
        if line.startswith("| Title |"):
            table_headers = split_table_row(line)
            continue
        if not line.startswith("|") or not table_headers or re.match(r"^\|\s*:?-+", line):
            continue

        cells = split_table_row(line)
        if len(cells) != len(table_headers):
            raise ValueError(
                f"README line {line_no}: expected {len(table_headers)} table cells, got {len(cells)}"
            )
        link = LINK_RE.search(cells[0])
        if not link:
            continue
        taxonomy: dict[str, str] = {}
        for header, cell in zip(table_headers[2:], cells[2:], strict=True):
            field_name = header_to_field(header)
            if field_name in TAXONOMY_FIELDS:
                taxonomy[field_name] = plain_cell(cell)
        occurrences.append(
            Occurrence(
                source_line=line_no,
                source_section=section,
                source_subsection=subsection,
                title=link.group(1).strip(),
                primary_url=link.group(2).strip(),
                repo_date=plain_cell(cells[1]),
                venue_label="",
                taxonomy_branch=subsection,
                taxonomy=taxonomy,
            )
        )

    return occurrences


class DisjointSet:
    def __init__(self, size: int) -> None:
        self.parent = list(range(size))

    def find(self, item: int) -> int:
        while self.parent[item] != item:
            self.parent[item] = self.parent[self.parent[item]]
            item = self.parent[item]
        return item

    def union(self, left: int, right: int) -> None:
        root_left = self.find(left)
        root_right = self.find(right)
        if root_left != root_right:
            self.parent[root_right] = root_left


def _join(values: Iterable[str]) -> str:
    return "; ".join(sorted({value for value in values if value}))


def build_works(occurrences: list[Occurrence]) -> list[Work]:
    identifiers_by_title: dict[str, set[str]] = defaultdict(set)
    for occurrence in occurrences:
        if not occurrence.strong_id.startswith("title:"):
            identifiers_by_title[occurrence.normalized_title].add(occurrence.strong_id)
    for title, identifiers in identifiers_by_title.items():
        if len(identifiers) < 2:
            continue
        if frozenset(identifiers) != REVIEWED_STRONG_ID_ALIASES.get(title):
            raise ValueError(
                "conflicting strong identifiers for title "
                f"{title!r}: {sorted(identifiers)}"
            )

    dsu = DisjointSet(len(occurrences))
    by_title: dict[str, int] = {}
    by_identifier: dict[str, int] = {}
    for index, occurrence in enumerate(occurrences):
        for key, index_map in (
            (occurrence.normalized_title, by_title),
            (occurrence.strong_id, by_identifier),
        ):
            if key in index_map:
                dsu.union(index, index_map[key])
            else:
                index_map[key] = index

    components: dict[int, list[int]] = defaultdict(list)
    for index in range(len(occurrences)):
        components[dsu.find(index)].append(index)

    section_priority = {
        "Latest Research Papers": 0,
        "Taxonomy": 1,
        "Applications, Datasets & Benchmarks": 2,
    }
    works: list[Work] = []
    for indexes in components.values():
        members = [occurrences[index] for index in indexes]
        preferred = min(
            members,
            key=lambda item: (section_priority[item.source_section], item.source_line),
        )
        titles = sorted({item.normalized_title for item in members})
        identifiers = sorted({item.strong_id for item in members})
        identity_material = "\n".join(identifiers + titles).encode("utf-8")
        work_id = f"ACL26-W-{hashlib.sha256(identity_material).hexdigest()[:12].upper()}"
        taxonomy_values: dict[str, str] = {}
        conflict = False
        for field_name in TAXONOMY_FIELDS:
            values = sorted({item.taxonomy.get(field_name, "") for item in members} - {""})
            taxonomy_values[field_name] = " || ".join(values)
            conflict = conflict or len(values) > 1
        year_match = re.search(r"\b(20\d{2})\b", preferred.repo_date)
        works.append(
            Work(
                work_id=work_id,
                title=preferred.title,
                primary_url=preferred.primary_url,
                year=year_match.group(1) if year_match else "",
                venue_label=preferred.venue_label,
                strong_identifiers=_join(identifiers),
                source_sections=_join(item.source_section for item in members),
                application_categories=_join(
                    item.source_subsection
                    for item in members
                    if item.source_section == "Applications, Datasets & Benchmarks"
                ),
                taxonomy_branches=_join(item.taxonomy_branch for item in members),
                source_line_refs=_join(f"README:L{item.source_line}" for item in members),
                occurrence_count=len(members),
                taxonomy_conflict="Yes" if conflict else "No",
                taxonomy=taxonomy_values,
                occurrence_indexes=tuple(indexes),
            )
        )
    return sorted(works, key=lambda item: (normalize_title(item.title), item.work_id))


def machine_screen(work: Work) -> dict[str, str]:
    title = normalize_title(work.title)
    patterns = {
        "SQ1": (
            "uncertainty",
            "clarif",
            "oversight",
            "interrupt",
            "intervention",
            "human in the loop",
            "controlled autonomy",
            "proactive",
            "verification",
            "attentive support",
        ),
        "SQ2": (
            "feedback",
            "correction",
            "preference",
            "memory",
            "personaliz",
            "runtime enforcement",
            "co edit",
            "human control",
            "critique",
        ),
        "SQ3": (
            "benchmark",
            "evaluat",
            "cross domain",
            "domain specific",
            "generaliz",
            "transfer",
            "real world",
            "configurable human participation",
        ),
    }
    sqs = [sq for sq, terms in patterns.items() if any(term in title for term in terms)]
    chapter_map = ["2.3 Human-agent collaboration design space"]
    if "SQ1" in sqs:
        chapter_map.append("2.4 Selective intervention and bounded oversight")
    if "SQ2" in sqs:
        chapter_map.append("2.5 Feedback, judgment, governance, and reuse")
    if "SQ3" in sqs:
        chapter_map.append("2.6 Evaluation and transfer")
    if len(sqs) >= 2:
        relevance = "Core candidate"
    elif sqs:
        relevance = "Relevant candidate"
    elif work.taxonomy_branches:
        relevance = "Contextual candidate"
    else:
        relevance = "Peripheral candidate"
    return {
        "Work_ID": work.work_id,
        "Title": work.title,
        "Primary_URL": work.primary_url,
        "Evidence_Basis": "Pinned repository title and taxonomy metadata only",
        "Identity_Status": "Identifier present; independent metadata verification pending",
        "Machine_Preliminary_Relevance": relevance,
        "SQ_Map": (
            f"Provisional machine suggestion: {'; '.join(sqs)}"
            if sqs
            else "Provisional machine suggestion: Unmapped; canonical RQ wording unresolved"
        ),
        "Chapter2_Map": "; ".join(chapter_map),
        "Machine_Screen_Status": "Complete",
        "Human_Review_Status": "Pending",
        "Inclusion_Decision": "Pending human title/abstract review",
        "Exclusion_Reason": "",
        "Full_Text_Status": "Pending",
        "Authors_Conclusions": "Pending full-text review",
        "Researcher_Synthesis": "Pending human review",
        "Reviewer": "",
        "Review_Date": "",
    }


def occurrence_rows(
    occurrences: list[Occurrence], works: list[Work]
) -> list[dict[str, str | int]]:
    index_to_work: dict[int, str] = {}
    for work in works:
        for index in work.occurrence_indexes:
            index_to_work[index] = work.work_id
    rows: list[dict[str, str | int]] = []
    for index, occurrence in enumerate(occurrences):
        row: dict[str, str | int] = {
            "Occurrence_ID": f"ACL26-O-{index + 1:04d}",
            "Work_ID": index_to_work[index],
            "Source_Commit": SOURCE_COMMIT,
            "Source_Line": occurrence.source_line,
            "Source_Section": occurrence.source_section,
            "Source_Subsection": occurrence.source_subsection,
            "Title_As_Listed": occurrence.title,
            "Primary_URL_As_Listed": occurrence.primary_url,
            "Strong_Identifier": occurrence.strong_id,
            "Repository_Date": occurrence.repo_date,
            "Venue_Label": occurrence.venue_label,
            "Taxonomy_Branch": occurrence.taxonomy_branch,
        }
        row.update({field_name: occurrence.taxonomy.get(field_name, "") for field_name in TAXONOMY_FIELDS})
        rows.append(row)
    return rows


def work_rows(works: list[Work]) -> list[dict[str, str | int]]:
    rows: list[dict[str, str | int]] = []
    for work in works:
        row: dict[str, str | int] = {
            "Work_ID": work.work_id,
            "Title": work.title,
            "Year_As_Listed": work.year,
            "Venue_Label_As_Listed": work.venue_label,
            "Primary_URL": work.primary_url,
            "Strong_Identifiers": work.strong_identifiers,
            "Source_Commit": SOURCE_COMMIT,
            "Source_Sections": work.source_sections,
            "Application_Categories": work.application_categories,
            "Taxonomy_Branches": work.taxonomy_branches,
            "Source_Line_Refs": work.source_line_refs,
            "Occurrence_Count": work.occurrence_count,
            "Taxonomy_Value_Conflict": work.taxonomy_conflict,
        }
        row.update(work.taxonomy)
        rows.append(row)
    return rows


def local_candidate_audit(
    acl_works: list[Work],
    source_path: Path = LOCAL_CANDIDATE_CORPUS,
    native_capture: dict[str, object] | None = None,
) -> dict[str, object]:
    source_bytes = source_path.read_bytes()
    input_sha256 = hashlib.sha256(source_bytes).hexdigest()
    if (
        source_path.resolve() == LOCAL_CANDIDATE_CORPUS.resolve()
        and input_sha256 != LOCAL_CANDIDATE_SHA256
    ):
        raise ValueError(
            "candidate corpus hash mismatch: "
            f"expected {LOCAL_CANDIDATE_SHA256}, got {input_sha256}"
        )
    data = json.loads(source_bytes)
    sources = data["sources"]
    raw_statuses = Counter(str(source["verification"]) for source in sources)
    declared_counts = {
        "total": data["totalSources"],
        "verified": data["verified"],
        "partial": data["partial"],
        "unverified": data["unverified"],
    }
    actual_counts = {
        "total": len(sources),
        "verified": raw_statuses["VERIFIED_ONLINE"],
        "partial": raw_statuses["PARTIALLY_VERIFIED"],
        "unverified": raw_statuses["COULD_NOT_VERIFY"],
    }
    if declared_counts != actual_counts:
        raise ValueError(
            "declared candidate counts do not match actual records: "
            f"declared={declared_counts}, actual={actual_counts}"
        )

    groups: dict[str, list[dict[str, object]]] = defaultdict(list)
    for source in sources:
        normalized_title = normalize_title(str(source["title"]))
        if not normalized_title:
            raise ValueError("candidate corpus contains a record with no normalized title")
        groups[normalized_title].append(source)
    strength = {"COULD_NOT_VERIFY": 0, "PARTIALLY_VERIFIED": 1, "VERIFIED_ONLINE": 2}
    merged_statuses: list[str] = []
    duplicate_groups: list[dict[str, object]] = []
    for group in groups.values():
        states = [str(item["verification"]) for item in group]
        unknown_states = set(states) - set(strength)
        if unknown_states:
            raise ValueError(
                f"candidate corpus contains unknown verification states: {unknown_states}"
            )
        # A title group is only as well verified as its weakest source record.
        weakest = min(states, key=strength.__getitem__)
        merged_statuses.append(weakest)
        if len(group) > 1:
            duplicate_groups.append(
                {
                    "normalized_title": normalize_title(str(group[0]["title"])),
                    "count": len(group),
                    "titles": sorted({str(item["title"]) for item in group}),
                    "years": sorted({str(item["year"]) for item in group}),
                    "verification_states": sorted(
                        {str(item["verification"]) for item in group}
                    ),
                }
            )
    statuses = Counter(merged_statuses)
    acl_titles = {normalize_title(work.title) for work in acl_works}
    local_titles = set(groups)
    if native_capture is None:
        native_capture = load_hash_bound_json(
            NATIVE_WORKBOOK_CAPTURE,
            NATIVE_WORKBOOK_CAPTURE_SHA256,
            "VEGO-NativeWorkbookConnectorCapture-v1",
        )
    sheet_captures = native_capture["sheet_captures"]
    if not isinstance(sheet_captures, dict):
        raise ValueError("native workbook capture has no sheet mapping")
    paper_capture = sheet_captures["Papers"]
    if not isinstance(paper_capture, dict):
        raise ValueError("native workbook Papers capture is invalid")
    captured_columns = paper_capture["sanitized_value_columns"]
    captured_rows = paper_capture["sanitized_values"]
    if not isinstance(captured_columns, list) or not isinstance(captured_rows, list):
        raise ValueError("native workbook Papers values are invalid")
    title_index = captured_columns.index("Title")
    native_titles = {
        normalize_title(str(row[title_index]))
        for row in captured_rows[1:]
        if isinstance(row, list) and row[title_index]
    }
    is_canonical_source = source_path.resolve() == LOCAL_CANDIDATE_CORPUS.resolve()
    verification_after_grouping = {
        "source_label_verified": statuses["VERIFIED_ONLINE"],
        "source_label_partial": statuses["PARTIALLY_VERIFIED"],
        "source_label_unverified": statuses["COULD_NOT_VERIFY"],
    }
    return {
        "schema_version": "VEGO-LocalCandidateCorpusAudit-v1",
        "source_path": (
            "literature/verified-research-corpus-2026-08-12.json"
            if is_canonical_source
            else str(source_path)
        ),
        "input_sha256": input_sha256,
        "input_source_locator": {
            "repository_path": "literature/verified-research-corpus-2026-08-12.json",
            "repository_commit": (
                LOCAL_CANDIDATE_SOURCE_COMMIT if is_canonical_source else None
            ),
        },
        "drive_xlsx_binding_status": "Not established; import blocked",
        "source_declared_counts": declared_counts,
        "source_actual_counts": actual_counts,
        "declared_counts_match_actual": True,
        "raw_records": len(sources),
        "deduplicated_works": len(groups),
        "duplicate_title_groups": len(duplicate_groups),
        "duplicate_groups": sorted(duplicate_groups, key=lambda item: str(item["normalized_title"])),
        "verification_after_title_grouping": verification_after_grouping,
        "verification_after_dedup": {
            "verified": verification_after_grouping["source_label_verified"],
            "partial": verification_after_grouping["source_label_partial"],
            "unverified": verification_after_grouping["source_label_unverified"],
        },
        "acl_title_overlap": len(acl_titles & local_titles),
        "native_workbook": {
            "spreadsheet_alias": NATIVE_WORKBOOK_ALIAS,
            "spreadsheet_locator": NATIVE_WORKBOOK_LOCATOR,
            "identity_withheld_from_public_artifacts": True,
            "snapshot_date": "2026-08-15",
            "paper_rows": paper_capture["data_rows"],
            "overlap_with_local_candidates": len(native_titles & local_titles),
            "status": native_capture["evidence_status"],
        },
        "claim_boundary": (
            "139 is the number of normalized-title works, not the number independently verified. "
            "Conservative per-work aggregation uses the weakest source label in each title "
            "group; source labels are not independent bibliographic verification."
        ),
    }


def native_workbook_snapshot(
    capture: dict[str, object] | None = None,
) -> dict[str, object]:
    """Build a derived snapshot from the hash-verified read-only capture."""

    if capture is None:
        capture = load_hash_bound_json(
            NATIVE_WORKBOOK_CAPTURE,
            NATIVE_WORKBOOK_CAPTURE_SHA256,
            "VEGO-NativeWorkbookConnectorCapture-v1",
        )
    captures = capture["sheet_captures"]
    if not isinstance(captures, dict):
        raise ValueError("native workbook capture has no sheet mapping")
    data_rows: dict[str, int] = {}
    headers: dict[str, list[str]] = {}
    snapshot_sheets: dict[str, dict[str, object]] = {}
    for sheet_name, expected_headers in NATIVE_WORKBOOK_HEADERS.items():
        sheet = captures.get(sheet_name)
        if not isinstance(sheet, dict):
            raise ValueError(f"native workbook capture missing {sheet_name}")
        actual_headers = sheet.get("headers")
        if actual_headers != expected_headers:
            raise ValueError(f"native workbook header mismatch for {sheet_name}")
        data_rows[sheet_name] = int(sheet["data_rows"])
        headers[sheet_name] = list(actual_headers)
        snapshot_sheets[sheet_name] = {
            key: sheet[key]
            for key in (
                "sheet_id",
                "used_range",
                "grid_rows",
                "grid_columns",
                "frozen_rows",
                "data_rows",
                "schema_sha256",
                "values_sha256",
                "validation_sha256",
                "table_evidence_sha256",
                "connector_sheet_response_sha256",
                "validation_entry_count",
            )
        }
    if data_rows != NATIVE_WORKBOOK_DATA_ROWS:
        raise ValueError(
            f"native workbook row-count mismatch: expected {NATIVE_WORKBOOK_DATA_ROWS}, "
            f"got {data_rows}"
        )
    capture_append_gate = capture["append_gate"]
    if not isinstance(capture_append_gate, dict):
        raise ValueError("native workbook capture append gate is invalid")

    return {
        "schema_version": "VEGO-NativeLiteratureWorkbookSnapshot-v1",
        "spreadsheet_alias": NATIVE_WORKBOOK_ALIAS,
        "spreadsheet_locator": NATIVE_WORKBOOK_LOCATOR,
        "identity_withheld_from_public_artifacts": True,
        "title": "VEGO-AI PhD Literature Workbook v0.1",
        "locale": "en_GB",
        "time_zone": "Asia/Jerusalem",
        "captured_date": "2026-08-15",
        "captured_at_utc": capture["captured_at_utc"],
        "snapshot_scope": (
            "Hash-bound read-only metadata, exact used-range values, validations, headers, "
            "and row counts; only sanitized public identity fields are committed"
        ),
        "write_status": "Not written; read-only snapshot",
        "data_rows": data_rows,
        "headers": headers,
        "sheet_captures": snapshot_sheets,
        "capture_evidence": {
            "input_path": (
                "literature/acl2026-human-agent-corpus/evidence-inputs/"
                "native-workbook-connector-capture-2026-08-15.json"
            ),
            "sha256": NATIVE_WORKBOOK_CAPTURE_SHA256,
            "hash_verified": True,
            "evidence_status": capture["evidence_status"],
        },
        "append_gate": {
            "live_append_ready": False,
            "table_metadata_status": capture["table_metadata_status"],
            "reason": capture_append_gate["reason"],
        },
        "append_only_contract": {
            "existing_rows": "Preserve every existing row and field exactly",
            "staged_rows": "Append only after Ali review and a fresh live re-read",
            "formal_queries": "Do not change QL-01 through QL-05 from Protocol ready",
            "precondition": (
                "Abort if input hash, schema, row count, validation hash, value hash, "
                "or table-evidence status differs from this snapshot"
            ),
        },
    }


def _doi_from_identifiers(value: str) -> str:
    for identifier in value.split("; "):
        if identifier.startswith("doi:"):
            return identifier.removeprefix("doi:")
    return ""


def _taxonomy_tags(work: Work) -> str:
    values = [work.taxonomy_branches]
    values.extend(work.taxonomy[field_name] for field_name in TAXONOMY_FIELDS)
    return _join(value for value in values if plain_cell(value))


def native_paper_rows(works: list[Work]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for work in works:
        screen = machine_screen(work)
        values = {
            "Paper_ID": work.work_id,
            "Title": work.title,
            "Authors": "",
            "Year": work.year,
            "Venue": work.venue_label,
            "Publication_Type": "",
            "DOI": _doi_from_identifiers(work.strong_identifiers),
            "URL": work.primary_url,
            "Database": "Pinned ACL 2026 taxonomy repository",
            "Query_ID": "ACL-CORPUS-001",
            "Search_Date": "2026-08-15",
            "Access_or_License": "Public repository metadata; article access not assessed",
            "Objective": "Pending human review",
            "Domain": "",
            "Study_Design": "",
            "Data_or_Corpus": "",
            "Sample": "",
            "Artifact_or_System": "",
            "Baseline": "",
            "Metrics": "",
            "Main_Results": "Pending full-text review",
            "Authors_Conclusions": "Pending full-text review",
            "Authors_Limitations": "Pending full-text review",
            "Taxonomy_Tags": _taxonomy_tags(work),
            "SQ_Map": "",
            "Plan_Map": "",
            "Use_Case_Map": "",
            "Gap_Evidence": "Pending full-text review",
            "Quality_Rating": "Not assessed",
            "Transferability": "Not assessed",
            "Researcher_Synthesis": "Pending human review",
            "Inclusion_Decision": "Pending human title/abstract review",
            "Exclusion_Reason": "",
            "Follow_Up": (
                f"{screen['SQ_Map']}; verify identity, then complete blind "
                "title/abstract review"
            ),
            "Reviewer": "",
            "Review_Date": "",
        }
        rows.append({header: values[header] for header in NATIVE_WORKBOOK_HEADERS["Papers"]})
    return rows


def native_screening_rows(works: list[Work]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for work in works:
        values = {
            "Paper_ID": work.work_id,
            "Title": work.title,
            "Identity_Verified": "Pending",
            "Deduplicated": "Yes",
            "Title_Abstract_Decision": "Pending",
            "Full_Text_Decision": "Pending",
            "Exclusion_Reason": "",
            "Reviewer": "",
            "Review_Date": "",
            "Evidence_or_Link": work.primary_url,
            "Notes": (
                "Repository-level connected-component dedup complete; independent identity "
                "verification and human screening not performed"
            ),
        }
        rows.append(
            {header: values[header] for header in NATIVE_WORKBOOK_HEADERS["Screening"]}
        )
    return rows


def native_search_log_rows() -> list[dict[str, str]]:
    values = {
        "Query_ID": "ACL-CORPUS-001",
        "Prepared_Date": "2026-08-15",
        "Database": "GitHub repository snapshot",
        "Concept_Group": "Bounded ACL 2026 human-agent survey corpus",
        "Search_String": SOURCE_README_URL,
        "Primary_Window": f"Immutable repository commit {SOURCE_COMMIT}",
        "Older_Seminal_Rule": "Not applicable to repository-corpus extraction",
        "Status": "Corpus extraction complete / human screening pending",
        "Results_Returned": str(EXPECTED_COUNTS["distinct_works"]),
        "Results_Screened": "0",
        "Added_to_Papers": "0",
        "Searcher": "Codex (deterministic machine extraction)",
        "Execution_Date": "2026-08-15",
        "Notes": (
            "116 machine metadata mappings staged; no human title/abstract screen and no "
            "native-workbook write. QL-01 through QL-05 remain Protocol ready."
        ),
    }
    return [
        {header: values[header] for header in NATIVE_WORKBOOK_HEADERS["Search_Log"]}
    ]


def validate_sheet_safe_rows(rows: list[dict[str, str]]) -> None:
    """Reject values Google Sheets could interpret as formulas on append."""

    for row_index, row in enumerate(rows, start=1):
        for column, value in row.items():
            if isinstance(value, str) and value.lstrip().startswith(("=", "+", "-", "@")):
                raise ValueError(
                    "spreadsheet formula prefix in "
                    f"staged row {row_index}, column {column}: {value[:40]!r}"
                )


def foundations_query_test(
    capture: dict[str, object] | None = None,
) -> dict[str, object]:
    """Derive a fail-closed query record from a hash-verified observation."""

    if capture is None:
        capture = load_hash_bound_json(
            FOUNDATIONS_QUERY_CAPTURE,
            FOUNDATIONS_QUERY_CAPTURE_SHA256,
            "VEGO-FoundationsQueryObservationCapture-v1",
        )
    reported = capture["operator_reported_observation"]
    if not isinstance(reported, dict):
        raise ValueError("Foundations query capture has no operator observation")
    return {
        "schema_version": "VEGO-FoundationsQueryTest-v1",
        "query_id": "FOUNDATIONS-LIVE-TEST-001",
        "capture_input_sha256": FOUNDATIONS_QUERY_CAPTURE_SHA256,
        "query_status": capture["query_status"],
        "exact_query": capture["exact_query"],
        "platform": "Google Scholar",
        "interface_locale": capture["interface_locale"],
        "search_scope": "Articles; Any time; include citations; exclude patents",
        "observation_date": capture["observation_date"],
        "time_zone": capture["time_zone"],
        "result_summary_as_displayed": reported["result_summary_as_displayed"],
        "result_count": {
            "value": 2500,
            "qualifier": "Approximate, unverified operator-reported platform estimate",
        },
        "captcha_observed": reported["captcha_observed"],
        "authentication_block_observed": reported["authentication_block_observed"],
        "export_performed": reported["export_performed"],
        "screening_performed": reported["screening_performed"],
        "evidence_status": capture["evidence_status"],
        "readiness_eligible": capture["readiness_eligible"],
        "browser_evidence": {
            "method": "Unverified operator observation; no durable DOM or screenshot",
            "durable_capture_available": capture["durable_browser_capture_available"],
            "first_visible_result": reported["first_visible_result_title"],
        },
        "access_limitations": [
            "The result count is approximate and can change over time, location, and session.",
            "Google Scholar's interpretation of nested Boolean expressions was not independently validated.",
            "Only the visible results page and count were observed; no result export or screening occurred.",
            "The query wording remains unverified against the 2026-08-12 audio.",
        ],
        "formal_query_boundary": capture["formal_query_boundary"],
        "verification_note": capture["verification_note"],
    }


def _captured_records(
    capture: dict[str, object], sheet_name: str
) -> list[dict[str, object]]:
    sheets = capture["sheet_captures"]
    if not isinstance(sheets, dict) or not isinstance(sheets.get(sheet_name), dict):
        raise ValueError(f"native capture missing {sheet_name}")
    sheet = sheets[sheet_name]
    columns = sheet["sanitized_value_columns"]
    values = sheet["sanitized_values"]
    if not isinstance(columns, list) or not isinstance(values, list):
        raise ValueError(f"native capture values invalid for {sheet_name}")
    records: list[dict[str, object]] = []
    for raw_row in values[1:]:
        if not isinstance(raw_row, list) or len(raw_row) != len(columns):
            raise ValueError(f"native capture row shape invalid for {sheet_name}")
        records.append(dict(zip(columns, raw_row, strict=True)))
    return records


def native_append_preflight(
    works: list[Work],
    paper_rows: list[dict[str, str]],
    screening_rows: list[dict[str, str]],
    search_rows: list[dict[str, str]],
    capture: dict[str, object],
) -> dict[str, object]:
    """Prove offline staging is lossless and a replay would fail closed."""

    for rows in (paper_rows, screening_rows, search_rows):
        validate_sheet_safe_rows(rows)
    staged_paper_ids = [row["Paper_ID"] for row in paper_rows]
    staged_screening_ids = [row["Paper_ID"] for row in screening_rows]
    expected_work_ids = [work.work_id for work in works]
    if len(staged_paper_ids) != len(set(staged_paper_ids)):
        raise ValueError("duplicate Paper_ID in native Papers staging")
    if len(staged_screening_ids) != len(set(staged_screening_ids)):
        raise ValueError("duplicate Paper_ID in native Screening staging")
    if staged_paper_ids != expected_work_ids or staged_screening_ids != expected_work_ids:
        raise ValueError("native append staging lost or reordered a work")

    existing_papers = _captured_records(capture, "Papers")
    existing_screening = _captured_records(capture, "Screening")
    existing_search = _captured_records(capture, "Search_Log")
    existing_paper_ids = {str(row["Paper_ID"]) for row in existing_papers}
    existing_screening_ids = {str(row["Paper_ID"]) for row in existing_screening}
    existing_query_ids = {str(row["Query_ID"]) for row in existing_search}
    staged_query_ids = [row["Query_ID"] for row in search_rows]
    existing_titles = {
        normalize_title(str(row["Title"])) for row in existing_papers if row["Title"]
    }
    staged_titles = {normalize_title(row["Title"]) for row in paper_rows}
    existing_dois = {
        str(row["DOI"]).strip().lower() for row in existing_papers if row["DOI"]
    }
    staged_dois = {
        row["DOI"].strip().lower() for row in paper_rows if row["DOI"].strip()
    }
    existing_urls = {
        str(row["URL"]).strip().rstrip("/").lower()
        for row in existing_papers
        if row["URL"]
    }
    staged_urls = {
        row["URL"].strip().rstrip("/").lower()
        for row in paper_rows
        if row["URL"].strip()
    }
    collision_checks = {
        "Papers.Paper_ID": sorted(existing_paper_ids & set(staged_paper_ids)),
        "Papers.normalized_title": sorted(existing_titles & staged_titles),
        "Papers.DOI": sorted(existing_dois & staged_dois),
        "Papers.URL": sorted(existing_urls & staged_urls),
        "Screening.Paper_ID": sorted(
            existing_screening_ids & set(staged_screening_ids)
        ),
        "Search_Log.Query_ID": sorted(existing_query_ids & set(staged_query_ids)),
    }
    collisions = {key: value for key, value in collision_checks.items() if value}
    if collisions:
        raise ValueError(f"native append staging collides with captured keys: {collisions}")

    # Simulate the post-append key state. Every row must then be rejected on a
    # replay, proving the key guard makes repeated staging/application idempotent.
    replay_collisions = {
        "Papers": len((existing_paper_ids | set(staged_paper_ids)) & set(staged_paper_ids)),
        "Screening": len(
            (existing_screening_ids | set(staged_screening_ids))
            & set(staged_screening_ids)
        ),
        "Search_Log": len(
            (existing_query_ids | set(staged_query_ids)) & set(staged_query_ids)
        ),
    }
    staged_counts = {
        "Papers": len(paper_rows),
        "Screening": len(screening_rows),
        "Search_Log": len(search_rows),
    }
    data_rows = {
        name: int(sheet["data_rows"])
        for name, sheet in capture["sheet_captures"].items()
    }
    return {
        "schema_version": "VEGO-NativeAppendPreflight-v1",
        "capture_input_sha256": NATIVE_WORKBOOK_CAPTURE_SHA256,
        "offline_staging_lossless": True,
        "lossless_checks": {
            "work_count": len(works),
            "paper_ids_match_work_order": True,
            "screening_ids_match_work_order": True,
            "paper_and_screening_ids_identical": staged_paper_ids == staged_screening_ids,
            "formula_prefix_scan": "Passed",
        },
        "idempotency_guard_enabled": True,
        "replay_rejected_by_key_guard": replay_collisions == staged_counts,
        "replay_collision_counts": replay_collisions,
        "captured_existing_key_collisions": collision_checks,
        "live_append_ready": False,
        "live_append_blocker": capture["table_metadata_status"],
        "staged_counts": staged_counts,
        "expected_post_append_counts": {
            "Papers": data_rows["Papers"] + staged_counts["Papers"],
            "Search_Log": data_rows["Search_Log"] + staged_counts["Search_Log"],
            "Screening": data_rows["Screening"] + staged_counts["Screening"],
            "Taxonomy_and_Gaps": data_rows["Taxonomy_and_Gaps"],
            "Resources": data_rows["Resources"],
            "Controlled_Lists": data_rows["Controlled_Lists"],
        },
        "write_status": "Offline validation only; no Google Sheet write performed",
    }


KEY_SOURCE_IDS = (
    "ACL26-W-648348500982",  # Survey
    "ACL26-W-D9ACE8823B34",  # Ask or Assume?
    "ACL26-W-59A397CFEBE2",  # Ask-before-Plan
    "ACL26-W-A9CBC0D4C5D5",  # Controlled autonomy
    "ACL26-W-3086638BE92A",  # Oversight in practice
    "ACL26-W-9467D8B4B48F",  # Collaborative Gym
    "ACL26-W-BE797B75B0BD",  # MINT
    "ACL26-W-3377393DBDBC",  # Latent preference from user edits
    "ACL26-W-28C8BBD8854D",  # Collaborative Memory
    "ACL26-W-6B3ADFD39E05",  # HAS-Bench
    "ACL26-W-FD19E6D06C96",  # SPHERE
    "ACL26-W-B60BD98A4CFF",  # AgentDS
)


def key_source_rows(works: list[Work]) -> list[dict[str, str]]:
    by_id = {work.work_id: work for work in works}
    missing = set(KEY_SOURCE_IDS) - set(by_id)
    if missing:
        raise ValueError(f"key source IDs missing from pinned corpus: {sorted(missing)}")
    chapter_use = {
        "ACL26-W-648348500982": "2.3 taxonomy backbone",
        "ACL26-W-D9ACE8823B34": "2.4 clarification candidate",
        "ACL26-W-59A397CFEBE2": "2.4 proactive intervention candidate",
        "ACL26-W-A9CBC0D4C5D5": "2.4 bounded-autonomy candidate",
        "ACL26-W-3086638BE92A": "2.4 oversight-work candidate",
        "ACL26-W-9467D8B4B48F": "2.6 evaluation candidate",
        "ACL26-W-BE797B75B0BD": "2.5 feedback-environment candidate",
        "ACL26-W-3377393DBDBC": "2.5 judgment/preference candidate",
        "ACL26-W-28C8BBD8854D": "2.5 memory/access-control candidate",
        "ACL26-W-6B3ADFD39E05": "2.6 participation-evaluation candidate",
        "ACL26-W-FD19E6D06C96": "2.6 evaluation-card candidate",
        "ACL26-W-B60BD98A4CFF": "2.6 domain-transfer candidate",
    }
    rows: list[dict[str, str]] = []
    for sequence, work_id in enumerate(KEY_SOURCE_IDS, start=1):
        work = by_id[work_id]
        rows.append(
            {
                "Anchor_ID": f"C2-KS-{sequence:02d}",
                "Work_ID": work.work_id,
                "Title": work.title,
                "Primary_URL": work.primary_url,
                "Source_Commit": SOURCE_COMMIT,
                "README_Line_Refs": work.source_line_refs,
                "Candidate_Chapter2_Use": chapter_use[work.work_id],
                "Evidence_Level": "Pinned repository title/taxonomy metadata only",
                "Identity_Status": "Independent verification pending",
                "Human_Review_Status": "Pending",
                "Claim_Boundary": "Do not attribute a finding or conclusion before full-text review",
            }
        )
    return rows


def write_csv(path: Path, rows: list[dict[str, object]]) -> bytes:
    if not rows:
        raise ValueError(f"cannot write empty CSV: {path}")
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=list(rows[0]), lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    content = buffer.getvalue().encode("utf-8-sig")
    path.write_bytes(content)
    return content


def render_readme() -> str:
    return """# ACL 2026 Human-Agent Corpus — Bounded Evidence Package

This package is generated from the README at the immutable commit recorded in
`source-manifest.json`. It is a bounded repository-corpus extraction, not a
systematic database review and not an execution of QL-01 through QL-05.

## Files and grain

- `occurrences.csv`: one row per in-scope README occurrence; 525 rows.
- `works.csv`: one row per deduplicated work; 116 rows.
- `screening.csv`: one machine metadata-screen row per work. Human inclusion,
  author conclusions, and researcher synthesis remain pending.
- `local-candidate-corpus-audit.json`: reconciles the separate 144-record local
  candidate corpus and the six-row native Google workbook snapshot. Its 139
  normalized-title groups retain the weakest source verification label in each
  duplicate group: 127 verified-labelled, 11 partial, and 1 unverified.
- `taxonomy-gap-matrix.md`: maps what the source taxonomy explicitly encodes,
  what it does not encode, and the evidence-safe Chapter 2 structure.
- `chapter2-source-anchors.md`: page/section anchors into the primary ACL
  survey, with claim-safe wording for Chapter 2.
- `conservative-key-sources.csv`: twelve title/taxonomy-level candidates for
  human screening; no paper-level finding is attributed.
- `native-workbook-snapshot-2026-08-15.json`: read-only schema and row-count
  snapshot derived from a hash-bound connector capture of all six used ranges,
  including 11 Controlled_Lists data rows.
- `evidence-inputs/`: immutable, hash-bound sanitized inputs for the native
  workbook read and the unverified Foundations-query observation.
- `native-*-append-staging.csv`: exact-schema append candidates. These files
  have not been written to the native workbook. Their canonical SQ/Plan fields
  remain blank because the RQs and Plan A/B are unresolved.
- `native-append-preflight.json`: lossless/order/key-replay proof for offline
  staging. Live append remains blocked because native table metadata was not
  exposed by the connector.
- `foundations-query-test-2026-08-15.json`: one hash-bound, unverified operator
  observation of the Foundations query; no durable DOM/screenshot exists and
  it is not QL-01–QL-05 execution.

## Deduplication

Occurrences are joined when they share a normalized title or a strong
identifier (arXiv, ACL Anthology, OpenReview, DOI, or PubMed). This connects
publisher/preprint aliases and title variants while retaining every occurrence
and line reference. Same-title groups with conflicting strong identifiers fail
closed unless the exact publisher/preprint alias set is explicitly reviewed.
The final `Work_ID` is a deterministic hash of the connected component's
identifiers and normalized titles.

## Claim boundary

`Machine_Screen_Status=Complete` means only that all 116 titles and repository
taxonomy records received a deterministic preliminary mapping. It is never
equivalent to human title/abstract screening, full-text inclusion, independent
identity verification, or review completeness.
"""


def render_chapter2_source_anchors() -> str:
    return f"""# Chapter 2 Primary-Source Anchors

Primary source: Zou et al., *LLM-Based Human-Agent Collaboration and Interaction
Systems: A Survey*, Findings of ACL 2026, pages 36335–36364, DOI
`{SURVEY_DOI}`. Official landing page: {SURVEY_URL}. Official PDF:
https://aclanthology.org/2026.findings-acl.1811.pdf.

These anchors support only the survey-level statements below. Statements about
an individual cited work remain pending identity and full-text review.

| Anchor | Exact source location | Evidence-safe Chapter 2 statement | Boundary |
| --- | --- | --- | --- |
| C2-ACL-01 | p. 36335, Abstract | The survey frames LLM-based human-agent systems as systems that incorporate human information, feedback, or control and organizes the field around environment/profiling, feedback, interaction, orchestration, and communication. | This is the survey authors' framing, not independent proof of improved performance, reliability, or safety. |
| C2-ACL-02 | p. 36336, Figure 1 and Section 2 | The survey's system model contains five core components and assigns humans information/clarification, feedback/correction, and control/action roles. | Use as a taxonomy backbone; do not treat the listed benefits as VEGO-AI results. |
| C2-ACL-03 | pp. 36337–36338, Section 3.2 and Table 1 | Human feedback is categorized by type, granularity, and phase, including evaluative, corrective, guidance, and implicit forms. | Category definitions are source-reported; corpus-paper findings remain unscreened. |
| C2-ACL-04 | pp. 36339–36340, Section 3.3, Figure 2, and Table 2 | Interaction is separated into collaboration, competition, and coopetition; collaboration is refined into delegation, supervision, cooperation, and coordination. | This is one survey taxonomy, not the only possible taxonomy. |
| C2-ACL-05 | pp. 36340–36341, Sections 3.4–3.5 and Table 2 | Orchestration distinguishes task strategy from temporal synchronization, while communication distinguishes structure from mode. | Do not infer implementation effectiveness without primary-study review. |
| C2-ACL-06 | pp. 36341–36342, Section 3.6 and Table 3 | The survey adds a five-level Human Agency Scale spanning full automation through human-driven work. | Treat scale choice and suitability as questions for critical appraisal. |

## Repository anchors

The associated taxonomy repository is pinned to commit `{SOURCE_COMMIT}`. The
bounded parser found 525 in-scope README occurrences and 116 connected-component
works. Exact per-occurrence line anchors are in `occurrences.csv`; exact
per-work line sets are in `works.csv`; the twelve conservative starting points
are in `conservative-key-sources.csv`.

Repository line anchors prove only that a title/link/taxonomy assignment appears
in that pinned README. They do not prove bibliographic identity, study quality,
methods, results, or authors' conclusions.
"""


def render_gap_matrix() -> str:
    return f"""# ACL 2026 Taxonomy Coverage and Candidate-Gap Matrix

Source: Zou et al., *LLM-Based Human-Agent Collaboration and Interaction Systems:
A Survey*, Findings of ACL 2026, DOI `{SURVEY_DOI}`, and the associated repository
at commit `{SOURCE_COMMIT}`.

## Reconciled corpus

| Layer | Raw rows | Distinct works | Meaning |
| --- | ---: | ---: | --- |
| Latest Research Papers | 106 | 106 | Chronological repository list |
| Applications, Datasets & Benchmarks | 62 | 57 | Application/category occurrences |
| Taxonomy | 357 | 90 | Repeated work-by-taxonomy assignments |
| Union | 525 | 116 | Bounded corpus after connected-component deduplication |

Taxonomy rows: Human Feedback `89`; Interaction `89`; Orchestration `90`;
Communication `89`.

## What the source taxonomy explicitly encodes

| Branch | Encoded dimensions | Safe Chapter 2 use |
| --- | --- | --- |
| Human Feedback | type, subtype, granularity, phase | Describe what information/control humans provide and when |
| Interaction | interaction type and variant | Compare collaboration, supervision, delegation, cooperation, and coordination |
| Orchestration | strategy and synchronization | Describe one-by-one/simultaneous and synchronous/asynchronous control |
| Communication | structure and mode | Describe centralized/decentralized/hierarchical communication and conversation/observation |

## Dimensions not encoded by the taxonomy schema

The following are **schema-coverage observations**, not claims that no paper in
the corpus discusses the topic: case grounding; provenance; accountable expert
authority; validation and adjudication; conflict handling; scope, expiry, and
revocation; safe reuse of a judgment artifact; cross-context transfer of that
artifact; and measured expert burden. Full-text screening is required before
any absence or novelty claim.

## Evidence-safe Chapter 2 structure

1. **2.1 Review scope and evidence method.** Distinguish the bounded ACL corpus,
   the separate local candidate corpus, and deferred QL-01 through QL-05.
2. **2.2 Problem setting: guideline operationalization and observed
   variability.** Establish the domain problem before presenting a solution.
3. **2.3 Agentic systems and the human-agent collaboration design space.** Use
   the survey's four explicit taxonomy branches and their encoded dimensions.
4. **2.4 Selective intervention and bounded oversight.** Synthesize candidate
   evidence relevant to when a system asks; do not infer burden reduction from
   routing counts.
5. **2.5 Feedback, judgment representation, governance, and reuse.** Separate
   source-reported feedback mechanisms from the still-hypothetical governed
   judgment lifecycle.
6. **2.6 Evaluation, transfer, and context boundaries.** Separate general
   collaboration benchmarks from transfer of governed judgment artifacts.
7. **2.7 Synthesis and candidate gaps.** Every gap is source-backed or labelled
   `Pending full-text review`; provisional RQ wording is not used as a heading.

## Frozen boundaries

- RQ wording, exploration versus identification, and human versus expert remain unresolved.
- QL-01 through QL-05 remain protocol-ready and deferred after the proposal-stage bounded corpus pass.
- The pre-existing methodology draft is frozen; this tranche does not extend it.
"""


def fetch_source() -> bytes:
    with urllib.request.urlopen(SOURCE_README_URL, timeout=30) as response:  # noqa: S310
        return response.read()


def build(source_bytes: bytes, output_dir: Path) -> dict[str, object]:
    source_hash = hashlib.sha256(source_bytes).hexdigest()
    if source_hash != SOURCE_README_SHA256:
        raise ValueError(
            f"pinned README hash mismatch: expected {SOURCE_README_SHA256}, got {source_hash}"
        )
    source_text = source_bytes.decode("utf-8")
    occurrences = parse_readme(source_text)
    works = build_works(occurrences)

    section_works: dict[str, set[str]] = defaultdict(set)
    branch_rows = Counter()
    index_to_work: dict[int, str] = {}
    for work in works:
        for index in work.occurrence_indexes:
            index_to_work[index] = work.work_id
    for index, occurrence in enumerate(occurrences):
        section_works[occurrence.source_section].add(index_to_work[index])
        if occurrence.source_section == "Taxonomy":
            branch_rows[occurrence.taxonomy_branch] += 1

    actual_counts = {
        "raw_occurrences": len(occurrences),
        "distinct_works": len(works),
        "latest_research_works": len(section_works["Latest Research Papers"]),
        "application_works": len(section_works["Applications, Datasets & Benchmarks"]),
        "taxonomy_works": len(section_works["Taxonomy"]),
    }
    if actual_counts != EXPECTED_COUNTS:
        raise ValueError(f"pinned corpus count mismatch: {actual_counts}")
    if dict(branch_rows) != EXPECTED_TAXONOMY_ROWS:
        raise ValueError(f"pinned taxonomy row mismatch: {dict(branch_rows)}")

    native_capture = load_hash_bound_json(
        NATIVE_WORKBOOK_CAPTURE,
        NATIVE_WORKBOOK_CAPTURE_SHA256,
        "VEGO-NativeWorkbookConnectorCapture-v1",
    )
    foundations_capture = load_hash_bound_json(
        FOUNDATIONS_QUERY_CAPTURE,
        FOUNDATIONS_QUERY_CAPTURE_SHA256,
        "VEGO-FoundationsQueryObservationCapture-v1",
    )
    staged_papers = native_paper_rows(works)
    staged_screening = native_screening_rows(works)
    staged_search = native_search_log_rows()
    append_preflight = native_append_preflight(
        works,
        staged_papers,
        staged_screening,
        staged_search,
        native_capture,
    )

    output_dir.mkdir(parents=True, exist_ok=True)
    occurrence_bytes = write_csv(output_dir / "occurrences.csv", occurrence_rows(occurrences, works))
    works_bytes = write_csv(output_dir / "works.csv", work_rows(works))
    screening_bytes = write_csv(
        output_dir / "screening.csv", [machine_screen(work) for work in works]
    )
    key_source_bytes = write_csv(
        output_dir / "conservative-key-sources.csv", key_source_rows(works)
    )
    native_paper_bytes = write_csv(
        output_dir / "native-papers-append-staging.csv", staged_papers
    )
    native_screening_bytes = write_csv(
        output_dir / "native-screening-append-staging.csv", staged_screening
    )
    native_search_bytes = write_csv(
        output_dir / "native-search-log-append-staging.csv", staged_search
    )
    native_snapshot = native_workbook_snapshot(native_capture)
    native_snapshot_bytes = (
        json.dumps(native_snapshot, indent=2, ensure_ascii=False) + "\n"
    ).encode("utf-8")
    (output_dir / "native-workbook-snapshot-2026-08-15.json").write_bytes(
        native_snapshot_bytes
    )
    foundations_test = foundations_query_test(foundations_capture)
    foundations_test_bytes = (
        json.dumps(foundations_test, indent=2, ensure_ascii=False) + "\n"
    ).encode("utf-8")
    (output_dir / "foundations-query-test-2026-08-15.json").write_bytes(
        foundations_test_bytes
    )
    audit = local_candidate_audit(works, native_capture=native_capture)
    audit_bytes = (json.dumps(audit, indent=2, ensure_ascii=False) + "\n").encode("utf-8")
    (output_dir / "local-candidate-corpus-audit.json").write_bytes(audit_bytes)
    append_preflight_bytes = (
        json.dumps(append_preflight, indent=2, ensure_ascii=False) + "\n"
    ).encode("utf-8")
    (output_dir / "native-append-preflight.json").write_bytes(
        append_preflight_bytes
    )
    readme_bytes = render_readme().encode("utf-8")
    gap_bytes = render_gap_matrix().encode("utf-8")
    source_anchor_bytes = render_chapter2_source_anchors().encode("utf-8")
    (output_dir / "README.md").write_bytes(readme_bytes)
    (output_dir / "taxonomy-gap-matrix.md").write_bytes(gap_bytes)
    (output_dir / "chapter2-source-anchors.md").write_bytes(source_anchor_bytes)

    manifest: dict[str, object] = {
        "schema_version": "VEGO-ACL2026-Corpus-v1",
        "source": {
            "survey_url": SURVEY_URL,
            "survey_doi": SURVEY_DOI,
            "repository_url": SOURCE_REPOSITORY_URL,
            "commit": SOURCE_COMMIT,
            "readme_url": SOURCE_README_URL,
            "readme_sha256": source_hash,
            "retrieval_date": "2026-08-15",
        },
        "source_inputs": {
            "pinned_repository_readme": {
                "locator": SOURCE_README_URL,
                "sha256": source_hash,
                "evidence_status": "Immutable repository source",
            },
            "local_candidate_corpus": {
                "locator": "literature/verified-research-corpus-2026-08-12.json",
                "sha256": LOCAL_CANDIDATE_SHA256,
                "evidence_status": "Repository-bound candidate source labels",
            },
            "native_workbook_capture": {
                "locator": (
                    "literature/acl2026-human-agent-corpus/evidence-inputs/"
                    "native-workbook-connector-capture-2026-08-15.json"
                ),
                "sha256": NATIVE_WORKBOOK_CAPTURE_SHA256,
                "evidence_status": native_capture["evidence_status"],
            },
            "foundations_query_capture": {
                "locator": (
                    "literature/acl2026-human-agent-corpus/evidence-inputs/"
                    "foundations-query-observation-capture-2026-08-15.json"
                ),
                "sha256": FOUNDATIONS_QUERY_CAPTURE_SHA256,
                "evidence_status": foundations_capture["evidence_status"],
            },
        },
        "scope": {
            "included_sections": sorted(IN_SCOPE_SECTIONS),
            "deduplication": (
                "connected components over normalized title and strong identifiers; "
                "all source occurrences retained; conflicting strong IDs rejected unless "
                "the exact publisher/preprint alias set was reviewed"
            ),
            "screening_level": "Machine repository-metadata/title mapping only",
            "native_workbook_write_status": "Not written; append candidates staged only",
        },
        "counts": actual_counts,
        "taxonomy_rows": dict(sorted(branch_rows.items())),
        "boundaries": {
            "formal_queries": "QL-01 through QL-05: protocol ready / deferred after proposal",
            "research_questions": "Provisional / unresolved",
            "methodology": "Frozen pre-existing draft",
            "human_screening": "Pending for 116 of 116 works",
            "novelty_claim": "Not permitted from this extraction alone",
        },
        "artifacts": {
            "occurrences.csv": hashlib.sha256(occurrence_bytes).hexdigest(),
            "works.csv": hashlib.sha256(works_bytes).hexdigest(),
            "screening.csv": hashlib.sha256(screening_bytes).hexdigest(),
            "conservative-key-sources.csv": hashlib.sha256(key_source_bytes).hexdigest(),
            "native-papers-append-staging.csv": hashlib.sha256(native_paper_bytes).hexdigest(),
            "native-screening-append-staging.csv": hashlib.sha256(
                native_screening_bytes
            ).hexdigest(),
            "native-search-log-append-staging.csv": hashlib.sha256(
                native_search_bytes
            ).hexdigest(),
            "native-append-preflight.json": hashlib.sha256(
                append_preflight_bytes
            ).hexdigest(),
            "native-workbook-snapshot-2026-08-15.json": hashlib.sha256(
                native_snapshot_bytes
            ).hexdigest(),
            "foundations-query-test-2026-08-15.json": hashlib.sha256(
                foundations_test_bytes
            ).hexdigest(),
            "local-candidate-corpus-audit.json": hashlib.sha256(audit_bytes).hexdigest(),
            "README.md": hashlib.sha256(readme_bytes).hexdigest(),
            "taxonomy-gap-matrix.md": hashlib.sha256(gap_bytes).hexdigest(),
            "chapter2-source-anchors.md": hashlib.sha256(source_anchor_bytes).hexdigest(),
        },
    }
    manifest_bytes = (json.dumps(manifest, indent=2, ensure_ascii=False) + "\n").encode("utf-8")
    (output_dir / "source-manifest.json").write_bytes(manifest_bytes)
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--readme", type=Path, help="Optional local copy of the pinned README")
    parser.add_argument("--output-dir", type=Path, default=OUTPUT_DIR)
    args = parser.parse_args()
    source_bytes = args.readme.read_bytes() if args.readme else fetch_source()
    manifest = build(source_bytes, args.output_dir)
    print(
        "ACL 2026 corpus: "
        f"{manifest['counts']['raw_occurrences']} occurrences, "  # type: ignore[index]
        f"{manifest['counts']['distinct_works']} works -> {args.output_dir}"  # type: ignore[index]
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
