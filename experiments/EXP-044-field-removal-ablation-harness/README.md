# EXP-044 - Field-Removal Ablation Harness

Status: Tooling added; offline mechanism run pending. Explicitly INSTRUMENT validation for Study 2 Phase B, not the study itself.

Question: Do the ablation hook points in `GovernedJudgmentRecord-v1` (`ablation.mode = "field_removal"`, `withheldComponents` naming exactly one of `rationale`, `scope`, `authority`, `retainedDissent`, `provenance`, `lifecycle`, `strikeMethod = "delete_top_level_property"`, profiles `GJR-ABL-01..06`) make each governed component individually strikeable and identifiable when exercised against the intact reference example?

Run: pending a dedicated runner; the instrument is the schema's ablation block plus `src/vego_governed/records.py` exercised from tests:

```powershell
python -m pytest scripts/tests -q
```

Generated, ignored outputs: `reports/generated/exp044/` (none accepted yet).

Acceptance: the intact reference example `schemas/examples/governed-judgment-record.valid.json` validates under `ablation.mode = "none"`; each of the six single-component strikes over that example validates under `field_removal` with the struck top-level property absent (schema checks CHK-03..CHK-08) and with `profileId`, `harnessId`, and `harnessVersion` recorded; no strike removes more than its one named component; the CHK-18 suspension under a declared field-removal ablation behaves as the schema states, so a struck component is never reported as non-conformance.

Claim boundary: instrument-readiness evidence over the reference example only, not the Study 2 Phase B ablation study. No effect of any withheld component on human judgment is measured or claimed; EXP-005 remains 0/24 generalization-safe labels and Phase B stays blocked on recruited raters and a supervisor-approved protocol.
