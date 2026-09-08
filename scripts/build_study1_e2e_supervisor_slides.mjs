/**
 * Build the six-slide Hebrew supervisor deck for the evidence-bounded Study 1
 * E2E readout.  The content is deliberately limited to already-published
 * aggregate evidence and offline engineering checks.
 *
 * No provider, model, experiment, private evidence, or runtime behavior is
 * accessed by this builder.
 */

import fs from "node:fs/promises";
import path from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";

const SCRIPT_DIR = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(SCRIPT_DIR, "..");

function requiredEnvironment(name) {
  const value = process.env[name];
  if (!value || !path.isAbsolute(value)) {
    throw new Error(`${name} must name an absolute bundled-runtime path.`);
  }
  return path.resolve(value);
}

const SKILL_DIR = requiredEnvironment("SKILL_DIR");
const RUNTIME_NODE_MODULES = requiredEnvironment("RUNTIME_NODE_MODULES");
const RUNTIME_PYTHON = requiredEnvironment("RUNTIME_PYTHON");
const OUT = path.join(ROOT, "docs", "research", "phd-proposal", "2026-09-08-study1-e2e-supervisor-slides-he.pptx");
const BUILD = path.join(ROOT, ".codex-build-study1-e2e");
const STAGING = path.join(BUILD, "finalizer");
const PREVIEW_DIR = path.join(BUILD, "previews");

const { Presentation, PresentationFile } = await import(pathToFileURL(
  path.join(RUNTIME_NODE_MODULES, "@oai", "artifact-tool", "dist", "artifact_tool.mjs"),
).href);
const { resolvePresentationFont, finalizePresentation } = await import(pathToFileURL(
  path.join(SKILL_DIR, "container_tools", "artifact_tool_utils.mjs"),
).href);

const FONT = resolvePresentationFont({ fontFamily: "Calibri" });
const W = 1280;
const H = 720;
const M = 66;
const RTL_START = "\u202B";
const POP = "\u202C";

const C = Object.freeze({
  navy: "#102A43",
  blue: "#1864AB",
  teal: "#0B7285",
  green: "#2B8A3E",
  orange: "#D9480F",
  red: "#C92A2A",
  purple: "#7048E8",
  ink: "#243B53",
  muted: "#627D98",
  paper: "#F7FAFC",
  grid: "#D9E2EC",
  bluePale: "#E7F5FF",
  tealPale: "#E3FAFC",
  greenPale: "#EBFBEE",
  orangePale: "#FFF4E6",
  purplePale: "#F3F0FF",
});

function h(value) {
  return `${RTL_START}${value}${POP}`;
}

function cleanLine() {
  return { style: "solid", fill: "transparent", width: 0 };
}

function text(slide, name, value, position, style = {}) {
  const { rtl = true, ...textStyle } = style;
  const shape = slide.shapes.add({
    geometry: "textbox",
    name,
    position,
    fill: "transparent",
    line: cleanLine(),
  });
  shape.text = rtl ? h(value) : value;
  shape.text.style = {
    typeface: FONT,
    fontSize: 18,
    color: C.ink,
    alignment: style.alignment ?? "right",
    verticalAlignment: style.verticalAlignment ?? "middle",
    bold: Boolean(style.bold),
    autoFit: "shrinkText",
    ...textStyle,
  };
  return shape;
}

function box(slide, name, position, fill = "#FFFFFF", line = C.grid, radius = "rounded-xl") {
  return slide.shapes.add({
    geometry: "roundRect",
    name,
    position,
    fill,
    line: { style: "solid", fill: line, width: 1 },
    borderRadius: radius,
  });
}

function tag(slide, name, value, position, fill, size = 10) {
  const shape = slide.shapes.add({
    geometry: "roundRect",
    name,
    position,
    fill,
    line: cleanLine(),
    borderRadius: "rounded-lg",
  });
  shape.text = value;
  shape.text.style = {
    typeface: FONT,
    fontSize: size,
    color: "#FFFFFF",
    bold: true,
    alignment: "center",
    verticalAlignment: "middle",
    autoFit: "shrinkText",
  };
  return shape;
}

function line(slide, name, x, y, width, color = C.grid, lineWidth = 1) {
  return slide.shapes.add({
    geometry: "line",
    name,
    position: { left: x, top: y, width, height: 0 },
    fill: "transparent",
    line: { style: "solid", fill: color, width: lineWidth },
  });
}

function header(slide, number, title, subtitle) {
  slide.background.fill = C.paper;
  slide.shapes.add({
    geometry: "rect",
    name: `header-${number}`,
    position: { left: 0, top: 0, width: W, height: 74 },
    fill: C.navy,
    line: cleanLine(),
  });
  text(slide, `title-${number}`, title, { left: M, top: 14, width: W - 2 * M, height: 34 },
    { fontSize: 29, color: "#FFFFFF", bold: true });
  text(slide, `subtitle-${number}`, subtitle, { left: M, top: 46, width: W - 2 * M, height: 18 },
    { fontSize: 12, color: "#D9EAF7" });
  line(slide, `footer-line-${number}`, M, 680, W - 2 * M);
  text(slide, `footer-${number}`, `מחקר 1 | AirTravel | שקופית ${number} מתוך 6`,
    { left: M, top: 688, width: W - 2 * M, height: 17 }, { fontSize: 10, color: C.muted });
}

function note(slide, source) {
  slide.speakerNotes.textFrame.setText(source);
}

function metric(slide, name, x, y, value, label, micro, color) {
  box(slide, `${name}-box`, { left: x, top: y, width: 255, height: 92 }, "#FFFFFF", color);
  text(slide, `${name}-value`, value, { left: x + 16, top: y + 18, width: 76, height: 36 },
    { rtl: false, typeface: FONT, fontSize: 29, bold: true, alignment: "left", color });
  text(slide, `${name}-label`, label, { left: x + 96, top: y + 20, width: 145, height: 26 },
    { fontSize: 13, bold: true, color: C.navy });
  text(slide, `${name}-micro`, micro, { left: x + 96, top: y + 50, width: 145, height: 18 },
    { fontSize: 10, color: C.muted });
}

function setupTable(table, headerRow = 0) {
  table.styleOptions = { headerRow, bandedRows: true };
  table.borders.assign({ style: "solid", fill: C.grid, width: 1 });
  const allCells = table.cells.block({
    row: 0,
    column: 0,
    rowCount: table.rows.length,
    columnCount: table.columns.length,
  });
  allCells.textStyle.typeface = FONT;
  allCells.textStyle.fontSize = 13;
  allCells.textStyle.color = C.ink;
  allCells.textStyle.alignment = "right";
  allCells.textStyle.verticalAlignment = "middle";
  for (let row = 0; row < table.rows.length; row += 1) {
    for (let column = 0; column < table.columns.length; column += 1) {
      const cell = table.getCell(row, column);
      cell.fill = row === 0 ? C.navy : "#FFFFFF";
    }
  }
  const heading = table.cells.block({ row: 0, column: 0, rowCount: 1, columnCount: table.columns.length });
  heading.textStyle.typeface = FONT;
  heading.textStyle.fontSize = 14;
  heading.textStyle.color = "#FFFFFF";
  heading.textStyle.bold = true;
  heading.textStyle.alignment = "right";
  heading.textStyle.verticalAlignment = "middle";
}

function archiveBanner(slide, name, x, y, width) {
  tag(slide, name, "ARCHIVAL / RETROSPECTIVE DESCRIPTIVE EVIDENCE", { left: x, top: y, width, height: 20 }, C.purple, 8.6);
}

function fixtureBanner(slide, name, x, y, width) {
  tag(slide, name, "ENGINEERING_FIXTURE_NOT_SCIENTIFIC", { left: x, top: y, width, height: 19 }, C.orange, 7.7);
}

function engineeringOnlyBanner(slide, name, x, y, width) {
  tag(slide, name, "ENGINEERING_ONLY_NOT_SCIENTIFIC", { left: x, top: y, width, height: 19 }, C.teal, 7.7);
}

function slideOne(presentation) {
  const slide = presentation.slides.add();
  header(slide, 1, "מחקר 1: תהליך מקצה לקצה לקריאה מהירה", "חבילת מנחים בעברית | 8 בספטמבר 2026");
  text(slide, "slide1-main", "מה נבדק ומה גבול הטענה", { left: M, top: 102, width: W - 2 * M, height: 43 },
    { fontSize: 30, color: C.navy, bold: true });
  text(slide, "slide1-sub", "תיעוד שאלות ותשובות בין סוכני המערכת, עם תווית דיווח בלבד.",
    { left: M, top: 145, width: W - 2 * M, height: 27 }, { fontSize: 16, color: C.muted });

  const cards = [
    ["מה נבדק", "קורפוס ציבורי חיצוני", "PUBLIC_EXTERNAL", C.blue],
    ["המדגם", "4 מקרים שנבחרו באופן מכוון", "N = 4 | PURPOSIVE", C.teal],
    ["מה לא נבדק", "לא נתוני סטודנטים. לא מדגם מייצג.", "NO CHEERS / PARKWISE", C.orange],
  ];
  cards.forEach(([title, body, token, color], index) => {
    const x = M + index * 370;
    box(slide, `slide1-card-${index}`, { left: x, top: 210, width: 348, height: 163 }, "#FFFFFF", color);
    tag(slide, `slide1-tag-${index}`, token, { left: x + 20, top: 229, width: 150, height: 21 }, color, 8.4);
    text(slide, `slide1-card-title-${index}`, title, { left: x + 18, top: 264, width: 312, height: 29 },
      { fontSize: 20, color: C.navy, bold: true });
    text(slide, `slide1-card-body-${index}`, body, { left: x + 18, top: 302, width: 312, height: 43 },
      { fontSize: 15, color: C.ink });
  });

  box(slide, "slide1-boundary", { left: M, top: 420, width: W - 2 * M, height: 156 }, C.bluePale, C.blue);
  text(slide, "slide1-boundary-title", "גבול הטענה", { left: M + 22, top: 443, width: W - 2 * M - 44, height: 30 },
    { fontSize: 21, bold: true, color: C.navy });
  text(slide, "slide1-boundary-copy", "הריצה הארכיונית מתארת תהליך שנצפה בדיעבד. היא אינה מראה דיוק, תועלת, איכות, עליונות או הכללה.",
    { left: M + 22, top: 487, width: W - 2 * M - 44, height: 48 }, { fontSize: 17, color: C.ink });
  tag(slide, "slide1-status", "ARCHIVAL / RETROSPECTIVE DESCRIPTIVE EVIDENCE", { left: M + 22, top: 542, width: 280, height: 20 }, C.purple, 8);
  note(slide, "Sources: 2026-09-06 Study 1 execution receipt and preliminary-results report. Scope is retrospective descriptive evidence only.");
  return slide;
}

function slideTwo(presentation) {
  const slide = presentation.slides.add();
  header(slide, 2, "הזרימה מקצה לקצה", "נתונים, סוכנים, יומן Q&A, כלל, ותווית בדוח");
  text(slide, "slide2-copy", "התהליך מתועד. הוא אינו מתקן מקור, יעד, הנחיה או מודל.",
    { left: M, top: 105, width: W - 2 * M, height: 30 }, { fontSize: 18, color: C.navy, bold: true });
  const labels = [
    ["תווית בדוח", "LABEL", C.green],
    ["כלל ההתראה", "RULE", C.orange],
    ["יומן Q&A", "LOG", C.purple],
    ["סוכני המערכת", "AGENTS", C.teal],
    ["נתוני הקורפוס", "DATA", C.blue],
  ];
  const shapes = [];
  labels.forEach(([label, token, color], index) => {
    const x = 100 + index * 220;
    const card = box(slide, `slide2-step-${index}`, { left: x, top: 226, width: 164, height: 158 }, "#FFFFFF", color);
    const circle = slide.shapes.add({
      geometry: "ellipse",
      name: `slide2-circle-${index}`,
      position: { left: x + 56, top: 244, width: 52, height: 52 },
      fill: color,
      line: cleanLine(),
    });
    text(slide, `slide2-token-${index}`, token, { left: x + 59, top: 260, width: 46, height: 20 },
      { rtl: false, typeface: FONT, fontSize: 9, color: "#FFFFFF", bold: true, alignment: "center" });
    text(slide, `slide2-label-${index}`, label, { left: x + 12, top: 314, width: 140, height: 28 },
      { fontSize: 16, color: C.navy, bold: true, alignment: "center" });
    shapes.push(card);
  });
  for (let index = 0; index < shapes.length - 1; index += 1) {
    slide.shapes.connect(shapes[index], shapes[index + 1], {
      kind: "straight",
      fromSide: "right",
      toSide: "left",
      line: { style: "solid", fill: C.blue, width: 2 },
      head: { type: "arrow", width: "med", length: "med" },
    });
  }
  box(slide, "slide2-bottom", { left: M, top: 467, width: W - 2 * M, height: 111 }, C.tealPale, C.teal);
  const bottomRows = [
    "מתועדים: סוכן שואל, סוכן משיב, שאלה, תשובה, סבב וסיום אפיזודה.",
    "הכלל משתמש באותות Q&A קפואים בלבד.",
    "הפלט הוא תווית בדוח בלבד.",
  ];
  bottomRows.forEach((row, index) => {
    const marker = slide.shapes.add({ geometry: "ellipse", name: `slide2-marker-${index}`,
      position: { left: 1140, top: 493 + index * 25, width: 9, height: 9 }, fill: C.teal, line: cleanLine() });
    text(slide, `slide2-row-${index}`, row, { left: M + 26, top: 485 + index * 25, width: W - 2 * M - 54, height: 20 },
      { fontSize: 14, color: C.ink });
  });
  note(slide, "Sources: Study 1 signal dictionary and transparency data/log-contract materials. Diagram describes mechanism, not benefit.");
  return slide;
}

function slideThree(presentation) {
  const slide = presentation.slides.add();
  header(slide, 3, "איזה יומן משמש למה", "מקור השיח, עקבת מודל אפשרית, ביקורת ממשק ומנגנון שונות");
  const table = slide.tables.add({
    rows: 5,
    columns: 3,
    left: M,
    top: 125,
    width: W - 2 * M,
    height: 263,
    values: [
      [h("שימוש בדוח"), h("מה הוא מתעד"), "יומן"],
      [h("מקור השיח כאשר הוא מאומת"), h("שאלות, תשובות, סבבים וסיום אפיזודה"), "qa_events.jsonl"],
      [h("עקבת מודל אפשרית בלבד"), h("עקבת מודל אפשרית. אינה מקור לכלל"), "interaction_log.json"],
      [h("ביקורת ממשק בלבד"), h("פעולות ממשק. אינו מקור לשיח"), "user_actions.log"],
      [h("מנגנון שונות נפרד"), h("סיווג שונות נפרד. אינו קלט לכלל"), "Agent-4 output"],
    ],
    columnWidths: [300, 405, 377],
  });
  setupTable(table, true);
  box(slide, "slide3-alert", { left: M, top: 438, width: W - 2 * M, height: 137 }, C.greenPale, C.green);
  text(slide, "slide3-alert-title", "מה פירוש התראה", { left: M + 24, top: 458, width: W - 2 * M - 48, height: 28 },
    { fontSize: 21, bold: true, color: C.navy });
  text(slide, "slide3-alert-text", "התראה = מועמד לבדיקה אנושית בדוח.",
    { left: M + 24, top: 494, width: W - 2 * M - 48, height: 30 }, { fontSize: 23, bold: true, color: C.green });
  text(slide, "slide3-alert-boundary", "היא אינה שגיאה, אינה הוכחת תועלת, ואינה תיקון אוטומטי.",
    { left: M + 24, top: 533, width: W - 2 * M - 48, height: 24 }, { fontSize: 15, color: C.ink });
  note(slide, "Sources: Study 1 log-contract matrix and signal dictionary. No raw logs appear in this deck.");
  return slide;
}

function slideFour(presentation) {
  const slide = presentation.slides.add();
  header(slide, 4, "מה הכלל עושה", "כלל ההתראה מסווג אפיזודת שיח כתווית דיווח בלבד");
  tag(slide, "slide4-strong", "STRONG_ALERT = S1 OR S3 OR S7", { left: 95, top: 131, width: 350, height: 31 }, C.red, 13);
  tag(slide, "slide4-weak", "WEAK_ALERT = no strong AND (S2 OR S6)", { left: 474, top: 131, width: 420, height: 31 }, C.orange, 12);
  tag(slide, "slide4-none", "NO_ALERT = otherwise", { left: 923, top: 131, width: 260, height: 31 }, C.muted, 13);
  const cols = [
    ["S1", "ביטחון נמוך שדווח על ידי המודל", C.red],
    ["S3", "ראיה ריקה או חסרה בלבד", C.red],
    ["S7", "סיום במגבלת סבבים", C.red],
    ["S2", "ביטחון בינוני שדווח על ידי המודל", C.orange],
    ["S6", "יותר מסבב אחד", C.orange],
  ];
  cols.forEach(([signal, copy, color], index) => {
    const x = 83 + index * 226;
    box(slide, `slide4-signal-${index}`, { left: x, top: 220, width: 194, height: 130 }, "#FFFFFF", color);
    tag(slide, `slide4-signal-tag-${index}`, signal, { left: x + 15, top: 240, width: 42, height: 22 }, color, 11);
    text(slide, `slide4-signal-copy-${index}`, copy, { left: x + 15, top: 282, width: 164, height: 46 },
      { fontSize: 14, color: C.ink, alignment: "center" });
  });
  box(slide, "slide4-boundary", { left: M, top: 423, width: W - 2 * M, height: 145 }, C.orangePale, C.orange);
  text(slide, "slide4-boundary-title", "מה לא מפעיל התראה", { left: M + 22, top: 444, width: W - 2 * M - 44, height: 28 },
    { fontSize: 21, bold: true, color: C.navy });
  tag(slide, "slide4-context-tag", "C1 / C2 / C3 = CONTEXT ONLY", { left: M + 22, top: 480, width: 240, height: 23 }, C.muted, 9);
  text(slide, "slide4-boundary-copy", "משתני הקשר ופלטי מיפוי סמנטי אינם אותות לכלל. S3 מתייחס לקיום או לאורך שדה ראיה בלבד, ולא לאיכות הראיה.",
    { left: M + 278, top: 481, width: W - 2 * M - 300, height: 44 }, { fontSize: 16, color: C.ink });
  text(slide, "slide4-boundary-last", "הכלל אינו קובע תשובה נכונה או שגויה.", { left: M + 22, top: 536, width: W - 2 * M - 44, height: 20 },
    { fontSize: 15, color: C.orange, bold: true });
  note(slide, "Sources: frozen Detector-v1 signal contract. S1/S2 are model self-report; S3 is null/zero-length evidence only; S6 is round_count > 1.");
  return slide;
}

function slideFive(presentation) {
  const slide = presentation.slides.add();
  header(slide, 5, "שני מנגנונים, שתי יחידות ניתוח", "הדיווח וסיווג השונות נותרים נפרדים גם בדיווח");
  const left = 66;
  const cardWidth = 548;
  const right = 666;
  box(slide, "slide5-detector", { left: right, top: 126, width: cardWidth, height: 434 }, C.bluePale, C.blue);
  text(slide, "slide5-detector-title", "Detector-v1", { left: right + 22, top: 152, width: cardWidth - 44, height: 35 },
    { fontSize: 29, color: C.navy, bold: true });
  tag(slide, "slide5-detector-tag", "Q&A EPISODE", { left: right + 22, top: 199, width: 130, height: 23 }, C.blue, 10);
  const detectorItems = [
    ["יחידת ניתוח", "אפיזודת Q&A"],
    ["פעולה", "תווית מועמד לבדיקה בדוח"],
    ["תור", "לא נוצר תור"],
    ["שינוי אוטומטי", "לא מבוצע"],
  ];
  detectorItems.forEach(([label, value], index) => {
    const y = 252 + index * 64;
    text(slide, `slide5-detector-label-${index}`, label, { left: right + 22, top: y, width: cardWidth - 44, height: 20 },
      { fontSize: 13, color: C.muted });
    text(slide, `slide5-detector-value-${index}`, value, { left: right + 22, top: y + 21, width: cardWidth - 44, height: 25 },
      { fontSize: 17, color: C.ink, bold: index === 1 });
    line(slide, `slide5-detector-line-${index}`, right + 22, y + 52, cardWidth - 44, "#B6D9F5");
  });

  box(slide, "slide5-agent4", { left, top: 126, width: cardWidth, height: 434 }, C.purplePale, C.purple);
  text(slide, "slide5-agent4-title", "Agent-4", { left: left + 22, top: 152, width: cardWidth - 44, height: 35 },
    { fontSize: 29, color: C.navy, bold: true });
  tag(slide, "slide5-agent4-tag", "VARIABILITY CLASSIFICATION", { left: left + 22, top: 199, width: 220, height: 23 }, C.purple, 8.8);
  const agentItems = [
    ["יחידת ניתוח", "סיווג שונות"],
    ["פעולה", "בונה תור נפרד כאשר הכתיבה מצליחה"],
    ["מצב הקורפוס", "EXECUTED_THEN_BLOCKED"],
    ["מצב תור", "NOT_AVAILABLE"],
  ];
  agentItems.forEach(([label, value], index) => {
    const y = 252 + index * 64;
    text(slide, `slide5-agent4-label-${index}`, label, { left: left + 22, top: y, width: cardWidth - 44, height: 20 },
      { fontSize: 13, color: C.muted });
    text(slide, `slide5-agent4-value-${index}`, value, { left: left + 22, top: y + 21, width: cardWidth - 44, height: 25 },
      { rtl: index < 2, typeface: FONT, fontSize: 16, color: index >= 2 ? C.purple : C.ink, bold: index >= 2 });
    line(slide, `slide5-agent4-line-${index}`, left + 22, y + 52, cardWidth - 44, "#D5C8FF");
  });
  text(slide, "slide5-agent4-reason", "נבנתה רשומת ביקורת, אך סכמת המורשת חסמה את כתיבת התור.",
    { left: left + 22, top: 523, width: cardWidth - 44, height: 27 }, { fontSize: 11, color: C.purple });
  note(slide, "Sources: transparency correction package. Agent-4 queue status is NOT_AVAILABLE; its absence does not mean it was not triggered.");
  return slide;
}

function slideSix(presentation) {
  const slide = presentation.slides.add();
  header(slide, 6, "תמונה ארכיונית, בדיקות הנדסיות, והמשך", "שלושה סוגי מידע מוצגים בנפרד כדי למנוע מסקנת יתר");
  archiveBanner(slide, "slide6-archive-banner", M, 102, W - 2 * M);
  const x0 = M;
  metric(slide, "slide6-cases", x0, 138, "4", "מקרים שנבחרו", "מכנה: 4 מקרים", C.blue);
  metric(slide, "slide6-episodes", x0 + 277, 138, "3", "אפיזודות שלמות", "מכנה: 3 אפיזודות", C.teal);
  metric(slide, "slide6-qa", x0 + 554, 138, "44", "שאלות ותשובות", "44 שאלות + 44 תשובות", C.purple);
  metric(slide, "slide6-alerts", x0 + 831, 138, "3/3", "STRONG_ALERT", "מכנה: 3 אפיזודות", C.red);
  text(slide, "slide6-archive-source", "מקור: תוצאות Study 1 שפורסמו. עדות תיאורית בדיעבד בלבד.",
    { left: M, top: 241, width: W - 2 * M, height: 18 }, { fontSize: 11, color: C.muted });

  const checks = [
    ["מעטפת הכלל", "9/9", "מצבי בדיקה תאמו לכלל", "מקור: fixture | מכנה: 9", "מוכיח מסלולים של המכשור בלבד", C.orange, "fixture"],
    ["חוסן סדר אירועים", "500/500", "ערבובים שמרו על הסיווג", "מקור: יומן ארכיוני | מכנה: 500", "מוכיח אי-תלות בסדר בלבד", C.teal, "engineering"],
    ["כיול שמירת עלות", "43", "בקשות בקבלה הארכיונית", "מקור: קבלה ארכיונית | מכנה: 1", "מוכיח אריתמטיקת שמירה בלבד", C.purple, "engineering"],
  ];
  checks.forEach(([title, value, detail, source, limit, color, classification], index) => {
    const x = M + index * 374;
    box(slide, `slide6-check-${index}`, { left: x, top: 295, width: 352, height: 143 }, "#FFFFFF", color);
    if (classification === "fixture") {
      fixtureBanner(slide, `slide6-check-banner-${index}`, x + 13, 311, 326);
    } else {
      engineeringOnlyBanner(slide, `slide6-check-banner-${index}`, x + 13, 311, 326);
    }
    text(slide, `slide6-check-title-${index}`, title, { left: x + 14, top: 341, width: 324, height: 22 },
      { fontSize: 14, color: C.navy, bold: true });
    text(slide, `slide6-check-value-${index}`, value, { left: x + 14, top: 370, width: 90, height: 30 },
      { rtl: false, typeface: FONT, fontSize: 24, color, bold: true, alignment: "left" });
    text(slide, `slide6-check-detail-${index}`, detail, { left: x + 105, top: 374, width: 232, height: 20 },
      { fontSize: 11, color: C.ink });
    text(slide, `slide6-check-source-${index}`, source, { left: x + 14, top: 399, width: 323, height: 16 },
      { fontSize: 10, color: C.ink });
    text(slide, `slide6-check-limit-${index}`, limit, { left: x + 14, top: 420, width: 323, height: 12 },
      { fontSize: 9.2, color: C.muted });
  });
  box(slide, "slide6-open", { left: M, top: 488, width: W - 2 * M, height: 96 }, C.orangePale, C.orange);
  text(slide, "slide6-open-title", "מה נשאר פתוח", { left: M + 20, top: 506, width: W - 2 * M - 40, height: 25 },
    { fontSize: 19, color: C.navy, bold: true });
  text(slide, "slide6-open-copy", "קישור ראיות פרטיות | אמת־מידה ובוחנים אנושיים | תוצאת ON/OFF | טענה על דיוק או תועלת",
    { left: M + 20, top: 546, width: W - 2 * M - 40, height: 22 }, { fontSize: 15, color: C.ink });
  note(slide, "Sources: archival Study 1 receipt/results and 2026-09-08 offline instrument addendum. Only the first check is ENGINEERING_FIXTURE_NOT_SCIENTIFIC.");
  return slide;
}

async function build() {
  if (await fs.stat(OUT).catch(() => undefined)) {
    throw new Error(`Refusing to overwrite existing final deck: ${OUT}`);
  }
  await fs.mkdir(STAGING, { recursive: true });
  await fs.mkdir(PREVIEW_DIR, { recursive: true });
  await fs.mkdir(path.dirname(OUT), { recursive: true });

  const presentation = Presentation.create({ slideSize: { width: W, height: H } });
  const slides = [
    slideOne(presentation),
    slideTwo(presentation),
    slideThree(presentation),
    slideFour(presentation),
    slideFive(presentation),
    slideSix(presentation),
  ];

  for (let index = 0; index < slides.length; index += 1) {
    const currentSlide = slides[index];
    const preview = await presentation.export({ slide: currentSlide, format: "png", scale: 2 });
    await fs.writeFile(path.join(PREVIEW_DIR, `slide-${String(index + 1).padStart(2, "0")}.png`), new Uint8Array(await preview.arrayBuffer()));
    const layout = await currentSlide.export({ format: "layout" });
    await fs.writeFile(path.join(PREVIEW_DIR, `slide-${String(index + 1).padStart(2, "0")}.layout.json`), await layout.text());
  }

  const candidatePath = path.join(STAGING, "candidate.pptx");
  await (await PresentationFile.exportPptx(presentation)).save(candidatePath);
  const receiptPath = path.join(BUILD, "presentation-validation.json");
  await finalizePresentation({
    explicitTotalSlideCount: 6,
    requiredNativeTableOwnerSlides: [3],
    requiredNativeChartOwnerSlides: [],
    workspaceDir: ROOT,
    candidatePath,
    finalPath: OUT,
    pythonExecutable: RUNTIME_PYTHON,
    integrityValidatorPath: path.join(SKILL_DIR, "container_tools", "inspect_presentation_package_integrity.py"),
    layoutValidatorPath: path.join(SKILL_DIR, "container_tools", "inspect_presentation_layout_geometry.py"),
    layoutArgs: [
      "--expected-slide-size-emu", "12192000,6858000",
      "--validate-heading-fit",
      "--require-native-table-slide", "3",
    ],
    fontPolicy: { basis: "design", families: ["Calibri"] },
    verifyArtifactToolImport: true,
    receiptPath,
  });
  const inspect = await presentation.inspect({ kind: "slide,textbox,shape,table,notes", maxChars: 20000 });
  await fs.writeFile(path.join(BUILD, "presentation-inspect.ndjson"), inspect.ndjson, "utf8");
  console.log(OUT);
}

await build();
