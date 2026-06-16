# INSTALLATION.md — Toolkit Setup Guide (Hebrew)

> **תיקיה זו מכילה את כל כלי הניתוח, מיומנויות וטמפלטים של פרויקט Industrial Areas.**

---

## 🚀 התקנה מהירה (5 דקות)

### שלב 1: Clone / Extract

```bash
# אם התקבלת tarball:
tar -xzf toolkit-distribution.tar.gz
cd toolkit/

# אם clone מ-git:
cd Industrial-Areas-Report/
```

### שלב 2: התקן את pylib

```bash
# Development (editable install — לעדכון רציף)
pip install -e ./pylib

# Verify:
python -c "from signalkit import calculate_bucket; print('✓ OK')"
```

### שלב 3: העתק Skills ל-Claude Code

```bash
# Create ~/.claude/skills if it doesn't exist
mkdir -p ~/.claude/skills/

# Copy each skill
cp -r skills/severity-calculator ~/.claude/skills/
cp -r skills/trend-detective ~/.claude/skills/
cp -r skills/agent-rag ~/.claude/skills/

# Verify in Claude Code
# You should see /<severity-calculator>, /<trend-detective>, /<agent-rag>
```

### שלב 4: קרא את Playbooks

```bash
# Playbooks are in markdown format — use any editor
cat playbooks/zone_report_process_v5.md
cat playbooks/data_pipeline_spec.md
```

---

## 📦 תוכן התיקייה

```
toolkit/
├── README.md                           — קטלוג ראשי (התחל כאן)
├── INSTALLATION.md                     — קובץ זה
├── DISTRIBUTION.md                     — איך לשתף עם צוות
│
├── pylib/
│   ├── setup.<bdi>py                        ← pip</bdi> metadata
│   ├── pyproject.<bdi>toml                  ← modern</bdi> packaging
│   ├── README.<bdi>md                       ← API</bdi> docs + quick-start
│   └── signalkit/                      — 4 מודולים
│       ├── trend_analysis.py           (Mann-Kendall)
│       ├── severity_calculator.py      (Bucket 0–8)
│       ├── forensics_engine.py         (Decay chains)
│       └── data_pipeline.py            (CSV parsing)
│
├── skills/
│   ├── severity-calculator/SKILL.md    ← /<severity-calculator>
│   ├── trend-detective/SKILL.md        ← /<trend-detective>
│   └── agent-rag/SKILL.md              ← /<agent-rag>
│
└── playbooks/
    ├── zone_report_process_v5.md       ← 7-step workflow
    └── data_pipeline_spec.md           ← 6-CSV schema
```

---

## 🔧 Troubleshooting

### בעיה: `pip install -e ./pylib` נכשל

```bash
# בדוק Python version (≥3.8 required)
python --version

# בדוק שנמצא בתיקיית toolkit/
pwd
ls pylib/setup.py  # Should exist

# נסה עם pip upgrade
pip install --upgrade pip
pip install -e ./pylib
```

### בעיה: `/<severity-calculator>` לא מופיע בClaude Code

```bash
# 1. בדוק שהעתקת את הskill לתיקייה הנכונה
ls ~/.claude/skills/severity-calculator/SKILL.md

# 2. Reload Claude Code (F5 or ⌘R)

# 3. בדוק settings.json
cat ~/.claude/settings.json | grep -i "skill"
```

### בעיה: `ImportError: No module named signalkit`

```bash
# בדוק שהתקנת נכון
pip list | grep signalkit

# אם לא מופיע, התקן מחדש
pip install -e ./pylib

# בדוק עם absolute path
python -c "import sys; sys.path.insert(0, './pylib'); from signalkit import *; print('OK')"
```

---

## 💡 דוגמה שימוש (Python)

```python
# בקובץ Python כלשהו בפרויקט שלך:

from signalkit.trend_analysis import calculate_mann_kendall
from signalkit.severity_calculator import calculate_bucket

# דוגמה 1: Trend detection
measurements = [5, 8, 12, 18, 25, 31, 35]  # ppb over time
trend = calculate_mann_kendall(measurements)
print(trend)
# Output: {'trend': 'ALERT', 'slope': 4.29, 'p_value': 0.014, ...}

# דוגמה 2: Severity bucket
bucket = calculate_bucket(c_max_5y=101, dws=10)  # 101 ppb / 10 ppb standard
print(bucket)  # Output: 3 (Elevated)
```

---

## 📚 קריאה נוספת

1. **README.md** (בתיקיית toolkit/) — catalog ראשי
2. **pylib/README.md** — API reference + configuration
3. **playbooks/zone_report_process_v5.md** — workflow לזונה חדשה
4. **playbooks/data_pipeline_spec.md** — 6-CSV schema

---

## ❓ שאלות נפוצות

**Q: האם אני יכול להשתמש ב-signalkit בפרויקט שלי?**  
A: כן! זה Python library עם pip. רק `pip install -e ./pylib` (development) או חכה ל-PyPI (production).

**Q: האם ה-skills עובדים offline?**  
A: כן. severity-calculator + trend-detective לא צריכים internet. agent-rag צריך web-search לחלק מהטסקים.

**Q: איך מעדכנים את pylib בחלוף הזמן?**  
A: Clone את הrepo  — `git pull origin`  — שינויים אוטומטיים (editable install).

**Q: איפה אני משתמש בplaybooks?**  
A: הם markdown templates לתיעוד תהליך. קרא + עקוב אחרי הצעדים כשמתחילים אזור חדש.

---

## ✅ Checklist לאחרי הקנה

- [ ] `pip install -e ./pylib` הצליח
- [ ] `python -c "from signalkit import *"` עובד
- [ ] 3 folders תחת `~/.claude/skills/`
- [ ] `/<severity-calculator>` מופיע בClaude Code
- [ ] קרא README.md (toolkit/)
- [ ] קרא zone_report_process_v5.md

---

**Status**: ✓ Ready for Team Distribution  
**Version**: 1.0 (May 2026)  
**License**: MIT (pending formal declaration)
