# Typography

## Font families (Google Fonts)

All three are part of the IBM Plex family — designed together, harmonious across Hebrew, Latin, and numerals.

| family                    | role                                      | weights              |
| ---                       | ---                                       | ---                  |
| **IBM Plex Sans Hebrew**  | All UI, headings, body — both files       | 300, 400, 500, 600, 700 |
| **IBM Plex Mono**         | Numbers, codes, labels, mono-spaced data  | 400, 500, 600        |
| **IBM Plex Serif**        | Long prose **public only** (`context_intro`, finding bodies, means cards) | 300, 400, 500 |

### Why this family

- One typographic voice across three scripts (Hebrew, Latin, numerals).
- Tabular numbers via `font-feature-settings:"tnum"` — critical for data tables.
- Geometric, neutral, conservative — credible for government work without being bureaucratic.
- Free, well-supported, mature.

### Loader (paste in `<head>`)

```html
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans+Hebrew:wght@300;400;500;600;700&family=IBM+Plex+Serif:wght@300;400;500&family=IBM+Plex+Mono:wght@400;500;600&display=swap" rel="stylesheet">
```

For internal-only (no serif), drop the `Plex+Serif` segment.

## RTL discipline

The document is `<html lang="he" dir="rtl">`. Hebrew is the dominant direction. Latin tokens embedded in Hebrew text **must be isolated** with `<bdi>`:

```html
ב-<bdi>04/2025</bdi> חצה הקידוח <bdi>מק חולון 14</bdi> את תקן ה-<bdi>TCE</bdi> ל-<bdi>7.59 µg/L</bdi>.
```

Without `<bdi>`, the BiDi algorithm will produce visually-corrupted ordering (e.g. dates flipped, percentages misaligned with their unit).

### Where to bdi

Wrap these in `<bdi>`:
- Years and dates: `<bdi>04/2025</bdi>`, `<bdi>2020–2026</bdi>`
- Borehole IDs: `<bdi>מק חולון 14</bdi>` (yes, even Hebrew names with numbers)
- Chemical codes: `<bdi>TCE</bdi>`, `<bdi>1,4-דיאוקסן</bdi>`
- Numbers + units: `<bdi>7.59 µg/L</bdi>`, `<bdi>101%</bdi>`
- Document IDs: `<bdi>HOL/EXEC/INT/2026-01</bdi>`

### Apply isolate to block elements

In tokens.css:
```css
p, li, td, th, h1, h2, h3, h4, h5, figcaption { unicode-bidi: isolate; }
```

## Type scale (informal)

Maintained via inline values in component CSS, not formal scale tokens. Approximate sizes:

| usage                         | size      | family | weight |
| ---                           | ---       | ---    | ---    |
| Hero H1 (public)              | 64px      | sans   | 300    |
| Section H2                    | 24–32px   | sans   | 500–600 |
| KPI big number                | 44–54px   | sans   | 300–500 |
| Finding H3                    | 20–22px   | sans   | 600    |
| Body prose (public)           | 16–18px   | serif  | 400    |
| Body prose (internal)         | 14.5px    | sans   | 400    |
| Bottom-line block (internal)  | 17px      | sans   | 400    |
| Table cell                    | 12.5–14px | sans   | 400–500 |
| Meta/caption                  | 10.5–11px | mono   | 500–600 |
| Eyebrow / chip                | 11–12px   | mono   | 500    |

When uncertain, copy values from the reference files.

## Numbers

Use IBM Plex Mono with tabular numbers (`font-feature-settings:"tnum"`) for any numerical data — KPI values, table cells, percentages, dates. This keeps columns aligned.

Body text containing numbers can stay in sans (Hebrew flow); but wrap each number in `<bdi>` so the BiDi algorithm renders it correctly.
