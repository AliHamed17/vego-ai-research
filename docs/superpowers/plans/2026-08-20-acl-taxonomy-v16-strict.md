# ACL-2026 Taxonomy → VEGO-AI Relevance Map v16 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Publish a source-traceable, thesis-ready ACL-2026 taxonomy relevance map that separates source taxonomy from VEGO-AI-derived gaps and aligns each subquestion with the current one-artifact-per-study methodology.

**Architecture:** One human-readable evidence map and one CSV matrix are the semantic source; Mermaid is the editable diagram source; SVG is the standalone thesis/deck figure. The proposal README exposes the current artifact and a strict audit records what was and was not verified. All changes are documentation-only on `docs/acl-taxonomy-v16-strict`.

**Tech Stack:** Markdown, CSV, Mermaid, SVG, CairoSVG/XML static verification, GitHub Contents API.

**Spec:** `docs/superpowers/specs/2026-08-20-acl-taxonomy-v16-strict-design.md`

## Global Constraints

- Do not modify VEGO-AI runtime, schemas, tests, classifiers, prompts, or evaluation outputs.
- Do not claim QL search execution, systematic-review completion, supervisor approval, empirical benefit, safe transfer, or medical readiness.
- Use exactly: `HIGHLY RELEVANT`, `LESS RELEVANT`, `NOT RELEVANT AT ALL`, `MISSING FROM ACL TAXONOMY`.
- Preserve five paper-level core aspects and four companion-repository taxonomy navigation branches as separate denominators.
- Use the current Chapter 4 artifacts, not the bundled C1–C7 architecture.
- Treat Fervers et al. (2006) as valid and distinct; do not reintroduce the corrected false-positive regression claim.
- Do not silently settle the Raykar/Aamodt & Plaza or Dellermann/Dhanorkar anchor-lineage decisions.

---

### Task 1: Create the controlled evidence map — COMPLETE

**Files:**
- Create: `docs/research/phd-proposal/acl-2026-taxonomy-vego-ai-relevance-map-v16.md`
- Create: `docs/research/phd-proposal/acl-2026-taxonomy-evidence-matrix-v16.csv`

**Interfaces:**
- Consumes: Zou et al. five paper-level components; repository four-branch denominator; provisional RQs; Chapter 4 artifact recommendations.
- Produces: canonical branch IDs, provenance classes, relevance labels, RQ mappings, and evidence boundaries consumed by both visual files.

- [x] **Step 1: Write the evidence-map Markdown**

The map states the source denominator, classification decisions, nearest VEGO-AI literature streams, one-artifact-per-study mapping, limitations, open gates, and release checklist.

- [x] **Step 2: Write the machine-readable CSV**

Exact columns:

```text
branch_id,parent_id,provenance,source_dimension,source_category,relevance,rq_mapping,study_artifact,vego_ai_interpretation,evidence_basis,claim_boundary
```

- [x] **Step 3: Verify classification completeness**

Actual matrix checks:

```text
paper_core_aspects = 5
repository_taxonomy_branches = 4
exact_scale_labels = 4
acl_source_rows = 34
vego_ai_missing_rows = 6
total_matrix_rows = 40
```

The initial plan estimate of nine source rows was superseded by the deliberate fine-grained extraction of all represented source categories/subcategories; the denominator definitions remain unchanged.

- [x] **Step 4: Commit evidence artifacts**

Completed through GitHub connector commits on the dedicated branch.

---

### Task 2: Build the editable thesis taxonomy figure — COMPLETE, LOCAL MERMAID RENDER PENDING

**File:** `docs/visualizations/vego-ai-acl-taxonomy-map-v16.mmd`

- [x] **Step 1: Define the conceptual root**

```text
Governed Human Judgment in Agentic-AI Variability Exploration (VEGO-AI)
```

- [x] **Step 2: Add all five paper-level source aspects**

Environment & Profiling, Human Feedback, Interaction Type, Orchestration Paradigm, and Communication are represented.

- [x] **Step 3: Apply exact relevance labels**

Competition and coopetition are `NOT RELEVANT AT ALL`; orchestration and communication are `LESS RELEVANT`; Environment & Profiling, Human Feedback, and Collaboration are `HIGHLY RELEVANT`.

- [x] **Step 4: Add six VEGO-AI-derived dimensions**

Every derived branch displays `MISSING FROM ACL TAXONOMY`, its RQ relationship, evidence boundary, and current study artifact where applicable.

- [x] **Step 5: Add gate and authorship notes**

```text
QL-01–QL-05: 0/5 | ACL full disposition: incomplete | EXP-005: 0/24 | Medical: 0/6
```

```text
Author-generated synthesis; not exhaustive; provisional RQs; no empirical contribution claim.
```

- [ ] **Step 6: Run the repository visualization-agent/Mermaid renderer**

Not executable through the GitHub connector-only environment. Required before merge in a normal worktree.

---

### Task 3: Build and statically verify the standalone SVG — COMPLETE

**File:** `docs/visualizations/vego-ai-acl-taxonomy-map-v16.svg`

- [x] **Step 1: Create the portrait vector canvas**

The figure uses a white background, serif text, orthogonal connectors, rounded pastel boxes, source/derived provenance sections, and a four-column hierarchy modeled on the reference visual grammar without copying the original artwork.

- [x] **Step 2: Render ACL source sections**

Each major source section is marked `ACL SOURCE` and color-coded.

- [x] **Step 3: Render VEGO-AI extension section**

The lower section is marked `ALI-DERIVED` and uses a separate teal palette.

- [x] **Step 4: Add legend and gate note**

The legend explains all four relevance labels, both source denominators, the current study artifacts, and the unchanged gates.

- [x] **Step 5: Perform static SVG verification**

Verified in the execution container:

```text
XML declaration present
one root <svg>
XML parsed successfully
viewBox = 0 0 2400 4124
no external image/font dependency
all four relevance labels present
all three current study artifact names present
open-gate statement present
```

- [x] **Step 6: Render and inspect a PNG preview**

CairoSVG produced a 2400 × 4124 PNG. The hierarchy, connectors, colors, badges, legend, and source/derived separation were visually inspected; no blank render or missing major branch was observed.

---

### Task 4: Wire navigation and record the strict audit — COMPLETE

**Files:**
- Modify: `docs/research/phd-proposal/README.md`
- Create: `docs/research/phd-proposal/acl-taxonomy-v16-strict-audit.md`

- [x] **Step 1: Add current taxonomy navigation**

The proposal README links the evidence map, Mermaid, and SVG and identifies the artifact as controlled, derived, provisional, and non-exhaustive.

- [x] **Step 2: Align README study artifacts with Chapter 4**

The table now uses:

- SQ1: attention-budget cost/coverage model;
- SQ2: normative judgment-record contract + executable conformance suite;
- SQ3: transfer-eligibility decision procedure + target-context descriptor.

All remain explicitly pending supervisor decision.

- [x] **Step 3: Write the audit note**

The audit records the denominator, exact scale, source/derived split, artifact reconciliation, Fervers correction, unresolved anchor lineage, static render checks, connector limitations, and unchanged gates.

---

### Task 5: Sync, verify, and open a draft PR — IN PROGRESS

- [x] **Step 1: Compare branch against main**

The first comparison found eight intended changed paths and no runtime files. It also found the branch two commits behind current `main`; synchronization is required before PR review.

- [ ] **Step 2: Synchronize current main without dropping either side**

Create a merge commit using current main as the base tree, overlay the eight intended branch paths, and retain both the branch head and current main as parents.

- [ ] **Step 3: Re-run changed-path and claim-language inspection**

Expected changed paths remain limited to:

```text
docs/research/phd-proposal/README.md
docs/research/phd-proposal/acl-2026-taxonomy-evidence-matrix-v16.csv
docs/research/phd-proposal/acl-2026-taxonomy-vego-ai-relevance-map-v16.md
docs/research/phd-proposal/acl-taxonomy-v16-strict-audit.md
docs/superpowers/plans/2026-08-20-acl-taxonomy-v16-strict.md
docs/superpowers/specs/2026-08-20-acl-taxonomy-v16-strict-design.md
docs/visualizations/vego-ai-acl-taxonomy-map-v16.mmd
docs/visualizations/vego-ai-acl-taxonomy-map-v16.svg
```

Inspect unsupported uses of:

```text
validated
safe transfer
systematic review complete
approved RQ
empirically improves
medical readiness
```

Every occurrence must be negated, bounded, or removed.

- [ ] **Step 4: Open a draft PR**

The PR body must state:

- documentation/visualization only;
- no runtime changes;
- no evidence-gate changes;
- source-derived versus Ali-derived content;
- local scripts that were not executable;
- exact reviewer questions.

- [ ] **Step 5: Inspect PR changed-file list and CI/check status**

Unexpected paths must block review. If no workflow is triggered or checks are unavailable, record `not run / unavailable`, never `passed`.
