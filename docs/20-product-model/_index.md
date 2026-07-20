---
id: index-product-model
title: "Product Model — authoritative WHAT"
type: product-model
owner: orchestrator
status: active
since: 2026-07-19
updated: 2026-07-19
relations:
  - { type: part-of, target: index-docs }
  - { type: governed-by, target: index-adr }
---
# 20-product-model

- **Belongs here:** the authoritative description of WHAT this product is.
- **What the repo observably is today (recorded, pending the owner's product statement):**
  an **enterprise SCM domain platform** — 14 SCOR-DS-aligned departments of executable
  domain logic (TypeScript), mathematical/ML models (Python), per-department SQL schemas,
  KPI frameworks and regulatory compliance logic, grounded in named standards (ADR-0008).
  It has **no recorded runtime/API/UI decision yet** (open decisions,
  `10-decisions/README.md`).
- **Exists today:**
  - [glossary.md](glossary.md) — the controlled vocabulary, seeded from the estate.
- **MISSING (owner input needed):**
  - `product-model.md` — the product statement: who it serves, the delivery form
    (library / service / full ERP), and the growth path. Until it exists, `README.md` +
    `CLAUDE.md` §Project Overview are the best available description (allowlisted homes).
  - `context-map.md` — the SCOR-DS ↔ department map is currently in `README.md`
    (referenced, not duplicated); promote it here when it needs to grow.
- **Rule:** product concepts are DEFINED here and REFERENCED everywhere else. A change
  that introduces or renames a concept lands here FIRST (plan⇄context discipline,
  ADR-0010).
