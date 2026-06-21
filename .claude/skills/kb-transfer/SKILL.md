---
name: kb-transfer
description: Distill durable, reusable knowledge from a source (an IAR doc, a raw report, or a pasted ChatGPT/Claude chat) into Water-KB pages — Markdown + frontmatter under knowledge-base/kb_export/, marked status:draft + evidence:D until a human reviews. Distills the load-bearing ~5%; does NOT copy. Invoke when adding knowledge to the KB, filing a chat back, or transferring project knowledge.
---

# /kb-transfer — Distill a source into KB draft pages

Turn a source into a small number of high-signal KB pages. **Distill, don't copy** — keep only the ~5% reusable across future water projects; drop project-specifics, chit-chat, dead-ends.

## Governance (read first)
`knowledge-base/kb_export/KB_GOVERNANCE.md` is the contract. Non-negotiables:
- Minimal frontmatter on every page (title/type/status/evidence/source/last_compiled; validated_by for reviewed/locked).
- Transferred content enters as `status: draft, evidence: D` — the file-back quarantine. A human promotes it.
- KB explains/governs; it never restates an operational parameter that lives in code — link via `implements:`.
- Never commit a raw, unfiltered dump (privacy + bloat). Filter to professional-relevant first.

## Step 1 — Read & classify
Identify durable items and their target layer:
- `01_Domains/` — a contaminant, hydrogeology, a marker, a standard.
- `02_Methods/` — a method/procedure (links to toolkit code).
- `03_Projects/` — a reusable project pattern/precedent.
- `_Lessons/` — a footgun/lesson worth carrying forward.

## Step 2 — Filter (the ~5%)
Keep: methods, domain facts, decisions that constrain future work, lessons, reusable patterns.
Drop: zone-specific data, one-off runs, conversational noise, anything re-derived in 30s.
A rich chat usually yields 1–3 durable pages, not ten.

## Step 3 — Write draft pages → knowledge-base/kb_export/<layer>/<slug>.md
- Minimal frontmatter, `status: draft`, `evidence: D` (A/B only if it traces to a cited raw report).
- Prose: when / why / limitations. For any operational number, link to code — never restate it.
- `source:` records origin (e.g., "ChatGPT chat: <topic>, <date>").

## Step 4 — Index & hand off
- List pages created (path + one line each).
- Flag what needs the human's evidence grade or sign-off to leave draft.
- Do NOT self-promote to reviewed/locked. Do NOT commit raw dumps.

## Calibration
10 pages from one chat = under-filtered. When unsure something is durable: leave it out.
