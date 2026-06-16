# TEAM_README.md — קבלת הToolkit (חברי צוות)

> **בשביל חברי צוות**: הוראות פשוטות לקבלת הToolkit והשימוש בו.

---

## 📥 קבלה מהפרוייקט הראשי

### Option 1: Git Clone (המומלץ ביותר)

```bash
# הורדה של הפרוייקט + Toolkit
git clone https://github.com/haimk-max/Industrial-Areas-Report.git
cd Industrial-Areas-Report/

# עדכון (אם כבר יש לך את הפרוייקט)
git pull origin feature/hybrid-v5-implementation
```

### Option 2: Tarball (ללא Git)

```bash
# 1. קבל את הקובץ: toolkit-distribution-YYYY-MM-DD.tar.gz
# 2. חלץ אותו
tar -xzf toolkit-distribution-*.tar.gz

# 3. נוצרה תיקיית toolkit/
cd toolkit/
```

---

## ⚡ התקנה מהירה (2 דקות)

### דרך 1: Automatic (מומלץ)

```bash
# בתיקיית toolkit/:
./setup-toolkit.sh

# זה עושה הכל בקליק אחד ✓
```

### דרך 2: Manual

```bash
# 1. התקן את Python library
pip install -e ./pylib

# 2. העתק את Skills ל-Claude Code
mkdir -p ~/.claude/skills
cp -r skills/* ~/.claude/skills/

# 3. בדוק
python -c "from signalkit import calculate_bucket; print('OK')"
```

---

## ✅ Verification Checklist

```bash
# 1. Python library
python -c "from signalkit import *; print('✓ pylib')"

# 2. Skills (תראה את הקבצים)
ls -la ~/.claude/skills/severity-calculator/

# 3. Claude Code (אם אתה משתמש בClaude Code)
# Open Claude Code  — עברי ל-editor  — סוג "/"
# אתה צריך לראות: /<severity-calculator>, /<trend-detective>, /<agent-rag>
```

---

## 📚 מה זה כל דבר?

| Component | מה זה | איפה משתמשים |
|-----------|--------|-------------|
| **pylib** | Python library (signalkit) | בקוד Python שלך |
| **skills** | 3 tools ל-Claude Code | `/severity-calculator`, `/trend-detective`, `/agent-rag` |
| **playbooks** | templates + תיעוד | markdown files להלמדה |

---

## 🎯 שימוש מיידי

### דוגמה 1: Calculate Severity

```bash
# בClaude Code, סוג:
/<severity-calculator> --c_max 101 --dws 10
```

**Output**: Bucket 3 (Elevated) — 101% of standard

### דוגמה 2: Trend Analysis

```bash
# בClaude Code, סוג:
/<trend-detective> --borehole holon_nt_1 --parameter TCE --interactive

# Paste measurements:
5, 8, 12, 18, 25, 31
```

**Output**: ALERT trend detected

### דוגמה 3: Python Code

```python
from signalkit import calculate_bucket, calculate_mann_kendall

# Calculate bucket
bucket = calculate_bucket(c_max_5y=3456, dws=10)
print(f"Bucket: {bucket}")  # 5 = Very High

# Detect trend
measurements = [5, 8, 12, 18, 25, 31, 35]
trend = calculate_mann_kendall(measurements)
print(f"Trend: {trend['trend']}")  # ALERT
```

---

## 📖 Documentation

**Start here**:

1. **README.md** (in toolkit/) — Overview + component status
2. **INSTALLATION.md** — More detailed setup + troubleshooting
3. **zone_report_process_v5.md** — How to create a zone report (7 steps)
4. **data_pipeline_spec.md** — CSV schema for data

**Advanced**:

- **pylib/README.md** — API reference + configuration
- **DISTRIBUTION.md** — For managers sharing toolkit

---

## ❓ Troubleshooting

**Q: `setup-toolkit.sh` לא עובד**

```bash
# בדוק שאתה בתיקיית toolkit/
pwd
# output should contain "toolkit"

# אם לא, עבור לשם
cd path/to/toolkit/

# נסה שוב
./setup-toolkit.sh
```

**Q: `/<severity-calculator>` לא מופיע**

1. ודא שהעתקת ל-`~/.claude/skills/`
   ```bash
   ls ~/.claude/skills/severity-calculator/SKILL.md
   ```

2. Reload Claude Code (F5 or ⌘R)

3. אם עדיין לא עובד, תקן ידנית:
   ```bash
   mkdir -p ~/.claude/skills/severity-calculator
   cp -r toolkit/skills/severity-calculator/* ~/.claude/skills/severity-calculator/
   ```

**Q: `from signalkit import *` נכשל**

```bash
# בדוק installation
pip list | grep signalkit
# output: signalkit 0.1.0

# אם לא מופיע, התקן
pip install -e ./toolkit/pylib
```

---

## 🚀 Next Steps

1. **Complete Installation** ✓ (you're here)
2. **Read zone_report_process_v5.md** (understand workflow)
3. **Try a skill** (test in Claude Code)
4. **Use in Python code** (import signalkit)
5. **Create your first report** (zone analysis)

---

## 💬 Questions?

- **Installation issues** → See INSTALLATION.md troubleshooting
- **Usage questions** → Read playbooks/zone_report_process_v5.md
- **Bug reports** → Contact project lead
- **Feature requests** → Open GitHub issue

---

**Version**: 1.0  
**Last Updated**: 2026-05-27  
**Status**: ✓ Ready to use
