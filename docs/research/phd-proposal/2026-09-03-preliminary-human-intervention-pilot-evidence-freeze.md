# Preliminary Human-Intervention Pilot — Evidence Freeze

**INTERNAL EVIDENCE FREEZE — NOT A NEW SUPERVISOR DELIVERABLE.**
Scientific/methodological lead record. Codex holds the technical/reproducibility lane.
Date 2026-09-03. Base revision `3b8ce46`. Evidence source: the supervisor-supplied package
(`System/eval_output`, `System/analysis`), which is byte-identical to `VEGO-AI/eval_output` in this repo.

This document does **not** replace
[`2026-09-03-preliminary-human-intervention-experiment.en.md`](2026-09-03-preliminary-human-intervention-experiment.en.md),
which may already have been sent. It records which statements in that page must be corrected before any
result is reported. No intervention was executed. No agent, LLM, schema or `eval_output` file was touched.

## 1. Evidence state

| Item | Value | Source |
| --- | --- | --- |
| Distinct Agent-C case artifacts | 165 (45+46+37+37) | `eval_output/*/agentC_case_*.json` |
| Ranking rows | 179 (46+48+44+41) | `agentC_all_scores.json` |
| Duplicate-ID ranking rows | 14 | joined on `case_id` |
| Expert-reviewed compliance judgments | 915 | four `scores_*.xlsx` / `compliance_vectors` |
| Expert-rejected (`Score`=0) | 120 | ditto |
| Trigger `status != Satisfied` | 257/915 = 28.1%, captures 108/120 = 90% | ditto |
| Agent-B coverage gap | **59 of 80** (not 59 of 78) | `agentB_metrics.json` `false_negatives` / `TP+FN` |
| Cases where `total_score` = sum of contributions | 27 of 165 | recomputed read-only |
| Variability patterns | 27 shipped / 26 in the paper | `agentD_variability_classes*.json` vs Table 4 |
| EXP-005 generalization-safe labels | **0 of 24** | `exp005_label_review_full.csv` |

`Score` in `compliance_vectors` is an **expert agreement flag on the agent's verdict**, not a compliance
score (rows with `Not-Satisfied` carry `Score`=1). The `Comment` column carries the corrected label.

**New contradictions recorded, not resolved.** (a) The camera-ready states 16 Model Inspector outcomes
were reviewed, 4 per setting; the artifact carries expert scores on 32 (setting, case) pairs — 8/8/7/9 —
over 18 distinct case ids. (b) Each case file records the compliance label **twice**, in
`existing_mapping[]` and in `compliance_contributions[]`, and these disagree in **78 of 4,852 entries
across 36 cases**. Any replay must state which array it treats as the decision of record.

## 2. Corrected count interpretation

**PARTIALLY RECONCILED.** 179 ranking rows → 165 distinct case identifiers → 14 duplicate-ID rows is
verified. Why the published paper prints **178** rather than 179 is **not** established. The gap is
localised to `ch-cd` alone (Table 1 says 47; the ranking array has 48); the other three settings match
exactly. **No explanation is offered.**

Required wording: *"The published paper reports 178 case models; the supplied ranking artifacts contain
179 scoring rows over 165 distinct case identifiers."*

**Duplicate causes are mixed — the earlier "all AppleDouble" claim is withdrawn.** Of the 14:
AppleDouble `._` stub 8 · `_1` copy 3 · draft/final variant 1 · alternate submission 1 · other 1.
The loader is an unfiltered `sorted(folder.glob("*.txt"))`, so eight binary resource forks were read as
text and scored: in `cd_pw` a 506-byte fork of case 70229 scored **130.6%** and ranks first in that
setting. Only the second load persists into the case artifacts. Two md5-identical files (case 70248)
scored 91.7% and 58.3% — a directly measured non-determinism datum.

**Patterns: 27 shipped vs 26 published.** Localised to one cell: `pw-ucd` substantial 5 vs 4; the other
three settings and all occasional counts match. Cause **UNRESOLVED**.

## 3. Reference-quality boundary

The recorded expert review is **RECORDED EXPERT / DEVELOPMENT REFERENCE**. It is **not** independent
held-out ground truth. The camera-ready states the assessors were *"two of the co-authors acting as
domain experts, who also served as evaluators in the earlier phases"*. There is one `Score` column, no
reviewer id and no second rating, so **no inter-rater agreement is computable** from this package.

Agent-4 has **no** reference at all: `System/analysis/agentD_*.json` is md5-identical to
`eval_output/*/agentD_*.json`, so any "expert vs agent" comparison there is self-comparison.

## 4. Primary executable pilot cases

**One intervention type — correction of a recorded compliance verdict — over two cases.** Both are in the
27 clean cases, both are fully expert-reviewed at row level, and both carry **zero** `existing_mapping`
vs `compliance_contributions` label disagreements, so neither depends on Codex's re-aggregation.

**P-A · `cd_ch` / case 68064** — upward corrections. `agentC_case_68064.json`, baseline `total_score`
22.0 = recomputed 22.0, `max_score` 26.0.

| Row | Guideline | Baseline | Expert `Comment` | Contribution | Delta |
| --- | --- | --- | --- | --- | --- |
| `scores_cd_ch.xlsx` r58 | G5 Order Composition | Partially-Satisfied | `Satisfied` | 0.5 → 1.0 | +0.50 |
| r60 | G7 Employee Ordering Conditions | Partially-Satisfied | `Satisfied` | 0.5 → 1.0 | +0.50 |
| r78 | G25 Inventory Update Process | Not-Satisfied | `Partially-Satisfied` | 0.0 → 0.5 | +0.50 |

Total delta **+1.50** → 23.5/26.0 (84.6% → 90.4%).

**P-B · `ucd_pw` / case 70219** — **opposite direction**, the agent was more generous than the expert.
`agentC_case_70219.json`, baseline 48.0 = recomputed 48.0, `max_score` 48.0, all 48 guidelines
`Satisfied`.

Six rows in `scores_ucd_pw.xlsx` — r389 G4, r391 G6, r399 G14, r411 G26, r424 G39, r425 G40 — all
baseline `Satisfied`, all expert `Comment` = `Partially`, each 1.0 → 0.5. Total delta **−3.00** →
45.0/48.0 (100.0% → 93.8%).

P-B is included deliberately: it is the only clean fully-reviewed case that moves the score **down**.
Corroborating contradiction, recorded not smoothed: `all_scores_published.xlsx` r98 gives this same case
agent 100% against a human grade of 18.5/25 = 74%.

## 5. Secondary / exploratory cases

| Case | Verdict | Reason |
| --- | --- | --- |
| **P-C** `cd_ch`/68113 — Not-Satisfied→Satisfied | **SECONDARY, blocked** | Supplies the missing upward-from-Not-Satisfied direction (+2.00) but is one of the 138: printed 24.5 vs recomputed 24.0. Two routes give 26.0 (=max) or 26.5 (>max). **Waits on Codex.** |
| **C1 missing guideline** (page's P2) | **REMOVED from the paired pilot** | Option A falsified: all 17 human-inserted rows hold the literal string `null` in every Run-ID, name, description and citation cell, supplying **0 of the 6** fields the Model Inspector consumes. Even with an object, the verdict is an LLM call — `agentC_case_scorer.py` marks `score_case_model` `[LLM call]`. |
| **C1-B guideline deletion** | **CANDIDATE, needs a design pass** | 21 rows are `Status='WRONG'`; 13 have a real Run-1 ID and exist in the best run. Primary candidate `ucd_ch` G20. First-order arithmetic is deterministic; **second-order effects are not** — whether removal changes remaining verdicts needs an LLM. Carry as a stated assumption or drop. |
| **C3 uncovered fragment** (page's P1) | **EXPLORATORY ONLY** | 27 rejections partition 3 / 12 / 10 / 2. Only 3 name a different schema label, and even those are not rescorable: a Mistake label requires a severity the expert never supplied, and the baseline severity is `N/A`. The universal claim "C3 is always outside the schema" is **withdrawn** — 88.9% is accurate. |
| **C4 variability** | **REJECT** | Self-comparison (md5-identical). `requires_human_review` false on all 27. Absent from `Tasks.docx`. |
| The 114-row set as a block | **EXPLORATORY ONLY** | Six of the 114 sit in cases with the dual-label disagreement; a set-level claim needs per-row screening. Individually screened cases remain admissible. |

**Dependency on external evidence (raised by Codex, `74d389f`).** P-A and P-B are identified from
`System/analysis/scores_*.xlsx`, which is **not tracked in this repository** — only aggregate EXP-046
evidence is. Codex's technical boundary lists "exact public C2 row selection" as blocked for that reason
and puts "whether controlled external EXP-046 row-level evidence may be used" under supervisor approval.
**These two cases therefore cannot be executed until that approval is given.** The selection above is
recorded so the decision can be taken on concrete rows rather than in the abstract. Both agree with Codex
on 179/165/14/27, on the Agent-4 byte-identity, on EXP-005 0/24, and on C1 being blocked without an LLM.

## 6. Frozen Condition A

The recorded run exactly as shipped: `agentC_case_<id>.json` with its `existing_mapping[]`,
`compliance_contributions[]` and `total_score`. Nothing is re-executed. For P-A and P-B the printed and
recomputed totals agree, so no aggregation choice is required.

## 7. Controlled Condition B

**FROZEN-OUTPUT CONTROLLED COUNTERFACTUAL REPLAY.** One bounded expert-derived correction is substituted
at one identified decision point; only the deterministic downstream score aggregation is recomputed by
applying the published schema constant. **No agent runs. No LLM call. No file in `eval_output` is
modified** — the replay reads frozen inputs and writes only to a separate result record.

This demonstrates intervention-point feasibility, input-representation feasibility and downstream-effect
feasibility. It does **not** demonstrate real-time interaction, agent adaptation, joint human–AI
performance, accuracy improvement or user benefit. The term *"Human-Assisted VEGO-AI"* used in §7 of the
delivered one-pager **overstates** what happens and must be corrected.

## 8. Trigger rule

`compliance_status != "Satisfied"`, computable from the frozen artifact with no LLM. On the recorded
review it selects 257/915 = 28.1% of judgments and covers 108/120 = 90% of the expert's rejections.
These are **descriptive development statistics**, not accuracy evidence.

P-B is reached by this trigger only in the reverse sense — its six corrections sit on `Satisfied`
verdicts, which the rule does **not** flag. That is a finding about the trigger's blind spot and must be
reported as such, not hidden.

## 9. Predefined success criterion

Fixed before execution, per case:

- **Applied** — the corrected label is substituted at exactly the named guideline entry and nowhere else.
- **Deterministic** — recomputation uses only published schema constants; re-running yields identical output.
- **Expected delta** — P-A **+1.50** (22.0 → 23.5); P-B **−3.00** (48.0 → 45.0). A different delta is a
  failed replay, not a finding about human value.
- **Bounded** — exactly one field changes per correction; no other array is edited.

Outcome per case: **Improved / No Change / Degraded** against the recorded reference. P-B is expected to
record *Degraded* against the agent's own score, and that is a legitimate result.

## 10. Allowed conclusion

That an automatically computable condition marks decision points where a bounded, already-recorded expert
correction can be substituted into frozen VEGO-AI output and its downstream effect recomputed
deterministically. **Demonstrate feasibility, not prove effectiveness.**

## 11. Forbidden conclusions

No accuracy, effectiveness, benefit, effort-reduction, superiority, generalization or statistical claim.
Not independent validation — the reference is co-author development review. Not a user study. No claim
that the expert was right and the agent wrong: `Score`=0 records disagreement. No Agent-4 quantitative
claim. No claim built on `total_score` for the 138 unreconciled cases. Never the word *prove*.

## 12. Technical dependencies assigned to Codex

1. Score re-aggregation across the 138 cases where `total_score` ≠ sum of contributions (−3.5 to +11.5).
   Note the fragment key is `total_contribution`, not `score`.
2. Decide which array is the decision of record where `existing_mapping` and `compliance_contributions`
   disagree (78 entries, 36 cases).
3. Replay harness and provenance/hash checks.
4. Technical reconstruction of the paper's 178 for `ch-cd`, if reconstructible.
5. Contamination register for the 8 AppleDouble-scored rows and the 14 duplicate ids.

## 13. Open supervisor decisions

1. **Is a two-case, one-intervention-type pilot acceptable**, given three heterogeneous types are not
   defensible? Recommended: yes.
2. **P-B moves the score down.** Confirm it stays in.
3. **C1 deletion variant** — pursue with the stated second-order assumption, or drop C1 entirely?
4. **The delivered one-pager needs three corrections** before results are reported: §7
   "Human-Assisted VEGO-AI" → frozen-output counterfactual replay; §8 P3's reference "Blinded reviewers
   plus adjudication" — these do not exist (0 filled rows, no `_filled.csv`); P1's reference if it means
   Agent-4 classification — that is self-comparison.
5. **Non-independence disclosure** — the proposal does not state that the paper's assessors were
   co-authors. Add it.
6. **Report the package defects to the supervisors?** Resource forks scored as models, case id `20277`
   which does not exist, `Scores` vs `Score` header, spreadsheets missing 225 compliance and 70 fragment
   rows relative to the JSON.
