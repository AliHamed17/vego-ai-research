"""No live SDK, credentials or network: local transport doubles only."""

from __future__ import annotations

import asyncio
import importlib
import json
import subprocess
import sys
import time
from dataclasses import replace
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from pathlib import Path
from types import SimpleNamespace

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
contract = importlib.import_module("airtravel_execution_contract")
PROMPT = {"system": "Return JSON.", "user": "Synthetic fixture."}


def module():
    assert importlib.util.find_spec("airtravel_execution_provider") is not None, (
        "budgeted provider is missing"
    )
    return importlib.import_module("airtravel_execution_provider")


def config(**changes):
    cfg = contract.ExecutionConfig(
        model="test-model",
        provider_host="api.openai.com",
        max_usd=Decimal("6.00"),
        timeout_seconds=1,
        run_timeout_seconds=30,
        max_retries=1,
        concurrency=1,
        max_calls=28,
        max_input_tokens=1000,
        max_output_tokens=100,
        price_schedule=contract.PriceSchedule(
            "https://openai.com/api/pricing/",
            datetime.now(timezone.utc),
            Decimal("150"),
            Decimal("500"),
        ),
    )
    return replace(cfg, **changes)


def authorization(cfg):
    now = datetime.now(timezone.utc)
    source_paths = ["description.md"] + [
        f"result_one_{name}.txt"
        for name in ("claude-sonnet-4-6", "codestral-2508", "deepseek-chat", "gemini-2.5-flash")
    ]
    runtime_paths = ["domain_description/description.md"] + [
        f"candidate_models/{i:02d}_{name}" for i, name in enumerate(source_paths[1:], 1)
    ]
    files = tuple(
        contract.RuntimeFileBinding(source, runtime, 1, "b" * 64)
        for source, runtime in zip(source_paths, runtime_paths, strict=True)
    )
    manifest = contract.VerifiedInputManifest(
        code_sha="a" * 40,
        config_sha256=cfg.sha256,
        verification_sha256="c" * 64,
        source_inventory_sha256="d" * 64,
        source_archive_sha256="8cf82e2ab2d2ce3da9a7ec4165e760ae1e0d9af14468f5aa2a3883037d8da701",
        source_commit="253b26dc704d523209a5cba79686f8f7fab57d63",
        runtime_files=files,
        max_rounds=cfg.max_rounds,
        call_inventory_sha256=cfg.call_inventory_sha256,
        full_run_reservation=cfg.full_run_reservation,
    )
    command = [
        "runner.py",
        "execute",
        "--private-root",
        contract.PRIVATE_PARENT,
        "--run-id",
        "test-run",
    ]
    fields = {
        k: getattr(cfg, k)
        for k in (
            "model",
            "provider_host",
            "max_usd",
            "timeout_seconds",
            "run_timeout_seconds",
            "max_retries",
            "concurrency",
            "max_calls",
            "max_rounds",
            "call_inventory_sha256",
            "max_input_tokens",
            "max_output_tokens",
        )
    }
    grant = contract.ExecutionGrant(
        nonce="e" * 64,
        invocation_id="b5cd2d0c-021c-4300-81cc-296d66b5bb17",
        run_id="test-run",
        mode="execute",
        issued_at_utc=now - timedelta(seconds=5),
        expires_at_utc=now + timedelta(minutes=5),
        consumed=False,
        code_sha="a" * 40,
        input_manifest_sha256=manifest.sha256,
        config_sha256=cfg.sha256,
        price_schedule_sha256=cfg.price_schedule.sha256,
        command_sha256=contract.command_fingerprint(command),
        private_root=contract.PRIVATE_PARENT + "/test-run",
        full_run_reservation=cfg.full_run_reservation,
        **fields,
    )
    return {"grant": grant, "manifest": manifest, "current_commit": "a" * 40, "command": command}


class LocalSDK:
    """Double at the external boundary; forwards hooks before recording a request."""

    def __init__(self):
        self.requests = []
        self.client_options = None
        self.http_options = None
        self.transport_options = None
        self.outcome = "ok"
        self.closed = False
        self.before_transport = None
        self.before_response = None

    def install(self, monkeypatch):
        def transport(**kwargs):
            self.transport_options = kwargs
            return SimpleNamespace()

        def http(**kwargs):
            self.http_options = kwargs
            return SimpleNamespace()

        def sdk(**kwargs):
            self.client_options = kwargs
            return SimpleNamespace(
                chat=SimpleNamespace(completions=SimpleNamespace(create=self.create)),
                close=self.close,
            )

        monkeypatch.setitem(sys.modules, "openai", SimpleNamespace(AsyncOpenAI=sdk))
        monkeypatch.setitem(
            sys.modules, "httpx", SimpleNamespace(AsyncClient=http, AsyncHTTPTransport=transport)
        )
        # Replace the environment wholesale: never inspect host credentials.
        monkeypatch.setattr("os.environ", {})

    async def create(self, **kwargs):
        if self.before_transport:
            await self.before_transport()
        if self.outcome == "before_request_error":
            raise RuntimeError("private provider failure payload")
        request = SimpleNamespace(method="POST", url="https://api.openai.com/v1/chat/completions")
        for hook in self.http_options["event_hooks"]["request"]:
            await hook(request)
        self.requests.append(kwargs)
        if self.outcome == "timeout":
            raise TimeoutError("private provider failure payload")
        if self.outcome == "duplicate":
            for hook in self.http_options["event_hooks"]["request"]:
                await hook(request)
        if self.outcome == "error":
            raise RuntimeError("private provider failure payload")
        if self.outcome == "hang":
            await asyncio.Event().wait()
        if self.outcome == "cancelled":
            raise asyncio.CancelledError("private cancellation reason")
        if self.outcome == "redirect":
            for hook in self.http_options["event_hooks"]["response"]:
                await hook(SimpleNamespace(status_code=307))
        if self.before_response:
            await self.before_response()
        return SimpleNamespace(
            choices=[
                SimpleNamespace(
                    finish_reason="stop",
                    message=SimpleNamespace(
                        content='{"ok":true}' if self.outcome != "malformed" else "not-json"
                    ),
                )
            ],
            usage=SimpleNamespace(prompt_tokens=10, completion_tokens=5),
        )

    async def close(self):
        self.closed = True


def constructed(monkeypatch, cfg=None):
    p = module()
    cfg = cfg or config()
    ledger = p.BudgetLedger(cfg)
    sdk = LocalSDK()
    sdk.install(monkeypatch)
    provider = p.OpenAIProvider.construct_after_grant(cfg, ledger, **authorization(cfg))
    return p, provider, ledger, sdk


def test_whole_run_allocation_exists_before_first_transport_and_timeout_keeps_it(monkeypatch):
    from test_airtravel_execution_contract import full_budget_config

    p, provider, ledger, sdk = constructed(monkeypatch, full_budget_config())
    observed = []

    async def inspect_reserve():
        observed.append((ledger.full_run_reserve_active, ledger.reserved_usd))

    sdk.before_transport = inspect_reserve
    sdk.outcome = "timeout"
    with pytest.raises(p.TechnicalProviderFailure, match="^TIMEOUT$"):
        asyncio.run(provider.call(PROMPT, label="first"))
    assert observed == [(True, Decimal("6.00"))]
    assert ledger.reserved_usd == Decimal("6.00")
    assert ledger.unallocated_usd == Decimal("5.94")
    assert ledger.entries[0].reserved_usd == Decimal("0.06")
    assert ledger.physical_call_count == 1


def test_full_run_unaffordable_rejects_before_client_construction(monkeypatch):
    from test_airtravel_execution_contract import full_budget_config

    p = module()
    cfg = full_budget_config("6.01")
    sdk = LocalSDK()
    sdk.install(monkeypatch)
    with pytest.raises(p.TechnicalProviderFailure, match="^BUDGET_EXCEEDED$"):
        ledger = p.BudgetLedger(cfg)
        p.OpenAIProvider.construct_after_grant(cfg, ledger, **authorization(cfg))
    assert sdk.client_options is None
    assert sdk.requests == []


def test_every_physical_attempt_reserves_and_unknown_cost_is_retained():
    p = module()
    ledger = p.BudgetLedger(config())
    fake = p.DeterministicFakeProvider(["timeout", "ok"])
    with pytest.raises(p.TechnicalProviderFailure, match="^TIMEOUT$"):
        asyncio.run(p.guarded_call(fake, ledger, PROMPT, label="first"))
    assert ledger.physical_call_count == 1
    assert ledger.reserved_usd == Decimal("5.60")
    result = asyncio.run(p.guarded_call(fake, ledger, PROMPT, label="second", retry_of=1))
    assert result["output"] == {"ok": True}
    assert ledger.physical_call_count == 2
    assert ledger.external_provider_call_count == 0
    assert ledger.spent_usd == Decimal("0.004")
    assert ledger.reserved_usd == Decimal("5.40")
    assert ledger.entries[1].retry_of == 1
    assert fake.external_provider_call_count == 0


def test_reservation_failure_precedes_first_request():
    p = module()
    fake = p.DeterministicFakeProvider(["ok"])
    with pytest.raises(p.TechnicalProviderFailure, match="^BUDGET_EXCEEDED$"):
        ledger = p.BudgetLedger(config(max_input_tokens=40000))
        asyncio.run(p.guarded_call(fake, ledger, PROMPT, label="first"))
    assert fake.physical_call_count == 0


def test_explicit_config_call_cap_stops_even_when_money_remains():
    p = module()
    ledger = p.BudgetLedger(config(max_calls=1))
    fake = p.DeterministicFakeProvider(["ok", "ok"])
    asyncio.run(p.guarded_call(fake, ledger, PROMPT, label="first"))
    with pytest.raises(p.TechnicalProviderFailure, match="^CALL_CAP_EXCEEDED$"):
        asyncio.run(p.guarded_call(fake, ledger, PROMPT, label="second"))
    assert ledger.physical_call_count == fake.physical_call_count == 1


def test_explicit_retry_limit_cannot_be_exceeded():
    p = module()
    ledger = p.BudgetLedger(config(max_retries=0))
    fake = p.DeterministicFakeProvider(["timeout", "ok"])
    with pytest.raises(p.TechnicalProviderFailure, match="TIMEOUT"):
        asyncio.run(p.guarded_call(fake, ledger, PROMPT, label="first"))
    with pytest.raises(p.TechnicalProviderFailure, match="^RETRY_CAP_EXCEEDED$"):
        asyncio.run(p.guarded_call(fake, ledger, PROMPT, label="second", retry_of=1))
    assert fake.physical_call_count == 1


@pytest.mark.parametrize(
    "outcome",
    [
        "malformed",
        {"output": {}, "input_tokens": True, "output_tokens": 1},
        {"output": {}, "input_tokens": 1001, "output_tokens": 1},
    ],
)
def test_malformed_response_is_redacted_and_reservation_retained(outcome):
    p = module()
    ledger = p.BudgetLedger(config())
    fake = p.DeterministicFakeProvider([outcome])
    with pytest.raises(
        p.TechnicalProviderFailure, match="^(MALFORMED_RESPONSE|TOKEN_CAP_EXCEEDED)$"
    ):
        asyncio.run(p.guarded_call(fake, ledger, PROMPT, label="first"))
    assert ledger.reserved_usd == Decimal("5.60")
    assert ledger.spent_usd == 0
    assert ledger.entries[0].input_tokens is None


def test_prompt_descriptor_is_hash_only_and_mismatch_blocks_before_attempt():
    p = module()
    ledger = p.BudgetLedger(config())
    fake = p.DeterministicFakeProvider(["ok"])
    descriptor = p.describe_prompt(PROMPT)
    assert "Synthetic" not in repr(descriptor)
    with pytest.raises(p.TechnicalProviderFailure, match="^PROMPT_BINDING_MISMATCH$"):
        asyncio.run(
            p.guarded_call(
                fake, ledger, {**PROMPT, "user": "changed"}, label="first", descriptor=descriptor
            )
        )
    assert fake.physical_call_count == ledger.physical_call_count == 0


def test_input_bound_blocks_before_attempt():
    p = module()
    ledger = p.BudgetLedger(config(max_input_tokens=1))
    fake = p.DeterministicFakeProvider(["ok"])
    with pytest.raises(p.TechnicalProviderFailure, match="^TOKEN_CAP_EXCEEDED$"):
        asyncio.run(p.guarded_call(fake, ledger, PROMPT, label="first"))
    assert fake.physical_call_count == 0


def test_import_and_fake_provider_do_not_load_network_or_sdk():
    # A shared-process reload replaces class identities already bound by the
    # pipeline. Probe a genuinely fresh import without mutating those bindings.
    ledger_type = module().BudgetLedger
    probe = """
import builtins
import sys
sys.path.insert(0, 'scripts')
original = builtins.__import__
forbidden = {'openai', 'httpx', 'httpcore', 'socket', 'ssl', 'requests', 'urllib', 'asyncio'}
assert not any(name.split('.')[0] in forbidden for name in sys.modules)
def deny(name, *args, **kwargs):
    if name.split('.')[0] in forbidden:
        raise AssertionError('unexpected external-capability import')
    return original(name, *args, **kwargs)
builtins.__import__ = deny
import airtravel_execution_provider as provider
fake = provider.DeterministicFakeProvider(['ok'])
call = fake.call({'system': 'Return JSON.', 'user': 'Synthetic fixture.'}, label='first')
try:
    call.send(None)
except StopIteration as done:
    assert done.value['output'] == {'ok': True}
else:
    raise AssertionError('fake unexpectedly yielded')
assert fake.external_provider_call_count == 0
assert not any(name.split('.')[0] in forbidden for name in sys.modules)
print('PASS')
"""
    result = subprocess.run(
        [sys.executable, "-c", probe], cwd=ROOT, capture_output=True, text=True, timeout=30
    )
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == "PASS"
    assert module().BudgetLedger is ledger_type


def test_constructor_requires_valid_exact_grant_before_sdk_import(monkeypatch):
    p = module()
    cfg = config()
    sdk = LocalSDK()
    sdk.install(monkeypatch)
    bindings = authorization(cfg)
    bindings["command"] = ["runner.py", "preflight"]
    with pytest.raises(p.TechnicalProviderFailure, match="^INVALID_GRANT$"):
        p.OpenAIProvider.construct_after_grant(cfg, p.BudgetLedger(cfg), **bindings)
    assert sdk.client_options is None


@pytest.mark.parametrize(
    "options",
    [
        {"base_url": "https://other.invalid/v1"},
        {"base_url": "https://127.0.0.1/v1"},
        {"base_url": "https://[::1]/v1"},
        {"proxy": "https://other.invalid"},
        {"follow_redirects": True},
        {"transport": object()},
        {"socket_options": []},
    ],
)
def test_endpoint_or_transport_overrides_rejected_before_construction(monkeypatch, options):
    p = module()
    cfg = config()
    sdk = LocalSDK()
    sdk.install(monkeypatch)
    with pytest.raises(p.TechnicalProviderFailure, match="^UNSUPPORTED_TRANSPORT_CONFIG$"):
        p.OpenAIProvider.construct_after_grant(
            cfg, p.BudgetLedger(cfg), **authorization(cfg), **options
        )
    assert sdk.client_options is None


@pytest.mark.parametrize(
    "name", ["HTTP_PROXY", "https_proxy", "ALL_PROXY", "OPENAI_BASE_URL", "OPENAI_API_BASE"]
)
def test_environment_endpoint_overrides_rejected_without_values(monkeypatch, name):
    p = module()
    cfg = config()
    sdk = LocalSDK()
    sdk.install(monkeypatch)
    monkeypatch.setenv(name, "private endpoint")
    with pytest.raises(p.TechnicalProviderFailure, match="^UNSUPPORTED_TRANSPORT_CONFIG$"):
        p.OpenAIProvider.construct_after_grant(cfg, p.BudgetLedger(cfg), **authorization(cfg))
    assert sdk.client_options is None


def test_sdk_disables_automatic_retries_and_direct_call_uses_ledger(monkeypatch):
    p, provider, ledger, sdk = constructed(monkeypatch)
    assert sdk.client_options["max_retries"] == 0
    assert sdk.client_options["base_url"] == "https://api.openai.com/v1"
    assert sdk.http_options["follow_redirects"] is False
    assert sdk.http_options["trust_env"] is False
    assert sdk.transport_options["retries"] == 0
    assert sdk.transport_options["trust_env"] is False
    assert sdk.transport_options["verify"] is True
    result = asyncio.run(provider.call(PROMPT, label="first"))
    assert result["output"] == {"ok": True}
    assert ledger.physical_call_count == 1
    assert ledger.spent_usd == Decimal("0.004")
    assert ledger.reserved_usd == Decimal("5.40")
    assert sdk.requests[0]["max_completion_tokens"] == 100
    assert sdk.requests[0]["stream"] is False
    asyncio.run(provider.aclose())
    assert sdk.closed


@pytest.mark.parametrize(
    ("outcome", "code"),
    [
        ("timeout", "TIMEOUT"),
        ("error", "PROVIDER_ERROR"),
        ("malformed", "MALFORMED_RESPONSE"),
        ("redirect", "REDIRECT_REJECTED"),
        ("duplicate", "UNRESERVED_REQUEST"),
    ],
)
def test_sdk_failure_is_controlled_and_never_automatically_retried(monkeypatch, outcome, code):
    p, provider, ledger, sdk = constructed(monkeypatch)
    sdk.outcome = outcome
    with pytest.raises(p.TechnicalProviderFailure, match=f"^{code}$") as failed:
        asyncio.run(provider.call(PROMPT, label="first"))
    assert failed.value.__suppress_context__
    assert ledger.reserved_usd == Decimal("5.60")
    assert ledger.spent_usd == 0
    assert len(sdk.requests) == 1
    assert "private" not in repr(ledger.entries)


@pytest.mark.parametrize(
    "url",
    [
        "https://other.invalid/v1/chat/completions",
        "https://127.0.0.1/v1/chat/completions",
        "https://api.openai.com/v1/models",
        "http://api.openai.com/v1/chat/completions",
        "https://api.openai.com/v1/chat/completions?x=y",
    ],
)
def test_raw_sdk_request_cannot_escape_allowlist_or_reservation(monkeypatch, url):
    p, provider, ledger, sdk = constructed(monkeypatch)
    hook = sdk.http_options["event_hooks"]["request"][0]
    with pytest.raises(p.TechnicalProviderFailure):
        asyncio.run(hook(SimpleNamespace(method="POST", url=url)))
    assert ledger.physical_call_count == 0
    assert sdk.requests == []


def test_socket_bypass_provider_is_rejected_without_running_it():
    p = module()

    class Bypass:
        async def call(self, prompt, *, label):
            raise AssertionError("unapproved transport was invoked")

    with pytest.raises(p.TechnicalProviderFailure, match="^UNAPPROVED_PROVIDER$"):
        asyncio.run(p.guarded_call(Bypass(), p.BudgetLedger(config()), PROMPT, label="first"))


def test_ledger_snapshot_has_only_controlled_metadata():
    p = module()
    ledger = p.BudgetLedger(config())
    asyncio.run(
        p.guarded_call(p.DeterministicFakeProvider(["ok"]), ledger, PROMPT, label="phase1/template")
    )
    snapshot = ledger.to_dict()
    assert snapshot["physical_call_count"] == 1
    assert snapshot["input_token_count"] == 10
    assert snapshot["output_token_count"] == 5
    assert "Synthetic" not in json.dumps(snapshot)
    assert "Return JSON" not in json.dumps(snapshot)


def test_zero_price_schedule_fails_closed():
    cfg = config()
    with pytest.raises(contract.ContractValidationError, match="unbounded price schedule"):
        replace(
            cfg, price_schedule=replace(cfg.price_schedule, input_usd_per_million_tokens=Decimal("0"))
        )


def test_internal_call_without_reservation_cannot_reach_sdk(monkeypatch):
    p, provider, ledger, sdk = constructed(monkeypatch)
    with pytest.raises(p.TechnicalProviderFailure, match="^UNRESERVED_REQUEST$"):
        asyncio.run(provider._call_reserved(PROMPT, label="bypass"))
    assert ledger.physical_call_count == 0
    assert sdk.requests == []


def test_failure_before_transport_is_not_a_physical_request(monkeypatch):
    p, provider, ledger, sdk = constructed(monkeypatch)
    sdk.outcome = "before_request_error"
    with pytest.raises(p.TechnicalProviderFailure, match="^PROVIDER_ERROR$"):
        asyncio.run(provider.call(PROMPT, label="first"))
    assert ledger.physical_call_count == ledger.external_provider_call_count == 0
    assert len(ledger.entries) == 1
    assert ledger.entries[0].physical_attempted is False
    assert sdk.requests == []


def test_request_reservation_is_bound_to_its_task_context(monkeypatch):
    p, provider, ledger, sdk = constructed(monkeypatch)

    async def check():
        queued = asyncio.Event()
        release = asyncio.Event()

        async def pause():
            queued.set()
            await release.wait()

        sdk.before_transport = pause
        task = asyncio.create_task(provider.call(PROMPT, label="first"))
        await queued.wait()
        try:
            hook = sdk.http_options["event_hooks"]["request"][0]
            with pytest.raises(p.TechnicalProviderFailure, match="^UNRESERVED_REQUEST$"):
                await hook(
                    SimpleNamespace(method="POST", url="https://api.openai.com/v1/chat/completions")
                )
        finally:
            release.set()
            await task

    asyncio.run(check())
    assert ledger.physical_call_count == 1


def test_cancellation_retains_reservation_and_redacts_text(monkeypatch):
    p, provider, ledger, sdk = constructed(monkeypatch)
    sdk.outcome = "cancelled"
    with pytest.raises(asyncio.CancelledError, match="^CANCELLED$"):
        asyncio.run(provider.call(PROMPT, label="first"))
    assert ledger.entries[0].status == "CANCELLED"
    assert ledger.reserved_usd == Decimal("5.60")


def test_timeout_is_enforced_even_if_transport_never_finishes(monkeypatch):
    p, provider, ledger, sdk = constructed(monkeypatch)
    sdk.outcome = "hang"
    with pytest.raises(p.TechnicalProviderFailure, match="^TIMEOUT$"):
        asyncio.run(provider.call(PROMPT, label="first"))
    assert ledger.physical_call_count == 1
    assert ledger.reserved_usd == Decimal("5.60")


def test_whole_reservation_exists_at_transport_boundary(monkeypatch):
    p, provider, ledger, sdk = constructed(monkeypatch)

    async def check():
        assert ledger.reserved_usd == Decimal("5.60")
        assert ledger.spent_usd == 0

    sdk.before_transport = check
    asyncio.run(provider.call(PROMPT, label="first"))


def test_same_failed_prompt_requires_explicit_retry_identity():
    p = module()
    ledger = p.BudgetLedger(config(max_retries=0))
    fake = p.DeterministicFakeProvider(["timeout", "ok"])
    with pytest.raises(p.TechnicalProviderFailure, match="^TIMEOUT$"):
        asyncio.run(p.guarded_call(fake, ledger, PROMPT, label="first"))
    with pytest.raises(p.TechnicalProviderFailure, match="^INVALID_RETRY$"):
        asyncio.run(p.guarded_call(fake, ledger, PROMPT, label="different-label"))
    assert fake.physical_call_count == 1


@pytest.mark.parametrize("mutate", ["missing", "expired", "ledger"])
def test_constructor_rejects_missing_expired_or_other_ledger_grants(monkeypatch, mutate):
    p = module()
    cfg = config()
    sdk = LocalSDK()
    sdk.install(monkeypatch)
    bindings = authorization(cfg)
    ledger = p.BudgetLedger(cfg)
    if mutate == "missing":
        bindings["grant"] = None
    elif mutate == "expired":
        bindings["grant"] = replace(
            bindings["grant"],
            issued_at_utc=datetime.now(timezone.utc) - timedelta(minutes=5),
            expires_at_utc=datetime.now(timezone.utc) - timedelta(minutes=1),
        )
    else:
        ledger = p.BudgetLedger(replace(cfg, max_calls=3))
    with pytest.raises(
        p.TechnicalProviderFailure, match="^(INVALID_GRANT|LEDGER_CONFIG_MISMATCH)$"
    ):
        p.OpenAIProvider.construct_after_grant(cfg, ledger, **bindings)
    assert sdk.client_options is None


def test_closed_or_expired_provider_rejects_call_before_reservation(monkeypatch):
    p, provider, ledger, sdk = constructed(monkeypatch)
    asyncio.run(provider.aclose())
    with pytest.raises(p.TechnicalProviderFailure, match="^PROVIDER_CLOSED$"):
        asyncio.run(provider.call(PROMPT, label="first"))
    assert ledger.physical_call_count == 0
    assert sdk.requests == []


def test_async_timeout_type_on_python310_is_controlled(monkeypatch):
    p, provider, ledger, sdk = constructed(monkeypatch)
    # Before 3.11 asyncio.TimeoutError was distinct from builtin TimeoutError.
    legacy_timeout = type("TimeoutError", (Exception,), {})

    async def timed_out():
        raise legacy_timeout("private timeout detail")

    sdk.before_transport = timed_out
    with pytest.raises(p.TechnicalProviderFailure, match="^TIMEOUT$"):
        asyncio.run(provider.call(PROMPT, label="first"))
    assert ledger.reserved_usd == Decimal("5.60")


def test_inherited_child_task_cannot_consume_parent_reservation(monkeypatch):
    p, provider, ledger, sdk = constructed(monkeypatch)
    child_codes = []

    async def spawn_child_inside_sdk():
        async def child_request():
            hook = sdk.http_options["event_hooks"]["request"][0]
            try:
                await hook(
                    SimpleNamespace(method="POST", url="https://api.openai.com/v1/chat/completions")
                )
            except p.TechnicalProviderFailure as error:
                child_codes.append(error.code)
            else:
                child_codes.append("ALLOWED")

        # This child inherits the SDK callback's ContextVars, unlike the prior
        # regression that invoked the hook from an unrelated task context.
        await asyncio.create_task(child_request())
        assert ledger.physical_call_count == 0

    sdk.before_transport = spawn_child_inside_sdk
    parent_result = None
    parent_error = None
    try:
        parent_result = asyncio.run(provider.call(PROMPT, label="first"))
    except p.TechnicalProviderFailure as error:
        parent_error = error.code
    assert child_codes == ["UNRESERVED_REQUEST"]
    assert parent_error is None
    assert parent_result["output"] == {"ok": True}
    assert ledger.physical_call_count == ledger.external_provider_call_count == 1
    assert len(sdk.requests) == 1
    assert ledger.entries[0].status == "OK"


def test_cancellation_suppressed_late_dispatch_stays_blocked(monkeypatch):
    p, provider, ledger, sdk = constructed(monkeypatch)
    cancelled = []
    dispatch_codes = []

    async def check():
        dispatch_finished = asyncio.Event()
        hook = sdk.http_options["event_hooks"]["request"][0]

        async def observed_hook(request):
            try:
                await hook(request)
            except p.TechnicalProviderFailure as error:
                dispatch_codes.append(error.code)
                raise
            finally:
                dispatch_finished.set()

        async def suppress_cancellation_before_dispatch():
            try:
                await asyncio.Event().wait()
            except asyncio.CancelledError:
                cancelled.append(True)
                # A cancellation-suppressing SDK continues toward dispatch.

        sdk.http_options["event_hooks"]["request"] = [observed_hook]
        sdk.before_transport = suppress_cancellation_before_dispatch
        with pytest.raises(p.TechnicalProviderFailure, match="^TIMEOUT$"):
            await provider.call(PROMPT, label="first")
        await asyncio.wait_for(dispatch_finished.wait(), timeout=1)

    asyncio.run(check())
    assert cancelled == [True]
    assert dispatch_codes == ["TIMEOUT"]
    assert sdk.requests == []
    assert ledger.physical_call_count == ledger.external_provider_call_count == 0
    assert ledger.entries[0].status == "TIMEOUT"
    assert ledger.reserved_usd == Decimal("5.60")
    assert ledger.spent_usd == 0


def test_cancellation_suppressed_late_result_cannot_settle_success(monkeypatch):
    p, provider, ledger, sdk = constructed(monkeypatch)
    cancelled = []

    async def suppress_cancellation_before_result():
        try:
            await asyncio.Event().wait()
        except asyncio.CancelledError:
            cancelled.append(True)
            # The SDK returns a well-formed result, but it is already too late.

    sdk.before_response = suppress_cancellation_before_result
    with pytest.raises(p.TechnicalProviderFailure, match="^TIMEOUT$"):
        asyncio.run(provider.call(PROMPT, label="first"))
    assert cancelled == [True]
    assert len(sdk.requests) == 1
    assert ledger.physical_call_count == 1
    assert ledger.entries[0].status == "TIMEOUT"
    assert ledger.reserved_usd == Decimal("5.60")
    assert ledger.spent_usd == 0


def test_deadline_expired_without_cancellation_cannot_settle_success(monkeypatch):
    p, provider, ledger, sdk = constructed(monkeypatch)
    instant = time.monotonic_ns()
    monkeypatch.setattr(time, "monotonic_ns", lambda: instant)

    async def advance_past_attempt_deadline():
        # Deterministic monotonic-clock advance; the event loop timer need not
        # have run for a too-late response to be rejected at settlement.
        monkeypatch.setattr(time, "monotonic_ns", lambda: instant + 2_000_000_000)

    sdk.before_response = advance_past_attempt_deadline
    with pytest.raises(p.TechnicalProviderFailure, match="^TIMEOUT$"):
        asyncio.run(provider.call(PROMPT, label="first"))
    assert ledger.physical_call_count == 1
    assert ledger.entries[0].status == "TIMEOUT"
    assert ledger.reserved_usd == Decimal("5.60")
    assert ledger.spent_usd == 0
