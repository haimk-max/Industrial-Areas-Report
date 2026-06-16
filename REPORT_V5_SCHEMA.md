# Report V5 Schema — Generic Structure

**מטרה**: הגדרת מבנה הדוח הגנרי עבור כל אזור בהיברידי pipeline.

**תפקיד**: קובץ זה מגדיר את ה-scaffold עבור כל V5 report, ללא תוכן ספציפי לאזור.

**שימוש**: Opus מקבל את סכמה זה כחלק מה-prompt; reviewer משתמש בו להוודא עקביות.

---

## V5 Report — 6 Sections + Appendices

```
# דוח איכות מים — אזור [שם אזור]

## 1. תקציר מקצועי
[2-3 פסקאות]

## 2. תמונת מצב אזורית ומערך הניטור
[גיאוגרפיה, הידרוגיאולוגיה, מערך קידוחים]
### איור 1: מפת קידוחים ומוקדים

## 3. מוקדי זיהום עיקריים

### 3.1 / 3.2 / ... [מוקדים גיאוגרפיים לפי חומרת-מוקד יורדת — ראה §IV]
[תבנית מוקד חוזרת לכל אחד]

## 4. מגמות, החמרה ופערי ניטור
[מגמות, closed wells, gaps]

## 5. מקורות זיהום אפשריים ורמות ביטחון
[טבלה + הערות HIGH/MEDIUM/LOW]

## 6. המלצות
[Immediate / Short-term / Long-term]

## 7. מתודולוגיה
[קצר: formula, MK, selection bias]

## 8. מגבלות
[Data gaps, assumptions]

## נספחים
[א–ד]
```

---

## Section 1: תקציר מקצועי (Executive Summary)

**מטרה**: קריאה מהירה של המוקדים העיקריים, התשנויים מ-2021, פערים קריטיים, דחיפות.

**תוכן**:
- X מוקדי זיהום עיקריים (שמות, מזהמים דומיננטיים, ריכוזים כ-% of standard)
- שינויים מדוח 2021 (אם יש: חומרה עלתה/ירדה, מוקד חדש, וכו')
- פערי מידע קריטיים (parameter שלא נשקל, אזור ללא ניטור)
- האם נדרשת תגובה מיידית? (סימן שאלה / דיגום אישור / סגירה קידוח?)

**אורך**: 2-3 פסקאות (כ-200 מילים).

---

## Section 2: תמונת מצב אזורית ומערך הניטור

**מטרה**: הקשר גיאוגרפי + מערך פיזי של קידוחים.

**תוכן**:
- **גיאוגרפיה**: אזור בין-אזורי / קואורדינטות ITM / מיקום יחסי (כמו "צפוניות מ-תל-אביב")
- **הידרוגיאולוגיה**: אקוויפר (עמוק / שטחי / מוגבל?), כיוון זרימה, שכבות
- **מערך קידוחים**: מספר כולל (לדוג' "80 קידוחים פעילים"), חלוקה לסוגים (ניטור / אספקה / תצפית), סטטוס (פעיל / סגור)
- **איור 1**: מפה עם קידוחים ומוקדי זיהום מסומנים

**אורך**: 1-2 פסקאות + איור.

---

## Section 3: מוקדי זיהום עיקריים

**מטרה**: תיאור מפורט של כל מוקד זיהום גיאוגרפי, ובתוכו המשפחות הכימיות הדומיננטיות.

**סדר**: לפי מוקד גיאוגרפי (חומרת-מוקד יורדת); משפחות בתוך מוקד לפי §IV. סעיף "פערי כיסוי" אחרון.

### תבנית לכל מוקד (חוזרת)

```markdown
#### [3.1 / 3.2 / ...] מוקד [שם: רחוב / מפעל / אזור קוד]

**קידוחים מרכזיים**: [names + coordinates]

**מזהמים מובילים**: [list + sev index]
- TCE: אינדקס 8 (8,750% of standard)
- PCE: אינדקס 7 (1,200% of standard)

**ריכוזים ותאריכים**: [טבלה קצרה (3-5 שורות)]
| קידוח | parameter | ערך | תאריך | % of standard |
| ... | ... | ... | ... | ... |

**מגמות**: [Z, p, SNR, soft_trigger; קטגוריה]
- TCE בקידוח nt_1: Z=2.3, p=0.02, SNR=6.1, soft_trigger=true → **עלייה מובהקת**
- PCE בקידוח nt_3: Z=1.8, p=0.07, SNR=4.2 → **עלייה חלשה**

**קשר לדוח 2021**: [מה השתנה מ-2021? חומרה עלתה? קידוח חדש?]

**מקורות אפשריים**: [שם מפעל, סוג עסק, רמת ביטחון]
- מפעל ציפוי "אלגונל" (HIGH): address confirmed, Cr+Ni expected, 2010-present operative
- מפעל כימיקלים "כימי-ישראל" (MEDIUM): location ~800m away, CVOC expected, dates overlap

**פערי מידע**: [מה חסר?]
- PFAS לא נדגם בקידוח זה
- מדידות בחלון 5-שנים: רק 3 (הוגבל)

**פעולה נדרשת**: [מה צריך?]
- דיגום אישור TCE בחודשים הקרובים
- ניטור משופר לאחרונה (ramp up frequency)
```

**הערה**: תבנית זו חוזרת לכל מוקד גיאוגרפי (3.1, 3.2, ...). סדר = לפי §IV.

---

## Section 4: מגמות, החמרה ופערי ניטור

**מטרה**: ריכוז של תוצאות Mann-Kendall + תיעוד של פערים.

**תוכן**:
- **מגמות בולטות** (רק p<0.05 + SNR>5): רשימה של 3-5 מגמות משמעותיות בלבד (לא כל קידוח)
- **קידוחים שהופסק ניטורם** (closed wells): שמות + תאריך סגירה + סיבה
- **פערי ניטור אזוריים** (regional gaps): אזורים ללא קידוחים, parameters שלא נשקלו (לדוג' "PFAS gap בדרום-מערב")
- **Selection bias caveat**: "קידוחי ניטור הותקנו במכוון בסמיכות למקורות חשודים ולא נציגים של תפוצה אזורית"

**אורך**: 1.5-2 פסקאות + 1-2 טבלאות קטנות אם צריך.

---

## Section 5: מקורות זיהום אפשריים ורמות ביטחון

**מטרה**: סיכום מובנה של שיוך מזהמים למקורות.

**תוכן**:
- **טבלה קצרה** (5-10 שורות):

| מוקד | מזהם עיקרי | מפעל משוער | סוג עסק | רמת ביטחון |
|------|-----------|-----------|--------|----------|
| תדירגן | TCE | אלגונל | ציפוי מתכת | HIGH |
| סונול | CVOC | כימי-ישראל | ייצור כימיקלים | MEDIUM |
| דלק/אגד | BTEX | תחנה דלק טבעת | דלק | HIGH |

- **רמות ביטחון**: HIGH = address confirmed + parameter match + years overlap; MEDIUM = 2/3; LOW = 1/3

---

## Section 6: המלצות (Recommendations)

**מטרה**: פעולות מובנות לפי טווח זמן.

**תוכן**:
- **Immediate (30-90 ימים)**:
  - דיגום אישור TCE בקידוח X
  - בדיקה PFAS ראשונית בקידוח Y
  
- **Short-term (2026-2027)**:
  - בדיקת עומק בדרום-מערב
  - ניטור משופר בקידוח Z
  
- **Long-term (2027+)**:
  - עדכון מודל אזורי
  - הערכה של תיקון מקורות
  - ניטור רציף של מגמות

**אורך**: 0.5-1 פסקה + bullet list.

---

## Section 7: מתודולוגיה (Concise)

**מטרה**: הסברה קצר של שיטות (בלי פרטים מלאים).

**תוכן**:
- **אינדקס חומרה**: `bucket(C_max_5y / DWS × 100)` — חלון 5 שנים, טבלת 9-רמות
- **Mann-Kendall**: tie-corrected, SNR gate (SNR > 5 למובהק), soft_trigger = 2 consecutive rising values
- **מנין קידוחים**: X קידוחי תעשייה + Y קידוחי דלק = Z כ"סה
- **Selection bias**: קידוחים בדיוק למקורות, לא נציגים אזוריים
- **Caveats**: פערי ניטור (closed wells, n<5), הנחות על מקורות
- **הפניה**: ראה PROCESS_GUIDE §III לפרטים טכניים מלאים

**אורך**: 5-10 שורות בלבד (לא משכפלת את המדריך).

---

## Section 8: מגבלות (Limitations)

**מטרה**: תיעוד מפורש של ההנחות וחוסרים.

**תוכן**:
- **פערי ניטור**: קידוחים שנסגרו (שמות + תאריכים), parameters עם n<5 מדידות
- **Time gaps**: שנים ללא מדידות בקידוחים מסוימים
- **Selection bias**: קידוחים הותקנו במכוון בסמיכות למקורות חשודים
- **Uncertainty in sources**: confidences של attribution (HIGH/MEDIUM/LOW תיעדו)
- **Extrapolation**: מגמות היסטוריות לא בהכרח ימשיכו

**אורך**: 1 פסקה.

---

## Appendices

### Appendix A: טבלאות מלאות
- כל הקידוחים + severity indices לפי משפחה
- כל המגמות (Z, p, SNR, soft_trigger)
- קידוחים חורגים (index ≥ 6)
- ממצאים בתאריכים חדישים

### Appendix B: פורנזיקה כימית (Forensics)
- Decay chains (TCE → DCE → VC)
- Co-occurrence patterns (Cr+Ni, CVOC+MTBE)
- Source signatures (BTEX ratios, DNAPL reasoning)
- Temporal evolution (2008 vs 2021 vs 2024)

### Appendix C: מועמדי מקורות מלאים
- PRTR query results
- Web search findings (B144, local directories, news)
- Facility histories (founding year, production changes, shutdowns)
- Distance + confidence matrix (well vs facility)

### Appendix D: Context Pack Excerpts
- טקסט מקורי מדוח 2021 (רלוונטי לאזור)
- TAHAL 2008 טקסט (אם קיים)
- citations (עמוד, טבלה, תאריך)

---

## Validation Checklist (for this schema)

- [ ] 6 sections present (1–6 content + 7–8 methodology/limits)
- [ ] Section 3 uses consistent sub-template for each focus
- [ ] PFAS always included (even if max_bucket=0)
- [ ] §3 headers are geographic foci (not bare family names); ordered by focus severity descending (ראה §IV)
- [ ] Severity scale: 5-level labels only (נקי/נמוך/בינוני/גבוה/גבוה מאוד)
- [ ] No English operational terminology (ALERT/WATCH/ELEVATED)
- [ ] Confidence levels (HIGH/MEDIUM/LOW) on all facility attributions
- [ ] Selection bias caveat explicit (§4 + §8)
- [ ] Monitoring gaps explicit (§4 + §8)
- [ ] Recommendations: Immediate/Short-term/Long-term structure
- [ ] Methodology concise (5-10 lines; refers to PROCESS_GUIDE §III for full details)
- [ ] All figures cited with image markdown

---

## Example Skeleton (Minimal)

```markdown
# דוח איכות מים — אזור חולון

## 1. תקציר מקצועי

[2-3 פסקאות על מוקדים, שינויים מ-2021, פערים, דחיפות]

## 2. תמונת מצב אזורית ומערך הניטור

[גיאוגרפיה, הידרוגיאולוגיה, מערך קידוחים]

### איור 1: מפת קידוחים ומוקדים

[map image placeholder]

## 3. מוקדי זיהום עיקריים

### 3.1 מוקד תדירגן

[תבנית]

### 3.2 מוקד סונול

[תבנית]

### 3.3 משפחות מזהמים — CVOC / METALS / PFAS / FUEL

[או: חלוקה לפי משפחה, תלוי בstructure]

## 4. מגמות, החמרה ופערי ניטור

[מגמות בולטות, closed wells, gaps]

## 5. מקורות זיהום אפשריים

[טבלה קצרה]

## 6. המלצות

[Immediate / Short / Long]

## 7. מתודולוגיה

[קצר]

## 8. מגבלות

[gaps, bias, uncertainty]

## נספחים

[א–ד]
```

---

## See Also

🔧 **Zone Diagnosis template** (self-contained playbook): `toolkit/playbooks/zone_diagnosis_template.md` (Step 4 of V5 pipeline — diagnostic questions, reading order, principles)

🔧 **V5 Report prompt** (Opus call reference): `scripts/templates/zone_report_prompt_template_v5.md`

---

**Last Updated**: 2026-05-17  
**Phase**: H+ (Hybrid V5 Pipeline — Documentation)  
**Last Sanitized**: 2026-05-27 (Back-references + toolkit pointers added)
