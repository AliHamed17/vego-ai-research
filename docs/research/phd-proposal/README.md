# PhD Proposal Working Package

Status: **working package for supervisor review.** No research question, artifact boundary, medical
route, dataset, partner, ethics/IRB state, empirical effect, or formal deadline is recorded as
approved merely because it appears in this directory.

This directory organizes one provisional umbrella research question, exactly three provisional
subquestions, three studies, an integrated U-RQ evaluation, and two execution paths. The package is
evidence-bounded: software/modeling is the complete baseline; medicine is a conditional transfer
setting and has no reported performance result in this repository.

## Start here — current control path

1. [`canonical-version-manifest.md`](./canonical-version-manifest.md) — identifies the current
   working artifact lineages, evidence cutoffs, approval states, hard-gate facts, and release-hash
   rules.
2. [`artifact-layer-contract.md`](./artifact-layer-contract.md) — reconciles the primary research
   artifact, supporting implementation bundle, and evaluation package for U-RQ and SQ1–SQ3.
3. [`chapter-4-research-methodology.md`](./chapter-4-research-methodology.md) — internal methodology
   review draft with two-phase study designs and an integrated U-RQ evaluation.
4. [`three-study-contract.md`](./three-study-contract.md) — compact research contract aligned to the
   same layered artifact and evidence model.
5. [`2026-08-19-chapter4-decisions-packet.md`](./2026-08-19-chapter4-decisions-packet.md) — four
   Confirm/Correct/Defer decisions plus the exact Chapter 5 wording requiring confirmation.
6. [`chapter-5-preliminary-results.md`](./chapter-5-preliminary-results.md) — bounded mechanism,
   observability, and reference-implementation conformance evidence.
7. [`2026-08-05-rq-decision-pack.md`](./2026-08-05-rq-decision-pack.md) — provisional RQ wording and
   decisions requested from Iris and Arnon.
8. [`iris-requirements-closure-audit.md`](./iris-requirements-closure-audit.md) — point-by-point
   requirement and readiness audit.
9. [`../meetings/2026-08-05-supervisor-meeting.md`](../meetings/2026-08-05-supervisor-meeting.md) and
   [`../meetings/2026-08-12-supervisor-meeting.md`](../meetings/2026-08-12-supervisor-meeting.md) —
   machine-derived meeting records with attribution and approval caveats.
10. [`../../operations/study-resourcing-request-template.md`](../../operations/study-resourcing-request-template.md)
    — independent-implementer/rater role definitions, pre-recruitment controls, and separate draft
    outreach messages.

Historical plans and earlier proposal drafts remain available for audit but do not override the
current manifest and layered contract.

## Canonical working research architecture

### Provisional umbrella research question

> How can human judgment be captured, governed, and used to support agentic-AI-driven variability exploration in guideline operationalization scenarios, enabling reliable human–AI co-reasoning?

This wording was refined from the 2026-07-30 baseline during the 2026-08-05 supervisor working call.
The underlying record is machine-derived, and `D-RQ-01`/`D-RQ-02` remain pending. Do not present the
wording as approved or final.

| ID | Canonical working subquestion | Primary research artifact | Supporting bundle and evaluation |
| --- | --- | --- | --- |
| **SQ1 — Selective intervention** | When and how, in variability exploration scenarios, should an agentic assessment system request human judgment so that important uncertainties are addressed without unnecessary expert burden? | Attention-budget review-policy model | Orchestrator/routing/receipt bundle; analytical validation then held-out policy comparison |
| **SQ2 — Governed knowledge reuse** | How should expert judgment — including the system's core reasoning — be represented, validated, reconciled, and stored so it can be reused transparently without unsafe generalization or loss of human authority? | Normative governed-judgment contract | Judgment Object/Store/lifecycle bundle; conformance then label-only/unstructured comparator evaluation |
| **SQ3 — Evaluation and transfer** | How can expert judgment be reused and transferred across different guideline-operationalization contexts without unsafe generalization or loss of human authority, first in software/modeling and, when governance and access permit, in healthcare? | Transfer-eligibility decision procedure and target-context descriptor | Retrieval/permission/transfer bundle; rater reliability then frozen-store target evaluation |
| **U-RQ integration** | Do the three mechanisms jointly enable reliable human–AI co-reasoning under controlled attention and governance? | End-to-end governed human-judgment lifecycle | Human-only, AI-only, ordinary HITL, and governed VEGO-AI comparison |

The narrow artifact and the broad system are not competing definitions. The primary artifact carries
the scientific claim; the supporting bundle instantiates it; the evaluation package tests it.

## Plan A and Plan B

- **Plan A — conditional medical extension:** build and evaluate the common mechanism in
  software/modeling first, then enter healthcare only after expert, data, access, ethics, privacy,
  infrastructure, local-model, and protocol gates are evidenced.
- **Plan B — guaranteed non-medical completion:** answer the same U-RQ and SQ1–SQ3 in
  software/modeling and an authorized second software/modeling context, dataset, diagram family,
  reviewer panel, institution, or time period.

The fallback changes the second evaluation setting, not the research questions. Medicine must not
sit on the only path to doctoral completion.

## Binding evidence boundaries

- EXP-005 remains **0/24** adjudicated generalization-safe labels. Accuracy, macro-F1,
  generalization, effort-reduction, target-benefit, and superiority claims are not licensed.
- Formal literature searches QL-01–QL-05 remain **0/5** unless a later receipt explicitly changes
  that state.
- Medical entry gates remain **0/6**. There are no clinical-performance results.
- The Study 2 independent implementer and the two Study 3 raters are not recorded as assigned.
- The foundation manuscript reports **26 variability patterns**; the supplied implementation
  snapshot contains **27 pattern files**. The one-pattern discrepancy remains unresolved.
- Current results are software/modeling mechanism, observability, conformance, and readiness
  results—not evidence of improved outcomes.
- MIMIC, medical contacts, and MediVARIA are planning or feasibility resources, not approved
  datasets or completed studies.
- No patient data belongs in this repository or the general Drive workspace. Restricted student,
  organizational, or medical data must remain in its approved environment and must not be sent to
  an ordinary hosted LLM.
- Human recruitment or study-data collection requires the applicable ethics/IRB and data-access
  determination.

## Foundation-paper wording

The supplied VEGO-AI manuscript is used as the architecture and reported-results source. It is a
template/anonymized copy with placeholder publication metadata. The safe description is:

> the group's MODELS 2026 accepted/program-listed foundation paper and corresponding implementation
> snapshot

Do not infer a final proceedings DOI, final pagination, or an independently reproduced experiment
from the supplied copy.

## Source hierarchy

1. Actual recordings and human-confirmed decisions, when available.
2. Canonical meeting records and decision/change log with stated provenance caveats.
3. [`canonical-version-manifest.md`](./canonical-version-manifest.md),
   [`artifact-layer-contract.md`](./artifact-layer-contract.md), and the current Chapter 4/three-study
   contract for the working methodology structure.
4. Frozen repository evidence and experiment receipts.
5. Rendered literature/workbook packages only when their version, cutoff, approval state, and hashes
   match the canonical manifest.

The Hebrew ASR and English summaries are machine-derived unless explicitly marked human-reviewed.
These proposal files use evidence-linked paraphrases and do not convert inferred attribution into a
quotation or approval.
