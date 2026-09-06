"""The validator decides EVIDENCE_INVALID, so it must itself be shown to fail when it should.

Every fixture here is synthetic and built in a temporary directory. Nothing in this file
reads the private run evidence, which is git-ignored and absent in CI.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
VALIDATOR = ROOT / "scripts" / "study1_validate_evidence.py"

EPISODE = "EP-synthetic0000000000001"
SIGNALS = {"S1_LOW_ANSWER_CONFIDENCE": 1}


def _events() -> list[dict]:
    """One episode, one question, one low-confidence answer with non-empty evidence."""
    return [
        {
            "event_type": "QUESTION_EMITTED",
            "episode_id": EPISODE,
            "question_id": "Q1",
            "round_index": 1,
            "source_agent": "agent3",
            "target_agent": "agent2",
            "case_id": "01",
        },
        {
            "event_type": "ANSWER_RECEIVED",
            "episode_id": EPISODE,
            "question_id": "Q1",
            "answer_confidence": "Low",
            "answer_evidence_ref": {"length": 40},
        },
        {
            "event_type": "EPISODE_TERMINATED",
            "episode_id": EPISODE,
            "termination_reason": "CONVERGED",
        },
    ]


def _usage() -> dict:
    return {
        "actual_cost_usd": 0.0,
        "budget_usd": 10.0,
        "completion_tokens": 0,
        "outbound_request_cap": 326,
        "outbound_requests": 1,
        "price_input_per_1m_usd": 0.2,
        "price_output_per_1m_usd": 1.2,
        "prompt_tokens": 0,
        "total_tokens": 0,
        "within_budget": True,
    }


def _write(path: Path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _build_run(root: Path) -> Path:
    """A minimally complete run tree whose derived files agree with the event log."""
    out, analysis = root / "output", root / "analysis"
    out.mkdir(parents=True, exist_ok=True)
    analysis.mkdir(parents=True, exist_ok=True)

    (out / "qa_events.jsonl").write_text(
        "".join(json.dumps(e) + "\n" for e in _events()), encoding="utf-8"
    )
    _write(
        out / "run-receipt.json",
        {
            "setting_id": "cd_airtravel",
            "corpus_id": "text2uml_airtravel_253b26dc",
            "N": 4,
            "episode_count": 1,
            "question_count": 1,
            "answer_count": 1,
            "protected_orchestrator_fake_route_pair_count": 1,
            "routes": [{"source_agent": "agent3", "target_agent": "agent2", "question_count": 1}],
            "blocked_egress_attempts": 0,
            "status": "TECHNICAL_SUCCESS",
            "technical_exception": None,
            "usage": _usage(),
        },
    )
    _write(
        out / "compliance_vectors.json",
        {
            case: {
                "existing_mapping": [{"compliance_status": "Satisfied"}],
                "coverage_summary": {"satisfied": 1, "partially_satisfied": 0, "not_satisfied": 0},
            }
            for case in ("01", "02", "03", "04")
        },
    )
    _write(out / "uncovered_fragments.json", {c: {"uncovered_fragments": []} for c in ("01", "02", "03", "04")})
    _write(out / "reference_guidelines.json", {"reference_guidelines": [{"mapping_certainty": 0.85}]})
    _write(
        out / "variability_classifications.json",
        {
            "variability_classifications": [
                {
                    "pattern_id": "P1",
                    "classification": "Substantial Variability",
                    "confidence": "High",
                    "flag_for_guidelines_update": True,
                    "requires_human_review": False,
                }
            ]
        },
    )
    _write(
        out / "deviation_patterns.json",
        {
            "recurring_guideline_patterns": [],
            "recurring_fragment_patterns": [
                {"pattern_id": "P1", "dominant_fragment_label": "Alternative", "probe_confirmed": False}
            ],
        },
    )
    _write(
        analysis / "detector-summary.json",
        {
            "denominators": {"detector_v1_denominator": 1, "complete_episodes": 1},
            "detector_v1": {"STRONG_ALERT": 1, "WEAK_ALERT": 0, "NO_ALERT": 0, "EXCLUDED": 0},
            "termination_states": {"CONVERGED": 1},
            "counts": {"answers": 1, "max_round_index": 1, "questions": 1, "route_pairs": 1},
            "usage": _usage(),
            "signals_fired": SIGNALS,
            "evidence": {
                "event_log_sha256": __import__("hashlib")
                .sha256((out / "qa_events.jsonl").read_bytes())
                .hexdigest(),
                "event_count": 3,
            },
        },
    )
    _write(
        analysis / "extended-analytics.json",
        {
            "confidence_distribution": {"Low": 1},
            "answer_evidence_length": {"n": 1, "min": 40, "median": 40, "max": 40},
            "question_density_S9": {"per_episode": [1]},
            "round_dynamics": {"per_round": [{"round_index": 1, "low": 1, "medium": 0, "high": 0}]},
            "episode_profiles": [
                {"episode_id": EPISODE, "low": 1, "medium": 0, "high": 0, "max_round": 1}
            ],
            "pipeline_outputs": {
                "C1_mapping_certainty_values": [0.85],
                "C2_agent4_confidence_distribution": {"High": 1},
                "C3_flag_for_guidelines_update": {"true": 1},
                "classification_distribution": {"Substantial Variability": 1},
                "deviation_patterns": 1,
                "fragment_label_distribution": {"Alternative": 1},
                "mapping_status_distribution": {"Satisfied": 4},
                "per_case": {c: {"uncovered_fragments": 0} for c in ("01", "02", "03", "04")},
                "reference_guidelines": 1,
            },
        },
    )
    inventory = analysis / "output-inventory.json"
    _write(inventory, {"artifacts": {}})
    _write(
        analysis / "analysis-receipt.json",
        {
            "detector_v1": {"STRONG_ALERT": 1, "WEAK_ALERT": 0, "NO_ALERT": 0, "EXCLUDED": 0},
            "denominators": {"detector_v1_denominator": 1},
            "output_inventory_sha256": __import__("hashlib")
            .sha256(inventory.read_bytes())
            .hexdigest(),
        },
    )
    _write(
        analysis / "detector-envelope.json",
        {"provider_calls": 0, "evidence_class": "ENGINEERING_FIXTURE_NOT_SCIENTIFIC", "modes": []},
    )
    _write(
        analysis / "baseline-comparison.json",
        {
            "note": "fake fixture provider",
            "real_provider_run": {
                "answers": 1,
                "confidence": {"Low": 1},
                "episodes": 1,
                "evidence_missing": 0,
                "max_round": 1,
                "questions": 1,
                "routes": 1,
                "terminations": {"CONVERGED": 1},
            },
            "real_usage": _usage(),
            "detector_v1_real_run_only": {
                "STRONG_ALERT": 1,
                "WEAK_ALERT": 0,
                "NO_ALERT": 0,
                "EXCLUDED": 0,
            },
        },
    )
    (analysis / "detector.csv").write_text(
        "episode_id,classification,reason_codes,all_signals_fired\n"
        f"{EPISODE},STRONG_ALERT,S1_LOW_ANSWER_CONFIDENCE,S1_LOW_ANSWER_CONFIDENCE\n",
        encoding="utf-8",
    )
    (analysis / "episodes.csv").write_text(
        "episode_id,termination_reason,questions,answers,rounds,routes,in_detector_denominator\n"
        f"{EPISODE},CONVERGED,1,1,1,agent3->agent2,True\n",
        encoding="utf-8",
    )
    return root


def _run(run_root: Path, manifest: Path) -> tuple[int, dict]:
    proc = subprocess.run(
        [sys.executable, str(VALIDATOR), "--run-root", str(run_root), "--manifest", str(manifest)],
        capture_output=True,
        text=True,
        cwd=ROOT,
    )
    payload = json.loads(manifest.read_text(encoding="utf-8")) if manifest.is_file() else {}
    return proc.returncode, payload


def test_intact_run_reports_no_scientific_value_failure(tmp_path: Path) -> None:
    _, payload = _run(_build_run(tmp_path / "run"), tmp_path / "m.json")
    assert payload["scientific_values_reproduce"] is True
    assert payload["status"] != "EVIDENCE_INVALID"


def test_corrupted_derived_signal_count_is_invalid(tmp_path: Path) -> None:
    root = _build_run(tmp_path / "run")
    summary = root / "analysis" / "detector-summary.json"
    data = json.loads(summary.read_text(encoding="utf-8"))
    data["signals_fired"]["S1_LOW_ANSWER_CONFIDENCE"] = 99
    _write(summary, data)
    code, payload = _run(root, tmp_path / "m.json")
    assert code == 1
    assert payload["status"] == "EVIDENCE_INVALID"
    assert payload["scientific_values_reproduce"] is False


def test_missing_derived_artifact_fails_closed(tmp_path: Path) -> None:
    """Deleting a derived file must not silently remove its cross-checks."""
    root = _build_run(tmp_path / "run")
    (root / "analysis" / "detector-summary.json").unlink()
    code, payload = _run(root, tmp_path / "m.json")
    assert code == 1
    assert payload["status"] == "EVIDENCE_INVALID"


def test_absent_evidence_is_not_verifiable(tmp_path: Path) -> None:
    empty = tmp_path / "empty"
    empty.mkdir()
    code, payload = _run(empty, tmp_path / "m.json")
    assert code == 2
    assert payload["status"] == "NOT_VERIFIABLE"


def test_c2_reported_as_unavailable_fails(tmp_path: Path) -> None:
    """A document may not claim C2/C3 are NOT_AVAILABLE while the fields are populated."""
    root = _build_run(tmp_path / "run")
    _write(root / "output" / "variability_classifications.json", {"variability_classifications": []})
    code, payload = _run(root, tmp_path / "m.json")
    assert code == 1
    names = {row["check"] for row in payload["checks"] if row["status"] == "FAIL"}
    assert "C2 is computable from pipeline outputs" in names


def test_refuses_to_overwrite_a_foreign_artifact(tmp_path: Path) -> None:
    """The overwrite that destroyed analysis/output-inventory.json must not be repeatable."""
    root = _build_run(tmp_path / "run")
    victim = tmp_path / "someone-elses.json"
    _write(victim, {"schema_version": "not-this-validator", "value": 1})
    proc = subprocess.run(
        [sys.executable, str(VALIDATOR), "--run-root", str(root), "--manifest", str(victim)],
        capture_output=True,
        text=True,
        cwd=ROOT,
    )
    assert proc.returncode == 3
    assert json.loads(victim.read_text(encoding="utf-8"))["value"] == 1


@pytest.mark.parametrize("field", ["episode_count", "question_count", "answer_count"])
def test_receipt_disagreeing_with_the_event_log_is_invalid(tmp_path: Path, field: str) -> None:
    root = _build_run(tmp_path / "run")
    receipt_path = root / "output" / "run-receipt.json"
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    receipt[field] = receipt[field] + 7
    _write(receipt_path, receipt)
    code, payload = _run(root, tmp_path / "m.json")
    assert code == 1
    assert payload["status"] == "EVIDENCE_INVALID"
