# Preliminary study: when should VEGO-AI ask a human?

**Ali Hamed. For Prof. Iris Reinhartz-Berger and Prof. Arnon Sturm. 3 September 2026.**

> Figures referenced below (`figureN_*.png`) are generated, not committed as binaries: run `python scripts/make_figures.py --dataset-root <dataset> --out <dir>` and `python scripts/make_figure4.py --dataset-root <dataset> --out <dir>` against the delivered dataset, then `python scripts/build_paper.py <this file> <out.docx> --figures <dir>` (add `--rtl` for the Hebrew file).


**The question.** Sub-question SQ1 asks when an agentic assessment system should request human judgment. This study takes the *when* only, as a question about where in the pipeline. It demonstrates points at which a human could have been asked and shows that those points can be identified automatically. It does not prove that asking would have changed any outcome, and it compares no accuracy.

**The dataset.** The completed VEGO-AI run over the two course cases, Cheers and ParkWise, in use-case and class diagrams: 179 scored student models, 165 with a per-model inspection report, 27 variability patterns. The expert assessment recorded for the MODELS 2026 evaluation is used exactly as it stands; recomputing it reproduces the paper's Table 3 setting by setting. Nothing new is collected, no agent is re-run, and no synthetic data is used.

**What the run does today.** It asks a person at one point only, after the variability classifier, where 11 of 27 patterns were queued. Everything the first three agents left open passed on silently.

FIGURE:figure3_decision.png|**Figure 1.** The three points where a human enters, placed on the pipeline.

**The three points.**

| | Where | When to ask | Size of the ask | What the expert record shows |
| --- | --- | --- | --- | --- |
| H1 | Domain guidelines, before any model is scored | always, once per case | 119 guidelines govern 4,853 later judgments | 68 of 169 guidelines not fully aligned; 17 required ones missing |
| H2 | Inspector, per guideline and model | when the verdict is not *Satisfied* | 28% of items, covering 90% of the expert's changes | 120 of 915 judgments overturned |
| H3 | Variability classifier | keep the existing queue | 11 of 27 patterns | judged by the co-authors only |

**What I measure.** Four counts, each with its denominator. How many points each rule sends to a person, per stage and setting. How far those points coincide with the places the expert actually changed the verdict. Where the trade-off sits at the inspector, as the threshold moves. And, for each pattern, the earliest stage at which any signal fires, which is the measurable form of the open question about intervening at Agent 2 rather than Agent 3. No real users this month: the three of us stand in for the humans in the loop, and we inject one intervention by hand (Saturday) to see what it changes downstream, rather than only observing.

**What kind of intervention.** At H1, accept, reject, or add a missing guideline — the three actions already in the recorded review. At H2, accept the verdict or overrule it with a corrected one.

**Why H1 is unconditional and H2 is triggered.** At the inspector the agent's own verdict separates: the expert overturned 2% of *Satisfied*, 46% of *Partially-Satisfied*, 35% of *Not-Satisfied*. At the guideline stage nothing separates: rejection is 39% for guidelines produced by all three runs, 44% by two, 33% by one, and the certainty the agent states averages 0.76 for accepted against 0.69 for rejected. Where no signal works and the items are few, the review is unconditional; where a signal works and the items are many, it is triggered.

**Plan.** Friday 4 September: the counts above over the whole corpus, and the trade-off curve. Saturday 5 September: one case worked end to end, adding by hand the missing Cheers use-case requirement that no guideline covers, recording what changes downstream with no agent re-run. Sunday 6 September: two pages with results and conclusions. Wednesday 9 September: proposal version 2, with these results entered as the preliminary results of Study 1 (selective intervention).

**What this does not establish.** The experts who assessed the run are co-authors of the system, and at the classifier they judged their own output, so this is not independent adjudication. The reviewed items were chosen rather than sampled at random, so every rate describes that sample. Overturned records a disagreement, not a demonstrated error. Independent expert labels remain at 0 of 24.
