# Industrial Areas Report — Groundwater Quality Monitoring System

**Scope**: Structured reporting system for groundwater quality monitoring in coastal aquifer industrial zones, Israel.  
**Baseline zone**: Raanana industrial zone (קריית אתגרים) — Phases A–F complete.  
**Scale target**: 18 coastal aquifer zones (Phase 2, post-expert validation Q3 2026).

---

## Project Status

| Phase | Description | Status |
|---|---|---|
| A | Real data pipeline (Excel 2011–2026 → CSV) | ✅ Complete |
| B | Mann-Kendall trend engine (tie-corrected, SNR gating) | ✅ Complete |
| C | Charts (PFAS, CVOC, BTEX, trend charts) | ✅ Complete |
| D | Hebrew zone summary + 7 drilling cards | ✅ Complete |
| E | 3-tier borehole selection (18-zone scalable) | ✅ Complete |
| F | 25 automated regression tests | ✅ Complete |
| 4 | Expert hydrogeologist review + regulatory reporting | ⏳ Q3 2026 |

---

## Directory Structure

```
Industrial-Areas-Report/
├── Raanana/                     ← Production zone (complete)
│   ├── data/
│   │   ├── boreholes.csv        ← 7 boreholes with ITM coordinates
│   │   ├── concentrations.json  ← Time-series measurements
│   │   ├── facility_attribution.json  ← 9 suspected contamination sources
│   │   └── external/            ← PRTR queries, web findings log
│   ├── charts_v2/               ← 10 production charts (V2, current)
│   ├── forensics/               ← Forensic analysis results
│   └── output/
│       └── RAANANA_REPORT_V2.md ← Main zone summary report (Hebrew)
│
├── scripts/                     ← Data pipeline
│   ├── parse_excel.py           ← Step 1: Extract from Excel measurements
│   ├── preprocess.py            ← Step 2: Clean + normalise
│   ├── consolidate_data.py      ← Step 3: Merge TAHAL 2008 + 2021 Report
│   ├── trend_analysis.py        ← Step 4: Mann-Kendall trend engine
│   ├── forensics_analyzer.py    ← Step 5: Source attribution
│   ├── generate_charts_v2.py    ← Step 6: Generate charts + site map
│   ├── validate_report.py       ← QA: chart_refs / tone / attribution
│   ├── select_boreholes.py      ← Tier 1/2/3 zone selection
│   ├── generate_charts.py       ← [DEPRECATED — V1, use generate_charts_v2.py]
│   ├── charts/                  ← [DEPRECATED — V1 chart modules]
│   └── forensics/               ← Forensics sub-modules (active)
│
├── tests/                       ← 25 regression tests (pytest)
│   ├── test_preprocess.py       ← 8 tests: input validation, TPFAS exclusion
│   ├── test_chart_presets.py    ← 9 tests: chart rendering + PFAS S/A grouping
│   └── test_borehole_selection.py ← 8 tests: tier selection logic
│
├── zone_definitions/            ← 18-zone geographic config
│   ├── tier1_historical_boreholes.json
│   ├── zone_polygons.json       ← ITM polygons (Raanana complete; 17 pending)
│   └── tier3_cross_zone_boreholes.json
│
├── config/
│   └── analysis_config.yaml     ← MK params, SNR threshold, standards
│
├── docs/
│   ├── STYLE_GUIDE.md           ← Hebrew language + tone guide (2021 Report style)
│   └── CHART_SPEC.md            ← Chart specifications + RTL rendering
│
├── Base-Report/                 ← Source documents (PDFs, read-only)
├── External Data/               ← External data sources (see README inside)
├── Water Quality Data/          ← Raw Excel measurement files
├── base_layer/                  ← Seed data for 18-zone expansion
│
├── CLAUDE.md                    ← Project governance + phase definitions
├── DATA_DICTIONARY.md           ← Schema reference for all data files
├── REQUIREMENTS.md              ← 44 requirements (44 done, 0 pending)
└── requirements.txt             ← Python dependencies
```

---

## Running the Pipeline

```bash
# Full pipeline for Raanana zone
python scripts/parse_excel.py --zone raanana
python scripts/consolidate_data.py --zone raanana
python scripts/trend_analysis.py --zone raanana
python scripts/forensics_analyzer.py --zone raanana
python scripts/generate_charts_v2.py --zone Raanana

# Validate report quality (3 automated checks)
python scripts/validate_report.py

# Run regression tests
pytest tests/ -v
```

---

## Adding a New Zone (Phase 2)

1. `zone_definitions/tier1_historical_boreholes.json` — add zone borehole IDs
2. `zone_definitions/zone_polygons.json` — define ITM boundary polygon
3. Run pipeline with `--zone <new_zone>` flag
4. Write zone summary report + drilling cards (Raanana as template)

Requires: Ministry of Environmental Protection approval + expert validation first.

---

## Key Findings (Raanana — current)

| Parameter | Borehole | Level | Trend |
|---|---|---|---|
| PFAS (PFHxS) | nd_turbine | 1,160% of standard | Single measurement July 2025 — confirmatory Q3 2026 |
| TCE | nt_1 | 1,264% of standard | Declining from 10,900% peak (2019) |
| PCE | nt_3 | 1,055% of standard | Increasing — active PCE→TCE decay chain |
| TCE | p_25 (supply well) | 123–188% of standard | Exceedance since 2023 — supply well at risk |

Zone ranked **2nd of 18** in 2021 Water Authority contamination severity index (score 7/8).

---

## Known Limitations & Open Items

- **Basemap for site map** (`REQ-G1`): tile providers blocked in current environment — see `REQUIREMENTS.md`
- **Expert validation**: Forensic attributions await hydrogeologist review (Phase 4)
- **PFAS regulatory reporting**: Pending confirmatory sampling (Q3 2026)
- **17 zones**: Pending data integration after Raanana expert validation
