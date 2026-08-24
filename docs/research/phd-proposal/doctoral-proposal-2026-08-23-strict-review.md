# Doctoral Proposal (2026-08-23 draft) — Strict Reviewer Report

**Reviewed:** `VEGO_AI_Doctoral_Research_Proposal_Enhanced_PhD_Supervisor_Draft_2026-08-23.pdf` — the consolidated 21-page doctoral proposal (Abstract, Introduction, Critical Literature Review, Research Questions and Contributions, Methodology, Preliminary Results, Work Plan, Threats to Validity, References — 57 sources).

**Method:** Full text extraction via `pypdf` (the PDF-page-render tool was unavailable in this environment), then a 7-dimension adversarially-verified review covering citation integrity (13 references checked against real external sources — ACL Anthology, ACM DL, Springer, arXiv, DOI resolution), fulfillment of Iris and Arnon's specific 2026-08-12 instructions, whether this document resolves the issues flagged across the four prior reports in this lineage (v10, v13, v8, v15), evidence-boundary overclaim scanning, internal consistency/production quality, and genuine strengths. I additionally re-examined two findings the automated verify pass had auto-dropped on wording technicalities rather than substance, and restored their corrected versions below rather than silently losing true findings to a pedantic refutation.

## Strict score: 75/100

This is the strongest single document in the entire review lineage, and it is not close — the evidence-boundary discipline and design-science rigor are genuinely excellent. It is not, however, ready to present as-is: one specific deliverable Iris asked for by name has now been missing across four consecutive reviewed artifacts, a real structural violation of her "problem world, not solution world" instruction runs through three subsections, and one previously-tracked data discrepancy has regressed from "flagged as open" to "silently dropped."

| Dimension | Weight | Score | Why |
| --- | --- | --- | --- |
| Evidence-boundary discipline | 25 | 24 | Near-perfect; see section A |
| Citation integrity | 20 | 17 | 12 of 13 checked references confirmed exact; 1 author-initial error; only ~1/3 of the 57-reference bibliography was checked |
| Fulfillment of Iris/Arnon's 08-12 instructions | 20 | 8 | ACL taxonomy exercise still entirely absent (4th time running); solution-world bleed in Ch.2; two-scenario split only generic |
| Resolution of recurring cross-report issues | 15 | 10 | 3 of 5 genuinely resolved; 1 openly disclosed as still-open; 1 regressed (count mismatch dropped, not just left open) |
| Internal consistency / production quality | 10 | 6 | Figure numbering out of reading order; one TOC page-number error |
| Methodological / design-science rigor | 10 | 10 | Genuinely excellent throughout |
| **Total** | **100** | **75** | |

## What was done well (verified strengths)

1. **The "SECTION SUMMARY" device (Established / Research implication) is applied 23 times, consistently, across the entire document** — not just after literature review. It appears after conceptual claims (p.4), literature synthesis (p.8), the proposal's own preliminary results (p.17), and even the work plan (p.19), forcing every subsection to separate "what is known" from "what this means for the design." This is a genuine structural discipline device, not decoration.
2. **The falsifiable-propositions table (§3.4, p.12) gives every proposition an operational rejection condition**, not a restated null hypothesis — e.g. P1: "Any advantage disappears under matched burden, or errors are concentrated in autonomous cases." The section summary immediately below it states outright that null findings "will narrow the thesis claims rather than be treated as implementation defects to conceal."
3. **Source-reported baseline numbers are explicitly and repeatedly flagged as transcribed, not reproduced.** Figure 9's caption states "Values are transcribed from the supplied manuscript [1]. They are source-reported results, not an independent re-analysis or reproduction," and the surrounding text refuses to let a documented baseline weakness pre-validate the thesis's own contribution: "It does not show that the proposed human-judgment layer will improve the result."
4. **The Abstract itself — the most commonly overclaimed part of any proposal — states the non-claims up front**: "Current results are limited to the VEGO-AI baseline and preliminary mechanism or conformance evidence; they do not establish improved accuracy, reduced expert effort, safe transfer, or clinical validity." Most drafts bury this in a limitations section; this one leads with it.
5. **The §5.2 evidence-gating table assigns a distinct "permitted interpretation" per experiment ID**, not one blanket disclaimer — e.g. EXP-013–018 is explicitly "conformance precedent only; no implementation-independence or outcome claim." This is more granular claim discipline than most proposals attempt.
6. **The capability-gap declaration criteria (§2.4, p.8) require a four-part test** (stable failure signature, reproduction in distinct frozen contexts, independent confirmation, ruling out local artifacts) before a recurring failure can be called a transferable limitation — and this is carried through verbatim into the Study 3 outcome measures (p.15), not just asserted once and dropped.
7. **Explicit, non-overlapping research-question ownership** (§3.2, p.11: "SQ1 owns the intervention decision. SQ2 owns the source judgment... SQ3 consumes the governed source record and owns target-context fit...") prevents the same evidence being counted toward more than one contribution.
8. **The risk/mitigation table (§7, p.19) gives concrete, traceable mitigations**, not generic hedges — e.g. the resourcing-risk row's fallback is "report reference-implementation evidence only and narrow the claim," a specific, actionable retreat position rather than a vague reassurance.

## Gaps and defects

### A. Fulfillment of Iris/Arnon's 2026-08-12 instructions (highest-priority, since this is what supervisors will check first)

- **The ACL-2026 GitHub taxonomy branch-classification exercise Iris explicitly asked for is entirely absent — the fourth consecutive reviewed artifact where it's missing.** A full-text search for "branch," "GitHub," and "Awesome" returns zero hits anywhere in the document. "Zou" appears only once in-text (p.6): "A broad 2026 survey organizes human-agent systems around human feedback, interaction, orchestration, communication, environment, and profiling [10]" — a six-category summary of the survey's own taxonomy, not the branch-by-branch relevant/less-relevant/not-relevant/missing classification, using Ali's own RQs as the lens, that Iris asked for as one slide for the next meeting. This is the same gap I flagged in the v10, v13, and v8 reports, and it was only *partially* attempted for the first time in the v15 workbook (which itself fell short — see `literature-package-v15-verification-report.md`). In this proposal it doesn't appear at all, not even partially.
- **The literature review repeatedly crosses from problem-world synthesis into solution-world design detail, contrary to Iris's explicit instruction.** Figures 5, 6, and 7 (§§2.2–2.4, pp.7–9) are each captioned "Author-generated design synthesis" of the author's own proposed Study 1/2/3 artifact, and the surrounding prose states normative design requirements for VEGO-AI's own mechanisms — e.g. p.7: "A review policy must therefore combine uncertainty with consequence, novelty, evidence quality, cross-agent disagreement, expected future value, reviewer competence, and queue conditions"; p.8: "A governed record must therefore distinguish lifecycle status, validation status, and contestation status..." This content substantially duplicates what Chapter 4 §§4.2–4.4 already say about the same three artifacts. The literature chapter should state what the cited work establishes and the residual gap it leaves open — not re-derive the methodology chapter's own design requirements a second time.
- **The two-scenario (software-engineering/medical) split is stated once, generically, and conditionally at the whole-programme level — not per sub-question, as Iris and Arnon jointly directed.** Section 3.2's RQ wording, and each of §§4.2–4.4 (Studies 1–3), contain zero mentions of "medical" or "software engineering" inside those specific sections. The split appears only as a programme-wide caveat (§4.1, p.13: "The software/modeling context is the complete baseline... A medical setting may be added as an external-validity study only after [conditions]... It is not on the critical path") rather than as the explicit "two kinds of guideline scenario" sub-section directed for each study.
- **The organizing principle is much closer to what Iris wanted than any prior artifact, but doesn't say so in her words, and the section-2 structure still mirrors Study 1/2/3 under mechanism-name cover.** Section 2's headings ("2.1 Human-agent collaboration and decision authority," "2.2 Selective intervention under bounded attention," etc.) correctly avoid both HCI framing and VEGO-AI's own component names — a genuine improvement. But §1.3 (p.5) self-describes the review as organized "by problem mechanisms rather than by the names of proposed components," not by Iris's own phrase "human involvement in the context of agentic AI" — and §§2.2/2.3/2.4 map one-to-one onto Study 1/2/3 via the Figure 5/6/7 captions, so the SQ-mirrored shape she asked to avoid is still present, just relabeled.

### B. Regression — a previously-tracked data discrepancy is now silently dropped, not just left open

- **The manuscript-vs-package case-model/pattern count mismatch (178 vs 165 models, 26 vs 27 patterns) is presented as uncontested fact, with no caveat at all.** Section 5.1 (p.16) states flatly: "The supplied VEGO-AI manuscript reports evaluation across two domains, two UML languages, and 178 case models [1]" and "The Variability Explorer produced 26 reported patterns." The only attached caveat is that these are "source-reported results, not an independent re-analysis or reproduction" (Figure 9 caption) — which addresses attribution, not the count discrepancy itself. The v10 report called this an unresolved "reproducibility blocker"; the v13 report found it "still flagged open... but the specific competing numbers... no longer stated." This proposal is a further regression: it doesn't flag the discrepancy as open at all anymore.

### C. Citation integrity and production quality

- **Reference [45] has an incorrect author initial.** The proposal cites "K. E. Ahmed et al." for the MCeT paper (MODELS 2025, pp. 84–95). The actual first author, confirmed via the paper's own arXiv listing (2508.00630), its ORCID record, and its GitHub repository, is "Khaled Ahmed" — no middle initial anywhere in any source found. The paper itself is real and correctly matched on title/venue/pages; only the author-initial is wrong. Every other reference specifically checked in this pass (12 of 13: refs [10], [19], [42], [43], [44], [46], [51], [52], [54], [55], [56], [57]) was confirmed exactly correct against ACL Anthology, ACM DL, Springer, or arXiv — a strong track record, though this covers only about a third of the 57-reference bibliography, and the rest have not been externally checked in this pass.
- **Figures 5, 6, and 7 appear before Figures 3 and 4 in reading order, breaking the ascending sequence a reader expects.** Actual caption order in the document is: Fig 1 (p.4), Fig 2 (p.5), Fig 5 (p.7), Fig 6 (p.8), Fig 7 (p.9), Fig 3 (p.10), Fig 4 (p.13), Fig 8 (p.16), Fig 9 (p.17), Fig 10 (p.18). All 10 figures are captioned exactly once each with no duplicates — the numbering is just out of order, not missing or doubled. This is the kind of defect a supervisor or examiner notices immediately and reads as sloppy, independent of the content being sound.
- **One Table-of-Contents page number is wrong.** The TOC (p.3) lists "1.2 VEGO-AI baseline and motivating example" as starting on page 5; it actually starts on page 4. All other 16 TOC rows were checked line-by-line against the actual section markers and matched correctly.
- **Everything else checked out clean**: all "Page N of 21" footers correctly match their actual page; the P1–P4 propositions map cleanly onto SQ1–SQ3/U-RQ, C1–C4, and §§4.2–4.5 with no cross-wiring or orphaned entries.

### D. Carryforward from the four prior reports — three resolved, one still open (and disclosed), one regressed

| Recurring issue (from v10/v13/v8/v15 + Chapter 4) | Status in this proposal |
| --- | --- |
| SQ2 artifact-count conflict (one artifact per study vs. multiple) | **Resolved in substance.** Table 3.3 gives exactly one primary artifact for C2 ("System-independent governed-judgment contract and executable conformance suite"), matching Chapter 4 §4.4's recommendation. The SQ2/SQ3 boundary (p.11) conceptually matches Chapter 4 §4.7's division — phrased in different words, not verbatim-identical, which is normal paraphrase, not a red flag. |
| EXP-006/007/008 preliminary-results wording | **Resolved.** §5.2's table uses exactly the required framing ("Mechanism and observability evidence only; no expert-effort or quality claim"), consistent with `chapter-5-preliminary-results.md` and the decisions-packet's housekeeping note. EXP-009/EXP-010 are correctly omitted entirely, consistent with the packet's recommendation pending M-04. |
| Plan A/B medical boundary placement | **Resolved and applied consistently** as a conditional appendix throughout (Objective 6, §4.1, §4.5, Semester 5) — though the document never uses the "Plan A/Plan B" terminology itself, describing the same structure in different words. |
| Second Study-2 implementer and two Study-3 raters, still unnamed | **Still open, and correctly disclosed as an open risk rather than concealed** — §7's risk table explicitly names "Insufficient independent reviewers or implementers" with a stated fallback, and §6's Semester 3 plan states "recruit independent implementer and reviewers" as a future action. This matches `study-resourcing-request-template.md`'s framing of the same gap. |
| Manuscript-vs-package count mismatch (178 vs 165, 26 vs 27) | **Regressed** — see section B above. |

## Add / modify / change / delete

**Add**

- The ACL-2026 GitHub taxonomy branch-classification exercise and its one slide — this is the single highest-priority missing item, both because it's the most concrete unmet instruction and because it's now missing from four consecutive reviewed artifacts.
- An explicit two-scenario (software-engineering/medical) sub-section under §3.2, and a repeated, explicit statement of the split within each of §§4.2–4.4, rather than one generic programme-level mention.
- The specific competing counts (178 vs 165 case models; 26 vs 27 patterns) back into §5.1, with the same kind of open-item caveat already used elsewhere in this same document (e.g. the §5.2 evidence-gating table).

**Modify**

- Reword §1.3's self-description of the organizing principle to explicitly use Iris's own phrase ("human involvement in the context of agentic AI") rather than "problem mechanisms," so a supervisor skimming the chapter can map it directly back to her 08-12 directive.
- Correct reference [45]'s author initial from "K. E. Ahmed" to "K. Ahmed."
- Correct the Table of Contents page number for §1.2 (page 5 → page 4).

**Change**

- Renumber Figures 3–10 into actual reading order, or physically relocate the Study 1/2/3 design-synthesis figures so the existing numbers 5/6/7 don't precede 3/4.
- Move the "design synthesis" figures (5, 6, 7) and their associated normative "must" design-requirement sentences out of Chapter 2 into Chapter 4, where the same content is already stated — confining Chapter 2 to what the literature establishes and the residual gap, per Iris's explicit problem-world instruction.

**Delete / reconcile**

- Nothing in this document needs outright deletion beyond relocating the Ch.2 solution-world content described above. The one thing to actively *not* do is let the 178/26 baseline numbers stand uncaveated in any further revision — that's an active regression, not a pre-existing gap being carried forward.

## Bottom line

This is a genuinely strong proposal — the evidence-boundary discipline and design-science rigor are the best they have been across this entire review lineage, and three of five previously-recurring cross-report conflicts are now actually resolved rather than just relabeled. But a strict review has to weigh what a supervisor will notice first: the one specific, named, already-explained deliverable Iris asked for on 08-12 is still not here after four tries, the literature chapter still argues its own proposed solution inside what's supposed to be problem-world framing, and a data discrepancy that survived two prior rounds as an open caveat has now quietly disappeared rather than being resolved. None of these three requires new research — the taxonomy exercise is a bounded, already-scoped task; the solution-world content just needs to move to Chapter 4, where its twin already lives; and the count discrepancy needs one sentence restored, not new investigation. Fix those three and the figure-numbering/TOC/citation nits, and this document is close to supervisor-ready.
