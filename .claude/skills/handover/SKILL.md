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
