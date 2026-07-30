---
id: index-docs
title: "SCM Knowledge Root — apex map"
type: program
owner: orchestrator
status: active
since: 2026-07-19
updated: 2026-07-29
relations:
  - { type: governed-by, target: governance-root }
---
# Supply Chain Management — Knowledge Root

- **Belongs here:** the knowledge root for the whole repo: the authority-ordered tier map
  (contract → decisions → product model → foundation → contexts) plus the non-authority
  program area. Adopted from the ugixio context skeleton (ADR-0010).
- **Exists today:**
  - [00-governance](00-governance/_index.md) — knowledge rules + registries (meta)
  - [10-decisions](10-decisions/README.md) — ADRs, incl. the retroactive record of this
    repo's de-facto decisions (Tier 2)
  - [20-product-model](20-product-model/_index.md) — what the product is + glossary (Tier 3)
  - [25-concepts](25-concepts/_index.md) — the supply-chain concept catalogue: one node per
    concept/formula, stating meaning, the canonical formula, assumptions and the source that
    fixes it. A node links to **no** implementation and holds **no** parameter value — it
    names the project-chosen inputs and stops (Tier 3, ADR-0015 as narrowed by ADR-0037; G10)
  - [30-foundation](30-foundation/_index.md) — cross-cutting rules with stable IDs (Tier 4)
  - [40-contexts](40-contexts/_index.md) — the 14 departments: map of their knowledge
    homes + per-department rule/spec gaps (Tier 4/5)
  - [50-engineering](50-engineering/_index.md) — build-time architecture rules: layering,
    module boundaries, toolchain (Tier 6, materialized with the app build — ADR-0018/0023)
  - [program](program/_index.md) — workflow, operating model, templates (non-authority)
- **Knowledge living OUTSIDE `docs/` (allowlisted, see knowledge-architecture §3):**
  root [CLAUDE.md](../CLAUDE.md) (the contract) · root [README.md](../README.md) ·
  per-package `README.md` (next to the code it documents) ·
  `.claude/skills/*/SKILL.md` (the area-skill layer) · `.claude/commands/` ·
  [standards/REGULATORY_FRAMEWORK.md](standards/REGULATORY_FRAMEWORK.md) (grandfathered).
- **MISSING (tracked in [program/WORKFLOW.md](program/WORKFLOW.md)):** the `60-operations`
  tier — reserved, and it materializes with deployment and runbooks (Phase M5). Nothing else
  in the ladder is outstanding: `50-engineering` was materialized at P1 and all fourteen
  per-department `rule.md` files at U4/C2.
- **Governing refs:** `CLAUDE.md` · `00-governance/knowledge-architecture.md`.
