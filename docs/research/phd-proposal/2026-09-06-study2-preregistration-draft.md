# Study 2 preregistration draft — VEGO_AI_ON versus VEGO_AI_OFF

**Status: `PREPARED_NOT_EXECUTED` — requires separate independent review and fresh authorization.**

Nothing in this document has been run against a provider. No result exists. This
draft freezes the design *before* any outcome is observed so the design cannot be
chosen to fit a result afterwards.

Study 2 is **separate from Study 1**. No denominator, episode, count or artifact
from Study 1 is pooled with Study 2, and Study 1 results are not reinterpreted here.

## 1. Research question

> Holding corpus, cases, model and configuration constant, how do the produced
> artifacts, call volume, token usage, cost and elapsed time differ when VEGO-AI
> orchestration is enabled versus a defined non-VEGO baseline?

The question is comparative and **descriptive**. It does not ask which condition is
better, more accurate, or more useful, because no ground-truth labels exist.

## 2. Operational definitions

| Condition | Definition |
|---|---|
| `VEGO_AI_ON` | Full four-agent VEGO-AI orchestration: agent1 language advisor, agent2 domain advisor, agent3 model inspector, agent4 variability explorer, with the inter-agent question-and-answer protocol and the round loop bounded by `MAX_QA_ROUNDS = 10`. |
| `VEGO_AI_OFF` | A defined non-VEGO baseline: one direct model call per case pursuing the same per-case objective — map reference guidelines onto the candidate model and audit uncovered fragments — returning the same output contract. |

`VEGO_AI_OFF` must **not** contain agent decomposition, inter-agent Q&A, or a round
loop. It is not a disabled flag inside the orchestrator, and it is not a broken or
degraded system. It is a straightforward single-model implementation of the same task.

**Codex and Claude are implementation agents. They are never experimental
conditions and never appear as a row in any results table.**

## 3. The single varying factor

**VEGO-AI orchestration (on / off).** Any additional difference invalidates the
comparison or must be declared as a separate, preregistered factor.

## 4. Frozen before any output is observed

| Parameter | Value |
|---|---|
| Corpus | `text2uml_airtravel_253b26dc` |
| Setting | `cd_airtravel` |
| Case identifiers | exactly `01`, `02`, `03`, `04` — identical in both conditions |
| Provider / model | one model, identical in both conditions, recorded before the first call |
| Temperature / seed | provider default, not overridden, identical in both conditions |
| Max output tokens | identical in both conditions |
| Retry policy | at most 3 attempts per call, counted against the request cap |
| Request timeout | 180 s · run timeout 3600 s |
| Concurrency | 2 cases |
| Request cap | 326 outbound requests including retries, per condition |
| Budget cap | USD 10 hard ceiling with per-request worst-case reservation |
| Output contract | mapping rows, coverage summary, uncovered fragments |
| Stop rules | budget breach, cap breach, timeout, schema failure → stop and report |
| Privacy | private git-ignored output root; hashes and counts only in version control |

## 5. Shared outcome measures — comparable across conditions

- completed cases (of 4);
- output-schema validity per case;
- mapping rows per case;
- uncovered fragments per case;
- outbound calls;
- tokens (input and output);
- cost;
- elapsed time;
- technical failures.

Independently labelled output quality may be added **only if** a labelling plan with
human judges and an agreement measure is defined in advance. No such plan exists today.

## 6. Non-shared outcome — the decisive constraint

Detector-v1 operates on inter-agent Q&A episodes. `VEGO_AI_OFF` produces **no such
episodes**, so:

- Detector-v1 is applied to `VEGO_AI_ON` **only**;
- the Detector-v1 denominator for `VEGO_AI_OFF` is **`NOT_APPLICABLE`, never zero**;
- reporting OFF as "zero alerts" is a **category error** — absence of a measuring
  instrument is not absence of a phenomenon;
- **alert rates are never compared across the two conditions.**

## 7. Denominator rules

Separate denominators per condition. No pooling across conditions, across models, or
with Study 1. Technical failures are reported per condition and excluded from that
condition's denominator only.

## 8. Analysis plan

Descriptive counts and per-case tables only. With four cases, results are
**descriptive**: no significance test is computed and no statistical inference is
reported. Repeats, if authorized, are reported as separate runs with per-run values
and an explicit range — never averaged into a single headline figure.

## 9. Offline preflight requirement

Before any paid execution, both conditions must pass an offline fake-provider
preflight proving: no network, no credential, no provider; configuration parity;
that prompt differences arise only from the intended orchestration difference;
that outputs are separately tagged; that no cross-condition contamination occurs;
and that OFF contains no hidden Q&A. That preflight harness exists
(`scripts/study2_on_off_experiment.py`) and has been executed on fixtures only.

## 10. Authorization gates

1. Independent review of this preregistration.
2. Independent review of the implementation at one immutable head with green CI.
3. Fresh one-time offline preflight grant.
4. Independent audit of the preflight evidence.
5. **Separate** fresh authorization for each paid condition, with the model, budget
   and cap frozen in the authorization text itself.

## 11. Stop conditions

Stop and report — do not repair after the fact — if the baseline is undefined or
unrunnable, if any difference beyond orchestration is found, if the prompt-difference
receipt is missing or inconsistent, if a cap is breached, or if any credential, raw
prompt, raw answer or private path reaches version control.

## 12. Claim boundary

**Permitted:** descriptive differences in produced artifacts, calls, tokens, cost and
time, on one corpus under one configuration.

**Forbidden:** that either condition is better, more accurate, more correct, more
useful or more efficient in any quality sense; accuracy, precision, recall, F1;
alert correctness; human benefit; intervention effectiveness; representativeness;
generalization; and any statement about student behaviour or historical
Cheers/ParkWise material.

## 13. What has not been done

No provider call, no paid run, no result, no repeat count chosen, no model frozen,
no authorization requested. This document is a design, not an outcome.
