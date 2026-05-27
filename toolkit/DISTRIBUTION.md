# DISTRIBUTION.md — איך לשתף Toolkit עם הצוות

> **למנהל פרויקט**: רשמות ודרכים להפיץ toolkit לחברי צוות.

---

## 🎯 3 דרכים להפצה

### דרך 1: GitHub Clone (המומלץ ביותר)

**אם הצוות כבר בGit:**

```bash
# בקבצי הצוות שלהם
cd Industrial-Areas-Report/
git pull origin feature/hybrid-v5-implementation

# או
git clone https://github.com/haimk-max/Industrial-Areas-Report.git
cd Industrial-Areas-Report/

# עכשיו יש להם הכל בתיקיית toolkit/
```

**יתרונות**:
- ✓ תמיד עדכני (git pull)
- ✓ אפשר להעלות שינויים חזרה (git push)
- ✓ בדוק שינויים (git diff)

---

### דרך 2: Tarball (למי שלא משתמש ב-Git)

**1. בשרת/מחשב שלך:**

```bash
cd /path/to/Industrial-Areas-Report/

# יצור tarball של toolkit/
tar -czf toolkit-distribution-2026-05-27.tar.gz toolkit/

# בדוק גודל (צריך להיות < 5MB)
ls -lh toolkit-distribution-2026-05-27.tar.gz
```

**2. שלח לצוות:**

```bash
# Upload ל-email / Slack / Google Drive / וכו'
toolkit-distribution-2026-05-27.tar.gz
```

**3. הצוות שלך חילץ:**

```bash
# בתיקיית המשימה שלהם
mkdir industrial-areas-toolkit
cd industrial-areas-toolkit/
tar -xzf toolkit-distribution-2026-05-27.tar.gz
cd toolkit/

# עכשיו אונם עוקבים INSTALLATION.md
```

**יתרונות**:
- ✓ אין צורך בGit
- ✓ קובץ יחיד להורדה
- ✓ אפשר לשלוח בdatastick / email

---

### דרך 3: Pip Package (עתידית, PostPublish)

**כשאתה מפרסם לPyPI:**

```bash
# צוות שלך עשה פעם אחת:
pip install signalkit

# עכשיו עבור כל דוח/פרויקט:
from signalkit import calculate_bucket, calculate_mann_kendall
```

**יתרונות**:
- ✓ אין צורך ב-clone/tarball
- ✓ עדכונים דרך `pip upgrade`
- ✓ Distributed globally

**מתי**: אחרי Holon validation, כשהpylib יציב.

---

## 📋 Checklist — לפני שתשלח

**לבדוק:**

- [ ] `git status` — כל הקבצים committed
- [ ] `pip install -e ./toolkit/pylib` — עובד בלוקלי
- [ ] `python -c "from signalkit import *"` — importים עובדים
- [ ] `ls ~/.claude/skills/severity-calculator/` — files exist
- [ ] `toolkit/README.md` — up-to-date + readable
- [ ] `toolkit/INSTALLATION.md` — instructions clear

**Optional:**

- [ ] Run unit tests (TBD) — `pytest toolkit/pylib/tests/`
- [ ] בדוק tarball extract — `tar -xzf toolkit-*.tar.gz`
- [ ] Review security (TBD) — no credentials in code

---

## 📧 Email Template (עברית)

```
נושא: [Industrial Areas] Toolkit System — התקנה ושימוש

שלום צוות,

הכנו toolkit משלושה חלקים לניתוח איכות מי-תהום:

✓ Tier A: Claude Code Skills (3 tools interactive)
✓ Tier B: Python Library — signalkit (pip-installable)
✓ Tier C: Playbooks & Templates (zone reports)

QUICK START:
1. git clone / extract toolkit-distribution.tar.gz
2. pip install -e ./toolkit/pylib
3. cp -r toolkit/skills/* ~/.claude/skills/
4. Read toolkit/README.md + toolkit/INSTALLATION.md

הכל בעברית (documentation) + English (code).

שאלות? ראה INSTALLATION.md troubleshooting section.

———
Repository: https://github.com/haimk-max/Industrial-Areas-Report
Toolkit Status: 3 skills ready + pylib complete + 2 playbooks
Last Updated: 2026-05-27
```

---

## 🔄 After Distribution — Support

**בשבוע הראשון, הצוואה**:

1. **ודא התקנה**:
   - שלח email: "Did toolkit install OK? Any errors?"
   - בקש verification: `pip list | grep signalkit`

2. **Gather Feedback**:
   - "Was INSTALLATION.md clear?"
   - "Did skills show up in Claude Code?"
   - "Any missing dependencies?"

3. **Update PROCESS.md**:
   - הוסף feedback ל-LESSONS.md
   - עדכן INSTALLATION.md אם יש ברורים

---

## 🎁 Bonus: Automated Setup Script (Optional)

אם צוותך משתמש ב-Bash:

```bash
#!/bin/bash
# setup-toolkit.sh

set -e

echo "🔧 Industrial Areas Toolkit Setup"

# 1. Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Install it first."
    exit 1
fi

# 2. Install pylib
echo "📦 Installing signalkit..."
pip install -e ./toolkit/pylib

# 3. Create ~/.claude/skills if needed
mkdir -p ~/.claude/skills

# 4. Copy skills
echo "🎯 Installing skills..."
cp -r toolkit/skills/* ~/.claude/skills/

# 5. Verify
echo "✅ Verifying installation..."
python -c "from signalkit import calculate_bucket; print('✓ pylib OK')"
[ -f ~/.claude/skills/severity-calculator/SKILL.md ] && echo "✓ Skills OK"

echo "🎉 Setup complete! Read toolkit/README.md to get started."
```

**שימוש**:

```bash
chmod +x setup-toolkit.sh
./setup-toolkit.sh
```

---

## 📞 Support Contacts

| בעיה | מי לפנות | ערוץ |
|------|---------|------|
| Installation errors | DevOps/Tech Lead | Slack #tech-support |
| Usage questions | הידרולוג/Analyst | Email or meeting |
| Feature requests | PM/Lead | GitHub issues |
| Bug reports | Dev | GitHub issues |

---

## ✅ Success Criteria

הפצה הצליחה אם:

- [ ] ≥80% של צוות התקינו בהצלחה
- [ ] 0 "file not found" complaints
- [ ] ≥1 צוות member השתמש בskill בדוח בפועל
- [ ] No Python/import errors in team repos

---

**Version**: 1.0  
**Last Updated**: 2026-05-27  
**Next Review**: After Holon V5 validation
