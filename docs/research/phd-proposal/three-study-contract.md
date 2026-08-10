# Three-Study Research Contract

Last updated: 2026-08-10 (wording refined per the 2026-08-05 supervisor working call; see status note below)
Status: Working research contract for supervisor review; question wording, study scope, and Plan A/Plan B assignment are not approved until recorded in the decision/change log.

**2026-08-10 status note:** the umbrella RQ and SQ1–SQ3 wording below were refined live during the
2026-08-05 supervisor call (Iris and Arnon), against the `2026-07-30` working baseline recorded in
[`2026-08-05-rq-decision-pack.md`](./2026-08-05-rq-decision-pack.md). This is a **machine-transcribed,
provisional correction — `D-RQ-01`/`D-RQ-02` remain formally `Pending`** in that pack and in
`docs/research/meetings/2026-08-05-supervisor-presentation-checklist.md` until Ali verifies the exact
text against his own saved working draft from the call and logs a supervisor-confirmed decision. Do not
treat the wording below as approved. See
[`docs/research/meetings/2026-08-05-supervisor-meeting.md`](../meetings/2026-08-05-supervisor-meeting.md)
for the evidence.

## Scientific spine

### Working umbrella research question

> How can human judgment be captured, governed, and used to support agentic-AI-driven variability
> exploration in guideline operationalization scenarios, enabling reliable human–AI co-reasoning?

### Working subquestions

1. **SQ1 — Selective intervention:** When and how, in variability exploration scenarios, should an agentic assessment system request human judgment so that important uncertainties are addressed without unnecessary expert burden?
2. **SQ2 — Governed knowledge reuse:** How should expert judgment — including the system's core reasoning — be represented, validated, reconciled, and stored so it can be reused transparently without unsafe generalization or loss of human authority?
3. **SQ3 — Evaluation and transfer:** How can expert judgment be reused and transferred across different guideline-operationalization contexts without unsafe generalization or loss of human authority, first in software/modeling and, when governance and access permit, in healthcare?

These questions are deliberately domain-neutral. The software/modeling program can answer all three. Medicine is an optional evaluation context, not a prerequisite for the doctorate. (SQ3's software-modeling-first / conditional-healthcare framing is carried over unchanged from the pre-call baseline; the call's edits sharpened the *reuse-and-transfer* framing but did not revisit the domain sequencing, which is Plan A/Plan B territory in §"Plan A and Plan B execution contract" below.)

## Study contracts

| Contract field | Study 1 — Selective-intervention architecture | Study 2 — Governed judgment lifecycle | Study 3 — Evaluation and cross-domain transfer |
| --- | --- | --- | --- |
| Subquestion | SQ1 | SQ2 | SQ3 |
| Objective | Design and inspect when, where, and at what dosage agentic assessment should request real human judgment, balancing important uncertainty against expert burden. | Design and inspect a provenance-preserving lifecycle for representing, validating, reconciling, storing, retrieving, expiring, revoking, and transparently reusing human judgment while preserving human authority. | Empirically evaluate the common approach for assessment quality, consistency, traceability, and expert effort, then test what transfers and what must adapt in a second setting. |
| Primary method | Design-science construction plus requirements-to-artifact evaluation, intervention-policy modeling, architecture traceability, bounded scenario analysis, and structured literature synthesis. | Design-science artifact evaluation plus schema/contract validation, source-grounded verification scenarios, conflict/adjudication analysis, authority analysis, provenance inspection, and bounded-convergence analysis. | Controlled comparative empirical study in software/modeling followed by a comparative transfer case: blinded independent labeling, adjudication, paired comparison, workload/error/validity analysis, and Plan A or Plan B replication. |
| Units of analysis | Assessment events, uncertainty/importance signals, review candidates, intervention decisions, dosage modes, routing outcomes, timeouts, and reviewer tasks. | Judgment records, evidence sources, validations, conflicts, reconciliations, authority transitions, provenance chains, retrievals, reuse proposals, expiries/revocations, and convergence outcomes. | Assessment cases, reviewer judgments, changed-versus-unchanged decisions, settings/domains, datasets, artifacts/processes, reviewer panels, required adaptations, governance profiles, and cross-context outcomes. |
| Data and evidence | Existing VEGO-AI/H-layer requirements, event catalogs, traces, specifications, tests, controlled fixtures, literature corpus, and supervisor decisions. Synthetic fixtures remain mechanism tests only. | Existing judgment schemas, provenance and memory artifacts, H-Verify/conflict fixtures, tests, governance requirements, and later approved human judgments where available. | Frozen VEGO-AI software/modeling baseline; existing 27-pattern evidence; the 24 generalization-safe EXP-005 rows; later approved reviewer returns; then **Plan A** approved healthcare evidence or **Plan B** an authorized second software/modeling context. EXP-005 is currently 0/24. |
| Core artifact | Domain-neutral intervention architecture: listener/event catalog, eligibility/priority and uncertainty criteria, triage/dosage policy, human-routing contract, timeout/escalation rules, and burden budget. | Governed judgment lifecycle: structured judgment schema, H-Verify/source challenge, conflict/adjudication and authority rules, provenance model, judgment memory, explainable retrieval, scope controls, expiry/revocation, and bounded integration/reuse. | Preregistered evaluation and workload protocol; adjudicated reference evidence; result/validity package; traceability audit; transfer taxonomy; common-core/adaptation map; domain contract; governance profile; replication report; stop/fallback rules. |
| Primary measures | Requirements-to-artifact coverage; trigger/eligibility coverage; review-rate and burden projections; routing completeness; escalation/timeout behavior; decision traceability; missed-important-case criteria for later empirical testing. | Schema/contract validity; provenance completeness; validation and reconciliation coverage; conflict/authority-rule coverage; retrieval explanation completeness; unsafe-reuse rejection; scope/expiry/revocation enforcement; bounded convergence. | Assessment quality where eligible; inter-rater agreement; consistency; traceability completeness; reviewer time/cases per hour; adjudication and escalation rates; net correction; repeated-review effort; adaptation effort; invariant-versus-domain-specific component ratio; blocked-transfer reasons. |
| Measures explicitly excluded until gated | Empirical superiority, optimal dosage, accuracy improvement, or workload reduction based only on architecture/tests/fixtures. | Claims that governed reuse improves outcomes or generalizes safely based only on schemas, memory, tests, or synthetic fixtures. | Any positive accuracy/generalization/effort claim while EXP-005 is 0/24; clinical performance, alert reduction, treatment quality, patient outcomes, safe deployment, or broad transfer without authorized evidence. |
| Intended contribution | A reusable selective-intervention architecture explaining when and how human judgment should enter agentic assessment without making expert review universal. | A governed knowledge-reuse theory and artifact showing how judgment can remain validated, reconcilable, auditable, scoped, transparent, and human-authorized across reuse. | Evidence and boundary conditions for quality, consistency, traceability, effort, and transfer, including what generalizes, what must change, and when fallback or escalation is required. |
| Key dependencies | Stable event/uncertainty contract; literature synthesis; artifact validation; supervisor decisions on eligibility, dosage, timeout, and routing. | Study 1 intervention points; stable judgment/provenance contracts; supervisor decisions on validation, conflict, authority, convergence, and reuse scope. | Studies 1–2 artifacts; EXP-005 approval; two independent reviewers; adjudicator; sealed development/holdout discipline; no baseline overwrite; **Plan A:** six entry gates G1–G6 plus applicable downstream controls; **Plan B:** authorized independent software/modeling context and reviewer plan. |
| Fallback | If dosage effects cannot yet be measured, report the inspectable architecture, analytical burden model, scenario validation, unresolved decisions, and preregistered empirical test; keep effectiveness claims excluded. | If real judgment records remain unavailable, report mechanism/contract validation and the human-evidence gate; do not infer safe reuse from fixtures. | If EXP-005 remains incomplete, report the exact block and accept readiness-only evidence. If any G1–G6 gate lacks a documented owner, evidence path, and feasible completion date by 2026-08-26, execute Plan B. |
| Planned publication target | Paper 1: selective-intervention/agentic human-in-the-loop architecture paper for human–AI interaction, agentic systems, or AI/software-engineering research. | Paper 2: governed knowledge-reuse and judgment-lifecycle paper for human-centered AI, knowledge engineering, or AI-assisted software/model engineering. | Paper 3A: clinical-informatics/CDSS evaluation-and-transfer paper only if Plan A gates and evidence exist; otherwise Paper 3B: cross-domain/cross-institution software/modeling evaluation-and-transfer paper. |
| Exit criterion | Every SQ1 intervention requirement maps to an inspectable artifact and validation; burden and uncertainty controls are explicit; unsupported effect claims remain excluded; supervisors accept or correct the boundary. | Every SQ2 lifecycle stage, authority rule, and unsafe-reuse control maps to an inspectable artifact and validation; transparent reuse remains advisory/gated until evidence permits more. | At least 20 safe adjudicated labels for quantitative eligibility; negative/null results are retained; a common-core/adaptation analysis is completed under either plan; healthcare evidence appears only if every applicable gate passes. |

## Plan A and Plan B execution contract

| Dimension | Plan A — medical-enabled evaluation | Plan B — protected non-medical execution |
| --- | --- | --- |
| Scientific questions | Same umbrella RQ and SQ1–SQ3. | Same umbrella RQ and SQ1–SQ3. |
| Study 1 | Software/modeling baseline; medical workflow requirements may be used as a design stress test only after expert review. | Software/modeling baseline and intervention-policy evaluation. |
| Study 2 | Software/modeling governed-reuse evidence first; medical judgment lifecycle only after approved clinician/data protocol. | Software/modeling governed-reuse study with independent reviewers and leakage controls. |
| Study 3 | Gated transfer to clinical guideline adherence in an approved partner environment. | Replication across another software/modeling domain, institution, dataset, diagram/model type, or reviewer panel. |
| Mandatory readiness evidence | **A1:** precise use case/boundary; **A2:** named expert and committed availability; **A3:** data dictionary and bounded data-fit note; **A4:** license/privacy/ethics/institutional approval; **A5:** approved VDI/storage/compute; **A6:** approved offline model or non-LLM method; **A7:** feasible schedule; **A8:** supervisor-approved study protocol before execution. | Authorized non-medical corpus/context; independent reviewer plan; construct-comparability and provenance record; schedule and publication path. |
| Data boundary | No patient data in Git or the general Drive workspace. Restricted data stays in the approved VDI. MIMIC viewer access alone does not authorize processing. | Controlled software/modeling artifacts follow the existing data-management and publishability rules. |
| Decision rule | G1–G6 must each have a documented owner, evidence path, and feasible completion date by the checkpoint. All six must pass before row-level access is considered. | Activates automatically if one or more G1–G6 readiness gates fails the checkpoint. |
| Checkpoint | 2026-08-26, end of day, Asia/Jerusalem. | Default committed September proposal path from 2026-08-27 unless G1–G6 pass the logged readiness review. |
| Reopening rule | After fallback, Plan A can reopen only through completed G1–G6 evidence, applicable downstream controls, explicit supervisor decision, governance approval, and schedule-impact review. It cannot displace committed Plan B milestones without a recorded change. | Continues until an approved change log explicitly replaces it. |

The 2026-08-26 checkpoint is an internal project-control date. It is not attributed to the July 29 meeting and is not a formal university deadline.

## Evidence-state snapshot

- Current evidence is software/modeling evidence.
- The artifact and evaluation infrastructure provide preliminary and readiness evidence, not proof of improved accuracy or generalization.
- EXP-005 contains **0 of 24** required independent generalization-safe labels.
- Medical work is `Planned`, `Blocked`, or `Partner-dependent` as specified in the claim register; there are no medical performance results.
- MIMIC is an exploratory resource, not the selected final dataset.
- Clalit access, partner commitment, clinical experts, formal protocol, ethics/privacy approval, and approved local-model infrastructure are not evidenced as complete.

## Change control

Any change to the umbrella question, SQ wording, study objective, Plan A/Plan B boundary, evidence gate, or publication target must:

1. identify the affected requirement/action/question IDs;
2. record the old and new wording;
3. state the evidence and rationale;
4. identify approver, owner, and effective date;
5. update the master traceability and claim registers; and
6. preserve prior versions rather than rewriting the historical decision record.
