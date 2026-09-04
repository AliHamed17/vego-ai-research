"""Exact AirTravel protected-orchestrator fake-preflight harness (preparation default).

Preparation mode (``--prepare-only``, the default) verifies, without invoking
any orchestrator, provider, or fake client: the exact five-file runtime pack
hashes, the deterministic runtime archive hash, the protected-file hashes, the
bounded output path, and the network/provider-disabling controls.  It writes no
scientific event output and exits zero only when the future preflight command
is fully prepared.

Execution mode (``--execute``) is defined for a later, separately authorized
step and is gated behind ``--i-have-explicit-authorization`` plus an existing
authorization packet.  It runs the unchanged protected ``orchestrator.run``
against the frozen ``cd_airtravel`` five-file pack with the reviewed
deterministic local fake client injected at the existing ``LLMClient``
boundary, under a socket-level network guard and with provider credentials
scrubbed from the environment for the duration of the run.  It persists
hashes, lengths, and machine fields only -- never raw prompts or answers.

Counter semantics: ``protected_orchestrator_fake_route_count`` counts routes
observed while the protected orchestrator runs with the local fake client;
``provider_backed_production_route_count`` counts routes observed with a real
provider (always 0 here); ``external_provider_call_count`` counts network
provider calls (always 0 here).  Fake routes are never described as
provider-backed production routes.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import socket
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]

FROZEN: dict[str, Any] = {
    "setting_id": "cd_airtravel",
    "corpus_id": "text2uml_airtravel_253b26dc",
    "case_count": 4,
    "upstream_archive_sha256": "8cf82e2ab2d2ce3da9a7ec4165e760ae1e0d9af14468f5aa2a3883037d8da701",
    "runtime_archive_sha256": "e37baecd20a0c84eb1d9b87b3b78a23bc4b4eb8a9824ad3086dc30aa35fdd31f",
    "runtime_files": {
        "domain_description/description.md": (
            "96bc8a6fbf2c2fdd93592fdbf6fac7c2b9db403494fe2d5a45e0a2bcbf0167e2", 1477),
        "candidate_models/01_result_one_claude-sonnet-4-6.txt": (
            "240b034834e383b9844e9a3e9796f6be9b3d47fc95de6606ed022d278d751f91", 1248),
        "candidate_models/02_result_one_codestral-2508.txt": (
            "08399ca9432c1399f3f9784d34741314e4d39e40307a6efb14fa92a1c138b1d6", 1272),
        "candidate_models/03_result_one_deepseek-chat.txt": (
            "ee4d689d59c9ce3a5e8ff385747641954bd4821f2efeb18e581dcd1d5441d20a", 1324),
        "candidate_models/04_result_one_gemini-2.5-flash.txt": (
            "1c3d15eac71fcaab138857dbbc7153833b3df55ab57925ac756a79dc28dc847a", 1231),
    },
    "protected_files": {
        "VEGO-AI/framework/orchestrator.py":
            "fca4b885ee07381db0f02e558b1aebf25bdc7c27da1c471fd3103d7e0e2d5b88",
        "VEGO-AI/framework/qa_registry.py":
            "ab189d3fd954ea03ba891f5746b36eff8889baeff73d7594f820e68f8762ad5f",
        "VEGO-AI/framework/state.py":
            "d8492a623804065b86905d6183979c322d6f83376bf91026e718c615eea1730d",
        "VEGO-AI/framework/llm_client.py":
            "1a36b4ee860619db97a6ff84ecf64b4845a292ef67cf432c17a86eacd56f55da",
        "VEGO-AI/framework/qa_communication.py":
            "9f2cda1dc52fe919be22ac2ea42d61dce3ed22d3fae7ae27077b3db821594236",
        "VEGO-AI/framework/qa_instrumented_runner.py":
            "d187f8e8113a86caf24e55720e227f9a5f9b3466126969166bcefb83625a215f",
        "VEGO-AI/framework/agent1_language_advisor.py":
            "13e152fe4ec3b417a8c515bbe1bdb28ff952766579ce1ed6463a7ad9fa5b724e",
        "VEGO-AI/framework/agent2_domain_advisor.py":
            "fdf330b99295e871ad3cc3e5e934bb04a15f996a5060ea35d43fa13243d16d79",
        "VEGO-AI/framework/agent3_model_inspector.py":
            "4d0042777040f76abc1ca616a6e1dddcda591ddec54478fa2491b5020a817fa4",
        "VEGO-AI/framework/agent4_variability_explorer.py":
            "6b043c5643f9211d93ac402a9bf98685727e2cd92cab3377d1462dc3417df2ff",
        "schemas/qa-communication-event-v1.schema.json":
            "7df773a6a141a656b32012abd35c34aab25002f2a873c84e61c9ade06af670b2",
    },
    "provider_env_vars": ("OPENAI_API_KEY",),
    "forbidden_runtime_path_tokens": ("reference_only", "plantuml", "extramaterial"),
    "allowed_output_prefixes": ("external_data/", "output/", "reports/generated/"),
}

DEFAULT_RUNTIME_ROOT = Path("external_data/airtravel-v3.2.1/runtime_input")
DEFAULT_RUNTIME_ARCHIVE = Path("external_data/airtravel-v3.2.1/cd_airtravel-runtime-v1.0.2.zip")


class PreflightGateError(RuntimeError):
    """Raised when a fail-closed gate rejects the preparation or execution."""


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


class network_disabled:
    """Context manager that makes any socket creation a hard failure."""

    def __enter__(self) -> network_disabled:
        self._socket = socket.socket
        self._create = socket.create_connection

        def _blocked(*_args: Any, **_kwargs: Any) -> Any:
            raise PreflightGateError("network access attempted during a network-disabled preflight")

        socket.socket = _blocked
        socket.create_connection = _blocked
        return self

    def __exit__(self, *_exc: Any) -> None:
        socket.socket = self._socket
        socket.create_connection = self._create


def scrubbed_provider_env() -> dict[str, str | None]:
    removed: dict[str, str | None] = {}
    for name in FROZEN["provider_env_vars"]:
        removed[name] = os.environ.pop(name, None)
    return removed


def check_runtime_pack(runtime_root: Path) -> dict[str, Any]:
    result: dict[str, Any] = {"name": "runtime_pack", "status": "PASS", "problems": []}
    if not runtime_root.is_dir():
        return {"name": "runtime_pack", "status": "BLOCKED",
                "problems": [f"runtime root does not exist: {runtime_root}"]}
    expected = set(FROZEN["runtime_files"])
    tolerated = {"cd_airtravel.runtime-config.json"}
    observed = {
        path.relative_to(runtime_root).as_posix()
        for path in runtime_root.rglob("*") if path.is_file()
    }
    for token in FROZEN["forbidden_runtime_path_tokens"]:
        leaked = sorted(p for p in observed if token in p.lower())
        if leaked:
            result["problems"].append(f"reference material visible in runtime pack: {leaked}")
    missing = sorted(expected - observed)
    extra = sorted(observed - expected - tolerated)
    if missing:
        result["problems"].append(f"missing runtime files: {missing}")
    if extra:
        result["problems"].append(f"unexpected runtime files: {extra}")
    for relative, (digest, length) in FROZEN["runtime_files"].items():
        path = runtime_root / relative
        if not path.is_file():
            continue
        actual_digest = sha256_file(path)
        actual_length = path.stat().st_size
        if actual_digest != digest or actual_length != length:
            result["problems"].append(
                f"hash/length mismatch for {relative}: {actual_digest}/{actual_length}"
            )
    if result["problems"]:
        result["status"] = "FAIL"
    return result


def check_runtime_archive(archive: Path) -> dict[str, Any]:
    if not archive.is_file():
        return {"name": "runtime_archive", "status": "BLOCKED",
                "problems": [f"deterministic runtime archive not found: {archive}"]}
    digest = sha256_file(archive)
    if digest != FROZEN["runtime_archive_sha256"]:
        return {"name": "runtime_archive", "status": "FAIL",
                "problems": [f"archive hash mismatch: {digest}"]}
    return {"name": "runtime_archive", "status": "PASS", "problems": []}


def check_protected_files(repo_root: Path) -> dict[str, Any]:
    problems = []
    for relative, digest in FROZEN["protected_files"].items():
        path = repo_root / relative
        if not path.is_file():
            problems.append(f"protected file missing: {relative}")
            continue
        actual = sha256_file(path)
        if actual != digest:
            problems.append(f"protected hash drift: {relative} = {actual}")
    status = "PASS" if not problems else "FAIL"
    return {"name": "protected_files", "status": status, "problems": problems}


def check_output_dir(output_dir: Path | None, repo_root: Path) -> dict[str, Any]:
    if output_dir is None:
        return {"name": "output_dir", "status": "PASS",
                "problems": [], "note": "not supplied in prepare-only mode"}
    try:
        relative = output_dir.resolve().relative_to(repo_root.resolve()).as_posix() + "/"
    except ValueError:
        return {"name": "output_dir", "status": "FAIL",
                "problems": [f"output dir must live inside the repository: {output_dir}"]}
    if not relative.startswith(tuple(FROZEN["allowed_output_prefixes"])):
        return {"name": "output_dir", "status": "FAIL",
                "problems": [f"output dir outside the allowed prefixes: {relative}"]}
    if output_dir.exists() and any(output_dir.iterdir()):
        return {"name": "output_dir", "status": "FAIL",
                "problems": [f"output dir already contains files: {output_dir}"]}
    return {"name": "output_dir", "status": "PASS", "problems": []}


def check_provider_disabled(runtime_root: Path) -> dict[str, Any]:
    problems = []
    config_path = runtime_root / "cd_airtravel.runtime-config.json"
    config: dict[str, Any] = {}
    if config_path.is_file():
        config = json.loads(config_path.read_text(encoding="utf-8"))
        if config.get("provider_execution_enabled") is not False:
            problems.append("runtime config does not disable provider execution")
        if config.get("setting_id") != FROZEN["setting_id"]:
            problems.append("runtime config setting_id mismatch")
        if config.get("corpus_id") != FROZEN["corpus_id"]:
            problems.append("runtime config corpus_id mismatch")
    else:
        problems.append("runtime config missing: cd_airtravel.runtime-config.json")
    key_presence = {
        name: ("PRESENT" if os.environ.get(name) else "ABSENT")
        for name in FROZEN["provider_env_vars"]
    }
    status = "PASS" if not problems else ("BLOCKED" if not config else "FAIL")
    return {"name": "provider_disabled", "status": status, "problems": problems,
            "provider_key_presence": key_presence,
            "provider_key_required": False,
            "network_guard": "socket-level, enforced in execute mode",
            "fake_client": "VEGO-AI/framework/qa_instrumented_runner.DeterministicFixtureClient"}


def prepare_only(runtime_root: Path, runtime_archive: Path, output_dir: Path | None,
                 repo_root: Path = REPO_ROOT) -> dict[str, Any]:
    checks = [
        check_runtime_pack(runtime_root),
        check_runtime_archive(runtime_archive),
        check_protected_files(repo_root),
        check_output_dir(output_dir, repo_root),
        check_provider_disabled(runtime_root),
    ]
    ready = all(check["status"] == "PASS" for check in checks)
    return {
        "mode": "prepare_only",
        "setting_id": FROZEN["setting_id"],
        "corpus_id": FROZEN["corpus_id"],
        "case_count": FROZEN["case_count"],
        "checks": checks,
        "protected_orchestrator_fake_route_count": "NOT_EXECUTED",
        "provider_backed_production_route_count": 0,
        "external_provider_call_count": 0,
        "orchestrator_invoked": False,
        "fake_client_invoked": False,
        "scientific_events_written": False,
        "status": "PREPARED" if ready else "BLOCKED",
    }


def execute_preflight(runtime_root: Path, runtime_archive: Path, output_dir: Path,
                      authorization_packet: Path, repo_root: Path = REPO_ROOT) -> dict[str, Any]:
    """Authorized future path: run the unchanged protected orchestrator with the fake client."""
    if not authorization_packet.is_file():
        raise PreflightGateError("authorization packet not found; execution refused")
    preparation = prepare_only(runtime_root, runtime_archive, output_dir, repo_root)
    if preparation["status"] != "PREPARED":
        raise PreflightGateError(f"preparation gates not green: {preparation['checks']}")

    sys.path.insert(0, str(repo_root / "VEGO-AI" / "framework"))
    import asyncio

    import orchestrator
    from qa_communication import (
        QACommunicationRecorder,
        build_episode_projection,
        validate_event_stream,
    )
    from qa_instrumented_runner import DeterministicFixtureClient, InstrumentedLLMClientProxy

    output_dir.mkdir(parents=True, exist_ok=True)
    run_config = {
        "log_level": "WARNING",
        "settings": [{
            "setting_id": FROZEN["setting_id"],
            "language_name": "UML",
            "domain_description_file": str((runtime_root / "domain_description/description.md").resolve()),
            "case_models_dir": str((runtime_root / "candidate_models").resolve()),
            "output_dir": str((output_dir / "pipeline").resolve()),
            "max_concurrent_cases": 2,
        }],
    }
    config_path = output_dir / "run_config.preflight.json"
    config_path.write_text(json.dumps(run_config, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    recorder = QACommunicationRecorder(output_dir / "qa_events.jsonl",
                                       run_id=f"study1-airtravel-preflight-{FROZEN['corpus_id']}")
    proxy = InstrumentedLLMClientProxy(DeterministicFixtureClient(), recorder,
                                       run_id=recorder.run_id, setting_id=FROZEN["setting_id"])
    scrubbed = scrubbed_provider_env()
    original_client = orchestrator.LLMClient
    orchestrator.LLMClient = lambda **_: proxy
    try:
        with network_disabled():
            asyncio.run(orchestrator.run(config_path, only_setting=FROZEN["setting_id"]))
    finally:
        orchestrator.LLMClient = original_client
        for name, value in scrubbed.items():
            if value is not None:
                os.environ[name] = value

    validate_event_stream(recorder.events)
    episodes = build_episode_projection(recorder.events)
    unterminated = [e for e in episodes if e["termination_reason"] is None]
    if unterminated:
        raise PreflightGateError(f"unterminated episodes: {[e['episode_id'] for e in unterminated]}")
    receipt = {
        "mode": "execute",
        "authorization_packet_sha256": sha256_file(authorization_packet),
        "call_count": len(proxy.calls),
        "episode_count": len(episodes),
        "protected_orchestrator_fake_route_count": len({e["episode_id"] for e in episodes}),
        "provider_backed_production_route_count": 0,
        "external_provider_call_count": 0,
        "events_path": str(output_dir / "qa_events.jsonl"),
        "status": "EXECUTED_OFFLINE",
    }
    (output_dir / "preflight-receipt.json").write_text(
        json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return receipt


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prepare-only", action="store_true", default=False)
    parser.add_argument("--execute", action="store_true", default=False)
    parser.add_argument("--i-have-explicit-authorization", action="store_true", default=False)
    parser.add_argument("--authorization-packet", type=Path)
    parser.add_argument("--runtime-root", type=Path, default=DEFAULT_RUNTIME_ROOT)
    parser.add_argument("--runtime-archive", type=Path, default=DEFAULT_RUNTIME_ARCHIVE)
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--receipt", type=Path)
    args = parser.parse_args()

    if args.execute and args.prepare_only:
        parser.error("--execute and --prepare-only are mutually exclusive")
    if args.execute:
        if not args.i_have_explicit_authorization or not args.authorization_packet:
            parser.error("--execute requires --i-have-explicit-authorization and --authorization-packet")
        if not args.output_dir:
            parser.error("--execute requires --output-dir")
        result = execute_preflight(args.runtime_root, args.runtime_archive,
                                   args.output_dir, args.authorization_packet)
    else:
        result = prepare_only(args.runtime_root, args.runtime_archive, args.output_dir)

    rendered = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.receipt:
        args.receipt.parent.mkdir(parents=True, exist_ok=True)
        args.receipt.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 0 if result["status"] in {"PREPARED", "EXECUTED_OFFLINE"} else 2


if __name__ == "__main__":
    raise SystemExit(main())
