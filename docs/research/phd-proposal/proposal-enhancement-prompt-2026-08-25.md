# Enhancement Prompt — VEGO-AI Doctoral Proposal, next revision

Paste the block below into a fresh session that has the proposal source open. It is self-contained:
it quotes every current string to be changed and gives the exact replacement, so the session does not
need this conversation's context.

Source of truth for the findings: `docs/research/phd-proposal/doctoral-proposal-2026-08-25-rev2-review.md`
(score 91/100). The document being edited is the 30-page revision
`VEGO_AI_Doctoral_Proposal_Revised_20260825 (1).pdf`.

## Prompt

```text
You are revising the VEGO-AI doctoral research proposal (30 pages, dated 25 August 2026). A strict
review scored it 91/100 and found six items to fix. Apply them exactly and change nothing else.

FIRST: find the authoritative editable source. This proposal exists in the Downloads folder only as
a PDF; there is no editable source tracked in the repository. Do not edit the PDF as if it were the
source and do not invent a new authoring pipeline. If you cannot locate the editable original, stop
and ask Ali where it lives before making any content change.

HARD RULES, in priority order.

1. Do not weaken the evidence boundary. The following must remain true and stated: EXP-005
   generalization-safe expert labels are incomplete, so accuracy, generalization and
   integrated-benefit claims stay blocked; zero of six medical entry gates are satisfied; no
   literature search has been executed; independent reviewers, raters and an independent implementer
   are not recruited; supervisor approval of the research-question wording is not recorded; the
   178/26 versus 165/27 count discrepancy is unresolved. Never add an accuracy, generalization,
   expert-effort, transfer-safety or clinical claim.

2. DO NOT OVER-CORRECT. This is the single most important instruction. The previous revision
   introduced three factual errors purely by making its own work sound weaker than it is. Fixes 1-3
   below all consist of restoring accuracy, not of adding caution. If you find yourself writing a
   new hedge that is not requested here, stop.

3. Change only what is listed. Every integrity property currently holds and must survive: 62
   references numbered 1-62 with no gaps, every in-text citation resolving to an entry, no entry
   uncited, Figures 1-11 and Tables 1-16 in ascending order, every table-of-contents page number
   correct, and no dangling section cross-reference. Re-check all of these after editing.

4. Do not fabricate. If a fix needs a fact you cannot verify in the repository or from a publisher
   record, leave the current text and report what you could not confirm.
```
```text
FIX 1 (factual, three locations) — the protocol IS frozen; the document wrongly says it is not.

Current text, in §4.2 and again in Appendix B Table 16:
  "The database-specific Boolean syntax has not been written, so the protocol is not yet frozen and
   no query has been executed."

This contradicts the project's own controlled document,
docs/research/phd-proposal/literature-search-execution-register.md, which states "This register
freezes the first five literature-query concepts before execution", heads its §2 "Exact frozen
protocol queries", and states "The text in each code block is the exact canonical Boolean
expression." The canonical syntax is written and registered, and the QL-05 PubMed query is already
in platform syntax. What genuinely remains is per-platform field-wrapper translation, which the
register itself treats as an execution-time step.

Replace with:
  "The five query families and their canonical Boolean expressions are frozen and registered; the
   per-platform field wrappers and filters are recorded at execution. No query has been executed."

Keep the following sentence exactly as it stands — it is correct and load-bearing:
  "There are therefore no screening counts, no inclusion counts, ... and none will be reported until
   the searches are run."


FIX 2 (factual, three locations) — "per-family date bounds" is wrong.

The phrase "per-family date bounds" appears in the §3.2 section summary, in §4.2, and in Appendix B
Table 16. The register applies a SINGLE primary window, 2015-2026, across all five query families,
with a documented backward/forward snowballing exception for older seminal work. There are no
per-family bounds.

In all three places replace "per-family date bounds" with:
  "a single 2015-2026 window with a documented snowballing exception"


FIX 3 (factual, one location) — the experiment register is described as holding more than it does.

Current text, §4.3:
  "The identifiers below are entries in the project's internal experiment register, a controlled
   document that records for each run its inputs, frozen versions, procedure, and outputs."

The actual artifact, experiments/registry.md, is a seven-column table: ID, Title, Status, RQ,
Code/Config, Outputs, Notes. There is no procedure column, no run-date column, and no per-run
version or commit field. Version state appears only as a single global hash in the file header.

Replace with:
  "The identifiers below are entries in the project's internal experiment register, which records
   for each registered experiment its identifier, status, research question, code and configuration
   paths, the location of any generated outputs, and the interpretation attached to it."

Keep the rest of that paragraph unchanged, including "The register is not reproduced here and the
entries are not independently auditable from this document" — that disclosure is correct and should
stay.
```
```text
FIX 4 (substantive — the most important one) — the central gap claim has a tautological conjunct.

The gap currently rests, in both the Abstract and §1.8, on a negative existential over a three-part
conjunction. Current wording:
  "None of the reviewed formulations assumes a claim about a model fragment whose interpretation is
   contested, whose reviewer must be selected for competence and authority, and whose resolution may
   or may not legitimately affect a later and differently situated case."

Two defects. The three conjuncts are the proposal's own design commitments stated in the proposal's
own vocabulary, so a conjunction of them is close to unfalsifiable by construction — no prior work
was attempting to satisfy that specific triple. And "may or may not" is a tautology: every
resolution either does or does not affect a later case, so the conjunct excludes nothing and cannot
discriminate prior work. This is the load-bearing sentence of the whole proposal and the one a
committee member will press hardest.

Rewrite so that ONE conjunct carries the deficit and a falsifier is stated. Use this shape:
  "The specific deficit is reviewer selection: no formulation in the literature reviewed here makes
   the choice of reviewer a function of assessed competence and authority over the contested
   fragment. A single study that did so would refute this claim."

You may choose a different conjunct if you can argue it better, but the result must (a) name exactly
one deficit, (b) drop "may or may not" entirely, and (c) state what evidence would refute it. Keep
the existing caveat that already follows — "Because the formal searches described in §3.2 have not
been run, this is a statement about the literature reviewed here and not a proof that no such
evidence exists" — it is correct and must survive. Make the Abstract and §1.8 consistent with each
other after the rewrite.


FIX 5 (wording, Appendix A preamble) — the prototype dependency is denied while being relied on.

The preamble disclaims the exploratory prototype three times, yet one sentence earlier that same
prototype is the sole reason "part of every first-pass verdict" changed. Every verdict in Appendix A
is therefore conditional on an artifact the text says is not evidence. Also, "the corrected verdicts"
presumes the second pass was right.

Change "and the corrected verdicts are the ones given here" to:
  "and the second-pass verdicts are the ones given here; they are conditional on that prototype."

Keep all three existing disclaimers ("not part of the reported VEGO-AI baseline", "not one of the
three primary artifacts", "not evaluated evidence"). Add one sentence noting that the classification
is single-rater and its reliability has not been assessed.


FIX 6 (two small wording items).

a) "The reference audit" is relied on twice — in the References preamble and in Appendix B Table 16
   — but is neither included nor identified, so a reader cannot obtain it. This is the same kind of
   dangling pointer as the "the reference proposal" clause removed in the last revision. Either
   attach it as Appendix C and add it to the table of contents, or name it explicitly as a companion
   file with its filename.

b) In §4.2, "no corpus size to report" reads more absolutely than intended. It conceals nothing, as
   the next sentence discloses the 62-reference anchor set, but scope it anyway: change to
   "no protocol-derived corpus size".
```
```text
DO NOT CHANGE — each of these was verified correct and a "fix" would introduce an error.

- Reference [4] Hevner et al., "pp. 75-106". A reviewer alleged this should be 75-105; the
  allegation was checked and refuted. The publisher's typeset PDF footer does read 75-105, but
  Crossref's publisher-deposited record and OpenAlex both give 75-106, the printed DOI resolves to a
  landing page carrying 75-106, and the issue table of contents allocates 75-106 to this article with
  the next starting at 107. Both forms circulate legitimately. Leave it.
- Reference [18] Ahmed's middle initial, "K. E. Ahmed". DBLP's canonical form is "Khaled E. Ahmed".
  An earlier review round wrongly asked for "K. Ahmed"; that correction was withdrawn. Leave it.
- The "61 of 62 cited references verified ... Reference [1] is unpublished" formulation. It is
  precise and correct.
- The British-to-American spelling conversion. It did not corrupt any reference title; [13] Fervers
  correctly retains "Utilisation" because that is the published form. Do not re-run any global
  spelling replacement over the reference list.
- The section-summary device and its six chapter-appropriate label pairs (Established / Research
  implication; Decision / Consequence; Design choice / Evaluation consequence; Evidence to date /
  What it does not establish; Dependency / Planning implication; Risk / Decision rule). This is a
  deliberate scheme, not drift.
- Every statement of an open gate, an unrecruited participant, an unexecuted search, or an
  unresolved count discrepancy.


STILL OPEN, and NOT part of this revision unless Ali asks for it.

The ACL-2026 exercise Iris assigned has a remaining half: screening the survey's own corpus — the
roughly ninety papers classified under the four branches — against the research questions with the
four-way relevant / less relevant / not relevant / missing disposition, and reporting the counts.
The branch-level and dimension-level classification is done and is in Appendix A; Figure 11 carries
the slide content. The corpus screening is correctly disclosed as outstanding in three places, so
the document is honest as it stands. Do not silently mark it done, and do not report corpus counts
that do not exist.


SELF-VERIFICATION — run these before declaring the revision finished, and report each result.

1. References: exactly 62 entries, numbered 1-62 with no gaps; every in-text [N] resolves to an
   entry; no entry is uncited.
2. Figures 1-11 and Tables 1-16 each appear in ascending order in reading order.
3. Every table-of-contents page number matches the actual page the section starts on, including the
   appendix rows.
4. No section cross-reference (§N.N) points at a subsection that does not exist.
5. The phrases "not yet frozen" and "per-family date bounds" appear nowhere in the document.
6. "may or may not" no longer appears in the gap statement in either the Abstract or §1.8.
7. The Abstract still states the non-claims explicitly.
8. Page footers still read "Page N of <total>" with the correct total after any pagination change.

Report what you changed, quoting the before and after for each of the six fixes, and state
explicitly which of the eight verification checks passed.
```
