# EXP-041 - Governed-Judgment Conformance

Status: Tooling added; offline mechanism run pending. This is the Study 2 Phase A instrument, not the study.

Question: Does the reference `GovernedJudgmentRecord-v1` example pass the executable conformance suite (reconstructability, discrimination, completeness-review scaffold) while every deliberately non-conforming fixture variant fails for its specific, named reason?

Run:

```powershell
python scripts/run_governed_contract_conformance.py
```

Generated, ignored outputs: `reports/generated/exp041/` (none accepted yet; the suite reports to stdout/CI until a first offline run is registered).

Acceptance: the reference example `schemas/examples/governed-judgment-record.valid.json` passes reconstructability (trace, rationale, and scope elements present, internally referenced, and resolvable from the record alone); each planted variant (scope-less, never-leaves-draft, authority-less binding, dissent-ignored) fails with its named reason; the independent-implementer completeness arm is recorded as `not_run: independent_implementer_not_recruited`, never as a pass.

Claim boundary: mechanism evidence over the reference contract and fixtures only. Conformance of the instrument is not evidence of improved judgment quality, accuracy, reduced effort, or generalization; EXP-005 remains 0/24 generalization-safe labels, QL-01..05 remain 0/5, and Study 2 Phase B stays blocked on recruited human raters and a supervisor-approved protocol.
