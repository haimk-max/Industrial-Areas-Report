#!/usr/bin/env python3
"""Compute descriptive statistics for all 85 Holon boreholes (2021-2026).

Outputs JSON with:
  - Per-family descriptive stats (mean, std, median, IQR, skew, kurtosis, normality)
  - Cohort comparison: ALERT (25) vs ALL (85)
  - Temporal comparison: 2018-2020 vs 2021-2026 (ALERT only — full history available)
  - Spatial patterns: top-tail boreholes, family centroids
"""

import json
import sys
import numpy as np
import pandas as pd
from pathlib import Path
from scipy import stats

REPO_ROOT = Path(__file__).resolve().parent.parent
CLASSIFICATION_PATH = REPO_ROOT / "Holon" / "lean_workspace" / "04_deterministic_anchors" / "borehole_classification_all.csv"
SEVERITY_PARAM_PATH = REPO_ROOT / "Holon" / "lean_workspace" / "04_deterministic_anchors" / "severity_index_2025_holon_param_level.csv"
MEASUREMENTS_ALERT_PATH = REPO_ROOT / "Holon" / "lean_workspace" / "02_data_filtered" / "measurements_alert.csv"
OUTPUT_PATH = REPO_ROOT / "Holon" / "lean_workspace" / "04_deterministic_anchors" / "statistics_summary_2021_2026.json"


def describe_series(series):
    s = pd.Series(series).dropna()
    if len(s) < 2:
        return None
    desc = {
        'n': int(len(s)),
        'mean': float(s.mean()),
        'std': float(s.std()) if len(s) > 1 else 0.0,
        'median': float(s.median()),
        'q25': float(s.quantile(0.25)),
        'q75': float(s.quantile(0.75)),
        'min': float(s.min()),
        'max': float(s.max()),
    }
    if len(s) >= 3:
        desc['skew'] = float(stats.skew(s))
        desc['kurtosis'] = float(stats.kurtosis(s))
        try:
            _, shapiro_p = stats.shapiro(s.head(5000))
            desc['shapiro_p'] = float(shapiro_p)
        except Exception:
            desc['shapiro_p'] = None
        pos = s[s > 0]
        if len(pos) >= 3:
            try:
                _, shapiro_log_p = stats.shapiro(np.log(pos).head(5000))
                desc['shapiro_log_p'] = float(shapiro_log_p)
            except Exception:
                desc['shapiro_log_p'] = None
    return desc


def mann_whitney(a, b):
    a = pd.Series(a).dropna()
    b = pd.Series(b).dropna()
    if len(a) < 3 or len(b) < 3:
        return None
    try:
        u_stat, p_value = stats.mannwhitneyu(a, b, alternative='two-sided')
        n1, n2 = len(a), len(b)
        z = (u_stat - (n1 * n2 / 2)) / np.sqrt(n1 * n2 * (n1 + n2 + 1) / 12)
        r_eff = abs(z) / np.sqrt(n1 + n2)
        return {
            'u_stat': float(u_stat),
            'p_value': float(p_value),
            'effect_size_r': float(r_eff),
            'effect_size_interpretation': 'small' if r_eff < 0.3 else 'medium' if r_eff < 0.5 else 'large',
        }
    except Exception as exc:
        return {'error': str(exc)}


def main():
    classification = pd.read_csv(CLASSIFICATION_PATH)
    severity = pd.read_csv(SEVERITY_PARAM_PATH)
    measurements_alert = pd.read_csv(MEASUREMENTS_ALERT_PATH)
    print(f"Loaded: {len(classification)} boreholes, {len(severity)} param-rows, {len(measurements_alert)} alert measurements")

    output = {
        'metadata': {
            'date_computed': '2026-05-11',
            'cohort_definition': 'All Holon boreholes with measurements 2021-2026; severity from latest reading per parameter',
            'total_boreholes_in_classification': int(len(classification)),
            'total_boreholes_in_severity': int(severity['borehole'].nunique()),
            'alert_boreholes': int(classification['is_alert'].sum()),
            'classification_breakdown': classification['classification'].value_counts().to_dict(),
            'severity_bucket_distribution': {str(k): int(v) for k, v in classification['severity_bucket'].value_counts().sort_index().items()},
            'data_sources': {
                'classification': str(CLASSIFICATION_PATH.relative_to(REPO_ROOT)),
                'severity_param_level': str(SEVERITY_PARAM_PATH.relative_to(REPO_ROOT)),
                'measurements_alert_history': str(MEASUREMENTS_ALERT_PATH.relative_to(REPO_ROOT)),
            },
        },
        'family_membership_counts': {},
        'by_family': {},
        'cohort_comparison_alert_vs_nonalert': {},
        'temporal_comparison_pre2021_vs_recent': {},
        'spatial_patterns': {},
    }

    family_counts = {}
    for fam_str in classification['families'].dropna():
        for fam in fam_str.split(','):
            f = fam.strip()
            family_counts[f] = family_counts.get(f, 0) + 1
    output['family_membership_counts'] = family_counts

    for family, group in severity.groupby('family'):
        family_data = {
            'n_measurements': int(len(group)),
            'n_boreholes_with_family': int(group['borehole'].nunique()),
            'n_distinct_parameters': int(group['canonical_param'].nunique()),
            'parameters_list': sorted(group['canonical_param'].unique().tolist()),
            'concentration_stats': describe_series(group['concentration']),
            'pct_of_standard_stats': describe_series(group['pct_of_standard']),
            'crossed_standard_count': int((group['pct_of_standard'] >= 100).sum()),
            'crossed_standard_pct': round(float((group['pct_of_standard'] >= 100).mean() * 100), 2),
            'bucket_distribution': {str(k): int(v) for k, v in group['bucket'].value_counts().sort_index().items()},
            'top_parameters_by_pct_std': [],
        }
        param_summary = (group.groupby('canonical_param')
                              .agg(n=('pct_of_standard', 'size'),
                                   median_pct=('pct_of_standard', 'median'),
                                   max_pct=('pct_of_standard', 'max'),
                                   n_crossed=('pct_of_standard', lambda x: int((x >= 100).sum())))
                              .reset_index()
                              .sort_values('max_pct', ascending=False))
        family_data['top_parameters_by_pct_std'] = param_summary.head(10).to_dict('records')
        output['by_family'][family] = family_data

    historical_canonical_ids = set(measurements_alert['canonical_id'].dropna().unique())
    classification['has_history_pre2021'] = classification['borehole_name'].apply(
        lambda nm: any(canonical_id.replace('_', ' ').strip() == str(nm).strip() for canonical_id in historical_canonical_ids)
    )
    hist_mask = classification['has_history_pre2021']
    hist_pct = classification.loc[hist_mask, 'max_pct_standard'].dropna()
    new_pct = classification.loc[~hist_mask, 'max_pct_standard'].dropna()
    hist_crossed = classification.loc[hist_mask, 'crossed_standard_count'].dropna()
    new_crossed = classification.loc[~hist_mask, 'crossed_standard_count'].dropna()

    top_severity_mask = classification['severity_bucket'] >= 7
    top_pct = classification.loc[top_severity_mask, 'max_pct_standard'].dropna()
    low_pct = classification.loc[~top_severity_mask, 'max_pct_standard'].dropna()

    output['cohort_comparison_alert_vs_nonalert'] = {
        '_note': 'is_alert column from classification is all False; using "has_history_pre2021" as a proxy (boreholes appearing in measurements_alert.csv with 2018+ data). Also comparing severity ≥7 vs <7.',
        'historical_25_with_pre2021_data': {
            'n': int(hist_mask.sum()),
            'max_pct_standard_stats': describe_series(hist_pct),
            'crossed_count_stats': describe_series(hist_crossed),
        },
        'new_60_recent_only': {
            'n': int((~hist_mask).sum()),
            'max_pct_standard_stats': describe_series(new_pct),
            'crossed_count_stats': describe_series(new_crossed),
        },
        'mann_whitney_historical_vs_new_max_pct': mann_whitney(hist_pct, new_pct),
        'mann_whitney_historical_vs_new_crossed': mann_whitney(hist_crossed, new_crossed),
        'severity_high_vs_low': {
            'severity_ge_7': {
                'n': int(top_severity_mask.sum()),
                'max_pct_standard_stats': describe_series(top_pct),
            },
            'severity_lt_7': {
                'n': int((~top_severity_mask).sum()),
                'max_pct_standard_stats': describe_series(low_pct),
            },
            'mann_whitney': mann_whitney(top_pct, low_pct),
        },
    }

    measurements_alert['date'] = pd.to_datetime(measurements_alert['date'], errors='coerce')
    measurements_alert = measurements_alert[measurements_alert['date'].notna()]
    early = measurements_alert[measurements_alert['date'].dt.year < 2021]
    recent = measurements_alert[measurements_alert['date'].dt.year >= 2021]

    temporal_param_comp = {}
    common_params = set(early['param_code'].dropna()) & set(recent['param_code'].dropna())
    for param in sorted(common_params):
        e = early[early['param_code'] == param]['percent_of_standard'].dropna()
        r = recent[recent['param_code'] == param]['percent_of_standard'].dropna()
        if len(e) >= 5 and len(r) >= 5:
            mw = mann_whitney(e, r)
            temporal_param_comp[param] = {
                'pre_2021': {'n': int(len(e)), 'median_pct': float(e.median()), 'max_pct': float(e.max())},
                'recent_2021_2026': {'n': int(len(r)), 'median_pct': float(r.median()), 'max_pct': float(r.max())},
                'mann_whitney': mw,
                'change_direction': ('rising' if r.median() > e.median() * 1.1
                                     else 'falling' if r.median() < e.median() * 0.9
                                     else 'stable'),
            }

    output['temporal_comparison_pre2021_vs_recent'] = {
        'note': 'Compares pre-2021 vs 2021-2026. Based on 25 ALERT boreholes (only cohort with full history).',
        'overall_counts': {'pre_2021_measurements': int(len(early)), 'recent_measurements': int(len(recent))},
        'date_range_pre_2021': f"{early['date'].min().date()} to {early['date'].max().date()}" if len(early) else None,
        'date_range_recent': f"{recent['date'].min().date()} to {recent['date'].max().date()}" if len(recent) else None,
        'by_parameter': temporal_param_comp,
    }

    coords = classification[classification['east_itm'].notna() & classification['north_itm'].notna()].copy()
    top_tail = classification[classification['severity_bucket'] >= 7].copy()
    output['spatial_patterns'] = {
        'top_tail_severity_ge_7': {
            'n': int(len(top_tail)),
            'boreholes': top_tail[['borehole_id', 'borehole_name', 'severity_bucket', 'families', 'max_pct_standard', 'classification']].to_dict('records'),
        },
        'bounding_box_itm': {
            'east_min': float(coords['east_itm'].min()),
            'east_max': float(coords['east_itm'].max()),
            'north_min': float(coords['north_itm'].min()),
            'north_max': float(coords['north_itm'].max()),
            'east_span_km': round((coords['east_itm'].max() - coords['east_itm'].min()), 2),
            'north_span_km': round((coords['north_itm'].max() - coords['north_itm'].min()), 2),
        },
        'centroids_per_family': {},
    }

    for fam in family_counts.keys():
        mask = coords['families'].fillna('').str.contains(fam)
        sub = coords[mask]
        if len(sub) > 0:
            output['spatial_patterns']['centroids_per_family'][fam] = {
                'n_boreholes': int(len(sub)),
                'east_mean_km': round(float(sub['east_itm'].mean()), 3),
                'north_mean_km': round(float(sub['north_itm'].mean()), 3),
                'east_std_km': round(float(sub['east_itm'].std()), 3) if len(sub) > 1 else 0.0,
                'north_std_km': round(float(sub['north_itm'].std()), 3) if len(sub) > 1 else 0.0,
                'severity_median': float(sub['severity_bucket'].median()),
            }

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2, default=str)

    print(f"\nWrote: {OUTPUT_PATH.relative_to(REPO_ROOT)}")
    print(f"\n=== Summary ===")
    print(f"Boreholes: {output['metadata']['total_boreholes_in_classification']}")
    print(f"Classification: {output['metadata']['classification_breakdown']}")
    print(f"Family memberships: {family_counts}")
    print(f"\nBy family (from param-level severity index):")
    for fam, data in output['by_family'].items():
        print(f"  {fam}: {data['n_measurements']} measurements, "
              f"{data['n_boreholes_with_family']} boreholes, "
              f"{data['crossed_standard_pct']}% crossed standard")
    cmp = output['cohort_comparison_alert_vs_nonalert']
    hist = cmp.get('historical_25_with_pre2021_data', {})
    new = cmp.get('new_60_recent_only', {})
    print(f"\nHistorical (with pre-2021 data) vs New (recent only):")
    print(f"  Historical n={hist.get('n')}, New n={new.get('n')}")
    if hist.get('max_pct_standard_stats') and new.get('max_pct_standard_stats'):
        print(f"  Historical median max_pct: {hist['max_pct_standard_stats']['median']:.1f}%, "
              f"New median max_pct: {new['max_pct_standard_stats']['median']:.1f}%")
        mw = cmp.get('mann_whitney_historical_vs_new_max_pct')
        if mw:
            print(f"  Mann-Whitney p={mw['p_value']:.4f}, r={mw['effect_size_r']:.3f} ({mw['effect_size_interpretation']})")
    sev = cmp.get('severity_high_vs_low', {})
    print(f"\nSeverity ≥7 ({sev.get('severity_ge_7', {}).get('n')}) vs <7 ({sev.get('severity_lt_7', {}).get('n')}):")
    if sev.get('mann_whitney'):
        print(f"  Mann-Whitney p={sev['mann_whitney']['p_value']:.4f}, r={sev['mann_whitney']['effect_size_r']:.3f}")
    print(f"\nTemporal (pre-2021 vs recent): {len(output['temporal_comparison_pre2021_vs_recent']['by_parameter'])} parameters compared")
    print(f"Top-tail (severity ≥7): {output['spatial_patterns']['top_tail_severity_ge_7']['n']} boreholes")


if __name__ == '__main__':
    main()
