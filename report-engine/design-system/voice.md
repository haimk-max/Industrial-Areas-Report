# Voice

Two audiences, two voices, one truth.

## Voice A — Internal (management briefing)

**Reader:** Water Authority management. Not operational team, not bench scientists. They allocate resources and make policy calls. They have technical literacy but limited time.

**Tone:**
- Direct. No hedging. "Source contamination not cleaned" not "may indicate residual contamination".
- Action-oriented. Every finding implies a decision.
- Quantified. Always include the number: `7.59 µg/L`, `101% מהתקן`, `04/2025`.
- Names. Use real borehole names (`מק חולון 14`) and real facility names (`תדיראן קשר`).
- Marked certainty: `HIGH` / `MEDIUM` / `LOW` next to source attributions.

**Phrasing examples:**

| ✗ Avoid                              | ✓ Prefer                                     |
| ---                                  | ---                                          |
| "ייתכן שיש פוטנציאל לחריגה"          | "חרג ב-<bdi>101%</bdi> מהתקן ב-<bdi>04/2025</bdi>" |
| "פעולות שיקום נוספות יכולות לסייע"    | "להחזיר ל-<bdi>ISCO</bdi> שלב ב׳"             |
| "אזורים שדורשים תשומת לב"            | "<bdi>7+</bdi> קידוחים שותקים <bdi>39–150+ ח׳</bdi>" |

**Always include:**
- Borehole IDs (real names)
- Specific concentrations with units
- % of standard (computed, not estimated)
- Date of measurement
- Source certainty (HIGH/MEDIUM/LOW)
- Action recommendation in `action_internal` field

## Voice B — Public (transparency report)

**Reader:** Educated public — academics, environmental NGOs, professionals, engaged citizens. NOT "is my tap water safe" level — but also NOT industry experts. Background-having lay readers.

**Tone:**
- Explanatory, never condescending. Assume curiosity, not ignorance.
- Transparent about uncertainty AND gaps. "We don't have full coverage of PFAS yet — here's why and what we're doing" beats "PFAS levels are being monitored".
- Generic source categories. **Never name facilities.** Use `מפעל אלקטרוניקה / מתקן ביטחוני` not `תדיראן קשר`.
- Anonymized borehole codes. `B-01` not `מק חולון 14`.
- Plain-language scale. "פי <bdi>X</bdi> מהתקן" not z-score, not log10.
- Pair every finding with two things: **what it means** + **what we do**.

**Phrasing examples:**

| ✗ Avoid                              | ✓ Prefer                                       |
| ---                                  | ---                                            |
| "TCE concentrations of 7.59 µg/L (z=3.2)" | "פי <bdi>1.01</bdi> מהתקן — חציית סף רגעית" |
| "Tadiran facility is the source"     | "מתקן ביטחוני סמוך"                           |
| "Monitoring deficiencies exist"      | "אזורים שבהם הניטור צריך להתחזק"               |
| "ISCO remediation incomplete"        | "טיפול שיקום שטרם הסתיים"                      |

**Always include:**
- Borehole code only (`B-01`)
- Generic facility category (no proper noun)
- Public concentration framing (× standard, never z-score)
- "מה זה אומר" paragraph
- "מה אנחנו עושים" paragraph
- For exceedances: explicit acknowledgment + monitoring response

**Never include:**
- Real facility names (in body, popups, alt text, comments, ANYWHERE)
- Real borehole names except in a generic ID (B-01 not מק 14)
- Internal certainty (HIGH/MED/LOW) labels
- Internal decision matrix references
- Budget specifics ("תלוי תקציב Q3")
- Internal operational owner ("מי אחראי")

## Shared rules (both voices)

- Hebrew RTL throughout. All Latin tokens in `<bdi>`.
- No emoji in body text. Allowed: ✓ in legend/header for success.
- Numbers use IBM Plex Mono with tabular figures.
- Dates: `MM/YYYY` for months, `YYYY` for years. Wrapped in `<bdi>`.
- Standards: cite source briefly — "תקן ישראלי" or "תקן EPA" when relevant.
- Acknowledge the selection-bias caveat (framing warning) in BOTH documents.

## The transparency principle

The public document's value is not in being optimistic. It's in being **honest under load**. When findings are uncomfortable (monitoring gap, exceedance, new plume), the public voice **does not minimize them**. It states them clearly, explains them, and shows what's being done.

The reader's trust is earned by:
- Acknowledging the bad news first
- Then explaining context (selection bias, comparison standard)
- Then committing to action (what we do)

A public report that buries bad news at the bottom or hedges with "אזורים שדורשים תשומת לב" reads as evasion. A public report that leads with "<bdi>1</bdi> חריגת תקן ב-<bdi>04/2025</bdi> · אזורים שבהם הניטור חלקי" reads as authority.
