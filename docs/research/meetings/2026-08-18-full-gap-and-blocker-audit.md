Full gap and blocker audit — 2026-08-18

Requested directly by Ali: every gap across the files needed to deliver the PhD proposal, what is
blocked, and what is currently missing. Sourced from live checks run today (the requirements-
closure validator, the frozen literature register, issues.md) plus the chapter files' own status
headers, not recalled from memory. Numbers below are what those checks actually printed.

---

1. The six proposal chapters, where each one actually stands

Chapter 1, Introduction: drafted, but written out of its real place in the sequence. The confirmed
order writes the Introduction last, after the research-question wording is signed off, so this
draft will be rewritten rather than edited once that happens. It already carries the same wording
caveat as everything downstream of it.

Chapter 2, Literature review: does not exist as a file in this repository. It is being produced on
a separate track (the "v9" scholarly-validation files Ali shared). That track's own receipt reports
QL-01 through QL-05 at 0 of 5 executed, one pinned disposition (ACL-116) incomplete, the
review-wide 40-to-60 full-text extraction target not met, human scholarly review pending, and
supervisor approval pending. The actual review document from that track (the PDF/DOCX named in its
own hash manifest) has not been shared into this session, so its content cannot be checked from
here, only its own self-reported gate state can be.

Chapter 3, Gap and Research Questions: a complete draft exists, not supervisor-approved. The
research-question wording in it is the live wording from the 2026-08-05 call and stays provisional
pending D-RQ-01/D-RQ-02.

Chapter 4, Research Methodology: a complete working draft exists (written 2026-08-15, rewritten
for style 2026-08-18). It recommends one artifact per sub-question rather than presenting a decided
design, and lists 8 open items in its own closing section, including two unnamed people: an
independent implementer to test Study 2's conformance suite, and two raters for Study 3's
reliability evaluation.

Chapter 5, Preliminary Results: does not exist as a file. Real evidence exists to build it from -
the offline replay series (EXP-006 through EXP-008) and the architecture-conformance series
(EXP-013 through EXP-018) are both actually run - but nobody has written the chapter that reports
them at their correct evidentiary scope.

Chapter 6, Work Plan: a complete working draft exists. Every date in it is stated as an internal
working target; the university process itself (action A-14) is open - no submission, candidacy, or
review date has been confirmed in writing by the university.

---

2. Wording and decisions that have never been signed off

Ran fresh today: `scripts/validate_iris_requirements_closure.py --all --mode readiness` reports
0 of 10 D-RQ decisions have an explicit recorded meeting outcome, and the closure certificate has
0 of 44 controls with a final disposition (the certificate is a template, not an issued document).
Specifically still open:

- D-RQ-01 / D-RQ-02, the exact final wording of the main research question and SQ1-SQ3.
- E6, "exploration" versus "identification/classification" in the main question.
- E8, "human" versus "expert" judgment across the question set.
- The Plan A/Plan B boundary wording, and the evidence-boundary wording, used informally
  throughout every document, never formally signed off.

---

3. The evidence gates behind every claim in the proposal, unchanged for months

- EXP-005: 0 of 24 required generalization-safe expert labels. Needs two independent reviewers
  plus an adjudicator, none named.
- Medical entry gates G1-G6: 0 of 6. No named expert, no approved VDI/storage, no approved
  local-model infrastructure, no protocol.
- Literature searches QL-01-QL-05: protocol-ready, not executed, true both in this repo's own
  frozen register and, independently, in the parallel v9 track's own receipt.

The 44-control register (19 requirements + 15 actions + 10 questions from the original July 29
extraction) currently sits at: 6 evidence-ready, 22 partial, 9 not-started-and-blocked, 5
not-started, 2 acceptance-check-passed, confirmed by today's structure-mode validator run.

---

4. New resourcing gaps, surfaced by writing Chapter 4

- No one is named as the independent implementer needed to prove Study 2's judgment-record
  contract isn't just VEGO-AI describing its own schema.
- No one is named as either of the two raters Study 3 needs for its transfer-eligibility
  reliability evaluation.

---

5. Administrative items, human-only, some time-critical

- Scholarship recommendation letter (A0812-06): a template exists
  (docs/operations/scholarship-recommendation-request-template.md), but as of this session it has
  not been confirmed sent. The deadline referenced on the call was "the 15th."
- Drive re-share with Arnon (A0812-05): last known state is still open; arnon.sturm@gmail.com was
  supplied on the 08-12 call for this.
- University candidacy process (ISS-024, open since 2026-07-30): the deadline, reviewer count,
  nomination path, committee rules, and presentation requirements have never been confirmed in
  writing by an authoritative university source. Every September/October date in this project is a
  working target, not a real deadline, until this closes.
- PhD Drive and literature Sheet general access (ISS-026, open since 2026-07-30): existence is
  confirmed; recipient-access testing with Iris is not.
- Clalit meeting, 2026-08-26 (A0812-07): scheduled, coincides with the Plan A/B go/no-go
  checkpoint.

---

6. Open on GitHub right now

Three open pull requests, none merged, none blocking the proposal directly but all open loose ends
in the repository itself:

- #19, "Realign the seminar deck to CL7 and cap it at 20 slides", opened by the concurrent session
  working the course deck, not yet reviewed here.
- #17, "Add August 12 evidence-to-delivery package", draft, conflicting with current main.
- #14, "Publish BigUI experiment evaluation...", over three weeks stale, conflicting, a separate
  Codex-driven workstream unrelated to the PhD proposal.

---

7. Longer-standing tracked issues, lower priority for the proposal itself, listed for completeness

- ISS-019, a CI trust-SHA sync rule needs agreeing across branches.
- ISS-020 / ISS-021, two figures in tracked docs (a benchmark pass/fail label, a "179 student
  models" count) were flagged as needing correction on 2026-07-28, not confirmed fixed since.
- ISS-025, the shared MIMIC resource's file count and provenance do not fully match the official
  MIMIC-III v1.4 table set, blocked pending medical governance.
- ISS-027 / ISS-028, the supervisor presentation package needs a human timed rehearsal and a
  rebuilt offline backup before the stale one can be replaced.
- ISS-030, a memory-script quirk leaves a stray trailing blank line, cosmetic, catches CI hygiene
  checks if not caught first.
- ISS-031, this machine has more than one active checkout of the same repository, already known
  and worked around, not fixed at the tooling level.
- ISS-002, ISS-005, ISS-006, ISS-007, ISS-011, ISS-012, ISS-013, ISS-014, smaller process notes
  about EXP-005 tooling, Confluence access, and evaluation leakage discipline; none block proposal
  delivery on their own.

---

What this adds up to: the proposal has real chapters at 3, 4, and 6, a real methodology
framework, and real, if narrow, mechanism-level evidence. What it does not have is any of the
three things a committee will ask about first: a finished literature review, a single
supervisor-signed decision, or one real expert label.
