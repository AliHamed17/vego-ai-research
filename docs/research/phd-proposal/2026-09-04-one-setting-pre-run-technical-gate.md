# VEGO-AI Study 1 — one-setting pre-run technical gate

**Status: BLOCKED — do not start a provider-backed run**
**Audit date:** 2026-09-04 (Asia/Jerusalem)

## A. Repository and preregistration

- Current `main` was synchronized before this audit. The Claude preregistration present on the branch is `v1.0.1`, a pre-data correction (`2026-09-04-qa-escalation-signal-preregistration.md`).
- Detector-v1 policy is consumed as preregistered, but no data run is authorized. C1 for a future new corpus is strict `mapping_certainty < 0.7`; the legacy diagnostic `<= 0.75` rule is retained only as a clearly labelled historical scaffold.

## B. Input and evidence gate

The configured model directories are absent. One unbound ParkWise use-case candidate was found by a metadata-only, read-only inventory; no complete setting is recoverable and no candidate is promoted. See the companion [input-readiness receipt](2026-09-04-one-setting-input-readiness.md). A private manifest is required before any provider call.

## C. Offline instrumentation design (production wiring pending)

`VEGO-AI/framework/qa_instrumented_runner.py` provides an additive client-boundary proxy. It imports the protected orchestrator unchanged, supplies a deterministic local fake client, records prompt/answer hashes and lengths, and observes Q&A metadata through `qa_communication.py`. A task-local context variable is used for route fixtures; no global “current episode” is used. The proxy is pass-through and cannot change prompts, answers, policy decisions, or scientific state.

This is an execution harness and readiness proof, not a claim that the protected production runtime is wired to persist events. The protected `orchestrator.py`, `qa_registry.py`, and `state.py` remain hash-locked and unmodified.

## D. Offline protected-path proof

The deterministic fixture executes the actual protected `orchestrator.run` path and naturally emits one Agent 2 → Agent 1 route. Five additional declared combinations (and a repeated Agent 2 → Agent 1 control) are synthetic protected-helper route fixtures. No production route has been observed. The instrumented and non-instrumented runs have identical prompt/label traces and identical serialized scientific state. A concurrent task test confirms route context separation. These are offline structural tests; they are not provider results and do not create human labels.

## E. Termination states and claims

The communication schema now makes termination explicit: `CONVERGED`, `TERMINATED_MAX_ROUNDS`, or `INCOMPLETE_TECHNICAL`. Technical-incomplete episodes are excluded from any future scientific denominator. No accuracy, human-benefit, reviewer-selection, or policy-superiority claim is made.

## F. Release verdict

**INCOMPLETE_TECHNICAL / BLOCKED_INPUTS.** The code path, schema, strict C1 boundary, and offline parity harness are ready for human review. The actual one-setting run is blocked by missing/binding-unverified inputs and protected-change authorization. No API call, model invocation, spend, or external side effect was performed.

GitHub Actions run `33865519369` is red: the source job reports stale
`docs/research/hardening/release-manifest-v3.json`, while every Python matrix
job reports the protected-change authorization failure for the new
instrumentation paths. Reproduction at trusted ancestor `462c4e4` also failed,
but stopped earlier because its detached checkout had no distinct Git merge
base (`merge base resolves to HEAD`); therefore the current authorization
failure is unresolved, not labelled pre-existing.
