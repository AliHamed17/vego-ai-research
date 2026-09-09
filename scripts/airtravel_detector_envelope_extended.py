"""Extended Detector-v1 envelope: a complete truth table of the frozen rule on fixtures.

The original envelope drives three fixture modes, but its fake client hard-codes High confidence
and non-empty evidence, so it can only ever reach NO_ALERT (converged, one round) or STRONG_ALERT
via S7 (max rounds). Two of the rule's three classes and two of its three strong branches had
therefore never been produced anywhere: WEAK_ALERT had not been observed, and S3 had never fired.

This script covers the previously unreached classes and branches on synthetic input. It
subclasses the fixture client and injects, per mode, the answer confidence, the evidence value,
and the round schedule, so that each mode isolates one branch of the frozen rule (S7 cannot be
separated from S6). It does not modify airtravel_local_observer.py, which is part of the
accepted run's execution lineage, and it does not touch Detector-v1 or its thresholds.

Every mode runs the real protected orchestrator against a deterministic fake. Fixture calls are
counted from the fake's ledger. Provider absence is structural — the protected runtime stubs the
provider client constructor and the single construction site is monkeypatched to the fake — and
is audited after each mode by checking that no provider SDK module was imported; the row is
refused, not written, if that audit fails.

Evidence class: ENGINEERING_FIXTURE_NOT_SCIENTIFIC. These rows say nothing about any real model.
They characterise the instrument's reachable outputs on known input; they do not establish that
any alert is correct.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
import tempfile
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "VEGO-AI/framework"))

ANSWER_LABELS = {"agent1/answer_language_questions", "agent2/answer_domain_questions"}
PRESENT = "Local fixture evidence."
LEGACY_MODES = ("no_questions", "two_rounds", "max_rounds")
# Orchestrator output echoes private corpus text, so it must land under gitignored
# external_data/** and be deleted once the event log has been projected — never in system TEMP.
SCRATCH_ROOT = ROOT / "external_data/airtravel-pr38/scratch"

S1, S2, S3 = "S1_LOW_ANSWER_CONFIDENCE", "S2_MEDIUM_ANSWER_CONFIDENCE", "S3_MISSING_ANSWER_EVIDENCE"
S6, S7 = "S6_MULTIPLE_QA_ROUNDS", "S7_TERMINATED_MAX_ROUNDS"

# Legacy modes run the parent fixture untouched so their rows stay comparable with the original
# envelope ("two_rounds" is a legacy name for a schedule that asks in round 1 only).
# S7 cannot be isolated from S6: reaching the round cap implies more than one round.
MODES: dict[str, dict[str, Any]] = {
    "no_questions":          {"confidence": "High",   "evidence": PRESENT, "rounds": set(),  "expected": None,           "signals": set(),     "branch": "no episode; denominator 0"},
    "two_rounds":            {"confidence": "High",   "evidence": PRESENT, "rounds": {1},    "expected": "NO_ALERT",     "signals": set(),     "branch": "no signal"},
    "max_rounds":            {"confidence": "High",   "evidence": PRESENT, "rounds": "all",  "expected": "STRONG_ALERT", "signals": {S6, S7},  "branch": "S7 (S6 necessarily co-fires)"},
    "low_single":            {"confidence": "Low",    "evidence": PRESENT, "rounds": {1},    "expected": "STRONG_ALERT", "signals": {S1},      "branch": "S1 alone"},
    "empty_evidence_single": {"confidence": "High",   "evidence": "",      "rounds": {1},    "expected": "STRONG_ALERT", "signals": {S3},      "branch": "S3 alone, length-0 branch"},
    "null_evidence_single":  {"confidence": "High",   "evidence": None,    "rounds": {1},    "expected": "STRONG_ALERT", "signals": {S3},      "branch": "S3 alone, null branch"},
    "medium_single":         {"confidence": "Medium", "evidence": PRESENT, "rounds": {1},    "expected": "WEAK_ALERT",   "signals": {S2},      "branch": "S2 alone"},
    "high_two_rounds":       {"confidence": "High",   "evidence": PRESENT, "rounds": {1, 2}, "expected": "WEAK_ALERT",   "signals": {S6},      "branch": "S6 alone"},
    "medium_two_rounds":     {"confidence": "Medium", "evidence": PRESENT, "rounds": {1, 2}, "expected": "WEAK_ALERT",   "signals": {S2, S6},  "branch": "S2 and S6 together; still weak"},
}


def make_fake(mode: str):
    """Build a fixture client for `mode` without editing the accepted lineage file.

    Legacy modes return the parent class unchanged. New modes keep the parent permanently in
    its "no_questions" state (the extended mode lives in `fixture_mode`), so none of the parent's
    own branches can fire — in particular the agent4/classify variability row that "max_rounds"
    injects, which was found to alter the pipeline's phase structure and contaminate every other
    mode when the parent's mode was swapped to force a question. Questions are added onto the
    parent's own empty result for exactly the scheduled rounds, answer rows are rewritten with
    the injected confidence and evidence, and this call's ledger row (located by index, not by
    position at resume time) is refreshed to describe what was actually returned.
    """
    from airtravel_local_observer import RecordingFake, digest, metadata

    if mode in LEGACY_MODES:
        return RecordingFake(mode)
    spec = MODES[mode]

    class ExtendedFake(RecordingFake):
        def __init__(self) -> None:
            super().__init__("no_questions")
            self.fixture_mode = mode

        def _refresh(self, index, result):
            record = self.calls[index]
            record["answer_sha256"] = record["decision_sha256"] = digest(result)
            return result

        async def call(self, prompt, *, label):
            # The parent appends this call's ledger row synchronously before its first await, so
            # the row index captured here stays correct when concurrent cases interleave.
            index = len(self.calls)
            result = await super().call(prompt, label=label)
            if label in ANSWER_LABELS:
                for row in result.get("questions_answers", []):
                    row["confidence"] = spec["confidence"]
                    if spec["evidence"] is None:
                        row.pop("evidence", None)
                    else:
                        row["evidence"] = spec["evidence"]
                return self._refresh(index, result)
            meta = metadata(label, "fixture", "fixture")
            if meta is None or meta["round_index"] not in spec["rounds"]:
                return result
            result["questions_to_language_advisor"] = [{"question": "Local language fixture: " + label}]
            if "feedback" not in label:
                result["questions_to_domain_advisor"] = [{"question": "Local domain fixture: " + label}]
            return self._refresh(index, result)

    return ExtendedFake()


def run_mode(mode: str) -> dict[str, Any]:
    import airtravel_v4_execution as ex
    from airtravel_v4_contract import RUNTIME_FILES

    runtime_root = ROOT / "external_data/airtravel-pr38/runtime_input"
    domain = (runtime_root / "domain_description/description.md").read_text(encoding="utf-8")
    cases = [
        {"case_id": rel.split("/", 1)[1].split("_", 1)[0],
         "case_model": (runtime_root / rel).read_text(encoding="utf-8")}
        for rel in sorted(RUNTIME_FILES) if rel.startswith("candidate_models/")
    ]
    cfg = {
        "setting_id": "cd_airtravel", "corpus_id": "text2uml_airtravel_253b26dc",
        "language_name": "UML", "domain_description": domain, "case_models": cases,
        "max_concurrent_cases": 2, "model": "LOCAL_DETERMINISTIC_FAKE_V4",
        "api_key": None, "provider_execution_enabled": False,
    }
    module = ex._load_protected_runtime()
    SCRATCH_ROOT.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=SCRATCH_ROOT, prefix=f"envelope-ext-{mode}-") as tmp:
        out = Path(tmp) / "output"
        out.mkdir()
        return _run_in(mode, module, cfg, out)


def _run_in(mode: str, module, cfg: dict[str, Any], out: Path) -> dict[str, Any]:
    from airtravel_detector_analysis import project_episodes
    from extract_qa_escalation_features import detect_detector_v1

    async def drive():
        from airtravel_local_observer import Observer, Proxy
        from qa_communication import QACommunicationRecorder
        from qa_registry import QARegistry

        run_id = f"ENVELOPE-EXT-{mode}"
        recorder = QACommunicationRecorder(out / "qa_events.jsonl", run_id=run_id)
        observer = Observer(recorder)
        fake = make_fake(mode)
        proxy = Proxy(fake, observer, 4, cfg["setting_id"], run_id)
        original_client, original_registry = module.LLMClient, module.QARegistry
        module.LLMClient = lambda **_: proxy
        module.QARegistry = observer.registry(QARegistry)
        try:
            await module.run_setting({**cfg, "output_dir": str(out)}, out / "inline.json",
                                     None, cfg["setting_id"])
        finally:
            module.LLMClient, module.QARegistry = original_client, original_registry
            recorder.close_open_episodes()
        return len(fake.calls)

    fake_calls = asyncio.run(drive())
    import airtravel_v4_execution as ex
    sdk_modules = sorted(m for m in ex.OFFLINE_PROVIDER_IMPORTS - {"urllib", "google"} if m in sys.modules)
    stdlib_network = sorted(m for m in ("urllib",) if m in sys.modules)
    if sdk_modules:
        raise RuntimeError(f"provider SDK module loaded during fixture run: {sdk_modules}")
    log = out / "qa_events.jsonl"
    events = ([json.loads(l) for l in log.read_text(encoding="utf-8").splitlines() if l.strip()]
              if log.is_file() else [])
    episodes = project_episodes(events)
    verdicts = [detect_detector_v1(e) for e in episodes]
    scored = [v for v in verdicts if v["classification"] != "EXCLUDED"]
    counts = {"STRONG_ALERT": 0, "WEAK_ALERT": 0, "NO_ALERT": 0}
    for v in scored:
        counts[v["classification"]] += 1
    per_episode_signals = [frozenset(v["all_signals_fired"]) for v in scored]
    signals = sorted(set().union(*per_episode_signals)) if per_episode_signals else []
    answers = [e for e in events if e["event_type"] == "ANSWER_RECEIVED"]
    spec = MODES[mode]
    expected = spec["expected"]
    if expected is None:
        conforms = len(scored) == 0
    else:
        # Every scored episode must land in the expected class AND show exactly the expected
        # signal set; a stray signal means the mode did not isolate the branch it claims to.
        conforms = (len(scored) > 0 and counts[expected] == len(scored)
                    and all(s == frozenset(spec["signals"]) for s in per_episode_signals))
    return {
        "fixture_mode": mode,
        "isolated_branch": spec["branch"],
        "injected_confidence": spec["confidence"],
        "injected_evidence": ("<absent>" if spec["evidence"] is None
                              else "<empty>" if spec["evidence"] == "" else "<present>"),
        "question_rounds": "all" if spec["rounds"] == "all" else sorted(spec["rounds"]),
        "evidence_class": "ENGINEERING_FIXTURE_NOT_SCIENTIFIC",
        "fake_calls": fake_calls,
        "provider_calls": 0,
        "provider_absence_basis": {
            "construction_guard": "llm_client.LLMClient stubbed to raise PermissionError by the protected runtime loader",
            "construction_site": "orchestrator LLMClient monkeypatched to the recording fake proxy for the run",
            "provider_sdk_modules_loaded_after_run": sdk_modules,
            "stdlib_network_modules_loaded_after_run": stdlib_network,
            "audited_module_set": sorted(ex.OFFLINE_PROVIDER_IMPORTS),
        },
        "events": len(events),
        "episodes_observed": len(episodes),
        "complete_episodes": sum(1 for e in episodes if e["scientific_complete"]),
        "questions": sum(e["event_type"] == "QUESTION_EMITTED" for e in events),
        "answers": len(answers),
        "max_round_index": max((e["round_count"] for e in episodes), default=0),
        "confidence_observed": sorted({a.get("answer_confidence") for a in answers}),
        "evidence_zero_length_answers": sum(
            1 for a in answers if (a.get("answer_evidence_ref") or {}).get("length", 0) == 0),
        "termination_states": {
            r: sum(1 for e in episodes if e["termination_reason"] == r)
            for r in sorted({e["termination_reason"] for e in episodes if e["termination_reason"]})},
        "signals_fired_any_episode": signals,
        "expected_signals": sorted(spec["signals"]),
        "episodes_with_exact_expected_signals": sum(
            1 for s in per_episode_signals if s == frozenset(spec["signals"])),
        "detector_v1": counts,
        "detector_denominator": len(scored),
        "expected_class": expected,
        "conforms_to_frozen_rule": conforms,
        "run_level_status": "VALID_ZERO_QA_RUN" if not events else "QA_OBSERVED",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    rows = [run_mode(m) for m in MODES]
    classes = sorted({c for r in rows for c, n in r["detector_v1"].items() if n})
    payload = {
        "schema_version": "airtravel-detector-envelope-extended-v1",
        "evidence_class": "ENGINEERING_FIXTURE_NOT_SCIENTIFIC",
        "provider_calls": 0,
        "fake_calls_total": sum(r["fake_calls"] for r in rows),
        "modes": rows,
        "truth_table": {
            "classes_reachable": classes,
            "all_three_classes_reached": {"STRONG_ALERT", "WEAK_ALERT", "NO_ALERT"} <= set(classes),
            "strong_branches_isolated": sorted(
                r["isolated_branch"] for r in rows if r["expected_class"] == "STRONG_ALERT"),
            "weak_branches_isolated": sorted(
                r["isolated_branch"] for r in rows if r["expected_class"] == "WEAK_ALERT"),
            "modes_conforming": sum(1 for r in rows if r["conforms_to_frozen_rule"]),
            "modes_total": len(rows),
        },
        "note": (
            "Deterministic fixtures driving the real protected orchestrator. Not a scientific "
            "result; excluded from every scientific denominator; says nothing about any real "
            "model. It establishes that every class and every strong branch of the frozen rule "
            "is reachable, which the single accepted run and the original envelope did not."
        ),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes((json.dumps(payload, indent=2, sort_keys=True) + "\n").encode("utf-8"))
    tt = payload["truth_table"]
    print(f"modes {tt['modes_total']} conforming {tt['modes_conforming']} "
          f"classes {classes} all_three={tt['all_three_classes_reached']} "
          f"fake_calls={payload['fake_calls_total']} provider_calls=0")
    for r in rows:
        print(f"  {r['fixture_mode']:24} -> {r['detector_v1']}  denom={r['detector_denominator']}  "
              f"signals={r['signals_fired_any_episode']}  conforms={r['conforms_to_frozen_rule']}")
    return 0 if tt["modes_conforming"] == tt["modes_total"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
