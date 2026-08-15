# Literature Review — Structure and Query Draft (AI first pass, per Iris's live request)

**Status: AI-generated first draft. Not approved by Ali, Iris, or Arnon. Nothing here overrides
`literature-search-execution-register.md`'s frozen QL-01–QL-05 protocol — it responds to that
register and to the 2026-08-12 call, it does not replace either.**

## Why this document exists

During the 2026-08-12 call, Iris asked, live, for the research questions to be given to an AI
assistant with two requests (`F5` in
[`2026-08-12-supervisor-meeting.md`](../meetings/2026-08-12-supervisor-meeting.md)): (a) suggest how
to divide the literature-review section into subsections based on the research questions, and (b)
suggest a Google Scholar query for each subsection. Later in the same call (`F10`) she added a
structural correction: Chapter 2 must build the reader's understanding progressively toward Chapter
3's gap, in the order the reader actually encounters the document — so it should **not** simply be
three subsections that mirror SQ1/SQ2/SQ3, because the reader does not have the research questions
yet at that point. This document answers (a) and (b) literally, then reconciles them against (b), per
`A0812-02`/`A0812-03`.

## 0. The research questions this maps against

From the current Chapter 3 draft (canonical wording, itself still provisional pending
`D-RQ-01`/`D-RQ-02`):

> **U-RQ.** How can human judgment be captured, governed, and used to support agentic-AI-driven
> variability exploration in guideline operationalization scenarios, enabling reliable human–AI
> co-reasoning?

> **SQ1.** When and how, in variability exploration scenarios, should an agentic assessment system
> request human judgment so that important uncertainties are addressed without unnecessary expert
> burden?

> **SQ2.** How should expert judgment — including the system's core reasoning — be represented,
> validated, reconciled, and stored so it can be reused transparently without unsafe generalization or
> loss of human authority?

> **SQ3.** How can expert judgment be reused and transferred across different
> guideline-operationalization contexts without unsafe generalization or loss of human authority,
> first in software/modeling and, when governance and access permit, in healthcare?

## 1. What already exists — do not rebuild this from zero

`literature-search-execution-register.md` already freezes five queries, each with an explicit RQ
mapping, targeting ACM/IEEE/Scopus/Web of Science/PubMed:

| Query | Frozen concept | Existing RQ mapping |
| --- | --- | --- |
| `QL-01` | Agentic/multi-agent AI with human oversight | SQ1, Study 1 |
| `QL-02` | Expert feedback, knowledge capture, memory, reusable judgment | SQ2, Study 2 |
| `QL-03` | Domain modeling, assessment, variability, conformance | General/software baseline, all three studies |
| `QL-04` | Intervention workload, governance, trust, evaluation | SQ1 and SQ3 |
| `QL-05` | Clinical guidelines, CDSS overrides, alert fatigue, process mining | Conditional Plan A (medical) only |

This is **already** a per-RQ query set. Iris's request on the call largely already has an answer; what
is missing is (i) a Google-Scholar-usable phrasing (the frozen queries are written for databases that
support full nested Boolean, which Scholar's basic search handles unreliably), and (ii) explicit
literature-*chapter* subsections built from these five concepts rather than from the RQs directly.
Sections 2–3 below build both, without touching the frozen register itself.

## 2. Literal answer to Iris's request — RQ-based subsection draft

If subsections mirror the research questions directly, as literally requested:

| # | Subsection | Primary RQ | Google Scholar query (draft) |
| --- | --- | --- | --- |
| L1 | Agentic AI and multi-agent systems with human oversight | U-RQ (foundation for all) | `"agentic AI" OR "AI agent" OR "AI agents" "human oversight" OR "human-in-the-loop" OR "human intervention"` |
| L2 | Selective/triggered human intervention policies | SQ1 | `"human-in-the-loop" OR "human intervention" "when to" OR trigger OR policy uncertainty burden workload` |
| L3 | Capturing, validating, and reusing expert/human judgment | SQ2 | `"expert feedback" OR "human judgment" "knowledge reuse" OR "judgment reuse" OR memory OR provenance` |
| L4 | Variability, domain modeling, and guideline operationalization | U-RQ / software substrate | `"variability model" OR "domain model" OR "conceptual model" assessment OR conformance AI OR agent` |
| L5 | Cross-domain transfer and generalization of human-in-the-loop mechanisms | SQ3 | `"human-in-the-loop" OR "human oversight" transfer OR generalization OR "cross-domain" evaluation` |
| L6 | Clinical guideline variability and CDSS override behavior (Plan A only) | SQ3, conditional | `"clinical decision support" OR CDSS "override" OR "alert fatigue" OR "human oversight"` |

Direct correspondence to the frozen register: L1↔`QL-01`, L2↔`QL-01`+`QL-04`, L3↔`QL-02`, L4↔`QL-03`,
L5↔`QL-04`, L6↔`QL-05`. These Scholar queries are Scholar-safe simplifications of the same frozen
concepts — they narrow the quoted-phrase groups and drop the third-level `AND` clause Scholar tends to
over-restrict on, they are not new concepts.

## 3. Corrected answer — conventional literature-review structure (per `F10`)

Per Iris's later correction, the *written chapter* should read as a conventional literature survey that
builds toward the gap, not as three RQ-labelled boxes. The one paper the three of you reviewed live on
the call (the ACL 2026 Findings submission and its associated GitHub taxonomy of human-agent
collaboration literature — see `F9`/`F11`) is itself a reasonable structural model, since its own
top-level division (reconstructed from the call as approximately: foundations, elicitation,
presentation/validation, cross-context reuse, synthesis/gaps) already separates "what agentic systems
are" from "how humans intervene" from "how that transfers" — which is close to what a from-scratch
systematic-review structure would look like here regardless of which paper it started from.

Recommended chapter structure:

| § | Title | Feeds primarily | Built from |
| --- | --- | --- | --- |
| 2.1 | Foundations: agentic AI, autonomous agents, LLM agents | U-RQ | `QL-01` |
| 2.2 | Human involvement in agentic-AI systems: feedback types and interaction patterns | U-RQ, SQ1 | `QL-01`, `QL-04`, taxonomy paper |
| 2.3 | Capturing and governing human/expert judgment for reuse | SQ2 | `QL-02` |
| 2.4 | Variability and guideline operationalization as the problem substrate | U-RQ (motivates the gap, not the solution) | `QL-03` |
| 2.5 | Transfer and generalization across domains | SQ3 | `QL-04`, `QL-05` (conditional) |
| 2.6 | Synthesis: what is covered, what is not — leading into Chapter 3's gap | all | cross-cutting |

The RQ-tagging column already in the per-RQ literature spreadsheet (`A08-03`) stays exactly as-is as an
internal tracking tool — every source keeps its RQ1/RQ2/RQ3/general tag for traceability — but the
**chapter text itself** should follow §2.1–2.6 above, not the RQ order. This is the concrete reconciliation
`A0812-03` asks for: keep the tags, change the chapter's table of contents.

## 4. The one item this document cannot settle — `F9`'s live-drafted query

On the call, Iris and Arnon live-edited a candidate Google Scholar Boolean query for a "Foundations"
subsection while reviewing the ACL-2026 paper, converging on something built from Agentic AI /
Autonomous Agent / LLM Agent, Human-AI Collaboration / Interaction, and Variability / Variant, while
explicitly dropping "guideline," bare "decision making," and "exploration." The ASR fragments that
exchange into single-word segments (`00:28:40`–`00:36:15`) and **cannot reliably reconstruct the final
string** — reconstructing it here would risk inventing a query and attributing it to Iris and Arnon.

Best-effort reconstruction, explicitly unverified:

```text
("agentic AI" OR "autonomous agent" OR "LLM agent") AND ("human-AI collaboration" OR "human-AI interaction") AND (variability OR variant)
```

This is close in concept to `QL-01`, just narrower. **Action for Ali (`A0812-06`):** confirm this against
memory or by re-listening to `00:28:40`–`00:36:15`, then decide whether it becomes a new `QL-06` in the
frozen register or is folded into `QL-01` as a refinement — either way, it goes through the same
freeze-before-run discipline as `QL-01`–`QL-05`, not an ad hoc search.

## 5. What this document does not do

It does not run any search, does not add a row to the frozen execution register, and does not change
the review-completeness status (**PROTOCOL READY / NOT RUN** stands, for `QL-01`–`QL-05` and for any
query drafted here). It is a drafting aid for Ali's next-week task (`A0812-04`), not evidence of
coverage.
