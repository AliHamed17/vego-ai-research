# VEGO-AI Foundation Paper — Record and Claim Verification

Status: **verified against the paper PDF supplied 2026-08-11.** This document records what the published VEGO-AI paper actually reports, and resolves the previously unverified `MV-02` empirical claim in the [MediVARIA overview](./medivaria-medical-extension-overview.md).

## The publication

| Field | Value |
| --- | --- |
| Title | *Not All Differences Matter: Variability Exploration of Domain Models via Agentic AI* |
| Authors | Iris Reinhartz-Berger (University of Haifa); Maxim Bragilovski, Arnon Sturm (Ben-Gurion University of the Negev) |
| Venue | ACM/IEEE 29th International Conference on Model Driven Engineering Languages and Systems (MODELS '26), October 2026, Málaga, Spain |
| DOI | `10.1145/3822455.3830312` |
| Experimental material | `https://github.com/ieiris/VEGO-AI/` (per the paper's own footnote) |
| Source file | `Variability_VEGO-AI_MODELS2026_final.pdf`, 1,126,550 bytes, supplied via the shared VEGO-AI Drive folder |
| VEGO-AI expansion | **V**ariability **E**xploration for m**O**dels via a**G**entic **AI** |

**Correction logged 2026-08-18 — the acronym expansion above was previously wrong.** This
record used to read "Variability Exploration via Guideline Operationalization and Agentic
Intelligence." That string is the **Zoom meeting topic line** for the 2026-08-05 supervisor
call (see [`2026-08-05-supervisor-provenance-manifest.md`](../meetings/2026-08-05-supervisor-provenance-manifest.md),
which records it as the only content of the chat log) — a prior session mistook it for the
framework's official name and copied it here. The paper defines the acronym itself, twice
and identically, in the abstract and in §1: *"VEGO-AI (Variability Exploration for mOdels via
aGentic AI)"* — the capitalisation is the authors' own mnemonic. Verified 2026-08-18 against
`Variability_MAS4MODELS2026_Mar28_IRB2איריס.pdf`, p. 1 (abstract) and p. 2 (§1). Presenting
the wrong expansion of the supervisors' own framework name would have been a costly error.

**Version caveat on the citation fields above.** The only paper artifact currently on this
machine is the **anonymised MAS4Models submission draft** (`..._Mar28_IRB2איריס.pdf`), whose
page 1 still carries template placeholders — "FirstName Surname", "WOODSTOCK'18", and
`https://doi.org/10.1145/xxx`. It therefore cannot itself substantiate the Venue and DOI rows
above; those came from a `..._MODELS2026_final.pdf` that is no longer present on disk. Until
that final version is re-supplied, describe the paper as **accepted / program-listed at
MODELS 2026** and cite it by title and authors, without asserting a DOI. This matches the
conservative framing used in the 2026-08-17 structured literature review (v9, p. 2).

**Authorship note, stated plainly because it matters for how the thesis positions itself:** Ali is not an author of this paper. VEGO-AI is the supervisors' (and Maxim Bragilovski's) published framework. The doctoral work builds *on* it — which is exactly the separation Chapter 3 §3.7 already asserts ("VEGO-AI is the vehicle, not the question"). This record confirms that framing is correct rather than merely asserted.

**Correction to the MediVARIA one-pager:** that document says the architecture was "submitted to ACM/IEEE MODELS 2026." The paper carries a DOI and full proceedings citation, so it is accepted/published, not merely submitted. The one-pager was last edited 2026-05-05 and was presumably accurate then.

## What the paper reports

Four LLM-powered agents coordinated by a central orchestrator, implemented in Python, all calls to **GPT-4o at temperature 1.0**:

1. **Language Advisor** — produces language templates from the language name plus an expert-curated construct list.
2. **Domain Advisor** — produces evolving reference guidelines capturing valid modeling alternatives.
3. **Model Inspector** — assesses compliance and feeds newly discovered alternatives back into the guidelines.
4. **Variability Explorer** — classifies recurring deviation patterns as **substantial** (systematic, meaningful) or **occasional** (sporadic, erroneous).

Evaluation: two domains (Cheers, a winery management system; ParkWise, a parking-lot management system) × two UML languages (class diagrams, use-case diagrams) = four settings, drawn from a second-year undergraduate modeling course across consecutive years. Case-model counts per setting: ch-ucd 46, ch-cd 47, pw-ucd 44, pw-cd 41 (**178 total**). Student models supplied in PlantUML.

## Verification of the MediVARIA `MV-02` claim

The MediVARIA one-pager cites a TRL-3 empirical baseline. Each figure is checked below against the paper.

| MediVARIA claim | Paper says | Verdict |
| --- | --- | --- |
| "Language Advisor F-scores of 0.75–1.0" | Table 2 (Phase A): lowest F1 0.75 (Run 2, pw-cd); perfect 1.0 in several runs (Run 2 ch-ucd, Run 1 pw-ucd) | **Verified — exact** |
| "Domain Advisor guideline alignment of 0.70–0.88" | Phase B: 0.70 (ch-ucd), 0.85 (pw-ucd and pw-cd), 0.88 (ch-cd) | **Verified — exact** |
| "compliance scoring of 0.80–0.96 against expert review" | Table 3 (Phase C): "average scores on compliance vectors are consistently high across all four settings (0.80-0.96)" | **Verified — exact** |
| "all identified variability patterns validated correct by domain experts" | "The Variability Explorer yielded **26** variability patterns... **Eight** of the 26 were classified as substantial variability... The patterns indicated as substantial variability were judged correct **by the authors**." | **Overstated on two counts** — it was the 8 substantial patterns, not all 26; and the judges were the paper's authors, not independent domain experts |

**Net:** three of the four figures are exactly accurate. The fourth overstates both scope and independence of validation. Any reuse of these figures in proposal or funding material should carry the corrected wording.

## Material context the one-pager omits

The one-pager quotes only the favourable ranges. The paper also reports, in the same results section:

- **Uncovered-audit scores are substantially weaker and more variable: 0.55–0.88**, with both use-case-diagram settings at 0.55. The paper's own reading: this "reflect[s] the greater interpretive effort required to judge whether model additions are acceptable in specific contexts" and "**may require human involvement**."
- **Agreement with the human grader is weak.** Spearman's ρ = 0.22 (p = 0.007, 95% CI [0.060, 0.364]) between Model Inspector scores and the junior grader's grades. The paper notes the grader's evaluations "do not represent absolute ground truth."
- **The expert review was a sample**: 16 Model Inspector outcomes (4 per setting) reviewed by two experts.
- **Scope limits, per the paper's own threats section**: two domains from a single institution, one LLM, two modeling languages.

None of this undermines the framework — the paper is appropriately careful about it. But a funding or proposal document that cites 0.80–0.96 while omitting 0.55–0.88 and ρ = 0.22 is presenting a selected view, and would be vulnerable to exactly the question a reviewer should ask.

## Why this matters directly for the doctoral research

The paper's own Future Work section names this doctorate's research question as the natural next step:

> A second direction is to incorporate human-in-the-loop oversight at key pipeline stages (guideline validation, compliance review, and variability classification), which would strengthen reliability and serve as a natural next step toward deployment in real assessment settings.

Combined with the empirical finding that uncovered-fragment detection "may require human involvement" (0.55 in both UCD settings), this is **published, citable evidence from the supervisors' own work that the gap Chapter 3 argues is real, recognised, and open** — and it identifies precisely the three pipeline stages where intervention is needed, which maps onto SQ1's selective-intervention question.

This is stronger grounding than Chapter 3 currently uses. §3.1 presently argues the gap from the general literature with a "to our knowledge" hedge; it can now additionally cite a peer-reviewed paper that states the need explicitly. Recommended follow-up: add this citation to Chapter 3 §3.1 and §3.3, and add the paper as a tagged RQ1 source in the literature workbook.

## Data reconciliation note

The paper reports **178** case models across the four settings (46 + 47 + 44 + 41). The repository's tracked figure is "179 scored evaluations across 4 settings (83 distinct student models)" — see `ISS-021`, which already flags that 179 counts scored ranking rows including duplicates. The two numbers describe different units and are not necessarily in conflict, but the exact relationship should be reconciled before either figure enters a thesis chapter.
