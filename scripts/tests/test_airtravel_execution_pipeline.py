"""Synthetic-only lifecycle tests: no corpus bytes, SDK, credentials or transport."""

from __future__ import annotations

import asyncio
import hashlib
import importlib
import json
import os
import subprocess
import sys
from dataclasses import replace
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path

import pytest
from qa_communication import QACommunicationRecorder, build_episode_projection, load_event_stream

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
contract = importlib.import_module("airtravel_execution_contract")
boundary = importlib.import_module("airtravel_execution_provider")

STAGES = (
    ("agent2", "phase2_guideline_build", "build_guidelines"),
    ("agent3", "phase3_case_inspection", "inspect_case"),
    ("agent4", "phase4_variability_classification", "classify_variability"),
)


def module():
    assert importlib.util.find_spec("airtravel_execution_pipeline") is not None, (
        "isolated lifecycle pipeline is missing"
    )
    return importlib.import_module("airtravel_execution_pipeline")


def config(**changes):
    return replace(
        contract.ExecutionConfig(
            model="test-model", provider_host="api.openai.com", max_usd=Decimal("6.00"),
            timeout_seconds=1, run_timeout_seconds=30, max_retries=0, concurrency=1,
            max_calls=100, max_input_tokens=10000, max_output_tokens=1000,
            max_rounds=2,
            price_schedule=contract.PriceSchedule(
                "https://openai.com/api/pricing/", datetime(2026, 9, 12, tzinfo=timezone.utc),
                Decimal("1"), Decimal("1"),
            ),
        ), **changes,
    )


def frame(cfg, *, run_id="synthetic-run", max_rounds=2):
    pipeline = module()
    domain = "Synthetic domain description; no real source content."
    source_paths = ["description.md"] + [
        f"result_one_{name}.txt"
        for name in ("claude-sonnet-4-6", "codestral-2508", "deepseek-chat", "gemini-2.5-flash")
    ]
    cases = tuple(
        pipeline.PipelineCase(f"{i:02}", f"candidate_models/{i:02d}_{name}", f"Synthetic model {i}.")
        for i, name in enumerate(source_paths[1:], 1)
    )
    files = (("domain_description/description.md", domain),) + tuple(
        (row.candidate_path, row.candidate_text) for row in cases
    )
    manifest = contract.VerifiedInputManifest(
        code_sha="a" * 40, config_sha256=cfg.sha256,
        verification_sha256="b" * 64, source_inventory_sha256="c" * 64,
        source_archive_sha256=contract.PUBLIC_AIRTRAVEL_ARCHIVE_SHA256,
        source_commit=contract.PUBLIC_AIRTRAVEL_COMMIT,
        max_rounds=cfg.max_rounds, call_inventory_sha256=cfg.call_inventory_sha256,
        full_run_reservation=cfg.full_run_reservation,
        runtime_files=tuple(
            contract.RuntimeFileBinding(source, path, len(text.encode()), hashlib.sha256(text.encode()).hexdigest())
            for source, (path, text) in zip(source_paths, files, strict=True)
        ),
    )
    return pipeline.VerifiedPipelineFrame(
        run_id=run_id, setting_id="cd_airtravel", corpus_id="text2uml_airtravel_253b26dc",
        input_manifest=manifest, domain_description=domain, cases=cases, max_rounds=max_rounds,
    )


def test_frame_round_policy_cannot_differ_from_bound_manifest():
    with pytest.raises(module().PipelineFailure):
        frame(config(), max_rounds=3)


def test_pipeline_rejects_round_mismatch_even_with_rebound_config_hash(tmp_path):
    cfg = config(max_rounds=3)
    original = frame(config())
    rebound = replace(original, input_manifest=replace(original.input_manifest, config_sha256=cfg.sha256))
    with pytest.raises(module().PipelineFailure):
        run_fixture(tmp_path, cfg=cfg, frame_value=rebound)


def envelope(output):
    return {"output": output, "input_tokens": 10, "output_tokens": 5}


def decision(*, question=None, complete=True):
    return envelope({"stage_output": "Synthetic stage output.", "complete": complete,
                     "questions": [] if question is None else [question]})


def question(text="Synthetic generated question with actual text.", **changes):
    return {
        "question_text": text, "answering_agent": "agent1", "scope": "language",
        "guideline_id": None, "pattern_id": None, **changes,
    }


def identity(*, run_id="synthetic-run", case_id="01", agent="agent2",
             stage="phase2_guideline_build", skill="build_guidelines", **changes):
    return dict(run_id=run_id, setting_id="cd_airtravel", source_agent=agent, stage=stage,
                skill=skill, target_agent="agent1", scope="language", case_id=case_id,
                guideline_id=None, pattern_id=None, **changes)


def answer(identity_fields, *, round_index=1, **changes):
    episode_id = module().stable_episode_id(**identity_fields)
    return envelope({
        "run_id": identity_fields["run_id"], "episode_id": episode_id,
        "question_id": f"{episode_id}:q:{round_index}",
        "answer_text": "Synthetic answer to the exact generated question.",
        "answer_confidence": "High", "evidence_ref": "Synthetic evidence.",
        "source_tier": "synthetic", **changes,
    })


def outcomes(*, qa_cases=(), qa_agents=("agent2",), rounds=1, malformed=None):
    rows = []
    for case in range(1, 5):
        case_id = f"{case:02}"
        rows.append(envelope({"context": "Synthetic context."}))
        for agent, stage, skill in STAGES:
            if case_id in qa_cases and agent in qa_agents:
                for index in range(1, rounds + 1):
                    rows.append(decision(question=question(), complete=False))
                    response = answer(identity(case_id=case_id, agent=agent, stage=stage, skill=skill),
                                      round_index=index)
                    if malformed and case == 1 and index == 1:
                        response = malformed(response)
                    rows.append(response)
                if rounds < 2:
                    rows.append(decision())
            else:
                rows.append(decision())
    return rows


def run_fixture(tmp_path, *, cfg=None, rows=None, recorder_type=QACommunicationRecorder,
                frame_value=None):
    pipeline = module()
    cfg = cfg or config()
    frame_value = frame_value or frame(cfg)
    provider = boundary.DeterministicFakeProvider(rows if rows is not None else outcomes())
    ledger = boundary.BudgetLedger(cfg)
    recorder = recorder_type(tmp_path / "qa_events.jsonl", run_id=frame_value.run_id)
    result = asyncio.run(pipeline.run_airtravel_pipeline(
        config=cfg, frame=frame_value, provider=provider, ledger=ledger,
        recorder=recorder, runtime_root=tmp_path, max_rounds=frame_value.max_rounds,
    ))
    return result, recorder, ledger


def test_zero_qa_requires_all_four_cases_and_all_stage_receipts(tmp_path):
    result, _, ledger = run_fixture(tmp_path)
    assert result.status == "PASS"
    assert result.receipt["lifecycle_complete"] is True
    assert result.receipt["completed_case_count"] == 4
    assert result.receipt["completed_stage_count"] == 16
    assert result.receipt["question_count"] == result.receipt["answer_count"] == 0
    assert json.loads(result.detector_path.read_text())["episodes"] == []
    assert result.receipt["agent4_queue_status"] == "NOT_AVAILABLE"
    assert ledger.physical_call_count == 16
    assert ledger.external_provider_call_count == 0


@pytest.mark.parametrize("phase", ["context", "answer"])
@pytest.mark.parametrize("reason", ["HOST_REJECTED", "REDIRECT_REJECTED", "SDK_LOGGING_UNSAFE"])
def test_pipeline_preserves_sanitized_egress_denial(tmp_path, monkeypatch, phase, reason):
    original = boundary.DeterministicFakeProvider.call

    async def rejected(self, prompt, *, label):
        if phase == "context" or "/answer/" in label:
            try:
                raise boundary.TechnicalProviderFailure(reason)
            except boundary.TechnicalProviderFailure as error:
                raise RuntimeError("SYNTHETIC_PRIVATE_PROVIDER_EXCEPTION") from error
        return await original(self, prompt, label=label)

    monkeypatch.setattr(boundary.DeterministicFakeProvider, "call", rejected)
    result, recorder, ledger = run_fixture(tmp_path, rows=outcomes(qa_cases=("01",)))
    assert result.status == "INCOMPLETE_TECHNICAL"
    assert result.receipt["technical_error_code"] == "EGRESS_BLOCKED"
    assert ledger.external_provider_call_count == 0
    assert result.detector_path is None
    if phase == "answer":
        assert recorder.events[-1]["termination_reason"] == "INCOMPLETE_TECHNICAL"
    for path in tmp_path.iterdir():
        assert "SYNTHETIC_PRIVATE_PROVIDER_EXCEPTION" not in path.read_text(encoding="utf-8")


def test_empty_unfinished_run_is_not_a_valid_zero_qa_result(tmp_path):
    result, _, _ = run_fixture(tmp_path, rows=["malformed"])
    assert result.status == "INCOMPLETE_TECHNICAL"
    assert result.receipt["lifecycle_complete"] is False
    assert result.receipt["technical_error_code"] == "MALFORMED_RESPONSE"
    assert result.receipt["question_count"] == 0
    assert result.detector_path is None


def test_actual_questions_and_agent_234_metadata_are_preserved(tmp_path):
    result, recorder, _ = run_fixture(
        tmp_path, rows=outcomes(qa_cases=("01",), qa_agents=("agent2", "agent3", "agent4")),
    )
    assert result.status == "PASS"
    episodes = build_episode_projection(load_event_stream(result.qa_events_path))
    assert len(episodes) == 3
    assert all(row["termination_reason"] == "CONVERGED" for row in episodes)
    for agent, stage, skill in STAGES:
        rows = [event for event in recorder.events if event["source_agent"] == agent]
        q, a, terminal = rows
        assert q["question_text_ref"] == {
            "sha256": hashlib.sha256(b"Synthetic generated question with actual text.").hexdigest(),
            "length": 46,
        }
        assert a["question_id"] == q["question_id"]
        assert a["episode_id"] == q["episode_id"]
        for event in (q, a, terminal):
            assert (event["source_stage"], event["source_skill"], event["case_id"],
                    event["round_index"], event["target_agent"]) == (stage, skill, "01", 1, "agent1")
    assert {path.name for path in tmp_path.iterdir()} == {
        "qa_events.jsonl", "pipeline_manifest.json", "episode_projection.json", "detector_v1.json",
    }
    all_private_text = "\n".join(path.read_text() for path in tmp_path.iterdir())
    assert "Synthetic generated question" not in all_private_text
    assert "Synthetic answer" not in all_private_text
    assert "Synthetic model" not in all_private_text


def test_two_cases_keep_stable_episode_identity_across_rounds(tmp_path):
    result, _, _ = run_fixture(tmp_path, rows=outcomes(qa_cases=("01", "02"), rounds=2))
    episodes = build_episode_projection(load_event_stream(result.qa_events_path))
    assert len(episodes) == 2
    assert len({row["episode_id"] for row in episodes}) == 2
    assert all(row["question_count"] == row["answer_count"] == 2 for row in episodes)
    assert all(row["termination_reason"] == "TERMINATED_MAX_ROUNDS" for row in episodes)
    assert all(row["follow_up_present"] for row in episodes)
    assert result.receipt["lifecycle_summary"]["TERMINATED_MAX_ROUNDS"] == 2


def test_identity_changes_for_each_frozen_dimension_and_is_process_stable():
    pipeline = module()
    original = identity()
    expected = pipeline.stable_episode_id(**original)
    for field in original:
        variant = dict(original, **{field: "different"})
        assert pipeline.stable_episode_id(**variant) != expected
    command = [sys.executable, "-c", "import json; from airtravel_execution_pipeline import stable_episode_id; "
               "print(stable_episode_id(**json.loads(__import__('sys').argv[1])))", json.dumps(original)]
    for seed in ("1", "98"):
        env = dict(os.environ, PYTHONPATH=os.pathsep.join([str(ROOT / "scripts"), str(ROOT / "VEGO-AI/framework")]),
                   PYTHONHASHSEED=seed)
        assert subprocess.run(command, env=env, capture_output=True, text=True, check=True).stdout.strip() == expected


@pytest.mark.parametrize("change", [
    {"question_id": "unknown"}, {"episode_id": "another-episode"}, {"run_id": "another-run"},
    {"answer_text": ""}, {"answer_confidence": "Certain"},
])
def test_wrong_or_missing_answer_fails_closed(tmp_path, change):
    def malformed(value):
        return {**value, "output": {**value["output"], **change}}
    result, recorder, _ = run_fixture(tmp_path, rows=outcomes(qa_cases=("01",), malformed=malformed))
    assert result.status == "INCOMPLETE_TECHNICAL"
    assert result.receipt["technical_error_code"] == "MALFORMED_RESPONSE"
    assert result.detector_path is None
    assert recorder.events[-1]["termination_reason"] == "INCOMPLETE_TECHNICAL"
    assert all(event["event_type"] != "ANSWER_RECEIVED" for event in recorder.events)


@pytest.mark.parametrize("bad_question", [
    question(""), {key: value for key, value in question().items() if key != "question_text"},
    {**question(), "fixture_question": "Synthetic fallback must not be used."},
])
def test_no_fixture_question_fallback(tmp_path, bad_question):
    rows = [envelope({"context": "Synthetic context."}), decision(question=bad_question, complete=False)]
    result, recorder, ledger = run_fixture(tmp_path, rows=rows)
    assert result.status == "INCOMPLETE_TECHNICAL"
    assert result.receipt["technical_error_code"] == "MALFORMED_RESPONSE"
    assert not recorder.events
    assert ledger.physical_call_count == 2


@pytest.mark.parametrize("failure", ["missing", "duplicate", "cross_episode", "metadata"])
def test_malformed_recorded_answers_are_not_sent_to_detector(tmp_path, failure):
    class BrokenRecorder(QACommunicationRecorder):
        def emit_answer(self, **kwargs):
            if failure == "missing":
                return dict(kwargs["question"])
            if failure in {"cross_episode", "metadata"}:
                key, value = ("episode_id", "wrong-episode") if failure == "cross_episode" else ("case_id", "04")
                kwargs["question"] = {**kwargs["question"], key: value}
            event = super().emit_answer(**kwargs)
            if failure == "duplicate":
                super().emit_answer(**kwargs)
            return event
    result, _, _ = run_fixture(tmp_path, rows=outcomes(qa_cases=("01",)), recorder_type=BrokenRecorder)
    assert result.status == "INCOMPLETE_TECHNICAL"
    assert result.receipt["technical_error_code"] == "MALFORMED_RESPONSE"
    assert result.detector_path is None
    assert not (tmp_path / "detector_v1.json").exists()


def test_no_events_or_provider_call_after_terminal(tmp_path):
    result, recorder, ledger = run_fixture(tmp_path, rows=outcomes(qa_cases=("01",)))
    before = len(recorder.events)
    provider = boundary.DeterministicFakeProvider([answer(identity(), round_index=2)])
    with pytest.raises(module().PipelineFailure, match="MALFORMED_RESPONSE"):
        asyncio.run(module().route_question_answer(
            asking_agent="agent2", answering_agent="agent1", case_id="01",
            stage=STAGES[0][1], skill=STAGES[0][2], scope="language",
            question_text="Synthetic late question.", provider=provider, ledger=ledger,
            recorder=recorder, run_id="synthetic-run", setting_id="cd_airtravel", round_index=2,
        ))
    assert len(recorder.events) == before
    assert provider.physical_call_count == 0
    assert result.status == "PASS"


@pytest.mark.parametrize("code", ["TIMEOUT", "CALL_CAP_EXCEEDED"])
def test_provider_failures_close_open_episode_with_controlled_code(tmp_path, code):
    cfg = config(max_calls=2) if code == "CALL_CAP_EXCEEDED" else config()
    rows = [envelope({"context": "Synthetic context."}), decision(question=question(), complete=False), "timeout"]
    result, recorder, _ = run_fixture(tmp_path, cfg=cfg, rows=rows)
    assert result.status == "INCOMPLETE_TECHNICAL"
    assert result.receipt["technical_error_code"] == code
    if recorder.events:
        assert recorder.events[-1]["termination_reason"] == "INCOMPLETE_TECHNICAL"


def test_unaffordable_pipeline_is_rejected_before_any_episode_or_output(tmp_path):
    cfg = config(price_schedule=replace(config().price_schedule,
                 input_usd_per_million_tokens=Decimal("5000")))
    with pytest.raises(boundary.TechnicalProviderFailure, match="^BUDGET_EXCEEDED$"):
        run_fixture(tmp_path, cfg=cfg, rows=outcomes(qa_cases=("01",)))
    assert not list(tmp_path.rglob("*.jsonl"))
    assert not list(tmp_path.rglob("*.json"))


@pytest.mark.parametrize("label", ["C1", "C2", "C3", "Alternative", "Non-Satisfied"])
def test_non_detector_labels_never_become_detector_reasons(tmp_path, label):
    rows = outcomes(qa_cases=("01",))
    rows[1]["output"]["stage_output"] = label
    rows[2]["output"]["answer_text"] = label
    result, _, _ = run_fixture(tmp_path, rows=rows)
    detector = json.loads(result.detector_path.read_text())["detector_v1"]
    assert len(detector) == 1
    assert detector[0]["classification"] == "NO_ALERT"
    assert detector[0]["reason_codes"] == detector[0]["all_signals_fired"] == []


@pytest.mark.parametrize("max_rounds", [0, 11, True, 1.5, "2"])
def test_invalid_round_bound_fails_before_calls(max_rounds):
    with pytest.raises(module().PipelineFailure, match="MALFORMED_RESPONSE"):
        frame(config(), max_rounds=max_rounds)


def test_mismatched_round_bound_or_config_is_rejected_before_calls(tmp_path):
    pipeline = module()
    cfg = config()
    frm = frame(cfg)
    for supplied_cfg, supplied_rounds in ((cfg, 3), (config(max_calls=99), 2)):
        provider = boundary.DeterministicFakeProvider()
        with pytest.raises(pipeline.PipelineFailure, match="MALFORMED_RESPONSE"):
            asyncio.run(pipeline.run_airtravel_pipeline(
                config=supplied_cfg, frame=frm, provider=provider, ledger=boundary.BudgetLedger(supplied_cfg),
                recorder=QACommunicationRecorder(tmp_path / "qa_events.jsonl", run_id=frm.run_id),
                runtime_root=tmp_path, max_rounds=supplied_rounds,
            ))
        assert provider.physical_call_count == 0
        assert not list(tmp_path.iterdir())


def test_call_inventory_is_explicit_and_not_derived_from_cap(tmp_path):
    result, _, ledger = run_fixture(tmp_path)
    inventory = result.call_inventory
    assert inventory["max_rounds"] == 2
    assert inventory["case_count"] == 4
    assert inventory["minimum_calls"] == 16
    assert inventory["maximum_calls"] == 52
    assert inventory["automatic_retries"] == 0
    assert result.receipt["physical_call_count"] == ledger.physical_call_count == 16


def test_frame_rejects_unbound_bytes_and_not_four_unique_cases():
    pipeline = module()
    frm = frame(config())
    for changes in ({"domain_description": "Unbound synthetic replacement."},
                    {"cases": frm.cases[:3]}, {"cases": (frm.cases[0],) * 4}):
        with pytest.raises(pipeline.PipelineFailure, match="MALFORMED_RESPONSE"):
            replace(frm, **changes)


def test_recorder_outside_private_root_is_rejected_without_writes(tmp_path):
    pipeline = module()
    cfg = config()
    private = tmp_path / "private"
    private.mkdir()
    provider = boundary.DeterministicFakeProvider()
    with pytest.raises(pipeline.PipelineFailure, match="MALFORMED_RESPONSE"):
        asyncio.run(pipeline.run_airtravel_pipeline(
            config=cfg, frame=frame(cfg), provider=provider, ledger=boundary.BudgetLedger(cfg),
            recorder=QACommunicationRecorder(tmp_path / "escape.jsonl", run_id="synthetic-run"),
            runtime_root=private, max_rounds=2,
        ))
    assert provider.physical_call_count == 0
    assert not (tmp_path / "escape.jsonl").exists()


def test_two_concurrent_cases_keep_stable_episode_identity(tmp_path, monkeypatch):
    pipeline = module()
    original = boundary.DeterministicFakeProvider.call

    async def interleave(self, prompt, *, label):
        await asyncio.sleep(0)
        return await original(self, prompt, label=label)

    monkeypatch.setattr(boundary.DeterministicFakeProvider, "call", interleave)
    recorder = QACommunicationRecorder(tmp_path / "qa_events.jsonl", run_id="synthetic-run")

    async def case_work(case_id):
        provider = boundary.DeterministicFakeProvider([
            answer(identity(case_id=case_id), round_index=index) for index in (1, 2)
        ])
        ledger = boundary.BudgetLedger(config())
        previous = None
        for index in (1, 2):
            exchange = await pipeline.route_question_answer(
                asking_agent="agent2", answering_agent="agent1", case_id=case_id,
                stage=STAGES[0][1], skill=STAGES[0][2], scope="language",
                question_text=f"Synthetic concurrent question {case_id}/{index}.",
                provider=provider, ledger=ledger, recorder=recorder, run_id="synthetic-run",
                setting_id="cd_airtravel", round_index=index,
                follow_up_to_event_id=previous["event_id"] if previous else None,
            )
            previous = exchange["question_event"]
        recorder.emit_termination(episode_id=previous["episode_id"],
                                  termination_reason="TERMINATED_MAX_ROUNDS", converged=False)

    async def both():
        await asyncio.gather(case_work("01"), case_work("02"))

    asyncio.run(both())
    episodes = build_episode_projection(load_event_stream(recorder.path))
    assert len(episodes) == 2
    assert all(row["question_count"] == row["answer_count"] == 2 for row in episodes)
    assert [event["case_id"] for event in recorder.events[:2]] == ["01", "02"]
    assert all(event["event_type"] == "QUESTION_EMITTED" for event in recorder.events[:2])


@pytest.mark.parametrize("mutation", ["question_text", "source_agent", "answer_text", "answer_confidence", "answer_evidence"])
def test_recorder_cannot_substitute_question_or_answer_payload(tmp_path, mutation):
    class SubstitutingRecorder(QACommunicationRecorder):
        def emit_question(self, **kwargs):
            if mutation in {"question_text", "source_agent"}:
                kwargs[mutation] = "Synthetic fallback." if mutation == "question_text" else "agent4"
            return super().emit_question(**kwargs)

        def emit_answer(self, **kwargs):
            if mutation.startswith("answer_"):
                kwargs[mutation] = "Low" if mutation == "answer_confidence" else "Synthetic replacement."
            return super().emit_answer(**kwargs)

    result, _, _ = run_fixture(tmp_path, rows=outcomes(qa_cases=("01",)), recorder_type=SubstitutingRecorder)
    assert result.status == "INCOMPLETE_TECHNICAL"
    assert result.receipt["technical_error_code"] == "MALFORMED_RESPONSE"
    assert result.detector_path is None


def test_actual_generated_question_reaches_answer_prompt(tmp_path, monkeypatch):
    original = boundary.DeterministicFakeProvider.call
    observed = []

    async def inspect(self, prompt, *, label):
        if "/answer/" in label:
            observed.append(json.loads(prompt["user"]))
        return await original(self, prompt, label=label)

    monkeypatch.setattr(boundary.DeterministicFakeProvider, "call", inspect)
    result, recorder, _ = run_fixture(tmp_path, rows=outcomes(qa_cases=("01",)))
    assert result.status == "PASS"
    assert len(observed) == 1
    assert observed[0]["question_text"] == "Synthetic generated question with actual text."
    assert observed[0]["question_id"] == recorder.events[0]["question_id"]
    assert observed[0]["episode_id"] == recorder.events[0]["episode_id"]


def test_cancellation_persists_incomplete_receipt_and_closes_question(tmp_path, monkeypatch):
    original = boundary.DeterministicFakeProvider.call

    async def cancel_answer(self, prompt, *, label):
        if "/answer/" in label:
            raise asyncio.CancelledError("Synthetic private cancellation details.")
        return await original(self, prompt, label=label)

    monkeypatch.setattr(boundary.DeterministicFakeProvider, "call", cancel_answer)
    # Python 3.10's asyncio runner clears the message on a task-level
    # CancelledError; the persisted receipt is the authoritative code.
    with pytest.raises(asyncio.CancelledError) as raised:
        run_fixture(tmp_path, rows=outcomes(qa_cases=("01",)))
    assert str(raised.value) in {"", "CANCELLED"}
    manifest_text = (tmp_path / "pipeline_manifest.json").read_text()
    assert "Synthetic private" not in manifest_text
    receipt = json.loads(manifest_text)["receipt"]
    assert receipt["status"] == "INCOMPLETE_TECHNICAL"
    assert receipt["lifecycle_complete"] is False
    events = load_event_stream(tmp_path / "qa_events.jsonl")
    assert events[-1]["termination_reason"] == "INCOMPLETE_TECHNICAL"
    assert not (tmp_path / "detector_v1.json").exists()


def test_post_terminal_event_stream_never_reaches_detector(tmp_path):
    class LateRecorder(QACommunicationRecorder):
        def emit_termination(self, **kwargs):
            event = super().emit_termination(**kwargs)
            late = dict(self.events[0], sequence=len(self.events) + 1, question_id="late-question")
            stable = {key: value for key, value in late.items() if key not in {"event_id", "timestamp"}}
            late["event_id"] = hashlib.sha256(json.dumps(stable, sort_keys=True, separators=(",", ":"),
                                                        ensure_ascii=False).encode()).hexdigest()
            self.events.append(late)
            with self.path.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(late) + "\n")
            return event

    result, _, _ = run_fixture(tmp_path, rows=outcomes(qa_cases=("01",)), recorder_type=LateRecorder)
    assert result.status == "INCOMPLETE_TECHNICAL"
    assert result.receipt["technical_error_code"] == "MALFORMED_RESPONSE"
    assert result.detector_path is None


def test_existing_private_artifact_is_never_overwritten(tmp_path):
    existing = tmp_path / "pipeline_manifest.json"
    existing.write_text("Synthetic pre-existing artifact.", encoding="utf-8")
    with pytest.raises(module().PipelineFailure, match="MALFORMED_RESPONSE"):
        run_fixture(tmp_path)
    assert existing.read_text() == "Synthetic pre-existing artifact."
    assert not (tmp_path / "qa_events.jsonl").exists()


@pytest.mark.parametrize("complete,questions", [(False, []), (True, [question()]), (False, [question(), question()])])
def test_inconsistent_stage_lifecycle_response_fails_closed(tmp_path, complete, questions):
    rows = [envelope({"context": "Synthetic context."}), envelope({
        "stage_output": "Synthetic output.", "complete": complete, "questions": questions,
    })]
    result, _, _ = run_fixture(tmp_path, rows=rows)
    assert result.status == "INCOMPLETE_TECHNICAL"
    assert result.receipt["technical_error_code"] == "MALFORMED_RESPONSE"


def test_stage_cannot_switch_episode_identity_mid_loop(tmp_path):
    rows = outcomes(qa_cases=("01",), rounds=2)
    rows[3]["output"]["questions"][0]["pattern_id"] = "p-0123456789abcdef"
    fields = identity()
    fields["pattern_id"] = "p-0123456789abcdef"
    rows[4] = answer(fields, round_index=2)
    result, _, _ = run_fixture(tmp_path, rows=rows)
    assert result.status == "INCOMPLETE_TECHNICAL"
    assert result.receipt["technical_error_code"] == "MALFORMED_RESPONSE"
    assert result.detector_path is None


def test_two_outstanding_questions_cannot_have_their_answers_swapped(tmp_path, monkeypatch):
    pipeline = module()
    original_call = boundary.DeterministicFakeProvider.call

    async def interleave(self, prompt, *, label):
        await asyncio.sleep(0)
        return await original_call(self, prompt, label=label)

    class SwappingRecorder(QACommunicationRecorder):
        def emit_answer(self, **kwargs):
            original_question = kwargs["question"]
            kwargs["question"] = next(
                event for event in self.events
                if event["event_type"] == "QUESTION_EMITTED"
                and event["question_id"] != original_question["question_id"]
            )
            return super().emit_answer(**kwargs)

    monkeypatch.setattr(boundary.DeterministicFakeProvider, "call", interleave)
    recorder = SwappingRecorder(tmp_path / "qa_events.jsonl", run_id="synthetic-run")

    async def ask(case_id):
        return await pipeline.route_question_answer(
            asking_agent="agent2", answering_agent="agent1", case_id=case_id,
            stage=STAGES[0][1], skill=STAGES[0][2], scope="language",
            question_text="Synthetic question shared by two distinct cases.",
            provider=boundary.DeterministicFakeProvider([answer(identity(case_id=case_id))]),
            ledger=boundary.BudgetLedger(config()), recorder=recorder,
            run_id="synthetic-run", setting_id="cd_airtravel", round_index=1,
        )

    async def both():
        return await asyncio.gather(ask("01"), ask("02"), return_exceptions=True)

    results = asyncio.run(both())
    assert all(isinstance(result, pipeline.PipelineFailure) for result in results)
    assert all(result.code == "MALFORMED_RESPONSE" for result in results)
    terminals = [event for event in recorder.events if event["event_type"] == "EPISODE_TERMINATED"]
    assert len(terminals) == 2
    assert all(event["termination_reason"] == "INCOMPLETE_TECHNICAL" for event in terminals)


@pytest.mark.parametrize("metadata_field", ["source_tier", "guideline_id", "pattern_id"])
@pytest.mark.parametrize("private_value", [
    "SENSITIVE_SENTINEL_SYNTHETIC_PRIVATE_CONTENT",
    "Synthetic raw answer text must never be an identifier.",
    "Synthetic/Private/Source.txt", "x" * 200,
])
def test_model_metadata_cannot_persist_raw_or_sensitive_content(tmp_path, metadata_field, private_value):
    rows = outcomes(qa_cases=("01",))
    if metadata_field == "source_tier":
        rows[2]["output"][metadata_field] = private_value
    else:
        rows[1]["output"]["questions"][0][metadata_field] = private_value
        fields = identity()
        fields[metadata_field] = private_value
        rows[2] = answer(fields)
    result, _, _ = run_fixture(tmp_path, rows=rows)
    assert result.status == "INCOMPLETE_TECHNICAL"
    assert result.receipt["technical_error_code"] == "MALFORMED_RESPONSE"
    for path in tmp_path.iterdir():
        assert private_value not in path.read_text(encoding="utf-8")
    assert result.detector_path is None


@pytest.mark.parametrize("mutation", [
    {"round_index": 2},
    {"termination_reason": "TERMINATED_MAX_ROUNDS", "converged": False},
    {"question_id": "wrong-question"}, {"source_agent": "agent4"},
    {"target_agent": "agent2"}, {"case_id": "04"},
    {"source_stage": "wrong-stage"}, {"source_skill": "wrong-skill"},
])
def test_terminal_substitution_cannot_create_false_detector_signals(tmp_path, mutation):
    class ChangedTerminalRecorder(QACommunicationRecorder):
        def emit_termination(self, **kwargs):
            return super().emit_termination(**{**kwargs, **mutation})

    result, _, _ = run_fixture(tmp_path, rows=outcomes(qa_cases=("01",)),
                               recorder_type=ChangedTerminalRecorder)
    assert result.status == "INCOMPLETE_TECHNICAL"
    assert result.receipt["technical_error_code"] == "MALFORMED_RESPONSE"
    assert result.detector_path is None
    assert not (tmp_path / "detector_v1.json").exists()


def test_terminal_return_must_be_the_exact_persisted_event(tmp_path):
    class DetachedTerminalRecorder(QACommunicationRecorder):
        def emit_termination(self, **kwargs):
            return dict(super().emit_termination(**kwargs))

    result, _, _ = run_fixture(tmp_path, rows=outcomes(qa_cases=("01",)),
                               recorder_type=DetachedTerminalRecorder)
    assert result.status == "INCOMPLETE_TECHNICAL"
    assert result.receipt["technical_error_code"] == "MALFORMED_RESPONSE"
    assert result.detector_path is None


def test_opaque_metadata_identifiers_and_allowlisted_source_category_are_preserved(tmp_path):
    rows = outcomes(qa_cases=("01",))
    opaque = {"guideline_id": "g-0123456789abcdef", "pattern_id": "p-fedcba9876543210"}
    rows[1]["output"]["questions"][0].update(opaque)
    rows[2] = answer({**identity(), **opaque}, source_tier="domain_description")
    result, recorder, _ = run_fixture(tmp_path, rows=rows)
    assert result.status == "PASS"
    assert all(event["guideline_id"] == opaque["guideline_id"] for event in recorder.events)
    assert all(event["pattern_id"] == opaque["pattern_id"] for event in recorder.events)
    assert recorder.events[1]["answer_source_tier"] == "domain_description"


@pytest.mark.parametrize("metadata_field", ["guideline_id", "pattern_id"])
def test_direct_route_rejects_raw_identifier_before_recording(tmp_path, metadata_field):
    private_value = "SENSITIVE_SENTINEL_SYNTHETIC_PRIVATE_CONTENT"
    fields = {**identity(), metadata_field: private_value}
    recorder = QACommunicationRecorder(tmp_path / "qa_events.jsonl", run_id="synthetic-run")
    provider = boundary.DeterministicFakeProvider([answer(fields)])
    with pytest.raises(module().PipelineFailure, match="MALFORMED_RESPONSE"):
        asyncio.run(module().route_question_answer(
            asking_agent="agent2", answering_agent="agent1", case_id="01", stage=STAGES[0][1],
            skill=STAGES[0][2], scope="language", question_text="Synthetic actual question.",
            provider=provider, ledger=boundary.BudgetLedger(config()), recorder=recorder,
            run_id="synthetic-run", setting_id="cd_airtravel", round_index=1,
            **{metadata_field: private_value},
        ))
    assert recorder.events == []
    assert provider.physical_call_count == 0
    assert not recorder.path.exists()
