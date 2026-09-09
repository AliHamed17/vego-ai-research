import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "VEGO-AI/framework"))


def test_empty_untrusted_stream_is_technical_failure():
    import render_airtravel_results as r

    assert hasattr(r, "zero_qa_status")
    assert r.zero_qa_status([], {"status": "FIXTURE_ONLY"}) == "INVALID_OR_INCOMPLETE_ZERO_QA"


def test_successful_zero_qa_requires_every_completion_proof(tmp_path):
    import render_airtravel_results as r

    assert hasattr(r, "zero_qa_status")
    from test_render_airtravel_results import _technical_fixture

    events = tmp_path / "events.jsonl"
    events.write_text("")
    receipt = _technical_fixture(events)
    receipt.pop("fixture_only")
    assert r.zero_qa_status([], receipt) == "VALID_ZERO_QA_RUN"
    for field in receipt:
        changed = {**receipt}
        changed.pop(field)
        assert r.zero_qa_status([], changed) == "INVALID_OR_INCOMPLETE_ZERO_QA"


def test_canonical_signal_totals_and_forward_route():
    import render_airtravel_results as r

    assert hasattr(r, "canonical_totals")
    # The renderer must count exactly what the frozen detector returned, not recalculate thresholds.
    corpus = {
        "detector_v1": [
            {
                "classification": "STRONG_ALERT",
                "all_signals_fired": ["S1_LOW_ANSWER_CONFIDENCE", "S2_MEDIUM_ANSWER_CONFIDENCE"],
                "reason_codes": ["S1_LOW_ANSWER_CONFIDENCE"],
                "exclusion_reason": None,
            }
        ],
        "events": [
            {
                "event_type": "QUESTION_EMITTED",
                "source_agent": "agent3",
                "target_agent": "agent1",
                "episode_id": "a",
            }
        ],
    }
    result = r.canonical_totals(corpus)
    assert result["signals"] == {"S1": 1, "S2": 1, "S3": 0, "S6": 0, "S7": 0}
    assert result["route_rows"] == "| `agent3 → agent1` | 1 |"


def test_unrestricted_claim_arguments_are_not_accepted(monkeypatch):
    import render_airtravel_results as r

    monkeypatch.setattr(
        sys, "argv", ["render_airtravel_results.py", "--findings", "scientific success"]
    )
    with pytest.raises(SystemExit):
        r.main()


@pytest.mark.parametrize(
    "changes",
    [
        {"corpus_id": "wrong"},
        {"corpus_id": None},
        {"N": 3},
        {"status": "FIXTURE_ONLY"},
        {"timeout": True},
    ],
)
def test_renderer_binding_rejects_wrong_identity(changes, tmp_path):
    import render_airtravel_results as r

    assert hasattr(r, "verify_run_receipt")
    from airtravel_preflight_contract import canonical, digest

    receipt = tmp_path / "receipt.json"
    receipt.write_bytes(canonical({"setting_id": "cd_airtravel", **changes}))
    events = tmp_path / "events.jsonl"
    events.write_text("")
    with pytest.raises(ValueError):
        r.verify_run_receipt(
            events, receipt, digest(receipt), "0" * 40, "LOCAL_DETERMINISTIC_FAKE_V3"
        )
