# Per-RQ Literature Map and Coverage-Gap Check

Status: **working map for the 2026-08-12 supervisor meeting — inventory + gap analysis, not a completed review**

Source of the requirement: 2026-08-05 supervisor call, `A08-03` — build a literature
spreadsheet with a per-question tag (RQ1 / RQ2 / RQ3 / general), and use the pass to
"see we're covering all the relevant literature," i.e. an explicit coverage-gap check,
not just an inventory of what already exists.

Relation to other assets: the [native Google Sheet](https://docs.google.com/spreadsheets/d/1tVAM10bxlmL7_8SbgDgN5BRfAR2f5Q4pGvQmx-Ypp4A/edit)
remains the row-level workbook of record (one paper = one row); the
[QL-01–QL-05 register](../docs/research/phd-proposal/literature-search-execution-register.md)
remains the frozen search protocol (still `PROTOCOL READY / NOT RUN`); and
[`hitl-resource-pack/source-manifest.csv`](hitl-resource-pack/source-manifest.csv) carries the
`rq_tag` column at the file level. This map is the *view across all three*: what each RQ
currently has, and — the part Iris asked for — what each RQ still visibly lacks.

RQ labels here mean the three live sub-questions (2026-08-05 wording, provisional):
**RQ1** = SQ1 selective intervention; **RQ2** = SQ2 governed knowledge reuse;
**RQ3** = SQ3 evaluation and transfer.

## 1. Current per-RQ inventory (everything tagged so far)

Titles below are the exact `source-manifest.csv` strings. / הכותרות להלן הן המחרוזות המדויקות מה-CSV.

| RQ | Sources currently tagged | Type | From |
| --- | --- | --- | --- |
| RQ1 | HITL-001 ("Human-in-the-loop machine learning: a state of the art") | survey | resource pack |
| RQ1 | TOOL-003 ("modAL active learning framework") | tool | resource pack |
| RQ2 | TOOL-001 ("Label Studio"), TOOL-002 ("Argilla"), TOOL-004 ("cleanlab open-source documentation") | tools | resource pack |
| RQ3 | *(none yet)* | — | — |
| general | HAI-001 ("Guidelines for Human-AI Interaction"); GOV-001 ("NIST AI Risk Management Framework 1.0"); MDE-001 ("AI Assisted Domain Modeling Explainability and Traceability") | guidelines / governance / positioning | resource pack |
| (Sheet) | 6 seed rows in the native workbook (tagged there per its own taxonomy) | mixed | Google Sheet |

## 2. Coverage-gap check per RQ (the actual deliverable)

Verdict format: what the RQ *needs* literature-wise to argue its gap in Chapter 2/3 →
what exists → what is missing → which frozen query closes it.

### RQ1 — Selective intervention

Needs: human-oversight/HITL surveys; selective prediction & learning-to-defer;
uncertainty calibration of LLM/agentic outputs; alert-fatigue and interruption-cost
studies; review-budget/workload-aware triage designs.

| Needed cluster | Have | Gap | Closing route |
| --- | --- | --- | --- |
| HITL/oversight surveys | HITL-001 | Thin — one survey; need agentic/multi-agent-specific oversight work | QL-01 |
| Learning-to-defer / selective prediction | — | **Missing entirely** | No frozen query carries deferral/selective-prediction terms — QL-04 is the nearest hook (uncertainty/workload terms); expect to need **targeted snowballing** beyond the frozen set |
| LLM/agent uncertainty calibration | — | **Missing entirely** | QL-04 (the only frozen query containing "uncertainty"); QL-01 lacks calibration terms — supplement with snowballing |
| Alert fatigue / interruption cost | — | Missing on the SE side; the medical side (CDSS alert fatigue) is covered by QL-05 but only for Plan A | QL-04, QL-05 |
| Workload/budgeted triage | TOOL-003 (tool only — not research evidence) | Research-grade sources missing | QL-04 |

### RQ2 — Governed knowledge reuse

Needs: knowledge-representation/engineering for case-grounded expert rules; provenance
models; RLHF/preference-learning contrast literature (the "weight-absorbed" pole);
annotation/adjudication disagreement research; knowledge-base maintenance/staleness;
authority & contestability in socio-technical systems.

| Needed cluster | Have | Gap | Closing route |
| --- | --- | --- | --- |
| Structured feedback capture tooling | TOOL-001/002/004 (tools only) | Research-grade capture/representation sources missing | QL-02 |
| Provenance & governance frameworks | GOV-001 (framework-level) | Paper-level provenance-for-AI-knowledge sources missing | QL-02 |
| RLHF/preference learning (contrast pole) | — | **Missing entirely** — needed to argue the "two failing extremes" gap | No frozen query carries RLHF/preference terms; QL-02's mandatory second concept rarely matches this literature — expect **targeted snowballing** |
| Annotator disagreement / adjudication | — | **Missing entirely** — needed for validation/reconciliation design | QL-02 (its "reconciliation" term is the only hook; note QL-04 is register-mapped to SQ1/SQ3) + snowballing |
| Knowledge staleness / revocation | — | **Missing entirely** | QL-02 |

### RQ3 — Evaluation and transfer

Needs: cross-domain transfer studies of human-AI systems; external-validity and
leakage methodology; domain-adaptation vs. general-capability analyses; evaluation
protocols with independent labels; SE↔medical transfer precedents.

| Needed cluster | Have | Gap | Closing route |
| --- | --- | --- | --- |
| Anything at all | **zero tagged sources** | **RQ3 is the emptiest question — highest-priority gap in the whole map** | QL-03, QL-04, QL-05 |
| Leakage/evaluation methodology | (internal protocols exist; no external literature tagged) | Missing | QL-04 |
| Domain-specific vs. general capability framing (Arnon's E12 axis) | — | Missing; likely needs targeted snowballing beyond the frozen queries | QL-03 + snowballing |

### General / positioning

HAI-001, GOV-001, MDE-001 provisionally cover design-guideline, governance, and
MDE-positioning roles for the proposal stage — a working judgment pending the QL runs, not a
coverage finding; the MDE-assessment-gap positioning (retired SQ5) additionally reuses the
taxonomy in `docs/research/literature-review-taxonomy.md`.

## 3. What this means for the Aug-12 conversation

1. **Tag column: done at the file level** — `rq_tag` exists in the manifest CSV and each
   source above is assigned; the same column should be replicated in the native Sheet
   (owner: Ali, ~10 minutes — the Sheet is the workbook of record).
2. **Coverage verdict to present:** RQ1 thin, RQ2 tool-heavy/research-light,
   **RQ3 empty** — a defensible, honest snapshot that directly answers Iris's "are we
   covering the relevant literature?" question with "not yet, and here is exactly where."
3. **No search has been run** (QL-01–QL-05 all remain `Protocol ready / not run`), so
   this map creates no novelty or completeness claim — consistent with Iris's
   instruction to *think about* the survey but not execute it yet (`A08-04`).
4. Suggested Sheet addition: one row per *needed cluster* above (with an empty
   source cell), so the coverage gaps are visible inside the workbook itself rather
   than only in this repo document.

---

*Prepared 2026-08-10 for the Aug-12 meeting; derives from `A08-03` in the canonical
2026-08-05 record. Tags are working assignments, not screening decisions.*
