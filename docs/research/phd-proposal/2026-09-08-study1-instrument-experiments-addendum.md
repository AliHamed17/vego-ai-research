# Study 1 — Instrument Experiments Addendum

**Date:** 2026-09-08
**Scope:** Three offline experiments on the Study 1 instrument (Detector-v1) and its execution harness; they characterise reachable outputs and sensitivities and establish nothing about alert correctness.
**Provider calls made:** 0. **Detector-v1 modified:** No. **Credential state:** `OPENAI_API_KEY` absent from the execution environment (presence-only check). **Budget authorisation:** USD 6.00 authorised on 2026-09-08 for further experiments; unused.

All three experiments read only the accepted private evidence (`external_data/airtravel-pr38/v4-real-run/`, gitignored) or drive the protected orchestrator against deterministic fixtures. None produces scientific evidence about any model. Their outputs are folded into the results dossier (`docs/research/phd-proposal/VEGO-AI-Study1-Results-Dossier-HE.pdf`, sections 2, 8 and 11).

---

## 1. Gap addressed

The single accepted run classified 3/3 complete episodes as `STRONG_ALERT`, all through S1. The original fixture envelope (`scripts/airtravel_detector_envelope.py`) reached only `NO_ALERT` and `STRONG_ALERT`-via-S7, because its fake client hard-codes `confidence: High` and non-empty evidence. Consequently, before this work:

- `WEAK_ALERT` had never been produced anywhere, neither in evidence nor in a fixture;
- S3 (missing evidence) had never fired in either of its two encodings;
- no experiment had asked whether the reported classification depends on event order, on the completeness definition, or on the `any` aggregation over answers;
- the reserve arithmetic used to gate paid runs had never been calibrated against the one observed receipt.

## 2. Experiment A — Extended detector envelope (truth table)

**Script:** `scripts/airtravel_detector_envelope_extended.py` → `analysis/detector-envelope-extended.json`
**Evidence class:** `ENGINEERING_FIXTURE_NOT_SCIENTIFIC`. **Fixture calls:** 724. **Provider calls:** 0.

The fixture client in `scripts/airtravel_local_observer.py` is part of the accepted run's execution lineage and was not modified. A subclass injects, per mode, the answer confidence, the evidence value, and the rounds in which questions are emitted, so that each mode isolates one branch of the frozen rule. The three legacy modes run the parent class untouched.

| Mode | Isolated branch | Confidence | Evidence | Rounds asked | Denominator | STRONG / WEAK / NO | Signals | Conforms |
|---|---|---|---|---|---|---|---|---|
| `no_questions` | no episode; denominator 0 | High | present | none | 0 | 0 / 0 / 0 | — | ✓ |
| `two_rounds` (legacy) | no signal | High | present | 1 | 10 | 0 / 0 / 10 | — | ✓ |
| `max_rounds` (legacy) | S7 (S6 necessarily co-fires) | High | present | all | 11 | 11 / 0 / 0 | S6, S7 | ✓ |
| `low_single` | S1 alone | Low | present | 1 | 10 | 10 / 0 / 0 | S1 | ✓ |
| `empty_evidence_single` | S3 alone, length-0 encoding | High | `""` | 1 | 10 | 10 / 0 / 0 | S3 | ✓ |
| `null_evidence_single` | S3 alone, null encoding | High | absent | 1 | 10 | 10 / 0 / 0 | S3 | ✓ |
| `medium_single` | S2 alone | Medium | present | 1 | 10 | 0 / 10 / 0 | S2 | ✓ |
| `high_two_rounds` | S6 alone | High | present | 1, 2 | 10 | 0 / 10 / 0 | S6 | ✓ |
| `medium_two_rounds` | S2 and S6 together | Medium | present | 1, 2 | 10 | 0 / 10 / 0 | S2, S6 | ✓ |

Conformance requires every scored episode to land in the expected class **and** to show exactly the expected signal set. Result: 9/9 modes conform; all three classes are reachable; S1, S3 (both encodings), S2 and S6 are each reached in isolation. S7 cannot be isolated from S6, since reaching the round cap implies more than one round.

**Methodological note (disclosed deliberately).** A first implementation forced questions by temporarily switching the parent fixture into its `max_rounds` mode. That mode also injects a `variability_classifications` row with `flag_for_guidelines_update: True` on `agent4/classify` labels, which altered the pipeline's phase structure: the legacy `two_rounds` mode produced fewer episodes and S6 fired in every mode. The intermediate output was not retained, so those in-session observations are not verifiable from a shipped artefact (`Unknown`). The final implementation keeps the parent permanently in its `no_questions` state, adds questions onto the parent's empty result for exactly the scheduled rounds and never touches the classify branch; `two_rounds` classifies 10/10 `NO_ALERT`, identical to the original envelope. The unit tests pin this: new modes must return an empty `variability_classifications` list for `agent4/classify_r1`.

**What it shows:** the instrument is not degenerate in any branch. **What it does not show:** anything about the frequency of any branch under a real model, on this corpus or any other.

## 3. Experiment B — Instrument robustness on the accepted log

**Script:** `scripts/study1_instrument_robustness.py` → `analysis/instrument-robustness.json`
**Evidence class:** `DESCRIPTIVE_INSTRUMENT_ROBUSTNESS_ON_ONE_ACCEPTED_RUN`. **Provider calls:** 0. **Event log SHA-256:** `55ea9361…d117cac4`.

| Check | Result |
|---|---|
| Event-order invariance | 500/500 seeded permutations and 3/3 named reorderings (reversed, by event type, by episode then type) yield identical per-episode classifications. Episodes with more than one `EPISODE_TERMINATED` event: 0. |
| Value domain | 44 answers; confidence labels Low 16 · Medium 25 · High 3; labels outside {Low, Medium, High}: 0; recorder `UNKNOWN` fallback: 0; evidence ref null: 0; evidence ref length 0: 0. |
| Denominator sensitivity | Frozen completeness (`CONVERGED` or `TERMINATED_MAX_ROUNDS`): denominator 3, distribution 3 / 0 / 0. Hypothetical stricter completeness (`CONVERGED` only — not the preregistered rule): denominator 2, distribution 2 / 0 / 0. `INCOMPLETE_TECHNICAL` present: 0. |
| Leave-one-episode-out | Each removal leaves the remaining two episodes at 2 / 0 / 0. |

**Aggregation sensitivity (descriptive; not a detector).** Detector-v1 reads confidence with `any` over an episode's answers. For each alternative summary of the same recorded answers, the frozen rule is re-applied with the S1/S2 contribution replaced by the summary label while S3, S6 and S7 are kept exactly as recorded. Each cell shows the confidence label under that summary and the class it yields:

| Episode | Answers | Rounds | Low / Medium / High | Other recorded signals | `any` (frozen) | majority | ordinal median | first round | final round | plurality |
|---|---|---|---|---|---|---|---|---|---|---|
| `EP-577319bf…` | 1 | 1 | 1 / 0 / 0 | — | Low → STRONG | Low → STRONG | Low → STRONG | Low → STRONG | Low → STRONG | Low → STRONG |
| `EP-cefe8dd7…` | 4 | 2 | 3 / 1 / 0 | S6 | Low → STRONG | Low → STRONG | Low → STRONG | Low → STRONG | Low → STRONG | Low → STRONG |
| `EP-81b2c98d…` | 39 | 10 | 12 / 24 / 3 | S6, S7 | Low → STRONG | **Medium → STRONG** | **Medium → STRONG** | Low → STRONG | Low → STRONG | **Medium → STRONG** |

Agreement with the frozen rule at the classification level: 3/3 under every summary. At the label level: majority 2/3, ordinal median 2/3, first round 3/3, final round 3/3, plurality 2/3. In the largest episode the S1 signal fires only under `any` — under a majority, ordinal-median or plurality summary its confidence label is Medium — but the episode's `STRONG_ALERT` class is preserved by S7 (`TERMINATED_MAX_ROUNDS`), which does not read confidence. Therefore **no classification in this run depends on the aggregation rule; the S1 signal in one of three episodes does.** "Majority" is a true majority (a label held by more than half the answers, otherwise `NO_MAJORITY`); "ordinal median" is the median on the ordered scale Low < Medium < High. None of these summaries is proposed as a rule, and Detector-v1 is unchanged.

*Correction record.* An earlier draft of this addendum and of dossier section 2 (2026-09-08, before independent review) stated that one of three classifications rested on the `any` aggregation. That statement compared confidence labels rather than re-applied classes and overlooked S7; it was withdrawn on the same day after the adversarial review identified it. The script now recomputes the class per summary and refuses to run if its re-application of the rule disagrees with Detector-v1 on the recorded answers.

## 4. Experiment C — Cost calibration and reserve-bound protocol menu

**Script:** `scripts/study1_cost_calibration.py` → `analysis/cost-calibration.json`
**Evidence class:** `DESCRIPTIVE_COST_CALIBRATION_FROM_ONE_ACCEPTED_RECEIPT`. **Provider calls:** 0.

Aggregate actuals from the accepted receipt (no per-call ledger exists, so maxima and per-episode attribution are `NOT_AVAILABLE`):

| Quantity | Value |
|---|---|
| Outbound requests | 43 |
| Mean prompt tokens per request | 4,338.6 |
| Mean completion tokens per request | 1,892.7 |
| Mean cost per request | USD 0.003139 |
| Maximum prompt / completion per request | `NOT_AVAILABLE` |
| Cost per episode | `NOT_AVAILABLE` |

Reserve versus actual (reserve per request = (8,000 × 0.20 + max_out × 1.20) / 10⁶):

| Bound | Reserve / request | × 43 | Actual | Ratio | Mean completion as share of output cap |
|---|---|---|---|---|---|
| Study 1B frozen (16,384 out) | USD 0.0212608 | USD 0.9142 | USD 0.134972 | 6.77× | 12% |
| Pilot frozen (4,096 out) | USD 0.0065152 | USD 0.2802 | USD 0.134972 | 2.08× | 46% |

The input reserve of 8,000 tokens is a configuration constant, not a bound derived from the receipt: the largest prompt actually sent is `NOT_AVAILABLE`. The share of requests the 4,096-token pilot cap would truncate cannot be bounded from this receipt; any truncated finish must be recorded, never silently accepted.

**Protocol menu.** Thirty protocols (repeats 1–5 × call cap {90, 180, 326} × output cap {4,096, 16,384}) were enumerated. Each bound is repeats × call cap × reserve per request and holds only under the assumption that every prompt fits the 8,000-token input reserve; it bounds reservations, not spend, if a single prompt exceeds that reserve. 16 fit a USD 6.00 ceiling; 5 fit USD 2.00. The frozen Study 1B protocol (5 × 326 × 16,384) has a reserve bound of USD 34.6551 and fits neither. Protocols fitting USD 6.00:

| Output cap | Fitting protocols (repeats × call cap → bound) |
|---|---|
| 4,096 | 1×90 → 0.5864 · 2×90 → 1.1727 · **3×90 → 1.7591 (frozen pilot)** · 4×90 → 2.3455 · 5×90 → 2.9318 · 1×180 → 1.1727 · 2×180 → 2.3455 · 3×180 → 3.5182 · 4×180 → 4.6909 · 5×180 → 5.8637 · 1×326 → 2.1240 · 2×326 → 4.2479 |
| 16,384 | 1×90 → 1.9135 · 2×90 → 3.8269 · 3×90 → 5.7404 · 1×180 → 3.8269 |

Fitting a ceiling is arithmetic on frozen reserve constants. It is not authorisation to run, not a prediction of spend, and not evidence that a protocol would yield usable episodes.

## 5. Claim boundary

Permitted: the instrument reaches every class and every isolable branch on deterministic input; the reported classification of the accepted run is invariant to event order; the S1 signal in one of three episodes depends on the `any` aggregation while no classification does; the frozen reserve over-estimates observed spend by the stated factors on one receipt.

Forbidden: alert correctness; accuracy, precision, recall, F1; effectiveness; human benefit; causality; representativeness; generalisation; any reading of fixture rows as evidence about a model; any merging of fixture denominators with the accepted run's denominator; any presentation of the aggregation-sensitivity columns as alternative detectors.

## 6. Authorisation and execution status

- USD 6.00 was authorised for further experiments on 2026-09-08. No provider call has been made under it.
- `OPENAI_API_KEY` is absent from the execution environment. Presence was checked; the value was never read.
- The constrained exploratory pilot remains `PREREGISTERED_NOT_EXECUTED`; its gate 4 (independent review) is outstanding and gate 6 (confirmation of frozen model `gpt-5.6-luna`, ceiling and caps) is unconfirmed.
- Study 1B remains `BUDGET_BLOCKED_UNDER_FROZEN_PROTOCOL`. The menu shows that no five-repeat protocol at the Study 1B output cap fits USD 6.00 either.
- A protocol executed under the USD 6.00 ceiling would require its own preregistration naming the exact (repeats, call cap, output cap) row from the menu, `BudgetGuard` set to USD 6.00, the frozen model, and a present credential.
- The dossier records the authorisation from this document and decision D8, measures credential presence at build time (presence only), and scans the private evidence root for paid-run receipts dated on or after the authorisation (none exist).

## 7. Artifacts and regeneration

| Artifact | Path | Tracked |
|---|---|---|
| Extended envelope | `scripts/airtravel_detector_envelope_extended.py` | yes |
| Robustness | `scripts/study1_instrument_robustness.py` | yes |
| Cost calibration | `scripts/study1_cost_calibration.py` | yes |
| Tests (53) | `scripts/tests/test_airtravel_detector_envelope_extended.py` | yes |
| Dossier builder / renderer | `scripts/build_study1_results_dossier.py`, `scripts/render_study1_results_dossier.py` | yes |
| Rendered HTML | `docs/research/phd-proposal/figures/study1-results-dossier.html` | yes |
| Dossier PDF | `docs/research/phd-proposal/VEGO-AI-Study1-Results-Dossier-HE.pdf` | no (`*.pdf` ignored; regenerate locally) |
| Analysis outputs | `external_data/airtravel-pr38/v4-real-run/analysis/{detector-envelope-extended,instrument-robustness,cost-calibration,results-dossier}.json` | no (`external_data/**` ignored) |

```bash
py -3.13 scripts/airtravel_detector_envelope_extended.py --output external_data/airtravel-pr38/v4-real-run/analysis/detector-envelope-extended.json
py -3.13 scripts/study1_instrument_robustness.py --output external_data/airtravel-pr38/v4-real-run/analysis/instrument-robustness.json
py -3.13 scripts/study1_cost_calibration.py --output external_data/airtravel-pr38/v4-real-run/analysis/cost-calibration.json
py -3.13 scripts/build_study1_results_dossier.py --output external_data/airtravel-pr38/v4-real-run/analysis/results-dossier.json
py -3.13 scripts/render_study1_results_dossier.py --dossier external_data/airtravel-pr38/v4-real-run/analysis/results-dossier.json --output docs/research/phd-proposal/figures/study1-results-dossier.html
```

The PDF is printed from the HTML with headless Chrome (`--headless=new --no-pdf-header-footer --print-to-pdf=…`); the previous package's SVG bidi and fixed-footer defects do not apply because the dossier uses CSS bars and no fixed elements.
