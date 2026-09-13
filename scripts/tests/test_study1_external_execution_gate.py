"""Synthetic-only composition tests. Never execute the real-provider CLI mode."""

from __future__ import annotations

import builtins
import hashlib
import importlib
import json
import shutil
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from dataclasses import replace
from datetime import datetime, timedelta, timezone
from pathlib import Path
from types import SimpleNamespace

import pytest
from test_airtravel_execution_contract import config_data, full_budget_config
from test_verify_text2uml_airtravel_runtime import make_verified_inputs

contract = importlib.import_module("airtravel_execution_contract")
verifier = importlib.import_module("verify_text2uml_airtravel_runtime")
ROOT = Path(__file__).resolve().parents[2]


def modules():
    assert importlib.util.find_spec("study1_external_execution_gate") is not None, (
        "composition gate missing"
    )
    assert importlib.util.find_spec("study1_airtravel_external_runner") is not None, (
        "strict runner missing"
    )
    return (
        importlib.import_module("study1_external_execution_gate"),
        importlib.import_module("study1_airtravel_external_runner"),
    )


def test_composition_gate_and_strict_cli_are_available():
    modules()


@pytest.mark.parametrize("total,expected", [("6.00", "PASS"), ("6.01", "BLOCKED")])
def test_full_run_budget_gate_precedes_nonce_and_provider(workspace, monkeypatch, total, expected):
    gate, _, root, inputs, _, _ = workspace
    cfg = full_budget_config(total)
    evidence = verifier.verify_pack(**inputs)
    manifest = contract.build_input_manifest(
        verification=evidence, config=cfg, code_sha=gate.current_commit()
    )
    path = root / contract.PRIVATE_PARENT / "bound" / "input_manifest.json"
    command = command_for(workspace, "execute", path, "budget-gate")
    raw = grant_for(cfg, manifest, command)
    run_root = contract.assert_private_empty_run_root(Path(contract.PRIVATE_PARENT), "budget-gate")
    attempts = forbid_provider_imports(monkeypatch)
    result = gate.evaluate_gate(
        mode="execute", config=cfg, verification=evidence, input_manifest=manifest,
        grant=raw, current_commit=manifest.code_sha, command=command, run_root=run_root,
    )
    assert result["status"] == expected
    if expected == "BLOCKED":
        assert result["technical_error_code"] == "BUDGET_EXCEEDED"
    assert attempts == []
    assert (root / gate.CONTROL_PARENT).exists() is (expected == "PASS")


def test_full_execute_cli_unaffordable_has_zero_client_and_transport_attempts(workspace, monkeypatch):
    gate, runner, root, _, cfg_path, _ = workspace
    original, path = prepare_manifest(workspace)
    cfg = full_budget_config("6.01")
    manifest = replace(
        original, config_sha256=cfg.sha256, max_rounds=cfg.max_rounds,
        call_inventory_sha256=cfg.call_inventory_sha256,
        full_run_reservation=cfg.full_run_reservation,
    )
    write(cfg_path, cfg.to_dict())
    path = path.parent / "unaffordable_input_manifest.json"
    write(path, manifest.to_dict())
    command = command_for(workspace, "execute", path, "unaffordable")
    grant_path = root / command[command.index("--grant") + 1]
    write(grant_path, grant_for(cfg, manifest, command))
    attempts = forbid_provider_imports(monkeypatch)
    assert runner.main(command) == 2
    receipt = json.loads((root / contract.PRIVATE_PARENT / "unaffordable" / "receipt.json").read_text())
    assert receipt["status"] == "BLOCKED"
    assert receipt["technical_error_code"] == "BUDGET_EXCEEDED"
    assert receipt["physical_call_count"] == receipt["external_provider_call_count"] == 0
    assert receipt["full_run_reservation"]["full_run_usd"] == "6.01"
    assert not (root / gate.CONTROL_PARENT).exists()
    assert attempts == []


def test_untracked_qa_shadow_blocks_gate_and_is_never_imported(workspace):
    gate, _, root, _, _, _ = workspace
    marker = root / "shadow-executed.txt"
    shadow = root / "scripts" / "qa_communication.py"
    shadow.write_text(
        "from pathlib import Path\n"
        f"Path({str(marker)!r}).write_text('executed', encoding='utf-8')\n"
        "QACommunicationRecorder = QACommunicationValidationError = None\n"
        "build_episode_projection = load_event_stream = validate_event_stream = None\n",
        encoding="utf-8",
    )
    script = """
import sys
sys.path.insert(0, 'scripts')
try:
    import airtravel_execution_pipeline
except (ImportError, ValueError):
    print('BLOCKED')
else:
    print('IMPORTED')
"""
    result = subprocess.run(
        [sys.executable, "-c", script], cwd=root, capture_output=True, text=True
    )
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == "BLOCKED"
    assert not marker.exists(), "untracked QA shadow executed before rejection"
    with pytest.raises(contract.ContractValidationError):
        gate.current_commit()


@pytest.mark.parametrize(
    "relative,directory",
    [
        ("scripts/study1_external_execution_gate.py.", False),
        ("scripts/study1_external_execution_gate.py ", False),
        ("scripts./study1_external_execution_gate.py", False),
        ("scripts /study1_external_execution_gate.py", False),
        ("scripts.", True),
        ("scripts ", True),
    ],
)
def test_checked_input_rejects_windows_component_aliases(workspace, relative, directory):
    gate, _, _, _, _, _ = workspace
    with pytest.raises(contract.ContractValidationError):
        gate.checked_input(relative, directory=directory)


@pytest.mark.parametrize(
    "alias",
    ["inputs/config.json.", "inputs/config.json ", "inputs./config.json", "inputs /config.json"],
)
def test_private_input_alias_cannot_hide_a_tracked_canonical_target(workspace, alias):
    gate, _, root, _, cfg_path, _ = workspace
    canonical = cfg_path.relative_to(root).as_posix()
    git(root, "add", "--force", "--", canonical)
    with pytest.raises(contract.ContainmentError):
        gate.checked_input(canonical, private=True)
    with pytest.raises(contract.ContractValidationError):
        gate.checked_input(f"{contract.PRIVATE_PARENT}/{alias}", private=True)


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value), encoding="utf-8")


def git(root, *args):
    result = subprocess.run(
        ["git", "-C", str(root), *args], capture_output=True, text=True, check=True
    )
    return result.stdout.strip()


@pytest.fixture
def workspace(tmp_path, monkeypatch):
    gate, runner = modules()
    root = tmp_path / "repository"
    root.mkdir()
    git(root, "init", "--quiet")
    git(root, "config", "core.autocrlf", "false")
    (root / ".gitignore").write_text("external_data/\n", encoding="utf-8")
    for relative in gate.CODE_PATHS:
        target = root / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / relative, target)
    inputs = make_verified_inputs(root / "external_data" / "synthetic")
    amendment = root / "docs" / "synthetic-amendment.json"
    amendment.parent.mkdir(exist_ok=True)
    shutil.copyfile(inputs["amendment_manifest"], amendment)
    inputs["amendment_manifest"] = amendment
    git(root, "add", "--", ".")
    git(
        root,
        "-c",
        "user.name=Synthetic",
        "-c",
        "user.email=synthetic@example.invalid",
        "commit",
        "--quiet",
        "-m",
        "synthetic fixture",
    )
    monkeypatch.setattr(contract, "REPOSITORY_ROOT", root)
    actual_digest = verifier.sha256
    monkeypatch.setattr(
        verifier,
        "sha256",
        lambda path: (
            contract.PUBLIC_AIRTRAVEL_ARCHIVE_SHA256
            if path == inputs["archive"]
            else actual_digest(path)
        ),
    )
    private = root / contract.PRIVATE_PARENT
    cfg = private / "inputs" / "config.json"
    write(cfg, config_data())
    prepare = ["prepare", "--config", cfg.relative_to(root).as_posix()]
    for name, path in inputs.items():
        option = "amendment" if name == "amendment_manifest" else name.replace("_", "-")
        prepare += ["--" + option, path.relative_to(root).as_posix()]
    prepare += ["--private-root", contract.PRIVATE_PARENT, "--run-id", "prepared"]
    return gate, runner, root, inputs, cfg, prepare


def prepare_manifest(workspace):
    gate, runner, root, inputs, cfg, command = workspace
    assert runner.main(command) == 0
    path = root / contract.PRIVATE_PARENT / "prepared" / "input_manifest.json"
    return contract.VerifiedInputManifest.from_dict(json.loads(path.read_text())), path


def command_for(workspace, mode, manifest_path, run_id):
    _, _, root, _, cfg, _ = workspace
    result = [
        mode,
        "--config",
        cfg.relative_to(root).as_posix(),
        "--input-manifest",
        manifest_path.relative_to(root).as_posix(),
        "--private-root",
        contract.PRIVATE_PARENT,
        "--run-id",
        run_id,
    ]
    if mode == "execute":
        result += ["--grant", f"{contract.PRIVATE_PARENT}/inputs/grant.json"]
    return result


def grant_for(cfg, manifest, command, mode="execute"):
    now = datetime.now(timezone.utc)
    raw = {
        "schema_version": "airtravel-api-execution-grant-v1",
        "mode": "execute",
        "nonce": "c" * 64,
        "invocation_id": "b5cd2d0c-021c-4300-81cc-296d66b5bb17",
        "run_id": command[command.index("--run-id") + 1],
        "issued_at_utc": (now - timedelta(minutes=1)).isoformat().replace("+00:00", "Z"),
        "expires_at_utc": (now + timedelta(minutes=5)).isoformat().replace("+00:00", "Z"),
        "consumed": False,
        "code_sha": manifest.code_sha,
        "input_manifest_sha256": manifest.sha256,
        "config_sha256": cfg.sha256,
        "price_schedule_sha256": cfg.price_schedule.sha256,
        "command_sha256": contract.command_fingerprint(command),
    }
    for name in (
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
    ):
        raw[name] = getattr(cfg, name)
    raw["max_usd"] = "6.00"
    raw.update(contract._budget_binding(cfg.full_run_reservation))
    raw["private_root"] = f"{contract.PRIVATE_PARENT}/{raw['run_id']}"
    if mode == "preflight":
        raw["schema_version"] = "airtravel-local-fake-preflight-grant-v1"
        raw["mode"] = "preflight"
    return raw


def forbid_provider_imports(monkeypatch):
    original = builtins.__import__
    attempts = []

    class RecordingConstructor:
        def __init__(self, *args, **kwargs):
            attempts.append("constructor")

        @classmethod
        def construct_after_grant(cls, *args, **kwargs):
            attempts.append("construct_after_grant")
            return None

    blocked_module = SimpleNamespace(
        OpenAIProvider=RecordingConstructor,
        AsyncOpenAI=RecordingConstructor,
        BudgetLedger=RecordingConstructor,
        DeterministicFakeProvider=RecordingConstructor,
    )

    def guarded(name, *args, **kwargs):
        if name in {
            "openai",
            "httpx",
            "airtravel_execution_provider",
            "airtravel_execution_pipeline",
        }:
            attempts.append("import:" + name)
            return blocked_module
        return original(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", guarded)
    return attempts


def test_prepare_and_unauthorized_preflight_are_provider_free(workspace, monkeypatch, capsys):
    attempts = forbid_provider_imports(monkeypatch)
    _, runner, root, _, _, prepare = workspace
    manifest, path = prepare_manifest(workspace)
    assert manifest.max_rounds == 1
    assert runner.main(command_for(workspace, "preflight", path, "blocked-fake")) == 2
    receipt = json.loads(
        (root / contract.PRIVATE_PARENT / "blocked-fake" / "receipt.json").read_text()
    )
    assert receipt["status"] == "BLOCKED"
    assert receipt["external_provider_call_count"] == 0
    assert runner.main(prepare) == 2  # immutable/reused output is not overwritten
    for line in capsys.readouterr().out.splitlines():
        assert set(json.loads(line)) == {"status", "receipt_sha256"}
    assert attempts == []


def test_authorized_fake_preflight_has_full_hash_bound_zero_external_receipt(workspace):
    gate, runner, root, _, cfg_path, _ = workspace
    manifest, path = prepare_manifest(workspace)
    command = command_for(workspace, "preflight", path, "fake-allowed")
    cfg = contract.ExecutionConfig.from_json(cfg_path)
    write(
        path.parent / "fake_preflight_authorization.json",
        grant_for(cfg, manifest, command, "preflight"),
    )
    assert runner.main(command) == 0
    output = root / contract.PRIVATE_PARENT / "fake-allowed"
    receipt = contract.parse_execution_receipt(json.loads((output / "receipt.json").read_text()))
    assert receipt["physical_call_count"] == 16
    assert receipt["external_provider_call_count"] == 0
    assert receipt["call_inventory_sha256"] == cfg.call_inventory_sha256
    assert receipt["input_token_count"] == 160
    for field, filename in (
        ("ledger_sha256", "ledger.json"),
        ("event_log_sha256", "qa_events.jsonl"),
        ("pipeline_output_sha256", "pipeline_manifest.json"),
    ):
        assert receipt[field] == hashlib.sha256((output / filename).read_bytes()).hexdigest()
    assert receipt["scientific_result_count"] == 0
    assert receipt["spent_usd"] == "0.00"
    assert receipt["cost_basis"] == "LOCAL_FAKE_SIMULATION"
    assert receipt["simulated_spent_usd"] != "0.00"


@pytest.mark.parametrize(
    "change",
    [
        "missing",
        "expired",
        "replayed",
        "wrong_manifest",
        "wrong_command",
        "wrong_inventory",
        "wrong_code",
        "wrong_mode",
        "wrong_host",
        "wrong_model",
        "wrong_cap",
        "bad_verification",
    ],
)
def test_execute_gate_denies_before_provider_import(workspace, monkeypatch, change):
    gate, _, root, inputs, cfg_path, _ = workspace
    manifest, path = prepare_manifest(workspace)
    cfg = contract.ExecutionConfig.from_json(cfg_path)
    command = command_for(workspace, "execute", path, "execute-gate")
    baseline = grant_for(cfg, manifest, command)
    raw = dict(baseline)
    evidence = verifier.verify_pack(**inputs)
    run_root = contract.assert_private_empty_run_root(Path(contract.PRIVATE_PARENT), "execute-gate")
    args = dict(
        mode="execute",
        config=cfg,
        verification=evidence,
        input_manifest=manifest,
        grant=raw,
        current_commit=manifest.code_sha,
        command=command,
        run_root=run_root,
    )
    # Establish that every unmodified grant binding is valid before testing the
    # single changed binding. The positive counterfactual below also exercises
    # the actual exclusive-root/code/marker path, without constructing a provider.
    contract.validate_execution_grant(
        contract.ExecutionGrant.from_dict(baseline),
        config=cfg,
        manifest=manifest,
        current_commit=manifest.code_sha,
        command=command,
    )
    attempts = forbid_provider_imports(monkeypatch)
    if change == "replayed":
        assert gate.evaluate_gate(**args)["provider_construction_permitted"] is True
    if change == "expired":
        raw["expires_at_utc"] = (
            (datetime.now(timezone.utc) - timedelta(seconds=1)).isoformat().replace("+00:00", "Z")
        )
    if change == "wrong_manifest":
        raw["input_manifest_sha256"] = "f" * 64
    if change == "wrong_command":
        raw["command_sha256"] = "f" * 64
    if change == "wrong_inventory":
        raw["max_rounds"] = 2
    if change == "wrong_code":
        raw["code_sha"] = "f" * 40
    if change == "wrong_mode":
        raw["mode"] = "preflight"
    if change == "wrong_host":
        raw["provider_host"] = "unauthorized.example.invalid"
    if change == "wrong_model":
        raw["model"] = "other-synthetic-model"
    if change == "wrong_cap":
        raw["max_calls"] = cfg.max_calls + 1
    if change == "bad_verification":
        evidence["status"] = "BLOCKED"
    if change == "missing":
        args["grant"] = None
    decision = gate.evaluate_gate(**args)
    assert decision["status"] == "BLOCKED"
    assert decision["technical_error_code"] == "GRANT_INVALID"
    assert decision["provider_construction_permitted"] is False
    with pytest.raises(contract.GrantValidationError):
        gate.require_execute_authorization(decision)
    assert attempts == []
    if change != "replayed":
        assert not (root / gate.CONTROL_PARENT).exists(), (
            "rejection reached authorization consumption"
        )
        # Revert only the changed binding (including derived verifier status).
        evidence["status"] = "PASS"
        corrected = gate.evaluate_gate(**dict(args, grant=baseline))
        assert corrected["status"] == "PASS", "fixture failed for an unrelated reason"
        assert corrected["provider_construction_permitted"] is True
    assert attempts == []


def test_exclusive_durable_attempt_survives_output_deletion_and_races(workspace):
    gate, _, root, inputs, cfg_path, _ = workspace
    manifest, path = prepare_manifest(workspace)
    cfg = contract.ExecutionConfig.from_json(cfg_path)
    command = command_for(workspace, "execute", path, "claim-only")
    raw = grant_for(cfg, manifest, command)
    run_root = contract.assert_private_empty_run_root(Path(contract.PRIVATE_PARENT), "claim-only")
    args = dict(
        mode="execute",
        config=cfg,
        verification=verifier.verify_pack(**inputs),
        input_manifest=manifest,
        grant=raw,
        current_commit=manifest.code_sha,
        command=command,
        run_root=run_root,
    )
    with ThreadPoolExecutor(max_workers=2) as pool:
        decisions = list(pool.map(lambda _: gate.evaluate_gate(**args), range(2)))
    assert sorted(row["provider_construction_permitted"] for row in decisions) == [False, True]
    allowed = next(row for row in decisions if row["provider_construction_permitted"])
    gate.require_execute_authorization(allowed)
    with pytest.raises(contract.GrantValidationError):
        gate.require_execute_authorization(allowed)
    with pytest.raises(contract.GrantValidationError):
        gate.require_execute_authorization(dict(allowed))
    shutil.rmtree(run_root)
    run_root.mkdir()
    assert gate.evaluate_gate(**args)["status"] == "BLOCKED"
    markers = list((root / "external_data" / "airtravel-api-control").glob("*.attempt"))
    assert len(markers) == 2
    assert all(
        raw["nonce"] not in item.read_text() and "test-model" not in item.read_text()
        for item in markers
    )


@pytest.mark.parametrize("obstruction", ["file", "tracked", "symlink"])
def test_durable_control_root_rejects_unsafe_or_nonprivate_storage(workspace, obstruction):
    gate, _, root, _, _, _ = workspace
    control = root / "external_data" / "airtravel-api-control"
    if obstruction == "file":
        control.write_text("synthetic obstruction", encoding="utf-8")
    elif obstruction == "tracked":
        control.mkdir()
        (control / "tracked.txt").write_text("synthetic tracked control", encoding="utf-8")
        git(root, "add", "--force", "--", "external_data/airtravel-api-control/tracked.txt")
    else:
        target = root / "external_data" / "synthetic-target"
        target.mkdir()
        try:
            control.symlink_to(target, target_is_directory=True)
        except OSError:
            pytest.skip("symlink creation unavailable on this host")
    with pytest.raises((contract.ContractValidationError, OSError)):
        gate._claim_attempt("c" * 64, "b5cd2d0c-021c-4300-81cc-296d66b5bb17")
    assert not list((root / ".git").rglob("*.attempt"))
    assert not list((root / "external_data" / "synthetic-target").glob("*.attempt"))


@pytest.mark.parametrize(
    "suffix",
    [
        ["--config=private"],
        ["--run", "x"],
        ["--", "x"],
        ["--run-id", "x"],
        ["--grant", "x"],
        ["--run-id", "-x"],
    ],
)
def test_cli_rejects_noncanonical_options_without_creating_output(workspace, suffix):
    _, runner, root, _, _, command = workspace
    assert runner.main([*command, *suffix]) == 2
    assert not (root / contract.PRIVATE_PARENT / "prepared").exists()


@pytest.mark.parametrize(
    "value",
    ["../escape", "/tmp/escape", "C:/escape", "external_data/airtravel-api-runs/../elsewhere"],
)
def test_cli_rejects_path_escape(workspace, value):
    _, runner, root, _, _, command = workspace
    command[command.index("--private-root") + 1] = value
    assert runner.main(command) == 2
    assert not (root / contract.PRIVATE_PARENT / "prepared").exists()


def test_fresh_source_verification_and_dirty_code_block_fake_preflight(workspace):
    _, runner, root, inputs, cfg_path, _ = workspace
    manifest, path = prepare_manifest(workspace)
    command = command_for(workspace, "preflight", path, "changed-input")
    cfg = contract.ExecutionConfig.from_json(cfg_path)
    write(
        path.parent / "fake_preflight_authorization.json",
        grant_for(cfg, manifest, command, "preflight"),
    )
    target = next((inputs["runtime_root"] / "candidate_models").iterdir())
    target.write_text("Synthetic changed bytes.", encoding="utf-8")
    assert runner.main(command) == 2
    (root / "scripts" / "airtravel_execution_contract.py").write_text("# changed", encoding="utf-8")
    command[command.index("--run-id") + 1] = "changed-code"
    assert runner.main(command) == 2


def test_runner_import_does_not_import_provider_or_network_modules():
    script = """
import builtins, sys
from types import SimpleNamespace
sys.path.insert(0, 'scripts')
real = builtins.__import__
attempts = []
class RecordingConstructor:
    def __init__(self, *args, **kwargs):
        attempts.append('constructor')
    @classmethod
    def construct_after_grant(cls, *args, **kwargs):
        attempts.append('construct_after_grant')
stub = SimpleNamespace(OpenAIProvider=RecordingConstructor, AsyncOpenAI=RecordingConstructor)
def guarded(name, *args, **kwargs):
    if name in {'openai','httpx','airtravel_execution_provider','airtravel_execution_pipeline'}:
        attempts.append('import:' + name)
        return stub
    return real(name, *args, **kwargs)
builtins.__import__ = guarded
import study1_airtravel_external_runner
assert study1_airtravel_external_runner.main(['prepare', '--config=x']) == 2
assert attempts == [], attempts
"""
    result = subprocess.run(
        [sys.executable, "-c", script], cwd=ROOT, capture_output=True, text=True
    )
    assert result.returncode == 0, result.stderr


@pytest.mark.parametrize(
    "relative,hidden",
    [
        ("scripts/airtravel_execution_contract.py", True),
        ("schemas/qa-communication-event-v1.schema.json", False),
    ],
)
def test_code_check_detects_unstaged_bytes_even_if_git_index_hides_them(
    workspace, relative, hidden
):
    gate, _, root, _, _, _ = workspace
    path = root / relative
    if not path.exists():
        path.parent.mkdir(exist_ok=True)
        path.write_text("{}", encoding="utf-8")
        git(root, "add", "--", relative)
        git(
            root,
            "-c",
            "user.name=Synthetic",
            "-c",
            "user.email=synthetic@example.invalid",
            "commit",
            "--quiet",
            "-m",
            "schema fixture",
        )
    if hidden:
        git(root, "update-index", "--assume-unchanged", "--", relative)
    path.write_text("changed synthetic bytes", encoding="utf-8")
    with pytest.raises(contract.ContractValidationError):
        gate.current_commit()


def test_gate_rejects_incomplete_command_before_claim(workspace):
    gate, _, root, inputs, cfg_path, _ = workspace
    manifest, path = prepare_manifest(workspace)
    cfg = contract.ExecutionConfig.from_json(cfg_path)
    command = command_for(workspace, "execute", path, "incomplete-command")
    del command[1:3]  # --config and value must not be optional at the gate.
    raw = grant_for(cfg, manifest, command)
    run_root = contract.assert_private_empty_run_root(
        Path(contract.PRIVATE_PARENT), "incomplete-command"
    )
    result = gate.evaluate_gate(
        mode="execute",
        config=cfg,
        verification=verifier.verify_pack(**inputs),
        input_manifest=manifest,
        grant=raw,
        current_commit=manifest.code_sha,
        command=command,
        run_root=run_root,
    )
    assert result["status"] == "BLOCKED"
    assert not (root / "external_data" / "airtravel-api-control").exists()


def test_config_mismatch_still_writes_sanitized_terminal_receipt(workspace):
    _, runner, root, _, cfg_path, _ = workspace
    manifest, path = prepare_manifest(workspace)
    command = command_for(workspace, "preflight", path, "mismatched-config")
    cfg = contract.ExecutionConfig.from_json(cfg_path)
    write(
        path.parent / "fake_preflight_authorization.json",
        grant_for(cfg, manifest, command, "preflight"),
    )
    write(cfg_path, replace(cfg, model="different-test-model").to_dict())
    assert runner.main(command) == 2
    receipt = json.loads(
        (root / contract.PRIVATE_PARENT / "mismatched-config" / "receipt.json").read_text()
    )
    assert receipt["status"] == "BLOCKED"
    assert receipt["external_provider_call_count"] == 0
    assert "different-test-model" not in json.dumps(receipt)


def test_private_async_entry_requires_auth_even_for_fake_mode(monkeypatch):
    import asyncio

    _, runner = modules()
    attempts = forbid_provider_imports(monkeypatch)
    with pytest.raises(contract.GrantValidationError):
        asyncio.run(
            runner._run(
                mode="preflight",
                config=None,
                manifest=None,
                paths=None,
                root=None,
                decision={"status": "PASS", "mode": "preflight"},
                grant=None,
                command=[],
                ledger=None,
            )
        )
    assert attempts == []


def test_failure_after_fake_authorization_persists_sanitized_receipt(
    workspace, monkeypatch, capsys
):
    _, runner, root, _, cfg_path, _ = workspace
    manifest, path = prepare_manifest(workspace)
    cfg = contract.ExecutionConfig.from_json(cfg_path)
    command = command_for(workspace, "preflight", path, "fake-failure")
    write(
        path.parent / "fake_preflight_authorization.json",
        grant_for(cfg, manifest, command, "preflight"),
    )

    def broken_frame(*args):
        raise ValueError("SYNTHETIC_SECRET_PROMPT_EXCEPTION")

    monkeypatch.setattr(runner, "_frame", broken_frame)
    assert runner.main(command) == 2
    output = root / contract.PRIVATE_PARENT / "fake-failure"
    receipt = json.loads((output / "receipt.json").read_text())
    assert receipt["status"] == "INCOMPLETE_TECHNICAL"
    assert receipt["technical_error_code"] == "INTERNAL_FAILURE"
    assert receipt["external_provider_call_count"] == 0
    assert receipt["ledger_sha256"] is not None
    assert "SYNTHETIC_SECRET" not in capsys.readouterr().out + json.dumps(receipt)


def test_consumed_capability_binds_the_exact_grant(workspace):
    gate, _, _, inputs, cfg_path, _ = workspace
    manifest, path = prepare_manifest(workspace)
    cfg = contract.ExecutionConfig.from_json(cfg_path)
    command = command_for(workspace, "execute", path, "bound-grant")
    raw = grant_for(cfg, manifest, command)
    root = contract.assert_private_empty_run_root(Path(contract.PRIVATE_PARENT), "bound-grant")
    decision = gate.evaluate_gate(
        mode="execute",
        config=cfg,
        verification=verifier.verify_pack(**inputs),
        input_manifest=manifest,
        grant=raw,
        current_commit=manifest.code_sha,
        command=command,
        run_root=root,
    )
    assert decision["provider_construction_permitted"] is True
    with pytest.raises(contract.GrantValidationError):
        gate.authorize_invocation(
            decision,
            mode="execute",
            config=cfg,
            manifest=manifest,
            command=command,
            run_root=root,
            grant=dict(raw, nonce="d" * 64),
        )


def test_prepare_rejects_inventory_over_cap_with_other_bindings_valid(workspace):
    _, runner, root, _, cfg_path, command = workspace
    cfg = contract.ExecutionConfig.from_json(cfg_path)
    write(cfg_path, replace(cfg, max_calls=16).to_dict())
    assert runner.main(command) == 2
    output = root / contract.PRIVATE_PARENT / "prepared"
    assert not (output / "input_manifest.json").exists()
    assert json.loads((output / "receipt.json").read_text())["status"] == "BLOCKED"


def test_receipt_composition_failure_keeps_terminal_call_counts(workspace, monkeypatch):
    gate, runner, root, _, cfg_path, _ = workspace
    manifest, path = prepare_manifest(workspace)
    cfg = contract.ExecutionConfig.from_json(cfg_path)
    command = command_for(workspace, "preflight", path, "receipt-failure")
    write(
        path.parent / "fake_preflight_authorization.json",
        grant_for(cfg, manifest, command, "preflight"),
    )

    def fail_composition(**kwargs):
        raise ValueError("synthetic unsafe exception text")

    monkeypatch.setattr(gate, "compose_receipt", fail_composition)
    assert runner.main(command) == 2
    output = root / contract.PRIVATE_PARENT / "receipt-failure" / "receipt.json"
    assert output.exists(), "safe terminal receipt missing after composition failure"
    receipt = json.loads(output.read_text())
    assert receipt["status"] == "INCOMPLETE_TECHNICAL"
    assert receipt["physical_call_count"] == 16
    assert receipt["external_provider_call_count"] == 0
    assert "unsafe exception" not in json.dumps(receipt)
