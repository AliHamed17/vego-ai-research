# Protected-change authorization packet — historical recovery v3

**Status:** NOT REQUESTED / NO PROTECTED FILES TOUCHED  
**Base SHA:** `58311c2ec29e13b68ad19005b4e62b5b6420b227`  
**Proposed head SHA:** `6098d35dbfdaf0cc49eba465ba826d38bfe1ddca`  
**Human authorization:** not supplied; no protected authorization record was created or modified.

## Scope decision

The v3 audit reads the supplied project-backup ZIP and existing public repository
artifacts only. It does not modify protected runtime, provider, experiment,
Detector-v1, dataset, authorization, or release-manifest files. Consequently
there is no protected old/new file pair to authorize and no old/new protected
SHA-256 pair to report. The audit must not be promoted to a provider-backed run
without a new, explicit human authorization packet covering that separate change.

## Evidence hashes

| Artifact | Repository-relative path | SHA-256 |
|---|---|---|
| Supplied backup | external input; original local path intentionally not tracked | `8d37f3adb28e70b09bd095e7cf27b055c8488369aecd3628960a148d11b5b384` |
| Backup receipt | `docs/research/phd-proposal/historical-case-recovery-v3/backup-evidence-receipt.json` | `f47abefa1fa8e8fdbba13aefabed333a6a5527f9466c63d466739708b76a2162` |
| Historical load universe | `docs/research/phd-proposal/historical-case-recovery-v3/historical-load-universe.json` | `fff9ec305955c69923373101417a03ccb8c06ff3bc89289ccfc46ee4b9ec7bd8` |
| Provenance summary | `docs/research/phd-proposal/historical-case-recovery-v3/provenance-binding-summary.json` | `fef6945995b4a25e6b20fadfe82e7288b4c8bd4e54eafd57d365fceec88b432f` |

## Scientific justification and risk

The archive is byte-verified at the normalized file level (165/165), but no
file is historically run-bound or scientifically admissible. The `165/178/179`
units do not reconcile to an exact published universe, `CD_CH_48_VS_47_UNRESOLVED`
remains open, and the 68065 pair is byte-confirmed as `CONTENT_SWAPPED`. Using
these artifacts for a live run could misattribute cases, settings, or outcomes;
that risk is unacceptable without a new controlled recovery decision.

## Requested future authorization (not granted)

If the human owner later wants to proceed, the request must name exact protected
repository-relative paths, provide full old and proposed new SHA-256 hashes,
state the scientific purpose and rollback plan, and include an expiry timestamp.
The scope must explicitly exclude provider calls, synthetic generation, raw
student/expert material publication, and any unreviewed repair of 68065 or the
`CD_CH_48_VS_47_UNRESOLVED` discrepancy.
