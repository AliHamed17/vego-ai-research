# Future Work and Verification Plan — 2026-09-01

The successor to `architecture-enhancement-master-plan-2026-08-31.md`, written after Wave 1 landed.
Its subject is different: not what to build next, but how the research proceeds step by step with
the pipeline provably unbroken at every step, how each result is validated before the next step
depends on it, and how "enhancing" is distinguished from merely "correct" at every comparison. The
audience is Ali and any future agent session picking up the research mid-stream.

## 1. The standing health ladder — "nothing is broken" as a checkable property

"The pipeline works" is not an impression; it is the following ladder, run top to bottom, every
rung green. Any session that changes code, schemas, registry rows, or generated artifacts runs the
ladder before claiming done. Any red rung stops the work above it.

| Rung | What it proves | Command (from repo root) |
|---|---|---|
| Dependencies | lockfile matches declared deps | `uv run python scripts/check_dependency_lock.py --check` |
| Record integrity | every schema example + tracked record validates, cross-field invariants included | `uv run python scripts/validate_research_records.py schemas/examples` |
| Contract conformance | the governed-judgment reference record reconstructs; all planted invalid variants fail for their named reasons | `uv run python scripts/run_governed_contract_conformance.py` |
| Unit/mechanism tests | engines, guards, generators behave; 282 tests as of 2026-09-01 | `uv run --group thesis python -m pytest scripts/tests -q` (plus `VEGO-AI/tests`, `tests/hlayer_offline` as CI runs them) |
| Generated-artifact freshness | every derived artifact matches its sources (the hash chain) | the `--check` set: hardening manifests, bigui architecture snapshot, comparison experiments, run store, experiment benchmark, catalog, bigui hub, architecture experiments, thesis evidence package, progress visual, review manifest, visualization agent, gallery |
| Claim discipline | no unqualified accuracy/effort/generalization language anywhere tracked | `uv run python scripts/check_evidence_consistency.py --check`, `check_quality_ratchet.py`, `validate_thesis_content.py`, `check_thesis_citations.py` |
| Privacy/security | no secrets, no patient data, audit clean | `check_repository_privacy.py`, `security_audit.py --history` |

Known repair patterns when a freshness rung goes red, in dependency order (this is the data-flow
spine — sources on the left, derived views to the right): source `.py`/`.md`/schema change →
`thesis-evidence-snapshot` (`--source-revision <commit>`) → `THESIS_REVIEW_PACKAGE_MANIFEST`
(regenerate, then `--package-revision <commit>` as its own second commit) →
`baseline-comparison-results --refresh` → `experiment-benchmark --refresh` → catalog → bigui hub →
progress visual → hardening manifests last. Every cascade diff is inspected before commit: hash and
revision rebinding only; any changed *measured value* is a stop-and-investigate, never a commit.

Two standing repairs are already ticketed, not forgotten: `rfc3339-validator` is absent so
`format: "date-time"` is inert repo-wide (ISS-046 — its own change, cascade-checked), and the three
protected-tree defects await the D4 signed authorization (ISS-044).

## 2. Step-by-step research execution — each step verified before the next depends on it

Every step below names its entry gate, its verification, and its exit artifact. No step starts
before its predecessor's exit artifact exists and the health ladder is green.

**Step 1 — Supervisor decisions (D1–D4).** Entry: `2026-08-31-architecture-decisions-packet.md`
presented to Iris/Arnon. Verification: each decision recorded in `docs/agent-memory/decisions.md`
with date and chosen branch. Exit: D1 competence-evidence rule, D2 state-set resolution, D3 ladder
v2 or cohort definition, D4 signed authorization hash. Wave 2 items are mechanical once these land.

**Step 2 — Framework defect repair under D4.** Entry: signed hash. Verification: before/after
fixtures proving amended judgments supersede rather than vanish, retired records stop flowing, and
`applies_to_future_models` is enforced; full ladder green. Exit: ISS-044 closed with the fixture
evidence linked.

**Step 3 — EXP-005 real labels (the evidence gate).** Entry: two named reviewers plus adjudicator
(EXP-019/020 protocol, kappa and adjudication rules preregistered there). This is human work an
agent cannot do. Verification: `exp005_label_review.py` validation summary; reviewer agreement
reported with confidence intervals; 1–19 safe labels is pilot-only by standing rule, ≥20 opens
quantitative eligibility. Exit: frozen gold-label manifest. Until this exists, every downstream
"enhancing" claim stays closed — that is the honest state, not a failure of the plan.

**Step 4 — Study 1 Phase B (does the joint policy *enhance* routing?).** Entry: Step 3 + D1.
Instrument: the six-arm engine (`src/vego_governed/policy.py`) over frozen event logs — every arm
sees every case, identical budget. The comparison discipline in §3 applies. Exit: per-arm ledgers,
important-case capture at matched budget, selective-risk report for non-escalated cases, and a
narrowed P1 if the joint policy fails to beat the simple arms — a reportable result either way.

**Step 5 — Study 2 Phase B (is the governed record worth its burden?).** Entry: Step 3 reviewers +
independent implementer recruited (the one recruitment gap chapter-4 §4.4 names). Instruments: the
conformance suite (EXP-041) and the field-removal ablation harness (EXP-044) — between-condition
comparison (label-only / comments / provenance record / full governed record) then one-component-
at-a-time removal; a component surviving no ablation leaves the minimum record. Exit: the minimum
adequate contract, evidence-backed.

**Step 6 — Study 3 Phases A/B (does governed reuse beat the composite baseline?).** Entry: D3
ladder frozen + two trained raters. Phase A is a reliability *gate*: verdict and reason agreement
reported separately with CIs; failure is reported as the result, not absorbed. Phase B is
three-armed: no reuse, the mature composite (CBR retrieval + contextual matching + ABAC), and the
five-gate procedure — the composite is the comparator that matters, because beating "no reuse"
alone proves nothing about the contribution. Exit: target benefit over composite, or a narrowed P3.

**Step 7 — Integrated four-arm evaluation (C4).** Entry: Steps 4–6 variance estimates; design
frozen and preregistered (now expressible via `experiment-definition-v3`). Arms: AI-only,
human-only, ordinary non-governed HITL, governed. C4 is supported only if governed beats the
strongest single-mechanism arm at matched expert minutes with lower scope-violation and
revoked-reliance rates; equal performance at higher governance cost is a negative result and is
published as one.

**Step 8 — QL-01..05 execution + taxonomy reconciliation.** Entry: supervisor go-ahead (the
2026-08-12 sequencing makes this Ali's call). The frozen query families run verbatim from the
proposal §3.2 register with full audit records per query line; ISS-032's Judgment-Lifecycle-Grid ↔
Zou-taxonomy reconciliation closes alongside. Exit: the literature-gap language upgraded from
corpus-bounded to search-backed, and the "proven absence" claims finally permitted or corrected.

## 3. The comparison discipline — "enhancing", not merely "correct"

A mechanism that works is not yet a contribution. Every claim of enhancement must clear all five,
and the engines were built so each is checkable rather than rhetorical:

1. **Matched resources.** Same attention budget, same evidence access, same case sets across arms —
   the budget ledger makes "at matched budget" an assertion about data, not prose.
2. **The strongest honest baseline.** Uncertainty-only for routing (the shipped policy *is* that
   arm), the CBR+matching+ABAC composite for reuse, non-governed HITL for the lifecycle. Beating a
   strawman is reported as beating a strawman.
3. **Preregistered thresholds.** Success/failure conditions written before data, in the experiment
   card; effect sizes and 95% CIs accompany any significance test; sample sizes from pilot variance,
   not convenience.
4. **Selective risk stated.** Every routing result reports where errors remain among the cases NOT
   escalated — enhancement that concentrates silent risk is not enhancement.
5. **Negative results are results.** A narrowed proposition is a reportable outcome with the same
   publication path as a positive one; the tracked record keeps both.

## 4. Efficiency of the work itself

Verification is front-loaded because rework is the dominant waste: the cross-field invariants and
conformance suite catch inconsistent records at write time rather than at review time; the health
ladder catches cascade drift in minutes rather than at PR CI; the regenerate-then-rebind canon
avoids the red-main incidents the project has already paid for twice. Agent-session efficiency
rules that stay in force: isolated worktrees per change, memory logs per session so no successor
re-derives state, decisions packaged for supervisors instead of blocking work in place, and the
frozen benchmark cohort so registry growth stops breaking generators (fixed this wave).

## 5. Exit criterion for the whole plan

The research is "done and not broken" when: every rung of §1 is green on `main`; D1–D4 are recorded
decisions; EXP-005 holds ≥20 adjudicated safe labels; Studies 1–3 and the integrated evaluation have
preregistered, executed, and reported outcomes (positive or narrowed); QL-01..05 audit records
exist; and every thesis claim traces to one of those artifacts through the claim-consistency guard.
Nothing on that list is asserted as achieved by this document — as of 2026-09-01 the evidence state
is EXP-005 0/24, QL 0/5, medical gates 0/6, and the document exists precisely to keep that honest.
