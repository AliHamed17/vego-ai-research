<div dir="rtl">
# הערה טכנית ל-Claude — מילון אותות ומדידה של VEGO-AI Study 1

**סטטוס ראיות:** `NOT_AVAILABLE_IN_WORKTREE`.
הגדרות הקוד מתועדות להלן, אך סטטוס הנתונים הוא: קובץ האירועים הפרטי של ההרצה שהתקבלה אינו נמצא ב-worktree הנבדק.

## חמש שכבות המדידה

1. **שדות אירוע גולמיים:** מזהה שאלה, סוכן שואל, סוכן עונה, ביטחון תשובה, הפניית ראיות, מספר סבב וסיבת סיום.
2. **אותות תהליך:** `S1`, `S2`, `S3`, `S6`, `S7` מחושבים בדיוק כפי שמופיע ב-`scripts/extract_qa_escalation_features.py`.
3. **משתני הקשר:** `C1`, `C2`, `C3` מוצגים לצד האירועים בלבד ואינם קלט ל-Detector-v1.
4. **פלטים סמנטיים:** `Satisfied`, `Partially-Satisfied`, `Non-Satisfied`, `Alternative`, ודאות מיפוי, התאמת מקור–יעד ושברים שלא כוסו. אלה פלטי ניתוח, לא תוויות שגיאה אוטומטיות.
5. **פעולה תפעולית:** המונח היחיד המותר הוא ‘מועמד לבדיקה אנושית’. אין שינוי אוטומטי במקור, בהנחיה, ביעד או במודל.

## איך ההתראה החכמה פועלת

<div dir="ltr">STRONG_ALERT = S1 OR S3 OR S7</div>
<div dir="ltr">WEAK_ALERT = no strong signal AND (S2 OR S6)</div>
<div dir="ltr">NO_ALERT otherwise</div>

## שני מנגנונים נפרדים

**Detector-v1:** יחידת הניתוח היא אפיזודת שאלות–תשובות. הפלט הוא reporting-level candidate-for-review label בלבד; Detector-v1 אינו כותב לתור ואינו יוצר `human_review_queue.jsonl`.
**Selective Intervention Policy / מנגנון הבדיקה של Agent 4:** יחידת הניתוח היא סיווג השונות של Agent 4. כאשר queue builder נפרד מופעל, הוא עשוי ליצור `human_review_queue.jsonl`. אין שינוי אוטומטי במקור, ביעד, בהנחיה או במודל.
**סטטוס תור AirTravel:** `NOT_AVAILABLE` — לא נמצא בקובץ העבודה הנבדק תור מאומת וטעון. היעדר קובץ אינו פירושו ‘לא הופעל’ ואינו מספר אפס.

## גבול הפרשנות

ביטחון הוא דיווח עצמי של ה-LLM. נוכחות או אורך הפניה לראיות אינם מדד לאיכות הראיות. אין להסיק דיוק, תועלת לאדם, הפחתת עומס, הכללה או עדיפות מדיניות. `Alternative` ו-`Non-Satisfied` אינם שגיאה כשלעצמם.

## זמינות הנתונים

הטבלאות המצורפות מציינות `NOT_AVAILABLE_IN_WORKTREE` ואין בהן אפסים מומצאים. לאחר קבלת קובץ אירועים פרטי ומניפסט binding מאושר, יש לאמת SHA-256, run_id ושלמות lifecycle לפני חישוב כל ערך.

## מצבי אימות הראיות

הוולידטור הקנוני הוא `scripts/study1_evidence_recovery.py:validate_evidence`. במצב `prospective_self_binding` המניפסט חייב לציין `created_after_run = false`; במצב `retrospective_validation` הוא חייב לציין `created_after_run = true`, והוורדיקט נשאר לכל היותר `DESCRIPTIVE_REPORTING_WITH_RETROSPECTIVE_PROVENANCE`.

המסמך הוא טיוטה טכנית מסייעת-מכונה; המשמעות העברית דורשת ביקורת אנושית של Ali/המנחים.
</div>
