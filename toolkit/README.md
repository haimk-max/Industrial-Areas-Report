# Toolkit — מערכת כלים משולבת (Three-Tier Skills Library)

> **SSOT (Single Source of Truth)** לכל הנכסים במערכת הכלים: Claude Code Skills, Python Library, Templates.

---

## 📋 רשימה כללית (Overview)

מערכת זו משרתת שלוש שכבות טכנולוגיות בו-זמנית:

| שכבה | תיאור | אחסון | נגישות |
|------|-------|--------|--------|
| **Tier A — Claude Code Skills** | יומניות interactive עבור Claude Code | `toolkit/skills/` | web/desktop/CLI |
| **Tier B — Python Library** | חבילה pip-installable (`signalkit`) | `toolkit/pylib/` | Python projects |
| **Tier C — Templates & Playbooks** | governance docs, process guides, prompts | `toolkit/playbooks/` | Markdown readers |

**מטרה**: SSOT אחד שמשרת את Industrial Areas הנוכחית, Claude API projects, ו-ecosystems עתידיים (Cursor, וכדו').

---

## 🔵 Tier A — Claude Code Skills

### מהו?
**Skill** = יומן interactive עבור Claude Code (web, desktop, IDE extensions). כל skill הוא:
- קובץ `SKILL.md` + קובץ פרומפט דינמי
- נגיש מ-`~/.claude/skills/` (user-level registry, globally accessible)
- פתיחה מהשורה `/<skill-name>` בקובץ או בחלונית הקלט

### סטטוס
| Skill | תיאור קצר | מטרה | סטטוס |
|-------|------------|--------|--------|
| **severity-calculator** | חישוב אינדקס חומרה (bucket) מריכוזים ותקנים | automation of severity ranking per 2021 Report formula | ✓ READY |
| **trend-detective** | זיהוי מגמות + Mann-Kendall + soft triggers | interactive trend interpretation, confidence levels | ✓ READY |
| **agent-rag** | מנוע RAG עם context packs + LLM ingestion | unified context assembly (reports, data, web findings) | ✓ READY (skeleton) |
| **hydro-analyzer** | ניתוח מנהלות והידרוגיאוגרפיה בטקסט חופשי | parsing hydrogeologic reports, extraction of well data | ⏳ PLANNED |

### איך להשתמש
```bash
# התקנה לגלובל
cp -r toolkit/skills/hydro-analyzer ~/.claude/skills/

# שימוש בClaude Code
/<skill-name> [arguments]
```

### קובץ SKILL.md
כל skill יכיל:
```markdown
# Skill: <skill-name>

## מהו?
תיאור קצר בעברית של מה הכלי עושה.

## Input
- פרמטרים
- פורמט קלט

## Output
- פורמט פלט
- דוגמה

## Example
/<skill-name> [example parameters]
```

---

## 🟢 Tier B — Python Library (`signalkit`)

### מהו?
**`signalkit`** = חבילת Python pip-installable המרכזת:
- Trend analysis (Mann-Kendall, SNR gating, soft triggers)
- Severity index calculation
- Forensics engine (decay chains, source signatures)
- Data pipeline (CSV parsing, measurement normalization)

### סטטוס
| קומפוננט | תיאור | סטטוס |
|-----------|-------|--------|
| **trend_analysis.py** | Mann-Kendall + SNR gating | ✓ COMPLETE |
| **severity_calculator.py** | Bucket calculation per 2021 Report | ✓ COMPLETE |
| **forensics_engine.py** | Decay chains, source signatures | ✓ COMPLETE |
| **data_pipeline.py** | CSV parsing, normalization | ✓ COMPLETE |
| **setup.py + pyproject.toml** | pip metadata | ✓ COMPLETE |

### מבנה
```
toolkit/pylib/
├── setup.py                # pip metadata
├── pyproject.toml          # modern Python packaging
└── signalkit/              # source code
    ├── __init__.py
    ├── trend_analysis.py
    ├── severity_calculator.py
    ├── forensics_engine.py
    └── data_pipeline.py
```

### התקנה
```bash
# Development (editable install — recommended for current project)
pip install -e ./toolkit/pylib

# Production
pip install signalkit
# (future: after publication to PyPI)
```

### שימוש בקוד
```python
from signalkit.trend_analysis import calculate_mann_kendall
from signalkit.severity_calculator import calculate_bucket

# Mann-Kendall trend
slope, p_value, z_score = calculate_mann_kendall(measurements)

# Severity bucket
bucket = calculate_bucket(c_max_5y, dws)
```

---

## 🟡 Tier C — Templates & Playbooks

### מהו?
**Playbook** = Markdown template + governance doc שתיעד תהליכים, prompts, checklists.

### סטטוס
| Playbook | תיאור | סטטוס |
|----------|-------|--------|
| **zone_report_process_v5.md** | V5 hybrid pipeline (7-step workflow, context assembly, diagnosis, report) | ✓ COMPLETE |
| **data_pipeline_spec.md** | Structured Data Pack (6 CSVs schema + generation scripts) | ✓ COMPLETE |
| **zone_diagnosis_template.md** | 8-question professional zone assessment | ⏳ PLANNED |
| **monitoring_gaps_checklist.md** | Identification + flagging of monitoring gaps | ⏳ PLANNED |
| **forensics_attribution_guide.md** | HIGH/MEDIUM/LOW confidence levels for source attribution | ⏳ PLANNED |

### ספרייה
```
toolkit/playbooks/
├── zone_report_process_v5.md
├── data_pipeline_spec.md
├── zone_diagnosis_template.md
├── monitoring_gaps_checklist.md
└── forensics_attribution_guide.md
```

### שימוש
```markdown
# בפרויקט חדש
1. קרא toolkit/README.md (זה הקובץ)
2. בחר playbook רלוונטי מ-toolkit/playbooks/
3. עקוב אחר התבנית בעברית
```

---

## 🚀 Workflow — איך להתחיל

### ליצור אזור חדש (new zone)
1. **Assembly**: קרא `toolkit/playbooks/zone_report_process_v5.md`
2. **Data Pack**: בנה עם `toolkit/playbooks/data_pipeline_spec.md`
3. **Diagnosis**: הפעל `/<severity-calculator>` + `/<trend-detective>` (future)
4. **Report**: הרץ V5 prompt עם `/<hydro-analyzer>` (future)

### ליצור skill חדש
1. צור תיקייה בתוך `toolkit/skills/<skill-name>/`
2. כתוב `SKILL.md` עם מטרה, input, output, דוגמה
3. כתוב פרומפט דינמי בעברית
4. עדכן את הטבלה ב-README.md זה

### לתרום ל-pylib
1. Refactor פונקציה מ-`scripts/` ל-`toolkit/pylib/signalkit/`
2. כתוב unit tests
3. Update `setup.py` dependencies
4. Commit + push

---

## 📌 SSOT Rules

1. **README.md זה** הוא **קטלוג ראשי** — רשום כל nכס שנוצר
2. **סטטוס עדכוני**: PLANNED / ⏳ IN PROGRESS / ✓ COMPLETE
3. **ניתוק בין שכבות**: Tier A ≠ Tier B ≠ Tier C — כל אחד עם SSOT משלו
4. **Cross-references**: קישורים לקובצים אמיתיים (`toolkit/playbooks/zone_report_process_v5.md`)

---

## 🔄 Future Lifting Strategy

כאשר יש צרכן שני אמיתי (עקרון 2-המקרים):
- Export `toolkit/` כ-git subtree ל-repo עצמאי: `industrial-areas-toolkit`
- Publish `signalkit` ל-PyPI
- Maintain backwards-compatibility ב-Industrial Areas repo

---

## 📁 File Structure (Current)
```
toolkit/
├── README.md                        ← אתה כאן
├── pylib/
│   ├── setup.py
│   ├── pyproject.toml
│   └── signalkit/
│       ├── __init__.py
│       ├── trend_analysis.py
│       ├── severity_calculator.py
│       ├── forensics_engine.py
│       └── data_pipeline.py
├── skills/
│   ├── hydro-analyzer/
│   │   ├── SKILL.md
│   │   └── prompt.md
│   ├── severity-calculator/
│   │   ├── SKILL.md
│   │   └── prompt.md
│   └── ... (more skills)
└── playbooks/
    ├── zone_report_process_v5.md
    ├── data_pipeline_spec.md
    ├── zone_diagnosis_template.md
    ├── monitoring_gaps_checklist.md
    └── forensics_attribution_guide.md
```

---

## Implementation Status

**Status Summary** (as of 2026-05-27):

| Tier | Component | Status |
|------|-----------|--------|
| **A** | severity-calculator skill | ✓ READY |
| **A** | trend-detective skill | ✓ READY |
| **A** | agent-rag skill | ✓ READY (skeleton) |
| **A** | hydro-analyzer skill | ⏳ PLANNED |
| **B** | pylib (signalkit) — 4 modules | ✓ COMPLETE |
| **B** | setup.py + pip metadata | ✓ COMPLETE |
| **C** | zone_report_process_v5.md | ✓ COMPLETE |
| **C** | data_pipeline_spec.md | ✓ COMPLETE |
| **C** | 3 additional playbooks | ⏳ PLANNED |

### Next Steps

1. **Test pylib**: `pip install -e ./toolkit/pylib` + quick test
2. **Develop agent-rag orchestration**: Opus LLM + PDF extraction
3. **Port remaining playbooks**: zone_diagnosis_template, forensics_guide, monitoring_gaps
4. **Integrate with current projects**: Holon V5, Raanana updates
5. **Documentation**: Installation guide for users + developers

---

**Last Updated**: 2026-05-27  
**Status**: Tier A (3/4 skills) + Tier B (complete) + Tier C (2/5 playbooks) ✓ READY FOR INTEGRATION
