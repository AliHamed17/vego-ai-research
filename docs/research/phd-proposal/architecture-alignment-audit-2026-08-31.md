# Architecture and Experiment Alignment Audit — 2026-08-31

Does the implemented VEGO-AI architecture deliver what the 2026-08-25 doctoral proposal promises?

Method: five parallel auditors (one per contribution C1-C4, one for the experiment portfolio) read the
proposal's extracted text alongside the repository, each finding was then re-checked by an adversarial
verifier instructed to refute it, and three designers drafted the missing artifacts. 94 gaps raised, 88
confirmed (11 blocking, 38 major, 33 moderate, 6 minor). 86 of 88 are closable with no new empirical
evidence. Every load-bearing claim below was additionally spot-verified by hand against the named file.

Claim boundary: nothing here is an empirical result. EXP-005 is 0/24, QL-01..05 are 0/5, medical gates
are 0/6. Schemas and conformance checks are Phase-A treatment-validation artifacts; the proposal itself
(§3.1 summary) states this separation "prevents software completion, unit tests, or conformance checks
from being read as empirical evidence of improved outcomes."

## 1. Verdict

The architecture does not currently deliver C1-C4, but the condition is overwhelmingly
**designed-but-unbuilt and mis-labelled**, not unconsidered. Two findings carry the report.

**First**, the construct the proposal designates as its falsifiable novelty — reviewer selection as a
function of claim-specific *competence* and *authority*, modelled as distinct — has no implementation
surface, and competence is absent from the project's own design documents as well. Section 2 below.

**Second**, the shipped C1 routing surface,
[`selective_intervention_policy.py`](../../../VEGO-AI/framework/selective_intervention_policy.py), is a
disjunction of five uncertainty and flag booleans whose entry point is
`should_request_human_review(entry, *, include_medium=True)`. It takes no reviewer argument and no budget
argument, so it structurally cannot select a reviewer or be evaluated at a controlled attention budget.
That makes it, precisely, the "uncertainty only" and "fixed threshold" arms the proposal lists as
comparators the proposed policy must be evaluated *against*. The shipped policy is currently its own
baseline.

## 2. The novelty gap

The proposal stakes the thesis on a specific negative claim: no reviewed formulation makes reviewer
selection a function of assessed competence and authority over the *specific contested fragment*, and
none models authority as distinct from competence. Multi-expert deferral is said to condition on "an
aggregate competence profile over a task distribution, not assessed standing to settle the specific
contested fragment."

Verified by grep across every plausible location and alias:

- `competence`, `expertise`, `credential`, `reviewer_fit` — zero hits in `VEGO-AI/framework/`,
  `VEGO-AI/schemas/`, top-level `schemas/`, `src/vego_hlayer/`, `docs/architecture/`, and
  `docs/research/h-layer/`. The 13 files that do contain the word are all proposal, review, or
  prompt documents under `docs/research/phd-proposal/` plus agent-memory.
- Critically, competence is also absent from the project's own contract specification.
  [`chapter-4-research-methodology.md`](chapter-4-research-methodology.md) §4.4 enumerates the record's
  field groups as case grounding, the system's reasoning, the expert's rationale, scope, authority,
  provenance, and a six-state lifecycle. Competence is not among them. It is the only §3.4 content
  element that is undesigned as well as unimplemented.
- `authority` is not a field of any judgment record. What exists is role-based permission over runtime
  actions: `scripts/hlayer_offline/exp016.py` defines `ROLE_AUTHORITY` mapping
  `supervisor / trained_course_staff / course_staff / untrained_reviewer` onto
  `{submit_feedback, adjudicate, approve_correction}`, evaluated with no claim, fragment, or scope term.
  `src/vego_hlayer/contracts.py` gives `ReviewItem` a required `owner_role`, set to the literal
  `"human_reviewer"` in `adapters.py`. `schemas/gold-label-record-v2.schema.json` has `reviewerRole` in
  `{reviewer_1, reviewer_2, adjudicator}` — annotation label positions, not standing.
- There is no reviewer registry and no reviewer *set* to select from.
  [`framework-diagram.md`](../../architecture/framework-diagram.md) draws a single
  `HUMAN((Human Expert: real person - role delegation pending M-05))` node. The shipped policy enqueues
  into an undifferentiated list.

**What this means.** Every one of those role constructs is an aggregate role over an *action class*,
checked *after* a submission. That is the construct the proposal names as the literature's insufficient
form. The architecture as drawn today instantiates the prior work the novelty claim is defined against,
rather than the alternative. Three consequences worth stating to a supervisor:

1. The proposal's declared primary test for Study 1 cannot be run as specified — one of its five
   literature-derived signals has no representation to log, weight, or ablate.
2. The expertise-is-not-authority separation is currently untestable, because one of the two terms does
   not exist.
3. Two registry rows obscure this. EXP-016 and EXP-035 are titled with "authority" and anchored as
   Study 2 mechanism evidence, but implement role-based access control over runtime writes on
   `SYNTHETIC_NOT_HUMAN` fixtures. A reader scanning `experiments/registry.md` will read authority as
   covered.

This is the highest-priority item and it is closable now: it needs a schema, a reviewer registry, and
an honest statement of the design delta — no labels, no executed searches.

## 3. Contribution-by-contribution alignment

| Contribution | Promised artifact | What exists now | Principal gap | Closable now |
|---|---|---|---|---|
| **C1** selective intervention | Attention-budget review-policy model | Two disconnected tracks: the 90-line shipped policy above, and a real offline budget track where `budget_state` in `{within_budget, capped, deferred, evaluation_only}` is a required validated field on `TriageDecision` (`src/vego_hlayer/contracts.py`) with per-setting caps threaded through `scripts/hlayer_offline/exp015.py` | Competence/authority absent. Budget exists but is not a schema and is not connected to the shipped policy. Routing unit is an Agent-4 *pattern*, an aggregate *above* the model, where the proposal needs a unit *below* it | Yes |
| **C2** governed judgment | System-independent governed-judgment contract + executable conformance suite | `VEGO-AI/schemas/human_judgment.schema.json` is a real 18-required-field record, but VEGO-AI-bound by `memory_id` pattern and covering roughly half the required groups. Full prose spec exists at chapter-4 §4.4 including the six-state lifecycle | No versioned system-independent contract. Absent even in design: competence, exclusions, privacy, visibility, outcome receipts. Live defects in §4 below | Yes, except the independent-implementer arm, which is recruitment-blocked |
| **C3** controlled reuse | Cross-context reuse and capability-gap procedure + target-context descriptor | A three-check predecessor procedure specified at chapter-4 §4.5; four *different* distance orderings exist across the repo's drafts | Similarity is the only operative retrieval signal; fit, entitlement, and currency are not separate conditions. No frozen context-distance schema, no capability-gap construct (`capability gap` is zero hits repo-wide), no outcome receipt | Yes |
| **C4** integrated lifecycle | Four-arm end-to-end comparison, five outcome families | `docs/research/evaluation-plan.md`'s C0..C4B ladder; `framework-diagram.md` (still marked PROVISIONAL, dated 2026-07-10) | No four-arm design and no human-only arm anywhere. `schemas/experiment-definition-v2.schema.json` permits exactly one `baseline` and one `comparator`, so N-arm designs are structurally inexpressible. `evaluation-diagram.md` fixes a two-arm V0/V1 design whose omitted arm is the one C4's falsification condition names as decisive | Yes |

## 4. Live defects found while auditing

These are not design gaps; they are behaviours in committed code, each hand-verified.

1. **Amended judgments are silently dropped.** `human_judgment_memory.py` `write_memory()` dedups by
   `memory_id` keep-first (`if mid in seen: continue`). `memory_id` is `f"HJM-{setting}-{pid}"`, a
   deterministic function of setting and pattern only — not of content or version. A revised judgment
   for the same pattern therefore collides with its predecessor and is discarded if the older item is
   written first. Supersession is a C2 lifecycle requirement; this is its inverse.
2. **`search_memory()` has no status, requester, expiry, or revocation gate.** It checks
   `conflict_status == "needs_adjudication"` — a genuine partial implementation of "dissent blocks
   reuse", and worth crediting — but never reads `status`, so a retired record still flows downstream,
   and takes no requester parameter, so the proposal's first reuse gate (visibility and authorization
   before exposure) is currently unimplementable at that call site.
3. **A default-deny scope control that nothing consults.** `applies_to_future_models` appears exactly
   **once** in the entire framework: written as `False` in `build_memory_item()`. Nothing ever reads
   it. `memory_advisor.py` forwards `reuse_scope` as only `{domain, diagram_type}`, dropping both
   `applies_to_future_models` and `limitations` before any consumer sees them. Scope is recorded and
   inert.

Item 3 is the compact illustration of the C3 gap: the record already has the right *idea* and the
pipeline discards it.

## 5. What this change closes, and what it does not

This change adds three system-independent contracts as versioned JSON Schemas, registers them with the
CI record validator, and supplies one worked example each, grounded in the proposal's own Shift
Supervisor scenario:

- `schemas/review-policy-signal-contract-v1.schema.json` (C1) — models claim-specific competence and
  authority as two separate, separately-evidenced dimensions bound to a contested fragment, alongside
  an explicit attention budget and the comparator arms as configurations of one contract.
- `schemas/governed-judgment-record-v1.schema.json` (C2) — the eleven content groups, the lifecycle
  state machine, retained dissent as a reuse-blocking state, and per-component identifiability so the
  field-removal ablation layer can strike one component cleanly. **Deviation, flagged not hidden:**
  this schema ships *seven* lifecycle states, not the six chapter-4 §4.4 fixes. It adds
  `retained_dissent`, and its own conformance check makes that state mandatory whenever a qualified
  dissent is unadjudicated. The deviation is forced by a genuine tension in the specification — §4.4
  fixes six states while §3.4 requires dissent to be a retained state that blocks reuse, and
  `Contested` is not defined tightly enough to say whether it carries that blocking semantics. Either
  §4.4 moves to seven states, or `retained_dissent` collapses into `Contested` with the blocking rule
  attached there. This needs a decision before the contract is treated as settled; see ISS-048.
- `schemas/reuse-decision-record-v1.schema.json` (C3) — the five ordered gates, the four outcomes with
  `Undetermined` distinct from both allow and block, the frozen context-distance ladder, and an outcome
  receipt per use.

It does **not** close: the live defects in §4 (they sit in the protected `VEGO-AI/framework/` tree and
need a signed change authorization); the independent-implementer conformance arm (needs a person, per
chapter-4 §4.4's own note); anything requiring EXP-005 labels, executed QL searches, or medical gates.

The context-distance ladder in the C3 schema is a design proposal derived from the proposal's own
motivating example, pending supervisor confirmation. It is not a settled finding.

## 6. Findings raised while building the artifacts

Building and validating the worked examples surfaced further issues, recorded here rather than
quietly fixed.

1. **`format: "date-time"` is inert repo-wide.** `rfc3339-validator` is not installed in the `uv`
   environment, so `jsonschema.FormatChecker()` registers no `date-time` checker. Setting a timestamp
   to `"not-a-timestamp"` still validates. This affects every schema under `schemas/`, not only the
   three added here. Not fixed in this change: adding the dependency could turn previously-passing
   records red, which is a cascade that deserves its own change. Logged as ISS-046.
2. **The C3 context-distance ladder has no dimension for a revised domain description**, although the
   proposal's own p.9 sequence names it as a distinct step. It currently rides on `cohort`. The
   consequence is worth stating plainly: a *mid-semester* description revision within one cohort
   computes a differing-rank of 1 and would return plain "Eligible" with nothing recording that the
   ruling's premise had changed. That is the proposal's own failure mode reappearing inside the fix.
   Left as-is deliberately, because the ladder is a design proposal pending supervisor confirmation
   and adding a rank changes every downstream comparison. Logged as ISS-047.
3. **`importantCaseLabelIndependentOfPolicy` (C1) has no not-applicable state.** It is a required
   boolean, but when `importantCaseLabelSource` is `not_yet_established` no label exists whose
   independence could be asserted. Its two sibling fields solve this with `not_yet_*` enum members;
   the boolean has no equivalent, so the current instance sets `false` and explains the reading in its
   `claimBoundary`. Logged as ISS-047.

The C1 and C3 cross-field invariants the schemas describe in prose are now actually executed, in
`scripts/validate_research_records.py`, and are proven non-vacuous by negative test: mis-scoping a
competence assessment to a different fragment, or pointing the selected reviewer at a candidate that
does not exist, both fail validation. The first of those is the mechanical enforcement of the
thesis's own novelty distinction — a competence figure computed over some other unit can no longer be
presented as standing over this fragment.

## 6. Recommended sequence

1. Take a supervisor decision on the competence construct — it is absent from the design, not merely
   the code, so it cannot be closed by implementation alone.
2. Relabel EXP-016 and EXP-035 so "authority" in the registry does not read as claim-specific authority
   when it is role-based access control over runtime writes.
3. Connect the existing offline budget track to the C1 contract rather than inventing a third budget
   notion — `budget_state` is already validated and exercised.
4. Fix the three §4 defects under a signed H-layer change authorization.
5. Widen `experiment-definition-v2` beyond one baseline and one comparator, or C4's four-arm design
   stays inexpressible.
