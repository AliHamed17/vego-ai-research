# Historical case-recovery audit v3 — 2026-09-02 project backup

**Status: DATA NO-GO / TECHNICAL NO-GO for any provider-backed run**
**Backup SHA-256:** `8d37f3adb28e70b09bd095e7cf27b055c8488369aecd3628960a148d11b5b384`
**Current main:** `bc81cf0b2f86326473dc9e75b26d6f61e1dc58bb`
**Provider, experiment, Detector-v1, and synthetic calls:** 0

## Scope and preservation

This is a v3 successor audit. The v1 audit and commits `3f036350` and
`e999c480` remain preserved as superseded evidence; they were not rewritten.
The supplied backup hash matches the expected hash. Claude's unpushed
AirTravel commit `ff0a61a` was not modified or consumed.

## Independent archive and file comparison

All 632 ZIP entries were enumerated with `ZipFile.namelist()`. The four
normalized `System/models` directories contain 165 files: 37 `ucd_pw`, 37
`cd_pw`, 45 `ucd_ch`, and 46 `cd_ch`. Every normalized file was compared with
the v2 provenance manifest: **165/165 exact file-level matches**.

A different container ZIP hash can coexist with identical internal model bytes
because ZIP metadata, compression, directory ordering, and unrelated files can
change while the decompressed model entries remain byte-identical.

## Historical load universe

The first completed Phase-C load block in each evaluator log independently
produced:

| Setting | Load rows | Unique IDs | Duplicate-version rows | `agentC_all_scores` ranking |
|---|---:|---:|---:|---:|
| `ucd_pw` | 44 | 37 | 7 | 44 |
| `cd_pw` | 41 | 37 | 4 | 41 |
| `ucd_ch` | 46 | 45 | 1 | 46 |
| `cd_ch` | 48 | 46 | 2 | 48 |
| **Total** | **179** | **165** | **14** | — |

Duplicate groups are retained in the machine-readable load universe by case ID
and logged length. Filenames and raw content are not published.

## 165 / 178 / 179 reconciliation

These are separate units:

- 165 unique IDs and normalized model files;
- 178 published aggregate records (`46 + 47 + 44 + 41`);
- 179 runtime-loaded/scored rows.

The published workbook contains 164 stable-key rows in this backup, with
setting counts `cd_ch=44`, `cd_pw=37`, `ucd_ch=43`, and `ucd_pw=40`.
Its relationship to the 178 published aggregate count cannot be proven from
the available stable keys. Therefore the specific discrepancy is explicitly
`CD_CH_48_VS_47_UNRESOLVED`; no row is labeled omitted, filtered, overwritten,
or accidentally duplicated.

## Content binding

The audit reports exact duplicate hashes among normalized models, ID/decoded
stripped-length comparisons with historical logs, and all encoding/wrapper
findings without emitting model text. Six normalized files are non-UTF-8; one
is missing the complete PlantUML wrapper. The 159 remaining files match a
logged case ID and stripped decoded length.

The apparent 68065 Cheers cross-directory swap is byte-confirmed: the dataset
UseCase file has the same hash and length as the System Class file, and the
dataset Class file has the same hash and length as the System UseCase file.
The result is classified `CONTENT_SWAPPED`; no repair was performed. The
evaluator-log length is supporting evidence, not cryptographic proof of the
historical source binding.

## Provenance and readiness

`RECOVERED_VERBATIM` is limited to byte identity with the specifically named
archive. No file is promoted to `ORIGINAL_VERIFIED`, historically run-bound, or
scientifically admissible.

For every setting the report separates: populated directory, parser
compatibility, technical loadability, unique-ID completeness, byte binding to
historical raw input, and scientific admissibility. The directories are
populated and complete relative to the normalized archive subset; technical
loadability is blocked by invalid rows and no historical binding is proven.
No setting is historically or scientifically admissible.

## Synthetic policy

`CONFIRMED_MISSING_SLOTS = 0` and `AUTHORIZED_SYNTHETIC_GAP_FILL = 0`.
Neither 178−165 nor 179−165 defines a slot or a synthesis target.

## AirTravel feasibility preparation

The pinned Text2UML source manifest was independently checked against the
local pinned archive: 143/143 manifest file hashes match, including the
declared upstream commit `253b26dc704d523209a5cba79686f8f7fab57d63` and
archive hash `8cf82e2ab2d2ce3da9a7ec4165e760ae1e0d9af14468f5aa2a3883037d8da701`.
The intended setting/corpus remain `cd_airtravel` /
`text2uml_airtravel_253b26dc`, N=4. The source is GPL-3.0; redistribution and
attribution review remain pending. AirTravel remains feasibility-only and is
not frozen or executed by this audit.

## Verification and blockers

Focused and full local tests passed; no provider-backed activity occurred.
GitHub Actions run [33890423134](https://github.com/AliHamed17/vego-ai-research/actions/runs/33890423134)
passed all four Python matrix jobs. The source/security/documents job failed
on the pre-existing stale `release-manifest-v3.json`, and the merge gate failed
consequently. Refreshing that manifest requires the repository-controlled Agent
4 output and was not self-authorized.

The complete evidence-safe outputs are in
`historical-case-recovery-v3/backup-evidence-receipt.json`,
`historical-load-universe.json`, and `provenance-binding-summary.json`.
