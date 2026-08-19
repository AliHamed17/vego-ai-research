# Claude Prompt — Literature Review v16 Enhancement

Paste this into Claude (fresh session or this one) to fix the confirmed problems in Literature
Review v16, grounded in the strict independent audit already on file. Status: prompt only, not yet
executed.

## Prompt

```text
Fix Literature Review v16 (the file "VEGO_AI_Literature_Review_v16_GitHub_Synchronized_45_Page_
2026-08-19.pdf", supplied by Ali from Downloads, not currently tracked in this git repo) against
the findings in an independent, adversarially-verified audit already on file at
docs/research/phd-proposal/literature-review-v16-workbook-v11-verification-report.md. Read that
report in full before doing anything else - it is the source of truth for what is broken and why,
including exact page numbers and verbatim quotes for every finding. Also read
docs/agent-memory/issues.md entries ISS-036 and ISS-037, which track the two most severe problem
clusters from that audit.

Before touching content: find the actual editable source this PDF is generated or authored from -
search this repo for any build script under scripts/ that might produce it (there was none as of
this audit, so it is likely a hand-maintained Word document or a source outside this repo entirely)
and, if you cannot find one, ask Ali directly where the authoritative editable copy lives rather
than inventing a new one-off editing pipeline or editing the PDF as if it were the source. Do not
proceed with content fixes until you know what you are actually editing.

Once you know the real source, work through these confirmed problems, in priority order. The
headline "106/116" ACL-taxonomy-disposition figure is asserted as settled fact on the title page,
in the abstract, in the Figure 1 caption, and on p.34, while the document's own Appendix A register
- the place meant to hold the authoritative count - marks that same field "Not final" and calls for
"second review required"; either run the actual second review and replace "106/116" everywhere with
a number Appendix A itself can certify, or rephrase every one of those four locations to say
explicitly that the count is provisional and sourced from the companion workbook's title-screening
note, not from this document's own controlled register. Six named in-text citations have no entry
anywhere in the 45-page References list or the 81-entry Appendix B: Dhanorkar et al. (2026),
Villavicencio et al. (2026), and Zhou et al. (2026) - the three sources anchoring the document's
central "recent evidence narrows novelty further" argument on p.28 - plus Shneiderman (2020),
Dellermann et al. (2019), and Pearl & Bareinboim (2014). All six are real, correctly-attributed
papers; the companion workbook already has complete citations with DOIs for at least Dhanorkar and
Shneiderman, so pull the missing entries from there rather than re-researching them from scratch,
verify each one independently before adding it, and add every missing entry to both the References
list and Appendix B - or, if a citation genuinely cannot be verified, remove the claim that depends
on it rather than leaving it uncited. Appendix B's S002 entry carries an unresolved "(ref says
2013)" year annotation into the final References list; resolve it to a single clean year (2014,
per IEEE TSE vol. 40) rather than shipping the ambiguity.

The self-reported "hostile-review scorecard" (pp.34-35, "Overall 76/100") has no disclosed
weighting method, is entirely self-assigned despite its adversarial-sounding name, and lets a
perfect visual-quality score offset a near-failing search-rigor score in the same headline number -
this is the same defect the prior v15 audit already flagged in this document's own lineage, shipped
again unfixed. Either replace it with an actual external review, or keep it self-assessed but make
that explicit in its own label, disclose the exact weighting formula used for "Overall," and stop
letting a production-quality criterion (visual polish) mathematically cancel out execution-quality
criteria (search rigor, reproducibility) that the project's own gates (QL-01-05 at 0/5, EXP-005 at
0/24) say have not actually been earned yet. Do not simply lower the number without also fixing the
methodology that produces it - an unweighted composite with a different number is the same defect.

The RQ wording displayed as current (title page, p.4, Figure 29, p.31) is a demoted v15-candidate
wording, not the project's actual current canonical wording, which lives in
docs/research/phd-proposal/three-study-contract.md and the 2026-08-19 decisions packet (containing
the phrases "co-reasoning," "variability exploration scenarios," and "guideline operationalization
scenarios" - none of which appear anywhere in the 45-page PDF as it stands). Replace the displayed
wording with the actual canonical current wording, or, if you have a specific reason to keep
showing the v15 candidate instead, say so explicitly in the document rather than presenting a
substituted wording as if it were current - check three-study-contract.md's last-updated date
against your own edit date to make sure you are not looking at a stale copy of the canonical
wording yourself.

The claimed six-gap/three-RQ mutually-exclusive partition does not actually hold as written and
needs real reconciliation, not just softer language: G1's own definition requires evaluating
"persistent downstream reuse," which Table 8 assigns exclusively to SQ3, so either redefine G1 to
remove that dependency or explicitly acknowledge the SQ1/SQ3 overlap it creates. "Authority" is
claimed as an owned construct of both SQ2 and SQ3 in the same paragraph with no distinguishing
definition given at that point - add the distinction inline rather than leaving it to be inferred
from the companion workbook. G6 is a construct-validity critique of VEGO-AI's own internal labels,
a categorically different kind of claim than G1-G5's external-literature-gap claims - either give
it its own template rather than forcing it into the same "novelty boundary + falsifier" shape, or
justify why the shared template still fits. Figure 27's caption claims "primary and secondary RQ
ownership" but Table 8 only shows single-owner rows with no secondary-ownership column - either add
the secondary-ownership data Table 8 needs to actually support that caption, or stop claiming
arbitrated overlap resolution that isn't shown anywhere in the text. Resolve the "C1-C6 requirements"
(Table 8) vs. "C1-C7" (p.34 narrative) count mismatch for the same construct - state clearly whether
there are six or seven components and what the seventh is if the answer is seven. Add one explicit
equivalence statement, in one place, tying together the four names currently used for the same
three-way structure (Study 1/2/3, Artifact A/B/C, SQ1/SQ2/SQ3, and the workbook's own RQ1/RQ2/RQ3
sheet titles) so a reader does not have to reconstruct the mapping by cross-referencing an external
file.

Only 20 of the 81 candidate/anchor sources in Appendix B have complete extraction sheets, yet
Sections 2-12's prose reads as confident narrative-citation-chaining ("the literature establishes
that...") rather than the "concept-centric, not a sequence of paper summaries" framing Section 1.2
claims for itself. Either complete extraction on enough of the remaining 61 sources to defensibly
support the confidence level of the prose, or explicitly scope every field-level claim in Sections
2-12 down to the 20 sources that are actually fully extracted, rather than letting the prose imply
broader support than the extraction state can back.

Two things you should NOT do while fixing the above: do not touch the workbook (v11 xlsx) as part
of this task - a separate, paired prompt handles that, and fixing this PDF in a way that silently
re-breaks consistency with the workbook (e.g. changing G6, RQ wording, or FT-A/FT-B labels here
without checking what the workbook currently says) will just recreate the same cross-artifact
contradiction the audit already found. Before finalizing, re-read the current state of the workbook
CSVs/sheets so your PDF-side fixes are at least compatible with what the workbook says today, and
flag explicitly (to Ali, in your final summary) anywhere the two still won't agree until the paired
workbook prompt also runs. Also do not simply delete a hedge or caveat to make a finding disappear -
every fix above should make the document either more accurate or more honestly scoped, never just
quieter about the same underlying gap.

Before declaring this done: re-verify your own fixes with the same rigor the original audit used -
re-check that every citation you added actually resolves and is correctly attributed, re-check that
the "106/116" (or its replacement) is now consistent everywhere it appears, re-check the scorecard's
arithmetic actually matches its disclosed method, and re-read three-study-contract.md yourself to
confirm the RQ wording you inserted is in fact the current canonical text at the time you finish,
not what this prompt assumed at the time it was written. Update
docs/research/phd-proposal/literature-review-v16-workbook-v11-verification-report.md with a short
"resolved since" note per finding you fixed (or a follow-up report if you prefer a clean v17
verification pass), and update docs/agent-memory (session-log.md, revert-log.md, and issues.md to
close or update ISS-036/ISS-037) per this project's CLAUDE.md convention.
```
