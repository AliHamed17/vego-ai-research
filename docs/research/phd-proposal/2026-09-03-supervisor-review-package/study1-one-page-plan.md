# Study 1: where and when should VEGO-AI ask a human?

**Supervisor review draft — 3 September 2026**
**Status:** completed descriptive baseline and technical rehearsal; prospective human-outcome claims remain untested and require approval.

## Question and claim boundary

The immediate Iris-aligned study takes the current SQ1's **when** as **where in the four-stage pipeline a human could be asked**. It identifies those points automatically and tests one bounded downstream correction. It does not compare accuracy or prove that asking improves an outcome. Adding **whom**—the authorized reviewer matched to a claim type—is a proposed later extension of SQ1, not an approved change.

## Frozen data and three intervention points

The supplied evaluation package contains 179 scored model rows, 165 per-model inspection reports, and 27 variability-pattern records for Cheers and ParkWise use-case/class-diagram settings. The working foundation manuscript separately reports 178 models and 26 patterns; the unexplained counting difference is preserved. No agent was rerun, no synthetic empirical observation was introduced, and private student and reviewer material remains outside Git.

| Point | Where and rule | Size of ask / recorded evidence | Evidence-honest interpretation |
|---|---|---:|---|
| **H1** | Domain guidelines, before scoring: review once per case | 119 guidelines govern 4,853 later judgments; 68/169 agent-written guidelines were not accepted in full, and 17 required guidelines were absent | No reliable recorded separator supports selective review here; unconditional case-level review is the current baseline. |
| **H2** | Inspector, per model–guideline claim: ask when verdict is not *Satisfied* | Flags 257/915 (28.1%) and contains 108/120 (90.0%) recorded compliance changes | Retrospective attention-versus-change coverage in a selected project review; not accuracy, recall, or benefit. |
| **H3** | Variability classifier: retain the implemented trigger | 11/27 patterns were trigger-like; zero queue objects were materialized | A candidate hook exists, but the co-authors judged this stage and no independent labels exist. |
| **Rehearsal** | Frozen four-stage event adaptation plus one recorded correction | 1,874 events; matched budgets 93/187/374. One label correction changed 17.5/27 to 16.5/27; two runs were byte-identical | Candidate detection, fail-closed routing, and deterministic propagation only. |

## Immediate measures and Saturday demonstration

For H1–H3, report the number and denominator sent to review by stage/setting, overlap with places the recorded reviewer changed a judgment, the H2 review-load/change-coverage curve, and the earliest stage at which a signal fires for each pattern. Demonstrate one manually injected, previously recorded correction end to end without rerunning an agent. Record the source hash, exact changed item, downstream score delta, and output hash; retain the original immutable.

## Next controlled benchmark — only after the descriptive gate

Freeze claim-level events, independent labels, calibration/test partitions, reviewer qualification observations, and a claim-scoped authority matrix. Compare never ask, always ask, deterministic random, uncertainty-only, fixed threshold, competence-blind routing, and competence-aware/authority-constrained routing at a 10% primary attention budget (5% and 20% sensitivity). Co-primary outcomes are important-case capture and reviewer-conditional correctness; time, interruptions, queue delay, disagreement, and yield are secondary. State-dependent policies require queue-aware simulation.

## Decisions and stop conditions

- Confirm that the immediate deliverable answers **when/where** through H1–H3 and remains descriptive.
- Approve or revise the later SQ1 wording, reviewer qualification method, authority owner, and 10% primary budget.
- Stop any benefit or superiority claim if independent labels, reviewer observations, or ethics/data approval are missing; EXP-005 remains 0/24 independent expert labels.
