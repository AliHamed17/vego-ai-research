# Chapter 3 — Problem Definition and Research Questions

> Draft. Sources: `docs/research/research-plan.md`, `docs/research/methodology.md`. Frames the study as
> design science and fixes the research question and sub-questions.
>
> **2026-08-10 migration note:** the research question and sub-questions below were updated to the
> umbrella-RQ + exactly-three-subquestions structure (`SQ1` selective intervention, `SQ2` governed
> knowledge reuse, `SQ3` evaluation and transfer) required by the 2026-07-29 supervisor meeting and
> refined live in the 2026-08-05 supervisor working call. **This wording is provisional — pending formal
> `D-RQ-01`/`D-RQ-02` sign-off** in [`docs/research/phd-proposal/2026-08-05-rq-decision-pack.md`](../../docs/research/phd-proposal/2026-08-05-rq-decision-pack.md);
> see [`docs/research/meetings/2026-08-05-supervisor-meeting.md`](../../docs/research/meetings/2026-08-05-supervisor-meeting.md)
> for the machine-derived evidence and [`docs/research/phd-proposal/legacy-rq-crosswalk.md`](../../docs/research/phd-proposal/legacy-rq-crosswalk.md)
> for how the previous five thesis sub-questions (retained below in §3.3) map onto the new three.

## 3.1 Problem statement

AI-assisted assessment of domain models must do more than detect deviations from a reference; it must **interpret** them — deciding whether a recurring deviation is a valid alternative, an error, a domain-specific choice, a language-level issue, a guideline-update candidate, or an ambiguity requiring adjudication. These are judgments that depend on context, domain knowledge, and pedagogy. They cannot be reduced to a mechanical diff, and reasonable experts may disagree about them.

VEGO-AI automates this interpretation with a four-agent LLM pipeline that distinguishes substantial variability (valid alternatives) from occasional variability (errors). The pipeline produces confidence scores, review flags, and justification fields that anticipate human involvement — yet it provides no operational way to *incorporate* human judgment where it is most needed, and no way to *reuse* a judgment once made. An expert who reviews a flagged case and decides that a particular deviation is a valid alternative must communicate that decision outside the system; the next time a similar deviation appears, the expert must make the same judgment again from scratch.

The problem this thesis addresses is therefore: **how to capture human judgment about model variability as structured, reusable knowledge, and feed it back into AI-assisted assessment without replacing or corrupting the original AI pipeline.**

This problem has three dimensions. First, it is a *design* problem: what mechanisms are needed to selectively trigger human review, capture structured feedback, store reusable judgments, and retrieve them for future cases? Second, it is an *integration* problem: how can these mechanisms be added to an existing, functioning pipeline without changing its behavior or corrupting its baseline outputs? Third, it is an *evaluation* problem: how can the effect of reusable human judgment be measured honestly, given the specific evidence constraints (no independent benchmark, same-pattern leakage, small sample) that characterize this case?

## 3.2 Research question

> **U-RQ.** How can human judgment be captured, governed, and used to support agentic-AI-driven
> variability exploration in guideline operationalization scenarios, enabling reliable human–AI
> co-reasoning?

**Status: provisional working wording**, refined live from the 2026-07-29 working baseline during the
2026-08-05 supervisor call (Iris and Arnon). It replaces "reusable ... and reused" with "used" (the reuse
concept moves to SQ2 below), drops the "auditable" / "transferable" qualifiers from the headline, and
names *variability exploration* and *guideline operationalization* explicitly — addressing Arnon's
critique that the prior wording blurred the proposed Agentic-AI solution with the actual research
question. It is machine-transcribed and **not yet supervisor-confirmed** (`D-RQ-01`); the exact final
text must be checked against Ali's own saved working draft from the call before it is treated as final.

This is a design-science-compatible umbrella question: it asks how a mechanism (human judgment capture
and governance) can support a target activity (variability exploration in guideline operationalization)
reliably. VEGO-AI is the motivating case and the artifact, not the sole object of the underlying literature
review, which continues to inform the design (Chapter 2).

## 3.3 Sub-questions

The research question decomposes into **exactly three** sub-questions, each mapped to one primary study
(see `docs/research/phd-proposal/three-study-contract.md`) and to specific thesis chapters and milestones.
Wording below is provisional in the same sense as §3.2 (`D-RQ-02`, pending sign-off).

**SQ1 — Selective intervention.** When and how, in variability exploration scenarios, should an agentic
assessment system request human judgment so that important uncertainties are addressed without
unnecessary expert burden? This question motivates the Selective Intervention Policy (M1) and its
decision to escalate by exception rather than reviewing every case. It is addressed in Chapter 2 (§2.5)
and Chapter 5 (§5.2).

**SQ2 — Governed knowledge reuse.** How should expert judgment — including the system's core reasoning —
be represented, validated, reconciled, and stored so it can be reused transparently without unsafe
generalization or loss of human authority? This question underpins the bidirectional, structured design
of the artifact (M2–M4A): the AI's evidence is preserved and the expert's rationale is captured, validated,
stored with provenance, and resurfaced as advisory evidence. It is the central question of the thesis and
is addressed in Chapter 2 (§2.6, §2.8) and Chapter 5 (§5.3–§5.5).

**SQ3 — Evaluation and transfer.** How can expert judgment be reused and transferred across different
guideline-operationalization contexts without unsafe generalization or loss of human authority, first in
software/modeling and, when governance and access permit, in healthcare? This question governs the
non-destructive parallel comparison (M4B-1) and the evaluation methodology (Chapter 6): transfer is tested
first within the current software-engineering domain, consistent with the domain-neutral framing in §3.6.
It is addressed in Chapter 5 (§5.6) and evaluated in Chapter 6.

**On the retired SQ4/SQ5 (previous draft).** The prior five-sub-question draft's SQ4 (structure and reuse)
is absorbed into SQ2 (representation/storage) and SQ3 (the effect of reuse), and its SQ5 (the MDE-assessment
gap) is retained as literature positioning rather than a numbered sub-question — it motivates *why* this
problem is open (§3.1, Chapter 2) but is not itself a study. See
`docs/research/phd-proposal/legacy-rq-crosswalk.md` §3 for the full item-by-item disposition; nothing from
the prior draft is silently dropped.

## 3.4 Evaluation research questions and hypotheses

The main RQ and SQ1–SQ3 govern the literature synthesis and artifact design. A
separate set of empirical questions governs the accuracy-evidence phase. Keeping
these sets distinct prevents the absence of performance labels from obscuring
what the design-science work has already established.

> **E-RQ1 — Baseline errors.** Where, and in which error categories, does the
> frozen Agent 4 baseline disagree with independent expert judgment?

> **E-RQ2 — Targeting and retrieval.** Do selective review and memory retrieval
> focus attention on expert-identified baseline problems with relevant,
> scope-correct, traceable evidence?

> **E-RQ3 — Unseen paired effect.** Does a frozen deterministic parallel policy
> produce positive net correction on unseen, leakage-safe data while preserving
> baseline safety?

These questions are operationalized by four hypotheses. Their status is part of
the research result, not an implementation target that must be made positive.

| ID | Hypothesis | Current status | Decisive evidence |
| --- | --- | --- | --- |
| H1 | Selective review contains a meaningful share of expert-confirmed baseline errors. | Unproven | EXP-021 and EXP-022 |
| H2 | Human Judgment Memory retrieves relevant, scope-correct prior judgments. | Unproven | EXP-022 |
| H3 | A frozen deterministic parallel policy yields positive net correction on unseen data. | Unproven and blocked | EXP-024 pilot, then EXP-025 external replication |
| H4 | Reusable memory reduces repeated review effort without reducing escalation quality. | Unproven and not approved | EXP-026 controlled human-effort study |

The primary empirical estimand for H3 is **net correction**:
`changed-and-correct - changed-and-wrong`. This paired measure makes benefit and
harm visible. Accuracy and macro-F1 are secondary measures. A positive H3 claim
requires a separate external education-domain set with at least 30 adjudicated
generalization-safe rows and all preregistered statistical and safety criteria
to pass; the current 24-row set cannot supply that formal claim.

## 3.5 Design-science framing

The study follows a design-science research methodology (Hevner et al., 2004; Peffers et al., 2007; Gregor & Hevner, 2013). The cycle proceeds through five phases:

**Problem identification.** AI-assisted model assessment needs expert judgment, but one-off review does not scale or accumulate knowledge. The problem is real, recurring, and documented in VEGO-AI's own architecture (the latent human hooks of §4.4).

**Objectives.** Design a reusable human-judgment layer that selectively triggers review, captures structured feedback, stores judgments with provenance, retrieves them as advisory evidence, and enables controlled comparison — all without modifying the host pipeline's behavior.

**Design and development.** The artifact comprises five layers (M1–M4B-1) implemented as pure-Python modules with schema-validated data structures, deterministic matching, and non-destructive parallel comparison (Chapter 5).

**Demonstration.** The artifact is demonstrated on the VEGO-AI pipeline across four settings (two domains, two diagram types), processing 179 student models aggregated into 27 variability patterns (Chapter 7).

**Evaluation.** A bias- and leakage-controlled annotation protocol defines how to obtain independent expert labels and measure the artifact's empirical effect honestly (Chapter 6). The evaluation methodology is itself a contribution.

The artifact's novelty is not "a human step" but **turning human judgment into a reusable knowledge asset** for variability assessment. Contribution types are kept distinct: a literature-review contribution (taxonomy and gap), a design contribution (the co-reasoning architecture, feedback schema, and judgment-memory concept), a technical prototype (the implemented and tested M1–M4B-1 pipeline), and a planned empirical contribution (the leakage-aware evaluation).

## 3.6 Scope and boundaries

**In scope:** selective human review triggered by AI uncertainty signals; structured, schema-validated feedback capture with signature verification; reusable judgment memory with provenance tracking, conflict detection, and explainable retrieval; advisory evidence retrieval that preserves original AI output; and a deterministic, non-destructive comparison between original and memory-informed classifications.

**Out of scope** (and explicitly blocked for this thesis): LLM-based reclassification (M4B-2); any change to Agent 1–4 prompts, logic, or API behavior; automatic guideline rewriting without human approval; embedding-based retrieval; any overwrite of the baseline evaluation outputs. These boundaries are not limitations of the design but deliberate choices that keep the artifact cleanly evaluable against the preserved baseline.

**Data scope:** the evaluation is bounded by the available data — four settings, two domains (Cheers, ParkWise), two diagram types (UCD, CD), 179 student models, 27 recurring variability patterns — and by the evidence gates of Chapter 6, which require at least 20 generalization-safe expert labels before any quantitative accuracy claim is permitted.

The following table maps the research questions to the thesis structure:

| Question | Addressed in | Artifact layer | Evaluated in |
| --- | --- | --- | --- |
| SQ1 Selective intervention | Ch 2 §2.5, Ch 5 §5.2 | M1 Selective Review | Ch 7 §7.3 |
| SQ2 Governed knowledge reuse | Ch 2 §2.6/§2.8, Ch 5 §5.3–5.5 | M2–M4A | Ch 7 §7.3–7.4 |
| SQ3 Evaluation and transfer | Ch 5 §5.6 | M4B-1 | Ch 6, Ch 7 |
| MDE-assessment gap (positioning, not a numbered SQ) | Ch 2 §2.3/§2.4/§2.8 | — (positioning) | Ch 9 §9.1 |
| E-RQ1 Baseline errors | Ch 6 §6.10 | B0/B2 | EXP-020/021 |
| E-RQ2 Targeting & retrieval | Ch 6 §6.10 | M1/M3/M4A | EXP-022 |
| E-RQ3 Unseen paired effect | Ch 6 §6.10 | B3–B5 | EXP-023–025 |

*Crosswalk from the prior five-sub-question draft is in `docs/research/phd-proposal/legacy-rq-crosswalk.md` §3.*
