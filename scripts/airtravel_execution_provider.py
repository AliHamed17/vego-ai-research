"""Execute-only, budgeted provider boundary and an entirely local fake.

Importing this module or using the fake never imports the SDK or networking.
The real client is lazy, grant-validated and deliberately single-flight. Grant
validation is NOT nonce consumption: Task 5 must durably consume the exact grant
and bind the new lane's own call inventory before calling construct_after_grant.
Legacy Study 1 formulas are not used anywhere in this module.

These application-level guards are not an OS sandbox for hostile Python code.
No caller-supplied transports, SDK clients or arbitrary provider implementations
are accepted. Deployment-level egress controls remain an independent safeguard.
"""

from __future__ import annotations

import hashlib
import json
import re
from collections.abc import Mapping, Sequence
from contextvars import ContextVar
from dataclasses import asdict, dataclass, replace
from decimal import Decimal, localcontext
from threading import RLock
from typing import TYPE_CHECKING, Any, Protocol

if TYPE_CHECKING:
    from airtravel_execution_contract import ExecutionConfig, ExecutionGrant, VerifiedInputManifest

BASE_URL = "https://api.openai.com/v1"
REQUEST_URL = BASE_URL + "/chat/completions"
_CODES = frozenset(
    {
        "BUDGET_EXCEEDED",
        "CALL_CAP_EXCEEDED",
        "RETRY_CAP_EXCEEDED",
        "INVALID_RETRY",
        "MALFORMED_RESPONSE",
        "TOKEN_CAP_EXCEEDED",
        "PROMPT_BINDING_MISMATCH",
        "INVALID_PROMPT",
        "INVALID_LABEL",
        "UNBOUNDED_PRICE_SCHEDULE",
        "UNSUPPORTED_EXECUTION_CONFIG",
        "UNSUPPORTED_TRANSPORT_CONFIG",
        "INVALID_GRANT",
        "LEDGER_CONFIG_MISMATCH",
        "UNAPPROVED_PROVIDER",
        "UNRESERVED_REQUEST",
        "REDIRECT_REJECTED",
        "HOST_REJECTED",
        "SDK_UNAVAILABLE",
        "CONSTRUCTION_FAILED",
        "TIMEOUT",
        "PROVIDER_ERROR",
        "CANCELLED",
        "CONCURRENT_CALL_REJECTED",
        "RUN_TIMEOUT",
        "PROVIDER_CLOSED",
    }
)
_TOKEN = object()


class TechnicalProviderFailure(RuntimeError):
    """Only an allowlisted code, never provider exception text or prompt content."""

    def __init__(self, code: str):
        self.code = code if code in _CODES else "PROVIDER_ERROR"
        super().__init__(self.code)


@dataclass(frozen=True)
class PromptDescriptor:
    sha256: str
    input_token_upper_bound: int


def describe_prompt(prompt: Mapping[str, str]) -> PromptDescriptor:
    """Hash-only descriptor for a fixed two-message, text-only chat envelope.

    UTF-8 bytes plus 64 overhead tokens per message conservatively bound the
    supported byte-tokenized chat envelope. No tools, images, alternate roles,
    named messages or caller-controlled API options are permitted. An execute
    gate must verify the chosen model's envelope/tokenization before approval.
    """
    if (
        not isinstance(prompt, Mapping)
        or set(prompt) != {"system", "user"}
        or any(type(value) is not str or not value for value in prompt.values())
    ):
        raise TechnicalProviderFailure("INVALID_PROMPT")
    try:
        payload = json.dumps(
            dict(prompt), sort_keys=True, ensure_ascii=False, separators=(",", ":")
        ).encode("utf-8")
        upper_bound = sum(len(value.encode("utf-8")) for value in prompt.values()) + 128
    except (ValueError, TypeError, UnicodeError):
        raise TechnicalProviderFailure("INVALID_PROMPT") from None
    return PromptDescriptor(hashlib.sha256(payload).hexdigest(), upper_bound)


@dataclass(frozen=True)
class LedgerEntry:
    attempt_id: int
    label: str
    prompt_sha256: str
    input_token_upper_bound: int
    reserved_usd: Decimal
    external: bool
    retry_of: int | None = None
    retry_depth: int = 0
    status: str = "RESERVED"
    input_tokens: int | None = None
    output_tokens: int | None = None
    spent_usd: Decimal = Decimal("0")
    physical_attempted: bool = False
    deadline_monotonic_ns: int | None = None


def _check_attempt_deadline(entry: LedgerEntry) -> None:
    import time

    if (
        entry.deadline_monotonic_ns is not None
        and time.monotonic_ns() >= entry.deadline_monotonic_ns
    ):
        raise TechnicalProviderFailure("TIMEOUT")


@dataclass
class _AttemptPermission:
    entry: LedgerEntry
    owner: Any = None
    request_permitted: bool = True


class BudgetLedger:
    """Immutable config bound ledger; exact Decimal money, no optimistic refunds.

    Before request one, every authorized slot is allocated at both token caps.
    Unknown-cost failures keep their allocation. Known successful usage
    releases only its slot and records full uncached input/output rates.
    Physical counts advance at the request hook, or the local fake call boundary.
    Reservations that fail before transport are retained but are not physical calls.
    A timeout is not evidence that the remote service avoided billing.
    """

    def __init__(self, config: ExecutionConfig):
        from airtravel_execution_contract import ExecutionConfig

        if type(config) is not ExecutionConfig:
            raise TechnicalProviderFailure("UNSUPPORTED_EXECUTION_CONFIG")
        if config.concurrency != 1 or any(
            value > 1_000_000_000
            for value in (config.max_calls, config.max_input_tokens, config.max_output_tokens)
        ):
            raise TechnicalProviderFailure("UNSUPPORTED_EXECUTION_CONFIG")
        prices = (
            config.price_schedule.input_usd_per_million_tokens,
            config.price_schedule.output_usd_per_million_tokens,
        )
        if any(
            not rate.is_finite()
            or rate <= 0
            or rate > Decimal("1000000")
            or len(rate.as_tuple().digits) > 24
            or rate.as_tuple().exponent < -18
            for rate in prices
        ):
            raise TechnicalProviderFailure("UNBOUNDED_PRICE_SCHEDULE")
        self._config = config
        self._entries: list[LedgerEntry] = []
        self._lock = RLock()
        self._reserve_per_attempt = self._cost(config.max_input_tokens, config.max_output_tokens)
        self._full_run_reservation = config.full_run_reservation
        if self._full_run_reservation.full_run_usd > config.max_usd:
            raise TechnicalProviderFailure("BUDGET_EXCEEDED")
        self._full_run_reserve_active = True

    @property
    def full_run_reserve_active(self) -> bool:
        return self._full_run_reserve_active

    @property
    def unallocated_usd(self) -> Decimal:
        """Held slots not yet assigned to any attempt; failures never restore slots."""
        with localcontext() as ctx:
            ctx.prec = 100
            return self._full_run_reservation.full_run_usd - len(self._entries) * self.reserve_per_attempt

    @property
    def config(self) -> ExecutionConfig:
        return self._config

    @property
    def entries(self) -> tuple[LedgerEntry, ...]:
        return tuple(self._entries)

    @property
    def physical_call_count(self) -> int:
        return sum(entry.physical_attempted for entry in self._entries)

    @property
    def external_provider_call_count(self) -> int:
        return sum(entry.external and entry.physical_attempted for entry in self._entries)

    @property
    def reserve_per_attempt(self) -> Decimal:
        return self._reserve_per_attempt

    @property
    def reserved_usd(self) -> Decimal:
        with localcontext() as ctx:
            ctx.prec = 100
            return self.unallocated_usd + sum(
                (entry.reserved_usd for entry in self._entries if entry.status != "OK"),
                Decimal("0"),
            )

    @property
    def spent_usd(self) -> Decimal:
        with localcontext() as ctx:
            ctx.prec = 100
            return sum((entry.spent_usd for entry in self._entries), Decimal("0"))

    def _cost(self, input_tokens: int, output_tokens: int) -> Decimal:
        with localcontext() as ctx:
            ctx.prec = 100
            rates = self._config.price_schedule
            return (
                input_tokens * rates.input_usd_per_million_tokens
                + output_tokens * rates.output_usd_per_million_tokens
            ) / Decimal("1000000")

    def _reserve(
        self,
        descriptor: PromptDescriptor,
        label: str,
        *,
        external: bool,
        retry_of: int | None,
        deadline_monotonic_ns: int | None = None,
    ) -> LedgerEntry:
        if type(label) is not str or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_./:-]{0,127}", label):
            raise TechnicalProviderFailure("INVALID_LABEL")
        if descriptor.input_token_upper_bound > self._config.max_input_tokens:
            raise TechnicalProviderFailure("TOKEN_CAP_EXCEEDED")
        with self._lock, localcontext() as ctx:
            ctx.prec = 100
            if any(entry.status == "RESERVED" for entry in self._entries):
                raise TechnicalProviderFailure("CONCURRENT_CALL_REJECTED")
            depth = 0
            previous_prompt = next(
                (
                    entry
                    for entry in reversed(self._entries)
                    if entry.prompt_sha256 == descriptor.sha256
                ),
                None,
            )
            if retry_of is None and previous_prompt is not None and previous_prompt.status != "OK":
                raise TechnicalProviderFailure("INVALID_RETRY")
            if retry_of is not None:
                if type(retry_of) is not int or not 1 <= retry_of <= len(self._entries):
                    raise TechnicalProviderFailure("INVALID_RETRY")
                previous = self._entries[retry_of - 1]
                if (
                    previous.status not in {"TIMEOUT", "PROVIDER_ERROR"}
                    or previous.prompt_sha256 != descriptor.sha256
                    or any(entry.retry_of == retry_of for entry in self._entries)
                ):
                    raise TechnicalProviderFailure("INVALID_RETRY")
                depth = previous.retry_depth + 1
                if depth > self._config.max_retries:
                    raise TechnicalProviderFailure("RETRY_CAP_EXCEEDED")
            if len(self._entries) >= self._config.max_calls:
                raise TechnicalProviderFailure("CALL_CAP_EXCEEDED")
            if (
                not self.full_run_reserve_active
                or self.unallocated_usd < self.reserve_per_attempt
                or self.spent_usd + self.reserved_usd > self._config.max_usd
            ):
                raise TechnicalProviderFailure("BUDGET_EXCEEDED")
            entry = LedgerEntry(
                len(self._entries) + 1,
                label,
                descriptor.sha256,
                descriptor.input_token_upper_bound,
                self.reserve_per_attempt,
                external,
                retry_of,
                depth,
                deadline_monotonic_ns=deadline_monotonic_ns,
            )
            self._entries.append(entry)
            return entry

    def _begin_attempt(self, entry: LedgerEntry) -> None:
        with self._lock:
            _check_attempt_deadline(entry)
            if self._entries[entry.attempt_id - 1] is not entry or entry.status != "RESERVED":
                raise TechnicalProviderFailure("UNRESERVED_REQUEST")
            self._entries[entry.attempt_id - 1] = replace(entry, physical_attempted=True)

    def _finish(
        self,
        entry: LedgerEntry,
        *,
        code: str,
        input_tokens: int | None = None,
        output_tokens: int | None = None,
    ) -> None:
        with self._lock:
            if code == "OK":
                _check_attempt_deadline(entry)
            self._entries[entry.attempt_id - 1] = replace(
                self._entries[entry.attempt_id - 1],
                status=code,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                spent_usd=self._cost(input_tokens, output_tokens) if code == "OK" else Decimal("0"),
            )

    def to_dict(self) -> dict[str, Any]:
        """Private serializable metadata; no raw prompts, outputs or exceptions."""
        return {
            "config_sha256": self._config.sha256,
            "max_calls": self._config.max_calls,
            "max_usd": format(self._config.max_usd, "f"),
            "full_run_reservation": self._full_run_reservation.to_dict(),
            "full_run_reservation_sha256": self._full_run_reservation.sha256,
            "authorized_call_count": self._full_run_reservation.authorized_call_count,
            "full_run_reserve_active": self.full_run_reserve_active,
            "unallocated_usd": format(self.unallocated_usd, "f"),
            "cost_basis": "PLANNED_ONLY" if not self._entries else (
                "PROVIDER_USAGE" if any(entry.external for entry in self._entries)
                else "LOCAL_FAKE_SIMULATION"
            ),
            "physical_call_count": self.physical_call_count,
            "external_provider_call_count": self.external_provider_call_count,
            "input_token_count": sum(entry.input_tokens or 0 for entry in self._entries),
            "output_token_count": sum(entry.output_tokens or 0 for entry in self._entries),
            "spent_usd": format(self.spent_usd, "f"),
            "reserved_usd": format(self.reserved_usd, "f"),
            "entries": [
                {
                    key: format(value, "f") if isinstance(value, Decimal) else value
                    for key, value in asdict(entry).items()
                }
                for entry in self._entries
            ],
        }


class ProviderProtocol(Protocol):
    async def call(self, prompt: Mapping[str, str], *, label: str) -> Mapping[str, Any]:
        """Return a constrained response for one already-reserved physical call."""


class DeterministicFakeProvider:
    """Local outcomes only; never imports the SDK or any networking module."""

    external_provider_call_count = 0

    def __init__(self, outcomes: Sequence[str | Mapping[str, Any]] = ("ok",)):
        self._outcomes = iter(outcomes)
        self.physical_call_count = 0

    async def call(self, prompt: Mapping[str, str], *, label: str) -> Mapping[str, Any]:
        self.physical_call_count += 1
        outcome = next(self._outcomes, "malformed")
        if isinstance(outcome, Mapping):
            return dict(outcome)
        if outcome == "timeout":
            raise TechnicalProviderFailure("TIMEOUT") from None
        if outcome == "ok":
            return {"output": {"ok": True}, "input_tokens": 10, "output_tokens": 5}
        raise TechnicalProviderFailure("MALFORMED_RESPONSE") from None


def _failure_code(error: BaseException) -> str:
    # The SDK can wrap hook failures; inspect only exception types/codes, never text.
    seen = set()
    while id(error) not in seen:
        seen.add(id(error))
        if isinstance(error, TechnicalProviderFailure):
            return error.code
        if isinstance(error, TimeoutError) or type(error).__name__ in {
            "TimeoutError",
            "APITimeoutError",
            "TimeoutException",
            "ReadTimeout",
            "ConnectTimeout",
        }:
            return "TIMEOUT"
        if type(error).__name__ == "CancelledError":
            return "CANCELLED"
        if error.__cause__ is None:
            break
        error = error.__cause__
    return "PROVIDER_ERROR"


def _response(value: Mapping[str, Any], config: ExecutionConfig) -> dict[str, Any]:
    if (
        not isinstance(value, Mapping)
        or set(value) != {"output", "input_tokens", "output_tokens"}
        or type(value["output"]) is not dict
    ):
        raise TechnicalProviderFailure("MALFORMED_RESPONSE")
    for key, limit in (
        ("input_tokens", config.max_input_tokens),
        ("output_tokens", config.max_output_tokens),
    ):
        if type(value[key]) is not int or value[key] < 0:
            raise TechnicalProviderFailure("MALFORMED_RESPONSE")
        if value[key] > limit:
            raise TechnicalProviderFailure("TOKEN_CAP_EXCEEDED")
    try:
        json.dumps(value["output"], allow_nan=False)
    except (ValueError, TypeError, RecursionError):
        raise TechnicalProviderFailure("MALFORMED_RESPONSE") from None
    return dict(value)


async def guarded_call(
    provider: ProviderProtocol,
    ledger: BudgetLedger,
    prompt: Mapping[str, str],
    *,
    label: str,
    descriptor: PromptDescriptor | None = None,
    retry_of: int | None = None,
) -> Mapping[str, Any]:
    """One attempt only; caller must explicitly request and budget every retry."""
    if type(provider) not in (DeterministicFakeProvider, OpenAIProvider):
        raise TechnicalProviderFailure("UNAPPROVED_PROVIDER")
    external = type(provider) is OpenAIProvider
    if external:
        provider._check_ready(ledger)
    actual = describe_prompt(prompt)
    if descriptor is not None and (
        type(descriptor) is not PromptDescriptor or descriptor != actual
    ):
        raise TechnicalProviderFailure("PROMPT_BINDING_MISMATCH")
    # Detach the mutable caller mapping before an await or physical request.
    request_prompt = dict(prompt)
    deadline_ns = None
    if external:
        import time

        deadline_ns = min(
            time.monotonic_ns() + ledger.config.timeout_seconds * 1_000_000_000,
            provider._deadline_monotonic_ns,
        )
    entry = ledger._reserve(
        actual,
        label,
        external=external,
        retry_of=retry_of,
        deadline_monotonic_ns=deadline_ns,
    )
    try:
        if external:
            value = await provider._call_reserved(request_prompt, label=label, _entry=entry)
        else:
            ledger._begin_attempt(entry)
            value = await provider.call(request_prompt, label=label)
        result = _response(value, ledger.config)
        ledger._finish(
            entry,
            code="OK",
            input_tokens=result["input_tokens"],
            output_tokens=result["output_tokens"],
        )
        return result
    except BaseException as error:
        code = _failure_code(error)
        ledger._finish(entry, code=code)
        if isinstance(error, (KeyboardInterrupt, SystemExit)):
            raise
        if code == "CANCELLED":
            raise type(error)("CANCELLED") from None
        raise TechnicalProviderFailure(code) from None


class OpenAIProvider:
    """Fixed-host SDK adapter; constructor and direct calls cannot bypass the gate."""

    def __init__(self, *, _token: object = None):
        if _token is not _TOKEN:
            raise TechnicalProviderFailure("INVALID_GRANT")

    @classmethod
    def construct_after_grant(
        cls,
        config: ExecutionConfig,
        ledger: BudgetLedger,
        *,
        grant: ExecutionGrant | None = None,
        manifest: VerifiedInputManifest | None = None,
        current_commit: str = "",
        command: Sequence[str] = (),
        **options: Any,
    ) -> OpenAIProvider:
        """Validate exact bindings before lazy import; nonce consumption is upstream.

        No API-key/client/transport override is exposed. Actual SDK construction
        may obtain credentials only in a later separately authorized execute run.
        """
        import os
        import time

        from airtravel_execution_contract import require_full_run_budget, validate_execution_grant

        forbidden_environment = {
            "HTTP_PROXY",
            "HTTPS_PROXY",
            "ALL_PROXY",
            "NO_PROXY",
            "OPENAI_BASE_URL",
            "OPENAI_API_BASE",
            "OPENAI_PROXY",
            "OPENAI_WEBSOCKET_BASE_URL",
        }
        if (
            options
            or config.provider_host != "api.openai.com"
            or any(
                os.environ.get(name) or os.environ.get(name.lower())
                for name in forbidden_environment
            )
        ):
            raise TechnicalProviderFailure("UNSUPPORTED_TRANSPORT_CONFIG")
        if type(ledger) is not BudgetLedger or ledger.config != config or ledger.entries:
            raise TechnicalProviderFailure("LEDGER_CONFIG_MISMATCH")
        try:
            reservation = require_full_run_budget(config)
            if not ledger.full_run_reserve_active or ledger.reserved_usd != reservation.full_run_usd:
                raise TechnicalProviderFailure("LEDGER_CONFIG_MISMATCH")
            validate_execution_grant(
                grant,
                config=config,
                manifest=manifest,
                current_commit=current_commit,
                command=command,
            )
        except Exception:
            raise TechnicalProviderFailure("INVALID_GRANT") from None
        provider = cls(_token=_TOKEN)
        provider._ledger = ledger
        provider._grant = grant
        provider._deadline_monotonic_ns = (
            time.monotonic_ns() + config.run_timeout_seconds * 1_000_000_000
        )
        provider._attempt_context = ContextVar("airtravel_reserved_attempt", default=None)
        provider._closed = False
        try:
            import httpx
            from openai import AsyncOpenAI

            transport = httpx.AsyncHTTPTransport(retries=0, trust_env=False, verify=True)
            http_client = httpx.AsyncClient(
                transport=transport,
                trust_env=False,
                follow_redirects=False,
                timeout=config.timeout_seconds,
                event_hooks={
                    "request": [provider._before_request],
                    "response": [provider._after_response],
                },
            )
            provider._client = AsyncOpenAI(
                base_url=BASE_URL,
                max_retries=0,
                timeout=config.timeout_seconds,
                http_client=http_client,
            )
        except ImportError:
            raise TechnicalProviderFailure("SDK_UNAVAILABLE") from None
        except Exception:
            raise TechnicalProviderFailure("CONSTRUCTION_FAILED") from None
        return provider

    def _check_ready(self, ledger: BudgetLedger) -> None:
        import time
        from datetime import datetime, timezone

        if ledger is not self._ledger:
            raise TechnicalProviderFailure("LEDGER_CONFIG_MISMATCH")
        if self._closed:
            raise TechnicalProviderFailure("PROVIDER_CLOSED")
        if datetime.now(timezone.utc) >= self._grant.expires_at_utc:
            raise TechnicalProviderFailure("INVALID_GRANT")
        if time.monotonic_ns() >= self._deadline_monotonic_ns:
            raise TechnicalProviderFailure("RUN_TIMEOUT")

    async def _before_request(self, request: Any) -> None:
        import asyncio

        if request.method != "POST" or str(request.url) != REQUEST_URL:
            raise TechnicalProviderFailure("HOST_REJECTED")
        permission = self._attempt_context.get()
        if permission is None or permission.owner is not asyncio.current_task():
            raise TechnicalProviderFailure("UNRESERVED_REQUEST")
        _check_attempt_deadline(permission.entry)
        if not permission.request_permitted:
            raise TechnicalProviderFailure("UNRESERVED_REQUEST")
        self._check_ready(self._ledger)
        self._ledger._begin_attempt(permission.entry)
        permission.request_permitted = False

    async def _after_response(self, response: Any) -> None:
        if 300 <= response.status_code < 400:
            raise TechnicalProviderFailure("REDIRECT_REJECTED")

    async def call(
        self,
        prompt: Mapping[str, str],
        *,
        label: str,
        descriptor: PromptDescriptor | None = None,
        retry_of: int | None = None,
    ) -> Mapping[str, Any]:
        return await guarded_call(
            self, self._ledger, prompt, label=label, descriptor=descriptor, retry_of=retry_of
        )

    async def _call_reserved(
        self, prompt: Mapping[str, str], *, label: str, _entry: LedgerEntry | None = None
    ) -> Mapping[str, Any]:
        import asyncio
        import time

        if (
            _entry is None
            or not self._ledger.entries
            or self._ledger.entries[-1] is not _entry
            or _entry.status != "RESERVED"
            or not _entry.external
            or _entry.deadline_monotonic_ns is None
        ):
            raise TechnicalProviderFailure("UNRESERVED_REQUEST")
        permission = _AttemptPermission(_entry)
        cfg = self._ledger.config

        async def owned_request():
            # ContextVar values are inherited by child tasks, but task identity
            # is not. Only this exact task may use the request permission.
            permission.owner = asyncio.current_task()
            token = self._attempt_context.set(permission)
            try:
                return await self._client.chat.completions.create(
                    model=cfg.model,
                    messages=[{"role": key, "content": prompt[key]} for key in ("system", "user")],
                    max_completion_tokens=cfg.max_output_tokens,
                    response_format={"type": "json_object"},
                    stream=False,
                )
            finally:
                self._attempt_context.reset(token)

        worker = asyncio.create_task(owned_request())

        def consume_worker_outcome(task):
            # Cancellation suppression must not keep the caller waiting or
            # cause late SDK exceptions to be emitted by the event-loop logger.
            if not task.cancelled():
                task.exception()

        try:
            done, _ = await asyncio.wait(
                {worker},
                timeout=max(
                    0, (_entry.deadline_monotonic_ns - time.monotonic_ns()) / 1_000_000_000
                ),
            )
            if not done:
                raise TechnicalProviderFailure("TIMEOUT")
            result = worker.result()
            _check_attempt_deadline(_entry)
            if len(result.choices) != 1 or result.choices[0].finish_reason != "stop":
                raise TechnicalProviderFailure("MALFORMED_RESPONSE")

            def unique(pairs):
                value = {}
                for key, item in pairs:
                    if key in value:
                        raise ValueError("duplicate key")
                    value[key] = item
                return value

            output = json.loads(result.choices[0].message.content, object_pairs_hook=unique)
            return {
                "output": output,
                "input_tokens": result.usage.prompt_tokens,
                "output_tokens": result.usage.completion_tokens,
            }
        except (AttributeError, TypeError, ValueError, IndexError):
            raise TechnicalProviderFailure("MALFORMED_RESPONSE") from None
        finally:
            # Revoke before cancel: a cancellation-suppressing worker may keep
            # running, but can no longer dispatch under this reservation.
            permission.request_permitted = False
            if not worker.done():
                worker.cancel()
            worker.add_done_callback(consume_worker_outcome)

    async def aclose(self) -> None:
        """Release the owned SDK/HTTP client; later calls remain blocked."""
        self._closed = True
        try:
            await self._client.close()
        except Exception:
            raise TechnicalProviderFailure("PROVIDER_ERROR") from None
