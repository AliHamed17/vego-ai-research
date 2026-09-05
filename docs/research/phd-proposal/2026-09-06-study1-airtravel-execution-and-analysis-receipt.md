# Study 1 AirTravel — execution and analysis receipt

## Verdict

`TECHNICAL_NO_GO`: the engineering-only fake preflight passed, but the one
authorized provider-backed run ended `INCOMPLETE_TECHNICAL` before any complete
Q&A episode existed. Detector-v1 and the renderer were not run.

## Binding and provenance

| Field | Value |
|---|---|
| PR head with reports | `baca488e4f1137c80aefb8e91c097c1b547a3a03` |
| Head used by the provider run | `12f3faa0b3a3a5269349ce7132d49ff532248bfb` |
| Setting | `cd_airtravel` |
| Corpus | `text2uml_airtravel_253b26dc` |
| N | 4 |
| Classification | `PUBLIC_EXTERNAL + EXTERNAL_LLM_GENERATED` |
| Source verification | 143/143 matched; 0 missing, extra, or mismatched |
| Runtime pack | 5/5 files matched; configuration PASS; references not visible |
| Runtime archive | `e37baecd20a0c84eb1d9b87b3b78a23bc4b4eb8a9824ad3086dc30aa35fdd31f` |
| Source/runtime receipt | `docs/research/phd-proposal/airtravel-pr38-correction/source-runtime-receipt.json` |

The source receipt is retained as the source-verification record. The raw
archive, runtime bytes, and all run outputs remain outside Git and are not
redistributed here.

## Offline fake preflight (engineering evidence only)

The final-head preflight was executed once with a fresh one-time grant in an
isolated checkout. A separate read-only validation pass revalidated the receipt
and private layout.

| Metric | Result |
|---|---|
| Receipt | `TECHNICAL_SUCCESS` |
| Direct / instrumented calls | 46 / 46 |
| Combined fake calls | 92 |
| Events / questions / answers | 50 / 20 / 20 |
| Episodes / terminations | 10 / 10 |
| Termination states | 10 `CONVERGED` |
| Route pairs | 6 |
| Prompt, answer, decision parity | PASS / PASS / PASS |
| Pipeline/scientific-artifact parity | PASS / PASS |
| Containment/privacy | PASS / PASS |
| Network, provider, credential, Detector, renderer counters | all 0 |
| Private receipt SHA-256 | `d951a7baefaf0733282b4f81a82fb815f609d03a68bfa32caa832d6fe795a2fb` |
| Event-log SHA-256 | `fccac69b565fc278301b7a7fa7ba3f95131229002b8b81e5c7acf616756cc788` |

This is mechanism and safety evidence only. It is not a scientific result and
does not establish accuracy, alert correctness, human benefit, or
generalization.

## Provider-backed run (one authorized run; no retry of the experiment)

Private receipts show one authorized run with two technical attempts. The
first request was rejected by the API parameter validator before model output;
the second reached the model but failed closed in the answer-correlation
instrumentation. No whole-experiment retry, setting substitution, model
switch, or outcome-dependent expansion occurred.

| Attempt | Status | Requests | Tokens | Estimated cost |
|---|---|---:|---:|---:|
| 1 | `INCOMPLETE_TECHNICAL` (legacy `max_tokens` rejected) | 1 | 0 | $0.000000 |
| 2 | `INCOMPLETE_TECHNICAL` (`unknown, duplicate or missing answer`) | 3 | 17,148 | $0.010293 |
| **Total** | `INCOMPLETE_TECHNICAL` | **4** | **17,148** | **$0.010293** |

Frozen configuration: provider `openai`; model `gpt-5.6-luna`; `chat.completions`;
output ceiling 16,384; request timeout 180 seconds; run timeout 3,600 seconds;
concurrency 2; request cap 326; hard budget $10; no fallback or model switch.
The Luna prices used by the harness are $0.20/M input and $1.20/M output,
verified against [OpenAI model documentation](https://platform.openai.com/docs/models/gpt-4-turbo-and-gpt-4)
and the [OpenAI July 30, 2026 pricing announcement](https://openai.com/index/advancing-the-price-performance-frontier-with-gpt-5-6/).

Private artifact hashes:

| Artifact | SHA-256 |
|---|---|
| Attempt 1 receipt | `fa43912aa546ce86f56892c33c7a149e6e64808ab928a5fb423a156d2a711df8` |
| Attempt 2 receipt | `42101727ee97543b9e8a21e8843e409e205545f771c383f6ae5abec083079ccd` |
| Analysis summary | `879ad25e84781747e53da531912a221041ade3f0e7f4af6bcfcb679c0404ae05` |
| Episodes CSV | `f7a6b7abd960086c9abb942fa57d2d52e0a288c6b6c9a3753e04e7c922bf3b70` |
| Detector CSV | `497a2d7b739b5b3da8f986c6c1717ed4554df2999d3c1c051f4e84188b181860` |

## Scientific-state accounting

| Denominator / measure | Value |
|---|---:|
| Questions emitted | 1 |
| Answers recorded | 0 |
| Total observed episodes | 1 |
| Complete episodes | 0 |
| `INCOMPLETE_TECHNICAL` episodes | 1 |
| Detector-v1 denominator | 0 |
| Detector-v1 run count | 0 |
| Renderer run count | 0 |

Because the scientific denominator is zero, STRONG/WEAK/NO_ALERT and context
signals were not computed. The run is not a `VALID_ZERO_QA_RUN`; it is a
technical incompleteness.

## Safety and claim boundary

No raw corpus bytes, prompts, answers, credentials, private paths, or provider
secrets are committed. Protected VEGO-AI runtime files and the frozen Detector
and preregistration files were unchanged. No synthetic cases were created.
The only supported claims are that the offline authorization/containment and
parity controls passed, and that the provider run failed technically under the
recorded configuration. No claim is made about correctness, precision, recall,
F1, human benefit, intervention effectiveness, representativeness, or
generalization.

## Private artifact roots

The validated fake bundle is retained under the ignored local path
`external_data/airtravel-pr38/fresh-fake-run-baca488/`. The provider-run and
analysis artifacts remain in the ignored execution checkout. This receipt
contains hashes and counts only; it does not publish those files.
