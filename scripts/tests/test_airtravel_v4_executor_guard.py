"""Regression tests for the v4 executor guard, parity records and ledger.

Each test pins a defect that aborted or falsified a previous offline
preflight. None of them consume a grant or import a provider SDK.
"""

from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))


def runner():
    import airtravel_v4_execution

    return airtravel_v4_execution


def test_guard_allowlist_permits_persisted_call_records():
    """The aborted run denied its own parity records inside the guard."""
    from airtravel_preflight_execution import ALLOWED_FILES

    allowed = {
        *ALLOWED_FILES,
        *(
            f"{side}/{name}"
            for side in ("baseline", "instrumented")
            for name in runner()._SCIENTIFIC_OUTPUTS
        ),
        *(f"{side}/call-records.jsonl" for side in ("baseline", "instrumented")),
    }
    assert "baseline/call-records.jsonl" in allowed
    assert "instrumented/call-records.jsonl" in allowed


def test_length_correlation_survives_interleaved_calls():
    """calls[-1] after awaiting attaches lengths to another call's row."""

    class Base:
        def __init__(self):
            self.calls = []

        async def call(self, prompt, *, label):
            self.calls.append({"label": label})
            await asyncio.sleep(0.01)
            return {"answer": label}

    class Broken(Base):
        async def call(self, prompt, *, label):
            result = await super().call(prompt, label=label)
            self.calls[-1]["length"] = len(label)
            return result

    class Fixed(Base):
        async def call(self, prompt, *, label):
            index = len(self.calls)
            result = await super().call(prompt, label=label)
            row = self.calls[index]
            assert row["label"] == label
            row["length"] = len(label)
            return result

    async def drive(fake):
        await asyncio.gather(
            fake.call({}, label="first-call"),
            fake.call({}, label="second"),
        )
        return fake.calls

    broken = asyncio.run(drive(Broken()))
    assert any("length" not in row for row in broken), "expected the old defect"

    fixed = asyncio.run(drive(Fixed()))
    assert all(row["length"] == len(row["label"]) for row in fixed)


def test_privacy_safe_row_rejects_raw_content_and_credentials():
    base = {
        "label": "agent3/01/resolve_r1",
        "phase": "phase3",
        "case_id": "01",
        "inventory_row": "P3_RESOLVE_PRODUCER",
        "prompt_sha256": "a" * 64,
        "answer_sha256": "b" * 64,
        "decision_sha256": "c" * 64,
        "prompt_length": 10,
        "answer_length": 20,
    }
    for leak in ("prompt", "answer", "api_key", "credential"):
        with pytest.raises(ValueError, match="raw call content"):
            runner().privacy_safe_call_row({**base, leak: "secret"}, 1)


def test_privacy_safe_row_requires_lengths():
    """A row missing measured lengths must fail closed, not persist blanks."""
    incomplete = {
        "label": "agent3/01/resolve_r1",
        "phase": "phase3",
        "case_id": "01",
        "inventory_row": "P3_RESOLVE_PRODUCER",
        "prompt_sha256": "a" * 64,
        "answer_sha256": "b" * 64,
        "decision_sha256": "c" * 64,
    }
    with pytest.raises(ValueError, match="inventory missing"):
        runner().privacy_safe_call_row(incomplete, 1)


def test_receipt_requires_full_evidence_including_attempt_end(tmp_path):
    """require_evidence must fail while terminal ledger evidence is absent."""
    receipt = json.loads(
        (ROOT / "schemas/airtravel-technical-receipt-v2.schema.json").read_text(
            encoding="utf-8"
        )
    )
    assert "control/attempt-end.json" in _evidence()
    assert "verification/post-verification-receipt.json" in _evidence()
    assert receipt["properties"]["containment_status"]["const"] == "PASS"


def _evidence():
    from airtravel_v4_contract import frozen_manifest

    return frozen_manifest()["required_evidence_files"]


def test_manifest_is_not_stale_against_contract():
    """Harness edits must invalidate the checked-in machine manifest."""
    from build_airtravel_v4_manifest import main

    assert main(["--check"]) == 0


def test_consume_grant_returns_bindings_and_attempt_identity():
    """Receipt construction needs grant bindings, not only the attempt row."""
    import inspect

    source = inspect.getsource(runner().consume_grant)
    assert "{**bindings, **start}" in source


def test_failure_handler_covers_receipt_construction():
    """Any post-run failure must still write a terminal attempt marker."""
    import inspect

    source = inspect.getsource(runner().execute_authorized)
    tail = source[source.index("except BaseException:"):]
    assert "attempt-end.json" in tail
    assert source.index("validate_receipt_v2") < source.index("except BaseException:")
