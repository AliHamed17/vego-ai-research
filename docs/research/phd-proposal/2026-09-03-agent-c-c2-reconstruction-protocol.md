# Agent-C score reconstruction and C2 bridge protocol

**Status:** technical evidence only; scientific pilot execution is not authorized.

## Purpose

This protocol reconciles arithmetic stored in the frozen Agent-C per-case JSON
with its contribution vectors and binds the locally supplied C2 spreadsheets to
their exact workbook hashes. It is a read-only technical audit. It does not
rerun an agent, create a human label, alter `VEGO-AI/eval_output`, open a sealed
holdout, or execute an intervention.

## Inputs and provenance

The frozen inputs are the 165 `agentC_case_*.json` files under the four settings
of `VEGO-AI/eval_output`. The optional external inputs are the ignored local
workbooks `VEGO-AI/analysis/scores_{ucd_ch,ucd_pw,cd_ch,cd_pw}.xlsx`. The bridge
records SHA-256, workbook filename, `compliance_vectors` sheet, and row number
before reading values. A hash mismatch fails closed. Every rejected row is then
matched by `(setting, case_id, guideline_id)` to the frozen Agent-C JSON; the
private bridge records the Agent-C JSON hash, original status/contribution, and,
only for A/B classifications, the deterministic corrected contribution.

The workbook `Score` field is treated as the recorded-review agreement flag,
not as a compliance score. Row-level judgments are rows whose score is exactly
`0` or `1`; trailing aggregate rows are excluded. A `Score=0` comment is never
silently promoted to a scientific gold label. The conservative audit classes
are:

- **A:** exact existing-schema status (`Satisfied`, `Partially-Satisfied`, or
  `Not-Satisfied`);
- **B:** deterministic spelling/short-form normalization;
- **C:** textually suggestive but not a schema-verdict;
- **D:** no usable comment.

## Reconstruction

For each case, the reconstructed total is:

`sum(compliance_contributions.score) + sum(fragment_contributions.total_contribution)`.

The signed discrepancy is `stored total_score - reconstructed total`. Both values
remain evidence fields; no representation is selected as the scientific baseline.
The implementation is `scripts/iris_score_reconstruction.py` and uses only the
Python standard library for XLSX XML parsing.

## C2 candidate boundary

The external bridge can identify technically clean counterfactual candidates,
including P-A (three explicit corrections; arithmetic exact) and P-B (six
explicit corrections; arithmetic exact). P-C remains secondary and blocked by a
score/max inconsistency. Candidate identification does not establish admissible
study cases, reviewer truth, benefit, accuracy, or superiority. Claude and the
supervisor must approve any scientific admission or correction-injection design.

## Reproduction

```powershell
python scripts/iris_score_reconstruction.py `
  --vego-root VEGO-AI `
  --analysis-root VEGO-AI/analysis `
  --output reports/generated/iris_score_reconstruction.json
```

The generated report is private and ignored. Public documentation contains only
aggregates and claim boundaries; raw comments, case identifiers, and workbook
contents are not committed.
