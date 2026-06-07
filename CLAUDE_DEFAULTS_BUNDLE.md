# CLAUDE_DEFAULTS_BUNDLE — חבילת הגדרות יוזר לריפואים חדשים

> **מטרה**: ב-Claude Code on the web אין `~/.claude/` שורד. כדי שכל ריפו שאני עובד בו יתחיל עם אותן הגדרות, אילוצים והרגלים — מסמך זה מאגד את כל מה ש**היה** אמור לגור ב-`~/.claude/CLAUDE.md`, ומציע שתי דרכי התקנה.

---

## 1. מה החבילה כוללת

החבילה יוצרת בריפו יעד שלושה קבצים:

| קובץ | תפקיד |
|------|--------|
| הוספה ל-`CLAUDE.md` (שורש הריפו) | אילוצי סביבה + קונבנציות + העדפות יציבות. אם אין `CLAUDE.md`, יוצרים אותו. |
| `HANDOVER.md` (שורש הריפו) | זיכרון בין-סשן (תחליף ל-`~/.claude/CLAUDE.md` החולף). |
| `.claude/skills/handover/SKILL.md` | סקיל `/handover` שמתחזק את `HANDOVER.md` בסוף כל סשן. |

---

## 2. תוכן הקבצים

### 2.1. קטע לתחילת `CLAUDE.md` בריפו היעד

```markdown
## אילוצי סביבה (Environment — חשוב לכל סשן)

- המשתמש עובד **אך ורק** דרך Claude Code on the web (GitHub integration) — **אין גישה לטרמינל**.
- `~/.claude/` לא שורד בין סשנים (container חולף). כל זיכרון בין-סשן חייב להיות committed לריפו.
- **זיכרון בין-סשן**: `HANDOVER.md` בשורש הריפו — קרא אותו בתחילת כל סשן.
- **סקיל `/handover`**: מותקן ב-`.claude/skills/handover/SKILL.md` — הפעל בסוף כל סשן.

## קונבנציות שפה

- **קבצי Markdown** (CLAUDE.md, PROCESS.md, planning, todos): **עברית**.
- **קוד** (Python, JS, shell, שמות משתנים, comments, docstrings): **אנגלית**.
- **Commit messages**: אנגלית (convention של Git).
- **כותרות סעיפים בדוחות**: עברית בלבד.

## העדפות יציבות

- סיים כל סשן עבודה ב-`/handover` (או בבקשה חופשית "תעשה handover") כדי לייצר הערת מסירה מסוננת.
- ברירת מחדל: **שאל לפני commit או push**, גם אם הסשן כבר רץ זמן מה.
- שינויים הרסניים (`reset --hard`, `force push`, מחיקת ענפים) — דורשים אישור מפורש, גם בריפו זה.

## פרויקטים פעילים

- `Industrial-Areas-Report` — ניטור איכות מי תהום ב-18 אזה"ת לאורך אקוויפר החוף. SSOT מקומי בריפו: `CLAUDE.md`, `PROCESS.md`, `LESSONS.md`, `ZONE_REPORT_PROCESS_GUIDE.md`. V5 hybrid pipeline = המתודולוגיה המחייבת לאזורים חדשים.

## footguns בין-פרויקטיים

<!-- הוסף כאן רק דפוסים שגרמו לבעיות יותר מפעם אחת -->
—
```

### 2.2. תוכן `HANDOVER.md` (שורש הריפו)

```markdown
# HANDOVER.md — זיכרון בין-סשן

קובץ זה מתוחזק על-ידי הסקיל `/handover`. הוא מתעדכן **רק** כאשר סשן מייצר משהו שהסשן הבא צריך לדעת — אילוץ, footgun חוזר, החלטה שמגבילה עבודה עתידית.

**אסור לרשום כאן**: פעולות שגרתיות, התקדמות יומית, או מה שנלכד כבר בהודעות commit.

---

## אילוצי סביבה (Environment Constraints)

- המשתמש עובד **אך ורק** דרך Claude Code on the web (GitHub integration) — **אין גישה לטרמינל**.
- `~/.claude/` לא שורד בין סשנים (container חולף). כל דבר שצריך להישמר חייב להיות committed לריפו.
- הסקיל `/handover` מותקן ב-`.claude/skills/handover/SKILL.md` (בריפו, לא גלובלי) — זה מה שגורם לו לשרוד.

---

## החלטות מגבילות (Load-bearing Decisions)

<!-- הוסף כאן החלטות שמגבילות עבודה עתידית -->
—

## footguns חוזרים

<!-- הוסף כאן דפוסים שגרמו לבעיות יותר מפעם אחת -->
—

## עבודה בתהליך (In flight)

<!-- עדכן כאן רק כשמשהו נחתך באמצע ויש לחזור אליו -->
—
```

### 2.3. תוכן `.claude/skills/handover/SKILL.md`

````markdown
---
name: handover
description: End-of-session handover. Surveys git log + uncommitted changes, filters aggressively to keep only the 5% that's load-bearing for the next session, updates HANDOVER.md in the repo with persistent notes worth carrying forward, asks before committing anything, and prints a tight structured note (Shipped / In flight / Watch-outs / Open questions) readable in under 30 seconds. Invoke when the user types /handover or asks to wrap up / hand off the session.
---

# /handover — End-of-session handover

The user is wrapping up. Produce a short, high-signal note that future-them (or a cold-reading Claude) can absorb in under 30 seconds. **Filter aggressively.** Most of a session is forgettable execution — keep only what's load-bearing.

## Environment constraint

This repo is used exclusively via **Claude Code on the web** (GitHub integration). There is no terminal access for the user. `~/.claude/` does NOT persist between sessions — everything durable must be committed into the repo.

## Step 1 — Survey what actually happened

Run these in parallel:

- `git log --since="12 hours ago" --oneline` (commits this session; widen to 24h if empty)
- `git status --short` (uncommitted changes)
- `git diff --stat && git diff --stat --cached` (scope of uncommitted work)

Do **not** dump raw output to the user. Synthesize it.

## Step 2 — Identify load-bearing items

Keep: decisions that constrain future work; discovered constraints/gotchas/broken assumptions; half-finished work with enough context to resume cold; open questions only the user can answer.

Drop: routine execution; anything fully captured by a commit message; anything the next session would rediscover in 30 seconds.

When in doubt: **leave it out.**

## Step 3 — Update HANDOVER.md (selectively)

`HANDOVER.md` in the repo root is the persistent cross-session memory file. Update it **only** if this session produced something durable — a stable constraint, a recurring footgun, a convention the next session needs.

- Do not log daily activity or routine progress.
- Use `Edit` to surgically update an existing entry; add a new entry only if genuinely new and durable.
- If `PROCESS.md` or `LESSONS.md` is a better home for an item, **ask** rather than touching it silently.
- If nothing meets the bar, don't touch the file. Say so.
- After updating, propose a commit.

## Step 4 — Uncommitted changes

If `git status` shows work worth saving: summarize it (one sentence), **ask** whether to commit (propose a message), never commit silently or use `git add -A` without confirmation. If declined, put it under "In flight."

## Step 5 — Print the handover note

Output exactly this structure as the final message. Empty section = `—`. Target ~15 lines.

```
## Handover — <YYYY-MM-DD HH:MM>

### Shipped
- <short-sha> <commit subject>   (or: deploy, merged PR)

### In flight
- <what's half-done> — <enough context to resume cold>

### Watch-outs
- <gotcha, surprising state, broken assumption, footgun>

### Open questions
- <question only the user can answer>

Memory: <"updated HANDOVER.md: <one line>" | "no changes — nothing durable">
Uncommitted: <"none" | "<N> files — <decision taken>">
```

## Calibration

- 90% execution with no durable decisions → mostly dashes. Correct, not a failure.
- More than ~15 lines = not filtered enough. Cut.
- Never narrate the survey. Just produce the note.
````

---

## 3. דרך התקנה א' — ידני (3 שלבים)

1. **`CLAUDE.md`**: אם לא קיים, צור אותו עם התוכן מ-§2.1. אם קיים — הדבק את §2.1 בראשו (אחרי כותרת ה-`# CLAUDE.md` הראשונה).
2. **`HANDOVER.md`**: צור קובץ חדש בשורש הריפו עם התוכן מ-§2.2.
3. **`.claude/skills/handover/SKILL.md`**: צור את התיקיות אם צריך, ושים את התוכן מ-§2.3.

**Commit + push לענף ברירת המחדל** (לרוב `main`) — אחרת `/handover` לא יופיע בתפריט `/` בסשני web חדשים.

---

## 4. דרך התקנה ב' — Bootstrap prompt (העתק-הדבק ל-Claude בריפו חדש)

הדבק את הבלוק הבא כהודעה ראשונה לסשן Claude חדש בריפו היעד. Claude יבצע את כל ההתקנה בפעולה אחת.

```
התקן את חבילת ההגדרות הגלובליות שלי בריפו הזה. בצע את הצעדים הבאים, וודא commit + push לענף הנוכחי בסוף:

1. אם CLAUDE.md לא קיים בשורש — צור אותו עם כותרת "# CLAUDE.md" בלבד. הדבק את הקטעים הבאים מיד אחרי הכותרת:

## אילוצי סביבה (Environment — חשוב לכל סשן)

- המשתמש עובד **אך ורק** דרך Claude Code on the web (GitHub integration) — **אין גישה לטרמינל**.
- `~/.claude/` לא שורד בין סשנים (container חולף). כל זיכרון בין-סשן חייב להיות committed לריפו.
- **זיכרון בין-סשן**: `HANDOVER.md` בשורש הריפו — קרא אותו בתחילת כל סשן.
- **סקיל `/handover`**: מותקן ב-`.claude/skills/handover/SKILL.md` — הפעל בסוף כל סשן.

## קונבנציות שפה

- **קבצי Markdown** (CLAUDE.md, PROCESS.md, planning, todos): **עברית**.
- **קוד** (Python, JS, shell, שמות משתנים, comments, docstrings): **אנגלית**.
- **Commit messages**: אנגלית.
- **כותרות סעיפים בדוחות**: עברית בלבד.

## העדפות יציבות

- סיים כל סשן עבודה ב-`/handover` (או "תעשה handover") כדי לייצר הערת מסירה מסוננת.
- ברירת מחדל: **שאל לפני commit או push**.
- שינויים הרסניים (`reset --hard`, `force push`, מחיקת ענפים) — דורשים אישור מפורש.

2. צור את HANDOVER.md בשורש הריפו עם השלד הבא:

# HANDOVER.md — זיכרון בין-סשן

קובץ זה מתוחזק על-ידי הסקיל `/handover`. הוא מתעדכן **רק** כאשר סשן מייצר משהו שהסשן הבא צריך לדעת.

## אילוצי סביבה
- web-only, אין טרמינל, ~/.claude לא שורד.

## החלטות מגבילות
—

## footguns חוזרים
—

## עבודה בתהליך
—

3. צור את .claude/skills/handover/SKILL.md עם התוכן המלא מ-CLAUDE_DEFAULTS_BUNDLE.md §2.3 של ריפו Industrial-Areas-Report (העתק מילולית את הבלוק מהקובץ הזה: https://github.com/haimk-max/Industrial-Areas-Report/blob/main/CLAUDE_DEFAULTS_BUNDLE.md).

4. commit עם הודעה: "Install global defaults bundle (CLAUDE.md + HANDOVER.md + handover skill)"
5. push לענף הנוכחי.
6. סיים בהודעה למשתמש: "החבילה הותקנה. כדי ש-/handover יופיע בתפריט / בסשני web — צריך למזג ל-default branch."
```

> **הערה ל-bootstrap**: השלב השלישי מפנה לקובץ זה עצמו ב-GitHub כדי שלא צריך להעתיק את כל הסקיל לתוך ה-prompt. אם הריפו הזה פרטי או נמחק, החלף את הקישור בתוכן המלא מ-§2.3.

---

## 5. אחרי ההתקנה

- בסשן **חדש** (לא resumed) על הענף הנכון (כדי שהסקיל יופיע ב-`/`):
  - הקלד `/handover` — אמור להופיע בתפריט.
  - לחלופין: כתוב במילים "תעשה handover" — עובד מיד בכל סשן.
- אם רוצים שהסקיל יעבוד גם דרך הקלדה לפני מיזוג ל-main: עבוד עליו ישירות על `main` (אחרת ה-default branch לא מכיל אותו וה-`/` לא ימצא).

---

## 6. גרסה ומקור

- **גרסה**: 1.0 (2026-06-07)
- **מקור אמת**: `Industrial-Areas-Report/CLAUDE_DEFAULTS_BUNDLE.md`
- **שינויים**: כשמשתנה משהו ב-`~/.claude/CLAUDE.md` הלוגי (קונבנציות, אילוצים, פרויקטים) — לעדכן כאן, ולהריץ מחדש את ה-bootstrap בריפואים אחרים אם צריך.
