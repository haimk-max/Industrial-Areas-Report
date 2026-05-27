"""
Data pipeline utilities: CSV parsing, measurement normalization, unit conversion.
"""

from typing import List, Dict, Tuple, Optional
import re


# Unit conversion map (all → ppb / µg/L for consistency)
UNIT_CONVERSIONS = {
    "ppb": 1.0,
    "µg/L": 1.0,
    "μg/L": 1.0,
    "ug/L": 1.0,
    "ng/L": 0.001,
    "ppt": 0.001,
    "mg/L": 1000.0,
    "mg/l": 1000.0,
    "mg/liter": 1000.0,
    "ppm": 1000.0,  # In aqueous solutions, ppm ≈ mg/L
    "%": 10000.0,   # percent → ppb (rough conversion)
}


def parse_measurements_csv(
    filepath: str,
    borehole_col: str = "borehole_id",
    date_col: str = "measurement_date",
    parameter_col: str = "parameter",
    concentration_col: str = "concentration",
    unit_col: str = "unit",
    delimiter: str = ",",
) -> List[Dict]:
    """
    Parse measurements CSV file into standardized format.

    Args:
        filepath: Path to CSV file
        borehole_col: Column name for borehole ID
        date_col: Column name for measurement date (YYYY-MM-DD format)
        parameter_col: Column name for parameter/contaminant name
        concentration_col: Column name for concentration value
        unit_col: Column name for unit
        delimiter: CSV delimiter (default comma)

    Returns:
        List of dicts, each with:
          - borehole_id
          - measurement_date
          - parameter
          - concentration (normalized to ppb)
          - original_unit
          - source
    """
    measurements = []

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            lines = f.readlines()

        if not lines:
            return measurements

        # Parse header
        header = lines[0].strip().split(delimiter)
        try:
            borehole_idx = header.index(borehole_col)
            date_idx = header.index(date_col)
            param_idx = header.index(parameter_col)
            conc_idx = header.index(concentration_col)
            unit_idx = header.index(unit_col)
        except ValueError as e:
            raise ValueError(f"Missing required column: {e}")

        # Parse data rows
        for line in lines[1:]:
            if not line.strip() or line.startswith("#"):
                continue

            fields = line.strip().split(delimiter)
            if len(fields) <= max(borehole_idx, date_idx, param_idx, conc_idx, unit_idx):
                continue

            try:
                borehole_id = fields[borehole_idx].strip()
                measurement_date = fields[date_idx].strip()
                parameter = fields[param_idx].strip()
                concentration = float(fields[conc_idx].strip())
                unit = fields[unit_idx].strip()

                # Normalize unit
                normalized_conc = normalize_units(concentration, unit)

                measurements.append({
                    "borehole_id": borehole_id,
                    "measurement_date": measurement_date,
                    "parameter": parameter,
                    "concentration": normalized_conc,
                    "original_unit": unit,
                    "source": filepath,
                })
            except (ValueError, IndexError) as e:
                # Skip malformed rows
                continue

    except FileNotFoundError:
        raise FileNotFoundError(f"Measurements file not found: {filepath}")

    return measurements


def normalize_units(
    concentration: float,
    unit: str,
) -> float:
    """
    Normalize concentration to ppb (µg/L).

    Args:
        concentration: Numeric concentration value
        unit: Unit string (ppb, mg/L, %, etc.)

    Returns:
        float: Concentration in ppb (µg/L)
    """
    if not unit:
        return concentration  # No unit → assume ppb

    unit_normalized = unit.lower().strip()

    # Check for exact match
    if unit_normalized in UNIT_CONVERSIONS:
        return concentration * UNIT_CONVERSIONS[unit_normalized]

    # Try fuzzy matching (remove spaces, special chars)
    unit_normalized_fuzzy = re.sub(r"[\s\-_/]", "", unit_normalized)
    for known_unit, factor in UNIT_CONVERSIONS.items():
        known_fuzzy = re.sub(r"[\s\-_/]", "", known_unit.lower())
        if unit_normalized_fuzzy == known_fuzzy:
            return concentration * factor

    # Default: assume ppb if unknown
    return concentration


def validate_measurement(
    measurement: Dict,
    min_conc: float = -1.0,  # Allow LOD (< 0 sometimes used for non-detect)
    max_conc: float = 1e8,   # 100 million ppb (sanity check)
) -> Tuple[bool, Optional[str]]:
    """
    Validate a measurement record.

    Args:
        measurement: Dict from parse_measurements_csv()
        min_conc: Minimum allowable concentration
        max_conc: Maximum allowable concentration (sanity check)

    Returns:
        (is_valid, error_message)
    """
    if not measurement.get("borehole_id"):
        return False, "Missing borehole_id"

    if not measurement.get("measurement_date"):
        return False, "Missing measurement_date"

    if not measurement.get("parameter"):
        return False, "Missing parameter"

    conc = measurement.get("concentration")
    if conc is None:
        return False, "Missing concentration"

    if not isinstance(conc, (int, float)):
        return False, f"Concentration not numeric: {conc}"

    if conc < min_conc or conc > max_conc:
        return False, f"Concentration out of range: {conc}"

    return True, None


def batch_normalize_measurements(
    measurements: List[Dict],
) -> List[Dict]:
    """
    Batch normalize a list of measurements (filter out invalid records).

    Args:
        measurements: List from parse_measurements_csv()

    Returns:
        List of valid measurements (invalid ones removed)
    """
    valid = []
    for m in measurements:
        is_valid, error = validate_measurement(m)
        if is_valid:
            valid.append(m)
    return valid
