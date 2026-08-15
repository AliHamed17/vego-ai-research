#!/usr/bin/env node

import fs from "node:fs/promises";
import fsSync from "node:fs";
import path from "node:path";
import crypto from "node:crypto";
import { execFileSync } from "node:child_process";

const root = process.cwd();
const runRoot = path.join(root, "VEGO-AI", "runs", "20260614-122150", "human");
const outDir = path.join(root, "reports", "generated", "evaluation_comparison");
const artifactDir = path.join(root, "artifacts");
const reviewPath = path.join(artifactDir, "EVALUATION_STRICT_REVIEW.md");
const settings = ["cd_ch", "cd_pw", "ucd_ch", "ucd_pw"];

const baselineFiles = {
  cd_ch: "agentD_variability_classes__cd_ch.json",
  cd_pw: "agentD_variability_classes.json",
  ucd_ch: "agentD_variability_classes.json",
  ucd_pw: "agentD_variability_classes_ucd_pw.json",
};

function rel(filePath) {
  return path.relative(root, filePath).replaceAll(path.sep, "/");
}

function sha256(text) {
  return crypto.createHash("sha256").update(text).digest("hex");
}

async function readJson(filePath) {
  return JSON.parse(await fs.readFile(filePath, "utf8"));
}

async function readJsonl(filePath) {
  try {
    const text = await fs.readFile(filePath, "utf8");
    return text.split(/\r?\n/).filter(Boolean).map((line) => JSON.parse(line));
  } catch {
    return [];
  }
}

function countBy(rows, getter) {
  const out = {};
  for (const row of rows) {
    const key = getter(row) ?? "";
    out[key] = (out[key] ?? 0) + 1;
  }
  return out;
}

function boolCount(rows, getter) {
  return rows.filter((row) => Boolean(getter(row))).length;
}

function csvEscape(value) {
  const text = value == null ? "" : String(value);
  return /[",\r\n]/.test(text) ? `"${text.replaceAll('"', '""')}"` : text;
}

function toCsv(headers, rows) {
  return [
    headers.map(csvEscape).join(","),
    ...rows.map((row) => headers.map((header) => csvEscape(row[header])).join(",")),
  ].join("\n") + "\n";
}

function mdTable(headers, rows) {
  return [
    `| ${headers.join(" | ")} |`,
    `| ${headers.map(() => "---").join(" | ")} |`,
    ...rows.map((row) => `| ${headers.map((header) => String(row[header] ?? "").replaceAll("\n", "<br>")).join(" | ")} |`),
  ].join("\n");
}

function parseCsv(text) {
  const rows = [];
  let row = [];
  let field = "";
  let quote = false;
  for (let i = 0; i < text.length; i += 1) {
    const ch = text[i];
    const next = text[i + 1];
    if (quote) {
      if (ch === '"' && next === '"') {
        field += '"';
        i += 1;
      } else if (ch === '"') {
        quote = false;
      } else {
        field += ch;
      }
    } else if (ch === '"') {
      quote = true;
    } else if (ch === ",") {
      row.push(field);
      field = "";
    } else if (ch === "\n") {
      row.push(field.replace(/\r$/, ""));
      rows.push(row);
      row = [];
      field = "";
    } else {
      field += ch;
    }
  }
  if (field.length || row.length) {
    row.push(field);
    rows.push(row);
  }
  const headers = rows.shift() ?? [];
  return rows.filter((r) => r.length > 1 || r[0]).map((r) => Object.fromEntries(headers.map((h, i) => [h, r[i] ?? ""])));
}

function f1ForLabel(rows, label, predField) {
  let tp = 0;
  let fp = 0;
  let fn = 0;
  for (const row of rows) {
    const pred = row[predField];
    const gold = row.expert_label;
    if (pred === label && gold === label) tp += 1;
    if (pred === label && gold !== label) fp += 1;
    if (pred !== label && gold === label) fn += 1;
  }
  const precision = tp + fp === 0 ? null : tp / (tp + fp);
  const recall = tp + fn === 0 ? null : tp / (tp + fn);
  const f1 = precision == null || recall == null || precision + recall === 0 ? null : (2 * precision * recall) / (precision + recall);
  return { label, tp, fp, fn, precision, recall, f1 };
}

function accuracy(rows, predField) {
  if (!rows.length) return null;
  return rows.filter((row) => row[predField] === row.expert_label).length / rows.length;
}

function confusion(rows, predField) {
  const labels = Array.from(new Set(rows.flatMap((row) => [row.expert_label, row[predField]].filter(Boolean)))).sort();
  const matrix = {};
  for (const gold of labels) {
    matrix[gold] = {};
    for (const pred of labels) matrix[gold][pred] = 0;
  }
  for (const row of rows) {
    if (!row.expert_label) continue;
    matrix[row.expert_label][row[predField]] = (matrix[row.expert_label][row[predField]] ?? 0) + 1;
  }
  return { labels, matrix };
}

async function gatherBaseline() {
  const files = [];
  const rows = [];
  const preservation = [];
  for (const setting of settings) {
    const currentPath = path.join(root, "VEGO-AI", "eval_output", setting, baselineFiles[setting]);
    const currentText = await fs.readFile(currentPath, "utf8");
    let baselineText = "";
    let matchesOfficialBaseline = false;
    try {
      baselineText = execFileSync("git", ["show", `official-vego-ai-baseline:eval_output/${setting}/${baselineFiles[setting]}`], {
        cwd: root,
        encoding: "utf8",
        maxBuffer: 1024 * 1024 * 4,
      });
      matchesOfficialBaseline = sha256(currentText) === sha256(baselineText);
    } catch {
      matchesOfficialBaseline = false;
    }

    const json = JSON.parse(currentText);
    const classifications = json.variability_classifications ?? [];
    for (const item of classifications) {
      rows.push({
        setting,
        pattern_id: item.pattern_id,
        classification: item.classification,
        confidence: item.confidence ?? "",
        flag_for_guidelines_update: Boolean(item.flag_for_guidelines_update),
        requires_human_review: Boolean(item.requires_human_review),
      });
    }
    files.push({ setting, path: rel(currentPath), rows: classifications.length });
    preservation.push({
      setting,
      current_path: rel(currentPath),
      official_baseline_path: `eval_output/${setting}/${baselineFiles[setting]}`,
      matches_official_baseline: matchesOfficialBaseline,
      current_sha256: sha256(currentText),
      official_baseline_sha256: baselineText ? sha256(baselineText) : null,
    });
  }
  const caseCount = settings.reduce((sum, setting) => {
    const dir = path.join(root, "VEGO-AI", "eval_output", setting);
    return sum + fsSync.readdirSync(dir).filter((name) => /^agentC_case_.*\.json$/i.test(name)).length;
  }, 0);
  return {
    baseline_commit: execFileSync("git", ["rev-parse", "official-vego-ai-baseline"], { cwd: root, encoding: "utf8" }).trim(),
    baseline_branch_commit: execFileSync("git", ["rev-parse", "baseline/official-vego-ai"], { cwd: root, encoding: "utf8" }).trim(),
    files,
    preservation,
    settings_count: settings.length,
    student_model_case_count: caseCount,
    pattern_count: rows.length,
    classification_counts: countBy(rows, (row) => row.classification),
    confidence_counts: countBy(rows, (row) => row.confidence),
    guideline_update_flag_count: boolCount(rows, (row) => row.flag_for_guidelines_update),
    requires_human_review_flag_count: boolCount(rows, (row) => row.requires_human_review),
    rows,
  };
}

async function gatherEnhanced() {
  const reviewItems = [];
  const resolvedItems = [];
  const memoryItems = [];
  const adviceItems = [];
  const comparisonRows = [];
  const comparisonFileRows = [];

  for (const setting of settings) {
    const settingDir = path.join(runRoot, setting);
    reviewItems.push(...(await readJsonl(path.join(settingDir, "human_review_queue.jsonl"))).map((r) => ({ ...r, setting })));
    resolvedItems.push(...(await readJsonl(path.join(settingDir, "human_review_queue_resolved.jsonl"))).map((r) => ({ ...r, setting })));
    memoryItems.push(...(await readJsonl(path.join(settingDir, "human_judgment_memory.jsonl"))).map((r) => ({ ...r, setting })));

    try {
      const adviceJson = await readJson(path.join(settingDir, "memory_advice.json"));
      for (const advice of adviceJson.advice ?? []) adviceItems.push({ ...advice, setting });
    } catch {
      // no advice file for this setting
    }

    const comparisonPath = path.join(settingDir, "memory_informed_comparison.json");
    try {
      const comparisonJson = await readJson(comparisonPath);
      const comparisons = comparisonJson.comparisons ?? [];
      comparisonFileRows.push({ setting, path: rel(comparisonPath), rows: comparisons.length });
      for (const comparison of comparisons) comparisonRows.push({ ...comparison, setting, source_file: rel(comparisonPath) });
    } catch {
      comparisonFileRows.push({ setting, path: rel(comparisonPath), rows: 0 });
    }
  }

  const adviceHits = adviceItems.filter((item) => (item.memory_matches ?? []).length > 0);
  const adviceWithMatchReasons = adviceItems.filter((item) => (item.memory_matches ?? []).some((match) => (match.match_reasons ?? []).length > 0));
  return {
    run_root: rel(runRoot),
    human_review_queue_count: reviewItems.length,
    resolved_feedback_count: resolvedItems.length,
    reusable_judgment_count: memoryItems.length,
    memory_advice_record_count: adviceItems.length,
    memory_advice_hit_count: adviceHits.length,
    memory_advice_with_match_reasons_count: adviceWithMatchReasons.length,
    memory_informed_comparison_count: comparisonRows.length,
    requires_human_review_after_memory_count: boolCount(comparisonRows, (row) => row.requires_human_review_after_memory),
    memory_informed_differs_from_original_count: boolCount(comparisonRows, (row) => row.memory_informed_differs_from_original),
    ai_behavior_changed_in_baseline_count: boolCount(comparisonRows, (row) => row.ai_behavior_changed_in_baseline),
    ai_classification_changed_advice_count: boolCount(adviceItems, (row) => row.ai_classification_changed),
    review_trigger_counts: countBy(reviewItems, (row) => row.trigger_reason ?? row.trigger_type ?? (row.triggers ?? []).join(";") ?? "unknown"),
    review_status_counts: countBy(reviewItems, (row) => row.status ?? "unknown"),
    advice_strength_counts: countBy(comparisonRows, (row) => row.memory_advice?.advice_strength ?? "unknown"),
    leakage_counts: countBy(comparisonRows, (row) => row.evaluation_leakage_status ?? "unknown"),
    rule_counts: countBy(comparisonRows, (row) => row.rule_applied ?? "unknown"),
    conflict_count: comparisonRows.filter((row) => row.memory_advice?.has_conflicting_memory).length,
    moderate_disagreement_count: comparisonRows.filter((row) => row.rule_applied === "moderate_disagreement_keep_original_require_review").length,
    comparison_file_rows: comparisonFileRows,
    comparisonRows,
    memoryItems,
    adviceItems,
    reviewItems,
    resolvedItems,
  };
}

async function gatherExpertRows() {
  const exp001Path = path.join(root, "reports", "generated", "exp001", "exp001_evaluation_dataset.csv");
  const exp002Path = path.join(root, "reports", "generated", "exp002", "expert_labeling_sheet.csv");
  const exp001 = parseCsv(await fs.readFile(exp001Path, "utf8"));
  const exp002 = parseCsv(await fs.readFile(exp002Path, "utf8"));
  const exp001Labels = new Map();
  for (const row of exp001) {
    if (row.expert_classification) {
      exp001Labels.set(`${row.setting}|${row.pattern_id}`, row);
    }
  }
  const exp002Existing = exp002.filter((row) => row.existing_expert_label);
  const exp002New = exp002.filter((row) => row.expert_label);
  return {
    exp001_path: rel(exp001Path),
    exp002_path: rel(exp002Path),
    exp001,
    exp002,
    exp001Labels,
    exp002Existing,
    exp002New,
  };
}

function buildComparisonTable(enhanced, labels) {
  return enhanced.comparisonRows
    .sort((a, b) => `${a.setting}|${a.pattern_id}`.localeCompare(`${b.setting}|${b.pattern_id}`))
    .map((row) => {
      const label = labels.exp001Labels.get(`${row.setting}|${row.pattern_id}`);
      const expertLabel = label?.expert_classification ?? "";
      const original = row.original_agent4_classification?.classification ?? "";
      const memory = row.memory_informed_classification?.classification ?? "";
      return {
        setting: row.setting,
        pattern_id: row.pattern_id,
        original_agent4_classification: original,
        original_confidence: row.original_agent4_classification?.confidence ?? "",
        memory_advice_strength: row.memory_advice?.advice_strength ?? "",
        memory_informed_classification: memory,
        memory_informed_differs_from_original: String(Boolean(row.memory_informed_differs_from_original)),
        requires_human_review_after_memory: String(Boolean(row.requires_human_review_after_memory)),
        rule_applied: row.rule_applied ?? "",
        evaluation_leakage_status: row.evaluation_leakage_status ?? "",
        human_memory_used: (row.human_memory_used ?? []).map((item) => item.memory_id ?? item).join(";"),
        expert_label: expertLabel,
        expert_label_source: label?.expert_label_source ?? "",
        correct_original: expertLabel ? String(original === expertLabel) : "",
        correct_memory_informed: expertLabel ? String(memory === expertLabel) : "",
        source_file: row.source_file,
      };
    });
}

function evaluationMetrics(rows) {
  const labeled = rows.filter((row) => row.expert_label);
  const noSame = labeled.filter((row) => row.evaluation_leakage_status !== "same_pattern_memory_used");
  const safe = labeled.filter((row) => row.evaluation_leakage_status !== "same_pattern_memory_used" && row.evaluation_leakage_status !== "unknown");
  const crossSetting = labeled.filter((row) => row.evaluation_leakage_status === "cross_setting_memory_used");
  const labels = Array.from(new Set(labeled.map((row) => row.expert_label))).sort();
  const metricsFor = (subset) => {
    const originalAccuracy = accuracy(subset, "original_agent4_classification");
    const memoryAccuracy = accuracy(subset, "memory_informed_classification");
    const perClassOriginal = labels.map((label) => f1ForLabel(subset, label, "original_agent4_classification"));
    const perClassMemory = labels.map((label) => f1ForLabel(subset, label, "memory_informed_classification"));
    const macroF1Original = perClassOriginal.length ? perClassOriginal.reduce((sum, row) => sum + (row.f1 ?? 0), 0) / perClassOriginal.length : null;
    const macroF1Memory = perClassMemory.length ? perClassMemory.reduce((sum, row) => sum + (row.f1 ?? 0), 0) / perClassMemory.length : null;
    return {
      rows: subset.length,
      original_accuracy: originalAccuracy,
      memory_informed_accuracy: memoryAccuracy,
      original_macro_f1: subset.length ? macroF1Original : null,
      memory_informed_macro_f1: subset.length ? macroF1Memory : null,
      original_confusion_matrix: confusion(subset, "original_agent4_classification"),
      memory_informed_confusion_matrix: confusion(subset, "memory_informed_classification"),
      per_class_original: perClassOriginal,
      per_class_memory_informed: perClassMemory,
    };
  };
  return {
    all_labeled: metricsFor(labeled),
    excluding_same_pattern: metricsFor(noSame),
    generalization_safe: metricsFor(safe),
    cross_setting_only: metricsFor(crossSetting),
    paired: {
      original_wrong_memory_correct: labeled.filter((row) => row.original_agent4_classification !== row.expert_label && row.memory_informed_classification === row.expert_label).length,
      original_correct_memory_wrong: labeled.filter((row) => row.original_agent4_classification === row.expert_label && row.memory_informed_classification !== row.expert_label).length,
      both_correct: labeled.filter((row) => row.original_agent4_classification === row.expert_label && row.memory_informed_classification === row.expert_label).length,
      both_wrong: labeled.filter((row) => row.original_agent4_classification !== row.expert_label && row.memory_informed_classification !== row.expert_label).length,
      changed_and_correct: labeled.filter((row) => row.memory_informed_differs_from_original === "true" && row.memory_informed_classification === row.expert_label).length,
      changed_and_wrong: labeled.filter((row) => row.memory_informed_differs_from_original === "true" && row.memory_informed_classification !== row.expert_label).length,
      unchanged: labeled.filter((row) => row.memory_informed_differs_from_original !== "true").length,
    },
  };
}

function percentage(value) {
  return value == null ? "not evaluable" : `${(value * 100).toFixed(1)}%`;
}

function labelSourceRows(labels, enhanced) {
  return [
    {
      "Label source": "VEGO-AI/eval_output/<setting>/agentD_variability_classes*.json",
      Rows: 27,
      Settings: "cd_ch, cd_pw, ucd_ch, ucd_pw",
      "Label type": "Original Agent 4 output / baseline prediction",
      "Safe for generalization?": "No",
      Notes: "Baseline prediction only; must not be treated as ground truth.",
    },
    {
      "Label source": "VEGO-AI/analysis/agentD_variability_classes_*.json",
      Rows: 27,
      Settings: "cd_ch, cd_pw, ucd_ch, ucd_pw",
      "Label type": "Copied/curated analysis copy of Agent D output",
      "Safe for generalization?": "No",
      Notes: "No documentation found proving independent expert annotation; use as Agent 4 baseline copy.",
    },
    {
      "Label source": "VEGO-AI/runs/20260614-122150/human/ucd_ch/human_judgment_memory.jsonl",
      Rows: enhanced.memoryItems.length,
      Settings: "ucd_ch",
      "Label type": "Human Judgment Memory from expert_01 feedback",
      "Safe for generalization?": "No",
      Notes: "Usable for mechanism validation only; same-pattern memory creates leakage if used as test truth.",
    },
    {
      "Label source": labels.exp001_path,
      Rows: labels.exp001.filter((row) => row.expert_classification).length,
      Settings: "ucd_ch",
      "Label type": "Joined existing labels from Human Judgment Memory",
      "Safe for generalization?": "No",
      Notes: "All expert-labeled rows are same-pattern memory rows in current EXP-001 output.",
    },
    {
      "Label source": labels.exp002_path,
      Rows: labels.exp002.length,
      Settings: "cd_ch, cd_pw, ucd_ch, ucd_pw",
      "Label type": "Labeling sheet; existing labels plus blank expert_label fields",
      "Safe for generalization?": "Pending",
      Notes: `${labels.exp002Existing.length} existing labels; ${labels.exp002.filter((row) => row.generalization_safe_candidate === "True").length} generalization-safe candidates; human labels not filled yet.`,
    },
  ];
}

function layerRows(baseline, enhanced) {
  return [
    {
      Layer: "Original VEGO-AI / Agent 4",
      "Output file": "VEGO-AI/eval_output/<setting>/agentD_variability_classes*.json",
      "What it measures": "Baseline variability classification",
      Count: baseline.pattern_count,
      "Does it change baseline?": "No; this is the baseline",
    },
    {
      Layer: "M1 Human Review Queue",
      "Output file": "VEGO-AI/runs/20260614-122150/human/<setting>/human_review_queue.jsonl",
      "What it measures": "Patterns routed to human review",
      Count: enhanced.human_review_queue_count,
      "Does it change baseline?": "No",
    },
    {
      Layer: "M2 Human Feedback Manager",
      "Output file": "human_review_queue_resolved.jsonl",
      "What it measures": "Resolved structured feedback decisions",
      Count: enhanced.resolved_feedback_count,
      "Does it change baseline?": "No",
    },
    {
      Layer: "M3 Human Judgment Memory",
      "Output file": "human_judgment_memory.jsonl",
      "What it measures": "Reusable human judgments with provenance",
      Count: enhanced.reusable_judgment_count,
      "Does it change baseline?": "No",
    },
    {
      Layer: "M4A Memory Advisory",
      "Output file": "memory_advice.json",
      "What it measures": "Advisory memory retrieval; records/hits",
      Count: `${enhanced.memory_advice_record_count} records; ${enhanced.memory_advice_hit_count} hits`,
      "Does it change baseline?": "No",
    },
    {
      Layer: "M4B-1 Deterministic Comparison",
      "Output file": "memory_informed_comparison.json",
      "What it measures": "Parallel memory-informed classification comparison",
      Count: enhanced.memory_informed_comparison_count,
      "Does it change baseline?": "No",
    },
  ];
}

function improvementRows(enhanced, baseline) {
  return [
    { "Improvement type": "Review targeting", Metric: "Human review queue items", Value: enhanced.human_review_queue_count, "Why it matters": "Makes review needs explicit instead of hidden in free text." },
    { "Improvement type": "Review targeting", Metric: "Guideline-update baseline flags", Value: baseline.guideline_update_flag_count, "Why it matters": "Identifies patterns where guideline interpretation may need review." },
    { "Improvement type": "Traceability", Metric: "Resolved feedback records", Value: enhanced.resolved_feedback_count, "Why it matters": "Captures human decisions as auditable records." },
    { "Improvement type": "Traceability", Metric: "Memory entries with provenance", Value: enhanced.memoryItems.filter((item) => item.provenance).length, "Why it matters": "Links reusable judgment back to source review and feedback." },
    { "Improvement type": "Traceability", Metric: "Advice items with match reasons", Value: enhanced.memory_advice_with_match_reasons_count, "Why it matters": "Shows why memory was retrieved." },
    { "Improvement type": "Reusability", Metric: "Reusable Human Judgment Memory entries", Value: enhanced.reusable_judgment_count, "Why it matters": "Turns expert decisions into reusable knowledge." },
    { "Improvement type": "Reusability", Metric: "Memory advice hits", Value: enhanced.memory_advice_hit_count, "Why it matters": "Shows memory can be retrieved for later patterns." },
    { "Improvement type": "Safety", Metric: "ai_classification_changed in M4A", Value: enhanced.ai_classification_changed_advice_count, "Why it matters": "Confirms advisory-only boundary." },
    { "Improvement type": "Safety", Metric: "ai_behavior_changed_in_baseline in M4B-1", Value: enhanced.ai_behavior_changed_in_baseline_count, "Why it matters": "Confirms baseline behavior was not changed." },
    { "Improvement type": "Safety", Metric: "Comparison rows with leakage labels", Value: enhanced.memory_informed_comparison_count, "Why it matters": "Enables leakage-aware evaluation." },
    { "Improvement type": "Escalation", Metric: "requires_human_review_after_memory", Value: enhanced.requires_human_review_after_memory_count, "Why it matters": "Flags unresolved disagreement rather than forcing an automatic correction." },
    { "Improvement type": "Escalation", Metric: "Moderate disagreement rules", Value: enhanced.moderate_disagreement_count, "Why it matters": "Shows conservative handling of memory disagreement." },
    { "Improvement type": "Escalation", Metric: "Conflicting memory count", Value: enhanced.conflict_count, "Why it matters": "Tracks whether memory creates conflicts." },
  ];
}

function simpleBarSvg(title, data, color = "#0B7285") {
  const entries = Object.entries(data);
  const width = 960;
  const height = 360;
  const margin = 70;
  const max = Math.max(1, ...entries.map(([, value]) => value));
  const slot = (width - margin * 2) / Math.max(1, entries.length);
  const bars = entries.map(([label, value], index) => {
    const barWidth = slot * 0.55;
    const barHeight = (value / max) * 190;
    const x = margin + index * slot + slot * 0.225;
    const y = 280 - barHeight;
    return `<rect x="${x}" y="${y}" width="${barWidth}" height="${barHeight}" rx="6" fill="${color}"/><text x="${x + barWidth / 2}" y="${y - 12}" text-anchor="middle" class="value">${value}</text><text x="${x + barWidth / 2}" y="315" text-anchor="middle" class="label">${label}</text>`;
  }).join("\n");
  return `<svg xmlns="http://www.w3.org/2000/svg" width="${width}" height="${height}" viewBox="0 0 ${width} ${height}">
  <style>.title{font:700 28px Arial;fill:#0F172A}.label{font:400 16px Arial;fill:#334155}.value{font:700 18px Arial;fill:#0F172A}</style>
  <rect width="${width}" height="${height}" fill="#F8FAFC"/>
  <text x="${margin}" y="50" class="title">${title}</text>
  ${bars}
</svg>`;
}

async function main() {
  await fs.mkdir(outDir, { recursive: true });
  await fs.mkdir(artifactDir, { recursive: true });

  const baseline = await gatherBaseline();
  const enhanced = await gatherEnhanced();
  const labels = await gatherExpertRows();
  const comparisonRows = buildComparisonTable(enhanced, labels);
  const metrics = evaluationMetrics(comparisonRows);
  const labelSources = labelSourceRows(labels, enhanced);
  const layers = layerRows(baseline, enhanced);
  const improvements = improvementRows(enhanced, baseline);

  const headers = [
    "setting",
    "pattern_id",
    "original_agent4_classification",
    "original_confidence",
    "memory_advice_strength",
    "memory_informed_classification",
    "memory_informed_differs_from_original",
    "requires_human_review_after_memory",
    "rule_applied",
    "evaluation_leakage_status",
    "human_memory_used",
    "expert_label",
    "expert_label_source",
    "correct_original",
    "correct_memory_informed",
    "source_file",
  ];
  await fs.writeFile(path.join(outDir, "original_vs_memory_informed.csv"), toCsv(headers, comparisonRows), "utf8");
  await fs.writeFile(path.join(outDir, "original_vs_memory_informed.md"), `# Original vs Memory-Informed Comparison\n\n${mdTable(headers, comparisonRows)}\n`, "utf8");

  await fs.writeFile(path.join(outDir, "leakage_distribution.svg"), simpleBarSvg("Leakage Distribution", enhanced.leakage_counts, "#C2410C"), "utf8");
  await fs.writeFile(path.join(outDir, "advice_strength_distribution.svg"), simpleBarSvg("Memory Advice Strength", enhanced.advice_strength_counts, "#0B7285"), "utf8");
  await fs.writeFile(path.join(outDir, "classification_counts.svg"), simpleBarSvg("Baseline Agent 4 Classification Counts", baseline.classification_counts, "#2F9E44"), "utf8");

  const summary = {
    generated_at: new Date().toISOString(),
    baseline_definition: {
      baseline: "Original VEGO-AI Agent 4 variability classification outputs from official-vego-ai-baseline / baseline/official-vego-ai, represented locally under VEGO-AI/eval_output/<setting>/agentD_variability_classes*.json.",
      official_baseline_commit: baseline.baseline_commit,
      baseline_branch_commit: baseline.baseline_branch_commit,
      current_main_commit: execFileSync("git", ["rev-parse", "HEAD"], { cwd: root, encoding: "utf8" }).trim(),
      eval_output_matches_official_baseline: baseline.preservation.every((row) => row.matches_official_baseline),
      preservation: baseline.preservation,
    },
    baseline_outputs: {
      settings_count: baseline.settings_count,
      student_model_case_count: baseline.student_model_case_count,
      agent4_pattern_count: baseline.pattern_count,
      classification_counts: baseline.classification_counts,
      confidence_counts: baseline.confidence_counts,
      guideline_update_flag_count: baseline.guideline_update_flag_count,
      requires_human_review_flag_count: baseline.requires_human_review_flag_count,
      files: baseline.files,
    },
    enhanced_outputs: {
      run_root: enhanced.run_root,
      human_review_queue_count: enhanced.human_review_queue_count,
      resolved_feedback_count: enhanced.resolved_feedback_count,
      reusable_judgment_count: enhanced.reusable_judgment_count,
      memory_advice_record_count: enhanced.memory_advice_record_count,
      memory_advice_hit_count: enhanced.memory_advice_hit_count,
      memory_informed_comparison_count: enhanced.memory_informed_comparison_count,
      requires_human_review_after_memory_count: enhanced.requires_human_review_after_memory_count,
      memory_informed_differs_from_original_count: enhanced.memory_informed_differs_from_original_count,
      ai_behavior_changed_in_baseline_count: enhanced.ai_behavior_changed_in_baseline_count,
      ai_classification_changed_advice_count: enhanced.ai_classification_changed_advice_count,
      advice_strength_counts: enhanced.advice_strength_counts,
      leakage_counts: enhanced.leakage_counts,
      rule_counts: enhanced.rule_counts,
      comparison_file_rows: enhanced.comparison_file_rows,
    },
    label_sources: labelSources,
    accuracy: metrics,
    strict_verdict: {
      accuracy_improvement: "not_proven",
      reason: "Only 3 labeled rows are available, all from same-pattern Human Judgment Memory; there are 0 generalization-safe expert-labeled rows. Memory-informed classifications differ from original in 0 of 27 rows.",
      chosen_option: "C plus D: reusable memory mainly improves traceability and escalation, not classification accuracy; evidence is insufficient for generalization.",
      thesis_claim_allowed: "The artifact demonstrates a reusable human-judgment mechanism, advisory retrieval, leakage-aware non-destructive comparison, and safer escalation. It does not prove improved classification accuracy yet.",
    },
    output_files: {
      comparison_csv: rel(path.join(outDir, "original_vs_memory_informed.csv")),
      comparison_md: rel(path.join(outDir, "original_vs_memory_informed.md")),
      summary_json: rel(path.join(outDir, "evaluation_summary.json")),
      strict_review: rel(reviewPath),
    },
  };
  await fs.writeFile(path.join(outDir, "evaluation_summary.json"), `${JSON.stringify(summary, null, 2)}\n`, "utf8");

  const review = `# VEGO-AI Strict Evaluation Review\n\nGenerated: 2026-06-16\n\n## Verdict\n\n**No accuracy improvement is proven yet.** The current evidence shows that the enhanced pipeline is evaluation-ready and improves traceability, reusable evidence, and conservative escalation, but it does not prove better classification accuracy than the original VEGO-AI baseline.\n\nThe strict verdict is **Option C plus Option D**: reusable memory mainly improves traceability and escalation, not classification accuracy; evidence is insufficient for generalization.\n\n## 1. Baseline Definition\n\nThe baseline is the original VEGO-AI Agent 4 variability classification output from \`official-vego-ai-baseline\` / \`baseline/official-vego-ai\` at commit \`${baseline.baseline_commit.slice(0, 7)}\`. The local baseline outputs are the Agent D variability classification files under \`VEGO-AI/eval_output/<setting>/agentD_variability_classes*.json\`.\n\nBaseline preservation check: **${baseline.preservation.every((row) => row.matches_official_baseline) ? "PASS" : "FAIL"}**. The four current Agent D classification files ${baseline.preservation.every((row) => row.matches_official_baseline) ? "match" : "do not all match"} their official-baseline equivalents by SHA-256.\n\n${mdTable(["setting", "current_path", "official_baseline_path", "matches_official_baseline"], baseline.preservation.map((row) => ({ ...row, matches_official_baseline: String(row.matches_official_baseline) })))}\n\n## 2. Baseline Output Summary\n\n${mdTable(["Metric", "Value"], [\n+    { Metric: "Settings", Value: baseline.settings_count },\n+    { Metric: "Student model result files", Value: baseline.student_model_case_count },\n+    { Metric: "Agent 4 variability patterns", Value: baseline.pattern_count },\n+    { Metric: "Classification counts", Value: JSON.stringify(baseline.classification_counts) },\n+    { Metric: "Confidence distribution", Value: JSON.stringify(baseline.confidence_counts) },\n+    { Metric: "Guideline-update flags", Value: baseline.guideline_update_flag_count },\n+    { Metric: "requires_human_review flags in baseline", Value: baseline.requires_human_review_flag_count },\n+  ])}\n\n## 3. Output Layer Table\n\n${mdTable(["Layer", "Output file", "What it measures", "Count", "Does it change baseline?"], layers)}\n\n## 4. Benchmark / Expert Labels\n\n${mdTable(["Label source", "Rows", "Settings", "Label type", "Safe for generalization?", "Notes"], labelSources)}\n\nImportant: Agent 4 output is not ground truth. The current independent held-out expert-label count is **0**.\n\n## 5. Original vs Memory-Informed Accuracy\n\nAll currently labeled rows: **${metrics.all_labeled.rows}**. Original accuracy: **${percentage(metrics.all_labeled.original_accuracy)}**. Memory-informed accuracy: **${percentage(metrics.all_labeled.memory_informed_accuracy)}**.\n\nGeneralization-safe labeled rows: **${metrics.generalization_safe.rows}**. Generalization-safe accuracy is **not evaluable**.\n\nPaired comparison:\n\n${mdTable(["Metric", "Value"], Object.entries(metrics.paired).map(([Metric, Value]) => ({ Metric, Value })))}\n\nInterpretation: M4B-1 made **${enhanced.memory_informed_differs_from_original_count}** classification changes out of **${enhanced.memory_informed_comparison_count}** comparisons. Therefore, no automatic accuracy improvement can be observed in this run.\n\n## 6. Leakage\n\n${mdTable(["Leakage status", "Count"], Object.entries(enhanced.leakage_counts).map(([key, value]) => ({ "Leakage status": key, Count: value })))}\n\nSame-pattern rows are mechanism validation only. They cannot support a generalization claim.\n\n## 7. Non-Accuracy Improvements\n\n${mdTable(["Improvement type", "Metric", "Value", "Why it matters"], improvements)}\n\n## 8. Benchmark Question\n\nAre we better than the baseline? **Not proven.**\n\nReasons:\n\n- There are only 3 labeled rows.\n- All labeled rows are same-pattern memory rows, so they are leakage-heavy mechanism evidence.\n- There are 0 generalization-safe expert-labeled rows.\n- Memory-informed classification differs from the original in 0 of 27 cases.\n\nThe strongest current improvement is not accuracy. It is traceability, reusable judgment capture, advisory retrieval, leakage tracking, and safer escalation through \`requires_human_review_after_memory\`.\n\n## 9. Threats To Validity\n\n- Small number of labels.\n- Same-pattern leakage.\n- Single expert / no inter-rater agreement.\n- Limited domains/settings.\n- LLM stochasticity in the original VEGO-AI generation process.\n- Deterministic M4B-1 rules are intentionally conservative.\n- Human Judgment Memory examples are sparse.\n- M4B-2 is not implemented.\n- No live user study yet.\n\n## 10. Honest Thesis Claim\n\nYou can claim:\n\n> VEGO-AI was extended with a reusable human-judgment layer that supports selective review, structured feedback, reusable memory, advisory retrieval, leakage-aware evaluation, and non-destructive memory-informed comparison while preserving the original Agent 4 baseline.\n\nYou cannot yet claim:\n\n> The enhanced system improves classification accuracy.\n\n## 11. Missing Evidence\n\n- Fill EXP-002 expert labels for at least 20 rows, preferably all 27 current rows.\n- Ensure labels are held-out/generalization-safe.\n- Rerun the comparison with leakage-aware partitions.\n- Compute original vs memory-informed agreement against independent expert labels.\n- Add inter-rater/adjudication if possible.\n\n## Generated Files\n\n- \`${rel(path.join(outDir, "original_vs_memory_informed.csv"))}\`\n- \`${rel(path.join(outDir, "original_vs_memory_informed.md"))}\`\n- \`${rel(path.join(outDir, "evaluation_summary.json"))}\`\n- \`${rel(path.join(outDir, "leakage_distribution.svg"))}\`\n- \`${rel(path.join(outDir, "advice_strength_distribution.svg"))}\`\n- \`${rel(path.join(outDir, "classification_counts.svg"))}\`\n`;

  await fs.writeFile(reviewPath, review, "utf8");

  console.log(JSON.stringify({
    outDir: rel(outDir),
    strictReview: rel(reviewPath),
    baseline: summary.baseline_outputs,
    enhanced: summary.enhanced_outputs,
    accuracy: {
      all_labeled: summary.accuracy.all_labeled,
      generalization_safe_rows: summary.accuracy.generalization_safe.rows,
      paired: summary.accuracy.paired,
    },
    verdict: summary.strict_verdict,
  }, null, 2));
}

main().catch((error) => {
  console.error(error.stack || error.message || String(error));
  process.exit(1);
});
