#!/usr/bin/env python3
"""Fail-closed, read-only evidence audit for the Iris preliminary pilot.

The verifier inspects existing local artifacts only. It performs no model/API
calls, writes no files, changes no VEGO-AI behavior, and never reads the sealed
EXP-003 item mapping as structured data. Its output is a sanitized JSON receipt.
"""

from __future__ import annotations

import argparse
import collections
import csv
import hashlib
import io
import json
import pathlib
import re
import subprocess
import sys
import zipfile
from collections.abc import Iterable
from typing import Any

SETTINGS = ("ucd_ch", "ucd_pw", "cd_ch", "cd_pw")
OFFICIAL_BASELINE_TAG = "official-vego-ai-baseline"
EXPECTED_BASELINE_COMMIT = "2eeccb1cbb2d01faa3e8ceb43466a52e0fee23cf"
EXPECTED_FROZEN_COUNTS = {
    "ranked_rows": 179,
    "per_case_reports": 165,
    "duplicate_ranked_rows": 14,
    "distinct_case_ids": 83,
    "variability_patterns": 27,
}
EXP005_LABEL_FIELDS = ("expert_label", "reviewer_2_label", "adjudicated_label")


class AuditError(RuntimeError):
    """Raised when a protected evidence invariant cannot be verified."""


def _read_json(path: pathlib.Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def _read_jsonl(path: pathlib.Path) -> list[dict[str, Any]]:
    if not path.is_file():
        return []
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8-sig").splitlines()
        if line.strip()
    ]


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _sha256_file(path: pathlib.Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _zip_members(data: bytes) -> dict[str, bytes] | None:
    try:
        with zipfile.ZipFile(io.BytesIO(data)) as archive:
            return {
                name: archive.read(name)
                for name in sorted(archive.namelist())
                if not name.endswith("/")
            }
    except (zipfile.BadZipFile, OSError):
        return None


def canonical_content_equal(left: bytes, right: bytes) -> bool:
    """Compare content while tolerating checkout-only line-ending changes."""
    if left == right:
        return True
    try:
        return json.loads(left.decode("utf-8-sig")) == json.loads(right.decode("utf-8-sig"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        pass
    left_zip, right_zip = _zip_members(left), _zip_members(right)
    if left_zip is not None or right_zip is not None:
        if left_zip is None or right_zip is None or left_zip.keys() != right_zip.keys():
            return False
        return all(
            left_zip[name].replace(b"\r\n", b"\n") == right_zip[name].replace(b"\r\n", b"\n")
            for name in left_zip
        )
    return left.replace(b"\r\n", b"\n") == right.replace(b"\r\n", b"\n")


def canonical_content_digest(data: bytes) -> str:
    """Return a checkout-stable digest for JSON, ZIP containers, or text/binary."""
    try:
        canonical = json.dumps(
            json.loads(data.decode("utf-8-sig")),
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
        return _sha256_bytes(canonical)
    except (UnicodeDecodeError, json.JSONDecodeError):
        pass
    members = _zip_members(data)
    if members is not None:
        digest = hashlib.sha256()
        for name, content in members.items():
            digest.update(name.encode("utf-8"))
            digest.update(b"\0")
            digest.update(content.replace(b"\r\n", b"\n"))
        return digest.hexdigest()
    return _sha256_bytes(data.replace(b"\r\n", b"\n"))


def count_nonblank_csv_fields(path: pathlib.Path, fields: Iterable[str]) -> dict[str, int]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    return {field: sum(bool(str(row.get(field, "")).strip()) for row in rows) for field in fields}


def _csv_row_count(path: pathlib.Path) -> int:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return sum(1 for _ in csv.DictReader(handle))


def _git(repo: pathlib.Path, *args: str, binary: bool = False) -> str | bytes:
    return (
        subprocess.check_output(
            ["git", *args], cwd=repo, text=not binary, stderr=subprocess.STDOUT
        ).strip()
        if not binary
        else subprocess.check_output(["git", *args], cwd=repo, stderr=subprocess.STDOUT)
    )


def _relative(repo: pathlib.Path, path: pathlib.Path) -> str:
    return path.resolve().relative_to(repo.resolve()).as_posix()


def _tree_receipt(repo: pathlib.Path, paths: Iterable[pathlib.Path]) -> dict[str, Any]:
    files = sorted({p.resolve() for p in paths if p.is_file()}, key=lambda p: _relative(repo, p))
    digest = hashlib.sha256()
    for path in files:
        rel = _relative(repo, path)
        digest.update(rel.encode("utf-8"))
        digest.update(b"\0")
        digest.update(bytes.fromhex(canonical_content_digest(path.read_bytes())))
    return {"file_count": len(files), "tree_sha256": digest.hexdigest() if files else None}


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise AuditError(message)


def _variability_path(setting_root: pathlib.Path) -> pathlib.Path:
    matches = sorted(setting_root.glob("agentD_variability_classes*.json"))
    _require(
        len(matches) == 1,
        f"expected exactly one Agent 4 variability file in {setting_root}, found {len(matches)}",
    )
    return matches[0]


def _baseline_integrity(repo: pathlib.Path, vego: pathlib.Path) -> dict[str, Any]:
    commit = str(_git(repo, "rev-list", "-n", "1", OFFICIAL_BASELINE_TAG))
    _require(
        commit == EXPECTED_BASELINE_COMMIT, f"unexpected {OFFICIAL_BASELINE_TAG} target: {commit}"
    )
    names = str(
        _git(
            repo,
            "ls-tree",
            "-r",
            "--name-only",
            OFFICIAL_BASELINE_TAG,
            "--",
            "analysis",
            "eval_output",
        )
    ).splitlines()
    _require(bool(names), "official baseline tag contains no analysis/eval_output artifacts")
    equivalent = 0
    raw_identical = 0
    for tagged_path in names:
        local = vego / tagged_path
        _require(local.is_file(), f"missing frozen baseline artifact: VEGO-AI/{tagged_path}")
        tagged = _git(repo, "show", f"{OFFICIAL_BASELINE_TAG}:{tagged_path}", binary=True)
        current = local.read_bytes()
        if tagged == current:
            raw_identical += 1
        _require(
            canonical_content_equal(tagged, current),
            f"baseline content drift: VEGO-AI/{tagged_path}",
        )
        equivalent += 1
    return {
        "official_tag": OFFICIAL_BASELINE_TAG,
        "official_commit": commit,
        "checked_files": len(names),
        "content_equivalent_files": equivalent,
        "byte_identical_files": raw_identical,
        "normalization_note": "JSON structure and XLSX archive members are compared after checkout-only CRLF normalization; no semantic differences were found.",
    }


def _frozen_counts(
    vego: pathlib.Path,
) -> tuple[dict[str, Any], collections.Counter[str], collections.Counter[str]]:
    ranked_rows = 0
    report_count = 0
    all_case_ids: set[str] = set()
    duplicate_rows = 0
    compliance = collections.Counter()
    fragment_labels = collections.Counter()
    per_setting: dict[str, Any] = {}
    patterns = 0

    for setting in SETTINGS:
        root = vego / "eval_output" / setting
        scores = _read_json(root / "agentC_all_scores.json")["ranking"]
        ids = [str(row["case_id"]) for row in scores]
        id_counts = collections.Counter(ids)
        reports = sorted(root.glob("agentC_case_*.json"))
        classes = _read_json(_variability_path(root))["variability_classifications"]

        ranked_rows += len(scores)
        report_count += len(reports)
        all_case_ids.update(ids)
        duplicate_rows += sum(count - 1 for count in id_counts.values())
        patterns += len(classes)

        for path in reports:
            case = _read_json(path)
            compliance.update(
                str(item.get("compliance_status")) for item in case.get("existing_mapping", [])
            )
            fragment_labels.update(
                str(item.get("label")) for item in case.get("uncovered_fragments", [])
            )

        per_setting[setting] = {
            "ranked_rows": len(scores),
            "unique_ranked_case_ids": len(id_counts),
            "per_case_reports": len(reports),
            "duplicate_case_ids": sorted(
                case_id for case_id, count in id_counts.items() if count > 1
            ),
            "variability_patterns": len(classes),
        }

    result = {
        "ranked_rows": ranked_rows,
        "per_case_reports": report_count,
        "duplicate_ranked_rows": duplicate_rows,
        "distinct_case_ids": len(all_case_ids),
        "variability_patterns": patterns,
        "per_setting": per_setting,
        "reconciliation": "179 ranking rows include 14 duplicate rows within settings, yielding 165 unique setting-case reports; 83 is the cross-setting distinct student/case-ID count.",
        "paper_snapshot": {
            "ranked_models": 178,
            "patterns": 26,
            "source": "docs/research/bigui/paper-baseline-snapshot-v1.json",
            "boundary": "A separate paper-reported snapshot, not an improvement baseline; the current frozen repository has 179/27.",
        },
    }
    for name, expected in EXPECTED_FROZEN_COUNTS.items():
        _require(
            result[name] == expected, f"frozen count drift for {name}: {result[name]} != {expected}"
        )
    _require(sum(compliance.values()) == 4853, "unexpected Agent 3 compliance-item total")
    _require(sum(fragment_labels.values()) == 607, "unexpected Agent 3 uncovered-fragment total")
    return result, compliance, fragment_labels


def _agent4_ground_truth_check(repo: pathlib.Path, vego: pathlib.Path) -> dict[str, Any]:
    pairs = []
    covered = 0
    for setting in SETTINGS:
        analysis = vego / "analysis" / f"agentD_variability_classes_{setting}.json"
        output = _variability_path(vego / "eval_output" / setting)
        _require(analysis.is_file() and output.is_file(), f"Agent 4 pair absent for {setting}")
        left, right = _sha256_file(analysis), _sha256_file(output)
        _require(left == right, f"Agent 4 analysis/eval_output hash mismatch for {setting}")
        count = len(_read_json(analysis)["variability_classifications"])
        covered += count
        pairs.append(
            {
                "setting": setting,
                "analysis_path": _relative(repo, analysis),
                "eval_output_path": _relative(repo, output),
                "sha256": left,
                "pattern_count": count,
                "byte_identical": True,
            }
        )
    _require(covered == 27, f"Agent 4 pair coverage drift: {covered}")
    return {
        "byte_identical_pairs": len(pairs),
        "patterns_covered": covered,
        "independent_ground_truth": False,
        "finding": "The analysis files are byte-identical copies of Agent 4 outputs; they demonstrate agreement/copy integrity, not independent labels.",
        "pairs": pairs,
    }


def _human_layer(repo: pathlib.Path, vego: pathlib.Path) -> dict[str, Any]:
    run = vego / "runs" / "20260614-122150" / "human"
    queues: list[dict[str, Any]] = []
    resolved: list[dict[str, Any]] = []
    memory: list[dict[str, Any]] = []
    advice: list[dict[str, Any]] = []
    comparisons: list[dict[str, Any]] = []
    for setting in SETTINGS:
        root = run / setting
        queues.extend(_read_jsonl(root / "human_review_queue.jsonl"))
        resolved.extend(_read_jsonl(root / "human_review_queue_resolved.jsonl"))
        memory.extend(_read_jsonl(root / "human_judgment_memory.jsonl"))
        advice_path = root / "memory_advice.json"
        comparison_path = root / "memory_informed_comparison.json"
        if advice_path.is_file():
            advice.extend(_read_json(advice_path).get("advice", []))
        if comparison_path.is_file():
            comparisons.extend(_read_json(comparison_path).get("comparisons", []))

    facts = {
        "M1_queue_items": len(queues),
        "M1_2_signed_queue_items": sum(
            bool(item.get("review_id") and item.get("review_signature")) for item in queues
        ),
        "M2_resolved_feedback_records": len(resolved),
        "M3_memory_items": len(memory),
        "M4A_advice_rows": len(advice),
        "M4A_ai_classification_changes": sum(
            bool(item.get("ai_classification_changed")) for item in advice
        ),
        "M4A_memory_conflicts": sum(bool(item.get("has_conflicting_memory")) for item in advice),
        "M4B1_comparison_rows": len(comparisons),
        "M4B1_classification_differences": sum(
            bool(item.get("memory_informed_differs_from_original")) for item in comparisons
        ),
        "M4B1_review_after_memory": sum(
            bool(item.get("requires_human_review_after_memory")) for item in comparisons
        ),
    }
    expected = {
        "M1_queue_items": 11,
        "M1_2_signed_queue_items": 11,
        "M2_resolved_feedback_records": 4,
        "M3_memory_items": 3,
        "M4A_advice_rows": 27,
        "M4A_ai_classification_changes": 0,
        "M4A_memory_conflicts": 0,
        "M4B1_comparison_rows": 27,
        "M4B1_classification_differences": 0,
        "M4B1_review_after_memory": 2,
    }
    _require(facts == expected, f"human-layer evidence drift: {facts!r}")

    milestone_files = {
        "M1": (
            "VEGO-AI/framework/human_review_queue.py",
            "VEGO-AI/tests/test_human_review_queue.py",
        ),
        "M1.2": (
            "VEGO-AI/schemas/human_review_item.schema.json",
            "VEGO-AI/framework/human_review_queue.py",
        ),
        "M2": (
            "VEGO-AI/framework/human_feedback_manager.py",
            "VEGO-AI/tests/test_human_feedback_manager.py",
        ),
        "M3": (
            "VEGO-AI/framework/human_judgment_memory.py",
            "VEGO-AI/tests/test_human_judgment_memory.py",
        ),
        "M4A": ("VEGO-AI/framework/memory_advisor.py", "VEGO-AI/tests/test_memory_advisor.py"),
        "M4B-1": (
            "VEGO-AI/framework/memory_informed_classifier.py",
            "VEGO-AI/tests/test_memory_informed_classifier.py",
        ),
    }
    for milestone, paths in milestone_files.items():
        _require(
            all((repo / path).is_file() for path in paths),
            f"{milestone} implementation/test evidence missing",
        )
    return {
        "status": "verified_implemented_through_M4B-1",
        "facts": facts,
        "milestone_files": {name: list(paths) for name, paths in milestone_files.items()},
        "boundary": "M4A is advisory; M4B-1 is deterministic and non-destructive. Zero classification differences is mechanism evidence, not effectiveness evidence.",
    }


def _exp005_gate(repo: pathlib.Path) -> dict[str, Any]:
    generated = repo / "reports" / "generated"
    exp005 = generated / "exp005_label_review"
    package = generated / "exp003" / "annotation_package"
    summary = _read_json(exp005 / "label_validation_summary.json")
    full = exp005 / "exp005_label_review_full.csv"
    reviewer1 = package / "blind_sheet_reviewer1.csv"
    reviewer2 = package / "blind_sheet_reviewer2.csv"
    adjudication = exp005 / "exp005_adjudication_sheet.csv"
    gold = package / "gold_labels.csv"
    sealed = package / "item_mapping_PRIVATE.csv"
    for path in (full, reviewer1, reviewer2, adjudication, gold, sealed):
        _require(path.is_file(), f"EXP-005 gate artifact missing: {_relative(repo, path)}")

    reviewer1_counts = count_nonblank_csv_fields(reviewer1, ("expert_label",))
    reviewer2_counts = count_nonblank_csv_fields(reviewer2, ("expert_label",))
    adjudication_counts = count_nonblank_csv_fields(adjudication, EXP005_LABEL_FIELDS)
    result = {
        "rows": _csv_row_count(full),
        "generalization_safe_candidates": int(summary["generalization_safe_candidate_count"]),
        "labels_supplied": int(summary["labels_supplied_count"]),
        "valid_labels": int(summary["valid_label_count"]),
        "generalization_safe_valid_labels": int(summary["generalization_safe_valid_label_count"]),
        "same_pattern_valid_labels": int(summary["same_pattern_valid_label_count"]),
        "reviewer_1_labels": reviewer1_counts["expert_label"],
        "reviewer_2_labels": reviewer2_counts["expert_label"],
        "adjudicated_labels": adjudication_counts["adjudicated_label"],
        "gold_label_rows": _csv_row_count(gold),
        "holdout_status": "sealed_not_evaluated",
        "sealed_mapping": {
            "path": _relative(repo, sealed),
            "sha256": _sha256_file(sealed),
            "content_opened_by_verifier": False,
        },
        "strict_gate": summary["strict_gate"],
    }
    expected_zero = (
        "labels_supplied",
        "valid_labels",
        "generalization_safe_valid_labels",
        "same_pattern_valid_labels",
        "reviewer_1_labels",
        "reviewer_2_labels",
        "adjudicated_labels",
        "gold_label_rows",
    )
    _require(
        result["rows"] == 27 and result["generalization_safe_candidates"] == 24,
        "EXP-005 row/safe-candidate drift",
    )
    _require(
        all(result[key] == 0 for key in expected_zero),
        f"EXP-005 is no longer at the documented 0/24 gate: {result!r}",
    )
    _require(
        not result["strict_gate"]["quantitative_evaluation_allowed"],
        "EXP-005 gate unexpectedly permits quantitative evaluation",
    )
    return result


def _triggers(
    vego: pathlib.Path,
    compliance: collections.Counter[str],
    fragments: collections.Counter[str],
    human: dict[str, Any],
) -> dict[str, Any]:
    missed = 0
    open_questions = 0
    confidence = collections.Counter()
    for setting in SETTINGS:
        root = vego / "eval_output" / setting
        metrics = _read_json(root / "agentB_metrics.json")
        missed += len(metrics.get("unassigned_base_guidelines", []))
        best = _read_json(root / "agentB_best_guidelines.json")
        open_questions += len(best.get("questions_to_language_advisor", []))
        classes = _read_json(_variability_path(root))["variability_classifications"]
        confidence.update(str(row.get("confidence")) for row in classes)
    low_medium = confidence["Low"] + confidence["Medium"]
    result = {
        "missing guideline": {
            "status": "DERIVABLE",
            "origin": "original Agent 2 evaluator/reference comparison",
            "count": missed,
            "automatic": True,
        },
        "Alternative": {
            "status": "IMPLEMENTED",
            "origin": "original Agent 3 uncovered-fragment label",
            "count": fragments["Alternative"],
            "automatic": True,
        },
        "Domain Mistake": {
            "status": "IMPLEMENTED",
            "origin": "original Agent 3 uncovered-fragment label",
            "count": fragments["Domain Mistake"],
            "automatic": True,
        },
        "Language Mistake": {
            "status": "IMPLEMENTED",
            "origin": "original Agent 3 uncovered-fragment label",
            "count": fragments["Language Mistake"],
            "automatic": True,
        },
        "Not-Satisfied": {
            "status": "IMPLEMENTED",
            "origin": "original Agent 3 compliance status",
            "count": compliance["Not-Satisfied"],
            "automatic": True,
        },
        "Partially-Satisfied": {
            "status": "IMPLEMENTED",
            "origin": "original Agent 3 compliance status",
            "count": compliance["Partially-Satisfied"],
            "automatic": True,
        },
        "open question": {
            "status": "IMPLEMENTED",
            "origin": "original Agent 2 questions_to_language_advisor",
            "count": open_questions,
            "automatic": True,
        },
        "low/medium confidence": {
            "status": "IMPLEMENTED",
            "origin": "original Agent 4 confidence field",
            "count": low_medium,
            "automatic": True,
            "distribution": dict(confidence),
        },
        "cross-agent disagreement": {
            "status": "PROPOSED ONLY",
            "origin": "doctoral signal contract; unavailable in the frozen baseline",
            "count": None,
            "automatic": False,
        },
        "novelty": {
            "status": "PROPOSED ONLY",
            "origin": "doctoral signal contract; unavailable in the frozen baseline",
            "count": None,
            "automatic": False,
        },
        "memory disagreement/conflict": {
            "status": "IMPLEMENTED",
            "origin": "M4A/M4B-1 extension",
            "count": human["facts"]["M4A_memory_conflicts"],
            "automatic": True,
        },
    }
    expected = {
        "missing guideline": 59,
        "Alternative": 491,
        "Domain Mistake": 79,
        "Language Mistake": 37,
        "Not-Satisfied": 496,
        "Partially-Satisfied": 743,
        "open question": 12,
        "low/medium confidence": 3,
        "memory disagreement/conflict": 0,
    }
    for key, value in expected.items():
        _require(
            result[key]["count"] == value,
            f"trigger count drift for {key}: {result[key]['count']} != {value}",
        )
    return result


def _pilot_candidates(repo: pathlib.Path, vego: pathlib.Path) -> dict[str, Any]:
    mapping_path = vego / "eval_output" / "ucd_ch" / "agentB_guideline_mapping.json"
    clusters = _read_json(mapping_path)["clusters"]
    c1 = next((row for row in clusters if row.get("cluster_id") == "C1"), None)
    _require(
        c1 is not None and c1.get("base_assignment") is None,
        "C1 domain-guideline candidate no longer matches",
    )

    c3_path: pathlib.Path | None = None
    c3: dict[str, Any] | None = None
    alternatives: list[tuple[int, dict[str, Any]]] = []
    for setting in SETTINGS:
        for candidate_path in sorted((vego / "eval_output" / setting).glob("agentC_case_*.json")):
            candidate = _read_json(candidate_path)
            found = [
                (index, row)
                for index, row in enumerate(candidate.get("uncovered_fragments", []))
                if row.get("label") == "Alternative"
            ]
            if found:
                c3_path, c3, alternatives = candidate_path, candidate, found
                break
        if c3_path is not None:
            break
    _require(
        c3_path is not None and c3 is not None and bool(alternatives),
        "C3 uncovered-fragment candidate not found",
    )

    queue_path = vego / "human_review_output" / "cd_ch" / "human_review_queue.jsonl"
    c4 = next(
        (row for row in _read_jsonl(queue_path) if row.get("review_id") == "HRQ-cd_ch-P2"), None
    )
    _require(c4 is not None, "C4 Agent 4 queue candidate no longer exists")

    return {
        "C1": {
            "status": "FOUND",
            "stage": "Agent 2 domain advisor / guideline coverage",
            "identifier": "ucd_ch:AgentB:C1",
            "path": _relative(repo, mapping_path),
            "signal": "domain_cluster_no_base_match+low_mapping_certainty",
            "minimum_mapping_certainty": min(
                c1[f"run{i}_guideline"]["mapping_certainty"] for i in (1, 2, 3)
            ),
            "independent_outcome": False,
        },
        "C2": {
            "status": "NOT FOUND",
            "stage": "Agent 3 compliance disagreement",
            "path": "experiments/EXP-046-recorded-review-analysis/README.md",
            "reason": "Only aggregate recorded-review evidence is tracked; source workbooks with row identifiers remain outside the repository.",
            "independent_outcome": False,
        },
        "C3": {
            "status": "FOUND",
            "stage": "Agent 3 uncovered fragment",
            "identifier": f"{c3_path.parent.name}:case:{c3['case_id']}:uncovered_index:{alternatives[0][0]}",
            "path": _relative(repo, c3_path),
            "case_id": str(c3["case_id"]),
            "source_sha256": _sha256_file(c3_path),
            "recorded_label": alternatives[0][1]["label"],
            "independent_outcome": False,
        },
        "C4": {
            "status": "FOUND",
            "stage": "Agent 4 variability classification",
            "identifier": "cd_ch:pattern:P2",
            "path": _relative(repo, queue_path),
            "review_id": str(c4["review_id"]),
            "trigger_reasons": c4["trigger_reasons"],
            "affected_case_count": len(c4.get("affected_cases", [])),
            "independent_outcome": False,
        },
    }


def _replay_feasibility() -> dict[str, Any]:
    return {
        "C1_missing_guideline": {
            "without_llm": False,
            "state": "BLOCKED",
            "reason": "A new guideline requires semantic mapping/scoring; no approved bounded deterministic injection path exists.",
        },
        "C2_compliance_correction": {
            "without_llm": "PARTIAL",
            "state": "DERIVABLE",
            "reason": "Stored contribution arithmetic and aggregation are deterministic, but exact row-level human evidence and a bounded correction adapter are absent.",
        },
        "C3_fragment_relabel": {
            "without_llm": "PARTIAL",
            "state": "DERIVABLE",
            "reason": "Contribution arithmetic can be recomputed from stored records, but no approved human-relabel replay adapter exists.",
        },
        "C4_pattern_correction": {
            "without_llm": True,
            "state": "IMPLEMENTED",
            "reason": "M1-M4B-1 can capture feedback, retrieve memory, and emit a deterministic non-destructive comparison; it cannot establish benefit without independent labels.",
        },
        "prohibited": "Do not rerun Agent 1-4, call an LLM/API, overwrite baseline outputs, or treat a replay as an outcome evaluation.",
    }


def _experiment_registry(repo: pathlib.Path) -> dict[str, Any]:
    registry_path = repo / "experiments" / "registry.md"
    ids = re.findall(
        r"^\| (EXP-\d{3}) \|", registry_path.read_text(encoding="utf-8-sig"), re.MULTILINE
    )
    expected = [f"EXP-{i:03d}" for i in range(47)]
    _require(
        ids == expected, "experiment registry is not a unique contiguous EXP-000..EXP-046 sequence"
    )
    current = _read_json(repo / "experiments" / "current-run-index-v1.json")["currentRuns"]
    accepted = sorted((repo / "experiments" / "accepted-runs").glob("*.json"))
    return {
        "registry_path": "experiments/registry.md",
        "registered_count": len(ids),
        "registered_range": [ids[0], ids[-1]],
        "current_run_index_count": len(current),
        "accepted_manifest_count": len(accepted),
        "note": "Registration is not evidence that every experiment is complete; status and claim boundaries remain authoritative per row.",
    }


def _evidence_map(repo: pathlib.Path, vego: pathlib.Path) -> list[dict[str, Any]]:
    run = vego / "runs" / "20260614-122150" / "human"
    specs = [
        (
            "Agent 1 outputs",
            "VEGO-AI/eval_output/*/agentA_*",
            "original baseline",
            [p for p in (vego / "eval_output").glob("*/agentA_*")],
        ),
        (
            "Agent 2 outputs",
            "VEGO-AI/eval_output/*/agentB_*",
            "original baseline",
            [p for p in (vego / "eval_output").glob("*/agentB_*")],
        ),
        (
            "Agent 3 outputs",
            "VEGO-AI/eval_output/*/agentC_*",
            "original baseline",
            [p for p in (vego / "eval_output").glob("*/agentC_*")],
        ),
        (
            "Agent 4 outputs",
            "VEGO-AI/eval_output/*/agentD_*",
            "original baseline",
            [p for p in (vego / "eval_output").glob("*/agentD_*")],
        ),
        (
            "Human-review queue",
            "VEGO-AI/runs/20260614-122150/human/*/human_review_queue.jsonl",
            "doctoral extension M1/M1.2",
            list(run.glob("*/human_review_queue.jsonl")),
        ),
        (
            "Structured feedback",
            "VEGO-AI/runs/20260614-122150/human/*/human_review_queue_resolved.jsonl",
            "doctoral extension M2",
            list(run.glob("*/human_review_queue_resolved.jsonl")),
        ),
        (
            "Human Judgment Memory",
            "VEGO-AI/runs/20260614-122150/human/*/human_judgment_memory.jsonl",
            "doctoral extension M3",
            list(run.glob("*/human_judgment_memory.jsonl")),
        ),
        (
            "Memory advice",
            "VEGO-AI/runs/20260614-122150/human/*/memory_advice.json",
            "doctoral extension M4A",
            list(run.glob("*/memory_advice.json")),
        ),
        (
            "Memory-informed comparison",
            "VEGO-AI/runs/20260614-122150/human/*/memory_informed_comparison.json",
            "doctoral extension M4B-1",
            list(run.glob("*/memory_informed_comparison.json")),
        ),
        (
            "Expert annotation package",
            "reports/generated/exp003/annotation_package/*",
            "evaluation package; ignored/private boundary",
            list((repo / "reports" / "generated" / "exp003" / "annotation_package").glob("*")),
        ),
        (
            "EXP-005 gate",
            "reports/generated/exp005_label_review/*",
            "evaluation gate; ignored/private boundary",
            list((repo / "reports" / "generated" / "exp005_label_review").glob("*")),
        ),
    ]
    rows = []
    for source, path, layer, paths in specs:
        receipt = _tree_receipt(repo, paths)
        rows.append(
            {
                "source": source,
                "path": path,
                "type": "artifact set",
                "layer": layer,
                "verified": receipt["file_count"] > 0,
                **receipt,
                "note": "Hash receipt only for private/ignored sets; no raw content is copied into tracked documentation.",
            }
        )
    _require(
        all(row["verified"] for row in rows), "one or more evidence-map artifact sets are missing"
    )
    return rows


def audit(repo_root: pathlib.Path, vego_root: pathlib.Path) -> dict[str, Any]:
    repo, vego = repo_root.resolve(), vego_root.resolve()
    _require((repo / ".git").exists(), f"not a Git working copy: {repo}")
    _require(vego.is_dir(), f"VEGO-AI root not found: {vego}")
    head = str(_git(repo, "rev-parse", "HEAD"))
    branch = str(_git(repo, "branch", "--show-current"))
    _require(branch == "main", f"audit must run on main, found {branch!r}")

    baseline = _baseline_integrity(repo, vego)
    frozen, compliance, fragments = _frozen_counts(vego)
    ground_truth = _agent4_ground_truth_check(repo, vego)
    human = _human_layer(repo, vego)
    gate = _exp005_gate(repo)
    triggers = _triggers(vego, compliance, fragments, human)
    candidates = _pilot_candidates(repo, vego)

    return {
        "schema_version": "IrisPreliminaryPilotEvidenceAudit-v1",
        "status": "PASS",
        "read_only": True,
        "repository": {"branch": branch, "head": head},
        "claim_boundary": "descriptive_mechanism_evidence_only",
        "baseline_integrity": baseline,
        "doctoral_extension": human,
        "experiment_registry": _experiment_registry(repo),
        "frozen_run_counts": frozen,
        "agent4_ground_truth_check": ground_truth,
        "exp005_gate": gate,
        "trigger_inventory": triggers,
        "pilot_candidates": candidates,
        "replay_feasibility": _replay_feasibility(),
        "evidence_map": _evidence_map(repo, vego),
        "must_not_be_claimed": [
            "Agent 4 accuracy, human benefit, policy superiority, or generalization",
            "analysis/ as independent ground truth",
            "178/26 and 179/27 as interchangeable denominators",
            "same-pattern memory as held-out evidence",
            "an exact C2 row-level pilot case from repository-only evidence",
        ],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--repo-root", type=pathlib.Path, default=pathlib.Path(__file__).resolve().parents[1]
    )
    parser.add_argument("--vego-root", type=pathlib.Path)
    args = parser.parse_args(argv)
    repo = args.repo_root.resolve()
    vego = args.vego_root.resolve() if args.vego_root else repo / "VEGO-AI"
    try:
        report = audit(repo, vego)
        print(json.dumps(report, indent=2, ensure_ascii=False, sort_keys=True))
        return 0
    except (
        AuditError,
        KeyError,
        ValueError,
        OSError,
        subprocess.CalledProcessError,
        json.JSONDecodeError,
    ) as exc:
        print(
            json.dumps(
                {
                    "schema_version": "IrisPreliminaryPilotEvidenceAudit-v1",
                    "status": "FAIL",
                    "read_only": True,
                    "error": str(exc),
                },
                indent=2,
                ensure_ascii=False,
                sort_keys=True,
            )
        )
        return 1


if __name__ == "__main__":
    sys.exit(main())
