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
