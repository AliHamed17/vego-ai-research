# -*- coding: utf-8 -*-
"""Hebrew edition of the supervisor literature-review questions.

Two things reportlab does not do natively and are handled explicitly here:
  1. Hebrew glyphs - Arial is registered as an embedded TTF (verified 27/27 Hebrew letters).
  2. Bidirectional order - reportlab renders logical order as-is, so every string is passed
     through python-bidi's get_display() to produce visual order, and paragraphs are right
     aligned. Inline markup is deliberately avoided inside Hebrew runs, because tags would be
     reordered along with the text; emphasis is carried by style, not by inline tags.
"""
import os
from bidi.algorithm import get_display
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.enums import TA_RIGHT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (BaseDocTemplate, Frame, PageTemplate, Paragraph,
                                KeepTogether, Spacer)

OUT = r"C:\Users\ahamed\Downloads\VEGO_AI_Literature_Review_Questions_for_Supervisors_HE_20260826.pdf"

pdfmetrics.registerFont(TTFont("Arial", r"C:\Windows\Fonts\arial.ttf"))
pdfmetrics.registerFont(TTFont("Arial-Bold", r"C:\Windows\Fonts\arialbd.ttf"))
pdfmetrics.registerFont(TTFont("Arial-Italic", r"C:\Windows\Fonts\ariali.ttf"))

INK   = colors.HexColor("#1a1a1a")
MUTED = colors.HexColor("#5b5b5b")
RULE  = colors.HexColor("#c8c8c8")
ACC   = colors.HexColor("#1f4e79")
EXBG  = colors.HexColor("#f2f5f8")


def H(s):
    """Logical Hebrew -> visual order for reportlab."""
    return get_display(s)


title = ParagraphStyle("title", fontName="Arial-Bold", fontSize=15, leading=20,
                       textColor=INK, spaceAfter=3, alignment=TA_RIGHT)
sub = ParagraphStyle("sub", fontName="Arial", fontSize=9, leading=13.5,
                     textColor=MUTED, spaceAfter=10, alignment=TA_RIGHT)
intro = ParagraphStyle("intro", fontName="Arial", fontSize=9, leading=14,
                       textColor=INK, spaceAfter=12, alignment=TA_RIGHT)
qtext = ParagraphStyle("qtext", fontName="Arial-Bold", fontSize=9.7, leading=14,
                       textColor=ACC, spaceBefore=3, spaceAfter=3, alignment=TA_RIGHT)
body = ParagraphStyle("body", fontName="Arial", fontSize=8.7, leading=12.8,
                      textColor=INK, spaceAfter=3, alignment=TA_RIGHT)
ex = ParagraphStyle("ex", fontName="Arial", fontSize=8.4, leading=12.4,
                    textColor=INK, spaceAfter=3, leftIndent=5, rightIndent=7,
                    borderPadding=(4, 5, 4, 5), backColor=EXBG,
                    borderColor=EXBG, borderWidth=0, alignment=TA_RIGHT)
dec = ParagraphStyle("dec", fontName="Arial-Italic", fontSize=8.3, leading=12,
                     textColor=MUTED, spaceAfter=10, alignment=TA_RIGHT)

# (question, context, example, decision) - all logical order, converted at render time
QUESTIONS = [
 ("1. ארבעת הענפים של הטקסונומיה אינם מחלקים את קורפוס המאמרים. האם היא עדיין משמשת מסגרת ארגונית?",
  "השתייכות לענף כמעט אינה נושאת מידע על מאמר בודד, ולכן סיווג הענפים עשוי ללמד פחות מאשר סינון המאמרים עצמם.",
  "דוגמה. מתוך תשעים המאמרים, שמונים ותשעה נושאים את כל ארבעת תוויות הענפים. בדיוק אחד — מאמר על אורקסטרציה — משויך לענף יחיד.",
  "← האם נספח א׳ נשאר סיווג של הטקסונומיה, או הופך לסינון קורפוס בלבד."),

 ("2. איזו רוחב חיפוש נדרשת כדי לבסס טענת חדשנות — והאם זו בכלל חובה בשלב ההצעה?",
  "סינון תחום־קורפוס אינו יכול לבסס טענה שלילית, גם אם נעשה בקפידה. העבודה המתחרה הקרובה ביותר הייתה בלתי נראית מבנית לקורפוס שסיננתי.",
  "דוגמה. גישות Learning-to-Defer מרובות מומחים מנתבות בין מומחים מזוהים לפי כשירות פרטנית — העבודה הקרובה ביותר ל־SQ1. היא אינה מופיעה באף סקר מערכות אדם־סוכן, משום שמקומה בספרות התאורטית של למידת מכונה.",
  "← האם חמש משפחות השאילתות הרשומות חייבות לרוץ לפני ההגשה."),

 ("3. איזו מהימנות סינון נדרשת כדי שניתן יהיה לצטט את הספירות?",
  "הסינון בוצע בידי מסננת אחת ועל בסיס כותרות בלבד, אך קריטריוני ההכללה הם ברמת התוכן: הם נשענים על סוג התרומה של המאמר, שכותרת לרוב אינה חושפת.",
  "דוגמה. מתוך הכותרת Learning to Ask: When LLM Agents Meet Unclear Instruction — האם התרומה היא שיטה, מדד השוואה, או מאגר נתונים? הסיווג תלוי בכך לחלוטין, והכותרת אינה מכריעה.",
  "← האם להוסיף מסננת שנייה, או לסנן מחדש את עשרים ושבעה המכריעים ברמת התקציר."),

 ("4. האם הספרות צריכה לשבת במבוא, כשהסקירה השיטתית היא מחקר בפני עצמו?",
  "בהצעת המחקר מהפקולטה שקיבלתי אין כלל פרק סקירת ספרות, וטיוטה זו הולכת כעת בעקבותיה.",
  "דוגמה. באותה הצעה הספרות היא רקע בסעיפים 1.1–1.2, הסקירה השיטתית היא פעילות מחקר בסעיף 3.1, התקדמותה מדווחת בסעיף 4.1, והתוצר שלה הוא טקסונומיה.",
  "← האם זו הצורה המצופה במחלקה, או העדפה של מנחה אחד."),

 ("5. האם חֶסֶר יחיד וניתן להפרכה בחדות מספיק כדי לשאת דוקטורט?",
  "כטענה מצטברת של כל מה שהעבודה דורשת, הפער היה כמעט בלתי ניתן להפרכה. כעת הוא נשען על טענה אחת — ניתנות להפרכה שנקנתה במחיר הרוחב.",
  "דוגמה. הטענה היא שאף ניסוח בספרות שנסקרה אינו בוחר מעריך לפי כשירות מוערכת וגם סמכות ביחס למקטע השנוי במחלוקת. מחקר יחיד שעושה זאת יפריך את מלוא טענת החדשנות.",
  "← האם להיצמד לטענה הצרה או להרחיב, לפני הקפאת שאלות המחקר."),

 ("6. האם סמכות להכריע בטענה היא מושג בר־מחקר, או תפיסה ארגונית שתתנגד למדידה?",
  "כשירות כבר ממודלת סטטיסטית כדיוק צפוי לכל מומחה. סמכות אינה, והיא כעת הדבר היחיד שמפריד את העבודה מקודמתה הקרובה ביותר.",
  "דוגמה. מומחה לשפת המידול עשוי לקרוא את הסימון נכון ובכל זאת לא להחזיק מנדט לשנות כלל מוסדי; המרצה שבבעלותו המחוון עשוי להחזיק במנדט ולקרוא את הסימון שגוי.",
  "← האם שדות הסמכות בחוזה השיפוט המנוהל ניתנים למדידה, לפני עיצוב מחקר 2."),

 ("7. האם יש לשנות את ניסוח SQ2, או שהפרדה לפי בעלות מספיקה?",
  "החפיפה נפתרת כיום באמצעות גבול בעלות מוצהר ולא באמצעות הניסוח עצמו.",
  "דוגמה. SQ2 שואלת כיצד שיפוט נשמר ״כך שניתן יהיה לעשות בו שימוש חוזר״; SQ3 שואלת כיצד שיפוט ״נעשה בו שימוש חוזר בין הקשרים״. בקריאה ללא הצהרת הבעלות, שתיהן נראות כתובעות את אותו שטח.",
  "← האם ניתן להקפיא את מערך השאלות כפי שהוא."),

 ("8. מה ייחשב ראיה לכך שהסקירה רשאית להיעצר?",
  "הפרוטוקול מוקפא והשאילתות רשומות, אך לא הוגדר כלל עצירה.",
  "דוגמה. רוויה, מיצוי ארבעת מאגרי המידע הראשיים, או שיקול דעתכם — כולם מוצדקים, ומשתמעים מהם כשני סמסטרים של עבודה, אחד, או אפס.",
  "← אבן הדרך של הספרות בשנה הראשונה בתוכנית המעוגנת."),
]


def deco(canv, doc):
    canv.saveState()
    canv.setStrokeColor(RULE); canv.setLineWidth(0.5)
    canv.line(20*mm, 16*mm, A4[0]-20*mm, 16*mm)
    canv.setFont("Arial", 7.2); canv.setFillColor(MUTED)
    canv.drawRightString(A4[0]-20*mm, 11.5*mm,
                         H("VEGO-AI — שאלות פתוחות לסקירת הספרות לדיון עם המנחים — 26 באוגוסט 2026"))
    canv.drawString(20*mm, 11.5*mm, H("עמוד %d" % doc.page))
    canv.restoreState()


def build():
    doc = BaseDocTemplate(OUT, pagesize=A4,
                          leftMargin=20*mm, rightMargin=20*mm,
                          topMargin=18*mm, bottomMargin=22*mm,
                          title="VEGO-AI - Literature Review Questions (Hebrew)",
                          author="Ali Hamed")
    frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id="f")
    doc.addPageTemplates([PageTemplate(id="p", frames=[frame], onPage=deco)])

    story = [
        Paragraph(H("סקירת ספרות — שאלות פתוחות לדיון עם המנחים"), title),
        Paragraph(H("עלי חאמד  ·  לפרופ׳ איריס ריינהרץ־ברגר ולפרופ׳ ארנון שטורם  ·  26 באוגוסט 2026"), sub),
        Paragraph(H("שמונה הכרעות שאליהן הגיעה הסקירה ושאיני יכול להכריע בהן לבדי. כל אחת נובעת מעבודה שכבר "
                    "נעשתה, ולכן כל שאלה מציגה את הממצא, דוגמה אחת, ומה שהתשובה תשנה. איני שואל אם העבודה "
                    "ראויה — אני שואל איזה מבין כמה סטנדרטים לגיטימיים ברצונכם להחיל."), intro),
    ]

    for q, ctx, example, decision in QUESTIONS:
        story.append(KeepTogether([
            Paragraph(H(q), qtext),
            Paragraph(H(ctx), body),
            Paragraph(H(example), ex),
            Spacer(1, 2),
            Paragraph(H(decision), dec),
        ]))

    doc.build(story)
    print("WROTE:", OUT, os.path.getsize(OUT), "bytes")


build()
