# ACL-2026 Human-Agent Taxonomy → VEGO-AI Relevance Map v16

**Status:** controlled, author-generated literature-classification artifact for supervisor review.  
**Date:** 2026-08-20  
**Branch:** `docs/acl-taxonomy-v16-strict`  
**Scope:** literature structure and thesis positioning only; no VEGO-AI runtime change.

> **Evidence boundary.** This document classifies how the taxonomy in Zou et al. (2026) relates to the current VEGO-AI doctoral working questions. It is not a copy of the source figure, not an exhaustive systematic review, not a supervisor-approved taxonomy/RQ set, and not evidence that any proposed VEGO-AI mechanism is effective or safely transferable.

## 1. Why this map exists

The ACL survey provides a strong descriptive taxonomy of **LLM-based human-agent systems**. VEGO-AI needs a different but related analytical object: a problem-led map showing which source dimensions directly help explain governed human judgment in agentic variability exploration, which dimensions are only enabling context, which are outside the current thesis scope, and which thesis requirements are not first-class branches in the survey taxonomy.

The map therefore performs four operations:

1. **preserves the ACL source taxonomy;**
2. **classifies its relevance using Iris's exact scale;**
3. **adds explicitly labeled VEGO-AI dimensions where the ACL taxonomy is insufficient for the thesis problem;**
4. **connects the resulting literature structure to the current one-artifact-per-study methodology.**

## 2. Denominator and provenance control

### 2.1 Paper-level denominator

Zou et al. organize LLM-based human-agent systems around **five core aspects**:

1. Environment & Profiling
2. Human Feedback
3. Interaction Type
4. Orchestration Paradigm
5. Communication

### 2.2 Companion-repository denominator

The survey's companion GitHub repository exposes **four taxonomy navigation branches**:

1. Human Feedback
2. Interaction
3. Orchestration
4. Communication

`Environment & Profiling` remains a paper-level core aspect but is not a separate top-level taxonomy navigation branch in that repository. This distinction matters because the prior v15 workbook showed seven rows without clearly identifying which rows were source-taxonomy branches and which were Ali-derived synthesis.

### 2.3 Provenance labels used here

| Label | Meaning |
| --- | --- |
| `ACL-PAPER` | Explicit paper-level core aspect or category in Zou et al. (2026). |
| `ACL-REPO` | Explicit taxonomy navigation branch in the survey companion repository. |
| `VEGO-AI-DERIVED` | Ali's RQ-led synthesis based on the controlled VEGO-AI literature review and target problem; not a source-taxonomy branch. |
| `METHOD` | Current study artifact in `chapter-4-research-methodology.md`; recommendation pending supervisor decision. |

## 3. Exact relevance scale

Only these four labels are permitted:

| Label | Operational meaning in this map |
| --- | --- |
| **HIGHLY RELEVANT** | Directly structures a load-bearing construct in the umbrella RQ or SQ1–SQ3. |
| **LESS RELEVANT** | Useful enabling/background structure but not the primary doctoral knowledge contribution. |
| **NOT RELEVANT AT ALL** | Explicitly outside the current thesis problem and evaluation scope. |
| **MISSING FROM ACL TAXONOMY** | Required by the VEGO-AI problem but absent as a first-class branch in the source taxonomy. This does not assert that the survey never mentions any related idea in prose. |

## 4. Classification of the ACL source taxonomy

### 4.1 Environment & Profiling — **HIGHLY RELEVANT**

**Source structure.** Environment setting; human roles/goals/capabilities; agent roles/goals/capabilities; single/multiple human-agent configurations.

**Why it matters for VEGO-AI.** The thesis cannot treat “the expert” as globally authoritative. Language, domain, pedagogical, institutional, clinical, and governance competence are claim-specific. The decision context also changes across task, model type, guideline version, domain, institution, and transfer distance.

**VEGO-AI use.** Supports:

- claim-specific expert routing in SQ1;
- reviewer identity, role, competence, and authority in SQ2;
- source/target context descriptors and authorization in SQ3;
- Plan-B-first software/modeling scope and conditional medical transfer.

**Boundary.** The ACL dimension profiles participants and environments; it does not itself provide the VEGO-AI judgment lifecycle, permission model, or leakage-safe transfer test.

### 4.2 Human Feedback — **HIGHLY RELEVANT**

#### Type

| ACL category | Relevance | VEGO-AI interpretation |
| --- | --- | --- |
| Evaluative | HIGHLY RELEVANT | Fast verdict/assessment; useful but weak for reconstruction and reuse when stored alone. |
| Corrective | HIGHLY RELEVANT | Supports fixing mappings, evidence, rules, or classifications. |
| Guidance | HIGHLY RELEVANT | Supports rationale, alternatives, counterexamples, and domain/language clarification. |
| Implicit | LESS RELEVANT | Potential future signal for reliance or workflow behavior; too ambiguous to act as authoritative expert judgment without validation. |

#### Granularity

| ACL category | Relevance | VEGO-AI interpretation |
| --- | --- | --- |
| Holistic/coarse | LESS RELEVANT | Efficient for overall ratings but obscures the premise, fragment, or guideline that failed. |
| Segment-level/fine-grained | HIGHLY RELEVANT | Matches VEGO-AI's fragment-, guideline-, pattern-, and claim-level review units. |

#### Phase

| ACL category | Relevance | VEGO-AI interpretation |
| --- | --- | --- |
| Initial setup | HIGHLY RELEVANT | Guideline/template validation, role/authority definition, policy configuration. |
| During task | HIGHLY RELEVANT | Selective intervention and targeted clarification while the agentic assessment is active. |
| Post-task | HIGHLY RELEVANT | Audit sampling, adjudication, guideline refinement, memory validation, outcome tracing. |

**Closest controlled VEGO-AI literature.** Horvitz (mixed initiative), Amershi et al. (HAI interaction guidance), Kulesza et al. (explanatory debugging), Bansal et al. and Buçinca et al. (reliance/overreliance), Dong et al. (value of information).

**Boundary.** The ACL taxonomy classifies feedback form, granularity, and timing. It does not make a captured judgment attributable, reconstructable, authority-bounded, revocable, or safe to reuse.

### 4.3 Interaction Type

#### Collaboration — **HIGHLY RELEVANT**

| ACL subtype | Relevance | VEGO-AI interpretation |
| --- | --- | --- |
| Supervision | HIGHLY RELEVANT | Human monitors and intervenes when evidence, uncertainty, or consequence warrants review. |
| Delegation | LESS RELEVANT | Relevant to assigning review tasks to agents/humans, but VEGO-AI does not study unrestricted delegated autonomy. |
| Coordination | HIGHLY RELEVANT | Required for routing language/domain/policy claims and preserving agent-human workflow state. |
| Cooperation | HIGHLY RELEVANT | Captures complementary work on evidence, interpretation, correction, and adjudication. |

#### Competition — **NOT RELEVANT AT ALL**

VEGO-AI does not study a human and agent pursuing opposing goals or winning against one another. Adversarial robustness may be a future evaluation concern, but it is not the human-agent interaction relation in the current RQs.

#### Coopetition — **NOT RELEVANT AT ALL**

The current thesis does not define a mixed cooperative/competitive objective between humans and agents. Including it as relevant would broaden the scope without an RQ, artifact, or evaluation contract.

**Boundary.** Collaboration labels describe relationship patterns. They do not determine when to ask, what evidence to capture, whose judgment is authorized, or whether prior judgment may transfer.

### 4.4 Orchestration Paradigm — **LESS RELEVANT**

#### Task strategy

- **One by one / sequential:** useful for staged agent review, human escalation, adjudication, and lifecycle transitions.
- **Simultaneous / parallel:** potentially useful for independent review or parallel agent evidence generation, but it raises independence, conflict, and reconciliation questions.

#### Temporal synchronization

- **Synchronous:** relevant to immediate high-consequence intervention.
- **Asynchronous:** relevant to queues, batch review, post-task audit, and bounded expert availability.

**VEGO-AI use.** Supports intervention modes and operational feasibility in SQ1.

**Boundary.** Orchestration is an implementation/design dimension. The proposed Study 1 contribution is not “an orchestration architecture”; it is the narrower attention-budget cost/coverage relation and its falsifiable properties.

### 4.5 Communication — **LESS RELEVANT**

#### Structure

Centralized, decentralized, and hierarchical information-flow structures can support different agent/reviewer arrangements.

#### Mode

Conversation, observation, and message-pool modes can carry claims, evidence, uncertainty, corrections, dissent, and audit records.

**VEGO-AI use.** Supports inspectable evidence presentation and auditable feedback flow.

**Boundary.** Communication is enabling infrastructure. A message channel does not establish evidence sufficiency, authority, permission, validity, or successful reuse.

## 5. VEGO-AI dimensions **MISSING FROM ACL TAXONOMY**

These dimensions are Ali's derived synthesis. They must not be represented as branches copied from Zou et al.

### 5.1 Selective intervention under bounded expert attention

**RQ:** SQ1  
**Problem-world question:** When, how, and to whom should a fragment/pattern-level assessment be escalated so that important uncertainty is reviewed without asking on every case?

**Required dimensions:**

- calibrated uncertainty;
- cross-agent/cross-run disagreement;
- novelty and coverage gaps;
- consequence/policy importance;
- evidence weakness;
- expected value and expected reuse value;
- expert competence/availability;
- queue state and interruption burden.

**Nearest prior streams:** mixed initiative; learning to defer; selective prediction/reject option; value of information; active learning; reliance and interruption-cost literature.

**Current method artifact:** **attention-budget cost/coverage model**.

**Defensible residual question:** Which combination of signals and review modes yields a defensible load/coverage frontier for interpretive variability assessment? This remains a research hypothesis; the formal QL searches are not complete.

### 5.2 Reasoning-rich judgment representation

**RQ:** SQ2  
**Problem-world question:** How can a later authorized reviewer reconstruct what was judged, on what evidence, under which guideline/version, and why?

**Minimum information groups:**

- stable case/fragment/pattern identity;
- source evidence locator;
- system claim, confidence, and surfaced decision trace;
- expert verdict, rationale, counterevidence, and uncertainty;
- explicit scope and exclusions;
- role, competence, and claim-specific authority;
- provenance and version lineage;
- validation/adjudication state;
- downstream outcome trace.

**Nearest prior streams:** explanatory debugging; structured expert elicitation; provenance; knowledge representation; annotation/disagreement; Case-Based Reasoning.

**Current method artifact:** **normative judgment-record contract + executable conformance suite**.

**Anchor-lineage caution:** The Raykar/Aamodt & Plaza choice is not silently decided here. Raykar supports annotator reliability/disagreement; Aamodt & Plaza supports the retrieve-reuse-revise-retain predecessor baseline. Both roles must be evaluated separately rather than treated as interchangeable citations.

### 5.3 Claim-specific governance and contestability

**RQ:** SQ2  
**Problem-world question:** How can judgment remain challengeable and correctable through validation, dissent, adjudication, expiry, supersession, and revocation?

**Nearest prior streams:** W3C PROV-DM; contestable AI; model/data documentation; meaningful human control; disagreement and adjudication; access/authorization policy.

**Current method relationship:** governance requirements are part of the **judgment-record contract and conformance suite**, not a separate bundled C1–C7 contribution.

**Boundary:** Provenance records lineage; it does not by itself decide authority or permission. Contestability provides normative/process principles; it does not automatically supply the machine-testable VEGO-AI contract.

### 5.4 Scope-aware reuse

**RQ boundary:** SQ2 → SQ3  
**Problem-world question:** How can a prior judgment inform a new case without becoming global policy merely because it is retrievable or semantically similar?

**Required decision decomposition:**

1. retrieve candidate records;
2. assess contextual applicability;
3. check authority, status, visibility, expiry, revocation, and permission;
4. present eligible records as advisory evidence;
5. re-reason on current evidence;
6. log influence, override, outcome, and incident.

**Nearest prior streams:** RAG/external memory; agent memory; Case-Based Reasoning; provenance; authorization; contestability.

**Precise claim language:** Similarity-based retrieval alone does not establish contextual applicability, authorization, current validity, or beneficial target use.

### 5.5 Transfer eligibility and leakage-safe evaluation

**RQ:** SQ3  
**Problem-world question:** Under what source-target conditions may prior judgment be eligible, eligible with adaptation, or blocked?

**Required dimensions:**

- domain/task/guideline/version/population/institution/time distance;
- scope-defining vs non-defining context dimensions;
- local authorization and local validation;
- same-case/same-domain/cross-task/adjacent-domain/cross-domain distance;
- frozen source store and policy;
- independent blind target labels;
- matched no-reuse comparator;
- case, guideline, reviewer, temporal, policy-tuning, and store-contamination leakage controls.

**Nearest prior streams:** domain adaptation; WILDS/distribution shift; uncertainty under shift; transportability; clinical guideline adaptation; GRADE-ADOLOPMENT.

**Current method artifact:** **transfer-eligibility decision procedure + target-context descriptor**.

**Fervers correction retained:** Fervers et al. (2006) is a valid distinct guideline-adaptation source and is not treated as a year-error regression. It must not be conflated with the separate Fervers/ADAPTE Collaboration paper.

### 5.6 Variability exploration and guideline operationalization

**Role:** target problem substrate, cross-cutting all RQs.

The ACL taxonomy is domain-general and does not organize work around:

- language-versus-domain validity;
- alternative valid model representations;
- guideline fragments and versioned evidence locators;
- uncovered-fragment interpretation;
- recurrence versus validity;
- substantial versus occasional variability construct risk;
- leakage from guideline refinement into evaluation.

**Nearest prior streams:** software/process variability; model assessment; rule/reference-model grading; LLM-assisted conceptual modeling; computer-interpretable/guideline adaptation literature.

**Boundary:** This map does not resolve whether `occasional variability` should be renamed. The construct remains provisional because the current term may be read as frequency even though the working definition concerns validity/error.

## 6. RQ-to-artifact mapping used by the v16 figure

| RQ | Literature-derived problem | Current recommended artifact | Not claimed |
| --- | --- | --- | --- |
| SQ1 | Selective review under bounded attention | Attention-budget cost/coverage model | Optimal policy, effort reduction, accuracy improvement |
| SQ2 | Reconstructable, attributable, governed judgment | Normative judgment-record contract + conformance suite | Safe reuse, implementation independence, outcome gain |
| SQ3 | Explicit eligibility/adaptation/block decision across contexts | Transfer-eligibility decision procedure + target-context descriptor | Generalization, medical validity, safe cross-domain transfer |
| U-RQ | Integration of the three problem relationships | Integrated evaluation only after the three studies | Current demonstrated co-reasoning benefit |

## 7. Compact evidence map

| Branch | Provenance | Relevance | Primary RQ | Key VEGO-AI literature role |
| --- | --- | --- | --- | --- |
| Environment & Profiling | ACL-PAPER | HIGHLY RELEVANT | U-RQ/SQ1/SQ2/SQ3 | Roles, capabilities, context, claim-specific authority |
| Human Feedback | ACL-PAPER + ACL-REPO | HIGHLY RELEVANT | SQ1/SQ2 | Type, granularity, phase |
| Collaboration | ACL-PAPER + ACL-REPO | HIGHLY RELEVANT | U-RQ/SQ1 | Supervision, coordination, cooperation |
| Competition | ACL-PAPER + ACL-REPO | NOT RELEVANT AT ALL | — | Outside thesis relationship model |
| Coopetition | ACL-PAPER + ACL-REPO | NOT RELEVANT AT ALL | — | Outside thesis relationship model |
| Orchestration | ACL-PAPER + ACL-REPO | LESS RELEVANT | SQ1 | Timing and task strategy as enabling controls |
| Communication | ACL-PAPER + ACL-REPO | LESS RELEVANT | SQ1/SQ2 | Evidence/feedback flow as enabling infrastructure |
| Selective intervention | VEGO-AI-DERIVED | MISSING FROM ACL TAXONOMY | SQ1 | Multi-signal, burden-aware escalation |
| Judgment representation | VEGO-AI-DERIVED | MISSING FROM ACL TAXONOMY | SQ2 | Reconstructability and context preservation |
| Governance lifecycle | VEGO-AI-DERIVED | MISSING FROM ACL TAXONOMY | SQ2 | Authority, dissent, expiry, revocation |
| Scope-aware reuse | VEGO-AI-DERIVED | MISSING FROM ACL TAXONOMY | SQ2/SQ3 | Retrieval ≠ applicability ≠ permission ≠ benefit |
| Transfer/leakage controls | VEGO-AI-DERIVED | MISSING FROM ACL TAXONOMY | SQ3 | Eligibility, adaptation, holdout validity |
| Variability/guidelines | VEGO-AI-DERIVED | MISSING FROM ACL TAXONOMY | All | Target problem and construct boundary |

## 8. Open gates carried into v16

| Gate | Current state | Consequence |
| --- | --- | --- |
| Formal searches QL-01–QL-05 | 0/5 | No exhaustive/systematic gap claim |
| Full pinned ACL disposition | Incomplete | Source taxonomy can orient/snowball, not prove corpus saturation |
| Full-text extraction target | Below 40–60 | Detailed review-wide gap language remains bounded |
| Human scholarly inclusion review | Pending | Source selection is not final |
| RQ/construct approval | Pending | All RQ links and terminology remain provisional |
| EXP-005 | 0/24 generalization-safe labels | No accuracy/generalization benefit claim |
| Medical entry gates | 0/6 | No medical validation/deployment/safe-transfer claim |

## 9. Figure caption

> **Figure — ACL-2026 Human-Agent Taxonomy Relevance and VEGO-AI Gap Extensions.** Author-generated RQ-led synthesis based on Zou et al. (2026), the controlled VEGO-AI literature review, and the current Chapter 4 methodology. The upper section classifies source-taxonomy branches using Iris's relevance scale; the lower section identifies VEGO-AI problem dimensions missing as first-class ACL taxonomy branches. The figure is not copied from Zou et al., does not establish exhaustive literature coverage, and does not imply supervisor approval or empirical validation.

## 10. Release checklist

- [x] Five paper-level source aspects stated.
- [x] Four repository taxonomy navigation branches stated separately.
- [x] Exact relevance scale used.
- [x] `NOT RELEVANT AT ALL` applied explicitly to competition and coopetition.
- [x] Ali-derived dimensions labeled `MISSING FROM ACL TAXONOMY`.
- [x] Current Chapter 4 artifacts used instead of C1–C7.
- [x] Fervers false-positive correction retained.
- [x] Raykar/Aamodt and Dellermann/Dhanorkar issues not silently resolved.
- [x] Evidence gates preserved.
- [ ] Supervisor scholarly review and approval.
- [ ] Formal search and corpus-completion gates.
