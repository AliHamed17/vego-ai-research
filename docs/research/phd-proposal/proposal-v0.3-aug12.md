# PhD Research Proposal — Working Draft v0.3

**Status: WORKING DRAFT — NOT SUPERVISOR-APPROVED, NOT A SUBMISSION CANDIDATE.**
Prepared by Ali Hamed for the supervisor meeting of Wednesday 2026-08-12, 09:00.
Supervisors: Prof. Iris Reinhartz-Berger, Prof. Arnon.

This is the Word proposal document requested on 2026-08-05 (`E15`/`A08-06`). It is maintained
separately from the tracking document, as instructed. v0.3 delivers **Chapter 3 in full** — the
deliverable due at this meeting — and holds the remaining chapters at the status each has actually
reached. Nothing is presented as further along than it is.

---

## Title — decision required

The v0.2 title is **"Reusable Human Judgment for Auditable, Reliable, and Transferable Agentic AI
Assessment."** Three of its words — *reusable*, *auditable*, *transferable* — are precisely the words
the 2026-08-05 live edit removed from the research-question headline (`E5`: reuse belongs in a
sub-question; `E7`: lean toward dropping "auditable"/"transferable"/"end-to-end"). The §3 wording now
complies; **the title does not**. Leaving it is a visible inconsistency in a submitted proposal.

Three candidates, aligned to the current headline wording, for the supervisors to choose or replace:

| # | Candidate title | Rationale |
| --- | --- | --- |
| T1 | *Human Judgment in Agentic-AI Variability Exploration: Capture, Governance, and Reliable Co-Reasoning* | Mirrors the U-RQ almost verbatim; carries "reliable" (retained per `E7`) and drops all three removed words |
| T2 | *Reliable Human–AI Co-Reasoning for Variability Exploration in Guideline Operationalization* | Leads with the outcome; keeps the domain-neutral framing required by `E13` |
| T3 | *From One-Off Correction to Governed Judgment: Human Expertise in Agentic AI Assessment* | Leads with the gap (§3.3) rather than the artefact; strongest "open question" framing per `E4` |

**Decision `D-TITLE-01` — owner: supervisors, at the 2026-08-12 meeting.** Until it is logged, the
v0.2 title stands unchanged in the record.

---

## Chapter plan and current status

Structure per the confirmed chapter skeleton (`E13`, machine-derived record, pending confirmation):

| # | Chapter | Status at 2026-08-12 | Note |
| --- | --- | --- | --- |
| 1 | Introduction | **Not started — deliberately** | `E13` places it last; written once the questions are signed off |
| 2 | Literature Survey | **Not started — deliberately** | `E15`: *think about it, do not start it*. Four structural options prepared; searches `QL-01`–`QL-05` frozen and not run |
| **3** | **Gap and Research Questions** | **COMPLETE — this deliverable** | Full text below. Wording provisional pending `A08-01` / `D-RQ-01` / `D-RQ-02` |
| 4 | Research Methodology | **Not started — deliberately** | Design Science per Prof. Penina's course; per-RQ study/artifact/design/evaluation. Nine artifact options prepared, none selected |
| 5 | Preliminary Results | Partially available | Software/modelling only; mechanism and readiness evidence. Medical = infrastructure only |
| 6 | Plan | **Not started** | `E14`: ~3-month semester-aligned blocks over a **3-year** horizon; never month-by-month |

**What "not started" means here:** it is compliance with an instruction, not slippage. Iris asked for
§2 and §4 to be *thought about* and not begun; the thinking is delivered as a separate options note.

---

## Chapter 3 — Gap and Research Questions

> The complete chapter follows as a separate document in this package
> (`02 - Chapter 3 - Gap and Research Questions`), and is incorporated here by reference so the two
> never drift. Summary of what it argues:

**§3.1** frames the interpretive step: once a system detects that an artefact deviates from a norm,
something must decide what the deviation *means* — legitimate alternative, error, domain convention,
guideline defect, or genuine ambiguity. This is where automation is weakest and expertise most
expensive.

**§3.2** positions four bodies of work and states, for each, what it establishes and what it leaves
open: automated model assessment (detects deviation, does not interpret it); LLM and agentic
modelling assistance (documents *that* expert correction is needed, not *when* to request it or
*what* to keep); human-in-the-loop and oversight research (supplies mechanisms and governance
expectations, not a selection policy for agentic assessment under an attention budget); and
variability engineering (formalises *designed* variability, not *observed interpretive* variability).
It also defines both constructs — "variability" in this thesis's sense, and "guideline
operationalization" — against the established literature.

**§3.3** states the gap: the design knowledge for connecting selective expert intervention,
structured judgment capture, and scope-aware reuse does not exist in tested, generalizable form,
and neither does an evaluation approach able to say which parts of such a lifecycle transfer. It
argues why expert assessment judgment resists both mature capture paradigms — it is case-grounded,
scoped, contestable, and authority-bearing — and it explicitly does **not** presuppose that reusable
judgment improves assessment.

**§3.4–§3.7** give the main question and SQ1–SQ3, each with an argument for why it is open, an
evaluation criterion built into the question itself, and the wording decisions still outstanding.

**§3.8–§3.11** compose the three questions into one programme, position VEGO-AI as motivating case
rather than object of study, bound the scope, and state the evidence status plainly, including what
a negative result would mean for each question.

---

## Chapter 5 — Preliminary Results (status only)

Reported here as *status*, not as results, because the chapter is not written:

| Element | State |
| --- | --- |
| Software/modelling offline evidence | Mechanism, architecture and readiness evidence from the offline replay series; no effectiveness claim |
| Independent expert labels (EXP-005) | **0 of 24** generalization-safe labels supplied; ≥20 required for any quantitative claim |
| Medical instantiation | Infrastructure and feasibility only; **0 of 6** entry gates pass |
| Accuracy / generalization / clinical performance / effort reduction | **No claim made or supported** |

Which preliminary results may appear in the proposal — and under what label — is an open question for
the supervisors (see the thinking note, Part 3).

---

## Standing evidence boundary

Unchanged by anything in this version:

- No accuracy, generalization, clinical-performance or effort-reduction claim appears anywhere in
  this proposal, and none may until the label and gate counts change.
- The literature searches are protocol-ready and **not executed**; no novelty or review-completeness
  statement is made.
- The research-question wording is **provisional** pending `A08-01` verification and logged
  `D-RQ-01`/`D-RQ-02` decisions.
- The 2026-08-05 meeting record is machine-derived with inferred speakers and is pending participant
  confirmation; every reference to it carries its `E`-identifier so it can be checked in one step.

---

*v0.3 supersedes v0.2 for Chapter 3 only; all other v0.2 content and the v0.1 baseline remain in the
record. Version history and rationale are preserved in the decision and change log.*
