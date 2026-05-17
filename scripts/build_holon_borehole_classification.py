#!/usr/bin/env python3
"""Build comprehensive borehole classification for all Holon boreholes.

Analyzes water quality measurements (2021-2026) to classify each borehole by:
  - Contamination severity (max bucket across families)
  - Contamination families present
  - Recent measurement status
  - Alert criteria (ALERT/WATCH/STABLE/DECREASING/NONE)

Outputs: CSV with all boreholes, their coordinates, classifications, and stats.
"""

import pandas as pd
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
EXCEL_PATH = REPO_ROOT / "Water Quality Data" / "ההיסטוריה איכות מים לקידוחים - חולון.xlsx"
ALERT_BOREHOLES_PATH = REPO_ROOT / "Holon" / "lean_workspace" / "02_data_filtered" / "alert_boreholes.csv"
SEVERITY_PATH = REPO_ROOT / "Holon" / "lean_workspace" / "04_deterministic_anchors" / "severity_index_2025_holon.csv"
OUTPUT_PATH = REPO_ROOT / "Holon" / "lean_workspace" / "04_deterministic_anchors" / "borehole_classification_all.csv"

# Contamination families and key parameters
FAMILIES = {
    'CVOC': ['TCE', 'PCE', '1,4-DIOXANE', 'VINYL CHLORIDE'],
    'METALS': ['CHROMIUM', 'NICKEL', 'LEAD'],
    'FUEL': ['BENZENE', 'TOLUENE', 'MTBE'],
}

# Simplified drinking water standards (µg/L)
DWS = {
    'TCE': 5,
    'PCE': 5,
    '1,4-DIOXANE': 0.35,
    'VINYL CHLORIDE': 2,
    'CHROMIUM': 10,
    'NICKEL': 70,
    'LEAD': 10,
    'BENZENE': 5,
    'TOLUENE': 70,
    'MTBE': 20,
}

def load_excel_data() -> pd.DataFrame:
    """Load Holon water quality Excel file."""
    df = pd.read_excel(EXCEL_PATH, sheet_name=0, header=2)

    col_map = {
        'זיהוי קידוח': 'borehole_id',
        'שם קידוח': 'borehole_name',
        'מזרח': 'east_itm',
        'צפון': 'north_itm',
        'אגן': 'basin',
        'ייעוד הקידוח': 'designation',
        'אתר ניטור': 'monitoring_site',
        'סוג זיהום': 'contamination_type',
        'תאריך מדידה': 'measurement_date',
        'עומק הדיגום': 'sampling_depth',
        'שם פרמטר': 'parameter',
        'יחידת מידה': 'unit',
        'ריכוז': 'concentration',
        'סמן': 'marker',
        'תקן מי שתיה': 'drinking_water_standard',
        'אחוז מתקן מי השתיה': 'pct_standard'
    }

    df.rename(columns=col_map, inplace=True)
    df = df.dropna(subset=['borehole_id'])
    df['measurement_date'] = pd.to_datetime(df['measurement_date'], errors='coerce')

    # Filter to last 5 years
    df = df[df['measurement_date'].dt.year >= 2021].copy()

    return df

def load_alert_boreholes() -> set:
    """Load set of ALERT borehole IDs."""
    if ALERT_BOREHOLES_PATH.exists():
        alert_df = pd.read_csv(ALERT_BOREHOLES_PATH)
        return set(alert_df['borehole_id'].unique())
    return set()

def normalize_param_name(param: str) -> str:
    """Normalize parameter names to match family definitions."""
    if not isinstance(param, str):
        return ""
    param = param.upper().strip()
    # Remove common prefixes/suffixes
    param = param.replace(' AS CL', '').replace(' AS NO3', '').replace(' AS N', '')
    return param

def get_family(param: str) -> str:
    """Determine contamination family for parameter."""
    param_norm = normalize_param_name(param)
    for family, params in FAMILIES.items():
        for p in params:
            if p in param_norm:
                return family
    return None

def classify_borehole(borehole_df: pd.DataFrame, alert_ids: set) -> dict:
    """Classify a single borehole."""
    borehole_id = borehole_df['borehole_id'].iloc[0]
    borehole_name = borehole_df['borehole_name'].iloc[0]
    east = borehole_df['east_itm'].iloc[0]
    north = borehole_df['north_itm'].iloc[0]

    # Determine families with measurements
    families_present = set()
    max_pct_standard = 0
    crossed_standard_count = 0
    num_measurements = 0
    latest_date = None

    for _, row in borehole_df.iterrows():
        param = row['parameter']
        family = get_family(param)

        if family:
            families_present.add(family)

        if pd.notna(row['pct_standard']):
            num_measurements += 1
            pct = float(row['pct_standard'])
            max_pct_standard = max(max_pct_standard, pct)

            if pct > 100:
                crossed_standard_count += 1

        if pd.notna(row['measurement_date']):
            latest_date = max(latest_date, row['measurement_date']) if latest_date else row['measurement_date']

    # Determine severity bucket (0-8 scale, simplified)
    if crossed_standard_count >= 3:
        severity_bucket = 8
    elif max_pct_standard > 300:
        severity_bucket = 7
    elif max_pct_standard > 150:
        severity_bucket = 6
    elif max_pct_standard > 100:
        severity_bucket = 5
    elif max_pct_standard > 50:
        severity_bucket = 4
    elif max_pct_standard > 10:
        severity_bucket = 3
    elif max_pct_standard > 0:
        severity_bucket = 1
    else:
        severity_bucket = 0

    # Determine classification
    is_alert = borehole_id in alert_ids
    if is_alert:
        classification = 'ALERT'
    elif severity_bucket >= 6:
        classification = 'WATCH'
    elif severity_bucket >= 4:
        classification = 'ELEVATED'
    elif severity_bucket >= 1:
        classification = 'STABLE'
    else:
        classification = 'NONE'

    return {
        'borehole_id': int(borehole_id),
        'borehole_name': borehole_name,
        'east_itm': east,
        'north_itm': north,
        'severity_bucket': severity_bucket,
        'families': ','.join(sorted(families_present)) if families_present else '',
        'num_families': len(families_present),
        'max_pct_standard': round(max_pct_standard, 1),
        'crossed_standard_count': crossed_standard_count,
        'num_measurements_2021_26': num_measurements,
        'latest_measurement_date': latest_date.date() if latest_date else None,
        'classification': classification,
        'is_alert': is_alert
    }

def main():
    print("Loading Holon water quality data (2021-2026)...")
    df = load_excel_data()

    print(f"  Loaded {len(df)} measurements for {df['borehole_id'].nunique()} boreholes")

    print("Loading ALERT borehole list...")
    alert_ids = load_alert_boreholes()
    print(f"  Found {len(alert_ids)} ALERT boreholes")

    print("Classifying boreholes...")
    results = []

    for borehole_id, borehole_group in df.groupby('borehole_id'):
        classification = classify_borehole(borehole_group, alert_ids)
        results.append(classification)

    results_df = pd.DataFrame(results)
    results_df = results_df.sort_values(['classification', 'severity_bucket'],
                                       ascending=[False, False])

    # Output statistics
    print(f"\nBorehole Classification Summary (2021-2026):")
    print(f"  Total boreholes: {len(results_df)}")
    print(f"  ALERT: {len(results_df[results_df['classification'] == 'ALERT'])}")
    print(f"  WATCH: {len(results_df[results_df['classification'] == 'WATCH'])}")
    print(f"  ELEVATED: {len(results_df[results_df['classification'] == 'ELEVATED'])}")
    print(f"  STABLE: {len(results_df[results_df['classification'] == 'STABLE'])}")
    print(f"  NONE: {len(results_df[results_df['classification'] == 'NONE'])}")

    print(f"\nContamination families distribution:")
    for family in ['CVOC', 'METALS', 'FUEL']:
        count = len(results_df[results_df['families'].str.contains(family, na=False)])
        print(f"  {family}: {count} boreholes")

    # Save to CSV
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    results_df.to_csv(OUTPUT_PATH, index=False, encoding='utf-8-sig')
    print(f"\nSaved to {OUTPUT_PATH}")

    # Show top boreholes by severity
    print(f"\nTop 10 boreholes by severity:")
    print(results_df[['borehole_id', 'borehole_name', 'severity_bucket', 'classification',
                      'families', 'max_pct_standard']].head(10).to_string(index=False))

if __name__ == '__main__':
    main()
