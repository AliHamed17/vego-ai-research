# Eraser prompts — VEGO-AI proposal figures

Paste-ready natural-language prompts for Eraser (DiagramGPT). One figure per session — this file
grows as each one is described. Each entry gives the prompt exactly as typed into Eraser, plus a
short note on what to check in the generated result before exporting.

## Figure 1 — "Six readings of one observed model difference"

**Correction from the earlier Lovable prompt:** that prompt told Lovable to build this figure with
FOUR readings from the Shift Supervisor example. Checked directly against proposal §1.7: the
example actually gives SIX readings, verbatim. Four was wrong. This entry uses the correct six, and
the figure caption should read "Six readings", not "Four readings" — the earlier caption implied a
generic four-category framework, but grounding it in the real §1.7 example (which the reader meets
again nine pages later) is the stronger, truer choice, so keep the concrete example rather than
inventing an abstract placeholder with exactly four branches.

### Prompt for Eraser

```text
Create a diagram, general/flowchart type, landscape orientation, for an academic paper figure.

ONE central node at the left, styled as a plain rounded rectangle, containing this text exactly:
"Model Inspector reports: an added actor 'Shift Supervisor', not named in the domain text, mediating
two relations other submissions attach directly to the operator."

From that single node, draw six arrows fanning out to the right to six sibling nodes, arranged in a
vertical stack so all six are visible without crossing lines. Each sibling node is a rectangle
containing one of the following six labels, verbatim and in this order top to bottom:

1. "Defensible abstraction of an unnamed role"
2. "Modeling-language error (actor used where notation calls for a role/boundary element)"
3. "Domain misconception (who authorizes what)"
4. "Genuine ambiguity in the task description"
5. "Gap in the guideline (should admit this representation, does not)"
6. "Legitimate local/pedagogical decision by the instructor"

Style: minimal, no icons, no shadows, no gradients, no 3D effects. Use a single accent colour for
all six arrows and outline the six sibling nodes in that same colour, keep the central node in plain
black/grey so it reads as the shared, fixed starting point. Use a clean sans-serif font. Keep line
weight consistent across all six arrows -- do not vary thickness to imply importance, since the point
of the figure is that all six readings are equally live until someone judges between them.

Add a caption below the diagram: "Figure 1. Six readings of one observed model difference. The
artifact is identical in all six; only the interpretation differs. Concrete instance of the
motivating example developed in section 1.7."

Do not add any additional nodes, decision diamonds, or a "resolution" arrow -- the figure's entire
point is that nothing in the artifact itself picks among the six, so it must end at six open
siblings, not converge back to one answer.
```

### What to check in the generated result

- Exactly six sibling nodes, no more, no fewer, and no seventh "resolution" node added by the AI.
- No arrow points back toward the central node or between siblings — this is a pure one-to-six fan,
  not a decision tree with elimination.
- All six labels match the wording above; Eraser's generator sometimes shortens long labels — if it
  truncates any of the six, edit the node text directly rather than accepting a paraphrase, since
  these are near-verbatim quotes from the proposal text.
- Export as SVG once it looks right, not PNG — the figure needs to scale cleanly in the final
  document.
