# VEGO-AI supervisor evidence package

**Package date:** 3 September 2026
**Prepared for:** proposal and Study 1 review
**Status:** ready for supervisor review only
**Evidence vocabulary:** **FACT** = directly observed in a frozen source or reproducible output; **INFERENCE** = reasoned interpretation of facts; **PROPOSAL** = design choice awaiting approval or evaluation; **OPEN QUESTION** = unresolved decision or missing evidence.

## Executive answer

The supplied evidence supports a preliminary, bounded answer to the immediate supervisor question. **FACT:** candidate escalation signals occur at all four VEGO-AI stages, but the frozen implementation contains no materialised human-review request at any of the 1,874 canonical events. **FACT:** in a project-owned, non-random recorded review, disagreement was concentrated in generated guidelines and non-*Satisfied* case judgments. **FACT:** a simple retrospective Stage-3 rule would flag 257 of 915 reviewed compliance judgments and include 108 of 120 recorded changes. **FACT:** one recorded label correction can be applied to exactly one frozen fragment and propagated through scoring reproducibly. **INFERENCE:** the present system has inspectable places where a human could be involved, but it lacks the observed reviewer, authority, consequence, queue, and reuse-value signals required for a defensible joint policy. **OPEN QUESTION:** whether human involvement improves independent correctness remains entirely untested.

The proposal is therefore reframed around one falsifiable integration claim: claim-level review should connect a bounded routing decision, a governed judgment record, and controlled later reuse. The components are not individually new. The proposed contribution is the evaluated integration and the explicit separation of competence from authority.

# A. Supervisor Requirements Register

## A.1 Source and authority

The canonical atomic register is the repository file `iris-arnon-requirements-2026-09-02-checklist.md` in the parent proposal directory. It contains 115 timestamped rows plus its evidence caveat. Its older “where addressed” locations describe an earlier draft and are not treated as proof that the current package closes every row. The current package instead uses the reverified control view below and the tomorrow-deliverable coverage table in A.2. The English and Hebrew requirement sources are machine-derived meeting records with neutral/uncertain attribution; they are evidence of what was discussed, not proof of approval.

The table below is the implementation-level control view. “Closed in package” means the current artifact contains a traceable response; it does not mean that Iris or Arnon accepted it.

| Control ID | Requirement or constraint | Source class | Package response | Status |
|---|---|---|---|---|
| SR-01 | Prioritise preliminary results before study-detail and presentation questions. | Iris-derived call record | Results and protocol lead; formatting decisions follow. | Closed in package; confirmation pending |
| SR-02 | Lead the reader into the literature; do not present a sequence of paper summaries. | Arnon feedback relayed in call | Related work is organised as a mechanism chain, then reconciled with errors. | Closed in package; confirmation pending |
| SR-03 | Give a one-page study design with question, RQ link, data, measures, and exact plan. | Iris-derived call record | Separate one-page plan plus executable protocol. | Closed in package; confirmation pending |
| SR-04 | Give results and conclusions after the design is reviewed. | Iris-derived call record | Preliminary results are clearly marked as already-run descriptive evidence; prospective human evaluation remains gated. | Partially closed; new supervisor feedback pending |
| SR-05 | Proposal v2 must process all Arnon points and integrate preliminary results. | Iris-derived call record | Revised proposal and 26-row resolution matrix included. | Closed in package; approval pending |
| SR-06 | Be specific: name Cheers/ParkWise, architecture stage, baseline, measure, and evidence location. | Iris-derived call record | All appear in the one-page plan, protocol, and results. | Closed in package |
| SR-07 | The immediate preliminary question is **when** to escalate; do not expand the September demonstration into a full user study. | Iris-derived call record | Current result stays descriptive and technical. Proposed *whom* wording belongs to the later controlled benchmark. | Closed; wording decision open |
| SR-08 | Demonstrate, do not prove, places where human involvement could matter. | Iris-derived call record | Candidate signals and one bounded correction are shown; no benefit claim. | Closed in package |
| SR-09 | Show how at least some candidate points can be detected automatically. | Iris-derived call record | EXP-045 inventory and the non-*Satisfied* retrospective rule provide explicit detectors. | Closed descriptively |
| SR-10 | A complete catalogue is not required; examples may suffice. | Iris-derived call record | All cataloguing language is scoped to the frozen corpus and named searches. | Closed in package |
| SR-11 | Identify intervention types, including approval, correction, and possible guideline update. | Iris-derived call record | Architecture distinguishes confirm, correct, adjudicate, update-guideline-candidate, and block/review. | Proposed; not evaluated |
| SR-12 | A specific-case descriptive analysis can be sufficient for the proposal. | Iris-derived call record | One recorded correction is replayed end to end. | Closed technically |
| SR-13 | The three supervisors/candidate may stand in as simulated humans; no external users are required this month. | Iris-derived call record | Current replay uses an already recorded review; no new participant claim. | Closed for preliminary work |
| SR-14 | Inject an intervention at a chosen point and inspect downstream change. | Iris-derived call record | Exactly one bound fragment label is changed and the existing scoring calculation is propagated. | Closed technically |
| SR-15 | Do not claim improvement, accuracy, user benefit, burden reduction, or generalisation. | Iris-derived call record | Claim boundary appears beside every result and in machine-readable receipts. | Closed |
| SR-16 | Human involvement may harm or make no difference. | Iris-derived call record | Negative score direction is preserved and interpreted as correction propagation, not benefit. | Closed |
| SR-17 | Do not use synthetic domain data as the empirical basis. | Iris-derived call record | Real frozen project outputs are used; the only synthetic file is a public schema fixture and is never empirical evidence. | Closed |
| SR-18 | Use course examples Cheers and ParkWise. | Iris-derived call record | Both domains and both UML settings are retained. | Closed |
| SR-19 | The exercise/TA index is qualified reference evidence, not unquestioned ground truth. | Iris-derived call record | Recorded review and grade are development evidence; independent gold status is explicitly prohibited. | Closed |
| SR-20 | Confidence is a possible trigger, not a proven intervention rule. | Iris-derived call record | Confidence-based arm remains a comparator and is not called superior. | Closed |
| SR-21 | Explain the proposed choice of stage; do not rank Agent 2 versus Agent 3 without evidence. | Iris-derived call record | Stage inventory reports earliest available signals; no causal ranking is made. | Closed descriptively |
| SR-22 | Every claim needs evidence; unclear links between results and conclusions must be removed. | Supervisor feedback | Facts, inferences, proposals, and open questions are visibly separated. | Closed in package |
| SR-23 | Explain what each experiment did, its question, its delta, and its RQ linkage. | Iris-derived call record | Each experiment has an input, operation, result, claim boundary, and RQ mapping. | Closed |
| SR-24 | Separate substantive design from presentation. | Iris-derived call record | Experiment/gap decisions are made before document styling. | Closed |
| SR-25 | Give VEGO-AI its own subsection if it is central. | Arnon inline comment | Dedicated baseline and architecture subsection in proposal. | Closed in revision |
| SR-26 | Remove repeated section-summary boxes and unnecessary material. | Arnon inline comments | Summary boxes removed; seven decorative figures dropped. | Closed in revision |
| SR-27 | Move scenario instantiation into methodology. | Arnon inline comment | Scenario and data appear in Methodology, not objectives. | Closed in revision |
| SR-28 | Clarify the purpose and relevance of each distinction. | Arnon inline comments | Each construct is followed by its measured role or falsifier. | Closed in revision |
| SR-29 | Tighten search queries that would otherwise retrieve unmanageable results. | Arnon inline comment | Named mechanism-and-domain query families and adversarial neighbour targets are recorded. | Partially closed; full execution pending |
| SR-30 | A supporting taxonomy is not automatically a thesis contribution. | Arnon inline comment | Taxonomy is a review aid and seed only, not Study 4 or a contribution. | Closed in revision |
| SR-31 | The title must decide between “judgment” and “involvement.” | Arnon inline comment | “Governed Human Judgment” retained as candidate wording because the artifact is a decision record; choice is surfaced. | OPEN QUESTION |
| SR-32 | Research-question wording requires explicit approval. | Existing proposal boundary | Current and proposed wordings are shown separately. | OPEN QUESTION |
| SR-33 | Human routing must distinguish competence from authority if *whom* is claimed as a gap. | Strict committee review | Proposed SQ1, competence-blind comparator, qualification set, and mandate registry added. | Proposed; approval/data pending |
| SR-34 | Engage adjacent literatures already found: corrective memory, precedent, model editing, memory OS, living guidance, truth maintenance, and provenance. | Strict committee review | All are verified and conceded in the gap analysis. | Closed for named targets; full search pending |
| SR-35 | Offline replay cannot evaluate state-dependent signals without queue-aware simulation. | Strict committee review | C0 is restricted to state-independent descriptive behavior; future stateful evaluation is queue-aware. | Closed in design |
| SR-36 | A weighted rule/grid is a fitted policy even if it is not a learned model. | Strict committee review | Proposal calls it a calibrated rule-based policy and equalises tuning budgets. | Closed in revision |
| SR-37 | Fix the integrated design rather than leaving every decision open. | Strict committee review | Four arms, unit, blocking, randomisation, counterbalancing, washout, training, cluster analysis, and joint objective specified. | Proposed; pilot N pending |
| SR-38 | Add constants, MDE logic, multiplicity, margins, and failure thresholds. | Strict committee review | Proposed numerical defaults and pilot-adjustment rules included. | Proposed; supervisor/statistical review pending |
| SR-39 | Add ethics, recruitment, pilot, and review execution to the preparatory period. | Strict committee review | Work plan corrected; medical route de-scoped from the critical path. | Closed in plan |
| SR-40 | Expand AI-assistance disclosure and retain candidate responsibility. | Strict committee review | Tools, date, functions, verification, and responsibility are stated in a numbered section. | Closed in revision |

## A.2 Tomorrow-deliverable coverage

| Supervisor need | What is ready to show | Evidence location | What remains open |
|---|---|---|---|
| One narrow question | **When/where should VEGO-AI propose a human review?** | One-page plan, opening block | Iris confirmation of scope |
| Real baseline data | Frozen Cheers/ParkWise outputs; no synthetic empirical observation | One-page data block; protocol Sections 3–5 | 179/178 and 27/26 counting reconciliation |
| Human-intervention points | H1 guideline review, H2 claim review, H3 variability trigger | One-page H1–H3 table; EXP-045 | No causal stage ranking |
| Automatic identification | Explicit H1 baseline, non-*Satisfied* H2 rule, implemented H3 trigger | One-page H1–H3 table; results Sections E.1–E.2 | Prospective detector calibration |
| A concrete intervention | One hash-bound recorded correction propagated without rerunning an agent | Protocol Section 7; results Section E.4 | Independent correctness and human-benefit evidence |
| Baselines and budgets | Six-arm replay at 5%, 10%, and 20%; seven-arm prospective plan | Protocol Sections 6 and 8 | Approval of 10% primary budget and competence-blind arm |
| Evaluation and effort | Exact current formulas plus prospective quality, time, interruption, and queue measures | One-page scorecard; protocol Section 9; metric receipt | Independent labels, qualified reviewers, timing instrumentation |
| Honest conclusion | Technical/descriptive feasibility only | Every result boundary; Section I gates | Supervisor approval and prospective outcome study |

# B. Gap Analysis

## B.1 Before this revision

The prior proposal had a strong evidence-boundary style but a fractured logic. Its gap claimed *whom* while SQ1 and all comparators measured *when*; it described six already-found neighbouring literatures as unsearched; and the only study answering the umbrella question deferred nearly every design decision. The document also relied too heavily on a 16-outcome prior-work comparison, provided no new human-intervention result, and allocated more space to related work and an unexecuted search protocol than to the three studies.

## B.2 Corrected scientific gap

**FACT:** selective prediction, learning to defer, multi-expert assignment, interaction design, provenance, reviewability, corrective memory, precedent reuse, guideline adaptation, truth maintenance, access control, and transfer theory all exist. **INFERENCE:** their existence removes any defensible claim that the individual mechanisms are novel. **INFERENCE:** the frozen VEGO-AI outputs expose a claim-level coordination problem: the same contested fragment may require a competence judgment, an authority decision, a recorded rationale, and a later applicability decision.

Recent direct checks strengthen the benchmark design. [Wei, Cao, and Feng (2024)](https://proceedings.mlr.press/v235/wei24a.html) show that model–expert dependence matters to deferral; [Tailor et al. (2024)](https://proceedings.mlr.press/v238/tailor24a.html) characterize an available expert from a small context set; and [Nguyen, Do, and Carneiro (2025)](https://proceedings.iclr.cc/paper_files/paper/2025/hash/78df0f831fbe5854349dbdfccde7ee5d-Abstract-Conference.html) explicitly constrain workload distribution. **INFERENCE:** confidence-only routing is an insufficient comparator, reviewer qualification needs observations, and effort must be measured rather than assumed. None of these studies validates a VEGO-AI outcome.

**PROPOSAL — residual gap:** within the verified exploratory corpus, no evaluated approach was found that jointly provides, at the level of one assessment claim:

1. bounded review routing using separately evidenced reviewer competence and claim-scoped authority;
2. a judgment record carrying evidence, reasoning, dissent, provenance, and lifecycle state; and
3. later influence only after authorization and context-applicability checks, with a use receipt.

This is an integration-and-evaluation gap. It is not a field-wide absence claim. It is falsified by a directly comparable evaluated system or by failure of the integrated design to outperform the mature composite comparator without violating safety constraints.

## B.3 Gap-to-fix matrix

| Gap | Evidence of gap | Revision | Remaining blocker |
|---|---|---|---|
| Gap/RQ mismatch | *Whom* absent from current SQ1 | Proposed SQ1 includes an authorized reviewer and fixed budget | Supervisor approval |
| Competence/authority collapsed | Deferral predicts expert performance; governance assigns roles | Separate qualification score from mandate decision | Reviewer data and mandate owner |
| No strong Study-1 falsifier | All original arms were when-only | Add competence-blind matched-budget arm | Prospective labels |
| State-dependent replay invalid | Queue conditions change after each escalation | Restrict current replay; use queue-aware simulation later | Stateful implementation |
| Judgment under-specified | Label/comment cannot reconstruct applicability | Governed record plus reconstruction instrument | Instrument validation |
| Reuse comparator too weak | Retrieval alone is not the nearest mature assembly | Compare against retrieval + case precedent + authorization | Held-out target context |
| Revocation not operational | “Delete” does not prove downstream non-use | Dependency graph, zero revoked reliance tolerance, use receipt | Cross-context experiment |
| Integrated design open | Unit/assignment/order/training unspecified | Fixed four-arm blocked design and joint objective | Pilot-derived N only |
| Literature overstatement | Named competitors omitted | Concede and cite all neighbours | Full registered search and second screen |
| Evidence overclaim | Technical checks described as preliminary benefit | New result table labels technical, descriptive, and prospective states | Independent outcome study |
| Data discrepancy | Evaluation package: 179 scored rows, 165 inspection reports, 27 patterns; manuscript: 178 models, 26 patterns | All denominators retained with source labels | Documented selection/counting rule |
| Schedule infeasibility | Ethics/recruitment followed human analysis | Preparatory ethics/recruitment/pilot; integrated freeze moved earlier | Institutional lead times |

# C. One-page Experiment Plan

The controlled one-page plan is maintained as [`study1-one-page-plan.md`](study1-one-page-plan.md). Its core decision is to separate the already-completed **descriptive feasibility baseline** from the later **prospective human outcome benchmark**. The former can be reported now. The latter cannot begin until independent labels, reviewer qualification, authority, workload instrumentation, and ethics/data gates exist.

| Plan element | Controlled choice | Evidence state |
|---|---|---|
| Immediate question | Where and when can a review candidate be detected, and can one recorded correction propagate? | Answered descriptively/technically |
| Proposed Study 1 question | Which claim-level events should be reviewed, by which authorized reviewer, at a fixed attention budget? | PROPOSAL; wording approval pending |
| Data | Supplied Cheers/ParkWise package: 179 scored rows, 165 inspection reports, and 27 patterns; foundation manuscript separately reports 178 models and 26 patterns | FACT; denominator discrepancy retained |
| Current baseline | Stage inventory, recorded-review analysis, six-arm C0 replay, and one bounded correction | Completed and reproducible |
| Prospective comparator set | Never ask, always ask, deterministic random, uncertainty only, fixed threshold, competence-blind routing, and competence-aware authority-constrained routing | PROPOSAL |
| Primary budget | 10% of reviewer attention, with 5% and 20% sensitivity analyses | PROPOSAL; supervisor approval pending |
| Co-primary outcomes | Important-case capture and reviewer-conditional correctness at the fixed budget | Not yet measured |
| Stop conditions | Missing independent labels, reviewer competence, authority, or ethics/data clearance; breached budget/authority gate; simpler comparator equivalent | Hard gates |

The immediate supervisor decisions are therefore bounded: approve or revise the proposed SQ1 wording; confirm whether *whom* remains in Study 1; approve the primary and sensitivity budgets; nominate the qualification-set and mandate owners; and decide whether the next tranche remains descriptive or may proceed to prospective human evaluation.

# D. Executable Protocol

The command-level protocol is [`study1-executable-protocol.md`](study1-executable-protocol.md). It specifies source freezing, four analyses, expected hashes, acceptance checks, abort rules, and public/private release boundaries. The code path has a direct CLI regression test and a JSON Schema that forbids raw fragment text and outcome claims in a public correction directive.

| Step | Executable operation | Required receipt or abort |
|---|---|---|
| 1. Freeze | Hash the supplied archive and bind the private extraction root without modifying either source | Abort on source-hash drift |
| 2. Inventory | Run EXP-045 over the frozen four-stage outputs | Stage counts, denominators, and source hashes |
| 3. Review baseline | Run EXP-046 against the recorded project review | Separate evaluator and parser denominators; no gold-label claim |
| 4. Event adaptation | Build one canonical event table with eight signal values and observed/derived/unavailable status | Schema validation and stable event IDs |
| 5. C0 replay | Replay the same event table through six existing arms at 5%, 10%, and 20% budgets using seed `20260902` | Equal event set/budget, canonical hashes, second identical run |
| 6. Bounded correction | Apply one allowed, SHA-bound, development-only recorded correction without mutating the baseline | Exactly one match/change; deterministic score receipt |
| 7. Privacy gate | Scan tracked candidates for raw models, notes, identifiers, private URLs, absolute paths, and secrets | Zero prohibited findings |
| 8. Release boundary | Retain raw inputs/results privately; publish only code, schemas, synthetic fixtures, aggregates, and sanitized receipts | Draft PR only; no merge before human review |

The public correction directive accepts no raw fragment text and cannot assert independent truth, benefit, accuracy, causality, workload reduction, or policy superiority. Any attempt to use a stale hash, unsupported source type, unbounded match, or gold-label status fails closed.

# E. Preliminary Results

## E.1 Descriptive stage inventory

**FACT — EXP-045:** Stage 1 produced 6 candidate signals over 38 generated clusters and reported 7 of 40 reference constructs as unreached. Stage 2 produced 18 candidate signals over 28 clusters, carried 12 open questions, and recorded 59 missed reference guidelines against an evaluator denominator of 80. Stage 3 contained 491 alternative readings and 15 high-severity mistakes, giving 506 candidate signals across 165 case files. Stage 4 contained 11 trigger-like patterns among 27, but zero queue objects were materialised.

**INFERENCE:** all stages contain evidence that could support an escalation decision; only Stage 4 contains an intended hook, and that hook was not connected to a stored request in the frozen run. The numbers do not rank stages or show where intervention would improve outcomes.

## E.2 Recorded project review

**FACT — EXP-046:** the review workbook contains 186 Stage-2 rows: 169 agent-written guidelines plus 17 required guidelines added because no run had written them. Of the 169 agent-written guidelines, 68 were not accepted in full (46 partial, 21 wrong, 1 uncertain), or 40.2%. The source-text parser separately counted 78 non-comment reference lines, 59 unmatched. The EXP-045 evaluator denominator of 80 and source-parser denominator of 78 answer different questions and remain separate. Of 915 recorded compliance judgments, 120 were changed. Change rates were 12/658 for *Satisfied*, 75/162 for *Partially-Satisfied*, and 33/95 for *Not-Satisfied*. Of 104 uncovered-fragment judgments, 27 were changed.

**FACT — retrospective rule:** escalating every non-*Satisfied* compliance judgment would flag 257/915 (28.1%) and include 108/120 recorded changes (90.0%). **INFERENCE:** this rule is a useful baseline for attention-versus-retrospective-change coverage. It is not a prospective accuracy estimate because the recorded review is project-owned, selected non-randomly, and lacks independent adjudication.

**FACT — model-level association:** the VEGO-AI score and available course grade had Pearson `r=0.2501` across 164 paired rows. **INFERENCE:** they order models differently and should not be silently treated as the same construct. Neither is an item-level truth label.

## E.3 Six-arm C0 replay

**FACT:** a canonical adapter produced 1,874 events: 6 template, 18 guideline, 1,839 case-inspection, and 11 variability-classification events. The configured budgets were 93, 187, and 374 at 5%, 10%, and 20%. Never-ask selected zero; always-ask, random, uncertainty-only, and fixed-threshold arms consumed their budgets. The proposed joint policy selected zero at all budgets.

**INFERENCE:** the zero is a meaningful readiness result. The joint policy requires constructs the archive does not observe—reviewer competence, claim-scoped authority, consequence, live queue state, disagreement, and future reuse value. Treating them as available would fabricate evidence. The result is not evidence that the design is ineffective.

**FACT — determinism:** two runs produced identical canonical hashes for the event table, manifest, replay ledger, and sanitized summaries.

## E.4 One recorded correction

**FACT:** one already-recorded human review marked a case fragment classified as *Alternative* as a *Language Mistake*. The bounded replay matched the fragment by SHA-256, changed exactly one fragment and one scoring contribution, and left the baseline immutable. The score changed from 17.5/27 (64.8%) to 16.5/27 (61.1%); the −1.0 direction is expected because false positive credit was removed. Alignment with that recorded review changed from 0 to 1 by construction. Two independent executions were byte-identical.

**Permitted conclusion:** a recorded correction can be technically propagated through the frozen scoring representation with a deterministic receipt. **Forbidden conclusions:** the human was independently correct; the lower score is more accurate; a human improved the system; the policy reduced burden; or the result generalises.

## E.5 Measurement and effort scorecard

The public metric receipt recomputes each value from sanitized category totals and fails if a denominator, category sum, matched budget, or paired-run indicator is inconsistent.

| Question | Formula | Current result | Permitted use |
|---|---|---:|---|
| How much H2 review is requested? | selected / eligible | 257/915 = **28.1%** | Descriptive review load |
| How many recorded changes fall inside that set? | changed selected / all recorded changes | 108/120 = **90.0%** | Retrospective recorded-change coverage; not recall |
| How often was a selected item changed in the old review? | changed selected / selected | 108/257 = **42.0%** | Retrospective recorded-change yield; not precision |
| What review volume was not selected? | (eligible − selected) / eligible | 658/915 = **71.9%** | Replay volume not selected; not observed effort reduction |
| Can the computation be repeated? | canonical artifact hashes equal across runs | **PASS** | Technical reproducibility only |

Human effort has not been observed. The prospective benchmark must therefore record reviewer minutes per 100 eligible claims, interruptions per 100 claims, queue delay, abandonment, and useful adjudicated corrections per reviewer-hour. Independent labels are required for important-case capture and reviewer-conditional correctness. None may be back-filled from the project-owned recorded review.

# F. Revised Proposal

The revised proposal master is [`proposal-v2-candidate.md`](proposal-v2-candidate.md). It differs structurally from the prior 30-page extended review:

- a shorter problem-first literature synthesis replaces paper-by-paper exposition;
- VEGO-AI receives a dedicated baseline subsection;
- the error analysis and preliminary results are integrated as motivation, not used as ground truth;
- current and proposed RQ wording are separated;
- every study has an artifact, comparator, unit, outcome, analysis, and falsifier;
- the integrated four-arm design is fixed except for pilot-adjusted sample size;
- ethics, recruitment, pilot, and review execution occur before human outcome claims;
- decorative figures are removed and evidence-functional figures retained;
- AI assistance, supervisor co-authorship of the prior-work manuscript, and unresolved denominators are disclosed.

# G. Arnon Comment-resolution Matrix

The source DOCX contains 26 unresolved comment objects. “Resolved in candidate revision” means the text/design response exists below; it does not change the original comment object's state or claim Arnon accepted the response.

| Comment | Original issue | Resolution in candidate revision | Status |
|---:|---|---|---|
| 0 | “Involvement?” on title | Retain *judgment* as the candidate term because the research artifact is a governed decision record; surface *involvement* as the alternative. | OPEN QUESTION for supervisor |
| 4 | Introductory material not relevant there | Remove meta-organisation prose from the problem opening. | Resolved in candidate revision |
| 5 | Mixed topics, some not core | Rebuild Chapter 1 as problem → baseline → human decision → gap. | Resolved |
| 6 | Guideline operationalization introduced before reader knows it | Define it in plain language at first use and move cross-domain detail to related work. | Resolved |
| 7 | Incorrect implication that no HITL studies exist | Explicitly concede mature HITL, mixed-initiative, deferral, and oversight literatures. | Resolved |
| 8 | Unclear agentic-oversight paragraph | Replace with one operational sentence about where human decisions enter the VEGO-AI lifecycle. | Resolved |
| 9 | Relevance of presence/expertise/authority distinction unclear | Tie each term to a Study-1 variable and comparator. | Resolved |
| 11 | Unclear deferral paragraph | Define selective prediction, learning to defer, and reviewer assignment separately. | Resolved |
| 12 | Second unclear construct in same passage | State what each tradition optimises and its missing VEGO-AI variable. | Resolved |
| 13 | Lifecycle meaning unclear | Define active, contested, expired, superseded, and revoked with observable effects. | Resolved |
| 14 | Residual-question sentence unclear | Replace with one falsifiable three-part integration gap. | Resolved |
| 16 | Concrete example leads to solution too early | Move the example to methodology and use it only as a worked protocol trace. | Resolved |
| 18 | Purpose of six-readings example unclear | Remove the six speculative readings; retain only the recorded correction and its bounded role. | Resolved |
| 21 | Heading too long and not representative | Use “Research Questions and Contributions.” | Resolved |
| 24 | Objectives too vague | Rewrite each objective as artifact + comparator + outcome + failure condition. | Resolved |
| 25 | Section summary irrelevant | Remove summary box. | Resolved |
| 34 | Summary material redundant | Remove and let the RQ table carry ownership. | Resolved |
| 37 | Scenario instantiation belongs in methodology | Move Scenario A/B and data boundaries to Methodology. | Resolved |
| 38 | Scenario summary redundant | Remove. | Resolved |
| 39 | Section summary redundant | Remove. | Resolved |
| 41 | VEGO-AI needs a subsection | Add “VEGO-AI baseline and decision points.” | Resolved |
| 42 | Purpose of design-science paragraph unclear | State how build/evaluate cycles prevent software completion from becoming a research result. | Resolved |
| 43 | Evaluation-consequence summary redundant | Remove; retain concise claim boundary in each study. | Resolved |
| 44 | Search strings too general | Use locked mechanism + setting query families; record transformations and named-neighbour searches. | Partially resolved; full execution pending |
| 45 | Why include taxonomy if it is not a contribution? | Treat it solely as a search/classification aid and move detail outside the core proposal. | Resolved |
| 46 | Review summary redundant | Remove. | Resolved |

# H. RQ-to-study Traceability

## H.1 Wording control

The current RQ block remains the drafting baseline and is not represented as approved. The proposed wording below is a response to the strict review; it requires supervisor approval.

| RQ | Proposed wording | Study ownership | Artifact | Primary evidence | Falsifier |
|---|---|---|---|---|---|
| U-RQ | How can claim-level human judgment be selectively requested, governed, and safely reused in agentic variability exploration so that the combined process improves decision quality without exceeding declared attention and safety constraints? | Integrated study | Governed human-judgment layer around VEGO-AI | Joint objective across reviewer-conditional correctness, governance, and safe reuse under a fixed budget | Governed arm fails to beat ordinary HITL on the declared joint objective or violates a ceiling |
| SQ1 | For which claim-level VEGO-AI assessment events should review be requested, and to which authorized reviewer, to maximise reviewer-conditional decision correctness and important-case capture at a fixed attention budget? | Study 1 | Escalation and reviewer-routing policy | Prospective, held-out events with qualification and authority data | Competence-blind or simpler threshold is equivalent/better, or safety ceiling breached |
| SQ2 | What minimum representation of a human judgment preserves enough evidence, reasoning, dissent, provenance, authority, and lifecycle state for another person to reconstruct and contest the decision? | Study 2 | Governed Judgment Record and conformance suite | Blinded reconstruction instrument, correction success, capture cost | Structured provenance record is equivalent at lower cost, or independent implementation fails |
| SQ3 | Under what authorization, validity, and context conditions may a prior judgment influence a new guideline-operationalization case without unsafe transfer or reliance on revoked evidence? | Study 3 | Ordered reuse gate and context descriptor | Held-out target cases with scope/revocation tests | Mature composite comparator is equivalent/better or unsafe-influence ceiling breached |

## H.2 Evidence-state map

| Study | Exists now | Missing before outcome claim | September status |
|---|---|---|---|
| Study 1 | Event schema, stage inventory, six-arm descriptive replay, one deterministic correction replay | Independent labels, competence, authority, time/burden, prospective allocation | Technical/descriptive feasibility demonstrated |
| Study 2 | Draft record and lifecycle concepts in existing governed contracts | Validated reconstruction instrument and independent implementer | Design hypothesis |
| Study 3 | Draft reuse gates and receipts in existing contracts | Frozen source store, held-out contexts, authorization/applicability outcome labels | Design hypothesis |
| Integrated | Comparator set and fixed design specification | Mature Study 1–3 artifacts, ethics, participants, pilot N | Planned |

# I. Strict 0–100 Validation Report

## I.1 Score

**Self-audit score: 79/100 — ready for supervisor review, not submission-ready.** This is a traceable internal assessment, not an external committee score or supervisor acceptance.

| Dimension | Weight | Prior | Current self-audit | Rationale |
|---|---:|---:|---:|---|
| Methodological rigour and feasibility | 35 | 18.9/35 | **26/35** | Current replay is reproducible and bounded; future design, comparators, constants, and falsifiers are specified. Human outcome evidence and pilot-derived N remain missing. |
| Gap and contribution logic | 25 | 16/25 | **21/25** | Named neighbours are conceded; gap is integration/evaluation; SQ1 now carries *whom*. RQ wording is unapproved and systematic search incomplete. |
| Evidence integrity | 25 | 15.5/25 | **20/25** | Source hashes, denominator invariants, paired-run hashes, negative result, non-random review, and AI role are explicit. Independent labels and second-reviewer screening remain absent. |
| Structure and presentation | 15 | 10.2/15 | **12/15** | Proposal is problem-led, methodology-heavy, and visually reduced. Final supervisor terminology and institutional format review remain open. |

## I.2 Hard-gate audit

| Gate | Result |
|---|---|
| Source hashes recorded; original inputs unchanged | PASS |
| Every preliminary result mapped to frozen output or receipt | PASS |
| Fact/inference/proposal/open-question separation | PASS |
| No accuracy, benefit, burden, causality, or superiority claim from descriptive evidence | PASS |
| Six policy arms share the canonical event table and matched budgets | PASS |
| Two identical C0 runs and two identical correction runs | PASS |
| Metric formulas and category denominators independently recomputed | PASS |
| Raw student material and private review content excluded from tracked artifacts | PASS |
| All 26 Arnon comments have a disposition | PASS; acceptance pending |
| All 115 atomic supervisor rows preserved in canonical register | PASS; supervisor validation pending |
| Named adjacent literatures cited and conceded | PASS for targeted set |
| Registered review fully executed with second screening | FAIL / open |
| Independent human ground truth and adjudication | FAIL / open |
| Supervisor approval of title, RQs, thresholds, and Hebrew meaning | FAIL / open |
| Prospective human-outcome result | FAIL / out of current scope |

## I.3 What would raise the score

1. Supervisor approval or revision of the RQ block, title term, budgets, competence measure, and authority owner.
2. Independent blinded labels with adjudication and a reported inter-rater statistic.
3. Complete registered search execution, dual screening, and a version-of-record reconciliation receipt.
4. Pilot-derived sample size and validated Study-2 reconstruction instrument.
5. A held-out target context for Study 3 and a successful scope/revocation safety test.

# Final account

## Inspected

- the supplied proposal PDF, all 30 rendered pages, its editable near-match, and its 68-entry reference audit;
- all 26 inline Arnon comments and the prior response ledger;
- the English/Hebrew September 2 requirements record and the 115-row atomic checklist;
- the supplied VEGO-AI working manuscript, all 10 rendered pages, including its publication placeholders;
- the frozen implementation archive and its agent outputs, review workbooks, and evaluation records in a private ignored workspace;
- the strict committee review, SLR protocol/assessment, current Study-1 contracts, policy engine, tests, and release/privacy gates;
- primary authoritative records for the targeted missing literatures.

## Changed

- added one bounded human-correction replay module, direct CLI, JSON Schema, synthetic fixture, and regression tests;
- added a source-hash manifest, sanitized result record, literature verification log, one-page plan, executable protocol, revised proposal source, and this evidence package;
- added a fail-closed denominator validator and public-safe metric receipt for the supervisor-facing measures;
- reframed the gap as an integration-and-evaluation claim and aligned the proposed RQs and studies;
- fixed the prospective benchmark, integrated design, quantitative defaults, work plan, AI disclosure, and comment dispositions.

## Executed and obtained

- baseline repository suite before changes: 344 tests passed;
- EXP-045 stage inventory and EXP-046 recorded-review analysis on the supplied frozen archive;
- six-arm C0 replays at 5%, 10%, and 20%, twice, with matching hashes;
- one bounded recorded-correction replay, twice, with matching hashes;
- focused new tests for transformation scope, stale-input rejection, privacy, schema validity, and direct CLI execution.
- an independent 3 September validation rerun of EXP-045, EXP-046, paired C0 replay, paired correction replay, and the metric receipt.

## Still open

Supervisor approval, RQ wording, title terminology, reviewer qualification and authority definitions, ethics/data access, independent labels, prospective burden/outcome evidence, complete systematic-search execution, the 179-scored/165-report/27-pattern versus 178-model/26-pattern discrepancy, a validated reconstruction instrument, and a held-out transfer context.

## Overall status and readiness

**Ready for supervisor review. Not approved, not submission-ready, and not evidence of human benefit.** The immediate descriptive baseline and technical intervention feasibility question have defensible answers. The research contribution remains a proposal until prospective evaluations pass.

## Three highest-priority next actions

- Confirm the title/RQ wording and whether *whom*, competence, and authority remain in Study 1.
- Freeze an independently labelled calibration/test sample plus reviewer qualification and claim-scoped mandate data.
- Complete the locked literature protocol with a second screener before revising the gap claim.
