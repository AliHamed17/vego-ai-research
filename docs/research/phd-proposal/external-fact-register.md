# External-Fact Register — 29 July Supervisor Call

Status: **Seeded from meeting statements only; most claims remain unverified.**

Last updated: 2026-08-03

This register prevents conversational statements from becoming institutional policy, dataset fact, access evidence, partner commitment, or official scheduling information. Entries are paraphrases, not quotations. The raw recording and transcript remain the evidence for what was discussed; an accountable external source is required to establish whether a statement is true now.

## Verification states

| State | Meaning |
| --- | --- |
| `Unverified meeting statement` | Present in the machine-derived call record; no independent authoritative evidence is linked. |
| `Partially corroborated` | Some part is supported after the call, but the full statement or permission boundary is not established. |
| `Verified after call` | A dated authoritative source or accountable owner confirms the exact fact. |
| `Corrected or contradicted` | An authoritative source supplies different wording or facts; the correction must propagate. |
| `Retired or not applicable` | An approved decision makes the statement irrelevant to the execution route. |

Only `Verified after call`, `Corrected or contradicted`, or `Retired or not applicable` can close a fact that is critical to proposal submission or medical execution.

## Seeded claims

| ID | Meeting-statement claim | Call evidence | Current verification state | Authority/evidence required | Related controls |
| --- | --- | --- | --- | --- | --- |
| EF-01 | The candidacy review may use two examiners, with Arnon potentially one of them. | S-0022–S-0025 | Unverified meeting statement | Graduate Studies or current departmental regulation naming reviewer count and eligibility | R-05; A-14; Q-08 |
| EF-02 | A candidacy examination is required during the first semester. | S-0035–S-0038 | Unverified meeting statement | Current official doctoral/candidacy regulation and applicability to Ali’s program | R-05; A-14; Q-08 |
| EF-03 | Reviewer nomination, acceptance, a reading window of roughly one to one-and-a-half months, and a meeting commonly booked for up to two hours form the review process. | S-0039–S-0045 | Unverified meeting statement | Written current process from Graduate Studies, including timing and meeting format | R-05; A-14; Q-08 |
| EF-04 | The chair determines the committee. | S-0109–S-0110 | Unverified meeting statement | Current departmental authority/process statement | A-14; Q-08 |
| EF-05 | The proposal should be wrapped up before 28 September because the supervisor expects limited feedback availability from 28 September until 11 October. | S-0162–S-0185 | Unverified meeting statement | Iris confirmation of dates and availability; reconcile with official deadline | R-06; R-18; A-12–A-14; Q-08 |
| EF-06 | A more-developed draft is targeted for September and full submission is targeted for early October/pre-October. | S-0496–S-0499; S-0672–S-0681 | Unverified meeting statement; controlled as an internal working target | Iris/Arnon schedule confirmation plus authoritative university deadline | R-18; A-12–A-14; Q-08 |
| EF-07 | Weekly Wednesday meetings at 09:00 were to be scheduled. | S-0522–S-0536; S-0825–S-0828; S-1036–S-1057 | Verified after call for the recurring calendar series; execution discipline remains ongoing | Retain accepted calendar-series evidence and create a record for every actual meeting cycle | R-13; A-06–A-07; Q-07 |
| EF-08 | Medical/Clalit data would be accessed through a VDI rather than transferred to researchers. | S-0844–S-0849; S-0950–S-0955 | Unverified meeting statement | Written data-custodian, privacy, and security determination for the selected project | R-09; R-12; A-09; A-11; Q-05; Q-09 |
| EF-09 | Cloud/online processing is unavailable in the described restricted environment, so any later model use would require approved local/offline operation. | S-0850–S-0878 | Unverified meeting statement | Written institutional model/network policy and approved runtime/model register | R-12; A-11; Q-06 |
| EF-10 | Any granted medical access would be non-transferable and limited to defined research purposes. | S-0880–S-0889 | Unverified meeting statement | Executed authorization/DUA and written purpose, user, retention, export, and publication rules | R-12; A-09; A-11; Q-05; Q-09 |
| EF-11 | Clalit was described as holding information for approximately five million living patients and three million former/deceased patients. | S-0927–S-0933 | Unverified meeting statement; high translation/terminology risk | Current authoritative dataset description from the accountable data owner | R-09; Q-02; Q-09 |
| EF-12 | The described Clalit information includes treatments, tests, diagnoses, and immunization-related records, with some result connectivity incomplete. | S-0935–S-0949 | Unverified meeting statement; high translation/terminology risk | Current schema/data dictionary and custodian clarification | R-09; R-11; Q-02; Q-09 |
| EF-13 | A source folder was being shared with viewer access, and changes should be made only in a separate working folder. | S-0973–S-1014 | Partially corroborated: a 3 August read-only metadata listing matches the controlled source inventory and confirms source/working-location separation; the complete ACL, viewer-only setting, owner authority, and purpose-specific research authorization remain unverified | [Drive boundary verification record](../governance/drive-boundary-verification-2026-08-03.md), plus accountable permission record and named-user authorization/DUA | R-17; A-04–A-05; Q-07 |
| EF-14 | A partner message reported an initial idea and an unclear mechanism that might support retrieval/extraction, with a follow-up meeting proposed. | S-1087–S-1105 | Unverified meeting statement; terminology unresolved | Accountable participant’s written correction, invitation/minutes, mechanism description, and decision | R-09; A-15; Q-09–Q-10 |
| EF-15 | The medical/innovation interaction was moving quickly after the MediVARIA one-pager, and another innovation partner was reportedly involved. | S-1120–S-1147 | Partially corroborated (2026-08-11): the referenced one-pager (`MediVARIA_OnePage_v1.docx`, SHA-256 `70C49DB7...`) was supplied and read; its own metadata shows Iris as last editor (2026-05-05), directly evidencing the document's existence and her involvement — see [MediVARIA overview](../governance/medivaria-medical-extension-overview.md). The "another innovation partner was reportedly involved" half remains unverified; the document itself lists Medical Partner as "TBD — Discussions Ongoing." | Partner identity, role, meeting record, and accountable confirmation | R-09; A-15; Q-02; Q-10 |
| EF-16 | Ali would be included in the continuing partner communication loop. | S-1146–S-1152 | Unverified commitment; no subsequent inclusion evidence linked | Invitation/message/minutes showing Ali included, plus date and next owner | A-15; Q-10 |
| EF-17 | A supplied Drive folder (`iris-arnon-7.8.26`) contains an **EHRSHOT** clinical dataset in OMOP-CDM form, alongside `mimic-iii-1.4`. EHRSHOT is named in no prior control, plan, or decision in this project. | Not from a call — observed by metadata-only directory listing on 2026-08-11; see [supplied-drive inventory](../governance/supplied-drive-inventory-2026-08-11.md) | Unverified: presence is directly observed, but provenance, licence terms, individual project-specific authorization, and intended role in the research are all unestablished. Folder visibility is not authorization. | Written data-custodian statement of source and licence; per-researcher authorization/DUA for this exact project; a supervisor decision on whether EHRSHOT enters the Plan A dataset assumption at all | R-09; R-12; A-09; A-11; Q-02; Q-05; Q-09; G1; G3 |

## Update rule

For each verification event, record the authority, source title, date, stable link or retained evidence path, exact confirmed/corrected wording, reviewer, and affected artifacts. Do not overwrite the meeting-statement wording. If a claim changes, preserve the original row and add the correction to its verification record and the decision/change log.

No patient-row access, partner commitment, official deadline, institutional model approval, or submission claim may rely on an `Unverified meeting statement` or `Partially corroborated` entry.
