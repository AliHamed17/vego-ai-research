# Chapter 2 Claim Audit — VEGO-AI Doctoral Proposal

Audit date: 2026-09-06 (verification continued into 2026-09-07)
Auditor: Claude (literature-review execution lead)
Baseline audited: `VEGO_AI_Doctoral_Proposal_Revised_20260825`, Chapter 2 (§§2.1–2.6),
with supporting checks against §4.3, §5.1, Appendix A and Appendix B
Repository baseline SHA: `c34d3954b5e080d090017d2ea655d454d75a6b92`

**Scope and standing.** This document classifies every substantive absence or novelty
statement in Chapter 2. It does **not** rewrite Chapter 2. Replacement wording is offered
for every non-supported claim so that the reviewer can accept, reject or amend it, but no
proposal text has been changed.

**Evidence standing of this audit.** All four primary databases (ACM Digital Library,
IEEE Xplore, Scopus, Web of Science) were ACCESS BLOCKED; see the companion protocol
audit §10.3. Verification ran through the Crossref REST API, OpenAlex, publisher and
proceedings records, and targeted web search. This audit can therefore establish that a
competitor **exists** — it did so 35 times — but cannot establish that a competitor does
**not** exist. **Consequently no claim below is classified `REFUTED`.** The strongest
adverse classification reached is `LIKELY_FALSE`, reserved for statements contradicted by
a directly quoted passage in a verified Tier A source.

**Classification scheme.**

| Class | Meaning |
| --- | --- |
| `SUPPORTED` | The claim as written survives the audit. No change required. |
| `NEEDS_NARROWING` | The underlying gap survives, but the claim as written is broader than the evidence supports. Replacement wording supplied. |
| `UNVERIFIED` | The audit could not reach the evidence. Not a defect finding; a traceability finding. |
| `LIKELY_FALSE` | A verified Tier A source contradicts the claim as written. Replacement wording supplied. |
| `REFUTED` | A verified source closes the claim entirely. **No claim reached this class.** |

**Summary of results.**

| Class | Count | Claim IDs |
| ---: | --- | --- |
| `SUPPORTED` | 22 | C-01 … C-22 |
| `NEEDS_NARROWING` | 9 | C-23, C-24, C-25, C-26, C-28, C-29, C-30, C-31, C-32 |
| `LIKELY_FALSE` | 2 | C-27 (= C-34), C-33 |
| `UNVERIFIED` | 4 | C-35 … C-38 |
| `REFUTED` | 0 | — |
| **Total distinct claims classified** | **37** | C-01 … C-38, less the C-27/C-34 duplicate |

**One claim is deliberately discussed twice.** C-27 is classified `LIKELY_FALSE` but is
presented in Part 2 alongside the narrowings, because correcting it requires rewording the
surrounding paragraph rather than deleting a sentence. It reappears as C-34 in Part 3 for
completeness of the `LIKELY_FALSE` set. It is **one** claim and is counted once, under
`LIKELY_FALSE`.

---

## Part 1 — Claims classified `SUPPORTED`

No change required to any of the following.

### C-01 · §2.0 — "Every absence claim below is scoped to this anchor set"
`SUPPORTED`. The scoping discipline is applied consistently throughout the chapter and is
the reason the chapter withstands adversarial audit. **This language must survive
revision verbatim.** Nothing in this audit licenses a stronger form, and the chapter
nowhere uses the phrase "no research exists".

### C-02 · §2.0 — "the reuse stream is the thinnest, at seven references"
`SUPPORTED`. Consistent with the reference list, and the chapter correctly draws the
consequence that the reuse argument "is the least densely evidenced". The audit confirms
the diagnosis and sharpens it: the reuse stream is not merely thin but omits whole
predecessor literatures (organisational memory, case provenance, cross-project transfer).
See C-23, C-26, C-27.

### C-03 · §2.1 — "Neither literature treats structural divergence as evidence of error by itself"
`SUPPORTED`. Consistent with [5] (doi:10.1109/TSE.2013.56, verified) and [6]
(doi:10.1145/3041957, verified).

### C-04 · §2.1 — "automated and human grades disagree most exactly where modeling choices were defensible but unanticipated"
`SUPPORTED`. Reference [12] verified (doi:10.1145/3365438.3410944, MODELS '20,
pp. 365–376). The claim is appropriately narrow — it is asserted of the one family where
agreement was actually measured, and the chapter says so.

### C-05 · §2.1 — "It does not establish which output deserves checking, or who may overrule it"
`SUPPORTED`. Correct of multi-agent task separation as reviewed.

### C-06 · §2.2 — "that discrepancy is not closed"
`SUPPORTED`. The chapter discloses the 178/26 versus 165/27 conflict, states that the
reconciling implementation snapshot was not supplied, and explicitly rests no claim on
either figure. This is the correct handling of an unresolved evidence conflict.

### C-07 · §2.2 — "What that literature does not settle, for this setting, is three things"
`SUPPORTED` as scoped. The three items — what a reviewer should be shown, who is
competent and authorised for a specific claim, what becomes of the answer — are the
chapter's organising questions and are correctly framed as unsettled *for this setting*
rather than unaddressed in general.

### C-08 · §2.3 — "In none is the reviewer selected for competence or authority over the claim being judged"
`SUPPORTED`. Asserted specifically of the four complementarity studies [24]–[27], all
four verified (doi:10.1145/3411764.3445717; doi:10.1145/3449287;
doi:10.1145/3805689.3812329; doi:10.18653/v1/2026.findings-acl.422). None selects its
reviewer by competence or authority. The claim is bounded to four named papers and holds.

### C-09 · §2.3 — "none allocates decision authority, and none governs the answer's later life"
`SUPPORTED`. Asserted of selective prediction, learning-to-defer and active learning.
Verified against [33], [34], [35]–[37] and [38]. The audit confirms that authority is
absent from all deferral formulations examined, including the multi-expert ones — see
C-18, which is the surviving half of the GAP-1 argument.

### C-10 · §2.3 — "None has been tested with uncertainty, consequence, evidence quality, reviewer fit, and burden weighed jointly at a matched attention budget"
`SUPPORTED`. This is a five-way conjunction plus a matched-budget evaluation condition.
No competitor found in this audit satisfies it. Notably, the 2025 systematic review of
business-process resource allocation (doi:10.1016/j.is.2025.102541) independently reports
that its field lacks comparative benchmarking — which is corroborating rather than
contradicting evidence. **This is now the strongest-standing sentence in §2.3 and should
carry more of the GAP-1 argument than it currently does.**

### C-11 · §2.3 — "Asking on every case is not merely expensive; it can be less safe than asking selectively"
`SUPPORTED`. References [44] (doi:10.1186/s12911-017-0430-8) and [45]
(doi:10.1197/jamia.M1809) both verified. The structural reading of alert-fatigue evidence
is sound.

### C-12 · §2.3.1 — "Eleven concepts ... have no expressible position in the taxonomy"
`SUPPORTED`. Appendix A already bounds this correctly: single-rater, RQ-to-taxonomy
coverage analysis, "not independent evidence of a literature gap", and the concepts were
derived from the research questions rather than found in the field. Given those stated
bounds the claim is defensible as written. Appendix A.4's further concession — that the
corpus "could not have surfaced the nearest competing formulation at all" because
multi-expert learning-to-defer lives in a literature the survey does not index — is
exactly right, and this audit confirms it.

### C-13 · §2.4 — "Provenance can state that an entity was invalidated [47], but supplies neither the reasons a judgment lapses, nor conditions on who may declare it, nor any consequence obliging an invalidated judgment to stop influencing decisions"
`SUPPORTED` **as scoped to provenance**, which is how it is written. PROV-DM does indeed
supply none of the three.

**Required adjacent concession.** The sentence is true of provenance but sits immediately
before a sentence that generalises it (C-27, `LIKELY_FALSE`). Truth maintenance supplies
precisely the third item — a consequence obliging a withdrawn belief to stop acting, via
dependency-directed backtracking (Doyle, *AI* 12(3):231–272, 1979,
doi:10.1016/0004-3702(79)90008-0). Retaining C-13 unchanged is correct **only if** C-27
is corrected, so that the reader is not led from a true statement about provenance to a
false statement about the field.

### C-14 · §2.4 — "attribute-based access control decides exactly this ... without reference to how relevant the object is"
`SUPPORTED`. Reference [59] verified (doi:10.6028/NIST.SP.800-162). The separation of
authorisation from relevance is exactly what ABAC specifies, and the chapter uses it
correctly.

### C-15 · §2.4 — "Similarity cannot authorize, and authorization cannot appraise"
`SUPPORTED`. This is a claim about what the two mechanisms are, not about what any
literature has combined, and it remains true. It survives even though the *combination*
has now been demonstrated (see C-26) — combining two mechanisms in a pipeline does not
make either mechanism do the other's work.

### C-16 · §2.4 — "competence-preserving deletion ... is the nearest thing in the reviewed set to a governed retention decision"
`SUPPORTED` as scoped by "in the reviewed set". Reference [54] verified as to venue and
ordinal (Fourteenth IJCAI, 1995) and start page. The characterisation of what it decides
— whether the store as a whole stays competent, not whether one stored judgment may act
— is accurate. As a claim about the *field* it would need narrowing (Leake & Wilson's
maintenance framework, doi:10.1007/bfb0056333, is a broader account), but the chapter
does not make the field-level claim. See also the page-range correction in Part 5.

### C-17 · §2.6 — "This proposal claims none of them as new"
`SUPPORTED`, and it is the sentence that makes the chapter auditable. The chapter names
eleven existing mechanism streams and disclaims novelty in all of them. This audit added
several more streams the chapter had not named (design rationale, truth maintenance,
organisational memory, claim-level publication models, BPM authorisation) — additions
which extend the disclaimer rather than contradicting it.

### C-18 · §2.6 — "neither models authority as distinct from competence"
`SUPPORTED`, asserted of [60] and [61]. Both verified. This audit examined the
multi-expert deferral formulations directly and found no authority, mandate, eligibility
or decision-rights construct in either. **This clause is the surviving half of GAP-1 and
must now carry the claim that its companion clause (C-25) can no longer carry.**

### C-19 · §2.6 — "No formulation in the literature reviewed here, and none among the ninety papers screened in Appendix A, makes the selection of the reviewer a function of assessed competence and authority over the specific contested fragment"
`SUPPORTED` as a scoped conjunction. This is the chapter's central gap statement and it
survives the audit, because the conjunction is genuinely unmet: multi-expert deferral
supplies assessed instance-conditional competence but no authority; the business-process
literature supplies authority and declared capability but not assessed competence; and no
identified work supplies both, at claim level, in an evaluated routing policy.

**Two strengthening recommendations, neither required.** First, the word "assessed" is
doing decisive work here and should be defined at first use, because the entire GAP-1
residual now rests on the distinction between *assessed* and *declared* competence.
Second, the sentence would be stronger if it named the two half-matches explicitly rather
than leaving them to be inferred — see the replacement wording at C-25.

### C-20 · §2.6 — "Neither appears in the anchor set, because neither shares its vocabulary"
`SUPPORTED`, and independently confirmed by this audit in a stronger form than the
chapter states. The companion protocol audit (§§4.5, 5.6, 6.5) shows that the registered
queries could not have reached those literatures either, because the terms that lead into
them (`resource allocation`, `task assignment`, `provenance`, `transfer learning`) sit in
the generic class and are conjoined with the QL-05 substrate block, which papers in those
fields do not satisfy. The vocabulary mismatch the chapter identifies is real and is
built into the protocol as well as into the anchor set.

### C-21 · §2.6 — "an elaborate implementation is not a contribution if a simpler record, threshold, or review process performs as well"
`SUPPORTED`. The correct methodological stance, and it raises rather than lowers the
evidential bar the programme must clear. This audit reinforces its necessity: several
verified competitors (temporal validity intervals, a decision-record template,
relevancy-filtered reuse) are markedly simpler than the proposed artefacts and have never
been compared against them.

### C-22 · §2.6 — "On the umbrella question it offers no reviewed instance of the three operating together under one evaluation"
`SUPPORTED`. No identified work evaluates claim-level routing, a governed judgment record
and controlled reuse together. This is the least contested claim in the chapter.

---

## Part 2 — Claims classified `NEEDS_NARROWING`

The underlying gap survives in every case below. The wording does not.

### C-23 · §2.4 — "No record format combines reasoning-level content, scope, authority, retained disagreement, and a lifecycle at claim level"

**Why it needs narrowing.** A verified Tier A claim-level record model already combines
reasoning-level content, provenance and retained disagreement. Micropublications
(Clark, Ciccarese & Goble, *Journal of Biomedical Semantics* 5:28, 2014,
doi:10.1186/2041-1480-5-28) take a single claim as the unit and attach its attribution,
supporting data, methods and materials, the argument connecting evidence to claim, and —
explicitly — challenge and opposition. The abstract states the model "supports challenge
and disagreement" and that maximal forms include "all relevant evidence, interpretations,
discussions, challenges brought forward or opposition". Nanopublications
(doi:10.3233/isu-2010-0613) add version-exact claim-level identity. Design rationale
supplies retained competing positions with their supporting and opposing arguments
(doi:10.1145/58566.59297; doi:10.1207/s15327051hci0603&4_2). None of these is cited in
the chapter.

Three of the five listed elements are therefore already combined at claim level. The two
that are not are **scope** and **authority** — and competence, which the sentence does
not currently list.

**Replacement wording.**

> Within this anchor set no record format combines reasoning-level content with a validity
> scope and a claim-scoped authority. Claim-level models that carry rationale, provenance
> and retained disagreement do exist — micropublications attach evidence, argument and
> explicitly represented challenge to a single claim, and nanopublications give a claim
> version-exact provenance — but neither attaches the competence or the mandate of the
> person asserting it, neither carries a condition on which the claim lapses, and neither
> has been evaluated for reconstructability at a measured capture cost.

### C-24 · §2.4 — "case-based reasoning is the closest direct predecessor"

**Why it needs narrowing.** Closest for *retrieval and adaptation*, yes. But for the
specific question SQ3 asks — whether a stored item may act in a later context — two
verified predecessors are closer and neither is cited. Case provenance
(Leake & Whitehead, ICCBR 2007, doi:10.1007/978-3-540-74141-1_14) records where each
stored case came from and uses that provenance in later retrieval and retention
decisions. Intelligent lessons-learned systems (Weber, Aha & Becerra-Fernandez,
*Expert Systems with Applications* 20(1):17–34, 2001, doi:10.1016/s0957-4174(00)00046-4)
describe a lesson lifecycle with an explicit verification step before storage and an
explicit delivery step into a later decision, and report that recorded experience does
not influence later decisions unless delivery is embedded in the decision process.

**Replacement wording.**

> Case-based reasoning is the closest predecessor for retrieval and adaptation, and its
> retrieve–reuse–revise–retain cycle already separates finding a prior case from adapting
> it. Two adjacent lineages come closer to the governance question: case provenance
> records a stored case's sources and uses them in later retrieval and retention
> decisions, and organisational lessons-learned systems place an explicit verification
> step before storage and an explicit delivery step into a later decision — reporting, as
> this proposal also argues, that recorded experience does not influence later decisions
> unless delivery is embedded in the decision process.

### C-25 · §2.6 — "makes the selection of the reviewer a function of assessed competence and authority" (the accompanying characterisation of what BPM and deferral do)

**Why it needs narrowing.** The gap statement itself is `SUPPORTED` (C-19). What needs
narrowing is the surrounding framing, which does not concede how much of each half
already exists. Two verified findings must be conceded explicitly:

1. **Multi-expert deferral supplies assessed, instance-conditional competence.** See
   C-30 (`LIKELY_FALSE`) for the specific sentence that must change.
2. **The business-process literature supplies authority and declared capability in one
   framework, and has since 2005.** The workflow resource-pattern catalogue
   (Russell, van der Aalst, ter Hofstede & Edmond, CAiSE 2005, LNCS 3520, pp. 216–232,
   doi:10.1007/11431855_16) contains *Capability-Based Distribution*, *Authorisation*,
   *Separation of Duties* and *Role-Based Distribution* in a single pattern catalogue,
   evaluated per work item. Authority is separately formalised and enforced in
   Bertino, Ferrari & Atluri (*ACM TISSEC* 2(1):65–104, 1999, doi:10.1145/300830.300837),
   and capability and organisational position are jointly expressible in RAL/RALph
   (doi:10.1007/978-3-642-28108-2_5; doi:10.1007/978-3-319-19069-3_4).

**Replacement wording (to follow the gap statement in C-19).**

> The two halves of that conjunction exist separately, in literatures that do not cite
> each other. Multi-expert learning-to-defer supplies assessed competence: it estimates,
> for each named expert, the probability that the expert decides the specific instance
> correctly, and routes accordingly — but it represents no authority, mandate or
> eligibility. Business-process resource allocation supplies authority: the workflow
> resource patterns place capability-based distribution, authorisation and separation of
> duties in one catalogue, evaluated per work item, and task-level authorisation
> constraints have been formally specified and enforced since 1999 — but the capability
> matched there is declared rather than assessed, and that field's own 2025 systematic
> review of sixty-one allocation studies reports its methods to be predominantly
> rule-based, calling for evidence-oriented allocation and comparative benchmarking that
> it does not find. What is absent is the join: assessed, claim-specific competence
> conditioning a routing decision that also carries authority, evaluated at a matched
> attention budget against a preregistered selective-risk ceiling.

### C-26 · §2.4 — "No reported procedure decides whether a prior judgment may act in a specific new context, as opposed to retrieving it"

**Why it needs narrowing.** Two verified Tier B proceedings papers decide exactly whether
a retrieved item may be used, by policy, before it reaches the prompt:
Chen, Tackman, Setälä, Poranen & Zhang (ACM SAC 2025, pp. 915–919,
doi:10.1145/3672608.3707848) and Chen & Taipalus (RACS 2025, pp. 1–7,
doi:10.1145/3769002.3769952). Both enforce fine-grained access control at the retrieval
stage. Separately, guideline-adaptation frameworks already cited by the proposal as [9]
and [10] decide whether a source recommendation may be adopted in a new institutional
context, and lessons-learned systems interpose a verification step before a lesson is
allowed to act (doi:10.1016/s0957-4174(00)00046-4).

The gap survives because none of these tests **currency** — whether the prior conclusion
is still true — nor **applicability** to the target context, nor **benefit or safety** of
letting it act. What they test is entitlement.

**Replacement wording.**

> Entitlement to use a retrieved item is now decided by policy in the retrieval
> literature: access-control-aware retrieval enforces fine-grained permissions before a
> passage reaches the prompt, and guideline-adaptation frameworks appraise whether a
> source recommendation may be adopted in a new institutional context. What no reported
> procedure does is decide the whole question jointly — similarity, applicability to the
> target context, authorisation, current validity, and benefit or safety — for one
> recorded judgment at one moment of reuse.

### C-27 · §2.4 — "The lifecycle is the dimension least covered by any of these"

> **Classification: `LIKELY_FALSE`** (see C-34). Presented here rather than in Part 3
> because the correction requires rewording the surrounding paragraph, not deleting a
> sentence. Counted once, under `LIKELY_FALSE`.

**Why it is likely false.** This is the most consequential wording problem in §2.4, and
it is close to inverted. On the evidence gathered, the lifecycle is among the
*better*-covered dimensions:

| Lifecycle element | Covered by | Verified source |
| --- | --- | --- |
| Reason-conditioned lapse with automatic withdrawal | Truth maintenance | doi:10.1016/0004-3702(79)90008-0 |
| Concurrent conflicting assertions, each with its scope of validity | Assumption-based TMS | doi:10.1016/0004-3702(86)90080-9 |
| Principled supersession — which commitment yields | AGM belief revision | doi:10.2307/2274239 |
| Versioning and change management over stored knowledge | Ontology change and evolution surveys | doi:10.1017/s0269888908001367; doi:10.1017/s0269888913000349 |
| A state that lapses on a stated condition | Temporal RDF validity intervals | doi:10.1109/tkde.2007.34 |

The proposal itself names truth maintenance and belief revision in §2.6 as an exposed
area. This audit confirms the exposure is real and locates it precisely: the dimensions
genuinely least covered are **claim-scoped authority** and **assessed competence**, not
lifecycle.

**Replacement wording.**

> The dimensions least covered are authority and competence. The lifecycle, by contrast,
> has mature machinery in literatures the streams above do not cite: truth maintenance
> withdraws an assertion automatically when its support is withdrawn, assumption-based
> variants hold conflicting assertions concurrently with the conditions under which each
> holds, belief revision supplies a principled account of which commitment yields, and
> temporal representations give an assertion a validity interval that lapses. What none
> of them keys a lapse to is a governing policy that changed, a mandate that was
> withdrawn, or a challenge by a more authorised reviewer — and none attaches the
> competence or standing of a person to the assertion at all.

### C-28 · §2.4 — "no reported procedure separates a local quirk from a transferable limitation on independent evidence"

**Why it needs narrowing.** Empirical software engineering does close to exactly this,
per source–target pair, against independent target evidence.
Zimmermann, Nagappan, Gall, Giger & Murphy (ESEC/FSE 2009, pp. 91–100,
doi:10.1145/1595696.1595713) ran a large-scale experiment over many cross-project pairs
to determine whether a predictive relationship learned in one project transfers to
another, measured against the target project's own labelled outcomes, and found that
transfer succeeded in only a small fraction of pairs.
Turhan, Menzies, Bener & Di Stefano (*Empirical Software Engineering* 14(5):540–578,
2009, doi:10.1007/s10664-008-9103-7) add relevancy filtering of foreign data before it is
admitted, validated against target outcomes.

The gap survives on **unit**: what transfers there is a fitted statistical model over
labelled data, not one expert's recorded judgment about one contested claim, and the
diagnosis concerns predictor portability rather than whether a recurring correction
indicates a pipeline limitation or a local cause.

**Replacement wording.**

> Testing whether a conclusion learned in one context holds in another, per source–target
> pair and against independent target evidence, is established practice: cross-project
> defect-prediction studies do precisely this at scale, and report that transfer succeeds
> only rarely and only under identifiable conditions. What transfers in that work is a
> fitted model over labelled outcomes. No reported procedure makes the same
> determination for a single recorded human judgment about a single contested claim, or
> attributes a recurring correction to a general limitation of the assessment pipeline
> rather than to one ambiguous guideline, one task design, one model version or one
> reviewer population.

### C-29 · §2.4 — "the selection carries no test of whether the passage may be used [58]"

**Why it needs narrowing.** Exactly true of [58] (Lewis et al., retrieval-augmented
generation), to which it is attributed, and the attribution is explicit. It becomes false
if read as a claim about the retrieval literature, which the surrounding paragraph
invites. See C-26 for the evidence.

**Replacement wording.**

> Retrieval-augmented generation as originally formulated conditions an answer on
> passages selected by vector similarity alone, and that selection carries no test of
> whether the passage may be used [58]. Subsequent work adds one: access-control-aware
> retrieval enforces the requester's permissions before augmentation. The conflation the
> original formulation makes concrete is therefore partly resolved for entitlement, and
> not at all for currency, applicability or benefit.

### C-30 · §2.6 — SQ2 refutation condition: "a lifecycle state able to lapse on a stated condition"

**Why it needs narrowing.** As written, this refutation condition is **satisfiable by a
2007 database paper**. Temporal RDF (doi:10.1109/tkde.2007.34) gives an assertion an
explicit validity interval, and that interval is a stated condition on which the
assertion's status lapses. A reviewer applying the proposal's own stated condition
literally could close SQ2 on it.

The chapter plainly intends something stronger — a lapse keyed to a governing policy, an
evidence change, or a withdrawal of mandate. Because the refutation conditions are the
mechanism that makes the gap falsifiable, leaving this one loose is a material risk.

**Replacement wording.**

> For SQ2, either of two findings removes the need for Study 2. The first is a reported
> claim-level record that resolves conflicting qualified judgments to a single verdict and
> still supports blind reconstruction of the reasoning at equal or lower capture cost.
> The second is such a record carrying a lifecycle state that lapses on a non-temporal
> condition — a change in the governing guideline or policy, a withdrawal of the
> asserting reviewer's mandate, or a successful challenge by a more authorised reviewer —
> rather than on the passage of time alone.

### C-31 · §2.3 — "Within this anchor set, none of them selects which person by competence and authority over the specific claim"

**Why it needs narrowing.** Read against its antecedent — "The reviewed methods answer
when to ask" — the sentence sweeps in learning-to-defer, and multi-expert deferral is in
the anchor set as [60] and [61]. Those formulations *do* select which person, by
instance-conditional competence. The sentence is therefore too strong even within the
anchor set it scopes itself to.

**Replacement wording.**

> Within this anchor set, the methods that answer when to ask do not select which person
> at all; and the multi-expert deferral formulations that do select among differentiated
> experts select on assessed competence alone, with no representation of authority over
> the claim being decided.

### C-32 · §2.6 (and implicitly §3.2) — the competence-plus-authority conjunction presented as the distinguishing requirement

**Why it needs narrowing.** The conjunction is not conceptually novel. It is a binding
regulatory requirement:

> Regulation (EU) 2024/1689 (Artificial Intelligence Act), Article 26(2): "Deployers
> shall assign human oversight to natural persons who have the necessary competence,
> training and authority, as well as the necessary support."

This is a Tier A authoritative standard. It supplies no mechanism, no per-claim selection
procedure and no evaluation, so it does not refute GAP-1 — and it materially strengthens
the motivation for Study 1. But the proposal should not leave a reviewer to discover that
the pairing it treats as its distinguishing insight is already mandated in law.

**Recommended addition (to §2.3, alongside meaningful human control [31]).**

> The pairing is not merely a design preference. Regulation (EU) 2024/1689 requires
> deployers of high-risk AI systems to assign human oversight to persons holding the
> necessary competence, training and authority. The requirement is stated at the level of
> a role and a deployment; it specifies no procedure for deciding, for one contested
> claim, which person satisfies it. That procedure is what SQ1 asks for.

---

## Part 3 — Claims classified `LIKELY_FALSE`

### C-33 · §2.6 — "What they condition on is an aggregate competence profile over a task distribution, not assessed standing to settle the specific contested fragment"

`LIKELY_FALSE` for the first clause. **This is the audit's principal finding against the
chapter as written.**

**The contradicting evidence.** Verma, Barrejón & Nalisnick (AISTATS 2023, PMLR
206:11415–11434) — the proposal's own reference [60] — state in their abstract, quoted
verbatim from the PMLR proceedings page:

> "we study the frameworks ability to estimate P( m_j = y | x ), the probability that the
> jth expert will correctly predict the label for x"

The conditioning is on `x`, the specific instance. The quantity estimated is per-expert
correctness *for that instance*, not an aggregate profile over a task distribution. The
paper's two consistent surrogates and its conformal expert-subset selection are both
built on that instance-conditional estimate. The same holds for [61]
(Mao, Mohri, Mohri & Zhong, NeurIPS 36), whose routing function is likewise a function of
the instance.

**What survives.** The second clause of the sentence — "not assessed standing to settle
the specific contested fragment" — survives, but only because *standing* means authority,
not competence. And the following clause, "neither models authority as distinct from
competence" (C-18), is fully `SUPPORTED`. The GAP-1 argument therefore survives intact;
what fails is one factual characterisation of the closest competitor, and it fails on the
competitor's own abstract.

**Why this matters beyond accuracy.** A reviewer who checks the closest named competitor
and finds the proposal has mis-described it will discount the surrounding gap claim,
which is otherwise sound. Correcting this sentence strengthens the chapter.

**Replacement wording.**

> Learning-to-defer comes closest. Its single-expert formulations choose between a model
> and an undifferentiated human [35], [36], [37]; its multi-expert formulations select
> among differentiated experts by estimating, for each expert, the probability that the
> expert decides the specific instance correctly [60], [61]. Instance-conditional
> competence is therefore already modelled, and this proposal claims no novelty in it.
> What those formulations do not model is authority: an expert is characterised by
> expected accuracy and cost, never by standing to settle the matter. Nor do they operate
> without per-expert outcome labels, or over a unit that admits several defensible
> answers rather than one correct one. One study that routed by both claim-specific
> assessed competence and claim-specific authority would refute this.

### C-34 · §2.4 — "The lifecycle is the dimension least covered by any of these"

`LIKELY_FALSE`. **This is the same claim as C-27**, listed here so that the
`LIKELY_FALSE` set is complete in one place. The evidence table, the reasoning and the
replacement wording are given at C-27 above; they are not repeated. Counted once in the
summary table, under `LIKELY_FALSE`.

---

## Part 4 — Claims classified `UNVERIFIED`

None of the following is a defect finding. Each is a traceability finding: the audit
could not reach the evidence, and the reviewer should know that.

### C-35 · §2.2 — "no metric is given for either characterization"
`UNVERIFIED`. Asserted of the VEGO-AI foundation manuscript [1], which is unpublished and
is not in the repository. The claim cannot be checked from any available source. The
chapter's handling is otherwise exemplary — it declines to treat the characterisations as
measured results precisely because no metric is given — so the `UNVERIFIED` status
reflects the absent manuscript, not doubt about the statement.

### C-36 · §2.6 / Figure 8 — "the third [column] is empty for every construct"
`UNVERIFIED`. Figure 8's thirteen-construct, three-test coverage matrix is
author-generated, and the per-construct coding sheet behind it is not in the repository.
The audit's independent findings are broadly *consistent* with an empty third column —
no identified work evaluates the mechanisms in combination — but the second column
("operates at the level of a single contested claim") is now questionable for at least
two constructs, since micropublications operate at claim level for rationale and retained
disagreement, and BPM authorisation operates at work-item level for authority.
**Recommendation:** publish the coding sheet, and re-code the second column against the
28 papers in `literature/2026-09-06-high-priority-literature-map.csv` before Figure 8 is
relied upon again.

### C-37 · §5.1 / Appendix B — "67 of 68 verified against a publisher, proceedings, registry, or DOI record"
`UNVERIFIED` at repository level. The claim is credible and this audit found nothing
contradicting it, but its evidence file — `VEGO_AI_Reference_Audit_20260825.md` — is one
of five Appendix B deliverables absent from the repository. This audit independently
re-verified **54 of 68** references against an external record (see the protocol audit
§2.2). **Recommendation:** bring the five accompanying deliverables under version control
before the reviewer relies on the 67-of-68 figure.

### C-38 · §2.6 — "Two literatures are named here because they are the most likely to refute those conditions and have not been searched"
`UNVERIFIED` as a present-tense statement — more precisely, **superseded**. It was
accurate at the 25 August 2026 cover date. Both literatures have now been searched at
reconnaissance depth, and both narrowed their corresponding gap (protocol audit §§9.1,
9.2). The sentence must be updated as a matter of fact rather than of wording, and the
declaration of exposure replaced with the result.

**Replacement wording.**

> Two literatures were named in the August 2026 draft as the most likely to refute these
> conditions and as not yet searched: business-process work-item and resource allocation,
> and knowledge-base curation with truth maintenance and belief revision. Both have since
> been searched at reconnaissance depth, ahead of the registered protocol. Both narrowed
> the corresponding gap without closing it, and both are now cited above. The registered
> queries in Section 4.3 remain what would test the field systematically; they have not
> been executed.

---

## Part 5 — Citation-level defects

Distinct from the claim classifications. Each is a correction to the reference list.

| Ref | Defect | Evidence | Action |
| --- | --- | --- | --- |
| [54] Smyth & Keane | Page range given as 377–383 | ACM Digital Library record (`dl.acm.org/doi/10.5555/1625855.1625905`) gives 377–382; the IJCAI proceedings index confirms start page 377 | **Correct to 377–382**, or record why 383 is retained |
| [61] Mao, Mohri, Mohri & Zhong | Page range 3578–3606 not confirmed | NeurIPS 2023 proceedings record confirms authors, title, venue and year but the audit could not confirm the page range | **Recheck against the printed proceedings** |
| [13] Singh, Boubekeur & Mussbacher | No defect — recorded for the protocol | DOI `10.1145/3550356.3561583` is absent from the Crossref index but the ACM DL record exists with pages 257–266 exactly as cited | **No change.** Record the verification route as ACM DL, and note that Crossref cannot substitute for ACM coverage |
| [52] Zhou et al. | No defect | arXiv:2606.13174 verified: title, full author list, submission date 11 June 2026; no peer-reviewed venue stated | **No change.** Correctly marked a preprint; keep Tier C labelling wherever cited |
| [55] Ben-David et al. | No defect | Proposal cites 2010 (issue year, *Machine Learning* 79(1–2)); Crossref reports 2009 online-first | **No change.** Citing the issue year is correct |
| [32] Alfrink et al. | No defect | Proposal cites 2023 (vol. 33, no. 4); Crossref reports 2022 online-first | **No change** |
| — | Upstream metadata error to be aware of | Crossref's container-title for `10.1007/11431855_16` (Russell et al., recommended for citation per C-25) is corrupted to an unrelated fluid-mechanics series | Cite as **CAiSE 2005, LNCS 3520, pp. 216–232** per the Springer record, not per Crossref |

No duplicate DOI, no duplicate title, and no other year or venue inconsistency was found
across the 51 DOIs in the reference list.

---

## Part 6 — Gap verdicts

Applying the five-way scheme required by the audit brief. Each verdict is scoped to the
executed corpus, which did not include any primary database (protocol audit §10.3).

### GAP-1 / SQ1 — **B. NARROWED**

The conjunction survives; the framing does not. Assessed instance-conditional competence
is established prior art in multi-expert learning-to-defer, contradicting the chapter's
current characterisation (C-33). Authority, declared capability and separation of duties
are established prior art in business-process resource allocation and workflow
authorisation, in one framework, since 2005 (C-25). The conjunction of *assessed*,
claim-specific competence *with* authority, in an evaluated routing policy at a matched
attention budget, was not found — and the business-process field's own 2025 systematic
review independently reports that its allocation methods are predominantly rule-based and
lack comparative benchmarking, which corroborates the residual. Closest competitors:
doi:10.1007/11431855_16 (authority + declared capability, per work item) and PMLR
206:11415–11434 (assessed competence, per instance). Neither holds both.

### GAP-2 / SQ2 — **B. NARROWED**

Every individual element of the proposed record exists somewhere, and more of them exist
at claim level than the chapter concedes. Micropublications combine claim-level
rationale, provenance, attribution and explicitly retained challenge (C-23);
nanopublications add version-exact claim identity; truth maintenance, assumption-based
TMS, AGM revision, ontology evolution and temporal validity intervals collectively supply
the lifecycle (C-27), which the chapter incorrectly ranks as least covered. The residual
is narrower but intact: no identified record attaches assessed competence and authority
as a mandate to a claim-level judgment; no identified lapse condition is keyed to
anything but time or logical support; and no identified record has been evaluated for
blind reconstructability at a measured capture cost. **SQ2's second refutation condition
must be tightened (C-30) or it is satisfiable by a 2007 paper.**

### GAP-3 / SQ3 — **B. NARROWED**

Entitlement-checked retrieval now exists (C-26). Per-pair transfer testing against
independent target evidence is long-established software-engineering practice (C-28), as
is recurrence detection at industrial scale. Organisational lessons-learned systems
already interpose verification before stored experience acts, and already report the
enforcement-consequence finding the proposal argues for (C-24). The residual is the
**joint** test — similarity, applicability, authorisation, current validity, and
benefit or safety — applied to one recorded human judgment at one moment of reuse, and
the diagnostic attribution of a recurrence to a transferable capability limitation rather
than a local cause. Neither was found.

### Overall

No gap is `REFUTED`. No gap is `PARTIALLY REFUTED` in the sense of a specific study
closing a specific condition. All three are `NARROWED`, and in each case the narrowing
makes the residual claim **more** defensible than the current wording, because it names
the closest competitors and the exact residual difference instead of asserting a broader
absence. The `E. INSUFFICIENT EVIDENCE` class applies to no gap, but it does apply to one
sub-claim: whether a simpler existing record achieves equivalent reconstructability at
lower capture cost is **untested** — none of the identified claim-level record models has
been evaluated for capture cost or blind reconstruction — so that half of GAP-2 is
neither supported nor refuted but open, and Study 2 remains the way to settle it.

---

## Part 7 — Recommended action sequence

Chapter 2 must **not** be rewritten until the reviewer accepts this audit. When it is:

1. Correct C-33 first. It is the one factual error about a named competitor and the
   cheapest credibility repair in the chapter.
2. Correct C-27 / C-34 second, together with C-13's adjacent concession, so the reader is
   not led from a true statement about provenance to an inverted ranking.
3. Apply C-25's replacement wording, which converts §2.6's central paragraph from an
   assertion of absence into a positioned claim naming both half-matches.
4. Tighten C-30, the SQ2 refutation condition, before any reviewer applies it literally.
5. Apply C-23, C-24, C-26, C-28, C-29, C-31 — the remaining narrowings.
6. Add the eleven citations this audit found load-bearing and absent: Russell et al. 2005;
   Bertino et al. 1999; Pufahl et al. 2025; Clark et al. 2014; Groth et al. 2010;
   Singh et al. 2019; Gutierrez et al. 2007; Weber et al. 2001; Leake & Whitehead 2007;
   Zimmermann et al. 2009; and Regulation (EU) 2024/1689 Art. 26(2).
7. Update C-38 to state that both adjacent literatures have now been searched and what
   was found.
8. Resolve the four `UNVERIFIED` traceability items by bringing the Appendix B
   deliverables and the Figure 8 coding sheet under version control.
9. Correct the two page ranges in Part 5.
