---
title: LLM-Wiki + שכבת ממשל (הגישה)
type: methodology
status: draft
evidence: D
source: "סשן פיתוח KB 2026-06; docs/KB_METHODOLOGY_REVIEW.md"
last_compiled: 2026-06-21
---

# LLM-Wiki + שכבת ממשל — הגישה

## מה
דפוס ה-**LLM-Wiki של Karpathy** (`raw → wiki → file-back`, Markdown, ללא RAG/embeddings) **+ שכבת ממשל** לתוכן high-stakes/רגולטורי.

## למה השכבה
ה-gist של Karpathy מוצהר *"intentionally abstract"* — הוא מספק `raw/` immutable ושלב `Lint`, אבל **לא** דירוג-ראיות, חתימת-מומחה או מטא-provenance. הקהילה זיהתה את הסיכון: **"הזיה מתפשטת"** — טעות נדחסת לדף ומתפשטת על פני דפים מקושרים (חמור מ-RAG, שם טעות = תשובה אחת). שכבת הממשל עונה לכך **מבנית**.

## רקורסיה (אימות עצמאי)
ה-`KB_GOVERNANCE` שלנו הוא **מופע** של דפוסים שכבר הוכחו ב-IAR: SSOT-enforcement → כללי lint; data-integrity → evidence + שער ההסגר; deterministic/generative → גבול הסבר↔ביצוע. כלומר הגישה אומתה עצמאית מתוך פרויקט אמיתי, לא רק תיאורטית.

## ניוד
לכל דומיין **high-stakes, רב-סשן, data-heavy** — לא ספציפי-מים.

## ראה
`capture_hot_verify_cold.md` · `provenance_and_file_back_quarantine.md` · `explain_vs_execute_boundary.md`
