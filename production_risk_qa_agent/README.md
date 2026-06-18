# Production Risk Q&A Agent — חבילת קונטקסט וסיסטם פרומפט

**מטרה**: LLM-based Q&A component לשאלות סיכון זיקה מקור↔מוקד↔קידוחי הפקה.

**סביבה**: אזור תעשייה חולון (111 קידוחים פעילים, 15,170 מדידות).

---

## מה זה?

חבילה ניידת ומאוצרת המכילה:
1. **Context Pack**: CSV (נתונים) + MD (הקשר נרטיבי) מאזור חולון
2. **System Prompt**: הוראות ל-LLM לעיבוד שאלות סיכון בשני סגנונות
3. **XGBOOST Interface**: סכמה צפויה לפלט מודל XGBOOST חיצוני

**Setup זה L0-only** (ללא retrieval layer). רוב השאלות יתורנו מהשכבה הרדודה ביותר (Layer 0) — צמצום קונטקסט מכוון.

---

## קבצים עיקריים

### `SYSTEM_PROMPT.md`
System prompt בעברית (הוראות לLLM).

### `context_pack/00_manifest.md`
מילון + טעימות נתונים. התחל כאן אם אתה חדש.

### `context_pack/data/*.csv`
נתונים כמותיים: zone_wells, severity, trends, monitoring_gaps, וכו'.

### `context_pack/context/*.md`
הקשר נרטיבי: zone_diagnosis, hydrogeology, forensics_brief.

### `questions/test_questions.md`
8+ שאלות בדיקת איכות (Type A + Type B + validation).

---

## צעדים בעת שימוש

1. קרא `context_pack/00_manifest.md`
2. בדוק `SYSTEM_PROMPT.md`
3. הרץ שאלה מ-`questions/test_questions.md`

---

**Version**: 1.0.0 (SAMPLE)
EOF
