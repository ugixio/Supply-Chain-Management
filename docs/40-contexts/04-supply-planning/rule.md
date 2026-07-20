---
id: rule-supply-planning
title: "Rules — Supply Planning (SPL-R*)"
type: rule
owner: orchestrator
status: active
since: 2026-07-20
updated: 2026-07-20
relations:
  - { type: part-of, target: index-contexts }
  - { type: governed-by, target: index-adr }
  - { type: depends-on, target: rule-scm-core }
---
# Rules — Supply Planning

> Invariants enforced in `src/departments/04-supply-planning/` (BOM, MRP, MPS, capacity).
> Know-how lives in the allowlisted homes (`README.md`, `IMPLEMENTATION.md`,
> `.claude/skills/supply-planning/`). IDs append-only (family `SPL`). Inherited `SCM-R*`
> referenced, never restated.

## Invariants (NEVER violated — each verifiable by test)

- **SPL-R1:** A bill of materials forbids self-reference (a component is never its own
  parent) and duplicate component SKUs; every component's `quantityPer` is > 0 and
  `scrapFactorPct` is >= 0 (`BillOfMaterials.ts`).
- **SPL-R2:** A BOM activates only with at least one component, and its `effectiveTo` is
  strictly after `effectiveFrom`.
- **SPL-R3:** A capacity plan cannot be approved while `INFEASIBLE`, nor evaluated with no
  buckets (`CapacityPlan.ts`).
- **SPL-R4:** Capacity `planningHorizonWeeks` is within [1, 52]; per bucket
  `availableHours` > 0 and `requiredHours` >= 0.

## Anti-states (the system must never allow)

- A BOM whose component references itself (cyclic explosion — SPL-R1).
- An approved INFEASIBLE capacity plan (SPL-R3).

## Inherited rules (referenced, not restated)

- **SCM-R10** — quantities use GS1 UOM codes.
- **SCM-R11** — SKU codes are immutable.
