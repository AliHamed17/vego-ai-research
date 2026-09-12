# VEGO-AI Study 2: ON/OFF system comparison (preregistration-ready draft)

**Status:** `PREPARED_NOT_EXECUTED`
**Evidence boundary:** This document specifies a future comparison and its deterministic engineering preflight. It contains no scientific observations or scores.

## Question and intervention

Study 2 asks whether the complete VEGO-AI system workflow produces a different,
reproducible per-case assessment artifact from a direct one-call baseline when
the corpus, case identifiers, model configuration, output objective, retries,
timeout, concurrency, privacy controls, and stopping rules are held fixed.

The intervention is a **SYSTEM_COMPARISON**, not a claim that only an
orchestration switch changes. The ON system changes prompt structure and task
decomposition as well as enabling inter-agent Q&A; the OFF system intentionally
removes those structural components.

| Condition | Definition | Detector-v1 denominator |
|---|---|---|
| `VEGO_AI_ON` | Role-scoped multi-agent workflow with inter-agent Q&A and bounded rounds | Applicable to ON episodes only |
| `VEGO_AI_OFF` | One direct per-case model workflow; no agents, Q&A, or round loop | `NOT_APPLICABLE` (never zero) |

No ON/OFF alert-rate comparison is planned. Detector-v1 is not a shared outcome
because OFF has no inter-agent episode unit.

## Frozen inputs and controls

The machine authority is [`study2-frozen-config.json`](study2-frozen-config.json).
It binds `setting_id=cd_airtravel`,
`corpus_id=text2uml_airtravel_253b26dc`, four case IDs (`01`–`04`), the pinned
Text2UML source commit and manifest hash, and the selected five-file metadata
manifest (one domain description and four candidate models). The raw corpus is
not committed here.

Before any real call, the model identity and provider must be frozen. The draft
therefore uses `TO_BE_FROZEN_BEFORE_FIRST_CALL`; this is a gate, not a result.
Temperature, maximum output tokens, timeout (180 seconds), one retry, maximum
concurrency (2), cost ceiling (USD 10), and call ceiling (326) are enforced by
the same runner for both conditions. Every attempt, token count and cost is
recorded. A timeout, malformed response, secret, path violation, exhausted
retry, cost ceiling or call ceiling failure is terminal for that case/condition.

## Shared objective and artifacts

Both conditions must return the same strict case contract:

1. `existing_mapping` (an array of guideline mappings);
2. `coverage_summary` with `satisfied`, `partially_satisfied`, and
   `not_satisfied` counts;
3. `uncovered_fragments` (an array of classified fragments).

Required arrays are validated, not normalized. Missing or invalid arrays are
`TECHNICAL_FAILURE`, never an empty successful result. Each condition persists
only privacy-safe aggregates, prompt hashes, hashes of its event log and result
file, a pipeline-output manifest, and a run receipt. Raw prompts, answers,
model output, credentials, and corpus bytes are not persisted by the fixture
runner.

The receipt self-binds run identity, code SHA, corpus hashes, configuration
hash, prompt hashes (through the condition result), lifecycle summary, event-log
hash, pipeline manifest hash, result-file hashes, ordered attempt markers,
token/cost counters, and privacy counters. `scientific_result_status` remains
`NOT_EXECUTED` for the fixture suite.

## Engineering preflight

The command `scripts/study2_on_off_experiment.py` accepts an explicit output
root and approved parent root. It uses only
`vego_study2.fixtures.DeterministicFixtureClient`; it contains no provider
adapter or network path. The preflight exercises:

- valid ON/OFF outputs over all four cases;
- a no-Q&A ON fixture;
- malformed JSON and missing required fields;
- timeout and retry exhaustion;
- cost and call ceilings;
- output-root traversal, sibling paths, symlinks/reparse points;
- secret leakage rejection;
- deterministic prompt and normalized receipt hashes;
- ON episode lifecycle records (including converged and maximum-round states);
- OFF zero Q&A with Detector-v1 `NOT_APPLICABLE`.

All fixture outputs are explicitly `ENGINEERING_FIXTURE_ONLY` and are excluded
from every scientific denominator. A passing preflight demonstrates that the
instrument can enforce and record the protocol; it does not estimate accuracy,
quality, usefulness, human benefit, generalization, or which condition is
better.

## Future evaluation plan

After independent review, fresh authorization, a frozen provider/model and a
separate approved run, blinded human assessors will score the shared output
objective on five dimensions: factual alignment to the case model, coverage of
reference guidelines, unsupported claims, usefulness of uncovered-fragment
analysis, and schema completeness. The rubric is supplied separately in
`study2-quality-evaluation-template.md`. No scores are created in this phase,
and no LLM judge is used without a new frozen protocol.

## Separation and claims

Study 1 descriptive and retrospective-provenance records remain separate from
Study 2. Historical Cheers/ParkWise evidence is not an admissible Study 2
denominator. Engineering fixtures are not pooled with public-external,
historical, recovered, or future human-labelled evidence. The only current
status is `PREPARED_NOT_EXECUTED`.

## Gates before a real run

1. Supervisor/preregistration review.
2. Immutable implementation head with green CI.
3. Verified source/runtime manifest and privacy review.
4. Frozen provider, model identity, token policy, budget and call policy.
5. Fresh one-time authorization bound to the exact command, output root and
   hashes.
6. Independent human assessment and adjudication before any quality claim.
