# Reusable Human Judgment for Auditable, Reliable, and Transferable Agentic AI Assessment

Proposal version: 0.1
Prepared by: Ali
Date: 30 July 2026
Status: **working draft for supervisor review; research questions, studies, medical route, and dates remain provisional**

## Draft abstract

AI-assisted assessment systems can identify candidate differences, violations, or deviations under structured normative specifications, but their outputs often require expert interpretation. Human review is commonly treated as a one-time correction: the decision may resolve the immediate case while its rationale, provenance, scope, conflicts, and later reuse remain weakly governed. This proposal studies how reusable human judgment can become a first-class, auditable component of human-AI co-reasoning without replacing human authority or permitting unsupported automation.

The proposed doctorate has one umbrella research question and three linked studies. Study 1 develops the intervention architecture: when and how an agentic assessment system should request expert judgment while controlling unnecessary burden. Study 2 develops the governed judgment lifecycle: how judgments are represented, source-validated, reconciled, stored, retrieved, and reused without unsafe generalization or loss of human authority. Study 3 evaluates the complete framework’s effects on assessment quality, consistency, traceability, and expert effort, first in software/modeling and then through a gated transfer setting.

Software engineering/modeling is the evidence-backed baseline and guaranteed execution path. A medical setting is a conditional transfer route that requires domain experts, fit-for-purpose data, access, ethics/privacy approvals, approved infrastructure, and local/offline processing for restricted data. If those conditions do not materialize in time, the same transfer study will use a second software/modeling setting. Existing repository work provides mechanism, traceability, governance, and evaluation-readiness evidence; it does not yet support accuracy, generalization, effort-reduction, superiority, or clinical-performance claims. The current independent-evidence state is 0 of 24 adjudicated generalization-safe labels.

## 1. Introduction and motivation

### 1.1 Problem

Many assessment tasks are governed by structured norms: modeling languages, reference models, guidelines, policies, or other specifications define what is expected, while valid contextual variation means that difference is not automatically error. AI can assist by detecting candidate variability, organizing evidence, and proposing interpretations. The difficult step is deciding when a case requires human judgment and what should happen after that judgment is supplied.

A one-time correction does not by itself create reusable knowledge. For later reuse, the system must preserve:

- the decision and rationale;
- the source evidence available to the expert;
- confidence and scope;
- the identity or role of the human authority without unnecessary personal exposure;
- conflicts and adjudication;
- the relationship to prior and later cases;
- the permitted form of reuse; and
- the evidence required before reuse can affect automated behavior.

The research problem is therefore not merely how to insert a person into an AI pipeline. It is how to create a governed human-judgment lifecycle that remains useful, inspectable, bounded, and empirically testable.

### 1.2 Research aim

The aim is to design and evaluate a domain-neutral framework for governed reuse of human judgment in agentic AI assessment of domain-specific artifacts and processes, and to determine:

1. when and how the system should request human judgment without unnecessary burden;
2. how that judgment should be represented, validated, reconciled, stored, and reused transparently; and
3. to what extent the complete framework improves assessment and transfers across domains.

*Sync note (2026-08-10):* item 3 still paraphrases the pre-2026-08-05 SQ3 framing ("to what extent ...
improves assessment"). The 2026-08-05 working refinement (§3.2, provisional pending `D-RQ-02`) reframes
SQ3 around *how* expert judgment is reused and transferred across guideline-operationalization contexts
without unsafe generalization or loss of human authority, rather than an "extent of improvement" framing.
This numbered list has not been rewritten to match, to avoid guessing at wording beyond what §3.2 states;
it should be revisited once `D-RQ-02` is confirmed.

### 1.3 Candidate novelty

The candidate contribution is the combined lifecycle:

1. observe assessment events;
2. selectively identify a need for human judgment;
3. route a self-contained review request;
4. capture structured feedback;
5. verify feedback against available sources without blindly complying;
6. integrate only under explicit authority and evidence rules;
7. retain reusable judgment with provenance, scope, conflict, and lifecycle controls; and
8. evaluate later reuse without contaminating the reference evidence.

The literature review must test, narrow, or reject this novelty hypothesis. This draft does not assume that the gap is already established.

### 1.4 Doctoral scale

The doctorate is organized as three coherent but independently evaluable studies:

- an intervention-architecture study;
- a governed judgment-lifecycle study; and
- a combined evaluation-and-transfer study.

Together they move from artifact construction, through causal/comparative evaluation, to external-boundary analysis. The MSc/VEGO-AI work supplies preliminary software/modeling artifacts and evaluation infrastructure, not a completed answer to the doctoral program.

### 1.5 Scope

In scope:

- AI-assisted assessment under structured normative specifications;
- selective human intervention;
- structured expert feedback;
- source-grounded verification and bounded interaction;
- provenance, conflict, authority, and lifecycle governance;
- reusable judgment memory and controlled reuse;
- empirical quality/workload/safety trade-offs; and
- cross-domain transfer.

Out of scope unless separately approved and evidenced:

- autonomous clinical decision-making;
- patient-data storage in this repository;
- online/commercial LLM processing of restricted medical data;
- replacement of independent human labels with AI or synthetic labels;
- behavioral changes based only on synthetic trials; and
- claims of clinical performance or safety.

## 2. Literature review and research gap

### 2.1 Review purpose

The review will determine whether and how prior work connects the full governed judgment lifecycle. It will distinguish:

- systems that collect one-time labels or corrections;
- systems that preserve reusable expert knowledge;
- systems that verify or challenge human input;
- systems that change model weights versus inference-time memory or policy;
- systems that evaluate quality but not expert workload;
- systems that measure workload but not decision quality;
- single-domain mechanisms versus demonstrated transfer; and
- advisory reuse versus behavior-changing automation.

The starting taxonomy is in [`../literature-review-taxonomy.md`](../literature-review-taxonomy.md).

### 2.2 Literature groups

| Group | Core questions for extraction | Main proposal mapping |
| --- | --- | --- |
| Human-in/on-the-loop AI | When is the human asked, with what authority, and at what cost? | SQ1 |
| Human-AI collaboration in multi-agent systems | Where does human judgment enter the topology and how are handoffs governed? | SQ1 |
| Expert feedback and knowledge capture | How are rationale, scope, provenance, conflict, and reuse represented? | SQ2 |
| Agent memory and learning from feedback | What changes after feedback and how is unsafe reuse prevented? | SQ2 |
| Anti-sycophancy/source-grounded verification | How can the system question incorrect or conflicting human input while converging? | SQ2 |
| Intervention dosage and workload | When should review be requested, and what quality is gained per expert unit of effort? | SQ1, SQ3 |
| Evaluation of human-AI systems | Which comparison designs and validity controls combine technical and human measures? | SQ3 |
| AI-assisted domain modeling and variability | What assessment task and baseline make the studies concrete? | Preliminary results, Study 3 |
| Design-science research | How are problem, artifact, demonstration, evaluation, and contribution linked? | Overall method |
| Transfer and cross-domain adaptation | How are invariant mechanisms separated from domain-specific representations and controls? | SQ3 |
| Medical guideline/conformance work | What would a conditional medical transfer require and what claims remain unavailable? | Plan A only |

### 2.3 Living literature matrix

One paper will occupy one row. Column groups will remain visibly separated:

1. **Bibliographic:** title, authors, venue, year, identifier/link, publication type.
2. **Authors’ study:** question, method, sample/data, artifact, measures, results, limitations, authors’ conclusions.
3. **Researcher synthesis:** relevance, interpretation, gap contribution, SQ/study mapping, Plan A/B relevance, comparison group, confidence, follow-up.

Authors’ conclusions must not be merged with Ali’s interpretation. The spreadsheet will also record search source/query, screening status, exclusion reason, and verification status.

### 2.4 Provisional gap statement

The current hypothesis is that relevant work is fragmented across selective oversight, feedback capture, explanation, memory, verification, and evaluation. The proposed research asks whether these can be combined into a governed reusable-judgment lifecycle and whether its policies and transfer limits can be demonstrated empirically.

This statement remains provisional until the literature matrix supports:

- a transparent search and screening process;
- comparison of closely related systems;
- evidence that the proposed combination is not already established;
- a clear distinction between architectural novelty and empirical novelty; and
- a gap-to-contribution table.

## 3. Research questions

> **2026-08-10 migration note:** the umbrella research question and SQ1–SQ3 below were refined live
> during the 2026-08-05 supervisor call (Iris Reinhartz-Berger and Arnon Sturm), updating the
> ~2026-07-30/08-01 working draft recorded in [`2026-08-05-rq-decision-pack.md`](./2026-08-05-rq-decision-pack.md).
> **This wording is provisional — pending formal `D-RQ-01`/`D-RQ-02` sign-off**; both decisions remain
> `Pending` in that pack. See [`../meetings/2026-08-05-supervisor-meeting.md`](../meetings/2026-08-05-supervisor-meeting.md)
> (items E5–E10) for the machine-derived evidence and [`../meetings/2026-08-05-supervisor-provenance-manifest.md`](../meetings/2026-08-05-supervisor-provenance-manifest.md)
> for source provenance and caveats. The exact text still needs to be checked against Ali's own saved
> working draft from the call before it is treated as final.

### 3.1 Umbrella research question

**How can human judgment be captured, governed, and used to support agentic-AI-driven variability exploration in guideline operationalization scenarios, enabling reliable human–AI co-reasoning?**

### 3.2 Exactly three subquestions

**SQ1 — Selective intervention:** When and how, in variability exploration scenarios, should an agentic assessment system request human judgment so that important uncertainties are addressed without unnecessary expert burden?

**SQ2 — Governed knowledge reuse:** How should expert judgment — including the system's core reasoning — be represented, validated, reconciled, and stored so it can be reused transparently without unsafe generalization or loss of human authority?

**SQ3 — Evaluation and transfer:** How can expert judgment be reused and transferred across different guideline-operationalization contexts without unsafe generalization or loss of human authority, first in software/modeling and, when governance and access permit, in healthcare?

### 3.3 Internal coherence

| Question | Input | Output | Dependency |
| --- | --- | --- | --- |
| SQ1 | Agent events, uncertainties, importance criteria, review roles, and burden constraints | Inspectable intervention architecture and request policy | Determines which judgments enter the lifecycle |
| SQ2 | Study 1 review requests, expert judgments, sources, conflicts, authority, and reuse constraints | Inspectable governed knowledge lifecycle | Produces the complete framework to be evaluated |
| SQ3 | Studies 1–2 framework, frozen baseline, independent human evidence, and second-setting constraints | Effects, failure modes, workload evidence, transfer limits, and adaptations | Tests whether and where the claimed contribution is supported |

Alternative wording and the requested supervisor decisions are in [`2026-08-05-rq-decision-pack.md`](./2026-08-05-rq-decision-pack.md). Earlier questions are mapped in [`legacy-rq-crosswalk.md`](./legacy-rq-crosswalk.md).

## 4. Research methodology and artifacts

### 4.1 Overall methodology

The program uses design science with mixed-method empirical evaluation:

1. identify when human judgment should be requested and construct the intervention architecture;
2. construct the governed representation, validation, reconciliation, storage, and reuse lifecycle;
3. demonstrate both mechanism layers through traceable controlled scenarios;
4. evaluate the complete framework against independent human reference and workload evidence; and
5. test transfer through a comparative second setting.

The framework and its evaluation remain separate. Readiness, conformance, or observability is not performance evidence.

### 4.2 Study 1 — Intervention architecture

**Aim:** answer SQ1.

**Method:**

- consolidate intervention requirements from supervisor records and literature;
- define the observable event, uncertainty, importance, risk, and workload signals;
- define eligibility, timing, priority, dosage, and non-intervention rules;
- route a self-contained request to the appropriate human role;
- define timeout, deferral, escalation, and non-blocking behavior;
- trace each intervention requirement to an artifact and validation; and
- evaluate the design through controlled routing, failure, overload, and escalation scenarios plus expert review if authorized.

**Primary artifacts:**

- listener/event-coverage map;
- uncertainty, importance, and intervention taxonomy;
- triage, priority, timing, and dosage policy;
- self-contained review-request schema and routing interface;
- burden, timeout, deferral, and escalation model;
- domain-parameterized intervention interface; and
- requirements-to-validation traceability.

**Study 1 measures:**

- requirements coverage;
- event/trigger coverage;
- deterministic triage and routing conformance;
- request completeness and explainability;
- dosage, timeout, and escalation compliance;
- bounded queue/request behavior;
- failure and overload containment; and
- expert assessment of conceptual adequacy, if authorized.

These measures demonstrate intervention-architecture properties. They do not demonstrate reduced expert burden, improved assessment, or classification accuracy.

### 4.3 Study 2 — Judgment lifecycle

**Aim:** answer SQ2.

**Method:**

- define a judgment representation for decision, rationale, confidence, scope, source evidence, role, and permitted reuse;
- validate judgment claims against available sources without blindly complying;
- detect and reconcile conflicts among judgments, sources, or later evidence;
- preserve immutable submissions and separate adjudication/correction records;
- define human-authority states for advisory reuse, proposed deterministic change, and blocked automation;
- store and retrieve judgments with provenance, scope, obsolescence, and same-case/leakage controls;
- define bounded verification dialogue and escalation; and
- validate the lifecycle through schema/contract tests, controlled conflicts, unsafe-reuse attempts, failure injection, and expert review if authorized.

**Primary artifacts:**

- structured expert-judgment schema;
- source-validation and anti-sycophancy protocol;
- conflict-detection, reconciliation, and adjudication model;
- provenance, authority, consent/privacy, and retention model;
- bounded verification/convergence policy;
- judgment-memory storage and retrieval contract;
- scope, obsolescence, leakage, and unsafe-generalization controls; and
- audit and lifecycle traceability package.

**Study 2 measures:**

- schema and contract conformance;
- provenance/source completeness;
- validation and conflict-detection coverage;
- reconciliation/adjudication traceability;
- human-authority preservation;
- bounded-dialogue compliance;
- unsafe-reuse and leakage blocking;
- storage/retrieval explainability;
- audit reconstruction completeness; and
- failure containment.

These measures demonstrate lifecycle and governance properties. They do not establish that reuse improves assessment or safely generalizes.

### 4.4 Study 3 — Evaluation and transfer

**Aim:** answer SQ3.

**Software/modeling evaluation design:**

- retain a frozen baseline;
- obtain two blinded independent reviewer returns;
- measure agreement before adjudication;
- preserve raw returns and adjudicate separately;
- use a hidden development/holdout structure;
- freeze any candidate policy before holdout use;
- compare paired outcomes where equivalently labeled;
- measure expert effort through a controlled task study when authorized; and
- analyze class-level harm, regressions, uncertainty, interaction failures, and validity threats.

**Evaluation measures:**

- accuracy, macro-F1, balanced accuracy, and class-level precision/recall only when eligible;
- candidate-only correct, baseline-only correct, net correction, and paired exact tests;
- routing precision/recall and high-priority recall;
- traceability and audit reconstruction;
- review count, time, repeated questions, and completion;
- inter-reviewer agreement and adjudication rate;
- conflict, escalation, and bounded-convergence behavior;
- leakage eligibility and holdout integrity; and
- qualitative error/interaction themes.

**Transfer dimensions:**

- normative-specification representation;
- case/event representation;
- variability/deviation semantics;
- expert role and authority;
- evidence/source set;
- temporal/context requirements;
- intervention architecture and judgment-lifecycle policy;
- judgment-memory scope;
- privacy, ethics, and retention;
- outcome measures; and
- infrastructure constraints.

**Plan A — conditional healthcare setting**

After the required software/modeling evaluation, a healthcare extension may proceed only after a precise use case, domain experts, fit-for-purpose data, approvals, privacy/ethics path, approved restricted environment, and permitted local/offline tooling are evidenced. MIMIC familiarization is limited to data-shape grounding and does not establish dataset selection or clinical feasibility. MediVARIA is a candidate framing, not an approved study.

**Plan B — second software/modeling setting**

If the healthcare gates do not pass in time, the complete framework will be evaluated in a second software/modeling dataset, diagram family, task, institution, reviewer population, or longitudinal setting. The setting must create a real transfer boundary and preserve comparable constructs.

**Study 3 outputs:**

- preregistered evaluation protocol and adjudicated gold set;
- software/modeling result and validity package;
- common-core versus adaptation taxonomy;
- domain-parameterized framework;
- feasibility and governance profile;
- comparative evidence report;
- failure/negative-transfer analysis; and
- limits of generalization.

**Binding current boundary:** [`../independent-evidence/README.md`](../independent-evidence/README.md) records 0/2 reviewer returns and 0/24 adjudicated safe labels. Quantitative performance is not yet computable. At least 20 safe labels make quantitative MSc reporting eligible with small-sample limitations; they do not by themselves establish generalization. A negative or null result remains valid evidence.

### 4.5 Data management, ethics, and human authority

- No patient data enters this repository.
- Shared source material remains read-only; derived work uses an approved separate environment.
- Restricted medical data stays in the approved VDI or equivalent environment.
- Restricted data is not sent to an online or commercial LLM.
- Reviewer IDs are pseudonymous; private mappings and returns remain local and ignored.
- Human reviewers and adjudicators remain the source of independent ground truth.
- Raw human returns remain immutable; corrections occur through adjudication records.
- Medical decision authority remains human; the proposed research does not authorize autonomous clinical decisions.
- Any public/de-identified medical dataset still requires a documented permission, ethics/privacy, and workspace determination for the proposed use.

## 5. Preliminary results and current evidence

### 5.1 Supported current statements

The current repository documents:

- a VEGO-AI software/modeling baseline and human-judgment mechanisms;
- structured human-review, feedback, memory, advisory, and controlled-comparison artifacts;
- a provisional H-layer architecture that broadens intervention, verification, integration, and learning requirements;
- provenance, evidence-gating, leakage-control, and independent-review protocols; and
- an evaluation package that is ready for the authorized calibration stage.

Relevant evidence:

- [`../research-plan.md`](../research-plan.md)
- [`../extension-plan-2026-07-supervisor-redirect.md`](../extension-plan-2026-07-supervisor-redirect.md)
- [`../independent-evidence/README.md`](../independent-evidence/README.md)
- [`../independent-evidence/SUPERVISOR_DECISIONS_REQUIRED.md`](../independent-evidence/SUPERVISOR_DECISIONS_REQUIRED.md)

### 5.2 Claim/evidence boundary

| Claim | Current status | What is still required |
| --- | --- | --- |
| Human judgment can be structurally captured and retrieved in the current artifact | Mechanism/implementation evidence exists | Broader expert and cross-setting evaluation |
| The current artifact is auditable and preserves provenance under specified scenarios | Partial mechanism/validation evidence | Consolidated Study 2 lifecycle traceability and expert review |
| A policy improves classification quality | Not available | Eligible independent labels, frozen policy, paired evaluation |
| A policy reduces expert effort without harm | Not available | Controlled human task study plus quality evidence |
| Reusable judgment generalizes | Not available | Leakage-safe additional settings and external replication |
| The approach transfers to medicine | Planning hypothesis only | G1–G6, applicable downstream controls, and Study 3 evidence |
| The approach has clinical performance or safety | No evidence | Not claimable from current work |

### 5.3 EXP-005/independent-evidence state

- Candidate rows: 24.
- Independent reviewer returns: 0 of 2.
- Adjudicated generalization-safe labels: 0 of 24.
- Accuracy, macro-F1, generalization, effort reduction, and superiority: not yet computable.
- Synthetic or AI-generated labels cannot close the gate.
- Negative and null results remain acceptable research outcomes.

### 5.4 Medical preliminary-results boundary

Current medical material consists of proposed mappings, use-case concepts, literature branches, and a documented bounded metadata/schema-only MIMIC audit. That audit observed 25 CSVs totaling 39.65 GiB, missing `NOTEEVENTS`, and unresolved provenance; it inspected no patient rows and is not a medical result. The planned maximum was four hours, but no start/end or elapsed-time record exists, so this draft does not claim a completed four-hour run. Education/software-modeling metrics cannot be relabeled as medical results. No partner, clinician panel, approved dataset, ethics path, or restricted technical environment is evidenced as ready by this draft.

## 6. Work plan and timeline

### 6.1 Phases

| Phase | Provisional window | Main outputs | Exit gate |
| --- | --- | --- | --- |
| P0 Research architecture | 30 Jul–5 Aug 2026 | Working U-RQ/SQ1–SQ3, three-study map, legacy crosswalk, proposal `v0.1`, and supervisor decision pack | Explicit supervisor read-back |
| P1 Literature and study design | 5–19 Aug 2026 | Search protocol/screening, critical synthesis/gap matrix, Penina reuse, RACI, and Study 1–3 method/artifact/evidence plans | Scope, synthesis, and method review |
| P2 Route and feasibility lock | By 26 Aug 2026 | Proposal `v0.3`, frozen approved-or-revised architecture, G1–G6 dossier or Plan B committed setting | Logged medical go/no-go and September route |
| P3 Core proposal convergence | 27 Aug–9 Sep 2026 | Introduction, problem, gap, RQs, methods, preliminary evidence, and claim-boundary section complete | Internal evidence/consistency review |
| P4 Full developed draft | 10–16 Sep 2026 | `v0.7` with resources, ethics, risks, citations, and complete timeline | Complete internal draft |
| P5 Supervisor-resolution draft | 17–23 Sep 2026 | Comments resolved; formatting and official process verified | Supervisor corrections recorded |
| P6 Submission candidate | 24–30 Sep 2026 | `v1.0`, references and appendices validated | Requirements/traceability complete |
| P7 Final buffer | Through 7 Oct 2026 | Final approval, submission, or candidacy-presentation package | External process confirmation |
| P8 Study 1 execution | After proposal alignment | Intervention architecture and controlled design evaluation | Study 1 protocol and supervisor decisions |
| P9 Study 2 execution | After Study 1 interface alignment | Judgment lifecycle and controlled governance evaluation | Study 2 protocol and applicable human/ethics decisions |
| P10 Study 3 execution | Human- and route-gate dependent | Software/modeling evaluation, then Plan A healthcare or Plan B non-medical transfer | Existing independent-evidence and setting-specific gates |

The September and October dates are working targets from the supervisor discussion, not verified university deadlines.

### 6.2 Resources

| Resource | Available | Needed |
| --- | --- | --- |
| Repository mechanisms/specifications | Existing | Consolidation into Study 1 intervention and Study 2 judgment-lifecycle traceability |
| Frozen software/modeling baseline | Existing | Independent reference labels and later additional settings |
| Independent-evidence tooling | Calibration-ready | Two reviewers, calibration returns, instruction freeze, evaluation, adjudication |
| Literature taxonomy/resource pack | Existing seed | Living matrix, verified corpus, review method |
| Supervisors | Direction/decision role | Weekly bounded decisions and corrections |
| Penina course work | Expected reusable input | Confirm scope, due dates, and transparent reuse |
| MIMIC/shared material | Discussed as familiarization resource | Confirm access, permission, source protection, and bounded use |
| Medical expert/partner | Unresolved | Required only for Plan A |
| Restricted compute/local tooling | Unresolved | Required only for restricted Plan A work |
| University candidacy guidance | Unverified | Authoritative dates, reviewers, process, and format |

### 6.3 Principal risks

| Risk | Mitigation |
| --- | --- |
| Medical dependency makes the doctorate infeasible | Same RQs under Plan B; time-bound route decision |
| Deep medical learning delays proposal | Bounded metadata/schema audit boundary, future timing record, and stop rule |
| Evidence claims outrun data | Claim/evidence table and 0/24 boundary |
| Human availability blocks empirical work | Continue Studies 1–2, literature, and proposal; schedule reviewers explicitly |
| Restricted-data misuse | Approved environment only; no repository copy; no online/commercial LLM |
| Literature gap is assumed rather than demonstrated | Living matrix, transparent review method, gap-to-contribution synthesis |
| Study questions proliferate | Legacy crosswalk; hypotheses remain nested under exactly three SQs |
| Formal schedule is wrong | Verify with university sources before submission commitment |

### 6.4 Immediate decisions and actions

The next supervisor checkpoint should:

1. select/correct the U-RQ wording;
2. confirm SQ1–SQ3 and the study map;
3. confirm Plan A/Plan B definitions;
4. set the medical-route decision date;
5. confirm literature scope and review method direction;
6. authorize, narrow, or defer the bounded MIMIC note;
7. assign medical feasibility owners;
8. assign university-process verification;
9. confirm Drive access; the recurring weekly calendar is already verified; and
10. define the next single weekly task.

The concise pre-read is [`../meetings/2026-08-05-supervisor-pre-read.md`](../meetings/2026-08-05-supervisor-pre-read.md). The detailed execution plan is [`2026-07-29-doctoral-execution-plan.md`](./2026-07-29-doctoral-execution-plan.md).

## Record and review caveat

The July 29 Hebrew ASR and English translation are machine-derived; human bilingual review and full diarization remain pending. This draft uses the evidence-linked requirements/action registers and analytical paraphrases, not direct quotations. Supervisor corrections must be recorded explicitly and then propagated through the RQ pack, crosswalk, proposal, literature matrix, and study plans.
