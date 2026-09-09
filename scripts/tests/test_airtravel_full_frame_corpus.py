"""Tests for full-frame corpus materialisation and the run harness's declared bounds.

The materialiser's value is entirely in what it refuses. A digest check that passes when the
bytes are wrong, or that can be satisfied by writing the file it is meant to verify, would turn
a provenance guarantee into decoration. These tests therefore drive the failure paths: a tampered
archive, a tampered member, an absent member, and corruption introduced after the digest check.

The harness tests pin the two declared brakes — the reserve-based worst case and the rolling
budget guard — because a preregistration that cites a bound the code does not enforce is worse
than no bound at all.

No provider is contacted.
"""

from __future__ import annotations

import hashlib
import json
import sys
import zipfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

import airtravel_full_frame_corpus as corpus  # noqa: E402

MEMBER_ROOT = "text2uml-pinned/dataset/AirTravel/"


def build_archive(path: Path, files: dict[str, bytes]) -> None:
    with zipfile.ZipFile(path, "w") as archive:
        for name, data in files.items():
            archive.writestr(MEMBER_ROOT + name, data)


@pytest.fixture
def inventory_rows():
    payload = json.loads(corpus.INVENTORY.read_text(encoding="utf-8"))
    return payload["files"]


class TestEligibilityPredicate:
    def test_the_frame_holds_twenty_one_eligible_cases(self, inventory_rows):
        rows = corpus.eligible_rows({"files": inventory_rows})
        assert len(rows) == 21
        assert all(row["path"].startswith("result_one_") for row in rows)

    def test_the_predicate_is_deterministic_and_sorted(self, inventory_rows):
        first = [row["path"] for row in corpus.eligible_rows({"files": inventory_rows})]
        second = [row["path"] for row in corpus.eligible_rows({"files": inventory_rows})]
        assert first == second == sorted(first)

    @pytest.mark.parametrize(
        "override",
        [
            {"classification": "DOMAIN_DESCRIPTION_CANDIDATE"},
            {"path": "not_result_one.txt"},
            {"bytes": 0},
            {"syntax_validation": "MISSING_PLANTUML_WRAPPERS"},
            {"sha256": "short"},
        ],
    )
    def test_each_eligibility_condition_excludes_a_row(self, override):
        row = {
            "classification": "GENERATED_CANDIDATE_MODEL",
            "path": "result_one_x.txt",
            "bytes": 10,
            "syntax_validation": "WRAPPER_PRESENT",
            "sha256": "a" * 64,
        }
        assert corpus.eligible_rows({"files": [row]}) == [row]
        assert corpus.eligible_rows({"files": [{**row, **override}]}) == []


class TestArchiveVerificationRefuses:
    def test_a_tampered_archive_digest_is_refused(self, tmp_path):
        archive = tmp_path / "wrong.zip"
        build_archive(archive, {"description.md": b"anything"})
        with pytest.raises(corpus.ProvenanceError, match="archive digest"):
            corpus.materialise(archive, tmp_path / "runtime")

    def test_a_member_whose_bytes_do_not_match_is_refused(self):
        row = {"path": "result_one_x.txt", "sha256": hashlib.sha256(b"right").hexdigest(), "bytes": 5}
        members = {"result_one_x.txt": MEMBER_ROOT + "result_one_x.txt"}

        class FakeArchive:
            def read(self, _name):
                return b"wrong"

        with pytest.raises(corpus.ProvenanceError, match="does not match pinned"):
            corpus.read_verified(FakeArchive(), members, row)

    def test_a_member_absent_from_the_archive_is_refused(self):
        row = {"path": "missing.txt", "sha256": "a" * 64, "bytes": 1}
        with pytest.raises(corpus.ProvenanceError, match="absent from the pinned archive"):
            corpus.read_verified(None, {}, row)

    def test_a_correct_digest_with_the_wrong_length_is_refused(self):
        data = b"right"
        row = {"path": "x.txt", "sha256": hashlib.sha256(data).hexdigest(), "bytes": 999}
        members = {"x.txt": MEMBER_ROOT + "x.txt"}

        class FakeArchive:
            def read(self, _name):
                return data

        with pytest.raises(corpus.ProvenanceError, match="bytes"):
            corpus.read_verified(FakeArchive(), members, row)


class TestPostWriteVerification:
    def test_corruption_after_the_digest_check_is_detected(self, tmp_path):
        runtime = tmp_path / "runtime"
        (runtime / "candidate_models").mkdir(parents=True)
        target = runtime / "candidate_models/01_result_one_x.txt"
        target.write_bytes(b"original")
        contract = {
            "runtime_files": {
                "candidate_models/01_result_one_x.txt": {
                    "sha256": hashlib.sha256(b"original").hexdigest()
                }
            }
        }
        assert corpus.verify(runtime, contract) == []
        target.write_bytes(b"tampered")
        assert corpus.verify(runtime, contract) == [
            "candidate_models/01_result_one_x.txt: digest mismatch after write"
        ]

    def test_a_missing_file_is_reported_rather_than_skipped(self, tmp_path):
        contract = {"runtime_files": {"candidate_models/absent.txt": {"sha256": "a" * 64}}}
        assert corpus.verify(tmp_path, contract) == ["candidate_models/absent.txt: missing"]


class TestDeclaredRunBounds:
    def test_the_reserve_matches_the_preregistered_per_request_figure(self):
        import airtravel_full_frame_run as harness

        reserve = (
            harness.RESERVE_INPUT_TOKENS * harness.PRICE_IN_PER_M
            + harness.RESERVE_OUTPUT_TOKENS * harness.PRICE_OUT_PER_M
        ) / 1_000_000
        assert reserve == pytest.approx(0.0212608)
        assert harness.DEFAULT_MAX_REQUESTS * reserve == pytest.approx(4.890, abs=0.001)

    def test_the_configuration_matches_the_accepted_run_except_case_count(self):
        """Only the frame size may differ; a silent change to any other frozen value is a defect."""
        import airtravel_real_run as base
        import airtravel_full_frame_run as harness

        assert harness.MODEL == base.MODEL
        assert harness.RESERVE_OUTPUT_TOKENS == base.RESERVE_OUTPUT_TOKENS
        assert harness.RESERVE_INPUT_TOKENS == base.RESERVE_INPUT_TOKENS
        assert harness.REQUEST_TIMEOUT_SECONDS == base.REQUEST_TIMEOUT_SECONDS
        assert harness.MAX_CONCURRENT_CASES == base.MAX_CONCURRENT_CASES
        assert harness.SETTING_ID == base.SETTING_ID
        assert harness.CORPUS_ID == base.CORPUS_ID

    def test_the_budget_guard_refuses_a_request_it_cannot_fund(self):
        import airtravel_real_run as base

        guard = base.BudgetGuard(budget_usd=0.01, prior_spend_usd=0.0, max_requests=100)
        with pytest.raises(base.BudgetExceeded, match="budget"):
            guard.reserve()

    def test_the_request_cap_is_enforced_independently_of_the_budget(self):
        import airtravel_real_run as base

        guard = base.BudgetGuard(budget_usd=1000.0, prior_spend_usd=0.0, max_requests=1)
        guard.reserve()
        with pytest.raises(base.BudgetExceeded, match="request cap"):
            guard.reserve()

    def test_prior_spend_reduces_available_headroom(self):
        import airtravel_real_run as base

        guard = base.BudgetGuard(budget_usd=1.0, prior_spend_usd=0.99, max_requests=100)
        with pytest.raises(base.BudgetExceeded):
            guard.reserve()


class TestCallLedgerPrivacy:
    def test_the_ledger_records_counts_and_never_content(self):
        import airtravel_full_frame_run as harness

        class Usage:
            prompt_tokens, completion_tokens = 100, 200

        class Choice:
            finish_reason = "stop"

        class Response:
            usage, choices, model = Usage(), [Choice()], "gpt-5.6-luna"

        ledger = harness.CallLedger()
        ledger.record(1, Response(), 0.0)
        row = ledger.rows[0]
        assert set(row) == {
            "index", "prompt_tokens", "completion_tokens", "finish_reason", "truncated",
            "latency_seconds", "cost_usd", "model_reported",
        }
        assert row["truncated"] is False

    def test_a_length_finish_reason_is_counted_as_truncation(self):
        import airtravel_full_frame_run as harness

        class Usage:
            prompt_tokens, completion_tokens = 10, 16384

        class Choice:
            finish_reason = "length"

        class Response:
            usage, choices, model = Usage(), [Choice()], "gpt-5.6-luna"

        ledger = harness.CallLedger()
        ledger.record(1, Response(), 0.0)
        assert ledger.summary()["truncated_calls"] == 1
        assert ledger.summary()["max_completion_tokens_observed"] == 16384
