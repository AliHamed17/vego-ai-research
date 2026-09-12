"""Synthetic, local-only execution contract tests; no grant/config artifacts are tracked."""

from __future__ import annotations

import hashlib
import importlib
import json
import os
import stat
import subprocess
import sys
from dataclasses import FrozenInstanceError, replace
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path
from types import SimpleNamespace

import pytest
from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
contract = importlib.import_module("airtravel_execution_contract")
NOW = datetime(2026, 9, 13, 12, tzinfo=timezone.utc)
COMMIT = "a" * 40
ARCHIVE = "8cf82e2ab2d2ce3da9a7ec4165e760ae1e0d9af14468f5aa2a3883037d8da701"
UPSTREAM = "253b26dc704d523209a5cba79686f8f7fab57d63"
COMMAND = [
    "python",
    "runner.py",
    "execute",
    "--private-root",
    "external_data/airtravel-api-runs",
    "--run-id",
    "run-001",
]


def config_data() -> dict:
    return {
        "schema_version": "airtravel-api-execution-config-v1",
        "model": "test-model",
        "provider_host": "api.openai.com",
        "max_usd": "6.00",
        "timeout_seconds": 30,
        "run_timeout_seconds": 900,
        "max_retries": 0,
        "concurrency": 1,
        "max_calls": 16,
        "max_input_tokens": 10000,
        "max_output_tokens": 2000,
        "price_schedule": {
            "source": "https://openai.com/api/pricing/",
            "checked_at_utc": "2026-09-13T11:00:00Z",
            "input_usd_per_million_tokens": "0.15",
            "output_usd_per_million_tokens": "0.60",
        },
    }


def verification_data() -> dict:
    paths = ["domain_description/description.md"] + [
        f"candidate_models/{i:02d}.txt" for i in range(1, 5)
    ]
    inventory = [
        {"path": path, "bytes": i + 1, "sha256": hashlib.sha256(path.encode()).hexdigest()}
        for i, path in enumerate(paths)
    ]
    inventory += [
        {"path": f"source_only/{i}.txt", "bytes": 1, "sha256": "b" * 64} for i in range(138)
    ]
    return {
        "status": "PASS",
        "provider_call_made": False,
        "source_archive": {
            "status": "PASS",
            "expected_sha256": ARCHIVE,
            "declared_sha256": ARCHIVE,
            "actual_sha256": ARCHIVE,
            "expected_commit": UPSTREAM,
            "declared_commit": UPSTREAM,
            "commit_binding": True,
            "inventory_matches_manifest": True,
            "member_inventory": inventory,
            "duplicate_members": [],
            "invalid_members": [],
        },
        "source_entries": {
            "status": "PASS",
            "expected_count": 143,
            "observed_count": 143,
            "matched": 143,
            "unsafe_paths": [],
            "manifest_errors": [],
        },
        "source_to_runtime": {
            "status": "PASS",
            "byte_identical": True,
            "mapping_count": 5,
            "errors": [],
            "mappings": [{"source_path": p, "path": p, "byte_identical": True} for p in paths],
        },
        "runtime_pack": {
            "status": "PASS",
            "expected_count": 5,
            "observed_count": 5,
            "unsafe_paths": [],
            "manifest_errors": [],
            "allowed_configuration": True,
            "amendment_identity": True,
        },
        "reference_separation": {"status": "PASS", "reference_count": 1, "leaked_paths": []},
    }


def bindings():
    config = contract.ExecutionConfig.from_dict(config_data())
    manifest = contract.build_input_manifest(
        verification=verification_data(), config=config, code_sha=COMMIT
    )
    grant = {
        "schema_version": "airtravel-api-execution-grant-v1",
        "mode": "execute",
        "nonce": "c" * 64,
        "invocation_id": "b5cd2d0c-021c-4300-81cc-296d66b5bb17",
        "run_id": "run-001",
        "issued_at_utc": "2026-09-13T11:59:00Z",
        "expires_at_utc": "2026-09-13T12:05:00Z",
        "consumed": False,
        "code_sha": COMMIT,
        "input_manifest_sha256": manifest.sha256,
        "config_sha256": config.sha256,
        "model": config.model,
        "provider_host": config.provider_host,
        "price_schedule_sha256": config.price_schedule.sha256,
        "timeout_seconds": config.timeout_seconds,
        "run_timeout_seconds": config.run_timeout_seconds,
        "max_retries": config.max_retries,
        "concurrency": config.concurrency,
        "max_calls": config.max_calls,
        "max_input_tokens": config.max_input_tokens,
        "max_output_tokens": config.max_output_tokens,
        "max_usd": "6.00",
        "command_sha256": contract.command_fingerprint(COMMAND),
        "private_root": "external_data/airtravel-api-runs/run-001",
    }
    return config, manifest, grant


def validator(kind: str):
    schema = json.loads(
        (ROOT / "schemas" / f"airtravel-api-execution-{kind}-v1.schema.json").read_text()
    )
    Draft202012Validator.check_schema(schema)
    return Draft202012Validator(schema, format_checker=FormatChecker())


def validate(grant, config=None, manifest=None, **kwargs):
    base_config, base_manifest, _ = bindings()
    return contract.validate_execution_grant(
        grant,
        config=config or base_config,
        manifest=manifest or base_manifest,
        current_commit=kwargs.pop("current_commit", COMMIT),
        command=kwargs.pop("command", COMMAND),
        now=kwargs.pop("now", NOW),
        **kwargs,
    )


def test_canonical_hash_is_order_independent_and_decimal_exact():
    value = {"b": Decimal("6.00"), "a": 1}
    expected = hashlib.sha256(b'{"a":1,"b":"6.00"}').hexdigest()
    assert contract.canonical_json_sha256(value) == expected
    assert contract.canonical_json_sha256({"a": 1, "b": Decimal("6")}) == expected


@pytest.mark.parametrize("value", [1.2, float("nan"), Decimal("NaN"), {1: "bad"}, {"x": object()}])
def test_canonical_hash_rejects_ambiguous_or_non_json_values(value):
    with pytest.raises(contract.ContractValidationError):
        contract.canonical_json_sha256({"value": value})


def test_config_roundtrip_freezes_nested_prices_and_uses_decimal():
    raw = config_data()
    config = contract.ExecutionConfig.from_dict(raw)
    raw["price_schedule"]["input_usd_per_million_tokens"] = "999.00"
    assert config.max_usd == Decimal("6.00") and isinstance(config.max_usd, Decimal)
    assert config.price_schedule.input_usd_per_million_tokens == Decimal("0.15")
    assert config.to_dict() == config_data()
    with pytest.raises(FrozenInstanceError):
        config.price_schedule.source = "changed"
    validator("config").validate(config.to_dict())


@pytest.mark.parametrize(
    ("key", "value"),
    [
        ("max_usd", "6.01"),
        ("max_usd", "5.99"),
        ("max_usd", 6.0),
        ("max_usd", "6"),
        ("provider_host", "api.openai.com.evil.test"),
        ("provider_host", "https://api.openai.com"),
        ("provider_host", "127.0.0.1"),
        ("concurrency", 0),
        ("concurrency", True),
        ("max_retries", -1),
        ("max_calls", 0),
        ("max_output_tokens", 0),
        ("model", ""),
        ("unexpected", "private content"),
    ],
)
def test_config_schema_and_parser_reject_invalid_boundaries(key, value):
    raw = config_data()
    raw[key] = value
    assert list(validator("config").iter_errors(raw))
    with pytest.raises(contract.ContractValidationError):
        contract.ExecutionConfig.from_dict(raw)


def test_json_loader_rejects_duplicate_keys_and_missing_file(tmp_path):
    path = tmp_path / "private.json"
    with pytest.raises(contract.ContractValidationError):
        contract.ExecutionConfig.from_json(path)
    path.write_text('{"model":"one","model":"two"}', encoding="utf-8")
    with pytest.raises(contract.ContractValidationError):
        contract.ExecutionConfig.from_json(path)
    path.write_text(json.dumps(config_data()), encoding="utf-8")
    assert contract.ExecutionConfig.from_json(path).to_dict() == config_data()


def test_manifest_binds_full_verification_five_hashes_config_and_code():
    config, manifest, _ = bindings()
    assert len(manifest.runtime_files) == 5
    rows = {row.path: row for row in manifest.runtime_files}
    row = rows["domain_description/description.md"]
    assert row.bytes == 1
    assert row.sha256 == hashlib.sha256(b"domain_description/description.md").hexdigest()
    assert manifest.verification_sha256 == contract.canonical_json_sha256(verification_data())
    assert manifest.config_sha256 == config.sha256
    assert manifest.code_sha == COMMIT
    assert manifest.source_archive_sha256 == ARCHIVE
    assert contract.VerifiedInputManifest.from_dict(manifest.to_dict()) == manifest
    raw = verification_data()
    raw["reference_separation"]["reference_count"] = 2
    changed = contract.build_input_manifest(verification=raw, config=config, code_sha=COMMIT)
    assert changed.sha256 != manifest.sha256
    with pytest.raises(FrozenInstanceError):
        manifest.runtime_files[0].path = "changed"


@pytest.mark.parametrize(
    "mutation",
    [
        "blocked",
        "missing_check",
        "provider_called",
        "missing_hash",
        "missing_bytes",
        "missing_source",
        "duplicate_runtime",
        "bad_mapping",
        "missing_mapping",
        "wrong_archive",
        "wrong_commit",
        "false_reference",
        "missing_evidence",
        "bool_bytes",
    ],
)
def test_manifest_rejects_incomplete_or_failed_verifier_evidence(mutation):
    raw = verification_data()
    if mutation == "blocked":
        raw["status"] = "BLOCKED"
    elif mutation == "missing_check":
        del raw["source_entries"]
    elif mutation == "provider_called":
        raw["provider_call_made"] = True
    elif mutation in ("missing_hash", "missing_bytes"):
        del raw["source_archive"]["member_inventory"][0][
            "sha256" if mutation == "missing_hash" else "bytes"
        ]
    elif mutation == "missing_source":
        raw["source_to_runtime"]["mappings"][0]["source_path"] = "missing.txt"
    elif mutation == "duplicate_runtime":
        raw["source_to_runtime"]["mappings"][0]["path"] = raw["source_to_runtime"]["mappings"][1][
            "path"
        ]
    elif mutation == "bad_mapping":
        raw["source_to_runtime"]["mappings"][0]["byte_identical"] = False
    elif mutation == "missing_mapping":
        raw["source_to_runtime"]["mappings"].pop()
    elif mutation == "wrong_archive":
        raw["source_archive"]["actual_sha256"] = "f" * 64
    elif mutation == "wrong_commit":
        raw["source_archive"]["expected_commit"] = "f" * 40
    elif mutation == "false_reference":
        raw["reference_separation"]["leaked_paths"] = ["reference.txt"]
    elif mutation == "missing_evidence":
        del raw["runtime_pack"]["amendment_identity"]
    else:
        raw["source_archive"]["member_inventory"][0]["bytes"] = True
    with pytest.raises(contract.ContractValidationError):
        contract.build_input_manifest(
            verification=raw,
            config=contract.ExecutionConfig.from_dict(config_data()),
            code_sha=COMMIT,
        )


def test_grant_binds_config_manifest_and_commit_without_consuming():
    config, manifest, raw = bindings()
    validator("grant").validate(raw)
    grant = contract.ExecutionGrant.from_dict(raw)
    validate(grant)
    assert grant.consumed is False
    assert grant.to_dict() == raw
    with pytest.raises(contract.GrantValidationError, match="configuration hash"):
        validate(grant, config=replace(config, concurrency=2))
    with pytest.raises(contract.GrantValidationError):
        validate(grant, manifest=replace(manifest, verification_sha256="d" * 64))
    with pytest.raises(contract.GrantValidationError):
        validate(grant, current_commit="b" * 40)


@pytest.mark.parametrize(
    ("key", "value"),
    [
        ("mode", "preflight"),
        ("provider_host", "evil.test"),
        ("model", "other-model"),
        ("consumed", True),
        ("max_usd", "6.01"),
        ("max_calls", 17),
        ("max_retries", 1),
        ("max_input_tokens", 9999),
        ("max_output_tokens", 999),
        ("timeout_seconds", 29),
        ("run_timeout_seconds", 899),
        ("concurrency", 2),
        ("price_schedule_sha256", "f" * 64),
        ("private_root", "external_data/airtravel-api-runs/run-002"),
        ("private_root", "external_data/airtravel-api-runs-evil/run-001"),
        ("issued_at_utc", "2026-09-13T12:01:00Z"),
        ("expires_at_utc", "2026-09-13T12:00:00Z"),
        ("expires_at_utc", "2026-09-13T13:00:00+01:00"),
        ("expires_at_utc", "2026-09-13T13:00:00"),
        ("nonce", ""),
        ("invocation_id", "not-a-uuid"),
        ("extra", "exception private text"),
    ],
)
def test_grant_rejects_wrong_binding_or_invalid_schema(key, value):
    _, _, raw = bindings()
    raw[key] = value
    with pytest.raises(contract.GrantValidationError):
        validate(contract.ExecutionGrant.from_dict(raw))


def test_missing_grant_field_or_file_blocks(tmp_path):
    with pytest.raises(contract.GrantValidationError):
        validate(None)
    with pytest.raises(contract.GrantValidationError):
        contract.ExecutionGrant.from_json(tmp_path / "missing.json")
    _, _, raw = bindings()
    for field in raw:
        incomplete = {k: v for k, v in raw.items() if k != field}
        assert list(validator("grant").iter_errors(incomplete))
        with pytest.raises(contract.GrantValidationError):
            contract.ExecutionGrant.from_dict(incomplete)


def test_wrong_command_mode_root_run_id_and_naive_clock_block():
    _, _, raw = bindings()
    grant = contract.ExecutionGrant.from_dict(raw)
    for command in (
        COMMAND + ["--extra"],
        COMMAND[:-1] + ["run-002"],
        ["execute"],
        ["python", "runner.py", "preflight", *COMMAND[3:]],
    ):
        with pytest.raises(contract.GrantValidationError):
            validate(grant, command=command)
    with pytest.raises(contract.GrantValidationError):
        validate(grant, mode="preflight")
    with pytest.raises(contract.GrantValidationError):
        validate(grant, now=NOW.replace(tzinfo=None))
    # Even a re-fingerprinted grant cannot call the preflight command or redirect output.
    for command in (
        ["preflight", *COMMAND[3:]],
        COMMAND[:-1] + ["run-002"],
        ["execute", "--private-root", "../sibling", "--run-id", "run-001"],
    ):
        raw["command_sha256"] = contract.command_fingerprint(command)
        with pytest.raises(contract.GrantValidationError):
            validate(contract.ExecutionGrant.from_dict(raw), command=command)


def test_command_fingerprint_preserves_every_argument_and_boundary():
    assert contract.command_fingerprint(["a", "b c"]) != contract.command_fingerprint(["a b", "c"])
    assert contract.command_fingerprint(["a", " b "]) != contract.command_fingerprint(["a", "b"])
    for bad in ("execute", [], ["execute", ""], ["execute", "x\0y"], ["execute", 1]):
        with pytest.raises(contract.ContractValidationError):
            contract.command_fingerprint(bad)


@pytest.fixture
def private_repo(tmp_path, monkeypatch):
    subprocess.run(["git", "init", "--quiet", str(tmp_path)], check=True)
    (tmp_path / ".gitignore").write_text("external_data/**\n", encoding="utf-8")
    monkeypatch.setattr(contract, "REPOSITORY_ROOT", tmp_path)
    return tmp_path / "external_data" / "airtravel-api-runs"


@pytest.mark.parametrize(
    "run_id",
    [
        "",
        "../x",
        "C:/outside",
        "C:outside",
        "/tmp/x",
        "run/child",
        "run\\child",
        "run-001 ",
        ".",
        "..",
        "RUN-001",
        "con",
        "nul",
        "aux",
        "com1",
        "lpt9",
        "run.001",
        "run:001",
        "run-ä",
        "a" * 65,
    ],
)
def test_safe_run_id_rejects_cross_platform_escapes_and_collisions(run_id):
    with pytest.raises(contract.ContainmentError):
        contract.assert_safe_run_id(run_id)


def test_private_root_creates_only_approved_empty_ignored_directory_and_rejects_reuse(private_repo):
    root = contract.assert_private_empty_run_root(private_repo, "run-001")
    assert root == private_repo / "run-001" and list(root.iterdir()) == []
    with pytest.raises(contract.ContainmentError):
        contract.assert_private_empty_run_root(private_repo, "run-001")
    (root / "receipt.json").write_text("{}", encoding="utf-8")
    with pytest.raises(contract.ContainmentError):
        contract.assert_private_empty_run_root(private_repo, "run-001")


def test_private_root_rejects_sibling_traversal_nonignored_and_casefold(private_repo):
    for bad in (
        private_repo.with_name("airtravel-api-runs-evil"),
        private_repo.parent.parent,
        private_repo / ".." / "airtravel-api-runs",
        Path("../external_data/airtravel-api-runs"),
    ):
        with pytest.raises(contract.ContainmentError):
            contract.assert_private_empty_run_root(bad, "run-001")
    (private_repo.parents[1] / ".gitignore").write_text("", encoding="utf-8")
    with pytest.raises(contract.ContainmentError):
        contract.assert_private_empty_run_root(private_repo, "run-001")
    (private_repo.parents[1] / ".gitignore").write_text("external_data/**\n", encoding="utf-8")
    private_repo.mkdir(parents=True, exist_ok=True)
    (private_repo / "RUN-001").mkdir()
    with pytest.raises(contract.ContainmentError):
        contract.assert_private_empty_run_root(private_repo, "run-001")


def test_private_root_rejects_symlink_or_real_windows_junction(private_repo, tmp_path):
    target = tmp_path / "outside"
    target.mkdir()
    private_repo.parent.mkdir()
    if os.name == "nt":
        subprocess.run(
            ["cmd", "/c", "mklink", "/J", str(private_repo), str(target)],
            check=True,
            capture_output=True,
        )
    else:
        private_repo.symlink_to(target, target_is_directory=True)
    with pytest.raises(contract.ContainmentError):
        contract.assert_private_empty_run_root(private_repo, "run-001")
    assert not (target / "run-001").exists()


def test_reparse_attribute_is_blocked_even_without_symlink(private_repo, monkeypatch):
    private_repo.mkdir(parents=True)
    original = Path.lstat

    def reparse_metadata(path, *args, **kwargs):
        if path == private_repo:
            return SimpleNamespace(
                st_file_attributes=stat.FILE_ATTRIBUTE_REPARSE_POINT, st_mode=stat.S_IFDIR
            )
        return original(path, *args, **kwargs)

    monkeypatch.setattr(Path, "lstat", reparse_metadata)
    with pytest.raises(contract.ContainmentError):
        contract.assert_private_empty_run_root(private_repo, "run-001")


def test_receipt_skeleton_is_controlled_and_contains_no_text_payloads():
    config, manifest, _ = bindings()
    receipt = contract.build_receipt_skeleton(
        config=config, manifest=manifest, run_id="run-001", mode="prepare", now=NOW
    )
    validator("receipt").validate(receipt)
    assert receipt["technical_error_code"] == "NONE"
    assert receipt["external_provider_call_count"] == 0 and receipt["physical_call_count"] == 0
    assert receipt["spent_usd"] == "0.00" and receipt["scientific_result_count"] == 0
    assert receipt["status"] == "NOT_STARTED" and receipt["containment_check"] == "NOT_CHECKED"
    for key in ("prompt", "answer", "exception", "raw_response"):
        assert list(validator("receipt").iter_errors({**receipt, key: "private text"}))
    for code in (
        "NONE",
        "GRANT_INVALID",
        "BUDGET_EXCEEDED",
        "CALL_CAP_EXCEEDED",
        "TIMEOUT",
        "MALFORMED_RESPONSE",
        "EGRESS_BLOCKED",
        "INTERNAL_FAILURE",
    ):
        validator("receipt").validate({**receipt, "technical_error_code": code})
    assert list(
        validator("receipt").iter_errors({**receipt, "technical_error_code": "provider said..."})
    )


def test_contract_import_does_not_load_provider_sdk_or_network_clients():
    script = (
        "import sys; sys.path.insert(0, 'scripts'); import airtravel_execution_contract; "
        "assert not any(k in sys.modules for k in ('openai', 'httpx', 'requests', 'aiohttp'))"
    )
    subprocess.run([sys.executable, "-I", "-c", script], cwd=ROOT, check=True)
