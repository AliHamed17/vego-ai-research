# Study 1 executable protocol

**Protocol ID:** VEGO-S1-PRELIM-20260903
**Version:** 1.0, candidate for supervisor review
**Question answered now:** where and when do frozen VEGO-AI outputs expose candidate escalation points, and can one recorded correction be propagated deterministically?
**Not answered now:** whether a human improves accuracy, which policy is superior, how much burden is imposed, or whether results generalise.

## 1. Preconditions and abort rules

1. Run only in the isolated Study 1 worktree on the reviewed feature branch.
2. Keep the extracted C0 archive, workbooks, raw model artifacts, event tables, and full reports in the Git-ignored `research-private/study1/` workspace.
3. Calculate SHA-256 for the source archive before extraction. The approved frozen archive hash for this run is `8d37f3adb28e70b09bd095e7cf27b055c8488369aecd3628960a148d11b5b384`.
4. Abort if the archive hash differs, a source mutates during a run, output is directed outside the ignored private root, or a directive attempts to use a label as independent ground truth.
5. Do not call a cloud model, upload student material, or write to the source archive.
6. Keep the foundation manuscript separate from the evaluation-package evidence. Its 178-model/26-pattern report does not overwrite the package's 179 scored rows, 165 per-model inspection reports, and 27 pattern records.

## 2. Environment

From the repository root in PowerShell:

```powershell
uv sync --all-groups
uv run pytest -q tests/study1 scripts/tests/test_exp045_escalation_points.py scripts/tests/test_exp046_recorded_review.py
```

EXP-046 reads `.xlsx`; invoke it with a pinned transient dependency so the base environment remains locked:

```powershell
uv run --with openpyxl==3.1.5 python scripts/exp046_recorded_review.py --help
```

## 3. Frozen inputs

Set local variables to the approved private extraction and output roots. These values must never be committed.

```powershell
$studyInputRoot = Resolve-Path '<PRIVATE_EXTRACTED_ARCHIVE_ROOT>'
$studyOutputRoot = Join-Path (Resolve-Path '.') 'research-private/study1/protocol-run'
New-Item -ItemType Directory -Force -Path $studyOutputRoot | Out-Null
```

Record file size, SHA-256, relative role, and read time for every consumed file. Do not store original absolute paths in public output.

## 4. Analysis A — descriptive stage inventory (EXP-045)

```powershell
uv run python scripts/exp045_escalation_points.py `
  --vego-root $studyInputRoot `
  --out (Join-Path $studyOutputRoot 'exp045')
```

Acceptance checks:

- four settings are present;
- every count has a named denominator;
- each stage states whether reference evidence exists;
- `candidate_points` is never relabelled as error, need, or benefit;
- Stage 4 reports materialised queue objects separately from trigger-like pattern counts.

Expected aggregate receipt for the frozen input: 6/38 Stage-1 clusters, 18/28 Stage-2 clusters, 506 Stage-3 candidate signals, 11/27 Stage-4 trigger-like patterns, and 0 materialised Stage-4 queue objects.

## 5. Analysis B — recorded project review (EXP-046)

```powershell
uv run --with openpyxl==3.1.5 python scripts/exp046_recorded_review.py `
  --dataset-root $studyInputRoot `
  --json (Join-Path $studyOutputRoot 'exp046-summary.json')
```

Acceptance checks:

- “overturned” is described only as reviewer disagreement;
- the non-random, project-owned selection of reviewed items is disclosed;
- guideline completeness, compliance verdicts, and uncovered-fragment labels remain separate strata;
- course grades are not treated as item-level gold labels;
- the 78 non-comment reference-line denominator is not silently merged with EXP-045's 80 evaluator-recorded reference-guideline denominator.

Expected aggregate receipt: 186 Stage-2 review rows, comprising 169 agent-written guidelines and 17 required guidelines added because absent; 68/169 agent-written guidelines not accepted in full; 120/915 compliance judgments changed; 27/104 uncovered-fragment judgments changed; non-*Satisfied* flags cover 108/120 changes while flagging 257/915 judgments; model-score/course-grade correlation `r=0.2501` across 164 paired rows.

## 6. Analysis C — six-arm matched-budget C0 replay

```powershell
uv run python scripts/run_study1_c0_baseline.py `
  --c0-root $studyInputRoot `
  --private-output-root (Join-Path $studyOutputRoot 'c0-run-a')

uv run python scripts/run_study1_c0_baseline.py `
  --c0-root $studyInputRoot `
  --private-output-root (Join-Path $studyOutputRoot 'c0-run-b')
```

Acceptance checks:

- both runs create 1,874 events with identical stable identifiers;
- the six policy arms see the identical event table;
- budgets equal `max(1, floor(1874 × rate))`: 93, 187, and 374 at 5%, 10%, and 20%;
- random review is deterministic under seed `20260902`;
- unavailable signals remain unavailable;
- canonical run-A and run-B artifact hashes match.

Expected canonical hashes: event table `58d5219488174131cad47d470209413c61597816aa288f79e6205bd6d139ca52`; frozen manifest `ba691070aeb1b9872682571bff9d5923c8623b147159adaa4e2a58080a08dd91`; replay ledger `e2ddd7fb7ac39cd7f0d2c1592b66a0e54f44f46f799bdb5a2e42955bd56604f0`.

The proposed joint arm is expected to select zero events because several mandatory inputs are unavailable. A nonzero result produced by imputing those inputs fails this protocol.

## 7. Analysis D — one bounded recorded-correction replay

Create the private directive from an already recorded review. It must validate against `schemas/study1/study1-human-intervention-v1.schema.json`; it contains hashes and controlled labels, never raw student text.

```powershell
uv run python scripts/run_study1_human_intervention_feasibility.py `
  --case '<PRIVATE_FROZEN_CASE_JSON>' `
  --intervention '<PRIVATE_BOUND_DIRECTIVE_JSON>' `
  --scoring-schema '<PRIVATE_FROZEN_SCORING_SCHEMA>' `
  --private-output-root (Join-Path $studyOutputRoot 'intervention-run-a')

uv run python scripts/run_study1_human_intervention_feasibility.py `
  --case '<PRIVATE_FROZEN_CASE_JSON>' `
  --intervention '<PRIVATE_BOUND_DIRECTIVE_JSON>' `
  --scoring-schema '<PRIVATE_FROZEN_SCORING_SCHEMA>' `
  --private-output-root (Join-Path $studyOutputRoot 'intervention-run-b')
```

Acceptance checks:

- exactly one fragment and one contribution match the bound SHA-256;
- baseline label still matches the directive;
- baseline input is not mutated;
- only an allowed label and severity are accepted;
- the full assisted record remains private;
- the public receipt contains no case identifier or raw fragment;
- both runs are byte-identical.

Expected result: label *Alternative* to *Language Mistake*; score 17.5/27 to 16.5/27; delta −1.0; recorded-review alignment 0 to 1; sanitized receipt SHA-256 `cb36ade40b70f3bca0aac794396b6830b4142e819fa2191b40f4f607874d8e05`.

## 8. Prospective extension gate

The current analyses may be extended to outcome evaluation only after these inputs exist and are frozen:

1. independently labelled calibration and test partitions;
2. reviewer qualification-set decisions by claim type;
3. a separate claim-scoped authority/mandate registry;
4. review-time and interruption instrumentation;
5. adjudication rules and inter-rater statistic;
6. applicable ethics and data-access approvals.

The prospective primary attention budget is proposed as 10%, with 5% and 20% sensitivity runs. The comparator set adds competence-blind routing so the proposed *whom* mechanism can fail. Reviewer-conditional correctness and important-case capture are co-primary; selective risk is a ceiling. Multiplicity, power, and minimum detectable effects are frozen before test access.

## 9. Measurement contract

The denominator-audited public receipt is generated from sanitized aggregates. The current measures are descriptive and reproducibility-oriented:

| Measure | Definition | Current status |
|---|---|---|
| Review load | selected events / eligible events | Measured retrospectively for H2: 257/915 = 28.1% |
| Recorded-change coverage | changed selected events / all recorded changes | Measured retrospectively for H2: 108/120 = 90.0%; not recall |
| Recorded-change yield | changed selected events / selected events | Measured retrospectively for H2: 108/257 = 42.0%; not precision |
| Budget utilization | selected events / configured budget | Measured in the replay; not human effort |
| Stage placement | earliest lifecycle stage at which a traceable trigger is observable | Measured descriptively; no stage-superiority inference |
| Reproducibility | equality of canonical hashes across paired runs | Measured for C0 and the bounded correction |
| Important-case capture | independently important selected events / all independently important events | Prospective; blocked on independent labels |
| Reviewer-conditional correctness | final correctness conditional on reviewer assignment and qualification | Prospective; blocked on labels and qualification data |
| Human effort | review minutes, interruptions, abandonment, and queue delay per 100 eligible claims | Prospective; not observed in the archive |
| Review efficiency | adjudicated useful corrections / reviewer-hour | Prospective; cannot be inferred from review volume |

Generate the receipt with:

```powershell
uv run python scripts/validate_study1_measurements.py `
  --input docs/research/phd-proposal/2026-09-03-supervisor-review-package/study1-preliminary-results.sanitized.json `
  --output docs/research/phd-proposal/2026-09-03-supervisor-review-package/study1-metric-validation.sanitized.json
```

The command fails if category totals, denominators, matched-budget arithmetic, or paired-run evidence do not reconcile. A pass validates arithmetic and stated reproducibility only.

## 10. Reproducibility and release

```powershell
uv run ruff check src/vego_study1 tests/study1 scripts/run_study1_human_intervention_feasibility.py
uv run pytest -q
uv run python scripts/validate_study1_privacy.py
```

Only code, schemas, synthetic fixtures, aggregate numbers, and sanitized receipts may enter Git. Raw models, review notes, spreadsheets, full event tables, absolute paths, cloud identifiers, and private URLs remain excluded. Passing these checks proves technical consistency and the stated privacy boundary; it does not prove supervisor approval, human benefit, or scientific validity.
