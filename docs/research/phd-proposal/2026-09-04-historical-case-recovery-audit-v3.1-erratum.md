# Historical case-recovery audit v3.1 — correction and AirTravel technical gate

**Status: DATA NO-GO / TECHNICAL NO-GO for any provider-backed run**  
**Audit base SHA:** `cbc2fb5e3c05471cf37c0eef55a48857e2066403`  
**Evidence parent SHA:** `36602e41a3a7ccec52a300d9244f3afe4702153f`  
**Provider, experiment, Detector-v1, and synthetic calls:** 0

This is an explicit successor/erratum to v3. The v3 report and history remain
unchanged and are superseded evidence; this document does not rewrite them.

## Archive and historical counts

The expected archive SHA-256 is
`8d37f3adb28e70b09bd095e7cf27b055c8488369aecd3628960a148d11b5b384` and was
verified against the available original archive. The requested `(1)` filename
was not present locally; no copy or transformation was made.

The archive contains 632 entries and 165 normalized model files. Comparison
with the audit-v2 manifest is **165/165 exact file-level matches**. The first
completed Phase-C blocks report 44/37 (`ucd_pw`), 41/37 (`cd_pw`), 46/45
(`ucd_ch`), and 48/46 (`cd_ch`) loaded/unique rows; total 179/165. Ranking
lengths are 44, 41, 46, and 48.

## Corrected duplicate terminology

The v3 field `duplicate_version_rows` is replaced by
`duplicate_id_excess_rows`. There are 14 excess rows: 12 differing-length
excess rows and 2 same-length excess rows:

- `cd_pw/70248`: `[3822, 3822]`
- `ucd_pw/70248`: `[2719, 2719]`

Length equality or difference is only an observation; it does not establish
content identity or content difference.

## 165 / 178 / 179 reconciliation

These counts remain distinct: 165 unique IDs, 179 historical runtime rows, and
178 published aggregate records. The published workbook has 164 rows and 152
unique stable keys. Count alone does not create 178 authoritative slots.
`CD_CH_48_VS_47_UNRESOLVED` remains the controlled disposition.

## Measured executability

For each normalized model, v3.1 measures the evaluator's actual decode/read
behavior, PlantUML wrapper presence, and offline input-loader acceptance. These
are reported independently from provenance and scientific admissibility.
Syntactic validation is `NOT_INVOKED` because no PlantUML parser was run.
All four settings decode and load successfully at the evaluator text-loader
level; wrapper status is partial (invalid or incomplete wrappers remain).
Scientific admissibility is **NO** for every setting.

## 68065 and provenance

The four 68065 files remain byte-confirmed as `CONTENT_SWAPPED`; no repair was
performed. All 165 files are `RECOVERED_VERBATIM` relative to the named backup;
zero are `ORIGINAL_VERIFIED`, historically run-bound, or scientifically
admissible. Confirmed missing slots and authorized synthetic gap fill both
remain zero.

## Claude v1.0.2 amendment and AirTravel gate

The fetched public review branch is `origin/review/study1-airtravel-v102` at
commit `8561aa0b9e241255f0f2346ac85180758f3ccb53`. Its v1.0.2 amendment manifest
hash is `a4097902494f313594ab0b24e843280f6a1041889d72ddd2c53412353191c791`.
The pinned AirTravel archive is unavailable in this checkout, so the dedicated
verifier fails closed: exact five-file runtime-byte verification is **BLOCKED**,
not assumed. Reference-model separation therefore remains pending the same
archive. No GPL-covered source bytes were committed.

The intended identifiers remain separate: `setting_id=cd_airtravel` and
`corpus_id=text2uml_airtravel_253b26dc`. License is GPL-3.0; attribution and
redistribution review are pending. Historical Cheers/ParkWise evidence and the
AirTravel feasibility gate are independent tracks.

## Offline instrumentation

The protected orchestrator was exercised only through its deterministic local
fake-provider fixture. Prompt parity and scientific-state parity passed; all
six agent route pairs were observed, with 21 metadata events and 7 terminal
events. This is fixture evidence, not production-observed instrumentation and
not an AirTravel run. Exact AirTravel orchestration remains blocked by the
missing runtime archive and any protected-change authorization requirement.

## Remaining gates and verdict

Static AirTravel bound for frozen `N=4` remains minimum `4 + 3N = 16` and
retained worst-case `82 + 61N = 326`; API cost is **TO BE MEASURED**. Provider or
model selection, exact runtime-byte verification, license clearance, protected
authorization, and paid-run authorization remain pending.

Local focused, full, privacy, security, compile, and evidence checks pass. CI
run [33891001839](https://github.com/AliHamed17/vego-ai-research/actions/runs/33891001839)
passes all Python 3.10–3.13 jobs and fails only the stale
`release-manifest-v3.json` source gate; merge-gate fails consequently. That gate
was not bypassed.

**Final verdict: TECHNICAL NO-GO.** Stop before any provider-backed run.
