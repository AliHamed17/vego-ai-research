# Historical recovery v3.2 — AirTravel evidence reconciliation and technical preflight

**Status: TECHNICAL NO-GO**  
**Audit base SHA:** `8765af49fd9d15544e17371102881b88447dac46`  
**Provider, experiment, Detector-v1, and synthetic calls:** 0

This is a successor/erratum to v3 and v3.1. Earlier reports remain preserved
as superseded evidence. The inherited hard-coded AirTravel result is removed;
no 143/143 claim is made without the actual pinned archive.

## Historical evidence

The supplied archive hash is
`8d37f3adb28e70b09bd095e7cf27b055c8488369aecd3628960a148d11b5b384`.
The normalized historical model comparison remains **165/165 exact matches**.
Loaded/unique counts remain 44/37 (`ucd_pw`), 41/37 (`cd_pw`), 46/45
(`ucd_ch`), and 48/46 (`cd_ch`), with ranking counts 44, 41, 46, and 48.

Duplicate terminology is corrected to `duplicate_id_excess_rows`: 14 total,
comprising 12 differing-length excess rows and 2 same-length excess rows
(`cd_pw/70248=[3822,3822]`, `ucd_pw/70248=[2719,2719]`). Length alone does not
prove content identity or difference. The 165 unique IDs, 179 runtime rows,
and 178 published records remain distinct; `CD_CH_48_VS_47_UNRESOLVED` remains
open. 68065 remains `CONTENT_SWAPPED`, unrepaired. Historical status remains
DATA NO-GO; synthetic gap fill remains zero authorized.

## PR #36 manifest authority

PR #36 is the sole consumed scientific authority for this preflight. Its exact
head is `cb1099c214418f8ef39a98bc7e81395a444c2082`; its manifest SHA-256 is
`3cc5867366a9af7b531ff19eed57167dfacd8eab130f2cc243300ba50700bbac`.
The verifier resolves the supplied ref with `git rev-parse` and fails closed on
any mismatch. No `origin/review/study1-airtravel-v102` or commit `8561aa0` was
consumed.

## Three AirTravel verification layers

1. **Upstream source:** blocked because the pinned Text2UML archive is not
   available locally. Expected commit is
   `253b26dc704d523209a5cba79686f8f7fab57d63`; expected archive SHA-256 is
   `8cf82e2ab2d2ce3da9a7ec4165e760ae1e0d9af14468f5aa2a3883037d8da701`.
   Matched, missing, extra, and mismatched counts are therefore not asserted.
2. **Source-to-runtime mapping:** blocked. PR #36 does not provide a
   `source_path`/`runtime_path` mapping object, and upstream bytes are absent.
3. **Runtime pack:** blocked. The exact five runtime files cannot be verified
   without the pinned archive. Reference-only files are not exposed to the
   runtime configuration; byte-level separation remains pending archive access.

The intended identities remain separate: `setting_id=cd_airtravel`,
`corpus_id=text2uml_airtravel_253b26dc`. GPL-3.0 attribution and redistribution
review remain pending. No GPL-covered source bytes were committed.

## Loader and fake-provider preflight

The v3.2 implementation measures decode/read status, strict envelope status,
actual offline `load_inputs` acceptance, parser invocation status, and
scientific admissibility independently for each historical setting. All four
settings are loader-accepted; envelope checks are partial; syntactic parsing
was not invoked; scientific admissibility is NO.

The exact `cd_airtravel`, N=4 fake-provider preflight was **not run** because
the runtime-byte gate is blocked. Existing deterministic fixture tests remain
separate evidence and do not count as production-observed routes. Production
provider route count remains zero.

## Remaining gates

The independent gates are: PR #36 approval/merge, upstream archive and
source/runtime verification, production observer wiring, model/provider
selection, protected authorization, green CI, GPL redistribution scope, and
explicit paid-run authorization. Static N=4 call bounds remain 16 minimum and
326 retained worst-case; API cost is TO BE MEASURED.

CI run [33910965782](https://github.com/AliHamed17/vego-ai-research/actions/runs/33910965782)
passes Python 3.10–3.13 and fails the stale `release-manifest-v3.json` source
gate; merge-gate fails consequently. No release-manifest authorization was
bypassed.

**Final verdict: TECHNICAL NO-GO.** Stop before every real provider call.
