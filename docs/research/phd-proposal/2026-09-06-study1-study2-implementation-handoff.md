# VEGO-AI Study 1/Study 2 implementation handoff

**Date:** 2026-09-06
**Evidence class:** implementation, protocol and validation metadata; no new
provider run and no new scientific data.

## A. Reviewed heads and canonical draft

| Item | State at review | SHA |
|---|---|---|
| `origin/main` | fetched base | `c34d3954b5e080d090017d2ea655d454d75a6b92` |
| PR #38 | open, draft, unmerged | `a976494a624391efb0fb96e8f769512f52f52af0` |
| PR #41 | open, draft, unmerged | `63da0105f25207e3cc6e67bb3ec499652d65124c` |
| PR #42 | open, draft, unmerged; divergent Study 2 branch | `de65a57d5ca7289cc6032baa7cc797499fdc6812` |
| local canonical implementation | isolated branch | reported by `git rev-parse HEAD` at handoff time; intentionally not self-embedded |

The evidence parent for this draft is `origin/main` at
`c34d3954b5e080d090017d2ea655d454d75a6b92`; the local head is reported by the
final Git receipt rather than self-embedded in this file. PR #41 descends from PR #38. PR #42 is not an ancestor of PR #41, so only
its Study 2 contract, schemas, fixture runner and tests were ported. No broad
merge was performed and the protected VEGO-AI runtime, Detector-v1, v1.0.1 and
v1.0.2 were not changed.

## B. Study 1 evidence status

`EVIDENCE_NOT_AVAILABLE_IN_REVIEWED_WORKTREE`.

The fail-closed locator requires an explicitly mounted private read-only root,
a binding manifest, the accepted event log, the run receipt and the pipeline
manifest (plus any declared detector files). No such root is mounted in this
worktree. Therefore the generated safe metrics contain no numeric Study 1
values. Existing narrative or inherited reports are not used to populate them.

When a private accepted chain is supplied, the validator will check byte hashes,
accepted-replacement identity, one run ID, lifecycle, event-log hash, code/config
provenance and every declared aggregate before emitting aggregate-only rows.

## C. Study 1 measurement package

The checked-in package is:

- `study1-signal-dictionary-v1.json` — code-grounded raw fields, S1/S2/S3/S6/S7,
  context C1/C2/C3, semantic outputs and reporting-only action labels;
- `study1-signal-traceability-matrix-v1.csv` — explicit asking-agent and
  answering-agent columns;
- `study1-signal-metrics-v1.json` — schema-valid unavailable tables until the
  private chain is verified;
- `2026-09-06-study1-signal-technical-note.he.md` — Hebrew RTL companion.

The frozen detector remains:

```text
STRONG_ALERT = S1 OR S3 OR S7
WEAK_ALERT   = no strong signal AND (S2 OR S6)
NO_ALERT     otherwise
```

Signals can co-occur. `Alternative`, `Non-Satisfied`, C1, C2 and C3 are not
Detector-v1 triggers. A candidate alert is a reporting label only: no automatic
queue, correction, source change, target change or model replacement is
implemented by this package.

## D. Study 2 design and implementation status

Study 2 is a **system comparison**, not a claim that orchestration is the only
varying factor:

- `VEGO_AI_ON`: four-agent decomposition with inter-agent Q&A and bounded rounds;
- `VEGO_AI_OFF`: one direct per-case workflow with no agents, Q&A or round loop.

Both conditions bind the same `cd_airtravel` /
`text2uml_airtravel_253b26dc` case set, model placeholder, temperature, token
policy, retries, timeout, run timeout, concurrency, output contract, privacy
policy, cost/call caps and stopping policy. The strict condition schema fails
closed; OFF uses `Detector-v1 = NOT_APPLICABLE`, never zero. Prompt and task
decomposition differences are recorded rather than hidden.

The dependency-injected runner accepts only `ENGINEERING_FIXTURE_ONLY` cases and
the local deterministic fixture client. It writes hash/count receipts under a
caller-supplied private root. Fixture artifacts are permanently excluded from
scientific reporting; no provider or network adapter is available on that path.

## E. Future evidence and authorization

`study2-future-run-authorization-template.md` is `NOT_AUTHORIZED`. A future
provider run needs a fresh one-time authorization binding the exact code SHA,
configuration, corpus hashes, model identity, run ID, nonce, caps, output root,
and anti-replay receipt. Llama remains a separate model-portability study.

## F. Verification record

| Check | Result |
|---|---|
| Focused Study 1/Study 2 tests | **66 passed** |
| Root tests | **71 passed** |
| VEGO-AI tests | **134 passed** |
| Scripts tests | **654 passed, 22 skipped, 2 warnings, 7 subtests** |
| Scoped Ruff | **PASS** |
| Full-repository Ruff | **159 pre-existing findings** (not introduced by this scope) |
| Privacy scan | **PASS** |
| Evidence consistency | **PASS** (3/3 present checks; 5 expected unavailable skips) |
| Security audit | **PASS** |
| Python compile | **PASS** |
| JSON Schema validation | **PASS** (57 actual schemas; fixture data excluded) |
| Dashboard/outbox health | **PASS** |

No provider/API/model call, paid run, Detector-v1 experiment, synthetic
scientific-data generation, raw-data copy or protected-runtime modification was
performed.

## G. Remaining gates

1. Mount and independently bind the accepted Study 1 private evidence chain if
   descriptive numeric reporting is required.
2. Independently review this implementation and the preregistration.
3. Freeze a future provider/model, budget, egress policy and one-time grant only
   after the offline fixture path is reviewed.
4. Obtain blinded human-rubric judges before making any Study 2 quality claim.

Until these gates close, the correct status is **READY FOR INDEPENDENT HUMAN
REVIEW**, not an accuracy, benefit, effectiveness, superiority or generalization
result.
