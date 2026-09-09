# Study 1 hotspot results package — withdrawal record

**Date:** 2026-09-09 · **Status of the hotspot study: `PREREGISTERED_NOT_EXECUTED_OR_UNVERIFIED`.**

A results package for the human-review hotspot baseline was previously committed to this branch.
It is **withdrawn**. This record states exactly what was withdrawn, why, and what would be
required to publish it.

---

## 1. What was withdrawn

| Artefact | Disposition |
|---|---|
| `2026-09-09-study1-hotspot-deck-he.pptx` | removed from the head |
| `figures/study1-hotspot-report-he.html` | removed from the head |
| `figures/study1-hotspot-business-he.html` | removed from the head |
| `figures/study1-hotspot-map-he.html` | removed from the head |
| `figures/study1-hotspot-evidence-index-he.html` | removed from the head |

Git history retains them. Nothing was rewritten and no history was force-pushed.

**Retained:** the preregistration and its frozen manifest. Preregistering a study is a legitimate,
verifiable act, and the manifest continues to declare `PREREGISTERED_NOT_EXECUTED`. The
instruments — rater cards, adjudication, analysis, runtime materialiser, execution grant — are
also retained. They are code, and their correctness does not depend on any run having happened.

## 2. Why

The withdrawn package reported an executed run and closed with a verdict of `CONDITIONAL GO`.
Neither survives scrutiny against what this head can prove.

**No part of the execution evidence is tracked in this head.** A run receipt, an event log and a
per-call ledger exist on one machine. They are internally consistent, and that is not the test. A
private artefact is evidence to its holder and to nobody else; a reader of this pull request has
no way to check any of it. Execution therefore cannot be represented as established, and the
counts it would support are deliberately **not** republished here — publishing them would present
an unverified run as an executed one.

**The verdict was unsupported.** `CONDITIONAL GO` implies a scope within which the baseline is
established. No such scope was verified by an independent reviewer, and the primary outcome the
study is defined against does not exist. The correct current verdict is
**`DESCRIPTIVE_RULE_BEHAVIOUR_ONLY / NOT_READY_FOR_SCIENTIFIC_CONCLUSION`**.

**The sample was not prospective.** The draw seed was fixed *after* the full-frame run outcomes
were already known to the author. The draw is mechanically reproducible from the seed, which is
not the same thing as a pre-commitment record that predates the outcomes. The sample is
`PILOT_INFORMED_POST_OUTCOME` and may never be described as prospective, and no artefact of this
study may carry the label `PROSPECTIVE EMPIRICAL EVIDENCE`.

## 3. Claims withdrawn in particular

| Withdrawn wording | Why it fails |
|---|---|
| "the detector demonstrably prioritizes" | prioritization effectiveness is defined against human judgement that does not exist |
| "workload reduction" | a screening fraction is not measured human work |
| "retention" of review-worthy episodes | requires blinded ratings; none exist |
| "PROSPECTIVE EMPIRICAL EVIDENCE" | the sample is post-outcome informed, and the run is unverifiable from this head |
| "the only blocker is two raters" | false; the evidence chain is not verifiable from the head either |
| `CONDITIONAL GO` | no independent reviewer verified a complete evidence chain or defined a limited scope |

## 4. The screening-fraction rule, stated once and used everywhere

> A reduced number of episodes selected by a rule is not evidence of reduced human workload,
> retained useful cases, correctness, benefit, or safety without blinded human ratings and
> measured review time.

The quantity is named `UNVALIDATED_SCREENING_FRACTION` and carries that sentence in every table,
figure and document that reports it.

## 5. What would be required to publish a hotspot result

All of the following, together. Any one missing keeps the status at
`PREREGISTERED_NOT_EXECUTED_OR_UNVERIFIED`:

1. the run receipt, event log and per-call ledger **present in the exact current PR head**, or
   otherwise verifiable by a reader who has only this repository;
2. a receipt that **self-binds** its own event-log digest, lifecycle summary, execution-code
   digests and `MAX_QA_ROUNDS`, with the bound digests **recomputing** against the artefacts;
3. reserved and completed calls that **reconcile**, so cost may be called exact rather than a
   lower bound;
4. the sample class represented truthfully as `PILOT_INFORMED_POST_OUTCOME`;
5. **independent review** of the complete chain before any verdict stronger than
   `DESCRIPTIVE_RULE_BEHAVIOUR_ONLY` is written down.

Publishing the primary outcome additionally requires complete, paired, blinded human ratings and
measured review time. Neither exists.

## 6. What still stands

The machine-readable record is
[`study1c-reconciliation.json`](study1c-reconciliation.json), which lists every run with its
execution status, and [`study1c-claim-ledger.json`](study1c-claim-ledger.json), which lists what
may and may not be asserted.

The one substantive statement this package supports is unchanged by this withdrawal:

> Under the recorded rule, alert classification is highly sensitive to Q&A episode length; long
> episodes tend to saturate toward `STRONG_ALERT`. This is a rule-behaviour finding, not
> validation of real human-intervention need.
