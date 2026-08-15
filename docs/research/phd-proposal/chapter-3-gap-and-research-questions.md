# Chapter 3 — Gap and Research Questions

> **Status: complete draft for the 2026-08-12 supervisor meeting — not supervisor-approved.**
>
> Deliverable `A08-02` from the 2026-08-05 supervision call ("write the Gaps and Research Questions
> chapter in full"; goal for Aug 12 per `E15`). Written to the chapter skeleton confirmed in that
> call (`E13`): this chapter argues **the gap and the questions only**. The literature *synthesis*
> belongs to Chapter 2, the methodology and artifact design to Chapter 4; where this chapter cites
> literature it does so to establish that a question is open, not to review the field.
>
> **Wording status.** The research-question wording in §3.4–§3.7 is the live wording refined during
> the 2026-08-05 call and remains **provisional pending (a) verification against Ali's own saved
> working draft (`A08-01`) and (b) logged `D-RQ-01`/`D-RQ-02` decisions**.
>
> **Two source caveats.** (1) All references to the 2026-08-05 discussion derive from a machine
> transcript with inferred (undiarized) speakers; attributions are the record's inferences pending
> the participants' confirmation. (2) The systematic literature searches `QL-01`–`QL-05` are
> **protocol-ready but not executed**. The citations below therefore come from a *verified seed
> corpus* (the reference list of the research group's own MODELS/MAS4Models 2026 submission, plus
> the tracked human-AI-interaction and governance resource pack). They are sufficient to show that
> the questions are open; they are **not** a completed review, and every statement of the form "no
> established approach addresses X" is a **candidate claim** for Chapter 2 to establish or correct.

---

## 3.1 The interpretive step in AI-assisted assessment

AI systems are increasingly used to assess structured artifacts against norms: student models
against modeling guidelines, engineering documents against standards, clinical records against care
guidelines. This assessment task has a property that separates it from ordinary classification:
once a system has detected that an artifact *deviates* from the norm, something must decide what
the deviation **means**.

A recurring difference between a student's domain model and a reference solution may be a
legitimate alternative design, an outright error, a domain-specific convention, a defect in the
guideline itself, or a genuine ambiguity that competent experts would adjudicate differently. The
research group's own prior work names the two poles of this distinction — *substantial* variability
(systematic, meaningful, defensible variation) versus *occasional* variability (sporadic, erroneous
deviation) — and shows that treating all deviations uniformly both penalises valid modelling
competence and lets real errors pass undetected.

This interpretive step is exactly where automation is weakest and where human expertise is most
expensive. Everything in this chapter follows from that asymmetry.

## 3.2 What existing research establishes, and what it leaves open

Four bodies of work bear on the problem. Each establishes something real; each leaves a distinct
part of the interpretive step open.

### 3.2.1 Automated assessment of models

There is a mature line of work on automatically assessing models against a reference. Early
approaches matched diagrams structurally, including for explicitly *collaborative*
human–computer assessment [29] and for diagnosis in learning environments [4]. Automated grading of
class diagrams was developed and then critically examined by its own authors, who asked directly
whether such grading is effective [5, 6]. Later work detects mistakes in domain models [28],
assesses them through learned embeddings [12], and builds interoperable assessment infrastructure
for computing education [17].

**What it establishes.** Deviation from a reference can be detected and scored at scale.

**What it leaves open.** These approaches are predominantly built on structural similarity against a
*single* reference solution and treat deviations uniformly. They therefore cannot reason about
*conceptual justifiability* — whether a particular deviation is a defensible modelling decision —
nor aggregate deviations into patterns that reveal systematic difficulty. Detection is solved well
enough to be useful; **interpretation is not addressed**, and interpretation is the step that
requires human judgment.

### 3.2.2 LLM and agentic assistance for modelling

A rapidly growing literature applies LLMs to modelling tasks and to their assessment. On the
generation side, results are consistent and sobering: LLMs struggle with models beyond roughly
8–10 classes and misuse constructs such as association classes, multiple inheritance and
composition [10]; generative approaches outperform earlier non-generative ones for deriving domain
models yet still fall short of expert-produced models, introducing redundant elements, roles,
attributes and implementation constructs [8]; performance is highly variable and dependent on model
choice and prompting strategy, with associations and cardinalities persistently harder than classes
[9], a pattern confirmed across LLM families [12]. For sequence diagrams, structural correctness is
attainable but capturing behavioural semantics still requires substantial expert intervention [15].
Tooling has followed [24]. On the assessment side, LLMs have been used to score UML diagrams against
teaching-assistant baselines [7], to test whether multimodal LLMs can "grade like an expert" [18],
and to evaluate behavioural model correctness [1]. Process-modelling work has explored conversational
interaction with such systems [20]. Beyond single models, the field is moving to *agentic*
architectures: surveys chart the shift from LLMs to LLM-based agents in software engineering [19],
and specific proposals target multi-agentic automated software design and modelling [13] and
multi-agent software development platforms [26].

**What it establishes.** LLM- and agent-based assistance for modelling and for model assessment is
feasible, is being actively built, and reliably needs expert correction.

**What it leaves open.** Two things. First, monolithic LLM evaluation is prone to inconsistency and
conflates language-level violations with domain-level misunderstandings — the motivation for
decomposing assessment across specialised agents in the first place. Second, and more importantly
for this proposal: this literature documents *that* expert intervention is needed [15, 8, 9]
without answering *when* it should be requested, *what* should be retained from it, or *whether*
what is retained may be applied to a later case. Expert intervention appears in these works as a
remedy for a system's shortfall, not as a governed, reusable asset.

### 3.2.3 Human involvement in the loop

Human-in-the-loop machine learning is itself a surveyed field [HITL-001], and design guidance for
human–AI interaction is well established, including guidance on transparency, error recovery and
calibrated reliance [HAI-001]; governance frameworks set out expectations for human oversight of AI
systems [GOV-001]. Within modelling specifically, the closest work to this proposal moves explicitly
toward human-in-the-loop LLM-enabled domain modelling [27], and empirical work characterises how
practitioners actually interact with LLMs for conceptual modelling, identifying recurrent intentions
and interaction patterns and reporting user perception [2].

**What it establishes.** Human involvement in automated decision systems is a surveyed research area
with an organised body of mechanisms [HITL-001], an established set of interaction design guidelines
[HAI-001], and an explicit governance expectation of human oversight [GOV-001]; and human-in-the-loop
domain modelling is an active, named research direction [27]. (Note the framing: human oversight is
*expected and studied*, which is a weaker and more defensible premise than "human involvement
improves outcomes" — that stronger claim is not asserted here and is not needed for the argument.)

**What it leaves open.** The *selective-intervention problem for agentic assessment*. When a
multi-step, tool-using process emits hundreds of candidate judgments, on which of them should scarce
expert attention be spent? Blanket review does not scale and defeats the purpose of automation;
threshold-only routing inherits the calibration weaknesses of the underlying models. How an agentic
assessment process should decide, *during its own operation* and under an explicit budget of expert
attention, that a particular uncertainty warrants interrupting a human, is — on the seed corpus —
not resolved. This is a candidate claim for `QL-01`/`QL-04` to establish or refute.

### 3.2.4 Variability — and what the term means here

**Construct definition.** "Variability" is a heavily studied term in software engineering, with
systematic reviews of variability in software systems [16], of variability models [23], and of
metrics for variability and its implementation [14]; conceptual unification across space and time
[3]; foundational software product line engineering [22] and its subsequent assessment [21]; and
surveys of business process variability [25]. In that tradition variability is **designed**:
intentional, planned variation within a product or process family, to be modelled and managed.

**This thesis uses the term in a different sense**, and the difference is load-bearing. Here
variability is **observed and interpretive**: unplanned differences between artefacts produced
independently against the same guideline, whose *meaning* — legitimate alternative versus error — is
precisely what is unknown. Relatedly, *guideline operationalization* denotes turning a
natural-language norm into assessable reference expectations; dialogue-based approaches to eliciting
such models have been surveyed under conversational process modelling [20]. Both constructs are
carried into Chapter 2 for formal definition against the completed review.

**What it establishes.** A rich vocabulary and formalism for variability.

**What it leaves open.** The shared term conceals different phenomena, so the formalism does not
transfer to the interpretive case. On title-level evidence from the seed corpus — to be confirmed at
full text and by `QL-03` — no framework in this line classifies *observed interpretive* deviations by
justifiability, and none treats expert rulings about such deviations as reusable, scoped knowledge.

### 3.2.5 Positioning summary

| Body of work | Establishes | Does not address | Bears on |
| --- | --- | --- | --- |
| Automated model assessment [4, 5, 6, 12, 17, 28, 29] | Deviation can be detected and scored at scale against a reference | Conceptual justifiability of a deviation; pattern-level interpretation | Framing of §3.1 |
| LLM / agentic modelling assistance [1, 2, 7–13, 15, 18–20, 24, 26] | Assistance is feasible and consistently requires expert correction | *When* to request expertise; *what* to retain; *whether* it may be reused | SQ1, SQ2 |
| Human-in-the-loop & oversight [2, 27, HITL-001, HAI-001, GOV-001] | Human involvement helps; general mechanisms and governance expectations exist | Selective intervention under an attention budget in agentic, multi-step assessment | SQ1 |
| Variability engineering [3, 14, 16, 21–23, 25] | Vocabulary and formalism for *designed* variability | *Observed, interpretive* variability and the justifiability of deviations | Framing of U-RQ |

*(Numeric citations follow the reference list of the group's MODELS/MAS4Models 2026 submission; keyed
citations follow the tracked resource pack. Chapter 2 will renumber against the completed review.)*

## 3.3 The gap

Stated compactly:

> **The design knowledge for connecting selective expert intervention, structured judgment capture,
> and scope-aware reuse in agentic AI assessment does not exist in tested, generalizable form — and
> neither does an evaluation approach able to establish which parts of such a connected lifecycle
> transfer across contexts and which do not.**

The pieces are studied in isolation. Assessment research detects deviations but does not interpret
them (§3.2.1). Agentic-assistance research needs expert correction but treats it as a one-off repair
(§3.2.2). Human-in-the-loop research supplies mechanisms but not a selection policy for agentic
assessment under bounded attention (§3.2.3). Variability research supplies formalism for a different
kind of variability (§3.2.4). **The interaction between the pieces — when to ask → what to keep →
where it may legitimately be reused — is where the open scientific questions sit.**

Three properties make expert judgment about assessment resistant to the two mature capture
paradigms. Static knowledge bases capture expert rules explicitly but detached from the cases that
motivated them; fine-tuning and preference learning absorb human signals into model weights, where
they become uninspectable, unattributable and irrevocable. Expert assessment judgment is instead:

- **case-grounded** — an expert rules on *this* deviation, in *this* artefact, under *this*
  guideline;
- **scoped** — the ruling may hold for one course, one organisation, or one domain, and its
  generality is itself unknown at capture time;
- **contestable** — a later expert, or the same expert with more context, may disagree;
- **authority-bearing** — institutions need to know whose judgment is being applied and whether it
  is still endorsed.

Neither paradigm preserves all four. What is missing is a governed middle path.

**Two boundary clarifications** keep this an honest research gap rather than a product pitch.
First, the gap is not "no tool does this yet"; it is that the *design knowledge* — what information a
reusable judgment must carry, what governance prevents unsafe reuse, what intervention policies
preserve assessment quality under an attention budget, and what transfer-classification criteria are
valid — does not exist in tested form. Second, **nothing below presupposes that reusable judgment
improves assessment.** Whether it does, under which controls, and at what expert cost, is an
empirical outcome of the research; negative and null results are informative and will be reported.

## 3.4 Main research question

> **U-RQ.** How can human judgment be captured, governed, and used to support agentic-AI-driven
> variability exploration in guideline operationalization scenarios, enabling reliable human–AI
> co-reasoning?

*(Provisional live wording from the 2026-08-05 call; pending `D-RQ-01` sign-off.)*

Three commitments from that discussion shape it:

- **It names the task, not the solution** (`E4`, `E6`). The object of study is *variability
  exploration in guideline operationalization scenarios* — deciding which deviations from an
  operationalised guideline are meaningful variability and which are noise or error. Agentic AI
  appears as the assessment setting whose reliability is at stake, not as a claim that a particular
  agent architecture is the contribution.
  **Wording discrepancy flagged for `A08-01`:** the machine-derived record states `E6` as narrowing
  the question to variability *identification/classification*, whereas the reconstructed live wording
  above says variability *exploration*. These are not synonyms — "exploration" is broader and
  includes pattern discovery. The saved working draft must settle which was agreed; this chapter does
  not choose silently.
- **Reuse is not in the headline** (`E5`). Whether and how captured judgment may be *reused* is a
  governed, empirically testable concern belonging to the sub-questions — SQ2 captures and governs,
  SQ3 tests transfer. The headline asks only how human judgment can support the activity reliably.
- **"Reliable" is the retained quality target** (`E7`). Earlier drafts also carried "auditable",
  "transferable" and "end-to-end"; these are either sub-question concerns (transfer → SQ3) or
  properties of an artefact rather than of a question, and the live session leaned toward dropping
  them to keep the question sharp — a leaning the Aug-12 sign-off should ratify or reverse.

The question is **domain-neutral by design** (`E13`). Software/modelling and healthcare are
*instantiation contexts* (§3.9), not part of the question's wording.

## 3.5 SQ1 — Selective intervention

> **SQ1.** When and how, in variability exploration scenarios, should an agentic assessment system
> request human judgment so that important uncertainties are addressed without unnecessary expert
> burden?

**Why this is open.** Both extreme policies are known failures: review-everything does not scale and
spreads expert attention thinnest exactly where density is needed, while review-nothing forfeits the
interpretive step of §3.1. Between them lies a policy space — which uncertainty signals to trust,
what "important" means for a deviation, what dosage of review a workflow can absorb, when a request
expires or escalates. The human-in-the-loop literature supplies mechanisms [HITL-001] and interaction
guidance [HAI-001] but, on the seed corpus, not a selection policy for *agentic, multi-step*
assessment under a bounded attention budget; the modelling literature establishes that expert
intervention is needed [15, 8] without saying when to invoke it. Even the closest human-in-the-loop
modelling work [27] positions the human in the modelling activity rather than solving the routing
problem for a multi-agent assessment pipeline. `QL-01`/`QL-04` will test this.

**Answerable independently of any system.** Its outputs are intervention criteria, dosage/budget
policies, and their measured consequences for coverage of important uncertainty versus expert load —
statable and testable without reference to a particular implementation.

**Evaluation criterion built into the question** (`E9` symmetry). Success is explicitly two-sided:
important uncertainties addressed **and** expert burden bounded. A policy achieving coverage by
flooding the expert fails SQ1 by definition. This is what makes the question falsifiable rather than
aspirational.

## 3.6 SQ2 — Governed knowledge reuse

> **SQ2.** How should expert judgment — including the system's core reasoning — be represented,
> validated, reconciled, and stored so it can be reused transparently without unsafe generalization
> or loss of human authority?

**Why this is open.** §3.3 argued that the two mature capture paradigms each destroy properties that
expert assessment judgment requires. Designing a representation and governance regime that preserves
case-grounding, scope, contestability and attributable authority is not an engineering detail: it
determines whether reuse is *scientifically evaluable at all*, because an ungoverned judgment store
cannot support claims about which judgment produced which downstream effect.

**Two conceptually distinct halves** (`E8`). Following the capture-versus-transfer split from the
2026-08-05 discussion, SQ2 deliberately spans — and keeps separate — (a) the **capture** problem:
what the expert actually said, about which case, with what rationale, against which system reasoning;
and (b) the **forward-transfer** problem: under what conditions that captured judgment may inform a
future case at all. The second half hands over to SQ3 at the point where "may it be reused" becomes
"does reuse hold up across contexts".

**Core reasoning is inside the question** (`E9`). The judgment worth capturing is not a bare label.
The expert responds to the system's own core reasoning — the argument the agentic process gives for
flagging a deviation — and may endorse, correct, or reject *that reasoning*, not merely the verdict.
A representation that drops the reasoning cannot distinguish "the expert disagreed with the
conclusion" from "the expert disagreed with the argument", and those carry different reuse
implications. Relatedly, decomposing assessment across specialised agents is what makes a "core
reasoning" object well defined at all: a monolithic evaluator conflates language-level and
domain-level judgments, leaving nothing specific for an expert to endorse or reject.

**Evaluation criterion built into the question** (`E9`). Two failure modes bound the design:
*unsafe generalization* (a judgment applied beyond the scope its evidence supports) and *loss of
human authority* (reuse the original expert can no longer see, contest, or revoke). A store that
maximises reuse by ignoring scope fails SQ2 **even if downstream accuracy improves** — the criterion
is deliberately not reducible to accuracy.

**Terminology** (`E8`). "Expert judgment" is deliberate rather than "human judgment": in the medical
instantiation the source is a physician; in the software/modelling instantiation it is course- or
team-level engineering rigour. What SQ2 governs is *accountable domain expertise*, not crowd
feedback. (The `E8` record marks "expert" as a leaning, not a closed choice; the Aug-12 sign-off
should settle it.)

**An asymmetry to resolve, not to paper over.** The main question and SQ1 say "human judgment";
SQ2 and SQ3 say "expert judgment". Whether the main question is deliberately broader — humans in
general supply the judgment, accountable experts supply the *reusable* judgment — or whether this is
residue from the live-edit session is an `A08-01` verification item and a `D-RQ-01` decision. The
terms are **not** harmonised unilaterally here, because doing so would overwrite whichever wording
was actually agreed.

## 3.7 SQ3 — Evaluation and transfer

> **SQ3.** How can expert judgment be reused and transferred across different
> guideline-operationalization contexts without unsafe generalization or loss of human authority,
> first in software/modeling and, when governance and access permit, in healthcare?

**Why this is open.** Even a perfectly governed judgment store (SQ2) leaves the empirical question:
*which judgments actually hold outside the context that produced them?* Answering it requires a
distinction the field does not currently operationalise, and which `E12` placed at the analytic core
of SQ3 — between uncertainty that is **domain-specific** (the system lacks clinical, legal or
pedagogical context that only a domain expert holds) and uncertainty that reflects a **general
capability gap** (the system fails at something equally hard in every domain). The distinction is
practical, not philosophical: judgments attached to general capability gaps are candidates for broad
reuse, while judgments attached to domain-specific uncertainty must stay confined.

A **candidate** general capability gap, raised in the 2026-08-05 discussion and recorded as `E12`
(machine-derived, unverified), is failure to identify the *actors and use cases* of a described
system: if genuinely domain-independent, judgments about it would be transfer candidates. Whether it
is in fact domain-independent is itself an SQ3 question, not a premise. The contrasting case is
uncertainty about whether a chronic-pain treatment sequence may deviate from a clinical guideline,
which is plainly domain-bound. Existing evaluations of AI-assisted assessment [6, 7, 18] report
quality against a reference within a single setting and, on title-level evidence from the seed corpus,
do not separate these two sources of residual uncertainty. Without such a classification, **any claim
that reused judgment "transfers" is untestable**. `QL-03`/`QL-04` will test this characterisation.

**SQ3 therefore asks for two things**: the criteria that make the domain-specific/transferable
distinction operational, and the evidence discipline that tests transfer honestly — independent
labelling, leakage controls between the context that produced a judgment and the context in which it
is evaluated, and pre-registered success criteria.

**Transfer is staged, and the stages are governed.** First transfer tests stay inside
software/modelling (across settings, diagram types and domains within the existing corpus, then an
authorised external context under Plan B). The healthcare extension is explicitly conditional —
"when governance and access permit" is part of the wording because the medical instantiation is
gated by use-case, personnel, authorisation, ethics/privacy, environment and protocol prerequisites
that are institutional facts, not research variables. **The question remains fully answerable in
software/modelling alone**; healthcare tests its outer boundary. The two guideline contexts raised on
2026-08-05 (`E11`) — a chronic-pain management guideline and an age-related macular degeneration
guideline — share almost nothing at domain level, which is precisely why a classification, rather
than a blanket transfer claim, is the scientifically defensible target.

**Retained-language note** (`E10`). "Transparently" drew a mild, non-critical reservation in the
SQ3 discussion; it currently sits in SQ2's wording and is retained pending the final wording
sign-off. The relocation is a derived interpretation, flagged for Aug-12 review.

## 3.8 The three questions as one research programme

| | Asks | Produces | Hands over |
| --- | --- | --- | --- |
| **SQ1** | *When* should the system ask an expert? | Intervention criteria; dosage/budget policies | Captured expert responses → SQ2 |
| **SQ2** | *What* must be kept, and under what governance? | Judgment representation; validation/reconciliation; provenance, scope, authority controls | Governed, scoped judgments → SQ3 |
| **SQ3** | *Where else* does a judgment hold, and how would we know? | Domain-specific vs. transferable classification; leakage-safe transfer evidence | Boundary conditions back into SQ1/SQ2 policies |

Each sub-question maps to exactly one primary study (Studies 1–3 respectively), preserving the
one-question-one-study discipline recorded on 2026-07-29 and consistent with the 2026-08-05 record.

**An open decomposition question, stated rather than hidden.** Together the three sub-questions
address the *capture*, *governance* and *use* elements of the main question. Whether they are
**jointly sufficient** for "reliable human–AI co-reasoning" is not settled here: SQ1 asks when to
ask, SQ2 what to keep, SQ3 where it holds — none of them takes *reliability of the co-reasoning
itself* as its object, even though the main question names it as the outcome. Either reliability is
emergent from the three, or it requires separate treatment. This is a live question for `D-RQ-01`
and a deliberate item for the Aug-12 discussion. Failing any one sub-question still localises which
part of the lifecycle is out of reach — which is itself a reportable result.

## 3.9 Relationship to the motivating case

VEGO-AI — a four-agent pipeline that operationalises modelling guidelines and explores variability in
student-built domain models — is the **motivating case and initial instantiation platform**, not the
object of study. Its role in this chapter is evidential only: it demonstrates that the gap is real in
a concrete, instrumented setting. Its pipeline already emits uncertainty signals and review flags,
and has no governed way to capture or reuse the expert judgment those flags request; offline
reconstruction of one full run shows that only a small fraction of the observable decision points
were ever visible to its post-hoc review queue. That is the gap of §3.3, observed rather than argued.

The research questions are not questions *about* VEGO-AI, and Chapter 4 treats it as one of two
instantiation contexts. **The question is the contribution; the platform is the vehicle.** This
separation is maintained deliberately throughout the proposal, following the direction recorded on
2026-08-05 (`E4`).

## 3.10 Scope boundaries

**In scope:** selective-intervention policy design; structured judgment representation with
provenance, scope, conflict and authority governance; scope-aware advisory reuse; domain-specific
versus transferable classification of uncertainty and judgments; leakage-safe transfer evaluation in
software/modelling; a governance-gated healthcare extension.

**Out of scope:** autonomous modification of the underlying assessment pipeline by reused judgment;
any accuracy or effort-reduction claim ahead of the independent-label evidence gates; medical data
processing before all six entry gates pass; and any claim that captured judgment is ground truth —
captured judgment is *governed evidence*, contestable by design.

## 3.11 Evidence status and falsifiability

Stated plainly, so that Chapter 5 (Preliminary Results) cannot be over-read:

| Element | Current status |
| --- | --- |
| Literature searches `QL-01`–`QL-05` | Protocol-ready, **not executed**; §3.2 openness statements are candidate claims |
| Independent expert labels (EXP-005) | **0 of 24** generalization-safe labels supplied |
| Software/modelling evidence | Mechanism, architecture and readiness evidence only |
| Medical instantiation | Infrastructure/feasibility only; all six entry gates open |
| Accuracy / generalization / clinical performance | **No claim is made or supported** |

Each question is falsifiable on its own terms. SQ1 fails if no intervention policy achieves
acceptable coverage of important uncertainty within a defensible expert budget — a finding worth
reporting. SQ2 fails if no representation preserves case-grounding, scope, contestability and
authority simultaneously, or if governance costs exceed the value of reuse. SQ3 fails if the
domain-specific/transferable classification cannot be made to discriminate reliably, or if transfer
evidence does not survive leakage controls. **A negative result in any of the three is a genuine
contribution**, because it bounds what reliable human–AI co-reasoning can be asked to deliver.

---

## Seed-corpus references

Numeric entries `[1]`–`[29]` are the reference list of the research group's own MODELS/MAS4Models
2026 submission (`Variability_MAS4MODELS2026_Mar28`), reproduced here as the verified seed corpus for
this chapter. Keyed entries are from the tracked human-AI-interaction and governance resource pack
(`literature/hitl-resource-pack/source-manifest.csv`). **This list is a seed, not a review**:
Chapter 2 will renumber and extend it against the executed `QL-01`–`QL-05` searches.

[1] Ahmed, K., Song, J., Chen, B., Wei, O., & Zheng, B. (2025). MCeT: Behavioral Model Correctness Evaluation using Large Language Models. *Proc. ACM/IEEE 28th MODELS*, 84–95.
[2] Ali, S. J., Reinhartz-Berger, I., & Bork, D. (2024). How are LLMs used for conceptual modeling? An exploratory study on interaction behavior and user perception. *Int. Conf. Conceptual Modeling*, 257–275. Springer.
[3] Ananieva, S., Greiner, S., Kehrer, T., Krüger, J., Kühn, T., Linsbauer, L., Grüner, S., Koziolek, A., Lönn, H., Ramesh, S., & Reussner, R. (2022). A conceptual model for unifying variability in space and time. *Empirical Software Engineering*, 27(5), 101.
[4] Auxepaules, L., Py, D., & Lemeunier, T. (2008). A diagnosis method that matches class diagrams in a learning environment for object-oriented modeling. *ICALT 2008*, 26–30. IEEE.
[5] Bian, W., Alam, O., & Kienzle, J. (2019). Automated grading of class diagrams. *MODELS-C 2019*, 700–709. IEEE.
[6] Bian, W., Alam, O., & Kienzle, J. (2020). Is automated grading of models effective? Assessing automated grading of class diagrams. *MODELS 2020*, 365–376.
[7] Bouali, N., Gerhold, M., Rehman, T. U., & Ahmed, F. (2025). Toward Automated UML Diagram Assessment: Comparing LLM-Generated Scores with Teaching Assistants. *Proc. CSEDU*, 158–169.
[8] Bragilovski, M., van Can, A. T., Dalpiaz, F., & Sturm, A. (2025). Leveraging machines to derive domain models from user stories. *Requirements Engineering*, 30(2), 241–262.
[9] Calamo, M., Mecella, M., & Snoeck, M. (2025). Assessing the Suitability of Large Language Models in Generating UML Class Diagrams as Conceptual Models. *BPMDS 2025*, 211–226. Springer.
[10] Cámara, J., Troya, J., Burgueño, L., & Vallecillo, A. (2023). On the assessment of generative AI in modeling tasks: an experience report with ChatGPT and UML. *Software and Systems Modeling*, 22(3), 781–793.
[11] Chaaben, M. B., Burgueño, L., David, I., & Sahraoui, H. (2024). On the utility of domain modeling assistance with large language models. arXiv:2410.12577.
[12] Chen, K., Chen, B., Yang, Y., Mussbacher, G., & Varró, D. (2024). Embedding-based Automated Assessment of Domain Models. *MODELS Companion '24*, 87–94.
[13] Dam, H. K. (2025). Towards Multi-Agentic AI for automated software design and modelling. *Proc. ASEW 2025*, 311–314.
[14] El-Sharkawy, S., Yamagishi-Eichler, N., & Schmid, K. (2019). Metrics for analyzing variability and its implementation in software product lines: A systematic literature review. *Information and Software Technology*, 106, 1–30.
[15] Ferrari, A., Abualhaija, S., & Arora, C. (2024). Model generation with LLMs: From requirements to UML sequence diagrams. *IEEE REW 2024*, 291–300.
[16] Galster, M., Weyns, D., Tofan, D., Michalik, B., & Avgeriou, P. (2013). Variability in software systems – a systematic literature review. *IEEE Transactions on Software Engineering*, 40(3), 282–306.
[17] Hamann, M., Götz, S., & Aßmann, U. (2024). Towards an Interoperable Model-driven Automated Assessment System for Computer Science Education. *MODELS Companion '24*, 95–102.
[18] Ibáñez, M. B., Barrón-Estrada, M. L., & Zatarain-Cabada, R. (2025). Can multimodal large language models grade like an expert? A study on UML class diagram assessment accuracy. *Computer Applications in Engineering Education*, 33(5).
[19] Jin, H., Huang, L., Cai, H., Yan, J., Li, B., & Chen, H. (2024). From LLMs to LLM-based agents for software engineering: A survey. arXiv:2408.02479.
[20] Klievtsova, N., Benzin, J.-V., Kampik, T., Mangler, J., & Rinderle-Ma, S. (2023). Conversational process modelling: State of the art, applications, and implications in practice. *BPM Forum 2023*, 319–336. Springer.
[21] Metzger, A., & Pohl, K. (2014). Software product line engineering and variability management: achievements and challenges. *Future of Software Engineering Proceedings*, 70–84.
[22] Pohl, K., Böckle, G., & van der Linden, F. (2005). *Software product line engineering: foundations, principles, and techniques*. Springer.
[23] Pol'la, M., Buccella, A., & Cechich, A. (2021). Analysis of variability models: a systematic literature review. *Software and Systems Modeling*, 20, 1043–1077.
[24] Rajbhoj, A., Somase, A., Sant, T., Vale, S., & Kulkarni, V. (2025). LLM4Model: Automated Requirements Specification Model Authoring. *CAiSE 2025*, 128–136. Springer.
[25] Rosa, M. L., van der Aalst, W. M. P., Dumas, M., & Milani, F. P. (2017). Business process variability modeling: A survey. *ACM Computing Surveys*, 50(1), 1–45.
[26] Sami, M. A., Waseem, M., Rasheed, Z., Saari, M., Systä, K., & Abrahamsson, P. (2024). Experimenting with multi-agent software development: Towards a unified platform. arXiv:2406.05381.
[27] Silva, J., Ma, Q., Cabot, J., Kelsen, P., & Proper, H. A. (2025). Towards Human-in-the-Loop LLM-Enabled Domain Modeling. *Int. Conf. Conceptual Modeling*, 127–145. Springer.
[28] Singh, P., Boubekeur, Y., & Mussbacher, G. (2022). Detecting mistakes in a domain model. *MODELS '22 Companion*, 257–266.
[29] Tselonis, C., Sargeant, J., & Wood, M. M. (2005). Diagram matching for human-computer collaborative assessment. *9th Int. Computer Assisted Assessment Conf.*

**Resource-pack entries** (tracked metadata; local downloads are git-ignored):

- `[HAI-001]` Amershi, S. et al. (2019). *Guidelines for Human-AI Interaction.* CHI 2019. — human-AI interaction design guidance.
- `[HITL-001]` (2022). *Human-in-the-loop machine learning: a state of the art.* Artificial Intelligence Review. — HITL/active-learning survey.
- `[GOV-001]` NIST (2023). *AI Risk Management Framework 1.0.* — governance and human-oversight expectations.
- `[MDE-001]` *AI Assisted Domain Modeling: Explainability and Traceability.* ACM DOI 10.1145/3652620.3688197 — metadata only; full text not obtained.

---

*Draft prepared for the 2026-08-12 supervisor review against the canonical 2026-08-05 meeting record
(`E1`–`E15`). Wording provisional pending `A08-01` verification and logged `D-RQ-01`/`D-RQ-02`
decisions. Citations are from a verified seed corpus, not a completed systematic review.*
