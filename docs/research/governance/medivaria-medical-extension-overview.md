# MediVARIA — Medical Extension Overview

Status: **derived summary of a supplied source document — not itself a decision, not a design, not verified evidence.** MediVARIA is the named public/funding-facing identity for the medical-transfer arm this project's other governance docs already track as **Plan A**. Nothing here changes the six-gate medical readiness status (`medical-readiness-scorecard.md`), which remains **0/6** regardless of this document.

## Provenance

| Field | Value |
| --- | --- |
| Source file | `MediVARIA_OnePage_v1.docx`, supplied by Ali on 2026-08-11 from `C:\Users\ahamed\Downloads\` |
| Bytes | 167,544 |
| SHA-256 | `70C49DB7EF6FCCEA991A87A077FA95AE29EBE173B97013F0CB683167878B1F13` |
| Document metadata | Created 2026-05-02T06:29:00Z; last modified 2026-05-05T15:01:00Z; **last modified by "Iris"** (per `docProps/core.xml`) |
| Relation to the external-fact register | This is very likely the document [EF-15](../phd-proposal/external-fact-register.md) already refers to as "the MediVARIA one-pager" from the 2026-07-29 call evidence — its existence and Iris's editorial involvement are now directly evidenced rather than only reported secondhand |
| Archived copy | Obsidian vault and Google Drive, `VEGO-AI PhD/` (not committed into git — external-party-editable source material stays out of the tracked repo by the same convention as other supplied binaries this project handles) |

## What MediVARIA is, in one paragraph

A one-page technical/funding proposal that repositions VEGO-AI's existing four-agent variability-classification architecture (built and evaluated for software/modeling, per this document submitted to ACM/IEEE MODELS 2026) into a clinical decision-support tool. Instead of asking whether a clinician followed a guideline, it asks *why* they deviated, and classifies the deviation as **justified clinical variability** (context-driven — e.g., adjusted dosing for renal impairment) or an **erroneous deviation** (e.g., a missed mandatory screening), producing a structured rationale rather than a bare verdict.

## Architecture mapping (per the document's own Figure 1 caption)

| VEGO-AI (software/modeling, as built) | MediVARIA (clinical, as proposed) |
| --- | --- |
| Agent 1 — Language Advisor (modeling-language grammar/metamodel) | Clinical documentation/guideline-language structure |
| Agent 2 — Domain Advisor (domain guideline corpus) | Clinical guideline corpus |
| Agent 3 — Model Inspector (student-produced case model) | Patient EHR trajectory |
| Agent 4 — Variability Explorer (justified vs. erroneous modeling deviation) | Justified clinical variability vs. erroneous deviation → actionable clinical quality signal |

The document's own framing: adapting to a new domain "requires only configuring the Domain Advisor with the relevant guideline corpus and adjusting EHR field mappings; the core pipeline does not require retraining." It also names three non-medical domains as further candidates by the same logic: pharmaceutical manufacturing, financial compliance, legal-procedure auditing — noted here for completeness; nothing in this project currently pursues them.

## Claims this document makes, and their verification state

Same five-state vocabulary as [`external-fact-register.md`](../phd-proposal/external-fact-register.md); scoped here to this document rather than the 29 July call, since that register is explicitly seeded from call evidence only.

| ID | Claim | Current verification state | What would verify it |
| --- | --- | --- | --- |
| MV-01 | A four-agent VEGO-AI pipeline was "submitted to ACM/IEEE MODELS 2026" | Unverified document statement | The actual submission record/confirmation, or the paper itself |
| MV-02 | Empirical TRL-3 baseline: Language Advisor F-scores 0.75–1.0; Domain Advisor guideline alignment 0.70–0.88; compliance scoring 0.80–0.96 "against expert review"; all identified variability patterns validated correct by domain experts | **Unverified against this repo's own evidence trail** — see flag below | The underlying dataset/evaluation record behind the MODELS 2026 submission (not the same artifact as `reports/generated/exp005-gate.json`) |
| MV-03 | Medical Partner: "TBD — Discussions Ongoing" (as of the document's 2026-05-05 last edit) | Partially corroborated — consistent with, and independently dated evidence for, the same "no named medical partner" state that `A-15`/`Q-02`/`Q-09`/`Q-10` and EF-08–EF-16 already track from the 29 July/5 August calls | A named, accountable clinical/institutional partner with written confirmation |
| MV-04 | Pursued on a 3-year duration under an "IIA Applied Research" track | Unverified document statement (almost certainly the Israel Innovation Authority, given the Israeli-HMO target-customer list; not independently confirmed) | Confirmation of the actual funding-track name, application status, and whether/how it's currently being pursued |
| MV-05 | "To our knowledge, no commercial system currently addresses the justified/erroneous distinction that MediVARIA is built around" | Unverified document statement (a novelty claim, same category the project's own literature-search-execution register exists to eventually test — QL-01..05 remain not-run) | Completion of a literature/market search scoped to CDSS and clinical-guideline-conformance products |

**Flag on MV-02, stated plainly:** these specific numbers are not the same artifact as EXP-005 (`reports/generated/exp005-gate.json`, currently 0/24 real labels, no accuracy claim authorized) — they describe an earlier, separate evaluation of the already-built software/modeling system, presumably backing the MODELS 2026 submission. They are recorded here as a claim from the supplied document, not verified by anything else in this repository. Treat them the same way every other unverified meeting/document statement in this project is treated: usable as context, not citable as established evidence, until their own source material is produced and checked.

## Open question this document surfaces (needs Ali, not a document search)

The document does not say, and nothing else read for this project says, whether **MediVARIA is the same effort as the PhD's Plan-A medical track** (just under a public/funding-facing name) or a **related but separate** project that shares the architecture and runs on its own funding/timeline independent of Ali's candidacy. This changes how it should be tracked — as the same set of six entry gates under a new label, or as a second, parallel governance thread with its own gates and its own relationship to Plan B. Left open here rather than guessed.

## How this fits with what's already tracked

- **Medical readiness (`medical-readiness-scorecard.md`):** unchanged — still 0/6 entry gates, still `BLOCKED (open)`. MediVARIA gives Plan A a public name; it does not supply a partner, an owner, or evidence for any of the six gates.
- **Gaps report (`../meetings/2026-08-11-full-gaps-and-blockers-report.md`), Root Blockers I and J:** MediVARIA's own "Medical Partner: TBD" independently corroborates, with an independent date (2026-05-05), that no partner has been named — consistent with, not a change to, the existing blocker.
- **External-fact register, EF-15:** upgraded from "Unverified meeting statement" to "Partially corroborated" — the one-pager's existence and Iris's editorial involvement are now directly evidenced; the "another innovation partner was reportedly involved" half of that claim remains unverified.
