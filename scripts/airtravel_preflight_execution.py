"""Future two-pass protected fake execution; CLI grant verification precedes import."""

from __future__ import annotations

import asyncio
import hashlib
import json
import logging
from collections import Counter
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


def assert_pair_parity(a: dict, b: dict) -> dict:
    from study1_call_bound import validate_call_inventory

    for run in (a, b):
        validate_call_inventory(run["calls"])

    def counts(run):
        return Counter((r["phase"], r["case_id"], r["inventory_row"]) for r in run["calls"])

    parity = {
        "call_label_parity": [r["label"] for r in a["calls"]] == [r["label"] for r in b["calls"]],
        "phase_case_count_parity": counts(a) == counts(b),
        "prompt_parity": [r["prompt_sha256"] for r in a["calls"]]
        == [r["prompt_sha256"] for r in b["calls"]],
        "answer_parity": [r["answer_sha256"] for r in a["calls"]]
        == [r["answer_sha256"] for r in b["calls"]],
        "decision_parity": [r["decision_sha256"] for r in a["calls"]]
        == [r["decision_sha256"] for r in b["calls"]],
        "state_parity": a["state"] == b["state"],
        "output_parity": a["outputs"] == b["outputs"],
        "termination_parity": a["termination_result"] == b["termination_result"],
    }
    if not all(parity.values()):
        raise ValueError("baseline/instrumented parity difference")
    return parity


def scientific_outputs(root):
    if {p.name for p in root.iterdir() if p.is_file()} - (PASS_FILES | {"qa_events.jsonl"}):
        raise ValueError("unexpected protected output")
    if not all((root / name).is_file() for name in SCIENTIFIC_FILES):
        raise ValueError("expected protected output missing")
    return {name: contract.digest(root / name) for name in sorted(SCIENTIFIC_FILES)}


async def run_pair(
    cfg,
    output,
    module,
    *,
    mode="two_rounds",
    fixture_only=False,
    progress=None,
    run_id="fixture-pair",
):
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
                QACommunicationRecorder(subdir / "qa_events.jsonl", run_id=run_id)
                if observed
                else None
            )
            observer = Observer(recorder)
            fake = RecordingFake(mode)
            progress[side] = fake.calls
            client = Proxy(fake, observer, count, cfg["setting_id"], run_id) if observed else fake
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
                {
                    "calls": fake.calls,
                    "state": state,
                    "outputs": outputs,
                    "events": events,
                    "termination_result": {
                        "returned": True,
                        "completed_phases": state["completed_phases"],
                    },
                }
            )
        a, b = results
        parity = assert_pair_parity(a, b)
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
            "lifecycle_status": "PASS",
            "call_inventory_status": "PASS",
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
    inventory_before = (
        {
            p.relative_to(output).as_posix(): contract.digest(p)
            for p in output.rglob("*")
            if p.is_file()
        }
        if output.exists()
        else {}
    )
    if inventory_before:
        raise ValueError("output changed after authorization")
    run_id = (
        "FAKE-"
        + hashlib.sha256(
            contract.canonical(
                {
                    "grant": bindings["grant_sha256"],
                    "command": bindings["command_sha256"],
                    "commit": bindings["commit"],
                }
            )
        ).hexdigest()[:24]
    )
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
                return await run_pair(cfg, output, module, progress=progress, run_id=run_id)

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
        "run_id": run_id,
        "provider": "LOCAL_ONLY",
        "filesystem_inventory_before": inventory_before,
        "filesystem_containment": "PASS",
        **contract.counters(),
        **bindings,
        **result,
        "network_attempt_count": guard.network_attempt_count,
        "detector_v1_run_count": 0,
        "detector_v1_experimental_run_count": 0,
        "runtime_archive_sha256": contract.digest(archive),
        "api_cost": "TO BE MEASURED",
    }
    receipt.update(
        direct_fake_call_count=len(progress.get("baseline", [])),
        baseline_fake_call_count=len(progress.get("baseline", [])),
        instrumented_fake_call_count=len(progress.get("instrumented", [])),
        combined_fake_call_count=sum(len(v) for v in progress.values()),
    )
    if (
        guard.network_attempt_count
        or guard.violations
        or any(contract.digest(root / p) != h for p, h in tracked.items())
    ):
        receipt.update(
            status="TECHNICAL_FAILED",
            technical_exception="SafetyInvariantFailure",
            filesystem_containment="FAIL",
        )
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
        receipt.update(
            status="TECHNICAL_FAILED",
            technical_exception="OutputInvariantFailure",
            filesystem_containment="FAIL",
        )
    receipt["filesystem_inventory_after"] = receipt["files"]
    data = contract.canonical(receipt)
    if (
        sum(p.stat().st_size for p in output.rglob("*") if p.is_file()) + len(data)
        > contract.MAX_BYTES
    ):
        raise ValueError("receipt would exceed output quota")
    with (output / "preflight-receipt.json").open("xb") as handle:
        handle.write(data)
    return receipt
