# VEGO-AI proposal visual package

The deliverable is eleven standalone vector figure pairs: `rendered/svg/fig-01.svg` through
`fig-11.svg`, and the matching `rendered/pdf/` files. The build verifies the approved source before
loading the frozen content manifest. The public receipt records only the source filename, SHA-256,
and page count; it never records a local Downloads path.

## Rebuild

Run the complete deterministic build and QA pipeline on this machine:

```powershell
uv run python scripts/build_proposal_visuals.py --clean --verify
```

`--verify` safely resolves the provenance filename in the current user's Downloads directory. To use
another approved copy, supply it explicitly:

```powershell
uv run python scripts/build_proposal_visuals.py --clean --verify --source "<approved-pdf-path>"
```

Build one figure (without removing other generated figures) with:

```powershell
uv run python scripts/build_proposal_visuals.py --verify --figure fig-01
uv run python scripts/build_proposal_visuals.py --verify --figure fig-02
uv run python scripts/build_proposal_visuals.py --verify --figure fig-03
uv run python scripts/build_proposal_visuals.py --verify --figure fig-04
uv run python scripts/build_proposal_visuals.py --verify --figure fig-05
uv run python scripts/build_proposal_visuals.py --verify --figure fig-06
uv run python scripts/build_proposal_visuals.py --verify --figure fig-07
uv run python scripts/build_proposal_visuals.py --verify --figure fig-08
uv run python scripts/build_proposal_visuals.py --verify --figure fig-09
uv run python scripts/build_proposal_visuals.py --verify --figure fig-10
uv run python scripts/build_proposal_visuals.py --verify --figure fig-11
```

The source is `VEGO_AI_Doctoral_Proposal_Revised_20260825 (4).pdf`, 31 pages, SHA-256
`ADB663A4B8B0FFD3F09F2CEFEF43D690B5540FC36D4947FF60DCC624072846C9`.

`--clean` is deliberately narrow: it may remove only this package's `rendered/` and
`qa/generated/` children after resolved-path and child-name checks. It cannot delete the figures
directory, source files, content manifest, or review receipt.

## Visual language

| Role | Hex | Meaning |
| --- | --- | --- |
| Background | `#FFFFFF` | Document background |
| Ink | `#172033` | Text and neutral outlines |
| Existing baseline | `#17365D` | Committed/existing baseline element |
| Human judgment | `#A84A00` | Doctoral human-judgment layer |
| Conditional | `#5F6B7A` | Conditional, gated, or out-of-scope element |
| Neutral fill | `#F2F4F7` | Secondary panel or record fill |

The embedded Carlito family is used throughout. Every scene label is at least 7 pt at its native
artboard size; ordinary labels target 8 pt or larger. Rectangle = artifact/record; rounded rectangle = process/agent; diamond =
decision; cylinder = store; parallelogram = human input. Solid line = committed/existing, dashed =
conditional/proposed/gated, dotted = information reference. Labels, shapes, dash patterns, hatching,
and semantic role metadata make the meaning recoverable without colour alone.

The P2 ordinary-label calculation includes every `Text` role except the narrow, documented support
allowlist: `provenance`, `supporting-note`, and `boundary-note`. The default `label` role is ordinary;
it is never silently exempted. A scene containing no ordinary text fails that P2 calculation.

## QA evidence and boundaries

`qa/qa-receipt.json` is stable, path-safe machine evidence: source receipt, exact vector and raster
artifact SHA-256 values, tool/version records, and every check's `pass`, `fail`, or `unavailable`
status. The pipeline release gate requires both the 7 pt effective-text floor for every label and
the 8 pt effective floor for every ordinary label, as well as WCAG 2 contrast for palette and actual
text/fill pairs, SVG/PDF parse and vector structure, no image XObjects/external references, and
semantic non-colour redundancy. Its `FINAL_SIZE_FONT` receipt lists failed 7 pt and 8 pt ordinary
figure IDs and values separately.

The receipt also verifies both Carlito TTFs and the OFL license against the pinned font manifest,
records their path-safe identity/byte/SHA-256 receipts, and records path-safe byte/SHA-256 receipts
for the build script, lock/project definition, content and provenance manifests, shared visual
modules, and all eleven figure builders. SVG resources must be embedded Carlito data or internal
fragments; used PDF fonts must resolve to embedded font programs. Runtime evidence names CPython,
ReportLab, pypdf, Pillow, Poppler, and the `uv` build runtime without recording private paths.

Portrait A4 placement uses the declared insertion widths rather than a maximum-fit scale: Figures
1-7 and 9-10 use `4,716,000` EMU (371.34 pt); Figure 8 uses `4,104,000` EMU (323.15 pt); and
Figure 11 uses its standalone A4 width of 523 pt. The effective font check multiplies each native
font by that exact scale. The integration-size figures are dimensioned for those widths; the
current receipt must pass both the 7 pt hard floor and the 8 pt ordinary-label target at final size.
High-DPI evidence remains diagnostic and cannot override either numeric gate.

`qa/generated/` contains one-page A4 proof PDFs plus normal, greyscale, protanopia, and deuteranopia
PNG proofs at 144 and 576 DPI. The fixed colour-vision matrices are recorded in the QA receipt. Four
144-DPI contact sheets sit in `qa/generated/contact-sheets/`. PNGs are inspection evidence only;
they are not final figures.

`qa/visual-review.md` is a fail-closed human gate. The command writes a pending template on its first
run and returns failure until all eleven A4/400% proofs and the four contact sheets have been opened,
actual verdicts have been recorded, every required condition passes, and its status is set to `PASS`.
The committed review records the completed independent artifact inspection. Its `PASS` state is a
build-review gate, not Ali's scholarly or design approval; the integrated 31-page proposal is
rendered and inspected separately before the package may be marked ready for Ali review.

The review parser requires exactly one `<!-- visual-review-status: PASS -->` marker and exactly one
row for each figure with `PASS` in every required table cell. A second, contradictory, unknown, or
pending marker fails the gate. First creation parses the new template immediately, so a first run and
a clean rerun produce the same receipt instead of a one-off “template created” result.

The figures preserve source evidence boundaries: Figure 8 has no unreported uncertainty statistics;
Figure 9 is a conditional plan rather than a readiness result; and Figure 11 is standalone, not a
claim of proposal integration. No output establishes accuracy, generalisation, reduced effort,
transfer safety, clinical readiness, or completed validation.

## Pinned tools

The project uses Python 3.11, ReportLab 4.4.9, pypdf 6.15.0, Pillow 12.3.0, vendored Carlito TTFs,
and the bundled WinGet Poppler `pdftoppm`. The exact Poppler version used is captured in each QA
receipt. Run `uv sync --frozen --all-groups` from the repository root before rebuilding in a new
environment.

## Pinned proposal-document renderer

The copy-only DOCX integration uses Word only to insert and save the ten SVGs. PDF pagination and
release verification use the free, workspace-local LibreOffice 24.2.7.2 runtime bound by
`renderer-manifest.json`. The manifest records the official archive URLs, sizes, SHA-256 digests,
the complete executable engine contract, Caladea/Carlito font files, and the required
Calibri-to-Carlito and Cambria-to-Caladea substitutions. The engine contract hashes every
top-level file in `program/`, every file under `program/services/` and `share/registry/`, and all
eight files under `share/fonts/truetype/`. It intentionally excludes non-executable
localisation, help, gallery, and image resources.

Bootstrap or verify the ignored `.cache` runtime without installing LibreOffice system-wide:

```powershell
.\scripts\bootstrap_proposal_renderer.ps1
.\scripts\bootstrap_proposal_renderer.ps1 -VerifyOnly
```

`integrate_proposal_visuals.ps1` requires the tracked canonical manifest, validates the pinned
engine contract, creates an isolated temporary LibreOffice profile, and exports through
`writer_pdf_Export` in a hidden, bounded process. The PDF is first written to a unique staging
directory and then published without overwrite. Word pagination is a
baseline-aware sanity check: the integrated Word document must retain Word's own source baseline.
The post-verifier remains authoritative and requires the LibreOffice PDF to contain exactly 31
pages. The durable receipt records renderer and font hashes plus both pagination policies, without
recording runtime, profile, source, or user-directory paths.

The bootstrap's version probe and production PDF export are time-bounded and terminate their
process trees on timeout. The one-time MSI administrative extraction and Caladea `tar` extraction
are not yet time-bounded; this is a documented P2 bootstrap residual, not part of production
document export.

SVG text sizes are emitted as unitless viewBox coordinates. CSS `pt` units are forbidden inside
figure text because SVG consumers otherwise apply a 4/3 absolute-unit conversion and can overflow
the geometry even when the same Carlito metrics were used for layout.
