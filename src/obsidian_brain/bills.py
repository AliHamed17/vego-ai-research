from __future__ import annotations

import json
import re
from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path


@dataclass(frozen=True)
class BillReminder:
    issuer: str | None
    amount: str | None
    currency: str | None
    due_date: str | None
    review_state: str
    payment_action: str


_AMOUNT = re.compile(
    r"(?:amount due|total)\s*:?\s*([0-9]+(?:[.,][0-9]{2})?)\s*(ILS|USD|EUR|₪|\$|€)",
    re.IGNORECASE,
)
_DUE_DATE = re.compile(r"due\s*(?:date)?\s*:?\s*(\d{4}-\d{2}-\d{2})", re.IGNORECASE)
_ISSUER = re.compile(r"(?:invoice|bill)\s+from\s+([A-Za-z0-9 &'-]+)", re.IGNORECASE)


def parse_bill(text: str) -> BillReminder:
    """Extract a local reminder candidate; paying or contacting an issuer is unsupported."""

    amount = _AMOUNT.search(text)
    due_date = _DUE_DATE.search(text)
    issuer = _ISSUER.search(text)
    return BillReminder(
        issuer=issuer.group(1).strip() if issuer else None,
        amount=amount.group(1).replace(",", ".") if amount else None,
        currency=amount.group(2) if amount else None,
        due_date=due_date.group(1) if due_date else None,
        review_state="needs_human_review",
        payment_action="not_supported",
    )


def write_bill_reminder(notes_root: Path, bill: BillReminder) -> Path:
    """Create a local reminder candidate that requires a human review before any action."""

    values = {
        "issuer": bill.issuer,
        "amount": bill.amount,
        "currency": bill.currency,
        "due_date": bill.due_date,
        "review_state": bill.review_state,
        "payment_action": bill.payment_action,
    }
    for value in values.values():
        if value is not None and ("\r" in value or "\n" in value):
            raise ValueError("Bill reminder fields must be single-line values")
    bills_root = notes_root / "Bills"
    bills_root.mkdir(parents=True, exist_ok=True)
    identity = "|".join(
        part or "" for part in (bill.issuer, bill.amount, bill.currency, bill.due_date)
    )
    reminder_id = sha256(identity.encode("utf-8")).hexdigest()[:16]
    note = bills_root / f"BILL-{reminder_id}.md"
    note.write_text(
        "\n".join(
            (
                "---",
                f"reminder_id: BILL-{reminder_id}",
                f"issuer: {json.dumps(bill.issuer or 'unknown')}",
                f"amount: {json.dumps(bill.amount or 'unknown')}",
                f"currency: {json.dumps(bill.currency or 'unknown')}",
                f"due_date: {json.dumps(bill.due_date or 'unknown')}",
                f"review_state: {json.dumps(bill.review_state)}",
                f"payment_action: {json.dumps(bill.payment_action)}",
                "---",
                "",
                "This is a reminder candidate only. Confirm the source and due date before acting.",
            )
        )
        + "\n",
        encoding="utf-8",
    )
    return note
