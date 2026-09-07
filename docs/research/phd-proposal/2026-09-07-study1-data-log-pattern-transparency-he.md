<div dir="rtl">
# שקיפות נתונים, לוגים ודפוסים — VEGO-AI Study 1

**סטטוס:** READY FOR SUPERVISOR TRANSPARENCY REVIEW — NOT A NEW SCIENTIFIC RESULT.
**מקור הנתונים הפרטי:** `NOT_AVAILABLE_IN_WORKTREE`; לא הופקו נתונים מדעיים חדשים.
המסמך מתעד את מקור הנתונים הציבורי ואת חוזי הקוד. הוא אינו מחליף מניפסט binding של ההרצה שהתקבלה.

## 1. מקור הנתונים ובחירת המקרים

הגדרת ההכנה היא `setting_id=cd_airtravel` ו-`corpus_id=text2uml_airtravel_253b26dc`. המקור הוא Text2UML ציבורי, commit `253b26dc704d523209a5cba79686f8f7fab57d63`, תחת `dataset/AirTravel`.
ארכיון codeload אומת ב-SHA-256 `8cf82e2ab2d2ce3da9a7ec4165e760ae1e0d9af14468f5aa2a3883037d8da701`; נבדקו 143 קבצים מתוך 143, ללא שינוי בתוכן. הקבצים הגולמיים אינם נשמרים ב-Git.
בחירת N=4 היא purposive feasibility בלבד: ארבעת קבצי `result_one_*` שהוגדרו בתיקון v1.0.2 ותיאור הדומיין. זה אינו נתון של תלמידים, אינו Cheers/ParkWise ואינו ground truth.

| Runtime file | תפקיד | bytes | SHA-256 |
|---|---|---:|---|
| `domain_description/description.md` | domain_description | 1477 | `96bc8a6fbf2c2fdd93592fdbf6fac7c2b9db403494fe2d5a45e0a2bcbf0167e2` |
| `candidate_models/01_result_one_claude-sonnet-4-6.txt` | candidate_model | 1248 | `240b034834e383b9844e9a3e9796f6be9b3d47fc95de6606ed022d278d751f91` |
| `candidate_models/02_result_one_codestral-2508.txt` | candidate_model | 1272 | `08399ca9432c1399f3f9784d34741314e4d39e40307a6efb14fa92a1c138b1d6` |
| `candidate_models/03_result_one_deepseek-chat.txt` | candidate_model | 1324 | `ee4d689d59c9ce3a5e8ff385747641954bd4821f2efeb18e581dcd1d5441d20a` |
| `candidate_models/04_result_one_gemini-2.5-flash.txt` | candidate_model | 1231 | `1c3d15eac71fcaab138857dbbc7153833b3df55ab57925ac756a79dc28dc847a` |

### טבלת מקור קצרה

| פריט | מקור | כיצד אומת | מה ניתן להסיק | מה לא ניתן להסיק |
|---|---|---|---|---|
| corpus AirTravel | Text2UML ציבורי | commit, archive SHA-256 וספירת קבצים | provenance והיתכנות | התנהגות תלמידים, נכונות או תועלת אנושית |
| ארבעה candidates | `result_one_*` | כלל בחירה קפוא ו-SHA-256 | השוואת הכנה מתועדת | ייצוג סטטיסטי או ranking |
| references | reference-only | מופרדים מנתיב runtime | גבול קלט ברור | מקור לתווית Detector |
| accepted run | מניפסט פרטי נדרש | לא מותקן ב-worktree | אין ערך מספרי כרגע | כל מסקנה ניסויית |

## 2. מערכת וגרסה

נבדקה גרסת VEGO-AI הציבורית [v2.1.5.3](https://github.com/ieiris/VEGO-AI/releases/tag/v2.1.5.3) באמצעות ארכיון ציבורי, SHA-256 `f7c2f62c927f280c25ecfaec667515e6a8ef8ad8a4104f168f27a1401b4f98b6`. קבצי המקור שנבדקו כוללים את `action_logger.py`, `GUI_Common.py`, `llm_client.py`, `orchestrator.py`, יצוא Agent 3, Agent 4 וה-evaluator.
נוכחות פונקציה או נתיב בקוד אינה הוכחה שקובץ נוצר בהרצה. לכן כל שורת matrix מפרידה בין source-present לבין runtime-present.

## 3. איזה לוג הוא מקור האמת?

`qa_events.jsonl` של ה-recorder הקנוני הוא מקור האמת ל-Q&A ול-Detector-v1, כאשר הוא קיים ומחייב מניפסט binding מאומת. `interaction_log.json` הוא תיעוד קריאות LLM אפשרי; `user_actions.log` הוא לוג פעולות GUI. אף אחד משני אלה אינו מוכיח אפיזודת Q&A.
יצוא Agent 3 (`cases_summary.csv`) הוא סיכום GUI. פלט Agent 4 הוא סיווג שונות נפרד. receipts/manifests משמשים לבקרת provenance ולבדיקת hashes, ולא מחליפים event log.

| Artifact | יוצר | קיים במקור v2.1.5.3 | קיים בהרצה שנבדקה | מקור ל-Detector? | מגבלה מרכזית |
|---|---|---:|---|---:|---|
| `interaction_log.json` | VEGO GUI Common path / LLMClient when interaction_log is configured | כן | `NOT_AVAILABLE_IN_WORKTREE` | לא | A named path/function is not proof that a runtime file was produced; GUI uses JSONL content under a .json name. |
| `user_actions.log` | GUI Controller action_logger.py | כן | `NOT_AVAILABLE_IN_WORKTREE` | לא | It records GUI actions, not question/answer lifecycle, episode identity, confidence, evidence presence or termination. |
| `qa_events.jsonl` | VEGO-AI/framework/qa_communication.py recorder / local observer | לא | `NOT_AVAILABLE_IN_WORKTREE` | כן | Without a binding manifest and byte-verified accepted log, all metrics are NOT_AVAILABLE_IN_WORKTREE. |
| `Agent 3 structured CSV export (cases_summary.csv)` | GUI View Agent3Tab export action | כן | `NOT_AVAILABLE_IN_WORKTREE` | לא | CSV export is not the append-only Q&A event stream and cannot establish one-answer-per-question lifecycle. |
| `Agent 4 variability classifications` | Agent 4 evaluator/orchestrator | כן | `NOT_AVAILABLE_IN_WORKTREE` | לא | This is the separate Selective Intervention Policy input. It may feed a queue builder; absence of a queue artifact does not mean not triggered. |
| `run receipt / pipeline manifest / output hashes` | study execution and evidence-recovery tooling | לא | `NOT_AVAILABLE_IN_WORKTREE` | לא | Receipt numbers are cross-checks only; the event log remains primary for episode and detector counts. |

## 4. Detector-v1: כלל → שדה → פרשנות

יחידת הניתוח היא Q&A episode. התווית היא reporting-level candidate-for-human-review בלבד; Detector-v1 אינו כותב תור. הנוסח הקפוא:

<div dir="ltr">STRONG_ALERT = S1 OR S3 OR S7</div>
<div dir="ltr">WEAK_ALERT = no strong signal AND (S2 OR S6)</div>
<div dir="ltr">NO_ALERT otherwise</div>

| אות | כלל קוד מדויק | שדות נדרשים | מה הוא אומר | מה אינו אומר | Accepted evidence |
|---|---|---|---|---|---|
| `S1` | `if any(row.get("answer_confidence") == "Low" for row in answers):` | `run_id, episode_id, event_type, sequence (event ordering), event_id (answer event identifier), question_id, source_agent, target_agent, round_index, termination_reason, scientific_complete, answer_confidence` | At least one answer reports Low confidence under the frozen answer field. | It does not prove an incorrect answer, poor evidence, or that a human queue was written. | `NOT_AVAILABLE_IN_WORKTREE` |
| `S2` | `if any(row.get("answer_confidence") == "Medium" for row in answers):` | `run_id, episode_id, event_type, sequence (event ordering), event_id (answer event identifier), question_id, source_agent, target_agent, round_index, termination_reason, scientific_complete, answer_confidence` | At least one answer reports Medium confidence under the frozen answer field. | It does not prove error, disagreement or intervention benefit. | `NOT_AVAILABLE_IN_WORKTREE` |
| `S3` | `if any((ref := row.get("answer_evidence_ref")) is None or ref.get("length", 0) == 0 for row in answers):` | `run_id, episode_id, event_type, sequence (event ordering), event_id (answer event identifier), question_id, source_agent, target_agent, round_index, termination_reason, scientific_complete, answer_evidence_ref` | At least one answer has a null or zero-length evidence reference under the frozen structural rule. | It does not assess evidence quality, truth, or semantic support; it is not an observed finding without a validated log. | `NOT_AVAILABLE_IN_WORKTREE` |
| `S6` | `if episode.get("round_count", 0) > 1:` | `run_id, episode_id, event_type, sequence (event ordering), event_id (answer event identifier), question_id, source_agent, target_agent, round_index, termination_reason, scientific_complete` | The projected episode contains more than one Q&A round. | It does not prove unresolved disagreement, high burden, or answer quality. | `NOT_AVAILABLE_IN_WORKTREE` |
| `S7` | `if episode.get("termination_reason") == "TERMINATED_MAX_ROUNDS":` | `run_id, episode_id, event_type, sequence (event ordering), event_id (answer event identifier), question_id, source_agent, target_agent, round_index, termination_reason, scientific_complete` | The episode ended at the frozen maximum-round termination state. | It does not prove the final answer is wrong or that a human corrected it. | `NOT_AVAILABLE_IN_WORKTREE` |

S1/S2 הם דיווח עצמי של המודל. S3 בודק null/אורך אפס בלבד; אורך ההפניה אינו איכות ראיה. S6 הוא תיאור מספר הסבבים. S7 הוא מצב סיום.

## 5. מהו ‘דפוס’ כאן?

| סוג מידע | יחידת ניתוח | דוגמה | מפעיל Detector-v1? | יוצר תור אנושי? | משמעות |
|---|---|---|---:|---:|---|
| Detector pattern | Q&A episode | S1/S3/S6/S7 | כן | לא | תנאי קפוא לדיווח |
| descriptive communication statistic | route/case/round/run | מספר שאלות או routes | לא בהכרח | לא | תיאור תקשורת בלבד |
| Agent-4 selective-intervention classification | Agent-4 variability classification | confidence/Undetermined | לא | queue builder נפרד עשוי ליצור | מנגנון פעולה נפרד |

## 6. שני מנגנוני אדם נפרדים

**Detector-v1:** אפיזודת Q&A, תווית מועמד לדיווח, ללא queue וללא שינוי אוטומטי.
**Selective Intervention Policy / Agent-4:** סיווג השונות של Agent 4; queue builder נפרד עשוי לכתוב `human_review_queue.jsonl`. ב-AirTravel הסטטוס הוא `NOT_AVAILABLE` עד שקובץ queue מאומת יותקן. היעדרו אינו ‘not triggered’ ואינו אפס.
בשני המנגנונים אין שינוי אוטומטי במקור, ביעד, בהנחיה או במודל.

## 7. כרטיסי דוגמה למנחים

### EX-01 — אפיזודה מלאה ללא התראה
**המחשה הנדסית בלבד — אינה תוצאת ניסוי ואינה נתון אמפירי**
Input/case: `fixture-case-normal (engineering-only)` → log: `episode_id; QUESTION_EMITTED; ANSWER_RECEIVED; High; non-empty evidence ref; round_index=1; CONVERGED` → rule: `No S1/S2/S3/S6/S7` → result: `NO_ALERT (illustrative rule application only)`.
**פירוש:** הדוגמה ממחישה כיצד מצב תקין עובר ללא תווית מועמד. **מגבלה:** אינה מוכיחה נכונות תשובה או איכות ראיות.

### EX-02 — התראת חוזק עקב ביטחון נמוך
**המחשה הנדסית בלבד — אינה תוצאת ניסוי ואינה נתון אמפירי**
Input/case: `fixture-case-low-confidence (engineering-only)` → log: `episode_id; ANSWER_RECEIVED; answer_confidence=Low; non-empty evidence ref; CONVERGED` → rule: `S1 fires; STRONG_ALERT = S1 OR S3 OR S7` → result: `STRONG_ALERT (illustrative rule application only)`.
**פירוש:** זו תווית דיווח שמצביעה על מועמד לבדיקה אנושית בלבד. **מגבלה:** Low הוא דיווח עצמי של המודל ואינו תווית שגיאה.

### EX-03 — סיווג Agent-4 ותור נפרד
**המחשה הנדסית בלבד — אינה תוצאת ניסוי ואינה נתון אמפירי**
Input/case: `fixture-variability-classification (engineering-only)` → log: `classification=Undetermined; confidence=medium; requires_human_review=true` → rule: `Not a Detector-v1 input` → result: `Detector-v1: NOT_APPLICABLE`.
**פירוש:** Queue builder נפרד עשוי ליצור human_review_queue.jsonl אם יורץ. **מגבלה:** ב-AirTravel הסטטוס כרגע NOT_AVAILABLE; אין שינוי אוטומטי במקור, בהנחיה, ביעד או במודל.

כל שלושת הכרטיסים הם `ENGINEERING_ILLUSTRATION_ONLY` ואינם נכנסים לטבלת מדדים מדעית.

## 8. מה נצפה ומה לא נצפה

**נצפה:** חוזי קוד ציבוריים, נתיבי יצוא ושדות Detector מוגדרים. **לא נצפה:** כל דפוס אמפירי של Study 1, משום שקובץ האירועים הפרטי וה-binding manifest של ההרצה שהתקבלה אינם מותקנים ב-worktree. לכן S1–S7 מוצגים ככללים קיימים עם observed count = `NOT_AVAILABLE_IN_WORKTREE`, ולא כממצאים.
גם Agent-4 queue הוא `NOT_AVAILABLE`; אין להסיק מכך שלא הופעל.

## 9. פרטיות, שחזור וגבולות טענה

לא נקראו credentials, prompts, answers או raw outputs. אין להכניס אותם ל-Git. כדי לחשב מדדים בעתיד יש לספק binding manifest פרטי, לאמת SHA-256, run identity ושלמות lifecycle, ואז לחשב רק מה-event log. אין להסיק accuracy, precision/recall, correctness, human benefit, causality, generalization או superiority.
מניפסט האיורים `study1-transparency-figures-manifest-v1.json` מתעד שלושה איורי כלל/גבול בטוחים; אין בו נתוני ניסוי או גרף מדעי.
פקודות שחזור offline בלבד: `uv run python scripts/build_study1_transparency_package.py --output-dir <safe-output>` ולאחר מכן `uv run pytest -q scripts/tests/test_study1_transparency_package.py`. לא מופעל provider או model.

## 10. שאלות לאיריס ולארנון

1. האם `qa_events.jsonl` המקורי וה-binding manifest של ההרצה שהתקבלה זמינים בנתיב פרטי מאושר?
2. האם תרצו לאשר ש-Detector-v1 נשאר תווית דיווח ללא queue, ו-Agent-4 הוא מנגנון queue נפרד?
3. האם כלל הבחירה של ארבעת AirTravel candidates והפרדת reference-only מתאימים להצגה?
4. אילו שדות תרצו לראות בדוח הבא לאחר אימות ה-event log, בלי להרחיב את טענות המחקר?

*טיוטה בסיוע מכונה; המשמעות בעברית מחייבת ביקורת אנושית.*
</div>
