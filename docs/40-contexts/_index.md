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
| 01 | procurement | ✓ | ✓ | ✓ | ✓ | ✓ (PRC-R1..R8) | ⬜ |
| 02 | supplier-management | ✓ | ✓ | ✓ | ✓ | ✓ (SUP-R1..R4) | ⬜ |
| 03 | demand-planning | ✓ | ✓ | ✓ | ✓ | ✓ (DMD-R1..R4) | ⬜ |
| 04 | supply-planning | ✓ | ✓ | ✓ | ✓ | ✓ (SPL-R1..R4) | ⬜ |
| 05 | inventory-management | ✓ | ✓ | ✓ | ✓ | ✓ (INV-R1..R3) | ⬜ |
| 06 | warehouse-management | ✓ | ✓ | ✓ | ✓ | ✓ (WHS-R1..R4) | ⬜ |
| 07 | logistics-transportation | ✓ | ✓ | ✓ | ✓ | ✓ (LOG-R1..R3) | ⬜ |
| 08 | quality-management | ✓ | ✓ | ✓ | ✓ | ✓ (QMS-R1..R4) | ⬜ |
| 09 | compliance-regulatory | ✓ | ✓ | ✓ | ✓ | ✓ (CMP-R1..R3) | ⬜ |
| 10 | risk-management | ✓ | ✓ | ✓ | ✓ | ✓ (RSK-R1..R4) | ⬜ |
| 11 | finance-controlling | ✓ | ✓ | ✓ | ✓ | ✓ (FIN-R1..R3) | ⬜ |
| 12 | sop-planning | ✓ | ✓ | ✓ | ✓ | ✓ (SOP-R1..R3) | ⬜ |
| 13 | order-management | ✓ | ✓ | ✓ | ✓ | ✓ (ORD-R1..R4) | ⬜ |
| 14 | supplier-development | ✓ | ✓ | ✓ | ✓ | ✓ (SDV-R1..R3) | ⬜ |

> **rule.md × 14 landed at U4 (2026-07-20)**, each extracting the invariants its department's
> code already enforces. `specs/` stay ⬜ — created per unit of work when a change is made
> (not speculatively). Every rule ID needs a test (SCM-R13) — coverage is HOW-lane backlog (U7).

- **Rules:**
  - A department `rule.md` is created from `docs/program/templates/rule.md` with its
    reserved prefix (id-registry §2), extracting the invariants currently embedded in
    that department's code/README — backlog item U4 in `program/WORKFLOW.md`.
  - Cross-department rules live in `30-foundation/scm-core/rule.md` (SCM-Rx), inherited
    by every department — referenced, never restated.
  - Departments never read each other's internals; shared concepts live in `src/shared/`
    + `python/shared/` and are governed by SCM-Rx.
