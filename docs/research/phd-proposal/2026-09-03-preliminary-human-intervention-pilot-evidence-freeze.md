# Preliminary Human-Intervention Pilot — Evidence Freeze

**INTERNAL EVIDENCE FREEZE — NOT A NEW SUPERVISOR DELIVERABLE.**
Scientific/methodological lead record. Codex holds the technical/reproducibility lane.
**Revision 2**, 2026-09-03. Base revision `f12ba2c`. Revision 1 was `f12ba2c`.
Evidence source: the supervisor-supplied package (`System/eval_output`, `System/analysis`), byte-identical
to `VEGO-AI/eval_output` in this repo.

This does **not** replace
[`2026-09-03-preliminary-human-intervention-experiment.en.md`](2026-09-03-preliminary-human-intervention-experiment.en.md),
which may already have been sent. No intervention was executed. No agent, LLM, schema or `eval_output`
artifact was touched.

**Revision 2 fixes three methodological defects in Revision 1**, all raised in supervisor review and all
confirmed here against the rows: the unit of analysis was ambiguous; P-B was presented as a primary
triggered case when the stated trigger does not select it; and the Improved/Degraded outcome was
circular. See §14–§18.

## 1. Evidence state

| Item | Value | Source |
| --- | --- | --- |
| Distinct Agent-C case artifacts | 165 (45+46+37+37) | `eval_output/*/agentC_case_*.json` |
| Ranking rows | 179 (46+48+44+41) | `agentC_all_scores.json` |
| Duplicate-ID ranking rows | 14 | joined on `case_id` |
| Expert-reviewed compliance judgments | 915 | four `scores_*.xlsx` / `compliance_vectors` |
| Recorded expert disagreements (`Score`=0) | 120 | ditto |
| Agent-B coverage gap | **59 of 80** (not 59 of 78) | `agentB_metrics.json` `false_negatives` / `TP+FN` |
| Cases where `total_score` = sum of contributions | 27 of 165 | recomputed read-only |
| Variability patterns | 27 shipped / 26 in the paper | `agentD_variability_classes*.json` vs Table 4 |
| EXP-005 generalization-safe labels | **0 of 24** | `exp005_label_review_full.csv` |

`Score` is an **expert agreement flag on the agent's verdict**, not a compliance score. `Comment` carries
the corrected label. Two contradictions recorded, not resolved: the camera-ready states 16 Model Inspector
outcomes were reviewed (4/setting) against 32 (setting, case) pairs in the artifact (8/8/7/9, 18 case
ids); and the compliance label is stored **twice** per case — `existing_mapping[]` and
`compliance_contributions[]` — disagreeing in **78 of 4,852 entries across 36 cases**.

## 2. Corrected count interpretation

**PARTIALLY RECONCILED.** 179 ranking rows → 165 distinct ids → 14 duplicates is verified. Why the paper
prints **178** is **not** established; the gap is `ch-cd` alone (47 vs 48). No explanation offered.
Required wording: *"The published paper reports 178 case models; the supplied ranking artifacts contain
179 scoring rows over 165 distinct case identifiers."*

Duplicate causes are mixed — the "all AppleDouble" claim is withdrawn: AppleDouble 8, `_1` copy 3,
draft/final 1, alternate 1, other 1. The loader is an unfiltered `sorted(glob("*.txt"))`, so eight binary
resource forks were scored; in `cd_pw` a 506-byte fork ranks first at 130.6%. Two md5-identical files
(case 70248) scored 91.7% and 58.3%. **Patterns 27 vs 26: UNRESOLVED**, localised to `pw-ucd` substantial
5 vs 4.

## 3. Reference-quality boundary

**RECORDED EXPERT / DEVELOPMENT REFERENCE — not independent held-out ground truth.** The camera-ready
states the assessors were *"two of the co-authors acting as domain experts, who also served as evaluators
in the earlier phases"*. One `Score` column, no reviewer id, no second rating → **no inter-rater agreement
computable**. Agent-4 has no reference at all (`analysis/agentD_*` is md5-identical to `eval_output`).

## 14. FINAL PILOT UNIT

**One case-guideline compliance judgment: the triple `(setting, case_id, guideline_id)`.**

Revision 1 called a whole model "one bounded correction" while P-A carried 3 corrections and P-B carried
6. That was wrong. Each experimental unit now contains exactly one baseline verdict, one trigger state,
one recorded expert correction, one baseline contribution and one counterfactual contribution.

A model-level aggregate may be reported **secondarily**, only after multiple independent micro-
interventions are applied to the same case, and only where aggregation is technically clean. It must never
be described as the effect of a single human input.

## 15. FINAL PRIMARY OUTCOME

**Improved / No Change / Degraded is withdrawn as an outcome.** It is circular: the recorded expert
correction is both the input substituted into Condition B and the reference Condition B would be judged
against, so agreement is guaranteed by construction. The pilot cannot establish benefit from this design.

Per unit, report only:

| Field | Values |
| --- | --- |
| Trigger status | Triggered / Not Triggered |
| Replay status | Successful / Failed |
| Baseline verdict | recorded label |
| Controlled correction | recorded expert label |
| Baseline contribution | schema constant |
| Counterfactual contribution | schema constant |
| Contribution delta | signed number |
| Score effect | **UPWARD / DOWNWARD / NO SCORE EFFECT** |
| Model-level aggregate delta | only if aggregation is clean |
| Reference source | recorded development / co-author review |
| Independence | **not independent** |

A positive delta is **not** an improvement and a negative delta is **not** a degradation. Score direction
is not quality direction: case `ucd_pw`/70219 carries an agent score of 100% against a human grade of
18.5/25 = 74%, so a downward move there could be a correction of an over-generous baseline. Nothing in
this design can distinguish the two.

## 16. TRIGGER-POSITIVE PRIMARY SET

Trigger `compliance_status != "Satisfied"`. Eight screens applied: trigger-positive · explicit recorded
correction · existing-schema · no prose mapping · clean frozen baseline · no dual-array disagreement ·
deterministic contribution · no LLM.

**Exactly three units survive across the whole corpus.** All three are in `cd_ch`/68064.

| Unit | Guideline | Baseline | Recorded correction | Row | Contribution | Delta | Effect |
| --- | --- | --- | --- | --- | --- | --- | --- |
| U1 `cd_ch`/68064/G5 | Order Composition | Partially-Satisfied | Satisfied | `scores_cd_ch.xlsx` r58 | 0.5 → 1.0 | +0.50 | UPWARD |
| U2 `cd_ch`/68064/G7 | Employee Ordering Conditions | Partially-Satisfied | Satisfied | r60 | 0.5 → 1.0 | +0.50 | UPWARD |
| U3 `cd_ch`/68064/G25 | Inventory Update Process | Not-Satisfied | Partially-Satisfied | r78 | 0.0 → 0.5 | +0.50 | UPWARD |

**All three are UPWARD. No clean trigger-positive downward unit exists in the corpus.** This is reported
as found; no negative example was manufactured. Secondary model-level aggregate for 68064, if all three
are applied: 22.0 → 23.5 of `max_score` 26.0. The case is clean (printed = recomputed) and carries zero
dual-array disagreements, so the aggregate is technically admissible.

**Near-misses, available as sensitivity checks only:** `ucd_ch`/68074/G17 (r153) and /G19 (r155), both
Partially-Satisfied and trigger-positive in a clean case, excluded because the correction is prose
(*"Can be considerted as satisfied"*, *"Can be considered as satisfied"*) rather than an explicit label.

**Blocked:** `cd_ch`/68113/G4 (Not-Satisfied → Satisfied, +1.00) is the only clean-schema route to that
direction but sits among the 138 unreconciled cases (printed 24.5 vs recomputed 24.0), giving two routes
that differ by 0.5. It waits on Codex.

## 17. TRIGGER BLIND-SPOT SET

**P-B is reclassified. It is not a primary triggered case.** All six of its baseline verdicts are
`Satisfied`, so the trigger `compliance_status != "Satisfied"` would **not** have requested human review
for any of them.

`ucd_pw`/70219, six units — G4 (r389), G6 (r391), G14 (r399), G26 (r411), G39 (r424), G40 (r425) — all
baseline `Satisfied`, all recorded correction `Partially`, each 1.0 → 0.5, each delta −0.50.

Its scientific value is precisely that it is a **false negative of the proposed trigger**: a simple
`status != Satisfied` rule misses recorded expert disagreements, and this case concentrates six of them
in one model. That bears directly on Iris's *when* question and must not be hidden. Its counterfactual
replay, if run at all, is secondary and must be labelled a blind-spot demonstration.

## 18. DEVELOPMENT TRIGGER STATISTICS

Recomputed read-only over the four `compliance_vectors` sheets. These describe a **development-time
co-author review**, not independent ground truth. Labelled accordingly — not "accuracy", not "precision".

| Measure | Value |
| --- | --- |
| Reviewed judgments | 915 |
| Recorded expert disagreements | 120 |
| Flagged by `status != Satisfied` | 257 |
| **Development disagreement coverage** | 108 / 120 = **90.0%** |
| **Flag burden** | 257 / 915 = **28.1%** |
| **Review yield among flagged** | 108 / 257 = **42.0%** |

The 12 disagreements the trigger misses are all `Satisfied`-baseline rows; six of them are the
`ucd_pw`/70219 blind-spot set above.

## 4. Frozen Condition A

The recorded artifact exactly as shipped: `agentC_case_<id>.json` with `existing_mapping[]`,
`compliance_contributions[]` and `total_score`. Nothing re-executed.

## 5. Controlled Condition B

**FROZEN-OUTPUT CONTROLLED COUNTERFACTUAL REPLAY.** For one unit, the recorded expert label is
substituted at exactly that `(case, guideline)` entry and only the dependent scoring contribution — and,
where clean, the model aggregate — is recomputed from published schema constants. **No agent runs, no LLM
call, no write to `eval_output`.**

Demonstrates intervention-point, input-representation and downstream-effect feasibility. Does **not**
demonstrate real-time interaction, agent adaptation, joint human–AI performance, accuracy or benefit.
*"Human-Assisted VEGO-AI"* in §7 of the delivered one-pager overstates this and must be corrected.

**Dependency on external evidence (Codex, `74d389f`).** The units are identified from
`System/analysis/scores_*.xlsx`, which is **not tracked in this repository**. Codex lists "exact public C2
row selection" as blocked and puts use of that workbook under supervisor approval. See §19-B.

## 6. Technical success criterion (PASS / FAIL, per unit)

1. Exact frozen baseline identified. 2. Exactly one verdict substituted. 3. No other decision field
changes. 4. No LLM/API call. 5. Deterministic recomputation. 6. Repeated replay gives an identical result.
7. The expected arithmetic delta is reproduced (U1/U2/U3 each **+0.50**).

Scientific effect is **only** the observed downstream delta and its direction. It is never classified as
beneficial.

## 7. Allowed claim

*"In selected frozen VEGO-AI compliance judgments, an observable review trigger can identify decision
points at which one bounded, previously recorded expert correction can be substituted and its downstream
scoring consequence recomputed deterministically without rerunning the LLM pipeline."*

*"The pilot demonstrates intervention and replay feasibility; it does not establish that the intervention
improves assessment quality."*

Additionally admissible: that the proposed trigger has recorded false negatives (§17), and the measured
workload it creates (§18).

## 8. Forbidden claims

No accuracy, effectiveness, quality, benefit, effort, superiority, generalization or statistical claim ·
not independent validation · not a user study · `Score`=0 records disagreement, not agent error · a
positive delta is not improvement and a negative delta is not degradation · no Agent-4 quantitative claim ·
nothing built on `total_score` for the 138 unreconciled cases · never *prove*.

## 9. Iris's WHEN / WHERE, answered

- **WHEN** — `compliance_status != "Satisfied"`, computable from frozen output; flags 28.1% of judgments,
  covers 90.0% of recorded disagreements, yield 42.0%; with recorded false negatives (§17).
- **WHERE** — the Model Inspector compliance judgment for one `(case, guideline)` pair.
- **WHAT THE HUMAN DOES** — confirms or corrects that one verdict.
- **WHAT THE SYSTEM DOES** — recomputes only the corresponding scoring contribution, and the model
  aggregate where clean.
- **WHAT WE LEARN** — whether that intervention point is technically actionable, and how much review
  workload the trigger creates. Not whether the intervention helps.

## 19. EXECUTION GO / NO-GO CONDITIONS

**GO requires all of:**

1. **G1** Supervisor approval to use the external recorded-expert workbook as the human-input source
   (§19-B below). **Currently NOT granted.**
2. **G2** Codex confirms `cd_ch`/68064 remains clean under its reconstruction (printed = recomputed;
   zero dual-array disagreements). Independently verified here, pending Codex's own receipt.
3. **G3** The replay harness is Codex's, read-only against `eval_output`, writing only to a separate
   result record.
4. **G4** Outcome fields are those in §15. Any artifact using Improved/Degraded is a NO-GO.
5. **G5** U1–U3 are reported as three units, not one intervention.

**NO-GO if any of:** the delta differs from +0.50 on any unit (a failed replay, not a finding) · any LLM
call occurs · any `eval_output` file is modified · the aggregate is claimed for a case among the 138 ·
P-B is presented as trigger-positive.

**Two gates, deliberately separated (§19-A / §19-B):**

- **A — Internal technical/methodological preparation: MAY CONTINUE NOW.** Unit definition, screening,
  trigger statistics, harness design and dry-run planning need no further approval, and **EXP-005 at 0/24
  does not block them.** EXP-005 blocks accuracy and generalization claims, which this pilot does not make.
- **B — Using the external recorded-expert workbook as the human-input source for a supervisor-facing
  preliminary result: REQUIRES EXPLICIT IRIS/ARNON APPROVAL**, per Codex's technical boundary. This is the
  single blocking gate. The analysis is not blocked; only that use of it is.

## 10. Secondary / rejected cases

| Case | Verdict | Reason |
| --- | --- | --- |
| `cd_ch`/68113 | SECONDARY, blocked | Only clean-schema Not-Satisfied→Satisfied route; among the 138 |
| C1 insertion | REMOVED | All 17 rows hold literal `null` in every run-ID/name/description/citation cell — 0 of the 6 fields the Model Inspector consumes; and the verdict is an LLM call |
| C1 deletion variant | CANDIDATE, needs design | 13 viable `WRONG` guidelines; first-order deterministic, second-order not |
| C3 uncovered fragment | EXPLORATORY ONLY | 27 rejections split 3/12/10/2; even the 3 schema-naming rows need a severity the expert never supplied. The universal "outside the schema" claim is withdrawn — 88.9% |
| C4 variability | REJECT | Self-comparison (md5-identical); `requires_human_review` false on all 27; absent from `Tasks.docx` |
| The 114-row set as a block | EXPLORATORY ONLY | Six sit in dual-label-disagreement cases |

## 11. Technical dependencies assigned to Codex

Re-aggregation of the 138 (fragment key is `total_contribution`, not `score`) · deciding the decision-of-
record array for the 78 disagreeing entries · replay harness and provenance receipts · reconstruction of
`ch-cd` 47 if reconstructible · contamination register for the 8 resource-fork rows and 14 duplicates.

## 12. Open supervisor decisions

1. **G1/§19-B** — approve use of the external expert workbook? **This is the blocking gate.**
2. **A one-case, three-unit primary pilot** — acceptable? All three units are upward and all sit in a
   single model; there is no clean alternative.
3. **P-B as a blind-spot demonstration** — include or drop?
4. **C1 deletion variant** — pursue with the stated second-order assumption, or drop C1 entirely?
5. **The delivered one-pager needs corrections** before results are reported: §7 "Human-Assisted VEGO-AI"
   → frozen-output counterfactual replay; §8 P3's reference "Blinded reviewers plus adjudication" — these
   do not exist (0 filled rows, no `_filled.csv`); §8 "Outcome" column → the §15 fields; P1's reference if
   it means Agent-4 classification — that is self-comparison.
6. **Non-independence disclosure** — the proposal does not state the paper's assessors were co-authors.
7. **Report the package defects?** Resource forks scored as models; case id `20277` which does not exist;
   `Scores` vs `Score` header; spreadsheets missing 225 compliance and 70 fragment rows vs the JSON.
