---
id: index-foundation
title: "Foundation — cross-cutting rules"
type: rule
owner: orchestrator
status: active
since: 2026-07-19
updated: 2026-07-19
relations:
  - { type: part-of, target: index-docs }
  - { type: governed-by, target: index-adr }
---
# 30-foundation

- **Belongs here:** cross-cutting axes that apply to every department **and every project**.
  Each axis carries a `rule.md` (hard rules, stable IDs — Tier 4); its know-how counterpart is
  the matching `.claude/skills/*/SKILL.md` (allowlisted Tier-6 home).
- **Exists today:**
  - [scm-core/rule.md](scm-core/rule.md) — the cross-department core rules, reclassified at
    ADR-0037 to hold only externally-fixed statements (skill
    counterpart: `.claude/skills/supply-chain-core/SKILL.md`).
  - [platform/rule.md](platform/rule.md) — the platform / workspace rules **PLT-R1..R5**
    (prompt-refinement gate, read-only project reference, everything-connected, node/edge
    typing, one-branch-per-project). Governs the workspace layer above the 14 departments
    (ADR-0030/0032; the Node Model in `20-product-model/node-model.md`).
- **Candidate future axes (create only with owner authorization + cited need):**
  `security/` (authZ, secrets, audit — none recorded yet) · `data-governance/` (PII in
  supplier/grievance records) · `observability/`.
