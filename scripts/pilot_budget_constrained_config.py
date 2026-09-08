"""Frozen configuration for the BUDGET_CONSTRAINED_EXPLORATORY_PILOT.

Frozen by docs/research/phd-proposal/2026-09-06-budget-constrained-exploratory-pilot-preregistration.md
before any provider call. These are limits, not tuning knobs: nothing here may be changed after an
outcome is observed.

This pilot is NOT a replication of Study 1 and NOT Study 1B. Its token and call limits are lower,
so its outputs are produced under a different configuration and are not comparable with, poolable
with, or a check on Study 1.

MAX_OUTPUT_TOKENS is reduced from Study 1's 16,384 to 4,096, which is 2.16x the observed Study 1
average of 1,893 completion tokens per call. RESERVE_INPUT_TOKENS is an upper bound rather than an
average: the observed average prompt was 4,339 tokens. CALL_CAP_PER_REPEAT of 90 is 2.09x the 43
calls Study 1 actually used, against a protocol minimum of 4 + 3N = 16.

The worst-case bound is proven here rather than asserted: assert_bound_fits() recomputes it from
the frozen constants and refuses to return unless it fits the ceiling. Callers must invoke it
before the first request.
"""

from __future__ import annotations

from dataclasses import dataclass

STUDY_CLASS = "BUDGET_CONSTRAINED_EXPLORATORY_PILOT"
PREREGISTRATION = (
    "docs/research/phd-proposal/"
    "2026-09-06-budget-constrained-exploratory-pilot-preregistration.md"
)

SETTING_ID = "cd_airtravel"
CORPUS_ID = "text2uml_airtravel_253b26dc"
N_CASES = 4
MODEL = "gpt-5.6-luna"

PRICE_IN_PER_M = 0.20
PRICE_OUT_PER_M = 1.20

MAX_OUTPUT_TOKENS = 4_096
RESERVE_INPUT_TOKENS = 8_000
CALL_CAP_PER_REPEAT = 90
REPEATS = 3
BUDGET_USD = 2.00
PROTOCOL_MINIMUM_CALLS = 4 + 3 * N_CASES

MAX_QA_ROUNDS = 10
MAX_CONCURRENT_CASES = 2
MAX_RETRIES_PER_CALL = 3
REQUEST_TIMEOUT_SECONDS = 180
RUN_TIMEOUT_SECONDS = 3600
ALLOWED_HOSTS = frozenset({"api.openai.com"})

RUN_IDS = tuple(f"PILOT-{i:02d}" for i in range(1, REPEATS + 1))

TRUNCATED_FINISH_REASON = "length"


class BoundExceedsCeiling(RuntimeError):
    """Raised when the frozen limits cannot be conservatively bounded under the ceiling."""


@dataclass(frozen=True)
class Bound:
    per_request_usd: float
    call_cap_per_repeat: int
    repeats: int
    total_worst_case_usd: float
    ceiling_usd: float

    @property
    def fits(self) -> bool:
        return self.total_worst_case_usd <= self.ceiling_usd

    @property
    def headroom_usd(self) -> float:
        return self.ceiling_usd - self.total_worst_case_usd

    def as_dict(self) -> dict:
        return {
            "per_request_worst_case_usd": round(self.per_request_usd, 7),
            "call_cap_per_repeat": self.call_cap_per_repeat,
            "repeats": self.repeats,
            "total_worst_case_usd": round(self.total_worst_case_usd, 6),
            "ceiling_usd": self.ceiling_usd,
            "headroom_usd": round(self.headroom_usd, 6),
            "fits": self.fits,
            "method": (
                "every permitted call priced at the full reserve; retries counted against the "
                "call cap; not extrapolated from any prior run"
            ),
        }


def per_request_reserve_usd() -> float:
    return (
        RESERVE_INPUT_TOKENS * PRICE_IN_PER_M + MAX_OUTPUT_TOKENS * PRICE_OUT_PER_M
    ) / 1_000_000


def global_bound() -> Bound:
    reserve = per_request_reserve_usd()
    return Bound(
        per_request_usd=reserve,
        call_cap_per_repeat=CALL_CAP_PER_REPEAT,
        repeats=REPEATS,
        total_worst_case_usd=reserve * CALL_CAP_PER_REPEAT * REPEATS,
        ceiling_usd=BUDGET_USD,
    )


def assert_bound_fits() -> Bound:
    """Refuse to proceed unless the whole plan fits the ceiling. Call before the first request."""
    bound = global_bound()
    if not bound.fits:
        raise BoundExceedsCeiling(
            f"worst-case bound ${bound.total_worst_case_usd:.4f} exceeds the "
            f"${bound.ceiling_usd:.2f} ceiling; the frozen limits do not permit this pilot"
        )
    if CALL_CAP_PER_REPEAT < PROTOCOL_MINIMUM_CALLS:
        raise BoundExceedsCeiling(
            f"call cap {CALL_CAP_PER_REPEAT} is below the protocol minimum "
            f"{PROTOCOL_MINIMUM_CALLS}; a cap that cannot complete the protocol is not a pilot"
        )
    return bound


def frozen_config() -> dict:
    """The configuration a receipt must bind, in one canonical shape."""
    return {
        "study_class": STUDY_CLASS,
        "preregistration": PREREGISTRATION,
        "not_a_replication_of_study1": True,
        "comparable_with_study1": False,
        "setting_id": SETTING_ID,
        "corpus_id": CORPUS_ID,
        "n_cases": N_CASES,
        "model": MODEL,
        "max_output_tokens": MAX_OUTPUT_TOKENS,
        "reserve_input_tokens": RESERVE_INPUT_TOKENS,
        "call_cap_per_repeat": CALL_CAP_PER_REPEAT,
        "repeats": REPEATS,
        "budget_usd": BUDGET_USD,
        "max_qa_rounds": MAX_QA_ROUNDS,
        "max_concurrent_cases": MAX_CONCURRENT_CASES,
        "max_retries_per_call": MAX_RETRIES_PER_CALL,
        "request_timeout_seconds": REQUEST_TIMEOUT_SECONDS,
        "run_timeout_seconds": RUN_TIMEOUT_SECONDS,
        "allowed_hosts": sorted(ALLOWED_HOSTS),
        "run_ids": list(RUN_IDS),
        "price_input_per_1m_usd": PRICE_IN_PER_M,
        "price_output_per_1m_usd": PRICE_OUT_PER_M,
    }


def config_sha256() -> str:
    import hashlib
    import json

    payload = json.dumps(frozen_config(), sort_keys=True, ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


if __name__ == "__main__":
    import json

    bound = assert_bound_fits()
    print(json.dumps(
        {"bound": bound.as_dict(), "config_sha256": config_sha256(), "config": frozen_config()},
        indent=2, sort_keys=True,
    ))
