# Chapter 10 — Conclusion and PhD Continuation

> Draft. Summarizes contributions and honest status, revisits research questions, and sets out continuation
> work. Sources: `docs/research/research-plan.md`, `docs/research/m4b1-policy-refinement-plan.md`, the
> evaluation plan.

## 10.1 Summary of contributions

This thesis extended VEGO-AI from an automated agentic model-assessment pipeline into a staged human–AI co-reasoning system. The work makes four distinct contributions:

**A literature-grounded framing** of reusable human judgment for AI-assisted model-variability assessment. The literature review (Chapter 2) identified four interrelated gaps in the surveyed work: one-way explanation, transient judgment, emphasis on generation over assessment, and unused human-review signals. The contribution is the synthesis of these gaps into a coherent problem statement and the positioning of the thesis artifact against the state of the art.

**A design comprising selective review, structured feedback, and provenance-tracked judgment memory.** The co-reasoning artifact (Chapter 5) introduces seven transferable design principles — bidirectional explainability, structured feedback, reusable human judgment, selective intervention, human authority over the rubric, separation of concerns, and future-proofing — that can inform similar human–AI collaboration systems in other domains.

**A working, non-destructive technical prototype (M1–M4B-1)** with dashboard
and visualizer inspection surfaces and deterministic verification. The accepted
verification record reports both the VEGO-AI and research-script suites passing;
exact counts remain attached to that dated record. The prototype demonstrates the mechanism at a
concrete scale (179 models, 27 patterns, 11 review items, 3 reusable memories)
and preserves the original baseline throughout.

**A bias- and leakage-controlled evaluation methodology** that makes the artifact's empirical effect measurable. The methodology (Chapter 6) identifies the byte-identical baseline labels as unusable ground truth, defines a blind annotation protocol with anonymization, randomization, and two-reviewer adjudication, establishes a sealed development/holdout split for policy refinement, and pre-commits to explicit evidence gates. The methodology itself is a contribution: it provides a template for evaluating human–AI collaboration artifacts where conventional benchmarks are unavailable or unreliable.

## 10.2 Revisiting the research questions

> **2026-08-10 migration note:** restated against the exactly-three-subquestion structure of Chapter 3
> §3.3; see `docs/research/phd-proposal/legacy-rq-crosswalk.md` §3 for how the prior five-sub-question
> draft maps onto SQ1–SQ3. This wording remains provisional pending `D-RQ-01`/`D-RQ-02` supervisor sign-off.

**U-RQ.** The research question asked how human judgment can be captured, governed, and used to support agentic-AI-driven variability exploration in guideline operationalization scenarios, enabling reliable human–AI co-reasoning. The thesis answered this by surveying six areas of related work, identifying the gaps summarized below, and demonstrating a concrete artifact that closes them.

**SQ1 (Selective intervention):** the artifact positions itself between on-the-loop and co-reasoning, escalating by exception while making the human's rationale durable and retrievable.

**SQ2 (Governed knowledge reuse):** information flows bidirectionally — the AI's evidence informs the human's review, and the human's structured decision feeds forward through memory and advisory retrieval. Human judgment is treated as a reusable asset, not a transient correction: the judgment memory stores it with provenance and retrieves it for similar future cases. The running example (§4.4–§7.3) illustrates this concretely: a single expert judgment about "Customer as actor" is captured, stored, retrieved as advisory evidence, and used in a controlled comparison — demonstrating the full lifecycle. The combination of schema-validated feedback, provenance-tracked memory, and explainable retrieval is novel in the model-assessment context.

**SQ3 (Evaluation and transfer):** the deterministic parallel comparison mechanism (M4B-1) makes reuse measurable without changing the original result, which is what a transfer claim requires; whether reuse in fact transfers safely across settings and — when governance and access permit — across domains is the open empirical question carried into Chapter 6's evidence gates, not a result claimed here.

**Positioning (was SQ5, the MDE-assessment gap):** the thesis contributes the missing human-judgment lifecycle for variability interpretation, extending VEGO-AI's substantial/occasional distinction with reusable expert knowledge. Retained as literature positioning rather than a numbered sub-question, per the crosswalk.

## 10.3 Honest status

The mechanism build is complete through M4B-1. The artifact is implemented,
historically merged and tagged, and governed by evidence-consistency and
protected-path checks. The evaluation methodology is designed, the annotation
package is prepared with blind sheets and leakage controls, and the
EXP-019–EXP-027 evidence sequence is preregistered.

The empirical phase is not complete: there are zero generalization-safe expert labels, and the current deterministic policy changes zero classifications. The supportable claim at this stage is that the system enables structured, reusable human judgment with traceability, provenance, and safer escalation — not that it improves accuracy. This is an acceptable intermediate state for a design-science thesis because the artifact and methodology contributions stand on their own merits (Hevner et al., 2004; Peffers et al., 2007; Gregor & Hevner, 2013), and the remaining work is clearly defined and human-gated.

## 10.4 Immediate next work (unblocks the empirical claim)

The empirical phase advances through the following gates. The first three are
human-gated; later policy work is conditional rather than assumed:

1. **Calibrate reviewers without consuming the evaluation set.** Two reviewers
   complete EXP-019 on the three excluded same-pattern rows and freeze the
   instruction version.

2. **Execute independent annotation.** Two modeling experts label the 24 safe
   rows blind. Cohen's κ is computed before a third role adjudicates
   disagreements into a frozen gold-label set.

3. **Characterize the frozen baseline.** Open only the 16 development rows for
   EXP-021/022, identifying baseline errors and auditing review/retrieval
   validity while eight holdout rows remain sealed.

4. **Conditional policy decision.** Proceed to EXP-023 only if at least three
   potentially correctable development errors span at least two settings and a
   specific deterministic policy record is approved.

5. **Evaluate once, then replicate externally.** Open the eight-row holdout once.
   Treat it as a pilot. A formal improvement claim requires a separate new
   education-domain batch with at least 30 and preferably 48 adjudicated safe
   rows and every preregistered statistical and safety gate.

The evidence ladder is therefore B0 frozen baseline → B1 implemented mechanism
→ B2 independent labels → B3 approved frozen candidate → B4 sealed pilot → B5
external replication. Progress along the ladder is progress in evidence quality,
not guaranteed progress in accuracy.

## 10.5 PhD continuation directions

The MSc thesis establishes the mechanism and methodology; several directions extend the work toward a fuller understanding of reusable human judgment in AI-assisted assessment.

**M4B-2 — LLM-assisted reclassification.** A possible future research question,
not an approved implementation. Any later study would require a separate plan,
authorization, stochastic-evaluation protocol, and the same non-destructive
comparison boundary.

**M5 — Human-approved guideline refinement.** Studying the loop where substantial-variability judgments inform updates to the assessment rubric, under human authority. This extends the co-reasoning from classification to the assessment framework itself, addressing DP5 (human authority over the rubric) in a more ambitious form.

**Cross-context transfer.** Evaluating whether judgments transfer across settings (Cheers→ParkWise), diagram types (UCD→CD), and domains, using leave-one-pattern-out, cross-setting, and cross-domain experimental designs with larger expert panels and inter-rater reliability analysis.

**Longitudinal value.** Testing DP7 (future-proofing) directly by re-running the pipeline with newer LLMs and measuring whether the judgment memory's contribution persists, increases, or diminishes as the base model improves.

**Mixed-initiative interaction.** Extending the read-only inspection surfaces (dashboard, visualizer) into a genuine co-reasoning interface with feedback capture, real-time advisory display, and iterative refinement, while preserving the auditability and non-destruction guarantees established in this thesis.

## 10.6 Closing statement

This thesis moved VEGO-AI from "automated variability assessment" to "variability assessment with reusable human judgment." The artifact demonstrates that expert reasoning about model variability can be captured structurally, stored with provenance, retrieved as advisory evidence, and evaluated non-destructively against the original AI pipeline. Its lasting idea is methodological as much as technical: human judgment should be captured as structured, reusable, accountable knowledge — and its effect should be claimed only on the strength of leakage-aware, independently labeled evidence.

The safe claim now is feasibility and governance of the reusable-human-judgment
mechanism. A conditional pilot claim may be made after adjudicated labels and a
sealed evaluation. A formal improvement claim is allowed only after the external
EXP-025 gate passes. Accuracy improvement, generalization, reduced human effort,
benchmark superiority, and clinical performance are not established by the
current evidence.
