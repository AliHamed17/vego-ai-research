"""Study 2: compare the VEGO_AI_ON and VEGO_AI_OFF systems offline.

This is a system comparison, not a single-factor orchestration ablation. The
conditions necessarily differ in prompt text, task decomposition, call
structure and control flow; the prompt-difference receipt records those
structural differences rather than claiming they are incidental.

Detector-v1 is applicable only to the ON condition and is not executed by this
fixture harness. The OFF baseline emits no inter-agent episodes, so its detector
denominator is NOT_APPLICABLE and the two conditions are never compared on alert
counts. Schema/volume diagnostics are reported as explicitly not comparable as
quality; operational costs and timings are descriptive only.

Study 1 results are never pooled with anything produced here.

The historical protected-runtime helpers are retained only as fail-closed
compatibility names. The command-line interface accepts only the controlled
dependency-injected runner selected with ``--allowed-root``.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "VEGO-AI/framework"))
sys.path.insert(0, str(ROOT / "src"))

SETTING_ID = "cd_airtravel"
CORPUS_ID = "text2uml_airtravel_253b26dc"
FIXTURE_IDENTITY = "LOCAL_DETERMINISTIC_FAKE_V4"
COMPARISON_SCHEMA = json.loads(
    (ROOT / "schemas/study2-on-off-comparison-v1.schema.json").read_text(encoding="utf-8")
)


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
    """Validate and summarise ON artifacts without coercing malformed values.

    The protected pipeline stores the two shared output parts separately.  A
    missing list is a schema failure, not an empty scientific result.
    """
    def load(name: str) -> Any:
        path = output / name
        if not path.is_file():
            raise ValueError(f"ON output schema failure: {name} is missing")
        value = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(value, dict):
            raise ValueError(f"ON output schema failure: {name} must be an object")
        return value

    compliance = load("compliance_vectors.json")
    uncovered = load("uncovered_fragments.json")
    per_case = {}
    case_ids = sorted(set(compliance) | set(uncovered))
    if not case_ids:
        raise ValueError("ON output schema failure: no case records")
    for case_id in case_ids:
        vector = compliance.get(case_id)
        fragments = uncovered.get(case_id)
        if not isinstance(vector, dict) or not isinstance(fragments, dict):
            raise ValueError(f"ON output schema failure: case {case_id} is not an object pair")
        mapping = vector.get("existing_mapping")
        summary = vector.get("coverage_summary")
        frags = fragments.get("uncovered_fragments")
        if not isinstance(mapping, list) or not isinstance(frags, list):
            raise ValueError(f"ON output schema failure: case {case_id} requires mapping and fragment arrays")
        if not isinstance(summary, dict) or set(summary) != {"satisfied", "partially_satisfied", "not_satisfied"}:
            raise ValueError(f"ON output schema failure: case {case_id} has invalid coverage summary")
        if any(type(summary[key]) is not int or summary[key] < 0 for key in summary):
            raise ValueError(f"ON output schema failure: case {case_id} has invalid summary counts")
        for row in mapping:
            if not isinstance(row, dict) or set(row) - {"guideline_id", "evidence", "compliance_status", "notes"} or not {"guideline_id", "evidence", "compliance_status", "notes"} <= set(row):
                raise ValueError(f"ON output schema failure: case {case_id} has invalid mapping row")
            if row["compliance_status"] not in {"Satisfied", "Partially-Satisfied", "Not-Satisfied"}:
                raise ValueError(f"ON output schema failure: case {case_id} has invalid compliance status")
        for row in frags:
            if not isinstance(row, dict) or set(row) - {"fragment", "label", "severity", "reason"} or not {"fragment", "label", "severity", "reason"} <= set(row):
                raise ValueError(f"ON output schema failure: case {case_id} has invalid uncovered fragment")
            if row["label"] not in {"Alternative", "Domain Mistake", "Language Mistake"} or row["severity"] not in {"High", "Medium", "Low", "N/A"}:
                raise ValueError(f"ON output schema failure: case {case_id} has invalid fragment label/severity")
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
    """Deprecated protected-runtime fixture path; fail closed if called."""
    raise RuntimeError("legacy protected-runtime path is disabled; use the controlled fixture runner")


async def _legacy_run_on(corpus: dict[str, Any], output: Path, mode: str, run_id: str) -> dict[str, Any]:
    raise RuntimeError("legacy protected-runtime path is disabled; use the controlled fixture runner")


async def run_off(corpus: dict[str, Any], mode: str) -> dict[str, Any]:
    """Deprecated unbound baseline path; fail closed if called."""
    raise RuntimeError("legacy unbound baseline path is disabled; use the controlled fixture runner")


async def _legacy_run_off(corpus: dict[str, Any], mode: str) -> dict[str, Any]:
    raise RuntimeError("legacy unbound baseline path is disabled; use the controlled fixture runner")


def prompt_difference_receipt(on: dict[str, Any], off: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": "study2-prompt-difference-receipt-v1",
        "varying_factor": "VEGO-AI system workflow (agent decomposition, prompts, Q&A, and call structure)",
        "held_identical": [
            "corpus_id and case identifiers",
            "model identity and token policy",
            "retry policy, timeout, concurrency",
            "required output fields (mapping rows, uncovered fragments)",
            "private output root and privacy controls",
        ],
        "on_prompt_count": len(on["prompt_sha_by_call"]),
        "off_prompt_count": len(off["prompt_sha_by_call"]),
        "on_prompt_sha_by_call": on["prompt_sha_by_call"],
        "off_prompt_sha_by_call": off["prompt_sha_by_call"],
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


def _run_dependency_injected_fixture(
    *, output_dir: Path, allowed_root: Path, fixture_mode: str, run_id: str
) -> dict[str, Any]:
    """Run the package-level paired fixture with a local deterministic client.

    The explicit ``--allowed-root`` path selects this branch.  It never loads a
    provider adapter or the protected production orchestrator; the package
    runner receives only :class:`DeterministicFixtureClient`.
    """
    from vego_study2.config import load_config
    from vego_study2.fixtures import DeterministicFixtureClient, fixture_cases
    from vego_study2.runner import Study2Runner

    config = load_config(ROOT / "docs/research/phd-proposal/study2-frozen-config.json")
    config = {**config, "run_id": run_id}
    runner = Study2Runner(
        config=config,
        cases=fixture_cases(config),
        client=DeterministicFixtureClient(),
        output_root=output_dir,
        approved_root=allowed_root,
        code_sha="ENGINEERING_FIXTURE_ONLY",
    )
    result = asyncio.run(runner.run_both(fixture_mode=fixture_mode))
    return {
        "schema_version": result["schema_version"],
        "evidence_class": result["evidence_class"],
        "scientific_result_status": result["receipt"]["scientific_result_status"],
        "provider_calls": result["receipt"]["provider_calls"],
        "external_calls": result["receipt"]["external_calls"],
        "run_id": result["receipt"]["run_id"],
        "normalized_sha256": result["normalized_sha256"],
        "condition_status": {
            name: report["status"]
            for name, report in result["conditions"].items()
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--runtime-root", type=Path, default=ROOT / "external_data/airtravel-pr38/runtime_input")
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--fixture-mode", default="two_rounds", choices=["no_questions", "two_rounds", "max_rounds"])
    parser.add_argument("--run-id", default="STUDY2-FIXTURE")
    parser.add_argument(
        "--allowed-root",
        type=Path,
        help="Absolute private root; selects the dependency-injected, no-provider fixture runner",
    )
    args = parser.parse_args()

    if args.allowed_root is not None:
        summary = _run_dependency_injected_fixture(
            output_dir=args.output_dir,
            allowed_root=args.allowed_root,
            fixture_mode=args.fixture_mode,
            run_id=args.run_id,
        )
        print(json.dumps(summary, indent=2, sort_keys=True))
        return 0

    parser.error(
        "Study 2 is fixture-only in this revision; --allowed-root is required "
        "to select the controlled dependency-injected runner"
    )


if __name__ == "__main__":
    raise SystemExit(main())
