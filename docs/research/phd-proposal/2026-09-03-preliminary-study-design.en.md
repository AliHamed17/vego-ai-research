# Where should VEGO-AI ask a human? Preliminary study on the Cheers and ParkWise runs

**Ali Hamed, 3 September 2026. For Prof. Iris Reinhartz-Berger and Prof. Arnon Sturm.**

**The question.** SQ1 asks when an agentic assessment system should request human judgment. This study takes the *when* only: at which points in a completed VEGO-AI run could a human have been asked, and can those points be found automatically from what the system already produces? It demonstrates such points. It does not prove that asking would have produced a better model, and it compares no accuracy.

**The data, and the human judgment already inside it.** The completed run over the two course examples, Cheers and ParkWise, in use-case and class diagrams: 179 scored student models, 27 recurring variability patterns, four settings. Two kinds of human judgment already exist in the project's own workbooks and are used here as they stand: a review in which a person went through a sample of the agent's output and marked each item kept or overturned, with a written reason; and the course grade, available beside the agent's score for 164 model rows. Nothing new is collected, and no synthetic data is used.

**The baseline: where the system asks today, and what a human changed where it did not.**

|Stage|Does the system ask?|Human review already recorded|What the human changed|
|---|---|---|---|
|1. Language advisor|No|None|Not known|
|2. Domain advisor: the guidelines it writes|No|186 guidelines|68 not accepted in full (37%): 46 partly, 21 wrong, 1 unsure. Separately, 59 requirements in the course reference have no agent guideline matched to them|
|3. Inspector: is the guideline met?|No|915 judgments, 32 model reviews|120 overturned (13%)|
|3. Inspector: alternative reading or mistake?|No|104 judgments|27 overturned (26%)|
|4. Variability classifier|Yes, the only point|None|11 of 27 patterns queued, for medium confidence or a proposed guideline change|

**Can those points be found automatically? At Stage 3, largely yes, from the agent's own verdict.** The reviewer overturned 2% of the items the agent called *Satisfied*, but 46% of *Partially-Satisfied* and 35% of *Not-Satisfied*. A rule that asks a human whenever the agent did not say *Satisfied* would have put 28% of the items in front of a person and covered 90% of the judgments that person went on to change. For the second Stage 3 question, whether an unmatched fragment is a legitimate alternative or a mistake, no field separates them: the severity the agent assigns does not distinguish the overturned cases. That is where a human is needed most and where automatic identification helps least. At Stage 2, more than a third of the agent's own guidelines were not accepted in full, and the system never asks there.

**At model level.** For the 164 rows where both exist, the agent's score and the course grade order the models differently: correlation 0.25 overall, and 0.02 in the ParkWise use-case setting. They measure different things, and the grade is not treated here as the correct answer for any single guideline. The weak association is a reason to put a person in the loop, not evidence that either number is wrong.

**What the study adds by Sunday.** First, the same signals applied to the whole corpus rather than to the reviewed sample, reporting per stage how many items each rule would send to a person. Second, the trade-off curve behind the 28% and 90% above, at several thresholds. Third, one case worked end to end: Cheers use-case pattern P6, "Customer as actor", where the course reference names no such actor in any of its nine use-case requirements, three of the five models carrying it were flagged as alternative readings, and the classifier queued it at medium confidence; we then add the missing guideline by hand and record what changes, with no agent re-run. Fourth, for each pattern, the earliest stage at which any signal fires. That last one is the measurable form of the open question about intervening at Agent 2 rather than Agent 3: it reports where the first signal sits and ranks no stage.

**What is not claimed.** The recorded review is the project's own, not independent adjudication, and the reviewed items were chosen by the reviewer rather than sampled at random, so the rates describe that sample. "Overturned" means the reviewer disagreed, not that the system was proven wrong. No improvement, accuracy, effort or generalization statement follows, and no independent expert labels exist for the 27 classifications. Asking a human may also harm or change nothing.

**Plan.** Thursday 3 September: this page, for your comments before the run. Friday 4 September: whole-corpus signal counts and the trade-off curve. Saturday 5 September: the worked case and the earliest-stage counts. Sunday 6 September: two pages with results and conclusions. Wednesday 9 September: proposal version 2, with these results as the preliminary results of Study 1.
