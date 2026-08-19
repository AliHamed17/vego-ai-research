# Chapter 4 — Research Methodology

> **Status:** Internal working draft prepared by Ali on 2026-08-15 and revised on 2026-08-19.
> It was prepared in advance of the literature-review sequencing gate to reduce later drafting
> risk. It was not initiated, approved, or signed off by the 2026-08-12 supervisor meeting. All
> research-question wording, artifact choices, study boundaries, and evidence-admissibility rules
> remain recommendations pending Iris Reinhartz-Berger and Arnon Sturm's review. The controlling
> reconciliation rule for this revision is `artifact-layer-contract.md`: each study has one primary
> research artifact, a supporting implementation bundle, and a separate evaluation package.

---

## 4.1 Methodological stance

This research programme follows design science research. Its object of study is a governed
mechanism for introducing, recording, controlling, and reusing human judgment inside an agentic
assessment pipeline. The programme therefore combines two linked questions for each study:

1. **Design problem:** what artifact should be constructed to address the identified problem?
2. **Knowledge question:** under what conditions does the artifact satisfy its stated requirements,
   and what effect, if any, does its use have in the intended context?

Peffers, Tuunanen, Rothenberger and Chatterjee's design science research methodology supplies the
six-activity process: problem identification and motivation, definition of objectives, design and
development, demonstration, evaluation, and communication. Wieringa's design-science methodology
supplies the engineering-cycle vocabulary used below: problem investigation, treatment design,
treatment validation, treatment implementation, and implementation evaluation, nested within an
iterative design cycle. The two frameworks are complementary. Peffers gives a recognizable
proposal-level process; Wieringa gives the artifact-in-context distinction required to separate an
internally coherent instrument from an empirically useful treatment.

The methodological baseline is the group's MODELS 2026 accepted/program-listed foundation paper,
*Not All Differences Matter: Variability Exploration of Domain Models via Agentic AI*, together
with its corresponding implementation snapshot. The supplied manuscript is a template/anonymized
working copy rather than a final proceedings version, so this chapter does not assert a final DOI,
final pagination, or completed publication status.

### 4.1.1 Three evidence levels

Every study separates three levels of evidence:

| Evidence level | What it can establish | What it cannot establish by itself |
| --- | --- | --- |
| **Artifact/mechanism evidence** | The artifact exists, is inspectable, and behaves according to a stated mechanism on controlled inputs | Accuracy improvement, generalization, burden reduction, or safe transfer |
| **Instrument/conformance evidence** | A specification is internally consistent, independently applicable, reconstructable, and capable of rejecting named violations | That using the instrument improves outcomes or that its decisions are substantively correct |
| **Outcome/effect evidence** | Comparative performance, burden, safety, and boundary conditions under a frozen empirical protocol | Unbounded generalization beyond the studied population, context, and governance conditions |

This distinction is binding throughout the chapter. Instrument evidence may be produced before an
outcome study only if it is reported explicitly as instrument evidence. It does not bypass the
EXP-005 quality gate.

## 4.2 Evaluation contexts and sequencing

Each study is designed for guideline-operationalization scenarios in two possible settings:

- **Plan B — software/modeling baseline and guaranteed completion path.** Student UML domain
  models are assessed against modeling-language and domain guidelines. A second authorized
  software/modeling context supplies the replication or transfer setting.
- **Plan A — conditional medical extension.** Clinical records may be assessed against care
  guidelines only after the relevant access, ethics, privacy, local-expert, data, infrastructure,
  and protocol gates pass.

The two paths are not symmetric at proposal stage. Plan B is complete and sufficient for every
research question. Plan A is a conditional external-validity extension and is not required for the
doctoral programme to remain scientifically coherent.

The current software/modeling evidence also has a version-bound count discrepancy that must remain
visible. The foundation manuscript reports **26 variability patterns**: 8 substantial and 18
occasional. The supplied implementation snapshot contains **27 pattern files**: 9 substantial and
18 occasional. The additional substantial pattern is localized to the ParkWise use-case setting,
but the exact export/version explanation is unresolved. This chapter therefore refers to the
*manuscript's 26 reported patterns and the snapshot's 27 pattern files* rather than treating either
count as independently reproduced.

The medical entry gates `G1`–`G6` remain 0/6. The 2026-08-26 checkpoint is an internal project-control
date, not a university deadline and not a claim of supervisor approval. Until a recorded decision
changes that state, each study is written Plan-B-first. A medical instantiation appears only as a
conditional extension after the software/modeling design is complete.

## 4.3 Layered artifact architecture

Earlier proposal artifacts used *research artifact* to mean both a narrow scientific contribution
and the full engineering/evaluation package. This chapter resolves that conflict with three layers.

| Layer | Role |
| --- | --- |
| **Primary research artifact** | The smallest system-independent artifact carrying the study's generalizable design claim |
| **Supporting implementation bundle** | The VEGO-AI components, schemas, policies, receipts, and interfaces needed to instantiate the primary artifact |
| **Evaluation package** | The comparators, independent evidence, outcomes, leakage controls, analysis, and failure criteria needed to answer the knowledge question |

The canonical mapping is:

| Study | Primary research artifact | Supporting implementation bundle | Evaluation package |
| --- | --- | --- | --- |
| **Study 1 / SQ1** | Attention-budget review-policy model | Event catalog, proposed multi-signal scoring, Human Review Orchestrator, routing modes, queue/timeout rules, burden budget, trigger and routing receipts | Analytical validation followed by held-out policy comparison with expert-time and important-case outcomes |
| **Study 2 / SQ2** | Normative governed-judgment contract | Judgment Object, Contestable Store, reconciliation, lifecycle, authority, provenance, visibility, revocation, retrieval/use history, and receipts | Conformance/reconstructability first, then comparator-based usability and governance-effect evaluation |
| **Study 3 / SQ3** | Transfer-eligibility decision procedure and target-context descriptor | Retrieval Advisor, authorization pre-filter, applicability engine, permission filter, context schema, transfer classifier, advisory-use and outcome receipts | Rater reliability first, then frozen-store held-out target evaluation against a matched no-reuse arm |
| **Integrated U-RQ** | End-to-end governed human-judgment lifecycle and operational definition of reliable co-reasoning | Integrated Study 1–3 bundles | Human-only, AI-only, ordinary non-governed HITL, and governed VEGO-AI comparison |

This layering preserves the literature review's broader architecture without presenting a six- or
ten-component bundle as one indivisible scientific contribution. The primary artifact defines the
claim boundary; the supporting bundle makes it executable; the evaluation package determines
whether the claim survives empirical testing.

## 4.4 Study 1 — Selective intervention under bounded attention (SQ1)

### 4.4.1 Design problem and artifact

Study 1 asks when an agentic assessment system should request human judgment and how the request
should be delivered under bounded expert attention. Asking on every case is not scalable and can
create interruption, delay, and review fatigue. Asking only when a model reports low confidence is
also insufficient because high-confidence decisions may have high consequences, weak evidence, or
cross-agent disagreement.

The **primary research artifact** is an attention-budget review-policy model. It relates a trigger
configuration to four distinct outputs:

1. number of items sent to review;
2. estimated or observed cost of those reviews;
3. coverage of offline uncertainty/instability candidates; and
4. later, coverage of independently established important cases.

The **supporting implementation bundle** is the selective-intervention architecture already
anticipated elsewhere in the project: event/listener catalog, eligibility and priority signals,
Human Review Orchestrator, routing modes, queue and timeout rules, claim-specific reviewer routing,
burden budget, and reproducible trigger/routing receipts.

### 4.4.2 Proposed trigger representation

For an assessment event `e`, let `x(e)` be a proposed feature vector containing only signals that
can be produced reproducibly and attached to the event receipt. Candidate features include:

- calibrated or semantic uncertainty;
- cross-agent or cross-run disagreement;
- novelty or guideline-coverage weakness;
- consequence or policy importance;
- evidence completeness/quality;
- expected reuse value;
- queue state, reviewer availability, and estimated review cost.

The foundation paper and current pipeline do not establish that this complete vector already
exists per event. It is therefore a **proposed study representation**, to be implemented from
available signals and augmented only through versioned, testable features. No feature is described
as computed by the existing pipeline unless a repository receipt demonstrates it.

A policy configuration `θ` maps `x(e)` and the current attention state to a binary review decision
`Iθ(e) ∈ {0,1}`, an intervention mode, and a reviewer route. Four existing replay modes are useful
reference points, but they are not the complete artifact:

- `every_decision`: route every eligible event;
- `threshold(τ)`: route events satisfying a versioned score threshold;
- `top_n_then_auto(N)`: route the top `N` ranked events per declared window. The existing
  experiment name `first_n_then_auto` is retained in experiment citations, but the analytical
  model uses `top_n_then_auto` because the proposed rule is score-ranked rather than arrival-order;
- `silent`: route no item to a reviewer;
- `audit_sample(p)`: sample at rate `p` for a separate audit process.

`audit_sample(p)` is kept separate from `silent` because an audit that requires a person creates
human workload even when it does not interrupt the live decision.

### 4.4.3 Output quantities

Let `Ew` be the events in a defined evaluation window.

**Review count**

```text
ReviewCount(θ) = Σe∈Ew Iθ(e)
```

**Review cost**

```text
ReviewCost(θ) = Σe∈Ew Iθ(e) · ce
```

where `ce` is either observed review time/cost or a preregistered proxy. Until real review-time data
exist, routed-event count and estimated cost must be reported separately; neither may be called
expert-effort reduction.

**Candidate coverage**

```text
CandidateCoverage(θ) = (Σe∈Ew ze · Iθ(e)) / (Σe∈Ew ze)
```

where `ze = 1` marks an offline instability, uncertainty, or replay-defined candidate. EXP-006,
EXP-007, and EXP-008 can support this measure at mechanism/observability scope.

**Important-case coverage**

```text
ImportantCaseCoverage(θ) = (Σe∈Ew we · ye · Iθ(e)) / (Σe∈Ew we · ye)
```

where `ye` is an independent, adjudicated indication that the event required qualified review and
`we` is a preregistered consequence weight. This measure cannot be computed as an outcome claim
while the required independent labels are absent.

The analytical target is a multi-objective frontier over review count, review cost, candidate
coverage, and—when gated evidence exists—important-case coverage and selective risk. A policy is
not preferred merely because it routes fewer cases.

### 4.4.4 Phase A — artifact and mechanism validation

Phase A examines whether the model and implementation are coherent before any effectiveness claim.
It includes:

- schema and receipt completeness;
- deterministic reconstruction of each trigger decision;
- boundary tests for zero-review and all-review configurations;
- degenerate-case tests such as `top_n_then_auto(N=0)`;
- threshold behavior using a threshold strictly above the maximum observed score for a zero-review
  boundary, rather than assuming `τ → 1` is silent when a score can equal 1;
- monotonicity only within a nested policy family, such as increasing `N` or decreasing a fixed
  threshold. Monotonicity is not assumed across unrelated modes;
- detection of dominated configurations;
- explicit separation of live-review load from audit load.

EXP-006–EXP-008 may be used here as already-run event, replay, and candidate evidence. They remain
mechanism and observability evidence. EXP-007's routed-item counts are not human-effort results and
do not select a default policy.

### 4.4.5 Phase B — research-question effect evaluation

Phase B answers the knowledge question using held-out cases and independent outcome evidence.
Comparators are:

- never ask;
- always ask;
- random review at a matched budget;
- uncertainty-only review;
- fixed threshold;
- the proposed multi-signal attention-budget policy.

The unit of analysis is a case, fragment, guideline mapping, or pattern decision assigned under a
frozen policy. Primary outcomes are important-case capture or joint correctness at a stated expert
attention budget, with selective risk reported for autonomous decisions. Secondary outcomes include
review yield, expert minutes, interruption count, queue delay, abandonment, reviewer-role balance,
override behavior, and reusable-judgment yield.

The policy is falsified or narrowed if it does not improve the preregistered objective over a
simpler baseline, misses high-consequence cases above the allowed threshold, produces unacceptable
burden or queue delay, or appears beneficial only after post-hoc threshold tuning.

### 4.4.6 Contexts, dependencies, and fallback

Plan B supplies the complete software/modeling evaluation. A medical workflow may later stress-test
the trigger ontology only after local experts and governance permit it; no clinical effect claim
follows from transferring the policy structure.

Study 1 can produce Phase A evidence without EXP-005. Phase B quality claims require independent
labels, frozen policies, and an analysis plan. If those data are unavailable, the defensible output
is the inspectable model, supporting implementation, analytical/replay results, explicit unresolved
properties, and a preregistered empirical protocol—not a claim of burden or accuracy improvement.

## 4.5 Study 2 — Governed judgment representation and lifecycle (SQ2)

### 4.5.1 Design problem and artifact

Study 2 asks how expert judgment, including the inspectable reasoning presented by the system, can
be represented, validated, reconciled, stored, contested, and governed for later use. A final label
alone is insufficient because it does not preserve what claim was judged, which evidence and rule
were inspected, what authority the reviewer had, where the judgment applies, or why it later became
invalid.

The **primary research artifact** is a normative governed-judgment contract with executable
conformance requirements. VEGO-AI is one reference implementation; the contract is intended to be
system-independent.

The **supporting implementation bundle** includes the Governed Judgment Object, Contestable
Judgment Store, validation and reconciliation services, lifecycle enforcement, claim-specific
authority and visibility controls, provenance, expiry/revocation, retrieval/use history, and
machine-readable receipts.

### 4.5.2 Minimum contract

The contract classifies fields as mandatory core, mandatory when a condition applies, or extension
fields. The minimum groups are:

| Group | Required content |
| --- | --- |
| **Stable identity and case grounding** | Judgment ID; artifact, case, fragment/pattern, guideline and version; domain, modeling language, task, source version, observed deviation, and evidence locator |
| **Inspectable system decision trace** | Claim, confidence/calibration state, cited evidence, rule/guideline applied, alternatives considered, uncertainty source, and decisive inference exactly as displayed to the reviewer |
| **Human judgment** | Verdict, structured or free-text rationale, reasoning-level correction, counter-evidence, counterexamples, exclusions, and reviewer uncertainty |
| **Scope and transfer semantics** | Claim type; allowed contexts; hard exclusions; exact-match dimensions; adaptable dimensions and tolerances; ranking-only dimensions; known counterexamples; maximum transfer level |
| **Authority, visibility, and privacy** | Reviewer identity or protected participant code, role, competence basis, authorization level, advisory/binding policy, visibility class, consent/permission state, privacy classification, and access restrictions |
| **Validation and disagreement** | Validation tier, second-review requirement, conflict type, competing judgments, adjudication policy/version, adjudicator where applicable, and unresolved state |
| **Provenance and versioning** | Creator, modifiers, timestamps, source/model/prompt/policy versions, prior-version link, supersession pointer, and derivation chain |
| **Lifecycle** | Effective date, review date, expiry, revocation reason, replacement pointer, and enforceable lifecycle state |
| **Retrieval, use, and outcome history** | Retrieval queries/receipts, permission decisions, actual advisory use, influence on the current decision, human override, downstream outcome, incident, and later revocation impact |

The phrase *system reasoning* does not authorize storage of hidden chain-of-thought. The contract
stores the shortest sufficient **inspectable decision trace** that lets an authorized reviewer
identify the claim, evidence, rule, alternatives, uncertainty, and correction. It excludes opaque
private reasoning, unnecessary personal data, and unbounded transcripts.

### 4.5.3 Orthogonal status dimensions

A single flat state such as `Contested` cannot safely represent the record. The contract uses
orthogonal dimensions:

- `lifecycle_status`: `Draft`, `Active`, `Superseded`, `Expired`, `Revoked`;
- `validation_status`: `Unreviewed`, `Reviewed`, `Adjudicated`;
- `contestation_status`: `Uncontested`, `Contested`, `Resolved`.

For example, an active judgment can be contested without becoming invisible, while a superseded
judgment remains historically auditable. Every transition has a permitted predecessor, actor,
reason, timestamp, and receipt.

### 4.5.4 Authority and advisory-use default

The default contract rule is:

```text
advisory_only = true
```

A judgment may not silently bind a later automated decision. Binding effect requires a separate,
versioned policy authorization specifying the claim type, context, authority, effective period,
rollback rule, and outcome-monitoring obligation. Every authorized binding use produces a policy
receipt. This preserves the literature review's principle that retrieval is evidence access, not
permission or truth.

### 4.5.5 Phase A — specification and conformance validation

The executable conformance suite includes positive, negative, and boundary fixtures for every
invariant. At minimum it tests:

- valid record construction and deterministic serialization;
- blind reconstructability by a reviewer who did not participate in the original judgment;
- missing or ambiguous scope;
- invalid or insufficient authority;
- broken provenance or unresolved evidence locator;
- illegal lifecycle transition;
- a revoked or expired record remaining retrievable as active advice;
- missing privacy or visibility control;
- incompatible schema/policy version;
- supersession without a replacement pointer;
- dissent erased during adjudication;
- binding use without a separate policy authorization;
- a target-context use written into the source record without a versioned SQ2 transition.

A deliberately broken implementation must fail with a predictable, named reason code. One broken
variant is not sufficient for the complete claim; coverage is measured against the declared
invariants and fixture matrix.

The existing EXP-013–EXP-018 series can be cited only as reference-implementation conformance
precedent for the properties it directly tests. It does not establish that an independent
implementation conforms or that governed records improve outcomes.

### 4.5.6 Phase B — representation and governance effect evaluation

Phase B compares:

- label-only capture;
- unstructured comment capture;
- the governed-judgment contract and supporting lifecycle.

Units of analysis are review episodes and subsequent authorized audit/reuse tasks. Primary outcomes
include reconstruction accuracy, correction quality, contestability, audit completeness, and
scope/authority error. Secondary outcomes include completion time, reviewer workload, missing-field
rate, unresolved disagreement, privacy/visibility violations, revocation effectiveness, and user
comprehension.

The artifact is falsified or narrowed if reviewers cannot reconstruct or use the record reliably,
if the governed representation produces no benefit over a simpler record at comparable burden, if
scope/authority violations persist, or if governance cost exceeds the preregistered benefit.

### 4.5.7 Independence, ethics, and fallback

Implementation-independence requires a person who did not design the contract to implement or run
a variant against the specification. A critical reviewer alone can support design review but cannot
substitute for an independent implementation claim. The role is not yet assigned.

Before recruiting a participant or collecting study data, the project must obtain the applicable
institutional ethics/IRB determination and data-access approval. Participant names must not be
stored in a public repository without permission; coded identifiers should be used in research
data where appropriate.

If no independent implementer or human-effect evaluation is available, the fallback is to report
the contract, reference implementation, fixture coverage, and implementation-independence gap. No
safe-reuse or improved-outcome claim follows.

## 4.6 Study 3 — Transfer eligibility and target-context evaluation (SQ3)

### 4.6.1 Design problem and artifact

Study 3 asks whether a governed source judgment is eligible to inform a decision in a described
target context, with what adaptation, under what authority, and with what observed target effect.
Semantic similarity alone is insufficient because a seemingly similar case may differ in domain,
task, guideline version, institution, population, representation, risk, or permission.

The **primary research artifact** is a transfer-eligibility decision procedure paired with a
target-context descriptor.

The **supporting implementation bundle** includes the Scope-Aware Retrieval Advisor, visibility and
authorization pre-filter, applicability engine, permission filter, transfer-distance classifier,
context schema, advisory evidence presentation, and retrieval/permission/use/outcome receipts.

### 4.6.2 Inputs

The procedure takes:

1. a source judgment conforming to the Study 2 contract; and
2. a target-context descriptor containing at least:
   - domain and task;
   - modeling language or representation type;
   - artifact and fragment/pattern type;
   - guideline family and exact version;
   - institution, population, and jurisdiction;
   - source and target model/prompt/policy versions;
   - risk/consequence class;
   - required reviewer/organizational authority;
   - data-access, visibility, privacy, and consent class;
   - evidence provenance and completeness;
   - elapsed time since the source judgment;
   - known exclusions and counterexamples.

The source scope distinguishes four classes of dimensions:

- **hard exclusions:** a mismatch prohibits use;
- **exact-match dimensions:** a mismatch blocks the current eligibility path unless the source
  judgment is revised through Study 2;
- **adaptable dimensions:** a mismatch may be addressed by a named, predefined adaptation;
- **ranking-only dimensions:** influence retrieval priority but never grant permission.

### 4.6.3 Decision order

The procedure runs in a fixed order:

1. **Visibility and authorization pre-filter.** Before restricted evidence is exposed, confirm that
   the requester and environment may access the record and that no revocation, expiry, or policy
   prohibition applies.
2. **Relevance.** Determine whether the record addresses the same claim type and whether the target
   provides the required evidence signature.
3. **Applicability.** Compare exact-match and adaptable dimensions; calculate and record every
   mismatch rather than reducing the decision to one similarity score.
4. **Adaptation selection.** Apply only a named, versioned adaptation, such as local-reviewer
   reconfirmation or guideline-version delta review.
5. **Eligibility verdict and reason code.** Produce one of the states below.
6. **Advisory presentation and local re-reasoning.** The current agent/reviewer evaluates current
   evidence; the prior judgment does not replace the current case analysis.
7. **Outcome logging.** Record influence, override, target outcome, burden, incident, and any later
   revocation consequence.

### 4.6.4 Decision states

| State | Definition |
| --- | --- |
| `Eligible` | All required authorization, visibility, exact-match, and tolerance conditions pass; the judgment may be presented as advisory evidence |
| `EligibleWithAdaptation` | No hard prohibition applies, but one or more adaptable dimensions require a named adaptation before advisory use |
| `Blocked` | An explicit hard exclusion, authorization/visibility failure, revocation/expiry rule, exact-match failure, or distance beyond defined adaptation capacity applies |
| `Undetermined` | Required evidence, tolerance, authority, or policy is missing or conflicting; the item must be escalated for independent review rather than treated as permanently prohibited |

Every state carries the driving dimension, reason code, policy version, evidence completeness, and
required next action. `Undetermined` prevents missing evidence from being misreported as either safe
eligibility or a permanent block.

### 4.6.5 Phase A — procedure reliability

Two trained raters independently apply the frozen procedure to the same source-target pairs.
Before data collection, the protocol fixes:

- source-target pair selection and sample size rationale;
- rater eligibility and independence;
- training and calibration examples that are not part of the scored set;
- blind, randomized case order;
- primary agreement statistic: Cohen's `κ` for the nominal verdict when two raters are used;
- agreement on the driving reason/dimension as a separate outcome;
- confidence interval method;
- treatment of missing and `Undetermined` cases;
- the rule that adjudication occurs only after independent ratings are frozen.

Agreement establishes that the procedure can be applied consistently. It does not establish that
its verdicts are substantively correct, beneficial, or safe.

### 4.6.6 Phase B — transfer effect evaluation

The source store, retrieval policy, permission policy, guideline versions, thresholds, and source
judgments are frozen before target scoring. Held-out target cases are compared under:

- a matched no-reuse control using the same current evidence; and
- the scope-filtered advisory-reuse condition.

Independent target labels are created blind to the reused judgment and system recommendation.
Primary outcomes are target benefit and unsafe-transfer rate. Secondary outcomes include scope
violations, calibration under shift, expert burden, override behavior, benefit by transfer level,
blocked/undetermined reasons, and revocation responsiveness.

The procedure is falsified or narrowed if there is no target benefit, if unsafe-transfer or scope
violations exceed the predefined threshold, if the effect disappears under blinding/frozen-store
controls, if permission failures occur, or if benefit is explained only by additional human time.

### 4.6.7 Contexts, dependencies, and fallback

Plan B tests transfer across an authorized second software/modeling context, institution, dataset,
diagram family, reviewer panel, or time period. Plan A may test a medical context only after every
applicable entry and downstream control passes. No software/modeling result licenses a clinical
performance or deployment claim.

Study 3 requires the Study 2 source contract, an authorized target context, two independent raters
for Phase A, and independent target evidence for Phase B. If these are unavailable, the study may
report readiness, procedure design, and the exact block only.

## 4.7 Integrated evaluation of the umbrella research question

Completing the three studies independently does not by itself establish reliable human-AI
co-reasoning. The umbrella question requires an end-to-end integration test.

### 4.7.1 Unit, intervention, and comparators

The unit of analysis is a complete governed assessment episode:

```text
detect → triage → request → capture → validate/reconcile → store → retrieve/filter
→ apply as advice → monitor → expire/supersede/revoke
```

The intervention is the integrated governed VEGO-AI lifecycle under frozen policies. It is compared
with:

1. **AI-only:** the agentic assessment pipeline without human judgment;
2. **human-only:** authorized human assessment without VEGO-AI advice;
3. **ordinary non-governed HITL:** human correction or approval without the full selective,
   provenance, scope, lifecycle, and outcome controls;
4. **governed VEGO-AI:** the integrated Study 1–3 lifecycle.

### 4.7.2 Outcomes

The primary outcome is complementary team performance at a controlled attention budget. It must be
operationalized for the chosen task before data collection, not inferred from the presence of a
human or from system accuracy alone.

Secondary outcome families are:

- correctness/selective risk and calibration;
- expert time, interruptions, queue delay, and review yield;
- authority and visibility compliance;
- reconstruction, traceability, and audit completeness;
- contestation, adjudication, supersession, and revocation effectiveness;
- overreliance, underuse, and override quality;
- propagation errors, scope violations, and unsafe reuse;
- performance by reviewer role, case type, and transfer distance.

### 4.7.3 Success and failure interpretation

The integrated hypothesis is supported only if governed VEGO-AI improves the preregistered joint
objective over the relevant baselines while satisfying burden, authority, contestability,
traceability, and propagation-safety thresholds.

It is rejected or narrowed if:

- any load-bearing study artifact fails its own validity requirement;
- the integrated system introduces new propagation or authority errors;
- apparent gain is explained only by additional human time;
- ordinary non-governed HITL performs equivalently with lower cost;
- calibration or selective risk deteriorates;
- benefit depends on leakage, post-hoc tuning, or unblinded labels;
- the result fails to replicate in the authorized Plan B context.

A valid negative result may establish where judgment should not be requested, stored, or reused.

## 4.8 Evidence boundary and current state

Nothing in this chapter asserts accuracy improvement, generalization, effort reduction, safe
transfer, or clinical performance. Current hard gates are:

| Gate | Current state | Consequence |
| --- | ---: | --- |
| EXP-005 generalization-safe expert labels | **0/24** | No positive quality/generalization/effect claim |
| Medical entry gates `G1`–`G6` | **0/6** | No medical empirical or deployment claim |
| Formal literature searches `QL-01`–`QL-05` | **0/5** | No exhaustive-search or absence-of-prior-work claim |

EXP-006–EXP-008 provide already-run event, replay, and instability-candidate evidence. EXP-013–EXP-018
provide already-run reference-implementation conformance evidence. Each remains bounded to the
scope of its own protocol. EXP-009 and EXP-010 remain excluded from proposal evidence until `M-04`
protocol approval is recorded, unless Iris and Arnon explicitly decide otherwise.

## 4.9 Open decisions and real-world dependencies

The chapter is now internally specified, but it is not supervisor-approved. The four decisions in
`2026-08-19-chapter4-decisions-packet.md` remain open:

1. confirm or correct the three-layer artifact model;
2. confirm or correct the SQ2/SQ3 ownership boundary;
3. decide whether instrument evidence may be reported before EXP-005, under the stated restriction;
4. decide whether EXP-009/EXP-010 remain completely outside the proposal until `M-04`.

A separate housekeeping confirmation is requested for the exact Chapter 5 wording used for
EXP-006/007/008.

The following are real-world dependencies, not drafting gaps:

- an independent Study 2 implementer;
- two independent Study 3 raters;
- applicable ethics/IRB and data-access determinations before participant recruitment or study-data
  collection;
- the independent EXP-005 labels and adjudication process;
- an authorized Plan B target context;
- any Plan A partner, expert, governance, infrastructure, and approval evidence.

The recruitment controls and separate draft messages are in
`docs/operations/study-resourcing-request-template.md`. No person is considered committed until the
agreement is recorded through the approved project process. Until the decisions and dependencies
are resolved, the defensible status is:

> **Chapter 4 internal methodology review draft — artifact specifications defined; supervisor
> decisions, cross-artifact propagation, human resourcing, and outcome evidence pending.**
