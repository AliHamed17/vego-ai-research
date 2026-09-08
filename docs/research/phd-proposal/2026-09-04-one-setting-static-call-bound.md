# Study 1 static provider-call bound

This is a static formula only. It was produced without invoking a provider and
must be recalculated from the selected setting immediately before authorization.

Let `N` be the number of case models and `R = MAX_QA_ROUNDS = 10`
(`VEGO-AI/framework/orchestrator.py:36`). The protected orchestrator
(content SHA-256
`fca4b885ee07381db0f02e558b1aebf25bdc7c27da1c471fd3103d7e0e2d5b88`)
contains exactly ten `client.call` sites. The machine-readable inventory that
this document summarizes is `scripts/study1_call_bound.py::CALL_SITES`
(17 accounting rows: one per invoking control-flow position; the shared answer
helpers at `orchestrator.py:87` and `:110` make exactly one call per
invocation, so their multiplicity belongs to the loop that invokes them).
The module derives every constant by summing that inventory and refuses to
import if the sums disagree with the published formulas.

## Call-site inventory (fixed scope)

| Row | Label | Conditional | Min | Max | Evidence |
|---|---|---|---:|---:|---|
| P1_TEMPLATE | `agent1/build_language_template` | no | 1 | 1 | `orchestrator.py:59` |
| P2_GUIDELINES_PRODUCER | `agent2/guidelines_round{n}` | no | 1 | R=10 | loop `:135`; call `:149`; break `:158-160` |
| P2_LANG_ANSWERS | `agent1/answer_language_questions` | yes | 0 | R=10 | branch `:162`; call `:87` |
| P2_DOM_ANSWERS | `agent2/answer_domain_questions` | yes | 0 | R=10 | branch `:165`; call `:110` |
| P4_IDENTIFY | `agent4/identify_patterns` | no | 1 | 1 | `:356` |
| P4_CLASSIFY_PRODUCER | `agent4/classify_r{n}` | no | 1 | R=10 | loop `:362`; call `:372`; break `:377-378` |
| P4_CLASSIFY_LANG_ANSWERS | `agent1/answer_language_questions` | yes | 0 | R=10 | branch `:380`; call `:87` |
| P4_CLASSIFY_DOM_ANSWERS | `agent2/answer_domain_questions` | yes | 0 | R=10 | branch `:382`; call `:110` |
| P4_FEEDBACK_PRODUCER | `agent2/guidelines_feedback_r{n}` | yes | 0 | R=10 | gate `:395` (`if flagged`); loop `:408`; call `:419` |
| P4_FEEDBACK_LANG_ANSWERS | `agent1/answer_language_questions` | yes | 0 | R=10 | branch `:425`; call `:87` via `:428` |
| **Fixed subtotal** | | | **4** | **82** | `1+1+0+0+1+1+0+0+0+0 = 4`; `1+10+10+10+1+10+10+10+10+10 = 82` |

## Call-site inventory (per-case scope, Phase 3)

| Row | Label | Conditional | Min | Max | Evidence |
|---|---|---|---:|---:|---|
| P3_MAP | `agent3/{case}/map` | no | 1 | 1 | `orchestrator.py:210` |
| P3_RESOLVE_PRODUCER | `agent3/{case}/resolve_r{n}` | no | 1 | R=10 | loop `:213`; call `:225`; break `:230` |
| P3_RESOLVE_LANG_ANSWERS | `agent1/answer_language_questions` | yes | 0 | R=10 | branch `:234`; call `:87` |
| P3_RESOLVE_DOM_ANSWERS | `agent2/answer_domain_questions` | yes | 0 | R=10 | branch `:237`; call `:110` |
| P3_AUDIT_PRODUCER | `agent3/{case}/audit_r{n}` | no | 1 | R=10 | loop `:246`; call `:258`; break `:263` |
| P3_AUDIT_LANG_ANSWERS | `agent1/answer_language_questions` | yes | 0 | R=10 | branch `:266`; call `:87` |
| P3_AUDIT_DOM_ANSWERS | `agent2/answer_domain_questions` | yes | 0 | R=10 | branch `:268`; call `:110` |
| **Per-case subtotal** | | | **3** | **61** | `1+1+0+0+1+0+0 = 3`; `1+10+10+10+10+10+10 = 61` |

## Bounds

| Quantity | Formula | N=0 | N=1 | N=4 |
|---|---|---:|---:|---:|
| Minimum | `4 + 3N` | 4 | 7 | 16 |
| Worst case | `82 + 61N` | 82 | 143 | 326 |

The minimum is the direct no-question control-flow sum of the unconditional
rows: fixed `1 + 1 + 1 + 1 = 4` (Phase 1 template, first Phase 2 guideline
round, Phase 4 identify, first Phase 4 classify round) plus per-case
`1 + 1 + 1 = 3` (map, first resolve round, first audit round). Conditional
answer routes and the flag-gated feedback loop contribute zero to the minimum.
The worst case sums every row's maximum with `R = 10`; the Q&A-dependent worst
component within the fixed scope is `82 − 4 = 78`.

## Corrections carried by this revision

- The earlier statement `22 + 61N = 326` was arithmetically wrong
  (`22 + 61×4 = 266`, not 326) and is barred from reintroduction by
  `test_legacy_wrong_formula_is_not_reintroduced`; the verified fixed
  worst-case component is 82.
- The earlier `6 + 3N` minimum incorrectly treated the optional Phase 2
  language/domain answer routes as mandatory fixed calls; the unconditional
  path is `4 + 3N`.

`scripts/tests/test_study1_call_bound.py` derives its expectations from the
inventory rows (not from the published constants), checks N ∈ {0, 1, 4}, both
subtotals, `MAX_QA_ROUNDS = 10`, and rejects negative, fractional, and boolean
`N`. The offline fake-client counter records the direct path as `N=0 → 4`,
`N=1 → 7`, `N=4 → 16`; it does not invoke a provider.

`max_concurrent_cases` is the configured semaphore limit (2 in the offline
fixture; the real setting must supply its value). The configured model is
inherited from the selected run configuration and is not assumed here.
Token counts, provider pricing, and monetary cost are **TO BE MEASURED**; no
API call or cost estimate was fabricated.
