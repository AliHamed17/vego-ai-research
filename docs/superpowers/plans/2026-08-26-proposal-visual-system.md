# VEGO-AI Proposal Visual System Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build eleven reproducible vector visuals, integrate the ten replacements into a derived proposal DOCX/PDF, and publish evidence-backed accessibility and integrity receipts.

**Architecture:** A frozen proposal-derived content manifest feeds one deterministic scene graph with SVG and ReportLab PDF backends. Per-figure source modules contain only geometry and presentation choices; shared tokens enforce semantics, typography, sizing, and accessibility. Document integration is a separate fail-closed Windows/Word step that works only on a copy and cannot weaken standalone figure delivery.

**Tech Stack:** Python 3.10+, stdlib XML/JSON/dataclasses, ReportLab, Pillow, pypdf, python-docx, PowerShell 7/Windows PowerShell, Microsoft Word COM for the optional local integration path, pytest, ruff, Poppler for page rendering.

**Spec:** `docs/superpowers/specs/2026-08-26-proposal-visual-system-design.md`

## Global Constraints

- The attached proposal PDF hash is `ADB663A4B8B0FFD3F09F2CEFEF43D690B5540FC36D4947FF60DCC624072846C9`.
- The source PDF has 31 A4 pages, 10 figures, 14 tables, and zero raster-image XObjects.
- The Downloads DOCX is never modified in place.
- Shapes: rectangle=artifact/record; rounded rectangle=process/agent; diamond=decision; cylinder=store; parallelogram=human input.
- Lines: solid=committed/existing; dashed=conditional/proposed/gated; dotted=information reference.
- Palette roles: navy=baseline; Okabe-Ito orange=doctoral human-judgment layer; cool grey=conditional/gated/out of scope.
- Colour is never the sole carrier of meaning.
- Final labels are at least 7 pt; ordinary labels target at least 8 pt.
- Every text-on-fill combination must meet WCAG 4.5:1.
- SVG and PDF outputs contain no raster images or external font/style dependencies.
- Figure 8 uses the exact four data pairs and an untruncated 0-1 y-axis.
- Figure 9 covers October 2027-October 2030, with October 2026-October 2027 outside the three-year count and a September 2029 medical go/no-go.
- No visual implies accuracy, generalization, reduced effort, transfer safety, clinical readiness, or completed validation.
- EXP-005 remains 0/24 and medical readiness remains 0/6.
- Use red-green-refactor for every new behavior.

---

### Task 1: Freeze provenance and proposal-derived content

**Files:**
- Create: `src/proposal_visuals/__init__.py`
- Create: `src/proposal_visuals/content.py`
- Create: `docs/research/phd-proposal/figures/content.json`
- Create: `docs/research/phd-proposal/figures/source-provenance.json`
- Create: `tests/proposal_visuals/test_content.py`

**Interfaces:**
- Consumes: the approved spec and exact PDF-derived labels.
- Produces: `load_content(path: Path) -> VisualContent`; immutable `FigureContent` records keyed `fig-01` through `fig-11`.

- [ ] **Step 1: Write failing manifest tests**

```python
def test_manifest_has_exact_figure_contracts(content_path: Path) -> None:
    content = load_content(content_path)
    assert list(content.figures) == [f"fig-{n:02d}" for n in range(1, 12)]
    assert len(content.figures["fig-01"].items["readings"]) == 6
    assert len(content.figures["fig-05"].items["signals"]) == 8
    assert len(content.figures["fig-05"].items["actions"]) == 6
    assert content.figures["fig-07"].items["statuses"] == [
        "Eligible", "Eligible with adaptation", "Blocked", "Undetermined"
    ]
    assert len(content.figures["fig-10"].items["missing_concepts"]) == 11
    assert sum(content.figures["fig-11"].items["paper_disposition"].values()) == 90
```

- [ ] **Step 2: Run the test and confirm the missing-loader failure**

Run: `uv run pytest tests/proposal_visuals/test_content.py -q`

Expected: FAIL because `proposal_visuals.content` does not exist.

- [ ] **Step 3: Implement immutable content loading and validation**

```python
@dataclass(frozen=True)
class FigureContent:
    figure_id: str
    title: str
    caption: str
    provenance: str
    alt_text: str
    locators: tuple[str, ...]
    items: Mapping[str, Any]

def load_content(path: Path) -> VisualContent:
    payload = json.loads(path.read_text(encoding="utf-8"))
    expected = [f"fig-{n:02d}" for n in range(1, 12)]
    if list(payload["figures"]) != expected:
        raise ValueError("figure IDs must be ordered fig-01 through fig-11")
    return VisualContent.from_mapping(payload)
```

Populate the JSON with exact Figure 1 readings, Figure 5 signals/actions, Figure 6 states,
Figure 7 gates/statuses/AND checks, Figure 8 values, Figure 9 dates, Figure 10 concepts in Table 11
order, and Figure 11 screening/coverage values. Give every claim a PDF page and section/table locator.

- [ ] **Step 4: Add provenance hash verification**

```python
def verify_source_hash(path: Path, expected: str) -> None:
    actual = hashlib.sha256(path.read_bytes()).hexdigest().upper()
    if actual != expected.upper():
        raise ValueError(f"source drift: expected {expected}, got {actual}")
```

- [ ] **Step 5: Run tests and lint**

Run: `uv run pytest tests/proposal_visuals/test_content.py -q`

Run: `uv run ruff check src/proposal_visuals tests/proposal_visuals/test_content.py`

Expected: PASS with no warnings.

- [ ] **Step 6: Commit**

```powershell
git add -- src/proposal_visuals docs/research/phd-proposal/figures/content.json docs/research/phd-proposal/figures/source-provenance.json tests/proposal_visuals/test_content.py
git commit -m "feat: freeze proposal visual content"
```

### Task 2: Build the deterministic dual-format renderer

**Files:**
- Create: `src/proposal_visuals/model.py`
- Create: `src/proposal_visuals/tokens.py`
- Create: `src/proposal_visuals/svg_backend.py`
- Create: `src/proposal_visuals/pdf_backend.py`
- Create: `src/proposal_visuals/fonts.py`
- Create: `docs/research/phd-proposal/figures/vendor/fonts/Carlito-Regular.ttf`
- Create: `docs/research/phd-proposal/figures/vendor/fonts/Carlito-Bold.ttf`
- Create: `docs/research/phd-proposal/figures/vendor/fonts/OFL.txt`
- Create: `docs/research/phd-proposal/figures/vendor/fonts/manifest.json`
- Create: `tests/proposal_visuals/test_renderer.py`

**Interfaces:**
- Consumes: `FigureContent` and `VisualTokens`.
- Produces: `Scene`, `render_svg(scene, output_path)`, `render_pdf(scene, output_path)`, and `validate_scene(scene)`.

- [ ] **Step 1: Write failing renderer-contract tests**

```python
def test_scene_rejects_out_of_bounds_and_tiny_text() -> None:
    with pytest.raises(SceneValidationError, match="outside artboard"):
        validate_scene(Scene(width=100, height=100, elements=(Text(-1, 20, "bad", 8),)))
    with pytest.raises(SceneValidationError, match="below 7 pt"):
        validate_scene(Scene(width=100, height=100, elements=(Text(10, 20, "bad", 6.9),)))

def test_svg_is_standalone_vector(tmp_path: Path, sample_scene: Scene) -> None:
    target = tmp_path / "sample.svg"
    render_svg(sample_scene, target)
    text = target.read_text(encoding="utf-8")
    assert "<image" not in text
    assert "http://" not in text and "https://" not in text
    assert "data:font/ttf;base64," in text
```

- [ ] **Step 2: Run the tests and confirm missing-model/backend failures**

Run: `uv run pytest tests/proposal_visuals/test_renderer.py -q`

Expected: FAIL because the renderer modules do not exist.

- [ ] **Step 3: Implement focused scene primitives**

```python
Element = Text | Rect | RoundedRect | Diamond | Cylinder | Parallelogram | Polyline | Group

@dataclass(frozen=True)
class Scene:
    width: float
    height: float
    elements: tuple[Element, ...]
    title: str
    description: str
```

Implement explicit arrowhead polygons, measured wrapped text, shape bounds, dash styles, hatching,
and semantic-role metadata. Reject clipping before rendering.

- [ ] **Step 4: Vendor and register Carlito**

Fetch `Carlito-Regular.ttf`, `Carlito-Bold.ttf`, and `OFL.txt` from the Google Fonts `ofl/carlito`
directory, record URL/size/SHA-256 in `manifest.json`, and commit the exact files. Register the TTFs
with ReportLab and embed their base64 bytes in each SVG's internal `<style>`.

- [ ] **Step 5: Implement matching SVG and PDF backends**

```python
def render_svg(scene: Scene, output_path: Path) -> None:
    validate_scene(scene)
    output_path.write_text(SvgRenderer().render(scene), encoding="utf-8")

def render_pdf(scene: Scene, output_path: Path) -> None:
    validate_scene(scene)
    PdfRenderer(output_path, scene.width, scene.height).render(scene)
```

PDF coordinates must transform exactly from the same top-left scene coordinate system used by SVG.

- [ ] **Step 6: Prove determinism and vector integrity**

Add a test that renders each format twice and compares SHA-256 after deterministic ReportLab metadata
is fixed. Reopen PDFs with pypdf and assert zero `/Image` XObjects and embedded Carlito fonts.

- [ ] **Step 7: Run tests and lint**

Run: `uv run pytest tests/proposal_visuals/test_renderer.py -q`

Run: `uv run ruff check src/proposal_visuals tests/proposal_visuals`

Expected: PASS.

- [ ] **Step 8: Commit**

```powershell
git add -- src/proposal_visuals docs/research/phd-proposal/figures/vendor tests/proposal_visuals/test_renderer.py
git commit -m "feat: add deterministic proposal vector renderer"
```

### Task 3: Implement Figures 1-4

**Files:**
- Create: `docs/research/phd-proposal/figures/sources/fig_01_six_readings.py`
- Create: `docs/research/phd-proposal/figures/sources/fig_02_vego_baseline.py`
- Create: `docs/research/phd-proposal/figures/sources/fig_03_gap_mapping.py`
- Create: `docs/research/phd-proposal/figures/sources/fig_04_programme_spine.py`
- Create: `tests/proposal_visuals/test_figures_01_04.py`

**Interfaces:**
- Consumes: `FigureContent`, `VisualTokens`, and scene primitives.
- Produces: `build(content: FigureContent, tokens: VisualTokens) -> Scene` in every module.

- [ ] **Step 1: Write failing semantic-structure tests**

```python
def test_figure_1_has_equal_six_way_fanout(fig1: Scene) -> None:
    branches = [e for e in fig1.elements if e.metadata.get("role") == "reading-branch"]
    assert len(branches) == 6
    assert len({e.stroke_width for e in branches}) == 1
    assert not any(e.metadata.get("role") == "reading-convergence" for e in fig1.elements)

def test_figure_4_is_four_by_four_spine(fig4: Scene) -> None:
    assert scene_metadata(fig4, "columns") == 4
    assert scene_metadata(fig4, "rows") == ["SQ1", "SQ2", "SQ3", "Integrated"]
```

- [ ] **Step 2: Run tests and confirm module-import failures**

Run: `uv run pytest tests/proposal_visuals/test_figures_01_04.py -q`

- [ ] **Step 3: Implement Figure 1**

Use one origin, a 2x3 equal sibling grid, identical branch geometry, the exact six Section 1.7
readings, a non-converging layout, the corrected sentence, and the complete visual-language legend.

- [ ] **Step 4: Implement Figure 2**

Use a left-to-right four-agent pipeline, edge labels for all exchanged artifacts, an explicit
Variability Explorer-to-Domain Advisor refinement loop, and a secondary dashed attachment band.

- [ ] **Step 5: Implement Figure 3**

Use five established-stream nodes, an unfilled dashed open-gap boundary, three gap-to-SQ rows, and a
dotted reference from SQ1-SQ3 to the umbrella evaluation without visually closing the gap.

- [ ] **Step 6: Implement Figure 4**

Use exact row and column guides, bounded cell wrapping, a visually distinct integrated row, and
arrows showing that the integrated evaluation consumes all three component rows.

- [ ] **Step 7: Run targeted tests and render smoke checks**

Run: `uv run pytest tests/proposal_visuals/test_figures_01_04.py tests/proposal_visuals/test_renderer.py -q`

Render each to temporary SVG/PDF and run `validate_scene` before writing.

- [ ] **Step 8: Commit**

```powershell
git add -- docs/research/phd-proposal/figures/sources tests/proposal_visuals/test_figures_01_04.py
git commit -m "feat: redraw proposal figures 1 through 4"
```

### Task 4: Implement Figures 5-7

**Files:**
- Create: `docs/research/phd-proposal/figures/sources/fig_05_review_policy.py`
- Create: `docs/research/phd-proposal/figures/sources/fig_06_judgment_lifecycle.py`
- Create: `docs/research/phd-proposal/figures/sources/fig_07_reuse_procedure.py`
- Create: `tests/proposal_visuals/test_figures_05_07.py`

**Interfaces:**
- Consumes: shared figure build interface.
- Produces: three validated scenes with explicit semantic-role metadata.

- [ ] **Step 1: Write failing count and state-machine tests**

```python
def test_figure_5_separates_budget_from_signals(fig5: Scene) -> None:
    assert count_role(fig5, "policy-signal") == 8
    assert count_role(fig5, "routing-action") == 6
    assert count_role(fig5, "budget-constraint") == 1

def test_figure_7_separates_status_from_diagnosis(fig7: Scene) -> None:
    assert labels_for_role(fig7, "formal-status") == [
        "Eligible", "Eligible with adaptation", "Blocked", "Undetermined"
    ]
    assert count_role(fig7, "capability-gap-check") == 4
    assert scene_metadata(fig7, "gate_count") == 5
```

- [ ] **Step 2: Run tests and confirm missing-module failures**

Run: `uv run pytest tests/proposal_visuals/test_figures_05_07.py -q`

- [ ] **Step 3: Implement Figure 5**

Draw literature-derived and proposed signals in separate labelled groups. Enclose the central policy
with the matched-budget constraint. Route hard rules around the policy. Keep all six actions equal in
visual weight except the blocked action's dashed gated encoding.

- [ ] **Step 4: Implement Figure 6**

Draw field groups in the left panel and the six-state transition graph on the right. Use explicit
transition labels and visually retain auditability for terminal states. Record the Draft/Reviewed/
Active versus Created/Validated discrepancy in scene metadata for the final QA report.

- [ ] **Step 5: Implement Figure 7**

Draw five gates in sequence. Send failed or incomplete evidence to `Blocked` or `Undetermined` with
reason-labelled edges. Send passed cases to `Eligible` or `Eligible with adaptation`. Only then show
the local-quirk/capability-gap diagnostic split and the four-check AND guard.

- [ ] **Step 6: Run targeted tests and render smoke checks**

Run: `uv run pytest tests/proposal_visuals/test_figures_05_07.py tests/proposal_visuals/test_renderer.py -q`

- [ ] **Step 7: Commit**

```powershell
git add -- docs/research/phd-proposal/figures/sources tests/proposal_visuals/test_figures_05_07.py
git commit -m "feat: redraw proposal figures 5 through 7"
```

### Task 5: Implement Figures 8-11

**Files:**
- Create: `docs/research/phd-proposal/figures/sources/fig_08_expert_scores.py`
- Create: `docs/research/phd-proposal/figures/sources/fig_09_three_year_plan.py`
- Create: `docs/research/phd-proposal/figures/sources/fig_10_taxonomy_boundary.py`
- Create: `docs/research/phd-proposal/figures/sources/fig_11_corpus_screening.py`
- Create: `tests/proposal_visuals/test_figures_08_11.py`

**Interfaces:**
- Consumes: shared figure build interface.
- Produces: four validated scenes, including the standalone Figure 11 candidate.

- [ ] **Step 1: Write failing numerical/date/content tests**

```python
def test_figure_8_uses_exact_values_and_full_axis(fig8: Scene) -> None:
    assert scene_metadata(fig8, "y_domain") == [0.0, 1.0]
    assert scene_metadata(fig8, "pairs") == [
        [0.80, 0.55], [0.96, 0.81], [0.83, 0.55], [0.92, 0.88]
    ]

def test_figure_10_has_all_ordered_concepts(fig10: Scene, content: VisualContent) -> None:
    assert labels_for_role(fig10, "missing-concept") == content.figures["fig-10"].items["missing_concepts"]

def test_figure_11_keeps_levels_separate(fig11: Scene) -> None:
    assert scene_metadata(fig11, "paper_total") == 90
    assert scene_metadata(fig11, "missing_level") == "research-question"
```

- [ ] **Step 2: Run tests and confirm missing-module failures**

Run: `uv run pytest tests/proposal_visuals/test_figures_08_11.py -q`

- [ ] **Step 3: Implement Figure 8**

Draw grouped bars, full 0-1 grid, solid versus hatch series, direct numeric labels, and a caption-safe
legend. Treat both series as reported baseline evidence, never as doctoral-layer results.

- [ ] **Step 4: Implement Figure 9**

Draw preparatory, Year 1, Year 2, and Year 3 bands; six semester-aligned workstream bars; explicit
dependency arrows; Paper 1-3 and defence diamonds; and the dashed medical option with the September
2029 decision diamond outside the critical path.

- [ ] **Step 5: Implement Figure 10**

Use a 40/60 two-column layout, four branch cards, eleven ordered concept rows, and explicit claim-
scope text. Ensure the elicitation-trigger row is present and the design works at 16:9 slide width.

- [ ] **Step 6: Implement Figure 11**

Use a labelled 22/63/5 horizontal stacked bar and a compact U-RQ/SQ1/SQ2/SQ3 coverage panel. Encode
Yes/Partly/No with text and texture as well as colour. State single-rater/title-level limitations.

- [ ] **Step 7: Run targeted tests and render smoke checks**

Run: `uv run pytest tests/proposal_visuals/test_figures_08_11.py tests/proposal_visuals/test_renderer.py -q`

- [ ] **Step 8: Commit**

```powershell
git add -- docs/research/phd-proposal/figures/sources tests/proposal_visuals/test_figures_08_11.py
git commit -m "feat: redraw proposal figures 8 through 11"
```

### Task 6: Build outputs and accessibility QA

**Files:**
- Create: `scripts/build_proposal_visuals.py`
- Create: `src/proposal_visuals/qa.py`
- Create: `tests/proposal_visuals/test_qa.py`
- Create: `docs/research/phd-proposal/figures/README.md`
- Generate: `docs/research/phd-proposal/figures/rendered/svg/*.svg`
- Generate: `docs/research/phd-proposal/figures/rendered/pdf/*.pdf`
- Generate: `docs/research/phd-proposal/figures/qa/qa-receipt.json`
- Generate: `docs/research/phd-proposal/figures/qa/visual-review.md`

**Interfaces:**
- Consumes: eleven figure modules and shared renderer.
- Produces: `build_all(config: BuildConfig) -> BuildReceipt` and `run_qa(receipt: BuildReceipt) -> QaReceipt`.

- [ ] **Step 1: Write failing build/QA tests**

```python
def test_build_emits_complete_pair_set(tmp_path: Path) -> None:
    receipt = build_all(BuildConfig(output_root=tmp_path))
    assert len(receipt.figures) == 11
    assert all(item.svg.exists() and item.pdf.exists() for item in receipt.figures)

def test_palette_contrast_floor() -> None:
    ratios = all_text_fill_contrasts(default_tokens())
    assert min(ratios.values()) >= 4.5
```

- [ ] **Step 2: Run tests and confirm missing-build failures**

Run: `uv run pytest tests/proposal_visuals/test_qa.py -q`

- [ ] **Step 3: Implement one-command build**

The build command is:

```powershell
uv run python scripts/build_proposal_visuals.py --clean --verify
```

It removes only the explicit generated `rendered/` and `qa/generated/` children after validating
that their resolved paths remain under the figures directory. It writes stable manifests and hashes.

- [ ] **Step 4: Implement automated accessibility checks**

Compute WCAG contrast from tokens; render PDF pages through Poppler; create greyscale, protanopia,
and deuteranopia PNGs with fixed colour matrices; verify non-colour semantic redundancy from scene
metadata; and emit pass/fail plus the lowest contrast ratio per figure.

- [ ] **Step 5: Implement A4 and 400% checks**

Place each figure at its declared final width on a one-page A4 proof PDF, render at 144 dpi and 576
dpi, and verify vector structure directly from SVG/PDF. Create contact sheets for normal,
greyscale, protanopia, and deuteranopia views.

- [ ] **Step 6: Inspect every proof and record visual verdicts**

Open all eleven individual A4 proofs and all four contact sheets. Record clipping, line-crossing,
font-size, ambiguity, and consistency verdicts in `visual-review.md`. A visual failure blocks the
integrated build.

- [ ] **Step 7: Document rebuild commands and visual semantics**

List the exact one-line command for each figure and the all-figures command in `README.md`, along
with palette hex values, font sizes, shape/line meanings, and tool versions.

- [ ] **Step 8: Run full figure tests**

Run: `uv run pytest tests/proposal_visuals -q`

Run: `uv run ruff check src/proposal_visuals scripts/build_proposal_visuals.py tests/proposal_visuals`

- [ ] **Step 9: Commit**

```powershell
git add -- scripts/build_proposal_visuals.py src/proposal_visuals/qa.py tests/proposal_visuals/test_qa.py docs/research/phd-proposal/figures
git commit -m "feat: build and verify proposal visual package"
```

### Task 7: Integrate the ten replacement figures into a derived proposal

**Files:**
- Create: `scripts/integrate_proposal_visuals.ps1`
- Create: `src/proposal_visuals/integration.py`
- Create: `src/proposal_visuals/document_integrity.py`
- Create: `tests/proposal_visuals/test_integration.py`
- Create: `tests/proposal_visuals/test_document_integrity.py`
- Generate: `output/docx/VEGO_AI_Doctoral_Proposal_Visual_System_20260826.docx`
- Generate: `output/pdf/VEGO_AI_Doctoral_Proposal_Visual_System_20260826.pdf`
- Generate: `docs/research/phd-proposal/figures/qa/integration-receipt.json`

**Interfaces:**
- Consumes: frozen source DOCX, Figures 1-10 SVGs, content manifest, and passing QA receipt.
- Produces: `build_integration_plan(source_docx: Path, figures: Sequence[Path]) -> IntegrationPlan`; PowerShell applies the plan through Word COM to a copy.

- [ ] **Step 1: Write failing fail-closed integration tests**

```python
def test_integration_requires_ten_ordered_targets(source_docx: Path) -> None:
    plan = build_integration_plan(source_docx, figure_paths())
    assert [item.figure_id for item in plan.replacements] == [f"fig-{n:02d}" for n in range(1, 11)]

def test_source_hash_drift_blocks_integration(tmp_path: Path) -> None:
    source = tmp_path / "proposal.docx"
    source.write_bytes(b"changed")
    with pytest.raises(SourceDriftError):
        freeze_source(source, expected_sha256="0" * 64)
```

- [ ] **Step 2: Run tests and confirm missing-integration failures**

Run: `uv run pytest tests/proposal_visuals/test_integration.py -q`

- [ ] **Step 3: Implement pure integration planning and DOCX inspection**

Inspect the DOCX package for exactly ten existing vector media relationships, ten drawing objects,
and ten alt-text entries. Match captions in ascending order and reject duplicates, missing items, or
source drift before launching Word.

- [ ] **Step 4: Implement copy-only Word replacement**

The PowerShell script opens a copied DOCX in an invisible Word instance, replaces the ten inline
figures at their existing ranges, preserves widths, writes claim-focused alt text, changes only the
Figure 1 caption count, updates genuine fields, saves DOCX, exports PDF, and closes only documents it
opened. The source TOC is a static visible list rather than a native Word TOC, so no TOC-update claim
or operation is permitted. The script never writes the Downloads source.

- [ ] **Step 5: Run local integration**

```powershell
.\scripts\integrate_proposal_visuals.ps1 -SourceDocx '<path-to-frozen-source-docx>' -OutputRoot '.\output' -FigureRoot '.\docs\research\phd-proposal\figures\rendered\svg'
```

If the source remains locked or Word cannot produce a stable copy, stop integration and record the
exact blocker while retaining the complete standalone package.

- [ ] **Step 6: Verify derived document integrity**

Reopen DOCX and PDF through the pure-Python post-integration verifier. Require 31 pages, 10 exact
SVG bindings in Figure 1-10 order, the declared widths and alt text, unchanged scholarly body text and
citations outside the approved Figure 1 count correction, all 14 table captions in source order, all
39 static TOC rows unchanged and present on their declared PDF pages, zero dangling cross-references,
and zero raster-image XObjects. Only after those checks pass may a durable integration receipt be
created. Confirm Figure 11 remains standalone unless all insertion gates pass. The earlier 29-row TOC
count was an inspection error and is retired.

- [ ] **Step 7: Render and inspect every PDF page**

Render all 31 pages at 144 dpi and inspect each page for clipping, overlaps, headers, footers,
pagination, captions, tables, and figure placement. Reinspect the ten figure pages at 400%.

- [ ] **Step 8: Run integration tests and commit source/receipts**

Run: `uv run pytest tests/proposal_visuals/test_integration.py tests/proposal_visuals/test_document_integrity.py -q`

```powershell
git add -- scripts/integrate_proposal_visuals.ps1 src/proposal_visuals/integration.py src/proposal_visuals/document_integrity.py tests/proposal_visuals/test_integration.py tests/proposal_visuals/test_document_integrity.py docs/research/phd-proposal/figures/qa/integration-receipt.json
git commit -m "feat: integrate proposal visual system"
```

Do not track the derived DOCX/PDF unless repository policy explicitly permits these generated files.

### Task 8: Final verification, independent review, and draft PR

**Files:**
- Modify: `docs/research/phd-proposal/figures/qa/visual-review.md`
- Modify: `docs/agent-memory/session-log.md`
- Modify: `docs/agent-memory/revert-log.md`
- Modify: `docs/PROGRESS_TRACKER.md`

**Interfaces:**
- Consumes: frozen build/integration receipts and all code/tests.
- Produces: reviewer-ready branch and draft PR; no merge.

- [ ] **Step 1: Run the complete local verification set**

Run: `uv run pytest -q`

Run: `uv run ruff check src scripts/build_proposal_visuals.py tests`

Run: `uv run python scripts/build_proposal_visuals.py --clean --verify`

Run: `git diff --check`

Require zero failures and record exact counts.

- [ ] **Step 2: Reconcile every spec requirement**

Create a table in `visual-review.md` with one row per Figure 1-11 and columns for tool, change,
greyscale, protanopia, deuteranopia, contrast, A4 print, 400% zoom, label correctness, consistency,
and integrity. Record actual pass/fail; do not turn unavailable checks into passes.

- [ ] **Step 3: Run independent code and evidence review**

Dispatch a reviewer with the frozen commit. Reproduce every critical or important finding locally,
fix verified findings with failing tests first, and rerun the full verification set.

- [ ] **Step 4: Update project memory and tracking**

Run `agent-memory-finish.ps1` with exact files, commands, results, remaining gates, and rollback path.
Run `refresh-tracking.ps1 -Viz`, preserve dated evidence values when ignored runtime artifacts are
absent, then run the Confluence build/health workflow required by `AGENTS.md`.

- [ ] **Step 5: Push and open a draft PR**

Push `feature/proposal-visual-system`, open a draft PR against `main`, and include the source PDF hash,
test results, per-figure QA summary, derived-output status, evidence boundaries, and human-review
gate. Do not merge.

- [ ] **Step 6: Verify CI and handoff**

Wait for all required checks. Fix only verified branch defects. Final status is `Ready for Ali
review` only when CI is green and all available local gates pass; document integration may remain a
named blocker if the source lock or Word export cannot be safely resolved.
