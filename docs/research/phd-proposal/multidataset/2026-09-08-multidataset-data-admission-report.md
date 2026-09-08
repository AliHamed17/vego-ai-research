# VEGO-AI Study 1 — multi-dataset admission status

Status: `NO_GO_FOR_PROVIDER_EXECUTION`. This is a metadata-only admission report,
not a result report. It made no provider/API/model call and spent USD 0.

## Evidence boundary

- `AIRTRAVEL_QA_FEASIBILITY_BASELINE` remains archival, retrospective,
  descriptive evidence. It is not pooled with the datasets below.
- `QURE_EXTERNAL_REQUIREMENTS_QUALITY_VALIDATION` is not admitted. The pinned
  concept DOI is [`10.5281/zenodo.15656471`](https://doi.org/10.5281/zenodo.15656471);
  the captured version record is
  [`10.5281/zenodo.15656472`](https://doi.org/10.5281/zenodo.15656472). The
  record-specific licence, local raw-file hash, and versioned file inventory
  are not yet verified.
- `VEGO_SE_ARCHIVE_DATASET_PENDING_ADMISSION` is a metadata-only local archive
  inventory. Its provenance, licence, and task fit are unverified; no content
  inspection or provider execution was performed.

## Admission decisions

| Dataset | Decision | Blocking conditions | Permitted statement |
| --- | --- | --- | --- |
| QuRE | `NOT_ADMITTED` | `LICENCE_UNVERIFIED, RAW_FILE_HASH_UNAVAILABLE, VERSIONED_FILE_INVENTORY_UNAVAILABLE` | Official metadata was located; no requirements-quality experiment was run. |
| VEGO_SE archive | `NOT_ADMITTED` | `PROVENANCE_UNVERIFIED, LICENCE_UNVERIFIED, TASK_FIT_UNVERIFIED` | A local archive was inventoried by ZIP metadata only. |

## Claim boundary

No multi-dataset baseline, association result, ON/OFF result, alert accuracy,
human benefit, or generalisation claim has been established. QuRE labels, if
later admitted, are external requirements-quality labels —
`NOT_DIRECT_ALERT_GROUND_TRUTH`.
