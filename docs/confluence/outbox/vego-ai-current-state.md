# VEGO-AI Current State

Generated from repository memory on 2026-09-06 03:18 +03:00.

# Current State

Fast orientation for Codex and Claude. Update this whenever the project state changes.

**Last Updated:** 2026-09-04 by Codex (Tasks 2–5 technical lane: added the versioned privacy-safe Q&A communication contract, deterministic append-only observer/episode projection, live-event extractor support, and baseline terminology freeze. Offline observer verification passes, but direct wiring into protected `orchestrator.py` remains partial by design; the full suite has one unrelated merge-base hardening-test failure. No live LLM run, API call, human label, frozen-output mutation, or supervisor-document change was made). Earlier the same day, Task 1 local recovery found no original `interaction_log.jsonl`; archived code/logs support conditional historical full-content logging and the 12/30 Q&A baseline remains unchanged. The Q&A escalation detection study remains descriptive and human-validation pending. Earlier: 2026-09-03 by Codex (new supervisor direction makes **Q&A ESCALATION DETECTION STUDY** the active milestone: read-only extraction of inter-agent questions, confidence/evidence observability, transparent alert scaffold, and blind human-review materials; no validation run or performance claim). The Agent-C score reconstruction/C2 bridge remains valid later-stage technical evidence and the 111-versus-114 C2 discrepancy is deferred. The supervisor-facing operational plan now starts with zero-cost `interaction_log.jsonl` recovery, uses a one-setting feasibility rerun, and keeps `ANSWER_NOT_PERSISTED` terminology with no manual labeling in the current plan. Earlier: 2026-09-03 by Codex (strict one-page paired-condition human-intervention experiment). Earlier: 2026-09-02 by Claude (the supervisor call narrowed the preliminary study to ONE descriptive WHEN/WHERE escalation study over the frozen run; EXP-045/046 provide its descriptive basis). Earlier: 2026-08-24 by Claude (delivered the strict proposal review and repaired the pre-existing CI-red build chain; see ISS-039/040/041). Earlier still: 2026-08-14, transcribed and analyzed the 2026-08-12 Iris/Arnon call; see the August 12 checkpoint below and `docs/agent-memory/session-log.md`.

Both workstreams below are now merged into `main` (PR #15, then PR #16). Sections are still grouped by original workstream for orientation, since they cover distinct parts of the repo, but there is no longer a pending merge between them; `main` is the single current state for both. Feature branch `docs/iris-july29-phd-execution` is retained (not deleted) at commit `20b04fc` for reference.

### 1c. Study 2A VEGO-AI_ON versus VEGO-AI_OFF (2026-09-06)
* A separate preparation branch `study2/vego-ai-on-off-preparation` and draft PR #40 define a preregistered descriptive comparison on the frozen public AirTravel corpus (`cd_airtravel` / `text2uml_airtravel_253b26dc`, N=4). PR #40 is open, draft, and unmerged; its live head is kept in GitHub rather than pinned in durable memory.
* `VEGO-AI_ON` is the current full orchestration contract; `VEGO-AI_OFF` is a newly constructed single-model, no-delegation/no-Q&A/no-feedback/no-Detector baseline. Both conditions keep the same corpus, cases, model configuration, limits, schema, validation, privacy, and retention; roots, logs, IDs, and denominators remain separate.
* The tracked manifest and configs are preparation-only and disabled by default. The deterministic fake mode is an engineering fixture only; no provider/API call, Llama download, scientific experiment, Detector-v1 run, synthetic scientific data, or Study 1 mutation occurred. No accuracy, human-benefit, superiority, or generalization claim is permitted.
* Study 2B records `meta-llama/Llama-3.2-3B-Instruct` as a separate feasibility candidate only; license, hardware, cost, structured-output, and tool-support checks remain pending. Independent review and explicit run authorization are required before either condition is executed.

---

## 1. Quick Status

### 1a. Iris / PhD-proposal supervisor-closure workstream
* **September 3 strict one-page experiment design (pending supervisor review):** `docs/research/phd-proposal/2026-09-03-preliminary-human-intervention-experiment.en.md` maps the provisional SQ1 to three bounded paired cases. The local PDF is one A4 page, visually inspected, and hash-verified. It deliberately reports no intervention outcome because independent evaluation is still absent; EXP-005 remains 0/24.
* **September 2 checkpoint (2026-09-02, from the recording, machine transcript):** Iris ranked the gaps (preliminary results first, study detail second, presentation last) and narrowed the preliminary study to a descriptive demonstration of WHERE/WHEN a human could have been asked in the frozen run, identified automatically from existing per-stage signals; no accuracy comparison, no users this month, course data not synthetic data; the three supervisors stand in as humans. Her open question (agent 2 vs agent 3) must be settled in writing by measurement. Deliverables: Thu 09-03 one page (done: `2026-09-03-preliminary-study-design.en.md`/`.he.md`), Sun 09-06 two pages with results, Wed 09-09 proposal v2. EXP-045 inventory: Stage 2 misses 59/80 reference domain guidelines and has 12 unanswered advisor questions, 150/165 case files carry an Alternative fragment, Agent 4 queues 11/27 patterns; only Agent 4 has an escalation hook. Arnon: borderline but acceptable. Nothing approved.
* Branch `docs/iris-july29-phd-execution` preserves the ten July 29 evidence artifacts in `3d0beca`, the initial assurance tranche in `28ece6e`, the enhanced closure package in `18c0f2b`, and the next-step execution snapshot in `9a9279f`; production VEGO-AI behavior is unchanged.
* The bilingual-review-pending July 29 registers control all 19 requirements, 15 actions, and 10 questions; the closure audit has `44/44` locators, with **2 verified complete, 6 awaiting human acceptance, 22 partial, 5 open, and 9 blocked**.
* The recommended architecture is one umbrella RQ plus three subquestions: selective intervention, governed knowledge reuse, and evaluation/transfer. Iris and Arnon approval remains pending for the August 5 checkpoint.
* Plan A is a staged medical extension; Plan B completes the doctorate in software/modeling. Any unproved critical medical prerequisite on August 26 triggers Plan B for the September proposal.
* Proposal `v0.1`, the RQ decision pack, three-study contract, legacy crosswalk, claim register, RACI/RAID register, pre-read, and governance templates now form the first controlled tranche.
* A private Ali-owned nine-folder PhD working Drive and native six-tab literature Sheet exist. They have not been shared or sent; searches and screening are prepared but not yet executed.
* Ali, Iris, and Arnon are confirmed accepted on the recurring Wednesday 09:00-10:00 Asia/Jerusalem calendar event through October 7.
* The metadata-only MIMIC audit observed 25 CSVs totaling 39.65 GiB versus 26 official MIMIC-III v1.4 tables; `NOTEEVENTS` and provenance are unresolved. No patient rows were inspected.
* Medical readiness is **NO-GO at 0/6 entry gates**. EXP-005 remains blocked at 0/24 generalization-safe labels; no medical, accuracy, or generalization gain is claimed.
* A deterministic preliminary ledger covers S-0001–S-1195: 910 machine-linked segments and 285 conservative human-review placeholders. Separate Reviewer A/B and third-person adjudication inputs now feed a fail-closed merger; human bilingual/speaker review remains 0/1,195 segments plus 0/1 full-media record per reviewer, and no adjudicated output exists.
* The August 5 supervisor package is built locally as a 12-slide English core plus nine-slide appendix, 21/21 source-note sections, 21/21 native renders inspected, PDF export, and review workbook. The PPTX title/footer defects are corrected; the prior offline ZIP is explicitly stale and must be rebuilt only after rehearsal and freeze. Human timed/adversarial rehearsal, Ali release approval, sharing, and both access tests remain pending; this is not the candidacy deck.
* **August 12 checkpoint (2026-08-14, analyzed from the recording):** transcribed and cross-checked - see `docs/research/meetings/2026-08-12-supervisor-meeting.md` (`F1`-`F17`) and the bilingual `2026-08-12-post-meeting-plan.md`. Iris resequenced the open chapters: this week is literature-review-only (Chapter 2), methodology starts the week after; Chapter 2 must follow conventional literature-review structure rather than mirroring SQ1/SQ2/SQ3 (RQ-tagging stays an internal tool only); this week's literature scope is deliberately narrowed to one ACL-2026 paper's GitHub taxonomy corpus. `D-RQ-01`/`D-RQ-02`, `E6`, `E8`, the Plan A/B boundary wording, and the evidence-boundary wording were **not** raised or resolved on this call and remain open. A Clalit medical-track meeting is now confirmed for 2026-08-26.
* A canonical 29-work-package August 1-October 7 execution board, supervisor release runbook, Zoom reviewer operations guide, literature execution register, proposal v0.2 working draft, university-inquiry draft, and ten-sheet companion workbook now operationalize the next steps. Board structure passes with 18 blocked, 6 partial, and 5 planned work packages; no pending evidence was promoted.
* IRIS-EXP-01–10 now separate structure, readiness, and closure. All 10 pass structure mode on `main` as of merge commit `a78c1bf` (2026-08-04), verified in a fresh `git worktree add --detach` checkout (no gitignored artifacts, matching a bare CI clone) as well as the local machine. Readiness and closure still correctly fail while human review, rehearsal, delivery, decisions, acceptance, approval, and submission evidence are missing. Submission closure requires one exact schema-valid receipt hash-bound to authorization, package, external receipt, and issued certificate; the tracked template is `NOT_SUBMITTED`. September/October dates remain provisional pending official confirmation.
* CI (`supervisor-package.yml`) ran against this branch for the first time on 2026-08-03/04 (it never had run before) and surfaced 6 real, previously-undetected defects, all now fixed on `main`: (1) `render_manifest_structure_errors()` crashed with `FileNotFoundError` instead of failing closed when the gitignored PDF was absent; (2) `build_supervisor_source_manifest.py`'s two pytest tests crashed uncaught on gitignored `outputs/` workbooks instead of skipping; (3) `.gitattributes` had no `eol=lf` rule for `.jsonl`, so Windows `core.autocrlf` silently corrupted the raw ASR `machine.jsonl` transcript on any fresh checkout, breaking IRIS-EXP-05/07's hash checks; (4) IRIS-EXP-08's structure-mode checks wrongly included a check needing gitignored local evidence (moved to readiness); (5) the evaluation-phase hardening manifest (`release-manifest-v3.json`) was stale after the Iris schemas/tests merged in, and 4 unrelated tracked files (`pyproject.toml`, one `.mjs`, two `.ps1`) had working-tree bytes that had drifted from the declared `.gitattributes` policy in this specific long-lived local checkout; (6) `git diff --check` hygiene failures (3 files with a redundant trailing blank line, one file's intentional Markdown hard-break trailing spaces needing a `whitespace=-trailing-space` override) and a stale hash-bound provenance-manifest base-revision citation (`a55aee8` no longer had zero diff against the 20 frozen package paths; corrected to `bf45c98`, which does).

### 1b. VEGO-AI H-layer architecture-evaluation workstream
* Historical commits/tags contain the M1-M4B-1 reusable-human-judgment implementation. PR #8 records the thesis evidence release; PR #10 is the unified-runtime dependency; stacked PR #11 is the BigUI experiment-platform publication route. Live GitHub remains authoritative for review and merge state.
* Two constraints are active: offline H-layer architecture/experiment hardening and the EXP-005 human-label gate for the parked evaluation track.
* The machine-derived July 1 meeting record supports a **framework-first** direction pending participant confirmation. M-02 through M-05 have no recorded outcomes.
* July skills, prompt requirements, and six detailed specifications are **provisional drafts**, not approved interfaces. `allowed-touch-proposal.md` is also unapproved.
* **Research Loop:** Fifteen iterations (001-015) are accepted. Iterations 001-007 are historical/pre-manifest; 008-015 are manifest-backed. Iteration 015 (`HLAYER-UNIFIED-HARDENING-V1`) is the latest reliability-only snapshot, verdict `NEUTRAL`. It introduces legacy/unified/parity infrastructure but selects no empirical or model default. EXP-013-018 conformance remains offline-only and authorizes no live listener.
* **MediVARIA draft added (2026-07-04):** a provisional PhD/future-work proposal exists, but it is not supervisor-endorsed clinical work. MSc evidence remains education-only; there is no patient data or clinical-performance evidence in this repo.
* **Accuracy Verdict:** *Accuracy improvement cannot be evaluated yet* (0 generalization-safe real labels exist). The EXP-005 gate now gates the PARKED evaluation track only - not framework-track doc/spec work.
* **Thesis evidence package (2026-07-25):** a B0-B5 evidence ladder, canonical evidence snapshot, claim/chapter traceability, EXP-019..029 gated protocols, a 91-page review DOCX/PDF, and offline baseline-progress HTML are prepared and manifest-bound. This improves reliability and evaluation rigor; it does not establish an accuracy gain.
* **All-experiment benchmark (2026-07-26):** EXP-000..040 are evaluated with seven independent dimensions. Twenty-six experiments have current source-backed runs: 22 `MEASURED_PASS`, four `MEASURED_PARTIAL`, 13 `GATED_NOT_RUN`, and two `PARKED_NO_RUN`. `CurrentRunIndex-v1` identifies the current projection while 73 accepted bundles and 690 observations remain immutable history. Current accuracy evidence is still zero.
* **Evaluation phase (2026-07-28, Claude):** `scripts/run-full-evaluation.ps1` chains the 16-check gate -> benchmark -> per-component contribution report -> program overview/charts -> advisory analyst and PASSES end to end. `scripts/build_agent_contribution_report.py` gives every agent/component an evidence-based verdict (6 contributing, 2 partial, 1 not-yet-measurable): A1 fixture agreement 0.778-0.875 sits within the paper range, A2 guideline F1 0.267-0.545 sits below the paper's 0.70-0.88 (weakest measured link; H-layer churn triage is the designed compensation). `scripts/hlayer_llm_analyst.py` adds an ADVISORY-ONLY narrative (LLM via hardened client when a key exists, deterministic otherwise). `docs/research/iris-july1-implementation-matrix.md` maps all 12 July-1 directives to real implementations. Thesis snapshot, BigUI catalog, and research hub re-anchored to the new canonical revision. No accuracy claim anywhere; EXP-005 gate unchanged at 0/24.

---

## 2. Architecture State

```text
Original VEGO-AI Agent 1-4 pipeline (baseline)
  -> M1 Human Review Queue (routing triggers)
  -> M2 Human Feedback Manager (structured schema)
  -> M3 Human Judgment Memory (reusable knowledge storage)
  -> M4A Memory Advisory Layer (advisory retrieval, no reclassification)
  -> M4B-1 Deterministic Memory-Informed Comparison (parallel experimental comparison)
```
* **Git Repository:** Initialized; baseline pushed to private `AliHamed17/Vego-Ai`.
* **Git orientation:** PR #11 is stacked on PR #10 for the experiment benchmark and BigUI. Run live Git checks for branch, revision, PR state, approval, protection, and cleanliness; durable memory intentionally does not pin volatile values.
* **Publication records:** PR #6 covers earlier schema/test hardening; PR #8 covers the thesis evidence package; PR #10 covers unified contracts, parity, security, and provenance; PR #11 covers the results-first experiment observatory and benchmark.
* **Tags:** `milestone-m3-human-judgment-memory`, `milestone-m4a-memory-advisory`, `research-state-m4a-clean`, `research-state-results-dashboard`, `research-state-m4b1-deterministic-comparison`.

---

## 3. Active Blockers

| Blocker ID | Severity | Description | Next Step |
|------------|----------|-------------|-----------|
| **ISS-005** | Medium | Live Confluence sync blocked (Atlassian Rovo cloud access `724252a1-a5b7-45a5-b6ec-27a8292197ec` pending). | Use manual sync outbox files. |
| **ISS-006** | Medium | No completed generalization-safe expert labels for EXP-005 (parked evaluation track since 2026-07-04). | Supervisor/experts must label the blind sheet (27 rows; 24 generalization-safe candidates). |
| **ISS-007** | Medium | Evaluation leakage risk if same-pattern rows are claimed as generalization. | Keep same-pattern rows strictly for mechanism validation. |
| **ISS-012/013**| Medium | False-accuracy-narrative risk (synthetic vs real accuracy); weak evidence from one-reviewer. | Require κ & adjudication; quote real label status in reports. |
| **ISS-014** | High | M-01 through M-06 are unrecorded; no architecture/default/live authorization can be inferred. | Record explicit outcomes with Iris and Arnon; silence remains deferred. |
| **ISS-022** | High | July 29 Hebrew ASR, English translation, and speaker attribution remain machine-derived; the separate two-reviewer/adjudication interface is ready but contains 0/1,195 segment reviews and 0/1 full-media record per reviewer. | Complete independent Reviewer A/B returns and third-person disagreement adjudication through the fail-closed merge workflow before direct quotation or final attribution. |
| **ISS-023** | High | Medical readiness is 0/6 mandatory entry gates, with all accountable Plan A roles and approvals unproved. | Name owners and collect use-case, people, authorization, ethics/privacy, environment, and protocol evidence. |
| **ISS-024** | High | The official candidacy process, deadline, reviewer count, committee rules, and presentation requirements are unverified. | Obtain written confirmation from the department or Graduate Studies coordinator. |
| **ISS-025** | High | The shared MIMIC resource has 25 observed CSVs rather than 26 official tables and lacks canonical provenance. | Reconcile the manifest inside an authorized VDI only after all six entry gates pass. |
| **ISS-026** | Medium | The private PhD Drive and literature Sheet are not shared or access-tested. | Ali reviews the exact package, then explicitly authorizes sharing and recipient access checks. |
| **ISS-027** | High | The current August 5 PPTX/PDF, source notes, control appendix, workbook, and automated/render QA exist locally; human timed/adversarial rehearsal, Ali release approval, delivery, and Iris/Arnon access tests remain unproved. Candidacy presentation rules and its separate deck also remain unverified. | Ali reviews the exact frozen package; run and record both human rehearsals; correct and rerender if needed; then share only with authorization and record two recipient access tests. |

| **ISS-028** | Medium | The prior local offline ZIP contains the superseded PPTX/PDF and is marked stale/invalidated; readiness now verifies ZIP member hashes instead of trusting a filename or manifest hash alone. | Rebuild and re-hash the ZIP only after the exact package passes human rehearsal and RG-04 freeze. |
| **ISS-029** | Resolved (2026-08-04) | 2026-08-03 independent audit (Claude) found and fixed: 9/31 (then 10/32, after adding a missing gap-ledger row) stale provenance-manifest hashes, 4 stale "verified" hashes in the execution control board, a missing detached source manifest causing 2 test failures, a false "Structure passes" claim (IRIS-EXP-07/08 both FAILed structure mode), R-04's contradictory/unsupported appendix slide mapping, A-03/A-06's incomplete appendix slide mapping, an undefined control-status vocabulary on the deck's claim-states slide, and a G1-G6 label collision between the medical gates and `THESIS_ACCURACY_EVIDENCE_ADVANCEMENT_PLAN.md` (renamed to `AG0-AG6` there). All fixed; PPTX rebuilt as v10 (`7765132B...`), PDF/renders/manifests regenerated. The tree was committed and the provenance base revision was corrected to `bf45c98` (zero-diff ancestor for all 20 frozen package paths); all 10 IRIS-EXP checks now pass structure mode on `main`. | Closed. See the CI-hardening bullet above (6 further defects found once real CI ran) for what shipped alongside this. |

---

## 4. Next Action
1. **Ali review gate:** inspect the exact August 5 pre-read, corrected PPTX/PDF, RQ pack, proposal, Drive structure, literature Sheet, release runbook, and execution workbook before any external sharing.
2. **August 5 decision gate:** obtain and record Iris/Arnon decisions on the one-plus-three hierarchy, study map, Plan A/B labels, literature categories, medical owner, Penina dates, and official-process owner.
3. **Presentation gate:** Ali reviews the exact frozen local package; complete dated timed and adversarial human rehearsals, correct/rerender any defects, and record authorized delivery plus Iris/Arnon access tests without copying simulated outcomes into the real decision log.
4. **Literature tranche:** execute the recorded searches, deduplicate, screen, verify identities/claims, and prepare the August 12 synthesis without treating tools as evidence.
5. **Transcript gate:** complete bilingual and speaker review; continue using paraphrases only until then.
6. **EXP-005 gate:** appoint two independent reviewers plus an adjudicator and collect the 24 safe labels; do not infer or prefill labels.
7. **Medical gate:** keep all row-level work blocked at 0/6 and collect only documentary proof for the six prerequisites.
8. **August 26 fallback:** run the medical go/no-go review and default the September proposal to Plan B if any critical prerequisite remains unproved.
9. **Administrative gate:** obtain written confirmation of the official candidacy process and rebaseline within one working day if required.

---

## 5. Working Agreement
* **Prompt Start:** Run `.\scripts\agent-memory-start.ps1` and read `docs/agent-memory/compiled-memory-t1.md`.
* **Prompt End:** Run `.\scripts\agent-memory-finish.ps1` with conciseness when file changes or decisions happen.
* **Guards:** Run `python scripts\check_evidence_consistency.py` before any review/claim update (must PASS).
* **Boundaries:** Keep Agent 4, M4B-2, LLM/API calls, and baseline output overwrites blocked.
* **Git:** Record the actual dirty/clean state; never assume cleanliness. Do not stage unrelated local directories or data zones.

---

## 6. Deep Context (Expandable)

<details>
<summary><b>6.1 Source, Run, and Schema Context</b></summary>

* **Original Package:** Extracted to `VEGO-AI/`.
* **Framework Code:** `VEGO-AI/framework/human_feedback_manager.py`, `memory_advisor.py`, `build_results_dashboard.py`.
* **Tests:** The 2026-07-26 benchmark pass added source, schema, run-history, comparison, report, and browser tests. Final unsuppressed suite counts must be taken from the latest verification record rather than copied from this orientation page.
* **Schemas:** runtime schemas remain unchanged; the evidence package adds document-level schemas for the evidence snapshot, gold labels, policy candidates, and evaluation-run manifests.
* **Latest Run ID:** `20260614-122150` (27 comparisons, 0 differences, 2 review flags, 0 changes to baseline behavior).
</details>

<details>
<summary><b>6.2 Evaluation & Experiment Details (EXP-001...040)</b></summary>

* **EXP-001 (Mechanism):** 27 rows, 3 same-pattern labels, 0 generalization-safe labels.
* **EXP-002 (Generalization candidates):** 24 safe candidate rows identified for expert labeling.
* **EXP-003 (Accuracy evaluation):** Tooling/harness ready. Blind sheets generated under `reports/generated/exp003/`.
* **EXP-004 (Sensitivity):** Synthetic policy screening only (no real evidence).
* **EXP-005 (Real-label gate):** Tooling generates blind reviews, reliability stats, and kappa metrics. Closed until expert labels are added.
* **EXP-019..027 (Preregistered next phase):** reviewer calibration, independent labeling, development-only baseline error analysis, routing/retrieval validity, deterministic policy development, one-time sealed holdout, external education replication, human-effort evaluation, and ablation/robustness. They are planned protocols, not completed evidence.
* **EXP-030..040:** BigUI integrity, gated human-value protocols, runtime parity, topology trade-offs, authority fault injection, operational scale, paper reconciliation, architecture scorecard, valid cross-experiment deltas, and thesis-claim readiness. Only source-backed mechanism/offline results are populated; human and empirical cells remain empty.
</details>

<details>
<summary><b>6.3 Confluence & Dashboard Infrastructure</b></summary>

* **Target URL:** `https://alih10j.atlassian.net/wiki`
* **Cloud ID:** `724252a1-a5b7-45a5-b6ec-27a8292197ec`
* **Local outbox:** `docs/confluence/outbox/` containing manual sync files.
* **Dashboard Snapshots:** Generated by `scripts/build-dashboard-snapshot.ps1`.
* **E2E Progress Dashboard:** Generated by `scripts/build-e2e-progress-report.ps1`.
</details>

<details>
<summary><b>6.4 PhD Research Trajectory (Direct Track)</b></summary>

* **Topic:** Reusable human judgment for auditable, reliable, and transferable human-AI co-reasoning in agentic assessment.
* **Canonical working hierarchy:** one umbrella RQ plus SQ1 selective intervention, SQ2 governed knowledge reuse, and SQ3 evaluation/transfer.
* **Study map:** Study 1 intervention architecture; Study 2 judgment lifecycle; Study 3 evaluation and transfer.
* **Plans:** Plan A adds a gated medical transfer pilot; Plan B completes all questions through software/modeling and non-clinical replication.
* **Control interfaces:** master traceability, RQ crosswalk, three-study contract, five-state claim register, six-gate medical scorecard, weekly pre-read, and decision/change log.
* **Decision dates:** August 5 supervisor checkpoint; August 26 medical go/no-go; September/October proposal checkpoints are provisional pending official confirmation.
</details>


## Progress

# Progress

Track milestones, current work, and next steps here.

> **Executive at-a-glance view:** [`docs/PROGRESS_TRACKER.md`](../PROGRESS_TRACKER.md) — single-page phase
> board, milestones, experiments, thesis status, gates, and the human-gated critical path. This file remains
> the full chronological detail behind it.

## Milestones

| 2026-09-04 | Tasks 2–5 Q&A communication contract and offline observer | PARTIAL / pre-run review required | Added `qa-communication-event-v1`, privacy-safe append-only recorder, deterministic episode projection, live extractor support, baseline terminology freeze, and offline route/parity tests. Protected orchestrator wiring remains unmodified; all four settings are blocked by absent case-model directories; no live LLM/API run. |

| 2026-09-04 | Task 1 original interaction-log recovery audit | NOT FOUND locally / contact decision pending | Deterministic read-only inventory covered repository, ignored/untracked material, supplied archives, Downloads, Claude workspace, OneDrive Documents, mounted VEGO-AI Drive, and Codex attachments. No original/probable log; historical code/logs indicate conditional full-content logging. Q&A baseline 12/30 unchanged; no rerun or API call. |

| 2026-09-04 | Iris Q&A task-plan source and RTL verification hardening | Implemented / push and CI pending | Canonical JSON now drives Markdown/DOCX/PDF; equality tests cover all eight tasks and summary rows; send-gate and interaction-log semantic guards added. Approved supervisor wording unchanged; no experiment executed. |

| 2026-09-03 | Q&A escalation detection observability scaffold | Implemented / human validation pending | Added a read-only frozen Q&A extractor, confidence-separated feature inventory, transparent alert scaffold, and three blind reviewer-sheet generators. Canonical snapshot: 12 final questions, 0 persisted answers, 12 unanswered; 30 round-snapshot questions. No detector performance or intervention result is claimed. |

| Date | Milestone | Status | Notes |
| --- | --- | --- | --- |
| 2026-08-24 | Strict scored review of the 2026-08-23 consolidated doctoral proposal PDF | Delivered to Ali | Score 75/100; see `docs/research/phd-proposal/doctoral-proposal-2026-08-23-strict-review.md`. Cross-referenced against the v13/v8/v15 verification reports and external citation checks. Headline gaps: ACL taxonomy exercise still absent (4th consecutive artifact, ISS-040); model/pattern count mismatch now uncontested where v13 at least caveated it (ISS-041); minor citation/figure-order defects. Separately found and fixed a pre-existing CI-red `main` (pip PYSEC-2026-3721, cascading through the BigUI/thesis-evidence build chain) — see ISS-039 and the "Build-Chain Hash-Cascade Fix Pattern" decision. |
| 2026-08-01 | Iris next-step execution program operationalized | Implemented locally / human and external gates pending | Commit `9a9279f` adds a canonical 29-work-package control board and fail-closed validator, reviewer batch operations/validator, supervisor release runbook, literature execution register, university inquiry draft, proposal v0.2 working draft, ten-sheet execution workbook, and exact-package implementation manifest. It corrects native appendix titles, slide-11 footer, and machine-alignment wording in the August 5 deck and invalidates the superseded offline ZIP. Structure passes after provenance binding; readiness and closure intentionally remain non-zero. |
| 2026-08-01 | Enhanced Iris Zoom-to-submission closure tranche | Implemented locally / human and external gates pending | Commit `18c0f2b` adds deterministic S-0001–S-1195 preliminary disposition CSV/JSON and review workbook, a separate fail-closed two-reviewer/adjudication merge path, four-dimensional control state, IRIS-EXP-05–10, SCI-EXP crosswalk, external-fact/certificate controls, schema-bound submission receipt, and `structure`/`readiness`/`closure` validation. It also adds a 12-slide English core plus nine-slide appendix with 21/21 source-note sections; the PDF, native-render QA, and workbook remain local hash-bound derivatives. The earlier offline ZIP was later invalidated by presentation corrections. Structure passes only after current provenance binding; readiness/closure remain non-zero until human review, rehearsal, delivery, supervisor acceptance, approval, and submission evidence exist. |
| 2026-07-30 | July 29 supervisor evidence preserved | Done | Ten machine-derived working-evidence artifacts preserved on `docs/iris-july29-phd-execution` in commit `3d0beca`; human bilingual/speaker review remains open. |
| 2026-07-30 | Doctoral requirements-closure control package | Done / supervisor gates pending | Implemented the 19/15/10 master register, RQ decision pack, three-study contract, legacy crosswalk, claim/RACI/RAID controls, proposal `v0.1`, pre-read, and decision templates; supervisor approval is pending. |
| 2026-07-30 | Iris requirements assurance and presentation controls | Done / human runs pending | Commit `28ece6e` adds the 44-item call-time/evidence/acceptance audit, 12-checkpoint video-call checklist, IRIS-EXP-01..04 protocols, deterministic validator/tests, and weekly propagation preflight; synchronized SQ wording and removed an unsupported four-hour-completion claim. Traceability/claim checks pass; live rehearsal and first weekly cycle are not run. |
| 2026-07-30 | Private PhD Drive and native literature workbook | Done (initial tranche) | Created the Ali-owned nine-folder structure and six-tab Google Sheet; external sharing, database searches, screening, and access verification remain pending. |
| 2026-07-30 | MIMIC metadata/governance tranche | Done (metadata only) | Recorded 25 CSVs, 39.65 GiB, missing `NOTEEVENTS`, provenance gaps, three data zones, and a 0/6 medical readiness verdict without inspecting patient rows. |
| 2026-07-30 | Recurring supervision calendar acceptance | Done | Ali accepted; Ali, Iris, and Arnon are confirmed accepted for Wednesday 09:00-10:00 Asia/Jerusalem through October 7. |
| 2026-06-11 | Basic shared memory created | Done | Added Codex and Claude root instructions plus memory logs. |
| 2026-06-11 | Memory upgraded for per-prompt progress tracking | Done | Added current-state and progress tracking so future prompts can orient quickly. |
| 2026-06-11 | Scripted prompt memory pull/update added | Done | Added PowerShell scripts to generate compiled memory and append prompt summaries. |
| 2026-06-11 | PhD research workspace architecture added | Done | Added source, research, experiment, data, paper, thesis, and reproducibility scaffold. |
| 2026-06-11 | Git repository initialized | Done | Added `.gitignore` and initialized Git; baseline commit pending. |
| 2026-06-11 | Safe GitHub baseline published | Done | Pushed safe code/docs baseline to private `AliHamed17/Vego-Ai` on `main`. |
| 2026-06-11 | Claude bootstrap prompt added | Done | Added a paste-ready Claude startup prompt that enforces shared memory, architecture, Git, and safety rules. |
| 2026-06-11 | Workspace architecture diagram added | Done | Added a GitHub-rendered Mermaid diagram and linked it from the architecture docs and root README. |
| 2026-06-11 | Human feedback manager files added | Done | Added structured human-feedback schema, example feedback input, manager module, and review item feedback/status fields. |
| 2026-06-12 | Human feedback manager docs/tests added | Done | Added Milestone 2 documentation and tests; full VEGO-AI test suite passes with 30 tests. |
| 2026-06-12 | Research OS and Confluence sync infrastructure added | In progress | Added research audit registers, EXP-000 folder, Confluence sync docs/config/outbox builder, and research health checks. |
| 2026-06-12 | Confluence live target configured locally | In progress | Local config targets page `294914`; live sync blocked until Atlassian Rovo cloud access is granted. |
| 2026-06-12 | M3 Human Judgment Memory published | Done | Verified 45 tests, compileall, health checks, secret/forbidden audits, then pushed commit `5e109e5` to `origin/main`. |
| 2026-06-12 | Reusable human judgment research story hardened | Done | Updated research plan, methodology, evaluation plan, literature taxonomy, thesis outline, claim/evidence table, roadmap, risks, and EXP-001 shell. |
| 2026-06-12 | M4A Memory Advisory Layer reviewed and merged | Done | Reviewed PR #2, added edge-case fixes, posted review report, and squash-merged as `ecd0972`. |
| 2026-06-13 | M4A reproducibility tags and Claude handoff prepared | Done | Tagged M3, M4A, and research-state commits; added post-merge confirmation and Claude M4B handoff prompt. |
| 2026-06-13 | Dashboard/KPI tracking layer added | Done | Added tracked progress, KPI, and results dashboards and generated a fifth Confluence outbox page for progress tracking. |
| 2026-06-13 | Dashboard health gate added | Done | Added `scripts/dashboard-health.ps1` and wired it into research/project health plus agent end-of-prompt workflow. |
| 2026-06-13 | Dashboard runtime snapshot added | Done | Added `scripts/build-dashboard-snapshot.ps1`; Confluence wiki builds now embed a fresh ignored snapshot with repo, KPI, active-work, outbox, and live-sync status. |
| 2026-06-13 | Manual Confluence sync pack added | Done | Added a generated, ignored manual sync pack with page bodies, target metadata, and hashes for approved fallback publishing. |
| 2026-06-14 | M4B-1 conditional implementation contract recorded | Done | Added deterministic M4B-1 rules, leakage guard, schema expectations, Codex isolation, and Claude branch/PR handoff. |
| 2026-06-14 | Offline VEGO-AI results dashboard merged | Done | Added static dashboard generator, snapshot schema, docs, tests, and ignored generated reports; merged as `cf78d2d`. |
| 2026-06-14 | M4B-1 deterministic comparison merged | Done | PR #4 merged as `944c922`; tag `research-state-m4b1-deterministic-comparison` exists. |
| 2026-06-14 | M4B schema hardening PR opened | In review | PR #6 adds nested required fields and schema regression coverage only. |
| 2026-06-14 | Local no-key execution/results package generated | Done | Created local configs, generated M1-M4A/M4B outputs under `VEGO-AI/runs/20260614-122150/`, rebuilt dashboard, and wrote ignored `RUN_SUMMARY.md`. |
| 2026-06-14 | Visualizer model/result mismatch fix opened | In review | PR #7 adds exact case matching, stale-model clearing, mismatch banner, helper tests, filters, and read-only research panels. |
| 2026-06-14 | Full system validation report generated | Done | Tracked report `VEGO-AI/reports/system_validation_report.md` says PASS after governance cleanup; all functional and health checks pass. |
| 2026-06-14 | QA governance warnings fixed | Done | Added narrow research-health allowlist, restored local baseline tracking branch, and prepared `system_validation_report.md` as a tracked validation artifact. |
| 2026-06-14 | Visualizer UX refresh merged and tagged | Done | PR #7 passed real-display GUI validation, merged as `78b261e`, and tag `research-state-visualizer-ux-clean` points to the merge commit. |
| 2026-06-14 | Shared Claude/Codex state report added | Done | Added `docs/agent-memory/shared-state-report.md` and wired it into compiled memory/startup instructions. |
| 2026-06-14 | Evaluation phase scaffold added | Done | Added `docs/research/evaluation-report.md`; M4B-1 is treated as implemented/evaluation-pending, with release bundle available for review. |
| 2026-06-14 | EXP-001 initial mechanism/readiness evaluation run | Done | Generated ignored `reports/generated/exp001/` tables: 27 comparisons, 0 M4B-1 classification changes, 2 review-after-memory flags, and 0 generalization-safe expert labels. |
| 2026-06-14 | EXP-002 expert labeling package generated | Done | Generated ignored `reports/generated/exp002/` package: 27 rows, 24 generalization-safe candidates, 3 existing same-pattern labels, and 27 recommended labeling targets. |
| 2026-06-16 | Supervisor Zoom demo package generated | Done | Created ignored `artifacts/supervisor_demo_2026-06-17/` with 20-slide deck, brief, demo script, questions, screenshot checklist, figures, and tables for the 2026-06-17 supervisor session. |
| 2026-06-16 | EXP-003 accuracy-improvement evaluation tooling added | Done | Added full/blind labeling prep, expert-label protocol, strict accuracy gates, error-analysis/accuracy summary tooling, and ignored EXP-003 outputs. Initial EXP-003 has 0 safe expert labels, so accuracy improvement cannot be evaluated yet. |
| 2026-06-16 | Results and accuracy full report generated | Done | Created ignored `artifacts/RESULTS_AND_ACCURACY_FULL_REPORT.md` and linked it from `docs/research/evaluation-report.md`; strict verdict remains no proven accuracy improvement, with 0 generalization-safe expert-labeled rows and 0/27 memory-informed classification changes. |
| 2026-06-16 | Synthetic accuracy simulation generated | Done | Created ignored `artifacts/SYNTHETIC_ACCURACY_SIMULATION_REPORT.md` and `reports/generated/synthetic_accuracy_simulation/`; current M4B-1 has 0 synthetic accuracy delta, while counterfactual flips show synthetic-only possible deltas that are not real evidence and must not be reported as accuracy improvement. |
| 2026-06-16 | EXP-004 policy-sensitivity harness added | Done | Added reusable synthetic/candidate-policy simulation tooling and docs. Initial run shows current M4B-1 remains `+0.00 pp`; aggressive candidate policies can help or harm under different synthetic truth scenarios, so real labels remain required. |
| 2026-06-17 | EXP-005 real-label accuracy gate added | Done | Added supervisor/expert label-review tooling, validation, real-label policy gate outputs, and docs. Initial run has 27 rows, 24 safe candidates, 4 safe memory disagreements, 2 review-after-memory cases, 0 valid labels, and gate status `Accuracy improvement cannot be evaluated yet.` |
| 2026-06-21 | VEGO workbench launcher added | Done | Added one-command local launcher for dashboard, EXP-005 labels, optional GUI, optional wiki outbox, and optional health checks. |
| 2026-06-21 | VEGO topology report exported | Done | Added reusable HTML/PDF topology exporter and generated ignored `artifacts/topology-export/VEGO_TOPOLOGY_FLOW_REPORT.html` and `[PDF omitted]`. |
| 2026-06-21 | Baseline architecture overlay exported | Done | Added reusable overlay exporter and generated ignored `artifacts/topology-export/VEGO_BASELINE_OVERLAY_REPORT.html` and `[PDF omitted]` showing M1-M4B-1/EXP-005 on top of the paper architecture. |
| 2026-06-22 | Strategic review and hardening plan added | Done | Consolidated current flow, vulnerabilities, evidence gates, and next-step strategy in `docs/research/strategic-review-and-hardening-plan.md`; no VEGO behavior changes. |
| 2026-06-22 | EXP-005 evidence coverage enhanced | Done | Added adjudication sheet, evidence verdict, reproducibility manifest, reviewer-reliability summary, and thesis/KPI/publishability alignment; no VEGO behavior changes. |
| 2026-06-22 | EXP-005 synthetic trial interpreted | Done | Ran a synthetic-only EXP-005 pipeline trial, generated ignored synthetic outputs, and added a tracked design-only policy candidate review. Current M4B-1 remains 0/27 classification changes and 0.00 pp synthetic accuracy delta. |
| 2026-06-23 | Supervised Codex next-step loop added | Done | Added `scripts/run-codex-next-step.ps1` and docs so "continue" prompts run one safe cycle, stop at EXP-005/protected-path gates, and write ignored loop summaries. |
| 2026-06-23 | Project review architecture added | Done | Added memory-connected review state, review architecture docs, and `scripts/run-project-review.ps1` so review/continue prompts produce structured verdicts and claim gates. |
| 2026-06-23 | Progress visualization dashboard added | Done | Added refreshable Mermaid and local HTML progress visualizations generated from progress, KPI, and dashboard source files. |
| 2026-06-23 | Progress update architecture added | Done | Added the memory, dashboard, Confluence, health-check, and 4-hour thread update architecture. |
| 2026-06-23 | Progress update architecture diagram added | Done | Added a dedicated architecture-facing diagram for the progress update flow under `docs/architecture/`. |
| 2026-06-23 | E2E progress report and web dashboard added | Done | Added a generated full report and local static web page tying memory, dashboards, experiment summaries, review state, Git status, Confluence outbox, and 4-hour updates together. |
| 2026-06-23 | HITL resource pack added | Done | Added curated Human-in-the-Loop / Human-AI collaboration sources, BibTeX, tool-fit matrix, ignored downloads, and a download helper script. |
| 2026-06-24 | Alignment and structure hardening added | Done | Added the alignment control checkpoint, thesis structure map, and evidence consistency guard; no VEGO behavior changes. |
| 2026-06-29 | Chapter 7 current-evidence draft added | Done | Added an honest Experimental Results chapter that reports mechanism/readiness evidence and keeps quantitative accuracy results blocked until EXP-005 has real labels. |
| 2026-06-29 | Supervisor EXP-005 approval pack added | Done | Added a supervisor-first approval document and tightened the expert-labeling protocol so the next human action is explicit before reviewer outreach. |
| 2026-06-29 | PhD thesis optimization and Claude collaboration control added | Done | Added a PhD research trajectory page, Claude thesis collaboration prompt, and updated the research plan away from stale M4B implementation tasks. |
| 2026-06-29 | Doctoral capability alignment hardened | Done | Added a PhD capability stack and maturity ladder, updated the Claude prompt, alignment control, architecture map, and README so future work extends the baseline through explicit research capabilities. |
| 2026-07-04 | July 2026 supervisor redirect package implemented | Done | From the 2026-07-01 meeting transcript: meeting notes, active extension plan (H-layer framework first, evaluation parked), July-15 deliverables (skills map + prompt requirements), separated framework/evaluation diagrams, taxonomy July-2026 section, PhD idea log. Docs-only; no VEGO-AI source changes. |
| 2026-07-04 | MediVARIA medical-domain study plan integrated | Done | One-page IIA proposal (TRL 3->5) archived (ignored); tracked study plan with VEGO-AI/H-layer mapping, MV-RQ1-6, MV-P0..P5 phases, clinical claim boundaries, thesis-enhancement checklist, and July-15 agenda additions; wired into idea log, redirect plan, thesis map, PhD plan, taxonomy, skills-map open questions. Docs-only. |
| 2026-07-05 | H-layer mechanism experiment suite EXP-006..008 implemented and run | Done | Read-only replay: EXP-006 reported `11 queue items / 481 heterogeneous reconstructed lifecycle events`; this is a count ratio only, with no event-level visibility inference or linkage. E3/E9 gaps remained. EXP-007 replay found coarse signals; EXP-008 found 167 unstable guidelines, 160 not represented in the old queue. No VEGO-AI file touched. |
| 2026-07-10 | H-layer Phase P2 detailed specification drafts and offline demo scaffold produced | Specs provisional; demo isolated | Six specification drafts remain design aids pending M-02..M-05. The July 10 scaffold is a runnable offline interaction demo only: session-scoped output, deterministic checks, no semantic checker, no trusted-memory eligibility, and no runtime/evidence claim. |
| 2026-07-10 | Research Loop Iterations 4, 5, and 6 completed | Done | Iteration 4 (baseline comparison run), Iteration 5 (M-B5/M-B6 metrics scaffold), and Iteration 6 (H5 subject-level event bundling in `exp007_dosage_replay.py` and `hlayer_iteration_compare.py`) executed. This quantifies subject-level grouping workload reductions across settings. |
| 2026-07-10 | Research Loop Iteration 7 accepted | Done / provisional evidence | EXP-009/010 prototype scripts produced assumption-driven `SYNTHETIC_NOT_HUMAN` outputs. They expose rule behavior but do not validate real expert-error handling or approve M-04 choices. |
| 2026-07-10 | Legacy `iter_008` snapshot generated | Not accepted | The ignored pre-hardening snapshot has no accepted protocol-changing hypothesis/verdict and does not count as iteration 8. Preserve it for audit; the next accepted iteration requires atomic runner hardening and generated evidence. |
| 2026-07-10 | Phase 0 H-layer truth/governance reconciliation | Complete | Reconciled provisional status, experiment gates, real hook symbols, protected-path fingerprints, and allowed-touch authorization boundary without changing VEGO-AI runtime behavior. Ten iterations are accepted: iteration 009 is metric/contract repair and iteration 010 is a reliability-only rerun; both are NEUTRAL. |
| 2026-07-10 | EXP-013..018 offline conformance fixtures implemented and independently rerun | Validator passed | Six CLIs exited 0 with stable run IDs/hashes; 24 focused tests and the 19/19 offline validator passed. Claim scope remains fixture mechanism/safety only; atomic iteration-008 promotion/verdict is a separate gate. |
| 2026-07-10 | Hardened reliability iteration 008 accepted | Done / NEUTRAL | Atomically promoted run `hlayer-20260710T171143Z-2a66e71a3f` with per-experiment/suite/iteration manifests, deferred decision snapshot, validated EXP-005 gate at 0 safe labels, repaired EXP-012 canonical cross-check, and no protected runtime diff. Legacy iter-008 snapshots are quarantined. |
| 2026-07-10 | Offline metric-and-contract iteration 009 accepted | Done / NEUTRAL | Run `hlayer-20260710T175523Z-ab5175fd07` repaired ObservationRecord boundaries, workload denominators, transaction bundling, and Pareto sweeps: 481 captured + 20 explicit gaps; `threshold_sev2` event/transaction load 0.799/0.796, weighted/high-severity coverage 0.981/1.0; K30/K35 capture 0.75/0.85. Aggregate coverage/load target remains unmet; no default selected. |
| 2026-07-10 | Separate offline conformance suite accepted | Done / offline-only | Run `HLAYER-CONFORMANCE-7a426ce3a5336b158606`, normalized `7a426ce3a5336b15860687f1a7f69da241e88b60b0e1b23f95a1d69b21ebba27`, decision snapshot `681102be14d0aed854dd384fe0f18cc62081d46dfbf64ab6f1a3b47fe92cb0c1`; no runtime authority. |
| 2026-07-10 | Reliability iteration 010 and next-step reconciliation accepted | Done / NEUTRAL | Iteration 010 (`hlayer-20260710T183658Z-9199809f30`) snapshots the unchanged six-experiment replay suite. Status surfaces were corrected so it is not represented as an interactive-demo or performance iteration. |
| 2026-07-10 | Offline Vector 1 proposal generator and supervisor demo safety hardening | Done / proposal-only | Added deterministic eligibility/group/conflict/provenance artifacts with zero current candidates; isolated demo feedback from adjudication, disabled semantic checking, rejected protected output paths, and kept every demo/candidate record non-runtime and non-trusted. |
| 2026-07-11 | Reliability iteration 011 and feedback generalizer proposal implemented | Done / NEUTRAL | Iteration 011 (`hlayer-20260711T102518Z-1ecc5dc68f`) snapshots the updated replay suite with decision snapshot synchronizations and the new offline `feedback_generalizer.py` script. |
| 2026-07-11 | Reliability iteration 012 and supervisor pre-read synchronization completed | Done / NEUTRAL | Iteration 012 (`hlayer-20260711T123453Z-6cca11a0c8`) snapshots the updated replay suite with decision register snapshot synchronizations. |
| 2026-07-24 | Thesis accuracy-evidence advancement package prepared | Done / pending human evidence | Added a canonical evidence snapshot and schemas, B0-B5 evidence ladder, claim/chapter traceability, EXP-019..027 preregistrations, reviewer and supervisor decision protocols, updated thesis chapters, an offline progress explainer, and an 87-page DOCX/PDF review draft. Current evidence remains 0/24 independent safe labels and 0/27 comparison changes; no accuracy or generalization claim is authorized. |
| 2026-07-25 | Unified runtime and security hardening release verified | Done / governance-gated | Added canonical contracts, explicit legacy/unified/parity modes, fail-closed publication and comparison, locked dependencies, model/security provenance, and a 91-page manifest-bound review package. Final review hardening passes 113 VEGO-AI tests, 113 research tests plus 7 subtests, 46 offline tests, 18/18 evidence checks, controlled 27-row parity with 0 changes, dependency audits, and offline browser checks. Merge remains gated by independent approval and enforceable main protection. |
| 2026-07-28 | Evaluation phase: component verdicts, advisory analyst, Iris matrix, full-eval runner | Done / no accuracy claim | `scripts/run-full-evaluation.ps1` PASSES end to end (16-check gate + benchmark + contribution + overview + analyst). Per-component verdicts: 6 contributing, 2 partial, 1 not-yet-measurable; A1 fixture agreement 0.778-0.875 within paper range, A2 guideline F1 0.267-0.545 below paper 0.70-0.88 (weakest measured link). Advisory-only LLM analyst added with deterministic fallback. All 12 Iris July-1 directives mapped to implementations in `docs/research/iris-july1-implementation-matrix.md`. Thesis snapshot, BigUI catalog, and research hub re-anchored to the new canonical revision. |


## Active Work

| ID | Started | Status | Summary | Next Step |
| --- | --- | --- | --- | --- |
| TASK-001 | 2026-06-11 | Done | Durable revert support started by adding `.gitignore`, initializing Git, and pushing a safe baseline. | Continue using commits for every meaningful change. |
| TASK-003 | 2026-06-11 | Open | Audit data sensitivity and provenance. | Review `VEGO-AI/inputs/`, `[controlled case-model path omitted]`, `[controlled analysis path omitted]`, and the IRB-related PDF. |
| TASK-004 | 2026-06-11 | In progress | Map existing paper/package results to experiments. | Continue `EXP-000-existing-packaged-results-audit` without copying controlled artifacts into Git. |
| TASK-005 | 2026-06-12 | Blocked | Keep curated Confluence wiki current. | Grant Atlassian Rovo access to cloud `724252a1-a5b7-45a5-b6ec-27a8292197ec`, then create/update child pages and store page IDs in local config. |
| TASK-006 | 2026-06-12 | Done | Design and merge M4B-1 memory-informed parallel comparison. | Keep M4B-1 experimental and run EXP-001/C4B before making improvement claims. |
| TASK-007 | 2026-06-13 | Done | Release M1-M4A + dashboard + M4B-1 artifact bundle for external technical review. | Use GitHub release assets for review; do not treat the bundle as empirical proof. |
| TASK-008 | 2026-06-13 | Open | Keep progress, KPI, and results dashboards current. | Update `docs/dashboards/` whenever progress, KPI values, validated results, or Confluence tracking status changes. |
| TASK-009 | 2026-06-13 | Open | Keep dashboard/wiki tracking health verified. | Run `.\scripts\dashboard-health.ps1 -RequireOutbox` after every Confluence outbox build. |
| TASK-010 | 2026-06-13 | Open | Keep runtime dashboard snapshot fresh. | Run `.\scripts\build-confluence-wiki.ps1` after memory/dashboard updates; it regenerates `docs/dashboards/status-snapshot.generated.md`. |
| TASK-011 | 2026-06-13 | Open | Keep manual Confluence sync pack fresh while live access is blocked. | Run `.\scripts\build-confluence-wiki.ps1`; it regenerates `docs/confluence/manual-sync-pack.generated.md`. |
| TASK-012 | 2026-06-14 | Done | Add local/offline visual metrics dashboard for VEGO-AI result artifacts. | Keep generated `VEGO-AI/reports/results_dashboard/` ignored. |
| TASK-013 | 2026-06-14 | Done | Harden M4B nested schema requirements. | PR #6 merged. |
| TASK-014 | 2026-06-14 | Done | Fix research-health allowlist for the tracked dashboard generator. | Narrow allowlist added; `project-health`, `research-health`, and `dashboard-health` pass. |
| TASK-015 | 2026-06-14 | Done | Fix VEGO-AI visualizer model/result mismatch UX. | Preserve the no-silent-mismatch and read-only research-panel boundaries in future visualizer work. |
| TASK-016 | 2026-06-14 | Open | Complete EXP-001 expert-label evaluation. | Add held-out/cross-setting expert labels, rerun `.\scripts\build-exp001-evaluation.ps1`, and update the evaluation report with generalization-safe metrics. |
| TASK-017 | 2026-06-14 | Open | Fill EXP-002 expert labeling package. | Human/supervisor should label at least 20 rows, preferably all 27 current rows, then rerun evaluation with leakage-aware partitions. |
| TASK-018 | 2026-06-16 | Done | Prepare supervisor Zoom package for 2026-06-17. | Use the ignored package locally during the meeting, capture supervisor decisions, and convert accepted labels/decisions into tracked research docs afterward. |
| TASK-019 | 2026-06-16 | Open | Collect EXP-003 independent expert labels. | Fill the blind/full EXP-003 sheets with at least 20 generalization-safe labels before any accuracy-improvement claim or M4B-1 policy refinement. |
| TASK-020 | 2026-06-16 | Open | Use EXP-004 to screen policy candidates after real labels exist. | Rerun `.\scripts\build-policy-sensitivity-simulation.ps1` after EXP-003 has real labels; treat current synthetic results as pipeline/risk screening only. |
| TASK-021 | 2026-06-17 | Open | Collect EXP-005 supervisor/expert labels through the real-label gate. | Fill `reports/generated/exp005_label_review/exp005_label_review_blind.csv`, then run `.\scripts\build-exp005-label-review.ps1 -FilledLabelsSheet <filled-sheet> -RunDownstream`. |
| TASK-022 | 2026-06-21 | Open | Use the VEGO workbench launcher for daily local review. | Run `.\scripts\open-vego-workbench.ps1` from the repo root, or `.\scripts\open-vego-workbench.ps1 -Gui` when the visualizer is needed. |
| TASK-023 | 2026-06-22 | Open | Harden EXP-005 evidence validity. | Add a second reviewer or supervisor adjudication path for disputed rows before treating EXP-005 labels as strong quantitative evidence. |
| TASK-024 | 2026-06-22 | Open | Use EXP-005 generated verdict and manifest for evidence reruns. | Review `evidence_verdict.md` and `reproducibility_manifest.json` after every EXP-005 rerun; tag only stable validated evidence states. |
| TASK-025 | 2026-06-22 | Open | Revisit synthetic M4B-1.1 policy candidates only after real EXP-005 labels exist. | Use `docs/research/m4b1-synthetic-policy-candidate-review.md` as a discussion aid; do not implement policy changes until the real-label gate passes. |
| TASK-026 | 2026-06-23 | Open | Use the supervised next-step loop for continuation prompts. | Run `.\scripts\run-codex-next-step.ps1 -RefreshWiki -RunHealth -NoOpen`; inspect `reports/generated/next_step_loop/last-run.md` and `reports/generated/project_review/latest-review.md`. |
| TASK-027 | 2026-06-23 | Open | Use the structured project review architecture for review prompts. | Run `.\scripts\run-project-review.ps1 -UpdateReviewState` after meaningful review cycles and keep `docs/agent-memory/review-state.md` current. |
| TASK-028 | 2026-06-23 | Done | Add generated progress visualizations for local review and Confluence dashboard tracking. | Regenerate with `.\scripts\build-progress-visualizations.ps1` after progress or KPI updates. |
| TASK-029 | 2026-06-23 | Done | Document the progress update architecture for memory, dashboards, Confluence outbox, health checks, and 4-hour thread updates. | Keep `docs/operations/progress-update-architecture.md` aligned when the update flow changes. |
| TASK-030 | 2026-06-23 | Done | Add architecture-facing progress update diagram. | Keep `docs/architecture/progress-update-diagram.md` aligned with the operational progress update contract. |
| TASK-031 | 2026-06-23 | Done | Add HITL resource pack for thesis and tool planning. | Use `literature/hitl-resource-pack/` for Chapter 2 framing and future EXP-005 tool discussions; keep downloads ignored. |
| TASK-032 | 2026-06-23 | Done | Add E2E progress report and local web dashboard for full project updates. | Regenerate with `.\scripts\build-e2e-progress-report.ps1` after memory, KPI, experiment, or review-state updates. |
| TASK-033 | 2026-06-24 | Done | Add alignment and structure hardening checkpoint. | Use `docs/operations/alignment-control.md`, `docs/research/thesis-structure-map.md`, and `python scripts\check_evidence_consistency.py` before evidence claims or thesis status updates. |
| TASK-034 | 2026-06-29 | Done | Draft Chapter 7 without overclaiming results. | After EXP-005 labels exist, rerun the downstream gate and replace the blocked quantitative-result placeholders with real accuracy, macro-F1, paired-correctness, and reliability results. |
| TASK-035 | 2026-06-29 | Done | Prepare supervisor-first EXP-005 approval pack. | Send/review `docs/research/supervisor-label-approval-pack.md` with the supervisor; after approval, collect blind labels and rerun the EXP-005 downstream gate. |
| TASK-036 | 2026-06-29 | Done | Align Claude/Codex around the PhD thesis trajectory. | Use `docs/research/phd-thesis-optimization-plan.md` and `docs/agent-memory/claude-phd-thesis-collaboration-prompt.md` for future thesis/research-structure collaboration. |
| TASK-037 | 2026-06-29 | Done | Harden doctoral extension capability model. | Use the capability stack in `docs/research/phd-thesis-optimization-plan.md` before proposing PhD extension work, especially baseline, memory, evaluation, and governance changes. |
| TASK-040 | 2026-07-04 | In progress | Execute the July 2026 supervisor redirect (`docs/research/extension-plan-2026-07-supervisor-redirect.md`). | Finalize the 2026-07-15 meeting package (skills map, prompt requirements, framework diagram, open questions); after the meeting, start P2 detail specs. |
| TASK-041 | 2026-07-04 | Open | Literature survey for Pnina's course per the taxonomy July-2026 section. | Build the corpus log per branch; presentation mid-August 2026; submission end-September/October 2026; the gap statement is the key output. |
| TASK-042 | 2026-07-04 | Open | Maintain the PhD extension idea log. | Add entries to `docs/research/phd-extension-ideas.md` while reading; medical-domain transfer is the preferred direction; Ali to check direct-track admin with Sigal. |
| TASK-043 | 2026-07-04 | Open | Execute the MediVARIA study plan (MV-P0 groundwork). | Present `docs/research/medivaria/medivaria-study-plan.md` at the 2026-07-15 meeting (agenda section 8); get Iris/Arnon endorsement of the thesis-vs-IIA role split and the first clinical guideline domain; keep thesis scope education-only until submission. |
| TASK-044 | 2026-07-05 | Open | Advance the H-layer mechanism experiment suite. | Harden atomic execution first; then rerun only approved protocols. EXP-009/010 already have provisional synthetic prototypes and await M-04. |
| TASK-045 | 2026-07-05 | Open / gated | Run the H-layer improvement loop per iteration protocol. | Fifteen iterations are accepted; iteration 015 is the latest reliability-only `NEUTRAL` snapshot. Preserve iteration-009 Pareto semantics; `threshold_sev2` and K30/K35 remain comparison points only. No accuracy or model default follows from iteration 015. |
| TASK-046 | 2026-07-05 | Done / human-gated | Repair EXP-012 measurement scaffold. | Validated interface and canonical cross-check pass; safe N=0 remains `NOT YET COMPUTABLE`. Next change requires real human labels, not code inference. |
| TASK-047 | 2026-07-10 | Blocked | Prepare passive H-layer shadow listener. | Offline design only until M-05 plus the separate five-file implementation authorization are recorded. |
| TASK-048 | 2026-07-10 | Done / proposal-only | Prepare the offline Vector 1 feedback-generalization gate and safe July 15 CLI demo. | Current feedback yields `BLOCKED_NO_VERIFIED_FEEDBACK`; collect verified/adjudicated reusable records and M-05 authorization before any LLM or Agent B context work. |
| TASK-049 | 2026-07-12 | Open (Phase 1 done) | Execute the H-layer enhancement plan (`docs/research/h-layer/enhancement-plan-2026-07-12.md`). | Phase 1 delivered: unified program overview, one-command gate, consistency fixes, and iteration-014 coherence repair. EXP-019/020 now have registered proposal protocols; execution remains human-gated. Run `.\scripts\verify-hlayer-all.ps1` before every finish. |
| TASK-050 | 2026-07-24 | Done / human-gated | Prepare the thesis evidence-advancement and review package. | Ask Iris and Arnon to approve the contribution framing, blind-label protocol, two-reviewer/adjudicator roles, development/holdout boundary, policy-candidate gate, and external-replication claim gate. Then calibrate reviewers and collect the 24 independent safe labels. |
| TASK-051 | 2026-07-24 | Done | Execute the continuation plan (`docs/research/continuation-plan-2026-07-24.md`). | PR #8 is the historical thesis evidence release. Its human-label and claim gates remain in force. |
| TASK-052 | 2026-07-25 | In review / governance-gated | Publish unified runtime, baseline, model, security, infrastructure, and package hardening through PR #10. | Local release verification is green. Keep the PR open until exact-head review is clean, required CI passes, enforceable main protection is confirmed, and one separate collaborator approves. Never bypass these gates. |
| TASK-053 | 2026-08-01 | Implemented locally / human-gated | Execute the Iris requirements next-step program through the August 5 package and August 12 handoff interfaces. | Ali reviews and approves the exact corrected package, names the human roles, runs timed/adversarial rehearsals, authorizes sharing/access tests, and records August 5 decisions. Continue transcript review and literature execution without inventing evidence. |
| TASK-054 | 2026-09-02 | In progress | Preliminary Study 1 (EXP-045): descriptive WHEN-to-escalate inventory over the frozen Cheers/ParkWise run; Thursday one-page design delivered (EN/HE) with the 115-item call checklist. | Fri 09-04 freeze per-row CSV and send the marking sheet; Sat 09-05 marks, m2-m5, injected P6 intervention; Sun 09-06 two-page results; Wed 09-09 proposal v2 (Study 1 preliminary results). |

## Completed Work

| Date | Summary | Files |
| --- | --- | --- |
| 2026-09-03 | Created and validated the strict one-page preliminary human-intervention experiment for Iris. It uses three frozen cases, explicit autonomous/human-assisted conditions, bounded controlled inputs, and `To be measured` outcomes; the local PDF is exactly one A4 page and is not an effectiveness result. | `docs/research/phd-proposal/2026-09-03-preliminary-human-intervention-experiment.en.md`, `scripts/build_paper.py`, `scripts/tests/test_preliminary_human_intervention_one_page.py`, ignored local PDF |
| 2026-06-11 | Created shared memory foundation for Codex and Claude. | `AGENTS.md`, `CLAUDE.md`, `docs/agent-memory/*` |
| 2026-06-11 | Added clearer current-state and progress tracking requirements. | `AGENTS.md`, `CLAUDE.md`, `docs/agent-memory/README.md`, `docs/agent-memory/current-state.md`, `docs/agent-memory/progress.md` |
| 2026-06-11 | Added scripted memory automation for prompt start/end. | `scripts/agent-memory-start.ps1`, `scripts/agent-memory-finish.ps1`, `docs/agent-memory/automation.md` |
| 2026-06-11 | Extracted original VEGO-AI package and added PhD research architecture scaffold. | `VEGO-AI/`, `README.md`, `PROJECT_CHARTER.md`, `docs/architecture/`, `docs/research/`, `experiments/`, `data/`, `papers/`, `thesis/`, `scripts/` |
| 2026-06-11 | Published safe baseline to private GitHub repo. | `main` branch on `AliHamed17/Vego-Ai` |
| 2026-06-11 | Added reusable Claude bootstrap prompt and linked it from Claude instructions. | `CLAUDE.md`, `docs/agent-memory/claude-bootstrap-prompt.md`, `docs/agent-memory/README.md` |
| 2026-06-11 | Added and linked the workspace architecture diagram. | `README.md`, `docs/architecture/README.md`, `docs/architecture/project-map.md`, `docs/architecture/workspace-diagram.md` |
| 2026-06-11 | Added human-feedback manager files and schema fields. | `VEGO-AI/framework/human_feedback_manager.py`, `VEGO-AI/inputs/human_feedback.example.jsonl`, `VEGO-AI/schemas/human_feedback.schema.json`, `VEGO-AI/schemas/human_review_item.schema.json` |
| 2026-06-12 | Added human-feedback manager docs/tests and ignored local Claude settings. | `.gitignore`, `VEGO-AI/README.md`, `VEGO-AI/docs/human_feedback_manager.md`, `VEGO-AI/docs/human_review_queue.md`, `VEGO-AI/tests/test_human_feedback_manager.py` |
| 2026-06-12 | Added Research OS and Confluence sync infrastructure. | `docs/research/`, `docs/confluence/`, `experiments/EXP-000-existing-packaged-results-audit/`, `scripts/build-confluence-wiki.ps1`, `scripts/research-health.ps1` |
| 2026-06-12 | Configured ignored local Confluence target. | `docs/confluence/wiki-sync-config.local.json` (ignored), `docs/confluence/wiki-sync.md`, agent instruction files |
| 2026-06-12 | Published M3 Human Judgment Memory to GitHub. | Commit `5e109e5` on `origin/main` |
| 2026-06-12 | Hardened the MSc/PhD research story around reusable human judgment. | `PROJECT_CHARTER.md`, `docs/research/*`, `thesis/outline.md`, `papers/mas4models2026/claim-evidence-table.md`, `docs/project-management/*`, `experiments/EXP-001-memory-assisted-agent4-controlled-experiment/README.md` |
| 2026-06-12 | Reviewed and merged M4A advisory layer. | PR #2, commit `ecd0972`, `VEGO-AI/framework/memory_advisor.py`, `VEGO-AI/schemas/memory_advice.schema.json`, `VEGO-AI/tests/test_memory_advisor.py`, `VEGO-AI/docs/memory_advisor.md` |
| 2026-06-13 | Tagged reproducible M3/M4A states and added Claude handoff. | `docs/research/m4a-post-merge-confirmation.md`, `docs/agent-memory/claude-m4b-handoff-prompt.md`, tags `milestone-m3-human-judgment-memory`, `milestone-m4a-memory-advisory`, `research-state-m4a` |
| 2026-06-13 | Added progress/KPI/results dashboard tracking. | `docs/dashboards/`, `scripts/build-confluence-wiki.ps1`, `scripts/research-health.ps1`, agent instructions, Confluence sync docs |
| 2026-06-13 | Added dashboard health enforcement. | `scripts/dashboard-health.ps1`, `scripts/research-health.ps1`, agent instructions, dashboard docs |
| 2026-06-13 | Added generated dashboard runtime snapshot. | `scripts/build-dashboard-snapshot.ps1`, `scripts/build-confluence-wiki.ps1`, `.gitignore`, dashboard/confluence workflow docs |
| 2026-06-13 | Added generated manual Confluence sync pack. | `scripts/build-confluence-manual-sync-pack.ps1`, `docs/confluence/manual-sync.md`, `scripts/build-confluence-wiki.ps1`, `scripts/dashboard-health.ps1`, `scripts/research-health.ps1` |
| 2026-06-14 | Recorded M4B-1 conditional approval contract and Claude handoff. | `docs/research/m4b-conditional-approval.md`, `experiments/EXP-001-memory-assisted-agent4-controlled-experiment/README.md`, `docs/agent-memory/claude-m4b-handoff-prompt.md`, research/planning/dashboard docs |
| 2026-06-14 | Added offline VEGO-AI results dashboard branch and PR. | PR #5, `.gitignore`, `[controlled analysis path omitted]build_results_dashboard.py`, `VEGO-AI/docs/results_dashboard.md`, `VEGO-AI/schemas/results_dashboard_snapshot.schema.json`, `VEGO-AI/tests/test_results_dashboard.py` |
| 2026-06-14 | Ran no-key local execution package and generated results summary. | Ignored `VEGO-AI/runs/20260614-122150/`, ignored `VEGO-AI/reports/results_dashboard/`, local configs, PR #6 |
| 2026-06-14 | Opened visualizer mismatch UX PR. | PR #7, `VEGO-AI/vego_visualizer_delivery/visualizer_utils.py`, `VEGO-AI/vego_visualizer_delivery/visualize_compliance.py`, `VEGO-AI/tests/test_visualizer_helpers.py`, `VEGO-AI/vego_visualizer_delivery/README.md` |
| 2026-06-14 | Ran full QA/system validation. | `VEGO-AI/reports/system_validation_report.md` (untracked), ignored `VEGO-AI/runs/system_validation_20260614-142018/`, ignored `VEGO-AI/reports/results_dashboard/` |
| 2026-06-14 | Fixed QA governance warnings after validation. | `scripts/research-health.ps1`, `VEGO-AI/reports/system_validation_report.md`, local `baseline/official-vego-ai` tracking branch, memory files |
| 2026-06-14 | Merged and tagged visualizer mismatch UX fix. | PR #7, commit `78b261e`, tag `research-state-visualizer-ux-clean`, real-display screenshots in `%TEMP%\vego_gui_validation_20260614_144509` |
| 2026-06-14 | Added shared state report for Claude and Codex. | `docs/agent-memory/shared-state-report.md`, `scripts/agent-memory-start.ps1`, `AGENTS.md`, `CLAUDE.md`, `docs/agent-memory/README.md`, `docs/agent-memory/claude-bootstrap-prompt.md` |
| 2026-06-14 | Added evaluation report scaffold and updated research dashboard state. | `docs/research/evaluation-report.md`, `docs/research/evaluation-plan.md`, `experiments/registry.md`, `docs/dashboards/`, `docs/agent-memory/` |
| 2026-06-14 | Ran initial EXP-001 mechanism/readiness evaluation. | `scripts/build-exp001-evaluation.ps1`, `docs/research/evaluation-report.md`, `experiments/EXP-001-memory-assisted-agent4-controlled-experiment/README.md`, ignored `reports/generated/exp001/` |
| 2026-06-14 | Generated EXP-002 expert labeling package. | `scripts/build-exp002-labeling-package.ps1`, `experiments/EXP-002-expert-label-expansion-holdout-evaluation/README.md`, `docs/research/evaluation-report.md`, ignored `reports/generated/exp002/` |
| 2026-06-16 | Generated supervisor Zoom demo package. | Ignored `artifacts/supervisor_demo_2026-06-17/`, ignored `outputs/manual-20260616-supervisor/`, refreshed `reports/generated/exp001/`, `reports/generated/exp002/`, and `VEGO-AI/reports/results_dashboard/` |
| 2026-06-16 | Added EXP-003 accuracy-improvement evaluation path. | `docs/research/accuracy-improvement-plan.md`, `docs/research/expert-labeling-protocol.md`, `experiments/EXP-003-accuracy-improvement-evaluation/README.md`, `scripts/build-exp003-error-analysis.ps1`, EXP-003 evaluator/test, ignored `reports/generated/exp003/` |
| 2026-06-16 | Generated full results and accuracy report. | `docs/research/evaluation-report.md`, ignored `artifacts/RESULTS_AND_ACCURACY_FULL_REPORT.md` |
| 2026-06-16 | Ran synthetic accuracy simulation. | `docs/research/evaluation-report.md`, ignored `artifacts/SYNTHETIC_ACCURACY_SIMULATION_REPORT.md`, ignored `reports/generated/synthetic_accuracy_simulation/` |
| 2026-06-16 | Added EXP-004 policy-sensitivity simulation harness. | `scripts/policy_sensitivity_simulation.py`, `scripts/build-policy-sensitivity-simulation.ps1`, `experiments/EXP-004-policy-sensitivity-simulation/README.md`, `experiments/registry.md`, research docs, ignored `reports/generated/policy_sensitivity/`, ignored `artifacts/POLICY_SENSITIVITY_EXPERIMENT_REPORT.md` |
| 2026-06-17 | Added EXP-005 real-label accuracy gate package. | `scripts/exp005_label_review.py`, `scripts/build-exp005-label-review.ps1`, `experiments/EXP-005-real-label-accuracy-gate/README.md`, `experiments/registry.md`, research docs, ignored `reports/generated/exp005_label_review/`, ignored `artifacts/EXP005_LABEL_REVIEW_PACKAGE.md` |
| 2026-06-21 | Added one-command VEGO workbench launcher. | `scripts/open-vego-workbench.ps1`, `docs/operations/vego-workbench.md`, `README.md`, memory files |
| 2026-06-21 | Exported VEGO topology/flow report to HTML and PDF. | `scripts/export-topology-report.ps1`, `docs/operations/vego-workbench.md`, ignored `artifacts/topology-export/VEGO_TOPOLOGY_FLOW_REPORT.html`, ignored `artifacts/topology-export/VEGO_TOPOLOGY_FLOW_REPORT[PDF omitted]` |
| 2026-06-21 | Exported baseline architecture overlay to HTML and PDF. | `scripts/export-baseline-overlay-report.ps1`, `docs/operations/vego-workbench.md`, ignored `artifacts/topology-export/VEGO_BASELINE_OVERLAY_REPORT.html`, ignored `artifacts/topology-export/VEGO_BASELINE_OVERLAY_REPORT[PDF omitted]` |
| 2026-06-22 | Added strategic review and hardening plan. | `docs/research/strategic-review-and-hardening-plan.md`, `docs/research/evaluation-report.md`, `docs/research/accuracy-improvement-plan.md`, `docs/project-management/risk-register.md`, memory files |
| 2026-06-22 | Enhanced EXP-005 evidence coverage. | `scripts/exp005_label_review.py`, `scripts/open-vego-workbench.ps1`, `experiments/EXP-005-real-label-accuracy-gate/README.md`, `docs/research/expert-labeling-protocol.md`, `docs/research/accuracy-improvement-plan.md`, `docs/research/publishability-register.md`, `docs/research/validity-threats.md`, `thesis/outline.md`, `docs/dashboards/kpi-register.md`, memory files |
| 2026-06-22 | Interpreted EXP-005 synthetic trial as design-only policy guidance. | `docs/research/m4b1-synthetic-policy-candidate-review.md`, `docs/research/accuracy-improvement-plan.md`, `experiments/EXP-005-real-label-accuracy-gate/README.md`, `docs/dashboards/kpi-register.md`, ignored `reports/generated/exp005_synthetic_trial/`, ignored `artifacts/SYNTHETIC_EXP005_TRIAL_REPORT.md` |
| 2026-06-23 | Added supervised Codex next-step loop. | `scripts/run-codex-next-step.ps1`, `docs/operations/codex-next-step-loop.md`, `docs/operations/vego-workbench.md`, `README.md`, `AGENTS.md`, `CLAUDE.md`, memory files |
| 2026-06-23 | Added memory-connected project review architecture. | `scripts/run-project-review.ps1`, `docs/operations/project-review-architecture.md`, `docs/agent-memory/review-state.md`, `scripts/agent-memory-start.ps1`, loop/docs/memory instruction files |
| 2026-06-23 | Added generated progress visualizations. | `scripts/build-progress-visualizations.ps1`, `docs/dashboards/README.md`, `docs/dashboards/progress-dashboard.md`, `scripts/build-confluence-wiki.ps1`, `scripts/dashboard-health.ps1`, `scripts/research-health.ps1`, `.gitignore` |
| 2026-06-23 | Added progress update architecture. | `docs/operations/progress-update-architecture.md`, `README.md`, `docs/architecture/project-map.md`, `docs/architecture/README.md`, `docs/dashboards/README.md`, `scripts/build-confluence-wiki.ps1`, `scripts/research-health.ps1` |
| 2026-06-23 | Added architecture-facing progress update diagram. | `docs/architecture/progress-update-diagram.md`, `README.md`, `docs/architecture/README.md`, `docs/architecture/project-map.md`, `scripts/build-confluence-wiki.ps1`, `scripts/research-health.ps1` |
| 2026-06-23 | Added E2E progress report and web dashboard. | `scripts/build-e2e-progress-report.ps1`, `docs/dashboards/README.md`, `docs/dashboards/progress-dashboard.md`, `docs/operations/progress-update-architecture.md`, `docs/architecture/progress-update-diagram.md`, `scripts/build-confluence-wiki.ps1`, `scripts/dashboard-health.ps1`, `scripts/research-health.ps1`, `scripts/open-vego-workbench.ps1` |
| 2026-06-23 | Added HITL resource pack for thesis and tool planning. | `literature/hitl-resource-pack/`, `scripts/download-hitl-resources.ps1`, `docs/research/literature-review-taxonomy.md`, `docs/research/methodology.md`, `docs/research/accuracy-improvement-plan.md`, `scripts/research-health.ps1` |
| 2026-06-24 | Added alignment and structure hardening sprint. | `docs/operations/alignment-control.md`, `docs/research/thesis-structure-map.md`, `scripts/check_evidence_consistency.py`, `README.md`, `docs/architecture/project-map.md`, `docs/research/README.md`, `docs/agent-memory/resource-memory.md`, `scripts/research-health.ps1` |
| 2026-06-29 | Added Chapter 7 current-evidence/results-readiness draft and refreshed thesis progress status. | `thesis/chapters/07-experimental-results.md`, `thesis/outline.md`, `docs/research/thesis-structure-map.md`, `docs/PROGRESS_TRACKER.md`, memory files |
| 2026-06-29 | Added supervisor-first EXP-005 approval pack and label workflow handoff. | `docs/research/supervisor-label-approval-pack.md`, `docs/research/expert-labeling-protocol.md`, `thesis/outline.md`, `docs/PROGRESS_TRACKER.md`, `docs/research/README.md`, memory files |
| 2026-06-29 | Added PhD thesis optimization and Claude collaboration handoff. | `docs/research/phd-thesis-optimization-plan.md`, `docs/agent-memory/claude-phd-thesis-collaboration-prompt.md`, `CLAUDE.md`, `docs/research/research-plan.md`, `docs/research/thesis-structure-map.md`, `docs/research/README.md`, memory files |
| 2026-06-29 | Hardened doctoral capability alignment for Claude/Codex and future PhD studies. | `docs/research/phd-thesis-optimization-plan.md`, `docs/agent-memory/claude-phd-thesis-collaboration-prompt.md`, `docs/operations/alignment-control.md`, `docs/architecture/project-map.md`, `docs/architecture/README.md`, `README.md`, memory files |

## Next Steps

- **2026-09-06 (Codex):** prepared separate Study 2A `VEGO-AI_ON` versus `VEGO-AI_OFF` descriptive comparison on the frozen public AirTravel corpus, with a newly constructed single-model no-VEGO baseline, exact parity controls, disabled-by-default local harness, JSON Schema, bilingual Hebrew preregistration/readiness documents, and a separate Study 2B Llama feasibility record. PR #40 is open/draft/unmerged; its latest CI run passed all six jobs. No provider/model call, Llama download, scientific experiment, or Study 1 mutation occurred. Independent review and explicit run authorization remain required.

- **2026-09-03 (Codex):** produced the filled Hebrew supervisor-facing Q&A task plan (8 tasks, P0/P1/P2, no manual labeling), plus ignored local RTL DOCX/PDF deliverables. Current 12 Q&A records are documented as `ANSWER_NOT_PERSISTED`; only a descriptive feasibility result is permitted until complete observability is available.
- **2026-09-03 (Codex):** refined the plan after Claude/GitHub evidence: interaction-log recovery is now Task 1, the first rerun is one setting only, supervisor requests are limited to log transfer or one-run/API-cost approval, and the PDF/DOCX omit internal commit SHAs.

- **2026-09-03 (Codex):** Ali reviews and sends the strict one-page experiment design to Iris. Obtain explicit approval of the case/review unit and independent-review protocol before replacing any `To be measured` outcome or making a benefit claim.
- **2026-09-02 (Claude):** send the one-page study design to Iris and Arnon before Thu 09-03 13:00; request the Cheers domain-base files / TA exercise index; run EXP-045 to a per-row CSV on Fri 09-04; collect the three marking sheets by Sat 09-05 (fallback: report m1, m2, m5 and Ali's marks on Sunday); write the Sun 09-06 two-pager; integrate as Chapter 5 preliminary results in the Wed 09-09 proposal v2.
Note (2026-08-14): superseded by the August 12 call. The August 5 supervisor package was delivered and the August 12 meeting happened; see [`2026-08-12-supervisor-meeting.md`](../research/meetings/2026-08-12-supervisor-meeting.md) (evidence matrix `F1`-`F17`) and its bilingual companion [`2026-08-12-post-meeting-plan.md`](../research/meetings/2026-08-12-post-meeting-plan.md) for the current, live next-step list. Medical work remains blocked at 0/6 gates and EXP-005 remains 0/24 — unchanged by this call.

1. **Time-critical:** fill in the real scholarship name/portal/deadline in [`scholarship-recommendation-request-template.md`](../operations/scholarship-recommendation-request-template.md) and send it to Iris and Arnon before the stated "15th" deadline (`F16`/`A0812-06`) — this assistant cannot send email itself.
2. Literature review (Chapter 2) is being produced on a separate, parallel verification track (not this session) — do not duplicate `A0812-01`/`02`/`03` here.
3. [`chapter-4-research-methodology.md`](../research/phd-proposal/chapter-4-research-methodology.md) is now a working draft (`A0812-04`) — Ali/supervisors need to confirm or correct the three recommended artifacts and work through the 8 open items in its own §4.7 before it can be treated as decided.
4. Confirm the correct email address and re-share the Drive with Arnon — closes the `A08-05` item open since August 5 (`F17`/`A0812-05`); this assistant has no Drive-sharing write access.
5. Still open, not resolved by the August 12 call — put on the next meeting's agenda explicitly: `D-RQ-01`/`D-RQ-02` (RQ wording sign-off), `E6` (exploration vs. identification/classification), `E8` (human vs. expert judgment), the Plan A/B boundary wording, the evidence-boundary wording, and owner assignment for medical-feasibility/university-process verification.
6. Obtain written department/Graduate Studies confirmation of the candidacy deadline, reviewer count, nomination path, committee rules, and presentation requirements (unresolved since 2026-07-30, `ISS-024`).
7. Keep patient-row inspection, medical computation, external APIs, and pilots blocked until all six medical entry gates pass; the Clalit meeting confirmed for 2026-08-26 (`A0812-07`) is the next real checkpoint on that path.
8. Appoint two independent EXP-005 reviewers plus an adjudicator and collect the 24 generalization-safe labels without inferring or prefilling any value — also blocks Chapter 4 §4.5's rater question.
9. Name an independent implementer/reviewer for Chapter 4's Study 2 conformance-suite gap, and two raters for Study 3 — both currently unnamed (`chapter-4-research-methodology.md` §4.7).
10. Refresh dashboards, evidence checks, project health, and agent memory after each implementation tranche.


## Open Issues

<!--
last_updated: 2026-09-03
staleness_threshold_days: 7
-->

# Issues

Track project issues here. Keep active issues near the top.

## Open

| ISS-053 | 2026-09-03 | Supervisor feedback / Q&A escalation tranche | High | High | Medium | Open, supervisor validation pending | The immediate study is now Q&A escalation detection: the frozen final snapshot exposes 12 Agent-2→Agent-1 questions but 0 persisted answers, so answer-confidence, answer-evidence, round linkage, and true/false alert validation are not yet observable. Claude/Codex disagreement on usable C2 corrections (114 vs 111) is deferred and does not block this study. | Capture or supply approved answer-level Q&A histories and blind human labels covering alerts and non-alerts; do not run intervention or score-effect replay. |

| ID | Date | Source | Severity | Impact | Effort | Status | Summary | Next Step |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ISS-052 | 2026-09-02 | Claude (EXP-045 scouts) | Low | Low | Low | Partially resolved 2026-09-02 | Documentation drift found while grounding the preliminary study: (a) `docs/research/baseline-characterization.md` line 48 described the M1 triggers as `requires_human_review` most common, while the four queue files show `guideline_update_proposed` 9 and `medium_confidence` 3 with `requires_human_review` 0 (corrected); (b) `docs/research/phd-proposal/chapter-5-preliminary-results.md` 5.2 reports the EXP-008 33/26 figures without naming the `cd_ch` setting (open); (c) Chapter 4 section 4.3 describes a composite trigger score `s(e)` that no framework code computes (open; only categorical per-agent fields exist). Also: the Cheers `domain_base_{ucd,cd}.txt` files named by `inputs/README.md` are not in the repository. | Keep chapter text bound to file-backed numbers; recover the Cheers domain-base files from the course materials before the Sunday 2026-09-06 run. |
| ISS-049 | 2026-09-01 | Claude (wave-1 merge sync) | Medium | Medium | Low | Resolved in the wave-1 PR; process gap still open | PR #32 ("Complete documentation structure...") edited the protected-tree file `VEGO-AI/eval/README_EVALUATOR.md` without updating `CURRENT_RUNTIME_LOCKS` in `scripts/build_hardening_manifests.py`, and was merged while its CI run concluded FAILURE - leaving `main` red on the hardening check. Repaired in the wave-1 branch by re-locking the README's hash (content diff reviewed: docs-only, no runtime change) and regenerating the manifests. Process gap: nothing prevents merging a red PR; this is the second time a red merge reached `main` (see the 2026-08-24 pip-audit incident). | Consider branch protection requiring the merge-gate check on `main`, and a rule that any protected-tree edit must update the lock table in the same PR. |
| ISS-048 | 2026-08-31 | Claude (contract artifact build) | Medium | Medium | Low | Open, specification tension needing a decision | `schemas/governed-judgment-record-v1.schema.json` ships SEVEN lifecycle states, not the six `chapter-4-research-methodology.md` §4.4 fixes (`Draft, Active, Contested, Superseded, Expired, Revoked`). It adds `retained_dissent`, and conformance check CHK-14 makes that state mandatory whenever a qualified dissent is unadjudicated - so the seventh state is forced, not optional. This is not schema sloppiness; it is a real tension in the specification: §4.4 fixes six states, while §3.4 requires retained dissent to be a state that BLOCKS REUSE pending adjudication, and `Contested` is not defined tightly enough to say whether it carries that blocking semantics. The deviation is documented in the audit report rather than hidden. | Decide one of: (a) update §4.4 to seven states, or (b) collapse `retained_dissent` into `Contested` and attach the reuse-blocking rule there. Until decided, do not describe the contract as implementing "the six-state lifecycle". See `docs/research/phd-proposal/architecture-alignment-audit-2026-08-31.md` §5. |
| ISS-047 | 2026-08-31 | Claude (contract artifact build) | Low | Medium | Low | Open, design questions for supervisor | Two design gaps in the new contracts, left deliberately unfixed. (1) `schemas/reuse-decision-record-v1.schema.json`'s context-distance ladder has no dimension for a *revised domain description*, though the proposal's p.9 sequence names it as a distinct step; it currently rides on `cohort`, so a mid-semester revision within one cohort computes differing-rank 1 and returns plain "Eligible" with nothing recording that the prior ruling's premise changed - the proposal's own failure mode reappearing inside the fix. Adding a rank changes every downstream comparison and the ladder is explicitly pending supervisor confirmation, so it was not changed unilaterally. (2) `schemas/review-policy-signal-contract-v1.schema.json`'s `importantCaseLabelIndependentOfPolicy` is a required boolean with no not-applicable state, so when `importantCaseLabelSource` is `not_yet_established` an instance must assert `true`/`false` about a label that does not exist; its two sibling fields solve this with `not_yet_*` enum members. | Put the revised-description ladder rank to Iris/Arnon with the mid-semester example; make the boolean nullable or a three-value enum. See `docs/research/phd-proposal/architecture-alignment-audit-2026-08-31.md` §6. |
| ISS-046 | 2026-08-31 | Claude (contract artifact build) | Medium | Medium | Low | Open | `format: "date-time"` is inert across every schema in `schemas/`. `rfc3339-validator` is not installed in the `uv` environment, so `jsonschema.FormatChecker()` registers no `date-time` checker and a timestamp of `"not-a-timestamp"` still passes `scripts/validate_research_records.py`. Verified by direct mutation test. This is repo-wide, not specific to the three contracts added on 2026-08-31. | Add `rfc3339-validator` to the dependency set and re-run the full example suite - expect previously-passing records to fail, so treat it as its own change with a cascade check, not a drive-by fix. |
| ISS-045 | 2026-08-31 | Claude (architecture alignment audit) | Medium | Medium | Low | Open | `experiments/registry.md` rows EXP-016 ("Authority and timeout safety") and EXP-035 ("Fault injection and authority safety") use "authority" to mean role-based access control over runtime writes on `SYNTHETIC_NOT_HUMAN` fixtures (`scripts/hlayer_offline/exp016.py` `ROLE_AUTHORITY` maps four roles onto `{submit_feedback, adjudicate, approve_correction}` with no claim, fragment, or scope term). The proposal's C2/§3.4 sense of "authority" is claim-specific standing to settle a particular contested fragment. A reader scanning the registry will read the proposal's construct as covered when it is not. | Relabel both rows to say "role-based action authorization" and add a one-line note distinguishing them from claim-specific authority; see `docs/research/phd-proposal/architecture-alignment-audit-2026-08-31.md` §2. |
| ISS-044 | 2026-08-31 | Claude (architecture alignment audit) | High | High | Medium | Open, needs signed H-layer change authorization | Three verified live defects in `VEGO-AI/framework/human_judgment_memory.py` and `memory_advisor.py`, each contradicting a C2/C3 lifecycle requirement. (1) `write_memory()` dedups by `memory_id` keep-first, and `memory_id` is `f"HJM-{setting}-{pid}"` (setting+pattern only, not content or version), so an amended judgment for the same pattern collides with its predecessor and is silently dropped - the inverse of supersession. (2) `search_memory()` gates on `conflict_status == "needs_adjudication"` but never reads `status`, so a retired record still flows downstream, and takes no requester parameter, so the proposal's first reuse gate (visibility/authorization before exposure) is unimplementable at that call site. (3) `applies_to_future_models` appears exactly once in the whole framework - written as `False` in `build_memory_item()` - and is never read; `memory_advisor.py` forwards `reuse_scope` as only `{domain, diagram_type}`, dropping both `applies_to_future_models` and `limitations`. A default-deny reuse-scope control that nothing consults. | These files are under `VEGO-AI/framework/`, protected by `scripts/check_hlayer_change_authorization.py`; fixing them needs a signed authorization hash. Raise with Ali, then fix under that authorization. See the audit report §4. |
| ISS-043 | 2026-08-31 | Claude (architecture alignment audit) | High | High | Medium | Open, needs a supervisor decision not an implementation | The construct the 2026-08-25 proposal §1.8 designates as the thesis's falsifiable novelty - reviewer selection as a function of claim-specific *competence* and *authority*, modelled as distinct dimensions - has no implementation surface, and `competence` is absent from the project's own design documents as well: `chapter-4-research-methodology.md` §4.4's field list names case grounding, system reasoning, expert rationale, scope, authority, provenance, and lifecycle, but not competence. It is the only §3.4 content element that is undesigned as well as unimplemented. What exists (`ROLE_AUTHORITY`, `ReviewItem.owner_role`, `gold-label-record-v2.reviewerRole`) is aggregate role over an action class, checked after submission - verbatim the form §1.8 names as the literature's insufficient version. Consequence: §3.3's declared primary test for Study 1 cannot be run as specified, since one of its five literature-derived signals has nothing to log, weight, or ablate. This PR adds `schemas/review-policy-signal-contract-v1.schema.json` modelling the two dimensions separately, but the construct itself needs supervisor confirmation before it can be treated as settled. | Put the competence construct to Iris/Arnon explicitly: is claim-specific competence assessment in scope, and how is it evidenced? See `docs/research/phd-proposal/architecture-alignment-audit-2026-08-31.md` §2. |
| ISS-042 | 2026-08-31 | Claude (architecture review) | Low | Medium | Low | Open, needs a decision not a guess | `docs/PROGRESS_TRACKER.md`'s `AUTO:stamp` region reads its "as of" date from `docs/research/h-layer/program-status-snapshot-v1.json`'s own `generatedAt` field (by design - deterministic, not wall-clock), which is `2026-07-26`. That file has no dedicated regenerator script in `scripts/` (only consumers), only one version (`v1`) exists, and no decision record says whether it is an intentionally-frozen snapshot of the now-paused/concluded H-layer experimental track, or a live feed that stopped being regenerated by mistake. Until this call is made, the stamp's wording has been changed (this PR) to state its H-layer-only scope explicitly and point to `docs/agent-memory/current-state.md` for overall project freshness, so it no longer reads as a whole-project staleness signal - but the underlying question of whether `program-status-snapshot-v1.json` should ever get a `v2` is still open. | Ali/Iris/Arnon (or a future agent with the H-layer meeting history in context) decides: freeze-and-document it as historical, or specify what should trigger a `v2` regeneration. |
| ISS-041 | 2026-08-24 | Claude (v23 doctoral proposal strict review) | Medium | Medium | Low | Open / half-resolved 2026-08-25 | The 2026-08-23 consolidated proposal PDF states the case-model/pattern counts (178 models, 26 patterns) as uncontested fact with zero open-item caveat, while the companion evidence package independently computes 165 models / 27 patterns for the same evidence state. v13's equivalent mismatch at least carried a partial caveat; this is worse than that. | Reconcile the two counts or restore an explicit caveat before this proposal is shown to Iris/Arnon; see `docs/research/phd-proposal/doctoral-proposal-2026-08-23-strict-review.md` section B. **Update 2026-08-25:** the caveat was restored in the 2026-08-25 revision, and the foundation manuscript was then supplied and verified directly. Table 1 of the manuscript gives 46+47+44+41 = **178** case models, and it states verbatim **26** patterns = 8 substantial + 18 occasional. The manuscript figures are therefore correct and the 165/27 side is what needs explaining. Still open only because the implementation snapshot has not been supplied. See the reference [1] section of `docs/research/phd-proposal/external-citation-verification-log.md`. |
| ISS-040 | 2026-08-24 | Claude (v23 doctoral proposal strict review) | High | High | Medium | Open, 4th consecutive artifact | The Iris-assigned ACL-2026 GitHub taxonomy classification exercise (relevant/less relevant/not relevant/missing, one slide) is still entirely absent from the 2026-08-23 consolidated proposal PDF -- the fourth artifact in a row (after literature-review-v13, workbook-v8, package-v15) to skip this specific 2026-08-12 instruction while doing other literature work instead. | Do the narrow taxonomy classification exercise and the one slide; do not let further proposal drafts substitute broader literature work for this specific still-open instruction. See `docs/research/phd-proposal/doctoral-proposal-2026-08-23-strict-review.md` section A and ISS-034. |
| ISS-038 | 2026-08-20 | Claude (v16 strict audit) | Medium | Medium | Low | Open / unchanged after workbook repair | PR #20 (`docs/literature-awesome-index-and-root-cleanup`, the generated awesome-list `literature/README.md` rebuild) is fully green and `MERGEABLE` but was never merged into `main`. The workbook v12 repair did not merge or otherwise change this PR; `main`'s current `literature/README.md` remains the old generic stub. | Merge PR #20, or explicitly decide not to and record why. |
| ISS-037 | 2026-08-20 | Claude (v16 strict audit, 70-agent adversarial workflow) | Critical | High | Medium | Open | Literature Review v16's central novelty argument (p.28, "recent 2026 evidence narrows novelty further") cites Dhanorkar et al. 2026, Villavicencio et al. 2026, and Zhou et al. 2026 -- none appear in the 45-page References list or the 81-entry Appendix B, though all three are real papers already fully cited with DOIs in the companion workbook v11. Shneiderman (2020), Dellermann et al. (2019, a recurring defect since v13), and Pearl & Bareinboim (2014) are three more in-text citations with no bibliography entry. | Add complete References/Appendix B entries for all six names or remove the claims that depend on them before this is shown to Iris/Arnon; see `docs/research/phd-proposal/literature-review-v16-workbook-v11-verification-report.md`. |
| ISS-036 | 2026-08-20 | Claude (v16 strict audit, 70-agent adversarial workflow) | High | High | Medium | Open / workbook side remediated | Workbook v12 now rejects a global readiness score, marks ACL-116 disposition provisional, adds G6, corrects the EXP-008 arithmetic and source attributions, reconciles anchor maturity, and removes unverifiable pseudo-scores. The paired PDF v16 still self-reports 76/100 and still requires its own scorecard/count/bibliography repair, so the cross-artifact issue is not closed. | Do not present 76/100 to Iris/Arnon. Complete the paired PDF repair, then rerun a PDF/workbook consistency audit using `literature-review-v16-workbook-v11-follow-up-v12.md`. |
| ISS-034 | 2026-08-19 | Claude (v13 verification) | High | High | Medium | Open | This week's actual assignment from Iris (classify the ACL-2026 GitHub taxonomy corpus as relevant/less relevant/not relevant/missing, produce one slide) is not done in literature-review-v13. v13 instead ran nine broader search families across ACL/ACM/AAAI/PMLR/PubMed/ScienceDirect/web -- the broader search Iris explicitly deferred to after the proposal stage. | Do the narrow taxonomy classification exercise and the one slide before broadening the search further; see `docs/research/phd-proposal/literature-review-v13-workbook-verification-report.md` section D. |
| ISS-033 | 2026-08-19 | Claude (v13 verification) | High | High | Medium | Open | Literature-review-v13.docx states "Current readiness score: 84/100"; the companion evidence workbook's own `Dashboard.csv` independently computes `Overall literature readiness: 36`, `Release Decision: NOT DOCTORAL-READY`, for the same evidence state. Root cause: the workbook's `Provenance.csv` still names v10, not v13, as the current authoritative review -- the two artifacts are unreconciled. | Rebuild/rebase the workbook against v13 before either artifact is shown to Iris/Arnon; reconcile or drop the 84/100 figure. See `docs/research/phd-proposal/literature-review-v13-workbook-verification-report.md` sections A and C. |
| ISS-031 | 2026-08-11 | Claude (gaps-and-blockers audit) | Low | Medium | Low | Open | This machine has two separate checkouts: the git worktree this session's shell defaults into (`.claude\worktrees\trusting-kilby-79f5d4`, an old branch missing `docs/research/phd-proposal/`, `thesis/chapters/`, and most current `issues.md`/`decisions.md` history) and the real working checkout at `C:\Users\ahamed\vego-ai` on `main`, which is where all real work happens. Two of eight parallel sub-agents in a gaps-sweep read the stale worktree and falsely concluded real files/tables "don't exist." | Always explicitly `cd` to `C:\Users\ahamed\vego-ai` before any git/file operation (this session already does); consider deleting or fast-forwarding the stale worktree; when delegating to sub-agents, pass and verify the absolute repo path rather than relying on template interpolation. |
| ISS-030 | 2026-08-04 | Claude (CI push) | Low | Low | Low | Open | `scripts/agent-memory-finish.ps1`'s `Add-Content` calls to `session-log.md`/`revert-log.md` leave an extra trailing blank line each run, which fails CI's `git diff --check` line-ending hygiene step (caught when pushing straight to `main`; the log/archive files inherit the same issue). | Before pushing after running the finish script, check `git diff --check <base>...HEAD` and trim any new trailing blank line; ideally fix the script's here-string/Add-Content usage so it stops happening. |
| ISS-028 | 2026-08-01 | Codex (release integrity audit) | Medium | Medium | Rebuild after human freeze | Open / fail-closed | The existing local offline ZIP contains the superseded presentation package. It is marked `STALE / INVALIDATED`, and readiness now compares the ZIP member hashes with the current PPTX, PDF, and review workbook. | Do not deliver it. Rebuild the ZIP only after the corrected package passes human rehearsal and RG-04 freeze, then refresh manifests and hashes. |
| ISS-027 | 2026-07-30 | Codex (presentation audit) | High | High | Human rehearsal + authorized delivery | Open / production portion remediated 2026-08-01 | The corrected August 5 PPTX/PDF, 21 source-note sections, 44-control appendix, review workbook, and native-render QA now exist. The prior backup is stale. Human timed and adversarial rehearsal, Ali exact-package approval, delivery, Iris/Arnon access tests, and the separately governed candidacy deck remain unproved; candidacy rules are still unverified. | Freeze the exact package after Ali review, run both dated human rehearsals, rebuild the backup, then share only with authorization and record two independent recipient access tests. |
| ISS-026 | 2026-07-30 | Codex (July 29 closure) | Medium | High | Human review | Open | The private Ali-owned PhD Drive and native literature Sheet exist but have not been shared, sent, or recipient-access-tested. | Ali reviews the exact package and explicitly authorizes sharing; then verify each intended recipient's access. |
| ISS-025 | 2026-07-30 | Codex (metadata audit) | High | High | Governance + authorized VDI | Blocked | The shared MIMIC resource contains 25 observed CSVs totaling 39.65 GiB versus 26 official MIMIC-III v1.4 tables; `NOTEEVENTS`, workbook authority, checksums, environment, parameters, and input-to-output provenance are unresolved. | Keep rows untouched. After all six medical gates pass, reconcile the canonical manifest inside the approved VDI. |
| ISS-024 | 2026-07-30 | Codex (July 29 closure) | High | High | External confirmation | Open | The official candidacy deadline, reviewer count, nomination process, committee rules, and presentation requirements are unverified. | Obtain written department or Graduate Studies confirmation and rebaseline within one working day if dates differ. |
| ISS-023 | 2026-07-30 | Codex (medical readiness) | High | High | Partner + governance | Blocked | Medical readiness is 0/6 mandatory entry gates: use-case, people, authorization, ethics/privacy, environment, and protocol are all open. | Name accountable owners and collect project-specific approval evidence; default to Plan B on August 26 if any critical prerequisite remains unproved. |
| ISS-022 | 2026-07-30 | Codex (July 29 evidence) | High | High | Bilingual human review | Open | The July 29 Hebrew ASR, English translation, and speaker attribution are machine-derived working evidence. | Complete bilingual and diarization review before direct quotation, final attribution, or external release. |
| ISS-032 | 2026-08-19 | Claude (CI push) | Low | Low | Unknown | Open | `scripts/dashboard-health.ps1 -RequireOutbox` throws "Generated dashboard snapshot must be ignored by Git" for `docs/dashboards/status-snapshot.generated.md` (and its sibling `.generated.md`/`.generated.html` files). `.gitignore` does list `docs/dashboards/*.generated.md`/`*.generated.html`, but these exact files were deliberately force-tracked in commit `9163b2d` ("Track generated presentations, output renders, and dashboard snapshots"), predating this session — so the check and the tracking decision now disagree. Not investigated further; left as-is rather than guessing which side is stale. Note: a related-but-distinct set of files from the same commit (PDFs/ZIP, not the dashboard `.generated.*` files) was resolved as ISS-035, untracked with Ali's confirmation — this dashboard-file question is still open on its own. | Decide whether these generated dashboard files should be tracked (and update `dashboard-health.ps1`'s check accordingly) or untracked (and `git rm --cached` them) — then re-run `dashboard-health.ps1 -RequireOutbox` to confirm. |
| ISS-019 | 2026-07-28 | Claude | Medium | Medium | Process rule | Open | The trusted authorization SHA (local git config + GitHub variable `H_LAYER_AUTHORIZATION_SHA256`) was advanced to the record version on unmerged branch `agent/bigui-live-evaluation-v2` (commit `cacfab7`), which broke `verify-hlayer-all` on every other branch until they adopt that record version. `feature/evaluation-phase` adopted it on 2026-07-28. | Agree on a rule: only re-point the trusted SHA at record versions that are merged to `main`, or synchronize all active branches in the same change. |
| ISS-002 | 2026-06-11 | Codex | Low | Low | Medium | Open | Prompt memory automation is script/instruction based, not a background service or native runtime hook. | Use the scripts consistently; consider native hooks later if the active tools support them. |
| ISS-005 | 2026-06-12 | Codex | Medium | Medium | High | Blocked | Live Confluence sync target is configured locally, but Atlassian Rovo reports cloud `724252a1-a5b7-45a5-b6ec-27a8292197ec` is not explicitly granted. | Grant Atlassian Rovo access, or enable the Codex Chrome Extension route, then update pages. |
| ISS-006 | 2026-06-12 | Codex | Medium | High | High | Open | M4B-1 memory-informed parallel comparison has evaluation tooling, but no completed generalization-safe expert labels. | Fill the EXP-005 blind label-review sheet with at least 20 safe expert labels. |
| ISS-007 | 2026-06-14 | Codex | Medium | High | Low | Open | M4B/C4B can suffer evaluation leakage if memory from the same pattern is reused for that pattern. | Keep same-pattern rows strictly for mechanism validation; label EXP-002 candidates. |
| ISS-011 | 2026-06-21 | Codex | Low | Low | Low | Open | EXP-005 label package regeneration can hit a Windows file lock if CSV is open in Excel during build. | Close the blind CSV before rerunning workbench or build scripts. |
| ISS-012 | 2026-06-22 | Codex | Medium | High | Low | Open | Strategic review found a false-accuracy-narrative risk: synthetic results could be misread as real accuracy. | Keep synthetic outputs labeled as policy-risk screening only; quote label status in reports. |
| ISS-013 | 2026-06-22 | Codex | Medium | High | Low | Open | Strategic review found that one-reviewer labels would be weak evidence for strong accuracy claims. | Use `exp005_adjudication_sheet.csv` for reviewer-2 or supervisor adjudication and reliability checks. |
| ISS-014 | 2026-07-10 | Codex | High | High | Human decision | Blocked | M-02 through M-05 have no recorded outcomes, so architecture, dosage, H-Verify, authority, timeout, and live-hook choices cannot become defaults. | Record explicit outcomes in the July 15 decision register; silence remains deferred. |

## Blocked

| ID | Date | Source | Reason | Summary | Needed |
| --- | --- | --- | --- | --- | --- |

## Resolved

### ISS-054 — Current Q&A artifacts do not preserve complete episodes

**Opened:** 2026-09-03
**Status:** Open / observability gap
**Summary:** The frozen Q&A snapshot contains 12 persisted Agent 2 → Agent 1 questions but no persisted matching answers, answer confidence, answer evidence, or reconstructable round/follow-up/convergence metadata.
**Impact:** Alerts can be reported only as `ANSWER_NOT_PERSISTED` candidate signals; no true/false validation or detector performance claim is permitted.
**Next action:** Add complete episode instrumentation before the next corpus run; keep manual labeling deferred.

### ISS-055 — Original interaction log availability is unresolved

**Opened:** 2026-09-03
**Status:** Open / recovery step pending
**Summary:** `eval_config.json` names `interaction_log.jsonl` and `llm_client.py` can persist `response_raw`, but the original log was not included in the frozen package.
**Impact:** Additional raw model-call provenance may be recoverable at zero API cost, but advisor answers cannot be reconstructed if the answering loop never ran.
**Next action:** Search local archives first; request the file from Iris/Arnon only if Ali cannot locate it.

| ID | Opened | Resolved | Source | Summary | Resolution |
| --- | --- | --- | --- | --- | --- |
| ISS-039 | 2026-08-24 | 2026-08-24 | Claude (CI push) | `main` was CI-red before this session's own push (confirmed via the weekly security-audit run on the prior commit): `pip-audit` flagged `pip 26.1.2` (PYSEC-2026-3721), pinned as a transitive `pip_api` dependency in `uv.lock`. Bumping it cascaded through the whole BigUI/thesis-evidence build chain, breaking the Python test matrix and the manifest/catalog freshness checks too. | Bumped pip to 26.2.1 (`uv lock --upgrade-package pip --native-tls`, commit `41810e0`), regenerated the hardening manifests (commit `2e725f9`), then iteratively regenerated the full dependent build chain to a verified fixed point across 3 stable passes (commit `e44a308`). CI confirmed green (all jobs incl. `merge-gate`) via `gh run view --json jobs`. See the "Build-Chain Hash-Cascade Fix Pattern" row (2026-08-24) in `decisions.md` for the reusable fix pattern. |
| ISS-035 | 2026-08-20 | 2026-08-20 | Claude (do-next-step review) | `run-project-review.ps1` returned verdict `unsafe` ("Forbidden/generated/controlled artifacts are tracked") because 27 files (5 architecture-figure PDFs, several supervisor-delivery PDF/ZIP snapshots under `outputs/` and `presentations/`) were git-tracked despite matching the script's forbidden-artifact patterns and already being covered by `.gitignore` (`*[PDF omitted]`, `*[archive omitted]`, `outputs/**`). All 27 traced to the same historical commit `9163b2d` as ISS-032. | Ali confirmed via AskUserQuestion: `git rm --cached` on all 27 (files remain on disk, now correctly ignored going forward). Re-ran `run-project-review.ps1`; verdict changed from `unsafe` to `blocked` (only the standing EXP-005 0/24 gate remains, which requires real human labeling, not a fix). |
| ISS-001 | 2026-06-11 | 2026-06-11 | Codex | Workspace was not a Git repository. | Added `.gitignore` and initialized Git. |
| ISS-003 | 2026-06-11 | 2026-06-11 | Codex | Git was initialized but no baseline commit existed. | Created and pushed safe baseline to GitHub. |
| ISS-004 | 2026-06-11 | 2026-07-11 | Codex | Data sensitivity, provenance, and IRB constraints are not audited yet. | Completed the ethics-irb checklist and updated artifact-audit metadata status. |
| ISS-008 | 2026-06-14 | 2026-06-14 | Codex | `research-health.ps1` flagged tracked build_results_dashboard.py as forbidden. | Added a narrow allowlist for this dashboard script. |
| ISS-009 | 2026-06-14 | 2026-06-14 | Codex | Visualizer could show stale or mismatched model/result pairs. | PR #7 added exact matching and auto-clearing. |
| ISS-010 | 2026-06-16 | 2026-06-16 | Codex | Bundled presentation tool runtime was unavailable for PPTX deck. | Generated Markdown/HTML deck and used ignored PPTX builder. |
| ISS-015 | 2026-07-10 | 2026-07-10 | Codex | EXP-012 was not connected to the validated EXP-005 export. | Repaired explicit eligibility/leakage/provenance filtering and passed the canonical EXP-003 cross-check; safe N=0 still blocks computation. |
| ISS-016 | 2026-07-10 | 2026-07-10 | Codex | Next-step handoff/status drift and unsafe provisional feedback flows: seven-experiment/iteration-010 misreporting, adjudication leakage, self-asserted synthesis eligibility, partial output promotion, input/output aliasing, and linked-file writes. | Reconciled authoritative manifests/registry/ledger; required a separately validated hash-bound trusted export; added rollback publication, collision/protected/link guards, adjudication separation, and deterministic-only demo checks; full validation passes. |
| ISS-017 | 2026-07-25 | 2026-07-25 | Codex review | Exact-head review found stale artifact/manifest publication, Python numeric/boolean parity equivalence, and archive-history blindness after extension changes. | Added staged pair replacement with rollback, canonical-JSON parity comparison, raw-tree historical archive enumeration, and regression coverage; the complete release gate passes. |
| ISS-018 | 2026-07-25 | 2026-07-25 | Codex review | The candidate branch could self-edit its protected-change authorization, and the standalone architecture CLI could publish an artifact without its manifest after a partial failure. | Bound authorization to an external SHA-256 stored outside the candidate tree; added fail-closed mismatch tests; staged and transactionally published the CLI artifact/manifest pair with rollback coverage. |
| ISS-020 | 2026-07-28 | 2026-08-18 | Claude (deck fact-check / gap fill) | `EXPERIMENT_BENCHMARK_ANALYTICS_REPORT.md` stated EXP-036 "meets the declared unified and parity overhead limits" and graded it MEASURED_PASS, while the pinned artifact recorded `engineeringTargetMet = false`. | Corrected the 4 hard-coded strings in `scripts/build_experiment_benchmark.py` to state unified P95 fails at scale while parity P95/peak-memory pass and run-to-run variance is real; regenerated the full downstream chain (catalog, BigUI HTML, analytics report). |
| ISS-021 | 2026-07-28 | 2026-08-18 | Claude (deck fact-check / gap fill) | Tracked docs described the corpus as "179 student models," but 179 is scored evaluation rows (83 distinct student models, 165 model x setting evaluations). | Corrected `scripts/build_thesis_evidence_package.py` to "179 scored evaluations across 4 settings (83 distinct student models), aggregated into 27 Agent 4 patterns," cross-verified against `docs/research/governance/vego-ai-foundation-paper-record.md`. |
| ISS-050 | 2026-09-02 | 2026-09-02 | Claude (proposal Rev. 19 memory log) | Untracking the four `docs/dashboards/*.generated.*` files in 5d757f7 (required by `dashboard-health.ps1`) left `docs/visualizations/catalog.generated.md` stale, so `visualization_agent.py --check` failed and `main` went red on 5d757f7 and 1e462c3. Fixed by running the write-mode regeneration chain to a fixed point with the EXP-045 registration. | Regenerated `docs/visualizations/catalog.generated.md` and the dependent snapshots to a fixed point in 63e9418; Run `visualization_agent.py --check` (and the full CI check list) locally before any push that changes tracked generated files; the recorded hash-cascade pattern applies to untracking as well as editing. |
| ISS-051 | 2026-09-02 | 2026-09-02 | Claude (EXP-045 registration push) | pip-audit in CI flagged pypdf 6.15.0 (CVE-2026-84309/84310/84311, fixed in 6.16.1); after the locked bump, `vego_doctor.py` failed because its `EXPECTED_PACKAGES` pin still said 6.15.0. Bumped the lock and projection, aligned the doctor pin, regenerated hardening/SBOM/security-posture snapshots to a fixed point. | Commits 910754c, 6b1d448, 3fa4c4e, a671543; `vego_doctor.py` pins must move with `pyproject.toml`; add `uv run python scripts/vego_doctor.py` to the local pre-push check list. |
| ISS-056 | 2026-09-04 |  | Codex (artifact QA) | DOCX visual rendering could not run in this Windows environment because the bundled renderer lacks `pdf2image` and LibreOffice is unavailable. | Structural DOCX checks passed; PDF rendered and all three pages were visually inspected. Re-run DOCX page rendering in an environment with the missing dependencies before external release. |
| ISS-057 | 2026-09-04 |  | Codex (Task 1 recovery audit) | The historical evaluator logs point to an interaction log on an unavailable Google-Drive shortcut target; no corresponding log bytes are present in accessible local material. | Local search is exhausted and documented in `docs/research/phd-proposal/2026-09-04-interaction-log-recovery-receipt.md`. Human decision required before requesting the original from Iris/Arnon; no instrumentation or rerun is authorized. |
| ISS-058 | 2026-09-04 |  | Codex (Tasks 2–5 observer lane) | Direct instrumentation hooks into protected `VEGO-AI/framework/orchestrator.py` would fail the runtime hash guard and invalidate the evidence boundary. | Keep the additive observer/contract offline-verifiable and obtain a separately reviewed authorization/runner integration before any live one-setting run. |
| ISS-059 | 2026-09-06 |  | Codex (Study 2A preparation) | The ON/OFF comparison and separate Llama feasibility interface are prepared, but no condition has an authorized provider-backed run and no valid non-VEGO AirTravel baseline existed before this preparation. | Obtain independent review and a fresh explicit authorization; preserve separate condition roots/denominators and keep all claims descriptive until a later approved run. |


## Durable Decisions

<!--
last_updated: 2026-07-04
staleness_threshold_days: 14
-->

# Decisions

Durable decisions for this project.

## Decision Lifecycle Registry

| 2026-09-03 | Q&A Escalation Detection as Active Milestone | Active, supervisor-directed | The immediate technical path is read-only Q&A communication observability → transparent candidate alert rules → blind human validation sheets. Prior Agent-C score reconstruction/C2 bridge remains valid later-stage evidence; P-A/P-B/P-C replay, correction injection, and Condition-A selection are deferred. |

| Date | Title | Status | Notes / Superseded By |
|---|---|---|---|
| 2026-08-19 | Chapter 4 Completion Pass Ahead of Literature-Review Gate | Active, Ali-initiated | Ali explicitly chose to proceed with a Chapter 4 completion pass now, ahead of Iris's 2026-08-12 sequencing instruction (methodology starts only once the literature review is judged done, which it isn't yet per 3 independent verification reports this week). Sorted the chapter's 7 open items by kind: 4 packaged as supervisor decisions (`2026-08-19-chapter4-decisions-packet.md`), 1 resolved editorially (Plan A placement, §4.2), 1 turned into a real-world resourcing request (`docs/operations/study-resourcing-request-template.md`), 1 already answered by Chapter 5 precedent. See `chapter-4-completion-plan-2026-08-19.md`. |
| 2026-08-24 | Build-Chain Hash-Cascade Fix Pattern | Active | A `uv.lock` or hardening-manifest hash change cascades through `build_hardening_manifests.py` to `build_bigui_run_store.py` to `build_experiment_benchmark.py` to `build_bigui_catalog.py` to `build_bigui.py` to `build_thesis_evidence_package.py` to `build_thesis_progress_visual.py` to `build_thesis_review_manifest.py`, since each embeds an upstream sha256/count in its own output. A single mechanical bump (regenerate one file, commit) is not sufficient; fix is to run the full write-mode chain in dependency order repeatedly until a fixed point is reached, verified by an unchanged sha256 on `docs/research/bigui/experiment-catalog-snapshot-v1.json` across at least 2 consecutive passes, then run every script's `--check` mode individually with real exit codes (not chained via `set -e`, which was observed to not reliably halt this Bash tool's multi-line scripts) plus the full pytest suite before committing. Applied 2026-08-24 (commits `41810e0` pip 26.1.2->26.2.1 for PYSEC-2026-3721, `2e725f9` hardening manifest, `e44a308` full chain convergence at 103 accepted bundles / 932 observations, 0 safe labels unchanged) to fix a pre-existing CI-red `main` (confirmed red on the commit before mine too, via the weekly security-audit workflow). New `experiments/accepted-runs/EXP-033..040` files that appear during this regeneration are expected: deterministic synthetic/offline fixtures already hardcoded in `build_bigui_run_store.py` (`source=clone_safe_fixture`), append-only content-addressed by hash suffix — do not delete older hash-suffixed siblings. |
| 2026-08-19 | packageRevision Regenerate-Then-Rebind Pattern | Active | `THESIS_REVIEW_PACKAGE_MANIFEST.json`'s `packageRevision` cannot equal the commit currently being authored (the HTML badge and manifest sha256 are fixed at build time, before that commit's hash exists), so `--package-revision` defaulting to `git rev-parse HEAD` only works if HEAD already contains byte-identical tracked outputs. Fix pattern (already present in repo history as e.g. `0ac71b8`, `92850ec`, `ccd80b1`): commit 1 regenerates content and accepts a transient `packageRevision` `--check` failure; commit 2 immediately reruns `build_thesis_review_manifest.py --package-revision <commit-1-hash>` touching only the manifest, then both are pushed together so CI only ever evaluates the final consistent tip. Applied twice on 2026-08-19 (commits 64b6b79+99ff8ad, then 1537b78+4455138) to fix two prior-session CI-red pushes (`aba2450`, `ba65471`, `4ac2ed8`) that had instead tried to pin `sourceRevision`/`packageRevision` to literal current HEAD in a single commit. |
| 2026-08-03 | Independent Audit Standard for the Iris Closure Package | Active | 21-agent adversarial audit found 0 refuted findings; restored all 10 IRIS-EXP structure checks to PASS. |
| 2026-07-30 | July 29 Requirements-Closure Authority | Active working authority | The 19 requirements, 15 actions, and 10 open questions control the successor program, subject to bilingual confirmation and supervisor decisions. |
| 2026-07-30 | One-Plus-Three Research Architecture | Recommended, pending approval | One umbrella RQ and SQ1 selective intervention, SQ2 governed knowledge reuse, and SQ3 evaluation/transfer map to three studies. |
| 2026-07-30 | Plan A / Plan B and August 26 Fallback | Active working default | Plan A is a gated medical extension; Plan B completes through software/modeling and becomes the September default if any critical medical prerequisite is unproved. |
| 2026-07-30 | Three-Zone PhD Data Boundary | Active | Repository metadata/aggregate evidence, private working Drive, and restricted VDI are separated; patient rows and restricted derivatives never enter Git, ordinary Drive, or online LLMs. |
| 2026-06-11 | Shared Agent Memory | Active | Uses AGENTS.md, CLAUDE.md, and docs/agent-memory/ |
| 2026-06-11 | Current-State First Workflow | Active | Stored in current-state.md and progress.md |
| 2026-06-11 | Scripted Prompt Memory | Active | start/finish scripts for memory updates |
| 2026-06-11 | PhD Research Workspace Architecture | Active | Folders for research, thesis, experiments |
| 2026-06-11 | Git And Generated Artifact Policy | Active | Ignores local large data/caches, tracks code/docs |
| 2026-06-11 | Safe GitHub Baseline | Active | Pushed safe baseline to private repo |
| 2026-06-11 | Claude Bootstrap Prompt | Active | Startup instructions at claude-bootstrap-prompt.md |
| 2026-06-11 | Workspace Diagram Format | Active | Markdown + Mermaid diagram in workspace-diagram.md |
| 2026-06-12 | Claude Local Settings Policy | Active | Ignored machine-specific permission files |
| 2026-06-12 | Human-AI Co-Reasoning Milestone 2 | Active | feedback manager and test harness |
| 2026-06-12 | Research OS Infrastructure | Active | Ethics, management, and audit registers |
| 2026-06-12 | Confluence Wiki Target Site | Active | Target space ~71202099edcf0e26ec40cea521806deb9e9687 |
| 2026-06-12 | Reusable Human Judgment Story | Active | Focus on framework, inert memory, controlled M4 |
| 2026-06-12 | Memory Advisory Layer (M4A) Merge | Active | Squashed to main; advisory-only verification |
| 2026-06-13 | Milestone Tags & Handoff | Active | Lightweight tags created, Claude prompts written |
| 2026-06-13 | KPI Register Dashboard | Active | Track dashboards locally and in Confluence outbox |
| 2026-06-13 | Dashboard Health Gate | Active | dashboard-health.ps1 script blocks invalid outbox |
| 2026-06-13 | Runtime Dashboard Snapshot | Active | snapshot.generated.md embedded in Progress page |
| 2026-06-13 | Confluence Manual Sync Pack | Active | Outbox generator fallback for blocked access |
| 2026-06-14 | Conditional M4B-1 Approval Contract | Active | comparison only, Agent 4 frozen |
| 2026-06-14 | Results Dashboard Implementation | Active | offline build_results_dashboard.py merged |
| 2026-06-14 | Visualizer UX and Match Hardening | Active | PR #7 exact matching, auto-clear stale models |
| 2026-06-14 | Evaluation Report and Register | Active | registry.md and evaluation-report.md created |
| 2026-06-14 | EXP-001 Mechanism Readiness | Active | mechanism validation on 27 comparisons |
| 2026-06-14 | EXP-002 Expert Labeling Package | Active | Identified 24 safe candidate rows |
| 2026-06-16 | Supervisor Zoom Preparation | Active | demo prep scripts and slide decks |
| 2026-06-16 | EXP-003 Scaffolding & Accuracy | Active | accuracy evaluation path tooling |
| 2026-06-16 | EXP-004 Policy Sensitivity Tooling | Active | policy sensitivity checks on synthetic labels |
| 2026-06-17 | EXP-005 Real-Label Gate Tooling | Active | blind labeling sheets, κ stats, adjudication |
| 2026-06-21 | VEGO Workbench Launcher | Active | open-vego-workbench.ps1 command-line tool |
| 2026-06-22 | Strategic Review and Hardening | Active | validation consistency checks and strict gates |
| 2026-06-23 | Supervised Codex Next-Step Loop | Active | run-codex-next-step.ps1 for loop execution |
| 2026-06-23 | Project Review Architecture | Active | run-project-review.ps1 updates review-state.md |
| 2026-06-23 | Generated Progress Visualizations | Active | progress visualizations generated for dashboard |
| 2026-06-23 | Progress Update Architecture | Active | defines e2e report, Confluence, and 4-hr updates |
| 2026-06-23 | Progress Update Diagram | Active | diagrams the progress update operational contract |
| 2026-06-23 | E2E Progress Report and Web Page | Active | build-e2e-progress-report.ps1 web output |
| 2026-06-23 | HITL Resource Pack | Active | literature and tooling templates for Chapter 2 |
| 2026-06-24 | Hardened Annotation Pack | Active | 24 safe blind rows split, Dev/Holdout split |
| 2026-07-03 | Tiered Memory & Log Archival | Active | T1/T2/T3 compiled files, session-log pruning |

## 2026-06-11 - Shared Agent Memory

- Decision: Use root-level `AGENTS.md` for Codex instructions and `CLAUDE.md` for Claude instructions.
- Decision: Store shared progress, issues, decisions, and rollback notes in `docs/agent-memory/`.
- Reason: Both agents can read plain Markdown files, which keeps the history portable and easy to review.
- Consequence: Every future prompt that involves meaningful work should update the memory files before the final response.

## 2026-06-11 - Current-State First Workflow

- Decision: Add `docs/agent-memory/current-state.md` and `docs/agent-memory/progress.md`.
- Reason: Future prompts need a quick way to understand project flow without rereading every historical entry.
- Consequence: Agents should use current-state and progress as the first memory resources, then consult detailed logs/issues/decisions as needed.

## 2026-06-11 - Scripted Prompt Memory

- Decision: Add PowerShell scripts for prompt start and prompt finish.
- Reason: The user wants memory files pulled and updated automatically at each prompt.
- Consequence: Agents should run `scripts/agent-memory-start.ps1` at prompt start, then `scripts/agent-memory-finish.ps1` before the final response when meaningful work happened.
- Boundary: Scripts can standardize memory updates, but agents must still use judgment for issues, decisions, and current-state changes.

## 2026-06-11 - PhD Research Workspace Architecture

- Decision: Preserve the extracted source package in `VEGO-AI/` and build the PhD research architecture around it at the repository root.
- Decision: Use dedicated folders for experiments, data zones, literature, papers, thesis, reports, outputs, tests, future cleaned source, and project documentation.
- Reason: The project needs to support scientific traceability, reproducibility, writing, data governance, prompt memory, and software evolution at the same time.
- Consequence: Research notes and thesis/paper materials should stay outside `VEGO-AI/`; source behavior changes inside `VEGO-AI/` should be linked to experiments or decisions.

## 2026-06-11 - Git And Generated Artifact Policy

- Decision: Initialize Git and add `.gitignore` before the first baseline commit.
- Decision: Ignore large archives, generated outputs, raw/interim/processed/external data zones, Python caches, virtual environments, and generated compiled memory.
- Reason: Version control should track source, docs, templates, and lightweight reproducibility records without accidentally committing secrets, bulky generated data, or disposable artifacts.
- Consequence: A baseline commit is still needed before Git gives strong rollback support.

## 2026-06-11 - Safe GitHub Baseline

- Decision: Publish directly to private GitHub repo `AliHamed17/Vego-Ai` on `main` without force-pushing.
- Decision: Preserve remote README-only history with an `ours` merge.
- Decision: Exclude root PDF, zip archives, generated outputs, compiled memory, model files, analysis files, eval outputs, visualizer bundled data, generated review queues, bundled executable, and `get-pip.py` from the safe baseline.
- Reason: The repo should have durable GitHub history while avoiding premature upload of research artifacts that need data/IRB review.
- Consequence: Deferred artifacts remain local and ignored until the data/provenance audit decides what can be shared.

## 2026-06-11 - Claude Bootstrap Prompt

- Decision: Keep a paste-ready Claude startup prompt at `docs/agent-memory/claude-bootstrap-prompt.md` and link it from `CLAUDE.md`.
- Reason: Fresh Claude sessions need a reliable way to load shared memory, respect the PhD architecture, and follow the same Git/data-safety workflow as Codex.
- Consequence: When starting Claude, the user can paste the bootstrap prompt so Claude treats project memory as context and updates it before final responses.

## 2026-06-11 - Workspace Diagram Format

- Decision: Use Markdown plus Mermaid for the first workspace architecture diagram at `docs/architecture/workspace-diagram.md`.
- Reason: GitHub renders Mermaid diagrams directly, so the diagram stays reviewable as text and avoids binary asset management.
- Consequence: Future architecture diagrams can follow the same text-first pattern unless a paper-quality figure export is needed.

## 2026-06-12 - Claude Local Settings Policy

- Decision: Ignore `.claude/*.local.json`.
- Reason: Claude local settings can contain machine-specific permission state and absolute paths that are not portable project configuration.
- Consequence: Portable Claude instructions remain tracked in `CLAUDE.md` and `docs/agent-memory/claude-bootstrap-prompt.md`; local permission state stays untracked.

## 2026-06-12 - Research OS And Confluence Sync

- Decision: Use metadata-only research registers for artifact audit, provenance, and publishability before exposing deferred artifacts.
- Decision: Generate five curated Confluence page bodies after meaningful prompts: wiki home, current state, progress dashboard, update changelog, and research operations.
- Decision: Keep Confluence target IDs in ignored `docs/confluence/wiki-sync-config.local.json`; track only `wiki-sync-config.template.json`.
- Reason: The project needs an external latest wiki without copying controlled research artifacts or local machine state into Git/Confluence.
- Consequence: Until real Confluence IDs are configured, agents generate ignored outbox pages and report live sync as pending.

## 2026-06-12 - Confluence Live Target

- Decision: Use Confluence page `294914` in `https://alih10j.atlassian.net/wiki` as `VEGO-AI Wiki Home`.
- Decision: Use child pages under `294914` for current state, progress dashboard, update changelog, and research operations.
- Decision: Store actual target/page IDs only in ignored `docs/confluence/wiki-sync-config.local.json`.
- Reason: The user provided the Confluence edit URL and requested the wiki stay updated with the latest project state.
- Consequence: Live sync is blocked until Atlassian Rovo access is granted for cloud `724252a1-a5b7-45a5-b6ec-27a8292197ec`; generated outbox remains the pending update meanwhile.

## 2026-06-13 - Dashboard/KPI Tracking

- Decision: Use tracked Markdown files under `docs/dashboards/` as the source of truth for progress, KPI, and results dashboards.
- Decision: Generate a dedicated `VEGO-AI Progress Dashboard` Confluence outbox page from those tracked dashboard sources.
- Decision: Generate an ignored runtime snapshot at `docs/dashboards/status-snapshot.generated.md` and embed it in the Confluence Progress Dashboard.
- Decision: Generate an ignored manual sync pack at `docs/confluence/manual-sync-pack.generated.md` with curated page bodies, target metadata, and hashes for approved fallback publishing.
- Decision: Add dashboard files to research health so progress tracking becomes part of the standard quality gate.
- Decision: Add `scripts/dashboard-health.ps1` to verify dashboard sources, KPI rows, Confluence builder wiring, config page slots, and generated outbox readiness.
- Reason: The user wants progress and research results visible in Confluence without copying controlled artifacts or relying on ad hoc summaries.
- Consequence: Agents should update `docs/dashboards/` whenever progress, KPI values, validated results, or Confluence tracking status changes, then regenerate the runtime snapshot/Confluence outbox/manual sync pack and run `.\scripts\dashboard-health.ps1 -RequireOutbox`.

## 2026-06-12 - Milestone Branch/PR Discipline + Baseline Preservation

- Decision: From Milestone 3 onward, milestone CODE goes on a feature branch (e.g. `feature/human-judgment-memory`) and lands on `main` via a reviewed PR. No direct commits of milestone code to `main` without review (applies to both Codex and Claude). Shared-memory/doc updates may still be committed directly.
- Decision: Preserve the official VEGO-AI baseline (`2eeccb1`) as tag `official-vego-ai-baseline` and branch `baseline/official-vego-ai` on `origin`.
- Decision: Adopt `main` as the canonical development branch (it already carries baseline + M1 + M1.2 + M2 at `217150c`). Do NOT merge `master` into `main` with `--allow-unrelated-histories`. Keep `master` + `feature/human-review-queue` as a granular-history archive; PR #1 closed as superseded.
- Reason: A clean, reviewable audit trail is required for thesis reproducibility; M1/M2 had been published directly to `main`, losing per-milestone review.
- Consequence: Future milestones use feature branches + PRs into `main`, approved before merge.
- Status: M1 (Human Review Queue) + M1.2 (review_signature) + M2 (Human Feedback Manager) complete on `main`. M3 (Human Judgment Memory) was implemented and published as commit `5e109e5`.

## 2026-06-12 - Reusable Human Judgment Research Spine

- Decision: Make reusable human judgment in AI-assisted domain model assessment the explicit research spine for VEGO-AI.
- Decision: Use the main research question: "What approaches have been proposed to support human-AI collaboration in AI-assisted domain modeling and model assessment, and how can they inform the design of reusable human judgment mechanisms in systems such as VEGO-AI?"
- Decision: Use the contribution statement: "selectively triggered, structurally captured, and stored as reusable knowledge."
- Reason: The research review identified this framing as the strongest MSc thesis foundation and the clearest bridge to PhD continuation.
- Consequence: Research docs, thesis outline, evaluation plan, roadmap, and claim/evidence tracking should align to M1 selective review, M2 structured feedback, M3 reusable memory, M4A advisory evidence, and M4B controlled reuse.

## 2026-06-12 - M3 Inert Boundary And M4 Controlled Reuse

- Decision: Treat M3 Human Judgment Memory as implemented but inert.
- Decision: Do not wire memory into Agent 4, embeddings, guideline mutation, or the visualizer until a separate controlled experiment is run.
- Reason: The thesis needs a clean distinction between building reusable knowledge and proving that reused knowledge improves AI-assisted variability interpretation.
- Consequence: M4A is advisory-only; M4B/EXP-001 is the next behavior-changing controlled experiment and behavior-improvement claims wait for C4B evidence.

## 2026-06-12 - M4A Advisory Boundary And M4B Design Gate

- Decision: Treat M4A as an advisory-only bridge from Human Judgment Memory to future model assessment.
- Decision: M4A may retrieve relevant human judgments and generate `memory_advice.json`, but it must not change Agent 4 classifications, prompts, guidelines, visualizer behavior, or baseline evaluation outputs.
- Decision: M4B is design-only until separately reviewed; it must preserve original Agent 4 output and produce a comparison rather than replacing the baseline classification.
- Reason: PR #2 showed the safe bridge needed before any behavior-changing memory-informed reclassification.
- Consequence: Future M4B plans must include `original_agent4_classification`, `memory_advice`, `memory_informed_classification`, `memory_informed_differs_from_original`, `requires_human_review_after_memory`, `evaluation_leakage_status`, `decision_trace`, `policy_version`, and `human_memory_used`.

## 2026-06-13 - M4A Reproducibility Tags

- Decision: Use lightweight Git tags for the M3 code state, M4A code state, and M4A research-state snapshot.
- Decision: Keep `milestone-m3-human-judgment-memory` at `5e109e5f9f2073d9cdc2325bcea2823d57c77882`, `milestone-m4a-memory-advisory` at `ecd097245c463089a5721d68b17d6b22a1005a43`, and `research-state-m4a` at `28289405fc7cb687665f949bf039355a97967c59`.
- Reason: Thesis and artifact review need stable, reproducible anchors for the code milestone and the surrounding research-story state.
- Consequence: Future artifact manifests should reference these tags instead of relying only on moving branch names.

## 2026-06-14 - M4B-1 Conditional Approval Contract

- Decision: Treat M4B-1 as a deterministic, experimental, parallel-comparison layer, not a baseline Agent 4 behavior change.
- Decision: Use `memory_informed_differs_from_original` and always keep `ai_behavior_changed_in_baseline=false`.
- Decision: Require `policy_version="memory-informed-classifier-v1"`, `decision_trace`, `requires_human_review_after_memory`, and `evaluation_leakage_status` on future M4B-1 outputs.
- Decision: Defer M4B-2, Agent 4 `resolve_with_answers`, LLM/API calls, embeddings, visualizer changes, and baseline output overwrites.
- Decision: Future M4B-1 implementation must use branch `feature/memory-informed-comparison` and PR review; Codex must not commit VEGO-AI milestone implementation paths directly to `main`.
- Reason: The M4B review approved the research direction only if reusable memory remains a controlled comparison mechanism with leakage tracking and reproducible deterministic rules.
- Consequence: Claude can implement only the approved M4B-1 scope after confirming `docs/research/m4b-conditional-approval.md`; improvement claims wait for EXP-001/C4B evidence.

## 2026-06-14 - Offline Results Dashboard Boundary

- Decision: Add a local/offline VEGO-AI results dashboard generator under `[controlled analysis path omitted]build_results_dashboard.py`, with generated HTML/JSON output ignored under `VEGO-AI/reports/results_dashboard/`.
- Decision: Track only the generator, tests, docs, schema, and ignore policy; do not track generated dashboard outputs or controlled result artifacts.
- Decision: The dashboard is evidence reporting only: it reads existing JSON/JSONL artifacts, performs no LLM/API/network calls, does not modify baseline outputs, and does not change Agent 4 or M4A classifications.
- Reason: The project needs visual, reviewable research metrics without weakening IRB/data boundaries or confusing reporting with model behavior.
- Consequence: Use PR #5 for review/merge; keep `ai_classification_changed_count=0` as the M4A boundary check and continue treating M4B as a separate controlled experiment.

## 2026-06-14 - Visualizer Pairing And Read-Only Research Panels

- Decision: The visualizer must treat model/result pairing as an explicit case-id contract: Agent C results use `agentC_case_<case_id>.json`, model files use the substring before the first underscore, and auto-load searches only for files beginning with `<case_id>_`.
- Decision: When no exact case-prefix model exists, the visualizer must clear the previous model selection and show `No matching model found`; it must never keep a stale model silently.
- Decision: Manual model changes must be validated against the currently selected result and surfaced as Matched, Mismatch, Unknown, or No matching model found in a persistent top banner.
- Decision: Visualizer research panels are read-only only; they may display M1/M2 review, M3 memory, M4A advice, and M4B-1 comparison sidecars, but must not write feedback, memory, advice, comparison, eval output, model, or analysis artifacts.
- Reason: The review identified stale visualizer pairing as the highest-risk UX issue because it could make a wrong assessment appear normal.
- Consequence: PR #7 carries the UI/helper/test implementation; any future visualizer work must preserve the no-silent-mismatch boundary and avoid changing Agent 4 or evaluator behavior.

## 2026-06-14 - System Validation Artifact And Dashboard Generator Allowlist

- Decision: Track `VEGO-AI/reports/system_validation_report.md` as a research validation artifact.
- Decision: Allowlist only `[controlled analysis path omitted]build_results_dashboard.py` in `scripts/research-health.ps1` because it is an intentionally tracked source generator, not a controlled/generated analysis artifact.
- Decision: Keep all other `[controlled analysis path omitted]` artifacts forbidden unless separately reviewed and explicitly allowlisted.
- Reason: The full-system QA report is useful thesis/research evidence, and the dashboard generator is now part of the reproducibility infrastructure.
- Consequence: `project-health`, `research-health`, and `dashboard-health` pass while controlled analysis spreadsheets/outputs remain excluded.

## 2026-06-14 - Visualizer UX Merge Anchor

- Decision: Treat PR #7 as the validated visualizer UX clean state after real-display GUI validation and squash merge.
- Decision: Use lightweight tag `research-state-visualizer-ux-clean` at commit `78b261e033fc4f3f66170985a884aa5cd0a0cfd2`.
- Reason: The stale model/result mismatch risk affected research interpretation, so the fixed UI state needs a stable reproducibility anchor.
- Consequence: Future visualizer work should preserve exact case-id pairing, stale-model clearing, visible match status, read-only research panels, and unchanged AI behavior.

## 2026-06-14 - Shared Claude/Codex State Report

- Decision: Keep a high-level shared state report at `docs/agent-memory/shared-state-report.md` and include it in generated compiled memory.
- Reason: Claude and Codex need one compact research/governance narrative that explains the milestone chain, contribution, boundaries, and next evaluation direction without relying only on chronological logs.
- Consequence: Future agents should read the report at startup, but still rely on `current-state.md` and Git for exact moving branch/PR status.

## 2026-06-14 - Implementation Freeze And Evaluation Pivot

- Decision: Treat the implemented prototype as complete through M4B-1 for evaluation purposes, anchored by `research-state-m4b1-deterministic-comparison` and the later visualizer UX tag `research-state-visualizer-ux-clean`.
- Decision: The next major deliverable is `docs/research/evaluation-report.md`, not additional feature implementation.
- Reason: The engineering prototype is strong, but empirical evidence is still incomplete; the thesis now needs expert-label comparison, leakage-aware evaluation, and dashboard-backed tables/figures.
- Consequence: M4B-2, Agent 4 memory-based reclassification, LLM resolve modes, embeddings, automatic guideline rewriting, and GUI feedback editing remain blocked until M4B-1 evaluation evidence exists.

## 2026-06-14 - EXP-001 Initial Evaluation Interpretation

- Decision: Treat the first EXP-001 output as mechanism/readiness evidence only.
- Reason: The run has 27 comparison rows and valid leakage tracking, but only 3 expert-labeled rows are available and all are same-pattern Human Judgment Memory cases; there are 0 generalization-safe expert-labeled rows.
- Consequence: The thesis may say M4B-1 preserves baseline output, produces reproducible comparison tables, and flags 2 cases for human review after memory. It must not claim accuracy improvement or generalization until held-out expert labels are added and evaluated.

## 2026-06-14 - EXP-002 Expert Labeling Before More Features

- Decision: Move from mechanism validation to expert-label collection through EXP-002 before implementing more memory behavior.
- Decision: Treat the generated EXP-002 labeling package as the next research artifact: 27 rows, 24 generalization-safe candidates, 3 existing same-pattern labels, and 27 recommended labeling targets.
- Reason: The weak point is empirical evidence, not architecture; M4B-1 cannot support accuracy/generalization claims until independent labels exist.
- Consequence: M4B-2, Agent 4 `resolve_with_answers`, LLM/API reclassification, embeddings, automatic guideline rewriting, and GUI feedback editing remain blocked. The next manual work is expert labeling and rationale collection.

## 2026-06-16 - EXP-003 Accuracy Improvement Gate

- Decision: Treat EXP-003 as the evaluation-first path for any future accuracy-improvement claim or deterministic M4B-1 policy refinement.
- Decision: Generate full and blind expert-labeling sheets, but do not treat original Agent 4 output, copied analysis files, or same-pattern memory as independent ground truth.
- Decision: If there are zero generalization-safe expert labels, the required conclusion is `Accuracy improvement cannot be evaluated yet.`
- Decision: If there are fewer than 20 generalization-safe expert labels, any accuracy or macro-F1 result is pilot evidence only.
- Decision: Do not implement M4B-1.1, M4B-2, Agent 4 changes, LLM/API calls, embeddings, or baseline-output overwrites until EXP-003 provides enough safe labels and a reviewed policy-refinement plan exists.
- Reason: The strict evaluation found no independent benchmark, 0 safe labels, and 0 memory-informed classification differences.
- Consequence: The next research action is expert labeling and error analysis, not classifier behavior change.

## 2026-06-16 - EXP-004 Policy Sensitivity Boundary

- Decision: Add EXP-004 as a policy-sensitivity simulation harness only.
- Decision: Treat EXP-004 synthetic deltas as pipeline/risk screening, not expert evidence and not accuracy improvement.
- Decision: Keep current M4B-1 as the only implemented behavior; candidate variants must not modify Agent 4, M4B-1 production behavior, M4B-2, baseline outputs, `[controlled eval-output path omitted]`, LLM/API behavior, or embeddings.
- Decision: Use EXP-004 after real EXP-003 labels exist to compare candidate policies against non-synthetic evidence.
- Reason: The user wants to keep working toward better accuracy, but the project still lacks independent labels; safe progress requires measurable simulations and gates rather than unreviewed behavior changes.
- Consequence: Accuracy improvement remains unclaimed. Candidate M4B-1.1 policy implementation remains blocked until EXP-003 labels and reviewed error analysis justify a specific rule.

## 2026-06-17 - EXP-005 Real-Label Accuracy Gate

- Decision: Add EXP-005 as the supervisor/expert label-review and real-label policy gate before any deterministic accuracy-improvement change.
- Decision: Use the EXP-005 blind CSV for expert labeling so original Agent 4 and memory-informed classifications are hidden from the reviewer.
- Decision: Use the EXP-005 full CSV as audit context and as the merged downstream input when a filled blind sheet is supplied.
- Decision: Keep the strict gate: `0` safe labels means `Accuracy improvement cannot be evaluated yet`; `1-19` safe labels means pilot evidence only; `20+` safe labels allows quantitative reporting with validity threats, not automatic improvement claims.
- Decision: Keep M4B-1.1, M4B-2, Agent 4 changes, LLM/API calls, embeddings, baseline-output overwrites, and `VEGO-AI/eval_output` changes blocked until EXP-005 evidence and supervisor/reviewer approval justify a specific policy.
- Reason: EXP-004 showed candidate policy risk synthetically, but real accuracy improvement needs independent, leakage-safe expert labels.
- Consequence: The immediate accuracy work is filling and validating EXP-005 labels, not changing classifier behavior.

## 2026-06-21 - Local VEGO Workbench Launcher

- Decision: Use `scripts/open-vego-workbench.ps1` as the main local startup command for result review, EXP-005 labeling, demos, and visualizer opening.
- Decision: Keep the launcher operational only: it may regenerate ignored dashboard/EXP-005/wiki outputs and open local files, but it must not modify Agent 4, M4B-2, `VEGO-AI/eval_output`, baseline outputs, LLM/API behavior, or embeddings.
- Reason: Manual path mistakes were slowing down review and demos; one repo-root command reduces friction without changing research behavior.
- Consequence: Daily review can use `.\scripts\open-vego-workbench.ps1`, GUI review can use `.\scripts\open-vego-workbench.ps1 -Gui`, and non-interactive validation can use `.\scripts\open-vego-workbench.ps1 -All -NoOpen`.

## 2026-06-22 - Strategic Review Evidence Freeze

- Decision: Freeze new feature work and treat EXP-005 real labels as the next required evidence gate.
- Decision: Keep M4B-2, Agent 4 changes, LLM/API reclassification, embeddings, baseline overwrites, and `VEGO-AI/eval_output` changes blocked.
- Decision: Treat EXP-004 synthetic results and same-pattern labels as mechanism/risk-screening evidence only, not real accuracy improvement.
- Decision: Add a second reviewer or supervisor adjudication path before treating EXP-005 labels as strong quantitative evidence.
- Reason: The strategic review found that the architecture is technically strong, while the remaining blocker is empirical validity: 0 supplied EXP-005 labels and 0 generalization-safe valid labels.
- Consequence: The next move is expert-label collection, validation, and strict interpretation, not classifier or policy implementation.

## 2026-06-22 - EXP-005 Evidence Coverage

- Decision: Keep the blind EXP-005 sheet as the first-pass expert-labeling file and add a separate generated adjudication sheet for reviewer-2 or supervisor review.
- Decision: Generate an EXP-005 evidence verdict and reproducibility manifest for every package/rerun.
- Decision: Treat generated EXP-005 verdicts and manifests as ignored local evidence artifacts until publishability is approved.
- Reason: The project needs stronger reliability and reproducibility without changing VEGO-AI classification behavior.
- Consequence: Evidence reruns should review `evidence_verdict.md`, `reproducibility_manifest.json`, reviewer reliability counts, and protected-path diff status before any thesis claim or tag.

## 2026-06-22 - EXP-005 Synthetic Trial Boundary

- Decision: Allow synthetic EXP-005 labels only in a separate ignored trial folder and mark them with reviewer ID `SYNTHETIC_NOT_HUMAN`.
- Decision: Treat the synthetic policy-candidate review as design-only guidance, not real evidence and not authorization for implementation.
- Decision: Keep M4B-1.1, M4B-2, Agent 4 changes, LLM/API calls, embeddings, baseline-output overwrites, and `VEGO-AI/eval_output` changes blocked after the synthetic trial.
- Reason: The synthetic trial confirmed the pipeline works and current M4B-1 has 0.00 pp synthetic accuracy delta, while candidate policy gains depend on synthetic assumptions.
- Consequence: Real EXP-005 labels remain the required next step before any accuracy claim or policy refinement.

## 2026-06-23 - Supervised Next-Step Loop

- Decision: Use `scripts/run-codex-next-step.ps1` as the supervised one-cycle loop for "continue" or "next step" prompts.
- Decision: Keep the loop per-prompt and explicit; do not represent it as a background service or unattended 24/7 automation.
- Decision: The loop may inspect state, open blocked materials, refresh wiki/dashboard outputs, and run EXP-005 downstream only when real labels are saved, complete, valid, and the sheet is closed.
- Decision: The loop must stop on missing labels, invalid/incomplete labels, locked CSV files, or protected VEGO behavior diffs.
- Reason: The user wants Codex to keep making progress with minimal intervention, but the project has hard research and behavior-safety gates.
- Consequence: Future continuation prompts should run the loop first, inspect `reports/generated/next_step_loop/last-run.md`, then perform any safe follow-up work.

## 2026-06-23 - Project Review Architecture

- Decision: Add a structured project review architecture connected to shared agent memory.
- Decision: Keep `docs/agent-memory/review-state.md` as the tracked fast review state and include it in compiled memory.
- Decision: Use `scripts/run-project-review.ps1` to produce ignored review reports under `reports/generated/project_review/`.
- Decision: Use fixed review verdicts: `green`, `yellow`, `blocked`, and `unsafe`.
- Decision: When EXP-005 blocks the next-step loop, run the project review cycle so Codex and Claude get a full audit report instead of only repeating the label blocker.
- Reason: The project now needs repeatable governance/evidence review more than new feature work.
- Consequence: Future review/continue prompts should inspect `reports/generated/project_review/latest-review.md`, keep safe claims separate from blocked claims, and update review-state memory when the review changes project state.

## 2026-07-04 - July 2026 Supervisor Redirect Adopted As A Provisional Working Plan

- Repository planning decision: use `docs/research/extension-plan-2026-07-supervisor-redirect.md` as the active provisional framework-first plan while preserving the parked evaluation gate.
- Proposed design: the human-judgment layer is reframed as an H-layer with skills S1-S7 mapped to H1/H2/H3. Full passive E1-E14 observation, active routing, and agent decomposition remain M-02/M-03 choices, not recorded supervisor decisions.
- Decision: Rename M1/M2/M3 to H1/H2/H3 in NEW research docs and diagrams only; code, schemas, tags, and history keep M-names until a dedicated rename PR is approved.
- Working interpretation pending participant confirmation: M4 is deferred to a separate parked evaluation view; framework and evaluation live in separate diagrams.
- Safety boundary: the expert is a real person; detailed dosage, reviewer roles, source set, round bound, and authority matrix remain M-03..M-05 choices. On timeout, preserve baseline behavior and park the item; no H3 auto-application. S6 is proposal-only.
- Decision: EXP-005 stays the real-label gate of the parked evaluation track; all existing claim boundaries and behavior blocks remain in force; this phase is documentation-only (no VEGO-AI source changes).
- Reason: Machine ASR and machine-derived meeting notes support the redirect, but wording, attribution, and D1-D12 still await participant confirmation.
- Consequence: Offline docs/contracts/experiments may advance. Live implementation stays blocked until M-05 and a separate exact-file authorization are explicitly recorded.

## 2026-07-04 - MediVARIA Drafted As Proposed PhD/Future Work

- Proposal: MediVARIA is a post-meeting planning draft for possible medical-domain transfer; it is not an Iris/Arnon-endorsed clinical project. Study plan: `docs/research/medivaria/medivaria-study-plan.md`.
- Working boundary: the MSc thesis stays education-domain in scope; MediVARIA appears only as motivation, transferability discussion, and proposed future work unless separately approved.
- Governance boundary: no patient data in this repository; ethics/IRB review precedes any future data work; education-domain results are never clinical-performance evidence; partner/negotiation details stay out of tracked docs while TBD.
- Open M-06 choice: whether H-layer detail specs should be domain-parameterized for future transfer. Education remains the MSc empirical scope.
- Reason: User direction on 2026-07-04 to integrate the MediVARIA study and enhance project/thesis per the supervisor's guidance; MediVARIA operationalizes phd-extension-ideas idea 1 and gives ideas 2, 3, and 5 their clinical setting.
- Consequence: 2026-07-15 meeting agenda gains the MediVARIA items (study-plan section 8); TASK-043 tracks MV-P0; all existing evidence gates and the framework-first sequencing remain unchanged.

## 2026-07-10 - Offline Feedback Generalization and Demo Boundary

- Decision: Treat iteration manifests as authoritative: iteration 010 is a `NEUTRAL`, `reliability_only` snapshot of the six-experiment replay suite, not an interactive-demo or quality-improvement result.
- Decision: Implement Vector 1 only as a deterministic, offline proposal generator. It may emit eligibility, grouping, conflict, provenance, and synthesis-request artifacts, but it must not call an LLM, inject Agent B, or mark any rule runtime-eligible.
- Decision: Require S5-verified or explicitly supervisor-adjudicated status, an allowlisted trusted origin, `trusted_memory_eligible = true`, `reusable = true`, a nonblank reuse scope, provenance references, no unresolved override, and a separately validated manifest binding the exact export hash and eligible record IDs before feedback can enter a synthesis group.
- Decision: Keep the supervisor CLI as an isolated offline demo. Ordinary demo feedback and `needs_adjudication` candidates use separate files; every record is unconfirmed and `trusted_memory_eligible = false`; semantic checking remains disabled.
- Decision: Reject generated-output paths under repository `VEGO-AI/` and `.git/` for both the generalizer and demo.
- Reason: M-02 through M-05 remain deferred, current prototype records are informal/unadjudicated, EXP-005 has zero valid safe labels, and automatic prompt/context delivery would cross the protected decision boundary.
- Consequence: The current generalizer result is `BLOCKED_NO_VERIFIED_FEEDBACK` with zero candidate rules. Any LLM synthesis, trusted-memory reuse, Agent B context delivery, or live listener work requires new evidence and explicit authorization.

## 2026-07-28 - One-Command Full Evaluation and Component Verdict Standard

- Decision: `scripts/run-full-evaluation.ps1` is the canonical end-to-end evaluation entry: 16-check verification gate -> experiment benchmark (--refresh) -> per-component contribution report -> program overview/charts -> advisory analyst. Evidence stages gate the exit code; the analyst stage is advisory and never gates.
- Decision: Per-agent/component value questions are answered only by `scripts/build_agent_contribution_report.py` verdicts (CONTRIBUTING / PARTIAL / NOT-YET-MEASURABLE), each backed by named measured signals with N and source paths, plus an explicit "verdict changes if" condition. Narrative layers (LLM analyst) must carry the ADVISORY banner and may never introduce numbers absent from the cited artifacts.
- Decision: When canonical sources legitimately change, re-anchor derived artifacts in this order: commit sources -> `build_thesis_evidence_package.py --source-revision HEAD` + review manifest -> `build_bigui_catalog.py --source-revision <full sha>` -> `build_bigui.py` -> commit. Skipping the catalog/HTML step leaves determinism tests failing (and pytest can stall for minutes computing a difflib diff of the multi-megabyte research hub HTML).
- Reason: The 2026-07-28 evaluation phase surfaced each of these as a real failure mode while wiring the pipeline end to end.
- Consequence: Continuation prompts can run one command for the full program verdict; component claims stay evidence-bound while the EXP-005 gate holds at 0/24 labels.

## 2026-07-30 - July 29 Doctoral Requirements-Closure and Proposal Program

- Decision: Treat the July 29 requirement/action/open-question registers as the successor working authority. The July 1 redirect and July 24 continuation remain preserved as absorbed legacy plans; no older file is silently deleted.
- Decision: Recommend exactly one umbrella research question plus SQ1 selective intervention, SQ2 governed knowledge reuse, and SQ3 evaluation/transfer, mapped one-to-one to intervention architecture, judgment lifecycle, and evaluation/transfer studies.
- Decision: Keep the working wording provisional until Iris and Arnon decide it. The August 5 pre-read is prepared but not recorded as shared or sent.
- Decision: Use Plan A as a staged medical extension and Plan B as a complete software/modeling route. If any critical medical prerequisite remains unproved on August 26, use Plan B in the September proposal and retain Plan A only as a conditional annex.
- Decision: Enforce six sequential pre-row-level medical gates: use-case, people, authorization, ethics/privacy, environment, and protocol. Current readiness is 0/6; integrity, pilot, and export controls are downstream and cannot replace an entry gate.
- Decision: Maintain three data zones: repository for metadata/schemas/proposal/aggregate evidence; private working Drive for collaborative documents; restricted VDI for patient-level data, clinical derivatives, approved local tools, and audit logs.
- Decision: Keep the supplied MIMIC folder unchanged and viewer/source-only. The metadata audit records 25 CSVs and 39.65 GiB versus 26 official tables, with `NOTEEVENTS` and provenance unresolved; no patient rows were inspected.
- Decision: Keep five claim states (`Established`, `Preliminary`, `Planned`, `Blocked`, `Partner-dependent`) and preserve EXP-005 at 0/24 until independent real labels exist.
- Decision: Require Ali review of the exact private Drive, native literature Sheet, proposal, and pre-read before any external sharing. Literature searches and screening are not complete merely because the workbook exists.
- Decision: Treat September and October dates as working targets until written department or Graduate Studies confirmation arrives.

## 2026-07-30 - Iris Requirements Assurance and Presentation Controls

- Decision: Distinguish control coverage from accepted completion. The closure audit has 44/44 locators, while current readiness is 2 verified complete, 6 implemented awaiting human acceptance, 22 partial, 5 open, and 9 blocked.
- Decision: Synchronize the exact recommended umbrella RQ and SQ1-SQ3 wording across the master register, study contract, proposal, decision pack, and execution plan. This fixes internal drift but does not create supervisor approval.
- Decision: Use a separate `IRIS-EXP-01`–`IRIS-EXP-04` assurance register so presentation/process checks do not alter the canonical `EXP-000`–`EXP-040` scientific catalog or empirical evidence.
- Decision: Treat IRIS-EXP-01 traceability and IRIS-EXP-03 claim-boundary results as PASS; treat IRIS-EXP-02 as ready pending a human rehearsal and IRIS-EXP-04 as ready pending the first real weekly cycle.
- Decision: Replace the unsupported “completed four-hour MIMIC audit” statement with the evidenced formulation: bounded metadata/schema audit documented; no patient rows inspected; elapsed time not recorded.
- Decision: Do not reuse July 15/21 decks unchanged. A current August/candidacy presentation requires the 12-checkpoint outline, `[Sources]` notes, rendered QA, a dated rehearsal, and Ali’s exact-package review.
- Reason: Independent call, traceability, and presentation audits found inconsistent question wording, stale presentation material, absent current deck/rehearsal evidence, and an unsupported elapsed-time claim.
- Consequence: The supervisor package can now be checked deterministically without overstating completion. Supervisor decisions, live usability, literature execution, shared access, university rules, EXP-005, and medical gates remain human/external work.

## 2026-08-01 - Enhanced Iris Zoom-to-Submission Closure Controls

- Decision: Preserve the raw media, ASR, translation, and July 29 R/A/Q registers as immutable evidence/snapshots; use the 1,195-row ledger as a machine-only review interface until two independent bilingual reviews and adjudication are recorded.
- Decision: Keep the first 910 control-linked segments distinct from 285 conservative `Human-review-needed` placeholders. A preliminary disposition is not a reviewed translation, speaker attribution, substantive-clause disposition, or acceptance.
- Decision: Separate extraction, implementation, acceptance, and ongoing-control state in the master register. A drafted or built artifact cannot satisfy supervisor acceptance, and silence cannot close a control.
- Decision: Extend assurance through IRIS-EXP-10 and require three fail-closed modes: `structure` may pass on deterministic artifacts; `readiness` also requires current human rehearsal/delivery/access evidence; `closure` additionally requires adjudication, final dispositions, approvals, and submission evidence.
- Decision: Treat SCI-EXP-01–06 as proposal aliases crosswalked to the canonical EXP registry, not as independent result IDs. No new accuracy, generalization, effort, usability, medical, or transfer result is created.
- Decision: The August 5 supervisor presentation is a separate controlled artifact from the later candidacy presentation. The local PPTX/PDF, notes, appendix, workbook, visual QA, and backup establish construction only; human rehearsal, Ali release approval, sharing, access, meeting decisions, and acceptance remain open.
- Decision: Keep reviewer returns and adjudication separate from the byte-reproducible preliminary ledger. The merger may emit an authoritative adjudicated ledger only after both distinct reviewers supply all 1,195 segment rows plus full-media evidence and a third person resolves every disagreement.
- Decision: A submission filename or placeholder cannot satisfy closure. IRIS-EXP-10 requires one exact schema-valid `authorized-submission-receipt.json` whose verified route, zoned time, receipt ID, submitted-package hash, external-receipt hash, authorization evidence, and issued-certificate binding all validate.
- Reason: The enhanced plan requires media-to-control completeness, evidence-honest delivery assurance, and a signed route to submission without allowing automated structure checks to impersonate human or institutional evidence.
- Consequence: The program can report `structure` PASS while `readiness` and `closure` correctly return non-zero. A 100% certificate remains ineligible until every human, external, acceptance, approval, and receipt gate is evidenced.

## 2026-08-01 - Iris Next-Step Execution Interfaces and Release Integrity

- Decision: Operationalize the August 1-October 7 program as a canonical 29-work-package JSON board plus a human-readable ten-sheet workbook; the workbook is a companion view and does not replace the master traceability register or board.
- Decision: Keep Reviewer A/B inputs blind and separate, validate partial batches without treating them as reviewed truth, require one full-media row per reviewer, and require a distinct adjudicator for every disagreement.
- Decision: Treat the university inquiry, proposal v0.2, literature search register, release runbook, role assignments, rehearsals, sharing, access tests, supervisor outcomes, and submission records as prepared interfaces only until the named human or external evidence exists.
- Decision: Correct appendix-title and slide-11 footer defects in native PowerPoint, rerender the changed slides, and bind the final PPTX/PDF hashes before release review.
- Decision: Invalidate the earlier offline ZIP after any package correction. Readiness must parse the current backup status and compare each required ZIP member hash with the current PPTX, PDF, and review workbook; matching a stale ZIP filename or outer hash is insufficient.
- Reason: The user requested implementation of the full next-step plan while preserving an evidence-honest boundary between locally automatable work and human, supervisor, institutional, medical, and submission gates.
- Consequence: Local structure can be complete and testable now, while human rehearsal, delivery, transcript adjudication, decisions, labels, medical authorization, proposal approval, and submission remain visibly blocked.

## 2026-08-03 - Independent Audit Standard for the Iris Closure Package

- Decision: Before reporting any package as "high quality" or "100% correct," an independent audit must reproduce the claim from source — run the actual tests/validators, recompute hashes, and visually inspect rendered artifacts — rather than trust prior session narration. A 21-agent adversarial audit (0 findings refuted) is the standard applied here and should be repeated after any future large edit pass on this package.
- Decision: All 10 IRIS-EXP structure-mode checks must pass at all times going forward; a stale provenance hash, a missing detached manifest, or an uncommitted frozen-package path is treated as a structure-mode regression to fix immediately, not a readiness/closure-only concern.
- Reason: The 2026-08-03 audit found the prior "Structure passes" claim in this file was false against the live repository (9 of 31 provenance hashes stale, 2 test failures, IRIS-EXP-07/08 both FAIL), because a documentation edit pass changed frozen-package files without re-running the provenance/manifest builders afterward.
- Consequence: `bf45c98` (fix pass) + `0456cff` (provenance rebinding) + `e637f0d` (.gitignore) + `ef12f6f` (source-manifest refresh) restore all 10 structure checks to PASS. Readiness and closure remain correctly non-zero pending human evidence.

## 2026-08-04 - Fresh-Worktree Verification Before Trusting Local Checkouts

- Decision: Before pushing a branch and expecting CI to pass, verify CI-equivalent checks (full test suite, structure-mode validator, hardening manifest, diff hygiene) in a disposable `git worktree add --detach HEAD` at the exact commit being pushed, not only in the primary long-lived local checkout.
- Reason: Pushing `docs/iris-july29-phd-execution` triggered CI for the first time this branch had ever run (`supervisor-package.yml` had never executed against it before), and it failed repeatedly for reasons invisible locally: (1) gitignored PDF/workbook artifacts that only ever existed on this machine, crashing validators that assumed local presence; (2) a missing `.gitattributes` `eol=lf` rule for `.jsonl`, so Windows `core.autocrlf` silently corrupted the raw ASR transcript on any fresh checkout while the long-lived local copy (checked out before the rule existed, or written directly by a script) stayed correct; (3) 4 further tracked files (`pyproject.toml`, one `.mjs`, two `.ps1`) whose on-disk bytes in this specific checkout had drifted from the declared attribute policy and were never re-smudged, corrupting an aggregate content hash (the evaluation-phase hardening manifest) that a fresh checkout computed differently. None of these were visible running tests directly in the primary checkout; each was only caught by diffing a fresh worktree's files byte-for-byte against the primary checkout, or by running the actual GitHub Actions job.
- Consequence: 6 CI-blocking commits (`bf980ec` through `20b04fc`) fixed all of the above; CI went green on both the feature branch and the resulting `main` merge commit (`a78c1bf`). Adopt this verification step as standard practice before any push expected to pass CI, especially after a long-lived local checkout has accumulated manual edits, scratch scripts, or older `.gitattributes` history.

## 2026-08-12 - Second Supervisor Checkpoint: Literature-First Sequencing and Structural Correction

- Decision: Treat the August 12 call's closing instruction as binding over its opening one: this week is literature-review-only (Chapter 2); methodology (Chapter 4) work does not start until the following week, and only if literature is done well.
- Decision: Chapter 2 must be structured as a conventional literature-review chapter that builds the reader from the Introduction toward Chapter 3's gap, not as three subsections mirroring SQ1/SQ2/SQ3. The existing per-RQ tag column in the literature spreadsheet (`A08-03`) stays as an internal tracking tool only; it does not dictate the chapter's table of contents.
- Decision: This week's literature scope is deliberately narrow - work the one ACL-2026 Findings paper and its associated GitHub taxonomy corpus thoroughly (classify relevance against the RQs, log gaps), rather than chasing additional separate papers. Broader search is deferred to after the proposal stage. This was an explicit, stated disagreement Iris raised against Arnon's preference to center the review on HCI as a field.
- Decision: `D-RQ-01`/`D-RQ-02` (RQ wording sign-off), `E6`, `E8`, the Plan A/B boundary wording, and the evidence-boundary wording remain explicitly open - the August 12 call did not raise or resolve any of them, and reading the working RQ text aloud without objection is not treated as approval.
- Reason: Direct machine transcript of the 2026-08-12 Zoom call (Ali, Iris, Arnon; ASR in `artifacts/meetings/2026-08-12-iris-arnon/`, evidence matrix in `docs/research/meetings/2026-08-12-supervisor-meeting.md`, items `F1`-`F17`).
- Consequence: `docs/research/phd-proposal/literature-review-structure-and-queries-draft.md` was produced as the first draft satisfying Iris's live request to hand the RQs to an AI assistant for a subsection breakdown and per-subsection Google Scholar queries (`F5`), reconciled against her later structural correction (`F10`). The five frozen `QL-01`-`QL-05` queries in `literature-search-execution-register.md` were found to already answer most of that request and were left untouched; a sixth candidate query (`F9`, live-drafted on the call) is flagged `Needs transcript verification` pending Ali's confirmation before it can become `QL-06` or fold into `QL-01`.

## 2026-08-18 - Chapter 4 (Research Methodology) Drafted With Recommended-Not-Decided Artifacts

- Decision: Write Chapter 4 now, in parallel with a separate literature-review verification track (run outside this session), per Ali's explicit instruction to execute the 2026-08-12 call's non-literature requirements and skip literature-review work.
- Decision: Recommend one concrete artifact per sub-question — an attention-budget cost/coverage model (SQ1), a normative judgment-record contract plus conformance suite (SQ2), and a transfer-eligibility decision procedure plus context descriptor (C2, SQ3) — chosen from the option sets already analyzed in `sections-2-and-4-thinking-notes.md`, each because it is buildable without waiting on EXP-005 (0/24) or medical gates (0/6). Each recommendation is explicitly marked as a recommendation, not a supervisor-confirmed decision.
- Decision: Cite only the chapter's own methodological framework (Peffers et al. 2007 DSRM; Wieringa 2014), both already `VERIFIED_ONLINE` in `literature/verified-research-corpus-2026-08-12.json`, and cite no substantive related-work literature — that stays out of scope for this chapter, consistent with skipping the literature-review track.
- Reason: `sections-2-and-4-thinking-notes.md` Part 3 lists 14 open questions that block a fully-decided Chapter 4, and the 2026-08-12 call did not resolve them (it reaffirmed the three-study structure at a high level only). Writing a chapter with no artifact choice would not be reviewable; writing one that silently picks an artifact without flagging it as provisional would repeat the exact solution-first framing Arnon's `E4` criticism targeted on 2026-08-05.
- Consequence: `docs/research/phd-proposal/chapter-4-research-methodology.md` (new) states the three recommended artifacts and their validation models, and carries forward eight specific open items in its own §4.7 (artifact/abstraction confirmation, the SQ2/SQ3 boundary, instrument-reliability admissibility, offline-replay wording, EXP-009/010 gating, Plan A placement, two unnamed resourcing gaps — an independent implementer for Study 2 and two raters for Study 3). None of it should be read as supervisor-approved.

## 2026-09-03 - Supervisor-facing Q&A task plan

- Decision: Current execution is limited to complete Q&A observability, deterministic candidate-alert extraction, and automated descriptive analysis. No manual labeling or row-by-row review is requested from Iris or Arnon.
- Decision: Replace any definitive `UNANSWERED` interpretation with `ANSWER_NOT_PERSISTED` / “לא נשמרה תשובה תואמת בנתונים הקיימים” unless direct runtime evidence proves non-response.
- Decision: Reviewer sheets remain prepared for a future validation stage and are not sent or used in the current execution plan. True/false alert quality, precision, recall, accuracy, and intervention necessity remain unmeasurable without independent labels.
- Reason: The frozen snapshot has 12 questions and no persisted matching answers, confidence, evidence, or reconstructable episode metadata; the supervisor constraint explicitly rules out manual labeling now.

## 2026-09-03 - Interaction-log-first supervisor plan revision

- Decision: Recover the original `interaction_log.jsonl` before changing instrumentation or spending API budget. The log can recover only model calls that actually occurred; it cannot supply advisor answers that were never generated.
- Decision: The first new runtime should be one controlled setting selected after input-availability checks. Expansion to four settings is conditional on complete answered-Q&A episodes and recorded runtime/cost evidence.
- Decision: Remove commit SHA/base-revision details from the supervisor-facing DOCX/PDF; retain repository provenance in Git and internal Markdown/audit records.
- Decision: Iris/Arnon are not asked to approve detector rules or descriptive sufficiency now. Their only possible actions are providing the original log or approving one controlled run/API cost if recovery fails.

## 2026-09-04 - Canonical Q&A task-plan source and verification hardening

- Decision: Keep the approved supervisor-facing Hebrew Markdown byte-equivalent while moving task, summary, metadata, and effort content into `scripts/data/qa_task_plan.json`; Markdown, DOCX, and PDF builders consume that source through one loader.
- Decision: Add deterministic RTL/control-character normalization and a non-aborting multi-pattern send-gate scanner, plus a semantic interaction-log guard that distinguishes `metadata_only` from full-content logging and forbids reconstructing answers that were never generated.
- Reason: Engineering consistency and privacy verification require one source of truth and complete diagnostics without changing Iris-facing scientific wording or executing the study.
- Consequence: Generated local derivatives are ready for human review; DOCX rendering remains structurally checked because the environment lacks `pdf2image`/LibreOffice.

## 2026-09-04 - Task 1 interaction-log recovery

- Decision: Classify the accessible local search as `NOT FOUND — LOCAL SEARCH EXHAUSTED`; do not instrument, rerun VEGO-AI, call an API, or alter the approved supervisor PDF/DOCX.
- Decision: Treat the archived evaluator configuration/log initialization and archived client implementation as evidence for conditional historical `full_content` logging, but never treat that capability as recovered interaction records.
- Reason: No `interaction_log.jsonl` bytes or credible variant were found in the repository, supplied archives, Downloads, Claude workspace, OneDrive Documents, mounted VEGO-AI Drive folder, or Codex attachments. The historical G-drive shortcut target remains inaccessible locally.
- Consequence: The frozen 12 canonical questions / 30 snapshot records baseline remains unchanged; contacting Iris/Arnon is a separate human decision only if the inaccessible original source is still needed.

## 2026-09-04 - Tasks 2–5 Q&A communication observer

- Decision: Add a dedicated `qa-communication-event-v1` contract and privacy-safe append-only observer with deterministic episode projection; preserve the historical `qa-escalation-event-v1` semantics.
- Decision: Do not alter protected `VEGO-AI/framework/orchestrator.py`, `qa_registry.py`, or `state.py` when the runtime hash guard rejects direct edits. Treat runner wiring as a separate reviewed change.
- Decision: Retire F5 as a human-escalation trigger for the frozen corpus; expose `ANSWER_NOT_PERSISTED` only as a data-availability status.
- Reason: Offline parity, schema, ordering, duplicate-ID, follow-up, termination, privacy, and route-representation checks pass. A direct production edit would weaken the protected-runtime evidence boundary.
- Consequence: The technical verification is `PARTIAL`; no one-setting run can proceed until case-model inputs and a reviewed runtime integration are available.

## 2026-09-06 - Study 2A ON/OFF preparation and Study 2B Llama feasibility

- Decision: Register a separately preregistered descriptive comparison using `VEGO-AI_ON` (full current orchestration) and `VEGO-AI_OFF` (new single-model, no-delegation/no-Q&A/no-feedback/no-Detector baseline) on the same frozen AirTravel corpus and N=4 cases. The OFF condition is not historical evidence and is never pooled with Study 1 or the ON condition.
- Decision: Freeze identical provider/model/corpus/objective/token/cost/timeout/retry/concurrency/schema/validation/privacy/retention controls while keeping condition identifiers, roots, event logs, denominators, and claim boundaries separate. Preparation remains disabled by default and supports only deterministic in-memory engineering fixtures.
- Decision: Record `meta-llama/Llama-3.2-3B-Instruct` as a separate feasibility candidate only; do not download, run, or combine it with Study 2A. License, hardware, cost, structured-output, and tool-support checks remain pending.
- Reason: The requested study tests observable orchestration and communication behavior, not accuracy, human benefit, or policy superiority. A meaningful no-VEGO comparator must be explicit and independently reproducible before any later provider-backed run.
- Consequence: PR #40 is preparation-only and remains open/draft/unmerged pending independent review and fresh run authorization; no provider/API call or scientific result exists.

