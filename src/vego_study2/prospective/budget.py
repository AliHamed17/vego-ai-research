"""Pessimistic reservation arithmetic and the shared hard-ceiling guard.

The guard is the enforcement mechanism: no provider request is issued unless
the cumulative recorded spend plus one full per-request reservation stays at
or below the guard ceiling, and no request is issued beyond the frozen total
or per-condition request caps.  Retries, failed calls and parse re-attempts
are requests like any other.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any

from . import constants as c


class BudgetStop(RuntimeError):
    """Raised when a request would breach a frozen cap or the ceiling."""


def per_request_reserve_usd(
    reserve_input_tokens: int = c.RESERVE_INPUT_TOKENS,
    max_output_tokens: int = c.MAX_OUTPUT_TOKENS,
    price_in_per_m: float = c.PRICE_IN_PER_M,
    price_out_per_m: float = c.PRICE_OUT_PER_M,
) -> float:
    return (reserve_input_tokens * price_in_per_m + max_output_tokens * price_out_per_m) / 1_000_000


def total_request_cap(guard_ceiling_usd: float = c.GUARD_CEILING_USD, reserve: float | None = None) -> int:
    reserve = per_request_reserve_usd() if reserve is None else reserve
    return math.floor(guard_ceiling_usd / reserve + 1e-9)


def design_menu(eligible_cases: int) -> dict[str, Any]:
    """Return the three protocol options with their pessimistic reservations."""
    reserve = per_request_reserve_usd()
    cap = total_request_cap()
    per_unit = c.ON_REQUEST_CAP_PER_CASE + c.OFF_REQUEST_CAP_PER_CASE
    largest_n = min(eligible_cases, cap // per_unit)

    def option(name: str, distinct_cases: int, repeats: int, purpose: str) -> dict[str, Any]:
        units = distinct_cases * repeats
        requests = units * per_unit
        return {
            "option": name,
            "purpose": purpose,
            "distinct_cases": distinct_cases,
            "repeats_per_case": repeats,
            "paired_units": units,
            "on_request_cap": units * c.ON_REQUEST_CAP_PER_CASE,
            "off_request_cap": units * c.OFF_REQUEST_CAP_PER_CASE,
            "requests_reserved": requests,
            "reservation_usd": round(requests * reserve, 4),
            "fits_guard_ceiling": requests <= cap and requests * reserve <= c.GUARD_CEILING_USD + 1e-9,
            "meets_minimum_cases": distinct_cases >= c.MIN_PAIRED_CASES,
        }

    return {
        "per_request_reserve_usd": round(reserve, 7),
        "guard_ceiling_usd": c.GUARD_CEILING_USD,
        "hard_ceiling_usd": c.HARD_CEILING_USD,
        "total_request_cap": cap,
        "requests_per_paired_unit": per_unit,
        "options": [
            option("A_HIGHEST_COVERAGE", largest_n, 1, "largest distinct paired sample that fits the ceiling"),
            option("B_REPEATABILITY", max(c.MIN_PAIRED_CASES, largest_n // 2), 2, "fewer distinct cases, two repeats each"),
            option("C_MINIMUM_VIABLE", c.MIN_PAIRED_CASES, 1, "four paired cases, one repeat"),
        ],
    }


@dataclass
class SharedBudgetGuard:
    """One ledger for both conditions; caps are frozen at construction."""

    guard_ceiling_usd: float
    total_request_cap: int
    condition_request_caps: dict[str, int]
    per_request_reserve: float = field(default_factory=per_request_reserve_usd)
    requests: int = 0
    requests_by_condition: dict[str, int] = field(default_factory=dict)
    prompt_tokens: int = 0
    completion_tokens: int = 0
    spent_usd: float = 0.0
    refusals: list[dict[str, Any]] = field(default_factory=list)

    def reserve(self, condition: str) -> None:
        cap = self.condition_request_caps.get(condition)
        if cap is None:
            raise BudgetStop(f"condition {condition!r} has no frozen request cap")
        used = self.requests_by_condition.get(condition, 0)
        if used + 1 > cap:
            self._refuse(condition, "CONDITION_REQUEST_CAP", f"{condition} request cap {cap} reached")
        if self.requests + 1 > self.total_request_cap:
            self._refuse(condition, "TOTAL_REQUEST_CAP", f"total request cap {self.total_request_cap} reached")
        if self.spent_usd + self.per_request_reserve > self.guard_ceiling_usd + 1e-12:
            self._refuse(
                condition,
                "COST_CEILING",
                f"reservation would exceed guard ceiling ${self.guard_ceiling_usd:.2f} "
                f"(spent ${self.spent_usd:.4f}, reserve ${self.per_request_reserve:.4f})",
            )
        self.requests += 1
        self.requests_by_condition[condition] = used + 1

    def _refuse(self, condition: str, code: str, detail: str) -> None:
        self.refusals.append({"condition": condition, "code": code, "detail": detail})
        raise BudgetStop(f"{code}: {detail}")

    def record(self, prompt_tokens: int, completion_tokens: int) -> float:
        cost = (prompt_tokens * c.PRICE_IN_PER_M + completion_tokens * c.PRICE_OUT_PER_M) / 1_000_000
        self.prompt_tokens += prompt_tokens
        self.completion_tokens += completion_tokens
        self.spent_usd += cost
        return cost

    def remaining_reservation_capacity(self) -> int:
        """How many further fully reserved requests the ceiling still admits."""
        return max(0, math.floor((self.guard_ceiling_usd - self.spent_usd) / self.per_request_reserve + 1e-9))

    def summary(self) -> dict[str, Any]:
        return {
            "requests": self.requests,
            "requests_by_condition": dict(sorted(self.requests_by_condition.items())),
            "total_request_cap": self.total_request_cap,
            "condition_request_caps": dict(sorted(self.condition_request_caps.items())),
            "prompt_tokens": self.prompt_tokens,
            "completion_tokens": self.completion_tokens,
            "total_tokens": self.prompt_tokens + self.completion_tokens,
            "actual_cost_usd": round(self.spent_usd, 6),
            "per_request_reserve_usd": round(self.per_request_reserve, 7),
            "guard_ceiling_usd": self.guard_ceiling_usd,
            "hard_ceiling_usd": c.HARD_CEILING_USD,
            "within_hard_ceiling": self.spent_usd <= c.HARD_CEILING_USD,
            "price_input_per_1m_usd": c.PRICE_IN_PER_M,
            "price_output_per_1m_usd": c.PRICE_OUT_PER_M,
            "refusals": list(self.refusals),
        }
