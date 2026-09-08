"""Offline preflight: measure how the pipeline's call count scales with the case-frame size.

The paid full-frame run must declare a call cap before it starts, and a cap guessed from a single
four-case observation is not a bound. This module runs the protected orchestrator against the
deterministic local fake at several frame sizes and fits the structural cost as ``a + b*N``, so
the declared cap rests on measured control flow rather than on an extrapolated cost.

Two things this preflight cannot do, stated plainly so its output is not over-read:

  * the fake converges in one round, so it measures the *structural* call count, not the
    conversational depth a live provider produces. It is a floor on shape, not a forecast of cost;
  * it produces no scientific observation whatsoever. Its answers are synthetic.

No provider is contacted. The run asserts that no provider SDK was imported into the process,
and refuses to report success if one was.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
import tempfile
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "VEGO-AI/framework"))

SCRATCH_ROOT = ROOT / "external_data/airtravel-pr38/scratch"
DEFAULT_SIZES = (4, 8, 14, 21)


def frame_cases(runtime_root: Path, size: int) -> list[dict[str, str]]:
    contract = json.loads((runtime_root / "full-frame-contract.json").read_text(encoding="utf-8"))
    relatives = sorted(
        rel for rel in contract["runtime_files"] if rel.startswith("candidate_models/")
    )
    if size > len(relatives):
        raise ValueError(f"frame holds {len(relatives)} cases, {size} requested")
    return [
        {
            "case_id": rel.split("/", 1)[1].split("_", 1)[0],
            "case_model": (runtime_root / rel).read_text(encoding="utf-8"),
        }
        for rel in relatives[:size]
    ]


def measure(runtime_root: Path, size: int) -> dict[str, Any]:
    import airtravel_v4_execution as ex

    domain = (runtime_root / "domain_description/description.md").read_text(encoding="utf-8")
    cases = frame_cases(runtime_root, size)
    cfg = {
        "setting_id": "cd_airtravel",
        "corpus_id": "text2uml_airtravel_253b26dc",
        "language_name": "UML",
        "domain_description": domain,
        "case_models": cases,
        "max_concurrent_cases": 2,
        "model": "LOCAL_DETERMINISTIC_FAKE_FULL_FRAME",
        "api_key": None,
        "provider_execution_enabled": False,
    }
    module = ex._load_protected_runtime()

    async def drive(out: Path) -> tuple[int, list[dict[str, Any]]]:
        from airtravel_local_observer import Observer, Proxy, RecordingFake
        from qa_communication import QACommunicationRecorder
        from qa_registry import QARegistry

        run_id = f"FULLFRAME-PREFLIGHT-N{size:02d}"
        recorder = QACommunicationRecorder(out / "qa_events.jsonl", run_id=run_id)
        observer = Observer(recorder)
        fake = RecordingFake("two_rounds")
        proxy = Proxy(fake, observer, size, cfg["setting_id"], run_id)
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
        return len(fake.calls), recorder.events

    SCRATCH_ROOT.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=SCRATCH_ROOT, prefix=f"fullframe-pre-N{size}-") as tmp:
        out = Path(tmp) / "output"
        out.mkdir()
        calls, events = asyncio.run(drive(out))

    leaked = sorted(
        module_name
        for module_name in ex.OFFLINE_PROVIDER_IMPORTS - {"urllib", "google"}
        if module_name in sys.modules
    )
    if leaked:
        raise RuntimeError(f"provider SDK module loaded during offline preflight: {leaked}")

    questions = [event for event in events if event["event_type"] == "QUESTION_EMITTED"]
    return {
        "case_count": size,
        "fake_calls": calls,
        "episodes": len({event["episode_id"] for event in events}),
        "questions": len(questions),
        "answers": sum(1 for event in events if event["event_type"] == "ANSWER_RECEIVED"),
        "terminations": dict(
            Counter(
                event.get("termination_reason")
                for event in events
                if event["event_type"] == "EPISODE_TERMINATED"
            )
        ),
        "provider_absence_basis": "no provider SDK module present in sys.modules after the run",
    }


def fit_linear(points: list[tuple[int, int]]) -> dict[str, float]:
    """Least-squares fit of calls = a + b*N over the measured frame sizes."""
    n = len(points)
    mean_x = sum(x for x, _ in points) / n
    mean_y = sum(y for _, y in points) / n
    denominator = sum((x - mean_x) ** 2 for x, _ in points)
    slope = (
        sum((x - mean_x) * (y - mean_y) for x, y in points) / denominator if denominator else 0.0
    )
    return {"intercept": round(mean_y - slope * mean_x, 4), "slope_per_case": round(slope, 4)}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--runtime-root",
        type=Path,
        default=ROOT / "external_data/airtravel-pr38/fullframe_runtime",
    )
    parser.add_argument("--sizes", type=int, nargs="+", default=list(DEFAULT_SIZES))
    parser.add_argument("--out", type=Path, default=None)
    args = parser.parse_args()

    measurements = [measure(args.runtime_root, size) for size in args.sizes]
    fit = fit_linear([(row["case_count"], row["fake_calls"]) for row in measurements])
    report = {
        "schema_version": "airtravel-full-frame-preflight-v1",
        "evidence_class": "ENGINEERING_FIXTURE_NOT_SCIENTIFIC",
        "purpose": "measure structural call-count scaling to justify a declared call cap",
        "measurements": measurements,
        "structural_fit": fit,
        "limitation": (
            "the local fake converges in one round, so these counts bound pipeline structure "
            "only and are not a forecast of live conversational depth or cost"
        ),
        "provider_calls": 0,
    }
    text = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(text, encoding="utf-8")
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
