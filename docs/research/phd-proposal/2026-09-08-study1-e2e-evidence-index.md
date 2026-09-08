# Study 1 E2E supervisor readout: evidence index

**Package status:** `SUPERVISOR_READOUT / EVIDENCE-BOUNDED`

This index governs the short Hebrew readout and six-slide deck. It contains only published, aggregate, non-sensitive information. It does not bind or disclose private run artifacts.

## Permitted sources

| Source | Permitted use in this package | Evidence boundary |
|---|---|---|
| `2026-09-06-study1-airtravel-execution-and-analysis-receipt.md` | AirTravel scope, completed-episode denominator, Q&A totals, routes, and Detector-v1 labels | `ARCHIVAL / RETROSPECTIVE DESCRIPTIVE EVIDENCE` only |
| `2026-09-06-study1-airtravel-preliminary-results-he.md` | Hebrew wording for scope, log roles, alert interpretation, and limitations | Descriptive only; no accuracy or benefit conclusion |
| `2026-09-07-study1-data-log-pattern-transparency-he.md` | Separation of Detector-v1 and Agent-4, log roles, and availability wording | Agent-4 queue stays `NOT_AVAILABLE` without a validated queue artifact |
| `2026-09-08-study1-instrument-experiments-addendum.md` | The three offline instrument checks and their measured engineering denominators | First check: `ENGINEERING_FIXTURE_NOT_SCIENTIFIC`; the other two are engineering-only descriptive checks |
| `study1-signal-dictionary-v1.json` and `study1-transparency-data-dictionary-v1.json` | Frozen signal names and the distinction between Q&A, context, and mapping layers | No new calculation or result is derived here |

## Fixed reporting language

- Corpus: public external AirTravel material; four purposively selected cases.
- The four cases are `PURPOSIVE_NON_REPRODUCIBLE` among 21 eligible cases. They are not student data, Cheers/ParkWise, a representative sample, or synthetic gap fill.
- Detector-v1 operates on a Q&A episode and emits a reporting-level candidate-for-review label only.
- `התראה = מועמד לבדיקה אנושית בדוח.`
- Detector-v1 does not create a queue or change a source, target, guideline, or model.
- Agent-4 is a separate variability-classification mechanism. AirTravel status: `EXECUTED_THEN_BLOCKED`; queue status: `NOT_AVAILABLE`.

## Claim boundary

The archival run provides retrospective descriptive process evidence only. The package makes no claim about ground truth, error detection, accuracy, benefit, quality, superiority, generalization, or a completed ON/OFF comparison. Private evidence binding, human-rater assessment, and prospective evidence remain open.
