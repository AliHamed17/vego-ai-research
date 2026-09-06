# Study 2 future paired-run authorization template

**Status: `NOT_AUTHORIZED` · template only · no provider/API call has been made.**

This packet is a controlled checklist for a future paired `VEGO_AI_ON` /
`VEGO_AI_OFF` run. It is not an authorization, does not contain credentials,
and must not be copied into a shell until every placeholder is reviewed and a
fresh one-time human grant is issued.

## Immutable bindings required before execution

| Field | Required value/source | Current state |
|---|---|---|
| `study_id` | `VEGO-AI-STUDY-2` | frozen |
| `setting_id` | `cd_airtravel` | frozen |
| `corpus_id` | `text2uml_airtravel_253b26dc` | frozen |
| `case_ids` | `01`, `02`, `03`, `04` | frozen |
| code SHA | exact reviewed execution commit | `TO_BE_BOUND` |
| configuration SHA | canonical `study2-frozen-config-v1` hash | `TO_BE_BOUND` |
| corpus manifest/hash chain | five-file verified runtime manifest | `TO_BE_BOUND` |
| provider/model | one named provider and model | `TO_BE_FROZEN_BEFORE_FIRST_CALL` |
| temperature/tokens | exact values in the grant | `TO_BE_BOUND` |
| run ID | fresh unique identifier | `TO_BE_BOUND` |
| nonce | fresh one-time nonce | `TO_BE_BOUND` |
| budget/call caps | USD and request ceiling | `TO_BE_BOUND` |

The ON and OFF conditions must use the same corpus hashes, model parameters,
retry/timeout/concurrency policy, output schema, privacy policy, ordering and
stopping rules. Their prompts and task decomposition necessarily differ; this
is a system comparison, not an orchestration-only factor.

## Permitted execution scope

Only one paired run may be attempted. Retries are transport-only and remain
inside the frozen cap. No model switching, prompt editing, corpus replacement,
threshold change, outcome-dependent retry or second run is permitted. Llama is
outside this study and requires a separate preregistration.

The future receipt must bind before any output is interpreted:

- code, configuration and corpus hashes;
- run ID, nonce, exact start/end timestamps and attempt markers;
- ordered prompt/answer/decision hashes (not raw text);
- lifecycle/event-log hashes for ON and an explicit no-Q&A status for OFF;
- output and pipeline-manifest hashes;
- model parameters, call/token/cost counters and privacy/network counters;
- `ENGINEERING_FIXTURE_ONLY` versus provider-backed evidence class.

`VEGO_AI_OFF` has no inter-agent episode unit; its Detector-v1 denominator is
`NOT_APPLICABLE`, never zero. Study 1, fixtures, historical data and any
synthetic engineering material remain separate denominators.

## Human grant text (to be completed, not yet valid)

> I authorize exactly one paired Study 2 run at reviewed code SHA `<CODE_SHA>`
> with configuration SHA `<CONFIG_SHA>`, corpus manifest SHA `<CORPUS_SHA>`,
> run ID `<RUN_ID>`, nonce `<NONCE>`, provider/model `<MODEL>`, temperature
> `<TEMPERATURE>`, max output tokens `<MAX_TOKENS>`, budget `<BUDGET_USD>` and
> request cap `<CALL_CAP>`. The command and output root are those recorded in
> the machine manifest. No second attempt, model switch, corpus change,
> threshold change or outcome-dependent retry is authorized. This grant covers
> the named paired run only and expires at `<EXPIRY_ISO8601>`.

Until that text is completed, hashed, recorded and independently reviewed, the
execution state remains `NOT_AUTHORIZED`. No provider authorization is implied
by this template.
