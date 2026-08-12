# Proposal v0.4 — Examiner-Level Review Findings

Status: **independent adversarial review of the v0.4 package.** 36 findings: 5 critical, 15 high, 11 medium, 5 low.

This review was run as if by a doctoral examiner reading the package cold. It reports defects only — there is no praise and no generic advice. Each finding quotes the text it refers to and states a specific repair.

> **Scope note.** Four further review passes (claim-boundary sweep, requirement conformance against E1–E15, internal-consistency sweep, and the analysis of Iris's marked-up paper) did not complete because the session hit its usage limit. The findings below therefore come from the academic-quality pass alone, and should be treated as a floor, not a ceiling. The remaining passes are still worth running.

---

## The five critical findings

These are the ones that would be raised in the room. They are not wording problems.

### C1. Gap Argument

**Where:** Chapter 3 - Gap and Research Questions.docx — §3.2 preamble and §3.11 evidence table

> every statement of the form "no established approach addresses X" is a candidate claim for Chapter 2 to establish or correct.

**The problem.** The chapter's sole job is to establish that the questions are open, and it concedes in its own front matter that it has not done so. The literature searches QL-01–QL-05 are unexecuted, so every openness claim in §3.2 is, by the document's own admission, a hypothesis about the literature rather than a finding. §3.11 repeats this: 'Literature searches QL-01–QL-05 | Protocol-ready, not executed; §3.2 openness statements are candidate claims'. An examiner cannot accept a gap chapter that self-certifies its central claims as unverified.

**Repair.** Either execute QL-01–QL-05 before Chapter 3 is defended, or rewrite every universal claim in §3.2 to the scope the evidence actually covers: replace 'no framework in this line classifies…' with 'none of the N sources in the seed corpus classifies…', and delete 'no established approach' phrasing entirely. A bounded, true claim beats an unbounded, unverified one.

### C2. Gap Argument

**Where:** Chapter 3 §3.3, gap statement (bolded paragraph) and §3.2.5 positioning table

> The design knowledge for connecting selective expert intervention, structured judgment capture, and scope-aware reuse in agentic AI assessment does not exist in tested, generalizable form

**The problem.** This is Arnon's E4 criticism recurring, not fixed. The gap is stated in the vocabulary of the proposed solution: 'selective expert intervention', 'structured judgment capture', 'scope-aware reuse' are the three artifacts of Studies 1–3. A gap defined by the solution's own coinages is unfalsifiable by any literature search — no prior work can be found to have 'connected' three components nobody else names. The §3.2.5 table makes the circularity explicit: the 'Does not address' column entries are verbatim the sub-questions ('When to request expertise; what to retain; whether it may be reused' → 'Bears on SQ1, SQ2'). The literature was asked the proposal's questions and reported not to answer them; that is a category mismatch, not a gap.

**Repair.** Restate the gap as an unanswered question about a phenomenon, in terms a prior paper could in principle already have answered: e.g. 'It is not known whether an expert's ruling on the legitimacy of a deviation predicts the correct ruling on a similar deviation in a different course/corpus/diagram type, nor what information about the original ruling is needed to make that prediction.' Then show that the literature has not answered *that*. Rebuild the §3.2.5 'Does not address' column from what each body of work claims and fails to deliver on its own terms, not from SQ1–SQ3.

### C3. Methodology

**Where:** Proposal v0.3 (current).docx — 'Chapter plan and current status' table, row 4; and absence of Chapter 4 in the package

> 4 | Research Methodology | Not started — deliberately | Design Science per Prof. Penina's course; per-RQ study/artifact/design/evaluation. Nine artifact options prepared, none selected

**The problem.** There is no methodology. Chapter 4 is 'Not started — deliberately'. The proposal therefore contains no unit of analysis, no procedure, no analysis plan, no comparator, no sample-size justification, and no validity controls for any of the three studies. The Three-Study Contract (a separate, non-incorporated document in 01_Research_Questions) supplies 'Units of analysis', 'Data and evidence' and 'Primary measures' but no analysis plan and no validity section either. As submitted, the proposal cannot be assessed for doctoral adequacy on criterion 3 because the relevant material does not exist in any form.

**Repair.** Chapter 4 must exist before defence. Minimum per study: one named unit of analysis; the data source with N; the procedure as a sequence a third party could execute; the dependent and independent variables with instruments; the statistical or qualitative analysis plan naming the specific test/coding scheme; and a threats-to-validity subsection. Also: 'Nine artifact options prepared, none selected' after a year of work is itself a finding — commit to one.

### C4. Research Questions

**Where:** Chapter 3 §3.4 (U-RQ) and §3.8 ('An open decomposition question')

> none of them takes reliability of the co-reasoning itself as its object, even though the main question names it as the outcome. Either reliability is emergent from the three, or it requires separate treatment.

**The problem.** The main question's outcome construct — 'reliable human–AI co-reasoning' — is never defined, never operationalised, and by the proposal's own admission is measured by no study. 'Reliable' appears eight times in Chapter 3 and in two of the three title candidates with no definition; the chapter defines 'variability' and 'guideline operationalization' but not the outcome term of its own headline question. §3.8 states the problem and then defers it to a supervisor meeting ('This is a live question for D-RQ-01'). Deferring the central dependent construct to a decision meeting is not a research design, and a U-RQ phrased 'How can X be done…?' has no disconfirming result at all — it presupposes X can be done.

**Repair.** Choose one of two repairs and write it in: (a) define reliability operationally (e.g. agreement between the human–AI joint decision and an adjudicated expert panel, plus stability of that agreement across repeated runs and across reviewers), give it a measure, and assign it to a named study; or (b) delete 'enabling reliable human–AI co-reasoning' from the U-RQ and stop claiming it as the outcome. Do not submit with the term in the headline and in no study.

### C5. Methodology

**Where:** Chapter 3 §3.11 and Chapter 6 §6.2.4 (Y1 B2) and §6.3.1 gate G-LBL

> the labelling protocol's preferred target is 30–50, which exceeds the 24 generalization-safe candidates currently available and therefore requires either a second labelling round or an extension of the candidate set

**The problem.** The entire quantitative evidence base for a three-study doctorate is ≥20 adjudicated labels drawn from a pool of 24 candidates, and that same set is simultaneously the gold set for Study 1's coverage-versus-burden evaluation and 'the evidence base for later transfer testing' in Study 3 (§6.2.4 'Advances'). Twenty items cannot support a coverage/burden trade-off frontier, an inter-rater reliability estimate, and a cross-context transfer classification. Chapter 6 concedes the preferred target is unreachable from the existing pool. There is no power analysis or target-N derivation anywhere in the package.

**Repair.** State a target N per study derived from the smallest effect worth detecting (Study 1) and from the number of judgments needed per cell of the domain-specific × transferable grid (Study 3). Chapter 1 §1.1 reports the motivating corpus at 178 student models — explain in Chapter 4 why only 24 of the derived items are 'generalization-safe' and what procedure would expand the pool. Note also that the sentence conflates items with labels: a 'second labelling round' over the same 24 candidates raises labels-per-item, not the candidate count.

---

## High-severity findings

### H1. Validity — Chapters 1, 3 and 6 — no threats-to-validity section exists; Chapter 6 §6.2.5 defers one

> Error and validity analysis, including the threats register for Study 1.

Threats to validity are not engaged superficially — they are absent. The strings 'threats to validity', 'construct validity', 'internal validity', 'external validity', 'confound' and 'bias' occur zero times across Chapter 1, Chapter 3 and Chapter 6. The only appearance is a future deliverable in Y1 B3. Meanwhile §6.6 gives ten schedule risks (R1–R10) with triggers, effects, mitigations and owners. The ratio — ten project risks, zero inferential threats — is exactly what an examiner will name: the candidate has thought hard about delivery risk and not at all about the risk of being wrong.

**Repair.** Add a threats section to Chapter 3 (or Chapter 4 when written) with the same table discipline as §6.6, covering at minimum: construct validity of the substantial/occasional distinction, the anchoring confound (below), single-corpus/single-model dependence, researcher-as-instrument, and the reference-standard ceiling. Each with the specific control that addresses it, not a mitigation slogan.

### H2. Validity — Chapter 3 §3.6 ('Core reasoning is inside the question (E9)') read against Chapter 6 §6.2.3/§6.2.4 'blinded evaluation set'

> The expert responds to the system's own core reasoning — the argument the agentic process gives for flagging a deviation — and may endorse, correct, or reject that reasoning, not merely the verdict.

SQ2's central design commitment creates the study's most likely alternative explanation, and the proposal never names it. If the expert is shown the system's own argument before ruling, anchoring and automation bias are the leading rival hypothesis for any observed expert–system agreement, and the expert cannot be blinded to the machine origin of the judgment they are asked to endorse. The plan says 'blinded evaluation set' and 'blinded labelling' repeatedly without ever stating what the reviewer is blinded to. These two commitments are in direct tension and the tension is unaddressed.

**Repair.** Design the confound out and say so: split the expert task into an independent-first phase (expert rules with the deviation but not the system's reasoning) followed by a reveal phase (system reasoning shown, expert may revise, revision recorded). The difference between the two is a measurement of anchoring, which converts the threat into a result. Define 'blinded' explicitly wherever it appears — blinded to condition, to system verdict, to the other reviewer, or all three.

### H3. Validity — Chapter 3 §3.7, §6.2.8, §6.2.10 — 'leakage controls' used five times, never defined

> leakage controls between the context that produced a judgment and the context in which it is evaluated

'Leakage controls between the context that produced a judgment and the context in which it is evaluated' is the load-bearing validity mechanism for SQ3 — it is what makes any transfer claim credible — and it is stated identically five times across two chapters without once being operationalised. A leakage control is a concrete splitting rule; the proposal never says what unit must not appear on both sides. Same defect for 'sealed holdout' (§6.2.4, §6.2.10), which is named but never given a sealing procedure or an unsealing authority.

**Repair.** State the splitting rule as a rule: e.g. 'no student, no course offering, no guideline clause, and no expert may contribute items to both the judgment-producing set and the transfer-evaluation set; splits are made at the course-offering level and hashed before any judgment is captured.' Name who holds the holdout key and what event authorises unsealing.

### H4. Research Questions — Chapter 3 §3.11, all three falsification statements

> SQ1 fails if no intervention policy achieves acceptable coverage of important uncertainty within a defensible expert budget — a finding worth reporting.

None of the three stated disconfirming results is operational. SQ1: 'acceptable coverage' and 'defensible expert budget' are undefined, and the claim is universally quantified over policies ('no intervention policy'), which no finite experiment can establish — you can only show the policies you tried failed. SQ2's first clause is a design-existence claim over the author's own stipulated desiderata and is trivially satisfiable by adding fields to a record, so it cannot fail; its second clause ('governance costs exceed the value of reuse') is the only falsifiable part and neither term has a unit or an instrument anywhere in the package. SQ3: 'discriminate reliably' has no agreement threshold, no rater count, no item count.

**Repair.** Replace each with a pre-registered numeric statement and a named comparator. SQ1: 'SQ1 is disconfirmed if no policy on the tested frontier surfaces ≥X% of adjudicated-important deviations at ≤Y% review rate, where the threshold-only baseline achieves (X₀, Y₀).' SQ2: define governance cost (expert + adjudicator minutes per captured judgment) and reuse value (adjudicated-important deviations correctly resolved per captured judgment) and state the ratio at which SQ2 fails. SQ3: state the agreement statistic and threshold (e.g. two independent raters, κ ≥ 0.6 on the domain-specific/transferable classification over ≥N judgments).

### H5. Research Questions — Chapter 3 §3.5 (SQ1) read against its own 'Why this is open' paragraph

> Between them lies a policy space — which uncertainty signals to trust, what "important" means for a deviation, what dosage of review a workflow can absorb, when a request expires or escalates.

SQ1's success criterion contains an undefined term whose definition is one of the study's results. The question requires that 'important uncertainties are addressed', and §3.5 then lists 'what "important" means for a deviation' as part of the open policy space to be determined. The evaluation therefore cannot be specified in advance without deciding the thing being researched, which means the criterion can be tuned after the data are seen.

**Repair.** Fix the importance label independently and before the policy work, from a source outside the policy: e.g. a deviation is 'important' iff independent adjudicators disagreed about it, or iff its misclassification changes the assigned grade band. Then the policy is evaluated against a label it did not define. Move 'what makes a deviation important' out of SQ1's answer space and into Chapter 4 as a measurement decision.

### H6. Methodology — Chapter 6 §6.2.5 (Y1 B3, Study 1 evaluation) and Three-Study Contract, Study 1 'Primary measures'

> Primary measures | Requirements-to-artifact coverage; trigger/eligibility coverage; review-rate and burden projections; routing completeness; escalation/timeout behavior; decision traceability; missed-important-case criteria for later empirical testing.

Study 1 has no comparator and does not measure the quantity SQ1 asks about. The 'controlled evaluation' names no control condition — threshold-only routing is attacked twice (§3.2.3, §3.5) but never designated as the baseline, and no random-sampling or review-everything ceiling is specified. Without a comparator, a coverage-versus-load curve describes one system rather than evaluating it. Separately, the contract's Study 1 measures are 'review-rate and burden projections' — burden is modelled, not measured — while SQ1's falsification criterion is a claim about real expert burden. As designed, Study 1 cannot answer SQ1.

**Repair.** Name three conditions — proposed policy, confidence-threshold routing, and uniform random sampling at matched review rate — and evaluate all three on the same items. Add a human arm with N reviewers, randomised condition assignment, and measured time-on-task; or, if that is out of budget, restate SQ1 as a question about a modelled attention budget and say so in the question's wording.

### H7. Methodology — Three-Study Contract, Study 2 'Primary measures'; Chapter 6 §6.2.7 exit criteria

> Schema/contract validity; provenance completeness; validation and reconciliation coverage; conflict/authority-rule coverage; retrieval explanation completeness; unsafe-reuse rejection; scope/expiry/revocation enforcement; bounded convergence.

Every Study 2 measure is a self-conformance check: schema validity, provenance completeness, validation coverage, conflict-rule coverage, retrieval-explanation completeness, unsafe-reuse rejection, scope/expiry/revocation enforcement. Each of these is a property the designer specifies and then verifies against his own specification. None can come out wrong in a way that is informative about anything outside the artifact. A doctoral study whose measures cannot disconfirm its own design is a conformance test suite. §6.2.7's exit criterion confirms this — 'Every SQ2 lifecycle stage, authority rule, and unsafe-reuse control maps to an inspectable artifact and a validation' — which is a coverage statement about the build, not a result.

**Repair.** Add at least one measure whose value is not under the designer's control: e.g. the proportion of real expert rulings that the schema can represent without loss (coded blind by a second rater against verbatim expert rationales), and the proportion of expert–expert disagreements the conflict model resolves the way a third adjudicator does. Both can come out badly, which is what makes them measures.

### H8. Methodology — Chapter 6 §6.2.6 (Y1 B4, Study 2 design frozen) vs §6.2.8 (Y2 B2, expert panel)

> Study 2 design frozen and preregistered: the structured judgment schema (including the system's own core reasoning, not only the expert's verdict); source-grounded verification and challenge protocol; conflict, adjudication, and authority rules

The evidence order is inverted for SQ2. SQ2 asks what must be captured from an expert's ruling, but the judgment schema is frozen a full year before any expert is observed producing a ruling. The representation's adequacy is therefore assumed at design time and only tested against itself afterwards. No qualitative method — think-aloud, interview, rationale coding — appears anywhere in the plan, despite the object of study being expert reasoning.

**Repair.** Insert an elicitation study before the schema freeze: 8–12 experts adjudicating real deviations with think-aloud protocol, rationales transcribed and open-coded, the schema derived from the coding and reported with the coding scheme and inter-coder agreement. This is also the cheapest doctoral-grade empirical contribution available given the label shortage, and it does not depend on gate G-LBL.

### H9. Internal Contradiction — Chapter 3 §3.2.3 prose vs §3.2.5 positioning table, row 3

> Human-in-the-loop & oversight [2, 27, HITL-001, HAI-001, GOV-001] | Human involvement helps; general mechanisms and governance expectations exist

The summary table asserts precisely the claim the prose six lines earlier says it is not asserting. §3.2.3 goes out of its way to adopt the weaker premise, then the table's 'Establishes' column states the stronger one as established. An examiner reading the table alone gets an unsupported claim; an examiner reading both gets a contradiction in a chapter whose whole credibility rests on claim discipline.

**Repair.** Change the table cell to match the prose: 'Human oversight is expected and studied; general mechanisms and governance expectations exist.' Delete 'Human involvement helps.'

### H10. Contribution Framing — Chapter 1 §1.5 'Design knowledge' paragraph; Three-Study Contract 'Intended contribution' row

> Design knowledge — the primary intended contribution, on which the thesis stands or falls: intervention criteria and attention-budget policies specifying when an agentic process should interrupt an expert; a representation for expert judgment that preserves case-grounding, scope, contestability, and attributable authority

The three-way split (design knowledge / artefacts / empirical evidence) is the right structure, but the design-knowledge items are stated as artifact components at one level of abstraction, not as knowledge claims. 'Intervention criteria and attention-budget policies', 'a representation for expert judgment', 'criteria distinguishing…' are all things to be built. Design knowledge is a conditional — in context C, mechanism M produces outcome O for reason R — and none of the three is in that form. The contract is worse: Study 1's intended contribution is 'A reusable selective-intervention architecture', which is an artifact, and Study 2's is a seven-adjective list.

**Repair.** Restate each as a technological rule that could be wrong. Example for SQ1: 'In agentic assessment under a bounded review budget, routing on predicted expert disagreement rather than on model confidence yields higher coverage of adjudicated-important deviations at equal review rate, because model confidence is uncalibrated with respect to interpretive difficulty.' Do the same for SQ2 and SQ3. Then the thesis defends three propositions, not three builds.

### H11. Gap Argument — Chapter 1 §1.3 read against Chapter 3 §3.9

> What the framework does not yet have is any governed means of accepting the human involvement it identifies as needed: no policy for deciding which of its many uncertain judgements warrant an expert's time; no representation for what the expert says once asked, beyond a corrected label

E4 recurs at the instance level. §3.9 insists VEGO-AI is 'motivating case rather than object of study', but §1.3 enumerates the gap as a list of VEGO-AI's specific missing features — no routing policy, no representation, no reasoning record, no provenance/scope/revocation. If the gap is the feature backlog of one system, the object of study is that system, and the contribution is its next release. Compounding this, both studies are built inside VEGO-AI, evaluated on its corpus, and the platform is authored by both supervisors.

**Repair.** Rewrite §1.3 to state the missing capability generically ('systems that detect deviations and flag uncertainty generally have no governed path from the flag to a retained, scoped ruling'), then cite VEGO-AI as one instrumented instance where the absence is directly observable, and name at least one independently-authored system exhibiting the same absence. One instance is an anecdote; two is a pattern.

### H12. Research Questions — Chapter 3 §3.6 (SQ2) and §3.7 (SQ3) wording

> How can expert judgment be reused and transferred across different guideline-operationalization contexts without unsafe generalization or loss of human authority

SQ2 and SQ3 share a verbatim tail — 'without unsafe generalization or loss of human authority' — and both are about reuse. The only wording difference is 'across different guideline-operationalization contexts'. An examiner will ask why these are two questions rather than one question with two settings. §3.6 supplies the intended distinction in prose ('the point where "may it be reused" becomes "does reuse hold up"') but the question text does not carry it, so the sub-questions are not separable as written.

**Repair.** Make SQ2 purely representational and governance-facing — end it at '…so that a later reuse decision can be made, audited, contested and revoked' and remove 'reused' as SQ2's outcome. Reserve all reuse *outcomes* for SQ3, and drop the duplicated tail from SQ3 since it is now SQ2's territory.

### H13. Research Questions — Chapter 3 §3.7, SQ3 wording; Chapter 6 §6.4.4

> first in software/modeling and, when governance and access permit, in healthcare?

SQ3 contains an institutional scheduling clause inside the research question, and the plan already expects that clause to be void. 'when governance and access permit' is a project risk, not a scientific condition, and §6.4.4 records 'On present evidence the checkpoint resolves to Plan B' with all six medical gates at zero. A question whose second half the plan expects not to be executed should not be in the question.

**Repair.** Delete the clause. SQ3 becomes 'How can expert judgment be transferred across guideline-operationalization contexts, and what distinguishes judgments that transfer from those that must stay confined?' Move the healthcare instantiation to §3.10 scope and Chapter 4 as an optional additional setting. This also removes the appearance of a medical doctorate that has not obtained medical access.

### H14. Validity — Chapter 3 §3.10 (out of scope) read against §3.11 and the G-LBL gate

> any claim that captured judgment is ground truth — captured judgment is governed evidence, contestable by design

Two commitments are irreconcilable and never reconciled. §3.10 rules out treating captured judgment as ground truth — it is 'contestable by design'. But every quantitative claim in the programme is gated on adjudicated expert labels serving exactly as the reference standard. If the reference is contestable, every agreement figure is agreement with a contestable standard, and the 'gate to any quantitative claim' framing implies the labels deliver truth.

**Repair.** Name the reference standard for what it is — consensus of adjudicated experts — and report the ceiling alongside every system–expert figure: expert–expert agreement before adjudication. Where the two experts disagreed, no system score is interpretable, and that subset should be reported separately rather than folded in after adjudication.

### H15. Internal Contradiction — Chapter 6 §6.2.2 (Block 0 deliverables) vs §6.3.2 (block-to-gate dependency table, row 'Y1 B1 (Chapter 2)')

> Y1 B1 (Chapter 2) | G-LIT | No novelty or review-completeness claim may appear anywhere in the proposal or thesis; Chapter 3's gap statements remain candidate claims

The plan contradicts itself about Chapter 2 and, in doing so, schedules the proposal for submission with its gap chapter formally unsupported. §6.2.2 has Chapter 2 drafted in Block 0 (Aug–Sep 2026); §6.3.2 says Chapter 2 cannot start until G-LIT, and G-LIT does not clear until the searches execute in Y1 B1 (Oct–Dec 2026). Meanwhile §6.5.3 targets proposal submission at 'Block 0 / early Y1 B1' — i.e. before the searches run. §6.6 R5 warns against exactly the failure this schedule creates.

**Repair.** Pick one. Either move search execution into Block 0 and submit after G-LIT clears, or move the submission target to the end of Y1 B1 and say so. Do not submit a proposal whose own dependency table states that its gap statements remain candidate claims at the moment of submission.

---

## Medium and low findings

| # | Severity | Category | Where | Problem | Repair |
| --- | --- | --- | --- | --- | --- |
| 1 | medium | methodology | Three-Study Contract, 'Units of analysis' row, all three studies | No unit of analysis has been chosen. Study 1 lists eight different entities; Study 2 lists eleven; Study 3 lists ten. A unit of analysis is the single thing one row of the dataset is. Listing everythi… | State one primary unit per study (Study 1: the flagged deviation; Study 2: the captured judgment record; Study 3: the judgment–target-context pair) with everything else demoted to covariates. State th… |
| 2 | medium | validity | Chapter 1 §1.1 (VEGO-AI evaluation description); absent from Chapter 6… | Every prospective SQ1 and SQ2 result is conditional on one LLM's uncertainty calibration and one corpus, and this dependence is neither listed as a scope limitation in §3.10 nor as a risk in §6.6. SQ1… | Add a model-substitution arm as a construct-validity control — replicate Study 1's routing evaluation on at least one non-GPT model family — or, if that is out of scope, state the dependence explicitl… |
| 3 | medium | internal-contradiction | Proposal v0.3 (current).docx — 'Chapter plan and current status' table… | The proposal's own status table is factually wrong about the package it sits in. It records Chapter 1 as 'Not started — deliberately' and Chapter 6 as 'Not started', while a full Chapter 1 early draft… | Regenerate the status table from the actual package contents before circulating: Chapter 1 'Early draft, out of sequence', Chapter 6 'Complete working draft'. Alternatively remove those two files from… |
| 4 | medium | internal-contradiction | Chapter 1 §1.6 vs Chapter 6 §6.3.1 and §6.4.3 vs Three-Study Contract … | The six medical entry gates are enumerated three different ways in three documents of the same package. Chapter 1 lists 'use case, expert availability, data fit, ethics and institutional approval, app… | Define G1–G6 once, in one place, and have every other document cite the identifiers rather than restate the list. If data fit is a seventh gate, make it G7 and update the count everywhere. |
| 5 | medium | writing-quality | Chapter 3 §3.9 | The single piece of empirical motivation in the entire gap chapter is unquantified. 'Only a small fraction' is doing the work of an observation and is a vague quantifier standing in for two integers t… | Give both counts and the denominator definition: 'of N observable decision points in one full run, M (M/N%) reached the post-hoc review queue', with 'observable decision point' defined. If the counts … |
| 6 | medium | writing-quality | Chapter 3 §3.1 closing, §3.3 closing, §3.6, §3.11 closing | Assertions substituted for argument, in four places where the chapter most needs argument. '§3.1: Everything in this chapter follows from that asserted asymmetry' claims entailment rather than showing… | Delete all four sentences. For §3.3, end the paragraph at the four properties and add the citation the four properties currently lack — they are stipulated by the author with no source. For §3.11, rep… |
| 7 | medium | writing-quality | Chapter 6 §6.1.1, §6.1.4, §6.2.15, §6.4.2, §6.5.2, §6.5.3, §6.6.1 | Roughly a third of Chapter 6 is meta-commentary in which the plan argues for its own honesty and drafting choices rather than stating the plan. A doctoral work plan is judged on whether the work is fe… | Cut §6.1.1's justification to two sentences, delete §6.2.15 entirely (its content is already visible in the exit criteria), delete the closing sentences of §6.4.2 and §6.6.1 ('Plan B is the protected … |
| 8 | medium | redundancy | Across the package: Proposal wrapper (×2), Chapter 3 §3.11, Chapter 1 … | The evidence-boundary statement — 0 of 24 labels, 0 of 6 gates, searches not run, no accuracy claim — is restated nine times across the package in near-identical wording. The machine-transcript caveat… | State the evidence boundary once, in a front-matter 'Evidence status' note, and have every other location cross-reference it in one clause. Same for the transcript caveat — once, in front matter. |
| 9 | medium | citation-integrity | Chapter 3 §3.2.4, §3.7, and the seed-corpus reference list | Four distinct citation-hygiene defects in a chapter whose argument is entirely citation-dependent. (1) Two openness claims rest on title-level reading: §3.2.4 'no framework in this line classifies obs… | Read [6], [7], [18] in full and replace both title-level claims with what the papers actually report — this is a few hours of work standing between the chapter and its two most contested claims. Cite … |
| 10 | medium | gap-argument | Chapter 3, 'Seed-corpus references' preamble | The evidence base for the gap argument is another paper's reference list — specifically, the supervisors' own paper's. That set is by construction the works that paper chose to position itself against… | Declare the selection bias explicitly in the preamble, and break it before defence with one independent search — a single backward/forward snowball from the three closest works ([27], [18], [2]) would… |
| 11 | medium | research-questions | Chapter 3 §3.4 (E6 discrepancy) and §3.6 ('An asymmetry to resolve, no… | The proposal is submitted with the main question's object noun and the subject noun of two sub-questions both formally undecided — 'exploration' vs 'identification/classification', and 'human judgment… | Choose both, mark each choice as the candidate's recommendation with a one-line rationale, and put the alternative in a footnote for the supervisors to overturn. Recommended: 'exploration' (broader, m… |
| 12 | low | internal-contradiction | Three-Study Contract, Study 2 'Intended contribution'; Chapter 3 §3.4 … | 'Auditable' is listed as a property of the Study 2 contribution after Chapter 3 records that it was dropped from the question set per E7. The package therefore carries the removed term in the study co… | Sweep the package for the three retired terms ('auditable', 'transferable', 'end-to-end') and either remove them or reinstate them deliberately. Also reduce this contribution statement from seven adje… |
| 13 | low | writing-quality | Chapter 3 §3.9 closing sentence | A question is not a contribution; an answer is. As written the sentence claims credit for asking, which is the weakest possible reading of a proposal that elsewhere works hard to state contributions a… | 'The contribution is the answer and the design knowledge it yields; the platform is the setting in which they are obtained.' |
| 14 | low | reporting | Chapter 1 §1.3 | Prior results are reported as ranges across settings with no n, no confidence intervals, and no per-setting breakdown, and the weakest and most load-bearing figure is framed emphasis-first. 'Positive … | Report n and the confidence interval, and lead with the magnitude: 'ρ = 0.22 (95% CI …, n = …), i.e. the Inspector's scores explain under 5% of the variance in the human grader's marks despite p = 0.0… |
| 15 | low | terminology | Chapter 3 §3.5, §3.8; Chapter 6 §6.2.3, §6.2.4; Three-Study Contract | Four terms are used as technical objects without definition, and three of them are used interchangeably for what may or may not be the same construct. 'Dosage' of expert review appears six times acros… | Add a short definitions block to Chapter 3 (it already defines two constructs; add these). Define dosage with a unit (reviews per assessment run, or reviewer-minutes per 100 deviations), pick one name… |
| 16 | low | formatting | Chapter 3 §3.4, first bullet | An unclosed emphasis marker changes what the sentence appears to claim. The asterisk opens before 'variability exploration in guideline operationalization scenarios' and the closing asterisk does not … | Close the emphasis after 'scenarios', and split the A08-01 discrepancy note into its own paragraph. A wording flag should not be buried inside the sentence it contradicts. |

---

*Generated from an independent review pass over the v0.4 package on 2026-08-12. Findings are the reviewer's, recorded verbatim; no finding has been softened.*