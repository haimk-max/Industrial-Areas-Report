# External Data Sources

This directory contains external reference data used for contamination source attribution.

## Files

### `prtr_fulldatabase-2024.xlsx`
**Source**: Israel PRTR (Pollutant Release and Transfer Register), query date 2026-05-04  
**Purpose**: Industry-reported pollutant releases ≥1,000 kg/year threshold  
**Coverage**: National (all registered facilities)  
**Limitation**: Below-threshold facilities (common in industrial zones) not included  
**Used by**: `facility_attribution.json` — cross-referenced to identify CVOC-reporting facilities near Raanana

### `תאגיד-מי-רעננה-ניטור-שפכי-מפעלים-דיווח-שנתי-2025.pdf`
**Source**: Mey Raanana water utility, annual industrial wastewater monitoring report 2025  
**Purpose**: Industrial discharge monitoring for Raanana zone businesses  
**Coverage**: Car washes and petrol stations only (industrial facilities excluded from 2025 report)  
**Limitation**: Does not cover chemical/pharmaceutical manufacturers  
**Used by**: `facility_attribution.json` — confirms car wash + fuel station UST activity

## Usage

Both files were reviewed as part of **Phase E facility discovery** (2026-05-04).  
Results and methodology documented in:
- `Raanana/data/facility_attribution.json` (structured output)
- `Raanana/data/external/web_findings.md` (search log)
- `docs/STYLE_GUIDE.md §H` (discovery methodology)
