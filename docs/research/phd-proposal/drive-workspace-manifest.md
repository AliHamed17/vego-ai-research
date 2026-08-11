# PhD Working Drive Manifest

Date: 2026-07-30 · Contents populated: 2026-08-11
Owner: Ali (research lead)
Status: **structure implemented and populated privately; supervisor sharing and access testing still pending Ali review**

**2026-08-11 population record.** The nine-folder skeleton created on 2026-07-30 held only the
native literature Sheet; no working outputs had been uploaded, leaving the second half of `A-04`
("upload current outputs") open. 54 repo-derived files were published on 2026-08-11 by
[`scripts/publish-working-drive.ps1`](../../../scripts/publish-working-drive.ps1), which maps repository
documents to the intended content defined in the table below and writes a per-folder `_README.md`
stating that folder's honest current state. The native Google Sheet was not touched.
`07_Submission_Package` and `99_Archive` deliberately received only a `_README.md` — nothing has been
Ali-approved for submission, and nothing is yet both superseded and reviewed. Sharing and access
testing remain open (see the access gate at the end of this document); populating the folder is not
sharing it.

## Boundary

This Drive is the editable PhD working area for proposal text, literature
records, decisions, weekly pre-reads, and non-sensitive aggregate evidence. It
must not contain patient rows, MIMIC/Clalit extracts, restricted clinical
derivatives, credentials, or raw controlled participant/expert material. The
binding zone rules are in
[`../governance/phd-data-boundary.md`](../governance/phd-data-boundary.md).

The supplied MIMIC source folder remains separate from the working root:
[MIMIC-III source resource](https://drive.google.com/drive/folders/1_RheL2DUcicQLGXJyY_soUb91zn9XLsz).
Link to it; do not copy it into this working area.

A 3 August read-only metadata check corroborated the controlled item counts and
sizes, but did not prove a content-level unchanged state, the complete ACL, or
research-use authorization. See the
[Drive boundary verification record](../governance/drive-boundary-verification-2026-08-03.md).

## Implemented structure

Root:
[VEGO-AI PhD Working 2026](https://drive.google.com/drive/folders/1Och2Vlux87uqk6QZy0F4xr2WhfzY_cd-)

| Folder | Drive link | Intended content |
| --- | --- | --- |
| `00_Admin_and_Decisions` | [Open](https://drive.google.com/drive/folders/1xJgHXMybYoNUJTHD4rOwt3ubtw2kY3YY) | Decision/change log, process verification, RACI, RAID |
| `01_Research_Questions` | [Open](https://drive.google.com/drive/folders/10AyWhY7P_EzWInRG_XotGkAWCfcsSbum) | RQ decision pack, legacy crosswalk, study contract |
| `02_PhD_Proposal` | [Open](https://drive.google.com/drive/folders/1EAhtp872pCmdWCy66AQZRv-mkSjSTJLm) | Proposal versions and reviewed feedback |
| `03_Literature_Review` | [Open](https://drive.google.com/drive/folders/1FKKeWaCMeVnoKLhL99sE8iXkQNh9Q9JS) | Native literature workbook, protocols, synthesis |
| `04_SE_Modeling_Studies` | [Open](https://drive.google.com/drive/folders/1-poNJLv3iOZ7y3dIEV80FRYffkpMVRqf) | Software/modeling study material and aggregate evidence |
| `05_Medical_Feasibility_Gated` | [Open](https://drive.google.com/drive/folders/11FwDh1eMKvMOIBAXImLTYBpmmSvHVhwb) | Non-sensitive feasibility metadata and approvals only |
| `06_Weekly_Meetings` | [Open](https://drive.google.com/drive/folders/10ULnOU9pN7O5Bdw0cXajmJZIMFJ7SiNE) | Reviewed pre-reads, minutes, and commitment records |
| `07_Submission_Package` | [Open](https://drive.google.com/drive/folders/14IxkgBxo5fewSKUxoGR-R3mqprBLGPJt) | Ali-approved submission candidates |
| `99_Archive` | [Open](https://drive.google.com/drive/folders/1_pcFuLZ-3M2tmzoihofz4DMYms7B-rHe) | Superseded reviewed working material |

## Literature workbook

[VEGO-AI PhD Literature Workbook v0.1](https://docs.google.com/spreadsheets/d/1tVAM10bxlmL7_8SbgDgN5BRfAR2f5Q4pGvQmx-Ypp4A/edit)
is a native Google Sheet in `03_Literature_Review`.

Verified implementation:

- six tabs: `Papers`, `Search_Log`, `Screening`,
  `Taxonomy_and_Gaps`, `Resources`, and `Controlled_Lists`;
- one paper per row and separate `Authors_Conclusions` and
  `Researcher_Synthesis` columns;
- five native Google Sheets tables with finite dropdown columns;
- six seeded records: four academic/official resource-pack entries, the
  repository baseline publication record, and one modeling candidate awaiting
  independent identity/full-text verification;
- tools such as Label Studio and Argilla are in `Resources`, not research
  evidence;
- spreadsheet locale `en_GB`, timezone `Asia/Jerusalem`;
- search queries are prepared but have not been represented as executed.

## Access state and next gate

The root and workbook are currently owner-only. This intentionally preserves
the plan's Ali-review gate. Before sharing:

1. Ali reviews the exact files and workbook rows;
2. intended supervisors and their roles are confirmed;
3. sharing permissions use the minimum required access;
4. both supervisors' access is tested without exposing controlled data; and
5. the sharing event and result are recorded in the decision/change log.

The supplied source has three separate controls: metadata inventory, ACL /
viewer-only permission, and purpose-specific research authorization. Only the
first was corroborated on 3 August. The other two remain unverified and block
row-level use regardless of folder visibility.
