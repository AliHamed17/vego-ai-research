# Study 1 one-setting input recovery and readiness

**Audit date:** 2026-09-04 (Asia/Jerusalem)
**Scope:** read-only recovery for the pre-run technical gate; no provider call and no evaluation-output inspection.

## Evidence boundary

The current `VEGO-AI/eval/eval_config.json` references four external case-model directories (`ucd_pw`, `cd_pw`, `ucd_ch`, `cd_ch`). None of those configured directories exists in the current checkout. A metadata-only inventory across the repository, Downloads, OneDrive Documents, Claude workspaces, and Codex attachments found two byte-identical copies of one ParkWise use-case model candidate (SHA-256 `cd90fc1d1b4ba57428ae10f97ebdf233acf13bfe1c5a13082c8da326c6481a1f`, 45,430 bytes). The candidate is not bound to a setting, is not a complete four-setting corpus, and is not promoted into the frozen baseline.

The private inventory receipt is generated at `reports/generated/case_model_recovery/2026-09-04-input-recovery.json` and is intentionally ignored by Git. It records absolute paths, hashes, and archive-member metadata for local recovery only (12 relevant archives; member names were inspected without extraction). No case-model content was copied into tracked artifacts.

## Readiness matrix

| Setting | Configured path exists | Candidate evidence | Readiness | Action before provider run |
|---|---:|---|---|---|
| `ucd_pw` | No | One unbound ParkWise use-case candidate | `BLOCKED_INPUT_BINDING` | Confirm provenance, bind to the setting, and freeze manifest |
| `cd_pw` | No | None | `NOT_FOUND` | Supply or restore the class-diagram cases |
| `ucd_ch` | No | None | `NOT_FOUND` | Supply or restore the Cheers use-case cases |
| `cd_ch` | No | None | `NOT_FOUND` | Supply or restore the Cheers class-diagram cases |

## Gate decision

The one-setting run is **not ready**. The minimum safe unblock is a user-supplied, provenance-bound case-model directory for one declared setting, with a manifest containing file hashes and a reviewable mapping. Until that happens, the controlled baseline remains descriptive and the provider-backed run remains prohibited.
