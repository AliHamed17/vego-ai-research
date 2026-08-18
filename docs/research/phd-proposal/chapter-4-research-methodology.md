# Chapter 4 — Research Methodology

> Status: working draft, produced 2026-08-15 in response to the 2026-08-12 supervisor call's
> instruction to move the methodology chapter into active writing. Recommends one concrete artifact
> per sub-question so the chapter is reviewable, but every such choice is a recommendation, not a
> supervisor-confirmed decision — see the open-decisions section at the end, which carries forward
> the questions from `sections-2-and-4-thinking-notes.md` that this draft did not resolve on its own
> authority. Chapter 2 (literature review) is being produced on a separate, parallel verification
> track and is out of scope here; this chapter cites only its own methodological framework, not the
> substantive related-work literature.

---

## 4.1 Methodological stance

This programme follows design science research (DSR), for two converging reasons rather than one
default choice. First, the object of study is an *artifact* — a governed mechanism for capturing
and reusing human judgment inside an agentic assessment pipeline — not a naturally occurring
phenomenon to be observed. Second, both the umbrella question and each sub-question in Chapter 3
are stated as design problems with an attached knowledge question, which is exactly the split
Wieringa's engineering cycle is built around.

Two DSR references anchor the chapter, each doing different work. Peffers, Tuunanen, Rothenberger
and Chatterjee (2007), *A Design Science Research Methodology for Information Systems Research*,
JMIS 24(3), pp. 45-77 (DOI 10.2753/MIS0742-1222240302), supplies the six-activity process — problem
identification and motivation, definition of objectives, design and development, demonstration,
evaluation, and communication — and licenses treating each sub-question as one DSRM iteration
rather than a single pass repeated three times. Wieringa (2014), *Design Science Methodology for
Information Systems and Software Engineering*, Springer (DOI 10.1007/978-3-662-43839-8), supplies
the vocabulary this chapter actually writes in: the engineering cycle (problem investigation,
treatment design, treatment validation, treatment implementation, implementation evaluation) nested
inside the design cycle, the hard separation between a *design problem* and a *knowledge question*,
and the *artifact-in-context* framing that governs every transfer claim in Study 3. Wieringa is the
better fit for the day-to-day writing because it speaks the language this thesis already uses — UML
domain models, a MODELS-published foundation artifact, a software-engineering audience — while
Peffers gives the six-activity skeleton a committee will recognise on sight.

Per sub-question, this chapter therefore states the design problem, the paired knowledge question,
the artifact that instantiates the treatment, and the validation model, rather than one combined
"methodology" narrative. This mirrors how Chapter 3 already separates the gap from the questions:
methodology fixes *how* each question will be answered, not *what* the answer is.

## 4.2 Two evaluation contexts

Per the 2026-08-12 call, every study is tested in two kinds of guideline-operationalization
scenario, not one: a software-engineering context (student UML domain models assessed against
modeling guidelines, the setting of the group's own MODELS 2026 foundation work) and a medical
context (clinical records assessed against care guidelines). The two contexts are not symmetric at
proposal stage, and this chapter states that difference plainly rather than papering over it.

The software-engineering context is the baseline: the VEGO-AI pipeline already runs on it, the
27-pattern offline evidence and the EXP-006 through EXP-008 replay series already exist, and the
24 EXP-005 generalization-safe candidate rows are drawn from it. Every sub-question is designed to
be fully answerable here alone. The medical context is a conditional extension, gated by the six
Plan A entry gates (`G1`-`G6`) recorded in `three-study-contract.md`, currently at 0 of 6, with a
2026-08-26 internal checkpoint after which Plan B (a second authorized software/modeling context)
becomes the committed path for any gate without an owner, evidence path, and feasible date. Nothing
in this chapter assumes Plan A activates; each study below states what it does under Plan B alone
and what changes if Plan A does clear its gates.

This chapter does not attempt to resolve where, structurally, the scenario framing itself is
discussed at length — Part 3, item 12 of `sections-2-and-4-thinking-notes.md` asks whether Plan A
should appear as a conditional appendix or be developed in parallel, and that remains an open
decision (§4.7 below), not something this draft settles by writing the sections in a particular
order.

## 4.3 Study 1 — Selective intervention (SQ1)

Design problem: design a policy that decides when an agentic assessment system should route an
uncertain or important deviation to a human, under a bounded review budget, rather than reviewing
everything or nothing. Knowledge question: to what extent does a given policy trade reviewer load
against coverage of the deviations that matter.

Recommended artifact: an explicit attention-budget cost/coverage model — a small analytical
relation between a trigger configuration and (i) expected reviewer load and (ii) coverage of
uncertainty-marked events — rather than the bundled six-component reference architecture that
`three-study-contract.md`'s Study 1 row currently names as one artifact. `sections-2-and-4-thinking-
notes.md` (option A2) sets out the reasoning: an architecture reads as an engineering deliverable
unless one generalizable claim sits explicitly on top of it, and bundling six components (listener
catalog, eligibility criteria, dosage policy, routing contract, timeout rules, burden budget) hides
which one is that claim. The cost/coverage model keeps the same components as instantiations inside
its parameter space instead of as the contribution itself — the four dosage modes already replayed
offline (`every_decision`, `threshold`, `first_n_then_auto`, `silent`) become four points in that
space, not the artifact.

Validation model: analytical inspection of the model's properties (monotonicity, boundary
behaviour, degenerate cases), instantiated by the existing offline replay evidence — EXP-006's
event reconstruction, EXP-007's per-mode load-versus-coverage counts, EXP-008's unstable-but-never-
reviewed trigger candidates — reported strictly as observability and mechanism evidence, never as
an effort-reduction result. This is a hard, explicit boundary: EXP-007's routed-item counts describe
a property of an offline replay, and `three-study-contract.md`'s own excluded-measures row already
forbids reading them as expert-effort reduction. No claim of optimal dosage, accuracy improvement,
or workload reduction is made from architecture, tests, or fixtures alone.

Dependency and fallback: this is the least gate-blocked of the three studies — it needs no EXP-005
labels, because it evaluates the instrument's properties, not assessment quality. It still depends
on the RQ/SQ wording sign-off (`D-RQ-01`/`D-RQ-02`) and, later, on `QL-01`/`QL-04` execution to
ground the eligibility and dosage requirements in prior work; neither blocks constructing the model
itself. If dosage effects cannot yet be measured empirically, the fallback already recorded in
`three-study-contract.md` applies: report the inspectable model, the analytical burden relation, and
the preregistered empirical test, with effectiveness claims excluded.

## 4.4 Study 2 — Governed knowledge reuse (SQ2)

Design problem: design a record format and a validation/authority regime for captured expert
judgment such that it can be reused across cases without unsafe generalization or loss of human
authority. Knowledge question: does an independent implementation of that record format actually
conform to it, and does conformance behave correctly on cases designed to break it.

Recommended artifact: a normative judgment-record contract — a system-independent specification of
what a reusable judgment record must carry (case grounding, the system's own reasoning as the
expert actually saw it, the expert's rationale, scope, authority, provenance chain, validity and
expiry) — paired with an executable conformance suite any implementation can be run against.
VEGO-AI becomes reference implementation one; the contribution is the contract plus the test that
decides conformance, not a description of VEGO-AI's own schemas. `sections-2-and-4-thinking-
notes.md` (option B2) is explicit about why this is preferred over the bundled nine-component
lifecycle the contract's Study 2 row currently names: an "everything" artifact invites reviewers to
contest its boundary, and the H-Verify/convergence half of that bundle currently rests on EXP-009
and EXP-010, which the experiment plan labels provisional synthetic fixtures gated on `M-04`
protocol approval — evidence that cannot yet stand in for real expert-judgment handling.

Validation model: conformance evaluation. The reference implementation is shown to pass; at least
one deliberately non-conforming variant is shown to fail, for a named reason; and the specification
itself is reviewed for completeness and ambiguity. The existing architecture-conformance series
(EXP-013 through EXP-018 — schema, lineage, explicit-gap, determinism, isolation, and
non-application checks) is offline fixture evidence of the same shape this artifact would
generalize, and is reported at that scope only: it grants no runtime authority claim.

Dependency and fallback: this artifact needs no EXP-005 labels and is buildable now, which is its
main attraction relative to the bundled alternative. It has one real, unresolved resourcing gap:
demonstrating implementation-independence needs a second, independent implementer or reviewer to
run the conformance suite against a variant they build, and no such person is named anywhere in the
tracked record — this is carried into §4.7 as an open question, not assumed away. If no independent
implementer is available before submission, the fallback is to report contract and conformance-
suite validation against the reference implementation only, state the implementation-independence
gap explicitly, and exclude any claim that governed reuse improves outcomes or generalizes safely.

## 4.5 Study 3 — Evaluation and transfer (SQ3)

Design problem: design a procedure that decides, for a given judgment record and a described
target context, whether that judgment is eligible for reuse, eligible with a stated adaptation, or
blocked, with a recorded reason. Knowledge question: is that procedure applied reliably by
independent raters, and what does the distribution of its verdicts reveal about which components of
governed judgment travel across contexts and which stay domain-specific.

Recommended artifact: a transfer-eligibility decision procedure plus a target-context descriptor
schema — sharpening what `sections-2-and-4-thinking-notes.md` (option C2) calls the taxonomy
question into a decidable instrument, and pulling forward the `three-study-contract.md` Plan B
"domain contract" as the designed part rather than an output of running the study. This is chosen
over the bundled ten-item evaluation-and-transfer package the contract currently names, because at
least six of those ten items are outputs of *running* the study, not artifacts *designed* by it, and
because the package's evidential half cannot be produced at all while EXP-005 sits at 0 of 24 —
presenting it as "the artifact" at proposal stage would risk implying an evaluation already exists.

Validation model: reliability of the procedure itself, not of assessment accuracy. Two trained
raters independently apply the procedure to the same set of existing judgment records and context
descriptors; the study reports inter-rater agreement, undecidable cases, and the distribution of
blocking reasons. This is deliberately one of the few Study 3 evaluation paths that needs no expert
gold labels — it still needs two raters, so it is gold-label-free, not label-free, and that
distinction is stated wherever this result is reported. Agreement on *applying* the procedure is
evidence about the instrument; it is explicitly not evidence that the procedure's verdicts are
correct, and this chapter does not conflate the two.

Dependency and fallback: whether instrument-reliability evidence of this kind is admissible as a
Study 3 result ahead of the EXP-005 gate, or whether every Study 3 evaluation must wait for at least
20 generalization-safe adjudicated labels, is Part 3 item 9 of `sections-2-and-4-thinking-
notes.md` and is not resolved by this chapter — it is carried forward in §4.7 as a ruling this
programme needs from Iris and Arnon. Two raters are also not yet named, mirroring the same
resourcing gap Study 2 has for an independent implementer. If EXP-005 remains at 0 of 24 and no
raters are secured, the fallback already in `three-study-contract.md` applies: report the exact
block and accept readiness-only evidence; any healthcare instantiation of Study 3 remains blocked
independently at 0 of 6 medical entry gates regardless of the raters question.

## 4.6 Evidence boundary for this chapter

Every method above is licensed to run now or is explicitly marked as gated. Nothing in this chapter
claims accuracy improvement, generalization, effort reduction, or clinical performance. The three
gates that bound what any of these studies may report today are unchanged by this chapter: EXP-005
holds 0 of 24 required generalization-safe expert labels; medical entry gates `G1`-`G6` stand at 0
of 6; and the frozen literature searches `QL-01`-`QL-05` are protocol-ready but not executed. The
offline replay series (EXP-006, EXP-007, EXP-008) and the architecture-conformance series (EXP-013
through EXP-018) are real, already-run evidence, but each is reported strictly at the scope its own
experiment plan assigns it — mechanism, observability, or conformance, never quality, accuracy, or
effort.

## 4.7 Open decisions carried forward, not resolved by this draft

This chapter makes a recommendation per sub-question so it can be read and reacted to, but it does
not have the standing to close the following, all inherited from `sections-2-and-4-thinking-
notes.md` Part 3 and unresolved by the 2026-08-12 call:

- Artifact granularity and abstraction level: confirm or correct the three recommendations above
  (§4.3 cost/coverage model, §4.4 contract-plus-conformance-suite, §4.5 eligibility procedure) —
  Part 3 items 6 and 7.
- The SQ2/SQ3 boundary: `reuse_scope` lives on the judgment record in Study 2, while the
  domain-specific-versus-transferable classification is the analytic core of Study 3 — confirm
  these do not ship the same artifact twice (Part 3 item 8).
- Instrument-reliability admissibility ahead of EXP-005, for both Study 2's conformance evidence and
  Study 3's rater-agreement evidence (Part 3 item 9).
- Whether the offline replay series (EXP-006/007/008) may appear as preliminary results in this
  chapter, and with exactly what wording for EXP-007 (Part 3 item 10).
- Whether EXP-009/EXP-010 appear at all before `M-04` protocol approval is recorded (Part 3 item
  11).
- Plan A's presence in this chapter: conditional appendix or developed in parallel with Plan B
  (Part 3 item 12, referenced in §4.2 above).
- Naming the people this chapter currently leaves as gaps: an independent implementer or reviewer
  for Study 2 (§4.4), and two raters for Study 3 (§4.5) — Part 3 item 13.
- When the instruction to move from thinking to writing formally lifts for this chapter, and who
  owns the first supervisor-facing revision against which of the options above (Part 3 item 14).

None of these six studies' claims, and none of this chapter's own text, should be read as
supervisor-approved until these are worked through and logged in the decision/change record, the
same discipline Chapter 3 already applies to its own research-question wording.
