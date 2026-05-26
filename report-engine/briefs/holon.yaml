# ════════════════════════════════════════════════════════════════════
# Holon Industrial Zone · Report Brief
# Conforms to: schemas/zone-brief.schema.json
# This file is the SOLE input to the report engine for Holon.
# Validates and reproduces output/holon/INTERNAL.html + PUBLIC.html
# ════════════════════════════════════════════════════════════════════

zone:
  id: HOL
  name_he: "אזה״ת חולון"
  name_en: "Holon Industrial Zone"
  period: "2020–2026"
  edition: "2026-01"
  edition_date: "2026-05"
  doc_id_internal: "HOL/EXEC/INT/2026-01"
  doc_id_public:   "HOL/EXEC/PUB/2026-01"
  active_boreholes: "~58"           # placeholder accepted by schema
  contaminant_families_count: 4
  monitoring_gaps_count: 7
  pfas_coverage_pct: 3.6
  exceedance_count: 1

# ─── INTERNAL §00 ───────────────────────────────────────────────────
bottom_line:
  - "מי-התהום באזה״ת חולון מציגים תמונה <strong>דו-קוטבית</strong>: רוב הקידוחים תקינים — אך באפריל <bdi>2025</bdi> חצה קידוח ההפקה <strong>מק חולון <bdi>14</bdi></strong> לראשונה זה עשור את תקן <bdi>TCE</bdi> (<span class=\"red\"><bdi>101%</bdi></span>), ומזהם חדש (<bdi>1,4-דיאוקסן</bdi>) מתפשט אל קידוח חקלאי במרחק כקילומטר."
  - "במקביל, מערך הניטור מציג <strong>פערים שיטתיים</strong> — שבעה קידוחים ואשכולות שותקים <bdi>39–150+</bdi> חודשים, חלקם בריכוזי שיא; כיסוי <bdi>PFAS</bdi> עומד על <span class=\"red\"><bdi>~3.6%</bdi></span> בלבד, ולא במתקני הסיכון הגבוה."
  - "נדרשת פעולה מתואמת בארבעה צירים: <span class=\"teal\">עדכון תכנית הניטור</span>, <span class=\"teal\">קידוחים חדשים</span>, <span class=\"teal\">חקירת מקורות</span>, ו<span class=\"teal\">מדיניות הפקה</span> — כמפורט במטריקס ההחלטות בסעיף §<bdi>05</bdi>."

# ─── PUBLIC §01 ────────────────────────────────────────────────────
context_intro:
  - "אזור התעשייה של חולון הוא מהוותיקים בארץ — פעיל מאז שנות ה-<bdi>60</bdi>, ומכיל היסטוריה תעשייתית מגוונת: מפעלי ציפוי מתכות, אלקטרוניקה, מתקני דלק, מחזור, טקסטיל וכימיקלים. חלק מהפעילויות הללו השאירו טביעה היסטורית בקרקע ובמי-התהום."
  - "החל מסוף שנות ה-<bdi>90</bdi> אנחנו מפעילים מערך ניטור באזור — כיום <strong>כ-<bdi>58</bdi> קידוחי ליבה</strong> שנדגמים בתדירות משתנה. הדוח הזה מסכם את שש השנים האחרונות: רוב הקידוחים תקינים, אך באזורים מסוימים זוהו מוקדים היסטוריים שאנחנו עוקבים אחריהם בצמוד."
  - "המסמך נכתב במחויבות לשקיפות: אנו מציגים את <strong>מה שמצאנו</strong>, את <strong>מה שעדיין לא יודעים</strong>, ואת <strong>מה שאנחנו עושים</strong> — ללא הסתרה."

# ─── Both reports — selection bias caveat ───────────────────────────
framing_warning: >
  שיעור החריגות אינו מייצג את כלל מרחב חולון — קידוחי הניטור מוקמו בכוונה ליד מקורות זיהום
  חשודים (הטיית-בחירה). אין להסיק מהמדגם הזה לאיכות מי-התהום הכללית.

# ─── INTERNAL §01 — KPI cards ───────────────────────────────────────
kpis:
  - id: exceedance_production
    label: "חריגת תקן · קידוח הפקה"
    value: "101"
    unit: "%"
    tier: urgent
    delta: "▲ +101 pp מעל ספי תקן (04/2025)"
    note: "מק חולון 14 · TCE 7.59 µg/L"

  - id: active_boreholes
    label: "קידוחי ליבה פעילה"
    value: "~58"
    tier: teal
    delta: "נדגמו 2021–2026 · מעבר לדלק"
    note: "ליבה אנליטית של הדוח."

  - id: monitoring_gaps
    label: "פערי ניטור"
    value: "7"
    unit: "+ קידוחים"
    tier: urgent
    delta: "▲ 39–150+ חודשי שתיקה"
    note: "כולל קידוחים בריכוזי שיא ושני דפוסי 'שתיקה מתואמת'"

  - id: pfas_coverage
    label: "כיסוי PFAS"
    value: "3.6"
    unit: "%"
    tier: urgent
    delta: "כל הנדגמים תחת הסף · אתרי סיכון לא נדגמו"
    note: "נקודה עיוורת ב-AFFF וציפוי כרום."

# ─── PUBLIC §01 — Stat cards (lighter) ──────────────────────────────
stats_public:
  - k: "קידוחים שנדגמו"
    v: "~58"
    tier: teal
    note: "מהווים את 'ליבת הניטור' — נדגמו לפחות פעם אחת ב-5 השנים האחרונות."

  - k: "חריגת תקן · קידוח אספקה"
    v: "1"
    tier: red
    note: "קידוח אספקה (מק חולון 14) חצה ב-04/2025 את תקן TCE. המדידות הבאות חזרו מתחת לסף."

  - k: "שיקום מוצלח"
    v: "×57"
    tier: green
    note: "ירידה בריכוז ניקל באתר רימטל לאחר התערבות שיקום — מודל הצלחה."

# ─── INTERNAL §02 — Severity by contaminant family ──────────────────
family_ledger:
  - family: CVOC
    desc: "ממסים כלורניים"
    narrative: "המשפחה הדומיננטית. שני מוקדי DNAPL עיקשים (תדירגן, אלביט), פלאום 1,4-דיאוקסן מתפשט, והופעת VC ב-נת חולון 11. חריגת תקן ראשונה בקידוח הפקה לאחר עשור."
    count_value: "×9"
    count_label: "קידוחים בסף"

  - family: METALS
    desc: "מתכות וכרום"
    narrative: "סיפור מעורב — הצלחת שיקום ברימטל (Ni פי 57↓), אך כרום נקודתי בנת חולון 26 ועליית סטרונציום באתרים משוקמים."
    count_value: "×4"
    count_label: "קידוחים בסף"

  - family: PFAS
    desc: "פר-/פוליפלואוריים"
    narrative: "נקודה עיוורת. כיסוי ~3.6%, כל הנדגמים תחת הסף — אך מתקני הסיכון הגבוה (AFFF, ציפוי כרום) לא נדגמו."
    count_value: "0/2"
    count_label: "חיובי / נדגם"
    dim: true

  - family: FUEL
    desc: "פחמימני דלק · BTEX/MTBE"
    narrative: "רקע ספציפי-לאתר. מוקדי MTBE סביב תחנות דלק ואגד, אך ללא חציית תקן ברורה בקידוחי הליבה."
    count_value: "×2"
    count_label: "קידוחים בסף"
    dim: true

# ─── Both reports §03 — Seven findings ──────────────────────────────
findings:

  - id: F1
    urgency: critical
    title_internal: "חריגת תקן בקידוח הפקה"
    title_public:   "חציית סף בקידוח אספקה"
    body_internal: "מק חולון 14 חצה ב-<bdi>04/2025</bdi> את תקן TCE הישראלי (<bdi>7.59 µg/L</bdi> ≈ <strong style=\"color:var(--red)\"><bdi>101%</bdi> מהתקן</strong>) לראשונה זה עשור. המדידות שלאחר מכן ירדו מתחת לתקן."
    body_public: "בחודש <bdi>אפריל 2025</bdi> חצה קידוח אספקה אחד את תקן TCE (ממס תעשייתי) ברמה של <strong>פי <bdi>1.01</bdi> מהתקן</strong> — לראשונה זה עשור. הניטור הוגבר מיד, והמדידות הבאות חזרו מתחת לתקן."
    action_internal: "דרושה הצהרה רגולטורית, ניטור חודשי בקידוח, ובדיקת נתיב אספקה לרשת. שיקול השעיה זהירה לקידוחים סמוכים (מק 12, 23) במידה ותחזור עלייה."
    public_what_it_means: "אירוע שדורש מעקב צמוד. החריגה הייתה רגעית; המים שיוצאים מהקידוח עוברים תהליך טיפול לפני אספקה לרשת."
    public_what_we_do: "ניטור חודשי תכוף בקידוח, בדיקת נתיב האספקה, ובחינת קידוחים סמוכים."
    stat: { value: "×1.01", label: "פי תקן · 04/2025", color: red }
    metadata:
      - { k: "קידוח", v: "מק חולון 14" }
      - { k: "מזהם", v: "TCE" }
      - { k: "ריכוז", v: "7.59 µg/L", color: red }
      - { k: "% תקן", v: "101%", color: red }
      - { k: "תאריך", v: "04/2025" }
    certainty: medium

  - id: F2
    urgency: critical
    title_internal: "DNAPL עיקש · תדירגן/סונול"
    title_public:   "מוקד תעשייתי היסטורי עיקש"
    body_internal: "נד סונול המלאכה מ-1 מציג TCE <bdi>2,722 µg/L</bdi> (<bdi>01/2026</bdi>) — יציב לאורך 3 שנים, על אף שיקום ISCO שבוצע באתר הציפוי הסגור בין <bdi>2013–2020</bdi>."
    body_public: "באחד מאתרי הציפוי הסגורים מ-<bdi>2013</bdi> אנחנו ממשיכים למדוד ריכוזים גבוהים של TCE, גם לאחר טיפול שיקום של 7 שנים. זה מצביע על <strong>מקור עומק שלא נוקה</strong>."
    action_internal: "מצביע על מקור עומק שלא נוקה. נדרשת חקירת DNAPL רב-מפלסית בתדירגן + אלביט + הפלד-הסדנה. ייתכן שיש להחזיר ל-ISCO שלב ב׳."
    public_what_it_means: "המים בקידוחי הניטור באתר אינם משמשים לאספקה. הזיהום ממוקד וידוע, ואינו מתפשט באופן משמעותי לסביבה."
    public_what_we_do: "חקירת מקור הזיהום בעומק, ובחינת אפשרות לשלב נוסף של טיפול שיקום."
    stat: { value: "2,722", label: "µg/L · יציב 3 שנים", color: red }
    metadata:
      - { k: "קידוח", v: "נד סונול ה.מ-1" }
      - { k: "מזהם", v: "TCE" }
      - { k: "ריכוז", v: "2,722 µg/L", color: red }
      - { k: "% תקן", v: "36,293%", color: red }
      - { k: "מקור", v: "תדירגן · ציפוי" }
    certainty: high

  - id: F3
    urgency: critical
    title_internal: "התפשטות 1,4-דיאוקסן"
    title_public:   "מזהם חדש מתפשט לעבר אזור חקלאי"
    body_internal: "הפלאום מתפשט מהאשכול התעשייתי אל קידוח חקלאי במרחק ~1 ק״מ. נת חווה חקלאית א: <bdi>38.8 µg/L</bdi> (<bdi>02/2026</bdi>) ≈ <bdi>1,293%</bdi> מתקן EPA. נת חולון 11 הגיע ל-<bdi>1,036 µg/L</bdi>."
    body_public: "זוהה פלאום של מזהם פחות מוכר (1,4-דיאוקסן) שמתפשט מהאשכול התעשייתי לקידוח חקלאי במרחק כקילומטר. הריכוזים מצטברים — נדרשת חקירת מקור והגברת הניטור."
    action_internal: "דיגום חוזר דחוף בקידוחי החוות. חיפוש במרשם התעשייה אחר יצרני PVDC ושימושי דיאוקסן. הרחבת פאנל CVOC לכלול דיאוקסן בכל הליבה."
    public_what_it_means: "המזהם אינו עומד בתקן ה-EPA האמריקאי (תקן רפרנס; אין עדיין תקן ישראלי רשמי). הקידוח החקלאי בו זוהה אינו מספק מים לשתייה."
    public_what_we_do: "דיגום חוזר דחוף, איתור מקור הזיהום במרשם התעשייה, והרחבת פאנל הבדיקות."
    stat: { value: "×13", label: "מתקן EPA · קידוח חקלאי", color: red }
    metadata:
      - { k: "קידוח שיא", v: "נת חולון 11" }
      - { k: "מזהם", v: "1,4-Dioxane" }
      - { k: "שיא", v: "1,036 µg/L", color: red }
      - { k: "% EPA", v: "34,533%", color: red }
      - { k: "תאריך", v: "02/2026" }
    certainty: low

  - id: F4
    urgency: high
    title_internal: "פערי ניטור שיטתיים"
    title_public:   "אזורים שבהם הניטור צריך להתחזק"
    body_internal: "שבעה קידוחים ואשכולות שקטים בין 39 ל-150+ חודשים — חלקם בריכוזי שיא היסטוריים. מזוהים שני דפוסי 'שתיקה מתואמת' באשכולות אגד ובקידוחי נת חולון 2 + נד המרכבה ק2."
    body_public: "שבעה קידוחים — חלקם בריכוזי שיא היסטוריים — לא נדגמו בין <strong>39 ל-150 חודשים</strong>. אנחנו מתחייבים לחדש את הדיגום בכולם ולוודא שאף אזור סיכון לא יוצא ממערך המעקב."
    action_internal: "חידוש דיגום CVOC מיידי בכל השבעה. סקירת אחריות תפעולית — מי הופסק להידגם וכיצד נפל מהתכנית."
    public_what_it_means: "פערי ניטור הם נושא שמתפרסם במסמך זה ב<strong>שקיפות מלאה</strong> — לא כדי להמעיט בחשיבותם, אלא כדי להציג את התמונה האמיתית."
    public_what_we_do: "חידוש דיגום בכל שבעת הקידוחים והאשכולות, וביצוע סקירה תפעולית של תהליך תיעדוף הניטור."
    stat: { value: "7+", label: "קידוחים שותקים", color: red }
    metadata:
      - { k: "קידוחים שקטים", v: "7+" }
      - { k: "טווח שתיקה", v: "39–150+ ח׳" }
      - { k: "דפוסים", v: "×2 אשכולות" }
      - { k: "קטגוריה", v: "תפעולית" }
    certainty: high

  - id: F5
    urgency: high
    title_internal: "הופעת ויניל-כלוריד"
    title_public:   "זיהוי תוצר פירוק מסרטן"
    body_internal: "ב-נת חולון 11 זוהה VC <bdi>13.8 µg/L</bdi> (<bdi>11/2024</bdi>) — <bdi>2,767%</bdi> מתקן EPA, לאחר שנות אפס. VC הוא תוצר פירוק מסרטן (group 1) המעיד על דה-הלוגנציה אנאירובית פעילה."
    body_public: "לראשונה זוהה בקידוח ניטור תוצר לוואי של פירוק כימי — חומר המסווג כמסרטן (VC). הריכוזים נמוכים מבחינה מוחלטת אך גבוהים יחסית לסף הבריאותי האמריקאי."
    action_internal: "דיגום דופליקט לאישוש. הוספת תוצרי פירוק (VC, ethene) לפאנל הליבה. בדיקת אם דה-הלוגנציה טבעית או תוצר התערבות שיקום."
    public_what_it_means: "הקידוח אינו משמש לאספקה. הימצאות החומר מעידה על כך שתהליך פירוק כימי טבעי או יזום פעיל באזור."
    public_what_we_do: "דיגום נוסף לאישוש, והוספת בדיקות לתוצרי פירוק נוספים בפאנל הקבוע."
    stat: { value: "13.8", label: "µg/L · קידוח ניטור", color: red }
    metadata:
      - { k: "קידוח", v: "נת חולון 11" }
      - { k: "מזהם", v: "VC" }
      - { k: "ריכוז", v: "13.8 µg/L", color: red }
      - { k: "% EPA", v: "2,767%", color: red }
      - { k: "משמעות", v: "מסרטן · פירוק" }
    certainty: medium

  - id: F6
    urgency: high
    title_internal: "נקודה עיוורת PFAS"
    title_public:   "פערי כיסוי לחומרי PFAS"
    body_internal: "רק ~3.6% מקידוחי הליבה נדגמו ל-PFAS. כל הנדגמים אפס — אך אתרי AFFF (קצף-כיבוי בתחנות דלק ומחנות צה״ל) ואתרי ציפוי כרום (שהשתמשו ב-PFOS עד 2010) לא נדגמו."
    body_public: "משפחת מזהמים נוספת (PFAS — 'כימיקלים נצחיים') נבדקה רק ב-<bdi>~3.6%</bdi> מהקידוחים. <strong>כל הקידוחים שנדגמו היו תקינים</strong>, אך אנחנו עדיין לא דגמנו במתקני הסיכון הגבוה. נדרש קמפיין דיגום ממוקד."
    action_internal: "קמפיין דיגום ממוקד של 8–12 קידוחים סביב מתקני AFFF וציפוי. תלוי תקציב — להעלות בישיבת תקציב Q3."
    public_what_it_means: "פער הכיסוי הזה מפורסם בשקיפות. הקמפיין יכלול 8–12 קידוחים נוספים סביב מתקני סיכון."
    public_what_we_do: "תכנון קמפיין דיגום PFAS ייעודי בקידוחים חדשים וקיימים."
    stat: { value: "3.6%", label: "כיסוי נוכחי", color: neutral }
    metadata:
      - { k: "כיסוי", v: "3.6%", color: red }
      - { k: "חיוביים", v: "0/2" }
      - { k: "פערים", v: "AFFF · ציפוי" }
      - { k: "קמפיין", v: "8–12 קידוחים" }
    certainty: high

  - id: F7
    urgency: good
    title_internal: "הצלחת שיקום · רימטל"
    title_public:   "שיקום מוצלח — מודל לאתרים אחרים"
    body_internal: "קידוחי רימטל מציגים ירידה של פי ~57 בניקל: מ-<bdi>2.0 mg/L</bdi> אל <bdi>13.8 µg/L</bdi> בעקבות סגירת בור ספיגה וניקוי קרקע (<bdi>2023</bdi>). מודל הצלחה ראוי לשכפול."
    body_public: "באתר מחזור מתכות הוכיחו פעולות שיקום (סגירת בור ספיגה + ניקוי קרקע) ירידה דרמטית בריכוזי ניקל — <strong>פי 57 פחות</strong> תוך שלוש שנים. זהו מודל הצלחה שאנחנו מתעדים ומבקשים לשכפל באתרים דומים."
    action_internal: "לתעד כ-case study, להחיל על אתרים דומים. אזהרה נלווית: עליית סטרונציום באותם קידוחים — לעקוב."
    public_what_it_means: "פעולות שיקום ממוקדות עובדות. זוהי הוכחה שתהליך השיקום הסביבתי באזה״ת חולון מניב תוצאות."
    public_what_we_do: "תיעוד מתודולוגי של ההצלחה, והחלת המודל על אתרים נוספים שעדיין דורשים טיפול."
    stat: { value: "×57 ↓", label: "ירידה · 2.0 mg/L → 13.8 µg/L", color: green }
    metadata:
      - { k: "קידוח", v: "רימטל" }
      - { k: "מזהם", v: "Ni" }
      - { k: "לפני", v: "2.0 mg/L" }
      - { k: "אחרי", v: "13.8 µg/L" }
      - { k: "שינוי", v: "×57 ↓", color: green }
    certainty: high

# ─── Boreholes ──────────────────────────────────────────────────────
boreholes:
  - id: MK-14
    name_he: "מק חולון 14"
    role: "קידוח הפקה"
    tier: critical
    coords: [32.01510, 34.78090]
    on_severity_matrix: true
    severity_by_family: { CVOC: 8, Dioxane: 4, VC: 0, METALS: 2, PFAS: 0, FUEL: 2 }
    popup_rows_internal:
      - { k: "מזהם", v: "TCE" }
      - { k: "ריכוז", v: "7.59 µg/L" }
      - { k: "% תקן", v: "101%", color: red }
      - { k: "תאריך", v: "04/2025" }
      - { k: "חומרה", v: "s8", color: red }
    public:
      code: "B-01"
      desc: "קידוח אספקה"
      tier: crit
      popup_rows:
        - { k: "חומרה", v: "גבוהה", color: red }
        - { k: "חריגת תקן", v: "×1.01 (04/2025)", color: red }
        - { k: "מזהם", v: "TCE" }

  - id: SONOL-1
    name_he: "נד סונול ה.מ-1"
    role: "ניטור · DNAPL"
    tier: critical
    coords: [32.01180, 34.78870]
    on_severity_matrix: true
    severity_by_family: { CVOC: 8, Dioxane: 6, VC: 4, METALS: 5, PFAS: 0, FUEL: 3 }
    public:
      code: "B-02"
      desc: "קידוח ניטור"
      tier: crit
      popup_rows:
        - { k: "חומרה", v: "גבוהה מאוד", color: red }
        - { k: "מזהם", v: "ממס תעשייתי" }
        - { k: "הקשר", v: "מוקד תעשייתי היסטורי" }

  - id: NT-11
    name_he: "נת חולון 11"
    role: "ניטור"
    tier: critical
    coords: [32.01340, 34.78580]
    on_severity_matrix: true
    severity_by_family: { CVOC: 8, Dioxane: 8, VC: 8, METALS: 4, PFAS: 0, FUEL: 3 }
    public:
      code: "B-03"
      desc: "קידוח ניטור"
      tier: crit
      popup_rows:
        - { k: "חומרה", v: "גבוהה", color: red }
        - { k: "מזהמים", v: "דיאוקסן · VC" }
        - { k: "הקשר", v: "פלאום מתפשט" }

  - id: FARM-A
    name_he: "נת חווה חקלאית א"
    role: "קידוח חקלאי"
    tier: critical
    coords: [32.02020, 34.77380]
    on_severity_matrix: true
    severity_by_family: { CVOC: 6, Dioxane: 8, VC: 3, METALS: 2, PFAS: 0, FUEL: null }
    public:
      code: "B-04"
      desc: "קידוח חקלאי"
      tier: crit
      popup_rows:
        - { k: "חומרה", v: "גבוהה", color: red }
        - { k: "מזהם", v: "1,4-דיאוקסן" }
        - { k: "הקשר", v: "אינו לאספקה" }

  - id: NT-26
    name_he: "נת חולון 26"
    role: "ניטור"
    tier: high
    coords: [32.01040, 34.78320]
    on_severity_matrix: true
    severity_by_family: { CVOC: 5, Dioxane: 2, VC: 0, METALS: 7, PFAS: 0, FUEL: 2 }
    public:
      code: "B-05"
      desc: "קידוח ניטור"
      tier: high
      popup_rows:
        - { k: "חומרה", v: "גבוהה" }
        - { k: "מזהם", v: "כרום (Cr)" }

  - id: TADIRAN-NM
    name_he: "נד תדירגן"
    role: "חוץ-ליבה"
    tier: high
    coords: [32.00950, 34.79080]
    on_severity_matrix: true
    severity_by_family: { CVOC: 7, Dioxane: 4, VC: 5, METALS: 5, PFAS: 0, FUEL: 2 }
    public:
      code: "B-06"
      desc: "חוץ-ליבה"
      tier: high
      popup_rows:
        - { k: "חומרה", v: "גבוהה" }
        - { k: "מזהם", v: "CVOC" }

  - id: ELBIT-NM
    name_he: "נד אלביט"
    role: "ניטור"
    tier: high
    coords: [32.00840, 34.78950]
    on_severity_matrix: true
    severity_by_family: { CVOC: 6, Dioxane: 3, VC: 2, METALS: 4, PFAS: 0, FUEL: 2 }
    public:
      code: "B-07"
      desc: "קידוח ניטור"
      tier: high
      popup_rows:
        - { k: "חומרה", v: "גבוהה" }
        - { k: "מזהם", v: "CVOC" }

  - id: EGGED-CL
    name_he: "אשכול אגד"
    role: "שותק · 74 ח׳"
    tier: silent
    silent_months: 74
    coords: [32.01390, 34.79320]
    on_severity_matrix: true
    severity_by_family: { CVOC: 4, Dioxane: 0, VC: 0, METALS: 2, PFAS: 0, FUEL: 5 }
    public:
      code: "B-08"
      desc: "טרם נדגם לאחרונה"
      tier: silent
      popup_rows:
        - { k: "סטטוס", v: "חידוש דיגום מתוכנן", color: red }

  - id: NT-2
    name_he: "נת חולון 2"
    role: "שותק · 47 ח׳"
    tier: silent
    silent_months: 47
    coords: [32.01530, 34.78760]
    on_severity_matrix: true
    severity_by_family: { CVOC: 3, Dioxane: 0, VC: 0, METALS: 2, PFAS: 0, FUEL: 2 }
    public:
      code: "B-09"
      desc: "טרם נדגם לאחרונה"
      tier: silent
      popup_rows:
        - { k: "סטטוס", v: "חידוש דיגום מתוכנן", color: red }

  - id: MRK-K2
    name_he: "נד המרכבה ק2"
    role: "שותק"
    tier: silent
    silent_months: 60
    coords: [32.00720, 34.78720]
    public:
      code: "B-10"
      desc: "טרם נדגם לאחרונה"
      tier: silent
      popup_rows:
        - { k: "סטטוס", v: "חידוש דיגום מתוכנן", color: red }

  - id: REMITAL
    name_he: "רימטל"
    role: "משוקם · case study"
    tier: success
    coords: [32.00690, 34.79140]
    on_severity_matrix: true
    severity_by_family: { CVOC: 2, Dioxane: 0, VC: 0, METALS: 3, PFAS: 0, FUEL: 3 }
    public:
      code: "B-11"
      desc: "אתר משוקם"
      tier: success
      popup_rows:
        - { k: "שינוי", v: "×57 ירידה", color: green }
        - { k: "מזהם", v: "ניקל" }
        - { k: "סטטוס", v: "שיקום מוצלח", color: green }

# ─── Sources (INTERNAL map only — never rendered in PUBLIC) ─────────
sources:
  - id: TADIRAN
    name_internal: "תדיראן קשר"
    name_generic:  "מפעל אלקטרוניקה / מתקן ביטחוני"
    certainty: high
    category: "אלקטרוניקה / ביטחוני"
    contaminants: [TCE, PCE, "כרומאט", "ציאנידים"]
    status: "פעיל"
    coords: [32.00990, 34.79050]

  - id: ELBIT
    name_internal: "אלביט"
    name_generic:  "מתקן ביטחוני"
    certainty: high
    category: "מתקן ביטחוני"
    contaminants: [TCE, PCE, DCE, "כרומאט"]
    status: "פעיל"
    coords: [32.00880, 34.78930]

  - id: TADIRGAN
    name_internal: "תדירגן"
    name_generic:  "מפעל ציפוי מתכות (סגור)"
    certainty: high
    category: "ציפוי מתכות"
    contaminants: [TCE, PCE, "כרומאט", "ציאנידים"]
    status: "סגור · שוקם 2013–2020"
    coords: [32.00950, 34.78250]

  - id: REMITAL-SRC
    name_internal: "רימטל"
    name_generic:  "מפעל מחזור מתכות"
    certainty: high
    category: "מחזור מתכות"
    contaminants: [Ni, Al, Cu, Pb, TPH]
    status: "משוקם"
    coords: [32.00710, 34.79180]

# ─── Plume polylines ────────────────────────────────────────────────
plume_paths:
  - path:
      - [32.01340, 34.78580]
      - [32.01600, 34.78200]
      - [32.01850, 34.77750]
      - [32.02020, 34.77380]
    label: "פלאום 1,4-דיאוקסן · כיוון התפשטות"
    color: red

# ─── INTERNAL §05 — Decisions matrix ────────────────────────────────
decisions:
  - category: "עדכון תכנית הניטור"
    actions:
      - action: "ניטור חודשי במק 14"
        need:   "מעבר לדיגום TCE + 1,4-דיאוקסן חודשי בקידוח ההפקה שחצה תקן."
        notes:  "חריגה 101% | F·01"
        finding_refs: [F1]
      - action: "חידוש קידוחים שקטים"
        need:   "החזרת נת חולון 2 + נד המרכבה ק2 + אשכול אגד לדיגום CVOC."
        notes:  "פער 47–74 ח׳ | F·04"
        finding_refs: [F4]
      - action: "הרחבת פאנל"
        need:   "הוספת 1,4-דיאוקסן ותוצרי פירוק (VC, ethene) לפאנל ה-CVOC."
        notes:  "F·03, F·05"
        finding_refs: [F3, F5]

  - category: "קידוחי ניטור חדשים"
    actions:
      - action: "קמפיין PFAS"
        need:   "קידוח/דיגום 8–12 קידוחים באתרי סיכון (מרכבות האש, אגד, ציפוי, הפקה)."
        notes:  "תלוי תקציב | F·06"
        finding_refs: [F6]
      - action: "קידוחים חקלאיים"
        need:   "דגימה חוזרת דחופה בנת חווה חקלאית א/ב."
        notes:  "דחוף | F·03"
        finding_refs: [F3]

  - category: "חקירת מקורות זיהום"
    actions:
      - action: "מיפוי DNAPL בעומק"
        need:   "חקירת מקור עומק בתדירגן/סונול, אלביט, הפלד-הסדנה."
        notes:  "ודאות גבוהה | F·02"
        finding_refs: [F2]
      - action: "איתור מקור 1,4-דיאוקסן"
        need:   "חיפוש במרשם התעשייה אחר יצרני PVDC/דיאוקסן."
        notes:  "ראשון מסוגו | F·03"
        finding_refs: [F3]

  - category: "מדיניות הפקה"
    actions:
      - action: "הצהרה רגולטורית"
        need:   "דיווח על חריגת מק חולון 14 + הערכת נתיב אספקה לרשת."
        notes:  "דחוף | F·01"
        finding_refs: [F1]
      - action: "קריטריון השעיה"
        need:   "מדיניות השעיה זהירה לקידוחי הפקה בסיכון (מק חולון 12, 23)."
        notes:  "מניעתי"

# ─── PUBLIC §02 — Timeline events ───────────────────────────────────
timeline:
  - id: T1
    period: "1965–85"
    type: hist
    label: "רקע"
    text:  "הקמת אזור התעשייה. תקופת הזיהום ההיסטורית."
    position_pct: 8
    layer: B
    edge: left

  - id: T2
    period: "2000"
    type: hist
    label: "מעקב"
    text:  "תחילת ניטור שיטתי של מי-התהום באזור."
    position_pct: 38
    layer: C

  - id: T3
    period: "2013–20"
    type: hist
    label: "שיקום"
    text:  "פעולות שיקום באתרים תעשייתיים סגורים."
    position_pct: 55
    layer: A

  - id: T4
    period: "2023"
    type: good
    label: "הצלחה ✓"
    text:  "ירידה של פי 57 בריכוז ניקל באתר משוקם."
    position_pct: 80
    layer: D

  - id: T5
    period: "11/2024"
    type: crit
    label: "התראה"
    text:  "זיהוי תוצר פירוק מסרטן (VC) בקידוח ניטור."
    position_pct: 89
    layer: A
    edge: right

  - id: T6
    period: "04/2025"
    type: crit
    label: "חריגה"
    text:  "קידוח אספקה חצה את תקן TCE — לראשונה זה עשור."
    position_pct: 94
    layer: C
    edge: right

  - id: T7
    period: "02/2026"
    type: cur
    label: "עדכני"
    text:  "פלאום 1,4-דיאוקסן מתפשט לעבר אזור חקלאי."
    position_pct: 98
    layer: B
    edge: right

# ─── PUBLIC §05 — What it means · what we do ────────────────────────
means_summary:
  - label: "סיכום · א"
    title: "הסיפור הגדול הוא לא דרמטי, אבל גם לא רגוע"
    body: "<p>רוב המים באזה״ת חולון תקינים. אבל יש שני סוגי 'סיפורי-משנה' שאנחנו לוקחים ברצינות: <strong>מוקדים היסטוריים</strong> שעדיין משפיעים על איכות המים המקומית, ו<strong>איתות חדש</strong> של מזהם פוטנציאלי שמתפשט לעבר אזור חקלאי.</p><p>אנחנו לא מתעלמים מאף אחד מהם, וגם לא מגזימים בדרמה. הדוח הזה הוא הניסיון שלנו להציג את התמונה כפי שהיא.</p>"

  - label: "סיכום · ב"
    title: "מה אנחנו עושים מעכשיו"
    body: "<ul><li>חידוש דיגום בכל הקידוחים שלא נדגמו לאחרונה — ביטול 'פערי השתיקה'.</li><li>קמפיין PFAS ממוקד באזורים שעדיין לא נדגמו.</li><li>הגברת ניטור בקידוח האספקה שחצה את התקן, ובחינת קידוחים סמוכים.</li><li>חקירת מקור פלאום ה-1,4-דיאוקסן ואיתורו במרשם התעשייה.</li><li>הוספת תוצרי פירוק נוספים לפאנל בדיקות הקבוע.</li><li>תיעוד מודל ההצלחה של רימטל והחלתו על אתרים דומים.</li></ul>"

  - label: "סיכום · ג"
    title: "מה הדוח הזה לא אומר"
    body: "<p>הדוח <strong>אינו</strong> מסקנה לגבי המים שזורמים בברז שלכם. רוב המים באזור עוברים תהליכי טיפול, ובדיקות איכות מתבצעות בנקודות אספקה נפרדות.</p><p>הדוח גם <strong>אינו תחליף</strong> למסמכים מקצועיים מלאים — הוא תקציר. מי שמעוניין בנתונים גולמיים מוזמן לפנות אלינו.</p>"

  - label: "סיכום · ד"
    title: "למה לפרסם דוח כזה"
    body: "<p>מי-תהום הוא משאב ציבורי. ניטור איכותו ממומן מכספי ציבור, והממצאים שייכים לציבור.</p><p>שקיפות במצב הסביבה היא חלק מהמחויבות שלנו, גם — ובמיוחד — כשהממצאים אינם נוחים. דוח זה הוא צעד אחד בכיוון הזה, ולא אחרון.</p>"

# ─── PUBLIC §06 — Methodology ───────────────────────────────────────
methodology:
  - title: "מקור הנתונים"
    body:  "מסד נתוני הניטור של רשות המים, אגף מי-תהום. נתונים מתאריכי דיגום 01/2020 – 02/2026."
  - title: "קריטריון השוואה"
    body:  "תקנות מי-שתייה (2013) לישראל. עבור מזהמים ללא תקן ישראלי, השוואה לתקני EPA אמריקאיים."
  - title: "חישוב חומרה"
    body:  "מבוסס על C_max ב-5 השנים האחרונות, כאחוז מהתקן. ערכים מוצגים בפועל, לא מעובדים סטטיסטית."

# ─── PUBLIC footer ──────────────────────────────────────────────────
contact:
  email: water@water.gov.il
  raw_data_note: "לבירורים נוספים, גישה לנתונים גולמיים, או בקשות מקצועיות"
