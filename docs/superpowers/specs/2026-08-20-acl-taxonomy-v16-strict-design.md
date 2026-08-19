# ACL-2026 Taxonomy → VEGO-AI Relevance Map v16 — Strict Design

**Status:** Approved implementation scope for branch `docs/acl-taxonomy-v16-strict`. This is a documentation/visualization enhancement only. It does not approve the provisional RQs, close a literature-search gate, validate a contribution, or change any VEGO-AI runtime behavior.

## 1. Goal

Create a thesis-ready, source-traceable taxonomy figure in the visual form of Zou et al. (ACL 2026), while making the intellectual ownership and evidence boundary explicit:

1. reproduce the **classification structure**, not the source figure artwork;
2. distinguish the survey's own dimensions from Ali's VEGO-AI-specific synthesis;
3. use Iris's exact relevance scale;
4. map the relevant branches to the current provisional RQs and the narrower one-artifact-per-study methodology in Chapter 4;
5. retain all open evidence and approval gates.

## 2. Authoritative inputs

| Input | Permitted use | Prohibited use |
| --- | --- | --- |
| Zou et al. (2026), *LLM-Based Human-Agent Collaboration and Interaction Systems: A Survey* | Names/definitions of the five paper-level core components and their subdimensions; source-taxonomy provenance | Copying the original figure layout pixel-for-pixel; treating the survey as proof of a VEGO-AI-specific gap |
| Survey companion GitHub repository | Confirms the repository's four taxonomy navigation branches: Human Feedback, Interaction, Orchestration, Communication | Treating repository headings as an exhaustive research corpus |
| VEGO-AI literature review v10 | Provisional RQs, evidence levels, current synthesis, claim boundaries, anchor-source identities | Upgrading provisional wording to approved wording; claiming systematic-review completion |
| `chapter-4-research-methodology.md` | Current narrower artifact recommendation for each study | Replacing that structure with the older bundled C1–C7 component list |
| `literature-package-v15-verification-report.md` | Verified defect list and ACL-classification repair requirements | Reintroducing superseded or corrected findings; treating composite readiness scores as authoritative closure evidence |

## 3. Source taxonomy denominator

The survey paper analyzes **five core aspects**:

1. Environment & Profiling
2. Human Feedback
3. Interaction Type
4. Orchestration Paradigm
5. Communication

The companion repository exposes **four taxonomy navigation branches**: Human Feedback, Interaction, Orchestration, and Communication. Environment & Profiling remains a paper-level core aspect even though it is not a separate taxonomy heading in that repository navigation.

The v16 map must show both denominators and must not present a seven-branch VEGO-AI synthesis as though all seven branches came from the source taxonomy.

## 4. Exact relevance scale

Every source-derived branch or subbranch must use exactly one of the following labels:

- **HIGHLY RELEVANT**
- **LESS RELEVANT**
- **NOT RELEVANT AT ALL**
- **MISSING FROM ACL TAXONOMY**

`MISSING FROM ACL TAXONOMY` applies only to Ali-derived VEGO-AI requirements that are not first-class branches in the source taxonomy. It does not mean the survey never discusses a related concept somewhere in its prose.

## 5. Classification decisions

### 5.1 ACL source dimensions

| Source dimension | Relevance | VEGO-AI interpretation |
| --- | --- | --- |
| Environment & Profiling | HIGHLY RELEVANT | Supports claim-specific roles, expertise, authority, domain/task context, agent capabilities, and software/medical scenario boundaries. |
| Human Feedback | HIGHLY RELEVANT | Directly structures feedback type, granularity, and phase; most important source branch for SQ1 and SQ2. |
| Interaction Type — Collaboration | HIGHLY RELEVANT | Supervision, delegation, coordination, and cooperation describe the human-agent relationship around review and judgment. |
| Interaction Type — Competition | NOT RELEVANT AT ALL | Outside the current thesis scope; VEGO-AI does not study adversarial human-versus-agent goal competition. |
| Interaction Type — Coopetition | NOT RELEVANT AT ALL | Outside the current thesis scope; no mixed cooperative/competitive objective is proposed or evaluated. |
| Orchestration Paradigm | LESS RELEVANT | Useful for intervention timing and synchronous/asynchronous review, but not the primary research contribution. |
| Communication | LESS RELEVANT | Enabling design concern for evidence presentation and feedback flow, not an independent thesis contribution. |

### 5.2 VEGO-AI dimensions missing as first-class ACL taxonomy branches

| Ali-derived dimension | Relevance label | RQ / study relationship |
| --- | --- | --- |
| Selective intervention under bounded attention | MISSING FROM ACL TAXONOMY | SQ1 / Study 1 — attention-budget cost/coverage model |
| Reasoning-rich judgment representation | MISSING FROM ACL TAXONOMY | SQ2 / Study 2 — normative judgment-record contract |
| Claim-specific authority, contestability, lifecycle, expiry, and revocation | MISSING FROM ACL TAXONOMY | SQ2 / Study 2 — conformance suite and governance requirements |
| Scope-aware reuse: retrieval → applicability → permission → advisory use → outcome | MISSING FROM ACL TAXONOMY | SQ2–SQ3 boundary; reuse logic must not be collapsed into similarity |
| Transfer eligibility and leakage-safe evaluation | MISSING FROM ACL TAXONOMY | SQ3 / Study 3 — transfer-eligibility decision procedure |
| Variability exploration and guideline operationalization | MISSING FROM ACL TAXONOMY | Target problem substrate; not a generic LLM-HAS taxonomy branch |

## 6. Visual architecture

The figure must preserve the visual grammar of the reference image without copying its artwork:

- a vertical root label on the left;
- color-coded major sections;
- a second column for dimensions;
- a third column for categories/subcategories;
- a wide evidence/relevance column on the right;
- thin orthogonal connectors;
- rounded boxes;
- a bottom legend explaining provenance and the relevance scale.

The visual must separate:

1. **ACL SOURCE TAXONOMY** — source-derived branches;
2. **VEGO-AI DERIVED EXTENSIONS** — Ali's gap-led synthesis;
3. **CURRENT STUDY ARTIFACTS** — one narrower artifact per SQ from Chapter 4.

## 7. Source and claim discipline

The map must contain the following caption or equivalent:

> Author-generated RQ-led synthesis based on Zou et al. (2026), the controlled VEGO-AI literature review, and the current Chapter 4 methodology. It is not a copy of the source taxonomy figure, not evidence of exhaustive literature coverage, and not a supervisor-approved RQ or contribution claim.

Rules:

- Do not list a paper as a core anchor merely because it appears in the survey.
- Do not silently decide the Raykar/Aamodt or Dellermann/Dhanorkar anchor-lineage issue in the figure.
- Preserve Fervers et al. (2006) as a valid, distinct source; it is not a year-error regression.
- Prefer problem-world labels over C1–C7 solution component names.
- Use the current Chapter 4 artifact names:
  - attention-budget cost/coverage model;
  - normative judgment-record contract + conformance suite;
  - transfer-eligibility decision procedure + target-context descriptor.
- Keep QL-01–QL-05 = 0/5, ACL full-corpus disposition incomplete, EXP-005 = 0/24, and medical readiness = 0/6 visible in supporting documentation; the visual itself may show a compact `OPEN GATES` note.

## 8. Deliverables

1. `docs/research/phd-proposal/acl-2026-taxonomy-vego-ai-relevance-map-v16.md`
2. `docs/research/phd-proposal/acl-2026-taxonomy-evidence-matrix-v16.csv`
3. `docs/visualizations/vego-ai-acl-taxonomy-map-v16.mmd`
4. `docs/visualizations/vego-ai-acl-taxonomy-map-v16.svg`
5. PhD proposal README navigation update
6. A strict change/audit note and draft PR

## 9. Acceptance criteria

- [ ] The paper-level denominator is five core aspects.
- [ ] The companion-repository taxonomy denominator is four navigation branches.
- [ ] Every source branch is marked with Iris's exact scale.
- [ ] Competition and coopetition are explicitly classified `NOT RELEVANT AT ALL` for this thesis scope.
- [ ] Every Ali-derived addition is labeled `MISSING FROM ACL TAXONOMY` and clearly identified as derived synthesis.
- [ ] The three study artifacts match Chapter 4 rather than C1–C7.
- [ ] No evidence gate is upgraded.
- [ ] No systematic/exhaustive coverage claim is introduced.
- [ ] The figure is legible in SVG and the source remains editable in Mermaid.
- [ ] The PR body states what was and was not verified in this connector-only execution environment.
