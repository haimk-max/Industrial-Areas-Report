# Industrial Areas Report · Engine

A generic engine for generating two-twin executive-summary HTML reports for **any**
Israeli industrial groundwater-monitoring zone. The only thing that changes per zone
is the YAML brief — the design system, schema, and reference outputs are frozen and shared.

> This engine is **zone-agnostic** by design. Do not hard-code zone specifics into the
> design system or schema. Per-zone data lives only in `briefs/<zone>.yaml`.

## Structure

```
report-engine/
├── CLAUDE.md                          ← operating manual for the build agent (read first)
├── README.md                          ← this file
├── design-system/                     ← FROZEN visual + voice contract
│   ├── README.md                      ← design-system overview
│   ├── architecture.md                ← "twins, not identical" philosophy
│   ├── tokens.css                     ← single source of truth for CSS variables
│   ├── typography.md                  ← font system + RTL discipline
│   ├── color.md                       ← semantic palette rules
│   ├── voice.md                       ← copy/tone rules (internal vs. public)
│   └── reference/                     ← gold-standard outputs (Holon)
│       ├── HOLON_INTERNAL.html
│       ├── HOLON_PUBLIC.html
│       └── index.html
├── schemas/
│   └── zone-brief.schema.json         ← JSON Schema validating each brief
├── briefs/
│   └── holon.yaml                     ← per-zone input (the only thing that varies)
└── output/
    └── holon/                         ← generated reports per zone
        ├── INTERNAL.html
        └── PUBLIC.html
```

## Pipeline

```
{zone}/output/{ZONE}_REPORT_Vn.md  (latest canonical report)
   →  scripts/generate_zone_brief.py prepare   (assembles Opus prompt + provenance)
   →  [OPUS authors raw_brief.yaml]
   →  scripts/generate_zone_brief.py finalize   (validates + injects coords + stamps source_report sha)
   →  briefs/<zone>.yaml
   →  scripts/generate_zone_html_from_brief.py   (data-replace into frozen reference)
   →  {zone}/output/{ZONE}_EXECUTIVE_SUMMARY_{INTERNAL,PUBLIC}.html   →  publish
```

Driven end-to-end by `scripts/run_pipeline.sh <ZONE> exec-summary` (Step 8). See ORCHESTRATION.md.

### Canonical deliverable location
The **distribution copies** are `{zone}/output/{ZONE}_EXECUTIVE_SUMMARY_{INTERNAL,PUBLIC}.html`
(per-zone, alongside the main report). The engine's `output/<zone>/{INTERNAL,PUBLIC}.html` is the
**build artifact**; `design-system/reference/HOLON_*.html` is the **frozen gold-standard** (do not edit).
For Holon these are the same lineage (Holon was the design source).

### Staleness contract (important)
The brief is built from a **specific report version + sha**, stamped in the brief header
(`source_report_sha256_12`). **Whenever the main report changes version (e.g. V5→V8), the brief AND
the exec summaries are stale and must be regenerated.** `run_pipeline.sh ... exec-summary` warns if the
brief's stamped sha differs from the current report. As of REQ #29, the on-disk Holon exec summaries are
V5-era (carry a visible "מיושן" banner) pending V8 regeneration after hydrogeologist approval.

### Known tech-debt (REQ #29)
`scripts/generate_zone_html_from_brief.py` still uses a few Holon-literal replacement anchors
(`"~58"`, `"HOL/2026/01"`, a Holon framing-warning substring). These work because the frozen reference
IS the Holon gold-standard; a 2nd zone will validate/replace them. Not blocking Holon.

## Adding a new zone

1. Emit `briefs/<zone>.yaml` (must validate against `schemas/zone-brief.schema.json`).
2. Run the build agent from this directory: "Build `output/<zone>/` from `briefs/<zone>.yaml`."
   It reads `CLAUDE.md` automatically.
3. Inspect the output. If anything is off, the issue is almost always in the brief, not the engine.

## Status

- **Holon** — pilot zone. `briefs/holon.yaml` fully reproduces the reference outputs.
- Reference HTML in `design-system/reference/` and the Holon output in `output/holon/`
  are byte-identical (Holon is the source from which the design system was built).

See `CLAUDE.md` for the full build process, field mappings, quality bar, and anti-patterns.
