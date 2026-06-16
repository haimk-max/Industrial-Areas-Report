# Industrial Areas Report · Build Instructions for Claude

You are building two HTML reports per industrial zone, from a structured YAML brief, following a frozen design system.

This file is your operating manual. Read it in full before any build.

---

## 1 · What you produce

For each zone (e.g. `holon`, `ashdod`):

```
output/<zone-id>/
  ├── INTERNAL.html      # internal management brief — names + decision matrix
  ├── PUBLIC.html        # public transparency report — generic + narrative
  └── index.html         # optional landing card linking both
```

Both files are **self-contained** — no build step, no bundler, open in any modern browser.

---

## 2 · What you read

```
briefs/<zone-id>.<bdi>yaml              ← per-zone</bdi> data (the only thing that varies)
design-system/                     ← FROZEN. do not modify.
  ├── tokens.<bdi>css                   ← CSS</bdi> variables — copy into <style> of every output
  ├── architecture.<bdi>md              ← the</bdi> "twins, not identical" philosophy
  ├── typography.<bdi>md                ← font</bdi> system + RTL rules
  ├── color.<bdi>md                     ← semantic</bdi> color rules
  ├── voice.<bdi>md                     ← copy</bdi>/tone rules for both audiences
  └── reference/
      ├── HOLON_INTERNAL.<bdi>html      ← gold</bdi> standard — match its quality
      ├── HOLON_PUBLIC.<bdi>html        ← gold</bdi> standard — match its quality
      └── index.html
schemas/zone-brief.schema.<bdi>json     ← validate</bdi> brief before building
```

---

## 3 · Pre-flight (always do this first)

1. **Load brief.** Parse `briefs/<zone-id>.yaml`.
2. **Validate.** Check against `schemas/zone-brief.schema.json`. **Halt on failure** with a clear error pointing to the missing/invalid field.
3. **Read the reference files in full.** They are your structural template. You are NOT inventing layout — you are replacing Holon's data with the new zone's data inside an existing structure.
4. **Read architecture.md + voice.md.** Internalize the twin-document philosophy and the two voices.

---

## 4 · Build process

For each output file:

### Step 1 — Clone the reference
Open `design-system/reference/HOLON_INTERNAL.html` (or `PUBLIC.html`) and use it as the structural template. **Preserve every CSS rule, every section, every component pattern, every interaction.** You are replacing content, not redesigning.

### Step 2 — Replace data, top to bottom
Walk the file from `<head>` to `</body>`, swapping Holon-specific strings with the new zone's data per the field-mapping table below.

### Step 3 — Generate narrative where needed
For prose fields (`bottom_line`, `context_intro`, finding bodies, panel text), the brief may provide explicit text OR leave them as structured data for you to write. If the brief provides <bdi>text → use</bdi> as-is. If only data → write per voice rules.

### Step 4 — Verify before declaring done
Check the quality bar in §8 below. If any item fails, fix before output.

---

## 5 · <bdi>Field → Section</bdi> Mapping

### INTERNAL.html

| YAML path                | HTML location                          |
| ---                      | ---                                    |
| `zone.classification`    | top-bar red badge                      |
| `zone.name_he`           | masthead H1                            |
| `zone.period`            | masthead eyebrow + chip                |
| `zone.edition`           | top-bar version, footer doc-id        |
| `zone.active_boreholes`  | KPI card + chip ("~N" placeholder OK) |
| `bottom_line`            | §00 (3 paragraphs in border-right block) |
| `kpis[]`                 | §01 (4-card grid; `urgent` class for red top-bar) |
| `family_ledger[]`        | §02 (one row per contaminant family)  |
| `framing_warning`        | §02 amber callout                      |
| `findings[]`             | §03 (7 cards: F·01 → F·07)             |
| `findings[].urgency`     | tag class: `crit` / `high` / `good`    |
| `findings[].metadata`    | aside meta-rows                        |
| `findings[].certainty`   | cert badge HIGH/MED/LOW                |
| `boreholes[]` matrix     | §04 severity matrix rows               |
| `decisions[]`            | §05 (grouped by category)              |
| `boreholes[]` + `sources[]` | §06 Leaflet markers                 |
| `plume_paths[]`          | §06 polylines (optional)               |
| `zone.doc_id_internal`   | colophon                                |

### PUBLIC.html

| YAML path                | HTML location                          |
| ---                      | ---                                    |
| `zone.name_he`           | hero H1                                |
| `zone.period`            | hero eyebrow                            |
| `zone.active_boreholes`  | hero-meta + stat card                  |
| `context_intro[]`        | §01 prose paragraphs                    |
| `framing_warning`        | §01 amber callout                      |
| `stats_public[]`         | §01 stats (typically 3)                |
| `timeline[]`             | §02 events (use `position_pct` + `layer`) |
| `findings[]`             | §03 (use public versions of fields)    |
| `findings[].public_*`    | title/body/explanation/response        |
| `boreholes[].public.*`   | §04 map (codes only, no real names!)   |
| `means_summary[]`        | §05 (typically 4 cards)                |
| `methodology[]`          | §06 (typically 3 cells)                |
| `contact`                | footer                                  |
| `zone.doc_id_public`     | footer                                  |

---

## 6 · The two voices (read voice.md for detail)

### Internal voice
- Technical, action-oriented, direct.
- Real names: `מק חולון 14`, `תדיראן קשר`.
- Quantify: `7.59 µg/L`, `101% מהתקן`, `04/2025`.
- Mark certainty: `HIGH` / `MEDIUM` / `LOW`.
- "What to do + who" framing.

### Public voice
- Explanatory, transparent, never condescending.
- Generic categories ONLY: `מפעל ציפוי מתכות (סגור)`, `מתקן ביטחוני`. **Never** facility names.
- Borehole codes ONLY: `B-01`, `B-02`. **Never** real well names.
- Plain language: "פי X מהתקן" not z-scores.
- Always pair "מה זה אומר" with "מה אנחנו עושים".
- Acknowledge gaps openly: "מתפרסם בשקיפות מלאה".

---

## 7 · Visual rules (NEVER override)

### Semantic colors — exclusive use
- `--red` (#c0392b): standard exceedance · monitoring gap · urgency
- `--teal` (#0f6b7a): anchor color · water identity · actions · links
- `--green` (#1f7a4d): remediation success
- `--amber` (#b87333): caveats · framing warnings
- All others: neutral grayscale only

### Typography
- UI/body: IBM Plex Sans Hebrew (300, 400, 500, 600, 700)
- Numbers/codes: IBM Plex Mono (400, 500, 600)
- Long prose (public only): IBM Plex Serif (300, 400, 500)
- No other fonts ever.

### RTL discipline
- All Latin tokens (TCE, PFAS, MK-14, 2026, %, µg/L) inside Hebrew text must be wrapped in `<bdi>`.
- Maps and timelines use internal `direction:ltr` while page is `dir="rtl"`.
- No emoji in body text. ✓ allowed in legends/headers only.

### Map rules (Leaflet + CartoDB Positron)
**Internal map:**
- All boreholes (real names) as colored circles
- All sources (real names) as diamond markers (filled = HIGH cert, outlined = MED)
- Plume polylines with informative tooltip
- Filter bar: all / boreholes / sources / exceedances / silent
- Popup shows real name + full metadata + certainty

**Public map:**
- Boreholes ONLY (anonymized codes B-01...)
- **NEVER** show sources. Not in any form.
- Plume polylines OK with generic tooltip
- Popup shows code + tier label + 2–4 generic rows

---

## 8 · Quality bar (verify before output)

Before declaring complete, run through this checklist:

- [ ] Both files render without console errors
- [ ] Brief YAML validates against schema
- [ ] All findings have both `_internal` and `_public` variants
- [ ] Severity matrix includes only boreholes with `on_severity_matrix: true`
- [ ] Decision matrix categories preserve order from brief
- [ ] Internal map: borehole count + source count match brief
- [ ] Public map: **zero** facility names in any popup
- [ ] Public map: borehole codes are `B-NN` format
- [ ] Timeline: each event has `position_pct` + `layer` (A/B/C/D); no two adjacent events share both
- [ ] All `<bdi>` wrappers present around Latin tokens
- [ ] tokens.css inlined identically in both files
- [ ] Reference fonts loaded via Google Fonts preconnect
- [ ] Leaflet loaded from unpkg with integrity hashes
- [ ] All `% of standard` values calculated from raw concentration / DWS × 100

If any item fails → fix → re-verify. Do not output a partial build.

---

## 9 · When the brief is incomplete

The brief is the contract. If a required field is missing, **halt with a clear error** rather than inventing data:

> `briefs/<zone>.yaml`: missing required field `findings[3].metadata.percent_of_standard`. Either provide it or set `urgency: high` and explain in `body_internal`.

Optional fields (e.g. `plume_paths`, `timeline[].edge`) can be safely omitted.

---

## 10 · Anti-patterns (DO NOT DO)

- ❌ Redesign anything. The reference files are frozen.
- ❌ Invent KPI cards or sections not specified in the brief.
- ❌ Use any color outside the token palette.
- ❌ Leak facility names into PUBLIC.html — not in popups, captions, alt text, or comments.
- ❌ Use emoji as decoration (✓ in legends OK; everywhere else not).
- ❌ Generate "filler" findings if brief has fewer than 7 — output exactly what's in the brief.
- ❌ Add hover/click interactions beyond what's already in the reference.
- ❌ Change Leaflet to another map library or tile source.
- ❌ Inline base64 images — keep files lean.
- ❌ Modify tokens.css to add new variables. New tokens require explicit human approval.

---

End of instructions. Build well.
