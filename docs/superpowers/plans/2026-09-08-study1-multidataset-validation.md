# VEGO-AI Study 1 Multi-Dataset Validation

## Authority and base

This plan implements the user-supplied 2026-09-08 Study 1 Multi-Dataset
Validation instruction.  It starts from PR #41 head
`f36cf96f34fa6d85625a027516aa202baa432fcf` on branch
`feature/study1-multidataset-baseline`.  The resulting work is a stacked,
draft follow-up until PR #41 is independently reviewed and merged.

## Global constraints

- Preserve AirTravel as `AIRTRAVEL_QA_FEASIBILITY_BASELINE`; do not rerun,
  reinterpret, or pool archival evidence.
- Acquire QuRE only from the user-pinned Zenodo concept DOI
  `10.5281/zenodo.15656471`, retaining the resolved version identity.
- Treat the supplied software-engineering archive as
  `VEGO_SE_ARCHIVE_DATASET_PENDING_ADMISSION` until its provenance, licence,
  task fit, privacy, and independent validation artifacts are verified.
- Raw data and provider outputs stay in ignored `external_data/` paths.
- No label leakage, fabricated data, pooled denominators, accuracy claim,
  benefit claim, or detector-threshold change.
- Provider work is OpenAI-only, one frozen user-approved model, one retry only
  for documented transport failure, and no more than USD 6.00 total.
- A real provider run is forbidden until every pre-execution gate passes,
  green CI binds the exact head, and the model is explicitly frozen.

## Task 1: Dataset discovery and admission evidence

Create a data-admission layer for QuRE and the local VEGO-SE archive:

- retrieve metadata and bytes only from the allowed QuRE source;
- produce safe data cards, inventory receipts, licences, hashes, and
  provenance/admission decisions;
- inspect a supplied archive using metadata before content, and fail closed
  when it is missing, unsafe, or not admissible;
- add tests for source pinning, missing files, safe archive inventory, and
  non-admission states.

## Task 2: Leakage-safe adapters and deterministic case selection

Implement adapters and manifests that:

- select QuRE cases through an executable fixed-seed predicate;
- expose text to the pipeline while retaining labels solely in the evaluation
  layer;
- record hashes, case IDs, selection, privacy class, and evidence class;
- provide safe no-data/blocked states for VEGO-SE;
- include test-first coverage for leakage, drift, determinism, and private
  output containment.

## Task 3: Matched ON/OFF and budget-control implementation

Implement a configuration-bound ON/OFF runner and budget packet that enforce
the same model, temperature, tokens, timeout, retry, concurrency, output
schema, case hashes, call limits, egress boundary, and private output root.
OFF must never invoke agents, Q&A, Detector-v1, or Agent-4.  Detector-v1 is
ON-only and `NOT_APPLICABLE` for OFF.

## Task 4: Offline fake-provider preflight

Run only deterministic local fake-provider preflight for each admitted
dataset/condition.  Validate lifecycle, receipts, error containment, label
separation, budget/call control, output validation, and post-run privacy.  No
provider SDK, credential, external model, or real experiment is used here.

## Task 5: Reporting, human-review preparation, and final gates

Generate the required data-admission report, evidence index, human-review
rubric/cards, decision table, Hebrew RTL report/deck/diagram, and executive
summary from evidence-bound structured sources.  Render and inspect every
page/slide.  Run the full test, schema, compile, lint, privacy, security,
evidence-consistency, and manifest suite.  Push one immutable draft PR and
require green CI.

## Task 6: Conditional real provider execution

Only after Tasks 1-5 pass and an explicit model selection is present:

- generate the exact pre-execution packet and conservative USD 6.00 proof;
- confirm a clean exact head, single model, call cap, output root, and OpenAI
  endpoint-only egress;
- execute at most one pre-registered provider-backed run per admitted lane;
- recompute results from raw private evidence, without pooling datasets;
- stop on every failure or cap breach and report `BUDGET_NO_GO` or
  `TECHNICAL_NO_GO` as applicable.

## Initial rulings

1. Use the reviewed PR #41 head as the stacked base rather than unpublished
   local `study1/full-frame-and-baselines` commits.  This avoids silently
   inheriting unreviewed scientific scope; cost if wrong: later port a
   deliberately reviewed change.
2. The user-pinned QuRE concept DOI must govern version selection; a newer
   record is not substituted merely because it exists.  Cost if wrong: a
   later explicit version amendment may be needed.
3. “You can use budget” authorizes spending up to the stated USD 6.00 cap but
   does not name the single frozen model required by the plan.  All offline
   work proceeds; a provider call remains blocked pending that exact choice.
