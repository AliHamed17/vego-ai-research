# Q&A Escalation Signal Preregistration

## 1. Status and freeze date

**Preregistration. Frozen 2026-09-04, before any new Q&A data are generated.** This document fixes the
scientific policy — unit of analysis, admissible signals, detector logic, setting-selection rule,
feasibility criteria, and descriptive analysis plan — in advance of the one-setting instrumented run that
Codex is preparing. No such run has occurred at the time of this freeze: the interaction-log recovery
audit of 2026-09-04 concluded `NOT FOUND — LOCAL SEARCH EXHAUSTED`, and no instrumented run has yet been
executed. This document does not inspect, and was not informed by, any run output, because none exists.

This is a scientific policy record, authored by the methodological lead. It does not modify VEGO-AI
framework code, schemas, or any Codex implementation or test file.

## 2. Supervisor motivation

Arnon: the first stage is only to identify the cases in which human intervention is required, with no
relation yet to whether intervention improves anything — define the conditions, build an automatic
detector, run it, and determine which alerts are correct. Iris: the study should not be organised
primarily around individual agents; it should examine inter-agent communication, especially Q&A, and
possibly the agents' answer confidence. Arnon agreed communication is important. This preregistration
exists to prevent the detector or its thresholds from being chosen after the new data are seen.

## 3. Study question

Can observable patterns in VEGO-AI's inter-agent Q&A communication be used to automatically identify
situations in which human expert intervention may be warranted? This addresses the **WHEN** component of
provisional SQ1. *(SQ1 wording is provisional and not supervisor-approved.)* No effectiveness, benefit, or
accuracy claim is in scope.

## 4. Unit of analysis

**One complete Q&A communication episode**, defined structurally against the orchestrator's own control
flow, not in terms of any eventual human label.

The orchestrator runs five independent round-loops, each bounded by `MAX_QA_ROUNDS = 10`
(`orchestrator.py:35`): phase 2 guideline building (`:134`), Model Inspector skill 3-2 (`:212`), skill 3-3
(`:245`), Variability Explorer skill 4-2 (`:361`), and the guidelines feedback loop (`:407`). An episode is
scoped to exactly one execution of one such loop, for one context unit (the whole run for phase 2 and the
feedback loop; one `case_id` for skills 3-2/3-3/4-2).

- **Starts** when round 1 of that loop produces at least one non-empty entry in
  `questions_to_language_advisor` and/or `questions_to_domain_advisor`.
- **Continues** through round `n+1` if the loop's own condition for continuing is met — in the frozen code
  this is the negation of `if not q_lang and not q_dom: break` (`orchestrator.py:157-159`): the routed
  advisor's answer leaves at least one further non-empty question list from the same loop.
- **Ends** in exactly one of two states: **CONVERGED**, when a round produces no further questions and the
  loop's `break` fires; or **TERMINATED_MAX_ROUNDS**, when round `MAX_QA_ROUNDS` completes without
  convergence — the code's own boundary, marked at four call sites by
  `logger.warning("...reached MAX_QA_ROUNDS...")` (`:169`, `:240`, `:270`, `:384`, `:429`).

**This unit is not yet observable from persisted state.** `qa_registry.py` (verified byte-identical between
the frozen package and the current repository) records only a flat, globally sequential ID counter
(`Q_lang_NNN` / `Q_dom_NNN`, `qa_registry.py:33-37`) and two flat accumulation lists, `lang_qa` / `dom_qa`
(`:27-28`, appended only by `record_answers`, `:50-55`). No round number, episode identifier, or follow-up
linkage is persisted anywhere in the code inspected. Making the unit observable is a Codex instrumentation
dependency; see §15.

Communication is the primary object of the unit (Iris); every reported measure is additionally stratified
by source agent, source stage/skill, and target agent (Arnon) — see §14.

## 5. Candidate signal adjudication table

Every admission decision is grounded in quoted code or prompt text; no threshold is chosen by inspecting a
distribution.

| # | Signal | Verdict | Grounding |
| --- | --- | --- | --- |
| S1 | Low Q&A answer confidence | **ADMIT PRIMARY** (after corpus) | `confidence` is a mandatory, closed field, `High \| Medium \| Low` (`agent1_language_advisor.py:224`, mirrored `agent2_domain_advisor.py:487`). `Low` is defined by the prompt itself as "relies on trained knowledge; no direct artefact support" (agent1) / "relies on general knowledge; no direct artefact support" (agent2) — an architecture-defined, not inspected, threshold. |
| S2 | Medium Q&A answer confidence | **ADMIT PRIMARY** (after corpus) | Same field; `Medium` is defined as "inferred from context within the artefacts." |
| S3 | Answer without direct evidence | **ADMIT PRIMARY** (after corpus) | `evidence` is a mandatory field required to be a verbatim citation ("VERBATIM excerpt … DO NOT PARAPHRASE", both agents). An empty or non-citing value is a structural absence, checkable without NLP. |
| S4 | Answer based on an explicit lower-priority / trained-knowledge source | **ADMIT SECONDARY / EXPLORATORY** | Grounded only for the language channel: the prompt defines a four-tier `SOURCE PRIORITY`, tier 4 "trained knowledge (flag explicitly when used)" (`agent1_language_advisor.py`, source-priority block). No dedicated structured field carries the tier; it can only be recovered by literal-phrase detection over the free-text `justification`/`evidence` fields, which is fragile against paraphrase. It is also analytically close to S1: the prompt's own definition of `Low` confidence already names "relies on trained knowledge" as the reason. Treated as exploratory and reported separately from S1 rather than folded into it, so the overlap can be measured rather than assumed. |
| S5 | Repeated / follow-up clarification | **REJECT for v1; ADMIT SECONDARY once instrumented** | No follow-up/parent-question linkage field exists anywhere in the inspected code (see §4). Cannot be computed as written. |
| S6 | Multiple Q&A rounds before resolution | **ADMIT PRIMARY** (after corpus and after episode/round instrumentation) | Directly grounded in the orchestrator's own round loop and `MAX_QA_ROUNDS` constant (§4). Requires the round number to be persisted per record — a named Codex dependency, not yet met. |
| S7 | Non-convergence / reaching `MAX_QA_ROUNDS` | **ADMIT PRIMARY** (after corpus and instrumentation) | Directly grounded in the same code; the four `logger.warning` sites are the system's own definition of non-convergence. This is the closest observable proxy to an unresolved episode, and is preferred over "unanswered question," which was rejected as a v1 signal in the prior study freeze because it was true of 100% of the frozen (harness-broken) corpus by construction. Under the orchestrator (which does execute the Q&A loop), an unresolved episode is only meaningful as `TERMINATED_MAX_ROUNDS`, so this signal supersedes rather than repeats the earlier rejected one. |
| S8 | Follow-up question after an answer | **REJECT for v1; ADMIT SECONDARY once instrumented** | Same missing-linkage-field limitation as S5. If Codex's instrumentation adds an episode/round schema, S8 becomes distinguishable from S6 by requiring the follow-up to be a new question addressed to the same target within the same episode, rather than merely counting rounds. |
| S9 | Unusually high question density within one decision episode | **REJECT for v1** | No episode grouping key exists to define "one decision episode" as a denominator (§4). Cannot be computed as written; revisit once instrumented. |
| C1 | Agent-2 `mapping_certainty` | **ADMIT — contextual comparator, not a Q&A signal** | Threshold is **`< 0.7`**, quoted verbatim from the architecture contract: "For every guideline whose mapping_certainty is below 0.7, you MUST raise a Q_lang question asking Agent 1 to confirm or correct the template assignment" (`agent2_domain_advisor.py`, guideline-creation and update-iteration instructions, both occurrences). This is the system's own internal escalation trigger from Agent 2 to Agent 1, not an inspected convenience cut. **Correction to the current technical scaffold:** `docs/research/phd-proposal/2026-09-03-qa-escalation-observability.md` §"Frozen counts and features" reports feature F11 at `≤ 0.75`; no text grounds `0.75`. The frozen threshold for any future computation of C1 is `< 0.7`, and this discrepancy is handed to Codex to reconcile (§15), not corrected in that file directly. |
| C2 | Agent-4 classification confidence | **ADMIT — contextual comparator only** | Already established in the prior evidence freeze: `requires_human_review` is false on all 27 frozen patterns, and Agent-4 has no independent reference (`analysis/agentD_*` is md5-identical to `eval_output`). Usable only as a contextual descriptor, never as Q&A evidence, and never compared against itself as ground truth. |
| C3 | Explicit `requires_human_review` / guideline-update flags | **ADMIT — contextual comparator only** | `flag_for_guidelines_update` is already established as perfectly co-extensive with `classification == "Substantial Variability"` (9 of 27) and therefore carries no information beyond that class label; reported as context, not as an independent signal. |

**Not admitted at any tier:** `agent2_domain_advisor.py`'s `scope_errors` field (a language/domain
mis-routing record) exists structurally and is supported in code, but is outside the nine signals and
three contextual comparators specified for this preregistration. It is noted here for completeness and is
not part of Detector v1; adding it later requires the change-control procedure in §16.

## 6. Detector-v1 frozen policy

**Structure: strict logical OR over admitted primary signals, computed independently per episode.** A
tiered or weighted structure would require a justification this preregistration does not have evidence
for, and would risk looking like post-hoc calibration; an OR over explicitly grounded, binary conditions
is the smallest structure that satisfies "transparent, deterministic, rule-based, auditable, no ML, no
fitted weights, no empirical tuning, no labels."

| Rule | Input field | Condition | Reason code |
| --- | --- | --- | --- |
| R1 | `confidence` | `== "Low"` | `S1_LOW_CONFIDENCE` |
| R2 | `confidence` | `== "Medium"` | `S2_MEDIUM_CONFIDENCE` |
| R3 | `evidence` | empty, or does not contain a parseable artefact citation | `S3_NO_EVIDENCE` |
| R4 | round count for the episode | `> 1` | `S6_MULTI_ROUND` |
| R5 | termination state | `== TERMINATED_MAX_ROUNDS` | `S7_NON_CONVERGENCE` |

An episode receives **ALERT** if any of R1–R5 fires, and **NO ALERT** otherwise: `confidence == "High"`,
`evidence` present and citing, exactly one round, and the episode `CONVERGED`. Every alert carries every
reason code that fired, not only the first. S4/S5/S8/S9 are excluded from v1 by §5 and may only enter a
later, explicitly versioned revision (§16). C1/C2/C3 are reported alongside every episode as context and
never contribute to the ALERT decision.

## 7. Strong vs. weak signals

Evaluated on the evidence available, not asserted by convention.

**Strong (highest-priority escalation indicators): S1 (Low confidence) and S7 (non-convergence).** Both are
the system's own explicit statements that it could not ground an answer in artefact evidence, or could not
resolve a question within its own designed bound. Neither depends on interpretation.

**Weaker / exploratory: S2 (Medium confidence), S6 (multiple rounds), S4.** Medium confidence is explicitly
defined as "inferred from context" — the system did find support, only indirectly — which is a materially
different claim from Low. Two rounds instead of one records only that a clarification occurred, not that
the outcome is suspect; a converged two-round episode may be a routine refinement. S4 is weak because of
its structural fragility (§5) and its overlap with S1.

The example given in the task brief — "Low confidence, unsupported-answer, and exhausted rounds are
stronger than Medium confidence, two rounds, or multiple questions" — is evaluated rather than assumed, and
is upheld for S1/S7 vs. S2/S6 on the grounds above. S3 (no evidence) is treated as comparably strong to S1,
since the two are often the same underlying event (a Low-confidence answer typically also lacks a citable
artefact), and this overlap is itself worth reporting descriptively rather than resolved by ranking one
above the other in advance.

## 8. Setting-selection policy — frozen before the run

**Rule, fixed in advance:**
1. Exclude any setting whose required run inputs are not verified complete immediately before execution.
2. Among complete settings, choose the one with the highest historical question-emission count from the
   frozen 12-question canonical snapshot.
3. Tie-break, if needed: ascending alphabetical order of the setting identifier (`cd_ch` < `cd_pw` <
   `ucd_ch` < `ucd_pw`), lowest wins — arbitrary but fixed before any run, not chosen from a future outcome.
4. The choice is never revised based on a detector or alert outcome.

Historical counts: `cd_pw` 6, `cd_ch` 3, `ucd_ch` 2, `ucd_pw` 1 (12 total), all from the canonical
`questions_to_language_advisor` snapshot already frozen in the study evidence.

**Provisional first choice: `cd_pw`, conditional on a completeness re-check at execution time.** One
concrete, currently verifiable input asymmetry supports this: the repository's tracked `VEGO-AI/inputs/`
carries `pw/domain_base_cd.txt` and `pw/domain_base_ucd.txt`, while no `ch/domain_base_cd.txt` or
`ch/domain_base_ucd.txt` exists at any tracked path (`git ls-tree -r HEAD -- VEGO-AI/inputs`). The Cheers
domain descriptions themselves (`ch/domain_description*.txt`) are present, so this asymmetry does not by
itself prove Cheers cannot generate Q&A — the domain-base files are the course's ground-truth requirement
list used by Agent-B *coverage evaluation*, not confirmed here as required for the Q&A-generating phases.
No case-model input directory is tracked for **any** setting in the repository, so that dimension is common
to all four settings and does not differentiate them; case models would need to come from the supplied
package or a location Codex names.

**This is a purposive high-information feasibility selection, not representative sampling.** `cd_pw`'s count
of 6 is the largest available signal that Q&A behaviour occurs at all in this system; it is chosen to
maximise the chance of observing a non-degenerate corpus for feasibility purposes, not to estimate a rate
that would generalise to the other three settings.

The final completeness verification against whatever input set the instrumented run script actually reads
is a Codex technical dependency (§15), to be executed immediately before the run and reported, not assumed
from this document.

## 9. Feasibility success / failure criteria

Defined before the run; no criterion may be adjusted after seeing output.

- **TECHNICAL SUCCESS** — the instrumented run completes without a harness error, and produces at least
  one persisted, complete episode: a question and its matching answer, with `confidence` and `evidence`
  populated, and round/termination state reconstructable per §4/§15.
- **SCIENTIFICALLY USABLE DATA** — at least **5** technically complete episodes. Justification: this is a
  descriptive-adequacy floor, not a statistical power calculation. The frozen corpus has never shown more
  than 6 questions in any single setting, so 5 is the largest round number smaller than that historical
  ceiling that still permits describing more than a single anecdote (a frequency, not just a point). No
  inferential or generalising claim is licensed at this or any larger n reached by one setting.
- **PARTIAL SUCCESS** — between 1 and 4 technically complete episodes. Usable only as a single qualitative
  worked example per episode; no distribution, rate, or prevalence figure may be reported.
- **FAILURE** — zero technically complete episodes: the run either produced no non-empty question lists,
  or answers failed to persist, confidence/evidence remained empty, or the episode boundary could not be
  reconstructed.

## 10. Expansion rule

**EXPAND** beyond the first setting only if all of: (a) the first run meets TECHNICAL SUCCESS; (b) it
meets SCIENTIFICALLY USABLE DATA, not merely PARTIAL; (c) at least one admitted primary signal (S1, S2,
S3, S6, S7) shows non-degenerate variance across the recovered episodes (not every episode identical on
every signal); and (d) expansion is needed specifically to observe a communication route not exercised by
the first setting — for example, a Domain-Advisor-directed question (`questions_to_domain_advisor`), which
has zero historical occurrences in any of the four frozen settings and therefore carries only weak prior
support for expecting it elsewhere either.

**STOP** after one setting if it reaches SCIENTIFICALLY USABLE DATA and condition (d) is not met — proceed
directly to the descriptive analysis in §11 rather than expand without a stated architectural reason.

**REVISE INSTRUMENTATION** if TECHNICAL SUCCESS is not met — return to Codex before any analysis is
attempted; do not analyse output from a run that failed its own technical criteria.

Expansion is never triggered because a result is undesirable — a low alert rate, mostly `High` confidence,
or few multi-round episodes are all legitimate scientific outcomes of this study, not reasons to seek more
data.

## 11. Descriptive analysis plan

No human labels exist at this stage; nothing below may be interpreted as a rate of correctness.

**Primary measures:** number of complete episodes; questions per episode; rounds per episode; confidence
distribution (`High`/`Medium`/`Low`); evidence-presence rate; convergence rate (`CONVERGED` vs.
`TERMINATED_MAX_ROUNDS`); candidate `ALERT` count and rate; alerts by reason code; alerts by source
agent/stage and target agent (§14).

**Secondary measures:** co-occurrence of reason codes within one alert (for example, how often R1 and R3
fire together, bearing on the S1/S3 overlap noted in §7); C1/C2/C3 contextual distributions reported
alongside, never combined into the alert decision.

None of the above may be called accuracy, precision, recall, effectiveness, or benefit.

## 12. Allowed claims

That certain observable, code-grounded communication features of a VEGO-AI Q&A episode — confidence,
evidence presence, round count, and convergence state — can be computed deterministically from frozen
run output and used to raise a transparent, auditable candidate alert. That the resulting alert counts and
distributions describe this one purposively selected setting and do not generalise to the others without
further data.

## 13. Forbidden claims

True alerts; false alerts; precision; recall; F1; accuracy; missed intervention; human benefit;
effectiveness; that intervention improves VEGO-AI; that a single-setting result is representative. No
synthetic or AI-generated label may substitute for an independent reference. Q&A answer confidence is an
LLM self-report — an observable system signal, not a calibrated probability and not ground truth — and must
never be presented as either. It must remain reported separately from Agent-2 `mapping_certainty` and
Agent-4 classification confidence, which have different producers and different semantics (§5).

## 14. Threats / limitations

Single purposively-selected setting: results are a feasibility demonstration, not an estimate that
transfers to the other three settings. Confidence is self-reported by the same model whose behaviour is
under study, with no independent check on calibration. `mapping_certainty` is read by zero code paths
today (established in the prior evidence freeze) and is included here only as a comparator, not because
any part of the system currently acts on it. The unit of analysis (§4) depends entirely on instrumentation
not yet built; if that instrumentation captures round/episode state differently than specified here, this
document's definitions — not the instrumentation's — must be revisited under change control (§16), and the
discrepancy reported rather than silently absorbed. The domain-question channel has zero historical
occurrences across all four settings; a null result there is not evidence the channel is broken, only that
it has never yet fired.

### 14a. Communication-route reporting

Every reported measure in §11 is broken down, at minimum, by: source agent (Agent 2, Agent 3, or Agent 4);
source stage/skill (phase 2 guideline build/update, skill 3-2, skill 3-3, skill 4-2, guidelines feedback
loop); target agent (Agent 1 or Agent 2); and scope (`lang` or `dom`). This reconciles Iris's
communication-centred unit with Arnon's request for a per-agent/stage breakdown. A route that is
`SUPPORTED_IN_CODE` but has zero historical observations (Agent 3 → either advisor; Agent 4 → either
advisor; Agent 2 → Agent 2 domain questions) is reported as a route with zero observed episodes, never as
an empirically confirmed absence of behaviour.

## 15. Dependencies on Codex instrumentation

The following must exist before §4's unit of analysis, and therefore any signal in §5 beyond C1–C3, is
computable. This document specifies what the science requires; the implementation is Codex's:

1. A stable `episode_id` per round-loop instance (phase/skill + case identifier or `global` + a sequence
   number), persisted on every question and answer record belonging to that episode.
2. A `round` number on every question and answer record, matching the orchestrator's own `round_n`.
3. A `termination_state` per episode: `CONVERGED` or `TERMINATED_MAX_ROUNDS`, set at the same code points
   already logging the corresponding warnings (§4).
4. Source agent, source stage/skill, and target agent tagged on every record (§14a).
5. Reconciliation of the C1 threshold: confirm whether
   `2026-09-03-qa-escalation-observability.md`'s F11 (`≤ 0.75`) should be corrected to `< 0.7` per §5, or
   whether a distinct, separately justified reason for `0.75` exists that this document has not seen.
6. A pre-run completeness check against whatever input set the instrumented run script actually reads for
   each of the four settings, reported before execution (§8).

Until items 1–3 exist, S5, S8, and S9 remain REJECT, and S6/S7 remain frozen as policy but not computable.

## 16. Change-control rule

Once this preregistration is committed, Detector-v1's rules (§6) may not be changed after the first real
run's output has been inspected, **except** where a field specified in §15 is technically unavailable, the
instrumentation is confirmed wrong, or a rule is impossible to compute exactly as written. Any such change
must be versioned (`v1.1`, dated), state exactly what changed and why, and be reported explicitly as a
**post-data change** — never silently substituted for v1. Adding S4, S5, S8, or S9 as primary signals,
adopting a non-OR detector structure, or changing any threshold in §5/§6 all require this procedure. This
document is not amended in place for such changes; a dated addendum or successor section records them.
