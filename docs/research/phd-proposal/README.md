# PhD Proposal Working Package

Status: **working package for supervisor review; no research question, medical route, dataset, partner, approval, or formal deadline is recorded as approved by these files.**

This directory turns the requirements from the 29 July 2026 supervisor call into a single proposal architecture: one umbrella research question, exactly three subquestions, three mapped studies, and two execution paths. The package is deliberately evidence-bounded. Software engineering/modeling is the current research baseline; medicine is a conditional transfer setting and has no reported result in this repository.

## Start here

1. [`2026-08-05-rq-decision-pack.md`](./2026-08-05-rq-decision-pack.md) — recommended wording, two wording variants, study mapping, and decisions requested from Iris and Arnon.
2. [`2026-07-29-doctoral-execution-plan.md`](./2026-07-29-doctoral-execution-plan.md) — end-to-end work plan, resources, gates, dependencies, risks, and provisional milestones.
3. [`proposal-v0.1.md`](./proposal-v0.1.md) — initial six-section proposal draft.
4. [`legacy-rq-crosswalk.md`](./legacy-rq-crosswalk.md) — maps earlier MSc, PhD-roadmap, evidence, and MediVARIA questions into the new three-subquestion hierarchy.
5. [`../meetings/2026-08-05-supervisor-pre-read.md`](../meetings/2026-08-05-supervisor-pre-read.md) — concise supervisor-facing pre-read.
6. [`iris-requirements-closure-audit.md`](./iris-requirements-closure-audit.md) — point-by-point `R/A/Q` readiness audit with call times, evidence, presentation checks, and remaining gates.
7. [`../meetings/2026-08-05-supervisor-presentation-checklist.md`](../meetings/2026-08-05-supervisor-presentation-checklist.md) — 12-checkpoint video-call outline, full requirement coverage, decision worksheet, preflight, and closeout.
8. [`iris-alignment-experiment-register.md`](./iris-alignment-experiment-register.md) — separate non-production assurance series for traceability, presentation readiness, claim boundaries, and weekly propagation.
9. [`iris-arnon-requirements-2026-09-02.en.md`](./iris-arnon-requirements-2026-09-02.en.md) / [`.he.md`](./iris-arnon-requirements-2026-09-02.he.md) — reviewed paraphrase of the 2026-09-02 supervisor call that narrowed the preliminary study to one descriptive WHEN-to-escalate study and set the 09-03 / 09-06 / 09-09 deliverables.
10. [`iris-arnon-requirements-2026-09-02-checklist.md`](./iris-arnon-requirements-2026-09-02-checklist.md) — word-by-word checklist of that call (115 items) with where each is addressed.
11. [`2026-09-03-preliminary-study-design.en.md`](./2026-09-03-preliminary-study-design.en.md) / [`.he.md`](./2026-09-03-preliminary-study-design.he.md) — the one-page study design due Thursday 2026-09-03 (EXP-045; descriptive; no improvement claim).
12. [`2026-09-03-preliminary-human-intervention-experiment.en.md`](./2026-09-03-preliminary-human-intervention-experiment.en.md) — the strict one-page paired-condition experiment design for Iris: three frozen cases, explicit trigger status, bounded controlled human input, credible reference evidence, and no fabricated outcome.
13. [`2026-09-03-preliminary-study-two-page-backup.en.md`](./2026-09-03-preliminary-study-two-page-backup.en.md) — a two-page backup with more detail, if Iris asks for it; requests the course grading index by name.
14. [`2026-09-03-preliminary-study-comprehensive-paper.en.md`](./2026-09-03-preliminary-study-comprehensive-paper.en.md) — the full deep-research write-up (three pages, four figures) behind the one-pager, with the negative results stated explicitly.
15. [`study1-evidence-recovery-status-v1.json`](./study1-evidence-recovery-status-v1.json) — safe, aggregate-only recovery status; the accepted private event log is not mounted in this worktree, so no Study 1 values are emitted here.
16. [`study2-on-off-readiness-v1.json`](./study2-on-off-readiness-v1.json) and [`2026-09-06-study2-readiness-note.he.md`](./2026-09-06-study2-readiness-note.he.md) — strict ON/OFF output contract and fixture-only readiness boundary; no Study 2 result.
17. [`2026-09-06-study2-future-run-authorization-template.md`](./2026-09-06-study2-future-run-authorization-template.md) — one-time future-run binding template; `NOT_AUTHORIZED` and never a provider grant.
18. [`2026-09-06-study1-study2-canonical-draft-selection.md`](./2026-09-06-study1-study2-canonical-draft-selection.md) — fetched PR ancestry/divergence audit and canonical draft decision.

## Canonical working research architecture

**Umbrella research question**

_Provisional — this wording was refined live during the 2026-08-05 supervisor call with Iris Reinhartz-Berger and Arnon Sturm, superseding the 29 July working draft below. Evidence and caveats are in [`../meetings/2026-08-05-supervisor-meeting.md`](../meetings/2026-08-05-supervisor-meeting.md) (items E5–E10) and [`../meetings/2026-08-05-supervisor-provenance-manifest.md`](../meetings/2026-08-05-supervisor-provenance-manifest.md). It remains pending D-RQ-01 (umbrella RQ) and D-RQ-02 (SQ1–SQ3) sign-off — Ali still needs to verify the exact text against his own saved working notes from the call and log a supervisor decision — and must not be presented as approved, confirmed, or final._

How can human judgment be captured, governed, and used to support agentic-AI-driven variability exploration in guideline operationalization scenarios, enabling reliable human–AI co-reasoning?

| ID | Canonical working subquestion | Study |
| --- | --- | --- |
| SQ1 — Selective intervention | When and how, in variability exploration scenarios, should an agentic assessment system request human judgment so that important uncertainties are addressed without unnecessary expert burden? | Study 1 — intervention architecture |
| SQ2 — Governed knowledge reuse | How should expert judgment — including the system's core reasoning — be represented, validated, reconciled, and stored so it can be reused transparently without unsafe generalization or loss of human authority? | Study 2 — judgment lifecycle |
| SQ3 — Evaluation and transfer | How can expert judgment be reused and transferred across different guideline-operationalization contexts without unsafe generalization or loss of human authority, first in software/modeling and, when governance and access permit, in healthcare? | Study 3 — evaluation and transfer |

This is the working wording pending sign-off, not a supervisor-approved wording. Alternate phrasings are wording options for the same four conceptual slots; they are not additional research questions.

## Plan A and Plan B

- **Plan A — conditional medical transfer:** construct Studies 1 and 2, evaluate the complete framework first in software/modeling, and extend Study 3 to healthcare only after expert, data, access, ethics, privacy, infrastructure, and approved-local-LLM gates are evidenced.
- **Plan B — guaranteed non-medical completion:** answer the same umbrella question and three subquestions by evaluating the complete framework in software/modeling and a second software/modeling setting, dataset, diagram family, reviewer panel, or institution.

The fallback does not change the research questions; it changes the second evaluation setting. The medical route must never sit on the only path to doctoral completion.

## Binding evidence boundaries

- The current independent-evidence state is **0 of 24 adjudicated generalization-safe labels** and **0 of 2 independent reviewer returns**. Accuracy, macro-F1, generalization, effort-reduction, and superiority claims are not yet computable.
- Current results are software-engineering/modeling mechanism and evidence-readiness results. There are no clinical-performance results.
- MIMIC and MediVARIA are planning or familiarization resources, not approved datasets or completed studies.
- No patient data belongs in this repository. Restricted data must remain in its institutionally approved environment and must not be sent to a commercial or online-connected LLM.
- The recurring master event is verified as accepted by Ali, Iris, and Arnon: Wednesday 09:00–10:00 Asia/Jerusalem through the 2026-10-07 occurrence.
- Formal candidacy dates, reviewer count, committee rules, Drive receipt, and external-partner access must still be independently confirmed.

## Source hierarchy

1. [`../meetings/2026-07-29-iris-requirements-register.md`](../meetings/2026-07-29-iris-requirements-register.md)
2. [`../meetings/2026-07-29-iris-supervisor-action-register.md`](../meetings/2026-07-29-iris-supervisor-action-register.md)
3. [`../meetings/2026-07-29-iris-supervisor-call-report.md`](../meetings/2026-07-29-iris-supervisor-call-report.md)
4. Current repository evidence, especially [`../phd-thesis-optimization-plan.md`](../phd-thesis-optimization-plan.md), [`../independent-evidence/README.md`](../independent-evidence/README.md), and [`../literature-review-taxonomy.md`](../literature-review-taxonomy.md)

The underlying Hebrew ASR and English translation are machine-derived. Human bilingual review and full diarization remain pending. These proposal files use evidence-linked paraphrases only; they contain no direct quotations from the call.
