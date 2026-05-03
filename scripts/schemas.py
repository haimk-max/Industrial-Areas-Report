"""Pydantic models for all base_layer JSON files and Raanana data."""
from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class Coordinates(BaseModel):
    easting: float
    northing: float
    crs: str = "EPSG:2039"


class Borehole(BaseModel):
    id: str
    name: str
    name_he: str | None = None
    coordinates: Coordinates
    depth_m: float | None = None
    geological_layer: str | None = None
    classification: Literal["natural", "column", "charged"] | None = None
    source_document_page: int | None = None


class Measurement(BaseModel):
    borehole_id: str
    parameter: str
    unit: str
    year: int
    concentration: float | None
    source_page: int | None = None


class Industry(BaseModel):
    id: str
    name: str
    name_he: str | None = None
    coordinates: Coordinates
    type: str
    category: str | None = None
    potential_contaminants: list[str] = Field(default_factory=list)
    risk_level: Literal["low", "medium-low", "medium", "medium-high", "high"]
    source_page: int | None = None
    notes: str | None = None


class RiskAssessment(BaseModel):
    overall_risk: str
    aquifer_type: str | None = None
    vulnerability: str | None = None
    contamination_spread_rate: str | None = None
    source_document_page: int | None = None


class TahalZoneData(BaseModel):
    """Schema for base_layer/tahal_2008/{zone_id}.json"""
    zone_id: str
    zone_name_he: str
    source_document: str
    boreholes: list[Borehole] = Field(default_factory=list)
    measurements_1999_2008: list[Measurement] = Field(default_factory=list)
    industries: list[Industry] = Field(default_factory=list)
    risk_assessment: RiskAssessment | None = None


class ExceedanceParameter(BaseModel):
    borehole_id: str
    parameter: str
    unit: str
    concentration: float
    drinking_water_standard: float | None
    percent_of_standard: float | None
    severity_level: int | None
    source_page: int | None = None


class ZoneComparison(BaseModel):
    rank_among_18_zones: int | None
    description: str | None
    source_page: int | None


class MonitoringRecommendations(BaseModel):
    frequency: str | None
    parameters: list[str] = Field(default_factory=list)
    recommended_boreholes: list[str] = Field(default_factory=list)
    source_page: int | None = None


class Report2021ZoneData(BaseModel):
    """Schema for base_layer/report_2021/{zone_id}.json"""
    zone_id: str
    zone_name_he: str
    severity_index: int | None
    severity_classification: str | None
    source_document: str
    boreholes_2021: list[Borehole] = Field(default_factory=list)
    exceedance_parameters: list[ExceedanceParameter] = Field(default_factory=list)
    zone_comparison: ZoneComparison | None = None
    monitoring_recommendations: MonitoringRecommendations | None = None


class ParameterEntry(BaseModel):
    code: str
    name: str
    name_he: str | None = None
    cas_number: str | None = None
    units: list[str] = Field(default_factory=list)
    family: str | None = None
    drinking_water_standard: float | None = None
    drinking_water_standard_unit: str | None = None
    drinking_water_standard_source: str | None = None
    is_calculated: bool = False
    detected_zones: list[str] = Field(default_factory=list)
    sources: list[str] = Field(default_factory=list)


class ParametersDictionary(BaseModel):
    """Schema for base_layer/parameters_dictionary.json"""
    parameters: list[ParameterEntry]
    families: dict[str, list[str]]
    excluded_calculated: list[str] = Field(default_factory=list)


class TrendRow(BaseModel):
    """Schema for Raanana/data/trends.csv (one row)"""
    borehole_id: str
    parameter: str
    n: int
    n5: int
    mk_z_5y: float | None
    mk_p_5y: float | None
    mk_z_full: float | None
    mk_p_full: float | None
    snr_5y: float | None
    soft_trigger: bool
    classification: Literal["ALERT", "WATCH", "STABLE", "DECREASING", "NONE"]
    last_two_5y: str | None
    crossed_standard: bool
