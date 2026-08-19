# Chapter 4 Decisions Packet — Four Items Blocking Methodology Sign-Off

Prepared for: Iris Reinhartz-Berger and Arnon Sturm  
Prepared by: Ali  
Status: **decision request. Nothing in this file is approved until a dated response is recorded.**

## How to use this packet

For each item, choose one response:

- **Confirm** the working recommendation;
- **Correct** it by writing replacement wording; or
- **Defer** it with a reason and the condition or date for reopening it.

The recommendations below are intended to reduce decision time. They are not decisions attributed
to Iris or Arnon. The affected files must be synchronized only after a decision is recorded.

## Item 1 — Artifact granularity and the three-layer model

### Decision question

Should each study have one narrow primary research artifact while retaining the broader system
components as a supporting implementation bundle and the empirical protocol as a separate
evaluation package?

### Working recommendation

**Correct the earlier either/or framing and adopt the three-layer model.** The narrow and broad
artifact descriptions should not be treated as mutually exclusive:

| Study | Primary research artifact | Supporting implementation bundle | Evaluation package |
| --- | --- | --- | --- |
| Study 1 / SQ1 | Attention-budget review-policy model | Orchestrator, event catalog, trigger signals, routing modes, queue/timeout rules, burden budget, receipts | Analytical/replay validation followed by held-out policy comparison with burden and important-case outcomes |
| Study 2 / SQ2 | Normative governed-judgment contract | Judgment Object, Contestable Store, reconciliation, lifecycle, authority, provenance, visibility, revocation, and receipts | Conformance/reconstructability followed by label-only/unstructured comparator evaluation |
| Study 3 / SQ3 | Transfer-eligibility procedure and target-context descriptor | Retrieval Advisor, authorization pre-filter, applicability/permission filters, transfer classifier, advisory-use and outcome receipts | Rater reliability followed by frozen-store held-out target evaluation against matched no-reuse control |

The primary artifact defines the scientific contribution boundary. The supporting bundle makes it
executable. The evaluation package determines whether the associated knowledge claim survives.
This preserves the literature review's broader mechanisms without presenting a large engineering
bundle as one indivisible contribution.

### Response

- [ ] Confirm the three-layer model.
- [ ] Correct to: ________________________________________________
- [ ] Defer because/until: ______________________________________

### Decision record

| Field | Entry |
| --- | --- |
| Decision | Pending |
| Decision date | — |
| Decision maker(s) | — |
| Rationale/comments | — |
| Effective date | — |
| Affected files | `artifact-layer-contract.md`; `chapter-4-research-methodology.md`; `three-study-contract.md`; literature-review contribution/study tables; RQ workbook artifact/comparator/evaluation rows; proposal figures |

## Item 2 — Exact SQ2/SQ3 ownership boundary

### Decision question

Where does governed representation end and transfer evaluation begin, so Studies 2 and 3 do not
claim the same artifact?

### Working recommendation

**Confirm with the following clarification:**

- **Study 2 defines and governs the source judgment.** It owns the record's scope declaration, hard
  exclusions, exact-match dimensions, adaptable dimensions and tolerances, ranking-only dimensions,
  authority, visibility, validation, contestation, lifecycle, provenance, and revocation semantics.
- **Study 3 applies that source scope to a target context.** It owns target-context description,
  authorization and visibility pre-filtering, source-target comparison, adaptation selection,
  eligibility verdict, reason code, and target-outcome evaluation.
- Study 3 may detect that a source scope is missing or defective, but it may not silently rewrite
  the source judgment. Any source-record revision returns to the Study 2 lifecycle and produces a
  new version with provenance.

### Response

- [ ] Confirm this boundary.
- [ ] Correct to: ________________________________________________
- [ ] Defer because/until: ______________________________________

### Decision record

| Field | Entry |
| --- | --- |
| Decision | Pending |
| Decision date | — |
| Decision maker(s) | — |
| Rationale/comments | — |
| Effective date | — |
| Affected files | Chapter 4 §§4.5–4.6; `three-study-contract.md`; `artifact-layer-contract.md`; workbook SQ2/SQ3 rows; lifecycle and transfer figures |

## Item 3 — Instrument evidence before EXP-005

### Decision question

May Study 2 conformance/reconstructability evidence and Study 3 rater-agreement evidence be
reported before EXP-005 reaches the independent-label threshold?

### Working recommendation

**Confirm with a strict evidence restriction.** The following may be reported before EXP-005 if
their protocols are frozen and their actual results exist:

- schema/invariant conformance;
- blind reconstructability;
- predictable rejection of named non-conforming variants;
- independent-implementation conformance, if a genuinely independent implementer participates;
- inter-rater agreement on transfer-eligibility verdict and driving reason.

They must be labeled **instrument evidence**. They do not support claims of assessment accuracy,
generalization, safe reuse, target benefit, burden reduction, clinical performance, or broad
transfer. EXP-005 and the later target studies remain necessary for those claims.

### Response

- [ ] Confirm instrument evidence under this restriction.
- [ ] Correct to: ________________________________________________
- [ ] Defer because/until: ______________________________________

### Decision record

| Field | Entry |
| --- | --- |
| Decision | Pending |
| Decision date | — |
| Decision maker(s) | — |
| Rationale/comments | — |
| Effective date | — |
| Affected files | Chapter 4 evidence rules and Study 2/3 phases; Chapter 5 result taxonomy; claim register; experiment register; proposal wording |

## Item 4 — EXP-009 and EXP-010 before M-04

### Decision question

Should EXP-009 and EXP-010 appear anywhere in the supervisor-facing proposal before `M-04`
protocol approval is recorded?

### Working recommendation

**Confirm that they remain outside proposal evidence until `M-04` is recorded.** They may stay in
internal experiment planning as provisional synthetic fixtures, but they should not appear in the
proposal's evidence, preliminary-results, or contribution-support tables. A provisional-fixture
caveat would still risk being read as positive evidence.

### Response

- [ ] Confirm exclusion until `M-04`.
- [ ] Correct to: ________________________________________________
- [ ] Defer because/until: ______________________________________

### Decision record

| Field | Entry |
| --- | --- |
| Decision | Pending |
| Decision date | — |
| Decision maker(s) | — |
| Rationale/comments | — |
| Effective date | — |
| Affected files | Chapter 4 §4.8; Chapter 5 if later extended; experiment register; claim/evidence tables; proposal figures and appendices |

## Housekeeping confirmation — Exact EXP-006/007/008 wording already used

This is not a new scientific decision. It asks whether the existing Chapter 5 wording is acceptable
for supervisor-facing use. The text below is reproduced so it can be confirmed without opening a
second document.

### Exact framing paragraph from Chapter 5 §5.1

> Two already-run experiment series back Study 1 and Study 2 respectively. Both are offline replays
> and conformance tests against existing VEGO-AI/H-layer artifacts — mechanism and observability
> evidence, never assessment-quality evidence. Nothing below answers whether selective intervention
> or governed reuse actually improves anything; that question waits on EXP-005 labels that do not
> yet exist. What these results do show is that the mechanisms describe real, inspectable behavior
> rather than only a paper design.

### Exact EXP-007 paragraph from Chapter 5 §5.2

> EXP-007 replays four dosage-mode candidates against that same reconstructed stream and reports,
> for each, event load relative to reviewing every decision and coverage of high-severity cases:
> `threshold_sev1` (load 0.889, coverage 1.0), `threshold_sev2` (load 0.799, coverage 1.0),
> `threshold_sev3` (load 0.578, coverage 0.726), and `first_n_then_auto` (load 0.581, coverage 0.73);
> `every_decision` is the load-1.0/coverage-1.0 reference point and `silent` the load-0/coverage-0
> one. The honest finding is a null result stated as such: the experiment's own guardrails target
> coverage of at least 0.8 at load of at most 0.5, and no tested mode reaches both at once — the two
> modes that cut load furthest (`threshold_sev3`, `first_n_then_auto`) also lose roughly a quarter
> of high-severity cases. This is reported as an observed trade-off boundary, per the experiment's
> own instruction not to select or silently tune a default, and not as a recommended operating
> point.

### Exact evidence-boundary paragraph from Chapter 5 §5.5

> Every result above is mechanism, observability, or conformance evidence, each reported at exactly
> the scope its own experiment plan assigns it. None of it is read as evidence of assessment
> quality, accuracy, generalization, expert-effort reduction, or clinical performance. EXP-007's
> load figures in particular describe a property of an offline replay against one existing corpus,
> not an effort-reduction result — the experiment's own guardrails forbid that reading, and this
> chapter follows them. The gate that would license a quality claim, EXP-005, stands at 0 of 24
> generalization-safe expert labels, unchanged by anything in this chapter.

### Housekeeping response

- [ ] Confirm the exact wording above.
- [ ] Request the following changes: ______________________________

| Field | Entry |
| --- | --- |
| Decision | Pending |
| Decision date | — |
| Decision maker(s) | — |
| Rationale/comments | — |
| Affected files | `chapter-5-preliminary-results.md`; Chapter 4 Study 1 Phase A and evidence boundary; preliminary-results slides/tables |

## Closeout rule

After Iris and Arnon respond, Ali should record the dated decisions in the decision/change log and
update every affected artifact in one controlled synchronization pass. An unchecked box or an oral
assumption is not a recorded decision.
