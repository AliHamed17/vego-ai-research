"""Shared rendering engine for the Hebrew Study 1 results-and-method package.

Every number in the package comes from one tracked JSON value file, and every value in that
file carries the tracked source it was read from, a verbatim quote from that source, and its
evidence class. Nothing is computed here from private evidence: this worktree does not mount
`external_data/`, so the package is reproducible from tracked files alone.

Two evidence classes are rendered in visually distinct colours and are never mixed inside one
figure, because merging them would let an engineering fixture be read as an empirical result:

  ARCHIVAL_RETROSPECTIVE_DESCRIPTIVE_EVIDENCE - a published descriptive value of the one
      accepted historical run, validated retrospectively.
  ENGINEERING_FIXTURE_NOT_SCIENTIFIC - deterministic instrumentation behaviour on synthetic
      input, which says nothing about any model.

The value accessor is fail-closed: an unknown key raises instead of rendering an empty cell,
so a typo can never silently become a missing number in a supervisor-facing document.
"""

from __future__ import annotations

import html
import json
import unicodedata
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]

PROSPECTIVE = "PROSPECTIVE EMPIRICAL EVIDENCE"
ARCHIVAL = "ARCHIVAL / RETROSPECTIVE DESCRIPTIVE EVIDENCE"
FIXTURE = "ENGINEERING-ONLY FIXTURE"
UNAVAILABLE = "NOT_AVAILABLE"

CHIP_HE = {
    PROSPECTIVE: "ראיה אמפירית פרוספקטיבית",
    ARCHIVAL: "ראיה ארכיונית־רטרוספקטיבית תיאורית",
    FIXTURE: "בדיקת הנדסה בלבד — אינה תוצאה מדעית",
    UNAVAILABLE: "אינו זמין — ולא אפס",
}
CHIP_CLASS = {PROSPECTIVE: "pro", ARCHIVAL: "arch", FIXTURE: "fix", UNAVAILABLE: "na"}


def esc(value: Any) -> str:
    return html.escape(str(value))


def normalise(text: str) -> str:
    """Fold whitespace and Unicode form so a quote can be matched inside its source file."""
    folded = unicodedata.normalize("NFC", text).replace("‑", "-")
    return " ".join(folded.split())


BASE_CSS = """
* { box-sizing: border-box; }
body { font-family:"Segoe UI",Arial,sans-serif; color:rgb(11,11,11); margin:0; line-height:1.34; }
h1 { font-size:15pt; margin:0 0 1mm; color:rgb(20,55,94); }
h2 { font-size:10.4pt; margin:2.6mm 0 1.2mm; padding-bottom:0.8mm; color:rgb(20,55,94);
     border-bottom:1.6px solid rgb(42,120,214); }
h3 { font-size:8.8pt; margin:1.8mm 0 0.8mm; color:rgb(20,55,94); }
p { margin:0 0 1.1mm; }
.sub { color:rgb(82,81,78); font-size:8pt; margin:0 0 2mm; }
.lead { font-size:9.4pt; margin:0 0 1.8mm; }
table { width:100%; border-collapse:collapse; font-size:7.6pt; margin:0 0 1mm; }
th,td { border:1px solid rgb(216,216,212); padding:0.9mm 1.2mm; text-align:right; vertical-align:top; }
th { background:rgb(244,245,243); font-weight:600; }
td.n, th.n { text-align:center; font-variant-numeric:tabular-nums; }
code { font-family:Consolas,monospace; font-size:7pt; background:rgb(244,245,243);
       padding:0 0.6mm; direction:ltr; unicode-bidi:isolate; }
.num { unicode-bidi:isolate; font-variant-numeric:tabular-nums; }
.f { font-family:Consolas,monospace; direction:ltr; unicode-bidi:isolate; font-size:8.6pt;
     display:block; text-align:center; background:rgb(244,245,243); border-radius:1mm;
     padding:1.1mm; margin:0 0 1mm; }
.chip { display:inline-block; font-size:6.8pt; font-weight:700; padding:0.5mm 1.6mm;
        border-radius:1mm; margin:0 0 1mm; }
.two { display:grid; grid-template-columns:1fr 1fr; gap:4mm; margin:2mm 0; }
.two h3 { margin:0 0 1mm; font-size:9pt; color:rgb(20,55,94); }
.two ul { margin:0; padding-inline-start:4mm; }
.chip.pro  { background:rgb(232,226,253); color:rgb(48,26,110); border:1px solid rgb(112,72,220); }
.chip.arch { background:rgb(226,238,253); color:rgb(20,55,94); border:1px solid rgb(42,120,214); }
.chip.fix  { background:rgb(253,236,229); color:rgb(150,58,18); border:1px solid rgb(235,104,52); }
.chip.pub  { background:rgb(230,244,233); color:rgb(20,80,40); border:1px solid rgb(60,150,90); }
.chip.def  { background:rgb(240,240,238); color:rgb(60,60,58); border:1px solid rgb(170,170,166); }
.chip.na   { background:rgb(238,238,238); color:rgb(70,70,70); border:1px solid rgb(150,150,150); }
.cap { font-size:6.9pt; color:rgb(82,81,78); margin:0.5mm 0 1.6mm; }
.cap b { color:rgb(40,40,38); }
.key  { background:rgb(238,244,252); border-right:3px solid rgb(42,120,214);
        padding:1.6mm 2.2mm; font-size:8.4pt; margin:0 0 1.8mm; }
.warn { background:rgb(253,242,238); border-right:3px solid rgb(235,104,52);
        padding:1.6mm 2.2mm; font-size:8pt; margin:0 0 1.8mm; }
.na   { background:rgb(242,242,242); border-right:3px solid rgb(140,140,140);
        padding:1.6mm 2.2mm; font-size:8pt; margin:0 0 1.8mm; }
.grid2 { display:grid; grid-template-columns:1fr 1fr; gap:3.4mm; align-items:start; }
.grid3 { display:grid; grid-template-columns:1fr 1fr 1fr; gap:2.6mm; align-items:start; }
.grid4 { display:grid; grid-template-columns:1fr 1fr 1fr 1fr; gap:2.2mm; align-items:start; }
.kpi { border:1px solid rgb(216,216,212); border-radius:1.8mm; padding:1.8mm; text-align:center; }
.kpi .v { font-size:13pt; font-weight:700; color:rgb(20,55,94); line-height:1.05; }
.kpi .l { font-size:7pt; color:rgb(82,81,78); margin-top:0.6mm; }
.kpi .d { font-size:6.4pt; color:rgb(120,118,114); margin-top:0.3mm; }
.row { display:flex; align-items:center; gap:1.6mm; margin:0.6mm 0; }
.lbl { flex:0 0 42mm; font-size:7.4pt; text-align:right; }
.track { flex:1 1 auto; position:relative; height:3.8mm; background:rgb(244,245,243);
         border-radius:0.8mm; }
.bar { position:absolute; top:0; right:0; height:100%; background:rgb(42,120,214);
       border-radius:0.8mm; }
.bar.fixbar { background:rgb(235,104,52); }
.bar.zero { background:rgb(170,170,166); width:0.8mm !important; }
.val { position:absolute; left:1.4mm; top:0.15mm; font-size:7pt; font-weight:700;
       color:rgb(20,55,94); }
.stage { border:1.4px solid rgb(42,120,214); border-radius:1.8mm; padding:1.6mm 1.4mm;
         background:rgb(250,252,255); text-align:center; }
.stage .n { display:inline-block; width:4.6mm; height:4.6mm; line-height:4.6mm; border-radius:50%;
            background:rgb(42,120,214); color:#fff; font-size:7pt; font-weight:700; }
.stage .t { font-size:7.8pt; font-weight:700; color:rgb(20,55,94); margin:0.7mm 0 0.3mm; }
.stage .s { font-size:6.7pt; color:rgb(82,81,78); }
.aside { border:1.4px dashed rgb(235,104,52); border-radius:1.8mm; padding:1.6mm;
         background:rgb(254,249,246); }
.ok { color:rgb(20,110,50); font-weight:700; }
.no { color:rgb(150,40,40); font-weight:700; }
ul, ol { margin:0 0 1.2mm; padding-right:4.6mm; padding-left:0; }
li { font-size:8pt; margin:0 0 0.5mm; }
tr, .key, .warn, .na, .kpi, .stage, .aside, figure { page-break-inside:avoid; }
.pb { page-break-before:always; }
"""

DOC_CSS = "@page { size:A4; margin:11mm 12mm 12mm; } body { font-size:8.4pt; }" + BASE_CSS
MAP_CSS = "@page { size:A4 landscape; margin:9mm 10mm; } body { font-size:8.6pt; }" + BASE_CSS


def num(value: Any) -> str:
    """Isolate a number used inside Hebrew prose, so the bidi algorithm cannot glue it."""
    return f'<span class="num">{esc(value)}</span>'


def formula(text: str) -> str:
    """A code expression is left-to-right text, not Hebrew, and is rendered as its own block."""
    return f'<span class="f">{esc(text)}</span>'


def chip(evidence_class: str) -> str:
    return (f'<span class="chip {CHIP_CLASS[evidence_class]}">'
            f'{esc(CHIP_HE[evidence_class])}</span>')


def caption(*, meaning: str, numerator: str, denominator: str, source: str, limitation: str) -> str:
    """The four fields every figure in this package must carry, plus its limitation."""
    return (f'<p class="cap"><b>מה מוצג:</b> {meaning} · <b>מונה:</b> {numerator} · '
            f'<b>מכנה:</b> {denominator} · <b>מקור:</b> <code>{esc(source)}</code> · '
            f'<b>מה אינו מוכיח:</b> {limitation}</p>')


def kpi(value: str, label: str, detail: str = "") -> str:
    tail = f'<div class="d">{esc(detail)}</div>' if detail else ""
    return f'<div class="kpi"><div class="v">{esc(value)}</div><div class="l">{esc(label)}</div>{tail}</div>'


def bars(rows: list[tuple[str, float, str]], *, maximum: float | None = None,
         fixture: bool = False) -> str:
    top = maximum if maximum else max((v for _, v, _ in rows), default=0) or 1
    out = []
    for label, value, shown in rows:
        width = (value / top * 100) if top else 0
        klass = "bar fixbar" if fixture else "bar"
        if value == 0:
            klass += " zero"
        out.append(
            f'<div class="row"><span class="lbl">{esc(label)}</span>'
            f'<span class="track"><span class="{klass}" style="width:{width:.1f}%"></span>'
            f'<span class="val">{esc(shown)}</span></span></div>'
        )
    return "".join(out)


def table(headers: list[str], rows: list[list[str]], *, numeric_from: int = 1,
          highlight: set[int] | None = None) -> str:
    highlight = highlight or set()
    head = "".join(
        f'<th class="n">{esc(h)}</th>' if i >= numeric_from else f"<th>{esc(h)}</th>"
        for i, h in enumerate(headers)
    )
    body = []
    for r, cells in enumerate(rows):
        tds = "".join(
            f'<td class="n">{c}</td>' if i >= numeric_from else f"<td>{c}</td>"
            for i, c in enumerate(cells)
        )
        shade = ' style="background:rgb(255,248,232)"' if r in highlight else ""
        body.append(f"<tr{shade}>{tds}</tr>")
    return f"<table><tr>{head}</tr>{''.join(body)}</table>"


def stages(items: list[tuple[str, str]]) -> str:
    """A numbered right-to-left flow. Numbers carry the order, so no arrow can be misread."""
    cells = "".join(
        f'<div class="stage"><span class="n">{i}</span>'
        f'<div class="t">{esc(title)}</div><div class="s">{esc(sub)}</div></div>'
        for i, (title, sub) in enumerate(items, 1)
    )
    cols = f"repeat({len(items)}, 1fr)"
    return (f'<div style="display:grid;grid-template-columns:{cols};gap:2mm;'
            f'direction:rtl">{cells}</div>')


def page(title: str, css: str, body: str, *, lang: str = "he") -> str:
    return (f'<!DOCTYPE html><html lang="{lang}" dir="rtl"><head><meta charset="utf-8">'
            f"<title>{esc(title)}</title><style>{css}</style></head><body>{body}</body></html>")
