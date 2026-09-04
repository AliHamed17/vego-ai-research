# Historical recovery v3.2.1 — AirTravel materialization and verifier hardening

**Status: TECHNICAL NO-GO**  
**Audit base SHA:** `b2275c34755352b2caefe3a2cdd3a72903b16a1d`  
**Provider, external-model, Detector-v1, and paid-experiment calls:** `0`

This is a successor/erratum to v3.2. Earlier v3/v3.1/v3.2 files remain
preserved as superseded evidence. The historical path is now independent of
the obsolete AirTravel branch and does not call `v3.1.audit_v31()`.

## Authority and source receipt

- PR #36 head consumed: `3c2eb4494c89fbbd0d6ac05c3ff4aeaaeff78bee`
- v1.0.2 manifest SHA-256: `bd2b7f03585582ff7591d21795fbd3ed4701244d66d26221683520238c2dead2`
- Upstream commit: `253b26dc704d523209a5cba79686f8f7fab57d63`
- Codeload archive SHA-256: `8cf82e2ab2d2ce3da9a7ec4165e760ae1e0d9af14468f5aa2a3883037d8da701`
- Archive verification: **PASS**, exactly 143 dataset/AirTravel files; matched 143,
  missing 0, extra 0, mismatched 0, duplicate members 0.

The downloaded archive and derived runtime pack are under the ignored
`external_data/airtravel-v3.2.1/` directory. No upstream source bytes are
tracked.

## Historical reconciliation

The supplied private project archive remains an exact **165/165** normalized
model match. Historical loads are 44/37 (`ucd_pw`), 41/37 (`cd_pw`), 46/45
(`ucd_ch`), and 48/46 (`cd_ch`); ranking counts are 44, 41, 46, 48. Duplicate
ID excess is 14 (12 differing-length and 2 same-length). The 165 unique IDs,
179 historical rows, and 178 published records remain distinct. The
`CD_CH_48_VS_47_UNRESOLVED` and 68065 `CONTENT_SWAPPED` findings are preserved.
Confirmed missing slots remain 0 and authorized synthetic gap fill remains 0.

## Source-to-runtime mapping

The PR #36 mapping passes all strict requirements: exactly five mappings, five
unique source paths, five unique runtime paths, one domain description, four
candidate models, expected transformation values, `byte_transformation=NONE`,
declared lengths, and SHA-256 values. Byte identity is `true`; missing and
mismatched lists are empty.

## Runtime pack

The ignored deterministic pack is
`external_data/airtravel-v3.2.1/cd_airtravel-runtime-v1.0.2.zip` (SHA-256
`fb4f0d4b2be76aa25665af972c0491829f4310cd30db5e10b46f718c80da1933`). It has
exactly five observed/expected files, no extras, duplicates, missing files,
mismatches, or reference paths. The mandatory configuration passes with
`setting_id=cd_airtravel`, `corpus_id=text2uml_airtravel_253b26dc`, description
path `domain_description/description.md`, candidate directory
`candidate_models`, and `provider_execution_enabled=false`.

## Fake-provider preflight and gates

The exact protected `cd_airtravel`, N=4 orchestrator preflight is
`BLOCKED_PROTECTED_CONFIG`; it was not executed because protected observer
authorization is absent. Provider calls remain 0. Production-observed routes
remain 0; fixture-only routes are not substituted. Static bound is `4 + 3N`:
N=4 gives minimum 16 and retained worst-case 326. API cost remains **TO BE
MEASURED**. GPL-3.0 redistribution review, model/budget selection, and paid-run
authorization remain pending.

## Verification and CI

Focused v3.2.1 tests pass (`9 passed`, one expected duplicate-ZIP warning),
ruff and compilation pass. The latest full local suites are `346 passed,
22 skipped` in `scripts/tests`, `134 passed` in `VEGO-AI/tests`, and `46 passed`
in the root suite; evidence consistency, security, and privacy checks pass.

CI run [33915362487](https://github.com/AliHamed17/vego-ai-research/actions/runs/33915362487)
is not green: Python 3.10–3.12 passed, Python 3.13 remained incomplete in the
final API state, the source job failed on the stale `release-manifest-v3.json`,
and merge-gate failed. The stale authorization gate was not bypassed.

**Final verdict:** source/mapping/runtime preparation is PASS, but the overall
technical gate is **TECHNICAL NO-GO** while CI is red, protected observer
authorization is absent, and model/budget/paid-run authorization remain open.
If those gates later pass, the next stopping state is **TECHNICAL GO — AWAITING
MODEL/BUDGET AND EXPLICIT PAID-RUN AUTHORIZATION**. No real provider run is
authorized or performed.
