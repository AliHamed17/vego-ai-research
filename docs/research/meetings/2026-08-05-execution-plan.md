# Execution Plan (Bilingual) - Week of 2026-08-05 to 2026-08-12

תוכנית ביצוע (דו-לשונית) - השבוע שבין 5.8.2026 ל-12.8.2026

## Purpose / מטרת המסמך

**EN:** This is a **derived planning document**, not a verbatim record. It translates the requirements captured in [`2026-08-05-supervisor-meeting.md`](2026-08-05-supervisor-meeting.md) (the canonical, machine-derived evidence matrix - English only) into a concrete, sequenced, bilingual "how do I actually do this" plan for the week before the August 12 follow-up. Every requirement below links back to its source item (`E#`/`A08-#`) in the canonical record. If this plan and the canonical record ever disagree, the canonical record (and, above that, the actual recording) wins.

**HE:** זהו **מסמך תכנון נגזר**, ולא רשומה מילולית. המסמך מתרגם את הדרישות שתועדו ב-[`2026-08-05-supervisor-meeting.md`](2026-08-05-supervisor-meeting.md) (הרשומה הקנונית, הנגזרת ממכונה - באנגלית בלבד) לכדי תוכנית פעולה קונקרטית, מסודרת לפי סדר עדיפויות, ודו-לשונית, לשבוע שלפני פגישת ה-12 באוגוסט. כל דרישה למטה מקושרת לסעיף המקור שלה (`E#`/`A08-#`) ברשומה הקנונית. אם מסמך זה סותר את הרשומה הקנונית - הרשומה הקנונית (ומעליה, ההקלטה עצמה) קובעת.

**Status legend used below / מקרא הסטטוסים:** 🔴 blocking / חוסם — 🟡 this week / השבוע — 🟢 background, don't start yet / ברקע, אין להתחיל עדיין.

---

## 🔴 Step 0 - Recover the settled research-question wording

## שלב 0 - שחזור הניסוח הסופי של שאלות המחקר

**EN:** Everything else this week depends on this. During the call (`00:13-00:44`), you and Iris/Arnon dictated live edits into an AI chat (referred to on the call as "Claude") to redraft the main RQ and SQ1-3. The ASR cannot reconstruct the exact final sentence from that fast, overlapping dictation (see `E7`-`E10`, all flagged `Needs transcript verification`). **Before writing Chapter 3, find that chat session or whatever you pasted the final version into**, and treat it as the source of truth over both this plan and the meeting record's draft reconstruction. If you can't find it, budget 15 minutes to re-listen to `00:26:29-00:44:37` in the recording and reconcile it against the draft wording in `docs/video1638342429.transcript.en.md` §5.

**HE:** כל שאר השבוע תלוי בשלב הזה. במהלך השיחה (`00:13-00:44`), אתה יחד עם איריס וארנון הכתבתם בזמן אמת עריכות לתוך צ'אט AI (המכונה בשיחה "קלוד") כדי לנסח מחדש את שאלת המחקר הראשית ואת שלוש תתי-השאלות. תמלול המכונה אינו יכול לשחזר את המשפט הסופי המדויק מתוך ההכתבה המהירה והחופפת הזו (ראו `E7`-`E10`, המסומנים כולם `Needs transcript verification`). **לפני כתיבת פרק 3, מצא את שיחת הצ'אט הזו או כל מקום אחר שבו הדבקת את הניסוח הסופי**, והתייחס אליו כמקור האמת - מעל התוכנית הזו ומעל השחזור הטיוטתי ברשומת הפגישה. אם אינך מוצא אותו, הקדש כ-15 דקות להאזנה חוזרת לקטע `00:26:29-00:44:37` בהקלטה ולהשוואה מול הניסוח הטיוטתי במסמך `docs/video1638342429.transcript.en.md` סעיף 5.

---

## 🔴 Step 1 - Write Chapter 3 (Gap & Research Question) in full

## שלב 1 - כתיבת פרק 3 (פער ושאלת מחקר) במלואו

*Source: `A08-01`, `A08-02`, `E3`-`E12`*

**EN:** This is the single deliverable Iris named explicitly as the goal for Aug 12 (`E15`). Concrete sub-steps:
1. Drop in the settled RQ + SQ1-3 wording from Step 0.
2. Write the **gap** narrative that motivates the three sub-questions - Arnon's critique (`E4`) was that the solution and the question were blurred, so make sure the gap section argues *why this is an open research question*, not *why your Agentic-AI design is a good idea*.
3. For SQ2, make sure the wording explicitly references "core reasoning" and carries an evaluation-criteria clause in the same style as SQ1/SQ3 (`E9`) - correctness vs. completeness, no unsafe generalization or loss of human authority.
4. For SQ3, fold in Arnon's classification framing: distinguish uncertainty that is genuinely domain-specific from uncertainty that is a general capability gap (`E12`) - the actor/use-case example is a ready-made illustration.
5. Keep the RQs domain-neutral in wording (`E13`) - domain framing (SE vs. medical) belongs in Research Methodology, not in the RQ text itself.

**HE:** זהו התוצר היחיד שאיריס ציינה במפורש כמטרה לפגישת ה-12 באוגוסט (`E15`). שלבי ביצוע קונקרטיים:
1. הכנס את הניסוח הסופי של שאלת המחקר הראשית ושלוש תתי-השאלות משלב 0.
2. כתוב את קטע ה**פער (gap)** שמניע את שלוש תתי-השאלות - הביקורת של ארנון (`E4`) הייתה שהפתרון ושאלת המחקר מטושטשים זה בזה, אז ודא שקטע הפער מסביר *מדוע זו שאלת מחקר פתוחה*, ולא *מדוע העיצוב האג'נטי שלך הוא רעיון טוב*.
3. בתת-שאלה 2, ודא שהניסוח מתייחס במפורש ל"core reasoning" וכולל סעיף קריטריוני-הערכה באותו סגנון כמו תתי-שאלות 1 ו-3 (`E9`) - איזון בין נכונות לשלמות, ללא הכללת-יתר לא בטוחה או אובדן סמכות אנושית.
4. בתת-שאלה 3, שלב את מסגרת הסיווג של ארנון: הבחנה בין אי-ודאות שהיא אכן ספציפית לתחום לבין אי-ודאות שהיא פער יכולת כללי (`E12`) - הדוגמה של הגדרת אקטורים/use-cases היא איור מוכן מראש.
5. שמור על ניסוח שאלות המחקר ניטרלי מבחינת תחום (`E13`) - מיקוד תחומי (הנדסת תוכנה מול רפואה) שייך לפרק המתודולוגיה, לא לטקסט של שאלות המחקר עצמן.

---

## 🟡 Step 2 - Build the per-RQ literature spreadsheet

## שלב 2 - בניית גיליון הספרות לפי שאלת מחקר

*Source: `A08-03`*

**EN:** Extend the literature worksheet already on the Drive (per §2 of the transcript walkthrough). Add one column tagging each source as RQ1 / RQ2 / RQ3 / general. Use this pass to actively check for coverage gaps - Iris's stated purpose is "so we can see we're covering all the relevant literature," not just logging what you already had.

**HE:** הרחב את גיליון הספרות שכבר קיים בדרייב (לפי סעיף 2 בסקירת התמלול). הוסף עמודה אחת שמתייגת כל מקור כ-RQ1 / RQ2 / RQ3 / כללי. נצל מעבר זה כדי לבדוק באופן אקטיבי פערי כיסוי - המטרה שאיריס ציינה היא "כדי שנוכל לראות שאנחנו מכסים את כל הספרות הרלוונטית", ולא רק לתעד מה שכבר היה לך.

---

## 🟡 Step 3 - Share the Drive

## שלב 3 - שיתוף הדרייב

*Source: `A08-05`*

**EN:** Share the project Drive with Iris and Arnon with edit or comment access, as agreed on the call. Do this early in the week, not the night before Aug 12 - Iris said she'd send a check-in email before Sunday (`A08-07`), so access should be live before that lands.

**HE:** שתף את הדרייב של הפרויקט עם איריס וארנון, עם הרשאת עריכה או הערות, כפי שסוכם בשיחה. עשה זאת מוקדם בשבוע, לא בלילה שלפני ה-12 באוגוסט - איריס אמרה שתשלח מייל בדיקת-התקדמות לפני יום ראשון (`A08-07`), כך שהגישה צריכה להיות פעילה לפני שהמייל מגיע.

---

## 🟡 Step 4 - Maintain the two working documents

## שלב 4 - תחזוקת שני מסמכי העבודה

*Source: `A08-06`*

**EN:** Keep the actual proposal in Word (confirmed - not Overleaf), and a **separate** short tracking/status document showing where each item stands. Update the tracking document as you complete Steps 1-3, so it's current when Iris's email arrives and when you present at Aug 12.

**HE:** שמור את ההצעה עצמה בוורד (כפי שאושר - לא באוברליף), ומסמך **נפרד** קצר למעקב/סטטוס שמראה איפה עומד כל סעיף. עדכן את מסמך המעקב תוך כדי השלמת שלבים 1-3, כך שיהיה עדכני כשמייל של איריס יגיע וכשתציג בפגישת ה-12 באוגוסט.

---

## 🟢 Step 5 - Start *thinking about* sections 2 and 4 (do not write yet)

## שלב 5 - להתחיל *לחשוב* על פרקים 2 ו-4 (אין לכתוב עדיין)

*Source: `A08-04`, `E13`*

**EN:** Iris was explicit: don't start executing the full literature survey (§2) or the research-artifact design (§4) yet. The one useful thing to do now is start informal notes on **what exactly the artifact is per RQ** - an architecture? a framework? a classification scheme? - since that question was raised but not answered on the call, and having a first answer ready will speed up whatever comes after Aug 12.

**HE:** איריס הייתה מפורשת: אין להתחיל לבצע את סקר הספרות המלא (פרק 2) או את עיצוב תוצר המחקר (פרק 4) עדיין. הדבר השימושי היחיד לעשות כרגע הוא להתחיל רשימות לא-פורמליות על **מהו בדיוק התוצר (artifact) לכל שאלת מחקר** - ארכיטקטורה? מסגרת עבודה (framework)? סכמת סיווג? - שכן השאלה הזו הועלתה בשיחה אך לא נענתה, ותשובה ראשונית מוכנה תזרז את מה שיבוא לאחר ה-12 באוגוסט.

---

## 🟡 Step 6 - Respond to Iris's check-in email

## שלב 6 - מענה למייל בדיקת-ההתקדמות של איריס

*Source: `A08-07`*

**EN:** Iris said she'd email early next week, before the Sunday before Aug 12, asking for a progress check. Watch for it and respond with real status (ideally: Step 1 done, Step 2 in progress) rather than a generic reply.

**HE:** איריס אמרה שתשלח מייל בתחילת השבוע הבא, לפני יום ראשון שלפני ה-12 באוגוסט, ותבקש בדיקת התקדמות. שים לב למייל וענה עם סטטוס אמיתי (במצב אידיאלי: שלב 1 הושלם, שלב 2 בתהליך) ולא בתשובה גנרית.

---

## 🟡 Step 7 - Prepare the live progress presentation

## שלב 7 - הכנת המצגת החיה של ההתקדמות

*Source: `A08-08`*

**EN:** Ali is expected to present the material live at the Aug 12 meeting, not just have it written down. Prepare a short walkthrough of Chapter 3 and the literature spreadsheet, ready to screen-share the same way the Drive was shared on Aug 5.

**HE:** אלי צפוי להציג את החומר בשידור חי בפגישת ה-12 באוגוסט, לא רק להשאיר אותו כתוב. הכן סקירה קצרה של פרק 3 וגיליון הספרות, מוכנה לשיתוף מסך באותו אופן שבו הדרייב שותף ב-5 באוגוסט.

---

## Suggested order this week / סדר מוצע לשבוע

**EN:** (1) Step 0 first, today if possible - it blocks Step 1. (2) Step 1 and Step 3 in parallel early in the week. (3) Step 2 and Step 4 throughout. (4) Step 5 as spare-time background work. (5) Step 6 reactively, whenever the email lands. (6) Step 7 the day or two before Aug 12.

**HE:** (1) שלב 0 ראשון, היום אם אפשר - הוא חוסם את שלב 1. (2) שלב 1 ושלב 3 במקביל בתחילת השבוע. (3) שלב 2 ושלב 4 לאורך כל השבוע. (4) שלב 5 כעבודת רקע בזמן פנוי. (5) שלב 6 באופן תגובתי, מתי שהמייל יגיע. (6) שלב 7 יום-יומיים לפני ה-12 באוגוסט.

## Related evidence / מסמכים קשורים

- [`2026-08-05-supervisor-meeting.md`](2026-08-05-supervisor-meeting.md) - canonical evidence matrix (English) / רשומת הראיות הקנונית (אנגלית)
- [`2026-08-05-supervisor-provenance-manifest.md`](2026-08-05-supervisor-provenance-manifest.md) - ASR provenance / מקור התמלול
- `docs/video1638342429.transcript.en.md` - English narrative rendering / תרגום נרטיבי לאנגלית
- `docs/video1638342429.transcript.he.md` - Hebrew ASR transcript / תמלול המכונה בעברית
