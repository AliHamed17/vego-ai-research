# Study 1 protected-change authorization packet

**Status:** Request for human-owner review; no authorization is granted by this
document. No provider, API, external model, or real experiment was invoked.

## Scope and provenance

- Repository: `AliHamed17/vego-ai-research`
- Local checkout: `C:\Users\ahamed\vego-ai`
- Base SHA: `cab11051d7af7347540c32440bb068ae2c6333b1`
- Proposed implementation head SHA: `e45ee35b3cc0d5a64b55d3cfa1f1431006770e88`
  (the commit containing the technical correction)
- Scientific interpretation: Claude's immediately preceding episode-semantics
  clarification and the preregistered v1.0.1 termination contract control.

## Exact file hashes

SHA-256 values below are byte hashes of the files at the base commit and at the
proposed implementation head. The base values are independently read from the
Git object; the new values were computed from the working-tree bytes before
commit.

| Repository-relative path | Full local path | Old SHA-256 (base) | New SHA-256 (proposed head) |
|---|---|---|---|
| `VEGO-AI/framework/qa_communication.py` | `C:\Users\ahamed\vego-ai\VEGO-AI\framework\qa_communication.py` | `e46f03a53fdba17b2669c32882d56853a71a0e26684cd4534093caa0222738da` | `9f2cda1dc52fe919be22ac2ea42d61dce3ed22d3fae7ae27077b3db821594236` |
| `VEGO-AI/framework/qa_instrumented_runner.py` | `C:\Users\ahamed\vego-ai\VEGO-AI\framework\qa_instrumented_runner.py` | `7b3c811ca702f30e2b0536ac5f8163764658b0fcc21db309b5e5133cea318393` | `2176830dea96f6e467d7feb544c715c20cd6bd1ae97cbd73cb4ca2c48608d73d` |
| `VEGO-AI/tests/test_qa_communication.py` | `C:\Users\ahamed\vego-ai\VEGO-AI\tests\test_qa_communication.py` | `0fb35d63a9d65dd0f44517c10756eb0f161eecd2ae7032c93a7d92d2f1b9e919` | `ebd8b6dd133a617063f104056e6bce61310306ba0ba0a74e83abd4b8335b3c2d` |
| `VEGO-AI/tests/test_qa_instrumented_runner.py` | `C:\Users\ahamed\vego-ai\VEGO-AI\tests\test_qa_instrumented_runner.py` | `d9b4b75acaa45d8cbccee21e12d826fbbeccbead26c02b9e1943bfc668a0991b` | `4e6c88fec0802a7caae67bf77a37d07384014330b9646478bc795f6ebbfe7c7f` |
| `scripts/extract_qa_escalation_features.py` | `C:\Users\ahamed\vego-ai\scripts\extract_qa_escalation_features.py` | `eb801df32dfbbbdfef63c7451d7f8a804dd1c0e9c67eb8d7d7ab7793f94817f8` | `8723f8f7cb75df51d5c82bda2b604bfaa2b72c230ce580090f7ba06cf3457974` |
| `scripts/tests/test_extract_qa_escalation_features.py` | `C:\Users\ahamed\vego-ai\scripts\tests\test_extract_qa_escalation_features.py` | `29e5674272d2b54e10c42764ab1b386ca54dd59fdfe521f13fc2a394869f454b` | `56c49c08145f51983429e9d6b355ca951b67dc74f34928ae5fdafb63f46830fa` |
| `docs/research/phd-proposal/2026-09-04-one-setting-pre-run-technical-gate.md` | `C:\Users\ahamed\vego-ai\docs\research\phd-proposal\2026-09-04-one-setting-pre-run-technical-gate.md` | `7c1018d16513998050a28e40d34dd08072d2960414914c66ae99b5c62e3f5a34` | `62bc441a9543462085341bc69fe237201f3d6312568fbfca26077559dda9ceb2` |
| `docs/research/phd-proposal/2026-09-04-one-setting-static-call-bound.md` | `C:\Users\ahamed\vego-ai\docs\research\phd-proposal\2026-09-04-one-setting-static-call-bound.md` | `f7df0e01b246d1f7ef09edae2499fac8cc81a56e44aff537b5c2f092ce577e76` | `497c138eaaab3ae0b96b84a18ffd635d284c3441017a576065b66b5613110917` |
| `docs/research/phd-proposal/2026-09-04-qa-instrumentation-verification.md` | `C:\Users\ahamed\vego-ai\docs\research\phd-proposal\2026-09-04-qa-instrumentation-verification.md` | `1f3519177c0ba509b84b54cf32f2a58455b146e7287516fdf459fc5c86e2305c` | `d93d5f33bd69055a38489fc46243efe740ba280493af5523878a132829612eea` |
| `scripts/study1_call_bound.py` | `C:\Users\ahamed\vego-ai\scripts\study1_call_bound.py` | *(absent)* | `83587c8e068a5e6248354efdec348afe7c6f0a8833ca4fccb5c3e84072db66cc` |
| `scripts/tests/test_study1_call_bound.py` | `C:\Users\ahamed\vego-ai\scripts\tests\test_study1_call_bound.py` | *(absent)* | `6619f98f80455c96e1c3bc5269cc230bcf50a6e56b3816650c87f9d32a43e02a` |

## Scientific justification

The change makes the preregistered event contract executable: one run identity,
question-before-answer correlation within an episode, one terminal event, and
fail-closed exclusion of technical-incomplete or zero-question records. Episode
identity is a deterministic hash of declared scientific context (run, setting,
stage, source/target, skill, scope, case, guideline/pattern, and episode key),
with round excluded so one episode persists across rounds. The proxy correlates
the actual producer question text and rejects missing text; it never uses a
fixture-question fallback. Detector-v1 preserves strong-tier precedence while
exposing `all_signals_fired` for descriptive co-occurrence. The static minimum
call bound is corrected to `4 + 3N`; `82 + 61N` remains a separately derived
worst-case bound.

## Risk assessment

- **Scientific risk:** no labels, accuracy, human-benefit, reviewer-selection,
  or policy-superiority claim is introduced. The live experiment remains blocked.
- **Privacy risk:** only hashes, lengths, metadata, and sanitized documentation
  are tracked; raw student material, notes, secrets, private URLs, and provider
  outputs are not included.
- **Runtime risk:** `orchestrator.py`, `qa_registry.py`, and `state.py` remain
  unchanged and provider access is not reachable from the fixture harness.
- **Release risk:** the current CI source job is blocked by a stale release
  manifest; that protected authorization/release record is not modified here.

## Requested authorization

Please authorize only review and merge consideration of the listed code,
tests, schema-compatible extraction, and documentation paths, for this
correction branch, expiring **2026-09-11 23:59 Asia/Jerusalem**. Authorization
does not permit a provider-backed run, data-label import, protected manifest
change, or modification of unrelated user-owned files. The human owner must
confirm the scientific interpretation and the Hebrew/research release decision
separately.
