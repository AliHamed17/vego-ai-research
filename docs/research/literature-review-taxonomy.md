# Literature Review Taxonomy

This taxonomy organizes the related work around the thesis spine: reusable human judgment in AI-assisted domain modeling and model assessment.

> **Note (2026-08-19):** the M1-M4 / H1-H3 / S1-S7 framing below predates the 2026-08-05
> supervisor call's pivot to the current U-RQ / SQ1-SQ2-SQ3 wording — see
> `docs/research/phd-proposal/three-study-contract.md` for the current questions. This
> document's *thematic* taxonomy (below) is for structuring the written Chapter 2
> narrative; it is complementary to, not a substitute for, the *lifecycle-stage* taxonomy
> (`TRIGGER -> ASK -> RECORD -> REUSE -> PROVE`) used for evidence/gap classification over
> the 140-source verified corpus at `literature/README.md#taxonomy`. Use both together:
> this one for how the chapter reads, that one for what each source actually establishes.

## Review Lens

The literature review should explain how prior work supports or fails to support this VEGO-AI design move:

> Human judgment is selectively triggered, structurally captured, and stored as reusable knowledge for future variability interpretation.

## Taxonomy

| Area | What To Look For | Relevance To VEGO-AI | Evidence To Extract |
| --- | --- | --- | --- |
| Human-in-the-loop AI | Systems where humans correct, label, approve, or supervise AI outputs. | Frames M1-M2 as selective review and structured feedback. | Trigger policy, review workload, feedback schema, governance model. |
| Human-on-the-loop AI | Systems where humans monitor or intervene in otherwise automated decisions. | Helps position selective intervention instead of reviewing every case. | Intervention criteria, oversight boundaries, audit requirements. |
| Explainable AI | Explanations, rationales, provenance, and inspectable decision paths. | Supports transparent memory retrieval and match reasons in M3. | Explanation form, trust claims, limitations of explanation-only support. |
| Expert feedback and knowledge capture | Methods for converting expert correction into reusable rules, cases, or guidelines. | Directly motivates Human Judgment Memory. | Knowledge representation, reuse policy, conflict handling, lifecycle. |
| AI-assisted domain modeling | LLM or AI support for models, diagrams, requirements, guidelines, or conformance. | Provides the domain-specific context for VEGO-AI. | Model type, task, evaluation data, expert comparison. |
| Model assessment and variability interpretation | Techniques for comparing domain models and distinguishing valid variation from errors. | Grounds the meaning of "variability" and "assessment." | Classification scheme, metrics, examples, expert labels. |
| Human-AI co-reasoning | Shared reasoning loops where human and AI contributions remain visible. | Names the combined H1-H3 framework architecture (M4 advisory/comparison is now parked evaluation, not framework). | Turn structure, memory, accountability, human authority. |
| Design science research | Artifact construction and evaluation as research method. | Frames VEGO-AI as artifact plus evaluation path. | Problem, objectives, artifact, demonstration, evaluation, contribution. |

## July 2026 Supervisor Redirect Additions

Added 2026-07-04 per the 2026-07-01 supervisor meeting (`docs/research/meetings/2026-07-01-supervisor-meeting-iris.md`; active plan: `docs/research/extension-plan-2026-07-supervisor-redirect.md`). This section is also the scope definition for the literature survey in Pnina's research-methodology course (presentation mid-August 2026; submission around end of September/October 2026). Note on naming: the M1/M2/M3 framing used elsewhere in this file maps to H1/H2/H3 (human review detection / feedback capture / judgment memory and learning) per the redirect; M4 material is parked evaluation-track context.

| Area | What To Look For | Relevance To VEGO-AI | Evidence To Extract |
| --- | --- | --- | --- |
| Agentic human-in-the-loop architectures | HITL designs specifically for LLM-agent and multi-agent pipelines: listener/monitor patterns, interrupt and approval mechanisms, where the human plugs into agent communication. | Directly frames the H-layer listener over VEGO-AI's artifact and Q&A circles (S1-S3). | Integration points, event/trigger models, monitoring granularity, blocking vs. non-blocking designs. |
| Human-AI collaboration in multi-agent systems | Coordination between human participants and multiple cooperating agents; who sees what; authority handoffs. | Positions the H-layer among Agents 1-4 rather than atop a single model. | Role definitions, communication topology, authority and escalation rules. |
| RLHF, reinforcement learning, and LLM feedback learning | How human feedback improves systems at training time (RLHF, reward models, preference learning) vs. inference-time alternatives when the base model is NOT retrained. Distinguish carefully: VEGO-AI does not fine-tune; it learns via memory, context, and guideline refinement. | Contrast class for S7 learning; answers Arnon's "how does RL transfer to the LLM world" question. | What is actually updated, feedback-loop mechanics, applicability without weight access. |
| Agent memory and learning from feedback | Agent memory systems that go beyond save/retrieve: reflection, consolidation, self-correction, knowledge-base refinement from accumulated feedback. | Grounds the "reason and learn, not just save-and-retrieve" directive (S6/S7). | Memory representation, consolidation policy, how memory changes future behavior, evaluation of the learning effect. |
| Anti-sycophancy and source-grounded challenge | Evidence that models comply with user assertions even when wrong; mitigation via source-grounded verification, disagreement strategies, question-raising dialogue. | Grounds S5 H-Verify (colleague-level questioning with convergence). | Sycophancy measurements, mitigation methods, dialogue convergence, escalation designs. |
| Intervention policies and human workload/dosage | Adjustable oversight regimes: per-decision approval, confidence-threshold routing, first-N calibration (active-learning-flavored); cost of expert time. | Grounds the S2 dosage configuration and Iris's workload concern. | Policy types, quality gained per expert-hour, threshold selection. |
| Evaluation of human-AI systems | Study designs combining correctness measures with usability instruments; with/without-human comparisons. | Informs the PARKED evaluation track (Version 0 vs. Version 1 + usability questionnaire); design input only, no near-term claims. | Comparison designs, usability instruments, validity threats. |

### MediVARIA Branches (PhD track, added 2026-07-04)

Supporting the medical-domain transfer plan (`docs/research/medivaria/medivaria-study-plan.md`); survey these at lower priority than the framework branches above, primarily for the thesis discussion/future-work chapters and the PhD proposal:

| Area | What To Look For | Relevance | Evidence To Extract |
| --- | --- | --- | --- |
| CDSS alert fatigue and override behavior | Override rates, causes (context-blind alerts), and mitigation designs. | Motivates S2 dosage as the alert-fatigue answer (MV-RQ3); starting points cited in the MediVARIA one-pager (Felisberto 2024; Nanji 2021 - to be independently verified). | Override rates by setting, causes, what reduced them. |
| Conformance checking in healthcare | Measuring adherence to clinical guidelines from event/EHR data. | Positions MediVARIA against whether-not-why systems (Oliart 2022 as cited in the one-pager - to be verified). | Methods, data requirements, what they cannot interpret. |
| Clinical guideline modeling and conditional language | Computer-interpretable guidelines; handling "as tolerated" / "in the absence of contraindications". | Grounds MV-RQ6 transfer costs (guideline-language semantics = Agent 1's clinical role). | Representation formalisms, known failure modes. |

Citation policy for this section: no fabricated citations. Concrete sources are still **to be sourced** during the course survey; candidate starting points live in `literature/hitl-resource-pack/` (tracked metadata only) and in the MediVARIA one-pager's reference list (archived, ignored).

## Search And Reading Rules

- Prioritize recent peer-reviewed work on human-AI collaboration, AI-assisted modeling, model assessment, and design science.
- Capture both mechanism and evaluation: what the system does, and how the authors know it helps.
- Record when a paper only handles one-time feedback, because that contrast supports the reusable-judgment gap.
- Avoid overstating future-AI claims; connect reuse claims to concrete VEGO-AI mechanisms. M4A advisory evidence and planned C4B evidence (defined in `docs/research/evaluation-plan.md`) are parked evaluation-track material per the July 2026 redirect - cite them as future evaluation, never as near-term evidence.

## Curated Resource Pack

The repo-local resource pack at `literature/hitl-resource-pack/` contains a source manifest, BibTeX entries, and a tool-fit matrix for HITL and Human-AI collaboration resources.

Use it to support Chapter 2 and methodology writing, especially:

- Human-AI interaction design guidelines for review and visualization behavior.
- AI risk/governance sources for claim boundaries and human oversight.
- Active learning and HITL-ML sources for future EXP-005 sampling and M4B policy discussion (parked evaluation-track context per the July 2026 redirect).
- Tool references for possible future Label Studio or Argilla reviewer workflows.

Downloaded source files remain ignored under `literature/hitl-resource-pack/downloads/`; tracked docs should cite metadata and links rather than copying external content.

## Thesis Use

Use the taxonomy to write Chapter 2 and to justify why M3 is not just storage. The novelty claim should focus on the combined lifecycle: selective trigger, structured capture, transparent reusable memory, and controlled reuse in later AI interpretation.
