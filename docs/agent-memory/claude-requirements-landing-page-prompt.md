# Claude Prompt — Bilingual Requirements Landing Page

Paste the block below into Claude (a fresh session or this one) to design and build a strict,
evidence-linked, Hebrew/English landing page showing every tracked supervisor requirement, its
real done/not-done status, and a link to the exact file where that status is proven. Two copies of
the same prompt follow — English and Hebrew — pick either; they ask for the same deliverable.
Status: prompt only, not yet executed. No landing page has been built from this yet.

## Prompt (English)

```text
Build a single, self-contained, static HTML landing page that presents every supervisor
requirement tracked in this project as one strict, evidence-linked list, with a toggle between
Hebrew and English. This is a "did we actually do it, and where's the proof" page for Ali to show
Iris/Arnon - it must be accurate, not persuasive. Do not soften, round up, or omit any status.

Read the two source files in full before building anything, and do not invent requirement text or
status from memory: docs/research/phd-proposal/iris-arnon-requirements.en.md and
docs/research/phd-proposal/iris-arnon-requirements.he.md. These two files are row-aligned by ID -
R-01..R-19, E1..E15, A08-01..A08-09, then an unprefixed 1..13+ block from the 2026-08-12 call, then
a "section 4" bullet list of open decisions requiring formal sign-off, then a "section 5" table of
hard evidence gates (EXP-005, medical G1-G6, QL-01-05). Confirm the row counts and exact current
text yourself by reading both files - do not assume the counts in this prompt are still current.

Hard rules, since this must be strict rather than persuasive: parse the two markdown files directly
at build time (regex or a markdown-table parser) rather than hand-transcribing a separate JSON copy
of the requirements, since a second copy could silently drift from the file supervisors and Ali
actually edit. Every requirement's status must be the literal status text from the source file, not
a rephrasing or a rounded-up verdict - if a status is "Partial", show Partial, not Done. A
requirement gets a clickable evidence link only when its status text contains an explicit "see
X.md" style citation; extract the filename, resolve it against wherever it actually lives (try
docs/research/phd-proposal/, docs/research/meetings/, literature/), and link to it with a path
relative to the generated HTML file's own location so the link works both opened locally and viewed
on GitHub. Before considering the build done, verify every generated link actually resolves to a
file that exists on disk; if a cited file is missing or ambiguous, do not silently drop it - render
the status text without a working link and print a build warning listing every unresolved citation.
Keep the four sections (R-/E-/A08-/unprefixed-08-12-numbers) as clearly separated, labeled groups
rather than merging them into one flat ID namespace, since the unprefixed 08-12 numbers can collide
with the other sections. Render section 4 (open decisions awaiting sign-off) and section 5 (the
fixed evidence-gate table) as their own distinct panels rather than forcing them into the
requirement-row template, since they are a different shape of information, not per-item statuses.
Add a top-line summary count computed from the real parsed data (for example "38 Done, 9 Open, 6
Ongoing, 4 Partial, 7 Info" with the actual numbers, not a guess) plus a status filter. Include a
visible disclaimer reusing this project's existing claim-boundary language - the "not a
supervisor-confirmed final decision" wording already at the top of both source files - stating that
this page mirrors the tracking file's self-reported status and does not independently re-verify
each item.

For the bilingual toggle: a single visible control switches the entire page - every label,
requirement, and status string - between Hebrew and English in place, no reload, no separate URL.
English text comes from the .en.md file and Hebrew text from the .he.md file, matched to each other
by ID. Switching to Hebrew must flip the page to RTL layout (dir="rtl", right-aligned text, mirrored
layout where it matters), not just swap text inside an LTR layout. If an ID in one language file has
no matching row in the other, do not silently fall back - flag it in the build warning the same way
as an unresolved file link, and pick a visible in-page fallback (such as showing the other
language's text with a small "no translation yet" marker) rather than leaving a blank row.

On technical approach: look first at scripts/build_thesis_progress_visual.py, this project's
existing pattern for a self-contained, dependency-free, embedded-data HTML generator (inline CSS,
embedded JSON, single output file, dark color-scheme), and follow its spirit rather than inventing a
new style - a Python build script under scripts/ that parses the two source markdown files, builds a
data structure, and renders one self-contained HTML file with everything inlined so it still works
opened offline. Also check docs/dashboards/ (the existing home for generated dashboards) and
scripts/build_supervisor_package.py, validate_supervisor_package.py, and dashboard-health.ps1 for
how this project already validates and publishes supervisor-facing artifacts, and fit into that
pipeline instead of creating an orphaned one-off file - name the output something like
docs/dashboards/requirements-landing-page.generated.html and the builder
scripts/build_requirements_landing_page.py unless a better-fitting location turns up. Add a --check
mode, matching the --check convention already used across this project's other build scripts, that
fails non-zero if the generated file would differ from what is committed, if any citation fails to
resolve, or if any ID is missing its Hebrew or English counterpart.

On the visual bar: this should read as clean and modern and information-dense rather than
decorative - one line per requirement by default (ID, a short status badge, the first ~80 characters
of the requirement text, an evidence-file icon or link), expandable per row for the full text rather
than a wall of prose. Status badges should use a small, consistent, accessible color set (Done
green, Open red or amber, Ongoing blue, Partial amber, Info grey) - for a second opinion on the
palette, use this project's own dataviz skill for the color formula and accessibility validation
rather than picking colors ad hoc. Group rows by the four sections, each collapsible, with that
section's own Done/Open/Ongoing/Partial/Info sub-count shown in its header, plus a simple text
filter box and a status-only filter such as "show only Open items".

Before declaring the work done: run the build script and open the generated HTML in a real browser
using this environment's Browser tool, and confirm the toggle actually flips language and RTL
layout, every status badge matches the literal source text, every evidence link that should exist
opens the right file, the summary counts match a manual spot-check against the source markdown, and
there are no console errors. Report any citation that could not be resolved to a real file, and any
ID missing its Hebrew or English counterpart, explicitly to Ali rather than quietly working around
it. Update docs/agent-memory (session-log.md, revert-log.md, and progress.md or decisions.md if
relevant) per this project's CLAUDE.md convention once the page is built and verified.

Do not start by writing HTML. Start by reading both source markdown files in full, then the
existing build_thesis_progress_visual.py and docs/dashboards/ conventions, and only then design the
data model and the build script.
```

## פרומפט (עברית)

```text
בנה עמוד נחיתה יחיד, עצמאי, סטטי ב-HTML, שמציג כל דרישת מנחים שמתועדת בפרויקט הזה כרשימה אחת
קפדנית ומקושרת לראיות, עם מתג מעבר בין עברית לאנגלית. זהו עמוד "האם באמת עשינו את זה, ואיפה
ההוכחה" שאלי יציג לאיריס וארנון - הוא חייב להיות מדויק, לא משכנע. אין לרכך, לעגל כלפי מעלה, או
להשמיט אף סטטוס.

קרא את שני קובצי המקור במלואם לפני שאתה בונה משהו, ואל תמציא טקסט דרישה או סטטוס מהזיכרון:
docs/research/phd-proposal/iris-arnon-requirements.en.md ו-
docs/research/phd-proposal/iris-arnon-requirements.he.md. שני הקבצים מיושרים שורה-לשורה לפי מזהה -
R-01..R-19, E1..E15, A08-01..A08-09, ואז בלוק ממוספר ללא קידומת 1..13+ משיחת 12.8.2026, ואז "סעיף
4" - רשימת החלטות פתוחות הדורשות אישור רשמי, ואז "סעיף 5" - טבלת שערי ראיות קשיחים (EXP-005, שערים
רפואיים G1-G6, חיפושי QL-01-05). אמת בעצמך את מספרי השורות והטקסט המדויק הנוכחי על ידי קריאת שני
הקבצים - אל תניח שהמספרים בפרומפט הזה עדיין עדכניים.

כללים קשיחים, מכיוון שזה חייב להיות קפדני ולא משכנע: פענח את שני קובצי ה-markdown ישירות בזמן
הבנייה (regex או פרסר טבלאות markdown) במקום להעתיק ידנית עותק JSON נפרד של הדרישות, מכיוון שעותק
שני עלול לסטות בשקט מהקובץ שהמנחים ואלי באמת עורכים. הסטטוס של כל דרישה חייב להיות טקסט הסטטוס
המילולי מקובץ המקור, לא ניסוח מחדש או פסיקה מעוגלת כלפי מעלה - אם הסטטוס הוא "חלקי", הצג חלקי, לא
בוצע. דרישה מקבלת קישור ראיה לחיצה רק כאשר טקסט הסטטוס שלה מכיל ציטוט מפורש בסגנון "ראו X.md"; חלץ
את שם הקובץ, פתור אותו מול היכן שהוא באמת נמצא (נסה docs/research/phd-proposal/,
docs/research/meetings/, literature/), וקשר אליו בנתיב יחסי למיקום קובץ ה-HTML שנוצר כך שהקישור
יעבוד גם כשנפתח מקומית וגם כשנצפה ב-GitHub. לפני שאתה מחשיב את הבנייה כגמורה, ודא שכל קישור שנוצר
אכן פותר לקובץ שקיים בפועל; אם קובץ מצוטט חסר או דו-משמעי, אל תשמיט אותו בשקט - הצג את טקסט הסטטוס
בלי קישור פעיל והדפס אזהרת בנייה שמפרטת כל ציטוט שלא נפתר. שמור את ארבעת הסעיפים
(R-/E-/A08-/מספרים לא-מקודדים מ-12.8) כקבוצות מופרדות וברורות במקום למזג אותם למרחב מזהים שטוח
אחד, מכיוון שהמספרים הלא-מקודדים מ-12.8 עלולים להתנגש עם הסעיפים האחרים. הצג את סעיף 4 (החלטות
פתוחות הממתינות לאישור) ואת סעיף 5 (טבלת שערי הראיות הקבועה) כפאנלים נפרדים משלהם במקום לכפות אותם
לתבנית שורת-הדרישה, מכיוון שהם סוג מידע שונה, לא סטטוסים לכל פריט. הוסף ספירת סיכום עליונה
המחושבת מהנתונים האמיתיים שפוענחו (למשל "38 בוצע, 9 פתוח, 6 מתמשך, 4 חלקי, 7 מידע" עם המספרים
האמיתיים, לא ניחוש) בתוספת סינון לפי סטטוס. כלול הבהרה נראית לעין שמשתמשת מחדש בניסוח גבול-הטענה
הקיים בפרויקט - הניסוח "לא החלטה סופית שאושרה על ידי המנחים" שכבר קיים בראש שני קובצי המקור -
שקובעת שהעמוד הזה משקף את הסטטוס המדווח-עצמית בקובץ המעקב ואינו מאמת כל פריט באופן עצמאי.

לגבי המתג הדו-לשוני: פקד גלוי לעין אחד מחליף את כל העמוד - כל תווית, דרישה, ומחרוזת סטטוס - בין
עברית לאנגלית במקום, בלי טעינה מחדש, בלי כתובת URL נפרדת. טקסט אנגלי מגיע מקובץ ה-.en.md וטקסט
עברי מקובץ ה-.he.md, מותאמים זה לזה לפי מזהה. מעבר לעברית חייב להפוך את פריסת העמוד ל-RTL
(dir="rtl", יישור טקסט לימין, פריסה משתקפת היכן שרלוונטי), לא רק להחליף טקסט בתוך פריסת LTR. אם
למזהה בקובץ שפה אחד אין שורה מקבילה בשני, אל תיפול בחזרה בשקט - סמן זאת באזהרת הבנייה באותו אופן
כמו קישור קובץ שלא נפתר, ובחר נפילה חזרה גלויה בעמוד (כמו הצגת הטקסט מהשפה השנייה עם סימון קטן
"אין עדיין תרגום") במקום להשאיר שורה ריקה.

לגבי הגישה הטכנית: הסתכל קודם על scripts/build_thesis_progress_visual.py, התבנית הקיימת של
הפרויקט למחולל HTML עצמאי, ללא תלויות, עם נתונים מוטמעים (CSS מוטמע, JSON מוטמע, קובץ פלט יחיד,
ערכת צבעים כהה), ועקוב אחר רוח התבנית הזו במקום להמציא סגנון חדש - סקריפט בנייה ב-Python תחת
scripts/ שמפענח את שני קובצי ה-markdown, בונה מבנה נתונים, ומרנדר קובץ HTML עצמאי אחד עם הכל מוטמע
כך שהוא עדיין עובד אופליין. בדוק גם את docs/dashboards/ (הבית הקיים ללוחות מחוונים) ואת
scripts/build_supervisor_package.py, validate_supervisor_package.py, ו-dashboard-health.ps1 כדי
לראות איך הפרויקט כבר מאמת ומפרסם תוצרים מול המנחים, והשתלב בצנרת הזו במקום ליצור קובץ יתום
חד-פעמי - תן לפלט שם כמו docs/dashboards/requirements-landing-page.generated.html ולבונה
scripts/build_requirements_landing_page.py אלא אם תמצא מיקום מתאים יותר. הוסף מצב --check,
בהתאם למוסכמה הקיימת בסקריפטי בנייה אחרים בפרויקט, שנכשל עם קוד שגיאה אם הקובץ שנוצר היה שונה
ממה שמאושר, אם ציטוט כלשהו לא נפתר, או אם למזהה כלשהו חסר מקביל עברי או אנגלי.

לגבי רף העיצוב: זה צריך להיראות נקי ומודרני וצפוף במידע ולא דקורטיבי - שורה אחת לדרישה כברירת
מחדל (מזהה, תג סטטוס קצר, כ-80 התווים הראשונים של טקסט הדרישה, אייקון או קישור לקובץ ראיה), הרחבה
לכל שורה לטקסט המלא במקום קיר של פרוזה. תגי סטטוס צריכים להשתמש בסט צבעים קטן, עקבי, נגיש (בוצע
ירוק, פתוח אדום או כתום, מתמשך כחול, חלקי כתום, מידע אפור) - לחוות דעת שנייה על הפלטה, השתמש בסקיל
dataviz של הפרויקט הזה לנוסחת הצבע ולאימות הנגישות במקום לבחור צבעים אד-הוק. קבץ שורות לפי ארבעת
הסעיפים, כל אחד ניתן לקיפול, עם ספירת המשנה בוצע/פתוח/מתמשך/חלקי/מידע של הסעיף מוצגת בכותרת שלו,
בתוספת תיבת סינון טקסט פשוטה וסינון לפי סטטוס בלבד כמו "הצג רק פריטים פתוחים".

לפני שמכריזים על סיום העבודה: הרץ את סקריפט הבנייה ופתח את קובץ ה-HTML שנוצר בדפדפן אמיתי באמצעות
כלי הדפדפן של הסביבה הזו, וודא שהמתג באמת מחליף שפה ופריסת RTL, שכל תג סטטוס תואם לטקסט המקור
המילולי, שכל קישור ראיה שאמור להתקיים באמת פותח את הקובץ הנכון, שספירות הסיכום תואמות בדיקת-מדגם
ידנית מול ה-markdown המקורי, ושאין שגיאות קונסולה. דווח על כל ציטוט שלא ניתן היה לפתור לקובץ אמיתי,
ועל כל מזהה שחסר לו מקביל עברי או אנגלי, במפורש לאלי במקום לעקוף את זה בשקט. עדכן את
docs/agent-memory (session-log.md, revert-log.md, ו-progress.md או decisions.md אם רלוונטי) לפי
מוסכמת ה-CLAUDE.md של הפרויקט הזה לאחר שהעמוד נבנה ואומת.

אל תתחיל בכתיבת HTML. התחל בקריאת שני קובצי המקור במלואם, ואז המוסכמות הקיימות של
build_thesis_progress_visual.py ו-docs/dashboards/, ורק אז תכנן את מודל הנתונים וסקריפט הבנייה.
```
