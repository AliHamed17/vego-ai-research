# PR #48 — what is still red, and what is needed to clear it

Every CI failure that can be fixed by code has been fixed. What remains is a
**protected-change authorization decision**, which requires a human and is deliberately
not something an agent can grant itself.

## What is already green

| check | state |
|---|---|
| `VEGO-AI/tests` | **159 passing** (was 134) |
| `tests/hlayer_offline` | 46 passing |
| `VEGO-AI/framework/test_orchestrator_fixes.py` | 5/5 |
| all 17 validators in "Validate contracts, manifests, claims, citations, and freshness" | **0 failures** |
| `scripts/tests/test_bigui_catalog.py::test_every_metric_and_source_has_publishable_provenance` | fixed — was hash drift |
| `scripts/tests/test_thesis_evidence_package.py::test_provenance_validation_survives_unreachable_build_commits` | fixed — was hash drift |
| working tree | clean; all derived manifests regenerated to a fixed point |
| mutation evidence | **8/8 fixes guarded** |

## What is still red, and why

`scripts/tests/test_hlayer_hardening.py` shells out to `scripts/build-hlayer-experiments.ps1`,
which runs `scripts/check_hlayer_change_authorization.py` before promotion. That check
currently reports:

```
FAIL: trusted authorization SHA-256 is not configured outside the candidate tree
FAIL: unauthorized protected changes:
        VEGO-AI/framework/orchestrator.py
        VEGO-AI/framework/qa_instrumented_runner.py
        VEGO-AI/framework/qa_registry.py
        VEGO-AI/framework/test_orchestrator_fixes.py
        VEGO-AI/tests/test_qa_id_correlation.py
        VEGO-AI/tests/test_qa_pipeline_integrity.py
FAIL: protected path lacks a valid authorized hash: <each of the above>
FAIL: authorization must require independent approval
```

There are **two separate causes**, and both need a human.

### 1. No trusted authorization hash is configured

`check_hlayer_change_authorization.py` will only trust
`configs/protected-change-authorization-v1.json` if its SHA-256 is supplied from **outside**
the candidate tree, via the `H_LAYER_AUTHORIZATION_SHA256` environment variable or the
`vego.hlayerAuthorizationSha256` local git config. Neither is set, so the checker loads an
empty config and every field appears absent — which is why it also complains that the
expiry "must be an ISO date" when the file plainly contains `2026-08-31`.

This is working as designed: an in-tree file cannot authorise its own tree.

### 2. The authorization itself has expired and does not cover this PR

`configs/protected-change-authorization-v1.json` currently says:

| field | value |
|---|---|
| `authorization_scope` | `PR #10 unified-runtime-security-hardening-v1` |
| `authorization_expires_on` | **2026-08-31** (in the past) |
| `merge_requires_independent_approval` | `true` |
| `forbidden_paths` | includes **`VEGO-AI/framework/orchestrator.py`** |

So this PR changes a file that is explicitly forbidden, under an authorization that expired
and was scoped to a different PR.

## What the PR actually changes, and why each file is necessary

| file | change | why it cannot be avoided |
|---|---|---|
| `VEGO-AI/framework/orchestrator.py` | phase-4 payload compaction; reroute of scope-rejected questions; per-round merge of the compliance vector and guidelines; `gather()` error propagation; unanswered- and malformed-answer reporting; provenance stamping at 9 raise sites | these are the pipeline defects the PR exists to fix |
| `VEGO-AI/framework/qa_registry.py` | `seed_counters_from_history`; `record_answers` joins answers to questions and stamps provenance and `setting_id` | without this, resumed runs re-issue ids and saved Q&A has no verifiable provenance |
| `VEGO-AI/framework/qa_instrumented_runner.py` | `asked_question_ids` | without this the instrumented harness records ids that were never asked |
| `VEGO-AI/framework/test_orchestrator_fixes.py` | 5 no-API tests | guards the phase-4 and rerouting fixes |
| `VEGO-AI/tests/test_qa_id_correlation.py` | 11 tests | guards the id-correlation fix |
| `VEGO-AI/tests/test_qa_pipeline_integrity.py` | 14 end-to-end tests | guards every fix above; mutation-proven 8/8 |

The last three are new **test** files. They land under protected prefixes
(`VEGO-AI/tests/`) purely because of where tests live, not because they alter runtime
behaviour.

## What is being asked for

A decision by whoever owns the protected-change policy:

1. Issue an authorization record scoped to **PR #48**, listing the six paths above with
   their current content hashes, with a future `authorization_expires_on`, retaining
   `merge_requires_independent_approval: true`.
2. Configure the trusted authorization SHA-256 out of tree (repository secret exposed as
   `H_LAYER_AUTHORIZATION_SHA256`, or the local git config key) so the checker will load it.

Until then PR #48 cannot go green, and that is the control behaving correctly rather than
a fault to be worked around. No attempt has been made to bypass, weaken, or self-authorise
the check.

## Evidence for the review

- `docs/research/qa-pipeline-integrity-v1.md` — the eight defects, their fixes, and the
  mutation evidence that each fix is guarded.
- `scripts/qa_integrity_evidence.py` — re-runs that evidence on demand.

## Current content hashes for the six paths

Computed from the bytes git materialises (LF, per `.gitattributes`).

```json
{
  "VEGO-AI/framework/orchestrator.py": "c8cfee8495c6ba31c1ee7c300a1170fbd90c148a1ee8a7718682d877c7243b24",
  "VEGO-AI/framework/qa_registry.py": "49e77df66b33ffa4f83d7f83fa8e9765fd9b6f2bc942efbfe246c66445398e03",
  "VEGO-AI/framework/qa_instrumented_runner.py": "7474582b9625651b71cdc331943732a8c29bf40e04f9ea4b4e29e79c7bb71a98",
  "VEGO-AI/framework/test_orchestrator_fixes.py": "9d2daa0da5128343f92abebc2187ce618e5425e49a612f316cae8c6e70eb9ae4",
  "VEGO-AI/tests/test_qa_id_correlation.py": "9bdce84ede34e8393110a65dca9651f01c59a294eb6a973e77830d2dc797fa51",
  "VEGO-AI/tests/test_qa_pipeline_integrity.py": "5c039bd8f80d37e70a9875f604afcc07cac40a266961be8e7d4fa44b347a6567"
}
```
