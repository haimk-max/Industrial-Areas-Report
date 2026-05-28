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
raw monitoring data  →  ETL emits briefs/<zone>.yaml  →  validate vs. schema
   →  build agent reads CLAUDE.md + design-system/ + brief
   →  writes output/<zone>/{INTERNAL,PUBLIC}.html  →  publish
```

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
