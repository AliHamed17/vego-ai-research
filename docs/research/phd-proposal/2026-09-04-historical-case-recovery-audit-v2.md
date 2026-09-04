# Historical case-recovery audit v2 (independent inventory)

**Status: DATA RECOVERY NO-GO**
**Audit version:** `historical-case-recovery-v2`
**Date:** 2026-09-04
**Provider calls:** 0
**Synthetic models generated:** 0

## Purpose and boundary

This successor audit corrects the v1 circularity in which `expected_count` was
derived from the local file count and `missing` could never increase. It keeps
the v1 artifacts as historical evidence and writes a separate v2 output
directory. It does not call a provider, inspect model text in reports, generate
synthetic data, or claim that any recovered bytes were consumed by the
historical run.

`RECOVERED_VERBATIM` means only that a local file is byte-identical to the
same-named member of the supplied archive. It is not historical-run or
supervisor provenance.

## Independent inventories

The executable audit independently enumerates:

1. local files under each of the four declared model directories;
2. every archive member under `VEGO-AI/models/<setting-directory>`;
3. evaluation case identifiers under each setting's `eval_output` directory;
4. the documented aggregate counts (178 paper records and 179 scored rows),
   which are retained as different units rather than treated as file names.

The complete row-level inventory and hashes are in
`historical-case-recovery-v2/provenance-manifest.json`.

## Frozen result

| Setting | Local | Archive members | Exact intersection | Documented aggregate | Evaluation IDs | Readiness |
|---|---:|---:|---:|---:|---:|---|
| `ucd_pw` | 37 | 37 | 37 | 44 | 37 | Not executable: historical binding unresolved |
| `cd_pw` | 37 | 37 | 37 | 41 | 37 | Not executable: historical binding unresolved |
| `ucd_ch` | 45 | 45 | 45 | 46 | 45 | Not executable: historical binding unresolved |
| `cd_ch` | 46 | 46 | 46 | 47 | 46 | Not executable: historical binding unresolved |
| **Total** | **165** | **165** | **165** | **178** | **165** | **No scientifically admissible setting** |

Archive SHA-256: `bce905ff4a1af274f106fd052692f7b1c6b47a7614b65877152a9ed74225a2c9`.
The archive and local model universes have no membership differences in this
snapshot; that is not a completeness proof because no independent 178-file
identity universe was supplied.

## Set-difference and validation result

- archive ∩ local: 165 named paths;
- archive − local: 0;
- local − archive: 0;
- evaluation IDs − recovered IDs: 0;
- recovered IDs − evaluation IDs: 0;
- independently supplied expected universe: none;
- duplicate archive names: 0;
- duplicate local case IDs: 0;
- duplicate-content groups: 2 (reported, not deduplicated);
- validation findings: 7 rows are non-UTF-8 or missing the PlantUML wrapper.

The exact lists and row-level validation statuses are machine-readable in
`expected-case-inventory.json`. Because an independently documented expected
member universe is absent, the completeness verdict is
`COMPLETENESS_UNRESOLVED`, not `MISSING=0`, `100% complete`, or executable.

## Reconciliation and admissibility

The 165 raw files, 178 paper aggregate records, and 179 scored rows are
different historical units/version snapshots. No difference is converted into
a missing-file count or a synthesis target. The v2 audit therefore marks all
four settings `NOT_EXECUTABLE_HISTORICAL_BINDING_UNRESOLVED` and exposes an
empty scientifically admissible-settings list. A future closure requires an
independent expected member/slot universe plus authoritative historical-run
binding; it must not be inferred from local counts.

## Verification

Focused historical-recovery tests cover archive-only, local-only,
expected-but-absent, unrelated archive members, empty models, byte mismatch,
duplicate archive names and case IDs, duplicate content, setting-directory
mismatch, non-UTF-8 input, and missing PlantUML wrappers. The v2 outputs are
canonical and deterministic, contain metadata and hashes only, and preserve
the no-provider/no-synthetic boundary.
