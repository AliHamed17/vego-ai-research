"""Study 2: run VEGO_AI_ON and VEGO_AI_OFF over the same corpus and compare.

The single varying factor is VEGO-AI orchestration. Corpus, case identifiers,
model, token policy, retries, timeout, concurrency and output schema are held
identical, and a prompt-difference receipt records what actually differed.

Detector-v1 is applied only to the ON condition. The OFF baseline emits no
inter-agent episodes, so its detector denominator is NOT_APPLICABLE and the two
conditions are never compared on alert counts. They are compared on the shared
per-case output objective, on cost and on time.

Study 1 results are never pooled with anything produced here.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
import time
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "VEGO-AI/framework"))

SETTING_ID = "cd_airtravel"
CORPUS_ID = "text2uml_airtravel_253b26dc"
FIXTURE_IDENTITY = "LOCAL_DETERMINISTIC_FAKE_V4"


def load_corpus(runtime_root: Path) -> dict[str, Any]:
    from airtravel_v4_contract import RUNTIME_FILES, digest

    for relative, expected in RUNTIME_FILES.items():
        target = runtime_root / relative
        if not target.is_file() or digest(target) != expected["sha256"]:
            raise ValueError(f"runtime file mismatch: {relative}")
    return {
        "domain_description": (runtime_root / "domain_description/description.md").read_text(
            encoding="utf-8"
        ),
        "cases": [
            {
                "case_id": rel.split("/", 1)[1].split("_", 1)[0],
                "case_model": (runtime_root / rel).read_text(encoding="utf-8"),
            }
            for rel in sorted(RUNTIME_FILES)
            if rel.startswith("candidate_models/")
        ],
    }


def summarise_on(output: Path) -> dict[str, Any]:
    """Per-case artifact counts produced by the orchestrated pipeline."""
    def load(name: str) -> Any:
        path = output / name
        return json.loads(path.read_text(encoding="utf-8")) if path.is_file() else {}

    compliance = load("compliance_vectors.json")
    uncovered = load("uncovered_fragments.json")
    per_case = {}
    for case_id in sorted(set(compliance) | set(uncovered)):
        vector = compliance.get(case_id) or {}
        fragments = uncovered.get(case_id) or {}
        mapping = vector.get("existing_mapping") if isinstance(vector, dict) else None
        frags = fragments.get("uncovered_fragments") if isinstance(fragments, dict) else None
        per_case[case_id] = {
            "mapping_rows": len(mapping) if isinstance(mapping, list) else 0,
            "uncovered_fragments": len(frags) if isinstance(frags, list) else 0,
            "schema_complete": isinstance(mapping, list) and isinstance(frags, list),
        }
    return per_case


def summarise_off(result: dict[str, Any]) -> dict[str, Any]:
    return {
        case_id: {
            "mapping_rows": len(row["existing_mapping"]),
            "uncovered_fragments": len(row["uncovered_fragments"]),
            "schema_complete": row["schema_complete"],
        }
        for case_id, row in result["cases"].items()
    }


async def run_on(corpus: dict[str, Any], output: Path, mode: str, run_id: str) -> dict[str, Any]:
    import airtravel_v4_execution as ex
    from airtravel_local_observer import Observer, Proxy, RecordingFake
    from qa_communication import QACommunicationRecorder
    from qa_registry import QARegistry

    module = ex._load_protected_runtime()
    output.mkdir(parents=True, exist_ok=True)
    recorder = QACommunicationRecorder(output / "qa_events.jsonl", run_id=run_id)
    observer = Observer(recorder)
    fake = RecordingFake(mode)
    proxy = Proxy(fake, observer, len(corpus["cases"]), SETTING_ID, run_id)
    cfg = {
        "setting_id": SETTING_ID,
        "corpus_id": CORPUS_ID,
        "language_name": "UML",
        "domain_description": corpus["domain_description"],
        "case_models": corpus["cases"],
        "max_concurrent_cases": 2,
        "model": FIXTURE_IDENTITY,
        "output_dir": str(output),
    }
    original_client, original_registry = module.LLMClient, module.QARegistry
    module.LLMClient = lambda **_: proxy
    module.QARegistry = observer.registry(QARegistry)
    started = time.monotonic()
    try:
        await module.run_setting(cfg, output / "inline.json", None, SETTING_ID)
    finally:
        module.LLMClient, module.QARegistry = original_client, original_registry
        recorder.close_open_episodes()
    events = recorder.events
    prompts = {row["label"]: row["prompt_sha256"] for row in fake.calls}
    return {
        "condition": "VEGO_AI_ON",
        "elapsed_seconds": round(time.monotonic() - started, 3),
        "calls": len(fake.calls),
        "agent_decomposition": True,
        "inter_agent_qa": True,
        "episodes": len({e["episode_id"] for e in events}),
        "questions": sum(e["event_type"] == "QUESTION_EMITTED" for e in events),
        "answers": sum(e["event_type"] == "ANSWER_RECEIVED" for e in events),
        "termination_states": dict(
            Counter(
                e["termination_reason"] for e in events if e["event_type"] == "EPISODE_TERMINATED"
            )
        ),
        "per_case": summarise_on(output),
        "prompt_sha_by_label": prompts,
    }


async def run_off(corpus: dict[str, Any], mode: str) -> dict[str, Any]:
    from airtravel_local_observer import RecordingFake
    from study2_vego_off_baseline import run_off_baseline

    class BaselineFake(RecordingFake):
        """Fixture client for the baseline: no protected call-inventory contract."""

        def __init__(self, mode: str):
            self.mode = mode
            self.calls = []

        async def call(self, prompt, *, label):
            self.calls.append({"label": label})
            await asyncio.sleep(0)
            return {
                "skill_version": "off-baseline-v1",
                "case_id": label.split("/")[1],
                "existing_mapping": [],
                "coverage_summary": {"satisfied": 0, "partially_satisfied": 0, "not_satisfied": 0},
                "uncovered_fragments": [],
            }

    client = BaselineFake(mode)
    started = time.monotonic()
    result = await run_off_baseline(
        client, corpus["cases"], corpus["domain_description"], "UML", max_concurrent=2
    )
    result["elapsed_seconds"] = round(time.monotonic() - started, 3)
    result["per_case"] = summarise_off(result)
    return result


def prompt_difference_receipt(on: dict[str, Any], off: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": "study2-prompt-difference-receipt-v1",
        "varying_factor": "VEGO-AI orchestration (agent decomposition and inter-agent Q&A)",
        "held_identical": [
            "corpus_id and case identifiers",
            "model identity and token policy",
            "retry policy, timeout, concurrency",
            "required output fields (mapping rows, uncovered fragments)",
            "private output root and privacy controls",
        ],
        "on_prompt_count": len(on["prompt_sha_by_label"]),
        "off_prompt_count": len(off["prompt_sha_by_case"]),
        "on_prompt_sha_by_label": on["prompt_sha_by_label"],
        "off_prompt_sha_by_case": off["prompt_sha_by_case"],
        "structural_differences": {
            "agent_decomposition": {"on": True, "off": False},
            "inter_agent_qa": {"on": True, "off": False},
            "round_loop": {"on": True, "off": False},
        },
        "note": (
            "Prompt text necessarily differs because the conditions differ structurally: "
            "ON issues role-scoped skill prompts across agents, OFF issues one direct "
            "per-case prompt. Hashes are recorded so the difference is auditable rather "
            "than asserted. Raw prompt text is not persisted."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--runtime-root", type=Path, default=ROOT / "external_data/airtravel-pr38/runtime_input")
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--fixture-mode", default="two_rounds", choices=["no_questions", "two_rounds", "max_rounds"])
    parser.add_argument("--run-id", default="STUDY2-FIXTURE")
    args = parser.parse_args()

    corpus = load_corpus(args.runtime_root)
    on = asyncio.run(run_on(corpus, args.output_dir / "on", args.fixture_mode, args.run_id))
    off = asyncio.run(run_off(corpus, args.fixture_mode))

    cases = sorted(set(on["per_case"]) | set(off["per_case"]))
    comparison = []
    for case_id in cases:
        a, b = on["per_case"].get(case_id, {}), off["per_case"].get(case_id, {})
        comparison.append(
            {
                "case_id": case_id,
                "on_mapping_rows": a.get("mapping_rows"),
                "off_mapping_rows": b.get("mapping_rows"),
                "on_uncovered_fragments": a.get("uncovered_fragments"),
                "off_uncovered_fragments": b.get("uncovered_fragments"),
                "on_schema_complete": a.get("schema_complete"),
                "off_schema_complete": b.get("schema_complete"),
            }
        )

    payload = {
        "schema_version": "study2-on-off-comparison-v1",
        "evidence_class": "ENGINEERING_FIXTURE_NOT_SCIENTIFIC",
        "provider_calls": 0,
        "fixture_mode": args.fixture_mode,
        "setting_id": SETTING_ID,
        "corpus_id": CORPUS_ID,
        "cases": len(corpus["cases"]),
        "conditions": {
            "VEGO_AI_ON": {k: v for k, v in on.items() if k != "prompt_sha_by_label"},
            "VEGO_AI_OFF": {
                k: v for k, v in off.items() if k not in {"cases", "prompt_sha_by_case"}
            },
        },
        "per_case_comparison": comparison,
        "detector_v1": {
            "applied_to": "VEGO_AI_ON only",
            "off_denominator": "NOT_APPLICABLE",
            "reason": (
                "The baseline produces no inter-agent episodes. Absence of a measuring "
                "unit is not a zero-alert observation, so the conditions are never "
                "compared on alert counts."
            ),
        },
        "prompt_difference_receipt": prompt_difference_receipt(on, off),
        "pooling": "Study 1 results are not pooled with this comparison.",
        "forbidden_metrics_computed": [],
    }
    target = args.output_dir / "on-off-comparison.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes((json.dumps(payload, indent=2, sort_keys=True) + "\n").encode("utf-8"))
    print(json.dumps({k: payload[k] for k in ("conditions", "per_case_comparison", "detector_v1")}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
