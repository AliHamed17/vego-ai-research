# Chapter 4 Completion and Reconciliation Plan — 2026-08-19

Prepared for: Ali, for later use with Iris Reinhartz-Berger and Arnon Sturm.

Status: **internal project-control plan.** It does not override the 2026-08-12 sequencing
instruction that the literature review is the priority and that methodology becomes
supervisor-facing only after the literature review is judged sufficiently complete. The purpose of
this early drafting pass is to reduce later reconciliation risk, not to represent Chapter 4 as
approved or complete.

## Why this plan exists

The earlier Chapter 4 draft mixed eight different open decision/dependency groups:

1. artifact granularity;
2. SQ2/SQ3 ownership boundary;
3. instrument-evidence admissibility before EXP-005;
4. wording for EXP-006/007/008 preliminary evidence;
5. EXP-009/EXP-010 before `M-04`;
6. Plan A placement;
7. Study 2/3 human resourcing; and
8. the sequencing/status of the methodology draft.

These items cannot be closed in the same way. Some require supervisor decisions, one is an
editorial structure choice, one requires real people and ethics/data controls, one already has a
working wording precedent in Chapter 5, and one concerns document status rather than scientific
content.

## Disposition

| Open group | Kind | Current disposition | Controlling location |
| --- | --- | --- | --- |
| Artifact granularity | Supervisor decision | Reframed as a three-layer model: primary artifact, supporting implementation bundle, evaluation package | `artifact-layer-contract.md`; decisions packet Item 1 |
| SQ2/SQ3 boundary | Supervisor decision | Study 2 defines/governs source scope; Study 3 applies it to a target context and evaluates outcome | Decisions packet Item 2 |
| Instrument evidence before EXP-005 | Supervisor decision | Recommended as admissible only when labeled instrument evidence, never as quality/generalization/safety evidence | Decisions packet Item 3 |
| EXP-006/007/008 wording | Housekeeping confirmation | Exact Chapter 5 wording reproduced for confirmation | Decisions packet housekeeping section |
| EXP-009/EXP-010 before `M-04` | Supervisor decision | Recommended exclusion from proposal evidence until `M-04` | Decisions packet Item 4 |
| Plan A placement | Editorial structure | Plan B first; Plan A conditional after gates | Chapter 4 §4.2 |
| Study 2 implementer and Study 3 raters | Real-world resourcing and governance | Separate role definitions and draft messages; ethics/data determination required before recruitment | `docs/operations/study-resourcing-request-template.md` |
| Sequencing/status | Document control | Chapter 4 labeled internal early draft; not attributed to supervisor initiation or approval | Chapter 4 status block and this plan |

## Work completed in this reconciliation pass

1. Created `artifact-layer-contract.md` to reconcile narrow research artifacts with the broader
   system and evaluation bundles.
2. Created `canonical-version-manifest.md` to identify the current working lineages and prevent
   version-number, approval-state, hard-gate, and release-hash drift.
3. Rewrote Chapter 4 with:
   - corrected draft status;
   - accepted/program-listed foundation-paper wording;
   - explicit 26-manuscript-pattern versus 27-snapshot-file discrepancy;
   - layered artifacts;
   - two evidence phases per study;
   - corrected Study 1 cost/coverage definitions and policy boundaries;
   - expanded Study 2 contract, status dimensions, advisory-use default, and conformance matrix;
   - expanded Study 3 context schema, authorization-first procedure, fourth `Undetermined` state,
     reliability protocol, and frozen-store target evaluation;
   - a separate integrated U-RQ evaluation.
4. Reconciled `three-study-contract.md` to the same artifact and evidence model.
5. Rebuilt the Chapter 4 decisions packet with recommended answers, decision/date/approver/rationale
   fields, affected-file lists, and the exact Chapter 5 wording requiring confirmation.
6. Replaced the combined resourcing note with separate Study 2 and Study 3 outreach drafts and
   pre-recruitment ethics/data/confidentiality controls.
7. Updated the proposal README to make the reconciled methodology controls visible from the entry
   page.

## What remains open

The drafting pass does not close:

- Iris and Arnon's four decisions in the Chapter 4 packet;
- exact RQ wording approval;
- human resourcing;
- ethics/IRB and data-access determinations;
- EXP-005 labels;
- an authorized Plan B target context;
- Plan A medical gates;
- formal QL-01–QL-05 execution;
- synchronization of the binary literature-review and workbook deliverables in the next rendered
  release.

## Release rule

The next supervisor-facing methodology package may be labeled current only when:

1. the literature-review and workbook tables use the same layered artifact model;
2. the canonical version manifest identifies every delivered artifact and its actual state;
3. the four decisions are either answered or visibly pending;
4. the PDF/DOCX/workbook version labels, metadata, page numbering, hard-gate counts, and approval
   language agree;
5. every named companion deliverable is present; and
6. release SHA-256 hashes are generated after the final render.

Until then, the defensible status is:

> **Chapter 4 internal methodology review draft — artifact specifications defined; supervisor
> decisions, binary-artifact propagation, human resourcing, and outcome evidence pending.**
