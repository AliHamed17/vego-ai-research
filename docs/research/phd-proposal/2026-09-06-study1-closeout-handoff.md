# Study 1 close-out and Study 2 handoff

**Date:** 2026-09-06 · **Prepared by:** Claude, as scientific lead, independent auditor and
supervisor-facing reporting owner.

No provider was called. No model, API, paid call or new experiment was run. Detector-v1, its
thresholds and preregistration v1.0.1/v1.0.2 are unmodified. No scientific result was
fabricated, inferred, pooled or gap-filled. All raw evidence remains private and git-ignored;
only hashes, aggregate counts and safe metadata are tracked.

---

## 1. Evidence status

**`DERIVED_CHAIN_BROKEN` — with every scientific value reproducing.**

The validator was extended from 20 checks to 92 and re-run against the accepted private
artifacts. It recomputes each quantity from the persisted event log, run receipt and pipeline
outputs, then compares it against every derived analysis file.

| | |
|---|---|
| Checks executed | **92** |
| Passed | **87** |
| Scientific value failures | **0** |
| Provenance gaps | **4** |
| Derived-artifact chain failures | **1** |

Recomputed and confirmed: 3 episodes (2 `CONVERGED`, 1 `TERMINATED_MAX_ROUNDS`), 0
`INCOMPLETE_TECHNICAL`, denominator 3; 44 questions and 44 answers; maximum round index 10; 3 of
6 directed route pairs (asking agent4 / answering agent2 = 39, agent3 / agent2 = 4, agent3 /
agent1 = 1); answer confidence Low 16 / Medium 25 / High 3; evidence length n 44, min 38, median
62, max 540, zero-length 0; Detector-v1 `STRONG_ALERT` 3, `WEAK_ALERT` 0, `NO_ALERT` 0 with
signals S1 3, S2 2, S6 2, S7 1, S3 0; 43 outbound requests of a 326 cap; 186,558 + 81,384 =
267,942 tokens; USD 0.134972 of a USD 10.00 budget, reproduced from the published prices; 0
blocked egress attempts. The event-log and run-receipt hashes both reproduce byte-exactly.

## 2. Provenance status

**`PARTIAL_EVIDENCE_ONLY / DESCRIPTIVE_REPORTING_WITH_RETROSPECTIVE_PROVENANCE`.**

The private evidence was validated retrospectively; the original receipt did not self-bind the
event-log hash, lifecycle summary, or execution-code SHA. Provenance is fixed at execution time.
**Supervisor acknowledgement does not upgrade this run to prospective or preregistered
provenance** — only a new authorized run whose receipt self-binds all three fields can.

Four gaps, three of them in the run receipt:

| # | Gap | Nature |
|---|---|---|
| 1 | Receipt does not bind its own event-log hash | binding absent |
| 2 | Receipt carries no lifecycle summary | binding absent |
| 3 | Receipt does not record the execution-code SHA | binding absent |
| 4 | `MAX_QA_ROUNDS` is a harness constant, not recorded in the receipt | binding absent |

The receipt was **not** amended. Retrofitting it would manufacture the provenance the caveat
exists to disclose.

### 2.1 The one chain failure — self-inflicted, disclosed, unrecovered

`analysis/output-inventory.json` was overwritten on 2026-09-06 by an invocation of the validator
that was pointed at it as `--manifest`. The pin `output_inventory_sha256 = abbdd70e…` in
`analysis/analysis-receipt.json` therefore no longer resolves; the file now hashes to
`d02603ad…`.

Recovery was attempted before disclosure: all 52 pinned artifacts still exist unchanged, so a
serialization reproducing the pinned digest would have been proof rather than reconstruction.
144 candidates were tried across three artifact sets, three path roots, two value shapes, two
wrappers and four encoders. None matched. **The file was not reconstructed** — continuing would
have been hash-grinding, and writing a substitute would have fabricated provenance.

Scope: no published claim cites that file; the primary evidence under `output/` is untouched and
both published hashes re-verify. A first classification of this as a provenance gap was wrong and
was corrected on review — a binding that exists and does not resolve is a value failure, not a
missing binding. The validator now refuses to write over any file it did not produce.

## 3. Defects found and corrected

| Defect | Where | Disposition |
|---|---|---|
| C2 and C3 published as `NOT_AVAILABLE` | every Study 1 document | **Withdrawn.** Both are computable: C2 High 15 / Medium 4; C3 true 14 / false 5, over 19 variability patterns. The validator now asserts computability, so the claim cannot return. |
| All four SVG figures unreadable | `fig1`–`fig4` | **Fixed.** `direction="rtl"` with `text-anchor="end"` anchors the left edge, so every label ran off the viewBox and rendered as one or two characters. 29 elements re-anchored; verified by rasterising. These are embedded in the Hebrew report, so broken figures had been shipping. |
| A false zero in the derived analytics | `airtravel_extended_analytics.py` | **Fixed at source.** It read `deviation_patterns.json` for a key that does not exist, publishing `0` where the evidence holds 19 recurring fragment patterns. |
| Validator fail-open on a missing artifact | `study1_validate_evidence.py` | **Fixed.** Deleting a derived file removed its cross-checks and still reported success. |
| Validator stamped a commit a dirty tree cannot produce | same | **Fixed.** Tree state is now a check and the stamp is marked `+DIRTY_TREE`. |
| Validator required all three confidence levels | same | **Fixed.** A level that never occurs is a legitimate observation. |
| Stale heads, stale CI claims, stale check counts | PR #38, PR #41, dashboards | **Corrected**, each CI claim now naming its run id and head. |

## 4. Claims accepted

Descriptive only, on this corpus, under this configuration:

- one authorized provider-backed run on `cd_airtravel` / `text2uml_airtravel_253b26dc`, N = 4,
  denominator 3 complete episodes;
- the counts in §1, each recomputed from the raw event log;
- inter-agent communication can be captured end to end, preserved as hash-verified evidence, and
  classified by a rule frozen before any output was observed, at a provider cost of USD 0.135;
- the mapping result for this run is 4 of 4 cases `Satisfied`;
- 19 recurring fragment patterns, labelled `Alternative` 14 and `Domain Mistake` 5, with
  `probe_confirmed` false on all 19;
- **on this corpus all three episodes fall on the same side of the threshold**, so Detector-v1
  does not separate them and is not usable for prioritisation in its current state.

## 5. Claims rejected

Accuracy, precision, recall, F1; alert correctness; that any error occurred; human benefit or
intervention effectiveness; representativeness; generalization to other cases, models, corpora or
settings; provider performance; any quality claim — no independent quality measure exists; any
statement about student behaviour or historical Cheers/ParkWise material; and any claim that
supervisor acknowledgement upgrades this run's provenance.

**`STRONG_ALERT` means one thing: the episode is a candidate for human review.** It is not a
finding that an error occurred, that the model was wrong, that output was defective, or that
intervention was required. Alert correctness is untested and is not testable from this data,
because no ground-truth labels exist.

The three layers are reported separately and must not be conflated: (a) the **mapping result**
(`Satisfied` / `Partially-Satisfied` / `Not-Satisfied`), which feeds nothing; (b) the
**conversation-state signal** (answer confidence, evidence-field presence, round count), which is
Detector-v1's only input; (c) the **operational action**, candidacy for human review. An
`Alternative` label and a `Not-Satisfied` mapping both sit in layer (a). Neither is an error and
neither triggers an alert.

A context observation, recorded and not interpreted: the pipeline's own `requires_human_review`
flag is `false` on all 19 variability rows while Detector-v1 marked 3 of 3 episodes. These are
different units of analysis, neither is ground truth, and they neither confirm nor refute each
other.

## 6. Remaining gaps

1. The four provenance gaps in §2 — removable only by a new authorized run with a self-binding
   receipt. The harness is already repaired to bind all three receipt fields.
2. The overwritten `analysis/output-inventory.json` — unrecovered, disclosed, referenced by no
   published claim.
3. `outbound_requests = 43` is receipt-asserted: the run persisted no per-call ledger, so it can
   be checked for internal arithmetic consistency but not independently recomputed.
4. Cached-token counts were never captured by the run counter and are reported `NOT_AVAILABLE`.
5. Study 2 has no result and no bound paid-run harness (§7).

## 7. Study 2

**Design status `PREPARED_NOT_EXECUTED`. Implementation verdict
`NOT_READY_FOR_PAID_AUTHORIZATION`.** Not pooled with Study 1, not a baseline for Study 1, and
carrying no result of any kind.

The preregistration is at version 2. Version 1 is withdrawn: it declared orchestration the single
varying factor — contradicted by the harness's own prompt-difference receipt — and defined no
primary outcome. Version 2 sets a **system comparison** framing, a **blinded human-rubric primary
outcome** with judges, blinding procedure, five dimensions, an agreement threshold and a
`NOT_COLLECTED` fallback; secondary descriptive outcomes; an absolute prohibition on
cross-condition alert comparison; N = 4 as a purposive feasibility sample with inference
prohibited by name; predefined handling of missingness, schema failure, partial output and
**zero-Q&A behaviour** (a valid observation, not a failure); a ban on outcome-dependent retry and
model switching; a paired offline preflight before separate per-condition authorization; and
Llama confined to a separately preregistered Study 2B.

Blocking preconditions, from the independent implementation review: six controls the Study 2
harness does not bind that the Study 1 paid harness does — budget guard, request cap, egress
restriction, model identity, max output tokens, and timeout/retry enforcement — plus an
unenforced frozen case set. Three preregistered outcomes (tokens, cost, technical failures) are
not measurable by any Study 2 code. The preflight's `evidence_class` and `provider_calls` are
hardcoded literals rather than observations, and OFF's absence of hidden Q&A is asserted rather
than instrumented. The fixture run produced **0 versus 0 on every per-case row**, so it
demonstrates plumbing only.

No Study 2 implementation file was modified: that is Codex's lane. The review hands over ten
required corrections.

## 8. Supervisor-facing conclusion

A single authorized run on four public-external cases shows that inter-agent communication can be
captured end to end, preserved as hash-verified evidence, and classified by a pre-frozen rule, at
negligible cost. Every published number reproduces from the raw event log under 92 automated
checks.

The scientifically useful finding is a **negative** one: all three episodes land in the same
alert class, so the frozen threshold does not discriminate on this corpus and cannot serve as a
prioritisation mechanism as it stands. Nothing here shows that any alert was correct, useful or
necessary — that question needs ground-truth labels, which do not exist for this corpus, and it
is the substance of the proposed follow-up study.

Two honest caveats travel with the package: provenance for this run was established after
execution rather than at it, and one derived inventory file was destroyed during this work and
could not be recovered. Neither affects any published value, and both are recorded rather than
smoothed over.

## 9. Artifacts

| Artifact | Path |
|---|---|
| Hebrew results report | `docs/research/phd-proposal/2026-09-06-study1-airtravel-preliminary-results-he.md` |
| Hebrew technical appendix | `…-study1-airtravel-technical-appendix-he.md` |
| Hebrew six-slide outline | `…-study1-airtravel-six-slides-he.md` |
| Hebrew evidence-status | `…-study1-evidence-status-he.md` |
| Execution and analysis receipt | `…-study1-airtravel-execution-and-analysis-receipt.md` |
| Supervisor PDF | `docs/research/phd-proposal/VEGO-AI-Study1-Supervisor-Report-HE.pdf` |
| Results PDF | `…/VEGO-AI-Study1-AirTravel-Results.pdf` |
| Technical appendix PDF | `…/VEGO-AI-Study1-Technical-Appendix-HE.pdf` |
| Study 2 preregistration v2 | `…-study2-preregistration-draft.md` |
| Study 2 implementation review | `…-study2-implementation-review.md` |
| Study 2 supervisor one-pager | `…-study2-supervisor-onepage-he.md` |
| Validator (single source of truth) | `scripts/study1_validate_evidence.py` |
| Validator tests | `scripts/tests/test_study1_validate_evidence.py` |

The PDFs are git-ignored build outputs and regenerate from the HTML sources under
`docs/research/phd-proposal/figures/`.
