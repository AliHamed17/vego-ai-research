"""Single source of truth for Study 1 communication-signal definitions."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

S6_OPERATIONAL_DEFINITION = {
    "signal": "S6_MULTIPLE_QA_ROUNDS",
    "rule": 'episode.get("round_count", 0) > 1',
    "unit_of_analysis": "Q&A episode",
    "source_field": "round_count",
    "description": "The projected episode contains more than one Q&A round.",
    "measurement_kind": "deterministic_derived_field",
}


def s6_fires(episode: Mapping[str, Any]) -> bool:
    """Apply the frozen S6 predicate exactly once through this module."""

    return episode.get("round_count", 0) > 1
