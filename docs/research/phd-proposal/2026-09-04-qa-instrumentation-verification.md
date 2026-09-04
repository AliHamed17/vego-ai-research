# Q&A Instrumentation Verification — 2026-09-04

**Technical verdict:** PARTIAL — the offline observer, v1.0.1 contract, and protected
orchestrator fixture pass; production persistence wiring remains a reviewed follow-up. This
is not a scientific study result and is not approval for a live LLM run.

## Touched runtime paths

- `VEGO-AI/framework/qa_communication.py` — append-only event writer, schema
  validation, deterministic IDs, route observer, and episode projection.
- `VEGO-AI/framework/qa_instrumented_runner.py` — pass-through deterministic
  client proxy and offline protected-path parity harness; not a provider client.
- `VEGO-AI/framework/qa_registry.py`, `VEGO-AI/framework/orchestrator.py`, and
  `VEGO-AI/framework/state.py` were inspected but not modified: their protected
  runtime hashes are locked by the evidence guard. The observer is therefore
  provided as an additive adapter for a separately reviewed runner integration;
  no scientific behavior changed.
- `schemas/qa-communication-event-v1.schema.json` — dedicated live contract;
  the historical `qa-escalation-event-v1` meaning is unchanged.
- `scripts/extract_qa_escalation_features.py` — live episode projection and
  `ANSWER_NOT_PERSISTED` terminology correction for frozen extraction.

## Event architecture

The adapter writes append-only `QUESTION_EMITTED`, `ANSWER_RECEIVED`,
`EPISODE_CONTINUED`, and `EPISODE_TERMINATED` events. Each event contains a
stable `event_id`, sequence, episode/question identifiers, source/target/stage,
round, termination/convergence fields, and source provenance. Text is represented
by UTF-8 SHA-256 and character length; raw prompts and responses are not written.
`build_episode_projection` deterministically derives episode-level counts,
confidence values, evidence presence, follow-up state, convergence, termination,
and source/target pairs.

## Offline routes and fixtures

The offline runner executes the protected `orchestrator.run` path and then each
protected Q&A helper route against a deterministic fake. The adapter can
represent all existing advisor routes through the shared helpers:

| Route | Runtime support |
|---|---|
| Agent 2 → Agent 1 | adapter-supported |
| Agent 2 → Agent 2 | adapter-supported |
| Agent 3 → Agent 1 | adapter-supported |
| Agent 3 → Agent 2 | adapter-supported |
| Agent 4 → Agent 1 | adapter-supported |
| Agent 4 → Agent 2 | adapter-supported |

No route was invented and no provider/model client was invoked by verification.

## Verification results

- Synthetic episodes: 8 deterministic episode paths (baseline, six route
  representations, and one follow-up/`MAX_QA_ROUNDS` episode).
- Prompt/scientific-state parity: instrumented and non-instrumented protected
  fixture runs match exactly; the proxy is post-call and pass-through.
- Concurrent route context: separate async tasks retain their own source/target
  metadata; no global current-episode state is used.
- Decision parity: no decision object is read or changed by the observer.
- Deterministic repeatability: event IDs and sequence values are stable for the
  same run ID and fixture order.
- Malformed events: schema, sequence, duplicate-ID, and unknown-answer references
  fail closed with `QACommunicationValidationError`.
- Privacy: only hashes/lengths are persisted; no raw Q&A text is emitted.
- Baseline mutation: frozen evaluator artifacts are not read-modified-written.

## Input availability and one-setting preparation

The evaluator configuration declares four settings. Their domain descriptions
are present locally, but all configured historical case-model directories are
absent from this checkout:

| Setting | Status | Missing input |
|---|---|---|
| `ucd_ch` | BLOCKED | Cheers use-case case-model directory |
| `ucd_pw` | BLOCKED | ParkWise use-case case-model directory |
| `cd_ch` | BLOCKED | Cheers class-diagram case-model directory |
| `cd_pw` | BLOCKED | ParkWise class-diagram case-model directory |

Historical question-emission counts are selection context only: `cd_pw=6`,
`cd_ch=3`, `ucd_ch=2`, `ucd_pw=1`. Because no setting is complete, no
recommended executable setting can be selected. If inputs become available,
the deterministic rule is to choose the complete setting with the highest
historical count, breaking ties lexicographically.

## Cost and call estimate

No live model run was performed. Baseline-call count, Q&A-loop calls, model
pricing, and API cost are therefore **TO BE MEASURED BEFORE RUN** from the
selected setting's dry-run structure and current provider pricing. No estimate
has been fabricated.

## Remaining gaps

Independent prompt/decision hash manifests over a real controlled run, complete
case-model inputs, and human review remain outstanding. This document does not
claim accuracy, recall, precision, human benefit, policy superiority, or
successful scientific evaluation. A reviewed runtime integration is required
before a controlled one-setting run.
