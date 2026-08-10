# Artifact-per-SQ Brainstorm (informal)

> **Status: informal brainstorm only — not a decision, not a design.**
> On the 2026-08-05 supervisor call, Iris told Ali to *think about* (not yet
> start formally designing) what the "research artifact" is for each
> sub-question — architecture, framework, classification scheme, or
> something else (`docs/research/meetings/2026-08-05-supervisor-meeting.md`,
> item A08-04: "Think about (do not yet execute) section 2 ... and section 4
> (research artifact per RQ - what exactly each artifact is)"). This file is
> that thinking-about step, nothing more. It lists **options for Ali to
> consider**, not a chosen answer. No candidate below is adopted, ranked as
> "the" answer, or ready for the proposal's Methodology section. Formal
> artifact design stays out of scope until Iris/Arnon say otherwise.

Grounding: options below are read off what already exists in
`thesis/chapters/05-human-ai-co-reasoning-artifact.md` (VEGO-AI M1–M4B-1),
so each is a plausible *extension* of shipped code/schemas rather than a
speculative new build.

## SQ1 — Selective intervention

Built today: `selective_intervention_policy.py` + `human_review_queue.py` —
a rule-based, conjunctive filter over Agent 4's own uncertainty signals
(`requires_human_review`, `Undetermined`, low/medium confidence,
`flag_for_guidelines_update`) that routes 11/27 patterns to a queue (§5.2).

1. **Architecture** (listener/triage/routing components, generalized from
   M1's queue-building pipeline). *Pro:* already matches the Study 1
   language in the RQ decision pack ("domain-neutral listener/triage/
   routing architecture"), so it's the lowest-friction framing.
   *Con:* reads as an engineering deliverable; may need an explicit
   theoretical/generalizable claim layered on top to count as a doctoral
   contribution rather than a component diagram.
2. **Trigger taxonomy + dosage policy** — generalize the four conjunctive
   criteria into a named, domain-neutral classification of *why* a case
   gets escalated, paired with a threshold/dosage rule. *Pro:* directly
   extends the concrete rule set already coded, and taxonomies are easy to
   evaluate for precision/recall (matches planned EXP-021/022). *Con:* a
   taxonomy alone is thin — likely needs to be paired with a decision
   procedure (see #3) to stand as a full artifact.
3. **Decision framework** (the policy-table style already used for M4B-1,
   applied one layer earlier — parametrized thresholds/escalation rules
   rather than one fixed policy instance). *Pro:* gives SQ1 and SQ3
   methodological symmetry (both are "policy table" artifacts). *Con:*
   risks blurring into SQ3's evaluation framework if the "decide when to
   intervene" artifact isn't kept analytically separate from the "measure
   the effect" artifact.

## SQ2 — Governed knowledge reuse

Built today: schema-validated feedback (`human_feedback.schema.json`),
signature-verified attachment (M2); provenance-tracked, scope-tagged
judgment memory (`human_judgment.schema.json`) with explicit promotion
rules and conflict handling (M3); deterministic, explainable (embedding-
free) retrieval with graded advice strength (M4A) (§5.3–5.5).

1. **Governance framework** (capture → validate → promote → store →
   retrieve → advise, with the schema/signature/conflict rules as its
   controls). *Pro:* nearly verbatim match to the decision pack's Study 2
   description ("validation/reconciliation protocol, provenance/authority
   model ... reuse policy"). *Con:* "framework" is broad — reviewers may
   ask for a sharper boundary between framework, protocol, and process.
2. **Knowledge representation / schema architecture** — treat the schema
   pair plus their provenance links as the artifact itself, i.e. a formal
   representation model for reusable expert judgment. *Pro:* maps onto
   something that already concretely exists and is checkable now (schema
   conformance, provenance completeness). *Con:* undersells the retrieval/
   matching/conflict logic, which is arguably the more novel piece.
3. **Safe-reuse classification scheme** — formalize `memory_advisor.py`'s
   match-reason + advice-strength logic into a general scheme that
   classifies a judgment along scope × conflict × match-strength to decide
   if/how it may be reused. *Pro:* tracks the most distinctive existing
   mechanism (explainable, non-embedding retrieval). *Con:* narrower than
   #1 — doesn't obviously cover the M2 validation/governance side without
   being paired with another candidate.

## SQ3 — Evaluation and transfer

Built today: deterministic policy-table comparison
(`memory_informed_classifier.py`) producing a non-destructive parallel
artifact with schema-enforced constants, evaluation-leakage tagging, and a
component-to-evidence traceability table (§5.6, §5.9); Arnon's 2026-08-05
correction reframed SQ3 around classifying domain-specific vs. broadly
transferable elements (meeting record, item E12).

1. **Evaluation protocol/methodology artifact** — a reusable protocol
   (paired comparison + leakage tagging + gold-label gating) rather than a
   system component. *Pro:* matches Study 3's decision-pack description
   ("preregistered protocol, gold set ... validity and stopping analysis")
   and is what Chapter 6 needs regardless. *Con:* a "protocol" reads as
   methodology, not artifact — may reintroduce the solution-vs-question
   conflation Arnon flagged on Aug 5 (item E4) if not kept distinct.
2. **Transfer classification scheme** — extend M3's existing
   `reuse_scope` field (same-pattern/same-setting/cross-setting/
   cross-domain) into a full scheme classifying which elements are
   domain-specific vs. broadly transferable. *Pro:* directly answers
   Arnon's explicit Aug 5 correction, so it's grounded in a supervisor
   instruction rather than invention. *Con:* sits logically close to
   SQ2's scope field — the SQ2/SQ3 boundary would need working out, not
   assumed.
3. **Comparative measurement framework** — generalize the M4B-1
   parallel-comparison pattern plus the §5.9 invariant/failure-mode/
   evidence table into a domain-neutral instrument for measuring quality/
   consistency/traceability/effort deltas. *Pro:* the most literal
   extension of what's already running today. *Con:* closest of the three
   to "the existing implementation, renamed" — risks not reading as a
   distinct contribution from SQ1/SQ2's artifacts unless scoped tightly to
   measurement logic only.

## Note

These nine options are not mutually exclusive, not scored, and not
proposed as a shortlist. The next step, if any, is Ali's own reflection
and then a supervisor conversation — not a written design — per Iris's
instruction not to start section 4 yet.
