# Chapter 9 — Discussion

> Draft. Interprets what the artifact demonstrates and what it does not, derives design principles, maps
> findings to research questions, compares with related work, and discusses implications. Sources:
> `papers/mas4models2026/claim-evidence-table.md`, `docs/research/literature-review-taxonomy.md`,
> `artifacts/EVALUATION_STRICT_REVIEW.md`. No accuracy claim.

## 9.1 What the artifact demonstrates

The implemented system shows that reusable human judgment can be made operational in AI-assisted model assessment as a *complete, inspectable path*: AI uncertainty → human review → structured feedback → provenance-tracked judgment memory → advisory retrieval → non-destructive parallel comparison. Each step is schema-validated and reproducible, and the original AI output is preserved verbatim (`ai_classification_changed = 0`, `ai_behavior_changed_in_baseline = false`).

This is a design-science result: an artifact that closes a loop the host architecture only anticipated. The baseline VEGO-AI system produces review signals (`requires_human_review`, `human_review_reason`, confidence scores) and implements skills for incorporating external answers (`resolve_with_answers`), but none of these are connected to an operational human-judgment workflow. The thesis artifact connects them, turning latent affordances into a functioning chain that selectively routes work to a human, captures the response structurally, stores it with provenance, retrieves it as advisory evidence, and evaluates its impact through a parallel comparison.

The mechanism works at the scale of the available data: 179 models, 27 patterns, 11 review items, 3 reusable memories, 8 advice items, and 27 comparison records. The workflow is deterministic and offline — it does not depend on LLM calls, API availability, or network conditions — and it is governed by an evidence-consistency guard that verifies 18 invariants at every prompt.

## 9.2 What it does not yet demonstrate

The artifact does **not** demonstrate that reusable judgment improves classification accuracy. Two facts make this precise.

First, there is no independent benchmark in the data. The author-reviewed labels are byte-identical to the AI output for all 27 patterns, so they record agreement, not ground truth. Any evaluation using them would be circular. The only admissible evaluation requires independently collected expert labels (§6.6), which have not yet been obtained.

Second, the current deterministic policy is conservative by design — it changes zero of 27 classifications. Original and memory-informed predictions are identical, so no labeling can produce a delta under the current policy. A delta is only possible if a future policy refinement (M4B-1.1) is justified by error analysis on development rows and evaluated once on the sealed holdout.

The honest reading is that the present contribution is **mechanism, traceability, and escalation**, and that the accuracy question is *well-posed but not yet answerable*. This is itself a non-trivial result: the project has identified exactly what evidence is missing (independent expert labels), designed a protocol to obtain it (the bias- and leakage-controlled annotation study), built the machinery to process it (the evaluation harness), and defined the conditions under which claims are permitted (the evidence gates). The gap between mechanism readiness and empirical proof is as narrow and well-defined as it can be without the labels themselves.

## 9.3 Addressing the research questions

> **2026-08-10 migration note:** this section previously mapped findings to a five-sub-question draft
> (`SQ1` control/timing, `SQ2` information direction, `SQ3` role of judgment, `SQ4` structure/reuse, `SQ5`
> MDE-assessment gap). It now maps to the exactly-three-subquestion structure adopted in Chapter 3 §3.3.
> No finding below is new; each is carried over from the corresponding prior sub-question per
> `docs/research/phd-proposal/legacy-rq-crosswalk.md` §3.

The research question (U-RQ) asks how human judgment can be captured, governed, and used to support
agentic-AI-driven variability exploration in guideline operationalization scenarios, enabling reliable
human–AI co-reasoning. The three sub-questions map to specific findings.

**SQ1 — Selective intervention.** The literature review (§2.5) identifies three patterns: human-in-the-loop (the human is part of every decision cycle), human-on-the-loop (the human monitors and intervenes by exception), and human–AI co-reasoning (both parties contribute reasoning that remains visible and reusable). The thesis artifact positions itself between on-the-loop and co-reasoning: the Selective Intervention Policy (M1) escalates by exception (on-the-loop), but the human's rationale becomes durable, retrievable evidence (co-reasoning). This combination is not found in the surveyed literature.

**SQ2 — Governed knowledge reuse.** Three findings from the prior literature review converge on this question. *Direction of information:* the surveyed systems predominantly flow information AI→human (the AI explains, and the human consumes the explanation); where human→AI flow exists (in HITL systems), the input is typically a label or correction, not a structured, rationale-bearing judgment. The thesis artifact implements bidirectional flow instead: the AI's evidence and justification inform the human's review (M1), and the human's structured decision (M2) feeds forward through memory (M3) and advisory retrieval (M4A). *Role of judgment:* across the surveyed work, human judgment is treated as a temporary correction for current AI limits — it fixes the immediate case but does not accumulate. The thesis artifact treats human judgment as an essential, reusable asset: the Human Judgment Memory (M3) stores it with provenance, scope, conflict status, and match reasons, making it retrievable for future similar cases even if the underlying LLM improves. *Structure:* no surveyed system provides the combination of schema-validated feedback capture (M2), provenance-tracked memory storage (M3), and explainable embedding-free retrieval (M3/M4A). Individual elements exist — structured feedback in annotation tools, memory in case-based reasoning systems, advisory retrieval in recommendation engines — but the specific combination for model-variability assessment is novel.

**SQ3 — Evaluation and transfer.** The deterministic parallel comparison (M4B-1, §5.6) is the mechanism that makes reuse *measurable* without changing the original result: it is the artifact that Chapters 6–7 evaluate to ask whether memory-informed classifications transfer safely across settings. No surveyed system pairs a provenance-tracked judgment store with a non-destructive, deterministic comparison mechanism built specifically to test transfer without contaminating the baseline. Whether transfer in fact holds — within the current software-engineering domain, and toward a second domain when governance and access permit — is an empirical question answered (or left open) by the evidence gates of Chapter 6, not asserted here.

**Positioning: the MDE-assessment gap** (retained as literature positioning per the crosswalk, not a numbered sub-question). The gap in the model-assessment literature (§2.3) is the single-reference, error-centric stance: deviation is treated as defect (Bian et al., 2019; Ibáñez et al., 2025). VEGO-AI addresses this with the substantial/occasional distinction, and this thesis adds the missing human-judgment lifecycle. The running example (§4.4, §5.6, §7.3) makes this concrete: Agent 4 classifies "Customer as actor" as an error, but a human expert recognizes it as a valid alternative — a judgment that, once stored, can inform future assessments of similar patterns. The combination — variability-aware AI assessment *plus* reusable human judgment — is not found in the surveyed MDE or HITL literature.

## 9.4 Reusable judgment as co-reasoning

The system sits between human-on-the-loop and human–AI co-reasoning, and this positioning deserves clarification because "co-reasoning" is a strong claim.

The system is on-the-loop in that the Selective Intervention Policy escalates by exception rather than reviewing everything. The AI operates autonomously for confident, unambiguous cases, and the human is engaged only where the AI's own signals indicate uncertainty or a need for review. This is a standard on-the-loop pattern.

What moves the system toward co-reasoning is the **persistence and reuse** of the human's contribution. In a purely on-the-loop system, the human's intervention resolves the current case and is consumed — the system returns to autonomous operation with no memory of the human's reasoning. In this thesis's system, the human's rationale becomes durable, retrievable evidence that is surfaced when similar cases arise later. The human and the AI are not reasoning about the same case simultaneously (as in a real-time collaborative interface), but the human's past reasoning persists alongside the AI's current reasoning, and both are visible, attributable, and auditable.

The distinctive feature is that the co-reasoning happens *across time*: a judgment made about "Customer as an actor" in the Cheers UCD setting persists and can inform the assessment of a similar pattern in ParkWise or in a class diagram — not as an automatic override, but as advisory evidence that a human or controlled experiment can evaluate. This temporal extension of the reasoning loop is what differentiates the artifact from a standard on-the-loop correction.

## 9.5 Design principles

The artifact instantiates a set of transferable design principles that could inform similar human–AI collaboration systems in other domains:

**DP1 — Bidirectional explainability.** The AI explains its reasoning to the human (evidence, justification, confidence), and the human can explain back (structured rationale, decision, scope). Both explanations are preserved and auditable. This principle responds to the one-way explanation gap identified in §2.8.

**DP2 — Structured, not free-text, feedback.** Human judgments are captured in a schema-validated format with required fields (decision, rationale, reviewer, timestamp). This makes them machine-actionable and comparable, unlike informal comments or email exchanges. The structure is what enables promotion to reusable memory.

**DP3 — Reusable human judgment.** Every approved human decision becomes durable, recallable knowledge with provenance (who decided, when, on what case, with what rationale). The judgment is indexed by domain, diagram type, guideline, and keyword, and can be retrieved for future similar cases. This is the central design principle of the thesis.

**DP4 — Selective intervention.** The system asks the human where explicit AI
uncertainty and governance signals satisfy the routing policy. This makes the
intervention criteria inspectable and configurable. Whether the policy
concentrates expert-confirmed errors or saves time is not assumed from queue
counts; EXP-022 and EXP-026 are designed to test those effects.

**DP5 — Human authority over the rubric.** Guideline changes require human approval. The AI may flag a pattern for guideline update (`flag_for_guidelines_update = true`), but it cannot unilaterally rewrite the assessment criteria. This preserves the human's role as the authority on evaluation standards.

**DP6 — Preserve separation of concerns.** The extension keeps language, domain, and pedagogical judgments distinct, mirroring the four-agent architecture of the baseline. Memory entries are scoped by domain and diagram type, and retrieval respects these scopes.

**DP7 — Model-independent judgment assets.** The human-judgment record is
separable from a particular base-model response and therefore can be reevaluated
when the model changes. This design creates the *possibility* of longitudinal
value; whether the asset remains useful as base models improve requires a future
multi-version study.

## 9.6 Comparison with related work

The design principles relate to and extend prior work in several ways.

Amershi et al.'s (2019) *Guidelines for Human–AI Interaction* emphasize making the AI's uncertainty visible, supporting efficient correction, and learning from human input. The thesis artifact implements these principles (visible confidence in M1, efficient review in M2) and extends them with reuse (M3) and non-destructive comparison (M4B-1), which the guidelines recommend but do not operationalize.

The NIST AI Risk Management Framework (2023) frames human oversight as a governance requirement, emphasizing accountability and meaningful human control. The thesis artifact provides a concrete realization of these principles: every human judgment is traceable, every AI decision is preserved, and the comparison artifact makes the effect of human input measurable without hiding or overwriting the AI's original output.

Silva et al.'s (2025) work on human-in-the-loop LLM-enabled domain modeling is the most directly relevant precedent. The thesis extends their HITL pattern by adding reuse: where their system captures human input for the current modeling session, this thesis's system stores it as persistent, retrievable knowledge for future sessions and settings.

Mosqueira-Rey et al.'s (2023) HITL survey identifies patterns such as active learning and interactive labeling. The thesis artifact is distinct in that the human's input is not consumed by a training loop (as in active learning) but stored as a separable, inspectable knowledge item that retains its identity and provenance.

## 9.7 Implications

**For practice.** The artifact offers educators and assessment practitioners a
traceable way to route selected cases and accumulate an institutional judgment
record rather than leaving decisions in informal channels. It may support future
reuse across semesters, but the current evidence does not show that the routing
selects the most important errors, reduces teaching-assistant workload, or
improves consistency. Those are empirical questions, not assumed benefits.

**For evaluation methodology.** The no-benchmark finding — that author-reviewed labels duplicate the AI output byte-for-byte — is a caution for any study that uses researcher-agreed labels as ground truth. Agreement-with-AI artifacts are easy to mistake for independent benchmarks, and leakage-aware evaluation designs (per-row leakage tags, blind labeling, sealed holdouts) should be standard practice in human–AI assessment studies.

**For the HITL research community.** The work argues that the valuable target in AI-assisted assessment is not more automation but **reusable, accountable human judgment**. The design principles (§9.5) provide a transferable framework for systems that want to move human input from transient correction to durable knowledge.

**For the MDE community.** The artifact demonstrates that model-variability assessment can be framed as a human–AI co-reasoning activity, not just a classification task. This reframes the assessment problem from "compare against a reference" to "build a shared understanding of what counts as valid," with the judgment memory serving as the institutional record of that understanding.

## 9.8 Contribution as a nascent design theory

The design principles of §9.5 are not only a practitioner checklist; abstracted over the constructs introduced in §9.1–9.4, they constitute a **nascent design theory** of governed human-judgment reuse (Gregor & Hevner, 2013, Level 2), developed in full in the design-theory chapter. Two moves lift the principles to a theory. First, they are organized as *principles of form and function* — each commitment (e.g., non-destruction, selective intervention, governed reuse) is paired with the function it serves and the kernel knowledge that justifies it. Second, and decisively for a doctoral contribution, the theory yields **testable propositions**, each stated with its admissible test and current status, and none asserted as confirmed:

- **P1 (targeting)** — selective intervention concentrates expert effort on the patterns most likely to be errors; *queue rate measured (40.7%); error-coverage pending labels.*
- **P2 (escalation without contamination)** — governed comparison flags ambiguous cases for review while preserving correct baseline outputs verbatim; *non-destruction demonstrated (0/27 changed); escalation precision pending labels.*
- **P3 (non-circular reuse)** — provenance plus per-row leakage tagging yields reuse evidence that is not self-referential; *retrieval mechanism demonstrated; generalization-safe rows currently 0.*
- **P4 (justified adoption)** — a deterministic policy refinement raises agreement with experts only when justified by held-out error analysis, and without increasing changed-and-wrong; *conditional and gated.*
- **P5 (reviewer-grounded validity)** — inter-rater reliability bounds the trust placed in any effect estimate; *protocol ready; pending labels.*
- **P6 (transferability)** — the principles and the evaluation methodology transfer across domains, diagram types, reviewers, and model versions; *PhD-scale, seeded by the five cross-setting comparison rows.*

This propositional framing is what separates the contribution from a single situated artifact: it renders the design knowledge falsifiable and transferable beyond VEGO-AI, positioning the work as a Level-2 design-theory contribution. The form-and-function principles (DP1–DP7) are demonstrated now; the effect propositions (P1–P4) await the gated evaluation — precisely the boundary the next section makes explicit.

## 9.9 Conditional interpretation of empirical outcomes

The evaluation is not structured around obtaining a positive result. Four
outcome families lead to different conclusions:

| Outcome | Evidence pattern | Interpretation | Action |
| --- | --- | --- | --- |
| Mechanism only | B1 passes; no independent labels | Reusable judgment is implemented and governed; performance is unknown | Complete EXP-019/020 |
| Baseline errors but no safe candidate | B2 finds errors; EXP-022 finds no reliable correction rule | Human review may remain valuable, but automatic parallel correction is not justified | Strengthen escalation, not classification |
| Positive holdout pilot | B4 net correction is positive on 8 rows | Promising pilot only; uncertainty remains high | Seek EXP-025, keep policy frozen |
| Null or harmful holdout | Net correction is zero/negative or changed-and-wrong appears | Candidate is unsupported or unsafe for the tested rows | Reject/defer candidate; preserve baseline |
| Positive external gate | N≥30 and every preregistered criterion passes | Scoped formal improvement may be reported for the sampled education context | Publish with validity limits |
| Mixed external outcome | Aggregate improvement but macro-F1/subgroup/safety gate fails | No formal improvement claim | Report trade-offs and stop deployment |

This matrix prevents a favorable point estimate from overriding reviewer
reliability, paired harm, class balance, subgroup safety, or provenance.

## 9.10 Limitations

The evidence base is small (27 patterns, at most 24 generalization-safe, currently 0 labeled), the scope is narrow (two domains, two diagram types, one institution, one LLM), and the policy is deliberately conservative (zero classification changes). These limitations bound every claim and are analyzed in detail in Chapter 8. The central remaining question — whether reusable human judgment actually improves classification accuracy — is well-posed, methodologically prepared for, but not yet answerable. The thesis contributions (mechanism, design, methodology) stand independently of the eventual accuracy result, but the empirical contribution awaits the labels.
