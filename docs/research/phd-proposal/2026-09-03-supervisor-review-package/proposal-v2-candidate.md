# Governed Human Judgment for Agentic Variability Exploration

## Selective review, traceable decisions, and controlled reuse in VEGO-AI

**Doctoral research proposal — Version 2 candidate**
**Ali Hamed · 3 September 2026**
**Status:** ready for supervisor review; title, research questions, thresholds, and human-study design are not yet supervisor-approved.

## Abstract

Agentic systems can inspect many domain models, but an unexpected model fragment is not automatically an error. It may be a language mistake, a domain mistake, or a defensible alternative that a reference guideline omitted. Deciding among these readings can require human competence and institutional authority. Yet involving a person creates three connected problems: selecting when and whom to ask under scarce attention, preserving the resulting judgment so it remains inspectable and contestable, and controlling whether that judgment may influence a later case. This proposal extends VEGO-AI, a four-agent variability-exploration pipeline, with a governed human-judgment layer. A structured exploratory review shows that deferral, expert assignment, provenance, corrective memory, precedent reuse, authorization, and transfer controls are established individually. The proposed contribution is therefore not a new component but an evaluated claim-level integration of routing, judgment governance, and controlled reuse. Preliminary analysis of a frozen Cheers/ParkWise archive identified candidate signals throughout the pipeline, reproduced six policy arms at matched review budgets, and propagated one recorded correction deterministically. These results establish technical and descriptive feasibility only. Prospective studies with independent labels are required before claiming correctness, human benefit, burden reduction, or safe transfer.

## Evidence-status legend

**FACT** denotes an observation bound to a frozen source or reproducible output. **INFERENCE** denotes a reasoned synthesis that may be challenged by contrary evidence. **PROPOSAL** denotes an unevaluated design choice. **OPEN QUESTION** denotes an unresolved decision or unavailable evidence. These labels protect the boundary between the existing system, the present preliminary work, and the proposed doctorate.

# 1. Problem and motivation

## 1.1 Variability is not automatically error

A domain model translates narrative requirements into concepts, actors, relations, constraints, and behaviour. This translation is interpretive. Two modelers can make different abstraction choices while both remain defensible. Software- and business-process-variability research therefore distinguishes intentional contextual variation from accidental inconsistency rather than treating structural difference as proof of error (Galster et al., 2014; La Rosa et al., 2017).

Automated model assessment makes this distinction operational. A tool may find that a model fragment is absent from a reference model or guideline. It must still decide what the absence means. Rule-based grading, mistake catalogues, embedding similarity, and LLM assessment each provide useful evidence, but none turns every difference into a verdict (Bian et al., 2019; Bian et al., 2020; Singh et al., 2022; Chen et al., 2024). Recent studies of LLM assistance for conceptual modelling further establish the surrounding task without resolving governed claim-level human review (Ali et al., 2024; Ben Chaaben et al., 2026). The decisive unit in this proposal is therefore a **claim**: one assessable statement about one model fragment under one versioned guideline.

The same issue appears in guideline operationalization. Clinical-informatics work distinguishes a narrative recommendation from its executable representation, and guideline adaptation methods make context an explicit decision rather than a copy operation (Peleg et al., 2003; Boxwala et al., 2004; Schünemann et al., 2017). VEGO-AI applies that broader problem to software/domain-model assessment: it turns descriptions into reference guidance and uses that guidance to assess diverse artifacts.

## 1.2 VEGO-AI baseline and decision points

VEGO-AI is prior work by Reinhartz-Berger, Bragilovski, and Sturm (see Reinhartz-Berger et al., 2026); the candidate is not an author of that foundation manuscript. The supplied manuscript remains a working paper with placeholder publication metadata. It is used to describe the architecture, not presented as a published source.

The baseline has four specialised agents:

1. the **Language Advisor** builds a modeling-language template and responds to language questions;
2. the **Domain Advisor** converts a domain description into reference guidelines;
3. the **Model Inspector** assesses individual models against those guidelines and classifies uncovered fragments; and
4. the **Variability Explorer** aggregates recurring deviations and classifies patterns.

Each transition exposes a potential human decision. A language expert may judge whether a template omitted a construct. A domain owner may accept, reject, or revise a generated guideline. A reviewer may decide whether a case-level fragment is a mistake or valid alternative. A rubric owner may authorize a recurring alternative to change future guidance. These roles are not interchangeable. Competence describes the ability to judge a claim; authority describes the mandate to make the judgment operative.

The supplied evaluation package contains 179 scored model rows, 165 per-model inspection reports, and 27 pattern records. The foundation working manuscript separately reports 178 model cases and 26 patterns. **OPEN QUESTION:** the source selection/counting rule needed to reconcile those denominators is not documented. This proposal preserves each figure with its source and bases each preliminary calculation on the denominator it actually inspected.

## 1.3 Why “add a human” is not a solution

Mixed-initiative research asks when a system should act, ask, or defer while accounting for uncertainty and interruption cost (Horvitz, 1999). Human-AI interaction guidelines add expectation setting, correction, user control, and visible system status (Amershi et al., 2019). These traditions establish that human participation must be designed, not appended.

Empirical results also caution against assuming benefit. Explanations can increase acceptance of AI recommendations without increasing complementary team performance (Bansal et al., 2021). Cognitive forcing can reduce overreliance while making an interface less acceptable and producing heterogeneous effects (Buçinca et al., 2021). Consequently, VEGO-AI cannot claim that a human review layer helps merely because the layer exists. Correctness, reliance, workload, and safety must be measured together under explicit comparators.

## 1.4 Three connected decisions

The research problem has three stages.

**Before judgment:** should the current claim be reviewed, by which available person, and in what mode? Asking everyone about everything wastes scarce attention. Asking only on model uncertainty can fail when confidence is miscalibrated or when the wrong reviewer receives the claim.

**At judgment:** what must be recorded so that the decision can be reconstructed, challenged, updated, or revoked? A label or comment may omit the evidence considered, the authority exercised, a dissenting view, the scope of validity, or the version to which the answer applied.

**After judgment:** may the decision influence a later case? Semantic similarity alone does not establish authorization, current validity, or contextual applicability. A useful precedent in one course may be unsafe in a revised course or a different organization.

“Reliable human-AI co-reasoning” is used here in a narrow empirical sense. It requires a combined process that meets predeclared outcome targets while respecting attention, authority, provenance, and reuse-safety constraints. It does not mean that the AI reasons like a person or that a human is always correct.

# 2. Related work and research gap

## 2.1 Review method and boundary

The current review is structured and exploratory. It combines a verified anchor set, backward/forward citation checks, the pinned ACL taxonomy corpus, targeted mechanism queries, and adversarial named-neighbour searches. Identity is checked through primary publisher, proceedings, standards, registry, or DOI records. The full registered multi-database search and second-reviewer screening are still open; therefore no field-wide absence or exhaustive-systematic-review claim is made.

The synthesis proceeds top down and bottom up. The top-down pass asks what established research provides for each mechanism. The bottom-up pass asks which frozen VEGO-AI errors and missing fields remain unexplained. A residual gap is kept only if it survives both passes.

## 2.2 Selective review and deferral

Reject-option and selective-classification research formalises the trade-off between coverage and risk (Chow, 1970; Geifman & El-Yaniv, 2017). Learning-to-defer extends that decision to a human expert and requires observed expert decisions to evaluate the joint system (Mozannar & Sontag, 2020). Later work addresses exact optimisation, calibration, and multiple experts (Mozannar et al., 2023; Verma et al., 2023; Mao et al., 2023).

These works directly challenge a weak novelty claim. They show that *when to defer* and *which expert is likely to be correct* are established research problems. They also provide stronger comparators than uncertainty-only review. However, the expert is generally represented through expected predictive performance or cost. Claim-scoped institutional authority, a governed post-decision record, and cross-context reuse are not the outcome of these methods.

Reviewer-assignment research supplies another neighbour. It maps tasks to expertise under workload and conflict constraints, and stakeholder studies warn that similarity scores omit important considerations (Thorn Jakobsen & Rogers, 2022; Dasgupta et al., 2025). This literature supports an explicit competence estimator and a competence-blind comparator. It does not permit competence to be equated with authority.

## 2.3 Human reliance, oversight, and authority

Human-AI collaboration aims at complementary performance, not ceremonial review. The negative and mixed results on explanation and cognitive forcing imply that the proposed system must measure whether people accept correct and incorrect advice appropriately, not only whether an explanation was displayed (Bansal et al., 2021; Buçinca et al., 2021).

Governance work places the decision within an organization. The NIST AI RMF 1.0 calls for differentiated human-AI roles, responsibilities, proficiency, and oversight across the lifecycle (National Institute of Standards and Technology [NIST], 2023). Meaningful human control and contestable-AI research similarly treat authority and the capacity to challenge a decision as design properties (Santoni de Sio & van den Hoven, 2018; Alfrink et al., 2023). These works make “the human” too coarse a variable. VEGO-AI must specify whether the reviewer is qualified for the claim and whether the reviewer may change the operative guideline.

## 2.4 Judgment as a governed record

W3C PROV-DM supplies a general representation of entities, activities, agents, derivation, and responsibility (Moreau & Missier, 2013). Decision-provenance and reviewability research extend the focus from model explanation to the socio-technical chain that produced and used a decision (Singh et al., 2019; Cobbe et al., 2021). Datasheets and model cards show how documentation can make provenance and intended use explicit, while disagreement-aware annotation work cautions against averaging away qualified dissent (Gebru et al., 2021; Mitchell et al., 2019; Aroyo & Welty, 2015).

Truth-maintenance systems provide a deeper lifecycle predecessor. Doyle (1979) links beliefs to justifications so conclusions can be revised when support changes. De Kleer (1986) represents alternative assumption sets and explicit retraction. These are not modern governance systems, but they refute the idea that dependency-aware revision is new.

The remaining design question is narrower: which minimum record lets a later reader reconstruct an expert judgment about a model claim, understand competence and authority, preserve dissent, and know whether the judgment is active, contested, expired, superseded, or revoked? That question requires an instrument and comparison, not only a schema.

## 2.5 Corrective memory, precedent, and reuse

Corrective-memory systems already store human feedback for later use. MemPrompt retrieves prior user corrections to modify later prompts (Madaan et al., 2022). GRACE performs local sequential model edits and evaluates retention and locality (Hartvigsen et al., 2023). MemOS treats model, activation, and plaintext memory as managed resources, though its relevant record is a preprint rather than peer-reviewed evidence (Li et al., 2025). Case Law Grounding retrieves and selects prior cases as precedents for human-led and LLM-led decisions (Zhang et al., 2025).

Case-based reasoning also studies when a case should be retained or deleted. Deletion can protect efficiency while damaging competence (Smyth & Keane, 1995). Guideline adaptation and living-guideline methods require explicit contextual reassessment rather than automatic copying (Schünemann et al., 2017; Akl et al., 2023).

Transfer theory limits what may be inferred across domains or populations (Ben-David et al., 2010; Bareinboim & Pearl, 2016). Attribute-based access control separately decides whether a subject may perform an action on an object under environmental conditions (Hu et al., 2019). Certified removal shows that a deletion claim can be specified as a verifiable property (Guo et al., 2020). Together these literatures imply that similarity, applicability, authorization, and removal are different questions. No one metric should stand in for all four.

## 2.6 Bottom-up error analysis

The frozen archive provides the following observations.

- **FACT:** Stage 2 contains generated guidelines that a recorded reviewer did not accept in full.
- **FACT:** Stage 3 contains compliance judgments and uncovered-fragment labels that the recorded reviewer changed.
- **FACT:** the recorded review was selected by the project, not independently sampled or adjudicated.
- **FACT:** candidate signals can be derived at every stage, but no canonical event has an attached human-review request.
- **FACT:** the current archive lacks the reviewer, mandate, consequence, queue, and reuse-value observations required for the proposed joint policy.
- **FACT:** one recorded correction can be propagated deterministically without mutating the baseline.

**INFERENCE:** the data support a feasibility problem before an effectiveness problem. VEGO-AI can expose claims and propagate a correction, but it cannot yet determine the right reviewer or evaluate the outcome of asking. The literature supplies mechanisms for the missing parts, but combining them changes the unit of evaluation: the unit is not a whole model or a generic expert; it is one versioned claim, one reviewer role, one mandate, and one possible later use.

## 2.7 Residual gap and contribution boundary

**PROPOSAL — residual gap:** within the verified exploratory corpus, no evaluated approach was found that simultaneously provides:

1. bounded claim-level review routing based on separately represented competence and authority;
2. a reconstructable judgment record with evidence, rationale, dissent, provenance, and lifecycle state; and
3. later influence only after authorization and context-applicability checks, with a use receipt.

The gap is an integration-and-evaluation gap. Deferral, expert matching, provenance, memory, precedent, authorization, and transfer are prior art. The doctoral contribution exists only if the integrated artifact supports a result that the mature components and composite comparators do not.

The gap has explicit falsifiers. A directly comparable published system would narrow the novelty claim. A competence-blind routing policy performing equivalently would remove competence-aware assignment from Study 1. A structured provenance record matching the governed record at lower cost would narrow Study 2. A composite of retrieval, precedent selection, and authorization matching the full reuse procedure would narrow Study 3. Failure of the governed integrated arm to improve the joint objective would refute the umbrella proposition.

# 3. Research questions and contributions

## 3.1 Current provisional wording

The following wording is preserved from the existing proposal and is not represented as approved.

- **U-RQ:** How can human judgment be captured, governed, and used to support agentic-AI-driven variability exploration in guideline-operationalization scenarios, enabling reliable human-AI co-reasoning?
- **SQ1:** When and how, in variability exploration scenarios, should an agentic assessment system request human judgment so that important uncertainties are addressed without unnecessary expert burden?
- **SQ2:** How should expert judgment—including the system's core reasoning—be represented, validated, reconciled, stored, and updated so that it can be reused?
- **SQ3:** How can expert judgment be reused across guideline-operationalization contexts while distinguishing local variability from transferable capability gaps?

## 3.2 Proposed wording for supervisor decision

The strict review found that the stated gap depends on *whom*, while the current SQ1 asks only *when and how*. The following block is therefore a **PROPOSAL**, not a silent replacement.

- **U-RQ-P:** How can claim-level human judgment be selectively requested, governed, and safely reused in agentic variability exploration so that the combined process improves decision quality without exceeding declared attention and safety constraints?
- **SQ1-P:** For which claim-level VEGO-AI assessment events should review be requested, and to which authorized reviewer, to maximise reviewer-conditional decision correctness and important-case capture at a fixed attention budget?
- **SQ2-P:** What minimum representation of a human judgment preserves enough evidence, reasoning, dissent, provenance, authority, and lifecycle state for another person to reconstruct and contest the decision?
- **SQ3-P:** Under what authorization, validity, and context conditions may a prior judgment influence a new guideline-operationalization case without unsafe transfer or reliance on revoked evidence?

## 3.3 Expected contributions

The expected contributions are expressed as hypotheses until evaluated.

**C1 — selective review and reviewer routing.** A transparent policy combines event uncertainty, consequence, evidence quality, reviewer competence, claim-scoped authority, queue state, novelty, disagreement, and expected reuse value. Contribution is supported only if it improves the declared outcomes over matched-budget uncertainty, threshold, random, and competence-blind comparators.

**C2 — governed judgment record.** A system-independent record schema and conformance suite preserve the claim, evidence, reasoning, verdict, uncertainty, dissent, provenance, scope, authority, validation, and lifecycle. Contribution is supported only if independent readers reconstruct and contest decisions better than from label-only, comment-only, and structured-provenance records at acceptable capture cost.

**C3 — controlled reuse.** An ordered procedure checks visibility, authorization, validity, applicability, and expected value before a prior judgment influences a new case. Contribution is supported only if it improves target decisions over a mature composite baseline without exceeding zero revoked reliance and the predeclared scope-violation ceiling.

**C4 — integrated governed co-reasoning.** The three artifacts form one claim-level loop around VEGO-AI. Contribution is supported only if the governed arm passes authority and reuse-safety gates and improves the declared joint objective over ordinary unstructured human-in-the-loop operation.

# 4. Research methodology

## 4.1 Design-science programme

The research follows design-science methodology (Hevner et al., 2004; Peffers et al., 2007; Wieringa, 2014). Each study begins with a problem and evidence analysis, specifies an artifact and measurable requirements, builds the smallest implementation needed for evaluation, and compares it with credible alternatives. Software completion, schema validity, or passing unit tests establishes technical readiness only. A research claim requires the corresponding empirical outcome.

The three studies are sequential but independently falsifiable. Study 1 creates review events and routes them. Study 2 governs the answer. Study 3 controls later use. The integrated study tests the umbrella proposition after the component instruments and safety gates mature.

## 4.2 Scenario, data, and units

**Scenario A — primary:** domain-model assessment in the Cheers and ParkWise course examples, covering use-case and class diagrams. The supplied evaluation package contains 179 scored model rows, 165 per-model inspection reports, and 27 pattern records. The working manuscript's 178-model/26-pattern count is retained separately until its selection rule is reconciled. Raw student artifacts, review records, and detailed event logs stay in the controlled local environment.

**Scenario B — conditional:** another guideline-operationalization setting, potentially medical. It enters only after explicit ethics, data, domain-expert, governance, and secure-computing gates. The software/modeling scenario is sufficient for the doctorate; medical work is not on the critical path.

The canonical unit is a `CandidateEscalationEvent`: one reviewable decision point with a stable event ID, source hash, lifecycle stage, item type, private locator hash, eight signal slots, evidence state (`observed`, `derived`, or `unavailable`), and the claim boundary `candidate_escalation_only`. Outcomes are analysed at claim level while models, tasks, reviewers, and contexts are retained as clustering variables.

## 4.3 Human intervention architecture

The proposed human layer is inserted at four points:

| Stage | Candidate signal | Reviewer competence | Authority required | Possible action |
|---|---|---|---|---|
| Language template | missing construct, low agreement, unresolved language question | modeling-language knowledge | advisory unless template owner | confirm, correct, request evidence |
| Domain guideline | omitted requirement, unsupported guideline, unresolved question | domain and guideline knowledge | domain/rubric ownership | accept, revise, reject, retain dissent |
| Case inspection | non-*Satisfied* verdict, ambiguous uncovered fragment, cross-agent conflict | model and claim-type knowledge | assessment mandate | confirm, relabel, block, escalate |
| Variability pattern | recurrence, novelty, medium confidence, guideline-change candidate | domain plus cross-case knowledge | guideline-change mandate | keep local, amend guideline, open capability-gap candidate |

The system may select one of six modes: autonomous action with receipt, audit sampling, batched review, queued review, immediate qualified review, or blocked action. Hard authorization and revoked-record rules precede any score. Missing mandatory evidence yields `Undetermined` or no selection; it is never silently set to a favourable value.

## 4.4 Study 1 — selective intervention and routing

### Goal and proposition

Study 1 answers SQ1-P. **P1:** at a fixed review budget, a policy that uses calibrated claim signals and claim-specific reviewer competence, subject to authority constraints, will increase both important-case capture and reviewer-conditional correctness relative to uncertainty-only and competence-blind routing without exceeding the selective-risk ceiling. P1 is narrowed if a simpler policy is equivalent or better.

### Phase 0: completed feasibility baseline

The current phase inventories signals, replays six arms, and applies one recorded correction. It uses no new participant and makes no outcome claim. State-dependent queue conditions are not evaluated by offline counterfactual replay. The proposed joint policy correctly selects zero because mandatory fields are unavailable.

### Phase 1: reference and reviewer data

Independent reviewers label a frozen, stratified sample without seeing policy assignments. A qualification set estimates each reviewer's proficiency by claim type. Competence is recorded as an empirical estimate with uncertainty. Authority is recorded separately in a mandate matrix supplied by the scenario owner. Disagreement is retained; adjudication begins only after independent labels are frozen.

### Policies and budgets

All policies receive the same events, evidence, calibration split, and tuning allowance. The arms are never ask, always ask, deterministic random review, uncertainty only, fixed threshold, competence-blind joint routing, and competence-aware authority-constrained routing. The primary attention budget is **PROPOSED 10%**, with **PROPOSED 5% and 20%** sensitivity analyses. Budget units are reviewer minutes where time data are available and review items otherwise; the unit is never changed after outcomes are inspected.

### Outcomes and analysis

Co-primary outcomes are important-case capture and reviewer-conditional correctness at the fixed budget. Both must support P1. Selective risk is a safety ceiling, not a substitutable outcome. Secondary measures are review yield, time, interruptions, queue delay, abandonment, calibration, workload distribution, and authority violations.

The main analysis uses hierarchical models with reviewer and task/model-family effects, reporting effect sizes and 95% confidence intervals. The two co-primary tests use a family-wise two-sided alpha of .05, allocated .025 each unless a gatekeeping procedure is preregistered. For a conservative paired-binary approximation, the minimum detectable difference is about `3.08/sqrt(N)` under 80% power: approximately 15.4 percentage points at 400 independent pairs and 10.9 points at 800. These are planning bounds only; cluster design effects and pilot discordance determine the final N.

### Failure conditions

P1 fails or narrows if independent reference labels cannot be established; competence and authority cannot be measured separately; the policy violates the budget or authority gate; the competence-blind arm is equivalent; a fixed threshold performs as well; or any gain requires unacceptable selective risk.

## 4.5 Study 2 — governed judgment

### Goal and proposition

Study 2 answers SQ2-P. **P2:** a minimum governed record will improve blind reconstruction and contestability over label-only, free-comment, and structured-provenance records at an acceptable capture cost. P2 is narrowed when a simpler record is equivalent.

### Artifact

The Governed Judgment Record contains: event and artifact identifiers; claim and target fragment; evidence and applied guidance; decision trace; verdict and uncertainty; rationale and counterevidence; competence evidence; authority and mandate; scope and exclusions; retained dissent; validation and adjudication state; source/version provenance; lifecycle state; and retrieval/use/outcome receipts.

Legal states are `draft`, `reviewed`, `active`, `contested`, `expired`, `superseded`, and `revoked`. Transitions are versioned. Revocation prevents new influence and triggers dependency checks; it does not erase the historical fact that the judgment once existed.

### Evaluation

Readers who did not create the judgment receive one of four record conditions: label only, free comment, structured provenance, or full governed record. The primary contrast is full governed record versus structured provenance. A preregistered rubric scores reconstruction of the claim, decisive evidence, rationale, scope, authority, dissent, and current applicability. Two blinded graders score answers; agreement and adjudication are reported.

The proposed starting sample is 36 participants/reader instances after qualification. Under a simple paired normal approximation and three Bonferroni-adjusted contrasts, 36 observations detect a standardised within-unit effect near `dz=0.54` at 80% power. This is not a final power calculation; pilot variance, clustering, missingness, and the validated scoring distribution determine the final N. Capture time, correction success, and subjective workload are secondary.

### Failure conditions

P2 narrows if the rubric lacks reliability or headroom, independent implementers cannot produce conforming records, structured provenance performs equivalently at lower cost, or individual field-removal tests show that proposed fields do not contribute to reconstruction or contestability.

## 4.6 Study 3 — controlled reuse

### Goal and proposition

Study 3 answers SQ3-P. **P3:** an ordered authorization-validity-applicability procedure will improve held-out target decisions over a mature retrieval/precedent/authorization composite without unsafe reliance on out-of-scope or revoked judgments.

### Artifact and comparators

The procedure first determines whether the requester may discover the record. It then checks claim and action authorization, current lifecycle validity, context applicability, and expected benefit. Only then may the record be shown as attributed advice. Each decision produces a receipt. Outcomes are `Eligible`, `Eligible with adaptation`, `Blocked`, or `Undetermined`.

Five arms separate the mechanisms: no reuse; semantic similarity retrieval; MemPrompt-style correction retrieval; Case-Law-style precedent selection; a composite of retrieval, contextual matching, and ABAC; and the full governed procedure. The composite, not retrieval alone, is the primary comparator.

### Data partition and outcomes

Source-store construction, threshold calibration, rater training, and held-out target evaluation use disjoint partitions. Model version, guideline version, context descriptor, store, policy, and exclusion rules are frozen before target access. The primary outcome is target-case correctness over the composite after the safety gates pass. Proposed safety constants are zero reliance on revoked judgments, a +2.5 percentage-point non-inferiority margin for scope violations, and a −5 percentage-point minimum acceptable bound for target benefit. These numbers are placeholders for supervisor and pilot review, not results.

A transferable capability-gap claim requires the same predeclared failure signature in at least two contexts above a frozen distance threshold, independent confirmation, and elimination of local guideline, task, version, data, and reviewer explanations. If a second defensible context cannot be obtained, the thesis reports procedure reliability and does not claim cross-context capability gaps.

### Failure conditions

P3 narrows if independent raters cannot apply the procedure reliably, the composite comparator is equivalent or superior, the safety ceiling is exceeded, revoked evidence influences an output, or apparent transfer disappears after context differences are controlled.

## 4.7 Integrated evaluation

### Proposition and primary objective

**P4:** governed VEGO-AI will outperform ordinary unstructured human-in-the-loop operation on a gated joint objective: it must first have zero authority violations, zero revoked-record reliance, and remain within the scope-violation ceiling; among arms passing those gates, it must improve reviewer-conditional correctness on important claims at the fixed attention budget. P4 narrows if the governed arm fails any gate or does not improve the outcome.

### Fixed design

The four arms are AI-only VEGO-AI, human-only assessment, ordinary unstructured HITL, and governed VEGO-AI. The claim/model block is the allocation unit; no participant sees the same fragment in two arms. Qualified reviewers each complete two of the four arms on disjoint, difficulty-matched blocks in a balanced incomplete-block design. Arm pairs and order are randomised; sequence is counterbalanced with a Latin-square schedule. Standardised training and a qualification test precede allocation. Sessions are separated by a one-week washout. Independent adjudicators remain blinded to arm.

Analysis includes reviewer and task/model-family effects and clusters claim outcomes within model. Cases, evidence access, reviewer role, and review-time budget are matched. Attrition, protocol deviations, missing responses, and post hoc changes are reported. Only final sample size remains pilot-adjustable; the unit, arms, allocation, counterbalancing, washout, training, clustering, gates, and objective are fixed before the pilot.

## 4.8 Ethics, privacy, and open-science boundary

No new human-participant outcome data are collected before the institutional determination and consent/data-access requirements are recorded. Student artifacts remain in the approved private environment. Public Git history contains only code, schemas, synthetic fixtures, aggregate data, and sanitized hashes/receipts. Reviewers see only the minimum evidence authorized for their task.

The protocol, hypotheses, code, synthetic fixtures, and analysis plan can be public. Raw models, identities, full review notes, private storage identifiers, and linkable local paths cannot. A reproducible package proves execution consistency; it does not prove that a person consented, a label is correct, or a supervisor approved the design.

# 5. Preliminary results

## 5.1 Stage-level inventory

**FACT:** EXP-045 found candidate signals at each stage of the frozen archive. Stage 1 produced 6 candidate signals over 38 clusters and 7 unreached constructs among 40 reference constructs. Stage 2 produced 18 candidate signals over 28 clusters, 12 open questions, and 59 missed reference guidelines against the evaluator-recorded denominator of 80. Stage 3 contained 491 alternative readings and 15 high-severity mistakes, producing 506 signal instances across 165 case files. Stage 4 contained 11 trigger-like patterns among 27 but no materialised review-queue object.

These counts identify places to inspect. They do not show that the agent was wrong, that a human was needed, or that one stage is more valuable than another.

## 5.2 Recorded-review baseline

**FACT:** EXP-046 read the recorded project review. Its 186 Stage-2 rows comprise 169 agent-written guidelines and 17 required guidelines added because no run had written them. Sixty-eight of the 169 agent-written guidelines were not accepted in full (40.2%). The source files separately contained 78 non-comment reference lines, 59 unmatched. The EXP-045 evaluator denominator of 80 and source-parser denominator of 78 are retained because they answer different questions.

Among 915 reviewed compliance judgments, 120 were changed. Rates differed by original verdict: 12/658 *Satisfied*, 75/162 *Partially-Satisfied*, and 33/95 *Not-Satisfied*. A retrospective rule that flags every non-*Satisfied* verdict would send 257/915 items to review and include 108/120 recorded changes. Among 104 reviewed uncovered-fragment judgments, 27 were changed.

**INFERENCE:** the non-*Satisfied* rule is an interpretable baseline for retrospective change coverage at a stated review load. It is not an accuracy estimator because review items were selected non-randomly, the reviewer was not independent, and no adjudication exists.

The VEGO-AI score and course grade had `r=0.2501` across 164 paired model rows. This is descriptive association between different measures, not evidence that either is correct at claim level.

## 5.3 C0 policy replay

**FACT:** the canonical adapter created 1,874 candidate events: 6 template, 18 guideline, 1,839 case-inspection, and 11 variability-classification. Budgets were 93, 187, and 374 events at 5%, 10%, and 20%. All arms saw the same event table and fixed seed 20260902.

Never-ask selected zero. Always-ask, deterministic random, uncertainty-only, and fixed-threshold arms filled their budgets. The proposed joint policy selected zero at every budget because required signals were unavailable. Two full runs produced identical hashes.

**INFERENCE:** this is a readiness failure that protects the study from fabricated constructs. The joint design cannot be evaluated until competence, authority, consequence, queue, disagreement, and reuse-value inputs are observed or explicitly derived under a validated rule.

## 5.4 Bounded human-correction replay

**FACT:** an existing recorded review changed one fragment from *Alternative* to *Language Mistake*. A bound directive identified that fragment by SHA-256, verified the baseline label, altered exactly one fragment and scoring contribution, and preserved the source. The score changed from 17.5/27 (64.8%) to 16.5/27 (61.1%). The negative delta is consistent with removing positive credit. Two executions were byte-identical.

The permitted conclusion is that a recorded correction can propagate through the frozen representation with a deterministic receipt. The result does not establish independent correctness or human benefit. It does not rerun the LLM agents, measure a user, or estimate generalisation.

## 5.5 What the preliminary work changes

The feasibility baseline changes the architecture plan in three ways. First, review requests must be first-class objects; trigger-like fields are insufficient. Second, the system must collect the missing reviewer and governance signals rather than estimate them retrospectively from outputs. Third, Stage 2 and Stage 3 need separate outcome strata because guideline adequacy and case-level compliance are different decisions.

It also narrows the immediate claim. September evidence supports **where/when candidate identification and technical propagation**. It does not yet support *whom*, a benefit estimate, or policy superiority. Those become prospective gates in Study 1 rather than conclusions in this proposal.

# 6. Validity, falsification, and risk controls

## 6.1 Construct validity

“Important case,” “correctness,” “competence,” “authority,” “burden,” “applicability,” and “unsafe influence” receive separate operational definitions. Course grade is not a substitute for claim correctness. Confidence is not a substitute for uncertainty under shift. Availability is not competence. Competence is not authority. Semantic similarity is not applicability. Deletion is not evidence of removed downstream influence.

## 6.2 Internal validity

Calibration, training, source-store construction, and test partitions remain disjoint, with leakage controls treated as part of reproducibility rather than as a post-hoc check (Kapoor & Narayanan, 2023). Human labels are frozen before policy evaluation. Assignment and order are randomised and counterbalanced. The same reviewer never receives the same fragment under two policies. Protocol deviations and missing data are retained. State-dependent policies use queue-aware simulation or prospective execution, not static replay.

## 6.3 External validity

Cheers and ParkWise are two course examples, not a population of organizations. Findings will be reported by domain, UML language, stage, and claim type. Generalisation requires replication in a predeclared different context. Medical transfer is conditional and cannot rescue a failed software/modeling study.

## 6.4 Statistical conclusion validity

Effect sizes and uncertainty accompany significance tests. Co-primary outcomes and multiplicity are preregistered. Equivalence or non-inferiority conclusions require explicit margins. Clustered outcomes use clustered or hierarchical analysis. Small samples produce minimum-detectable-effect statements rather than unsupported “no difference” claims.

## 6.5 Socio-technical risks

Human review can harm, delay, or bias decisions. Reviewer competence may drift. Mandates may conflict. A record can preserve a poor judgment. A memory can amplify historical errors. A high-performing policy can concentrate burden unfairly. The design therefore retains dissent, records version and scope, exposes workload distribution, and treats revocation and authorization as hard gates.

# 7. Work plan and milestones

The doctorate is three formal research years preceded by a preparatory year; elapsed calendar time is reported honestly.

| Period | Main work | Exit evidence |
|---|---|---|
| Sep 2026–Sep 2027: preparation | approve RQs; execute review; ethics/data pathway; freeze definitions; recruit/qualify reviewer pool; pilot instruments and queue simulation | approved protocol set, screened corpus, pilot estimates, ethics/data receipts |
| Oct 2027–Mar 2028: Semester 1 | Study-1 calibration data and event/mandate collection | frozen partitions, competence and authority records |
| Apr–Sep 2028: Semester 2 | prospective Study 1 and Paper 1 | matched-budget results or explicit null/narrowing |
| Oct 2028–Mar 2029: Semester 3 | Study-2 instrument validation and conformance | reliable rubric, independent implementation |
| Apr–Sep 2029: Semester 4 | Study 2; freeze integrated design; secure second context | Study-2 results, integrated preregistration, context gate |
| Oct 2029–Mar 2030: Semester 5 | Study 3 and integrated pilot | reuse/revocation results, final N and logistics |
| Apr–Sep 2030: Semester 6 | integrated run, synthesis, dissertation completion | P4 result, archived evidence package, thesis |

If a second context or sufficient qualified reviewers cannot be secured, Study 3 is narrowed to procedure reliability and the integrated design uses the primary scenario only. Scope is reduced before evidence standards are weakened.

# 8. Research assistance and responsibility

OpenAI Codex was used during August–September 2026 for local code assistance, source extraction, document restructuring, candidate-reference discovery, diagram generation, and automated QA. Primary bibliographic identities were checked against authoritative records. AI-generated wording, code, and classifications were reviewed against the frozen evidence and tests. The candidate remains responsible for inclusion decisions, interpretations, numerical claims, citations, and the final submission.

The two supervisors are co-authors of the supplied unpublished VEGO-AI foundation manuscript. Its reported results are therefore treated as prior-work claims rather than independently audited evidence. The unresolved difference between the package's 179 scored rows, 165 inspection reports, and 27 patterns and the manuscript's 178 models and 26 patterns remains visible.

# 9. Conclusion

The immediate baseline is now clear. VEGO-AI exposes many candidate review signals and can propagate one recorded correction, but the frozen system does not yet create first-class review requests or observe the reviewer and governance variables needed for defensible routing. The literature already provides the component mechanisms. The doctoral opportunity is to test whether routing, governed judgment, and controlled reuse can work together at claim level and outperform mature alternatives under explicit attention and safety constraints. Until prospective evidence exists, that opportunity remains a falsifiable proposal rather than a demonstrated benefit.

# References

Akl, E. A., et al. (2023). Methods for living guidelines: Early guidance based on practical experience. Paper 1: Introduction. *Journal of Clinical Epidemiology, 155*, 84–96. https://doi.org/10.1016/j.jclinepi.2022.12.024

Alfrink, K., Keller, I., Kortuem, G., & Doorn, N. (2023). Contestable AI by design: Towards a framework. *Minds and Machines, 33*(4), 613–639. https://doi.org/10.1007/s11023-022-09611-z

Ali, S. J., Reinhartz-Berger, I., & Bork, D. (2024). How are LLMs used for conceptual modeling? An exploratory study on interaction behavior and user perception. In *Conceptual Modeling (ER 2024)* (pp. 257–275). https://doi.org/10.1007/978-3-031-75872-0_14

Amershi, S., et al. (2019). Guidelines for human-AI interaction. In *Proceedings of CHI 2019* (pp. 1–13). https://doi.org/10.1145/3290605.3300233

Aroyo, L., & Welty, C. (2015). Truth is a lie: Crowd Truth and the seven myths of human annotation. *AI Magazine, 36*(1), 15–24. https://doi.org/10.1609/aimag.v36i1.2564

Bansal, G., et al. (2021). Does the whole exceed its parts? The effect of AI explanations on complementary team performance. In *Proceedings of CHI 2021* (pp. 1–16). https://doi.org/10.1145/3411764.3445717

Bareinboim, E., & Pearl, J. (2016). Causal inference and the data-fusion problem. *Proceedings of the National Academy of Sciences, 113*(27), 7345–7352. https://doi.org/10.1073/pnas.1510507113

Ben-David, S., Blitzer, J., Crammer, K., Kulesza, A., Pereira, F., & Wortman Vaughan, J. (2010). A theory of learning from different domains. *Machine Learning, 79*(1–2), 151–175. https://doi.org/10.1007/s10994-009-5152-4

Ben Chaaben, M., Burgueño, L., David, I., & Sahraoui, H. (2026). On the utility of domain modeling assistance with large language models. *ACM Transactions on Software Engineering and Methodology, 35*(4), 1–38. https://doi.org/10.1145/3744920

Bian, W., Alam, O., & Kienzle, J. (2019). Automated grading of class diagrams. In *MODELS-C 2019* (pp. 700–709). https://doi.org/10.1109/MODELS-C.2019.00106

Bian, W., Alam, O., & Kienzle, J. (2020). Is automated grading of models effective? In *MODELS 2020* (pp. 365–376). https://doi.org/10.1145/3365438.3410944

Boxwala, A. A., et al. (2004). GLIF3: A representation format for sharable computer-interpretable clinical practice guidelines. *Journal of Biomedical Informatics, 37*(3), 147–161. https://doi.org/10.1016/j.jbi.2004.04.002

Buçinca, Z., Malaya, M. B., & Gajos, K. Z. (2021). To trust or to think: Cognitive forcing functions can reduce overreliance on AI in AI-assisted decision-making. *Proceedings of the ACM on Human-Computer Interaction, 5*(CSCW1), Article 188. https://doi.org/10.1145/3449287

Chen, K., Chen, B., Yang, Y., Mussbacher, G., & Varró, D. (2024). Embedding-based automated assessment of domain models. In *MODELS Companion 2024* (pp. 87–94). https://doi.org/10.1145/3652620.3687774

Chow, C. K. (1970). On optimum recognition error and reject tradeoff. *IEEE Transactions on Information Theory, 16*(1), 41–46. https://doi.org/10.1109/TIT.1970.1054406

Cobbe, J., Lee, M. S. A., & Singh, J. (2021). Reviewable automated decision-making: A framework for accountable algorithmic systems. In *FAccT 2021*. https://doi.org/10.1145/3442188.3445921

Dasgupta, S., Sharma, H., Patel, D., Desai, P., & Roy, A. K. (2025). Are key-phrases all that reviewers care about? A comprehensive benchmarking of reviewer matchmaking systems. In *AAAI 2025*. https://doi.org/10.1609/aaai.v39i22.34545

de Kleer, J. (1986). An assumption-based TMS. *Artificial Intelligence, 28*(2), 127–162. https://doi.org/10.1016/0004-3702(86)90080-9

Doyle, J. (1979). A truth maintenance system. *Artificial Intelligence, 12*(3), 231–272. https://doi.org/10.1016/0004-3702(79)90008-0

Galster, M., Weyns, D., Tofan, D., Michalik, B., & Avgeriou, P. (2014). Variability in software systems—A systematic literature review. *IEEE Transactions on Software Engineering, 40*(3), 282–306. https://doi.org/10.1109/TSE.2013.56

Gebru, T., et al. (2021). Datasheets for datasets. *Communications of the ACM, 64*(12), 86–92. https://doi.org/10.1145/3458723

Geifman, Y., & El-Yaniv, R. (2017). Selective classification for deep neural networks. In *Advances in Neural Information Processing Systems 30* (pp. 4878–4887). https://proceedings.neurips.cc/paper/2017/hash/4a8423d5e91fda00bb7e46540e2b0cf1-Abstract.html

Guo, C., Goldstein, T., Hannun, A., & van der Maaten, L. (2020). Certified data removal from machine learning models. In *ICML 2020* (pp. 3832–3842). https://proceedings.mlr.press/v119/guo20c.html

Hartvigsen, T., Sankaranarayanan, S., Palangi, H., Kim, Y., & Ghassemi, M. (2023). Aging with GRACE: Lifelong model editing with discrete key-value adaptors. In *Advances in Neural Information Processing Systems 36*. https://proceedings.neurips.cc/paper_files/paper/2023/hash/95b6e2ff961580e03c0a662a63a71812-Abstract.html

Hevner, A. R., March, S. T., Park, J., & Ram, S. (2004). Design science in information systems research. *MIS Quarterly, 28*(1), 75–106. https://doi.org/10.2307/25148625

Horvitz, E. (1999). Principles of mixed-initiative user interfaces. In *Proceedings of CHI 1999* (pp. 159–166). https://doi.org/10.1145/302979.303030

Hu, V. C., et al. (2019). *Guide to attribute based access control definition and considerations* (NIST Special Publication 800-162; updated August 2, 2019). https://doi.org/10.6028/NIST.SP.800-162

Kapoor, S., & Narayanan, A. (2023). Leakage and the reproducibility crisis in machine-learning-based science. *Patterns, 4*(9), Article 100804. https://doi.org/10.1016/j.patter.2023.100804

La Rosa, M., van der Aalst, W. M. P., Dumas, M., & Milani, F. P. (2017). Business process variability modeling: A survey. *ACM Computing Surveys, 50*(1), Article 2. https://doi.org/10.1145/3041957

Li, Z., et al. (2025). MemOS: An operating system for memory-augmented generation in large language models. *arXiv preprint*. https://arxiv.org/abs/2505.22101

Madaan, A., Tandon, N., Clark, P., & Yang, Y. (2022). Memory-assisted prompt editing to improve GPT-3 after deployment. In *EMNLP 2022* (pp. 2833–2861). https://doi.org/10.18653/v1/2022.emnlp-main.183

Mao, A., Mohri, C., Mohri, M., & Zhong, Y. (2023). Two-stage learning to defer with multiple experts. In *Advances in Neural Information Processing Systems 36* (pp. 3578–3606). https://proceedings.neurips.cc/paper_files/paper/2023/hash/0b17d256cf1fe1cc084922a8c6b565b7-Abstract-Conference.html

Mitchell, M., et al. (2019). Model cards for model reporting. In *FAT 2019* (pp. 220–229). https://doi.org/10.1145/3287560.3287596

Moreau, L., & Missier, P. (Eds.). (2013). *PROV-DM: The PROV data model*. W3C Recommendation. https://www.w3.org/TR/prov-dm/

Mozannar, H., Lang, H., Wei, D., Sattigeri, P., Das, S., & Sontag, D. (2023). Who should predict? Exact algorithms for learning to defer to humans. In *AISTATS 2023* (pp. 10520–10545). https://proceedings.mlr.press/v206/mozannar23a.html

Mozannar, H., & Sontag, D. (2020). Consistent estimators for learning to defer to an expert. In *ICML 2020* (pp. 7076–7087). https://proceedings.mlr.press/v119/mozannar20b.html

National Institute of Standards and Technology. (2023). *Artificial Intelligence Risk Management Framework (AI RMF 1.0)*. https://doi.org/10.6028/NIST.AI.100-1

Peffers, K., Tuunanen, T., Rothenberger, M. A., & Chatterjee, S. (2007). A design science research methodology for information systems research. *Journal of Management Information Systems, 24*(3), 45–77. https://doi.org/10.2753/MIS0742-1222240302

Peleg, M., et al. (2003). Comparing computer-interpretable guideline models: A case-study approach. *Journal of the American Medical Informatics Association, 10*(1), 52–68. https://doi.org/10.1197/jamia.M1135

Reinhartz-Berger, I., Bragilovski, M., & Sturm, A. (2026). Not all differences matter: Variability exploration of domain models via agentic AI. Supplied working manuscript; publication metadata not yet verifiable.

Santoni de Sio, F., & van den Hoven, J. (2018). Meaningful human control over autonomous systems: A philosophical account. *Frontiers in Robotics and AI, 5*, Article 15. https://doi.org/10.3389/frobt.2018.00015

Schünemann, H. J., et al. (2017). GRADE Evidence to Decision frameworks for adoption, adaptation, and de novo development of trustworthy recommendations: GRADE-ADOLOPMENT. *Journal of Clinical Epidemiology, 81*, 101–110. https://doi.org/10.1016/j.jclinepi.2016.09.009

Singh, J., Cobbe, J., & Norval, C. (2019). Decision provenance: Harnessing data flow for accountable systems. *IEEE Access, 7*, 6562–6574. https://doi.org/10.1109/ACCESS.2018.2887201

Singh, P., Boubekeur, Y., & Mussbacher, G. (2022). Detecting mistakes in a domain model. In *SAM 2022* (pp. 257–266). https://doi.org/10.1145/3550356.3561583

Smyth, B., & Keane, M. T. (1995). Remembering to forget: A competence-preserving case deletion policy for case-based reasoning systems. In *IJCAI 1995* (pp. 377–383). https://www.ijcai.org/Proceedings/95-1/Papers/050.pdf

Thorn Jakobsen, T., & Rogers, A. (2022). What factors should paper-reviewer assignments rely on? In *NAACL 2022* (pp. 4810–4823). https://doi.org/10.18653/v1/2022.naacl-main.354

Verma, R., Barrejon, D., & Nalisnick, E. (2023). Learning to defer to multiple experts: Consistent surrogate losses, confidence calibration, and conformal ensembles. In *AISTATS 2023* (pp. 11415–11434). https://proceedings.mlr.press/v206/verma23a.html

Wieringa, R. J. (2014). *Design science methodology for information systems and software engineering*. Springer. https://doi.org/10.1007/978-3-662-43839-8

Zhang, A. X., et al. (2025). Case law grounding: Using precedents to align decision-making for humans and AI. In *ACM Collective Intelligence Conference*. https://doi.org/10.1145/3715928.3737487
