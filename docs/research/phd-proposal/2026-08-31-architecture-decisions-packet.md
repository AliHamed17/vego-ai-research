# Architecture Decisions Packet — 2026-08-31

Four decisions the 2026-08-31 architecture alignment audit isolated as belonging to Ali and/or the
supervisors, not to an agent. Each entry gives the question, the evidence, a recommendation, the
falsifier for that recommendation, and what stays blocked until decided. Companion documents:
`architecture-alignment-audit-2026-08-31.md` (the verified gap inventory) and
`../architecture-enhancement-master-plan-2026-08-31.md` (the wave plan these decisions gate).

## D1 — Is claim-specific competence assessment in scope, and how is it evidenced? (ISS-043)

The proposal's §1.8 stakes the thesis's novelty on routing by claim-specific *competence* and
*authority*, modelled as distinct. Authority is designed (chapter-4 §4.4 field list) and now has a
schema surface; competence is absent from both the code and the project's own design documents — it
is the only §3.4 contract element that is undesigned as well as unimplemented. The new
`review-policy-signal-contract-v1` schema models it as a separately-evidenced dimension, and the
Wave-1 policy engine carries a placeholder selection function, but placeholders cannot answer the
design question: what counts as evidence of competence *for a specific contested fragment* —
declared credentials, seed-question calibration (the classical-model tradition the review already
cites), task history on the same guideline, or supervisor designation?

Recommendation: adopt a two-source minimum for Study 1 — declared credential plus one observable
(calibration seed set or same-guideline history) — and record the assessment method in the record,
as the schema already allows. Falsifier: if the supervisors judge per-fragment competence assessment
infeasible for the course setting, the §3.3 primary test must be redesigned around authority plus
aggregate competence, and the §1.8 novelty claim correspondingly narrowed — that is a proposal-text
change, not an implementation change. Blocked until decided: any claim that the routing policy
implements the §1.8 construct; Study 1 Phase B design freeze.

## D2 — Six or seven lifecycle states? (ISS-048)

Chapter-4 §4.4 fixes six states (`Draft, Active, Contested, Superseded, Expired, Revoked`). §3.4
separately requires retained dissent to be a state that blocks reuse pending adjudication.
`Contested` is not defined tightly enough to say whether it carries that blocking semantics, so the
shipped `governed-judgment-record-v1` schema resolved the tension by adding a seventh state,
`retained_dissent`, which its own conformance check makes mandatory whenever a qualified dissent is
unadjudicated. The deviation is documented, not hidden.

Recommendation: fold `retained_dissent` into `Contested` and attach the reuse-blocking rule to
`Contested` explicitly — six states, one of them now precisely defined — because a smaller state
space is easier to defend and §4.4's set is already written into the methodology chapter. Falsifier:
if `Contested` must also cover non-blocking contest states (e.g. a challenge under review that does
NOT suspend reuse), the two semantics genuinely differ and seven states is correct. Blocked until
decided: describing the contract as final; v2 of the schema.

## D3 — A revised-description rank in the context-distance ladder? (ISS-047)

The proposal's own p.9 sequence names "a later cohort working from a revised description" as a
distinct step, but the shipped ladder has no revised-description dimension — it rides on `cohort`.
Consequence, stated concretely: a mid-semester description revision within one cohort computes
differing-rank 1 and returns plain "Eligible", with nothing recording that the prior ruling's
premise (the role was *unnamed* in the description) no longer holds. That is the proposal's own
motivating failure reappearing inside the fix.

Recommendation: add `description_version` as its own rank between `cohort` and
`modeling_language`, and re-freeze the ladder as CDS-C3-v2 before any Study 3 work uses it.
Falsifier: if the supervisors define description revisions as constitutive of a new cohort (i.e.
the course context *is* the description version), the current ladder is correct and the definition
should be written into the descriptor's `cohort` documentation instead. Blocked until decided:
freezing the ladder; any Study 3 fixture design.

## D4 — Authorization to fix the three live framework defects (ISS-044)

Three hand-verified behaviours in the protected tree contradict the contract the thesis is building
(details and line references in the audit §4): `write_memory()` silently drops amended judgments
(keep-first dedup on a setting+pattern key — the inverse of supersession); `search_memory()` never
checks `status` and takes no requester, so retired records flow downstream and the first reuse gate
cannot be enforced at that call site; `applies_to_future_models` is written once as `False` and
never read anywhere. These sit under `VEGO-AI/framework/`, which requires a signed
change-authorization hash per `scripts/check_hlayer_change_authorization.py`.

Recommendation: authorize a minimal, test-covered fix set — content-versioned `memory_id` (or
last-write-wins with explicit supersession records), a `status`+requester gate in `search_memory()`,
and honoring `applies_to_future_models` in `memory_advisor.py` — as one reviewed change with
before/after fixtures. Falsifier: none needed; this is a defect-repair authorization, not a design
question. Blocked until signed: the defects persist, and every downstream consumer inherits them.

---

None of these decisions is assumed anywhere in Wave 1. The engines and schemas are written so that
either branch of each decision is implementable without discarding the artifacts: D1 changes a
selection function, D2 collapses one enum member, D3 inserts one ladder rank and re-freezes, D4
touches only the protected tree.
