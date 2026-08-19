# ACL-2026 Taxonomy → VEGO-AI Relevance Map v16 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Publish a source-traceable, thesis-ready ACL-2026 taxonomy relevance map that separates source taxonomy from VEGO-AI-derived gaps and aligns each subquestion with the current one-artifact-per-study methodology.

**Architecture:** The enhancement uses one authoritative evidence note and CSV matrix as the semantic source, one editable Mermaid figure as the primary diagram source, and one standalone SVG for thesis/deck insertion. A README entry and audit note expose the artifact and its evidence boundary. All changes are documentation-only on a dedicated branch.

**Tech Stack:** Markdown, CSV, Mermaid, SVG, GitHub Contents API.

**Spec:** `docs/superpowers/specs/2026-08-20-acl-taxonomy-v16-strict-design.md`

## Global Constraints

- Do not modify VEGO-AI runtime, schemas, tests, classifiers, prompts, or evaluation outputs.
- Do not claim QL search execution, systematic-review completion, supervisor approval, empirical benefit, safe transfer, or medical readiness.
- Use exactly: `HIGHLY RELEVANT`, `LESS RELEVANT`, `NOT RELEVANT AT ALL`, `MISSING FROM ACL TAXONOMY`.
- Preserve five paper-level core aspects and four companion-repository taxonomy navigation branches as separate denominators.
- Use the current Chapter 4 artifacts, not the bundled C1–C7 architecture.
- Treat Fervers et al. (2006) as valid and distinct; do not reintroduce the corrected false-positive regression claim.

---

### Task 1: Create the controlled evidence map

**Files:**
- Create: `docs/research/phd-proposal/acl-2026-taxonomy-vego-ai-relevance-map-v16.md`
- Create: `docs/research/phd-proposal/acl-2026-taxonomy-evidence-matrix-v16.csv`

**Interfaces:**
- Consumes: Zou et al. five paper-level components; repository four-branch denominator; provisional RQs; Chapter 4 artifact recommendations.
- Produces: canonical branch IDs, provenance classes, relevance labels, RQ mappings, and evidence boundaries consumed by both visual files.

- [ ] **Step 1: Write the evidence-map Markdown**

Include exact source denominator, classification decisions, nearest VEGO-AI literature streams, one-artifact-per-study mapping, limitations, open gates, and a release checklist.

- [ ] **Step 2: Write the machine-readable CSV**

Use these exact columns:

```text
branch_id,parent_id,provenance,source_dimension,source_category,relevance,rq_mapping,study_artifact,vego_ai_interpretation,evidence_basis,claim_boundary
```

- [ ] **Step 3: Verify classification completeness manually**

Expected checks:

```text
paper_core_aspects = 5
repository_taxonomy_branches = 4
exact_scale_labels = 4
source_rows_with_relevance = 9
vego_ai_missing_rows = 6
```

- [ ] **Step 4: Commit**

```bash
git add docs/research/phd-proposal/acl-2026-taxonomy-vego-ai-relevance-map-v16.md \
        docs/research/phd-proposal/acl-2026-taxonomy-evidence-matrix-v16.csv
git commit -m "docs: add source-traceable ACL taxonomy relevance map"
```

---

### Task 2: Build the editable thesis taxonomy figure

**Files:**
- Create: `docs/visualizations/vego-ai-acl-taxonomy-map-v16.mmd`

**Interfaces:**
- Consumes: branch IDs and labels from Task 1.
- Produces: editable Mermaid source with a left-to-right taxonomy tree.

- [ ] **Step 1: Define the left vertical conceptual root**

Use the root label:

```text
Governed Human Judgment in Agentic-AI Variability Exploration (VEGO-AI)
```

- [ ] **Step 2: Add source-taxonomy subgraph**

Create one node for each of the five paper-level aspects and subordinate nodes for Human Feedback, Interaction, Orchestration, and Communication categories.

- [ ] **Step 3: Apply exact relevance labels**

Show competition and coopetition as `NOT RELEVANT AT ALL`; show orchestration and communication as `LESS RELEVANT`; show Environment & Profiling, Human Feedback, and Collaboration as `HIGHLY RELEVANT`.

- [ ] **Step 4: Add VEGO-AI-derived subgraph**

Every derived branch must display `MISSING FROM ACL TAXONOMY` plus its RQ/study artifact.

- [ ] **Step 5: Add evidence-boundary footer nodes**

Include:

```text
QL-01–QL-05: 0/5 | ACL full disposition: incomplete | EXP-005: 0/24 | Medical: 0/6
```

and:

```text
Author-generated synthesis; not exhaustive; provisional RQs; no empirical contribution claim.
```

- [ ] **Step 6: Commit**

```bash
git add docs/visualizations/vego-ai-acl-taxonomy-map-v16.mmd
git commit -m "docs: add editable ACL-to-VEGO taxonomy diagram"
```

---

### Task 3: Build the standalone vector SVG

**Files:**
- Create: `docs/visualizations/vego-ai-acl-taxonomy-map-v16.svg`

**Interfaces:**
- Consumes: semantic ordering and wording from Tasks 1–2.
- Produces: high-resolution, thesis/deck-ready vector figure.

- [ ] **Step 1: Create SVG canvas and typography**

Use an approximately A3 portrait aspect ratio, white background, serif body text, thin black connectors, rounded pastel boxes, and a four-column hierarchy matching the reference visual grammar.

- [ ] **Step 2: Render ACL source sections**

Color-code Environment & Profiling, Human Feedback, Interaction, Orchestration, and Communication. Prefix each major section with `ACL SOURCE`.

- [ ] **Step 3: Render VEGO-AI extension sections**

Use a separate neutral/teal family and prefix each major section with `VEGO-AI ADDITION`.

- [ ] **Step 4: Add bottom legend and scope note**

The legend must explain provenance, relevance labels, RQ mappings, and open gates.

- [ ] **Step 5: Perform static SVG validation by inspection**

Verify:

```text
XML declaration present
one root <svg>
all opened groups closed
viewBox present
no external image/font dependency
all four relevance labels appear
all three current study artifact names appear
```

- [ ] **Step 6: Commit**

```bash
git add docs/visualizations/vego-ai-acl-taxonomy-map-v16.svg
git commit -m "docs: add thesis-ready ACL taxonomy SVG"
```

---

### Task 4: Wire navigation and record the strict audit

**Files:**
- Modify: `docs/research/phd-proposal/README.md`
- Create: `docs/research/phd-proposal/acl-taxonomy-v16-strict-audit.md`

**Interfaces:**
- Consumes: all Task 1–3 deliverables.
- Produces: discoverable entry point and explicit verification/limitation record.

- [ ] **Step 1: Add a current literature-taxonomy entry to README**

State that the v16 map is a controlled derived classification and not approved/exhaustive.

- [ ] **Step 2: Write the audit note**

Record:

- five paper-level vs four repository-branch denominator;
- exact relevance scale;
- source vs Ali-derived branch count;
- Chapter 4 artifact reconciliation;
- Fervers correction retained;
- Raykar/Aamodt and Dellermann/Dhanorkar not silently resolved;
- local script/render checks not executed in the connector-only environment;
- gates unchanged.

- [ ] **Step 3: Commit**

```bash
git add docs/research/phd-proposal/README.md \
        docs/research/phd-proposal/acl-taxonomy-v16-strict-audit.md
git commit -m "docs: wire and audit ACL taxonomy v16"
```

---

### Task 5: Verify branch and open a draft PR

**Files:**
- No additional source files required.

**Interfaces:**
- Consumes: branch diff.
- Produces: reviewable GitHub PR with claim boundaries.

- [ ] **Step 1: Compare branch against main**

Expected changed paths are limited to the spec, plan, evidence map, CSV, Mermaid, SVG, README, and audit note.

- [ ] **Step 2: Check for prohibited claims**

Search changed text for unsupported uses of:

```text
validated
safe transfer
systematic review complete
approved RQ
empirically improves
medical readiness
```

Any occurrence must be either negated/bounded or removed.

- [ ] **Step 3: Open a draft PR**

The PR body must state:

- documentation/visualization only;
- no runtime changes;
- no evidence gate changes;
- what was source-derived vs Ali-derived;
- what could not be executed locally;
- exact reviewer questions.

- [ ] **Step 4: Inspect PR changed-file list and diff**

Reject unexpected paths or generated drift.

- [ ] **Step 5: Record CI/check status without inventing a pass**

If no workflow is triggered or checks are unavailable, write `not run / unavailable`, not `passed`.
