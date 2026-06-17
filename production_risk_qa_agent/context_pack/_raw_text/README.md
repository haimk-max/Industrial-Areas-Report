# Layer 3: Raw TXT Extractions — Backup Only

⚠️ **BACKUP LAYER ONLY — Don't use unless necessary.**

This directory contains raw text extractions from PDF files. They are:
- **Unstructured** (no JSON, no parsing)
- **Large** (41–333 KB each)
- **Slow to search** (full-text grep)

---

## When to use Layer 3?

**Rare**:
- "I need the exact verbatim text from page X of the 2007 report"
- "Extracted_findings.json doesn't have the detail I need"

**Never**:
- For normal Q&A
- For quick answers
- For sourcing evidence (use Layer 2 JSON + references instead)

---

## Files (Not Imported)

The following files exist in `Holon/data/external/_raw_text/`:
- `water-sources-status_tehom_FinalReport-Holon.txt` (176 KB)
- `water-sources-status_tehom_Holon-BatYan-Dec2007.txt` (333 KB)
- `water-sources-status_tehom_holon-part1.txt` (128 KB)
- `water-sources-status_tehom_holon-part2.txt` (41 KB)
- Hebrew filenames (2 files, 68–70 bytes — likely redirect stubs)

---

## How to Access

If you truly need raw TXT:
```bash
# Find the file
find Holon/data/external/_raw_text/ -name "*2007*"

# Search for a keyword
grep -i "tcE" Holon/data/external/_raw_text/*

# Extract specific page context (rough)
sed -n '100,150p' Holon/data/external/_raw_text/finalreport.txt
```

---

**Recommendation**: Use Layer 2 (JSON) first. Only drop to Layer 3 if Layer 2 lacks detail.
