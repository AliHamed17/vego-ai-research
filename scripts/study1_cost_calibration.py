"""Reserve-versus-actual cost calibration and a reserve-bound protocol menu.

The accepted Study 1 run is the only provider-backed observation. Its receipt records
aggregate usage only (no per-call ledger), so everything here is an aggregate: means are
computed, maxima are NOT_AVAILABLE, and nothing is attributed to an individual episode.

The reserve arithmetic is the one already frozen for Study 1B and the constrained pilot:
one request is reserved at RESERVE_INPUT_TOKENS in and MAX_OUTPUT_TOKENS out at list price.
The input reserve is a configuration constant, not a bound derived from the receipt; the
largest prompt actually sent is unknown, and that limitation is stated in the output.

The menu enumerates repeat x call-cap x output-cap protocols and reports, for each, the
reserve bound (valid only under the assumption that every prompt fits the input reserve) and
whether it fits USD 2.00 and USD 6.00. A protocol that fits is
executable only after its own preregistration and gate review; fitting is not authorisation.

Evidence class: DESCRIPTIVE_COST_CALIBRATION_FROM_ONE_ACCEPTED_RECEIPT.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from pilot_budget_constrained_config import (  # noqa: E402
    CALL_CAP_PER_REPEAT, MAX_OUTPUT_TOKENS, REPEATS, RESERVE_INPUT_TOKENS,
)

STUDY1B = {"repeats": 5, "call_cap": 326, "max_output_tokens": 16_384, "ceiling_usd": 2.00}
PILOT = {"repeats": REPEATS, "call_cap": CALL_CAP_PER_REPEAT, "max_output_tokens": MAX_OUTPUT_TOKENS,
         "ceiling_usd": 2.00}
CEILINGS = (2.00, 6.00)


def reserve_per_request(price_in: float, price_out: float, max_out: int,
                        reserve_in: int = RESERVE_INPUT_TOKENS) -> float:
    return (reserve_in * price_in + max_out * price_out) / 1_000_000


def actuals(usage: dict[str, Any]) -> dict[str, Any]:
    n = usage["outbound_requests"]
    return {
        "outbound_requests": n,
        "prompt_tokens": usage["prompt_tokens"],
        "completion_tokens": usage["completion_tokens"],
        "actual_cost_usd": usage["actual_cost_usd"],
        "mean_prompt_tokens_per_request": round(usage["prompt_tokens"] / n, 1),
        "mean_completion_tokens_per_request": round(usage["completion_tokens"] / n, 1),
        "mean_cost_per_request_usd": round(usage["actual_cost_usd"] / n, 6),
        "max_prompt_tokens_per_request": "NOT_AVAILABLE",
        "max_completion_tokens_per_request": "NOT_AVAILABLE",
        "per_episode_cost": "NOT_AVAILABLE",
        "note": "no per-call ledger was persisted; maxima and per-episode attribution cannot be computed",
    }


def calibration(usage: dict[str, Any]) -> dict[str, Any]:
    pin, pout = usage["price_input_per_1m_usd"], usage["price_output_per_1m_usd"]
    n, cost = usage["outbound_requests"], usage["actual_cost_usd"]
    rows = {}
    for name, proto in (("study1b_frozen", STUDY1B), ("pilot_frozen", PILOT)):
        r = reserve_per_request(pin, pout, proto["max_output_tokens"])
        rows[name] = {
            "reserve_per_request_usd": round(r, 7),
            "reserve_for_observed_request_count_usd": round(r * n, 4),
            "actual_cost_usd": cost,
            "reserve_to_actual_ratio": round(r * n / cost, 2),
            "mean_completion_share_of_output_cap": round(
                usage["completion_tokens"] / n / proto["max_output_tokens"], 3),
        }
    return {
        "prices_per_1m_usd": {"input": pin, "output": pout},
        "input_reserve_tokens": RESERVE_INPUT_TOKENS,
        "input_reserve_basis": ("frozen configuration constant; the largest prompt actually sent is "
                                "NOT_AVAILABLE, so the reserve is an assumption about prompt size, "
                                "not a bound derived from evidence"),
        "by_protocol": rows,
        "truncation_risk_under_pilot_cap": {
            "pilot_output_cap_tokens": MAX_OUTPUT_TOKENS,
            "mean_completion_tokens_per_request": round(usage["completion_tokens"] / n, 1),
            "mean_below_pilot_cap": usage["completion_tokens"] / n < MAX_OUTPUT_TOKENS,
            "max_completion_tokens_per_request": "NOT_AVAILABLE",
            "share_of_requests_the_cap_would_truncate": "NOT_AVAILABLE",
            "note": ("only the mean is observable from this receipt; the per-request maximum is "
                     "NOT_AVAILABLE, so the truncation share cannot be bounded; a truncated finish "
                     "must be recorded, never silently accepted"),
        },
    }


def menu(usage: dict[str, Any]) -> list[dict[str, Any]]:
    pin, pout = usage["price_input_per_1m_usd"], usage["price_output_per_1m_usd"]
    rows = []
    for max_out in (MAX_OUTPUT_TOKENS, STUDY1B["max_output_tokens"]):
        r = reserve_per_request(pin, pout, max_out)
        for cap in (CALL_CAP_PER_REPEAT, 180, STUDY1B["call_cap"]):
            for repeats in range(1, 6):
                bound = repeats * cap * r
                rows.append({
                    "repeats": repeats, "call_cap_per_repeat": cap, "max_output_tokens": max_out,
                    "reserve_per_request_usd": round(r, 7),
                    "reserve_bound_usd": round(bound, 4),
                    "fits": {f"{c:.2f}": bound <= c for c in CEILINGS},
                    "is_frozen_study1b": (repeats, cap, max_out) == (5, 326, 16_384),
                    "is_frozen_pilot": (repeats, cap, max_out) == (REPEATS, CALL_CAP_PER_REPEAT, MAX_OUTPUT_TOKENS),
                })
    return rows


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--receipt", type=Path,
                        default=ROOT / "external_data/airtravel-pr38/v4-real-run/output/run-receipt.json")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    receipt = json.loads(args.receipt.read_text(encoding="utf-8"))
    usage = receipt["usage"]
    rows = menu(usage)
    payload = {
        "schema_version": "study1-cost-calibration-v1",
        "evidence_class": "DESCRIPTIVE_COST_CALIBRATION_FROM_ONE_ACCEPTED_RECEIPT",
        "provider_calls": 0,
        "source_run_id": receipt["run_id"],
        "model": receipt["model_requested"],
        "actuals": actuals(usage),
        "calibration": calibration(usage),
        "protocol_menu": rows,
        "menu_summary": {
            f"protocols_fitting_{c:.2f}": sum(1 for r in rows if r["fits"][f"{c:.2f}"]) for c in CEILINGS
        } | {"protocols_total": len(rows)},
        "claim_boundary": ("Fitting a ceiling is arithmetic on frozen reserve constants and bounds reservations, "
                           "not spend, unless every prompt fits the 8,000-token input reserve; it is not "
                           "authorisation to run, not a prediction of actual spend, and not evidence "
                           "that a protocol would yield usable episodes. Any execution needs its own "
                           "preregistration, gate review, a present credential, and BudgetGuard set to "
                           "the authorised ceiling."),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    a, c = payload["actuals"], payload["calibration"]["by_protocol"]
    print(f"actual: {a['outbound_requests']} req, ${a['actual_cost_usd']} "
          f"(mean ${a['mean_cost_per_request_usd']}/req, {a['mean_prompt_tokens_per_request']} in, "
          f"{a['mean_completion_tokens_per_request']} out)")
    for k, v in c.items():
        print(f"  {k}: reserve/req ${v['reserve_per_request_usd']}  x{a['outbound_requests']} = "
              f"${v['reserve_for_observed_request_count_usd']}  ratio {v['reserve_to_actual_ratio']}x  "
              f"mean out share {v['mean_completion_share_of_output_cap']}")
    print(f"menu: {payload['menu_summary']}")
    for r in rows:
        if r["fits"]["6.00"] and not r["fits"]["2.00"]:
            print(f"  fits $6 only: {r['repeats']}x{r['call_cap_per_repeat']} @out{r['max_output_tokens']} "
                  f"-> ${r['reserve_bound_usd']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
