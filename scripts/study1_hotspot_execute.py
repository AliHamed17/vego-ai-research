"""Issue a one-time execution grant, verify every gate, and run the frozen hotspot protocol.

A grant that merely records an intention is decoration. This one is checkable and single-use: it
binds the head, the manifest digest, the model, the budget, the call cap, the corpus digest and
the output root, and the runner refuses unless every binding still holds at execution time. A
grant is consumed the moment a run starts, so the same grant cannot authorise a second run.

The gates verified before any provider call:

  * the working tree is clean, so the executing code is exactly the reviewed head;
  * continuous integration concluded **success at that exact head**, not at some earlier commit;
  * the manifest digest matches the one the grant was issued against;
  * the offline fake-provider preflight has been run and contacted no provider;
  * the pessimistic whole-study reservation still fits the ceiling;
  * no receipt already exists at the output root.

At consumption every binding is recomputed rather than trusted. A git-ignored runtime file,
contract or preflight record that changed after issue invalidates the grant, because those
files are outside version control and nothing else would notice they moved.

Refusal is the default. Any gate that cannot be evaluated is treated as failed.
"""

from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

MANIFEST = ROOT / "docs/research/phd-proposal/study1-hotspot-manifest.json"
GRANT_PATH = ROOT / "external_data/airtravel-pr38/hotspot/execution-grant.json"
PREFLIGHT = ROOT / "external_data/airtravel-pr38/hotspot/preflight.json"
RUNTIME_ROOT = ROOT / "external_data/airtravel-pr38/hotspot/runtime"
OUTPUT_ROOT = ROOT / "external_data/airtravel-pr38/hotspot/run/output"
RUN_ID = "HOTSPOT-01"


class GateFailure(RuntimeError):
    """Raised when a precondition cannot be verified. Refusal is the default."""


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git(*args: str) -> str:
    return subprocess.run(
        ["git", *args], cwd=ROOT, capture_output=True, text=True, check=False
    ).stdout.strip()


def gate_clean_tree() -> dict[str, Any]:
    """Executing code must be committed, so an untracked script fails this gate too."""
    modified, untracked_code = [], []
    for line in git("status", "--porcelain").splitlines():
        if not line.strip():
            continue
        path = line[3:].strip().strip('"')
        if line.startswith("??"):
            if path.startswith(("scripts/", "src/", "VEGO-AI/")) and path.endswith(
                (".py", ".ps1", ".mjs", ".js")
            ):
                untracked_code.append(path)
        else:
            modified.append(path)
    if modified:
        raise GateFailure(f"uncommitted tracked changes: {modified[:5]}")
    if untracked_code:
        raise GateFailure(f"untracked executable code would run unreviewed: {untracked_code[:5]}")
    return {"clean_tree": True, "untracked_code": []}


def gate_ci_green(head: str) -> dict[str, Any]:
    raw = subprocess.run(
        ["gh", "run", "list", "--limit", "20", "--json",
         "databaseId,status,conclusion,headSha,workflowName"],
        cwd=ROOT, capture_output=True, text=True, check=False,
    ).stdout
    try:
        runs = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise GateFailure(f"could not read CI status: {exc}") from exc
    at_head = [run for run in runs if run.get("headSha") == head]
    if not at_head:
        raise GateFailure(f"no CI run found at exact head {head}")
    completed = [run for run in at_head if run.get("status") == "completed"]
    if not completed:
        raise GateFailure(f"CI at head {head} has not completed")
    failed = [run for run in completed if run.get("conclusion") != "success"]
    if failed:
        raise GateFailure(
            f"CI at head {head} concluded {[run['conclusion'] for run in failed]}"
        )
    return {
        "exact_head": head,
        "runs": [{"id": run["databaseId"], "conclusion": run["conclusion"]} for run in completed],
    }


def gate_preflight() -> dict[str, Any]:
    if not PREFLIGHT.is_file():
        raise GateFailure("offline preflight has not been run")
    payload = json.loads(PREFLIGHT.read_text(encoding="utf-8"))
    if payload.get("provider_calls") != 0:
        raise GateFailure("preflight recorded provider calls; it must be offline")
    return {
        "preflight_sha256": digest(PREFLIGHT),
        "provider_calls": 0,
        "structural_calls_at_frame_size": payload["measurements"][0]["fake_calls"],
    }


def gate_budget(manifest: dict[str, Any]) -> dict[str, Any]:
    budget = manifest["budget"]
    if not budget["fits"]:
        raise GateFailure("pessimistic whole-study reservation exceeds the ceiling")
    return budget


def gate_corpus() -> dict[str, Any]:
    contract_path = RUNTIME_ROOT / "full-frame-contract.json"
    if not contract_path.is_file():
        raise GateFailure("hotspot runtime has not been materialised")
    contract = json.loads(contract_path.read_text(encoding="utf-8"))
    for relative, pin in contract["runtime_files"].items():
        target = RUNTIME_ROOT / relative
        if not target.is_file() or digest(target) != pin["sha256"]:
            raise GateFailure(f"runtime file does not match its pin: {relative}")
    if contract["manifest_sha256"] != digest(MANIFEST):
        raise GateFailure("runtime was materialised against a different manifest")
    return {
        "case_count": contract["case_count"],
        "archive_sha256": contract["archive_sha256"],
        "contract_sha256": digest(contract_path),
    }


def issue_grant() -> dict[str, Any]:
    if GRANT_PATH.exists():
        raise GateFailure(f"a grant already exists at {GRANT_PATH}; grants are one-time")
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    head = git("rev-parse", "HEAD")
    grant = {
        "schema_version": "study1-hotspot-execution-grant-v1",
        "grant_id": f"GRANT-{RUN_ID}",
        "issued_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "state": "ISSUED",
        "single_use": True,
        "bindings": {
            "head": head,
            "manifest_sha256": digest(MANIFEST),
            "model": manifest["protocol"]["model"],
            "budget_usd": manifest["budget"]["ceiling_usd"],
            "call_cap": manifest["budget"]["call_cap"],
            "run_count": manifest["protocol"]["run_count"],
            "corpus_id": manifest["corpus"]["corpus_id"],
            "output_root": str(OUTPUT_ROOT.relative_to(ROOT)).replace("\\", "/"),
            "run_id": RUN_ID,
        },
        "gates": {
            "clean_tree": gate_clean_tree(),
            "ci_green_at_exact_head": gate_ci_green(head),
            "offline_preflight": gate_preflight(),
            "pessimistic_reservation": gate_budget(manifest),
            "corpus_pins": gate_corpus(),
        },
    }
    GRANT_PATH.parent.mkdir(parents=True, exist_ok=True)
    GRANT_PATH.write_text(json.dumps(grant, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return grant


def consume_grant() -> dict[str, Any]:
    if not GRANT_PATH.is_file():
        raise GateFailure("no execution grant exists")
    grant = json.loads(GRANT_PATH.read_text(encoding="utf-8"))
    if grant["state"] != "ISSUED":
        raise GateFailure(f"grant state is {grant['state']}; it has already been used")
    bindings = grant["bindings"]
    head = git("rev-parse", "HEAD")
    if bindings["head"] != head:
        raise GateFailure(f"grant is bound to head {bindings['head']}, current head is {head}")
    if bindings["manifest_sha256"] != digest(MANIFEST):
        raise GateFailure("the manifest changed after the grant was issued")
    gate_clean_tree()
    corpus_now = gate_corpus()
    issued = grant["gates"]
    if corpus_now["contract_sha256"] != issued["corpus_pins"]["contract_sha256"]:
        raise GateFailure("the runtime contract changed after the grant was issued")
    if corpus_now["archive_sha256"] != issued["corpus_pins"]["archive_sha256"]:
        raise GateFailure("the corpus archive digest changed after the grant was issued")
    if corpus_now["case_count"] != issued["corpus_pins"]["case_count"]:
        raise GateFailure("the runtime case count changed after the grant was issued")
    if gate_preflight()["preflight_sha256"] != issued["offline_preflight"]["preflight_sha256"]:
        raise GateFailure("the offline preflight record changed after the grant was issued")
    grant["state"] = "CONSUMED"
    grant["consumed_at"] = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    GRANT_PATH.write_text(json.dumps(grant, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return grant


def execute(grant: dict[str, Any]) -> int:
    import airtravel_full_frame_run as harness

    if not os.environ.get("OPENAI_API_KEY"):
        raise GateFailure("OPENAI_API_KEY is absent from the process environment")
    bindings = grant["bindings"]
    if (OUTPUT_ROOT / "run-receipt.json").exists():
        raise GateFailure("a receipt already exists at the output root")

    receipt = asyncio.run(
        harness.run(
            OUTPUT_ROOT,
            RUNTIME_ROOT,
            bindings["run_id"],
            budget_usd=float(bindings["budget_usd"]),
            prior_spend_usd=0.0,
            max_requests=int(bindings["call_cap"]),
        )
    )
    receipt["study_id"] = "STUDY1-HOTSPOT"
    receipt["grant_id"] = grant["grant_id"]
    receipt["manifest_sha256"] = bindings["manifest_sha256"]
    receipt["evidence_class"] = "PROSPECTIVE EMPIRICAL EVIDENCE"
    target = OUTPUT_ROOT / "run-receipt.json"
    with target.open("xb") as handle:
        handle.write(
            (json.dumps(receipt, indent=2, sort_keys=True, ensure_ascii=False) + "\n").encode("utf-8")
        )
    print(json.dumps(receipt, indent=2, sort_keys=True, ensure_ascii=False))
    return 0 if receipt["status"] == "TECHNICAL_SUCCESS" else 3


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--issue-grant", action="store_true")
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args()
    try:
        if args.issue_grant:
            grant = issue_grant()
            print(json.dumps({"state": grant["state"], "bindings": grant["bindings"]}, indent=2))
            return 0
        if args.execute:
            return execute(consume_grant())
    except GateFailure as exc:
        print(json.dumps({"status": "REFUSED", "gate_failure": str(exc)}, indent=2))
        return 2
    parser.error("choose --issue-grant or --execute")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
