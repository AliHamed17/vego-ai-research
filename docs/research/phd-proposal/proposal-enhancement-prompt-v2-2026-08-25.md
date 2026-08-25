# Enhancement Prompt v2 — VEGO-AI Doctoral Proposal

Supersedes `proposal-enhancement-prompt-2026-08-25.md`. That prompt only repaired defects and it
opened with a blocker ("stop if you cannot find the editable source"), which is probably why nothing
came back. This version does three things differently: it produces usable output even when the
source is a PDF, it separates work a session can actually do from work only Ali can do, and it adds
the changes that raise the proposal rather than merely correcting it.

Current state: 30 pages, scored 91/100 on 2026-08-25
(`doctoral-proposal-2026-08-25-rev2-review.md`). Six defects outstanding, none yet applied.

## Prompt

```text
You are improving the VEGO-AI doctoral research proposal (30 pages, dated 25 August 2026,
"VEGO_AI_Doctoral_Proposal_Revised_20260825.pdf"). A strict review scored it 91/100. Your job is
both to repair six specific defects and to make the document genuinely stronger.

HOW TO WORK, AND HOW TO DELIVER

The proposal exists only as a PDF; there is no editable source in the repository. Do not stop
because of this, and do not edit the PDF as if it were the source. Instead produce a single markdown
deliverable, `proposal-revision-<date>.md`, structured as one entry per change:

    ## <section> — <one-line description>
    CURRENT:  <the exact text now in the document, quoted>
    REPLACE:  <the exact replacement text>
    REASON:   <one or two sentences>

That format is applicable to any authoring tool and is checkable line by line. Where a change adds
new material rather than replacing text, write NEW instead of CURRENT/REPLACE and give the full
text to insert plus the exact insertion point.

Extract the PDF text with pypdf to get exact current wording. Do not paraphrase what the document
says from memory.

HARD RULES

1. Never weaken the evidence boundary. These must remain stated and true: EXP-005
   generalization-safe expert labels incomplete, so accuracy, generalization and integrated-benefit
   claims stay blocked; zero of six medical entry gates satisfied; independent reviewers, raters and
   implementer not recruited; supervisor approval of research-question wording not recorded; the
   178/26 versus 165/27 count discrepancy unresolved. Never add an accuracy, generalization,
   expert-effort, transfer-safety or clinical claim.

2. Do not over-correct. All three factual errors in the previous revision came from making the work
   sound weaker than it is. Parts 1a-1c below restore accuracy; they do not add caution. If you find
   yourself writing a hedge that is not requested here, stop.

3. Do not fabricate. If a change needs a fact you cannot verify in the repository or against a
   publisher record, leave the current text and say what you could not confirm. Never invent counts,
   dates, approvals, or names.

4. Preserve every integrity property: 62 references numbered 1-62 with no gaps, every in-text
   citation resolving to an entry, no uncited entry, Figures 1-11 and Tables 1-16 ascending, every
   table-of-contents page number correct, no dangling section cross-reference.
```
```text
PART 1 — REPAIRS (six defects, all verified against the project's own documents)

1a. The protocol IS frozen; the document wrongly says it is not. In §4.2 and Appendix B Table 16,
    "The database-specific Boolean syntax has not been written, so the protocol is not yet frozen
    and no query has been executed." This contradicts
    docs/research/phd-proposal/literature-search-execution-register.md, which states "This register
    freezes the first five literature-query concepts before execution", heads its §2 "Exact frozen
    protocol queries", and states "The text in each code block is the exact canonical Boolean
    expression." QL-05's PubMed query is already in platform syntax. Replace with: "The five query
    families and their canonical Boolean expressions are frozen and registered; the per-platform
    field wrappers and filters are recorded at execution. No query has been executed." Keep the
    following sentence about there being no screening or inclusion counts exactly as it stands.

1b. "Per-family date bounds" is wrong, in three places (§3.2 summary, §4.2, Appendix B Table 16).
    The register applies a single primary window, 2015-2026, across all five families, with a
    documented snowballing exception. Replace each occurrence with "a single 2015-2026 window with a
    documented snowballing exception".

1c. The experiment register is described as holding more than it does. §4.3 says it "records for
    each run its inputs, frozen versions, procedure, and outputs". experiments/registry.md is a
    seven-column table: ID, Title, Status, RQ, Code/Config, Outputs, Notes. No procedure column, no
    run date, no per-run version field. Replace with: "which records for each registered experiment
    its identifier, status, research question, code and configuration paths, the location of any
    generated outputs, and the interpretation attached to it." Keep the existing sentence about the
    register not being independently auditable.

1d. The central gap claim contains a tautology. In the Abstract and §1.8: "None of the reviewed
    formulations assumes a claim about a model fragment whose interpretation is contested, whose
    reviewer must be selected for competence and authority, and whose resolution may or may not
    legitimately affect a later and differently situated case." The three conjuncts are the
    proposal's own design commitments in its own vocabulary, so the conjunction is near
    unfalsifiable; and "may or may not" excludes nothing. Rewrite so ONE conjunct carries the
    deficit and a falsifier is stated, for example: "The specific deficit is reviewer selection: no
    formulation in the literature reviewed here makes the choice of reviewer a function of assessed
    competence and authority over the contested fragment. A single study that did so would refute
    this claim." Drop "may or may not" entirely. Keep the existing caveat that follows about the
    formal searches not having been run. Make the Abstract and §1.8 consistent afterwards.

1e. Appendix A denies a dependency it relies on. Change "and the corrected verdicts are the ones
    given here" to "and the second-pass verdicts are the ones given here; they are conditional on
    that prototype." Keep all three existing disclaimers about the prototype. Add one sentence
    stating the classification is single-rater and its reliability has not been assessed.

1f. Two small items. "The reference audit" is relied on twice but never included or identified:
    either attach it as an appendix and add it to the table of contents, or name it as a companion
    file with its filename. And in §4.2 change "no corpus size to report" to "no protocol-derived
    corpus size".
```
```text
PART 2 — IMPROVEMENTS (this is what raises the document, not just repairs it)

2a. HIGHEST VALUE: complete the corpus screening. This is the outstanding half of the exercise
    Prof. Reinhartz-Berger assigned on 2026-08-12, and it is now missing from a fifth consecutive
    artifact. The branch-level and dimension-level classification is already done (Appendix A) and
    Figure 11 carries the slide content. What remains is screening the survey's own corpus.

    Method: the corpus is the papers classified under the four taxonomy branches of Zou et al.,
    "LLM-Based Human-Agent Collaboration and Interaction Systems: A Survey" (Findings of ACL 2026,
    reference [20]), listed in its companion repository
    github.com/HenryPengZou/Awesome-Human-Agent-Collaboration-Interaction-Systems. Fetch the
    repository README, extract the paper rows under the Taxonomy section, and screen each on title
    and abstract against the four research questions with the four-way disposition: relevant, less
    relevant, not relevant, missing. Report the counts per branch and per disposition, name the
    screening criterion for each disposition, and state that screening was single-rater.

    Note honestly that "missing" cannot apply to a paper. Apply it at the level of a research
    question or a taxonomy branch: it marks a concern of this research that no paper in the corpus
    addresses. Say so explicitly rather than forcing a four-way scale onto papers.

    Add the result as a new subsection of Appendix A, and update the three places that currently
    disclose corpus screening as outstanding so they report what was done. Do not mark the
    consolidation into an evaluated taxonomy as done; that remains future work.

2b. Strengthen the SQ2 and SQ3 gap statements the same way as 1d. §1.8's Table 1 states what remains
    uncertain for each sub-question. Check each row for the same defect: a negative claim resting on
    a conjunction of the proposal's own design commitments. Where you find one, name the single
    load-bearing element and state what evidence would refute it. A gap a committee cannot falsify
    is a gap it can dismiss.

2c. Make the contribution boundary sharper. The proposal claims four contributions, C1 to C4, where
    C4 is the integrated lifecycle. C4 is the most vulnerable, because an integration claim can
    always be met with "the parts already exist". Add one sentence to C4 stating what evidence would
    show the integration contributes something the parts do not, and what result would show it does
    not. The existing propositions P1 to P4 already do this well for the studies; C4 should match.

2d. Tighten the abstract's final third. It currently spends several sentences on what the results do
    not establish. That discipline is right and must stay, but it is stated twice over. Compress to
    one sentence of non-claims without dropping any of the four items (accuracy, expert effort, safe
    reuse, clinical validity), and use the space to state the contribution's boundary more precisely.

2e. Check every cross-document number for drift. The document cites counts that live in other
    project files: 62 references, five query families, four taxonomy branches, eleven unexpressible
    concepts, ten dimensions, six medical gates, three studies, four contributions. Verify each
    against the source that owns it and report any mismatch rather than silently adjusting.
```
```text
PART 3 — WHAT YOU CANNOT DO, AND MUST NOT PRETEND TO

These are the largest remaining constraints on the proposal, and none of them can be closed by
editing text. Do not fabricate progress on any of them. List them at the end of your deliverable as
a short section headed "Requires Ali, not editing", so they stay visible:

- Executing the literature searches. Zero of the five query families have been run. This is the
  ceiling on the entire literature contribution: until they are run, Chapter 1 is a critical
  synthesis and cannot be presented as systematic coverage. Running even one or two families would
  change §4.2 from "nothing to report" into real screening and inclusion counts, and would let the
  gap claim rest on a searched corpus rather than an anchor set. This is the single highest-value
  action available to the project.
- Resolving the 178/26 versus 165/27 count discrepancy. It needs the implementation snapshot, which
  was not supplied to the last revision.
- Supervisor approval of the research-question wording. Currently not recorded.
- Recruiting the independent reviewers, raters and implementer that Studies 2 and 3 require.
  Reliability and implementation-independence claims stay blocked until they exist. A resourcing
  request template already exists at docs/operations/study-resourcing-request-template.md.
- Completing EXP-005 generalization-safe expert labels.

PART 4 — DO NOT CHANGE

Each of these was verified correct; "fixing" it would introduce an error.

- Reference [4] Hevner et al., "pp. 75-106". An allegation that it should be 75-105 was checked and
  refuted: Crossref's publisher-deposited record and OpenAlex give 75-106, the printed DOI resolves
  to a page carrying 75-106, and the issue allocates 75-106 with the next article starting at 107.
- Reference [18] Ahmed's middle initial, "K. E. Ahmed". DBLP's canonical form is "Khaled E. Ahmed".
  An earlier request to change it to "K. Ahmed" was wrong and was withdrawn.
- The "61 of 62 cited references verified ... Reference [1] is unpublished" formulation.
- The British-to-American spelling conversion. It corrupted no reference title; [13] Fervers
  correctly retains "Utilisation" because that is the published form. Do not re-run any global
  spelling replacement over the reference list.
- The section-summary scheme and its six chapter-appropriate label pairs.
- Every statement of an open gate, unrecruited participant, unexecuted search, or unresolved count.

PART 5 — VERIFY AND REPORT

Run these checks against your deliverable and report each result explicitly:

1. References: 62 entries, 1-62, no gaps; every in-text [N] resolves; no entry uncited.
2. Figures 1-11 and Tables 1-16 ascending in reading order.
3. Every table-of-contents page number correct, including appendix rows.
4. No §N.N cross-reference points at a subsection that does not exist.
5. "not yet frozen" and "per-family date bounds" appear nowhere.
6. "may or may not" no longer appears in any gap statement.
7. The abstract still states all four non-claims.
8. Corpus screening counts, if added, are traceable to the repository listing you actually fetched.

Then state plainly: which of Parts 1 and 2 you completed, which you could not and why, and which
items from Part 3 remain open. Quote before and after for every change.
```
