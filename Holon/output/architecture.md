# Architecture · "Twins, not identical"

This product is two HTML documents per zone, designed as **non-identical twins**.

## The mandate

Same evidence, two framings. Three axes shift:

1. **Source attribution** — internal names real facilities; public uses generic categories.
2. **Technical depth** — internal quantifies (µg/L, % of standard, certainty); public translates ("פי X מהתקן").
3. **The "what to do" layer** — internal has a decision matrix; public has only "what it means · what we do".

## Shared DNA

Both documents are unmistakably from the same authority. They share:

- Type system (IBM Plex Hebrew · Mono · Serif)
- Color tokens (white surfaces · teal anchor · semantic red/amber/green)
- Component vocabulary (KPI cards · finding cards · maps · matrices)
- RTL Hebrew with `<bdi>` for LTR tokens
- Leaflet + CartoDB Positron for all maps
- Same factual base — every number agrees across the two

## Where they diverge

| dimension              | internal                              | public                                  |
| ---                    | ---                                   | ---                                     |
| chrome                 | classified ribbon, version, doc-id    | "transparency report" badge             |
| density                | dashboard-dense, multi-column         | airy, generous whitespace                |
| narrative              | bullet-points, decision-orientation   | flowing prose with serif for breathing  |
| sources                | named + certainty (HIGH/MED/LOW)      | generic category only                    |
| boreholes (map)        | real names                            | anonymized codes (B-01…)                 |
| sources (map)          | shown as diamonds                     | **never** shown                         |
| timeline               | absent                                | present (§02) — historical → today      |
| decision matrix        | present (§05) — 4 categories         | **never** present                        |
| methodology disclosure | minimal                               | present (§06) — explicit                |
| contact info           | classification + doc-id               | public email for raw data requests       |

## Why this matters operationally

The brief schema enforces this split: every finding has both an `_internal` and `_public` variant; every borehole has a separate `public.code` and `public.popup_rows`. **Source records carry no public-facing form by design** — they cannot leak.

If a sufficiently motivated agent or human still tries to leak facility names into the public file, they will violate explicit field-mapping rules in CLAUDE.md and fail the quality bar in §8.

This is intentional. Trust by construction, not by review.
