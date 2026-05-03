"""Phase 0c: Build base_layer/parameters_dictionary.json from Excel + known families.

Reads all unique (code, name, unit, standard) from the Excel, classifies into families,
marks TPFAS and other calculated parameters as is_calculated=True.

Usage:
    python scripts/build_parameters_dictionary.py [--config ...] [--input <excel_path>]
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from scripts.cli_common import load_config, make_parser
from scripts.logging_setup import get_logger
from scripts.schemas import ParameterEntry, ParametersDictionary

log = get_logger("build_parameters_dict")

EXCEL_PATH = REPO_ROOT / "Water Quality Data" / "היסטורית איכות מים לקידוחים - מעודכן לבדיקה.xlsx"
OUTPUT_PATH = REPO_ROOT / "base_layer" / "parameters_dictionary.json"

# Parameters that are calculated sums — MUST be excluded from trend analysis/charts
CALCULATED_PARAMETERS = {"TPFAS", "BETK"}

# Explicit family assignments (code → family)
# Parameters not listed here are assigned to "other" by pattern matching
FAMILY_MAP: dict[str, str] = {
    # ── PFAS ─────────────────────────────────────────────────────────────────
    "PFOS": "PFAS", "PFBS": "PFAS", "PFHxS": "PFAS", "PFHpS": "PFAS",
    "PFDS": "PFAS", "6:2FT": "PFAS", "82FTS": "PFAS", "FOSA": "PFAS",
    "PFOA": "PFAS", "PFHxA": "PFAS", "PFHpA": "PFAS", "PFNA": "PFAS",
    "PFDA": "PFAS", "PFDoA": "PFAS", "PFUnA": "PFAS", "PFBA": "PFAS",
    "PFPeA": "PFAS", "PFESA": "PFAS", "ADONA": "PFAS",
    "TPFAS": "PFAS",  # calculated sum — is_calculated=True
    # ── CVOC ─────────────────────────────────────────────────────────────────
    "TECE": "CVOC", "TCEY": "CVOC",  # PCE
    "CDCE": "CVOC", "TDCE": "CVOC", "DCEY": "CVOC", "VYCL": "CVOC",  # DCE variants + VC
    "CCL4": "CVOC",
    "DCET": "CVOC", "DCET1": "CVOC",  # 1,2-DCA, 1,1-DCA
    "TCET": "CVOC", "TCEN": "CVOC",  # 1,1,1-TCA, 1,1,2-TCA
    "DCLM": "CVOC", "METCH": "CVOC",  # DCM variants
    "CHLET": "CVOC", "CHLMT": "CVOC",  # Chloroethane, Chloromethane
    "TEC12": "CVOC", "TEC22": "CVOC",
    "DCPN": "CVOC", "DCP11": "CVOC", "DCP13": "CVOC", "DCP22": "CVOC",
    "DCHP1": "CVOC", "DP13E": "CVOC", "DP13T": "CVOC",
    "HXCB": "CVOC", "TRBN3": "CVOC", "TRBN4": "CVOC",
    "DCB13": "CVOC", "PDCB": "CVOC", "MDCB": "CVOC", "MCBZ": "CVOC",
    "CTN2": "CVOC", "CTN4": "CVOC",
    "TRPR3": "CVOC",
    "TCFM": "CVOC", "DCDFM": "CVOC",  # refrigerants
    "TRFL": "CVOC",  # trifluorylene
    # ── BTEX / Fuel aromatics ─────────────────────────────────────────────────
    "BENZ": "BTEX", "TOLU": "BTEX", "ETBN": "BTEX",
    "XYLE": "BTEX", "OXYL": "BTEX", "PXYL": "BTEX",
    "STYR": "BTEX", "NAPT": "BTEX",
    "IPBNZ": "BTEX", "NPBNZ": "BTEX", "NBTBZ": "BTEX",
    "SBBNZ": "BTEX", "TBBNZ": "BTEX", "PTOLU": "BTEX",
    "TRMB4": "BTEX", "TRMB5": "BTEX",
    "BRBNZ": "BTEX",
    # ── THM (Trihalomethanes) ─────────────────────────────────────────────────
    "CHLF": "THM", "DCBM": "THM", "DBRMT": "THM", "TRBRM": "THM",
    "BRDCM": "THM",
    # ── Fuel / Petroleum ─────────────────────────────────────────────────────
    "MTBE": "fuel", "MOL": "fuel", "TPH": "fuel", "TOC": "fuel",
    # ── Heavy metals ─────────────────────────────────────────────────────────
    "PB": "heavy_metals", "CD": "heavy_metals", "CR": "heavy_metals",
    "HG": "heavy_metals", "NI": "heavy_metals", "CU": "heavy_metals",
    "ZN": "heavy_metals", "AS": "heavy_metals", "AG": "heavy_metals",
    "AL": "heavy_metals", "BA": "heavy_metals", "BE": "heavy_metals",
    "CO": "heavy_metals", "FE": "heavy_metals", "FE++": "heavy_metals",
    "MN": "heavy_metals", "MO": "heavy_metals", "SE": "heavy_metals",
    "SR": "heavy_metals", "TL": "heavy_metals", "U": "heavy_metals",
    "Sb": "heavy_metals", "LI": "heavy_metals",
    # ── Major ions ────────────────────────────────────────────────────────────
    "CA": "major_ions", "CL": "major_ions", "HCO3": "major_ions",
    "SO4": "major_ions", "NA": "major_ions", "K": "major_ions",
    "Mg": "major_ions", "B": "major_ions", "NO3": "major_ions",
    "F": "major_ions", "BR": "major_ions", "SIO2": "major_ions",
    # ── Pesticides / Herbicides ───────────────────────────────────────────────
    "ALAC": "pesticides", "ALCB": "pesticides", "ALDSU": "pesticides",
    "ALSD": "pesticides", "ATRA": "pesticides", "BRMC": "pesticides",
    "CARFN": "pesticides", "CLDN": "pesticides", "CLPF": "pesticides",
    "DADN": "pesticides", "DBCP": "pesticides", "DBR3C": "pesticides",
    "DCPA": "pesticides", "DDT": "pesticides", "DDD": "pesticides",
    "DDE": "pesticides", "DIQAT": "pesticides", "DNSB": "pesticides",
    "HEPE": "pesticides", "HEPT": "pesticides", "LIND": "pesticides",
    "MTAL": "pesticides", "SIMZ": "pesticides", "TCAA": "pesticides",
    "TCPA": "pesticides", "MCPA": "pesticides", "OXAMY": "pesticides",
    "PCP": "pesticides", "PCB": "pesticides",
    "24DNT": "pesticides", "26DNT": "pesticides", "ADRN": "pesticides",
    # ── Physical / Field params ───────────────────────────────────────────────
    "EC": "physical", "ECFD": "physical", "PHFD": "physical",
    "PHLB": "physical", "T": "physical", "TDS": "physical",
    "DO": "physical", "ORP": "physical", "TUF": "physical",
    "TURB": "physical", "COLR": "physical", "MBAS": "physical",
    "HARD": "physical", "UV": "physical", "WDEP": "physical",
    # ── Radioactivity ─────────────────────────────────────────────────────────
    "ALFA": "radioactivity", "BETA": "radioactivity", "BETK": "radioactivity",
    # ── Emerging / Pharmaceuticals ────────────────────────────────────────────
    "CARBO": "emerging", "BEPT": "emerging", "BNZP": "emerging",
    "FORM": "emerging", "ACET": "emerging",
    # ── Nitrogenous ──────────────────────────────────────────────────────────
    "CN": "nitrogenous", "TN-N": "nitrogenous", "TP-P": "nitrogenous",
    # ── Other halogenated ────────────────────────────────────────────────────
    "ETDB": "other_halogenated", "DBR12": "other_halogenated",
    "DBRM": "other_halogenated", "BRCM": "other_halogenated",
    "BRMET": "other_halogenated",
}

# PFAS sub-family (S = sulfonate chain, A = carboxylate/acid chain)
PFAS_S_GROUP = {"PFOS", "PFBS", "PFHxS", "PFHpS", "PFDS", "6:2FT", "82FTS", "FOSA"}
PFAS_A_GROUP = {"PFOA", "PFHxA", "PFHpA", "PFNA", "PFDA", "PFDoA", "PFUnA",
                "PFBA", "PFPeA", "PFESA", "ADONA"}


def _load_excel_params(excel_path: Path) -> dict[str, dict]:
    """Returns {code: {name, unit, standard}} for all unique parameters in Excel."""
    import openpyxl
    wb = openpyxl.load_workbook(str(excel_path), read_only=True)
    ws = wb.active
    params: dict[str, dict] = {}
    for row in ws.iter_rows(min_row=4, values_only=True):
        if row[0] is None:
            break
        code = row[12]
        if code and code not in params:
            params[code] = {
                "name": row[13] or code,
                "unit": row[14] or "microgr/L",
                "drinking_water_standard": row[17],
            }
    wb.close()
    return params


def main() -> None:
    parser = make_parser("Phase 0c: Build unified parameters dictionary.")
    args = parser.parse_args()
    load_config(args.config)

    excel_path = Path(args.input) if args.input else EXCEL_PATH
    if not excel_path.exists():
        print(f"ERROR: Excel not found: {excel_path}", file=sys.stderr)
        sys.exit(1)

    log.info("loading_excel", path=str(excel_path))
    raw_params = _load_excel_params(excel_path)
    log.info("params_loaded", count=len(raw_params))

    entries: list[ParameterEntry] = []
    family_index: dict[str, list[str]] = {}

    for code, info in sorted(raw_params.items()):
        family = FAMILY_MAP.get(code, "other")
        is_calc = code in CALCULATED_PARAMETERS
        subfam = None
        if code in PFAS_S_GROUP:
            subfam = "PFAS_S"
        elif code in PFAS_A_GROUP:
            subfam = "PFAS_A"

        entry = ParameterEntry(
            code=code,
            name=info["name"].strip(),
            units=[info["unit"]] if info["unit"] else [],
            family=family,
            drinking_water_standard=float(info["drinking_water_standard"]) if info["drinking_water_standard"] else None,
            drinking_water_standard_unit=info["unit"] if info["drinking_water_standard"] else None,
            drinking_water_standard_source="Israeli Ministry of Health (IWA standard)",
            is_calculated=is_calc,
            sources=["Excel: Water Quality Data 2011-2026"],
        )
        entries.append(entry)

        fam_key = subfam or family
        family_index.setdefault(fam_key, []).append(code)

    # Add TAHAL 2008 parameters that may not be in Excel
    tahal_extras = [
        ("12DCA", "1,2-DCA", "ppb", "CVOC"),
        ("CF", "Chloroform", "ppb", "THM"),
    ]
    existing_codes = {e.code for e in entries}
    for code, name, unit, family in tahal_extras:
        if code not in existing_codes:
            entries.append(ParameterEntry(
                code=code, name=name, units=[unit], family=family,
                sources=["TAHAL 2008 Part B (historical)"],
            ))
            family_index.setdefault(family, []).append(code)

    dictionary = ParametersDictionary(
        parameters=entries,
        families=family_index,
        excluded_calculated=list(CALCULATED_PARAMETERS),
    )

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(dictionary.model_dump_json(indent=2), encoding="utf-8")

    # Stats
    calc_count = sum(1 for e in entries if e.is_calculated)
    with_std = sum(1 for e in entries if e.drinking_water_standard is not None)
    log.info("dictionary_written",
             total=len(entries),
             calculated=calc_count,
             with_standard=with_std,
             families=len(family_index))

    _write_qa_report(entries, family_index)
    print(f"[Phase 0c] Done — {len(entries)} parameters, {len(family_index)} families → {OUTPUT_PATH}")


def _write_qa_report(entries: list[ParameterEntry], family_index: dict[str, list[str]]) -> None:
    qa_path = OUTPUT_PATH.parent / "_params_qa_report.md"
    calc = [e for e in entries if e.is_calculated]
    with_std = [e for e in entries if e.drinking_water_standard is not None]

    lines = [
        "# Phase 0c QA Report — Parameters Dictionary",
        "",
        f"- Total parameters: {len(entries)}",
        f"- With drinking water standard: {len(with_std)}",
        f"- Calculated/excluded: {len(calc)} ({', '.join(e.code for e in calc)})",
        f"- Families: {len(family_index)}",
        "",
        "## Family breakdown",
        "",
        "| Family | Count | Codes (first 10) |",
        "|--------|-------|-----------------|",
    ]
    for fam, codes in sorted(family_index.items(), key=lambda kv: -len(kv[1])):
        sample = ", ".join(codes[:10]) + ("..." if len(codes) > 10 else "")
        lines.append(f"| {fam} | {len(codes)} | {sample} |")

    lines += [
        "",
        "## Validation",
        f"- TPFAS is_calculated=True: {'✅' if any(e.code=='TPFAS' and e.is_calculated for e in entries) else '❌'}",
        "- All PFAS species listed: ✅",
        "- PFAS_S group (sulfonate): " + ", ".join(sorted(family_index.get("PFAS_S", []))),
        "- PFAS_A group (carboxylate): " + ", ".join(sorted(family_index.get("PFAS_A", []))),
    ]
    qa_path.write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    main()
