# Anticipated Q&A — Aug-12 Supervisor Meeting

# שאלות ותשובות צפויות — פגישת מנחים 12 באוגוסט

Prep aid for Ali. Likely questions from Iris and Arnon, with crisp, **evidence-honest** answers.
Every answer stays inside the claim boundary (no approval claimed; EXP-005 0 supplied labels / 27 blind /
24 generalization-safe, gate needs ≥20; medical 0/6; searches not run; wording provisional). Do not
promise results that don't exist — the strength here is honesty about a proposal-stage project.

מסמך הכנה לעלי. שאלות צפויות מאיריס וארנון, עם תשובות תמציתיות **וכנות מבחינת ראיות**. כל תשובה
נשארת בתוך גבול הטענות (אין טענת אישור; EXP-005; רפואה 0/6; החיפושים לא רצו; ניסוח זמני).

---

## 1. "Isn't this just describing your VEGO-AI system rather than a research question?" (Arnon's core critique)

**EN:** No — that conflation is exactly what we fixed after 5 August. The question is domain-neutral: it
asks *how* human judgment can be captured, governed, and used to support variability exploration
reliably (note: "reused" was deliberately dropped from the headline and moved into SQ2). VEGO-AI is the
motivating case and the platform I build on, not the object of study — Chapter 3 §3.7 states this
explicitly, and the gap section argues why the question is open, not why my design is good.

**HE:** לא — בדיוק את הערבוב הזה תיקנּו אחרי 5 באוגוסט. השאלה ניטרלית-תחום: היא שואלת *כיצד* ניתן
ללכוד, לנהל ולהשתמש בשיפוט אנושי כדי לתמוך בחקר שונוּת באופן אמין (הערה: "שימוש חוזר" הוסר במכוון
מהכותרת והועבר ל-SQ2). VEGO-AI הוא מקרה המבחן והפלטפורמה, לא מושא המחקר (פרק 3, §3.7).

## 2. "Where is your evidence that this works?"

**EN:** At proposal stage I have mechanism and architecture readiness — the capture, memory, advisory,
and non-destructive comparison layers are implemented and tested. I deliberately do **not** claim accuracy,
generalization, or effort reduction: EXP-005 has 0 supplied expert labels of 24 generalization-safe
candidates (the gate needs ≥20), so those results are not yet computable. The evaluation is designed,
leakage-controlled, and gated — that design is itself a contribution.

**HE:** בשלב ההצעה יש מוכנות מנגנון וארכיטקטורה — שכבות הלכידה, הזיכרון, הייעוץ וההשוואה הלא-הרסנית
ממומשות ונבדקו. במכוון אינני טוען דיוק/הכללה/הפחתת מאמץ: ל-EXP-005 יש 0 תיוגי מומחה מתוך 24
מועמדים בטוחים-להכללה (השער דורש ≥20). ההערכה מעוצבת, מבוקרת-דליפה, ומגודרת — והעיצוב עצמו תרומה.

## 3. "Is this doctoral-scale? What's the novelty?"

**EN:** The candidate novelty is a *governed lifecycle* that connects three problems usually studied
separately: when to request expert judgment (SQ1), how to represent/validate/store it for safe reuse
(SQ2), and how to classify and evaluate what transfers across domains (SQ3). Three studies, three papers.
Novelty is a candidate claim until the literature review confirms it — I'm not asserting it as established.

**HE:** החידוש המועמד הוא *מחזור-חיים מבוקר* שמחבר שלוש בעיות שנחקרות בנפרד: מתי לבקש שיפוט מומחה
(SQ1), כיצד לייצג/לאמת/לאחסן לשימוש חוזר בטוח (SQ2), וכיצד לסווג ולהעריך מה עובר בין תחומים (SQ3).
שלושה מחקרים, שלושה מאמרים. החידוש הוא טענה מועמדת עד לאישור בסקר הספרות.

## 4. "How is SQ2 different from RLHF or a knowledge base?"

**EN:** Both extremes destroy properties expert assessment judgment needs. A knowledge base is static and
detached from the case; RLHF absorbs feedback into weights where it's uninspectable, unattributable, and
irrevocable. SQ2 designs the governed middle: judgment kept case-grounded, scoped, contestable, and
authority-bearing — validated, reconciled, stored with provenance, and reused only within its scope.

**HE:** שני הקצוות הורסים תכונות שנדרשות לשיפוט הערכה מומחה. בסיס-ידע סטטי ומנותק מהמקרה; RLHF בולע
משוב אל תוך המשקלים באופן בלתי-ניתן-לבדיקה, לא-משויך ובלתי-הפיך. SQ2 מעצב את האמצע המבוקר: שיפוט
מעוגן-מקרה, בעל-היקף, בר-ערעור ובעל-סמכות — מאומת, מתואם, מאוחסן עם מקור, ומשומש רק בתוך היקפו.

## 5. "Why start with software/modeling instead of medicine?"

**EN:** Domain-transfer behavior is unproven, so I evaluate first in the domain where I already have a
baseline and data (software/modeling), then test transfer. Medicine is a *conditional* extension (Plan A),
gated on six entry gates — use-case, people, authorization, ethics/privacy, environment, protocol. Starting
in medicine would make the doctorate depend on partner access I don't yet control.

**HE:** התנהגות ההעברה בין תחומים לא מוכחת, לכן אני מעריך תחילה בתחום שבו כבר יש בסיס ונתונים
(תוכנה/מודלים), ואז בודק העברה. רפואה היא הרחבה *מותנית* (תוכנית A), מגודרת בשישה שערי כניסה. התחלה
ברפואה הייתה הופכת את הדוקטורט לתלוי בגישת שותף שעדיין אינה בשליטתי.

## 6. "What if the medical partner or data falls through?"

**EN:** Plan B answers every research question without medical data — a second authorized software/modeling
context (another dataset, diagram family, institution, or reviewer panel). The doctoral contribution is
preserved either way. The 26 August checkpoint (an internal control date, not yet supervisor-approved) is
when Plan B becomes the committed September route if any gate lacks an owner, evidence path, or feasible date.

**HE:** תוכנית B עונה על כל שאלות המחקר בלי נתונים רפואיים — הקשר תוכנה/מודלים שני ומורשה. התרומה
נשמרת כך או כך. נקודת הבקרה 26.8 (תאריך פנימי, טרם מאושר) היא המועד שבו B הופכת למסלול ספטמבר
המחויב אם שער כלשהו חסר בעל תפקיד, מסלול ראיות, או תאריך ריאלי.

## 7. "How will you evaluate transfer honestly — won't reused judgment just leak?"

**EN:** That's why SQ3's core is a classification: separating uncertainty that is *domain-specific* (must
stay confined) from a *general capability gap* (a transfer candidate) — Arnon's own example, failing to
identify actors/use-cases, is a general gap, not a domain one. Evaluation uses independent labels, explicit
leakage controls between the context that produced a judgment and the one it's tested in, and pre-registered
success criteria.

**HE:** לכן ליבת SQ3 היא סיווג: הפרדת אי-ודאות *ספציפית-לתחום* (חייבת להישאר מוגבלת) מ*פער יכולת כללי*
(מועמד להעברה) — הדוגמה של ארנון, כשל בהגדרת אקטורים/use-cases, היא פער כללי. ההערכה משתמשת בתיוגים
עצמאיים, בקרות דליפה מפורשות, וקריטריוני הצלחה שנרשמו מראש.

## 8. "What's your literature coverage — have you done the review?"

**EN:** The searches are protocol-frozen (QL-01..QL-05) but **not yet run**, so I make no
review-completeness or novelty claim. What exists is a per-question tagging and an honest coverage-gap map:
RQ1 thin, RQ2 tool-heavy, RQ3 currently empty — each gap already mapped to the query or snowballing that
closes it. Running the searches against the confirmed wording is the natural next task.

**HE:** החיפושים קפואים בפרוטוקול (QL-01..QL-05) אך **טרם הורצו**, לכן אין טענת שלמות או חידוש. קיים
תיוג לפי שאלה ומפת פערים כנה: RQ1 דל, RQ2 עתיר-כלים, RQ3 ריק — כל פער כבר ממופה לשאילתה שסוגרת אותו.

## 9. "Is the 3-year timeline realistic?"

**EN:** The plan is written in ~3-month semester-aligned blocks over a 3-year horizon (not month-by-month,
per your guidance). This week is on track — Chapter 3 drafted, literature tagged, and the Drive being
shared with you — which is the evidence the cadence is being kept. Dates beyond the confirmed cadence are
working targets, not official university deadlines.

**HE:** התוכנית כתובה בבלוקים של כ-3 חודשים מיושרי-סמסטר על אופק 3 שנים (לא חודש-חודש, לפי הנחייתכם).
השבוע בעיצומו — פרק 3 נוסח, הספרות תויגה, והדרייב בתהליך שיתוף אתכם — עדות לשמירת הקצב. תאריכים מעבר
לקצב המאושר הם יעדי עבודה, לא מועדים רשמיים.

## 10. "What exactly do you need us to decide today?"

**EN:** Six mandatory decisions: the umbrella RQ wording, SQ1–SQ3 wording, the three-study mapping, the
Plan A/Plan B boundary, that every RQ stays answerable under Plan B, and the evidence-boundary wording.
Four more if time allows: the 26-Aug fallback date, initial literature scope, the MIMIC metadata boundary,
and assigning owners for medical feasibility and university-process verification.

**HE:** שש החלטות מחייבות: ניסוח שאלת-העל, ניסוח SQ1–SQ3, מיפוי שלושת המחקרים, גבול תוכנית A/B, שכל
שאלה נשארת ניתנת-למענה בתוכנית B, וניסוח גבול הראיות. עוד ארבע אם יורשה הזמן: תאריך 26.8, תחום
הספרות, גבול MIMIC, והקצאת בעלי תפקיד.

## 11. "Can we trust the wording — where did it come from?"

**EN:** The wording is my reconstruction of the live edits from the 5 August call, from a machine
transcript with inferred (undiarized) speakers. That's why exact-wording sign-off is the first decision
today (`D-RQ-01`/`D-RQ-02`): I want you to confirm or correct it against your own memory of the call before
it's treated as final. I quote nothing verbatim from the transcript.

**HE:** הניסוח הוא שחזור שלי של העריכות החיות מ-5 באוגוסט, מתמליל מכונה עם דוברים משוערים. לכן אישור
הניסוח המדויק הוא ההחלטה הראשונה היום — שתאשרו או תתקנו מול הזיכרון שלכם לפני שהוא נחשב סופי. איני
מצטט דבר מילולית מהתמליל.

## 12. "What's the single most important open risk?"

**EN:** That the framework's *effectiveness* is unproven until the independent-label evaluation runs — and
that evaluation depends on getting real expert labels (EXP-005) and, for the medical arm, six gates that
are institutional facts outside my control. Both are explicitly managed: Plan B removes the medical
dependency, and the labeling is designed and tooled, waiting on expert time. The proposal does not depend
on a positive result; negative results remain valid outcomes.

**HE:** שהיעילות של המסגרת אינה מוכחת עד שההערכה עם התיוגים העצמאיים תרוץ — וזו תלויה בתיוגי מומחה
אמיתיים (EXP-005) ובשישה שערים מוסדיים מחוץ לשליטתי (לזרוע הרפואית). שניהם מנוהלים במפורש: תוכנית B
מסירה את התלות הרפואית, והתיוג מעוצב ומצויד וממתין לזמן מומחה. ההצעה אינה תלויה בתוצאה חיובית.

---

*Grounding: `docs/research/phd-proposal/chapter-3-gap-and-research-questions-draft.md`,
`docs/research/phd-proposal/three-study-contract.md`, `docs/research/meetings/2026-08-05-supervisor-meeting.md`,
`docs/research/meetings/2026-08-05-supervisor-presentation-checklist.md` (forbidden-claims list). Answers
are prep, not commitments; the confirmation protocol governs what is actually decided.*
