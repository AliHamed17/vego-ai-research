# Study 2 ON/OFF — independent implementation review

**Date:** 2026-09-06 · **Reviewer:** Claude (independent of the implementation)
**Scope:** `scripts/study2_on_off_experiment.py`, `scripts/study2_vego_off_baseline.py`,
`docs/research/phd-proposal/airtravel-pr38-correction/study2-frozen-config.json`,
and the two Study 2 documents.

**Verdict: `NOT_READY_FOR_PAID_AUTHORIZATION`.**

The harness is a coherent offline fixture. It is not a paid-run harness, and several of its
emitted attestations are asserted rather than measured. No paid Study 2 run may be authorized
against it in its current state.

This review changes no implementation file. Implementation is Codex's lane; every item below is
a required correction handed over, not a change made.

---

## 1. Operational ON/OFF definitions — PARTIAL

ON and OFF are defined in prose in the preregistration and are distinguishable in code by
construction (`run_on` drives the protected orchestrator; `run_off` issues one call per case).
`VEGO_AI_OFF` correctly contains no agent decomposition, no inter-agent Q&A and no round loop.

**But three properties are constants, not observations.** `run_off_baseline` returns
`agent_decomposition: False`, `inter_agent_qa: False` and `episodes: 0` as hardcoded literals. No
code path inspects a baseline response for question-like content, and `normalise` discards every
key outside the output contract without recording what it discarded. The only barrier against
hidden Q&A in OFF is a sentence in the prompt asking the model not to ask questions — a request,
not a control.

This matters more than any other item in this review, because the entire `NOT_APPLICABLE`
denominator rests on OFF genuinely producing no episodes. That property is currently **asserted,
not proven**.

## 2. Detector-v1 `NOT_APPLICABLE` for OFF — PRESENT, with one wording defect

The distinction is correctly and repeatedly made: `detector_v1_denominator` is the string
`NOT_APPLICABLE`, never `0`, and both the code and the documents state that absence of a
measuring instrument is not absence of a phenomenon. This is the single strongest part of the
design and it should be preserved verbatim.

One defect: the emitted comparison says Detector-v1 was `applied_to` the ON condition. It was not
applied at all — the harness never invokes it, and the payload carries no detector result, no ON
denominator and no alert counts. `applied_to` should read `applicable_to`, with an explicit
`detector_v1_executed: false`.

## 3. No output-quality comparison claimed before independent evaluation — FAILS

Two claims exceed what any instrument in the design can support.

- The module docstring states the conditions are "compared on the shared per-case output
  objective". No instrument compares output quality; none is preregistered.
- `per_case_comparison` emits `on_mapping_rows` against `off_mapping_rows` and
  `on_uncovered_fragments` against `off_uncovered_fragments`. These are **volume counts with no
  ground-truth anchor**, and they are not like-for-like across conditions. Any non-zero difference
  will be read as a quality difference. Each row needs an explicit
  `comparability: NOT_COMPARABLE_AS_QUALITY` field.

## 4. Controls bound in code and configuration — FAILS on six of eleven

Verified by direct comparison against `scripts/airtravel_real_run.py`, which is the project's
demonstrated paid-run harness.

| Control | Study 1 paid harness | Study 2 harness |
|---|---|---|
| Corpus pinning by sha256 | bound | **bound** |
| Concurrency | bound | **bound** (2 in both paths) |
| Output contract | bound | **bound** |
| Budget guard with per-request reservation | bound | **absent** |
| Outbound request cap | bound | **absent** |
| Egress restriction to the provider host | bound | **absent** |
| Frozen model identity | bound | **absent** (fixture identity only) |
| Max output tokens | bound | **absent** |
| Request timeout / run timeout enforcement | bound | **absent** |
| Retry policy | bound | **absent** |
| Frozen case set `01`–`04` enforced | bound (raises on a mismatch) | **absent** (accepts whatever the manifest yields) |

The frozen configuration and the preregistration both name a USD 10 budget cap and a 326-request
cap. Neither exists in Study 2 code. Those are intentions, not bindings, and the documents have
been corrected to say so.

Three preregistered shared outcomes — tokens, cost and technical failures — cannot be produced by
any Study 2 code at all. There is no token accounting, no price constant and no status field.

## 5. The single-factor claim — REJECTED, correction required

The harness asserts that "the single varying factor is VEGO-AI orchestration" and emits
`varying_factor: "VEGO-AI orchestration"`. **Its own emitted note contradicts this in the same
JSON object**, stating that prompt text necessarily differs because the conditions differ
structurally.

Both cannot be true. Prompt text, task decomposition and call structure all differ, and they
differ *because* orchestration differs — they are constitutive of the manipulation, not
incidental to it. No design can hold them constant while varying orchestration.

Study 2 is therefore a **system comparison**, and every occurrence of the single-factor claim
must be replaced with system-comparison wording — in the module docstring, in the emitted
`varying_factor` field, in the frozen configuration, and in both documents. The preregistration
has been corrected (§3 of version 2). The code sites remain for Codex.

A consequence the correction must carry: the stop rule "stop if any difference beyond
orchestration is found" is **unevaluable as written**. Read literally it has already triggered;
read loosely it can never trigger. It must be replaced by a stop rule referencing a
structural-difference schedule fixed in advance.

## 6. Fixtures are engineering-only and unpooled — PRESENT, but the fixture shows nothing

`evidence_class: ENGINEERING_FIXTURE_NOT_SCIENTIFIC` and `provider_calls: 0` are emitted, and the
payload states that Study 1 is not pooled. Correct in intent.

Two defects:

- **Both fields are unconditional literals.** Nothing observes whether a provider was contacted.
  If a real client were substituted, the artifact would still describe itself as a fixture with
  zero provider calls — and the frozen configuration cites exactly these two fields as the
  preflight's evidence. The central attestation of the offline preflight is a hardcoded string.
- **The fixture carries no comparative content.** The baseline fixture client returns empty
  mapping and fragment lists by construction, so every per-case row is `0` versus `0`. The fixture
  demonstrates that the plumbing runs and that the schema shape holds. It demonstrates nothing
  about either condition, and no figure or sentence may present it as a difference.

Separately, the fixture artifact carrying the supervisor-facing counts lives under
`external_data/**`, which is git-ignored, and no tracked file records its path or digest. A
reviewer at the preflight-audit gate has no version-controlled handle on the object being audited.

## 7. Further implementation defects

| Defect | Effect |
|---|---|
| `prompt_sha_by_label` is a dict keyed by label | Repeated labels collapse under last-write-wins, so the prompt receipt undercounts calls. The ON fixture made 46 calls and the receipt records 28 entries. |
| OFF outputs are never persisted | `run_on` writes ON artifacts to disk; `run_off` holds results in memory only. The OFF condition leaves no auditable artifact. |
| `summarise_on` coerces failures to zero | A missing artifact yields `{}` and the case vanishes; a malformed field is coerced to `0`, which is indistinguishable from a genuine empty result. |
| `BaselineFake` inherits from `RecordingFake` without calling it | It silently drops the call ceiling the ON path retains. |
| OFF prompt hashes are re-derived, not captured at the call site | The receipt attests to a prompt that may never have been sent. |
| `load_corpus` does not enforce the frozen case set | The case identifiers named in the preregistration are unenforced in code. |
| No `--execute` gate; `--run-id` defaults to a constant | A bare invocation runs, and every run carries the same identifier, defeating the provenance role `run_id` plays in Study 1. |
| No test file exercises either module | Green CI cannot be cited as implementation evidence at the authorization gate. The claim scanner covers the Study 2 *documents*, not the code. |

## 8. Required before any paid Study 2 authorization

1. Bind the six missing controls (budget guard, request cap, egress restriction, model identity,
   max output tokens, timeouts and retries) and enforce the frozen case set.
2. Replace every single-factor claim with system-comparison wording, and replace the unevaluable
   stop rule with one referencing a fixed structural-difference schedule.
3. Derive `evidence_class` and `provider_calls` from observation instead of literals; refuse to
   write the artifact when the run mode cannot be asserted.
4. Instrument the no-hidden-Q&A property in OFF instead of asserting it.
5. Persist OFF outputs; record every call in the prompt receipt without collapsing duplicates;
   capture prompt hashes at the call site.
6. Distinguish `ARTIFACT_ABSENT`, `MALFORMED` and `COMPLETE` in the per-case summary instead of
   coercing to zero.
7. Add token, cost and failure-status accounting, or mark those three preregistered outcomes
   `NOT_MEASURABLE_BY_THE_CURRENT_HARNESS`.
8. Add a Study 2 test file, and record the preflight artifact's path and digest in a tracked file.
9. Add `comparability: NOT_COMPARABLE_AS_QUALITY` to every per-case comparison row.
10. Pin the Detector-v1 configuration for Study 2 by module path and digest, so the instrument
    cannot be tuned after an outcome is observed.

Until items 1–4 are closed, `study2_on_off_experiment.py` is an offline fixture harness and
nothing more. It should continue to be described that way.

## 9. What this review does not say

It does not say the Study 2 design is unsound. The ON/OFF separation, the `NOT_APPLICABLE`
denominator, the refusal to compare alert rates and the no-pooling rule are all correct and should
be preserved. The defects are in binding and in attestation: the harness promises controls it does
not implement and attests to properties it does not measure.

It also makes no claim about which condition would produce better output. No instrument in this
design can answer that, and none is preregistered.
