# Study 1: where and when should VEGO-AI ask a human?

**Supervisor review draft — 3 September 2026**
**Status:** completed descriptive baseline and technical rehearsal; prospective human-outcome claims remain untested and require approval.

## Question, data, and claim boundary

The immediate Iris-aligned study asks **where in the four-stage pipeline a human could be asked, and which current signals could trigger that ask**. It detects candidate points automatically and tests one bounded downstream correction. It does not compare accuracy or prove benefit. Adding **whom**—an authorized reviewer matched to a claim type—is a proposed later extension, not an approved RQ change.

## Frozen data and three intervention points

The frozen Cheers/ParkWise package contains 179 scored rows, 165 inspection reports, and 27 pattern records. The working manuscript separately reports 178 models and 26 patterns; this unresolved difference is preserved. No agent was rerun, no synthetic observation was used as evidence, and private student and reviewer material remains outside Git.

| Point | Where and rule | Size of ask / recorded evidence | Evidence-honest interpretation |
|---|---|---:|---|
| **H1** | Domain guidelines, before scoring: review once per case | 119 guidelines govern 4,853 later judgments; 68/169 (40.2%) were not accepted in full; 17 required guidelines were absent | No reliable recorded separator supports selective review; unconditional case-level review is the baseline. |
| **H2** | Inspector, per model–guideline claim: ask when verdict is not *Satisfied* | Flags 257/915 (28.1%) and contains 108/120 (90.0%) recorded compliance changes | Retrospective attention-versus-change coverage in a selected project review; not accuracy, recall, or benefit. |
| **H3** | Variability classifier: retain the implemented trigger | 11/27 (40.7%) patterns were trigger-like; zero queue objects were materialized | A candidate hook exists, but no independent labels exist. |
| **Rehearsal** | Four-stage event adaptation plus one recorded correction | 1,874 events; budgets 93/187/374. One correction changed 17.5/27 to 16.5/27; paired runs were byte-identical | Detection, fail-closed routing, and deterministic propagation only. |

## Measurable now versus evidence still required

| Measure | Current value and interpretation |
|---|---|
| Review load | `selected / eligible = 257/915 = 28.1%` for H2. |
| Recorded-change coverage | `changed selected / all recorded changes = 108/120 = 90.0%`; retrospective, not recall. |
| Recorded-change yield | `changed selected / selected = 108/257 = 42.0%`; descriptive, not precision. |
| Technical reproducibility | Paired event, replay, and correction artifacts have matching canonical hashes. |
| Not measured yet | Independent correctness/benefit, reviewer minutes, interruptions, queue delay, qualification, authority, or generalization. |

## Tomorrow: show, decide, then measure prospectively

| Show as completed | Ask Iris to confirm |
|---|---|
| H1–H3 automatic candidate detectors; frozen descriptive baseline; one bounded correction; denominator-audited receipt; explicit limits. | Keep the immediate scope at **when/where**; accept/revise 10% attention budget; define reviewer qualification and authority; approve collection of independent prospective labels. |

After approval, compare seven arms—never, always, deterministic random, uncertainty-only, fixed threshold, competence-blind, and competence/authority constrained—at 10% (5% and 20% sensitivity). Measure important-case capture and reviewer-conditional correctness; also review minutes per 100 claims, interruptions, queue delay, disagreement, budget utilization, and useful adjudicated corrections per reviewer-hour. Use queue-aware simulation for state-dependent policies.

## Decisions and stop conditions

- Confirm H1–H3 as the descriptive **when/where** baseline and select the prospective design.
- Stop benefit or superiority claims while independent labels, reviewer observations, or ethics/data approval are missing; EXP-005 remains 0/24 independent expert labels.
