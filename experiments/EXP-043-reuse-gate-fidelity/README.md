# EXP-043 - Reuse-Gate Fidelity

Status: Tooling added; offline mechanism run pending. Study 3 Phase A mechanism precursor only.

Question: Does the reuse-gate engine evaluate the five gates in their frozen order (`g1_visibility_authorization` -> `g2_claim_relevance` -> `g3_context_fit` -> `g4_current_case_evidence` -> `g5_adaptation_risk`), short-circuit so a gate-1 failure leaves gates 2-5 unevaluated with no restricted evidence exposed, reach all four outcomes from fixtures, and emit a consistent outcome receipt per evaluation?

Run: pending a dedicated runner; the instrument is `src/vego_governed/reuse.py` exercised from its tests:

```powershell
python -m pytest scripts/tests -q
```

Generated, ignored outputs: `reports/generated/exp043/` (none accepted yet).

Acceptance: gate order proven by test; on a gate-1 `fail` or `undetermined`, gates 2-5 are `not_evaluated` and `restrictedEvidenceExposed` is `false`; all four outcomes (`reuse_eligible`, `reuse_eligible_with_adaptation`, `reuse_blocked`, `reuse_undetermined`) are reachable by fixtures; `reuse_undetermined` routes to independent review and is never collapsed into allow/block; every decision names its `ruleId` and `contextDimensionId`; an outcome receipt is emitted for every evaluation.

Claim boundary: gate-order, non-exposure, reachability, and receipt mechanism evidence over fixtures only. No cross-context reuse benefit, capability-gap, accuracy, effort, or generalization claim is made; EXP-005 remains 0/24 generalization-safe labels and Study 3 Phases A/B stay blocked on real labels and supervisor-approved protocols.
