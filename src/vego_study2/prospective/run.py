"""Command-line entry point: gates, preflight, one-time execution, aggregate, validate.

Every command loads the frozen manifest first and fails closed on any gate.
Absolute private paths never enter a JSON document; the private root is
referred to by the placeholder token from :mod:`constants`.
"""

from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

from vego_study2.paths import UnsafeOutputPathError, ensure_safe_output_root

from . import constants as c
from .aggregate import assert_redacted, build_public_aggregate, validate_public
from .budget import SharedBudgetGuard, per_request_reserve_usd
from .contract import canonical_sha256
from .inventory import (
    InventoryError,
    build_case_selection,
    build_eligible_inventory,
    load_case_inputs,
)
from .manifest import (
    DOCS_DIR,
    ROOT,
    ManifestError,
    command_fingerprint,
    environment_fingerprint,
    file_sha256,
    git_head,
    git_is_clean,
    load_manifest,
)
from .off_runner import OffIsolationError, assert_off_isolation, run_off
from .provider import CallLedger, build_client, credential_present, restrict_egress, utc_now

CLAIM_BOUNDARY = [
    "Prospective exploratory paired comparison of two system workflows on one public LLM-generated corpus.",
    "No claim of system superiority, human benefit, alert correctness, accuracy, recall, precision, F1, causality, representativeness or generalisation.",
    "Detector-v1 output is a reporting-only candidate-for-human-review label with no human labels behind it.",
    "Detector-v1 is NOT_APPLICABLE under VEGO_AI_OFF because no inter-agent episodes exist there; that is not zero alerts.",
    "Human assessment outcomes are NOT_MEASURED until two independent raters score the blinded cards.",
]


class GateFailure(RuntimeError):
    pass


class Lifecycle:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.records: list[dict[str, Any]] = []

    def __call__(self, *, stage: str, state: str, condition: str | None = None, case_id: str | None = None,
                 detail: Any = None) -> None:
        record = {"timestamp": utc_now(), "stage": stage, "state": state, "condition": condition,
                  "case_id": case_id, "detail": None if detail is None else str(detail)[:160]}
        self.records.append(record)
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, sort_keys=True, ensure_ascii=False) + "\n")

    def summary(self) -> dict[str, Any]:
        counts: dict[str, int] = {}
        for record in self.records:
            key = f"{record['stage']}:{record['condition'] or '-'}:{record['state']}"
            counts[key] = counts.get(key, 0) + 1
        return {"records": len(self.records), "counts": dict(sorted(counts.items()))}


def _gate(gates: dict[str, Any], name: str, passed: bool, detail: str = "") -> None:
    gates[name] = {"passed": bool(passed), "detail": detail}
    if not passed:
        raise GateFailure(f"{name}: {detail}")


def run_gates(manifest: dict[str, Any], private_root: Path, output_root: Path, *, live: bool,
              expected_head: str | None) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    gates: dict[str, Any] = {}
    _gate(gates, "manifest_loaded_and_self_bound", True, manifest["manifest_sha256"][:16])
    head = git_head()
    if live:
        _gate(gates, "expected_head_supplied", bool(expected_head), "live execution requires --expected-head")
        _gate(gates, "git_head_matches_expected", head == expected_head, f"HEAD {head[:12]}")
        _gate(gates, "working_tree_clean", git_is_clean(), "tracked files must be unmodified")
    else:
        gates["git_head_recorded"] = {"passed": True, "detail": head[:12]}
    runtime_root = private_root / "fullframe_runtime"
    _gate(gates, "private_runtime_root_present", runtime_root.is_dir(), "fullframe_runtime under the private root")
    try:
        inventory = build_eligible_inventory(runtime_root, verify_bytes=True)
    except InventoryError as exc:
        _gate(gates, "eligible_inventory_verified", False, str(exc))
    _gate(gates, "eligible_inventory_verified",
          inventory["eligible_case_count"] == manifest["case_selection"]["eligible_case_count"],
          f"{inventory['eligible_case_count']} eligible cases, every digest re-verified")
    selection = build_case_selection(inventory, manifest["case_selection"]["sample_size"], manifest["case_selection"]["seed"])
    _gate(gates, "selection_reproduced_from_seed",
          selection["selected_case_ids"] == manifest["case_selection"]["selected_case_ids"],
          ",".join(selection["selected_case_ids"]))
    frozen_selection = json.loads((ROOT / manifest["case_selection"]["path"]).read_text(encoding="utf-8"))
    _gate(gates, "frozen_selection_document_matches",
          frozen_selection["selected_case_ids"] == selection["selected_case_ids"]
          and {r["case_id"]: r["sha256"] for r in frozen_selection["selected_cases"]} == manifest["corpus_hashes"]["cases"],
          "case ids and digests agree")
    try:
        inputs = load_case_inputs(runtime_root, selection)
    except InventoryError as exc:
        _gate(gates, "corpus_hashes_verified_at_load", False, str(exc))
    _gate(gates, "corpus_hashes_verified_at_load",
          inputs["case_input_hashes"] == manifest["corpus_hashes"]["cases"]
          and inputs["domain_description_sha256"] == manifest["corpus_hashes"]["domain_description"],
          "domain description and every selected case match the frozen digests")
    try:
        ensure_safe_output_root(output_root, private_root / "study2-prospective")
        safe = True
        detail = "absolute, inside the private root, no symlink or reparse point"
    except UnsafeOutputPathError as exc:
        safe, detail = False, str(exc)
    _gate(gates, "output_root_safe", safe, detail)
    _gate(gates, "output_root_fresh", not output_root.exists(), "output root must not exist yet")
    caps = manifest["caps"]
    reservation = (caps[c.CONDITION_ON] + caps[c.CONDITION_OFF]) * per_request_reserve_usd()
    _gate(gates, "whole_study_reservation_within_guard", reservation <= manifest["budget"]["guard_ceiling_usd"] + 1e-9,
          f"{caps[c.CONDITION_ON] + caps[c.CONDITION_OFF]} requests x {per_request_reserve_usd():.7f} = {reservation:.4f} USD")
    _gate(gates, "minimum_paired_cases", len(selection["selected_case_ids"]) >= c.MIN_PAIRED_CASES,
          f"{len(selection['selected_case_ids'])} paired cases")
    if live:
        _gate(gates, "credential_present_value_unread", credential_present(),
              f"{c.CREDENTIAL_ENV} present in process environment, value never read by the harness")
    else:
        gates["credential_not_required"] = {"passed": True, "detail": "fake provider, no credential path"}
    try:
        assert_off_isolation("gates")
        _gate(gates, "off_isolation_before_start", True, "no orchestration, Q&A, detector or queue module loaded")
    except OffIsolationError as exc:
        _gate(gates, "off_isolation_before_start", False, str(exc))
    _gate(gates, "frozen_model_and_host", manifest["provider"]["model"] == c.MODEL
          and manifest["provider"]["allowed_hosts"] == sorted(c.ALLOWED_HOSTS), f"{c.MODEL} via {sorted(c.ALLOWED_HOSTS)}")
    return gates, inputs, selection


def _corpus_fragments(inputs: dict[str, Any]) -> list[str]:
    fragments: list[str] = []
    texts = [inputs["domain_description"], *(case["case_model"] for case in inputs["case_models"])]
    for text in texts:
        for line in text.splitlines():
            line = line.strip()
            if len(line) >= 24:
                fragments.append(line[:40])
    return fragments


def _output_manifest(output_root: Path, *, exclude: set[str]) -> dict[str, Any]:
    files = {}
    for path in sorted(output_root.rglob("*")):
        if path.is_file() and path.name not in exclude:
            files[path.relative_to(output_root).as_posix()] = {
                "sha256": file_sha256(path), "bytes": path.stat().st_size,
            }
    return {"schema_version": "study2-prospective-output-manifest-v1", "files": files, "file_count": len(files)}


async def execute(args: argparse.Namespace, *, live: bool) -> dict[str, Any]:
    manifest = load_manifest()
    private_root = Path(args.private_root).resolve()
    stamp = utc_now().replace("-", "").replace(":", "")[:15]
    run_id = args.run_id or f"S2P-{'LIVE' if live else 'PREFLIGHT'}-{stamp}"
    output_root = (private_root / "study2-prospective" / run_id).resolve()
    mode = "LIVE" if live else "PREFLIGHT_FAKE_PROVIDER"
    fake_mode = None if live else args.fake_mode
    public_argv = [a.replace(str(private_root), c.PRIVATE_ROOT_TOKEN) for a in args.argv_for_fingerprint]
    gates, inputs, selection = run_gates(manifest, private_root, output_root, live=live, expected_head=args.expected_head)
    output_root.mkdir(parents=True, exist_ok=False)
    lifecycle = Lifecycle(output_root / "lifecycle.jsonl")
    ledger = CallLedger(output_root / "call-ledger.jsonl")
    caps = manifest["caps"]
    guard = SharedBudgetGuard(
        guard_ceiling_usd=manifest["budget"]["guard_ceiling_usd"],
        total_request_cap=caps["total_requests"],
        condition_request_caps={c.CONDITION_ON: caps[c.CONDITION_ON], c.CONDITION_OFF: caps[c.CONDITION_OFF]},
    )
    egress = restrict_egress(frozenset(manifest["provider"]["allowed_hosts"]) if live else frozenset())
    fake_sdk = None
    if not live:
        from .fake_provider import FakeSDK

        fake_sdk = FakeSDK(fake_mode)

    def client_factory():
        return build_client(guard, ledger, live=live, fake_sdk=fake_sdk)

    started = utc_now()
    lifecycle(stage="RUN", state="STARTED", detail=mode)
    conditions: dict[str, Any] = {}
    try:
        lifecycle(stage="CONDITION", condition=c.CONDITION_OFF, state="STARTED")
        conditions[c.CONDITION_OFF] = await run_off(
            client_factory=client_factory, cases=inputs["case_models"], domain_description=inputs["domain_description"],
            output_dir=output_root / "off", lifecycle=lifecycle,
            run_timeout_seconds=manifest["run_timeouts_seconds"][c.CONDITION_OFF],
            max_concurrent=manifest["concurrency"][c.CONDITION_OFF],
        )
        lifecycle(stage="CONDITION", condition=c.CONDITION_OFF, state=conditions[c.CONDITION_OFF]["status"])
        remaining = guard.remaining_reservation_capacity()
        gates["on_unit_reservation_before_start"] = {
            "passed": remaining >= caps[c.CONDITION_ON],
            "detail": f"{remaining} reservable requests remain, ON cap {caps[c.CONDITION_ON]}",
        }
        if remaining >= caps[c.CONDITION_ON]:
            from .on_runner import run_on

            lifecycle(stage="CONDITION", condition=c.CONDITION_ON, state="STARTED")
            conditions[c.CONDITION_ON] = await run_on(
                client_factory=client_factory, cases=inputs["case_models"], domain_description=inputs["domain_description"],
                output_dir=output_root / "on", run_id=run_id, lifecycle=lifecycle, ledger_entries=lambda: list(ledger.entries),
                run_timeout_seconds=manifest["run_timeouts_seconds"][c.CONDITION_ON],
                max_concurrent=manifest["concurrency"][c.CONDITION_ON],
            )
            lifecycle(stage="CONDITION", condition=c.CONDITION_ON, state=conditions[c.CONDITION_ON]["status"])
        else:
            lifecycle(stage="CONDITION", condition=c.CONDITION_ON, state="NOT_STARTED_INSUFFICIENT_RESERVATION")
            conditions[c.CONDITION_ON] = {
                "condition": c.CONDITION_ON, "status": "NOT_STARTED_INSUFFICIENT_RESERVATION", "cases": [],
                "planned_cases": len(inputs["case_models"]), "completed_cases": 0, "elapsed_seconds": 0.0,
                "agent_decomposition": True, "inter_agent_qa": True, "detector_v1": "APPLICABLE",
                "setting_level_requests": 0, "setting_level_cost_usd": 0.0, "setting_level_label_counts": {},
                "episode_summary": {}, "episodes": [], "routes": {}, "event_log_sha256": None, "event_count": 0,
                "event_stream_valid": None, "detector_v1_sha256": None, "protected_runtime_sha256": {},
            }
    finally:
        egress["restore"]()
        lifecycle(stage="RUN", state="FINISHED")
    completed = utc_now()
    output_manifest = _output_manifest(output_root, exclude={"pipeline-output-manifest.json", "run-receipt.json"})
    (output_root / "pipeline-output-manifest.json").write_text(
        json.dumps(output_manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n"
    )
    receipt = {
        "schema_version": c.RECEIPT_SCHEMA,
        "study_id": manifest["study_id"],
        "run_id": run_id,
        "mode": mode,
        "fake_mode": fake_mode,
        "evidence_class": c.EVIDENCE_PROSPECTIVE if live else c.EVIDENCE_FIXTURE,
        "scientific_result_status": "EXECUTED" if live else "NOT_EXECUTED_FIXTURE",
        "execution_git_sha": git_head(),
        "expected_head": args.expected_head,
        "working_tree_clean": git_is_clean(),
        "manifest_path": manifest_relative(),
        "manifest_sha256": manifest["manifest_sha256"],
        "case_selection_sha256": manifest["case_selection"]["sha256"],
        "budget_reservation_sha256": manifest["budget"]["reservation_sha256"],
        "command_fingerprint": command_fingerprint(public_argv),
        "environment": environment_fingerprint(),
        "model": {
            "provider": manifest["provider"]["name"], "model": manifest["provider"]["model"],
            "api_mode": manifest["provider"]["api_mode"], "request_parameters": manifest["request_parameters"],
            "allowed_hosts": manifest["provider"]["allowed_hosts"],
        },
        "caps": caps,
        "budget": guard.summary(),
        "egress": {"allowed_hosts": egress["allowed_hosts"], "blocked_attempts": egress["blocked_hosts"],
                   "blocked_names": egress["blocked_names"]},
        "credential_source": (
            f"process environment variable {c.CREDENTIAL_ENV}, read only by the provider SDK, value never read by the harness"
            if live else "NOT_USED_FAKE_PROVIDER"
        ),
        "case_ids": selection["selected_case_ids"],
        "corpus_hashes": manifest["corpus_hashes"],
        "started_at": started,
        "completed_at": completed,
        "gates": gates,
        "conditions": conditions,
        "lifecycle_summary": lifecycle.summary(),
        "event_log_sha256": conditions[c.CONDITION_ON].get("event_log_sha256"),
        "pipeline_output_manifest_sha256": canonical_sha256(output_manifest),
        "ledger_sha256": file_sha256(output_root / "call-ledger.jsonl") if (output_root / "call-ledger.jsonl").is_file() else None,
        "output_root_template": manifest["output_root_template"].replace("<run_id>", run_id),
        "claim_boundary": CLAIM_BOUNDARY,
    }
    receipt["receipt_binding"] = {
        "algorithm": "sha256 over canonical JSON of the receipt without this field",
        "sha256": canonical_sha256(receipt),
    }
    with (output_root / "run-receipt.json").open("xb") as handle:
        handle.write((json.dumps(receipt, indent=2, sort_keys=True, ensure_ascii=False) + "\n").encode("utf-8"))
    aggregate = build_public_aggregate(receipt, ledger.entries)
    assert_redacted(aggregate, forbidden_fragments=_corpus_fragments(inputs))
    public_dir = Path(args.public_dir) if args.public_dir else DOCS_DIR / "evidence" / run_id
    public_dir.mkdir(parents=True, exist_ok=True)
    (public_dir / "public-aggregate.json").write_text(
        json.dumps(aggregate, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n"
    )
    summary = {
        "run_id": run_id, "mode": mode, "status": {k: v["status"] for k, v in conditions.items()},
        "requests": guard.requests, "actual_cost_usd": round(guard.spent_usd, 6),
        "within_hard_ceiling": guard.spent_usd <= c.HARD_CEILING_USD, "public_aggregate_sha256": aggregate["aggregate_sha256"],
        "receipt_binding_sha256": receipt["receipt_binding"]["sha256"],
    }
    return summary


def manifest_relative() -> str:
    from .manifest import MANIFEST_PATH

    return MANIFEST_PATH.relative_to(ROOT).as_posix()


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("preflight", "execute"):
        p = sub.add_parser(name)
        p.add_argument("--private-root", required=True, help="private evidence root (never written to Git)")
        p.add_argument("--run-id", default=None)
        p.add_argument("--public-dir", default=None)
        p.add_argument("--expected-head", default=None)
        if name == "preflight":
            p.add_argument("--fake-mode", default="two_rounds")
        else:
            p.add_argument("--authorize-live-provider", action="store_true", required=True)
    v = sub.add_parser("validate")
    v.add_argument("--output-root", required=True)
    v.add_argument("--public-aggregate", required=True)
    g = sub.add_parser("gates")
    g.add_argument("--private-root", required=True)
    g.add_argument("--expected-head", default=None)
    args = parser.parse_args(argv)
    args.argv_for_fingerprint = argv
    try:
        if args.command == "validate":
            result = validate_public(Path(args.output_root), Path(args.public_aggregate))
            print(json.dumps(result, indent=2, sort_keys=True))
            return 0 if result["match"] and result["receipt_binding_valid"] and result["ledger_matches_receipt"] else 3
        if args.command == "gates":
            manifest = load_manifest()
            private_root = Path(args.private_root).resolve()
            probe = private_root / "study2-prospective" / f"GATE-PROBE-{hashlib.sha256(utc_now().encode()).hexdigest()[:8]}"
            gates, _, _ = run_gates(manifest, private_root, probe, live=True, expected_head=args.expected_head)
            print(json.dumps({"gates": gates, "all_passed": all(g["passed"] for g in gates.values())}, indent=2, sort_keys=True))
            return 0
        live = args.command == "execute"
        result = asyncio.run(execute(args, live=live))
        print(json.dumps(result, indent=2, sort_keys=True))
        return 0
    except (GateFailure, ManifestError, InventoryError, OffIsolationError) as exc:
        print(json.dumps({"status": "REFUSED", "reason": f"{type(exc).__name__}: {exc}"}, indent=2))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
