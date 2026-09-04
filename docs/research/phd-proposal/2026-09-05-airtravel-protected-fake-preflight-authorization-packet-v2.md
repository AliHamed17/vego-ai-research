# Protected authorization packet v2 — AirTravel fake-provider preflight

**Status: AUTHORIZATION REQUESTED — NOT GRANTED.**
This packet contains no self-approval language; only the owner (Ali Hamed) may grant it, in chat, after
review. It supersedes `2026-09-05-airtravel-protected-fake-preflight-authorization-packet.md`, which was
bound to superseded `main` `11cbe0413884624469867afa7aba66a0050a6442` and to a fixture/parity command
rather than the exact `cd_airtravel` configuration; the v1 packet is retained unmodified as history.

## 1–2. Commit bindings

| Field | Value |
|---|---|
| `packet_base_sha` (green `main` parent of the preparation branch; a fixed prior reference, never this commit's own hash) | `c34d3954b5e080d090017d2ea655d454d75a6b92` |
| Preparation-branch commits bound at packet-writing time | `1ba1a43` (call-bound proof), `63999d78e8653409c8e8a8e3fe856189ccfa6fda` (harness/renderer/template) |
| Final branch head | recorded in the PR body at push time; a commit cannot contain its own hash |
| Expiry | this packet expires automatically if `origin/main` moves past the merged preparation PR without re-verification, or if any protected-file or runtime hash below drifts |

## 3–4. Frozen runtime bytes

Runtime archive (deterministic ZIP): SHA-256
`e37baecd20a0c84eb1d9b87b3b78a23bc4b4eb8a9824ad3086dc30aa35fdd31f`
(derived byte-identically from upstream archive
`8cf82e2ab2d2ce3da9a7ec4165e760ae1e0d9af14468f5aa2a3883037d8da701`, Text2UML commit `253b26dc`).

| Runtime file (relative to runtime root) | Bytes | SHA-256 |
|---|---:|---|
| `domain_description/description.md` | 1,477 | `96bc8a6fbf2c2fdd93592fdbf6fac7c2b9db403494fe2d5a45e0a2bcbf0167e2` |
| `candidate_models/01_result_one_claude-sonnet-4-6.txt` | 1,248 | `240b034834e383b9844e9a3e9796f6be9b3d47fc95de6606ed022d278d751f91` |
| `candidate_models/02_result_one_codestral-2508.txt` | 1,272 | `08399ca9432c1399f3f9784d34741314e4d39e40307a6efb14fa92a1c138b1d6` |
| `candidate_models/03_result_one_deepseek-chat.txt` | 1,324 | `ee4d689d59c9ce3a5e8ff385747641954bd4821f2efeb18e581dcd1d5441d20a` |
| `candidate_models/04_result_one_gemini-2.5-flash.txt` | 1,231 | `1c3d15eac71fcaab138857dbbc7153833b3df55ab57925ac756a79dc28dc847a` |

Setting: `setting_id=cd_airtravel`, `corpus_id=text2uml_airtravel_253b26dc`, `N=4`.

## 5. Protected files (all read-only; before/after hashes identical by design)

| Path | SHA-256 |
|---|---|
| `VEGO-AI/framework/orchestrator.py` | `fca4b885ee07381db0f02e558b1aebf25bdc7c27da1c471fd3103d7e0e2d5b88` |
| `VEGO-AI/framework/qa_registry.py` | `ab189d3fd954ea03ba891f5746b36eff8889baeff73d7594f820e68f8762ad5f` |
| `VEGO-AI/framework/state.py` | `d8492a623804065b86905d6183979c322d6f83376bf91026e718c615eea1730d` |
| `VEGO-AI/framework/llm_client.py` | `1a36b4ee860619db97a6ff84ecf64b4845a292ef67cf432c17a86eacd56f55da` |
| `VEGO-AI/framework/qa_communication.py` | `9f2cda1dc52fe919be22ac2ea42d61dce3ed22d3fae7ae27077b3db821594236` |
| `VEGO-AI/framework/qa_instrumented_runner.py` | `d187f8e8113a86caf24e55720e227f9a5f9b3466126969166bcefb83625a215f` |
| `VEGO-AI/framework/agent1_language_advisor.py` | `13e152fe4ec3b417a8c515bbe1bdb28ff952766579ce1ed6463a7ad9fa5b724e` |
| `VEGO-AI/framework/agent2_domain_advisor.py` | `fdf330b99295e871ad3cc3e5e934bb04a15f996a5060ea35d43fa13243d16d79` |
| `VEGO-AI/framework/agent3_model_inspector.py` | `4d0042777040f76abc1ca616a6e1dddcda591ddec54478fa2491b5020a817fa4` |
| `VEGO-AI/framework/agent4_variability_explorer.py` | `6b043c5643f9211d93ac402a9bf98685727e2cd92cab3377d1462dc3417df2ff` |
| `schemas/qa-communication-event-v1.schema.json` | `7df773a6a141a656b32012abd35c34aab25002f2a873c84e61c9ade06af670b2` |

The harness verifies every hash above and fails closed on any drift.

## 6. Harness binding

`scripts/prepare_airtravel_protected_fake_preflight.py`, SHA-256
`3f235902edc429aaa6c2f6c12e088b189c856ee51fce532f93e811b25f6f4a3d` (at commit `63999d7`).

## 7–10. Exact future command, read paths, write directory, expected outputs

Run from the repository root. Preparation gate (may be run at any time; read-only):

```
python scripts/prepare_airtravel_protected_fake_preflight.py --prepare-only --output-dir external_data/airtravel-v3.2.1/preflight_evidence_001
```

Exact execution command (only after this packet is explicitly granted):

```
python scripts/prepare_airtravel_protected_fake_preflight.py --execute --i-have-explicit-authorization --authorization-packet docs/research/phd-proposal/2026-09-05-airtravel-protected-fake-preflight-authorization-packet-v2.md --runtime-root external_data/airtravel-v3.2.1/runtime_input --runtime-archive external_data/airtravel-v3.2.1/cd_airtravel-runtime-v1.0.2.zip --output-dir external_data/airtravel-v3.2.1/preflight_evidence_001 --receipt external_data/airtravel-v3.2.1/preflight_evidence_001/prepare-receipt.json
```

Both commands use repository-relative paths only; no environment variables, placeholders, or
machine-specific absolute paths are required. Path resolution and byte verification are performed by the
harness itself, which refuses to run unless the runtime archive hashes to `e37baecd…` and every runtime and
protected file matches its frozen hash — this is the deterministic resolver; no private path is committed.

- **Allowed read paths:** `external_data/airtravel-v3.2.1/runtime_input/`,
  `external_data/airtravel-v3.2.1/cd_airtravel-runtime-v1.0.2.zip`, the protected files in §5,
  `VEGO-AI/framework/` (imports), `schemas/qa-communication-event-v1.schema.json`, this packet.
- **Allowed write directory:** `external_data/airtravel-v3.2.1/preflight_evidence_001/` only (must not
  pre-exist non-empty; `external_data/` is gitignored).
- **Expected output filenames:** `run_config.preflight.json`, `qa_events.jsonl`,
  `preflight-receipt.json`, `pipeline/` (protected orchestrator outputs), `prepare-receipt.json`.

## 11–13. Network, fake provider, and call bounds

- **Network-disabled enforcement:** the harness replaces `socket.socket` and `socket.create_connection`
  with hard-failing guards for the duration of the run, and scrubs `OPENAI_API_KEY` from the environment;
  any socket creation or provider-credential access is a hard failure.
- **Fake provider identity:** `VEGO-AI/framework/qa_instrumented_runner.DeterministicFixtureClient`,
  injected through `InstrumentedLLMClientProxy` at the existing `orchestrator.LLMClient` boundary — the
  already-reviewed mechanism; no protected file changes.
- **Expected call bounds (N=4, `MAX_QA_ROUNDS=10`):** minimum `4 + 3N = 16`; worst case `82 + 61N = 326`;
  derivation in `scripts/study1_call_bound.py::CALL_SITES` and
  `docs/research/phd-proposal/2026-09-04-one-setting-static-call-bound.md`. A call count outside
  `[16, 326]` is a stop condition.

## 14–17. Timeout, termination, privacy, rollback

- **Timeout:** 30 minutes wall clock for the whole offline run; exceeding it is a failure, not a retry.
- **Termination behavior:** the harness validates the full event stream after the run and fails closed on
  malformed lifecycles, duplicate event or question IDs, missing answers in an allegedly complete episode,
  multiple terminations, events after termination, invalid follow-up pointers, invalid
  termination/convergence combinations, or any unterminated episode.
- **Privacy:** only hashes, byte lengths, and machine fields are persisted; raw prompts and answers are
  never written to committed evidence; provider keys are reported PRESENT/ABSENT only, never by value.
- **Rollback/cleanup:** the run writes only inside the single gitignored output directory above; cleanup is
  deletion of that directory alone; no tracked or protected file is touched, so code rollback is a no-op.

## 18. Stop conditions

Any hash drift (runtime, archive, protected file); non-empty output directory; any socket or provider
credential access; any lifecycle validation failure; call count outside `[16, 326]`; `origin/main` moving
past the bound commits without re-verification; any attempt to treat fake-route observations as
provider-backed production routes.

## 19. Provider boundary

Provider-backed calls remain **forbidden** under this packet in every mode. Expected counters:
`protected_orchestrator_fake_route_count = NOT_EXECUTED` until the granted execution, an integer after it;
`provider_backed_production_route_count = 0`; `external_provider_call_count = 0`. A paid provider run
requires a further, separate authorization after this preflight passes and is not requested here.

## 20. Expiration

This packet expires immediately if `origin/main` changes in a way that alters any §3–§6 hash, if any
protected file in §5 changes, or if the preparation PR is not merged as pushed. Re-issue with fresh
bindings in any of those cases.

**Owner decision: `PENDING — Ali must explicitly grant or reject this packet in chat.`**
