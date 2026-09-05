"""Generate metadata-only review packet; optionally materialize verified private bytes."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path

import airtravel_preflight_contract as c
from audit_historical_case_recovery_v3_2 import (
    UPSTREAM_SHA256,
    verify_mapping,
    verify_runtime_pack,
    verify_upstream,
)
from materialize_airtravel_runtime_v3_2_1 import materialize_runtime
from prepare_airtravel_protected_fake_preflight import FROZEN, prepare_only

DOC = c.ROOT / "docs/research/phd-proposal"
EVIDENCE = DOC / "airtravel-pr38-correction"
MANIFEST = DOC / "text2uml-airtravel/amendment-manifest-v1.0.2.json"
MANIFEST_HASH = "bd2b7f03585582ff7591d21795fbd3ed4701244d66d26221683520238c2dead2"
CODE = [
    "scripts/prepare_airtravel_protected_fake_preflight.py",
    "scripts/airtravel_preflight_contract.py",
    "scripts/airtravel_execution_safety.py",
    "scripts/airtravel_local_observer.py",
    "scripts/airtravel_preflight_execution.py",
    "scripts/study1_call_bound.py",
    "schemas/airtravel-fake-grant-v1.schema.json",
    "schemas/qa-communication-event-v1.schema.json",
    "scripts/extract_qa_escalation_features.py",
]


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(c.canonical(value) if not isinstance(value, str) else value.encode("utf-8"))


def build(upstream, *, materialize=False):
    if c.digest(upstream) != UPSTREAM_SHA256:
        raise ValueError("upstream archive hash mismatch")
    if c.digest(MANIFEST) != MANIFEST_HASH:
        raise ValueError("scientific manifest changed")
    source = verify_upstream(upstream, DOC / "text2uml-airtravel/source-manifest.json")
    if source["status"] != "PASS":
        raise ValueError("source verification failed")
    private = c.ROOT / "external_data/airtravel-pr38"
    runtime = private / "runtime_input"
    archive = private / "cd_airtravel-runtime-v1.0.2.zip"
    if materialize:
        if runtime.exists() or archive.exists():
            raise ValueError("refusing to overwrite runtime")
        if not c.git(c.ROOT, "check-ignore", "--", "external_data/airtravel-pr38/runtime_input"):
            raise ValueError("private corpus is not ignored")
        materialize_runtime(upstream, runtime)
    amendment = json.loads(MANIFEST.read_text(encoding="utf-8"))
    mapping = verify_mapping(source, amendment, archive)
    pack = verify_runtime_pack(archive, amendment, runtime / "cd_airtravel.runtime-config.json")
    if (
        c.digest(archive) != FROZEN["runtime_archive_sha256"]
        or mapping["status"] != "PASS"
        or pack["status"] != "PASS"
    ):
        raise ValueError("mapping/runtime verification failed")
    protected = c.protected_hashes(c.ROOT)
    code = {p: c.digest(c.ROOT / p) for p in CODE}
    payload = {
        "status": "AUTHORIZATION_REQUESTED_NOT_GRANTED",
        "base_sha": c.BASE,
        "correction_parent_sha": c.PARENT,
        "pr": 38,
        "protected_hashes": protected,
        "code_hashes": code,
        "runtime_archive_sha256": c.digest(archive),
        "amendment_manifest_sha256": MANIFEST_HASH,
        "setting_id": c.SETTING,
        "corpus_id": c.CORPUS,
        "N": 4,
        "runtime_files": {
            p: {"sha256": v[0], "bytes": v[1]} for p, v in FROZEN["runtime_files"].items()
        },
    }
    write(EVIDENCE / "protected-hashes.json", protected)
    write(
        EVIDENCE / "source-runtime-receipt.json",
        {
            "audit_base_sha": c.BASE,
            "amendment_manifest_sha256": MANIFEST_HASH,
            "source": {
                k: source[k]
                for k in (
                    "status",
                    "archive_sha256",
                    "manifest_sha256",
                    "expected_file_count",
                    "observed_file_count",
                    "matched_count",
                    "missing_count",
                    "extra_count",
                    "mismatched_count",
                    "duplicate_members",
                    "commit_identity_status",
                )
            },
            "mapping": mapping,
            "runtime": pack,
            "derivation": "DERIVED_BYTE_IDENTICAL_RUNTIME_PREPARATION",
            **c.counters(),
            "exact_fake_preflight": "NOT_EXECUTED",
        },
    )
    table = "\n".join(f"| `{p}` | `{h}` | READ_ONLY / unchanged |" for p, h in protected.items())
    code_table = "\n".join(f"| `{p}` | `{h}` |" for p, h in code.items())
    runtime_table = "\n".join(
        f"| `{p}` | {v[1]} | `{v[0]}` |" for p, v in FROZEN["runtime_files"].items()
    )
    text = f"""# AirTravel authorization packet v3

Status: **AUTHORIZATION_REQUESTED_NOT_GRANTED**. Packet v2 is SUPERSEDED_NOT_AUTHORIZABLE.
PR: [38](https://github.com/AliHamed17/vego-ai-research/pull/38); do not merge or execute.
Green base: `{c.BASE}`. Correction parent: `{c.PARENT}`.
The later owner-issued grant must bind the **full final corrected PR head**, independently compared to `git rev-parse HEAD`, this packet hash, harness hash, archive, command fingerprint, output directory and all protected hashes. A PR body or an assertion flag is not a grant. This immutable request plus a separate matching grant are both required; the request alone always fails. No grant is issued by this task.

## Future command and scope

Working directory: the exact checkout identified in the private `external_data/airtravel-pr38/private-execution-request.json` (generated on the executing machine). Verify its HEAD is the subsequently reviewed green PR head before issuing the grant. Public records intentionally omit personal absolute paths.

```powershell
python scripts/prepare_airtravel_protected_fake_preflight.py --execute --authorization-packet docs/research/phd-proposal/2026-09-05-airtravel-protected-fake-preflight-authorization-packet-v3.md --authorization-grant external_data/airtravel-pr38/authorization-grant.json --runtime-root external_data/airtravel-pr38/runtime_input --runtime-archive external_data/airtravel-pr38/cd_airtravel-runtime-v1.0.2.zip --output-dir external_data/airtravel-pr38/authorized-fake-run --receipt external_data/airtravel-pr38/authorized-fake-run/preflight-receipt.json
```

DO NOT RUN this command now. The private request records its fully resolved executable/arguments and SHA-256 fingerprint. The grant file does not exist. The sole tracked example is `TEST_FIXTURE_ONLY` and is rejected.

Allowed reads: clean tracked checkout files (including the protected table), exact five runtime files below, the runtime configuration/archive, packet and grant during validation. Provider credentials, browser profiles, key stores, subprocesses and dynamic native/provider imports are forbidden during orchestration. Allowed writes: **only** `external_data/airtravel-pr38/authorized-fake-run/`, initially absent/empty, symlink-free and Git-ignored. Fixed children: `baseline/`, `instrumented/`, `preflight-receipt.json`. Full private resolved paths are fingerprint-bound in the grant.

Each pipeline child writes pipeline_state.json, pipeline.log, language_template.json, reference_guidelines.json, compliance_vectors.json, uncovered_fragments.json, deviation_patterns.json, variability_classifications.json, lang_qa_history.json, dom_qa_history.json and human_review_queue.jsonl. Instrumented alone adds qa_events.jsonl. Maximum {c.MAX_FILES} files and {c.MAX_BYTES} persisted bytes; conservative cumulative write quota is also enforced. Unexpected files, outside writes, nonempty destinations or tracked/protected drift fail closed. The receipt cannot escape the granted directory.

## Two-pass checks and timeout

Direct `RecordingFake(two_rounds)` baseline versus the same deterministic fake through `Proxy` and the external registry observer. Expected 46 logical calls per pass, 92 combined; enforced minimum/maximum **16–326 per pass**, never 326 combined. Absolute combined maximum 652. The bound verifies the current protected orchestrator hash before using its inventory. Costs and tokens: **TO BE MEASURED** (not HTTP retry bounds).

Require ordered labels, prompt hashes, answer hashes, per-pass counts, complete PipelineState and every scientific output hash to match. Only logs (wall-clock timestamps) are excluded from scientific byte parity; observer events/receipts are the permitted additions. All four case IDs 01–04 and all four phases must complete.

Timeout: {c.TIMEOUT} seconds around the complete two-pass coroutine, with cancellation, no retry, LLMClient/registry restoration, environment restoration and handler closure before a TECHNICAL_FAILED receipt. Fixture tests use a short timeout; CLI cannot override it. Trusted deterministic Python control flow yields at each fake call. This is a Python audit/IO safety boundary, not a kernel sandbox or a defense against hostile native extensions. Event-loop local IPC is created before external-network denial; protected execution permits no network attempt. Any attempted socket/DNS/provider path is counted and fails even if caught below.

Lifecycle: actual source/skill/case/round labels and registry-assigned IDs bind exact pre-hash questions to answers. One loop invocation retains its episode across rounds and targets. A questionless next round closes CONVERGED; answered final round closes TERMINATED_MAX_ROUNDS; exception/missing answer/correlation failure closes INCOMPLETE_TECHNICAL. Never label every open episode converged. Unresolved/cross-run/cross-episode/duplicate/post-terminal evidence is rejected. No helper-only routes are counted as provider observations.

Counters: protected_orchestrator_fake_route_count counts distinct directed (source_agent,target_agent) QUESTION_EMITTED pairs only after execution; before then NOT_EXECUTED. Episode/question/answer counts are separate. Baseline/instrumented/combined fake-call counts are separate. Provider-backed production routes, external provider calls, network attempts and Detector-v1 experimental runs remain zero before execution. Detector-v1 is not invoked by preflight.

## Privacy, failure, rollback and expiry

Only the Q&A event log stores hashes, lengths and machine fields. Pipeline artifacts can contain complete fake/public-external scientific state. Every output remains private and ignored; nothing is automatically committed. Extracted public receipts require a separate privacy scan. Future paid-run raw prompts/answers remain private.

On failure: stop without retry, report technical failure, never treat empty events as valid zero-Q&A. Keep partial evidence private. Rollback: restore the reviewed checkout via an ordinary reviewed revert if needed; after verifying its exact resolved path, remove only this run's ignored output directory. Do not reset main, clean the repository, or delete unrelated work. No protected file modification is requested.

Expiry: any bound commit/hash/path/command change, main drift, or expiry timestamp invalidates the grant. Ali alone may issue the later matching machine grant after explicit approval of this exact packet and green corrected head. GPL review concerns publication/redistribution, not private local preflight. This request authorizes neither a provider, paid run, Detector-v1 experimental analysis, raw-data publication nor synthetic corpus generation.

## Runtime bytes

Archive SHA-256: `{c.digest(archive)}`. Setting `{c.SETTING}`, corpus `{c.CORPUS}`, N=4. Reference files are outside runtime inputs.

| Runtime path | Bytes | SHA-256 |
|---|---:|---|
{runtime_table}

## Corrected executable content

| Path | SHA-256 |
|---|---|
{code_table}

## Protected inventory

| Full repository-relative path | Before = after SHA-256 | Access |
|---|---|---|
{table}

<!-- AIRTRAVEL_PACKET_V3
{json.dumps(payload, sort_keys=True, indent=2)}
-->
"""
    write(c.ROOT / c.PACKET, text)
    out = private / "authorized-fake-run"
    tokens = c.execution_tokens(
        runtime, archive, out, c.ROOT / c.PACKET, private / "authorization-grant.json"
    )
    write(
        private / "private-execution-request.json",
        {
            "status": "AUTHORIZATION_REQUESTED_NOT_GRANTED",
            "working_directory": str(c.ROOT),
            "observed_preparation_head": c.git(c.ROOT, "rev-parse", "HEAD"),
            "packet_sha256": c.digest(c.ROOT / c.PACKET),
            "command": subprocess.list2cmdline(tokens),
            "tokens": tokens,
            "command_sha256": hashlib.sha256(c.canonical(tokens)).hexdigest(),
            "output_directory": str(out),
        },
    )
    return prepare_only(runtime, archive, out, c.ROOT)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--upstream-archive", type=Path, required=True)
    parser.add_argument("--materialize", action="store_true")
    args = parser.parse_args()
    print(json.dumps(build(args.upstream_archive, materialize=args.materialize), sort_keys=True))
