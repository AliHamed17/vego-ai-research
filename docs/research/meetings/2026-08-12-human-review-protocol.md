# August 12 bilingual evidence review protocol

## Status and boundary

This protocol governs human review of the private August 12 Zoom evidence. It does not authorize public release of raw media or a direct quotation. The machine layer contains 1,064 Hebrew ASR segments and 215 uncovered media intervals across the full 53:44.448 timeline. Machine English is a review aid, not a verified translation.

פרוטוקול זה מסדיר את הבדיקה האנושית של ראיות שיחת הזום הפרטיות מ־12 באוגוסט. הוא אינו מתיר פרסום של המדיה הגולמית או ציטוט ישיר. שכבת המכונה כוללת 1,064 מקטעי תמלול בעברית ו־215 מרווחי מדיה שלא כוסו על־ידי התמלול, לאורך מלוא 53:44.448 הדקות. האנגלית המכונתית היא כלי עזר לבדיקה ואינה תרגום מאומת.

## Independent returns / החזרות עצמאיות

1. Reviewer A and Reviewer B receive identical, hash-bound private media, the machine ledger, and separate pre-populated CSV templates.
2. They work independently and do not inspect each other's return before both returns are frozen.
3. Each reviewer completes, in the supplied order:
   - `S12-0001` through `S12-1064`;
   - `G12-0001` through `G12-0215`;
   - one `MEDIA-TIMELINE` record covering the complete recording.
4. Each segment receives reviewed Hebrew and English, speaker, confidence, basis, content class, control IDs, notes, reviewer identity, and review date.
5. Each gap is watched or listened to at its exact interval. If substantive speech exists, the reviewer transcribes and translates it, classifies it, and assigns or proposes a control. A gap must not be labelled silence merely because ASR omitted it.
6. The reviewer identity must match the privately approved roster ID. Case or Unicode variants of one identity do not create a second reviewer.
7. `MEDIA-TIMELINE` uses the exact attestation `media_duration_seconds=3224.448; reviewed_media_seconds=3224.448; unreviewed_media_seconds=0.000` only after the reviewer has reviewed the entire recording.

1. בודק א' ובודק ב' מקבלים מדיה פרטית זהה הקשורה ב־hash, את רישום המכונה ושתי תבניות CSV נפרדות ומאוכלסות מראש.
2. הם עובדים באופן עצמאי ואינם מעיינים בהחזרה של האחר לפני ששתי ההחזרות מוקפאות.
3. כל בודק משלים, לפי הסדר שסופק, את `S12-0001` עד `S12-1064`, את `G12-0001` עד `G12-0215`, ורשומת `MEDIA-TIMELINE` אחת המכסה את ההקלטה המלאה.
4. לכל מקטע נרשמים עברית ואנגלית שנבדקו, דובר, רמת ביטחון, בסיס לייחוס, סיווג תוכן, מזהי בקרה, הערות, זהות הבודק ותאריך הבדיקה.
5. כל מרווח נבדק בזמן המדויק שלו. אם קיימת בו אמירה מהותית, הבודק מתמלל ומתרגם אותה, מסווג אותה ומשייך או מציע בקרה. אין לסמן מרווח כשקט רק מפני שמערכת התמלול השמיטה אותו.
6. זהות הבודק חייבת להתאים למזהה שאושר ברשימה הפרטית. הבדלי רישיות או Unicode של אותה זהות אינם יוצרים בודק שני.
7. ברשומת `MEDIA-TIMELINE` נעשה שימוש בהצהרה המדויקת `media_duration_seconds=3224.448; reviewed_media_seconds=3224.448; unreviewed_media_seconds=0.000` רק לאחר בדיקת ההקלטה בשלמותה.

## Controlled values / ערכים מבוקרים

Speaker values are limited to `Iris`, `Arnon`, `Ali`, `Multiple`, `Unresolved`, and `Non-speech`. Confidence is `High`, `Medium`, `Low`, or `Unknown`. A named speaker requires `High` or `Medium` confidence plus an evidence-grade basis beginning with an approved audiovisual, visible-name-label, self-identification, or written-confirmation basis; otherwise the speaker remains `Unresolved`. Content class must be one of the classes enforced by the evidence builder. Conversational inference is not sufficient for a named quotation.

ערכי הדובר מוגבלים ל־`Iris`, `Arnon`, `Ali`, `Multiple`, `Unresolved` ו־`Non-speech`. רמת הביטחון היא `High`, `Medium`, `Low` או `Unknown`. דובר מזוהה בשם מחייב רמת `High` או `Medium` ובסיס ראייתי מאושר מסוג אישור אודיו־ויזואלי, תווית שם גלויה, זיהוי עצמי או אישור כתוב; אחרת הדובר נשאר `Unresolved`. סיווג התוכן חייב להיות אחד הערכים שנאכפים על־ידי בונה הראיות. הסקה מהקשר השיחה אינה מספיקה לציטוט בשם אדם.

Control IDs use only registered `F12-###`, `A12-###`, `D12-###`, `Q12-###`, or `R12-###` values. A substantive record must reach a registered control. A newly discovered obligation receives the next unused stable ID in the register before review can pass. Existing IDs are never repurposed to force agreement with a draft denominator.

מזהי הבקרה משתמשים רק בערכים רשומים מסוג `F12-###`, `A12-###`, `D12-###`, `Q12-###` או `R12-###`. רשומה מהותית חייבת להיות מקושרת לבקרה רשומה. חובה חדשה שמתגלית מקבלת תחילה את המזהה היציב הבא ברשם. אין לשנות משמעות של מזהה קיים כדי להתאים בכוח למכסה שהופיעה בטיוטה.

## Disagreement and adjudication / מחלוקת והכרעה

Any difference in reviewed Hebrew, reviewed English, speaker, confidence, attribution basis, content class, control IDs, or review notes is a disagreement. A roster-bound third person, distinct from both reviewers after identity normalization, adjudicates every disagreement. An adjudication is valid only when all applicable final fields and a non-blank rationale are present and `Decision_Status` is `Resolved`. Gap and timeline adjudications remain in the final 1,280-record ledger. An unresolved item remains open; it is never filled by majority, silence, or software default.

כל הבדל בעברית שנבדקה, באנגלית שנבדקה, בדובר, ברמת הביטחון, בבסיס לייחוס, בסיווג התוכן, במזהי הבקרה או בהערות הבדיקה הוא מחלוקת. אדם שלישי מרשימה מאושרת, השונה משני הבודקים גם לאחר נרמול הזהות, מכריע בכל מחלוקת. הכרעה תקפה רק כאשר כל השדות הרלוונטיים ונימוק שאינו ריק קיימים ו־`Decision_Status` הוא `Resolved`. הכרעות על מרווחים וציר הזמן נשמרות ברישום הסופי בן 1,280 הרשומות. סעיף שלא הוכרע נשאר פתוח.

## Release gate / שער שחרור

Human review can pass only when both returns cover all 1,280 required records, reviewer identities are distinct, every disagreement has one completed adjudication, the adjudicator is distinct, no unsupported named attribution remains, and the complete media timeline has zero unreviewed seconds. Supervisor acceptance and external facts remain separate gates even after bilingual review passes.

הבדיקה האנושית יכולה לעבור רק כאשר שתי ההחזרות מכסות את כל 1,280 הרשומות הנדרשות, זהויות הבודקים שונות, לכל מחלוקת קיימת הכרעה מלאה אחת, המכריע הוא אדם שלישי, לא נשאר ייחוס שמי ללא תמיכה, ולציר הזמן המלא נותרו אפס שניות שלא נבדקו. אישור המנחים ואימות עובדות חיצוניות נשארים שערים נפרדים גם לאחר שהבדיקה הדו־לשונית עוברת.

Until that gate passes, the permitted description is: **machine-derived Hebrew and English, human verification incomplete** / **עברית ואנגלית שנגזרו במכונה; האימות האנושי טרם הושלם**.
