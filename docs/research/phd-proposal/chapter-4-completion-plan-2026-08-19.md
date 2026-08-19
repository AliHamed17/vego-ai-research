# Chapter 4 completion plan — 2026-08-19

Prepared for: Ali, for use with Iris Reinhartz-Berger and Arnon Sturm.
Status: working plan; nothing here overrides Iris's own 2026-08-12 sequencing instruction
(literature review only this week, methodology work starts the week after and only if the
literature review is judged done). Ali has chosen to proceed with this plan now regardless, so
this document exists to make that choice as low-risk as possible: it separates what can honestly
be finished today from what genuinely needs a supervisor decision or a real person, so no part of
Chapter 4 gets presented as more settled than it is.

## Why a "completion plan" instead of just finishing the chapter

Chapter 4 (`chapter-4-research-methodology.md`, drafted 2026-08-18) already recommends one artifact
per sub-question and lists 7 open items in its own §4.7. Those 7 items are not uniform in kind:

- Some are genuine supervisor decisions (artifact granularity, the SQ2/SQ3 boundary, evidence
  admissibility ahead of `EXP-005`, whether `EXP-009`/`EXP-010` may appear before `M-04`). No
  amount of further writing closes these — they need Iris and Arnon's answer, the same way the
  five items in `2026-08-19-decisions-packet.md` do.
- One is a real-world resourcing action (naming a second Study 2 implementer and two Study 3
  raters). Writing cannot manufacture real people; fabricating placeholder names would violate
  this project's own evidence-boundary discipline.
- The rest are structural/editorial calls within normal methodological judgment that do not
  require new supervisor authority to make, and can be closed today.

Treating all 7 the same way — either leaving them all open, or writing past all of them as if
already resolved — would be worse than sorting them. This plan sorts them.

## Item-by-item disposition

| §4.7 item | Kind | Disposition today | Where it lands |
| --- | --- | --- | --- |
| Artifact granularity/abstraction level (items 6-7) | Supervisor decision | Packaged for a Confirm/Correct/Defer answer | `2026-08-19-chapter4-decisions-packet.md`, Item 1 |
| SQ2/SQ3 boundary (item 8) | Supervisor decision | Packaged | Same packet, Item 2 |
| Instrument-reliability admissibility ahead of `EXP-005` (item 9) | Supervisor decision | Packaged | Same packet, Item 3 |
| EXP-006/007/008 as preliminary results, exact wording (item 10) | Already has a working answer in practice | Documented as precedent, not re-opened | See "Item 10 already has a working answer" below |
| `EXP-009`/`EXP-010` before `M-04` (item 11) | Supervisor decision | Packaged | Same packet, Item 4 |
| Plan A placement: appendix vs. parallel (item 12) | Editorial/structural | Resolved now | Chapter 4 §4.2, edited today |
| Naming the Study 2 implementer and two Study 3 raters (item 13) | Real-world resourcing action | Cannot be resolved by writing; drafted a request Ali can actually send | `docs/operations/study-resourcing-request-template.md` |
| When sequencing formally lifts (item 14) | Ali's own call, already made | Superseded — Ali chose to proceed now | This document |

## Item 10 already has a working answer

Chapter 5 (`chapter-5-preliminary-results.md`, written 2026-08-19) already reports EXP-006, EXP-007,
and EXP-008 as preliminary results, using exactly the framing item 10 asked about: mechanism and
observability evidence, never effort reduction, with EXP-007's per-mode routed-item counts
explicitly excluded from any effort-reduction reading. That is a real precedent, not a new
argument — Chapter 4 §4.3 already states the same rule prospectively. The remaining gap is narrow:
Chapter 5 exists and follows the rule, but nobody has told Iris and Arnon it exists or asked them
to confirm the wording is acceptable. That confirmation is folded into the decisions packet as a
housekeeping note rather than a full new item, since the substantive question is already answered
by precedent.

## What "build it" means for today's execution pass

Beyond closing the 7 items, "build and do it" also means making each of the three recommended
artifacts more concrete — moving from "a cost/coverage model" to the actual functional form, field
list, or decision states a reviewer could evaluate — without crossing into claiming the artifact is
built, validated, or evidenced beyond what already exists. Today's pass:

1. Resolves Plan A placement in Chapter 4 §4.2 (item 12).
2. Adds a fully specified functional form for Study 1's attention-budget cost/coverage model in
   §4.3 — the exact inputs, the two output quantities, and how the four already-replayed dosage
   modes map onto it as parameter points, so the model is something a reader could actually
   compute against the existing EXP-006/007/008 evidence.
3. Adds the exact field list and validity states for Study 2's judgment-record contract in §4.4,
   and the exact pass/fail structure of its conformance suite, so "conformance testing" in that
   section stops being an abstract phrase and becomes a specification someone could implement
   against.
4. Adds the exact decision states and required inputs for Study 3's transfer-eligibility procedure
   in §4.5, so "eligible / eligible with adaptation / blocked" has a defined basis rather than
   being three unspecified labels.
5. Every addition keeps the chapter's existing hedge language (`recommended`, `proposed`,
   `research hypothesis, not a validated contribution`) attached, and does not add any claim not
   already licensed by `three-study-contract.md`'s excluded-measures rows or Chapter 4 §4.6's
   evidence boundary.
6. Packages items 6-9 and 11 as `2026-08-19-chapter4-decisions-packet.md`.
7. Drafts `docs/operations/study-resourcing-request-template.md` for item 13.
8. Updates Chapter 4's own §4.7 to show the new disposition per item, so the chapter does not read
   as if all 7 items are still uniformly open once this pass lands.

## What remains genuinely open after this pass

Items 1, 2, 3, and 4 of the new Chapter 4 decisions packet, and the resourcing request in item 13,
still require Iris, Arnon, or Ali's own outreach respectively. This plan does not and cannot close
those — it only makes sure each is asked in a form that can actually be answered quickly, the same
discipline the existing `2026-08-19-decisions-packet.md` already applies to `D-RQ-01`/`D-RQ-02`,
`E6`, `E8`, and the Plan A/B and evidence-boundary wording.
