#!/usr/bin/env node

import fs from "node:fs/promises";
import path from "node:path";

const root = process.cwd();
const outDir = path.join(root, "artifacts", "supervisor_demo_2026-06-17");
const figuresDir = path.join(outDir, "figures");
const tablesDir = path.join(outDir, "tables");
const workspace = path.join(root, "outputs", "manual-20260616-supervisor", "presentations", "vego-ai-supervisor");
const slidesDir = path.join(workspace, "slides");

const paths = {
  dashboard: path.join(root, "VEGO-AI", "reports", "results_dashboard", "index.html"),
  dashboardMetrics: path.join(root, "VEGO-AI", "reports", "results_dashboard", "metrics_snapshot.json"),
  exp001Summary: path.join(root, "reports", "generated", "exp001", "exp001_summary.json"),
  exp001Csv: path.join(root, "reports", "generated", "exp001", "exp001_evaluation_dataset.csv"),
  exp001Table: path.join(root, "reports", "generated", "exp001", "exp001_evaluation_table.md"),
  exp002Summary: path.join(root, "reports", "generated", "exp002", "exp002_summary.json"),
  exp002Csv: path.join(root, "reports", "generated", "exp002", "expert_labeling_sheet.csv"),
  exp002Sheet: path.join(root, "reports", "generated", "exp002", "expert_labeling_sheet.md"),
  exp002Recommended: path.join(root, "reports", "generated", "exp002", "recommended_patterns_to_label.md"),
};

function repoRel(filePath) {
  return path.relative(root, filePath).replaceAll(path.sep, "/");
}

async function readJson(filePath) {
  return JSON.parse(await fs.readFile(filePath, "utf8"));
}

function escXml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");
}

function escCsv(value) {
  const text = value == null ? "" : String(value);
  if (/[",\r\n]/.test(text)) {
    return `"${text.replaceAll('"', '""')}"`;
  }
  return text;
}

function mdTable(headers, rows) {
  const header = `| ${headers.join(" | ")} |`;
  const sep = `| ${headers.map(() => "---").join(" | ")} |`;
  const body = rows.map((row) => `| ${row.map((cell) => String(cell ?? "").replaceAll("\n", "<br>")).join(" | ")} |`);
  return [header, sep, ...body].join("\n");
}

function csv(headers, rows) {
  return [
    headers.map(escCsv).join(","),
    ...rows.map((row) => row.map(escCsv).join(",")),
  ].join("\n") + "\n";
}

function distToText(dist = []) {
  return dist.map((item) => `${item.value}: ${item.count}`).join(", ");
}

function pct(value) {
  if (value == null) return "not evaluable";
  return `${Math.round(value * 1000) / 10}%`;
}

function cardText(lines) {
  return lines.map((line, index) => `<text x="0" y="${index * 30}" class="${index === 0 ? "cardTitle" : "cardBody"}">${escXml(line)}</text>`).join("\n");
}

function writeCardSvg({ title, subtitle, cards, footer, width = 1600, height = 900 }) {
  const cols = Math.min(cards.length, 4);
  const rows = Math.ceil(cards.length / cols);
  const marginX = 90;
  const top = 190;
  const gap = 28;
  const cardW = (width - marginX * 2 - gap * (cols - 1)) / cols;
  const cardH = Math.min(190, (height - top - 130 - gap * (rows - 1)) / rows);
  const palette = ["#0B7285", "#2F9E44", "#5F3DC4", "#C2410C", "#0F766E", "#7C2D12", "#1D4ED8", "#4D7C0F"];
  const body = cards.map((card, index) => {
    const col = index % cols;
    const row = Math.floor(index / cols);
    const x = marginX + col * (cardW + gap);
    const y = top + row * (cardH + gap);
    const accent = palette[index % palette.length];
    const lines = Array.isArray(card.lines) ? card.lines : [card.title, card.body].filter(Boolean);
    return `
      <g transform="translate(${x}, ${y})">
        <rect width="${cardW}" height="${cardH}" rx="14" fill="#FFFFFF" stroke="#CBD5E1" stroke-width="2"/>
        <rect width="${cardW}" height="10" rx="5" fill="${accent}"/>
        <g transform="translate(26, 48)">${cardText(lines)}</g>
      </g>`;
  }).join("\n");

  return `<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="${width}" height="${height}" viewBox="0 0 ${width} ${height}">
  <style>
    .bg { fill: #F8FAFC; }
    .title { font: 700 48px Arial, sans-serif; fill: #0F172A; }
    .subtitle { font: 400 25px Arial, sans-serif; fill: #475569; }
    .cardTitle { font: 700 26px Arial, sans-serif; fill: #0F172A; }
    .cardBody { font: 400 22px Arial, sans-serif; fill: #334155; }
    .footer { font: 400 22px Arial, sans-serif; fill: #64748B; }
  </style>
  <rect class="bg" width="${width}" height="${height}"/>
  <text x="90" y="88" class="title">${escXml(title)}</text>
  <text x="90" y="132" class="subtitle">${escXml(subtitle)}</text>
  ${body}
  <text x="90" y="${height - 58}" class="footer">${escXml(footer)}</text>
</svg>`;
}

function writeFlowSvg({ title, subtitle, nodes, footer, width = 1600, height = 900 }) {
  const marginX = 80;
  const y = 345;
  const nodeW = 210;
  const nodeH = 150;
  const gap = (width - marginX * 2 - nodeW * nodes.length) / Math.max(nodes.length - 1, 1);
  const palette = ["#0B7285", "#2F9E44", "#5F3DC4", "#C2410C", "#0F766E", "#1D4ED8"];
  const body = nodes.map((node, index) => {
    const x = marginX + index * (nodeW + gap);
    const nextX = x + nodeW + gap;
    const arrow = index < nodes.length - 1 ? `<path d="M ${x + nodeW + 12} ${y + nodeH / 2} L ${nextX - 20} ${y + nodeH / 2}" stroke="#64748B" stroke-width="5" fill="none"/><path d="M ${nextX - 20} ${y + nodeH / 2} l -18 -12 v 24 z" fill="#64748B"/>` : "";
    return `
      <g>
        ${arrow}
        <rect x="${x}" y="${y}" width="${nodeW}" height="${nodeH}" rx="16" fill="#FFFFFF" stroke="${palette[index % palette.length]}" stroke-width="4"/>
        <text x="${x + 22}" y="${y + 48}" class="nodeTitle">${escXml(node.title)}</text>
        <text x="${x + 22}" y="${y + 86}" class="nodeBody">${escXml(node.body1 ?? "")}</text>
        <text x="${x + 22}" y="${y + 116}" class="nodeBody">${escXml(node.body2 ?? "")}</text>
      </g>`;
  }).join("\n");

  return `<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="${width}" height="${height}" viewBox="0 0 ${width} ${height}">
  <style>
    .bg { fill: #F8FAFC; }
    .title { font: 700 48px Arial, sans-serif; fill: #0F172A; }
    .subtitle { font: 400 25px Arial, sans-serif; fill: #475569; }
    .nodeTitle { font: 700 25px Arial, sans-serif; fill: #0F172A; }
    .nodeBody { font: 400 21px Arial, sans-serif; fill: #334155; }
    .footer { font: 400 22px Arial, sans-serif; fill: #64748B; }
  </style>
  <rect class="bg" width="${width}" height="${height}"/>
  <text x="80" y="88" class="title">${escXml(title)}</text>
  <text x="80" y="132" class="subtitle">${escXml(subtitle)}</text>
  ${body}
  <text x="80" y="${height - 58}" class="footer">${escXml(footer)}</text>
</svg>`;
}

async function writeFile(rel, content) {
  const target = path.join(outDir, rel);
  await fs.mkdir(path.dirname(target), { recursive: true });
  await fs.writeFile(target, content.endsWith("\n") ? content : `${content}\n`, "utf8");
}

async function copyIfExists(source, relTarget) {
  try {
    await fs.mkdir(path.dirname(path.join(outDir, relTarget)), { recursive: true });
    await fs.copyFile(source, path.join(outDir, relTarget));
  } catch {
    // Optional source files are omitted if not generated in this workspace.
  }
}

function mmdFlow(nodes, title) {
  const nodeLines = nodes.map((n, i) => `  N${i}["${n.title}<br/>${n.body1 ?? ""} ${n.body2 ?? ""}"]`).join("\n");
  const edgeLines = nodes.slice(1).map((_, i) => `  N${i} --> N${i + 1}`).join("\n");
  return `---\ntitle: ${title}\n---\nflowchart LR\n${nodeLines}\n${edgeLines}\n`;
}

async function main() {
  await fs.mkdir(figuresDir, { recursive: true });
  await fs.mkdir(tablesDir, { recursive: true });
  await fs.mkdir(slidesDir, { recursive: true });

  const dashboard = await readJson(paths.dashboardMetrics);
  const exp001 = await readJson(paths.exp001Summary);
  const exp002 = await readJson(paths.exp002Summary);
  const overview = dashboard.overview;

  const generatedAt = "2026-06-16";
  const meetingDate = "2026-06-17";

  const milestones = [
    ["Original VEGO-AI", "Baseline AI-assisted model assessment", "Preserved baseline output and Agent 4 behavior"],
    ["M1 Human Review Queue", "Detects cases where human judgment is needed", `${overview.human_review_queue_count} review queue items in dashboard snapshot`],
    ["M2 Human Feedback Manager", "Captures human decisions structurally", `${overview.resolved_feedback_count} resolved feedback entries available`],
    ["M3 Human Judgment Memory", "Stores reusable judgment as knowledge", `${overview.judgment_memory_count} reusable memory entries available`],
    ["M4A Memory Advisory Layer", "Retrieves memory as advisory evidence", `${overview.memory_advice_count} advice records; advisory-only boundary preserved`],
    ["M4B-1 Deterministic Comparison", "Produces parallel memory-informed comparison", `${exp001.totals.comparison_count} comparisons; changed baseline classifications: ${exp001.totals.changed_count}`],
    ["Dashboard", "Makes evidence inspectable", `${overview.settings_count} settings, ${overview.case_count} cases, ${overview.variability_pattern_count} patterns`],
    ["Visualizer UX", "Prevents model/result mismatch during manual inspection", "Read-only research panels and mismatch detection"],
  ];

  const validationRows = [
    ["pytest", "python -m pytest VEGO-AI\\tests -q", "93 passed"],
    ["compileall", "python -m compileall -q VEGO-AI\\framework VEGO-AI\\eval VEGO-AI\\analysis VEGO-AI\\vego_visualizer_delivery", "passed"],
    ["project health", ".\\scripts\\project-health.ps1", "passed"],
    ["research health", ".\\scripts\\research-health.ps1", "passed"],
    ["dashboard health", ".\\scripts\\dashboard-health.ps1 -RequireOutbox", "passed"],
    ["boundary", "Dashboard and EXP-001 checks", `ai_classification_changed_count=${overview.ai_classification_changed_count}; M4B-1 changed_count=${exp001.totals.changed_count}`],
  ];

  const exp001Rows = [
    ["Comparison rows", exp001.totals.comparison_count, "Mechanism coverage across four settings"],
    ["Existing expert labels", exp001.totals.expert_labeled_count, "Mechanism validation only"],
    ["Generalization-safe expert labels", exp001.totals.generalization_safe_expert_labeled_count, "Not evaluable yet"],
    ["Memory-informed changed cases", exp001.totals.changed_count, "Baseline preserved; deterministic comparison did not override"],
    ["Requires review after memory", exp001.totals.requires_human_review_after_memory_count, "Useful uncertainty signal"],
    ["Advice strength distribution", distToText(exp001.distributions.advice_strength), "Evidence of retrieval coverage"],
    ["Leakage distribution", distToText(exp001.distributions.evaluation_leakage_status), "Same-pattern labels excluded from generalization claims"],
    ["Mechanism agreement", `${pct(exp001.agreement.mechanism_validation.original_expert_agreement_rate)} original; ${pct(exp001.agreement.mechanism_validation.memory_informed_expert_agreement_rate)} memory-informed`, "Do not claim accuracy improvement"],
  ];

  const exp002Rows = [
    ["Rows prepared for supervisor labeling", exp002.totals.row_count, "Use as the meeting action item"],
    ["Existing labels", exp002.totals.existing_expert_label_count, "Seed labels only"],
    ["Generalization-safe candidates", exp002.totals.generalization_safe_candidate_count, "Main next evidence source"],
    ["Recommended rows", exp002.totals.recommended_count, "All rows are useful for initial labeling"],
    ["Minimum target", exp002.label_protocol.minimum_target, "Minimum for first quantitative comparison"],
    ["Preferred target", exp002.label_protocol.preferred_target, "Better for thesis evaluation"],
    ["Allowed labels", exp002.label_protocol.allowed_labels.join("; "), "Keep label protocol simple and auditable"],
  ];

  const decisionRows = [
    ["D1", "Evaluation framing", "Approve mechanism readiness wording and block accuracy-improvement claims until held-out labels exist"],
    ["D2", "Expert label protocol", "Approve labels: Substantial Variability, Occasional Variability, Undetermined / Needs Review"],
    ["D3", "Labeling target", "Choose minimum 20 rows or preferred 30-50 rows for EXP-002"],
    ["D4", "Leakage policy", "Confirm same-pattern memory is leakage-aware mechanism validation, not generalization evidence"],
    ["D5", "Next implementation gate", "Keep M4B-2 blocked until EXP-002 results are reviewed"],
  ];

  await writeFile("tables/milestones_contributions.md", `# Milestones And Contributions\n\n${mdTable(["Layer", "Research role", "Evidence"], milestones)}\n`);
  await writeFile("tables/milestones_contributions.csv", csv(["Layer", "Research role", "Evidence"], milestones));
  await writeFile("tables/validation_summary.md", `# Validation Summary\n\n${mdTable(["Check", "Command or evidence", "Status"], validationRows)}\n`);
  await writeFile("tables/validation_summary.csv", csv(["Check", "Command or evidence", "Status"], validationRows));
  await writeFile("tables/exp001_summary.md", `# EXP-001 Summary\n\n${mdTable(["Metric", "Value", "Interpretation"], exp001Rows)}\n`);
  await writeFile("tables/exp001_summary.csv", csv(["Metric", "Value", "Interpretation"], exp001Rows));
  await writeFile("tables/exp002_labeling_plan.md", `# EXP-002 Labeling Plan\n\n${mdTable(["Item", "Value", "Use"], exp002Rows)}\n`);
  await writeFile("tables/exp002_labeling_plan.csv", csv(["Item", "Value", "Use"], exp002Rows));
  await writeFile("tables/supervisor_decisions.md", `# Supervisor Decisions\n\n${mdTable(["ID", "Decision needed", "Recommended decision"], decisionRows)}\n`);
  await writeFile("tables/supervisor_decisions.csv", csv(["ID", "Decision needed", "Recommended decision"], decisionRows));
  await copyIfExists(paths.exp001Csv, "tables/source_exp001_evaluation_dataset.csv");
  await copyIfExists(paths.exp001Table, "tables/source_exp001_evaluation_table.md");
  await copyIfExists(paths.exp002Csv, "tables/source_exp002_expert_labeling_sheet.csv");
  await copyIfExists(paths.exp002Sheet, "tables/source_exp002_expert_labeling_sheet.md");
  await copyIfExists(paths.exp002Recommended, "tables/source_exp002_recommended_patterns_to_label.md");

  const fig1Nodes = [
    { title: "AI review", body1: "detects where", body2: "judgment is needed" },
    { title: "Human feedback", body1: "captured as", body2: "structured evidence" },
    { title: "Memory", body1: "stored as", body2: "reusable knowledge" },
    { title: "Advice", body1: "retrieved as", body2: "context" },
    { title: "Comparison", body1: "parallel and", body2: "non-destructive" },
  ];
  const fig2Nodes = [
    { title: "M1", body1: "Human Review", body2: "Queue" },
    { title: "M2", body1: "Feedback", body2: "Manager" },
    { title: "M3", body1: "Judgment", body2: "Memory" },
    { title: "M4A", body1: "Memory", body2: "Advice" },
    { title: "M4B-1", body1: "Deterministic", body2: "Comparison" },
  ];
  const figures = [
    ["01_research_spine", writeFlowSvg({ title: "Research Spine", subtitle: "Reusable human judgment in AI-assisted model assessment", nodes: fig1Nodes, footer: "Claim: human judgment can be selectively triggered, structurally captured, and reused as advisory evidence." }), mmdFlow(fig1Nodes, "Research Spine")],
    ["02_milestone_architecture", writeFlowSvg({ title: "Milestone Architecture", subtitle: "Staged implementation with explicit boundaries", nodes: fig2Nodes, footer: "M4B-2, Agent 4 reclassification, embeddings, and LLM calls remain out of scope." }), mmdFlow(fig2Nodes, "Milestone Architecture")],
    ["03_non_destructive_boundary", writeCardSvg({ title: "Non-Destructive Comparison Boundary", subtitle: "The memory-informed layer does not overwrite the original AI pipeline", footer: "ai_classification_changed_count=0; M4B-1 changed_count=0 in current evidence run.", cards: [
      { lines: ["Original Agent 4", "unchanged baseline classification"] },
      { lines: ["Memory advice", "advisory evidence only"] },
      { lines: ["M4B-1 output", "parallel comparison file"] },
      { lines: ["Research claim", "clarifies, does not automatically correct"] },
    ] }), "flowchart LR\n  A[Original Agent 4] --> B[Baseline output preserved]\n  C[Human Judgment Memory] --> D[Memory advice]\n  D --> E[M4B-1 comparison]\n  B --> E\n  E --> F[Parallel evidence only]\n"],
    ["04_artifact_chain", writeFlowSvg({ title: "Artifact Chain", subtitle: "Evidence files created by the human-judgment layer", nodes: [
      { title: "review_queue", body1: "M1", body2: "triggered review" },
      { title: "feedback", body1: "M2", body2: "human decision" },
      { title: "memory", body1: "M3", body2: "reusable entry" },
      { title: "advice", body1: "M4A", body2: "retrieved context" },
      { title: "comparison", body1: "M4B-1", body2: "parallel result" },
    ], footer: "Every stage is inspectable as JSON/JSONL and summarized by the dashboard." }), "flowchart LR\n  Q[human_review_queue.jsonl] --> F[human_feedback.jsonl]\n  F --> M[human_judgment_memory.jsonl]\n  M --> A[memory_advice.json]\n  A --> C[memory_informed_comparison.json]\n"],
    ["05_dashboard_snapshot", writeCardSvg({ title: "Dashboard Evidence Snapshot", subtitle: "Current dashboard generated from local project outputs", footer: `Dashboard path: ${repoRel(paths.dashboard)}`, cards: [
      { lines: [`${overview.settings_count} settings`, "CD/UCD x Cheers/Parking"] },
      { lines: [`${overview.case_count} cases`, "assessment coverage"] },
      { lines: [`${overview.variability_pattern_count} patterns`, "Agent D variability evidence"] },
      { lines: [`${overview.human_review_queue_count} review items`, "human judgment triggers"] },
      { lines: [`${overview.judgment_memory_count} memory entries`, "reusable knowledge"] },
      { lines: [`${overview.memory_advice_count} advice records`, "advisory retrieval"] },
      { lines: [`${overview.ai_classification_changed_count} baseline changes`, "non-destructive boundary"] },
      { lines: [`${overview.average_score_mean}`, "average score mean"] },
    ] }), "flowchart TB\n  D[Dashboard] --> S[4 settings]\n  D --> C[179 cases]\n  D --> P[27 variability patterns]\n  D --> H[Human review and memory panels]\n"],
    ["06_validation_gate", writeCardSvg({ title: "Validation Gate", subtitle: "Engineering readiness before the supervisor meeting", footer: "No new model behavior was implemented for this package.", cards: [
      { lines: ["pytest", "93 passed"] },
      { lines: ["compileall", "framework/eval/analysis/visualizer passed"] },
      { lines: ["project-health", "passed"] },
      { lines: ["research-health", "passed"] },
      { lines: ["dashboard-health", "passed with outbox"] },
      { lines: ["baseline", "outputs unchanged"] },
    ] }), "flowchart LR\n  T[pytest] --> C[compileall]\n  C --> P[project-health]\n  P --> R[research-health]\n  R --> D[dashboard-health]\n  D --> B[baseline preserved]\n"],
    ["07_exp001_findings", writeCardSvg({ title: "EXP-001 Findings", subtitle: "Evaluate M4B-1 deterministic comparison without overclaiming", footer: "Conclusion: mechanism readiness only; held-out expert labels still needed.", cards: [
      { lines: [`${exp001.totals.comparison_count} comparisons`, "four settings"] },
      { lines: [`${exp001.totals.expert_labeled_count} labels`, "mechanism validation"] },
      { lines: [`${exp001.totals.generalization_safe_expert_labeled_count} held-out labels`, "not evaluable"] },
      { lines: [`${exp001.totals.changed_count} changed outputs`, "non-destructive result"] },
      { lines: [`${exp001.totals.requires_human_review_after_memory_count} still need review`, "uncertainty retained"] },
      { lines: ["same-pattern memory", "leakage-aware only"] },
    ] }), "flowchart LR\n  E[EXP-001] --> M[Mechanism validation]\n  E --> G[Generalization-safe labels: 0]\n  M --> N[No accuracy claim]\n"],
    ["08_exp002_workflow", writeFlowSvg({ title: "EXP-002 Supervisor Workflow", subtitle: "The next research step is expert labeling, not new features", nodes: [
      { title: "Select rows", body1: `${exp002.totals.row_count} prepared`, body2: "patterns" },
      { title: "Apply labels", body1: "Substantial /", body2: "Occasional / Review" },
      { title: "Exclude leakage", body1: "hold out", body2: "same-pattern cases" },
      { title: "Compare", body1: "original vs", body2: "memory-informed" },
      { title: "Decide", body1: "M4B-2 gate", body2: "after results" },
    ], footer: `Recommended next labeling target: minimum ${exp002.label_protocol.minimum_target}; preferred ${exp002.label_protocol.preferred_target}.` }), "flowchart LR\n  A[Prepared labeling sheet] --> B[Supervisor labels]\n  B --> C[Generalization-safe subset]\n  C --> D[Agreement metrics]\n  D --> E[Decision on M4B-2]\n"],
  ];

  for (const [name, svg, mmd] of figures) {
    await writeFile(`figures/${name}.svg`, svg);
    await writeFile(`figures/${name}.mmd`, mmd);
  }
  await writeFile("figures/FIGURE_INDEX.md", `# Figure Index\n\n${mdTable(["Figure", "Use in talk"], figures.map(([name]) => [name, `See figures/${name}.svg and figures/${name}.mmd`]))}\n`);

  const slideSpine = [
    { title: "VEGO-AI Thesis Progress", section: "Opening", subtitle: `Supervisor session package for ${meetingDate}`, claim: "VEGO-AI has moved from feature implementation to research evaluation.", bullets: ["M1-M4B-1 are implemented and validated as a non-destructive research prototype.", "The contribution is reusable human judgment for AI-assisted model assessment.", "The next decision is EXP-002 expert labeling, not more feature work."], evidence: ["Main baseline: M4B-1 deterministic comparison", "Dashboard: 4 settings, 179 cases, 27 variability patterns", "Boundary: Agent 4 unchanged; M4B-2 not implemented"], kind: "title" },
    { title: "Session Goal", section: "Opening", claim: "Use the meeting to align research claims, evidence, and next evaluation decisions.", bullets: ["Show what was built and validated.", "Separate mechanism readiness from accuracy-improvement claims.", "Agree on EXP-002 expert labeling protocol and target size."], evidence: ["Output folder: artifacts/supervisor_demo_2026-06-17", "Open first: dashboard index.html", "Decision table: tables/supervisor_decisions.md"] },
    { title: "Motivation", section: "Research Problem", claim: "AI-assisted model assessment can flag variability, but it needs reusable expert judgment to support repeated analysis.", bullets: ["Assessment outputs expose variation across student/domain models.", "Human review is expensive if every similar pattern is handled from scratch.", "The research opportunity is to reuse human judgment without replacing the original AI decision pipeline."], evidence: ["Terms to use: reusable human judgment, human-AI co-reasoning, non-destructive comparison"] },
    { title: "Original VEGO-AI", section: "Baseline", claim: "The original pipeline remains the baseline that all new research layers must preserve.", bullets: ["Agent outputs assess domain models and classify variability patterns.", "The baseline produces the original AI classification evidence.", "The human-judgment layer is added around the baseline, not inside Agent 4 behavior."], evidence: ["Boundary statement: Agent 4 unchanged", "Baseline outputs not overwritten", "M4B-2 not implemented"] },
    { title: "Research Gap", section: "Research Problem", claim: "The gap is not human involvement in general; it is reusable, structurally captured judgment for future model assessment.", bullets: ["Human-in/on-the-loop is known; the thesis focuses on the reusable judgment mechanism.", "Same-pattern reuse is useful for mechanism validation but not generalization proof.", "Held-out expert labels are still needed before accuracy claims."], evidence: ["Avoid saying: the AI is better now", "Say instead: the mechanism is ready for controlled evaluation"] },
    { title: "Contribution Statement", section: "Contribution", claim: "Human judgment is selectively triggered, structurally captured, and stored as reusable knowledge.", bullets: ["M1 triggers human review where model assessment is uncertain or consequential.", "M2 captures decisions in a structured feedback schema.", "M3 stores reusable Human Judgment Memory.", "M4A/M4B-1 retrieve and compare memory without modifying the baseline."], evidence: ["Design-science artifact: problem -> gap -> artifact -> mechanisms -> evaluation path"], kind: "flow", flow: fig2Nodes },
    { title: "Milestone Architecture", section: "Contribution", claim: "The architecture is staged, testable, and boundary-aware.", bullets: ["Each milestone has a distinct research role.", "Schemas and output files make the mechanism inspectable.", "Later features are blocked until evaluation evidence exists."], evidence: milestones.slice(1, 6).map((row) => `${row[0]}: ${row[1]}`), kind: "table" },
    { title: "M1 Human Review Queue", section: "Mechanisms", claim: "M1 converts model-assessment uncertainty into explicit review work.", bullets: ["Creates review items from variability and guideline evidence.", "Preserves trigger reasons for auditability.", "Makes human judgment need visible instead of hidden in free text."], evidence: [`Dashboard review queue count: ${overview.human_review_queue_count}`, "Output: human_review_queue.jsonl"] },
    { title: "M2 Human Feedback Manager", section: "Mechanisms", claim: "M2 turns expert decisions into structured evidence.", bullets: ["Captures decision, rationale, reuse flag, and guideline context.", "Keeps feedback separate from baseline AI output.", "Creates the bridge from one-time review to reusable memory."], evidence: [`Resolved feedback count: ${overview.resolved_feedback_count}`, "Output: resolved feedback JSONL"] },
    { title: "M3 Human Judgment Memory", section: "Mechanisms", claim: "M3 is the reusable knowledge layer.", bullets: ["Stores accepted human judgments as reusable memory entries.", "Keeps provenance and review signatures inspectable.", "Supports future retrieval without calling LLM/API."], evidence: [`Judgment memory count: ${overview.judgment_memory_count}`, "No embeddings; no automatic guideline rewriting"] },
    { title: "M4A Memory Advisory Layer", section: "Mechanisms", claim: "M4A retrieves memory as advice while preserving the AI classification boundary.", bullets: ["Advice is contextual evidence, not an automatic correction.", "Advice strength and leakage status are tracked.", "The advisory-only boundary is measurable."], evidence: [`Memory advice count: ${overview.memory_advice_count}`, `AI classification changed count: ${overview.ai_classification_changed_count}`] },
    { title: "M4B-1 Deterministic Comparison", section: "Mechanisms", claim: "M4B-1 produces a deterministic, non-destructive comparison for evaluation.", bullets: ["Creates memory-informed comparison beside the original result.", "Does not call LLM/API and does not change Agent 4.", "Provides EXP-001 metrics for mechanism readiness."], evidence: [`Comparison rows: ${exp001.totals.comparison_count}`, `Changed cases: ${exp001.totals.changed_count}`, `Requires human review after memory: ${exp001.totals.requires_human_review_after_memory_count}`] },
    { title: "Non-Destructive Boundary", section: "Governance", claim: "The strongest research-control decision is that original VEGO-AI behavior stays untouched.", bullets: ["Original classification remains the baseline.", "Memory-informed classification is a parallel research artifact.", "This prevents premature claims and protects reproducibility."], evidence: [`ai_classification_changed_count=${overview.ai_classification_changed_count}`, "M4B-2 remains blocked", "Agent 4 behavior unchanged"], kind: "metrics" },
    { title: "Dashboard And Visualizer", section: "Evidence", claim: "The project now has inspection surfaces for both quantitative summaries and manual model/result review.", bullets: ["Dashboard summarizes settings, cases, patterns, review queues, feedback, memory, advice, and comparisons.", "Visualizer UX prevents model/result mismatch during manual analysis.", "Research panels remain read-only."], evidence: [`Dashboard: ${repoRel(paths.dashboard)}`, `${overview.settings_count} settings; ${overview.case_count} cases; ${overview.variability_pattern_count} patterns`] },
    { title: "Validation State", section: "Evidence", claim: "The implementation is engineering-ready for supervisor review, with research claims still constrained.", bullets: ["Tests, compile checks, project health, research health, and dashboard health passed.", "Generated outputs were refreshed for the meeting.", "No new feature implementation was done for this package."], evidence: validationRows.map((row) => `${row[0]}: ${row[2]}`), kind: "table" },
    { title: "EXP-001 Result", section: "Evaluation", claim: "EXP-001 supports mechanism readiness, not accuracy improvement.", bullets: ["There are 27 deterministic comparison rows.", "Existing expert labels are too small and leakage-heavy for generalization.", "Generalization-safe expert-labeled count is currently 0."], evidence: [`Mechanism agreement: original ${pct(exp001.agreement.mechanism_validation.original_expert_agreement_rate)}, memory-informed ${pct(exp001.agreement.mechanism_validation.memory_informed_expert_agreement_rate)}`, `Generalization-safe labels: ${exp001.totals.generalization_safe_expert_labeled_count}`, "Conclusion: no accuracy-improvement claim allowed"], kind: "metrics" },
    { title: "EXP-002 Labeling Package", section: "Evaluation", claim: "The next empirical step is expert labeling for held-out evaluation.", bullets: ["A labeling sheet is ready with 27 rows.", "24 rows are generalization-safe candidates.", "The supervisor should approve labels, target size, and leakage policy."], evidence: [`Rows: ${exp002.totals.row_count}`, `Generalization-safe candidates: ${exp002.totals.generalization_safe_candidate_count}`, `Minimum target: ${exp002.label_protocol.minimum_target}; preferred: ${exp002.label_protocol.preferred_target}`], kind: "metrics" },
    { title: "Limitations", section: "Research Control", claim: "The thesis should be explicit about what has not yet been proven.", bullets: ["Current evidence does not prove accuracy improvement.", "Same-pattern memory is leakage-aware mechanism validation only.", "Generalization still requires held-out expert labels across settings/domains."], evidence: ["Use phrase: held-out expert labels still needed", "Do not say: the AI is better now"] },
    { title: "Supervisor Decisions", section: "Decision", claim: "The meeting should produce concrete decisions for the evaluation phase.", bullets: ["Approve the research framing and wording.", "Approve EXP-002 labeling protocol and target size.", "Confirm M4B-2 remains blocked until EXP-002 results exist."], evidence: decisionRows.map((row) => `${row[0]}: ${row[1]}`), kind: "decision" },
    { title: "Demo Order And Close", section: "Appendix", claim: "The demo should stay evidence-led and avoid live implementation risk.", bullets: ["Open the dashboard first.", "Then show the slides and one-page brief.", "Then open EXP-001 and EXP-002 tables.", "Close with supervisor decisions."], evidence: [`Dashboard: ${repoRel(paths.dashboard)}`, "Slides: VEGO_AI_Thesis_Progress_Slides.md / .pptx", "Questions: SUPERVISOR_QUESTIONS.md"], kind: "appendix" },
  ];

  const slideMd = [
    "# VEGO-AI Thesis Progress Slides",
    "",
    `Prepared: ${generatedAt}`,
    `Supervisor session: ${meetingDate}`,
    "",
    "> Core wording: mechanism readiness, reusable human judgment, non-destructive comparison, human-AI co-reasoning, held-out expert labels still needed.",
    "",
    ...slideSpine.flatMap((slide, index) => [
      "---",
      "",
      `## ${index + 1}. ${slide.title}`,
      "",
      `**Claim:** ${slide.claim}`,
      "",
      "**Talking points:**",
      ...slide.bullets.map((b) => `- ${b}`),
      "",
      "**Evidence to show:**",
      ...slide.evidence.map((e) => `- ${e}`),
      "",
      `**Section:** ${slide.section}`,
    ]),
  ].join("\n");
  await writeFile("VEGO_AI_Thesis_Progress_Slides.md", slideMd);

  await writeFile("ONE_PAGE_SUPERVISOR_BRIEF.md", `# VEGO-AI Supervisor Brief\n\nDate: ${meetingDate}\n\n## Current State\n\nThe implemented prototype is complete through M4B-1: Human Review Queue, Human Feedback Manager, Human Judgment Memory, Memory Advisory Layer, deterministic memory-informed comparison, dashboard, visualizer UX refresh, and shared Claude-Codex memory.\n\n## Main Contribution\n\nVEGO-AI can be extended with a reusable human-judgment layer that supports human-AI co-reasoning in domain model assessment while preserving the original AI decision pipeline.\n\n## Evidence Snapshot\n\n${mdTable(["Evidence", "Value"], [["Settings", overview.settings_count], ["Cases", overview.case_count], ["Variability patterns", overview.variability_pattern_count], ["Review queue items", overview.human_review_queue_count], ["Resolved feedback", overview.resolved_feedback_count], ["Human Judgment Memory entries", overview.judgment_memory_count], ["Memory advice records", overview.memory_advice_count], ["AI classification changed in baseline", overview.ai_classification_changed_count], ["EXP-001 comparison rows", exp001.totals.comparison_count], ["EXP-002 labeling rows", exp002.totals.row_count]])}\n\n## What Is Not Claimed Yet\n\n- We do not claim that memory improves accuracy yet.\n- We do not claim that Agent 4 was corrected by memory.\n- Same-pattern memory is leakage-aware mechanism validation, not proof of generalization.\n- Held-out expert labels are still needed.\n\n## Decision Needed\n\nApprove EXP-002 expert labeling so original vs memory-informed agreement can be evaluated on generalization-safe labels.\n`);

  await writeFile("THESIS_DEMO_SCRIPT.md", `# Thesis Demo Script\n\n## Opening Sentence\n\n\"I want to show the progress from the original VEGO-AI assessment pipeline to a reusable human judgment layer. The main point is mechanism readiness, not an accuracy-improvement claim yet.\"\n\n## Open These Files In This Order\n\n1. Dashboard: \`${repoRel(paths.dashboard)}\`\n2. Slides: \`artifacts/supervisor_demo_2026-06-17/VEGO_AI_Thesis_Progress_Slides.pptx\` or \`VEGO_AI_Thesis_Progress_Slides.md\`\n3. One-page brief: \`artifacts/supervisor_demo_2026-06-17/ONE_PAGE_SUPERVISOR_BRIEF.md\`\n4. EXP-001 table: \`artifacts/supervisor_demo_2026-06-17/tables/exp001_summary.md\`\n5. EXP-002 labeling plan: \`artifacts/supervisor_demo_2026-06-17/tables/exp002_labeling_plan.md\`\n6. Supervisor decisions: \`artifacts/supervisor_demo_2026-06-17/tables/supervisor_decisions.md\`\n\n## 10-Minute Talk Track\n\n1. Problem: VEGO-AI can assess models and detect variability, but repeated expert judgment should not be lost.\n2. Contribution: human judgment is selectively triggered, structurally captured, and stored as reusable knowledge.\n3. Architecture: M1-M4B-1 create review queue, feedback, memory, advice, and deterministic comparison.\n4. Boundary: this is a non-destructive comparison; Agent 4 and baseline outputs are unchanged.\n5. Evidence: dashboard summarizes ${overview.settings_count} settings, ${overview.case_count} cases, ${overview.variability_pattern_count} variability patterns, ${overview.human_review_queue_count} review items, ${overview.judgment_memory_count} memory entries, and ${overview.memory_advice_count} advice records.\n6. EXP-001: ${exp001.totals.comparison_count} comparison rows; ${exp001.totals.generalization_safe_expert_labeled_count} generalization-safe expert labels, so no accuracy claim yet.\n7. EXP-002: ${exp002.totals.row_count} labeling rows are prepared; ${exp002.totals.generalization_safe_candidate_count} are generalization-safe candidates.\n8. Ask: approve the labeling protocol, target size, leakage policy, and M4B-2 gate.\n\n## Avoid Saying\n\n- \"We proved accuracy improvement.\"\n- \"The AI is better now.\"\n- \"Human-in-the-loop is new.\"\n- \"The system automatically corrects Agent 4.\"\n\n## Use These Phrases\n\n- \"mechanism readiness\"\n- \"reusable human judgment\"\n- \"non-destructive comparison\"\n- \"human-AI co-reasoning\"\n- \"held-out expert labels still needed\"\n- \"same-pattern memory is leakage-aware mechanism validation\"\n`);

  await writeFile("SUPERVISOR_QUESTIONS.md", `# Supervisor Questions\n\n${mdTable(["Area", "Question", "Why it matters"], [
    ["Research framing", "Is the thesis question focused enough around reusable human judgment in AI-assisted model assessment?", "Locks the thesis narrative before writing."],
    ["Contribution", "Is the phrase 'selectively triggered, structurally captured, and stored as reusable knowledge' acceptable?", "This becomes the contribution statement."],
    ["Evaluation labels", "Should EXP-002 use only Substantial, Occasional, and Undetermined / Needs Review?", "Keeps expert labeling reliable and auditable."],
    ["Target size", "Is 20 labels enough for the first MSc evaluation, or should we target 30-50?", "Controls evidence strength and workload."],
    ["Leakage", "Should same-pattern memory be excluded from generalization evaluation?", "Protects the empirical claim."],
    ["M4B-2 gate", "Should M4B-2 remain blocked until EXP-002 results are reviewed?", "Prevents premature behavior-changing implementation."],
  ])}\n`);

  await writeFile("SCREENSHOT_CHECKLIST.md", `# Screenshot Checklist\n\nCapture these manually if the supervisor asks for figures in the thesis draft.\n\n${mdTable(["Screenshot", "Path or action", "Purpose"], [
    ["Dashboard overview", repoRel(paths.dashboard), "Show project-scale evidence."],
    ["Human review section", "Dashboard page section", "Show M1 review queue counts."],
    ["Memory/advice section", "Dashboard page section", "Show M3/M4A evidence."],
    ["EXP-001 table", "artifacts/supervisor_demo_2026-06-17/tables/exp001_summary.md", "Show mechanism-readiness conclusion."],
    ["EXP-002 labeling sheet", "artifacts/supervisor_demo_2026-06-17/tables/source_exp002_expert_labeling_sheet.md", "Show next expert labeling task."],
    ["Visualizer mismatch banner", "Run VEGO-AI/vego_visualizer_delivery/visualize_compliance.py", "Show research safety UX."],
  ])}\n\nDo not screenshot controlled PDFs, model bundles, API keys, private Confluence config, or ignored raw research artifacts unless explicitly audited.\n`);

  await writeFile("README.md", `# Supervisor Demo Package\n\nPrepared for the thesis supervisor Zoom session on ${meetingDate}.\n\n## Primary Files\n\n- \`VEGO_AI_Thesis_Progress_Slides.md\`: 20-slide Markdown deck.\n- \`VEGO_AI_Thesis_Progress_Slides.pptx\`: editable PowerPoint deck if generated successfully.\n- \`ONE_PAGE_SUPERVISOR_BRIEF.md\`: one-page meeting summary.\n- \`THESIS_DEMO_SCRIPT.md\`: exact talk track and file order.\n- \`SUPERVISOR_QUESTIONS.md\`: questions to ask during the meeting.\n- \`SCREENSHOT_CHECKLIST.md\`: manual screenshot checklist.\n- \`figures/\`: static SVG and Mermaid source figures.\n- \`tables/\`: Markdown/CSV evidence tables.\n\n## Safe Claims\n\n- The system demonstrates mechanism readiness for reusable human judgment.\n- The comparison is non-destructive: the original VEGO-AI output remains the baseline.\n- M4B-1 supports controlled evaluation of memory-informed comparison.\n- Held-out expert labels are still needed before any accuracy-improvement claim.\n\n## Claims To Avoid\n\n- Accuracy improvement has been proven.\n- Agent 4 has been corrected by memory.\n- Human-in-the-loop is new.\n- M4B-2 has been implemented.\n\n## Data Sources Used\n\n- \`${repoRel(paths.dashboardMetrics)}\`\n- \`${repoRel(paths.exp001Summary)}\`\n- \`${repoRel(paths.exp002Summary)}\`\n\n## Validation State Used For This Package\n\n${mdTable(["Check", "Status"], validationRows.map((row) => [row[0], row[2]]))}\n`);

  const commonModule = `const slides = ${JSON.stringify(slideSpine, null, 2)};\n\nconst colors = {\n  ink: "#0F172A",\n  muted: "#475569",\n  sub: "#64748B",\n  bg: "#F8FAFC",\n  panel: "#FFFFFF",\n  line: "#CBD5E1",\n  teal: "#0B7285",\n  green: "#2F9E44",\n  violet: "#5F3DC4",\n  orange: "#C2410C",\n};\n\nfunction text(ctx, slide, textValue, x, y, w, h, opts = {}) {\n  return ctx.addText(slide, {\n    text: textValue,\n    x,\n    y,\n    width: w,\n    height: h,\n    fontSize: opts.size ?? 24,\n    color: opts.color ?? colors.ink,\n    bold: opts.bold ?? false,\n    typeface: opts.face ?? (opts.title ? ctx.fonts.title : ctx.fonts.body),\n    insets: opts.insets ?? { left: 8, right: 8, top: 6, bottom: 6 },\n    fill: opts.fill ?? "#00000000",\n    line: opts.line ?? ctx.line("#00000000", 0),\n    align: opts.align ?? "left",\n    valign: opts.valign ?? "top",\n  });\n}\n\nfunction box(ctx, slide, x, y, w, h, fill = colors.panel, stroke = colors.line) {\n  return ctx.addShape(slide, { x, y, width: w, height: h, fill, line: ctx.line(stroke, 2) });\n}\n\nfunction bulletBlock(ctx, slide, items, x, y, w, h, size = 23) {\n  text(ctx, slide, items.map((item) => \`- \${item}\`).join("\\n"), x, y, w, h, { size, color: colors.ink, insets: { left: 12, right: 12, top: 8, bottom: 8 } });\n}\n\nfunction footer(ctx, slide, n) {\n  text(ctx, slide, "VEGO-AI thesis progress | supervisor session | " + String(n).padStart(2, "0"), 56, 675, 840, 28, { size: 14, color: colors.sub });\n}\n\nfunction addHeader(ctx, slide, data, n) {\n  ctx.addShape(slide, { x: 0, y: 0, width: 1280, height: 720, fill: colors.bg, line: ctx.line("#00000000", 0) });\n  ctx.addShape(slide, { x: 0, y: 0, width: 1280, height: 12, fill: colors.teal, line: ctx.line("#00000000", 0) });\n  text(ctx, slide, data.section.toUpperCase(), 56, 34, 460, 26, { size: 14, color: colors.teal, bold: true });\n  text(ctx, slide, data.title, 52, 70, 780, 58, { size: 36, bold: true, title: true });\n  footer(ctx, slide, n);\n}\n\nfunction renderTitle(presentation, ctx, data, n) {\n  const slide = presentation.slides.add();\n  ctx.addShape(slide, { x: 0, y: 0, width: 1280, height: 720, fill: "#0F172A", line: ctx.line("#0F172A", 0) });\n  ctx.addShape(slide, { x: 0, y: 0, width: 16, height: 720, fill: colors.teal, line: ctx.line(colors.teal, 0) });\n  text(ctx, slide, data.title, 76, 92, 900, 86, { size: 48, bold: true, title: true, color: "#FFFFFF" });\n  text(ctx, slide, data.subtitle ?? "", 78, 182, 740, 38, { size: 24, color: "#D1E7EC" });\n  bulletBlock(ctx, slide, data.bullets, 78, 276, 655, 220, 25);\n  const cardX = 815;\n  box(ctx, slide, cardX, 98, 360, 430, "#FFFFFF", "#FFFFFF");\n  text(ctx, slide, "Evidence", cardX + 24, 126, 290, 34, { size: 23, bold: true, color: colors.teal });\n  bulletBlock(ctx, slide, data.evidence, cardX + 22, 174, 310, 285, 20);\n  text(ctx, slide, "Non-destructive comparison | M4B-2 blocked", 78, 638, 720, 28, { size: 18, color: "#D1E7EC" });\n  text(ctx, slide, String(n).padStart(2, "0"), 1118, 626, 70, 44, { size: 24, bold: true, color: "#FFFFFF", align: "right" });\n  return slide;\n}\n\nfunction renderFlow(presentation, ctx, data, n) {\n  const slide = presentation.slides.add();\n  addHeader(ctx, slide, data, n);\n  text(ctx, slide, data.claim, 56, 136, 870, 58, { size: 25, color: colors.muted });\n  const nodes = data.flow ?? [];\n  const startX = 64;\n  const y = 270;\n  const w = 205;\n  const gap = 28;\n  nodes.forEach((node, index) => {\n    const x = startX + index * (w + gap);\n    box(ctx, slide, x, y, w, 132, "#FFFFFF", index % 2 ? colors.green : colors.teal);\n    text(ctx, slide, node.title, x + 16, y + 18, w - 32, 28, { size: 22, bold: true, color: colors.ink });\n    text(ctx, slide, [node.body1, node.body2].filter(Boolean).join("\\n"), x + 16, y + 56, w - 32, 56, { size: 18, color: colors.muted });\n    if (index < nodes.length - 1) {\n      text(ctx, slide, ">", x + w + 2, y + 47, gap - 4, 34, { size: 26, bold: true, color: colors.sub, align: "center" });\n    }\n  });\n  bulletBlock(ctx, slide, data.bullets, 70, 460, 540, 145, 21);\n  bulletBlock(ctx, slide, data.evidence, 650, 460, 500, 145, 20);\n  return slide;\n}\n\nfunction renderMetrics(presentation, ctx, data, n) {\n  const slide = presentation.slides.add();\n  addHeader(ctx, slide, data, n);\n  text(ctx, slide, data.claim, 56, 136, 920, 56, { size: 25, color: colors.muted });\n  const evidence = data.evidence.slice(0, 4);\n  evidence.forEach((item, index) => {\n    const x = 72 + index * 292;\n    box(ctx, slide, x, 230, 250, 150, "#FFFFFF", [colors.teal, colors.green, colors.violet, colors.orange][index]);\n    const parts = item.split(":");\n    text(ctx, slide, parts[0], x + 18, 252, 212, 38, { size: 20, bold: true, color: colors.ink });\n    text(ctx, slide, parts.slice(1).join(":").trim() || item, x + 18, 302, 212, 52, { size: 24, bold: true, color: colors.teal });\n  });\n  bulletBlock(ctx, slide, data.bullets, 76, 445, 840, 150, 22);\n  return slide;\n}\n\nfunction renderTable(presentation, ctx, data, n) {\n  const slide = presentation.slides.add();\n  addHeader(ctx, slide, data, n);\n  text(ctx, slide, data.claim, 56, 136, 900, 54, { size: 25, color: colors.muted });\n  const rows = data.evidence.slice(0, 6);\n  rows.forEach((row, index) => {\n    const y = 220 + index * 54;\n    box(ctx, slide, 70, y, 1060, 44, index % 2 ? "#F1F5F9" : "#FFFFFF", "#D8E2EA");\n    const [left, ...rest] = row.split(":");\n    text(ctx, slide, left, 88, y + 7, 285, 30, { size: 18, bold: true, color: colors.ink });\n    text(ctx, slide, rest.join(":").trim(), 388, y + 7, 720, 30, { size: 18, color: colors.muted });\n  });\n  return slide;\n}\n\nfunction renderDefault(presentation, ctx, data, n) {\n  const slide = presentation.slides.add();\n  addHeader(ctx, slide, data, n);\n  text(ctx, slide, data.claim, 56, 136, 850, 72, { size: 26, color: colors.muted });\n  box(ctx, slide, 64, 240, 690, 330, "#FFFFFF", "#D8E2EA");\n  text(ctx, slide, "Talking points", 88, 266, 260, 28, { size: 21, bold: true, color: colors.teal });\n  bulletBlock(ctx, slide, data.bullets, 86, 306, 620, 230, 22);\n  box(ctx, slide, 798, 240, 330, 330, "#FFFFFF", colors.teal);\n  text(ctx, slide, "Evidence", 822, 266, 240, 28, { size: 21, bold: true, color: colors.teal });\n  bulletBlock(ctx, slide, data.evidence, 820, 306, 275, 230, 19);\n  return slide;\n}\n\nexport async function renderSlide(presentation, ctx, index) {\n  const data = slides[index];\n  const n = index + 1;\n  if (data.kind === "title") return renderTitle(presentation, ctx, data, n);\n  if (data.kind === "flow") return renderFlow(presentation, ctx, data, n);\n  if (data.kind === "metrics") return renderMetrics(presentation, ctx, data, n);\n  if (data.kind === "table" || data.kind === "decision") return renderTable(presentation, ctx, data, n);\n  return renderDefault(presentation, ctx, data, n);\n}\n`;
  await fs.writeFile(path.join(slidesDir, "common.mjs"), commonModule, "utf8");
  for (let i = 1; i <= slideSpine.length; i += 1) {
    const nn = String(i).padStart(2, "0");
    await fs.writeFile(path.join(slidesDir, `slide-${nn}.mjs`), `import { renderSlide } from "./common.mjs";\nexport async function slide${nn}(presentation, ctx) {\n  return renderSlide(presentation, ctx, ${i - 1});\n}\n`, "utf8");
  }
  await fs.writeFile(path.join(workspace, "slide-spine.json"), `${JSON.stringify(slideSpine, null, 2)}\n`, "utf8");

  console.log(JSON.stringify({
    outputDir: outDir,
    slides: slideSpine.length,
    figures: figures.length,
    tables: 5,
    dashboardOverview: overview,
    exp001Totals: exp001.totals,
    exp002Totals: exp002.totals,
  }, null, 2));
}

main().catch((error) => {
  console.error(error.stack || error.message || String(error));
  process.exit(1);
});
