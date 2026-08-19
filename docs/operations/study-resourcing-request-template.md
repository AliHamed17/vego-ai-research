Study 2/3 resourcing request — draft for Ali to fill in and send

Source: `chapter-4-research-methodology.md` §4.4 and §4.5, and Part 3 item 13 of
`sections-2-and-4-thinking-notes.md`. Two roles are named as required but nobody is assigned to
either: an independent implementer or reviewer for Study 2's conformance suite (someone who builds
or runs a variant implementation they did not design themselves, to test whether the judgment-
record contract actually discriminates conforming from non-conforming implementations), and two
raters for Study 3's transfer-eligibility reliability study (who independently apply the
eligibility procedure to the same source records and target-context descriptors so inter-rater
agreement can be measured). This assistant has no ability to recruit, name, or commit a real person
to either role — that has to happen through Ali's own outreach, which is what this template is for.

## What to ask for

**Study 2 — independent implementer/reviewer.** Needs to be someone who did not design the
judgment-record contract, capable of either implementing a variant against the specification in
§4.4 or critically reviewing an implementation someone else built for hidden assumptions. A fellow
PhD student, a lab colleague, or a suitably qualified person outside the immediate research group
would all work — the requirement is independence from the design process, not seniority.

**Study 3 — two raters.** Needs to be two people, independent of each other and of Study 3's
design, willing to apply a defined decision procedure (not make free-form judgment calls) to a set
of source-judgment/target-context pairs and record which of three states they reach and why.
Domain familiarity with the guideline-operationalization setting (software-engineering or medical,
depending which scenario is being rated) is more important than research experience — this is a
reliability study on the procedure, not an expert-panel study.

## Draft message — fill in the brackets before sending

Subject line: Looking for [one/two] volunteer[s] for a short PhD evaluation task

Hi [name],

I'm working on my PhD proposal under Iris Reinhartz-Berger and Arnon Sturm, and I need
[an independent implementer to test a specification / two independent raters to apply a decision
procedure] as part of the methodology. [Describe the task in 2-3 sentences using the relevant
paragraph above.] It should take about [estimate] and would happen around [rough timeframe].
Would you be willing to help, and if so, when would work for you?

Thanks,
Ali

## What to do with this

Decide who to approach for each role (a specific person, not a placeholder), fill in the brackets,
and send it yourself — this assistant has no outreach or email-sending access. Once someone agrees,
record their name, role, and the date they agreed in `docs/research/phd-proposal/decision-change-
log.md` or the relevant study's own tracking, and update `chapter-4-research-methodology.md` §4.7
and `2026-08-19-chapter4-decisions-packet.md` to remove this item from the open list. Until then,
both studies' fallback applies as already stated in `three-study-contract.md`: report the
implementation-independence gap and the rater gap outright, and make no claim that requires the
missing role to have been filled.
