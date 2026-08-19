# Chapter 4 — Research Methodology

> Status: working draft, written 2026-08-15 after the 2026-08-12 supervisor call moved this
> chapter into active writing; revised 2026-08-19 per `chapter-4-completion-plan-2026-08-19.md` to
> deepen each artifact specification and resolve the one open item (Plan A placement, §4.2) that
> did not require new supervisor authority. Each sub-question gets one recommended artifact so the
> chapter is actually reviewable, but a recommendation is not a supervisor-confirmed decision —
> §4.7's remaining items are packaged as `2026-08-19-chapter4-decisions-packet.md` for Iris and
> Arnon, and are not resolved on this chapter's own authority. This revision runs ahead of Iris's
> 2026-08-12 sequencing instruction that methodology work start only once the literature review is
> judged done; Ali made that call explicitly, and it does not change what claims this chapter is
> licensed to make. Chapter 2 (literature review) is being produced on a separate, parallel
> verification track and is out of scope here; the only sources cited below are this chapter's own
> methodological framework, not the substantive related-work literature.

---

## 4.1 Methodological stance

This programme follows design science research. The object of study is an artifact — a governed
mechanism for capturing and reusing human judgment inside an agentic assessment pipeline — not a
phenomenon to observe from the outside. The umbrella question and each sub-question in Chapter 3
are already phrased as design problems paired with a knowledge question, which is the split
Wieringa's engineering cycle is built around.

Two references anchor the chapter, and they do different work. Peffers, Tuunanen, Rothenberger and
Chatterjee (2007), *A Design Science Research Methodology for Information Systems Research*, JMIS
24(3), pp. 45-77 (DOI 10.2753/MIS0742-1222240302), gives the six-activity process — problem
identification and motivation, definition of objectives, design and development, demonstration,
evaluation, communication — and licenses treating each sub-question as its own DSRM iteration
rather than one pass repeated three times. Wieringa (2014), *Design Science Methodology for
Information Systems and Software Engineering*, Springer (DOI 10.1007/978-3-662-43839-8), gives the
vocabulary the rest of this chapter actually uses: the engineering cycle (problem investigation,
treatment design, treatment validation, treatment implementation, implementation evaluation)
nested inside the design cycle, the separation between a design problem and a knowledge question,
and the artifact-in-context framing every transfer claim in Study 3 depends on. Wieringa fits the
day-to-day writing better because it speaks this thesis's own language — UML domain models, a
MODELS-published foundation artifact, a software-engineering audience — while Peffers gives the
six-activity skeleton a committee will recognize on sight.

Each sub-question below gets the same treatment: what needs to be designed, what needs to be
known, and what artifact and evaluation would answer both. Chapter 3 separates the gap from the
questions; this chapter separates the questions from how they get answered.

## 4.2 Two evaluation contexts

Per the 2026-08-12 call, every study is tested in two guideline-operationalization scenarios: a
software-engineering context (student UML domain models assessed against modeling guidelines, the
setting of the group's own MODELS 2026 foundation work) and a medical context (clinical records
assessed against care guidelines). The two are not symmetric at proposal stage.

The software-engineering context is the baseline. The VEGO-AI pipeline already runs on it, the
27-pattern offline evidence and the EXP-006 through EXP-008 replay series already exist, and the
24 EXP-005 candidate rows come from it. Every sub-question can be answered here alone. The medical
context is a conditional extension, gated by the six Plan A entry gates (`G1`-`G6`) recorded in
`three-study-contract.md`, currently at 0 of 6. A 2026-08-26 internal checkpoint follows; after it,
Plan B — a second authorized software/modeling context — becomes the committed path for any gate
without an owner, evidence path, and feasible date. Nothing below assumes Plan A activates; each
study states what it does under Plan B alone and what changes if Plan A clears its gates.

Where the scenario framing itself belongs structurally is resolved as of this pass: each study
below (§4.3-§4.5) is written Plan-B-first, describing the software-engineering-only version of the
study as a complete, self-standing account. The medical extension for each study is then stated as
a conditional appendix to that account — what changes if Plan A's six gates clear — rather than
developed as a parallel, equally-weighted track. This follows directly from §4.2's own asymmetry:
Plan B can answer every sub-question alone today, while Plan A remains gated at 0 of 6 with a
2026-08-26 checkpoint that defaults to Plan B if any gate lacks an owner, evidence path, and
feasible date. Writing two symmetric tracks would overstate how live Plan A currently is. This is
an editorial decision within normal methodological judgment, not a claim about medical readiness,
and it can be revisited without any evidence-boundary consequence if Plan A's gates clear.

## 4.3 Study 1 — Selective intervention (SQ1)

Study 1 needs a policy that decides when an agentic assessment system should route an uncertain or
important deviation to a human, under a bounded review budget, instead of reviewing everything or
nothing. The open empirical question is how much a given policy trades reviewer load against
coverage of the deviations that actually matter.

The recommended artifact is not the six-component reference architecture that
`three-study-contract.md`'s Study 1 row currently names — it is a smaller attention-budget
cost/coverage model: an analytical relation between a trigger configuration and (i) expected
reviewer load and (ii) coverage of uncertainty-marked events. `sections-2-and-4-thinking-notes.md`
(option A2) sets out why: an architecture reads as an engineering deliverable unless one
generalizable claim sits on top of it, and bundling six components together (listener catalog,
eligibility criteria, dosage policy, routing contract, timeout rules, burden budget) obscures which
one that claim actually is. Under the cost/coverage framing, those same components become
instantiations inside the model's parameter space rather than the contribution itself — the four
dosage modes already replayed offline (`every_decision`, `threshold`, `first_n_then_auto`,
`silent`) are four points in that space, not the artifact.

Validating the model means inspecting its properties analytically — monotonicity, boundary
behavior, degenerate cases — against the offline replay evidence that already exists: EXP-006's
event reconstruction, EXP-007's per-mode load-versus-coverage counts, EXP-008's
unstable-but-never-reviewed trigger candidates. All of it is reported as observability and
mechanism evidence, never as an effort-reduction result. EXP-007's routed-item counts describe a
property of an offline replay, and `three-study-contract.md`'s own excluded-measures row already
rules out reading them as expert-effort reduction. No claim of optimal dosage, accuracy
improvement, or workload reduction follows from architecture, tests, or fixtures alone.

**Model specification.** Each assessment event `e` carries a trigger score `s(e)` in `[0,1]`, a
composite of the uncertainty, consequence, disagreement, and evidence-weakness signals the
existing pipeline already computes per event, produced identically regardless of which dosage mode
is active. A trigger configuration `θ` is a decision rule over `s(e)` that selects which events get
escalated to a human reviewer. The four already-replayed modes are four such rules, not four
architectures: `every_decision` escalates all events (no free parameter); `threshold(τ)` escalates
events with `s(e) ≥ τ`; `first_n_then_auto(N)` escalates the top-`N` events per window ranked by
`s(e)` and auto-resolves the rest; `silent(p)` escalates nothing for review and only samples at
rate `p` for audit. Two output quantities follow for any `θ`: `Load(θ)`, the expected number of
events routed to a reviewer per window (directly readable from EXP-007's per-mode routed-item
counts), and `Coverage(θ)`, the fraction of independently uncertainty-marked events that are
actually escalated under `θ` (readable against EXP-006's reconstructed events and EXP-008's
unstable-but-never-reviewed candidates). The model's claim is the `Load`-`Coverage` relation as `θ`
sweeps its parameter — a load/coverage frontier, with the four replayed modes as four sampled
points on or near it, not four separate contributions. The properties this chapter proposes to
inspect analytically follow directly: monotonicity (`Coverage` should not decrease as `Load`
increases along a single-parameter sweep — a configuration that raises load without raising
coverage is dominated and should be identifiable as such); boundary behavior (`every_decision`
should sit at the maximal-`Load`, `Coverage = 1` corner, and `silent(p=0)` at the minimal-`Load`
corner); and degenerate-case collapse (`first_n_then_auto(N=0)` and `threshold(τ→1)` should both
reduce to `silent`; `threshold(τ=0)` should reduce to `every_decision`). None of this requires new
data collection — it is a lens applied to the EXP-006/007/008 evidence that already exists, and a
configuration that fails the monotonicity or boundary checks against that evidence would be a
concrete falsification of the model as specified, not just a disappointing result.

Study 1 is the least gate-blocked of the three — it needs no EXP-005 labels, since it evaluates the
instrument's properties rather than assessment quality. What it still needs is the RQ/SQ wording
sign-off (`D-RQ-01`/`D-RQ-02`) and, eventually, `QL-01`/`QL-04` execution to ground the eligibility
and dosage requirements in prior work, though neither blocks building the model itself. If dosage
effects can't be measured empirically in time, the existing fallback in `three-study-contract.md`
holds: report the inspectable model, the analytical burden relation, and the preregistered
empirical test, with effectiveness claims left out.

## 4.4 Study 2 — Governed knowledge reuse (SQ2)

Study 2 needs a record format and a validation/authority regime for captured expert judgment, one
that lets it be reused across cases without unsafe generalization or loss of human authority. The
knowledge question is whether an independent implementation of that record format actually
conforms to it, including on cases built specifically to break it.

The recommended artifact is a normative judgment-record contract — a system-independent
specification of what a reusable judgment record must carry (case grounding, the system's own
reasoning as the expert actually saw it, the expert's rationale, scope, authority, provenance
chain, validity and expiry) — paired with an executable conformance suite that any implementation
can be run against. VEGO-AI becomes reference implementation one; the contribution is the contract
and the test that decides conformance, not a description of VEGO-AI's own schemas.
`sections-2-and-4-thinking-notes.md` (option B2) argues for this over the bundled nine-component
lifecycle that the contract's Study 2 row currently names, because an "everything" artifact invites
reviewers to dispute its boundary, and because the H-Verify/convergence half of that bundle rests
on EXP-009 and EXP-010, which the experiment plan labels provisional synthetic fixtures gated on
`M-04` protocol approval — evidence that can't yet stand in for how real expert judgment is
actually handled.

**Contract specification.** The seven field groups already named above expand to a concrete
minimum record: case grounding (artifact identifier, fragment/pattern identifier, guideline
identifier and version, domain, language, task type, evidence locator into the source artifact,
and the observed deviation); the system's reasoning exactly as the expert saw it at judgment time
(the system's claim, its confidence, and the decision trace actually surfaced to the reviewer, not
one reconstructed afterward); the expert's rationale (verdict, structured or free-text
justification, any counter-evidence cited, the expert's own stated uncertainty); scope (the
claim-specific boundary this judgment is authorized to speak to, stated narrowly enough that it
does not silently cover cases it was never evaluated against); authority (reviewer identity and
role, authorization level, and whether the judgment may bind later automated decisions or is
advisory-only); provenance (who or what created, modified, or superseded the record, with
timestamps and a pointer to any prior version); and a lifecycle state drawn from a fixed set —
`Draft`, `Active`, `Contested`, `Superseded`, `Expired`, `Revoked` — each with the condition that
triggers it and, for `Revoked`, a required reason. The conformance suite that tests any
implementation against this contract has three parts: a reconstructability test, where a second
reviewer blind to the original judgment must be able to state, from the record alone, what claim
was judged, why, and under what scope; a discrimination test, where at least one deliberately
non-conforming variant (for example, one that omits the scope field or never transitions out of
`Draft`) must fail the suite for the specific, named reason it violates; and a completeness review
of the specification itself by the independent implementer named in §4.7, checking for fields that
prove ambiguous or missing against a real case. Validation here means conformance testing: the
reference implementation passes, at least one deliberately non-conforming variant fails for a
named reason, and the specification itself gets reviewed for completeness and ambiguity. The existing architecture-conformance series (EXP-013
through EXP-018 — schema, lineage, explicit-gap, determinism, isolation, non-application checks) is
offline fixture evidence of the same shape this artifact would generalize, reported at that scope
only; it grants no runtime authority claim.

This artifact needs no EXP-005 labels and can be built now, which is its main advantage over the
bundled alternative. What it lacks is a person: demonstrating implementation-independence needs a
second, independent implementer or reviewer to run the conformance suite against a variant they
build themselves, and nobody is named for that role anywhere in the tracked record. That gap
carries into §4.7 rather than getting assumed away. Without an independent implementer before
submission, the fallback is to report contract and conformance-suite validation against the
reference implementation only, state the implementation-independence gap outright, and make no
claim that governed reuse improves outcomes or generalizes safely.

## 4.5 Study 3 — Evaluation and transfer (SQ3)

Study 3 needs a procedure that decides, given a judgment record and a described target context,
whether that judgment is eligible for reuse, eligible with a stated adaptation, or blocked, with a
reason recorded either way. The knowledge question is whether independent raters apply that
procedure reliably, and what the resulting spread of verdicts says about which parts of governed
judgment travel across contexts and which stay domain-specific.

The recommended artifact is a transfer-eligibility decision procedure paired with a target-context
descriptor schema. `sections-2-and-4-thinking-notes.md` (option C2) sharpens what would otherwise
be a taxonomy question into a decidable instrument, pulling forward the "domain contract" that
`three-study-contract.md`'s Plan B row already treats as mandatory readiness evidence and making it
the designed artifact rather than an output of running the study. This is preferred over the
bundled ten-item evaluation-and-transfer package the contract currently names, because at least six
of those ten items are outputs of running the study rather than artifacts designed by it, and
because the package's evidential half can't be produced at all while EXP-005 sits at 0 of 24 —
calling it "the artifact" at proposal stage would risk implying an evaluation already exists.

**Procedure specification.** The procedure takes two inputs — a source judgment record in the
§4.4 contract, with its scope field, and a target-context descriptor stating the candidate case's
domain, task type, guideline family and version, institution or population, and time elapsed since
the source judgment — and runs three checks in a fixed order. A relevance check first asks whether
the target context matches the source record's scope on every dimension that scope names as
defining; any mismatch on a defining dimension routes straight to `Blocked`, reason "out of
scope," without evaluating the remaining checks. An applicability check then measures distance on
the non-defining dimensions (institution, population, elapsed time, guideline-version delta); a
distance within the stated tolerance on every dimension yields `Eligible`, a distance beyond
tolerance on one or more dimensions but within a named adaptation's reach yields `Eligible with
adaptation`, naming that adaptation (for example, "requires local-reviewer re-confirmation" or
"requires a guideline-version delta review"), and a distance beyond any defined adaptation yields
`Blocked`, reason "context distance exceeds adaptation capacity." An authorization check runs
independently of the first two: if the requesting context lacks the authorization level the source
record's authority field requires, the verdict is `Blocked`, reason "insufficient authorization,"
regardless of how relevant or applicable the judgment otherwise is. Every verdict — `Eligible`,
`Eligible with adaptation`, or `Blocked` — carries the specific reason and the specific dimension
that drove it, which is what makes rater agreement checkable at two levels: whether two raters
reach the same verdict, and whether they cite the same driving dimension for it. Validation targets
the procedure's reliability, not assessment accuracy. Two trained raters apply
it independently to the same set of existing judgment records and context descriptors, and the
study reports inter-rater agreement, undecidable cases, and the spread of blocking reasons. It is
one of the few Study 3 paths that needs no expert gold labels at all — it still needs two raters,
so it is gold-label-free rather than label-free, and that distinction should stay attached wherever
the result is reported. Agreement on applying the procedure is evidence about the instrument, not
evidence that its verdicts are correct, and the two should not be conflated.

Whether instrument-reliability evidence like this is admissible as a Study 3 result ahead of the
EXP-005 gate, or whether every Study 3 evaluation has to wait for at least 20 generalization-safe
adjudicated labels, is Part 3 item 9 of `sections-2-and-4-thinking-notes.md`. This chapter does not
resolve it; it is a ruling the programme needs from Iris and Arnon, carried forward in §4.7. Two
raters also are not named yet, the same resourcing gap Study 2 has for its independent implementer.
If EXP-005 stays at 0 of 24 and no raters are secured, the existing fallback in
`three-study-contract.md` applies: report the exact block and accept readiness-only evidence. Any
healthcare instantiation of Study 3 stays blocked independently at 0 of 6 medical entry gates
regardless of the raters question.

## 4.6 Evidence boundary for this chapter

None of the methods above claim more than they can support. Nothing here asserts accuracy
improvement, generalization, effort reduction, or clinical performance. The same three gates bound
what any of these studies can report today: EXP-005 holds 0 of 24 required generalization-safe
expert labels, medical entry gates `G1`-`G6` stand at 0 of 6, and the frozen literature searches
`QL-01`-`QL-05` are protocol-ready but not executed. The offline replay series (EXP-006, EXP-007,
EXP-008) and the architecture-conformance series (EXP-013 through EXP-018) are real, already-run
evidence, but each is reported only at the scope its own experiment plan assigns it — mechanism,
observability, or conformance, never quality, accuracy, or effort.

## 4.7 Open decisions carried forward, not resolved by this draft

Recommending an artifact for each sub-question makes this chapter reviewable, but a recommendation
is not a decision. `chapter-4-completion-plan-2026-08-19.md` sorts the items below by what kind of
resolution each one actually needs; the disposition noted per item reflects that pass, not a claim
that the underlying question is settled.

- Artifact granularity and abstraction level: confirm or correct the three recommendations above
  (§4.3 cost/coverage model, §4.4 contract-plus-conformance-suite, §4.5 eligibility procedure) —
  Part 3 items 6 and 7. **Still a supervisor decision** — packaged as Item 1 in
  `2026-08-19-chapter4-decisions-packet.md`.
- The SQ2/SQ3 boundary: `reuse_scope` lives on the judgment record in Study 2, while the
  domain-specific-versus-transferable classification is the analytic core of Study 3 — confirm
  these do not ship the same artifact twice (Part 3 item 8). **Still a supervisor decision** —
  packaged as Item 2 in the same packet.
- Instrument-reliability admissibility ahead of EXP-005, for both Study 2's conformance evidence
  and Study 3's rater-agreement evidence (Part 3 item 9). **Still a supervisor decision** —
  packaged as Item 3 in the same packet.
- Whether the offline replay series (EXP-006/007/008) may appear as preliminary results in this
  chapter, and with exactly what wording for EXP-007 (Part 3 item 10). **Already has a working
  answer in practice**: `chapter-5-preliminary-results.md` reports all three under exactly this
  framing. What remains is supervisor confirmation that the existing wording is acceptable, noted
  as a housekeeping item in the decisions packet rather than reopened from scratch.
- Whether EXP-009/EXP-010 appear at all before `M-04` protocol approval is recorded (Part 3 item
  11). **Still a supervisor decision** — packaged as Item 4 in the same packet.
- Plan A's presence in this chapter: conditional appendix, or developed in parallel with Plan B
  (Part 3 item 12, referenced in §4.2 above). **Resolved in this pass** — §4.2 now states
  Plan-B-first with Plan A as a conditional appendix per study, as an editorial decision that does
  not require new supervisor authority and can be revisited if Plan A's gates clear.
- Naming the people this chapter currently leaves as gaps: an independent implementer or reviewer
  for Study 2 (§4.4), and two raters for Study 3 (§4.5) — Part 3 item 13. **A real-world action,
  not something this chapter can resolve by writing** — see
  `docs/operations/study-resourcing-request-template.md`.
- When the instruction to move from thinking to writing formally lifts for this chapter, and who
  owns the first supervisor-facing revision against which of the options above (Part 3 item 14).
  **Superseded** — Ali chose to proceed with this completion pass on 2026-08-19 ahead of the
  literature-review gate closing, per `chapter-4-completion-plan-2026-08-19.md`.

Until the four still-open supervisor decisions above are worked through and logged in the
decision/change record, none of these three studies' claims — and none of this chapter's own text
— should be read as approved. Chapter 3 already holds itself to the same rule for its
research-question wording.
