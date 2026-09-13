# AirTravel API Execution Gate Design

**Status:** proposed implementation design; no provider call authorized by this document

## Purpose

Run one reproducible, budget-capped VEGO-AI Study 1 replication on the public
Text2UML AirTravel setting only.  The run will describe the system's observed
Q&A episodes and Detector-v1 reporting labels.  It will not claim correctness,
benefit, human-effort reduction, generalisation, or comparative superiority.

## Scope and non-scope

### In scope

- Public external setting: `setting_id=cd_airtravel`,
  `corpus_id=text2uml_airtravel_253b26dc`.
- A frozen, byte-verified five-file runtime pack: one domain description and
  four candidate models, with reference models excluded from every
  provider-visible input path.
- One new, isolated execution runner with an OpenAI API adapter, a private
  ignored output root, hash-bound receipts, and an aggregate-only reporting
  exporter.
- A deterministic fake-provider preflight before any real call.

### Explicitly excluded

- Historical VEGO-AI/Cheers/ParkWise ZIP content, `VEGO-AI/models`, expert
  worksheets, GUI exports, `interaction_log` full content, and `user_actions`
  logs.  These are controlled data and must not reach an external provider.
- QuRE (the likely meaning of “qoule”).  It remains `NOT_ADMITTED` until its
  exact source, version, licence, hashes, task fit, and data-transfer authority
  are recorded.
- Reference-model bytes, synthetic gap filling, corpus modification, Detector-v1
  threshold changes, protected-runtime edits, automatic human correction, and
  any reuse of a prior authorization token or receipt.

## Design decisions

### 1. Separate execution lane

The runner will be added on a new branch from `origin/main` and will not call
the legacy generic `VEGO-AI/framework/orchestrator.py` directly.  That legacy
path does not currently enforce a whole-run USD cap, one-time grant, immutable
input manifest, or host-only egress policy.

The lane has three commands:

1. `prepare`: validate source/archive/runtime bytes and create an immutable
   private input manifest.
2. `preflight`: run the exact configuration through a deterministic local fake
   provider.  It proves configuration loading, prompt construction, event
   persistence, lifecycle validation, containment, and call-counter behavior.
3. `execute`: remains unavailable unless the supplied one-time authorization
   validates the exact code SHA, command fingerprint, input manifest hash,
   provider/model parameters, budget/call caps, output root, and expiry.

The implementation must make a real provider call impossible from `prepare`
and `preflight`.

### 2. Public input and reference separation

Before any request, the runner checks:

- upstream archive SHA-256:
  `8cf82e2ab2d2ce3da9a7ec4165e760ae1e0d9af14468f5aa2a3883037d8da701`;
- pinned upstream commit:
  `253b26dc704d523209a5cba79686f8f7fab57d63`;
- all 143 AirTravel source-manifest entries;
- exactly five runtime files, their declared paths, byte lengths, and hashes;
- no reference file, symlink/reparse point, extra file, or unverified path is
  present under the runtime-visible root.

The provider input is constructed only from the frozen description and the
four selected candidate models.  The selection rule and the five hashes are
part of the manifest; no filename-only or mutable-directory selection is
accepted.

### 3. Budget, call, timeout, retry, and egress controls

The execution configuration must set and bind all of the following before a
call:

- exact OpenAI model identifier and price schedule source/date;
- maximum total spend of USD 6.00, with conservative reservation for every
  allowed request before the first real request;
- deterministic call cap derived from the frozen configuration; the currently
  documented `N=4` static range is minimum `16` and maximum `326`, but the
  selected cap must be recomputed by the implementation and bound in the
  receipt;
- per-call timeout, whole-run timeout, retry policy, concurrency, and maximum
  output tokens;
- the sole permitted provider host: `api.openai.com`;
- a blocked-attempt ledger for any other base URL or network path.

Before every request, the runner verifies that both the remaining call cap and
the remaining reserved USD budget can cover that request.  A timeout, retry,
cost uncertainty, malformed response, or cap breach terminates the run with a
technical status; it is never converted into an empty scientific result.

### 4. Private evidence and receipt model

All raw inputs, prompts, answers, event records, usage data, and derived
pipeline files live only beneath a newly created ignored root:

`external_data/airtravel-api-runs/<run_id>/`

The runner refuses absolute paths outside this root, traversal, symlinks,
reparse points, unexpected sibling roots, or a pre-existing nonempty run
directory.  Git-tracked output consists only of code, schemas, tests, a
sanitized protocol, and a receipt template with no private hashes, paths,
prompt text, answer text, or credentials.

The private run receipt binds the input manifest, execution code SHA,
configuration, event-log hash, pipeline-output hash, cost/call ledger, model,
provider host, Detector-v1 version, lifecycle summary, and containment check.

### 5. Scientific interpretation

The unit of Detector-v1 analysis is a complete Q&A episode.  `STRONG_ALERT`,
`WEAK_ALERT`, and `NO_ALERT` remain reporting-level candidate labels only.
They do not prove a model error, a correct human intervention point, a human
benefit, or a need for automatic correction.  Zero Q&A episodes remains a
valid reportable outcome if the lifecycle receipt is complete.

Agent-4's variability-classification queue is independent of Detector-v1.  It
may be reported only when a validated queue artifact exists; otherwise its
status is `NOT_AVAILABLE`.

## Acceptance criteria

The code is ready for a one-time execution request only if all are true:

1. Source, runtime, selection, configuration, and code hashes verify.
2. Deterministic fake-provider preflight passes with zero external calls.
3. Tests prove budget, call, timeout, retry, egress, containment, lifecycle,
   reference-separation, and receipt-tamper failure paths.
4. A current branch has passed CI on its exact SHA.
5. A human signs a new, time-limited authorization naming the provider, model,
   budget, call cap, input manifest, command fingerprint, output root, and
   allowed host.

Until all five conditions hold, status is `PREFLIGHT_PREPARED_AWAITING_FRESH_EXECUTION_GRANT`.

## Rollback

No protected runtime or corpus bytes are modified.  Removing the branch or
private ignored output root removes this lane without changing the legacy
pipeline.  A failed or cancelled run remains recorded only in its private
receipt and is never pooled into a scientific denominator.
