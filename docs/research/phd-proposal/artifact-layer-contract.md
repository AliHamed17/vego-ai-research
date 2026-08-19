# Layered Artifact Contract

Last updated: 2026-08-19

Status: **internal working control for supervisor review.** This document reconciles the narrower
primary artifacts proposed in Chapter 4 with the broader implementation and evaluation bundles
already used in the literature review, workbook, and three-study contract. It does not record
supervisor approval and does not change the provisional RQ wording.

## Purpose

The proposal package previously used two incompatible meanings of *research artifact*:

1. a narrow, falsifiable contribution boundary, such as an attention-budget model or a
   transfer-eligibility procedure; and
2. the complete system bundle needed to instantiate and evaluate that contribution, such as an
   orchestrator, judgment store, retrieval advisor, and evaluation harness.

Neither meaning is sufficient alone. A narrow artifact without an implementation and evaluation
path is not demonstrable. A large bundle presented as one contribution obscures which claim is
intended to generalize and which components are supporting engineering. The working resolution is
therefore a three-layer contract.

## Three-layer definition

### Layer 1 — Primary research artifact

The smallest system-independent artifact that carries the study's generalizable design claim. It
must have a defined input, output, invariant or decision rule, and a falsification condition.

### Layer 2 — Supporting implementation bundle

The VEGO-AI components, schemas, services, receipts, policies, and interfaces required to instantiate
the primary artifact. These components can provide mechanism and conformance evidence, but their
existence alone does not establish effectiveness.

### Layer 3 — Evaluation package

The protocol, comparators, independent evidence, outcome measures, leakage controls, analysis, and
failure criteria needed to answer the study's knowledge question. Evaluation outputs are not part
of the primary artifact and must not be described as already available before their gates pass.

## Canonical layered model

| Research question | Primary research artifact | Supporting implementation bundle | Evaluation package |
| --- | --- | --- | --- |
| **U-RQ — Integrated governed human-AI co-reasoning** | End-to-end governed human-judgment lifecycle and its operational definition of reliable co-reasoning | Integrated Study 1–3 components; shared identity, evidence, policy, provenance, permission, and outcome receipts | Human-only, AI-only, ordinary non-governed HITL, and governed VEGO-AI comparison on an independent test set; complementary performance, calibration, burden, authority, contestability, traceability, and propagation-safety outcomes |
| **SQ1 — Selective intervention** | Attention-budget review-policy model relating trigger configuration to review count, review cost, candidate coverage, and later important-case coverage | Event/listener catalog, proposed multi-signal score, Human Review Orchestrator, routing modes, queue and timeout rules, burden budget, trigger and routing receipts | Phase A analytical/mechanism validation; Phase B held-out policy comparison against never-ask, always-ask, random, uncertainty-only, and fixed-threshold baselines; expert-time and important-case outcomes |
| **SQ2 — Governed knowledge reuse** | Normative governed-judgment contract with executable conformance requirements | Governed Judgment Object, Contestable Judgment Store, reconciliation and adjudication mechanisms, lifecycle controls, provenance, authority, visibility, revocation, retrieval/use history, and receipts | Phase A schema, invariant, reconstructability, negative-fixture, and independent-implementation conformance; Phase B comparison with label-only and unstructured-comment records for correction quality, usability, contestability, audit completeness, and governance error |
| **SQ3 — Evaluation and transfer** | Transfer-eligibility decision procedure with target-context descriptor and explicit `Eligible`, `Eligible with adaptation`, `Blocked`, and `Undetermined` outcomes | Scope-Aware Retrieval Advisor, authorization and visibility pre-filter, applicability engine, permission filter, transfer-distance classifier, context schema, advisory-use and outcome receipts | Phase A rater-reliability study; Phase B frozen-store held-out target evaluation against matched no-reuse control, with unsafe-transfer, scope-violation, calibration, burden, override, target-benefit, and revocation outcomes |

## Ownership boundary between SQ2 and SQ3

- **SQ2 defines and governs the source judgment.** It owns the record's scope declaration, hard
  exclusions, exact-match dimensions, adaptable dimensions, authority, visibility, lifecycle,
  validation, contestation, provenance, and revocation semantics.
- **SQ3 evaluates a proposed use in a target context.** It owns target-context description,
  authorization pre-filtering, source-target comparison, adaptation selection, eligibility verdict,
  reason code, and target-outcome evaluation.
- SQ3 may report that a source scope is incomplete or unusable, but it may not silently rewrite the
  source judgment. Any revision returns to the SQ2 lifecycle and produces a new version with
  provenance.

## Evidence and claim rules

1. **Implementation is not effectiveness.** Code, fixtures, schemas, and passing conformance tests
   establish only the properties they directly inspect.
2. **Instrument evidence is not outcome evidence.** Conformance and inter-rater agreement may be
   reported as instrument evidence if supervisors permit, but they do not establish accuracy,
   generalization, safe reuse, burden reduction, or target benefit.
3. **EXP-005 remains the quality gate.** While EXP-005 is 0/24, no positive assessment-quality,
   generalization, or effort claim is licensed.
4. **Medical work remains conditional.** Plan A stays blocked until every applicable medical entry
   and downstream control passes. Plan B remains sufficient for every RQ.
5. **The integrated U-RQ needs its own test.** Three individually completed studies do not by
   themselves establish reliable co-reasoning; the integrated lifecycle must be evaluated against
   the stated baselines.

## Required cross-file adoption

This contract is the working reconciliation target for:

- `chapter-4-research-methodology.md`;
- `three-study-contract.md`;
- `2026-08-19-chapter4-decisions-packet.md`;
- the literature-review contribution and three-study tables;
- the RQ workbook artifact, baseline, and evaluation rows; and
- any proposal figure that presents one artifact per study.

Until Iris and Arnon confirm or correct Item 1 in the Chapter 4 decisions packet, this remains a
recommended control rather than an approved doctoral contribution structure.

## Change control

Any later change must identify:

1. the affected RQ and layer;
2. the old and new artifact wording;
3. whether the change alters a scientific claim, implementation only, or evaluation only;
4. the evidence and rationale;
5. the approver, owner, and effective date; and
6. every proposal, workbook, figure, and register that must be synchronized.
