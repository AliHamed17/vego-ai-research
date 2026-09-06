"""Fail-closed locator and validator for the accepted Study 1 evidence chain.

The accepted run is private evidence.  This module never searches for it, copies
it, prints it, or writes inside the evidence root.  A caller must provide an
explicitly mounted read-only root and a binding manifest created from the
original artifacts.  Only hashes, safe aggregate counts, and validation states
leave this boundary.

The validator deliberately does not trust narrative reports.  It accepts a
scientific run only when the manifest identifies the accepted replacement run,
all declared bytes match, the event stream is a single valid run, and any
available aggregate artifacts agree with a recomputation from that stream.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any

import jsonschema

ROOT = Path(__file__).resolve().parents[1]
FRAMEWORK = ROOT / "VEGO-AI" / "framework"
SCRIPTS = ROOT / "scripts"
if str(FRAMEWORK) not in sys.path:
    sys.path.insert(0, str(FRAMEWORK))
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

SETTING_ID = "cd_airtravel"
CORPUS_ID = "text2uml_airtravel_253b26dc"

ACCEPTED = "ACCEPTED_FOR_DESCRIPTIVE_REPORTING_WITH_RETROSPECTIVE_PROVENANCE"
PARTIAL = "PARTIAL_EVIDENCE_ONLY"
EVIDENCE_INVALID = "EVIDENCE_INVALID"
EVIDENCE_NOT_AVAILABLE = "EVIDENCE_NOT_AVAILABLE_IN_REVIEWED_WORKTREE"

LOCATION_CLASS = "authorized_read_only_evidence_root"
PRIMARY_ARTIFACTS = ("qa_events_jsonl", "run_receipt", "pipeline_output_manifest")
OPTIONAL_ARTIFACTS = ("detector_summary", "episode_csv", "detector_csv")
HEX64 = re.compile(r"^[0-9a-f]{64}$")


class EvidenceRecoveryError(ValueError):
    """Raised for a malformed or unsafe evidence binding."""


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _safe_digest_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _check(name: str, status: str, *, expected: Any = None, actual: Any = None, note: str = "") -> dict[str, Any]:
    return {"check": name, "status": status, "expected": expected, "actual": actual, "note": note}


def _relative_artifact(root: Path, descriptor: dict[str, Any], name: str) -> Path:
    if not isinstance(descriptor, dict):
        raise EvidenceRecoveryError(f"{name} artifact descriptor is not an object")
    relative = descriptor.get("path")
    expected = descriptor.get("sha256")
    if not isinstance(relative, str) or not relative or Path(relative).is_absolute():
        raise EvidenceRecoveryError(f"{name} artifact path must be relative")
    parts = Path(relative).parts
    if any(part in {"", ".", ".."} for part in parts) or "\\" in relative:
        raise EvidenceRecoveryError(f"{name} artifact path is unsafe")
    if not isinstance(expected, str) or not HEX64.fullmatch(expected):
        raise EvidenceRecoveryError(f"{name} artifact hash is invalid")
    target = root / Path(*parts)
    resolved_root = root.resolve(strict=True)
    resolved = target.resolve(strict=False)
    try:
        resolved.relative_to(resolved_root)
    except ValueError as exc:
        raise EvidenceRecoveryError(f"{name} artifact escapes evidence root") from exc
    cursor = root
    for part in parts:
        cursor = cursor / part
        if cursor.is_symlink():
            raise EvidenceRecoveryError(f"{name} artifact uses a symlink/reparse path")
    if not target.is_file():
        raise EvidenceRecoveryError(f"{name} artifact is missing")
    return target


def _json(path: Path, label: str) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise EvidenceRecoveryError(f"{label} is not valid JSON") from exc
    if not isinstance(value, dict):
        raise EvidenceRecoveryError(f"{label} must be a JSON object")
    return value


def _load_events(path: Path) -> list[dict[str, Any]]:
    from qa_communication import load_event_stream

    try:
        events = load_event_stream(path)
    except Exception as exc:  # noqa: BLE001 - public boundary must fail closed
        raise EvidenceRecoveryError(f"event stream failed schema/lifecycle validation: {type(exc).__name__}") from exc
    if not events:
        raise EvidenceRecoveryError("accepted event stream is empty")
    run_ids = {event.get("run_id") for event in events}
    if len(run_ids) != 1 or None in run_ids:
        raise EvidenceRecoveryError("accepted event stream must contain exactly one non-empty run_id")
    _strict_lifecycle(events)
    return events


def _strict_lifecycle(events: list[dict[str, Any]]) -> None:
    """Apply accepted-run invariants without changing the protected recorder."""
    from qa_communication import TERMINATION_REASONS

    run_ids = {event.get("run_id") for event in events}
    if len(run_ids) != 1 or not next(iter(run_ids)):
        raise EvidenceRecoveryError("exactly one run_id is required")
    by_episode: dict[str, list[dict[str, Any]]] = {}
    questions: dict[str, dict[str, Any]] = {}
    for event in events:
        by_episode.setdefault(event["episode_id"], []).append(event)
        if event["event_type"] == "QUESTION_EMITTED":
            questions[event["question_id"]] = event
    for episode_id, rows in by_episode.items():
        terminals = [row for row in rows if row["event_type"] == "EPISODE_TERMINATED"]
        if len(terminals) != 1:
            raise EvidenceRecoveryError(f"episode {episode_id} does not have exactly one terminal event")
        terminal = terminals[0]
        if rows[-1] is not terminal:
            raise EvidenceRecoveryError(f"episode {episode_id} contains events after termination")
        episode_questions = [row for row in rows if row["event_type"] == "QUESTION_EMITTED"]
        reason = terminal.get("termination_reason")
        if reason in {"CONVERGED", "TERMINATED_MAX_ROUNDS"} and not episode_questions:
            raise EvidenceRecoveryError(f"scientific episode {episode_id} has no question")
        answers = [row for row in rows if row["event_type"] == "ANSWER_RECEIVED"]
        answer_counts = Counter(row.get("question_id") for row in answers)
        if any(count != 1 for count in answer_counts.values()):
            raise EvidenceRecoveryError(f"episode {episode_id} has duplicate answers")
        # Every emitted question must have exactly one later answer, including
        # episodes that eventually become technical-incomplete.  Otherwise a
        # partial transport record could be mistaken for a complete scientific
        # episode during downstream aggregation.
        if any(answer_counts.get(row["question_id"], 0) != 1 for row in episode_questions):
            raise EvidenceRecoveryError(f"episode {episode_id} has an unanswered or multiply answered question")
        if reason not in TERMINATION_REASONS:
            raise EvidenceRecoveryError(f"episode {episode_id} has an unsupported termination reason")
    # Every answer must resolve to a prior question in the same episode.
    for index, event in enumerate(events):
        if event["event_type"] != "ANSWER_RECEIVED":
            continue
        question = questions.get(event.get("question_id"))
        if question is None or question["episode_id"] != event["episode_id"]:
            raise EvidenceRecoveryError("answer references an unknown or cross-episode question")
        if question["sequence"] >= event["sequence"] or question["sequence"] >= index + 1:
            raise EvidenceRecoveryError("answer does not follow its question")


def _hash_and_record(root: Path, descriptors: dict[str, Any], name: str, checks: list[dict[str, Any]]) -> Path:
    target = _relative_artifact(root, descriptors.get(name), name)
    observed = digest(target)
    expected = descriptors[name]["sha256"]
    checks.append(_check(f"{name} byte hash", "PASS" if observed == expected else "FAIL", expected=expected, actual=observed))
    if observed != expected:
        raise EvidenceRecoveryError(f"{name} hash mismatch")
    return target


def _number(value: Any) -> int | float | None:
    return value if type(value) in {int, float} else None


def _compare_optional(mapping: dict[str, Any], candidates: list[tuple[str, Any]], checks: list[dict[str, Any]], label: str) -> None:
    for key, recomputed in candidates:
        if key not in mapping:
            continue
        actual = mapping[key]
        checks.append(_check(f"{label}.{key}", "PASS" if actual == recomputed else "FAIL", expected=recomputed, actual=actual))
        if actual != recomputed:
            raise EvidenceRecoveryError(f"{label}.{key} disagrees with event recomputation")


def _recompute(events: list[dict[str, Any]]) -> dict[str, Any]:
    from airtravel_detector_analysis import project_episodes
    from extract_qa_escalation_features import detect_detector_v1

    projections = project_episodes(events)
    verdicts = [detect_detector_v1(episode) for episode in projections]
    complete = [row for row in projections if row.get("scientific_complete")]
    scored = [row for row in verdicts if row.get("classification") != "EXCLUDED"]
    answers = [event for event in events if event["event_type"] == "ANSWER_RECEIVED"]
    questions = [event for event in events if event["event_type"] == "QUESTION_EMITTED"]
    routes = Counter((event.get("source_agent"), event.get("target_agent")) for event in questions)
    lengths = [int((event.get("answer_evidence_ref") or {}).get("length", 0)) for event in answers]
    return {
        "total_episodes": len(projections),
        "complete_episodes": len(complete),
        "excluded_episodes": len(projections) - len(complete),
        "detector_v1_denominator": len(scored),
        "questions": len(questions),
        "answers": len(answers),
        "max_round_index": max((int(event.get("round_index") or 0) for event in questions), default=0),
        "route_pair_count": len(routes),
        "termination_states": dict(Counter(row.get("termination_reason") for row in projections)),
        "confidence": dict(Counter(event.get("answer_confidence") for event in answers)),
        "evidence": {
            "answer_count": len(lengths),
            "present_count": sum(length > 0 for length in lengths),
            "zero_length_count": sum(length == 0 for length in lengths),
            "min_length": min(lengths) if lengths else None,
            "max_length": max(lengths) if lengths else None,
        },
        "detector_v1": dict(Counter(row["classification"] for row in scored)),
        "signals": dict(Counter(signal for row in scored for signal in detect_detector_v1(next(ep for ep in projections if ep["episode_id"] == row["episode_id"]))["all_signals_fired"])),
        "route_counts": {f"{source}->{target}": count for (source, target), count in sorted(routes.items())},
    }


def _safe_aggregate(recomputed: dict[str, Any]) -> dict[str, Any]:
    return {
        "evidence_status": ACCEPTED,
        "denominator": "complete_episodes",
        "recomputed": recomputed,
        "claim_boundary": "descriptive_only; no correctness, benefit, effectiveness, accuracy, or generalization claim",
    }


def unavailable_result(note: str) -> dict[str, Any]:
    return {
        "schema_version": "study1-evidence-recovery-v1",
        "status": EVIDENCE_NOT_AVAILABLE,
        "location_class": LOCATION_CLASS,
        "note": note,
        "run_id_sha256": None,
        "checks": [_check("private accepted evidence root", "NOT_AVAILABLE", note=note)],
        "recomputed": None,
        "safe_values": {"episode_count": "NOT_AVAILABLE_IN_WORKTREE", "question_count": "NOT_AVAILABLE_IN_WORKTREE", "answer_count": "NOT_AVAILABLE_IN_WORKTREE"},
    }


def recover(evidence_root: Path, binding_manifest: Path) -> dict[str, Any]:
    """Validate one explicitly supplied private evidence root without mutating it."""
    checks: list[dict[str, Any]] = []
    root = evidence_root
    if not root.exists() or not root.is_dir() or root.is_symlink():
        return unavailable_result("explicit read-only evidence root is absent from the reviewed worktree")
    if not binding_manifest.is_file() or binding_manifest.is_symlink():
        return unavailable_result("private binding manifest is absent from the reviewed worktree")
    try:
        manifest = _json(binding_manifest, "binding manifest")
        schema = _json(ROOT / "schemas/study1-evidence-binding-v1.schema.json", "binding schema")
        try:
            jsonschema.Draft202012Validator(schema).validate(manifest)
        except jsonschema.ValidationError as exc:
            identity = manifest.get("run_identity") if isinstance(manifest.get("run_identity"), dict) else {}
            checks.append(
                _check(
                    "fake or non-accepted run exclusion",
                    "FAIL",
                    actual={
                        "run_class": identity.get("run_class"),
                        "fake_preflight": identity.get("fake_preflight"),
                    },
                    note="binding schema rejected an unsafe run identity",
                )
            )
            raise EvidenceRecoveryError(f"binding manifest schema invalid: {exc.message}") from exc
        if manifest.get("schema_version") != "study1-evidence-binding-v1":
            raise EvidenceRecoveryError("unsupported binding manifest schema")
        identity = manifest.get("run_identity")
        if not isinstance(identity, dict):
            raise EvidenceRecoveryError("run_identity is missing")
        checks.append(_check("accepted replacement identity", "PASS" if identity.get("accepted_replacement") is True and identity.get("run_class") == "accepted_replacement_real_run" else "FAIL"))
        if manifest.get("accepted_run") is not True or identity.get("accepted_replacement") is not True or identity.get("run_class") != "accepted_replacement_real_run" or identity.get("fake_preflight") is True:
            checks.append(_check("fake or non-accepted run exclusion", "FAIL", note="fake preflight, failed attempt, or unknown run cannot support science"))
            raise EvidenceRecoveryError("binding does not identify the accepted replacement real run")
        checks.append(_check("fake or non-accepted run exclusion", "PASS"))
        run_id = identity.get("run_id")
        if not isinstance(run_id, str) or not run_id:
            raise EvidenceRecoveryError("accepted run_id is missing")
        if manifest.get("setting_id") != SETTING_ID or manifest.get("corpus_id") != CORPUS_ID:
            raise EvidenceRecoveryError("setting_id/corpus_id binding mismatch")
        descriptors = manifest.get("artifacts")
        if not isinstance(descriptors, dict):
            raise EvidenceRecoveryError("artifact binding map is missing")
        for name in PRIMARY_ARTIFACTS:
            if name not in descriptors:
                raise EvidenceRecoveryError(f"primary artifact binding missing: {name}")
        paths = {name: _hash_and_record(root, descriptors, name, checks) for name in PRIMARY_ARTIFACTS}
        for name in OPTIONAL_ARTIFACTS:
            if name in descriptors:
                _hash_and_record(root, descriptors, name, checks)
        events = _load_events(paths["qa_events_jsonl"])
        checks.append(_check("event stream has exactly one run_id", "PASS", expected=run_id, actual=events[0]["run_id"]))
        if {event["run_id"] for event in events} != {run_id}:
            raise EvidenceRecoveryError("event stream run_id differs from binding")
        receipt = _json(paths["run_receipt"], "run receipt")
        if receipt.get("run_id") != run_id:
            raise EvidenceRecoveryError("run receipt run_id differs from binding")
        if receipt.get("status") not in {"ACCEPTED_REPLACEMENT", "ACCEPTED"}:
            raise EvidenceRecoveryError("run receipt does not identify the accepted replacement")
        if receipt.get("setting_id") != SETTING_ID or receipt.get("corpus_id") != CORPUS_ID:
            raise EvidenceRecoveryError("run receipt setting/corpus differs from binding")
        if receipt.get("event_log_sha256") != digest(paths["qa_events_jsonl"]):
            raise EvidenceRecoveryError("run receipt event-log hash mismatch")
        provenance_gaps: list[str] = []
        for field, label in (("execution_code_sha256", "execution code"), ("config_sha256", "configuration")):
            if receipt.get(field) is None:
                provenance_gaps.append(f"run receipt does not bind {label} hash")
            elif receipt.get(field) != manifest.get(field):
                raise EvidenceRecoveryError(f"{label} hash differs from binding")
        recomputed = _recompute(events)
        _compare_optional(receipt, [("episode_count", recomputed["total_episodes"]), ("question_count", recomputed["questions"]), ("answer_count", recomputed["answers"]), ("termination_counts", recomputed["termination_states"])], checks, "run_receipt")
        pipeline = _json(paths["pipeline_output_manifest"], "pipeline output manifest")
        counts = pipeline.get("counts") if isinstance(pipeline.get("counts"), dict) else pipeline
        _compare_optional(counts, [("episodes", recomputed["total_episodes"]), ("questions", recomputed["questions"]), ("answers", recomputed["answers"])], checks, "pipeline_output_manifest")
        if "detector_summary" in descriptors:
            detector = _json(_relative_artifact(root, descriptors["detector_summary"], "detector_summary"), "detector summary")
            denominators = detector.get("denominators") if isinstance(detector.get("denominators"), dict) else {}
            detector_counts = detector.get("counts") if isinstance(detector.get("counts"), dict) else {}
            _compare_optional(denominators, [("complete_episodes", recomputed["complete_episodes"]), ("detector_v1_denominator", recomputed["detector_v1_denominator"])], checks, "detector_summary.denominators")
            _compare_optional(detector_counts, [("questions", recomputed["questions"]), ("answers", recomputed["answers"])], checks, "detector_summary.counts")
        status = PARTIAL if provenance_gaps else ACCEPTED
        return {
            "schema_version": "study1-evidence-recovery-v1",
            "status": status,
            "location_class": LOCATION_CLASS,
            "run_id_sha256": _safe_digest_text(run_id),
            "binding_manifest_sha256": digest(binding_manifest),
            "artifact_hashes": {name: descriptors[name]["sha256"] for name in descriptors},
            "checks": checks,
            "recomputed": recomputed,
            "safe_values": _safe_aggregate(recomputed),
            "provenance_gaps": provenance_gaps,
        }
    except EvidenceRecoveryError as exc:
        checks.append(_check("evidence chain", "FAIL", note=str(exc)))
        return {
            "schema_version": "study1-evidence-recovery-v1",
            "status": EVIDENCE_INVALID,
            "location_class": LOCATION_CLASS,
            "checks": checks,
            "recomputed": None,
            "safe_values": {"episode_count": "NOT_AVAILABLE_AFTER_INVALID_CHAIN", "question_count": "NOT_AVAILABLE_AFTER_INVALID_CHAIN", "answer_count": "NOT_AVAILABLE_AFTER_INVALID_CHAIN"},
        }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--evidence-root", type=Path, required=True)
    parser.add_argument("--binding-manifest", type=Path, required=True)
    parser.add_argument("--safe-output", type=Path)
    args = parser.parse_args(argv)
    result = recover(args.evidence_root, args.binding_manifest)
    if args.safe_output:
        args.safe_output.parent.mkdir(parents=True, exist_ok=True)
        args.safe_output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": result["status"], "location_class": result["location_class"], "check_count": len(result["checks"])}, sort_keys=True))
    return 0 if result["status"] == ACCEPTED else 2


if __name__ == "__main__":
    raise SystemExit(main())
