# Reusable Human Judgment for Auditable, Reliable, and Transferable Agentic AI Assessment

Proposal version: 0.2 working draft - controlled delta from v0.1

Prepared by: Ali

Date: 1 August 2026

Status: **WORKING DRAFT - NOT SUPERVISOR-APPROVED, NOT SHARED, AND NOT A SUBMISSION CANDIDATE**

This document advances proposal writing while preserving every unresolved
decision and evidence gate. It is read with [proposal v0.1](./proposal-v0.1.md),
the [RQ decision pack](./2026-08-05-rq-decision-pack.md), and the
[three-study contract](./three-study-contract.md). If the August 5 supervisors
approve corrections, their exact wording must replace the affected draft text
through the decision/change process; no decision is inferred here.

## 1. v0.2 delta and unresolved gates

| Area | Writing advance in this draft | Gate that remains open |
| --- | --- | --- |
| Problem and contribution | Links selective intervention, governed judgment reuse, and evidence-controlled transfer into one candidate contribution | Literature synthesis and supervisor adequacy judgment |
| Research architecture | Preserves one umbrella RQ and exactly three subquestions with one primary study each | D-RQ-01 through D-RQ-05 |
| Literature method | Freezes QL-01 through QL-05 and the execution evidence fields | Searches, deduplication, screening, quality appraisal, and synthesis are not run |
| Preliminary evidence | Separates established mechanisms from blocked effectiveness claims | EXP-005 remains `0/24`; exact result selection awaits supervisors |
| Plan A/B | Preserves a common software/modeling core and conditional medical transfer | Plan interpretation and fallback date await supervisor decision; medical readiness remains `0/6` |
| Administration | Adds an authoritative university inquiry interface | Inquiry is a draft, not sent; official rules and dates remain unverified |

## 2. Refined problem and candidate contribution

AI-assisted assessment under structured norms can identify candidate
differences, violations, or deviations, but context-sensitive interpretation
often remains a human responsibility. Existing workflows commonly treat that
intervention as a one-case correction. The decision may solve the immediate
case while its rationale, evidence, authority, scope, conflicts, and later use
remain weakly represented or governed.

The candidate contribution is a controlled lifecycle that connects three
problems which are often evaluated separately:

1. deciding when an assessment system should request human judgment and how to
   control timing, dosage, routing, escalation, and burden;
2. representing, validating, reconciling, storing, retrieving, and reusing that
   judgment with provenance, scope, conflict, and human-authority controls; and
3. evaluating the complete lifecycle against independent evidence, including
   its quality, consistency, traceability, effort, failure modes, and transfer
   limits.

The literature review must establish whether this combination is absent,
incomplete, or already addressed. Therefore novelty and doctoral scale remain
candidate claims, not conclusions.

## 3. Working research questions - supervisor decision pending

### Umbrella research question

**How can human judgment be captured, governed, and used to support
agentic-AI-driven variability exploration in guideline operationalization
scenarios, enabling reliable human–AI co-reasoning?**

### Exactly three subquestions

**SQ1 - Selective intervention:** When and how, in variability exploration
scenarios, should an agentic assessment system request human judgment so that
important uncertainties are addressed without unnecessary expert burden?

**SQ2 - Governed knowledge reuse:** How should expert judgment - including the
system's core reasoning — be represented, validated, reconciled, and stored so
it can be reused transparently without unsafe generalization or loss of human
authority?

**SQ3 - Evaluation and transfer:** How can expert judgment be reused and
transferred across different guideline-operationalization contexts without
unsafe generalization or loss of human authority, first in software/modeling
and, when governance and access permit, in healthcare?

This is the NEW canonical working wording, refined live during the 5 August
2026 supervisor call with Iris Reinhartz-Berger and Arnon Sturm. It supersedes
the ~30 July - 1 August working draft recorded in the
[RQ decision pack](./2026-08-05-rq-decision-pack.md), which is preserved there
unchanged as the pre-call snapshot. Evidence and caveats for this refinement
are in the
[2026-08-05 supervisor meeting record](../meetings/2026-08-05-supervisor-meeting.md)
(items E5-E10) and the
[2026-08-05 supervisor provenance manifest](../meetings/2026-08-05-supervisor-provenance-manifest.md).
This wording remains **provisional and not supervisor-approved**: D-RQ-01
(umbrella RQ wording) and D-RQ-02 (SQ1-3 wording) stay Pending until Ali
verifies the exact text against his own saved working draft from the call and
a supervisor decision is logged.

## 4. Three-study argument and evaluation contract

### Study 1 - intervention architecture

Study 1 answers SQ1 by constructing and validating a domain-neutral policy for
observing assessment events, estimating uncertainty and importance, requesting
human review, routing requests, controlling dosage, and handling timeout,
deferral, overload, and escalation. The primary evidence is requirements and
artifact conformance under controlled scenarios, followed by authorized expert
review. Architecture readiness cannot establish reduced expert burden or
improved assessment.

Planned measures include requirement coverage, trigger and routing conformance,
request completeness, dosage and escalation compliance, queue bounds, and
failure containment. The artifact is the inspectable intervention policy and
its requirements-to-validation traceability package.

### Study 2 - governed judgment lifecycle

Study 2 answers SQ2 by defining the judgment record, source validation,
conflict detection, reconciliation, authority state, provenance, retention,
retrieval, scope checking, and safe-reuse rules. Controlled tests will include
compatible, conflicting, stale, under-specified, and out-of-scope judgments.
The artifact is a governed judgment lifecycle and reuse policy that can abstain
or escalate when evidence is insufficient.

Planned measures include schema and provenance completeness, conflict-detection
coverage, reconciliation traceability, scope enforcement, safe abstention,
retrieval precision, and unsafe-reuse rate. Mechanism conformance does not by
itself establish beneficial reuse.

### Study 3 - evaluation and transfer

Study 3 answers SQ3 through blinded independent labeling, adjudication, paired
comparisons, workload/usability evidence, error analysis, validity analysis,
and a second-setting transfer study. The software/modeling baseline is required
under both plans. Plan A may add a gated medical transfer; Plan B uses an
authorized non-medical replication setting.

Planned measures include paired assessment quality, calibration, consistency,
traceability, expert time and workload, reviewer agreement, abstention and
unsafe-reuse rates, transfer degradation, and error propagation. The exact
analysis, units, thresholds, and sample-size reasoning remain protocol
placeholders until the literature synthesis, reviewer route, and supervisor
method decisions are complete.

## 5. Literature review execution delta

The first frozen search tranche is controlled by the
[QL-01 through QL-05 execution register](./literature-search-execution-register.md):

- QL-01: agentic or multi-agent AI with human oversight;
- QL-02: expert feedback, knowledge capture, memory, and reusable judgment;
- QL-03: domain modeling, assessment, variability, and conformance;
- QL-04: intervention workload, governance, trust, and evaluation; and
- QL-05: clinical guidelines, CDSS overrides, alert fatigue, and healthcare
  process mining for conditional Plan A only.

Current status is **protocol ready / not run**. No hit count, included-paper
count, novelty conclusion, contradiction synthesis, or gap conclusion is
available from this draft. The completed literature section must report the
exact queries and dates, deduplication, screening flow, exclusion reasons,
quality appraisal, taxonomy synthesis, contradictions, and a gap-to-study and
gap-to-contribution matrix.

Working synthesis placeholders:

| Literature area | What must be established | Current evidence state |
| --- | --- | --- |
| Selective oversight | Trigger, timing, dosage, authority, and workload designs | Search not run |
| Reusable expert judgment | Representation, provenance, validation, conflict, memory, and safe reuse | Search not run |
| Assessment/modeling baseline | Concrete assessment tasks, norms, variability, and conformance methods | Search not run; repository baseline exists separately |
| Human-AI evaluation | Quality, workload, usability, trust, governance, and validity designs | Search not run |
| Medical transfer | Conditional transfer constructs and governance constraints | PubMed branch not run; no clinical study approved |

## 6. Preliminary evidence and claim boundary

The proposal may use current software/modeling artifacts as bounded preliminary
evidence. It must not convert artifact existence or mechanism tests into
effectiveness claims.

| Statement | Claim state | Permitted interpretation |
| --- | --- | --- |
| A software/modeling baseline and inspectable capture, memory, advisory, and comparison mechanisms exist | Established | Mechanisms exist and can support controlled study preparation |
| The one-plus-three architecture and combined lifecycle are suitable doctoral framing | Preliminary | Working framing pending literature and supervisor review |
| The EXP-019 calibration package is ready for two human reviewers | Preliminary | Calibration only; EXP-020 evaluation release still requires two valid calibration returns and a human-frozen instruction manifest |
| Reusable judgment improves accuracy, effort, or generalization | Blocked | EXP-005 remains `0/24`; no positive result is computable |
| A second non-medical transfer study will be executed under Plan B | Planned | Context, owner, reviewers, and protocol remain to be selected |
| A medical transfer can be executed | Partner-dependent and blocked | Medical readiness remains `0/6`; no row-level work is authorized |

Negative or null empirical results remain valid outcomes if the protocol and
evidence are sound. The proposal does not depend on a positive result.

## 7. Plan A, Plan B, and the medical stop rule

### Common core

Both plans complete Study 1 and Study 2 in software/modeling and evaluate the
complete framework first in software/modeling under Study 3. Both plans answer
the same umbrella RQ and SQ1-SQ3.

### Plan A - staged medical extension

Plan A adds a bounded healthcare transfer only after all six medical gates are
evidenced: use case, people, authorization, ethics/privacy, environment, and
protocol. Medical evidence is an extension, not the sole basis of the
doctorate. MIMIC remains an exploratory metadata/schema resource; it is not the
selected dataset.

### Plan B - complete software/modeling path

Plan B completes Study 3 through an authorized second software/modeling
dataset, diagram family, task, institution, reviewer panel, or longitudinal
reuse setting. It preserves independent human evidence, construct
comparability, leakage controls, the same outcome measures, and doctoral scale
without medical data or a medical partner.

### Fallback control

The current internal control date is 26 August 2026. If any one of G1-G6 lacks
its required owner, evidence path, or feasible completion date at the
checkpoint, Plan B becomes the committed September execution path and Plan A
moves to a partner-dependent conditional extension. D-RQ-04 through D-RQ-06
must approve or correct the interpretation and date. Regardless of the route
decision, no medical row-level work begins until all six gates actually pass
and every applicable downstream authorization and integrity control passes.

## 8. Resources, ethics, and validity placeholders

### Resources that are available with limits

- the current VEGO-AI software/modeling baseline and governed mechanism
  artifacts;
- evaluation and blinded-review infrastructure, without reviewer returns;
- a private Ali-owned PhD working Drive, not supervisor-shared or access-tested;
- a native literature workbook with seed rows, not a completed review; and
- a recurring Wednesday supervisor calendar, which proves logistics only.

### Resources that remain missing or unverified

- two independent EXP-005 reviewers and an adjudicator;
- an authorized Plan B replication context and external reviewer route;
- every Plan A clinical, partner, data, ethics, privacy, and VDI role;
- an approved restricted local/offline runtime, if later required;
- official university deadlines, reviewer, committee, formatting,
  presentation, and submission rules; and
- verified Penina course dates and requirements.

### Validity structure to complete

The developed methods section must address construct validity, internal
validity, external validity, conclusion validity, reviewer independence and
agreement, selection bias, learning and carryover effects, leakage,
missingness, small samples, workload measurement, transfer comparability,
negative/null results, and researcher positionality. Each threat must map to a
design control, residual limitation, and reporting rule.

## 9. Administration and schedule

The [university inquiry](./university-process-inquiry-draft.md) is a draft and
has not been sent. The following are internal working targets until an
authoritative response is recorded:

| Date | Working output | Acceptance boundary |
| --- | --- | --- |
| 5 Aug | Supervisor decisions on RQs, studies, Plan A/B, claims, literature, MIMIC, and owners | Exact outcomes and corrections recorded; silence is deferred |
| 12 Aug | Executed first literature tranche, screening start, Penina reuse, proposal v0.2 integration, and Clalit request draft | Real search logs and review evidence; no fabricated partner or course status |
| 19 Aug | Critical synthesis, gap matrix, methods/metrics/validity, RACI/resources, and Plan B reviewer route | Every claimed gap maps to evidence and a study; missing people remain visible |
| 26 Aug | Proposal v0.3, architecture freeze, and medical go/no-go | Route recorded from the six-gate evidence; Plan B if any one of G1-G6 lacks the required control or passed evidence |
| 2 Sep | Problem, gap, RQs, and methods internally complete | Cross-document consistency and claim checks pass |
| 9 Sep | Preliminary evidence and claim-boundary section complete | `0/24` remains visible unless valid real evidence changes it |
| 16 Sep | Developed draft v0.7 | All substantive sections, resources, ethics, risks, validity, and timeline present |
| 23 Sep | Supervisor comments and process requirements resolved | Official rules cited and schedule reconciled |
| 30 Sep | Submission candidate v1.0 | References, appendices, manifests, traceability, and authorization checks pass |
| 7 Oct | Final buffer | Approval/submission/candidacy artifact only under verified official rules |

If an authoritative deadline differs, the schedule must be rebaselined within
one working day. No submission is reported without version-specific supervisor
approval, an authorized route, and a receipt.

## 10. v0.2 release criteria

This working delta may be integrated into a supervisor-facing v0.2 only after:

- [ ] D-RQ-01 through D-RQ-05 and D-RQ-07 have explicit outcomes;
- [ ] every correction is propagated without stale competing wording;
- [ ] the QL register records actual execution evidence or remains explicitly unrun;
- [ ] preliminary evidence is selected with exact versions and claim states;
- [ ] Plan B has an executable candidate context, owner, reviewer route, and schedule;
- [ ] official-process status is reported from authoritative evidence or remains visibly unverified;
- [ ] all medical and restricted-data language remains within the six-gate stop rule;
- [ ] links, tables, evidence consistency, and Markdown checks pass; and
- [ ] Ali reviews and authorizes the exact version before any external sharing.

Until these gates pass, this file is writing progress, not an approved proposal
or evidence that any external action occurred.
