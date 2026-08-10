# Supervisor Pre-Read — Doctoral Research Architecture

Prepared for: Iris Reinhartz-Berger and Arnon Sturm
Prepared by: Ali
Provisional checkpoint: 5 August 2026
Status: **working pre-read; recurring calendar verified, research decisions pending, and this pre-read is not recorded as sent**

Verified meeting logistics: the recurring master event is accepted by Ali, Iris, and Arnon for Wednesday 09:00–10:00 Asia/Jerusalem through the 2026-10-07 occurrence. Calendar acceptance confirms cadence only; it does not approve the research architecture.

## Purpose

The requested outcome is a decision on one umbrella PhD research question, exactly three subquestions, their three-study mapping, and the Plan A/Plan B interpretation. The proposal can then advance in parallel with the literature review and candidacy-process verification.

Detailed pack:

- [`../phd-proposal/2026-08-05-rq-decision-pack.md`](../phd-proposal/2026-08-05-rq-decision-pack.md)
- [`../phd-proposal/2026-07-29-doctoral-execution-plan.md`](../phd-proposal/2026-07-29-doctoral-execution-plan.md)
- [`../phd-proposal/proposal-v0.1.md`](../phd-proposal/proposal-v0.1.md)
- [`../phd-proposal/legacy-rq-crosswalk.md`](../phd-proposal/legacy-rq-crosswalk.md)
- [`../phd-proposal/iris-requirements-closure-audit.md`](../phd-proposal/iris-requirements-closure-audit.md)
- [`./2026-08-05-supervisor-presentation-checklist.md`](./2026-08-05-supervisor-presentation-checklist.md)

## Recommended research-question set

**Umbrella RQ**

How can reusable human judgment be captured, governed, and reused in agentic AI assessment of domain-specific artifacts and processes to support auditable, reliable, and transferable human–AI co-reasoning?

**SQ1 — Selective intervention**

When and how should an agentic assessment system request human judgment so that important uncertainties are addressed without unnecessary expert burden?

**SQ2 — Governed knowledge reuse**

How should expert judgments be represented, validated, reconciled, and stored so they can be reused transparently without unsafe generalization or loss of human authority?

**SQ3 — Evaluation and transfer**

To what extent does the resulting framework improve assessment quality, consistency, traceability, and expert effort across domains, first in software/modeling and, when governance and access permit, in healthcare?

Two alternate phrasings of the same four conceptual slots are provided in the decision pack. They are wording options, not extra questions.

> **Post-meeting update (2026-08-10):** The umbrella RQ and SQ1–SQ3 wording proposed above was this pre-read's going-in draft for the 2026-08-05 call. During that call, Iris Reinhartz-Berger and Arnon Sturm refined the wording live, in conversation. The refined text was machine-transcribed and is recorded, with full evidence and caveats, in [`2026-08-05-supervisor-meeting.md`](./2026-08-05-supervisor-meeting.md) (see items E5–E10) and the provenance manifest, [`2026-08-05-supervisor-provenance-manifest.md`](./2026-08-05-supervisor-provenance-manifest.md). That source records the following **provisional, working wording** — it is *not* supervisor-approved:
>
> - **U-RQ:** How can human judgment be captured, governed, and used to support agentic-AI-driven variability exploration in guideline operationalization scenarios, enabling reliable human–AI co-reasoning?
> - **SQ1 — Selective intervention:** When and how, in variability exploration scenarios, should an agentic assessment system request human judgment so that important uncertainties are addressed without unnecessary expert burden?
> - **SQ2 — Governed knowledge reuse:** How should expert judgment — including the system's core reasoning — be represented, validated, reconciled, and stored so it can be reused transparently without unsafe generalization or loss of human authority?
> - **SQ3 — Evaluation and transfer:** How can expert judgment be reused and transferred across different guideline-operationalization contexts without unsafe generalization or loss of human authority, first in software/modeling and, when governance and access permit, in healthcare?
>
> Decisions D-RQ-01 (umbrella RQ wording) and D-RQ-02 (SQ1–SQ3 wording) remain **Pending** in [`2026-08-05-rq-decision-pack.md`](../phd-proposal/2026-08-05-rq-decision-pack.md) until Ali verifies this text against his own saved working draft from the call and a supervisor decision is logged. The pre-read text below is left as originally prepared (the pre-call draft) and should not be read as the outcome of the call.

## Three-study map

| Study | Question | Method and output |
| --- | --- | --- |
| Study 1 — Intervention architecture | SQ1 | Design and validate event observation, uncertainty/priority criteria, review dosage, routing, escalation, and burden-aware request mechanisms |
| Study 2 — Judgment lifecycle | SQ2 | Design and validate judgment representation, source validation, reconciliation, provenance, authority, storage, retrieval, and safe-reuse controls |
| Study 3 — Evaluation and transfer | SQ3 | Evaluate the complete framework first in software/modeling, then compare transfer under conditional healthcare Plan A or a second software/modeling Plan B |

Earlier five-question PhD and six-question MediVARIA sets are preserved as hypotheses, measurements, and transfer factors inside these studies rather than being discarded.

## Proposed Plan A and Plan B

- **Plan A:** construct the intervention architecture and judgment lifecycle, evaluate the complete framework first in software/modeling, and extend Study 3 to healthcare only after all six entry gates pass: use-case, people, authorization, ethics/privacy, environment, and protocol.
- **Plan B:** construct the same framework and complete Study 3 through software/modeling plus a second software/modeling dataset, diagram family, task, institution, reviewer panel, or longitudinal setting.

Proposed control: if the medical gates do not have documented owners, evidence paths, and feasible dates by 26 August, write the September proposal with Plan B as the committed path and Plan A as contingent. This date was not approved in the July 29 call.

## Evidence boundary

- Current evidence is from software engineering/modeling.
- The independent-evidence state is 0/2 reviewer returns and 0/24 adjudicated generalization-safe labels.
- Accuracy, macro-F1, effort reduction, generalization, and superiority are not yet computable.
- No medical or clinical-performance result exists.
- MIMIC may support a short data-shape familiarization note; it is not selected as the final dataset.
- MediVARIA is a candidate medical transfer vehicle, not an approved or completed study.
- Restricted medical data must remain in an approved environment and cannot be processed by an online/commercial LLM.

## Decisions requested in this checkpoint

Please record **Confirm**, **Confirm with correction**, **Retire or supersede**,
or **Defer** for each item below. Silence is `Defer`; a rejection without an
approved replacement remains a blocking governance exception and cannot close
the item.

1. the umbrella-RQ wording;
2. SQ1, SQ2, and SQ3;
3. the three-study mapping;
4. Plan A as conditional medical transfer and Plan B as non-medical transfer;
5. the requirement that every question remains answerable under Plan B;
6. the proposed 26 August fallback decision date;
7. the existing evidence-boundary wording;
8. the initial literature-review scope;
9. the documented bounded metadata/schema-only MIMIC boundary, the absence of elapsed-time evidence, and continued prohibition on patient-row inspection; and
10. owners for medical feasibility and university-process verification.

## Immediate next outputs after the decision

| Provisional date | Output |
| --- | --- |
| 12 Aug | Search protocol and first screening pass; Penina outline/reuse map; proposal `v0.2`; Clalit request template |
| 19 Aug | Critical synthesis and gap matrix; resource/RACI and preliminary-results registers; methods, metrics, validity threats, and publication outputs |
| 26 Aug | Proposal `v0.3`; RQ/study architecture freeze; six-gate medical go/no-go and committed September route |
| 2 Sep | Introduction, problem, gap, RQs, and methods internally complete |
| 9 Sep | Preliminary evidence and five-state claim-boundary section complete |
| 16 Sep | Full developed draft `v0.7`, including resources, ethics, risks, and timeline |
| 23 Sep | Supervisor comments resolved; formatting and official process verified |
| 30 Sep | Submission candidate `v1.0`; references and appendices validated |
| 7 Oct | Buffer for final approval, submission, or candidacy-presentation package |

## Open items requiring external confirmation

- shared-folder receipt and permission level;
- exact Clalit/partner use case and next-contact status;
- medical expert availability;
- dataset license, access, privacy, and ethics path;
- approved restricted compute/local model;
- candidacy deadline, reviewer count, nomination, committee, and presentation rules; and
- Penina course dates and reuse expectations.

## Record-quality caveat

This pre-read is grounded in the evidence-linked [`2026-07-29-iris-requirements-register.md`](./2026-07-29-iris-requirements-register.md) and [`2026-07-29-iris-supervisor-action-register.md`](./2026-07-29-iris-supervisor-action-register.md). The underlying bilingual transcript is machine-derived; human bilingual review and full diarization remain pending. No direct quotations are used.
