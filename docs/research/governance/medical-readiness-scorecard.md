# Medical Track Readiness Scorecard

**Assessment date:** 2026-07-30
**Public/funding-facing name:** this track is pursued externally under the name **MediVARIA** — see the [MediVARIA overview](./medivaria-medical-extension-overview.md) for what that document adds. It does not change anything below; still 0/6.
**Overall verdict:** **NO-GO — BLOCKED (0/6 entry gates passed)**
**Permitted work now:** governance documentation, public literature review, proposal design, stakeholder coordination, and metadata-only reconciliation that does not expose medical rows.
**Not permitted:** inspection of a patient/event/encounter row, clinical-note access, medical computation, local-model execution on medical data, a bounded pilot, export, or medical evidence claims.

## Control model

The six gates below are the mandatory **pre-row-level entry gates**. They are sequential and cumulative:

```text
1 Use-case
    -> 2 People
        -> 3 Authorization
            -> 4 Ethics/privacy
                -> 5 Environment
                    -> 6 Protocol
                        -> row-level access may be considered
                        -> downstream integrity control
                        -> bounded pilot control
                        -> disclosure/export control
```

A gate passes only when every required item is verified, current, project-specific, and approved by every named approver. Partial evidence does not produce a partial pass. Passing Gate 6 does not itself authorize a pilot or export; it only completes the entry prerequisites for the separately controlled downstream work.

If the use case, people, data source, authorization, ethics/privacy determination, environment, or protocol changes materially—or an approval expires—that gate and all later entry/downstream controls return to blocked.

## Six mandatory entry gates

| Gate | Mandatory decision | Required evidence | Required approver(s) | Evidence currently available | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | **Use-case** | Named clinical workflow and decision point; problem owner; affected unit/service; intended user; minimum input concepts; intended output and action; current baseline; non-goals; measurable technical and clinical success/failure criteria | Clinical problem owner; supervisor/PI; lead researcher | Meeting-derived themes and a blank Clalit request template exist, but no approved workflow, problem owner, unit, input/output contract, or success criteria exist | **BLOCKED (open)** |
| 2 | **People** | Named clinician/domain expert; named data custodian; named privacy/ethics owner; named VDI administrator; supervisor/PI; methods reviewer; responsibilities, availability, escalation route, and conflicts recorded | Supervisor/PI; clinical problem owner; institutional/data-owner representative | Roles are described generically; the required people, availability, and responsibility acceptance are not recorded | **BLOCKED (open)** |
| 3 | **Authorization** | For each researcher: identity, exact selected data source, exact approved project/purpose, individual access basis, training/DUA or partner authorization, start/expiry, least privilege, and confirmation that access/data will not be shared | Data custodian or licensing/data-access authority; institutional research owner; lead researcher | Drive metadata proves file visibility only. Individual MIMIC/Clalit permission for the stated project is unverified | **BLOCKED (open)** |
| 4 | **Ethics/privacy** | Written determination separately covering MIMIC and Clalit as applicable; project purpose; patient/record-level processing; derivatives; linkage; retention/deletion; publication and examples; disclosure/export; incident response; consent/waiver/IRB basis; restrictions and review/expiry date | Named privacy/ethics owner; data custodian; supervisor/PI | No project-specific written determination covering the required lifecycle is attached | **BLOCKED (open)** |
| 5 | **Environment** | Approved restricted VDI; storage and compute location; named accounts; least privilege; encryption; audit logging; network/clipboard/drive-redirection controls; export quarantine; backup/retention/deletion; incident path; approved dependencies; offline/no-telemetry tool list; explicit local-LLM approval or no-LLM decision; egress test | Named VDI administrator; IT/security owner; data custodian/privacy owner | A restricted environment is expected, but its owner, configuration, audit evidence, tool allowlist, and no-egress/no-telemetry proof are absent | **BLOCKED (open)** |
| 6 | **Protocol** | Approved cohort and unit of analysis; inclusion/exclusion; index and observation windows; outcome and comparator; case/activity/timestamp rules where process mining applies; missingness/duplicates/censoring; label and temporal leakage controls; statistical analysis, uncertainty, sensitivity, subgroup/bias checks, stop criteria, and supervisor approval | Supervisor/PI; named clinician/domain expert; methods reviewer; lead researcher | Meeting requirements and templates exist, but no complete, versioned, approved medical protocol exists | **BLOCKED (open)** |

## Entry-gate evidence checklist

### Gate 1 — Use-case

- [ ] Clinical workflow, setting, unit/service, and exact decision point are named.
- [ ] Clinical problem owner and intended users confirm the problem.
- [ ] Minimum input concepts are defined without requesting real rows.
- [ ] Intended output, user action, and integration point are defined.
- [ ] Current workflow/baseline and explicit non-goals are recorded.
- [ ] Technical, clinical, safety, feasibility, and failure criteria are measurable.
- [ ] Plan A/Plan B and an objective fallback trigger are aligned with the September proposal boundary.

### Gate 2 — People

- [ ] Clinician/domain expert is named and accepts the validation responsibility.
- [ ] Data custodian is named and accepts access, retention, and export responsibility.
- [ ] Privacy/ethics owner is named and accepts the determination responsibility.
- [ ] VDI administrator and IT/security owner are named.
- [ ] Supervisor/PI, lead researcher, and methods reviewer are named.
- [ ] Availability, substitutes, decision rights, escalation route, and conflicts are recorded.

### Gate 3 — Authorization

- [ ] Every researcher has individual permission for the selected data and the exact stated project.
- [ ] MIMIC access evidence includes current credentialing/training/DUA where applicable.
- [ ] Clalit access evidence names the data owner, approved purpose, and permitted fields/system.
- [ ] Access start, expiry, least-privilege scope, and revocation mechanism are recorded.
- [ ] No shared credentials, inherited access, or shared downloaded dataset is treated as permission.
- [ ] The apparent MIMIC files in shared Drive receive a written data-custodian disposition; no ad hoc cleanup is performed.

### Gate 4 — Ethics/privacy

- [ ] Written determination exists for MIMIC use and derivatives.
- [ ] Written determination exists for Clalit use and derivatives, if applicable.
- [ ] Patient/record-level processing, linkage, and minimum-necessary use are addressed.
- [ ] Retention, deletion, backups, derived artifacts, and model/log handling are addressed.
- [ ] Publication, examples, aggregate thresholds, and disclosure/export review are addressed.
- [ ] Incident reporting, contact, containment, and notification are addressed.
- [ ] Consent, waiver, IRB/privacy basis, restrictions, expiry, and re-review triggers are explicit.

### Gate 5 — Environment

- [ ] VDI, storage, compute, owner, and named accounts are approved.
- [ ] Encryption, audit logging, least privilege, backups, retention, and deletion are evidenced.
- [ ] Browser, network, clipboard, local-drive, shared-Drive, repository, email, and print/export controls are tested.
- [ ] Export quarantine and incident procedures are tested.
- [ ] Tools and dependencies are versioned, allowlisted, offline-capable, and no-telemetry.
- [ ] Any local LLM has approved weights/runtime, no API, no telemetry/update path, and no external log/cache path; otherwise the decision is `No LLM`.
- [ ] Secrets use an approved secret store and never enter code, documents, or prompts.

### Gate 6 — Protocol

- [ ] Main question and exactly three subquestions are approved and mapped to method, evidence, artifact, and success/failure criterion.
- [ ] Cohort, unit of analysis, inclusion/exclusion, index event, windows, outcomes, comparator, and sample-size rationale are defined.
- [ ] Case, activity, timestamp, event-ordering, duplicate, and trace rules are defined for process mining.
- [ ] Missingness, censoring, class imbalance, and subgroup/fairness risks are specified.
- [ ] Label leakage and temporal leakage controls are pre-specified.
- [ ] Statistical methods, metrics, uncertainty, multiple comparisons, sensitivity checks, validation, and stop criteria are pre-specified.
- [ ] Clinician, methods reviewer, and supervisor approve the exact version.

## Downstream controls after all six entry gates pass

These controls are mandatory but are **not substitutes for the six entry gates**. None may start while any entry gate is blocked.

### D1 — Data integrity and provenance

Before a pilot:

- reconcile the expected MIMIC-III v1.4 26-table manifest against the 25 observed CSVs;
- document the `NOTEEVENTS` decision without silently reacquiring it;
- verify official checksums, local hashes, file sizes, schema, VDI-computed row counts, acquisition record, and named licensee;
- classify `results.xlsx`, field summaries, XES, notebook, figures, and `index.xlsx` as authoritative, superseded, historical, or invalid;
- establish source, code, environment, parameter, run, and parent-artifact provenance.

**Current status:** **BLOCKED — not started; entry gates 1–6 are blocked.**

### D2 — Bounded pilot and scientific validation

After D1 passes:

- execute only the smallest pre-approved extract and tables/time window;
- use locked code, environment, source hashes, configuration, and run ID;
- perform the protocol's data-quality, missingness, leakage, bias, baseline, uncertainty, sensitivity, and stop checks;
- obtain independent methods review and named clinical interpretation;
- classify every finding as verified, preliminary, proposal, open question, or unavailable.

**Current status:** **BLOCKED — not started; D1 and entry gates are blocked.**

### D3 — Disclosure, export, and evidence acceptance

After D2 passes, for each exact artifact:

- complete the derived-artifact provenance record;
- verify absence of rows, identifiers, notes, rare-case excerpts, screenshots, reversible encodings, and unsafe small cells;
- apply approved aggregation/suppression rules;
- approve the exact destination, audience, retention, disposal, and file hash;
- obtain data-custodian/privacy, clinical/methods, and supervisor approval for the artifact and exact claim wording.

**Current status:** **BLOCKED — no artifact is approved for export or medical claims.**

## Current blocker register

| ID | Entry/downstream control | Blocker | Next evidence-producing action | Owner | State |
| --- | --- | --- | --- | --- | --- |
| MR-01 | Gate 1 — Use-case | Clinical workflow, problem owner, unit, input/output, and success are not approved | Complete the Clalit/MIMIC use-case section and obtain clinical problem-owner and supervisor approval | Lead researcher + clinical problem owner | Open |
| MR-02 | Gate 2 — People | Required accountable people are unnamed | Name clinician, custodian, privacy/ethics owner, VDI admin, methods reviewer, and escalation path | Supervisor/PI + institutional owner | Open |
| MR-03 | Gate 3 — Authorization | Individual project-specific MIMIC/Clalit authority is unknown | Verify each researcher's exact permission, training/DUA or partner approval, scope, and expiry | Data custodian + lead researcher | Open |
| MR-04 | Gate 4 — Ethics/privacy | Lifecycle determination is absent | Obtain written MIMIC/Clalit determination covering derivatives, retention, publication, and incidents | Privacy/ethics owner + data custodian | Open |
| MR-05 | Gate 5 — Environment | VDI, audit logging, egress controls, and offline/no-telemetry tools are unproved | Produce approved environment/control evidence and tool allowlist | VDI administrator + IT/security | Open |
| MR-06 | Gate 6 — Protocol | Cohort/outcome/process/statistical protocol is not approved | Complete and version the protocol; obtain clinician, methods, and supervisor approval | Lead researcher + reviewers | Open |
| MR-D1 | D1 — Integrity | Dataset is incomplete/unverified; existing artifacts lack provenance | After Gates 1–6, reconcile 25 CSVs against the official 26-table release inside the VDI | Authorized analyst + data custodian | Blocked |
| MR-D2 | D2 — Pilot | No authorized, reproducible bounded pilot exists | After D1, run only the approved minimum pilot and review it | Lead researcher + clinician + methods reviewer | Blocked |
| MR-D3 | D3 — Export | No disclosure/export package exists | After D2, complete artifact provenance and obtain claim/export approvals | Privacy/data custodian + supervisor | Blocked |

## Authoritative external controls

- [MIMIC-III Clinical Database v1.4](https://physionet.org/content/mimiciii/1.4/)
- [PhysioNet credentialing and reuse FAQ](https://physionet.org/about/faqs/)
- [PhysioNet Credentialed Health Data License 1.5.0](https://physionet.org/about/licenses/physionet-credentialed-health-data-license-150/)
- [PhysioNet LLM and online-services guidance](https://physionet.org/news/post/llm-responsible-use/)
