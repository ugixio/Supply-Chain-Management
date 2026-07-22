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
- **What it is (owner direction, 2026-07-22 — ADR-0030/0031/0032, Accepted):** a
  **project/workspace modeled as a technology company**, where **SCM is the operating
  discipline** — a read-only versioned **Global Context** (SCM discipline + engineering
  practice + standards, wiki front end, `docs/` SSOT) that governs a **portfolio of
  Projects spanning all tech branches** (AI, ML, Data, Backend, Frontend, DevOps, …). Adds
  a **prompt-refinement gate** (ADR-0032) and a future **Monitoring** connector (ADR-0031).
  Not a commercial product. Full statement in `product-statement.md`.
- **Exists today:**
  - [product-statement.md](product-statement.md) — the authoritative WHAT: layers, who it
    serves, delivery form/staging, core concepts, invariants, open owner decisions.
  - [glossary.md](glossary.md) — the controlled vocabulary, seeded from the estate.
- **MISSING (owner input needed):**
  - `context-map.md` — the concept relationship map (Global Context ↔ Workspace ↔ Project
    ↔ Monitoring) + the SCOR-DS ↔ department map currently in `README.md` (referenced, not
    duplicated); promote it here when it needs to grow.
- **Rule:** product concepts are DEFINED here and REFERENCED everywhere else. A change
  that introduces or renames a concept lands here FIRST (plan⇄context discipline,
  ADR-0010).
