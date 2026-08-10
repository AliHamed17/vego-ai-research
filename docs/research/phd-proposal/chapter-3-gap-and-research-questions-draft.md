# Chapter 3 — Gap and Research Questions (Full Draft for the Word Proposal)

> **Status: complete working draft for the 2026-08-12 supervisor meeting — not supervisor-approved.**
> Deliverable required by the 2026-08-05 call (`A08-02`: "Write the Gaps and Research Questions
> chapter in full"; goal for Aug 12 per `E15`). The research-question wording below is the live
> wording refined during that call and remains **provisional pending (a) verification against
> Ali's own saved working draft (`A08-01`) and (b) a logged `D-RQ-01`/`D-RQ-02` decision**.
> Built to the chapter skeleton confirmed in that discussion (`E13`): this chapter argues the
> *gap and the questions only* — methodology, artifacts, and evaluation design belong to
> Chapter 4, and the literature synthesis itself to Chapter 2. Paste-ready for the Word proposal.
>
> Two source caveats carried from the canonical record: (1) all references to the 2026-08-05
> discussion derive from a machine transcript with inferred (undiarized) speakers — attributions
> are the record's inferences, pending the participants' own confirmation; (2) the literature
> searches (QL-01–QL-05) have **not been executed**, so every literature-gap statement in §3.1
> is a candidate claim to be established or corrected by the completed review, not a finding.

## 3.1 The gap

AI systems based on large language models are increasingly used to assess structured artifacts
against norms: student models against modeling guidelines, engineering documents against
standards, clinical records against care guidelines. In all of these settings the assessment
task has a property that distinguishes it from classification benchmarks: after the system has
detected that an artifact *deviates* from the norm, someone must decide what the deviation
*means*. A recurring difference between a student's model and the reference solution may be a
legitimate alternative design, an error, a domain-specific convention, a defect in the guideline
itself, or an ambiguity that reasonable experts would adjudicate differently. This interpretive
step — deciding which of these a deviation is — is precisely where automated assessment is
least reliable and where human expertise is most expensive.

Three bodies of work approach this problem from different directions, and each leaves a
distinct part of it open.

**First, human-in-the-loop and human oversight research** has established *that* human
involvement improves the safety and acceptability of automated decision systems, and offers
general mechanisms — review queues, confidence thresholds, escalation rules. What it does not
settle is the *selective-intervention problem for agentic assessment*: when a multi-step,
tool-using AI process produces hundreds of candidate judgments, on which of them should human
attention be spent? Blanket review does not scale and defeats the purpose of automation;
threshold-only triggers inherit the calibration weaknesses of the underlying models. The open
question — which, to our knowledge, the human-oversight literature has not resolved for
agentic, multi-step assessment, subject to confirmation by the frozen literature searches — is
how an agentic assessment process should *decide, during its own operation*, that a particular
uncertainty is important enough to interrupt a human, and how to do this under an explicit
budget of expert attention rather than an idealized unlimited reviewer.

**Second, knowledge-capture and expertise-reuse research** — from classic knowledge engineering
to modern feedback-learning pipelines — addresses how human input can improve a system. At one
extreme, knowledge bases capture expert rules explicitly but statically, detached from the
cases that motivated them; at the other, fine-tuning and preference-learning absorb human
signals into model weights, where they become uninspectable, unattributable, and irrevocable.
Neither extreme fits expert judgment about artifact assessment, which is *case-grounded* (an
expert rules on this deviation, in this artifact, under this guideline), *scoped* (the ruling
may hold for one course, one organization, or one domain — its generality is itself unknown at
capture time), *contestable* (a later expert, or the same expert with more context, may
disagree), and *authority-bearing* (institutions need to know whose judgment is being applied
and whether it is still endorsed). What is missing is a governed middle path: a way to
represent an expert judgment — together with the reasoning that produced it, both the human's
rationale and the system's own core reasoning that the human saw and responded to — so that it
can be validated, reconciled with conflicting judgments, stored with provenance and scope, and
brought back in future cases without silently overgeneralizing and without the human losing
authority over how their judgment is used.

**Third, evaluation and transfer research** in AI-assisted assessment appears, to our
knowledge, to report predominantly single-domain results (a candidate claim the QL-03/QL-04
searches must test). When human-AI assessment pipelines are evaluated at all, the evaluation
rarely separates two very different sources of residual uncertainty: uncertainty that is
*domain-specific* (the system lacks the clinical, legal, or pedagogical context that only a
domain expert holds) and uncertainty that reflects a *general capability gap* (the system fails
at something — such as identifying the actors and use cases of a described system — that is
equally hard in every domain and equally improvable everywhere). The distinction matters
practically: judgments attached to general capability gaps are candidates for broad reuse,
while judgments attached to domain-specific uncertainty must stay confined to their domain.
We are not aware of an established framework that classifies captured expert judgments along
this axis — the completed literature review must confirm or refute this — and without such a
classification, any claim that reused judgment "transfers" is untestable.

The gap, stated compactly: **the design knowledge for connecting selective expert
intervention, structured judgment capture, and scope-aware reuse in agentic AI assessment does
not exist in tested, generalizable form — nor does an evaluation approach that can tell which
parts of such a connected lifecycle transfer across domains and which do not.** Existing work
studies the pieces in isolation; the interaction between them (when to ask → what to keep →
where it may be reused) is exactly where the open scientific questions sit.

Two boundary clarifications keep this an honest research gap rather than a product pitch.
First, the gap is not "no tool does this yet"; it is that the *design knowledge* — what
information a reusable judgment must carry, what governance prevents unsafe reuse, what
intervention policies preserve assessment quality under an attention budget, what
transfer-classification criteria are valid — does not exist in tested, generalizable form.
Second, none of the questions below presuppose that reusable judgment *improves* assessment;
whether it does, under which controls, and at what expert cost, is an empirical outcome of the
research, and negative results are informative.

## 3.2 Main research question

> **U-RQ.** How can human judgment be captured, governed, and used to support agentic-AI-driven
> variability exploration in guideline operationalization scenarios, enabling reliable human–AI
> co-reasoning?

*(Provisional live wording from the 2026-08-05 supervisor call; pending `D-RQ-01` sign-off.)*

The question is deliberately structured around three commitments that came out of the
2026-08-05 supervision discussion:

- **It names the task, not the solution.** The object of study is *variability exploration in
  guideline operationalization scenarios* — deciding which deviations from an operationalized
  guideline are meaningful variability and which are noise or error. Agentic AI appears in the
  question as the assessment setting whose reliability is at stake, not as a claim that a
  particular agent architecture is the contribution.
- **Reuse is not in the headline.** Whether and how captured judgment may be *reused* is a
  governed, empirically testable concern that belongs to the sub-questions (SQ2 captures and
  governs; SQ3 tests transfer); the main question asks only how human judgment can support the
  activity reliably.
- **"Reliable" is the retained quality target.** Earlier drafts carried "auditable,"
  "transferable," and "end-to-end" in the headline; these are either sub-question concerns
  (transfer → SQ3) or properties of the artifact rather than the question, and the live-edit
  session leaned toward dropping them from the headline to keep the question sharp (a leaning
  the Aug-12 sign-off should ratify or reverse).

The question is domain-neutral by design. Software/modeling and healthcare are the two
*instantiation contexts* of this research (Section 3.6), but nothing in the question's wording
binds it to either — an explicit requirement from the 2026-08-05 supervision discussion
(per the machine-derived record) that domain framing live in the methodology chapter, not the
question.

## 3.3 SQ1 — Selective intervention

> **SQ1.** When and how, in variability exploration scenarios, should an agentic assessment
> system request human judgment so that important uncertainties are addressed without
> unnecessary expert burden?

**Why this is open.** The two extreme policies are both known failures: review-everything does
not scale and dilutes expert attention exactly where it matters least, and review-nothing
forfeits the interpretive step that Section 3.1 identified as the heart of the task. Between
them lies a policy space — which uncertainty signals to trust, what importance means for a
deviation, what dosage of review a workflow can absorb, when a request expires or escalates —
that, to our knowledge, current human-oversight literature does not resolve for agentic,
multi-step assessment (QL-01/QL-04 will test this).
The question is answerable independently of any particular system: its outputs are
intervention criteria, dosage/budget policies, and their measured consequences for coverage of
important uncertainty versus expert load.

**Evaluation criterion built into the question.** Success is explicitly two-sided — important
uncertainties addressed *and* expert burden bounded. A policy that achieves coverage by
flooding the expert fails SQ1 by definition, which is what makes the question falsifiable
rather than aspirational.

## 3.4 SQ2 — Governed knowledge reuse

> **SQ2.** How should expert judgment — including the system's core reasoning — be represented,
> validated, reconciled, and stored so it can be reused transparently without unsafe
> generalization or loss of human authority?

**Why this is open.** As Section 3.1 argued, the two mature capture paradigms (static knowledge
bases; weight-absorbed feedback) both destroy properties that expert assessment judgment needs:
case-grounding, scope, contestability, and attributable authority. Designing a representation
and governance regime that preserves them is not an engineering detail — it determines whether
reuse is scientifically evaluable at all, because an ungoverned judgment store cannot support
claims about *which* judgment produced *which* downstream effect.

**Two conceptually distinct halves.** Following the capture-vs-transfer framing from the
2026-08-05 discussion (attributed to Arnon in the machine-derived record),
SQ2 deliberately spans — and keeps separate — (a) the *capture* problem: what the expert
actually said, about which case, with what rationale, against which system reasoning; and (b)
the *forward-transfer* problem: under what conditions that captured judgment may inform a
future case at all. The second half hands over to SQ3 at the point where "may it be reused"
becomes "does reuse hold up across contexts."

**Core reasoning is inside the question.** The judgment worth capturing is not a bare label.
The expert responds to the system's own core reasoning — the argument the agentic process
gives for flagging a deviation — and may endorse, correct, or reject that reasoning, not just
the verdict. A representation that drops the reasoning cannot distinguish "the expert
disagreed with the conclusion" from "the expert disagreed with the argument," and those have
different reuse implications. This is why the question names the system's core reasoning
explicitly rather than treating capture as label-collection.

**Evaluation criterion built into the question.** Symmetric to SQ1 and SQ3: the design must
balance correctness against completeness of what is captured and reused, and two failure modes
bound it — *unsafe generalization* (a judgment applied beyond the scope its evidence supports)
and *loss of human authority* (reuse the original expert can no longer see, contest, or
revoke). A store that maximizes reuse by ignoring scope fails SQ2 even if downstream accuracy
improves.

**Terminology.** "Expert judgment" is deliberate (rather than "human judgment"): in the medical
instantiation the judgment source is a physician; in the software/modeling instantiation it is
course-level or team-level engineering rigor. What SQ2 governs is *accountable domain
expertise*, not crowd feedback.

## 3.5 SQ3 — Evaluation and transfer

> **SQ3.** How can expert judgment be reused and transferred across different
> guideline-operationalization contexts without unsafe generalization or loss of human
> authority, first in software/modeling and, when governance and access permit, in healthcare?

**Why this is open.** Even a perfectly governed judgment store (SQ2) leaves the empirical
question: which judgments actually hold outside the context that produced them? Section 3.1
noted that the field lacks a classification separating domain-specific from broadly
transferable uncertainty — and following the correction recorded in the 2026-08-05 discussion
(attributed to Arnon in the machine-derived record), that classification is the analytic core
of SQ3, not an afterthought. Failure to identify the actors and use cases
of a described system is a *general* capability gap: judgments about it are transfer
candidates. Uncertainty about whether a chronic-pain treatment sequence may deviate from a
clinical guideline is *domain-bound*: judgments about it must not travel. SQ3 asks for the
criteria that make this distinction operational, and for the evidence discipline that tests
transfer honestly — independent labels, leakage controls between the context that produced a
judgment and the context in which it is evaluated, and pre-registered success criteria.

**Transfer is staged, and the stages are governed.** The first transfer tests stay inside
software/modeling (across settings, diagram types, and domains within the existing corpus, and
then an authorized external context under Plan B). The healthcare extension is explicitly
conditional — "when governance and access permit" is part of the question's wording because
the medical instantiation is gated by use-case, personnel, authorization, ethics/privacy,
environment, and protocol prerequisites that are institutional facts, not research variables.
The question remains fully answerable in software/modeling alone; healthcare tests its outer
boundary. Two guideline contexts raised in the 2026-08-05 discussion illustrate the distance
transfer must survive: a chronic-pain management guideline (Clalit) and an age-related macular
degeneration guideline (Soroka) share almost nothing at the domain level — which is exactly why a
domain-specific/transferable classification, rather than a blanket transfer claim, is the
scientifically defensible target.

**Retained language note.** The word "transparently" drew a noted mild reservation during the
2026-08-05 SQ3 discussion (`E10`); it currently appears in SQ2's wording and is retained,
together with the shared "without unsafe generalization or loss of human authority" clause,
pending the final wording sign-off — this relocation note is a derived interpretation, flagged
for the Aug-12 review.

## 3.6 The three questions as one research program

The questions compose a single lifecycle and a division of labor:

| | Asks | Produces | Hands over |
| --- | --- | --- | --- |
| SQ1 | *When* should the system ask an expert? | Intervention criteria and dosage/budget policies | Captured expert responses → SQ2 |
| SQ2 | *What* must be kept, and under what governance? | Judgment representation, validation/reconciliation, provenance, scope, authority controls | Governed, scoped judgments → SQ3 |
| SQ3 | *Where else* does a judgment hold, and how would we know? | Domain-specific vs. transferable classification; leakage-safe transfer evidence | Boundary conditions back to SQ1/SQ2 policies |

Each sub-question maps to exactly one primary study in the study contract (Study 1, 2, 3
respectively), keeping the one-question-one-study discipline the supervision team set on
2026-07-29 and reconfirmed on 2026-08-05. Answering all three yields the main question's
"captured, governed, and used"; failing any one of them localizes precisely which part of
reliable human-AI co-reasoning remains out of reach — which is itself a reportable result.

## 3.7 Relationship to the motivating case

VEGO-AI — a four-agent pipeline that operationalizes modeling guidelines and explores
variability in student-built domain models — is the motivating case and the initial
instantiation platform for this research. Its role in this chapter is evidential only: it
demonstrates that the gap is real in a concrete, instrumented setting (its pipeline emits
uncertainty signals and review flags but has no governed way to capture or reuse the expert
judgment those flags request). The research questions are not questions *about* VEGO-AI, and
Chapter 4's methodology treats it as one of two instantiation contexts rather than the object
of study. This separation — the question is the contribution, the platform is the vehicle — is
maintained deliberately throughout the proposal, following the supervision team's direction of
2026-08-05.

## 3.8 Scope boundaries for the questions

- **In scope:** selective intervention policy design; structured judgment representation with
  provenance, scope, conflict, and authority governance; scope-aware advisory reuse;
  domain-specific vs. transferable classification of uncertainty and judgments; leakage-safe
  transfer evaluation in software/modeling; a governance-gated healthcare extension.
- **Out of scope:** autonomous modification of the underlying assessment pipeline by reused
  judgment; any accuracy or effort-reduction claim ahead of the independent-label evidence
  gates; medical data processing before all six entry gates pass; and any claim that captured
  judgment is ground truth — captured judgment is governed evidence, contestable by design.

---

*Draft prepared 2026-08-10 against the canonical 2026-08-05 meeting record (E3–E13) for the
Aug 12 supervisor review. Wording provisional pending `A08-01` verification and logged
`D-RQ-01`/`D-RQ-02` decisions.*
