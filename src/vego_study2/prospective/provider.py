"""Metered provider layer shared by both conditions.

Both conditions obtain the protected :class:`llm_client.LLMClient` from
:func:`build_client`.  Metering, the hard-ceiling guard, the single transport
retry, the frozen parameter surface, the returned-model check and the
text-free call ledger are applied at the SDK boundary
(``chat.completions.create``), so the ON orchestrator and the OFF direct call
are governed by exactly the same code path.

Two provider-specific adaptations live here.  The protected client sends the
legacy ``max_tokens`` name, which this model's endpoint rejects, so the value
is forwarded unchanged as ``max_completion_tokens``.  When a response omits
usage, the full per-request reservation is charged rather than zero.

The credential is never read by this module.  Presence is tested with a key
membership check; the OpenAI SDK reads the value itself.
"""

from __future__ import annotations

import asyncio
import contextvars
import hashlib
import json
import os
import re
import socket
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from . import constants as c
from .budget import SharedBudgetGuard

ROOT = Path(__file__).resolve().parents[3]

LABEL: contextvars.ContextVar[str | None] = contextvars.ContextVar("study2p_label", default=None)
CONDITION: contextvars.ContextVar[str | None] = contextvars.ContextVar("study2p_condition", default=None)
CASE: contextvars.ContextVar[str | None] = contextvars.ContextVar("study2p_case", default=None)

SECRET_RE = re.compile(
    r"(?:\bsk-[A-Za-z0-9_-]{8,}|\bAIza[A-Za-z0-9_-]{12,}|Bearer\s+\S+|(?:api[_ -]?key|password)\s*[:=])",
    re.I,
)
ALLOWED_REQUEST_KEYS = frozenset({"model", "messages", "max_completion_tokens", "timeout"})


class ProviderPolicyError(RuntimeError):
    """A request violated the frozen parameter surface or policy."""


class ModelMismatch(RuntimeError):
    """The provider answered with a model that is not the frozen model."""


class CredentialAbsent(RuntimeError):
    """The credential variable is not present in the process environment."""


def contains_secret(value: Any) -> bool:
    try:
        return bool(SECRET_RE.search(json.dumps(value, ensure_ascii=False)))
    except (TypeError, ValueError):
        return True


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")


def restrict_egress(allowed_hosts: frozenset[str]) -> dict[str, Any]:
    """Permit name resolution only for the allowed hosts (empty set blocks all)."""
    counters: dict[str, Any] = {"blocked_hosts": 0, "blocked_names": [], "allowed_hosts": sorted(allowed_hosts)}
    original = socket.getaddrinfo

    def guarded(host, port, *args, **kwargs):
        name = host.decode() if isinstance(host, bytes) else host
        if name not in allowed_hosts:
            counters["blocked_hosts"] += 1
            if len(counters["blocked_names"]) < 20:
                counters["blocked_names"].append(str(name))
            raise PermissionError(f"egress to {name!r} is not permitted for this run")
        return original(host, port, *args, **kwargs)

    socket.getaddrinfo = guarded
    counters["restore"] = lambda: setattr(socket, "getaddrinfo", original)
    return counters


def credential_present() -> bool:
    return c.CREDENTIAL_ENV in os.environ


@dataclass
class CallLedger:
    """Append-only, text-free record of every provider request."""

    path: Path | None
    entries: list[dict[str, Any]] = field(default_factory=list)
    _seq: int = 0

    def next_seq(self) -> int:
        self._seq += 1
        return self._seq

    def append(self, entry: dict[str, Any]) -> None:
        entry = {"schema_version": c.LEDGER_SCHEMA, **entry}
        if contains_secret(entry):
            raise ProviderPolicyError("ledger entry rejected: secret-like content")
        self.entries.append(entry)
        if self.path is not None:
            with self.path.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(entry, sort_keys=True, ensure_ascii=False) + "\n")

    def by_condition(self, condition: str) -> list[dict[str, Any]]:
        return [row for row in self.entries if row["condition"] == condition]


def _is_transport_error(exc: BaseException) -> bool:
    try:
        import openai
    except ImportError:
        return False
    transport = (openai.APIConnectionError, openai.RateLimitError, openai.InternalServerError)
    return isinstance(exc, transport) or isinstance(exc, asyncio.TimeoutError)


def _messages_digest(messages: Any) -> str:
    return hashlib.sha256(json.dumps(messages, sort_keys=True, ensure_ascii=False).encode("utf-8")).hexdigest()


def _validate_request(kwargs: dict[str, Any]) -> str:
    if "max_tokens" in kwargs:
        kwargs["max_completion_tokens"] = kwargs.pop("max_tokens")
    if kwargs.get("model") != c.MODEL:
        raise ProviderPolicyError("model switching is forbidden")
    if kwargs.get("max_completion_tokens") != c.MAX_OUTPUT_TOKENS:
        raise ProviderPolicyError("output-token ceiling differs from the frozen value")
    kwargs.setdefault("timeout", c.REQUEST_TIMEOUT_SECONDS)
    extra = set(kwargs) - ALLOWED_REQUEST_KEYS
    if extra:
        raise ProviderPolicyError(f"unfrozen request parameters: {sorted(extra)}")
    messages = kwargs.get("messages")
    if not isinstance(messages, list) or [m.get("role") for m in messages] != ["system", "user"]:
        raise ProviderPolicyError("message roles differ from the frozen system+user shape")
    return _messages_digest(messages)


def metered_create(original_create, guard: SharedBudgetGuard, ledger: CallLedger):
    """Wrap ``chat.completions.create`` with the frozen policy."""

    async def metered(*args, **kwargs):
        if args:
            raise ProviderPolicyError("positional provider arguments are not permitted")
        condition, label, case_id = CONDITION.get(), LABEL.get(), CASE.get()
        if condition not in {c.CONDITION_ON, c.CONDITION_OFF}:
            raise ProviderPolicyError("provider request outside a condition context")
        digest = _validate_request(kwargs)
        retry_of: int | None = None
        transport_retries = 0
        while True:
            guard.reserve(condition)
            seq = ledger.next_seq()
            base = {
                "seq": seq,
                "timestamp": utc_now(),
                "condition": condition,
                "label": label,
                "case_id": case_id,
                "messages_sha256": digest,
                "request_max_completion_tokens": c.MAX_OUTPUT_TOKENS,
                "retry_of_seq": retry_of,
            }
            started = time.perf_counter()
            try:
                response = await original_create(**kwargs)
            except Exception as exc:
                transport = _is_transport_error(exc)
                ledger.append({
                    **base,
                    "status": "TRANSPORT_ERROR" if transport else "PROVIDER_ERROR",
                    "error_type": type(exc).__name__,
                    "latency_ms": round((time.perf_counter() - started) * 1000),
                    "prompt_tokens": 0,
                    "completion_tokens": 0,
                    "cost_usd": 0.0,
                })
                if transport and transport_retries < c.TRANSPORT_RETRIES_PER_REQUEST:
                    transport_retries += 1
                    retry_of = seq
                    continue
                raise
            latency = round((time.perf_counter() - started) * 1000)
            usage = getattr(response, "usage", None)
            if usage is None:
                prompt_tokens = completion_tokens = None
                cost = guard.record(c.RESERVE_INPUT_TOKENS, c.MAX_OUTPUT_TOKENS)
                usage_status = "MISSING_USAGE_CHARGED_AT_RESERVE"
            else:
                prompt_tokens = int(getattr(usage, "prompt_tokens", 0) or 0)
                completion_tokens = int(getattr(usage, "completion_tokens", 0) or 0)
                cost = guard.record(prompt_tokens, completion_tokens)
                usage_status = "REPORTED"
            returned_model = getattr(response, "model", None)
            choices = getattr(response, "choices", None) or []
            entry = {
                **base,
                "status": "OK",
                "error_type": None,
                "latency_ms": latency,
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "usage_status": usage_status,
                "cost_usd": round(cost, 8),
                "response_model": returned_model,
                "system_fingerprint": getattr(response, "system_fingerprint", None),
                "finish_reason": getattr(choices[0], "finish_reason", None) if choices else None,
            }
            if not isinstance(returned_model, str) or not returned_model.startswith(c.MODEL):
                entry["status"] = "MODEL_MISMATCH"
                ledger.append(entry)
                raise ModelMismatch(f"provider returned model {returned_model!r}")
            ledger.append(entry)
            return response

    return metered


def _framework_on_path() -> None:
    framework = str(ROOT / "VEGO-AI" / "framework")
    if framework not in sys.path:
        sys.path.insert(0, framework)


def build_client(guard: SharedBudgetGuard, ledger: CallLedger, *, live: bool, fake_sdk: Any | None = None):
    """Return the protected LLMClient with the metered SDK boundary installed.

    ``live=True`` requires the credential variable to be present and lets the
    SDK read it.  ``live=False`` substitutes an in-process stub for the SDK
    class before construction, so no network object is ever created.
    """
    _framework_on_path()
    import llm_client

    if live:
        if fake_sdk is not None:
            raise ProviderPolicyError("a fake SDK cannot be combined with live execution")
        if not credential_present():
            raise CredentialAbsent(f"{c.CREDENTIAL_ENV} is absent from the process environment")
        client = llm_client.LLMClient(model=c.MODEL, interaction_log=None)
    else:
        if fake_sdk is None:
            raise ProviderPolicyError("offline construction requires a fake SDK")
        original = llm_client.AsyncOpenAI

        class _StubAsyncOpenAI:
            def __init__(self, *args, **kwargs):
                self.chat = fake_sdk.chat

        llm_client.AsyncOpenAI = _StubAsyncOpenAI
        try:
            client = llm_client.LLMClient(model=c.MODEL, interaction_log=None)
        finally:
            llm_client.AsyncOpenAI = original
    completions = client._client.chat.completions
    if not getattr(completions.create, "_study2p_metered", False):
        wrapped = metered_create(completions.create, guard, ledger)
        wrapped._study2p_metered = True
        completions.create = wrapped
    return client
