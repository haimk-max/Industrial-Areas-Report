# סקירת מתודולוגיה: דפוס ה-LLM-Wiki של Karpathy והקמת ה-KB שלך

> **תאריך**: 2026-06-21
> **היקף**: סיכום סקירה (מול מקורות אמינים) + הערות קהילה + בחינת בסיס-הידע (KB) הרגולטורי הקונקרטי.
> **הקשר**: מסמך שיקול-דעת לקראת הקמת KB לתחום איכות-המים, בהשראת דפוס ה-LLM-Wiki של Andrej Karpathy, מותאם לעבודה רגולטורית. נשמר כזיכרון בין-סשן (container חולף — חייב committed).
> **תיקון דיוק** (לעומת טיוטה קודמת): בעבר נכתב ש-Karpathy "אינו מספק guardrails" — לא מדויק. אימות חוזר של ה-gist מצא שני guardrails מבניים (`raw/` + "Lint"). מתוקן בסעיף 1.

---

## 1. מה Karpathy באמת הציע

דפוס ה-**LLM-Wiki** (gist‏ `llm-wiki.md`, אפריל 2026): ה-LLM מקמפל ומתחזק wiki ב-Markdown מתוך מקורות-גלם; האדם מספק מקורות ושואל שאלות; תשובות טובות "מתויקות בחזרה" (file-back). בלי RAG, בלי embeddings — *"the most compact, LLM-readable, and human-auditable format."*

**שני guardrails מבניים שהוא כן כלל**:
- שכבת **`raw/`** — מקורות *immutable*: *"the LLM reads from them but never modifies them. This is your source of truth."*
- שלב **"Lint"** — *"Periodically, ask the LLM to health-check the wiki. Look for: contradictions between pages, stale claims that newer sources have superseded, orphan pages..."*

**מה שהשאיר במכוון בחוץ** (*"intentionally abstract... describes the idea, not a specific implementation"*): דירוג ראיות, חתימת-מומחה, מטא-provenance, ממשל רגולטורי. וה-lint הוא "בקש מה-LLM לבדוק את עצמו" — בלי שער אנושי.

**קליטה** (לפי סיקור הקהילה): ויראלי — ~16M צפיות בציוץ, 5,000+ stars ו-4,400+ forks ל-gist תוך שבועיים, עשרות מימושים עצמאיים, סיקור VentureBeat.

---

## 2. הערות הקהילה (בעד ונגד)

| בעד | נגד (ביקורות אמיתיות) |
|-----|------------------------|
| **מבנה > דמיון-וקטורי** — התעשייה הגזימה ב-Vector DBs לבעיות שהן ביסודן מבניות | **① "מיפוי חשיבה החוצה"** — ה-bookkeeping (תיוק, קישור, סיכום) הוא *המקום שבו נוצרת הבנה*; מאצילים אותו → "תחושת ידע בלי למידה" |
| **ידע מצטבר** — "כל מקור חדש מייקר את כל הקודמים"; "ידע כמו קוד מהודר" | **② "RAG עם צעדים נוספים"** |
| מאמת את עקרון ה-file-back ואת ה-Markdown-auditability | **③ הזיה שמתפשטת** *(הקריטית)* — ה-LLM דוחס מקורות → טעות נצרבת כ"עובדה"; ב-wiki מקושר אי-הבנה קטנה **מתפשטת על פני דפים**. חמור מ-RAG: שם טעות = תשובה אחת; כאן הטעות מתפשטת בכל בסיס-הידע |

**מענה הקהילה לסיכון ③**: שלב ה-lint/audit, מעקב כל טענה אל `raw/`, ו-spot-check מול המקורות.

---

## 3. בחינת ה-KB הקונקרטי שלך (רגולטורי, איכות-מים)

הביקורות נושכות **חזק יותר** אצלך: אין אימות חינמי (Willison: *"no quick, free way to verify"*), טעויות יקרות, צרכנים חיצוניים (רשות, ציבור), והזיה-מתפשטת = **סיכון ציות**. אבל — וזה העיקר — **המתודולוגיה שלך כבר עונה לכל ביקורת, מבנית**:

| ביקורת קהילה | המענה המבני שלך | אימות חיצוני |
|---------------|------------------|---------------|
| ③ הזיה מתפשטת | evidence **A–E** + הסגר file-back (`evidence:D` עד אימות) + גבול KB↔toolkit (אין שכפול פרמטר) | W3C PROV · model collapse (Nature 2024) · EU AI Act §50 |
| ① מיפוי חשיבה החוצה | האדם נשאר אחראי מקורות+שאלות (כמו Karpathy) **+ שער חתימה** (`validated_by` ל-`reviewed`/`locked`) — שיפוט המומחה מקודד, לא מואצל | Evergreen notes · certification שמי |
| ② RAG+ | לידע חוצה-18-אזורים + PFAS/CBZ/GIS — **מבנה הוא העיקר**; ה-KB מוגדר "מעל הפרויקטים" | Second Brain / Digital Gardens |

**מיפוי קונקרטי — חלקי Karpathy ↔ ה-KB שלך:**
- `raw/` (immutable) → מקורות הגלם שלך = **בסיס evidence A**. **ערוצי-מקור מרובים** נכנסים לכאן: דוחות רשמיים (TAHAL 2008, דוח 2021, Excel), פרויקט IAR, **צ'אטים מ-ChatGPT/Claude**, מצגות, מסמכי מדיניות. ה-KB יושב *מעל* כל הערוצים; אף אחד אינו "source of truth" בלעדי. תוכן שיחתי (ChatGPT/Claude) נכנס כ-`evidence:D, status:draft` עד אימות מומחה.
- `wiki` → `01_Domains / 02_Methods / 03_Projects / _Lessons`.
- `Lint` → **הקשחה**: frontmatter-lint מכונה (כל `locked`→`validated_by`; כל `implements:`→פונקציה קיימת) — כמו שערי ה-QA של IAR (`qa_pipeline`), במקום "LLM בודק את עצמו".
- `file-back` → file-back **+ שער הסגר** (`evidence:D` עד אימות).

---

## 4. שורה תחתונה

הרעיון **בשל, מקורי, וקהילתית-מאומת** — והקהילה עצמה זיהתה בדיוק את הסיכון (הזיה מתפשטת) שהממשל שלך פותר. ה-KB שלך אינו סטייה מ-Karpathy אלא **"Karpathy + ההקשחה שהמקרה הרגולטורי מחייב"**: לוקח את ה-`raw/` וה-`lint` שלו, והופך את ה-lint משער-עצמי-של-LLM לשער **מכונה + אדם**, מדורג-ראיות.

**עמדה מומלצת**: התחל פשוט (Markdown + `raw/` + lint, בדיוק כמו Karpathy), הוסף *רק* את הממשל שמצדיק את עצמו — סטטוס בגרות, evidence A–E, הסגר file-back, וגבול KB↔toolkit.

---

## מקורות

**ראשוני (Karpathy)**: [llm-wiki gist](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f) · [context engineering (X)](https://x.com/karpathy/status/1937902205765607626) · [Software Is Changing — YC](https://www.ycombinator.com/library/MW-andrej-karpathy-software-is-changing-again)

**הערות קהילה**: [VentureBeat](https://venturebeat.com/data/karpathy-shares-llm-knowledge-base-architecture-that-bypasses-rag-with-an) · ["An LLM Wiki Won't Compound Your Knowledge" (bitsofchris)](https://bitsofchris.com/p/an-llm-wiki-wont-compound-your-knowledge) · [HN — Obsidian workflow](https://news.ycombinator.com/item?id=48351115) · [Show HN — Markdown+Git](https://news.ycombinator.com/item?id=47899844) · [סקירת משתמש Zettelkasten](https://yu-wenhao.com/en/blog/karpathy-zettelkasten-comparison/)

**מסגרות וממשל**: [Anthropic — context engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents) · [Matuschak — Evergreen notes](https://notes.andymatuschak.org/Evergreen_notes) · [Diátaxis](https://diataxis.fr/) · [W3C PROV](https://www.w3.org/TR/prov-overview/) · [model collapse (Nature 2024)](https://arxiv.org/abs/2410.12954) · [EU AI Act §50](https://artificialintelligenceact.eu/article/50/)
