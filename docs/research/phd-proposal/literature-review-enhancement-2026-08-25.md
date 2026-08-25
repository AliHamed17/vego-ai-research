# Literature Review — Enhancement Package (2026-08-25)

Paste-ready enhancements for the literature review, derived from the verified findings in
`doctoral-proposal-2026-08-23-strict-review.md` and re-grounded in Iris's actual 2026-08-12
instructions as recorded in `docs/research/meetings/2026-08-12-supervisor-meeting.md`.

## Which document does this apply to?

There is **no editable source in this repository, or in Downloads, for either** the
2026-08-23 doctoral proposal (whose Chapter 2 is the literature review reviewed here) **or**
Literature Review v17. Both exist only as PDFs. The newest editable literature-review source
is `VEGO_AI_Literature_Review_v13_45_Page_Visual_Repaired_2026-08-19.docx`, which is four
versions behind the current content.

This package is therefore written as **located, self-contained replacement text** rather than
as an edit to a specific file, so it can be applied to whichever document is authoritative.
Every item names the exact target location and quotes the current text it replaces.

## Correction to the earlier review before applying anything

One instruction in the strict review was **wrong and must not be applied**. It asked for the
two-scenario (software-engineering/medical) split to be repeated inside each of §§4.2-4.4.
The meeting record shows Iris asked for the opposite: the organizing principle is
*"human involvement in the context of agentic AI, with or without the specific scenarios this
project studies. **Domain-independent**"*, and *"a separate section may cover the scenarios -
guideline operationalization - and **there** the software-engineering and medical contexts are
discussed."* Repeating the split per sub-question would contradict the domain-independence she
asked for. Item 2 below replaces that recommendation with what she actually directed.

## Item 1 — Remove the solution-world bleed (2 sentences, 3 captions)

Iris: the gap must live *"in the problem world, not the solution world."* Chapter 2 currently
names the candidate's own studies five times and twice issues design orders to them. The
chapter already contains the correct pattern, so the fix is to make the two offenders match it.

**Model to copy — the correct pattern, already in §2.2 (p.7):**

> Research implication. *The residual question is whether* these signals can be coupled for
> claim-level variability assessment and evaluated at a controlled attention budget.

**1a. §2.3 (p.8) — replace:**

> Research implication. **Study 2 must test whether** their joint expression as a claim-specific
> judgment contract improves reconstruction and governance enough to justify the additional
> capture burden.

**with:**

> Research implication. The residual question is whether reasoning-level correction, provenance,
> documentation, disagreement handling, contestability and lifecycle control — each established
> separately — can be expressed jointly as a claim-specific judgment record, and whether the
> resulting reconstruction and governance gain is large enough to justify the capture burden it
> imposes. No existing record type is reported to combine them at claim level.

**1b. §2.4 (p.9) — replace:**

> Research implication. **Study 3 must treat** prior judgment as attributed advice and require
> independent target evidence before describing a recurring issue as a transferable capability gap.

**with:**

> Research implication. The residual question is whether prior expert judgment can be carried into
> a new guideline-operationalization context as attributed advice rather than as a settled label,
> and on what independent target evidence a recurring issue may be reclassified from a local
> quirk to a transferable capability gap. The reviewed literature supplies similarity-based
> retrieval and distribution-shift diagnostics, but no reported procedure makes that distinction
> a governed decision.

**1c. Figures 5, 6, 7 (pp.7-9) — recaption or relocate.** Each is currently captioned
"Author-generated design synthesis" of the candidate's own Study 1/2/3 artifact, which places
proposed solutions inside the problem-world chapter. Two acceptable fixes:

- *Preferred* — move all three into Chapter 4 beside the study that owns each artifact
  (Figure 5 → §4.2, Figure 6 → §4.3, Figure 7 → §4.4). This also fixes the out-of-order
  numbering, because Figures 3 and 4 then precede them naturally.
- *Minimal* — keep them in place but recaption each as a synthesis of the **reviewed
  literature's** requirements rather than of a study design, and drop "Study N" from the caption:
  e.g. "Figure 5. Signals the reviewed intervention literature identifies, and the coupling it
  leaves unevaluated."

Do **not** apply the earlier recommendation to "move this content to Chapter 4 where the same
content is already stated." Chapters 2 and 4 share only 14 five-word sequences, nearly all page
boilerplate — there is no duplicate passage there to merge into.

## Item 2 — Add the two-scenario sub-section where Iris asked for it

Iris asked for *"a sub-section stating the work will be tested in two kinds of guideline
scenario: software-engineering/students, and medical"*, placed in the section covering the
scenarios. **§2.5 "Guideline operationalization, variability, and model assessment" is that
section, and it currently names neither scenario** — zero mentions of medical, clinical,
software engineering, student or healthcare anywhere in it.

The material is already there and merely unlabelled: §2.5 cites clinical computer-interpretable
guideline work at [34], [35] and student model-grading work at [38]-[40]. Add this as a closing
sub-section of §2.5, before its SECTION SUMMARY:

> **2.5.1 The two guideline-operationalization scenarios**
>
> The reviewed guideline literature divides into two scenario families that this research treats
> as its evaluation contexts. The first is **software-engineering and student modeling**, where
> guidelines act as assessment rubrics over domain models and the reviewed automated-grading and
> LLM-assisted-modeling work sits [38]-[46]; expert judgment here concerns modeling-language
> semantics, alternative-aware correctness, and instructional intent. The second is
> **medical guideline operationalization**, where the computer-interpretable guideline lineage
> reviewed above originates [32]-[35]; expert judgment here additionally carries institutional
> authority, patient-safety consequence, and formal adaptation procedure.
>
> Both are guideline-operationalization scenarios in the same sense: a narrative recommendation
> is turned into an assessable structure, and differences from it must be judged rather than
> merely counted. They differ in the consequence attached to a wrong judgment and in who holds
> the authority to make it, which is why the same governed-judgment mechanism must be examined in
> both rather than assumed to transfer. The software-engineering scenario is the complete baseline
> and is sufficient to answer all three sub-questions; the medical scenario is staged as an
> external-validity extension, entered only once its expertise, data, ethics, privacy,
> infrastructure and protocol preconditions are formally satisfied, and it is not on the critical
> path for doctoral completion.

That last sentence keeps the enhancement consistent with the Plan A/Plan B boundary and with
medical readiness standing at 0/6 gates, so it adds the sub-section Iris asked for without
promising a medical study that is not yet authorized.

## Item 3 — State the organizing principle in Iris's own words

**§1.3 (p.5) currently self-describes the review as organized** "by problem mechanisms rather
than by the names of proposed components." That is the right structure but not her phrase, so a
supervisor skimming for her instruction will not see it acknowledged. Replace with:

> The review is organized around **human involvement in the context of agentic AI**, treated
> domain-independently, rather than around the names of the proposed components or the venues in
> which the work appears. Guideline-operationalization scenarios are handled separately, in §2.5.
> Research-question tags are used only as an internal completeness check and do not drive the
> chapter structure.

This also records, in the text itself, the two things she asked to avoid — HCI as the frame, and
mirroring the sub-question structure.
## Item 4 — Citation fixes (verified 2026-08-25 against Crossref, DBLP, IEEE Xplore, PubMed)

All 57 references were externally verified: 54 exact, 0 unverifiable, 3 real defects. Each
defect was re-checked by an independent adjudicator instructed to refute it; none was overturned.

| Ref | Defect | Correction |
| --- | --- | --- |
| **[35]** Boxwala et al., GLIF3 | **Wrong journal.** Cited as *JAMIA*, vol. 11, no. 4, pp. 375-385 | Change venue to ***Journal of Biomedical Informatics*, vol. 37, no. 3, pp. 147-161**, 2004, doi `10.1016/j.jbi.2004.04.002`. Title, first author and year are already correct. Independent proof the cited locus cannot exist: JAMIA 11(4) spans pp. 235-338 |
| **[20]** Ancker et al. | Title truncated | Restore the dropped closing clause: "... on Alert Fatigue **in a Clinical Decision Support System**" (doi `10.1186/s12911-017-0430-8`) |
| **[27]** Santoni de Sio & van den Hoven | Subtitle omitted | Append the subtitle: "Meaningful Human Control over Autonomous Systems**: A Philosophical Account**" (doi `10.3389/frobt.2018.00015`) |

**Do not change [45].** An earlier review round claimed "K. E. Ahmed" should be "K. Ahmed."
That was wrong: DBLP's canonical author form is *Khaled E. Ahmed*, so the reference is correct
as written. The arXiv, ORCID and GitHub renderings simply omit the middle initial.

Formatting-only differences — stripped umlauts (Söllner → Sollner), "using" vs "Using", and
optional omitted DOIs — were explicitly judged non-defects and need no action.

## Item 5 — Carry the eight-signal requirement into the methodology

This one is a Chapter 4 edit, but it exists only because Chapter 2 raised the requirement, so
it belongs in this package.

§2.2 (p.7) states that a review policy *"must therefore combine uncertainty with consequence,
novelty, evidence quality, cross-agent disagreement, expected future value, reviewer competence,
and queue conditions."* §4.2 — where that policy is actually specified — says only that it
*"uses versioned signals rather than one opaque score"* and never enumerates them. Three of the
eight (**novelty, evidence quality, reviewer competence**) appear nowhere in Chapter 4 at all;
the others appear only in other roles (uncertainty as a comparator, expected future value as an
outcome measure, queue as infrastructure, consequence inside a hard rule).

In §4.2, after "The policy uses versioned signals rather than one opaque score", insert:

> The declared signal set is the one the reviewed literature identifies in §2.2: claim-level
> uncertainty, consequence of an unreviewed error, novelty relative to the judgment store,
> evidence quality, cross-agent disagreement within the pipeline, expected future reuse value,
> reviewer competence for the specific claim, and current queue conditions. Each is versioned and
> logged separately so that its contribution to a routing decision can be audited and ablated;
> P1 is tested against this declared set rather than against an unspecified score.

Without this, P1 ("the proposed policy improves important-case capture ... over simpler routing
policies") has no stated signal set to be tested against, and the requirement Chapter 2 derives
is never delivered.

## Item 6 — Restore the count caveat in §5.1

§5.1 (p.16) states flatly that the manuscript "reports evaluation across two domains, two UML
languages, and 178 case models [1]" and that "The Variability Explorer produced 26 reported
patterns." The competing figures from the evidence package — **165 case models and 27 patterns** —
appear nowhere in the document; "165" has zero occurrences. The v10 review called this an
unresolved reproducibility blocker and v13 still flagged it open, so dropping it silently is a
regression rather than a resolution.

Append to that paragraph:

> These counts are the manuscript's own reported figures. The companion evidence package
> independently reports 165 case models and 27 patterns for the same evidence state. The
> discrepancy is unresolved and is tracked as an open reproducibility item; neither figure is
> relied upon for any claim in this proposal.

## Item 7 — Structural model from the approved Haifa reference proposal

Reference: `PrivacyCompliant SW Reuse - Research Proposal_For submission (1).pdf`, a University of
Haifa submitted proposal (26 pages; the harness labels it 14, which is a metadata artifact).
Supplied by Ali as the model for how a literature review should be done here.

### The single biggest structural difference

**The reference proposal has no standalone literature-review chapter at all.** Its table of
contents runs: 1 Introduction · 2 Research Objectives, Questions and Contributions · 3 The
Research Methodology and Expected Research Artifacts · 4 Progress and Preliminary Results ·
5 Research Work Plan · 6 Challenges and Pitfalls · 7 References.

Literature is handled in three separate places, each doing a different job:

| Where | What it does | Size |
| --- | --- | --- |
| §1.1-1.2 (Introduction) | Narrative background that funnels from the broad problem to the specific gap | ~2.5 pages |
| §3.1 (Methodology) | The **systematic literature review as a research activity**, with a stated protocol | ~1 page |
| §4.1 (Progress) | Actual SLR results so far, with real counts | ~1.5 pages |

Ali's proposal instead carries a 5-page standalone Chapter 2 ("Critical Literature Review",
pp.6-10), and the literature is **not** one of his three studies. That is the structural
mismatch to fix.

### Pattern 1 — background subsections end with an explicit "To summarize" gap statement

Both reference background subsections close the same way: what is established, then what is
still open. Verbatim:

> §1.1: "To summarize, privacy gains an increasing interest in the last two decades and a variety
> of regulations, strategies and technologies have been proposed to address its different aspects.
> **However, their operationalization in software engineering practices is still challenging.**"

> §1.2: "To summarize, performing forward engineering activities in software development
> compliantly to privacy regulations has already been explored by different studies, [...]
> **achieving compliance in software reuse activities is still challenging.**"

This is the same job Ali's `SECTION SUMMARY (Established / Research implication)` device does —
and it **independently validates Item 1 above**. The reference never writes "Study 2 must test
whether…". It writes "X is still challenging." A problem-world gap statement, never a design
directive aimed at the author's own studies. Ali's device is arguably better structured; it just
needs its two offending instances rewritten to this standard.

### Pattern 2 — the review is a study with a citable protocol, stated in the proposal

§3.1 states the method in the proposal body, not in a side document:

> "will follow the guidelines for conducting SLRs by Kitchenham [29], [30], complemented by the
> guidelines on snowball sampling by Wohlin [31] and the guidelines for study selection in
> PRISMA2020 statement [32]."

…then lists the search concepts as explicit boolean groups (Concept 1 the examined aspect;
Concept 2 the examined process; Concept 3 the examined object; Concept 4 the examined phase),
each with the actual query terms and truncation wildcards.

**Ali already has all of this and it is invisible in the proposal.**
`docs/research/phd-proposal/literature-review-protocol.md` defines six source roles (ACM, IEEE,
Scopus, Web of Science, PubMed conditional, Google Scholar for snowballing only), a 2015-2026
window with a documented-snowballing exception for seminal work, five concept groups, and a
per-query audit record (database, exact query string, filters, date, returned/screened/included
counts, searcher). That is equal to or stronger than the reference's protocol. It simply is not
surfaced in the proposal document, and it cites no methodology authority.

**Action:** add a methodology subsection stating the review protocol in the proposal body, citing
Kitchenham, Wohlin and PRISMA 2020 as the reference does, and reproduce the five concept groups
with their actual query strings.

### Pattern 3 — the review's output is a named, evaluated artifact

> §3.1: "We further plan to consolidate the SLR results into a privacy compliant software
> development **taxonomy**. The taxonomy will be evaluated for **usefulness, robustness,
> conciseness and extensibility**, applying well known methods and measures [34]."

This is the most useful single insight for Ali, because it reframes the outstanding ACL-taxonomy
work. In the reference structure, a **taxonomy is what a literature review produces** — a research
artifact with named evaluation criteria, not a background chapter. So the ACL-2026
branch-classification exercise Iris asked for is not a side errand or a slide: **it is the
literature review's artifact**, and it belongs in the methodology as the review activity's
deliverable, evaluated against criteria of the same kind.

### Pattern 4 — progress is reported with real counts and a categorized result set

> §4.1: "a corpus of **55 papers** addressing both privacy and software reuse was established" —
> then the domains covered, the regulations encountered, and a five-category breakdown of what the
> corpus actually contains (Risk Analysis · Threat Detection · Requirements Elicitation ·
> (Re)Engineering · Rule & Policy Definition), each with citations.

Ali's §5 reports no literature-review progress at all. The honest current number is **zero
executed searches**: `literature-search-execution-register.md` marks QL-01 through QL-05
`PROTOCOL READY / NOT RUN` across all four databases, and `literature/per-rq-literature-map.md`
is explicitly "a working map […] not a completed review."

**Action, and it must stay honest:** add a literature-review progress subsection to §5 that
reports the real state — protocol frozen, five query lines defined across four databases, zero
executed, therefore no screening or inclusion counts yet — alongside the anchor-set work that
*has* been done. Do not report a corpus count until the searches are actually run. The reference
proposal earns its §4.1 by having done the work; the equivalent honesty here is to state the
protocol is ready and unexecuted.

### Recommended target structure for Ali's literature treatment

Two viable options; the second is the smaller change.

**Option A — follow the reference exactly.** Dissolve Chapter 2 into: Introduction background
subsections that funnel to the gap (domain-independent, per Iris), plus a review *activity* in
Chapter 4 with the protocol and the taxonomy artifact, plus a progress subsection in Chapter 5.
Closest to the approved reference and to Iris's "the review gives us the logic toward the gaps."

**Option B — keep Chapter 2, add what the reference has that it lacks.** Retain §§2.1-2.6 as the
problem-world funnel, apply Items 1-3 above, and additionally: state the protocol with Kitchenham
/Wohlin/PRISMA citations and the five concept groups; declare the ACL taxonomy classification as
the review's artifact with evaluation criteria; and add the honest progress subsection to §5.

Option B is recommended for the next revision, because it preserves the section summaries and the
already-strong evidence-boundary discipline while closing the four gaps the reference exposes.
Option A is the larger rewrite and is better timed after the QL-01-QL-05 searches have actually
been run, since that is what makes a reference-style §4.1 possible.

## Item 8 — The ACL-2026 taxonomy classification exercise (the deliverable missing four times)

This is the exercise Iris assigned on 2026-08-12, and the item absent from v13, workbook v8,
package v15 and the 2026-08-23 proposal. Per Item 7 it is not a side slide: in the reference
proposal's structure a taxonomy is **what a literature review produces**, so this is the review's
artifact.

Source of truth: Zou et al., "LLM-Based Human-Agent Collaboration and Interaction Systems: A
Survey," Findings of ACL 2026, pp. 36335-36364 (arXiv 2505.00753) - reference [10] in the
proposal. Branch and dimension names below were read from the survey PDF and its companion
repository `HenryPengZou/Awesome-Human-Agent-Collaboration-Interaction-Systems`, not from memory.

**Method note, and it matters.** Each branch was classified by one agent, then attacked by an
independent adversarial reviewer. The reviewers overturned part of **all four** first-pass
classifications, in every case by checking Ali's own implementation rather than reasoning
abstractly. The corrected verdicts below are the ones to use. The most important reversal: the
first pass claimed Corrective feedback was "deliberately excluded" from VEGO-AI. That is falsified
by `VEGO-AI/schemas/human_feedback.schema.json`, whose `guideline_update.action` enum is
`[none, add_alternative, edit_description, restrict_scope, reject_guideline, new_guideline]` - six
corrective actions, already implemented. Publishing the first pass would have contradicted his own
schema in front of the supervisor who assigned the exercise.

### 8.0 A citation correction this exercise exposed

**Section 2.1 (p.6) currently states** that the survey "organizes human-agent systems around human
feedback, interaction, orchestration, communication, **environment, and profiling** [10]" - six
categories. That is wrong on two counts. The survey's Section 3 opening reads: *"In this section,
we examine LLM-HAS through **five core aspects**: environment & profiling, human feedback,
interaction type, orchestration paradigm, and communication."* So (a) "environment & profiling" is
**one** conjoined component (Section 3.1), not two, and (b) the five core components are not the
classification taxonomy, which has **four** top-level branches (Sections 3.2-3.5) and deliberately
excludes environment & profiling because 3.1 is scene-setting rather than a classification axis.

Replace with:

> A broad survey of LLM-based human-agent systems describes five core components - environment and
> profiling, human feedback, interaction type, orchestration paradigm, and communication - of which
> the latter four form the top-level branches of its classification taxonomy [10].

### 8.1 Branch-level disposition

| Branch | Disposition | Owns | Why |
| --- | --- | --- | --- |
| **Human Feedback** (3.2) | **Relevant** - for SQ1 positioning and vocabulary | SQ1 | The only branch whose axes describe the human input itself rather than agent topology. Supplies the coordinate system for *when* a judgment is requested and *how coarse* it is. **Not** a design source for SQ2 or SQ3: it has no axis for validation, reconciliation, storage or reuse |
| **Interaction** (3.3) | **Less relevant** - premise, not variable | SQ1 (premise only); SQ2 for the authority clause | Locates the work as a move from Delegation toward governed Supervision, the unstated premise of SQ1 and of "without loss of human authority". But a four-value vocabulary about locus of control encodes nothing about representation, validation, reconciliation or storage. Not SQ3 at all |
| **Orchestration** (3.4) | **Less relevant** - positioning only | none | Both dimensions are pinned constants for this design (One-by-One, Asynchronous) and cannot discriminate between any two options he is choosing between. Useful for describing the system, useless as a design variable |
| **Communication** (3.5) | **Relevant** - but only one of its two dimensions | SQ2 (primary), SQ3 (dependent) | Communication Mode is where the contribution actually sits: the governed judgment record is a persistent shared artifact that later runs read. Communication Structure is inter-agent topology, fixed by the baseline |

### 8.2 Dimension-level disposition

| Dimension | Disposition | Notes that matter |
| --- | --- | --- |
| **Feedback Type** | **Relevant** | Evaluative (the verdict) and Guidance-as-critique (the rationale) are the two-part shape of every record. Corrective is in scope too — the `guideline_update` enum implements six corrective actions. Only *Implicit* is genuinely excluded, on governance grounds: an inferred preference cannot be attributed or held to account. Honest caveat: the survey's dominant Guidance value (63.9% of its corpus) means humans steering mid-run, whereas VEGO-AI's guidance is retrospective critique of a finished claim — the word is inherited, not the mechanism, and the chapter should say so |
| **Feedback Subtype** | **Relevant** (raised from less-relevant on challenge) | Three values map to fields already collected: Binary Assessment approximates his label, though his is *ternary* with an explicit abstain value the vocabulary cannot express; Critique maps to `expert_rationale`; Refinement maps to `guideline_update.proposed_text`. Scalar Rating mis-fits — the survey means scoring agent-output quality, his means reviewer certainty, which is an SQ1 trigger signal rather than a quality judgment. Preference Ranking is inapplicable: his instrument is absolute classification against a guideline, not pairwise comparison |
| **Feedback Granularity** | **Relevant — SQ1 only** | Per-pattern review is a deliberate Segment-level commitment, priced honestly at N judgements per run, with Holistic named as the rejected cheap alternative that yields nothing reusable. Do not claim this axis carries SQ3's transfer distinction — in his own design that is carried by implemented fields (`reuse_scope.applies_to_future_models`, `reuse_scope.limitations`), not by granularity |
| **Feedback Phase** | **Relevant** | Literally SQ1's "when". Current state is Post Task, whose own survey caveat ("no impact on completed task") states the present limitation exactly. During Task is the target and must be stated as a hypothesis, not an achieved position. Initial Setup is in scope, not out: `selective_intervention_policy.py` carries `guideline_update_proposed` as a trigger, i.e. rubric-level judgment requests |
| **Interaction Types** | **Not relevant** | Constant at Collaboration. Competition and Coopetition presuppose misaligned payoffs that do not exist between a reviewer and an assessment pipeline. Internal Domain-Advisor / Model-Inspector disagreement is correctly *not* human-agent Competition |
| **Interaction Variant** | **Less relevant — premise only** | Handle with care: the survey defines Supervision as *human-initiated* ("one party, usually a human operator, oversees, monitors, and guides the actions of an LLM-based agent"). SQ1 asks the opposite — when should the system request judgment. The taxonomy therefore has no value for system-initiated escalation, and that absence is itself a finding (8.3 item 7) rather than a slot he occupies |
| **Orchestration Strategy** | **Not relevant** | Pinned to One-by-One. Simultaneous is ruled out by an SQ2 attribution requirement — a judgment must be attributable to one identified reviewer — so the value is derived from the RQ rather than chosen |
| **Orchestration Synchronization** | **Not relevant** (demoted on challenge) | Pinned to Asynchronous, with no synchronous arm designed, planned or evaluated, so it discriminates nothing. The first pass also claimed it touches SQ3 because "the judgment's first real use is on a later case"; that is temporal deferral inside one context, not cross-context reuse. Clause deleted |
| **Communication Structure** | **Less relevant** | Inter-agent topology, fixed by the baseline. Retains a narrow role: describing the system, plus one threat-to-validity sentence about centralized-store failure |
| **Communication Mode** | **Relevant** | The contribution sits here. State plainly that the judgment store is a *reinterpretation* of Message Pool, not an instantiation: the survey's Message Pool is a blackboard among concurrent agents inside one episode, whereas his is a persistent, versioned, human-authored record consumed across episodes. Claiming instantiation is the first thing a reviewer would attack |

### 8.3 MISSING — what the RQs need that the taxonomy cannot express

This is the most valuable column of the exercise, because it is where the doctoral contribution
lives. Eleven concepts were identified; each was tested against the nearest existing dimension and
kept only where that dimension genuinely cannot carry it.

| # | Missing concept | Needed by | Nearest dimension, and why it falls short |
| --- | --- | --- | --- |
| 1 | Reuse of a stored judgment in a later, different episode, plus the reuse mode (inert / advisory / behaviour-changing) with non-destructive write semantics | U-RQ, SQ3 | Feedback Phase "Post Task" is closest but the arrow points the wrong way: it means feedback given after this task, not feedback from a prior task consumed as input to this one. Every Human Feedback dimension is indexed to the episode that produced the feedback |
| 2 | Claim-level validity scope — the prospective applicability envelope, including explicit *negative* scope | SQ2, SQ3 | Feedback Granularity is routinely mistaken for this. It partitions the *current* output; scope is prospective and concerns *future* applicability. The two are orthogonal |
| 3 | Diagnostic attribution — does an intervention reveal a domain-specific quirk or a transferable capability gap in the pipeline? | SQ3, which names this distinction explicitly | None. Every feedback dimension describes what the human did to the output; none describes what the intervention reveals about the *system* |
| 4 | Temporal validity — expiry, supersession, revocation, and lapse when the interpreted guideline is revised | SQ2, SQ3 | Feedback Phase is the dimension people assume covers this and does not: its values locate an act inside one episode and say nothing about how long the resulting judgment stays authoritative |
| 5 | Claim-scoped authority and competence, with a tier separating case-level decisions from rubric-level changes | SQ1, SQ2, SQ3 | Partially adjacent: Feedback Subtype "Human Control" expresses that a human took control of an action; Interaction Variant "Supervision" expresses a standing role. Neither expresses entitlement or competence to decide *this claim* |
| 6 | Version-exact provenance binding to the artifact state judged, with staleness detection and a first-class non-applying outcome | SQ2, SQ3 | None for binding. No branch refers to the identity or version of the artifact under discussion; feedback is assumed to attach to "the output" implicitly and immediately |
| 7 | The elicitation trigger as a versioned, reason-coded policy object, including agent-side uncertainty and abstention signals | SQ1 — its entire object of study | Feedback Phase says *when, conditional on it happening*; Interaction Variant says a human *may* intervene. Neither has any value space for the decision procedure that determines whether a human is asked at all |
| 8 | Attention-budget accounting — a bounded budget per run, an allocation rule across competing claims, per-question expected value | SQ1's "without unnecessary expert burden" | None. The taxonomy has no cost dimension of any kind. Orchestration governs ordering and coupling, not rationing a scarce reviewer |
| 9 | Preserved dissent — two conflicting judgments both retained, reuse blocked pending adjudication, minority position kept as a caveat | SQ2's "validated, reconciled" | The taxonomy models feedback as a signal consumed and resolved within the episode: rankings aggregate, critique informs, refinement replaces, and nothing persists as a retained conflict state |
| 10 | Reuse-leakage control — provenance disjointness between the judgment store and the cases reuse is evaluated on | SQ3 and the U-RQ evaluation boundary | None. State this one *fairly*: the taxonomy is a design-configuration taxonomy, so evaluation hygiene is arguably outside its remit — then argue that for cumulative-memory systems the configuration itself creates the contamination risk |
| 11 | Judgment target layer — verdict vs the agent's stated reasoning vs evidence selection vs the guideline itself, and the recognition that the *rationale*, not the verdict, is what transfers | SQ2 ("including the system's core reasoning"), SQ3 | Granularity gives extent and Subtype gives form; nothing gives the target *layer*. A rationale is not a smaller span of the output, it is a different object |

How to phrase the resulting claim, conservatively: six of the eleven (items 2, 4, 5, 6, 9, 11) are
precisely the fields the governed-judgment contract in SQ2 already enumerates, and three (1, 3, 10)
are what SQ3 adds. That is the gap argument — the taxonomy comprehensively describes *how human
feedback arrives and how agents are wired*, and has no vocabulary for *what happens to a judgment
after it is given*. Say exactly that and no more: it is a coverage claim about one survey's
taxonomy, not evidence that the proposed contract works.

### 8.4 The one slide Iris asked for

Title: **Where the ACL-2026 human-agent taxonomy meets this research — and where it stops**

Left column, "Covered by the taxonomy": Human Feedback — phase, granularity, type/subtype
(SQ1's when and how coarse). Communication Mode — a shared persistent artifact (SQ2's store).
Interaction Variant — Delegation to Supervision, the premise.

Right column, "Not in the taxonomy": what happens to a judgment *after* it is given — validity
scope, expiry and supersession, claim-scoped authority, version-exact provenance, preserved
dissent, target layer (verdict vs rationale), cross-episode reuse and its mode, diagnostic
attribution (local quirk vs capability gap), attention-budget accounting, leakage control.

Footer, one line: *Four taxonomy branches; two describe agent wiring that the VEGO-AI baseline
fixes. The doctoral contribution lives in the right-hand column.*
