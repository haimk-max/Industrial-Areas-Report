# Design System

This folder is the **visual and voice contract** for the Industrial Areas Report engine. It is frozen — changes require deliberate review.

## Files

| file               | purpose                                              |
| ---                | ---                                                  |
| `architecture.md`  | The "twins, not identical" philosophy. Read first.   |
| `tokens.css`       | All CSS variables. Inlined into every output.        |
| `typography.md`    | Font system, type scale, RTL rules.                  |
| `color.md`         | Semantic palette and forbidden usages.               |
| `voice.md`         | Copy/tone rules for internal vs. public.             |
| `reference/`       | Gold-standard Holon outputs. Use as structural templates. |

## How to use

When building a new zone's reports:

1. Read `architecture.md` to internalize the twin-document philosophy.
2. Open `reference/HOLON_INTERNAL.html` and `reference/HOLON_PUBLIC.html` in full. These ARE the template — your job is to replace Holon's data with the new zone's data without touching the structure.
3. Apply `voice.md` rules when writing narrative prose.
4. Verify against `color.md` and `typography.md` discipline — no decorative colors, all Latin tokens in `<bdi>`.

## Modification policy

**Never modify** without explicit stakeholder approval:
- `tokens.css` — adding new variables breaks parity with reference files
- `architecture.md` — the philosophical contract
- Any reference file's visual design

**Safe to extend** (additive, with care):
- New components in a `components/` folder (currently embedded in reference files)
- Examples in markdown docs
- Additional voice guidance in `voice.md` (clarifications, not contradictions)

## Visual identity at a glance

- **Surface:** Warm near-white `#fafaf8`, cards `#ffffff`.
- **Anchor:** Teal `#0f6b7a` — single non-grayscale brand color, used sparingly.
- **Semantic colors:** Red (exceedance), Amber (caveat), Green (success). Exclusive use.
- **Type:** IBM Plex Hebrew (UI), Plex Mono (numbers), Plex Serif (public prose only).
- **Layout:** Single column, max 920–1180px. Generous whitespace in public, dense in internal.
- **Maps:** Leaflet + CartoDB Positron tiles (neutral grey basemap).
