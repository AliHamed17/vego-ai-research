# VEGO-AI Study 1 — multi-dataset pre-execution readiness

Current status: `NO_GO_FOR_PROVIDER_EXECUTION`.

This package completed only safe metadata admission, generic label-leakage
controls, an offline engineering-fixture harness, and human-review templates.
It did not run a provider, API, model, Detector-v1 experiment, or empirical
ON/OFF comparison. Spend is USD 0.

Budget status: `BUDGET_MODEL_RATE_UNAVAILABLE`. The hard USD-6 ceiling is
recorded, but conservative per-call arithmetic cannot be frozen until one
specific user-approved OpenAI model and version are named. This is a gate, not
permission to select a model or spend.

## Dataset decisions

| Lane | Required term | State | Why it cannot run now |
| --- | --- | --- | --- |
| AirTravel | `AIRTRAVEL_QA_FEASIBILITY_BASELINE` | ARCHIVAL / RETROSPECTIVE | No new empirical claim is created or pooled. |
| QuRE | `QURE_EXTERNAL_REQUIREMENTS_QUALITY_VALIDATION` | NOT_ADMITTED | Record-specific licence, raw-file hash, and versioned inventory are not verified. |
| Local archive | `VEGO_SE_ARCHIVE_DATASET_PENDING_ADMISSION` | NOT_ADMITTED | Provenance, licence, and task fit are unverified. |

## What the new engineering controls establish

- QuRE-style external labels are structurally separated from execution cases,
  prompts, selection manifests, and model-output records.
- Deterministic selection is based on a fixed seed and input hashes, not labels.
- The local fixture harness keeps ON and OFF structurally separate: OFF has no
  agents, Q&A, rounds, Detector-v1, or Agent-4 invocation.
- The fixture harness blocks socket egress and writes only hash-safe receipts.

These are engineering controls, not empirical evidence of alert correctness,
human benefit, VEGO-AI superiority, generalisation, or model performance.

## Exact requirements before any spend

1. Capture an explicit QuRE licence and exact raw-file inventory/hash from the
   official pinned record, or receive licensor confirmation.
2. Establish provenance, licence, and a declared task for the VEGO_SE archive.
3. Freeze one explicit OpenAI model and version, supplied by the user.
   The freeze must include an immutable approval-record SHA-256; a model-like
   string alone is not a freeze.
4. Freeze case selection, model configuration, call ceiling, and conservative
   USD-6 arithmetic before any output is read.
5. Run the appropriate private, full ON/OFF fake preflight, push the immutable
   exact head, obtain green CI, and issue a separate one-time execution grant.

The pre-execution machine record is
[`multidataset-preregistration-template-v1.json`](multidataset-preregistration-template-v1.json).
