# Where should an agentic assessment pipeline ask a human? Evidence from a completed VEGO-AI run

**Ali Hamed. For Prof. Iris Reinhartz-Berger and Prof. Arnon Sturm. 3 September 2026.**

> Figures referenced below (`figureN_*.png`) are generated, not committed as binaries: run `python scripts/make_figures.py --dataset-root <dataset> --out <dir>` and `python scripts/make_figure4.py --dataset-root <dataset> --out <dir>` against the delivered dataset, then `python scripts/build_paper.py <this file> <out.docx> --figures <dir>` (add `--rtl` for the Hebrew file).


**Abstract.** VEGO-AI assesses student UML models through four agents and requests a human at one point, after the last of them. We ask where it should request one. We use a completed run over two course cases, the expert-written requirement lists that the course already owns, and the review a person recorded over part of the output. Three results follow. Where a person reviewed the pipeline, they changed 147 of 1,019 judgments and rejected 68 of 169 guidelines. At the inspection stage the verdict the agent gives is itself a usable trigger; at the guideline stage neither of the two available signals separates anything. Against the expert lists the guidelines miss 59 of 78 requirements. We conclude with three intervention points and the code seams that carry them.

## 1. The question

An assessment pipeline does not make one decision. It writes a rubric, applies it to each model, and generalises across models, and each step is a judgment that can be wrong in its own way. VEGO-AI asks a human after the last step only. Sub-question SQ1 of the doctoral proposal asks when such a system should request human judgment; this paper takes the *when* as a question about *where in the pipeline*, and answers it from a run that has already happened. We do not claim that asking would have produced better models, and we compare no accuracy.

## 2. The system, and the judgment already recorded about it

Four agents run in sequence (Figure 1). Agent 1 writes guidelines for the modelling language. Agent 2 converts the case description into domain guidelines. Agent 3 judges each guideline against each student model. Agent 4 groups the recurring deviations into variability patterns. The run covers two cases, Cheers and ParkWise, in use-case and class diagrams: 179 scored models, 165 with a per-model inspection report, 27 patterns.

Three kinds of human judgment already exist around this run, and we use all three as they stand. First, the course's own requirement lists, which the input files label ground truth: 78 domain requirements across the four settings and the UML construct lists. Second, a review recorded in the project workbooks, in which a person went through part of the output and marked each item kept or overturned with a written reason. Third, the course grade, recorded beside the agent score for 164 model rows. No new data was collected and no agent was re-run.

FIGURE:figure1_pipeline.png|**Figure 1.** The pipeline makes four kinds of judgment and asks a human after one of them. Dashed arrows mark judgments a person later changed when asked to review them; at those points the run itself asked no one.

## 3. Where a human already changed the outcome

Table 1 places the recorded review against the pipeline. At the guideline stage the reviewer rejected 68 of the 169 guidelines the agent wrote, and added 17 requirements no run had produced at all, each annotated as an explicit requirement of the case. At the inspection stage the reviewer overturned 120 of 915 compliance judgments and 27 of 104 alternative-or-mistake judgments. The pipeline requested a human at none of these points; its one request, the review queue after Agent 4, covers 11 of 27 patterns.

| Stage | Does the run ask? | Reviewed | Changed by the reviewer |
| --- | --- | --- | --- |
| 1. Language advisor | No | none | not known |
| 2. Domain advisor, the guidelines it writes | No | 169 guidelines | 68 rejected (40%), plus 17 required ones absent |
| 3. Inspector, is the guideline met? | No | 915 judgments | 120 overturned (13%) |
| 3. Inspector, alternative or mistake? | No | 104 judgments | 27 overturned (26%) |
| 4. Variability classifier | Yes, the only point | none | 11 of 27 patterns queued |

**Table 1.** The recorded review against the point at which the run asks.

What the reviewer contributed is not uniform. Of 345 annotations, the largest group is 146 recalibrations of a compliance verdict, and of the 119 written as text, 96 make the verdict stronger rather than weaker: the agent was mostly too strict. The second group, 46 entries, says the requirement is real but sits in the wrong construct, twenty of them the phrase "may be an operation", all in class-diagram settings. That is modelling-language expertise, not domain knowledge, and it is a different competence from the case ownership behind the 116 annotations that simply affirm a guideline is explicit in the description.

## 4. What separates the points a human changed

FIGURE:figure2_signals.png|**Figure 2.** The verdict the agent gave at Stage 3 separates the judgments a human later changed. Neither signal available at Stage 2 does: agreement between the three runs is flat, and the certainty the agent states overlaps almost entirely between accepted and rejected guidelines.

At the inspection stage the agent's own verdict is the separator (Figure 2a). The reviewer overturned 2% of what the agent called *Satisfied*, 46% of *Partially-Satisfied* and 35% of *Not-Satisfied*. A rule that asks a human whenever the agent did not say *Satisfied* would have put 257 of 915 items, 28%, in front of a person and covered 108 of the 120 changes, 90%.

At the guideline stage nothing separates them. Guidelines produced by all three runs were rejected at 39%, by two runs at 44%, by one run at 33% (Figure 2b); the certainty the agent states averages 0.76 for accepted and 0.69 for rejected guidelines, and a threshold at 0.8 flags 75% of the rejected but also 60% of the accepted (Figure 2c). The code explains both. Agent 2 is instructed never to abstain: *"Every segment MUST be operationalized. If no template fits well, assign the closest available template with a low mapping_certainty (0.0-0.39)"*, so uncertainty is written down rather than acted on, and no Python in the pipeline ever reads `mapping_certainty`. The three runs are not a vote either: the winner is an `argmax` over an F1 computed from the model's own confidence labels, with no temperature or seed set, so agreement between runs measures sampling, not confidence.

The two failure modes also sit in different places (Figure 4). The reviewer kept 82% of the compliance verdicts and 55% of the alternative-or-mistake calls in the use-case settings, against 94% and 85% in the class settings. Coverage runs the other way: measured against the course's own requirement lists, 59 of 78 requirements have no agent guideline matched to them, and the worst settings are the class diagrams, 22 of 26 and 16 of 20. Verdicts fail where diagrams are looser; coverage fails where requirements are denser. One global escalation rule would serve neither.

FIGURE:figure4_settings.png|**Figure 4.** The two failure modes concentrate in different settings. (a) The reviewer disagrees most with the verdicts on use-case diagrams. (b) The guidelines miss most of the expert-written requirements on class diagrams.

At model level the agent score and the course grade order the models differently, r = 0.25 over 164 rows, and 0.02 in the ParkWise use-case setting. The two measure different things, and we do not treat the grade as the correct answer for any single guideline; the weak association is a reason to put a person in the loop, not evidence that either number is wrong.

## 5. Where the human belongs

FIGURE:figure3_decision.png|**Figure 3.** Where the human belongs, decided from the results: unconditional review where no signal separates and the items are few, a triggered request where a signal works and the items are many, and the existing queue kept. Agent 1 carries no recorded review, so no intervention point is claimed there.

**H1, review every guideline once, unconditionally.** No available signal predicts which guideline the reviewer will reject, so triggering is not possible here; the items are few and each one is reused, since 119 guidelines govern 4,853 guideline-model judgments. Review is a batch pass over a list, before any model is scored, and it must also add what is missing, which is how the 17 absent requirements were found. The competence needed is ownership of the case description plus modelling-language judgment.

**H2, at the inspection stage, ask whenever the verdict is not Satisfied.** This is a triggered request on a working signal: 28% of items reach a person and 90% of the judgments the reviewer changed are among them. The alternative-or-mistake call has no separator and the lowest agreement of any judgment in the run, 55% in the use-case settings, so it needs a sampled review rather than a trigger.

**H3, keep the queue after Agent 4**, which is the one point that already asks.

The code makes these cheap. Both question-routing functions are self-contained list-in, list-out functions whose single model call is the only thing that changes; the Phase 2 round loop already materialises the question lists beside the guidelines that carry the certainty; the Phase 3 merge holds both conflicting verdicts on one line; and the classifier's output already carries `requires_human_review`, a field the agents emit and no code reads during a run. Today the whole human surface is eleven lines appended after all results are final, and the outcome of the review has no path back into the run.

## 6. What this does not establish

The recorded review is the project's own, not independent adjudication, and its items were chosen by the reviewer rather than sampled at random, so every rate describes that sample: 7 to 10 of the 22 to 47 cases per setting. *Overturned* records a disagreement, not a demonstrated error. The overturn rates by verdict are an association within that sample; no threshold is fitted here, and the 28% and 90% would need to be re-measured on a random sample before they could be called operating points. The requirement lists are the course's own artefact, adequate for asking whether a guideline exists but not for judging whether a particular model satisfies it. No independent expert labels exist for the 27 classifications. Nothing here shows that asking a person would have improved any assessment.

## 7. Next

Apply the three signals to the whole corpus rather than the reviewed sample and report the load each rule implies per stage; draw the trade-off curve behind the 28% and 90% at several thresholds; and run one case end to end, adding by hand the missing Cheers use-case requirement that no guideline covers, to record what changes downstream without re-running an agent.

## References

Chow, C. K. (1970). On optimum recognition error and reject tradeoff. Dumais, S. T. and Nielsen, J. (1992). Automating the assignment of submitted manuscripts to reviewers. Kuhn, L., Gal, Y. and Farquhar, S. (2023). Semantic uncertainty. Mao, A., Mohri, C., Mohri, M. and Zhong, Y. (2023). Two-stage learning to defer with multiple experts. Mozannar, H., Lang, H., Wei, D., Sattigeri, P., Das, S. and Sontag, D. (2023). Who should predict? Reinhartz-Berger, I., Bragilovski, M. and Sturm, A. (2026). Not all differences matter: variability exploration of domain models via agentic AI. Villavicencio, M., Pan, S. and Wang, Q. (2026). Not all uncertainty is equal. Zou, H. P. et al. (2026). LLM-based human-agent collaboration and interaction systems.
