# Mermaid source — VEGO-AI proposal figures

Ready-to-render Mermaid diagram source, one figure per section. Paste directly into mermaid.live,
the VS Code Mermaid extension, or `mmdc` for SVG/PNG export.

## Figure 10 — Three-year work plan (Gantt)

Two things Mermaid's `gantt` chart genuinely cannot do, worth knowing before you render this:

1. **No dashed-border style per task.** The medical-extension bar was specced as a dashed amber
   lane. Mermaid gantt has exactly three built-in visual states — `done`, `active`, `crit` — each
   with a fixed colour, no dash option. The code below tags the medical bar `crit` and overrides its
   colour to amber via the `%%{init}%%` theme block, purely for visual distinction; it is not using
   `crit` in its usual "critical path" sense, so the task label itself says "(CONDITIONAL)" to keep
   the meaning unambiguous regardless of colour.
2. **No explicit dependency arrows between lanes.** Mermaid gantt sequences tasks with `after
   taskId`, which affects start dates correctly, but draws no connecting line. The Study 1 → Study 2
   → Study 3 → Integrated Evaluation dependency is therefore encoded in the *dates* below (each
   lane's work genuinely starts after the feeding lane's output), but if you need the arrows drawn
   on the page — the proposal's Chapter 5 prose explicitly argues from that dependency — use this
   Mermaid version as the fast draft to check dates and logic, then rebuild the final figure in the
   Lovable Figure Studio's custom SVG Gantt (already specced to draw both the dashed style and the
   dependency arrows) or in Eraser/draw.io for the version that actually goes in the document.

Also corrected here versus Table 11's current wording: Semester 1's literature-review task is
"execute" the query families, not "freeze the protocol" — the protocol is already frozen per the
project's own search register (see enhancement prompt v3, fix 4a). Use this corrected wording going
forward.

```text
%%{init: {'theme': 'base', 'themeVariables': {
  'critBkgColor': '#c98a2e',
  'critBorderColor': '#8a5f1e',
  'critTextColor': '#3a2a10'
}}}%%
gantt
    title Figure 10 — Three-year research work plan (Oct 2027 - Oct 2030)
    dateFormat YYYY-MM-DD
    axisFormat %b %Y

    section Preparatory (not one of the three years)
    Proposal, approval, candidacy      :prep, 2026-10-01, 2027-09-30

    section Literature Review
    Execute 5 query families + screen ACL corpus   :lit1, 2027-10-01, 2028-03-31

    section Study 1
    Freeze Study 1 protocol; baseline labels       :s1a, 2027-10-01, 2028-03-31
    Implement + evaluate; burden analysis          :s1b, after s1a, 2028-09-30

    section Study 2
    Freeze contract; conformance fixtures; recruit :s2a, after s1b, 2029-03-31
    Comparator study; analysis; source-store handoff :s2b, after s2a, 2029-09-30

    section Study 3
    Reliability + target-context evaluation        :s3a, after s2b, 2030-03-31

    section Medical extension (conditional, off critical path)
    Go/no-go decision                              :milestone, med0, 2029-09-30, 0d
    Medical work (CONDITIONAL - only if all 6 gates approved) :crit, med1, after med0, 2030-09-30

    section Integrated Evaluation
    Integrated evaluation; synthesis; defence prep :ie1, after s3a, 2030-09-30
    Thesis defence                                 :milestone, defence, 2030-10-01, 0d

    section Publications
    Paper 1 submission                             :milestone, p1, 2028-09-30, 0d
    Paper 2 submission                              :milestone, p2, 2029-09-30, 0d
    Paper 3 submission                              :milestone, p3, 2030-03-31, 0d
```

### Checks before you export

- Confirm the axis reads Oct 2026 on the left and Oct 2030 on the right — if your renderer clips the
  preparatory band, widen the chart width setting rather than trimming dates.
- The four milestone diamonds (Paper 1, Paper 2, Paper 3, Thesis defence) should render as small
  diamonds, not bars — this is automatic from the `milestone` keyword, but some older renderers need
  a `0d` duration explicitly, which is already included.
- The medical lane's amber colour depends on `theme: 'base'` being respected by your renderer;
  mermaid.live and the VS Code extension both honour it. If you render via a pipeline that ignores
  `%%{init}%%` (some static site generators strip it), the bar will fall back to Mermaid's default
  red "crit" colour — still visually distinct, just not amber.
- Double-check the Semester 1 label reads "Execute 5 query families" — not "freeze the protocol" —
  since the protocol is already frozen and Table 11's current wording needs the same fix (4a) applied
  here for consistency.
