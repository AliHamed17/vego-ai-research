"""Post-hoc correction layer for agentC case scores.

Applies three corrections that a validation study showed halve the disagreement with
human graders. It reads agentC output and emits a corrected score; it does not modify
the scorer, so no protected runtime path is touched."""
from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

CRITICISM_MARKERS = (
    "without", "lack", "lacks", "missing", "unclear", "not outlined", "no clear",
    "fails", "beyond its declaration", "ambiguous", "incomplete", "unused",
    "redundant", "undefined", "vague", "inconsistent", "absent", "does not",
    "not provide", "not defined", "not specified", "no explicit", "not aligned",
    "not distinct", "without specific", "not modeled", "not represented",
)

INEXPRESSIBLE_CREDIT_FRACTION = 0.5


@dataclass(frozen=True)
class CorrectionConfig:
    """Each correction is switchable so its individual contribution stays measurable."""

    bonus_may_only_offset_penalties: bool = True
    reject_self_critical_rewards: bool = True
    inexpressible_credit_fraction: float = INEXPRESSIBLE_CREDIT_FRACTION
    cap_at_full_marks: bool = True


def fragment_contribution(fragment: dict[str, Any]) -> float:
    total = fragment.get("total_contribution")
    if total is not None:
        return float(total)
    base = float(fragment.get("base_score", 0) or 0)
    modifier = float(fragment.get("severity_modifier", 1) or 1)
    return base * modifier


def fragment_text(fragment: dict[str, Any]) -> str:
    for key in ("fragment", "description", "note"):
        value = fragment.get(key)
        if value:
            return str(value)
    return ""


def is_self_critical(text: str) -> bool:
    lowered = text.lower()
    return any(marker in lowered for marker in CRITICISM_MARKERS)


def load_expressibility(path: str | Path) -> dict[str, dict[str, str]]:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    coding = data.get("coding")
    if not isinstance(coding, dict):
        raise ValueError(f"{path} has no 'coding' object")
    return coding


def correct_case(
    case: dict[str, Any],
    expressibility: dict[str, str],
    config: CorrectionConfig | None = None,
) -> dict[str, Any]:
    config = config or CorrectionConfig()
    contributions = case.get("compliance_contributions") or []
    fragments = case.get("fragment_contributions") or []

    earned_total = 0.0
    max_total = 0.0
    reduced: list[dict[str, Any]] = []
    for entry in contributions:
        guideline_id = entry.get("guideline_id")
        earned = float(entry.get("score", 0) or 0)
        if expressibility.get(guideline_id) == "N" and earned > 0:
            withheld = earned * (1.0 - config.inexpressible_credit_fraction)
            if withheld:
                reduced.append({"guideline_id": guideline_id, "credit_withheld": round(withheld, 4)})
            earned -= withheld
        earned_total += earned
        max_total += 1.0
    if max_total == 0:
        max_total = float(case.get("max_score") or 1.0)

    rejected: list[dict[str, Any]] = []
    bonus = 0.0
    penalty = 0.0
    for fragment in fragments:
        value = fragment_contribution(fragment)
        if value > 0:
            text = fragment_text(fragment)
            if config.reject_self_critical_rewards and is_self_critical(text):
                rejected.append({"points": round(value, 4), "text": text[:200]})
                continue
            bonus += value
        elif value < 0:
            penalty += -value

    effective_bonus = min(bonus, penalty) if config.bonus_may_only_offset_penalties else bonus
    total = earned_total + effective_bonus - penalty
    if config.cap_at_full_marks:
        total = min(total, max_total)
    corrected_pct = 100.0 * total / max(max_total, 1e-9)
    original_pct = float(case.get("score_pct") or 0.0)

    return {
        "case_id": case.get("case_id"),
        "original_score_pct": round(original_pct, 4),
        "corrected_score_pct": round(corrected_pct, 4),
        "delta": round(corrected_pct - original_pct, 4),
        "corrected_total": round(total, 4),
        "max_points": round(max_total, 4),
        "bonus_raw": round(bonus, 4),
        "bonus_effective": round(effective_bonus, 4),
        "bonus_withheld": round(bonus - effective_bonus, 4),
        "penalty": round(penalty, 4),
        "guidelines_credit_reduced": reduced,
        "rewards_rejected_as_self_critical": rejected,
    }


def correct_directory(
    eval_output: Path, expressibility_path: Path, config: CorrectionConfig | None = None
) -> list[dict[str, Any]]:
    coding = load_expressibility(expressibility_path)
    results: list[dict[str, Any]] = []
    for condition_dir in sorted(p for p in eval_output.iterdir() if p.is_dir()):
        per_condition = coding.get(condition_dir.name, {})
        for case_path in sorted(condition_dir.glob("agentC_case_*.json")):
            case = json.loads(case_path.read_text(encoding="utf-8"))
            result = correct_case(case, per_condition, config)
            result["condition"] = condition_dir.name
            results.append(result)
    return results


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--eval-output", required=True, type=Path)
    parser.add_argument("--expressibility", required=True, type=Path)
    parser.add_argument("--out", type=Path)
    parser.add_argument("--credit-fraction", type=float, default=INEXPRESSIBLE_CREDIT_FRACTION)
    args = parser.parse_args()

    config = CorrectionConfig(inexpressible_credit_fraction=args.credit_fraction)
    results = correct_directory(args.eval_output, args.expressibility, config)
    payload = {"n_cases": len(results), "config": config.__dict__, "cases": results}
    if args.out:
        args.out.write_text(json.dumps(payload, ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"wrote {args.out} ({len(results)} cases)")
    else:
        print(json.dumps(payload, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
