# Chapter 5 — Preliminary Results

> Status: working draft, written 2026-08-19 to close a gap flagged in the 2026-08-18 audit — real,
> already-run evidence existed with no chapter reporting it. Per `E13`, this chapter is
> software-engineering-domain results only; the medical track is infrastructure-building and
> feasibility work, not evidence, and is reported that way below. Every number below is read
> directly from the tracked run artifacts under `reports/generated/`, not summarized from memory.
> Nothing here claims accuracy, generalization, effort reduction, or clinical performance — that
> claim boundary is fixed by EXP-005 standing at 0 of 24 generalization-safe expert labels, which
> this chapter does not change.

---

## 5.1 What this chapter is evidence of, and what it is not

Two already-run experiment series back Study 1 and Study 2 respectively. Both are offline replays
and conformance tests against existing VEGO-AI/H-layer artifacts — mechanism and observability
evidence, never assessment-quality evidence. Nothing below answers whether selective intervention
or governed reuse actually improves anything; that question waits on EXP-005 labels that do not
yet exist. What these results do show is that the mechanisms describe real, inspectable behavior
rather than only a paper design.

## 5.2 Selective-intervention mechanism evidence (Study 1 / SQ1)

EXP-006 replays the H-Listen event stream against the existing baseline and reconstructs it into
481 contract-valid observation records spanning event types E1 through E14, with three types
(E3, E9, and the E10/E11/E14 group) explicitly marked unobservable in this baseline rather than
silently omitted — the instrumentation gap is recorded, not hidden. This establishes that the
event vocabulary the intervention-policy work depends on actually occurs in real runs, not only in
the architecture description.

EXP-007 replays four dosage-mode candidates against that same reconstructed stream and reports,
for each, event load relative to reviewing every decision and coverage of high-severity cases:
`threshold_sev1` (load 0.889, coverage 1.0), `threshold_sev2` (load 0.799, coverage 1.0),
`threshold_sev3` (load 0.578, coverage 0.726), and `first_n_then_auto` (load 0.581, coverage 0.73);
`every_decision` is the load-1.0/coverage-1.0 reference point and `silent` the load-0/coverage-0
one. The honest finding is a null result stated as such: the experiment's own guardrails target
coverage of at least 0.8 at load of at most 0.5, and no tested mode reaches both at once — the two
modes that cut load furthest (`threshold_sev3`, `first_n_then_auto`) also lose roughly a quarter of
high-severity cases. This is reported as an observed trade-off boundary, per the experiment's own
instruction not to select or silently tune a default, and not as a recommended operating point.

EXP-008 mines the same stream for triggers that were unstable (guideline definitions later
revised) but never reviewed at the time — 33 such candidates against 26 final guideline
definitions, an instability rate of 1.35. A capture-share sweep shows a capped review budget of 30
transactions surfaces 90.9% of them; every threshold tested at 1 or above surfaces all 33. This
bounds how large an early-trigger review queue would need to be to catch this class of case in
this corpus; it is not a claim that catching them improves downstream assessment quality.

## 5.3 Governed-lifecycle conformance evidence (Study 2 / SQ2)

Six conformance experiments (EXP-013 through EXP-018) all pass their stated acceptance criteria
against the existing judgment-memory implementation. EXP-013 verifies schema validity and lineage
completeness on 5 records, with the two known-unobservable event types (E3, E9) explicit rather
than silently dropped, and confirms that a parked evaluation-only signal (E15) cannot create a
live framework action. EXP-014 confirms deterministic, duplicate-free ordering across three
repeated runs. EXP-015 confirms high-severity items are preserved through deferred recovery with
no cross-subject bundle collisions. EXP-016 confirms that timeouts and denials park rather than
silently apply a correction, with zero trusted-memory writes and zero correction applications in
the tested scenarios. EXP-017 confirms every traced source family resolves deterministically
before any semantic step runs, with zero synthetic-memory contamination and missing sources
routed to adjudication rather than guessed. EXP-018 confirms a proposed change reproduces the same
diff without being applied and without modifying repository source.

Together these six passes are conformance evidence for the specific properties a governed
judgment-record contract would need — schema validity, determinism, non-destructive handling of
uncertainty, and provenance discipline — on the existing reference implementation only. They are
not evidence that an independently built implementation would conform, which is exactly the
implementation-independence gap Chapter 4 §4.4 already names as unresolved.

## 5.4 Medical context

Per `E13` and the evidence-state snapshot in `three-study-contract.md`, there are no medical
results to report here, by design. What exists is feasibility and infrastructure work only: a
Soroka data-access framework under discussion, an exploratory MIMIC dataset with no medical expert
attached to validate correctness, and a Ma'ayanei HaYeshua contact still forming a direction. None
of these produce a number this chapter could cite, and all six Plan A medical entry gates
(`G1`-`G6`) remain at 0 of 6. This section exists to say that plainly rather than by omission.

## 5.5 Evidence boundary for this chapter

Every result above is mechanism, observability, or conformance evidence, each reported at exactly
the scope its own experiment plan assigns it. None of it is read as evidence of assessment
quality, accuracy, generalization, expert-effort reduction, or clinical performance. EXP-007's
load figures in particular describe a property of an offline replay against one existing corpus,
not an effort-reduction result — the experiment's own guardrails forbid that reading, and this
chapter follows them. The gate that would license a quality claim, EXP-005, stands at 0 of 24
generalization-safe expert labels, unchanged by anything in this chapter. Study 3 (SQ3) has no
entry here because it evaluates transfer and reuse, which by design waits on Study 1 and Study 2
artifacts that are still recommendations rather than supervisor-confirmed designs, per Chapter 4.
