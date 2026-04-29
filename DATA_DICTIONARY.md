# Data Dictionary - Industrial Areas Report

## Project Overview
Structured system for generating professional reports and monitoring dashboards for groundwater quality in industrial areas. Demonstration zone: **Raanana (אזה"ת רעננה)**

## Information Architecture

### Layer 1: Current Monitoring Data (Ground Truth)
- **Location**: `Water Quality Data/` directory
- **Purpose**: Most up-to-date internal monitoring data
- **Source**: Current annual monitoring campaigns
- **Content**: Latest borehole measurements, contamination levels, trend data

### Layer 2: 2021 Baseline Report (Official Context)
- **Location**: `Base-Report/` directory
- **Source PDF**: "Water Quality Control in Industrial Areas Monitoring System in Coastal Aquifer 2021.pdf"
- **Coverage**: 18 industrial zones, regional overview
- **Role**: Official context layer, NOT a comparison table

### Layer 3: TAHAL 2008 Historical (Planning Depth)
- **Location**: `Base-Report/` directory
- **Source PDFs**: Parts A & B of 2008 assessment
- **Coverage**: Historical methodology (1999-2008), borehole selection criteria, risk framework
- **Role**: Historical-planning depth layer

### Layer 4: Contaminants Groups Forensics (Analysis)
- **Location**: `Raanana/forensics/` directory
- **Content**: Deep forensic analysis, source attribution, temporal patterns
- **Role**: Analytical layer for interpretation

### Layer 5: External Data (Enrichment)
- **Location**: `External Data/` directory
- **Sources**: MAFLAS/PRTR registry, Ministry databases, web searches
- **Role**: Contextual enrichment of analysis

---

## Raanana Zone Data Files

### 1. **boreholes.csv**
Master registry of all monitoring boreholes in Raanana zone.

**Columns**:
- `borehole_id`: Unique identifier (R-001, R-002, etc.)
- `name`: Human-readable borehole name
- `zone`: Zone assignment (always "Raanana" for this file)
- `easting`: UTM X coordinate (Israeli coordinate system)
- `northing`: UTM Y coordinate (Israeli coordinate system)
- `depth_m`: Total drilling depth in meters
- `geological_layer`: Hydrogeological layer designation (A2, AB, B2, B3)
- `classification`: Borehole type per TAHAL 2008:
  - `natural`: No direct contamination link
  - `column`: Partial distance from contamination source
  - `charged`: Within or near active contamination
- `source_document`: Citation to source (e.g., "TAHAL 2008 Part B p.53")
- `extraction_notes`: Notes on data extraction or interpretation

**Data Quality**:
- UTM coordinates verified against maps in 2021 Report and TAHAL 2008
- Depths cross-checked against geological profiles
- Classifications based on proximity to industrial facilities

---

### 2. **concentrations.csv**
Historical and current contamination measurements across all parameters and years.

**Columns**:
- `borehole_id`: Reference to boreholes.csv
- `parameter`: Contaminant name (TCE, 1,2-DCA, Chloroform, etc.)
- `year`: Measurement year (1999-2021)
- `concentration`: Measured concentration value
- `unit`: Concentration unit (ppb, mg/L, ng/L)
- `severity_index`: Calculated severity grade (0-8) per methodology
- `status`: Assessment status (detected, elevated, high, low, etc.)
- `source_document`: Citation to measurement source
- `notes`: Interpretation or observation (e.g., "Significant increase from 1999")

**Severity Index Scale** (from 2021 Report):
```
Index = (C_measured / C_standard) × 100

0: No contamination
1: 0 < C ≤ 30
2: 30 < C ≤ 60
3: 60 < C ≤ 90
4: 90 < C ≤ 1,870
5: 1,870 < C ≤ 4,080
6: 4,080 < C ≤ 7,180
7: 7,180 < C ≤ 10,000
8: C > 10,000
```

**Data Quality**:
- All values extracted from TAHAL 2008 Part B Table 10.6
- Units standardized to ppb for consistency
- Severity indices recalculated from source values

---

### 3. **industries.json**
Industrial facilities in Raanana zone and their potential contamination linkages.

**Top-Level Fields**:
- `zone`: Zone identifier
- `zone_name_he`: Hebrew zone name
- `industries`: Array of industrial facility records
- `flow_affected_boreholes`: Mapping of industry → affected boreholes

**Industry Record Fields**:
- `id`: Facility identifier (I-001, I-002, etc.)
- `name`: English facility name
- `name_he`: Hebrew facility name
- `type`: Industry category (Chemicals, Pharmaceuticals, Light Manufacturing, etc.)
- `category`: Specific subcategory
- `easting`, `northing`: Facility location coordinates
- `potential_contaminants`: List of contaminants this facility could produce
- `risk_level`: Qualitative risk assessment (low, medium, high, etc.)
- `notes`: Contextual information

**Data Quality**:
- Industry locations inferred from maps in 2021 Report and TAHAL 2008
- Facility names anonymized due to data sensitivity
- Contamination linkages based on industry process knowledge

---

### 4. **flow_direction.json**
Groundwater flow patterns, velocity, and aquifer vulnerability assessment.

**Top-Level Sections**:
- `primary_flow`: Main groundwater direction
- `local_flow_variations`: Regional deviations from primary direction
- `flow_velocity`: Estimated m/year with min/max/average
- `water_table_depth`: Depth to groundwater (m)
- `boreholes_gradient_relationship`: Upgradient/on-gradient/downgradient classification
- `vulnerability_assessment`: Aquifer sensitivity and contamination spread rate

**Data Quality**:
- Flow direction based on contour interpretation from 2021 Report maps
- Not field-measured; based on hydrogeological theory
- Velocity estimates from TAHAL 2008 hydrogeological section

---

### 5. **forensics/contamination_families.json**
Deep analytical interpretation of contamination patterns and source attribution.

**Top-Level Sections**:
- `TCE_decay_chain`: TCE and its degradation products (DCE, vinyl chloride)
- `chlorinated_compounds`: 1,2-DCA, dichloromethane, chloroform
- `heavy_metals`: Fe, Mn, Zn, Cu, Pb, Cd
- `PFAS_family`: Per- and Polyfluoroalkyl substances (not in TAHAL 2008, recommendation for addition)
- `co_occurrence_patterns`: Which contaminants appear together (source signatures)
- `temporal_forensics`: Trends over time, anomalies, hypotheses

**Forensic Interpretation**:
- Pattern 1: TCE + chlorinated compounds → Chemical synthesis facility (I-001)
- Pattern 2: Dichloromethane + VOCs → Pharmaceutical manufacturing (I-002)
- Anomalies flagged for expert review (e.g., 2004 TCE drop followed by 2006 spike)

**Data Quality**:
- All interpretations based on documented contaminant patterns
- Source attributions supported by industry type and location
- Hypotheses marked as requiring expert validation

---

## Contamination Families Reference

### Volatil Organic Compounds (VOCs) - Light Solvents/Dyes
- TCE (Trichloroethylene) - Primary detected
- Benzene, Toluene, Xylene (BTEX)
- Dichloromethane

### Chlorinated Compounds
- 1,2-DCA (1,2-Dichloroethane) - Highly volatile
- cis-1,2-DCE, trans-1,2-DCE (Dichloroethylene isomers)
- Chloroform - Persistent disinfection byproduct

### Fuel-Related
- MTBE (Methyl tert-butyl ether)
- TBA (tert-Butyl alcohol)

### Heavy Metals
- Iron (Fe), Manganese (Mn), Zinc (Zn)
- Copper (Cu), Lead (Pb), Cadmium (Cd)

### PFAS (Per- and Polyfluoroalkyl Substances)
- PFOA, PFOS - Priority compounds
- Chain-length variants
- **Note**: Not in TAHAL 2008 data; recommended addition post-2021

### Nutrients & General
- Nitrate (NO₃⁻), Nitrite (NO₂⁻), Ammonium (NH₄⁺)
- pH, Electrical Conductivity (EC)
- Total Organic Carbon (TOC)
- Biological Oxygen Demand (BOD), Chemical Oxygen Demand (COD)

---

## Methodology

### Trend Identification
1. **Data Point Mapping**: Plot all historical measurements chronologically
2. **Linear Regression**: Calculate slope and R² for trend significance
3. **Multi-Period Segmentation**: Compare 1999-2008 vs 2008-2015 vs 2015-2021
4. **Moving Average**: Smooth noise to reveal underlying trends
5. **Anomaly Detection**: Flag points deviating significantly from trend
6. **Classification**: Label as Increasing/Stable/Decreasing/Volatile/Stable-Low

### Severity Index Calculation
```
Index = (C_measured / C_standard) × 100
```
Then assign grade 0-8 based on reference table in 2021 Report.

### Risk Assessment Framework
- Proximity to active industry
- Borehole depth and geological vulnerability
- Distance from shoreline and water table
- Groundwater flow direction (up/on/down-gradient)
- Pollution source identification

### Borehole Classification (TAHAL 2008)
- **Natural**: No direct contamination link
- **Column**: Partial distance from contamination source
- **Charged**: Within or near active contamination

---

## Data Validation & Quality Assurance

### Source Attribution
Every data point must cite its source:
- TAHAL 2008 Part A/B with page number
- 2021 Report with page number
- External database with access date

### Recalculation Verification
- Severity indices recalculated from raw concentrations
- Trend slopes verified against source document interpretations
- Boreholes coordinates checked against maps

### Edge Cases & Limitations
- **Data Gap 2008-2021**: Available measurements only, no interpolation
- **PFAS Absent**: Pre-dates PFAS awareness; add from 2021+ data
- **Industrial Attribution**: Requires expert judgment; forensics flag uncertainties
- **Flow Direction**: Estimated from hydrogeology, not field-measured

---

## Next Phases

### Phase 2: Historical Data Integration
- Extract all 2021 data from official report
- Merge with TAHAL 2008 historical data
- Validate date ranges and parameter coverage
- Flag any inconsistencies for expert review

### Phase 3: Drilling Card & Report Generation
- Per-borehole summary cards with maps, trends, risk assessment
- Zone-level report with regional context
- Forensics section with source attribution
- Recommendations based on trends and severity

### Phase 4: System Validation & Annual Cycle
- Expert review of methodology alignment
- Validation against regulatory standards
- Approved report becomes context layer for next year

---

**Document Version**: 1.0  
**Date**: 2026-04-29  
**Raanana Data Extraction Status**: Complete for TAHAL 2008; Pending 2021 integration
