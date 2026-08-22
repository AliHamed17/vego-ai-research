from pathlib import Path

import pytest

from obsidian_brain.bills import BillReminder, parse_bill, write_bill_reminder


def test_bill_parser_creates_a_review_required_reminder_without_payment_details() -> None:
    bill = parse_bill("Invoice from Example Energy. Amount due: 125.50 ILS. Due date: 2026-09-01")

    assert bill.issuer == "Example Energy"
    assert bill.amount == "125.50"
    assert bill.due_date == "2026-09-01"
    assert bill.review_state == "needs_human_review"
    assert bill.payment_action == "not_supported"


def test_bill_reminder_note_is_explicitly_non_actioning(tmp_path: Path) -> None:
    bill = parse_bill("Invoice from Example Energy. Amount due: 125.50 ILS. Due date: 2026-09-01")

    note = write_bill_reminder(tmp_path, bill)

    content = note.read_text(encoding="utf-8")
    assert "needs_human_review" in content
    assert "not_supported" in content
    assert "bank transfer" not in content.casefold()


def test_bill_reminder_rejects_multiline_frontmatter_values(tmp_path: Path) -> None:
    bill = BillReminder(
        issuer="issuer\nprivate source body",
        amount="125.50",
        currency="ILS",
        due_date="2026-09-01",
        review_state="needs_human_review",
        payment_action="not_supported",
    )

    with pytest.raises(ValueError, match="single-line"):
        write_bill_reminder(tmp_path, bill)
