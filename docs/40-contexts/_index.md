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
  §3): the department's `.claude/skills/<key>/SKILL.md` (practice) and its concept nodes in
  `docs/25-concepts/NN-<key>/` (meaning). No code tree backs these any more (ADR-0037).
- **Knowledge map (existing homes ✓ · gaps ⬜):**

| # | Department | Live rules | specs |
|---|---|---|---|
| 01 | procurement | 4 | ⬜ |
| 02 | supplier-management | 1 | ⬜ |
| 03 | demand-planning | 2 | ⬜ |
| 04 | supply-planning | 3 | ⬜ |
| 05 | inventory-management | 3 | ⬜ |
| 06 | warehouse-management | 2 | ⬜ |
| 07 | logistics-transportation | 3 | ⬜ |
| 08 | quality-management | 3 | ⬜ |
| 09 | compliance-regulatory | 3 | ⬜ |
| 10 | risk-management | 3 | ⬜ |
| 11 | finance-controlling | 3 | ⬜ |
| 12 | sop-planning | 2 | ⬜ |
| 13 | order-management | 3 | ⬜ |
| 14 | supplier-development | 3 | ⬜ |

> **Swept at Phase C2 (2026-07-27, ADR-0037).** The families were first extracted at U4 from the
> `throw` guards of an application this repository no longer contains, so most of what they called
> invariants were invented workflows or field checks. Each file now holds only what a standards
> body, a regulator or an arithmetic identity fixes, a **Retired rules** table explaining every
> removal, and a **Project decisions** section naming what the department must answer for itself.
> Counts above are live rules per family; the retirement tables carry the rest.
>
> `specs/` stay ⬜ — created per unit of work, never speculatively.

- **Rules:**
  - A department `rule.md` is created from `docs/program/templates/rule.md` with its
    reserved prefix (id-registry §2), extracting the invariants currently embedded in
    that department's code/README — backlog item U4 in `program/WORKFLOW.md`.
  - Cross-department rules live in `30-foundation/scm-core/rule.md` (SCM-Rx), inherited
    by every department — referenced, never restated.
  - Departments never read each other's internals; shared concepts live in `src/shared/`
    and are governed by the `SCM-R*` family.
