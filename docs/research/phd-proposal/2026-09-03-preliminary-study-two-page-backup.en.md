# Where the human enters VEGO-AI: the three points, the expert baseline they rest on, and what we test

**Ali Hamed. For Prof. Iris Reinhartz-Berger and Prof. Arnon Sturm. 3 September 2026.**

> Figures referenced below (`figureN_*.png`) are generated, not committed as binaries: run `python scripts/make_figures.py --dataset-root <dataset> --out <dir>` and `python scripts/make_figure4.py --dataset-root <dataset> --out <dir>` against the delivered dataset, then `python scripts/build_paper.py <this file> <out.docx> --figures <dir>` (add `--rtl` for the Hebrew file).


This page answers the question asked on 2 September: at which points should the system ask a person, what do we check to find out, and from what baseline. Every number below comes from the experimental material of the MODELS 2026 submission and its completed run over the Cheers and ParkWise course cases. Nothing new was collected, no agent was re-run, and no synthetic data enters any number here.

## The expert baseline already exists

The expert review is in the experimental material and is documented in the paper itself. In Phase B each reference-guideline cluster was assessed by an expert as fully, partially or wrongly aligned with the domain description. In Phase C a sample of Model Inspector outcomes was reviewed by two experts with extensive experience in teaching and assessing modelling artefacts, who rated each feedback item fully, partially or wrongly identified. Recomputing those sheets reproduces the paper's Table 3 exactly, setting by setting, which is how we know the sheets and the published results are the same thing.

| Stage | Does the run ask? | Expert review on record | What the expert changed |
| --- | --- | --- | --- |
| 1. Language advisor, writes the language guidelines | No | expert-curated construct list (Phase A) | 7 of 40 constructs never reached |
| 2. Domain advisor, writes the case guidelines | No | 169 guidelines assessed (Phase B) | 68 not fully aligned (40%), plus 17 required ones no run wrote |
| 3. Inspector, is the guideline met? | No | 915 judgments (Phase C) | 120 overturned (13%) |
| 3. Inspector, alternative or mistake? | No | 104 judgments (Phase C) | 27 overturned (26%) |
| 4. Variability classifier | Yes, the only point | judged by the co-authors | 11 of 27 patterns queued |

Two further anchors need no new expert. The course's own requirement lists, which the input files label ground truth, hold 78 domain requirements, and 59 of them have no agent guideline matched to them. Separately the junior grader's marks exist for 164 models; the paper is explicit that these are not absolute ground truth, because the grader worked from a strict grading index that penalised deviation from a reference solution while VEGO-AI penalised redundancies the index did not list. The two rank models only weakly together, Spearman 0.22 in the paper and Pearson 0.25 on our recomputation.

## The three points, and what the task list already asks for

The project task list already specifies human operations at exactly these stages: template add, update and delete; guideline update, operationalising a segment, unoperationalising it, and segment edits; and, at case evaluation, updating the scoring schema, the feedback, the compliance status, and mapping or unmapping an uncovered fragment. What the data adds is *when* to ask and *how much* it costs.

FIGURE:figure3_decision.png|**Figure 1.** The three points on the pipeline. Unconditional review where no signal separates and the items are few; a triggered request where a signal works and the items are many; the existing queue kept.

**H1. Review every domain guideline once, before any model is scored.** Unconditional, because no available signal predicts which guideline an expert will reject: guidelines produced by all three runs were rejected at 39%, by two runs at 44%, by one at 33%, and the certainty the agent states averages 0.76 for accepted against 0.69 for rejected. The cost is bounded and the leverage is high, since 119 guidelines govern 4,853 guideline-model judgments, and the reviewer must also add what is missing, which is how the 17 absent requirements were found. This is the task list's operationalise-segment operation. Competence: ownership of the case description plus modelling-language judgment.

**H2. At the inspector, ask whenever the verdict is not Satisfied.** Triggered, because here the agent's own verdict separates: the experts overturned 2% of *Satisfied*, 46% of *Partially-Satisfied* and 35% of *Not-Satisfied*. The rule sends 28% of items to a person and covers 90% of the judgments the experts went on to change. The second inspector question, whether an unmatched fragment is a legitimate alternative or a mistake, has no separator and the weakest expert agreement in the run, 0.55 in both use-case settings; the paper draws the same conclusion, that this judgment may require human involvement.

**H3. Keep the queue after the classifier**, the one point that already asks, and give its outcome a path back into the run; today it has none, and the task list's log of user operations is the place to record it.

## What we check and test

| # | What we test | Measure | Data | When |
| --- | --- | --- | --- | --- |
| T1 | Does the load implied by each rule hold beyond the reviewed sample? | items each rule sends to a person, per stage and setting | 165 inspected models, 27 patterns | Fri 4 Sep |
| T2 | Where is the trade-off point at the inspector? | share of items flagged against share of expert changes covered, at several thresholds | 915 reviewed judgments | Fri 4 Sep |
| T3 | Does a missing guideline propagate? | one Cheers use-case requirement no guideline covers, added by hand, then re-reading the affected models and pattern | 5 models of pattern P6 | Sat 5 Sep |
| T4 | Which stage fires first on the same point? | earliest stage carrying a signal, per pattern | 27 patterns | Sat 5 Sep |
| T5 | Does the measurement run end to end before the missing labels exist? | rehearsal over 27 synthetic records, reported as rehearsal only | synthetic, not evidence | done |

## What is still missing

One thing only. The variability classification at Stage 4 was judged by the co-authors themselves, who also served as evaluators in the earlier phases, so it is the weakest link in the chain and the reason EXP-005 stands at 0 of 24 generalization-safe labels. A search of the PhD Drive found the EXP-005 labelling protocol and no filled labels. Two requests would close the remaining gaps: the course grading index the junior grader used, which is named in the paper but not in the experimental material, and an independent labelling pass over the 27 patterns.

Meanwhile we generated a synthetic expert review over those 27 patterns under a stated deterministic rule set, every record stamped `SYNTHETIC_NOT_HUMAN` and `SYNTHETIC_NOT_EXPERT_EVIDENCE`. It rehearses the analysis end to end; it produces no agreement or accuracy result, none of its rows enter any number on this page, and EXP-005 remains at 0 of 24.

## Where this sits in the literature

H2 is a selective-prediction question, the reject option and its cost frontier (Chow 1970) in its modern deferral form, where the decision depends on the particular human rather than on abstention alone (Mozannar et al. 2023; Mao et al. 2023). H1 is not: there is no confidence signal to defer on, which is what the uncertainty literature anticipates when it separates stated confidence from what a person actually verifies (Kuhn et al. 2023; Villavicencio et al. 2026). The competence split, case ownership at H1 against modelling-language judgment at H2, is the reviewer-assignment problem (Dumais and Nielsen 1992), and the arrangement classifies against the human-agent involvement taxonomy (Zou et al. 2026) on the branch of feedback into a running system (Reinhartz-Berger et al. 2026).

## What this does not establish

The experts who assessed Phases B and C are co-authors of the system, and for Stage 4 they judged their own classifier, so none of this is independent adjudication. The reviewed items were chosen rather than sampled at random, so every rate describes that sample. Overturned records an expert disagreement, not a demonstrated error. The 28% and 90% would need re-measuring on a random sample before they are operating points. Nothing here shows that asking a person would have improved any assessment, and no accuracy is compared.
