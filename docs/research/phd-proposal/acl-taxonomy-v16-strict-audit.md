# ACL Taxonomy v16 — Strict Enhancement Audit

**Date:** 2026-08-20  
**Branch:** `docs/acl-taxonomy-v16-strict`  
**Change class:** documentation + literature classification + visualization only  
**Runtime impact:** none

## 1. Verdict

The v16 tranche closes the two narrowly defined ACL-classification defects identified in the current v15 verification report:

1. the source denominator is now explicit and traceable;
2. the relevance classification now uses Iris's exact four labels and distinguishes source-taxonomy branches from Ali's VEGO-AI additions.

It does **not** close the formal literature-search, corpus-screening, human-review, RQ-approval, EXP-005, or medical-readiness gates.

## 2. Artifacts created or changed

| Path | Role |
| --- | --- |
| `docs/superpowers/specs/2026-08-20-acl-taxonomy-v16-strict-design.md` | Approved design and claim boundary |
| `docs/superpowers/plans/2026-08-20-acl-taxonomy-v16-strict.md` | Implementation/verification plan |
| `docs/research/phd-proposal/acl-2026-taxonomy-vego-ai-relevance-map-v16.md` | Human-readable evidence and classification map |
| `docs/research/phd-proposal/acl-2026-taxonomy-evidence-matrix-v16.csv` | Machine-readable branch/provenance/relevance/RQ matrix |
| `docs/visualizations/vego-ai-acl-taxonomy-map-v16.mmd` | Editable Mermaid source |
| `docs/visualizations/vego-ai-acl-taxonomy-map-v16.svg` | Standalone thesis/deck-ready vector figure |
| `docs/research/phd-proposal/README.md` | Current navigation and Chapter 4 artifact alignment |
| `docs/research/phd-proposal/acl-taxonomy-v16-strict-audit.md` | This audit |

## 3. Source-denominator verification

### Paper-level structure

Zou et al. (2026) define **five core aspects**:

1. Environment & Profiling
2. Human Feedback
3. Interaction Type
4. Orchestration Paradigm
5. Communication

### Companion-repository structure

The survey companion repository exposes **four taxonomy navigation branches**:

1. Human Feedback
2. Interaction
3. Orchestration
4. Communication

`Environment & Profiling` is therefore retained as a paper-level core aspect and marked `ACL-PAPER`; it is not falsely described as a fifth repository navigation branch.

### Prior v15 seven-row issue

The prior `ACL Branch Map v15` contained seven rows without adequately distinguishing source categories from Ali's synthesis. The v16 map uses provenance labels:

- `ACL-PAPER`
- `ACL-REPO`
- `VEGO-AI-DERIVED`
- `METHOD`

The six VEGO-AI extensions are now explicitly marked `MISSING FROM ACL TAXONOMY` rather than presented as source branches.

## 4. Relevance-scale verification

The following exact labels appear in the Markdown, CSV, Mermaid, and SVG artifacts:

- `HIGHLY RELEVANT`
- `LESS RELEVANT`
- `NOT RELEVANT AT ALL`
- `MISSING FROM ACL TAXONOMY`

`NOT RELEVANT AT ALL` is applied to the source Interaction subbranches `Competition` and `Coopetition`, because the current RQs do not define an opposing-goal or mixed cooperative/competitive human-agent relationship.

The classification is scope-specific. It does not claim those branches are unimportant in human-agent research generally.

## 5. VEGO-AI-derived dimensions

Six problem-led additions are separated from the ACL source taxonomy:

1. selective intervention under bounded expert attention;
2. reasoning-rich judgment representation;
3. claim-specific governance and contestability;
4. scope-aware reuse;
5. transfer eligibility and leakage-safe evaluation;
6. variability exploration and guideline operationalization.

The word `missing` is controlled: it means **not a first-class branch in the ACL taxonomy used here**. It does not assert that Zou et al. never mention any related issue in prose.

## 6. Chapter 4 reconciliation

The v16 artifacts no longer present the bundled C1–C7 architecture as the artifact per RQ. They use the current Chapter 4 recommendations:

| RQ | Current recommended artifact |
| --- | --- |
| SQ1 | attention-budget cost/coverage model |
| SQ2 | normative judgment-record contract + executable conformance suite |
| SQ3 | transfer-eligibility decision procedure + target-context descriptor |

These remain recommendations pending supervisor decision. The documentation does not describe them as approved contributions or demonstrated capabilities.

## 7. Citation/anchor-lineage controls

### Fervers correction retained

Fervers et al. (2006), *Adaptation of clinical guidelines: Literature review and proposition for a framework and procedure*, is retained as a valid, distinct source. It is not treated as a wrong-year regression and is not conflated with the separate Fervers/ADAPTE Collaboration publication.

### Raykar vs. Aamodt & Plaza

The v16 map does not silently select one as a replacement for the other:

- Raykar et al. support annotator reliability and disagreement modeling;
- Aamodt & Plaza represent the Case-Based Reasoning predecessor family.

Whether either belongs in the five-source SQ2 anchor set remains a separate scholarly/lineage decision.

### Dellermann vs. Dhanorkar

The v16 map does not silently resolve the U-RQ anchor-lineage issue:

- Dellermann et al. support hybrid-intelligence/complementarity framing;
- Dhanorkar et al. provide recent empirical boundary evidence on oversight work for software agents.

Core-anchor selection remains subject to explicit decision and human scholarly review.

## 8. Static visualization verification performed

The standalone SVG was generated deterministically and checked in this execution environment.

### XML/static checks

- XML parsed successfully.
- Exactly one root `<svg>` element exists.
- `viewBox="0 0 2400 4124"` is present.
- No external image or font file dependency is used.
- All four relevance labels are present.
- All three current study-artifact names are present.
- The open-gate statement is present.

### Render check

- The SVG was rendered to a `2400 × 4124` PNG using CairoSVG.
- The PNG preview was visually inspected for hierarchy, connectors, branch coloring, relevance badges, legend, and source/derived separation.
- No blank render or missing major branch was observed.

### Mermaid check boundary

The `.mmd` source was inspected for unique node IDs, balanced source/derived branches, styles, and explicit gate text. The repository's visualization-agent/Mermaid render command was **not** executed through the GitHub connector environment; no Mermaid-render pass is claimed.

## 9. Repository-workflow boundary

This enhancement was performed through GitHub connector writes on a dedicated branch. The local repository commands required by `AGENTS.md` could not be executed in this connector-only environment, including:

- `scripts/refresh-tracking.ps1 -Pull`
- `scripts/run-codex-next-step.ps1`
- `scripts/refresh-tracking.ps1 -Viz`
- `scripts/build-confluence-wiki.ps1`
- `scripts/dashboard-health.ps1 -RequireOutbox`

Therefore:

- no local PowerShell health result is claimed;
- no generated catalog/dashboard/wiki refresh is claimed;
- no Confluence sync is claimed;
- the draft PR must request that these commands be run in a normal repository worktree before merge.

## 10. Evidence gates — unchanged

| Gate | State after this change |
| --- | --- |
| Formal QL-01–QL-05 searches | 0/5 |
| Complete pinned ACL disposition | incomplete |
| 40–60 full-text extraction target | open |
| Human scholarly inclusion/second review | pending |
| RQ and construct approval | pending |
| EXP-005 generalization-safe labels | 0/24 |
| Medical entry gates | 0/6 |

The visual and its polish cannot bypass any gate.

## 11. Strict reviewer questions before merge

1. Does Iris agree with the branch-level use of `NOT RELEVANT AT ALL` for Competition and Coopetition in this thesis scope?
2. Are the six `VEGO-AI-DERIVED` dimensions the correct problem-led additions, or should any be merged/split?
3. Is the SQ2→SQ3 boundary for scope-aware reuse acceptable?
4. Should Environment & Profiling appear as its own major figure section even though the companion repository does not expose it as a top-level taxonomy branch?
5. Are the Chapter 4 artifact recommendations ready to appear in the literature classification, with their pending-decision status visible?
6. Which sources should occupy the five-source core-anchor slots after the parallel workbook lineages are reconciled?

## 12. Merge recommendation

**Draft PR only.** The source/derived separation and SVG are suitable for review, but merge should wait for:

- Mermaid/local visualization-agent render verification;
- repository health/tracking refresh;
- review of the six derived dimensions and exact relevance assignments;
- confirmation that no concurrent literature-package branch supersedes the same paths.
