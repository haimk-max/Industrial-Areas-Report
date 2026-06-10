#!/usr/bin/env bash
#
# run_pipeline.sh — V5 hybrid pipeline driver for one zone.
#
# Runs the DETERMINISTIC stages end-to-end and STOPS at each Opus-inference
# boundary (Step 4 diagnosis, Step 5 report) — those are LLM calls, not scripts,
# and must be run by the operator/agent, then this driver resumed.
#
# See ORCHESTRATION.md for the full map (which stage is deterministic vs Opus,
# and the per-script --zone casing convention).
#
# Usage:
#   scripts/run_pipeline.sh <ZONE_DIR> <stage>
#
#   <ZONE_DIR>  directory name, e.g. Holon   (V5 pack tools use this casing)
#   <stage>     data | render-diagnosis | render-report | html | validate | help
#
# Convention split (pre-existing, tracked in PROCESS.md REQ #28):
#   - core data scripts (parse_excel, trend_analysis, forensics) take the
#     LOWERCASED zone id (capitalized internally) — e.g. --zone holon
#   - V5 pack/prompt/QA tools (generate_zone_data_pack, render_zone_prompt,
#     qa_pipeline) take the DIRECTORY NAME — e.g. --zone Holon
#
set -euo pipefail

ZONE="${1:-}"
STAGE="${2:-help}"
if [[ -z "$ZONE" || "$STAGE" == "help" ]]; then
  sed -n '2,30p' "$0"
  exit 0
fi
ZONE_LC="$(echo "$ZONE" | tr '[:upper:]' '[:lower:]')"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

case "$STAGE" in
  data)
    echo "▶ Stage 2 — deterministic data pack for $ZONE"
    python scripts/parse_excel.py            --zone "$ZONE_LC"
    python scripts/trend_analysis.py         --zone "$ZONE_LC"
    python scripts/forensics_analyzer.py     --zone "$ZONE_LC"
    python scripts/generate_zone_data_pack.py --zone "$ZONE"
    python scripts/qa_pipeline.py --gate 2   --zone "$ZONE"
    echo "✓ data pack ready → $ZONE/02_data/  (Gate 2 passed)"
    echo "  NEXT (manual): assemble 03_context/, then: $0 $ZONE render-diagnosis"
    ;;

  render-diagnosis)
    echo "▶ Step 4a — render diagnosis prompt (deterministic)"
    python scripts/render_zone_prompt.py --zone "$ZONE" --step diagnosis --name-he "${ZONE_NAME_HE:?set ZONE_NAME_HE}"
    echo "✓ rendered $ZONE/context_pack/05_prompt/zone_diagnosis_prompt.md"
    echo "  NEXT (OPUS CALL #1): run that prompt → $ZONE/context_pack/04_diagnosis/zone_diagnosis.md"
    echo "  THEN: python scripts/qa_pipeline.py --gate 4 --zone $ZONE"
    echo "  THEN: $0 $ZONE render-report"
    ;;

  render-report)
    echo "▶ Step 5a — render report prompt from the CURRENT diagnosis (deterministic)"
    echo "  (re-render is MANDATORY after any Step 4 re-run — see REQ #27 staleness footgun)"
    python scripts/render_zone_prompt.py --zone "$ZONE" --step report --name-he "${ZONE_NAME_HE:?set ZONE_NAME_HE}"
    python scripts/qa_pipeline.py --gate 3 --zone "$ZONE"
    echo "✓ rendered zone_report_prompt.md (Gate 3 passed — fresh vs template)"
    echo "  NEXT (OPUS CALL #2): run that prompt → $ZONE/output/{ZONE}_REPORT_Vn.md"
    echo "  THEN: python scripts/qa_pipeline.py --gate 5 --zone $ZONE ; then: $0 $ZONE html"
    ;;

  html)
    echo "▶ Step 6 — render final HTML (deterministic)"
    echo "  NOTE: the V5 HTML generator is still Holon-coupled (REQ #28). For Holon:"
    echo "    python scripts/generate_holon_v5_html.py --report $ZONE/output/<REPORT>.md --output $ZONE/output/<REPORT>.html"
    ;;

  validate)
    echo "▶ Step 7 — all QA gates"
    python scripts/qa_pipeline.py --gate all --zone "$ZONE"
    ;;

  *)
    echo "unknown stage: $STAGE (use: data | render-diagnosis | render-report | html | validate | help)" >&2
    exit 1
    ;;
esac
