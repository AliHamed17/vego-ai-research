"""Fail-closed composition boundary. Importing this module has no provider capability.

The CLI reruns source verification and snapshots the five bound runtime files.
An accepted execute decision additionally consumes durable nonce AND invocation
markers in a fixed private repository-local control root, outside run outputs.
Markers are exclusive, fsynced, contain no grant data, and are never removed.
Partial claims are deliberately burned on failure. A local actor able to delete
control records or replace running Python is outside this filesystem trust boundary.
"""

from __future__ import annotations

import hashlib
import json
import os
import stat
import subprocess
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from threading import Lock
from typing import Any

import airtravel_execution_contract as contract

CODE_PATHS = (
    "scripts/study1_external_execution_gate.py",
    "scripts/study1_airtravel_external_runner.py",
    "scripts/airtravel_execution_contract.py",
    "scripts/airtravel_execution_provider.py",
    "scripts/airtravel_execution_pipeline.py",
    "scripts/verify_text2uml_airtravel_runtime.py",
    "scripts/extract_qa_escalation_features.py",
    "VEGO-AI/framework/qa_communication.py",
    "schemas/airtravel-api-execution-config-v1.schema.json",
    "schemas/airtravel-api-execution-grant-v1.schema.json",
    "schemas/airtravel-api-execution-receipt-v1.schema.json",
    "schemas/qa-communication-event-v1.schema.json",
    "pyproject.toml",
    "uv.lock",
)
VERIFICATION_KEYS = frozenset(
    {
        "archive",
        "source_root",
        "source_manifest",
        "runtime_root",
        "reference_root",
        "amendment_manifest",
    }
)
CONTROL_PARENT = "external_data/airtravel-api-control"
_PERMISSION = object()


@dataclass
class _Permit:
    token: object
    expires_at: datetime
    context_sha256: str
    used: bool = False
    lock: Any = field(default_factory=Lock, repr=False)


def _invocation_digest(mode, config, manifest, command, run_root, grant):
    return contract.canonical_json_sha256(
        {
            "mode": mode,
            "config": config.sha256,
            "manifest": manifest.sha256,
            "command": contract.command_fingerprint(command),
            "root": str(run_root),
            "grant": grant.to_dict() if isinstance(grant, contract.ExecutionGrant) else grant,
        }
    )


@dataclass(frozen=True)
class _Decision(Mapping):
    status: str
    mode: str
    provider_construction_permitted: bool = False
    technical_error_code: str = "NONE"
    _permission: object = field(default=None, repr=False)

    def __getitem__(self, key):
        if key not in tuple(self):
            raise KeyError(key)
        return getattr(self, key)

    def __iter__(self):
        return iter(("status", "mode", "provider_construction_permitted", "technical_error_code"))

    def __len__(self):
        return 4


def current_commit() -> str:
    """Bind committed execution code, rejecting dirty, missing and untracked code."""
    for name in ("qa_communication.py", "qa_communication.pyc", "qa_communication"):
        shadow = contract.REPOSITORY_ROOT / "scripts" / name
        if shadow.exists() or shadow.is_symlink():
            raise contract.ContractValidationError("QA module shadow rejected")
    result = contract._git("rev-parse", "HEAD")
    if result.returncode:
        raise contract.ContractValidationError("code identity unavailable")
    commit = contract._commit(result.stdout.strip())
    for name in CODE_PATHS:
        assert_committed_file(name, commit)
    tracked = contract._git("ls-files", "--error-unmatch", "--", *CODE_PATHS)
    dirty = contract._git("diff", "--quiet", "HEAD", "--", *CODE_PATHS)
    if tracked.returncode or dirty.returncode:
        raise contract.ContractValidationError("execution code does not match commit")
    return commit


def assert_committed_file(name: str, commit: str) -> None:
    """Compare actual bytes to the commit, bypassing assume-unchanged/index caches."""
    path = checked_input(name)
    result = subprocess.run(
        [
            "git",
            "-C",
            str(contract.REPOSITORY_ROOT),
            "cat-file",
            "blob",
            f"{contract._commit(commit)}:{name}",
        ],
        capture_output=True,
        check=False,
        timeout=10,
    )
    if result.returncode or result.stdout != path.read_bytes():
        raise contract.ContractValidationError("committed input byte mismatch")


def parse_complete_command(argv: Sequence[str]) -> dict[str, str]:
    """Use Task 2's parser once, then require this runner's complete option set."""
    parsed = contract.parse_execution_command(argv)
    if argv[0] != parsed["mode"]:
        raise contract.ContractValidationError("CLI argv cannot contain a launcher")
    common = {"mode", "config", "private_root", "run_id"}
    required = common | (
        {"archive", "source_root", "source_manifest", "runtime_root", "amendment", "reference_root"}
        if parsed["mode"] == "prepare"
        else {"input_manifest"}
    )
    if parsed["mode"] == "execute":
        required.add("grant")
    if set(parsed) != required or parsed["private_root"] != contract.PRIVATE_PARENT:
        raise contract.ContractValidationError("incomplete or noncanonical CLI")
    contract.assert_safe_run_id(parsed["run_id"])
    for name, value in parsed.items():
        if name not in {"mode", "run_id"}:
            contract._relative_file(value)
    return parsed


def checked_input(value: str, *, private: bool = False, directory: bool = False) -> Path:
    """Canonical repo-relative input; never follow links, reparse points or ADS."""
    contract._relative_file(value)
    path = contract.REPOSITORY_ROOT / value
    contract._check_path_components(path if directory else path.parent)
    info = path.lstat()
    if (
        stat.S_ISLNK(info.st_mode)
        or getattr(info, "st_file_attributes", 0)
        & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 1024)
        or (not directory and not stat.S_ISREG(info.st_mode))
        or (directory and not stat.S_ISDIR(info.st_mode))
        or (not directory and info.st_nlink != 1)
    ):
        raise contract.ContainmentError("unsafe input")
    for sibling in path.parent.iterdir():
        if sibling.name.casefold() == path.name.casefold() and sibling.name != path.name:
            raise contract.ContainmentError("input case collision")
    # Reject lexical aliases first; only then resolve the accepted filesystem
    # object and use that canonical relative spelling for Git's exact matching.
    path = path.resolve(strict=True)
    relative = path.relative_to(contract.REPOSITORY_ROOT.resolve(strict=True)).as_posix()
    if private and not relative.startswith(contract.PRIVATE_PARENT + "/"):
        raise contract.ContainmentError("input is not under private parent")
    if private:
        ignored = contract._git("check-ignore", "--no-index", "--quiet", "--", relative)
        tracked = contract._git("ls-files", "--", relative)
        if ignored.returncode or tracked.returncode or tracked.stdout.strip():
            raise contract.ContainmentError("input is not private")
    return path


def check_run_root(root: Path, run_id: str) -> None:
    contract.assert_safe_run_id(run_id)
    expected = contract.REPOSITORY_ROOT / contract.PRIVATE_PARENT / run_id
    if root != expected or not root.is_dir():
        raise contract.ContainmentError("run root mismatch")
    contract._check_path_components(root)
    relative = f"{contract.PRIVATE_PARENT}/{run_id}"
    if contract._git(
        "check-ignore", "--no-index", "--quiet", "--", relative + "/receipt.json"
    ).returncode:
        raise contract.ContainmentError("output is not private")
    tracked = contract._git("ls-files", "--", relative)
    if tracked.returncode or tracked.stdout.strip():
        raise contract.ContainmentError("output contains tracked files")


def write_private(root: Path, name: str, value: Mapping[str, Any], *, immutable=False) -> Path:
    """Exclusive private artifact write; no overwrite even after partial failure."""
    check_run_root(root, root.name)
    if name not in {"input_manifest.json", "receipt.json", "ledger.json"}:
        raise contract.ContainmentError("unapproved artifact")
    payload = json.dumps(
        value, sort_keys=True, ensure_ascii=False, allow_nan=False, separators=(",", ":")
    ).encode()
    path = root / name
    root_id = root.stat()
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0)
    fd = os.open(path, flags, 0o600)
    with os.fdopen(fd, "wb") as handle:
        check_run_root(root, root.name)
        if not os.path.samestat(root_id, root.stat()):
            raise contract.ContainmentError("output directory replaced")
        handle.write(payload)
        handle.flush()
        os.fsync(handle.fileno())
    if immutable:
        path.chmod(stat.S_IREAD)
    return path


def _claim_attempt(nonce: str, invocation_id: str) -> None:
    root = contract.REPOSITORY_ROOT / CONTROL_PARENT
    contract._check_path_components(root)
    for item in (CONTROL_PARENT, CONTROL_PARENT + "/probe.attempt"):
        if contract._git("check-ignore", "--no-index", "--quiet", "--", item).returncode:
            raise contract.ContainmentError("durable control root is not ignored")
    tracked = contract._git("ls-files", "--", CONTROL_PARENT)
    if tracked.returncode or tracked.stdout.strip():
        raise contract.ContainmentError("durable control root contains tracked paths")
    root.mkdir(mode=0o700, exist_ok=True)
    contract._check_path_components(root)
    root_id = root.stat()
    for category, identity in (("nonce", nonce), ("invocation", invocation_id)):
        name = hashlib.sha256((category + ":" + identity).encode()).hexdigest() + ".attempt"
        fd = os.open(
            root / name, os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0), 0o600
        )
        with os.fdopen(fd, "wb") as handle:
            contract._check_path_components(root)
            if not os.path.samestat(root_id, root.stat()):
                raise contract.GrantValidationError("durable store replaced")
            handle.write(b'{"schema_version":"airtravel-attempt-v1","attempted":true}')
            handle.flush()
            os.fsync(handle.fileno())
    if os.name != "nt":
        fd = os.open(root, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0))
        try:
            os.fsync(fd)
        finally:
            os.close(fd)


def _fake_authorization(raw, config, manifest, command, now):
    """Separate local authority: no fake grant becomes an ExecutionGrant object."""
    if (
        not isinstance(raw, Mapping)
        or raw.get("schema_version") != "airtravel-local-fake-preflight-grant-v1"
        or raw.get("mode") != "preflight"
    ):
        raise contract.GrantValidationError("separate local fake authorization required")
    # Reuse the strict field/type schema only, not execute authorization.
    shape = dict(raw, schema_version="airtravel-api-execution-grant-v1", mode="execute")
    contract._schema_validate("grant", shape)
    parsed = contract.parse_execution_command(command)
    expected = {
        key: getattr(config, key)
        for key in (
            "model",
            "provider_host",
            "timeout_seconds",
            "run_timeout_seconds",
            "max_retries",
            "concurrency",
            "max_calls",
            "max_input_tokens",
            "max_output_tokens",
            "max_rounds",
            "call_inventory_sha256",
        )
    }
    expected.update(
        **contract._budget_binding(config.full_run_reservation),
        max_usd="6.00",
        config_sha256=config.sha256,
        input_manifest_sha256=manifest.sha256,
        price_schedule_sha256=config.price_schedule.sha256,
        code_sha=manifest.code_sha,
        command_sha256=contract.command_fingerprint(command),
        consumed=False,
        run_id=parsed["run_id"],
        private_root=f"{contract.PRIVATE_PARENT}/{parsed['run_id']}",
    )
    if any(raw.get(key) != value for key, value in expected.items()):
        raise contract.GrantValidationError("fake authorization binding mismatch")
    if (
        not contract._parse_timestamp(raw["issued_at_utc"])
        <= now
        < contract._parse_timestamp(raw["expires_at_utc"])
    ):
        raise contract.GrantValidationError("fake authorization expired")


def evaluate_gate(
    *,
    mode: str,
    config: contract.ExecutionConfig,
    verification: Mapping[str, Any],
    input_manifest: contract.VerifiedInputManifest | None,
    grant: contract.ExecutionGrant | Mapping[str, Any] | None,
    current_commit: str,
    command: Sequence[str] = (),
    run_root: Path | None = None,
    now: datetime | None = None,
) -> Mapping[str, Any]:
    """Fail closed; only an exact execute claim can permit OpenAI construction.

    Verification is the fresh in-process Task 1 result, never persisted evidence.
    This function does not import providers or load credentials.
    """
    try:
        instant = now if now is not None else datetime.now(timezone.utc)
        contract._utc(instant)
        parsed = parse_complete_command(command)
        if parsed["mode"] != mode or parsed.get("private_root") != contract.PRIVATE_PARENT:
            raise contract.GrantValidationError("mode or output mismatch")
        contract.assert_safe_run_id(parsed["run_id"])
        if config.concurrency != 1 or config.max_retries != 0:
            raise contract.GrantValidationError("unsupported isolated-lane policy")
        # Pure full-run admission must precede durable attempt consumption below.
        contract.require_full_run_budget(config)
        paths = input_manifest.verification_inputs if input_manifest is not None else ()
        fresh = contract.build_input_manifest(
            verification=verification,
            config=config,
            code_sha=current_commit,
            verification_inputs=paths,
        )
        if mode == "prepare":
            return _Decision("PASS", mode)
        if type(input_manifest) is not contract.VerifiedInputManifest or fresh != input_manifest:
            raise contract.GrantValidationError("fresh manifest does not match")
        if mode == "preflight":
            _fake_authorization(grant, config, input_manifest, command, instant)
        elif mode == "execute":
            if isinstance(grant, Mapping):
                grant = contract.ExecutionGrant.from_dict(grant)
            contract.validate_execution_grant(
                grant,
                config=config,
                manifest=input_manifest,
                current_commit=current_commit,
                command=command,
                now=instant,
            )
        else:
            raise contract.GrantValidationError("unapproved mode")
        if run_root is None:
            raise contract.GrantValidationError("exclusive output required")
        check_run_root(run_root, parsed["run_id"])
        if any(run_root.iterdir()):
            raise contract.GrantValidationError("output already used")
        if globals()["current_commit"]() != current_commit:
            raise contract.GrantValidationError("current code changed")
        nonce = grant["nonce"] if isinstance(grant, Mapping) else grant.nonce
        invocation = grant["invocation_id"] if isinstance(grant, Mapping) else grant.invocation_id
        _claim_attempt(nonce, invocation)
        expires = (
            contract._parse_timestamp(grant["expires_at_utc"])
            if isinstance(grant, Mapping)
            else grant.expires_at_utc
        )
        permit = _Permit(
            _PERMISSION,
            expires,
            _invocation_digest(mode, config, input_manifest, command, run_root, grant),
        )
        return _Decision("PASS", mode, mode == "execute", _permission=permit)
    except contract.FullRunBudgetError:
        return _Decision("BLOCKED", mode, technical_error_code="BUDGET_EXCEEDED")
    except Exception:
        return _Decision("BLOCKED", mode, technical_error_code="GRANT_INVALID")


def require_execute_authorization(decision: Mapping[str, Any]) -> None:
    _require_mode_authorization(decision, "execute")


def _require_mode_authorization(decision: Mapping[str, Any], mode: str) -> None:
    if (
        type(decision) is not _Decision
        or type(decision._permission) is not _Permit
        or decision._permission.token is not _PERMISSION
        or mode not in {"execute", "preflight"}
        or decision.mode != mode
        or decision.status != "PASS"
        or decision.provider_construction_permitted != (mode == "execute")
    ):
        raise contract.GrantValidationError("execution is not authorized")
    permit = decision._permission
    with permit.lock:
        if permit.used or datetime.now(timezone.utc) >= permit.expires_at:
            raise contract.GrantValidationError("decision used or expired")
        permit.used = True


def authorize_invocation(decision, *, mode, config, manifest, command, run_root, grant):
    """Consume the exact bound in-process capability before even provider imports."""
    if type(decision) is not _Decision or type(decision._permission) is not _Permit:
        raise contract.GrantValidationError("no claimed invocation")
    if decision._permission.context_sha256 != _invocation_digest(
        mode, config, manifest, command, run_root, grant
    ):
        raise contract.GrantValidationError("invocation changed after claim")
    _require_mode_authorization(decision, mode)


def compose_receipt(
    *, config, manifest, mode, run_root, status, code="NONE", pipeline=None, ledger=None
):
    receipt = contract.build_receipt_skeleton(
        config=config, manifest=manifest, run_id=run_root.name, mode=mode
    )
    receipt.update(status=status, technical_error_code=code, containment_check="PASS")
    if pipeline is not None:
        receipt.update(
            {
                name: pipeline.receipt[name]
                for name in (
                    "status",
                    "technical_error_code",
                    "lifecycle_summary",
                    "scientific_result_count",
                    "detector_version",
                    "agent4_queue_status",
                )
            }
        )
        if contract.canonical_json_sha256(pipeline.call_inventory) != config.call_inventory_sha256:
            raise contract.ContractValidationError("pipeline inventory mismatch")
        for key, path in (
            ("event_log_sha256", pipeline.qa_events_path),
            ("pipeline_output_sha256", pipeline.manifest_path),
        ):
            if path.parent != run_root:
                raise contract.ContainmentError("pipeline artifact escaped")
            checked_input(path.relative_to(contract.REPOSITORY_ROOT).as_posix(), private=True)
            receipt[key] = hashlib.sha256(path.read_bytes()).hexdigest()
    if ledger is not None:
        value = ledger.to_dict()
        for key in (
            "physical_call_count",
            "external_provider_call_count",
            "input_token_count",
            "output_token_count",
        ):
            receipt[key] = value[key]
        cost_field = "simulated_spent_usd" if mode == "preflight" else "spent_usd"
        receipt[cost_field] = contract._decimal_string(ledger.spent_usd)
        receipt["reserved_usd"] = contract._decimal_string(ledger.reserved_usd)
        path = write_private(run_root, "ledger.json", value)
        receipt["ledger_sha256"] = hashlib.sha256(path.read_bytes()).hexdigest()
    return contract.parse_execution_receipt(receipt)
