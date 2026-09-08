# Study 2 ON/OFF control hardening

**Status:** `PREPARED_NOT_EXECUTED` · implementation review follow-up

This note records the code-grounded correction to the 2026-09-06 independent
implementation review. It does not authorize a provider, model, paid run,
Detector-v1 analysis, or scientific experiment.

## Controlled execution path

`vego_study2.runner.Study2Runner` is the only controlled Study 2 fixture path.
It accepts a client only when the client explicitly declares `offline_only=True`
and rejects any configuration whose network policy is not `DISABLED` with an
empty host allow-list. The actual request site binds and checks the frozen model
identity, temperature, per-call output-token ceiling, timeout, condition, call
ceiling, cumulative cost reservation, retry count, and concurrency semaphore.
The common socket connection entry points used by clients are blocked for the
run and increment `privacy_counters.blocked_egress_attempts`; non-finite usage
values are rejected before they can evade the cost ceiling. The approved root
remains lexical until path validation, so symlink/reparse-point roots are
rejected rather than resolved away.

The low-level `study2_vego_off_baseline.py` module remains a strict parser and
prompt utility only; its historical unbound executor now fails closed rather
than accepting an arbitrary client. It is not a paid-run harness. The legacy
protected-runtime helpers fail closed, and the CLI rejects an invocation
without `--allowed-root`. The Study 2 comparison must use the controlled
package runner.

## Evidence and receipt binding

Each condition records the same model, execution policy, corpus hashes, and
fixture-case input hashes. The run receipt binds both condition artifacts,
pipeline manifests, lifecycle summaries, controls, and privacy counters. A
canonical SHA-256 binding covers the complete receipt excluding its own binding
field. `validate_persisted_receipt` rechecks the binding, result/event/manifest
hashes, strict result schema, condition identity, and ON/OFF symmetry before a
comparison is returned.

Malformed or missing condition output is `TECHNICAL_FAILURE`; it is never
coerced into a successful empty result. `VEGO_AI_ON` is the only condition to
which Detector-v1 is applicable. The fixture does not execute Detector-v1, and
`VEGO_AI_OFF` remains `NOT_APPLICABLE`, not zero.

## Interpretation boundary

Study 2 is a **system comparison**, not a claim that orchestration alone is the
only varying factor. Prompt text, task decomposition, call structure, and
control flow necessarily differ. Fixture mapping/fragment volumes are labelled
`NOT_COMPARABLE_AS_QUALITY`; no accuracy, correctness, benefit, superiority, or
generalisation claim is produced. Study 1 artifacts are not pooled.

Detector-v1 remains a Q&A-episode, reporting-level candidate label and never
writes a queue. The separate Selective Intervention Policy / Agent-4 mechanism
may create `human_review_queue.jsonl` only when its queue builder is explicitly
run. For AirTravel, queue status is `NOT_AVAILABLE` unless a validated queue
artifact is mounted; absence is not a zero or a “not triggered” finding.

## Study 1B gate

The five-repeat Study 1B variance protocol was reviewed independently before
execution. The current PR branch now records its closed state:
`BUDGET_BLOCKED_UNDER_FROZEN_PROTOCOL`. Its immutable five-repeat protocol has
a conservative whole-plan bound of USD 34.6551 against the authorized USD 2.00
ceiling, so it cannot execute. The pre-run verdict is therefore `REJECT` and
there is no Study 1B run, provider call, credential use, or variance result.
The separately prepared budget-constrained exploratory pilot is not a Study 1B
replacement and cannot answer the repetition-stability question because its
token and call limits differ. No authorization is issued here.
