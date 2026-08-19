Chapter 4 decisions packet — four items that block methodology sign-off

Prepared for: Iris Reinhartz-Berger and Arnon Sturm
Prepared by: Ali (drafted with AI assistance; every recommendation below is a suggestion, not a
decision)
Status: decision request; nothing in this file is recorded as approved until answered

Why this exists: `chapter-4-research-methodology.md` (drafted 2026-08-18, revised 2026-08-19)
recommends one artifact per sub-question and specifies each in enough detail to evaluate, but
Part 3 of `sections-2-and-4-thinking-notes.md` named several questions the chapter cannot answer on
its own authority. `chapter-4-completion-plan-2026-08-19.md` sorted those questions; the four below
are the ones that genuinely need Iris and Arnon's answer, not further writing. Each can be answered
the same way as the existing `2026-08-19-decisions-packet.md`: Confirm the working recommendation
as-is, Correct it (write the replacement directly on this page), or Defer it with a reason.

Item 1 (Part 3, items 6-7) — Is one narrower artifact per study the right granularity, or should
each study keep the broader, bundled artifact `three-study-contract.md` currently names?

Chapter 4 recommends replacing the bundled artifacts in `three-study-contract.md`'s "Core artifact"
row with one narrower artifact per study: for Study 1, an attention-budget cost/coverage model
(§4.3) rather than the six-component intervention architecture the contract currently names; for
Study 2, a judgment-record contract plus executable conformance suite (§4.4) rather than the
nine-component governed lifecycle the contract names; for Study 3, a transfer-eligibility decision
procedure plus context-descriptor schema (§4.5) rather than the ten-item evaluation-and-transfer
package the contract names. The recommendation's rationale, in short: a bundled artifact invites a
reviewer to dispute where its boundary sits and obscures which single claim actually generalizes,
while a narrower artifact is falsifiable on its own terms. Adopting this means `three-study-
contract.md`'s three "Core artifact" rows would need updating to match. Answer: Confirm / Correct
to ___ / Defer.

Item 2 (Part 3, item 8) — Where exactly is the SQ2/SQ3 boundary, so Studies 2 and 3 do not ship the
same artifact twice?

Study 2's judgment-record contract (§4.4) carries a `scope` field stating what a judgment is
authorized to speak to. Study 3's transfer-eligibility procedure (§4.5) separately classifies
whether a target context falls inside or outside that scope, with what adaptation. The chapter's
working position is that Study 2 owns *defining* scope (writing the field) and Study 3 owns
*applying* it against a new context (the relevance/applicability/authorization checks in §4.5) —
representation and lifecycle in one study, applicability and transfer decision in the other. This
has not been confirmed against the 2026-08-10 brainstorm's original framing of the risk. Answer:
Confirm / Correct to ___ / Defer.

Item 3 (Part 3, item 9) — Is instrument-reliability evidence admissible as a preliminary Study 2/3
result ahead of EXP-005, or does every evaluation wait for at least 20 generalization-safe
adjudicated labels?

Both Study 2's conformance suite (does an independent implementation conform, and does a
deliberately broken variant fail for a named reason) and Study 3's rater-agreement study (do two
raters reach the same eligibility verdict for the same reason) produce evidence about the
instrument, not about assessment accuracy — no expert gold labels are involved in either. Chapter 4
treats this as "gold-label-free rather than label-free" and admissible on its own terms, distinct
from and not a substitute for the EXP-005-gated accuracy questions. Correcting this would mean
withholding both results until EXP-005 reaches its threshold, which currently has no target date.
Answer: Confirm / Correct to ___ / Defer.

Item 4 (Part 3, item 11) — Do EXP-009/EXP-010 appear in the proposal at all before M-04 protocol
approval is recorded, and under what label if so?

EXP-009 and EXP-010 remain provisional synthetic fixtures per the experiment plan, gated on M-04.
Chapter 4 §4.4 currently treats them as not yet available evidence for Study 2's H-Verify/
convergence question and does not cite them as support for any claim. The working recommendation
is to keep them out of the proposal entirely until M-04 is recorded, rather than cite them with a
provisional-fixture caveat, since a caveated citation still risks being read as evidence. Answer:
Confirm / Correct to ___ / Defer.

Housekeeping note (Part 3, item 10) — EXP-006/007/008 as preliminary results, already in practice.

`chapter-5-preliminary-results.md` (written 2026-08-19) already reports EXP-006's event
reconstruction, EXP-007's per-mode load-versus-coverage counts, and EXP-008's unstable-but-never-
reviewed candidates as preliminary mechanism/observability evidence, with EXP-007's counts
explicitly excluded from any effort-reduction reading. This is not asking a new question — it is
flagging that the answer Part 3 item 10 asked about already exists in a committed chapter, and
requesting confirmation that the wording used there is acceptable rather than reopening the
question from scratch. Answer: Confirm the existing wording in Chapter 5 / Request changes to ___.
