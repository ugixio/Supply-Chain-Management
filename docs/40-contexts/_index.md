---
id: index-contexts
title: "Bounded Contexts — the 14 departments' knowledge map"
type: rule
owner: orchestrator
status: active
since: 2026-07-19
updated: 2026-07-19
relations:
  - { type: part-of, target: index-docs }
  - { type: governed-by, target: index-adr }
---
# 40-contexts — the 14 departments

- **Belongs here:** one directory per department for its normative knowledge — `rule.md`
  (hard rules, stable IDs) and `specs/<key>.md` (unit-of-work specs). The departments'
  **know-how already exists in allowlisted homes** and is NOT moved (knowledge-architecture
  §3): `src/departments/NN-<key>/README.md` (domain treatment), `IMPLEMENTATION.md`
  (analytics playbook), `.claude/skills/<key>/SKILL.md` (agent skill),
  `python/NN_<key>/` (models).
- **Knowledge map (existing homes ✓ · gaps ⬜):**

| # | Department | README | IMPL | SKILL | Python | rule.md (family) | specs |
|---|---|---|---|---|---|---|---|
| 01 | procurement | ✓ | ✓ | ✓ | ✓ | ⬜ (PRC) | ⬜ |
| 02 | supplier-management | ✓ | ✓ | ✓ | ✓ | ⬜ (SUP) | ⬜ |
| 03 | demand-planning | ✓ | ✓ | ✓ | ✓ | ⬜ (DMD) | ⬜ |
| 04 | supply-planning | ✓ | ✓ | ✓ | ✓ | ⬜ (SPL) | ⬜ |
| 05 | inventory-management | ✓ | ✓ | ✓ | ✓ | ⬜ (INV) | ⬜ |
| 06 | warehouse-management | ✓ | ✓ | ✓ | ✓ | ⬜ (WHS) | ⬜ |
| 07 | logistics-transportation | ✓ | ✓ | ✓ | ✓ | ⬜ (LOG) | ⬜ |
| 08 | quality-management | ✓ | ✓ | ✓ | ✓ | ⬜ (QMS) | ⬜ |
| 09 | compliance-regulatory | ✓ | ✓ | ✓ | ✓ | ⬜ (CMP) | ⬜ |
| 10 | risk-management | ✓ | ✓ | ✓ | ✓ | ⬜ (RSK) | ⬜ |
| 11 | finance-controlling | ✓ | ✓ | ✓ | ✓ | ⬜ (FIN) | ⬜ |
| 12 | sop-planning | ✓ | ✓ | ✓ | ✓ | ⬜ (SOP) | ⬜ |
| 13 | order-management | ✓ | ✓ | ✓ | ✓ | ⬜ (ORD) | ⬜ |
| 14 | supplier-development | ✓ | ✓ | ✓ | ✓ | ⬜ (SDV) | ⬜ |

- **Rules:**
  - A department `rule.md` is created from `docs/program/templates/rule.md` with its
    reserved prefix (id-registry §2), extracting the invariants currently embedded in
    that department's code/README — backlog item U4 in `program/WORKFLOW.md`.
  - Cross-department rules live in `30-foundation/scm-core/rule.md` (SCM-Rx), inherited
    by every department — referenced, never restated.
  - Departments never read each other's internals; shared concepts live in `src/shared/`
    + `python/shared/` and are governed by SCM-Rx.
