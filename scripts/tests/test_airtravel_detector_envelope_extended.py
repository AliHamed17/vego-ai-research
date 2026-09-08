"""Tests for the extended Detector-v1 envelope.

The unit tests pin the fixture's per-mode injection and schedule without running the
orchestrator: the mode table must agree with the frozen rule, new modes must inject exactly
the declared confidence and evidence, ask in exactly the declared rounds, and never trip the
parent's classify branch. One guarded integration test drives the real protected orchestrator
for a single new mode when the private runtime input is present. No provider is contacted and
Detector-v1 is never modified.
"""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

import airtravel_detector_envelope_extended as ext  # noqa: E402

STRONG = {ext.S1, ext.S3, ext.S7}
WEAK = {ext.S2, ext.S6}
NEW_MODES = [m for m in ext.MODES if m not in ext.LEGACY_MODES]
RUNTIME = ROOT / "external_data/airtravel-pr38/runtime_input/domain_description/description.md"


def frozen_rule(signals: set[str]) -> str:
    if signals & STRONG:
        return "STRONG_ALERT"
    return "WEAK_ALERT" if signals & WEAK else "NO_ALERT"


def answer_prompt(*ids: str) -> dict:
    body = ", ".join(f'{{"id": "{i}"}}' for i in ids)
    return {"system": f"Questions to be Answered: ** [{body}]"}


def run(coro):
    return asyncio.run(coro)


@pytest.fixture
def offline_fake(monkeypatch):
    """The parent ledger refuses calls that do not originate inside the protected orchestrator.

    Unit tests exercise the fixture directly, so the stack-inspecting inventory capture is
    replaced with an inert stub; the integration test below keeps the real one.
    """
    import airtravel_local_observer as observer

    monkeypatch.setattr(observer, "capture_call_inventory",
                        lambda label: {"inventory": "UNIT_TEST_STUB"})
    return ext.make_fake


@pytest.mark.parametrize("mode", [m for m in ext.MODES if ext.MODES[m]["expected"]])
def test_expected_class_follows_from_declared_signals(mode):
    spec = ext.MODES[mode]
    assert frozen_rule(set(spec["signals"])) == spec["expected"]


@pytest.mark.parametrize("mode", list(ext.MODES))
def test_declared_signals_follow_from_injected_values(mode):
    spec = ext.MODES[mode]
    signals = set(spec["signals"])
    rounds = spec["rounds"]
    assert (ext.S1 in signals) == (spec["confidence"] == "Low")
    assert (ext.S2 in signals) == (spec["confidence"] == "Medium")
    assert (ext.S3 in signals) == (spec["evidence"] in ("", None))
    assert (ext.S7 in signals) == (rounds == "all")
    assert (ext.S6 in signals) == (rounds == "all" or len(rounds) > 1)


def test_table_covers_every_class_and_every_isolable_branch():
    expected = {ext.MODES[m]["expected"] for m in ext.MODES} - {None}
    assert expected == {"STRONG_ALERT", "WEAK_ALERT", "NO_ALERT"}
    isolated = [frozenset(ext.MODES[m]["signals"]) for m in ext.MODES]
    for single in (ext.S1, ext.S3, ext.S2, ext.S6):
        assert frozenset({single}) in isolated
    assert sum(1 for m in ext.MODES if ext.MODES[m]["evidence"] in ("", None)) == 2


@pytest.mark.parametrize("mode", list(ext.LEGACY_MODES))
def test_legacy_modes_return_the_parent_class_unchanged(mode):
    from airtravel_local_observer import RecordingFake

    fake = ext.make_fake(mode)
    assert type(fake) is RecordingFake
    assert fake.mode == mode


@pytest.mark.parametrize("mode", NEW_MODES)
def test_answer_rows_carry_the_injected_confidence_and_evidence(mode, offline_fake):
    spec = ext.MODES[mode]
    fake = offline_fake(mode)
    result = run(fake.call(answer_prompt("Q-1", "Q-2"), label="agent2/answer_domain_questions"))
    rows = result["questions_answers"]
    assert [r["question_id"] for r in rows] == ["Q-1", "Q-2"]
    for row in rows:
        assert row["confidence"] == spec["confidence"]
        if spec["evidence"] is None:
            assert "evidence" not in row
        else:
            assert row["evidence"] == spec["evidence"]


def test_null_and_empty_evidence_are_distinct_encodings(offline_fake):
    null = run(offline_fake("null_evidence_single").call(
        answer_prompt("Q"), label="agent1/answer_language_questions"))
    empty = run(offline_fake("empty_evidence_single").call(
        answer_prompt("Q"), label="agent1/answer_language_questions"))
    assert "evidence" not in null["questions_answers"][0]
    assert empty["questions_answers"][0]["evidence"] == ""


@pytest.mark.parametrize("mode", NEW_MODES)
def test_questions_are_emitted_in_exactly_the_declared_rounds(mode, offline_fake):
    spec = ext.MODES[mode]
    fake = offline_fake(mode)
    for r in (1, 2, 3):
        result = run(fake.call({"system": "x"}, label=f"agent4/01/resolve_r{r}"))
        asked = bool(result["questions_to_language_advisor"])
        assert asked == (r in spec["rounds"]), (mode, r)
        assert bool(result["questions_to_domain_advisor"]) == asked


def test_feedback_labels_route_to_the_language_advisor_only(offline_fake):
    fake = offline_fake("medium_single")
    result = run(fake.call({"system": "x"}, label="agent2/guidelines_feedback_r1"))
    assert result["questions_to_language_advisor"]
    assert result["questions_to_domain_advisor"] == []


@pytest.mark.parametrize("mode", NEW_MODES)
def test_new_modes_never_inject_the_parent_classify_row(mode, offline_fake):
    fake = offline_fake(mode)
    result = run(fake.call({"system": "x"}, label="agent4/classify_r1"))
    assert result["variability_classifications"] == []


def test_legacy_max_rounds_still_injects_the_classify_row(offline_fake):
    fake = offline_fake("max_rounds")
    result = run(fake.call({"system": "x"}, label="agent4/classify_r1"))
    assert result["variability_classifications"]


def test_unrelated_labels_pass_through_unchanged(offline_fake):
    fake = offline_fake("low_single")
    result = run(fake.call({"system": "x"}, label="agent4/identify_patterns"))
    assert result == {"deviation_patterns": []}


def test_ledger_digests_describe_the_mutated_result(offline_fake):
    from airtravel_local_observer import digest

    fake = offline_fake("low_single")
    result = run(fake.call(answer_prompt("Q"), label="agent2/answer_domain_questions"))
    record = fake.calls[-1]
    assert record["answer_sha256"] == digest(result)
    assert record["decision_sha256"] == digest(result)
    assert record["label"] == "agent2/answer_domain_questions"


@pytest.mark.parametrize("mode", NEW_MODES)
def test_new_modes_keep_the_parent_in_its_no_questions_state(mode):
    fake = ext.make_fake(mode)
    assert fake.mode == "no_questions"
    assert fake.fixture_mode == mode


def test_concurrent_calls_refresh_their_own_ledger_rows(offline_fake):
    from airtravel_local_observer import digest

    fake = offline_fake("low_single")

    async def two():
        return await asyncio.gather(
            fake.call(answer_prompt("Q-A"), label="agent2/answer_domain_questions"),
            fake.call(answer_prompt("Q-B"), label="agent1/answer_language_questions"),
        )

    result_a, result_b = run(two())
    assert result_a != result_b
    assert [r["label"] for r in fake.calls] == ["agent2/answer_domain_questions", "agent1/answer_language_questions"]
    assert fake.calls[0]["answer_sha256"] == digest(result_a)
    assert fake.calls[1]["answer_sha256"] == digest(result_b)


def test_ledger_cap_is_inherited(offline_fake):
    from airtravel_local_observer import worst_case_calls

    fake = offline_fake("medium_single")
    for _ in range(worst_case_calls(4)):
        run(fake.call({"system": "x"}, label="agent4/identify_patterns"))
    with pytest.raises(ValueError, match="maximum exceeded"):
        run(fake.call({"system": "x"}, label="agent4/identify_patterns"))


@pytest.mark.skipif(not RUNTIME.is_file(), reason="private runtime input not present")
def test_medium_single_reaches_weak_alert_through_the_real_orchestrator():
    before = sorted(p.name for p in ext.SCRATCH_ROOT.iterdir()) if ext.SCRATCH_ROOT.is_dir() else []
    row = ext.run_mode("medium_single")
    after = sorted(p.name for p in ext.SCRATCH_ROOT.iterdir()) if ext.SCRATCH_ROOT.is_dir() else []
    assert after == before, "orchestrator output must not remain after the run"
    assert ext.SCRATCH_ROOT.is_relative_to(ext.ROOT / "external_data")
    assert row["provider_calls"] == 0
    assert row["detector_denominator"] > 0
    assert row["detector_v1"]["WEAK_ALERT"] == row["detector_denominator"]
    assert row["signals_fired_any_episode"] == [ext.S2]
    assert row["conforms_to_frozen_rule"] is True
    assert row["evidence_class"] == "ENGINEERING_FIXTURE_NOT_SCIENTIFIC"
