# Chapter 4 Reconciliation — One-Page Change Summary

Date: 2026-08-19  
Prepared for: Iris Reinhartz-Berger and Arnon Sturm  
Status: **summary of proposed revisions; not a record of approval**

## Why Chapter 4 was revised

The earlier package used two incompatible meanings of *artifact*: Chapter 4 proposed one narrow,
falsifiable artifact per study, while the literature review, workbook, and three-study contract
used broader system and evaluation bundles. The revision does not discard either view. It separates
them into three layers so the scientific claim, implementation, and evidence are not conflated.

## Proposed structure

| Study | Primary research artifact | Supporting implementation | Evaluation |
| --- | --- | --- | --- |
| **SQ1** | Attention-budget review-policy model | Orchestrator, trigger/routing modes, queue and burden controls, receipts | Analytical/replay validation, then held-out comparison against simpler policies with actual burden and important-case outcomes |
| **SQ2** | Governed-judgment contract | Judgment Object, Contestable Store, reconciliation, authority, provenance, lifecycle, revocation, and receipts | Conformance/reconstructability, then comparison with label-only and unstructured records |
| **SQ3** | Transfer-eligibility procedure and context descriptor | Retrieval Advisor, authorization/applicability/permission controls, transfer classifier, outcome receipts | Rater reliability, then frozen-store held-out target comparison against no reuse |
| **U-RQ** | End-to-end governed human-judgment lifecycle | Integrated SQ1–SQ3 components | Human-only, AI-only, ordinary HITL, and governed VEGO-AI comparison |

## Methodological corrections

- **Study 1:** separates review count from review cost; distinguishes replay-candidate coverage from
  independently labeled important-case coverage; treats the multi-signal score as proposed rather
  than already proven; limits monotonicity claims to nested policy families; separates live review
  from audit sampling.
- **Study 2:** stores an inspectable decision trace rather than hidden chain-of-thought; expands
  authority, scope, disagreement, privacy, lifecycle, retrieval/use, and outcome fields; separates
  lifecycle, validation, and contestation states; makes reuse advisory by default; requires
  positive, negative, and boundary conformance fixtures.
- **Study 3:** adds `Undetermined` for missing/conflicting evidence; separates hard exclusions from
  adaptable differences; checks visibility/authorization before exposing evidence; defines a
  richer target context and a preregistered rater-agreement protocol; separates reliability from
  target benefit and safety.
- **Integration:** adds a distinct U-RQ evaluation so completing three isolated artifacts is not
  treated as proof of reliable co-reasoning.

## Evidence boundaries retained

- EXP-005 remains **0/24**; no positive accuracy, generalization, effort, or target-benefit claim.
- Medical entry gates remain **0/6**; no medical performance or deployment claim.
- Formal QL searches remain **0/5**; no exhaustive-literature or absence-of-prior-work claim.
- EXP-006–EXP-008 remain mechanism/observability evidence.
- EXP-013–EXP-018 remain reference-implementation conformance evidence.
- EXP-009/EXP-010 remain outside proposal evidence before `M-04`, unless explicitly decided
  otherwise.
- The manuscript reports **26 patterns**, while the supplied snapshot contains **27 pattern files**;
  the discrepancy remains visible rather than silently resolved.

## Decisions requested

1. Confirm or correct the three-layer artifact model.
2. Confirm or correct the SQ2/SQ3 ownership boundary.
3. Decide whether conformance and rater-agreement results may appear before EXP-005 when labeled
   only as instrument evidence.
4. Decide whether EXP-009/EXP-010 remain completely outside the proposal until `M-04`.
5. Confirm or correct the exact Chapter 5 wording for EXP-006/007/008.

The full response fields and affected-file lists are in
`2026-08-19-chapter4-decisions-packet.md`.

## Current status

> **Internal methodology review draft — artifact specifications defined; supervisor decisions,
> binary literature/workbook synchronization, human resourcing, and outcome evidence pending.**
