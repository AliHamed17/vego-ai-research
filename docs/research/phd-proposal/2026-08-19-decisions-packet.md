Decisions packet — five items that have never been signed off

Prepared for: Iris Reinhartz-Berger and Arnon Sturm
Prepared by: Ali (drafted with AI assistance; every recommendation below is a suggestion, not a
decision)
Status: decision request; nothing in this file is recorded as approved until answered

Why this exists: the 2026-08-19 gap audit found that five wording items have been used informally
across every proposal document since 2026-08-05, but none has an explicit recorded meeting outcome
- the requirements-closure validator reports 0 of 10 D-RQ decisions closed. Each item below can be
answered in one of three ways: Confirm the working wording as-is, Correct it (write the replacement
directly on this page), or Defer it with a reason. Five short answers here unblock Chapter 2's
final structure, Chapter 3's sign-off, and Chapter 4's own artifact confirmation.

Item 1 (D-RQ-01, D-RQ-02) - Is the main research question and the three sub-questions final?

Working wording, live in Chapter 3 today:

U-RQ: How can human judgment be captured, governed, and used to support agentic-AI-driven
variability exploration in guideline operationalization scenarios, enabling reliable human-AI
co-reasoning?

SQ1: When and how, in variability exploration scenarios, should an agentic assessment system
request human judgment so that important uncertainties are addressed without unnecessary expert
burden?

SQ2: How should expert judgment - including the system's core reasoning - be represented,
validated, reconciled, and stored so it can be reused transparently without unsafe generalization
or loss of human authority?

SQ3: How can expert judgment be reused and transferred across different guideline-
operationalization contexts without unsafe generalization or loss of human authority, first in
software/modeling and, when governance and access permit, in healthcare?

This is the reconstruction from the 2026-08-05 live edit, read aloud without objection on
2026-08-12 but never explicitly confirmed. Answer: Confirm / Correct to ___ / Defer.

Item 2 (E6) - "exploration" or "identification/classification" in U-RQ?

The 2026-08-05 record shows Iris, echoing Arnon, asking to narrow the main question explicitly to
variability identification/classification rather than the broader "exploration" the current
wording still uses. Recommendation: keep "exploration" only if the three sub-questions are read as
jointly defining what exploring means here (when to ask, how to keep, what transfers); otherwise
"identification and classification" is the tighter, already-requested fit. Answer: Confirm
"exploration" / Change to "identification and classification" / Change to ___ / Defer.

Item 3 (E8) - "human" or "expert" judgment across the question set?

The 2026-08-05 record shows a lean toward "expert" - physicians specifically in the medical
domain, course/team-level rigor in software engineering - but no final word. Recommendation:
"expert" reads more defensible for a doctoral contribution (it names who the judgment source is
and why it counts as authoritative) and matches Chapter 4's own artifact language, which already
says "expert judgment" throughout. Answer: Confirm "human" / Change to "expert" / Change to ___ /
Defer.

Item 4 - Plan A / Plan B boundary wording

Used informally everywhere as: Plan A is a gated medical extension, conditional on six entry
gates (G1-G6); Plan B completes every research question through software/modeling alone and
becomes the committed path if any gate lacks an owner, evidence path, and feasible date by the
2026-08-26 checkpoint. Recommendation: confirm this exactly as written, since three-study-contract.
md, chapter-4-research-methodology.md, and the 2026-08-12 record all already depend on it holding.
Answer: Confirm as written / Correct to ___ / Defer.

Item 5 - Evidence-boundary wording

Used informally everywhere as: no accuracy, generalization, effort-reduction, or clinical-
performance claim is made until EXP-005 reaches at least 20 of 24 generalization-safe adjudicated
labels; medical claims additionally wait on all six entry gates; literature-completeness or
novelty claims wait on QL-01 through QL-05 actually running. Recommendation: confirm as written -
every chapter drafted so far is built on exactly this boundary holding. Answer: Confirm as written
/ Correct to ___ / Defer.

Once answered, record the outcome in decision-change-log.md and re-run
scripts/validate_iris_requirements_closure.py --all --mode readiness to confirm the 0 of 10 count
above moves.
