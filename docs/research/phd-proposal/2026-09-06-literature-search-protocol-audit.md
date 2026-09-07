# Literature Search Protocol Audit — VEGO-AI Doctoral Proposal

Audit date: 2026-09-06 (verification runs continued into 2026-09-07)
Auditor: Claude (literature-review execution lead)
Baseline audited: `VEGO_AI_Doctoral_Proposal_Revised_20260825`, Chapter 2, §4.3, §5.1, Appendix A, Appendix B, References
Repository baseline SHA: `c34d3954b5e080d090017d2ea655d454d75a6b92`

**Status of this document.** This is a pre-execution protocol audit and evidence-closure
report. It does not execute the registered systematic review, and it does not rewrite
Chapter 2. No count in this document is a database screening count. Where a database
could not be reached, the fact is recorded as `ACCESS BLOCKED` rather than estimated.

---

## 1. Current protocol status

The proposal registers, in §4.3, five query families with a two-class term scheme, a
2015–2026 primary window with a documented snowballing exception, fixed source roles,
and a per-query audit record. §5.1 and Appendix B both state that **zero queries have
been executed**. This audit confirms that position: no execution record exists anywhere
in the repository, and the audit did not execute one.

Three status findings require correction.

**1.1 The repository register and the proposal disagree on what the five families are.**
`docs/research/phd-proposal/literature-search-execution-register.md` (dated 2026-07-30,
status `PROTOCOL READY / NOT RUN`) defines QL-01 to QL-05 as:

| ID | Register concept (2026-07-30) | Proposal §4.3 Table 3 concept (2026-08-25) |
| --- | --- | --- |
| QL-01 | Agentic or multi-agent AI with human oversight | human–agent collaboration |
| QL-02 | Expert feedback, knowledge capture, memory, reusable judgment | selective intervention |
| QL-03 | Domain modeling, assessment, variability, conformance | judgment representation and governance |
| QL-04 | Intervention workload, governance, trust, evaluation | reuse and transfer |
| QL-05 | Clinical guidelines, CDSS overrides, alert fatigue, healthcare process mining | substrate (runs alone) |

These are not the same five families, and the mapping is not a renaming: QL-03 and QL-04
have exchanged subject matter, and QL-05 has changed from a conditional medical family to
the substrate conjunction block used by all four other families. The register still
carries the superseded Boolean expressions and the superseded planned execution matrix.
Any agent or supervisor reading the register rather than the proposal would execute the
wrong protocol. **The register must be superseded or explicitly marked as historical
before execution.** This is the single highest-priority reproducibility defect found.

**1.2 The accompanying deliverables named in Appendix B are not in the repository.**
Appendix B names five files as shipping alongside the proposal:
`VEGO_AI_Appendix_A2_Dimension_Disposition_20260825.md`,
`VEGO_AI_Reference_Audit_20260825.md`, `VEGO_AI_ACL_Taxonomy_Slide_20260825.pptx`,
`VEGO_AI_SLR_Protocol_Pack_20260825.md`, `VEGO_AI_SLR_Assessment_20260825.md`.
A recursive search of the repository returns none of them. The per-reference
verification sources on which §5.1's "67 of 68 verified" claim rests are therefore not
auditable from the repository. The claim is not disputed — this audit independently
re-verified a majority of the reference list (§2 below) — but its evidence base is
currently external to version control.

**1.3 The term-class assignment is frozen, which is correct, but one consequence of it
defeats the protocol's own stated purpose.** §4.3 states that generic terms are
"conjoined with a substrate block drawn from QL-05, so that a record must touch both the
mechanism and the modeling-or-guideline setting before it is retrieved." §2.6
simultaneously registers business-process resource allocation and knowledge-base
curation / truth maintenance / belief revision as "required targets of the searches
specified in Section 4.3." These two commitments are incompatible for any term in the
generic class, because a business-process or knowledge-base-curation paper does not
mention domain models, conceptual models, automated grading or computer-interpretable
guidelines. §§4 and 6 below identify exactly which terms are affected. This is a
structural defect, not a tuning issue, and it is the second highest-priority finding.

---

## 2. Current evidence base

### 2.1 What the proposal claims

- 68 cited anchor references, reached by targeted search and backward citation tracing.
- 67 of 68 verified against a publisher, proceedings, registry or DOI record; [1] is
  unpublished and cited from a supplied working manuscript.
- One unpublished VEGO-AI foundation manuscript [1].
- 90 unique papers screened from the ACL-2026 survey's companion repository:
  22 relevant, 63 less relevant, 5 not relevant; relevant and not-relevant dispositions
  abstract-confirmed 27 of 27; the 63 less-relevant dispositions remain title-level.
- Screening and taxonomy classification single-rater, no inter-rater reliability.
- A five-family registered protocol, not executed.

Chapter 2 correctly and repeatedly scopes its absence claims to the anchor set and the
90 screened papers rather than to the field. That scoping discipline is sound and should
be preserved verbatim through any revision.

### 2.2 What this audit independently re-verified

The proposal's reference list contains **51 distinct DOIs**. All 51 were machine-checked
against the Crossref REST API. Results:

| Outcome | Count | Notes |
| --- | ---: | --- |
| Resolved in Crossref with title, type, year and container | 49 | metadata consistent with the proposal's citation in every case |
| Not in Crossref | 2 | `10.1145/3550356.3561583` and `10.48550/arXiv.2606.13174` |

Both misses were resolved by other authoritative routes:

- **[13] Singh, Boubekeur & Mussbacher, "Detecting mistakes in a domain model."** The DOI
  is absent from the Crossref index but the record exists on the ACM Digital Library at
  `dl.acm.org/doi/10.1145/3550356.3561583`, in the MODELS '22 Companion proceedings, with
  pages 257–266 exactly as cited. A sibling DOI under the same proceedings prefix
  (`10.1145/3550356.3556502`) *is* in Crossref, so this is an ACM deposit gap, not a
  citation error. **No defect in the proposal.** Consequence for the protocol: Crossref
  cannot be used as a substitute for ACM Digital Library coverage (§10).
- **[52] Zhou et al., arXiv:2606.13174.** Verified on the arXiv abstract page: title,
  full author list and submission date 11 June 2026 all match. arXiv DOIs are registered
  with DataCite, not Crossref, so the Crossref miss is expected. The page states no
  peer-reviewed venue. The proposal already marks this reference as "a preprint, and read
  as such" — **correct handling, Tier C.**

Three non-DOI references carrying the core argument were additionally verified against
authoritative proceedings records:

| Ref | Verification route | Outcome |
| --- | --- | --- |
| [60] Verma, Barrejón & Nalisnick | PMLR v206 proceedings page | Verified. Pages 11415–11434 match exactly. |
| [61] Mao, Mohri, Mohri & Zhong | NeurIPS 2023 proceedings record | Venue, authors and year verified. **Page range 3578–3606 not confirmed** — recheck. |
| [54] Smyth & Keane | IJCAI proceedings index for 1995 | Conference ordinal confirmed as the *Fourteenth* IJCAI, 1995; start page 377 confirmed. **ACM DL gives 377–382 against the proposal's 377–383** — reconcile. |

**Total references re-verified in this audit against an external record: 54 of 68.**

The remaining 14 are non-DOI items ([1], [11], [34]–[40], [43], [47], [56], [58], [62])
which were **not re-verified here** and remain covered only by the proposal's own August
audit file, which is absent from the repository (§1.2). They should be brought under
version control before the reviewer relies on the 67-of-68 figure.

### 2.3 Year and venue consistency

Two apparent year discrepancies were checked and are **not defects**:

- **[55] Ben-David et al.** Proposal 2010; Crossref 2009. The journal issue (*Machine
  Learning* 79(1–2)) is 2010; 2009 is the online-first date. Citing the issue year is
  correct practice.
- **[32] Alfrink et al.** Proposal 2023 (vol. 33, no. 4); Crossref 2022 online-first.
  Same pattern, same conclusion.

No duplicate DOI and no duplicate title was found in the reference list. Every DOI is
distinct; every title is distinct.

### 2.4 What the audit added

Twenty-eight high-priority papers were identified, verified and extracted
(`literature/2026-09-06-high-priority-literature-map.csv`); 35 candidate refuters were
assessed (`literature/2026-09-06-gap-refutation-matrix.csv`). Of the 28 mapped papers,
24 are Tier A and 4 are Tier B. **No Tier C or Tier D source supports any
presence-or-absence conclusion in this audit.** The single Tier C item discussed
(arXiv:2606.13174) is marked as a preprint throughout and carries no absence claim.

---

## 3. QL-01 audit — human–agent collaboration

### 3.1 Registered terms reproduced

- **Narrow phrases, run unrestricted across title, abstract and keywords:**
  mixed initiative · human-in-the-loop · human-on-the-loop · complementary performance ·
  meaningful human control
- **Generic terms, title and author-keyword fields only, AND the QL-05 substrate block:**
  human oversight · decision authority

### 3.2 Terms that are too broad

`human-in-the-loop` is registered as a narrow phrase but is not precise in the sense
§4.3 requires. It is a field label attached to a very large and heterogeneous literature,
and run unrestricted across title, abstract and keywords it will dominate the QL-01
union. It should either move to the generic class or, better, be retained as narrow but
paired with a pre-declared volume ceiling and the one-step tightening rule §4.3 already
specifies.

### 3.3 Missing synonyms

`human-AI collaboration`, `human-agent teaming`, `human-machine teaming`,
`hybrid intelligence`, `human-AI complementarity`, `appropriate reliance`,
`overreliance`, `algorithm aversion`, `adjustable autonomy`, `shared autonomy`,
`supervisory control`, `levels of automation`.

The most consequential omission is **`delegation`** and **`human-AI delegation`**. The
information-systems delegation literature is directly on QL-01's subject — who should
decide, and whether the human or the system should hold that choice — and its central
empirical result is that humans misjudge their own competence badly enough that letting
the system hold the delegation decision produces better joint outcomes (Fügener et al.,
*Information Systems Research* 33(2):678–696, 2022, doi:10.1287/isre.2021.1079). No
registered QL-01 term retrieves it: it uses neither "mixed initiative" nor
"human-in-the-loop" nor "complementary performance" as its vocabulary. This paper
directly supports the proposal's own presence-is-not-expertise distinction, so the gap
is a missed *support*, not a missed refuter — but it demonstrates the vocabulary hole.

### 3.4 Terminology from adjacent fields the current vocabulary would miss

Organisational and management vocabulary for the same concept: `decision rights`,
`delegation of authority`, `span of control`, `accountability structure`. QL-01's
`decision authority` is the nearest registered term, and it sits in the generic class.

### 3.5 Are the current field restrictions defensible?

Partly. Restricting `human oversight` to title and keyword fields is defensible: run
against abstracts it would retrieve a large part of the AI-governance literature.
Restricting **`decision authority`** the same way is **not defensible**, for two
compounding reasons. First, it is a two-word phrase with substantially more precision
than `human oversight`, so on the protocol's own stated criterion it belongs in the
narrow class. Second, conjoining it with the QL-05 substrate block means a retrieved
record must mention both decision authority *and* domain models, conceptual models,
automated grading or computer-interpretable guidelines. No paper in the authority
literature satisfies that conjunction. The registered form of this term retrieves
approximately nothing, and its presence in the protocol creates a false impression that
authority has been searched for.

### 3.6 Recommended frozen revision

1. Move `decision authority` to the narrow class, unrestricted.
2. Add to narrow: `human-AI delegation`, `hybrid intelligence`,
   `human-agent teaming`, `appropriate reliance`, `adjustable autonomy`.
3. Add to generic: `human-AI collaboration`, `overreliance`, `decision rights`.
4. Retain `human oversight` as generic with the substrate conjunction, and additionally
   run it once in QL-06 (§18) without the conjunction, capped.
5. Declare a per-database volume ceiling for `human-in-the-loop` before execution.

---

## 4. QL-02 audit — selective intervention

### 4.1 Registered terms reproduced

- **Narrow, unrestricted:** learning to defer · selective prediction · reject option ·
  value of information · expert routing · reviewer workload · alert fatigue ·
  interruption cost · work item allocation
- **Generic, title/keyword only, AND substrate block:** abstention · active learning ·
  uncertainty estimation · clarification · task assignment · resource allocation

### 4.2 Terms that are too broad

None of the narrow phrases is objectionably broad. This family's narrow set is the
best-constructed of the five.

### 4.3 Missing synonyms — including one that would miss the proposal's own reference

**`selective classification` is absent.** Proposal reference [34] is Geifman &
El-Yaniv, "Selective Classification for Deep Neural Networks" (NeurIPS 30, 2017). Its
title, and the vocabulary of the modern literature descending from it, use *selective
classification*, not *selective prediction*. A registered protocol that cannot retrieve
a paper the proposal already relies on is demonstrably under-specified. This is the
clearest single vocabulary defect in the protocol.

Also missing: `multi-expert deferral`, `deferral`, `expert deferral`,
`algorithmic triage`, `triage`, `risk-coverage`, `selective risk`, `coverage`,
`conformal prediction`, `escalation`, `escalation policy`.

`escalation` deserves specific comment. Study 1's proposed artefact maps a claim-bearing
event onto six actions, several of which are escalations, and the BPM literature
formalises exactly this under that word (van der Aalst, Rosemann & Dumas,
*Decision Support Systems* 43(2):492–511, 2007, doi:10.1016/j.dss.2006.11.005). The
protocol contains no term that retrieves it.

`learning to defer` as an exact phrase **does** retrieve the multi-expert deferral
papers [60] and [61], because both carry the phrase in their titles. That part of the
protocol works, and it is why the strongest GAP-1 competitors were reachable at all.

### 4.4 Terminology from adjacent fields the current vocabulary would miss

The BPM resource-perspective vocabulary: `work item distribution` (BPM's own term —
the protocol registers `work item allocation`, which is markedly less common in that
literature), `capability-based distribution`, `role-based distribution`,
`separation of duties`, `binding of duties`, `authorization constraint`,
`workflow resource`, `organizational model`, `resource behaviour`.

Crowdsourcing and review-system vocabulary: `task routing`, `worker selection`,
`reviewer assignment`, `paper-reviewer assignment`, `expertise matching`.

### 4.5 Are the current field restrictions defensible?

**No — this is where the substrate conjunction does the most damage.** `resource
allocation` and `task assignment` are the two principal entry terms into the
business-process resource-allocation literature, and both are in the generic class,
which means both are conjoined with the QL-05 substrate block. The consequence is
precise and demonstrable: the following, all verified in this audit as serious GAP-1
competitors, **cannot be retrieved by the protocol as registered**:

| Competitor | Why the protocol misses it |
| --- | --- |
| Pufahl, Stiehle, Ihde, Weske & Weber, *Information Systems* 2025, doi:10.1016/j.is.2025.102541 — systematic review of 61 resource-allocation studies | `resource allocation` is generic; the paper does not mention the substrate |
| Russell, van der Aalst, ter Hofstede & Edmond, CAiSE 2005, doi:10.1007/11431855_16 — capability-based distribution **and** authorisation **and** separation of duties in one catalogue | no narrow term matches; `resource allocation` conjunction fails |
| Bertino, Ferrari & Atluri, ACM TISSEC 2(1):65–104, 1999, doi:10.1145/300830.300837 — formal task-level authorisation with separation of duty | no narrow term matches |
| Arias, Rojas, Muñoz-Gama & Sepúlveda, doi:10.1007/978-3-319-42887-1_37 — allocation from mined performance evidence | `resource allocation` conjunction fails |

§2.6 declares business-process work-item and resource allocation a **required target**
of these searches. As registered, the searches cannot reach it. The protocol would
therefore have recorded "not reached" and the gap would have survived on a procedural
artefact rather than on evidence. §18 recommends the fix.

### 4.6 Recommended frozen revision

1. Add to narrow: `selective classification`, `multi-expert deferral`,
   `algorithmic triage`, `risk-coverage`, `escalation policy`, `separation of duties`,
   `capability-based distribution`, `work item distribution`, `reviewer assignment`.
2. Add to generic: `deferral`, `triage`, `escalation`, `expertise matching`.
3. Route `resource allocation` and `task assignment` through QL-06 (§18) **without**
   the substrate conjunction, capped and screened, in addition to their current
   substrate-conjoined form.

---

## 5. QL-03 audit — judgment representation and governance

### 5.1 Registered terms reproduced

- **Narrow, unrestricted:** rationale capture · explanatory debugging ·
  interactive machine learning · annotation disagreement · contestability ·
  knowledge-base curation · truth maintenance · belief revision · ontology evolution
- **Generic, title/keyword only, AND substrate block:** provenance · adjudication ·
  versioning · expiry · supersession · revocation

### 5.2 What this family gets right

Registering `knowledge-base curation`, `truth maintenance`, `belief revision` and
`ontology evolution` as **narrow, unrestricted** phrases is the protocol's single best
decision. It means the second literature §2.6 names as a likely refuter *is* reachable.
This audit confirms it is reachable and that it does contain material that narrows GAP-2
(§9.2). The proposal deserves credit for registering these before searching.

### 5.3 Terms that are too broad

`interactive machine learning` run unrestricted will retrieve a large literature only
partly concerned with judgment representation. Recommend a declared volume ceiling
rather than reclassification, since the phrase is genuinely on-topic.

### 5.4 Missing synonyms

`nanopublication`, `micropublication`, `decision provenance`, `design rationale`,
`architecture decision record`, `argumentation`, `assertion lifecycle`,
`temporal validity`, `valid time`, `audit trail`, `traceability`,
`human label variation`, `inter-annotator agreement`, `retraction`,
`knowledge graph curation`.

Four of these matter materially, because each names a verified GAP-2 competitor the
registered vocabulary cannot reach:

| Missing term | Competitor it would retrieve |
| --- | --- |
| `micropublication` | Clark, Ciccarese & Goble, *J. Biomed. Semantics* 5:28, 2014, doi:10.1186/2041-1480-5-28 — claim-level record with argument, attribution, provenance and **explicitly retained challenge and disagreement** |
| `nanopublication` | Groth, Gibson & Velterop, doi:10.3233/isu-2010-0613 — assertion + provenance + publication info, immutable and version-exact |
| `decision provenance` | Singh, Cobbe & Norval, *IEEE Access* 7:6562–6574, 2019, doi:10.1109/access.2018.2887201 |
| `design rationale` / `architecture decision record` | MacLean et al., *HCI* 6(3–4):201–250, 1991, doi:10.1207/s15327051hci0603&4_2; Jansen & Bosch, WICSA 2005, doi:10.1109/wicsa.2005.61; Tyree & Akerman, *IEEE Software* 22(2):19–27, 2005, doi:10.1109/ms.2005.27 |

### 5.5 Terminology from adjacent fields the current vocabulary would miss

Database and semantic-web vocabulary for the lifecycle half: `temporal RDF`,
`valid-time`, `bitemporal`, `assertion validity`, `graph versioning`. Verified
competitor: Gutierrez, Hurtado & Vaisman, *IEEE TKDE* 19(2):207–218, 2007,
doi:10.1109/tkde.2007.34, which gives assertions explicit validity intervals — a
lifecycle state that lapses on a stated condition.

Software-engineering vocabulary for the rationale half: `decision record`,
`ADR`, `design decision`, `knowledge management in software architecture`.

### 5.6 Are the current field restrictions defensible?

**No, for `provenance` specifically.** Placing `provenance` in the generic class with
the substrate conjunction means a retrieved record must mention provenance *and* the
modelling-or-guideline substrate. PROV-DM (proposal reference [47]), decision provenance,
nanopublications and micropublications all fail that conjunction. As with `resource
allocation` in QL-02, the protocol as registered cannot retrieve the literature the
proposal's own argument turns on. `versioning`, `expiry`, `supersession` and
`revocation` are correctly generic — each is a single common word that would otherwise
flood the union — but they too need an unconjoined route in QL-06 to be useful.

### 5.7 Recommended frozen revision

1. Add to narrow: `nanopublication`, `micropublication`, `decision provenance`,
   `design rationale`, `architecture decision record`, `temporal validity`,
   `human label variation`, `assertion lifecycle`.
2. Move `provenance` to narrow, unrestricted, with a declared volume ceiling; or run it
   unconjoined in QL-06.
3. Add to generic: `argumentation`, `audit trail`, `retraction`, `valid time`.
4. Declare a volume ceiling for `interactive machine learning`.

---

## 6. QL-04 audit — reuse and transfer

### 6.1 Registered terms reproduced

- **Narrow, unrestricted:** case-based reasoning · retrieval-augmented generation ·
  agent memory · correction persistence · attribute-based access control ·
  domain adaptation · distribution shift · transportability · guideline adaptation
- **Generic, title/keyword only, AND substrate block:** access control · transfer learning

### 6.2 Terms that are too broad

`case-based reasoning` and `domain adaptation` are both field labels rather than precise
phrases, and both will contribute large volume when run unrestricted. Both are
genuinely on-topic, so recommend declared ceilings rather than reclassification.

### 6.3 Missing synonyms

`lessons learned`, `organizational memory`, `experience factory`, `experience reuse`,
`knowledge reuse`, `case-base maintenance`, `case provenance`,
`competence-preserving deletion`, `cross-project`, `cross-company`,
`defect prediction`, `duplicate bug report`, `crash report`, `failure signature`,
`permission-aware retrieval`, `policy-governed retrieval`, `capability evaluation`,
`generalization gap`.

Three clusters matter:

| Missing cluster | Competitor it would retrieve | Effect |
| --- | --- | --- |
| `lessons learned`, `organizational memory`, `experience reuse` | Weber, Aha & Becerra-Fernandez, *ESWA* 20(1):17–34, 2001, doi:10.1016/s0957-4174(00)00046-4 | An entire required SQ3 adjacent literature, absent from the anchor set, whose central finding — recorded lessons do not influence later decisions unless delivery is embedded in the decision process — prefigures the proposal's own enforcement-consequence argument |
| `cross-project`, `cross-company`, `defect prediction` | Zimmermann et al., ESEC/FSE 2009, doi:10.1145/1595696.1595713; Turhan et al., *EMSE* 14(5):540–578, 2009, doi:10.1007/s10664-008-9103-7 | The strongest challenge to GAP-3's methodological novelty: per-pair transfer testing against independent target evidence is established SE practice |
| `case provenance`, `case-base maintenance` | Leake & Whitehead, ICCBR 2007, doi:10.1007/978-3-540-74141-1_14; Leake & Wilson, EWCBR 1998, doi:10.1007/bfb0056333 | Narrows the claim that CBR maintenance decides only whole-store competence |

### 6.4 Terminology from adjacent fields the current vocabulary would miss

Empirical software engineering's transfer vocabulary (`cross-project`, `cross-company`,
`within-project`) is entirely absent, and `transfer learning` — the one registered term
that might reach it — is in the generic class and therefore substrate-conjoined. SE
defect-prediction papers do not mention domain models or clinical guidelines, so the
conjunction fails.

### 6.5 Are the current field restrictions defensible?

Mixed. `access control` as a generic term is defensible in itself, and the loss is
mitigated because `attribute-based access control` is registered narrow — which is why
this audit could reach the 2025 access-control-aware retrieval work
(doi:10.1145/3672608.3707848; doi:10.1145/3769002.3769952) via the narrow phrase
`retrieval-augmented generation` instead. `transfer learning` as generic is **not**
defensible for the same structural reason as `resource allocation` and `provenance`: it
is the only route to the SE transfer literature and the conjunction closes it.

### 6.6 Recommended frozen revision

1. Add to narrow: `lessons learned`, `organizational memory`, `experience factory`,
   `case-base maintenance`, `case provenance`, `cross-project defect prediction`,
   `permission-aware retrieval`, `failure signature`.
2. Add to generic: `experience reuse`, `knowledge reuse`, `duplicate bug report`,
   `capability evaluation`.
3. Route `transfer learning` and `access control` through QL-06 unconjoined, capped.
4. Declare ceilings for `case-based reasoning` and `domain adaptation`.

---

## 7. QL-05 audit — substrate (runs alone)

### 7.1 Registered terms reproduced

- **Narrow, unrestricted:** domain model · conceptual model · model assessment ·
  automated grading · LLM-based assessment · computer-interpretable guideline ·
  guideline operationalization
- **Generic:** none — this family supplies the conjunction block for QL-01 to QL-04.

### 7.2 Terms that are too broad — a term-class error

`domain model` and `conceptual model` are registered as **narrow** phrases on the
ground that "precision is carried by the phrase itself." Neither satisfies that test.
`domain model` is used across software engineering, machine learning, simulation,
linguistics and economics, and run unrestricted across title, abstract and keywords it
will return very large volumes with low precision. `model assessment` is worse still,
because in statistics and machine learning it denotes model *evaluation* generally.

This misclassification has an amplified effect that a reader might not notice: because
QL-05 is the conjunction block for the other four families, **every** generic term in
QL-01 to QL-04 inherits QL-05's imprecision. A loose substrate block does not merely
inflate QL-05; it degrades the precision of the substrate-conjoined half of the entire
protocol while still excluding the adjacent literatures (§§4.5, 5.6, 6.5).

### 7.3 Missing synonyms

`class diagram`, `UML`, `metamodel`, `model-driven engineering`, `variability model`,
`software product line`, `conformance checking`, `automated assessment`, `rubric`,
`clinical decision support`, `CDSS`, `Arden syntax`, `GLIF`, `clinical guideline`.

The absence of `UML` and `class diagram` is notable: proposal references [11], [12] and
[14] are all class-diagram assessment papers, and [15] is explicitly about UML.

### 7.4 Terminology from adjacent fields the current vocabulary would miss

The medical-informatics substrate vocabulary is under-represented. `computer-interpretable
guideline` and `guideline operationalization` are registered, but `clinical decision
support`, `CDSS` and `clinical guideline` are not — and those are the terms references
[7], [8], [44] and [45] actually use. If the Plan A medical branch is ever activated, the
substrate block will not reach its own literature.

### 7.5 Are the current field restrictions defensible?

QL-05 running alone and unrestricted is defensible as a design, because it is the
substrate family and needs recall. What is not defensible is doing so with two very
broad phrases while simultaneously using the family as a precision filter for four other
families. A substrate block used as a conjunction should be *tighter* than a substrate
family used for standalone recall. Recommend splitting the two roles.

### 7.6 Recommended frozen revision

1. Split QL-05 into two registered artefacts with the same provenance:
   **QL-05-R (recall)**, run alone, retaining all seven current phrases plus the
   additions in §7.3; and **QL-05-C (conjunction block)**, a deliberately tighter set
   used only as the AND-block for generic terms:
   `domain model` · `conceptual model` · `class diagram` · `UML` · `metamodel` ·
   `model-driven engineering` · `automated grading` · `model assessment` ·
   `computer-interpretable guideline` · `guideline operationalization` ·
   `clinical decision support`.
2. Add to QL-05-R: `class diagram`, `UML`, `metamodel`, `model-driven engineering`,
   `variability model`, `conformance checking`, `clinical decision support`, `CDSS`,
   `clinical guideline`.
3. Declare volume ceilings for `domain model`, `conceptual model` and `model assessment`.

---

## 8. Missing vocabulary — consolidated

Terms absent from the registered protocol, grouped by the gap they bear on. Terms marked
**★** are those whose absence demonstrably prevents retrieval of a competitor this audit
verified.

**GAP-1 / SQ1 — routing by competence and authority**
★ `selective classification` · ★ `separation of duties` · ★ `capability-based distribution` ·
★ `work item distribution` · ★ `escalation policy` · ★ `human-AI delegation` ·
`multi-expert deferral` · `deferral` · `expert deferral` · `algorithmic triage` · `triage` ·
`risk-coverage` · `selective risk` · `coverage` · `conformal prediction` · `escalation` ·
`binding of duties` · `authorization constraint` · `workflow resource` ·
`organizational model` · `resource behaviour` · `role-based distribution` ·
`reviewer assignment` · `paper-reviewer assignment` · `expertise matching` ·
`task routing` · `worker selection` · `decision rights` · `delegation of authority` ·
`hybrid intelligence` · `human-agent teaming` · `human-machine teaming` ·
`human-AI collaboration` · `appropriate reliance` · `overreliance` · `algorithm aversion` ·
`adjustable autonomy` · `shared autonomy` · `supervisory control` · `levels of automation`

**GAP-2 / SQ2 — governed judgment record and lifecycle**
★ `micropublication` · ★ `nanopublication` · ★ `decision provenance` · ★ `design rationale` ·
★ `architecture decision record` · ★ `temporal validity` · `assertion lifecycle` ·
`valid time` · `bitemporal` · `assertion validity` · `graph versioning` · `temporal RDF` ·
`argumentation` · `audit trail` · `traceability` · `retraction` ·
`human label variation` · `inter-annotator agreement` · `knowledge graph curation` ·
`decision record` · `ADR` · `design decision`

**GAP-3 / SQ3 — controlled reuse and capability-gap classification**
★ `lessons learned` · ★ `organizational memory` · ★ `cross-project defect prediction` ·
★ `cross-company` · ★ `case provenance` · ★ `case-base maintenance` ·
★ `permission-aware retrieval` · `experience factory` · `experience reuse` ·
`knowledge reuse` · `competence-preserving deletion` · `defect prediction` ·
`duplicate bug report` · `crash report` · `failure signature` ·
`policy-governed retrieval` · `capability evaluation` · `generalization gap`

**QL-05 substrate**
`class diagram` · `UML` · `metamodel` · `model-driven engineering` · `variability model` ·
`software product line` · `conformance checking` · `automated assessment` · `rubric` ·
`clinical decision support` · `CDSS` · `Arden syntax` · `GLIF` · `clinical guideline`

---

## 9. Adjacent fields

The proposal mandates four adjacent searches. All four were attempted at reconnaissance
depth in this audit. None was searched to systematic depth, because the primary databases
were inaccessible (§10.3).

### 9.1 A. Business process / workflow resource allocation — SEARCHED, GAP NARROWED

**Question posed:** does any approach jointly represent claim-or-task-specific competence
**and** authority?

**Answer: yes for the task-specific case, and it has been the case since 2005.** The
workflow resource-pattern catalogue (Russell et al., CAiSE 2005,
doi:10.1007/11431855_16) contains, in one framework, *Capability-Based Distribution*
(match the participant's declared capabilities against the work item),
*Authorisation* (specify the range of resources permitted to execute it),
*Separation of Duties* and *Role-Based Distribution*. Authority is additionally
formalised and enforced in Bertino, Ferrari & Atluri (ACM TISSEC 2(1):65–104, 1999,
doi:10.1145/300830.300837), and both capability and organisational position are jointly
expressible in the RAL/RALph resource-assignment languages
(doi:10.1007/978-3-642-28108-2_5; doi:10.1007/978-3-319-19069-3_4).

**Two residual differences survive, and they are substantive.** First, BPM capability is
**declared** and matched by predicate satisfaction, not **assessed** from evidence for
the specific item. The nearest BPM approach to assessed competence derives allocation
recommendations from mined event-log performance (doi:10.1007/978-3-319-42887-1_37), and
that work does not jointly model authority. Second, and decisively, the field's own 2025
systematic review of 61 primary studies (Pufahl, Stiehle, Ihde, Weske & Weber,
*Information Systems*, doi:10.1016/j.is.2025.102541) reports that reviewed approaches are
**predominantly rule-based and process-oriented**, mostly 1-to-1 allocations, and calls
explicitly for **evidence-oriented allocation methods** and **comparative benchmarking**.
The adjacent literature's own review therefore identifies the absence of the two
properties GAP-1's residual now rests on.

**Effect: GAP-1 is NARROWED, not refuted.** The proposal must stop claiming that
competence and authority are not represented together, and must claim instead that
assessed, claim-specific competence has not been combined with authority in an evaluated
routing policy at a matched attention budget.

### 9.2 B. Knowledge-base curation / truth maintenance / belief revision — SEARCHED, GAP NARROWED

**Question posed:** does this literature already provide most or all of SQ2's proposed
governed-judgment lifecycle?

**Answer: it provides most of the lifecycle mechanics, and the proposal's §2.4
characterisation of provenance understates this.** §2.4 states that provenance "supplies
neither the reasons a judgment lapses, nor conditions on who may declare it, nor any
consequence obliging an invalidated judgment to stop influencing decisions." That is true
of PROV-DM. It is **not** true of the literature §2.6 itself names:

| SQ2 lifecycle element | Provided by | Reference |
| --- | --- | --- |
| Reason-conditioned lapse and automatic withdrawal | Truth maintenance — a belief loses status when its justification is withdrawn, via dependency-directed backtracking | Doyle, *AI* 12(3):231–272, 1979, doi:10.1016/0004-3702(79)90008-0 |
| Retained conflicting conclusions **with** their scope of validity | Assumption-based TMS — all consistent contexts maintained concurrently, each labelled by its assumption set | de Kleer, *AI* 28(2):127–162, 1986, doi:10.1016/0004-3702(86)90080-9 |
| Principled supersession — which commitment yields | AGM belief revision, with epistemic entrenchment | Alchourrón, Gärdenfors & Makinson, *JSL* 50(2):510–530, 1985, doi:10.2307/2274239 |
| Versioning and change management over stored knowledge | Ontology change and evolution surveys | doi:10.1017/s0269888908001367; doi:10.1017/s0269888913000349 |
| Lifecycle state that lapses on a stated condition | Temporal RDF validity intervals | Gutierrez, Hurtado & Vaisman, *IEEE TKDE* 19(2):207–218, 2007, doi:10.1109/tkde.2007.34 |

Additionally, and outside the two literatures §2.6 names, **claim-level records with
rationale, provenance and retained disagreement already exist**: micropublications
(doi:10.1186/2041-1480-5-28) model a claim with its attribution, evidence, connecting
argument, and explicitly represented challenge and opposition; nanopublications
(doi:10.3233/isu-2010-0613) give version-exact claim-level provenance.

**Residual after this search:** no identified record attaches **assessed competence** and
**authority as a mandate** to a claim-level judgment, and no identified lifecycle lapse
condition is keyed to anything other than time or logical support — none lapses on
"the governing policy changed", "the mandate was withdrawn", or "a more authorised
reviewer challenged it". No identified record has been evaluated for blind
reconstructability at a measured capture cost.

**Effect: GAP-2 is NARROWED.** The §2.4 sentence "No record format combines
reasoning-level content, scope, authority, retained disagreement, and a lifecycle at
claim level" must be narrowed, and the claim that the lifecycle is "the dimension least
covered" must be withdrawn — on this evidence it is among the better-covered dimensions.

### 9.3 C. Organisational / case memory — SEARCHED, GAP NARROWED

Lessons-learned systems (Weber, Aha & Becerra-Fernandez, *ESWA* 20(1):17–34, 2001,
doi:10.1016/s0957-4174(00)00046-4) describe a lesson lifecycle including explicit
**verification** before storage and **delivery** into a later decision, and report that
recorded experience does not influence later decisions unless delivery is embedded in the
decision process. Case provenance (doi:10.1007/978-3-540-74141-1_14) records case sources
and uses them in later retrieval and retention decisions. Case-base maintenance
(doi:10.1007/bfb0056333) supplies the established policy vocabulary.

**Residual:** lessons are organisation-level narrative records, not claim-level judgments;
no authorisation, no lapse condition, no independent target-evidence test, and no
quirk-versus-capability-gap classification.

### 9.4 D. Human expert routing in medicine / crowdsourcing / review systems — SEARCHED, LIMITED TRANSFER

Reviewer-assignment and crowdsourcing task-routing systems match declared or estimated
expertise to a specific item, and conference systems additionally enforce
conflict-of-interest exclusions — which is an eligibility constraint, structurally
adjacent to authority. This is the weakest of the four adjacent searches and the least
methodologically transferable: conflict-of-interest is a *negative* eligibility filter,
not a positive mandate to decide, and the assignment objective is load-balanced coverage
rather than correctness on a contested claim. Two candidate anchors
(Toronto Paper Matching System; Whitehill et al., NeurIPS 2009) could **not** be verified
in Crossref, which does not index those venues for those years, and are therefore **not**
carried into the deliverables. Recorded here as an open search line, not as evidence.

### 9.5 One further adjacent finding, outside the mandated four

An adversarial search for authority-and-competence conjunctions surfaced a **binding
regulatory requirement** that conjoins them explicitly:

> Regulation (EU) 2024/1689 (Artificial Intelligence Act), Article 26(2):
> "Deployers shall assign human oversight to natural persons who have the necessary
> competence, training and authority, as well as the necessary support."

This is a Tier A authoritative standard. It does not refute GAP-1 — it supplies no
mechanism, no per-claim selection procedure and no evaluation — but it removes any claim
that the competence-plus-authority conjunction is conceptually novel, and it strengthens
the practical motivation for Study 1 considerably. It should be cited in Chapter 2.

The same search returned predominantly Tier D material (consultancy blogs, vendor
governance pages). Per §7 of the audit brief, **none of it is used to support any
presence-or-absence claim**, and it is recorded here only to note that the query's
precision was poor.

---

## 10. Database strategy

### 10.1 The proposal's current roles — assessment

| Source | Current role | Assessment |
| --- | --- | --- |
| ACM Digital Library | Primary | Defensible and necessary. Reference [13] demonstrates ACM records exist that Crossref does not index, so ACM DL cannot be substituted by a metadata registry. |
| IEEE Xplore | Primary | Defensible. |
| Scopus | Primary | Defensible, subject to institutional entitlement (§10.3). |
| Web of Science | Primary | Defensible, subject to entitlement. Overlaps Scopus heavily; its distinct value is citation-network corroboration rather than additional recall. |
| PubMed | Conditional, medical branch only | Defensible and correctly gated. Appendix B records zero of six medical entry gates satisfied, so the branch is dormant. |
| Google Scholar | Snowballing only, never primary | **Correct, and should be preserved verbatim.** Non-reproducible result sets and no stable export make it unusable as a primary source. |

### 10.2 The six sources the brief asks to be evaluated

None should be promoted to a primary database. Each has a defensible non-primary role.

| Source | Recommended role | Reason |
| --- | --- | --- |
| **DBLP** | Discovery aid + venue/ordinal verification; completeness cross-check | Bibliographic metadata only, with **no abstract field**. Title/abstract/keyword queries are structurally impossible, so it cannot execute the registered protocol. Excellent for confirming a venue, an ordinal or an author's full publication list. |
| **Semantic Scholar** | Discovery aid + forward/backward citation snowballing | Corpus composition is not editorially controlled and abstract coverage is uneven; mixes preprints with peer-reviewed records without a reliable venue-quality signal. Strong citation graph makes it a good snowballing instrument under Wohlin's guidelines. |
| **Crossref** | **Verification registry only** — identity, DOI, venue, year, type, pages; duplicate-DOI detection | Not a search database: no reliable abstract or author-keyword fields, and deposits are publisher-dependent. Reference [13] is the concrete proof that Crossref coverage gaps exist for indexed ACM proceedings. Used in exactly this role in this audit (§2.2). |
| **OpenAlex** | Discovery aid + coverage cross-check + abstract retrieval where publisher access is blocked | Inherits Crossref/MAG lineage and includes non-peer-reviewed records; type and venue fields are occasionally wrong. Its search ranking is also demonstrably noisy — a title search for a known paper returned four irrelevant works above it in this audit. Useful, not authoritative. |
| **SpringerLink** | Full-text retrieval + verification | Publisher-scoped. Promoting it to primary would bias the corpus toward one publisher's imprints (LNCS, LNBIP), which is precisely where much BPM and CBR work sits — a bias that would look like a finding. |
| **ScienceDirect** | Full-text retrieval + verification | Same reasoning. Returned HTTP 403 to automated access in this audit. |

**Rule to freeze:** a discovery engine or metadata registry may generate candidates and
may verify identity, but every included record must be attributable to a primary-database
query line or to a documented snowballing chain. No candidate enters the corpus with
"found via OpenAlex" as its only provenance.

### 10.3 Database access limitations in this audit — ACCESS BLOCKED

| Source | Status in this audit |
| --- | --- |
| ACM Digital Library | **ACCESS BLOCKED** — no subscription/API search access. One record page reached via web search for verification of [13]. No query executed, no count. |
| IEEE Xplore | **ACCESS BLOCKED** — no subscription/API search access. |
| Scopus | **ACCESS BLOCKED** — requires institutional entitlement and API key; neither available. |
| Web of Science | **ACCESS BLOCKED** — same. |
| PubMed | **NOT ATTEMPTED** — medical branch dormant; attempting it would misrepresent the Plan A gate status. |
| Crossref REST API | **REACHABLE** from the shell. Used for all bibliographic verification. |
| OpenAlex API | **BLOCKED from the shell** (HTTP 000, corporate proxy); **reachable** via the WebFetch tool. Used for abstract retrieval. |
| DBLP API | **ACCESS BLOCKED** from the shell (HTTP 000, corporate proxy). |
| Semantic Scholar API | **ACCESS BLOCKED** from the shell (HTTP 000, corporate proxy). |
| arXiv API | **ACCESS BLOCKED** from the shell (HTTP 000); abstract pages reachable via WebFetch. |
| doi.org resolver, DataCite API | **ACCESS BLOCKED** from the shell (HTTP 000). |
| ScienceDirect | **ACCESS BLOCKED** — HTTP 403 to automated access. |
| SpringerLink | **PARTIAL** — redirects to an authentication endpoint for full text; Crossref metadata used instead. |

**Consequence, stated plainly:** the four primary databases were all inaccessible.
This audit therefore executed **no registered protocol query and produced no screening
count**. It is a targeted, adversarial verification exercise over a candidate set built
from domain knowledge and from Crossref/OpenAlex/web discovery. It can establish that a
competitor **exists** — and it did so, 35 times — but it cannot establish that a
competitor does **not** exist. Every gap verdict below is therefore expressed as
"narrowed" or "supported within the executed corpus", never as proven absence.

---

## 11. Search window

The registered window is 2015–2026 with a documented snowballing exception for
foundational work. **The window is defensible and should be retained.** The exception
mechanism is also correctly specified: each pre-window entrant records its entry point.

The proposal already names five pre-2015 lineages requiring the exception: mixed
initiative, case-based reasoning, computer-interpretable guidelines, active learning, and
transfer/domain adaptation theory. To these, this audit's findings add **eight further
pre-2015 entrants that are load-bearing for the gap argument** and must be pre-registered
with entry points rather than discovered during screening:

| Entrant | Year | Bears on | Entry point |
| --- | ---: | --- | --- |
| Doyle, truth maintenance, doi:10.1016/0004-3702(79)90008-0 | 1979 | GAP-2 lifecycle | Named target, §2.6 |
| de Kleer, assumption-based TMS, doi:10.1016/0004-3702(86)90080-9 | 1986 | GAP-2 scope + retained disagreement | Backward from Doyle |
| Alchourrón, Gärdenfors & Makinson, doi:10.2307/2274239 | 1985 | GAP-2 supersession | Named target, §2.6 |
| Conklin & Begeman, gIBIS, doi:10.1145/58566.59297 | 1988 | GAP-2 retained disagreement | Backward from rationale capture |
| MacLean et al., QOC, doi:10.1207/s15327051hci0603&4_2 | 1991 | GAP-2 rationale | Backward from rationale capture |
| Sandhu et al., RBAC, doi:10.1109/2.485845 | 1996 | GAP-1 authority | Backward from ABAC [59] |
| Bertino, Ferrari & Atluri, doi:10.1145/300830.300837 | 1999 | GAP-1 authority | Backward from BPM allocation |
| Weber, Aha & Becerra-Fernandez, doi:10.1016/s0957-4174(00)00046-4 | 2001 | GAP-3 organisational memory | Adjacent-field search |

Note that Russell et al. (2005) and Cabanillas et al. (2012, 2015) fall **inside** the
window and require no exception — they were missed by vocabulary, not by date. Two of the
eight above (Doyle, AGM) are already named as required targets in §2.6, so their
pre-window status is a protocol bookkeeping matter rather than a new decision.

---

## 12. Inclusion / exclusion rules

The rules in `literature-review-protocol.md` are sound in structure: verified identity and
venue; extractable objective, method, evidence, results, conclusions and limitations;
relevance to at least one SQ, construct, method, metric, threat or transfer boundary;
permissible access. Exclusion requires a controlled reason. Tool documentation is kept
in a separate register and is explicitly not research evidence. `Needs verification` is
explicitly not `Included`. All of this should be retained.

Four amendments are required to make the rules capable of settling the gap questions.

**12.1 Add a source-tier field and a tier rule.** The protocol currently distinguishes
publication *types* but has no quality tier. Freeze the brief's four tiers —
A (peer-reviewed journal / major conference / authoritative standard),
B (peer-reviewed workshop / recognised venue / strong technical report),
C (preprint), D (blog / company page / unreviewed web material) — and freeze two rules:
**gap closure relies on Tier A/B only**, and **no Tier D source may support a scholarly
presence-or-absence claim**. Tier C may identify an emerging competitor and must remain
labelled a preprint wherever it appears.

**12.2 Add a gap-relevance inclusion route.** The current rules admit a record that
"informs at least one SQ, construct, method, metric, threat, or transfer boundary." A
paper that *refutes* a gap may satisfy none of those and still be the most important
record in the corpus. Add an explicit route: a record is included if it is a candidate
refuter of GAP-1, GAP-2 or GAP-3 under the §17 protocol, whether or not it informs a
construct.

**12.3 Add the relationship-to-gap classification as a mandatory extraction field.**
Freeze the six values used in this audit: `DIRECT_PREDECESSOR`, `PARTIAL_PREDECESSOR`,
`NEAR_MISS`, `POSSIBLE_REFUTER`, `REFUTER`, `SUPPORTING_BACKGROUND`. No record is
`Included` without one.

**12.4 Add an extraction-depth field.** This audit found it indispensable and it is
absent from the workbook contract. Freeze three values: `metadata_only`,
`abstract_level`, `full_text`. A gap verdict of `REFUTED` or `PARTIALLY_REFUTED` may only
rest on a `full_text` extraction. Every row in
`literature/2026-09-06-high-priority-literature-map.csv` records this field, and **none
of the 28 rows claims `full_text`** — which is precisely why this audit's verdicts stop
at "narrowed".

---

## 13. Deduplication

The registered rule — DOI first, then normalised title/year/first-author, with manual
review of ambiguous matches — is correct and should be retained. Three additions:

**13.1 A missing DOI is not a duplicate signal and not an exclusion ground.** Reference
[13] has a valid ACM DOI that Crossref does not index. A deduplication or verification
pipeline keyed solely to Crossref resolution would have flagged a correctly cited paper
as unverifiable. Record the *verification route* alongside each identity check.

**13.2 Handle the preprint/published pair explicitly.** Several verified competitors
exist in both forms — for example Verma et al. as arXiv:2210.16955 and as PMLR
206:11415–11434. Freeze the rule: the peer-reviewed version is the record of account;
the preprint is recorded as an alternate identifier on the same row, never as a second
row. This also prevents a Tier C item silently inheriting a Tier A verdict.

**13.3 Deduplicate the cross-classified survey corpus once, at the set level.** Appendix
A.4 already establishes that the ACL-2026 branches are four cross-classifications of one
paper set (89 of 90 appear in all four branch tables), and that screening was correctly
performed once on the deduplicated set. Preserve that finding in the protocol so a later
executor does not reintroduce branch-level double counting.

---

## 14. Snowballing

Wohlin's guidelines (proposal reference [63], doi:10.1145/2601248.2601268) are the right
instrument and are correctly cited. The registered design — Google Scholar for
snowballing only, never primary, with each chain recorded — is sound.

Three amendments.

**14.1 Snowballing must not be the plan for reaching the adjacent literatures.** §4.3
already commits to this: the two named adjacent literatures are "registered here as
required targets rather than left to snowballing." That commitment is correct and this
audit shows why it must be honoured operationally — the vocabulary gaps in §§4.5, 5.6 and
6.5 mean the substrate-conjoined queries cannot reach those fields, so if the required
targets are not given their own reachable query lines they will fall back to snowballing
by default.

**14.2 Declare the start set before execution.** Wohlin's procedure is sensitive to start-set
composition and the anchor set is unevenly distributed by topic — §2.0 concedes the reuse
stream is thinnest at seven references. Freeze a start set per gap, and record it, so
that the snowballing yield can be attributed.

**14.3 Use the citation graph in both directions for the eight pre-2015 entrants.** Each
of the entrants in §11 has a large forward-citation neighbourhood that the primary window
covers but the registered vocabulary does not reach — modern work on assertion lifecycle,
provenance-bearing claim records and resource allocation cites these ancestors without
using the substrate vocabulary. Forward snowballing from the eight is the cheapest
available route to that modern work, and should be a registered step rather than an
opportunistic one.

---

## 15. Screening procedure

The registered two-stage design (title/abstract, then full text or authoritative
document), with controlled exclusion reasons and a recorded reviewer and date per
decision, is correct.

The material weakness is **single-rater screening**. Appendix B and Appendix A.4 both
disclose it honestly, and disclosure is the right first response. But three of this
audit's findings turn on judgment calls a second rater would plausibly have caught
earlier — whether multi-expert deferral conditions on the instance or on an aggregate;
whether a capability-plus-authorisation pattern catalogue counts as jointly representing
competence and authority; whether a claim-level record with retained challenge satisfies
the SQ2 record requirement. These are exactly the borderline dispositions where
single-rater screening is least reliable.

Recommended procedure, in decreasing order of cost:

1. **Dual independent screening with a computed agreement statistic** on a stratified
   sample of at least 20% of title/abstract decisions and 100% of decisions that would
   change a gap verdict, with recorded adjudication. Cohen's kappa reported per stage.
   This is Kitchenham & Charters' recommendation and the defensible target.
2. **If a second rater cannot be recruited** — Appendix B records that independent
   reviewers, raters and the implementer are not recruited, so this is the live case —
   adopt a documented substitute and name it as a limitation rather than leaving the
   single-rater status implicit: (a) blinded re-screening by the same rater after a
   declared interval, with intra-rater agreement reported; (b) mandatory full-text
   extraction for every record classified `POSSIBLE_REFUTER` or `REFUTER`; and
   (c) supervisor adjudication of every disposition that would move a gap verdict.
3. **Freeze the three-way relevance criteria before execution**, as Appendix A.4 already
   did for the survey corpus. That precedent was methodologically sound and should be
   the template.

The 63 title-level `less relevant` dispositions in the ACL-2026 screening remain
provisional, as Appendix A.4 states. They should be raised to abstract level before any
consolidated taxonomy is built on them, because the taxonomy consolidation (§4.3) takes
that classification as its first input.

---

## 16. Quality control

Retain the fit-for-purpose criteria already registered (verified identity and source
authority; transparent design and unit of analysis; appropriate comparator; data
suitability; valid metrics; stated limitations; reproducibility; transferability). Add:

**16.1 Unit-of-decision as a first-class quality dimension.** The single most
discriminating field in this audit was `unit_of_decision`. Nearly every competitor that
matched a gap on mechanism failed on unit: a prediction instance (deferral), a work item
(BPM), an assertion (TMS), a project pair (cross-project defect prediction), a retrieval
request (access-controlled RAG). Because the proposal's contribution is defined at the
level of one contested claim, unit comparability is a quality question, not just an
extraction field.

**16.2 Distinguish "does not do X" from "was not evaluated for X".** These have very
different force against a gap, and this audit had to separate them repeatedly. Temporal
RDF *does* provide a lapse condition but *was not evaluated* for judgment
reconstructability; micropublications *do* retain disagreement but *were not evaluated*
for capture cost. Freeze two extraction values rather than one.

**16.3 Verify peer-review status per record, and never infer it.** No record may be
marked peer-reviewed without a verified venue record. In this audit, 24 of 28 mapped
records are Tier A and 4 are Tier B, each with a named verification route; one record
(Kitchenham & Charters) is explicitly marked `NOT RE-VERIFIED IN THIS AUDIT`.

**16.4 Run the validation battery as a gate, not a report.** The six checks the brief
specifies — citation verification, duplicate DOI, duplicate title, year/venue
consistency, gap-claim consistency, source-tier validation — should block corpus
promotion on failure. Results for this audit are in §20.

---

## 17. Gap-refutation strategy

The proposal's refutation design is its strongest methodological feature and should be
preserved. §2.6 states the deficit as **one claim rather than a conjunction**, concedes
that a conjunctive claim "would be close to unfalsifiable, and a committee would be right
to discount it", and names, for each SQ, the specific reported finding that would remove
the need for the corresponding study. That is a genuinely falsifiable formulation and it
is what made this audit possible.

Two amendments follow from what the audit found.

**17.1 One refutation condition is currently satisfiable on a reading the proposal did
not intend, and must be tightened.** SQ2's second condition is met by "such a record
carrying a lifecycle state able to lapse on a stated condition." Temporal RDF
(doi:10.1109/tkde.2007.34) gives assertions a validity interval that lapses on a stated
condition — a date. Read literally, the condition is met. The proposal plainly intends
something stronger: a lapse keyed to a governing policy, an evidence change, or a
withdrawal of mandate. **Tighten the wording to a non-temporal, policy-or-evidence-keyed
lapse condition**, or concede the point. Leaving it as written invites a reviewer to
close SQ2 on a 2007 database paper.

**17.2 Adopt a standing refuter-hunt procedure per gap.** The procedure this audit used
worked and should be frozen:

1. For each gap, write the sentence a refuting paper's abstract would contain.
2. Enumerate the vocabularies in which that sentence could be written — including
   vocabularies the proposal does not use.
3. Search each vocabulary independently, without the substrate conjunction.
4. For each candidate, record `What_it_matches` and `What_it_does_not_match` separately,
   before assigning a verdict.
5. Assign a verdict only after both columns are filled.
6. Where the closest competitor matches on mechanism but differs on unit of decision,
   record that explicitly — it is the most common outcome and the most easily overlooked.

**17.3 Preserve the scoping language verbatim.** Chapter 2's formulations — "Within this
anchor set", "none among the ninety papers screened", "it is not a proof that no such
evidence exists anywhere" — are exactly right and must survive revision. Nothing in this
audit licenses a stronger form. Conversely, nothing in this audit licenses "no research
exists", and that phrasing appears nowhere in the current chapter.

---

## 18. Recommended frozen protocol

The following is the recommended pre-execution amendment. It is a **pre-execution**
amendment: no query has been run, so no expression is being changed after seeing results.
It should be dated, versioned and frozen with the supervisors before execution begins.

### 18.1 Structural changes

**A. Supersede the 2026-07-30 register.** Mark
`docs/research/phd-proposal/literature-search-execution-register.md` as historical and
regenerate the execution matrix from proposal §4.3 Table 3, so that exactly one
definition of QL-01 to QL-05 exists in the repository. (§1.1)

**B. Split QL-05 into QL-05-R and QL-05-C.** A recall family run alone, and a tighter
conjunction block used as the AND-block for generic terms. (§7.6)

**C. Add QL-06 — adjacent-field refuter family, run without the substrate conjunction.**
This is the central recommendation of the audit. QL-06 exists to make the two literatures
§2.6 names as required targets actually reachable, while preserving volume control by
admitting **narrow phrases only** and by carrying a declared per-database ceiling.

Proposed QL-06 narrow phrase set, frozen:

```text
QL-06a  business-process resource allocation and authority
  "work item distribution" OR "work item allocation" OR "capability-based distribution"
  OR "role-based distribution" OR "resource allocation" OR "separation of duties"
  OR "binding of duties" OR "authorization constraint" OR "workflow resource"
  OR "escalation policy" OR "decision authority" OR "decision rights"

QL-06b  assertion lifecycle, curation and claim-level records
  "truth maintenance" OR "belief revision" OR "knowledge-base curation"
  OR "ontology evolution" OR "nanopublication" OR "micropublication"
  OR "decision provenance" OR "temporal validity" OR "valid time"
  OR "assertion lifecycle" OR "design rationale" OR "architecture decision record"

QL-06c  experience reuse and transfer with target evidence
  "lessons learned" OR "organizational memory" OR "experience factory"
  OR "case-base maintenance" OR "case provenance" OR "cross-project defect prediction"
  OR "cross-company" OR "permission-aware retrieval" OR "policy-governed retrieval"
```

QL-06 runs on all four primary databases, unioned with QL-01 to QL-04 and deduplicated
before screening, exactly as the other families are. Its results are screened against the
same criteria. Its purpose is recall into adjacent vocabularies, and its ceiling is
declared before execution.

**D. Retain the two-class term scheme and the union-then-screen design.** Both are sound.
The defect is not the scheme; it is which terms were placed in which class, and the
absence of an unconjoined route for adjacent fields.

### 18.2 Term-class corrections, frozen

| Family | Move to narrow | Add to narrow | Add to generic |
| --- | --- | --- | --- |
| QL-01 | `decision authority` | `human-AI delegation`, `hybrid intelligence`, `human-agent teaming`, `appropriate reliance`, `adjustable autonomy` | `human-AI collaboration`, `overreliance`, `decision rights` |
| QL-02 | — | `selective classification`, `multi-expert deferral`, `algorithmic triage`, `risk-coverage`, `escalation policy`, `separation of duties`, `capability-based distribution`, `work item distribution`, `reviewer assignment` | `deferral`, `triage`, `escalation`, `expertise matching` |
| QL-03 | `provenance` | `nanopublication`, `micropublication`, `decision provenance`, `design rationale`, `architecture decision record`, `temporal validity`, `human label variation`, `assertion lifecycle` | `argumentation`, `audit trail`, `retraction`, `valid time` |
| QL-04 | — | `lessons learned`, `organizational memory`, `experience factory`, `case-base maintenance`, `case provenance`, `cross-project defect prediction`, `permission-aware retrieval`, `failure signature` | `experience reuse`, `knowledge reuse`, `duplicate bug report`, `capability evaluation` |
| QL-05-R | — | `class diagram`, `UML`, `metamodel`, `model-driven engineering`, `variability model`, `conformance checking`, `clinical decision support`, `CDSS`, `clinical guideline` | — |

Declared volume ceilings required before execution for: `human-in-the-loop`,
`interactive machine learning`, `case-based reasoning`, `domain adaptation`,
`domain model`, `conceptual model`, `model assessment`, and every QL-06 sub-family.

### 18.3 Process changes, frozen

1. Source-tier field with the A/B/C/D rule; Tier D may not support an absence claim. (§12.1)
2. Gap-relevance inclusion route for candidate refuters. (§12.2)
3. Mandatory `relationship_to_gap` and `extraction_depth` fields; `REFUTED` /
   `PARTIALLY_REFUTED` verdicts require `full_text`. (§12.3, §12.4)
4. Verification route recorded per identity check; Crossref non-resolution is not an
   exclusion ground. (§13.1)
5. Preprint/published pairs as one row with an alternate identifier. (§13.2)
6. Declared snowballing start set per gap; forward snowballing from the eight pre-2015
   entrants as a registered step. (§14.2, §14.3)
7. Dual screening with kappa, or the named single-rater substitute with mandatory
   full-text extraction for every candidate refuter. (§15)
8. Tighten SQ2's second refutation condition to a non-temporal lapse condition. (§17.1)
9. Standing refuter-hunt procedure per gap. (§17.2)
10. Validation battery as a promotion gate. (§16.4)
11. Bring the five Appendix B accompanying deliverables under version control. (§1.2)

### 18.4 What must not change

The scoping language of Chapter 2; the union-then-screen design; the two-class term
scheme as a scheme; the 2015–2026 window with a documented exception; Google Scholar as
snowballing-only; PubMed as gated and conditional; the separation of authors'
conclusions from the candidate's synthesis in the workbook; and the rule that an unrun
query, a seed row, a tool page or a preprint cannot establish novelty, effectiveness or
review completeness.

---

## 19. Remaining supervisor decisions

Each item below is a decision this audit cannot take.

**19.1 Freeze the amended protocol, or execute as registered and record the misses?**
The audit's recommendation is to freeze the §18 amendment first, because executing as
registered would produce a "required target not reached" record for both literatures
§2.6 names, and the gaps would then survive on a procedural artefact. Executing first and
amending later would also breach the proposal's own rule that expressions are not changed
after execution. **Recommended: amend before execution, dated and versioned.**

**19.2 How is the single-rater constraint resolved?** Appendix B records that independent
reviewers and raters are not recruited. Options: recruit a second screener; adopt the
§15.2 substitute and name it a limitation; or restrict the review's claim strength to
match single-rater evidence. This choice bounds what Chapter 2 may assert after execution.

**19.3 Which gap wording is adopted for GAP-1?** The audit establishes that the current
§2.6 wording is inaccurate about multi-expert deferral — it characterises the closest
competitor as conditioning on an aggregate competence profile when that competitor's own
abstract states it estimates per-expert correctness for the specific instance (claim audit
C-33, `LIKELY_FALSE`; framing correction at C-25). The supervisors must choose between the
replacement formulations offered there.

**19.4 Is SQ2's second refutation condition tightened?** As written, temporal RDF
arguably satisfies it (§17.1). Tightening is a substantive change to a registered
refutation condition and is a supervisor decision.

**19.5 Should the EU AI Act Article 26(2) requirement be cited in Chapter 2?** It
strengthens the motivation and removes a latent overclaim, but it also introduces a
regulatory frame the proposal currently does not use. Recommended: cite it, in §2.3,
alongside meaningful human control [31].

**19.6 Are Scopus and Web of Science actually available?** Both are ACCESS BLOCKED to
this audit. If institutional entitlement does not exist, the primary-source set must be
formally revised — with the revision recorded as a protocol amendment, not as a silent
substitution of discovery engines for primary databases.

**19.7 Does the review own the taxonomy output?** Appendix B records that no question
owns the review taxonomy (§4.3). Unchanged by this audit; still open.

**19.8 Are the 63 title-level ACL-2026 dispositions raised to abstract level before
taxonomy consolidation?** Recommended yes, since that classification is the
consolidation's first input.

---

## 20. Reproducibility record and validation results

### 20.1 Searches actually executed in this audit

No registered protocol query was executed. The following verification and discovery
queries were run. Counts are returned-record counts, **not** screening counts.

| # | Interface | Query form | Fields / filters | Date | Returned | Export |
| ---: | --- | --- | --- | --- | ---: | --- |
| 1 | Crossref REST `/works/{doi}` | 51 DOI lookups from the proposal reference list | exact DOI | 2026-09-06 | 49 resolved, 2 not found | `crossref_verify.tsv` (52 lines incl. header) |
| 2 | Crossref REST `/works?query.bibliographic` | 20 GAP-2 candidate title/author queries | `rows=2` | 2026-09-06 | 40 records | shell transcript |
| 3 | Crossref REST `/works?query.bibliographic` | 18 GAP-3 and cross-cutting candidate queries | `rows=2` | 2026-09-06 | 36 records | shell transcript |
| 4 | Crossref REST `/works?query.bibliographic` | 4 BPM candidate queries | `rows=3` | 2026-09-06 | 12 records | shell transcript |
| 5 | Crossref REST `/works/{doi}` | 3 newly discovered DOIs | exact DOI | 2026-09-06 | 2 resolved, 1 not found (IJCAI) | shell transcript |
| 6 | OpenAlex via WebFetch | 4 queries (1 keyword search, 3 DOI/entity lookups) | default | 2026-09-06 | 4 responses | tool transcript |
| 7 | Web search | 9 targeted adversarial queries | none | 2026-09-06 | 9 result sets | tool transcript |
| 8 | Direct page fetch | 8 fetches (PMLR, arXiv, IJCAI index, EU AI Act Art. 26, ACM/Springer/ScienceDirect attempts) | none | 2026-09-06/07 | 5 succeeded, 3 blocked or truncated | tool transcript |

Deduplication: candidate records were deduplicated by DOI. No duplicate DOI and no
duplicate title survived into either deliverable.

### 20.2 Validation battery

| Check | Method | Result |
| --- | --- | --- |
| Citation verification | Crossref `/works/{doi}` for all 51 proposal DOIs; authoritative proceedings records for [54], [60], [61]; ACM DL for [13]; arXiv for [52] | **PASS with 2 corrections** — 54 of 68 references re-verified. Corrections: [54] page range (ACM DL 377–382 vs proposal 377–383); [61] page range unconfirmed. |
| Duplicate DOI check | Set comparison across the 51 proposal DOIs and the 24 DOIs in the high-priority map | **PASS** — no duplicate DOI in either set, and no collision between them |
| Duplicate title check | Normalised title-prefix comparison within each deliverable and against the reference list | **PASS** — no duplicates |
| Year / venue consistency | Crossref year and container-title against each proposal citation | **PASS with 2 reconciled and 1 noted** — [55] and [32] are online-first vs issue-year differences and are not defects; the Crossref container-title for `10.1007/11431855_16` is corrupted upstream to an unrelated series, so the Springer record is used as the source of truth |
| Gap-claim consistency | Every row of the refutation matrix carries a non-empty `What_it_matches`, `What_it_does_not_match` and `Effect_on_proposal`; every claim in the claim audit carries a classification and, where non-supported, replacement wording | **PASS** — 35 of 35 matrix rows complete; 28 of 28 map rows carry `exact_gap_effect` |
| Source-tier validation | Tier assigned per record with a named verification route | **PASS** — 24 Tier A, 4 Tier B, 0 Tier C, 0 Tier D in the high-priority map. One record marked `NOT RE-VERIFIED IN THIS AUDIT`. No Tier C or D source supports any absence claim. |
| CSV structural validation | `csv.DictReader` parse; field-count and empty-cell checks | **PASS** — matrix 35 rows × 10 fields, no empty cells; map 28 rows × 45 fields, no missing `paper_id` or `exact_gap_effect` |

### 20.3 Standing limitation

All four primary databases were ACCESS BLOCKED (§10.3). This audit can demonstrate that
a competitor exists; it cannot demonstrate that one does not. No verdict in the
accompanying claim audit is stronger than `NEEDS_NARROWING`, and none is `REFUTED`.

---

## 21. Companion deliverables

- `literature/2026-09-06-gap-refutation-matrix.csv` — 35 candidate refuters across the
  three gaps, with matched and unmatched capability recorded separately.
- `literature/2026-09-06-high-priority-literature-map.csv` — 28 papers (8 GAP-1,
  8 GAP-2, 6 GAP-3, 6 cross-cutting), 45 extraction fields each, every row with an
  explicit role and a recorded extraction depth.
- `docs/research/phd-proposal/2026-09-06-chapter2-claim-audit.md` — statement-by-statement
  classification of Chapter 2's absence and novelty claims, with replacement wording for
  every non-supported claim.
