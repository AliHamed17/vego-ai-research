# Legacy Research-Question Crosswalk

Status: **working consolidation map for supervisor review**

Purpose: preserve the value of earlier research questions while enforcing the 29 July requirement for one umbrella question and exactly three subquestions. This document does not declare earlier questions invalid. It reclassifies them as subconstructs, study-level experimental questions, literature tasks, or conditional transfer factors.

**2026-08-10 status note:** the wording below was refined live during the 2026-08-05 supervisor call
(Iris and Arnon) against the wording this document originally recorded. The crosswalk logic in §§2–8
(which legacy item maps to which canonical SQ) is **unaffected** by this wording refinement — only the
exact phrasing of U-RQ/SQ1–SQ3 changed, not their scope or boundaries. `D-RQ-01`/`D-RQ-02` remain formally
`Pending` until Ali verifies the exact wording against his own saved working draft and a supervisor
decision is logged; see `docs/research/meetings/2026-08-05-supervisor-meeting.md` for the evidence. Chapter
3 of the thesis (`thesis/chapters/03-problem-and-research-questions.md`) has been migrated to this wording.

## 1. Canonical working hierarchy

**U-RQ:** How can human judgment be captured, governed, and used to support agentic-AI-driven variability
exploration in guideline operationalization scenarios, enabling reliable human–AI co-reasoning?

| Canonical ID | Exact working question |
| --- | --- |
| SQ1 — Selective intervention | When and how, in variability exploration scenarios, should an agentic assessment system request human judgment so that important uncertainties are addressed without unnecessary expert burden? |
| SQ2 — Governed knowledge reuse | How should expert judgment — including the system's core reasoning — be represented, validated, reconciled, and stored so it can be reused transparently without unsafe generalization or loss of human authority? |
| SQ3 — Evaluation and transfer | How can expert judgment be reused and transferred across different guideline-operationalization contexts without unsafe generalization or loss of human authority, first in software/modeling and, when governance and access permit, in healthcare? |

The wording remains pending supervisor decision in [`2026-08-05-rq-decision-pack.md`](./2026-08-05-rq-decision-pack.md) (`D-RQ-01`, `D-RQ-02`).

## 2. Current `research-plan.md` crosswalk

Source: [`../research-plan.md`](../research-plan.md)

| Legacy item | Disposition | Canonical destination | Reason |
| --- | --- | --- | --- |
| Main RQ — capture, governance, and evaluation of reusable human judgment for auditable co-reasoning | Retain as direct predecessor | U-RQ | The new umbrella broadens assessment beyond domain models and makes transfer explicit. |
| RQ1 — baseline identification/classification before human intervention | Reclassify as baseline characterization | Study 3 / preliminary results | It defines the comparator and errors; it is not a separate doctoral contribution. |
| RQ2 — which classifications require human judgment | Retain as an intervention-design question | SQ1 | It becomes the eligibility, timing, priority, and dosage component. |
| RQ3 — structured/provenanced feedback for audit, conflict, and reuse | Retain as a judgment-lifecycle question | SQ2 | It is central to representation, validation, reconciliation, provenance, storage, and authority. |
| RQ4 — advisory and controlled memory-informed reuse | Split into governance and effect | SQ2 + SQ3 | Safe reuse rules belong in SQ2; empirical consequences and transfer belong in SQ3. |
| RQ5 — positioning in HITL/XAI/design-science literature | Reclassify as literature task | Literature review across all SQs | Positioning supports the gap and contribution but is not one of the three empirical/design questions. |

## 3. Thesis Chapter 3 crosswalk

Source: [`../../../thesis/chapters/03-problem-and-research-questions.md`](../../../thesis/chapters/03-problem-and-research-questions.md)

The MSc thesis chapter currently contains one literature/design-science RQ, five thesis subquestions, and three separate evaluation RQs. They remain valid within the MSc thesis. For the PhD proposal, they are explicitly nested under the new hierarchy rather than silently removed.

| Thesis Chapter 3 item | Disposition in PhD proposal | Canonical destination | Reason |
| --- | --- | --- | --- |
| Thesis main RQ — prior approaches to human–AI collaboration and their implications for reusable-judgment mechanisms | Retain as a supporting literature/design question | U-RQ literature and Study 1–2 rationale | It frames the state of the art and artifact design but is not an additional PhD-level RQ. |
| Thesis SQ1 — control and timing | Retain as a Study 1 design question | SQ1 | Directly covers when review is requested and how control/timing is distributed. |
| Thesis SQ2 — direction of information | Split across the two mechanism studies | SQ1 + SQ2 | AI-to-human request/evidence packaging belongs in SQ1; human-to-AI feedback capture and reuse belongs in SQ2. |
| Thesis SQ3 — role of judgment | Retain as a Study 2 conceptual question | SQ2 | Distinguishes transient correction from governed reusable knowledge. |
| Thesis SQ4 — structure and reuse | Retain as a Study 2 design question; evaluate effects in Study 3 | SQ2 + SQ3 | Representation, storage, retrieval, and authority belong in SQ2; benefit/harm of reuse belongs in SQ3. |
| Thesis SQ5 — MDE-assessment gap | Retain as supporting positioning | Literature review and software/modeling baseline | It establishes the motivating domain gap but is not a fourth PhD subquestion. |
| Thesis E-RQ1 — baseline errors | Retain as evaluation-only | SQ3 / Study 3 software-modeling baseline | It supplies the error characterization and comparator for framework evaluation. |
| Thesis E-RQ2 — targeting and retrieval | Split between design and evaluation | SQ1 + SQ2 + SQ3 | Targeting is designed in SQ1, retrieval/governance in SQ2, and their observed effect in SQ3. |
| Thesis E-RQ3 — unseen paired effect | Retain as evaluation-only | SQ3 / Study 3 | It is a nested empirical question governed by the holdout and external-replication gates. |

The chapter’s H1–H4 hypotheses remain nested Study 3 hypotheses. Their unproven status and evidence gates remain unchanged; consolidation into the PhD hierarchy does not turn them into positive claims.

## 4. `phd-thesis-optimization-plan.md` crosswalk

Source: [`../phd-thesis-optimization-plan.md`](../phd-thesis-optimization-plan.md)

| Legacy item | Canonical destination | Treatment |
| --- | --- | --- |
| P-RQ1 — when to ask for human judgment | SQ1 | Intervention eligibility, priority, timing, dosage, routing, and burden |
| P-RQ2 — reusable, auditable, conflict-aware representation | SQ2 | Judgment schema, validation, provenance, conflict handling, storage, and authority |
| P-RQ3 — when reuse improves, clarifies, or escalates | SQ3 | Paired effects, escalation, error analysis, effort, and stopping rules |
| P-RQ4 — advisory versus deterministic versus blocked automation | SQ2 + SQ3 | Reuse authority and transition rules in SQ2; evidence of effects in SQ3 |
| P-RQ5 — transfer across domains, diagrams, reviewers, datasets | SQ3 | Primary predecessor of the evaluation-and-transfer study |

The five items remain useful as analytic dimensions within three studies. They no longer need to appear as five top-level PhD questions.

## 5. H-layer directive crosswalk

Sources:

- [`../extension-plan-2026-07-supervisor-redirect.md`](../extension-plan-2026-07-supervisor-redirect.md)
- [`../h-layer/skills-map.md`](../h-layer/skills-map.md)

| H-layer construct | Canonical destination | Research role |
| --- | --- | --- |
| S1 listening, S2 triage, and S3 human routing | SQ1 | Event coverage, eligibility, timing, dosage, routing, escalation, and burden-aware request architecture |
| S4 structured capture | SQ2 | Judgment representation, provenance, scope, confidence, and authority |
| S5 source-grounded verification | SQ2 + SQ3 | Validation/reconciliation architecture in SQ2; measured effect and friction in SQ3 |
| S6 integration and S7 learning/reuse | SQ2 + SQ3 | Governed storage/reuse in SQ2; evidence of later effects and transfer in SQ3 |
| Intervention dosage | SQ1 + SQ3 | Policy design in SQ1; quality/workload trade-offs in SQ3 |
| Convergence/bounded dialogue | SQ2 + SQ3 | Reconciliation/authority safety constraint and measurable interaction cost |
| Cross-domain parameterization | SQ3 | Evaluation and transfer analysis |

H1/H2/H3 are capability groups, not additional research questions. M4/EXP instruments remain part of the evaluation path rather than the framework’s claimed outcome.

## 6. Independent-evidence question crosswalk

Sources:

- [`../independent-evidence/README.md`](../independent-evidence/README.md)
- [`../thesis-evidence/THESIS_ACCURACY_EVIDENCE_ADVANCEMENT_PLAN.md`](../thesis-evidence/THESIS_ACCURACY_EVIDENCE_ADVANCEMENT_PLAN.md)

| Evidence question | Canonical destination | Boundary |
| --- | --- | --- |
| E-RQ1 / baseline errors | SQ3, baseline characterization | Requires independent human reference evidence |
| E-RQ2 / targeting and retrieval | SQ1 + SQ3 | Intervention/retrieval design belongs in SQ1; its effect requires SQ3 evidence |
| E-RQ3 / unseen paired effect | SQ3 | Holdout is a pilot; broader transfer needs another setting |
| Better classification | SQ3 | Not computable at 0/24 |
| Lower human effort | SQ3 | Requires a controlled task study |
| Best routing rule | SQ1 + SQ3 | Rule design belongs in SQ1; selection requires adjudicated targets and SQ3 evaluation |
| Best topology | SQ3 | Compares complete-framework performance/resource trade-offs |
| External replication | SQ3 | Required for a broader transfer/generalization claim |

These are operational hypotheses or measurements inside Studies 1–3, not top-level PhD questions.

## 7. MediVARIA crosswalk

Source: [`../medivaria/medivaria-study-plan.md`](../medivaria/medivaria-study-plan.md)

MediVARIA is treated here as a **candidate Plan A setting**. The existing plan explicitly records supervisor endorsement, partner, data access, and clinical evidence as pending.

| MediVARIA item | Canonical destination | Treatment under the new architecture |
| --- | --- | --- |
| MV-RQ1 — architecture transfer and domain-agnostic components | SQ3 | Core transfer factor for candidate healthcare Study 3 |
| MV-RQ2 — justified versus erroneous deviation quality | SQ3 | Candidate healthcare outcome; no result or feasibility claim exists |
| MV-RQ3 — intervention dosage and clinician load | SQ1 + SQ3 | Intervention construct in Study 1, conditionally evaluated in healthcare under Study 3 |
| MV-RQ4 — source-grounded verification of overrides | SQ2 + SQ3 | Validation/reconciliation construct in Study 2, conditionally evaluated in Study 3 |
| MV-RQ5 — longitudinal clinical-judgment memory | SQ2 + SQ3 | Knowledge-reuse construct plus later longitudinal evaluation factor |
| MV-RQ6 — ontology, temporal, and conditional-language transfer costs | SQ3 | Adaptation taxonomy and feasibility analysis |

The six medical questions therefore become conditional measurements or adaptation factors under Study 3 evaluation and transfer. They are not six additional PhD subquestions.

## 8. PhD idea-log crosswalk

Source: [`../phd-extension-ideas.md`](../phd-extension-ideas.md)

| Idea | Canonical destination | Plan |
| --- | --- | --- |
| Medical transfer | SQ3 | Plan A candidate |
| Human dosage across domains | SQ1 + SQ3 | Study 1 intervention policy, then Study 3 evaluation/conditional replication |
| Source-grounded anti-sycophancy | SQ2 + SQ3 | Study 2 validation/reconciliation mechanism and Study 3 effect |
| Cross-institution modeling evaluation | SQ3 | Strong Plan B candidate |
| Longitudinal judgment memory | SQ2 + SQ3 | Study 2 knowledge-lifecycle design and Study 3 longitudinal effect |

## 9. Proposal placement

| Material | Proposal section |
| --- | --- |
| Prior main RQ and P-RQs | Research background and rationale for consolidated RQs |
| Baseline RQ1 and E-RQ1 | Preliminary results and Study 3 comparator |
| H-layer S1–S3 and P-RQ1 | Methodology/artifacts for Study 1 intervention architecture |
| H-layer S4–S7 and P-RQ2/P-RQ4 governance aspects | Methodology/artifacts for Study 2 judgment lifecycle |
| P-RQ3/P-RQ5, evidence questions, idea log, and MV-RQs | Study 3 evaluation/transfer hypotheses, measures, and Plan A/Plan B |
| Prior RQ5/literature positioning | Literature review and gap synthesis |

## 10. Change-control rule

Future proposed questions must be classified as one of:

1. wording refinement of U-RQ/SQ1/SQ2/SQ3;
2. study-level hypothesis or measurement;
3. construct or artifact requirement;
4. literature-review question;
5. transfer factor; or
6. genuinely new top-level research question requiring supervisor-approved restructuring.

Do not add a fourth subquestion or restore a parallel five-/six-question list without an explicit supervisor decision.

## 11. Evidence caveat

This consolidation is grounded in the evidence-linked July 29 requirements and action registers. The underlying transcript and English translation are machine-derived, human bilingual review and full diarization remain pending, and no direct quotations are used here.
