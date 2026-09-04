# Q&A Escalation Signal Preregistration

## 0. Revision block

**Version: v1.0.1. Revision type: PRE-DATA CORRECTION. Data exposure before this revision: NONE.**

v1.0.0 was committed at `3a5b0d22658fdc3b9b81424d44a69687797dc278` (2026-09-04). Before this revision was
made, `main` advanced by two commits, both implementation/schema/test/documentation work with no live
run and no experimental result: `378be0a` "Add passive Q&A communication instrumentation" and `462c4e4`
"Clarify offline Q&A fixture coverage." Both were inspected as code/schema/contract, per the constraint
that implementation may be read to confirm field availability while no real-run output may be inspected;
none exists — `docs/research/phd-proposal/2026-09-04-qa-instrumentation-verification.md` confirms no live
model call was made and all four settings are currently `BLOCKED` on missing case-model inputs. This
revision is therefore still pre-data and legitimately correctable in place; it is not a post-data change
under §16.

Corrections made in v1.0.1, each identified in supervisor review of v1.0.0:

1. Removed the arbitrary `N ≥ 5` "scientifically usable" threshold (§9). Historical question emissions
   are not future complete episodes, and no defensible sample-size floor was ever established. Replaced
   with a criterion structure that reports exact N always and imposes no minimum for descriptive use.
2. Removed "non-degenerate signal variance" from the expansion rule (§10), which made expansion depend on
   the observed result. Replaced with a rule conditioned only on technical/structural facts.
3. Re-adjudicated S5, S8, S9 for internal consistency: S6/S7 were admitted despite depending on
   not-yet-persisted instrumentation while S5/S8 were rejected for the identical reason. Signals are now
   adjudicated by scientific determinism and grounding, not by today's persistence alone (§5).
4. Replaced S3's underspecified "parseable artefact citation" test with an unambiguous structural
   condition that requires no citation grammar (§5, §6).
5. Made the strong/weak distinction operational in Detector v1 via a two-tier precedence structure, and
   resolved the inconsistency between §7's prose (which called S3 comparably strong to S1) and the
   original strong-signal summary, which omitted it (§6, §7).
6. Corrected an overstated claim in §14 that no part of the system acts on `mapping_certainty`; the
   Agent-2 prompt contract explicitly instructs the model to raise a question below the threshold, even
   though no Python-side deterministic gate enforces it (§5, §14).
7. Added a third episode termination state, `INCOMPLETE_TECHNICAL`, distinct from `CONVERGED` and
   `TERMINATED_MAX_ROUNDS`, excluded from all Detector-v1 denominators (§4, §9).
8. Corrected §12's allowed-claim wording, which referred to "frozen run output"; the frozen 12/30 corpus
   cannot supply confidence, evidence, or round data. The claim applies to a future instrumented
   one-setting run only.
9. Reconciled §5/§15 against the live schema Codex committed after v1.0.0
   (`schemas/qa-communication-event-v1.schema.json`): field names below are updated to match it exactly
   (`episode_id`, `round_index`, `termination_reason`, `converged`, `answer_confidence`,
   `answer_evidence_ref`, `follow_up_to_event_id`, `source_agent`/`source_stage`/`source_skill`,
   `target_agent`, `provenance`) in place of the descriptive names v1.0.0 used before the schema existed.

No real-run output or detector result was inspected before or during this revision. No threshold below
was chosen from a new-data distribution.

## 1. Status and freeze date

**Preregistration. Originally frozen 2026-09-04; corrected pre-data as v1.0.1, same date.** This document
fixes the scientific policy — unit of analysis, admissible signals, detector logic, setting-selection
rule, feasibility criteria, and descriptive analysis plan — before the one-setting instrumented run that
Codex is preparing. No such run has occurred: the interaction-log recovery audit concluded
`NOT FOUND — LOCAL SEARCH EXHAUSTED`, and the instrumentation-verification receipt confirms no live model
call has been made and every setting is currently blocked on missing case-model inputs.

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
- **Ends** in exactly one of **three** terminal states, carried in the live schema's `termination_reason`
  field alongside a boolean `converged`:
  - **`CONVERGED`** (`converged = true`) — a round produces no further questions and the loop's `break`
    fires.
  - **`TERMINATED_MAX_ROUNDS`** (`converged = false`) — round `MAX_QA_ROUNDS` completes without
    convergence, the code's own boundary, marked at four call sites by
    `logger.warning("...reached MAX_QA_ROUNDS...")` (`:169`, `:240`, `:270`, `:384`, `:429`).
  - **`INCOMPLETE_TECHNICAL`** (`converged = null`) — the episode began but did not reach either scientific
    terminal state because of a runtime exception, a parse failure, a missing required answer event,
    an instrumentation failure, or a corrupted event lifecycle. This state is **not** a form of
    non-convergence and **not** a form of "no alert"; it records that the episode cannot be trusted as an
    observation at all. Episodes in this state are excluded from every Detector-v1 denominator (§6, §9) and
    reported only as a separate technical-missingness count.

**This unit is now schema-defined but not yet run-observed.** After v1.0.0 was committed, Codex added
`schemas/qa-communication-event-v1.schema.json` and `VEGO-AI/framework/qa_communication.py`, an append-only
observer that emits `QUESTION_EMITTED`, `ANSWER_RECEIVED`, `EPISODE_CONTINUED`, and `EPISODE_TERMINATED`
events carrying `episode_id`, `round_index`, `termination_reason`, `converged`, and full source/target
tagging. This closes most of the instrumentation gap v1.0.0 identified, but the schema is a contract, not
an observation: no live model call has been made (verified in
`2026-09-04-qa-instrumentation-verification.md`), and wiring the observer into the protected orchestrator
runtime is an explicitly separate, still-pending step. `qa_registry.py`, `orchestrator.py`, and `state.py`
remain unmodified and protected. Remaining requirements on this instrumentation are listed as a Codex
dependency in §15, including the requirement that `termination_reason` take exactly the three values
above rather than free text chosen at implementation time.

Communication is the primary object of the unit (Iris); every reported measure is additionally stratified
by source agent, source stage/skill, and target agent (Arnon) — see §14.

## 5. Candidate signal adjudication table

Every admission decision is grounded in quoted code or prompt text; no threshold is chosen by inspecting a
distribution. Field names below match the live schema's exact names where Codex has defined them.

| # | Signal | Verdict | Grounding |
| --- | --- | --- | --- |
| S1 | Low Q&A answer confidence | **ADMIT PRIMARY** (after corpus) | `answer_confidence` is a mandatory, closed field in both the prompt contract (`High \| Medium \| Low`, `agent1_language_advisor.py:224`, mirrored `agent2_domain_advisor.py:487`) and the live schema (`enum: ["High","Medium","Low","UNKNOWN",null]`). `Low` is defined by the prompt itself as "relies on trained knowledge; no direct artefact support" (agent1) / "relies on general knowledge; no direct artefact support" (agent2) — an architecture-defined, not inspected, threshold. |
| S2 | Medium Q&A answer confidence | **ADMIT PRIMARY** (after corpus) | Same field; `Medium` is defined as "inferred from context within the artefacts." |
| S3 | Missing answer evidence | **ADMIT PRIMARY** (after corpus) | Rule fixed in v1.0.1 (see rationale below): `answer_evidence_ref` is null, or its `length` is `0`. Deterministic; requires no citation grammar. |
| S4 | Answer based on an explicit lower-priority / trained-knowledge source | **ADMIT SECONDARY / EXPLORATORY** | Grounded only for the language channel: the prompt defines a four-tier `SOURCE PRIORITY`, tier 4 "trained knowledge (flag explicitly when used)" (`agent1_language_advisor.py`, source-priority block). The live schema carries `answer_source_tier` as a free string, not a closed enum, so this remains a text-detection signal over that field's literal value, fragile against paraphrase, and analytically close to S1 (the prompt's own definition of `Low` already names "trained knowledge" as its reason). Reported separately from S1 so the overlap can be measured, not assumed. |
| S5 | Repeated clarification | **ADMIT SECONDARY / EXPLORATORY, conditional** | Not admitted on any semantic-similarity basis. Admissible **only** under an exact, frozen definition: within one `episode_id`, a question in round `k′ > k` is a "repeat" of round `k` if their texts are identical after a fixed normalization (case-folded, whitespace-collapsed, punctuation-stripped). The live schema stores `question_text_ref` as a content hash (`sha256` + `length`), not raw text, so this comparison must be computed by the instrumentation at write time, over the pre-hash text, using exactly this normalization — a Codex dependency (§15). If that normalized-equality field is not persisted, S5 remains unusable and is reported as such, not silently dropped from the document. |
| S6 | Multiple Q&A rounds before resolution | **ADMIT PRIMARY** (after corpus) | Directly grounded in the orchestrator's own round loop and `MAX_QA_ROUNDS` constant (§4), and now schema-carried as `round_index` per event. |
| S7 | Non-convergence / reaching `MAX_QA_ROUNDS` | **ADMIT PRIMARY** (after corpus) | Directly grounded in the same code; the four `logger.warning` sites are the system's own definition of non-convergence, now schema-carried as `termination_reason = "TERMINATED_MAX_ROUNDS"`. This is the closest observable proxy to an unresolved episode, and is preferred over "unanswered question," which was rejected as a v1 signal in the prior study freeze because it was true of 100% of the frozen (harness-broken) corpus by construction; the corrected terminology for that frozen condition is `ANSWER_NOT_PERSISTED` (`2026-09-04-qa-baseline-freeze.md`), which is explicitly not a behavioural signal. Under the orchestrator, an unresolved episode is only meaningful as `TERMINATED_MAX_ROUNDS`, so S7 supersedes rather than repeats the earlier rejected signal. |
| S8 | Follow-up question after an answer | **ADMIT SECONDARY / EXPLORATORY, conditional** | The live schema already carries `follow_up_to_event_id` (a hash-formatted pointer to the prior event). Distinct from S5: a follow-up is a *new*, non-repeated question raised in response to an answer, addressed to the same target within the same episode, whereas S5 is the *same* question recurring. Admissible as a secondary/exploratory measure once `follow_up_to_event_id` is populated by a real run; **not** admitted to Detector v1's primary rule set (§6) without independent justification, because its scientific meaning (does the system generate a materially new concern, or merely re-ask) has not itself been validated. |
| S9 | Unusually high question density within one decision episode | **REJECT as a detector trigger; retained as a plain descriptive measure** | No text anywhere defines what "unusually high" means, and choosing a cut after seeing data would violate this preregistration's own purpose. Raw questions-per-episode is reported in §11 with no threshold attached. |
| C1 | Agent-2 `mapping_certainty` | **ADMIT — contextual comparator, not a Q&A signal** | Threshold is **`< 0.7`**, quoted verbatim from the architecture contract: "For every guideline whose mapping_certainty is below 0.7, you MUST raise a Q_lang question asking Agent 1 to confirm or correct the template assignment" (`agent2_domain_advisor.py`, guideline-creation and update-iteration instructions, both occurrences). This is the system's own internal escalation trigger from Agent 2 to Agent 1, not an inspected convenience cut. **Correction retained from v1.0.0:** `2026-09-03-qa-escalation-observability.md`'s feature F11 used `≤ 0.75`; no text grounds `0.75`. The frozen threshold for any future computation of C1 is `< 0.7`. As of this revision the discrepancy is unresolved in that document and remains a named Codex dependency (§15). |
| C2 | Agent-4 classification confidence | **ADMIT — contextual comparator only** | Already established in the prior evidence freeze: `requires_human_review` is false on all 27 frozen patterns, and Agent-4 has no independent reference (`analysis/agentD_*` is md5-identical to `eval_output`). Usable only as a contextual descriptor, never as Q&A evidence, and never compared against itself as ground truth. |
| C3 | Explicit `requires_human_review` / guideline-update flags | **ADMIT — contextual comparator only** | `flag_for_guidelines_update` is already established as perfectly co-extensive with `classification == "Substantial Variability"` (9 of 27) and therefore carries no information beyond that class label; reported as context, not as an independent signal. |

**S3 rationale (v1.0.1).** v1.0.0's rule — "empty, or does not contain a parseable artefact citation" —
required a citation grammar that neither the prompt contract nor the live schema defines; Codex would have
had to invent one at implementation time, which this preregistration exists to prevent. The prompt contract
requires a free-text, verbatim-citation `evidence` string with no formal grammar, and the live schema does
not store that text at all — only `answer_evidence_ref = {sha256, length}` or `null`. The only condition
computable without inventing a parser is structural absence: `answer_evidence_ref is null` or
`answer_evidence_ref.length == 0`. This is Option A from the correction brief, adapted to the schema that
now exists; no citation grammar is defined, so Option B is not exercised.

**Not admitted at any tier:** `agent2_domain_advisor.py`'s `scope_errors` field (a language/domain
mis-routing record) exists structurally and is supported in code, but is outside the nine signals and
three contextual comparators specified for this preregistration. It is noted here for completeness and is
not part of Detector v1; adding it later requires the change-control procedure in §16.

## 6. Detector-v1 frozen policy

**Structure: a two-tier precedence structure — strong signals dominate, weak signals apply only when no
strong signal fired. No weights, no scores, no fitted parameters, no ML, no empirical tuning, no labels.**

v1.0.0 collapsed every primary signal into a single OR, which gave `S2` (Medium confidence) and `S6`
(more than one round) the identical operational consequence as `S1` (Low confidence) and `S7`
(non-convergence) — contradicting §7's own claim that these are not equally strong indicators. v1.0.1
corrects this without introducing a weight or a score:

| Tier | Condition | Reason codes |
| --- | --- | --- |
| **STRONG_ALERT** | `S1_LOW_CONFIDENCE` **OR** `S3_MISSING_EVIDENCE` **OR** `S7_NON_CONVERGENCE` | `answer_confidence == "Low"`; `answer_evidence_ref` null or zero-length; `termination_reason == "TERMINATED_MAX_ROUNDS"` |
| **WEAK_ALERT** | no strong rule fired **AND** ( `S2_MEDIUM_CONFIDENCE` **OR** `S6_MULTI_ROUND` ) | `answer_confidence == "Medium"`; episode `round_index` (maximum observed for the episode) `> 1` |
| **NO_ALERT** | neither tier fired | `answer_confidence == "High"`, evidence present and non-empty, exactly one round, `termination_reason == "CONVERGED"` |

`CANDIDATE_ALERT = STRONG_ALERT OR WEAK_ALERT`. Every alert carries **every** reason code that fired
within its tier, not only the first. Episodes whose `termination_reason == "INCOMPLETE_TECHNICAL"` are
excluded from this table entirely (§4, §9) — they are neither `NO_ALERT` nor any alert tier; they are
reported separately as technical missingness.

S4, S5, S8, and S9 remain outside Detector v1 by §5 and may only enter a later, explicitly versioned
revision (§16). C1/C2/C3 are reported alongside every episode as context and never contribute to either
tier.

## 7. Strong vs. weak signals

Evaluated on the evidence available, not asserted by convention, and now consistent with §6's operational
structure.

**Strong: S1 (Low confidence), S3 (missing evidence), S7 (non-convergence).** All three are the system's
own explicit statement that it could not ground an answer in artefact evidence (S1, S3) or could not
resolve a question within its own designed bound (S7). None depends on interpretation. S1 and S3 are
frequently the same underlying event — a Low-confidence answer typically also lacks a citable artefact —
and this overlap is reported descriptively in §11 rather than resolved by treating one as subordinate to
the other.

**Weak: S2 (Medium confidence), S6 (multiple rounds).** Medium confidence is explicitly defined as
"inferred from context" — the system did find support, only indirectly — a materially different claim
from Low. More than one round records only that a clarification occurred, not that the outcome is
suspect; a converged two-round episode may be a routine refinement.

**Exploratory, not tiered: S4, S5, S8.** None enters Detector v1 (§6); each requires either fragile
text-detection (S4) or instrumentation not yet confirmed present in a real run (S5, S8).

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

**Current status (updated from v1.0.0): all four settings are BLOCKED.**
`2026-09-04-qa-instrumentation-verification.md` reports that while each setting's domain description is
present locally, the historical case-model directory for all four settings is absent from this checkout.
No setting currently satisfies rule 1, so no setting is presently executable. This supersedes v1.0.0's
narrower observation (that only the Cheers `domain_base_*.txt` ground-truth files were absent) with a more
complete technical finding: the domain-base asymmetry from v1.0.0 remains true and relevant to Agent-B
coverage evaluation, but is not the operative blocker for Q&A generation — the missing case-model
directories are.

**`cd_pw` remains the provisional first choice once inputs are supplied**, because it is the highest count
among settings whose completeness is unresolved rather than negatively resolved: no setting is
currently known-complete, and none is known-incomplete for a reason other than the shared case-model gap.
When case-model inputs become available for one or more settings, rule 2 applies exactly as stated; the
rule itself required no revision, only the completeness fact it depends on.

This is a **purposive high-information feasibility selection, not representative sampling.** `cd_pw`'s
count of 6 is the largest available signal that Q&A behaviour occurs at all in this system; it is chosen
to maximise the chance of observing a non-degenerate corpus for feasibility purposes, not to estimate a
rate that would generalise to the other three settings.

The final completeness verification against whatever input set the instrumented run script actually reads
is a Codex technical dependency (§15), to be re-executed immediately before the run and reported, not
assumed from this document.

## 9. Feasibility success / failure criteria

Corrected in v1.0.1: v1.0.0 introduced an arbitrary `N ≥ 5` "scientifically usable" threshold, justified
only by its position below the historical ceiling of 6 — not a scientific argument, and conflating
historical *question emissions* with future *complete episodes*. That threshold is removed. Exact N and
its denominator are always reported; no minimum count converts a result from unusable to usable.

- **TECHNICAL SUCCESS** — at least one genuinely complete, routed Q&A episode is observed: every field
  required by §4/§6 is populated (`episode_id`, `round_index`, `answer_confidence`, `answer_evidence_ref`,
  a terminal `termination_reason` of `CONVERGED` or `TERMINATED_MAX_ROUNDS`), and no harness or
  instrumentation failure prevented trustworthy observation of it.
- **DESCRIPTIVELY USABLE** — **every** technically complete episode (§4's `CONVERGED` or
  `TERMINATED_MAX_ROUNDS` states only) is admissible for the descriptive analysis in §11, at whatever
  exact N is observed. If the corpus is sparse, it is reported and characterised as sparse, and the claim
  in §12 is scoped accordingly; no inferential or generalising claim is licensed at any N from one setting,
  regardless of size.
- **PARTIAL TECHNICAL SUCCESS** — the runtime executes, but one or more otherwise-terminal episodes are
  missing a required field (§4/§6) needed to place them in Detector v1. Such episodes are reported as
  partial, separately from both the descriptively-usable set and the `INCOMPLETE_TECHNICAL` count, with
  the specific missing field named.
- **VALID ZERO-Q&A RUN** — the system executes correctly for the selected setting and emits zero Q&A
  episodes. This is a legitimate scientific null/feasibility result, not an instrumentation failure, and is
  reported as such; see §10 for what may follow it.
- **FAILURE** — a harness, instrumentation, or runtime failure prevents trustworthy observation, such that
  even a zero-episode or low-episode outcome cannot be attributed to the system's actual behaviour.
  `INCOMPLETE_TECHNICAL` episodes (§4) are the per-episode form of this; a run-level FAILURE is the case
  where the failure is general rather than confined to specific episodes.

## 10. Expansion rule

Corrected in v1.0.1: v1.0.0 required "non-degenerate signal variance" before expanding, which made the
decision to collect more data depend on the observed detector result — precisely the kind of data-dependent
stopping rule a preregistration exists to prevent. Expansion now depends only on predeclared
technical/structural facts.

**A. If instrumentation fails (run-level FAILURE, §9):** REVISE INSTRUMENTATION. Do not analyse invalid
output, and do not select a further setting until the failure is diagnosed and fixed.

**B. If the selected setting reaches TECHNICAL SUCCESS with one or more DESCRIPTIVELY USABLE episodes:**
complete the one-setting feasibility analysis (§11) on exactly the episodes observed, regardless of
whether the observed signals are frequent, rare, constant, or entirely absent among those episodes. This
is the default path and requires no further setting.

**C. If the selected setting reaches a VALID ZERO-Q&A RUN (§9):** this is itself a reportable feasibility
result. A single predefined fallback setting **may** be run only if the study's objective still requires
observing at least one complete episode to demonstrate instrumentation feasibility. The fallback is
selected by the already-frozen ranking in §8 among settings verified complete at that time — never by
which setting is expected to produce a particular detector outcome. Given the frozen historical counts, the
fallback after `cd_pw` is `cd_ch` (3), then `ucd_ch` (2), then `ucd_pw` (1), in that order, skipping any
setting not verified complete.

**D. Never expand because an observed rate is undesirable.** A low alert rate, a confidence distribution
dominated by `High`, or few multi-round episodes are all legitimate scientific outcomes of TECHNICAL
SUCCESS and are not, by themselves, grounds to collect more data.

**E. Expansion for communication-route coverage** (for example, to observe a Domain-Advisor-directed
question, which has zero historical occurrences in any of the four frozen settings) requires an explicit,
predeclared structural objective stated before the additional run — never a post-hoc justification invoked
because the first setting's signal values were unsatisfying.

## 11. Descriptive analysis plan

No human labels exist at this stage; nothing below may be interpreted as a rate of correctness. Every
figure is reported with its exact N and denominator; sparse corpora are characterised as sparse rather than
padded to a nominal minimum.

**Primary measures:** number of complete episodes (`CONVERGED` + `TERMINATED_MAX_ROUNDS`), separately from
the `INCOMPLETE_TECHNICAL` and partial-technical-success counts (§9); questions per episode; rounds per
episode; confidence distribution (`High`/`Medium`/`Low`/`UNKNOWN`); evidence-presence rate; convergence
rate; candidate `ALERT` count and rate, reported by tier (`STRONG_ALERT`/`WEAK_ALERT`/`NO_ALERT`); alerts by
reason code; alerts by source agent/stage and target agent (§14).

**Secondary measures:** co-occurrence of reason codes within one alert (in particular, how often
`S1_LOW_CONFIDENCE` and `S3_MISSING_EVIDENCE` fire together, per §7); raw questions-per-episode with no
threshold attached (S9, §5); C1/C2/C3 contextual distributions reported alongside, never combined into the
alert decision.

None of the above may be called accuracy, precision, recall, effectiveness, or benefit.

## 12. Allowed claims

That certain observable, code-grounded communication features of a VEGO-AI Q&A episode — confidence,
evidence presence, round count, and convergence state — can be computed deterministically **from the new
instrumented one-setting run's output** and used to raise a transparent, auditable, tiered candidate alert.
*(Corrected in v1.0.1: v1.0.0 referred to "frozen run output," which is incorrect — the frozen 12/30 corpus
has no persisted answers, confidence, evidence, or round data and remains historical baseline/context
only, per `2026-09-04-qa-baseline-freeze.md`.)* That the resulting alert counts and distributions describe
this one purposively selected setting and do not generalise to the others without further data.

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
under study, with no independent check on calibration.

**Corrected in v1.0.1:** v1.0.0 stated that "no part of the system currently acts on" `mapping_certainty`.
This overstated the case and is withdrawn. The precise statement is: no Python-side deterministic gate is
currently established as enforcing `mapping_certainty < 0.7` — the value is not read by any code path
inspected in this or the prior evidence freeze. However, Agent-2's own prompt contract explicitly
instructs the model to act on the threshold: "For every guideline whose mapping_certainty is below 0.7,
you MUST raise a Q_lang question." `mapping_certainty` is therefore an upstream model-instruction
trigger/context that the model itself is told to condition its behaviour on, not an independent
ground-truth label and not a deterministically enforced gate.

The unit of analysis (§4) is now schema-defined but still depends on instrumentation not yet wired into a
live run (§4, §15); if a real run's instrumentation captures round/episode state differently than
specified here, this document's definitions — not the instrumentation's — must be revisited under change
control (§16), and the discrepancy reported rather than silently absorbed. The domain-question channel has
zero historical occurrences across all four settings; a null result there is not evidence the channel is
broken, only that it has never yet fired.

### 14a. Communication-route reporting

Every reported measure in §11 is broken down, at minimum, by: source agent (Agent 2, Agent 3, or Agent 4);
source stage/skill (phase 2 guideline build/update, skill 3-2, skill 3-3, skill 4-2, guidelines feedback
loop); target agent (Agent 1 or Agent 2); and scope (`lang` or `dom`) — matching the live schema's
`source_agent`/`source_stage`/`source_skill`/`target_agent`/`scope` fields exactly. A route that is
supported in code but has zero historical observations (Agent 3 → either advisor; Agent 4 → either
advisor; Agent 2 → Agent 2 domain questions) is reported as a route with zero observed episodes, never as
an empirically confirmed absence of behaviour.

## 15. Dependencies on Codex instrumentation

Reconciled against `schemas/qa-communication-event-v1.schema.json` and `VEGO-AI/framework/qa_communication.py`,
committed after v1.0.0. This closes most of the gap v1.0.0 identified; what remains open is listed below,
split by whether it blocks a Detector-v1 GO decision or is needed only for the exploratory signals in §5.

**Required for Detector v1 (blocking):**
1. `termination_reason` must take **exactly** one of three values — `CONVERGED`, `TERMINATED_MAX_ROUNDS`,
   `INCOMPLETE_TECHNICAL` — with `converged` set `true` only for the first. The schema's field is free
   text; the three-value contract is a scientific requirement this document adds, not yet confirmed as
   enforced by `qa_communication.py`'s callers.
2. The observer must be wired into a live run path (confirmed as an explicitly separate, still-pending
   step in `2026-09-04-qa-instrumentation-verification.md`, since `qa_registry.py`, `orchestrator.py`, and
   `state.py` remain unmodified and protected).
3. `episode_id`, `round_index`, `answer_confidence`, `answer_evidence_ref`, `source_agent`,
   `source_stage`, `source_skill`, `target_agent`, and `provenance` populated on every event by a real run
   — schema-defined, not yet run-observed.
4. Reconciliation of the C1 threshold: correct `2026-09-03-qa-escalation-observability.md`'s F11
   (`≤ 0.75`) to `< 0.7` per §5, or supply an independent justification for `0.75` this document has not
   seen, before any new-corpus C1 value is reported.
5. A pre-run completeness check against whatever input set the instrumented run script actually reads,
   re-executed immediately before execution and reported (§8) — the current `BLOCKED` status on all four
   settings is the latest such check and must be re-verified once case-model inputs are supplied.

**Required only for exploratory signals (non-blocking for GO):**
6. `follow_up_to_event_id` populated by a real run, for S8.
7. A frozen, exact-normalization repeat-detection computation (case-folded, whitespace-collapsed,
   punctuation-stripped equality within one `episode_id`) computed at write time over pre-hash question
   text, for S5. Without it, S5 is reported as unusable, not silently omitted.

## 16. Change-control rule

Once this preregistration reaches a version with confirmed zero data exposure, Detector-v1's rules (§6)
may not be changed after the first real run's output has been inspected, **except** where a field specified
in §15 is technically unavailable, the instrumentation is confirmed wrong, or a rule is impossible to
compute exactly as written. Any such change must be versioned (`v1.1`, dated), state exactly what changed
and why, and be reported explicitly as a **post-data change** — never silently substituted for v1. Adding
S4, S5, S8, or S9 as primary signals, adopting a different detector structure, or changing any threshold in
§5/§6 all require this procedure. This document is not amended in place for such changes; a dated addendum
or successor section records them. **v1.0.1 (this revision) is exempt from this procedure**, because no
data exposure occurred before or during it (§0); it is the last change permitted without invoking §16.
