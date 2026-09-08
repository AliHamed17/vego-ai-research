# Study 2 Preregistration: Prospective Paired VEGO_AI_ON versus VEGO_AI_OFF

**Status:** FROZEN before any provider output. **Version:** 3.0 (execution
freeze). **Date:** 2026-09-08. **Study identifier:** VEGO-AI-STUDY-2-PROSPECTIVE.
**Supersedes for this execution:** the Study 2 preregistration draft of
2026-09-06 (version 2), whose blinded rubric, blinding procedure and claim
boundary are carried forward unchanged where this document does not restate them.

The machine-readable twin of this document is
`experiment-manifest.json` in the same directory. Where a value here and a value
in the manifest could ever disagree, the manifest is authoritative and the
runner refuses to start.

## 1. Evidence class and claim boundary

This is a **prospective exploratory paired experiment**. Its results are
classified **PROSPECTIVE EMPIRICAL EVIDENCE** on one public, LLM-generated
corpus with one provider model on one day. It is **not** a claim of system
superiority, human benefit, alert correctness, accuracy, recall, precision,
F1, causality, representativeness or generalisation. Human-assessment outcomes
are **NOT_MEASURED** until two independent raters have scored the blinded
cards.

## 2. Research questions

**Primary (both conditions).** Holding the provider model, the input cases, the
domain material, the output schema, the output-token ceiling, the request
parameters, the timeout and the budget policy constant, how do the VEGO-AI
multi-agent workflow (VEGO_AI_ON) and a matched direct single-model workflow
(VEGO_AI_OFF) compare on

1. output completeness (an artifact produced per case),
2. structural validity (the artifact satisfies the shared output contract),
3. execution cost (provider requests, tokens, priced USD),
4. elapsed time,
5. technical failure rate, and
6. availability of explainable communication evidence (recorded inter-agent
   question-and-answer episodes)?

**Secondary (VEGO_AI_ON only).** Applied to the recorded episodes, does the
frozen Detector-v1 rule identify question-and-answer episodes that a human
reviewer would consider worth prioritised inspection? The rule is
reporting-only. Until two raters score, the answer is NOT_MEASURED.

No directional hypothesis is preregistered. The analysis is descriptive and
paired per case.

## 3. Conditions

| Attribute | VEGO_AI_ON | VEGO_AI_OFF |
|---|---|---|
| Workflow | Unmodified four-agent pipeline: Language Advisor, Domain Advisor, Model Inspector, Variability Explorer | One direct per-case request |
| Agent decomposition | Yes | No |
| Inter-agent Q&A | Yes, bounded and logged | No |
| Round loop | `MAX_QA_ROUNDS` as shipped | None |
| Detector-v1 | APPLICABLE, reporting-only label | NOT_APPLICABLE (no episodes exist; never "zero alerts") |
| Provider, model, API | openai, gpt-5.6-luna, chat.completions | identical |
| Request parameters | model, messages [system, user], max_completion_tokens 16384; temperature, seed, response_format and tools not sent | identical |
| Output contract | study2-condition-output-v1 | identical |
| Request timeout | 180 s | identical |
| Retry policy | one transport retry per request; protected client parse re-attempts | identical (same client class) |
| Budget policy | shared guard, shared ceiling | identical |

OFF is not "no AI". It is the same model doing the same per-case task in one
request, without the multi-agent decomposition, the question-and-answer
protocol or the round loop. Detector-v1 denominators are never merged with OFF
metrics.

**Temperature.** The protected client does not send a temperature parameter.
Both conditions therefore run at the provider default, which is identical by
construction. Freezing an explicit temperature that ON has never used would
have changed the system under test.

## 4. Data, provenance and case selection

- **Corpus.** Text2UML AirTravel, corpus identifier `text2uml_airtravel_253b26dc`,
  pinned commit `253b26dc704d523209a5cba79686f8f7fab57d63`. Public, external,
  LLM-generated. Not student data, not Cheers or ParkWise, not representative
  of any population of modellers.
- **Eligible frame.** The complete population of 21 candidate models pinned by
  the private full-frame contract (`airtravel-full-frame-contract-v1`), plus one
  domain description. Every digest is re-verified before any request.
- **Selection rule (executable).**
  `sorted(random.Random(20260908).sample(sorted(eligible_case_ids), 12))`.
  Executed once before any output was observed. No substitution afterwards.
- **Selected (12):** 01, 02, 03, 05, 06, 07, 08, 12, 15, 18, 20, 21.
- **Excluded (9):** 04, 09, 10, 11, 13, 14, 16, 17, 19 (not drawn).
- **Overlap with Study 1 by digest:** three selected files are byte-identical to
  Study 1 inputs (full-frame 03, 06, 07 correspond to Study 1 cases 01, 03, 04).
  Recorded for transparency; no Study 1 output is reused.
- The full inventory, digests, seed, selected and excluded identifiers are in
  `case-selection-manifest.json`. Corpus bytes never enter Git.

## 5. Budget design and the chosen protocol

Pricing frozen at USD 0.20 per million input tokens and USD 1.20 per million
output tokens. Per-request reservation = (12,000 × 0.20 + 16,384 × 1.20) / 10^6
= USD 0.0220608. Hard ceiling USD 6.00; guard ceiling USD 5.90 (a USD 0.10
margin absorbs any input-token overshoot on the final admitted request). Total
request cap = floor(5.90 / 0.0220608) = 267.

| Option | Distinct cases | Repeats | Paired units | Requests reserved | Reservation USD | Fits |
|---|---|---|---|---|---|---|
| A highest coverage | 12 | 1 | 12 | 264 | 5.8241 | yes |
| B repeatability | 6 | 2 | 12 | 264 | 5.8241 | yes |
| C minimum viable | 4 | 1 | 4 | 88 | 1.9414 | yes |

**Chosen: A.** The primary question is a paired per-case comparison, so distinct
paired units are worth more than repeats of a default-temperature stochastic
system. Operational request caps: ON 19 per case (228 total), OFF 3 per case
(36 total). The theoretical ON bound (82 + 61 N logical calls at ten rounds,
each up to three parse attempts) exceeds the ceiling at any N ≥ 4 under
full-output reservation; the enforced ceiling is therefore the per-request
guard, and the operational caps decide admission. Exceeding a cap stops that
condition with `STOPPED_AT_CAP`; the remaining cases stay in the evidence.
Study 1 (43 requests for 4 cases, USD 0.135) is a calibration reference only,
never an upper bound.

## 6. Frozen execution parameters

| Item | Value |
|---|---|
| Provider / model | openai / gpt-5.6-luna, no fallback, no switching |
| Allowed network destination | api.openai.com only |
| Credential | `OPENAI_API_KEY` read only by the provider SDK; never printed, logged, hashed, committed or transmitted by the harness |
| Execution order | VEGO_AI_OFF then VEGO_AI_ON |
| Concurrency | 2 cases (both conditions) |
| Run timeouts | OFF 1,800 s; ON 5,400 s |
| Output root | `${VEGO_PRIVATE_EVIDENCE_ROOT}/study2-prospective/<run_id>` (absolute, inside the private root, no symlink or reparse point) |
| Detector-v1 | `scripts/extract_qa_escalation_features.py`, digest frozen in the manifest, thresholds unmodified |
| Protected runtime | digests of orchestrator, registry, state, client, agents frozen in the manifest |

## 7. Metrics and denominators

Metrics M1 to M10 with their sections, denominators, conditions and evidence
classes are frozen in the manifest (`metrics`). In brief: Section A shared
operational metrics (M1 completeness, M2 structural validity, M3 cost, M4 time,
M5 technical failure, M6 availability of communication evidence); Section B ON
communication metrics (M7); Section C Detector-v1 boundaries (M8); Section D
business-relevance descriptors (M9); Section E blinded human assessment (M10,
NOT_MEASURED until two raters).

ON cost is reported twice: setting-level (phases shared across cases) and
case-attributed (Model Inspector requests plus the advisor answers they
triggered). ON per-case elapsed time is the first-to-last attributed request
span under concurrency and is labelled approximate.

## 8. Technical-failure policy and stopping rule

| Situation | Handling |
|---|---|
| No artifact for a case and condition | `NOT_PRODUCED`; remains in the denominators of M1 and M5 |
| Artifact fails the shared contract | `SCHEMA_INVALID`; counted in M2; never repaired |
| Provider, parse, model-mismatch or secret-detection failure | `TECHNICAL_FAILURE` with request count and cost disclosed |
| Cap or ceiling reached | `STOPPED_AT_CAP`; remaining cases reported as not produced |
| Zero episodes under ON | Valid observation; Detector-v1 contribution `NO_EPISODE` |
| Transport failure before valid output | One retry per request, counted against caps and ceiling |
| Valid but undesirable result | Never retried |

Stopping rule: run every planned unit once; stop only on cap, ceiling, run
timeout, model mismatch, credential absence or gate failure. Never stop early
because results are favourable or unfavourable.

## 9. Human assessment (Section E)

Blinded redacted cards are generated into the private root only; their count
and digests are published. Two independent raters score every card using the
Hebrew rubric (`human-rater-rubric.he.md`). Decisions:
REVIEW_WORTHY, NOT_REVIEW_WORTHY, INSUFFICIENT_INFORMATION. Suggested actions:
verify, clarify, revise guideline, no action. Until two real raters have scored,
agreement, correctness, precision, recall, F1, workload and benefit are
NOT_MEASURED. No AI judgement is ever labelled as a human judgement.

## 10. Analysis plan

Descriptive, paired per case. For each shared metric, report both conditions
per case and the paired difference, with the count of cases favouring each
direction. No inferential test is preregistered; with twelve paired cases from
one corpus, none would be interpretable as more than description. Every chart
carries title, source, condition, denominator, evidence class, metric
definition and a one-line limitation.

## 11. Gates before the single authorised execution

Manifest loaded and self-bound; Git HEAD equals the CI-green head and the tree
is clean; private runtime root present; eligible inventory re-verified;
selection reproduced from the seed; frozen selection document matches; corpus
digests verified at load; output root safe and fresh; whole-study reservation
within the guard ceiling; at least four paired cases; credential present (value
unread); OFF isolation verified; frozen model and host. Any failed gate refuses
execution. Any code or configuration change after CI is green voids the
authorisation until the gates are repeated on the new head.

## 12. Deviations

None at freeze. Any deviation during execution is recorded in the run receipt
and in this section before analysis.
