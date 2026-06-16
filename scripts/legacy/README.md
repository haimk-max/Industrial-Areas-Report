# Legacy Scripts Archive

This directory contains superseded scripts from earlier pipeline iterations (V4-era and Raanana-hardcoded versions). These are retained for reference but are **not part of the current V5 hybrid pipeline**.

## Archived Scripts

| Script | Reason | Migration Path |
|--------|--------|-----------------|
| `generate_holon_full_html.py` | Raanana-hardcoded implementation; V4-era design not generalizable to 18 zones | Use `scripts/generate_zone_v5_html.py --zone {zone_id}` (V5 hybrid pipeline) |
| `build_holon_borehole_classification.py` | Holon-specific borehole taxonomy builder; logic now part of zone_diagnosis.md (Step 4 via Opus) | Run `render_zone_prompt.py` + Opus Step 4 (Zone Diagnosis) |
| `generate_charts.py` | Early chart generation (pre-v2); superseded by `generate_charts_v2.py` | Use `scripts/generate_charts_v2.py --zone {zone_id}` |
| `extract_report_2021.py` | Legacy single-source PDF extractor; no cross-zone abstraction | Use `scripts/extract_zone_pdfs.py --zone {zone_id}` + agent-rag skill for facility discovery |
| `build_tahal_base.py` | Legacy TAHAL 2008 extraction; single format | Consolidated by `extract_zone_pdfs.py` + multi-source handling |
| `search_water_authority.py` | Legacy facility web search; no facility scoring | Use toolkit Tier A skill: `agent-rag` (facility discovery with confidence levels) |
| `fetch_water_authority_refs.py` | Legacy facility reference fetching | Use toolkit Tier A skill: `agent-rag` (web-search + PDF ingestion) |

## When These Scripts Were Used

- **Phase D–E (2025–2026)**: Raanana zone (reference implementation, V2) used simplified versions of `build_tahal_base.py` and `search_water_authority.py`
- **Phase 5 (Holon V4.2)**: `generate_holon_full_html.py` and `build_holon_borehole_classification.py` were Holon-specific; generalization was incomplete
- **Phase H+ (V5 hybrid pipeline, 2026-05-28)**: Generic pipeline introduced; these scripts no longer needed

## Current V5 Hybrid Pipeline (Active)

See `ZONE_REPORT_PROCESS_GUIDE.md` §VIII for the 7-step orchestration:

1. **Step 1–2**: Deterministic data ingestion (`parse_excel.py`, `trend_analysis.py`, `generate_zone_data_pack.py`)
2. **Step 3**: Zone Diagnosis (Opus #1, via `render_zone_prompt.py`)
3. **Step 4–5**: HTML + Word generation (`generate_zone_v5_html.py`, document converters)
4. **QA Gates**: `qa_pipeline.py` (Gates 2–6)

**Reference**: `scripts/run_pipeline.sh` for the full orchestration.

---

**Last updated**: 2026-06-10 (REQ #28 stage 1 — legacy archive)
