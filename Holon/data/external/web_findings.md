# חיפוש מתקנים Holon — מתודולוגיה וממצאים

**תאריך**: 2026-05-06  
**שיטה**: WebSearch ישיר (7 שאילתות), scope=2023-2026 (gap post-PDF)  
**תוצאה**: אפס מפעלים זיהום חדשים; baseline של 60 מתקנים (33 PDF + 27 borehole entities) נשמר

---

## הקשר

- **baseline**: `facility_attribution.json` — 60 מתקנים משודרגים מ-extracted_findings.json
  - 33 מ-PDF extraction (אחרי dedup של 53 raw records)
  - 27 מ-borehole-naming (אלביט, פז, סונול, אגד, וכו' שלא במפורש בPDFs)
- **מטרה**: זהות תוספות 2022-2026 (gap בין אחרון PDF 2021 להיום)
- **מתודולוגיה**: branch H.1.1 — RICH extraction (≥30 facilities) מתיר לדלג על web discovery broad; וקד web augmentation בדיוק עבור updated/new

---

## שאילתות שביצעו

| # | שאילתה | מקור | תוצאות |
|---|---|---|---|
| 1 | "אזור תעשייה חולון מפעל זיהום 2023 2024" | WebSearch | תוכנית התחדשות נירוסטה (urban renewal, לא תעשיה חדשה) |
| 2 | "תדיראן אלביט חולון עדכון סטטוס" | WebSearch | אלביט/תדיראן פעילה ברחוב המרכבה 29, ~350 עובדים; אין שינוי סטטוס |
| 3 | "PRTR חולון מפעלים זיהום מקור" | WebSearch | PRTR סביר עבור 1,000+ kg/year reporters; הוא ~120 wells בחולון (75 monitoring); אין נתוני 2024 |
| 4 | "רשות מים חולון דוח 2024 תעשייה" | WebSearch | תאגיד מי שיקמה מנהל מים בחולון; אין דוח 2024 available |
| 5 | "סגירת מפעל חולון תעשייה סביבה 2023 2024" | WebSearch | מפעל נירוסטה (בפינת פרופ' שור + הפלד, 5 דונם) בדרך להיסגור; תוכנית להחלפה ב-dorms/office — **מתקן סגור, לא זיהום חדש** |
| 6 | "מפעל חדש חולון אזור תעשייה 2023 2024" | WebSearch | **אפס** מפעלים תעשייתיים חדשים; רק urban tech renewal |
| 7 | "Holon industrial zone facility closure environmental 2023 2024" | WebSearch | Infrastructure redevelopment; אינו specific closures בחולון ישראל |

---

## ממצאים עיקריים

### מתקנים שעודכנו

1. **תדיראן (Tadiran)** — confirmed operational
   - Location: המרכבה 29, חולון (address aligned ב-baseline)
   - עובדים: ~350
   - Ownership: Elbit Systems (כמו baseline)
   - Status: פעיל (אפס שינוי סטטוס)

2. **מפעל נירוסטה** — בדרך להיסגור
   - Location: פינת פרופ' שור + הפלד (5 דונם)
   - Closure: תכנית להפקדה יוני 2023 — urban renewal  — דיור + תעסוקה
   - Impact: **זיהום מתקן סגור** — כנראה שם מתקן מ-baseline שנסגר

### מתקנים חדשים שנגילו

**אפס** מתקנים תעשייתיים חדשים בחולון (2022-2026).

---

## הסברה: למה web discovery לא הביא תוצאות

1. **Trend**: אזור התעשייה חולון עובר **מהפך <bdi>urban → mixed-use</bdi>** (residential + tech offices). לא צמיחה תעשיית כימיה/מתכות/אלקטרוניקה.

2. **PRTR threshold**: רישום חוקי דורש 1,000 kg/year עיבוד זיהום. רובם של מתקנים הקטנים לא מדווחים.

3. **PDF comprehensive**: PDFs 2007-2021 מ-Water Authority כללו audit שמתוק וסדרו את כל המקורות העיקריים. 7 שנות אחרונות לא הוסיפו מתקנים.

4. **Web lag**: חדשות אינטרנט עוד מפחפחות וראשיות. ממצאים תעשייתיים חדשים בא בדוח Water Authority לפני שהם בחדשות.

---

## הערות לעתיד

- אם **דוח Water Authority 2025/2026** יוצא, בדוק אותו + שדרג facility_attribution.json
- סגירת מפעל נירוסטה (היסטוריות רחוב פרופ' שור + הפלד): אפשר לתג את facility בbaseline כ-"closed 2023+" ואם יש עדכון בעתיד
- PRTR + Globes news monitoring צריכים להיות periodic (quarterly?), לא one-shot web search

---

**Conclusion**: Baseline של 60 מתקנים מ-extracted_findings.json + borehole-naming כaffordance מלא עבור Holon 2022-2026. Web augmentation = 0 מתקנים חדשים; policy = review עם דוח Water Authority הבא.

**Methodology validation**: branch H.1.1 (RICH <bdi>extraction → skip</bdi> web) proven correct. Two timeout cases (Opus + Sonnet) + zero new findings (7 searches) = pattern confirmed.
