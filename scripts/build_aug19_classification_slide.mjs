#!/usr/bin/env node
/** Build the single-slide bilingual ACL-corpus classification artifact. */

import fs from "node:fs/promises";
import path from "node:path";
import { Presentation, PresentationFile } from "@oai/artifact-tool";

const SURVEY_URL = "https://aclanthology.org/2026.findings-acl.1811/";
const REPO_URL =
  "https://github.com/HenryPengZou/Awesome-Human-Agent-Collaboration-Interaction-Systems/tree/7b3ba9deefe99172748582f6025d995ccc2a6f86";

function argsFrom(argv) {
  const args = {};
  for (let index = 0; index < argv.length; index += 1) {
    if (!argv[index].startsWith("--")) continue;
    const key = argv[index].slice(2);
    const value = argv[index + 1];
    if (!value || value.startsWith("--")) throw new Error(`Missing value for --${key}`);
    args[key] = value;
    index += 1;
  }
  return args;
}

function required(args, key) {
  if (!args[key]) throw new Error(`Missing --${key}`);
  return path.resolve(args[key]);
}

async function writeBlob(target, blob) {
  await fs.mkdir(path.dirname(target), { recursive: true });
  await fs.writeFile(target, new Uint8Array(await blob.arrayBuffer()));
}

function addText(slide, text, position, style, name) {
  const box = slide.shapes.add({
    geometry: "textbox",
    name,
    position,
    fill: "none",
    line: { style: "solid", fill: "none", width: 0 },
  });
  box.text = text;
  box.text.style = { fontFamily: "Arial", ...style };
  return box;
}

async function main() {
  const args = argsFrom(process.argv.slice(2));
  const contentPath = required(args, "content");
  const outputPath = required(args, "output");
  const previewPath = required(args, "preview");
  const layoutPath = required(args, "layout");
  const content = JSON.parse(await fs.readFile(contentPath, "utf8"));
  const data = content.classification_slide;

  const presentation = Presentation.create({ slideSize: { width: 1280, height: 720 } });
  const slide = presentation.slides.add();
  slide.background.fill = "#F7F8FC";

  slide.shapes.add({
    geometry: "rect",
    name: "top-accent",
    position: { left: 0, top: 0, width: 1280, height: 10 },
    fill: "#7257D6",
    line: { style: "solid", fill: "none", width: 0 },
  });

  addText(
    slide,
    data.title,
    { left: 66, top: 42, width: 1148, height: 52 },
    { fontSize: 38, bold: true, color: "#17233C" },
    "title",
  );
  addText(
    slide,
    data.subtitle,
    { left: 68, top: 101, width: 1120, height: 46 },
    { fontSize: 18, color: "#4B5872" },
    "subtitle",
  );

  const chips = [
    ["Corpus | קורפוס", "116 works | 116 עבודות", "#E9E5FF", "#5039A7"],
    ["Human screening | סינון אנושי", "0/116", "#FFF1D6", "#8A5A00"],
    ["EXP-005", "0/24", "#FDE6E7", "#A02A32"],
    ["Medical readiness | מוכנות רפואית", "0/6", "#E8EDF5", "#40506B"],
  ];
  chips.forEach(([label, value, fill, color], index) => {
    const left = 68 + index * 287;
    slide.shapes.add({
      geometry: "roundRect",
      name: `chip-${index + 1}`,
      position: { left, top: 151, width: 268, height: 48 },
      fill,
      line: { style: "solid", fill, width: 1 },
      borderRadius: "rounded-lg",
    });
    addText(
      slide,
      `${label}\n${value}`,
      { left: left + 12, top: 157, width: 244, height: 36 },
      { fontSize: 13, bold: true, color },
      `chip-text-${index + 1}`,
    );
  });

  const headers = [
    "Display class\nמחלקת הצגה",
    "Derived mapping\nמיפוי נגזר",
    "Count\nכמות",
    "Interpretation boundary\nגבול פרשנות",
  ];
  const values = [headers, ...data.rows];
  const table = slide.tables.add({
    rows: values.length,
    columns: 4,
    left: 68,
    top: 216,
    width: 1144,
    height: 345,
    columnWidths: [176, 305, 154, 509],
    values,
  });
  table.styleOptions = { headerRow: true, bandedRows: false };
  table.borders.assign({ style: "solid", fill: "#CDD4E1", width: 1 });
  table.rows[0].height = 62;
  for (let row = 1; row < 5; row += 1) table.rows[row].height = 70;
  table.cells.block({ row: 0, column: 0, rowCount: 1, columnCount: 4 }).assign({
    fill: "#17233C",
    textStyle: { fontFamily: "Arial", fontSize: 15, bold: true, color: "#FFFFFF" },
    margins: { left: 10, right: 10, top: 8, bottom: 8 },
  });
  const rowFills = ["#EAF7F0", "#EAF2FB", "#F1F3F6", "#FFF4DC"];
  for (let row = 1; row < 5; row += 1) {
    table.cells.block({ row, column: 0, rowCount: 1, columnCount: 4 }).assign({
      fill: rowFills[row - 1],
      textStyle: { fontFamily: "Arial", fontSize: 14, color: "#1F2B43" },
      margins: { left: 10, right: 10, top: 8, bottom: 8 },
    });
    table.getCell(row, 0).text.style = {
      fontFamily: "Arial",
      fontSize: 15,
      bold: true,
      color: "#17233C",
    };
    table.getCell(row, 2).text.style = {
      fontFamily: "Arial",
      fontSize: 15,
      bold: true,
      color: "#17233C",
    };
  }

  addText(
    slide,
    `Boundary | גבול: ${data.boundary}`,
    { left: 68, top: 578, width: 1144, height: 54 },
    { fontSize: 15, color: "#4B5872" },
    "evidence-boundary",
  );
  addText(
    slide,
    "C2-ACL-01 | C2-ACL-03 | Repository commit 7b3ba9deefe9 | Ready for Ali review - not delivered",
    { left: 68, top: 650, width: 1144, height: 32 },
    { fontSize: 15, color: "#6A7489" },
    "source-footer",
  );

  slide.speakerNotes.textFrame.setText([
    "Present this as a prioritization view, not a completed review.",
    "High/Low/No are derived from Core/Relevant+Contextual/Peripheral machine labels.",
    "Missing means a taxonomy-schema theme is not encoded; it does not prove absence from papers.",
    "Human screening remains 0/116. EXP-005 remains 0/24. Medical readiness remains 0/6.",
    "[Sources]",
    SURVEY_URL,
    REPO_URL,
  ]);
  slide.speakerNotes.setVisible(true);

  const rendered = await presentation.export({ slide, format: "png", scale: 1 });
  await writeBlob(previewPath, rendered);
  const layout = await slide.export({ format: "layout" });
  await fs.mkdir(path.dirname(layoutPath), { recursive: true });
  await fs.writeFile(layoutPath, await layout.text(), "utf8");
  const pptx = await PresentationFile.exportPptx(presentation);
  await fs.mkdir(path.dirname(outputPath), { recursive: true });
  await pptx.save(outputPath);
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
