# Merge Plan — 2026-05-31
## coordinate_system_fix (rerun-verification-2026-05-28 → claude/create-base-report-directory-5DqAR)

**Branch Status**: rerun-verification-2026-05-28 is **21 commits ahead** of target branch.

---

## Overview
This plan documents the systematic transfer of the coordinate system SSOT fix (Steps 1–3) to the target branch, along with all preceding V5 pipeline work.

---

## Commits to Transfer (21 total, grouped by feature)

### Coordinate System Fix (3 commits — REQ #22)
| # | Commit | Message | Status | Target Branch |
|---|--------|---------|--------|---|
| 1 | **a289da9** | Fix coordinate system SSOT violation: make map bounds dynamic (Step 1) | ✅ READY | YES |
| 2 | **5ea733c** | Update governance files: document coordinate system fix (Step 2) | ✅ READY | YES |
| 3 | *pending* | Plan merge strategy (Step 3) | 🔄 PENDING | YES (this plan) |

**Impact**: Fixes invisible boreholes on SVG map. Makes map zone-agnostic.
**Dependencies**: None (pure fix, builds on existing code).
**Merge risk**: LOW — function already in use; no API changes, only implementation detail.

---

### V5 Pipeline Completion (18 commits — REQ #21 infrastructure + prior work)

#### Map & Visualization Enhancements (6 commits)
| # | Commit | Message | Rationale for Target | Status |
|---|--------|---------|-------|--------|
| 4 | c2163b1 | [REQ #21] Steps 5+6 complete — V5 Report + HTML | V5 HTML generation | ✅ READY |
| 5 | b2bcff3 | Fix DOCX RTL: add w:rtl to runs, w:bidi to lang | Word format support | ✅ READY |
| 6 | 0abee65 | Enhance map visibility + add figures to Word | Map background + figures | ✅ READY |
| 7 | e0c25df | Improve map visibility, fix chart captions RTL, insert figures | Chart + figure polish | ✅ READY |
| 8 | 1de3f22 | Update map data source: use fresh May 28 data | Data freshness | ✅ READY |
| 9 | 9288184 | Improve map visibility, fix chart captions, insert figures at original positions | Original positioning | ✅ READY |

#### Word Document Support (4 commits)
| # | Commit | Message | Rationale for Target | Status |
|---|--------|---------|-------|--------|
| 10 | dcd10aa | Add HTML→DOCX conversion via LibreOffice | Word workflow | ⚠️ OPTIONAL |
| 11 | 37a12e3 | Add Word document review workflow infrastructure | Review infrastructure | ⚠️ OPTIONAL |
| 12 | 748f26a | Enhance Word RTL settings, track changes | RTL support | ⚠️ OPTIONAL |
| 13 | aba099b | Add markdown_to_docx; remove superseded variants | Markdown→DOCX | ⚠️ OPTIONAL |

**Note**: Word-related commits can be deferred if target branch scope is HTML-only. Check user intent.

#### Infrastructure & Data Management (8 commits)
| # | Commit | Message | Rationale for Target | Status |
|---|--------|---------|-------|--------|
| 14 | d1b815c | [REQ #21] Step 4 complete — Zone Diagnosis | V5 methodology | ✅ READY |
| 15 | dde5698 | [REQ #21] Step 3a complete — Reports Context Pack | V5 data assembly | ✅ READY |
| 16 | 30abdad | [REQ #21] Step 3b complete — Source Candidates Pack | V5 context | ✅ READY |
| 17 | 19db983 | [PROCESS.md] REQ #21 updated — strict SSOT alignment | Governance tracking | ✅ READY |
| 18 | 6e87a87 | Revert "[rerun] gitignore Holon/rerun_2026-05-28/" | Cleanup | ✅ READY |
| 19 | 4e7f02b | [rerun] gitignore Holon/rerun_2026-05-28/ | Backup handling | ✅ READY |
| 20 | 5ba2d40 | [PROCESS.md] added #21 — Verification Rerun | REQ tracking | ✅ READY |
| 21 | 1559137 | [rerun] Add backup dir to gitignore + PDF timestamp | Cleanup | ✅ READY |

---

## Merge Strategy

### Option A: Linear Fast-Forward (Recommended)
```bash
# Ensure target branch is up-to-date
git fetch origin claude/create-base-report-directory-5DqAR

# Review all 21 commits
git log --oneline claude/create-base-report-directory-5DqAR..HEAD

# Fast-forward merge (if no conflicts)
git checkout claude/create-base-report-directory-5DqAR
git pull origin claude/create-base-report-directory-5DqAR
git merge --ff-only rerun-verification-2026-05-28

# Verify
git log --oneline -10
git push origin claude/create-base-report-directory-5DqAR
```

### Option B: Selective Cherry-Pick (If Word commits excluded)
If target branch scope is HTML-only, cherry-pick just the essential commits:
1. Coordinate system fix (a289da9, 5ea733c)
2. Map enhancements (c2163b1, b2bcff3, etc.)
3. V5 infrastructure (d1b815c, dde5698, 30abdad)

---

## Pre-Merge Checklist

- [ ] **Code review**: All 21 commits audited for correctness
- [ ] **Test verification**: 
  - [ ] `python scripts/generate_holon_v5_html.py` succeeds (194KB HTML, map visible)
  - [ ] `python scripts/generate_holon_designed.py` succeeds (167KB HTML, map visible)
  - [ ] No regression in existing HTML generators
- [ ] **Governance alignment**:
  - [ ] CLAUDE.md §8 updated (dynamic bounds documented) ✅
  - [ ] PROCESS.md REQ #22 added ✅
  - [ ] LESSONS.md §1.7 documented ✅
- [ ] **Merge conflicts**: Verify no overlap with target branch commits
- [ ] **Documentation**: This plan + commit messages provide full audit trail ✅

---

## Post-Merge Activities

1. **Close REQ #22** in PROCESS.md:
   - Move to Closed table
   - Record merge commit hash
   - Verification: "All 3 steps complete + merged to target branch"

2. **Update CLAUDE.md** Phase status (if applicable):
   - Note that coordinate system SSOT fix validates V5 architecture

3. **Pipeline readiness**: After merge, target branch is ready for:
   - Zone #3 onboarding
   - Full 18-zone activation planning

---

## Risk Assessment

| Risk | Severity | Mitigation |
|------|----------|-----------|
| Merge conflicts | LOW | Linear fast-forward if possible; manual resolve if needed |
| Regression in HTML | LOW | Test both generators before pushing |
| Word format break | LOW | Word commits marked optional; can defer if not in scope |
| Coordinate calculation fail | LOW | Dynamic bounds tested on Holon data; no hardcoded assumptions |

---

## Sign-Off

**Branch**: rerun-verification-2026-05-28  
**Target**: claude/create-base-report-directory-5DqAR  
**Date**: 2026-05-31  
**Plan reviewed by**: Claude Code (systematic audit trail maintained via PROCESS.md + LESSONS.md + CLAUDE.md)  
**Status**: 🟢 Ready for merge (pending user confirmation of Word document scope)

---
