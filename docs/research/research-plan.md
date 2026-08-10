# Research Plan

Status (2026-07-30): working successor architecture for the 2026-08-05
supervisor decision. It is not an approved supervisor decision until recorded
in the decision/change log. The complete control package is indexed in
`docs/research/phd-proposal/README.md`.

## Topic

Reusable human judgment in agentic AI assessment of domain-specific artifacts
and processes.

## Main Research Question

**U-RQ:** How can human judgment be captured, governed, and used to support
agentic-AI-driven variability exploration in guideline operationalization
scenarios, enabling reliable human–AI co-reasoning?

**2026-08-10 status note:** this wording was refined live during the 2026-08-05
supervisor call (Iris Reinhartz-Berger and Arnon Sturm), replacing the 2026-07-30
working draft below. It is **provisional working wording, not supervisor-approved**
— sign-off is tracked as decision `D-RQ-01` in
`docs/research/phd-proposal/2026-08-05-rq-decision-pack.md` and remains `Pending`
until Ali verifies the exact text against his own saved working draft from the call
and a supervisor decision is logged. Evidence, with caveats, is in
`docs/research/meetings/2026-08-05-supervisor-meeting.md` (items E5-E10) and
`docs/research/meetings/2026-08-05-supervisor-provenance-manifest.md`; the canonical
working hierarchy is also recorded in
`docs/research/phd-proposal/legacy-rq-crosswalk.md` §1.

*Prior working draft (2026-07-30, superseded above pending sign-off):* "How can
reusable human judgment be captured, governed, and reused in agentic AI assessment
of domain-specific artifacts and processes to support auditable, reliable, and
transferable human-AI co-reasoning?" This exact wording remains unchanged, as the
intentional pre-call snapshot, in
`docs/research/phd-proposal/2026-08-05-rq-decision-pack.md`.

## Contribution Statement

This research contributes a domain-neutral human-AI co-reasoning framework in
which human judgment is selectively requested, structurally captured,
validated and reconciled, stored with provenance, reused transparently, and
evaluated under explicit evidence gates. VEGO-AI software/modeling evidence is
the common core. A medical transfer is conditional Plan A evidence, never the
sole basis of the doctorate.

## Core Problem

Domain models can differ in many ways, but not every difference matters. VEGO-AI already provides a multi-agent pipeline for identifying candidate variability. The research gap is that expert judgment is often treated as a one-time correction rather than a reusable research and system asset.

This project studies how human review can move from episodic validation to reusable knowledge: uncertain or important AI classifications are routed to a human, the decision is captured in a structured schema, and approved judgments become transparent memory that can later support variability interpretation.

## Design-Science Framing

| Element | VEGO-AI Framing |
| --- | --- |
| Problem | Agentic assessment needs expert judgment, but one-off review neither scales nor accumulates governed knowledge. |
| Gap | Existing human-in-the-loop and XAI work often explains or corrects individual decisions without preserving reusable, provenance-rich domain judgment. This gap remains a working proposition until the systematic literature search tests it. |
| Artifact | Domain-neutral H-layer: selective-intervention policy, structured-feedback lifecycle, conflict and authority controls, and reusable human-judgment memory. |
| Mechanisms | Trigger review selectively, capture decisions structurally, preserve provenance, detect conflicts, retrieve prior judgments with explainable matching, and present them as advisory evidence before behavior-changing reuse. |
| Evaluation path | Compare staged intervention and judgment-reuse conditions using assessment quality, consistency, traceability, expert effort, reliability, conflict handling, and validity threats. Accuracy or generalization results remain blocked until real expert labels and the registered evidence gates exist. |

## Research Questions

**2026-08-10 status note:** the Question column below was refined live during the
2026-08-05 supervisor call (Iris Reinhartz-Berger and Arnon Sturm) from the
2026-07-30 working draft. This is **provisional working wording, not
supervisor-approved** — sign-off is tracked as decision `D-RQ-02` in
`docs/research/phd-proposal/2026-08-05-rq-decision-pack.md` and remains `Pending`
until Ali verifies the exact text against his own saved working draft from the call
and a supervisor decision is logged. SQ3 in particular changed from a "to what
extent" outcome-measurement framing to a "how can ... be reused and transferred"
design framing; the Study and evidence path column is unchanged and still applies.
Evidence, with caveats, is in
`docs/research/meetings/2026-08-05-supervisor-meeting.md` (items E5-E10) and
`docs/research/meetings/2026-08-05-supervisor-provenance-manifest.md`.

| ID | Question | Study and evidence path |
| --- | --- | --- |
| SQ1 | When and how, in variability exploration scenarios, should an agentic assessment system request human judgment so that important uncertainties are addressed without unnecessary expert burden? | Study 1: event/trigger analysis, intervention-policy comparison, offline conformance testing, and existing VEGO-AI model cases. |
| SQ2 | How should expert judgment — including the system's core reasoning — be represented, validated, reconciled, and stored so it can be reused transparently without unsafe generalization or loss of human authority? | Study 2: structured-feedback cases, provenance/conflict tests, expert review, and safe memory-retrieval/reuse analysis. |
| SQ3 | How can expert judgment be reused and transferred across different guideline-operationalization contexts without unsafe generalization or loss of human authority, first in software/modeling and, when governance and access permit, in healthcare? | Study 3: controlled comparisons, real expert labels, paired outcomes, workload/usability evidence, and external replication. Plan B completes this in software/modeling; Plan A may add a gated medical transfer pilot. |

*Prior working draft (2026-07-30, superseded above pending sign-off):* SQ1 "When
and how should an agentic assessment system request human judgment so that
important uncertainties are addressed without unnecessary expert burden?"; SQ2 "How
should expert judgments be represented, validated, reconciled, and stored so they
can be reused transparently without unsafe generalization or loss of human
authority?"; SQ3 "To what extent does the resulting framework improve assessment
quality, consistency, traceability, and expert effort across domains, first in
software/modeling and, when governance and access permit, in healthcare?" This
exact wording remains unchanged, as the intentional pre-call snapshot, in
`docs/research/phd-proposal/2026-08-05-rq-decision-pack.md`.

All former RQ, SQ, P-RQ, and MV-RQ identifiers are retained with explicit
dispositions in `docs/research/phd-proposal/legacy-rq-crosswalk.md`. They are
not parallel active hierarchies.

## Current Mechanism State

| Milestone | Mechanism | Status | Boundary |
| --- | --- | --- | --- |
| M1 | Human Review Queue | Implemented | Selects cases for review; does not decide them. |
| M2 | Human Feedback Manager | Implemented | Attaches validated human feedback to review items. |
| M3 | Human Judgment Memory | Implemented and published | Builds and searches reusable memory; remains inert. |
| M4A | Memory Advisory Layer | Implemented and published | Retrieves relevant memory for Agent 4 patterns and emits advisory reports; no AI classification change. |
| M4B-1 | Memory-informed parallel comparison | Implemented and merged | Deterministic controlled experiment only; writes a separate comparison artifact and keeps baseline behavior unchanged. |
| M4B-2 | Optional Agent 4/LLM reclassification | Deferred | Not approved; no Agent 4 prompt/API/embedding changes. |
| M5 | Human-approved guideline refinement | Planned PhD continuation | Future work; guideline changes require explicit approval and real-label evidence. |
| M6 | Broader evaluation and thesis synthesis | Planned PhD continuation | Consolidates evidence across additional runs, reviewers, domains, and diagrams. |

## Current Artifacts

- Source package: `VEGO-AI/`
- M1-M4B-1 human-AI co-reasoning implementation, comparison tooling, dashboards, and tests.
- Research OS registers for artifact audit, provenance, and publishability.
- Thesis drafts under `thesis/chapters/`, including a guarded Chapter 7 current-evidence draft.
- PhD control page: `docs/research/phd-thesis-optimization-plan.md`.
- Active doctoral execution package:
  `docs/research/phd-proposal/README.md`.
- Medical/data controls: `docs/research/governance/README.md`.
- Supervisor EXP-005 approval pack: `docs/research/supervisor-label-approval-pack.md`.
- Controlled local artifacts including root paper/IRB material, model files, analysis outputs, and evaluation outputs remain ignored until audit.

## Near-Term Milestones

1. Complete and review the 2026-08-05 RQ decision pack, three-study contract,
   Plan A/B comparison, literature workbook, bounded MIMIC audit, and
   supervisor pre-read by 2026-08-04 18:00 Asia/Jerusalem.
2. Record supervisor decisions within one working day; do not rewrite a working
   recommendation as approval.
3. Execute the reproducible literature search and first screening pass by
   2026-08-12, then connect every supported gap to a study and contribution.
4. Preserve the EXP-005 campaign at 0/24 until real independent labels are
   supplied under its approved protocol. Only then run the downstream
   evaluation and claim checks.
5. Run the medical go/no-go on 2026-08-26. Any unproven critical gate defaults
   the September proposal to Plan B and leaves Plan A as a conditional annex.
6. Converge proposal versions against the provisional September/October
   checkpoints while the department confirms the official process and date.
7. Keep M4B-1.1, M4B-2, Agent 4 behavior changes, online LLM/API processing of
   restricted data, embeddings, and baseline overwrites blocked until their
   separate evidence and approval gates pass.
