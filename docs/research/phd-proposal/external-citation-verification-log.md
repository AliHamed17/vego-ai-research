# External Citation Verification Log

Running record of literature/source citations checked directly against an external authority (a
DOI resolver, a publisher page, an official conference program, ACL Anthology, arXiv) rather than
taken on the word of any workbook, docx, or prior review. Distinct from
`external-fact-register.md`, which tracks institutional/administrative claims from supervisor
calls, not literature citations. Each entry states exactly what was checked, the method, and the
result — no citation here is marked verified without an actual fetch/search having happened.

## VEGO-AI foundation paper

**Reinhartz-Berger, Bragilovski & Sturm — "Not All Differences Matter: Variability Exploration of
Domain Models via Agentic AI" (MODELS 2026).** Checked 2026-08-20 via `WebFetch` against the
official MODELS 2026 Research Papers track page
(`conf.researchr.org/track/models-2026/models-2026-research-papers`). Result: the paper appears in
the actual accepted-papers listing, exact title and author order confirmed, marked as part of the
Foundations Track. No individual paper page, abstract, or session date is published yet. Separately,
the DOI that has circulated across workbooks (`10.1145/3822455.3830312`) returns a real HTTP 404 —
consistent with a paper that is accepted/program-listed but not yet assigned a final ACM DOI ahead
of the conference. Conclusion: the paper is real and accepted; treat as "accepted, program-listed,
DOI not yet live" — exactly the cautious framing already used in
`literature-review-v13-workbook-verification-report.md` — not as a confirmed final citation.

Fervers et al. — two distinct real papers, not one citation with a wrong year. Checked 2026-08-20
via direct DOI resolution. This corrects an error in
`literature-package-v15-verification-report.md`'s first draft (see that file's own correction note).

- Fervers et al. (2006), "Adaptation of clinical guidelines: literature review and proposition for
  a framework and procedure," International Journal for Quality in Health Care 18(3):167-176, DOI
  `10.1093/intqhc/mzi108`. Confirmed via publisher metadata fetch — title, authors, journal, volume,
  pages all match exactly.
- Fervers et al. / ADAPTE Collaboration (2010/2011), "Guideline adaptation: an approach to enhance
  efficiency in guideline development and improve utilisation," BMJ Quality & Safety 20(3):228-236,
  DOI `10.1136/bmjqs.2010.043257`. Confirmed via web search (direct fetch was blocked, HTTP 403) —
  title, authors, journal, volume, pages all match.

Conclusion: both are real, correctly citable papers on related but distinct topics. Any workbook
citing "Fervers et al. (2006)" with the IJQHC title/DOI above is citing correctly — this is not a
defect.

ACL-2026 human-agent taxonomy repository —
`github.com/HenryPengZou/Awesome-Human-Agent-Collaboration-Interaction-Systems`, the exact URL Iris
pasted in the 2026-08-12 Zoom chat. Checked 2026-08-20 via `gh api repos/.../readme`. The repo's own
Table of Contents has exactly one "Taxonomy" section with 4 branches: Human Feedback, Interaction,
Orchestration, Communication — each tied to a specific section of the underlying survey paper
(arXiv 2505.00753, accepted ACL 2026). Full detail and the resulting comparison against
`ACL_Branch_Map_v15.csv`'s 7 branches is in `literature-package-v15-verification-report.md`,
section E.

2026 agent-memory papers flagged in the v13 workbook review as highest-maturity sources never
cited in synthesis. All four checked 2026-08-20 via `WebSearch`. All four are real, with
exact-matching titles, authors, and venues — the v13 finding that they were never actually cited
in that review's synthesis text stands, but none of the four is a fabricated or unfindable source.

| Source | Title | Venue | Identifier |
| --- | --- | --- | --- |
| APEX-MEM | Agentic Semi-Structured Memory with Temporal Reasoning for Long-Term Conversational AI | ACL 2026 (Long Papers), pp. 16470-16489 | arXiv:2604.14362 |
| MemORAI | Memory Organization and Retrieval via Adaptive Graph Intelligence for LLM Conversational Agents | arXiv preprint, 2026-05-02 | arXiv:2605.01386 |
| PerMemSafe | Benchmarking Implicit Personalized Safety of Long Horizon Self-Evolving Agents (authors: Hengyu An, Minxi Li, Naen Xu, Chunyi Zhou, Xiaogang Xu, Tianyu Du, Jinbao Li, Shouling Ji) | ACL 2026 Findings | (not captured) |
| TiMem | Temporal-Hierarchical Memory Consolidation for Long-Horizon Conversational Agents (authors incl. Kai Li et al.) | ACL 2026 Findings | arXiv:2601.02845 |

Two 2026 papers flagged in the earlier v8 workbook report as "plausible but unverified." Checked
2026-08-20 via `WebSearch`. Both confirmed real, exact metadata match; superseding the "unverified,
cannot confirm from this review alone" caveat in
`literature-workbook-v8-rq-only-verification-report.md`.

- Dhanorkar, Passi & Vorvoreanu, "Human Oversight of Agentic Systems in Practice: Examining the
  Oversight Work, Challenges, and Heuristics of Developers Using Software Agents," FAccT '26,
  pp. 6438-6465, DOI `10.1145/3805689.3812402`, also arXiv:2606.05391.
- Dong et al., "Value of Information: A Framework for Human-Agent Communication," ACL 2026
  (Long Papers), pp. 42879-42896, arXiv:2601.06407.

How to extend this log: add a new dated section per verification pass. State the method used (DOI
resolve, `gh api`, `WebSearch`, `WebFetch`) so a reader can judge how strong the confirmation is —
a bare web search summary is weaker evidence than a direct DOI resolve or an official program-page
fetch. Never mark something confirmed here without the actual fetch/search having happened in that
session.

## Reference [1] — the VEGO-AI foundation manuscript, verified against the source (2026-08-25)

The foundation manuscript was supplied directly by Ali on 2026-08-25 as
`Variability_MAS4MODELS2026_Mar28_IRB2<...>.pdf` (10 pages, anonymized MODELS 2026 submission
version; author block carries placeholder "FirstName Surname" entries as expected for double-blind
review). Title confirmed exactly: "Not All Differences Matter: Variability Exploration of Domain
Models via Agentic AI". This is the one reference in the proposal that had never been externally
verifiable, because it is unpublished and its circulated DOI 404s. It is now verified against the
primary source itself, which is stronger evidence than any index could give.

All four agent names used throughout the doctoral proposal are confirmed present in the manuscript:
Language Advisor (13 mentions), Domain Advisor (18), Model Inspector (16), Variability Explorer (10).

### The 178 / 26 counts are correct, which half-resolves a long-standing open item

The manuscript's Table 1 (Evaluation Settings) gives case models per setting:

| Code | Domain | Language | Case models |
| --- | --- | --- | --- |
| ch-ucd | Cheers | UCD | 46 |
| ch-cd | Cheers | CD | 47 |
| pw-ucd | ParkWise | UCD | 44 |
| pw-cd | ParkWise | CD | 41 |

46 + 47 + 44 + 41 = **178**. The number "178" is never printed as a single figure in the manuscript;
it is the sum of Table 1, which is why earlier reviews could not confirm it by text search. A search
for the literal strings "178" and "165" returns zero hits in the manuscript.

On patterns, the manuscript states verbatim: "The Variability Explorer yielded **26** variability
patterns across the four settings... **Eight** of the 26 patterns were classified as substantial
variability, all of which were flagged for guidelines update, and **18** as occasional variability."
8 + 18 = 26.

**Consequence for the open count discrepancy.** The proposal's §4.1 figures (178 case models; 26
patterns, eight substantial and eighteen occasional) are correct against the source. The competing
"165 case models and 27 patterns" attributed to the companion evidence package is therefore the side
that requires explanation — it is either counting a filtered subset, a different snapshot, or is
wrong. The reconciliation task is no longer "which figure is right" but "what is the evidence
package counting". This does not close the item, because the implementation snapshot still has not
been supplied, but it removes the manuscript from suspicion.

### Phase C expert-review figures are also correct

The manuscript reports: "A sample of **16** Model Inspector outcomes (**4 per setting**) was reviewed
by **two experts**"; compliance-vector averages "consistently high across all four settings
(0.80-0.96)"; uncovered-audit averages "lower and more variable (0.55-0.88)". Table 3 gives ch-ucd
0.80/0.55, ch-cd 0.96/0.81, pw-ucd 0.83/0.55, pw-cd 0.92/0.88 — so both use-case-diagram settings do
score 0.55 on uncovered audits, exactly as the proposal states. The proposal discloses the 16-outcome
sample and the four-per-setting split, and its Figure 9 caption correctly notes that no dispersion is
reported in the source.

One detail the proposal omits: the manuscript says the review was performed by **two** experts. The
proposal says only "expert review". Two raters with no reported inter-rater statistic is a real
limitation of the source and is worth one clause, particularly since the doctoral work proposes to
strengthen exactly this kind of judgment evidence.

### The doctorate's motivating premise is supported by the source

The proposal asserts the baseline "is weakest on open-world interpretation of uncovered fragments".
This is borne out: uncovered-fragment audits (0.55-0.88) score lower and more variably than
compliance vectors (0.80-0.96), and the manuscript itself attributes this to "the greater
interpretive effort required". The manuscript's own declared scope limits are "two domains from a
single institution, one LLM, and two modeling languages", which is consistent with how the proposal
characterizes the baseline's boundaries.
