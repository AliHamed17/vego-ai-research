# ACL-2026 Taxonomy v16 — Strict Review and Merge Gate

**Artifact set:** `acl-2026-taxonomy-*v16`, `vego-ai-acl-taxonomy-map-v16.*`  
**Branch:** `docs/acl-taxonomy-v16-strict`  
**Review posture:** adversarial, evidence-bounded, no silent closure  
**Current verdict:** **NOT MERGE READY**

This gate reviews the v16 ACL-taxonomy deliverable as a derived literature-classification artifact. It does **not** certify the literature review as complete, validate the research questions, close citation-lineage disputes, establish empirical benefit, or authorize a medical claim.

## 1. What v16 is allowed to claim

The v16 artifact may claim only that:

1. it provides an **Ali-owned, RQ-led relevance classification** derived from the ACL-2026 human-agent taxonomy rather than copying the source figure;
2. it states both relevant source denominators: **five paper-level aspects** and **four companion-repository taxonomy branches**;
3. it uses Iris's required four labels exactly:
   - `HIGHLY RELEVANT`;
   - `LESS RELEVANT`;
   - `NOT RELEVANT AT ALL`;
   - `MISSING FROM ACL TAXONOMY`;
4. `NOT RELEVANT AT ALL` is scoped to the current VEGO-AI thesis problem, not a claim that the ACL branch has no scientific value;
5. `MISSING FROM ACL TAXONOMY` means **not represented as a first-class source-taxonomy branch**; it does not mean that no related idea appears anywhere in the paper or corpus;
6. the map aligns each SQ with the current **one-primary-artifact-per-study** methodology contract:
   - SQ1 — attention-budget cost/coverage model;
   - SQ2 — normative judgment-record contract plus conformance suite;
   - SQ3 — transfer-eligibility decision procedure plus target-context descriptor;
7. all RQ wording and artifact granularity remain provisional until a dated supervisor decision exists.

## 2. What v16 must not claim

The artifact must not be used to claim that:

- the ACL corpus has been exhaustively screened;
- QL-01–QL-05 have been executed;
- the 40–60 full-text target has been reached;
- the six VEGO-AI-derived dimensions are novel;
- no prior work integrates the relevant mechanisms;
- the RQs or artifact boundaries are supervisor-approved;
- EXP-005 has labels or establishes an accuracy/generalization gain;
- healthcare transfer is authorized, safe, validated, or ready;
- the taxonomy figure itself is evidence that the proposed architecture works.

## 3. Strict static-review findings

| Check | Verdict | Strict interpretation |
|---|---|---|
| Source versus Ali-derived material is separated | **PASS at artifact level** | Source branches and VEGO-AI-derived gap dimensions must remain visually and textually distinct. |
| Source denominators are disclosed | **PASS at artifact level** | The reader can distinguish the paper's five aspects from the companion repository's four navigation branches. |
| Exact four-label scale is present | **PASS at artifact level** | Labels must not be replaced by `RELEVANT`, `BACKGROUND`, or other non-requested substitutes. |
| `NOT RELEVANT AT ALL` is scope-bounded | **PASS at artifact level** | The label applies only to the current thesis problem and cannot become a general assessment of the source branch. |
| Missing dimensions are framed conservatively | **PASS at artifact level** | Absence is asserted only at first-class taxonomy-branch level. |
| Chapter 4 artifact alignment is explicit | **PASS at artifact level** | This resolves a presentation inconsistency only; supervisor approval remains open. |
| Formal-search completeness | **BLOCKED** | QL-01–QL-05 remain `0/5`; the map is not proof of exhaustive coverage. |
| Full ACL-corpus disposition | **BLOCKED** | The bounded source corpus still lacks complete human-reviewed disposition. |
| Full-text evidence target | **BLOCKED** | The declared 40–60 complete extractions and second review remain open. |
| Human scholarly review | **BLOCKED** | Classification and source interpretation require a named reviewer, dated decision, and resolved comments. |
| RQ/construct approval | **BLOCKED** | RQ wording, human versus expert, and the SQ2/SQ3 boundary remain provisional. |
| Citation/anchor lineage | **BLOCKED** | Raykar versus Aamodt & Plaza and Dellermann versus Dhanorkar require an explicit decision record. Fervers (2006) is not to be re-flagged as a year defect without new primary-source evidence. |
| Mermaid/local render verification | **NOT RUN in connector-only pass** | A committed source file is not equivalent to a successful local render and visual inspection. |
| Repository health/next-step workflow | **NOT RUN in connector-only pass** | Required PowerShell tracking, project-review, visualization, wiki, and dashboard-health commands must run in the repository environment. |
| Empirical validation | **BLOCKED** | EXP-005 remains `0/24`; taxonomy quality cannot substitute for empirical evidence. |
| Medical readiness | **BLOCKED** | Medical entry gates remain `0/6`. |

## 4. Adversarial reviewer challenges

### HCI / human-agent reviewer

- Does the map classify human involvement rather than merely relabeling the RQs?
- Are feedback timing, granularity, collaboration, orchestration, and communication preserved where they materially affect the thesis?
- Is `co-reasoning` treated as a proposed construct unless the literature establishes a stable definition?

### Machine-learning reviewer

- Is selective intervention distinguished from active learning, selective prediction, abstention, and learning to defer?
- Does uncertainty remain one signal rather than a proxy for consequence or authority?

### Knowledge-representation / CBR reviewer

- Is the SQ2/SQ3 distinction defensible against the CBR cycle `retrieve → reuse → revise → retain`?
- Does the proposed judgment record add more than a case representation with provenance and policy metadata?

### Governance reviewer

- Is the statement `retrieval is not permission` expressed precisely as: similarity-based retrieval alone does not establish applicability, authorization, current validity, or target benefit?
- Are competence, authority, permission, and correctness kept separate?

### MDE reviewer

- Is variability exploration linked to model-assessment and guideline-operationalization literature rather than presented as an isolated agentic-AI problem?
- Is validity kept separate from recurrence/frequency?

### Methodology reviewer

- Can every displayed classification be traced to a source row, locator, interpretation, and claim boundary?
- Could a different reviewer reproduce the label from the stated rule?
- Is contradictory or nearest-prior work recorded rather than filtered out?

## 5. Required local verification before merge

Run from a fresh checkout of the PR head and record exact commands, revision, timestamp, and outputs:

1. `./scripts/refresh-tracking.ps1 -Pull`
2. `./scripts/run-project-review.ps1`
3. `./scripts/run-codex-next-step.ps1 -RefreshWiki -RunHealth -NoOpen`
4. render `docs/visualizations/vego-ai-acl-taxonomy-map-v16.mmd` through the repository visualization workflow;
5. inspect the rendered SVG/PNG at full size and reduced thesis-page size;
6. verify XML/SVG parsing, viewBox, embedded text, connector integrity, clipping, and absence of external font/image dependencies;
7. run the repository's evidence-consistency and research-health checks;
8. run `./scripts/refresh-tracking.ps1 -Viz`;
9. rebuild the Confluence outbox and run dashboard health;
10. confirm the branch is based on the latest `main`, CI is green, and the worktree is clean.

A screenshot or a manually opened source file is insufficient evidence for these checks.

## 6. Required scholarly decision record

Before changing the PR from draft to ready-for-review, record a dated human decision for each item:

| Decision | Allowed outcomes |
|---|---|
| Four-label classification accepted? | accept / revise labels / revise scope note |
| Five-aspect and four-branch denominators correct? | accept / correct source denominator |
| Six VEGO-AI-derived dimensions complete enough for this slide? | accept as selective / add / remove / regroup |
| SQ1 primary artifact | accept / revise |
| SQ2 primary artifact | accept / revise |
| SQ3 primary artifact | accept / revise |
| Raykar versus Aamodt & Plaza | retain Raykar / replace with Aamodt & Plaza / retain both with different roles |
| Dellermann versus Dhanorkar | retain Dellermann / replace with Dhanorkar / retain both with different roles |
| Chapter-2 placement | include as derived classification / appendix only / exclude |

Blank, silent, or inferred decisions remain **deferred**, not approved.

## 7. Merge acceptance checklist

- [ ] Latest `main` merged or rebased into the branch with no unresolved conflict
- [ ] PR changed-file list contains only intended documentation/visualization/control artifacts
- [ ] Exact four-label scale verified in Markdown, CSV, Mermaid, and SVG
- [ ] Five paper aspects and four repository branches verified against primary source artifacts
- [ ] All Ali-derived dimensions marked as derived synthesis, not source taxonomy
- [ ] Chapter 4 one-primary-artifact-per-study alignment verified
- [ ] Citation/anchor lineage decision record added
- [ ] Local Mermaid render completed and visually inspected
- [ ] Evidence-consistency, research-health, project-review, and dashboard-health checks pass
- [ ] Agent memory, progress tracker, visualization catalog, and wiki outbox refreshed
- [ ] Human scholarly review completed with owner, date, evidence, and resolved comments
- [ ] CI green on the final PR head
- [ ] PR remains free of runtime VEGO-AI behavior changes
- [ ] PR body reports all open scientific and human gates without composite-score masking

## 8. Current disposition

**Keep PR #23 in draft.** The artifact-level classification improvements are useful, but merge would be premature until local repository verification and human scholarly review are recorded. No formatting, diagram quality, or technical QA result can close the formal-search, citation-lineage, EXP-005, medical, or supervisor-decision gates.
