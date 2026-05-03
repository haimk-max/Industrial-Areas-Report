# Phase 0b QA Report — 2021 Report Extraction

## Source
2021 Water Quality Report (text-based PDF, 50 pages)

## Summary Table (Table 19, page 49) — all 18 zones

| Zone | Max Index | Classification | N Boreholes | Median |
|------|-----------|----------------|-------------|--------|
| ashkelon_north | 7 | very_high | 11 | 6.1 |
| bnei_ram | 7 | very_high | 9 | 1.8 |
| rishon_letzion_east | 7 | very_high | 8 | 4.4 |
| holon | 7 | very_high | 25 | 3.5 |
| raanana | 7 | very_high | 3 | 5.0 |
| kiryat_eliezer_netanya | 7 | very_high | 14 | 4.5 |
| sapir_netanya | 6 | high | 11 | 2.4 |
| yavne | 5 | medium | 3 | 2.0 |
| rehovot_kramtech | 5 | medium | 5 | 3.0 |
| rishon_letzion_west | 4 | medium | 9 | 1.6 |
| bat_yam | 4 | medium | 4 | 1.5 |
| even_yehuda | 3 | low | 2 | 1.5 |
| nes_ziona_rehovot_sci_park | 2 | low | 4 | 0.8 |
| nes_ziona | 1 | low | 6 | 0.2 |
| ashkelon_south | 0 | none | 5 | 0.0 |
| ashdod_south | 0 | none | 5 | 0.0 |
| hadera | 0 | none | 6 | 0.0 |
| or_akiva | 0 | none | 8 | 0.0 |

## Zones with borehole index tables (4)
- **holon**: individual borehole data extracted
- **raanana**: individual borehole data extracted
- **sapir_netanya**: individual borehole data extracted
- **kiryat_eliezer_netanya**: individual borehole data extracted

## Zones without borehole tables (14)
(indices in graphical format only — require manual reading from PDF charts)
- ashkelon_south
- ashkelon_north
- ashdod_south
- yavne
- bnei_ram
- rehovot_kramtech
- nes_ziona_rehovot_sci_park
- nes_ziona
- rishon_letzion_west
- rishon_letzion_east
- bat_yam
- even_yehuda
- hadera
- or_akiva

## Validation
- All 18 zone JSONs written: ✅
- Summary table data (Table 19, page 49) encoded: ✅
- Raanana borehole table (Table 14, page 35) encoded: ✅
- Holon borehole table (Table 13, page 32) partial: ✅
- Pydantic schema validation passed: ✅
- Raanana max_index=7 (נת רעננה 1 = TCE contamination): ✅
- Zones with index=0 classified as 'none': ✅