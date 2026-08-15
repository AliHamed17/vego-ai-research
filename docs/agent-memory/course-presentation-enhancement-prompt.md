# Handoff prompt — enhance the IS Research Seminar final presentation

Paste this into a fresh Claude Code session (attach whatever new files/resources you
have first) to continue enhancing the MSc final-seminar deck.

---

You're picking up work on Ali Hamed's MSc "IS Research Seminar" (214.4001, Prof. Penina
Soffer) final presentation — a PhD-track student presenting a literature-review-guided
research direction for his VEGO-AI human-judgment thesis. Treat any files attached to
this message as new source material to fold in, with the same verification discipline
described below — check every new claim and citation before it goes on a slide.

## Where everything lives

- **The deck**: `C:\Users\ahamed\vego-ai\outputs\course-presentation\VEGO-AI - IS Research Seminar - Final Presentation.pptx`
  (18 slides: 14 presented + 4 backup). Built by
  `C:\Users\ahamed\vego-ai\scripts\build_course_presentation.py`.
- **Figures**: built by `scripts\build_course_presentation_charts.py` into
  `outputs\course-presentation\figures\` — each has a titled standalone version and a
  `-bare` version (no title/subtitle) for embedding, since the slide already carries
  the heading. Follow the `dataviz` skill for any new chart (validated palette,
  direct labels, no dual axes).
- **Synthesized findings** (streams, the analysis framework, gaps): 
  `outputs\course-presentation\findings.json` — this is what the deck script reads for
  slide text. Edit this file, not hard-coded strings in the build script, when changing
  findings content.
- **Rebuild + visual QA loop**: `scripts\render_deck.ps1` — rebuilds the pptx, exports
  to PDF via PowerPoint COM (no LibreOffice on this machine), rasterises every slide to
  `outputs\course-presentation\render\slide-NN.png`. **Always look at every rendered
  slide image after a change** — text overflow and title/subtitle collisions are the
  most common defects and are easy to miss by reading code alone.
- **Claim guard**: `scripts\check_course_presentation_claims.py` — must print
  `PASS` before you consider the deck done. It catches forbidden claims and unscoped
  "proven absence" language (see rules below).

## Source materials already used

- **Course materials** (`C:\Users\ahamed\Downloads\science research\`): CL1–CL7 decks
  + syllabus. CL7 ("Final Assignment") is the actual assignment spec — a 10–12 min
  presentation covering motivation, RQ, derived questions, search strategy, initial
  findings (streams / classification framework / gaps). CL1–CL2 (design science) and
  CL3–CL4 (research questions, literature review) are already reflected structurally.
  **CL5 ("Structure of paper") and CL6 ("Review process") are about the WRITTEN
  literature-review paper due end of September, not the oral presentation** — low
  priority for the deck itself, but worth mining when the written work starts.
- **Literature corpus**: `literature\verified-research-corpus-2026-08-12.json` — 144
  sources, each independently verified (132 `VERIFIED_ONLINE`, 11 `PARTIALLY_VERIFIED`,
  1 `COULD_NOT_VERIFY` and quarantined). This is the *only* source of citable titles.
- **Measured mechanism evidence**: `reports\generated\exp006\summary.json`,
  `exp007\summary.json`, `exp008\summary.json` — real, run, source-backed numbers
  (481 reconstructed lifecycle events vs. an 11-item legacy queue; the EXP-007 dosage
  Pareto frontier; EXP-008's guideline-instability rate).
- **Published-framework evidence**:
  `docs\research\governance\vego-ai-foundation-paper-record.md` — verified figures from
  the actual VEGO-AI MODELS'26 paper (ρ = 0.22 grader agreement, the 0.55–0.88
  uncovered-fragment range, the paper's own future-work statement naming human
  oversight).
- **Current RQ/SQ wording**: `docs\research\phd-proposal\three-study-contract.md`.
- **The Aug-12 supervisor call** (Iris + Arnon), transcribed this session:
  `artifacts\meetings\2026-08-12-iris-arnon\machine-transcript.txt` (machine ASR,
  Hebrew, undiarized — do not quote as attributed speech) and the curated writeup at
  `docs\research\meetings\2026-08-12-supervisor-meeting.md`.

## A concrete gap worth checking first

On the Aug-12 call, Iris explicitly asked for the literature-review section to be
**divided into subsections with a Google Scholar query per subsection** — read the
transcript around `[00:16:00–00:17:30]` for her exact wording. Check
`docs\research\phd-proposal\literature-review-structure-and-queries-draft.md` (produced
by a concurrent session — read it before writing anything new, it may already have
this breakdown) and decide whether the deck's search-strategy slide should show the
per-subsection queries explicitly rather than the current general protocol summary.

## Hard rules — do not relax these

1. **Never cite a title that isn't an exact match in the corpus JSON.** Verify
   programmatically (exact string match, not eyeballing), the way the earlier
   adversarial-check workflow did — it also planted a fake citation to confirm the
   matcher actually catches absence.
2. **Never assert proven absence in the literature.** The frozen protocol searches
   (QL-01–QL-05) have not been executed. Every gap/finding is phrased "within the
   reviewed corpus..." — never "no one has done X."
3. **No forbidden claims**: accuracy improvement, effort reduction, generalization,
   or clinical performance. EXP-005 stands at 0/24 validated generalization-safe
   expert labels — that gate is unchanged and blocks all four.
4. **GenAI disclosure** stays on the deck (currently a backup slide) — what it was
   used for, and explicitly what it was not used for (deciding gaps, generating
   citations, designing the framework).
5. Prefer editing `findings.json` and the chart script over hand-editing slide text
   in the build script, so content stays traceable to its data source.

## Before you start

Pull latest `main` first — a concurrent session (this project runs Claude and Codex
in parallel on the same checkout per its own convention) may have pushed changes since
this prompt was written. Check `git log --oneline -5` and `gh pr list` before assuming
the state above is current.

## When done

Re-run `scripts\render_deck.ps1`, visually inspect every slide image, run the claim
guard to a clean `PASS`, then follow the repo's existing git workflow: branch, commit,
push, `gh pr create` against `main` — check for an already-open PR with the same intent
first, the way the last session found PR #18 already covering its work.
