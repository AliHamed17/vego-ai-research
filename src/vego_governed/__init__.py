"""Reference engines for the governed-judgment contracts (PR #31 schemas).

Deterministic, offline, no LLM/API calls. Operates instances of
ReviewPolicySignalContract-v1, GovernedJudgmentRecord-v1, and
ReuseDecisionRecord-v1. Design artifacts only: nothing here asserts an
empirical outcome (EXP-005 0/24, QL-01..05 0/5, medical gates 0/6).
Sibling of the protected src/vego_hlayer/ package; this package is
intentionally outside the H-layer authorization boundary.
"""

__all__ = ["lifecycle", "policy", "reuse", "records"]
