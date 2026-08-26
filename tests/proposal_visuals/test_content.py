from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest
from pypdf import PdfWriter

from proposal_visuals.content import (
    load_content,
    load_source_provenance,
    load_verified_content,
    verify_source_hash,
)


@pytest.fixture
def content_path() -> Path:
    return (
        Path(__file__).resolve().parents[2]
        / "docs"
        / "research"
        / "phd-proposal"
        / "figures"
        / "content.json"
    )


@pytest.fixture
def provenance_path() -> Path:
    return (
        Path(__file__).resolve().parents[2]
        / "docs"
        / "research"
        / "phd-proposal"
        / "figures"
        / "source-provenance.json"
    )


def _write_pdf(path: Path) -> str:
    writer = PdfWriter()
    writer.add_blank_page(width=72, height=72)
    with path.open("wb") as stream:
        writer.write(stream)
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def _write_provenance(path: Path, source: Path, sha256: str, page_count: int = 1) -> None:
    path.write_text(
        json.dumps(
            {
                "source_artifact": {
                    "filename": source.name,
                    "media_type": "application/pdf",
                    "sha256": sha256,
                    "proposal_date": "2026-08-25",
                    "page_count": page_count,
                    "authority": "test fixture",
                }
            }
        ),
        encoding="utf-8",
    )


def test_manifest_has_exact_figure_contracts(content_path: Path, provenance_path: Path) -> None:
    """A missing frozen label or count must fail before any visual is built."""
    content = load_content(content_path)
    provenance = load_source_provenance(provenance_path)

    assert list(content.figures) == [f"fig-{number:02d}" for number in range(1, 12)]
    assert provenance.filename == "VEGO_AI_Doctoral_Proposal_Revised_20260825 (4).pdf"
    assert provenance.media_type == "application/pdf"
    assert provenance.page_count == 31
    assert content.figures["fig-01"].title == "Six readings of one observed model difference"
    assert content.figures["fig-01"].caption == "Figure 1. Six readings of one observed model difference."
    assert content.figures["fig-01"].alt_text == (
        "One observed Shift Supervisor model difference branches equally to six interpretations, "
        "showing that the artifact alone is not a verdict."
    )
    assert content.figures["fig-01"].items["readings"] == [
        "The actor may be a defensible abstraction of a role the description implies without naming.",
        "It may be a modeling-language error, if the student has used an actor where the notation calls for a role or a boundary element.",
        "It may be a domain misconception about who authorizes what.",
        "It may reflect genuine ambiguity in the task description.",
        "It may expose a gap in the guideline, which should have admitted this representation and does not.",
        "Or it may be a legitimate local decision that the instructor permits for a pedagogical reason specific to this course.",
    ]
    assert content.figures["fig-05"].items["signals"] == [
        "claim-level uncertainty",
        "consequence of an unreviewed error",
        "evidence quality",
        "reviewer competence for the specific claim",
        "current queue conditions",
        "novelty relative to the judgment store",
        "cross-agent disagreement",
        "expected future reuse value",
    ]
    assert content.figures["fig-05"].items["actions"] == [
        "immediate qualified review",
        "queue",
        "batch review",
        "audit sample",
        "autonomous action with logging",
        "blocked action",
    ]
    assert content.figures["fig-07"].items["statuses"] == [
        "Eligible",
        "Eligible with adaptation",
        "Blocked",
        "Undetermined",
    ]
    assert content.figures["fig-07"].items["outcomes"] == [
        "reuse permitted",
        "local quirk",
        "capability-gap candidate",
    ]
    assert content.figures["fig-06"].items["states"] == [
        "Created",
        "Validated",
        "Contested",
        "Superseded",
        "Expired",
        "Revoked",
    ]
    assert content.figures["fig-08"].items["values"] == {
        "ch-ucd": {"compliance_vectors": 0.8, "uncovered_fragment_audits": 0.55},
        "ch-cd": {"compliance_vectors": 0.96, "uncovered_fragment_audits": 0.81},
        "pw-ucd": {"compliance_vectors": 0.83, "uncovered_fragment_audits": 0.55},
        "pw-cd": {"compliance_vectors": 0.92, "uncovered_fragment_audits": 0.88},
    }
    assert content.figures["fig-08"].items["y_domain"] == [0.0, 1.0]
    assert content.figures["fig-08"].items["sample"] == (
        "16 outcomes; four per setting; two experts; no dispersion or inter-rater statistic reported"
    )
    assert content.figures["fig-08"].items["series_labels"] == [
        "Compliance vectors",
        "Uncovered-fragment audits",
    ]
    assert content.figures["fig-08"].items["sample_disclosure"] == (
        "n=16; four per setting; two experts; no dispersion or inter-rater statistic reported"
    )
    assert content.figures["fig-08"].items["evidence_boundary"] == (
        "Reported foundation-manuscript baseline evidence only; not a doctoral result."
    )
    assert content.figures["fig-08"].items["axis"] == {
        "label": "Reported score (0-1)",
        "ticks": [0.0, 0.2, 0.4, 0.6, 0.8, 1.0],
    }
    assert content.figures["fig-09"].items["main_period"] == "Oct 2027 - Oct 2030"
    assert content.figures["fig-09"].items["preparatory_outside_count"] is True
    assert content.figures["fig-09"].items["milestone_schedule"] == [
        {"label": "Paper 1", "semester": 2},
        {"label": "Paper 2", "semester": 4},
        {"label": "Paper 3", "semester": 5},
        {"label": "defence", "semester": 6},
    ]
    assert content.figures["fig-09"].items["conditional_medical_option"] == {
        "label": "Conditional medical extension",
        "critical_path": False,
        "go_no_go": "go / no-go - Sep 2029",
    }
    assert content.figures["fig-09"].items["readiness_gates"] == {
        "exp005": "0/24",
        "medical": "0/6",
        "note": "EXP-005 remains 0/24; medical readiness remains 0/6. This plan makes no readiness claim.",
    }
    assert content.figures["fig-10"].items["missing_concepts"] == [
        "Reuse of a stored judgment in a later, different episode, and the reuse mode - inert, advisory, or behavior-changing",
        "Claim-level validity scope: the prospective applicability envelope, including explicit negative scope",
        "Diagnostic attribution: whether an intervention reveals a domain-specific quirk or a transferable capability gap",
        "Temporal validity: expiry, supersession, revocation, and lapse when the interpreted guideline is revised",
        "Claim-scoped authority and competence, separating case-level decisions from rubric-level changes",
        "Version-exact provenance binding to the artifact state judged, with staleness detection",
        "The elicitation trigger as a versioned, reason-coded policy object",
        "Attention-budget accounting: a bounded budget per run and an allocation rule across claims",
        "Preserved dissent: two conflicting judgments both retained, reuse blocked pending adjudication",
        "Reuse-leakage control: provenance disjointness between the judgment store and the evaluation cases",
        "Judgment target layer: verdict, the agent's stated reasoning, evidence selection, or the guideline",
    ]
    assert content.figures["fig-11"].items["paper_disposition"] == {
        "Relevant": 22,
        "Less relevant": 63,
        "Not relevant": 5,
    }
    assert content.figures["fig-11"].items["rq_coverage"] == {
        "U-RQ": "Partly",
        "SQ1": "Yes",
        "SQ2": "Partly",
        "SQ3": "No",
    }
    assert content.figures["fig-11"].items["screening_limit"] == (
        "single-rater and title-level; corpus-scoped rather than field-scoped"
    )
    assert content.figures["fig-11"].items["paper_total"] == 90
    assert content.figures["fig-11"].items["paper_disposition_heading"] == (
        "Paper-level disposition: 90 screened papers"
    )
    assert content.figures["fig-11"].items["rq_coverage_heading"] == (
        "Research-question-level coverage - not paper-level disposition"
    )
    assert content.figures["fig-11"].items["missing_coverage_note"] == (
        "research-question-level missing coverage; not paper-level disposition"
    )
    assert content.figures["fig-11"].items["standalone_status"] == (
        "Standalone candidate only - not integrated into the proposal."
    )
    assert content.figures["fig-03"].items["streams"] == [
        "mixed-initiative design",
        "deferral & active learning",
        "explanatory debugging & provenance",
        "case-based reasoning & transfer",
        "guideline operationalization",
    ]
    assert content.figures["fig-04"].items["columns"] == [
        "Sub-question",
        "Primary artifact",
        "Evaluation",
        "Planned output",
    ]
    assert content.figures["fig-04"].items["spine_rows"] == [
        {
            "row": "SQ1",
            "cells": [
                "SQ1 Selective intervention",
                "Attention-budget review-policy model",
                "Matched-budget policy study",
                "Paper 1",
            ],
        },
        {
            "row": "SQ2",
            "cells": [
                "SQ2 Governed judgment",
                "Governed-judgment contract",
                "Conformance and comparator study",
                "Paper 2",
            ],
        },
        {
            "row": "SQ3",
            "cells": [
                "SQ3 Controlled reuse",
                "Reuse and capability-gap procedure",
                "Reliability and frozen-target study",
                "Paper 3",
            ],
        },
        {
            "row": "Integrated",
            "cells": [
                "Integrated evaluation of the umbrella question",
                "Four-arm comparison",
                "Comparator arms",
                "Matched cases, evidence and attention",
            ],
        },
    ]
    assert content.figures["fig-04"].items["integrated_arms"] == [
        "AI-only",
        "human-only",
        "ordinary non-governed HITL",
        "governed VEGO-AI",
    ]
    assert content.figures["fig-04"].items["integrated_boundary"] == (
        "Consumes all three studies; not answered by completing them."
    )
    assert content.figures["fig-04"].alt_text == (
        "Four aligned rows map SQ1-SQ3 to their specified artifacts, evaluations, and "
        "papers; a fourth row compares AI-only, human-only, ordinary non-governed HITL, and "
        "governed VEGO-AI under matched cases, evidence, and attention."
    )
    assert content.figures["fig-07"].alt_text == (
        "Five sequential reuse gates precede a four-status reuse decision whose exact routing rule "
        "is not specified. Reuse permitted is shown separately from the four statuses, while local "
        "quirk and a four-check capability-gap candidate form an independent diagnostic layer."
    )


def test_loaded_content_is_immutable(content_path: Path) -> None:
    """A renderer cannot mutate frozen proposal content during layout."""
    content = load_content(content_path)

    with pytest.raises(TypeError):
        content.figures["fig-01"].items["readings"] = []


def test_verify_source_hash_rejects_source_drift(tmp_path: Path) -> None:
    """A changed source artifact must stop a build that claims this provenance."""
    source = tmp_path / "source.pdf"
    source.write_bytes(b"frozen source")

    verify_source_hash(
        source,
        "B7771CC1BF86EA34EDDA47235F8678519B12234800ECEF2C0CCB2EEC0165F62A",
    )
    source.write_bytes(b"changed source")

    with pytest.raises(ValueError, match="source drift"):
        verify_source_hash(
            source,
            "B7771CC1BF86EA34EDDA47235F8678519B12234800ECEF2C0CCB2EEC0165F62A",
        )


def test_load_verified_content_consumes_pdf_provenance(
    content_path: Path, tmp_path: Path
) -> None:
    """A renderer receives content only after the recorded PDF identity is verified."""
    source = tmp_path / "proposal.pdf"
    provenance = tmp_path / "provenance.json"
    _write_provenance(provenance, source, _write_pdf(source))

    content = load_verified_content(content_path, provenance, source)

    assert list(content.figures) == [f"fig-{number:02d}" for number in range(1, 12)]


def test_load_verified_content_rejects_drift_before_parsing_content(tmp_path: Path) -> None:
    """An incorrect source hash stops the render path before malformed content is accepted."""
    source = tmp_path / "proposal.pdf"
    provenance = tmp_path / "provenance.json"
    malformed_content = tmp_path / "content.json"
    _write_pdf(source)
    _write_provenance(provenance, source, "0" * 64)
    malformed_content.write_text("{", encoding="utf-8")

    with pytest.raises(ValueError, match="source drift"):
        load_verified_content(malformed_content, provenance, source)


def test_load_verified_content_rejects_page_count_drift(content_path: Path, tmp_path: Path) -> None:
    """The recorded PDF page count is part of the production provenance gate."""
    source = tmp_path / "proposal.pdf"
    provenance = tmp_path / "provenance.json"
    _write_provenance(provenance, source, _write_pdf(source), page_count=2)

    with pytest.raises(ValueError, match="page count drift"):
        load_verified_content(content_path, provenance, source)


@pytest.mark.parametrize(
    ("field", "value", "match"),
    [
        ("media_type", "text/plain", "application/pdf"),
        ("sha256", "not-a-hash", "SHA-256"),
        ("page_count", 0, "page_count"),
    ],
)
def test_load_source_provenance_rejects_invalid_recorded_source_metadata(
    tmp_path: Path, field: str, value: object, match: str
) -> None:
    """Malformed recorded source metadata cannot silently disable verification."""
    source = tmp_path / "proposal.pdf"
    provenance = tmp_path / "provenance.json"
    _write_pdf(source)
    _write_provenance(provenance, source, hashlib.sha256(source.read_bytes()).hexdigest().upper())
    payload = json.loads(provenance.read_text(encoding="utf-8"))
    payload["source_artifact"][field] = value
    provenance.write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(ValueError, match=match):
        load_source_provenance(provenance)


@pytest.mark.parametrize(
    "locators",
    [
        [],
        [""],
        ["   "],
        ["PDF p. 5"],
        ["§1.7"],
    ],
)
def test_load_content_rejects_missing_or_incomplete_locators(
    content_path: Path, tmp_path: Path, locators: list[str]
) -> None:
    """Every figure must retain a nonblank page plus section-or-table locator."""
    payload = json.loads(content_path.read_text(encoding="utf-8"))
    payload["figures"]["fig-01"]["locators"] = locators
    invalid_content = tmp_path / "content.json"
    invalid_content.write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(ValueError, match="locators"):
        load_content(invalid_content)
