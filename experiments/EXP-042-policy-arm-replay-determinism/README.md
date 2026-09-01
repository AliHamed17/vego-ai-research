# EXP-042 - Policy-Arm Replay Determinism

Status: Tooling added; offline mechanism run pending. Study 1 Phase A mechanism only.

Question: Do the six section-3.3 comparator arms (`never_ask`, `always_ask`, `random_at_matched_budget`, `uncertainty_only`, `fixed_threshold`, `proposed_policy`), executed as configurations of one engine over frozen synthetic fixtures at one fixed matched budget, produce identical decision sequences and budget ledgers on replay?

Run: pending a dedicated runner; the instrument is `src/vego_governed/policy.py` exercised from its tests:

```powershell
python -m pytest scripts/tests -q
```

Generated, ignored outputs: `reports/generated/exp042/` (none accepted yet).

Acceptance: two replays of the same frozen fixture set at the same `budgetId` yield identical per-arm decision sequences; per-arm `attentionAccounting` ledgers (`budgetUnitsConsumedInPeriod`, `budgetUnitsRemainingInPeriod`) match across replays; live-review and audit-sample charges stay separately counted; every declared signal appears in the per-arm decision log.

Claim boundary: determinism and ledger integrity only. NO important-case labels exist (EXP-005 is 0/24 generalization-safe labels), so no capture or effectiveness measure is computed, no arm is selected, and no arm is claimed better than another.
