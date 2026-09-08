"""Guard the Study 1 and Study 2 claim boundary in tracked documents.

A forbidden term is allowed where the surrounding paragraph negates it, marks
it as not measured, or frames it as a future condition. It is a failure where
a document asserts it. The scanner therefore reads paragraph context rather
than matching a bare term, because a disclaimer often wraps across lines.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
DOCS = ROOT / "docs/research/phd-proposal"

FORBIDDEN = {
    "accuracy": r"\baccurac",
    "precision": r"\bprecision\b",
    "recall": r"\brecall\b",
    "f1": r"\bF1\b",
    "alert_correctness": r"alert[- ]?correctness|נכונות ה?התרע",
    "human_benefit": r"human[- ]?benefit|תועלת אנושית",
    "effectiveness": r"\beffectiveness\b|אפקטיביות",
    "representativeness": r"representativ|ייצוגיות",
    "generalization": r"generaliz|הכללה",
    "student_evidence": r"student (data|evidence|behaviou?r)|נתוני סטודנטים",
    "historical_recovery": r"historical recovery|שחזור של Cheers",
}

NEGATION_TERMS = [
    r"\bno\b", r"\bnot\b", r"\bnever\b", r"\bwithout\b", r"\bcannot\b",
    r"\bneither\b", r"\bnor\b", r"\bforbidden\b", r"\bprohibit", r"\bif\b",
    r"\bwould\b", r"\bshould\b", r"\brequire", r"\bunless\b", r"\bpending\b",
    r"\bfuture\b", r"\bdoes not\b", r"\bis not\b", r"\bare not\b",
    "אין", "אינו", "אינם", "אינה", "לא ", "ללא", "אסור", "נאסר",
    "אם ", "ייבחן", "נדרש", "עתידי", "טרם", "לא חושב", "לא נטענ",
]
NEGATION = re.compile("|".join(NEGATION_TERMS), re.IGNORECASE)

BOAST = re.compile(
    r"detector works well|works well|threshold is correct|proves that|proven to"
    r"|הגלאי עובד היטב|הסף נכון|צורך מוכח",
    re.IGNORECASE,
)


def tracked_docs() -> list[Path]:
    prefixes = ("2026-09-06-study1", "2026-09-06-study2", "2026-09-05-study1")
    return sorted(p for p in DOCS.glob("*.md") if p.name.startswith(prefixes))


def paragraphs(text: str) -> list[str]:
    """Blank-line separated blocks: a disclaimer may wrap across several lines."""
    return [block for block in re.split(r"\n\s*\n", text) if block.strip()]


@pytest.mark.parametrize("path", tracked_docs(), ids=lambda p: p.name)
def test_forbidden_claims_only_appear_under_negation(path: Path):
    offenders = []
    for block in paragraphs(path.read_text(encoding="utf-8")):
        if NEGATION.search(block):
            continue
        for label, pattern in FORBIDDEN.items():
            if re.search(pattern, block, re.IGNORECASE):
                offenders.append(f"[{label}] {block.strip()[:140]}")
    assert not offenders, f"{path.name} asserts forbidden claims:\n" + "\n".join(offenders)


@pytest.mark.parametrize("path", tracked_docs(), ids=lambda p: p.name)
def test_no_unbounded_success_wording(path: Path):
    offenders = [
        block.strip()[:140]
        for block in paragraphs(path.read_text(encoding="utf-8"))
        if BOAST.search(block)
    ]
    assert not offenders, f"{path.name} contains unbounded success wording:\n" + "\n".join(offenders)


def test_scanner_detects_an_affirmative_claim():
    """The scanner must fail a real violation, not pass everything."""
    bad = "The detector reached high accuracy on this corpus."
    assert not NEGATION.search(bad)
    assert re.search(FORBIDDEN["accuracy"], bad, re.IGNORECASE)


def test_scanner_allows_a_wrapped_disclaimer():
    good = "No accuracy, precision, recall, F1,\nrepresentativeness or generalization claim is made."
    assert NEGATION.search(good)


def test_scanner_allows_a_hebrew_conditional():
    good = "אם ייבחן נכונות ההתרעות — נדרשת תוכנית תיוג בלתי תלויה."
    assert NEGATION.search(good)


def test_at_least_one_document_is_scanned():
    assert tracked_docs(), "claim scanner found no Study 1 or Study 2 documents"
