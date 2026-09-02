# When should VEGO-AI ask a human? Preliminary study design, for comment before the run

**Ali Hamed, 3 September 2026. For Prof. Iris Reinhartz-Berger and Prof. Arnon Sturm.**

**The question.** SQ1 asks when an agentic assessment system should request human judgment. This study takes the *when* only: in one completed VEGO-AI run, which points did the system leave open, either as an uncertainty it signalled itself or as a gap against the course reference material, and can those points be found automatically? It demonstrates such points. It does not prove that asking a human would have improved the result, and it compares no accuracy.

**The data.** The completed run of 14 June 2026 over the two course examples, Cheers and ParkWise, in use-case and class diagrams: 179 scored student models, 165 of them with a per-model inspection report, and 27 recurring variability patterns across the four settings. No new data, no synthetic data, no re-run of the agents.

**The baseline: what happens today.** The pipeline asks for a human in exactly one place, after Agent 4, the variability classification. It queued 11 of the 27 patterns, each for medium confidence or for a proposed guideline change. Everything the first three agents left open passed on silently: no request, no record. That silence is the baseline this study describes.

**Where a human could have been asked, and how the point is found automatically.**

|Stage|What the human would be asked|Signal that finds the point|Uncertainties the run signalled|Gaps against the course reference|
|---|---|---|---|---|
|1. Language advisor|Template guidelines: is this one right, and is the unreached construct needed?|Cluster match not "high", or no link to the language base|6 of 38 guideline clusters|7 of 40 language constructs never reached|
|2. Domain advisor|Domain guidelines: is this one correct, and is the missing one needed?|Mapping certainty below 0.8, no link to the course base, or a question the agent asked and never had answered|18 of 28 clusters, plus 12 questions raised and unanswered|59 of 80 course guidelines with no agent match|
|3. Model inspector|Per student model: is this a legitimate alternative reading or a mistake?|Fragment labelled "alternative", or a mistake marked high severity|150 of 165 models carry at least one alternative; 15 high-severity mistakes|No reference exists at this stage|
|4. Variability classifier|Is this really occasional or substantial variability?|Medium confidence, or the agent proposes a guideline change|11 of 27 patterns, the only stage that asks today|No reference exists at this stage|

Counts are totals over the four settings; the per-setting rows are frozen as a table on Friday. They are counts of signals, not verified errors.

**One case, worked through.** Cheers use-case, pattern P6, "Customer as actor", found in five student models. Agent 4 classified it as occasional variability with medium confidence and queued it, which is the one request the run made. Upstream it was silent: none of the 27 domain guidelines names Customer as an actor, and three of the five models had already been flagged at Stage 3 as carrying an alternative reading. We will also add the missing guideline, "Customer is an actor who places orders", by hand and re-read what changes in those five models and in the classification. No agent is re-run, and no output is graded.

**What will be measured.** How many points each signal finds, per stage and per setting, as tabled. How far the automatically found points coincide with the reference gaps at Stages 1 and 2. On one case, how far they coincide with the points where the three of us, marking independently, would have wanted to be asked. And, for each pattern, the earliest stage at which any signal fires: this is the measurable form of the open question about intervening at Agent 2 rather than Agent 3. It reports where the first signal sits and ranks no stage.

**What is not claimed.** No improvement, accuracy, effort or generalization statement. Asking a human may also harm or change nothing. No independent expert label exists for any of the 27 classifications, so nothing here is scored against a correct answer, and our own marks are not expert ground truth. The course guideline bases are reference material, not adjudicated truth, and Stages 3 and 4 have no reference at all.

**Plan.** Thursday 3 September: this page, for your comments before the run. Friday 4 September: freeze the per-setting table; send the marking sheet, about fifteen minutes each. Saturday 5 September: collect the marks. Sunday 6 September: two pages with the results and conclusions; if fewer than two sheets are back, Sunday reports the measures that need no marks and the rest follows on Wednesday. Wednesday 9 September: proposal version 2, with these results as the preliminary results of Study 1.
