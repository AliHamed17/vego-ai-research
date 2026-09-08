"""Exercise the Detector-v1 lifecycle envelope on deterministic fixtures.

Engineering evidence only. Fixture answers are synthetic, so nothing here is a
scientific result and none of it enters a scientific denominator. The purpose
is to observe how the frozen detector behaves under lifecycle states the single
real run did not produce: a run with no Q&A at all, and a run where every
episode reaches the round limit. No provider is contacted.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "VEGO-AI/framework"))

MODES = ("no_questions", "two_rounds", "max_rounds")


def run_mode(mode: str) -> dict:
    import airtravel_v4_execution as ex
    from airtravel_detector_analysis import project_episodes
    from airtravel_v4_contract import RUNTIME_FILES
    from extract_qa_escalation_features import detect_detector_v1

    runtime_root = ROOT / "external_data/airtravel-pr38/runtime_input"
    domain = (runtime_root / "domain_description/description.md").read_text(encoding="utf-8")
    cases = [
        {
            "case_id": rel.split("/", 1)[1].split("_", 1)[0],
            "case_model": (runtime_root / rel).read_text(encoding="utf-8"),
        }
        for rel in sorted(RUNTIME_FILES)
        if rel.startswith("candidate_models/")
    ]
    cfg = {
        "setting_id": "cd_airtravel",
        "corpus_id": "text2uml_airtravel_253b26dc",
        "language_name": "UML",
        "domain_description": domain,
        "case_models": cases,
        "max_concurrent_cases": 2,
        "model": "LOCAL_DETERMINISTIC_FAKE_V4",
        "api_key": None,
        "provider_execution_enabled": False,
    }
    module = ex._load_protected_runtime()
    out = Path(tempfile.mkdtemp()) / "output"
    out.mkdir(parents=True)

    async def drive():
        from airtravel_local_observer import Observer, Proxy, RecordingFake
        from qa_communication import QACommunicationRecorder
        from qa_registry import QARegistry

        run_id = f"ENVELOPE-{mode}"
        recorder = QACommunicationRecorder(out / "qa_events.jsonl", run_id=run_id)
        observer = Observer(recorder)
        fake = RecordingFake(mode)
        proxy = Proxy(fake, observer, 4, cfg["setting_id"], run_id)
        original_client, original_registry = module.LLMClient, module.QARegistry
        module.LLMClient = lambda **_: proxy
        module.QARegistry = observer.registry(QARegistry)
        try:
            await module.run_setting(
                {**cfg, "output_dir": str(out)}, out / "inline.json", None, cfg["setting_id"]
            )
        finally:
            module.LLMClient, module.QARegistry = original_client, original_registry
            recorder.close_open_episodes()
        return {"direct_fake_call_count": len(fake.calls)}

    result = asyncio.run(drive())
    log = out / "qa_events.jsonl"
    events = (
        [json.loads(line) for line in log.read_text(encoding="utf-8").splitlines() if line.strip()]
        if log.is_file()
        else []
    )
    episodes = project_episodes(events)
    verdicts = [detect_detector_v1(e) for e in episodes]
    scored = [v for v in verdicts if v["classification"] != "EXCLUDED"]
    complete = [e for e in episodes if e["scientific_complete"]]
    counts = {"STRONG_ALERT": 0, "WEAK_ALERT": 0, "NO_ALERT": 0}
    for v in scored:
        counts[v["classification"]] = counts.get(v["classification"], 0) + 1
    zero_qa = len(events) == 0
    return {
        "fixture_mode": mode,
        "evidence_class": "ENGINEERING_FIXTURE_NOT_SCIENTIFIC",
        "calls_per_pass": result["direct_fake_call_count"],
        "events": len(events),
        "episodes_observed": len(episodes),
        "complete_episodes": len(complete),
        "incomplete_technical": len(episodes) - len(complete),
        "questions": sum(e["event_type"] == "QUESTION_EMITTED" for e in events),
        "answers": sum(e["event_type"] == "ANSWER_RECEIVED" for e in events),
        "max_round_index": max((e["round_count"] for e in episodes), default=0),
        "termination_states": {
            r: sum(1 for e in episodes if e["termination_reason"] == r)
            for r in sorted({e["termination_reason"] for e in episodes if e["termination_reason"]})
        },
        "detector_v1": counts,
        "detector_denominator": len(scored),
        "run_level_status": "VALID_ZERO_QA_RUN" if zero_qa else "QA_OBSERVED",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    results = [run_mode(mode) for mode in MODES]
    payload = {
        "schema_version": "airtravel-detector-envelope-v1",
        "evidence_class": "ENGINEERING_FIXTURE_NOT_SCIENTIFIC",
        "provider_calls": 0,
        "note": (
            "Deterministic fixtures. Not a scientific result and excluded from every "
            "scientific denominator. Shows how the frozen Detector-v1 responds to "
            "lifecycle states the single real run did not produce."
        ),
        "modes": results,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes((json.dumps(payload, indent=2, sort_keys=True) + "\n").encode("utf-8"))
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
