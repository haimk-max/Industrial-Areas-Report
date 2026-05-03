#!/usr/bin/env python3
"""
Data consolidation and analysis script for Industrial Areas Report.
Consolidates data from multiple CSV/JSON files and performs trend analysis.
"""

import csv
import json
import os
import sys
from pathlib import Path
from collections import defaultdict
from statistics import mean, stdev
from datetime import datetime

class RaananaDataConsolidator:
    def __init__(self, base_path="/home/user/Industrial-Areas-Report/Raanana"):
        self.base_path = Path(base_path)
        self.data_path = self.base_path / "data"
        self.boreholes = {}
        self.concentrations = defaultdict(list)
        self.industries = {}
        self.flow_direction = {}
        self.forensics = {}

    def load_boreholes(self):
        """Load borehole registry from CSV."""
        borehole_file = self.data_path / "boreholes.csv"
        with open(borehole_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                borehole_id = row['borehole_id']
                self.boreholes[borehole_id] = {
                    'name': row['name'],
                    'zone': row['zone'],
                    'easting': float(row['easting']),
                    'northing': float(row['northing']),
                    'depth_m': float(row['depth_m']),
                    'geological_layer': row['geological_layer'],
                    'classification': row['classification'],
                    'source': row['source_document']
                }
        print(f"✓ Loaded {len(self.boreholes)} boreholes")
        return self.boreholes

    def load_concentrations(self):
        """Load concentration data from CSV."""
        conc_file = self.data_path / "concentrations.csv"
        with open(conc_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                key = (row['borehole_id'], row['parameter'])
                self.concentrations[key].append({
                    'year': int(row['year']),
                    'concentration': float(row['concentration']),
                    'unit': row['unit'],
                    'severity_index': int(row['severity_index']),
                    'status': row['status'],
                    'source': row['source_document'],
                    'notes': row['notes']
                })
        print(f"✓ Loaded {len(self.concentrations)} borehole-parameter pairs")
        return self.concentrations

    def load_industries(self):
        """Load industrial facilities data from JSON."""
        industries_file = self.data_path / "industries.json"
        with open(industries_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            self.industries = data
        print(f"✓ Loaded {len(self.industries.get('industries', []))} industrial facilities")
        return self.industries

    def load_flow_direction(self):
        """Load groundwater flow data from JSON."""
        flow_file = self.data_path / "flow_direction.json"
        with open(flow_file, 'r', encoding='utf-8') as f:
            self.flow_direction = json.load(f)
        print(f"✓ Loaded flow direction data")
        return self.flow_direction

    def load_forensics(self):
        """Load forensics analysis from JSON."""
        forensics_file = self.base_path / "forensics" / "contamination_families.json"
        with open(forensics_file, 'r', encoding='utf-8') as f:
            self.forensics = json.load(f)
        print(f"✓ Loaded forensics analysis")
        return self.forensics

    def load_all(self):
        """Load all data files."""
        print("Loading Raanana data files...")
        self.load_boreholes()
        self.load_concentrations()
        self.load_industries()
        self.load_flow_direction()
        self.load_forensics()
        print("✓ All data loaded successfully\n")

    def analyze_trends(self, borehole_id, parameter):
        """Analyze concentration trends for a borehole/parameter combination."""
        key = (borehole_id, parameter)
        if key not in self.concentrations:
            return None

        data_points = self.concentrations[key]
        if len(data_points) < 2:
            return {'trend': 'insufficient_data', 'data_points': len(data_points)}

        # Sort by year
        sorted_data = sorted(data_points, key=lambda x: x['year'])
        years = [d['year'] for d in sorted_data]
        values = [d['concentration'] for d in sorted_data]

        # Calculate trend
        n = len(years)
        mean_x = mean(years)
        mean_y = mean(values)

        # Linear regression
        numerator = sum((years[i] - mean_x) * (values[i] - mean_y) for i in range(n))
        denominator = sum((years[i] - mean_x) ** 2 for i in range(n))

        if denominator == 0:
            slope = 0
        else:
            slope = numerator / denominator

        # Calculate R-squared
        y_pred = [mean_y + slope * (x - mean_x) for x in years]
        ss_tot = sum((values[i] - mean_y) ** 2 for i in range(n))
        ss_res = sum((values[i] - y_pred[i]) ** 2 for i in range(n))
        r_squared = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0

        # Classify trend
        if abs(slope) < 0.5:
            trend_class = 'stable'
        elif slope > 0:
            trend_class = 'increasing'
        else:
            trend_class = 'decreasing'

        return {
            'borehole': borehole_id,
            'parameter': parameter,
            'data_points': n,
            'year_range': f"{years[0]}-{years[-1]}",
            'slope_per_year': round(slope, 4),
            'r_squared': round(r_squared, 4),
            'trend': trend_class,
            'min_concentration': round(min(values), 2),
            'max_concentration': round(max(values), 2),
            'average_concentration': round(mean(values), 2),
            'latest_value': round(values[-1], 2),
            'latest_year': years[-1]
        }

    def generate_trend_summary(self):
        """Generate summary of all trends."""
        print("=" * 70)
        print("TREND ANALYSIS SUMMARY - RAANANA ZONE")
        print("=" * 70)
        print()

        for (borehole_id, parameter), data_points in sorted(self.concentrations.items()):
            trend = self.analyze_trends(borehole_id, parameter)
            if trend is None:
                continue

            print(f"Borehole: {borehole_id} | Parameter: {parameter}")
            print(f"  Years: {trend['year_range']} | Data Points: {trend['data_points']}")
            print(f"  Range: {trend['min_concentration']} - {trend['max_concentration']} ppb")
            print(f"  Average: {trend['average_concentration']} ppb | Latest: {trend['latest_value']} ppb ({trend['latest_year']})")
            print(f"  Trend: {trend['trend'].upper()} (slope: {trend['slope_per_year']} ppb/year, R²: {trend['r_squared']})")

            # Add interpretation
            if trend['trend'] == 'increasing':
                print(f"  ⚠️  CONCERN: Concentration increasing over time")
            elif trend['trend'] == 'decreasing':
                print(f"  ✓ POSITIVE: Concentration decreasing over time")
            elif trend['trend'] == 'stable':
                print(f"  → STABLE: Concentration relatively stable")
            print()

        print("=" * 70)

    def generate_borehole_summary(self, borehole_id):
        """Generate summary for a specific borehole."""
        if borehole_id not in self.boreholes:
            print(f"Borehole {borehole_id} not found")
            return

        bh = self.boreholes[borehole_id]
        print(f"\n{'=' * 70}")
        print(f"BOREHOLE SUMMARY: {borehole_id} - {bh['name']}")
        print(f"{'=' * 70}")
        print(f"Location: UTM {bh['easting']:.0f}, {bh['northing']:.0f}")
        print(f"Depth: {bh['depth_m']} m | Geological Layer: {bh['geological_layer']} | Classification: {bh['classification']}")
        print()

        # Find all measurements for this borehole
        params = set()
        for (bid, param) in self.concentrations.keys():
            if bid == borehole_id:
                params.add(param)

        print(f"Parameters Monitored: {', '.join(sorted(params))}")
        print()

        for param in sorted(params):
            trend = self.analyze_trends(borehole_id, param)
            if trend:
                print(f"  {param}:")
                print(f"    {trend['year_range']} | {trend['data_points']} measurements")
                print(f"    Latest: {trend['latest_value']} ppb ({trend['latest_year']}) | Trend: {trend['trend']}")
        print()

def main():
    consolidator = RaananaDataConsolidator()
    consolidator.load_all()
    consolidator.generate_trend_summary()

    # Example: detailed summary for critical borehole
    print("\n\nDetailed Summary for Critical Borehole:")
    consolidator.generate_borehole_summary("R-004")

if __name__ == "__main__":
    main()
