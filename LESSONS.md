# LESSONS.md — Open Patterns, Deferred Decisions, Tooling Roadmap

**Purpose**: Buffer between observation and codification. This file holds:
1. **Open patterns**: things observed in 1 case, awaiting a 2nd case before promoting to `REQUIREMENTS.md`/`CLAUDE.md`
2. **Deferred decisions**: choices we've consciously postponed, with the trigger that should reopen them
3. **Tooling & Skills roadmap**: future tooling we've agreed makes sense — when, why, and what triggers it

**Rule**: Promote to `REQUIREMENTS.md` only after the 2nd real case validates the pattern. Until then, entries here are tentative.

**Pruning**: Each phase boundary, review entries — promote, drop, or keep with updated context.

---

## 1. Open Patterns (1-Case, Awaiting 2nd-Case Validation)

### 1.1 Cross-zone parameter naming variance
- **Observation (Raanana → Holon)**: Raanana Excel uses short codes (`TCEY`, `PCE`); Holon uses full English names (`TRICHLORO ETHYLENE`).
- **Solution applied**: `scripts/param_families.py` regex-based classifier returns `CVOC | BTEX | PFAS | OTHER` for either format.
- **2nd-case test**: When zone #3 arrives — does its naming convention also fit one of the two patterns, or does it surface a 3rd? If 3rd, the regex approach may need rethinking (config-table?).
- **Status**: ⏳ Awaiting zone #3.

### 1.2 Borehole-set vs. zone-set mismatch
- **Observation (Holon)**: Excel contained 112 boreholes; only 111 were inside the zone polygon. Pipeline initially processed all 112 (wasteful + misleading metrics).
- **Solution applied**: `scripts/select_boreholes.py` writes `selected_boreholes.json`; downstream scripts filter via `borehole_filter.py`.
- **2nd-case test**: Will another zone have the inverse problem (Excel under-supplies; need cross-zone borehole import)? If yes, the filter may need to extend to *additions* not just *exclusions*.
- **Status**: ⏳ Awaiting zone #3.

### 1.3 PDF extraction parallelism heuristic
- **Observation (Holon)**: Single AI agent on 692K Hebrew chars (4 PDFs) hit stream idle timeout. Splitting to 4 parallel sub-agents (Sonnet) succeeded.
- **Heuristic applied**: > ~150K characters → parallel; < 150K → single agent acceptable.
- **2nd-case test**: Validate threshold on next zone. If a single 200K PDF runs fine, threshold is too conservative; if 100K times out, too liberal.
- **Status**: ⏳ Awaiting zone #3 with different PDF sizes. Heuristic codified in `~/.claude/CLAUDE.md` (#6) as tentative.

### 1.4 Merge dedup logic
- **Observation (Holon)**: 5 source PDFs → 127 borehole mentions → 112 unique (dedup by `name_he`).
- **Concern**: `name_he` exact-match may miss equivalents (e.g., "מק חולון 8" vs "מקורות חולון 8" vs "MK Holon 8"). Holon happened to have consistent Hebrew naming — luck or pattern?
- **2nd-case test**: Zone #3 may have inconsistent naming across sources, exposing dedup gaps.
- **Status**: ⏳ Awaiting evidence. May need fuzzy-match or canonical_id lookup.

### 1.5 Facility discovery via AI agent — TWO timeout cases, ready for promotion
- **Observation (Raanana)**: Opus agent + sector-based search produced 9 candidates with confidence levels (worked; Raanana's PDF extraction was sparse — ~0 facilities — so web discovery was the source of truth).
- **Observation (Holon attempt 1, 2026-05-06 morning)**: Opus agent for facility discovery timed out at ~7+ minutes / 27 tool calls; no output written.
- **Observation (Holon attempt 2, 2026-05-06 afternoon)**: Sonnet agent with explicit `max 30 web searches` cap **also timed out** at 12.5 minutes / 65 tool uses; no output written. Cap on search count alone does not prevent stream-idle timeout — the bottleneck is the dialogue overhead (read context → iterate searches → construct large JSON output).
- **Validated rule (2-case rule satisfied)**: Branch facility discovery methodology by PDF-extraction richness:
  - **Sparse extraction** (≤10 facilities, like Raanana): web-discovery agent is the primary source. Use Opus or Sonnet with capped scope.
  - **Rich extraction** (≥30 facilities with addresses + evidence + confidence, like Holon): **skip web discovery entirely**. Direct consolidation + post-hoc characterization is sufficient and avoids the timeout. Web discovery's marginal value does not justify the cost.
- **Heuristic threshold**: ~30 PDF-extracted facilities with structured evidence is the inflection point. Below → do web discovery; above → skip and consolidate.
- **Status**: 🟢 Ready to promote to REQUIREMENTS.md (2-case rule satisfied: Raanana sparse → web works; Holon rich → web times out twice).
- **What changes in STYLE_GUIDE.md § H**: methodology should branch on extraction richness check (Step 0d count of `facilities_suspected[]`).

---

## 2. Deferred Decisions (Trigger to Reopen)

### 2.1 OCR for scanned PDFs (TAHAL 2008-A and 2008-B)
- **Status**: TAHAL 2008 Parts A and B extracted to ~70 bytes each via `pdftotext -layout` — image-based scans.
- **Decision**: Defer OCR for now. The reports are referenced indirectly through 2021 report and Ecolog 2012 anyway.
- **Trigger to revisit**: If Holon expert review notes critical content in TAHAL 2008 missing from current findings, OR if zone #3 depends primarily on TAHAL 2008 with no later report covering it.
- **Tools to consider when revisiting**: `tesseract-ocr` (install required), `ocrmypdf`, or commercial OCR for Hebrew RTL.

### 2.2 Basemap integration (REQ-G1)
- **Status**: Tile providers (OSM, CartoDB, Stamen, ESRI) blocked in current environment — 403 Forbidden.
- **Decision**: Offline ITM schematic is production-ready; basemap deferred.
- **Trigger to revisit**: When environment permits external tile fetch, OR when expert reviewer specifically requests street/cadastral context.
- **Options documented**: cached MBTiles, Israeli WMS (govmap), Overpass vector rendering.
- **★ See § 2.4** — Water Authority ArcGIS Portal integration subsumes this when deployed.

### 2.3 Methodology file consolidation
- **Status (post-cleanup, 2026-05-06)**: REQUIREMENTS.md has REQ-A through REQ-H (12 H-items). Some may overlap or be superseded.
- **Decision**: Don't consolidate now — wait for Holon report to reveal which requirements are actually load-bearing.
- **Trigger to revisit**: After Holon expert review approves the report. Then re-read REQUIREMENTS.md and mark `[ACTIVE]` / `[SUPERSEDED]` / `[ZONE-SPECIFIC]`.

### 2.3a Holon Directory Organization — Cleanup Roadmap (2026-05-25)
- **Issue discovered (post-review)**: Holon has 3 overlapping data trees:
  1. `Holon/lean_workspace/{01..06}/` — V4-era workspace (includes anchors PILOT in `04_deterministic_anchors/`)
  2. `Holon/context_pack/{03_context, 04_diagnosis}/` — V5 context + diagnosis
  3. `Holon/02_data/` — V5 Structured Data Pack (6 CSVs, canonical per DATA_PIPELINE_SPEC.md)
  4. Plus: `Holon/data/`, `Holon/data/external/`, `Holon/charts_v2/`, etc.
  
  **Naming collision**: Both `lean_workspace/04_deterministic_anchors` and `context_pack/04_diagnosis` use "04_", confusing schema readers. CLAUDE.md §8 defines V5 canonical structure as `{zone}/01_scope/`, `02_data/`, `context_pack/03_context/`, `context_pack/04_diagnosis/`, `output/` — but anchors are orphaned in legacy `lean_workspace`.

- **Decision (pragmatic)**: Document paths explicitly in future prompts / generators. Do NOT refactor Holon mid-project (too risky; would require re-testing all outputs).

- **Action — When next zone is created** (Raanana refresh or zone #3): Enforce CLAUDE.md §8 structure from day 1. No sprawl.

- **Future REQ** (`future-tech-debt-cleanup`): After Holon V5 complete + approved: "Holon directory consolidation" — move `04_deterministic_anchors` to `context_pack/`, unify paths, retire `lean_workspace`. Est. 2 hours. Lower priority.

### 2.3b Methodology File Sync — 5 Files Lag V5 Refactor (2026-05-25)
- **Issue**: 5 governance MD files last updated 2026-05-06 (before V5 PROCESS_GUIDE refactor on 2026-05-17):
  - `REQUIREMENTS.md` — mentions "Holon = first application", predates V5 scope clarity
  - `LESSONS.md` — section 2.3 (now 2.3a/2.3b) references old patterns
  - `DATA_DICTIONARY.md` — schema may mix old/V5
  - `docs/STYLE_GUIDE.md` § H (facility discovery) — describes `facility_attribution.json` as primary source, but PROCESS_GUIDE §I deprecated this (artifact, not evidence)
  - `docs/CHART_SPEC.md` — Raanana-only examples, may not reflect svg_charts.py `boreholes_override` API

- **Decision**: No urgent fix. SSOT for V5 work = `ZONE_REPORT_PROCESS_GUIDE.md` §I–IX. Old files used as reference/style guidance only.

- **Trigger to revisit**: On next cycle (zone #3 or refresh). Audit for broken references + update examples. Low priority; deferred.

### 2.4 ★ Water Authority ArcGIS Portal integration (deployment phase)
- **Status**: System currently runs in a sandbox environment with no access to authoritative geographic data (Overpass / OSM tiles / govmap WMS — all blocked, 403 Forbidden). Zone polygons are loaded from one-off KMZ uploads converted via pyproj; street enumeration falls back to agent general knowledge; basemaps are offline ITM schematics.
- **Future state**: When the system is deployed inside the Water Authority's enterprise infrastructure, the operator will have credentials to the **Water Authority's enterprise ArcGIS Portal** (פורטל ArcGIS הארגוני של רשות המים). This single integration solves multiple current limitations simultaneously:
  - **Zone polygons**: authoritative — replace `zone_definitions/zone_polygons.json` (manually-curated KMZ conversions) with feature service queries against the official 18-zone layer
  - **Cadastral & street networks**: feature services for streets, parcels (גושים/חלקות), municipal boundaries — replaces agent-knowledge street enumeration with authoritative data
  - **Basemap tiles**: enterprise basemap services replace blocked OSM/Stamen/ESRI tile providers (resolves REQ-G1, see § 2.2)
  - **Boreholes & monitoring infrastructure**: cross-reference against Water Authority's official borehole layer (canonical IDs, depths, casing, ownership)
  - **Industrial enforcement layers**: PRTR locations, business permits, environmental enforcement actions — accessible via Authority's ArcGIS feature services rather than ad-hoc web scraping
- **Trigger to revisit**: Deployment phase — when the system moves from this development sandbox to production within Water Authority IT.
- **Cross-references**:
  - § 2.2 (basemap integration) — subsumed by this once deployed
  - STYLE_GUIDE.md § H.2 Step 0b (street enumeration via polygon) — current methods 1–3 (Overpass / govmap / agent knowledge) become fallbacks; ArcGIS Portal becomes primary
  - REQ-G1 (basemap) — resolved when deployed
- **Implications for current methodology**: Methods documented for street enumeration, polygon definition, basemap rendering should be tagged as "sandbox fallback" — the production methodology will be a single ArcGIS Portal integration. Don't over-engineer the fallbacks.

---

## 3. Tooling & Skills Roadmap

### 3.1 Run now (low cost, immediate value)

| Skill / Tool | Purpose | Trigger |
|---|---|---|
| `fewer-permission-prompts` | Reduce friction during agent runs and pipeline execution | Run once after current cleanup phase; updates `.claude/settings.json` |

### 3.2 Create after Holon report is approved

| Skill / Tool | Purpose | Why wait |
|---|---|---|
| **`activate-zone` skill** (project-local) | Automates Steps 1–3, 5 of "Adding a New Zone" pipeline (parse → select → extract → merge); pauses before AI-agent steps | Wait for 2 successful manual runs (Raanana + Holon = 2 cases) before extracting the abstraction. After Holon approval, this is legitimate. |
| **`methodology-prune` skill** (optional) | Scans CLAUDE.md/REQUIREMENTS.md for outdated entries, suggests removals | Only worth building if cleanup recurs ≥ 2 times. Review after zone #3. |

### 3.3 Long-term (next project phase: any geographic area / facility)

| Tool | Purpose | Trigger |
|---|---|---|
| **`discover-zone-data` skill** | Given coordinates/place name → discovers available data (Excel, PDFs, polygons) and stages them in zone directory structure | When the project pivots from "18 known zones" to "arbitrary input → report" |
| **Dashboard generator** (script + skill) | Produces interactive zone dashboard alongside or instead of full markdown report | When dashboard format is specified by user |

### 3.4 Available skills referenced

For convenience — skills available in this environment that are relevant here:
- `simplify` — code review for reuse/quality. Use after pipeline scripts grow (post-zone #3).
- `update-config` — for hooks (e.g., pre-commit validating no outdated terms in methodology files). Currently no hooks needed.
- `review` — pre-merge PR review. Use before merging feature branches to main.
- `security-review` — not currently relevant (no secrets / external auth in pipeline).

---

## 4. Patterns Promoted Out of This File (History)

*(Empty — no patterns have been promoted yet. This section will track what graduated from `LESSONS.md` to `REQUIREMENTS.md` and when, so we can audit our promotion discipline.)*

---

**Last Update**: 2026-05-06 (initial creation during methodology hygiene phase)  
**Next Review**: After Holon zone summary report is approved by expert hydrogeologist
