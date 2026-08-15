# August 12 Evidence-to-Delivery Audit / ביקורת ראיות למסירה מ־12 באוגוסט

**Evidence snapshot:** 2026-08-15, Asia/Jerusalem

**Maximum current status:** **Ready for Ali review — not delivered, accepted, closed, or 100% complete**

**Closure certificate:** **Not permitted**

This is the sanitized control-facing audit for the August 12 execution tranche. It contains no
transcript text, private connector identifier, scholarship attachment, raw media, restricted
medical row, or private filesystem locator. Hashes identify controlled evidence; they do not turn
machine output into human-verified evidence.

זהו דוח הביקורת המסונן של מקטע הביצוע מ־12 באוגוסט. הדוח אינו כולל טקסט תמלול, מזהה פרטי של
שירות חיצוני, מסמך מלגה, מדיה גולמית, שורה רפואית מוגבלת או נתיב פרטי. הגיבובים מזהים ראיות
מבוקרות; הם אינם הופכים פלט מכונה לראיה שאומתה בידי אדם.

## 1. Frozen component versions / גרסאות רכיבים מוקפאות

| Component / רכיב | Exact version or binding / גרסה או קישור מדויק | Reviewed state / מצב ביקורת |
| --- | --- | --- |
| Four-file Zoom source chain | See [machine-evidence provenance](2026-08-12-machine-evidence-provenance.md); duration `3,224.448` seconds | Source hashes and decoded-audio equivalence pass |
| Private machine-evidence package | Builder commit `534da4aab609ab40c0ef5a7672b7af14ddcd031d`; provenance SHA-256 `B42BFB65EFA28A8AB123859E0994E91F453EEE48ABDCC74C655535FBC393B125` | Independent adversarial review pass for machine-only preliminary evidence |
| ACL 2026 bounded corpus | Sanitized corpus commit `974552efd90d233980c588746f50928d8e397b0e`; taxonomy repository commit `7b3ba9deefe99172748582f6025d995ccc2a6f86` | Deterministic inventory/offline staging pass; human screening `0/116` |
| August 19 supervisor package | Package fix commit `627d4cfdd5e28bdd759bc60a81dc81fecafa3ccf`; [sanitized manifest](2026-08-19-supervisor-package/final/package-manifest.sanitized.json) SHA-256 `6AFD13C03E09F5431BD7CF5145FC9E74E5B511804E0F01DBED57265C0AFF48B8` | Exact 10-file inventory and independent 25-page visual review pass |
| Scholarship lane | [controlled status](../../operations/2026-08-vatat-scholarship-status.md) | Draft-only; not submitted; Iris letter and eligibility resolution missing |

The private machine-evidence review report is bound by SHA-256
`CC3683A2B861CBEA39D498279371E8B42BBE4BA15A83389FD3E37684C3FC18F5`.
The supervisor-package review report is bound by SHA-256
`C478B4156670138ACD20E53357DFEA6970EBB615A7E58A9AF719CFFB5D50E622`.
The reports remain local coordination evidence; these hashes do not imply supervisor acceptance.

## 2. Acceptance matrix / מטריצת קבלה

| Area / תחום | Current evidence / ראיה נוכחית | State / מצב |
| --- | --- | --- |
| Source integrity | Four locked files; M4A and MP4 audio decode to the same `51,591,168` samples and PCM hash | **Pass** |
| Timeline coverage | `1,064` ASR segments plus `215` uncovered intervals totaling `166.788` seconds account for the full `3,224.448` seconds | **Structural pass; human review pending** |
| Machine alignment | `1,064/1,064` machine-English rows are source-hash aligned | **Pass as machine evidence only** |
| Human bilingual review | Reviewer A `0/1,280`; Reviewer B `0/1,280`; adjudications `0`; reviewed media `0/3,224.448` seconds | **Blocked** |
| Controls and crosswalk | `F12-001..019`, `A12-001..010`, `D12-001..005`, `Q12-001..009`, `R12-001..009`; Claude draft references preserved by crosswalk | **Structural pass; acceptance pending** |
| Research decisions | RQ wording, E6, E8, Plan A/B, evidence-boundary wording, and Section 4 disposition remain explicit questions | **Deferred / open** |
| Literature inventory | `525` source occurrences resolve to `116` unique works at the pinned repository commit | **Inventory pass** |
| Literature screening | Identity, publication type, include/exclude reason, reviewer, and date remain pending for every work | **Blocked at `0/116`** |
| Broad queries | QL-01..QL-05 remain `Protocol ready`; the Foundations observation is non-release-eligible | **Intentionally unexecuted** |
| Bilingual documents | Exact ten-file allowlist; nine bound deliverables; EN/HE parity, links, citations, RTL, page/slide rendering, and visual inspection pass | **Ready for Ali review** |
| Scholarship | Arnon's two-page letter validated; Iris/Arnon Gmail replies are drafts; no Iris letter or submission receipt | **Urgent human action / blocked** |
| Drive | Root remains link-readable; Iris remains Writer; Arnon lacks intended access; old folder contains 16 mixed-scope files | **Release control failed** |
| Gmail | Two scholarship replies remain labelled Draft and `sent=false` | **Draft-only pass; no send receipt** |
| Repository | Work is isolated locally; public `main` is unprotected and its latest observed workflow is red on stale generated content; PR #14 remains conflicting and untouched | **PR/CI gate pending** |
| Evidence boundaries | EXP-005 `0/24`; medical readiness `0/6`; no restricted medical-row inspection | **Preserved** |
| Closure | Human review, supervisor dispositions, permissions, delivery, CI, and receipts are incomplete | **Not eligible** |

## 3. What is locally complete / מה הושלם מקומית

- The four supplied Zoom files are byte-bound without modifying the OneDrive originals.
- M4A/MP4 audio equivalence, the complete gap ledger, immutable Hebrew ASR, aligned machine English,
  model/execution bindings, and the append-only v3 package passed independent adversarial checks.
- The canonical control register, old-ID crosswalk, reviewer templates, bilingual corrected report,
  claim register, and open-decision sheet exist. They use paraphrases and do not promote uncertain
  speaker attribution to quotation.
- The ACL taxonomy repository is pinned and deterministically enumerated. Offline native-workbook
  staging is lossless and replay-protected; no Google Sheet write occurred.
- The ten-file August 19 package excludes raw media, transcripts, scholarship material, thinking
  notes, anticipated Q&A, and workbook duplication. All 25 PDF pages and the PPTX rendering were
  inspected; the package is bound to Python 3.11.14 and `pypdf 6.15.0`.
- The exact meeting checkpoint was confirmed as 2026-08-19, 09:00–10:00 Asia/Jerusalem.

- ארבעת קובצי המקור של Zoom קושרו ברמת הבתים בלי לשנות את קובצי OneDrive המקוריים.
- שקילות האודיו, רישום הפערים המלא, התמלול העברי המכונתי, האנגלית המכונאית המיושרת וחבילת v3
  עברו בדיקות יריבות עצמאיות.
- קיימים מרשם בקרות, מיפוי מזהים ישנים, תבניות לשני סוקרים, דוח דו־לשוני מתוקן, מרשם טענות
  וגיליון החלטות פתוחות. אין בהם ציטוט ישיר או ייחוס דובר שאינו מאומת.
- מאגר ה־ACL נעול לגרסה מדויקת וממופה באופן דטרמיניסטי. לא בוצעה כתיבה ל־Google Sheets.
- חבילת 19 באוגוסט כוללת בדיוק עשרה קבצים מאושרים לבדיקה פנימית; כל העמודים והשקופית נבדקו
  חזותית. המצב הוא מוכנות לבדיקת עלי בלבד.

## 4. Human and external blockers / חסמים אנושיים וחיצוניים

1. **Scholarship:** Ali must review and send the Iris request, obtain the signed Iris letter or
   direct-send confirmation, resolve direct-PhD eligibility, reconcile conflicting academic figures,
   submit the exact application by the written August 16 deadline, and retain receipts.
2. **Transcript review:** Ali completes Reviewer A. A distinct bilingual Reviewer B and a distinct
   adjudicator must be named and must complete all 1,280 records, including every gap and the full
   timeline attestation.
3. **Literature:** Reviewers must screen all 116 works. Novelty or absence claims remain hypotheses
   until the completed screening supports them.
4. **Supervisor decisions:** The August 19 worksheet must record only explicit `Confirm`, `Confirm
   with correction`, `Retire or supersede`, or `Defer` outcomes. Silence is `Defer`.
5. **Drive:** Only after Ali approves the exact ten-file package may the operator remove link access,
   change Iris to Commenter, add Arnon as Commenter, mark the mixed 16-file folder superseded without
   deleting it, create the clean folder, and test both recipient accounts.
6. **Repository:** The sanitized intended tree must pass clean-worktree privacy, tests, manifests,
   documents, browser, and CI gates in an isolated PR. No direct-main push, merge, PR #14 change, or
   branch-protection change is authorized by this audit.

1. **מלגה:** עלי צריך לבדוק ולשלוח את הטיוטה לאיריס, לקבל מכתב חתום או אישור שליחה ישירה,
   לפתור את שאלת הזכאות, ליישב נתונים אקדמיים סותרים, להגיש עד 16 באוגוסט ולשמור קבלות.
2. **בדיקת תמלול:** עלי משלים את סוקר א'. יש למנות סוקר ב' דו־לשוני נפרד ומכריע נפרד, ולהשלים
   את כל 1,280 הרשומות, כולל כל הפערים ואישור ציר הזמן המלא.
3. **ספרות:** יש לסקור אנושית את כל 116 העבודות. טענות חדשנות או היעדר מסגרת נשארות השערות
   עד שהסקירה המלאה תומכת בהן.
4. **החלטות מנחים:** בגיליון 19 באוגוסט יירשמו רק תוצאות מפורשות: אישור, אישור עם תיקון,
   פרישה או החלפה, או דחייה. שתיקה פירושה דחייה.
5. **Drive:** רק לאחר אישור עלי לחבילה המדויקת ניתן להסיר גישת קישור, להפוך את איריס ואת ארנון
   למגיבים, לסמן את התיקייה הישנה כמוחלפת בלי למחוק אותה, ליצור תיקייה נקייה ולבדוק את שני החשבונות.
6. **מאגר הקוד:** העץ המסונן חייב לעבור בדיקות פרטיות, בדיקות קוד, מניפסטים, מסמכים, דפדפן ו־CI
   בתוך PR מבודד. דוח זה אינו מאשר דחיפה ישירה ל־main, מיזוג, שינוי PR #14 או שינוי הגנת ענף.

## 5. Release and incident boundary / גבול מסירה ואירוע

An earlier PowerPoint COM export attached to and closed a pre-existing user PowerPoint process. The
source presentation survived and the incident is recorded. PowerPoint COM is retired for this
package; current slide rendering uses the bounded non-COM route. The user application state was not
restored and this audit does not claim otherwise.

During later inspection, externally opened Word and PowerPoint windows created lock files in the
shared worktree. They were not closed or modified by this implementation. The approved package was
verified from the committed Git blobs in a clean detached checkout, so the local package verdict does
not depend on disturbing those windows.

במהלך ניסיון קודם PowerPoint COM התחבר לתהליך PowerPoint קיים וסגר אותו. קובץ המקור נשמר,
האירוע מתועד, ונתיב COM הוצא משימוש לחבילה זו. מצב היישום של המשתמש לא שוחזר ואין טענה כזו.
חלונות Word ו־PowerPoint שנפתחו מאוחר יותר לא נסגרו ולא שונו; האימות בוצע בעותק Git נקי ומנותק.

## 6. Closure decision / החלטת סגירה

**No closure certificate may be issued.** Local structural and visual verification is complete for
the versioned machine-evidence package, bounded ACL inventory, and exact ten-file supervisor package.
It is not a substitute for bilingual review, literature screening, supervisor disposition, privacy
correction, recipient access tests, scholarship submission, green PR checks, Ali approval, or
external receipts.

**אין להנפיק אישור סגירה.** אימות מקומי מבני וחזותי הושלם לרכיבים המפורטים, אך הוא אינו מחליף
בדיקה דו־לשונית, סינון ספרות, החלטות מנחים, תיקון הרשאות, בדיקות גישה, הגשת המלגה, CI ירוק,
אישור עלי או קבלות חיצוניות.
