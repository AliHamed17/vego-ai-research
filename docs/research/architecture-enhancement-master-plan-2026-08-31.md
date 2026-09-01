# VEGO-AI Architecture Enhancement Master Plan — 2026-08-31

One plan that takes the architecture, infrastructure, and experiment portfolio from their audited
2026-08-31 state to full alignment with the 2026-08-25 doctoral proposal, executed in waves that
respect the project's hard gates. Grounding documents, in authority order: the 2026-08-25 proposal
(external PDF, supplied by Ali), `docs/research/phd-proposal/three-study-contract.md`,
`docs/research/phd-proposal/chapter-4-research-methodology.md`, and the verified gap inventory in
`docs/research/phd-proposal/architecture-alignment-audit-2026-08-31.md` (94 raised, 88 confirmed,
86 closable without new empirical evidence).

Standing claim boundary, restated once: EXP-005 is 0/24 generalization-safe labels, QL-01..05 are
0/5 executed, medical gates 0/6. Everything in Wave 1 is Phase-A treatment-validation work — design,
schemas, reference implementations, conformance tooling, replay mechanisms. None of it asserts an
empirical outcome, and the proposal's own §3.1 summary states that software completion and
conformance checks must never be read as evidence of improved outcomes.

## 1. The alignment spine

| Proposal contribution | Primary scientific artifact (Table 2) | Workstreams that deliver it |
|---|---|---|
| C1 selective intervention (SQ1, Study 1) | Attention-budget review-policy model | WS-C, WS-E |
| C2 governed judgment (SQ2, Study 2) | System-independent governed-judgment contract + executable conformance suite | WS-A, WS-B, WS-F |
| C3 controlled reuse (SQ3, Study 3) | Cross-context reuse and capability-gap decision procedure + target-context descriptor | WS-D |
| C4 integrated lifecycle (U-RQ) | End-to-end governed process, four-arm evaluation | WS-E, WS-G |

The contracts themselves (the schemas) merged in PR #31. This plan builds the second halves the
proposal requires — the *executable* parts — and realigns the experiment portfolio around them.

## 2. Workstreams

### WS-A — Governed-judgment reference engine (`src/vego_governed/`)

A new, unprotected Python package (sibling of the protected `src/vego_hlayer/`; `src/` is already on
the pytest pythonpath) that loads, validates, and operates `GovernedJudgmentRecord-v1` instances:
the seven-state lifecycle as an executable state machine with enumerated legal transitions and named
rejection codes; retained dissent computing a closed reuse gate; receipts (retrieval/use/outcome)
emitted as data, never as claims. This is the "reference implementation" half that chapter-4 §4.4's
conformance suite needs a subject for. Acceptance: every legal transition accepted, every illegal
transition rejected with the code the schema names, dissent-present records refuse reuse, all under
test in `scripts/tests/`.

### WS-B — Executable conformance suite (C2's second half)

`scripts/run_governed_contract_conformance.py`, implementing the three parts §4.4 specifies:
a reconstructability check (the record alone must answer what claim was judged, why, and under what
scope — mechanically: required trace/rationale/scope elements present, internally referenced, and
resolvable); a discrimination check (deliberately non-conforming fixture variants must each fail for
the specific, named reason they violate — a scope-less record, a never-leaves-Draft record, an
authority-less binding record, a dissent-ignored record); and a completeness-review scaffold that
records the independent-implementer arm as `not_run: independent_implementer_not_recruited` rather
than pretending. Acceptance: reference example passes; every planted variant fails with its named
reason; the suite is wired into CI as a `--check` script following repo convention.

### WS-C — Selective-intervention policy engine v2

`src/vego_governed/policy.py`: evaluates `ReviewPolicySignalContract-v1` instances — the six §3.3
comparator arms (never ask, always ask, random at matched budget, uncertainty only, fixed threshold,
proposed joint policy) as *configurations of one engine* over identical inputs; attention-budget
accounting reusing the already-validated `budget_state` vocabulary from the offline track
(`within_budget/capped/deferred/evaluation_only`) rather than inventing a third notion; and
selective-risk accounting (which cases were NOT escalated, so the error-remaining denominator is
computable when labels exist). The shipped `VEGO-AI/framework/selective_intervention_policy.py` is
protected and stays untouched: it is reproduced *as the `uncertainty_only` arm configuration*, which
is exactly the comparator role §3.3 assigns it. Acceptance: all six arms produce decisions over the
same frozen fixture set; a deterministic replay of the same fixtures twice yields identical decision
sequences and budget ledgers; per-arm decision logs carry every declared signal.

### WS-D — Reuse-gate engine (C3's procedure, executable)

`src/vego_governed/reuse.py`: the five gates in their required order (visibility/authorization →
claim relevance → context fit → current-case evidence → adaptation risk), short-circuiting so
restricted evidence is never exposed before gate 1 passes; four outcomes with `Undetermined` routed
to independent review rather than collapsed into allow/block; every decision naming its rule and the
context dimension that produced it; an outcome receipt per evaluation; the frozen context-distance
ladder evaluated from the target-context descriptor; and the capability-gap guard refusing any gap
claim without two distinct frozen contexts above cohort rank plus independent confirmation flags.
Acceptance: gate order proven by test (a gate-1 failure leaves gates 2-5 unevaluated and no
restricted evidence exposed); all four outcomes reachable by fixtures; receipts always emitted.

### WS-E — Experiment portfolio realignment

New experiment cards binding the engines to the study design, registered in
`experiments/registry.md`: EXP-041 (governed-judgment lifecycle conformance — Study 2 Phase A),
EXP-042 (six-arm policy replay determinism at a fixed budget on frozen fixtures — Study 1 Phase A
mechanism only), EXP-043 (reuse-gate order/outcome fidelity — Study 3 Phase A mechanism precursor),
EXP-044 (field-removal ablation harness readiness — Study 2 Phase B's instrument, run against the
reference example, explicitly *instrument validation*, not the study itself). Plus the ISS-045
relabels: EXP-016 and EXP-035 registry rows renamed to say "role-based action authorization" so
"authority" no longer reads as the claim-specific construct. Plus `experiment-definition-v3` schema
permitting N comparison arms (audit finding: v2's single `baseline`+`comparator` makes C4's four-arm
design structurally inexpressible), additive alongside v2, with a valid example.

### WS-F — Validator and infrastructure hardening

Extend `scripts/validate_research_records.py` with the `GovernedJudgmentRecord-v1` referential
invariants the C2 build flagged as unchecked (competence/authority claim ids matching case grounding;
trace slots citing evidence ids that exist; rationale refs resolving to real slots; use receipts
referencing real retrieval receipts), proven non-vacuous by mutation the same way the C1/C3
invariants were in PR #31. Deliberately deferred from this wave: `rfc3339-validator` (ISS-046) stays
its own change because turning on date-time checking can flip previously-passing records red across
the whole repo and deserves an isolated cascade check.

### WS-G — Decision packets (blocked on people, packaged now)

One supervisor decision packet, `docs/research/phd-proposal/2026-08-31-architecture-decisions-packet.md`,
carrying the four open calls the audit isolated as not-an-agent's-to-make: D1 the competence
construct (ISS-043 — in scope? evidenced how?), D2 six vs. seven lifecycle states (ISS-048), D3 a
revised-description rank in the context-distance ladder (ISS-047), D4 authorization to fix the three
live `VEGO-AI/framework/` defects (ISS-044) under a signed H-layer change hash. Each with the
recommendation, the falsifier, and what stays blocked until decided.

### WS-H — Research continuity (evidence-gated, staged not started)

QL-01..05 execution readiness: the proposal §3.2 freezes the five query families and their canonical
Boolean expressions before execution — this workstream keeps the frozen register verbatim in the
repo so execution (a human-authorized step) starts from the registered text, and tracks ISS-032's
taxonomy reconciliation. No search is executed by this plan; running them is Ali's call per the
2026-08-12 supervisor sequencing.

## 3. Waves

Wave 1 (this session, end to end): WS-A, WS-B, WS-C, WS-D, WS-E, WS-F, WS-G packaging — everything
the audit marked closable-now that fits outside protected paths. Exit: all engines under test, the
conformance suite green with planted-failure discrimination, full CI-equivalent suite green, PR
merged, memory updated.

Wave 2 (decision-gated): whatever D1-D4 unlock — the framework defect fixes under signed
authorization, the lifecycle-state resolution propagated to schema+prose, competence-evidence design.

Wave 3 (evidence-gated): Study 1 Phase B, Study 2 Phase B (between-condition + ablation with humans),
Study 3 Phases A/B, integrated four-arm evaluation — all blocked on EXP-005 labels, recruited
reviewers/raters/implementer, and supervisor-approved protocols. Nothing in this plan pretends
otherwise.

## 4. Guardrails

No protected path is touched (verified against `check_hlayer_change_authorization.py`'s prefix list;
the new package is a sibling, not a child, of `src/vego_hlayer/`). No LLM/API calls in any engine —
pure deterministic Python over fixtures, matching the repo's offline-mechanism convention. Generated
artifacts regenerate through the documented dependency order and the regenerate-then-rebind pattern;
cascade diffs are inspected for measured-value changes before commit. Every new capability lands with
tests in `scripts/tests/` (CI-discovered) and, where it validates records, with mutation-proven
non-vacuous checks.
