# Text2UML/AirTravel v1.0.2 pre-run technical gate

**Status: TECHNICAL NO-GO — amendment and green-CI gates are missing.**  No
provider, API, external model, or experiment was invoked.

This receipt consumes the approved scientific boundary literally.  The Claude
v1.0.2 amendment artifact (including its frozen runtime-byte manifest and
commit identifier) was not present in the repository, attachments, or local
Claude project at verification time.  The existing AirTravel pack is therefore
reported as an observed preparation pack, not silently promoted to v1.0.2.

## A–T gate record

| Item | Evidence-bound result |
|---|---|
| A. Current `main` SHA | `e242c83c4a767ff9e092d24888f6649a0b3d3ff0` (pushed to `origin/main`). |
| B. Claude v1.0.2 commit | **NOT SUPPLIED / NOT FOUND**. Known prior preregistration is v1.0.1 at `917f1089b4e8d19fdc39d5f80a59e3663ab664cd`; it is not substituted. |
| C. Text2UML upstream SHA | `253b26dc704d523209a5cba79686f8f7fab57d63` (`IlKaiser/text2uml`). Archive SHA-256: `8cf82e2ab2d2ce3da9a7ec4165e760ae1e0d9af14468f5aa2a3883037d8da701`. |
| D. Input-manifest hash | `source-manifest.json` SHA-256 `f13f4172f05422971c3d049d9be672b5befb9f49a1ab5f4589dda3587aa2910c`. |
| E. Selected runtime files and hashes | Observed pack: `description.md` (1,477 bytes; `96bc8a6fbf2c2fdd93592fdbf6fac7c2b9db403494fe2d5a45e0a2bcbf0167e2`); `01_result_one_claude-sonnet-4-6.txt` (1,248; `240b034834e383b9844e9a3e9796f6be9b3d47fc95de6606ed022d278d751f91`); `02_result_one_codestral-2508.txt` (1,272; `08399ca9432c1399f3f9784d34741314e4d39e40307a6efb14fa92a1c138b1d6`); `03_result_one_deepseek-chat.txt` (1,324; `ee4d689d59c9ce3a5e8ff385747641954bd4821f2efeb18e581dcd1d5441d20a`); `04_result_one_gemini-2.5-flash.txt` (1,231; `1c3d15eac71fcaab138857dbbc7153833b3df55ab57925ac756a79dc28dc847a`); `LICENSE` (35,149; `3972dc9744f6499f0f9b2dbf76696f2ae7ad8af9b23dde66d6af86c9dfb36986`). These are **not v1.0.2-verified** until Claude’s manifest is supplied. |
| F. Reference separation | `reference_only/plantuml.txt` (1,300; `01448d859c916a4229a2becec2e3675614ab6f00495d9049ace30b7c82bb7b98`), `plantuml_adjusted.txt` (1,328; `17c4179653fcfea5b2bfd306cb1382d1b93bc5dc946419f85e8fc5e4b480f3ff`), and `extramaterial/AirTravel.cd4a` (1,452; `51a73df36663ab70e251e365266cc51d9a3f2c41ddf2dcf2a3cc106246ce61df`) are outside `runtime_input`; the verifier and configuration contain no reference path under runtime input. |
| G. Production instrumentation | Offline observer and protected Q&A contract are implemented and tested; direct provider wiring remains intentionally partial. Production route invocations observed: **0**. |
| H. Prompt parity | Offline parity tests pass for provider-off versus provider-on construction; no provider call occurred. |
| I. Scientific-state parity | Offline parity tests pass; candidate escalation remains descriptive only, with no accuracy, benefit, or superiority claim. |
| J. Concurrency/identity | Async correlation and independent-process deterministic episode identity tests pass; stable identity hashes scientific context and excludes counters, task IDs, and addresses. |
| K. Lifecycle adversarial tests | Mixed runs, cross-episode answers, duplicate/missing answers, empty terminal episodes, multiple terminals, and post-termination events fail closed. |
| L. Detector-v1 truth table | 20 focused tests pass; strong precedence and `all_signals_fired` behavior preserved; C1/S5/S8/S9 remain non-triggering. Detector was not applied to AirTravel outputs. |
| M. Frozen N and call bound | Observed proposed `N=4`; minimum `4 + 3N = 16`; retained worst-case `82 + 61N = 326`. These are static bounds only and must be recalculated from the v1.0.2-frozen N. |
| N. Model configuration | `setting_id=cd_airtravel`; `corpus_id=text2uml_airtravel_253b26dc`; provider execution disabled at global and setting levels; model/provider unspecified. |
| O. API cost | **TO BE MEASURED** after explicit authorization and a provider run; current cost is not estimated. |
| P. Protected authorization | No protected authorization was self-issued. Full hash-bound request packet: `2026-09-04-airtravel-v102-protected-authorization-packet.md`. |
| Q. Full tests | Root `46 passed`; VEGO-AI `134 passed`; scripts `331 passed, 10 skipped, 7 subtests passed`; focused AirTravel/Q&A `28 passed`; detector/policy `20 passed`; compileall passed; privacy, security, evidence consistency, and research-record validation passed. Full-repository Ruff is **FAIL** on 116 pre-existing findings; touched files pass Ruff. |
| R. CI | Latest pushed run `33879580478` (head `e242c83…`): Python 3.10/3.11/3.12/3.13 **SUCCESS**; Source/security/documents **FAIL** at stale `docs/research/hardening/release-manifest-v3.json`; merge-gate **FAIL**. CI is not green. |
| S. Remaining blockers | (1) obtain and hash-bind Claude v1.0.2 amendment; (2) verify every runtime byte against that manifest; (3) resolve stale release manifest under authorized change; (4) rerun CI to green; (5) obtain explicit human authorization before any provider call. |
| T. Final verdict | **TECHNICAL NO-GO**. When blockers clear, the permitted stopping state is **TECHNICAL GO — AWAITING EXPLICIT HUMAN AUTHORIZATION TO RUN**. |

## Verification boundary

`scripts/verify_text2uml_airtravel_runtime.py` is fail-closed: a missing
amendment manifest returns `BLOCKED` and cannot infer v1.0.2 from observed
files. Unit tests cover missing-manifest blocking, hash drift, ID separation,
reference separation, and provider-disabled configuration. The script performs
no network or model operation.
