# Three-Study Research Contract

Last updated: 2026-08-19

Status: **working research contract for supervisor review.** Research-question wording, study
boundaries, artifact choices, evidence admissibility, and Plan A/Plan B wording are not approved
until recorded in the decision/change log.

## Status and source authority

The umbrella RQ and SQ1–SQ3 wording below were refined from the 2026-07-30 baseline during the
2026-08-05 supervisor working call. The meeting record is machine-derived and the exact final text
has not been verified against Ali's saved notes. `D-RQ-01` and `D-RQ-02` therefore remain pending.
Do not present the wording as approved.

The artifact structure in this contract follows
[`artifact-layer-contract.md`](./artifact-layer-contract.md):

1. one **primary research artifact** carries the scientific contribution boundary;
2. a **supporting implementation bundle** instantiates that artifact in VEGO-AI; and
3. a separate **evaluation package** answers the study's knowledge question.

This reconciles the narrower Chapter 4 artifacts with the broader architecture and evaluation
bundles used in the literature review and workbook. It remains a recommendation pending Item 1 in
`2026-08-19-chapter4-decisions-packet.md`.

## Scientific spine

### Working umbrella research question

> How can human judgment be captured, governed, and used to support agentic-AI-driven variability exploration in guideline operationalization scenarios, enabling reliable human–AI co-reasoning?

### Working subquestions

1. **SQ1 — Selective intervention:** When and how, in variability exploration scenarios, should an agentic assessment system request human judgment so that important uncertainties are addressed without unnecessary expert burden?
2. **SQ2 — Governed knowledge reuse:** How should expert judgment — including the system's core reasoning — be represented, validated, reconciled, and stored so it can be reused transparently without unsafe generalization or loss of human authority?
3. **SQ3 — Evaluation and transfer:** How can expert judgment be reused and transferred across different guideline-operationalization contexts without unsafe generalization or loss of human authority, first in software/modeling and, when governance and access permit, in healthcare?

The questions are deliberately domain-neutral. Software/modeling Plan B can answer all three.
Healthcare is an optional, gated external-validity context rather than a prerequisite for doctoral
completion.

## Study contracts

| Contract field | Study 1 — Selective intervention | Study 2 — Governed judgment | Study 3 — Transfer eligibility and evaluation |
| --- | --- | --- | --- |
| **Subquestion** | SQ1 | SQ2 | SQ3 |
| **Objective** | Design and evaluate when, where, to whom, and at what dosage an agentic assessment system should request judgment under bounded expert attention. | Design and evaluate a reconstructable, provenance-preserving, contestable, claim-authorized representation and lifecycle for human judgment. | Design and evaluate a procedure that decides whether a governed source judgment may inform a target context, with what adaptation and observed target effect. |
| **Primary research artifact** | Attention-budget review-policy model relating trigger configuration to review count, review cost, candidate coverage, and later important-case coverage. | Normative governed-judgment contract with executable invariants and conformance requirements. | Transfer-eligibility decision procedure plus target-context descriptor with `Eligible`, `Eligible with adaptation`, `Blocked`, and `Undetermined` states. |
| **Supporting implementation bundle** | Event/listener catalog; proposed multi-signal score; Human Review Orchestrator; interrupt/queue/batch/audit/log modes; reviewer routing; timeout/escalation rules; burden budget; trigger and routing receipts. | Governed Judgment Object; Contestable Judgment Store; evidence and inspectable decision trace; validation tier; conflict/adjudication; claim-specific authority; visibility/privacy; provenance; lifecycle; expiry/revocation; retrieval/use/outcome history and receipts. | Scope-Aware Retrieval Advisor; visibility/authorization pre-filter; relevance and applicability checks; permission filter; context schema; transfer-distance classifier; adaptation rules; advisory-use and outcome receipts. |
| **Evaluation package** | Phase A analytical/replay and receipt validation; Phase B held-out policy comparison with independent outcome labels and observed human burden. | Phase A schema/invariant/reconstructability and independent-implementation conformance; Phase B label-only/unstructured comparator study for correction quality, usability, contestability, auditability, and governance errors. | Phase A independent-rater reliability; Phase B frozen-store held-out target comparison against matched no-reuse control with blind target labels and leakage controls. |
| **Units of analysis** | Assessment events, cases/fragments/patterns, trigger decisions, routing outcomes, review episodes, reviewer tasks, and policy windows. | Judgment records, evidence sources, review episodes, conflicts, validations, lifecycle transitions, retrieval/use events, audits, and revocations. | Source-target pairs, eligibility decisions, reason codes, raters, held-out target cases, advisory uses, overrides, and target outcomes. |
| **Phase A evidence** | Receipt completeness, deterministic reconstruction, nested-policy monotonicity, boundary and degenerate cases, candidate coverage, replay frontier, separate live-review and audit load. | Contract completeness, positive/negative/boundary fixture coverage, blind reconstruction, named failure codes, reference and independent implementation conformance. | Rater agreement on verdict and driving reason, procedure usability, distribution of `Blocked`/`Undetermined` causes, and ambiguity diagnosis. |
| **Phase B comparators** | Never ask; always ask; random review at matched budget; uncertainty-only; fixed threshold; proposed multi-signal policy. | Label-only record; unstructured comment; governed judgment contract/lifecycle. | Matched no-reuse arm under identical current evidence; scope-filtered advisory reuse. |
| **Primary Phase B outcomes** | Important-case capture or joint correctness at a stated attention budget; selective risk among autonomous decisions. | Reconstruction, correction quality, contestability, audit completeness, and scope/authority error. | Target benefit and unsafe-transfer rate, separated by transfer distance and context. |
| **Secondary outcomes** | Expert minutes, interruptions, queue delay, abandonment, review yield, role balance, override quality, reusable-judgment yield. | Completion time, workload, missing fields, unresolved disagreement, privacy/visibility errors, revocation effectiveness, user comprehension. | Calibration under shift, burden, override behavior, scope violations, blocked/undetermined reasons, revocation responsiveness, benefit by transfer level. |
| **Evidence currently available** | EXP-006–EXP-008 provide event, replay, load/coverage, and instability-candidate evidence at mechanism/observability scope only. | EXP-013–EXP-018 provide reference-implementation conformance precedent for the exact properties they test. | Readiness and proposed procedure only; no target-effect evidence. |
| **Measures explicitly excluded until gated** | Empirical superiority, optimal dosage, accuracy improvement, or workload reduction inferred from architecture, routed-item counts, tests, or fixtures. | Improved outcomes, safe generalization, successful reuse, or implementation independence inferred only from schemas, one implementation, tests, or synthetic fixtures. | Positive target benefit, generalization, effort reduction, clinical performance, safe deployment, or broad transfer while EXP-005 and target evidence are incomplete. |
| **Key dependencies** | Stable event/identity contract; literature synthesis; frozen policy and thresholds; independent labels for Phase B; reviewer availability and burden logging. | Study 1 intervention points; stable judgment/provenance contract; independent implementer for the independence claim; applicable ethics/data determination for human study data. | Study 2 source contract; authorized target context; two independent raters; blind target labels; frozen store/policies; no target contamination; Plan A or Plan B controls. |
| **Fallback** | Report the inspectable model, supporting implementation, analytical/replay results, unresolved properties, and preregistered Phase B protocol; retain effect claims as excluded. | Report the contract, reference implementation, fixture coverage, and implementation-independence/human-evidence gaps; do not infer safe reuse. | Report the procedure, readiness evidence, and exact missing-rater/target-evidence block; do not infer target benefit or safe transfer. |
| **Planned paper** | Paper 1: selective intervention and attention-budget policy in agentic assessment. | Paper 2: governed judgment contract, contestability, and lifecycle. | Paper 3A: medical transfer only if every applicable Plan A gate passes; otherwise Paper 3B: cross-context software/modeling transfer. |
| **Exit criterion** | Primary artifact and receipts pass Phase A; Phase B is completed or transparently preregistered as blocked; unsupported effect claims remain excluded; supervisors accept or correct the boundary. | Every mandatory invariant maps to an executable test; implementation-independence is either demonstrated or explicitly absent; Phase B evidence or its block is reported; advisory authority remains enforceable. | Procedure reliability is evaluated; target evaluation uses frozen partitions and blind labels; common-core/adaptation boundaries are reported under Plan A or Plan B; healthcare appears only if every applicable gate passes. |

## SQ2/SQ3 ownership boundary

- **Study 2 defines and governs source scope.** It owns hard exclusions, exact-match dimensions,
  adaptable dimensions/tolerances, ranking-only dimensions, authority, visibility, lifecycle,
  validation, contestation, provenance, and revocation semantics.
- **Study 3 applies source scope to a target context.** It owns target description, visibility and
  authorization pre-filtering, source-target comparison, adaptation selection, eligibility state,
  reason code, and target-outcome evaluation.
- Study 3 may identify a missing or defective source scope but may not silently rewrite it. Any
  source-record change returns through Study 2 and creates a new version with provenance.

This boundary is the working recommendation in Chapter 4 and remains subject to Item 2 in the
Chapter 4 decisions packet.

## Integrated U-RQ contract

The umbrella RQ is not answered merely by completing three independent artifacts.

| Field | Integrated contract |
| --- | --- |
| **Primary artifact** | End-to-end governed human-judgment lifecycle and operational definition of reliable human–AI co-reasoning. |
| **Unit of analysis** | Complete governed assessment episode: detect → triage → request → capture → validate/reconcile → store → retrieve/filter → apply as advice → monitor → expire/supersede/revoke. |
| **Comparators** | Human-only; AI-only; ordinary non-governed HITL; governed VEGO-AI. |
| **Primary outcome** | Complementary team performance at a controlled attention budget. |
| **Required governance/safety outcomes** | Calibration, authority and visibility compliance, traceability, contestability, burden, override quality, propagation errors, scope violations, unsafe reuse, and revocation effectiveness. |
| **Failure criterion** | Any load-bearing study fails; the integrated system creates propagation/authority errors; benefit is explained only by extra human time; ordinary HITL matches it at lower cost; or the result depends on leakage/post-hoc tuning. |

## Plan A and Plan B execution contract

| Dimension | Plan A — medical-enabled extension | Plan B — protected non-medical execution |
| --- | --- | --- |
| **Scientific questions** | Same U-RQ and SQ1–SQ3. | Same U-RQ and SQ1–SQ3. |
| **Study 1** | Software/modeling baseline first; medical workflow requirements may stress-test the trigger ontology only after expert and governance review. | Software/modeling intervention-policy evaluation. |
| **Study 2** | Software/modeling governed-judgment evidence first; a medical judgment lifecycle only under an approved clinician/data protocol. | Software/modeling governed-judgment study with independent implementation/review and leakage controls. |
| **Study 3** | Gated transfer to clinical guideline operationalization in an approved partner environment. | Transfer/replication across another software/modeling domain, institution, dataset, diagram family, reviewer panel, or time period. |
| **Mandatory readiness evidence** | Precise use case and boundary; named qualified expert; data dictionary and fit note; license/privacy/ethics/institutional approval; approved VDI/storage/compute; approved local/offline model or non-LLM method; feasible schedule; supervisor-approved study protocol. | Authorized non-medical context; independent reviewer/rater plan; construct-comparability and provenance record; frozen partitions; schedule and publication path. |
| **Data boundary** | No patient data in Git or the general Drive workspace; restricted data remains in the approved environment; viewer access alone does not authorize processing. | Controlled software/modeling artifacts follow existing data-management and publishability rules. |
| **Decision rule** | Every `G1`–`G6` gate must have a documented owner, evidence path, and feasible date, and all six must pass before row-level access is considered. | Activates if one or more Plan A readiness gates fails the checkpoint, unless a recorded decision changes the plan. |
| **Checkpoint** | 2026-08-26, end of day, Asia/Jerusalem — internal project-control date only. | Default proposal path from 2026-08-27 unless the logged readiness review records all Plan A gates as passed. |
| **Reopening rule** | Plan A may reopen only through completed readiness evidence, downstream controls, explicit supervisor decision, governance approval, and schedule-impact review. | Continues until an approved change log explicitly replaces it. |

## Evidence-state snapshot

- Current evidence is software/modeling evidence.
- The foundation manuscript reports 26 variability patterns; the supplied implementation snapshot
  contains 27 pattern files. The one-pattern difference remains unresolved.
- EXP-005 contains **0/24** required independent generalization-safe labels.
- Formal literature searches QL-01–QL-05 remain **0/5** unless later receipts change the state.
- Medical entry gates remain **0/6**; there are no medical performance results.
- MIMIC and partner discussions are feasibility/planning resources, not approved datasets or
  completed studies.
- Instrument evidence, implementation evidence, and outcome/effect evidence remain separate.
- EXP-009/EXP-010 are not proposal evidence before `M-04` unless supervisors decide otherwise.

## Human resourcing and ethics controls

- Study 2's implementation-independence claim requires an independent implementer, not only a
  reviewer of the authors' implementation.
- Study 3's procedure-reliability study requires two independent raters and a frozen rating
  protocol.
- Applicable ethics/IRB and data-access determinations must be obtained before participant
  recruitment or study-data collection.
- Real participant names are not stored in a public repository without permission; coded
  identifiers are used where appropriate.
- The current outreach drafts are in
  `docs/operations/study-resourcing-request-template.md`; no person is considered committed until
  an agreement is recorded through the approved process.

## Change control

Any change to the U-RQ/SQ wording, study objective, artifact layer, SQ2/SQ3 boundary, Plan A/Plan B
boundary, evidence gate, comparator, primary outcome, or publication target must:

1. identify the affected requirement/action/question IDs;
2. record the old and new wording;
3. classify the change as scientific, implementation-only, evaluation-only, or administrative;
4. state the evidence and rationale;
5. identify approver, owner, and effective date;
6. update Chapter 4, the decision/change log, the canonical version manifest, literature-review
   contribution tables, workbook rows, and proposal figures; and
7. preserve prior versions rather than rewriting the historical decision record.
