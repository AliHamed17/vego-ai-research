const slides = [
  {
    "title": "VEGO-AI Thesis Progress",
    "section": "Opening",
    "subtitle": "Supervisor session package for 2026-06-17",
    "claim": "VEGO-AI has moved from feature implementation to research evaluation.",
    "bullets": [
      "M1-M4B-1 are implemented and validated as a non-destructive research prototype.",
      "The contribution is reusable human judgment for AI-assisted model assessment.",
      "The next decision is EXP-002 expert labeling, not more feature work."
    ],
    "evidence": [
      "Main baseline: M4B-1 deterministic comparison",
      "Dashboard: 4 settings, 179 cases, 27 variability patterns",
      "Boundary: Agent 4 unchanged; M4B-2 not implemented"
    ],
    "kind": "title"
  },
  {
    "title": "Session Goal",
    "section": "Opening",
    "claim": "Use the meeting to align research claims, evidence, and next evaluation decisions.",
    "bullets": [
      "Show what was built and validated.",
      "Separate mechanism readiness from accuracy-improvement claims.",
      "Agree on EXP-002 expert labeling protocol and target size."
    ],
    "evidence": [
      "Output folder: artifacts/supervisor_demo_2026-06-17",
      "Open first: dashboard index.html",
      "Decision table: tables/supervisor_decisions.md"
    ]
  },
  {
    "title": "Motivation",
    "section": "Research Problem",
    "claim": "AI-assisted model assessment can flag variability, but it needs reusable expert judgment to support repeated analysis.",
    "bullets": [
      "Assessment outputs expose variation across student/domain models.",
      "Human review is expensive if every similar pattern is handled from scratch.",
      "The research opportunity is to reuse human judgment without replacing the original AI decision pipeline."
    ],
    "evidence": [
      "Terms to use: reusable human judgment, human-AI co-reasoning, non-destructive comparison"
    ]
  },
  {
    "title": "Original VEGO-AI",
    "section": "Baseline",
    "claim": "The original pipeline remains the baseline that all new research layers must preserve.",
    "bullets": [
      "Agent outputs assess domain models and classify variability patterns.",
      "The baseline produces the original AI classification evidence.",
      "The human-judgment layer is added around the baseline, not inside Agent 4 behavior."
    ],
    "evidence": [
      "Boundary statement: Agent 4 unchanged",
      "Baseline outputs not overwritten",
      "M4B-2 not implemented"
    ]
  },
  {
    "title": "Research Gap",
    "section": "Research Problem",
    "claim": "The gap is not human involvement in general; it is reusable, structurally captured judgment for future model assessment.",
    "bullets": [
      "Human-in/on-the-loop is known; the thesis focuses on the reusable judgment mechanism.",
      "Same-pattern reuse is useful for mechanism validation but not generalization proof.",
      "Held-out expert labels are still needed before accuracy claims."
    ],
    "evidence": [
      "Avoid saying: the AI is better now",
      "Say instead: the mechanism is ready for controlled evaluation"
    ]
  },
  {
    "title": "Contribution Statement",
    "section": "Contribution",
    "claim": "Human judgment is selectively triggered, structurally captured, and stored as reusable knowledge.",
    "bullets": [
      "M1 triggers human review where model assessment is uncertain or consequential.",
      "M2 captures decisions in a structured feedback schema.",
      "M3 stores reusable Human Judgment Memory.",
      "M4A/M4B-1 retrieve and compare memory without modifying the baseline."
    ],
    "evidence": [
      "Design-science artifact: problem -> gap -> artifact -> mechanisms -> evaluation path"
    ],
    "kind": "flow",
    "flow": [
      {
        "title": "M1",
        "body1": "Human Review",
        "body2": "Queue"
      },
      {
        "title": "M2",
        "body1": "Feedback",
        "body2": "Manager"
      },
      {
        "title": "M3",
        "body1": "Judgment",
        "body2": "Memory"
      },
      {
        "title": "M4A",
        "body1": "Memory",
        "body2": "Advice"
      },
      {
        "title": "M4B-1",
        "body1": "Deterministic",
        "body2": "Comparison"
      }
    ]
  },
  {
    "title": "Milestone Architecture",
    "section": "Contribution",
    "claim": "The architecture is staged, testable, and boundary-aware.",
    "bullets": [
      "Each milestone has a distinct research role.",
      "Schemas and output files make the mechanism inspectable.",
      "Later features are blocked until evaluation evidence exists."
    ],
    "evidence": [
      "M1 Human Review Queue: Detects cases where human judgment is needed",
      "M2 Human Feedback Manager: Captures human decisions structurally",
      "M3 Human Judgment Memory: Stores reusable judgment as knowledge",
      "M4A Memory Advisory Layer: Retrieves memory as advisory evidence",
      "M4B-1 Deterministic Comparison: Produces parallel memory-informed comparison"
    ],
    "kind": "table"
  },
  {
    "title": "M1 Human Review Queue",
    "section": "Mechanisms",
    "claim": "M1 converts model-assessment uncertainty into explicit review work.",
    "bullets": [
      "Creates review items from variability and guideline evidence.",
      "Preserves trigger reasons for auditability.",
      "Makes human judgment need visible instead of hidden in free text."
    ],
    "evidence": [
      "Dashboard review queue count: 11",
      "Output: human_review_queue.jsonl"
    ]
  },
  {
    "title": "M2 Human Feedback Manager",
    "section": "Mechanisms",
    "claim": "M2 turns expert decisions into structured evidence.",
    "bullets": [
      "Captures decision, rationale, reuse flag, and guideline context.",
      "Keeps feedback separate from baseline AI output.",
      "Creates the bridge from one-time review to reusable memory."
    ],
    "evidence": [
      "Resolved feedback count: 4",
      "Output: resolved feedback JSONL"
    ]
  },
  {
    "title": "M3 Human Judgment Memory",
    "section": "Mechanisms",
    "claim": "M3 is the reusable knowledge layer.",
    "bullets": [
      "Stores accepted human judgments as reusable memory entries.",
      "Keeps provenance and review signatures inspectable.",
      "Supports future retrieval without calling LLM/API."
    ],
    "evidence": [
      "Judgment memory count: 3",
      "No embeddings; no automatic guideline rewriting"
    ]
  },
  {
    "title": "M4A Memory Advisory Layer",
    "section": "Mechanisms",
    "claim": "M4A retrieves memory as advice while preserving the AI classification boundary.",
    "bullets": [
      "Advice is contextual evidence, not an automatic correction.",
      "Advice strength and leakage status are tracked.",
      "The advisory-only boundary is measurable."
    ],
    "evidence": [
      "Memory advice count: 8",
      "AI classification changed count: 0"
    ]
  },
  {
    "title": "M4B-1 Deterministic Comparison",
    "section": "Mechanisms",
    "claim": "M4B-1 produces a deterministic, non-destructive comparison for evaluation.",
    "bullets": [
      "Creates memory-informed comparison beside the original result.",
      "Does not call LLM/API and does not change Agent 4.",
      "Provides EXP-001 metrics for mechanism readiness."
    ],
    "evidence": [
      "Comparison rows: 27",
      "Changed cases: 0",
      "Requires human review after memory: 2"
    ]
  },
  {
    "title": "Non-Destructive Boundary",
    "section": "Governance",
    "claim": "The strongest research-control decision is that original VEGO-AI behavior stays untouched.",
    "bullets": [
      "Original classification remains the baseline.",
      "Memory-informed classification is a parallel research artifact.",
      "This prevents premature claims and protects reproducibility."
    ],
    "evidence": [
      "ai_classification_changed_count=0",
      "M4B-2 remains blocked",
      "Agent 4 behavior unchanged"
    ],
    "kind": "metrics"
  },
  {
    "title": "Dashboard And Visualizer",
    "section": "Evidence",
    "claim": "The project now has inspection surfaces for both quantitative summaries and manual model/result review.",
    "bullets": [
      "Dashboard summarizes settings, cases, patterns, review queues, feedback, memory, advice, and comparisons.",
      "Visualizer UX prevents model/result mismatch during manual analysis.",
      "Research panels remain read-only."
    ],
    "evidence": [
      "Dashboard: VEGO-AI/reports/results_dashboard/index.html",
      "4 settings; 179 cases; 27 patterns"
    ]
  },
  {
    "title": "Validation State",
    "section": "Evidence",
    "claim": "The implementation is engineering-ready for supervisor review, with research claims still constrained.",
    "bullets": [
      "Tests, compile checks, project health, research health, and dashboard health passed.",
      "Generated outputs were refreshed for the meeting.",
      "No new feature implementation was done for this package."
    ],
    "evidence": [
      "pytest: 93 passed",
      "compileall: passed",
      "project health: passed",
      "research health: passed",
      "dashboard health: passed",
      "boundary: ai_classification_changed_count=0; M4B-1 changed_count=0"
    ],
    "kind": "table"
  },
  {
    "title": "EXP-001 Result",
    "section": "Evaluation",
    "claim": "EXP-001 supports mechanism readiness, not accuracy improvement.",
    "bullets": [
      "There are 27 deterministic comparison rows.",
      "Existing expert labels are too small and leakage-heavy for generalization.",
      "Generalization-safe expert-labeled count is currently 0."
    ],
    "evidence": [
      "Mechanism agreement: original 66.7%, memory-informed 66.7%",
      "Generalization-safe labels: 0",
      "Conclusion: no accuracy-improvement claim allowed"
    ],
    "kind": "metrics"
  },
  {
    "title": "EXP-002 Labeling Package",
    "section": "Evaluation",
    "claim": "The next empirical step is expert labeling for held-out evaluation.",
    "bullets": [
      "A labeling sheet is ready with 27 rows.",
      "24 rows are generalization-safe candidates.",
      "The supervisor should approve labels, target size, and leakage policy."
    ],
    "evidence": [
      "Rows: 27",
      "Generalization-safe candidates: 24",
      "Minimum target: 20; preferred: 30-50"
    ],
    "kind": "metrics"
  },
  {
    "title": "Limitations",
    "section": "Research Control",
    "claim": "The thesis should be explicit about what has not yet been proven.",
    "bullets": [
      "Current evidence does not prove accuracy improvement.",
      "Same-pattern memory is leakage-aware mechanism validation only.",
      "Generalization still requires held-out expert labels across settings/domains."
    ],
    "evidence": [
      "Use phrase: held-out expert labels still needed",
      "Do not say: the AI is better now"
    ]
  },
  {
    "title": "Supervisor Decisions",
    "section": "Decision",
    "claim": "The meeting should produce concrete decisions for the evaluation phase.",
    "bullets": [
      "Approve the research framing and wording.",
      "Approve EXP-002 labeling protocol and target size.",
      "Confirm M4B-2 remains blocked until EXP-002 results exist."
    ],
    "evidence": [
      "D1: Evaluation framing",
      "D2: Expert label protocol",
      "D3: Labeling target",
      "D4: Leakage policy",
      "D5: Next implementation gate"
    ],
    "kind": "decision"
  },
  {
    "title": "Demo Order And Close",
    "section": "Appendix",
    "claim": "The demo should stay evidence-led and avoid live implementation risk.",
    "bullets": [
      "Open the dashboard first.",
      "Then show the slides and one-page brief.",
      "Then open EXP-001 and EXP-002 tables.",
      "Close with supervisor decisions."
    ],
    "evidence": [
      "Dashboard: VEGO-AI/reports/results_dashboard/index.html",
      "Slides: VEGO_AI_Thesis_Progress_Slides.md / .pptx",
      "Questions: SUPERVISOR_QUESTIONS.md"
    ],
    "kind": "appendix"
  }
];

const colors = {
  ink: "#0F172A",
  muted: "#475569",
  sub: "#64748B",
  bg: "#F8FAFC",
  panel: "#FFFFFF",
  line: "#CBD5E1",
  teal: "#0B7285",
  green: "#2F9E44",
  violet: "#5F3DC4",
  orange: "#C2410C",
};

function text(ctx, slide, textValue, x, y, w, h, opts = {}) {
  return ctx.addText(slide, {
    text: textValue,
    x,
    y,
    width: w,
    height: h,
    fontSize: opts.size ?? 24,
    color: opts.color ?? colors.ink,
    bold: opts.bold ?? false,
    typeface: opts.face ?? (opts.title ? ctx.fonts.title : ctx.fonts.body),
    insets: opts.insets ?? { left: 8, right: 8, top: 6, bottom: 6 },
    fill: opts.fill ?? "#00000000",
    line: opts.line ?? ctx.line("#00000000", 0),
    align: opts.align ?? "left",
    valign: opts.valign ?? "top",
  });
}

function box(ctx, slide, x, y, w, h, fill = colors.panel, stroke = colors.line) {
  return ctx.addShape(slide, { x, y, width: w, height: h, fill, line: ctx.line(stroke, 2) });
}

function bulletBlock(ctx, slide, items, x, y, w, h, size = 23) {
  text(ctx, slide, items.map((item) => `- ${item}`).join("\n"), x, y, w, h, { size, color: colors.ink, insets: { left: 12, right: 12, top: 8, bottom: 8 } });
}

function footer(ctx, slide, n) {
  text(ctx, slide, "VEGO-AI thesis progress | supervisor session | " + String(n).padStart(2, "0"), 56, 675, 840, 28, { size: 14, color: colors.sub });
}

function addHeader(ctx, slide, data, n) {
  ctx.addShape(slide, { x: 0, y: 0, width: 1280, height: 720, fill: colors.bg, line: ctx.line("#00000000", 0) });
  ctx.addShape(slide, { x: 0, y: 0, width: 1280, height: 12, fill: colors.teal, line: ctx.line("#00000000", 0) });
  text(ctx, slide, data.section.toUpperCase(), 56, 34, 460, 26, { size: 14, color: colors.teal, bold: true });
  text(ctx, slide, data.title, 52, 70, 780, 58, { size: 36, bold: true, title: true });
  footer(ctx, slide, n);
}

function renderTitle(presentation, ctx, data, n) {
  const slide = presentation.slides.add();
  ctx.addShape(slide, { x: 0, y: 0, width: 1280, height: 720, fill: "#0F172A", line: ctx.line("#0F172A", 0) });
  ctx.addShape(slide, { x: 0, y: 0, width: 16, height: 720, fill: colors.teal, line: ctx.line(colors.teal, 0) });
  text(ctx, slide, data.title, 76, 92, 900, 86, { size: 48, bold: true, title: true, color: "#FFFFFF" });
  text(ctx, slide, data.subtitle ?? "", 78, 182, 740, 38, { size: 24, color: "#D1E7EC" });
  bulletBlock(ctx, slide, data.bullets, 78, 276, 655, 220, 25);
  const cardX = 815;
  box(ctx, slide, cardX, 98, 360, 430, "#FFFFFF", "#FFFFFF");
  text(ctx, slide, "Evidence", cardX + 24, 126, 290, 34, { size: 23, bold: true, color: colors.teal });
  bulletBlock(ctx, slide, data.evidence, cardX + 22, 174, 310, 285, 20);
  text(ctx, slide, "Non-destructive comparison | M4B-2 blocked", 78, 638, 720, 28, { size: 18, color: "#D1E7EC" });
  text(ctx, slide, String(n).padStart(2, "0"), 1118, 626, 70, 44, { size: 24, bold: true, color: "#FFFFFF", align: "right" });
  return slide;
}

function renderFlow(presentation, ctx, data, n) {
  const slide = presentation.slides.add();
  addHeader(ctx, slide, data, n);
  text(ctx, slide, data.claim, 56, 136, 870, 58, { size: 25, color: colors.muted });
  const nodes = data.flow ?? [];
  const startX = 64;
  const y = 270;
  const w = 205;
  const gap = 28;
  nodes.forEach((node, index) => {
    const x = startX + index * (w + gap);
    box(ctx, slide, x, y, w, 132, "#FFFFFF", index % 2 ? colors.green : colors.teal);
    text(ctx, slide, node.title, x + 16, y + 18, w - 32, 28, { size: 22, bold: true, color: colors.ink });
    text(ctx, slide, [node.body1, node.body2].filter(Boolean).join("\n"), x + 16, y + 56, w - 32, 56, { size: 18, color: colors.muted });
    if (index < nodes.length - 1) {
      text(ctx, slide, ">", x + w + 2, y + 47, gap - 4, 34, { size: 26, bold: true, color: colors.sub, align: "center" });
    }
  });
  bulletBlock(ctx, slide, data.bullets, 70, 460, 540, 145, 21);
  bulletBlock(ctx, slide, data.evidence, 650, 460, 500, 145, 20);
  return slide;
}

function renderMetrics(presentation, ctx, data, n) {
  const slide = presentation.slides.add();
  addHeader(ctx, slide, data, n);
  text(ctx, slide, data.claim, 56, 136, 920, 56, { size: 25, color: colors.muted });
  const evidence = data.evidence.slice(0, 4);
  evidence.forEach((item, index) => {
    const x = 72 + index * 292;
    box(ctx, slide, x, 230, 250, 150, "#FFFFFF", [colors.teal, colors.green, colors.violet, colors.orange][index]);
    const parts = item.split(":");
    text(ctx, slide, parts[0], x + 18, 252, 212, 38, { size: 20, bold: true, color: colors.ink });
    text(ctx, slide, parts.slice(1).join(":").trim() || item, x + 18, 302, 212, 52, { size: 24, bold: true, color: colors.teal });
  });
  bulletBlock(ctx, slide, data.bullets, 76, 445, 840, 150, 22);
  return slide;
}

function renderTable(presentation, ctx, data, n) {
  const slide = presentation.slides.add();
  addHeader(ctx, slide, data, n);
  text(ctx, slide, data.claim, 56, 136, 900, 54, { size: 25, color: colors.muted });
  const rows = data.evidence.slice(0, 6);
  rows.forEach((row, index) => {
    const y = 220 + index * 54;
    box(ctx, slide, 70, y, 1060, 44, index % 2 ? "#F1F5F9" : "#FFFFFF", "#D8E2EA");
    const [left, ...rest] = row.split(":");
    text(ctx, slide, left, 88, y + 7, 285, 30, { size: 18, bold: true, color: colors.ink });
    text(ctx, slide, rest.join(":").trim(), 388, y + 7, 720, 30, { size: 18, color: colors.muted });
  });
  return slide;
}

function renderDefault(presentation, ctx, data, n) {
  const slide = presentation.slides.add();
  addHeader(ctx, slide, data, n);
  text(ctx, slide, data.claim, 56, 136, 850, 72, { size: 26, color: colors.muted });
  box(ctx, slide, 64, 240, 690, 330, "#FFFFFF", "#D8E2EA");
  text(ctx, slide, "Talking points", 88, 266, 260, 28, { size: 21, bold: true, color: colors.teal });
  bulletBlock(ctx, slide, data.bullets, 86, 306, 620, 230, 22);
  box(ctx, slide, 798, 240, 330, 330, "#FFFFFF", colors.teal);
  text(ctx, slide, "Evidence", 822, 266, 240, 28, { size: 21, bold: true, color: colors.teal });
  bulletBlock(ctx, slide, data.evidence, 820, 306, 275, 230, 19);
  return slide;
}

export async function renderSlide(presentation, ctx, index) {
  const data = slides[index];
  const n = index + 1;
  if (data.kind === "title") return renderTitle(presentation, ctx, data, n);
  if (data.kind === "flow") return renderFlow(presentation, ctx, data, n);
  if (data.kind === "metrics") return renderMetrics(presentation, ctx, data, n);
  if (data.kind === "table" || data.kind === "decision") return renderTable(presentation, ctx, data, n);
  return renderDefault(presentation, ctx, data, n);
}
