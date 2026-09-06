"""Real protected phase control flow, literal non-AirTravel engineering fixtures."""

import asyncio
import importlib
import sys
from dataclasses import asdict
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))


def observer_module():
    assert importlib.util.find_spec("airtravel_local_observer") is not None
    return importlib.import_module("airtravel_local_observer")


async def fixture(root, *, n=2, mode="two_rounds", observed=True, broken=False):
    m = observer_module()
    runtime = m.runtime()
    from qa_communication import QACommunicationRecorder
    from qa_registry import QARegistry
    from state import PipelineState

    recorder = QACommunicationRecorder(run_id="fixture-pr38") if observed else None
    observer = m.Observer(recorder)
    fake = m.RecordingFake(mode)
    if broken:

        async def broken_call(prompt, *, label):
            raise ValueError("fixture failure")

        original = fake.call

        async def call(prompt, *, label):
            return await (
                broken_call(prompt, label=label)
                if "answer_" in label
                else original(prompt, label=label)
            )

        fake.call = call
    client = m.Proxy(fake, observer, n, "fixture_only", "fixture-pr38") if observed else fake
    registry = observer.registry(QARegistry)() if observed else QARegistry()
    cfg = {
        "language_name": "Fixture",
        "domain_description": "Literal fixture",
        "max_concurrent_cases": 2,
        "case_models": [{"case_id": str(i), "case_model": "Literal fixture"} for i in range(n)],
    }
    state = PipelineState()
    try:
        for fn in (
            runtime.phase1_build_language_template,
            runtime.phase2_build_reference_guidelines,
            runtime.phase3_evaluate_cases,
            runtime.phase4_variability_analysis,
        ):
            if fn == runtime.phase1_build_language_template:
                await fn(cfg, state, client, root / "state.json")
            else:
                await fn(cfg, state, registry, client, root / "state.json")
        if recorder:
            m.validate_final_stream(recorder.events)
    except Exception:
        if recorder:
            recorder.close_open_episodes()
        if not broken:
            raise
    return fake.calls, asdict(state), recorder.events if recorder else []


@pytest.mark.parametrize("n,low,high", [(0, 4, 82), (1, 7, 143), (4, 16, 326)])
def test_source_bounds_through_real_phase_control_flow(tmp_path, n, low, high):
    assert len(asyncio.run(fixture(tmp_path / "min", n=n, mode="no_questions"))[0]) == low
    assert len(asyncio.run(fixture(tmp_path / "max", n=n, mode="max_rounds"))[0]) == high


def test_next_round_convergence_and_concurrent_case_identity(tmp_path):
    off = asyncio.run(fixture(tmp_path / "baseline", observed=False))
    on = asyncio.run(fixture(tmp_path / "instrumented"))
    assert off[:2] == on[:2]
    events = on[2]
    terms = [e for e in events if e["event_type"] == "EPISODE_TERMINATED"]
    assert len(terms) == 6
    assert all(e["termination_reason"] == "CONVERGED" for e in terms)
    questions = [e for e in events if e["event_type"] == "QUESTION_EMITTED"]
    assert {e["case_id"] for e in questions if e["source_agent"] == "agent3"} == {"0", "1"}
    assert len({e["episode_id"] for e in questions if e["source_agent"] == "agent3"}) == 4
    assert observer_module().route_metrics(events)["protected_orchestrator_fake_route_count"] == 6


def test_maximum_round_closes_without_inventing_convergence(tmp_path):
    _, _, events = asyncio.run(fixture(tmp_path, mode="max_rounds"))
    terms = [e for e in events if e["event_type"] == "EPISODE_TERMINATED"]
    assert len(terms) == 7
    assert all(
        e["termination_reason"] == "TERMINATED_MAX_ROUNDS" and e["round_index"] == 10 for e in terms
    )


def test_failure_closes_incomplete_and_excludes_from_detector(tmp_path):
    _, _, events = asyncio.run(fixture(tmp_path, broken=True))
    m = observer_module()
    m.validate_final_stream(events)
    from extract_qa_escalation_features import detect_detector_v1
    from qa_communication import build_episode_projection

    episodes = build_episode_projection(events)
    assert episodes and all(e["termination_reason"] == "INCOMPLETE_TECHNICAL" for e in episodes)
    assert all(detect_detector_v1(e)["classification"] == "EXCLUDED" for e in episodes)


def test_unterminated_stream_is_rejected():
    m = observer_module()
    m.runtime()
    from qa_communication import QACommunicationRecorder

    r = QACommunicationRecorder(run_id="fixture-open")
    r.emit_question(episode_id="e", question_id="q", question_text="fixture", round_index=1)
    with pytest.raises(ValueError):
        m.validate_final_stream(r.events)


def test_identity_is_independent_process_deterministic():
    import subprocess

    code = "from airtravel_local_observer import metadata; print(metadata('agent3/case01/resolve_r2','fixture','fixture')['episode_id'])"
    outputs = [
        subprocess.check_output([sys.executable, "-c", code], cwd=ROOT / "scripts", text=True)
        for _ in range(2)
    ]
    assert outputs[0] == outputs[1]
    m = observer_module()
    assert (
        m.metadata("agent3/case01/resolve_r1", "fixture", "fixture")["episode_id"]
        == m.metadata("agent3/case01/resolve_r2", "fixture", "fixture")["episode_id"]
    )
    assert (
        m.metadata("agent3/case02/resolve_r2", "fixture", "fixture")["episode_id"]
        != m.metadata("agent3/case01/resolve_r2", "fixture", "fixture")["episode_id"]
    )


def test_multiple_episodes_and_route_pairs_are_not_conflated():
    m = observer_module()
    events = [
        {"event_type": "QUESTION_EMITTED", "source_agent": s, "target_agent": t, "episode_id": e}
        for s, t, e in [
            ("agent3", "agent1", "a"),
            ("agent3", "agent1", "b"),
            ("agent3", "agent2", "a"),
        ]
    ]
    result = m.route_metrics(events)
    assert result["protected_orchestrator_fake_route_count"] == 2
    assert result["episode_count"] == 2 and result["question_count"] == 3
    assert result["routes"][0] == {
        "source_agent": "agent3",
        "target_agent": "agent1",
        "question_count": 2,
    }


def test_complete_protected_two_case_fixture_outputs_and_parity(tmp_path):
    from airtravel_execution_safety import ExecutionGuard, timed_operation
    from airtravel_preflight_execution import ALLOWED_FILES, run_pair

    m = observer_module()
    runtime = m.runtime()
    from qa_communication import validate_event_stream

    validate_event_stream([])
    cfg = {
        "setting_id": "fixture_only",
        "language_name": "Fixture",
        "domain_description": "Fixture domain",
        "case_models": [
            {"case_id": str(i), "case_model": "Literal test fixture"} for i in range(2)
        ],
        "max_concurrent_cases": 2,
    }

    async def guarded():
        try:
            with ExecutionGuard(
                tmp_path,
                ALLOWED_FILES,
                {ROOT / "VEGO-AI/framework/orchestrator.py"}
                | {p for p in ROOT.rglob("*.json") if ".git" not in p.parts},
            ):
                return await run_pair(cfg, tmp_path, runtime, fixture_only=True)
        except Exception:
            import traceback

            traceback.print_exc()
            raise

    result = asyncio.run(timed_operation(guarded, runtime, timeout=15))
    assert result["status"] == "TECHNICAL_SUCCESS", result
    assert all(
        result[k] for k in ("prompt_parity", "answer_parity", "state_parity", "output_parity")
    )
    assert result["processed_case_ids"] == ["0", "1"]
