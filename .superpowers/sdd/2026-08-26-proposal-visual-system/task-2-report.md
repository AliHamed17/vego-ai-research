# Task 2 — Deterministic dual-format renderer report

## Delivery

Implemented the focused shared renderer only; no proposal figure modules or generated figures were added.

- Immutable top-left-coordinate `Scene` model and primitives: text, rectangle, rounded rectangle,
  diamond, cylinder, parallelogram, arrow-bearing polyline, and group.
- Fail-closed validation for artboard bounds (including stroke bleed), 7 pt text minimum, text contrast,
  geometry, dash semantics, role metadata, and explicit polygon arrowheads.
- Immutable Carlito/Okabe-Ito-compatible visual tokens with WCAG contrast calculation.
- Deterministic standalone SVG output: paths/shapes/text only, local Carlito regular and bold embedded as
  base64 `data:font/ttf` resources, no image elements, HTTP(S) resources, or marker arrowheads.
- Deterministic ReportLab PDF output: shared top-left coordinate contract, fixed invariant metadata,
  embedded/subset Carlito fonts, and no image drawing operations.
- Vector-integrity tests prove deterministic SHA-256 equality across repeated SVG/PDF renders, zero PDF
  image XObjects, and embedded Carlito PDF font resources.

## Font provenance

The one permitted source fetch was completed from the official Google Fonts `ofl/carlito` directory.
The repository now has no runtime font network dependency.

| File | Bytes | SHA-256 |
| --- | ---: | --- |
| `Carlito-Regular.ttf` | 628032 | `F6418F708BAEDE9789DAEF5D458C0F53D2A888AF9820E8062934E504FEDC6595` |
| `Carlito-Bold.ttf` | 682468 | `BB5D20F79B82599EC72983597437373A80F2D2085FA91FC144FD74E876A594DB` |
| `OFL.txt` | 4424 | `58402F82A7C332A700294988FE7554FBB0A63A8D27CCC1EE3BBC640311990A00` |

The corresponding official URLs, byte counts, hashes, and license receipt are recorded in
`docs/research/phd-proposal/figures/vendor/fonts/manifest.json`.

## TDD evidence

1. The initial contract test was added first and failed during collection with
   `ModuleNotFoundError: No module named 'proposal_visuals.model'`.
2. The model and backends were implemented until the focused tests passed.
3. A follow-up clipping test was added first, failed because a 2 pt stroke at x=0 was accepted, then
   passed after validation expanded every stroked shape/polyline bound by half its line width.
4. A clean `uv sync` then exposed that the requested plain `uv run pytest` could not import `pypdf`.
   `pypdf` was promoted from the optional thesis group to the runtime dependencies because existing content
   imports and the PDF-integrity test require it. The clean sync and requested commands then passed.

## Verification

Base HEAD: `644daf989957fd7834b3f359c8be1ab7d9b4dbb5`.

| Command | Result |
| --- | --- |
| `uv run pytest tests/proposal_visuals/test_renderer.py -q` | `5 passed in 2.34s` |
| `uv run ruff check src/proposal_visuals tests/proposal_visuals` | `All checks passed!` |
| `uv run pytest -q` | `65 passed in 5.39s` |
| `git diff --check` | One intentional upstream-license whitespace notice: `OFL.txt:22` |

## Concerns / follow-on boundary

- This task deliberately does not construct any of the eleven figures. Later figure modules must place
  elements inside a half-line-width inset, because the renderer correctly refuses visible stroke clipping.
- Text wrapping uses a deterministic local width approximation rather than backend-specific font metrics so
  SVG and PDF retain the same scene geometry. Final figure work should still use the required visual QA at
  proposed print widths.
- `reportlab==4.4.9` and `pypdf==6.15.0` are runtime-pinned in `pyproject.toml`; this is necessary for a
  fresh plain test run and deterministic PDF/vector-integrity checks.
- The verbatim Google Fonts `OFL.txt` includes a trailing space on line 22. It is retained so the vendor
  receipt hash matches the fetched license; the scoped `.gitattributes` rule now preserves it without a
  `git diff --check` warning.

## Follow-up review remediation

The Task 2 review findings were remediated without adding figure modules or later-task work.

- Replaced the fixed `0.52` character-width heuristic with ReportLab measurements from the same pinned
  Carlito regular/bold TTFs that the PDF backend embeds. Wrapping and artboard bounds now share this metric
  path; an unbreakable measured token that exceeds `max_width` fails closed rather than clipping.
- Introduced one bounded `CylinderGeometry` contract for validation, SVG, and PDF. The SVG cubic controls
  remain inside the declared shape bounds, and the PDF now applies hatch clipping before drawing the shared
  top ellipse.
- Allow-listed paint values to the frozen token palette and allow-listed the local `diagonal` hatch name.
  All external/URL/non-token fill or stroke values fail validation before rendering.
- Added `OFL.txt` byte count to the font manifest and a receipt verifier that validates URL, bytes, and
  SHA-256 for Carlito regular, Carlito bold, and the exact OFL receipt.
- Preserved validated group semantics in SVG `data-meta-*` attributes and in deterministic PDF `/Keywords`
  metadata as canonical JSON.
- Added the exact `.gitattributes` whitespace exception for the upstream license file, leaving its bytes and
  recorded SHA-256 unchanged. This removes the prior diff-check warning.
- Rejected non-positive `Polyline.line_width` explicitly.

### Follow-up TDD evidence

The review regression suite was added before implementation and first failed at collection because
`cylinder_geometry` did not exist. A metric probe then demonstrated the unsafe heuristic: at 8 pt, regular
Carlito measures `WWWW` at `28.46875` pt but `iiiiiiii` at `14.6875` pt (bold: `29.0` and `15.71875` pt).
The new tests cover both weights, bounded/hatching cylinder output, external paint rejection, complete font
receipts, group semantic serialization, and Polyline width validation.

### Follow-up verification

| Command | Result |
| --- | --- |
| `uv run pytest tests/proposal_visuals/test_renderer.py -q` | `15 passed in 1.34s` |
| `uv run ruff check src/proposal_visuals tests/proposal_visuals` | `All checks passed!` |
| `uv run pytest -q` | `75 passed in 5.89s` |
| `git diff --check 644daf989957fd7834b3f359c8be1ab7d9b4dbb5..HEAD` | Passed with no output after commit |

## Final finite-geometry remediation

Added fail-closed `math.isfinite` validation before every numeric comparison, bounds calculation, metric
measurement, or backend call. The protected numeric surface includes artboard width/height; all text layout
scalars; base-shape geometry and line widths; rounded-rectangle radius; parallelogram skew; every polyline
and arrowhead coordinate; and polyline line width. Cylinder, diamond, and parallelogram inherit the same
base-shape scalar gate, while their additional scalars are checked before their specialized geometry paths.

The adversarial regression suite exercises NaN, positive infinity, and negative infinity across this surface,
including the reviewer examples `Rect(nan, ...)` and `Text(..., font_size=nan)`. Each invalid scene must raise
`SceneValidationError` containing `finite` from `validate_scene`, `render_svg`, and `render_pdf`; neither
backend output path may be created.

| Command | Result |
| --- | --- |
| `uv run pytest tests/proposal_visuals/test_renderer.py -q` | `32 passed in 1.19s` |
| `uv run ruff check src/proposal_visuals tests/proposal_visuals` | `All checks passed!` |
| `uv run pytest -q` | `92 passed in 8.99s` |
| `git diff --check` | Passed with no output before commit |

## SVG standalone namespace remediation

Added the mandatory default SVG namespace exactly once on every emitted root element:
`xmlns="http://www.w3.org/2000/svg"`. The regression initially failed because the root had no namespace.
It now renders a small SVG, parses it with `xml.etree.ElementTree`, and verifies the root tag is
`{http://www.w3.org/2000/svg}svg`.

The vector-external-resource check was retained with its intended meaning: the one required SVG namespace
is allowed, while any additional `http://` occurrence or any `https://` reference fails. No browser smoke
test was needed because the standards-aware parser is direct evidence for this focused markup change.

| Command | Result |
| --- | --- |
| `uv run pytest tests/proposal_visuals/test_renderer.py -q` | `33 passed in 2.56s` |
| `uv run ruff check src/proposal_visuals tests/proposal_visuals` | `All checks passed!` |
| `uv run pytest -q` | `97 passed in 8.71s` |
| `git diff --check` | Passed with no output before commit |
