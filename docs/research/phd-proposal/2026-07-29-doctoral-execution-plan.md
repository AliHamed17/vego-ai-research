# Doctoral Execution Plan After the 29 July 2026 Supervisor Call

Date: 29 July 2026
Working-plan version: 0.1
Owner: Ali
Decision authorities: Iris and Arnon for research direction; the university and relevant data/ethics authorities for their respective formal approvals
Status: **provisional, evidence-linked execution plan**

## 1. Purpose and completion definition

This plan converts the July 29 requirements into a controlled path from the current VEGO-AI evidence base to a supervisor-ready doctoral proposal. It covers research architecture, proposal writing, literature review, study design, evidence generation, medical-route feasibility, governance, resources, weekly execution, and candidacy administration.

The planning package is complete when:

1. one umbrella research question and exactly three subquestions are approved or corrected by the supervisors;
2. each subquestion maps to a study, method, evidence source, and research artifact;
3. the proposal contains the six required sections and an explicit novelty, doctoral-scale, feasibility, resources, risk, and schedule argument;
4. Plan A and Plan B share the same research-question spine and the fallback remains independently completable;
5. the literature matrix is operating as a living evidence base rather than a collection of isolated summaries;
6. the September draft and early-October working target are reconciled with verified university dates; and
7. no claim exceeds the available evidence.

Primary requirement sources:

- [`../meetings/2026-07-29-iris-requirements-register.md`](../meetings/2026-07-29-iris-requirements-register.md)
- [`../meetings/2026-07-29-iris-supervisor-action-register.md`](../meetings/2026-07-29-iris-supervisor-action-register.md)
- [`../meetings/2026-07-29-iris-supervisor-call-report.md`](../meetings/2026-07-29-iris-supervisor-call-report.md)

## 2. Non-negotiable boundaries

| Boundary | Operational rule |
| --- | --- |
| Research hierarchy | Maintain one umbrella question and exactly three subquestions. Earlier five-question and six-question sets become supporting experimental questions, constructs, or transfer factors. |
| Domain neutrality | Every question must remain answerable in the software/modeling baseline. Medicine may strengthen transfer evidence but cannot determine PhD viability. |
| Current evidence | Describe existing results as software/modeling mechanism, traceability, governance, or evaluation-readiness evidence. |
| EXP-005 | The current state is 0/24 adjudicated generalization-safe labels and 0/2 independent reviewer returns. Accuracy, macro-F1, generalization, effort, and superiority remain unavailable. |
| Medical claims | No clinical-performance, clinical-safety, clinician-acceptance, or medical-generalization claim exists. |
| Data | Do not place patient data in the repository. Preserve any shared source area as read-only and use a separately authorized working environment. |
| LLM use | No restricted medical data may be processed by a commercial or online-connected LLM. Approved local/offline tooling is a later institutional decision. |
| Human authority | Experts supply judgment; AI or synthetic labels never substitute for independent human ground truth. |
| Transcript | The July 29 record is machine-derived and not fully diarized. Use paraphrase with confidence and never present unreviewed text as a direct quotation. |
| External process | The weekly master event is verified as accepted by Ali, Iris, and Arnon: Wednesday 09:00–10:00 Asia/Jerusalem through the 2026-10-07 occurrence. Do not treat Drive receipt, partner access, ethics clearance, reviewer count, or university dates as confirmed without external evidence. |

## 3. Working research architecture

### Umbrella research question

How can reusable human judgment be captured, governed, and reused in agentic AI assessment of domain-specific artifacts and processes to support auditable, reliable, and transferable human–AI co-reasoning?

### Three subquestions

| ID | Subquestion | Construct under study |
| --- | --- | --- |
| SQ1 — Selective intervention | When and how should an agentic assessment system request human judgment so that important uncertainties are addressed without unnecessary expert burden? | Intervention eligibility, timing, dosage, routing, and burden |
| SQ2 — Governed knowledge reuse | How should expert judgments be represented, validated, reconciled, and stored so they can be reused transparently without unsafe generalization or loss of human authority? | Judgment representation, validation, reconciliation, provenance, authority, and safe reuse |
| SQ3 — Evaluation and transfer | To what extent does the resulting framework improve assessment quality, consistency, traceability, and expert effort across domains, first in software/modeling and, when governance and access permit, in healthcare? | Empirical effects, limitations, and cross-domain transfer |

> **Update note (added after the 2026-08-05 supervisor call).** The umbrella RQ and SQ1–SQ3 wording above is the correct historical record of what this plan carried on 29 July 2026 and is left unchanged here. On 2026-08-05, a supervisor call with Iris Reinhartz-Berger and Arnon Sturm refined this wording live, in conversation. That refinement is machine-transcribed and recorded, with full evidence and caveats, in [`../meetings/2026-08-05-supervisor-meeting.md`](../meetings/2026-08-05-supervisor-meeting.md) (items E5–E10) and [`../meetings/2026-08-05-supervisor-provenance-manifest.md`](../meetings/2026-08-05-supervisor-provenance-manifest.md).
>
> The resulting new canonical working wording is **provisional**, not supervisor-approved — decisions D-RQ-01 (umbrella RQ wording) and D-RQ-02 (SQ1–3 wording) remain formally "Pending" in [`2026-08-05-rq-decision-pack.md`](./2026-08-05-rq-decision-pack.md) until Ali verifies the exact text against his own saved working draft from the call and a supervisor decision is logged. It is reproduced here for traceability only, not as a replacement for the text above:
>
> - **U-RQ:** How can human judgment be captured, governed, and used to support agentic-AI-driven variability exploration in guideline operationalization scenarios, enabling reliable human–AI co-reasoning?
> - **SQ1 — Selective intervention:** When and how, in variability exploration scenarios, should an agentic assessment system request human judgment so that important uncertainties are addressed without unnecessary expert burden?
> - **SQ2 — Governed knowledge reuse:** How should expert judgment — including the system's core reasoning — be represented, validated, reconciled, and stored so it can be reused transparently without unsafe generalization or loss of human authority?
> - **SQ3 — Evaluation and transfer:** How can expert judgment be reused and transferred across different guideline-operationalization contexts without unsafe generalization or loss of human authority, first in software/modeling and, when governance and access permit, in healthcare?

### Three-study mapping

| Study | RQ | Method | Evidence/data | Primary artifacts | Exit evidence |
| --- | --- | --- | --- | --- | --- |
| Study 1 — Intervention architecture | SQ1 | Design-science construction and requirements-to-artifact evaluation; controlled event, uncertainty, priority, dosage, routing, escalation, and burden scenarios | Existing VEGO-AI/H-layer event catalogs, review-queue specifications, tests, controlled fixtures, and supervisor decisions | Domain-neutral listener/triage/routing architecture; intervention taxonomy; dosage and escalation policy; burden model; traceability matrix | Every intervention requirement maps to an inspectable artifact and validation; no quality or workload-improvement claim is inferred from readiness |
| Study 2 — Judgment lifecycle | SQ2 | Design-science construction plus contract, provenance, source-validation, conflict, reconciliation, authority, storage, retrieval, and unsafe-reuse analysis | Existing feedback/memory specifications, schemas, tests, controlled conflict and verification fixtures, and supervisor decisions | Judgment schema; source-validation and reconciliation protocol; provenance/authority model; safe storage/retrieval/reuse policy; bounded-verification protocol | Every lifecycle and governance requirement maps to an inspectable artifact and validation; transparent reuse does not imply beneficial effect |
| Study 3 — Evaluation and transfer | SQ3 | Blinded independent labeling, adjudication, paired controlled comparison, workload study, error/validity analysis, and comparative cross-domain case study | Frozen software/modeling baseline; 24-row independent-evidence set; later approved reviewer returns; Plan A approved healthcare material or Plan B second software/modeling setting | Preregistered evaluation protocol; adjudicated gold set; empirical result/validity package; transfer taxonomy; adaptation and governance profile | At least 20 safe adjudicated labels for quantitative eligibility; negative/null results accepted; healthcare and broader transfer claims require their own gated evidence |

The detailed wording decision is in [`2026-08-05-rq-decision-pack.md`](./2026-08-05-rq-decision-pack.md). Earlier questions are preserved through [`legacy-rq-crosswalk.md`](./legacy-rq-crosswalk.md).

## 4. Plan A / Plan B decision architecture

### Common core

Both plans must complete:

- Study 1 intervention architecture in the software/modeling context;
- Study 2 governed judgment lifecycle in the software/modeling context;
- Study 3 evaluation of the complete framework first in software/modeling through independent human evidence and explicit claim gates;
- a literature synthesis spanning human-in/on-the-loop AI, multi-agent human collaboration, expert-knowledge capture, reusable memory, anti-sycophancy/source-grounded verification, intervention dosage, design science, and transfer;
- a domain-neutral artifact and governance model; and
- a documented second-setting transfer comparison within Study 3.

### Plan A — conditional medical transfer

Study 3 extends from its required software/modeling evaluation into a medical setting only when every entry gate has written evidence:

| Gate | Required evidence | Owner |
| --- | --- | --- |
| G1 use-case | Precise clinical workflow, problem owner, unit of analysis, intended input/output, baseline, non-goals, and measurable success/failure criteria | Supervisors + Ali + clinical owner |
| G2 people | Named clinician/domain expert, data custodian, privacy/ethics owner, VDI administrator, supervisor, and methods reviewer, with responsibilities and availability | Supervisors + partner/institution |
| G3 authorization | Individual project-specific permission for every researcher, exact data and purpose, training/DUA or partner authority, least privilege, and expiry | Data custodian/partner |
| G4 ethics/privacy | Written determination covering the selected data, derivatives, retention, publication, disclosure, and incident handling | Ethics/privacy owner + data custodian |
| G5 environment | Approved VDI, storage, compute, audit logging, egress controls, and offline/no-telemetry toolchain or explicit no-LLM decision | VDI/IT/security + data custodian |
| G6 protocol | Approved cohort, inclusion/exclusion, outcome, case/activity/timestamp rules, missingness, leakage controls, statistics, stop rules, and clinical/method/supervisor review | Ali + supervisors + clinical/method reviewers |

MIMIC may support a bounded schema/data-shape familiarization note, but it is not selected as the doctoral dataset by this plan. MediVARIA is a candidate transfer vehicle described in [`../medivaria/medivaria-study-plan.md`](../medivaria/medivaria-study-plan.md); its supervisor endorsement, partner, data, and clinical evaluation remain pending.

### Plan B — guaranteed non-medical completion

If any Plan A gate is absent by the agreed decision date, Study 3 proceeds using an approved second software/modeling setting. Candidate variations include:

- a new diagram family or modeling task;
- a second annotated dataset or run;
- an external course/institution;
- a different reviewer panel or expertise profile; or
- a longitudinal reuse setting across iterations.

Plan B must preserve construct comparability, independent human evidence, leakage control, and the same SQ3 evaluation-and-transfer measures.

### Fallback trigger

Proposed trigger for supervisor decision: **if any of the six mandatory entry gates G1–G6 lacks a documented owner, evidence path, or feasible completion date by 26 August 2026, the September proposal is written with Plan B as the committed execution path and Plan A as a contingent extension.** This is a proposed control date, not a meeting-approved deadline.

## 5. Workstreams

### WS1 — Research-question and contribution lock

Actions:

1. Review the recommended wording and two variants.
2. Confirm that SQ1–SQ3 are collectively exhaustive and non-overlapping enough for three studies.
3. Confirm the novelty unit: the linked intervention architecture, governed knowledge lifecycle, and evidence-controlled evaluation/transfer—not memory, routing, or a medical application in isolation.
4. Freeze a versioned RQ set after supervisor read-back.

Deliverables:

- [`2026-08-05-rq-decision-pack.md`](./2026-08-05-rq-decision-pack.md)
- [`legacy-rq-crosswalk.md`](./legacy-rq-crosswalk.md)
- decision record with outcome, corrections, owner, and date

Acceptance:

- one umbrella RQ and exactly three SQs;
- every SQ has a method and artifact;
- every SQ is answerable under Plan B;
- terminology is defined consistently across proposal, literature matrix, and studies.

### WS2 — Proposal drafting

Build the six required sections in [`proposal-v0.1.md`](./proposal-v0.1.md):

1. introduction and motivation;
2. literature review and gap;
3. research questions;
4. methodology and artifacts;
5. preliminary results; and
6. work plan and timeline.

Each iteration must also contain:

- explicit novelty and contribution;
- doctoral-scale argument based on three coherent studies;
- feasibility and resource analysis;
- Plan A/Plan B and risks;
- evidence/claim table; and
- unresolved decisions rather than invented resolutions.

### WS3 — Living literature evidence base

Use the existing taxonomy in [`../literature-review-taxonomy.md`](../literature-review-taxonomy.md) as the starting scope. The working spreadsheet must use one paper per row and separate:

1. bibliographic metadata;
2. authors’ method, data, artifacts, results, limitations, and conclusions; and
3. Ali’s synthesis, RQ/study mapping, gap relevance, transfer relevance, and confidence.

Required process fields:

- source/database and query;
- screening state and exclusion reason;
- peer-review status;
- access link/identifier;
- study design and sample;
- claimed contribution;
- threats/limitations;
- author conclusion;
- researcher interpretation;
- SQ1/SQ2/SQ3 and Study 1/2/3 mapping;
- Plan A/Plan B relevance; and
- verification status.

The next checkpoint requires a valid template and available seed papers; the meeting set no minimum paper count. A later systematic or scoping-review protocol, search strings, databases, date range, inclusion/exclusion criteria, quality appraisal, and deduplication method require supervisor/method-course alignment.

### WS4 — Current evidence and EXP-005

Treat [`../independent-evidence/README.md`](../independent-evidence/README.md) as the current empirical boundary:

- 24 candidate rows;
- 0/2 independent reviewer returns;
- 0/24 adjudicated safe labels;
- performance measures not computable;
- calibration release authorized, evaluation release not yet authorized.

Execution remains human-gated:

1. obtain two calibration returns;
2. freeze instructions through a human decision;
3. release blinded evaluation only after the existing gate;
4. preserve immutable reviewer returns;
5. adjudicate through the authorized human process;
6. freeze the gold set;
7. run development evaluation;
8. preregister and freeze any candidate change before opening the holdout;
9. treat the holdout as a pilot; and
10. require a second setting for generalization.

No proposal milestone depends on obtaining a positive result. Negative and null results are valid.

### WS5 — Bounded medical familiarization

Purpose: keep the research questions realistic without turning proposal drafting into medical-domain training.

Status: **the initial bounded metadata/schema audit was documented on 30 July 2026; no patient row was inspected. The intended maximum was four hours, but start/end or elapsed-time evidence was not recorded, so four-hour completion is not claimed.**

- four hours maximum for the initial tranche;
- metadata, file manifest, index, schema, and process-mining feasibility questions only;
- no patient, event, encounter, note, or other raw-row sample;
- no full-dataset download, model training, patient-level inference, or clinical interpretation;
- stop immediately if access, license, privacy, or purpose is unclear.

Output: [`../governance/mimic-metadata-audit-2026-07-30.md`](../governance/mimic-metadata-audit-2026-07-30.md), recording 25 observed CSVs, 39.65 GiB, missing `NOTEEVENTS`, workbook/provenance gaps, and unresolved questions. The audit does not select the final dataset or establish medical feasibility.

### WS6 — Medical/partner feasibility and governance

Create a decision dossier, not a technical implementation:

- precise Clalit or alternative partner request;
- candidate clinical use case;
- expert roles and expected hours;
- required variables/data structures;
- approvals and contracts;
- allowed storage and compute;
- local/offline tool constraints;
- data minimization and retention;
- researcher access and audit logging;
- no-partner fallback; and
- earliest feasible decision date.

No restricted data, partner negotiation detail, personal identifier, credential, or patient record belongs in tracked files.

### WS7 — Resources and capability readiness

| Resource | Current status | Gap/action |
| --- | --- | --- |
| VEGO-AI baseline and H-layer artifacts | Existing repository evidence | Freeze references and distinguish implementation from evaluation evidence |
| Independent-evidence protocol | Calibration-ready; human returns absent | Complete human process without synthetic substitution |
| Literature taxonomy and resource pack | Existing seed structure | Build living matrix and verified corpus |
| Penina course work | Reusable in proposal | Confirm course deliverable/date and trace reused material |
| Supervisors | Research-direction authorities | Weekly task/decision cadence and explicit read-back |
| Independent reviewers/adjudicator | Defined by accepted protocol | Secure participation and returns |
| Shared MIMIC/source material | Sharing discussed/reported | Confirm receipt, authorization, read-only behavior, and permitted use |
| Medical experts/partner | Unresolved | Identify roles, availability, use case, and approvals |
| Restricted compute/local LLM | Unresolved | Institutionally approve only when Plan A reaches that stage |
| University process | Conversational guidance only | Verify formal deadlines, reviewer count, nomination, and committee rules |
| Working Drive/folder | Partially arranged in the call | Confirm access; separate immutable source and editable work areas |

### WS8 — Weekly governance and reporting

For each short weekly meeting:

1. circulate a short pre-read;
2. show completed artifacts and evidence links;
3. state blockers and decisions needed;
4. record each decision as approved, corrected, deferred, or rejected;
5. assign one primary next task, owner, and acceptance check; and
6. update the proposal, action register, risk register, and literature matrix after the meeting.

The recurring master event is now verified as accepted by Ali, Iris, and Arnon: Wednesday 09:00–10:00 Asia/Jerusalem through the 2026-10-07 occurrence. This verifies logistics only; it does not approve any research decision.

### WS9 — Candidacy administration

Verify through university sources:

- formal proposal deadline;
- candidacy timing;
- document/template/page requirements;
- reviewer count and eligibility;
- nomination and conflict-of-interest process;
- committee composition and approval route;
- presentation length and format; and
- required ethics/data-management attachments.

Prepare the short candidacy presentation only after these requirements are verified. It should orient reviewers, show progress, and focus on decisions rather than repeat the full proposal.

## 6. Provisional milestone plan

All research-deliverable dates below are internal controls pending university and supervisor confirmation. The weekly calendar cadence itself is verified as stated in WS8.

| Date | Milestone | Acceptance |
| --- | --- | --- |
| 5 Aug 2026 | Supervisor RQ decision checkpoint | Decision or precise correction on umbrella RQ, three SQs, study mapping, Plan A/B interpretation, and immediate literature scope |
| 12 Aug 2026 | Architecture/literature baseline and proposal `v0.2` | Search protocol and first screening pass, core taxonomy coverage, Penina outline/reuse map, and Clalit request delivered |
| 19 Aug 2026 | Critical synthesis and study-design closure | Gap matrix, resource/RACI, preliminary-results register, and Study 1–3 methods, metrics, validity threats, and publication outputs drafted |
| 26 Aug 2026 | Proposal `v0.3`, architecture freeze, and Plan A review | Approved-or-revised RQ/study architecture frozen; G1–G6 reviewed; committed September path selected under the fallback rule |
| 2 Sep 2026 | Core proposal sections complete | Introduction, problem, gap, RQs, and methods internally complete |
| 9 Sep 2026 | Evidence and claim-boundary section complete | Preliminary evidence carries five-state labels and no unsupported claims |
| 16 Sep 2026 | Full developed draft `v0.7` | Resources, ethics, risks, timeline, and all substantive sections complete |
| 23 Sep 2026 | Comments/process resolution | Supervisor comments resolved; formatting and official process verified |
| 30 Sep 2026 | Submission candidate `v1.0` | References, appendices, evidence consistency, and cross-document traceability validated |
| 7 Oct 2026 | Final buffer | Final approval, submission, or candidacy-presentation package, subject to formal rules |

Research and writing continue while candidacy/reviewer scheduling proceeds.

## 7. Risk and dependency register

| Risk | Trigger | Control | Owner |
| --- | --- | --- | --- |
| Medical route blocks PhD | Expert/data/access gate lacks proof | Common core + Plan B; 26 Aug proposed fallback decision | Ali + supervisors |
| Medical familiarization consumes proposal time | Moves beyond the bounded metadata/schema scope, lacks a timing record, or requires deep domain study | Stop rule; record start/end for any future time box and preserve unanswered questions for experts | Ali |
| Evidence overclaim | Quantitative/medical wording without eligible evidence | 0/24 boundary; claim/evidence review; explicit “not yet computable” | Ali |
| Privacy/tooling breach | Restricted material considered for online tooling/export | Approved environment and local/offline tooling gate; no data in repo | Institution + team |
| Literature becomes descriptive | Paper-by-paper summaries without synthesis | Grouping, gap-to-contribution fields, monthly synthesis memo | Ali |
| RQ/study drift | New question or artifact lacks canonical mapping | Crosswalk and change decision before adoption | Ali + supervisors |
| Human bottleneck | Reviewer, adjudicator, or clinician unavailable | Non-blocking documentation work; Plan B; explicit due dates | Ali + supervisors |
| Schedule based on hearsay | Formal date/process remains unverified | University verification workstream | Ali + supervisors |
| Source corruption | Shared source material edited | Read-only source area; separate working directory | Ali |
| Transcript misunderstanding | Machine text treated as authoritative quotation | Paraphrase only; human bilingual review for disputed requirements | Ali + supervisors |

## 8. Supervisor decisions required

The next decision checkpoint should record:

1. preferred wording option for the umbrella RQ;
2. confirmation or correction of SQ1–SQ3;
3. approval or correction of the three-study mapping;
4. whether Plan A means conditional medical transfer and Plan B means non-medical transfer;
5. whether the 26 August fallback control date is acceptable;
6. literature-review scope and intended review method;
7. permitted scope of the MIMIC familiarization note;
8. owners for medical expert/data/governance checks;
9. the next primary task for the verified weekly cadence; and
10. the owner and source for formal university-process verification.

Use [`2026-08-05-rq-decision-pack.md`](./2026-08-05-rq-decision-pack.md) for the read-back.

## 9. Quality checks before each proposal release

- one umbrella RQ and exactly three SQs appear;
- each SQ maps to one primary study;
- each study lists method, data/evidence, artifact, gate, and validity threats;
- current evidence is distinguished from planned evidence;
- 0/24 is current wherever EXP-005 is summarized;
- no medical result or approval is implied;
- Plan B remains fully executable;
- authors’ conclusions are separated from researcher interpretation;
- all cited repository paths resolve;
- dates are labeled formal or provisional;
- direct quotations from the machine transcript are absent; and
- supervisor changes are recorded as decisions rather than silently rewritten.
