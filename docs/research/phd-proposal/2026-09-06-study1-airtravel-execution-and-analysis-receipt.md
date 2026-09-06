# Study 1 — AirTravel execution and analysis receipt

> **Controlling verdict:** `PARTIAL_EVIDENCE_ONLY / DESCRIPTIVE_REPORTING_WITH_RETROSPECTIVE_PROVENANCE`
>
> The private evidence was validated retrospectively; the original receipt did not self-bind the event-log hash, lifecycle summary, or execution-code SHA. These are provenance gaps, not value errors: every number reproduces from the event log. Supervisor acknowledgement does **not** upgrade this run to prospective or preregistered provenance.


Machine-verifiable record for one authorized offline preflight and one
authorized provider-backed run. Every value below is derived from a persisted
artifact; none is narrated.

## Binding

| Item | Value |
|---|---|
| Reviewed head | `efe686ac0b13c6e17695b816da7eb0cdd3eadcc1` |
| PR | #38 (open, draft, unmerged) |
| Preflight reviewed_head | `efe686ac0b13c6e17695b816da7eb0cdd3eadcc1` |
| Grant nonce / invocation | `ROBNRnnTeW0O-T2ufFITz_I36mEXBvg0` / `airtravel-v4-d2cf0854c4c068db` |
| Grant window | `2026-09-05T23:02:14Z` → `2026-09-05T23:32:14Z` |
| Packet SHA-256 | `e2f6a4416e7ce3ca9154e5ea51d1f88b87f724d73b35d775bd263b7a753b32b1` |
| Machine manifest SHA-256 | `3db072dd221e9465e06dfac4be2a26f38277945c8e50de8f408d7aee3191dcfc` |
| Command fingerprint | `a2ef88358f19d2918cddaeba1eead45ee8c2f5a284b7d99557209d6a15e6a7ba` |
| Runtime archive SHA-256 | `e37baecd20a0c84eb1d9b87b3b78a23bc4b4eb8a9824ad3086dc30aa35fdd31f` |
| Source verification | 143/143 source files, 5/5 runtime files |

*[Retrospective provenance — see the controlling caveat at the top of this document.]*
## Offline fake preflight — engineering evidence only

| Item | Value |
|---|---|
| Status | `TECHNICAL_SUCCESS` |
| Direct / instrumented calls | 46 / 46 (equal: True) |
| Prompt / answer / decision parity | True / True / True |
| PipelineState / artifact parity | True / True |
| Events / questions / answers | 50 / 20 / 20 |
| Terminations | {"CONVERGED": 10} |
| Route pairs | 6 |
| Containment / privacy | PASS / PASS |
| Safety counters all zero | True |
| Protected manifest before = after | True |
| Tracked manifest before = after | True |

*[Retrospective provenance — see the controlling caveat at the top of this document.]*
This is technical readiness. It is not a scientific result.

## Real provider-backed run — exactly one

| Item | Value |
|---|---|
| Run ID | `REAL-efe686a-20260905T2303Z` |
| Status | `TECHNICAL_SUCCESS` |
| Provider / model | openai / `gpt-5.6-luna` |
| API mode | `chat.completions` |
| max_tokens | 16384 |
| Request / run timeout | 180s / 3600s |
| Concurrency | 2 |
| Started / completed | 2026-09-05T23:03:01Z → 2026-09-05T23:12:38Z |
| Outbound requests | **43** of 326 |
| Prompt / completion tokens | 186,558 / 81,384 |
| Total tokens | 267,942 |
| Actual cost | **USD 0.134972** of 10.0 |
| Within budget | True |
| Blocked egress attempts | 0 |
| Credential | process environment variable, value never read |

*[Retrospective provenance — see the controlling caveat at the top of this document.]*
Call bounds: minimum 4 + 3N = 16, maximum 82 + 61N = 326. Observed
43 outbound requests, inside both bounds.

## Detector-v1 — frozen, byte-identical to main

| Item | Value |
|---|---|
| Total episodes observed | 3 |
| Complete episodes (denominator) | **3** |
| INCOMPLETE_TECHNICAL (excluded) | 0 |
| Questions / answers | 44 / 44 |
| Max round index | 10 |
| Directed route pairs | 3 |
| Termination states | {"CONVERGED": 2, "TERMINATED_MAX_ROUNDS": 1} |
| STRONG_ALERT | **3** |
| WEAK_ALERT | 0 |
| NO_ALERT | 0 |
| Signals fired | {"S1_LOW_ANSWER_CONFIDENCE": 3, "S2_MEDIUM_ANSWER_CONFIDENCE": 2, "S6_MULTIPLE_QA_ROUNDS": 2, "S7_TERMINATED_MAX_ROUNDS": 1} |

*[Retrospective provenance — see the controlling caveat at the top of this document.]*
Classification rule applied unchanged: `STRONG_ALERT = S1 ∨ S3 ∨ S7`;
`WEAK_ALERT = ¬STRONG ∧ (S2 ∨ S6)`; otherwise `NO_ALERT`.
C1/C2/C3 are context only, C1 strictly `mapping_certainty < 0.7`.
S5/S8/S9 remain non-triggering or descriptive as preregistered.

## Private evidence hashes

| Artifact | SHA-256 |
|---|---|
| Real-run event log | `55ea9361304482033a5b6fed83697a748dbd89b8d951e80c211eba69d117cac4` |
| Real-run receipt | `7bb234a6dee79860ce007027d2f8ebcdd24489dc9c5436a3a683fe477eeb2438` |
| Detector summary | `c6a5f058b9b994448002f5b06d503140ea6c6a15106e624a68ceaa051ec46fd8` |
| Episode CSV | `219f73f22b9b6ad91dc46e67474e9637a45ade78709337a6f9cdfd818814e8da` |
| Detector CSV | `616b9f93a6114ae07661c53f872e4d7edea09db97fd5812a37fe52dfa2a1d23c` |
| Preflight receipt | `20d90f28adc44ba2467b0d895bf0b2173a22c6d3278cc5e2f175946f1e45afaa` |
| Preflight output inventory | `3151f72da1e097dae651b93f4f857d28561984f2e7f1b32e9d6317f20ba6e112` |

*[Retrospective provenance — see the controlling caveat at the top of this document.]*
## Privacy and claim boundary

Raw prompts, raw answers, pipeline artifacts and corpus bytes are stored only
outside version control. Committed material carries hashes, aggregate counts
and receipts. The API credential was read only by the provider SDK from a local
environment variable; its value was never read, printed, logged, hashed or
persisted. Network egress was restricted to the provider API host.

No accuracy, precision, recall, F1, alert-correctness, human-benefit,
intervention-effectiveness, representativeness or generalization claim is made
or computed. The corpus is public-external and LLM-generated: not student data,
not Cheers/ParkWise, not synthetic.

## Verdict

`AIRTRAVEL_PRELIMINARY_RESULTS_ACCEPTED` — a descriptive observation on this
exact four-case corpus under the recorded model and configuration.
