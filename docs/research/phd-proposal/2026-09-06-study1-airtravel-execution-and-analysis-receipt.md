# Study 1 — AirTravel execution and analysis receipt

> **Controlling verdict:** `PARTIAL_EVIDENCE_ONLY / DESCRIPTIVE_REPORTING_WITH_RETROSPECTIVE_PROVENANCE`
>
> The private evidence was validated retrospectively; the original receipt did not self-bind the event-log hash, lifecycle summary, or execution-code SHA. A fourth, separate item concerns a derived artifact whose pinned digest no longer resolves. All four are recorded in *Provenance gaps* below. These are provenance gaps, not value errors: every number reproduces from the event log. Supervisor acknowledgement does **not** upgrade this run to prospective or preregistered provenance.


Machine-verifiable record for one authorized offline preflight and one
authorized provider-backed run. Every value below is derived from a persisted
artifact; none is narrated.

## Authorization-time binding — values not self-bound by the run receipt

The real-run receipt carries exactly these keys: `N`, `answer_count`,
`api_mode`, `blocked_egress_attempts`, `completed_at`, `corpus_id`,
`credential_source`, `episode_count`, `max_concurrent_cases`, `max_tokens`,
`model_requested`, `protected_orchestrator_fake_*`, `provider`,
`question_count`, `request_timeout_seconds`, `routes`, `run_id`,
`run_timeout_seconds`, `schema_version`, `setting_id`, `started_at`, `status`,
`technical_exception`, `usage`. It carries **no `reviewed_head` field**. The
values in the table below were recorded at authorization time, in the protected
authorization packet and its offline preflight; the run receipt does not
self-bind them.

| Item | Value | Source |
|---|---|---|
| Reviewed head | `efe686ac0b13c6e17695b816da7eb0cdd3eadcc1` | Authorization packet — **not** the run receipt |
| PR (current) | #41 | Repository state |
| PR (superseded) | #38 — retained for history only, not the current review target | Repository state |
| Preflight reviewed_head | `efe686ac0b13c6e17695b816da7eb0cdd3eadcc1` | Offline preflight receipt |
| Grant nonce / invocation | `ROBNRnnTeW0O-T2ufFITz_I36mEXBvg0` / `airtravel-v4-d2cf0854c4c068db` | Authorization packet |
| Grant window | `2026-09-05T23:02:14Z` → `2026-09-05T23:32:14Z` | Authorization packet |
| Packet SHA-256 | `e2f6a4416e7ce3ca9154e5ea51d1f88b87f724d73b35d775bd263b7a753b32b1` | Authorization packet |
| Machine manifest SHA-256 | `3db072dd221e9465e06dfac4be2a26f38277945c8e50de8f408d7aee3191dcfc` | Authorization packet |
| Command fingerprint | `a2ef88358f19d2918cddaeba1eead45ee8c2f5a284b7d99557209d6a15e6a7ba` | Authorization packet |
| Runtime archive SHA-256 | `e37baecd20a0c84eb1d9b87b3b78a23bc4b4eb8a9824ad3086dc30aa35fdd31f` | Authorization packet |
| Source verification | 143/143 source files, 5/5 runtime files | Authorization packet |

The evidence-bound execution code SHA is
`efe686ac0b13c6e17695b816da7eb0cdd3eadcc1`. Any `reporting_code_sha` appearing
in generated documents is a document-generation stamp and is **not** part of
the evidence chain.

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

This is technical readiness. It is not a scientific result. The fixture is not
a control group and is not a provider comparison. Any fixture-versus-real
juxtaposition is an engineering / instrumentation check only — never a
scientific result and never `VEGO_AI_ON` versus `VEGO_AI_OFF`. The fixture
denominator (20 answers) is separate from the real-run denominator
(44 answers); the two must never be merged.

## Real provider-backed run — exactly one

| Item | Value |
|---|---|
| Run ID | `REAL-efe686a-20260905T2303Z` |
| Status | `TECHNICAL_SUCCESS` |
| Setting / corpus / N | `cd_airtravel` / `text2uml_airtravel_253b26dc` / 4 |
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

### What an alert means, in plain language

`STRONG_ALERT` means exactly one thing: **the episode is a candidate for human
review** (מועמדת לבדיקה אנושית). It is not a finding that an error occurred,
not a finding that the model was wrong, not a finding that the output was
defective, and not a finding that intervention was required or performed.

Three layers must never be conflated:

| Layer | What it is | Feeds Detector-v1 |
|---|---|---|
| (a) Mapping result | Satisfied / Partially-Satisfied / Not-Satisfied — the pipeline's judgement about the candidate model | **No** |
| (b) Conversation-state signal | Answer confidence, evidence-field presence, round count | **Yes — the only input** |
| (c) Reporting label | Candidacy for human review | This is the **output** |

"Alternative" and "Not-Satisfied" belong to layer (a). Neither is an error and
neither can trigger an alert.

| Item | Value |
|---|---|
| Total episodes observed | 3 |
| Complete episodes (denominator) | **3** |
| INCOMPLETE_TECHNICAL (excluded) | 0 |
| Questions / answers | 44 / 44 |
| Max round index | 10 |
| Answer confidence (of 44 answers) | Low 16 / Medium 25 / High 3 |
| Directed route pairs | 3 of 6 |
| Route breakdown | asking agent4 / answering agent2 = 39; asking agent3 / answering agent2 = 4; asking agent3 / answering agent1 = 1 |
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

S3 (empty evidence field) never fired. Evidence-length distribution over the
44 answers: minimum 38, median 62, maximum 540 characters; zero-length
answers 0. Source artifact: the real-run event log.

### Context-only variables — none feeds the alert rule

Denominator for C2, C3 and the system flag: **n = 19 variability patterns**.
This is not the 3 episodes and not the 4 cases. C1 has its own denominator of
one reference guideline.

| Variable | Value | Denominator | Feeds the alert rule |
|---|---|---|---|
| C1 `mapping_certainty` | 0.85 on the single reference guideline → **0** instances below the 0.7 threshold | 1 reference guideline | **No** |
| C2 agent-4 classification confidence | High 15 / Medium 4 | 19 variability patterns | **No** |
| C3 `flag_for_guidelines_update` | true 14 / false 5 | 19 variability patterns | **No** |
| System `requires_human_review` flag | false on all 19 | 19 variability patterns | **No** |

What this table does **not** prove: it does not show that any answer was
correct or incorrect, and it does not show that any alert was justified or
unjustified. Detector-v1 reads only S1/S3/S7 and S2/S6; C1, C2 and C3 can never
trigger an alert. Source artifact: the real-run event log.

**Correction.** A previous version of these documents reported C2 and C3 as
`NOT_AVAILABLE`. That statement was wrong and is withdrawn; the values are the
ones tabulated above.

## Mapping result and deviation patterns — a separate layer that feeds nothing

Everything in this section belongs to layer (a). It is not a Detector-v1 input
and it is not an alert trigger.

| Item | Value | Denominator | Source artifact |
|---|---|---|---|
| Mapping result — Satisfied | 4 | 4 cases | Real-run pipeline artifacts |
| Mapping result — Partially-Satisfied | 0 | 4 cases | Real-run pipeline artifacts |
| Mapping result — Not-Satisfied | 0 | 4 cases | Real-run pipeline artifacts |
| `recurring_guideline_patterns` | 0 | 19 variability patterns | Real-run pipeline artifacts |
| `recurring_fragment_patterns` | 19 | 19 variability patterns | Real-run pipeline artifacts |
| Dominant fragment label — Alternative | 14 | 19 recurring fragment patterns | Real-run pipeline artifacts |
| Dominant fragment label — Domain Mistake | 5 | 19 recurring fragment patterns | Real-run pipeline artifacts |
| `probe_confirmed` | false on all 19 | 19 recurring fragment patterns | Real-run pipeline artifacts |
| Uncovered fragments per case | 01 = 23, 02 = 22, 03 = 21, 04 = 20 (total 86) | 4 cases | Real-run pipeline artifacts |

"Alternative" denotes a valid alternative formulation. It is **not** an error.

The two deviation-pattern counts must always be published under their own key
names. A bare row labelled only "deviation patterns" with the value 0 was a
key-name defect in an earlier version and is corrected here:
`recurring_guideline_patterns` is 0 and `recurring_fragment_patterns` is 19.

What this section does **not** prove: it carries no accuracy, correctness or
quality measure of any kind, and it says nothing about whether Detector-v1
alerted on the corresponding episodes.

*[Retrospective provenance — see the controlling caveat at the top of this document.]*

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

## Provenance gaps — three in the receipt, one in the derived-artifact chain

| # | Gap | Layer affected |
|---|---|---|
| 1 | The run receipt does not self-bind the hash of its own event log | Receipt provenance |
| 2 | The run receipt contains no lifecycle summary; termination states were computed from the event log | Receipt provenance |
| 3 | The run receipt does not record the execution code SHA | Receipt provenance |
| 4 | `analysis/output-inventory.json` was overwritten and cannot be restored | Derived-artifact chain |

Item 4 in full. On 2026-09-06 the file `analysis/output-inventory.json` was
overwritten by a validator invocation that was pointed at that same file as its
`--manifest` argument. The pin recorded in `analysis/analysis-receipt.json`,
`output_inventory_sha256=abbdd70e…`, therefore no longer resolves; the digest of
the file now on disk is `d02603ad…`. Recovery was attempted across 144
candidate serializations and none reproduced the pinned digest, so the file was
**not** reconstructed and no substitute was fabricated in its place.

Scope of the damage: no published claim cites `analysis/output-inventory.json`.
The primary evidence is unaffected, and both published hashes — the real-run
event log and the real-run receipt — re-verify byte for byte. This is a broken
chain on a derived artifact, not a change to any reported value.

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
