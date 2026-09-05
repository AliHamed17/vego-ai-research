"""Future two-pass protected fake execution; CLI grant verification precedes import."""

from __future__ import annotations

import asyncio
import json
import logging
from pathlib import Path

import airtravel_preflight_contract as contract
from airtravel_execution_safety import ExecutionGuard, timed_operation

SCIENTIFIC_FILES = {
    "pipeline_state.json",
    "language_template.json",
    "reference_guidelines.json",
    "compliance_vectors.json",
    "uncovered_fragments.json",
    "deviation_patterns.json",
    "variability_classifications.json",
    "lang_qa_history.json",
    "dom_qa_history.json",
    "human_review_queue.jsonl",
}
PASS_FILES = SCIENTIFIC_FILES | {"pipeline.log"}
ALLOWED_FILES = {f"{side}/{name}" for side in ("baseline", "instrumented") for name in PASS_FILES}
ALLOWED_FILES |= {"instrumented/qa_events.jsonl", "preflight-receipt.json"}


def scientific_outputs(root):
    if {p.name for p in root.iterdir() if p.is_file()} - (PASS_FILES | {"qa_events.jsonl"}):
        raise ValueError("unexpected protected output")
    if not all((root / name).is_file() for name in SCIENTIFIC_FILES):
        raise ValueError("expected protected output missing")
    return {name: contract.digest(root / name) for name in sorted(SCIENTIFIC_FILES)}


async def run_pair(cfg, output, module, *, mode="two_rounds", fixture_only=False, progress=None):
    """Private control-flow routine; unit tests use inline non-AirTravel two-case fixtures."""
    from airtravel_local_observer import (
        Observer,
        Proxy,
        RecordingFake,
        route_metrics,
        validate_final_stream,
    )
    from qa_communication import QACommunicationRecorder
    from qa_registry import QARegistry

    recorder = None
    results = []
    progress = progress if progress is not None else {}
    count = len(cfg.get("case_models", [])) if fixture_only else 4
    try:
        for side in ("baseline", "instrumented"):
            observed = side == "instrumented"
            subdir = output / side
            subdir.mkdir()
            current = {**cfg, "output_dir": str(subdir)}
            recorder = (
                QACommunicationRecorder(subdir / "qa_events.jsonl", run_id="airtravel-fake-v3")
                if observed
                else None
            )
            observer = Observer(recorder)
            fake = RecordingFake(mode)
            progress[side] = fake.calls
            client = (
                Proxy(fake, observer, count, cfg["setting_id"], "airtravel-fake-v3")
                if observed
                else fake
            )
            module.LLMClient = lambda _client=client, **_: _client
            module.QARegistry = observer.registry(QARegistry) if observed else QARegistry
            await module.run_setting(
                current, output / "inline-config-not-written.json", None, cfg["setting_id"]
            )
            state = json.loads((subdir / "pipeline_state.json").read_text(encoding="utf-8"))
            outputs = scientific_outputs(subdir)
            events = recorder.events if observed else []
            if observed:
                validate_final_stream(events)
                if not (subdir / "qa_events.jsonl").exists():
                    (subdir / "qa_events.jsonl").touch(exist_ok=False)
            results.append(
                {"calls": fake.calls, "state": state, "outputs": outputs, "events": events}
            )
        a, b = results
        parity = {
            "prompt_parity": [(r["label"], r["prompt_sha256"]) for r in a["calls"]]
            == [(r["label"], r["prompt_sha256"]) for r in b["calls"]],
            "answer_parity": [r["answer_sha256"] for r in a["calls"]]
            == [r["answer_sha256"] for r in b["calls"]],
            "state_parity": a["state"] == b["state"],
            "output_parity": a["outputs"] == b["outputs"],
        }
        if not all(parity.values()):
            raise ValueError("baseline/instrumented parity difference")
        state = b["state"]
        expected = (
            {c["case_id"] for c in cfg["case_models"]} if fixture_only else {"01", "02", "03", "04"}
        )
        if (
            set(state["compliance_vectors"]) != expected
            or set(state["uncovered_fragments"]) != expected
            or set(state["completed_phases"]) != {"phase1", "phase2", "phase3", "phase4"}
        ):
            raise ValueError("not all cases/phases completed")
        counts = (
            contract.check_counts(len(a["calls"]), len(b["calls"]))
            if not fixture_only
            else {
                "baseline_fake_call_count": len(a["calls"]),
                "instrumented_fake_call_count": len(b["calls"]),
                "combined_fake_call_count": len(a["calls"]) + len(b["calls"]),
            }
        )
        return {
            "status": "TECHNICAL_SUCCESS",
            **parity,
            "differences": [],
            **counts,
            **route_metrics(b["events"]),
            "orchestrator_completed": True,
            "processed_case_ids": sorted(expected),
            "expected_outputs_exist": True,
            "event_recorder_completed": True,
            "event_count": len(b["events"]),
            "technical_exception": None,
            "outputs": {
                side: results[i]["outputs"] for i, side in enumerate(("baseline", "instrumented"))
            },
        }
    except BaseException:
        if recorder:
            recorder.close_open_episodes()
        raise
    finally:
        # run_setting lacks a failure-finally around its handler; close only this run's handlers.
        for handler in list(logging.getLogger().handlers):
            filename = getattr(handler, "baseFilename", None)
            if filename and Path(filename).resolve().is_relative_to(output.resolve()):
                logging.getLogger().removeHandler(handler)
                handler.close()


def execute_verified(runtime_root, archive, output, packet, grant, root):
    # Independently revalidate even if this internal function is invoked directly.
    bindings = contract.authorize(runtime_root, archive, output, packet, grant, root)
    import prepare_airtravel_protected_fake_preflight as harness

    if harness.prepare_only(runtime_root, archive, output, root)["status"] != "PREPARED":
        raise ValueError("preparation changed before execution")
    from airtravel_local_observer import runtime

    module = runtime()
    from qa_communication import validate_event_stream

    validate_event_stream([])  # preload schema machinery before read restrictions
    protected = {p: contract.digest(root / p) for p in bindings["protected_hashes"]}
    tracked = {
        p: contract.digest(root / p)
        for p in contract.git(root, "ls-files").splitlines()
        if (root / p).is_file()
    }
    reads = {root / p for p in tracked} | {
        runtime_root / p for p in harness.FROZEN["runtime_files"]
    }
    # Schema/framework templates are tracked. No browser profiles or credential stores are readable.
    output.mkdir(parents=True, exist_ok=True)
    cfg = {
        "setting_id": contract.SETTING,
        "corpus_id": contract.CORPUS,
        "language_name": "UML",
        "domain_description_file": str(runtime_root / "domain_description/description.md"),
        "case_models_dir": str(runtime_root / "candidate_models"),
        "max_concurrent_cases": 2,
        "model": contract.MODEL,
        "api_key": None,
        "provider_execution_enabled": False,
    }
    loop = asyncio.new_event_loop()  # loop-local IPC established before denying external sockets
    guard = ExecutionGuard(
        output,
        ALLOWED_FILES,
        reads,
        max_files=contract.MAX_FILES - 1,
        max_bytes=contract.MAX_BYTES - 65536,
    )
    progress = {}
    try:

        async def operation():
            with guard:
                return await run_pair(cfg, output, module, progress=progress)

        result = loop.run_until_complete(timed_operation(operation, module))
    finally:
        pending = asyncio.all_tasks(loop)
        for task in pending:
            task.cancel()
        if pending:
            loop.run_until_complete(asyncio.gather(*pending, return_exceptions=True))
        loop.close()
    receipt = {
        "schema_version": "airtravel-technical-receipt-v1",
        **contract.counters(),
        **bindings,
        **result,
        "network_attempt_count": guard.network_attempt_count,
        "detector_v1_run_count": 0,
        "runtime_archive_sha256": contract.digest(archive),
        "api_cost": "TO BE MEASURED",
    }
    receipt.update(
        baseline_fake_call_count=len(progress.get("baseline", [])),
        instrumented_fake_call_count=len(progress.get("instrumented", [])),
        combined_fake_call_count=sum(len(v) for v in progress.values()),
    )
    if (
        guard.network_attempt_count
        or guard.violations
        or any(contract.digest(root / p) != h for p, h in tracked.items())
    ):
        receipt.update(status="TECHNICAL_FAILED", technical_exception="SafetyInvariantFailure")
    if any(contract.digest(root / p) != h for p, h in protected.items()):
        receipt.update(status="TECHNICAL_FAILED", technical_exception="ProtectedHashDrift")
    events = output / "instrumented/qa_events.jsonl"
    receipt["event_log_sha256"] = contract.digest(events) if events.exists() else None
    receipt["files"] = {
        p.relative_to(output).as_posix(): contract.digest(p)
        for p in sorted(output.rglob("*"))
        if p.is_file()
    }
    if set(receipt["files"]) - ALLOWED_FILES or len(receipt["files"]) + 1 > contract.MAX_FILES:
        receipt.update(status="TECHNICAL_FAILED", technical_exception="OutputInvariantFailure")
    data = contract.canonical(receipt)
    if (
        sum(p.stat().st_size for p in output.rglob("*") if p.is_file()) + len(data)
        > contract.MAX_BYTES
    ):
        raise ValueError("receipt would exceed output quota")
    with (output / "preflight-receipt.json").open("xb") as handle:
        handle.write(data)
    return receipt
