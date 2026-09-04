# VEGO-AI historical case recovery audit

**Status: RECOVERY GO — metadata recovery complete; historical scientific admissibility remains pending Claude/human review.**  This audit is a byte-recovery and inventory exercise. It is not a provider-backed experiment, an accuracy evaluation, or permission to generate replacement models.

## Evidence boundary

The supplied archive `VEGO-AI-20260611T112722Z-3-001.zip` was hashed as `bce905ff4a1af274f106fd052692f7b1c6b47a7614b65877152a9ed74225a2c9`. The ignored local `VEGO-AI/models` inventory was compared with archive members without extracting or emitting model text. Every compared byte stream was hashed twice through deterministic canonical output generation. Provider calls: **0**. Synthetic models generated: **0**.

## Count reconciliation

The defensible file-level inventory is **165** raw model files: `ucd_pw=37`, `cd_pw=37`, `ucd_ch=45`, and `cd_ch=46`. The archive contains the same 165 model members, and all 165 local files match their corresponding archive members byte-for-byte.

Two other controlled records use different units or snapshots: the paper historical aggregate is **178** (`46+47+44+41`, with no unambiguous setting binding in the recovered evidence), while the current evaluation record reports **179 scored rows**. The unexplained arithmetic differences are therefore **13** and **14**, respectively; they are not evidence of missing model bytes and are not filled synthetically.

## Provenance and readiness

| Setting | Expected raw files | Recovered verbatim | Partial | Missing | Recoverable | Technical readiness |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| `ucd_pw` | 37 | 37 | 0 | 0 | 100% | executable from recovered bytes, subject to provenance review |
| `cd_pw` | 37 | 37 | 0 | 0 | 100% | executable from recovered bytes, subject to provenance review |
| `ucd_ch` | 45 | 45 | 0 | 0 | 100% | executable from recovered bytes, subject to provenance review |
| `cd_ch` | 46 | 46 | 0 | 0 | 100% | executable from recovered bytes, subject to provenance review |
| **Total** | **165** | **165** | **0** | **0** | **100%** | **technically executable; not scientifically authorized** |

No row is labelled `ORIGINAL_VERIFIED`: the archive gives exact byte recovery, but it is not an independently signed historical-run record. Every row is `RECOVERED_VERBATIM`, carries the archive hash, local hash, byte length, encoding/wrapper metadata, relative source member, and `admissibility_pending_claude=true`. Two duplicate-content hash groups (four slots) are recorded as a finding; they are not collapsed or treated as identity ambiguity because their setting and filename bindings remain distinct.

## Synthetic-gap decision

The exact proposed synthetic gap count relative to the recoverable raw inventory is **0**. `SYN-GAP-000` is explicitly `NOT_PROPOSED`; the 178- and 179-based alternatives are rejected because they conflate historical aggregates/scored rows with raw file inventory. Option A (verified recovered bytes only) is recommended. Option B (minimal synthetic gap) is not justified. Option C (Text2UML/AirTravel) remains a separate, non-mixed external feasibility corpus (observed candidate count 4, not frozen for this audit).

## Deliverables

- `historical-case-recovery/expected-case-inventory.json` — count evidence and reconciliation.
- `historical-case-recovery/provenance-manifest.json` — one metadata row for each of the 165 slots; no model text.
- `historical-case-recovery/missingness-report.json` — per-setting and aggregate recoverability.
- `historical-case-recovery/synthetic-gap-fill-proposal.json` — zero-execution proposal and rejected alternatives.
- `historical-case-recovery/text2uml-comparison.json` — explicit corpus-separation record.
- `historical-case-recovery/recovery-evidence-receipt.json` — archive/manifest hashes and no-call/no-synthesis receipt.

The audit script is `scripts/audit_historical_case_recovery.py`; focused tests are in `scripts/tests/test_audit_historical_case_recovery.py`. These artifacts do not authorize a provider-backed run. Claude/human review is required to bind the recovered bytes to a particular historical run and approve any future scientific use.
